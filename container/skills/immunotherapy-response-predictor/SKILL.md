---
name: immunotherapy-response-predictor
description: Immunotherapy response predictor and immune checkpoint inhibitor analyst. Predicts patient response to immune checkpoint inhibitors through systematic multi-biomarker analysis, producing a quantitative ICI Response Score (0-100). Use when user mentions immunotherapy, checkpoint inhibitor, ICI, PD-1, PD-L1, CTLA-4, pembrolizumab, nivolumab, atezolizumab, ipilimumab, durvalumab, avelumab, cemiplimab, tumor mutational burden, TMB, microsatellite instability, MSI, MSI-H, MSS, mismatch repair, MMR, dMMR, neoantigen, immune checkpoint, tumor microenvironment, TIME, immune evasion, resistance genes, STK11, PTEN, JAK1, JAK2, B2M, POLE, POLD1, ICI response, immunotherapy prediction, biomarker analysis, immune response score, T-cell infiltration, immune desert, immune inflamed, immune excluded, objective response rate, ORR, pembrolizumab TMB-H, anti-PD-1, anti-PD-L1, anti-CTLA-4, combination immunotherapy, ipilimumab nivolumab, checkpoint blockade, immunotherapy biomarker, or immune profiling.
---

# Immunotherapy Response Predictor

Predicts patient response to immune checkpoint inhibitors (ICIs) through systematic multi-biomarker analysis. Integrates tumor mutational burden (TMB), microsatellite instability (MSI/MMR), PD-L1 expression, neoantigen burden, resistance gene mutations, and clinical evidence to produce a quantitative ICI Response Score (0-100). Uses Open Targets for target-disease evidence, ChEMBL for compound activity, DrugBank for drug-target pharmacology, PubMed for clinical literature, FDA for approved indications and labels, and ClinicalTrials.gov for ongoing immunotherapy trials.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_immunotherapy-response-predictor_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Somatic/germline variant interpretation for cancer → use `cancer-variant-interpreter`
- Drug safety signals and adverse event monitoring → use `pharmacovigilance-specialist`
- Immunotherapy clinical trial search and enrollment → use `clinical-trial-analyst`
- FDA approval status and labeling for checkpoint inhibitors → use `fda-consultant`
- Immune repertoire sequencing analysis (TCR/BCR) → use `immune-repertoire-analysis`
- Clinical decision support beyond immunotherapy → use `clinical-decision-support`

## Cross-Reference: Other Skills

- **Somatic/germline variant interpretation for cancer** -> use cancer-variant-interpreter skill
- **Drug safety signals and adverse event monitoring** -> use pharmacovigilance-specialist skill
- **Immunotherapy clinical trial search and enrollment** -> use clinical-trial-analyst skill
- **FDA approval status and labeling for checkpoint inhibitors** -> use fda-consultant skill
- **Target identification and druggability assessment** -> use drug-target-analyst skill
- **Integrated treatment risk-benefit analysis** -> use clinical-decision-support skill
- **Immune cell type expression signatures (CELLxGENE)** -> use cell-type-expression skill

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

### `mcp__chembl__chembl_info` (Bioactivity & Compounds)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `compound_search` | Search molecules by name/SMILES/ID | `query`, `limit` |
| `target_search` | Search biological targets | `query`, `limit` |
| `get_bioactivity` | Compound-target activity data (IC50, Ki, EC50) | `chembl_id`, `target_id`, `limit` |
| `get_mechanism` | Mechanism of action | `chembl_id` |
| `drug_search` | Search drugs by indication or name | `query`, `limit` |
| `get_admet` | ADMET/drug-likeness properties | `chembl_id` |

### `mcp__drugbank__drugbank_info` (Drug-Target Pharmacology)

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

### `mcp__pubmed__pubmed_articles` (Clinical & Translational Literature)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Quick keyword search | `keywords`, `num_results` |
| `search_advanced` | Filtered search | `term`, `journal`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Full article details | `pmid` |

