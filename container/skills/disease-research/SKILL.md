---
name: disease-research
description: Disease research and intelligence report generator. Comprehensive disease profiling across 10 research dimensions — identity, clinical presentation, genetics, treatments, pathways, epidemiology, similar diseases, cancer-specific, pharmacology, and drug safety. Use when user mentions disease research, disease report, disease profile, disease intelligence, disease overview, epidemiology, disease prevalence, disease genetics, treatment landscape, disease pathways, disease classification, ICD-10, EFO, MONDO, disease ontology, or comprehensive disease analysis.
---

# Disease Research

Generates comprehensive disease intelligence reports by systematically investigating 10 research dimensions using all available MCP databases. Resolves disease ontology across EFO, MONDO, ICD-10, and SNOMED. Integrates epidemiological data from CDC, clinical evidence from trials, genetic basis from Open Targets, treatment landscape from ChEMBL/DrugBank, and safety signals from FDA.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_disease-research_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Drug target validation and druggability assessment → use `drug-target-analyst`
- Clinical trial pipeline analysis or trial design → use `clinical-trial-analyst`
- Post-market safety signal detection or FAERS analysis → use `pharmacovigilance-specialist`
- Rare disease differential diagnosis with phenotype matching → use `rare-disease-diagnosis`
- Competitive landscape and patent/exclusivity analysis → use `competitive-intelligence`
- Pharmacogenomic patient stratification → use `pharmacogenomics-specialist`

## Cross-Reference: Other Skills

- **Drug target validation and druggability** → use drug-target-analyst skill
- **Clinical trial pipeline for this disease** → use clinical-trial-analyst skill
- **Post-market safety signals for treatments** → use pharmacovigilance-specialist skill
- **FDA regulatory history for approved therapies** → use fda-consultant skill
- **Rare/ultra-rare disease differential diagnosis** → use rare-disease-diagnosis skill
- **Pharmacogenomic stratification of patients** → use precision-medicine-stratifier skill

## Available MCP Tools

### `mcp__opentargets__opentargets_info` (Target-Disease Associations)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_targets` | Search targets by gene symbol/name | `query`, `size` |
| `search_diseases` | Search diseases by name/synonym | `query`, `size` |
| `get_target_disease_associations` | Evidence-scored target-disease links | `targetId` (Ensembl ID), `diseaseId` (EFO ID), `minScore`, `size` |
| `get_disease_targets_summary` | All targets for a disease | `diseaseId`, `minScore`, `size` |
| `get_target_details` | Full target info (function, pathways, tractability) | `id` (Ensembl ID) |
| `get_disease_details` | Full disease info (ontology, phenotypes) | `id` (EFO ID) |

### `mcp__chembl__chembl_info` (Bioactivity & Drug Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `compound_search` | Search molecules by name/SMILES/ID | `query`, `limit` |
| `target_search` | Search biological targets | `query`, `limit` |
| `get_bioactivity` | Compound-target activity data (IC50, Ki, EC50) | `chembl_id`, `target_id`, `limit` |
| `get_mechanism` | Mechanism of action | `chembl_id` |
| `drug_search` | Search drugs by indication or name | `query`, `limit` |
| `get_admet` | ADMET/drug-likeness properties | `chembl_id` |

### `mcp__drugbank__drugbank_info` (Drug Pharmacology)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_by_name` | Find drug by name | `query` |
| `get_drug_details` | Full drug profile (mechanism, pharmacodynamics, targets) | `drugbank_id` |
| `search_by_target` | All drugs acting on a target | `target`, `limit` |
| `get_drug_interactions` | Drug-drug interactions | `drugbank_id` |
| `get_similar_drugs` | Pharmacologically similar drugs | `drugbank_id`, `limit` |
| `get_pathways` | Metabolic/signaling pathways | `drugbank_id` |
| `search_by_category` | Drugs by therapeutic category | `category`, `limit` |
| `search_by_structure` | Structural similarity search | `smiles` or `inchi`, `limit` |
| `search_by_carrier` | Drugs using same carrier protein | `carrier`, `limit` |
| `search_by_transporter` | Drugs using same transporter | `transporter`, `limit` |
| `get_external_identifiers` | Cross-database IDs (PubChem, ChEMBL, KEGG) | `drugbank_id` |

### `mcp__pubmed__pubmed_articles` (Literature Evidence)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Quick keyword search | `keywords`, `num_results` |
| `search_advanced` | Filtered search | `term`, `journal`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Full article details | `pmid` |

