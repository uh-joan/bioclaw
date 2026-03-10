---
name: precision-oncology-advisor
description: Precision oncology clinical decision support advisor. Molecular profiling, biomarker-driven treatment matching, resistance mechanism analysis, clinical trial identification, combination therapy assessment, treatment prioritization. Use when user mentions precision oncology, molecular profiling, cancer treatment, oncology biomarker, tumor mutation, treatment recommendation, resistance mechanism, acquired resistance, bypass pathway, TMB, tumor mutational burden, MSI, microsatellite instability, PD-L1, gene fusion, amplification, actionable mutation, targeted therapy, immunotherapy selection, treatment tiering, clinical trial matching, combination therapy, drug resistance, oncology decision support, cancer genomics, variant interpretation, somatic mutation, treatment algorithm, NCCN, ESMO, molecular tumor board, next-generation sequencing, NGS panel, comprehensive genomic profiling, CGP, liquid biopsy, ctDNA, treatment sequencing, line of therapy, or evidence-based oncology.
---

# Precision Oncology Advisor

Clinical decision support for cancer treatment via molecular profiling, biomarker-driven drug matching, resistance pattern analysis, and clinical trial identification. Synthesizes data from Open Targets, ChEMBL, DrugBank, PubMed, FDA, ClinicalTrials.gov, and bioRxiv to generate evidence-graded treatment recommendations answering "what should we do next?"

## Report-First Workflow

1. **Create report file immediately**: `[tumor]_precision_oncology_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Variant pathogenicity and functional annotation → use `cancer-variant-interpreter`
- Immunotherapy biomarkers and response prediction → use `immunotherapy-response-predictor`
- Drug safety signals and adverse event monitoring → use `pharmacovigilance-specialist`
- Clinical trial pipeline intelligence and enrollment tracking → use `clinical-trial-analyst`
- FDA regulatory status, labels, and approvals → use `fda-consultant`
- Target identification, druggability, and SAR → use `drug-target-analyst`

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

### `mcp__chembl__chembl_info` (Bioactivity & Compound Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `compound_search` | Search molecules by name/SMILES/ID | `query`, `limit` |
| `target_search` | Search biological targets | `query`, `limit` |
| `get_bioactivity` | Compound-target activity data (IC50, Ki, EC50) | `chembl_id`, `target_id`, `limit` |
| `get_mechanism` | Mechanism of action | `chembl_id` |
| `drug_search` | Search drugs by indication or name | `query`, `limit` |
| `get_admet` | ADMET/drug-likeness properties | `chembl_id` |

### `mcp__drugbank__drugbank_info` (Drug Pharmacology & Interactions)

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

### `mcp__pubmed__pubmed_articles` (Oncology Literature)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Quick keyword search | `keywords`, `num_results` |
| `search_advanced` | Filtered search | `term`, `journal`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Full article details | `pmid` |

### `mcp__fda__fda_info` (Regulatory & Approval Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_drugs` | Search FDA drug database | `query`, `limit` |
| `get_drug_label` | Full prescribing information | `drug_id` |
| `get_adverse_events` | Reported adverse events | `drug_name`, `limit` |
| `search_by_active_ingredient` | Find drugs by active ingredient | `ingredient`, `limit` |
| `get_drug_interactions` | FDA-documented interactions | `drug_id` |
| `get_recalls` | Drug recall information | `query`, `limit` |
| `get_approvals` | Approval history and timeline | `query`, `limit` |
| `search_devices` | Companion diagnostic devices | `query`, `limit` |

### `mcp__ctgov__ctgov_info` (Clinical Trial Matching)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_studies` | General clinical trial search | `query`, `limit` |
| `get_study_details` | Full trial protocol and eligibility | `nct_id` |
| `search_by_condition` | Trials for a specific cancer type | `condition`, `limit` |
| `search_by_intervention` | Trials using a specific drug/therapy | `intervention`, `limit` |

### `mcp__biorxiv__biorxiv_info` (Preprint Intelligence)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_preprints` | Search preprints by keyword | `query`, `limit` |
| `get_preprint_details` | Full preprint metadata and abstract | `doi` |
| `get_categories` | Available subject categories | none |
| `search_published_preprints` | Preprints that have been peer-reviewed | `query`, `limit` |

### DepMap — Cancer Dependency Map

