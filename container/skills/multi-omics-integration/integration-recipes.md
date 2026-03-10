# Multi-Omics Integration Recipes

Python and R code templates for multi-omics data integration. Covers MOFA2, mixOmics, SNF, MCIA, iCluster+, concatenation-based approaches, cross-omics correlation, WGCNA, and evaluation metrics.

Cross-skill routing: use `multi-omics-integration` for conceptual guidance, `proteomics-analysis` for proteomics preprocessing, `epigenomics` for methylation/ChIP-seq preprocessing, `metabolomics-analysis` for metabolite annotation.

---

## 1. MOFA2: Model Setup and Training

Multi-Omics Factor Analysis v2 for discovering shared and view-specific latent factors across omics layers.

```python
import subprocess
import pandas as pd
import numpy as np

def run_mofa2(layer_dict, groups=None, n_factors=15, convergence_mode="slow",
              seed=42, outfile="mofa2_model.hdf5"):
    """Run MOFA2 via the mofapy2 Python interface.

    Parameters:
        layer_dict: dict of {layer_name: DataFrame (samples x features)}
        groups: dict of {sample: group_label} for multi-group analysis (optional)
        n_factors: max number of latent factors to learn
        convergence_mode: 'fast', 'medium', or 'slow' (more iterations)
        seed: random seed
        outfile: path to save trained model
    Returns:
        trained MOFA model object
    """
    from mofapy2.run.entry_point import entry_point

    ent = entry_point()

    # Prepare data: list of numpy arrays, one per view
    data = [[None]]  # placeholder, will be replaced
    views = list(layer_dict.keys())
    samples = list(layer_dict.values())[0].index.tolist()

    # Set data
    data_matrices = {}
    for view_name, df in layer_dict.items():
        data_matrices[view_name] = df.loc[samples].values.astype(np.float64)

    ent.set_data_options(scale_views=True, scale_groups=False)

    # Set data matrices
    data_list = [[data_matrices[v]] for v in views]
    ent.set_data_matrix(data_list, views_names=views,
                        samples_names=[samples],
                        groups_names=["group1"])

    # Model options
    ent.set_model_options(factors=n_factors, spikeslab_weights=True,
                          ard_weights=True)

    # Training options
    ent.set_train_options(convergence_mode=convergence_mode, seed=seed,
                          drop_factor_threshold=0.02, gpu_mode=False)

    ent.build()
    ent.run()
    ent.save(outfile)

    print(f"MOFA2 model saved to {outfile}")
    print(f"Active factors: {ent.model.getFactors().shape[1]}")
    return ent

# Usage
layers = {
    "RNA": rna_df,        # samples x genes
    "Protein": prot_df,   # samples x proteins
    "Methylation": meth_df  # samples x CpG probes
}
mofa_model = run_mofa2(layers, n_factors=15)
```

**Key parameters:**
- `n_factors`: start with 15-25; MOFA2 drops inactive factors automatically (drop_factor_threshold).
- `scale_views=True`: normalizes variance across views so no single view dominates.
- `spikeslab_weights=True`: enforces sparsity in feature weights for interpretability.
- `convergence_mode="slow"`: 5000 iterations max. Use "fast" for exploration.

**Expected output:** HDF5 model file containing factors (samples x factors), weights (features x factors per view), and variance explained.

---

## 2. MOFA2 Factor Interpretation: Variance Explained and Weights

Interpret MOFA2 factors by examining variance explained per view and top contributing features.

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def interpret_mofa_factors(model_path, layer_dict, top_n=20):
    """Extract and interpret MOFA2 factors from a trained model.

    Parameters:
        model_path: path to trained MOFA2 HDF5 model
        layer_dict: dict of {layer_name: DataFrame} used for training
        top_n: number of top features per factor per view
    Returns:
        dict with factors, weights, and variance explained
    """
    import h5py

    with h5py.File(model_path, "r") as f:
        # Extract factors (samples x factors)
        factors = np.array(f["expectations"]["Z"]["group1"])
        views = [v.decode() for v in f["views"]["views"][:]]
        samples = [s.decode() for s in f["samples"]["group1"]["samples"][:]]

        # Extract weights per view
        weights = {}
        for i, view in enumerate(views):
            W = np.array(f["expectations"]["W"][view])
            features = [feat.decode() for feat in f["features"][view]["features"][:]]
            weights[view] = pd.DataFrame(W, index=features,
                                          columns=[f"Factor{k+1}" for k in range(W.shape[1])])

    n_factors = factors.shape[1]
    factors_df = pd.DataFrame(factors, index=samples,
                               columns=[f"Factor{k+1}" for k in range(n_factors)])

    # Variance explained per view per factor
    var_explained = {}
    for view, df in layer_dict.items():
        total_var = np.var(df.loc[samples].values)
        W = weights[view].values
        ve = []
        for k in range(n_factors):
            recon = np.outer(factors[:, k], W[:, k])
            ve.append(np.var(recon) / total_var)
        var_explained[view] = ve

    ve_df = pd.DataFrame(var_explained,
                          index=[f"Factor{k+1}" for k in range(n_factors)])

    # Plot variance explained
    fig, ax = plt.subplots(figsize=(10, 6))
    ve_df.plot(kind="bar", ax=ax, width=0.8)
    ax.set_ylabel("Variance Explained")
    ax.set_title("MOFA2 Variance Explained per View per Factor")
    ax.legend(title="View")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("mofa2_variance_explained.png", dpi=150)

    # Top features per factor per view
    print("\nTop features per factor:")
    for factor in factors_df.columns[:5]:
        print(f"\n  {factor}:")
        for view in views:
            top = weights[view][factor].abs().nlargest(top_n)
            genes = ", ".join(top.index[:5])
            print(f"    {view}: {genes}")

    return {"factors": factors_df, "weights": weights, "variance_explained": ve_df}

