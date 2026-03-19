#!/usr/bin/env python3
"""Re-query DrugBank for all trials to get uncapped interaction counts."""
import sys, os, signal, time
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
os.environ['MCP_CONFIG_FILE'] = os.path.join(os.path.dirname(__file__), 'mcp-config.json')

import re
import pandas as pd

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'trials_raw.csv')

class TO(Exception): pass
def _to(s,f): raise TO()
def sc(func, *a, **kw):
    old = signal.signal(signal.SIGALRM, _to)
    signal.alarm(20)
    try:
        r = func(*a, **kw)
        signal.alarm(0)
        return r
    except:
        signal.alarm(0)
        return None
    finally:
        signal.signal(signal.SIGALRM, old)

def parse_half_life(text):
    if not text or not isinstance(text, str): return ''
    m = re.search(r'(\d+\.?\d*)\s*(?:to|and|-)?\s*(?:\d+\.?\d*)?\s*hour', text, re.I)
    if m: return float(m.group(1))
    m = re.search(r'(\d+\.?\d*)\s*day', text, re.I)
    if m: return float(m.group(1)) * 24
    return ''

def main():
    from mcp.servers.drugbank_mcp import search_by_name, get_drug_details

    df = pd.read_csv(DATA_FILE, dtype=str)
    print(f"Loaded {len(df)} trials")

    # Get unique drugs
    drugs_done = set()
    updated = 0

    for idx, row in df.iterrows():
        drug = str(row.get('intervention_name', '')).lower().strip()
        if not drug or drug == 'nan' or drug in drugs_done:
            if drug in drugs_done:
                # Apply cached result
                continue
            continue

        r = sc(search_by_name, query=drug)
        if not r or not isinstance(r, dict):
            drugs_done.add(drug)
            continue
        results = r.get('results', [])
        if not results:
            drugs_done.add(drug)
            continue

        db_id = results[0].get('drugbank_id', '')
        if not db_id:
            drugs_done.add(drug)
            continue

        details = sc(get_drug_details, drugbank_id=db_id)
        if not details:
            drugs_done.add(drug)
            continue

        dd = details.get('drug', details.get('data', {}))
        if not isinstance(dd, dict):
            drugs_done.add(drug)
            continue

        # Extract all fields
        hl = parse_half_life(dd.get('half_life', ''))
        mw = dd.get('average_mass', dd.get('molecular_weight', ''))
        ints = dd.get('drug_interactions', [])
        targets = dd.get('targets', [])
        enzymes = dd.get('enzymes', [])
        transporters = dd.get('transporters', [])

        # Update ALL rows with this drug
        mask = df['intervention_name'].str.lower().str.strip() == drug
        if hl: df.loc[mask, 'drugbank_half_life_hours'] = str(hl)
        if mw: df.loc[mask, 'drugbank_molecular_weight'] = str(mw)
        if isinstance(ints, list): df.loc[mask, 'drugbank_interaction_count'] = str(len(ints))
        if isinstance(targets, list): df.loc[mask, 'drugbank_target_count'] = str(len(targets))
        if isinstance(enzymes, list): df.loc[mask, 'drugbank_enzyme_count'] = str(len(enzymes))
        if isinstance(transporters, list): df.loc[mask, 'drugbank_transporter_count'] = str(len(transporters))

        updated += mask.sum()
        drugs_done.add(drug)

        if len(drugs_done) % 20 == 0:
            df.to_csv(DATA_FILE, index=False)
            print(f"  [{len(drugs_done)} drugs] updated {updated} trial rows", flush=True)

        time.sleep(0.3)

    df.to_csv(DATA_FILE, index=False)
    vals = pd.to_numeric(df['drugbank_interaction_count'], errors='coerce').dropna()
    print(f"\nDone. {len(drugs_done)} drugs, {updated} rows updated.")
    print(f"interaction_count: max={vals.max():.0f}, mean={vals.mean():.0f}, filled={len(vals)}/{len(df)}")

if __name__ == '__main__':
    main()