### `mcp__fda__fda_info` (Regulatory & Safety)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_drugs` | Search FDA drug labels | `query`, `limit` |
| `get_drug_label` | Full prescribing information | `application_number` or `brand_name` |
| `search_adverse_events` | FAERS adverse event reports | `query`, `limit` |
| `get_recall_info` | Drug recalls and safety alerts | `query`, `limit` |
| `search_clinical_trials` | FDA-tracked trial results | `query`, `limit` |
| `get_approval_history` | Drug approval timeline | `query` |
| `get_orange_book` | Patent/exclusivity data | `query` |
| `search_device_events` | Medical device adverse events | `query`, `limit` |

### `mcp__ctgov__ctgov_info` (Clinical Trials)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_trials` | Search ClinicalTrials.gov | `query`, `status`, `phase`, `limit` |
| `get_trial_details` | Full trial protocol and results | `nct_id` |
| `get_trial_results` | Published results for a trial | `nct_id` |
| `search_by_intervention` | Trials by drug/intervention name | `intervention`, `status`, `limit` |

### `mcp__nlm__nlm_ct_codes` (Disease Ontology & Classification)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `icd-10-cm` | ICD-10-CM diagnosis codes | `query` |
| `icd-11` | ICD-11 classification codes | `query` |
| `hcpcs-LII` | Healthcare procedure codes | `query` |
| `npi-organizations` | Healthcare organization lookup | `query` |
| `npi-individuals` | Healthcare provider lookup | `query` |
| `hpo-vocabulary` | Human Phenotype Ontology terms | `query` |
| `conditions` | Disease/condition terminology | `query` |
| `rx-terms` | Drug/prescription terminology | `query` |
| `loinc-questions` | Lab test codes | `query` |
| `ncbi-genes` | Gene information from NCBI | `query` |
| `major-surgeries-implants` | Surgical procedure codes | `query` |

### `mcp__cdc__cdc_health_data` (Epidemiology & Public Health)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_places_data` | CDC PLACES local health data | `measure`, `state`, `year`, `limit` |
| `get_brfss_data` | Behavioral Risk Factor Surveillance | `question`, `year`, `state`, `limit` |
| `get_vaccination_coverage` | Vaccine coverage rates | `vaccine`, `year`, `geography`, `limit` |
| `get_overdose_surveillance` | Drug overdose data | `state`, `year`, `limit` |
| `get_chronic_disease_indicators` | Chronic disease prevalence | `topic`, `question`, `state`, `limit` |
| `get_youth_risk_behavior` | Youth health risk data | `topic`, `year`, `limit` |
| `get_natality_data` | Birth/natality statistics | `year`, `state`, `limit` |
| `get_mortality_data` | Death/mortality statistics | `cause`, `year`, `state`, `limit` |
| `get_wonder_data` | CDC WONDER database queries | `query`, `limit` |
| `get_covid_data` | COVID-19 surveillance data | `state`, `date`, `limit` |
| `get_flu_surveillance` | Influenza surveillance | `region`, `season`, `limit` |
| `get_sti_surveillance` | STI surveillance data | `disease`, `year`, `state`, `limit` |
| `get_tb_surveillance` | Tuberculosis surveillance | `state`, `year`, `limit` |
| `get_hepatitis_surveillance` | Hepatitis surveillance data | `type`, `year`, `state`, `limit` |
| `get_foodborne_outbreaks` | Foodborne illness outbreaks | `pathogen`, `year`, `limit` |
| `get_environmental_health` | Environmental health data | `topic`, `state`, `limit` |
| `get_cancer_statistics` | Cancer incidence/mortality | `cancer_type`, `state`, `year`, `limit` |
| `get_diabetes_surveillance` | Diabetes prevalence data | `indicator`, `state`, `year`, `limit` |
| `get_heart_disease_data` | Heart disease statistics | `indicator`, `state`, `year`, `limit` |
| `get_maternal_health` | Maternal health indicators | `indicator`, `state`, `year`, `limit` |
| `get_injury_data` | Injury surveillance data | `mechanism`, `intent`, `state`, `limit` |