# Usage
results = interpret_mofa_factors("mofa2_model.hdf5", layers)
```

**Key parameters:**
- Factors active in multiple views are "shared" factors (biological signal).
- Factors active in only one view are "view-specific" (may be technical or biology unique to that layer).
- Top features (highest absolute weight) for each factor identify the driving genes/proteins/CpGs.

**Expected output:** Variance explained heatmap, factor-feature weight rankings per view.

---

## 3. MOFA2 Multi-Group Analysis for Condition Comparison

Compare latent factors across experimental conditions or patient groups.

```python
import pandas as pd
import numpy as np
from scipy.stats import mannwhitneyu, ttest_ind
from statsmodels.stats.multitest import multipletests

def mofa_group_comparison(factors_df, group_labels, group1, group2):
    """Compare MOFA factor values between two groups.

    Parameters:
        factors_df: DataFrame (samples x factors) from MOFA2
        group_labels: dict {sample: group_label} or Series
        group1, group2: group labels to compare
    Returns:
        DataFrame with test statistics per factor
    """
    if isinstance(group_labels, dict):
        group_labels = pd.Series(group_labels)

    g1_samples = group_labels[group_labels == group1].index
    g2_samples = group_labels[group_labels == group2].index
    g1_samples = g1_samples.intersection(factors_df.index)
    g2_samples = g2_samples.intersection(factors_df.index)

    results = []
    for factor in factors_df.columns:
        v1 = factors_df.loc[g1_samples, factor].values
        v2 = factors_df.loc[g2_samples, factor].values

        t_stat, t_pval = ttest_ind(v1, v2, equal_var=False)
        u_stat, u_pval = mannwhitneyu(v1, v2, alternative="two-sided")

        results.append({
            "factor": factor,
            "mean_g1": np.mean(v1),
            "mean_g2": np.mean(v2),
            "diff": np.mean(v2) - np.mean(v1),
            "t_stat": t_stat,
            "t_pval": t_pval,
            "u_stat": u_stat,
            "u_pval": u_pval,
        })

    res_df = pd.DataFrame(results)
    _, res_df["t_padj"], _, _ = multipletests(res_df["t_pval"], method="fdr_bh")
    _, res_df["u_padj"], _, _ = multipletests(res_df["u_pval"], method="fdr_bh")

    sig = res_df[res_df["t_padj"] < 0.05]
    print(f"Significant factors ({group1} vs {group2}): {len(sig)}")
    for _, row in sig.iterrows():
        print(f"  {row['factor']}: diff={row['diff']:.3f}, padj={row['t_padj']:.2e}")

    return res_df

# Usage
group_results = mofa_group_comparison(results["factors"], group_labels, "Disease", "Control")
```

**Expected output:** DataFrame with per-factor group differences, t-test and Mann-Whitney statistics, BH-adjusted p-values.

---

## 4. mixOmics DIABLO: Supervised Multi-Block Integration

Supervised multi-block PLS-DA for classification across multiple omics blocks.

```python
import subprocess
import pandas as pd

