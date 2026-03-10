---
name: regulatory-genomics
description: "Non-coding variant interpretation, enhancer analysis, transcription factor binding, eQTL mapping, chromatin state annotation, gene regulation"
---

# Regulatory Genomics

> **Code recipes**: See [scenic-recipes.md](scenic-recipes.md) for pySCENIC GRN inference, cisTarget regulon pruning, AUCell scoring, SCENIC+, WGCNA co-expression networks, ARACNe-AP, and differential regulon activity analysis.

Specialist in non-coding genome interpretation and gene regulation. Analyzes regulatory variants by integrating chromatin state annotations (ChromHMM, ENCODE), transcription factor binding site disruption, expression quantitative trait loci (eQTL) from GTEx, enhancer-gene linking via chromatin interactions and activity-by-contact models, and conservation-based constraint metrics. Produces scored regulatory variant impact assessments with explicit evidence attribution across chromatin accessibility, TF motif disruption, eQTL support, evolutionary constraint, and functional validation data. Writes and executes Python code for position weight matrix scoring, eQTL effect size visualization, chromatin state enrichment analysis, and regulatory element overlap statistics.

## Report-First Workflow

1. **Create report file immediately**: `[variant_or_region]_regulatory_genomics_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Clinical coding variant classification (ACMG/AMP framework) → use `variant-interpretation`
- GWAS SNP annotation, LD expansion, and locus-to-gene mapping → use `gwas-snp-interpretation`
- DNA methylation, histone modification ChIP-seq, and ATAC-seq analysis → use `epigenomics`
- Differential gene expression and RNA-seq count-based pipelines → use `rnaseq-deseq2`
- Single-cell chromatin accessibility and gene expression → use `single-cell-analysis`
- Fine-mapping of causal variants at GWAS loci → use `gwas-finemapping`

## Cross-Reference: Other Skills

- **Clinical coding variant classification (ACMG/AMP framework)** -> use variant-interpretation skill
- **GWAS SNP annotation, LD expansion, and locus-to-gene mapping** -> use variant-analysis skill
- **DNA methylation, histone modification ChIP-seq, and ATAC-seq analysis** -> use epigenomics skill
- **Differential gene expression and RNA-seq count-based pipelines** -> use rnaseq-deseq2 skill
- **Single-cell chromatin accessibility and gene expression** -> use single-cell-analysis skill

## Python Environment

| Package | Purpose |
|---------|---------|
| `pandas`, `numpy` | Data manipulation and numerical computation |
| `scipy` | Statistical tests, position weight matrix scoring, Fisher's exact test |
| `statsmodels` | Linear regression, multiple testing correction, colocalization statistics |
| `scikit-learn` | PCA, clustering, machine learning for regulatory prediction models |
| `matplotlib`, `seaborn` | Visualization (heatmaps, effect size plots, enrichment charts, motif logos) |
| `pybedtools` | BED file manipulation for regulatory element overlaps |
| `gseapy` | Gene set enrichment on regulated gene lists |

---

## Available MCP Tools

### `mcp__ensembl__ensembl_data` (Regulatory Element Annotation)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_gene_info` | Gene coordinates, biotype, strand, description | `gene_id`, `species` |
| `get_regulatory_features` | ENCODE regulatory elements overlapping a region (promoters, enhancers, CTCF sites, open chromatin) | `region`, `species` |
| `get_variants` | Known variants at a position with population frequencies and clinical significance | `variant_id`, `species` |
| `get_variant_consequences` | Predict regulatory and coding variant effects via VEP (consequence type, impact, regulatory annotations) | `variants` (HGVS array) |
| `get_overlap_region` | All features overlapping a genomic interval (genes, regulatory elements, constrained elements, motifs) | `region`, `species`, `feature_type` |

### `mcp__gtex__gtex_data` (eQTL Data & Tissue Expression)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_gene_expression` | Expression levels across GTEx tissues for a gene | `gencodeId`, `tissueSiteDetailId` |
| `get_single_tissue_eqtls` | cis-eQTLs for a gene in a specific tissue (p-value, NES, MAF) | `gencodeId`, `tissueSiteDetailId` |
| `get_multi_tissue_eqtls` | eQTLs across all GTEx tissues for cross-tissue regulatory comparison | `gencodeId` |
| `search_genes` | Search genes in GTEx database by symbol or name to get GENCODE IDs | `query`, `page`, `pageSize` |

### `mcp__opentargets__ot_data` (Variant-to-Gene Evidence)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_target` | Search targets by gene symbol or name | `query`, `size` |
| `get_target_info` | Full target details: function, constraint metrics, pathways, tractability | `id` (Ensembl ID) |
| `get_associations` | Evidence-scored variant-disease and target-disease links with L2G breakdown | `targetId`, `diseaseId`, `minScore`, `size` |

### `mcp__pubmed__pubmed_data` (Regulatory Genomics Literature)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search` | Search PubMed for regulatory genomics, enhancer, eQTL, and chromatin publications | `keywords`, `num_results` |
| `fetch_details` | Retrieve full article metadata including abstract, authors, journal by PMID | `pmid` |

### `mcp__geneontology__go_data` (Transcription Factor Activity Terms)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_go_terms` | Find GO terms for TF activity, chromatin binding, enhancer function, transcriptional regulation | `query`, `max` |
| `get_go_term` | Full GO term details with definitions, parent/child relationships, and cross-references | `id` (GO:XXXXXXX) |

### `mcp__kegg__kegg_data` (Signaling Pathways Regulated by TFs)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_pathway` | Retrieve pathway details including gene members and metabolic/signaling reactions | `pathway_id` |
| `find_pathway` | Search pathways by keyword (e.g., "MAPK signaling", "Wnt pathway", "Notch signaling") | `query`, `organism` |

### `mcp__reactome__reactome_data` (Gene Expression Regulation Pathways)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_pathways` | Search for gene regulation, transcription, and chromatin remodeling pathways | `query`, `species` |
| `get_pathway` | Full pathway details with reactions, participants, and literature references | `pathway_id` |

### `mcp__uniprot__uniprot_data` (TF Protein Information)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_proteins` | Search for transcription factors and DNA-binding proteins by name or domain | `query`, `organism`, `size` |
| `get_protein` | Full protein record: DNA-binding domains (zinc finger, bHLH, homeodomain), GO annotations, interactions | `accession` |

### `mcp__stringdb__stringdb_data` (TF Regulatory Networks)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_network` | Protein-protein interaction network for TF complexes and co-regulators | `identifiers`, `species`, `required_score` |
| `get_enrichment` | Functional enrichment (GO, KEGG, Reactome) of TF regulatory network members | `identifiers`, `species` |

### `mcp__gnomad__gnomad_data` (Population Variant Frequencies in Regulatory Regions)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_variants_by_region` | Retrieve all variants within a genomic interval — use to catalog population variation across regulatory elements (enhancers, promoters, CTCF sites) | `region`, `dataset` |
| `get_variant` | Variant-level annotation including allele frequencies, filtering status, and population-specific counts — use for regulatory variant characterization | `variant_id`, `dataset` |
| `get_gene_constraint` | Gene-level constraint metrics (pLI, LOEUF, missense Z) — provides intolerance context for genes regulated by the element under analysis | `gene_id` |

#### gnomAD Workflow: Regulatory Region Variant Assessment