### `mcp__fda__fda_info` (FDA Approvals & Labeling)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_drugs` | Search FDA drug database | `query`, `limit` |
| `get_drug_label` | Full prescribing information / label | `application_number` or `drug_name` |
| `get_adverse_events` | FAERS adverse event reports | `drug_name`, `limit` |
| `search_by_active_ingredient` | Find drugs by ingredient | `ingredient`, `limit` |
| `get_drug_interactions` | FDA-listed drug interactions | `drug_name` |
| `get_recalls` | Drug recall information | `query`, `limit` |
| `get_approvals` | FDA approval history | `query`, `limit` |
| `search_devices` | Medical device search | `query`, `limit` |

### `mcp__ctgov__ctgov_info` (Clinical Trials)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_studies` | Search clinical trials | `query`, `limit` |
| `get_study_details` | Full trial protocol and results | `nct_id` |
| `search_by_condition` | Trials for a disease/condition | `condition`, `limit` |
| `search_by_intervention` | Trials using a specific drug/intervention | `intervention`, `limit` |

### `mcp__depmap__depmap_data` (Cancer Dependency & Functional Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_gene_dependency` | Immune gene essentiality across cancer cell lines | `gene`, `lineage`, `dataset` |
| `get_gene_expression` | Immune checkpoint expression levels in cancer lines | `gene`, `lineage`, `dataset` |
| `get_biomarker_analysis` | Link immune biomarkers to gene dependency | `gene`, `biomarker_gene`, `lineage` |

**DepMap workflow:** Check whether immune targets (PD-L1/CD274, CTLA4, PD-1/PDCD1) show dependency in specific cancer lineages to identify tumors intrinsically reliant on immune checkpoint pathways. This helps prioritize which cancer types may respond to ICI based on functional dependency data rather than expression alone.

```
mcp__depmap__depmap_data(method: "get_gene_dependency", gene: "CD274", lineage: "lung")
mcp__depmap__depmap_data(method: "get_gene_expression", gene: "CTLA4", lineage: "skin")
mcp__depmap__depmap_data(method: "get_biomarker_analysis", gene: "CD274", biomarker_gene: "STK11", lineage: "lung")
```

### `mcp__cbioportal__cbioportal_data` (Cancer Genomics — TMB & Mutation Patterns)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_mutation_frequency` | TMB proxy — mutation count across cancer cohorts | `study_id`, `gene`, `profile_id` |
| `search_studies` | Find immunotherapy cohorts in cBioPortal | `keyword`, `cancer_type` |
| `get_mutations` | Neoantigen landscape — detailed mutation data for specific genes/samples | `study_id`, `gene`, `sample_id` |

**cBioPortal workflow:** Use cBioPortal to assess tumor mutation burden and mutation patterns in immunotherapy cohorts. Query mutation frequencies across TCGA and MSK-IMPACT datasets to contextualize a patient's TMB relative to cancer-type-specific distributions, and retrieve mutation-level data for neoantigen landscape assessment.

```
mcp__cbioportal__cbioportal_data(method: "search_studies", keyword: "immunotherapy")
mcp__cbioportal__cbioportal_data(method: "get_mutation_frequency", study_id: "nsclc_tcga", gene: "TP53")
mcp__cbioportal__cbioportal_data(method: "get_mutations", study_id: "tmb_mskcc_2017", gene: "STK11")
```

---

## 11-Phase ICI Response Prediction Pipeline

### Phase 1: Cancer Type Standardization

```
1. mcp__opentargets__opentargets_info(method: "search_diseases", query: "cancer_type")
   -> Get EFO disease ID and standardized cancer type name

2. mcp__opentargets__opentargets_info(method: "get_disease_details", id: "EFO_xxxxxxx")
   -> Ontology classification, subtypes, known phenotypes

3. Establish cancer-type-specific baseline ICI response rates from literature:
   mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "cancer_type checkpoint inhibitor response rate meta-analysis", num_results: 10)
```

### Phase 2: TMB Classification

