# Advanced Clustering & Cell Annotation Recipes

Python and R code templates for advanced clustering, batch correction, cell type annotation, and trajectory initialization in single-cell RNA-seq analysis.

Cross-skill routing: use `gene-enrichment` for pathway enrichment of marker gene lists, `systems-biology` for network analysis of DE results.

---

## 1. Leiden Clustering with Resolution Sweep and Silhouette Scoring

Systematically evaluate clustering quality across resolutions to find the optimal granularity.

```python
import scanpy as sc
import numpy as np
import pandas as pd
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt

def resolution_sweep(adata, resolutions=None, n_pcs=30, n_neighbors=15,
                     use_rep=None, key_prefix="leiden"):
    """Sweep Leiden resolutions and score each with silhouette coefficient.

    Parameters
    ----------
    adata : AnnData
        Preprocessed AnnData with PCA computed.
    resolutions : list of float
        Resolutions to test. Default: 0.2 to 2.0 in 0.1 steps.
    n_pcs : int
        Number of PCs for neighbor graph (if not already computed).
    n_neighbors : int
        Number of neighbors for the graph.
    use_rep : str or None
        Representation to use (e.g., 'X_scVI', 'X_pca_harmony'). Default: 'X_pca'.

    Returns
    -------
    pd.DataFrame with resolution, n_clusters, silhouette_score columns.
    """
    if resolutions is None:
        resolutions = np.arange(0.2, 2.1, 0.1).round(1).tolist()

    rep = use_rep or "X_pca"

    # Compute neighbors if not present
    if "neighbors" not in adata.uns:
        sc.pp.neighbors(adata, n_neighbors=n_neighbors, n_pcs=n_pcs, use_rep=rep)

    results = []
    for res in resolutions:
        key = f"{key_prefix}_{res}"
        sc.tl.leiden(adata, resolution=res, key_added=key)
        labels = adata.obs[key].astype(int).values
        n_clusters = len(np.unique(labels))

        if n_clusters < 2 or n_clusters >= adata.n_obs - 1:
            sil = np.nan
        else:
            # Subsample for speed on large datasets
            if adata.n_obs > 50000:
                idx = np.random.choice(adata.n_obs, 50000, replace=False)
                sil = silhouette_score(adata.obsm[rep][idx, :n_pcs], labels[idx])
            else:
                sil = silhouette_score(adata.obsm[rep][:, :n_pcs], labels)

        results.append({"resolution": res, "n_clusters": n_clusters, "silhouette": sil})
        print(f"  res={res:.1f}: {n_clusters} clusters, silhouette={sil:.4f}" if not np.isnan(sil)
              else f"  res={res:.1f}: {n_clusters} clusters, silhouette=NA")

    df = pd.DataFrame(results)

    # Plot
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot(df["resolution"], df["silhouette"], "b-o", label="Silhouette")
    ax1.set_xlabel("Resolution"); ax1.set_ylabel("Silhouette Score", color="b")
    ax2 = ax1.twinx()
    ax2.plot(df["resolution"], df["n_clusters"], "r--s", label="# Clusters")
    ax2.set_ylabel("Number of Clusters", color="r")
    ax1.set_title("Resolution Sweep"); fig.tight_layout()
    plt.savefig("resolution_sweep.png", dpi=150, bbox_inches="tight")
    plt.close()

    best = df.loc[df["silhouette"].idxmax()]
    print(f"\nBest resolution: {best['resolution']} "
          f"({int(best['n_clusters'])} clusters, silhouette={best['silhouette']:.4f})")
    return df

# Usage
sweep_df = resolution_sweep(adata, resolutions=[0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.5, 2.0])
```

**Expected output**: A DataFrame ranking resolutions by silhouette score, and a dual-axis plot showing the silhouette vs cluster count trade-off. Higher silhouette means tighter, better-separated clusters.

---

## 2. Optimal n_neighbors and n_pcs Selection via Stability Analysis

Assess how robust clusters are to parameter perturbation using Adjusted Rand Index.

