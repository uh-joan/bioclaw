# pySCENIC & Gene Regulatory Network Recipes

Python and R code templates for gene regulatory network inference, regulon activity scoring, and network visualization using pySCENIC, WGCNA, and ARACNe.

Cross-skill routing: use `single-cell-analysis` for upstream scRNA-seq processing, `gene-enrichment` for pathway enrichment of regulon target genes.

---

## 1. GRNBoost2 Adjacency Matrix Computation (Dask Distributed)

Infer gene regulatory network using gradient boosting on expression data.

```python
import pandas as pd
import numpy as np
from arboreto.algo import grnboost2
from arboreto.utils import load_tf_names
from distributed import Client, LocalCluster

def run_grnboost2(expression_matrix, tf_names_file, n_workers=4,
                   seed=42, output_file="adjacencies.tsv"):
    """Run GRNBoost2 to infer TF-target gene regulatory links.

    Parameters
    ----------
    expression_matrix : pd.DataFrame
        Expression matrix (cells x genes). Use raw or log-normalized counts.
        Recommended: 2000-5000 HVGs plus all TFs.
    tf_names_file : str
        Path to file with transcription factor names (one per line).
        Sources:
        - Human: https://github.com/aertslab/pySCENIC/tree/master/resources
        - Lambert et al. 2018 curated TF list
    n_workers : int
        Number of Dask workers for parallel computation.
    seed : int
        Random seed for reproducibility.
    output_file : str
        Path to save adjacency table.

    Returns
    -------
    pd.DataFrame with columns: TF, target, importance.
    """
    # Load TF names
    tf_names = load_tf_names(tf_names_file)
    print(f"Transcription factors: {len(tf_names)}")

    # Filter to TFs present in expression matrix
    tf_in_data = [tf for tf in tf_names if tf in expression_matrix.columns]
    print(f"TFs in expression data: {len(tf_in_data)}/{len(tf_names)}")

    # Start Dask cluster
    cluster = LocalCluster(n_workers=n_workers, threads_per_worker=1,
                            memory_limit="4GB")
    client = Client(cluster)
    print(f"Dask dashboard: {client.dashboard_link}")

    try:
        # Run GRNBoost2
        adjacencies = grnboost2(
            expression_data=expression_matrix,
            tf_names=tf_in_data,
            seed=seed,
            verbose=True,
            client_or_address=client,
        )

        # Save
        adjacencies.to_csv(output_file, sep="\t", index=False)

        print(f"\nGRNBoost2 results:")
        print(f"  Total TF-target links: {len(adjacencies)}")
        print(f"  Unique TFs: {adjacencies['TF'].nunique()}")
        print(f"  Unique targets: {adjacencies['target'].nunique()}")
        print(f"  Mean importance: {adjacencies['importance'].mean():.4f}")
        print(f"  Max importance: {adjacencies['importance'].max():.4f}")

        # Top regulatory links
        print(f"\nTop 20 TF-target links by importance:")
        print(adjacencies.nlargest(20, "importance").to_string(index=False))

    finally:
        client.close()
        cluster.close()

    return adjacencies

# Usage
import scanpy as sc
adata = sc.read_h5ad("processed_scrnaseq.h5ad")

# Use log-normalized expression matrix
expr_df = pd.DataFrame(
    adata.raw.X.toarray() if hasattr(adata.raw.X, "toarray") else adata.raw.X,
    index=adata.obs_names,
    columns=adata.raw.var_names,
)
adjacencies = run_grnboost2(expr_df, "hs_hgnc_tfs.txt", n_workers=4)
```

**Key parameters**: GRNBoost2 uses gradient boosting (not correlation) to infer regulatory links, making it more robust to indirect associations. Use all cells (not downsampled) for best results. Runtime scales with cells x genes x TFs; expect 30-60 min for 10k cells.

---

## 2. cisTarget Regulon Pruning with Ranking Databases

Prune GRN adjacencies using cis-regulatory motif enrichment.

