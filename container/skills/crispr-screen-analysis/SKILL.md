---
name: crispr-screen-analysis
description: CRISPR genetic screen data analysis. Guide RNA counting, gene-level aggregation, essentiality scoring, hit calling, dropout screens, enrichment screens, fitness screens, MAGeCK-like analysis, Bayes factor scoring, quality control metrics. Use when user mentions CRISPR screen, genetic screen, guide RNA, sgRNA, gene essentiality, dropout screen, enrichment screen, MAGeCK, CRISPR knockout, CRISPRi, CRISPRa, fitness screen, or functional genomics screen.
---

# CRISPR Screen Analysis

> **Code recipes**: See [mageck-recipes.md](mageck-recipes.md) for MAGeCK CLI workflows, JACKS analysis, CRISPResso2 quantification, normalization strategies, essential gene benchmarking, and base editing screen analysis.
> **Experiment design recipes**: See [experiment-design-recipes.md](experiment-design-recipes.md) for guide RNA design, off-target analysis, library construction, delivery method selection, validation assays (T7EI, ICE/TIDE, CRISPResso2), base editing, and prime editing pegRNA design.

CRISPR genetic screen data analysis from raw guide counts to gene-level hit lists. The agent writes and executes Python code for guide-level QC, normalization, log fold change calculation, gene-level aggregation (RRA-like scoring), hit calling, essentiality analysis with Bayes Factor scoring, and quality metrics. Supports dropout (negative selection), enrichment (positive selection), and fitness screens across CRISPR knockout, CRISPRi, and CRISPRa modalities.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_crispr-screen-analysis_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Pathway enrichment analysis on a gene list (not raw screen data) → use `gene-enrichment`
- Variant-level interpretation of edited loci → use `variant-analysis`
- Druggability assessment of screen hit genes → use `drug-target-validator`
- Protein interaction network analysis of hits → use `systems-biology`
- Single-cell transcriptomic analysis (Perturb-seq) → use `single-cell-analysis`
- Disease-gene association lookup without screen data → use `disease-research`

## Cross-Reference: Other Skills

- **Pathway enrichment on screen hits** -> use gene-enrichment skill
- **Variant-level analysis of edited loci** -> use variant-analysis skill
- **Target druggability for essential genes** -> use drug-target-validator skill
- **Network analysis of hit genes** -> use systems-biology skill
- **DepMap cross-validation of screen hits** -> use `mcp__depmap__depmap_data` tools (see table below and Cross-Referencing Hits with DepMap section)

## Python Environment

Python 3 with pandas, numpy, scipy, matplotlib, seaborn, and standard library (re, csv, gzip, collections). All analysis uses pure Python/scipy implementations. No MAGeCK binary required -- the pipeline implements equivalent statistical methods in Python.

## Available MCP Tools

### `mcp__geneontology__go_data` (Gene Ontology)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_go_terms` | Search GO terms by keyword | `query`, `size`, `ontology` (molecular_function/biological_process/cellular_component), `include_obsolete` |
| `get_go_term` | Get full GO term details (definition, synonyms, xrefs) | `id` (GO:XXXXXXX) |
| `validate_go_id` | Check if GO ID is valid | `id` |
| `get_ontology_stats` | GO ontology statistics | -- |

### DepMap — Cancer Dependency Map (World's Largest CRISPR Screen)
| Tool | Method | Use |
|------|--------|-----|
| `mcp__depmap__depmap_data` | `get_gene_dependency` | CRISPR Chronos scores — reference essentiality from 1000+ cell lines |
| | `get_gene_dependency_summary` | Pan-cancer essentiality summary — common essential vs selective |
| | `get_multi_gene_profile` | Compare hit list against DepMap profiles (up to 20 genes) |
| | `get_biomarker_analysis` | Validate screen hits: does genotype predict dependency? |
| | `get_mutations` | Cross-reference screen hits with DepMap mutation data |
| | `get_copy_number` | Copy number context for screen hits |
| | `get_context_info` | Cancer lineages for context-specific analysis |

---

## Screen Types & Design

### Modalities

| Modality | Mechanism | Readout | Typical Use |
|----------|-----------|---------|-------------|
| **CRISPR-Cas9 knockout** | DSB-mediated gene disruption | Loss of function | Essentiality, resistance, synthetic lethality |
| **CRISPRi** | dCas9-KRAB transcriptional repression | Knockdown (partial) | Dosage-sensitive phenotypes, essential gene titration |
| **CRISPRa** | dCas9-VP64/p65/Rta activation | Gain of function | Sufficiency, overexpression phenotypes |

