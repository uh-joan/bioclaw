#!/usr/bin/env python3
"""
Precedent Finder - Discovers approved drugs in an indication across FDA and EMA.

Extracts:
- Approval pathway (NDA, BLA, 505(b)(2), Centralized MAA, etc.)
- Approval date and timeline
- Pivotal trial design (NCT ID, endpoints, enrollment)
- Key regulatory issues raised
- Designations granted (Breakthrough, Fast Track, Orphan, PRIME)

All MCP functions accessed via mcp_funcs parameter (injected by server).
"""

import sys
import os
import re
from typing import Dict, Any, List, Optional, Callable

# Add script directory to path for local imports
_script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _script_dir)

from regulatory_constants import NO_PRECEDENT_THRESHOLD

# Terms that are too generic to be useful as FDA label search terms
_NOISE_TERMS = {
    'disease', 'disorder', 'syndrome', 'condition', 'unspecified',
    'other', 'complications', 'sequelae', 'manifestations',
}

# Symptoms/signs that are shared across unrelated diseases and cause false positives
# (e.g., "chorea" matches Huntington's AND Sydenham's chorea in Penicillin labels)
_NOISY_SYMPTOMS = {
    'chorea', 'tremor', 'spasticity', 'ataxia', 'neuropathy',
    'anemia', 'edema', 'cachexia', 'fatigue', 'seizure', 'seizures',
    'pain', 'inflammation', 'fibrosis', 'necrosis',
}

# Oncology umbrella terms → specific subtypes for FDA label search expansion
# These umbrella terms often don't appear in FDA labels, which use specific subtypes
_ONCOLOGY_SUBTYPE_MAP = {
    'non-hodgkin lymphoma': [
        'diffuse large B-cell lymphoma', 'mantle cell lymphoma',
        'follicular lymphoma', 'marginal zone lymphoma',
        'Burkitt lymphoma',
    ],
    'non-hodgkin\'s lymphoma': [
        'diffuse large B-cell lymphoma', 'mantle cell lymphoma',
        'follicular lymphoma', 'marginal zone lymphoma',
    ],
    'lung cancer': [
        'non-small cell lung cancer', 'small cell lung cancer',
    ],
    'skin cancer': [
        'melanoma', 'basal cell carcinoma', 'squamous cell carcinoma',
        'cutaneous squamous cell carcinoma', 'Merkel cell carcinoma',
    ],
    'brain cancer': [
        'glioblastoma', 'glioma', 'astrocytoma', 'medulloblastoma',
    ],
    'blood cancer': [
        'acute myeloid leukemia', 'chronic lymphocytic leukemia',
        'multiple myeloma', 'diffuse large B-cell lymphoma',
    ],
    'kidney cancer': [
        'renal cell carcinoma', 'clear cell renal cell carcinoma',
    ],
    'liver cancer': [
        'hepatocellular carcinoma',
    ],
}

# Cross-contamination pairs: subtype A should never pull in subtype B
# Format: stem → set of distinguishing modifiers that are mutually exclusive
_DISEASE_FAMILY_EXCLUSIONS = {
    'hepatitis': {'a', 'b', 'c', 'd', 'e'},
    'diabetes': {'1', '2'},
    'herpes': {'simplex', 'zoster'},
}

# Short abbreviations that are too ambiguous for FDA label searches
# (they match completely unrelated drugs — e.g., "PSA" matches prostate drugs,
# "PLA" matches unrelated generics). Only block terms <=4 chars that are
# known to cause false positives.
_NOISY_ABBREVIATIONS = {
    'psa', 'pla', 'iddm', 'niddm', 'dka', 'dfu', 'attr',
    'hba1c', 'a1c', 'bmi', 'ckd', 'esrd', 'hfref', 'hfpef',
    'copd',  # too broad for specific indication searches
}


