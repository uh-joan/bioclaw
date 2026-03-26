#!/usr/bin/env python3
"""
Patent & exclusivity scanner for regulatory precedent analysis.

Uses FDA Orange Book (via fda_get_patent_exclusivity MCP) to get actual
drug product patents, expiry dates, and exclusivity periods for precedent drugs.
Only works for NDA (small molecule) precedents — BLAs are not in the Orange Book.
"""

import re
from datetime import datetime
from typing import Dict, Any, List, Optional


def scan_patent_landscape(
    precedents: List[Dict],
    mcp_funcs: Dict,
    progress_callback=None,
) -> Dict[str, Any]:
    """
    Scan patent/exclusivity landscape for precedent drugs using FDA Orange Book.

    Returns a compact, deduplicated summary grouped by active ingredient.
    """
    fda_patents = mcp_funcs.get('fda_get_patent_exclusivity')
    if not fda_patents:
        return _empty_result('Missing fda_get_patent_exclusivity MCP function')

    candidates = _collect_nda_candidates(precedents)
    if not candidates:
        return _empty_result('No US NDA precedents to scan (BLAs/EU not in Orange Book)')

    raw_entries = []
    for i, (drug_name, app_num) in enumerate(candidates):
        if progress_callback:
            progress_callback(i / len(candidates), f"Checking Orange Book for {drug_name}...")

        entry = _scan_orange_book(drug_name, app_num, fda_patents)
        if entry:
            raw_entries.append(entry)

    if progress_callback:
        progress_callback(1.0, f"Patent scan complete: {len(raw_entries)} drugs checked")

    # Post-process: group by ingredient, deduplicate, summarize
    grouped = _group_by_ingredient(raw_entries)

    # Count only drugs with active protection
    protected = [g for g in grouped if g.get('patent_count', 0) > 0 or g.get('exclusivities')]
    active_patents = sum(1 for g in grouped if g.get('patent_count', 0) > 0)
    active_exclusivities = sum(1 for g in grouped if g.get('exclusivities'))

    return {
        'drug_patents': protected,
        'active_patent_count': active_patents,
        'active_exclusivity_count': active_exclusivities,
        'total_scanned': len(raw_entries),
        'sources': ['FDA Orange Book'] if raw_entries else [],
    }


def _empty_result(note: str) -> Dict[str, Any]:
    return {
        'drug_patents': [],
        'active_patent_count': 0,
        'active_exclusivity_count': 0,
        'total_scanned': 0,
        'sources': [],
        'note': note,
    }


def _collect_nda_candidates(precedents: List[Dict]) -> List[tuple]:
    """Extract unique US NDA drugs with application numbers."""
    seen = set()
    candidates = []

    for p in precedents:
        region = (p.get('region') or '').upper()
        if region != 'US':
            continue

        app_num = p.get('application_number') or ''
        if not app_num.upper().startswith('NDA'):
            continue

        num = re.sub(r'[^0-9]', '', app_num)
        if not num or num in seen:
            continue
        seen.add(num)

        drug_name = (p.get('drug_name') or p.get('brand_name') or '').strip()
        candidates.append((drug_name, num))

    return candidates


def _scan_orange_book(
    drug_name: str,
    nda_number: str,
    fda_patents,
) -> Optional[Dict[str, Any]]:
    """Query FDA Orange Book for a single NDA."""
    try:
        result = fda_patents(nda_number=nda_number, search_term=drug_name)

        if not isinstance(result, dict) or not result.get('success'):
            return {
                'drug_name': drug_name,
                'nda': nda_number,
                'active_patents': [],
                'exclusivities': [],
                'note': 'No Orange Book data',
            }

        data = result.get('data', {})
        raw_patents = data.get('patents', [])
        raw_excl = data.get('exclusivity', [])

        active_patents = _parse_patents(raw_patents)
        exclusivities = _parse_exclusivities(raw_excl)

        app_info = data.get('application', {})
        trade_name = app_info.get('tradeName', '')
        ingredient = app_info.get('ingredient', drug_name)

        return {
            'drug_name': drug_name,
            'trade_name': trade_name,
            'ingredient': ingredient,
            'nda': nda_number,
            'active_patents': active_patents,
            'exclusivities': exclusivities,
        }

    except Exception:
        return {
            'drug_name': drug_name,
            'nda': nda_number,
            'active_patents': [],
            'exclusivities': [],
            'note': 'Error querying Orange Book',
        }


