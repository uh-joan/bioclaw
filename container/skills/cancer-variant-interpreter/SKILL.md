---
name: cancer-variant-interpreter
description: Precision oncology cancer variant interpreter and molecular tumor board analyst. Somatic mutation interpretation, variant classification, therapeutic associations, resistance mechanisms, prognostic implications, evidence-graded clinical reports. Use when user mentions somatic mutation, cancer variant, tumor mutation, oncogene, tumor suppressor, variant interpretation, molecular tumor board, MTB, precision oncology, actionable mutation, BRAF V600E, KRAS G12C, EGFR mutation, ALK fusion, ROS1, NTRK, HER2 amplification, MSI-H, TMB, PD-L1, variant of unknown significance, VUS, AMP ASCO CAP, tier classification, resistance mutation, T790M, C797S, clinical actionability, variant annotation, oncology biomarker, companion diagnostic, targeted therapy, cancer genomics, NGS interpretation, tumor profiling, or genomic report.
---

# Cancer Variant Interpreter

Precision oncology molecular tumor board workflow. Interprets somatic cancer mutations into evidence-graded clinical reports covering therapeutic associations, resistance mechanisms, and prognostic implications. Uses Open Targets for target-disease evidence, ChEMBL for compound bioactivity, DrugBank for approved drug profiles, PubMed for clinical evidence, ClinicalTrials.gov for investigational options, and FDA for drug approvals and labeling.

## Report-First Workflow

1. **Create report file immediately**: `variant_interpretation_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Drug-target pharmacology and SAR for identified targets → use `drug-target-analyst`
- Drug safety signals and adverse event profiling → use `pharmacovigilance-specialist`
- Clinical trial matching for actionable variants → use `clinical-trial-analyst`
- FDA approval status and companion diagnostics → use `fda-consultant`
- Clinical decision support for treatment selection → use `clinical-decision-support`
- Risk assessment for treatment regimens → use `risk-management-specialist`
- Germline variant interpretation for inherited disease → use `variant-interpretation`
- Pharmacogenomic dosing based on patient genotype → use `pharmacogenomics-specialist`

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

### `mcp__pubmed__pubmed_articles` (Clinical Evidence Literature)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Quick keyword search | `keywords`, `num_results` |
| `search_advanced` | Filtered search | `term`, `journal`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Full article details | `pmid` |

### `mcp__ctgov__ctgov_info` (Clinical Trials)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_studies` | Search clinical trials by keyword | `query`, `limit` |
| `get_study_details` | Full trial details (arms, endpoints, eligibility) | `nct_id` |
| `search_by_condition` | Trials for a specific condition | `condition`, `limit` |
| `search_by_intervention` | Trials for a specific drug/intervention | `intervention`, `limit` |

### `mcp__fda__fda_info` (FDA Approvals & Labeling)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_drugs` | Search FDA drug database | `query`, `limit` |
| `get_drug_label` | Full prescribing information (indications, dosing, warnings) | `application_number` or `drug_name` |
| `get_adverse_events` | FAERS adverse event reports | `drug_name`, `limit` |
| `search_by_active_ingredient` | Drugs by active ingredient | `ingredient`, `limit` |
| `get_drug_interactions` | FDA-listed drug interactions | `drug_name` |
| `get_recalls` | Drug recall information | `query`, `limit` |
| `get_approvals` | Approval history and timeline | `drug_name` |
| `search_devices` | Companion diagnostic device search | `query`, `limit` |

### `mcp__ensembl__ensembl_data` (Genomic Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `lookup_gene` | Get gene info by ID or symbol | `gene_id`, `species`, `expand` |
| `get_transcripts` | Get transcripts for a gene | `gene_id`, `canonical_only` |
| `get_variant_consequences` | Predict variant effects (VEP) | `variants` (array of HGVS) |
| `get_regulatory_features` | Get regulatory elements in region | `region`, `species`, `feature_type`, `cell_type` |
| `get_xrefs` | Get cross-database references | `gene_id`, `external_db`, `all_levels` |

### `mcp__clinvar__clinvar_data` (ClinVar Germline vs Somatic Context)