def resolve_indication_synonyms(
    indication: str,
    mcp_funcs: Dict[str, Callable] = None,
) -> List[str]:
    """
    Dynamically resolve indication synonyms using NLM Conditions + OpenTargets.

    Strategy:
    1. NLM Conditions API (primary) — returns primary_name, consumer_name,
       word_synonyms, synonyms for medical conditions
    2. OpenTargets search_diseases (fallback) — catches newer terms NLM may not know
    3. Always include the original user term

    Returns deduplicated list of search terms.
    """
    if mcp_funcs is None:
        mcp_funcs = {}

    terms = set()
    terms.add(indication)  # Always include original

    nlm_search = mcp_funcs.get('nlm_search_codes')
    opentargets_search = mcp_funcs.get('opentargets_search')

    # --- Source 1: NLM Conditions ---
    if nlm_search:
        try:
            result = nlm_search(
                method='conditions',
                terms=indication,
                maxList=10,
                extraFields='primary_name,consumer_name,word_synonyms,synonyms,icd10cm_codes',
            )

            # Parse NLM response — can be list, dict with 'results', or dict with 'text'
            conditions = []
            if isinstance(result, list):
                conditions = result
            elif isinstance(result, dict):
                conditions = result.get('results', [])
                if not conditions and 'text' in result:
                    conditions = _parse_nlm_conditions_text(result['text'])

            # Use ICD-10 code clustering to filter complications/unrelated conditions.
            # The first result is the anchor — keep conditions whose ICD-10 block
            # matches the anchor's block (e.g., E11 for diabetes).
            anchor_block = None
            if conditions:
                anchor_icd = conditions[0].get('icd10cm_codes', '')
                anchor_block = _extract_icd10_block(anchor_icd)
                if anchor_block:
                    print(f"  [NLM] Anchor ICD-10 block: {anchor_block}")

            for cond in conditions:
                icd_code = cond.get('icd10cm_codes', '')
                cond_block = _extract_icd10_block(icd_code)

                # Filter: skip conditions whose ICD-10 block doesn't match anchor
                if anchor_block and cond_block and not _icd10_blocks_related(anchor_block, cond_block):
                    primary = cond.get('primary_name', '')
                    print(f"  [NLM] Filtered (ICD {cond_block} != {anchor_block}): {primary}")
                    continue

                primary = cond.get('primary_name', '')
                consumer = cond.get('consumer_name', '')
                syns = cond.get('synonyms', '')
                # NOTE: word_synonyms intentionally skipped — it contains individual
                # tokenized words (e.g., "CONGESTIVE", "HEART", "FAILURE" separately)
                # which are useless for FDA label searches. The synonyms field has
                # actual clinical aliases (e.g., "CHF", "NIDDM").

                if primary:
                    terms.add(primary)
                if consumer and consumer != primary:
                    # Strip parenthetical abbreviations for cleaner search
                    clean_consumer = re.sub(r'\s*\([^)]+\)\s*$', '', consumer).strip()
                    if clean_consumer:
                        terms.add(clean_consumer)

                # Parse list or string synonyms
                if isinstance(syns, list):
                    for s in syns:
                        s = s.strip() if isinstance(s, str) else ''
                        if s and len(s) > 2 and s.lower() not in _NOISE_TERMS:
                            terms.add(s)
                elif isinstance(syns, str) and syns:
                    for s in re.split(r'[;,]', syns):
                        s = s.strip()
                        if s and len(s) > 2 and s.lower() not in _NOISE_TERMS:
                            terms.add(s)

            print(f"  [NLM] Resolved {len(conditions)} conditions, {len(terms)} terms so far")

        except Exception as e:
            print(f"  [NLM] Error resolving synonyms: {e}")

    # --- Source 2: OpenTargets search_diseases ---
    if opentargets_search:
        try:
            result = opentargets_search(
                method='search_diseases',
                query=indication,
                size=5,
            )

            diseases = []
            if isinstance(result, dict):
                data = result.get('data', {})
                if isinstance(data, dict):
                    # Nested: {'data': {'search': {'hits': [...]}}}
                    hits = data.get('search', {}).get('hits', [])
                    diseases = hits if hits else []
                elif isinstance(data, list):
                    diseases = data
                if not diseases and 'text' in result:
                    diseases = _parse_opentargets_text(result['text'])

            indication_lower = indication.lower()
            for disease in diseases:
                name = disease.get('name', '')
                desc = disease.get('description', '')

                # Relevance check: does the disease name or description mention
                # the original indication? This filters OpenTargets noise
                # (e.g., "Haddad syndrome" when searching for "MASH")
                combined = f"{name} {desc}".lower()
                if not _is_relevant_disease(indication_lower, combined):
                    continue

                if name:
                    terms.add(name)

                if desc:
                    # Extract parenthetical aliases like "(MASH)" or "(NASH)"
                    paren_matches = re.findall(r'\(([A-Z]{2,8})\)', desc)
                    for abbr in paren_matches:
                        terms.add(abbr)

            print(f"  [OpenTargets] Found {len(diseases)} diseases, {len(terms)} terms total")

        except Exception as e:
            print(f"  [OpenTargets] Error resolving synonyms: {e}")

    # Filter and deduplicate
    unique = _deduplicate_terms(list(terms), indication=indication)
    print(f"  [Synonyms] Final search terms ({len(unique)}): {unique}")
    return unique


def _parse_nlm_conditions_text(text: str) -> List[Dict[str, Any]]:
    """Parse NLM conditions text/markdown response."""
    conditions = []
    if not text:
        return conditions

    current = {}
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            if current:
                conditions.append(current)
                current = {}
            continue

        for pattern, field in [
            (r'\*\*(?:Primary[_ ]?[Nn]ame|Name)\*\*[:\s]+(.+)', 'primary_name'),
            (r'\*\*Consumer[_ ]?[Nn]ame\*\*[:\s]+(.+)', 'consumer_name'),
            (r'\*\*(?:Word[_ ]?)?[Ss]ynonyms?\*\*[:\s]+(.+)', 'word_synonyms'),
            (r'\*\*[Ss]ynonyms?\*\*[:\s]+(.+)', 'synonyms'),
        ]:
            m = re.search(pattern, line)
            if m:
                current[field] = m.group(1).strip()

    if current:
        conditions.append(current)
    return conditions


def _parse_opentargets_text(text: str) -> List[Dict[str, Any]]:
    """Parse OpenTargets text/markdown response."""
    diseases = []
    if not text:
        return diseases

    current = {}
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            if current:
                diseases.append(current)
                current = {}
            continue

        for pattern, field in [
            (r'\*\*(?:Disease[_ ]?)?[Nn]ame\*\*[:\s]+(.+)', 'name'),
            (r'\*\*[Dd]escription\*\*[:\s]+(.+)', 'description'),
        ]:
            m = re.search(pattern, line)
            if m:
                current[field] = m.group(1).strip()

    if current:
        diseases.append(current)
    return diseases


