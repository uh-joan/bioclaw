# Proteomics Recipes

Python code templates for proteomics data analysis: protein abundance, differential expression, fold change, PCA, and clustering.

Cross-skill routing: use `proteomics-analysis` for conceptual guidance, `biostat-recipes` for statistical tests, `enrichment-recipes` for pathway analysis of differential proteins.

---

## 1. Loading Proteomics Data

```python
import pandas as pd
import numpy as np

def load_proteomics(filepath: str, index_col: int = 0) -> pd.DataFrame:
    """Load proteomics expression matrix (rows = proteins, cols = samples)."""
    prot = pd.read_csv(filepath, index_col=index_col)
    print(f"Loaded {prot.shape[0]} proteins x {prot.shape[1]} samples")
    print(f"Missing values: {prot.isna().sum().sum()} ({prot.isna().mean().mean()*100:.1f}%)")
    return prot

prot = load_proteomics('proteomics_data.csv')

# Define sample groups
tumor_cols = [c for c in prot.columns if c.startswith('Tumor')]
normal_cols = [c for c in prot.columns if c.startswith('Normal')]

# From metadata
meta = pd.read_csv('sample_metadata.csv')
tumor_cols = meta[meta['condition'] == 'tumor']['sample_id'].tolist()
normal_cols = meta[meta['condition'] == 'normal']['sample_id'].tolist()

# Handle missing values
def filter_missing(prot: pd.DataFrame, max_missing_frac: float = 0.5) -> pd.DataFrame:
    """Remove proteins with too many missing values."""
    thresh = int(prot.shape[1] * (1 - max_missing_frac))
    filtered = prot.dropna(thresh=thresh)
    print(f"Kept {filtered.shape[0]}/{prot.shape[0]} proteins (>= {thresh} non-NA values)")
    return filtered

# Impute remaining NAs
def impute_min(prot: pd.DataFrame, fraction: float = 0.5) -> pd.DataFrame:
    """Impute missing values with fraction of column minimum."""
    filled = prot.copy()
    for col in filled.columns:
        col_min = filled[col].min()
        filled[col] = filled[col].fillna(col_min * fraction)
    return filled
```

---

## 2. Log2 Transformation and Normalization

```python
def log2_transform(prot: pd.DataFrame, pseudocount: float = 1.0) -> pd.DataFrame:
    """Log2 transform with pseudocount."""
    return np.log2(prot + pseudocount)

prot_log2 = log2_transform(prot)

# Median normalization (center each sample to common median)
def median_normalize(prot_log2: pd.DataFrame) -> pd.DataFrame:
    """Subtract per-sample median to normalize across samples."""
    return prot_log2.subtract(prot_log2.median(axis=0), axis=1)

prot_norm = median_normalize(prot_log2)

# Quantile normalization
def quantile_normalize(df: pd.DataFrame) -> pd.DataFrame:
    """Quantile normalization across samples."""
    rank_mean = df.stack().groupby(
        df.rank(method='first').stack().astype(int)
    ).mean()
    return df.rank(method='min').stack().astype(int).map(rank_mean).unstack()

# Z-score normalization (per protein)
def zscore_normalize(prot: pd.DataFrame) -> pd.DataFrame:
    """Z-score normalization per protein (row-wise)."""
    return prot.subtract(prot.mean(axis=1), axis=0).div(prot.std(axis=1), axis=0)
```

---

## 3. Differential Protein Abundance