```python
from sklearn.metrics import adjusted_rand_score
from itertools import product

def parameter_stability(adata, n_neighbors_range=None, n_pcs_range=None,
                        resolution=0.8, n_repeats=3, use_rep="X_pca"):
    """Test clustering stability across n_neighbors and n_pcs combinations.

    Parameters
    ----------
    n_neighbors_range : list of int
        Neighbor counts to test. Default: [10, 15, 20, 30, 50].
    n_pcs_range : list of int
        PC counts to test. Default: [15, 20, 30, 40, 50].
    resolution : float
        Leiden resolution to use.
    n_repeats : int
        Number of Leiden runs per setting (Leiden is stochastic).

    Returns
    -------
    pd.DataFrame with n_neighbors, n_pcs, mean_ari, std_ari columns.
    """
    if n_neighbors_range is None:
        n_neighbors_range = [10, 15, 20, 30, 50]
    if n_pcs_range is None:
        n_pcs_range = [15, 20, 30, 40, 50]

    results = []
    ref_labels = None

    for nn, npc in product(n_neighbors_range, n_pcs_range):
        sc.pp.neighbors(adata, n_neighbors=nn, n_pcs=npc, use_rep=use_rep)
        run_labels = []
        for r in range(n_repeats):
            sc.tl.leiden(adata, resolution=resolution, key_added="_stability_tmp")
            run_labels.append(adata.obs["_stability_tmp"].values.copy())

        # Pairwise ARI between runs
        aris = []
        for i in range(len(run_labels)):
            for j in range(i + 1, len(run_labels)):
                aris.append(adjusted_rand_score(run_labels[i], run_labels[j]))

        mean_ari = np.mean(aris) if aris else 1.0
        std_ari = np.std(aris) if aris else 0.0

        results.append({
            "n_neighbors": nn, "n_pcs": npc,
            "mean_ari": mean_ari, "std_ari": std_ari,
            "n_clusters": len(np.unique(run_labels[0]))
        })
        print(f"  nn={nn}, npc={npc}: ARI={mean_ari:.4f} +/- {std_ari:.4f}, "
              f"k={len(np.unique(run_labels[0]))}")

    df = pd.DataFrame(results)

    # Heatmap
    pivot = df.pivot(index="n_neighbors", columns="n_pcs", values="mean_ari")
    import seaborn as sns
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(pivot, annot=True, fmt=".3f", cmap="YlGnBu", ax=ax)
    ax.set_title(f"Clustering Stability (ARI) at resolution={resolution}")
    plt.savefig("parameter_stability.png", dpi=150, bbox_inches="tight")
    plt.close()

    best = df.loc[df["mean_ari"].idxmax()]
    print(f"\nMost stable: nn={int(best['n_neighbors'])}, npc={int(best['n_pcs'])}, "
          f"ARI={best['mean_ari']:.4f}")
    return df

# Usage
stability_df = parameter_stability(adata, resolution=0.8)
```

**Expected output**: A heatmap of ARI scores. ARI near 1.0 indicates highly reproducible clusters; values below 0.8 suggest the clustering is sensitive to that parameter combination.

---

## 3. Harmony Batch Correction with Scanpy Integration

```python
import scanpy as sc
import harmonypy as hm
import matplotlib.pyplot as plt

def harmony_integrate(adata, batch_key="batch", n_pcs=30, max_iter=20,
                      theta=2.0, sigma=0.1, plot=True):
    """Run Harmony batch correction and rebuild downstream embeddings.

    Parameters
    ----------
    adata : AnnData
        Must have PCA computed in adata.obsm['X_pca'].
    batch_key : str
        Column in adata.obs with batch labels.
    n_pcs : int
        Number of PCs to use.
    theta : float
        Diversity clustering penalty. Higher = more aggressive correction.
        Default 2.0; use 1.0 for subtle effects, 3.0+ for strong batch effects.
    sigma : float
        Width of soft kmeans clusters. Lower = more aggressive correction.
    max_iter : int
        Maximum Harmony iterations.

    Returns
    -------
    adata with X_pca_harmony in obsm, recomputed neighbors, UMAP, Leiden.
    """
    # Run Harmony
    ho = hm.run_harmony(
        adata.obsm["X_pca"][:, :n_pcs],
        adata.obs,
        batch_key,
        max_iter_harmony=max_iter,
        theta=theta,
        sigma=sigma,
    )
    adata.obsm["X_pca_harmony"] = ho.Z_corr.T

    # Rebuild graph and embeddings
    sc.pp.neighbors(adata, use_rep="X_pca_harmony", n_neighbors=15)
    sc.tl.umap(adata)
    sc.tl.leiden(adata, resolution=0.5, key_added="leiden_harmony")

    if plot:
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        sc.pl.umap(adata, color=batch_key, ax=axes[0], title="Batch (Harmony)", show=False)
        sc.pl.umap(adata, color="leiden_harmony", ax=axes[1], title="Clusters (Harmony)", show=False)
        if "cell_type" in adata.obs.columns:
            sc.pl.umap(adata, color="cell_type", ax=axes[2], title="Cell Type", show=False)
        plt.tight_layout()
        plt.savefig("harmony_integration.png", dpi=150, bbox_inches="tight")
        plt.close()

    print(f"Harmony converged in {ho.kmeans_rounds[-1] if ho.kmeans_rounds else 'N/A'} iterations")
    print(f"Clusters after Harmony: {adata.obs['leiden_harmony'].nunique()}")
    return adata

# Usage
adata = harmony_integrate(adata, batch_key="batch", theta=2.0)
```

