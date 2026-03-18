---
name: ct-data-collector
description: Clinical trial data collector for the autoresearch CT predictor. Extracts structured features from 18 MCP sources for completed Phase 2/3 trials and labels them by FDA approval status. Use when user mentions collecting trial data, building the CT dataset, populating trials_raw.csv, or autoresearch data collection.
---

# Clinical Trial Data Collector

Collects structured features from 18 MCP servers for completed Phase 2/3 clinical trials. Outputs to `/workspace/autoresearch/projects/ct-predictor/data/trials_raw.csv`.

## Workflow

### Phase 1: Search Completed Trials

Search for completed Phase 2/3 trials in target indication areas. Start with oncology (most data), then expand.

```
mcp__ctgov__ct_gov_studies(method: "search", status: "COMPLETED", phase: "PHASE2", condition: "cancer", pageSize: 50)
mcp__ctgov__ct_gov_studies(method: "search", status: "COMPLETED", phase: "PHASE3", condition: "cancer", pageSize: 50)
```

Also search for terminated/withdrawn trials (failure labels):
```
mcp__ctgov__ct_gov_studies(method: "search", status: "TERMINATED", phase: "PHASE2|PHASE3", condition: "cancer", pageSize: 50)
mcp__ctgov__ct_gov_studies(method: "search", status: "WITHDRAWN", phase: "PHASE2|PHASE3", condition: "cancer", pageSize: 50)
```

### Phase 2: Label Determination

For each trial, determine success/failure:

1. Extract the drug/intervention name from the trial
2. Check FDA approval status:
   ```
   mcp__fda__fda_info(method: "search_drugs", query: "<drug_name>")
   ```
3. Label rules:
   - Trial completed + drug FDA-approved for studied indication within ~3 years → **label = 1** (success)
   - Trial terminated/withdrawn → **label = 0** (failure)
   - Trial completed but drug never approved for indication → **label = 0** (failure)

### Phase 3: Feature Extraction

For each trial, extract features from all 18 MCP sources. See below for exact queries.

#### 3a. Trial Design Features (ClinicalTrials.gov)
Extract from search results and full trial details:
```
mcp__ctgov__ct_gov_studies(method: "get", nctId: "<NCT_ID>")
```
→ phase, enrollment, study_type, allocation, masking, primary_purpose, intervention_type, intervention_name, condition, sponsor_type, lead_sponsor, num_arms, has_dmc, endpoint_type, num_secondary_endpoints, num_sites, has_biomarker_selection

Count competitor trials:
```
mcp__ctgov__ct_gov_studies(method: "search", condition: "<condition>", intervention: "<drug_class>", phase: "PHASE2|PHASE3", pageSize: 1)
```
→ competitor_trial_count (from total results count)

#### 3b. Target-Disease Evidence (OpenTargets)
```
mcp__opentargets__opentargets_info(method: "search_targets", query: "<gene_symbol>")
mcp__opentargets__opentargets_info(method: "get_target_disease_associations", targetId: "<ensembl_id>", diseaseId: "<efo_id>")
mcp__opentargets__opentargets_info(method: "get_target_details", id: "<ensembl_id>")
```
→ ot_genetic_score, ot_somatic_score, ot_literature_score, ot_animal_model_score, ot_known_drug_score, ot_affected_pathway_score, ot_overall_score, ot_target_tractability

#### 3c. Compound Pharmacology (ChEMBL)
```
mcp__chembl__chembl_info(method: "compound_search", query: "<drug_name>")
mcp__chembl__chembl_info(method: "get_bioactivity", chembl_id: "<chembl_id>")
mcp__chembl__chembl_info(method: "get_mechanism", chembl_id: "<chembl_id>")
```
→ chembl_selectivity, chembl_best_ic50_nm, chembl_num_assays, chembl_max_phase, chembl_moa_count

#### 3d. Drug Data (DrugBank)
```
mcp__drugbank__drugbank_data(method: "search_drugs", query: "<drug_name>")
```
→ drugbank_interaction_count, drugbank_target_count, drugbank_enzyme_count, drugbank_transporter_count, drugbank_half_life_hours, drugbank_molecular_weight

#### 3e. Binding Affinity (BindingDB)
```
mcp__bindingdb__bindingdb_data(method: "search_by_name", name: "<drug_name>")
```
→ bindingdb_ki_nm, bindingdb_kd_nm, bindingdb_num_measurements

#### 3f. Pharmacogenomics (ClinPGx)
```
mcp__clinpgx__clinpgx_data(method: "search_drug_gene_pairs", drug: "<drug_name>")
```
→ clinpgx_guideline_count, clinpgx_actionable, clinpgx_cyp_substrate_count

