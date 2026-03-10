# Spatial Transcriptomics Recipes

Python code templates for spatial transcriptomics analysis with Squidpy and scanpy. Covers spatial graph construction, autocorrelation, domain detection, deconvolution, cell communication, and visualization.

Cross-skill routing: use `spatial-transcriptomics` for conceptual guidance, `single-cell-analysis` for scRNA-seq reference preparation, `gene-enrichment` for pathway analysis of spatial clusters.

---

## 1. Squidpy Spatial Graph Construction

Build spatial neighbor graphs from coordinate data. The graph type depends on the platform geometry.

```python
import scanpy as sc
import squidpy as sq
import numpy as np

def build_spatial_graph(adata, platform="visium", n_neighs=None, radius=None):
    """Build spatial neighbor graph appropriate for the platform.

    Parameters:
        adata: AnnData with spatial coordinates in adata.obsm['spatial']
        platform: 'visium' (grid), 'merfish' (generic), 'slideseq' (generic)
        n_neighs: number of neighbors (default: 6 for Visium, 15 for others)
        radius: optional distance radius cutoff (microns)
    Returns:
        adata with spatial_connectivities and spatial_distances in adata.obsp
    """
    if platform == "visium":
        n_neighs = n_neighs or 6
        sq.gr.spatial_neighbors(adata, n_neighs=n_neighs, coord_type="grid")
    elif platform in ("merfish", "seqfish"):
        # Delaunay triangulation for single-cell resolution
        sq.gr.spatial_neighbors(adata, coord_type="generic", delaunay=True)
    else:
        n_neighs = n_neighs or 15
        if radius:
            sq.gr.spatial_neighbors(adata, coord_type="generic", radius=radius)
        else:
            sq.gr.spatial_neighbors(adata, n_neighs=n_neighs, coord_type="generic")

    n_edges = adata.obsp["spatial_connectivities"].nnz
    avg_neighbors = n_edges / adata.n_obs
    print(f"Spatial graph: {adata.n_obs} nodes, {n_edges} edges, "
          f"avg {avg_neighbors:.1f} neighbors/spot")
    return adata

# Usage
adata = sc.read_visium("path/to/spaceranger_output")
adata = build_spatial_graph(adata, platform="visium")
```

**Key parameters:**
- `coord_type="grid"`: hexagonal grids (Visium). `coord_type="generic"`: irregular coordinates.
- `delaunay=True`: Delaunay triangulation, best for single-cell spatial data (MERFISH, seqFISH).
- `radius`: distance threshold in coordinate units; only connects neighbors within this radius.

**Expected output:** `adata.obsp['spatial_connectivities']` (sparse adjacency matrix) and `adata.obsp['spatial_distances']` (sparse distance matrix).

---

## 2. Spatial Autocorrelation: Moran's I per Gene

Identify spatially variable genes (SVGs) via Moran's I statistic. High Moran's I indicates spatial clustering of expression.

```python
import squidpy as sq
import pandas as pd

def compute_morans_i(adata, genes=None, n_perms=100, n_jobs=-1, fdr_thresh=0.05):
    """Compute Moran's I spatial autocorrelation for all or selected genes.

    Parameters:
        adata: AnnData with spatial graph computed (sq.gr.spatial_neighbors)
        genes: list of genes to test (default: all var_names)
        n_perms: permutations for p-value estimation (100 for speed, 1000 for publication)
        n_jobs: parallel jobs (-1 for all cores)
        fdr_thresh: FDR threshold for significant SVGs
    Returns:
        DataFrame of SVG results sorted by Moran's I
    """
    if genes is None:
        genes = adata.var_names

    sq.gr.spatial_autocorr(
        adata, mode="moran", genes=genes, n_perms=n_perms, n_jobs=n_jobs
    )

    svg_df = adata.uns["moranI"].copy()
    svg_df = svg_df.sort_values("I", ascending=False)

    sig = svg_df[svg_df["pval_sim_fdr"] < fdr_thresh]
    print(f"Moran's I: {len(svg_df)} genes tested, {len(sig)} significant SVGs (FDR < {fdr_thresh})")
    print(f"Top 5 SVGs: {sig.head(5).index.tolist()}")
    print(f"Moran's I range: [{sig['I'].min():.3f}, {sig['I'].max():.3f}]")

    return svg_df

# Usage
svg_results = compute_morans_i(adata, n_perms=1000)
top_svgs = svg_results[svg_results["pval_sim_fdr"] < 0.05].head(50).index.tolist()
sq.pl.spatial_scatter(adata, color=top_svgs[:6], shape=None, size=1.5)
```

