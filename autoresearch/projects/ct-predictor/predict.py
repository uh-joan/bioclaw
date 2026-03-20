#!/usr/bin/env python3
"""
Predict clinical trial outcome from NCT ID.

Usage:
  python predict.py NCT05580562
  python predict.py NCT05580562 NCT04191421 NCT03872791
"""
import sys, os, json, pickle, signal
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
os.environ['MCP_CONFIG_FILE'] = os.path.join(os.path.dirname(__file__), 'mcp-config.json')

import pandas as pd
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model.pkl')
CACHE_FILE = os.path.join(os.path.dirname(__file__), 'data', 'drug_target_cache.json')

class TO(Exception): pass
def _to(s,f): raise TO()
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


def get_trial_data(nct_id):
    """Fetch trial data from CT.gov and extract drug + features."""
    import re
    from mcp.servers.ct_gov_mcp import get_study
    from backfill_ctgov import parse_markdown_study

    r = sc(get_study, nctId=nct_id, timeout_sec=20)
    if not r:
        return None

    text = r if isinstance(r, str) else r.get('text', str(r))
    features = parse_markdown_study(text)
    features['nct_id'] = nct_id

    # Extract ALL drugs from Interventions section
    raw_drugs = re.findall(r'###\s+(?:Drug|Biological|Combination Product):\s*(.+)', text)
    skip = {'placebo', 'matching placebo', 'oral placebo', 'iv placebo',
            'placebo oral', 'placebo iv', 'chemotherapy', 'standard of care',
            'observation', 'radiation', 'normal saline', 'dextrose',
            'saline solution', 'saline', 'dexamethasone', 'prednisone',
            'prednisolone', 'methylprednisolone', 'hydrocortisone',
            'diphenhydramine', 'acetaminophen', 'ondansetron', 'filgrastim',
            'pegfilgrastim', 'folinic acid'}
    cleaned_drugs = []
    for d in raw_drugs:
        name = d.strip()
        name = re.split(r'\s+\d+\s*(?:mg|ml|mcg|µg)', name, flags=re.I)[0].strip()
        name = re.sub(r'\s*\(.*?\)', '', name).strip().rstrip('/, ')
        # Remove trailing descriptions
        name = re.split(r',\s+an?\s+', name, flags=re.I)[0].strip()
        if name.lower() not in skip and len(name) > 2:
            if name.lower() not in [d.lower() for d in cleaned_drugs]:
                cleaned_drugs.append(name)

    if cleaned_drugs:
        # Standard chemo agents (control arm, not experimental)
        standard_chemo = {'carboplatin', 'paclitaxel', 'docetaxel', 'pemetrexed',
                         'cisplatin', 'gemcitabine', 'fluorouracil', 'capecitabine',
                         'doxorubicin', 'cyclophosphamide', 'etoposide', 'irinotecan',
                         'oxaliplatin', 'vincristine', 'methotrexate', 'leucovorin'}

        # Separate experimental vs standard
        experimental = [d for d in cleaned_drugs if d.lower() not in standard_chemo]
        standard = [d for d in cleaned_drugs if d.lower() in standard_chemo]

        if len(experimental) >= 2:
            # Multi-drug experimental combo
            features['intervention_name'] = ' + '.join(experimental[:3])
            features['is_combination'] = '1'
            features['n_drugs'] = str(len(experimental))
        elif experimental:
            if standard:
                # Experimental + chemo backbone
                features['intervention_name'] = experimental[0] + ' + ' + standard[0]
                features['is_combination'] = '1'
                features['n_drugs'] = str(len(experimental) + len(standard))
            else:
                features['intervention_name'] = experimental[0]
                features['is_combination'] = '0'
                features['n_drugs'] = '1'
        elif standard:
            features['intervention_name'] = standard[0]
            features['is_combination'] = '0'
            features['n_drugs'] = '1'

        print(f"  All drugs found: {cleaned_drugs}")
        print(f"  Experimental: {experimental}, Standard: {standard}")

    # Infer indication
    condition = features.get('condition', '')
    c = condition.lower()
    if any(x in c for x in ['cancer','tumor','carcinoma','melanoma','leukemia','lymphoma','sarcoma','myeloma']):
        features['indication_area'] = 'oncology'
    elif any(x in c for x in ['alzheimer','parkinson','epilepsy','depression','schizophrenia','sclerosis']):
        features['indication_area'] = 'cns'
    elif any(x in c for x in ['diabetes','obesity','nash','metabolic']):
        features['indication_area'] = 'metabolic'
    elif any(x in c for x in ['arthritis','lupus','psoriasis','crohn','colitis','dermatitis']):
        features['indication_area'] = 'immunology'
    elif any(x in c for x in ['heart','cardiac','hypertension','stroke']):
        features['indication_area'] = 'cardiovascular'
    elif any(x in c for x in ['asthma','copd','pulmonary','respiratory']):
        features['indication_area'] = 'respiratory'
    elif any(x in c for x in ['hiv','hepatitis','infection','covid']):
        features['indication_area'] = 'infectious'
    else:
        features['indication_area'] = 'other'

    return features


