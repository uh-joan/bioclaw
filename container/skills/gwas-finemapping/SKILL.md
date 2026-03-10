---
name: gwas-finemapping
description: GWAS fine-mapping and causal variant prioritization specialist. Identifies and prioritizes causal variants at GWAS loci using Bayesian statistical fine-mapping and locus-to-gene (L2G) predictions. Computes posterior probabilities, links variants to genes, and suggests validation strategies. Use when user mentions fine-mapping, fine mapping, credible set, causal variant, posterior probability, PIP, posterior inclusion probability, SuSiE, FINEMAP, PAINTOR, CAVIAR, Bayesian fine-mapping, 95% credible set, 99% credible set, causal SNP, variant prioritization, L2G score, locus-to-gene, functional annotation, eQTL colocalization, chromatin interaction, GWAS locus resolution, or variant-to-function.
---

# GWAS Fine-Mapping

Identifies and prioritizes causal variants at GWAS loci using Bayesian statistical fine-mapping and locus-to-gene (L2G) predictions. Computes posterior probabilities, constructs credible sets, links variants to effector genes via functional annotation integration, and suggests experimental validation strategies. Uses Open Targets for L2G scores and credible sets, PubMed for fine-mapping literature, NLM for gene/disease coding, DrugBank for pharmacological context of prioritized targets, and ChEMBL for compound intelligence.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_gwas-finemapping_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- SNP-level functional annotation and variant interpretation → use `gwas-snp-interpretation`
- Trait-to-gene mapping and gene prioritization → use `gwas-trait-to-gene`
- GWAS study comparison and meta-analysis assessment → use `gwas-study-explorer`
- Translating fine-mapped targets into drug candidates → use `gwas-drug-discoverer`
- Deep target validation and SAR analysis → use `drug-target-analyst`

## Cross-Reference: Other Skills

- **SNP-level interpretation and functional annotation** -> use gwas-snp-interpretation skill
- **Trait-to-gene mapping and gene prioritization** -> use gwas-trait-to-gene skill
- **GWAS study design and summary statistics** -> use gwas-study-explorer skill
- **Translating fine-mapped targets into drug candidates** -> use gwas-drug-discoverer skill
- **Deep target validation and SAR analysis** -> use drug-target-analyst skill

## Available MCP Tools

### `mcp__opentargets__opentargets_info` (PRIMARY — L2G Predictions & Credible Sets)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_targets` | Search targets by gene symbol/name | `query`, `size` |
| `search_diseases` | Search diseases by name/synonym | `query`, `size` |
| `get_target_disease_associations` | Evidence-scored target-disease links with genetic evidence and L2G breakdown | `targetId` (Ensembl ID), `diseaseId` (EFO ID), `minScore`, `size` |
| `get_disease_targets_summary` | All targets for a disease ranked by genetic evidence | `diseaseId`, `minScore`, `size` |
| `get_target_details` | Full target info (function, pathways, tractability, genetic constraint) | `id` (Ensembl ID) |
| `get_disease_details` | Full disease info (ontology, phenotypes, known associations) | `id` (EFO ID) |

### `mcp__pubmed__pubmed_articles` (Fine-Mapping Literature)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Quick keyword search for fine-mapping studies | `keywords`, `num_results` |
| `search_advanced` | Filtered search by journal, date, methodology | `term`, `journal`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Full article details including methods and results | `pmid` |

### `mcp__nlm__nlm_ct_codes` (Gene Lookups & Disease Coding)

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

### `mcp__drugbank__drugbank_info` (Pharmacological Context for Prioritized Targets)

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

### `mcp__chembl__chembl_info` (Compound Intelligence for Fine-Mapped Targets)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `compound_search` | Search molecules by name/SMILES/ID | `query`, `limit` |
| `target_search` | Search biological targets | `query`, `limit` |
| `get_bioactivity` | Compound-target activity data (IC50, Ki, EC50) | `chembl_id`, `target_id`, `limit` |
| `get_mechanism` | Mechanism of action | `chembl_id` |
| `drug_search` | Search drugs by indication or name | `query`, `limit` |
| `get_admet` | ADMET/drug-likeness properties | `chembl_id` |

