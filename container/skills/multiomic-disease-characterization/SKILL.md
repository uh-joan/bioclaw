---
name: multiomic-disease-characterization
description: Comprehensive multi-omics disease characterization integrating genomics, transcriptomics, proteomics, pathways, and therapeutic layers. Produces confidence-scored reports with cross-layer concordance analysis. Use when user mentions multi-omics, multi-omic, omics integration, disease characterization, omics layers, genomics transcriptomics proteomics, cross-layer concordance, disease driver genes, hub genes, PPI network, multi-omics confidence score, omics report, disease omics profile, integrated omics, cross-omics, omics pipeline, disease molecular profile, omics concordance, or multi-omic disease analysis.
---

# Multi-Omic Disease Characterization

Comprehensive multi-omics disease characterization integrating genomics, transcriptomics, proteomics, protein-protein interactions, pathways, gene ontology, and therapeutic landscape layers. Produces confidence-scored reports with cross-layer concordance analysis to identify high-confidence disease drivers. Uses Open Targets for target-disease evidence, ChEMBL for bioactivity and pharmacology, DrugBank for drug-target-pathway relationships, PubMed for literature evidence, PubChem for chemical biology and bioassays, FDA for regulatory and safety intelligence, ClinicalTrials.gov for clinical pipeline, and NLM for clinical coding and gene annotation.

## Report-First Workflow

1. **Create report file immediately**: `[disease]_multiomic-disease-characterization_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Deep disease biology, epidemiology, and natural history → use `disease-research`
- Exhaustive single-target profiling (9-path deep dive) → use `target-research`
- Computational multi-omics data integration (CCA, MOFA, factor analysis) → use `multi-omics-integration`
- Gene set enrichment analysis (ORA/GSEA) → use `gene-enrichment`
- Patient-level genomic-clinical stratification → use `precision-medicine-stratifier`
- Druggability assessment, SAR, and bioactivity analysis → use `drug-target-analyst`

## Cross-Reference: Other Skills

- **Deep disease biology and epidemiology** -> use disease-research skill
- **Exhaustive single-target profiling (9-path)** -> use target-research skill
- **Systems-level pathway integration and network topology** -> use systems-biology skill
- **Gene set enrichment analysis (ORA/GSEA)** -> use gene-enrichment skill
- **Patient-level genomic-clinical stratification** -> use precision-medicine-stratifier skill
- **Druggability, SAR, bioactivity analysis** -> use drug-target-analyst skill

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

### `mcp__chembl__chembl_info` (Bioactivity & SAR)

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

### `mcp__pubmed__pubmed_articles` (Literature Evidence)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Quick keyword search | `keywords`, `num_results` |
| `search_advanced` | Filtered search | `term`, `journal`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Full article details | `pmid` |

### `mcp__pubchem__pubchem_info` (Chemical Biology & Bioassays)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_compounds` | Compound lookup by name/CID/SMILES | `query`, `search_type` |
| `get_compound_properties` | Molecular properties (MW, logP, PSA, rotatable bonds) | `cid` |
| `get_compound_info` | Full compound record | `cid` |
| `get_safety_data` | GHS hazard classifications, signal words, pictograms | `cid` |
| `search_similar_compounds` | Structural analogs for scaffold analysis | `smiles`, `threshold` |
| `analyze_stereochemistry` | Stereo-specific assessment | `cid` |
| `get_patent_ids` | Patent landscape | `cid` |
| `get_bioassay_results` | Bioassay activity data | `cid`, `limit` |
| `get_3d_conformer` | 3D structure for binding analysis | `cid` |
| `get_pharmacology` | Pharmacological action data | `cid` |
| `get_synonyms` | All synonyms and identifiers | `cid` |
| `classify_compound` | Chemical classification hierarchy | `cid` |

### `mcp__fda__fda_info` (Regulatory & Safety Intelligence)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `lookup_drug` | Search drugs by name, adverse events, labels, recalls, shortages | `search_term`, `search_type`, `limit`, `count` |
| `lookup_device` | Search medical devices | `search_term`, `search_type`, `limit` |
| `search_orange_book` | Find brand/generic drug products by name | `drug_name`, `include_generics` |
| `get_therapeutic_equivalents` | Find AB-rated generic equivalents | `drug_name` |
| `get_patent_exclusivity` | Look up patents and exclusivity by NDA number | `nda_number` |
| `analyze_patent_cliff` | Forecast when a drug loses patent protection | `drug_name`, `years_ahead` |
| `search_purple_book` | Find biological products and biosimilars | `drug_name` |
| `get_biosimilar_interchangeability` | Check which biosimilars are interchangeable | `reference_product` |

### `mcp__ctgov__ctgov_info` (Clinical Trial Intelligence)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search` | Search clinical trials | `condition`, `intervention`, `phase`, `status`, `location`, `lead`, `ages`, `studyType`, `pageSize` |
| `get` | Get full trial details by NCT ID | `nctId` |
| `suggest` | Autocomplete terms | `input`, `dictionary` |
| `stats` | Trial statistics and counts | `condition`, `intervention` |