def run_diablo(layer_dict, labels, n_components=3, design_value=0.1,
               keepX_per_block=20, n_folds=5):
    """Run mixOmics DIABLO via R bridge.

    Parameters:
        layer_dict: dict of {layer_name: DataFrame (samples x features)}
        labels: Series with class labels indexed by sample
        n_components: number of latent components
        design_value: off-diagonal value in design matrix (0=unsupervised, 1=maximally supervised)
        keepX_per_block: features to keep per component per block
        n_folds: cross-validation folds
    Returns:
        dict with selected features, performance metrics
    """
    # Export data for R
    for name, df in layer_dict.items():
        df.to_csv(f"_diablo_{name}.csv")
    labels.to_csv("_diablo_labels.csv")
    block_names = list(layer_dict.keys())

    r_script = f'''
    library(mixOmics)

    # Load data
    blocks <- list()
    block_names <- c({", ".join([f'"{n}"' for n in block_names])})
    for (name in block_names) {{
        blocks[[name]] <- as.matrix(read.csv(paste0("_diablo_", name, ".csv"), row.names=1))
    }}
    Y <- factor(read.csv("_diablo_labels.csv", row.names=1)[,1])

    # Design matrix
    design <- matrix({design_value}, ncol=length(blocks), nrow=length(blocks),
                     dimnames=list(block_names, block_names))
    diag(design) <- 0

    # keepX
    keepX <- lapply(blocks, function(x) rep({keepX_per_block}, {n_components}))

    # Run DIABLO
    result <- block.splsda(blocks, Y, ncomp={n_components}, keepX=keepX, design=design)

    # Cross-validation
    perf <- perf(result, validation="Mfold", folds={n_folds}, nrepeat=10, cpus=2)

    # Export results
    for (name in block_names) {{
        selected <- selectVar(result, block=name, comp=1)$value
        write.csv(selected, paste0("_diablo_selected_", name, ".csv"))
    }}
    write.csv(data.frame(
        comp=1:{n_components},
        error_rate=perf$error.rate$overall[,"max.dist"]
    ), "_diablo_performance.csv", row.names=FALSE)
    '''

    with open("_diablo.R", "w") as f:
        f.write(r_script)
    subprocess.run(["Rscript", "_diablo.R"], check=True)

    # Read results
    selected = {}
    for name in block_names:
        selected[name] = pd.read_csv(f"_diablo_selected_{name}.csv", index_col=0)

    perf = pd.read_csv("_diablo_performance.csv")
    print(f"DIABLO performance (error rate): {perf['error_rate'].values}")

    return {"selected_features": selected, "performance": perf}

# Usage
diablo_results = run_diablo(
    {"RNA": rna_df, "Protein": prot_df, "Metabolite": metab_df},
    labels=patient_labels, n_components=3, keepX_per_block=20
)
```

**Key parameters:**
- `design_value`: 0.1 = weak supervision (let data speak), 1.0 = strong (maximize correlation between blocks).
- `keepX_per_block`: number of features selected per block per component. Start with 20-50.
- Cross-validation error rate < 0.3 indicates good classification performance.

**Expected output:** Selected features per block, error rates, and component scores.

---

## 5. mixOmics sPLS: Sparse PLS for Feature Selection

Sparse Partial Least Squares for feature selection across two omics layers.

```python
import subprocess
import pandas as pd

def run_spls(X_df, Y_df, x_name="RNA", y_name="Protein", n_components=3,
             keepX=50, keepY=50, mode="regression"):
    """Run mixOmics sPLS via R bridge.

    Parameters:
        X_df: DataFrame (samples x features) for first layer
        Y_df: DataFrame (samples x features) for second layer
        x_name, y_name: layer names for output
        n_components: number of latent components
        keepX, keepY: features to select per component
        mode: 'regression' (predict Y from X) or 'canonical' (maximize correlation)
    Returns:
        dict with selected features and correlation between components
    """
    X_df.to_csv("_spls_X.csv")
    Y_df.to_csv("_spls_Y.csv")

    r_script = f'''
    library(mixOmics)
    X <- as.matrix(read.csv("_spls_X.csv", row.names=1))
    Y <- as.matrix(read.csv("_spls_Y.csv", row.names=1))

    result <- spls(X, Y, ncomp={n_components}, mode="{mode}",
                   keepX=rep({keepX}, {n_components}),
                   keepY=rep({keepY}, {n_components}))

    # Selected features
    for (comp in 1:{n_components}) {{
        selX <- selectVar(result, comp=comp)$X$value
        selY <- selectVar(result, comp=comp)$Y$value
        write.csv(selX, paste0("_spls_selX_comp", comp, ".csv"))
        write.csv(selY, paste0("_spls_selY_comp", comp, ".csv"))
    }}

    # Component correlations
    cors <- sapply(1:{n_components}, function(k) cor(result$variates$X[,k], result$variates$Y[,k]))
    write.csv(data.frame(component=1:{n_components}, correlation=cors),
              "_spls_correlations.csv", row.names=FALSE)
    '''

    with open("_spls.R", "w") as f:
        f.write(r_script)
    subprocess.run(["Rscript", "_spls.R"], check=True)

    cors = pd.read_csv("_spls_correlations.csv")
    print(f"sPLS component correlations: {cors['correlation'].values}")

    return {"correlations": cors}

# Usage
spls_results = run_spls(rna_df, prot_df, keepX=50, keepY=50, mode="canonical")
```

**Expected output:** Selected features per component, component-wise correlations between X and Y variates.

---

## 6. SNF (Similarity Network Fusion)

Fuse per-omic patient similarity networks into a unified network for integrative clustering.

```python
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.cluster import SpectralClustering
from sklearn.metrics import silhouette_score