### `mcp__gwas__gwas_data` (GWAS Catalog — Variant Associations & Regional Context)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_variant` | Get variant info by rs ID for fine-mapping candidate lookup | `rs_id` |
| `get_variant_associations` | All GWAS associations for a variant — identifies studies reporting the signal | `rs_id`, `page`, `size` |
| `search_associations` | Search associations by query or PubMed ID | `query`, `pubmed_id`, `page`, `size` |
| `get_study` | Study details by GCST accession — sample size, ancestry, platform for LD reference selection | `study_id` |
| `get_gene_associations` | All GWAS associations for a gene — defines the association landscape at a locus | `gene`, `page`, `size` |
| `get_region_associations` | Associations in a genomic region — retrieves all signals in the fine-mapping window | `chromosome`, `start`, `end`, `page`, `size` |
| `search_genes` | Gene info with genomic context | `gene` |

**GWAS Catalog Workflow:** Use the GWAS Catalog to define the association landscape before fine-mapping. Query `get_region_associations` to retrieve all reported GWAS signals within the fine-mapping window — multiple independent signals from different studies indicate allelic heterogeneity requiring multi-signal fine-mapping (SuSiE). Use `get_variant_associations` to check whether credible set variants have been independently reported, which strengthens causal candidacy. Use `get_study` to extract study-level metadata (sample size, ancestry, platform) needed for selecting appropriate LD reference panels.

```
# Retrieve all GWAS signals in the fine-mapping region
mcp__gwas__gwas_data(method: "get_region_associations", chromosome: "9", start: 21900000, end: 22200000)

# Check if a credible set variant has been independently reported
mcp__gwas__gwas_data(method: "get_variant_associations", rs_id: "rs1333049")

# Get study metadata for LD reference panel selection
mcp__gwas__gwas_data(method: "get_study", study_id: "GCST000001")
```

### `mcp__gnomad__gnomad_data` (Regional Variant Annotation & Gene Constraint)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_variants_by_region` | Retrieve all variants in a genomic region for annotating credible set candidates | `region`, `dataset` |
| `get_variant` | Individual variant annotation including allele frequency, functional consequence, and clinical flags | `variant_id`, `dataset` |
| `get_gene_constraint` | Gene-level constraint metrics (pLI, LOEUF) to prioritize constrained genes at fine-mapped loci | `gene`, `dataset` |

**gnomAD Workflow:** After constructing a credible set, query gnomAD for all variants in the fine-mapping region to annotate each credible set member with population allele frequencies, functional consequences, and clinical flags. Variants that are rare or absent in gnomAD but present in the credible set may represent population-specific causal candidates. Complement this with gene constraint scores (pLI, LOEUF) to prioritize effector genes at the locus -- highly constrained genes harboring credible set variants are stronger causal candidates.

```
# Retrieve all gnomAD variants in the fine-mapping region
mcp__gnomad__gnomad_data(method: "search_variants_by_region", region: "9:21900000-22200000")

# Annotate a specific credible set variant
mcp__gnomad__gnomad_data(method: "get_variant", variant_id: "9-22125503-C-G")

# Assess gene constraint for the candidate effector gene
mcp__gnomad__gnomad_data(method: "get_gene_constraint", gene: "CDKN2A")
```

### `mcp__gwas__gwas_data` (GWAS Catalog — Credible Set Variant Data)

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

**GWAS Catalog Workflow:** Use the GWAS Catalog to annotate credible set variants with published association data. After constructing a credible set, query `get_variant_associations` for each credible set member to determine whether it has been reported as a lead variant in any published GWAS — variants that are themselves GWAS lead SNPs have stronger prior probability of being causal. Use `get_region_associations` to retrieve all GWAS associations within the fine-mapping window, identifying additional signals and independent associations at the locus that may indicate allelic heterogeneity requiring multi-signal fine-mapping. Use `get_study` to retrieve metadata for the original GWAS studies that reported associations at the locus, informing the choice of LD reference panel and ancestry composition for fine-mapping.