Use ClinVar to distinguish germline pathogenic variants from somatic-only alterations and to cross-reference clinical significance when classifying cancer variants — critical for accurate AMP/ASCO/CAP tier assignment and identifying hereditary cancer syndrome overlap.

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_variants` | Free-text search for ClinVar variants | `query`, `retmax`, `retstart` |
| `get_variant_summary` | Get summary for variant IDs (max 50) | `id` or `ids` (array) |
| `search_by_gene` | Search variants by gene symbol | `gene`, `retmax`, `retstart` |
| `search_by_condition` | Search by disease/phenotype | `condition`, `retmax`, `retstart` |
| `search_by_significance` | Search by clinical significance (e.g. pathogenic) | `significance`, `retmax`, `retstart` |
| `get_variant_details` | Detailed variant record with HGVS, locations, submissions | `id` |
| `combined_search` | Multi-filter: gene + condition + significance | `gene`, `condition`, `significance`, `retmax`, `retstart` |
| `get_gene_variants_summary` | Search gene then return summaries (max 50) | `gene`, `limit` |

### DepMap — Cancer Dependency Map

| Tool | Method | Use |
|------|--------|-----|
| `mcp__depmap__depmap_data` | `get_mutations` | Mutation prevalence across 1000+ cancer cell lines |
| | `get_biomarker_analysis` | Test if a mutation predicts dependency on specific genes (functional impact) |
| | `get_gene_dependency` | Is the mutated gene essential? Loss-of-function tolerance |
| | `get_copy_number` | Copy number context for the variant's gene |
| | `get_gene_expression` | Expression levels across cancer contexts |

### gnomAD — Population Variant Frequencies

| Tool | Method | Use |
|------|--------|-----|
| `mcp__gnomad__gnomad_data` | `get_variant` | Population frequency — distinguish somatic (absent in gnomAD) vs germline |
| | `get_population_frequencies` | Per-population AF for germline variant filtering |
| | `get_gene_constraint` | Gene LoF intolerance — tumor suppressor evidence |

### cBioPortal — Cancer Genomics

| Tool | Method | Use |
|------|--------|-----|
| `mcp__cbioportal__cbioportal_data` | `search_studies` | Find relevant TCGA/MSK-IMPACT studies for the cancer type |
| | `get_mutation_frequency` | How often is this gene mutated in the tumor type? |
| | `get_mutations` | Specific mutation patterns (hotspots, truncating) |
| | `get_copy_number` | Amplification/deletion patterns |
| | `get_molecular_profiles` | Available data types for a study |

### COSMIC — Catalogue of Somatic Mutations in Cancer

Use COSMIC to assess somatic mutation recurrence and frequency across cancer types. Cross-reference variant hotspot status, tissue-specific mutation prevalence, and pan-cancer recurrence to strengthen or weaken driver classification and AMP/ASCO/CAP tier assignment.

| Tool | Method | Use |
|------|--------|-----|
| `mcp__cosmic__cosmic_data` | `search_by_gene` | Mutation spectrum for a gene across cancers, optionally filtered by tissue (`gene`, `site`, `limit`) |
| | `get_mutation` | Look up a specific mutation by COSMIC ID e.g. COSM476 (`mutation_id`) |
| | `search_by_site` | Find mutations by tissue site and histology (`site`, `histology`, `gene`, `limit`) |
| | `search_by_mutation_aa` | Search by amino acid change e.g. V600E — confirm hotspot status (`mutation`, `gene`, `limit`) |
| | `search_by_mutation_cds` | Search by CDS change e.g. c.1799T>A (`mutation`, `gene`, `limit`) |
| | `search_by_position` | Search by genomic position e.g. 7:140453136-140453136 (`position`, `limit`) |
| | `search_free_text` | General search across all COSMIC fields (`query`, `filter`, `limit`) |
| | `get_gene_mutation_profile` | Comprehensive profile: tissue distribution, mutation types, top AA changes (`gene`) |
| | `get_file_download_url` | Get authenticated URL for COSMIC bulk data files (`filepath`) |
| | `list_fields` | List all searchable fields, common sites, and histologies |

---

## 8-Phase Variant Interpretation Workflow

### Phase 1: Gene Disambiguation and Ensembl ID Resolution

```
1. mcp__opentargets__opentargets_info(method: "search_targets", query: "GENE_SYMBOL", size: 5)
   -> Resolve to Ensembl gene ID (ENSG...), confirm correct gene, check aliases

2. mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   -> Full gene profile: protein function, subcellular location, protein class,
      known cancer roles, pathway membership

3. mcp__chembl__chembl_info(method: "target_search", query: "GENE_SYMBOL")
   -> Get ChEMBL target ID for downstream bioactivity queries

4. mcp__ensembl__ensembl_data(method: "get_transcripts", gene_id: "ENSG00000xxxxx", canonical_only: true)
   -> Get canonical transcript for variant annotation (MANE Select)

5. mcp__ensembl__ensembl_data(method: "get_variant_consequences", variants: ["ENST00000xxxxx:c.1799T>A"])
   -> VEP consequence prediction: impact, SIFT, PolyPhen, regulatory overlap
