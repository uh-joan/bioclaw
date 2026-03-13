---
name: biomarker-discovery
description: "Biomarker identification and validation, FDA BEST categories, ROC/AUC analysis, companion diagnostics, validation ladder, clinical utility assessment"
---

# Biomarker Discovery and Validation Specialist

Identifies, characterizes, and validates biomarkers across the full translational spectrum -- from omics-driven discovery through analytical and clinical validation to regulatory qualification and clinical utility demonstration. Applies the FDA Biomarkers, EndpointS, and other Tools (BEST) framework to classify biomarkers by intended use. Integrates multi-omics data (genomics, transcriptomics, proteomics, metabolomics), clinical trial evidence, FDA labeling, tissue expression patterns, and pathway biology to produce actionable biomarker assessment reports with readiness scoring, ROC/AUC performance metrics, and companion diagnostic feasibility analysis.

> **ML panel recipes**: See [ml-panel-recipes.md](ml-panel-recipes.md) for machine learning biomarker panel selection code templates (mutual information, LASSO, random forest importance, cross-validated AUC, mutation sensitivity, resistance profiling, lineage enrichment, elastic net, panel size optimization, biomarker readiness scoring, survival association, multi-omics integration).

## Report-First Workflow

1. **Create report file immediately**: `[biomarker]_discovery_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Differential gene expression analysis from RNA-seq data -> use `rnaseq-deseq2`
- Single-cell transcriptomics and cell-type deconvolution -> use `single-cell-analysis`
- Mass spectrometry proteomics and protein quantification -> use `proteomics-analysis`
- Multi-omics data integration across platforms -> use `multi-omics-integration`
- GWAS-based trait-to-gene mapping -> use `gwas-trait-to-gene` or `gwas-snp-interpretation`
- Clinical trial protocol design for biomarker-driven studies -> use `clinical-trial-protocol-designer`

## Cross-Reference: Other Skills

- **Drug mechanism, pharmacology, and compound profiles** -> use drug-research skill
- **PK/PD modeling, dose-response, and therapeutic windows** -> use clinical-pharmacology skill
- **Differential gene expression from RNA-seq experiments** -> use rnaseq-deseq2 skill
- **Single-cell transcriptomics and cell-type deconvolution** -> use single-cell-analysis skill
- **Mass spectrometry proteomics and protein quantification** -> use proteomics-analysis skill
- **Cell-type-specific expression validation (CELLxGENE)** -> use cell-type-expression skill

## Available MCP Tools

### `mcp__pubmed__pubmed_data` (Biomarker Literature)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search` | Search PubMed for biomarker publications by keyword, MeSH terms, or structured queries | `query`, `num_results`, `sort_order` |
| `fetch_details` | Retrieve full article metadata including abstract, authors, journal, MeSH headings, and publication type | `pmid` |

### `mcp__clinicaltrials__ct_data` (Biomarker Validation Studies)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_studies` | Search ClinicalTrials.gov for biomarker validation trials, companion diagnostic studies, or enrichment designs | `query`, `status`, `phase`, `limit` |
| `get_study` | Retrieve full trial record including biomarker eligibility criteria, endpoints, and results | `nct_id` |

### `mcp__fda__fda_data` (Approved Companion Dx & Biomarker-Based Labels)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_drugs` | Search FDA drug database for biomarker-linked approvals | `query`, `limit` |
| `get_drug_label` | Full prescribing information including companion diagnostic requirements, biomarker-defined indications, and pharmacogenomic sections | `set_id` or `drug_name` |

### `mcp__opentargets__ot_data` (Target-Disease Associations)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_target` | Search targets by gene symbol or protein name to obtain Ensembl gene IDs | `query`, `size` |
| `get_target_info` | Full target profile including function, pathways, tractability, and known drug modalities | `id` (Ensembl ID) |
| `get_associations` | Evidence-scored target-disease association data across genetic, somatic, literature, and pathway evidence types | `targetId`, `diseaseId`, `minScore`, `size` |

### `mcp__gtex__gtex_data` (Tissue Expression Patterns)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_gene_expression` | Gene expression data across GTEx tissues with sample-level detail | `gene_id`, `tissue` |
| `get_median_gene_expression` | Median TPM expression across all GTEx tissues for tissue-specificity profiling | `gene_id` |
| `search_genes` | Search GTEx gene annotations by symbol or name | `query`, `limit` |

### `mcp__ensembl__ensembl_data` (Genomic Context)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_gene_info` | Full gene annotation including coordinates, biotype, description, and cross-references | `gene_id` |
| `get_variants` | Known genetic variants in a gene region including clinical significance annotations | `gene_id`, `consequence_type` |
| `get_gene_by_symbol` | Resolve gene symbol to Ensembl ID with species-specific lookup | `symbol`, `species` |

### `mcp__uniprot__uniprot_data` (Protein Biomarkers)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_proteins` | Search UniProt for proteins by name, gene, organism, or keyword | `query`, `limit`, `organism` |
| `get_protein` | Full protein record including function, subcellular location, post-translational modifications, and disease associations | `accession` |
| `get_protein_features` | Protein feature annotations: domains, active sites, binding sites, signal peptides, glycosylation sites | `accession` |

### `mcp__kegg__kegg_data` (Pathway Biomarkers)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_pathway` | Full KEGG pathway details including genes, compounds, and disease links | `pathway_id` |
| `find_pathway` | Search KEGG pathways by keyword to identify biomarker-relevant signaling cascades | `query` |
| `get_genes_in_pathway` | List all genes in a KEGG pathway for pathway-based biomarker panel construction | `pathway_id` |

### `mcp__geneontology__go_data` (Functional Annotation)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_go_terms` | Search Gene Ontology for biological process, molecular function, or cellular component terms | `query`, `limit`, `aspect` |
| `get_go_term` | Retrieve full GO term definition, relationships, and annotated gene products | `go_id` |

### `mcp__hpo__hpo_data` (Phenotype-Biomarker Links)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_hpo_terms` | Search Human Phenotype Ontology for clinical phenotypes linked to biomarker abnormalities | `query`, `limit` |
| `get_hpo_term` | Full HPO term details including disease associations, frequency, and inheritance patterns | `hpo_id` |

### DepMap — Cancer Dependency Map

| Tool | Method | Use |
|------|--------|-----|
| `mcp__depmap__depmap_data` | `get_biomarker_analysis` | Functional biomarker discovery -- test if mutation predicts gene dependency |
| | `get_gene_dependency` | Dependency as a functional readout for biomarker validation |
| | `get_drug_sensitivity` | Drug response biomarkers -- mutation-sensitivity correlations |
| | `get_gene_expression` | Expression biomarkers across cancer cell lines |
| | `get_mutations` | Mutation landscape for biomarker candidate genes |

### `mcp__cbioportal__cbioportal_data` (Cancer Biomarker Prevalence)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_mutation_frequency` | Biomarker prevalence in cancer — mutation frequency across TCGA/MSK-IMPACT cohorts | `study_id`, `gene`, `profile_id` |
| `search_studies` | Find validation cohorts for cancer biomarkers across curated datasets | `keyword`, `cancer_type` |
| `get_mutations` | Mutation-outcome associations — detailed variant data for biomarker candidates | `study_id`, `gene`, `sample_id` |

**cBioPortal workflow:** Use cBioPortal to assess cancer biomarker prevalence and find validation cohorts across TCGA/MSK-IMPACT. Query mutation frequencies to determine how common a candidate biomarker alteration is in a given cancer type, identify independent cohorts for cross-validation, and retrieve mutation-level data to analyze biomarker-outcome associations.

```
mcp__cbioportal__cbioportal_data(method: "search_studies", cancer_type: "lung")
mcp__cbioportal__cbioportal_data(method: "get_mutation_frequency", study_id: "luad_tcga", gene: "EGFR")
mcp__cbioportal__cbioportal_data(method: "get_mutations", study_id: "msk_impact_2017", gene: "KRAS")
```

### `mcp__geo__geo_data` (GEO Public Datasets)

| Tool | Method | Use |
|------|--------|-----|
| `mcp__geo__geo_data` | `search_datasets` | Find expression datasets for biomarker validation |
| | `search_by_gene` | Find gene expression across studies |
| | `get_dataset_summary` | Get dataset details for validation cohort selection |

**GEO workflow:** Search GEO for independent expression datasets to validate biomarker candidates across cohorts.

```
mcp__geo__geo_data(method: "search_datasets", query: "DISEASE biomarker expression profiling")
mcp__geo__geo_data(method: "search_by_gene", gene: "BIOMARKER_GENE")
mcp__geo__geo_data(method: "get_dataset_summary", dataset_id: "GDSxxxxxx")
```

### `mcp__hmdb__hmdb_data` (Metabolite Biomarker Validation)

Use HMDB to validate metabolite biomarker candidates by retrieving disease associations, normal/abnormal concentration ranges across biofluids, and pathway context. Essential for assessing metabolite biomarker clinical utility and establishing reference intervals. Note: HMDB uses Cloudflare protection so some requests may be blocked intermittently.

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_metabolite` | Comprehensive metabolite data (name, formula, SMILES, InChI, description, biofluid/tissue locations, pathways, diseases) | `hmdb_id` (required) |
| `search_metabolites` | Search metabolites by name/keyword | `query` (required), `limit` (optional, default 25) |
| `get_metabolite_diseases` | Disease associations with OMIM IDs and references | `hmdb_id` (required) |
| `get_metabolite_concentrations` | Normal and abnormal concentration data across biofluids | `hmdb_id` (required) |
| `get_metabolite_pathways` | Biological pathways, biofluid locations, tissue locations, cellular locations | `hmdb_id` (required) |
| `search_by_mass` | Find metabolites by molecular weight in Daltons | `mass` (required), `tolerance` (optional, default 0.05), `limit` (optional, default 25) |

---

## Core Workflow 1: Biomarker Discovery Pipeline

A structured five-stage pipeline from omics screening through clinical utility demonstration. Each stage gates progression to the next.

### Stage 1: Omics Screening and Candidate Identification

```
1. mcp__pubmed__pubmed_data(method: "search", query: "DISEASE biomarker discovery omics profiling", num_results: 20)
   -> Landscape of published biomarker discovery efforts for the disease

2. mcp__opentargets__ot_data(method: "search_target", query: "CANDIDATE_GENE")
   -> Resolve gene identity, get Ensembl ID