---

## Bayesian Fine-Mapping Methods

### Method Comparison

| Method | Approach | Causal Variants | Strengths | Best Use Case |
|--------|----------|-----------------|-----------|---------------|
| **SuSiE** | Iterative Bayesian regression (sum of single effects) | Multiple (independent signals) | Handles multiple causal variants per locus, provides per-variant PIPs and credible sets per signal | Default choice for multi-signal loci |
| **FINEMAP** | Shotgun stochastic search | Multiple | Scalable to large regions, enumerates configurations efficiently | Large loci (>1000 variants), rapid analysis |
| **PAINTOR** | Bayesian with functional annotation integration | Multiple | Integrates epigenomic data (ATAC-seq, H3K27ac) as priors, boosts power | When functional annotation data is available |
| **CAVIAR** | Exhaustive enumeration with colocalization | 1-6 (limited) | Exact posterior computation, built-in colocalization (eCAVIAR) | Small loci, eQTL colocalization |

### When to Use Each Method

```
SuSiE (default):
- Multiple independent association signals at one locus
- Standard GWAS summary statistics + LD matrix available
- Need per-signal credible sets

FINEMAP:
- Very large loci (>1000 variants in region)
- Need fast turnaround
- Single or multiple causal variants

PAINTOR:
- Functional annotation data available (ENCODE, Roadmap Epigenomics)
- Tissue-specific fine-mapping (e.g., islet enhancers for T2D)
- Want to leverage prior biological knowledge

CAVIAR/eCAVIAR:
- Small, well-defined loci (<200 variants)
- Need exact posterior computation
- eQTL-GWAS colocalization analysis
```

---

## Credible Set Construction

### Definition

A **credible set** is the minimal set of variants that, ranked by posterior probability, cumulatively exceeds a confidence threshold (typically 95% or 99%) for containing the true causal variant.

### Confidence Levels

| Level | Interpretation | Typical Set Size | Use Case |
|-------|---------------|------------------|----------|
| **95% credible set** | 95% probability the causal variant is included | Smaller, more focused | Standard reporting, variant prioritization |
| **99% credible set** | 99% probability the causal variant is included | Larger, more inclusive | Conservative analysis, ensuring causal variant is captured |

### Credible Set Quality Indicators

```
High-resolution locus (actionable):
- 95% credible set contains <= 5 variants
- Lead variant PIP > 0.5
- Clear functional candidate in set

Moderate-resolution locus (further work needed):
- 95% credible set contains 6-20 variants
- Lead variant PIP 0.1-0.5
- Multiple plausible functional candidates

Low-resolution locus (difficult to resolve):
- 95% credible set contains > 20 variants
- Lead variant PIP < 0.1
- Strong LD across region, no clear functional standout
```

---

## Posterior Probability Interpretation

### Posterior Inclusion Probability (PIP)

The PIP is the probability that a variant is causal, summed across all causal configurations that include it.

| PIP Range | Interpretation | Action |
|-----------|---------------|--------|
| **> 0.5** | Very likely causal — strong statistical evidence | Prioritize for functional validation |
| **0.1 - 0.5** | Plausible causal — moderate evidence | Include in credible set, seek corroborating functional evidence |
| **0.01 - 0.1** | Possible causal — weak evidence | Consider if functional annotation supports causality |
| **< 0.01** | Unlikely causal | Deprioritize unless in strong LD with high-PIP variant |

### Interpreting PIPs in Context

```
High confidence assignment:
- PIP > 0.5 AND coding variant (missense, nonsense, splice) → near-certain causal
- PIP > 0.5 AND eQTL for nearby gene → strong causal with effector gene identified
- PIP > 0.3 AND in active enhancer (tissue-matched) → probable regulatory causal

Lower confidence — seek additional evidence:
- PIP 0.1-0.3 AND intronic/intergenic → check chromatin interaction, eQTL data
- Multiple variants with PIP 0.05-0.2 → locus not well resolved, consider multi-ancestry fine-mapping
- PIP driven by single ancestry → replicate in diverse populations
```

