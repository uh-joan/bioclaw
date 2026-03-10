---
name: gene-regulatory-networks
description: Gene regulatory network inference and analysis. pySCENIC pipeline with GRNBoost2 for network inference, cisTarget for motif enrichment and regulon pruning, AUCell for regulon activity scoring per cell, WGCNA weighted gene coexpression network analysis with soft-thresholding power selection and module eigengenes, coexpression network construction with Pearson and Spearman correlation and mutual information and ARACNe, differential network analysis comparing GRNs across conditions, network inference from perturbation data with CellOracle and Dictys, regulon visualization with heatmaps and UMAP overlays and RSS regulon specificity score, integration with chromatin accessibility via SCENIC+, cisTarget motif databases and ranking databases for hg38 and mm10, GRNBoost2 importance threshold tuning, AUCell percentile thresholds. Use when user asks about gene regulatory networks, GRN, regulons, pySCENIC, SCENIC, GRNBoost2, cisTarget, AUCell, WGCNA, coexpression networks, transcription factor networks, regulon activity, network inference, ARACNe, mutual information networks, CellOracle, perturbation networks, Dictys, regulon specificity, module eigengenes, soft-thresholding, or SCENIC+.
---

# Gene Regulatory Network Inference and Analysis

Comprehensive pipeline for inferring and analyzing gene regulatory networks (GRNs). Covers the pySCENIC pipeline (GRNBoost2 -> cisTarget -> AUCell), WGCNA coexpression networks, mutual information-based methods (ARACNe), perturbation-based inference (CellOracle, Dictys), and integration with chromatin accessibility data (SCENIC+).

## Report-First Workflow

1. **Create report file immediately**: `[topic]_grn_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as analysis completes
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Single-cell clustering and cell type annotation -> use `single-cell-analysis`
- Differential gene expression (DESeq2, edgeR) -> use `transcriptomics`
- Pathway enrichment (GO, KEGG, Reactome) -> use `gene-enrichment`
- ChIP-seq TF binding analysis -> use `chipseq-analysis`
- ATAC-seq chromatin accessibility -> use `atac-seq-analysis`
- Protein-protein interaction networks -> use `systems-biology`

## Cross-Reference: Other Skills

- **Single-cell preprocessing and clustering** -> use single-cell-analysis skill
- **Pathway enrichment on regulon gene lists** -> use gene-enrichment skill
- **TF ChIP-seq binding data** -> use chipseq-analysis skill
- **Chromatin accessibility for SCENIC+** -> use atac-seq-analysis skill
- **Multi-omics integration** -> use multi-omics-integration skill

---

## GRN Inference Method Selection

```
What data do you have?
|
+-> Single-cell RNA-seq
|   |
|   +-> Expression data only
|   |   -> pySCENIC (GRNBoost2 + cisTarget + AUCell)
|   |   -> Best for: TF-target regulon discovery
|   |
|   +-> Expression + scATAC-seq (multiome)
|   |   -> SCENIC+ (integrates chromatin accessibility)
|   |   -> Best for: enhancer-driven regulatory networks
|   |
|   +-> Expression + perturbation data (CRISPR screens)
|       -> CellOracle or Dictys
|       -> Best for: causal GRN inference
|
+-> Bulk RNA-seq
|   |
|   +-> Many samples (> 20), exploratory
|   |   -> WGCNA (weighted coexpression networks)
|   |   -> Best for: module discovery, trait correlation
|   |
|   +-> Expression + TF binding (ChIP-seq)
|   |   -> Integrate coexpression with binding data
|   |   -> Correlation + binding evidence = high confidence
|   |
|   +-> Time-series expression
|       -> ARACNe (mutual information) or GENIE3
|       -> Best for: dynamic regulatory relationships
|
+-> Want to compare networks across conditions?
    -> Differential network analysis
    -> Compare regulon activity, module preservation
```

---

## Phase 1: pySCENIC Pipeline

### Overview

```
The pySCENIC pipeline has three sequential steps:

Step 1: GRNBoost2 (or GENIE3)
  - Input: Expression matrix (genes x cells)
  - Output: TF-target gene adjacencies with importance scores
  - Method: Gradient boosting regression (each gene predicted from TFs)
  - Note: Identifies co-expression, NOT causality

Step 2: cisTarget (RcisTarget in R)
  - Input: TF-target adjacencies from Step 1
  - Output: Pruned regulons (TF + validated target genes)
  - Method: Motif enrichment in cis-regulatory regions of target genes
  - Purpose: Filters false positives by requiring TF motif presence

Step 3: AUCell
  - Input: Regulons from Step 2 + expression matrix
  - Output: Regulon activity scores per cell (AUC values)
  - Method: Area Under the recovery Curve ranking
  - Purpose: Quantify regulon activity in each cell
```

### Step 1: GRNBoost2 Network Inference

```python
import pandas as pd
import numpy as np
from arboreto.algo import grnboost2
from ctxcore.rnkdb import FeatherRankingDatabase

