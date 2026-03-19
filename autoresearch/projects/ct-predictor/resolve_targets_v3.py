#!/usr/bin/env python3
"""
Target resolution v3: DrugBank → UniProt chain for non-oncology drugs.

Strategy (in order):
1. Fix garbage drug names via CT.gov get_study() Interventions section
2. OpenTargets search (fast, works for targeted therapies)
3. DrugBank → target protein name → UniProt → gene symbol (works for everything)
4. Cache all results to disk
"""
import sys, os, json, re, signal, time
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
os.environ['MCP_CONFIG_FILE'] = os.path.join(os.path.dirname(__file__), 'mcp-config.json')

import pandas as pd

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'trials_raw.csv')
CACHE_FILE = os.path.join(os.path.dirname(__file__), 'data', 'drug_target_cache.json')

cache = {}
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE) as f:
        cache = json.load(f)

class TO(Exception): pass
def _to(s,f): raise TO()
def sc(func, *a, timeout_sec=15, **kw):
    old = signal.signal(signal.SIGALRM, _to)
    signal.alarm(timeout_sec)
    try:
        r = func(*a, **kw)
        signal.alarm(0)
        return r
    except:
        signal.alarm(0)
        return None
    finally:
        signal.signal(signal.SIGALRM, old)

def save_cache():
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)

JUNK_NAMES = {'la','ct','the','an','mp','mra','treatment','anti','pro','pre','post',
              'surgery','use of','different','blue','morning','continued','stabilization',
              'endocrine','beauty','standard','egf cancer','nonmetastat','unknown','nan','',
              'ubiquitous sr','mri and','efficacy and','the efficacy','the safety',
              'the effect','the pain','the evolution','the addition','the anti','the proposed',
              'the effects','an individual','diminished bone','cytokine'}

def is_garbage(name):
    if not name or name == 'nan': return True
    name = name.lower().strip()
    return name in JUNK_NAMES or len(name) < 3


# === Phase 1: Fix garbage drug names ===

def fix_garbage_names():
    """Extract real drug names from CT.gov Interventions section."""
    from mcp.servers.ct_gov_mcp import get_study

    df = pd.read_csv(DATA_FILE, dtype=str)
    garbage_idx = [i for i, row in df.iterrows() if is_garbage(str(row.get('intervention_name', '')))]
    print(f"Phase 1: Fixing {len(garbage_idx)} garbage drug names")

    fixed = 0
    for count, idx in enumerate(garbage_idx):
        nct_id = str(df.at[idx, 'nct_id'])
        old = str(df.at[idx, 'intervention_name'])

        r = sc(get_study, nctId=nct_id, timeout_sec=20)
        if not r: continue
        text = r if isinstance(r, str) else r.get('text', str(r))

        drugs = re.findall(r'###\s+(?:Drug|Biological):\s*(.+)', text)
        if not drugs: continue

        new_drug = drugs[0].strip()
        new_drug = re.split(r'\s+\d+\s*(?:mg|ml|mcg)', new_drug, flags=re.I)[0].strip()
        new_drug = re.sub(r'\s*\(.*?\)', '', new_drug).strip().rstrip('/, ')
        if new_drug.lower() in ('placebo','chemotherapy','standard of care','observation','radiation',''):
            continue

        df.at[idx, 'intervention_name'] = new_drug
        fixed += 1
        if (count+1) % 20 == 0:
            df.to_csv(DATA_FILE, index=False)
            print(f"  [{count+1}/{len(garbage_idx)}] fixed={fixed}", flush=True)
        time.sleep(0.2)

    df.to_csv(DATA_FILE, index=False)
    print(f"Phase 1 done. Fixed {fixed} drug names.")


# === Phase 2: Resolve targets ===

def resolve_via_opentargets(drug):
    """Fast: OpenTargets search_targets."""
    from mcp.servers.opentargets_mcp import search_targets
    r = sc(search_targets, query=drug, size=1, timeout_sec=10)
    if r:
        hits = r.get('data', {}).get('search', {}).get('hits', [])
        if hits:
            gene = hits[0].get('approvedSymbol', hits[0].get('name', ''))
            if gene and len(gene) <= 10 and gene.replace('-','').isalpha():
                return gene
    return ''