### `mcp__nlm__nlm_ct_codes` (Clinical Coding & Terminology)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `icd-10-cm` | Diagnosis codes | `terms`, `maxList` |
| `icd-11` | ICD-11 diagnosis codes (WHO 2023) | `terms`, `maxList` |
| `rx-terms` | Drug names with strengths/forms | `terms`, `maxList` |
| `loinc-questions` | Lab test codes (LOINC) | `terms`, `maxList` |
| `conditions` | Medical conditions with ICD mappings | `terms`, `maxList` |
| `npi-organizations` | Healthcare organization lookup | `terms`, `maxList` |
| `npi-individuals` | Provider lookup by name/specialty | `terms`, `maxList` |
| `hcpcs-LII` | Procedure/equipment codes | `terms`, `maxList` |
| `ncbi-genes` | Gene information (BRCA1, TP53) | `terms`, `maxList` |
| `major-surgeries-implants` | Surgical procedure codes | `terms`, `maxList` |
| `hpo-vocabulary` | Human Phenotype Ontology terms | `terms`, `maxList` |

### `mcp__depmap__depmap_data` (Multi-Omic Cancer Functional Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_gene_expression` | Cancer cell line expression data as additional transcriptomic layer | `gene`, `lineage`, `dataset` |
| `get_mutations` | Mutation profiles across cancer cell lines | `gene`, `lineage`, `dataset` |
| `get_copy_number` | Copy number alteration data across cancer lines | `gene`, `lineage`, `dataset` |
| `get_gene_dependency` | Functional dependency layer -- gene essentiality from CRISPR screens | `gene`, `lineage`, `dataset` |

**DepMap workflow:** Integrate DepMap expression, mutation, and copy number data as additional omic layers to complement patient-derived datasets. The dependency layer adds a unique functional dimension -- identifying which genomic/transcriptomic alterations actually drive cell viability -- that cannot be obtained from observational omics alone.

```
mcp__depmap__depmap_data(method: "get_gene_expression", gene: "TP53", lineage: "breast")
mcp__depmap__depmap_data(method: "get_mutations", gene: "BRCA1", lineage: "ovary")
mcp__depmap__depmap_data(method: "get_copy_number", gene: "MYC", lineage: "lung")
```

### `mcp__cbioportal__cbioportal_data` (Cancer Multi-Omic Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_studies` | Cancer cohort discovery across TCGA, MSK-IMPACT, and curated datasets | `keyword`, `cancer_type` |
| `get_molecular_profiles` | Available omics layers (mutations, CNA, mRNA, methylation) for a study | `study_id` |
| `get_mutations` | Somatic mutation data for cancer genomics characterization | `study_id`, `gene`, `sample_id` |
| `get_copy_number` | Copy number alteration data across cancer cohorts | `study_id`, `gene`, `profile_id` |
| `get_clinical_attributes` | Clinical outcomes and patient annotations (survival, stage, treatment) | `study_id`, `attribute_id` |

**cBioPortal workflow:** Integrate cBioPortal multi-omic cancer data (mutations, CNA, clinical) for disease characterization. Use `search_studies` to find relevant cancer cohorts, `get_molecular_profiles` to identify available omics layers, then pull mutation, copy number, and clinical data to complement patient-derived and DepMap datasets in the cross-layer concordance analysis.

```
mcp__cbioportal__cbioportal_data(method: "search_studies", cancer_type: "breast")
mcp__cbioportal__cbioportal_data(method: "get_molecular_profiles", study_id: "brca_tcga")
mcp__cbioportal__cbioportal_data(method: "get_mutations", study_id: "brca_tcga", gene: "TP53")
mcp__cbioportal__cbioportal_data(method: "get_copy_number", study_id: "brca_tcga", gene: "MYC")
mcp__cbioportal__cbioportal_data(method: "get_clinical_attributes", study_id: "brca_tcga")
```

---

## 9-Phase Multi-Omics Pipeline

### Phase 0: Disease Disambiguation

**MANDATORY first step.** Resolve the disease to canonical ontology IDs before any omics query. Always use underscore-format IDs (e.g., MONDO_0004975, EFO_0000311).

```
1. mcp__opentargets__opentargets_info(method: "search_diseases", query: "disease_name", size: 10)
   -> Get EFO disease ID (EFO_xxxxxxx)
   -> Confirm correct disease (check synonyms, parent terms, subtypes)

2. mcp__opentargets__opentargets_info(method: "get_disease_details", id: "EFO_xxxxxxx")
   -> Full disease ontology: EFO, MONDO, OMIM, Orphanet mappings
   -> Phenotypes, therapeutic areas, child diseases

3. mcp__nlm__nlm_ct_codes(method: "icd-10-cm", terms: "disease_name", maxList: 10)
   -> ICD-10-CM codes for clinical classification

4. mcp__nlm__nlm_ct_codes(method: "icd-11", terms: "disease_name", maxList: 10)
   -> ICD-11 codes (WHO 2023 classification)

5. mcp__nlm__nlm_ct_codes(method: "conditions", terms: "disease_name", maxList: 10)
   -> Medical conditions with ICD mappings and cross-references

6. mcp__nlm__nlm_ct_codes(method: "hpo-vocabulary", terms: "disease_name", maxList: 15)
   -> Human Phenotype Ontology terms (phenotypic features)

7. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "disease_name ontology classification molecular subtypes", num_results: 10)
   -> Literature on disease classification and molecular subtypes
```

