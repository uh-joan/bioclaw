#!/usr/bin/env python3
"""
Fix garbage drug names by extracting real interventions from CT.gov get_study().

For trials where intervention_name is junk (regex extraction from titles),
calls get_study(nctId) and parses the '### Drug: NAME' or '### Biological: NAME'
lines from the Interventions section.

Then resolves targets via OpenTargets.
"""
import sys, os, json, re, signal, time
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
os.environ['MCP_CONFIG_FILE'] = os.path.join(os.path.dirname(__file__), 'mcp-config.json')

import pandas as pd

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'trials_raw.csv')
CACHE_FILE = os.path.join(os.path.dirname(__file__), 'data', 'drug_target_cache.json')

# Load cache
cache = {}
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE) as f:
        cache = json.load(f)


class TimeoutError(Exception):
    pass

def _timeout(signum, frame):
    raise TimeoutError()

def safe_call(func, *args, timeout_sec=15, **kwargs):
    old = signal.signal(signal.SIGALRM, _timeout)
    signal.alarm(timeout_sec)
    try:
        r = func(*args, **kwargs)
        signal.alarm(0)
        return r
    except:
        signal.alarm(0)
        return None
    finally:
        signal.signal(signal.SIGALRM, old)


def is_garbage_name(name: str) -> bool:
    """Check if a drug name is likely garbage from title extraction."""
    if not name or name == 'nan':
        return True
    name = name.lower().strip()
    if len(name) < 3:
        return True
    # Known junk patterns
    junk = {'metastat', 'the efficacy', 'the safety', 'the effect', 'feasib',
            'beauty care', 'surgery alone', 'treatment', 'continued treatment',
            'anti', 'pre', 'post', 'use of', 'egf cancer', 'prostat',
            'neoadjuvant atezolizumab', 'preoperative short'}
    if name in junk:
        return True
    # Starts with common non-drug words
    if name.split()[0] in {'the', 'a', 'an', 'study', 'trial', 'phase', 'effect',
                            'use', 'compare', 'different', 'blue', 'short', 'long',
                            'continued', 'standard', 'stabilization', 'endocrine'}:
        return True
    # No pharma suffix AND not in target cache
    has_suffix = bool(re.search(r'mab|nib|lib|sib|tide|stat|pril|mycin|olol|zumab|ximab|umab|taxel|platin|tinib|ciclib|rafenib|lisib|sertib|cetinib|cillin|azole', name, re.I))
    if not has_suffix and name not in cache:
        return True
    return False


def extract_drugs_from_study(text: str) -> list:
    """Extract drug/biological names from CT.gov get_study() markdown."""
    # Pattern: ### Drug: NAME or ### Biological: NAME
    drugs = re.findall(r'###\s+(?:Drug|Biological|Combination Product|Dietary Supplement|Device):\s*(.+)', text)
    cleaned = []
    for d in drugs:
        # Clean up: take the drug name, strip dosing info
        name = d.strip()
        # Remove dosing: "Pembrolizumab 200mg Q3W" → "Pembrolizumab"
        name = re.split(r'\s+\d+\s*(?:mg|ml|mcg|µg|ug|mg/m2)', name, flags=re.I)[0].strip()
        # Remove code prefixes: "CP 690,550 5 mg" → "CP 690,550"
        # Remove parenthetical: "MDX-010 (anti-CTLA4)" → "MDX-010"
        name = re.sub(r'\s*\(.*?\)', '', name).strip()
        # Remove trailing slashes, commas
        name = name.rstrip('/, ')
        if name.lower() not in ('placebo', 'chemotherapy', 'standard of care', 'best supportive care',
                                 'observation', 'radiation', 'radiotherapy', 'surgery', ''):
            cleaned.append(name)
    return cleaned


def resolve_target_ot(drug: str) -> str:
    """Resolve via OpenTargets search_targets (fastest method)."""
    drug_lower = drug.lower().strip()
    if drug_lower in cache:
        return cache[drug_lower]

    from mcp.servers.opentargets_mcp import search_targets
    r = safe_call(search_targets, query=drug, size=1)
    if r:
        hits = r.get('data', {}).get('search', {}).get('hits', [])
        if hits:
            gene = hits[0].get('approvedSymbol', hits[0].get('name', ''))
            if gene and len(gene) <= 10:
                cache[drug_lower] = gene
                return gene
    cache[drug_lower] = ''
    return ''


def save_cache():
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)


def main():
    df = pd.read_csv(DATA_FILE, dtype=str)
    print(f"Loaded {len(df)} trials")

    # Find trials with garbage drug names
    garbage_idx = []
    for idx, row in df.iterrows():
        name = str(row.get('intervention_name', ''))
        if is_garbage_name(name):
            garbage_idx.append(idx)

    print(f"Trials with garbage drug names: {len(garbage_idx)}")

    from mcp.servers.ct_gov_mcp import get_study

    fixed = 0
    resolved = 0
    failed = 0

    for count, idx in enumerate(garbage_idx):
        row = df.iloc[idx]
        nct_id = str(row['nct_id'])
        old_name = str(row.get('intervention_name', ''))

        # Get study details
        r = safe_call(get_study, nctId=nct_id, timeout_sec=20)
        if not r:
            failed += 1
            continue

        text = r if isinstance(r, str) else r.get('text', str(r))
        drugs = extract_drugs_from_study(text)

        if not drugs:
            failed += 1
            if (count + 1) % 10 == 0:
                print(f"  [{count+1}/{len(garbage_idx)}] {nct_id} no interventions found")
            continue

        # Use the first real drug
        new_drug = drugs[0]
        df.at[idx, 'intervention_name'] = new_drug
        fixed += 1

        # Try to resolve target
        target = resolve_target_ot(new_drug)
        if target:
            resolved += 1

        print(f"  [{count+1}/{len(garbage_idx)}] {nct_id} \"{old_name}\" → \"{new_drug}\" target={target or '?'}")

        # Save periodically
        if (count + 1) % 20 == 0:
            df.to_csv(DATA_FILE, index=False)
            save_cache()

        time.sleep(0.3)

    df.to_csv(DATA_FILE, index=False)
    save_cache()

    total_targets = sum(1 for v in cache.values() if v)
    print(f"\nDone. Fixed {fixed} drug names, resolved {resolved} targets, {failed} failures.")
    print(f"Cache: {total_targets} drugs with targets / {len(cache)} total")


if __name__ == '__main__':
    main()
