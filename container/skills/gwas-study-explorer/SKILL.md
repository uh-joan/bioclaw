---
name: gwas-study-explorer
description: GWAS study explorer and meta-analysis specialist. Compares GWAS studies and performs meta-analyses across cohorts, evaluating study quality, replication, and cross-ancestry consistency. Use when user mentions GWAS comparison, meta-analysis, study heterogeneity, cross-ancestry, replication, I-squared, fixed effects, random effects, cohort comparison, sample size, population stratification, effect size comparison, allelic heterogeneity, study quality, GWAS catalog, Manhattan plot interpretation, forest plot, funnel plot, Cochran Q, DerSimonian-Laird, Mantel-Haenszel, or multi-cohort analysis.
---

# GWAS Study Explorer

Compares GWAS studies and performs meta-analyses across cohorts, evaluating study quality, replication, and cross-ancestry consistency. Uses Open Targets for genetic associations and target-disease evidence, PubMed for study literature, NLM for disease and gene coding, DrugBank for pharmacological context of validated targets, and ChEMBL for compound and bioactivity data linked to GWAS-implicated genes.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_gwas-study-explorer_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- SNP functional interpretation and variant annotation → use `gwas-snp-interpretation`
- Translating GWAS hits into drug targets → use `gwas-drug-discoverer`
- Mapping GWAS loci to causal genes → use `gwas-trait-to-gene`
- Statistical fine-mapping and credible set analysis → use `gwas-finemapping`
- Genotype-based patient stratification → use `precision-medicine-stratifier`

## Cross-Reference: Other Skills

- **SNP functional interpretation and variant annotation** -> use gwas-snp-interpretation skill
- **Translating GWAS hits into drug targets** -> use gwas-drug-discoverer skill
- **Mapping GWAS loci to causal genes** -> use gwas-trait-to-gene skill
- **Statistical fine-mapping and credible set analysis** -> use gwas-finemapping skill
- **Genotype-based patient stratification** -> use precision-medicine-stratifier skill

## Available MCP Tools

### `mcp__opentargets__opentargets_info` (Genetic Associations & Study Evidence) — PRIMARY

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_targets` | Search targets by gene symbol/name | `query`, `size` |
| `search_diseases` | Search diseases by name/synonym | `query`, `size` |
| `get_target_disease_associations` | Evidence-scored target-disease links with genetic evidence breakdown | `targetId` (Ensembl ID), `diseaseId` (EFO ID), `minScore`, `size` |
| `get_disease_targets_summary` | All targets for a disease ranked by evidence | `diseaseId`, `minScore`, `size` |
| `get_target_details` | Full target info (function, pathways, tractability, genetic constraint) | `id` (Ensembl ID) |
| `get_disease_details` | Full disease info (ontology, phenotypes, known associations) | `id` (EFO ID) |

### `mcp__pubmed__pubmed_articles` (GWAS Study Literature)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Quick keyword search | `keywords`, `num_results` |
| `search_advanced` | Filtered search | `term`, `journal`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Full article details | `pmid` |

### `mcp__nlm__nlm_ct_codes` (Disease Coding & Gene Lookups)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_mesh` | Search MeSH terms for disease/gene concepts | `query`, `limit` |
| `get_mesh_details` | Full MeSH descriptor with tree numbers | `mesh_id` |
| `search_snomed` | Search SNOMED CT codes | `query`, `limit` |
| `get_snomed_details` | SNOMED concept details and hierarchy | `concept_id` |
| `search_icd10` | Search ICD-10 codes | `query`, `limit` |
| `search_rxnorm` | Search drug codes in RxNorm | `query`, `limit` |
| `get_rxnorm_details` | RxNorm concept details and relationships | `rxcui` |
| `search_gene` | Search gene information by symbol/name | `query`, `limit` |
| `get_gene_details` | Full gene record (aliases, location, function) | `gene_id` |
| `map_codes` | Cross-map between coding systems (MeSH, SNOMED, ICD-10) | `source_code`, `source_system`, `target_system` |
| `search_omim` | Search OMIM for Mendelian disease-gene links | `query`, `limit` |

