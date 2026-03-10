# miRNA Recipes

Python code templates for miRNA differential expression analysis, fold change, multiple testing correction, and visualization.

Cross-skill routing: use `biostat-recipes` for general statistical tests, `deseq2-recipes` if using DESeq2 for miRNA DE.

---

## 1. Loading miRNA Expression Data

```python
import pandas as pd
import numpy as np

def load_mirna_expression(filepath: str, index_col: int = 0) -> pd.DataFrame:
    """Load miRNA expression matrix (rows = miRNAs, cols = samples)."""
    mirna = pd.read_csv(filepath, index_col=index_col)
    print(f"Loaded {mirna.shape[0]} miRNAs x {mirna.shape[1]} samples")
    return mirna

# From tab-delimited
mirna = pd.read_csv('mirna_counts.tsv', sep='\t', index_col=0)

# Define sample groups
patient_cols = [c for c in mirna.columns if c.startswith('Patient')]
control_cols = [c for c in mirna.columns if c.startswith('Control')]

# Or from a metadata file
meta = pd.read_csv('sample_metadata.csv')
patient_cols = meta[meta['group'] == 'patient']['sample_id'].tolist()
control_cols = meta[meta['group'] == 'control']['sample_id'].tolist()
```

---

## 2. Log2 Transformation

```python
def log2_transform(df: pd.DataFrame, pseudocount: float = 1.0) -> pd.DataFrame:
    """Log2 transform with pseudocount to handle zeros."""
    return np.log2(df + pseudocount)

mirna_log2 = log2_transform(mirna)

# CPM normalization before log2
def cpm_log2(df: pd.DataFrame, pseudocount: float = 1.0) -> pd.DataFrame:
    """Counts per million then log2 transform."""
    cpm = df.div(df.sum(axis=0), axis=1) * 1e6
    return np.log2(cpm + pseudocount)

mirna_cpm_log2 = cpm_log2(mirna)

# Quantile normalization
def quantile_normalize(df: pd.DataFrame) -> pd.DataFrame:
    """Quantile normalization across samples."""
    rank_mean = df.stack().groupby(
        df.rank(method='first').stack().astype(int)
    ).mean()
    return df.rank(method='min').stack().astype(int).map(rank_mean).unstack()
```

---

## 3. Differential Expression (t-test per miRNA)

```python
from scipy.stats import ttest_ind

def de_ttest(mirna: pd.DataFrame, patient_cols: list, control_cols: list,
             equal_var: bool = False) -> pd.DataFrame:
    """Differential expression via t-test for each miRNA.
    Uses Welch's t-test by default (equal_var=False).
    """
    results = []
    for mirna_id in mirna.index:
        patient_vals = mirna.loc[mirna_id, patient_cols].astype(float)
        control_vals = mirna.loc[mirna_id, control_cols].astype(float)
        t_stat, pval = ttest_ind(patient_vals, control_vals, equal_var=equal_var)
        results.append({
            'mirna': mirna_id,
            'mean_patient': patient_vals.mean(),
            'mean_control': control_vals.mean(),
            't_stat': t_stat,
            'pval': pval,
        })
    return pd.DataFrame(results).set_index('mirna')

de_results = de_ttest(mirna_log2, patient_cols, control_cols)
```

### Non-parametric alternative (Mann-Whitney U)

```python
from scipy.stats import mannwhitneyu

def de_mannwhitney(mirna: pd.DataFrame, patient_cols: list,
                    control_cols: list) -> pd.DataFrame:
    """Non-parametric DE using Mann-Whitney U test."""
    results = []
    for mirna_id in mirna.index:
        p_vals = mirna.loc[mirna_id, patient_cols].astype(float).values
        c_vals = mirna.loc[mirna_id, control_cols].astype(float).values
        try:
            U, pval = mannwhitneyu(p_vals, c_vals, alternative='two-sided')
        except ValueError:
            U, pval = np.nan, np.nan
        results.append({'mirna': mirna_id, 'U': U, 'pval': pval})
    return pd.DataFrame(results).set_index('mirna')
```

---

## 4. Multiple Testing Correction