| Tool | Method | Use |
|------|--------|-----|
| `mcp__depmap__depmap_data` | `get_drug_sensitivity` | Drug sensitivity across cancer cell lines — preclinical efficacy evidence |
| | `get_gene_dependency` | Gene dependency in patient's tumor lineage — targetability evidence |
| | `get_biomarker_analysis` | Does patient's mutation predict sensitivity to a target/drug? |
| | `get_mutations` | Mutation landscape across cell lines for context |
| | `get_context_info` | Match patient lineage to DepMap cell line contexts |
| | `get_copy_number` | Copy number amplification/deletion patterns |

### cBioPortal — Cancer Genomics

| Tool | Method | Use |
|------|--------|-----|
| `mcp__cbioportal__cbioportal_data` | `search_studies` | Find TCGA/MSK-IMPACT studies matching patient tumor |
| | `get_mutation_frequency` | Prevalence of patient's mutations across cohorts |
| | `get_mutations` | Mutation landscape in matching studies |
| | `get_copy_number` | CNA patterns (amplifications for targeted therapy) |
| | `get_clinical_attributes` | Available clinical outcomes data |

### COSMIC — Catalogue of Somatic Mutations in Cancer

Use COSMIC to find mutation-specific treatment evidence by querying the exact amino acid change or CDS variant observed in the patient. Tissue-specific mutation profiles and pan-cancer recurrence data inform whether a mutation has established clinical significance and support off-label or cross-tumor-type treatment rationale.

| Tool | Method | Use |
|------|--------|-----|
| `mcp__cosmic__cosmic_data` | `search_by_gene` | Mutation landscape for a target gene, optionally filtered by tissue (`gene`, `site`, `limit`) |
| | `get_mutation` | Look up a specific mutation by COSMIC ID e.g. COSM476 (`mutation_id`) |
| | `search_by_site` | Find mutations by tissue site and histology (`site`, `histology`, `gene`, `limit`) |
| | `search_by_mutation_aa` | Search by amino acid change e.g. V600E — link to known treatment evidence (`mutation`, `gene`, `limit`) |
| | `search_by_mutation_cds` | Search by CDS change e.g. c.1799T>A (`mutation`, `gene`, `limit`) |
| | `search_by_position` | Search by genomic position e.g. 7:140453136-140453136 (`position`, `limit`) |
| | `search_free_text` | General search across all COSMIC fields (`query`, `filter`, `limit`) |
| | `get_gene_mutation_profile` | Comprehensive profile: tissue distribution, mutation types, top AA changes (`gene`) |
| | `get_file_download_url` | Get authenticated URL for COSMIC bulk data files (`filepath`) |
| | `list_fields` | List all searchable fields, common sites, and histologies |

---

## 6-Phase Treatment Advisory Pipeline

### Phase 1: Gene/Mutation Resolution and Variant Interpretation

```
1. mcp__opentargets__opentargets_info(method: "search_targets", query: "GENE_SYMBOL")
   -> Get Ensembl gene ID, confirm gene identity

2. mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   -> Full target profile: function, pathways, tractability, known drug modalities

3. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE MUTATION cancer functional significance", num_results: 15)
   -> Variant functional evidence: gain-of-function, loss-of-function, dominant-negative

4. Classify variant actionability:
   - Tier I: FDA-approved companion diagnostic biomarker
   - Tier II: Standard-of-care biomarker (NCCN/ESMO guideline)
   - Tier III: Clinical trial eligibility biomarker
   - Tier IV: Preclinical evidence of actionability
```

### Phase 2: Treatment Identification via OpenTargets/ChEMBL/DrugBank

```
1. mcp__opentargets__opentargets_info(method: "search_diseases", query: "cancer_type")
   -> Get EFO disease ID for the specific cancer

2. mcp__opentargets__opentargets_info(method: "get_target_disease_associations", targetId: "ENSG00000xxxxx", diseaseId: "EFO_xxxxxxx")
   -> Association score and evidence breakdown for this target in this cancer

3. mcp__chembl__chembl_info(method: "drug_search", query: "target_name inhibitor", limit: 30)
   -> All compounds with activity against the target

4. mcp__drugbank__drugbank_info(method: "search_by_target", target: "target_name", limit: 20)
   -> Approved and investigational drugs for this target

5. mcp__fda__fda_info(method: "search_drugs", query: "drug_name", limit: 10)
   -> Confirm FDA approval status and approved indications

6. mcp__fda__fda_info(method: "get_drug_label", drug_id: "drug_id")
   -> Check biomarker requirements, approved indications, dosing
```