```
Query gnomAD for variants within regulatory elements to assess constraint
and population frequency of regulatory variants:

1. mcp__gnomad__gnomad_data(method: "search_variants_by_region", region: "1:12000-12500", dataset: "gnomad_r4")
   -> All population variants overlapping the regulatory element
   -> Identify common vs. rare variation density across the element
   -> Depleted variation in constrained regulatory regions suggests purifying selection

2. mcp__gnomad__gnomad_data(method: "get_variant", variant_id: "1-12345-A-G", dataset: "gnomad_r4")
   -> Allele frequency, population breakdown, filtering status for specific regulatory variant
   -> Ultra-rare (AF < 0.0001) variants in active regulatory elements are higher priority

3. mcp__gnomad__gnomad_data(method: "get_gene_constraint", gene_id: "ENSG00000xxxxx")
   -> Constraint metrics for the target gene regulated by the element
   -> Highly constrained genes (LOEUF < 0.35) imply regulatory variants may also be deleterious
```

### `mcp__jaspar__jaspar_data` (CORE: Transcription Factor Binding Profiles)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_matrices` | Find TF binding profiles by TF name, species, family | `tf_name`, `species`, `family` |
| `get_matrix` | Get specific TF binding matrix (PFM, consensus) | `matrix_id` |
| `get_pwm` | Compute position weight matrix (log-odds scores) for scoring | `matrix_id` |
| `scan_sequence` | Scan DNA sequence for TF binding sites | `matrix_id`, `sequence` |
| `variant_impact` | CORE: Assess variant effect on TF binding (ref vs alt) | `matrix_id`, `ref_sequence`, `alt_sequence` |
| `list_collections` | Available JASPAR collections (CORE, UNVALIDATED, etc.) | |
| `list_species` | Available species | |

#### JASPAR TF Binding Site Variant Impact Analysis

```
Assess the impact of variants on transcription factor binding using JASPAR
position weight matrices — CORE capability for regulatory variant interpretation:

1. mcp__jaspar__jaspar_data(method="search_matrices", tf_name="CTCF", species="9606")
   -> Identify TFs of interest and retrieve their JASPAR matrix IDs
   -> Filter by species (9606 = human), TF family, or TF class

2. mcp__jaspar__jaspar_data(method="get_pwm", matrix_id="MA0139.1")
   -> Get the position weight matrix for the TF
   -> Log-odds scores at each position for A, C, G, T

3. mcp__jaspar__jaspar_data(method="variant_impact", matrix_id="MA0139.1", ref_sequence="CCGCGNGGNGGCAG", alt_sequence="CCGCGNGGNGTCAG")
   -> Assess variant effect on TF binding: compare ref vs alt sequence scores
   -> Interpret result: creates_binding, disrupts_binding, increases_binding, decreases_binding

4. mcp__jaspar__jaspar_data(method="scan_sequence", matrix_id="MA0139.1", sequence="<regulatory_region>")
   -> Scan an entire regulatory region for all TF binding sites
   -> Identify all predicted binding locations and their scores

5. Interpretation:
   -> creates_binding: variant introduces a new TF binding site (gain-of-function)
   -> disrupts_binding: variant abolishes an existing TF binding site (loss-of-function)
   -> increases_binding: variant strengthens TF affinity at an existing site
   -> decreases_binding: variant weakens TF affinity without fully disrupting the site
```

---

## Core Workflows

### Workflow 1: Non-Coding Variant Prioritization

Systematically score and rank non-coding variants for regulatory impact using multiple evidence layers: pathogenicity scores, RegulomeDB categories, and ENCODE/Roadmap chromatin states.

#### Step 1: Variant Annotation with Regulatory Features

```
1. mcp__ensembl__ensembl_data(method: "get_variant_consequences", variants: ["chr1:g.12345A>G"])
   -> VEP annotation: regulatory_region_variant, TF_binding_site_variant, upstream_gene_variant, etc.
2. mcp__ensembl__ensembl_data(method: "get_regulatory_features", region: "1:12000-12500", species: "homo_sapiens")
   -> Overlapping ENCODE regulatory elements: promoter, enhancer, CTCF_binding_site, open_chromatin_region
3. mcp__ensembl__ensembl_data(method: "get_overlap_region", region: "1:12000-12500", species: "homo_sapiens", feature_type: "constrained")
   -> GERP constrained elements overlapping the variant position
4. mcp__opentargets__ot_data(method: "search_target", query: "NEAREST_GENE", size: 5)
   -> Ensembl gene ID for downstream queries and genetic constraint metrics
```

#### Step 2: Non-Coding Pathogenicity Scores

```
Score          Range         Interpretation
CADD (Phred)   0-99          >10 = top 10% deleterious; >20 = top 1%; >30 = top 0.1%
DANN           0-1           >0.98 = highly deleterious; neural network-based
Eigen          -inf to +inf  >0 = predicted deleterious; unsupervised spectral approach
FATHMM-MKL    0-1           >0.5 = deleterious; multiple kernel learning
ReMM           0-1           >0.5 = regulatory mendelian mutation candidate
LINSIGHT       0-1           >0.5 = fitness-reducing; integrates INSIGHT with genomic features
DeepSEA        0-1           >0.5 = predicted functional; deep learning on chromatin features
Sei            Profile       Sequence effect on 40 chromatin classes; identifies regulatory activity type
```

#### Step 3: RegulomeDB Scoring System

```
Category   Score   Evidence Composition
1a         1       eQTL + TF binding + matched TF motif + DNase peak
1b         1       eQTL + TF binding + any motif + DNase peak
1c         1       eQTL + TF binding + DNase peak
1d         1       eQTL + TF binding + matched TF motif
1e         1       eQTL + TF binding + any motif
1f         2       eQTL + TF binding
2a         2       TF binding + matched TF motif + DNase peak
2b         2       TF binding + any motif + DNase peak
2c         3       TF binding + matched TF motif
3a         3       TF binding + any motif
3b         4       TF binding + DNase peak
4          4       TF binding or DNase peak
5          5       TF binding or DNase peak (minimal evidence)
6          6       Motif hit only (no experimental binding data)
7          7       No evidence of regulatory function

Interpretation thresholds:
  Categories 1a-1f: Strong evidence of regulatory function (eQTL-supported)
  Categories 2a-3b: Likely regulatory (TF binding evidence without eQTL)
  Categories 4-5: Minimal binding evidence; low confidence
  Categories 6-7: No or weak evidence; deprioritize
```

#### Step 4: ENCODE/Roadmap Chromatin State Cross-Reference

```
5. Map variant position to ChromHMM 15-state model in disease-relevant tissue(s)
6. Check DNase I hypersensitivity signal in matched cell types
7. Overlay histone mark signals:
   - H3K4me1 + H3K27ac = active enhancer
   - H3K4me3 + H3K27ac = active promoter
   - H3K4me1 + H3K27me3 = poised/bivalent enhancer
   - H3K27me3 alone = Polycomb-repressed
8. Aggregate across Roadmap reference epigenomes (127 tissues/cell types)
```

---

### Workflow 2: Enhancer-Gene Linking

Connect distal regulatory elements to their target genes using multiple orthogonal evidence types.

#### eQTL-Based Linking

