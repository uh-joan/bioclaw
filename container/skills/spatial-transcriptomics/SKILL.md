---
name: spatial-transcriptomics
description: Spatial transcriptomics analyst. Spatially-resolved gene expression analysis across platforms (10x Visium, MERFISH, seqFISH, Slide-seq). Spatial clustering, spatially variable gene detection, neighborhood enrichment, cell-type deconvolution, spatial cell communication. Use when user mentions spatial transcriptomics, Visium, MERFISH, seqFISH, Slide-seq, spatial gene expression, spatially variable genes, SVG, spatial clustering, neighborhood enrichment, cell deconvolution, cell2location, Tangram, squidpy, spatial neighbors, Moran's I, spatial omics, tissue architecture, or spatial cell communication.
---

# Spatial Transcriptomics

> **Code recipes**: See [spatial-recipes.md](spatial-recipes.md) for copy-paste executable code templates covering spatial graph construction, Moran's I, deconvolution, neighborhood enrichment, and more.

Spatially-resolved gene expression analysis across major platforms. Uses scanpy/squidpy for computational analysis, Open Targets for gene-disease annotation, PubMed for spatial biology literature, and DrugBank for pharmacological context of spatially variable targets.

## Report-First Workflow

1. **Create report file immediately**: `[tissue]_spatial_transcriptomics_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill
- Biological interpretation of spatial multi-omics data (pathway enrichment, immune profiling) → use `spatial-omics-analysis`
- Single-cell RNA-seq analysis without spatial coordinates → use `single-cell-analysis`
- Gene set enrichment and pathway analysis → use `gene-enrichment`
- Network-level pathway modeling from spatial patterns → use `systems-biology`
- Multi-omic integration beyond transcriptomics → use `multiomic-disease-characterization`

## Cross-Reference: Other Skills

- **Single-cell reference for deconvolution** -> use single-cell-analysis skill
- **Gene set enrichment of spatial clusters** -> use gene-enrichment skill
- **Pathway modeling from spatial patterns** -> use systems-biology skill
- **Multi-omic integration with spatial data** -> use multiomic-disease-characterization skill
- **Broader spatial omics context** -> use spatial-omics-analysis skill

## Available MCP Tools

### `mcp__opentargets__opentargets_info` (Gene-Disease Annotation)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_targets` | Search targets by gene symbol/name | `query`, `size` |
| `search_diseases` | Search diseases by name/synonym | `query`, `size` |
| `get_target_disease_associations` | Evidence-scored target-disease links | `targetId` (Ensembl ID), `diseaseId` (EFO ID), `minScore`, `size` |
| `get_disease_targets_summary` | All targets for a disease | `diseaseId`, `minScore`, `size` |
| `get_target_details` | Full target info (function, pathways, tractability) | `id` (Ensembl ID) |
| `get_disease_details` | Full disease info (ontology, phenotypes) | `id` (EFO ID) |

### `mcp__pubmed__pubmed_articles` (Spatial Biology Literature)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Quick keyword search | `keywords`, `num_results` |
| `search_advanced` | Filtered search | `term`, `journal`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Full article details | `pmid` |

### `mcp__drugbank__drugbank_info` (Pharmacology of Spatial Targets)

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

---

## 8-Phase Spatial Transcriptomics Pipeline

### Phase 1: Data QC

```python
import scanpy as sc
import squidpy as sq

# Load spatial data (platform-specific)
# Visium:
adata = sc.read_visium("path/to/spaceranger_output")
# MERFISH/seqFISH:
adata = sc.read_h5ad("path/to/merfish_data.h5ad")

# QC metrics
sc.pp.calculate_qc_metrics(adata, percent_top=None, inplace=True)
adata.var["mt"] = adata.var_names.str.startswith("MT-")
sc.pp.calculate_qc_metrics(adata, qc_vars=["mt"], percent_top=None, inplace=True)

# Apply QC filters
adata = adata[adata.obs["n_genes_by_counts"] >= 200, :]   # >=200 genes/spot
adata = adata[adata.obs["total_counts"] >= 500, :]         # >=500 UMI/spot
adata = adata[adata.obs["pct_counts_mt"] < 20, :]          # <20% mitochondrial
sc.pp.filter_genes(adata, min_cells=10)

# Visualize QC spatially
sq.pl.spatial_scatter(adata, color=["n_genes_by_counts", "total_counts", "pct_counts_mt"], shape=None)
```

### Phase 2: Preprocessing

```python
# Normalize and log-transform
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)

# Store raw for DE later
adata.raw = adata

# Highly variable genes
sc.pp.highly_variable_genes(adata, n_top_genes=3000, flavor="seurat_v3", span=0.3)
adata = adata[:, adata.var["highly_variable"]]

# Scale
sc.pp.scale(adata, max_value=10)
```