---

## Locus-to-Gene (L2G) Score Integration

### L2G Score Components

The Open Targets L2G model integrates multiple evidence streams to predict the most likely effector gene at each GWAS locus.

| Evidence Stream | What it Measures | Weight |
|----------------|-----------------|--------|
| **Distance** | Physical distance from variant to gene TSS | Baseline prior |
| **eQTL coloc** | GWAS-eQTL colocalization (posterior probability of shared causal variant) | High |
| **pQTL coloc** | GWAS-pQTL colocalization | Very high |
| **Chromatin interaction** | PCHi-C, promoter-capture Hi-C linking variant to gene promoter | High |
| **Functional consequence** | VEP-predicted impact on protein coding (missense, LoF) | Very high |
| **Chromatin accessibility** | Variant in DHS/ATAC-seq peak near gene | Moderate |

### L2G Score Interpretation

| L2G Score | Confidence | Interpretation |
|-----------|-----------|----------------|
| **> 0.8** | High | Strong multi-evidence support for this gene |
| **0.5 - 0.8** | Moderate | Good evidence but some ambiguity |
| **0.2 - 0.5** | Low | Suggestive — likely nearest gene or single evidence line |
| **< 0.2** | Very low | Weak assignment, consider alternative genes |

---

## Variant Prioritization Hierarchy

### Ranking Framework

Prioritize causal variants using this evidence hierarchy (highest to lowest weight):

```
1. Posterior Inclusion Probability (PIP)
   - Statistical fine-mapping output
   - PIP > 0.5 = top priority

2. Functional Consequence
   - Coding: LoF > missense (CADD > 20) > synonymous
   - Non-coding: splice region > UTR > promoter > enhancer > intergenic
   - CADD score > 15 suggests functional impact

3. eQTL Evidence
   - Is the variant an eQTL for a nearby gene in disease-relevant tissue?
   - Colocalization posterior probability (H4) > 0.8 = strong

4. Conservation & Constraint
   - PhyloP > 2 (conserved across mammals)
   - GERP > 4 (constrained element)
   - Gene-level: pLI > 0.9 or LOEUF < 0.35 (loss-of-function intolerant)

5. Chromatin Context
   - Active enhancer in disease-relevant tissue/cell type
   - Chromatin interaction linking to gene promoter

6. Experimental Feasibility
   - Is the variant amenable to CRISPR editing?
   - Are relevant cell models available?
   - Can the effect be measured with a reporter assay?
```

---

## Fine-Mapping Workflow

### Step 1: Define the Locus and Retrieve Genetic Evidence

```
1. mcp__opentargets__opentargets_info(method: "search_diseases", query: "disease_name")
   -> Get EFO disease ID

2. mcp__opentargets__opentargets_info(method: "get_disease_targets_summary", diseaseId: "EFO_xxxxxxx", minScore: 0.3, size: 50)
   -> All genetically associated targets, ranked by evidence score

3. mcp__nlm__nlm_ct_codes(method: "search_gene", query: "GENE_SYMBOL")
   -> Gene details, chromosomal location, aliases

4. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_SYMBOL fine-mapping credible set causal variant", num_results: 15)
   -> Published fine-mapping studies at this locus
```

### Step 2: Assess Credible Sets and Posterior Probabilities

```
1. mcp__opentargets__opentargets_info(method: "get_target_disease_associations", targetId: "ENSG00000xxxxx", diseaseId: "EFO_xxxxxxx")
   -> Genetic evidence breakdown including L2G scores, credible set membership

2. mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   -> Target function, pathways, tractability, genetic constraint scores

3. mcp__pubmed__pubmed_articles(method: "search_advanced", term: "rsXXXXXXXX fine-mapping posterior probability", num_results: 10)
   -> Literature reporting PIPs for specific variants at this locus

4. mcp__nlm__nlm_ct_codes(method: "search_omim", query: "GENE_SYMBOL")
   -> Mendelian disease links (strongest causal evidence for gene)
```