```
Classify tumor mutational burden:

| TMB Category | Mutations/Mb | TMB Score Points |
|-------------|-------------|------------------|
| Very-Low    | < 5         | 5                |
| Low         | 5-9         | 10               |
| Intermediate| 10-19       | 20               |
| High        | >= 20       | 30               |

1. If TMB value is provided directly, classify into category above
2. If TMB-High (>= 10 mut/Mb), check FDA-approved indications:
   mcp__fda__fda_info(method: "get_drug_label", drug_name: "pembrolizumab")
   -> Confirm TMB-H pan-tumor indication (>= 10 mut/Mb)

3. Retrieve TMB-response evidence for this cancer type:
   mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "tumor mutational burden cancer_type checkpoint inhibitor predictive", num_results: 10)
```

### Phase 3: Neoantigen Burden Estimation

```
1. Estimate neoantigen load from TMB:
   - General rule: ~1-2 neoantigens per nonsynonymous mutation
   - Higher neoantigen burden -> stronger immune recognition

| Neoantigen Level | Estimated Neoantigens | Score Points |
|-----------------|----------------------|--------------|
| Very-Low        | < 50                 | 5            |
| Low             | 50-149               | 8            |
| Moderate        | 150-399              | 12           |
| High            | >= 400               | 15           |

2. mcp__opentargets__opentargets_info(method: "search_targets", query: "HLA-A")
   -> Check for known HLA alleles affecting neoantigen presentation

3. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "neoantigen burden cancer_type immunotherapy response prediction", num_results: 10)
   -> Cancer-type-specific neoantigen-response correlations
```

### Phase 4: MSI/MMR Status Assessment

```
Classify microsatellite instability / mismatch repair status:

| MSI Status | Definition | MSI Score Points |
|-----------|-----------|------------------|
| MSS       | Microsatellite stable | 5              |
| MSI-L     | Low instability (1 marker) | 10         |
| MSI-H     | High instability (>= 2 markers) | 25    |

1. If MSI status is provided, assign score directly
2. If MMR gene status is provided (MLH1, MSH2, MSH6, PMS2):
   - dMMR (deficient) -> treat as MSI-H (25 pts)
   - pMMR (proficient) -> treat as MSS (5 pts)

3. Check FDA-approved MSI-H indications:
   mcp__fda__fda_info(method: "search_drugs", query: "pembrolizumab microsatellite instability")
   -> Confirm MSI-H/dMMR pan-tumor indication

4. mcp__fda__fda_info(method: "get_approvals", query: "dostarlimab MSI-H")
   -> Additional MSI-H approved agents

5. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "microsatellite instability cancer_type immunotherapy response", num_results: 10)
```

### Phase 5: PD-L1 Expression Scoring

```
Classify PD-L1 expression level:

| PD-L1 Level | TPS / CPS | Score Points |
|------------|-----------|--------------|
| Negative   | TPS < 1%  | 5            |
| Low        | TPS 1-49% | 12           |
| High       | TPS >= 50% or CPS >= 10 | 20 |

1. Accept PD-L1 as TPS (Tumor Proportion Score) or CPS (Combined Positive Score)
2. Check cancer-type-specific PD-L1 cutoffs:
   mcp__fda__fda_info(method: "get_drug_label", drug_name: "pembrolizumab")
   -> Indication-specific PD-L1 thresholds (e.g., NSCLC TPS >= 50%, gastric CPS >= 1)

3. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "PD-L1 expression cancer_type immunotherapy predictive value", num_results: 10)
   -> PD-L1 predictive strength varies by cancer type
```

### Phase 6: Immune Microenvironment Profiling