3. mcp__opentargets__ot_data(method: "get_associations", targetId: "ENSG00000xxxxx", diseaseId: "EFO_xxxxxxx")
   -> Genetic, somatic mutation, literature, and pathway evidence linking target to disease

4. mcp__gtex__gtex_data(method: "get_median_gene_expression", gene_id: "ENSG00000xxxxx")
   -> Tissue expression profile: is the candidate expressed in relevant tissue?
   -> Flag tissue-restricted vs ubiquitous expression (specificity assessment)

5. mcp__kegg__kegg_data(method: "find_pathway", query: "DISEASE_PATHWAY")
   -> Identify pathway context; prioritize candidates in dysregulated pathways

6. mcp__geneontology__go_data(method: "search_go_terms", query: "BIOLOGICAL_PROCESS_OF_INTEREST")
   -> Functional annotation to confirm biological plausibility

Candidate prioritization criteria:
- Fold-change magnitude (>2-fold for transcriptomic, >1.5-fold for proteomic)
- Statistical significance (FDR <0.05 in discovery, <0.01 for validation)
- Biological plausibility (pathway involvement, known disease association)
- Measurability (protein secreted into accessible biofluid preferred)
- Prior literature support (PubMed evidence count)
```

### Stage 2: Candidate Selection and Characterization

```
1. mcp__uniprot__uniprot_data(method: "get_protein", accession: "UNIPROT_ID")
   -> Protein function, subcellular location, secretion status, isoforms
   -> KEY: Secreted proteins are preferred serum/plasma biomarkers

2. mcp__uniprot__uniprot_data(method: "get_protein_features", accession: "UNIPROT_ID")
   -> Domain architecture, PTMs, epitopes for immunoassay development

3. mcp__ensembl__ensembl_data(method: "get_gene_info", gene_id: "ENSG00000xxxxx")
   -> Genomic context, transcript variants, regulatory regions

4. mcp__ensembl__ensembl_data(method: "get_variants", gene_id: "ENSG00000xxxxx")
   -> Known variants that may affect biomarker measurement or interpretation

5. mcp__hpo__hpo_data(method: "search_hpo_terms", query: "CLINICAL_PHENOTYPE")
   -> Link candidate biomarker to observable clinical phenotypes

6. mcp__gtex__gtex_data(method: "get_gene_expression", gene_id: "ENSG00000xxxxx", tissue: "TARGET_TISSUE")
   -> Expression level and variability in disease-relevant tissue

Selection criteria for advancement:
- Detectable in accessible specimen (blood, urine, saliva, tissue)
- Commercially available or developable immunoassay/PCR assay
- Dynamic range sufficient to discriminate disease from healthy
- Minimal confounding by age, sex, BMI, medications
- Patent freedom-to-operate assessment
```

### Stage 3: Analytical Validation

```
Analytical validation establishes that the assay reliably measures the biomarker.

Key parameters to assess:
- Limit of Detection (LOD): lowest concentration reliably distinguished from blank
  Determined by measuring blank samples (n>=20) and calculating mean + 2-3 SD
- Limit of Quantification (LOQ): lowest concentration with acceptable precision (CV <20%)
  Typically 3-10x the LOD depending on assay type
- Linearity: range over which measurement is proportional to concentration
- Precision: within-run (repeatability) and between-run (reproducibility) CV
- Accuracy: recovery in spike-and-dilution experiments (target: 80-120% recovery)
- Specificity: interference from hemolysis, lipemia, bilirubin, common medications
- Stability: specimen stability (freeze-thaw cycles, room temperature, long-term storage)

1. mcp__pubmed__pubmed_data(method: "search", query: "BIOMARKER_NAME assay validation analytical performance LOD precision", num_results: 15)
   -> Published analytical validation data for existing assays

2. mcp__fda__fda_data(method: "search_drugs", query: "BIOMARKER_NAME diagnostic")
   -> Check if FDA-cleared assays already exist for this biomarker

CLIA/CAP validation requirements:
- Precision study: minimum 20 runs over 20 days (CLSI EP05-A3)
- Method comparison: minimum 40 patient samples across the measurement range (CLSI EP09-A3)
- Reference interval: minimum 120 healthy individuals per partition (CLSI EP28-A3c)
- Linearity verification: minimum 5 concentrations spanning the reportable range (CLSI EP06-A)
- Interference testing: per CLSI EP07-A3 with hemolysis, lipemia, icterus, and common drugs
- Carryover assessment: high-low-low sequence to detect sample-to-sample contamination
```

### Stage 4: Clinical Validation

```
Clinical validation establishes the biomarker's ability to detect or predict the clinical condition.

1. mcp__clinicaltrials__ct_data(method: "search_studies", query: "BIOMARKER_NAME validation diagnostic", limit: 20)
   -> Existing or ongoing clinical validation studies

2. mcp__pubmed__pubmed_data(method: "search", query: "BIOMARKER_NAME sensitivity specificity ROC clinical validation", num_results: 20)
   -> Published clinical performance data

