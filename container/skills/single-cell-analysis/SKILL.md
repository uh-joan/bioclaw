---
name: single-cell-analysis
description: Single-cell RNA-seq analysis specialist. Production-ready scRNA-seq pipelines covering QC, normalization, dimensionality reduction, clustering, differential expression, cell type annotation, batch correction, trajectory inference, and cell-cell communication. Use when user mentions single-cell, scRNA-seq, single cell RNA, scanpy, anndata, UMAP, t-SNE, Leiden clustering, cell type annotation, marker genes, pseudotime, trajectory inference, cell communication, ligand-receptor, pseudo-bulk, differential expression single cell, batch correction, harmony, 10x Genomics, Cell Ranger, or h5ad.
---

# Single-Cell Analysis

> **Code recipes**: See [recipes.md](recipes.md) for miRNA DE and scvi-tools templates, [clustering-recipes.md](clustering-recipes.md) for advanced clustering, batch correction, cell type annotation, doublet detection, and trajectory initialization, [qc-recipes.md](qc-recipes.md) for QC workflows (data loading, MAD filtering, ambient RNA removal, cell cycle scoring, multi-sample QC), and [scvi-recipes.md](scvi-recipes.md) for comprehensive scvi-tools models (scVI, scANVI, totalVI, PeakVI, MultiVI, DestVI, veloVI, sysVI, scArches, training diagnostics).

Production-ready scRNA-seq analysis methodology. The agent writes and executes Python code using scanpy/anndata for QC, normalization, dimensionality reduction, clustering, differential expression, cell type annotation, batch correction, trajectory inference, and cell-cell communication. Uses Open Targets, PubMed, ChEMBL, and DrugBank for biological annotation of results.

## Report-First Workflow

1. **Create report file immediately**: `[dataset]_single_cell_analysis_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Gene set enrichment of marker gene lists (ORA/GSEA) → use `gene-enrichment`
- Pathway and network analysis of DE results → use `systems-biology`
- Drug target assessment from cell communication hits → use `target-research`
- Disease associations for cell type markers → use `disease-research`
- Multi-omic integration with scRNA-seq data → use `multiomic-disease-characterization`
- Bulk RNA-seq differential expression (PyDESeq2) → use `rnaseq-deseq2`

## Cross-Reference: Other Skills

- **Gene set enrichment of marker genes** → use gene-enrichment skill
- **Pathway and network analysis of DE results** → use systems-biology skill
- **Drug targets from cell communication hits** → use target-research skill
- **Disease associations for cell type markers** → use disease-research skill
- **Multi-omic integration with scRNA-seq** → use multiomic-disease-characterization skill

## Available MCP Tools

### `mcp__opentargets__opentargets_info` (Gene-Disease Associations for Marker Genes)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_targets` | Search targets by gene symbol/name | `query`, `size` |
| `search_diseases` | Search diseases by name/synonym | `query`, `size` |
| `get_target_disease_associations` | Evidence-scored target-disease links | `targetId` (Ensembl ID), `diseaseId` (EFO ID), `minScore`, `size` |
| `get_disease_targets_summary` | All targets for a disease | `diseaseId`, `minScore`, `size` |
| `get_target_details` | Full target info (function, pathways, tractability) | `id` (Ensembl ID) |
| `get_disease_details` | Full disease info (ontology, phenotypes) | `id` (EFO ID) |

### `mcp__pubmed__pubmed_articles` (Cell Type Marker Literature)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Quick keyword search | `keywords`, `num_results` |
| `search_advanced` | Filtered search | `term`, `journal`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Full article details | `pmid` |

### `mcp__chembl__chembl_info` (Drug-Target for Cell Communication)

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

### `mcp__gtex__gtex_data` (Tissue Expression & eQTLs)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_genes` | Search genes in GTEx | `query`, `page`, `pageSize` |
| `get_median_gene_expression` | Median expression per tissue | `gencodeId`, `tissueSiteDetailId` |
| `get_gene_expression` | Expression across tissues | `gencodeId`, `tissueSiteDetailId` |
| `get_tissue_info` | Available tissue metadata | — |