```
Classify tumor immune microenvironment (TIME):

| TIME Phenotype | Description | ICI Implication |
|---------------|-------------|-----------------|
| Immune-inflamed | High T-cell infiltration, PD-L1+, IFN-gamma signature | Best ICI response |
| Immune-excluded | T-cells at tumor margin, not infiltrating | Moderate response, may need combination |
| Immune-desert | Minimal immune cell presence | Poor response, needs priming |

1. mcp__opentargets__opentargets_info(method: "search_targets", query: "CD8A")
   -> Get target info for T-cell infiltration markers

2. mcp__opentargets__opentargets_info(method: "get_target_disease_associations", targetId: "ENSG_CD8A", diseaseId: "EFO_cancer_type")
   -> CD8+ T-cell association with this cancer type

3. Key immune signature genes to assess:
   - CD8A, CD8B (cytotoxic T-cells)
   - IFNG, CXCL9, CXCL10 (IFN-gamma pathway)
   - GZMA, GZMB, PRF1 (effector function)
   - FOXP3 (regulatory T-cells, immunosuppression)
   - CD274/PD-L1, PDCD1/PD-1 (checkpoint axis)

4. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "tumor immune microenvironment cancer_type checkpoint inhibitor response", num_results: 10)
```

### Phase 7: Resistance Gene Penalties

```
Apply penalties for known ICI resistance mutations:

| Gene | Mutation Impact | Penalty Points | Mechanism |
|------|----------------|---------------|-----------|
| STK11 (LKB1) | Loss-of-function | -10 | Impairs T-cell recruitment, reduces PD-L1 |
| PTEN | Loss-of-function | -10 | Enhances immunosuppressive cytokines, PI3K activation |
| JAK1 | Loss-of-function | -5 to -10 | Impairs IFN-gamma signaling, immune evasion |
| JAK2 | Loss-of-function | -5 to -10 | Impairs IFN-gamma signaling, antigen presentation |
| B2M | Loss-of-function | -15 | Loss of MHC class I, complete antigen presentation failure |

1. For each resistance gene reported mutated:
   mcp__opentargets__opentargets_info(method: "search_targets", query: "GENE_SYMBOL")
   -> Get Ensembl ID and functional annotation

2. mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG_xxxxxxx")
   -> Confirm function relevant to immune evasion

3. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_SYMBOL mutation immunotherapy resistance cancer", num_results: 10)
   -> Evidence strength for this resistance mechanism

4. mcp__chembl__chembl_info(method: "drug_search", query: "GENE_SYMBOL inhibitor")
   -> Potential agents to overcome resistance
```

### Phase 8: Sensitivity Bonuses

```
Apply bonuses for known ICI sensitivity mutations:

| Gene | Mutation Impact | Bonus Points | Mechanism |
|------|----------------|-------------|-----------|
| POLE | Exonuclease domain mutations | +10 | Ultra-high TMB (>100 mut/Mb), strong neoantigen load |
| POLD1 | Exonuclease domain mutations | +5 | Elevated TMB, increased neoantigen generation |

1. For each sensitivity gene reported mutated:
   mcp__opentargets__opentargets_info(method: "search_targets", query: "POLE")
   -> Get target details

2. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "POLE mutation immunotherapy response ultramutator", num_results: 10)
   -> Clinical evidence for exceptional responses

3. mcp__ctgov__ctgov_info(method: "search_studies", query: "POLE mutation immunotherapy")
   -> Ongoing trials specifically enrolling POLE-mutant patients
```

### Phase 9: Clinical Evidence Retrieval

```
1. mcp__pubmed__pubmed_articles(method: "search_advanced", term: "cancer_type immune checkpoint inhibitor phase III", journal: "", start_date: "2020/01/01", end_date: "", num_results: 15)
   -> Landmark trial results for this cancer type

2. mcp__ctgov__ctgov_info(method: "search_by_condition", condition: "cancer_type")
   -> Active immunotherapy trials

3. mcp__ctgov__ctgov_info(method: "search_by_intervention", intervention: "pembrolizumab OR nivolumab OR atezolizumab")
   -> Checkpoint inhibitor trials across cancer types

4. mcp__fda__fda_info(method: "get_approvals", query: "cancer_type immunotherapy")
   -> FDA-approved ICI indications for this cancer type

5. Classify evidence by tier:
   | Tier | Evidence Type | Example |
   |------|-------------|---------|
   | T1 | FDA-approved indication with companion diagnostic | Pembrolizumab + TPS >= 50% in NSCLC |
   | T2 | Phase III trial with positive biomarker subgroup | CheckMate-227 TMB >= 10 in NSCLC |
   | T3 | Phase II / retrospective biomarker analysis | Basket trial biomarker correlations |
   | T4 | Expert opinion / preclinical rationale | NCCN guideline recommendation without RCT |
```