### Step 3: Link Variants to Genes (L2G Integration)

```
1. mcp__opentargets__opentargets_info(method: "search_targets", query: "GENE_SYMBOL", size: 5)
   -> Get Ensembl ID for candidate effector gene

2. mcp__opentargets__opentargets_info(method: "get_target_disease_associations", targetId: "ENSG00000xxxxx", diseaseId: "EFO_xxxxxxx")
   -> L2G score, evidence streams (eQTL coloc, distance, chromatin interaction)

3. mcp__nlm__nlm_ct_codes(method: "get_gene_details", gene_id: "GENE_ID")
   -> Full gene record: function, expression pattern, pathway involvement

4. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_SYMBOL eQTL colocalization GWAS", num_results: 10)
   -> Published eQTL colocalization evidence
```

### Step 4: Assess Druggability of Fine-Mapped Targets

```
1. mcp__drugbank__drugbank_info(method: "search_by_target", target: "gene_name")
   -> Existing drugs that modulate this target

2. mcp__chembl__chembl_info(method: "target_search", query: "gene_name")
   -> ChEMBL target ID and target classification

3. mcp__chembl__chembl_info(method: "get_bioactivity", target_id: "CHEMBLxxxxx", limit: 30)
   -> Known compounds with measured activity against this target

4. mcp__drugbank__drugbank_info(method: "get_pathways", drugbank_id: "DBxxxxx")
   -> Pathway context for pharmacological intervention
```

---

## Evidence Grading Framework

### Tier Classification for Fine-Mapped Variants

| Tier | Criteria | Confidence | Recommended Action |
|------|----------|-----------|-------------------|
| **T1 — Definitive** | PIP > 0.5 + coding variant (LoF/missense) or PIP > 0.5 + eQTL coloc H4 > 0.8 in disease tissue | Very high | Proceed to functional validation, target nomination |
| **T2 — Strong** | PIP 0.1-0.5 + in active enhancer (tissue-matched) + L2G > 0.5 for one gene | High | Prioritize for reporter assay, CRISPR editing |
| **T3 — Moderate** | PIP 0.01-0.1 + some functional annotation support (DHS, conservation) OR multiple variants with PIP 0.05-0.2 | Moderate | Pursue multi-ancestry fine-mapping, additional functional data |
| **T4 — Suggestive** | PIP < 0.01 or large credible set (>20 variants) with no clear functional candidate | Low | Needs more data — larger GWAS, better LD reference, functional screens |

### Upgrading Evidence Tier

```
T4 -> T3:
- Multi-ancestry fine-mapping narrows credible set
- New functional annotation data (ATAC-seq in disease tissue)

T3 -> T2:
- eQTL discovered in disease-relevant tissue
- Chromatin interaction data links variant to specific gene

T2 -> T1:
- CRISPR editing confirms allele-specific effect
- Reporter assay validates enhancer activity
- Colocalization with pQTL confirmed
```

---

## Validation Strategies

### Experimental Validation Approaches

| Strategy | What it Tests | Best For | Throughput |
|----------|-------------|----------|------------|
| **CRISPR knock-in** | Direct effect of variant allele swap | Coding and non-coding variants | Low (1-5 variants) |
| **Massively parallel reporter assay (MPRA)** | Enhancer activity of variant-containing sequences | Non-coding variants in regulatory regions | High (thousands) |
| **CRISPRi/CRISPRa** | Effect of silencing/activating regulatory element | Non-coding variants, enhancer validation | Medium (tens) |
| **eQTL analysis** | Allele-specific gene expression | Linking variant to effector gene | Population-scale |
| **Colocalization (coloc/TWAS)** | Shared causal variant between GWAS and eQTL | Confirming regulatory mechanism | Computational |
| **Luciferase reporter assay** | Enhancer/promoter activity difference by allele | Candidate regulatory variants | Low-medium |
| **Hi-C / Capture-C** | 3D chromatin contacts between variant and gene | Long-range regulatory variants | Medium |
| **Base editing** | Precise single-nucleotide changes without DSB | SNV effects in cell models | Low-medium |