def run_grnboost2(expression_matrix, tf_list_file, output_file="adjacencies.tsv",
                   seed=42):
    """Run GRNBoost2 to infer TF-target gene co-expression network.

    Parameters:
      expression_matrix: DataFrame, genes as columns, cells as rows
      tf_list_file: Path to file with one TF name per line
      output_file: Path to save adjacencies

    Critical parameters:
      - expression_matrix should be log-normalized (e.g., Scanpy default)
      - Only include genes expressed in >= 1-3% of cells
      - TF list should match gene names in expression matrix exactly
    """
    # Load TF list
    with open(tf_list_file) as f:
        tf_names = [line.strip() for line in f if line.strip()]

    # Filter TFs present in expression matrix
    available_tfs = [tf for tf in tf_names if tf in expression_matrix.columns]
    print(f"TFs available: {len(available_tfs)} / {len(tf_names)}")
    print(f"Total genes: {expression_matrix.shape[1]}")
    print(f"Total cells: {expression_matrix.shape[0]}")

    # Run GRNBoost2
    adjacencies = grnboost2(
        expression_data=expression_matrix,
        tf_names=available_tfs,
        seed=seed,
        verbose=True
    )

    # Save adjacencies
    adjacencies.to_csv(output_file, sep='\t', index=False)
    print(f"\nAdjacencies computed: {len(adjacencies)}")
    print(f"Unique TFs: {adjacencies['TF'].nunique()}")
    print(f"Unique targets: {adjacencies['target'].nunique()}")

    # Importance score distribution
    print(f"\nImportance score distribution:")
    print(f"  Mean: {adjacencies['importance'].mean():.4f}")
    print(f"  Median: {adjacencies['importance'].median():.4f}")
    print(f"  95th percentile: {adjacencies['importance'].quantile(0.95):.4f}")
    print(f"  99th percentile: {adjacencies['importance'].quantile(0.99):.4f}")

    return adjacencies
```

**GRNBoost2 parameter guidance:**

| Parameter | Consideration |
|-----------|---------------|
| Input genes | Filter to >= 1% cells expressing (reduces noise and compute time) |
| TF list | Use curated list (e.g., AnimalTFDB, Lambert et al. 2018) |
| Number of cells | 5,000-20,000 optimal; subsample if > 50,000 |
| Normalization | Log-normalized counts (not scaled/regressed) |
| Importance threshold | Keep top 50-100 targets per TF (or importance > median) |
| Seed | Set for reproducibility |

### Step 2: cisTarget Regulon Pruning

```python
from pyscenic.prune import prune2df, df2regulons
from ctxcore.rnkdb import FeatherRankingDatabase as RankingDatabase

def run_cistarget(adjacencies, expression_matrix,
                   ranking_db_paths, motif_annotation_file,
                   output_file="regulons.pkl"):
    """Run cisTarget to prune GRNBoost2 adjacencies into regulons.

    Parameters:
      adjacencies: DataFrame from GRNBoost2
      expression_matrix: Same matrix used for GRNBoost2
      ranking_db_paths: List of paths to feather ranking databases
      motif_annotation_file: Path to motif2TF annotation file

    Required databases (download from cisTarget resources):
      Ranking databases (feather format):
        hg38: hg38_10kbp_up_10kbp_down_full_tx_v10_clust.genes_vs_motifs.rankings.feather
              hg38_500bp_up_100bp_down_full_tx_v10_clust.genes_vs_motifs.rankings.feather
        mm10: mm10_10kbp_up_10kbp_down_full_tx_v10_clust.genes_vs_motifs.rankings.feather
              mm10_500bp_up_100bp_down_full_tx_v10_clust.genes_vs_motifs.rankings.feather

      Motif annotation:
        motifs-v10nr_clust-nr.hgnc-m0.001-o0.0.tbl (human)
        motifs-v10nr_clust-nr.mgi-m0.001-o0.0.tbl (mouse)
    """
    # Load ranking databases
    dbs = [RankingDatabase(fname=path, name=path.split('/')[-1])
           for path in ranking_db_paths]
    print(f"Loaded {len(dbs)} ranking databases")

    # Prune adjacencies using cisTarget
    df_motifs = prune2df(
        dbs,
        adjacencies,
        motif_annotation_file,
        num_workers=8,
        module_chunksize=100
    )

    # Convert to regulons
    regulons = df2regulons(df_motifs)

    # Save regulons
    import pickle
    with open(output_file, 'wb') as f:
        pickle.dump(regulons, f)

    print(f"\nRegulons discovered: {len(regulons)}")
    for reg in sorted(regulons, key=lambda r: len(r.genes), reverse=True)[:20]:
        print(f"  {reg.name}: {len(reg.genes)} target genes")

    return regulons, df_motifs
```

**cisTarget database selection:**

| Genome | Promoter DB | Extended DB | Use Case |
|--------|-------------|-------------|----------|
| hg38 | 500bp_up_100bp_down | 10kbp_up_10kbp_down | Human analyses |
| mm10 | 500bp_up_100bp_down | 10kbp_up_10kbp_down | Mouse analyses |

```
Always use BOTH promoter and extended databases:
  - Promoter DB: captures proximal regulatory motifs (TSS-proximal TF binding)
  - Extended DB: captures distal enhancer motifs (long-range regulation)
  - Using both increases sensitivity without increasing false positives
  - cisTarget internally takes the union of enriched motifs from both