### `mcp__gnomad__gnomad_data` (Population Frequencies for Replication Context)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_variant` | Variant annotation including global and population-specific allele frequencies | `variant_id`, `dataset` |
| `get_population_frequencies` | Ancestry-specific allele frequencies (AFR, AMR, ASJ, EAS, FIN, NFE, SAS) for assessing replication context across GWAS cohorts | `variant_id`, `dataset` |

**gnomAD Workflow:** Annotate GWAS hits with gnomAD population frequencies to contextualize cross-ancestry replication patterns. When a GWAS signal fails to replicate in a different ancestry, gnomAD allele frequencies reveal whether the variant is rare or monomorphic in that population, explaining the lack of replication without invoking a false positive. Conversely, variants with similar frequencies across gnomAD populations that still fail to replicate suggest genuine heterogeneity in effect size or gene-environment interactions.

```
# Annotate a GWAS hit with gnomAD frequency data
mcp__gnomad__gnomad_data(method: "get_variant", variant_id: "9-22125503-C-G")

# Get ancestry-specific frequencies for replication context
mcp__gnomad__gnomad_data(method: "get_population_frequencies", variant_id: "9-22125503-C-G")
```

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

### `mcp__chembl__chembl_info` (Compound & Bioactivity Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `compound_search` | Search molecules by name/SMILES/ID | `query`, `limit` |
| `target_search` | Search biological targets | `query`, `limit` |
| `get_bioactivity` | Compound-target activity data (IC50, Ki, EC50) | `chembl_id`, `target_id`, `limit` |
| `get_mechanism` | Mechanism of action | `chembl_id` |
| `drug_search` | Search drugs by indication or name | `query`, `limit` |
| `get_admet` | ADMET/drug-likeness properties | `chembl_id` |

### `mcp__gwas__gwas_data` (GWAS Catalog — Study Metadata & Cross-Study Comparison)

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

**GWAS Catalog Workflow:** Use the GWAS Catalog as the primary source for study metadata and cross-study comparison. In Function 1 (Study Comparison), query `search_studies` to retrieve all GWAS catalog entries for a disease trait, then use `get_study` to extract study-level metadata including sample size, ancestry, platform, and publication details for systematic comparison. In Function 3 (Replication Assessment), use `get_variant_associations` to check whether a specific variant has been reported across multiple independent GWAS studies — multiple catalog entries for the same variant-trait pair from different studies constitute replication evidence. Use `search_by_trait` to identify all associations for a trait across studies, enabling heterogeneity assessment by comparing effect sizes and p-values across GCST accessions.

---

## 4 Core Functions

### Function 1: Study Comparison

Compare GWAS studies by sample sizes, ancestries, phenotype definitions, genotyping platforms, and statistical methods.

```
1. mcp__pubmed__pubmed_articles(method: "search_advanced", term: "TRAIT GWAS genome-wide association study", journal: "", start_date: "", end_date: "", num_results: 30)
   -> Identify all published GWAS for the trait of interest

2. mcp__pubmed__pubmed_articles(method: "get_article_metadata", pmid: "PMID")
   -> Extract study details: sample size, ancestry, phenotype definition, genotyping platform

3. mcp__nlm__nlm_ct_codes(method: "search_mesh", query: "TRAIT_NAME")
   -> Harmonize phenotype definitions across studies using MeSH terms

4. mcp__nlm__nlm_ct_codes(method: "map_codes", source_code: "disease_code", source_system: "ICD10", target_system: "MeSH")
   -> Cross-map disease coding to ensure consistent phenotype comparison

5. mcp__opentargets__opentargets_info(method: "search_diseases", query: "TRAIT_NAME")
   -> Get EFO disease ID for querying aggregated genetic evidence
```

**Study Comparison Parameters:**

```
For each study, extract and compare:
- Sample size: cases + controls (or total for quantitative traits)
- Ancestry composition: % European, East Asian, African, South Asian, Hispanic/Latino
- Phenotype definition: ICD codes, self-report, clinical diagnosis, biomarker threshold
- Genotyping platform: Illumina, Affymetrix, WGS, WES, imputation panel (TOPMed, HRC, 1000G)
- Imputation quality: info score threshold applied (typically > 0.3 or > 0.8)
- Statistical method: logistic/linear regression, BOLT-LMM, SAIGE, REGENIE
- Genomic control lambda: inflation factor (lambda_GC, LDSC intercept)
- Significance threshold: standard 5x10^-8 or adjusted
```

