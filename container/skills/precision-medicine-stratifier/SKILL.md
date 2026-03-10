---
name: precision-medicine-stratifier
description: Precision medicine patient stratification and risk scoring. Genomic-clinical integration, disease-specific routing, pharmacogenomic profiling, molecular pathway enrichment, treatment recommendations. Use when user mentions precision medicine, patient stratification, risk score, genomic risk, treatment recommendation, pharmacogenomics, CYP2D6, CYP2C19, metabolizer status, HLA screening, germline risk, somatic variants, molecular profiling, disease routing, comorbidity screening, clinical decision support, tiered treatment, risk tier, DPYD, UGT1A1, or precision oncology stratification.
---

# Precision Medicine Stratifier

Patient-level genomic-clinical integration with disease-specific routing. Produces a Precision Medicine Risk Score (0-100) combining genetic burden, clinical features, molecular markers, and pharmacogenomic modifiers, with tiered treatment intensity recommendations. Uses Open Targets for target-disease evidence, ChEMBL for compound pharmacology, DrugBank for drug-gene interactions and pathways, PubMed for literature evidence, FDA for drug labels and adverse events, ClinicalTrials.gov for trial matching, and NLM for clinical coding and gene annotation.

## Report-First Workflow

1. **Create report file immediately**: `[patient]_precision_medicine_stratifier_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Somatic variant interpretation for cancer → use `cancer-variant-interpreter`
- Immunotherapy biomarker analysis and response prediction → use `immunotherapy-response-predictor`
- Comprehensive oncology treatment planning and sequencing → use `precision-oncology-advisor`
- Deep pharmacogenomic analysis (CYP/HLA/DPYD) → use `pharmacogenomics-specialist`
- Rare or monogenic disease diagnosis → use `rare-disease-diagnosis`
- Clinical guideline-based decision support → use `clinical-decision-support`

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

### `mcp__chembl__chembl_info` (Compound Pharmacology & Bioactivity)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `compound_search` | Search molecules by name/SMILES/ID | `query`, `limit` |
| `target_search` | Search biological targets | `query`, `limit` |
| `get_bioactivity` | Compound-target activity data (IC50, Ki, EC50) | `chembl_id`, `target_id`, `limit` |
| `get_mechanism` | Mechanism of action | `chembl_id` |
| `drug_search` | Search drugs by indication or name | `query`, `limit` |
| `get_admet` | ADMET/drug-likeness properties | `chembl_id` |

### `mcp__drugbank__drugbank_info` (Drug-Gene Interactions & Pathways)

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

### `mcp__pubmed__pubmed_articles` (Clinical & Genomic Literature)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Quick keyword search | `keywords`, `num_results` |
| `search_advanced` | Filtered search | `term`, `journal`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Full article details | `pmid` |

### `mcp__fda__fda_info` (Drug Labels, Safety & Approvals)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_drugs` | Search FDA drug database | `query`, `limit` |
| `get_drug_label` | Full prescribing information (boxed warnings, PGx) | `application_number` or `drug_name` |
| `get_adverse_events` | FAERS adverse event reports | `drug_name`, `reaction`, `limit` |
| `search_by_active_ingredient` | Drugs by active ingredient | `ingredient`, `limit` |
| `get_drug_interactions` | FDA-documented drug interactions | `drug_name` |
| `get_recalls` | Drug recall history | `drug_name`, `limit` |
| `get_approvals` | FDA approval history and timeline | `drug_name`, `limit` |
| `search_devices` | Search medical devices (companion diagnostics) | `query`, `limit` |

### `mcp__ctgov__ctgov_info` (Clinical Trial Matching)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_studies` | Search clinical trials | `query`, `limit` |
| `get_study_details` | Full trial protocol and eligibility | `nct_id` |
| `search_by_condition` | Trials by condition/disease | `condition`, `status`, `limit` |
| `search_by_intervention` | Trials by drug/intervention | `intervention`, `status`, `limit` |

### `mcp__nlm__nlm_ct_codes` (Clinical Coding & Gene Annotation)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `icd-10-cm` | ICD-10-CM diagnosis codes | `query` |
| `icd-11` | ICD-11 diagnosis codes | `query` |
| `hcpcs-LII` | HCPCS Level II procedure codes | `query` |
| `npi-organizations` | NPI lookup for organizations | `query` |
| `npi-individuals` | NPI lookup for individual providers | `query` |
| `hpo-vocabulary` | Human Phenotype Ontology terms | `query` |
| `conditions` | Standardized condition names | `query` |
| `rx-terms` | RxNorm drug terminology | `query` |
| `loinc-questions` | LOINC laboratory test codes | `query` |
| `ncbi-genes` | NCBI gene annotations and identifiers | `query` |
| `major-surgeries-implants` | Surgical procedure classification | `query` |

### `mcp__gwas__gwas_data` (GWAS Catalog — Genetic Risk & Trait Associations)