**Critical:** If the disease name is ambiguous (e.g., "diabetes" could be T1D or T2D, "lymphoma" has dozens of subtypes), resolve to the most specific entity before proceeding. Record ALL canonical identifiers:
- EFO: EFO_xxxxxxx
- MONDO: MONDO_xxxxxxx (use underscore format)
- ICD-10: Xxx.x
- ICD-11: xx.xxxx
- OMIM: xxxxxx (if Mendelian component)
- Orphanet: ORPHA:xxxxx (if rare disease)

---

### Phase 1: Genomics Layer

Map the genetic architecture of the disease -- GWAS associations, somatic mutations, Mendelian variants, copy number alterations.

```
1. mcp__opentargets__opentargets_info(method: "get_disease_targets_summary", diseaseId: "EFO_xxxxxxx", minScore: 0.3, size: 100)
   -> All genetically associated targets, ranked by evidence score
   -> Filter for genetic_association and somatic_mutation data types

2. For top 20 targets:
   mcp__opentargets__opentargets_info(method: "get_target_disease_associations", targetId: "ENSG00000xxxxx", diseaseId: "EFO_xxxxxxx", size: 50)
   -> Evidence breakdown: genetic association, somatic mutation, known drug, literature

3. mcp__nlm__nlm_ct_codes(method: "ncbi-genes", terms: "top_gene_symbol", maxList: 5)
   -> Gene details, chromosomal location, RefSeq IDs

4. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "disease_name GWAS genome-wide association genetic risk loci", num_results: 20)
   -> Published GWAS studies, meta-analyses, fine-mapping studies

5. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "disease_name somatic mutation driver gene exome sequencing", num_results: 15)
   -> Somatic mutation landscape (especially for cancer)

6. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "disease_name copy number alteration amplification deletion", num_results: 10)
   -> Copy number variation studies
```

**Output:** Genomics layer card -- top genetic risk loci (GWAS), driver mutations (somatic), Mendelian genes, CNVs. Each gene tagged with evidence type.

### Phase 2: Transcriptomics Layer

Identify differentially expressed genes, expression signatures, and transcriptional programs associated with the disease.

```
1. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "disease_name RNA-seq transcriptome differentially expressed genes", num_results: 20)
   -> Transcriptomic profiling studies

2. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "disease_name gene expression signature microarray", num_results: 15)
   -> Gene expression signatures from microarray and RNA-seq

3. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "disease_name single-cell RNA-seq scRNA-seq cell type", num_results: 15)
   -> Single-cell transcriptomics revealing cell-type-specific changes

4. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "disease_name long non-coding RNA miRNA transcriptional regulation", num_results: 10)
   -> Non-coding RNA involvement

5. For top differentially expressed genes identified in literature:
   mcp__opentargets__opentargets_info(method: "search_targets", query: "GENE_SYMBOL", size: 5)
   -> Get Ensembl IDs
   mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   -> Expression patterns, tissue specificity, function

6. mcp__nlm__nlm_ct_codes(method: "loinc-questions", terms: "disease_name biomarker", maxList: 10)
   -> Clinical lab tests measuring expression-based biomarkers
```

**Output:** Transcriptomics layer card -- top DEGs (up/down), expression signatures, cell-type-specific programs, non-coding RNA regulators. Each gene tagged with study type and fold-change direction.

### Phase 3: Proteomics & Interactions Layer

Map the protein-level alterations and protein-protein interaction network relevant to the disease.

```
1. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "disease_name proteomics mass spectrometry protein expression", num_results: 20)
   -> Proteomics profiling studies

2. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "disease_name phosphoproteomics post-translational modification signaling", num_results: 15)
   -> Post-translational modification studies (phospho, ubiquitin, acetyl)

3. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "disease_name protein-protein interaction network interactome", num_results: 15)
   -> PPI network studies

4. For key disease proteins:
   mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   -> Protein interactions, subcellular location, protein class

5. mcp__drugbank__drugbank_info(method: "search_by_target", target: "disease_protein", limit: 20)
   -> Drugs targeting disease-associated proteins

6. mcp__drugbank__drugbank_info(method: "search_by_carrier", carrier: "disease_protein", limit: 10)
   -> Carrier protein relationships

7. mcp__drugbank__drugbank_info(method: "search_by_transporter", transporter: "disease_protein", limit: 10)
   -> Transporter protein relationships

8. mcp__pubchem__pubchem_info(method: "get_bioassay_results", cid: CID_NUMBER, limit: 50)
   -> Bioassay data for compounds targeting disease proteins
```

**Output:** Proteomics layer card -- differentially abundant proteins, PTM alterations, PPI network with hub genes identified (degree centrality > mean + 1 SD). Each protein tagged with detection method and study.

### Phase 4: Pathways & Networks Layer

Identify dysregulated pathways and construct pathway-level disease models.