```python
from pyscenic.prune import prune2df, df2regulons
from ctxcore.rnkdb import FeatherRankingDatabase
import pandas as pd
import os

def run_ctx_pruning(adjacencies, ranking_db_paths, motif_annotations_file,
                     output_file="regulons.csv"):
    """Prune TF-target links using cisTarget motif enrichment.

    Parameters
    ----------
    adjacencies : pd.DataFrame
        GRNBoost2 output with TF, target, importance columns.
    ranking_db_paths : list of str
        Paths to ranking database files (.feather format).
        Download from: https://resources.aertslab.org/cistarget/
        Human hg38:
        - hg38_500bp_up_100bp_down_full_tx_v10_clust.genes_vs_motifs.rankings.feather
        - hg38_10kbp_up_10kbp_down_full_tx_v10_clust.genes_vs_motifs.rankings.feather
    motif_annotations_file : str
        Path to motif-to-TF annotation file.
        e.g., motifs-v10nr_clust-nr.hgnc-m0.001-o0.0.tbl

    Returns
    -------
    list of pyscenic Regulon objects.
    """
    # Load ranking databases
    dbs = [FeatherRankingDatabase(path) for path in ranking_db_paths]
    print(f"Loaded {len(dbs)} ranking databases:")
    for db in dbs:
        print(f"  {db.name}: {db.total_genes} genes")

    # Load motif annotations
    motif_annotations = pd.read_csv(motif_annotations_file, sep="\t")
    print(f"Motif annotations: {len(motif_annotations)} entries")

    # Prune adjacencies using cisTarget
    df_motifs = prune2df(
        dbs,
        adjacencies,
        motif_annotations_file,
        num_workers=4,
        auc_threshold=0.05,
        nes_threshold=3.0,
        rank_threshold=5000,
    )

    # Convert to regulons
    regulons = df2regulons(df_motifs)

    print(f"\ncisTarget pruning results:")
    print(f"  Input TF-target links: {len(adjacencies)}")
    print(f"  Regulons after pruning: {len(regulons)}")

    # Regulon summary
    regulon_stats = []
    for reg in regulons:
        regulon_stats.append({
            "TF": reg.name.split("(")[0],
            "n_targets": len(reg.genes),
            "regulon_name": reg.name,
        })
    stats_df = pd.DataFrame(regulon_stats).sort_values("n_targets", ascending=False)
    print(f"\nTop regulons by target count:")
    print(stats_df.head(20).to_string(index=False))

    # Save regulons
    stats_df.to_csv(output_file, index=False)

    return regulons

# Usage
adjacencies = pd.read_csv("adjacencies.tsv", sep="\t")
ranking_dbs = [
    "hg38_500bp_up_100bp_down_full_tx_v10_clust.genes_vs_motifs.rankings.feather",
    "hg38_10kbp_up_10kbp_down_full_tx_v10_clust.genes_vs_motifs.rankings.feather",
]
regulons = run_ctx_pruning(adjacencies, ranking_dbs,
                            "motifs-v10nr_clust-nr.hgnc-m0.001-o0.0.tbl")
```

**Key parameters**: `nes_threshold=3.0` is the standard cutoff for enriched motifs. `rank_threshold=5000` limits to top-ranked genes per motif. The 500bp database captures proximal promoter motifs; the 10kb database captures distal enhancer motifs.

---

## 3. AUCell Regulon Activity Scoring Per Cell

Score each cell for the activity of each regulon.

```python
from pyscenic.aucell import aucell
import scanpy as sc
import pandas as pd
import numpy as np

def run_aucell(expression_matrix, regulons, auc_threshold=0.05,
               num_workers=4):
    """Score regulon activity per cell using AUCell.

    Parameters
    ----------
    expression_matrix : pd.DataFrame
        Expression matrix (cells x genes).
    regulons : list
        List of regulon objects from cisTarget pruning.
    auc_threshold : float
        Fraction of ranked genes to use for AUC calculation.
        0.05 = top 5% of genes. Lower = more stringent.
    num_workers : int
        Parallel workers.

    Returns
    -------
    pd.DataFrame (cells x regulons) with AUC scores.
    """
    auc_matrix = aucell(
        expression_matrix,
        regulons,
        auc_threshold=auc_threshold,
        num_workers=num_workers,
    )

    print(f"AUCell results:")
    print(f"  Cells: {auc_matrix.shape[0]}")
    print(f"  Regulons: {auc_matrix.shape[1]}")

    # Summary statistics per regulon
    stats = pd.DataFrame({
        "regulon": auc_matrix.columns,
        "mean_auc": auc_matrix.mean().values,
        "std_auc": auc_matrix.std().values,
        "max_auc": auc_matrix.max().values,
        "pct_active": (auc_matrix > auc_matrix.mean()).mean().values * 100,
    }).sort_values("std_auc", ascending=False)

    print(f"\nMost variable regulons (by std):")
    print(stats.head(15).to_string(index=False))

    return auc_matrix

# Usage
import scanpy as sc
adata = sc.read_h5ad("processed_scrnaseq.h5ad")
expr_df = pd.DataFrame(
    adata.raw.X.toarray() if hasattr(adata.raw.X, "toarray") else adata.raw.X,
    index=adata.obs_names,
    columns=adata.raw.var_names,
)

auc_mtx = run_aucell(expr_df, regulons)

# Store in AnnData
adata.obsm["X_aucell"] = auc_mtx.values
for col in auc_mtx.columns:
    adata.obs[f"regulon_{col}"] = auc_mtx[col].values

# Visualize top regulons on UMAP
import matplotlib.pyplot as plt
top_regulons = auc_mtx.std().nlargest(6).index.tolist()
sc.pl.umap(adata, color=[f"regulon_{r}" for r in top_regulons], ncols=3,
           cmap="viridis", frameon=False)
plt.savefig("regulon_activity_umap.png", dpi=150, bbox_inches="tight")
```

**Expected output**: AUC matrix (cells x regulons) where higher scores indicate stronger regulon activity. High-variance regulons are cell-type-specific transcriptional programs.

---

## 4. Full pySCENIC CLI Pipeline (grn -> ctx -> aucell)

Run the complete pySCENIC pipeline from command line.

