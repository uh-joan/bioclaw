#!/usr/bin/env python3
"""Backfill MCP features with per-server timeout protection."""
import sys, os, json, signal
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
os.environ['MCP_CONFIG_FILE'] = os.path.join(os.path.dirname(__file__), 'mcp-config.json')

import pandas as pd

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'trials_raw.csv')
CACHE_FILE = os.path.join(os.path.dirname(__file__), 'data', 'drug_target_cache.json')

# Load target cache
DRUG_TARGET = {}
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE) as f:
        DRUG_TARGET = {k: v for k, v in json.load(f).items() if v}
print(f"Target cache: {len(DRUG_TARGET)} drugs")


class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("MCP call timed out")

def safe_call(func, *args, timeout_sec=30, **kwargs):
    """Call with signal-based timeout."""
    old = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_sec)
    try:
        result = func(*args, **kwargs)
        signal.alarm(0)
        return result
    except TimeoutError:
        print(f"    TIMEOUT {func.__name__}")
        return None
    except Exception as e:
        signal.alarm(0)
        return None
    finally:
        signal.signal(signal.SIGALRM, old)


def enrich_trial(drug, target, condition):
    """Get all MCP features for one trial."""
    out = {}

    # Drug-only features (no target needed)
    try:
        from mcp.servers.chembl_mcp import compound_search, get_bioactivity, get_mechanism
        r = safe_call(compound_search, query=drug, limit=3, timeout_sec=20)
        if r:
            mols = r.get('molecules', [])
            if mols:
                mol = mols[0]
                cid = mol.get('molecule_chembl_id', '')
                out['chembl_max_phase'] = mol.get('max_phase', '')
                props = mol.get('molecule_properties', {}) or {}
                out['drugbank_molecular_weight'] = props.get('full_mwt', '')
                if cid:
                    bio = safe_call(get_bioactivity, chembl_id=cid, limit=50, timeout_sec=20)
                    if bio:
                        acts = bio.get('activities', [])
                        out['chembl_num_assays'] = len(acts)
                        targets_hit = set(a.get('target_chembl_id','') for a in acts if a.get('target_chembl_id'))
                        out['chembl_selectivity'] = len(targets_hit)
                        ic50s = [a for a in acts if a.get('standard_type')=='IC50' and a.get('standard_value')]
                        if ic50s:
                            out['chembl_best_ic50_nm'] = min(float(a['standard_value']) for a in ic50s)
                    mech = safe_call(get_mechanism, chembl_id=cid, timeout_sec=15)
                    if mech:
                        out['chembl_moa_count'] = len(mech.get('mechanisms', []))
    except:
        pass

    try:
        from mcp.servers.fda_mcp import lookup_drug
        r = safe_call(lookup_drug, search_term=drug, count="openfda.brand_name.exact", limit=5, timeout_sec=15)
        if r and isinstance(r, dict) and r.get('success'):
            results = r.get('data', {}).get('results', [])
            out['fda_prior_approval_class'] = 1 if results else 0
            out['fda_class_ae_count'] = len(results)
    except:
        pass

    try:
        from mcp.servers.clinpgx_mcp import get_chemical
        r = safe_call(get_chemical, drug=drug, timeout_sec=15)
        if r and isinstance(r, dict):
            results = r.get('results', [])
            out['clinpgx_guideline_count'] = len(results)
            out['clinpgx_actionable'] = 1 if results else 0
    except:
        pass

    try:
        from mcp.servers.ema_mcp import search_medicines
        r = safe_call(search_medicines, active_substance=drug, timeout_sec=15)
        if r and isinstance(r, dict):
            out['ema_approved_similar'] = 1 if r.get('total_count', 0) > 0 else 0
    except:
        pass

    try:
        from mcp.servers.hpo_mcp import search_hpo_terms
        r = safe_call(search_hpo_terms, query=condition, timeout_sec=15)
        if r and isinstance(r, dict):
            out['hpo_phenotype_count'] = r.get('totalResults', '')
    except:
        pass

    # Target-dependent features
    if target:
        try:
            from mcp.servers.gnomad_mcp import get_gene_constraint
            r = safe_call(get_gene_constraint, gene=target, timeout_sec=20)
            if r and isinstance(r, dict):
                c = r.get('constraint', r)
                out['gnomad_pli'] = c.get('pLI', '')
                out['gnomad_loeuf'] = c.get('oe_lof_upper', c.get('loeuf', ''))
        except:
            pass

        try:
            from mcp.servers.reactome_mcp import find_pathways_by_gene
            r = safe_call(find_pathways_by_gene, gene=target, timeout_sec=15)
            if r and isinstance(r, dict):
                pw = r.get('pathways', r.get('results', []))
                out['reactome_pathway_count'] = len(pw) if isinstance(pw, list) else ''
        except:
            pass

        try:
            from mcp.servers.stringdb_mcp import get_protein_interactions
            r = safe_call(get_protein_interactions, protein=target, timeout_sec=15)
            if r and isinstance(r, dict):
                out['stringdb_interaction_degree'] = r.get('total_interactions', len(r.get('interactions', [])))
        except:
            pass

        try:
            from mcp.servers.depmap_mcp import get_gene_dependency
            r = safe_call(get_gene_dependency, gene=target, timeout_sec=15)
            if r and isinstance(r, dict):
                out['depmap_essentiality'] = r.get('summary', {}).get('mean_gene_effect', '')
        except:
            pass

        try:
            from mcp.servers.clinvar_mcp import get_gene_variants_summary
            r = safe_call(get_gene_variants_summary, gene=target, timeout_sec=15)
            if r and isinstance(r, dict):
                out['clinvar_pathogenic_count'] = r.get('total_count', '')
        except:
            pass

        try:
            from mcp.servers.pubmed_mcp import search_keywords
            r = safe_call(search_keywords, keywords=f"{target} {condition}", num_results=20, timeout_sec=20)
            if isinstance(r, list):
                out['pubmed_target_pub_count'] = len(r)
        except:
            pass

        try:
            from mcp.servers.openalex_mcp import search_works
            r = safe_call(search_works, query=f"{target} {condition}", timeout_sec=15)
            if r and isinstance(r, dict):
                results = r.get('results', [])
                if results:
                    cites = [w.get('cited_by_count', 0) for w in results[:10]]
                    out['openalex_citation_velocity'] = sum(cites) / max(len(cites), 1)
        except:
            pass

    return out