```
1. mcp__opentargets__opentargets_info(method: "get_disease_targets_summary", diseaseId: "EFO_xxxxxxx", minScore: 0.5, size: 50)
   -> Extract Reactome pathway annotations from top disease targets

2. For top disease targets:
   mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   -> Reactome pathways, GO biological processes

3. mcp__drugbank__drugbank_info(method: "get_pathways", drugbank_id: "DBxxxxx")
   -> Metabolic/signaling pathway mapping for disease-relevant drugs

4. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "disease_name pathway signaling cascade dysregulated", num_results: 20)
   -> Pathway perturbation studies

5. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "disease_name network biology systems biology interactome topology", num_results: 15)
   -> Network-level disease models

6. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "disease_name metabolic pathway metabolomics", num_results: 10)
   -> Metabolic pathway alterations
```

**Output:** Pathway layer card -- dysregulated signaling pathways, metabolic alterations, pathway crosstalk, network topology metrics. Pathways ranked by number of disease genes they contain.

### Phase 5: Gene Ontology Layer

Systematic functional annotation of disease-associated genes across GO biological process, molecular function, and cellular component.

```
1. For all genes identified across Phases 1-4:
   mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   -> GO biological process, molecular function, cellular component annotations

2. Group genes by GO biological process:
   -> Identify enriched biological processes
   -> Flag processes with genes from multiple omics layers (cross-layer concordance)

3. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "disease_name gene ontology enrichment biological process", num_results: 10)
   -> Published GO enrichment analyses for this disease

4. mcp__nlm__nlm_ct_codes(method: "ncbi-genes", terms: "GENE_SYMBOL", maxList: 5)
   -> Gene function summaries and GO annotations from NCBI

5. mcp__pubchem__pubchem_info(method: "get_pharmacology", cid: CID_NUMBER)
   -> Pharmacological action data linking compounds to GO-annotated targets
```

**Output:** GO layer card -- enriched GO terms (BP, MF, CC), genes per term, cross-layer overlap per GO term. Highlight GO terms where genes from 3+ omics layers converge.

### Phase 6: Therapeutic Landscape Layer

Map the full therapeutic landscape -- approved drugs, clinical pipeline, druggable targets, and treatment gaps.

```
1. mcp__chembl__chembl_info(method: "drug_search", query: "disease_name", limit: 50)
   -> All drugs for this indication in ChEMBL

2. mcp__drugbank__drugbank_info(method: "search_by_category", category: "disease_therapeutic_category", limit: 30)
   -> Drugs by therapeutic category

3. For top disease targets:
   mcp__drugbank__drugbank_info(method: "search_by_target", target: "GENE_SYMBOL", limit: 20)
   -> Existing drugs modulating disease targets

4. For approved drugs:
   mcp__drugbank__drugbank_info(method: "get_drug_details", drugbank_id: "DBxxxxx")
   -> Full drug profile: mechanism, pharmacodynamics, targets

5. mcp__fda__fda_info(method: "lookup_drug", search_term: "disease_drug", search_type: "label", limit: 10)
   -> FDA label information, approved indications

6. mcp__fda__fda_info(method: "search_orange_book", drug_name: "drug_name")
   -> Approval status, generics availability

7. mcp__fda__fda_info(method: "search_purple_book", drug_name: "drug_name")
   -> Biological products and biosimilars

8. mcp__fda__fda_info(method: "lookup_drug", search_term: "disease_drug", search_type: "adverse_events", count: "patient.reaction.reactionmeddrapt.exact", limit: 20)
   -> Post-market safety signals

9. mcp__ctgov__ctgov_info(method: "search", condition: "disease_name", pageSize: 50)
   -> Active and completed clinical trials

10. mcp__ctgov__ctgov_info(method: "stats", condition: "disease_name")
    -> Trial statistics by phase, status, intervention type

11. mcp__ctgov__ctgov_info(method: "search", condition: "disease_name", status: "RECRUITING", pageSize: 30)
    -> Currently recruiting trials (active pipeline)

12. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "disease_name novel therapeutic target drug development pipeline", num_results: 15)
    -> Emerging therapeutic strategies
```

**Output:** Therapeutic landscape card -- approved drugs (by mechanism), clinical pipeline (by phase), druggable but untargeted genes, treatment gaps, emerging strategies.

### Phase 7: Multi-Omics Integration

Cross-reference all layers to identify high-confidence disease drivers through concordance analysis.

```
1. Build cross-layer gene matrix:
   - Row: each unique gene/protein identified across Phases 1-6
   - Columns: Genomics (Phase 1), Transcriptomics (Phase 2), Proteomics (Phase 3),
              Pathways (Phase 4), GO (Phase 5), Therapeutic (Phase 6)
   - Cell: present/absent + evidence type

2. Calculate cross-layer concordance:
   - Genes in 1 layer: low confidence (single-omics evidence)
   - Genes in 2 layers: moderate confidence (dual-omics evidence)
   - Genes in 3+ layers: HIGH CONFIDENCE disease drivers
   - Genes in 4+ layers: VERY HIGH CONFIDENCE -- core disease biology

3. For high-confidence genes (3+ layers):
   mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   -> Full target profile for each high-confidence driver

   mcp__chembl__chembl_info(method: "target_search", query: "GENE_SYMBOL", limit: 10)
   -> Druggability assessment

   mcp__chembl__chembl_info(method: "get_bioactivity", target_id: "CHEMBLxxxxx", limit: 50)
   -> Existing bioactivity data

4. Hub gene identification from PPI network (Phase 3):
   - Calculate degree centrality for each node
   - Hub gene threshold: degree centrality > mean + 1 SD
   - Cross-reference hubs with concordance score

5. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "disease_name multi-omics integration systems biology driver genes", num_results: 15)
   -> Published multi-omics integration studies for validation

6. mcp__pubmed__pubmed_articles(method: "search_advanced", term: "disease_name omics integration", start_date: "2022/01/01", num_results: 20)
   -> Recent multi-omics publications
```