```

**Key considerations:**
- Always resolve gene symbol to Ensembl ID before querying associations
- Check for gene aliases (e.g., PDGFRA vs CD140a, ERBB2 vs HER2)
- Confirm the protein product and its functional role (kinase, receptor, transcription factor)

### Phase 2: Clinical Evidence Query

```
1. mcp__opentargets__opentargets_info(method: "search_diseases", query: "cancer_type")
   -> Get EFO disease ID for the specific tumor type

2. mcp__opentargets__opentargets_info(method: "get_target_disease_associations",
   targetId: "ENSG00000xxxxx", diseaseId: "EFO_xxxxxxx", minScore: 0.1, size: 20)
   -> Association score with evidence breakdown: genetic, somatic, literature, known drugs

3. mcp__pubmed__pubmed_articles(method: "search_keywords",
   keywords: "GENE_SYMBOL mutation cancer_type clinical significance", num_results: 20)
   -> Published clinical evidence for this variant in this tumor type

4. mcp__pubmed__pubmed_articles(method: "search_advanced",
   term: "GENE_SYMBOL specific_variant therapeutic", journal: "Journal of Clinical Oncology",
   num_results: 10)
   -> High-impact clinical evidence from top oncology journals
```

### Phase 3: Prevalence Analysis

```
1. mcp__pubmed__pubmed_articles(method: "search_keywords",
   keywords: "GENE_SYMBOL mutation prevalence frequency cancer_type", num_results: 15)
   -> Mutation frequency in this tumor type

2. mcp__opentargets__opentargets_info(method: "get_disease_targets_summary",
   diseaseId: "EFO_xxxxxxx", minScore: 0.3, size: 50)
   -> Rank this gene among all targets for this cancer type

3. mcp__pubmed__pubmed_articles(method: "search_keywords",
   keywords: "GENE_SYMBOL pan-cancer frequency TCGA GENIE", num_results: 10)
   -> Pan-cancer prevalence from large genomic datasets
```

**Interpret prevalence context:**
- Hotspot mutations (e.g., BRAF V600E in melanoma ~50%) vs rare variants
- Tumor-type-specific frequencies vs pan-cancer occurrence
- Co-mutation patterns (e.g., KRAS + TP53 in pancreatic cancer)

### Phase 4: Therapeutic Options (Approved + Investigational)

```
1. mcp__drugbank__drugbank_info(method: "search_by_target", target: "GENE_SYMBOL", limit: 20)
   -> All drugs targeting this gene product (approved, investigational, experimental)

2. mcp__fda__fda_info(method: "search_drugs", query: "drug_name_for_mutation", limit: 10)
   -> FDA approval status for matched therapies

3. mcp__fda__fda_info(method: "get_drug_label", drug_name: "matched_drug")
   -> Prescribing information: approved indications, biomarker requirements,
      companion diagnostic, dosing

4. mcp__chembl__chembl_info(method: "drug_search", query: "GENE_SYMBOL inhibitor", limit: 20)
   -> All compounds in development against this target

5. mcp__chembl__chembl_info(method: "get_mechanism", chembl_id: "CHEMBLxxxxx")
   -> Mechanism of action for each therapeutic candidate

6. mcp__fda__fda_info(method: "search_devices", query: "GENE_SYMBOL companion diagnostic")
   -> FDA-approved companion diagnostic tests for this biomarker
```

### Phase 5: Resistance Mechanisms

```
1. mcp__pubmed__pubmed_articles(method: "search_keywords",
   keywords: "GENE_SYMBOL resistance mutation acquired mechanism", num_results: 20)
   -> Known resistance mutations and mechanisms

2. mcp__pubmed__pubmed_articles(method: "search_advanced",
   term: "GENE_SYMBOL drug_name resistance clinical",
   start_date: "2020-01-01", num_results: 15)
   -> Recent resistance data from clinical experience

3. mcp__chembl__chembl_info(method: "get_bioactivity",
   chembl_id: "DRUG_CHEMBL_ID", target_id: "MUTANT_TARGET_ID", limit: 50)
   -> Activity of drug against wild-type vs mutant (resistant) target

4. mcp__drugbank__drugbank_info(method: "search_by_target",
   target: "GENE_SYMBOL mutant", limit: 10)
   -> Drugs specifically designed for resistant variants
```

### Phase 6: Clinical Trial Search

```
1. mcp__ctgov__ctgov_info(method: "search_studies",
   query: "GENE_SYMBOL mutation cancer_type", limit: 20)
   -> Active trials for patients with this specific variant