```python
from scipy.stats import ttest_ind

def differential_abundance(prot: pd.DataFrame, tumor_cols: list,
                            normal_cols: list,
                            equal_var: bool = False) -> pd.DataFrame:
    """t-test for differential protein abundance (tumor vs normal).
    Uses Welch's t-test by default.
    """
    results = []
    for protein in prot.index:
        tumor_vals = prot.loc[protein, tumor_cols].astype(float).dropna()
        normal_vals = prot.loc[protein, normal_cols].astype(float).dropna()

        if len(tumor_vals) < 2 or len(normal_vals) < 2:
            continue

        t_stat, pval = ttest_ind(tumor_vals, normal_vals, equal_var=equal_var)

        mean_tumor = tumor_vals.mean()
        mean_normal = normal_vals.mean()
        fc = mean_tumor / mean_normal if mean_normal != 0 else np.nan
        log2fc = np.log2(fc) if fc is not None and fc > 0 else np.nan

        results.append({
            'protein': protein,
            'mean_tumor': mean_tumor,
            'mean_normal': mean_normal,
            'fold_change': fc,
            'log2FC': log2fc,
            't_stat': t_stat,
            'pval': pval,
        })

    return pd.DataFrame(results).set_index('protein')

results_df = differential_abundance(prot_log2, tumor_cols, normal_cols)
```

### Non-parametric (Mann-Whitney U)

```python
from scipy.stats import mannwhitneyu

def differential_abundance_mw(prot: pd.DataFrame, group1_cols: list,
                                group2_cols: list) -> pd.DataFrame:
    """Non-parametric differential abundance."""
    results = []
    for protein in prot.index:
        g1 = prot.loc[protein, group1_cols].astype(float).dropna().values
        g2 = prot.loc[protein, group2_cols].astype(float).dropna().values
        if len(g1) < 2 or len(g2) < 2:
            continue
        try:
            U, pval = mannwhitneyu(g1, g2, alternative='two-sided')
        except ValueError:
            U, pval = np.nan, np.nan
        results.append({'protein': protein, 'U': U, 'pval': pval})
    return pd.DataFrame(results).set_index('protein')
```

---

## 4. Multiple Testing Correction

```python
from statsmodels.stats.multitest import multipletests

def apply_fdr(results_df: pd.DataFrame, pval_col: str = 'pval',
               method: str = 'fdr_bh') -> pd.DataFrame:
    """Apply FDR correction to p-values."""
    df = results_df.copy()
    valid = df[pval_col].notna()
    _, df.loc[valid, 'padj'], _, _ = multipletests(
        df.loc[valid, pval_col].values, method=method
    )
    return df

results_df = apply_fdr(results_df)

# Summary
sig = results_df[(results_df['padj'] < 0.05) & (results_df['log2FC'].abs() > 1)]
print(f"Significant proteins (FDR < 0.05, |log2FC| > 1): {len(sig)}")
print(f"  Upregulated in tumor: {(sig['log2FC'] > 0).sum()}")
print(f"  Downregulated in tumor: {(sig['log2FC'] < 0).sum()}")
```

---

## 5. Extract Specific Protein

```python
def lookup_protein(prot: pd.DataFrame, gene_symbol: str,
                    tumor_cols: list, normal_cols: list) -> dict:
    """Look up a protein by gene symbol and compute fold change."""
    matches = prot.loc[prot.index.str.contains(gene_symbol, case=False)]
    if matches.empty:
        return {'found': False, 'gene': gene_symbol}

    row = matches.iloc[0]
    protein_id = matches.index[0]

    normal_mean = row[normal_cols].astype(float).mean()
    tumor_mean = row[tumor_cols].astype(float).mean()
    fc = tumor_mean / normal_mean if normal_mean != 0 else np.nan
    log2fc = np.log2(fc) if fc and fc > 0 else np.nan

    return {
        'found': True,
        'protein_id': protein_id,
        'gene': gene_symbol,
        'normal_mean': normal_mean,
        'tumor_mean': tumor_mean,
        'fold_change': fc,
        'log2FC': log2fc,
        'normal_values': row[normal_cols].astype(float).tolist(),
        'tumor_values': row[tumor_cols].astype(float).tolist(),
    }

# Usage
eno1 = lookup_protein(prot_log2, 'ENO1', tumor_cols, normal_cols)
print(f"ENO1 fold change: {eno1['fold_change']:.2f} (log2FC: {eno1['log2FC']:.2f})")

# Batch lookup
genes_of_interest = ['ENO1', 'GAPDH', 'TP53', 'EGFR', 'BRCA1']
for gene in genes_of_interest:
    info = lookup_protein(prot_log2, gene, tumor_cols, normal_cols)
    if info['found']:
        print(f"  {gene}: FC={info['fold_change']:.2f}, log2FC={info['log2FC']:.2f}")
    else:
        print(f"  {gene}: not found")
```