### Selection Schemes

| Screen Type | Selection | What Depletes | What Enriches | Example |
|-------------|-----------|---------------|---------------|---------|
| **Dropout / negative selection** | Cell viability/growth | Essential genes, fitness genes | Non-essential, growth suppressors | Essentiality mapping |
| **Positive selection / enrichment** | Drug treatment, sorting | Sensitizers (die with drug) | Resistance genes | Drug resistance screen |
| **Fitness screen** | Competitive growth | Growth-disadvantaged | Growth-advantaged | Synthetic lethality |
| **FACS-based** | Marker sorting | Low-marker guides | High-marker guides | Reporter/pathway screens |

### Library Design

Guides per gene: 4-10 (most libraries 4-6). Non-targeting controls: 100-1,000. Positive controls: core essential gene guides (Hart et al. 2015). MOI: 0.3-0.5 (one guide per cell). Coverage: 500-1,000x cells per guide at infection, maintain 500x+ throughout.

---

## Analysis Pipeline

### Phase 1: Guide Count QC

```
Inputs:
- Count matrix: guides (rows) x samples (columns)
- Library annotation: guide ID, gene target, guide sequence
- Sample metadata: condition, timepoint, replicate

QC checks:
1. Total reads per sample (expect > 10M for genome-wide libraries)
2. Guides with zero counts (< 5% expected in plasmid/T0)
3. Gini index of guide distribution (< 0.2 = good uniformity)
4. Skewness of count distribution
5. Correlation between replicates (Pearson r > 0.9 expected)
6. Non-targeting control guide behavior (should be neutral)
```

```python
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

# ---- Load count matrix and library annotation ----
counts = pd.read_csv("counts.csv", index_col=0)  # guides x samples
library = pd.read_csv("library.csv", index_col=0)  # guide_id -> gene, sequence

print(f"Guides: {counts.shape[0]}, Samples: {counts.shape[1]}")
print(f"Genes targeted: {library['gene'].nunique()}")
print(f"Guides per gene: {library.groupby('gene').size().describe()}")

# ---- Per-sample QC ----
sample_stats = pd.DataFrame({
    'total_reads': counts.sum(),
    'detected_guides': (counts > 0).sum(),
    'zero_count_guides': (counts == 0).sum(),
    'pct_zero': (counts == 0).sum() / counts.shape[0] * 100,
    'mean_count': counts.mean(),
    'median_count': counts.median(),
    'gini': counts.apply(lambda x: gini_index(x.values))
})

def gini_index(array):
    """Calculate Gini index of count distribution."""
    array = np.sort(array.astype(float))
    n = len(array)
    index = np.arange(1, n + 1)
    return (2 * np.sum(index * array) / (n * np.sum(array))) - (n + 1) / n

print("\nSample QC:")
print(sample_stats.to_string())

# ---- Replicate correlation ----
corr_matrix = counts.corr(method='pearson')
print("\nReplicate correlations:")
print(corr_matrix.to_string())

# ---- QC plots: log count distribution, Lorenz curve, replicate scatter ----
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
for col in counts.columns:
    axes[0].hist(np.log10(counts[col] + 1), bins=50, alpha=0.5, label=col)
axes[0].set_xlabel('log10(count + 1)'); axes[0].set_title('Guide Count Distribution')
if counts.shape[1] >= 2:
    cols = counts.columns[:2]
    axes[2].scatter(np.log10(counts[cols[0]] + 1), np.log10(counts[cols[1]] + 1), s=1, alpha=0.3)
    axes[2].set_title(f'Replicate Correlation (r={counts[cols[0]].corr(counts[cols[1]]):.3f})')
plt.tight_layout()
plt.savefig('guide_count_qc.png', dpi=150)
```

### Phase 2: Normalization

```
Methods:
1. Total count normalization: scale each sample to same total
2. Median-ratio normalization: DESeq2-style size factors
3. Control-based normalization: use non-targeting controls as reference

Decision logic:
- Default: median-ratio normalization (robust to dropout effects)
- If many guides are depleted (dropout screen): use control-based normalization
- Total count normalization is acceptable for initial exploration
```

