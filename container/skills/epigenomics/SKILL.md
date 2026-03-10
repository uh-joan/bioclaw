---
name: epigenomics
description: Epigenomics and epigenetic data analysis. DNA methylation, bisulfite sequencing, methylation arrays (450K, EPIC), histone modifications, ChIP-seq, ATAC-seq, chromatin accessibility, enhancer identification, epigenetic clock, CpG islands, differential methylation. Use when user mentions epigenomics, epigenetics, DNA methylation, bisulfite, ChIP-seq, ATAC-seq, histone modification, chromatin accessibility, CpG, methylation array, 450K, EPIC array, epigenetic clock, Horvath clock, enhancer, promoter methylation, or imprinting.
---

# Epigenomics Analysis

> **Code recipes**: See [recipes.md](recipes.md) for DNA methylation analysis templates, and [chipseq-recipes.md](chipseq-recipes.md) for ChIP-seq and ATAC-seq analysis templates.

Epigenomics and epigenetic data analysis covering DNA methylation (bisulfite-seq, 450K/EPIC arrays), histone modifications (ChIP-seq), and chromatin accessibility (ATAC-seq). The agent writes and executes Python code for methylation QC, normalization, differential methylation analysis, CpG annotation, epigenetic clock estimation, peak-based chromatin analysis, and histone code interpretation. Uses Open Targets for gene-disease annotation, PubMed for literature evidence, and NLM for gene ID resolution.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_epigenomics_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Deep pathway enrichment (ORA/GSEA multi-database) on DMP gene lists → use `gene-enrichment`
- Protein interaction network analysis of epigenetically regulated genes → use `systems-biology`
- Single-cell ATAC-seq or scBS-seq clustering and cell type annotation → use `single-cell-analysis`
- Joint multi-omics integration (methylation + expression + proteomics) → use `multi-omics-integration`
- Clinical variant interpretation in epigenetic contexts → use `variant-interpretation`
- Spatial chromatin accessibility analysis → use `spatial-transcriptomics`

## Cross-Reference: Other Skills

- **Multi-omics integration with methylation and expression** -> use multi-omics-integration skill
- **Pathway enrichment on differentially methylated gene lists** -> use gene-enrichment skill
- **Systems-level network analysis of epigenetically regulated genes** -> use systems-biology skill
- **Clinical variant interpretation in epigenetic contexts** -> use variant-interpretation skill

## Python Environment

| Package | Purpose |
|---------|---------|
| `pandas`, `numpy` | Data manipulation and numerical computation |
| `scipy` | Statistical tests (t-tests, Mann-Whitney, linear models) |
| `statsmodels` | Linear regression, multiple testing correction |
| `scikit-learn` | PCA, clustering, machine learning for clock models |
| `matplotlib`, `seaborn` | Visualization (heatmaps, volcano plots, density plots) |
| `pybedtools` | BED file manipulation for peak-based analyses |
| `gseapy` | Gene set enrichment on methylation-associated gene lists |

## Data Types & Input Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| Beta value matrix | `.csv`, `.tsv` | Probes x Samples, values 0-1 |
| M-value matrix | `.csv`, `.tsv` | Probes x Samples, logit-transformed betas |
| Bisulfite-seq calls | `.cov`, `.bedGraph` | chr, start, end, meth%, count_meth, count_unmeth |
| Peak files | `.bed`, `.narrowPeak`, `.broadPeak` | Genomic intervals with scores (MACS2/3 output) |
| Count matrix | `.csv`, `.tsv` | Peaks/regions x Samples (for differential accessibility) |

```python
import numpy as np

def beta_to_m(beta, offset=1e-6):
    """Convert beta values to M-values (logit transformation).
    M-values are better for statistics; beta values for interpretation."""
    beta = np.clip(beta, offset, 1 - offset)
    return np.log2(beta / (1 - beta))

def m_to_beta(m):
    """Convert M-values back to beta values."""
    return 2**m / (2**m + 1)
```

---

## DNA Methylation Analysis Pipeline

### Phase 1: Data Loading & QC