**Output:** Integration matrix -- all genes ranked by cross-layer concordance score, hub gene status, druggability, and therapeutic relevance. Top 10 high-confidence disease drivers highlighted.

### Phase 8: Report Finalization

Compile all layers into a structured, confidence-scored report.

```
1. Calculate Multi-Omics Confidence Score (0-100):

   Data Completeness (0-30 points):
   - Genomics layer populated:        0-5 points
   - Transcriptomics layer populated:  0-5 points
   - Proteomics layer populated:       0-5 points
   - Pathways layer populated:         0-5 points
   - GO layer populated:               0-5 points
   - Therapeutic layer populated:      0-5 points

   Biological Insight Depth (0-40 points):
   - Cross-layer concordant genes identified:     0-10 points
   - Hub genes identified in PPI network:         0-10 points
   - Dysregulated pathways mapped:                0-10 points
   - Novel druggable targets identified:          0-10 points

   Evidence Quality (0-30 points):
   - T1 evidence (human/clinical) present:        0-10 points
   - T2 evidence (functional studies) present:    0-10 points
   - Multiple independent data sources used:      0-10 points

2. Generate report sections:
   - Executive Summary (confidence score, top findings)
   - Disease Identity (Phase 0)
   - Per-Layer Results (Phases 1-6)
   - Cross-Layer Concordance Analysis (Phase 7)
   - High-Confidence Disease Drivers (ranked list)
   - Therapeutic Opportunities (druggable gaps)
   - Evidence Quality Assessment
   - Completeness Audit

3. Assign evidence grades to all findings (T1-T4)
4. Flag data gaps and recommend follow-up experiments
```

---

## Evidence Grading System (T1-T4)

Assign an evidence grade to each major finding in the report.

| Grade | Evidence Type | Description | Examples |
|-------|-------------|-------------|----------|
| **T1 -- Human/Clinical** | Clinical data, approved drugs, positive trials, validated biomarkers | Highest confidence -- direct human evidence | Approved drug for indication; positive Phase 3 trial; validated clinical biomarker |
| **T2 -- Functional Studies** | CRISPR/siRNA, overexpression, cell-based assays, patient-derived models | Causal evidence in human cells/tissues | CRISPR screen hit; functional validation in patient-derived organoids |
| **T3 -- Association** | GWAS, differential expression, proteomic changes, pathway enrichment | Correlative evidence, not yet causally validated | GWAS risk locus; DEG in RNA-seq; enriched pathway in patient cohort |
| **T4 -- Computational** | Text mining, pathway inference, network prediction, animal model only | Hypothesis-generating | Network analysis prediction; text-mined co-occurrence; mouse model only |

**Grading rules:**
- Every factual claim in the report MUST carry a T-grade tag
- Multiple evidence types for the same finding upgrade the grade (T3 + T2 = report as T2)
- Absence of evidence is NOT T4 -- it is "No data" and must be explicitly stated
- Cross-layer concordance upgrades evidence: gene in 3+ omics layers with T3 evidence each -> report as T2

---

## Cross-Layer Gene Concordance Framework

### Concordance Score Calculation

```
For each gene identified across the pipeline:

Layer presence scoring:
  Genomics (Phase 1):        +1 if GWAS/somatic/Mendelian/CNV evidence
  Transcriptomics (Phase 2): +1 if differentially expressed (up or down)
  Proteomics (Phase 3):      +1 if differentially abundant or PTM-altered
  Pathways (Phase 4):        +1 if member of dysregulated pathway
  GO (Phase 5):              +1 if annotated to enriched GO term
  Therapeutic (Phase 6):     +1 if existing drug target or in clinical pipeline

Concordance classification:
  Score 1:   LOW confidence    -- single-omics evidence only
  Score 2:   MODERATE          -- dual-omics evidence
  Score 3:   HIGH              -- multi-omics concordant disease driver
  Score 4:   VERY HIGH         -- strong multi-omics driver
  Score 5-6: CORE BIOLOGY      -- central to disease mechanism across all layers
```

### Concordance Matrix Output Format

```
| Gene | Genomics | Transcriptomics | Proteomics | Pathways | GO | Therapeutic | Concordance | Hub Gene |
|------|----------|-----------------|------------|----------|-----|-------------|-------------|----------|
| TP53 | GWAS+somatic | Up (2.3x) | Phos-altered | p53 pathway | Apoptosis | Approved drugs | 6/6 CORE | Yes |
| BRCA1 | Mendelian | Down (0.4x) | Reduced | HR repair | DNA repair | Pipeline (Ph3) | 5/6 V.HIGH | Yes |
| CDK4 | Amplified | Up (3.1x) | -- | Cell cycle | Kinase activity | Approved (palbociclib) | 5/6 V.HIGH | No |
```

---

## Hub Gene Identification

### PPI Network Hub Analysis