```
1. mcp__gtex__gtex_data(method: "search_genes", query: "GENE_SYMBOL")
   -> Get GENCODE ID for GTEx queries
2. mcp__gtex__gtex_data(method: "get_single_tissue_eqtls", gencodeId: "ENSG00000xxxxx.xx", tissueSiteDetailId: "Liver")
   -> cis-eQTLs within 1Mb of gene TSS; p-value, normalized effect size (NES), MAF
3. mcp__gtex__gtex_data(method: "get_multi_tissue_eqtls", gencodeId: "ENSG00000xxxxx.xx")
   -> Cross-tissue eQTL comparison; identifies tissue-specific vs. shared regulatory effects
4. mcp__gtex__gtex_data(method: "get_gene_expression", gencodeId: "ENSG00000xxxxx.xx")
   -> Tissue expression profile to identify disease-relevant tissues for interpretation
```

#### Activity-by-Contact (ABC) Model

```
Enhancer-gene linking score = Enhancer_activity * Contact_frequency / Sum(all elements for gene)
Where:
  Enhancer_activity = geometric_mean(H3K27ac_signal, DHS_signal) normalized per cell type
  Contact_frequency = Hi-C KR-normalized contact frequency at 5kb resolution
  Denominator = sum of activity * contact for all candidate elements near the gene
  Threshold: ABC score > 0.02 for high-confidence links (Nasser et al., Nature 2021)
  Validated against CRISPRi perturbation data in >100 enhancer-gene pairs
```

#### Evidence Hierarchy for Enhancer-Gene Assignment

```
Tier 1 (Strongest): CRISPR perturbation of enhancer alters target gene expression
  - CRISPRi silencing or CRISPR deletion with RNA-seq readout
  - Allelic series from base editing at enhancer element

Tier 2 (Strong): eQTL in variant-containing enhancer with colocalizing GWAS signal
  - Colocalization PP.H4 > 0.8 between eQTL and GWAS
  - Allele-specific expression consistent with eQTL direction

Tier 3 (Moderate): Chromatin interaction data + enhancer marks
  - Hi-C, Capture-C, HiChIP, or PLAC-seq interaction
  - Enhancer has H3K4me1 + H3K27ac in disease-relevant cell type

Tier 4 (Supportive): Activity-by-contact model prediction
  - ABC score > 0.02 in relevant cell type
  - Computational prediction without experimental interaction data

Tier 5 (Weak): Nearest gene assignment only
  - Often incorrect: nearest gene is the correct target for only ~40% of GWAS loci
  - Distal enhancers can regulate genes >1Mb away (e.g., ZRS enhancer for SHH is 1Mb distal)
  - Always seek higher-tier evidence before accepting nearest gene
```

---

### Workflow 3: Transcription Factor Binding Analysis

Assess how variants affect transcription factor binding and downstream gene regulation through motif disruption, ChIP-seq overlap, and TF footprinting.

#### Step 1: Identify TF Binding Context

```
1. mcp__ensembl__ensembl_data(method: "get_regulatory_features", region: "1:12000-12500", species: "homo_sapiens")
   -> Check for TF_binding_site features from ENCODE ChIP-seq compendium
2. mcp__uniprot__uniprot_data(method: "search_proteins", query: "transcription factor DNA-binding zinc finger", organism: "9606", size: 10)
   -> Identify TFs with known binding at locus; retrieve protein family information
3. mcp__uniprot__uniprot_data(method: "get_protein", accession: "P04637")
   -> TF protein details: DNA-binding domain type, functional domains, post-translational modifications
4. mcp__geneontology__go_data(method: "search_go_terms", query: "sequence-specific DNA binding transcription factor activity")
   -> GO terms for classifying TF molecular function and biological process
```

#### Step 2: Motif Disruption Quantification

```
5. Score reference and alternate alleles against position weight matrix (PWM)
6. Calculate delta log-odds score: deltaScore = PWM_alt - PWM_ref
7. Interpret motif disruption:
   - |deltaScore| > 2.0: Strong motif disruption or creation
   - |deltaScore| 1.0-2.0: Moderate disruption
   - |deltaScore| < 1.0: Weak or no disruption
8. Assess position within motif:
   - Core positions (information content >1.5 bits): disruption most impactful
   - Flanking positions (IC 0.5-1.5 bits): moderate impact
   - Degenerate positions (IC <0.5 bits): minimal impact
9. Check if variant creates a new TF binding site (gain-of-function variant)
```

#### Step 3: TF Network and Pathway Analysis

```
10. mcp__stringdb__stringdb_data(method: "get_network", identifiers: ["TP53", "MDM2", "CDKN1A"], species: 9606, required_score: 700)
    -> TF interaction partners, co-regulatory relationships, complex membership
11. mcp__stringdb__stringdb_data(method: "get_enrichment", identifiers: ["TP53", "MDM2", "CDKN1A"], species: 9606)
    -> Pathway enrichment of TF regulatory network (KEGG, Reactome, GO)
12. mcp__kegg__kegg_data(method: "find_pathway", query: "p53 signaling pathway", organism: "hsa")
    -> Signaling pathway context for TF-mediated regulation
13. mcp__reactome__reactome_data(method: "search_pathways", query: "transcription factor activity", species: "Homo sapiens")
    -> Gene expression regulation pathways involving the disrupted TF
```

#### TF Footprinting Interpretation

```
Digital genomic footprinting from DNase-seq or ATAC-seq:
  - Protected region within DHS peak = TF occupancy footprint
  - Footprint depth: ratio of signal at footprint vs. flanking DHS
  - Depth ratio < 0.5: strong footprint (confident TF occupancy)
  - Variant within footprint: high probability of disrupting bound TF
  - Variant in flanking DHS but outside footprint: may affect accessibility without direct TF disruption
```

#### Pioneer Factor Considerations

```
Pioneer factors access closed chromatin and initiate remodeling cascades:
  FOXA1/2:   Liver, pancreas development; opens chromatin for HNF4A and nuclear receptors
  GATA4/6:   Cardiac development; binds nucleosomal DNA to establish cardiac enhancers
  PU.1/SPI1: Hematopoietic lineage; establishes myeloid and lymphoid enhancer landscapes
  SOX2/OCT4: Pluripotency; establishes super-enhancers at pluripotency gene network
  TP63:      Epithelial identity; skin and squamous cell development programs
  PAX7:      Satellite cell identity; muscle stem cell enhancer activation
  CEBPA:     Myeloid and adipocyte differentiation; opens lineage-specific enhancers

Variants in pioneer factor binding sites have outsized effects because:
  1. Disruption prevents the chromatin opening cascade entirely
  2. Downstream TFs depend on pioneer-mediated accessibility to bind
  3. Effects are cell-type specific and often developmentally timed
  4. Cannot be compensated by other TFs (unlike cooperative binding redundancy)
```

---

### Workflow 4: eQTL Mapping & Colocalization

Integrate eQTL data with GWAS signals to identify causal regulatory variants and their target genes.

#### cis-eQTL Analysis Pipeline

```
1. mcp__gtex__gtex_data(method: "search_genes", query: "SORT1")
   -> Get GENCODE ID (e.g., ENSG00000134243.12) for GTEx queries
2. mcp__gtex__gtex_data(method: "get_single_tissue_eqtls", gencodeId: "ENSG00000134243.12", tissueSiteDetailId: "Liver")
   -> cis-eQTLs: variant ID, p-value, normalized effect size (NES), MAF
3. mcp__gtex__gtex_data(method: "get_multi_tissue_eqtls", gencodeId: "ENSG00000134243.12")
   -> Multi-tissue eQTL map for cross-tissue comparison of regulatory effects
4. mcp__gtex__gtex_data(method: "get_gene_expression", gencodeId: "ENSG00000134243.12")
   -> Tissue expression profile (TPM) to identify tissues where gene is expressed
```