```bash
# ---- Step 1: GRN inference (GRNBoost2) ----
pyscenic grn \
    expression_matrix.loom \
    hs_hgnc_tfs.txt \
    --method grnboost2 \
    --num_workers 8 \
    --seed 42 \
    --output adjacencies.tsv

# ---- Step 2: cisTarget motif pruning ----
pyscenic ctx \
    adjacencies.tsv \
    hg38_500bp_up_100bp_down_full_tx_v10_clust.genes_vs_motifs.rankings.feather \
    hg38_10kbp_up_10kbp_down_full_tx_v10_clust.genes_vs_motifs.rankings.feather \
    --annotations_fname motifs-v10nr_clust-nr.hgnc-m0.001-o0.0.tbl \
    --expression_mtx_fname expression_matrix.loom \
    --mode "dask_multiprocessing" \
    --num_workers 8 \
    --output regulons.csv

# ---- Step 3: AUCell regulon activity scoring ----
pyscenic aucell \
    expression_matrix.loom \
    regulons.csv \
    --output aucell_matrix.loom \
    --num_workers 8 \
    --auc_threshold 0.05
```

```python
# ---- Post-processing: integrate with scanpy ----
import loompy
import scanpy as sc
import pandas as pd

def load_scenic_results(aucell_loom, adata):
    """Load pySCENIC CLI output into AnnData.

    Parameters
    ----------
    aucell_loom : str
        Path to AUCell output loom file.
    adata : AnnData
        Preprocessed AnnData to integrate with.

    Returns
    -------
    AnnData with regulon scores in obsm.
    """
    with loompy.connect(aucell_loom, mode="r") as ds:
        auc_matrix = pd.DataFrame(
            ds[:, :].T,
            index=ds.ca["CellID"],
            columns=ds.ra["Regulons"],
        )

    # Align cells
    common_cells = adata.obs_names.intersection(auc_matrix.index)
    auc_aligned = auc_matrix.loc[common_cells]

    adata_subset = adata[common_cells].copy()
    adata_subset.obsm["X_aucell"] = auc_aligned.values

    # Add individual regulon scores to obs
    for reg in auc_aligned.columns:
        clean_name = reg.replace("(", "_").replace(")", "").replace("+", "pos").replace("-", "neg")
        adata_subset.obs[f"regulon_{clean_name}"] = auc_aligned[reg].values

    print(f"Loaded {auc_aligned.shape[1]} regulons for {len(common_cells)} cells")
    return adata_subset

# Usage
adata = sc.read_h5ad("processed.h5ad")
adata = load_scenic_results("aucell_matrix.loom", adata)
```

**Expected output**: Complete regulon analysis from raw expression to per-cell activity scores. CLI pipeline is faster for large datasets. Typical runtime: 1-4 hours for 50k cells.

---

## 5. SCENIC+ Chromatin-Informed Regulon Discovery

Integrate scATAC-seq with scRNA-seq for enhanced regulon detection.

```python
import scenicplus
from scenicplus.scenicplus_class import SCENICPLUS
import pycisTopic

def run_scenic_plus(rna_adata, atac_adata, genome="hg38"):
    """Run SCENIC+ for chromatin-informed regulon discovery.

    Parameters
    ----------
    rna_adata : AnnData
        scRNA-seq AnnData (log-normalized).
    atac_adata : AnnData
        scATAC-seq AnnData (fragment counts or peak accessibility).
    genome : str
        Genome assembly ('hg38', 'mm10').

    Returns
    -------
    SCENICPLUS object with eRegulons.
    """
    # Step 1: Topic modeling on ATAC-seq (cisTopic)
    cistopic_obj = pycisTopic.cistopic_class.create_cistopic_object(atac_adata)
    models = pycisTopic.lda_models.run_cgs_models(
        cistopic_obj,
        n_topics=[10, 20, 30, 40, 50],
        n_cpu=4,
        n_iter=300,
        random_state=42,
    )
    # Select best model
    cistopic_obj = pycisTopic.lda_models.evaluate_models(
        models, return_model=True
    )

    # Step 2: Differentially accessible regions (DARs)
    imputed_acc = pycisTopic.diff_features.impute_accessibility(
        cistopic_obj, scale_factor=10**6
    )

    # Step 3: Build SCENIC+ object
    scplus = SCENICPLUS(
        rna_anndata=rna_adata,
        atac_anndata=atac_adata,
        cistopic_obj=cistopic_obj,
    )

    # Step 4: Run SCENIC+ pipeline
    scplus.run_scenicplus(
        biomart_host="http://www.ensembl.org",
        species="hsapiens",
        assembly=genome,
        tf_file="utoronto_human_tfs_v_1.01.txt",
        search_space_upstream=150_000,
        search_space_downstream=150_000,
        n_cpu=8,
    )

    print(f"SCENIC+ results:")
    print(f"  eRegulons: {len(scplus.uns['eRegulon_metadata'])}")
    print(f"  TFs with eRegulons: {scplus.uns['eRegulon_metadata']['TF'].nunique()}")

    return scplus

# NOTE: SCENIC+ is computationally intensive and requires paired
# scRNA-seq + scATAC-seq data. Simplified workflow shown above.
# Full documentation: https://scenicplus.readthedocs.io/
```

**Key parameters**: SCENIC+ requires paired (multiome) or integrated scRNA-seq + scATAC-seq data. eRegulons are regulons with both motif enrichment (from pySCENIC) and chromatin accessibility support (from scATAC-seq), making them higher confidence than standard regulons.