### `mcp__geneontology__go_data` (Gene Ontology)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_go_terms` | Search GO terms by keyword | `query`, `size`, `ontology` (molecular_function/biological_process/cellular_component), `include_obsolete` |
| `get_go_term` | Get full GO term details (definition, synonyms, xrefs) | `id` (GO:XXXXXXX) |
| `validate_go_id` | Check if GO ID is valid | `id` |
| `get_ontology_stats` | GO ontology statistics | -- |

### `mcp__geo__geo_data` (GEO Public Datasets)

| Tool | Method | Use |
|------|--------|-----|
| `mcp__geo__geo_data` | `search_datasets` | Find scRNA-seq datasets for reference atlases or benchmarking |
| | `search_by_gene` | Find gene-specific expression datasets |
| | `get_series_info` | Get study details (design, samples, platform) |
| | `get_download_links` | Get FTP download URLs for raw/processed data |

**GEO workflow:** Find public scRNA-seq datasets in GEO for reference atlases, benchmarking, or meta-analysis.

```
mcp__geo__geo_data(method: "search_datasets", query: "single-cell RNA-seq TISSUE_OR_DISEASE")
mcp__geo__geo_data(method: "get_series_info", series_id: "GSExxxxxx")
mcp__geo__geo_data(method: "get_download_links", series_id: "GSExxxxxx")
```

---

## Analysis Decision Tree

```
User request → Determine analysis type:

├── Full scRNA-seq pipeline (raw data → annotated clusters)
│   → Go to "Full Pipeline Workflow"
│
├── Differential expression only (pre-processed object)
│   → Go to "Differential Expression Workflow"
│
├── Clustering / re-clustering only
│   → Go to "Clustering Workflow"
│
├── Correlation / co-expression analysis
│   → Go to "Correlation Workflow"
│
├── Cell-cell communication
│   → Go to "Cell Communication Workflow"
│
└── Trajectory / pseudotime inference
    → Go to "Trajectory Inference Workflow"
```

---

## Full Pipeline Workflow

### Step 1: Load Data and QC

```python
import scanpy as sc
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Load data (supports h5ad, 10x mtx, CSV, loom)
adata = sc.read_h5ad("data.h5ad")
# or: adata = sc.read_10x_mtx("filtered_feature_bc_matrix/")
# or: adata = sc.read_csv("counts.csv")

# Data orientation detection: auto-transpose if genes > samples by 5x
if adata.shape[1] > adata.shape[0] * 5:
    print(f"Detected transposed matrix ({adata.shape}), transposing...")
    adata = adata.T

# Ensure unique var/obs names
adata.var_names_make_unique()
adata.obs_names_make_unique()

# QC metrics
adata.var["mt"] = adata.var_names.str.startswith("MT-")
sc.pp.calculate_qc_metrics(adata, qc_vars=["mt"], percent_top=None, log1p=False, inplace=True)

# QC filtering
sc.pp.filter_cells(adata, min_genes=200)
sc.pp.filter_genes(adata, min_cells=3)
adata = adata[adata.obs.pct_counts_mt < 20, :].copy()

# QC plots
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
sc.pl.violin(adata, ["n_genes_by_counts"], ax=axes[0], show=False)
sc.pl.violin(adata, ["total_counts"], ax=axes[1], show=False)
sc.pl.violin(adata, ["pct_counts_mt"], ax=axes[2], show=False)
plt.tight_layout()
plt.savefig("qc_violins.png", dpi=150, bbox_inches="tight")
plt.show()

print(f"After QC: {adata.n_obs} cells, {adata.n_vars} genes")
```

### Step 2: Normalize and Select HVGs

```python
# Store raw counts for DE later
adata.layers["counts"] = adata.X.copy()

# Normalize to 10,000 counts per cell, log-transform
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)

# Store normalized data
adata.raw = adata

# Highly variable genes (top 2000)
sc.pp.highly_variable_genes(adata, n_top_genes=2000, flavor="seurat_v3", layer="counts")
sc.pl.highly_variable_genes(adata)
plt.savefig("hvg_selection.png", dpi=150, bbox_inches="tight")

# Subset to HVGs for dimensionality reduction
adata = adata[:, adata.var.highly_variable].copy()

# Scale (clip values at max 10 standard deviations)
sc.pp.scale(adata, max_value=10)
```