2. mcp__ctgov__ctgov_info(method: "search_by_condition",
   condition: "cancer_type", limit: 30)
   -> All trials for this cancer type (filter by biomarker eligibility)

3. mcp__ctgov__ctgov_info(method: "search_by_intervention",
   intervention: "targeted_drug_name", limit: 15)
   -> Trials for specific matched therapies

4. mcp__ctgov__ctgov_info(method: "get_study_details", nct_id: "NCTxxxxxxxx")
   -> Eligibility criteria, arms, primary endpoints, enrollment status
```

### Phase 7: Prognostic Context

```
1. mcp__pubmed__pubmed_articles(method: "search_keywords",
   keywords: "GENE_SYMBOL mutation prognosis survival outcome cancer_type", num_results: 15)
   -> Prognostic impact of this mutation

2. mcp__pubmed__pubmed_articles(method: "search_keywords",
   keywords: "GENE_SYMBOL predictive biomarker response cancer_type", num_results: 15)
   -> Predictive value for treatment response

3. mcp__opentargets__opentargets_info(method: "get_target_disease_associations",
   targetId: "ENSG00000xxxxx", diseaseId: "EFO_xxxxxxx")
   -> Evidence types that inform prognosis (somatic mutations, literature)
```

### Phase 8: Report Synthesis

Compile findings into structured clinical report with the following sections:

```
VARIANT INTERPRETATION REPORT
=============================

1. VARIANT SUMMARY
   - Gene: [symbol] ([Ensembl ID])
   - Variant: [protein change, e.g., p.V600E]
   - Variant type: [missense, frameshift, amplification, fusion, etc.]
   - Tumor type: [cancer_type]

2. AMP/ASCO/CAP CLASSIFICATION
   - Tier: [I / II / III / IV] (see classification framework below)
   - Evidence level: [A / B / C / D]

3. THERAPEUTIC ASSOCIATIONS
   - T1 (FDA-approved): [drug — indication — companion diagnostic]
   - T2 (Phase 2-3): [drug — trial — evidence]
   - T3 (Preclinical): [drug — evidence]
   - T4 (Computational): [predicted associations]

4. RESISTANCE MECHANISMS
   - Known resistance mutations: [list]
   - Mechanism category: [target alteration / bypass / downstream / phenotypic]
   - Next-line options after resistance: [drugs]

5. PROGNOSTIC IMPLICATIONS
   - Overall survival impact: [favorable / unfavorable / neutral / unknown]
   - Predictive value: [response to specific therapy]

6. CLINICAL TRIAL OPTIONS
   - Biomarker-matched trials: [NCT IDs with phase and status]
   - Basket/umbrella trials: [mutation-agnostic options]

7. CLINICAL ACTIONABILITY RATING
   - Rating: [HIGH / MODERATE / LOW / UNKNOWN]

8. REFERENCES
   - [PMIDs, trial IDs, FDA labels cited]
```

### Functional Impact via DepMap

Use DepMap data to assess whether a variant has functional consequences across cancer cell lines. This complements clinical evidence (Phases 2-7) with large-scale functional genomics data.

```
1. Check mutation prevalence in DepMap cell lines:
   mcp__depmap__depmap_data(method: "get_mutations", gene: "GENE_SYMBOL")
   -> How frequently is this gene mutated across 1000+ cancer cell lines?
   -> Is the specific variant (e.g., V600E) recurrent, suggesting selection pressure?

2. Assess if the gene is essential (dependency scores):
   mcp__depmap__depmap_data(method: "get_gene_dependency", gene: "GENE_SYMBOL")
   -> Negative CERES/Chronos scores indicate the gene is essential for cell viability
   -> Compare dependency across lineages to identify cancer-type-specific essentiality
   -> Essential genes with activating mutations are strong oncogene addiction candidates

3. Test if the mutation predicts dependency on other genes (synthetic lethality / oncogene addiction):
   mcp__depmap__depmap_data(method: "get_biomarker_analysis", gene: "GENE_SYMBOL")
   -> Does mutation status in GENE predict dependency on specific other genes?
   -> Identifies synthetic lethal partners (e.g., BRCA1-mutant lines depend on PARP1)
   -> Identifies oncogene addiction (e.g., KRAS-mutant lines depend on KRAS itself)

4. Cross-reference with copy number to distinguish driver vs passenger:
   mcp__depmap__depmap_data(method: "get_copy_number", gene: "GENE_SYMBOL")
   -> Is the mutated gene amplified (suggesting oncogene) or deleted (tumor suppressor)?
   -> Copy number context helps classify ambiguous variants
   -> Co-amplification patterns may reveal pathway-level dependencies