### `mcp__hpo__hpo_data` (Human Phenotype Ontology)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_hpo_terms` | Search phenotype terms for disease characterization | `query`, `max`, `category` |
| `get_hpo_term` | Get full phenotype term details | `id` (HP:XXXXXXX) |
| `get_hpo_children` | Browse more specific sub-phenotypes | `id` |
| `get_hpo_descendants` | Get all descendant terms for phenotype grouping | `id`, `max` |
| `get_hpo_ancestors` | Trace to broader phenotype categories | `id`, `max` |
| `get_hpo_term_stats` | Check annotation frequency (how common a phenotype is) | `id` |
| `batch_get_hpo_terms` | Batch lookup multiple phenotype terms | `ids` |
| `compare_hpo_terms` | Compare phenotypes across diseases | `id1`, `id2` |

### `mcp__monarch__monarch_data` (Monarch Initiative — Disease-Gene-Phenotype Knowledge Graph)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search` | Search diseases, genes, phenotypes by text | `query` |
| `get_disease_genes` | Find genes associated with a disease | `disease_id` (MONDO/OMIM ID) |
| `get_disease_phenotypes` | Get HPO phenotypes for a disease | `disease_id` |
| `get_gene_diseases` | Find diseases associated with a gene | `gene_id` (HGNC ID) |

### `mcp__biorxiv__biorxiv_info` (Preprints & Emerging Research)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_preprints` | Search bioRxiv/medRxiv preprints | `query`, `server`, `limit` |
| `get_preprint_details` | Full preprint metadata | `doi` |
| `get_recent_preprints` | Latest preprints by topic | `topic`, `days`, `limit` |
| `get_published_version` | Find journal-published version | `doi` |

### `mcp__kegg__kegg_data` (Disease & Pathway Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_diseases` | Search KEGG disease entries by keyword | `query` |
| `get_disease_info` | Disease details (genes, pathways, drugs, markers) | `disease_id` |
| `search_pathways` | Search KEGG pathways by keyword | `query` |
| `get_pathway_info` | Full pathway details (description, classes) | `pathway_id` |
| `get_pathway_genes` | All genes in a disease-related pathway | `pathway_id` |
| `search_drugs` | Search KEGG drug entries | `query` |
| `get_drug_info` | Drug details (targets, pathways) | `drug_id` |
| `convert_identifiers` | Convert between KEGG and external IDs | `identifiers`, `source_db`, `target_db` |
| `find_related_entries` | Find entries related to a given KEGG entry | `entry_id` |

---

## 10-Dimension Disease Research Workflow

### Dimension 1: Identity & Classification

```
1. mcp__opentargets__opentargets_info(method: "search_diseases", query: "DISEASE_NAME", size: 10)
   → Get EFO disease ID, synonyms, parent/child ontology

2. mcp__opentargets__opentargets_info(method: "get_disease_details", id: "EFO_xxxxxxx")
   → Full ontology tree, phenotypes, cross-references (MONDO, Orphanet, OMIM)

3. mcp__nlm__nlm_ct_codes(method: "icd-10-cm", query: "DISEASE_NAME")
   → ICD-10-CM code for billing, epidemiological tracking

4. mcp__nlm__nlm_ct_codes(method: "icd-11", query: "DISEASE_NAME")
   → ICD-11 classification (WHO standard)

5. mcp__nlm__nlm_ct_codes(method: "conditions", query: "DISEASE_NAME")
   → Standardized condition terminology and synonyms

6. mcp__kegg__kegg_data(method: "search_diseases", query: "DISEASE_NAME")
   → Get KEGG disease ID with linked pathways, genes, and drugs
   mcp__kegg__kegg_data(method: "get_disease_info", disease_id: "H00001")
   → Full KEGG disease record: associated genes, pathways, therapeutic drugs, markers
```

### Dimension 2: Clinical Presentation

```
1. mcp__hpo__hpo_data(method: "search_hpo_terms", query: "DISEASE_NAME", max: 20)
   → HPO phenotype terms — signs, symptoms, clinical features

2. For key phenotypes, get full details and explore hierarchy:
   mcp__hpo__hpo_data(method: "get_hpo_term", id: "HP:XXXXXXX")
   mcp__hpo__hpo_data(method: "get_hpo_descendants", id: "HP:XXXXXXX", max: 20)
   → Complete phenotype characterization with sub-phenotypes

3. mcp__hpo__hpo_data(method: "get_hpo_term_stats", id: "HP:XXXXXXX")
   → How frequently this phenotype is annotated across diseases (specificity indicator)

4. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "DISEASE_NAME clinical presentation diagnosis criteria", num_results: 15)
   → Published diagnostic criteria and clinical phenotype descriptions

5. mcp__nlm__nlm_ct_codes(method: "loinc-questions", query: "DISEASE_NAME")
   → Laboratory tests used for diagnosis and monitoring
```