def snf(layer_dict, k=20, mu=0.5, n_iter=20):
    """Similarity Network Fusion for multi-omics integration.

    Parameters:
        layer_dict: dict of {layer_name: DataFrame (samples x features)}
        k: number of nearest neighbors for KNN kernel
        mu: hyperparameter controlling kernel width (0.3-0.8)
        n_iter: number of fusion iterations
    Returns:
        fused_similarity: fused similarity matrix (samples x samples)
        samples: sample names
    """
    samples = list(layer_dict.values())[0].index.tolist()
    n = len(samples)

    # Step 1: Compute per-omic similarity matrices
    similarities = []
    for name, df in layer_dict.items():
        X = df.loc[samples].values
        D = euclidean_distances(X)

        # Scaled exponential kernel
        epsilon = np.mean(np.sort(D, axis=1)[:, 1:k+1], axis=1)
        W = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                W[i, j] = np.exp(-D[i, j]**2 / (mu * epsilon[i] * epsilon[j]))
        np.fill_diagonal(W, 0)

        # Normalize
        row_sums = W.sum(axis=1, keepdims=True)
        W = W / (row_sums + 1e-10)
        similarities.append(W)
        print(f"  {name}: similarity matrix computed")

    # Step 2: KNN kernel (sparse version of similarity)
    def knn_kernel(W, k):
        Wk = np.zeros_like(W)
        for i in range(W.shape[0]):
            neighbors = np.argsort(W[i])[-k:]
            Wk[i, neighbors] = W[i, neighbors]
        # Symmetrize
        Wk = (Wk + Wk.T) / 2
        row_sums = Wk.sum(axis=1, keepdims=True)
        return Wk / (row_sums + 1e-10)

    knn_sims = [knn_kernel(W, k) for W in similarities]

    # Step 3: Iterative fusion
    fused = [W.copy() for W in similarities]
    m = len(similarities)
    for t in range(n_iter):
        new_fused = []
        for v in range(m):
            # Average of other views
            others = np.mean([fused[j] for j in range(m) if j != v], axis=0)
            # Update: P_v = S_v x (average of others) x S_v^T
            new_W = knn_sims[v] @ others @ knn_sims[v].T
            # Normalize
            row_sums = new_W.sum(axis=1, keepdims=True)
            new_W = new_W / (row_sums + 1e-10)
            new_fused.append(new_W)
        fused = new_fused

    # Final fused matrix = average across views
    fused_sim = np.mean(fused, axis=0)
    fused_sim = (fused_sim + fused_sim.T) / 2

    print(f"SNF complete: {n} samples, {m} views, {n_iter} iterations")
    return pd.DataFrame(fused_sim, index=samples, columns=samples), samples

def snf_cluster(fused_sim, k_range=(2, 8)):
    """Cluster patients from SNF fused similarity matrix.

    Parameters:
        fused_sim: DataFrame (samples x samples) fused similarity matrix
        k_range: range of cluster numbers to evaluate
    Returns:
        dict with labels and silhouette scores for each k
    """
    results = {}
    for k in range(k_range[0], k_range[1] + 1):
        labels = SpectralClustering(n_clusters=k, affinity="precomputed",
                                     random_state=42).fit_predict(fused_sim.values)
        sil = silhouette_score(1 - fused_sim.values, labels, metric="precomputed")
        results[k] = {"labels": pd.Series(labels, index=fused_sim.index), "silhouette": sil}
        print(f"  k={k}: silhouette={sil:.3f}")

    best_k = max(results, key=lambda k: results[k]["silhouette"])
    print(f"Best k={best_k} (silhouette={results[best_k]['silhouette']:.3f})")
    return results

# Usage
fused, samples = snf({"RNA": rna_df, "Protein": prot_df, "Methylation": meth_df}, k=20)
clusters = snf_cluster(fused, k_range=(2, 6))
```

**Key parameters:**
- `k=20`: KNN neighbors. Typical range 10-30. Larger k = smoother network.
- `mu=0.5`: kernel width. Range 0.3-0.8. Higher = broader similarity.
- `n_iter=20`: fusion iterations. Usually converges by 10-20.

**Expected output:** Fused similarity matrix and spectral clustering labels with silhouette scores.

---

## 7. MCIA (Multiple Co-Inertia Analysis)

Multi-table analysis for integrating more than 2 data types simultaneously.

```python
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from scipy.linalg import svd