### Step 3: Dimensionality Reduction

```python
# PCA
sc.tl.pca(adata, n_comps=50, svd_solver="arpack")
sc.pl.pca_variance_ratio(adata, n_pcs=50, log=True)
plt.savefig("pca_variance.png", dpi=150, bbox_inches="tight")

# Select number of PCs (elbow method — typically 15-30)
n_pcs = 30

# Neighborhood graph
sc.pp.neighbors(adata, n_neighbors=15, n_pcs=n_pcs)

# UMAP
sc.tl.umap(adata)

# Plot UMAP
sc.pl.umap(adata, color=["total_counts", "n_genes_by_counts", "pct_counts_mt"], ncols=3)
plt.savefig("umap_qc.png", dpi=150, bbox_inches="tight")
```

### Step 4: Clustering

```python
# Leiden clustering (multiple resolutions to explore)
for res in [0.3, 0.5, 0.8, 1.0]:
    sc.tl.leiden(adata, resolution=res, key_added=f"leiden_{res}")

# Default resolution
sc.tl.leiden(adata, resolution=0.5)

# Plot clusters
sc.pl.umap(adata, color=["leiden", "leiden_0.3", "leiden_0.5", "leiden_0.8", "leiden_1.0"], ncols=3)
plt.savefig("umap_clusters.png", dpi=150, bbox_inches="tight")
```

### Step 5: Marker Genes

```python
# Wilcoxon rank-sum test for marker genes (recommended for single-cell)
sc.tl.rank_genes_groups(adata, groupby="leiden", method="wilcoxon", pts=True)
sc.pl.rank_genes_groups(adata, n_genes=10, sharey=False)
plt.savefig("marker_genes.png", dpi=150, bbox_inches="tight")

# Extract markers as DataFrame
markers = sc.get.rank_genes_groups_df(adata, group=None)
markers_filtered = markers[(markers["pvals_adj"] < 0.05) & (markers["logfoldchanges"] > 1)]

# Top 5 markers per cluster
top_markers = markers_filtered.groupby("group").head(5)
print(top_markers[["group", "names", "logfoldchanges", "pvals_adj", "pct_nz_group", "pct_nz_reference"]])

# Dotplot of top markers
top_genes = markers_filtered.groupby("group").head(3)["names"].tolist()
sc.pl.dotplot(adata, var_names=top_genes, groupby="leiden", standard_scale="var")
plt.savefig("marker_dotplot.png", dpi=150, bbox_inches="tight")
```

### Step 6: Cell Type Annotation

```python
# Manual annotation based on canonical markers
# Look up marker genes using MCP tools, then assign:

cell_type_map = {
    "0": "T cells",         # CD3D, CD3E, IL7R
    "1": "Monocytes",       # CD14, LYZ, S100A8
    "2": "B cells",         # CD79A, MS4A1, CD19
    "3": "NK cells",        # GNLY, NKG7, KLRD1
    "4": "Dendritic cells", # FCER1A, CST3, CLEC10A
    # ... extend based on marker gene results
}
adata.obs["cell_type"] = adata.obs["leiden"].map(cell_type_map)

sc.pl.umap(adata, color=["cell_type"], legend_loc="on data")
plt.savefig("umap_celltypes.png", dpi=150, bbox_inches="tight")
```

**MCP-assisted annotation — validate markers against literature:**

```
1. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "CD3D CD3E marker T cell single-cell RNA-seq", num_results: 5)
   → Confirm marker-cell type associations from literature

2. mcp__opentargets__opentargets_info(method: "search_targets", query: "CD14")
   → Get Ensembl ID and target details for key markers

3. mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   → Function, expression pattern, known associations for marker gene

4. mcp__geneontology__go_data(method: "search_go_terms", query: "T cell activation", ontology: "biological_process", size: 5)
   → Validate GO terms associated with marker gene enrichment results

5. mcp__geneontology__go_data(method: "get_go_term", id: "GO:0042110")
   → Get full definition and synonyms for GO terms enriched in cluster markers

6. mcp__gtex__gtex_data(method: "search_genes", query: "MARKER_GENE")
   → Get GENCODE ID for GTEx bulk reference expression

7. mcp__gtex__gtex_data(method: "get_median_gene_expression", gencodeId: "ENSG00000xxxxx.xx")
   → Bulk tissue expression reference — compare single-cell marker expression patterns against GTEx bulk reference to validate cell type annotations and assess tissue specificity
```