### Dimension 3: Genetic & Molecular Basis

```
1. mcp__opentargets__opentargets_info(method: "get_disease_targets_summary", diseaseId: "EFO_xxxxxxx", minScore: 0.5, size: 50)
   → All validated gene targets ranked by evidence score

2. For top targets:
   mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   → Gene function, pathways, protein structure, tractability

3. mcp__nlm__nlm_ct_codes(method: "ncbi-genes", query: "GENE_SYMBOL")
   → NCBI gene details, genomic location, function summary

4. mcp__pubmed__pubmed_articles(method: "search_advanced", term: "DISEASE_NAME GWAS genetics", num_results: 10)
   → GWAS and genetic association studies

5. mcp__biorxiv__biorxiv_info(method: "search_preprints", query: "DISEASE_NAME genetics molecular mechanism", limit: 10)
   → Emerging genetic findings not yet peer-reviewed
```

### Dimension 4: Treatment Landscape

```
1. mcp__chembl__chembl_info(method: "drug_search", query: "DISEASE_NAME", limit: 50)
   → All drugs for this indication in ChEMBL (approved + experimental)

2. mcp__drugbank__drugbank_info(method: "search_by_category", category: "THERAPEUTIC_CATEGORY", limit: 30)
   → Drugs by therapeutic class

3. For each key drug:
   mcp__drugbank__drugbank_info(method: "get_drug_details", drugbank_id: "DBxxxxx")
   → Full pharmacological profile — mechanism, pharmacodynamics, indications

4. mcp__fda__fda_info(method: "search_drugs", query: "DISEASE_NAME", limit: 20)
   → FDA-approved drugs with labeling

5. mcp__fda__fda_info(method: "get_approval_history", query: "DRUG_NAME")
   → Approval timeline, supplemental approvals, indication expansions

6. mcp__nlm__nlm_ct_codes(method: "rx-terms", query: "DRUG_NAME")
   → Standardized drug terminology, formulations
```

### Dimension 5: Biological Pathways

```
1. For top target drugs:
   mcp__drugbank__drugbank_info(method: "get_pathways", drugbank_id: "DBxxxxx")
   → Metabolic and signaling pathway involvement

2. mcp__chembl__chembl_info(method: "get_mechanism", chembl_id: "CHEMBLxxxxx")
   → Mechanism of action for key drugs

3. mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   → Reactome pathways, GO terms for key targets

4. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "DISEASE_NAME pathophysiology signaling pathway", num_results: 10)
   → Published pathway studies
```

### Dimension 6: Epidemiology

```
1. mcp__cdc__cdc_health_data(method: "get_chronic_disease_indicators", topic: "DISEASE_NAME")
   → US prevalence and incidence data

2. mcp__cdc__cdc_health_data(method: "get_places_data", measure: "DISEASE_MEASURE")
   → Local-level prevalence (county/city)

3. mcp__cdc__cdc_health_data(method: "get_brfss_data", question: "DISEASE_RELATED_QUESTION")
   → Population survey data on risk factors and prevalence

4. mcp__cdc__cdc_health_data(method: "get_mortality_data", cause: "DISEASE_NAME")
   → Mortality statistics and trends

5. mcp__pubmed__pubmed_articles(method: "search_advanced", term: "DISEASE_NAME epidemiology prevalence incidence", num_results: 10)
   → Global epidemiological studies

6. Disease-specific CDC endpoints (use as applicable):
   - get_cancer_statistics for oncology
   - get_diabetes_surveillance for metabolic disease
   - get_heart_disease_data for cardiovascular
   - get_overdose_surveillance for substance-related
   - get_sti_surveillance / get_tb_surveillance / get_hepatitis_surveillance for infectious disease
```

### Dimension 7: Similar & Related Diseases

```
1. mcp__opentargets__opentargets_info(method: "get_disease_details", id: "EFO_xxxxxxx")
   → Ontology children, parent terms, related diseases

2. mcp__opentargets__opentargets_info(method: "search_diseases", query: "BROADER_DISEASE_CATEGORY", size: 20)
   → Diseases in the same therapeutic area

3. mcp__drugbank__drugbank_info(method: "get_similar_drugs", drugbank_id: "DBxxxxx", limit: 10)
   → Pharmacologically similar treatments (implies similar disease biology)

4. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "DISEASE_NAME differential diagnosis comorbidity", num_results: 10)
   → Differential diagnosis and comorbidity literature
```