#### GTEx Tissue Codes (Commonly Used)

```
Brain tissues:
  Brain_Cortex, Brain_Cerebellum, Brain_Hippocampus, Brain_Frontal_Cortex_BA9
  Brain_Caudate_basal_ganglia, Brain_Putamen_basal_ganglia, Brain_Substantia_nigra

Cardiovascular:
  Heart_Left_Ventricle, Heart_Atrial_Appendage, Artery_Aorta, Artery_Coronary, Artery_Tibial

Metabolic:
  Liver, Kidney_Cortex, Pancreas, Adipose_Subcutaneous, Adipose_Visceral_Omentum

Gastrointestinal:
  Colon_Transverse, Colon_Sigmoid, Esophagus_Mucosa, Esophagus_Muscularis, Stomach, Small_Intestine_Terminal_Ileum

Immune/Blood:
  Whole_Blood, Cells_EBV-transformed_lymphocytes, Spleen

Musculoskeletal:
  Muscle_Skeletal, Nerve_Tibial

Endocrine:
  Thyroid, Adrenal_Gland, Pituitary

Reproductive:
  Breast_Mammary_Tissue, Uterus, Ovary, Prostate, Testis, Vagina

Other:
  Lung, Skin_Sun_Exposed_Lower_leg, Skin_Not_Sun_Exposed_Suprapubic
```

#### trans-eQTL Considerations

```
trans-eQTLs (variant >5Mb from gene or on different chromosome):
  - Fewer detected due to severe multiple testing burden (~20,000 genes x millions of variants)
  - Often mediated by TFs: variant affects TF expression in cis, TF regulates distant gene in trans
  - Master regulators enriched in trans-eQTL loci: IRF1, KLF4, CTCF, YY1, NFKB1
  - Require larger sample sizes (n > 5000) for robust detection at genome-wide significance
  - Validate with mediation analysis: variant -> TF expression (cis) -> target gene expression (trans)
  - trans-eQTL effect sizes typically smaller (NES < 0.5) than cis-eQTLs
```

#### Colocalization with GWAS (coloc Method)

```
Bayesian colocalization tests whether GWAS and eQTL signals share a causal variant
(Giambartolomei et al., PLoS Genetics, 2014):

Hypotheses:
  H0: No association at locus with either trait
  H1: Association with GWAS trait only
  H2: Association with eQTL only
  H3: Association with both traits, but INDEPENDENT causal variants
  H4: Association with both traits, SHARED causal variant

Interpretation of posterior probabilities:
  PP.H4 > 0.8: Strong colocalization — same causal variant drives both GWAS and eQTL signals
  PP.H4 0.5-0.8: Suggestive colocalization — may share causal variant, consider LD confounding
  PP.H3 > 0.8: Independent signals — distinct causal variants at overlapping locus
  PP.H4 < 0.5 and PP.H3 < 0.5: Inconclusive — insufficient statistical power or complex LD

Default prior probabilities:
  p1 = 1e-4 (probability any SNP is associated with trait 1)
  p2 = 1e-4 (probability any SNP is associated with trait 2)
  p12 = 1e-5 (probability any SNP is associated with both traits)

Alternative colocalization methods:
  eCAVIAR:  Handles multiple causal variants; CLPP > 0.01 = colocalization
  coloc-SuSiE: Extends coloc with SuSiE fine-mapping for multi-signal loci
  SMR/HEIDI: Summary-based Mendelian Randomization; SMR p < 0.05/n AND HEIDI p > 0.05
  TWAS/FUSION: Imputes gene expression from genotype, tests trait association
```

---

### Workflow 5: Chromatin State Annotation

Annotate genomic regions with the 15-state ChromHMM model, ATAC-seq peaks, and DNase hypersensitivity data.

#### 15-State ChromHMM Model (Roadmap Epigenomics)

```
State  Name        Marks                            Color           Interpretation
1      TssA        H3K4me3                          Red             Active TSS
2      TssAFlnk    H3K4me1, H3K4me3                 OrangeRed       Flanking active TSS
3      TxFlnk      H3K4me1, H3K36me3                LimeGreen       Transcription at gene 5'/3'
4      Tx          H3K36me3                         Green           Strong transcription
5      TxWk        H3K36me3 (weak)                  DarkGreen       Weak transcription
6      EnhG        H3K4me1, H3K36me3                GreenYellow     Genic enhancers
7      Enh         H3K4me1, H3K27ac                 Yellow          Enhancers (distal)
8      ZNF/Rpts    H3K9me3, H3K36me3                MediumAquamarine ZNF genes & repeats
9      Het         H3K9me3                          PaleTurquoise   Heterochromatin
10     TssBiv      H3K4me3, H3K27me3                IndianRed       Bivalent/poised TSS
11     BivFlnk     H3K4me1, H3K27me3                DarkSalmon      Flanking bivalent TSS/enhancer
12     EnhBiv      H3K4me1, H3K27me3                DarkKhaki       Bivalent enhancer
13     ReprPC      H3K27me3                         Silver          Repressed PolyComb
14     ReprPCWk    H3K27me3 (weak)                  Gainsboro       Weak repressed PolyComb
15     Quies       None                             White           Quiescent/low signal
```

#### Key Histone Marks and Their Regulatory Meaning

```
Mark       Genomic Feature           Functional Significance
H3K4me3    Active promoters          Marks CpG-rich promoters of actively transcribed genes
H3K4me1    Enhancers (primed/active) Marks distal regulatory elements; enhancer identity
H3K27ac    Active enhancers/promoters Distinguishes ACTIVE from POISED regulatory elements
H3K36me3   Transcribed gene bodies   Co-transcriptional deposition by SETD2; marks exons
H3K27me3   Polycomb repression       PRC2-mediated silencing; developmental gene regulation
H3K9me3    Heterochromatin           Constitutive silencing; repeat elements, pericentromeric
H3K9me1    Heterochromatin (weak)    Weak heterochromatic mark
H4K20me1   Transcribed regions       Enriched in gene bodies of active genes
H2A.Z      Promoters/enhancers       Variant histone; marks regulatory regions, often bivalent
```

#### ENCODE Regulatory Element Classes (Ensembl Regulatory Build)

```
Element Type              Identification Criteria                  Typical Size
Promoter                  Overlaps annotated TSS, H3K4me3+,        0.5-2 kb
                          open chromatin, CpG island overlap
Promoter_Flanking         Adjacent to promoter (<2kb), H3K4me1+    0.5-1 kb
Enhancer                  Distal from TSS (>2kb), H3K4me1+,        0.2-1 kb
                          H3K27ac+, tissue-specific activity
CTCF_Binding_Site         CTCF ChIP-seq peak, insulator function,  50-200 bp
                          often at TAD boundaries
TF_Binding_Site           Non-CTCF TF ChIP-seq peak               50-200 bp
Open_Chromatin            DNase/ATAC-seq peak without specific     200-500 bp
                          TF binding assignment

Activity states per cell type:
  ACTIVE:    Open chromatin + active histone marks in this cell type
  POISED:    H3K4me1+ but H3K27me3+ (bivalent, ready to activate upon signal)
  REPRESSED: H3K27me3+ without active marks (Polycomb-silenced)
  INACTIVE:  No signal, closed chromatin in this cell type
  NA:        Not assessed in this cell type
```