---

## Differential Expression Workflow

### DE Method Selection

```
Experimental design → Choose DE method:

├── Single-cell level DE (cluster vs cluster, condition within cluster)
│   ├── Wilcoxon rank-sum (default, robust, non-parametric)
│   │   sc.tl.rank_genes_groups(adata, groupby="group", method="wilcoxon")
│   ├── t-test with overestimated variance (fast, parametric)
│   │   sc.tl.rank_genes_groups(adata, groupby="group", method="t-test_overestim_var")
│   └── Logistic regression (multi-class, accounts for covariates)
│       sc.tl.rank_genes_groups(adata, groupby="group", method="logreg")
│
├── Pseudo-bulk DE (multiple biological replicates, condition comparison)
│   └── PyDESeq2 (aggregates cells per sample, proper statistical model)
│       → Go to "Pseudo-bulk DE Template"
│
└── Simple two-group comparison (no single-cell structure)
    ├── scipy.stats.mannwhitneyu (non-parametric)
    └── scipy.stats.ttest_ind (parametric)
```

### Pseudo-bulk DE Template (PyDESeq2)

```python
import anndata as ad
from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds import DeseqStats

# Aggregate counts per sample per cell type
def pseudo_bulk(adata, sample_col, celltype_col, condition_col):
    results = []
    for ct in adata.obs[celltype_col].unique():
        ct_data = adata[adata.obs[celltype_col] == ct]
        for sample in ct_data.obs[sample_col].unique():
            mask = ct_data.obs[sample_col] == sample
            counts = ct_data[mask].layers["counts"].sum(axis=0)
            counts = np.asarray(counts).flatten()
            condition = ct_data.obs.loc[mask, condition_col].iloc[0]
            results.append({
                "sample": sample,
                "cell_type": ct,
                "condition": condition,
                "counts": counts
            })
    return results

aggregated = pseudo_bulk(adata, "sample", "cell_type", "condition")

# Build count matrix and metadata for one cell type
ct_data = [r for r in aggregated if r["cell_type"] == "T cells"]
count_matrix = pd.DataFrame(
    [r["counts"] for r in ct_data],
    index=[r["sample"] for r in ct_data],
    columns=adata.var_names
)
metadata = pd.DataFrame(
    {"condition": [r["condition"] for r in ct_data]},
    index=[r["sample"] for r in ct_data]
)

# Run PyDESeq2
dds = DeseqDataSet(counts=count_matrix, metadata=metadata, design="~condition")
dds.deseq2()
stat_res = DeseqStats(dds, contrast=["condition", "treated", "control"])
stat_res.summary()
results_df = stat_res.results_df
sig_genes = results_df[(results_df.padj < 0.05) & (abs(results_df.log2FoldChange) > 1)]
print(f"Significant DE genes: {len(sig_genes)}")
```

---

## Batch Correction Workflow

### Harmony Integration (Multi-Sample)

```python
import harmonypy as hm

# Assumes PCA already computed and batch column in adata.obs
# adata.obs["batch"] must contain batch labels

# Run Harmony on PCA embeddings
ho = hm.run_harmony(adata.obsm["X_pca"], adata.obs, "batch", max_iter_harmony=20)
adata.obsm["X_pca_harmony"] = ho.Z_corr.T

# Recompute neighbors and UMAP from corrected embeddings
sc.pp.neighbors(adata, use_rep="X_pca_harmony", n_neighbors=15)
sc.tl.umap(adata)
sc.tl.leiden(adata, resolution=0.5)

# Plot before/after
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
sc.pl.umap(adata, color="batch", ax=axes[0], title="After Harmony", show=False)
# Store pre-harmony UMAP in obsm for comparison
sc.pl.umap(adata, color="leiden", ax=axes[1], title="Clusters (Harmony)", show=False)
plt.savefig("harmony_integration.png", dpi=150, bbox_inches="tight")
```

