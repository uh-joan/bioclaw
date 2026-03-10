---
name: gwas-trait-to-gene
description: GWAS trait-to-gene discovery and gene prioritization specialist. Systematically discovers genes linked to diseases and traits by querying GWAS data and applying gene prioritization methods. Use when user mentions trait-to-gene, GWAS gene discovery, gene prioritization, GWAS locus, lead SNP, genome-wide significant, p-value threshold, Bonferroni, L2G score, locus-to-gene, gene mapping, positional mapping, eQTL mapping, chromatin interaction, SNP aggregation, pleiotropy, pleiotropic gene, multiple testing correction, gene confidence, evidence ranking, GWAS catalog, trait association, or variant-to-gene.
---

# GWAS Trait-to-Gene

Systematically discovers genes linked to diseases and traits by querying GWAS data and applying gene prioritization methods. Uses Open Targets for GWAS associations and L2G predictions, PubMed for literature evidence, NLM for gene lookups and disease coding, DrugBank for pharmacological context, and ChEMBL for existing compound intelligence on prioritized genes.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_gwas-trait-to-gene_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- SNP-level interpretation and functional annotation → use `gwas-snp-interpretation`
- Translating GWAS genes into drug targets → use `gwas-drug-discoverer`
- GWAS study comparison and meta-analysis → use `gwas-study-explorer`
- Credible set and causal variant resolution → use `gwas-finemapping`
- Deep target validation and SAR analysis → use `drug-target-analyst`

## Cross-Reference: Other Skills

- **SNP-level interpretation and functional annotation** -> use gwas-snp-interpretation skill
- **Translating GWAS genes into drug targets** -> use gwas-drug-discoverer skill
- **GWAS study design and power analysis** -> use gwas-study-explorer skill
- **Credible set and causal variant resolution** -> use gwas-finemapping skill
- **Deep target validation and SAR analysis** -> use drug-target-analyst skill

## Available MCP Tools

### `mcp__opentargets__opentargets_info` (GWAS Associations & L2G — PRIMARY)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_targets` | Search targets by gene symbol/name | `query`, `size` |
| `search_diseases` | Search diseases by name/synonym | `query`, `size` |
| `get_target_disease_associations` | Evidence-scored target-disease links with genetic association breakdown | `targetId` (Ensembl ID), `diseaseId` (EFO ID), `minScore`, `size` |
| `get_disease_targets_summary` | All targets for a disease ranked by evidence | `diseaseId`, `minScore`, `size` |
| `get_target_details` | Full target info (function, pathways, tractability, genetic constraint) | `id` (Ensembl ID) |
| `get_disease_details` | Full disease info (ontology, phenotypes, known associations) | `id` (EFO ID) |

### `mcp__pubmed__pubmed_articles` (GWAS Literature)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Quick keyword search | `keywords`, `num_results` |
| `search_advanced` | Filtered search | `term`, `journal`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Full article details | `pmid` |

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

### `mcp__drugbank__drugbank_info` (Pharmacological Context)

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

### `mcp__chembl__chembl_info` (Compound Intelligence)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `compound_search` | Search molecules by name/SMILES/ID | `query`, `limit` |
| `target_search` | Search biological targets | `query`, `limit` |
| `get_bioactivity` | Compound-target activity data (IC50, Ki, EC50) | `chembl_id`, `target_id`, `limit` |
| `get_mechanism` | Mechanism of action | `chembl_id` |
| `drug_search` | Search drugs by indication or name | `query`, `limit` |
| `get_admet` | ADMET/drug-likeness properties | `chembl_id` |

### `mcp__gwas__gwas_data` (GWAS Catalog — Trait Associations & Gene Mapping)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_by_trait` | Search EFO traits by term, get associations for top match | `trait`, `page`, `size` |
| `search_associations` | Search associations by query or PubMed ID | `query`, `pubmed_id`, `page`, `size` |
| `get_variant` | Get variant info by rs ID | `rs_id` |
| `get_variant_associations` | All associations for a variant — cross-study replication evidence | `rs_id`, `page`, `size` |
| `get_gene_associations` | All GWAS associations for a gene — comprehensive trait-gene evidence | `gene`, `page`, `size` |
| `get_trait_associations` | All associations for an EFO trait ID | `efo_id`, `page`, `size` |
| `search_studies` | Search studies by disease trait name | `disease_trait`, `page`, `size` |
| `get_study` | Study details by GCST accession | `study_id` |
| `search_genes` | Gene info with genomic context | `gene` |
| `get_region_associations` | Associations in a genomic region — identifies all signals at a locus | `chromosome`, `start`, `end`, `page`, `size` |