Use the GWAS Catalog to support germline risk assessment (Phase 2) and molecular pathway enrichment (Phase 6) by retrieving published GWAS associations for patient variants and disease-gene evidence for risk scoring.

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_by_trait` | Search EFO traits by term, get associations — identifies genetic risk loci for the patient's disease | `trait`, `page`, `size` |
| `get_variant` | Get variant info by rs ID — annotate patient variants with GWAS context | `rs_id` |
| `get_variant_associations` | All associations for a variant — determines if a patient's variant has known disease associations | `rs_id`, `page`, `size` |
| `get_gene_associations` | All GWAS associations for a gene — supports molecular pathway enrichment | `gene`, `page`, `size` |
| `get_trait_associations` | All associations for an EFO trait ID | `efo_id`, `page`, `size` |
| `search_studies` | Search studies by disease trait name | `disease_trait`, `page`, `size` |
| `get_study` | Study details by GCST accession — sample size, ancestry for evidence grading | `study_id` |
| `search_associations` | Search associations by query or PubMed ID | `query`, `pubmed_id`, `page`, `size` |

**GWAS Catalog Workflow:** In Phase 2 (Germline Risk Assessment), use `get_variant_associations` to check whether patient germline variants have established GWAS associations — variants reported across multiple GWAS studies strengthen the Genetic Risk score component. Use `search_by_trait` to retrieve the full landscape of GWAS loci for the patient's disease, informing polygenic risk context. In Phase 6 (Molecular Pathway Enrichment), use `get_gene_associations` to assess whether genes in the patient's mutational profile have broader GWAS support across related traits, identifying pathway-level convergence.

```
# Retrieve GWAS associations for the patient's disease
mcp__gwas__gwas_data(method: "search_by_trait", trait: "breast carcinoma")

# Check if a patient's germline variant has known GWAS associations
mcp__gwas__gwas_data(method: "get_variant_associations", rs_id: "rs1799950")

# Assess GWAS evidence for a gene in the patient's molecular profile
mcp__gwas__gwas_data(method: "get_gene_associations", gene: "BRCA1")
```

### `mcp__clinvar__clinvar_data` (ClinVar Stratification Biomarker Lookup)

Use ClinVar to look up clinical significance of stratification biomarker variants — supports germline risk assessment (Phase 2) by retrieving expert-panel classifications for pathogenic variants in high-penetrance disease genes used for risk tier assignment.

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

### `mcp__hpo__hpo_data` (Human Phenotype Ontology)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_hpo_terms` | Search phenotype terms for clinical feature standardization | `query`, `max`, `category` |
| `get_hpo_term` | Get full term details (definition, synonyms) | `id` (HP:XXXXXXX) |
| `get_hpo_children` | Get more specific sub-phenotypes | `id` |
| `get_hpo_ancestors` | Get broader phenotype categories | `id`, `max` |
| `batch_get_hpo_terms` | Resolve multiple phenotypes at once | `ids` |
| `compare_hpo_terms` | Measure similarity between phenotypes | `id1`, `id2` |

### `mcp__ensembl__ensembl_data` (Genomic Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `lookup_gene` | Get gene info by ID or symbol | `gene_id`, `species`, `expand` |
| `get_variant_consequences` | Predict variant effects (VEP) | `variants` (array of HGVS) |
| `get_transcripts` | Get transcripts for a gene | `gene_id`, `canonical_only` |
| `search_genes` | Search genes by name/description | `query`, `species`, `biotype`, `limit` |

### `mcp__cosmic__cosmic_data` (COSMIC — Somatic Mutation Catalogue)

Use COSMIC for somatic mutation stratification when computing the Molecular Features component of the Precision Medicine Risk Score. Query mutation recurrence across cancer types, tissue-specific prevalence, and known hotspot status to inform whether a somatic variant is a recognized driver (upgrades score) or a rare/uncharacterized change (neutral or low score contribution).

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_by_gene` | Find mutations for a gene, optionally filtered by tissue | `gene`, `site`, `limit` |
| `get_mutation` | Look up specific mutation by COSMIC ID e.g. COSM476 | `mutation_id` |
| `search_by_site` | Find mutations by tissue site/histology | `site`, `histology`, `gene`, `limit` |
| `search_by_mutation_aa` | Search by amino acid change e.g. V600E | `mutation`, `gene`, `limit` |
| `search_by_mutation_cds` | Search by CDS change e.g. c.1799T>A | `mutation`, `gene`, `limit` |
| `search_by_position` | Search by genomic position e.g. 7:140453136-140453136 | `position`, `limit` |
| `search_free_text` | General search across all fields | `query`, `filter`, `limit` |
| `get_gene_mutation_profile` | Comprehensive profile: tissue distribution, mutation types, top AA changes | `gene` |
| `get_file_download_url` | Get authenticated URL for COSMIC bulk data files | `filepath` |
| `list_fields` | List all searchable fields, common sites, and histologies |

### `mcp__gtex__gtex_data` (Tissue Expression & eQTLs)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_genes` | Search genes in GTEx | `query`, `page`, `pageSize` |
| `get_gene_expression` | Expression across tissues | `gencodeId`, `tissueSiteDetailId` |
| `get_median_gene_expression` | Median expression per tissue | `gencodeId`, `tissueSiteDetailId` |
| `get_tissue_info` | Available tissue metadata | — |