---

## 6. Regulon Specificity Score (RSS) Calculation

Quantify how cell-type-specific each regulon is.

```python
import pandas as pd
import numpy as np
from scipy.stats import entropy

def calculate_rss(auc_matrix, cell_labels, normalize=True):
    """Calculate Regulon Specificity Score for each cell type.

    Parameters
    ----------
    auc_matrix : pd.DataFrame
        AUCell matrix (cells x regulons).
    cell_labels : pd.Series
        Cell type labels aligned with auc_matrix index.
    normalize : bool
        Normalize RSS to [0, 1] range.

    Returns
    -------
    pd.DataFrame (cell_types x regulons) with RSS values.
    """
    cell_types = cell_labels.unique()
    regulons = auc_matrix.columns

    # Mean AUC per cell type
    mean_auc = pd.DataFrame(index=cell_types, columns=regulons, dtype=float)
    for ct in cell_types:
        mask = cell_labels == ct
        mean_auc.loc[ct] = auc_matrix.loc[mask].mean()

    # RSS = 1 - (entropy of normalized mean AUC) / log(n_cell_types)
    rss = pd.DataFrame(index=cell_types, columns=regulons, dtype=float)
    max_entropy = np.log(len(cell_types))

    for reg in regulons:
        # Normalize to probability distribution
        values = mean_auc[reg].values.astype(float)
        values = values - values.min()
        total = values.sum()
        if total == 0:
            rss[reg] = 0
            continue
        probs = values / total

        # Jensen-Shannon divergence from uniform
        uniform = np.ones(len(cell_types)) / len(cell_types)
        for i, ct in enumerate(cell_types):
            # RSS for this cell type = specificity of regulon for this cell type
            ct_dist = np.zeros(len(cell_types))
            ct_dist[i] = 1.0
            m = (probs + ct_dist) / 2
            jsd = (entropy(probs, m) + entropy(ct_dist, m)) / 2
            rss.loc[ct, reg] = 1 - np.sqrt(jsd) if normalize else jsd

    # Top specific regulons per cell type
    print("Top 5 specific regulons per cell type (by RSS):")
    for ct in cell_types:
        top = rss.loc[ct].nlargest(5)
        print(f"\n  {ct}:")
        for reg, score in top.items():
            print(f"    {reg}: RSS={score:.4f}")

    return rss

# Usage
rss_scores = calculate_rss(auc_mtx, adata.obs["cell_type"])

# Heatmap of top specific regulons
import matplotlib.pyplot as plt
import seaborn as sns

# Select top 5 regulons per cell type
top_regulons = set()
for ct in rss_scores.index:
    top_regulons.update(rss_scores.loc[ct].nlargest(5).index.tolist())
top_regulons = sorted(top_regulons)

fig, ax = plt.subplots(figsize=(max(10, len(top_regulons) * 0.4),
                                max(5, len(rss_scores) * 0.5)))
sns.heatmap(rss_scores[top_regulons], cmap="YlOrRd", annot=False, ax=ax)
ax.set_title("Regulon Specificity Score (RSS)")
plt.tight_layout()
plt.savefig("rss_heatmap.png", dpi=150, bbox_inches="tight")
```

**Expected output**: RSS matrix showing which regulons are specific to which cell types. RSS close to 1 = highly specific (active in one cell type); RSS close to 0 = ubiquitous (active in all cell types).

---

## 7. Regulon Heatmap with Cell Type Annotation

```python
import scanpy as sc
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def regulon_heatmap(auc_matrix, cell_labels, top_n_per_type=3,
                     method="mean", figsize=None):
    """Create annotated heatmap of regulon activity across cell types.

    Parameters
    ----------
    auc_matrix : pd.DataFrame
        AUCell matrix (cells x regulons).
    cell_labels : pd.Series
        Cell type labels.
    top_n_per_type : int
        Top regulons per cell type to show.
    method : str
        Aggregation method: 'mean' or 'zscore'.

    Returns
    -------
    matplotlib Figure.
    """
    cell_types = sorted(cell_labels.unique())

    # Aggregate per cell type
    agg = pd.DataFrame(index=cell_types, columns=auc_matrix.columns, dtype=float)
    for ct in cell_types:
        mask = cell_labels == ct
        agg.loc[ct] = auc_matrix.loc[mask].mean()

    # Z-score across cell types
    if method == "zscore":
        agg = (agg - agg.mean()) / agg.std()

    # Select top regulons per cell type
    top_regulons = set()
    for ct in cell_types:
        top = agg.loc[ct].nlargest(top_n_per_type).index.tolist()
        top_regulons.update(top)
    top_regulons = sorted(top_regulons)

    # Plot
    plot_data = agg[top_regulons]
    if figsize is None:
        figsize = (max(10, len(top_regulons) * 0.5), max(4, len(cell_types) * 0.5))

    g = sns.clustermap(
        plot_data,
        cmap="RdBu_r" if method == "zscore" else "YlOrRd",
        center=0 if method == "zscore" else None,
        figsize=figsize,
        xticklabels=True,
        yticklabels=True,
        row_cluster=True,
        col_cluster=True,
        linewidths=0.5,
        linecolor="gray",
        dendrogram_ratio=0.1,
    )
    g.ax_heatmap.set_xlabel("Regulons")
    g.ax_heatmap.set_ylabel("Cell Types")
    plt.suptitle(f"Regulon Activity ({method})", y=1.02)
    g.savefig("regulon_heatmap.png", dpi=150, bbox_inches="tight")
    plt.close()

    return g

# Usage
regulon_heatmap(auc_mtx, adata.obs["cell_type"], top_n_per_type=5, method="zscore")
```