### Function 2: Meta-Analysis Assessment

Evaluate and interpret meta-analyses of GWAS results across cohorts.

```
1. mcp__pubmed__pubmed_articles(method: "search_advanced", term: "TRAIT meta-analysis GWAS genome-wide", journal: "", start_date: "", end_date: "", num_results: 20)
   -> Find published meta-analyses for the trait

2. mcp__pubmed__pubmed_articles(method: "get_article_metadata", pmid: "META_PMID")
   -> Extract meta-analysis methods, contributing cohorts, total sample size

3. mcp__opentargets__opentargets_info(method: "get_target_disease_associations", targetId: "ENSG00000xxxxx", diseaseId: "EFO_xxxxxxx")
   -> Check aggregated genetic evidence score reflecting meta-analytic strength

4. mcp__opentargets__opentargets_info(method: "get_disease_targets_summary", diseaseId: "EFO_xxxxxxx", minScore: 0.3, size: 50)
   -> Full landscape of meta-analytically supported targets for the disease
```

**Meta-Analysis Methods — Decision Framework:**

```
Choose method based on heterogeneity (I^2):

Fixed-Effects (Mantel-Haenszel / Inverse-Variance Weighted):
- Use when I^2 < 25% (low heterogeneity)
- Assumes all studies estimate the same true effect
- Weights studies by inverse variance (precision)
- More powerful when homogeneity holds
- Appropriate for studies from similar populations with similar designs

Random-Effects (DerSimonian-Laird):
- Use when I^2 >= 25% (moderate to considerable heterogeneity)
- Assumes true effect varies across studies
- Incorporates between-study variance (tau^2)
- Wider confidence intervals, more conservative
- Appropriate when studies differ in ancestry, phenotype, or design

Decision rule:
1. Calculate I^2 from Cochran's Q statistic
2. If I^2 < 25% -> Fixed-effects model
3. If I^2 25-75% -> Random-effects model, investigate heterogeneity sources
4. If I^2 > 75% -> Random-effects model, DO NOT pool without exploring subgroups
```

### Function 3: Replication Assessment

Evaluate whether GWAS findings replicate across independent studies and cohorts.

```
1. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_SYMBOL TRAIT replication independent cohort", num_results: 15)
   -> Find replication studies for specific loci

2. mcp__opentargets__opentargets_info(method: "search_targets", query: "GENE_SYMBOL")
   -> Get Ensembl ID for querying cross-study evidence

3. mcp__opentargets__opentargets_info(method: "get_target_disease_associations", targetId: "ENSG00000xxxxx", diseaseId: "EFO_xxxxxxx")
   -> Evidence score reflects replication across multiple studies in Open Targets

4. mcp__nlm__nlm_ct_codes(method: "search_gene", query: "GENE_SYMBOL")
   -> Confirm gene identity and aliases for comprehensive literature search

5. mcp__nlm__nlm_ct_codes(method: "search_omim", query: "GENE_SYMBOL")
   -> Mendelian disease links provide strongest form of replication (genetic convergence)
```

**Replication Criteria:**

```
A GWAS finding is considered replicated when ALL of the following are met:

1. Same direction of effect
   - Risk allele increases trait/disease risk in BOTH discovery and replication
   - Effect size (beta/OR) is in the same direction

2. Nominally significant in replication
   - p < 0.05 in independent replication cohort
   - After correcting for number of loci tested in replication stage

3. Genome-wide significant in combined meta-analysis
   - p < 5x10^-8 when discovery + replication are combined
   - Combined effect estimate is consistent with discovery

Additional strength indicators:
+ Replicated across multiple independent cohorts
+ Replicated across different ancestries
+ Consistent effect sizes (no winner's curse deflation > 50%)
+ Replicated using different genotyping platforms
+ Functional evidence supports the association (eQTL, chromatin)
```

### Function 4: Quality Evaluation

Assess the quality and reliability of individual GWAS and meta-analyses.