### `mcp__gwas__gwas_data` (GWAS Catalog — Genetic Evidence in Stratification)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_associations` | Search associations by query or PubMed ID | `query`, `pubmed_id`, `page`, `size` |
| `get_variant` | Get variant info by rs ID e.g. rs7329174 | `rs_id` |
| `get_variant_associations` | All associations for a variant | `rs_id`, `page`, `size` |
| `search_by_trait` | Search EFO traits by term, get associations for top match | `trait`, `page`, `size` |
| `get_study` | Study details by GCST accession | `study_id` |
| `search_studies` | Search studies by disease trait name | `disease_trait`, `page`, `size` |
| `get_gene_associations` | All GWAS associations for a gene | `gene`, `page`, `size` |
| `get_region_associations` | Associations in a genomic region | `chromosome`, `start`, `end`, `page`, `size` |
| `get_trait_associations` | All associations for an EFO trait ID | `efo_id`, `page`, `size` |
| `search_genes` | Gene info with genomic context | `gene` |

**GWAS Catalog Workflow:** Use the GWAS Catalog to strengthen the genetic evidence component of patient stratification. In Phase 2 (Germline Risk Assessment), query `get_gene_associations` to retrieve all GWAS associations for patient's germline risk genes — genes with multiple independent GWAS associations across related traits contribute higher Genetic Risk scores. In Phase 3 (Disease-Specific Stratification), use `search_by_trait` to identify the full GWAS landscape for the patient's disease, and `get_variant_associations` to check whether specific patient variants have established population-level trait associations. Use `search_studies` to identify the largest ancestry-matched GWAS for polygenic risk score integration, informing the Genetic Risk component (0-35) of the Precision Medicine Risk Score.

---

## 9-Phase Stratification Pipeline

### Phase 1: Disease Disambiguation

```
1. mcp__opentargets__opentargets_info(method: "search_diseases", query: "patient_diagnosis")
   → Get EFO disease ID, confirm disease ontology placement

2. mcp__nlm__nlm_ct_codes(method: "icd-10-cm", query: "diagnosis")
   → Standardize to ICD-10-CM code

3. mcp__nlm__nlm_ct_codes(method: "conditions", query: "diagnosis")
   → Map to standardized condition name

4. mcp__hpo__hpo_data(method: "search_hpo_terms", query: "patient_phenotype", max: 10)
   → Standardize clinical features to HPO terms for phenotype characterization

5. mcp__opentargets__opentargets_info(method: "get_disease_details", id: "EFO_xxxxxxx")
   → Full disease profile: subtypes, phenotypes, known genetic associations

6. Route to disease-specific stratification protocol (see Disease-Specific Routing below)
```

### Phase 2: Germline Risk Assessment

```
1. mcp__nlm__nlm_ct_codes(method: "ncbi-genes", query: "GENE_SYMBOL")
   → Gene annotation, chromosomal location, known disease associations

2. mcp__opentargets__opentargets_info(method: "search_targets", query: "GENE_SYMBOL")
   → Get Ensembl gene ID

3. mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   → Gene function, pathways, protein class, tractability

4. mcp__opentargets__opentargets_info(method: "get_target_disease_associations", targetId: "ENSG00000xxxxx", diseaseId: "EFO_xxxxxxx", minScore: 0.1)
   → Genetic evidence strength (GWAS, Mendelian, somatic mutation data)

5. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_SYMBOL germline variant penetrance", num_results: 10)
   → Published penetrance and risk data

6. mcp__ensembl__ensembl_data(method: "lookup_gene", gene_id: "GENE_SYMBOL", species: "homo_sapiens", expand: true)
   → Gene coordinates, biotype, canonical transcript for variant mapping

7. mcp__ensembl__ensembl_data(method: "get_variant_consequences", variants: ["ENST00000xxxxx:c.XXX>Y"])
   → VEP consequence prediction for germline variants — impact, SIFT, PolyPhen
```

### Phase 3: Disease-Specific Stratification

```
Apply disease-category-specific scoring (see Disease-Specific Routing below):
- Extract relevant biomarkers, staging, histology, molecular subtypes
- Score clinical features per disease-specific rubric
- Assign partial Clinical Risk score (0-30)
```

### Phase 4: Pharmacogenomic Profiling

```
1. mcp__drugbank__drugbank_info(method: "search_by_target", target: "CYP2D6")
   → All drugs metabolized by CYP2D6

2. mcp__drugbank__drugbank_info(method: "search_by_target", target: "CYP2C19")
   → All drugs metabolized by CYP2C19

3. mcp__drugbank__drugbank_info(method: "search_by_target", target: "CYP3A4")
   → All drugs metabolized by CYP3A4

4. mcp__fda__fda_info(method: "get_drug_label", drug_name: "candidate_drug")
   → Check for PGx boxed warnings, dosing modifications by genotype

5. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "pharmacogenomics CYP2D6 metabolizer dosing", num_results: 10)
   → CPIC/DPWG guideline references

6. For chemotherapy patients:
   mcp__drugbank__drugbank_info(method: "search_by_target", target: "DPYD")
   mcp__drugbank__drugbank_info(method: "search_by_target", target: "UGT1A1")
   → Fluoropyrimidine and irinotecan toxicity risk

7. For immunotherapy/hypersensitivity:
   mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "HLA allele drug hypersensitivity screening", num_results: 10)
   → HLA-B*57:01 (abacavir), HLA-B*58:01 (allopurinol), HLA-A*31:01 (carbamazepine)
```

### Phase 5: Comorbidity Screening

