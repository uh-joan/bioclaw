# DNA Methylation & Epigenetic Analysis Recipes

Copy-paste-ready Python/R code for methylation data processing and analysis.
Dependencies: `pandas`, `numpy`, `scipy`, `statsmodels`, `seaborn`, `matplotlib`.

---

## 1. Loading Methylation Data

```python
import pandas as pd
import numpy as np

# Rows = CpG sites, columns = samples
meth = pd.read_csv('methylation_data.csv', index_col=0)
# Beta values: [0, 1] proportion methylated. M-values: log2(beta/(1-beta)), better for stats.

print(f"CpGs: {meth.shape[0]}, Samples: {meth.shape[1]}")
print(f"Range: [{meth.min().min():.4f}, {meth.max().max():.4f}]")
print(f"Missing: {meth.isna().sum().sum()}")
```

**Pitfalls:** Beta near 0/1 has heteroscedasticity -- use M-values for tests. Check detection p-values. Confirm normalization (BMIQ, SWAN, Noob).

---

## 2. Beta to M-value Conversion

```python
import numpy as np

def beta_to_m(beta, offset=1e-6):
    """Convert beta values to M-values.

    Offset prevents log(0) or log(inf) for extreme values.
    """
    beta = np.clip(beta, offset, 1 - offset)
    return np.log2(beta / (1 - beta))

def m_to_beta(m):
    """Convert M-values back to beta values."""
    return 2**m / (2**m + 1)

# Apply to entire DataFrame
M_values = beta_to_m(meth)
beta_recovered = m_to_beta(M_values)

# Verify round-trip
print(f"Max round-trip error: {(meth - beta_recovered).abs().max().max():.2e}")
```

**When to use M-values vs beta:**
- M-values: statistical tests (t-test, regression, ANOVA). Homoscedastic, approximately normal.
- Beta values: visualization, reporting, biological interpretation. Intuitive 0-1 scale.

---

## 3. Filtering CpG Sites

```python
mean_beta = meth.mean(axis=1)

# Remove near-invariant sites
meth_filtered = meth[(mean_beta > 0.05) & (mean_beta < 0.95)]

# Keep top N most variable
meth_top = meth.loc[meth.var(axis=1).nlargest(10000).index]

# Remove sex chromosomes (mixed-sex studies)
# autosomal = annot[~annot['chr'].isin(['chrX', 'chrY'])].index
# meth_auto = meth.loc[meth.index.intersection(autosomal)]
```

**Pitfalls:** Filter BEFORE multiple testing correction. Remove cross-reactive probes (Chen 2013, Pidsley 2016) and SNP-containing probes.

---

## 4. Differential Methylation Analysis (per CpG)

Test each CpG site for methylation differences between groups.

```python
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, ttest_ind
from statsmodels.stats.multitest import multipletests

group1_cols = ['sample1', 'sample2', 'sample3', 'sample4']
group2_cols = ['sample5', 'sample6', 'sample7', 'sample8']

results = []
for cpg in meth.index:
    g1 = meth.loc[cpg, group1_cols].values.astype(float)
    g2 = meth.loc[cpg, group2_cols].values.astype(float)

    # Skip if too many NaNs
    g1 = g1[~np.isnan(g1)]
    g2 = g2[~np.isnan(g2)]
    if len(g1) < 3 or len(g2) < 3:
        continue

    # Mann-Whitney U (non-parametric, on beta values)
    _, p_mw = mannwhitneyu(g1, g2, alternative='two-sided')

    # t-test on M-values (parametric, preferred for arrays)
    m1 = np.log2(np.clip(g1, 1e-6, 1 - 1e-6) / (1 - np.clip(g1, 1e-6, 1 - 1e-6)))
    m2 = np.log2(np.clip(g2, 1e-6, 1 - 1e-6) / (1 - np.clip(g2, 1e-6, 1 - 1e-6)))
    _, p_tt = ttest_ind(m1, m2, equal_var=False)

    delta_beta = np.mean(g2) - np.mean(g1)

    results.append({
        'cpg': cpg,
        'delta_beta': delta_beta,
        'pval_mw': p_mw,
        'pval_ttest': p_tt,
        'mean_g1': np.mean(g1),
        'mean_g2': np.mean(g2),
    })

res = pd.DataFrame(results)

# Multiple testing correction
_, res['padj_mw'], _, _ = multipletests(res['pval_mw'], method='fdr_bh')
_, res['padj_tt'], _, _ = multipletests(res['pval_ttest'], method='fdr_bh')

# Significant DMPs (differentially methylated positions)
sig = res[(res['padj_mw'] < 0.05) & (res['delta_beta'].abs() > 0.2)]
print(f"Significant DMPs: {len(sig)}")
print(f"  Hypermethylated: {(sig['delta_beta'] > 0).sum()}")
print(f"  Hypomethylated: {(sig['delta_beta'] < 0).sum()}")
```