```
1. mcp__pubmed__pubmed_articles(method: "get_article_metadata", pmid: "PMID")
   -> Extract methods, sample size, journal, peer review status

2. mcp__pubmed__pubmed_articles(method: "search_advanced", term: "TRAIT GWAS quality assessment methodological", journal: "", start_date: "", end_date: "", num_results: 10)
   -> Find methodological reviews and quality assessments

3. mcp__nlm__nlm_ct_codes(method: "search_mesh", query: "genome-wide association study")
   -> Standardized MeSH indexing for quality-filtered searches

4. mcp__opentargets__opentargets_info(method: "get_disease_targets_summary", diseaseId: "EFO_xxxxxxx", minScore: 0.5, size: 30)
   -> High-confidence targets (minScore 0.5) reflect well-replicated, high-quality findings
```

---

## Study Quality Tiers

| Tier | Sample Size | Characteristics | Interpretation |
|------|-------------|-----------------|----------------|
| **Tier 1** | n >= 50,000 | Large biobank-scale (UKBB, FinnGen, MVP, BioBank Japan). Well-powered to detect common variants with small effects (OR 1.05-1.10). Robust genomic control. Multiple ancestry representation. | Gold standard. Results are highly reliable for common variants. Novel loci likely genuine. |
| **Tier 2** | 10,000-50,000 | Mid-scale consortium studies. Adequate power for moderate effects (OR > 1.15). May have limited ancestry diversity. | Reliable for moderate-to-large effects. Small-effect loci require replication. |
| **Tier 3** | n < 10,000 | Small studies, pilot GWAS, rare disease cohorts. Underpowered for small effects. Higher risk of population stratification artifacts. | Hypothesis-generating only for common variants. Adequate for rare variant burden tests. Require replication. |

**Quality Assessment Checklist:**

```
For each study, evaluate:

Sample Quality:
[ ] Adequate sample size for expected effect sizes
[ ] Ancestry composition clearly described
[ ] Related individuals removed or accounted for
[ ] Population stratification controlled (PCs, mixed models)

Genotyping Quality:
[ ] Genotyping platform and call rate reported
[ ] SNP-level QC (MAF, HWE, missingness thresholds stated)
[ ] Sample-level QC (heterozygosity, sex check, kinship)
[ ] Imputation panel and quality threshold documented

Statistical Quality:
[ ] Appropriate regression model for trait type
[ ] Genomic inflation factor reported (lambda_GC < 1.10 ideal)
[ ] LDSC intercept near 1.0 (distinguishes polygenicity from inflation)
[ ] Multiple testing correction applied
[ ] Sensitivity analyses performed

Reporting Quality:
[ ] Full summary statistics publicly available
[ ] Manhattan and QQ plots provided
[ ] Effect sizes with confidence intervals reported
[ ] Replication attempted in independent cohort
```

---

## Heterogeneity Assessment Framework

### I-Squared (I^2) Statistic

The I^2 statistic quantifies the proportion of total variation in effect estimates that is due to between-study heterogeneity rather than sampling error.

| I^2 Range | Classification | Interpretation | Action |
|-----------|---------------|----------------|--------|
| **< 25%** | Low | Studies are estimating similar effects. Variation is mostly due to sampling error. | Use fixed-effects meta-analysis. Pool results with confidence. |
| **25-75%** | Moderate | Meaningful heterogeneity present. Some studies differ in true effect. | Use random-effects meta-analysis. Investigate sources of heterogeneity. |
| **> 75%** | Considerable | Substantial between-study differences. Pooled estimate may be misleading. | Use random-effects with caution. Subgroup/meta-regression analyses mandatory before interpreting pooled effect. |

### Cochran's Q Test

```
Q statistic:
- Tests null hypothesis that all studies share the same effect
- Q ~ chi-squared with (k-1) degrees of freedom (k = number of studies)
- p < 0.10 typically used as threshold (conservative, given low power)
- Low power when few studies — absence of significance does NOT confirm homogeneity

Relationship to I^2:
I^2 = max(0, (Q - df) / Q) x 100%
- I^2 does not depend on number of studies (unlike Q)
- Preferred for reporting heterogeneity magnitude
```

### 5 Sources of Heterogeneity in GWAS Meta-Analysis