**Expected output**: Clustered heatmap showing regulon activity patterns across cell types. Z-scored view highlights cell-type-specific regulation regardless of absolute activity level.

---

## 8. WGCNA: pickSoftThreshold, blockwiseModules, Module Eigengenes (R)

Weighted Gene Co-expression Network Analysis for bulk or pseudo-bulk expression.

```R
library(WGCNA)
options(stringsAsFactors = FALSE)
enableWGCNAThreads(nThreads = 4)

# ---- Load expression data ----
# Rows = samples, columns = genes (WGCNA convention)
expr_data <- read.csv("expression_matrix.csv", row.names = 1)
expr_data <- t(expr_data)  # If genes x samples, transpose
cat("Samples:", nrow(expr_data), "Genes:", ncol(expr_data), "\n")

# ---- Filter low-variance genes ----
gene_var <- apply(expr_data, 2, var)
keep <- gene_var > quantile(gene_var, 0.25)
expr_data <- expr_data[, keep]
cat("Genes after variance filter:", ncol(expr_data), "\n")

# ---- 1. Pick soft threshold ----
powers <- c(seq(1, 10, by = 1), seq(12, 30, by = 2))
sft <- pickSoftThreshold(
    expr_data,
    powerVector    = powers,
    networkType    = "signed",     # "signed", "unsigned", or "signed hybrid"
    verbose        = 3,
    RssquaredCut   = 0.80          # Target R^2 for scale-free fit
)

# Plot
par(mfrow = c(1, 2))
plot(sft$fitIndices[, 1], -sign(sft$fitIndices[, 3]) * sft$fitIndices[, 2],
     xlab = "Soft Threshold (power)", ylab = "Scale Free Topology Model Fit (R^2)",
     main = "Scale independence", pch = 20, col = "red")
abline(h = 0.80, col = "blue")
text(sft$fitIndices[, 1], -sign(sft$fitIndices[, 3]) * sft$fitIndices[, 2],
     labels = powers, cex = 0.7)

plot(sft$fitIndices[, 1], sft$fitIndices[, 5],
     xlab = "Soft Threshold (power)", ylab = "Mean Connectivity",
     main = "Mean connectivity", pch = 20, col = "red")
text(sft$fitIndices[, 1], sft$fitIndices[, 5], labels = powers, cex = 0.7)

soft_power <- sft$powerEstimate
cat("Selected soft threshold power:", soft_power, "\n")

# ---- 2. Build network and detect modules ----
net <- blockwiseModules(
    expr_data,
    power                = soft_power,
    networkType          = "signed",
    TOMType              = "signed",
    minModuleSize        = 30,       # Min genes per module
    reassignThreshold    = 0,
    mergeCutHeight       = 0.25,     # Merge modules with correlation > 0.75
    numericLabels        = TRUE,
    pamRespectsDendro    = FALSE,
    saveTOMs             = TRUE,
    saveTOMFileBase       = "TOM",
    verbose              = 3,
    maxBlockSize         = 20000     # Increase for more genes (needs more RAM)
)

# Module assignments
module_colors <- labels2colors(net$colors)
cat("Modules detected:", length(unique(module_colors)), "\n")
cat("Module sizes:\n")
print(table(module_colors))

# ---- 3. Module eigengenes ----
MEs <- net$MEs
colnames(MEs) <- paste0("ME", labels2colors(as.numeric(gsub("ME", "", colnames(MEs)))))

# Plot dendrogram with module colors
plotDendroAndColors(
    net$dendrograms[[1]],
    module_colors[net$blockGenes[[1]]],
    "Module colors",
    main = "Gene dendrogram and module colors",
    dendroLabels = FALSE,
    hang = 0.03
)

# Save results
gene_modules <- data.frame(
    gene = colnames(expr_data),
    module_color = module_colors,
    module_number = net$colors
)
write.csv(gene_modules, "wgcna_gene_modules.csv", row.names = FALSE)
write.csv(MEs, "wgcna_module_eigengenes.csv")
```

**Key parameters**: `power` (soft threshold) ensures scale-free network topology -- pick the lowest power where R^2 > 0.8. `minModuleSize=30` prevents tiny noisy modules. `mergeCutHeight=0.25` merges highly correlated modules (lower = more merging). Use `networkType="signed"` to distinguish up- from down-regulation.

---

## 9. Module-Trait Correlation Analysis (WGCNA)

Correlate gene modules with clinical or experimental traits.