**Pitfalls:**
- Use delta_beta threshold (|0.2| or |0.1|) in addition to p-value. Small p-value with delta_beta = 0.01 is not biologically meaningful.
- For array data (450K, EPIC), use limma in R for better power (see R recipe below).
- Batch effects are common. Always check with PCA and correct if needed.

---

## 5. Hyper/Hypo Methylation Classification

```python
# delta_beta > 0.2 = hypermethylated, < -0.2 = hypomethylated
delta_beta = meth[tumor_cols].mean(axis=1) - meth[normal_cols].mean(axis=1)

hyper = delta_beta[delta_beta > 0.2]
hypo  = delta_beta[delta_beta < -0.2]

summary = pd.DataFrame({
    'delta_beta': delta_beta,
    'status': pd.cut(delta_beta, bins=[-np.inf, -0.2, 0.2, np.inf],
                     labels=['hypo', 'stable', 'hyper']),
})
```

**Interpretation:** Promoter hypermethylation silences genes. Gene body hypomethylation may increase expression. Global hypo + focal hyper is a cancer hallmark.

---

## 6. Chromosomal CpG Density

```python
import pandas as pd
import numpy as np

# annot DataFrame needs 'cpg', 'chr', 'pos' columns
# chrom_lengths dict: {'chr1': 248956422, 'chr2': 242193529, ...}  (GRCh38)

cpg_counts = annot.groupby('chr').size()
density = cpg_counts / pd.Series(chrom_lengths) * 1e6  # CpGs per Mb
density = density.dropna().sort_values(ascending=False)
print(density)

# Plot
density.plot(kind='bar', figsize=(12, 5), ylabel='CpGs per Mb')
plt.savefig('cpg_density.png', dpi=150)
```

---

## 7. Chi-square Test for Uniform CpG Distribution

```python
from scipy.stats import chisquare

cpg_per_chrom = annot.groupby('chr').size()
total_length = sum(chrom_lengths[c] for c in cpg_per_chrom.index)
expected = np.array([chrom_lengths[c] / total_length * cpg_per_chrom.sum()
                     for c in cpg_per_chrom.index])
chi2, pval = chisquare(cpg_per_chrom.values.astype(float), f_exp=expected)

# Residuals: enriched/depleted chromosomes
residuals = (cpg_per_chrom.values - expected) / np.sqrt(expected)
```

**Interpretation:** p < 0.05 = non-uniform distribution relative to chromosome length.

---

## 8. m6A RNA Methylation Analysis (MeRIP-seq)

Cross-tabulation of m6A status with differential expression.

```python
import pandas as pd
from scipy.stats import chi2_contingency, fisher_exact

contingency = pd.crosstab(df['m6A_status'], df['DEG_status'])
chi2, pval, dof, expected = chi2_contingency(contingency)

# Effect size: Cramer's V
n = contingency.sum().sum()
cramers_v = np.sqrt(chi2 / (n * (min(contingency.shape) - 1)))

# For 2x2 tables, use Fisher's exact test
binary = pd.crosstab(df['m6A_status'],
                     df['DEG_status'].map(lambda x: 'DE' if x != 'stable' else 'stable'))
odds_ratio, p_fisher = fisher_exact(binary)
```