**Key parameters**: `theta` controls correction strength (increase for strong batch effects); `sigma` controls soft-clustering width. Start with defaults and adjust if batch separation persists or biology is lost.

---

## 4. scVI Latent Space for Integration

Deep generative model for batch correction that learns a joint latent representation.

```python
import scanpy as sc
import scvi

def scvi_integrate(adata, batch_key="batch", n_latent=30, n_layers=2,
                   n_top_genes=3000, max_epochs=200, early_stopping=True):
    """Train scVI model for batch-integrated latent representation.

    Parameters
    ----------
    adata : AnnData
        Must contain raw counts in adata.layers['counts'] or adata.X.
    batch_key : str
        Column in adata.obs with batch labels.
    n_latent : int
        Dimensionality of latent space. 10-30 typical.
    n_layers : int
        Number of hidden layers in encoder/decoder. 1-2 typical.
    n_top_genes : int
        Number of HVGs to select.
    max_epochs : int
        Maximum training epochs.

    Returns
    -------
    adata with X_scVI in obsm, trained model object.
    """
    # Select HVGs (scVI expects raw counts)
    adata_scvi = adata.copy()
    sc.pp.highly_variable_genes(
        adata_scvi, n_top_genes=n_top_genes, subset=True, flavor="seurat_v3",
        layer="counts" if "counts" in adata_scvi.layers else None,
    )

    # Setup and train
    scvi.model.SCVI.setup_anndata(
        adata_scvi,
        layer="counts" if "counts" in adata_scvi.layers else None,
        batch_key=batch_key,
    )
    model = scvi.model.SCVI(adata_scvi, n_latent=n_latent, n_layers=n_layers, dropout_rate=0.1)
    model.train(max_epochs=max_epochs, early_stopping=early_stopping, early_stopping_patience=10)

    # Extract latent and store in original adata
    latent = model.get_latent_representation()
    adata.obsm["X_scVI"] = latent

    # Rebuild graph
    sc.pp.neighbors(adata, use_rep="X_scVI", n_neighbors=15)
    sc.tl.umap(adata)
    sc.tl.leiden(adata, resolution=0.5, key_added="leiden_scVI")

    train_elbo = model.history["elbo_train"]
    print(f"Final train ELBO: {train_elbo.iloc[-1].values[0]:.2f}")
    print(f"Epochs trained: {len(train_elbo)}")
    print(f"Clusters: {adata.obs['leiden_scVI'].nunique()}")

    return adata, model

# Usage
adata, scvi_model = scvi_integrate(adata, batch_key="batch", n_latent=30)
# Save: scvi_model.save("scvi_model/")
# Load: model = scvi.model.SCVI.load("scvi_model/", adata=adata_scvi)
```

**Expected output**: ELBO should decrease during training. Compare UMAP colored by batch before/after -- batches should intermix while cell types remain distinct.

---

## 5. Automated Cell Type Annotation with CellTypist

Pretrained machine-learning models for automated cell type annotation.