def _is_relevant_disease(indication_lower: str, candidate_text_lower: str) -> bool:
    """Check if a disease result is relevant to the user's indication.

    Uses word overlap: the candidate must mention the indication term,
    or the indication must appear in the candidate text.
    """
    # Direct substring match (handles abbreviations like "MASH" in descriptions)
    if indication_lower in candidate_text_lower:
        return True

    # Word-level overlap: at least one significant word from indication in candidate
    indication_words = set(re.findall(r'[a-z]{3,}', indication_lower))
    candidate_words = set(re.findall(r'[a-z]{3,}', candidate_text_lower))

    # Remove very common words
    stop_words = {'the', 'and', 'for', 'with', 'that', 'from', 'are', 'this', 'not', 'has', 'was', 'which'}
    indication_words -= stop_words
    candidate_words -= stop_words

    overlap = indication_words & candidate_words
    return len(overlap) > 0


def _extract_icd10_block(icd_code: str) -> Optional[str]:
    """Extract the 3-character ICD-10 block from a code (e.g., 'E11.9' → 'E11')."""
    if not icd_code:
        return None
    # ICD-10 codes look like E11.9, I50.9, M06.9, C50.9, G30.0
    match = re.match(r'([A-Z]\d{2})', icd_code.strip())
    return match.group(1) if match else None


def _icd10_blocks_related(anchor: str, candidate: str) -> bool:
    """Check if two ICD-10 blocks are related enough to keep.

    Rules:
    - Same block (E11 == E11) → always related
    - Same letter + adjacent numeric range (E10 vs E11, E13) → related
      (diabetes subtypes are E10-E14)
    - Same letter but distant range (E23 vs E11) → unrelated
    - Different letter (G63 vs E11) → unrelated
    """
    if anchor == candidate:
        return True

    # Must share the same letter (same ICD-10 chapter)
    if anchor[0] != candidate[0]:
        return False

    # Check if numeric part is within ±3 range
    # This handles related condition subtypes (e.g., E10-E14 for diabetes)
    # but prevents overly broad matches (e.g., J00 common cold vs J21 RSV bronchiolitis)
    try:
        anchor_num = int(anchor[1:])
        cand_num = int(candidate[1:])
        return abs(anchor_num - cand_num) <= 3
    except ValueError:
        return False


def _deduplicate_terms(terms: List[str], indication: str = None) -> List[str]:
    """Deduplicate terms case-insensitively, filtering noisy abbreviations.

    Filters:
    1. Known noisy abbreviations (PSA, ATTR, etc.)
    2. Terms <=2 chars (too ambiguous for FDA searches: "IB", "CF", etc.)
    3. Single-word parent categories from multi-word indications
       (e.g., "leukemia" is too broad for "chronic lymphocytic leukemia")
    4. Noisy symptoms shared across unrelated diseases (e.g., "chorea")
    5. Cross-contamination from disease families (e.g., "hepatitis B" for "hepatitis C")
    """
    seen = set()
    unique = []

    # Build indication word set for parent-category filtering
    indication_words = set()
    if indication:
        indication_words = {w.lower() for w in indication.split() if len(w) > 2}

    # Build cross-contamination filter: detect the indication's disease family subtype
    indication_lower = (indication or '').lower()
    excluded_subtypes = _build_cross_contamination_exclusions(indication_lower)

    for t in terms:
        tl = t.lower().strip()
        if not tl or tl in seen:
            continue
        # Skip very short terms (<=2 chars) — too ambiguous for FDA/EMA searches
        if len(tl) <= 2:
            print(f"  [Filter] Skipping short term: '{t}'")
            continue
        # Skip known noisy abbreviations that cause false-positive FDA matches
        if tl in _NOISY_ABBREVIATIONS:
            print(f"  [Filter] Skipping noisy abbreviation: '{t}'")
            continue
        # Skip noisy symptom terms shared across unrelated diseases
        if tl in _NOISY_SYMPTOMS:
            print(f"  [Filter] Skipping noisy symptom: '{t}'")
            continue
        # Skip single-word terms that are just a parent category of the indication
        # (e.g., "leukemia" for "chronic lymphocytic leukemia" — matches ALL leukemias)
        if (indication_words and len(indication_words) >= 3
                and len(tl.split()) == 1 and tl in indication_words):
            print(f"  [Filter] Skipping parent category: '{t}' (too broad for multi-word indication)")
            continue
        # Skip cross-contamination from disease families
        # (e.g., "hepatitis B" should not appear when searching for "hepatitis C")
        if _is_cross_contaminated(tl, excluded_subtypes):
            print(f"  [Filter] Skipping cross-contaminated term: '{t}' (different disease subtype)")
            continue
        seen.add(tl)
        unique.append(t)
    return unique


def _build_cross_contamination_exclusions(indication_lower: str) -> Dict[str, set]:
    """Build exclusion rules based on the indication's disease family.

    For "hepatitis C", returns {'hepatitis': {'a', 'b', 'd', 'e'}} — the other
    subtypes that should be blocked.
    """
    exclusions = {}
    for stem, subtypes in _DISEASE_FAMILY_EXCLUSIONS.items():
        if stem in indication_lower:
            # Find which subtype the indication belongs to
            indication_subtype = None
            for st in subtypes:
                # Check for "hepatitis c", "hepatitis b", "type 1", "type 2", etc.
                if f"{stem} {st}" in indication_lower or f"type {st}" in indication_lower:
                    indication_subtype = st
                    break
            if indication_subtype:
                # Block all OTHER subtypes
                exclusions[stem] = subtypes - {indication_subtype}
    return exclusions


