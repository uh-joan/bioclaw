#!/usr/bin/env python3
"""
Backfill biorxiv_preprint_count for all drugs.
Drug-only feature — no target gene needed.
Searches both bioRxiv and medRxiv with a wide date range.
"""
import sys, os, signal, time
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
os.environ['MCP_CONFIG_FILE'] = os.path.join(os.path.dirname(__file__), 'mcp-config.json')

import pandas as pd

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'trials_raw.csv')

class TO(Exception): pass
def _to(s, f): raise TO()
def sc(func, *a, timeout_sec=15, **kw):
    old = signal.signal(signal.SIGALRM, _to)
    signal.alarm(timeout_sec)
    try: r = func(*a, **kw); signal.alarm(0); return r
    except: signal.alarm(0); return None
    finally: signal.signal(signal.SIGALRM, old)


def get_biorxiv_count(drug):
    """Search bioRxiv + medRxiv for preprints mentioning this drug."""
    from mcp.servers.biorxiv_mcp import search_preprints
    total = 0

    for server in ['biorxiv', 'medrxiv']:
        r = sc(search_preprints, query=drug, server=server,
               date_from='2015-01-01', date_to='2026-03-21', limit=50)
        if r and isinstance(r, dict):
            count = r.get('count', 0)
            if isinstance(count, int):
                total += count
            else:
                preprints = r.get('preprints', [])
                if isinstance(preprints, list):
                    total += len(preprints)
        elif r and isinstance(r, list):
            total += len(r)
        time.sleep(0.3)

    return total


def main():
    df = pd.read_csv(DATA_FILE, dtype=str)
    print(f"Loaded {len(df)} trials")

    col = 'biorxiv_preprint_count'
    if col not in df.columns:
        df[col] = ''

    # Count how many need filling
    needs_fill = (df[col].isna() | (df[col] == '') | (df[col].astype(str) == 'nan'))
    print(f"Need to fill: {needs_fill.sum()} / {len(df)}")

    drug_cache = {}
    updated = 0

    for idx, row in df.iterrows():
        if not needs_fill.iloc[idx]:
            continue

        drug = str(row.get('intervention_name', '')).lower().split('+')[0].strip()
        if not drug or drug in ('nan', 'unknown', ''):
            continue

        if drug in drug_cache:
            count = drug_cache[drug]
        else:
            count = get_biorxiv_count(drug)
            drug_cache[drug] = count
            if (len(drug_cache)) % 10 == 0:
                print(f"  [{len(drug_cache)} drugs cached] last: {drug} = {count}", flush=True)

        if count is not None:
            df.at[idx, col] = str(count)
            updated += 1

        if (idx + 1) % 200 == 0:
            df.to_csv(DATA_FILE, index=False)
            print(f'  [{idx+1}/{len(df)}] updated={updated} cache={len(drug_cache)}', flush=True)

    df.to_csv(DATA_FILE, index=False)
    filled = (df[col].notna() & (df[col] != '') & (df[col].astype(str) != 'nan')).sum()
    print(f'Done. {filled}/{len(df)} filled ({filled/len(df)*100:.1f}%). {updated} new, {len(drug_cache)} unique drugs.')


if __name__ == '__main__':
    main()