```

### Step 3: AUCell Regulon Activity Scoring

```python
from pyscenic.aucell import aucell
import pandas as pd

def run_aucell(expression_matrix, regulons, output_file="auc_matrix.csv",
                auc_threshold=0.05, num_workers=8):
    """Score regulon activity per cell using AUCell.

    Parameters:
      expression_matrix: Same as input to GRNBoost2
      regulons: Regulon objects from cisTarget
      auc_threshold: Fraction of ranked genes to use for AUC calculation
        - Default 0.05 = top 5% of genes
        - Increase for small regulons, decrease for large regulons
        - Range: 0.01 - 0.2

    Output: AUC matrix (regulons x cells)
      Values represent regulon activity strength per cell
      Higher AUC = more target genes highly expressed in that cell
    """
    auc_mtx = aucell(
        expression_matrix,
        regulons,
        auc_threshold=auc_threshold,
        num_workers=num_workers
    )

    auc_mtx.to_csv(output_file)
    print(f"AUCell matrix: {auc_mtx.shape[0]} cells x {auc_mtx.shape[1]} regulons")
    print(f"\nTop variable regulons:")
    var = auc_mtx.var().sort_values(ascending=False)
    for reg_name, variance in var.head(20).items():
        print(f"  {reg_name}: var={variance:.6f}, "
              f"mean={auc_mtx[reg_name].mean():.4f}")

    return auc_mtx

def binarize_aucell(auc_mtx, method='otsu'):
    """Binarize AUCell scores to ON/OFF regulon states.

    Methods:
      'otsu': Otsu's thresholding (default, automatic)
      'percentile': Use 75th percentile as threshold
      'gmm': Gaussian mixture model (2 components)
    """
    from skimage.filters import threshold_otsu
    from sklearn.mixture import GaussianMixture

    binary_mtx = pd.DataFrame(0, index=auc_mtx.index, columns=auc_mtx.columns)
    thresholds = {}

    for regulon in auc_mtx.columns:
        values = auc_mtx[regulon].values

        if method == 'otsu':
            try:
                thresh = threshold_otsu(values)
            except ValueError:
                thresh = np.percentile(values, 75)
        elif method == 'percentile':
            thresh = np.percentile(values, 75)
        elif method == 'gmm':
            gmm = GaussianMixture(n_components=2, random_state=42)
            gmm.fit(values.reshape(-1, 1))
            means = gmm.means_.flatten()
            thresh = np.mean(means)

        binary_mtx[regulon] = (auc_mtx[regulon] > thresh).astype(int)
        thresholds[regulon] = thresh

    on_fraction = binary_mtx.mean()
    print("Binarized regulon ON fractions:")
    for reg in on_fraction.sort_values(ascending=False).head(20).index:
        print(f"  {reg}: {on_fraction[reg]:.1%} cells ON (threshold: {thresholds[reg]:.4f})")

    return binary_mtx, thresholds
```

### AUCell Threshold Tuning

```
AUCell auc_threshold parameter affects sensitivity:

  auc_threshold = 0.01 (1%):
    - Very stringent; only considers top-ranked genes
    - Best for: large regulons (>200 genes)
    - Risk: may miss weakly activated regulons

  auc_threshold = 0.05 (5%) [DEFAULT]:
    - Balanced sensitivity and specificity
    - Best for: typical regulons (20-200 genes)
    - Recommended starting point

  auc_threshold = 0.15-0.20 (15-20%):
    - More permissive; captures weaker signals
    - Best for: small regulons (<20 genes)
    - Risk: more noise, less discriminating

  Rule of thumb:
    auc_threshold should be set so that the number of genes
    considered (threshold * total_genes) is larger than the
    typical regulon size. If your regulons average 100 genes
    and you have 20,000 genes, 0.05 * 20,000 = 1,000 >> 100.
```

### Complete pySCENIC Workflow

```python
import scanpy as sc
import loompy
from pyscenic.cli.utils import load_signatures