#### 3g. FDA Regulatory (FDA)
```
mcp__fda__fda_info(method: "search_drugs", query: "<drug_class>")
mcp__fda__fda_info(method: "get_adverse_events", drug_name: "<drug_name>")
```
→ fda_prior_approval_class, fda_breakthrough, fda_fast_track, fda_orphan, fda_class_ae_count

#### 3h. Publication Signals (PubMed + OpenAlex + bioRxiv)
```
mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "<target> <disease>", num_results: 5)
mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "<drug_name>", num_results: 5)
mcp__openalex__openalex_data(method: "search_works", query: "<target> <disease>")
mcp__biorxiv__biorxiv_data(method: "search", query: "<target> <disease>")
```
→ pubmed_target_pub_count, pubmed_drug_pub_count, openalex_citation_velocity, biorxiv_preprint_count

#### 3i. Healthcare Spend (Medicare + Medicaid)
```
mcp__medicare__medicare_data(method: "search", query: "<disease>")
mcp__medicaid__medicaid_data(method: "search", query: "<disease>")
```
→ medicare_indication_spend, medicaid_indication_spend

#### 3j. Pathway & Network (Reactome + STRING-db)
```
mcp__reactome__reactome_data(method: "search", query: "<gene_symbol>")
mcp__stringdb__stringdb_data(method: "get_interactions", protein: "<gene_symbol>")
```
→ reactome_pathway_count, stringdb_interaction_degree, stringdb_betweenness

#### 3k. Genomic Features (GTEx, gnomAD, ClinVar, GWAS, DepMap, cBioPortal)
```
mcp__gtex__gtex_data(method: "get_gene_expression", gene: "<gene_symbol>")
mcp__gnomad__gnomad_data(method: "get_gene_constraint", gene: "<gene_symbol>")
mcp__clinvar__clinvar_data(method: "search_variants", gene: "<gene_symbol>")
mcp__gwas__gwas_data(method: "search_associations", query: "<gene_symbol> <disease>")
mcp__depmap__depmap_data(method: "get_gene_dependency", gene: "<gene_symbol>")
mcp__cbioportal__cbioportal_data(method: "get_gene_mutations", gene: "<gene_symbol>")
```
→ gtex_tissue_specificity, gnomad_pli, gnomad_loeuf, clinvar_pathogenic_count, gwas_hit_count, gwas_best_pvalue, depmap_essentiality, cbioportal_mutation_freq

#### 3l. Disease Complexity (HPO + Monarch)
```
mcp__hpo__hpo_data(method: "search_terms", query: "<disease>")
mcp__monarch__monarch_data(method: "search_diseases", query: "<disease>")
```
→ hpo_phenotype_count, monarch_gene_count

#### 3m. European Regulatory (EMA + EU Filings)
```
mcp__ema__ema_data(method: "search_medicines", query: "<drug_name>")
```
→ ema_approved_similar, eu_filings_count

### Phase 4: Write Data

Write each trial as a row to `/workspace/autoresearch/projects/ct-predictor/data/trials_raw.csv`.

Use Python to write the CSV:
```python
import csv
row = {
    "nct_id": "NCT01234567",
    "title": "Phase 3 Study of Drug X in Condition Y",
    "label": 1,
    # ... all features
}
with open("/workspace/autoresearch/projects/ct-predictor/data/trials_raw.csv", "a") as f:
    writer = csv.DictWriter(f, fieldnames=list(row.keys()))
    if f.tell() == 0:
        writer.writeheader()
    writer.writerow(row)
```

### Phase 5: Summary

After collecting data, report:
- Total trials collected
- Success/failure split
- Indication areas covered
- Feature completeness (% non-null per feature)
- Any MCP queries that returned no data

## Target Dataset Size

- Minimum: 200 trials (100 success + 100 failure)
- Ideal: 500+ trials across multiple indication areas
- Focus areas: oncology first (most structured data), then cardiovascular, CNS, metabolic, immunology

## Indication Area Classification

Map conditions to broad categories:
- **oncology**: cancer, tumor, carcinoma, melanoma, leukemia, lymphoma, sarcoma, myeloma
- **cns**: alzheimer, parkinson, epilepsy, depression, schizophrenia, multiple sclerosis, ALS
- **cardiovascular**: heart failure, hypertension, atrial fibrillation, stroke, MI
- **metabolic**: diabetes, obesity, NASH, dyslipidemia
- **immunology**: rheumatoid arthritis, lupus, psoriasis, Crohn's, ulcerative colitis
- **infectious**: HIV, hepatitis, influenza, COVID, bacterial infection
- **respiratory**: asthma, COPD, pulmonary fibrosis
- **rare**: any orphan disease designation
- **other**: everything else

## Missing Data Strategy

If an MCP query returns no data for a feature, write `""` (empty string). The feature engineering pipeline handles missing values with median imputation + missingness indicators.