**GWAS Catalog Workflow:** Use the GWAS Catalog as the primary source for trait-to-gene association discovery. In Step 1 (Trait Search), query `search_by_trait` to retrieve all GWAS associations for a trait, providing the initial locus list. In Step 2 (SNP Aggregation), use `get_region_associations` to identify all signals at each locus and `get_variant_associations` to check cross-study replication. In Step 3 (Gene Mapping), use `get_gene_associations` and `search_genes` to assess the full GWAS evidence landscape for each candidate gene — genes reported across multiple independent GWAS studies are stronger causal candidates. Use `get_study` to extract study-level metadata for evidence grading in Step 4.

```
# Retrieve all GWAS associations for a trait
mcp__gwas__gwas_data(method: "search_by_trait", trait: "type 2 diabetes")

# Get all GWAS associations for a candidate gene
mcp__gwas__gwas_data(method: "get_gene_associations", gene: "TCF7L2")

# Check cross-study replication for a lead variant
mcp__gwas__gwas_data(method: "get_variant_associations", rs_id: "rs7903146")
```

### `mcp__clinvar__clinvar_data` (ClinVar Causal Gene Evidence)

Use ClinVar to validate causal gene assignments at GWAS loci — genes with ClinVar pathogenic variants for related phenotypes provide independent evidence supporting GWAS gene prioritization and Mendelian-common disease convergence.

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

### `mcp__gnomad__gnomad_data` (Gene Constraint & Variant Landscape)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_gene_constraint` | Gene LoF intolerance metrics (pLI, LOEUF, missense Z-score) for target prioritization | `gene`, `dataset` |
| `batch_gene_constraint` | Compare constraint scores across multiple candidate genes at a locus simultaneously | `genes` (list), `dataset` |
| `get_gene_variants` | Full variant landscape in a candidate gene (coding, regulatory, clinical) | `gene`, `consequence_type`, `dataset` |

**gnomAD Workflow:** Use gnomAD gene constraint scores to prioritize candidate causal genes at GWAS loci. Genes with high pLI (> 0.9) or low LOEUF (< 0.35) are intolerant to loss-of-function variation, indicating essential or dosage-sensitive biology that strengthens their candidacy as causal genes. When multiple candidate genes exist at a locus, batch-query constraint scores to rank them -- the most constrained gene with supporting L2G evidence is the strongest candidate. The variant landscape within candidate genes further reveals whether the gene harbors known pathogenic or functional variants.

```
# Check constraint for a candidate causal gene
mcp__gnomad__gnomad_data(method: "get_gene_constraint", gene: "TCF7L2")

# Compare constraint across all candidate genes at a locus
mcp__gnomad__gnomad_data(method: "batch_gene_constraint", genes: ["TCF7L2", "VTI1A", "HABP2"])

# Explore the variant landscape in a prioritized gene
mcp__gnomad__gnomad_data(method: "get_gene_variants", gene: "TCF7L2", consequence_type: "lof")
```

### `mcp__monarch__monarch_data` (Gene-Disease-Phenotype Associations)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_gene_diseases` | Gene-disease evidence for GWAS candidate genes | `gene_id` |
| `get_gene_phenotypes` | Phenotype links for a gene | `gene_id` |
| `search` | Trait/disease search by name or synonym | `query`, `limit` |

**Monarch workflow:** Use Monarch gene-disease-phenotype data to prioritize causal genes at GWAS loci.

```
1. mcp__monarch__monarch_data(method: "search", query: "TRAIT_OR_DISEASE_NAME")
   → Resolve trait/disease to Monarch ID

2. mcp__monarch__monarch_data(method: "get_gene_diseases", gene_id: "HGNC:GENE_ID")
   → Gene-disease evidence supporting candidate gene causality

3. mcp__monarch__monarch_data(method: "get_gene_phenotypes", gene_id: "HGNC:GENE_ID")
   → Phenotype associations that corroborate GWAS trait biology
```