### Phase 3: Pathway and Network Analysis

```
1. mcp__drugbank__drugbank_info(method: "get_pathways", drugbank_id: "DBxxxxx")
   -> Map the signaling pathway (e.g., RAS-RAF-MEK-ERK, PI3K-AKT-mTOR)

2. mcp__opentargets__opentargets_info(method: "search_targets", query: "downstream_effector")
   -> Identify upstream/downstream targets in the same pathway

3. mcp__drugbank__drugbank_info(method: "search_by_target", target: "pathway_node", limit: 15)
   -> Drugs hitting other nodes in the pathway (combination candidates)

4. mcp__chembl__chembl_info(method: "get_mechanism", chembl_id: "CHEMBLxxxxx")
   -> Confirm mechanism of action for each candidate drug
```

### Phase 4: Resistance Mechanism Discovery

```
1. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_SYMBOL DRUG resistance mechanism cancer", num_results: 20)
   -> Published resistance mechanisms for this target-drug combination

2. mcp__biorxiv__biorxiv_info(method: "search_preprints", query: "GENE resistance mutation cancer", limit: 15)
   -> Emerging resistance data not yet peer-reviewed

3. mcp__chembl__chembl_info(method: "get_bioactivity", chembl_id: "CHEMBLxxxxx", target_id: "MUTANT_TARGET_ID", limit: 30)
   -> Activity of drug against known resistance mutants

4. Classify resistance type:
   - On-target: gatekeeper mutation, solvent-front mutation, compound mutation
   - Bypass: parallel pathway activation (e.g., MET amplification under EGFR TKI)
   - Downstream: reactivation below the drug target (e.g., MAPK reactivation)
   - Phenotypic: EMT, lineage plasticity, small-cell transformation
```

### Phase 5: Clinical Trial Matching

```
1. mcp__ctgov__ctgov_info(method: "search_by_condition", condition: "cancer_type", limit: 30)
   -> Active trials for this cancer type

2. mcp__ctgov__ctgov_info(method: "search_by_intervention", intervention: "drug_name", limit: 20)
   -> Trials using the candidate drug(s)

3. mcp__ctgov__ctgov_info(method: "search_studies", query: "GENE_SYMBOL mutation basket trial", limit: 15)
   -> Biomarker-selected basket/umbrella trials

4. mcp__ctgov__ctgov_info(method: "get_study_details", nct_id: "NCTxxxxxxxx")
   -> Full eligibility criteria, endpoints, enrollment status

5. Score each trial using Clinical Trial Matching Score (see below)
```

### Phase 6: Report Synthesis

```
Compile findings into a structured treatment advisory report:

1. Patient Molecular Profile Summary
   - Actionable alterations with tier classification
   - TMB, MSI, PD-L1 status if available

2. Treatment Recommendations (prioritized by tier)
   - Each recommendation includes: drug, mechanism, evidence level, FDA status, key references

3. Resistance Landscape
   - Known resistance mechanisms for recommended therapies
   - Monitoring strategy and next-line options

4. Clinical Trial Options
   - Top-scoring trials with matching rationale
   - Enrollment status and key eligibility criteria

5. Combination Therapy Opportunities
   - Synergy rationale, overlapping toxicity assessment

6. Evidence Citations
   - PubMed references, FDA labels, guideline citations
```

---

## Treatment Prioritization Framework

### Tier Classification

| Tier | Definition | Examples | Evidence Requirement |
|------|-----------|----------|---------------------|
| **Tier 1** | FDA-approved for this indication + biomarker | Osimertinib for EGFR T790M NSCLC, Imatinib for BCR-ABL CML | FDA label with companion diagnostic |
| **Tier 2** | FDA-approved different indication, same biomarker | Vemurafenib (melanoma) for BRAF V600E in hairy cell leukemia | FDA label + published evidence in other tumor |
| **Tier 3** | Phase 2-3 clinical trials with preliminary efficacy | Sotorasib for KRAS G12C (before approval), basket trials | Clinical trial data, conference abstracts |
| **Tier 4** | Phase 1 or preclinical evidence only | Novel target inhibitor with in vitro activity | Preclinical data, early-phase trial open |

### Within-Tier Ranking Criteria

```
For drugs within the same tier, rank by:
1. Strength of clinical evidence (randomized > single-arm > case series)
2. Response rate and durability (PFS, OS benefit)
3. Toxicity profile and patient tolerability
4. Drug-drug interaction potential (check via DrugBank)
5. Availability and access (approved > compassionate use > trial only)
6. Sequencing considerations (preserve future options)
```