### Phase 3: Spatial Clustering

```python
# PCA
sc.pp.pca(adata, n_comps=50)

# Build spatial neighbor graph (uses both expression and coordinates)
sq.gr.spatial_neighbors(adata, n_neighs=6, coord_type="generic")

# Alternatively, combine expression and spatial neighbors
sc.pp.neighbors(adata, n_neighbors=15, use_rep="X_pca")  # expression neighbors

# Leiden clustering
sc.tl.leiden(adata, resolution=0.8, key_added="spatial_cluster")

# UMAP for visualization
sc.tl.umap(adata)

# Visualize clusters in tissue space
sq.pl.spatial_scatter(adata, color="spatial_cluster", shape=None, size=1.5)
```

### Phase 4: Spatially Variable Gene (SVG) Detection

```python
# Compute spatial neighbors if not done
sq.gr.spatial_neighbors(adata, coord_type="generic", n_neighs=6)

# Moran's I for spatial autocorrelation
sq.gr.spatial_autocorr(adata, mode="moran", genes=adata.var_names, n_perms=100, n_jobs=-1)

# Filter significant SVGs (FDR < 0.05)
svg_results = adata.uns["moranI"]
svg_results = svg_results[svg_results["pval_sim_fdr"] < 0.05]
svg_results = svg_results.sort_values("I", ascending=False)

# Top spatially variable genes
top_svgs = svg_results.head(50).index.tolist()
sq.pl.spatial_scatter(adata, color=top_svgs[:6], shape=None, size=1.5)
```

### Phase 5: Neighborhood Enrichment

```python
# Compute neighborhood enrichment between clusters
sq.gr.nhood_enrichment(adata, cluster_key="spatial_cluster")

# Visualize co-localization patterns
sq.pl.nhood_enrichment(adata, cluster_key="spatial_cluster", method="ward")

# Co-occurrence analysis
sq.gr.co_occurrence(adata, cluster_key="spatial_cluster")
sq.pl.co_occurrence(adata, cluster_key="spatial_cluster", clusters=["0", "1", "2"])

# Ripley's statistics for spatial distribution
sq.gr.ripley(adata, cluster_key="spatial_cluster", mode="L")
sq.pl.ripley(adata, cluster_key="spatial_cluster", mode="L")
```

### Phase 6: scRNA-seq Integration (Cell-Type Deconvolution)

```python
# --- Cell2location ---
import cell2location
from cell2location.utils import select_slide

# Train reference model on scRNA-seq
cell2location.models.RegressionModel.setup_anndata(adata_ref, labels_key="cell_type")
mod_ref = cell2location.models.RegressionModel(adata_ref)
mod_ref.train(max_epochs=250)

# Export reference signatures
adata_ref = mod_ref.export_posterior(adata_ref)
inf_aver = adata_ref.varm["means_per_cluster_mu_fg"]

# Train spatial model
cell2location.models.Cell2location.setup_anndata(adata_vis, batch_key="sample")
mod = cell2location.models.Cell2location(adata_vis, cell_state_df=inf_aver, N_cells_per_location=30)
mod.train(max_epochs=30000)

# Export and visualize
adata_vis = mod.export_posterior(adata_vis)
sq.pl.spatial_scatter(adata_vis, color=["cell_type_1", "cell_type_2"], shape=None)

# --- Tangram (alternative) ---
import tangram as tg

tg.pp_adatas(adata_ref, adata_vis, genes=marker_genes)
ad_map = tg.map_cells_to_space(adata_ref, adata_vis, mode="cells", density_prior="rna_count_based")
tg.project_cell_annotations(ad_map, adata_vis, annotation="cell_type")
```

### Phase 7: Spatial Cell Communication

```python
# Ligand-receptor analysis
sq.gr.ligrec(
    adata,
    n_perms=1000,
    cluster_key="spatial_cluster",
    use_raw=True,
    transmitter_params={"categories": "ligand"},
    receiver_params={"categories": "receptor"},
)

# Visualize significant interactions
sq.pl.ligrec(
    adata,
    cluster_key="spatial_cluster",
    source_groups=["0", "1"],
    target_groups=["2", "3"],
    pvalue_threshold=0.01,
)
```

### Phase 8: Report Generation

```
1. Annotate top SVGs with disease/target context:
   mcp__opentargets__opentargets_info(method: "search_targets", query: "GENE_SYMBOL")
   mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")

2. Check druggability of spatial targets:
   mcp__drugbank__drugbank_info(method: "search_by_target", target: "SVG_gene_name")

3. Literature context for spatial patterns:
   mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_SYMBOL spatial transcriptomics tissue_type", num_results: 10)

4. Compile spatial report:
   - QC summary (spots retained, genes detected)
   - Spatial cluster map with marker genes
   - Top SVGs with Moran's I scores and spatial patterns
   - Neighborhood enrichment heatmap
   - Deconvolution results (cell-type proportions per spot)
   - Ligand-receptor interactions with spatial context
   - Druggable spatial targets with disease associations
```