def _group_by_ingredient(entries: List[Dict]) -> List[Dict]:
    """
    Deduplicate combo products by merging into single-ingredient entries.

    Strategy: Process single-ingredient products first, then merge combo products
    into the matching single-ingredient entries. Combos that don't match any
    single ingredient are kept as-is.
    """
    # Separate single-ingredient vs combo entries
    singles = {}  # normalized_ingredient -> entry
    combos = []

    for entry in entries:
        ingredient = (entry.get('ingredient') or entry.get('drug_name') or '').upper().strip()
        parts = [p.strip() for p in re.split(r'[,;]', ingredient) if p.strip()]

        if len(parts) <= 1:
            norm_key = _normalize_ingredient(ingredient)
            if norm_key not in singles:
                singles[norm_key] = {
                    'ingredient': ingredient.title(),
                    'trade_names': [],
                    'ndas': [],
                    'patents': {},
                    'exclusivities': {},
                }
            _merge_entry(singles[norm_key], entry)
        else:
            combos.append((parts, entry))

    # Merge combos into matching single-ingredient groups
    for parts, entry in combos:
        matched = False
        for part in parts:
            norm_key = _normalize_ingredient(part)
            if norm_key in singles:
                # Merge combo's patents/exclusivities under existing single ingredient
                _merge_entry(singles[norm_key], entry)
                matched = True
                break  # Only merge into first matching ingredient (avoid double-counting)

        if not matched:
            # No matching single ingredient — keep combo as its own entry
            combo_name = ' + '.join(p.title() for p in parts)
            norm_key = _normalize_ingredient(parts[0])
            if norm_key not in singles:
                singles[norm_key] = {
                    'ingredient': combo_name,
                    'trade_names': [],
                    'ndas': [],
                    'patents': {},
                    'exclusivities': {},
                }
            _merge_entry(singles[norm_key], entry)

    # Convert to output format
    results = []
    for norm_key, merged in singles.items():
        patents = list(merged['patents'].values())
        patents.sort(key=lambda x: _parse_date(x['expires']) or datetime.min)
        exclusivities = list(merged['exclusivities'].values())

        # Find key patent: prefer substance patent with latest expiry
        substance_patents = [p for p in patents if p.get('substance')]
        key_patent = substance_patents[-1] if substance_patents else (patents[-1] if patents else None)

        # Find latest patent expiry
        latest_expiry = None
        latest_expiry_str = ''
        for p in patents:
            d = _parse_date(p['expires'])
            if d and (latest_expiry is None or d > latest_expiry):
                latest_expiry = d
                latest_expiry_str = p['expires']

        results.append({
            'ingredient': merged['ingredient'],
            'trade_names': merged['trade_names'],
            'ndas': merged['ndas'],
            'patent_count': len(patents),
            'latest_expiry': latest_expiry_str,
            'key_patent': key_patent,
            'exclusivities': exclusivities,
        })

    # Sort by latest expiry (latest first = most protected)
    results.sort(key=lambda x: _parse_date(x['latest_expiry']) or datetime.min, reverse=True)
    return results


def _merge_entry(target: Dict, entry: Dict):
    """Merge an entry's trade name, NDA, patents, exclusivities into target."""
    trade = entry.get('trade_name', '')
    if trade and trade not in target['trade_names']:
        target['trade_names'].append(trade)
    nda = entry.get('nda', '')
    if nda and nda not in target['ndas']:
        target['ndas'].append(nda)
    for pat in entry.get('active_patents', []):
        pat_no = pat.get('patent_no', '')
        if pat_no and pat_no not in target['patents']:
            target['patents'][pat_no] = pat
    for exc in entry.get('exclusivities', []):
        exc_key = (exc.get('code', ''), exc.get('expires', ''))
        if exc_key not in target['exclusivities']:
            target['exclusivities'][exc_key] = exc