```
1. Load methylation data, detect format (beta vs M-values)
2. Verify probe IDs match platform (450K: ~485K probes, EPIC: ~865K probes)
3. QC checks:
   - Beta distribution per sample (should be bimodal: peaks near 0 and 1)
   - Filter probes with detection p > 0.01
   - Remove probes with > 5% missing values
   - Remove cross-reactive and SNP-affected probes
   - Handle sex chromosome probes separately or remove
```

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def load_methylation_data(file_path):
    sep = '\t' if file_path.endswith(('.tsv', '.txt')) else ','
    data = pd.read_csv(file_path, sep=sep, index_col=0)
    val_range = data.values[~np.isnan(data.values)]
    data_type = "beta" if (val_range.min() >= 0 and val_range.max() <= 1) else "mvalue"
    print(f"Detected: {data_type} values | Probes: {data.shape[0]}, Samples: {data.shape[1]}")
    return data, data_type

beta_df, data_type = load_methylation_data("methylation_data.csv")

# QC: Beta value density per sample
fig, ax = plt.subplots(figsize=(12, 6))
for col in beta_df.columns:
    beta_df[col].dropna().plot.kde(ax=ax, alpha=0.5, label=col)
ax.set_xlabel("Beta Value"); ax.set_ylabel("Density")
ax.set_title("Beta Value Distribution per Sample")
plt.tight_layout(); plt.savefig("beta_density_qc.png", dpi=150)

# Filter probes with excessive missing values
missing_rate = beta_df.isna().mean(axis=1)
beta_df = beta_df[missing_rate <= 0.05]
beta_df = beta_df.fillna(beta_df.median(axis=1), axis=0)
print(f"Probes after QC: {beta_df.shape[0]}")
```

### Phase 2: Normalization

```
1. BMIQ: Corrects Infinium I vs II probe type bias (Type II has compressed range)
2. Quantile normalization: Forces same distribution across samples
   - NOT appropriate when global methylation shifts are expected (e.g., cancer)
3. Functional normalization: Uses control probes to remove technical variation
```

```python
from scipy import stats

def quantile_normalize(df):
    """Quantile normalize across samples (columns)."""
    rank_mean = df.stack().groupby(
        df.rank(method='first').stack().astype(int)
    ).mean()
    return df.rank(method='min').stack().astype(int).map(rank_mean).unstack()

def simple_probe_type_correction(beta_df, probe_types):
    """Simplified Type I/II probe correction (BMIQ-like concept).
    probe_types: Series mapping probe ID to 'I' or 'II'."""
    corrected = beta_df.copy()
    type1 = probe_types[probe_types == 'I'].index.intersection(beta_df.index)
    type2 = probe_types[probe_types == 'II'].index.intersection(beta_df.index)
    for col in beta_df.columns:
        type1_vals = beta_df.loc[type1, col].dropna().sort_values()
        type2_vals = beta_df.loc[type2, col].dropna()
        type2_ranks = type2_vals.rank(pct=True)
        corrected.loc[type2, col] = np.quantile(type1_vals, type2_ranks.values)
    return corrected

beta_norm = quantile_normalize(beta_df)
```

### Phase 3: Differential Methylation Analysis

```
DMP (Differentially Methylated Position): per-CpG linear model + BH correction
DMR (Differentially Methylated Region): clusters of adjacent DMPs

- Use M-values for statistical testing, report delta-beta for interpretation
- Minimum delta-beta threshold: |0.05| (standard), |0.1| (stringent)
- Covariates: age, sex, cell type composition, batch
```

```python
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

def run_dmp_analysis(beta_df, metadata, group_col, covariates=None, alpha=0.05):
    """DMP analysis using per-probe linear models with BH correction."""
    m_values = np.log2(beta_df.clip(1e-6, 1-1e-6) / (1 - beta_df.clip(1e-6, 1-1e-6)))
    groups = metadata[group_col]
    unique_groups = groups.unique()
    assert len(unique_groups) == 2, f"Expected 2 groups, got {len(unique_groups)}"
    group_binary = (groups == unique_groups[1]).astype(int)

    design_cols = {'intercept': 1, 'group': group_binary}
    if covariates:
        for cov in covariates:
            design_cols[cov] = metadata[cov].values
    design = pd.DataFrame(design_cols, index=metadata.index)

    results = []
    for probe in m_values.index:
        y = m_values.loc[probe, metadata.index].values
        if np.isnan(y).any():
            continue
        try:
            model = sm.OLS(y, design.values).fit()
            g1_beta = beta_df.loc[probe, groups == unique_groups[0]].mean()
            g2_beta = beta_df.loc[probe, groups == unique_groups[1]].mean()
            results.append({
                'probe': probe, 'coef_m': model.params[1], 'se': model.bse[1],
                'pvalue': model.pvalues[1], 'delta_beta': g2_beta - g1_beta,
                'mean_beta_g1': g1_beta, 'mean_beta_g2': g2_beta
            })
        except Exception:
            continue

    results_df = pd.DataFrame(results).set_index('probe')
    _, padj, _, _ = multipletests(results_df['pvalue'], method='fdr_bh')
    results_df['padj'] = padj

    sig = results_df[(results_df['padj'] < alpha) &
                     (results_df['delta_beta'].abs() > 0.05)].sort_values('padj')
    print(f"Tested: {len(results_df)} | Significant DMPs: {len(sig)}")
    print(f"  Hypermethylated: {(sig['delta_beta'] > 0).sum()}")
    print(f"  Hypomethylated: {(sig['delta_beta'] < 0).sum()}")
    return results_df, sig