def _is_cross_contaminated(term_lower: str, excluded_subtypes: Dict[str, set]) -> bool:
    """Check if a term belongs to a different disease family subtype."""
    for stem, blocked in excluded_subtypes.items():
        if stem in term_lower:
            for st in blocked:
                if f"{stem} {st}" in term_lower or f"type {st}" in term_lower:
                    return True
                # Also catch abbreviations like "HBV" for hepatitis B, "HCV" for hepatitis C
                abbr_map = {'a': 'hav', 'b': 'hbv', 'c': 'hcv', 'd': 'hdv', 'e': 'hev'}
                if stem == 'hepatitis' and st in abbr_map:
                    if abbr_map[st] in term_lower:
                        return True
    return False


def search_fda_precedents(
    indication: str,
    search_terms: List[str],
    fda_search_func: Callable,
) -> List[Dict[str, Any]]:
    """
    Search FDA for approved drugs in the indication.

    Strategy (count-first):
    1. Use openFDA count endpoint to discover ALL unique NDA/BLA application numbers
       for labels mentioning the indication — zero noise, no limit issues.
    2. Fetch label details for each application number.

    Args:
        indication: The indication to search
        search_terms: Expanded list of search terms
        fda_search_func: MCP function for FDA lookups
    """
    import requests

    BASE_URL = "https://api.fda.gov/drug/label.json"

    # Step 1: Collect all NDA/BLA application numbers via count endpoint
    all_app_numbers = set()
    for term in search_terms:
        try:
            resp = requests.get(BASE_URL, params={
                'search': f'indications_and_usage:"{term}"',
                'count': 'openfda.application_number.exact',
                'limit': 1000,  # Max allowed; 100 was too low — ANDAs crowd out NDA/BLAs
            }, timeout=30)
            if resp.status_code != 200:
                print(f"  [FDA] Count query returned {resp.status_code} for '{term}'")
                continue

            counts = resp.json().get('results', [])
            nda_bla = [c['term'] for c in counts
                       if c['term'].startswith('NDA') or c['term'].startswith('BLA')]
            all_app_numbers.update(nda_bla)
            print(f"  [FDA] Found {len(nda_bla)} NDA/BLA apps for '{term}'")

        except Exception as e:
            print(f"  [FDA] Error in count query for '{term}': {e}")

    # Oncology subtype expansion: if umbrella term found few/no results, expand
    indication_lower = indication.lower()
    if len(all_app_numbers) < 3:
        for umbrella, subtypes in _ONCOLOGY_SUBTYPE_MAP.items():
            if umbrella in indication_lower:
                print(f"  [FDA] Umbrella term '{indication}' found <3 results. Expanding to subtypes: {subtypes}")
                for subtype in subtypes:
                    try:
                        resp = requests.get(BASE_URL, params={
                            'search': f'indications_and_usage:"{subtype}"',
                            'count': 'openfda.application_number.exact',
                            'limit': 1000,
                        }, timeout=30)
                        if resp.status_code != 200:
                            continue
                        counts = resp.json().get('results', [])
                        nda_bla = [c['term'] for c in counts
                                   if c['term'].startswith('NDA') or c['term'].startswith('BLA')]
                        if nda_bla:
                            all_app_numbers.update(nda_bla)
                            print(f"  [FDA] Subtype '{subtype}': +{len(nda_bla)} NDA/BLA apps")
                    except Exception as e:
                        print(f"  [FDA] Error expanding subtype '{subtype}': {e}")
                break  # Only expand once

    print(f"  [FDA] {len(all_app_numbers)} unique NDA/BLA applications total")

    if not all_app_numbers:
        return []

    # Step 2: Fetch label details for each application number
    precedents = []
    seen_generics = set()

    # Batch fetch: query up to 10 app numbers at a time (openFDA OR syntax)
    app_list = sorted(all_app_numbers)
    for batch_start in range(0, len(app_list), 10):
        batch = app_list[batch_start:batch_start + 10]
        or_clause = ' OR '.join(f'openfda.application_number.exact:"{a}"' for a in batch)
        try:
            resp = requests.get(BASE_URL, params={
                'search': or_clause,
                'limit': len(batch),
            }, timeout=30)
            if resp.status_code != 200:
                continue

            results = resp.json().get('results', [])
            for item in results:
                openfda = item.get('openfda', {})

                generic_names = openfda.get('generic_name', [])
                brand_names = openfda.get('brand_name', [])
                app_numbers = openfda.get('application_number', [])
                routes = openfda.get('route', [])
                manufacturers = openfda.get('manufacturer_name', [])

                generic = generic_names[0] if generic_names else ''
                if not generic or generic.lower() in seen_generics:
                    continue
                seen_generics.add(generic.lower())

                # Skip extremely long drug names (homeopathic combos)
                if len(generic) > 80:
                    continue

                app_number = app_numbers[0] if app_numbers else None
                pathway = _determine_pathway_from_app_number(app_number)

                indications = item.get('indications_and_usage', [])
                indication_text = indications[0][:300] if indications else ''

                precedent = {
                    'drug_name': _title_case_drug(generic),
                    'brand_name': _title_case_drug(brand_names[0]) if brand_names else _title_case_drug(generic),
                    'region': 'US',
                    'application_number': app_number,
                    'approval_pathway': pathway,
                    'approval_date': None,
                    'route': routes[0] if routes else 'Unknown',
                    'manufacturer': manufacturers[0] if manufacturers else 'Unknown',
                    'indication_snippet': indication_text,
                    'source': f'FDA ({app_number})' if app_number else 'FDA',
                }
                precedents.append(precedent)

        except Exception as e:
            print(f"  [FDA] Error fetching batch details: {e}")

    # Biosimilar → reference product recovery: if we found biosimilar variants
    # (e.g., "bevacizumab-awwb") but NOT the original (e.g., "bevacizumab"),
    # explicitly search for the reference product
    biosimilar_bases = set()
    existing_generics = {(p.get('drug_name') or '').lower() for p in precedents}
    for p in precedents:
        generic = (p.get('drug_name') or '').lower()
        # Biosimilar naming: base-suffix (e.g., bevacizumab-awwb, adalimumab-atto)
        if '-' in generic and len(generic.split('-')[-1]) <= 5:
            base = generic.rsplit('-', 1)[0]
            if base and base not in existing_generics:
                biosimilar_bases.add(base)

    for base_name in biosimilar_bases:
        try:
            resp = requests.get(BASE_URL, params={
                'search': f'openfda.generic_name:"{base_name}"',
                'limit': 1,
            }, timeout=30)
            if resp.status_code == 200:
                results = resp.json().get('results', [])
                for item in results:
                    openfda = item.get('openfda', {})
                    generic_names = openfda.get('generic_name', [])
                    brand_names = openfda.get('brand_name', [])
                    app_numbers = openfda.get('application_number', [])
                    routes = openfda.get('route', [])
                    manufacturers = openfda.get('manufacturer_name', [])

                    generic = generic_names[0] if generic_names else base_name
                    if generic.lower() in seen_generics:
                        continue
                    seen_generics.add(generic.lower())

                    app_number = app_numbers[0] if app_numbers else None
                    indications = item.get('indications_and_usage', [])
                    indication_text = indications[0][:300] if indications else ''

                    precedent = {
                        'drug_name': _title_case_drug(generic),
                        'brand_name': _title_case_drug(brand_names[0]) if brand_names else _title_case_drug(generic),
                        'region': 'US',
                        'application_number': app_number,
                        'approval_pathway': _determine_pathway_from_app_number(app_number),
                        'approval_date': None,
                        'route': routes[0] if routes else 'Unknown',
                        'manufacturer': manufacturers[0] if manufacturers else 'Unknown',
                        'indication_snippet': indication_text,
                        'source': f'FDA ({app_number})' if app_number else 'FDA',
                    }
                    precedents.append(precedent)
                    print(f"  [FDA] Recovered reference product: {precedent['brand_name']} ({base_name})")
        except Exception as e:
            print(f"  [FDA] Error recovering reference product '{base_name}': {e}")

    return precedents