def run_scenic_pipeline(adata, tf_list_file, ranking_db_paths,
                         motif_annotation_file, output_dir="scenic_output/"):
    """Run complete pySCENIC pipeline from AnnData object.

    Parameters:
      adata: Scanpy AnnData (log-normalized, filtered)
      tf_list_file: Path to TF list
      ranking_db_paths: List of paths to cisTarget ranking DBs
      motif_annotation_file: Path to motif annotation table
    """
    import os
    os.makedirs(output_dir, exist_ok=True)

    # Prepare expression matrix (genes as columns, cells as rows)
    expr_matrix = pd.DataFrame(
        adata.X.toarray() if hasattr(adata.X, 'toarray') else adata.X,
        index=adata.obs_names,
        columns=adata.var_names
    )

    # Filter genes: keep genes expressed in >= 1% of cells
    gene_filter = (expr_matrix > 0).mean(axis=0) >= 0.01
    expr_matrix = expr_matrix.loc[:, gene_filter]
    print(f"Genes after filtering: {expr_matrix.shape[1]}")

    # Step 1: GRNBoost2
    print("\n=== Step 1: GRNBoost2 ===")
    adjacencies = run_grnboost2(
        expr_matrix, tf_list_file,
        output_file=os.path.join(output_dir, "adjacencies.tsv")
    )

    # Step 2: cisTarget
    print("\n=== Step 2: cisTarget ===")
    regulons, df_motifs = run_cistarget(
        adjacencies, expr_matrix,
        ranking_db_paths, motif_annotation_file,
        output_file=os.path.join(output_dir, "regulons.pkl")
    )

    # Step 3: AUCell
    print("\n=== Step 3: AUCell ===")
    auc_mtx = run_aucell(
        expr_matrix, regulons,
        output_file=os.path.join(output_dir, "auc_matrix.csv")
    )

    # Add AUCell scores to AnnData
    adata.obsm['X_aucell'] = auc_mtx.loc[adata.obs_names].values
    adata.uns['regulon_names'] = list(auc_mtx.columns)

    return adata, regulons, auc_mtx
```

---

## Phase 2: Regulon Visualization

### UMAP Overlay of Regulon Activity

```python
import scanpy as sc
import matplotlib.pyplot as plt
import numpy as np

def plot_regulon_activity_umap(adata, auc_mtx, regulon_names, n_cols=4,
                                 output_png="regulon_umap.png"):
    """Plot regulon activity on UMAP embedding."""
    n_regs = len(regulon_names)
    n_rows = int(np.ceil(n_regs / n_cols))
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(4 * n_cols, 4 * n_rows))
    axes = axes.flatten() if n_regs > 1 else [axes]

    for i, reg_name in enumerate(regulon_names):
        if reg_name not in auc_mtx.columns:
            continue
        adata.obs['_regulon_score'] = auc_mtx.loc[adata.obs_names, reg_name].values
        sc.pl.umap(adata, color='_regulon_score', ax=axes[i],
                    title=reg_name, show=False, color_map='YlOrRd',
                    frameon=False, size=5)

    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)

    plt.tight_layout()
    plt.savefig(output_png, dpi=150, bbox_inches='tight')
    print(f"Saved: {output_png}")

def regulon_specificity_score(auc_mtx, cell_type_labels):
    """Calculate Regulon Specificity Score (RSS) for each cell type.

    RSS measures how specifically a regulon is active in one cell type
    versus others. Based on Jensen-Shannon divergence.

    RSS = 1 - sqrt(JSD(regulon_activity || cell_type_indicator))
    High RSS = regulon is specific to that cell type
    """
    from scipy.spatial.distance import jensenshannon

    cell_types = sorted(cell_type_labels.unique())
    rss_matrix = pd.DataFrame(index=auc_mtx.columns, columns=cell_types)

    for ct in cell_types:
        # Binary indicator for cell type
        ct_indicator = (cell_type_labels == ct).astype(float)
        ct_indicator = ct_indicator / ct_indicator.sum()

        for regulon in auc_mtx.columns:
            # Normalize regulon activity to probability distribution
            reg_activity = auc_mtx[regulon].values.copy()
            reg_activity = reg_activity - reg_activity.min()
            reg_sum = reg_activity.sum()
            if reg_sum > 0:
                reg_activity = reg_activity / reg_sum
            else:
                reg_activity = np.ones_like(reg_activity) / len(reg_activity)

            jsd = jensenshannon(reg_activity, ct_indicator.values)
            rss = 1 - jsd
            rss_matrix.loc[regulon, ct] = rss

    rss_matrix = rss_matrix.astype(float)

    # Report top regulons per cell type
    print("Top specific regulons per cell type:")
    for ct in cell_types:
        top = rss_matrix[ct].nlargest(5)
        print(f"\n  {ct}:")
        for reg, score in top.items():
            print(f"    {reg}: RSS = {score:.4f}")

    return rss_matrix

def plot_regulon_heatmap(auc_mtx, cell_type_labels, top_n=10,
                          output_png="regulon_heatmap.png"):
    """Plot regulon activity heatmap grouped by cell type."""
    import seaborn as sns

    # Select top variable regulons
    var_regs = auc_mtx.var().nlargest(top_n * 3).index

    # Calculate mean activity per cell type
    auc_with_ct = auc_mtx.copy()
    auc_with_ct['cell_type'] = cell_type_labels.values
    mean_activity = auc_with_ct.groupby('cell_type')[var_regs].mean()

    # Z-score normalize across cell types
    mean_zscore = (mean_activity - mean_activity.mean()) / mean_activity.std()

    # Select top N most variable across cell types
    row_var = mean_zscore.var(axis=0).nlargest(top_n)
    plot_data = mean_zscore[row_var.index].T

    fig, ax = plt.subplots(figsize=(max(8, len(mean_activity.index) * 0.8),
                                     max(6, top_n * 0.4)))
    sns.heatmap(plot_data, cmap='RdBu_r', center=0, ax=ax,
                xticklabels=True, yticklabels=True,
                cbar_kws={'label': 'Z-score'})
    ax.set_title('Regulon Activity by Cell Type')
    ax.set_xlabel('Cell Type')
    ax.set_ylabel('Regulon')
    plt.tight_layout()
    plt.savefig(output_png, dpi=150, bbox_inches='tight')
    print(f"Saved: {output_png}")