### `mcp__ensembl__ensembl_data` (Genomic Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `lookup_gene` | Get gene info by ID or symbol | `gene_id`, `species`, `expand` |
| `search_genes` | Search genes by name/description | `query`, `species`, `biotype`, `limit` |
| `get_homologs` | Get gene homologs across species | `gene_id`, `target_species`, `type` |
| `get_xrefs` | Get cross-database references | `gene_id`, `external_db`, `all_levels` |
| `get_transcripts` | Get transcripts for a gene | `gene_id`, `canonical_only` |

### `mcp__gtex__gtex_data` (Tissue Expression & eQTLs)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_genes` | Search genes in GTEx | `query`, `page`, `pageSize` |
| `get_single_tissue_eqtls` | eQTLs for a gene in a tissue | `gencodeId`, `tissueSiteDetailId`, `datasetId` |
| `get_multi_tissue_eqtls` | eQTLs across all tissues | `gencodeId`, `datasetId` |
| `get_gene_expression` | Expression across tissues | `gencodeId`, `tissueSiteDetailId` |

### `mcp__gwas__gwas_data` (GWAS Catalog — Locus-to-Gene Mapping Evidence)

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

**GWAS Catalog Workflow:** Use the GWAS Catalog to support locus-to-gene mapping with comprehensive association evidence. In Step 2 (SNP Aggregation), query `search_by_trait` or `get_trait_associations` to retrieve all genome-wide significant associations for the trait, providing the full locus catalog for gene mapping. In Step 3 (Gene Mapping), use `get_gene_associations` to check whether a candidate gene has GWAS associations reported directly (mapped gene in the catalog), and `search_genes` to retrieve the gene's genomic context for positional mapping. Use `get_region_associations` to identify all GWAS signals in a locus window — when multiple studies independently map to the same gene, this strengthens the L2G assignment and supports evidence ranking in Step 4.

---

## 5-Step Gene Discovery Pipeline

### Step 1: Trait Search

Identify the trait or disease of interest and resolve it to standardized identifiers.

```
1. mcp__opentargets__opentargets_info(method: "search_diseases", query: "TRAIT_OR_DISEASE_NAME")
   -> Get EFO disease ID, synonyms, ontology placement

2. mcp__nlm__nlm_ct_codes(method: "search_mesh", query: "TRAIT_OR_DISEASE_NAME")
   -> MeSH descriptor for literature searches and cross-referencing

3. mcp__nlm__nlm_ct_codes(method: "search_icd10", query: "TRAIT_OR_DISEASE_NAME")
   -> ICD-10 code for clinical coding context

4. mcp__nlm__nlm_ct_codes(method: "search_snomed", query: "TRAIT_OR_DISEASE_NAME")
   -> SNOMED CT code for precise clinical concept mapping

5. mcp__pubmed__pubmed_articles(method: "search_advanced", term: "TRAIT_NAME GWAS genome-wide association study", journal: "", start_date: "", end_date: "", num_results: 20)
   -> Identify published GWAS for this trait, sample sizes, ancestry composition
```

### Step 2: SNP Aggregation at Genome-Wide Significance

Retrieve all genome-wide significant associations and aggregate SNPs by locus.

```
1. mcp__opentargets__opentargets_info(method: "get_disease_targets_summary", diseaseId: "EFO_xxxxxxx", minScore: 0.1, size: 100)
   -> All targets with genetic evidence for this trait, ranked by association strength

2. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "TRAIT_NAME genome-wide significant loci SNP", num_results: 20)
   -> Published locus lists from major GWAS — identifies lead SNPs and mapped genes

3. mcp__pubmed__pubmed_articles(method: "search_advanced", term: "TRAIT_NAME GWAS meta-analysis", journal: "", start_date: "", end_date: "", num_results: 10)
   -> Meta-analyses with largest sample sizes yield most comprehensive locus catalogs
```