```python
import scanpy as sc
import celltypist
from celltypist import models

def annotate_celltypist(adata, model_name="Immune_All_Low.pkl", majority_voting=True):
    """Annotate cell types using CellTypist pretrained models.

    Parameters
    ----------
    adata : AnnData
        Log-normalized expression data (scanpy-style: log1p of count/10k).
    model_name : str
        CellTypist model name. Options:
        - 'Immune_All_Low.pkl': broad immune cell types (~30 types)
        - 'Immune_All_High.pkl': fine-grained immune (~100 types)
        - 'Developing_Human_Brain.pkl': brain cell types
        - 'Cells_Intestinal_Tract.pkl': gut epithelium
        See celltypist.models.models_description() for full list.
    majority_voting : bool
        Use over-clustering + majority voting for smoother labels.

    Returns
    -------
    adata with 'celltypist_label' and 'celltypist_conf' in obs.
    """
    # Download model if needed
    models.download_models(force_update=False, model=model_name)
    model = models.Model.load(model=model_name)

    # Predict
    predictions = celltypist.annotate(
        adata,
        model=model,
        majority_voting=majority_voting,
    )

    # Transfer labels
    result = predictions.to_adata()
    if majority_voting:
        adata.obs["celltypist_label"] = result.obs["majority_voting"]
        adata.obs["celltypist_conf"] = result.obs["conf_score"]
    else:
        adata.obs["celltypist_label"] = result.obs["predicted_labels"]
        adata.obs["celltypist_conf"] = result.obs["conf_score"]

    # Summary
    print(f"Cell types found: {adata.obs['celltypist_label'].nunique()}")
    print(adata.obs["celltypist_label"].value_counts())
    print(f"\nMean confidence: {adata.obs['celltypist_conf'].mean():.3f}")
    low_conf = (adata.obs["celltypist_conf"] < 0.5).sum()
    print(f"Low-confidence cells (<0.5): {low_conf} ({low_conf/adata.n_obs*100:.1f}%)")

    return adata

# Usage
adata = annotate_celltypist(adata, model_name="Immune_All_Low.pkl")
sc.pl.umap(adata, color="celltypist_label", legend_loc="on data", frameon=False)
plt.savefig("celltypist_annotation.png", dpi=150, bbox_inches="tight")
```

**Expected output**: Each cell receives a label and confidence score. Investigate cells with confidence < 0.5 -- they may represent transitional states or cell types absent from the training data.

---

## 6. Reference-Based Annotation with SingleR (Seurat/R)

```R
library(Seurat)
library(SingleR)
library(celldex)

# Load Seurat object
seurat_obj <- readRDS("seurat_object.rds")

# Load reference dataset
# Options: HumanPrimaryCellAtlasData(), BlueprintEncodeData(),
#          MonacoImmuneData(), DatabaseImmuneCellExpressionData()
ref <- celldex::HumanPrimaryCellAtlasData()

# Convert Seurat to SingleCellExperiment for SingleR
sce <- as.SingleCellExperiment(seurat_obj)

# Run SingleR with fine labels
singler_results <- SingleR(
    test = sce,
    ref = ref,
    labels = ref$label.fine,  # Use label.main for broad categories
    assay.type.test = "logcounts",
    de.method = "wilcox",
    BPPARAM = BiocParallel::MulticoreParam(workers = 4)
)

# Add to Seurat object
seurat_obj$singler_label <- singler_results$labels
seurat_obj$singler_pruned <- singler_results$pruned.labels
seurat_obj$singler_delta <- singler_results$delta.next

# Diagnostics
cat("Cell types found:", length(unique(singler_results$labels)), "\n")
cat("Pruned (low-confidence):", sum(is.na(singler_results$pruned.labels)), "\n")

# Heatmap of assignment scores
plotScoreHeatmap(singler_results, show.pruned = TRUE)
ggsave("singler_score_heatmap.png", width = 12, height = 8)

# Per-label diagnostics
plotDeltaDistribution(singler_results)
ggsave("singler_delta_distribution.png", width = 10, height = 8)

# UMAP with SingleR labels
DimPlot(seurat_obj, group.by = "singler_label", label = TRUE, repel = TRUE) +
    NoLegend()
ggsave("singler_umap.png", width = 10, height = 8)
```

**Key parameters**: `label.fine` gives granular types; `label.main` gives broad categories. Pruned labels (NA) indicate ambiguous cells. `delta.next` measures the difference between the best and second-best score -- low delta means uncertain assignment.

---

## 7. Marker Gene Scoring (sc.tl.score_genes)

Score cells for activity of predefined gene signatures.