```R
library(WGCNA)

# ---- Load module eigengenes and trait data ----
MEs <- read.csv("wgcna_module_eigengenes.csv", row.names = 1)
traits <- read.csv("clinical_traits.csv", row.names = 1)

# Align samples
common <- intersect(rownames(MEs), rownames(traits))
MEs <- MEs[common, ]
traits <- traits[common, ]

# Encode categorical traits as numeric
for (col in colnames(traits)) {
    if (is.character(traits[, col]) || is.factor(traits[, col])) {
        traits[, col] <- as.numeric(as.factor(traits[, col]))
    }
}

# ---- Correlate modules with traits ----
module_trait_cor <- cor(MEs, traits, use = "pairwise.complete.obs")
module_trait_pval <- corPvalueStudent(module_trait_cor, nrow(MEs))

# ---- Heatmap ----
text_matrix <- paste0(
    signif(module_trait_cor, 2), "\n(",
    signif(module_trait_pval, 1), ")"
)
dim(text_matrix) <- dim(module_trait_cor)

par(mar = c(6, 10, 3, 3))
labeledHeatmap(
    Matrix        = module_trait_cor,
    xLabels       = colnames(traits),
    yLabels       = colnames(MEs),
    ySymbols      = colnames(MEs),
    colorLabels   = FALSE,
    colors        = blueWhiteRed(50),
    textMatrix    = text_matrix,
    setStdMargins = FALSE,
    cex.text      = 0.5,
    zlim          = c(-1, 1),
    main          = "Module-Trait Relationships"
)

# ---- Gene significance and module membership ----
# For a specific trait of interest
trait_of_interest <- "disease_score"
gene_modules <- read.csv("wgcna_gene_modules.csv")

# Gene significance = correlation of gene expression with trait
GS <- as.data.frame(cor(expr_data, traits[, trait_of_interest], use = "p"))
colnames(GS) <- "GS"
GS$p_GS <- corPvalueStudent(GS$GS, nrow(expr_data))

# Module membership = correlation of gene expression with module eigengene
for (mod in colnames(MEs)) {
    gene_modules[[paste0("MM_", mod)]] <- cor(expr_data, MEs[, mod], use = "p")[, 1]
}

# Hub genes: high module membership AND high gene significance
cat("\nHub genes (top GS in each significant module):\n")
sig_modules <- colnames(module_trait_cor)[apply(module_trait_pval, 2, function(x) any(x < 0.05))]
for (mod_color in unique(gene_modules$module_color)) {
    mod_genes <- gene_modules[gene_modules$module_color == mod_color, ]
    mm_col <- paste0("MM_ME", mod_color)
    if (mm_col %in% colnames(mod_genes)) {
        top <- mod_genes[order(-abs(mod_genes[[mm_col]])), ][1:5, ]
        cat(sprintf("  %s module: %s\n", mod_color,
            paste(top$gene, collapse = ", ")))
    }
}

write.csv(gene_modules, "wgcna_gene_modules_with_MM.csv", row.names = FALSE)
```

**Expected output**: Heatmap showing correlations between module eigengenes and traits. Significant module-trait pairs (p < 0.05) indicate biological pathways associated with the trait. Hub genes (high module membership + high gene significance) are key drivers.

---

## 10. ARACNe-AP Mutual Information Network Inference

Information-theoretic network inference based on mutual information.

```bash
# ---- ARACNe-AP (Java, command-line) ----
# Download: https://github.com/califano-lab/ARACNe-AP

# Step 1: Calculate MI threshold
java -Xmx4G -jar aracne.jar \
    --expfile expression_matrix.txt \
    --tfs tf_list.txt \
    --output aracne_output/ \
    --calculateThreshold \
    --pvalue 1e-8 \
    --seed 1

# Step 2: Run bootstraps (100 recommended)
for i in $(seq 1 100); do
    java -Xmx4G -jar aracne.jar \
        --expfile expression_matrix.txt \
        --tfs tf_list.txt \
        --output aracne_output/ \
        --pvalue 1e-8 \
        --seed $i
done

# Step 3: Consolidate
java -Xmx4G -jar aracne.jar \
    --expfile expression_matrix.txt \
    --tfs tf_list.txt \
    --output aracne_output/ \
    --consolidate
```

```python
import pandas as pd
import numpy as np

def parse_aracne_output(network_file, min_mi=0):
    """Parse ARACNe-AP consolidated network.

    Parameters
    ----------
    network_file : str
        Path to ARACNe consolidated network file.
    min_mi : float
        Minimum mutual information score to retain.

    Returns
    -------
    pd.DataFrame with TF, target, MI columns.
    """
    edges = pd.read_csv(network_file, sep="\t", comment="#",
                         names=["TF", "target", "MI", "pvalue"])
    edges = edges[edges["MI"] > min_mi]

    print(f"ARACNe network:")
    print(f"  Total edges: {len(edges)}")
    print(f"  Unique TFs: {edges['TF'].nunique()}")
    print(f"  Unique targets: {edges['target'].nunique()}")
    print(f"  Mean MI: {edges['MI'].mean():.4f}")

    # TF hub scores
    tf_degree = edges.groupby("TF").size().sort_values(ascending=False)
    print(f"\nTop TF hubs (by degree):")
    print(tf_degree.head(20).to_string())

    return edges

# Usage
network = parse_aracne_output("aracne_output/network.txt")
```