**Key parameters:**
- `n_perms=100`: fast screening. Use `n_perms=1000` for publication-quality p-values.
- `mode="moran"`: global Moran's I. Alternative: `mode="geary"` for Geary's C (detects local heterogeneity).
- Moran's I range: -1 (dispersed) to +1 (clustered). Values > 0.3 with FDR < 0.05 are strong SVGs.

**Expected output:** `adata.uns["moranI"]` DataFrame with columns: `I` (Moran's I), `pval_sim` (permutation p-value), `pval_sim_fdr` (BH-adjusted p-value).

---

## 3. Spatial Domain Detection: STAGATE

Graph attention autoencoder for learning spatial domains. STAGATE integrates gene expression with spatial location through a graph attention network.

```python
import scanpy as sc
import numpy as np

def run_stagate(adata, n_domains=7, rad_cutoff=150, alpha=0.0, random_seed=42):
    """Run STAGATE spatial domain detection.

    Parameters:
        adata: AnnData with spatial coordinates and preprocessed expression
        n_domains: number of spatial domains to detect
        rad_cutoff: radius cutoff for spatial graph (in coordinate units)
        alpha: weight for spatial regularization (0.0 = expression only, 1.0 = spatial only)
        random_seed: for reproducibility
    Returns:
        adata with 'STAGATE_domain' in obs and 'STAGATE' embedding in obsm
    """
    import STAGATE_pyG as STAGATE

    # Build spatial graph for STAGATE
    STAGATE.Cal_Spatial_Net(adata, rad_cutoff=rad_cutoff)
    print(f"Spatial network: {adata.uns['Spatial_Net'].shape[0]} edges")

    # Train STAGATE
    adata = STAGATE.train_STAGATE(
        adata, alpha=alpha, random_seed=random_seed, n_epochs=1000
    )

    # Cluster the learned embedding
    sc.pp.neighbors(adata, use_rep="STAGATE", n_neighbors=15)
    sc.tl.leiden(adata, resolution=0.8, key_added="STAGATE_domain")

    # Refine domains if too many clusters
    if adata.obs["STAGATE_domain"].nunique() > n_domains:
        sc.tl.leiden(adata, resolution=0.5, key_added="STAGATE_domain")

    sc.tl.umap(adata)
    print(f"STAGATE domains: {adata.obs['STAGATE_domain'].nunique()}")

    return adata

# Usage
adata = run_stagate(adata, n_domains=7, rad_cutoff=150)
sq.pl.spatial_scatter(adata, color="STAGATE_domain", shape=None, size=1.5)
```

**Key parameters:**
- `rad_cutoff`: spatial graph radius. For Visium, typically 150-300 (coordinate units). Adjust based on spot spacing.
- `alpha`: 0.0 uses expression only (with spatial graph structure); increase for stronger spatial smoothing.
- `n_epochs=1000`: training epochs. Monitor loss for convergence.

**Expected output:** `adata.obsm['STAGATE']` (latent embedding), `adata.obs['STAGATE_domain']` (cluster labels).

---

## 4. BayesSpace Spatial Clustering with Smoothing

BayesSpace performs spatially-aware clustering with Bayesian smoothing, specifically designed for Visium data.

```python
import subprocess
import scanpy as sc

def run_bayesspace(adata, n_clusters=7, n_pcs=15, n_reps=50000, gamma=2):
    """Run BayesSpace spatial clustering via R bridge.

    Parameters:
        adata: AnnData with spatial coordinates and PCA
        n_clusters: target number of spatial clusters
        n_pcs: number of PCA components to use
        n_reps: MCMC iterations (50000 default, increase for better convergence)
        gamma: spatial smoothing parameter (higher = more spatial coherence)
    Returns:
        adata with 'bayesspace_cluster' in obs
    """
    # Export data for R
    adata.write_h5ad("_bayesspace_input.h5ad")

    r_script = f'''
    library(BayesSpace)
    library(SingleCellExperiment)
    library(zellkonverter)

    sce <- readH5AD("_bayesspace_input.h5ad")
    sce <- spatialPreprocess(sce, platform="Visium", n.PCs={n_pcs}, n.HVGs=2000)
    sce <- spatialCluster(sce, q={n_clusters}, nrep={n_reps}, gamma={gamma},
                          platform="Visium", save.chain=FALSE)
    labels <- colData(sce)$spatial.cluster
    write.csv(data.frame(barcode=colnames(sce), cluster=labels),
              "_bayesspace_output.csv", row.names=FALSE)
    '''

    with open("_bayesspace.R", "w") as f:
        f.write(r_script)

    subprocess.run(["Rscript", "_bayesspace.R"], check=True)

    results = pd.read_csv("_bayesspace_output.csv")
    cluster_map = dict(zip(results["barcode"], results["cluster"].astype(str)))
    adata.obs["bayesspace_cluster"] = adata.obs_names.map(cluster_map)

    print(f"BayesSpace clusters: {adata.obs['bayesspace_cluster'].nunique()}")
    return adata

# Usage
adata = run_bayesspace(adata, n_clusters=7, gamma=2)
sq.pl.spatial_scatter(adata, color="bayesspace_cluster", shape=None, size=1.5)
```

**Key parameters:**
- `gamma`: spatial smoothing. gamma=1 (weak smoothing) to gamma=3 (strong smoothing). Default gamma=2.
- `n_reps`: MCMC iterations. 50000 is standard; check convergence diagnostics.
- `n_clusters`: use `qTune()` in R to select optimal q via pseudo-log-likelihood.

**Expected output:** `adata.obs['bayesspace_cluster']` with spatially coherent cluster assignments.

---

## 5. Cell-Cell Communication: Ligand-Receptor Analysis

Spatially-constrained ligand-receptor interaction analysis using Squidpy.

```python
import squidpy as sq

def run_ligrec_analysis(adata, cluster_key="spatial_cluster", n_perms=1000,
                        pvalue_thresh=0.01, resources="CellPhoneDB"):
    """Run spatially-constrained ligand-receptor interaction analysis.

    Parameters:
        adata: AnnData with spatial graph and cluster annotations
        cluster_key: obs column with cell/spot type annotations
        n_perms: permutations for significance testing
        pvalue_thresh: threshold for significant interactions
        resources: interaction database ('CellPhoneDB', 'CellChatDB', 'NATMI')
    Returns:
        dict with interaction results and summary statistics
    """
    # Run ligand-receptor analysis
    sq.gr.ligrec(
        adata,
        n_perms=n_perms,
        cluster_key=cluster_key,
        use_raw=True,
        transmitter_params={"categories": "ligand"},
        receiver_params={"categories": "receptor"},
        interactions_params={"resources": resources},
    )

    # Extract results
    pvals = adata.uns[f"{cluster_key}_ligrec"]["pvalues"]
    means = adata.uns[f"{cluster_key}_ligrec"]["means"]

    # Count significant interactions per cluster pair
    n_sig = (pvals < pvalue_thresh).sum()
    print(f"Significant interactions (p < {pvalue_thresh}): {n_sig.sum()}")

    # Top interactions
    sig_mask = pvals < pvalue_thresh
    sig_means = means.where(sig_mask)
    top_interactions = sig_means.stack().dropna().sort_values(ascending=False)
    print(f"Top 10 interactions by mean expression:")
    for idx, val in top_interactions.head(10).items():
        print(f"  {idx}: mean={val:.3f}")

    return {
        "pvalues": pvals,
        "means": means,
        "n_significant": int(n_sig.sum()),
        "top_interactions": top_interactions,
    }

# Usage
results = run_ligrec_analysis(adata, cluster_key="spatial_cluster")

# Visualize specific source-target pairs
sq.pl.ligrec(
    adata,
    cluster_key="spatial_cluster",
    source_groups=["Tumor", "Fibroblast"],
    target_groups=["T_cell", "Macrophage"],
    pvalue_threshold=0.01,
    means_range=(0.5, None),
)
```

**Key parameters:**
- `n_perms=1000`: permutations for statistical significance. Higher = more precise p-values.
- `resources`: ligand-receptor database. CellPhoneDB is most common; CellChatDB has curated signaling pathways.
- `means_range=(0.5, None)`: filter weak interactions by mean expression threshold.

**Expected output:** `adata.uns['{cluster_key}_ligrec']` with `pvalues` and `means` DataFrames indexed by ligand-receptor pairs and cluster pairs.

---

## 6. Spatial Deconvolution: Cell2location, Tangram, RCTD

Three major deconvolution methods for estimating cell-type composition in spatial spots.

### Cell2location

```python
import cell2location
import scanpy as sc

def run_cell2location(adata_vis, adata_ref, cell_type_key="cell_type",
                      batch_key=None, n_cells_per_location=30, max_epochs_ref=250,
                      max_epochs_spatial=30000):
    """Run Cell2location deconvolution.

    Parameters:
        adata_vis: spatial AnnData (Visium/Slide-seq)
        adata_ref: scRNA-seq reference AnnData with cell type annotations
        cell_type_key: obs column in adata_ref with cell type labels
        batch_key: obs column for batch correction (optional)
        n_cells_per_location: expected cells per spot (Visium: 5-30)
        max_epochs_ref: training epochs for reference model
        max_epochs_spatial: training epochs for spatial model
    Returns:
        adata_vis with cell type abundance estimates in obsm
    """
    # Step 1: Train reference model
    cell2location.models.RegressionModel.setup_anndata(
        adata_ref, labels_key=cell_type_key, batch_key=batch_key
    )
    mod_ref = cell2location.models.RegressionModel(adata_ref)
    mod_ref.train(max_epochs=max_epochs_ref, use_gpu=True)
    adata_ref = mod_ref.export_posterior(adata_ref)
    inf_aver = adata_ref.varm["means_per_cluster_mu_fg"]

    print(f"Reference signatures: {inf_aver.shape[1]} cell types, {inf_aver.shape[0]} genes")

    # Step 2: Train spatial model
    cell2location.models.Cell2location.setup_anndata(
        adata_vis, batch_key="sample" if batch_key else None
    )
    mod = cell2location.models.Cell2location(
        adata_vis, cell_state_df=inf_aver,
        N_cells_per_location=n_cells_per_location,
        detection_alpha=20,
    )
    mod.train(max_epochs=max_epochs_spatial, use_gpu=True)
    adata_vis = mod.export_posterior(adata_vis)

    cell_types = inf_aver.columns.tolist()
    print(f"Deconvolution complete. Cell types mapped: {cell_types}")

    return adata_vis, cell_types

# Usage
adata_vis, cell_types = run_cell2location(adata_vis, adata_ref)
sq.pl.spatial_scatter(adata_vis, color=cell_types[:4], shape=None, size=1.5)
```

### Tangram

```python
import tangram as tg

def run_tangram(adata_ref, adata_vis, cell_type_key="cell_type",
                marker_genes=None, mode="cells", density_prior="rna_count_based"):
    """Run Tangram spatial deconvolution.

    Parameters:
        adata_ref: scRNA-seq reference AnnData
        adata_vis: spatial AnnData
        cell_type_key: obs column with cell type labels
        marker_genes: list of marker genes (if None, uses HVGs)
        mode: 'cells' (map individual cells) or 'clusters' (map cell types)
        density_prior: 'rna_count_based' (uses total counts) or 'uniform'
    Returns:
        adata_vis with projected cell type annotations
    """
    if marker_genes is None:
        sc.tl.rank_genes_groups(adata_ref, groupby=cell_type_key, method="wilcoxon")
        markers = adata_ref.uns["rank_genes_groups"]["names"]
        marker_genes = list(set([g for col in markers.dtype.names
                                 for g in markers[col][:50]]))

    tg.pp_adatas(adata_ref, adata_vis, genes=marker_genes)
    ad_map = tg.map_cells_to_space(
        adata_ref, adata_vis, mode=mode, density_prior=density_prior
    )
    tg.project_cell_annotations(ad_map, adata_vis, annotation=cell_type_key)

    cell_types = adata_ref.obs[cell_type_key].unique().tolist()
    print(f"Tangram mapping complete. Cell types: {cell_types}")
    return adata_vis

# Usage
adata_vis = run_tangram(adata_ref, adata_vis, marker_genes=marker_genes)
```

### RCTD (Robust Cell Type Decomposition)

```python
import subprocess
import pandas as pd

def run_rctd(adata_vis, adata_ref, cell_type_key="cell_type", max_cores=4):
    """Run RCTD deconvolution via R bridge (spacexr package).

    Parameters:
        adata_vis: spatial AnnData
        adata_ref: scRNA-seq reference AnnData
        cell_type_key: obs column with cell type labels
        max_cores: parallel cores for RCTD
    Returns:
        DataFrame with cell type weights per spot
    """
    # Export counts and metadata for R
    import scipy.sparse as sp
    counts_vis = adata_vis.X.toarray() if sp.issparse(adata_vis.X) else adata_vis.X
    pd.DataFrame(counts_vis.T, index=adata_vis.var_names,
                 columns=adata_vis.obs_names).to_csv("_rctd_spatial_counts.csv")
    pd.DataFrame(adata_vis.obsm["spatial"], index=adata_vis.obs_names,
                 columns=["x", "y"]).to_csv("_rctd_coords.csv")

    counts_ref = adata_ref.X.toarray() if sp.issparse(adata_ref.X) else adata_ref.X
    pd.DataFrame(counts_ref.T, index=adata_ref.var_names,
                 columns=adata_ref.obs_names).to_csv("_rctd_ref_counts.csv")
    adata_ref.obs[[cell_type_key]].to_csv("_rctd_ref_meta.csv")

    r_script = f'''
    library(spacexr)
    counts <- as.matrix(read.csv("_rctd_spatial_counts.csv", row.names=1))
    coords <- read.csv("_rctd_coords.csv", row.names=1)
    puck <- SpatialRNA(coords, counts)
    ref_counts <- as.matrix(read.csv("_rctd_ref_counts.csv", row.names=1))
    ref_meta <- read.csv("_rctd_ref_meta.csv", row.names=1)
    reference <- Reference(ref_counts, factor(ref_meta${cell_type_key}))
    rctd <- create.RCTD(puck, reference, max_cores={max_cores})
    rctd <- run.RCTD(rctd, doublet_mode="full")
    weights <- as.data.frame(rctd@results$weights)
    write.csv(weights, "_rctd_weights.csv")
    '''

    with open("_rctd.R", "w") as f:
        f.write(r_script)
    subprocess.run(["Rscript", "_rctd.R"], check=True)

    weights = pd.read_csv("_rctd_weights.csv", index_col=0)
    print(f"RCTD complete: {weights.shape[0]} spots x {weights.shape[1]} cell types")
    return weights

# Usage
weights = run_rctd(adata_vis, adata_ref, cell_type_key="cell_type")
```

**Expected output:** Per-spot cell type proportion/abundance estimates. Cell2location gives absolute cell counts; Tangram and RCTD give proportions.

---

## 7. Niche Detection: Neighborhood Enrichment

Quantify spatial co-localization between cell types or clusters.

```python
import squidpy as sq
import numpy as np
import pandas as pd

def neighborhood_enrichment(adata, cluster_key="spatial_cluster", n_perms=1000):
    """Compute neighborhood enrichment to identify spatially co-localized clusters.

    Parameters:
        adata: AnnData with spatial graph and cluster annotations
        cluster_key: obs column with cluster/cell type labels
        n_perms: permutations for z-score computation
    Returns:
        dict with z-score matrix and significant co-localizations
    """
    sq.gr.nhood_enrichment(adata, cluster_key=cluster_key, n_perms=n_perms)

    zscore = adata.uns[f"{cluster_key}_nhood_enrichment"]["zscore"]
    clusters = adata.obs[cluster_key].cat.categories.tolist()

    # Extract significant co-localizations (z > 2) and avoidances (z < -2)
    coloc = []
    avoid = []
    for i, c1 in enumerate(clusters):
        for j, c2 in enumerate(clusters):
            if i >= j:
                continue
            z = zscore[i, j]
            if z > 2:
                coloc.append({"cluster_1": c1, "cluster_2": c2, "zscore": z})
            elif z < -2:
                avoid.append({"cluster_1": c1, "cluster_2": c2, "zscore": z})

    print(f"Co-localized pairs (z > 2): {len(coloc)}")
    print(f"Avoidance pairs (z < -2): {len(avoid)}")

    return {
        "zscore_matrix": pd.DataFrame(zscore, index=clusters, columns=clusters),
        "co_localized": pd.DataFrame(coloc).sort_values("zscore", ascending=False) if coloc else pd.DataFrame(),
        "avoidance": pd.DataFrame(avoid).sort_values("zscore") if avoid else pd.DataFrame(),
    }

# Usage
nhood = neighborhood_enrichment(adata, cluster_key="spatial_cluster")
sq.pl.nhood_enrichment(adata, cluster_key="spatial_cluster", method="ward", figsize=(8, 8))
```

**Key parameters:**
- z-score > 2: clusters are significantly co-localized (neighbors more than expected by chance).
- z-score < -2: clusters significantly avoid each other.

**Expected output:** `adata.uns['{cluster_key}_nhood_enrichment']` with `zscore` and `count` matrices.

---

## 8. Co-occurrence Analysis

Measure co-occurrence probability of cluster pairs as a function of distance.

```python
import squidpy as sq
import matplotlib.pyplot as plt

def co_occurrence_analysis(adata, cluster_key="spatial_cluster",
                           clusters_of_interest=None, interval=50):
    """Compute co-occurrence scores between clusters across spatial distances.

    Parameters:
        adata: AnnData with spatial coordinates and cluster annotations
        cluster_key: obs column with cluster labels
        clusters_of_interest: list of cluster labels to analyze (None = all)
        interval: number of distance intervals to evaluate
    Returns:
        adata with co-occurrence results in uns
    """
    sq.gr.co_occurrence(adata, cluster_key=cluster_key, interval=interval)

    if clusters_of_interest is None:
        clusters_of_interest = adata.obs[cluster_key].cat.categories[:4].tolist()

    sq.pl.co_occurrence(
        adata, cluster_key=cluster_key,
        clusters=clusters_of_interest, figsize=(12, 6)
    )
    plt.tight_layout()
    plt.savefig("co_occurrence.png", dpi=150, bbox_inches="tight")

    print(f"Co-occurrence computed for {adata.obs[cluster_key].nunique()} clusters "
          f"across {interval} distance intervals")
    return adata

# Usage
adata = co_occurrence_analysis(adata, clusters_of_interest=["Tumor", "Immune", "Stroma"])
```

**Key parameters:**
- `interval`: number of distance bins. Higher = finer distance resolution.
- Co-occurrence ratio > 1: clusters appear together more than expected. < 1: less than expected.

**Expected output:** `adata.uns['{cluster_key}_co_occurrence']` with occurrence probabilities across distance intervals.

---

## 9. Image Feature Extraction from H&E

Extract morphological features from histology images associated with spatial data.

```python
import squidpy as sq
import scanpy as sc

def extract_image_features(adata, features=("summary", "histogram", "texture"),
                           key="spatial", spot_scale=1.0, n_jobs=-1):
    """Extract image features from H&E tissue image for each spot/cell.

    Parameters:
        adata: AnnData with spatial coordinates and associated tissue image
        features: feature types to extract
            - 'summary': mean, std of pixel intensities per channel
            - 'histogram': histogram of pixel intensities
            - 'texture': Haralick texture features (GLCM-based)
        key: key in adata.uns['spatial'] containing image data
        spot_scale: scale factor for spot crop size (1.0 = default)
        n_jobs: parallel jobs
    Returns:
        adata with image features in obsm
    """
    for feat_type in features:
        sq.im.calculate_image_features(
            adata,
            adata.uns["spatial"][list(adata.uns["spatial"].keys())[0]]["images"]["hires"],
            features=feat_type,
            key_added=f"img_{feat_type}",
            spot_scale=spot_scale,
            n_jobs=n_jobs,
        )
        n_feats = adata.obsm[f"img_{feat_type}"].shape[1]
        print(f"  {feat_type}: {n_feats} features extracted")

    # Combine all features
    import pandas as pd
    all_features = pd.concat(
        [adata.obsm[f"img_{ft}"] for ft in features], axis=1
    )
    adata.obsm["img_features"] = all_features
    print(f"Total image features: {all_features.shape[1]}")

    return adata

# Usage
adata = extract_image_features(adata, features=("summary", "histogram", "texture"))

# Correlate image features with gene expression
from scipy.stats import spearmanr
for gene in ["CDH1", "VIM", "COL1A1"]:
    if gene in adata.var_names:
        expr = adata[:, gene].X.toarray().flatten()
        for feat_col in adata.obsm["img_features"].columns[:3]:
            r, p = spearmanr(expr, adata.obsm["img_features"][feat_col])
            if abs(r) > 0.3:
                print(f"  {gene} vs {feat_col}: rho={r:.3f}, p={p:.2e}")
```

**Key parameters:**
- `summary`: mean, std per channel (3 channels x 2 stats = 6 features).
- `texture`: GLCM features (contrast, correlation, energy, homogeneity).
- `spot_scale`: crop size multiplier. 1.0 = spot diameter; increase for larger context.

**Expected output:** `adata.obsm['img_features']` with morphological features per spot.

---

## 10. Ripley's Statistics for Spatial Point Patterns

Test whether cell types show clustered, random, or dispersed spatial distributions.

```python
import squidpy as sq
import matplotlib.pyplot as plt

def ripley_analysis(adata, cluster_key="spatial_cluster", mode="L",
                    clusters=None, n_simulations=100):
    """Compute Ripley's statistics to characterize spatial point patterns.

    Parameters:
        adata: AnnData with spatial coordinates and cluster annotations
        cluster_key: obs column with cluster/cell type labels
        mode: 'L' (L-function, normalized K), 'F' (empty space), 'G' (nearest neighbor)
        clusters: list of clusters to analyze (None = all)
        n_simulations: Monte Carlo simulations for confidence envelope
    Returns:
        adata with Ripley's results in uns
    """
    sq.gr.ripley(adata, cluster_key=cluster_key, mode=mode,
                 n_simulations=n_simulations)

    # Plot results
    if clusters is None:
        clusters = adata.obs[cluster_key].cat.categories[:4].tolist()

    sq.pl.ripley(adata, cluster_key=cluster_key, mode=mode)
    plt.tight_layout()
    plt.savefig(f"ripley_{mode}.png", dpi=150, bbox_inches="tight")

    print(f"Ripley's {mode}-function computed for {adata.obs[cluster_key].nunique()} clusters")
    print("Interpretation:")
    print("  L(r) > expected: clustered at distance r")
    print("  L(r) < expected: dispersed at distance r")
    print("  L(r) = expected: complete spatial randomness (CSR)")

    return adata

# Usage
adata = ripley_analysis(adata, cluster_key="cell_type", mode="L")
```

**Key parameters:**
- `mode="L"`: L-function (variance-stabilized K). Most common. L(r) - r > 0 indicates clustering.
- `mode="F"`: empty space function. Tests for voids.
- `mode="G"`: nearest-neighbor function. Tests for aggregation.
- `n_simulations`: simulations for confidence envelopes under complete spatial randomness.

**Expected output:** `adata.uns['{cluster_key}_ripley_{mode}']` with observed statistics and simulation envelopes.

---

## 11. Integration of Multiple Spatial Sections

Integrate multiple tissue sections for joint analysis while preserving spatial information.

```python
import scanpy as sc
import squidpy as sq
import numpy as np

def integrate_spatial_sections(adata_list, section_names, batch_key="section",
                               n_hvgs=3000, n_pcs=30):
    """Integrate multiple spatial sections for joint analysis.

    Parameters:
        adata_list: list of AnnData objects (one per section)
        section_names: list of section identifiers
        batch_key: obs column name for section labels
        n_hvgs: number of highly variable genes for integration
        n_pcs: PCA components for Harmony integration
    Returns:
        concatenated AnnData with batch-corrected embedding
    """
    for adata, name in zip(adata_list, section_names):
        adata.obs[batch_key] = name
        # Offset spatial coordinates to avoid overlap
        if name != section_names[0]:
            x_offset = max(a.obsm["spatial"][:, 0].max()
                          for a in adata_list[:adata_list.index(adata)]) + 1000
            adata.obsm["spatial"][:, 0] += x_offset

    # Concatenate
    adata_combined = sc.concat(adata_list, label=batch_key, keys=section_names)

    # Standard preprocessing
    sc.pp.normalize_total(adata_combined, target_sum=1e4)
    sc.pp.log1p(adata_combined)
    adata_combined.raw = adata_combined
    sc.pp.highly_variable_genes(adata_combined, n_top_genes=n_hvgs,
                                 flavor="seurat_v3", batch_key=batch_key)
    adata_combined = adata_combined[:, adata_combined.var["highly_variable"]]
    sc.pp.scale(adata_combined, max_value=10)
    sc.pp.pca(adata_combined, n_comps=n_pcs)

    # Harmony batch correction
    import harmonypy as hm
    ho = hm.run_harmony(adata_combined.obsm["X_pca"], adata_combined.obs, batch_key)
    adata_combined.obsm["X_pca_harmony"] = ho.Z_corr.T

    # Build neighbors and cluster on corrected embedding
    sc.pp.neighbors(adata_combined, use_rep="X_pca_harmony", n_neighbors=15)
    sc.tl.leiden(adata_combined, resolution=0.8, key_added="integrated_cluster")
    sc.tl.umap(adata_combined)

    print(f"Integrated: {len(adata_list)} sections, {adata_combined.n_obs} total spots")
    print(f"Clusters: {adata_combined.obs['integrated_cluster'].nunique()}")

    return adata_combined

# Usage
adata_combined = integrate_spatial_sections(
    [adata_s1, adata_s2, adata_s3],
    section_names=["section_1", "section_2", "section_3"]
)
```

**Key parameters:**
- Spatial coordinate offset prevents visual overlap when plotting combined sections.
- Harmony corrects batch effects while preserving biological variation.
- Use `batch_key` in HVG selection for cross-section consistency.

**Expected output:** Combined AnnData with `X_pca_harmony` embedding and `integrated_cluster` labels.

---

## 12. Visualization: Spatial Scatter Plots with Gene Overlay

Production-quality spatial visualizations with gene expression overlay.

```python
import squidpy as sq
import scanpy as sc
import matplotlib.pyplot as plt
import numpy as np

def spatial_gene_plot(adata, genes, cluster_key=None, ncols=3, spot_size=1.3,
                      cmap="Spectral_r", save_prefix="spatial"):
    """Create spatial scatter plots with gene expression or cluster overlays.

    Parameters:
        adata: AnnData with spatial coordinates
        genes: list of genes to visualize
        cluster_key: obs column to show alongside genes (optional)
        ncols: columns in subplot grid
        spot_size: spot size for plotting
        cmap: colormap for continuous values
        save_prefix: filename prefix for saved figures
    """
    # Gene expression spatial plots
    color_vars = list(genes)
    if cluster_key:
        color_vars = [cluster_key] + color_vars

    nrows = int(np.ceil(len(color_vars) / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(5 * ncols, 4.5 * nrows))
    axes = np.atleast_2d(axes)

    for idx, var in enumerate(color_vars):
        row, col = divmod(idx, ncols)
        ax = axes[row, col]
        if var in adata.obs.columns:
            sq.pl.spatial_scatter(adata, color=var, shape=None, size=spot_size, ax=ax)
        elif var in adata.var_names:
            sq.pl.spatial_scatter(adata, color=var, shape=None, size=spot_size,
                                  cmap=cmap, ax=ax)
        ax.set_title(var, fontsize=10, fontweight="bold")
        ax.axis("off")

    # Hide empty subplots
    for idx in range(len(color_vars), nrows * ncols):
        row, col = divmod(idx, ncols)
        axes[row, col].axis("off")

    plt.tight_layout()
    plt.savefig(f"{save_prefix}_genes.png", dpi=300, bbox_inches="tight")
    plt.show()
    print(f"Saved: {save_prefix}_genes.png")


def spatial_multi_panel(adata, panel_configs, figsize=(16, 12)):
    """Create multi-panel spatial figure with different overlays.

    Parameters:
        adata: AnnData with spatial coordinates
        panel_configs: list of dicts with keys 'color', 'title', optional 'cmap'
        figsize: figure size
    """
    n = len(panel_configs)
    ncols = min(3, n)
    nrows = int(np.ceil(n / ncols))

    fig, axes = plt.subplots(nrows, ncols, figsize=figsize)
    axes = np.atleast_2d(axes).flatten()

    for idx, config in enumerate(panel_configs):
        ax = axes[idx]
        sq.pl.spatial_scatter(
            adata, color=config["color"],
            shape=None, size=1.3,
            cmap=config.get("cmap", "Spectral_r"),
            ax=ax
        )
        ax.set_title(config.get("title", config["color"]), fontsize=10)
        ax.axis("off")

    for idx in range(n, len(axes)):
        axes[idx].axis("off")

    plt.tight_layout()
    plt.savefig("spatial_multi_panel.png", dpi=300, bbox_inches="tight")
    plt.show()

# Usage
spatial_gene_plot(adata, genes=["EPCAM", "VIM", "CD3D", "CD68", "COL1A1"],
                  cluster_key="spatial_cluster", spot_size=1.5)

# Multi-panel with different settings
spatial_multi_panel(adata, [
    {"color": "spatial_cluster", "title": "Spatial Clusters"},
    {"color": "n_genes_by_counts", "title": "Gene Count", "cmap": "viridis"},
    {"color": "EPCAM", "title": "EPCAM (Epithelial)", "cmap": "Reds"},
    {"color": "VIM", "title": "VIM (Mesenchymal)", "cmap": "Blues"},
    {"color": "CD3D", "title": "CD3D (T cells)", "cmap": "Greens"},
    {"color": "CD68", "title": "CD68 (Macrophages)", "cmap": "Oranges"},
])
```

**Key parameters:**
- `spot_size`: adjust based on data density. Visium: 1.0-1.5. MERFISH: 0.3-0.8.
- `cmap="Spectral_r"`: good for gene expression (low=blue, high=red). `"viridis"` for QC metrics.
- `dpi=300`: publication quality. Use `dpi=150` for quick previews.

**Expected output:** PNG files with spatial scatter plots showing gene expression or cluster assignments overlaid on tissue coordinates.

---

## Quick Reference

| Task | Recipe | Key function |
|------|--------|-------------|
| Spatial graph construction | #1 | `sq.gr.spatial_neighbors()` |
| SVG detection (Moran's I) | #2 | `sq.gr.spatial_autocorr()` |
| Domain detection (STAGATE) | #3 | `STAGATE.train_STAGATE()` |
| Spatial clustering (BayesSpace) | #4 | `spatialCluster()` (R) |
| Ligand-receptor analysis | #5 | `sq.gr.ligrec()` |
| Deconvolution | #6 | Cell2location / Tangram / RCTD |
| Neighborhood enrichment | #7 | `sq.gr.nhood_enrichment()` |
| Co-occurrence | #8 | `sq.gr.co_occurrence()` |
| H&E image features | #9 | `sq.im.calculate_image_features()` |
| Ripley's statistics | #10 | `sq.gr.ripley()` |
| Multi-section integration | #11 | Harmony + `sc.concat()` |
| Spatial visualization | #12 | `sq.pl.spatial_scatter()` |

---

## Cross-Skill Routing

- Statistical test details and assumptions --> `biostat-recipes`
- Single-cell reference preparation for deconvolution --> `single-cell-analysis`
- Gene set enrichment of spatial clusters --> `gene-enrichment`
- Multi-omic integration with spatial data --> `multi-omics-integration`
- Pathway modeling from spatial patterns --> `systems-biology`