```python
from statsmodels.stats.multitest import multipletests

def apply_corrections(pvals: np.ndarray) -> pd.DataFrame:
    """Apply Bonferroni, BH, and Holm corrections."""
    corrections = {}

    # Bonferroni
    _, padj_bonf, _, _ = multipletests(pvals, method='bonferroni')
    corrections['padj_bonferroni'] = padj_bonf

    # Benjamini-Hochberg (FDR)
    _, padj_bh, _, _ = multipletests(pvals, method='fdr_bh')
    corrections['padj_bh'] = padj_bh

    # Holm
    _, padj_holm, _, _ = multipletests(pvals, method='holm')
    corrections['padj_holm'] = padj_holm

    return pd.DataFrame(corrections)

# Apply to DE results
pvals = de_results['pval'].values
corrections = apply_corrections(pvals)
de_results = pd.concat([de_results, corrections], axis=1)
```

---

## 5. Counting Significant miRNAs

```python
def count_significant(de_results: pd.DataFrame, alpha: float = 0.05) -> dict:
    """Count significant miRNAs before and after correction."""
    counts = {
        'raw_p < 0.05': (de_results['pval'] < alpha).sum(),
        'raw_p < 0.01': (de_results['pval'] < 0.01).sum(),
    }

    for method in ['padj_bonferroni', 'padj_bh', 'padj_holm']:
        if method in de_results.columns:
            counts[f'{method} < {alpha}'] = (de_results[method] < alpha).sum()

    # Ratio of BH to Bonferroni significant
    sig_bh = (de_results['padj_bh'] < alpha).sum()
    sig_bonf = (de_results['padj_bonferroni'] < alpha).sum()
    counts['bh_to_bonf_ratio'] = sig_bh / sig_bonf if sig_bonf > 0 else float('inf')

    return counts

sig_counts = count_significant(de_results)
for method, n in sig_counts.items():
    print(f"  {method}: {n}")
```

---

## 6. Log2 Fold Change Calculation

```python
def calc_log2fc(mirna: pd.DataFrame, patient_cols: list,
                control_cols: list, pseudocount: float = 1.0) -> pd.Series:
    """Log2 fold change: log2(mean_patient + pc) - log2(mean_control + pc)."""
    mean_patient = mirna[patient_cols].mean(axis=1)
    mean_control = mirna[control_cols].mean(axis=1)
    log2fc = np.log2(mean_patient + pseudocount) - np.log2(mean_control + pseudocount)
    return log2fc

de_results['log2FC'] = calc_log2fc(mirna, patient_cols, control_cols)

# Classify direction
de_results['direction'] = np.where(de_results['log2FC'] > 0, 'up', 'down')

# Filter significant with fold change threshold
sig_de = de_results[
    (de_results['padj_bh'] < 0.05) &
    (de_results['log2FC'].abs() > 1.0)
]
print(f"Significant DE miRNAs (|log2FC| > 1, FDR < 0.05): {len(sig_de)}")
print(f"  Upregulated: {(sig_de['direction'] == 'up').sum()}")
print(f"  Downregulated: {(sig_de['direction'] == 'down').sum()}")
```

---

## 7. ANOVA Across Cell Types

```python
from scipy.stats import f_oneway

def anova_cell_types(mirna: pd.DataFrame,
                      cell_type_groups: dict[str, list[str]]) -> pd.DataFrame:
    """One-way ANOVA for each miRNA across cell types.
    cell_type_groups: {'T_cell': [col1, col2], 'B_cell': [col3, col4], ...}
    """
    results = []
    for mirna_id in mirna.index:
        groups = [mirna.loc[mirna_id, cols].astype(float).values
                  for cols in cell_type_groups.values()]
        # Need at least 2 groups with variance
        valid_groups = [g for g in groups if len(g) >= 2 and np.std(g) > 0]
        if len(valid_groups) >= 2:
            F, pval = f_oneway(*valid_groups)
        else:
            F, pval = np.nan, np.nan
        results.append({'mirna': mirna_id, 'F_stat': F, 'pval': pval})

    res_df = pd.DataFrame(results).set_index('mirna')
    _, res_df['padj_bh'], _, _ = multipletests(
        res_df['pval'].fillna(1).values, method='fdr_bh'
    )
    return res_df

# Usage
cell_type_groups = {
    'T_cell': ['T1', 'T2', 'T3'],
    'B_cell': ['B1', 'B2', 'B3'],
    'Monocyte': ['M1', 'M2', 'M3'],
    'NK': ['NK1', 'NK2', 'NK3'],
}
anova_results = anova_cell_types(mirna_log2, cell_type_groups)
sig_anova = anova_results[anova_results['padj_bh'] < 0.05]
```