```
Hub gene identification protocol:

1. Construct PPI network from Phase 3 interactome data
2. Calculate degree centrality for each node:
   Degree = number of direct interactors

3. Hub threshold:
   Hub gene = degree centrality > mean + 1 standard deviation

4. Hub classification:
   - Provincial hub: high degree within one module/pathway
   - Connector hub: high degree across multiple modules/pathways
   - Date hub: interactions change across conditions
   - Party hub: interactions are constitutive

5. Cross-reference hub status with concordance score:
   - Hub gene + concordance >= 3 = PRIORITY disease driver
   - Hub gene + concordance < 3 = structurally important but less disease-specific
   - Non-hub + concordance >= 3 = disease-specific but not structurally central

6. Druggability assessment for priority drivers:
   mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   -> Tractability (small molecule, antibody, other modalities)
   mcp__chembl__chembl_info(method: "get_bioactivity", target_id: "CHEMBLxxxxx", limit: 50)
   -> Existing chemical matter
```

---

## Therapeutic Landscape Mapping

### Drug Classification Framework

| Category | Definition | Source |
|----------|-----------|--------|
| **Approved** | FDA-approved drug for this indication | FDA Orange Book, DrugBank |
| **Approved (off-label)** | FDA-approved for other indication, evidence for this disease | DrugBank, PubMed, ClinicalTrials.gov |
| **Phase 3** | Active Phase 3 trials for this indication | ClinicalTrials.gov |
| **Phase 2** | Active Phase 2 trials | ClinicalTrials.gov |
| **Phase 1** | Active Phase 1 trials | ClinicalTrials.gov |
| **Preclinical** | Published preclinical data, no trials | PubMed, ChEMBL |
| **Druggable (untargeted)** | Target is druggable but no drug in development | Open Targets tractability, ChEMBL |
| **Undruggable (current)** | No known druggable pocket or modality | Open Targets tractability |

### Therapeutic Gap Analysis

```
1. Map all disease driver genes (concordance >= 3) to therapeutic categories above
2. Identify GAPS:
   - High-confidence drivers with NO approved drug = therapeutic opportunity
   - High-confidence drivers with Phase 1/2 only = emerging pipeline
   - Hub genes that are druggable but untargeted = PRIORITY gaps
3. For each gap:
   mcp__chembl__chembl_info(method: "target_search", query: "GENE_SYMBOL", limit: 10)
   -> Any chemical starting points?
   mcp__pubchem__pubchem_info(method: "search_compounds", query: "GENE_SYMBOL inhibitor", search_type: "name")
   -> Chemical probes available?
   mcp__pubchem__pubchem_info(method: "get_bioassay_results", cid: CID_NUMBER, limit: 30)
   -> Bioassay data for available compounds?
```

---

## Disease Disambiguation Protocol

**Always Phase 0 -- never skip.** Disease disambiguation prevents catastrophic pipeline errors from querying the wrong disease entity.

### Common Disambiguation Challenges

| Input | Ambiguity | Resolution |
|-------|-----------|------------|
| "Diabetes" | Type 1 vs Type 2 vs gestational vs MODY | Clarify subtype; default to T2D (MONDO_0005148) if unspecified |
| "Lymphoma" | Hodgkin vs NHL vs DLBCL vs FL vs MCL | Clarify histological subtype |
| "Breast cancer" | ER+ vs HER2+ vs TNBC vs lobular vs ductal | Clarify molecular subtype |
| "Alzheimer's" | Early-onset (familial) vs late-onset (sporadic) | MONDO_0004975 for general; specify if familial |
| "Arthritis" | Rheumatoid vs osteo vs psoriatic vs juvenile | Clarify type; vastly different molecular biology |

### ID Format Rules

```
ALWAYS use underscore format for ontology IDs:
  CORRECT: MONDO_0004975
  WRONG:   MONDO:0004975

  CORRECT: EFO_0000311
  WRONG:   EFO:0000311

Reason: MCP tool parameters require underscore format for disease IDs.
```

---

## Completeness Audit Checklist

**MANDATORY at the end of every multi-omics characterization report.** Every phase must meet minimum data requirements.

| Phase | Minimum Requirement | Pass/Fail Criteria |
|-------|-------------------|-------------------|
| **Phase 0: Disambiguation** | Disease resolved to EFO + MONDO + ICD-10 IDs | FAIL if disease ID not confirmed |
| **Phase 1: Genomics** | Top 10 genetically associated genes listed with evidence type | FAIL if no genetic evidence queried |
| **Phase 2: Transcriptomics** | DEG direction (up/down) documented for top genes, literature cited | FAIL if no transcriptomic data searched |
| **Phase 3: Proteomics** | Protein-level changes documented, PPI network queried | FAIL if proteomics not searched |
| **Phase 4: Pathways** | At least 3 dysregulated pathways identified | FAIL if no pathway data and no fallback attempted |
| **Phase 5: GO** | GO enrichment across BP, MF, CC assessed | FAIL if GO annotations not queried |
| **Phase 6: Therapeutic** | Approved drugs listed, trial count provided, pipeline mapped | FAIL if DrugBank and ClinicalTrials.gov not both queried |
| **Phase 7: Integration** | Cross-layer concordance matrix built, high-confidence drivers listed | FAIL if no concordance analysis performed |
| **Phase 8: Report** | Confidence score calculated, all findings T-graded | FAIL if confidence score missing |