**When to use:** Testing whether RNA methylation (m6A, m5C) is associated with DE, splicing, or functional categories.

---

## 9. Age-related CpG Analysis (Epigenetic Clock)

```python
from scipy.stats import pearsonr
from statsmodels.stats.multitest import multipletests

results = []
for cpg in meth.index:
    beta = meth.loc[cpg, sample_cols].values.astype(float)
    valid = ~np.isnan(beta)
    if valid.sum() < 5:
        continue
    r, p = pearsonr(ages[valid], beta[valid])
    results.append({'cpg': cpg, 'r': r, 'pval': p, 'direction': 'gain' if r > 0 else 'loss'})

age_res = pd.DataFrame(results)
_, age_res['padj'], _, _ = multipletests(age_res['pval'], method='fdr_bh')
sig_age = age_res[age_res['padj'] < 0.05]
```

**Context:** Epigenetic clocks (Horvath, Hannum) use ~300-500 CpGs to predict biological age.

---

## 10. Visualization

### Heatmap of Methylation Levels

```python
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Select top variable CpGs for visualization
variance = meth.var(axis=1)
top_cpgs = variance.nlargest(50).index
meth_top = meth.loc[top_cpgs]

fig, ax = plt.subplots(figsize=(12, 10))
sns.heatmap(
    meth_top,
    cmap='RdBu_r',
    center=0.5,
    vmin=0, vmax=1,
    xticklabels=True,
    yticklabels=False,
    ax=ax,
)
ax.set_title('Top 50 Most Variable CpG Sites')
ax.set_xlabel('Samples')
ax.set_ylabel('CpG Sites')
plt.tight_layout()
plt.savefig('methylation_heatmap.png', dpi=150)
```

### Volcano Plot for Differential Methylation

```python
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(8, 6))
colors = np.where(
    (res['padj_mw'] < 0.05) & (res['delta_beta'] > 0.2), 'red',
    np.where((res['padj_mw'] < 0.05) & (res['delta_beta'] < -0.2), 'blue', 'grey'))
ax.scatter(res['delta_beta'], -np.log10(res['pval_mw']), c=colors, alpha=0.5, s=5)
ax.axhline(-np.log10(0.05), color='black', ls='--', lw=0.5)
ax.axvline(0.2, color='black', ls='--', lw=0.5)
ax.axvline(-0.2, color='black', ls='--', lw=0.5)
ax.set_xlabel('Delta Beta'); ax.set_ylabel('-log10(p-value)')
plt.savefig('methylation_volcano.png', dpi=150)
```

### Beta Value Distribution

```python
fig, ax = plt.subplots(figsize=(8, 5))
for col in meth.columns[:10]:
    meth[col].plot(kind='density', ax=ax, alpha=0.5, label=col)
ax.set_xlabel('Beta Value'); ax.set_xlim(0, 1); ax.legend(fontsize=6)
plt.savefig('beta_distributions.png', dpi=150)
```

---

## 11. Differentially Methylated Regions (DMR) Detection

Group consecutive DMPs into regions using a simple sliding window approach.