**Genome-Wide Significance Threshold:**
- Standard threshold: p < 5x10^-8 (Bonferroni correction across ~1 million independent common variants)
- Suggestive threshold: p < 1x10^-5 (requires replication in independent cohort)
- Multiple testing: correction for ~1M independent tests in European-ancestry LD structure; trans-ethnic analyses may require adjusted thresholds

**SNP Aggregation Rules:**
```
Locus definition:
- Group SNPs within +/- 500kb of the lead variant (lowest p-value)
- Or use LD-based clumping: r^2 > 0.1 within 1Mb window
- Each independent locus = one signal (unless conditional analysis reveals multiple)

LD awareness (CRITICAL):
- The lead SNP is the one with the smallest p-value, NOT necessarily the causal variant
- Associated SNP may TAG the causal variant through linkage disequilibrium
- Association != Causation at the variant level
- Fine-mapping is required to resolve the causal variant within a locus
- LD patterns differ across ancestries — multi-ancestry data helps narrow candidates
```

### Step 3: Gene Mapping Extraction

Map each genome-wide significant locus to candidate causal genes using multiple evidence lines.

```
1. For each top target from Step 2:
   mcp__opentargets__opentargets_info(method: "search_targets", query: "GENE_SYMBOL")
   -> Get Ensembl gene ID, verify gene identity

2. mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   -> Full gene profile: function, subcellular location, pathways, genetic constraint

3. mcp__nlm__nlm_ct_codes(method: "search_gene", query: "GENE_SYMBOL")
   -> Gene aliases, chromosomal location, functional annotation

4. mcp__nlm__nlm_ct_codes(method: "get_gene_details", gene_id: "GENE_ID")
   -> Detailed gene record: expression, orthologs, known phenotypes

5. mcp__nlm__nlm_ct_codes(method: "search_omim", query: "GENE_SYMBOL")
   -> Mendelian disease associations (strongest form of gene-disease evidence)

6. mcp__ensembl__ensembl_data(method: "lookup_gene", gene_id: "GENE_SYMBOL", species: "homo_sapiens", expand: true)
   -> Gene boundaries, biotype, strand — confirm positional mapping

7. mcp__ensembl__ensembl_data(method: "get_homologs", gene_id: "ENSG00000xxxxx", type: "orthologues")
   -> Orthologs across species — supports conservation-based gene prioritization

8. mcp__ensembl__ensembl_data(method: "get_xrefs", gene_id: "ENSG00000xxxxx", all_levels: true)
   -> Cross-references to UniProt, HGNC, RefSeq for ID reconciliation

9. mcp__gtex__gtex_data(method: "search_genes", query: "GENE_SYMBOL")
   -> Get GENCODE ID for GTEx eQTL and expression queries

10. mcp__gtex__gtex_data(method: "get_single_tissue_eqtls", gencodeId: "ENSG00000xxxxx.xx", tissueSiteDetailId: "RELEVANT_TISSUE")
    -> eQTL evidence for causal gene assignment — variant affecting gene expression in disease-relevant tissue is strong mapping evidence
```

**Gene Mapping Methods:**

| Method | What it captures | Confidence |
|--------|-----------------|------------|
| **Positional (nearest gene)** | Gene closest to lead SNP | Low — often incorrect, especially in gene deserts |
| **eQTL colocalization** | Variant affects gene expression; GWAS and eQTL signals share the same causal variant | High when colocalization posterior probability > 0.8 |
| **pQTL colocalization** | Variant affects protein levels | Very high — direct protein-level evidence |
| **Chromatin interaction (Hi-C, PCHi-C)** | 3D genome contact between variant-containing region and gene promoter | Medium-high — cell-type specific |
| **Coding variant in LD** | Missense/nonsense variant in LD with lead SNP | High — directly implicates the gene |
| **Rare variant burden** | Gene-level aggregation of rare damaging variants | High — independent of GWAS LD structure |
| **L2G machine learning** | Integrates all above into a single score | Best available composite prediction |

### Step 4: Evidence Ranking

Rank candidate genes by strength of evidence linking them to the trait.