def enrich_trial_quick(drug, target, condition):
    """Quick enrichment — only the most impactful features."""
    out = {}

    # ChEMBL
    try:
        from mcp.servers.chembl_mcp import compound_search
        r = sc(compound_search, query=drug, limit=1)
        if r and r.get('molecules'):
            mol = r['molecules'][0]
            out['chembl_max_phase'] = mol.get('max_phase', '')
            out['chembl_moa_count'] = len(r.get('mechanisms', []))
    except: pass

    # HPO
    try:
        from mcp.servers.hpo_mcp import search_hpo_terms
        r = sc(search_hpo_terms, query=condition)
        if r and isinstance(r, dict):
            out['hpo_phenotype_count'] = r.get('totalResults', '')
    except: pass

    # EMA
    try:
        from mcp.servers.ema_mcp import search_medicines
        r = sc(search_medicines, active_substance=drug)
        if r and isinstance(r, dict):
            out['ema_approved_similar'] = 1 if r.get('total_count', 0) > 0 else 0
    except: pass

    # ClinPGx
    try:
        from mcp.servers.clinpgx_mcp import get_chemical
        r = sc(get_chemical, drug=drug)
        if r and isinstance(r, dict):
            out['clinpgx_actionable'] = 1 if r.get('results') else 0
    except: pass

    # Target-dependent
    if target:
        try:
            from mcp.servers.gnomad_mcp import get_gene_constraint
            r = sc(get_gene_constraint, gene=target)
            if r and isinstance(r, dict):
                c = r.get('constraint', r)
                out['gnomad_pli'] = c.get('pLI', '')
        except: pass

        try:
            from mcp.servers.reactome_mcp import find_pathways_by_gene
            r = sc(find_pathways_by_gene, gene=target)
            if r and isinstance(r, dict):
                pw = r.get('pathways', r.get('results', []))
                out['reactome_pathway_count'] = len(pw) if isinstance(pw, list) else ''
        except: pass

    return out


def predict(nct_id):
    """Predict outcome for a single trial."""
    # Load model
    with open(MODEL_PATH, 'rb') as f:
        bundle = pickle.load(f)
    model = bundle['model']
    scaler = bundle['scaler']
    feature_names = bundle['feature_names']

    # Load target cache
    cache = {}
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            cache = json.load(f)

    # Get trial data
    print(f"Fetching {nct_id}...")
    trial = get_trial_data(nct_id)
    if not trial:
        print(f"  Could not fetch trial data for {nct_id}")
        return None

    drug = trial.get('intervention_name', 'unknown')
    condition = trial.get('condition', '')
    indication = trial.get('indication_area', 'other')
    title = trial.get('title', '')
    phase = trial.get('phase', '?')
    enrollment = trial.get('enrollment', '?')

    print(f"  Title: {title[:80]}")
    print(f"  Drug: {drug}")
    print(f"  Condition: {condition[:50]}")
    print(f"  Phase: {phase} | Enrollment: {enrollment} | Indication: {indication}")

    # Resolve target
    target = cache.get(drug.lower(), '')
    if not target:
        from mcp.servers.opentargets_mcp import search_targets
        r = sc(search_targets, query=drug, size=1)
        if r:
            hits = r.get('data', {}).get('search', {}).get('hits', [])
            if hits:
                target = hits[0].get('approvedSymbol', hits[0].get('name', ''))
    print(f"  Target: {target or 'unknown'}")

    # Full enrichment from all MCPs
    print(f"  Enriching from MCPs (full)...")
    from backfill_safe import enrich_trial, enrich_combination
    extra = enrich_trial(drug.lower(), target, condition)

    # Combination enrichment
    if '+' in drug or ' plus ' in drug.lower():
        print(f"  Enriching combination drug...")
        import json as _json
        _cache = {}
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE) as _f:
                _cache = {k: v for k, v in _json.load(_f).items() if v}
        combo = enrich_combination(drug, target, condition, _cache)
        extra.update(combo)
        print(f"    Drug2 target: {combo.get('combo_drug2_has_target', '?')}, interact: {combo.get('combo_targets_interact', '?')}, shared pathways: {combo.get('combo_shared_pathways', '?')}")
    trial.update(extra)

    # Build features using train.py's build_features
    from train import build_features
    # Create a single-row DataFrame with all columns from training data
    train_df = pd.read_csv('data/trials_raw.csv', nrows=1)
    row = {col: '' for col in train_df.columns}
    row.update(trial)
    row['label'] = 0  # dummy
    single_df = pd.DataFrame([row])

    X, _ = build_features(single_df)

    # Align to model features
    for f in feature_names:
        if f not in X.columns:
            X[f] = 0
    X = X[feature_names]

    X_scaled = scaler.transform(X)
    prob = model.predict_proba(X_scaled)[0][1]

    # Display
    print()
    bar_len = int(prob * 30)
    bar = '█' * bar_len + '░' * (30 - bar_len)
    if prob >= 0.7:
        verdict = "LIKELY SUCCESS"
    elif prob >= 0.4:
        verdict = "UNCERTAIN"
    else:
        verdict = "LIKELY FAILURE"

    print(f"  ┌────────────────────────────────────┐")
    print(f"  │ Prediction: {prob:.1%} success probability │")
    print(f"  │ [{bar}] │")
    print(f"  │ Verdict: {verdict:26s} │")
    print(f"  └────────────────────────────────────┘")

    return prob


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python predict.py NCT05580562 [NCT04191421 ...]")
        sys.exit(1)

    for nct_id in sys.argv[1:]:
        predict(nct_id)
        print()