def search_ema_precedents(
    indication: str,
    search_terms: List[str],
    ema_search_func: Callable,
) -> List[Dict[str, Any]]:
    """Search EMA for authorized medicines in the indication."""
    precedents = []
    seen_substances = set()

    # Filter search terms for EMA: skip short abbreviations (<4 chars)
    # that won't match EMA's therapeutic_area field meaningfully
    ema_terms = [t for t in search_terms if len(t) > 3]
    if not ema_terms:
        ema_terms = [indication]

    for term in ema_terms:
        try:
            result = ema_search_func(
                method="search_medicines",
                therapeutic_area=term,
                status="Authorised",
                limit=100,
            )

            # Handle different response structures
            # EMA API returns 'results' (not 'data'), with fields like
            # 'name_of_medicine', 'orphan_medicine', etc.
            data = []
            if isinstance(result, dict):
                if 'results' in result:
                    d = result['results']
                    data = d if isinstance(d, list) else []
                elif 'data' in result:
                    d = result['data']
                    data = d if isinstance(d, list) else []
                elif 'text' in result:
                    data = _parse_ema_text_response(result['text'])

            for med in data:
                substance = (
                    med.get('active_substance', '')
                    or med.get('international_non_proprietary_name_common_name', '')
                    or med.get('activeSubstance', '')
                )
                if not substance or substance.lower() in seen_substances:
                    continue
                seen_substances.add(substance.lower())

                medicine_name = (
                    med.get('name_of_medicine', '')
                    or med.get('medicine_name', '')
                    or med.get('medicineName', '')
                )
                auth_date = med.get('marketing_authorisation_date', '') or med.get('marketingAuthorisationDate', '')
                holder = (
                    med.get('marketing_authorisation_developer_applicant_holder', '')
                    or med.get('marketing_authorisation_holder', '')
                    or med.get('marketingAuthorisationHolder', '')
                )
                is_orphan = (
                    str(med.get('orphan_medicine', '')).lower() == 'yes'
                    or med.get('orphan', False)
                    or med.get('orphanMedicine', False)
                )
                is_conditional = (
                    str(med.get('conditional_approval', '')).lower() == 'yes'
                    or med.get('conditionalApproval', False)
                )
                is_prime = (
                    str(med.get('prime_priority_medicine', '')).lower() == 'yes'
                    or med.get('prime', False)
                )

                pathway = "Conditional MA" if is_conditional else "Centralized MAA"

                designations = []
                if is_orphan:
                    designations.append("Orphan (EU)")
                if is_prime:
                    designations.append("PRIME")

                ema_number = med.get('ema_product_number', '') or med.get('emaProductNumber', '')

                precedent = {
                    'drug_name': substance,
                    'brand_name': medicine_name,
                    'region': 'EU',
                    'application_number': ema_number or None,
                    'approval_pathway': pathway,
                    'approval_date': auth_date,
                    'route': None,
                    'manufacturer': holder,
                    'designations_granted': designations,
                    'source': f'EMA ({medicine_name})',
                }
                precedents.append(precedent)

        except Exception as e:
            print(f"  [EMA] Error searching for '{term}': {e}")
            continue

    return precedents


