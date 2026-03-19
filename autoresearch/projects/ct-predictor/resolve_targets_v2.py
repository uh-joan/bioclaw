#!/usr/bin/env python3
"""
Resolve drug → target gene for all trials.

Strategy (in order):
1. Clean drug name (strip combos, prefixes, junk)
2. OpenTargets search_targets (drug name → gene directly) — best
3. DrugBank target name → OpenTargets gene lookup — fallback
4. ChEMBL mechanism chain — last resort

Saves to data/drug_target_cache.json incrementally.
"""
import sys, os, json, re, signal, time
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
os.environ['MCP_CONFIG_FILE'] = os.path.join(os.path.dirname(__file__), 'mcp-config.json')

import pandas as pd

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'trials_raw.csv')
CACHE_FILE = os.path.join(os.path.dirname(__file__), 'data', 'drug_target_cache.json')

# Load existing cache
cache = {}
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE) as f:
        cache = json.load(f)
print(f"Loaded cache: {sum(1 for v in cache.values() if v)} with targets, {len(cache)} total")


class TimeoutError(Exception):
    pass

def _timeout_handler(signum, frame):
    raise TimeoutError()

def safe_call(func, *args, timeout_sec=15, **kwargs):
    old = signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(timeout_sec)
    try:
        result = func(*args, **kwargs)
        signal.alarm(0)
        return result
    except TimeoutError:
        return None
    except Exception:
        signal.alarm(0)
        return None
    finally:
        signal.signal(signal.SIGALRM, old)


def save_cache():
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)


def clean_drug_name(raw: str) -> str:
    """Clean a raw drug name extracted from a trial title."""
    if not raw or raw == 'nan':
        return ''

    name = raw.lower().strip()

    # Take first drug from combinations
    for sep in [' + ', ' plus ', ' and ', ' with ', ' combined with ', ' in combination with ']:
        if sep in name:
            name = name.split(sep)[0].strip()

    # Remove common prefixes/suffixes that aren't drug names
    junk_patterns = [
        r'^(neoadjuvant|adjuvant|preoperative|postoperative|oral|intravenous|iv|subcutaneous)\s+',
        r'\s+(versus|vs|compared|with|for|in|on|alone|arm|group|treatment|therapy|regimen).*$',
        r'\s+(dose|dosing|doses|mg|ml|mcg)\s*\d*.*$',
        r'^\d+\s*',  # leading numbers
    ]
    for pat in junk_patterns:
        name = re.sub(pat, '', name, flags=re.IGNORECASE).strip()

    # Skip obvious non-drug names
    junk_names = {'the', 'a', 'an', 'study', 'trial', 'phase', 'treatment', 'therapy',
                  'surgery', 'radiation', 'placebo', 'control', 'standard', 'care',
                  'chemotherapy', 'immunotherapy', 'combination', 'efficacy', 'safety',
                  'effect', 'use', 'beauty', 'feasib', 'continued', 'anti', 'pre', 'post',
                  'la', 'cp', 'bp', 'mk', 'bms', 'mw', 'dlbs', 'sibp', 'uft', 'nab',
                  'abi', 'fes', 'egf', 'pet', ''}
    if name in junk_names or len(name) < 3:
        return ''

    return name


def resolve_via_opentargets(drug: str) -> str:
    """Best method: OpenTargets search returns gene directly from drug name."""
    from mcp.servers.opentargets_mcp import search_targets
    r = safe_call(search_targets, query=drug, size=1)
    if r:
        hits = r.get('data', {}).get('search', {}).get('hits', [])
        if hits:
            gene = hits[0].get('name', '')  # 'name' field IS the gene symbol
            gene_id = hits[0].get('id', '')  # Ensembl ID
            # Verify it's actually a gene (not a random text match)
            if gene and gene.isupper() and len(gene) <= 10:
                return gene
            # Sometimes 'name' is the full name, try approvedSymbol
            symbol = hits[0].get('approvedSymbol', '')
            if symbol:
                return symbol
    return ''


def resolve_via_drugbank(drug: str) -> str:
    """Fallback: DrugBank → target protein name → OpenTargets → gene symbol."""
    from mcp.servers.drugbank_mcp import search_by_name, get_drug_details
    from mcp.servers.opentargets_mcp import search_targets

    r = safe_call(search_by_name, query=drug)
    if not r:
        return ''
    results = r.get('results', [])
    if not results:
        return ''

    db_id = results[0].get('drugbank_id', '')
    if not db_id:
        return ''

    details = safe_call(get_drug_details, drugbank_id=db_id)
    if not details:
        return ''

    dd = details.get('drug', details.get('data', {}))
    if not isinstance(dd, dict):
        return ''

    targets = dd.get('targets', [])
    if not targets:
        return ''

    # Use the first target's name to search OpenTargets
    target_name = targets[0].get('name', '')
    if target_name:
        r2 = safe_call(search_targets, query=target_name, size=1)
        if r2:
            hits = r2.get('data', {}).get('search', {}).get('hits', [])
            if hits:
                symbol = hits[0].get('name', hits[0].get('approvedSymbol', ''))
                if symbol and len(symbol) <= 10:
                    return symbol
    return ''