```
1. mcp__opentargets__opentargets_info(method: "get_target_disease_associations", targetId: "ENSG00000xxxxx", diseaseId: "EFO_xxxxxxx")
   -> Association score with evidence breakdown (genetic, somatic, literature, known drugs, animal models)

2. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_SYMBOL TRAIT_NAME functional validation", num_results: 15)
   -> Published functional studies supporting causal role

3. mcp__nlm__nlm_ct_codes(method: "search_omim", query: "GENE_SYMBOL")
   -> Mendelian disease concordance (e.g., rare mutations in same gene cause related phenotype)

4. mcp__drugbank__drugbank_info(method: "search_by_target", target: "GENE_SYMBOL", limit: 10)
   -> Pharmacological evidence: do drugs targeting this gene affect the trait?

5. mcp__chembl__chembl_info(method: "target_search", query: "GENE_SYMBOL")
   -> Known chemical probes and tool compounds for functional interrogation
```

**Evidence Grading Tiers:**

| Tier | Criteria | Interpretation |
|------|----------|----------------|
| **T1 -- Validated** | Genome-wide significant (p < 5x10^-8), high L2G (>0.7), multiple evidence lines (eQTL + coding + chromatin), replicated across ancestries, Mendelian disease concordance | Causal gene with high confidence |
| **T2 -- Strong** | Genome-wide significant, moderate L2G (0.5-0.7), at least one functional evidence line (eQTL or coding variant), single-ancestry replication | Likely causal gene, suitable for follow-up |
| **T3 -- Moderate** | Genome-wide significant, low L2G (<0.5) or positional mapping only, no functional evidence yet | Gene assignment uncertain, requires fine-mapping |
| **T4 -- Emerging** | Suggestive association (p < 1x10^-5), or significant locus in gene desert with no clear effector gene, or single small study without replication | Hypothesis-generating, monitor for replication |

### Step 5: L2G Annotation

Apply Locus-to-Gene (L2G) predictions to assign confidence scores to gene-locus pairs.

```
1. mcp__opentargets__opentargets_info(method: "get_target_disease_associations", targetId: "ENSG00000xxxxx", diseaseId: "EFO_xxxxxxx")
   -> L2G score embedded in genetic evidence — extract ot_genetics_portal data

2. mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   -> Genetic constraint scores (pLI, LOEUF) — highly constrained genes more likely causal

3. mcp__pubmed__pubmed_articles(method: "search_advanced", term: "GENE_SYMBOL locus-to-gene fine-mapping colocalization", journal: "", start_date: "", end_date: "", num_results: 10)
   -> Published fine-mapping and colocalization studies refining gene assignment

4. mcp__nlm__nlm_ct_codes(method: "get_gene_details", gene_id: "GENE_ID")
   -> Gene function and expression context to evaluate biological plausibility
```

**L2G Score Interpretation:**

The L2G (Locus-to-Gene) model integrates multiple evidence sources into a single prediction score (0-1) for the probability that a gene is the causal gene at a GWAS locus.

```
L2G input features:
- Distance: variant-to-gene distance (nearest gene, nearest protein-coding gene)
- Molecular QTL: eQTL and pQTL colocalization across tissues
- Chromatin interaction: PCHi-C and enhancer-promoter contacts
- Variant pathogenicity: coding consequence (VEP), regulatory annotations
- Gene constraint: pLI, LOEUF (o/e loss-of-function)

L2G is a machine learning model trained on gold-standard causal genes
(Mendelian disease genes at GWAS loci) — it predicts which gene at a
locus is most likely causal, NOT whether the locus itself is causal.
```

---

## Gene Prioritization Output Format

For each trait-gene association discovered, produce a structured prioritization record:

```
Gene Prioritization Record:
---------------------------
Gene Symbol:        [HGNC symbol]
Ensembl ID:         [ENSG00000xxxxx]
Chromosome:         [chr:start-end]
Minimum P-value:    [smallest p-value from GWAS]
Evidence Count:     [number of independent GWAS reporting this gene-trait association]
L2G Score:          [0-1, from Open Targets Genetics]
Confidence:         [HIGH / MEDIUM / LOW]
Evidence Tier:      [T1 / T2 / T3 / T4]
Mapping Methods:    [positional, eQTL, pQTL, chromatin, coding, rare variant]
Mendelian Link:     [OMIM disease if concordant, or "None"]
Druggability:       [tractability category from Open Targets]
Existing Drugs:     [count and names from DrugBank]
Pleiotropy:         [other traits associated with same gene]
```