MAX_ENRICHMENT_DRUGS = 15  # Cap CT.gov enrichment to avoid 99 sequential API calls


def enrich_with_pivotal_trials(
    precedents: List[Dict[str, Any]],
    indication: str,
    ctgov_search_func: Callable,
    progress_callback=None,
) -> List[Dict[str, Any]]:
    """Enrich precedent drugs with pivotal trial information from CT.gov.

    Caps enrichment at MAX_ENRICHMENT_DRUGS to avoid excessive API calls
    for crowded indications (e.g., T2D with 99 drugs). Deduplicates by
    drug name (case-insensitive) to avoid enriching the same drug twice
    from FDA + EMA.
    """
    # Deduplicate: only enrich each drug name once (first occurrence wins)
    seen_drugs = set()
    enrichment_targets = []
    for prec in precedents:
        drug_name = (prec.get('drug_name') or '').lower().strip()
        if not drug_name or drug_name in seen_drugs:
            continue
        seen_drugs.add(drug_name)
        enrichment_targets.append(prec)

    # Cap at MAX_ENRICHMENT_DRUGS
    if len(enrichment_targets) > MAX_ENRICHMENT_DRUGS:
        print(f"  [CT.gov] Capping enrichment at {MAX_ENRICHMENT_DRUGS} drugs (of {len(enrichment_targets)} unique)")
        enrichment_targets = enrichment_targets[:MAX_ENRICHMENT_DRUGS]

    total = len(enrichment_targets)
    # Build lookup for sharing enrichment results with duplicate entries
    enrichment_results = {}

    for i, prec in enumerate(enrichment_targets):
        drug_name = prec.get('drug_name', '')
        if not drug_name:
            continue

        if progress_callback:
            progress_callback(i / max(total, 1), f"Enriching {drug_name} with trial data...")

        try:
            # Truncate drug name to 80 chars to avoid CT.gov 400 Bad Request
            search_name = drug_name[:80] if len(drug_name) > 80 else drug_name
            result = ctgov_search_func(
                method="search",
                condition=indication,
                intervention=search_name,
                phase="PHASE3",
                status="COMPLETED",
                pageSize=5,
            )

            text = result if isinstance(result, str) else result.get('text', '') if isinstance(result, dict) else ''
            trials = _parse_ct_trials(text)

            if trials:
                best_trial = max(trials, key=lambda t: t.get('enrollment', 0))
                prec['pivotal_trial'] = best_trial
            else:
                prec['pivotal_trial'] = None

            # Cache result for sharing with duplicate entries (same drug from different regions)
            enrichment_results[drug_name.lower().strip()] = prec.get('pivotal_trial')

        except Exception as e:
            print(f"  [CT.gov] Error searching trials for {drug_name}: {e}")
            prec['pivotal_trial'] = None
            enrichment_results[drug_name.lower().strip()] = None

    # Share enrichment results with non-enriched duplicates
    for prec in precedents:
        if 'pivotal_trial' not in prec:
            drug_key = (prec.get('drug_name') or '').lower().strip()
            prec['pivotal_trial'] = enrichment_results.get(drug_key)

    return precedents


def find_precedents(
    indication: str,
    target_regions: List[str] = None,
    mcp_funcs: Dict[str, Callable] = None,
    progress_callback=None,
) -> Dict[str, Any]:
    """
    Main precedent discovery function.

    Args:
        indication: Disease/condition to search
        target_regions: List of regions ["US", "EU"]
        mcp_funcs: Dict of MCP functions (injected by server or built for CLI)
        progress_callback: Callback(progress, message) for progress updates

    Returns:
        Dict with precedents, mode, search_terms, sources
    """
    if target_regions is None:
        target_regions = ["US", "EU"]
    if mcp_funcs is None:
        mcp_funcs = {}

    search_terms = resolve_indication_synonyms(indication, mcp_funcs)
    all_precedents = []
    sources = []

    fda_search = mcp_funcs.get('fda_search')
    ema_search = mcp_funcs.get('ema_search')
    ctgov_search = mcp_funcs.get('ctgov_search')

    # Step 1: Search FDA (US)
    if "US" in target_regions and fda_search:
        if progress_callback:
            progress_callback(0.0, f"Searching FDA for approved drugs in {indication}...")

        fda_precedents = search_fda_precedents(indication, search_terms, fda_search)
        all_precedents.extend(fda_precedents)
        sources.append(f"FDA openFDA API (searched: {', '.join(search_terms)})")

        if progress_callback:
            progress_callback(0.4, f"Found {len(fda_precedents)} FDA-approved drugs")

    # Step 2: Search EMA (EU)
    if "EU" in target_regions and ema_search:
        if progress_callback:
            progress_callback(0.4, f"Searching EMA for authorized medicines in {indication}...")

        ema_precedents = search_ema_precedents(indication, search_terms, ema_search)
        all_precedents.extend(ema_precedents)
        sources.append(f"EMA medicines database (searched: {', '.join(search_terms)})")

        if progress_callback:
            progress_callback(0.7, f"Found {len(ema_precedents)} EMA-authorized medicines")

    # Step 3: Enrich with pivotal trial data
    if all_precedents and ctgov_search:
        if progress_callback:
            progress_callback(0.7, "Enriching with pivotal trial data from CT.gov...")

        enrich_with_pivotal_trials(
            all_precedents,
            indication,
            ctgov_search,
            progress_callback=lambda p, m: progress_callback(0.7 + p * 0.3, m) if progress_callback else None,
        )
        sources.append("ClinicalTrials.gov (pivotal trial data)")

    # Dedup precedent rows: same drug_name + same region = duplicate
    seen_keys = set()
    deduped_precedents = []
    for p in all_precedents:
        key = ((p.get('drug_name') or '').lower(), p.get('region', ''))
        if key not in seen_keys:
            seen_keys.add(key)
            deduped_precedents.append(p)
    if len(deduped_precedents) < len(all_precedents):
        print(f"  [Dedup] Removed {len(all_precedents) - len(deduped_precedents)} duplicate precedent row(s)")
    all_precedents = deduped_precedents

    # Determine mode
    unique_drugs = set()
    for p in all_precedents:
        name = (p.get('drug_name') or '').lower()
        if name:
            unique_drugs.add(name)

    mode = "no_precedent" if len(unique_drugs) < NO_PRECEDENT_THRESHOLD else "precedent"

    if progress_callback:
        progress_callback(1.0, f"Precedent discovery complete: {len(all_precedents)} drugs, {len(unique_drugs)} unique ({mode} mode)")

    return {
        'precedents': all_precedents,
        'mode': mode,
        'unique_drug_count': len(unique_drugs),
        'search_terms': search_terms,
        'sources': sources,
    }