```python
import scanpy as sc
import numpy as np

def score_gene_signatures(adata, signatures, ctrl_size=50, use_raw=False):
    """Score cells for multiple gene signatures.

    Parameters
    ----------
    adata : AnnData
        Normalized, log-transformed data.
    signatures : dict
        {signature_name: [gene_list]}. Example:
        {'T_cell_activation': ['CD69', 'IL2RA', 'TNFRSF9', 'IFNG'],
         'Exhaustion': ['PDCD1', 'LAG3', 'HAVCR2', 'TIGIT', 'TOX']}
    ctrl_size : int
        Number of reference genes per binned expression level.
        Larger = more stable scores but slower.
    use_raw : bool
        Score from adata.raw (recommended if adata is subset to HVGs).

    Returns
    -------
    adata with score columns in obs.
    """
    for name, genes in signatures.items():
        # Filter to genes present in the data
        var_names = adata.raw.var_names if use_raw else adata.var_names
        valid = [g for g in genes if g in var_names]
        missing = [g for g in genes if g not in var_names]

        if missing:
            print(f"  {name}: {len(missing)} genes missing: {missing}")

        if len(valid) < 2:
            print(f"  {name}: skipping, <2 valid genes")
            continue

        sc.tl.score_genes(
            adata,
            gene_list=valid,
            ctrl_size=ctrl_size,
            score_name=f"score_{name}",
            use_raw=use_raw,
        )
        score_col = f"score_{name}"
        print(f"  {name}: scored with {len(valid)} genes, "
              f"mean={adata.obs[score_col].mean():.3f}, "
              f"std={adata.obs[score_col].std():.3f}")

    return adata

# Usage
signatures = {
    "T_cell_activation": ["CD69", "IL2RA", "TNFRSF9", "IFNG", "TNF", "IL2"],
    "Exhaustion": ["PDCD1", "LAG3", "HAVCR2", "TIGIT", "TOX", "CTLA4"],
    "Cytotoxicity": ["GZMA", "GZMB", "GZMK", "PRF1", "GNLY", "NKG7"],
    "Proliferation": ["MKI67", "TOP2A", "CDK1", "PCNA", "MCM2", "TYMS"],
    "Interferon_response": ["ISG15", "MX1", "IFIT1", "IFIT3", "OAS1", "STAT1"],
}
adata = score_gene_signatures(adata, signatures, use_raw=True)

# Visualize
sc.pl.umap(adata, color=[f"score_{s}" for s in signatures.keys()], ncols=3,
           cmap="RdBu_r", vcenter=0, frameon=False)
plt.savefig("gene_signature_scores.png", dpi=150, bbox_inches="tight")
```

**Expected output**: Each cell gets a score per signature. Positive scores indicate higher-than-average activity relative to control genes of similar expression level.

---

## 8. Subclustering Workflow for Specific Lineages

```python
import scanpy as sc
import numpy as np

def subcluster_lineage(adata, lineage_col="cell_type", lineage_value="T cells",
                       n_top_genes=2000, n_pcs=20, resolutions=None):
    """Extract a cell lineage and re-cluster from scratch.

    Parameters
    ----------
    adata : AnnData
        Full dataset with cell type annotations.
    lineage_col : str
        Column with cell type labels.
    lineage_value : str or list
        Cell type(s) to extract. Can be a single string or list.
    n_top_genes : int
        HVGs to select within the subset.
    n_pcs : int
        PCs for neighbor graph.
    resolutions : list of float
        Leiden resolutions to test.

    Returns
    -------
    AnnData subset with new HVGs, PCA, UMAP, and clusters.
    """
    if isinstance(lineage_value, str):
        lineage_value = [lineage_value]

    sub = adata[adata.obs[lineage_col].isin(lineage_value)].copy()
    print(f"Subset: {sub.n_obs} cells from {lineage_value}")

    # Re-process from counts
    if "counts" in sub.layers:
        sub.X = sub.layers["counts"].copy()
    sc.pp.normalize_total(sub, target_sum=1e4)
    sc.pp.log1p(sub)
    sc.pp.highly_variable_genes(sub, n_top_genes=n_top_genes, flavor="seurat_v3",
                                 layer="counts" if "counts" in sub.layers else None)
    sub_hvg = sub[:, sub.var.highly_variable].copy()
    sc.pp.scale(sub_hvg, max_value=10)
    sc.tl.pca(sub_hvg, n_comps=min(50, n_pcs + 20))
    sc.pp.neighbors(sub_hvg, n_neighbors=15, n_pcs=n_pcs)
    sc.tl.umap(sub_hvg)

    # Multi-resolution clustering
    if resolutions is None:
        resolutions = [0.3, 0.5, 0.8, 1.0, 1.5]
    for res in resolutions:
        sc.tl.leiden(sub_hvg, resolution=res, key_added=f"subleiden_{res}")

    # Marker genes for default resolution
    sc.tl.leiden(sub_hvg, resolution=0.5, key_added="subleiden")
    sc.tl.rank_genes_groups(sub_hvg, groupby="subleiden", method="wilcoxon", pts=True)
    markers = sc.get.rank_genes_groups_df(sub_hvg, group=None)
    top_markers = markers[(markers["pvals_adj"] < 0.05) & (markers["logfoldchanges"] > 1)]

    print(f"\nSubclusters: {sub_hvg.obs['subleiden'].nunique()}")
    print(f"Top markers per subcluster:")
    print(top_markers.groupby("group").head(3)[["group", "names", "logfoldchanges", "pvals_adj"]])

    # Plot
    sc.pl.umap(sub_hvg, color=["subleiden"] + [f"subleiden_{r}" for r in resolutions], ncols=3)
    plt.savefig(f"subcluster_{'_'.join(lineage_value)}.png", dpi=150, bbox_inches="tight")

    return sub_hvg, top_markers

# Usage
t_sub, t_markers = subcluster_lineage(adata, lineage_value="T cells", n_pcs=20)
```