def main():
    df = pd.read_csv(DATA_FILE, dtype=str)
    df = df.drop_duplicates(subset='nct_id', keep='first').reset_index(drop=True)
    print(f"Processing {len(df)} trials")

    updated = 0
    for idx, row in df.iterrows():
        drug = str(row.get('intervention_name', '')).lower().strip()
        condition = str(row.get('condition', ''))
        target = DRUG_TARGET.get(drug, '')

        # Skip well-enriched trials
        mcp_cols = ['chembl_selectivity', 'gnomad_pli', 'reactome_pathway_count', 'depmap_essentiality']
        filled = sum(1 for c in mcp_cols if pd.notna(row.get(c)) and str(row.get(c, '')).strip() not in ('', 'nan'))
        if filled >= 3:
            continue

        if not drug or drug == 'nan':
            continue

        features = enrich_trial(drug, target, condition)

        new_fields = 0
        for col, val in features.items():
            if col in df.columns and val not in (None, '', 'nan'):
                current = str(row.get(col, '')).strip()
                if current in ('', 'nan', 'None'):
                    df.at[idx, col] = str(val)
                    new_fields += 1

        if new_fields > 0:
            updated += 1

        if (idx + 1) % 5 == 0:
            print(f"[{idx+1}/{len(df)}] {drug:25s} target={target:10s} +{new_fields} fields (total updated: {updated})")
            sys.stdout.flush()

        if (idx + 1) % 20 == 0:
            df.to_csv(DATA_FILE, index=False)

    df.to_csv(DATA_FILE, index=False)
    print(f"\nDone. Updated {updated}/{len(df)} trials.")


if __name__ == '__main__':
    main()