---

## SVG Pattern Classification

### Spatial Expression Pattern Types

| Pattern | Description | Detection Method | Biological Meaning |
|---------|-------------|-----------------|-------------------|
| **Gradient** | Smooth expression gradient across tissue | High Moran's I, spatially smooth | Morphogen signaling, diffusion-driven patterning |
| **Hotspot** | Discrete high-expression foci | High Moran's I, clustered | Localized cell populations, microenvironments |
| **Boundary** | Expression marking tissue interfaces | High Moran's I at transitions | Tissue boundaries, niche interfaces, TME edges |
| **Periodic** | Repeating spatial pattern | Fourier analysis, periodic autocorrelation | Structural organization (e.g., liver lobules, intestinal crypts) |

### Classification Workflow

```python
# After Moran's I computation, classify patterns:
# 1. Compute local Moran's I (LISA) for hotspot detection
sq.gr.spatial_autocorr(adata, mode="moran", genes=top_svgs, n_perms=100)

# 2. For gradient detection — check correlation with spatial coordinates
import numpy as np
from scipy.stats import spearmanr

for gene in top_svgs:
    expr = adata[:, gene].X.toarray().flatten()
    coords = adata.obsm["spatial"]
    r_x, _ = spearmanr(expr, coords[:, 0])
    r_y, _ = spearmanr(expr, coords[:, 1])
    if max(abs(r_x), abs(r_y)) > 0.5:
        print(f"{gene}: GRADIENT pattern (rho_x={r_x:.3f}, rho_y={r_y:.3f})")

# 3. For boundary detection — check expression at cluster interfaces
# Genes with high variance at cluster boundaries are boundary markers
```

---

## Platform-Specific Handling

### Resolution and Characteristics

| Platform | Resolution | Capture Area | Gene Panel | Data Format |
|----------|-----------|-------------|------------|-------------|
| **10x Visium** | 55 um spots (1-10 cells) | 6.5 x 6.5 mm | Whole transcriptome | Space Ranger output |
| **MERFISH** | Single-cell (~100 nm) | Variable | 100-10,000 genes (targeted) | Cell x gene matrix + coordinates |
| **seqFISH** | Single-cell (~100 nm) | Variable | 100-10,000 genes (targeted) | Cell x gene matrix + coordinates |
| **Slide-seq** | 10 um beads (sub-cellular) | 3 mm diameter | Whole transcriptome | Bead x gene matrix + coordinates |

### Platform-Specific Considerations

```
10x Visium (55 um spots):
- Each spot captures 1-10 cells → deconvolution REQUIRED for cell-type inference
- Use cell2location or Tangram with matched scRNA-seq reference
- Spatial neighbor graph: n_neighs=6 (hexagonal grid)
- Spot-level analysis: treat as pseudo-bulk per spot

MERFISH (single-cell resolution):
- No deconvolution needed — direct cell-type annotation
- Targeted panel: limited to pre-selected genes (no genome-wide SVG discovery)
- Segmentation quality is critical — verify cell boundaries
- Spatial neighbor graph: Delaunay triangulation or k-NN (n_neighs=10-30)

seqFISH (single-cell resolution):
- Similar to MERFISH — targeted panel, single-cell
- Typically smaller panels (100-300 genes)
- High positional accuracy enables subcellular analysis
- Spatial neighbor graph: k-NN with distance threshold

Slide-seq (10 um beads):
- Higher resolution than Visium but lower capture efficiency
- Sub-cellular potential but noisy — aggregate beads for robustness
- Deconvolution beneficial (beads capture partial transcriptomes)
- Spatial neighbor graph: n_neighs=10-20 (random bead placement)
```

---

## Deconvolution Methods

### Method Selection Criteria

| Method | Best For | Requirements | Strengths | Limitations |
|--------|---------|-------------|----------|-------------|
| **Cell2location** | Visium, Slide-seq | scRNA-seq reference, GPU recommended | Probabilistic, quantitative cell counts, handles ambient RNA | Computationally heavy, requires training |
| **Tangram** | Visium, Slide-seq | scRNA-seq reference | Fast, maps individual cells to spots, works with targeted panels | Less quantitative than cell2location |
| **SPOTlight** | Visium | scRNA-seq reference | NMF-based, lightweight, fast | Less accurate for rare cell types |

### Decision Guide

```
Choose Cell2location when:
- You need absolute cell-type abundance estimates (counts per spot)
- Reference and spatial data are from the same tissue/condition
- Computational resources allow GPU training
- Handling complex tissues with many cell types (>10)

Choose Tangram when:
- You need fast results or iterative exploration
- Working with targeted panels (MERFISH/seqFISH genes)
- You want to map individual reference cells to spatial locations
- scRNA-seq reference may be from a related (not identical) tissue

Choose SPOTlight when:
- Quick exploratory deconvolution needed
- Limited computational resources
- Fewer cell types to resolve (<8)
- Used as a first-pass before more rigorous methods
```