```

---

## Phase 3: WGCNA Coexpression Networks

### Network Construction

```r
# R code for WGCNA
library(WGCNA)
options(stringsAsFactors = FALSE)
allowWGCNAThreads(16)

# Load expression data (genes as columns, samples as rows)
datExpr <- read.csv("expression_matrix.csv", row.names = 1)

# QC: Check for outlier samples
sampleTree <- hclust(dist(datExpr), method = "average")
plot(sampleTree, main = "Sample Clustering to Detect Outliers")

# Choose soft-thresholding power
powers <- c(1:20)
sft <- pickSoftThreshold(datExpr, powerVector = powers,
                          networkType = "signed", verbose = 5)

# Plot results
par(mfrow = c(1, 2))
plot(sft$fitIndices[, 1], -sign(sft$fitIndices[, 3]) * sft$fitIndices[, 2],
     xlab = "Soft Threshold (power)", ylab = "Scale Free Topology Model Fit, signed R^2",
     type = "n", main = "Scale independence")
text(sft$fitIndices[, 1], -sign(sft$fitIndices[, 3]) * sft$fitIndices[, 2],
     labels = powers, cex = 0.9, col = "red")
abline(h = 0.85, col = "red")  # R^2 cutoff

plot(sft$fitIndices[, 1], sft$fitIndices[, 5],
     xlab = "Soft Threshold (power)", ylab = "Mean Connectivity",
     type = "n", main = "Mean connectivity")
text(sft$fitIndices[, 1], sft$fitIndices[, 5], labels = powers, cex = 0.9, col = "red")

# Select power where R^2 > 0.85 and connectivity is reasonable
softPower <- sft$powerEstimate
cat("Selected soft-thresholding power:", softPower, "\n")
```

### Soft-Thresholding Power Selection Guide

```
Signed vs Unsigned Networks:
  Signed (recommended): Preserves direction of correlation
    - Positive correlation = co-activation
    - Negative correlation = treated as unrelated
    - Better for biological interpretation
    - Typical power: 12-20

  Unsigned: Uses absolute correlation
    - Positive and negative correlations treated equally
    - Can mix activating and repressive relationships
    - Typical power: 6-12

Power selection rules:
  1. R² of scale-free topology fit > 0.85 (ideally > 0.90)
  2. Mean connectivity should not be too low (> 10)
  3. If R² never reaches 0.85:
     - Try signed hybrid network type
     - Reduce gene count (use more variable genes)
     - Check for batch effects or confounders
  4. For signed networks: typically power = 12 (human) or 18 (mouse)
  5. For unsigned networks: typically power = 6
```

### Module Detection

```r
# Construct network and detect modules
net <- blockwiseModules(datExpr,
  power = softPower,
  networkType = "signed",
  TOMType = "signed",
  minModuleSize = 30,
  reassignThreshold = 0,
  mergeCutHeight = 0.25,
  numericLabels = TRUE,
  pamRespectsDendro = FALSE,
  maxBlockSize = 20000,
  verbose = 3
)

# Module colors
moduleColors <- labels2colors(net$colors)
table(moduleColors)

# Plot dendrogram with module colors
plotDendroAndColors(net$dendrograms[[1]], moduleColors[net$blockGenes[[1]]],
                    "Module colors", dendroLabels = FALSE, hang = 0.03)

# Module eigengenes (first principal component of each module)
MEs <- moduleEigengenes(datExpr, moduleColors)$eigengenes
MEs <- orderMEs(MEs)

# Correlate module eigengenes with traits
if (exists("traitData")) {
  moduleTraitCor <- cor(MEs, traitData, use = "p")
  moduleTraitPvalue <- corPvalueStudent(moduleTraitCor, nrow(datExpr))

  # Heatmap
  textMatrix <- paste(signif(moduleTraitCor, 2), "\n(",
                       signif(moduleTraitPvalue, 1), ")", sep = "")
  dim(textMatrix) <- dim(moduleTraitCor)
  labeledHeatmap(Matrix = moduleTraitCor,
    xLabels = names(traitData), yLabels = names(MEs),
    ySymbols = names(MEs), colorLabels = FALSE,
    colors = blueWhiteRed(50), textMatrix = textMatrix,
    setStdMargins = FALSE, cex.text = 0.5,
    main = "Module-trait relationships")
}