**Key parameters**: `--pvalue 1e-8` controls the MI significance threshold. Lower p-value = more stringent (fewer but higher-confidence edges). 100 bootstraps is standard for robust network estimation. ARACNe applies the Data Processing Inequality to remove indirect interactions, producing sparser, more accurate networks than correlation-based methods.

---

## 11. Network Visualization with igraph/networkx

Visualize gene regulatory networks.

```python
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def visualize_grn(edges_df, tf_col="TF", target_col="target",
                   weight_col="importance", top_n_tfs=20,
                   min_targets=5, layout="spring"):
    """Visualize a gene regulatory network.

    Parameters
    ----------
    edges_df : pd.DataFrame
        Edge list with TF, target, and weight columns.
    top_n_tfs : int
        Show only top N TFs by degree.
    min_targets : int
        Minimum targets for a TF to be included.
    layout : str
        'spring', 'kamada_kawai', 'circular', or 'shell'.

    Returns
    -------
    networkx.DiGraph.
    """
    # Filter to top TFs
    tf_degree = edges_df.groupby(tf_col).size()
    tf_degree = tf_degree[tf_degree >= min_targets].nlargest(top_n_tfs)
    top_tfs = tf_degree.index.tolist()

    filtered = edges_df[edges_df[tf_col].isin(top_tfs)]

    # Build directed graph
    G = nx.DiGraph()
    for _, row in filtered.iterrows():
        G.add_edge(row[tf_col], row[target_col],
                   weight=row.get(weight_col, 1))

    # Node properties
    node_types = {}
    for node in G.nodes():
        if node in top_tfs:
            node_types[node] = "TF"
        else:
            node_types[node] = "target"

    # Layout
    layouts = {
        "spring": lambda G: nx.spring_layout(G, k=2, seed=42, iterations=50),
        "kamada_kawai": lambda G: nx.kamada_kawai_layout(G),
        "circular": lambda G: nx.circular_layout(G),
        "shell": lambda G: nx.shell_layout(G, nlist=[top_tfs,
                           [n for n in G.nodes() if n not in top_tfs]]),
    }
    pos = layouts.get(layout, layouts["spring"])(G)

    # Plot
    fig, ax = plt.subplots(figsize=(16, 12))

    # Draw target nodes
    target_nodes = [n for n in G.nodes() if node_types[n] == "target"]
    nx.draw_networkx_nodes(G, pos, nodelist=target_nodes, node_size=20,
                            node_color="lightgray", alpha=0.5, ax=ax)

    # Draw TF nodes
    tf_nodes = [n for n in G.nodes() if node_types[n] == "TF"]
    tf_sizes = [tf_degree.get(n, 5) * 10 for n in tf_nodes]
    nx.draw_networkx_nodes(G, pos, nodelist=tf_nodes, node_size=tf_sizes,
                            node_color="tomato", alpha=0.8, ax=ax)

    # Draw edges
    nx.draw_networkx_edges(G, pos, alpha=0.1, arrows=True,
                            arrowsize=5, edge_color="gray", ax=ax)

    # Label TFs only
    tf_labels = {n: n for n in tf_nodes}
    nx.draw_networkx_labels(G, pos, labels=tf_labels, font_size=8,
                             font_weight="bold", ax=ax)

    ax.set_title(f"Gene Regulatory Network ({len(tf_nodes)} TFs, "
                 f"{len(target_nodes)} targets, {G.number_of_edges()} edges)")
    ax.axis("off")
    plt.tight_layout()
    plt.savefig("grn_network.png", dpi=150, bbox_inches="tight")
    plt.close()

    # Network statistics
    print(f"Network statistics:")
    print(f"  Nodes: {G.number_of_nodes()} ({len(tf_nodes)} TFs, {len(target_nodes)} targets)")
    print(f"  Edges: {G.number_of_edges()}")
    print(f"  Mean out-degree (TFs): {np.mean([G.out_degree(n) for n in tf_nodes]):.1f}")
    print(f"  Mean in-degree (targets): {np.mean([G.in_degree(n) for n in target_nodes]):.1f}")

    # Centrality analysis
    pagerank = nx.pagerank(G)
    top_pr = sorted(pagerank.items(), key=lambda x: -x[1])[:10]
    print(f"\nTop nodes by PageRank:")
    for node, pr in top_pr:
        print(f"  {node}: {pr:.4f} ({node_types[node]})")

    return G

# Usage
adjacencies = pd.read_csv("adjacencies.tsv", sep="\t")
G = visualize_grn(adjacencies, top_n_tfs=20, min_targets=10)
```

**Expected output**: Network visualization with TF hub nodes (sized by degree) and target genes. PageRank identifies the most influential nodes considering both direct and indirect regulatory effects.

---

## 12. Differential Regulon Activity Between Conditions

Compare regulon activity between experimental conditions or disease states.