5. Optional — Check expression levels for context:
   mcp__depmap__depmap_data(method: "get_gene_expression", gene: "GENE_SYMBOL")
   -> Is the gene expressed in the relevant cancer lineage?
   -> Low expression + mutation may indicate passenger status
   -> High expression + mutation strengthens driver hypothesis
```

**Interpreting DepMap results for variant classification:**
- **Driver evidence:** Recurrent mutation + gene is essential (negative dependency score) + mutation predicts self-dependency = strong driver
- **Passenger evidence:** Rare mutation + gene is not essential + no biomarker associations = likely passenger
- **Therapeutic vulnerability:** Mutation predicts dependency on a druggable gene = actionable synthetic lethality
- **Copy number context:** Amplification of a mutated oncogene strengthens Tier I/II classification; homozygous deletion of a tumor suppressor confirms LOF

### Somatic vs Germline Classification via gnomAD + cBioPortal

Use gnomAD population frequencies and cBioPortal cancer cohort data to distinguish somatic drivers from germline polymorphisms. This is critical for accurate AMP/ASCO/CAP tier assignment (Tier IV = benign/germline).

```
1. Check gnomAD population frequency (present = likely germline):
   mcp__gnomad__gnomad_data(method="get_variant", variant_id="7-140753336-A-T")
   -> If AF > 0.01 (1%) in any population, likely germline benign -> Tier IV
   -> If absent from gnomAD, consistent with somatic origin -> proceed to step 2

2. Check cBioPortal mutation frequency in matching cancer type (recurrent = likely driver):
   mcp__cbioportal__cbioportal_data(method="get_mutation_frequency", studyId="brca_tcga", genes=["BRAF"])
   -> High recurrence in the tumor type supports somatic driver status
   -> Cross-reference with specific mutation patterns (hotspot vs distributed)

   mcp__cbioportal__cbioportal_data(method="search_studies", query="breast cancer")
   -> Find relevant TCGA/MSK-IMPACT studies for the patient's cancer type

   mcp__cbioportal__cbioportal_data(method="get_mutations", studyId="brca_tcga", gene="BRAF")
   -> Examine specific mutation patterns — hotspot clustering supports oncogene, truncating distribution supports tumor suppressor

3. Check gene constraint (LoF intolerant = tumor suppressor candidate):
   mcp__gnomad__gnomad_data(method="get_gene_constraint", gene="BRCA1")
   -> High pLI / low LOEUF = gene is intolerant to loss-of-function
   -> LoF-intolerant genes with truncating mutations are strong tumor suppressor candidates

   mcp__gnomad__gnomad_data(method="get_population_frequencies", variant_id="7-140753336-A-T")
   -> Per-population allele frequencies for fine-grained germline filtering
   -> Some variants are population-specific polymorphisms (e.g., higher AF in specific ancestry)