# Hub genes per module (highest module membership)
for (mod in unique(moduleColors)) {
  modGenes <- colnames(datExpr)[moduleColors == mod]
  kME <- cor(datExpr[, modGenes], MEs[, paste0("ME", mod)], use = "p")
  hub_genes <- modGenes[order(-abs(kME))[1:min(10, length(modGenes))]]
  cat("Module", mod, "hub genes:", paste(hub_genes, collapse = ", "), "\n")
}
```

### WGCNA Parameter Reference

| Parameter | Default | Description | Guidance |
|-----------|---------|-------------|----------|
| `power` | Auto | Soft-thresholding power | Select from `pickSoftThreshold` |
| `networkType` | "unsigned" | Network type | "signed" recommended |
| `TOMType` | "unsigned" | TOM calculation type | Match to networkType |
| `minModuleSize` | 30 | Minimum genes per module | 20-50 typical; larger for big datasets |
| `mergeCutHeight` | 0.25 | Module merge threshold | Lower = fewer merges; 0.15-0.35 range |
| `maxBlockSize` | 5000 | Genes per block | Increase for large datasets (up to 20000) |
| `deepSplit` | 2 | Module splitting sensitivity | 0 (fewer, larger) to 4 (more, smaller) |

---

## Phase 4: Coexpression Network Methods

### Pearson/Spearman Correlation Networks

```python
import pandas as pd
import numpy as np
from scipy.stats import spearmanr, pearsonr
from statsmodels.stats.multitest import multipletests

def build_correlation_network(expression_matrix, method='spearman',
                                threshold_padj=0.01, threshold_corr=0.5):
    """Build gene coexpression network from correlation.

    Parameters:
      expression_matrix: genes x samples DataFrame
      method: 'pearson' or 'spearman'
      threshold_padj: significance threshold after BH correction
      threshold_corr: minimum absolute correlation

    Returns: edge list DataFrame
    """
    genes = expression_matrix.index.tolist()
    n_genes = len(genes)

    edges = []
    pvalues = []
    correlations = []

    for i in range(n_genes):
        for j in range(i + 1, n_genes):
            x = expression_matrix.iloc[i].values
            y = expression_matrix.iloc[j].values

            if method == 'spearman':
                corr, pval = spearmanr(x, y)
            else:
                corr, pval = pearsonr(x, y)

            if abs(corr) >= threshold_corr:
                edges.append((genes[i], genes[j]))
                correlations.append(corr)
                pvalues.append(pval)

    if not edges:
        print("No edges pass threshold. Consider lowering threshold_corr.")
        return pd.DataFrame()

    edge_df = pd.DataFrame({
        'gene1': [e[0] for e in edges],
        'gene2': [e[1] for e in edges],
        'correlation': correlations,
        'pvalue': pvalues
    })

    _, edge_df['padj'], _, _ = multipletests(edge_df['pvalue'], method='fdr_bh')
    edge_df = edge_df[edge_df['padj'] < threshold_padj]

    print(f"Network edges: {len(edge_df)}")
    print(f"Unique genes: {len(set(edge_df['gene1']) | set(edge_df['gene2']))}")
    print(f"Positive correlations: {(edge_df['correlation'] > 0).sum()}")
    print(f"Negative correlations: {(edge_df['correlation'] < 0).sum()}")

    return edge_df.sort_values('padj')
```

### ARACNe (Mutual Information Networks)

```python
def aracne_network(expression_matrix, tf_list, n_bootstraps=100,
                    mi_threshold='auto', dpi_tolerance=0.0):
    """ARACNe-style mutual information network inference.

    ARACNe uses mutual information instead of correlation:
      - Captures non-linear relationships
      - Data Processing Inequality (DPI) removes indirect interactions
      - Bootstrap aggregation increases robustness

    Parameters:
      expression_matrix: genes x samples
      tf_list: list of TF gene names (regulators)
      n_bootstraps: number of bootstrap iterations
      mi_threshold: MI significance threshold ('auto' = permutation-based)
      dpi_tolerance: DPI tolerance (0 = strict, higher = more edges)
    """
    from sklearn.feature_selection import mutual_info_regression

    genes = expression_matrix.index.tolist()
    tfs_present = [tf for tf in tf_list if tf in genes]

    all_edges = []

    for boot in range(n_bootstraps):
        # Bootstrap sample
        sample_idx = np.random.choice(expression_matrix.columns,
                                       size=len(expression_matrix.columns),
                                       replace=True)
        boot_expr = expression_matrix[sample_idx]

        for tf in tfs_present:
            tf_values = boot_expr.loc[tf].values.reshape(-1, 1)
            target_genes = [g for g in genes if g != tf]
            target_matrix = boot_expr.loc[target_genes].values.T

            # Calculate MI for each TF-target pair
            mi_values = mutual_info_regression(target_matrix, tf_values.ravel(),
                                                random_state=boot)

            for gene, mi in zip(target_genes, mi_values):
                if mi > 0:
                    all_edges.append({'TF': tf, 'target': gene,
                                       'MI': mi, 'bootstrap': boot})

    edges_df = pd.DataFrame(all_edges)

    # Aggregate across bootstraps
    agg = edges_df.groupby(['TF', 'target']).agg(
        mean_MI=('MI', 'mean'),
        support=('MI', 'count')  # Number of bootstraps where edge appeared
    ).reset_index()

    # Filter by support (edge must appear in > 50% of bootstraps)
    agg = agg[agg['support'] > n_bootstraps * 0.5]

    print(f"ARACNe network edges: {len(agg)}")
    print(f"TFs with targets: {agg['TF'].nunique()}")
    print(f"Unique targets: {agg['target'].nunique()}")

    return agg.sort_values('mean_MI', ascending=False)
