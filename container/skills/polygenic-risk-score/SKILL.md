---
name: polygenic-risk-score
description: Polygenic risk score construction and interpretation specialist. Builds and interprets polygenic risk scores for complex diseases using GWAS summary statistics. Calculates genetic predisposition profiles with population percentile interpretation. Use when user mentions polygenic risk score, PRS, genetic risk score, GRS, genome-wide risk, genetic predisposition, risk percentile, SNP-based risk, GWAS summary statistics, effect size, beta coefficient, odds ratio, allele dosage, risk allele, weighted score, population percentile, genetic liability, heritability, common variant risk, multi-SNP risk, or cumulative genetic risk.
---

# Polygenic Risk Score

Builds and interprets polygenic risk scores for complex diseases using GWAS summary statistics. Calculates genetic predisposition profiles by aggregating effect sizes across genome-wide significant variants, with population percentile interpretation and clinical context. Uses Open Targets for GWAS associations and target-disease evidence, PubMed for GWAS literature and PRS validation studies, NLM for SNP annotation and clinical coding, DrugBank for pharmacogenomic context and pathway mapping, and ChEMBL for compound pharmacology linked to genetically implicated targets.

## Report-First Workflow

1. **Create report file immediately**: `[trait]_polygenic_risk_score_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- SNP-level variant annotation and fine-mapping → use `gwas-snp-interpretation`
- Trait-to-gene mapping and colocalization analysis → use `gwas-trait-to-gene`
- Patient stratification integrating clinical and genomic data → use `precision-medicine-stratifier`
- Pharmacogenomic dosing guidance from risk variants → use `pharmacogenomics-specialist`
- Disease biology and therapeutic landscape overview → use `disease-research`
- GWAS study discovery and exploration → use `gwas-study-explorer`

## Available MCP Tools

### `mcp__opentargets__opentargets_info` (PRIMARY -- GWAS Data & Target-Disease Associations)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_targets` | Search targets by gene symbol/name | `query`, `size` |
| `search_diseases` | Search diseases by name/synonym | `query`, `size` |
| `get_target_disease_associations` | Evidence-scored target-disease links with genetic evidence | `targetId` (Ensembl ID), `diseaseId` (EFO ID), `minScore`, `size` |
| `get_disease_targets_summary` | All targets for a disease ranked by evidence | `diseaseId`, `minScore`, `size` |
| `get_target_details` | Full target info (function, pathways, tractability) | `id` (Ensembl ID) |
| `get_disease_details` | Full disease info (ontology, phenotypes) | `id` (EFO ID) |

### `mcp__pubmed__pubmed_articles` (PRS Literature & Validation Studies)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Quick keyword search | `keywords`, `num_results` |
| `search_advanced` | Filtered search | `term`, `journal`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Full article details | `pmid` |

### `mcp__nlm__nlm_ct_codes` (SNP Annotation & Clinical Coding)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `ncbi_genes` | Gene info by symbol or ID (aliases, chromosome, summary) | `query`, `limit` |
| `ncbi_snps` | SNP details by rsID (alleles, position, MAF, clinical significance) | `query`, `limit` |
| `ncbi_clinvar` | ClinVar variant-disease annotations | `query`, `limit` |
| `conditions` | Search conditions/diseases | `query`, `limit` |
| `hpo_vocabulary` | Human Phenotype Ontology terms | `query`, `limit` |
| `rxnorm_drugs` | Drug names and RxNorm codes | `query`, `limit` |
| `icd10_codes` | ICD-10 diagnosis codes | `query`, `limit` |
| `icd10pcs_codes` | ICD-10-PCS procedure codes | `query`, `limit` |
| `snomed_codes` | SNOMED CT concept lookup | `query`, `limit` |
| `loinc_codes` | LOINC laboratory test codes | `query`, `limit` |
| `cpt_codes` | CPT procedure codes | `query`, `limit` |

### `mcp__drugbank__drugbank_info` (Pharmacogenomic Context)

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

### `mcp__chembl__chembl_info` (Compound Pharmacology for Genetically Implicated Targets)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `compound_search` | Search molecules by name/SMILES/ID | `query`, `limit` |
| `target_search` | Search biological targets | `query`, `limit` |
| `get_bioactivity` | Compound-target activity data (IC50, Ki, EC50) | `chembl_id`, `target_id`, `limit` |
| `get_mechanism` | Mechanism of action | `chembl_id` |
| `drug_search` | Search drugs by indication or name | `query`, `limit` |
| `get_admet` | ADMET/drug-likeness properties | `chembl_id` |