```
1. mcp__nlm__nlm_ct_codes(method: "icd-10-cm", query: "comorbidity_name")
   → Standardize each comorbidity

2. mcp__fda__fda_info(method: "get_drug_interactions", drug_name: "current_medication")
   → Drug-drug interactions with planned treatment

3. mcp__drugbank__drugbank_info(method: "get_drug_interactions", drugbank_id: "DBxxxxx")
   → Comprehensive interaction check

4. mcp__fda__fda_info(method: "get_adverse_events", drug_name: "planned_drug", reaction: "comorbidity_related_AE")
   → Risk of exacerbating comorbid conditions
```

### Phase 6: Molecular Pathway Enrichment

```
1. mcp__opentargets__opentargets_info(method: "get_disease_targets_summary", diseaseId: "EFO_xxxxxxx", minScore: 0.5, size: 30)
   → Top molecular targets for the disease

2. mcp__drugbank__drugbank_info(method: "get_pathways", drugbank_id: "DBxxxxx")
   → Pathway mapping for candidate drugs

3. mcp__chembl__chembl_info(method: "get_mechanism", chembl_id: "CHEMBLxxxxx")
   → Mechanism of action for candidate compounds

4. mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   → Pathway involvement of patient's mutated genes

5. mcp__gtex__gtex_data(method: "search_genes", query: "GENE_SYMBOL")
   → Get GENCODE ID for GTEx tissue expression queries

6. mcp__gtex__gtex_data(method: "get_median_gene_expression", gencodeId: "ENSG00000xxxxx.xx")
   → Tissue expression profile of mutated gene — tissue-specific expression informs which organs are at risk and guides monitoring strategy

7. Identify actionable pathway nodes:
   mcp__chembl__chembl_info(method: "target_search", query: "pathway_target")
   mcp__chembl__chembl_info(method: "get_bioactivity", target_id: "CHEMBLxxxxx", limit: 20)
   → Available compounds for druggable pathway nodes
```

### Phase 7: Guidelines Mapping

```
1. mcp__pubmed__pubmed_articles(method: "search_advanced", term: "disease_name clinical practice guideline", journal: "", start_date: "2022-01-01", num_results: 10)
   → Current NCCN, ESMO, AHA, AAN guidelines

2. mcp__fda__fda_info(method: "get_approvals", drug_name: "recommended_drug")
   → FDA approval status and approved indications

3. mcp__fda__fda_info(method: "search_devices", query: "companion diagnostic disease_name")
   → FDA-approved companion diagnostics for biomarker testing

4. mcp__nlm__nlm_ct_codes(method: "hcpcs-LII", query: "genetic_test_name")
   → Billing codes for recommended genomic tests

5. mcp__nlm__nlm_ct_codes(method: "loinc-questions", query: "biomarker_name")
   → LOINC codes for laboratory tests in the guideline
```

### Phase 8: Clinical Trial Matching

```
1. mcp__ctgov__ctgov_info(method: "search_by_condition", condition: "disease_name", status: "RECRUITING", limit: 20)
   → Active trials for this condition

2. mcp__ctgov__ctgov_info(method: "search_by_intervention", intervention: "targeted_therapy_name", status: "RECRUITING", limit: 10)
   → Trials with molecularly matched interventions

3. mcp__ctgov__ctgov_info(method: "get_study_details", nct_id: "NCTxxxxxxxx")
   → Full eligibility criteria, endpoints, sites

4. mcp__ctgov__ctgov_info(method: "search_studies", query: "GENE_SYMBOL mutation basket trial", limit: 10)
   → Biomarker-driven basket/umbrella trials

5. Match patient profile against eligibility:
   - Molecular markers, prior therapies, performance status, organ function
   - Flag trials where patient's risk tier qualifies for escalated therapy arms
```

### Phase 9: Integrated Risk Score Computation

```
Aggregate scores from Phases 2-8 into the Precision Medicine Risk Score (see scoring framework below).
Generate tiered treatment recommendation based on final score.
Compile structured report with evidence citations and confidence levels.
```

---

## Precision Medicine Risk Score (0-100)

### Score Components

| Component | Weight | Sources | What it captures |
|-----------|--------|---------|-----------------|
| **Genetic Risk** | 0-35 | Open Targets, PubMed, NCBI Genes | Pathogenic variants, polygenic risk, germline burden |
| **Clinical Risk** | 0-30 | Disease-specific staging, comorbidities, biomarkers | Stage, grade, organ function, performance status |
| **Molecular Features** | 0-25 | ChEMBL, Open Targets, DrugBank | Actionable mutations, pathway activation, tumor mutational burden |
| **Pharmacogenomic Risk** | 0-10 | DrugBank, FDA labels, PubMed | Metabolizer status, HLA risk alleles, toxicity predictors |

### Genetic Risk Scoring (0-35)

```
Pathogenic germline variant in high-penetrance gene:     +15-25
  (BRCA1/2, TP53, APC, MLH1/MSH2, CFTR, HTT, etc.)
Moderate-penetrance variant (CHEK2, ATM, PALB2):         +8-14
Polygenic risk score in top 5% percentile:                +5-10
Family history with concordant genetics:                  +3-5
Pharmacogenomic high-risk allele (DPYD*2A, HLA-B*57:01): +2-5
No significant germline findings:                         +0
```

### Clinical Risk Scoring (0-30)

```
Advanced stage / high-grade disease:                      +10-15
Poor performance status (ECOG 2+):                        +5-8
Significant comorbidity burden (Charlson 3+):             +5-8
Adverse laboratory biomarkers:                            +3-5
Refractory to prior standard therapy:                     +5-8
Early stage / well-controlled:                            +0-3
```