```python
def normalize_total(counts_df, target_total=None):
    """Normalize to equal total counts per sample."""
    if target_total is None:
        target_total = counts_df.sum().median()
    scale_factors = target_total / counts_df.sum()
    return counts_df * scale_factors

def normalize_median_ratio(counts_df, pseudocount=1):
    """DESeq2-style median-ratio normalization."""
    log_counts = np.log(counts_df + pseudocount)
    geo_mean = log_counts.mean(axis=1)
    # Remove genes with zero geometric mean
    valid = geo_mean > 0
    ratios = log_counts.loc[valid].subtract(geo_mean[valid], axis=0)
    size_factors = np.exp(ratios.median(axis=0))
    return counts_df / size_factors, size_factors

def normalize_control_based(counts_df, control_guides):
    """Normalize using non-targeting control guide median."""
    ctrl_counts = counts_df.loc[control_guides]
    ctrl_median = ctrl_counts.median()
    ref_median = ctrl_median.median()
    scale_factors = ref_median / ctrl_median
    return counts_df * scale_factors, scale_factors

# Identify non-targeting controls from library annotation
ntc_guides = library[library['gene'].str.contains('Non-targeting|NTC|CTRL',
                     case=False, na=False)].index.tolist()
print(f"Non-targeting controls: {len(ntc_guides)}")

# Apply normalization
norm_counts, size_factors = normalize_median_ratio(counts)
print(f"Size factors: {size_factors.to_dict()}")
```

### Phase 3: Guide-Level Analysis

```
Log fold change calculation:
- LFC = log2(treatment / control) with pseudocount
- Pseudocount: +0.5 or +1 to avoid log(0)
- Average replicates before or after LFC calculation
- Z-score guides relative to non-targeting control distribution
```

```python
def calculate_guide_lfc(norm_counts, control_cols, treatment_cols, pseudo=0.5):
    """Calculate log2 fold change per guide."""
    ctrl_mean = norm_counts[control_cols].mean(axis=1)
    treat_mean = norm_counts[treatment_cols].mean(axis=1)
    lfc = np.log2((treat_mean + pseudo) / (ctrl_mean + pseudo))
    return lfc

# Define sample groups
control_cols = ['T0_rep1', 'T0_rep2', 'T0_rep3']
treatment_cols = ['T14_rep1', 'T14_rep2', 'T14_rep3']

guide_lfc = calculate_guide_lfc(norm_counts, control_cols, treatment_cols)
library['lfc'] = guide_lfc

# Z-score relative to non-targeting controls
ntc_lfc = guide_lfc[ntc_guides]
ntc_mean = ntc_lfc.mean()
ntc_std = ntc_lfc.std()
guide_zscore = (guide_lfc - ntc_mean) / ntc_std
library['zscore'] = guide_zscore

# Guide-level p-values (two-sided z-test against NTC distribution)
from scipy.stats import norm
guide_pval = 2 * norm.sf(np.abs(guide_zscore))
library['pvalue'] = guide_pval

print(f"NTC distribution: mean={ntc_mean:.3f}, std={ntc_std:.3f}")
print(f"Guides with |z| > 2: {(np.abs(guide_zscore) > 2).sum()}")
print(f"Guides with |z| > 3: {(np.abs(guide_zscore) > 3).sum()}")
```

### Phase 4: Gene-Level Aggregation

```
Methods for combining guide-level scores to gene-level:
1. Mean/median LFC across guides per gene
2. Second-best guide approach (robust to outliers)
3. Robust Rank Aggregation (RRA) — MAGeCK-like scoring
4. Alpha-RRA: modified RRA with alpha cutoff for top-ranked guides

Decision logic:
- Default: RRA-like scoring (most robust, handles variable guide efficiency)
- Quick analysis: mean LFC + number of concordant guides
- Conservative: second-best guide (ignores best guide, reduces false positives)
```