### Phase 10: Resistance Pathway Assessment

```
1. mcp__opentargets__opentargets_info(method: "get_disease_targets_summary", diseaseId: "EFO_cancer_type", minScore: 0.3, size: 50)
   -> All validated targets in this cancer type, identify immune evasion pathways

2. Key resistance pathways to assess:
   - WNT/beta-catenin activation -> immune exclusion
   - PI3K/AKT/mTOR hyperactivation -> immunosuppressive microenvironment
   - MAPK pathway activation -> reduced T-cell function
   - TGF-beta signaling -> immune exclusion, fibrosis
   - IDO1/TDO2 overexpression -> tryptophan depletion, T-cell suppression

3. mcp__chembl__chembl_info(method: "target_search", query: "IDO1")
   -> Identify combination targets to overcome resistance

4. mcp__drugbank__drugbank_info(method: "search_by_target", target: "indoleamine 2,3-dioxygenase")
   -> Existing IDO inhibitors for combination strategies

5. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "immunotherapy resistance pathway cancer_type combination strategy", num_results: 10)
   -> Emerging combination approaches
```

### Phase 11: Final Integration — ICI Response Score Calculation

```
ICI Response Score = TMB_score + MSI_score + PDL1_score + Neoantigen_score + Resistance_penalties + Sensitivity_bonuses

Score Component Ranges:
| Component | Min | Max | Weight Rationale |
|-----------|-----|-----|-----------------|
| TMB Score | 5 | 30 | Strongest pan-cancer biomarker |
| MSI Score | 5 | 25 | FDA-approved predictive biomarker |
| PD-L1 Score | 5 | 20 | Cancer-type-dependent predictive value |
| Neoantigen Score | 5 | 15 | Emerging biomarker, less standardized |
| Resistance Penalties | -15 | 0 | Per gene, cumulative |
| Sensitivity Bonuses | 0 | +15 | Per gene, cumulative |

Maximum possible score: 30 + 25 + 20 + 15 + 0 + 15 = 105 (capped at 100)
Minimum possible score: 5 + 5 + 5 + 5 - 50 + 0 = -30 (floored at 0)
```

---

## Response Tier Classification

| Tier | ICI Response Score | Expected ORR | Recommendation |
|------|-------------------|-------------|----------------|
| **HIGH** | 70-100 | 50-80% | Strong candidate for ICI monotherapy or combination. Priority enrollment in ICI trials. |
| **MODERATE** | 40-69 | 20-50% | Consider ICI combination therapy (ICI+ICI or ICI+chemo). Biomarker-guided trial enrollment. |
| **LOW** | 0-39 | < 20% | ICI monotherapy unlikely to benefit. Consider alternative strategies: chemo, targeted therapy, combination immunotherapy with microenvironment modifiers. |

---

## Confidence Level Assessment

| Confidence | Biomarkers Available | Interpretation |
|-----------|---------------------|---------------|
| **HIGH** | All 4 (TMB + MSI + PD-L1 + Neoantigen/immune signature) | Robust prediction, high reliability |
| **MODERATE** | 3 of 4 biomarkers | Reasonable prediction, recommend additional testing |
| **LOW** | 2 of 4 biomarkers | Preliminary estimate, significant uncertainty |
| **VERY LOW** | Cancer type only (no molecular biomarkers) | Based on historical response rates only, not individualized |

---

## Evidence Classification