```python
import pandas as pd
import numpy as np
from scipy.stats import mannwhitneyu, ranksums
from statsmodels.stats.multitest import multipletests
import matplotlib.pyplot as plt
import seaborn as sns

def differential_regulon_activity(auc_matrix, condition_labels,
                                    condition1="control", condition2="treatment",
                                    test="mannwhitney"):
    """Test for differential regulon activity between conditions.

    Parameters
    ----------
    auc_matrix : pd.DataFrame
        AUCell matrix (cells x regulons).
    condition_labels : pd.Series
        Condition labels aligned with auc_matrix index.
    condition1, condition2 : str
        Condition names to compare.
    test : str
        Statistical test: 'mannwhitney', 'ranksums', or 'ttest'.

    Returns
    -------
    pd.DataFrame with regulon, fold_change, p_value, padj columns.
    """
    mask1 = condition_labels == condition1
    mask2 = condition_labels == condition2

    group1 = auc_matrix.loc[mask1]
    group2 = auc_matrix.loc[mask2]

    print(f"Comparing: {condition1} ({mask1.sum()} cells) vs "
          f"{condition2} ({mask2.sum()} cells)")

    results = []
    for regulon in auc_matrix.columns:
        v1 = group1[regulon].values
        v2 = group2[regulon].values

        # Effect size (log2 fold change of means)
        mean1 = v1.mean()
        mean2 = v2.mean()
        log2fc = np.log2((mean2 + 1e-10) / (mean1 + 1e-10))

        # Statistical test
        if test == "mannwhitney":
            stat, pval = mannwhitneyu(v1, v2, alternative="two-sided")
        elif test == "ranksums":
            stat, pval = ranksums(v1, v2)
        else:
            from scipy.stats import ttest_ind
            stat, pval = ttest_ind(v1, v2, equal_var=False)

        # Cohen's d effect size
        pooled_std = np.sqrt((v1.std()**2 + v2.std()**2) / 2)
        cohens_d = (mean2 - mean1) / pooled_std if pooled_std > 0 else 0

        results.append({
            "regulon": regulon,
            f"mean_{condition1}": mean1,
            f"mean_{condition2}": mean2,
            "log2FC": log2fc,
            "cohens_d": cohens_d,
            "pvalue": pval,
        })

    df = pd.DataFrame(results)
    _, df["padj"], _, _ = multipletests(df["pvalue"], method="fdr_bh")
    df = df.sort_values("padj")

    sig = df[df["padj"] < 0.05]
    print(f"\nDifferential regulons (padj < 0.05): {len(sig)}")
    print(f"  Activated in {condition2}: {(sig['log2FC'] > 0).sum()}")
    print(f"  Repressed in {condition2}: {(sig['log2FC'] < 0).sum()}")

    print(f"\nTop differential regulons:")
    print(sig.head(20)[["regulon", "log2FC", "cohens_d", "padj"]].to_string(index=False))

    # Volcano plot
    fig, ax = plt.subplots(figsize=(10, 8))
    neg_log_p = -np.log10(df["padj"].clip(lower=1e-300))
    colors = np.where(
        (df["padj"] < 0.05) & (df["log2FC"] > 0.1), "red",
        np.where((df["padj"] < 0.05) & (df["log2FC"] < -0.1), "blue", "gray")
    )
    ax.scatter(df["log2FC"], neg_log_p, c=colors, s=30, alpha=0.6)

    # Label significant regulons
    for _, row in sig.head(15).iterrows():
        ax.annotate(row["regulon"], (row["log2FC"], -np.log10(max(row["padj"], 1e-300))),
                    fontsize=7, alpha=0.8)

    ax.axhline(-np.log10(0.05), ls="--", c="black", lw=0.5)
    ax.axvline(0.1, ls="--", c="black", lw=0.5)
    ax.axvline(-0.1, ls="--", c="black", lw=0.5)
    ax.set_xlabel("log2 Fold Change (AUC)")
    ax.set_ylabel("-log10(adjusted p-value)")
    ax.set_title(f"Differential Regulon Activity: {condition2} vs {condition1}")
    plt.tight_layout()
    plt.savefig("differential_regulons_volcano.png", dpi=150, bbox_inches="tight")
    plt.close()

    # Box plots for top differential regulons
    top_regs = sig.head(9)["regulon"].tolist()
    if top_regs:
        fig, axes = plt.subplots(3, 3, figsize=(12, 10))
        for ax, reg in zip(axes.flatten(), top_regs):
            plot_data = pd.DataFrame({
                "AUC": auc_matrix[reg],
                "Condition": condition_labels,
            })
            plot_data = plot_data[plot_data["Condition"].isin([condition1, condition2])]
            sns.boxplot(data=plot_data, x="Condition", y="AUC", ax=ax,
                       palette={"control": "lightblue", "treatment": "salmon"})
            pval = df[df["regulon"] == reg]["padj"].values[0]
            ax.set_title(f"{reg}\npadj={pval:.2e}", fontsize=8)
        plt.tight_layout()
        plt.savefig("differential_regulons_boxplots.png", dpi=150, bbox_inches="tight")
        plt.close()

    return df

# Usage
diff_regulons = differential_regulon_activity(
    auc_mtx,
    adata.obs["condition"],
    condition1="control",
    condition2="treatment",
)
diff_regulons.to_csv("differential_regulons.csv", index=False)
```

**Expected output**: Ranked list of differentially active regulons between conditions with effect sizes and adjusted p-values. Volcano plot highlights the most significantly changed regulons. Box plots show the distribution of activity scores for top hits.