### Dimension 8: Cancer-Specific Data (if applicable)

```
1. mcp__cdc__cdc_health_data(method: "get_cancer_statistics", cancer_type: "CANCER_TYPE")
   → Incidence, mortality, survival rates

2. mcp__opentargets__opentargets_info(method: "get_disease_targets_summary", diseaseId: "EFO_CANCER_ID", minScore: 0.3, size: 50)
   → Somatic mutation drivers, oncogenes, tumor suppressors

3. mcp__chembl__chembl_info(method: "drug_search", query: "CANCER_TYPE", limit: 30)
   → Chemotherapy, targeted therapy, immunotherapy agents

4. mcp__ctgov__ctgov_info(method: "search_trials", query: "CANCER_TYPE", phase: "3", limit: 20)
   → Late-stage oncology trials

5. mcp__biorxiv__biorxiv_info(method: "search_preprints", query: "CANCER_TYPE biomarker immunotherapy", limit: 10)
   → Emerging oncology research
```

### Dimension 9: Pharmacology Deep-Dive

```
1. For each major drug class:
   mcp__chembl__chembl_info(method: "get_bioactivity", chembl_id: "CHEMBLxxxxx", limit: 50)
   → IC50, Ki, EC50 values across compounds

2. mcp__chembl__chembl_info(method: "get_admet", chembl_id: "CHEMBLxxxxx")
   → Drug-likeness, ADMET properties

3. mcp__drugbank__drugbank_info(method: "get_drug_interactions", drugbank_id: "DBxxxxx")
   → Drug-drug interactions for key treatments

4. mcp__drugbank__drugbank_info(method: "search_by_target", target: "TARGET_NAME")
   → All drugs modulating the primary target

5. mcp__drugbank__drugbank_info(method: "search_by_transporter", transporter: "TRANSPORTER_NAME")
   → Transporter-mediated pharmacokinetic considerations
```

### Dimension 10: Drug Safety & Post-Market Surveillance

```
1. mcp__fda__fda_info(method: "search_adverse_events", query: "DRUG_NAME", limit: 50)
   → FAERS adverse event reports

2. mcp__fda__fda_info(method: "get_recall_info", query: "DRUG_NAME")
   → Drug recalls and safety communications

3. mcp__fda__fda_info(method: "get_drug_label", brand_name: "DRUG_NAME")
   → Black box warnings, contraindications, warnings & precautions

4. mcp__pubmed__pubmed_articles(method: "search_advanced", term: "DRUG_NAME safety adverse effects long-term", num_results: 10)
   → Post-market safety literature
```

---

### Monarch Disease-Gene-Phenotype Mapping

Use Monarch to map disease-gene-phenotype relationships for comprehensive disease characterization.

```
1. Search for the disease in Monarch knowledge graph:
   mcp__monarch__monarch_data(method="search", query="DISEASE_NAME")
   → Get MONDO disease ID and cross-references

2. Get genes associated with the disease:
   mcp__monarch__monarch_data(method="get_disease_genes", disease_id="MONDO:XXXXXXX")
   → Curated gene-disease associations from Monarch (complements Open Targets)

3. Get disease phenotypes from Monarch:
   mcp__monarch__monarch_data(method="get_disease_phenotypes", disease_id="MONDO:XXXXXXX")
   → HPO phenotype profile for the disease — compare with HPO MCP data

4. For key genes, find all associated diseases:
   mcp__monarch__monarch_data(method="get_gene_diseases", gene_id="HGNC:XXXX")
   → Reveals pleiotropy and shared genetic architecture with related conditions

5. Integrate with other dimensions:
   - Cross-reference Monarch gene list with Open Targets evidence scores (Dimension 3)
   - Use Monarch phenotypes to enrich clinical presentation (Dimension 2)
   - Map Monarch gene-disease links to identify related diseases (Dimension 7)
```

---

## Report-First Methodology

### Step 1: Create Report Template

Before making any MCP calls, create a markdown report with all 10 dimension headings and placeholder sections. This ensures systematic coverage and prevents missing dimensions.