---

## 6. Volcano Plot for Proteomics

```python
import matplotlib.pyplot as plt

def volcano_plot(results_df: pd.DataFrame, fc_col: str = 'log2FC',
                  pval_col: str = 'padj', alpha: float = 0.05,
                  fc_thresh: float = 1.0, figsize: tuple = (10, 8),
                  title: str = 'Proteomics Volcano Plot') -> plt.Figure:
    """Volcano plot with significance and fold change thresholds."""
    fig, ax = plt.subplots(figsize=figsize)

    df = results_df.dropna(subset=[fc_col, pval_col])
    log10p = -np.log10(df[pval_col].clip(lower=1e-300))
    fc = df[fc_col]

    colors = []
    for p, f in zip(df[pval_col], fc):
        if p < alpha and f > fc_thresh:
            colors.append('red')
        elif p < alpha and f < -fc_thresh:
            colors.append('blue')
        elif p < alpha:
            colors.append('orange')
        else:
            colors.append('gray')

    ax.scatter(fc, log10p, c=colors, alpha=0.5, s=10, edgecolors='none')

    ax.axhline(-np.log10(alpha), color='black', linestyle='--', linewidth=0.5)
    ax.axvline(fc_thresh, color='black', linestyle='--', linewidth=0.5)
    ax.axvline(-fc_thresh, color='black', linestyle='--', linewidth=0.5)

    ax.set_xlabel('Log2 Fold Change')
    ax.set_ylabel('-Log10 Adjusted P-value')
    ax.set_title(title)

    n_up = sum(1 for c in colors if c == 'red')
    n_down = sum(1 for c in colors if c == 'blue')
    ax.text(0.02, 0.98, f'Up: {n_up}\nDown: {n_down}',
            transform=ax.transAxes, va='top', fontsize=10)

    plt.tight_layout()
    return fig

# Label top hits
def volcano_with_labels(results_df: pd.DataFrame, top_n: int = 10, **kwargs):
    """Volcano plot with top proteins labeled."""
    fig = volcano_plot(results_df, **kwargs)
    ax = fig.axes[0]

    top = results_df.dropna(subset=['padj']).nsmallest(top_n, 'padj')
    for protein_id, row in top.iterrows():
        ax.annotate(protein_id,
                     (row['log2FC'], -np.log10(row['padj'])),
                     fontsize=7, alpha=0.8,
                     arrowprops=dict(arrowstyle='-', alpha=0.3))
    return fig

fig = volcano_with_labels(results_df, top_n=15)
fig.savefig('proteomics_volcano.png', dpi=150, bbox_inches='tight')
```

---

## 7. PCA on Proteomics Data