### Alternative: scVI Integration

```python
import scvi

# Requires raw counts in adata.layers["counts"]
scvi.model.SCVI.setup_anndata(adata, layer="counts", batch_key="batch")
model = scvi.model.SCVI(adata, n_latent=30, n_layers=2)
model.train(max_epochs=200, early_stopping=True)
adata.obsm["X_scVI"] = model.get_latent_representation()

sc.pp.neighbors(adata, use_rep="X_scVI", n_neighbors=15)
sc.tl.umap(adata)
sc.tl.leiden(adata, resolution=0.5)
```

---

## Cell-Cell Communication Workflow

### OmniPath Ligand-Receptor Analysis

```python
import omnipath as op

# Get curated ligand-receptor interactions from OmniPath
interactions = op.interactions.AllInteractions.get(
    genesymbols=True,
    datasets=["ligrecextra", "CellChatDB", "CellPhoneDB"]
)

# Filter to ligand-receptor pairs
lr_pairs = interactions[
    (interactions["is_directed"]) &
    (interactions["consensus_direction"])
][["source_genesymbol", "target_genesymbol"]].drop_duplicates()

# Score communication between cell types
def score_communication(adata, lr_pairs, celltype_col="cell_type"):
    """Score ligand-receptor activity between cell type pairs."""
    # Get mean expression per cell type (from raw/normalized data)
    cell_types = adata.obs[celltype_col].unique()
    mean_expr = pd.DataFrame(
        index=adata.raw.var_names,
        columns=cell_types,
        data=np.zeros((adata.raw.n_vars, len(cell_types)))
    )
    for ct in cell_types:
        mask = adata.obs[celltype_col] == ct
        mean_expr[ct] = np.asarray(adata.raw[mask].X.mean(axis=0)).flatten()

    results = []
    for _, row in lr_pairs.iterrows():
        ligand, receptor = row["source_genesymbol"], row["target_genesymbol"]
        if ligand in mean_expr.index and receptor in mean_expr.index:
            for sender in cell_types:
                for receiver in cell_types:
                    lig_expr = mean_expr.loc[ligand, sender]
                    rec_expr = mean_expr.loc[receptor, receiver]
                    if lig_expr > 0.1 and rec_expr > 0.1:
                        score = lig_expr * rec_expr
                        results.append({
                            "ligand": ligand, "receptor": receptor,
                            "sender": sender, "receiver": receiver,
                            "score": score
                        })
    return pd.DataFrame(results).sort_values("score", ascending=False)

comm_scores = score_communication(adata, lr_pairs)
print(comm_scores.head(20))
```

**MCP-assisted annotation of communication hits:**

```
1. mcp__chembl__chembl_info(method: "target_search", query: "RECEPTOR_NAME")
   → Find ChEMBL target ID for the receptor

2. mcp__drugbank__drugbank_info(method: "search_by_target", target: "RECEPTOR_NAME")
   → Existing drugs targeting this receptor

3. mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   → Druggability and tractability of the receptor target

4. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "LIGAND RECEPTOR cell communication single-cell", num_results: 10)
   → Literature evidence for this signaling axis
```

---

## Trajectory Inference Workflow

### Diffusion Pseudotime and PAGA

```python
# Assumes preprocessed adata with neighbors graph computed

# PAGA — partition-based graph abstraction
sc.tl.paga(adata, groups="leiden")
sc.pl.paga(adata, plot=True, threshold=0.1)
plt.savefig("paga_graph.png", dpi=150, bbox_inches="tight")

# Initialize UMAP with PAGA positions for better layout
sc.tl.umap(adata, init_pos="paga")

# Diffusion map
sc.tl.diffmap(adata, n_comps=15)

# Set root cell (select cluster representing progenitor/stem cells)
root_cluster = "0"  # adjust based on biology
adata.uns["iroot"] = np.flatnonzero(adata.obs["leiden"] == root_cluster)[0]

# Diffusion pseudotime
sc.tl.dpt(adata)

# Plot pseudotime on UMAP
sc.pl.umap(adata, color=["dpt_pseudotime", "leiden", "cell_type"], ncols=3)
plt.savefig("trajectory_pseudotime.png", dpi=150, bbox_inches="tight")

# Genes changing along pseudotime
sc.pl.paga_path(
    adata,
    nodes=["0", "1", "3", "5"],  # adjust path through clusters
    keys=["gene1", "gene2", "gene3"],  # genes of interest
)
plt.savefig("trajectory_genes.png", dpi=150, bbox_inches="tight")
```