| Source | Description | How to Detect | How to Address |
|--------|-------------|--------------|----------------|
| **1. Population stratification** | Ancestral differences in allele frequencies and LD create spurious or inflated associations | Compare effect sizes across ancestry-specific strata. Check genomic inflation per cohort. | Stratified meta-analysis by ancestry. Use trans-ethnic meta-analysis methods (MR-MEGA, MANTRA). |
| **2. Phenotype definition** | Different studies use different case definitions (ICD codes, self-report, clinical diagnosis, biomarker thresholds) | Compare phenotype ascertainment protocols. Map definitions to common ontology (MeSH, EFO). | Harmonize phenotypes where possible. Meta-regression on phenotype definition. Subgroup analysis by definition type. |
| **3. Genotyping platform** | Different arrays capture different variants directly; imputation fill varies | Check overlap of directly genotyped variants. Compare imputation panels and quality scores. | Restrict to well-imputed variants (info > 0.8). Meta-analyze only overlapping variants. |
| **4. Imputation quality** | Variants imputed with low accuracy inflate variance and may introduce bias | Compare info scores across cohorts for key variants. Check concordance with directly genotyped proxies. | Apply stringent info score filters (> 0.8 for meta-analysis). Weight by imputation quality. |
| **5. Analysis method** | Different software, covariates, or models (logistic vs mixed model, BOLT-LMM vs SAIGE vs REGENIE) | Compare methods sections across studies. Check if mixed models vs standard regression yield different results. | Sensitivity analysis using uniform method. Meta-regression on analysis method. Prefer LMM/SAIGE for biobank-scale data. |

---

## Cross-Ancestry Analysis Framework

### Ancestry Groups and Major Biobanks

| Ancestry | Abbreviation | Major Biobanks/Cohorts | Typical LD Characteristics |
|----------|-------------|----------------------|---------------------------|
| **European** | EUR | UK Biobank, FinnGen, deCODE, MVP (EUR), Estonian Biobank | Longer LD blocks, well-imputed with HRC/TOPMed |
| **East Asian** | EAS | BioBank Japan, China Kadoorie, TWB, CKB | Moderate LD, different haplotype structure |
| **African** | AFR | Africa Wits-INDEPTH, APCDR, H3Africa, MVP (AFR) | Shortest LD blocks, highest genetic diversity, best for fine-mapping |
| **South Asian** | SAS | LOLIPOP, Born in Bradford, UK Biobank (SAS) | Intermediate LD, distinct founder effects |
| **Hispanic/Latino** | AMR | HCHS/SOL, Million Veteran Program (HIS), SIGMA | Admixed (EUR/AMR/AFR), complex LD patterns |

### Cross-Ancestry Comparison Workflow

```
1. mcp__pubmed__pubmed_articles(method: "search_advanced", term: "TRAIT GWAS multi-ancestry trans-ethnic cross-population", journal: "", start_date: "", end_date: "", num_results: 20)
   -> Find multi-ancestry GWAS publications

2. mcp__opentargets__opentargets_info(method: "get_target_disease_associations", targetId: "ENSG00000xxxxx", diseaseId: "EFO_xxxxxxx")
   -> Aggregated genetic evidence (includes multi-ancestry sources)

3. mcp__nlm__nlm_ct_codes(method: "search_gene", query: "GENE_SYMBOL")
   -> Gene-level info for cross-ancestry context

4. mcp__nlm__nlm_ct_codes(method: "get_gene_details", gene_id: "GENE_ID")
   -> Population genetics context, gene function across populations

5. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_SYMBOL ancestry-specific allele frequency population", num_results: 10)
   -> Population-specific allele frequency and effect data
```

### Transferability Assessment

```
Cross-ancestry transferability categories:

1. Fully transferable (strongest evidence):
   - Same variant is genome-wide significant in >= 2 ancestry groups
   - Consistent direction and similar effect size
   - Implies shared causal mechanism independent of LD

2. Locus-level transferable:
   - Same locus/gene is significant across ancestries
   - Different lead variants (due to LD differences)
   - Fine-mapping may converge on same causal variant
   - Supports shared biology, LD structure explains lead variant differences

3. Ancestry-enriched:
   - Significant in one ancestry group, suggestive in others
   - May reflect allele frequency differences (variant rare in some populations)
   - Gene-environment interactions possible
   - Requires larger sample sizes in underrepresented populations

4. Ancestry-specific:
   - Significant in one ancestry, null in others even with adequate power
   - Could indicate: population-specific regulatory effects, founder mutations,
     gene-environment interactions, or structural variant in LD
   - Important for precision medicine — effect may not generalize

5. Not transferable (weakest evidence):
   - No evidence of association outside discovery population
   - Possible false positive in discovery, or truly population-specific
   - Requires functional validation before clinical translation
```