```python
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

def pca_proteomics(prot_log2: pd.DataFrame, meta: pd.DataFrame = None,
                    group_col: str = 'condition',
                    n_components: int = 2) -> dict:
    """PCA on proteomics data (samples as observations)."""
    # Transpose: samples as rows, proteins as features
    X = prot_log2.dropna().T
    pca = PCA(n_components=n_components)
    coords = pca.fit_transform(X)

    result = {
        'coords': pd.DataFrame(coords, index=X.index,
                                 columns=[f'PC{i+1}' for i in range(n_components)]),
        'explained_variance': pca.explained_variance_ratio_,
        'loadings': pd.DataFrame(pca.components_.T, index=X.columns,
                                   columns=[f'PC{i+1}' for i in range(n_components)]),
        'pca_model': pca,
    }
    return result

pca_result = pca_proteomics(prot_log2)

# Plot
def plot_pca(pca_result: dict, sample_groups: dict[str, list[str]],
              figsize: tuple = (8, 6)) -> plt.Figure:
    """PCA scatter plot colored by group."""
    fig, ax = plt.subplots(figsize=figsize)
    coords = pca_result['coords']
    var = pca_result['explained_variance']

    colors = {'tumor': 'red', 'normal': 'blue'}
    for group, samples in sample_groups.items():
        mask = coords.index.isin(samples)
        ax.scatter(coords.loc[mask, 'PC1'], coords.loc[mask, 'PC2'],
                    label=group, c=colors.get(group, 'gray'), alpha=0.7, s=50)

    ax.set_xlabel(f'PC1 ({var[0]*100:.1f}%)')
    ax.set_ylabel(f'PC2 ({var[1]*100:.1f}%)')
    ax.set_title('PCA - Proteomics')
    ax.legend()
    plt.tight_layout()
    return fig

fig = plot_pca(pca_result, {'tumor': tumor_cols, 'normal': normal_cols})
fig.savefig('proteomics_pca.png', dpi=150, bbox_inches='tight')

# Top contributing proteins per PC
def top_loadings(pca_result: dict, pc: str = 'PC1', top_n: int = 20) -> pd.DataFrame:
    """Proteins with highest absolute loadings on a given PC."""
    loadings = pca_result['loadings'][pc].abs().sort_values(ascending=False)
    return loadings.head(top_n)
```

---

## 8. Hierarchical Clustering

```python
import scipy.cluster.hierarchy as sch
import matplotlib.pyplot as plt

def hierarchical_clustering(prot_log2: pd.DataFrame, method: str = 'ward',
                             metric: str = 'euclidean',
                             n_clusters: int = 3) -> dict:
    """Hierarchical clustering of samples."""
    X = prot_log2.dropna().T  # samples as rows
    linkage = sch.linkage(X, method=method, metric=metric)
    clusters = sch.fcluster(linkage, t=n_clusters, criterion='maxclust')

    return {
        'linkage': linkage,
        'clusters': pd.Series(clusters, index=X.index, name='cluster'),
        'n_clusters': n_clusters,
    }

clust = hierarchical_clustering(prot_log2, n_clusters=3)
print(clust['clusters'].value_counts())

# Dendrogram
def plot_dendrogram(clust_result: dict, figsize: tuple = (12, 6),
                     title: str = 'Sample Clustering') -> plt.Figure:
    """Plot dendrogram from hierarchical clustering."""
    fig, ax = plt.subplots(figsize=figsize)
    sch.dendrogram(clust_result['linkage'],
                    labels=clust_result['clusters'].index.tolist(),
                    leaf_rotation=90, leaf_font_size=8, ax=ax)
    ax.set_title(title)
    ax.set_ylabel('Distance')
    plt.tight_layout()
    return fig

fig = plot_dendrogram(clust)
fig.savefig('proteomics_dendrogram.png', dpi=150, bbox_inches='tight')

# Heatmap with clustering
def clustered_heatmap(prot_log2: pd.DataFrame, top_n: int = 50,
                       figsize: tuple = (14, 10)) -> plt.Figure:
    """Heatmap of top variable proteins with hierarchical clustering."""
    # Select top variable proteins
    var = prot_log2.var(axis=1).nlargest(top_n)
    subset = prot_log2.loc[var.index].dropna()

    # Cluster rows and columns
    row_linkage = sch.linkage(subset, method='ward')
    col_linkage = sch.linkage(subset.T, method='ward')
    row_order = sch.leaves_list(row_linkage)
    col_order = sch.leaves_list(col_linkage)

    ordered = subset.iloc[row_order, col_order]

    fig, ax = plt.subplots(figsize=figsize)
    im = ax.imshow(ordered, aspect='auto', cmap='RdBu_r')
    ax.set_yticks(range(len(ordered.index)))
    ax.set_yticklabels(ordered.index, fontsize=6)
    ax.set_xticks(range(len(ordered.columns)))
    ax.set_xticklabels(ordered.columns, rotation=90, fontsize=6)
    plt.colorbar(im, ax=ax, label='Log2 Abundance')
    ax.set_title(f'Top {top_n} Variable Proteins')
    plt.tight_layout()
    return fig
```