def run_mcia(layer_dict, n_components=5):
    """Multiple Co-Inertia Analysis for multi-omics integration.

    Parameters:
        layer_dict: dict of {layer_name: DataFrame (samples x features)}
        n_components: number of components to extract
    Returns:
        dict with global scores, per-view scores, and pseudo-eigenvalues
    """
    samples = list(layer_dict.values())[0].index.tolist()
    views = list(layer_dict.keys())

    # Step 1: PCA per view (column-centered)
    view_scores = {}
    view_loadings = {}
    for name, df in layer_dict.items():
        X = df.loc[samples].values
        X_centered = X - X.mean(axis=0)
        pca = PCA(n_components=min(n_components, X.shape[0] - 1, X.shape[1]))
        scores = pca.fit_transform(X_centered)
        view_scores[name] = scores
        view_loadings[name] = pca.components_.T
        print(f"  {name}: {pca.n_components_} PCs, "
              f"var explained: {pca.explained_variance_ratio_.sum():.1%}")

    # Step 2: Concatenate PCA scores and run SVD for global compromise
    all_scores = np.hstack([view_scores[v] for v in views])
    U, s, Vt = svd(all_scores, full_matrices=False)

    n_comp = min(n_components, U.shape[1])
    global_scores = U[:, :n_comp] * s[:n_comp]

    # Step 3: Project back to per-view spaces
    projections = {}
    for i, name in enumerate(views):
        start = sum(view_scores[v].shape[1] for v in views[:i])
        end = start + view_scores[name].shape[1]
        proj = Vt[:n_comp, start:end].T
        projections[name] = pd.DataFrame(proj, columns=[f"MCIA{k+1}" for k in range(n_comp)])

    global_df = pd.DataFrame(global_scores, index=samples,
                              columns=[f"MCIA{k+1}" for k in range(n_comp)])

    pseudo_eigen = s[:n_comp]**2 / sum(s**2)
    print(f"\nMCIA pseudo-eigenvalues: {pseudo_eigen}")
    print(f"Cumulative variance: {pseudo_eigen.cumsum()}")

    return {
        "global_scores": global_df,
        "projections": projections,
        "pseudo_eigenvalues": pseudo_eigen,
    }

# Usage
mcia_results = run_mcia({"RNA": rna_df, "Protein": prot_df, "Metabolite": metab_df})
```

**Expected output:** Global compromise scores (samples x components), per-view projections, pseudo-eigenvalues.

---

## 8. iCluster+ for Integrative Clustering

Joint model-based clustering across multiple omics layers.

```python
import subprocess
import pandas as pd

def run_iclusterplus(layer_dict, k_range=(2, 5), lambda_values=None, n_cores=4):
    """Run iClusterPlus integrative clustering via R bridge.

    Parameters:
        layer_dict: dict of {layer_name: DataFrame (samples x features)}
        k_range: range of cluster numbers to evaluate
        lambda_values: regularization (None = auto-tune)
        n_cores: parallel cores
    Returns:
        dict with cluster labels and BIC for each k
    """
    block_names = list(layer_dict.keys())
    for name, df in layer_dict.items():
        df.to_csv(f"_icluster_{name}.csv")

    r_script = f'''
    library(iClusterPlus)

    blocks <- list()
    block_names <- c({", ".join([f'"{n}"' for n in block_names])})
    for (name in block_names) {{
        blocks[[name]] <- as.matrix(read.csv(paste0("_icluster_", name, ".csv"), row.names=1))
    }}

    results <- list()
    for (k in {k_range[0]}:{k_range[1]}) {{
        fit <- iClusterPlus(
            dt1=blocks[[1]], dt2=blocks[[2]],
            {"dt3=blocks[[3]]," if len(block_names) >= 3 else ""}
            type=rep("gaussian", length(blocks)),
            K=k, maxiter=50
        )
        results[[as.character(k)]] <- list(
            clusters=fit$clusters,
            BIC=fit$BIC
        )
        write.csv(data.frame(sample=rownames(blocks[[1]]),
                             cluster=fit$clusters),
                  paste0("_icluster_k", k, ".csv"), row.names=FALSE)
        cat("k=", k, " BIC=", fit$BIC, "\\n")
    }}

    bic_df <- data.frame(
        k={k_range[0]}:{k_range[1]},
        BIC=sapply(results, function(r) r$BIC)
    )
    write.csv(bic_df, "_icluster_bic.csv", row.names=FALSE)
    '''

    with open("_icluster.R", "w") as f:
        f.write(r_script)
    subprocess.run(["Rscript", "_icluster.R"], check=True)

    bic = pd.read_csv("_icluster_bic.csv")
    best_k = bic.loc[bic["BIC"].idxmin(), "k"]
    best_labels = pd.read_csv(f"_icluster_k{int(best_k)}.csv")

    print(f"Best k={int(best_k)} (BIC={bic['BIC'].min():.1f})")
    return {"bic": bic, "best_k": int(best_k), "labels": best_labels}

# Usage
icluster_results = run_iclusterplus(
    {"RNA": rna_df, "Protein": prot_df}, k_range=(2, 5)
)
```

**Expected output:** Cluster assignments for each k, BIC values for model selection.

---

## 9. Concatenation-Based Integration with Batch-Aware PCA

Simple early integration by concatenating omics layers with proper scaling and batch awareness.

```python
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