**Expected output**: A new AnnData with subclusters of the target lineage, marker gene table, and UMAP at multiple resolutions.

---

## 9. Doublet Detection with Scrublet

Remove likely doublets before downstream analysis.

```python
import scrublet as scr
import scanpy as sc
import numpy as np
import matplotlib.pyplot as plt

def detect_doublets(adata, expected_rate=0.06, n_prin_comps=30,
                    min_counts=2, min_cells=3, threshold=None):
    """Run Scrublet doublet detection.

    Parameters
    ----------
    adata : AnnData
        Raw count matrix (before normalization).
    expected_rate : float
        Expected doublet rate. ~0.008 per 1000 cells captured (10x).
        For 10,000 cells: ~0.08. For 5,000 cells: ~0.04.
    n_prin_comps : int
        PCs for nearest-neighbor calculation.
    threshold : float or None
        Manual doublet score threshold. None = automatic (bimodal detection).

    Returns
    -------
    adata with 'doublet_score' and 'predicted_doublet' in obs.
    """
    # Use raw counts
    counts = adata.layers["counts"] if "counts" in adata.layers else adata.X

    scrub = scr.Scrublet(counts, expected_doublet_rate=expected_rate)
    doublet_scores, predicted_doublets = scrub.scrub_doublets(
        min_counts=min_counts,
        min_cells=min_cells,
        n_prin_comps=n_prin_comps,
    )

    if threshold is not None:
        predicted_doublets = doublet_scores > threshold

    adata.obs["doublet_score"] = doublet_scores
    adata.obs["predicted_doublet"] = predicted_doublets

    n_doublets = predicted_doublets.sum()
    print(f"Doublets detected: {n_doublets} ({n_doublets/adata.n_obs*100:.1f}%)")
    print(f"Threshold: {scrub.threshold_}")

    # Plot score distribution
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    axes[0].hist(scrub.doublet_scores_obs_, bins=50, alpha=0.6, label="Observed", density=True)
    axes[0].hist(scrub.doublet_scores_sim_, bins=50, alpha=0.6, label="Simulated", density=True)
    axes[0].axvline(scrub.threshold_, color="black", ls="--")
    axes[0].set_xlabel("Doublet Score"); axes[0].legend(); axes[0].set_title("Score Distribution")

    if "X_umap" in adata.obsm:
        sc.pl.umap(adata, color="doublet_score", cmap="Reds", ax=axes[1], show=False,
                   title="Doublet Scores on UMAP")
    plt.tight_layout()
    plt.savefig("doublet_detection.png", dpi=150, bbox_inches="tight")
    plt.close()

    return adata

# Usage
adata = detect_doublets(adata, expected_rate=0.06)
# Filter doublets
adata_clean = adata[~adata.obs["predicted_doublet"]].copy()
print(f"After doublet removal: {adata_clean.n_obs} cells")
```

**Expected output**: Bimodal score distribution with clear separation. Typical doublet rates: 1-8% depending on loading density. If no bimodal split is found, consider adjusting `expected_rate`.

---

## 10. PAGA Graph Abstraction for Trajectory Initialization