```python
from scipy.stats import beta as beta_dist
from statstools import multipletests  # or manual BH correction

def robust_rank_aggregation(gene_guides_ranks, n_total, alpha=0.25):
    """
    Simplified RRA scoring (MAGeCK-like).
    For each gene, takes guides ranked by LFC, computes a score based on
    how unlikely it is to see that many guides ranked so high by chance.
    """
    k = len(gene_guides_ranks)
    # Use only top-alpha fraction of guides
    n_top = max(1, int(np.ceil(k * alpha)))
    sorted_ranks = np.sort(gene_guides_ranks)[:n_top]

    # For each top guide, compute beta distribution p-value
    # Under null, rank of j-th best guide out of k follows Beta(j, k-j+1)
    p_values = []
    for j, rank in enumerate(sorted_ranks):
        u = rank / n_total  # uniform(0,1) under null
        p = beta_dist.cdf(u, j + 1, k - j)
        p_values.append(p)

    # RRA score = minimum p-value across top guides
    rra_score = min(p_values)
    return rra_score

def gene_level_analysis(library_df, lfc_col='lfc', gene_col='gene'):
    """Compute gene-level statistics from guide-level data."""
    # Rank all guides by LFC (ascending for dropout, descending for enrichment)
    n_total = len(library_df)

    # Dropout analysis: rank by ascending LFC (most depleted first)
    library_df['rank_neg'] = library_df[lfc_col].rank(method='min')
    # Enrichment analysis: rank by descending LFC (most enriched first)
    library_df['rank_pos'] = (-library_df[lfc_col]).rank(method='min')

    gene_results = []
    for gene, guides in library_df.groupby(gene_col):
        if gene.startswith('Non-targeting') or 'NTC' in gene.upper():
            continue
        n_guides = len(guides)
        mean_lfc = guides[lfc_col].mean()
        sorted_lfc = guides[lfc_col].sort_values()
        rra_neg = robust_rank_aggregation(guides['rank_neg'].values, n_total)
        rra_pos = robust_rank_aggregation(guides['rank_pos'].values, n_total)
        n_concordant = (guides[lfc_col] < 0).sum() if mean_lfc < 0 else (guides[lfc_col] > 0).sum()
        gene_results.append({
            'gene': gene, 'n_guides': n_guides, 'mean_lfc': mean_lfc,
            'median_lfc': guides[lfc_col].median(),
            'second_best_neg': sorted_lfc.iloc[1] if n_guides >= 2 else sorted_lfc.iloc[0],
            'rra_score_neg': rra_neg, 'rra_score_pos': rra_pos,
            'n_concordant': n_concordant, 'pct_concordant': n_concordant / n_guides * 100
        })

    gene_df = pd.DataFrame(gene_results)

    # FDR correction (Benjamini-Hochberg)
    gene_df['fdr_neg'] = bh_correction(gene_df['rra_score_neg'].values)
    gene_df['fdr_pos'] = bh_correction(gene_df['rra_score_pos'].values)

    return gene_df.sort_values('rra_score_neg')

def bh_correction(pvalues):
    """Benjamini-Hochberg FDR correction."""
    n = len(pvalues)
    ranked = np.argsort(pvalues)
    adjusted = np.zeros(n)
    cummin = 1.0
    for i in range(n - 1, -1, -1):
        idx = ranked[i]
        adjusted[idx] = min(cummin, pvalues[idx] * n / (i + 1))
        cummin = min(cummin, adjusted[idx])
    return adjusted

# Run gene-level analysis
gene_results = gene_level_analysis(library)
print(f"\nGene-level results: {len(gene_results)} genes")
print(f"Significant dropout (FDR < 0.05): {(gene_results['fdr_neg'] < 0.05).sum()}")
print(f"Significant enrichment (FDR < 0.05): {(gene_results['fdr_pos'] < 0.05).sum()}")
print(gene_results.head(20)[['gene', 'n_guides', 'mean_lfc', 'rra_score_neg', 'fdr_neg']])
```

### Phase 5: Hit Calling

```
Criteria for calling a gene as a hit:
1. FDR < 0.05 (from RRA or equivalent test)
2. |mean LFC| > threshold (typically 0.5-1.0 for dropout screens)
3. >= 2 concordant guides (out of 4-6 total)
4. Passes non-targeting control benchmarks

For dropout screens: FDR_neg < 0.05 AND mean_lfc < -0.5
For enrichment screens: FDR_pos < 0.05 AND mean_lfc > 0.5
```