### `mcp__gnomad__gnomad_data` (Population Frequencies for PRS Calibration & Equity)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_variant` | Variant allele frequency across populations — use for PRS weight calibration against population-specific AF | `variant_id`, `dataset` |
| `get_population_frequencies` | Ancestry-specific allele frequencies (AFR, AMR, EAS, SAS, NFE, etc.) — CRITICAL for assessing PRS transferability across ancestries | `variant_id`, `dataset` |
| `batch_gene_constraint` | Gene-level constraint metrics (pLI, LOEUF) for multiple genes — provides gene-level context for interpreting PRS loci biological significance | `gene_ids` |

#### gnomAD Workflow: PRS Portability and Ancestry Equity Assessment

```
Use gnomAD population-specific frequencies to assess PRS portability
across ancestries — major issue in PRS equity:

1. mcp__gnomad__gnomad_data(method: "get_variant", variant_id: "1-12345-A-G", dataset: "gnomad_r4")
   -> Overall allele frequency for PRS weight calibration
   -> Compare discovery GWAS AF with gnomAD AF to detect winner's curse inflation

2. mcp__gnomad__gnomad_data(method: "get_population_frequencies", variant_id: "1-12345-A-G", dataset: "gnomad_r4")
   -> Ancestry-specific AF: AFR, AMR, EAS, SAS, NFE, ASJ, FIN, MID
   -> Flag PRS variants with large AF divergence across populations (>2-fold)
   -> Variants monomorphic or ultra-rare in non-European populations will not contribute to PRS in those groups
   -> Quantify expected PRS accuracy loss: large AF differences correlate with reduced transferability

3. mcp__gnomad__gnomad_data(method: "batch_gene_constraint", gene_ids: ["ENSG00000xxxxx", "ENSG00000yyyyy"])
   -> Constraint context for PRS loci — highly constrained genes (LOEUF < 0.35) suggest larger biological effects
   -> Helps prioritize which PRS variants are most likely functionally relevant vs. tagging signals

4. Equity assessment checklist:
   -> Calculate proportion of PRS variants with AF data in each gnomAD population
   -> Identify variants absent or rare (<0.1%) in specific populations
   -> Report predicted PRS accuracy reduction per ancestry based on AF divergence
   -> Recommend multi-ancestry PRS methods (PRS-CSx) when >20% of variants show >2-fold AF difference
```

---

## PRS Construction Pipeline

### PRS Formula

```
PRS = SUM(dosage_i * effect_size_i) for i = 1 to N SNPs

Where:
- dosage_i = number of risk alleles (0, 1, or 2) at SNP i
- effect_size_i = beta (continuous traits) or ln(OR) (binary traits) from GWAS
- Standardized PRS z-score = (PRS_individual - PRS_population_mean) / PRS_population_SD
```

### Step 1: Trait Selection and Disease Characterization

```
1. mcp__opentargets__opentargets_info(method: "search_diseases", query: "disease_or_trait_name")
   -> Get EFO disease ID and verify trait ontology

2. mcp__opentargets__opentargets_info(method: "get_disease_details", id: "EFO_xxxxxxx")
   -> Full disease profile: phenotypes, therapeutic areas, ontology hierarchy

3. mcp__nlm__nlm_ct_codes(method: "conditions", query: "disease_name")
   -> Standardized condition names, synonyms

4. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "disease_name polygenic risk score GWAS heritability", num_results: 15)
   -> Published PRS studies, reported heritability estimates, validated PRS performance (AUC, R-squared)
```

### Step 2: Association Collection (p < 5x10^-8)

```
1. mcp__opentargets__opentargets_info(method: "get_disease_targets_summary", diseaseId: "EFO_xxxxxxx", minScore: 0.3, size: 100)
   -> All genetically associated targets ranked by evidence score (includes GWAS loci)

2. For each top target:
   mcp__opentargets__opentargets_info(method: "get_target_disease_associations", targetId: "ENSG00000xxxxx", diseaseId: "EFO_xxxxxxx")
   -> Evidence breakdown: genetic association score, GWAS studies, effect sizes

3. mcp__pubmed__pubmed_articles(method: "search_advanced", term: "disease_name GWAS genome-wide significant", journal: "", num_results: 20)
   -> Source GWAS publications reporting genome-wide significant associations

4. mcp__pubmed__pubmed_articles(method: "get_article_metadata", pmid: "GWAS_PMID")
   -> Full article details for effect size extraction from supplementary tables
```

### Step 3: Effect Size Extraction