```python
import scanpy as sc
import numpy as np
import matplotlib.pyplot as plt

def run_paga_trajectory(adata, groups="leiden", root_group=None,
                        threshold=0.1, model="v1.2"):
    """PAGA graph abstraction with diffusion pseudotime.

    Parameters
    ----------
    adata : AnnData
        Preprocessed with neighbors graph computed.
    groups : str
        obs column with cluster/cell type labels.
    root_group : str or None
        Cluster to use as trajectory root. If None, uses the cluster
        with highest expression of stem/progenitor markers.
    threshold : float
        Connectivity threshold for PAGA edges. Lower = more edges.
    model : str
        PAGA model version: 'v1.0' (original) or 'v1.2' (improved).

    Returns
    -------
    adata with PAGA graph, dpt_pseudotime, and PAGA-initialized UMAP.
    """
    # Compute PAGA
    sc.tl.paga(adata, groups=groups, model=model)

    # Plot PAGA graph
    sc.pl.paga(adata, threshold=threshold, fontsize=8, node_size_scale=1.5,
               edge_width_scale=0.5)
    plt.savefig("paga_graph.png", dpi=150, bbox_inches="tight")
    plt.close()

    # PAGA-initialized UMAP for better layout
    sc.tl.umap(adata, init_pos="paga")

    # Diffusion pseudotime
    sc.tl.diffmap(adata, n_comps=15)

    if root_group is None:
        # Auto-detect root: cluster with smallest diffusion component 1
        dc1_means = adata.obs.groupby(groups).apply(
            lambda x: adata.obsm["X_diffmap"][x.index.get_indexer(x.index), 0].mean()
        )
        root_group = dc1_means.idxmin()
        print(f"Auto-selected root cluster: {root_group}")

    adata.uns["iroot"] = np.flatnonzero(adata.obs[groups] == str(root_group))[0]
    sc.tl.dpt(adata)

    # Plot
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    sc.pl.umap(adata, color=groups, ax=axes[0], title="Clusters", show=False, legend_loc="on data")
    sc.pl.umap(adata, color="dpt_pseudotime", ax=axes[1], title="Pseudotime", show=False)
    sc.pl.paga(adata, threshold=threshold, ax=axes[2], title="PAGA", show=False)
    plt.tight_layout()
    plt.savefig("paga_trajectory.png", dpi=150, bbox_inches="tight")
    plt.close()

    print(f"Pseudotime range: {adata.obs['dpt_pseudotime'].min():.3f} - "
          f"{adata.obs['dpt_pseudotime'].max():.3f}")
    return adata

# Usage
adata = run_paga_trajectory(adata, groups="leiden", root_group="0")
```

**Expected output**: PAGA graph showing cluster connectivity strengths, a UMAP initialized from PAGA positions (preserving global topology), and diffusion pseudotime values per cell.

---

## 11. Dendrogram-Based Cluster Merging

Merge overclustered groups that lack distinguishing markers.

```python
import scanpy as sc
import numpy as np
from scipy.cluster.hierarchy import fcluster

def merge_clusters_by_dendrogram(adata, groupby="leiden", n_merge=None,
                                  distance_threshold=None, method="wilcoxon"):
    """Merge clusters based on hierarchical clustering of expression profiles.

    Parameters
    ----------
    adata : AnnData
        Must have normalized expression data.
    groupby : str
        obs column with cluster labels to merge.
    n_merge : int or None
        Target number of final clusters. Mutually exclusive with distance_threshold.
    distance_threshold : float or None
        Distance cutoff for merging. Higher = fewer merges.
    method : str
        DE method for post-merge marker gene validation.

    Returns
    -------
    adata with '{groupby}_merged' in obs.
    """
    # Compute dendrogram
    sc.tl.dendrogram(adata, groupby=groupby, use_rep="X_pca", optimal_ordering=True)
    sc.pl.dendrogram(adata, groupby=groupby)
    plt.savefig("cluster_dendrogram.png", dpi=150, bbox_inches="tight")
    plt.close()

    # Get linkage matrix
    linkage = adata.uns[f"dendrogram_{groupby}"]["linkage"]
    categories = adata.uns[f"dendrogram_{groupby}"]["categories_ordered"]

    # Cut dendrogram
    if n_merge is not None:
        merge_labels = fcluster(linkage, t=n_merge, criterion="maxclust")
    elif distance_threshold is not None:
        merge_labels = fcluster(linkage, t=distance_threshold, criterion="distance")
    else:
        # Auto: merge clusters with distance < 20th percentile
        distances = linkage[:, 2]
        distance_threshold = np.percentile(distances, 20)
        merge_labels = fcluster(linkage, t=distance_threshold, criterion="distance")

    # Build mapping
    cluster_map = {}
    for orig_label, new_label in zip(categories, merge_labels):
        cluster_map[str(orig_label)] = str(new_label - 1)

    merged_key = f"{groupby}_merged"
    adata.obs[merged_key] = adata.obs[groupby].astype(str).map(cluster_map).astype("category")

    n_orig = adata.obs[groupby].nunique()
    n_merged = adata.obs[merged_key].nunique()
    print(f"Merged {n_orig} clusters → {n_merged} clusters")

    # Show merge mapping
    for new_c in sorted(adata.obs[merged_key].unique()):
        orig = [k for k, v in cluster_map.items() if v == new_c]
        if len(orig) > 1:
            print(f"  Cluster {new_c} ← merged from {orig}")

    # Validate with marker genes
    sc.tl.rank_genes_groups(adata, groupby=merged_key, method=method, pts=True)
    markers = sc.get.rank_genes_groups_df(adata, group=None)
    top = markers[(markers["pvals_adj"] < 0.05) & (markers["logfoldchanges"] > 0.5)]
    for c in sorted(adata.obs[merged_key].unique()):
        n_markers = len(top[top["group"] == c])
        print(f"  Cluster {c}: {n_markers} significant markers")

    return adata

# Usage
adata = merge_clusters_by_dendrogram(adata, groupby="leiden", n_merge=8)
sc.pl.umap(adata, color=["leiden", "leiden_merged"], ncols=2)
plt.savefig("merged_clusters.png", dpi=150, bbox_inches="tight")
```