### Molecular Features Scoring (0-25)

```
Actionable driver mutation with approved therapy:         +15-20
  (EGFR, ALK, BRAF V600E, HER2, BCR-ABL, etc.)
Actionable mutation with clinical trial options only:     +8-14
Elevated pathway activation (PI3K/mTOR, MAPK, Wnt):      +3-8
High tumor mutational burden / MSI-H:                     +5-10
No actionable molecular features:                         +0-2
```

### Pharmacogenomic Risk Scoring (0-10)

```
Poor/ultrarapid metabolizer for planned drug (CYP2D6/2C19): +4-6
HLA risk allele for planned therapy:                         +3-5
DPYD deficiency with fluoropyrimidine planned:               +5-8 (capped at 10)
UGT1A1*28 homozygous with irinotecan planned:               +3-5
Multiple PGx interactions:                                   +6-10
Normal metabolizer, no HLA risk:                             +0
```

---

## Risk Tiers and Treatment Recommendations

| Tier | Score | Clinical Meaning | Treatment Intensity |
|------|-------|-----------------|---------------------|
| **VERY HIGH** | 75-100 | High genetic burden + advanced disease + actionable targets + PGx risk | Aggressive targeted therapy; clinical trial enrollment strongly recommended; PGx-guided dosing mandatory; multidisciplinary tumor board review; consider combination regimens |
| **HIGH** | 50-74 | Significant risk factors with some actionable features | Targeted therapy if available; intensified monitoring; PGx testing before prescribing; clinical trial screening; specialist referral |
| **INTERMEDIATE** | 25-49 | Moderate risk, limited actionable targets | Standard-of-care per guidelines; elective PGx testing; surveillance schedule per stage; clinical trial optional |
| **LOW** | 0-24 | Low genetic burden, early/stable disease, no PGx flags | Standard-of-care; routine monitoring; prevention focus; lifestyle modification; screening per guidelines |

---

## Disease-Specific Routing

### CANCER

#### Breast Cancer

```
Key genes: BRCA1, BRCA2, PALB2, CHEK2, ATM, TP53, PIK3CA, ESR1, ERBB2
Molecular subtypes: Luminal A, Luminal B, HER2+, Triple-negative (TNBC)
Biomarkers: ER/PR/HER2 status, Ki-67, Oncotype DX score, TMB, PD-L1

1. mcp__opentargets__opentargets_info(method: "search_diseases", query: "breast carcinoma")
2. mcp__nlm__nlm_ct_codes(method: "ncbi-genes", query: "BRCA1")
3. mcp__chembl__chembl_info(method: "drug_search", query: "breast cancer", limit: 30)
4. mcp__fda__fda_info(method: "search_devices", query: "companion diagnostic breast cancer")
5. mcp__ctgov__ctgov_info(method: "search_by_condition", condition: "triple negative breast cancer", status: "RECRUITING")

Stratification: TNBC + BRCA1/2 → PARP inhibitor eligible (olaparib, talazoparib)
                HER2+ → trastuzumab/pertuzumab ± T-DXd
                PIK3CA mutant → alpelisib + fulvestrant
                High Oncotype DX → chemotherapy benefit
```

#### Lung Cancer (NSCLC)

```
Key genes: EGFR, ALK, ROS1, BRAF, KRAS G12C, MET, RET, NTRK, HER2
Biomarkers: PD-L1 TPS, TMB, driver mutation status

1. mcp__opentargets__opentargets_info(method: "search_diseases", query: "non-small cell lung carcinoma")
2. mcp__chembl__chembl_info(method: "target_search", query: "EGFR")
3. mcp__fda__fda_info(method: "get_approvals", drug_name: "osimertinib")
4. mcp__ctgov__ctgov_info(method: "search_studies", query: "KRAS G12C NSCLC", limit: 15)

Stratification: EGFR mut → osimertinib (1L); ALK+ → alectinib/lorlatinib
                KRAS G12C → sotorasib/adagrasib
                PD-L1 >= 50% no driver → pembrolizumab monotherapy
                No driver, PD-L1 < 50% → chemo-IO combination
```

#### Colorectal Cancer

```
Key genes: APC, KRAS, NRAS, BRAF V600E, MLH1, MSH2, MSH6, PMS2, PIK3CA
Biomarkers: MSI/MMR status, RAS/BRAF mutation, HER2 amplification, DPYD status

1. mcp__opentargets__opentargets_info(method: "search_diseases", query: "colorectal carcinoma")
2. mcp__drugbank__drugbank_info(method: "search_by_target", target: "DPYD")
3. mcp__fda__fda_info(method: "get_drug_label", drug_name: "fluorouracil")

Stratification: MSI-H/dMMR → checkpoint inhibitor (pembrolizumab 1L)
                BRAF V600E → encorafenib + cetuximab
                RAS wild-type → anti-EGFR eligible
                DPYD deficient → fluoropyrimidine contraindicated or dose-reduced
```

#### Melanoma

```
Key genes: BRAF, NRAS, KIT, NF1, CDKN2A
Biomarkers: BRAF V600 status, TMB, PD-L1, LDH

Stratification: BRAF V600E/K → dabrafenib + trametinib or encorafenib + binimetinib
                BRAF wild-type → nivolumab + ipilimumab or anti-PD-1 monotherapy
                KIT mutant (mucosal/acral) → imatinib
```