metadata = pd.read_csv("sample_metadata.csv", index_col=0)
all_results, sig_dmps = run_dmp_analysis(beta_df, metadata, "condition",
                                          covariates=["age", "sex"])
all_results.to_csv("dmp_all_results.csv")
sig_dmps.to_csv("dmp_significant.csv")
```

### Phase 4: CpG Annotation & Enrichment

```
CpG genomic context:
- CpG Island: GC > 50%, obs/exp CpG > 0.6, > 200 bp. Usually unmethylated.
- CpG Shore: 0-2 kb flanking island. Tissue-specific methylation changes.
- CpG Shelf: 2-4 kb flanking island.
- Open Sea: > 4 kb from island. Generally methylated.

Gene region: TSS1500, TSS200, 5'UTR, 1st Exon, Body, 3'UTR
```

```python
from scipy.stats import fisher_exact

def cpg_context_enrichment(sig_probes, all_probes, annotation_df):
    """Test DMP enrichment in CpG contexts using Fisher's exact test."""
    contexts = ['Island', 'N_Shore', 'S_Shore', 'N_Shelf', 'S_Shelf', 'OpenSea']
    results = []
    for ctx in contexts:
        sig_in = annotation_df.loc[sig_probes, 'Relation_to_Island'].eq(ctx).sum()
        sig_out = len(sig_probes) - sig_in
        bg_in = annotation_df.loc[all_probes, 'Relation_to_Island'].eq(ctx).sum()
        bg_out = len(all_probes) - bg_in
        odds, pval = fisher_exact([[sig_in, sig_out], [bg_in, bg_out]])
        results.append({'context': ctx, 'sig_count': sig_in, 'odds_ratio': odds, 'pvalue': pval})
    enrich_df = pd.DataFrame(results)
    _, enrich_df['padj'], _, _ = multipletests(enrich_df['pvalue'], method='fdr_bh')
    return enrich_df.sort_values('padj')

def extract_dmp_genes(sig_dmps, annotation_df):
    """Extract unique genes from DMP annotations for enrichment."""
    annotated = sig_dmps.join(annotation_df[['UCSC_RefGene_Name', 'UCSC_RefGene_Group']])
    genes = annotated['UCSC_RefGene_Name'].dropna().str.split(';').explode().unique().tolist()
    print(f"Unique genes associated with DMPs: {len(genes)}")
    return genes

# Gene enrichment via gseapy
import gseapy as gp
dmp_genes = extract_dmp_genes(sig_dmps, annotation_df)
enr = gp.enrichr(gene_list=dmp_genes, gene_sets='GO_Biological_Process_2023', organism='human')
sig_terms = enr.results[enr.results['Adjusted P-value'] < 0.05]
print(sig_terms[['Term', 'Overlap', 'Adjusted P-value']].head(15))
```

### Phase 5: Epigenetic Clock Analysis

```
Epigenetic clocks predict biological age from DNA methylation:

1. Horvath (2013): 353 CpGs, multi-tissue, chronological age
2. Hannum (2013): 71 CpGs, blood-optimized
3. PhenoAge (Levine, 2018): 513 CpGs, trained on clinical biomarkers
4. GrimAge (Lu, 2019): DNAm surrogates for plasma proteins, best mortality predictor
5. DunedinPACE (2022): Pace of aging (rate), values > 1 = accelerated