```

**Decision matrix:**
- **Absent in gnomAD + recurrent in cBioPortal** = strong somatic driver evidence -> Tier I-III depending on therapeutic associations
- **Absent in gnomAD + rare in cBioPortal** = possible passenger or rare driver -> Tier III, investigate functional data
- **Present in gnomAD (AF > 1%) + not recurrent in cancer** = likely germline benign -> Tier IV
- **Low AF in gnomAD (0.01-1%) + recurrent in cancer** = ambiguous, may be low-penetrance germline risk variant -> requires further investigation (segregation, tumor-only vs matched normal)
- **LoF-intolerant gene + truncating variant + absent in gnomAD** = high-confidence tumor suppressor LOF -> assess for synthetic lethality (e.g., PARP inhibitors for BRCA)

---

## Evidence Grading System

### Therapeutic Evidence Tiers

| Tier | Definition | Criteria | Example |
|------|-----------|----------|---------|
| **T1** | FDA-approved therapy with Level A evidence | FDA approval in this tumor type with this biomarker; NCCN Category 1 | Vemurafenib for BRAF V600E melanoma |
| **T2** | Standard-of-care with Phase 2-3 data | Phase 2-3 trial data showing clinical benefit; NCCN Category 2A | Crizotinib for MET exon 14 skipping NSCLC |
| **T3** | Preclinical or case report evidence | Case reports, small series, or preclinical data suggesting benefit | HER2 amplification in cholangiocarcinoma |
| **T4** | Computational or extrapolated | In silico predictions, pathway inference, cross-tumor-type extrapolation | Novel kinase domain mutation predicted activating |

### Clinical Actionability Rating

| Rating | Criteria |
|--------|----------|
| **HIGH** | T1 or T2 evidence exists; FDA-approved therapy available for this variant in this tumor type; companion diagnostic available |
| **MODERATE** | T2 evidence in a different tumor type; active Phase 2-3 trials available; strong biological rationale with preliminary clinical data |
| **LOW** | T3 evidence only; preclinical data or case reports; early-phase trials only; variant type suggests possible response but no direct evidence |
| **UNKNOWN** | T4 or no evidence; variant of unknown significance (VUS); no clinical data; computational prediction only |

---

## AMP/ASCO/CAP Variant Classification

### Tier System for Somatic Variant Interpretation

| Tier | Level | Classification | Description |
|------|-------|---------------|-------------|
| **Tier I** | A | Strong clinical significance | FDA-approved therapy, professional guidelines (NCCN, ESMO), well-powered studies with consensus |
| **Tier I** | B | Strong clinical significance | Well-powered studies with expert consensus but not yet in guidelines |
| **Tier II** | C | Potential clinical significance | FDA-approved therapies for different tumor types; multiple small studies; investigational therapies with clinical trial eligibility |
| **Tier II** | D | Potential clinical significance | Preclinical or case-level data showing potential significance |
| **Tier III** | — | Unknown significance | No published evidence of cancer association; not observed in population databases at significant frequency |
| **Tier IV** | — | Benign or likely benign | Observed at significant frequency in population databases (gnomAD, ExAC); no known functional impact |

### Classification Decision Process

```
Step 1: Is the variant in a known cancer gene?
  YES -> Proceed to Step 2
  NO  -> Check COSMIC, cBioPortal recurrence -> If absent, likely Tier III or IV

Step 2: Is there an FDA-approved therapy for this variant?
  YES, same tumor type    -> Tier I, Level A
  YES, different tumor    -> Tier II, Level C
  NO                      -> Proceed to Step 3

Step 3: Is there clinical trial evidence?
  Phase 3 with consensus  -> Tier I, Level B
  Phase 2-3 data          -> Tier II, Level C
  Case reports only       -> Tier II, Level D
  NO                      -> Proceed to Step 4

Step 4: Is there preclinical/functional evidence?
  Known activating/LOF    -> Tier II, Level D
  Predicted functional     -> Tier III
  No evidence             -> Tier III

Step 5: Check population frequency
  > 1% in gnomAD          -> Tier IV (likely benign)
  Known germline benign   -> Tier IV
```

---

## Variant Type Decision Tree

### Activating Mutations (Gain-of-Function)

```
Identified activating mutation (e.g., BRAF V600E, KRAS G12C, EGFR L858R)
|
+-> Query approved targeted therapies:
|   mcp__fda__fda_info(method: "search_drugs", query: "GENE inhibitor")
|   mcp__drugbank__drugbank_info(method: "search_by_target", target: "GENE")
|
+-> Check if mutation is a known hotspot:
|   mcp__pubmed__pubmed_articles(method: "search_keywords",
|     keywords: "GENE variant hotspot oncogenic driver")
|
+-> Assess resistance landscape:
|   mcp__pubmed__pubmed_articles(method: "search_keywords",
|     keywords: "GENE drug resistance acquired mutation")
|
+-> Search for active clinical trials:
    mcp__ctgov__ctgov_info(method: "search_studies",
      query: "GENE mutation inhibitor")
```

### Loss-of-Function Mutations (Tumor Suppressors)

```
Identified LOF mutation (e.g., TP53 truncating, BRCA1/2, RB1, PTEN loss)
|
+-> Check for synthetic lethality targets:
|   mcp__pubmed__pubmed_articles(method: "search_keywords",
|     keywords: "GENE loss synthetic lethality therapeutic vulnerability")
|
+-> Query drugs exploiting LOF:
|   mcp__drugbank__drugbank_info(method: "search_by_target",
|     target: "synthetic_lethal_partner")
|   (e.g., BRCA1/2 LOF -> PARP inhibitors)
|
+-> Assess prognostic impact:
|   mcp__pubmed__pubmed_articles(method: "search_keywords",
|     keywords: "GENE loss prognosis cancer_type survival")
|
+-> Search trials for LOF-directed therapies:
    mcp__ctgov__ctgov_info(method: "search_studies",
      query: "GENE deficient cancer therapy")