### METABOLIC

#### Type 2 Diabetes (T2D)

```
Key genes: TCF7L2, KCNJ11, PPARG, SLC30A8, HNF1A, GCK
Biomarkers: HbA1c, fasting glucose, C-peptide, GAD antibodies, BMI

1. mcp__opentargets__opentargets_info(method: "search_diseases", query: "type 2 diabetes mellitus")
2. mcp__drugbank__drugbank_info(method: "search_by_category", category: "antidiabetic", limit: 30)
3. mcp__chembl__chembl_info(method: "target_search", query: "GLP-1 receptor")

Stratification: HNF1A/GCK variant → MODY, sulfonylurea responsive
                Severe insulin resistance phenotype → thiazolidinedione/GLP-1
                High cardiovascular risk → SGLT2i or GLP-1 RA preferred
                CYP2C9 poor metabolizer → sulfonylurea dose reduction
```

#### Obesity

```
Key genes: MC4R, LEP, LEPR, POMC, PCSK1, FTO
Biomarkers: BMI, waist circumference, leptin, insulin resistance markers

Stratification: MC4R deficiency → setmelanotide eligible
                Monogenic obesity gene → targeted therapy evaluation
                Polygenic obesity → GLP-1 RA (semaglutide, tirzepatide)
```

#### NAFLD/NASH

```
Key genes: PNPLA3, TM6SF2, HSD17B13, MBOAT7
Biomarkers: ALT, AST, FIB-4, NAFLD fibrosis score, liver stiffness

Stratification: PNPLA3 I148M homozygous → accelerated fibrosis risk
                Advanced fibrosis (F3-F4) → clinical trial priority
                HSD17B13 loss-of-function → reduced risk (protective)
```

### CARDIOVASCULAR

#### Coronary Artery Disease (CAD)

```
Key genes: LDLR, PCSK9, APOB, LPA, 9p21 locus
Biomarkers: LDL-C, Lp(a), coronary calcium score, hsCRP, polygenic risk score

1. mcp__opentargets__opentargets_info(method: "search_diseases", query: "coronary artery disease")
2. mcp__drugbank__drugbank_info(method: "search_by_target", target: "PCSK9")
3. mcp__chembl__chembl_info(method: "drug_search", query: "PCSK9 inhibitor", limit: 10)

Stratification: Familial hypercholesterolemia (LDLR/APOB/PCSK9) → PCSK9i + high-intensity statin
                Elevated Lp(a) → emerging Lp(a)-lowering trials
                CYP2C19 poor metabolizer → clopidogrel resistance, use ticagrelor/prasugrel
                Statin myopathy risk (SLCO1B1*5) → dose adjustment or alternative
```

#### Heart Failure

```
Key genes: TTN, LMNA, MYH7, MYBPC3, SCN5A, BAG3
Biomarkers: BNP/NT-proBNP, LVEF, LGE on cardiac MRI

Stratification: LMNA pathogenic variant → high arrhythmia risk, early ICD consideration
                TTN truncation → dilated cardiomyopathy, better prognosis vs LMNA
                Sarcomeric (MYH7/MYBPC3) → HCM phenotype, mavacamten eligible
```

#### Atrial Fibrillation (AFib)

```
Key genes: PITX2, KCNQ1, SCN5A, KCNA5
Biomarkers: CHA2DS2-VASc score, LA diameter

Stratification: CYP2C9/VKORC1 variants → warfarin dose adjustment
                CYP3A4 interaction risk → DOAC selection (apixaban vs rivaroxaban)
                High CHA2DS2-VASc → anticoagulation mandatory
```

### NEUROLOGICAL

#### Alzheimer's Disease

```
Key genes: APP, PSEN1, PSEN2, APOE (e4 allele), TREM2, SORL1
Biomarkers: Amyloid PET, CSF A-beta42/tau ratio, plasma p-tau217

1. mcp__opentargets__opentargets_info(method: "search_diseases", query: "Alzheimer disease")
2. mcp__drugbank__drugbank_info(method: "search_by_category", category: "anti-Alzheimer", limit: 20)
3. mcp__ctgov__ctgov_info(method: "search_by_condition", condition: "Alzheimer disease", status: "RECRUITING")

Stratification: APOE e4/e4 → highest amyloid risk, ARIA monitoring with anti-amyloid Abs
                PSEN1/2 or APP → autosomal dominant, DIAN-TU trial eligible
                APOE e4 carrier → lecanemab/donanemab with enhanced MRI monitoring
                TREM2 variant → microglial dysfunction phenotype
```

#### Parkinson's Disease

```
Key genes: LRRK2, GBA1, SNCA, PARK2 (Parkin), PINK1
Biomarkers: DAT-SPECT, alpha-synuclein seed amplification assay

Stratification: GBA1 variant → faster progression, ambroxol trial eligible
                LRRK2 G2019S → kinase inhibitor trials (DNL201, BIIB122)
                Young onset + Parkin/PINK1 → mitochondrial phenotype
```

### RARE / MONOGENIC

#### Marfan Syndrome