| Tier | Evidence Type | Description | Example |
|------|-------------|-------------|---------|
| **T1** | FDA-approved companion diagnostic | Biomarker required for approved ICI indication | Pembrolizumab + TMB-H (>= 10 mut/Mb), Pembrolizumab + MSI-H/dMMR |
| **T2** | Prospective phase III biomarker subgroup | Biomarker validated in randomized trial subgroup analysis | TMB >= 10 in CheckMate-227 (NSCLC) |
| **T3** | Phase II / retrospective analysis | Biomarker correlation from non-randomized or retrospective data | PD-L1 CPS in basket trial analysis |
| **T4** | Expert opinion / preclinical | NCCN recommendation, preclinical rationale, or case series | Emerging biomarkers (e.g., POLE mutations) |

---

## Biomarker-Specific FDA Approval Checking

### TMB-H Indications

```
1. mcp__fda__fda_info(method: "get_drug_label", drug_name: "pembrolizumab")
   -> Check for TMB-H (>= 10 mut/Mb) pan-tumor indication
   -> Approved: Keytruda for unresectable/metastatic TMB-H solid tumors (FoundationOne CDx companion diagnostic)

2. mcp__fda__fda_info(method: "get_approvals", query: "tumor mutational burden")
   -> All TMB-related approvals

3. Confirm assay requirements:
   - FDA-approved CDx: FoundationOne CDx (Foundation Medicine)
   - TMB threshold: >= 10 mutations/Mb
   - Prior treatment requirement: progressed on prior therapy, no satisfactory alternative
```

### MSI-H/dMMR Indications

```
1. mcp__fda__fda_info(method: "search_drugs", query: "microsatellite instability high")
   -> All MSI-H approved agents

2. Key MSI-H/dMMR approved ICIs:
   - Pembrolizumab: MSI-H/dMMR unresectable or metastatic solid tumors (pan-tumor)
   - Dostarlimab: MSI-H/dMMR recurrent or advanced endometrial cancer; dMMR recurrent or advanced solid tumors
   - Nivolumab: MSI-H/dMMR metastatic colorectal cancer (with or without ipilimumab)

3. mcp__fda__fda_info(method: "get_drug_label", drug_name: "dostarlimab")
   -> Confirm dMMR solid tumor indication details

4. mcp__fda__fda_info(method: "get_drug_label", drug_name: "nivolumab")
   -> Confirm MSI-H CRC indication and combination details
```

### PD-L1-Dependent Indications

```
1. mcp__fda__fda_info(method: "get_drug_label", drug_name: "pembrolizumab")
   -> Cancer-type-specific PD-L1 cutoffs:
   - NSCLC: TPS >= 1% (with chemo), TPS >= 50% (monotherapy first-line)
   - Gastric/GEJ: CPS >= 1
   - Cervical: CPS >= 1
   - Head and neck: CPS >= 1
   - Urothelial: CPS >= 10 (first-line cisplatin-ineligible)

2. mcp__fda__fda_info(method: "get_drug_label", drug_name: "atezolizumab")
   -> PD-L1 requirements by indication (IC scoring vs TC scoring)
```

---

## ICI Response Prediction Workflow (Complete)

### Step 1: Gather Patient Inputs

```
Required inputs:
- Cancer type (required)
- TMB value in mut/Mb (optional, strongly recommended)
- MSI/MMR status (optional, strongly recommended)
- PD-L1 TPS or CPS (optional, recommended)
- Known mutations: resistance genes (STK11, PTEN, JAK1, JAK2, B2M) and sensitivity genes (POLE, POLD1)
- Prior treatments (for FDA indication checking)
- Stage/metastatic status
```

### Step 2: Execute 11-Phase Pipeline

```
Run Phases 1-11 sequentially as described above.
For each phase, record:
- Raw data retrieved
- Score assigned
- Evidence tier (T1-T4)
- Source references (PMIDs, NCT IDs, FDA application numbers)
```

### Step 3: Generate Final Report