def _normalize_ingredient(name: str) -> str:
    """Normalize ingredient name for dedup by stripping pharmaceutical salt forms.

    Suffix list derived from FDA openFDA product ingredient frequency analysis
    (top salt/ester/cation suffixes appearing in >50 products).
    """
    n = name.upper().strip()
    n = re.sub(
        r'\s+('
        r'HYDROCHLORIDE|DIHYDROCHLORIDE|HCL|'       # 6,216 + 77 products
        r'SODIUM|DISODIUM|'                           # 1,445 + 59
        r'SULFATE|'                                   # 1,082
        r'CHLORIDE|'                                  # 844
        r'ACETATE|'                                   # 544
        r'PHOSPHATE|'                                 # 492
        r'TARTRATE|BITARTRATE|'                       # 350 + 263
        r'MALEATE|'                                   # 320
        r'ACETONIDE|'                                 # 272
        r'SUCCINATE|'                                 # 248
        r'FUMARATE|HEMIFUMARATE|'                     # 237
        r'CALCIUM|'                                   # 211
        r'POTASSIUM|DIPOTASSIUM|'                     # 182 + 64
        r'CITRATE|'                                   # 181
        r'PROPIONATE|DIPROPIONATE|'                   # 174 + 95
        r'BESYLATE|'                                  # 166
        r'BROMIDE|HYDROBROMIDE|'                      # 149 + 117
        r'MESYLATE|'                                  # 140
        r'LACTATE|'                                   # 112
        r'HYCLATE|'                                   # 110
        r'TROMETHAMINE|'                              # 84
        r'GLUCONATE|'                                 # 77
        r'MAGNESIUM|'                                 # 74
        r'BICARBONATE|CARBONATE|'                     # 73 + 70
        r'MEDOXOMIL|'                                 # 65
        r'VALERATE|'                                  # 60
        r'BENZOATE|'                                  # common (alogliptin)
        r'NITRATE|'                                   # common
        r'NAPSYLATE|PAMOATE|TOSYLATE|EDISYLATE|'      # less common but real
        r'ESYLATE|ISETHIONATE|XINAFOATE|DECANOATE'    # depot/inhaler forms
        r')$',
        '', n
    )
    return n.strip()


def _parse_patents(raw_patents: List[Dict]) -> List[Dict]:
    """Deduplicate and parse patent entries, keeping only active (not expired)."""
    now = datetime.now()
    seen = set()
    patents = []

    for p in raw_patents:
        pat_no = p.get('patentNo', '')
        if not pat_no or pat_no in seen:
            continue
        seen.add(pat_no)

        if '*PED' in pat_no:
            continue

        expire_str = p.get('patentExpireDate', '')
        expire_date = _parse_date(expire_str)

        if expire_date and expire_date < now:
            continue

        patents.append({
            'patent_no': pat_no,
            'expires': expire_str,
            'substance': p.get('drugSubstanceFlag', '') == 'Y',
            'product': p.get('drugProductFlag', '') == 'Y',
            'use_code': p.get('patentUseCode', ''),
            'url': f"https://patents.google.com/patent/US{pat_no}",
        })

    patents.sort(key=lambda x: _parse_date(x['expires']) or datetime.min)
    return patents


def _parse_exclusivities(raw_excl: List[Dict]) -> List[Dict]:
    """Deduplicate and parse exclusivity entries, keeping only active."""
    now = datetime.now()
    seen = set()
    exclusivities = []

    # FDA Orange Book exclusivity code prefixes
    # Full list: https://www.fda.gov/drugs/drug-approvals-and-databases/orange-book-data-files
    code_prefixes = {
        'NCE': 'NCE (5yr)',
        'ODE': 'Orphan',
        'PED': 'Pediatric (+6mo)',
        'NPP': 'New Patient Pop.',
        'I-': 'New Indication',
        'M-': 'Marketing',
        'D-': 'New Data (3yr)',
        'P-': 'Pediatric (+6mo)',
    }

    for e in raw_excl:
        code = e.get('exclusivityCode', '')
        date_str = e.get('exclusivityDate', '')
        dedup_key = (code, date_str)
        if dedup_key in seen or not code:
            continue
        seen.add(dedup_key)

        expire_date = _parse_date(date_str)
        if expire_date and expire_date < now:
            continue

        # Resolve description: exact match first, then prefix match
        desc = code_prefixes.get(code)
        if not desc:
            for prefix, prefix_desc in code_prefixes.items():
                if code.startswith(prefix):
                    desc = prefix_desc
                    break
        if not desc:
            desc = code

        exclusivities.append({
            'code': code,
            'description': desc,
            'expires': date_str,
        })

    return exclusivities


def _parse_date(date_str: str) -> Optional[datetime]:
    """Parse FDA date formats like 'Nov 24, 2026'."""
    if not date_str:
        return None
    for fmt in ('%b %d, %Y', '%B %d, %Y', '%Y-%m-%d'):
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    return None