```python
def call_hits(gene_df, fdr_thresh=0.05, lfc_thresh=0.5, min_concordant=2):
    """Call dropout and enrichment hits."""
    dropout_hits = gene_df[
        (gene_df['fdr_neg'] < fdr_thresh) &
        (gene_df['mean_lfc'] < -lfc_thresh) &
        (gene_df['n_concordant'] >= min_concordant)
    ].copy()
    dropout_hits['direction'] = 'dropout'

    enrichment_hits = gene_df[
        (gene_df['fdr_pos'] < fdr_thresh) &
        (gene_df['mean_lfc'] > lfc_thresh) &
        (gene_df['n_concordant'] >= min_concordant)
    ].copy()
    enrichment_hits['direction'] = 'enrichment'

    print(f"Dropout hits (FDR<{fdr_thresh}, LFC<-{lfc_thresh}): {len(dropout_hits)}")
    print(f"Enrichment hits (FDR<{fdr_thresh}, LFC>{lfc_thresh}): {len(enrichment_hits)}")
    return dropout_hits, enrichment_hits

dropout_hits, enrichment_hits = call_hits(gene_results)

# ---- Volcano plot ----
fig, ax = plt.subplots(figsize=(10, 8))
gene_results['neg_log10_fdr'] = -np.log10(gene_results['fdr_neg'].clip(lower=1e-300))
colors = np.where(
    (gene_results['fdr_neg'] < 0.05) & (gene_results['mean_lfc'] < -0.5), 'blue',
    np.where((gene_results['fdr_pos'] < 0.05) & (gene_results['mean_lfc'] > 0.5), 'red', 'grey'))
ax.scatter(gene_results['mean_lfc'], gene_results['neg_log10_fdr'], c=colors, s=8, alpha=0.6)
for _, row in gene_results.head(10).iterrows():
    ax.annotate(row['gene'], (row['mean_lfc'], row['neg_log10_fdr']), fontsize=7)
ax.axhline(-np.log10(0.05), ls='--', color='black', lw=0.5)
ax.axvline(-0.5, ls='--', color='black', lw=0.5); ax.axvline(0.5, ls='--', color='black', lw=0.5)
ax.set_xlabel('Mean log2 Fold Change'); ax.set_ylabel('-log10(FDR)')
ax.set_title('CRISPR Screen Volcano Plot')
plt.tight_layout()
plt.savefig('screen_volcano.png', dpi=150)
```

### Phase 6: Essential Gene Analysis

```
Reference gene sets:
- Core essential genes (CEG): Hart et al. 2015, 2017 (~680 genes)
  Genes required for viability across all cell lines
- Non-essential genes (NEG): Hart et al. 2014 (~920 genes)
  Genes dispensable for viability in most cell lines
- Common essential (DepMap): genes essential in >90% of cell lines

Bayes Factor (BF) scoring:
- Compare guide LFC distribution to essential vs non-essential reference
- BF > 5: likely essential
- BF < -5: likely non-essential
- -5 < BF < 5: ambiguous

Quality metrics using reference sets:
- NNMD: normalized null-model distance between essential and non-essential
- AUC-ROC: separation of essential vs non-essential by screen LFC
- Precision-recall at various thresholds
```

```python
from scipy.stats import gaussian_kde

# Reference gene sets (user provides or use built-in lists)
CORE_ESSENTIAL = [
    'RPS14', 'RPL11', 'RPS19', 'RPL5', 'SF3B1', 'POLR2A', 'POLR2B',
    'RPA1', 'RPA2', 'PSMA1', 'PSMA2', 'PSMD1', 'COPS5', 'EEF2',
    'PCNA', 'RFC4', 'MCM2', 'MCM4', 'MCM7', 'CDC45', 'CDK1',
    # ... typically ~680 genes loaded from file
]

NON_ESSENTIAL = [
    'ADRA1A', 'ADRA1B', 'ADRB1', 'ADRB3', 'CHRM1', 'CHRM2', 'CHRM4',
    'DRD1', 'DRD2', 'DRD3', 'DRD4', 'DRD5', 'GRM2', 'GRM3',
    'HTR1A', 'HTR1B', 'HTR2A', 'HTR5A', 'OPRD1', 'OPRK1', 'OPRM1',
    # ... typically ~920 genes loaded from file
]

def bayes_factor_scoring(gene_df, essential_genes, nonessential_genes, lfc_col='mean_lfc'):
    """Calculate Bayes Factor for essentiality."""
    ess_lfc = gene_df[gene_df['gene'].isin(essential_genes)][lfc_col].dropna()
    noness_lfc = gene_df[gene_df['gene'].isin(nonessential_genes)][lfc_col].dropna()

    if len(ess_lfc) < 10 or len(noness_lfc) < 10:
        print("WARNING: Too few reference genes found. Check gene symbol format.")
        return gene_df

    # Fit KDEs
    kde_ess = gaussian_kde(ess_lfc.values)
    kde_noness = gaussian_kde(noness_lfc.values)

    # Calculate BF for each gene
    all_lfc = gene_df[lfc_col].values
    log_ess = np.log(kde_ess(all_lfc) + 1e-300)
    log_noness = np.log(kde_noness(all_lfc) + 1e-300)
    gene_df['bayes_factor'] = log_ess - log_noness

    return gene_df

def screen_quality_metrics(gene_df, essential_genes, nonessential_genes, lfc_col='mean_lfc'):
    """Calculate NNMD and AUC-ROC using reference gene sets."""
    ess_lfc = gene_df[gene_df['gene'].isin(essential_genes)][lfc_col].dropna()
    noness_lfc = gene_df[gene_df['gene'].isin(nonessential_genes)][lfc_col].dropna()
    nnmd = (noness_lfc.median() - ess_lfc.median()) / ess_lfc.mad()
    from sklearn.metrics import roc_auc_score
    labels = np.concatenate([np.ones(len(ess_lfc)), np.zeros(len(noness_lfc))])
    scores = np.concatenate([-ess_lfc.values, -noness_lfc.values])
    auc = roc_auc_score(labels, scores)
    print(f"NNMD: {nnmd:.2f} ({'Good' if nnmd > 2.5 else 'Poor'})")
    print(f"AUC-ROC: {auc:.3f} ({'Good' if auc > 0.85 else 'Poor'})")
    return {'nnmd': nnmd, 'auc': auc}

# Run essentiality analysis
gene_results = bayes_factor_scoring(gene_results, CORE_ESSENTIAL, NON_ESSENTIAL)
qc_metrics = screen_quality_metrics(gene_results, CORE_ESSENTIAL, NON_ESSENTIAL)

# ---- Essential vs non-essential distribution plot ----
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
ess_lfc = gene_results[gene_results['gene'].isin(CORE_ESSENTIAL)]['mean_lfc']
noness_lfc = gene_results[gene_results['gene'].isin(NON_ESSENTIAL)]['mean_lfc']
axes[0].hist(ess_lfc, bins=40, alpha=0.6, label='Essential', color='red', density=True)
axes[0].hist(noness_lfc, bins=40, alpha=0.6, label='Non-essential', color='blue', density=True)
axes[0].set_xlabel('Mean log2 Fold Change'); axes[0].legend()
axes[0].set_title(f'Essential vs Non-Essential (NNMD={qc_metrics["nnmd"]:.2f})')
# Precision-recall curve
from sklearn.metrics import precision_recall_curve, average_precision_score
labels = np.concatenate([np.ones(len(ess_lfc)), np.zeros(len(noness_lfc))])
scores = np.concatenate([-ess_lfc.values, -noness_lfc.values])
prec, rec, _ = precision_recall_curve(labels, scores)
axes[1].plot(rec, prec, color='darkblue')
axes[1].set_xlabel('Recall'); axes[1].set_ylabel('Precision')
axes[1].set_title(f'Precision-Recall (AP={average_precision_score(labels, scores):.3f})')
plt.tight_layout()
plt.savefig('essentiality_qc.png', dpi=150)
```