### Validation Decision Tree

```
Is the variant coding?
  YES -> CRISPR knock-in in disease-relevant cell line
         Measure protein function, stability, localization
  NO  -> Is it in an active enhancer/promoter?
           YES -> Reporter assay (luciferase or MPRA)
                  CRISPRi to silence the element
                  Check for eQTL in matched tissue
           NO  -> Is there a chromatin interaction to a gene?
                    YES -> Capture-C to confirm interaction
                           CRISPRi at variant position
                    NO  -> Consider:
                           - Multi-ancestry fine-mapping to narrow set
                           - ATAC-seq in disease tissue to find regulatory marks
                           - Computational prediction (DeepSEA, Enformer)
```

---

## Multi-Ancestry Fine-Mapping

### Why Multi-Ancestry Matters

```
Benefits:
- Different LD patterns across ancestries break apart correlated variants
- Credible sets shrink 2-5x on average with multi-ancestry data
- Reveals ancestry-specific causal variants
- Improves L2G predictions by reducing candidate gene ambiguity

Approach:
1. Run fine-mapping independently per ancestry
2. Combine using multi-ancestry methods (MR-MEGA, MANTRA, or meta-SuSiE)
3. Compare credible sets — variants in intersection are high-priority
4. Variants absent from one ancestry's credible set may be in LD with true causal
```

---

## Multi-Agent Workflow Examples

**"Fine-map the GWAS locus at 9p21 for coronary artery disease"**
1. GWAS Fine-Mapping -> Retrieve credible set variants, compute PIPs, identify top candidate (rs1333049 region), assess L2G for CDKN2A/B vs ANRIL
2. GWAS SNP Interpretation -> Annotate lead variants with functional consequences, allele frequencies, regulatory overlaps
3. GWAS Trait-to-Gene -> Prioritize CDKN2A vs CDKN2B vs ANRIL using full L2G evidence integration
4. Drug Target Analyst -> Assess druggability of prioritized gene, existing compounds, pathway context

**"Identify causal variants for type 2 diabetes at the TCF7L2 locus"**
1. GWAS Fine-Mapping -> Bayesian fine-mapping of TCF7L2 region, credible set construction, PIP computation
2. GWAS Study Explorer -> Retrieve all T2D GWAS studies reporting TCF7L2 associations, compare effect sizes across ancestries
3. GWAS Drug Discoverer -> Translate fine-mapped causal variant and effector gene into drug target hypothesis
4. Drug Target Analyst -> TCF7L2 druggability, Wnt pathway compounds, bioactivity data

**"Prioritize causal variants across 50 autoimmune disease loci for CRISPR screening"**
1. GWAS Fine-Mapping -> Compute credible sets for all 50 loci, rank by PIP, filter to T1/T2 tier variants
2. GWAS SNP Interpretation -> Annotate all T1/T2 variants with regulatory marks, eQTL status, CADD scores
3. GWAS Trait-to-Gene -> Assign effector genes to each locus using L2G, identify shared genes across diseases
4. Drug Target Analyst -> Druggability screen of top effector genes, identify existing compounds for repurposing

---

## Completeness Checklist

- [ ] Locus defined with disease ID resolved and genetic evidence retrieved from Open Targets
- [ ] Credible set constructed with variants ranked by posterior inclusion probability (PIP)
- [ ] Fine-mapping method selected and justified (SuSiE, FINEMAP, PAINTOR, or CAVIAR)
- [ ] Credible set quality assessed (set size, lead variant PIP, resolution tier)
- [ ] L2G scores retrieved and effector gene assigned with evidence breakdown
- [ ] Variant prioritization hierarchy applied (PIP, functional consequence, eQTL, conservation, chromatin)
- [ ] Evidence tier (T1-T4) assigned to fine-mapped variants
- [ ] Validation strategy recommended based on variant type (coding vs regulatory)
- [ ] Multi-ancestry fine-mapping potential assessed
- [ ] Report file created with no remaining `[Analyzing...]` placeholders