---

## Molecular Profile Integration

### Biomarker Categories and Their Treatment Implications

| Biomarker Type | Examples | Treatment Approach |
|---------------|----------|-------------------|
| **Activating mutation** | EGFR L858R, BRAF V600E, KRAS G12C | Matched targeted inhibitor |
| **Gene fusion** | ALK-EML4, ROS1-CD74, NTRK fusions | Fusion-specific TKI |
| **Amplification** | HER2, MET, FGFR | Target-specific antibody or TKI |
| **Loss-of-function** | BRCA1/2, ATM, PALB2 | PARP inhibitor, platinum sensitivity |
| **TMB-High** | > 10 mut/Mb | Immune checkpoint inhibitor |
| **MSI-High** | dMMR | Pembrolizumab (tumor-agnostic) |
| **PD-L1 High** | TPS >= 50%, CPS >= 10 | Front-line immunotherapy |

### Multi-Alteration Integration

```
When multiple actionable alterations co-exist:
1. Prioritize by driver hierarchy (trunk vs branch mutation)
2. Assess co-occurring alteration impact on drug sensitivity
   - e.g., concurrent KRAS mutation predicts resistance to EGFR TKI
   - e.g., TP53 co-mutation may reduce benefit of targeted therapy
3. Consider combination strategies if supported by evidence
4. Flag mutually exclusive biomarkers (e.g., EGFR mutation vs ALK fusion)
```

---

## Resistance Mechanism Analysis

### Resistance Classification

| Category | Mechanism | Timeline | Example |
|----------|----------|----------|---------|
| **Primary (intrinsic)** | Pre-existing feature preventing response | No initial response | KRAS mutation under anti-EGFR antibody |
| **Acquired (secondary)** | Emerges under treatment selection pressure | After initial response | EGFR T790M under erlotinib |
| **Bypass pathway** | Alternative pathway provides survival signal | Variable | MET amplification under osimertinib |
| **Target mutation** | Drug-binding site alteration | After initial response | ALK G1202R under crizotinib |
| **Phenotypic** | Lineage or identity change | Late | Small-cell transformation in EGFR NSCLC |

### Resistance Analysis Workflow

```
1. Identify known resistance mechanisms:
   mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "DRUG TARGET resistance mechanism", num_results: 20)

2. Check next-generation inhibitors:
   mcp__chembl__chembl_info(method: "get_bioactivity", chembl_id: "NEXT_GEN_DRUG", target_id: "MUTANT_TARGET")
   -> Activity against resistance mutants

3. Assess bypass pathway drugs:
   mcp__drugbank__drugbank_info(method: "search_by_target", target: "bypass_target")
   -> Drugs for combination to overcome bypass resistance

4. Find clinical trials for resistant disease:
   mcp__ctgov__ctgov_info(method: "search_studies", query: "DRUG resistant CANCER_TYPE", limit: 15)

5. Check emerging data:
   mcp__biorxiv__biorxiv_info(method: "search_preprints", query: "DRUG resistance overcome novel", limit: 10)
```

### DepMap-Guided Treatment Prioritization

Use DepMap preclinical data to strengthen or challenge treatment recommendations with cell line evidence.

**Workflow:**

1. **Identify patient's tumor lineage and key mutations**
   ```
   mcp__depmap__depmap_data(method: "get_context_info", query: "lung adenocarcinoma")
   -> Match patient lineage to DepMap contexts (e.g., lung NSCLC, breast luminal)
   ```

2. **Query drug sensitivity for candidate therapies in matching lineages**
   ```
   mcp__depmap__depmap_data(method: "get_drug_sensitivity", drug: "osimertinib", lineage: "lung")
   -> IC50/AUC distribution across lung cancer cell lines — does the drug show selective activity?
   ```

3. **Check if patient's mutations predict dependency on specific targets**
   ```
   mcp__depmap__depmap_data(method: "get_gene_dependency", gene: "EGFR", lineage: "lung")
   -> CRISPR/RNAi dependency scores — is the target essential in this lineage?

   mcp__depmap__depmap_data(method: "get_biomarker_analysis", mutation: "EGFR_L858R", target: "EGFR")
   -> Do cell lines with this mutation show stronger dependency on the target?
   ```

