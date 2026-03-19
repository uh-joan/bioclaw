#!/usr/bin/env python3
"""
Parallel backfill — splits trials into N workers, each with its own MCP server instances.
Staggered starts (5s between workers) to avoid rate limit spikes.
Each worker writes to a separate temp CSV, then merged at the end.
"""
import sys, os, json, signal, re, time, csv, multiprocessing
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import pandas as pd

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'trials_raw.csv')
CACHE_FILE = os.path.join(os.path.dirname(__file__), 'data', 'drug_target_cache.json')
COLUMNS_FILE = os.path.join(os.path.dirname(__file__), 'collect.py')

N_WORKERS = 4
TIMEOUT_SEC = 12  # Reduced from 15-20 to speed up
RATE_LIMIT_DELAY = 0.5  # Seconds between MCP calls within a worker


# Import the canonical enrich function from backfill_safe
from backfill_safe import enrich_trial as _enrich_trial_safe


def enrich_one(drug, target, condition):
    """Wrapper that calls backfill_safe.enrich_trial with rate limiting."""
    result = _enrich_trial_safe(drug, target, condition)
    time.sleep(RATE_LIMIT_DELAY)  # Rate limit between trials
    return result


def worker(worker_id, trial_indices, drug_target, columns):
    """Process a batch of trials. Writes results to a temp file."""
    # Stagger start
    time.sleep(worker_id * 5)

    # Setup env for this process
    os.environ['MCP_CONFIG_FILE'] = os.path.join(os.path.dirname(__file__), 'mcp-config.json')

    df = pd.read_csv(DATA_FILE, dtype=str)
    temp_file = os.path.join(os.path.dirname(__file__), 'data', f'backfill_worker_{worker_id}.json')
    results = {}

    for count, idx in enumerate(trial_indices):
        row = df.iloc[idx]
        drug = str(row.get('intervention_name', '')).lower().strip()
        condition = str(row.get('condition', ''))
        target = drug_target.get(drug, '')
        nct_id = str(row.get('nct_id', ''))

        if not drug or drug == 'nan':
            continue

        features = enrich_one(drug, target, condition)

        # Filter to only new values
        new_fields = {}
        for col, val in features.items():
            if val not in (None, '', 'nan'):
                current = str(row.get(col, '')).strip()
                if current in ('', 'nan', 'None'):
                    new_fields[col] = str(val)

        if new_fields:
            results[nct_id] = new_fields

        if (count + 1) % 5 == 0:
            # Save progress
            with open(temp_file, 'w') as f:
                json.dump(results, f)
            print(f"  [W{worker_id}] {count+1}/{len(trial_indices)} processed, {len(results)} updated", flush=True)

    # Final save
    with open(temp_file, 'w') as f:
        json.dump(results, f)
    print(f"  [W{worker_id}] DONE: {len(results)} trials enriched", flush=True)
    return temp_file


def main():
    # Load data and cache
    df = pd.read_csv(DATA_FILE, dtype=str)
    df = df.drop_duplicates(subset='nct_id', keep='first').reset_index(drop=True)

    drug_target = {}
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            drug_target = {k: v for k, v in json.load(f).items() if v}
    print(f"Loaded {len(drug_target)} drug→target mappings")

    # Find trials needing enrichment
    mcp_cols = ['chembl_selectivity', 'gnomad_pli', 'reactome_pathway_count', 'depmap_essentiality']
    needs_enrichment = []
    for idx, row in df.iterrows():
        filled = sum(1 for c in mcp_cols if pd.notna(row.get(c)) and str(row.get(c,'')).strip() not in ('','nan'))
        if filled < 3:
            needs_enrichment.append(idx)

    print(f"Trials needing enrichment: {len(needs_enrichment)}/{len(df)}")
    print(f"Workers: {N_WORKERS}")

    # Split into batches
    batch_size = len(needs_enrichment) // N_WORKERS + 1
    batches = [needs_enrichment[i:i+batch_size] for i in range(0, len(needs_enrichment), batch_size)]

    from collect import COLUMNS

    # Run workers sequentially (can't fork with MCP stdio subprocesses)
    # But each worker staggers its MCP calls
    # Actually, use multiprocessing with fork
    print(f"Starting {len(batches)} workers...")

    processes = []
    for i, batch in enumerate(batches):
        p = multiprocessing.Process(target=worker, args=(i, batch, drug_target, COLUMNS))
        p.start()
        processes.append(p)
        print(f"  Worker {i} started: {len(batch)} trials")

    # Wait for all
    for p in processes:
        p.join()

    print("\nAll workers done. Merging results...")

    # Merge temp files into main CSV
    df = pd.read_csv(DATA_FILE, dtype=str)
    df = df.drop_duplicates(subset='nct_id', keep='first').reset_index(drop=True)

    total_updates = 0
    for i in range(len(batches)):
        temp_file = os.path.join(os.path.dirname(__file__), 'data', f'backfill_worker_{i}.json')
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
    print(f"Merged {total_updates} trial updates into {DATA_FILE}")

    # Final stats
    for c in mcp_cols + ['ot_overall_score', 'fda_prior_approval_class', 'hpo_phenotype_count',
                          'pubmed_target_pub_count', 'drugbank_half_life_hours']:
        if c in df.columns:
            f = (df[c].notna() & (df[c] != '') & (df[c].astype(str) != 'nan')).sum()
            print(f"  {f:3d}/{len(df)} {c}")


if __name__ == '__main__':
    main()