def resolve_via_chembl(drug: str) -> str:
    """Last resort: ChEMBL compound → mechanism → target → gene."""
    from mcp.servers.chembl_mcp import compound_search, get_mechanism, target_search

    r = safe_call(compound_search, query=drug, limit=1)
    if not r:
        return ''
    mols = r.get('molecules', [])
    if not mols:
        return ''

    cid = mols[0].get('molecule_chembl_id', '')
    if not cid:
        return ''

    mech = safe_call(get_mechanism, chembl_id=cid)
    if not mech:
        return ''
    mechs = mech.get('mechanisms', [])
    if not mechs:
        return ''

    target_cid = mechs[0].get('target_chembl_id', '')
    if not target_cid:
        return ''

    t = safe_call(target_search, query=target_cid, limit=1)
    if not t:
        return ''
    targets = t.get('targets', [])
    if not targets:
        return ''

    components = targets[0].get('components', [])
    if not components:
        return ''

    synonyms = components[0].get('synonyms', [])
    gene = next((s for s in synonyms if s.isupper() and len(s) <= 10 and s.isalpha()), '')
    return gene


def resolve_target(drug_raw: str) -> str:
    """Multi-strategy target resolution."""
    drug = clean_drug_name(drug_raw)
    if not drug:
        return ''

    # Check cache first (with cleaned name)
    if drug in cache:
        return cache[drug]

    # Strategy 1: OpenTargets (fastest, most reliable)
    gene = resolve_via_opentargets(drug)
    if gene:
        cache[drug] = gene
        return gene

    # Strategy 2: DrugBank → OpenTargets
    gene = resolve_via_drugbank(drug)
    if gene:
        cache[drug] = gene
        return gene

    # Strategy 3: ChEMBL chain
    gene = resolve_via_chembl(drug)
    if gene:
        cache[drug] = gene
        return gene

    # Mark as tried but failed
    cache[drug] = ''
    return ''


def main():
    df = pd.read_csv(DATA_FILE, dtype=str)
    drugs_raw = df['intervention_name'].dropna().unique()
    drugs_raw = [str(d) for d in drugs_raw if str(d).strip() and str(d) != 'nan']

    # Also try raw names mapped to cleaned names
    unique_cleaned = {}
    for raw in drugs_raw:
        cleaned = clean_drug_name(raw)
        if cleaned and cleaned not in cache:
            unique_cleaned[cleaned] = raw

    # Also add combination splits
    for raw in drugs_raw:
        name = str(raw).lower().strip()
        for sep in [' + ', ' plus ', ' and ', ' with ']:
            if sep in name:
                first = name.split(sep)[0].strip()
                if first and first not in cache and len(first) >= 3:
                    unique_cleaned[first] = raw

    to_resolve = [d for d in unique_cleaned if d not in cache]
    already_resolved = sum(1 for v in cache.values() if v)

    print(f"Drugs to resolve: {len(to_resolve)}")
    print(f"Already in cache: {len(cache)} ({already_resolved} with targets)")

    new_resolved = 0
    new_failed = 0

    for i, drug in enumerate(to_resolve):
        gene = resolve_target(drug)

        if gene:
            new_resolved += 1
            print(f"  [{i+1}/{len(to_resolve)}] ✓ {drug:30s} → {gene}")
        else:
            new_failed += 1
            if (i + 1) % 10 == 0:
                print(f"  [{i+1}/{len(to_resolve)}]   ({new_resolved} resolved, {new_failed} failed)")

        # Save every 10
        if (i + 1) % 10 == 0:
            save_cache()

        time.sleep(0.3)  # Rate limit

    save_cache()

    # Now update the cache for raw drug names (map raw → cleaned → target)
    for raw in drugs_raw:
        raw_lower = str(raw).lower().strip()
        if raw_lower not in cache or not cache[raw_lower]:
            cleaned = clean_drug_name(raw)
            if cleaned and cleaned in cache and cache[cleaned]:
                cache[raw_lower] = cache[cleaned]

    save_cache()

    total_resolved = sum(1 for v in cache.values() if v)
    print(f"\nDone. New: {new_resolved} resolved, {new_failed} failed.")
    print(f"Cache total: {total_resolved} with targets, {len(cache)} entries")

    # Coverage on actual trials
    trial_drugs = df['intervention_name'].str.lower().str.strip()
    has_target = trial_drugs.map(lambda d: bool(cache.get(d, '') or cache.get(clean_drug_name(d), ''))).sum()
    print(f"Trial coverage: {has_target}/{len(df)} ({has_target/len(df):.0%})")


if __name__ == '__main__':
    main()