#### ATAC-seq Quality Metrics

```
Metric                     Good Quality    Poor Quality
FRiP (fraction reads in    > 0.3           < 0.1
peaks)
TSS enrichment score       > 7             < 4
Fragment size distribution Nucleosomal     No clear
                           periodicity     periodicity
                           (~200bp)
Mitochondrial read %       < 20%           > 50%
Duplicate rate             < 30%           > 60%
Number of peaks            > 50,000        < 10,000
```

#### DNase Hypersensitivity Reference Data

```
- ENCODE: 733 biosample types profiled with DNase-seq
- Index DHSs: ~3.6 million unique DHSs across human genome (Meuleman et al., Nature 2020)
- Signal = -log10(p-value) of accessibility
- Hotspot2 algorithm for peak calling (standard ENCODE pipeline)
- Cell-type specificity: ~60% of DHSs are active in <5% of cell types
```

---

### Workflow 6: Promoter-Enhancer Interaction

Analyze 3D genome organization and its role in gene regulation, including TAD boundaries, insulator elements, CTCF binding, and loop domains.

#### TAD Boundaries and Insulation

```
Topologically Associating Domains (TADs):
  - Self-interacting chromatin domains, median ~880kb in human
  - Bounded by convergent CTCF + cohesin ring complex
  - ~80% of enhancer-promoter interactions occur within the same TAD
  - Conserved across cell types (~70%) but ~30% are cell-type variable
  - Hierarchical: sub-TADs nest within larger TADs at different resolution scales

Insulation score interpretation:
  Score < -1.0: Very strong boundary (top 10%)
  Score < -0.5: Strong boundary (top quartile)
  Score ~ 0:    Weak or no boundary
  Score > 0:    No insulation; region is not a boundary

TAD boundary disruption consequences:
  - Enhancer hijacking: ectopic enhancer-promoter contact across disrupted boundary
  - Known disease examples:
    * EPHA4/WNT6 locus: boundary deletion -> limb malformations (Lupianez et al., Cell 2015)
    * TAL1 locus: boundary loss -> T-ALL oncogene activation
    * PDGFRA locus: boundary disruption in IDH-mutant gliomas
```

#### CTCF Binding and Loop Extrusion

```
1. mcp__ensembl__ensembl_data(method: "get_regulatory_features", region: "1:1000000-2000000", species: "homo_sapiens")
   -> Identify CTCF_Binding_Site features within the region
2. mcp__uniprot__uniprot_data(method: "get_protein", accession: "P49711")
   -> CTCF protein: 11 zinc finger domains, context-dependent binding, ~55,000 sites genome-wide
3. mcp__ensembl__ensembl_data(method: "get_overlap_region", region: "1:1000000-2000000", species: "homo_sapiens", feature_type: "regulatory")
   -> All regulatory features including CTCF in the interval

CTCF loop extrusion model:
  - Cohesin (SMC1/3 + RAD21 + SA1/2) extrudes chromatin bidirectionally
  - Extrusion halts at convergent CTCF sites (> <) forming stable loops
  - Convergent orientation (> <): required for loop formation
  - Tandem orientation (> >): does NOT form stable loops
  - Divergent orientation (< >): does NOT form stable loops
  - CTCF motif is 19-20bp; core motif orientation determines loop anchor direction

Variant impact on CTCF:
  - Variant disrupting CTCF motif orientation -> abolishes loop domain
  - Loss of one anchor -> asymmetric loop weakening
  - CTCF methylation sensitivity: CpG methylation at CTCF motif blocks binding
  - ~15% of CTCF sites are methylation-sensitive boundaries

Insulator function:
  - CTCF + cohesin at TAD boundaries prevent cross-boundary enhancer action
  - Super-enhancers within loop domains are insulated from neighboring genes
  - Boundary disruption score = delta(insulation_score) upon variant introduction
```

#### Chromatin Interaction Detection Methods

```
Method          Resolution    Throughput       Best for
Hi-C            5-10kb        Genome-wide      TADs, A/B compartments, loop anchors
Capture-C       <1kb          Targeted         Specific viewpoint interactions (1-to-all)
HiChIP          1-5kb         Mark-guided      Active enhancer-promoter loops (H3K27ac HiChIP)
PLAC-seq        1-5kb         Mark-guided      Promoter-centered interactions (H3K4me3)
Micro-C         ~200bp        Genome-wide      Nucleosome-resolution contacts, fine-scale loops
ChIA-PET        1-5kb         Factor-based     CTCF- or RNAPII-mediated loops
GAM             ~30kb         Genome-wide      Nuclear architecture without ligation bias
SPRITE          ~1Mb          Genome-wide      Multi-way contacts and nuclear body associations
```

---

## Regulatory Variant Impact Score (RVIS)

Composite score (0-100) integrating five evidence dimensions. Higher score indicates stronger evidence for functional regulatory impact.

### Scoring Components

#### 1. Chromatin Accessibility (20 points max)

```
Evidence                                                    Points
ATAC-seq or DNase peak in disease-relevant tissue             8
ChromHMM active state (TssA, Enh, EnhG) in relevant tissue   6
H3K27ac signal in disease-relevant tissue                     4
Open chromatin in any tissue (not disease-matched)            2
No chromatin accessibility evidence                           0
```

#### 2. Transcription Factor Motif Disruption (20 points max)

```
Evidence                                                    Points
Strong motif disruption (|delta| > 2.0) at core position     10
ChIP-seq confirms TF binding at variant position              6
Strong motif disruption at flanking position                   6
Moderate disruption (|delta| 1.0-2.0) at core position       5
Motif creation (gain of new TF binding site)                  4
Weak or no motif disruption (|delta| < 1.0)                   0
```

#### 3. eQTL Evidence (25 points max)

```
Evidence                                                    Points
Significant eQTL in disease-relevant tissue (p < 5e-8)       10
Colocalization with GWAS signal (PP.H4 > 0.8)                 8
eQTL replicated in multiple tissues (>3 tissues)               4
eQTL in any tissue (p < 1e-5) but not disease-relevant        3
No eQTL evidence                                              0
```

#### 4. Conservation / Constraint (15 points max)

```
Evidence                                                    Points
CADD Phred > 20 (top 1% most deleterious genome-wide)        5
GERP++ RS > 4 (strongly constrained across vertebrates)       4
PhyloP > 2 (conserved across mammals)                         3
LINSIGHT > 0.5 (predicted fitness-reducing)                   3
Not conserved or low constraint scores                        0
```

#### 5. Functional Validation Evidence (20 points max)

```
Evidence                                                    Points
CRISPR deletion or base editing alters target expression      10
MPRA or STARR-seq validates allelic enhancer activity          6
Luciferase reporter assay confirms regulatory activity         4
Allele-specific expression (ASE) in heterozygotes              4
Allele-specific TF binding (ChIP-seq or ATAC-seq)             3
No functional validation data                                  0
```

### Score Interpretation

```
RVIS Score    Classification            Recommended Action
80-100        High-impact regulatory    Report as likely causal; prioritize for functional validation
60-79         Moderate-impact           Strong candidate; seek additional orthogonal evidence
40-59         Low-moderate impact       Possible regulatory; functional testing needed for confidence
20-39         Low impact                Weak evidence; deprioritize unless in critical regulatory element
0-19          Minimal evidence          Unlikely regulatory; consider alternative mechanisms
```