---

## 8. Pairwise Cell Type Comparison (Log2 FC)

```python
from itertools import combinations

def pairwise_log2fc(mirna: pd.DataFrame,
                     cell_type_groups: dict[str, list[str]],
                     pseudocount: float = 1.0) -> pd.DataFrame:
    """Compute median log2 FC between all pairs of cell types."""
    cell_types = list(cell_type_groups.keys())
    results = []

    for ct1, ct2 in combinations(cell_types, 2):
        mean1 = mirna[cell_type_groups[ct1]].mean(axis=1)
        mean2 = mirna[cell_type_groups[ct2]].mean(axis=1)
        log2fc = np.log2(mean1 + pseudocount) - np.log2(mean2 + pseudocount)
        results.append({
            'comparison': f'{ct1}_vs_{ct2}',
            'median_log2FC': log2fc.median(),
            'mean_log2FC': log2fc.mean(),
            'n_up': (log2fc > 0).sum(),
            'n_down': (log2fc < 0).sum(),
        })

    return pd.DataFrame(results)

# Per-miRNA pairwise FC matrix
def pairwise_fc_matrix(mirna_id: str, mirna: pd.DataFrame,
                        cell_type_groups: dict[str, list[str]]) -> pd.DataFrame:
    """FC matrix for a single miRNA across cell types."""
    means = {}
    for ct, cols in cell_type_groups.items():
        means[ct] = mirna.loc[mirna_id, cols].astype(float).mean()
    ct_names = list(means.keys())
    mat = pd.DataFrame(index=ct_names, columns=ct_names, dtype=float)
    for i, ct1 in enumerate(ct_names):
        for j, ct2 in enumerate(ct_names):
            mat.loc[ct1, ct2] = np.log2((means[ct1] + 1) / (means[ct2] + 1))
    return mat
```

---

## 9. Distribution Analysis (Fold Change Skewness)

```python
from scipy.stats import skew, kurtosis, shapiro

def fc_distribution_stats(log2fc_values: np.ndarray) -> dict:
    """Analyze distribution of log2 fold changes."""
    fc = log2fc_values[~np.isnan(log2fc_values)]
    stats = {
        'n': len(fc),
        'mean': np.mean(fc),
        'median': np.median(fc),
        'std': np.std(fc),
        'skewness': skew(fc),
        'kurtosis': kurtosis(fc),
        'min': np.min(fc),
        'max': np.max(fc),
        'pct_positive': (fc > 0).mean() * 100,
    }

    # Shapiro-Wilk normality test (max 5000 samples)
    if len(fc) <= 5000:
        W, p = shapiro(fc)
        stats['shapiro_W'] = W
        stats['shapiro_p'] = p
        stats['is_normal'] = p > 0.05

    return stats

dist = fc_distribution_stats(de_results['log2FC'].values)
print(f"Skewness: {dist['skewness']:.3f}")
print(f"  > 0 = right-skewed (more upregulated)")
print(f"  < 0 = left-skewed (more downregulated)")
```

---

## 10. Volcano Plot for miRNA