def concatenation_integration(layer_dict, n_pcs=30, scale_per_layer=True,
                               weight_by_features=False):
    """Early integration via feature concatenation with optional layer weighting.

    Parameters:
        layer_dict: dict of {layer_name: DataFrame (samples x features)}
        n_pcs: number of PCA components
        scale_per_layer: z-score normalize each layer independently
        weight_by_features: if True, weight each layer by 1/sqrt(n_features) to equalize contribution
    Returns:
        dict with PCA results and concatenated matrix
    """
    samples = sorted(set.intersection(*[set(df.index) for df in layer_dict.values()]))
    print(f"Shared samples: {len(samples)}")

    scaled_layers = {}
    for name, df in layer_dict.items():
        X = df.loc[samples].values
        if scale_per_layer:
            scaler = StandardScaler()
            X = scaler.fit_transform(X)
        if weight_by_features:
            X = X / np.sqrt(X.shape[1])
        scaled_layers[name] = pd.DataFrame(X, index=samples, columns=df.columns)
        print(f"  {name}: {X.shape[1]} features")

    # Concatenate
    concat = pd.concat(scaled_layers.values(), axis=1)
    concat.columns = [f"{name}:{feat}" for name, df in scaled_layers.items()
                      for feat in df.columns]

    # Handle NaN
    concat = concat.fillna(0)

    # PCA
    n_comp = min(n_pcs, concat.shape[0] - 1, concat.shape[1])
    pca = PCA(n_components=n_comp)
    scores = pca.fit_transform(concat.values)
    scores_df = pd.DataFrame(scores, index=samples,
                              columns=[f"PC{k+1}" for k in range(n_comp)])

    print(f"\nConcatenated: {concat.shape[1]} features total")
    print(f"PCA: {n_comp} components, cumulative variance: "
          f"{pca.explained_variance_ratio_.cumsum()[-1]:.1%}")

    # Per-layer contribution to PCs
    loadings = pd.DataFrame(pca.components_.T, index=concat.columns,
                             columns=scores_df.columns)
    for name in layer_dict:
        layer_cols = [c for c in loadings.index if c.startswith(f"{name}:")]
        contrib = loadings.loc[layer_cols].abs().mean()
        print(f"  {name} contribution to PC1: {contrib['PC1']:.4f}")

    return {"scores": scores_df, "pca": pca, "concat": concat, "loadings": loadings}

# Usage
concat_results = concatenation_integration(
    {"RNA": rna_df, "Protein": prot_df, "Methylation": meth_df},
    n_pcs=30, weight_by_features=True
)
```

**Key parameters:**
- `scale_per_layer=True`: essential to prevent high-dimensional layers from dominating.
- `weight_by_features=True`: equalizes layer contribution when feature counts differ greatly.

**Expected output:** PCA scores, loadings with layer prefixes, per-layer contribution metrics.

---

## 10. Cross-Omics Correlation Analysis

Feature-level correlation between two omics layers with FDR correction.

```python
import numpy as np
import pandas as pd
from scipy.stats import spearmanr, pearsonr
from statsmodels.stats.multitest import multipletests

def cross_omics_correlation(layer1, layer2, l1_name="RNA", l2_name="Protein",
                            method="spearman", top_n=100, fdr_thresh=0.05):
    """Compute feature-level correlations between two omics layers.

    Parameters:
        layer1, layer2: DataFrames (samples x features) with shared sample index
        l1_name, l2_name: layer names for output
        method: 'spearman' or 'pearson'
        top_n: number of most variable features per layer to test
        fdr_thresh: FDR threshold for significance
    Returns:
        DataFrame of significant cross-omics correlations
    """
    samples = sorted(set(layer1.index) & set(layer2.index))
    L1 = layer1.loc[samples]
    L2 = layer2.loc[samples]

    # Select top variable features
    var1 = L1.var().nlargest(top_n).index
    var2 = L2.var().nlargest(top_n).index
    L1, L2 = L1[var1], L2[var2]

    corr_func = spearmanr if method == "spearman" else pearsonr
    results = []
    for i, f1 in enumerate(var1):
        for j, f2 in enumerate(var2):
            x = L1[f1].values
            y = L2[f2].values
            valid = ~(np.isnan(x) | np.isnan(y))
            if valid.sum() < 5:
                continue
            r, p = corr_func(x[valid], y[valid])
            results.append({
                f"{l1_name}_feature": f1,
                f"{l2_name}_feature": f2,
                "r": r, "p": p
            })

    df = pd.DataFrame(results)
    if len(df) == 0:
        print("No valid correlations found")
        return df

    _, df["padj"], _, _ = multipletests(df["p"], method="fdr_bh")
    sig = df[df["padj"] < fdr_thresh].sort_values("padj")

    print(f"Cross-correlation ({l1_name} x {l2_name}): "
          f"{len(results)} pairs tested, {len(sig)} significant (FDR < {fdr_thresh})")
    print(f"Positive: {(sig['r'] > 0).sum()}, Negative: {(sig['r'] < 0).sum()}")

    return sig

# Usage
sig_correlations = cross_omics_correlation(rna_df, prot_df, l1_name="RNA", l2_name="Protein")
```

**Expected output:** DataFrame with significant feature pairs, correlation coefficients, and adjusted p-values.

---

## 11. Network-Based Integration: WGCNA Modules Across Omics

Weighted Gene Correlation Network Analysis applied across omics layers to find conserved modules.

```python
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform
import matplotlib.pyplot as plt