### Gene Confidence Tiers

| Confidence | L2G Score | Evidence Requirements | Interpretation |
|------------|-----------|----------------------|----------------|
| **HIGH** | > 0.7 | Multiple independent evidence lines (eQTL + coding + chromatin interaction), replicated across studies or ancestries | Gene assignment is robust; proceed to functional validation or drug target assessment |
| **MEDIUM** | 0.5 - 0.7 | At least one functional evidence line beyond positional mapping, or strong positional evidence with biological plausibility | Gene is the likely candidate; additional fine-mapping or colocalization recommended |
| **LOW** | < 0.5 | Positional mapping only, or single weak evidence line, or gene desert locus | Gene assignment uncertain; exercise caution, consider alternative candidates at the locus |

---

## Pleiotropy Detection

### Workflow

Identify genes associated with multiple traits to detect pleiotropic effects.

```
1. mcp__opentargets__opentargets_info(method: "search_targets", query: "GENE_SYMBOL")
   -> Get Ensembl ID

2. mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   -> Review all associated diseases/traits for this target

3. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_SYMBOL pleiotropic pleiotropy GWAS multiple traits", num_results: 15)
   -> Published pleiotropy analyses

4. mcp__nlm__nlm_ct_codes(method: "search_omim", query: "GENE_SYMBOL")
   -> Mendelian pleiotropic effects (single gene, multiple phenotypes)

5. mcp__drugbank__drugbank_info(method: "search_by_target", target: "GENE_SYMBOL", limit: 20)
   -> Drugs for this target across different indications reveal clinical pleiotropy
```

**Pleiotropy Interpretation:**

```
Types of pleiotropy in GWAS:
1. Biological pleiotropy (true):
   - Same gene causally influences multiple traits through shared biology
   - Example: APOE affects both Alzheimer's and lipid levels
   - Implication: drugging this target may affect multiple traits simultaneously

2. Mediated pleiotropy (vertical):
   - Gene affects trait A, which causes trait B
   - Example: FTO affects BMI, which affects type 2 diabetes risk
   - Implication: intervening on the upstream trait may resolve downstream effects

3. Spurious pleiotropy (LD-driven):
   - Different causal variants in LD each affect different traits
   - Appears pleiotropic at locus level but distinct at variant level
   - Implication: fine-mapping resolves this — different genes may be causal for different traits

Assessment checklist:
+ Same lead variant for multiple traits? -> likely true pleiotropy
+ Same gene but different lead variants? -> check if same causal variant via colocalization
+ Same locus but different genes for different traits? -> LD-driven, not true gene-level pleiotropy
+ Direction of effect consistent across traits? -> concordant pleiotropy (favorable for drug targeting)
+ Direction of effect discordant? -> antagonistic pleiotropy (safety concern for drug targeting)
```

---

## Association vs. Causation Framework

### Critical Distinction: LD Awareness

```
GWAS reports ASSOCIATION between a variant and a trait.
Association does NOT equal causation at the variant level.

Why?
- GWAS tests tag SNPs on genotyping arrays (or imputed variants)
- The associated SNP may be in linkage disequilibrium (LD) with the true causal variant
- LD blocks can span 10kb to >1Mb depending on the genomic region
- The causal variant may be:
  (a) The lead SNP itself (sometimes)
  (b) A nearby variant in strong LD (r^2 > 0.8) with the lead SNP
  (c) Multiple causal variants at the same locus (allelic heterogeneity)

Resolving causality requires:
1. Fine-mapping: statistical methods (SuSiE, FINEMAP, CARMA) to identify
   credible sets of likely causal variants
2. Colocalization: testing whether GWAS and QTL signals share the same
   causal variant (methods: coloc, eCAVIAR, HyPrColoc)
3. Functional validation: experimental testing of candidate causal variants
   (CRISPR editing, reporter assays, allele-specific expression)

Similarly, at the GENE level:
- The nearest gene is NOT always the causal gene
- Up to 50% of GWAS loci may have a causal gene that is NOT the nearest gene
- Regulatory variants can act over long distances (>1Mb) via chromatin looping
- Always use L2G and multiple mapping methods rather than defaulting to nearest gene
```