Age acceleration = predicted age - chronological age
```

```python
from sklearn.linear_model import ElasticNet
from sklearn.model_selection import cross_val_predict
from sklearn.metrics import mean_absolute_error

def epigenetic_clock_analysis(beta_df, metadata, clock_cpgs, clock_coefficients,
                               intercept, age_col='age'):
    """Predict biological age using pre-trained clock coefficients."""
    available = [c for c in clock_cpgs if c in beta_df.index]
    missing = set(clock_cpgs) - set(available)
    print(f"Clock CpGs available: {len(available)}/{len(clock_cpgs)}")

    X = beta_df.loc[available, metadata.index].T
    for cpg in missing:
        X[cpg] = 0.5  # impute with population average
    X = X[clock_cpgs]

    predicted_age = X.values @ clock_coefficients + intercept
    results = pd.DataFrame({
        'chronological_age': metadata[age_col].values,
        'predicted_age': predicted_age,
        'age_acceleration': predicted_age - metadata[age_col].values
    }, index=metadata.index)

    mae = mean_absolute_error(results['chronological_age'], results['predicted_age'])
    corr = results['chronological_age'].corr(results['predicted_age'])
    print(f"MAE: {mae:.2f} years | Correlation: {corr:.3f}")
    print(f"Mean age acceleration: {results['age_acceleration'].mean():.2f} years")
    return results

def compare_age_acceleration(clock_results, metadata, group_col):
    """Compare age acceleration between two groups."""
    from scipy.stats import mannwhitneyu, ttest_ind
    merged = clock_results.join(metadata[[group_col]])
    groups = merged[group_col].unique()
    g1 = merged[merged[group_col] == groups[0]]['age_acceleration']
    g2 = merged[merged[group_col] == groups[1]]['age_acceleration']
    _, t_pval = ttest_ind(g1, g2)
    _, u_pval = mannwhitneyu(g1, g2, alternative='two-sided')
    print(f"{groups[0]}: mean={g1.mean():.2f} | {groups[1]}: mean={g2.mean():.2f}")
    print(f"t-test p={t_pval:.4e} | Mann-Whitney p={u_pval:.4e}")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for grp in groups:
        s = merged[merged[group_col] == grp]
        axes[0].scatter(s['chronological_age'], s['predicted_age'], label=grp, alpha=0.7)
    axes[0].plot([merged['chronological_age'].min(), merged['chronological_age'].max()],
                 [merged['chronological_age'].min(), merged['chronological_age'].max()], 'k--')
    axes[0].set_xlabel('Chronological Age'); axes[0].set_ylabel('Predicted Age')
    axes[0].legend()
    axes[1].boxplot([g1.values, g2.values], labels=groups)
    axes[1].axhline(0, color='red', linestyle='--')
    axes[1].set_ylabel('Age Acceleration (years)')
    plt.tight_layout(); plt.savefig('epigenetic_clock_results.png', dpi=150)

def train_custom_clock(beta_df, metadata, age_col='age', n_cpgs=500):
    """Train custom clock via ElasticNet when published coefficients unavailable."""
    cpg_var = beta_df.var(axis=1).nlargest(n_cpgs)
    X = beta_df.loc[cpg_var.index, metadata.index].T.values
    y = metadata[age_col].values
    best_mae, best_alpha = float('inf'), None
    for a in [0.1, 0.5, 1.0, 5.0, 10.0]:
        model = ElasticNet(alpha=a, l1_ratio=0.5, max_iter=10000)
        y_pred = cross_val_predict(model, X, y, cv=5)
        mae = mean_absolute_error(y, y_pred)
        if mae < best_mae:
            best_mae, best_alpha, best_model = mae, a, model
    best_model.fit(X, y)
    print(f"Custom clock: alpha={best_alpha}, CpGs={( best_model.coef_ != 0).sum()}, MAE={best_mae:.2f}")
    return best_model, cpg_var.index.tolist()