```

---

## Phase 5: Differential Network Analysis

```python
def differential_regulon_activity(auc_mtx, condition_labels, alpha=0.05):
    """Compare regulon activity between conditions.

    Identifies regulons with significantly different activity
    in one condition vs another.
    """
    from scipy.stats import mannwhitneyu

    conditions = condition_labels.unique()
    assert len(conditions) == 2

    c1 = condition_labels[condition_labels == conditions[0]].index
    c2 = condition_labels[condition_labels == conditions[1]].index

    results = []
    for regulon in auc_mtx.columns:
        c1_vals = auc_mtx.loc[c1, regulon].values
        c2_vals = auc_mtx.loc[c2, regulon].values

        mean_c1 = c1_vals.mean()
        mean_c2 = c2_vals.mean()
        diff = mean_c2 - mean_c1

        try:
            _, pval = mannwhitneyu(c1_vals, c2_vals, alternative='two-sided')
        except ValueError:
            pval = 1.0

        results.append({
            'regulon': regulon,
            'mean_activity_c1': mean_c1,
            'mean_activity_c2': mean_c2,
            'activity_diff': diff,
            'pvalue': pval
        })

    results_df = pd.DataFrame(results).set_index('regulon')
    _, results_df['padj'], _, _ = multipletests(results_df['pvalue'], method='fdr_bh')
    sig = results_df[results_df['padj'] < alpha].sort_values('padj')

    print(f"Differentially active regulons: {len(sig)}/{len(results_df)}")
    print(f"  More active in {conditions[1]}: {(sig['activity_diff'] > 0).sum()}")
    print(f"  More active in {conditions[0]}: {(sig['activity_diff'] < 0).sum()}")
    return results_df, sig

def compare_network_structure(network1, network2, shared_genes=None):
    """Compare two GRN structures to identify rewired edges.

    network1, network2: DataFrames with columns ['TF', 'target', 'score']
    """
    # Create edge sets
    edges1 = set(zip(network1['TF'], network1['target']))
    edges2 = set(zip(network2['TF'], network2['target']))

    shared = edges1 & edges2
    only_1 = edges1 - edges2
    only_2 = edges2 - edges1

    print(f"Network 1 edges: {len(edges1)}")
    print(f"Network 2 edges: {len(edges2)}")
    print(f"Shared edges: {len(shared)}")
    print(f"Only in network 1: {len(only_1)}")
    print(f"Only in network 2: {len(only_2)}")
    print(f"Jaccard similarity: {len(shared) / len(edges1 | edges2):.3f}")

    # Identify TFs with most rewiring
    all_tfs = set(network1['TF']) | set(network2['TF'])
    tf_rewiring = []
    for tf in all_tfs:
        targets1 = set(network1[network1['TF'] == tf]['target'])
        targets2 = set(network2[network2['TF'] == tf]['target'])
        if len(targets1 | targets2) == 0:
            continue
        jaccard = len(targets1 & targets2) / len(targets1 | targets2)
        tf_rewiring.append({
            'TF': tf,
            'targets_net1': len(targets1),
            'targets_net2': len(targets2),
            'shared_targets': len(targets1 & targets2),
            'jaccard': jaccard,
            'rewiring_score': 1 - jaccard
        })

    rewiring_df = pd.DataFrame(tf_rewiring).sort_values('rewiring_score', ascending=False)
    print(f"\nMost rewired TFs:")
    for _, row in rewiring_df.head(10).iterrows():
        print(f"  {row['TF']}: rewiring={row['rewiring_score']:.3f} "
              f"(net1={row['targets_net1']}, net2={row['targets_net2']}, "
              f"shared={row['shared_targets']})")

    return rewiring_df
```

---

## Phase 6: Perturbation-Based Network Inference

### CellOracle

```python
# CellOracle: GRN inference from scRNA-seq + perturbation/chromatin data

import celloracle as co

def celloracle_grn(adata, base_grn, cluster_column='cell_type'):
    """Infer GRN and simulate perturbations with CellOracle.

    Parameters:
      adata: Scanpy AnnData (preprocessed, with UMAP)
      base_grn: DataFrame with columns ['peak_id', 'gene_short_name']
                From ATAC-seq peak-gene links or motif analysis
      cluster_column: Column in adata.obs for cell type labels
    """
    # Initialize Oracle object
    oracle = co.Oracle()
    oracle.import_anndata_as_raw_count(
        adata=adata,
        cluster_column_name=cluster_column,
        embedding_name='X_umap'
    )

    # Add base GRN
    oracle.import_TF_data(TF_info_matrix=base_grn)

    # Fit GRN for each cluster
    oracle.perform_PCA()
    oracle.knn_imputation(k=30)

    # Get GRN links
    links = oracle.get_links(cluster_name_for_GRN_unit=cluster_column,
                              alpha=10, verbose_level=0)

    # Filter and visualize
    links.filter_links(p=0.001, weight="coef_abs", threshold_number=2000)

    # Simulate TF knockout
    oracle.simulate_shift(
        perturb_condition={"MYC": 0.0},  # Knock out MYC
        n_propagation=3
    )

    # Visualize perturbation effect
    oracle.plot_simulation_result()

    return oracle, links