```python
import pandas as pd
import numpy as np

def find_dmrs(dmp_df, annot_df, max_gap=1000, min_cpgs=3):
    """Group nearby DMPs into DMRs.

    Args:
        dmp_df: DataFrame with 'cpg' column (significant DMPs)
        annot_df: DataFrame with 'cpg', 'chr', 'pos' columns
        max_gap: Maximum distance (bp) between consecutive DMPs in a region
        min_cpgs: Minimum number of DMPs to form a DMR
    """
    merged = dmp_df.merge(annot_df, on='cpg').sort_values(['chr', 'pos'])

    dmrs = []
    for chrom, group in merged.groupby('chr'):
        group = group.sort_values('pos')
        positions = group['pos'].values

        region_start = 0
        for i in range(1, len(positions)):
            if positions[i] - positions[i-1] > max_gap:
                if i - region_start >= min_cpgs:
                    region = group.iloc[region_start:i]
                    dmrs.append({
                        'chr': chrom,
                        'start': positions[region_start],
                        'end': positions[i-1],
                        'n_cpgs': i - region_start,
                        'mean_delta': region['delta_beta'].mean(),
                        'cpgs': ','.join(region['cpg'].values),
                    })
                region_start = i

        # Last region
        if len(positions) - region_start >= min_cpgs:
            region = group.iloc[region_start:]
            dmrs.append({
                'chr': chrom,
                'start': positions[region_start],
                'end': positions[-1],
                'n_cpgs': len(positions) - region_start,
                'mean_delta': region['delta_beta'].mean(),
                'cpgs': ','.join(region['cpg'].values),
            })

    return pd.DataFrame(dmrs)

# dmr_results = find_dmrs(sig_dmps, annotation, max_gap=1000, min_cpgs=3)
```

**Pitfalls:**
- This is a simplified approach. For production use, consider dedicated tools: `dmrseq` (R), `bumphunter` (R), or `methylKit` (R).
- Gap and min_cpgs thresholds depend on array type (450K vs EPIC) and research question.

---

## 12. R Recipe: limma for Methylation Arrays (450K/EPIC)

```r
library(limma); library(minfi)
rgSet <- read.metharray.exp("idat_directory/")
mSet <- preprocessNoob(rgSet)
M <- getM(mSet); beta <- getBeta(mSet)

group <- factor(c(rep("control", 4), rep("treatment", 4)))
design <- model.matrix(~ group)
fit <- eBayes(lmFit(M, design))
results <- topTable(fit, coef=2, number=Inf, sort.by="p")
results$delta_beta <- rowMeans(beta[rownames(results), group == "treatment"]) -
                      rowMeans(beta[rownames(results), group == "control"])
sig <- results[results$adj.P.Val < 0.05 & abs(results$delta_beta) > 0.2, ]
```

---

## 13. R Recipe: methylKit for Bisulfite Sequencing (WGBS/RRBS)

```r
library(methylKit)
obj <- methRead(file_list, sample.id=sample_ids, assembly="hg38",
                treatment=c(0,0,1,1), context="CpG", mincov=10)
filtered <- filterByCoverage(obj, lo.count=10, hi.perc=99.9)
meth_merged <- unite(filtered, destrand=FALSE)
dm <- calculateDiffMeth(meth_merged, overdispersion="MN", test="Chisq")
hyper <- getMethylDiff(dm, difference=25, qvalue=0.01, type="hyper")
hypo  <- getMethylDiff(dm, difference=25, qvalue=0.01, type="hypo")
```

---

## Quick Reference

| Task | Recipe | Key function |
|------|--------|-------------|
| Load data | #1 | `pd.read_csv()` |
| Beta <-> M conversion | #2 | `np.log2(b/(1-b))` |
| Filter CpGs | #3 | Variance/mean thresholds |
| Per-CpG DM test | #4 | `mannwhitneyu` + `multipletests` |
| Hyper/hypo classify | #5 | delta_beta threshold |
| Chromosome density | #6 | `groupby('chr').size()` |
| Uniform distribution | #7 | `chisquare()` |
| m6A cross-tab | #8 | `chi2_contingency()` |
| Age correlation | #9 | `pearsonr()` per CpG |
| Heatmap/volcano | #10 | `seaborn.heatmap()` |
| DMR detection | #11 | Sliding window grouping |
| limma (R) | #12 | `lmFit` + `eBayes` |
| methylKit (R) | #13 | `calculateDiffMeth` |

---

## Cross-Skill Routing

- Statistical test details and assumptions --> `biostat-recipes`
- Epigenomics concepts and experimental design --> `epigenomics`
- Integration with expression data --> `deseq2-recipes`
- Variant-level analysis (SNPs in CpG sites) --> `variant-calling`
