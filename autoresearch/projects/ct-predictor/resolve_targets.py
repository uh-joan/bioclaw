#!/usr/bin/env python3
"""Resolve drug → target gene for all trials using ChEMBL, save to cache."""
import sys, os, json
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
os.environ['MCP_CONFIG_FILE'] = os.path.join(os.path.dirname(__file__), 'mcp-config.json')

import pandas as pd
from collect_scale2 import resolve_target, DRUG_TARGET_CACHE, _save_cache, _load_cache

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'trials_raw.csv')

df = pd.read_csv(DATA_FILE, dtype=str)
drugs = df['intervention_name'].dropna().unique()
drugs = [d for d in drugs if d.strip() and d not in ('', 'nan')]

print(f"Resolving targets for {len(drugs)} unique drugs...")

resolved = 0
failed = 0
for i, drug in enumerate(drugs):
    drug_lower = drug.lower().strip()
    if drug_lower in DRUG_TARGET_CACHE and DRUG_TARGET_CACHE[drug_lower]:
        continue
    if drug_lower in DRUG_TARGET_CACHE and DRUG_TARGET_CACHE[drug_lower] == '':
        continue  # Already tried, no result

    target = resolve_target(drug_lower)
    if target:
        resolved += 1
        print(f"  [{i+1}/{len(drugs)}] {drug} → {target}")
    else:
        failed += 1
        if (i + 1) % 20 == 0:
            print(f"  [{i+1}/{len(drugs)}] {drug} → (no target found)")

    # Save periodically
    if (i + 1) % 25 == 0:
        _save_cache()

_save_cache()
total_cached = sum(1 for v in DRUG_TARGET_CACHE.values() if v)
print(f"\nDone. Resolved {resolved} new, {failed} failed. Cache: {total_cached} drugs with targets.")