---

## Evidence Grading System

### Tiers T1-T4

| Tier | Criteria | Confidence | Action |
|------|----------|------------|--------|
| **T1 — Robust** | Genome-wide significant (p < 5x10^-8) in Tier 1 study (n >= 50,000). Replicated in >= 2 independent cohorts. Consistent across >= 2 ancestry groups. Low heterogeneity (I^2 < 25%). Same direction of effect in all studies. | Highest | Treat as established association. Proceed to functional characterization and drug target evaluation. |
| **T2 — Strong** | Genome-wide significant in Tier 1 or Tier 2 study. Replicated in >= 1 independent cohort. Moderate heterogeneity acceptable (I^2 25-50%). Cross-ancestry data limited but not contradictory. | High | Reliable association. Pursue replication in additional ancestries. Proceed with caution to translational work. |
| **T3 — Moderate** | Genome-wide significant in single study (any tier). No independent replication yet, or replication is nominal. Heterogeneity not fully assessed. Cross-ancestry data absent. | Moderate | Promising but unconfirmed. Requires independent replication before translational investment. |
| **T4 — Preliminary** | Suggestive significance (p < 1x10^-5) or genome-wide significant in Tier 3 study only. No replication. May have quality concerns (high lambda, small sample, single ancestry). | Low | Hypothesis-generating only. Do not use for clinical or drug development decisions without substantial additional evidence. |

### Applying Evidence Grades

```
Grading workflow:
1. Determine study quality tier (Tier 1/2/3 by sample size)
2. Assess replication status (independent cohorts, same direction)
3. Evaluate cross-ancestry consistency
4. Calculate heterogeneity (I^2 across studies)
5. Assign evidence grade T1-T4

Upgrading criteria:
- T3 -> T2: Independent replication with same direction, p < 0.05
- T2 -> T1: Multi-ancestry replication with low heterogeneity
- Functional evidence (eQTL, CRISPR) upgrades confidence within tier

Downgrading criteria:
- High heterogeneity (I^2 > 75%) across studies: downgrade by 1 tier
- Winner's curse (replication effect < 50% of discovery): flag concern
- Ancestry-specific only with no functional explanation: flag limitation
```

---

## Pharmacological Context for Validated GWAS Loci

### Linking GWAS Findings to Drug Landscape

```
1. mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   -> Tractability and druggability of GWAS-implicated target

2. mcp__drugbank__drugbank_info(method: "search_by_target", target: "GENE_SYMBOL", limit: 20)
   -> Existing drugs for the target

3. mcp__drugbank__drugbank_info(method: "get_drug_details", drugbank_id: "DBxxxxx")
   -> Full drug profile for pharmacological interpretation

4. mcp__chembl__chembl_info(method: "target_search", query: "GENE_SYMBOL")
   -> ChEMBL target classification and known ligands

5. mcp__chembl__chembl_info(method: "get_bioactivity", target_id: "CHEMBL_TARGET_ID", limit: 50)
   -> Bioactivity data for compounds targeting the GWAS gene

6. mcp__drugbank__drugbank_info(method: "get_pathways", drugbank_id: "DBxxxxx")
   -> Pathway context linking GWAS gene to druggable biology

7. mcp__drugbank__drugbank_info(method: "get_external_identifiers", drugbank_id: "DBxxxxx")
   -> Cross-database IDs for integrated analysis
```

---

## GWAS Meta-Analysis Reporting Template