4. **Cross-reference with clinical trial data for translational evidence**
   ```
   mcp__depmap__depmap_data(method: "get_mutations", gene: "KRAS", lineage: "colorectal")
   -> Mutation landscape across cell lines — identify co-occurring alterations that modulate response

   mcp__depmap__depmap_data(method: "get_copy_number", gene: "MET", lineage: "lung")
   -> Copy number patterns — correlate amplification with drug sensitivity

   mcp__ctgov__ctgov_info(method: "search_studies", query: "GENE biomarker-selected basket trial", limit: 15)
   -> Match DepMap findings to active clinical trials validating the preclinical signal
   ```

**Integration with Treatment Tiers:**

- DepMap dependency + drug sensitivity data can **upgrade Tier 4 to Tier 3** when preclinical signal is strong and consistent across multiple cell lines in the patient's lineage
- Absence of dependency in matching lineage cell lines is a **caution flag** even for Tier 1-2 therapies (may indicate subpopulation non-response)
- DepMap biomarker analysis linking patient's specific mutation to drug sensitivity provides **mechanistic support** for off-label or trial-based recommendations

### cBioPortal Tumor Context

Use cBioPortal to contextualize the patient's molecular profile against large cancer genomics cohorts (TCGA, MSK-IMPACT, GENIE). This informs treatment prioritization by revealing mutation prevalence, co-occurrence patterns, and available outcomes data.

```
1. Find relevant studies for the patient's cancer type:
   mcp__cbioportal__cbioportal_data(method="search_studies", query="non-small cell lung cancer")
   -> Identify TCGA, MSK-IMPACT, and other cohorts matching the patient's tumor type
   -> Select studies with sufficient sample size for meaningful frequency analysis

2. Check how common the patient's mutations are in matching cohorts:
   mcp__cbioportal__cbioportal_data(method="get_mutation_frequency", studyId="luad_tcga", genes=["EGFR", "KRAS", "TP53"])
   -> High-frequency mutations are well-characterized with established treatment algorithms
   -> Low-frequency mutations may require off-label or trial-based approaches

3. Examine mutation landscape for co-occurrence and exclusivity patterns:
   mcp__cbioportal__cbioportal_data(method="get_mutations", studyId="luad_tcga", gene="EGFR")
   -> Identify hotspot distribution (e.g., exon 19 del vs L858R prevalence)
   -> Co-mutation patterns that impact treatment selection (e.g., TP53 co-mutation reduces TKI benefit)

4. Assess copy number alteration context:
   mcp__cbioportal__cbioportal_data(method="get_copy_number", studyId="luad_tcga", gene="MET")
   -> Amplification frequency in the cohort — informs combination therapy rationale
   -> Homozygous deletion patterns for tumor suppressors

5. Check available clinical outcomes data:
   mcp__cbioportal__cbioportal_data(method="get_clinical_attributes", studyId="luad_tcga")
   -> Available survival, response, and treatment data for correlative analysis
   -> Enables cohort-level outcome context for the patient's mutation profile
```

**Integration with Treatment Prioritization:**
- Mutations found at high frequency in cBioPortal cohorts typically have well-established treatment guidelines (Tier 1-2)
- Rare mutations benefit from cross-study analysis across multiple cBioPortal cohorts to aggregate evidence
- Co-mutation patterns (e.g., KRAS + STK11) identified in cBioPortal can modify expected treatment response and should inform combination strategies
- CNA data from cBioPortal strengthens amplification-based treatment decisions (e.g., MET amplification for capmatinib/tepotinib)

---

## Clinical Trial Matching Score (0-100)

### Scoring Components

| Component | Points | Criteria |
|-----------|--------|----------|
| **Molecular Match** | 0-40 | Exact biomarker match (40), same pathway (25), same target class (15), broad eligibility (5) |
| **Clinical Eligibility** | 0-25 | Meets all criteria (25), meets most with waiverable exclusions (15), uncertain eligibility (5) |
| **Evidence Strength** | 0-20 | Phase 2+ efficacy signal (20), Phase 1 dose-escalation with signal (12), first-in-human (5) |
| **Trial Phase** | 0-10 | Phase 3 (10), Phase 2 (7), Phase 1/2 (5), Phase 1 (3) |
| **Geographic Feasibility** | 0-5 | Active site within reach (5), site available but distant (3), no accessible site (0) |

### Score Interpretation

