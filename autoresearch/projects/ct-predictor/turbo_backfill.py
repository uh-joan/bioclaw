#!/usr/bin/env python3
"""
Turbo backfill: resolve targets + 8-worker parallel enrichment.

Phase 1: Resolve drug→target for all unresolved drugs via OpenTargets (fast, 1 API call each)
Phase 2: 8-worker parallel backfill with 1s stagger, 0.3s rate limit between MCP calls
"""
import sys, os, json, signal, time, re, multiprocessing
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
os.environ['MCP_CONFIG_FILE'] = os.path.join(os.path.dirname(__file__), 'mcp-config.json')

import pandas as pd

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'trials_raw.csv')
CACHE_FILE = os.path.join(os.path.dirname(__file__), 'data', 'drug_target_cache.json')

N_WORKERS = 8
RATE_LIMIT_DELAY = 0.3


class TimeoutError(Exception):
    pass

def _to(s, f):
    raise TimeoutError()

def sc(func, *a, timeout_sec=12, **kw):
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


# ============================================================
# Phase 1: Resolve targets via OpenTargets
# ============================================================

def resolve_targets():
    """Resolve all unresolved drug→target mappings via OpenTargets."""
    cache = {}
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            cache = json.load(f)

    df = pd.read_csv(DATA_FILE, dtype=str)
    drugs = set(str(d).lower().strip() for d in df['intervention_name'].dropna().unique()
                if str(d).strip() not in ('', 'nan', 'unknown'))

    to_resolve = [d for d in drugs if d not in cache]
    print(f"Phase 1: Resolving {len(to_resolve)} drugs (cache has {len(cache)})")

    if not to_resolve:
        return cache

    from mcp.servers.opentargets_mcp import search_targets

    resolved = 0
    for i, drug in enumerate(to_resolve):
        r = sc(search_targets, query=drug, size=1, timeout_sec=10)
        if r:
            hits = r.get('data', {}).get('search', {}).get('hits', [])
            if hits:
                gene = hits[0].get('approvedSymbol', hits[0].get('name', ''))
                if gene and len(gene) <= 10:
                    # Filter out garbage matches
                    if drug in ('the', 'a', 'an', 'or', 'use', 'anti', 'pre', 'pro', 'long', 'short',
                                'treatment', 'surgery', 'different', 'blue', 'morning', 'continued',
                                'stabilization', 'endocrine', 'beauty', 'standard'):
                        cache[drug] = ''
                    else:
                        cache[drug] = gene
                        resolved += 1
                else:
                    cache[drug] = ''
            else:
                cache[drug] = ''
        else:
            cache[drug] = ''

        if (i + 1) % 50 == 0:
            with open(CACHE_FILE, 'w') as f:
                json.dump(cache, f, indent=2)
            print(f"  [{i+1}/{len(to_resolve)}] resolved={resolved}", flush=True)

        time.sleep(0.2)  # Rate limit for OpenTargets

    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)

    total = sum(1 for v in cache.values() if v)
    print(f"Phase 1 done. {resolved} new targets. Cache: {total} with targets / {len(cache)} total")
    return cache


# ============================================================
# Phase 2: Parallel backfill
# ============================================================