def resolve_via_drugbank_uniprot(drug):
    """Reliable: DrugBank → target protein name → UniProt → gene symbol."""
    from mcp.servers.drugbank_mcp import search_by_name, get_drug_details
    from mcp.client import get_client

    r = sc(search_by_name, query=drug, timeout_sec=15)
    if not r or not isinstance(r, dict): return ''
    results = r.get('results', [])
    if not results: return ''

    db_id = results[0].get('drugbank_id', '')
    if not db_id: return ''

    details = sc(get_drug_details, drugbank_id=db_id, timeout_sec=15)
    if not details: return ''
    dd = details.get('drug', details.get('data', {}))
    if not isinstance(dd, dict): return ''

    targets = dd.get('targets', [])
    if not targets: return ''

    # Get first target's name, search UniProt for gene symbol
    target_name = targets[0].get('name', '')
    if not target_name or target_name.lower() in ('dna', 'rna'): return ''

    uc = get_client('uniprot')
    ur = sc(uc.call_tool, 'uniprot_data',
            {'method': 'search_proteins', 'query': target_name, 'organism': 'human'},
            timeout_sec=15)
    if ur and isinstance(ur, dict):
        results = ur.get('results', [])
        if results:
            genes = results[0].get('genes', [])
            if genes:
                gene = genes[0].get('geneName', {}).get('value', '')
                if gene and len(gene) <= 15:
                    return gene
    return ''


def resolve_all():
    """Resolve targets for all unresolved drugs."""
    df = pd.read_csv(DATA_FILE, dtype=str)
    drugs = set(str(d).lower().strip() for d in df['intervention_name'].dropna().unique()
                if str(d).strip() not in ('', 'nan', 'unknown') and not is_garbage(str(d)))

    # Only resolve drugs not yet in cache
    to_resolve = [d for d in drugs if d not in cache]
    # Also retry empty cache entries (previous failures might work with DrugBank→UniProt)
    to_retry = [d for d in drugs if d in cache and cache[d] == '' and d not in JUNK_NAMES]

    print(f"Phase 2: {len(to_resolve)} new + {len(to_retry)} retries = {len(to_resolve)+len(to_retry)} drugs")

    all_drugs = to_resolve + to_retry
    resolved_ot = 0
    resolved_db = 0
    failed = 0

    for i, drug in enumerate(all_drugs):
        if is_garbage(drug):
            cache[drug] = ''
            continue

        # Strategy 1: OpenTargets (fast)
        gene = resolve_via_opentargets(drug)
        if gene:
            cache[drug] = gene
            resolved_ot += 1
            if (i+1) % 20 == 0:
                print(f"  [{i+1}/{len(all_drugs)}] OT: {drug} → {gene}", flush=True)
        else:
            # Strategy 2: DrugBank → UniProt (reliable for non-oncology)
            gene = resolve_via_drugbank_uniprot(drug)
            if gene:
                cache[drug] = gene
                resolved_db += 1
                print(f"  [{i+1}/{len(all_drugs)}] DB→UP: {drug} → {gene}", flush=True)
            else:
                cache[drug] = ''
                failed += 1

        if (i+1) % 30 == 0:
            save_cache()

        time.sleep(0.2)

    save_cache()

    # Map raw drug names in CSV to cleaned cache entries
    df = pd.read_csv(DATA_FILE, dtype=str)
    for idx, row in df.iterrows():
        drug_raw = str(row.get('intervention_name', '')).lower().strip()
        if drug_raw not in cache:
            # Try first word (for "drug + combo" patterns)
            first = drug_raw.split('+')[0].split(' plus ')[0].split(' and ')[0].strip()
            if first in cache and cache[first]:
                cache[drug_raw] = cache[first]

    save_cache()

    total = sum(1 for v in cache.values() if v)
    print(f"\nPhase 2 done. OT: {resolved_ot}, DB→UP: {resolved_db}, failed: {failed}")
    print(f"Cache: {total} with targets / {len(cache)} total")

    # Coverage
    drugs_in_csv = df['intervention_name'].str.lower().str.strip()
    has_target = sum(1 for d in drugs_in_csv if pd.notna(d) and cache.get(str(d), ''))
    print(f"Trial coverage: {has_target}/{len(df)} ({has_target/len(df):.0%})")


def main():
    fix_garbage_names()
    resolve_all()


if __name__ == '__main__':
    main()