### Phase 7: Pathway Enrichment of Hits

```
After identifying screen hits, perform pathway enrichment to
understand biological themes. Hand off to gene-enrichment skill for
deep analysis, or run quick enrichment with gseapy.

GO term resolution for screen hit enrichment:
- mcp__geneontology__go_data(method: "search_go_terms", query: "cell proliferation", ontology: "biological_process", size: 10)
  → Resolve GO terms from enrichment results to canonical IDs for screen hit annotation
- mcp__geneontology__go_data(method: "get_go_term", id: "GO:0008283")
  → Validate enriched GO term and retrieve full definition, synonyms, and cross-references
```

```python
import gseapy as gp

# ORA on dropout hits
dropout_gene_list = dropout_hits['gene'].tolist()
if len(dropout_gene_list) >= 5:
    enr_dropout = gp.enrichr(
        gene_list=dropout_gene_list,
        gene_sets=['KEGG_2021_Human', 'GO_Biological_Process_2021',
                   'Reactome_2022', 'MSigDB_Hallmark_2020'],
        organism='human',
        outdir='enrichment_dropout'
    )
    print("\nTop enriched pathways (dropout hits):")
    print(enr_dropout.results.sort_values('Adjusted P-value').head(10)[
        ['Term', 'Gene_set', 'Overlap', 'Adjusted P-value', 'Genes']])

# Ranked GSEA using gene-level LFC
gene_ranking = gene_results[['gene', 'mean_lfc']].dropna().sort_values('mean_lfc')
gene_ranking.to_csv('gene_ranking.rnk', sep='\t', header=False, index=False)
gsea_res = gp.prerank(rnk='gene_ranking.rnk', gene_sets='KEGG_2021_Human',
                      outdir='gsea_results', min_size=15, max_size=500, permutation_num=1000)
print("\nGSEA top results:")
print(gsea_res.res2d.sort_values('FDR q-val').head(10)[['Term', 'NES', 'FDR q-val']])
```

---

## Quality Metrics Reference