```
Key gene: FBN1
Biomarkers: Aortic root diameter, ectopia lentis, systemic score

1. mcp__nlm__nlm_ct_codes(method: "ncbi-genes", query: "FBN1")
2. mcp__nlm__nlm_ct_codes(method: "hpo-vocabulary", query: "aortic root dilatation")
3. mcp__opentargets__opentargets_info(method: "get_target_disease_associations", targetId: "ENSG00000166147", diseaseId: "Orphanet_558")

Stratification: FBN1 pathogenic variant + aortic root > 45mm → surgical threshold
                Losartan/atenolol per aortic growth rate
                Ghent criteria scoring for diagnosis confirmation
```

#### Cystic Fibrosis

```
Key gene: CFTR
Biomarkers: Sweat chloride, FEV1, CFTR genotype

Stratification: F508del homozygous → elexacaftor/tezacaftor/ivacaftor (Trikafta)
                G551D and other gating mutations → ivacaftor
                Nonsense mutations → investigational readthrough agents
                Residual function mutations → CFTR modulator responsive
```

#### Sickle Cell Disease

```
Key gene: HBB (E6V mutation)
Biomarkers: HbS percentage, HbF level, reticulocyte count, LDH

Stratification: HbSS with severe phenotype → gene therapy (lovotibeglogene, exagamglogene)
                Hydroxyurea responsive (HbF induction) → standard of care
                Recurrent VOC → crizanlizumab, voxelotor
                Eligible for stem cell transplant → matched donor screening
```

### AUTOIMMUNE

#### Rheumatoid Arthritis (RA)

```
Key genes: HLA-DRB1 (shared epitope), PTPN22, CTLA4, STAT4
Biomarkers: RF, anti-CCP, ESR, CRP, DAS28 score

1. mcp__opentargets__opentargets_info(method: "search_diseases", query: "rheumatoid arthritis")
2. mcp__drugbank__drugbank_info(method: "search_by_category", category: "antirheumatic", limit: 20)
3. mcp__chembl__chembl_info(method: "target_search", query: "JAK1")

Stratification: Anti-CCP+ / shared epitope → aggressive disease, early biologic
                TPMT/NUDT15 status → methotrexate/azathioprine dosing
                JAK inhibitor candidate → tofacitinib/upadacitinib (VTE risk assessment)
                High DAS28 refractory → biologic switch algorithm
```

#### Systemic Lupus Erythematosus (Lupus)

```
Key genes: HLA-DR2/DR3, TREX1, C1Q, C2, C4, STAT4, IRF5
Biomarkers: ANA, anti-dsDNA, complement C3/C4, SLEDAI score

Stratification: Lupus nephritis → belimumab + standard, voclosporin
                Type I IFN high → anifrolumab
                C1Q/C2/C4 deficiency → complement-mediated, early aggressive treatment
                CYP2D6 status → hydroxychloroquine toxicity risk
```

#### Multiple Sclerosis (MS)

```
Key genes: HLA-DRB1*15:01, IL7R, IL2RA
Biomarkers: OCB, MRI lesion burden, NfL, EDSS score

Stratification: Highly active RRMS → natalizumab (JCV risk stratification), ocrelizumab
                JCV antibody positive → avoid natalizumab or monitor closely
                HLA-A*02:01 → may influence disease course
                CYP1A2 status → teriflunomide metabolism
```

---

## Pharmacogenomic Integration Framework

### CYP Metabolizer Status Impact

| Gene | Key Drugs Affected | Poor Metabolizer Action | Ultrarapid Metabolizer Action |
|------|-------------------|------------------------|------------------------------|
| **CYP2D6** | Tamoxifen, codeine, tramadol, venlafaxine, atomoxetine | Switch drug or increase dose | Reduce dose or switch (codeine → toxicity risk) |
| **CYP2C19** | Clopidogrel, PPIs, voriconazole, escitalopram | Clopidogrel → switch to ticagrelor; PPI → no change | PPI → increase dose; voriconazole → increase dose |
| **CYP3A4** | Tacrolimus, cyclosporine, statins, DOACs | Reduce dose, monitor levels | Increase dose, monitor efficacy |
| **CYP2C9** | Warfarin, phenytoin, sulfonylureas, NSAIDs | Reduce dose significantly | Standard dosing usually adequate |

### HLA Allele Screening

| HLA Allele | Drug | Reaction | Action |
|------------|------|----------|--------|
| **HLA-B*57:01** | Abacavir | Hypersensitivity syndrome | Mandatory pre-test; contraindicated if positive |
| **HLA-B*58:01** | Allopurinol | SJS/TEN | Pre-test recommended; use febuxostat if positive |
| **HLA-A*31:01** | Carbamazepine | SJS/TEN/DRESS | Pre-test recommended |
| **HLA-B*15:02** | Carbamazepine, phenytoin | SJS/TEN | Mandatory in Southeast Asian ancestry |
| **HLA-B*13:01** | Dapsone | Hypersensitivity | Pre-test recommended |

### Chemotherapy Toxicity Genes