### Multiple Testing Correction

```
Genome-wide significance threshold: p < 5x10^-8

Derivation:
- Human genome has ~10 million common variants (MAF > 1%)
- Due to LD, these represent ~1 million independent tests
- Bonferroni correction: 0.05 / 1,000,000 = 5x10^-8
- This is conservative but widely accepted as the field standard

Context for interpretation:
- p = 5x10^-8 is NOT the same as "definitely real" — replication is still needed
- p = 1x10^-7 is NOT "almost significant" — it fails the threshold
- Suggestive associations (5x10^-8 < p < 1x10^-5) may be real in larger samples
- Bayesian approaches (posterior probability) complement frequentist thresholds
- For phenome-wide scans (PheWAS), additional correction across traits is needed
```

---

## L2G Integration: Detailed Feature Breakdown

### L2G Feature Categories and Weights

| Feature Category | Examples | Contribution |
|-----------------|----------|--------------|
| **Distance** | Distance to gene TSS, distance to gene body | Baseline (nearest gene often correct, but not always) |
| **Molecular QTL** | eQTL colocalization (GTEx, eQTLGen), pQTL colocalization (deCODE, UKB-PPP) | High — direct molecular link between variant and gene expression/protein |
| **Chromatin** | PCHi-C contacts, enhancer-gene predictions (ABC model, EpiMap) | Medium-high — 3D genome evidence for regulatory contact |
| **Variant annotation** | VEP consequence (coding, splice), CADD score, regulatory element overlap | Medium — functional impact of the variant itself |
| **Gene properties** | pLI (loss-of-function intolerance), LOEUF, gene expression in relevant tissue | Supportive — biological plausibility |

### L2G Validation Approach

```
1. Check L2G score for gene of interest:
   mcp__opentargets__opentargets_info(method: "get_target_disease_associations",
     targetId: "ENSG00000xxxxx", diseaseId: "EFO_xxxxxxx")
   -> Extract L2G score from genetic evidence

2. Cross-validate with independent evidence:
   mcp__nlm__nlm_ct_codes(method: "search_omim", query: "GENE_SYMBOL")
   -> Does a Mendelian disease in the same gene cause a related phenotype?

3. Check for coding variants in the gene:
   mcp__pubmed__pubmed_articles(method: "search_keywords",
     keywords: "GENE_SYMBOL coding variant missense functional", num_results: 10)
   -> Coding variants provide gene-level evidence independent of L2G

4. Assess biological plausibility:
   mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   -> Gene function, pathway membership, expression pattern

5. Pharmacological validation:
   mcp__drugbank__drugbank_info(method: "search_by_target", target: "GENE_SYMBOL")
   -> Do drugs targeting this gene have effects consistent with the trait?
```

---

## Trait-Specific Gene Discovery Workflows

### Complex Trait (Polygenic)

For highly polygenic traits (e.g., height, BMI, schizophrenia) with hundreds of loci:

```
1. mcp__opentargets__opentargets_info(method: "search_diseases", query: "TRAIT_NAME")
   -> Resolve to EFO ID

2. mcp__opentargets__opentargets_info(method: "get_disease_targets_summary",
     diseaseId: "EFO_xxxxxxx", minScore: 0.1, size: 100)
   -> Retrieve ALL genetically associated targets (expect many)

3. Apply confidence filters:
   - HIGH confidence (L2G > 0.7 + multiple evidence): prioritize for mechanistic analysis
   - MEDIUM confidence (L2G 0.5-0.7): include in pathway enrichment
   - LOW confidence (L2G < 0.5): include in gene set analysis but not individual follow-up

4. mcp__pubmed__pubmed_articles(method: "search_advanced",
     term: "TRAIT_NAME GWAS pathway gene set enrichment", journal: "", start_date: "", end_date: "", num_results: 15)
   -> Identify convergent biological pathways across many loci

5. For top-priority genes:
   mcp__chembl__chembl_info(method: "target_search", query: "GENE_SYMBOL")
   -> Identify druggable targets among the gene list
```

### Rare Disease (Mendelian Overlap)

For traits where GWAS loci overlap with known Mendelian disease genes:

