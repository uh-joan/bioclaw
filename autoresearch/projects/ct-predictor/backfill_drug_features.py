#!/usr/bin/env python3
"""
Backfill drug-only features: PubChem, FDA, PubMed, bioRxiv.
These don't need a target gene — just the drug name.
"""
import sys, os, signal, time, re
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
os.environ['MCP_CONFIG_FILE'] = os.path.join(os.path.dirname(__file__), 'mcp-config.json')

import pandas as pd

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'trials_raw.csv')

class TO(Exception): pass
def _to(s,f): raise TO()
def sc(func, *a, timeout_sec=12, **kw):
    old = signal.signal(signal.SIGALRM, _to)
    signal.alarm(timeout_sec)
    try: r = func(*a, **kw); signal.alarm(0); return r
    except: signal.alarm(0); return None
    finally: signal.signal(signal.SIGALRM, old)


def main():
    df = pd.read_csv(DATA_FILE, dtype=str)
    print(f"Loaded {len(df)} trials")

    # Cache per-drug results to avoid repeat queries
    drug_cache = {}
    updated = 0

    for idx, row in df.iterrows():
        drug = str(row.get('intervention_name', '')).lower().split('+')[0].strip()
        if not drug or drug in ('nan', 'unknown', ''): continue

        # Check if this trial needs any drug features
        needs_pubchem = not (pd.notna(row.get('pubchem_molecular_weight')) and str(row.get('pubchem_molecular_weight','')).strip() not in ('','nan'))
        needs_fda = not (pd.notna(row.get('fda_prior_approval_class')) and str(row.get('fda_prior_approval_class','')).strip() not in ('','nan'))
        needs_pubmed = not (pd.notna(row.get('pubmed_drug_pub_count')) and str(row.get('pubmed_drug_pub_count','')).strip() not in ('','nan'))

        if not (needs_pubchem or needs_fda or needs_pubmed):
            continue

        if drug in drug_cache:
            features = drug_cache[drug]
        else:
            features = {}

            # PubChem
            if needs_pubchem:
                try:
                    from mcp.servers.pubchem_mcp import search_compounds, get_compound_properties
                    r = sc(search_compounds, query=drug, limit=1)
                    if r and isinstance(r, dict):
                        props_list = r.get('details', {}).get('PropertyTable', {}).get('Properties', [])
                        cid = str(props_list[0].get('CID', '')) if props_list else ''
                        if cid:
                            props = sc(get_compound_properties, cid=cid)
                            if props and isinstance(props, dict):
                                p = props.get('PropertyTable', {}).get('Properties', [{}])[0]
                                features['pubchem_molecular_weight'] = p.get('MolecularWeight', '')
                                features['pubchem_xlogp'] = p.get('XLogP', '')
                                features['pubchem_hbond_donor'] = p.get('HBondDonorCount', '')
                                features['pubchem_hbond_acceptor'] = p.get('HBondAcceptorCount', '')
                                features['pubchem_rotatable_bonds'] = p.get('RotatableBondCount', '')
                                features['pubchem_complexity'] = p.get('Complexity', '')
                except: pass

            # FDA
            if needs_fda:
                try:
                    from mcp.servers.fda_mcp import lookup_drug
                    r = sc(lookup_drug, search_term=drug, count='openfda.brand_name.exact', limit=5)
                    if r and isinstance(r, dict) and r.get('success'):
                        results = r.get('data', {}).get('results', [])
                        features['fda_prior_approval_class'] = 1 if results else 0
                        features['fda_class_ae_count'] = len(results)
                except: pass

            # PubMed drug publications
            if needs_pubmed:
                try:
                    from mcp.servers.pubmed_mcp import search_keywords
                    r = sc(search_keywords, keywords=drug, num_results=20)
                    if isinstance(r, list):
                        features['pubmed_drug_pub_count'] = len(r)
                except: pass

            drug_cache[drug] = features
            time.sleep(0.2)

        # Apply cached features
        new = 0
        for col, val in features.items():
            if col in df.columns and val not in (None, '', 'nan'):
                current = str(row.get(col, '')).strip()
                if current in ('', 'nan', 'None'):
                    df.at[idx, col] = str(val)
                    new += 1

        if new > 0:
            updated += 1

        if (idx + 1) % 200 == 0:
            df.to_csv(DATA_FILE, index=False)
            print(f'  [{idx+1}/{len(df)}] updated={updated} cache={len(drug_cache)} drugs', flush=True)

    df.to_csv(DATA_FILE, index=False)
    for col in ['pubchem_molecular_weight', 'fda_prior_approval_class', 'pubmed_drug_pub_count', 'biorxiv_preprint_count']:
        f = (df[col].notna() & (df[col] != '') & (df[col].astype(str) != 'nan')).sum() if col in df.columns else 0
        print(f'  {f:4d}/{len(df)} {col}')
    print(f'Done. {updated} trials updated, {len(drug_cache)} unique drugs cached.')


if __name__ == '__main__':
    main()