---

## Python Code Templates

### Position Weight Matrix Scoring

```python
import numpy as np

def score_pwm(sequence, pwm, background=None):
    """Score a DNA sequence against a position weight matrix.

    Args:
        sequence: DNA string (e.g., "ACGTACGT")
        pwm: dict of lists, keys='A','C','G','T', values=frequency at each position
        background: dict of background nucleotide frequencies (default: uniform 0.25)

    Returns:
        Log-odds score of the sequence against the PWM
    """
    if background is None:
        background = {'A': 0.25, 'C': 0.25, 'G': 0.25, 'T': 0.25}

    pseudocount = 0.001
    score = 0.0
    for i, base in enumerate(sequence.upper()):
        if base not in 'ACGT':
            continue
        freq = pwm[base][i] + pseudocount
        score += np.log2(freq / background[base])
    return score


def score_variant_motif_disruption(ref_seq, alt_seq, pwm, background=None):
    """Calculate motif disruption score for a variant.

    Args:
        ref_seq: Reference allele sequence spanning the motif
        alt_seq: Alternate allele sequence spanning the motif
        pwm: Position weight matrix dict
        background: Background nucleotide frequencies

    Returns:
        dict with ref_score, alt_score, delta_score, impact classification
    """
    ref_score = score_pwm(ref_seq, pwm, background)
    alt_score = score_pwm(alt_seq, pwm, background)
    delta_score = alt_score - ref_score

    if abs(delta_score) > 2.0:
        impact = "strong_disruption" if delta_score < 0 else "strong_creation"
    elif abs(delta_score) > 1.0:
        impact = "moderate_disruption" if delta_score < 0 else "moderate_creation"
    else:
        impact = "no_effect"

    return {
        'ref_score': round(ref_score, 3),
        'alt_score': round(alt_score, 3),
        'delta_score': round(delta_score, 3),
        'impact': impact
    }


def information_content(pwm, position):
    """Calculate information content (bits) at a PWM position.
    IC > 1.5 bits = core position; IC 0.5-1.5 = flanking; IC < 0.5 = degenerate."""
    freqs = [pwm[base][position] for base in 'ACGT']
    freqs = [max(f, 1e-10) for f in freqs]
    entropy = -sum(f * np.log2(f) for f in freqs)
    return 2.0 - entropy  # max entropy for 4 bases = 2 bits


# Example: GATA motif PWM (WGATAA)
gata_pwm = {
    'A': [0.40, 0.05, 0.90, 0.10, 0.85, 0.80],
    'C': [0.10, 0.05, 0.03, 0.05, 0.05, 0.05],
    'G': [0.10, 0.85, 0.03, 0.05, 0.05, 0.05],
    'T': [0.40, 0.05, 0.04, 0.80, 0.05, 0.10]
}

result = score_variant_motif_disruption("AGATAA", "AGCTAA", gata_pwm)
print(f"Ref score: {result['ref_score']}, Alt score: {result['alt_score']}")
print(f"Delta: {result['delta_score']}, Impact: {result['impact']}")

# Check information content at each position
for pos in range(6):
    ic = information_content(gata_pwm, pos)
    print(f"Position {pos}: IC = {ic:.2f} bits")
```

### eQTL Effect Size Visualization

```python
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import numpy as np

def plot_eqtl_effect_sizes(eqtl_data, gene_symbol, output_path="eqtl_effects.png"):
    """Visualize eQTL effect sizes across tissues as a forest plot with significance panel.

    Args:
        eqtl_data: list of dicts with keys: tissue, nes, pvalue, variant_id
        gene_symbol: gene symbol for plot title
        output_path: path to save figure
    """
    df = pd.DataFrame(eqtl_data)
    df['neg_log10_p'] = -np.log10(df['pvalue'].clip(lower=1e-300))
    df = df.sort_values('nes')

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, max(6, len(df) * 0.35)),
                                    gridspec_kw={'width_ratios': [3, 2]})

    # Left panel: Effect size forest plot
    colors = ['#e74c3c' if x > 0 else '#3498db' for x in df['nes']]
    ax1.barh(range(len(df)), df['nes'], color=colors, alpha=0.7, edgecolor='black', linewidth=0.3)
    ax1.set_yticks(range(len(df)))
    ax1.set_yticklabels(df['tissue'].str.replace('_', ' '), fontsize=8)
    ax1.set_xlabel('Normalized Effect Size (NES)')
    ax1.set_title(f'{gene_symbol} eQTL Effect Sizes by Tissue')
    ax1.axvline(x=0, color='black', linewidth=0.5)

    # Right panel: Significance
    sig_threshold = -np.log10(5e-8)
    bar_colors = ['#e74c3c' if p > sig_threshold else '#95a5a6' for p in df['neg_log10_p']]
    ax2.barh(range(len(df)), df['neg_log10_p'], color=bar_colors, alpha=0.7)
    ax2.axvline(x=sig_threshold, color='red', linestyle='--', linewidth=0.8, label='5e-8')
    ax2.axvline(x=-np.log10(1e-5), color='orange', linestyle=':', linewidth=0.8, label='1e-5')
    ax2.set_xlabel('-log10(p-value)')
    ax2.set_title('Significance')
    ax2.set_yticks([])
    ax2.legend(fontsize=8, loc='lower right')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved eQTL effect size plot to {output_path}")


# Example usage with GTEx-format data:
# eqtl_results = [
#     {'tissue': 'Liver', 'nes': 0.45, 'pvalue': 1.2e-12, 'variant_id': 'rs12740374'},
#     {'tissue': 'Whole_Blood', 'nes': -0.22, 'pvalue': 3.5e-6, 'variant_id': 'rs12740374'},
#     {'tissue': 'Brain_Cortex', 'nes': 0.38, 'pvalue': 8.1e-9, 'variant_id': 'rs12740374'},
#     {'tissue': 'Adipose_Subcutaneous', 'nes': 0.15, 'pvalue': 0.003, 'variant_id': 'rs12740374'},
# ]
# plot_eqtl_effect_sizes(eqtl_results, "SORT1")
```

### Chromatin State Enrichment Analysis