```
1. mcp__opentargets__opentargets_info(method: "get_disease_targets_summary",
     diseaseId: "EFO_xxxxxxx", minScore: 0.3, size: 50)
   -> Genetically associated targets

2. For each candidate gene:
   mcp__nlm__nlm_ct_codes(method: "search_omim", query: "GENE_SYMBOL")
   -> Check for Mendelian disease in the same phenotypic spectrum

3. mcp__nlm__nlm_ct_codes(method: "get_gene_details", gene_id: "GENE_ID")
   -> Gene function, known disease associations

4. mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   -> Genetic constraint (pLI, LOEUF) — highly constrained genes with
      GWAS + Mendelian evidence are strongest causal candidates

5. mcp__pubmed__pubmed_articles(method: "search_keywords",
     keywords: "GENE_SYMBOL Mendelian GWAS common rare variant", num_results: 10)
   -> Published analyses connecting common and rare variant evidence
```

---

## Multi-Agent Workflow Examples

**"Discover genes associated with type 2 diabetes from GWAS"**
1. GWAS Trait-to-Gene -> Full 5-step pipeline: trait search, SNP aggregation, gene mapping, evidence ranking, L2G annotation; produce prioritized gene list with confidence tiers
2. GWAS SNP Interpretation -> Functional annotation of lead variants at each locus, regulatory overlap, eQTL lookups
3. Drug Target Analyst -> Druggability assessment and existing compound analysis for HIGH-confidence genes
4. GWAS Drug Discoverer -> Translate prioritized genes into drug repurposing opportunities

**"Identify pleiotropic genes shared between Alzheimer's and cardiovascular disease"**
1. GWAS Trait-to-Gene -> Run gene discovery pipeline for both traits independently, then intersect gene lists; flag shared genes with concordant/discordant effect directions
2. GWAS Study Explorer -> Identify largest GWAS for each trait, assess power and ancestry composition
3. Drug Target Analyst -> For shared pleiotropic targets, assess druggability and safety implications of modulating a shared pathway
4. GWAS Finemapping -> Colocalization analysis to distinguish true pleiotropy from LD-driven co-occurrence

**"Prioritize novel genes from a new Crohn's disease GWAS"**
1. GWAS Trait-to-Gene -> Ingest locus list, apply L2G scoring, classify genes into HIGH/MEDIUM/LOW confidence tiers, detect novel genes not previously reported
2. GWAS SNP Interpretation -> Annotate lead SNPs with functional consequences, eQTL effects, regulatory element overlap
3. GWAS Finemapping -> Generate credible sets for novel loci, refine gene assignment with posterior probabilities
4. Drug Target Analyst -> Deep target characterization for novel HIGH-confidence genes, competitive landscape analysis

**"Assess whether APOE is a reliable GWAS gene for Alzheimer's"**
1. GWAS Trait-to-Gene -> Evidence ranking for APOE-Alzheimer's association: L2G score, evidence count, p-value, multiple mapping methods, Mendelian concordance (APOE e4), pleiotropy detection (lipids, longevity)
2. Drug Target Analyst -> Existing drugs and compounds targeting APOE or its pathway, bioactivity data
3. GWAS Drug Discoverer -> Druggability evaluation, direction-of-effect analysis, repurposing candidates
4. GWAS Study Explorer -> Review all GWAS reporting APOE, sample sizes, ancestry representation, replication status

---

## Completeness Checklist

- [ ] Trait resolved to standardized identifiers (EFO, MeSH, ICD-10, SNOMED)
- [ ] All genome-wide significant loci retrieved and SNPs aggregated by locus
- [ ] Gene mapping performed using multiple methods (positional, eQTL, chromatin, coding, L2G)
- [ ] L2G scores retrieved for each candidate gene with evidence breakdown
- [ ] Evidence ranking completed with tiers (T1-T4) assigned to each gene
- [ ] Gene confidence classified as HIGH/MEDIUM/LOW based on L2G and evidence lines
- [ ] Pleiotropy detection performed for top-priority genes
- [ ] Mendelian disease concordance checked via OMIM for candidate genes
- [ ] Gene prioritization records produced in structured output format
- [ ] Report file created with no remaining `[Analyzing...]` placeholders
