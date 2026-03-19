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
    hits = r.get('data', {}).get('search', {}).get('hits', [])
    if not hits:
        return out
    ensembl_id = hits[0].get('id', '')
    assoc = safe_call(get_target_disease_associations, targetId=ensembl_id, size=5)
    if assoc:
        rows = assoc.get('data', {}).get('associatedDiseases', {}).get('rows', [])
        if rows:
            best = rows[0]
            out['ot_overall_score'] = best.get('score', '')
            dts = best.get('datatypeScores', [])
            for dt in (dts if isinstance(dts, list) else []):
                cid = dt.get('componentId', dt.get('id', ''))
                score = dt.get('score', '')
                if 'genetic' in cid: out['ot_genetic_score'] = score
                elif 'somatic' in cid: out['ot_somatic_score'] = score
                elif 'literature' in cid: out['ot_literature_score'] = score
                elif 'animal' in cid: out['ot_animal_model_score'] = score
                elif 'known_drug' in cid: out['ot_known_drug_score'] = score
                elif 'affected_pathway' in cid: out['ot_affected_pathway_score'] = score
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
    from mcp.servers.drugbank_mcp import search_by_name
    out = {}
    r = safe_call(search_by_name, query=drug)
    if not r:
        return out
    results = r.get('results', [])
    if not results:
        return out
    d = results[0]
    out['drugbank_half_life_hours'] = d.get('half_life', d.get('half-life', ''))
    out['drugbank_interaction_count'] = d.get('drug_interactions_count', d.get('interactions_count', ''))
    targets = d.get('targets', [])
    out['drugbank_target_count'] = len(targets) if isinstance(targets, list) else ''
    enzymes = d.get('enzymes', [])
    out['drugbank_enzyme_count'] = len(enzymes) if isinstance(enzymes, list) else ''
    transporters = d.get('transporters', [])
    out['drugbank_transporter_count'] = len(transporters) if isinstance(transporters, list) else ''
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
            # Try to compute tissue specificity (tau index)
            if isinstance(data[0], dict):
                values = [d.get('median', 0) for d in data if d.get('median')]
            elif isinstance(data[0], list):
                # Nested array format
                values = [max(d) if isinstance(d, list) else d for d in data]
            else:
                values = [float(x) for x in data if x]
            if values and max(values) > 0:
                norm = [v / max(values) for v in values]
                tau = sum(1 - v for v in norm) / (len(norm) - 1) if len(norm) > 1 else 0
                out['gtex_tissue_specificity'] = round(tau, 4)
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


def get_gwas_features(target_gene):
    from mcp.servers.gwas_mcp import get_gene_associations
    out = {}
    r = safe_call(get_gene_associations, gene=target_gene)
    if r and isinstance(r, dict) and 'error' not in r:
        assocs = r.get('associations', [])
        out['gwas_hit_count'] = len(assocs) if isinstance(assocs, list) else ''
        if isinstance(assocs, list) and assocs:
            pvals = [a.get('pvalue', 1) for a in assocs if a.get('pvalue')]
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
    if r and isinstance(r, dict):
        out['cbioportal_mutation_freq'] = r.get('mutation_frequency', '')
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
        out['bindingdb_num_measurements'] = len(results) if isinstance(results, list) else ''
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
            updates.update(get_gwas_features(target) or {})
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