```python
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

CHROMHMM_STATES = {
    1: 'TssA', 2: 'TssAFlnk', 3: 'TxFlnk', 4: 'Tx', 5: 'TxWk',
    6: 'EnhG', 7: 'Enh', 8: 'ZNF/Rpts', 9: 'Het', 10: 'TssBiv',
    11: 'BivFlnk', 12: 'EnhBiv', 13: 'ReprPC', 14: 'ReprPCWk', 15: 'Quies'
}

CHROMHMM_COLORS = {
    'TssA': '#FF0000', 'TssAFlnk': '#FF4500', 'TxFlnk': '#32CD32',
    'Tx': '#008000', 'TxWk': '#006400', 'EnhG': '#ADFF2F',
    'Enh': '#FFD700', 'ZNF/Rpts': '#66CDAA', 'Het': '#AFEEEE',
    'TssBiv': '#CD5C5C', 'BivFlnk': '#E9967A', 'EnhBiv': '#BDB76B',
    'ReprPC': '#C0C0C0', 'ReprPCWk': '#DCDCDC', 'Quies': '#F5F5F5'
}

# Typical genome fractions for 15 ChromHMM states (Roadmap average across 127 epigenomes)
GENOME_FRACTIONS = {
    'TssA': 0.017, 'TssAFlnk': 0.023, 'TxFlnk': 0.018, 'Tx': 0.045, 'TxWk': 0.053,
    'EnhG': 0.012, 'Enh': 0.043, 'ZNF/Rpts': 0.028, 'Het': 0.054, 'TssBiv': 0.007,
    'BivFlnk': 0.005, 'EnhBiv': 0.011, 'ReprPC': 0.035, 'ReprPCWk': 0.065, 'Quies': 0.584
}


def chromatin_state_enrichment(variant_states, genome_fractions=None, output_path="chromatin_enrichment.png"):
    """Test enrichment of variants in each ChromHMM state vs genome background.

    Args:
        variant_states: list of ChromHMM state names for each variant
        genome_fractions: dict mapping state name to genome fraction (defaults to Roadmap average)
        output_path: path to save enrichment plot

    Returns:
        DataFrame with fold enrichment, p-values, and significance flags
    """
    if genome_fractions is None:
        genome_fractions = GENOME_FRACTIONS

    n_variants = len(variant_states)
    state_counts = pd.Series(variant_states).value_counts()

    results = []
    for state_name, genome_frac in genome_fractions.items():
        observed = state_counts.get(state_name, 0)
        expected = n_variants * genome_frac
        fold_enrichment = observed / expected if expected > 0 else 0

        # Binomial test: observed count vs expected under null
        pval = stats.binom_test(observed, n_variants, genome_frac, alternative='greater')

        results.append({
            'state': state_name,
            'observed': observed,
            'expected': round(expected, 1),
            'fold_enrichment': round(fold_enrichment, 2),
            'pvalue': pval,
            'significant': pval < (0.05 / 15)  # Bonferroni correction for 15 states
        })

    df = pd.DataFrame(results).sort_values('fold_enrichment', ascending=True)

    # Plot enrichment
    fig, ax = plt.subplots(figsize=(10, 7))
    colors = [CHROMHMM_COLORS.get(s, '#888888') for s in df['state']]
    ax.barh(df['state'], df['fold_enrichment'], color=colors, edgecolor='black', linewidth=0.5)

    for i, (_, row) in enumerate(df.iterrows()):
        if row['significant']:
            ax.text(row['fold_enrichment'] + 0.05, i, '*', fontsize=14, va='center', fontweight='bold')

    ax.axvline(x=1.0, color='black', linestyle='--', linewidth=0.8, label='Expected (1.0)')
    ax.set_xlabel('Fold Enrichment over Genome Background')
    ax.set_title('Variant Enrichment in ChromHMM States (* = Bonferroni p < 0.05)')
    ax.legend(loc='lower right')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved chromatin enrichment plot to {output_path}")

    return df
```

### Regulatory Element Overlap Statistics

```python
import pandas as pd
import numpy as np
from scipy.stats import fisher_exact

def regulatory_overlap_test(variant_positions, regulatory_elements, genome_size=3.1e9, element_coverage=None):
    """Test enrichment of variants in regulatory elements using Fisher's exact test.

    Args:
        variant_positions: list of (chrom, pos) tuples for query variants
        regulatory_elements: dict mapping element type to list of (chrom, start, end)
        genome_size: total genome size in bp (default: 3.1 billion for human)
        element_coverage: optional dict mapping element type to total bp covered

    Returns:
        DataFrame with overlap counts, fold enrichment, odds ratios, and p-values
    """
    n_variants = len(variant_positions)

    results = []
    for elem_type, elements in regulatory_elements.items():
        # Count variants overlapping this element type
        overlapping = 0
        if element_coverage and elem_type in element_coverage:
            total_bp = element_coverage[elem_type]
        else:
            total_bp = sum(end - start for _, start, end in elements)

        for chrom, pos in variant_positions:
            for e_chrom, e_start, e_end in elements:
                if chrom == e_chrom and e_start <= pos <= e_end:
                    overlapping += 1
                    break

        not_overlapping = n_variants - overlapping
        frac_genome = total_bp / genome_size
        expected = n_variants * frac_genome

        # Fisher's exact test (2x2 contingency table)
        table = [
            [overlapping, not_overlapping],
            [int(total_bp), int(genome_size - total_bp)]
        ]
        odds_ratio, pvalue = fisher_exact(table, alternative='greater')

        results.append({
            'element_type': elem_type,
            'n_overlapping': overlapping,
            'n_total': n_variants,
            'fraction_overlapping': round(overlapping / n_variants, 3) if n_variants > 0 else 0,
            'genome_coverage_bp': int(total_bp),
            'genome_coverage_pct': round(frac_genome * 100, 2),
            'fold_enrichment': round((overlapping / n_variants) / frac_genome, 2) if frac_genome > 0 and n_variants > 0 else 0,
            'odds_ratio': round(odds_ratio, 2),
            'pvalue': pvalue
        })

    df = pd.DataFrame(results).sort_values('pvalue')

    # Apply Bonferroni correction
    df['bonferroni_p'] = np.minimum(df['pvalue'] * len(df), 1.0)
    df['significant'] = df['bonferroni_p'] < 0.05

    return df


# Typical regulatory element genome coverage (ENCODE, human GRCh38):
ENCODE_ELEMENT_COVERAGE = {
    'Promoter':           73_000_000,    # ~73 Mb (2.4% of genome)
    'Enhancer':          432_000_000,    # ~432 Mb (13.9%)
    'CTCF_Binding_Site':  57_000_000,    # ~57 Mb (1.8%)
    'Open_Chromatin':    510_000_000,    # ~510 Mb (16.5%, union across cell types)
    'TF_Binding_Site':   231_000_000,    # ~231 Mb (7.5%, union across TFs)
}
```

---

## Evidence Grading for Regulatory Variants

Four-tier evidence grading system for regulatory variant causality, from strongest functional evidence to positional inference only.

### Tier 1 (T1) -- Functional Validation

```
Criteria: Direct experimental evidence that the variant alters gene regulation.

Accepted experimental methods:
  - CRISPR-Cas9 deletion or base editing of regulatory element containing the variant
  - Luciferase or GFP reporter assay comparing reference vs. alternate allele activity
  - STARR-seq or MPRA (massively parallel reporter assay) with allelic effect quantification
  - Base editing at endogenous locus with RNA-seq or qPCR readout of target gene
  - CRISPRi (dCas9-KRAB) or CRISPRa (dCas9-VPR) perturbation of regulatory element

Requirements for T1 classification:
  - Tested in disease-relevant cell type or primary tissue
  - Statistically significant allelic difference (p < 0.05 after multiple testing correction)
  - Effect direction consistent with proposed disease mechanism
  - Replicated in >= 2 independent experiments or biological replicates

Confidence: Variant is causal regulatory variant (report as "functionally validated")
```

### Tier 2 (T2) -- eQTL + Chromatin Evidence

```
Criteria: Convergent evidence from expression data and epigenomic annotations.

All of the following must be met:
  1. Significant eQTL (p < 5e-8) for the variant-gene pair in a disease-relevant tissue
  2. Colocalization with GWAS signal for the disease/trait (PP.H4 > 0.5)
  3. At least ONE chromatin-level support:
     a. Variant overlaps active ChromHMM state (TssA, Enh, EnhG) in relevant tissue
     b. Variant in ATAC-seq or DNase hypersensitivity peak in relevant tissue
     c. Variant disrupts TF motif (|delta| > 1.0) with ChIP-seq TF binding support
  4. Target gene is biologically plausible for the trait/disease

Confidence: Variant is probable causal regulatory variant (report as "strong candidate")
```