### Alternative: scVelo RNA Velocity

```python
import scvelo as scv

# Requires spliced/unspliced counts (from velocyto or STARsolo)
scv.pp.filter_and_normalize(adata, min_shared_counts=20, n_top_genes=2000)
scv.pp.moments(adata, n_pcs=30, n_neighbors=30)
scv.tl.velocity(adata, mode="stochastic")
scv.tl.velocity_graph(adata)

scv.pl.velocity_embedding_stream(adata, basis="umap", color="cell_type")
plt.savefig("rna_velocity.png", dpi=150, bbox_inches="tight")
```

---

## Scanpy-to-Seurat Equivalence Table

| Task | Scanpy (Python) | Seurat (R) |
|------|-----------------|------------|
| **Load 10x** | `sc.read_10x_mtx()` | `Read10X()` + `CreateSeuratObject()` |
| **QC metrics** | `sc.pp.calculate_qc_metrics()` | `PercentageFeatureSet()` |
| **Filter cells** | `sc.pp.filter_cells()` | `subset(obj, nFeature_RNA > 200)` |
| **Normalize** | `sc.pp.normalize_total()` + `sc.pp.log1p()` | `NormalizeData()` |
| **HVGs** | `sc.pp.highly_variable_genes()` | `FindVariableFeatures()` |
| **Scale** | `sc.pp.scale()` | `ScaleData()` |
| **PCA** | `sc.tl.pca()` | `RunPCA()` |
| **Neighbors** | `sc.pp.neighbors()` | `FindNeighbors()` |
| **UMAP** | `sc.tl.umap()` | `RunUMAP()` |
| **Clustering** | `sc.tl.leiden()` | `FindClusters()` |
| **DE / Markers** | `sc.tl.rank_genes_groups()` | `FindAllMarkers()` |
| **Dotplot** | `sc.pl.dotplot()` | `DotPlot()` |
| **Integration** | `harmonypy` / `scvi` | `IntegrateLayers()` / `Harmony` |
| **Pseudotime** | `sc.tl.dpt()` | `monocle3::learn_graph()` |
| **Velocity** | `scvelo` | `velocyto.R` |

---

## Correlation Workflow

```python
# Gene-gene correlation within a cell type
ct_adata = adata[adata.obs["cell_type"] == "T cells"]
gene_a = "CD8A"
gene_b = "GZMB"

from scipy.stats import spearmanr
expr_a = ct_adata.raw[:, gene_a].X.toarray().flatten()
expr_b = ct_adata.raw[:, gene_b].X.toarray().flatten()
corr, pval = spearmanr(expr_a, expr_b)
print(f"Spearman correlation {gene_a} vs {gene_b}: r={corr:.3f}, p={pval:.2e}")

# Correlation matrix for a gene set
genes_of_interest = ["CD8A", "GZMB", "PRF1", "IFNG", "TNF"]
expr_matrix = pd.DataFrame(
    ct_adata.raw[:, genes_of_interest].X.toarray(),
    columns=genes_of_interest
)
corr_matrix = expr_matrix.corr(method="spearman")

import seaborn as sns
sns.clustermap(corr_matrix, cmap="RdBu_r", vmin=-1, vmax=1, annot=True, fmt=".2f")
plt.savefig("gene_correlation.png", dpi=150, bbox_inches="tight")
```

---

## Clustering Workflow