```

### Gene Amplifications

```
Identified amplification (e.g., HER2/ERBB2, MET, FGFR2, CDK4)
|
+-> Confirm therapeutic relevance by copy number threshold:
|   mcp__pubmed__pubmed_articles(method: "search_keywords",
|     keywords: "GENE amplification copy number threshold clinical")
|
+-> Query anti-GENE therapies:
|   mcp__fda__fda_info(method: "search_drugs", query: "anti-GENE antibody")
|   mcp__drugbank__drugbank_info(method: "search_by_target", target: "GENE")
|
+-> Check companion diagnostic requirements:
|   mcp__fda__fda_info(method: "search_devices",
|     query: "GENE amplification companion diagnostic")
|
+-> Assess co-amplification context:
    mcp__pubmed__pubmed_articles(method: "search_keywords",
      keywords: "GENE amplification co-occurring alteration cancer")
```

### Gene Fusions

```
Identified fusion (e.g., EML4-ALK, BCR-ABL, NTRK fusions, ROS1 fusions)
|
+-> Query fusion-specific therapies:
|   mcp__fda__fda_info(method: "search_drugs", query: "GENE fusion inhibitor")
|   mcp__drugbank__drugbank_info(method: "search_by_target",
|     target: "FUSION_KINASE")
|
+-> Check tumor-agnostic approvals:
|   mcp__fda__fda_info(method: "get_drug_label", drug_name: "fusion_inhibitor")
|   -> Review if approval is tumor-agnostic (e.g., larotrectinib for NTRK)
|
+-> Assess fusion partner significance:
|   mcp__pubmed__pubmed_articles(method: "search_keywords",
|     keywords: "GENE1-GENE2 fusion clinical significance partner")
|
+-> Search basket trials:
    mcp__ctgov__ctgov_info(method: "search_studies",
      query: "GENE fusion basket trial tumor agnostic")
```

### Resistance Mutations

```
Identified resistance mutation (e.g., EGFR T790M, ALK G1202R, BRAF splice variants)
|
+-> Confirm resistance mechanism:
|   mcp__pubmed__pubmed_articles(method: "search_keywords",
|     keywords: "GENE resistance_variant mechanism drug_name resistance")
|
+-> Query next-generation inhibitors:
|   mcp__chembl__chembl_info(method: "drug_search",
|     query: "GENE next generation inhibitor resistance")
|   mcp__drugbank__drugbank_info(method: "search_by_target", target: "GENE mutant")
|
+-> Check activity against resistant variant:
|   mcp__chembl__chembl_info(method: "get_bioactivity",
|     chembl_id: "NEXT_GEN_DRUG", target_id: "MUTANT_TARGET", limit: 20)
|
+-> Search trials for resistant patients:
    mcp__ctgov__ctgov_info(method: "search_studies",
      query: "GENE resistance_variant progression after drug_name")
```

---

## Resistance Mechanism Framework

### Primary vs Acquired Resistance

| Type | Definition | Timing | Investigation |
|------|-----------|--------|---------------|
| **Primary (intrinsic)** | No initial response to targeted therapy | At treatment start | Check co-mutations, pathway activation, tumor heterogeneity |
| **Acquired (secondary)** | Response followed by progression | Months to years on therapy | Re-biopsy or ctDNA for new resistance mutations |

### Resistance Mechanism Categories

| Category | Mechanism | Examples | Next-Line Strategy |
|----------|----------|---------|-------------------|
| **Target alteration** | Secondary mutation in drug target | EGFR T790M, ALK G1202R, BCR-ABL T315I | Next-gen inhibitor (osimertinib, lorlatinib, ponatinib) |
| **Target amplification** | Increased copies of target gene | MET amplification on EGFR TKI, BRAF amplification | Add target-specific inhibitor |
| **Bypass pathway** | Alternative pathway activation | MET amplification, HER2 upregulation, RAS activation | Combination therapy targeting bypass |
| **Downstream activation** | Constitutive activation downstream | MAPK reactivation, PI3K/AKT activation, STAT3 | Downstream pathway inhibitor |
| **Phenotypic transformation** | Histologic or lineage change | Small cell transformation from NSCLC, EMT | Chemotherapy, alternative approach |
| **Drug efflux** | Increased drug pump expression | P-gp/ABCB1 upregulation | Alternative agent not substrate |

### Resistance Investigation Workflow

```
1. Identify prior therapy and duration of response:
   -> Short response (< 3 months) suggests primary resistance
   -> Extended response (> 6 months) suggests acquired resistance

2. Query known resistance mechanisms:
   mcp__pubmed__pubmed_articles(method: "search_keywords",
     keywords: "GENE DRUG resistance mechanism clinical", num_results: 20)