Performance metrics to extract or calculate:
- Sensitivity (true positive rate): TP / (TP + FN)
- Specificity (true negative rate): TN / (TN + FP)
- Positive Predictive Value (PPV): TP / (TP + FP) -- prevalence-dependent
- Negative Predictive Value (NPV): TN / (TN + FN) -- prevalence-dependent
- Area Under the ROC Curve (AUC) with 95% confidence interval
- Likelihood ratios: LR+ = sensitivity / (1 - specificity), LR- = (1 - sensitivity) / specificity
- Diagnostic Odds Ratio: (TP * TN) / (FP * FN)
- Optimal cutpoint (Youden's J index or clinical decision threshold)

Study design requirements:
- Case-control studies: minimum for initial clinical validation
- Cross-sectional studies: prevalence estimation, PPV/NPV calculation
- Prospective cohort studies: gold standard for clinical validity
- Minimum sample size: 100 cases + 100 controls for adequate precision of AUC estimate
- STARD checklist compliance for diagnostic accuracy reporting
```

### Stage 5: Clinical Utility Demonstration

```
Clinical utility proves that using the biomarker improves patient outcomes.

1. mcp__clinicaltrials__ct_data(method: "search_studies", query: "BIOMARKER_NAME guided therapy randomized", limit: 15)
   -> Prospective-retrospective or randomized biomarker-strategy trials

2. mcp__pubmed__pubmed_data(method: "search", query: "BIOMARKER_NAME clinical utility outcome improvement decision impact", num_results: 15)
   -> Published clinical utility evidence

Study designs for utility demonstration:
- Biomarker-strategy design: randomize to biomarker-guided vs standard-of-care
- Enrichment design: select patients based on biomarker, compare to unselected population
- Prospective-retrospective: use archived specimens from completed RCT (Simon et al. 2009)
- Decision impact study: measure change in clinical decisions when biomarker result is provided
- Marker-based strategy trial: all patients tested, randomized to marker-guided vs empiric treatment

Utility evidence hierarchy (strongest to weakest):
1. Prospective RCT with biomarker-strategy design
2. Prospective-retrospective analysis of archived RCT specimens
3. Prospective observational study with pre-defined biomarker cutpoint
4. Retrospective study with independent validation cohort
5. Decision impact or modeling study

Health economic considerations:
- Cost per quality-adjusted life year (QALY) gained
- Incremental cost-effectiveness ratio (ICER) vs standard of care
- Budget impact analysis for payer adoption
- Number needed to test (NNTest) to prevent one adverse outcome
```

---

## Core Workflow 2: FDA BEST Biomarker Framework

The FDA Biomarkers, EndpointS, and other Tools (BEST) resource defines seven biomarker categories by intended use. Each category has distinct validation requirements and regulatory pathways.

### Susceptibility/Risk Biomarkers

```
Definition: Indicates potential for developing a disease or condition in an individual
who does not currently have clinically apparent disease.

Examples:
- BRCA1/BRCA2 germline mutations -> breast/ovarian cancer risk (lifetime risk 45-72%)
- APOE e4 allele -> Alzheimer's disease risk (3-15x increased risk, dose-dependent)
- HLA-B27 -> ankylosing spondylitis susceptibility
- Polygenic risk scores (PRS) -> cardiovascular disease, type 2 diabetes, breast cancer
- Family history + FH genetic panel -> familial hypercholesterolemia

1. mcp__ensembl__ensembl_data(method: "get_variants", gene_id: "RISK_GENE_ID")
   -> Known risk variants with population frequencies and clinical significance

2. mcp__opentargets__ot_data(method: "get_associations", targetId: "ENSG00000xxxxx", diseaseId: "EFO_xxxxxxx")
   -> Genetic association evidence strength across multiple data sources

3. mcp__hpo__hpo_data(method: "search_hpo_terms", query: "DISEASE_PHENOTYPE")
   -> Phenotype spectrum associated with the risk marker

4. mcp__pubmed__pubmed_data(method: "search", query: "GENE risk biomarker penetrance population screening", num_results: 15)
   -> Population-level risk quantification literature

Validation requirements:
- Large prospective cohorts (>10,000 subjects) for absolute risk quantification
- Absolute risk calculation with confidence intervals (not just odds ratios)
- Net reclassification improvement (NRI) over existing risk models
- Clinical actionability: must change screening interval, prevention strategy, or risk counseling
- Penetrance estimates across ancestries (genetic biomarkers)
```

### Diagnostic Biomarkers

```
Definition: Detects or confirms presence of a disease or condition, or identifies
individuals with a subtype of disease.

Examples:
- Troponin I/T (high-sensitivity) -> acute myocardial infarction (99th percentile cutoff)
- HER2 (IHC 3+ or FISH ratio >=2.0) -> HER2-positive breast cancer subtype
- BCR-ABL1 fusion transcript -> chronic myeloid leukemia (Philadelphia chromosome)
- PD-L1 TPS/CPS -> tumor classification for immunotherapy eligibility
- CD20 expression -> B-cell lymphoma subtyping (rituximab eligibility)

1. mcp__fda__fda_data(method: "search_drugs", query: "BIOMARKER companion diagnostic")
   -> FDA-approved companion diagnostics using this biomarker

2. mcp__pubmed__pubmed_data(method: "search", query: "BIOMARKER diagnostic accuracy sensitivity specificity meta-analysis", num_results: 20)
   -> Published diagnostic performance studies and meta-analyses

3. mcp__uniprot__uniprot_data(method: "get_protein", accession: "BIOMARKER_UNIPROT")
   -> Protein characteristics relevant to assay development (isoforms, PTMs)

4. mcp__uniprot__uniprot_data(method: "get_protein_features", accession: "BIOMARKER_UNIPROT")
   -> Epitope regions for antibody-based diagnostic development

Validation requirements:
- Sensitivity >=95% for rule-out applications (high NPV)
- Specificity >=95% for confirmatory applications (high PPV)
- Comparison to established gold standard reference method
- Multi-site, multi-lot, multi-operator analytical validation
- Specimen type qualification (FFPE, fresh-frozen, blood, etc.)
- STARD-compliant reporting of diagnostic accuracy studies
```

### Monitoring Biomarkers

```
Definition: Measured serially to assess disease status or evidence of drug exposure/effect.

Examples:
- PSA -> prostate cancer recurrence monitoring (PSA doubling time predicts recurrence)
- HbA1c -> glycemic control in diabetes (target <7% for most patients)
- HIV-1 RNA viral load -> antiretroviral treatment response (goal: <50 copies/mL)
- CEA -> colorectal cancer recurrence surveillance (>5 ng/mL triggers imaging)
- BCR-ABL1 transcript level -> CML molecular response (MR4 = BCR-ABL1 <=0.01% IS)
- CA-125 -> ovarian cancer treatment response and recurrence

1. mcp__pubmed__pubmed_data(method: "search", query: "BIOMARKER serial monitoring disease progression treatment response kinetics", num_results: 15)
   -> Evidence for serial measurement utility and optimal monitoring intervals

2. mcp__clinicaltrials__ct_data(method: "search_studies", query: "BIOMARKER monitoring serial measurement guided therapy", limit: 15)
   -> Trials using serial biomarker measurements as endpoints or decision tools

3. mcp__fda__fda_data(method: "get_drug_label", drug_name: "ASSOCIATED_DRUG")
   -> Label-recommended monitoring schedules and action thresholds

Validation requirements:
- Biological variability characterization (within-subject CV, CVI)
- Analytical variability characterization (CVA)
- Reference Change Value (RCV) = 2^(1/2) * Z * (CVA^2 + CVI^2)^(1/2)
- Minimum clinically important difference definition
- Optimal monitoring interval determination
- Specimen stability across serial collection time points
- Index of individuality (CVI/CVG): if <0.6, population reference ranges are uninformative
```

### Prognostic Biomarkers

```
Definition: Identifies likelihood of a clinical event, disease recurrence, or disease
progression in patients who have the disease, regardless of treatment received.

Examples:
- Oncotype DX 21-gene recurrence score -> breast cancer recurrence risk
  (RS <26: low risk, endocrine therapy alone; RS >=26: consider chemotherapy)
- Ki-67 proliferation index -> tumor aggressiveness and prognosis
- CTC count >=5/7.5mL -> poor prognosis in metastatic breast cancer (SWOG S0500)
- NT-proBNP -> heart failure prognosis (mortality stratification)
- Gleason score -> prostate cancer prognosis
- FLIPI -> follicular lymphoma prognosis

1. mcp__pubmed__pubmed_data(method: "search", query: "BIOMARKER prognostic survival outcome hazard ratio independent predictor", num_results: 20)
   -> Prognostic association studies with multivariate analysis

2. mcp__opentargets__ot_data(method: "get_associations", targetId: "ENSG00000xxxxx", diseaseId: "EFO_xxxxxxx")
   -> Strength of gene-disease association (genetic and somatic evidence)

3. mcp__kegg__kegg_data(method: "get_pathway", pathway_id: "hsa0xxxx")
   -> Pathway context for understanding prognostic mechanism

4. mcp__clinicaltrials__ct_data(method: "search_studies", query: "BIOMARKER prognostic stratification outcome", limit: 15)
   -> Trials stratified by prognostic biomarker

Validation requirements:
- Demonstrated prognostic value independent of standard clinical factors (multivariate Cox regression)
- Hazard ratio with 95% CI from adequately powered study
- Kaplan-Meier separation by biomarker strata (log-rank p <0.001)
- Validated cutpoint reproduced in independent cohort
- C-statistic improvement over clinical-only model (Harrell's C-index)
- Time-dependent AUC for censored survival outcomes
- Calibration assessment (predicted vs observed event rates)
```

### Predictive Biomarkers

```
Definition: Identifies individuals who are more likely to experience a favorable or
unfavorable effect from a specific intervention compared to biomarker-negative patients.

CRITICAL DISTINCTION from prognostic: A predictive biomarker requires demonstration
of a treatment-by-biomarker INTERACTION, not merely a prognostic effect within a
treated subgroup.

Examples:
- HER2 amplification -> trastuzumab benefit in breast cancer (HR 0.66 for OS)
- EGFR exon 19del/L858R -> erlotinib/gefitinib/osimertinib benefit in NSCLC
- KRAS wild-type -> cetuximab benefit in mCRC (KRAS mutant = no cetuximab benefit)
- BRAF V600E -> vemurafenib/dabrafenib + trametinib benefit in melanoma
- ALK rearrangement -> crizotinib/alectinib/lorlatinib benefit in NSCLC
- MSI-H/dMMR -> pembrolizumab benefit (first tumor-agnostic biomarker approval)
- NTRK fusion -> larotrectinib/entrectinib (second tumor-agnostic approval)
- PD-L1 CPS >=10 -> pembrolizumab benefit in gastric/GEJ cancer

1. mcp__fda__fda_data(method: "get_drug_label", drug_name: "TARGETED_THERAPY")
   -> Label biomarker requirements for prescribing (companion diagnostic mandate)

2. mcp__clinicaltrials__ct_data(method: "search_studies", query: "BIOMARKER predictive enrichment randomized controlled", limit: 20)
   -> Trials demonstrating treatment-by-biomarker interaction

3. mcp__pubmed__pubmed_data(method: "search", query: "BIOMARKER predictive treatment interaction subgroup analysis biomarker-positive negative", num_results: 20)
   -> Published subgroup analyses showing differential treatment effect

4. mcp__fda__fda_data(method: "search_drugs", query: "companion diagnostic BIOMARKER", limit: 10)
   -> Approved CDx devices for this predictive biomarker

Validation requirements:
- Statistically significant treatment-by-biomarker interaction (p-interaction <0.05)
- Prospective enrichment trial or prospective-retrospective analysis (Simon 2009 criteria)
- Biomarker-positive: statistically significant treatment effect
- Biomarker-negative: ideally no treatment effect (or significantly attenuated)
- Demonstrated in >=2 independent studies or one adequately powered pivotal trial
- Companion diagnostic with FDA PMA approval (for marketed therapeutics)
- Clinical cutpoint validated for treatment selection
```

### Pharmacodynamic/Response Biomarkers

```
Definition: Shows that a biological response has occurred after exposure to a drug
or environmental agent.

Examples:
- Phospho-ERK reduction -> MEK inhibitor target engagement (Western blot, IHC)
- Platelet aggregation inhibition -> P2Y12 inhibitor effect (VerifyNow assay)
- ACE activity decrease -> ACE inhibitor pharmacodynamic effect
- Serum uric acid reduction -> uricase (rasburicase) response
- Absolute neutrophil count nadir -> chemotherapy myelosuppressive effect
- Serum cholesterol reduction -> statin pharmacodynamic response
- INR -> warfarin anticoagulant effect

1. mcp__pubmed__pubmed_data(method: "search", query: "BIOMARKER pharmacodynamic response drug exposure target engagement dose-response", num_results: 15)
   -> PD biomarker literature and dose-response relationships

2. mcp__kegg__kegg_data(method: "get_pathway", pathway_id: "PATHWAY_ID")
   -> Pathway context to identify downstream PD readouts of drug action

3. mcp__uniprot__uniprot_data(method: "get_protein_features", accession: "TARGET_PROTEIN")
   -> Post-translational modification sites as PD readouts (phosphorylation, acetylation)

4. mcp__kegg__kegg_data(method: "get_genes_in_pathway", pathway_id: "PATHWAY_ID")
   -> Identify all pathway nodes for comprehensive PD biomarker panel design

Validation requirements:
- Dose-response relationship between drug exposure and biomarker change
- Temporal relationship (onset and offset kinetics matching PK profile)
- Magnitude of change exceeding biological variability (RCV calculation)
- Correlation with clinical efficacy (desirable but not required for PD biomarker use)
- Specimen timing relative to drug administration must be standardized
- Reversibility upon drug discontinuation (for target engagement markers)
```

### Safety Biomarkers

```
Definition: Measured before or after exposure to a medical product to indicate the
likelihood, presence, or extent of toxicity as an adverse effect.

Examples:
- ALT/AST -> hepatotoxicity / drug-induced liver injury (DILI)
  Hy's Law: ALT >3x ULN + bilirubin >2x ULN + no other cause = 10-50% fatal DILI risk
- Serum creatinine/eGFR -> nephrotoxicity (aminoglycosides, cisplatin, contrast agents)
- QTc interval -> cardiac arrhythmia risk (>500ms = high risk, >60ms increase = concern)
- High-sensitivity troponin -> cardiotoxicity (anthracyclines, immune checkpoint inhibitors)
- Lipase/amylase -> pancreatitis (GLP-1 agonists, azathioprine)
- CK/myoglobin -> rhabdomyolysis (statins, daptomycin)
- Absolute neutrophil count -> myelosuppression (chemotherapy, clozapine)
- UGT1A1*28 genotype -> irinotecan toxicity risk (homozygous = dose reduction)

1. mcp__fda__fda_data(method: "get_drug_label", drug_name: "DRUG")
   -> Label warnings, boxed warnings, monitoring requirements, dose modification rules

2. mcp__pubmed__pubmed_data(method: "search", query: "DRUG safety biomarker toxicity monitoring early detection predictive", num_results: 15)
   -> Published safety biomarker evidence for specific drug classes

3. mcp__clinicaltrials__ct_data(method: "search_studies", query: "DRUG toxicity biomarker safety monitoring", limit: 10)
   -> Trials evaluating novel safety biomarkers (e.g., KIM-1 for nephrotoxicity)

Validation requirements:
- Sensitivity for toxicity detection must be high (minimize false negatives -- missing toxicity is dangerous)
- Temporal precedence: biomarker change must precede clinical toxicity (early warning)
- Defined monitoring schedule and action thresholds (stop, hold, dose-reduce)
- Reversibility assessment: does biomarker normalize with dose reduction or discontinuation?
- FDA Biomarker Qualification Program status (Letter of Support or full qualification)
- Comparison to existing safety markers (incremental value)
```

---

## Core Workflow 3: ROC/AUC Analysis

Receiver Operating Characteristic analysis for evaluating biomarker discriminatory performance.

### Single-Marker ROC Analysis

```
Steps:
1. Define binary outcome (disease present vs absent, responder vs non-responder)
2. Collect biomarker measurements in both groups
3. Calculate sensitivity and specificity at each possible threshold
4. Plot ROC curve (sensitivity vs 1-specificity)
5. Calculate AUC with 95% CI (DeLong method or bootstrap with >=2000 resamples)
6. Determine optimal cutpoint via Youden's J index or clinical criteria

Performance interpretation:
- AUC 0.90-1.00: Excellent discrimination (standalone diagnostic potential)
- AUC 0.80-0.89: Good discrimination (useful with clinical context)
- AUC 0.70-0.79: Fair discrimination (screening/triage applications)
- AUC 0.60-0.69: Poor discrimination (limited standalone value)
- AUC 0.50-0.59: No discrimination (random chance, not clinically useful)

Clinical considerations:
- High sensitivity priority: screening and rule-out tests (e.g., hs-troponin for MI rule-out)
- High specificity priority: confirmatory and rule-in tests (e.g., tissue biopsy markers)
- Prevalence affects PPV and NPV but NOT sensitivity, specificity, or AUC
- For rare diseases (prevalence <1%), even tests with 99% specificity have low PPV
- Always report prevalence-adjusted PPV/NPV for the intended-use population
```

### Multi-Marker Panel ROC

```
Steps:
1. Combine individual markers via logistic regression, random forest, or other classifier
2. Generate predicted probability as composite score
3. Plot ROC for composite vs individual markers on same axes
4. Compare AUCs using DeLong test for paired ROC curves (correlated samples)
5. Assess net reclassification improvement (NRI) and integrated discrimination improvement (IDI)

Panel construction rules:
- Include markers from orthogonal biological pathways (avoid redundancy)
- Avoid highly correlated markers (Pearson |r| >0.8 adds noise, not signal)
- Minimum 10 events per predictor variable (EPV) to avoid overfitting
- Internal validation: bootstrap (>=1000 resamples) or repeated 10-fold cross-validation
- External validation in independent cohort is MANDATORY before clinical implementation
- Report optimism-corrected AUC (bootstrap or cross-validation estimate, NOT training AUC)
```

### Cutpoint Selection Methods

```
Method 1: Youden's J Index
- J = sensitivity + specificity - 1 = TPR - FPR
- Maximizes the sum of sensitivity and specificity
- Optimal when false positives and false negatives have equal clinical cost
- Most commonly used default method

Method 2: Sensitivity or Specificity Constraint
- Fix sensitivity >=0.95, find threshold that maximizes specificity
- Use for screening/rule-out where missing disease is more harmful than false positives
- Or fix specificity >=0.95 for confirmatory applications where false positives are costly

Method 3: Cost-Weighted Optimization
- Minimize: cost_FN * (1-sensitivity) * prevalence + cost_FP * (1-specificity) * (1-prevalence)
- Requires explicit cost assignment for false negatives vs false positives
- Appropriate when clinical consequences of FP and FN differ substantially

Method 4: Clinical Decision Threshold
- Based on treatment risk-benefit analysis using NNT and NNH
- Threshold probability = 1 / (1 + benefit/harm) = 1 / (1 + NNH/NNT)
- Decision curve analysis to evaluate net benefit across range of thresholds
- Preferred when treatment-related harm must be weighed against benefit of detection

Method 5: Two-Threshold (Rule-in / Rule-out)
- Define two cutpoints: low cutpoint (rule-out, high sensitivity) and high cutpoint (rule-in, high specificity)
- Intermediate zone requires further testing or clinical judgment
- Example: hs-troponin with <5 ng/L rule-out and >52 ng/L rule-in thresholds
```

---

## Core Workflow 4: Companion Diagnostic Development

Regulatory and technical pathway for developing a companion diagnostic (CDx) tied to a therapeutic product.

### CDx Requirements (FDA)

```
1. mcp__fda__fda_data(method: "search_drugs", query: "companion diagnostic", limit: 30)
   -> Landscape of FDA-approved CDx devices

2. mcp__pubmed__pubmed_data(method: "search", query: "companion diagnostic development FDA PMA regulatory pathway co-development", num_results: 15)
   -> CDx development literature and regulatory guidance documents

FDA CDx regulatory framework:
- Companion diagnostic: essential for safe and effective use of the drug (PMA required)
- Complementary diagnostic: identifies patients likely to benefit but drug can be used without it (510(k) possible)
- Must be co-developed with the therapeutic product (concurrent or retrospective bridging)
- Labeling must cross-reference both CDx device and therapeutic product
- Analytical validation: accuracy, precision, LOD, reproducibility, specimen types
- Clinical validation: bridging study linking CDx result to therapeutic outcome

CDx development timeline (typical):
- Biomarker discovery to CDx approval: 5-8 years
- Assay development and optimization: 6-12 months
- Analytical validation (multi-site): 12-18 months
- Clinical bridging study: 18-36 months (can overlap with drug Phase 2/3)
- PMA review at FDA: 6-12 months
- Total investment: $30-50M for a novel CDx

Key CDx approvals (landmark examples):
- HERCEPTEST (Dako, IHC) -> trastuzumab for HER2+ breast cancer (1998, first CDx)
- cobas EGFR Mutation Test v2 (Roche) -> erlotinib, osimertinib in NSCLC
- VYSIS ALK Break Apart FISH (Abbott) -> crizotinib in ALK+ NSCLC
- FoundationOne CDx (Foundation Medicine) -> multi-gene panel, pan-tumor, multiple therapies
- VENTANA PD-L1 SP142 (Roche) -> atezolizumab in TNBC and NSCLC
- Guardant360 CDx (Guardant Health) -> osimertinib in EGFR+ NSCLC (first liquid biopsy CDx)
- MSI/dMMR testing -> pembrolizumab (first tumor-agnostic biomarker-drug pairing)
```

### Analytical Validation for CDx

```
Required studies per FDA guidance (21 CFR 814):

1. Accuracy / Method comparison:
   - Compare CDx to validated reference method or orthogonal assay
   - Minimum 60 positive + 60 negative specimens (more for multi-analyte panels)
   - Report PPA (positive percent agreement) and NPA (negative percent agreement) with 95% CI
   - Near-cutoff samples: enriched testing at +/- 20% of cutoff value

2. Precision / Reproducibility:
   - Multi-site study: >=3 sites, >=2 operators per site, >=2 reagent lots, >=3 non-consecutive days
   - Panel of specimens spanning the measurement range including near-cutoff
   - Report within-run, between-run, between-lot, between-site, and total precision
   - Near-cutoff specimens must show >=95% correct classification

3. Limit of Detection (LOD):
   - For mutation detection: minimum mutant allele fraction (MAF) reliably detectable
     Example: cobas EGFR test LOD = 1.56% MAF for exon 19 deletions
   - For protein expression: minimum expression level detectable above background
   - Defined as lowest analyte level with >=95% detection rate across >=60 replicates

4. Specimen type validation:
   - Each specimen type in labeling requires independent validation
   - FFPE tissue, fresh-frozen tissue, cytology, blood/plasma are distinct specimen types
   - Pre-analytical variables: fixation type/duration, storage, shipping temperature
   - Tumor content requirements: minimum % tumor cellularity for valid result

5. Interfering substances:
   - Tissue-based: necrosis, melanin pigment, hemosiderin, crush artifact
   - Blood-based: hemolysis (Hb >500 mg/dL), lipemia (TG >1500 mg/dL), icterus, anticoagulant type
   - Exogenous: common medications, contrast agents
```

### Clinical Bridging Study Design

```
Purpose: Demonstrate that CDx result predicts therapeutic benefit in pivotal trial population.

Design 1: Prospective co-development (gold standard)
- CDx used prospectively to enroll patients in pivotal drug trial
- CDx-positive patients randomized to drug vs control
- CDx-negative patients may be enrolled in separate efficacy arm
- Drug and CDx approved simultaneously

Design 2: Prospective-retrospective (Simon 2009 criteria)
- Use archived specimens from already-completed randomized controlled trial
- Test specimens with candidate CDx assay (blinded to treatment and outcome)
- Demonstrate statistically significant treatment-by-biomarker interaction
- Requirements: adequate specimen availability (>=60% of trial), pre-specified analysis plan

Design 3: Analytical bridging (when CDx differs from clinical trial assay)
- Test overlapping specimen set with both CDx and original clinical trial assay
- Demonstrate concordance: PPA >=90%, NPA >=90%
- Apply clinical trial efficacy data to CDx via concordance bridge
- Example: FoundationOne CDx bridging to individual gene-specific clinical trial assays

Statistical requirements for all designs:
- Pre-specified statistical analysis plan (SAP) filed before unblinding
- Treatment-by-biomarker interaction test (p-interaction <0.05)
- Biomarker-positive subgroup: statistically significant treatment effect (primary)
- Biomarker-negative subgroup: no significant treatment effect (supportive)
- Adequate power: >=80% for interaction test at alpha=0.05
```

---

## Core Workflow 5: Validation Ladder

The biomarker validation ladder defines five progressive stages from initial discovery through clinical implementation. Each stage requires distinct evidence types, study designs, and quality standards.

### Stage 1: Discovery (Evidence Tier T4)

```
Goal: Identify candidate biomarkers from unbiased high-throughput screening.

Approaches:
- Transcriptomics: RNA-seq or microarray (differential expression, |log2FC| >1, FDR <0.05)
- Proteomics: LC-MS/MS, TMT/iTRAQ labeling, DIA (>1.5-fold change, FDR <0.05)
- Metabolomics: LC-MS/MS or NMR (VIP >1.0 in PLS-DA, p <0.05)
- Genomics: GWAS (p <5e-8 genome-wide significance), WES/WGS (recurrent mutations)
- Epigenomics: methylation arrays (450K/EPIC), ATAC-seq, ChIP-seq

1. mcp__pubmed__pubmed_data(method: "search", query: "DISEASE biomarker discovery proteomics transcriptomics screening", num_results: 20)
   -> Published discovery studies for the disease area

2. mcp__opentargets__ot_data(method: "get_associations", targetId: "ENSG00000xxxxx", diseaseId: "EFO_xxxxxxx")
   -> Multi-source evidence for candidate-disease link (genetic, somatic, literature)

3. mcp__kegg__kegg_data(method: "find_pathway", query: "DISEASE_ASSOCIATED_PATHWAY")
   -> Pathway context for prioritizing biologically plausible candidates

Typical sample size: 20-100 per group (discovery cohort)
Expected attrition: 90-95% of candidates will NOT replicate in independent validation
Quality requirements: discovery dataset + initial replication in independent samples
```

### Stage 2: Verification (Evidence Tier T3)

```
Goal: Confirm top candidates in independent samples using targeted, quantitative assays.

Approaches:
- RT-qPCR for transcriptomic candidates (replace microarray/RNA-seq)
- ELISA or Luminex for protein candidates (replace mass spectrometry discovery)
- Targeted mass spectrometry (MRM/PRM/SRM) for protein or metabolite candidates
- Sanger sequencing or targeted NGS for genomic candidates (replace WES/WGS)
- Pyrosequencing or targeted bisulfite for methylation candidates

1. mcp__pubmed__pubmed_data(method: "search", query: "BIOMARKER verification independent cohort targeted assay ELISA qPCR", num_results: 15)
   -> Verification study results from independent groups

2. mcp__uniprot__uniprot_data(method: "get_protein", accession: "CANDIDATE_UNIPROT")
   -> Protein characteristics informing assay selection (secretion, abundance, stability)

3. mcp__uniprot__uniprot_data(method: "get_protein_features", accession: "CANDIDATE_UNIPROT")
   -> Epitope mapping for immunoassay antibody selection

Typical sample size: 50-200 per group (verification cohort, independent from discovery)
Expected attrition: 50-70% of verified candidates will NOT clinically validate
Success criteria: p <0.01 in independent cohort, effect size consistent with discovery phase
```

### Stage 3: Analytical Validation (Evidence Tier T3)

```
Goal: Establish assay performance characteristics for the clinical-grade measurement.

Key deliverables:
- LOD and LOQ defined per CLSI EP17-A2
- Precision: within-run CV <5%, between-run CV <10%, total CV <15%
- Accuracy: recovery 80-120% in spike experiments; concordance >=95% with reference method
- Linearity: demonstrated across clinically relevant range (CLSI EP06-A)
- Interference: no significant bias from hemolysis, lipemia, icterus (CLSI EP07-A3)
- Stability: specimen stable for defined conditions (time, temperature, freeze-thaw cycles)
- Standard Operating Procedure (SOP) documented
- Reference materials and quality control samples established
- Measurement traceability to certified reference material (if available)
```

### Stage 4: Clinical Validation (Evidence Tier T2 or T1)

```
Goal: Demonstrate biomarker's ability to distinguish clinical states in the intended-use population.

Key deliverables:
- ROC analysis with AUC and 95% CI (bootstrap or DeLong)
- Defined clinical cutpoint with sensitivity, specificity, PPV, NPV
- Performance characterized in intended-use population (not just convenience samples)
- Head-to-head comparison with existing standard biomarkers
- Subgroup analyses: age, sex, ethnicity, disease stage, comorbidities
- Independent external validation in >=1 separate cohort (different institution/country)
- STARD-compliant study report
```

### Stage 5: Clinical Utility (Evidence Tier T1)

```
Goal: Prove that using the biomarker changes clinical decisions and improves patient outcomes.

Key deliverables:
- Demonstrated outcome improvement in biomarker-guided arm vs standard care (RCT or equivalent)
- Health economic analysis: cost-effectiveness (ICER), budget impact
- Decision impact study: documented change in clinical management
- Clinical practice guideline incorporation (NCCN, ASCO, ESMO, or equivalent)
- Payer coverage decision support documentation
- Post-implementation monitoring plan
```

---

## Core Workflow 6: Liquid Biopsy Biomarkers

Non-invasive biomarkers detected in blood and other biofluids, enabling serial monitoring without tissue biopsy.

### Circulating Tumor DNA (ctDNA)

```
1. mcp__pubmed__pubmed_data(method: "search", query: "ctDNA circulating tumor DNA CANCER_TYPE detection sensitivity clinical validation", num_results: 20)
   -> ctDNA literature for the specific cancer type

2. mcp__clinicaltrials__ct_data(method: "search_studies", query: "ctDNA liquid biopsy CANCER_TYPE minimal residual disease", limit: 15)
   -> Ongoing ctDNA clinical trials (MRD, monitoring, genotyping)

3. mcp__fda__fda_data(method: "search_drugs", query: "liquid biopsy ctDNA companion diagnostic")
   -> FDA-approved ctDNA-based CDx tests

ctDNA applications by clinical context:
- Genotyping: identify actionable mutations without invasive tissue biopsy
  (EGFR T790M in NSCLC progression, BRCA reversion in platinum-resistant ovarian)
- Minimal residual disease (MRD): detect molecular relapse months before imaging
  (CIRCULATE-Japan, DYNAMIC-III in CRC; IMvigor010 in bladder cancer)
- Treatment monitoring: track variant allele frequency (VAF) kinetics over time
  (VAF clearance at cycle 3 predicts response in DLBCL)
- Resistance detection: identify resistance mutations at radiographic progression
  (EGFR C797S after osimertinib, ESR1 mutations after aromatase inhibitors)
- Tumor mutational burden from blood (bTMB): estimate TMB non-invasively
  (bTMB >=16 mut/Mb predicts atezolizumab benefit in NSCLC)
- Tumor fraction estimation: quantify disease burden from ctDNA concentration
- Methylation-based cancer detection: multi-cancer early detection (MCED) tests

Technical considerations:
- Pre-analytical: cell-free DNA stabilization tubes (Streck, PAXgene ccfDNA)
  Process within 6h for EDTA, 7 days for Streck tubes; double centrifugation protocol
- Sensitivity: 0.01-0.1% VAF depending on technology and target
- Technologies: ddPCR (single mutation, LOD ~0.01% VAF), targeted NGS panels (multi-gene, LOD ~0.1%),
  WGS (genome-wide but lower sensitivity ~1% VAF), methylation arrays
- FDA-approved platforms: Guardant360 CDx, FoundationOne Liquid CDx, Epi proColon (SEPT9 methylation)
- GRAIL Galleri (multi-cancer early detection, methylation-based) -- breakthrough device designation
```

### Circulating Tumor Cells (CTCs)

```
1. mcp__pubmed__pubmed_data(method: "search", query: "circulating tumor cells CTC enumeration prognosis predictive", num_results: 15)
   -> CTC prognostic and predictive evidence across cancer types

2. mcp__clinicaltrials__ct_data(method: "search_studies", query: "circulating tumor cells CTC guided therapy", limit: 10)
   -> CTC-guided treatment trials

Applications:
- Prognostic: CTC count >=5/7.5mL = poor prognosis in metastatic breast/prostate/CRC
  (FDA-cleared CellSearch, 510(k) for prognosis in metastatic breast, prostate, CRC)
- Treatment monitoring: CTC count change during therapy correlates with response
- Molecular characterization: single-CTC genomic/transcriptomic profiling for heterogeneity
- AR-V7 in CTCs: predicts resistance to enzalutamide/abiraterone in mCRPC

Challenges and limitations:
- Extreme rarity: 1-10 CTCs per mL among ~5 billion blood cells per mL
- Heterogeneity: not all CTCs are viable, proliferative, or metastasis-competent
- Epithelial bias: EpCAM-based capture (CellSearch) misses mesenchymal-transitioned CTCs
- Size-based filters may capture large non-tumor cells (megakaryocytes, endothelial)
- Clinical utility beyond prognostication remains under investigation
```

### Exosomes and Extracellular Vesicles

```
1. mcp__pubmed__pubmed_data(method: "search", query: "exosome extracellular vesicle biomarker cancer diagnostic liquid biopsy", num_results: 15)
   -> Exosome biomarker literature and clinical applications

Applications:
- Exosomal RNA profiling: mRNA, miRNA, lncRNA cargo reflects parent cell state
- Exosomal protein analysis: surface markers for cell-of-origin identification
- FDA-approved: ExoDx Prostate (EPI) test -- exosomal RNA for high-grade prostate cancer prediction
  (ERG and PCA3 mRNA in urine exosomes, reduces unnecessary biopsies)

Advantages over ctDNA:
- Cargo includes proteins and RNA (not limited to DNA mutations)
- Protected from degradation by lipid bilayer membrane (more stable)
- Reflects active cellular secretion (biological state) not just cell death
- Tissue-specific surface markers enable enrichment of tumor-derived vesicles

Challenges:
- Standardization of isolation methods (ultracentrifugation vs size-exclusion vs immunocapture)
- Contamination with non-exosomal vesicles (microvesicles, apoptotic bodies)
- Limited quantification standards and reference materials
```

### Cell-Free RNA (cfRNA)

```
1. mcp__pubmed__pubmed_data(method: "search", query: "cell-free RNA cfRNA liquid biopsy cancer detection tissue deconvolution", num_results: 15)
   -> Emerging cfRNA biomarker research

Applications:
- Tissue-of-origin deconvolution from cfRNA expression profiles
- Cancer detection via tumor-specific transcript fragments
- Prenatal diagnostics: fetal cfRNA in maternal blood (non-invasive prenatal testing extensions)
- Organ transplant rejection monitoring (donor-derived cfRNA in recipient blood)
- Autoimmune disease activity monitoring (tissue damage signature)

Technical considerations:
- Rapid degradation by RNases: requires immediate stabilization (PAXgene RNA tubes)
- Lower abundance than cfDNA in most clinical scenarios
- Whole-transcriptome profiling possible via cfRNA-seq but technically demanding
- Complementary to cfDNA: provides expression/splicing information DNA cannot capture
```

---

## Core Workflow 7: Functional Biomarker Discovery via DepMap

Use the Cancer Dependency Map (DepMap) to discover and validate functional biomarkers -- mutations, expression changes, or other molecular features that predict cancer cell dependency on specific genes or sensitivity to drugs. DepMap provides genome-scale CRISPR knockout screens and drug sensitivity profiling across ~1,800 cancer cell lines, enabling data-driven biomarker-target hypothesis testing.

### Step 1: Hypothesize Biomarker-Target Relationship

```
Formulate a testable hypothesis linking a molecular feature (biomarker candidate) to
a functional consequence (gene dependency or drug sensitivity).

Example hypotheses:
- "KRAS G12C mutation predicts dependency on SHP2 (PTPN11)"
- "BRAF V600E mutation predicts sensitivity to MEK inhibitors"
- "STK11 loss predicts resistance to immune checkpoint inhibitors"
- "MYC amplification predicts dependency on CDK9"

Use Open Targets and PubMed to establish biological rationale:

1. mcp__opentargets__ot_data(method: "search_target", query: "TARGET_GENE")
   -> Resolve target identity and get Ensembl ID

2. mcp__pubmed__pubmed_data(method: "search", query: "BIOMARKER_GENE TARGET_GENE synthetic lethal dependency cancer", num_results: 15)
   -> Prior evidence for biomarker-target relationship

3. mcp__kegg__kegg_data(method: "find_pathway", query: "RELEVANT_PATHWAY")
   -> Pathway context linking biomarker and target
```

### Step 2: Test with Biomarker Analysis (Mutation-Dependency Correlation)

```
Use DepMap to test whether the candidate biomarker (e.g., mutation) predicts
dependency on the target gene across hundreds of cancer cell lines.

1. mcp__depmap__depmap_data(method: "get_biomarker_analysis", gene: "TARGET_GENE", biomarker_gene: "BIOMARKER_GENE")
   -> Statistical test: do cell lines with BIOMARKER_GENE mutation show greater
      dependency on TARGET_GENE than wild-type lines?
   -> Returns effect size (difference in mean dependency score), p-value, and
      number of mutant vs wild-type cell lines

Interpretation:
- Dependency score < -0.5 = strong dependency (cell death upon knockout)
- Dependency score ~ 0 = no effect of knockout
- Effect size: difference in mean dependency between mutant and wild-type groups
- p-value < 0.05 with |effect size| > 0.1 = meaningful biomarker-dependency association
- Larger sample sizes (more cell lines in both groups) increase statistical confidence

Example call:
  mcp__depmap__depmap_data(method: "get_biomarker_analysis", gene: "PTPN11", biomarker_gene: "KRAS")
  -> Tests whether KRAS-mutant cell lines are more dependent on SHP2 (PTPN11) than KRAS-wild-type lines
```

### Step 3: Validate with Drug Sensitivity Data

```
Cross-validate the functional dependency finding with drug sensitivity data.
If a biomarker predicts gene dependency, it should also predict sensitivity to
drugs targeting that gene or pathway.

1. mcp__depmap__depmap_data(method: "get_drug_sensitivity", gene: "BIOMARKER_GENE")
   -> Drug sensitivity correlations for cell lines with BIOMARKER_GENE alterations
   -> Identifies compounds whose efficacy correlates with the biomarker

2. mcp__depmap__depmap_data(method: "get_gene_dependency", gene: "TARGET_GENE")
   -> Dependency scores across all cell lines for the target gene
   -> Confirm that dependency is selective (not a pan-essential gene)

Convergence criteria:
- Genetic dependency (CRISPR) and pharmacological sensitivity (drug) should agree
- If BIOMARKER-mutant lines depend on TARGET_GENE AND are sensitive to TARGET_GENE inhibitors,
  the biomarker has convergent functional validation
- Discordance (dependency without drug sensitivity) may indicate drug-specific resistance
  mechanisms or insufficient target engagement
```

### Step 4: Assess Biomarker Prevalence Across Lineages

```
Determine how broadly the biomarker-dependency relationship holds across cancer types.
Lineage-specific vs pan-cancer biomarkers have different clinical development paths.

1. mcp__depmap__depmap_data(method: "get_mutations", gene: "BIOMARKER_GENE")
   -> Mutation landscape: frequency, types (missense, nonsense, frameshift),
      and distribution across cancer lineages

2. mcp__depmap__depmap_data(method: "get_gene_expression", gene: "TARGET_GENE")
   -> Expression levels of the target gene across cell lines and lineages
   -> Low expression may indicate lineages where the target is not relevant

3. mcp__depmap__depmap_data(method: "get_biomarker_analysis", gene: "TARGET_GENE", biomarker_gene: "BIOMARKER_GENE")
   -> Re-examine the biomarker-dependency association stratified by lineage
   -> Identify lineages where the effect is strongest vs absent

Clinical development implications:
- Pan-cancer biomarker (consistent across lineages): tumor-agnostic development path
  (precedent: MSI-H/dMMR for pembrolizumab, NTRK fusions for larotrectinib)
- Lineage-specific biomarker: indication-specific development with enrichment design
- Biomarker prevalence determines addressable patient population and commercial viability
```

### Step 5: Generate Effect Size and Statistical Significance

```
Compile quantitative evidence for the biomarker-target relationship with
formal statistical assessment.

1. mcp__depmap__depmap_data(method: "get_biomarker_analysis", gene: "TARGET_GENE", biomarker_gene: "BIOMARKER_GENE")
   -> Primary statistical output:
      - Effect size (Cohen's d or difference in means)
      - P-value (t-test or Wilcoxon rank-sum)
      - Number of mutant vs wild-type cell lines
      - 95% confidence interval for effect size

2. mcp__depmap__depmap_data(method: "get_gene_dependency", gene: "TARGET_GENE")
   -> Distribution of dependency scores for selectivity assessment
   -> Essential in all lines (pan-essential) = poor therapeutic target
   -> Selectively essential in biomarker-positive lines = ideal biomarker-target pair

3. mcp__depmap__depmap_data(method: "get_drug_sensitivity", gene: "BIOMARKER_GENE")
   -> Pharmacological validation effect sizes and significance

Reporting template:
- Biomarker: [GENE mutation/amplification/expression]
- Target: [GENE]
- N mutant lines: [n] | N wild-type lines: [n]
- Mean dependency (mutant): [score] | Mean dependency (WT): [score]
- Effect size: [difference] (95% CI: [lower, upper])
- P-value: [value]
- Drug sensitivity concordance: [yes/no, compound name, IC50 difference]
- Lineage specificity: [pan-cancer / lineage-restricted to X, Y, Z]
- Evidence tier: T3 (functional screen) or T4 (computational) pending clinical validation
- Recommended next step: [prospective clinical biomarker study / basket trial / companion Dx co-development]
```

---

## Biomarker Readiness Scoring

Composite score (0-100) assessing a biomarker's maturity across five weighted dimensions. Calculate for each candidate to prioritize development investment and identify critical gaps.

### Scoring Dimensions and Weights

| Dimension | Weight | 0-20 (Insufficient) | 21-40 (Early) | 41-60 (Developing) | 61-80 (Advanced) | 81-100 (Mature) |
|-----------|--------|---------------------|---------------|---------------------|-------------------|-----------------|
| **Analytical Validity** | 25% | No assay exists; research-use-only reagents | Research assay with preliminary LOD data | Assay with partial validation (LOD, precision, linearity) | Multi-site analytical validation complete; near-CLIA compliance | Fully validated clinical-grade assay; CLIA/CAP compliant; FDA-cleared platform |
| **Clinical Validity** | 25% | No clinical studies; in silico prediction only | Single pilot study (n<50), AUC <0.70 | Case-control study (n=50-200), AUC 0.70-0.80 | Multi-cohort validation, AUC 0.80-0.90 | Prospective validation in intended population, AUC >0.90 |
| **Clinical Utility** | 20% | No outcome data whatsoever | Decision impact modeling or simulation | Retrospective outcome association | Prospective observational utility data | Prospective RCT demonstrating improved outcomes with biomarker-guided strategy |
| **Regulatory Pathway Clarity** | 15% | No regulatory precedent; entirely novel biomarker type | Analogous biomarker exists but no direct guidance | FDA Letter of Support or CDRH Pre-Sub feedback | FDA Biomarker Qualification or CDx PMA precedent for same analyte class | FDA-qualified biomarker or approved CDx for this specific marker |
| **Technical Feasibility** | 15% | Requires novel technology not yet commercially available; specimen difficult to obtain | Standard platform but complex manual workflow; specialized specimen | Semi-automated platform; standard clinical specimen; 2-5 day TAT | Automated platform; routine specimen (blood, FFPE); 24-48h TAT | Point-of-care or fully automated; routine specimen; <=24h turnaround; <$200/test |

### Scoring Procedure

```
For each dimension:
1. Gather evidence using MCP tools (PubMed literature, ClinicalTrials.gov, FDA data, protein databases)
2. Assign subscores (0-100) based on criteria in the table above
3. Calculate weighted composite:

   Readiness Score = (Analytical_Validity * 0.25) + (Clinical_Validity * 0.25) +
                     (Clinical_Utility * 0.20) + (Regulatory_Clarity * 0.15) +
                     (Technical_Feasibility * 0.15)

Interpretation bands:
- 80-100: READY -- Clinical implementation viable; pursue regulatory submission or guideline adoption
- 60-79:  ADVANCED -- 1-2 dimensions need strengthening; targeted validation studies will close gaps
- 40-59:  DEVELOPING -- Significant gaps remain; multi-year development plan required
- 20-39:  EARLY -- Discovery/verification stage; high attrition risk; foundational work needed
- 0-19:   CONCEPT -- Insufficient evidence for development commitment; reconsider hypothesis

WORKED EXAMPLE 1: HER2 in breast cancer (predictive biomarker for trastuzumab)
- Analytical Validity: 95 (multiple FDA-approved IHC and FISH assays; ASCO/CAP testing guidelines; extensive round-robin proficiency testing)
- Clinical Validity: 98 (decades of prospective data; robust discrimination of HER2+ vs HER2-; concordance studies across platforms)
- Clinical Utility: 100 (HERA, NSABP B-31, NCCTG N9831 pivotal trials; 37% OS improvement; chemotherapy-sparing in HER2-low)
- Regulatory Pathway: 100 (multiple approved CDx since 1998; well-established PMA precedent)
- Technical Feasibility: 90 (IHC on routine FFPE tissue; 24-48h TAT; available in every pathology lab)
- Weighted Score: 0.25*95 + 0.25*98 + 0.20*100 + 0.15*100 + 0.15*90 = 96.8

WORKED EXAMPLE 2: Novel cfRNA panel for early-stage pancreatic cancer detection
- Analytical Validity: 30 (research-grade RNA-seq assay; LOD partially characterized; no multi-site precision)
- Clinical Validity: 25 (single pilot case-control study, n=50 per group, AUC 0.75)
- Clinical Utility: 5 (no outcome data; no decision impact study)
- Regulatory Pathway: 20 (LDT pathway theoretically possible; no FDA guidance specific to cfRNA cancer detection)
- Technical Feasibility: 35 (requires specialized RNA stabilization tubes; 3-5 day workflow; ~$1500/test)
- Weighted Score: 0.25*30 + 0.25*25 + 0.20*5 + 0.15*20 + 0.15*35 = 23.0
```

---

## Python Code Templates

### ROC Curve Analysis with AUC and Bootstrap Confidence Interval

```python
import numpy as np
from sklearn.metrics import roc_curve, auc
import matplotlib.pyplot as plt

def roc_analysis_with_ci(y_true, y_scores, n_bootstraps=2000, alpha=0.05):
    """
    ROC curve analysis with bootstrap confidence interval for AUC.

    Parameters:
        y_true: array of binary labels (0=control, 1=case)
        y_scores: array of continuous biomarker measurements
        n_bootstraps: number of bootstrap iterations for CI (default 2000)
        alpha: significance level for CI (default 0.05 for 95% CI)

    Returns:
        dict with fpr, tpr, thresholds, auc, auc_ci_lower, auc_ci_upper
    """
    y_true = np.asarray(y_true)
    y_scores = np.asarray(y_scores)

    # Primary ROC curve and AUC
    fpr, tpr, thresholds = roc_curve(y_true, y_scores)
    roc_auc = auc(fpr, tpr)

    # Bootstrap confidence interval for AUC
    bootstrapped_aucs = []
    rng = np.random.RandomState(42)
    for _ in range(n_bootstraps):
        indices = rng.randint(0, len(y_true), len(y_true))
        if len(np.unique(y_true[indices])) < 2:
            continue  # skip resamples with only one class
        boot_fpr, boot_tpr, _ = roc_curve(y_true[indices], y_scores[indices])
        bootstrapped_aucs.append(auc(boot_fpr, boot_tpr))

    sorted_aucs = np.array(sorted(bootstrapped_aucs))
    ci_lower = sorted_aucs[int((alpha / 2) * len(sorted_aucs))]
    ci_upper = sorted_aucs[int((1 - alpha / 2) * len(sorted_aucs))]

    # Plot ROC curve
    fig, ax = plt.subplots(1, 1, figsize=(8, 8))
    ax.plot(fpr, tpr, color='#2563eb', lw=2,
            label=f'ROC curve (AUC = {roc_auc:.3f}, 95% CI: {ci_lower:.3f}-{ci_upper:.3f})')
    ax.plot([0, 1], [0, 1], color='gray', lw=1, linestyle='--', label='Random classifier (AUC = 0.500)')
    ax.fill_between(fpr, tpr, alpha=0.1, color='#2563eb')
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel('1 - Specificity (False Positive Rate)', fontsize=12)
    ax.set_ylabel('Sensitivity (True Positive Rate)', fontsize=12)
    ax.set_title('Receiver Operating Characteristic Curve', fontsize=14)
    ax.legend(loc='lower right', fontsize=11)
    ax.set_aspect('equal')
    plt.tight_layout()
    plt.savefig('roc_curve.png', dpi=150, bbox_inches='tight')
    plt.close()

    return {
        'fpr': fpr, 'tpr': tpr, 'thresholds': thresholds,
        'auc': roc_auc, 'auc_ci_lower': ci_lower, 'auc_ci_upper': ci_upper
    }
```

### Youden's J Index for Optimal Cutpoint Selection

```python
import numpy as np
from sklearn.metrics import roc_curve, confusion_matrix

def youdens_j_cutpoint(y_true, y_scores):
    """
    Find optimal biomarker cutpoint using Youden's J statistic.
    J = sensitivity + specificity - 1 (maximized at optimal threshold).

    Also computes PPV, NPV, likelihood ratios, and diagnostic odds ratio.

    Parameters:
        y_true: array of binary labels (0=control, 1=case)
        y_scores: array of continuous biomarker measurements

    Returns:
        dict with optimal_threshold, sensitivity, specificity, ppv, npv,
              j_statistic, lr_positive, lr_negative, diagnostic_odds_ratio
    """
    y_true = np.asarray(y_true)
    y_scores = np.asarray(y_scores)

    fpr, tpr, thresholds = roc_curve(y_true, y_scores)

    # Youden's J = TPR - FPR = sensitivity + specificity - 1
    j_scores = tpr - fpr
    optimal_idx = np.argmax(j_scores)

    optimal_threshold = thresholds[optimal_idx]
    optimal_sensitivity = tpr[optimal_idx]
    optimal_specificity = 1 - fpr[optimal_idx]
    optimal_j = j_scores[optimal_idx]

    # Confusion matrix at optimal threshold
    y_pred = (y_scores >= optimal_threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

    # Performance metrics
    ppv = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    npv = tn / (tn + fn) if (tn + fn) > 0 else 0.0
    lr_positive = optimal_sensitivity / (1 - optimal_specificity) if optimal_specificity < 1.0 else float('inf')
    lr_negative = (1 - optimal_sensitivity) / optimal_specificity if optimal_specificity > 0.0 else float('inf')
    dor = (tp * tn) / (fp * fn) if (fp * fn) > 0 else float('inf')

    print(f"=== Optimal Cutpoint via Youden's J ===")
    print(f"Cutpoint:      {optimal_threshold:.4f}")
    print(f"Sensitivity:   {optimal_sensitivity:.3f} ({tp}/{tp+fn})")
    print(f"Specificity:   {optimal_specificity:.3f} ({tn}/{tn+fp})")
    print(f"PPV:           {ppv:.3f}")
    print(f"NPV:           {npv:.3f}")
    print(f"Youden's J:    {optimal_j:.3f}")
    print(f"LR+:           {lr_positive:.2f}")
    print(f"LR-:           {lr_negative:.3f}")
    print(f"DOR:           {dor:.1f}")

    return {
        'optimal_threshold': optimal_threshold,
        'sensitivity': optimal_sensitivity,
        'specificity': optimal_specificity,
        'ppv': ppv, 'npv': npv,
        'j_statistic': optimal_j,
        'lr_positive': lr_positive,
        'lr_negative': lr_negative,
        'diagnostic_odds_ratio': dor
    }
```

### Biomarker Panel Logistic Regression with Cross-Validation

```python
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RepeatedStratifiedKFold, cross_val_predict
from sklearn.metrics import roc_curve, auc, roc_auc_score
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

def biomarker_panel_logistic_regression(X, y, marker_names, n_repeats=10, n_splits=5):
    """
    Build and evaluate a multi-marker biomarker panel using L2-regularized
    logistic regression with repeated stratified cross-validation.

    Parameters:
        X: numpy array (n_samples, n_markers) of biomarker measurements
        y: array of binary labels (0=control, 1=case)
        marker_names: list of biomarker names corresponding to columns of X
        n_repeats: number of cross-validation repeats (default 10)
        n_splits: number of folds per repeat (default 5)

    Returns:
        dict with model, scaler, coefficients, individual_aucs, train_auc, cv_auc
    """
    X = np.asarray(X)
    y = np.asarray(y)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Fit logistic regression model on full data (for coefficients)
    model = LogisticRegression(penalty='l2', C=1.0, solver='lbfgs', max_iter=1000, random_state=42)
    model.fit(X_scaled, y)

    # Cross-validated predicted probabilities (unbiased performance estimate)
    cv = RepeatedStratifiedKFold(n_splits=n_splits, n_repeats=n_repeats, random_state=42)
    y_proba_cv = cross_val_predict(model, X_scaled, y, cv=cv, method='predict_proba')[:, 1]
    cv_auc = roc_auc_score(y, y_proba_cv)

    # Training AUC (will be optimistic -- report CV AUC for decisions)
    y_proba_train = model.predict_proba(X_scaled)[:, 1]
    train_auc = roc_auc_score(y, y_proba_train)

    # Individual marker AUCs for comparison
    individual_aucs = {}
    for i, name in enumerate(marker_names):
        individual_aucs[name] = roc_auc_score(y, X_scaled[:, i])

    # Comparative ROC plot: panel vs individual markers
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))

    fpr_panel, tpr_panel, _ = roc_curve(y, y_proba_cv)
    ax.plot(fpr_panel, tpr_panel, color='#dc2626', lw=2.5,
            label=f'Panel ({n_splits}-fold CV AUC = {cv_auc:.3f})')

    colors = plt.cm.Set2(np.linspace(0, 1, len(marker_names)))
    for i, name in enumerate(marker_names):
        fpr_i, tpr_i, _ = roc_curve(y, X_scaled[:, i])
        auc_i = individual_aucs[name]
        ax.plot(fpr_i, tpr_i, color=colors[i], lw=1.5, linestyle='--',
                label=f'{name} (AUC = {auc_i:.3f})')

    ax.plot([0, 1], [0, 1], color='gray', lw=1, linestyle=':')
    ax.set_xlabel('1 - Specificity', fontsize=12)
    ax.set_ylabel('Sensitivity', fontsize=12)
    ax.set_title('Biomarker Panel vs Individual Markers', fontsize=14)
    ax.legend(loc='lower right', fontsize=10)
    ax.set_aspect('equal')
    plt.tight_layout()
    plt.savefig('panel_roc_comparison.png', dpi=150, bbox_inches='tight')
    plt.close()

    # Model coefficients (standardized)
    coefficients = dict(zip(marker_names, model.coef_[0]))

    print("=== Biomarker Panel Results ===")
    print(f"Training AUC (optimistic): {train_auc:.3f}")
    print(f"Cross-validated AUC ({n_splits}-fold x {n_repeats} repeats): {cv_auc:.3f}")
    print(f"\nIndividual marker AUCs:")
    for name, a in sorted(individual_aucs.items(), key=lambda x: x[1], reverse=True):
        print(f"  {name}: {a:.3f}")
    print(f"\nStandardized logistic regression coefficients:")
    for name, c in sorted(coefficients.items(), key=lambda x: abs(x[1]), reverse=True):
        print(f"  {name}: {c:+.4f}")

    return {
        'model': model, 'scaler': scaler,
        'coefficients': coefficients,
        'individual_aucs': individual_aucs,
        'train_auc': train_auc, 'cv_auc': cv_auc
    }
```

### Kaplan-Meier Survival Analysis by Biomarker Strata

```python
import numpy as np
import matplotlib.pyplot as plt
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test

def km_by_biomarker_strata(time, event, biomarker, cutpoint, biomarker_name='Biomarker',
                            time_unit='months'):
    """
    Kaplan-Meier survival analysis stratified by biomarker cutpoint.
    Includes log-rank test, median survival comparison, and crude HR estimate.

    Parameters:
        time: array of follow-up times (months or years)
        event: array of event indicators (1=event occurred, 0=censored)
        biomarker: array of continuous biomarker measurements
        cutpoint: threshold to dichotomize biomarker (high >= cutpoint, low < cutpoint)
        biomarker_name: name for plot labels and output
        time_unit: unit of time axis (default 'months')

    Returns:
        dict with median_survival_high, median_survival_low, hr_estimate,
              logrank_p, logrank_statistic, n_high, n_low
    """
    time = np.asarray(time)
    event = np.asarray(event)
    biomarker = np.asarray(biomarker)

    high_mask = biomarker >= cutpoint
    low_mask = biomarker < cutpoint

    n_high = int(high_mask.sum())
    n_low = int(low_mask.sum())
    events_high = int(event[high_mask].sum())
    events_low = int(event[low_mask].sum())

    # Fit Kaplan-Meier for each stratum
    kmf_high = KaplanMeierFitter()
    kmf_high.fit(time[high_mask], event[high_mask],
                 label=f'{biomarker_name} High (n={n_high}, events={events_high})')

    kmf_low = KaplanMeierFitter()
    kmf_low.fit(time[low_mask], event[low_mask],
                label=f'{biomarker_name} Low (n={n_low}, events={events_low})')

    # Log-rank test for survival difference
    lr_result = logrank_test(
        time[high_mask], time[low_mask],
        event[high_mask], event[low_mask]
    )

    # Median survival times
    median_high = kmf_high.median_survival_time_
    median_low = kmf_low.median_survival_time_

    # Crude hazard ratio estimate from incidence rates
    person_time_high = time[high_mask].sum()
    person_time_low = time[low_mask].sum()
    rate_high = events_high / person_time_high if person_time_high > 0 else 0
    rate_low = events_low / person_time_low if person_time_low > 0 else 0
    hr_estimate = rate_high / rate_low if rate_low > 0 else float('inf')

    # Survival plot
    fig, ax = plt.subplots(1, 1, figsize=(10, 7))
    kmf_high.plot_survival_function(ax=ax, color='#dc2626', lw=2, ci_show=True)
    kmf_low.plot_survival_function(ax=ax, color='#2563eb', lw=2, ci_show=True)

    ax.set_xlabel(f'Time ({time_unit})', fontsize=12)
    ax.set_ylabel('Survival Probability', fontsize=12)
    ax.set_title(f'Kaplan-Meier Survival by {biomarker_name} Status (cutpoint = {cutpoint})', fontsize=14)

    # Annotation box with key statistics
    textstr = (f'Log-rank p = {lr_result.p_value:.2e}\n'
               f'HR (high/low) = {hr_estimate:.2f}\n'
               f'Median high = {median_high:.1f} {time_unit}\n'
               f'Median low = {median_low:.1f} {time_unit}')
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax.text(0.98, 0.98, textstr, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', horizontalalignment='right', bbox=props)

    ax.legend(loc='lower left', fontsize=11)
    plt.tight_layout()
    plt.savefig('km_biomarker_strata.png', dpi=150, bbox_inches='tight')
    plt.close()

    print(f"=== Kaplan-Meier Analysis: {biomarker_name} ===")
    print(f"Cutpoint: {cutpoint}")
    print(f"High group: n={n_high}, events={events_high}, median={median_high:.1f} {time_unit}")
    print(f"Low group:  n={n_low}, events={events_low}, median={median_low:.1f} {time_unit}")
    print(f"Log-rank chi-squared: {lr_result.test_statistic:.3f}")
    print(f"Log-rank p-value: {lr_result.p_value:.2e}")
    print(f"Crude HR (high/low): {hr_estimate:.2f}")

    return {
        'median_survival_high': median_high,
        'median_survival_low': median_low,
        'hr_estimate': hr_estimate,
        'logrank_p': lr_result.p_value,
        'logrank_statistic': lr_result.test_statistic,
        'n_high': n_high, 'n_low': n_low,
        'events_high': events_high, 'events_low': events_low
    }
```

---

## T1-T4 Evidence Grading

Assign an evidence tier to every biomarker claim based on the strength and provenance of supporting data. Evidence tier determines confidence in clinical decision-making.

| Tier | Label | Criteria | Typical Sources |
|------|-------|----------|-----------------|
| **T1** | Prospective clinical validation | Biomarker validated in prospective trial or prospective-retrospective analysis of RCT specimens; FDA-approved CDx; incorporated in clinical practice guidelines (NCCN, ASCO, ESMO) | Pivotal trial biomarker data, FDA drug labels with CDx requirements, NCCN/ESMO/ASCO guideline recommendations, FDA-qualified biomarker list |
| **T2** | Retrospective clinical validation | Biomarker validated in >=2 independent retrospective cohorts with adequate sample size; published meta-analyses of diagnostic/prognostic performance | PubMed meta-analyses of diagnostic accuracy, multi-center retrospective validation studies, CLIA-validated LDT performance data, large biobank studies |
| **T3** | Discovery and analytical validation | Biomarker identified in discovery-phase omics studies or analytically validated without clinical validation in intended-use population | Discovery proteomics/transcriptomics publications, CLSI-compliant analytical validation reports, small pilot clinical studies (n<100 per group), phase I/II exploratory biomarker substudies |
| **T4** | In silico and preclinical | Biomarker identified computationally, in preclinical models, or through pathway inference; no human clinical validation data | Open Targets text-mining scores, KEGG/Reactome pathway analysis, GTEx expression data, in vitro cell line experiments, animal model studies, bioinformatic prediction tools |

### Evidence Grading Procedure

```
For each biomarker assessed, follow this systematic grading procedure:

1. Search for prospective clinical validation:
   mcp__pubmed__pubmed_data(method: "search", query: "BIOMARKER prospective validation clinical trial randomized", num_results: 10)
   mcp__fda__fda_data(method: "get_drug_label", drug_name: "ASSOCIATED_DRUG")
   -> If biomarker appears in FDA label as required CDx: automatically T1
   -> If validated prospectively with pre-specified analysis in adequate sample: T1

2. Search for retrospective validation:
   mcp__pubmed__pubmed_data(method: "search", query: "BIOMARKER retrospective validation independent cohort multi-center", num_results: 10)
   -> If validated in >=2 independent cohorts with consistent performance: T2
   -> If meta-analysis available with >=3 studies: T2

3. Search for analytical validation or discovery studies:
   mcp__pubmed__pubmed_data(method: "search", query: "BIOMARKER analytical validation assay performance discovery omics", num_results: 10)
   -> If only discovery data or analytical validation without clinical correlation: T3

4. Check computational and database evidence only:
   mcp__opentargets__ot_data(method: "get_associations", targetId: "ENSG...", diseaseId: "EFO...")
   mcp__kegg__kegg_data(method: "find_pathway", query: "DISEASE_PATHWAY")
   mcp__gtex__gtex_data(method: "get_median_gene_expression", gene_id: "ENSG...")
   -> If only computational, pathway, or expression data without clinical studies: T4

Downgrade rules (apply regardless of study design claims):
- Single-center study without external validation: maximum T2
- Sample size <50 per group: maximum T3
- No analytical validation of measurement assay: maximum T3
- Animal model or cell line data only: T4 regardless of study quality
- Post-hoc subgroup analysis without pre-specification: downgrade one tier

Upgrade conditions (when supporting evidence is exceptionally strong):
- FDA Letter of Support or full biomarker qualification: qualifies for T1
- NCCN or ESMO clinical practice guideline recommendation: qualifies for T1
- Meta-analysis of >=5 independent validation studies with consistent results: qualifies for T1
- Prospective-retrospective analysis meeting all Simon 2009 criteria: qualifies for T1
```

### Fallback Chains

When a primary MCP tool returns no data for a biomarker query, follow the fallback chain before marking any section as "insufficient data."

```
Biomarker-disease association evidence:
  Open Targets get_associations -> PubMed search -> KEGG find_pathway -> GO search_go_terms -> HPO search_hpo_terms

Tissue expression and specificity:
  GTEx get_median_gene_expression -> GTEx get_gene_expression -> UniProt get_protein (subcellular location) -> Ensembl get_gene_info -> PubMed search

Protein biomarker characterization:
  UniProt get_protein -> UniProt get_protein_features -> Ensembl get_gene_info -> PubMed search

Pathway and functional context:
  KEGG get_pathway -> KEGG get_genes_in_pathway -> GO get_go_term -> Open Targets get_target_info -> PubMed search

Clinical validation performance data:
  PubMed search (ROC/AUC/sensitivity) -> ClinicalTrials.gov search_studies -> FDA get_drug_label (CDx section)

Companion diagnostic status:
  FDA search_drugs (companion diagnostic) -> FDA get_drug_label -> PubMed search (CDx development)

Phenotype-biomarker linkage:
  HPO search_hpo_terms -> HPO get_hpo_term -> Open Targets get_target_info -> PubMed search

Genomic variant context:
  Ensembl get_variants -> Ensembl get_gene_info -> Open Targets get_associations -> PubMed search

Functional dependency and drug sensitivity (cancer):
  DepMap get_biomarker_analysis -> DepMap get_gene_dependency -> DepMap get_drug_sensitivity -> DepMap get_mutations -> PubMed search
```

## Completeness Checklist

- [ ] Report file created with all section headers and placeholders populated
- [ ] Biomarker classified using FDA BEST framework (susceptibility/risk, diagnostic, monitoring, predictive, prognostic, pharmacodynamic/response, safety)
- [ ] Tissue expression pattern characterized (GTEx, protein atlas data)
- [ ] Target-disease association evidence retrieved and scored
- [ ] Literature evidence gathered (validation studies, clinical utility publications)
- [ ] ROC/AUC performance metrics calculated or cited for diagnostic/predictive biomarkers
- [ ] Biomarker Readiness Level (BRL) score assigned with justification
- [ ] Companion diagnostic feasibility assessed (if applicable)
- [ ] Clinical trial evidence reviewed for biomarker-stratified designs
- [ ] Validation ladder stage determined (discovery, analytical validation, clinical validation, clinical utility)
