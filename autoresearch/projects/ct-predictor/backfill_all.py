#!/usr/bin/env python3
"""Backfill ALL MCP features for existing trials using fixed wrappers."""
import sys, os, csv, re, traceback
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
os.environ['MCP_CONFIG_FILE'] = os.path.join(os.path.dirname(__file__), 'mcp-config.json')

import pandas as pd
import numpy as np

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'trials_raw.csv')

# Lazy imports — only import wrappers when first needed to avoid spawning all servers at once
def safe_call(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        return None


def get_ot_features(target_gene):
    from mcp.servers.opentargets_mcp import search_targets, get_target_disease_associations
    out = {}
    r = safe_call(search_targets, query=target_gene, size=1)
    if not r:
        return out
    # Response: {"data": {"search": {"hits": [{"id": "ENSG...", ...}]}}}
    hits = r.get('data', {}).get('search', {}).get('hits', [])
    if not hits:
        return out
    ensembl_id = hits[0].get('id', '')
    if not ensembl_id:
        return out
    assoc = safe_call(get_target_disease_associations, targetId=ensembl_id, size=5)
    if assoc and isinstance(assoc, dict):
        # Response: {"data": {"target": {"associatedDiseases": {"count": N, "rows": [...]}}}}
        target_data = assoc.get('data', {}).get('target', {})
        assoc_diseases = target_data.get('associatedDiseases', {})
        rows = assoc_diseases.get('rows', [])
        total_assoc = assoc_diseases.get('count', len(rows))
        out['ot_disease_association_count'] = total_assoc
        if rows:
            best = rows[0]
            out['ot_overall_score'] = best.get('score', '')
    return out


def get_chembl_features(drug):
    from mcp.servers.chembl_mcp import compound_search, get_bioactivity, get_mechanism
    out = {}
    r = safe_call(compound_search, query=drug, limit=3)
    if not r:
        return out
    mols = r.get('molecules', [])
    if not mols:
        return out
    mol = mols[0]
    chembl_id = mol.get('molecule_chembl_id', '')
    out['chembl_max_phase'] = mol.get('max_phase', '')
    props = mol.get('molecule_properties', {}) or {}
    out['drugbank_molecular_weight'] = props.get('full_mwt', '')
    # Get bioactivity
    if chembl_id:
        bio = safe_call(get_bioactivity, chembl_id=chembl_id, limit=50)
        if bio:
            activities = bio.get('activities', [])
            out['chembl_num_assays'] = len(activities)
            ic50s = [a for a in activities if a.get('standard_type') == 'IC50' and a.get('standard_value')]
            if ic50s:
                out['chembl_best_ic50_nm'] = min(float(a['standard_value']) for a in ic50s)
            targets_hit = set(a.get('target_chembl_id', '') for a in activities if a.get('target_chembl_id'))
            out['chembl_selectivity'] = len(targets_hit)
        mech = safe_call(get_mechanism, chembl_id=chembl_id)
        if mech:
            mechs = mech.get('mechanisms', [])
            out['chembl_moa_count'] = len(mechs)
    return out


def get_drugbank_features(drug):
    import re as _re
    from mcp.servers.drugbank_mcp import search_by_name, get_drug_details
    out = {}
    r = safe_call(search_by_name, query=drug)
    if not r:
        return out
    results = r.get('results', [])
    if not results:
        return out
    d = results[0]
    db_id = d.get('drugbank_id', '')
    # search_by_name returns minimal info; get_drug_details has full data
    if db_id:
        details = safe_call(get_drug_details, drugbank_id=db_id)
        if details and isinstance(details, dict):
            drug_data = details.get('drug', details.get('data', {}))
            if isinstance(drug_data, dict):
                # Half-life (parse text to hours)
                hl_text = drug_data.get('half_life', '')
                if hl_text and isinstance(hl_text, str):
                    m = _re.search(r'(\d+\.?\d*)\s*(?:to|and|-)\s*(?:\d+\.?\d*)?\s*hour', hl_text, _re.IGNORECASE)
                    if m:
                        out['drugbank_half_life_hours'] = float(m.group(1))
                    else:
                        m = _re.search(r'(\d+\.?\d*)\s*day', hl_text, _re.IGNORECASE)
                        if m:
                            out['drugbank_half_life_hours'] = float(m.group(1)) * 24
                # Molecular weight
                mw = drug_data.get('average_mass', drug_data.get('molecular_weight', ''))
                if mw:
                    out['drugbank_molecular_weight'] = mw
                # Interaction count
                interactions = drug_data.get('drug_interactions', [])
                if isinstance(interactions, list):
                    out['drugbank_interaction_count'] = len(interactions)
                # Target/enzyme counts
                targets = drug_data.get('targets', [])
                out['drugbank_target_count'] = len(targets) if isinstance(targets, list) else ''
                enzymes = drug_data.get('enzymes', [])
                out['drugbank_enzyme_count'] = len(enzymes) if isinstance(enzymes, list) else ''
                return out
    # Fallback: use search result data if details failed
    out['drugbank_molecular_weight'] = d.get('molecular_weight', d.get('average_mass', ''))
    return out


def get_pubmed_features(target_gene, condition):
    from mcp.servers.pubmed_mcp import search_keywords
    out = {}
    r1 = safe_call(search_keywords, keywords=f"{target_gene} {condition}", num_results=20)
    if isinstance(r1, list):
        out['pubmed_target_pub_count'] = len(r1)
    r2 = safe_call(search_keywords, keywords=target_gene, num_results=20)
    if isinstance(r2, list):
        out['pubmed_drug_pub_count'] = len(r2)
    return out


def get_openalex_features(target_gene, condition):
    from mcp.servers.openalex_mcp import search_works
    out = {}
    r = safe_call(search_works, query=f"{target_gene} {condition}")
    if r and isinstance(r, dict):
        meta = r.get('meta', {})
        total = meta.get('count', 0)
        results = r.get('results', [])
        if results:
            cite_counts = [w.get('cited_by_count', 0) for w in results[:10]]
            out['openalex_citation_velocity'] = sum(cite_counts) / max(len(cite_counts), 1)
    return out


def get_biorxiv_features(target_gene, condition):
    from mcp.servers.biorxiv_mcp import search_preprints
    out = {}
    r = safe_call(search_preprints, query=f"{target_gene} {condition}", limit=30)
    if r and isinstance(r, dict):
        preprints = r.get('preprints', r.get('results', []))
        out['biorxiv_preprint_count'] = len(preprints) if isinstance(preprints, list) else 0
    return out


def get_reactome_features(target_gene):
    from mcp.servers.reactome_mcp import find_pathways_by_gene
    out = {}
    r = safe_call(find_pathways_by_gene, gene=target_gene)
    if r and isinstance(r, dict):
        pathways = r.get('pathways', r.get('results', []))
        out['reactome_pathway_count'] = len(pathways) if isinstance(pathways, list) else ''
    return out


def get_stringdb_features(target_gene):
    from mcp.servers.stringdb_mcp import get_protein_interactions
    out = {}
    r = safe_call(get_protein_interactions, protein=target_gene)
    if r and isinstance(r, dict):
        interactions = r.get('interactions', r.get('results', []))
        out['stringdb_interaction_degree'] = len(interactions) if isinstance(interactions, list) else r.get('total_interactions', '')
    return out


def get_gtex_features(target_gene):
    from mcp.servers.gtex_mcp import get_gene_expression
    out = {}
    r = safe_call(get_gene_expression, gene=target_gene)
    if r and isinstance(r, dict):
        data = r.get('data', [])
        if isinstance(data, list) and data:
            import statistics
            # Each item: {tissueSiteDetailId, data: [TPM values per sample], ...}
            medians = []
            for tissue_item in data:
                if isinstance(tissue_item, dict):
                    vals = tissue_item.get('data', [])
                    if isinstance(vals, list) and vals:
                        medians.append(statistics.median(vals))
                elif isinstance(tissue_item, (int, float)):
                    medians.append(float(tissue_item))
            if medians and max(medians) > 0:
                norm = [v / max(medians) for v in medians]
                tau = sum(1 - v for v in norm) / (len(norm) - 1) if len(norm) > 1 else 0
                out['gtex_tissue_specificity'] = round(tau, 4)
                out['gtex_max_tpm'] = round(max(medians), 2)
                out['gtex_num_tissues'] = len(medians)
    return out


def get_gnomad_features(target_gene):
    from mcp.servers.gnomad_mcp import get_gene_constraint
    out = {}
    r = safe_call(get_gene_constraint, gene=target_gene)
    if r and isinstance(r, dict):
        constraint = r.get('constraint', r)
        out['gnomad_pli'] = constraint.get('pLI', '')
        out['gnomad_loeuf'] = constraint.get('oe_lof_upper', constraint.get('loeuf', ''))
    return out


def get_clinvar_features(target_gene):
    from mcp.servers.clinvar_mcp import get_gene_variants_summary
    out = {}
    r = safe_call(get_gene_variants_summary, gene=target_gene)
    if r and isinstance(r, dict):
        out['clinvar_pathogenic_count'] = r.get('total_count', '')
    return out


def get_gwas_features(target_gene, condition=''):
    from mcp.servers.gwas_mcp import search_associations
    out = {}
    query = f"{target_gene} {condition}" if condition else target_gene
    r = safe_call(search_associations, query=query, limit=20)
    if r and isinstance(r, dict) and 'error' not in r:
        assocs = r.get('associations', [])
        out['gwas_hit_count'] = r.get('total', len(assocs) if isinstance(assocs, list) else '')
        if isinstance(assocs, list) and assocs:
            pvals = []
            for a in assocs:
                m = a.get('pvalueMantissa')
                e = a.get('pvalueExponent')
                if m is not None and e is not None:
                    try:
                        pvals.append(float(m) * (10 ** float(e)))
                    except (ValueError, TypeError):
                        pass
            if pvals:
                out['gwas_best_pvalue'] = min(pvals)
    return out


def get_depmap_features(target_gene):
    from mcp.servers.depmap_mcp import get_gene_dependency
    out = {}
    r = safe_call(get_gene_dependency, gene=target_gene)
    if r and isinstance(r, dict):
        summary = r.get('summary', {})
        out['depmap_essentiality'] = summary.get('mean_gene_effect', '')
    return out


def get_cbioportal_features(target_gene):
    from mcp.servers.cbioportal_mcp import get_gene
    out = {}
    r = safe_call(get_gene, gene=target_gene)
    if r and isinstance(r, dict) and 'error' not in r:
        out['cbioportal_entrez_id'] = r.get('entrezGeneId', '')
        out['cbioportal_gene_type'] = r.get('type', '')
    return out


def get_hpo_features(condition):
    from mcp.servers.hpo_mcp import search_hpo_terms
    out = {}
    r = safe_call(search_hpo_terms, query=condition)
    if r and isinstance(r, dict):
        out['hpo_phenotype_count'] = r.get('totalResults', '')
    return out


def get_monarch_features(condition):
    from mcp.servers.monarch_mcp import get_disease_genes
    out = {}
    r = safe_call(get_disease_genes, disease=condition)
    if r and isinstance(r, dict) and 'error' not in r:
        items = r.get('items', r.get('associations', []))
        out['monarch_gene_count'] = len(items) if isinstance(items, list) else ''
    return out


def get_ema_features(drug):
    from mcp.servers.ema_mcp import search_medicines
    out = {}
    r = safe_call(search_medicines, active_substance=drug)
    if r and isinstance(r, dict):
        out['ema_approved_similar'] = 1 if r.get('total_count', 0) > 0 else 0
    return out


def get_fda_features(drug):
    from mcp.servers.fda_mcp import lookup_drug
    out = {}
    r = safe_call(lookup_drug, search_term=drug, count="openfda.brand_name.exact", limit=5)
    if r and isinstance(r, dict) and r.get('success'):
        data = r.get('data', {})
        results = data.get('results', [])
        out['fda_prior_approval_class'] = 1 if results else 0
        out['fda_class_ae_count'] = len(results)
    return out


def get_clinpgx_features(drug):
    from mcp.servers.clinpgx_mcp import get_chemical
    out = {}
    r = safe_call(get_chemical, drug=drug)
    if r and isinstance(r, dict):
        results = r.get('results', [])
        out['clinpgx_guideline_count'] = len(results)
        out['clinpgx_actionable'] = 1 if results else 0
    return out


def get_bindingdb_features(drug):
    from mcp.servers.bindingdb_mcp import search_by_name
    out = {}
    r = safe_call(search_by_name, query=drug)
    if r and isinstance(r, dict) and 'error' not in r:
        results = r.get('results', r.get('data', []))
        if isinstance(results, list):
            out['bindingdb_num_measurements'] = len(results)
            ki_vals = []
            kd_vals = []
            for entry in results:
                if isinstance(entry, dict):
                    for ki_key in ['Ki', 'ki', 'Ki (nM)', 'ki_nm', 'Ki_nM']:
                        val = entry.get(ki_key)
                        if val and str(val).strip() not in ('', 'None', 'nan', '>'):
                            try:
                                ki_vals.append(float(str(val).replace('>', '').replace('<', '').strip()))
                            except (ValueError, TypeError):
                                pass
                    for kd_key in ['Kd', 'kd', 'Kd (nM)', 'kd_nm', 'Kd_nM']:
                        val = entry.get(kd_key)
                        if val and str(val).strip() not in ('', 'None', 'nan', '>'):
                            try:
                                kd_vals.append(float(str(val).replace('>', '').replace('<', '').strip()))
                            except (ValueError, TypeError):
                                pass
            if ki_vals:
                out['bindingdb_best_ki_nm'] = min(ki_vals)
            if kd_vals:
                out['bindingdb_best_kd_nm'] = min(kd_vals)
    return out


# Load drug→target cache from ChEMBL resolution
import json as _json
_CACHE_FILE = os.path.join(os.path.dirname(__file__), 'data', 'drug_target_cache.json')
DRUG_TARGET = {}
if os.path.exists(_CACHE_FILE):
    with open(_CACHE_FILE) as _f:
        DRUG_TARGET = {k: v for k, v in _json.load(_f).items() if v}
    print(f"Loaded {len(DRUG_TARGET)} drug→target mappings from cache")


def main():
    df = pd.read_csv(DATA_FILE, dtype=str)
    print(f"Loaded {len(df)} trials")

    # Dedup first
    before = len(df)
    df = df.drop_duplicates(subset='nct_id', keep='first').reset_index(drop=True)
    if len(df) < before:
        print(f"Deduped: {before} → {len(df)} trials")

    updated_count = 0

    for idx, row in df.iterrows():
        drug = str(row.get('intervention_name', '')).lower().strip()
        condition = str(row.get('condition', ''))
        target = DRUG_TARGET.get(drug, '')

        # Count how many MCP features this trial already has
        mcp_cols = ['ot_overall_score', 'chembl_selectivity', 'drugbank_half_life_hours',
                    'pubmed_target_pub_count', 'reactome_pathway_count', 'stringdb_interaction_degree',
                    'gtex_tissue_specificity', 'gnomad_pli', 'depmap_essentiality']
        filled = sum(1 for c in mcp_cols if c in df.columns and pd.notna(row.get(c)) and str(row.get(c, '')).strip() not in ('', 'nan'))

        if filled >= 7:
            continue  # Already well-enriched

        print(f"[{idx+1}/{len(df)}] {row.get('nct_id','')} {drug} target={target} condition={condition[:30]} (filled={filled})")

        updates = {}

        # Run all MCP enrichments
        if target:
            updates.update(get_ot_features(target) or {})
            updates.update(get_reactome_features(target) or {})
            updates.update(get_stringdb_features(target) or {})
            updates.update(get_gtex_features(target) or {})
            updates.update(get_gnomad_features(target) or {})
            updates.update(get_clinvar_features(target) or {})
            updates.update(get_gwas_features(target, condition) or {})
            updates.update(get_depmap_features(target) or {})
            updates.update(get_cbioportal_features(target) or {})
            updates.update(get_pubmed_features(target, condition) or {})
            updates.update(get_openalex_features(target, condition) or {})
            updates.update(get_biorxiv_features(target, condition) or {})

        updates.update(get_chembl_features(drug) or {})
        updates.update(get_drugbank_features(drug) or {})
        updates.update(get_bindingdb_features(drug) or {})
        updates.update(get_fda_features(drug) or {})
        updates.update(get_clinpgx_features(drug) or {})
        updates.update(get_ema_features(drug) or {})
        updates.update(get_hpo_features(condition) or {})
        updates.update(get_monarch_features(condition) or {})

        # Only update empty cells
        new_fields = 0
        for col, val in updates.items():
            if col in df.columns and val not in (None, '', 'nan'):
                current = str(row.get(col, '')).strip()
                if current in ('', 'nan', 'None'):
                    df.at[idx, col] = str(val)
                    new_fields += 1

        if new_fields > 0:
            updated_count += 1
            print(f"  → {new_fields} new fields")

        # Save periodically
        if (idx + 1) % 10 == 0:
            df.to_csv(DATA_FILE, index=False)
            print(f"  [saved {idx+1} trials]")

    # Final save
    df.to_csv(DATA_FILE, index=False)
    print(f"\nDone. Updated {updated_count} trials. Total: {len(df)}")


if __name__ == '__main__':
    main()