# ============================================================================
# Helper functions
# ============================================================================

def _title_case_drug(name: str) -> str:
    """Normalize drug name to title case, handling edge cases."""
    if not name:
        return name
    # If already mixed case, leave it
    if name != name.upper() and name != name.lower():
        return name
    return name.title()


def _determine_pathway_from_app_number(app_number: Optional[str]) -> str:
    """Determine FDA approval pathway from application number prefix."""
    if not app_number:
        return "Unknown"

    if app_number.startswith("BLA"):
        return "BLA"
    elif app_number.startswith("NDA"):
        return "NDA"
    elif app_number.startswith("ANDA"):
        return "ANDA (Generic)"
    else:
        return f"Unknown ({app_number[:3]})"


def _determine_pathway(app_number: Optional[str], drug_info: dict) -> str:
    """Determine FDA approval pathway from application number with submission detail."""
    if not app_number:
        return "Unknown"

    if app_number.startswith("BLA"):
        return "BLA"
    elif app_number.startswith("NDA"):
        submissions = drug_info.get('submissions', [])
        for sub in submissions:
            sub_type = sub.get('submission_type', '')
            if '505' in str(sub_type) or 'b)(2)' in str(sub_type):
                return "505(b)(2)"
        return "NDA"
    elif app_number.startswith("ANDA"):
        return "ANDA (Generic)"
    else:
        return f"Unknown ({app_number[:3]})"


def _extract_approval_date(drug_info: dict) -> Optional[str]:
    """Extract earliest approval date from FDA drug submissions."""
    submissions = drug_info.get('submissions', [])
    for sub in submissions:
        sub_status = sub.get('submission_status', '')
        sub_date = sub.get('submission_status_date', '')
        if sub_status and 'AP' in sub_status.upper() and sub_date:
            return sub_date

    products = drug_info.get('products', [])
    for prod in products:
        start = prod.get('marketing_start_date', '')
        if start:
            return start
    return None


def _parse_ema_text_response(text: str) -> List[Dict[str, Any]]:
    """Parse EMA text/markdown response into structured data."""
    medicines = []
    if not text:
        return medicines

    lines = text.split('\n')
    current = {}

    for line in lines:
        line = line.strip()
        if not line:
            if current:
                medicines.append(current)
                current = {}
            continue

        for key_pattern, field_name in [
            (r'\*\*Medicine[_ ]?[Nn]ame\*\*[:\s]+(.+)', 'medicine_name'),
            (r'\*\*Active[_ ]?[Ss]ubstance\*\*[:\s]+(.+)', 'active_substance'),
            (r'\*\*Status\*\*[:\s]+(.+)', 'authorisation_status'),
            (r'\*\*Date\*\*[:\s]+(.+)', 'marketing_authorisation_date'),
            (r'\*\*Holder\*\*[:\s]+(.+)', 'marketing_authorisation_holder'),
        ]:
            match = re.search(key_pattern, line)
            if match:
                current[field_name] = match.group(1).strip()

    if current:
        medicines.append(current)
    return medicines