```markdown
# Disease Intelligence Report: [DISEASE_NAME]
**Date:** [DATE] | **Ontology:** EFO: [ID] | MONDO: [ID] | ICD-10: [CODE]

## 1. Identity & Classification
## 2. Clinical Presentation
## 3. Genetic & Molecular Basis
## 4. Treatment Landscape
## 5. Biological Pathways
## 6. Epidemiology
## 7. Similar & Related Diseases
## 8. Cancer-Specific Data
## 9. Pharmacology Deep-Dive
## 10. Drug Safety & Post-Market Surveillance
## Key Findings & Research Gaps
```

### Step 2: Progressive Population

Work through dimensions 1-10 sequentially. After each MCP call, immediately write findings into the report with inline citations. Do not batch all queries first — populate as you go.

### Step 3: Evidence Grading

Apply evidence tier to every claim in the report:

```
[T1] — Direct clinical evidence (approved drug, completed RCT, human genetics)
[T2] — Strong preclinical or observational (Phase II+ trial, large cohort study, GWAS)
[T3] — Moderate evidence (in vitro, animal model, case series, small trial)
[T4] — Hypothesis-level (text mining, pathway inference, preprint, single case report)
```

### Step 4: Mandatory Source Citation

Every factual claim must include its source inline:

```
- "BRCA1 mutations account for 5-10% of breast cancers [T1, PMID: 12345678]"
- "Overall association score 0.82 [T1, Open Targets EFO_0000305]"
- "US prevalence 8.2% in adults [T2, CDC BRFSS 2023]"
- "Novel pathway identified in zebrafish [T3, bioRxiv 10.1101/2024.xxx]"
```

---

## Disease Ontology Resolution

### Cross-Mapping Workflow

```
1. Start with user's disease term
   mcp__opentargets__opentargets_info(method: "search_diseases", query: "USER_TERM")
   → EFO ID (primary identifier for Open Targets queries)

2. Get full ontology mapping
   mcp__opentargets__opentargets_info(method: "get_disease_details", id: "EFO_xxxxxxx")
   → Cross-references to MONDO, Orphanet, OMIM, MESH, DOID

3. Resolve clinical codes
   mcp__nlm__nlm_ct_codes(method: "icd-10-cm", query: "DISEASE_NAME")
   mcp__nlm__nlm_ct_codes(method: "icd-11", query: "DISEASE_NAME")
   → Codes needed for CDC epidemiological queries

4. Resolve phenotype terms
   mcp__nlm__nlm_ct_codes(method: "hpo-vocabulary", query: "DISEASE_NAME")
   → HPO terms for phenotype-based analysis
```

### Key Ontology Identifiers

| System | Format | Use Case |
|--------|--------|----------|
| **EFO** | EFO_0000305 | Open Targets queries |
| **MONDO** | MONDO:0005015 | Cross-database disease mapping |
| **ICD-10-CM** | E11.9 | CDC epidemiology, billing data |
| **ICD-11** | 5A11 | WHO international classification |
| **OMIM** | 125853 | Mendelian/genetic disease reference |
| **Orphanet** | ORPHA:558 | Rare disease identification |
| **HPO** | HP:0001250 | Phenotype-based disease matching |
| **MESH** | D003920 | PubMed literature search |
| **SNOMED** | 73211009 | Clinical records, EHR systems |

---

## Comprehensive Target Mapping

### Ranking Targets by Evidence

```
1. mcp__opentargets__opentargets_info(method: "get_disease_targets_summary", diseaseId: "EFO_xxxxxxx", minScore: 0.1, size: 100)
   → Complete target list with overall association scores

2. Categorize targets by evidence type:
   - Genetic association (GWAS, somatic mutations)
   - Known drug targets (approved drugs hitting this target for this disease)
   - Pathway involvement (Reactome, signaling)
   - Literature evidence (text mining, co-mentions)

3. For top 10 targets, get full details:
   mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   → Druggability, protein class, subcellular location

4. Cross-reference with existing drugs:
   mcp__drugbank__drugbank_info(method: "search_by_target", target: "TARGET_NAME")
   → Treatment opportunities and competitive landscape
```

### Target Evidence Interpretation

| Score Range | Interpretation | Action |
|-------------|---------------|--------|
| **> 0.7** | Strong multi-source validation | Priority target — investigate drugs and trials |
| **0.4 - 0.7** | Moderate evidence | Promising — check for genetic or clinical validation |
| **0.2 - 0.4** | Emerging evidence | Worth monitoring — look for recent publications |
| **< 0.2** | Weak/single-source | Hypothesis only — note but do not prioritize |