| Gene | Drug | Risk | Action |
|------|------|------|--------|
| **DPYD** (*2A, *13, D949V) | 5-FU, capecitabine | Severe/fatal toxicity | Mandatory pre-test; dose reduce 50% (het) or contraindicate (hom) |
| **UGT1A1** (*28) | Irinotecan | Severe neutropenia/diarrhea | Dose reduce if *28/*28 homozygous |
| **TPMT / NUDT15** | 6-MP, azathioprine | Severe myelosuppression | Dose reduce or switch per genotype |
| **CYP2D6** | Tamoxifen | Reduced efficacy (poor metabolizer) | Switch to aromatase inhibitor if post-menopausal |

---

## Integrated Report Template

```
PRECISION MEDICINE STRATIFICATION REPORT
=========================================

PATIENT: [ID]    DATE: [Date]    DISEASE: [Primary Diagnosis]
ICD-10: [Code]   DISEASE CATEGORY: [CANCER/METABOLIC/CV/NEURO/RARE/AUTOIMMUNE]

1. DISEASE DISAMBIGUATION
   Diagnosis: [Confirmed diagnosis with ontology mapping]
   Subtype: [Molecular/clinical subtype]
   Stage/Severity: [Disease-specific staging]

2. PRECISION MEDICINE RISK SCORE: [XX]/100 — [TIER]
   Genetic Risk:        [XX]/35
   Clinical Risk:       [XX]/30
   Molecular Features:  [XX]/25
   Pharmacogenomic:     [XX]/10

3. KEY FINDINGS
   Germline:    [Pathogenic variants identified]
   Somatic:     [Actionable mutations if applicable]
   PGx:         [Metabolizer status, HLA alleles]
   Pathways:    [Activated/disrupted pathways]

4. TREATMENT RECOMMENDATIONS (Tier-Based)
   First-line:  [Guideline-concordant ± targeted therapy]
   PGx Adjustments: [Dose modifications per genotype]
   Clinical Trials: [Matched NCT IDs with eligibility summary]
   Monitoring:  [Biomarker surveillance schedule]

5. COMORBIDITY INTERACTIONS
   [Drug-drug interactions, organ function considerations]

6. EVIDENCE SUMMARY
   [Key PubMed citations, guideline references, evidence levels]

7. CLINICAL TRIAL MATCHES
   [NCT ID] — [Title] — [Phase] — [Status] — [Match rationale]
```

---

## Multi-Agent Workflow Examples

**"Stratify a BRCA1+ triple-negative breast cancer patient for treatment"**
1. Precision Medicine Stratifier → Full 9-phase pipeline: germline risk (BRCA1), disease routing (TNBC), PGx profiling (DPYD if chemo planned), risk score computation, trial matching
2. Cancer Variant Interpreter → Detailed BRCA1 variant pathogenicity, co-occurring somatic mutations
3. Precision Oncology Advisor → Treatment sequencing (PARP inhibitor vs chemo-IO), combination strategies
4. Immunotherapy Response Predictor → PD-L1, TMB, immune infiltrate assessment for IO eligibility

**"Evaluate a Parkinson's patient with GBA1 variant for precision therapy"**
1. Precision Medicine Stratifier → Germline risk (GBA1), disease routing (neurological), metabolizer profiling (CYP2D6 for MAO-B inhibitors), trial matching
2. Rare Disease Diagnosis → GBA1 variant classification, Gaucher disease spectrum assessment
3. Pharmacogenomics Specialist → Deep CYP2D6 analysis for levodopa adjuncts, ambroxol metabolism
4. Clinical Decision Support → Guideline-concordant Parkinson's management with genetic modifiers

**"Risk-stratify a type 2 diabetes patient with cardiovascular comorbidity"**
1. Precision Medicine Stratifier → Disease routing (metabolic + CV), polygenic risk assessment, PGx for metformin/sulfonylureas/statins, comorbidity interaction check
2. Clinical Decision Support → ADA/EASD guideline mapping, cardiovascular outcome trial evidence
3. Pharmacogenomics Specialist → CYP2C9 (sulfonylureas), SLCO1B1 (statins), OATP1B1 (metformin transport)

**"Assess a patient with familial hypercholesterolemia and statin intolerance"**
1. Precision Medicine Stratifier → Germline risk (LDLR/APOB/PCSK9 variant), CV disease routing, PGx (SLCO1B1*5 for statin myopathy), Lp(a) assessment, PCSK9i eligibility
2. Rare Disease Diagnosis → FH variant pathogenicity, cascade screening recommendations
3. Clinical Decision Support → ESC/EAS lipid guideline targets, PCSK9i + ezetimibe combination evidence

**"Stratify a lupus nephritis patient failing standard therapy"**
1. Precision Medicine Stratifier → Disease routing (autoimmune), HLA typing, complement genetics, PGx (CYP2D6 for hydroxychloroquine, TPMT for azathioprine), risk scoring, trial matching
2. Immunotherapy Response Predictor → Type I IFN signature for anifrolumab eligibility
3. Pharmacogenomics Specialist → Mycophenolate metabolism (UGT enzymes), tacrolimus (CYP3A5)
4. Clinical Decision Support → ACR/EULAR lupus nephritis guidelines, voclosporin evidence

## Completeness Checklist

- [ ] Disease disambiguated with EFO ID and ICD-10 code mapped
- [ ] Germline risk assessment completed with variant pathogenicity classified
- [ ] Disease-specific stratification protocol applied from routing table
- [ ] Pharmacogenomic profiling performed (CYP2D6, CYP2C19, HLA alleles, DPYD if applicable)
- [ ] Comorbidity screening and drug-drug interaction check completed
- [ ] Molecular pathway enrichment analyzed with actionable nodes identified
- [ ] Clinical guidelines mapped and FDA approval status confirmed
- [ ] Clinical trial matching performed with eligibility assessment
- [ ] Precision Medicine Risk Score computed (0-100) with component breakdown
- [ ] Report file verified with no remaining `[Analyzing...]` placeholders
