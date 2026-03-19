#!/usr/bin/env python3
"""Backfill MCP features with per-server timeout protection."""
import sys, os, json, signal, re
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


def _parse_half_life_hours(text):
    """Extract numeric half-life in hours from DrugBank text."""
    if not text or not isinstance(text, str):
        return ''
    m = re.search(r'(\d+\.?\d*)\s*(?:to|and|-)?\s*(?:\d+\.?\d*)?\s*hour', text, re.IGNORECASE)
    if m:
        return float(m.group(1))
    m = re.search(r'(\d+\.?\d*)\s*day', text, re.IGNORECASE)
    if m:
        return float(m.group(1)) * 24
    m = re.search(r'(\d+\.?\d*)\s*minute', text, re.IGNORECASE)
    if m:
        return round(float(m.group(1)) / 60, 2)
    return ''


def enrich_trial(drug, target, condition):
    """Get all MCP features for one trial."""
    out = {}

    # === Drug-only features ===

    # ChEMBL
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
                        targets_hit = set(a.get('target_chembl_id', '') for a in acts if a.get('target_chembl_id'))
                        out['chembl_selectivity'] = len(targets_hit)
                        ic50s = [a for a in acts if a.get('standard_type') == 'IC50' and a.get('standard_value')]
                        if ic50s:
                            out['chembl_best_ic50_nm'] = min(float(a['standard_value']) for a in ic50s)
                    mech = safe_call(get_mechanism, chembl_id=cid, timeout_sec=15)
                    if mech:
                        out['chembl_moa_count'] = len(mech.get('mechanisms', []))
    except Exception:
        pass

    # FDA (count-based + AE count)
    try:
        from mcp.servers.fda_mcp import lookup_drug
        r = safe_call(lookup_drug, search_term=drug, count="openfda.brand_name.exact", limit=5, timeout_sec=15)
        if r and isinstance(r, dict) and r.get('success'):
            results = r.get('data', {}).get('results', [])
            out['fda_prior_approval_class'] = 1 if results else 0
            out['fda_class_ae_count'] = len(results)
        ae = safe_call(lookup_drug, search_term=drug, search_type='adverse_events',
                       count='patient.reaction.reactionmeddrapt.exact', limit=5, timeout_sec=15)
        if ae and isinstance(ae, dict) and ae.get('success'):
            ae_results = ae.get('data', {}).get('results', [])
            if ae_results:
                out['fda_ae_report_count'] = sum(item.get('count', 0) for item in ae_results)
    except Exception:
        pass

    # DrugBank (search + details for half_life, interactions, molecular_weight)
    try:
        from mcp.servers.drugbank_mcp import search_by_name, get_drug_details
        r = safe_call(search_by_name, query=drug, timeout_sec=15)
        if r and isinstance(r, dict):
            results = r.get('results', [])
            if results:
                db_id = results[0].get('drugbank_id', '')
                if db_id:
                    details = safe_call(get_drug_details, drugbank_id=db_id, timeout_sec=15)
                    if details and isinstance(details, dict):
                        drug_data = details.get('drug', details.get('data', {}))
                        if isinstance(drug_data, dict):
                            hl_text = drug_data.get('half_life', '')
                            hl_hours = _parse_half_life_hours(hl_text)
                            if hl_hours:
                                out['drugbank_half_life_hours'] = hl_hours
                            mw = drug_data.get('average_mass', drug_data.get('molecular_weight', ''))
                            if mw:
                                out['drugbank_molecular_weight'] = mw
                            interactions = drug_data.get('drug_interactions', [])
                            if isinstance(interactions, list):
                                out['drugbank_interaction_count'] = len(interactions)
                            targets = drug_data.get('targets', [])
                            if isinstance(targets, list):
                                out['drugbank_target_count'] = len(targets)
                            enzymes = drug_data.get('enzymes', [])
                            if isinstance(enzymes, list):
                                out['drugbank_enzyme_count'] = len(enzymes)
    except Exception:
        pass

    # BindingDB (Ki/Kd via UniProt ID lookup)
    # Chain: target gene → UniProt → BindingDB affinities
    if target:
        try:
            from mcp.client import get_client as _get_client
            # Step 1: gene → UniProt ID
            uc = _get_client('uniprot')
            ur = safe_call(uc.call_tool, 'uniprot_data',
                          {'method': 'search_by_gene', 'gene': target, 'organism': 'human'},
                          timeout_sec=15)
            uniprot_id = ''
            if ur and isinstance(ur, dict):
                results = ur.get('results', [])
                if results:
                    uniprot_id = results[0].get('primaryAccession', '')

            if uniprot_id:
                # Step 2: UniProt → BindingDB Ki/Kd
                bc = _get_client('bindingdb')
                br = safe_call(bc.call_tool, 'bindingdb_data',
                              {'method': 'get_ligands_by_target', 'uniprot_id': uniprot_id, 'affinity_cutoff': 10000},
                              timeout_sec=20)
                if br and isinstance(br, dict):
                    out['bindingdb_num_measurements'] = br.get('total', 0)
                    results = br.get('results', [])
                    ki_vals = []
                    kd_vals = []
                    for entry in results:
                        if isinstance(entry, dict):
                            atype = entry.get('affinity_type', '')
                            aval = str(entry.get('affinity', '')).replace('<', '').replace('>', '').strip()
                            try:
                                val = float(aval)
                                if atype == 'Ki':
                                    ki_vals.append(val)
                                elif atype == 'Kd':
                                    kd_vals.append(val)
                            except (ValueError, TypeError):
                                pass
                    if ki_vals:
                        out['bindingdb_ki_nm'] = min(ki_vals)
                    if kd_vals:
                        out['bindingdb_kd_nm'] = min(kd_vals)
        except Exception:
            pass

    # ClinPGx
    try:
        from mcp.servers.clinpgx_mcp import get_chemical
        r = safe_call(get_chemical, drug=drug, timeout_sec=15)
        if r and isinstance(r, dict):
            results = r.get('results', [])
            out['clinpgx_guideline_count'] = len(results)
            out['clinpgx_actionable'] = 1 if results else 0
    except Exception:
        pass

    # EMA
    try:
        from mcp.servers.ema_mcp import search_medicines
        r = safe_call(search_medicines, active_substance=drug, timeout_sec=15)
        if r and isinstance(r, dict):
            out['ema_approved_similar'] = 1 if r.get('total_count', 0) > 0 else 0
    except Exception:
        pass

    # HPO
    try:
        from mcp.servers.hpo_mcp import search_hpo_terms
        r = safe_call(search_hpo_terms, query=condition, timeout_sec=15)
        if r and isinstance(r, dict):
            out['hpo_phenotype_count'] = r.get('totalResults', '')
    except Exception:
        pass

    # Medicare → write to schema column name medicare_indication_spend
    try:
        from mcp.servers.medicare_mcp import medicare_info
        r = safe_call(medicare_info, method='search_prescribers', drug_name=drug, limit=100, timeout_sec=20)
        if r and isinstance(r, dict):
            prescribers = r.get('prescribers', [])
            if prescribers:
                total_cost = sum(float(p.get('total_drug_cost', 0) or 0) for p in prescribers)
                if total_cost > 0:
                    out['medicare_indication_spend'] = round(total_cost, 2)
    except Exception:
        pass

    # Medicaid → write to schema column name medicaid_indication_spend
    try:
        from mcp.servers.medicaid_mcp import medicaid_info
        r = safe_call(medicaid_info, method='get_nadac_pricing', drug_name=drug, limit=5, timeout_sec=20)
        if r and isinstance(r, dict):
            data = r.get('data', [])
            if isinstance(data, list) and data:
                prices = [d.get('nadac_per_unit', 0) for d in data if d.get('nadac_per_unit')]
                if prices:
                    out['medicaid_indication_spend'] = round(sum(prices) / len(prices), 4)
    except Exception:
        pass

    # Competitor trial count (CT.gov search with pageSize=1 for count only)
    try:
        from mcp.servers.ct_gov_mcp import search as ctgov_search
        import re as _re
        r = safe_call(ctgov_search, condition=condition, phase='PHASE3', pageSize=1, timeout_sec=15)
        if r:
            text = r if isinstance(r, str) else r.get('text', str(r))
            m = _re.search(r'(\d+)\s+(?:of\s+)?(\d+)\s+(?:studies|trials)', text, _re.I)
            if m:
                out['competitor_trial_count'] = m.group(2)
    except Exception:
        pass

    # === Target-dependent features ===
    if target:
        # OpenTargets
        try:
            from mcp.servers.opentargets_mcp import search_targets, get_target_disease_associations
            r = safe_call(search_targets, query=target, size=1, timeout_sec=20)
            if r:
                hits = r.get('data', {}).get('search', {}).get('hits', [])
                if hits:
                    ensembl_id = hits[0].get('id', '')
                    if ensembl_id:
                        assoc = safe_call(get_target_disease_associations,
                                          targetId=ensembl_id, size=5, timeout_sec=20)
                        if assoc and isinstance(assoc, dict):
                            target_data = assoc.get('data', {}).get('target', {})
                            assoc_diseases = target_data.get('associatedDiseases', {})
                            rows = assoc_diseases.get('rows', [])
                            total_assoc = assoc_diseases.get('count', len(rows))
                            out['ot_disease_association_count'] = total_assoc
                            if rows:
                                out['ot_overall_score'] = rows[0].get('score', '')

                        # Tractability + safety via get_target_details
                        from mcp.client import get_client as _gc
                        ot_client = _gc('opentargets')
                        details = safe_call(ot_client.call_tool, 'opentargets_info',
                                           {'method': 'get_target_details', 'id': ensembl_id},
                                           timeout_sec=15)
                        if details and isinstance(details, dict):
                            td = details.get('data', {}).get('target', details.get('data', {}))
                            tract = td.get('tractability', [])
                            if tract:
                                out['ot_target_tractability'] = sum(1 for t in tract if t.get('value'))
                            safety = td.get('safetyLiabilities', [])
                            if isinstance(safety, list):
                                out['ot_safety_liability_count'] = len(safety)
        except Exception:
            pass

        # gnomAD
        try:
            from mcp.servers.gnomad_mcp import get_gene_constraint
            r = safe_call(get_gene_constraint, gene=target, timeout_sec=20)
            if r and isinstance(r, dict):
                c = r.get('constraint', r)
                out['gnomad_pli'] = c.get('pLI', '')
                out['gnomad_loeuf'] = c.get('oe_lof_upper', c.get('loeuf', ''))
        except Exception:
            pass

        # Reactome
        try:
            from mcp.servers.reactome_mcp import find_pathways_by_gene
            r = safe_call(find_pathways_by_gene, gene=target, timeout_sec=15)
            if r and isinstance(r, dict):
                pw = r.get('pathways', r.get('results', []))
                out['reactome_pathway_count'] = len(pw) if isinstance(pw, list) else ''
        except Exception:
            pass

        # STRING-DB
        try:
            from mcp.servers.stringdb_mcp import get_protein_interactions
            r = safe_call(get_protein_interactions, protein=target, timeout_sec=15)
            if r and isinstance(r, dict):
                out['stringdb_interaction_degree'] = r.get('total_interactions', len(r.get('interactions', [])))
        except Exception:
            pass

        # DepMap
        try:
            from mcp.servers.depmap_mcp import get_gene_dependency
            r = safe_call(get_gene_dependency, gene=target, timeout_sec=15)
            if r and isinstance(r, dict):
                out['depmap_essentiality'] = r.get('summary', {}).get('mean_gene_effect', '')
        except Exception:
            pass

        # ClinVar
        try:
            from mcp.servers.clinvar_mcp import get_gene_variants_summary
            r = safe_call(get_gene_variants_summary, gene=target, timeout_sec=15)
            if r and isinstance(r, dict):
                out['clinvar_pathogenic_count'] = r.get('total_count', '')
        except Exception:
            pass

        # GTEx (tissue specificity tau index)
        try:
            from mcp.servers.gtex_mcp import get_gene_expression
            r = safe_call(get_gene_expression, gene=target, timeout_sec=20)
            if r and isinstance(r, dict):
                data = r.get('data', [])
                if isinstance(data, list) and data:
                    import statistics
                    medians = []
                    for tissue_item in data:
                        if isinstance(tissue_item, dict):
                            vals = tissue_item.get('data', [])
                            if isinstance(vals, list) and vals:
                                medians.append(statistics.median(vals))
                    if medians and max(medians) > 0:
                        norm = [v / max(medians) for v in medians]
                        tau = sum(1 - v for v in norm) / (len(norm) - 1) if len(norm) > 1 else 0
                        out['gtex_tissue_specificity'] = round(tau, 4)
                        out['gtex_max_tpm'] = round(max(medians), 2)
                        out['gtex_num_tissues'] = len(medians)
        except Exception:
            pass

        # GWAS (use search_associations - gene associations returns 404)
        try:
            from mcp.servers.gwas_mcp import search_associations
            query = f"{target} {condition}" if condition else target
            r = safe_call(search_associations, query=query, limit=20, timeout_sec=15)
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
        except Exception:
            pass

        # cBioPortal (pan-cancer mutation frequency)
        try:
            from mcp.servers.cbioportal_mcp import get_mutation_frequency
            r = safe_call(get_mutation_frequency, gene=target, study_id='msk_impact_2017', timeout_sec=15)
            if r and isinstance(r, dict) and 'frequencies' in r:
                freqs = r['frequencies']
                if freqs:
                    out['cbioportal_mutation_freq'] = freqs[0].get('frequency', '')
        except Exception:
            pass

        # PubMed
        try:
            from mcp.servers.pubmed_mcp import search_keywords
            r = safe_call(search_keywords, keywords=f"{target} {condition}", num_results=20, timeout_sec=20)
            if isinstance(r, list):
                out['pubmed_target_pub_count'] = len(r)
        except Exception:
            pass

        # OpenAlex
        try:
            from mcp.servers.openalex_mcp import search_works
            r = safe_call(search_works, query=f"{target} {condition}", timeout_sec=15)
            if r and isinstance(r, dict):
                results = r.get('results', [])
                if results:
                    cites = [w.get('cited_by_count', 0) for w in results[:10]]
                    out['openalex_citation_velocity'] = sum(cites) / max(len(cites), 1)
        except Exception:
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