```

---

## Chromatin Accessibility Analysis (ATAC-seq)

### Peak Analysis

```python
def differential_accessibility(count_matrix, metadata, group_col, alpha=0.05):
    """Differential accessibility between two groups (Mann-Whitney on log2 CPM)."""
    from scipy.stats import mannwhitneyu
    groups = metadata[group_col].unique()
    assert len(groups) == 2
    g1 = metadata[metadata[group_col] == groups[0]].index
    g2 = metadata[metadata[group_col] == groups[1]].index

    cpm = count_matrix.div(count_matrix.sum(axis=0), axis=1) * 1e6
    log_cpm = np.log2(cpm + 1)

    results = []
    for peak in count_matrix.index:
        g1_vals, g2_vals = log_cpm.loc[peak, g1].values, log_cpm.loc[peak, g2].values
        try:
            _, pval = mannwhitneyu(g1_vals, g2_vals, alternative='two-sided')
        except ValueError:
            continue
        results.append({'peak': peak, 'log2FC': g2_vals.mean() - g1_vals.mean(), 'pvalue': pval})

    results_df = pd.DataFrame(results).set_index('peak')
    _, results_df['padj'], _, _ = multipletests(results_df['pvalue'], method='fdr_bh')
    sig = results_df[(results_df['padj'] < alpha) & (results_df['log2FC'].abs() > 1)].sort_values('padj')
    print(f"Peaks tested: {len(results_df)} | DA peaks: {len(sig)}")
    return results_df, sig

def annotate_peaks(peak_bed, gene_annotation):
    """Classify peaks as promoter (<2kb from TSS), proximal (<10kb), or distal."""
    annotations = []
    for _, peak in peak_bed.iterrows():
        same_chr = gene_annotation[gene_annotation['chr'] == peak['chr']]
        if len(same_chr) == 0:
            annotations.append({'peak_id': peak['peak_id'], 'feature': 'intergenic',
                                'nearest_gene': 'NA', 'distance_to_tss': np.nan})
            continue
        distances = (same_chr['tss'] - (peak['start'] + peak['end']) / 2).abs()
        nearest = same_chr.loc[distances.idxmin()]
        dist = distances.min()
        feature = 'promoter' if dist <= 2000 else ('proximal' if dist <= 10000 else 'distal')
        annotations.append({'peak_id': peak['peak_id'], 'feature': feature,
                            'nearest_gene': nearest['gene'], 'distance_to_tss': dist})
    return pd.DataFrame(annotations)
```

### Integration with Gene Expression

```python
def accessibility_expression_correlation(peak_annotation, peak_counts, expression_df):
    """Correlate promoter accessibility with gene expression (Spearman)."""
    from scipy.stats import spearmanr
    promoters = peak_annotation[peak_annotation['feature'] == 'promoter']
    common = peak_counts.columns.intersection(expression_df.columns)
    correlations = []
    for _, row in promoters.iterrows():
        gene, peak = row['nearest_gene'], row['peak_id']
        if gene not in expression_df.index or peak not in peak_counts.index:
            continue
        acc = peak_counts.loc[peak, common].values
        expr = expression_df.loc[gene, common].values
        if np.std(acc) == 0 or np.std(expr) == 0:
            continue
        rho, pval = spearmanr(acc, expr)
        correlations.append({'gene': gene, 'peak': peak, 'spearman_rho': rho, 'pvalue': pval})
    corr_df = pd.DataFrame(correlations)
    if len(corr_df):
        _, corr_df['padj'], _, _ = multipletests(corr_df['pvalue'], method='fdr_bh')
    return corr_df
```

---

## ChIP-seq Analysis Framework

### Peak Types

| Peak Type | Examples | Call With |
|-----------|----------|-----------|
| Narrow (focal) | TFs, H3K4me3, H3K27ac | MACS2/3 default |
| Broad (diffuse) | H3K36me3, H3K27me3, H3K9me3 | MACS2/3 `--broad` |

### Histone Mark Reference

| Mark | Type | Location | Function |
|------|------|----------|----------|
| H3K4me3 | Activating | Promoters | Active promoter |
| H3K4me1 | Activating | Enhancers | Enhancer priming (active + poised) |
| H3K27ac | Activating | Enhancers + Promoters | Distinguishes active from poised |
| H3K36me3 | Activating | Gene bodies | Transcription elongation |
| H3K27me3 | Repressive | Promoters + bodies | Polycomb silencing (reversible) |
| H3K9me3 | Repressive | Heterochromatin | Constitutive silencing |
| H3K9ac | Activating | Promoters | Active transcription |

## Histone Code Interpretation

```
Combinatorial marks -> chromatin state:

Active Promoter:      H3K4me3(+) H3K27ac(+) H3K27me3(-) -> strong expression
Bivalent Promoter:    H3K4me3(+) H3K27me3(+) H3K27ac(-) -> poised (stem cells)
Active Enhancer:      H3K4me1(+) H3K27ac(+) H3K4me3(-) -> tissue-specific activation
Poised Enhancer:      H3K4me1(+) H3K27ac(-) -> primed, not yet active
Polycomb Repressed:   H3K27me3(+) H3K4me3(-) -> reversible silencing
Heterochromatin:      H3K9me3(+) -> constitutive silencing (repeats, transposons)
Transcribed Body:     H3K36me3(+) -> actively transcribed gene
```

```python
def assign_chromatin_states(mark_signals):
    """Assign chromatin state from combinatorial histone mark signals.
    mark_signals: DataFrame, rows=regions, columns=histone marks, values=signal."""
    states = []
    for idx, row in mark_signals.iterrows():
        k4me3 = row.get('H3K4me3', 0) > mark_signals.get('H3K4me3', pd.Series([0])).median()
        k4me1 = row.get('H3K4me1', 0) > mark_signals.get('H3K4me1', pd.Series([0])).median()
        k27ac = row.get('H3K27ac', 0) > mark_signals.get('H3K27ac', pd.Series([0])).median()
        k27me3 = row.get('H3K27me3', 0) > mark_signals.get('H3K27me3', pd.Series([0])).median()
        k36me3 = row.get('H3K36me3', 0) > mark_signals.get('H3K36me3', pd.Series([0])).median()
        k9me3 = row.get('H3K9me3', 0) > mark_signals.get('H3K9me3', pd.Series([0])).median()

        if k4me3 and k27ac and not k27me3: state = 'Active_Promoter'
        elif k4me3 and k27me3: state = 'Bivalent_Promoter'
        elif k4me1 and k27ac and not k4me3: state = 'Active_Enhancer'
        elif k4me1 and not k27ac: state = 'Poised_Enhancer'
        elif k27me3 and not k4me3 and not k9me3: state = 'Polycomb_Repressed'
        elif k9me3: state = 'Heterochromatin'
        elif k36me3: state = 'Transcribed'
        else: state = 'Quiescent'
        states.append({'region': idx, 'chromatin_state': state})

    state_df = pd.DataFrame(states).set_index('region')
    print(state_df['chromatin_state'].value_counts())
    return state_df
```

---

## JASPAR TF Binding Analysis in Epigenomic Contexts

### `mcp__jaspar__jaspar_data` (TF Binding in Regulatory Regions)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_matrices` | Find TF binding profiles by TF name, species, family | `tf_name`, `species`, `family` |
| `scan_sequence` | Scan DNA sequence for TF binding sites within regulatory regions | `matrix_id`, `sequence` |
| `variant_impact` | Assess variant effect on TF binding (ref vs alt) | `matrix_id`, `ref_sequence`, `alt_sequence` |

#### Workflow: TF Binding Sites in Epigenomic Peaks

```
Use JASPAR to identify TF binding sites within epigenomic peaks (ATAC-seq,
ChIP-seq) and assess variant impact on TF occupancy:

1. Identify open chromatin or histone-marked regions from ATAC-seq/ChIP-seq peak calls
2. mcp__jaspar__jaspar_data(method="search_matrices", tf_name="<TF_name>", species="9606")
   -> Find JASPAR matrix IDs for TFs of interest
3. mcp__jaspar__jaspar_data(method="scan_sequence", matrix_id="<matrix_id>", sequence="<peak_sequence>")
   -> Scan peak sequences for predicted TF binding sites
   -> Overlay with chromatin accessibility to identify occupied sites
4. mcp__jaspar__jaspar_data(method="variant_impact", matrix_id="<matrix_id>", ref_sequence="<ref>", alt_sequence="<alt>")
   -> Assess whether variants within peaks disrupt or create TF binding
   -> Variants in ATAC-seq peaks that disrupt TF binding suggest loss of TF occupancy
   -> Variants in H3K27ac peaks affecting TF binding may alter enhancer activity
5. Integrate with differential accessibility/methylation results:
   -> DA peaks with disrupted TF binding -> mechanistic link to chromatin change
   -> DMPs at TF binding sites -> methylation-dependent TF binding regulation
```

---

## Evidence Grading Framework