---

## Epidemiological Data Integration

### US Prevalence Workflow

```
1. mcp__cdc__cdc_health_data(method: "get_chronic_disease_indicators", topic: "DISEASE_TOPIC")
   → National prevalence, trends over time

2. mcp__cdc__cdc_health_data(method: "get_places_data", measure: "DISEASE_MEASURE", state: "US")
   → County/city-level prevalence maps

3. mcp__cdc__cdc_health_data(method: "get_brfss_data", question: "RISK_FACTOR_QUESTION")
   → Risk factor prevalence by demographics

4. mcp__cdc__cdc_health_data(method: "get_mortality_data", cause: "DISEASE_ICD_CODE")
   → Age-adjusted mortality rates, trends
```

### Demographic Stratification

Always report epidemiological data stratified by:
- **Age group** (pediatric, adult, geriatric)
- **Sex/gender**
- **Race/ethnicity** (where data available)
- **Geographic region** (state, urban/rural)
- **Temporal trend** (increasing, decreasing, stable)

---

## Multi-Agent Workflow Examples

**"Generate a comprehensive disease report on Type 2 Diabetes"**
1. Disease Research → 10-dimension report: ontology, clinical features, genetics (TCF7L2, PPARG), treatments (metformin, GLP-1 agonists, SGLT2 inhibitors), CDC prevalence, pathways, safety
2. Drug Target Analyst → Deep-dive on novel targets (GIP receptor, glucokinase), druggability assessment
3. Clinical Trial Analyst → Phase III pipeline, emerging mechanisms (dual agonists, oral insulin)
4. Pharmacovigilance Specialist → Comparative safety across drug classes (cardiovascular outcomes, DKA risk)

**"Investigate Systemic Lupus Erythematosus for drug development"**
1. Disease Research → Full disease intelligence: autoimmune pathways, genetic basis (HLA, IRF5, STAT4), current treatments (belimumab, hydroxychloroquine), epidemiology, unmet needs
2. Rare Disease Diagnosis → Phenotype overlap with other autoimmune conditions, diagnostic odyssey patterns
3. Precision Medicine Stratifier → Patient subtyping by autoantibody profile, complement levels, organ involvement
4. FDA Consultant → Regulatory precedent for lupus nephritis approvals, endpoint guidance

**"Map the treatment landscape for non-small cell lung cancer"**
1. Disease Research → Cancer-specific report: driver mutations (EGFR, ALK, KRAS G12C, PD-L1), approved therapies, survival data, CDC incidence/mortality
2. Drug Target Analyst → Emerging targets (TROP2, HER3, MET exon 14), resistance mechanisms
3. Clinical Trial Analyst → Immunotherapy combinations, neoadjuvant trials, biomarker-selected studies
4. Pharmacovigilance Specialist → Immune-related adverse events, checkpoint inhibitor safety profiles

**"Assess rare disease: Fabry disease"**
1. Disease Research → Ontology (OMIM, Orphanet), GLA gene mutations, enzyme replacement therapy (agalsidase), epidemiology challenges, newborn screening data
2. Rare Disease Diagnosis → Phenotype matching via HPO, diagnostic delay analysis, differential diagnosis
3. Precision Medicine Stratifier → Genotype-phenotype correlation, classic vs late-onset variants
4. FDA Consultant → Orphan drug designations, accelerated approval history

## Completeness Checklist

- [ ] Disease ontology resolved across EFO, MONDO, ICD-10, and SNOMED with cross-references
- [ ] Clinical presentation characterized with HPO phenotype terms and diagnostic criteria
- [ ] Genetic basis mapped with Open Targets association scores and top validated targets
- [ ] Treatment landscape covers approved therapies (FDA/EMA) and experimental pipeline
- [ ] Biological pathways identified for key targets (Reactome, KEGG, GO)
- [ ] Epidemiology includes US prevalence/incidence with demographic stratification
- [ ] Similar and related diseases identified via ontology and pharmacological similarity
- [ ] Evidence tier (T1-T4) assigned to every factual claim with inline source citation
- [ ] All 10 research dimensions populated (or explicitly marked as not applicable)
- [ ] Key findings and research gaps summarized at end of report