def worker(worker_id, trial_indices, drug_target):
    """Process a batch of trials."""
    time.sleep(worker_id * 1)  # Stagger start by 1s per worker

    os.environ['MCP_CONFIG_FILE'] = os.path.join(os.path.dirname(__file__), 'mcp-config.json')

    df = pd.read_csv(DATA_FILE, dtype=str)
    temp_file = os.path.join(os.path.dirname(__file__), 'data', f'turbo_worker_{worker_id}.json')
    results = {}

    from backfill_safe import enrich_trial

    for count, idx in enumerate(trial_indices):
        row = df.iloc[idx]
        drug = str(row.get('intervention_name', '')).lower().strip()
        condition = str(row.get('condition', ''))
        target = drug_target.get(drug, '')
        nct_id = str(row.get('nct_id', ''))

        if not drug or drug in ('nan', 'unknown', ''):
            continue

        features = enrich_trial(drug, target, condition)
        time.sleep(RATE_LIMIT_DELAY)

        new_fields = {}
        for col, val in features.items():
            if val not in (None, '', 'nan'):
                current = str(row.get(col, '')).strip()
                if current in ('', 'nan', 'None'):
                    new_fields[col] = str(val)

        if new_fields:
            results[nct_id] = new_fields

        if (count + 1) % 5 == 0:
            with open(temp_file, 'w') as f:
                json.dump(results, f)
            print(f"  [W{worker_id}] {count+1}/{len(trial_indices)} processed, {len(results)} updated", flush=True)

    with open(temp_file, 'w') as f:
        json.dump(results, f)
    print(f"  [W{worker_id}] DONE: {len(results)} trials enriched", flush=True)


def parallel_backfill(drug_target):
    """Run N_WORKERS parallel backfill processes."""
    df = pd.read_csv(DATA_FILE, dtype=str)
    df = df.drop_duplicates(subset='nct_id', keep='first').reset_index(drop=True)

    # Find trials needing enrichment (fewer than 3 key MCP features filled)
    mcp_cols = ['chembl_selectivity', 'gnomad_pli', 'reactome_pathway_count',
                'pubchem_molecular_weight', 'pdb_structure_count']
    needs = []
    for idx, row in df.iterrows():
        filled = sum(1 for c in mcp_cols if c in df.columns and
                     pd.notna(row.get(c)) and str(row.get(c, '')).strip() not in ('', 'nan'))
        if filled < 3:
            needs.append(idx)

    print(f"Phase 2: {len(needs)}/{len(df)} trials need enrichment, {N_WORKERS} workers")

    if not needs:
        print("All trials already enriched!")
        return

    # Split into batches
    batch_size = len(needs) // N_WORKERS + 1
    batches = [needs[i:i + batch_size] for i in range(0, len(needs), batch_size)]

    processes = []
    for i, batch in enumerate(batches):
        p = multiprocessing.Process(target=worker, args=(i, batch, drug_target))
        p.start()
        processes.append(p)
        print(f"  Worker {i} started: {len(batch)} trials")

    for p in processes:
        p.join()

    # Merge
    print("\nMerging results...")
    df = pd.read_csv(DATA_FILE, dtype=str)
    df = df.drop_duplicates(subset='nct_id', keep='first').reset_index(drop=True)

    total_updates = 0
    for i in range(len(batches)):
        temp_file = os.path.join(os.path.dirname(__file__), 'data', f'turbo_worker_{i}.json')
        if os.path.exists(temp_file):
            with open(temp_file) as f:
                results = json.load(f)
            for nct_id, features in results.items():
                mask = df['nct_id'] == nct_id
                if mask.any():
                    idx = mask.idxmax()
                    for col, val in features.items():
                        if col in df.columns:
                            df.at[idx, col] = str(val)
                    total_updates += 1
            os.remove(temp_file)

    df.to_csv(DATA_FILE, index=False)
    print(f"Merged {total_updates} trial updates")

    # Stats
    for c in ['chembl_selectivity', 'pubchem_molecular_weight', 'alphafold_confidence',
              'nlm_condition_codes', 'pdb_structure_count', 'go_term_count',
              'cosmic_mutation_count', 'gnomad_pli', 'reactome_pathway_count']:
        if c in df.columns:
            f = (df[c].notna() & (df[c] != '') & (df[c].astype(str) != 'nan')).sum()
            print(f"  {f:4d}/{len(df)} {c}")


def main():
    # Phase 1: Resolve targets
    drug_target = resolve_targets()
    drug_target = {k: v for k, v in drug_target.items() if v}

    # Phase 2: Parallel backfill
    parallel_backfill(drug_target)


if __name__ == '__main__':
    main()