def wgcna_modules(df, power=6, min_module_size=30, merge_threshold=0.25):
    """WGCNA-style weighted correlation network module detection.

    Parameters:
        df: DataFrame (samples x features), z-score normalized
        power: soft-thresholding power (use pick_soft_threshold to determine)
        min_module_size: minimum features per module
        merge_threshold: merge modules with correlation > (1 - merge_threshold)
    Returns:
        dict with module assignments and eigengenes
    """
    # Correlation matrix
    corr = df.corr().values
    corr = np.abs(corr)

    # Adjacency matrix (soft thresholding)
    adj = np.power(corr, power)

    # Topological overlap matrix (TOM)
    n = adj.shape[0]
    k = adj.sum(axis=1) - np.diag(adj)
    tom = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            num = np.sum(adj[i, :] * adj[:, j]) + adj[i, j]
            denom = min(k[i], k[j]) + 1 - adj[i, j]
            tom[i, j] = tom[j, i] = num / denom if denom > 0 else 0

    # Distance = 1 - TOM
    dist = 1 - tom
    np.fill_diagonal(dist, 0)
    dist = np.clip(dist, 0, None)

    # Hierarchical clustering
    condensed = squareform(dist)
    Z = linkage(condensed, method="average")
    labels = fcluster(Z, t=min_module_size, criterion="maxclust")

    # Assign modules (filter small modules)
    module_map = pd.Series(labels, index=df.columns)
    module_sizes = module_map.value_counts()
    small = module_sizes[module_sizes < min_module_size].index
    module_map[module_map.isin(small)] = 0  # unassigned

    # Compute module eigengenes (PC1 of each module)
    from sklearn.decomposition import PCA
    eigengenes = {}
    for mod in sorted(module_map.unique()):
        if mod == 0:
            continue
        mod_features = module_map[module_map == mod].index
        pca = PCA(n_components=1)
        eigengenes[f"ME{mod}"] = pca.fit_transform(df[mod_features].values)[:, 0]

    eigengene_df = pd.DataFrame(eigengenes, index=df.index)

    print(f"Modules detected: {len(eigengenes)}")
    for mod in sorted(module_map.unique()):
        if mod == 0:
            continue
        print(f"  Module {mod}: {(module_map == mod).sum()} features")

    return {"modules": module_map, "eigengenes": eigengene_df}


def cross_omics_module_preservation(modules_layer1, df_layer2, n_perms=100):
    """Test module preservation across omics layers.

    Parameters:
        modules_layer1: Series mapping features to module labels (from layer 1)
        df_layer2: DataFrame (samples x features) for layer 2
        n_perms: permutations for significance testing
    Returns:
        DataFrame with preservation Z-scores per module
    """
    results = []
    for mod in sorted(modules_layer1.unique()):
        if mod == 0:
            continue
        mod_genes = modules_layer1[modules_layer1 == mod].index
        # Find matching features in layer 2 (by gene name)
        shared = [g for g in mod_genes if g in df_layer2.columns]
        if len(shared) < 3:
            continue

        # Observed module connectivity
        obs_corr = df_layer2[shared].corr().values
        obs_connectivity = np.mean(np.abs(obs_corr[np.triu_indices_from(obs_corr, k=1)]))

        # Permutation test
        perm_conn = []
        for _ in range(n_perms):
            random_genes = np.random.choice(df_layer2.columns, len(shared), replace=False)
            perm_corr = df_layer2[random_genes].corr().values
            perm_conn.append(np.mean(np.abs(perm_corr[np.triu_indices_from(perm_corr, k=1)])))

        z = (obs_connectivity - np.mean(perm_conn)) / (np.std(perm_conn) + 1e-10)
        results.append({
            "module": mod, "n_features": len(shared),
            "connectivity": obs_connectivity, "zscore": z,
            "preserved": z > 2
        })

    pres_df = pd.DataFrame(results)
    n_preserved = pres_df["preserved"].sum()
    print(f"Module preservation: {n_preserved}/{len(pres_df)} modules preserved (Z > 2)")
    return pres_df

# Usage
rna_modules = wgcna_modules(rna_df, power=6, min_module_size=30)
preservation = cross_omics_module_preservation(rna_modules["modules"], prot_df)
```

**Key parameters:**
- `power`: soft-thresholding power. Use `pick_soft_threshold()` to find scale-free topology fit R^2 > 0.8.
- `min_module_size=30`: minimum features per module. Increase for noisy data.
- Preservation Z > 2: module is preserved across omics layers. Z > 10: highly preserved.

**Expected output:** Module assignments, eigengene matrix, cross-omics preservation Z-scores.

---

## 12. Evaluation: Silhouette Scores, Survival Association, Known Biology

Evaluate integration quality using multiple complementary metrics.

```python
import numpy as np
import pandas as pd
from sklearn.metrics import silhouette_score, adjusted_rand_score
from scipy.stats import chi2_contingency