| Score Range | Recommendation |
|-------------|---------------|
| **80-100** | Strongly recommend enrollment discussion |
| **60-79** | Good candidate, review eligibility details |
| **40-59** | Consider if no higher-tier options available |
| **20-39** | Low priority, monitor for expansion |
| **0-19** | Not recommended at this time |

---

## Treatment Decision Tree

### By Cancer Type and Molecular Profile

```
NSCLC (Non-Small Cell Lung Cancer):
  EGFR mutation (L858R, exon 19 del)
    -> First-line: Osimertinib (Tier 1)
    -> Resistance (T790M): Osimertinib if not used first-line
    -> Resistance (C797S): Clinical trial (Tier 3-4)
    -> Resistance (MET amp): Osimertinib + MET inhibitor (Tier 2-3)
  ALK fusion
    -> First-line: Alectinib or Lorlatinib (Tier 1)
    -> Resistance (G1202R): Lorlatinib (Tier 1)
  KRAS G12C
    -> Second-line: Sotorasib or Adagrasib (Tier 1)
  ROS1 fusion
    -> Crizotinib or Entrectinib (Tier 1)
  BRAF V600E
    -> Dabrafenib + Trametinib (Tier 1)
  NTRK fusion
    -> Larotrectinib or Entrectinib (Tier 1, tumor-agnostic)
  PD-L1 >= 50%, no driver
    -> Pembrolizumab monotherapy (Tier 1)
  TMB-High
    -> Pembrolizumab (Tier 1, tumor-agnostic)

Breast Cancer:
  HER2-amplified
    -> Trastuzumab + pertuzumab + chemotherapy (Tier 1)
    -> Resistance: T-DXd (Tier 1)
  HR+/HER2-
    -> CDK4/6 inhibitor + endocrine therapy (Tier 1)
    -> ESR1 mutation: Elacestrant (Tier 1)
    -> PIK3CA mutation: Alpelisib + fulvestrant (Tier 1)
  BRCA1/2 mutant
    -> Olaparib or Talazoparib (Tier 1)

Melanoma:
  BRAF V600E/K
    -> Encorafenib + Binimetinib or Dabrafenib + Trametinib (Tier 1)
    -> Resistance: Immunotherapy (Tier 1)
  BRAF wild-type
    -> Nivolumab + Ipilimumab (Tier 1)
  NRAS Q61
    -> MEK inhibitor clinical trial (Tier 3)

Colorectal Cancer:
  MSI-High/dMMR
    -> Pembrolizumab or Nivolumab +/- Ipilimumab (Tier 1)
  KRAS/NRAS wild-type, left-sided
    -> Anti-EGFR (Cetuximab/Panitumumab) + chemotherapy (Tier 1)
  BRAF V600E
    -> Encorafenib + Cetuximab (Tier 1)
  HER2-amplified
    -> Trastuzumab + pertuzumab (Tier 2)
```

---

## Combination Therapy Assessment

### Synergy Evaluation Framework

```
For any proposed combination:

1. Mechanistic rationale:
   mcp__drugbank__drugbank_info(method: "get_pathways", drugbank_id: "DBxxxxx")
   -> Do the drugs hit complementary nodes in the same pathway or parallel pathways?

2. Preclinical synergy evidence:
   mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "DRUG_A DRUG_B combination synergy cancer", num_results: 15)

3. Clinical combination data:
   mcp__ctgov__ctgov_info(method: "search_studies", query: "DRUG_A DRUG_B combination", limit: 15)

4. Overlapping toxicity check:
   mcp__fda__fda_info(method: "get_adverse_events", drug_name: "DRUG_A", limit: 20)
   mcp__fda__fda_info(method: "get_adverse_events", drug_name: "DRUG_B", limit: 20)
   -> Flag shared high-grade toxicities (e.g., both hepatotoxic, both cause QTc prolongation)

5. Drug-drug interaction check:
   mcp__drugbank__drugbank_info(method: "get_drug_interactions", drugbank_id: "DBxxxxx")
   -> CYP450 interactions, transporter competition, protein binding displacement
```

### Combination Assessment Criteria

| Factor | Favorable | Unfavorable |
|--------|----------|-------------|
| **Mechanistic** | Vertical (same pathway, different nodes) or horizontal (parallel pathways) | Redundant (same target, same mechanism) |
| **Toxicity** | Non-overlapping toxicity profiles | Shared dose-limiting toxicity |
| **PK interaction** | No significant CYP/transporter interaction | Major CYP3A4 inhibition/induction |
| **Clinical evidence** | Phase 2+ combination data | No combination data, extrapolation only |
| **Scheduling** | Compatible dosing schedules | Conflicting food/timing requirements |