| Metric | Good | Acceptable | Poor | Description |
|--------|------|------------|------|-------------|
| **Gini index** | < 0.1 | 0.1-0.2 | > 0.2 | Uniformity of guide representation |
| **Zero-count guides** | < 1% | 1-5% | > 5% | Fraction of undetected guides |
| **Replicate correlation** | > 0.95 | 0.85-0.95 | < 0.85 | Pearson r between replicates |
| **NNMD** | > 4 | 2.5-4 | < 2.5 | Separation of essential vs non-essential |
| **AUC (essential)** | > 0.95 | 0.85-0.95 | < 0.85 | ROC AUC for essential gene detection |
| **Library coverage** | > 95% | 90-95% | < 90% | Fraction of library guides detected |
| **NTC behavior** | centered at 0 | slight shift | strong shift | Non-targeting control LFC distribution |

---

## Screen Design Considerations

| Parameter | Recommendation | Notes |
|-----------|---------------|-------|
| **MOI** | 0.3-0.5 | Ensures single guide per cell; >0.5 confounds assignment |
| **Coverage** | 500-1000x at infection | Maintain >=500x throughout; count cells/guides at harvest |
| **Replicates** | >=3 biological | Include plasmid DNA and/or T0 as reference |
| **Timepoints** | 10-14 doublings (dropout) | <7 may miss slow effects; >20 loses dynamic range |
| **Negative controls** | 500-1000 NTC guides | Also use safe-harbor guides (AAVS1, ROSA26) |
| **Positive controls** | Core essential guides | Validate dropout signal in every screen |

---

## Evidence Grading

### Screen Hit Evidence Tiers

| Tier | Criteria | Confidence |
|------|----------|------------|
| **T1 (Highest)** | FDR < 0.01, >= 3 concordant guides, effect in independent screen, known biology | High |
| **T2** | FDR < 0.05, >= 2 concordant guides, pathway enrichment support | Medium-High |
| **T3** | FDR < 0.05, mean LFC significant but few concordant guides, single screen | Medium |
| **T4 (Lowest)** | FDR 0.05-0.1, or single guide driving signal, no independent validation | Low |

### Grading Logic

```
T1 criteria (HIGH confidence hit):
  - Gene FDR < 0.01 (RRA or equivalent)
  - >= 3 of 4+ guides concordant in direction
  - Effect replicated in independent screen dataset (DepMap via `get_gene_dependency`, published)
  - Gene has known role in relevant biology

T2 criteria (MEDIUM-HIGH confidence hit):
  - Gene FDR < 0.05
  - >= 2 concordant guides
  - Gene found in enriched pathway (GO/KEGG/Reactome, adj. p < 0.05)
  - Supported by gene-disease association (Open Targets score > 0.3)

T3 criteria (MEDIUM confidence hit):
  - Gene FDR < 0.05
  - Mean LFC passes threshold
  - Fewer concordant guides or weaker pathway support
  - Single screen evidence only

T4 criteria (LOW confidence, flag for validation):
  - Marginal FDR (0.05-0.1)
  - Signal driven by single guide (possible off-target)
  - No pathway enrichment or known biology support
  - Recommend individual guide validation
```

---

## Cross-Referencing Hits with DepMap