```python
import matplotlib.pyplot as plt
import numpy as np

def volcano_plot(de_results: pd.DataFrame, fc_col: str = 'log2FC',
                  pval_col: str = 'padj_bh', alpha: float = 0.05,
                  fc_thresh: float = 1.0, figsize: tuple = (10, 8),
                  title: str = 'miRNA Volcano Plot') -> plt.Figure:
    """Volcano plot with significance and fold change thresholds."""
    fig, ax = plt.subplots(figsize=figsize)

    log10p = -np.log10(de_results[pval_col].clip(lower=1e-300))
    fc = de_results[fc_col]

    # Color by significance
    colors = []
    for p, f in zip(de_results[pval_col], fc):
        if p < alpha and f > fc_thresh:
            colors.append('red')       # up
        elif p < alpha and f < -fc_thresh:
            colors.append('blue')      # down
        elif p < alpha:
            colors.append('orange')    # significant but small FC
        else:
            colors.append('gray')

    ax.scatter(fc, log10p, c=colors, alpha=0.5, s=10, edgecolors='none')

    # Threshold lines
    ax.axhline(-np.log10(alpha), color='black', linestyle='--', linewidth=0.5)
    ax.axvline(fc_thresh, color='black', linestyle='--', linewidth=0.5)
    ax.axvline(-fc_thresh, color='black', linestyle='--', linewidth=0.5)

    # Labels
    ax.set_xlabel('Log2 Fold Change')
    ax.set_ylabel('-Log10 Adjusted P-value')
    ax.set_title(title)

    n_up = sum(1 for c in colors if c == 'red')
    n_down = sum(1 for c in colors if c == 'blue')
    ax.text(0.02, 0.98, f'Up: {n_up}\nDown: {n_down}',
            transform=ax.transAxes, va='top', fontsize=10)

    plt.tight_layout()
    return fig

# Label top miRNAs
def volcano_with_labels(de_results: pd.DataFrame, top_n: int = 10, **kwargs):
    """Volcano plot with top miRNAs labeled."""
    fig = volcano_plot(de_results, **kwargs)
    ax = fig.axes[0]

    top = de_results.nsmallest(top_n, 'padj_bh')
    for mirna_id, row in top.iterrows():
        ax.annotate(mirna_id,
                     (row['log2FC'], -np.log10(row['padj_bh'])),
                     fontsize=7, alpha=0.8,
                     arrowprops=dict(arrowstyle='-', alpha=0.3))
    return fig

fig = volcano_with_labels(de_results, top_n=15, title='miRNA DE: Patient vs Control')
fig.savefig('mirna_volcano.png', dpi=150, bbox_inches='tight')
```

---

## scvi-tools Recipes

Python code templates for deep generative models applied to single-cell data using scvi-tools. Covers batch correction, semi-supervised annotation, multi-modal integration, differential expression, and latent space extraction.

---

## 11. scVI Setup and Training for Batch Correction

Train a variational autoencoder to learn a batch-corrected latent representation.

```python
import scanpy as sc
import scvi

# Load and prepare AnnData
adata = sc.read_h5ad("single_cell_data.h5ad")

# Filter and normalize (scVI expects raw counts)
sc.pp.filter_genes(adata, min_counts=3)
sc.pp.highly_variable_genes(adata, n_top_genes=3000, subset=True, flavor="seurat_v3")

# Register the AnnData object with scVI
scvi.model.SCVI.setup_anndata(
    adata,
    layer="counts",       # layer with raw counts; omit if adata.X has counts
    batch_key="batch",    # column in adata.obs for batch labels
)

# Initialize and train model
model = scvi.model.SCVI(adata, n_latent=30, n_layers=2, dropout_rate=0.1)
model.train(max_epochs=200, early_stopping=True, early_stopping_patience=10)

# Training history
train_elbo = model.history["elbo_train"]
print(f"Final train ELBO: {train_elbo.iloc[-1].values[0]:.2f}")
print(f"Epochs trained: {len(train_elbo)}")

# Save model for later use
model.save("scvi_model/")
# Reload: model = scvi.model.SCVI.load("scvi_model/", adata=adata)
```

---

## 12. scANVI for Semi-Supervised Cell Type Annotation

Transfer known cell type labels to unlabeled cells using a semi-supervised model.

```python
import scvi

# Start from a trained scVI model (see recipe 11)
# Annotate a subset of cells with known labels; rest are "Unknown"
adata.obs["cell_type_partial"] = adata.obs["cell_type"].copy()
# Simulate partial labels: mask 70% as unknown
import numpy as np
mask = np.random.choice([True, False], size=len(adata), p=[0.7, 0.3])
adata.obs.loc[mask, "cell_type_partial"] = "Unknown"

# Setup scANVI from the trained scVI model
scvi.model.SCANVI.setup_anndata(
    adata,
    batch_key="batch",
    labels_key="cell_type_partial",
    unlabeled_category="Unknown",
)
scanvi_model = scvi.model.SCANVI.from_scvi_model(
    model, unlabeled_category="Unknown", adata=adata
)
scanvi_model.train(max_epochs=50, n_samples_per_label=100)

# Predict labels for all cells
adata.obs["predicted_cell_type"] = scanvi_model.predict(adata)

# Prediction probabilities
soft_predictions = scanvi_model.predict(adata, soft=True)
adata.obs["prediction_confidence"] = soft_predictions.max(axis=1).values
print(f"Mean confidence: {adata.obs['prediction_confidence'].mean():.3f}")
```