| Tier | Criteria | Confidence |
|------|----------|------------|
| **T1** | Multi-assay concordance (methylation + ChIP/ATAC at same locus), padj < 0.01, delta-beta > 0.15, literature support | High |
| **T2** | Significant DMR (padj < 0.05), methylation-expression anti-correlation, replicated in independent cohort | Medium-High |
| **T3** | Significant DMP (padj < 0.05, delta-beta > 0.05) or DA peak, single dataset/assay | Medium |
| **T4** | Marginal DMP (padj 0.05-0.1 or delta-beta < 0.05), single CpG without regional support | Low |

---

## Boundary Rules

```
DO:
- Write and execute Python code for methylation QC, normalization, DMP/DMR analysis
- Run epigenetic clock analysis (Horvath, Hannum, PhenoAge, GrimAge concepts)
- Analyze ATAC-seq differential accessibility from count matrices
- Interpret ChIP-seq peaks and assign chromatin states from histone marks
- Correlate promoter accessibility with gene expression
- Run gene enrichment (gseapy) on DMP-associated gene lists
- Annotate top genes via MCP tools (Open Targets, NLM, PubMed)

DO NOT:
- Perform read alignment or peak calling (upstream bioinformatics)
- Process raw IDAT files (use R minfi/sesame upstream)
- Run single-cell ATAC-seq clustering (use single-cell-analysis skill)
- Do deep pathway enrichment (hand off to gene-enrichment skill)
- Build protein interaction networks (use systems-biology skill)
- Interpret clinical variants (use variant-interpretation skill)
```

| Task | Skill |
|------|-------|
| Methylation QC, DMP/DMR, clocks, ATAC-seq DA, ChIP-seq states | This skill |
| Deep pathway enrichment (ORA/GSEA multi-database) | gene-enrichment |
| Network analysis | systems-biology |
| Single-cell epigenomics | single-cell-analysis |
| Multi-omics integration | multi-omics-integration |
| Clinical variant interpretation | variant-interpretation |

---

## Multi-Agent Workflow Examples

**"Analyze my 450K methylation array data comparing tumor vs normal"**
1. Epigenomics -> QC, normalize, DMP analysis, CpG context enrichment, volcano plot
2. Gene Enrichment -> ORA/GSEA on hyper/hypo-methylated DMP genes
3. Systems Biology -> Network of epigenetically silenced tumor suppressors

**"Run an epigenetic clock on my blood methylation data"**
1. Epigenomics -> QC, apply Horvath/Hannum clocks, age acceleration comparison
2. Gene Enrichment -> Enrichment of genes near age-acceleration CpGs
3. Disease Research -> Disease associations for accelerated aging

**"Integrate ATAC-seq and RNA-seq to find regulatory regions"**
1. Epigenomics -> DA analysis, peak annotation, accessibility-expression correlation
2. Multi-Omics Integration -> Joint chromatin-expression analysis
3. Gene Enrichment -> Pathways for concordant accessibility/expression genes

**"Identify enhancers from ChIP-seq with H3K4me1 and H3K27ac"**
1. Epigenomics -> Chromatin state assignment, active vs poised enhancers
2. Systems Biology -> Enhancer-gene regulatory networks
3. Gene Enrichment -> Functional enrichment of enhancer-associated genes

**"Compare methylation with batch correction"**
1. Epigenomics -> Detect batch, include in linear model, DMP analysis, DMR, CpG annotation
2. Gene Enrichment -> Enrichment on treatment-responsive epigenetic changes
3. Disease Research -> Literature context for differentially methylated genes

## Completeness Checklist

- [ ] Methylation data loaded and format detected (beta vs M-values, platform identified)
- [ ] QC completed: probe filtering, missing value assessment, beta density plots generated
- [ ] Normalization applied with method justified (quantile, BMIQ, functional)
- [ ] Differential methylation analysis run with appropriate covariates and multiple testing correction
- [ ] CpG context enrichment reported (Island, Shore, Shelf, Open Sea)
- [ ] DMP-associated genes extracted and annotated with gene regions
- [ ] Epigenetic clock analysis performed (if age data available)
- [ ] Chromatin state assignments completed (if ChIP-seq/ATAC-seq data provided)
- [ ] Visualizations generated (volcano plot, heatmap, density plots, clock scatter)
- [ ] Evidence tier assigned to all major findings (T1-T4)