### Sequence Optimization

```
When choosing order of therapies:
1. Use most effective option first (maximize initial response)
2. Preserve non-cross-resistant options for later lines
3. Consider cumulative toxicity (e.g., platinum exposure limits)
4. Factor in patient performance status trajectory
5. Check if earlier therapy impacts later eligibility:
   mcp__ctgov__ctgov_info(method: "get_study_details", nct_id: "NCTxxxxxxxx")
   -> Review "prior therapy" exclusion criteria
```

---

## Multi-Agent Workflow Examples

**"NSCLC patient with EGFR L858R progressing on osimertinib - what are the options?"**
1. Precision Oncology Advisor -> Identify resistance mechanisms (C797S, MET amp, HER3, small-cell transformation), match to next-line therapies, tier-prioritize options
2. Cancer Variant Interpreter -> Characterize the resistance mutation(s) from NGS results, assess functional impact
3. Clinical Trial Analyst -> Active trials for osimertinib-resistant EGFR NSCLC, basket trials accepting EGFR-mutant patients
4. Pharmacovigilance Specialist -> Safety profiles of candidate next-line agents, comparative toxicity

**"Newly diagnosed triple-negative breast cancer - build a molecular-guided treatment plan"**
1. Precision Oncology Advisor -> Profile actionable alterations (BRCA, PD-L1, PIK3CA, AR), match to approved therapies and trials, resistance anticipation
2. Immunotherapy Response Predictor -> Assess immunotherapy benefit (PD-L1, TILs, TMB, immune gene signatures)
3. Drug Target Analyst -> Druggability of any novel targets identified on comprehensive genomic profiling
4. Clinical Trial Analyst -> Front-line and neoadjuvant trials incorporating biomarker selection

**"Colorectal cancer with BRAF V600E and MSI-high - immunotherapy or targeted?"**
1. Precision Oncology Advisor -> Treatment decision tree for dual-biomarker scenario, prioritize immunotherapy vs BRAF-directed therapy, sequence recommendation
2. FDA Consultant -> Approved indications for each option, label restrictions, companion diagnostic requirements
3. Pharmacovigilance Specialist -> Comparative safety of encorafenib+cetuximab vs pembrolizumab in this context
4. Clinical Trial Analyst -> Combination trials testing immunotherapy + BRAF inhibitor

**"Rare tumor with NTRK fusion - is there a tumor-agnostic option?"**
1. Precision Oncology Advisor -> Tumor-agnostic approvals (larotrectinib, entrectinib), evidence by histology, resistance patterns (NTRK solvent-front mutations)
2. Drug Target Analyst -> NTRK target biology, next-generation TRK inhibitors (selitrectinib, repotrectinib) for resistance
3. Clinical Trial Analyst -> NTRK-directed trials, basket trials accepting this histology
4. FDA Consultant -> Tumor-agnostic regulatory pathway, real-world evidence requirements

**"Design a combination strategy for KRAS G12C NSCLC"**
1. Precision Oncology Advisor -> Combination rationale (sotorasib + SHP2 inhibitor, sotorasib + immunotherapy), synergy evidence, overlapping toxicity assessment, sequence optimization
2. Drug Target Analyst -> Pathway analysis (RAS-MAPK feedback reactivation), co-target identification (SOS1, SHP2, mTOR)
3. Clinical Trial Analyst -> Active combination trials for KRAS G12C, dose-escalation data
4. Pharmacovigilance Specialist -> Toxicity signals from early combination data, class effect predictions

## Completeness Checklist

- [ ] Gene/mutation resolved with Ensembl ID and variant actionability tiered (I-IV)
- [ ] Treatment options identified via Open Targets, ChEMBL, and DrugBank
- [ ] FDA approval status confirmed for each candidate therapy
- [ ] Pathway and network analysis completed for combination rationale
- [ ] Resistance mechanisms catalogued with next-line options identified
- [ ] Clinical trials matched and scored using Clinical Trial Matching Score
- [ ] Combination therapy assessed for synergy, overlapping toxicity, and PK interactions
- [ ] DepMap preclinical evidence integrated where available
- [ ] Treatment recommendations prioritized by tier with evidence citations
- [ ] Report file verified with no remaining `[Analyzing...]` placeholders