```
For each genome-wide significant variant:

1. Extract effect sizes from GWAS summary statistics:
   - Continuous traits: use beta coefficients (per-allele effect on trait units)
   - Binary traits: use ln(OR) — natural log of odds ratio
   - Confirm effect allele orientation (risk allele = allele increasing trait/risk)

2. mcp__nlm__nlm_ct_codes(method: "ncbi_snps", query: "rs12345678")
   -> Verify variant position, alleles, strand orientation
   -> Confirm reference vs alternate allele to align effect direction

3. Record for each SNP:
   -> rsID, chromosome, position, effect allele, other allele, effect size (beta or ln(OR)), p-value, standard error
```

### Step 4: SNP Filtering and Quality Control

```
Apply inclusion/exclusion criteria:

1. Minor Allele Frequency (MAF):
   mcp__nlm__nlm_ct_codes(method: "ncbi_snps", query: "rs12345678")
   -> Retain variants with MAF > 0.01 (exclude rare variants with unstable effect estimates)

2. Hardy-Weinberg Equilibrium (HWE):
   -> Exclude variants with HWE p < 1x10^-6 (indicates genotyping error)

3. Strand Ambiguity:
   -> Remove A/T and C/G SNPs (ambiguous strand alignment between studies)
   -> Unless frequency-based strand resolution is possible (MAF < 0.4)

4. Linkage Disequilibrium (LD) Pruning:
   -> Clump variants at r-squared < 0.1 within 250kb windows
   -> Retain variant with smallest p-value in each LD block
   -> Prevents double-counting correlated signals

5. Genome-wide significance filter:
   -> Standard PRS: retain only p < 5x10^-8 (most conservative)
   -> Extended PRS: consider p-value thresholds (pT) at multiple levels for optimal prediction
```

### Step 5: Score Calculation

```
1. For each individual genotype:
   PRS = SUM(dosage_i * effect_size_i) across all retained SNPs

2. Standardize to population z-scores:
   z_PRS = (PRS_raw - mean_PRS) / SD_PRS

3. Convert to percentile:
   Percentile = Phi(z_PRS) * 100
   Where Phi is the standard normal cumulative distribution function
```

### Step 6: Risk Interpretation via Percentiles

```
1. Assign risk category based on percentile:
   (See Risk Category Framework below)

2. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "disease_name polygenic risk score percentile clinical utility", num_results: 10)
   -> Published risk stratification studies with calibrated thresholds

3. Calculate absolute risk:
   Absolute_risk = baseline_prevalence * OR_per_SD^z_PRS
   -> Contextualize relative risk within population prevalence

4. Integrate clinical context:
   mcp__nlm__nlm_ct_codes(method: "icd10_codes", query: "disease_name")
   -> ICD-10 code for clinical documentation

   mcp__nlm__nlm_ct_codes(method: "hpo_vocabulary", query: "disease_phenotype")
   -> HPO terms for phenotype-genotype correlation
```

---

## Risk Category Framework

### PRS Percentile Risk Categories

| Percentile | Category | Interpretation | Clinical Action |
|-----------|----------|----------------|-----------------|
| **< 20th** | Low | Genetic predisposition below population average | Standard screening intervals; reassurance |
| **20th-80th** | Average | Typical population genetic risk | Standard of care; age-appropriate screening |
| **80th-95th** | Elevated | Above-average genetic predisposition | Enhanced screening; lifestyle modification counseling |
| **> 95th** | High | Top 5% genetic risk; substantially elevated predisposition | Intensified screening; specialist referral; consider chemoprevention |

### Relative Risk by PRS Category (Typical for Common Diseases)

| PRS Percentile | Approximate OR vs Population Average | Context |
|---------------|--------------------------------------|---------|
| **Top 1%** | 3-5x | Risk comparable to some monogenic conditions |
| **Top 5%** | 2-3x | Clinically actionable for many diseases |
| **Top 10%** | 1.5-2.5x | Moderate elevation; screening benefit |
| **Top 25%** | 1.2-1.5x | Modest elevation; population-level impact |
| **Bottom 25%** | 0.5-0.8x | Below-average risk |

---

## Evidence Grading Framework

### PRS Evidence Tiers

| Tier | Evidence Level | Criteria | Clinical Readiness |
|------|---------------|----------|-------------------|
| **T1** | Validated clinical utility | Prospective trials showing PRS-guided intervention improves outcomes | Ready for clinical implementation |
| **T2** | Demonstrated predictive value | Large cohort validation with significant AUC improvement over clinical models | Suitable for clinical decision support |
| **T3** | Replicated association | PRS association replicated in independent cohorts across ancestries | Research use; pilot clinical programs |
| **T4** | Discovery-phase | Single GWAS or limited replication; narrow ancestry representation | Research only; not for clinical decisions |