```
Report structure:
1. Patient Summary (cancer type, stage, prior therapy)
2. Biomarker Profile (TMB, MSI, PD-L1, neoantigen, mutations)
3. ICI Response Score: XX/100
4. Response Tier: HIGH / MODERATE / LOW
5. Confidence Level: HIGH / MODERATE / LOW / VERY LOW
6. Component Breakdown Table
7. FDA-Approved ICI Options (with biomarker match)
8. Active Clinical Trials (from ClinicalTrials.gov)
9. Resistance Mechanisms Identified
10. Recommended Combination Strategies
11. Key Literature References (PMIDs)
12. Limitations and Caveats
```

---

## Multi-Agent Workflow Examples

**"Predict immunotherapy response for a NSCLC patient with TMB 15, MSI-S, PD-L1 TPS 60%"**
1. Immunotherapy Response Predictor -> 11-phase pipeline: TMB score (20) + MSI score (5) + PD-L1 score (20) + neoantigen estimation, resistance/sensitivity gene check, FDA indication matching, ICI Response Score calculation
2. FDA Consultant -> Confirm pembrolizumab first-line monotherapy eligibility (TPS >= 50%), approved regimens and dosing
3. Clinical Trial Analyst -> Active NSCLC immunotherapy trials, biomarker-enriched enrollment opportunities

**"Evaluate ICI response for MSI-H colorectal cancer with STK11 mutation"**
1. Immunotherapy Response Predictor -> MSI-H strong positive signal (25 pts), STK11 resistance penalty (-10 pts), net score calculation, confidence assessment
2. Cancer Variant Interpreter -> STK11 variant pathogenicity, functional impact on immune signaling
3. Pharmacovigilance Specialist -> Safety profiles of pembrolizumab and nivolumab+ipilimumab in MSI-H CRC

**"Compare immunotherapy options for a patient with TMB-high melanoma and JAK2 loss"**
1. Immunotherapy Response Predictor -> TMB-H bonus, JAK2 resistance penalty, overall ICI score, recommended agents
2. Drug Target Analyst -> JAK2 pathway analysis, downstream effects on IFN-gamma signaling, potential combination targets
3. Clinical Trial Analyst -> Trials combining checkpoint inhibitors with JAK pathway modulators or alternative immune approaches

**"Assess immunotherapy candidacy for triple-negative breast cancer, PD-L1 CPS 5, TMB 8"**
1. Immunotherapy Response Predictor -> TMB low-intermediate (10 pts), PD-L1 low-positive (12 pts), TNBC-specific response rates, combination therapy recommendation
2. FDA Consultant -> Confirm atezolizumab+nab-paclitaxel indication (PD-L1 IC >= 1%), pembrolizumab+chemo (CPS >= 10 threshold not met)
3. Clinical Decision Support -> Risk-benefit analysis of ICI+chemo vs chemo alone given moderate prediction

**"Patient with endometrial cancer, dMMR, POLE mutation — is immunotherapy appropriate?"**
1. Immunotherapy Response Predictor -> dMMR/MSI-H (25 pts) + POLE sensitivity bonus (+10 pts), exceptionally favorable profile, HIGH tier prediction
2. FDA Consultant -> Dostarlimab dMMR endometrial indication, pembrolizumab MSI-H pan-tumor and TMB-H indications
3. Clinical Trial Analyst -> POLE-mutant specific immunotherapy trials, novel combination studies

## Completeness Checklist

- [ ] Cancer type standardized with EFO disease ID from Open Targets
- [ ] TMB classified and scored (Very-Low/Low/Intermediate/High)
- [ ] MSI/MMR status assessed and scored
- [ ] PD-L1 expression level scored with cancer-type-specific cutoffs
- [ ] Neoantigen burden estimated and scored
- [ ] Resistance gene mutations checked (STK11, PTEN, JAK1, JAK2, B2M) with penalties applied
- [ ] Sensitivity gene mutations checked (POLE, POLD1) with bonuses applied
- [ ] ICI Response Score calculated (0-100) with component breakdown
- [ ] Response tier and confidence level assigned
- [ ] FDA-approved ICI options listed with biomarker match confirmed
- [ ] Report file created with all sections populated (no `[Analyzing...]` remaining)