### Tier 3 (T3) -- Computational Prediction

```
Criteria: In silico evidence without direct functional or strong eQTL validation.

At least 2 of the following must be met:
  1. CADD Phred > 15 (top 3% most deleterious genome-wide)
  2. RegulomeDB category <= 3a (TF binding + motif evidence)
  3. Variant in conserved element (GERP++ RS > 2 or PhyloP > 1)
  4. Predicted TF motif disruption (|delta log-odds| > 1.0)
  5. ABC model links the element to a plausible target gene (ABC score > 0.02)
  6. eQTL in any tissue (p < 1e-5) but not in disease-relevant tissue specifically

Confidence: Variant is possible regulatory variant (report as "computational candidate")
```

### Tier 4 (T4) -- Positional Only

```
Criteria: Location-based evidence without functional, eQTL, or strong computational support.

Evidence limited to:
  - Variant is in a non-coding region near a disease-relevant gene
  - In LD with GWAS lead SNP (r2 > 0.6) but no fine-mapping prioritization
  - Located in a regulatory element in some cell type (not disease-relevant)
  - No significant eQTL, no TF motif disruption, no functional validation data

Confidence: Insufficient evidence for regulatory causality (report as "positional candidate")
Action: Deprioritize unless additional evidence emerges; do not report as regulatory variant
```

### Evidence Grading Summary Table

```
Tier   Label                     Key Evidence Required                          Confidence
T1     Functionally validated    Reporter assay, CRISPR, MPRA with allelic      High
                                 effect in relevant cell type
T2     Strong candidate          eQTL + GWAS colocalization + chromatin state    Moderate-High
                                 in disease-relevant tissue
T3     Computational candidate   CADD + RegulomeDB + motif disruption +          Moderate
                                 conservation (>= 2 of these)
T4     Positional candidate      Location only, no functional or eQTL support   Low
```

---

## CADD Score Interpretation Guide

```
Phred Score    Percentile        Interpretation
>= 30          Top 0.1%          Highly likely deleterious; comparable to known pathogenic variants
>= 25          Top 0.3%          Strong evidence of deleteriousness
>= 20          Top 1%            Likely deleterious; standard prioritization threshold
>= 15          Top 3%            Moderate evidence; useful with additional supporting data
>= 10          Top 10%           Weak evidence; informative for ranking, not sufficient alone
< 10           Bottom 90%        Unlikely to be deleterious by this metric alone

Key CADD features scored for non-coding variants:
  - Sequence context: GC content, CpG dinucleotide, repeat element overlap
  - Conservation: PhastCons (100-way vertebrates), PhyloP (100-way), GERP++ RS scores
  - Epigenomic marks: H3K4me1, H3K4me3, H3K27ac, H3K36me3, DNase signal (ENCODE)
  - Genomic distance: to nearest exon, TSS, splice site, miRNA binding site
  - TF binding: overlap with ENCODE ChIP-seq peaks, TF motif match score
  - Regulatory: Ensembl regulatory build annotation, Segway segmentation state
  - Population: derived allele frequency, number of observed alleles
```

---

## Reference: Key Databases and Resources

```
Database                  Content                                         Access
ENCODE                    Regulatory elements, TF ChIP-seq, DNase/ATAC    encodeproject.org
Roadmap Epigenomics       127 tissue/cell type ChromHMM states             egg2.wustl.edu/roadmap
GTEx (v8)                 eQTLs in 49 tissues, n=838 donors               gtexportal.org
RegulomeDB (v2)           Regulatory variant scoring from ENCODE data      regulomedb.org
JASPAR 2024               Curated TF binding motif PWMs (>2000 profiles)   jaspar.genereg.net
HOCOMOCO v11              Human/mouse TF binding models (quality-rated)    hocomoco11.autosome.org
4D Nucleome               Hi-C, Micro-C chromatin interaction data         4dnucleome.org
FANTOM5                   Enhancer atlas, CAGE-defined TSS and enhancers   fantom.gsc.riken.jp/5/
VISTA Enhancer Browser    In vivo validated enhancers (transgenic mice)    enhancer.lbl.gov
GeneHancer                Enhancer-gene associations (integrated scores)   genecards.org/genehancer
SEdb 2.0                  Super-enhancer database across cell types        superenhancer.bio
ClinGen                   Gene-disease clinical validity curation          clinicalgenome.org
SCREEN (ENCODE)           cCRE registry with biochemical activity data     screen.encodeproject.org
ABC Model catalog         Pre-computed ABC enhancer-gene predictions       engreitzlab.org
Open Chromatin Atlas      Index DHS catalog across 733 biosamples          meuleman.org
```

---

## Output Format

Structure regulatory genomics analysis reports as follows:

```
## Regulatory Variant Report: [variant_id]

### Variant Summary
- Position: chrX:NNNNNNN (GRCh38)
- Alleles: ref/alt
- MAF: X.XX (gnomAD)
- Genomic context: [promoter/enhancer/intergenic/intronic]
- CADD Phred: XX

### Regulatory Evidence
| Evidence Type | Finding | Score Component |
|---|---|---|
| Chromatin state | [ChromHMM state in tissue] | Accessibility: X/20 |
| TF motif | [TF name, delta score, impact] | Motif disruption: X/20 |
| eQTL | [tissue, NES, p-value] | eQTL evidence: X/25 |
| Conservation | [GERP, PhyloP, CADD] | Conservation: X/15 |
| Functional data | [assay type, result] | Validation: X/20 |

### RVIS Score: XX/100 ([Classification])
- Chromatin Accessibility: XX/20
- TF Motif Disruption: XX/20
- eQTL Evidence: XX/25
- Conservation/Constraint: XX/15
- Functional Validation: XX/20

### Evidence Tier: [T1/T2/T3/T4] ([Label])

### Target Gene Assignment
- Gene: [symbol] (method: [eQTL/promoter/Hi-C/ABC])
- Confidence: [High/Medium/Low]
- Supporting evidence: [summary of convergent evidence]

### Functional Hypothesis
[1-2 paragraph mechanistic explanation linking variant to gene to phenotype]

### Suggested Validation Experiments
1. [Experiment 1 with specific assay and cell type]
2. [Experiment 2]
3. [Experiment 3]
```

## Completeness Checklist

- [ ] Variant genomic context annotated (chromosome, position, ref/alt, nearby genes)
- [ ] Chromatin state assessed via ChromHMM/ENCODE annotations for relevant cell types
- [ ] Transcription factor binding site disruption scored using position weight matrices
- [ ] eQTL evidence queried from GTEx across relevant tissues
- [ ] Enhancer-gene linking evaluated (Hi-C, ABC model, promoter capture)
- [ ] Conservation and constraint metrics retrieved (GERP, PhyloP, CADD)
- [ ] RVIS score computed with evidence tier classification (T1-T4)
- [ ] Target gene assignment made with confidence level and supporting evidence
- [ ] Functional hypothesis drafted linking variant to gene to phenotype
- [ ] Report file finalized with no `[Analyzing...]` placeholders remaining