---

## 13. totalVI for CITE-seq (RNA + Protein) Integration

Joint modeling of RNA and surface protein data from CITE-seq experiments.

```python
import scvi
import scanpy as sc

# Load CITE-seq AnnData (RNA in .X, protein in .obsm["protein_expression"])
adata = sc.read_h5ad("cite_seq_data.h5ad")

# Setup for totalVI
scvi.model.TOTALVI.setup_anndata(
    adata,
    batch_key="batch",
    protein_expression_obsm_key="protein_expression",
    layer="counts",
)

# Train totalVI model
totalvi_model = scvi.model.TOTALVI(
    adata, n_latent=20, latent_distribution="normal"
)
totalvi_model.train(max_epochs=200, early_stopping=True)

# Get denoised protein expression
denoised_protein = totalvi_model.get_normalized_expression(
    adata, n_samples=25, return_mean=True,
    transform_batch=["batch_1"],  # normalize to reference batch
)
rna_denoised, protein_denoised = denoised_protein

# Store latent representation
adata.obsm["X_totalVI"] = totalvi_model.get_latent_representation()
print(f"Latent shape: {adata.obsm['X_totalVI'].shape}")

# Protein foreground probability (separates signal from background)
protein_fg_prob = totalvi_model.get_protein_foreground_probability(adata)
print(f"Protein foreground prob shape: {protein_fg_prob.shape}")
```

---

## 14. Differential Expression with scVI

Bayesian differential expression testing using the trained scVI model.

```python
import scvi
import pandas as pd

# Assumes a trained scVI model (see recipe 11)
# DE between two groups defined by an obs column
de_results = model.differential_expression(
    adata,
    groupby="condition",
    group1="treatment",
    group2="control",
    delta=0.25,        # log-FC threshold for hypothesis test
    batch_correction=True,
)

# Filter significant DE genes
de_sig = de_results[
    (de_results["is_de_fdr_0.05"] == True) &
    (de_results["lfc_mean"].abs() > 0.5)
].sort_values("lfc_mean", ascending=False)

print(f"Significant DE genes: {len(de_sig)}")
print(f"  Upregulated: {(de_sig['lfc_mean'] > 0).sum()}")
print(f"  Downregulated: {(de_sig['lfc_mean'] < 0).sum()}")

# Top genes
print("\nTop 10 upregulated:")
print(de_sig.head(10)[["lfc_mean", "lfc_std", "bayes_factor", "is_de_fdr_0.05"]])

print("\nTop 10 downregulated:")
print(de_sig.tail(10)[["lfc_mean", "lfc_std", "bayes_factor", "is_de_fdr_0.05"]])
```

---

## 15. Extract Latent Representation and Feed to Scanpy UMAP

Use the scVI latent space for downstream clustering and visualization in scanpy.

```python
import scanpy as sc

# Get latent representation from trained scVI model
adata.obsm["X_scVI"] = model.get_latent_representation()
print(f"Latent representation shape: {adata.obsm['X_scVI'].shape}")

# Use scVI latent space for neighbor graph and clustering
sc.pp.neighbors(adata, use_rep="X_scVI", n_neighbors=15)
sc.tl.umap(adata)
sc.tl.leiden(adata, resolution=0.8, key_added="leiden_scVI")

# Visualize
sc.pl.umap(adata, color=["batch", "leiden_scVI", "cell_type"],
           ncols=3, frameon=False, save="_scvi_latent.png")

# Compare batch mixing before/after correction
sc.pl.umap(adata, color="batch", title="scVI batch-corrected",
           frameon=False, save="_batch_corrected.png")

print(f"Clusters found: {adata.obs['leiden_scVI'].nunique()}")
print(adata.obs["leiden_scVI"].value_counts())
```