### PRS Performance Metrics

| Metric | Good | Moderate | Poor |
|--------|------|----------|------|
| **AUC improvement** | > 0.05 over clinical model | 0.02-0.05 | < 0.02 |
| **Variance explained (R-squared)** | > 10% | 5-10% | < 5% |
| **OR top vs bottom decile** | > 3.0 | 2.0-3.0 | < 2.0 |
| **Calibration** | Hosmer-Lemeshow p > 0.05 | Marginal | Poor fit |

---

## Ancestry Considerations

### Population Transferability

```
Key principles:
- Most GWAS conducted in European-ancestry populations
- PRS trained in Europeans has REDUCED accuracy in non-European populations
- Accuracy reduction: ~50-80% in African ancestry, ~30-50% in East Asian, ~20-40% in South Asian
- Causes: differences in LD structure, allele frequencies, causal variant tagging, gene-environment interactions

Assessment workflow:
1. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "disease_name polygenic risk score ancestry transferability multi-ethnic", num_results: 15)
   -> Published cross-ancestry PRS validation studies

2. Report ancestry of discovery GWAS and any validation cohorts
   -> Flag if PRS derived exclusively from European GWAS

3. Multi-ancestry PRS methods to consider:
   -> PRS-CSx: cross-population PRS using coupled continuous shrinkage
   -> Multi-ancestry meta-analysis GWAS for improved variant discovery
   -> Local ancestry-aware scoring for admixed populations
```

### Ancestry Reporting Requirements

```
Always report:
- Discovery GWAS ancestry composition
- Validation cohort ancestry (if available)
- Known transferability evidence for this trait
- Limitations disclaimer for non-represented populations
```

---

## Limitations and Caveats

### Known PRS Limitations

```
Statistical limitations:
- Winner's curse: effect sizes overestimated in discovery GWAS; use independent validation
- LD confounding: correlated variants inflate apparent signal; proper LD pruning essential
- Heritability gap: PRS typically captures 5-30% of trait heritability; substantial "missing heritability"
- Population stratification: uncorrected ancestry differences create spurious associations

Biological limitations:
- Environmental factors comprise 50%+ of risk for most complex diseases
- Gene-environment interactions not captured by PRS
- Rare variants (MAF < 0.01) excluded from standard PRS
- Epigenetic and somatic variation not reflected
- PRS assumes additive genetic architecture; ignores epistasis

Clinical limitations:
- Population-level prediction =/= individual prediction
- PRS does not diagnose disease; it quantifies genetic predisposition
- Absolute risk requires integration with clinical risk factors (age, sex, family history, biomarkers)
- Not validated for clinical use in most diseases (T3-T4 evidence)
- Ancestry bias reduces utility in non-European populations
```

---

## Clinical Interpretation Framework

### Absolute vs Relative Risk

```
Relative risk (OR or HR):
- Compares individual's risk to population average
- Useful for risk stratification
- Example: OR = 2.5 means 2.5x higher odds than average

Absolute risk:
- Individual's actual probability of developing disease over a time period
- Requires baseline population incidence/prevalence
- Example: 10-year absolute risk = 15% (with PRS in top 5%)

Key distinction:
- High relative risk + low baseline prevalence = modest absolute risk
- Example: OR = 3.0 for a disease with 1% prevalence -> absolute risk ~3%
- Always present BOTH relative and absolute risk to avoid misinterpretation
```

### Integrated Risk Assessment

```
1. Calculate PRS percentile and risk category

2. Layer clinical risk factors:
   mcp__nlm__nlm_ct_codes(method: "conditions", query: "comorbid_condition")
   -> Identify comorbidities that modify baseline risk

3. Layer pharmacogenomic context:
   mcp__drugbank__drugbank_info(method: "search_by_target", target: "PRS_implicated_gene")
   -> Drugs targeting genetically implicated pathways (preventive pharmacology)

   mcp__drugbank__drugbank_info(method: "get_drug_details", drugbank_id: "DBxxxxx")
   -> Pharmacogenomic dosing implications for risk-reduction therapies

4. Literature-based calibration:
   mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "disease_name absolute risk polygenic score calibration", num_results: 10)
   -> Published absolute risk models incorporating PRS
```

---

## SNP Annotation Workflow for PRS Variants

### Characterizing Individual PRS Variants