---

## Squidpy Code Templates

### Spatial Neighbors

```python
# Grid-based (Visium)
sq.gr.spatial_neighbors(adata, n_neighs=6, coord_type="grid")

# Distance-based (MERFISH, Slide-seq)
sq.gr.spatial_neighbors(adata, n_neighs=15, coord_type="generic", delaunay=False)

# Delaunay triangulation (MERFISH, seqFISH)
sq.gr.spatial_neighbors(adata, coord_type="generic", delaunay=True)
```

### Moran's I (Spatial Autocorrelation)

```python
# Global Moran's I for all genes
sq.gr.spatial_autocorr(adata, mode="moran", n_perms=100, n_jobs=-1)
svg_df = adata.uns["moranI"].sort_values("I", ascending=False)
significant_svgs = svg_df[svg_df["pval_sim_fdr"] < 0.05]

# Geary's C (alternative — detects local heterogeneity)
sq.gr.spatial_autocorr(adata, mode="geary", n_perms=100, n_jobs=-1)
```

### Neighborhood Enrichment

```python
# Which clusters are spatially co-localized?
sq.gr.nhood_enrichment(adata, cluster_key="spatial_cluster")
sq.pl.nhood_enrichment(adata, cluster_key="spatial_cluster", figsize=(8, 8), title="Neighborhood Enrichment")

# Interaction matrix interpretation:
# z-score > 2: clusters are significantly co-localized
# z-score < -2: clusters significantly avoid each other
```

### Ligand-Receptor Analysis

```python
# Spatially-constrained ligand-receptor interactions
sq.gr.ligrec(
    adata,
    n_perms=1000,
    cluster_key="spatial_cluster",
    use_raw=True,
    transmitter_params={"categories": "ligand"},
    receiver_params={"categories": "receptor"},
    interactions_params={"resources": "CellPhoneDB"},
)

# Filter and visualize
sq.pl.ligrec(
    adata,
    cluster_key="spatial_cluster",
    pvalue_threshold=0.01,
    means_range=(0.5, None),  # filter weak interactions
)
```

---

## Multi-Agent Workflow Examples

**"Map the tumor microenvironment architecture in a Visium dataset"**
1. Spatial Transcriptomics -> 8-phase pipeline: QC, clustering, SVG detection, deconvolution with cell2location, neighborhood enrichment, ligand-receptor analysis
2. Single-Cell Analysis -> Process matched scRNA-seq reference, annotate cell types, export signatures for deconvolution
3. Gene Enrichment -> Pathway enrichment for each spatial cluster's marker genes
4. Systems Biology -> Model signaling networks from spatially co-localized ligand-receptor pairs

**"Identify spatially variable drug targets in diseased tissue"**
1. Spatial Transcriptomics -> SVG detection (Moran's I), pattern classification, druggability annotation via DrugBank/Open Targets
2. Gene Enrichment -> Enrichment analysis of SVG sets (gradient vs hotspot genes)
3. Multiomic Disease Characterization -> Integrate spatial SVGs with GWAS loci and eQTL data

**"Compare spatial cell organization between healthy and diseased samples"**
1. Spatial Transcriptomics -> Independent 8-phase pipeline for each condition, differential SVG analysis, compare neighborhood enrichment z-scores
2. Single-Cell Analysis -> Unified scRNA-seq reference for consistent deconvolution across conditions
3. Systems Biology -> Differential pathway activity across spatial domains between conditions

**"Deconvolve Slide-seq data and characterize niche interactions"**
1. Spatial Transcriptomics -> Slide-seq-specific preprocessing (10 um beads), Tangram deconvolution, spatial communication analysis
2. Single-Cell Analysis -> Curate high-quality scRNA-seq reference with refined cell-type annotations
3. Gene Enrichment -> Niche-specific gene signatures, GO/KEGG enrichment per spatial domain

## Completeness Checklist
- [ ] Platform identified and platform-specific parameters applied
- [ ] Data QC completed with spatial visualization of metrics
- [ ] Preprocessing (normalization, HVG selection) performed
- [ ] Spatial clustering completed with tissue-space visualization
- [ ] Spatially variable genes detected with Moran's I and FDR filtering
- [ ] SVG patterns classified (gradient, hotspot, boundary, periodic)
- [ ] Neighborhood enrichment and co-occurrence analyzed
- [ ] Cell-type deconvolution performed (if Visium/Slide-seq)
- [ ] Ligand-receptor interactions mapped with spatial constraints
- [ ] Top SVGs annotated with disease associations and druggability