def _parse_ct_trials(text: str) -> List[Dict[str, Any]]:
    """Parse CT.gov markdown search results into trial dicts."""
    trials = []
    if not text:
        return trials

    entries = re.split(r'###\s+\d+\.', text)
    for entry in entries:
        if not entry.strip():
            continue

        trial = {}
        nct_match = re.search(r'(NCT\d{8})', entry)
        if nct_match:
            trial['nct_id'] = nct_match.group(1)

        title_match = re.search(r'\*\*Title:\*\*\s*(.+?)(?:\n|$)', entry)
        if title_match:
            trial['title'] = title_match.group(1).strip()

        status_match = re.search(r'\*\*Status:\*\*\s*(.+?)(?:\n|$)', entry)
        if status_match:
            trial['status'] = status_match.group(1).strip()

        phase_match = re.search(r'\*\*Phase:\*\*\s*(.+?)(?:\n|$)', entry)
        if phase_match:
            trial['phase'] = phase_match.group(1).strip()

        enroll_match = re.search(r'\*\*Enrollment:\*\*\s*(\d+)', entry)
        if enroll_match:
            trial['enrollment'] = int(enroll_match.group(1))
        else:
            trial['enrollment'] = 0

        sponsor_match = re.search(r'\*\*(?:Lead\s+)?Sponsor:\*\*\s*(.+?)(?:\n|$)', entry)
        if sponsor_match:
            trial['sponsor'] = sponsor_match.group(1).strip()

        outcome_match = re.search(r'\*\*Primary\s+Outcome[s]?:\*\*\s*(.+?)(?:\n\*\*|\n###|\Z)', entry, re.DOTALL)
        if outcome_match:
            trial['primary_endpoints'] = outcome_match.group(1).strip()

        if trial.get('nct_id'):
            trials.append(trial)

    return trials


def _build_cli_mcp_funcs() -> Dict[str, Callable]:
    """Build MCP functions for CLI testing (outside server context)."""
    # Navigate from scripts/ -> skill/ -> skills/ -> .claude/
    _abs_script_dir = os.path.abspath(_script_dir)
    _claude_dir = os.path.dirname(os.path.dirname(os.path.dirname(_abs_script_dir)))
    mcp_path = os.path.join(_claude_dir, "mcp")

    # Add .claude dir so `from mcp.client import get_client` resolves
    if _claude_dir not in sys.path:
        sys.path.insert(0, _claude_dir)

    # Import from the __init__.py files in each server directory
    import importlib
    fda_mod = importlib.import_module("__init__")  # fda_mcp/__init__.py is first in path
    # Need to be explicit: load each __init__ from its directory
    import importlib.util

    def _load_module(name, path):
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    fda_mod = _load_module("fda_mcp", os.path.join(mcp_path, "servers", "fda_mcp", "__init__.py"))
    ema_mod = _load_module("ema_mcp", os.path.join(mcp_path, "servers", "ema_mcp", "__init__.py"))
    ct_mod = _load_module("ct_gov_mcp", os.path.join(mcp_path, "servers", "ct_gov_mcp", "__init__.py"))
    nlm_mod = _load_module("nlm_codes_mcp", os.path.join(mcp_path, "servers", "nlm_codes_mcp", "__init__.py"))
    ot_mod = _load_module("opentargets_mcp", os.path.join(mcp_path, "servers", "opentargets_mcp", "__init__.py"))

    lookup_drug = fda_mod.lookup_drug
    ema_info = ema_mod.ema_info
    ct_search = ct_mod.search

    def fda_wrapper(**kwargs):
        method = kwargs.pop('method', 'lookup_drug')
        return lookup_drug(**kwargs)

    def ema_wrapper(**kwargs):
        method = kwargs.pop('method', 'search_medicines')
        return ema_info(method=method, **kwargs)

    def ctgov_wrapper(**kwargs):
        method = kwargs.pop('method', 'search')
        return ct_search(**kwargs)

    def nlm_wrapper(**kwargs):
        method = kwargs.pop('method', 'conditions')
        if method == 'conditions':
            return nlm_mod.search_conditions(**kwargs)
        elif method == 'icd-10-cm':
            return nlm_mod.search_icd_10_cm(**kwargs)
        return nlm_mod.search_conditions(**kwargs)

    def opentargets_wrapper(**kwargs):
        method = kwargs.pop('method', 'search_diseases')
        if method == 'search_diseases':
            return ot_mod.search_diseases(**kwargs)
        elif method == 'search_targets':
            return ot_mod.search_targets(**kwargs)
        elif method == 'get_disease_targets_summary':
            return ot_mod.get_disease_targets_summary(**kwargs)
        return ot_mod.search_diseases(**kwargs)

    return {
        'fda_search': fda_wrapper,
        'ema_search': ema_wrapper,
        'ctgov_search': ctgov_wrapper,
        'nlm_search_codes': nlm_wrapper,
        'opentargets_search': opentargets_wrapper,
    }


if __name__ == "__main__":
    indication = sys.argv[1] if len(sys.argv) > 1 else "obesity"

    def progress(pct, msg):
        print(f"  [{pct:.0%}] {msg}")

    print(f"Building MCP clients for CLI testing...")
    mcp_funcs = _build_cli_mcp_funcs()
    print(f"MCP clients ready: {list(mcp_funcs.keys())}")

    result = find_precedents(
        indication,
        mcp_funcs=mcp_funcs,
        progress_callback=progress,
    )

    print(f"\nMode: {result['mode']}")
    print(f"Unique drugs: {result['unique_drug_count']}")
    print(f"Total precedents: {len(result['precedents'])}")

    for prec in result['precedents'][:10]:
        print(f"\n  {prec['brand_name']} ({prec['drug_name']})")
        print(f"    Region: {prec['region']} | Pathway: {prec['approval_pathway']}")
        print(f"    Approved: {prec.get('approval_date', 'N/A')}")
        if prec.get('pivotal_trial'):
            t = prec['pivotal_trial']
            print(f"    Pivotal: {t.get('nct_id', 'N/A')} ({t.get('enrollment', '?')} pts)")