After calling hits from a custom CRISPR screen, cross-reference against DepMap (the world's largest CRISPR screen across 1000+ cell lines) to contextualize findings.

### Step 1: Look Up Each Hit's DepMap Dependency Profile

Take top hits and query their pan-cancer dependency:

```
# Single gene lookup — get Chronos scores across all DepMap cell lines
mcp__depmap__depmap_data(method: "get_gene_dependency", gene: "MYC")

# Batch lookup — compare up to 20 screen hits at once
mcp__depmap__depmap_data(method: "get_multi_gene_profile", genes: ["MYC", "TP53", "KRAS", "BRAF", "CDK4", "RB1"])
```

### Step 2: Get Pan-Cancer Essentiality Summary

Determine whether each hit is a common essential (depleted everywhere) or selectively essential (context-specific):

```
mcp__depmap__depmap_data(method: "get_gene_dependency_summary", gene: "CDK4")
```

- **Common essential** (depleted in >90% of lines): likely a general fitness gene, not a novel hit
- **Selective dependency** (depleted in specific lineages): potentially interesting context-specific target
- **Not in DepMap / no dependency**: novel hit unique to your screen — highest priority for validation

### Step 3: Distinguish Novel Hits from Known Essentials

```python
# After retrieving DepMap profiles for all hits, classify them
novel_hits = []       # Not essential in DepMap — unique to your screen
known_essential = []  # Common essential in DepMap — expected finding
selective = []        # Selectively essential — context-specific

for gene in screen_hits:
    # Query DepMap summary
    # mcp__depmap__depmap_data(method: "get_gene_dependency_summary", gene: gene)
    # Classify based on fraction of cell lines with Chronos < -0.5
    if depmap_fraction_dependent < 0.1:
        novel_hits.append(gene)      # Rarely essential in DepMap
    elif depmap_fraction_dependent > 0.9:
        known_essential.append(gene)  # Common essential
    else:
        selective.append(gene)        # Selectively essential
```

### Step 4: Check Lineage Specificity of Hits

For selectively essential genes, determine which cancer lineages show dependency:

```
# Get available lineages and disease contexts
mcp__depmap__depmap_data(method: "get_context_info")

# Check dependency in specific lineage
mcp__depmap__depmap_data(method: "get_gene_dependency", gene: "BRAF", lineage: "skin")
```

Compare your screen's cell line lineage against DepMap lineage-specific profiles. A gene essential in your melanoma screen that is also selectively essential in DepMap skin lineage lines increases confidence in the finding.

### Step 5: Use Biomarker Analysis to Find Predictive Mutations

For validated hits, identify genomic features that predict dependency — this reveals the patient population most likely to respond:

```
# Find mutations/features that predict dependency on a gene
mcp__depmap__depmap_data(method: "get_biomarker_analysis", gene: "BRAF")

# Cross-reference with mutation data
mcp__depmap__depmap_data(method: "get_mutations", gene: "BRAF")

# Check copy number context
mcp__depmap__depmap_data(method: "get_copy_number", gene: "MYC")
```

If biomarker analysis reveals that BRAF V600E mutation predicts BRAF dependency, this validates a genotype-to-dependency link and identifies a targetable patient subgroup.

---

## Multi-Agent Workflow Examples

**"Analyze my CRISPR knockout screen for essential genes"**
1. CRISPR Screen Analysis -> Guide QC, normalization, LFC, RRA scoring, Bayes Factor essentiality, quality metrics
2. Gene Enrichment -> ORA/GSEA on essential gene hits across GO/KEGG/Reactome
3. Systems Biology -> Protein interaction network of essential genes, module detection

**"Find drug resistance genes from my CRISPR enrichment screen"**
1. CRISPR Screen Analysis -> Guide QC, normalization, enrichment-direction RRA scoring, hit calling
2. Drug Target Validator -> Druggability assessment for resistance hits, existing compounds
3. Gene Enrichment -> Pathway analysis of resistance mechanisms

**"Compare CRISPR screen results between two cell lines"**
1. CRISPR Screen Analysis -> Run pipeline independently on each cell line, compare hit lists
2. Gene Enrichment -> Differential pathway enrichment between cell-line-specific hits
3. Systems Biology -> Network comparison, shared vs unique essential pathways

**"Validate my CRISPR screen hits against DepMap and find novel targets"**
1. CRISPR Screen Analysis -> Guide QC, normalization, RRA scoring, hit calling
2. Cross-reference hits with DepMap -> `get_multi_gene_profile` for batch lookup, `get_gene_dependency_summary` to classify common essential vs selective vs novel
3. DepMap lineage analysis -> `get_context_info` + `get_gene_dependency` with lineage filter for context-specific validation
4. Biomarker discovery -> `get_biomarker_analysis` + `get_mutations` to find predictive genotypes for top novel/selective hits
5. Drug Target Validator -> Druggability assessment for validated novel targets

**"Run a CRISPRi fitness screen analysis with quality control"**
1. CRISPR Screen Analysis -> Guide QC (Gini, representation), normalization, LFC, gene scoring, NNMD/AUC metrics
2. Gene Enrichment -> Functional enrichment of fitness genes
3. Drug Target Validator -> Therapeutic potential of fitness-modifying genes

## Completeness Checklist

- [ ] Guide count QC performed (total reads, zero-count guides, Gini index, replicate correlation)
- [ ] Normalization method selected and justified (median-ratio, control-based, or total count)
- [ ] Log fold change calculated with pseudocount and z-scored against non-targeting controls
- [ ] Gene-level aggregation performed using RRA or equivalent robust method
- [ ] Hit calling criteria specified (FDR threshold, LFC threshold, minimum concordant guides)
- [ ] Screen quality metrics reported (NNMD, AUC-ROC for essential vs non-essential separation)
- [ ] Evidence tier assigned to each hit (T1-T4 based on FDR, concordance, and validation)
- [ ] Top hits cross-referenced against DepMap for common essential vs selective vs novel classification
- [ ] Volcano plot and essential/non-essential distribution plots generated
- [ ] Pathway enrichment performed on hit list (ORA and/or ranked GSEA)