```python
# Re-clustering a subset of cells
subset = adata[adata.obs["cell_type"].isin(["T cells"])].copy()

# Re-run HVG, PCA, neighbors, UMAP, Leiden on subset
sc.pp.highly_variable_genes(subset, n_top_genes=2000, flavor="seurat_v3", layer="counts")
subset = subset[:, subset.var.highly_variable].copy()
sc.pp.scale(subset, max_value=10)
sc.tl.pca(subset, n_comps=30)
sc.pp.neighbors(subset, n_neighbors=15, n_pcs=20)
sc.tl.umap(subset)

# Test multiple resolutions
for res in [0.3, 0.5, 0.8, 1.0, 1.5]:
    sc.tl.leiden(subset, resolution=res, key_added=f"leiden_{res}")

sc.pl.umap(subset, color=[f"leiden_{r}" for r in [0.3, 0.5, 0.8, 1.0, 1.5]], ncols=3)
plt.savefig("subclustering.png", dpi=150, bbox_inches="tight")

# Markers for subclusters
sc.tl.rank_genes_groups(subset, groupby="leiden_0.5", method="wilcoxon")
sc.pl.rank_genes_groups(subset, n_genes=10, sharey=False)
plt.savefig("subcluster_markers.png", dpi=150, bbox_inches="tight")
```

---

## Data Orientation Detection

```python
def load_and_orient(path):
    """Load data and auto-detect orientation."""
    if path.endswith(".h5ad"):
        adata = sc.read_h5ad(path)
    elif path.endswith(".csv") or path.endswith(".tsv"):
        sep = "\t" if path.endswith(".tsv") else ","
        df = pd.read_csv(path, index_col=0, sep=sep)
        adata = ad.AnnData(df)
    elif path.endswith(".loom"):
        adata = sc.read_loom(path)
    else:
        adata = sc.read_10x_mtx(path)

    # Auto-transpose: if n_vars >> n_obs by 5x, matrix is likely transposed
    if adata.n_vars > adata.n_obs * 5:
        print(f"Auto-transposing: {adata.shape} → ", end="")
        adata = adata.T
        print(f"{adata.shape}")

    adata.var_names_make_unique()
    adata.obs_names_make_unique()

    # Validate: check for known gene names in var
    known_genes = {"GAPDH", "ACTB", "MALAT1", "MT-CO1", "CD3D", "CD19"}
    overlap = known_genes & set(adata.var_names)
    if len(overlap) == 0:
        print("WARNING: No common housekeeping genes found in var_names. Check orientation.")

    return adata
```

---

## Multi-Agent Workflow Examples

**"Analyze scRNA-seq data from tumor microenvironment and identify therapeutic targets"**
1. Single-Cell Analysis → Full pipeline: QC, clustering, cell type annotation, DE between tumor subtypes
2. Gene Enrichment → Pathway enrichment of marker genes and DE results (GSEA, GO, KEGG)
3. Target Research → Druggability assessment of top DE genes and cell communication receptors
4. Disease Research → Disease associations for novel cell type markers

**"Integrate multi-batch scRNA-seq and characterize disease-specific cell states"**
1. Single-Cell Analysis → Harmony batch correction, Leiden clustering, pseudo-bulk DE between conditions
2. Systems Biology → Network analysis of DE genes, regulatory module identification
3. Multiomic Disease Characterization → Integration with ATAC-seq or proteomics if available
4. Disease Research → Known associations for disease-enriched cell populations

**"Identify druggable cell communication axes in inflammatory disease"**
1. Single-Cell Analysis → Cell communication analysis using OmniPath ligand-receptor pairs
2. Target Research → Druggability and tractability of top receptor targets
3. Drug Target Analyst → Existing compounds and bioactivity for top communication targets
4. Disease Research → Genetic evidence linking communication targets to disease

## Completeness Checklist

- [ ] Data loaded and orientation validated (cells x genes, known housekeeping genes in var_names)
- [ ] QC filtering applied (min genes, min cells, mitochondrial %, QC violin plots saved)
- [ ] Normalization and HVG selection completed (log-normalized, top 2000 HVGs)
- [ ] Dimensionality reduction performed (PCA with elbow assessment, UMAP)
- [ ] Clustering executed at multiple resolutions with optimal resolution selected
- [ ] Marker genes identified per cluster (Wilcoxon, padj < 0.05, logFC > 1)
- [ ] Cell type annotations assigned with literature validation via MCP tools
- [ ] Batch correction applied if multi-sample/multi-batch data (Harmony or scVI)
- [ ] Differential expression or cell communication analysis completed if requested
- [ ] Report file finalized with no `[Analyzing...]` placeholders remaining