**Expected output**: Clusters that are transcriptionally similar get merged. Validate by checking that each merged cluster retains distinguishing marker genes.

---

## 12. Differential Abundance Testing with Milo

Test whether cell type proportions differ between conditions.

```python
import scanpy as sc
import numpy as np
import pandas as pd
import milopy
import milopy.core as milo

def run_milo_da(adata, sample_col="sample", condition_col="condition",
                n_neighbors=30, prop=0.1, alpha=0.1):
    """Differential abundance testing with Milo.

    Parameters
    ----------
    adata : AnnData
        Preprocessed with neighbors graph. Must have sample and condition
        columns in obs.
    sample_col : str
        Column with biological replicate/sample IDs.
    condition_col : str
        Column with experimental condition (e.g., 'treated' vs 'control').
    n_neighbors : int
        Neighbors for neighborhood construction.
    prop : float
        Proportion of cells to sample as neighborhood indices (0.05-0.2).
    alpha : float
        Significance threshold for spatial FDR.

    Returns
    -------
    adata with Milo results in adata.uns['nhood_adata'].
    """
    # Build KNN graph if not present
    if "neighbors" not in adata.uns:
        sc.pp.neighbors(adata, n_neighbors=n_neighbors, use_rep="X_pca")

    # Make neighborhoods
    milo.make_nhoods(adata, prop=prop)
    print(f"Neighborhoods: {adata.obsm['nhoods'].shape[1]}")

    # Count cells per sample per neighborhood
    milo.count_nhoods(adata, sample_col=sample_col)

    # Build design matrix and test
    design_df = (
        adata.obs[[sample_col, condition_col]]
        .drop_duplicates()
        .set_index(sample_col)
    )

    milo.DA_nhoods(adata, design=f"~ {condition_col}", model_contrasts=None)

    # Results
    nhood_adata = adata.uns["nhood_adata"]
    n_sig = (nhood_adata.obs["SpatialFDR"] < alpha).sum()
    n_da_up = ((nhood_adata.obs["SpatialFDR"] < alpha) & (nhood_adata.obs["logFC"] > 0)).sum()
    n_da_down = ((nhood_adata.obs["SpatialFDR"] < alpha) & (nhood_adata.obs["logFC"] < 0)).sum()

    print(f"\nDA neighborhoods (SpatialFDR < {alpha}): {n_sig}/{len(nhood_adata)}")
    print(f"  Enriched in condition: {n_da_up}")
    print(f"  Depleted in condition: {n_da_down}")

    # Annotate neighborhoods with cell types
    if "cell_type" in adata.obs.columns:
        milo.annotate_nhoods(adata, anno_col="cell_type")
        da_by_type = (
            nhood_adata.obs
            .groupby("nhood_annotation")
            .agg(
                n_nhoods=("logFC", "count"),
                mean_logFC=("logFC", "mean"),
                n_sig=("SpatialFDR", lambda x: (x < alpha).sum()),
            )
            .sort_values("mean_logFC")
        )
        print(f"\nDA by cell type:")
        print(da_by_type)

    # Beeswarm plot
    milopy.plot.plot_nhood_graph(adata, alpha=alpha, min_size=2)
    plt.savefig("milo_beeswarm.png", dpi=150, bbox_inches="tight")
    plt.close()

    return adata

# Usage
adata = run_milo_da(adata, sample_col="patient_id", condition_col="treatment")
```

**Expected output**: A beeswarm plot showing neighborhoods colored by log fold change, with significant DA neighborhoods highlighted. Cell types showing consistent enrichment or depletion indicate compositional changes between conditions.