```
1. mcp__nlm__nlm_ct_codes(method: "ncbi_snps", query: "rs12345678")
   -> Alleles, position, MAF, functional consequence, clinical significance

2. mcp__nlm__nlm_ct_codes(method: "ncbi_genes", query: "NEAREST_GENE")
   -> Gene context, function, pathway involvement

3. mcp__nlm__nlm_ct_codes(method: "ncbi_clinvar", query: "rs12345678")
   -> ClinVar pathogenicity (if annotated); most PRS variants are common and benign individually

4. mcp__opentargets__opentargets_info(method: "search_targets", query: "GENE_SYMBOL")
   -> Get Ensembl ID for target-disease evidence lookup

5. mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   -> Target function, tractability, pathway membership

6. mcp__chembl__chembl_info(method: "target_search", query: "GENE_SYMBOL")
   -> Existing compounds targeting this gene product (therapeutic opportunities)
```

---

## Pharmacogenomic Integration

### PRS-Informed Treatment Selection

```
1. Identify genetically implicated targets from PRS loci:
   mcp__opentargets__opentargets_info(method: "get_disease_targets_summary", diseaseId: "EFO_xxxxxxx", minScore: 0.5, size: 30)
   -> Targets with strong genetic evidence

2. Find drugs for genetically supported targets:
   mcp__drugbank__drugbank_info(method: "search_by_target", target: "PRS_gene_target")
   -> Approved/investigational drugs acting on PRS-implicated pathways

3. Check pharmacogenomic variants in PRS-relevant genes:
   mcp__drugbank__drugbank_info(method: "get_drug_details", drugbank_id: "DBxxxxx")
   -> Pharmacogenomic interactions, dosing guidance

4. Assess compound pharmacology:
   mcp__chembl__chembl_info(method: "get_bioactivity", chembl_id: "CHEMBLxxxxx", target_id: "CHEMBLxxxxx", limit: 30)
   -> Bioactivity data for compounds targeting PRS-implicated proteins

5. mcp__chembl__chembl_info(method: "get_mechanism", chembl_id: "CHEMBLxxxxx")
   -> Mechanism of action for risk-reduction candidate drugs

6. mcp__drugbank__drugbank_info(method: "get_pathways", drugbank_id: "DBxxxxx")
   -> Pathway context for genetically implicated drug targets
```

---

## Multi-Agent Workflow Examples

**"Build a polygenic risk score for type 2 diabetes and interpret clinical implications"**
1. Polygenic Risk Score -> Collect GWAS loci, extract effect sizes, filter SNPs, calculate PRS, assign risk percentile
2. GWAS SNP Interpretation -> Annotate each PRS variant with functional consequence, fine-mapping evidence, L2G scores
3. Precision Medicine Stratifier -> Integrate PRS with clinical risk factors (BMI, HbA1c, family history) for composite risk tier
4. Disease Research -> Disease biology, therapeutic landscape, emerging targets

**"Assess genetic predisposition to coronary artery disease with pharmacogenomic context"**
1. Polygenic Risk Score -> CAD PRS construction from CARDIoGRAMplusC4D GWAS, percentile calculation
2. Pharmacogenomics Specialist -> CYP2C19 status for antiplatelet therapy, statin pharmacogenomics
3. GWAS Trait-to-Gene -> Colocalization of PRS loci with eQTLs to identify causal genes
4. Disease Research -> CAD pathophysiology, risk factor interactions

**"Compare PRS performance across ancestries for breast cancer"**
1. Polygenic Risk Score -> Calculate PRS using European-derived weights, assess transferability to non-European cohorts
2. GWAS SNP Interpretation -> Variant annotation across populations, MAF differences, LD structure variation
3. Precision Medicine Stratifier -> Population-specific risk calibration and screening recommendations
4. Pharmacogenomics Specialist -> BRCA-pathway pharmacogenomics for risk-reduction therapies

## Completeness Checklist

- [ ] Disease/trait characterized with EFO ID and published heritability estimates
- [ ] GWAS loci collected from Open Targets with effect sizes extracted
- [ ] SNP quality control applied (MAF filter, strand ambiguity, LD pruning)
- [ ] PRS formula calculated with standardized z-scores and percentile assignment
- [ ] Risk category assigned using percentile framework (Low/Average/Elevated/High)
- [ ] Ancestry of discovery GWAS documented with transferability limitations noted
- [ ] gnomAD population frequencies checked for PRS portability assessment
- [ ] Both relative and absolute risk presented with clinical context
- [ ] Pharmacogenomic integration performed for genetically implicated targets
- [ ] Report file verified with no remaining `[Analyzing...]` placeholders