**Audit output format:**

```
COMPLETENESS AUDIT
==================
Phase 0 — Disambiguation:     [PASS/FAIL] — [note]
Phase 1 — Genomics:           [PASS/FAIL] — [note]
Phase 2 — Transcriptomics:    [PASS/FAIL] — [note]
Phase 3 — Proteomics:         [PASS/FAIL] — [note]
Phase 4 — Pathways:           [PASS/FAIL] — [note]
Phase 5 — Gene Ontology:      [PASS/FAIL] — [note]
Phase 6 — Therapeutic:        [PASS/FAIL] — [note]
Phase 7 — Integration:        [PASS/FAIL] — [note]
Phase 8 — Report:             [PASS/FAIL] — [note]

Multi-Omics Confidence Score: [XX/100]
  Data Completeness:      [XX/30]
  Biological Insight:     [XX/40]
  Evidence Quality:       [XX/30]

Overall: [X/9 PASS] — [COMPLETE / INCOMPLETE — requires Phase X, Y remediation]
```

---

## Fallback Chains

When primary tools fail or return no data, use these documented alternatives.

| Primary Source | If it fails... | Fallback 1 | Fallback 2 |
|---------------|---------------|------------|------------|
| Open Targets `get_disease_targets_summary` | Disease not in Open Targets | PubMed "disease_name genetic association" + NLM `conditions` | ChEMBL `drug_search` for indication |
| Open Targets `get_target_details` | Target not in Open Targets | PubMed review search + NLM `ncbi-genes` | ChEMBL `target_search` |
| ChEMBL `drug_search` | No drugs found | DrugBank `search_by_category` + FDA `lookup_drug` | PubMed "disease_name treatment drug" |
| DrugBank `get_pathways` | No pathway data | Open Targets Reactome pathways | PubMed "disease_name pathway signaling" |
| PubMed transcriptomics search | No studies found | PubMed "disease_name gene expression" (broader) | Open Targets expression data |
| PubMed proteomics search | No studies found | PubMed "disease_name protein biomarker" (broader) | DrugBank target data |
| ClinicalTrials.gov `search` | No trials | FDA `lookup_drug` for approved drugs | PubMed "disease_name clinical trial" |
| FDA `lookup_drug` | No FDA data | DrugBank `get_drug_details` | ClinicalTrials.gov `search` |
| NLM `hpo-vocabulary` | No HPO terms | PubMed "disease_name phenotype clinical features" | Open Targets `get_disease_details` |

**Fallback rules:**
- Always attempt at least one fallback before marking a phase as "No data available"
- Document which fallback was used in the report
- If all fallbacks fail, record: "No data from [Primary], [Fallback 1], [Fallback 2]. Phase scored as empty."

---

## Complete Workflow Example

### Multi-Omic Characterization of Parkinson's Disease

