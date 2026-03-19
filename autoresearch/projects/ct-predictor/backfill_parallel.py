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


class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError()

def safe_call(func, *args, timeout_sec=TIMEOUT_SEC, **kwargs):
    old = signal.signal(signal.SIGALRM, timeout_handler)
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


def _parse_half_life_hours(text):
    if not text or not isinstance(text, str):
        return ''
    m = re.search(r'(\d+\.?\d*)\s*(?:to|and|-)?\s*(?:\d+\.?\d*)?\s*hour', text, re.IGNORECASE)
    if m: return float(m.group(1))
    m = re.search(r'(\d+\.?\d*)\s*day', text, re.IGNORECASE)
    if m: return float(m.group(1)) * 24
    return ''


def enrich_one(drug, target, condition):
    """Enrich one trial. Each call has rate_limit_delay between MCP calls."""
    out = {}

    # ChEMBL
    try:
        from mcp.servers.chembl_mcp import compound_search, get_bioactivity, get_mechanism
        r = safe_call(compound_search, query=drug, limit=3)
        time.sleep(RATE_LIMIT_DELAY)
        if r:
            mols = r.get('molecules', [])
            if mols:
                mol = mols[0]
                cid = mol.get('molecule_chembl_id', '')
                out['chembl_max_phase'] = mol.get('max_phase', '')
                props = mol.get('molecule_properties', {}) or {}
                out['drugbank_molecular_weight'] = props.get('full_mwt', '')
                if cid:
                    bio = safe_call(get_bioactivity, chembl_id=cid, limit=50)
                    time.sleep(RATE_LIMIT_DELAY)
                    if bio:
                        acts = bio.get('activities', [])
                        out['chembl_num_assays'] = len(acts)
                        targets_hit = set(a.get('target_chembl_id','') for a in acts if a.get('target_chembl_id'))
                        out['chembl_selectivity'] = len(targets_hit)
                        ic50s = [a for a in acts if a.get('standard_type')=='IC50' and a.get('standard_value')]
                        if ic50s:
                            out['chembl_best_ic50_nm'] = min(float(a['standard_value']) for a in ic50s)
                    mech = safe_call(get_mechanism, chembl_id=cid)
                    time.sleep(RATE_LIMIT_DELAY)
                    if mech:
                        out['chembl_moa_count'] = len(mech.get('mechanisms', []))
    except: pass

    # FDA
    try:
        from mcp.servers.fda_mcp import lookup_drug
        r = safe_call(lookup_drug, search_term=drug, count="openfda.brand_name.exact", limit=5)
        time.sleep(RATE_LIMIT_DELAY)
        if r and isinstance(r, dict) and r.get('success'):
            results = r.get('data', {}).get('results', [])
            out['fda_prior_approval_class'] = 1 if results else 0
            out['fda_class_ae_count'] = len(results)
    except: pass

    # DrugBank
    try:
        from mcp.servers.drugbank_mcp import search_by_name, get_drug_details
        r = safe_call(search_by_name, query=drug)
        time.sleep(RATE_LIMIT_DELAY)
        if r and isinstance(r, dict):
            results = r.get('results', [])
            if results:
                db_id = results[0].get('drugbank_id', '')
                if db_id:
                    details = safe_call(get_drug_details, drugbank_id=db_id)
                    time.sleep(RATE_LIMIT_DELAY)
                    if details and isinstance(details, dict):
                        dd = details.get('drug', details.get('data', {}))
                        if isinstance(dd, dict):
                            hl = _parse_half_life_hours(dd.get('half_life', ''))
                            if hl: out['drugbank_half_life_hours'] = hl
                            mw = dd.get('average_mass', dd.get('molecular_weight', ''))
                            if mw: out['drugbank_molecular_weight'] = mw
                            ints = dd.get('drug_interactions', [])
                            if isinstance(ints, list): out['drugbank_interaction_count'] = len(ints)
                            tgts = dd.get('targets', [])
                            if isinstance(tgts, list): out['drugbank_target_count'] = len(tgts)
                            enz = dd.get('enzymes', [])
                            if isinstance(enz, list): out['drugbank_enzyme_count'] = len(enz)
    except: pass

    # ClinPGx
    try:
        from mcp.servers.clinpgx_mcp import get_chemical
        r = safe_call(get_chemical, drug=drug)
        time.sleep(RATE_LIMIT_DELAY)
        if r and isinstance(r, dict):
            results = r.get('results', [])
            out['clinpgx_guideline_count'] = len(results)
            out['clinpgx_actionable'] = 1 if results else 0
    except: pass

    # EMA
    try:
        from mcp.servers.ema_mcp import search_medicines
        r = safe_call(search_medicines, active_substance=drug)
        time.sleep(RATE_LIMIT_DELAY)
        if r and isinstance(r, dict):
            out['ema_approved_similar'] = 1 if r.get('total_count', 0) > 0 else 0
    except: pass

    # HPO
    try:
        from mcp.servers.hpo_mcp import search_hpo_terms
        r = safe_call(search_hpo_terms, query=condition)
        time.sleep(RATE_LIMIT_DELAY)
        if r and isinstance(r, dict):
            out['hpo_phenotype_count'] = r.get('totalResults', '')
    except: pass

    # === Target-dependent ===
    if target:
        # OpenTargets
        try:
            from mcp.servers.opentargets_mcp import search_targets, get_target_disease_associations
            r = safe_call(search_targets, query=target, size=1)
            time.sleep(RATE_LIMIT_DELAY)
            if r:
                hits = r.get('data', {}).get('search', {}).get('hits', [])
                if hits:
                    eid = hits[0].get('id', '')
                    if eid:
                        assoc = safe_call(get_target_disease_associations, targetId=eid, size=5)
                        time.sleep(RATE_LIMIT_DELAY)
                        if assoc and isinstance(assoc, dict):
                            td = assoc.get('data', {}).get('target', {})
                            ad = td.get('associatedDiseases', {})
                            rows = ad.get('rows', [])
                            out['ot_disease_association_count'] = ad.get('count', len(rows))
                            if rows:
                                out['ot_overall_score'] = rows[0].get('score', '')
        except: pass

        # gnomAD
        try:
            from mcp.servers.gnomad_mcp import get_gene_constraint
            r = safe_call(get_gene_constraint, gene=target)
            time.sleep(RATE_LIMIT_DELAY)
            if r and isinstance(r, dict):
                c = r.get('constraint', r)
                out['gnomad_pli'] = c.get('pLI', '')
                out['gnomad_loeuf'] = c.get('oe_lof_upper', c.get('loeuf', ''))
        except: pass

        # Reactome
        try:
            from mcp.servers.reactome_mcp import find_pathways_by_gene
            r = safe_call(find_pathways_by_gene, gene=target)
            time.sleep(RATE_LIMIT_DELAY)
            if r and isinstance(r, dict):
                pw = r.get('pathways', r.get('results', []))
                out['reactome_pathway_count'] = len(pw) if isinstance(pw, list) else ''
        except: pass

        # STRING-db
        try:
            from mcp.servers.stringdb_mcp import get_protein_interactions
            r = safe_call(get_protein_interactions, protein=target)
            time.sleep(RATE_LIMIT_DELAY)
            if r and isinstance(r, dict):
                out['stringdb_interaction_degree'] = r.get('total_interactions', len(r.get('interactions', [])))
        except: pass

        # DepMap
        try:
            from mcp.servers.depmap_mcp import get_gene_dependency
            r = safe_call(get_gene_dependency, gene=target)
            time.sleep(RATE_LIMIT_DELAY)
            if r and isinstance(r, dict):
                out['depmap_essentiality'] = r.get('summary', {}).get('mean_gene_effect', '')
        except: pass

        # ClinVar
        try:
            from mcp.servers.clinvar_mcp import get_gene_variants_summary
            r = safe_call(get_gene_variants_summary, gene=target)
            time.sleep(RATE_LIMIT_DELAY)
            if r and isinstance(r, dict):
                out['clinvar_pathogenic_count'] = r.get('total_count', '')
        except: pass

        # PubMed
        try:
            from mcp.servers.pubmed_mcp import search_keywords
            r = safe_call(search_keywords, keywords=f"{target} {condition}", num_results=20)
            time.sleep(RATE_LIMIT_DELAY)
            if isinstance(r, list):
                out['pubmed_target_pub_count'] = len(r)
        except: pass

        # OpenAlex
        try:
            from mcp.servers.openalex_mcp import search_works
            r = safe_call(search_works, query=f"{target} {condition}")
            time.sleep(RATE_LIMIT_DELAY)
            if r and isinstance(r, dict):
                results = r.get('results', [])
                if results:
                    cites = [w.get('cited_by_count', 0) for w in results[:10]]
                    out['openalex_citation_velocity'] = sum(cites) / max(len(cites), 1)
        except: pass

        # GWAS
        try:
            from mcp.servers.gwas_mcp import search_associations
            r = safe_call(search_associations, query=f"{target} {condition}", limit=20)
            time.sleep(RATE_LIMIT_DELAY)
            if r and isinstance(r, dict) and 'error' not in r:
                assocs = r.get('associations', [])
                out['gwas_hit_count'] = r.get('total', len(assocs) if isinstance(assocs, list) else '')
                if isinstance(assocs, list) and assocs:
                    pvals = []
                    for a in assocs:
                        m = a.get('pvalueMantissa')
                        e = a.get('pvalueExponent')
                        if m is not None and e is not None:
                            try: pvals.append(float(m) * (10 ** float(e)))
                            except: pass
                    if pvals:
                        out['gwas_best_pvalue'] = min(pvals)
        except: pass

    return out


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