def evaluate_integration(scores_df, cluster_labels, known_labels=None,
                         survival_df=None, pathway_genes=None, layer_dict=None):
    """Comprehensive evaluation of multi-omics integration results.

    Parameters:
        scores_df: DataFrame (samples x components) from integration method
        cluster_labels: Series with cluster assignments
        known_labels: Series with known biology labels (e.g., subtype) for ARI
        survival_df: DataFrame with 'time' and 'event' columns for survival analysis
        pathway_genes: dict of {pathway: gene_list} for biology enrichment
        layer_dict: original omics layers for per-layer concordance
    Returns:
        dict with evaluation metrics
    """
    metrics = {}

    # 1. Silhouette score
    sil = silhouette_score(scores_df.values, cluster_labels.loc[scores_df.index].values)
    metrics["silhouette"] = sil
    print(f"Silhouette score: {sil:.3f}")

    # 2. Adjusted Rand Index (if known labels available)
    if known_labels is not None:
        shared = cluster_labels.index.intersection(known_labels.index)
        ari = adjusted_rand_score(known_labels.loc[shared], cluster_labels.loc[shared])
        metrics["ARI"] = ari
        print(f"Adjusted Rand Index vs known labels: {ari:.3f}")

    # 3. Survival association (log-rank test)
    if survival_df is not None:
        try:
            from lifelines.statistics import logrank_test
            shared = cluster_labels.index.intersection(survival_df.index)
            clusters = cluster_labels.loc[shared].unique()
            if len(clusters) == 2:
                g1 = shared[cluster_labels.loc[shared] == clusters[0]]
                g2 = shared[cluster_labels.loc[shared] == clusters[1]]
                lr = logrank_test(
                    survival_df.loc[g1, "time"], survival_df.loc[g2, "time"],
                    survival_df.loc[g1, "event"], survival_df.loc[g2, "event"]
                )
                metrics["logrank_p"] = lr.p_value
                print(f"Log-rank p-value: {lr.p_value:.2e}")
        except ImportError:
            print("  lifelines not installed; skipping survival analysis")

    # 4. Per-layer concordance (do clusters separate in each individual layer?)
    if layer_dict is not None:
        from sklearn.metrics import silhouette_score as sil_score
        for name, df in layer_dict.items():
            shared = cluster_labels.index.intersection(df.index)
            if len(shared) < 10:
                continue
            try:
                s = sil_score(df.loc[shared].values, cluster_labels.loc[shared].values)
                metrics[f"silhouette_{name}"] = s
                print(f"  Per-layer silhouette ({name}): {s:.3f}")
            except Exception:
                pass

    # 5. Cluster-label association (chi-square)
    if known_labels is not None:
        ct = pd.crosstab(cluster_labels.loc[shared], known_labels.loc[shared])
        chi2, p, _, _ = chi2_contingency(ct)
        metrics["chi2_p"] = p
        print(f"Chi-square association with known labels: p={p:.2e}")

    return metrics

# Usage
eval_metrics = evaluate_integration(
    scores_df=results["factors"],
    cluster_labels=cluster_assignments,
    known_labels=known_subtypes,
    survival_df=survival_data,
    layer_dict={"RNA": rna_df, "Protein": prot_df}
)
```

**Key parameters:**
- Silhouette > 0.3: reasonable clustering structure. > 0.5: strong.
- ARI > 0.5: good agreement with known subtypes. ARI = 1: perfect.
- Log-rank p < 0.05: clusters have significantly different survival.

**Expected output:** Dictionary with silhouette scores (overall and per-layer), ARI, log-rank p-value, chi-square association.

---

## Quick Reference

| Task | Recipe | Key function |
|------|--------|-------------|
| MOFA2 training | #1 | `mofapy2.run.entry_point` |
| MOFA2 interpretation | #2 | Variance explained + top weights |
| MOFA2 group comparison | #3 | t-test / Mann-Whitney per factor |
| DIABLO (supervised) | #4 | `block.splsda()` (R) |
| sPLS (two-layer) | #5 | `spls()` (R) |
| SNF (network fusion) | #6 | Kernel similarity + iterative fusion |
| MCIA | #7 | Multi-table SVD |
| iCluster+ | #8 | `iClusterPlus()` (R) |
| Concatenation + PCA | #9 | `StandardScaler` + `PCA` |
| Cross-omics correlation | #10 | `spearmanr` + FDR |
| WGCNA modules | #11 | Soft-thresholded TOM + clustering |
| Evaluation metrics | #12 | Silhouette, ARI, survival, per-layer |

---

## Cross-Skill Routing

- Per-layer preprocessing (proteomics) --> `proteomics-analysis`
- Per-layer preprocessing (methylation) --> `epigenomics`
- Per-layer preprocessing (metabolomics) --> `metabolomics-analysis`
- Pathway enrichment on factor loadings --> `gene-enrichment`
- Network visualization --> `systems-biology`
- Disease context for integration results --> `multiomic-disease-characterization`