```
PHASE 0 — DISEASE DISAMBIGUATION:
mcp__opentargets__opentargets_info(method: "search_diseases", query: "Parkinson's disease", size: 10)
-> EFO_0002508 (Parkinson disease)
mcp__opentargets__opentargets_info(method: "get_disease_details", id: "EFO_0002508")
-> MONDO_0005180, ICD-10: G20, Orphanet: ORPHA:411602 (early-onset)
mcp__nlm__nlm_ct_codes(method: "icd-10-cm", terms: "Parkinson", maxList: 5)
-> G20 (Parkinson's disease), G21 (secondary parkinsonism)

PHASE 1 — GENOMICS:
mcp__opentargets__opentargets_info(method: "get_disease_targets_summary", diseaseId: "EFO_0002508", minScore: 0.3, size: 100)
-> Top genetic targets: SNCA (0.95), LRRK2 (0.93), PARK7 (0.88), PINK1 (0.85), PRKN (0.82), GBA1 (0.79)
-> GWAS risk loci: 90+ identified in meta-analyses
mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "Parkinson disease GWAS genome-wide risk loci", num_results: 20)
-> Nalls et al. 2019 meta-GWAS: 90 risk variants

PHASE 2 — TRANSCRIPTOMICS:
mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "Parkinson disease RNA-seq transcriptome substantia nigra", num_results: 20)
-> DEGs: SNCA up, TH down, DDC down in SN; mitochondrial genes down
-> scRNA-seq: dopaminergic neuron-specific transcriptional programs
mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "Parkinson disease single-cell RNA-seq dopaminergic neurons", num_results: 15)
-> Cell-type-specific vulnerability signatures

PHASE 3 — PROTEOMICS:
mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "Parkinson disease proteomics alpha-synuclein aggregation", num_results: 20)
-> Alpha-synuclein aggregation, ubiquitin-proteasome dysfunction
-> CSF proteomics: biomarker panels (alpha-synuclein, DJ-1, tau)
Hub genes (PPI): SNCA, LRRK2, PARK7, PINK1, UBB, HSPA5

PHASE 4 — PATHWAYS:
-> Dysregulated: mitochondrial complex I, autophagy-lysosome, ubiquitin-proteasome,
   dopamine metabolism, neuroinflammation (NF-kB, TNF), calcium signaling
mcp__drugbank__drugbank_info(method: "get_pathways", drugbank_id: "DB00190") [levodopa]
-> Dopamine biosynthesis pathway

PHASE 5 — GENE ONTOLOGY:
-> Enriched BP: mitochondrial organization, autophagy, protein folding,
   dopamine biosynthetic process, response to oxidative stress
-> Enriched CC: mitochondrion, lysosome, synapse, Lewy body
-> Enriched MF: protein kinase activity, ubiquitin-protein ligase activity

PHASE 6 — THERAPEUTIC LANDSCAPE:
mcp__drugbank__drugbank_info(method: "search_by_category", category: "anti-Parkinson", limit: 30)
-> Approved: levodopa/carbidopa, pramipexole, ropinirole, rasagiline, entacapone, amantadine
mcp__ctgov__ctgov_info(method: "stats", condition: "Parkinson disease")
-> >3000 trials; Phase 3: LRRK2 inhibitors, GBA modulators, alpha-synuclein antibodies

PHASE 7 — INTEGRATION (CONCORDANCE MATRIX):
| Gene | Genomics | Transcriptomics | Proteomics | Pathways | GO | Therapeutic | Score |
|------|----------|-----------------|------------|----------|-----|-------------|-------|
| SNCA | Mendelian+GWAS | Up (SN) | Aggregated | Autophagy | Protein folding | Pipeline (Ph2) | 6/6 CORE |
| LRRK2 | Mendelian+GWAS | Altered | Kinase active | Autophagy | Kinase activity | Pipeline (Ph3) | 6/6 CORE |
| PINK1 | Mendelian | Down | Reduced | Mitophagy | Kinase activity | Preclinical | 5/6 V.HIGH |
| GBA1 | Risk variant | Down | Reduced | Lysosome | Hydrolase | Pipeline (Ph2) | 5/6 V.HIGH |
| PARK7 | Mendelian | Down | Oxidized | Oxidative stress | Oxidoreductase | Preclinical | 5/6 V.HIGH |

PHASE 8 — REPORT:
Multi-Omics Confidence Score: 87/100
  Data Completeness: 28/30 (all layers populated, proteomics slightly sparse)
  Biological Insight: 35/40 (strong concordance, clear hub genes, pathway convergence)
  Evidence Quality: 24/30 (T1 evidence for genetics and approved drugs, T2 for functional)

COMPLETENESS AUDIT: 9/9 PASS — COMPLETE
```

---

## Multi-Agent Workflow Examples

**"Characterize the multi-omics landscape of Alzheimer's disease"**
1. Multi-Omic Disease Characterization -> 9-phase pipeline: disease disambiguation, genomics through integration, confidence-scored report
2. Disease Research -> Deep epidemiology, clinical presentation, subtypes
3. Systems Biology -> Network topology of dysregulated pathways, pathway crosstalk analysis
4. Gene Enrichment -> Formal ORA/GSEA on the concordant gene set across GO/KEGG/Reactome

**"Identify new drug targets for TNBC using multi-omics"**
1. Multi-Omic Disease Characterization -> Full pipeline with emphasis on Phase 7 (concordance) to find high-confidence drivers
2. Drug Target Analyst -> Druggability assessment, SAR, bioactivity for top concordant targets
3. Precision Medicine Stratifier -> Patient stratification by molecular subtype, pharmacogenomic modifiers
4. Target Research -> Deep 9-path profiling for the top 3 novel targets

**"Compare multi-omics profiles of Crohn's disease vs ulcerative colitis"**
1. Multi-Omic Disease Characterization -> Run full pipeline for EACH disease separately
2. Systems Biology -> Compare dysregulated pathway networks between the two diseases
3. Gene Enrichment -> Differential enrichment analysis: shared vs disease-specific pathways
4. Drug Target Analyst -> Identify shared druggable targets (pan-IBD) vs subtype-specific targets

**"Build a multi-omics report for rare disease X with limited data"**
1. Multi-Omic Disease Characterization -> 9-phase pipeline; expect sparse data in Phases 2-3; fallback chains critical
2. Disease Research -> Orphanet and OMIM deep dive, case reports, natural history
3. Target Research -> Exhaustive profiling of the few known disease genes
4. Precision Medicine Stratifier -> Genetic risk scoring even with limited cohort data

## Completeness Checklist

- [ ] Disease disambiguated to canonical ontology IDs (EFO, MONDO, ICD-10)
- [ ] Genomics layer populated with top genetically associated genes and evidence types
- [ ] Transcriptomics layer includes DEGs with direction (up/down) and literature citations
- [ ] Proteomics layer documents protein-level changes and PPI network hub genes
- [ ] Pathway layer identifies at least 3 dysregulated pathways with gene membership
- [ ] GO enrichment assessed across BP, MF, and CC categories
- [ ] Therapeutic landscape maps approved drugs, clinical pipeline, and druggable gaps
- [ ] Cross-layer concordance matrix built with confidence scores for all genes
- [ ] All findings assigned evidence grades (T1-T4)
- [ ] Multi-Omics Confidence Score calculated (0-100) with subscores
- [ ] Completeness audit performed (9/9 phases assessed as PASS/FAIL)