3. Check for next-generation agents:
   mcp__drugbank__drugbank_info(method: "search_by_target", target: "GENE", limit: 20)
   -> Filter for agents with activity against resistant variants

4. Search combination strategies:
   mcp__ctgov__ctgov_info(method: "search_studies",
     query: "GENE inhibitor combination resistance cancer", limit: 15)

5. Assess preclinical data for novel approaches:
   mcp__chembl__chembl_info(method: "get_bioactivity",
     target_id: "MUTANT_TARGET_CHEMBL_ID", limit: 50)
   -> Identify compounds with activity against the resistant form
```

---

## Multi-Agent Workflow Examples

**"Interpret BRAF V600E found in a patient's melanoma NGS report"**
1. Cancer Variant Interpreter -> Gene resolution, AMP/ASCO/CAP Tier I-A classification, therapeutic associations (vemurafenib/dabrafenib + trametinib), resistance landscape (NRAS, MEK1/2 mutations, BRAF amplification), prognostic context, clinical trial options
2. FDA Consultant -> Approved drug labels, companion diagnostic requirements (Cobas BRAF V600 test), dosing, contraindications
3. Clinical Trial Analyst -> Active Phase 3 trials for BRAF-mutant melanoma, novel combinations, immunotherapy + targeted therapy sequences

**"KRAS G12C found in stage IV non-small cell lung cancer"**
1. Cancer Variant Interpreter -> Variant classification, sotorasib/adagrasib evidence (T1-T2), resistance mechanisms (KRAS amplification, MET bypass, RAS-MAPK reactivation), co-mutation context (STK11, KEAP1)
2. Drug Target Analyst -> KRAS G12C inhibitor SAR, bioactivity comparison, next-gen covalent inhibitors in development
3. Clinical Trial Analyst -> Active trials for KRAS G12C NSCLC (combinations, novel agents)
4. Pharmacovigilance Specialist -> Safety profile comparison of sotorasib vs adagrasib

**"BRCA2 truncating mutation in pancreatic adenocarcinoma"**
1. Cancer Variant Interpreter -> LOF classification, synthetic lethality with PARP inhibition, olaparib/rucaparib evidence in pancreatic cancer, platinum sensitivity prediction, prognostic implications
2. Clinical Decision Support -> Treatment sequencing (platinum-based chemo -> PARP inhibitor maintenance), germline testing recommendation
3. Clinical Trial Analyst -> PARP inhibitor trials in pancreatic cancer, combination strategies
4. Risk Management Specialist -> Hereditary cancer syndrome implications, family screening recommendations

**"ALK fusion detected but patient progressed on crizotinib"**
1. Cancer Variant Interpreter -> Resistance mutation profiling (G1202R, I1171T, etc.), next-gen ALK inhibitor selection (lorlatinib for G1202R), sequential therapy evidence, re-biopsy recommendations
2. Drug Target Analyst -> Bioactivity comparison of ALK inhibitors against specific resistance mutations (crizotinib vs ceritinib vs alectinib vs lorlatinib)
3. FDA Consultant -> Approval status and sequencing guidelines for ALK inhibitors
4. Pharmacovigilance Specialist -> CNS penetration profiles, toxicity comparison across ALK inhibitors

**"Multiple variants found on tumor panel: EGFR amplification + PIK3CA H1047R in breast cancer"**
1. Cancer Variant Interpreter -> Interpret each variant independently, then assess co-occurrence significance, evaluate combination strategies (anti-HER therapy + PI3K inhibitor), check for mutual exclusivity or synergy data
2. Drug Target Analyst -> Pathway crosstalk analysis (EGFR/HER2 -> RAS-MAPK and PI3K-AKT), compound selectivity profiles
3. Clinical Trial Analyst -> Trials enrolling for co-mutated populations, basket trials accepting either alteration
4. Clinical Decision Support -> Prioritize actionable variants, recommend sequencing vs combination approach

---

## Completeness Checklist

- [ ] Gene symbol resolved to Ensembl ID with alias check
- [ ] Canonical transcript identified and variant consequence predicted (VEP)
- [ ] AMP/ASCO/CAP tier and evidence level assigned with rationale
- [ ] gnomAD population frequency checked (somatic vs germline distinction)
- [ ] cBioPortal mutation frequency and hotspot analysis completed
- [ ] FDA-approved therapies and companion diagnostics identified
- [ ] Resistance mechanisms documented with next-line options
- [ ] Active clinical trials searched and biomarker-matched trials listed
- [ ] Prognostic implications assessed with literature support
- [ ] Clinical actionability rating assigned (HIGH/MODERATE/LOW/UNKNOWN)