# Dictys: dynamic GRN inference from perturbation time-series
# (Specialized for time-course perturbation data)
# Run as command-line tool:
# dictys network --expression expr.h5ad --atac atac.h5ad --output grn_output/
```

---

## Phase 7: SCENIC+ (Chromatin-Aware GRN)

```python
# SCENIC+: integrates scRNA-seq + scATAC-seq for enhancer-driven GRNs

import scenicplus

def run_scenic_plus(rna_adata, atac_adata, output_dir="scenicplus_output/"):
    """Run SCENIC+ for enhancer-regulatory network inference.

    Requirements:
      - Paired scRNA-seq and scATAC-seq (multiome or co-assay)
      - Or integrated unpaired datasets with shared cell labels
      - cisTarget ranking databases (same as pySCENIC)
      - DEM (Differentially Enriched Motif) databases

    SCENIC+ workflow:
      1. Identify candidate enhancers from scATAC-seq peaks
      2. Link enhancers to target genes (correlation-based)
      3. Identify TF binding motifs in enhancers (cisTarget)
      4. Build eGRN (enhancer Gene Regulatory Network)
      5. Score eGRN activity per cell
    """
    from scenicplus.scenicplus_class import SCENICPLUS
    from scenicplus.wrappers.run_scenicplus import run_scenicplus as run_sp

    scplus_obj = SCENICPLUS(
        rna_anndata=rna_adata,
        atac_anndata=atac_adata
    )

    run_sp(
        scplus_obj,
        variable=['cell_type'],
        species='hsapiens',  # or 'mmusculus'
        assembly='hg38',     # or 'mm10'
        tf_file='utoronto_human_tfs_v_1.01.txt',
        save_path=output_dir,
        biomart_host='http://www.ensembl.org',
        upstream=[1000, 150000],
        downstream=[1000, 150000],
        calculate_TF_eGRN_correlation=True,
        calculate_DEGs_DARs=True,
        export_to_loom_file=True,
        export_to_UCSC_file=True,
        n_cpu=16
    )

    return scplus_obj
```

```
SCENIC+ vs pySCENIC comparison:

  pySCENIC:
    - Input: scRNA-seq only
    - Regulon definition: TF + target genes (expression-based)
    - Motif enrichment: In gene promoters/flanking regions
    - No enhancer information

  SCENIC+:
    - Input: scRNA-seq + scATAC-seq (multiome preferred)
    - eRegulon definition: TF + enhancers + target genes
    - Motif enrichment: In actual accessible chromatin regions
    - Captures distal enhancer-gene regulatory relationships
    - More biologically accurate but requires multiome data
    - Higher computational cost
```

---

## Evidence Grading Framework

| Tier | Criteria | Confidence |
|------|----------|------------|
| **T1** | Regulon validated by cisTarget motif enrichment + ChIP-seq binding evidence + perturbation data confirming causality | High |
| **T2** | Regulon discovered by SCENIC with strong motif support, cell-type-specific activity (RSS > 0.8), validated targets in literature | Medium-High |
| **T3** | Co-expression module (WGCNA) with trait correlation, hub genes functionally relevant, but no motif/binding validation | Medium |
| **T4** | Correlation-only edge, no motif support, single-method detection | Low |

---

## Boundary Rules

```
DO:
- Run pySCENIC pipeline (GRNBoost2 + cisTarget + AUCell)
- Build WGCNA coexpression networks with module detection
- Calculate regulon activity scores and specificity
- Visualize regulon activity on UMAP embeddings
- Compare regulon activity across conditions
- Construct correlation and mutual information networks
- Guide CellOracle and SCENIC+ analyses
- Perform differential network analysis
- Identify hub genes and key regulators

DO NOT:
- Perform single-cell QC, clustering, or cell type annotation (use single-cell-analysis)
- Run differential gene expression (use transcriptomics)
- Deep pathway enrichment on regulon gene lists (use gene-enrichment)
- ChIP-seq peak calling or analysis (use chipseq-analysis)
- ATAC-seq processing for SCENIC+ input (use atac-seq-analysis)
- Protein-protein interaction networks (use systems-biology)
```

## Completeness Checklist

- [ ] GRN inference method selected based on available data
- [ ] Expression matrix prepared (filtered, normalized appropriately)
- [ ] TF list curated and matched to expression gene names
- [ ] GRNBoost2 adjacencies computed (or alternative method)
- [ ] cisTarget motif pruning completed with appropriate databases
- [ ] AUCell regulon activity scored per cell
- [ ] Regulon specificity scores calculated per cell type (RSS)
- [ ] Key regulons visualized on UMAP embedding
- [ ] Differential regulon activity tested between conditions
- [ ] WGCNA modules detected and correlated with traits (if bulk data)
- [ ] Hub genes identified per module/regulon
- [ ] Network comparison performed (if multiple conditions)
- [ ] Evidence tier assigned to all major regulon findings