```
Meta-Analysis Summary:
- Trait: [phenotype with EFO/MeSH mapping]
- Number of contributing studies: [k]
- Total sample size: [N cases / N controls, or N total]
- Ancestry breakdown: [% EUR, % EAS, % AFR, % SAS, % AMR]
- Meta-analysis method: [Fixed-effects / Random-effects]
- Number of genome-wide significant loci: [n]
- Number of novel loci: [n] (not previously reported)

Heterogeneity Assessment:
- Median I^2 across significant loci: [value]
- Loci with I^2 > 75%: [n] / [total] — investigate individually
- Cochran's Q p-value distribution: [summary]
- Primary heterogeneity sources: [population stratification / phenotype / platform / etc.]

Replication Summary:
- Loci replicated (same direction, p < 0.05 in independent cohort): [n] / [total]
- Loci replicated across >= 2 ancestries: [n]
- Evidence grade distribution: T1: [n], T2: [n], T3: [n], T4: [n]

Cross-Ancestry Findings:
- Fully transferable loci: [n]
- Locus-level transferable: [n]
- Ancestry-enriched: [n]
- Ancestry-specific: [n]
```

---

## Multi-Agent Workflow Examples

**"Compare all published GWAS for Type 2 Diabetes and assess replication"**
1. GWAS Study Explorer -> Identify all T2D GWAS, compare sample sizes/ancestries/methods, assess heterogeneity across studies, evaluate replication of key loci, assign evidence grades T1-T4
2. GWAS SNP Interpretation -> Functional annotation of top replicated variants, eQTL/pQTL colocalization
3. GWAS Trait-to-Gene -> Causal gene assignment for novel and replicated loci using L2G and fine-mapping
4. Precision Medicine Stratifier -> Stratify findings by ancestry for clinical translation

**"Evaluate the quality of a new Alzheimer's GWAS meta-analysis"**
1. GWAS Study Explorer -> Assess contributing cohort quality (Tier 1/2/3), evaluate meta-analysis methodology (fixed vs random effects), calculate heterogeneity metrics, compare with prior meta-analyses, check cross-ancestry representation
2. GWAS Drug Discoverer -> Translate high-confidence loci into drug targets, druggability screening
3. GWAS Fine-Mapping -> Statistical fine-mapping of novel loci, credible set evaluation
4. GWAS SNP Interpretation -> Variant-level functional interpretation for top hits

**"Assess cross-ancestry consistency of blood pressure GWAS findings"**
1. GWAS Study Explorer -> Compile ancestry-specific GWAS results, transferability assessment for each locus, heterogeneity analysis by ancestry, identify ancestry-specific vs shared signals
2. Precision Medicine Stratifier -> Clinical implications of ancestry-specific findings, pharmacogenomic context
3. GWAS Trait-to-Gene -> Gene mapping prioritizing loci with cross-ancestry support
4. GWAS Drug Discoverer -> Drug target assessment focusing on universally replicated loci

**"Perform a systematic comparison of GWAS for coronary artery disease across biobanks"**
1. GWAS Study Explorer -> Compare UK Biobank, FinnGen, BioBank Japan, MVP results for CAD. Evaluate sample sizes, phenotype definitions (MI vs broad CAD), genotyping platforms, imputation quality, and statistical methods. Meta-analyze effect sizes, assess I^2, assign evidence grades to each locus
2. GWAS Fine-Mapping -> Fine-map loci with cross-biobank support using ancestry-diverse LD
3. GWAS Drug Discoverer -> Prioritize genetically-supported targets from robust (T1) loci for drug development
4. GWAS SNP Interpretation -> Functional characterization of loci showing biobank-specific heterogeneity

---

## Completeness Checklist

- [ ] All published GWAS for the trait identified via PubMed with sample sizes and ancestries
- [ ] Study quality assessed using the quality assessment checklist (sample, genotyping, statistical, reporting)
- [ ] Study quality tiers (Tier 1/2/3) assigned based on sample size
- [ ] Meta-analysis method justified (fixed-effects vs random-effects based on I-squared)
- [ ] Heterogeneity quantified (I-squared, Cochran's Q) and sources investigated
- [ ] Replication status evaluated for key loci (direction, significance, cross-ancestry)
- [ ] Cross-ancestry transferability assessed for each locus (fully transferable to ancestry-specific)
- [ ] Evidence grades (T1-T4) assigned to each association
- [ ] Report file created with no remaining `[Analyzing...]` placeholders
