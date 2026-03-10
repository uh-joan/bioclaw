---
name: proteomics-analysis
description: Proteomics and mass spectrometry data analysis. Protein quantification, differential expression, PTM analysis, pathway enrichment, label-free quantification, TMT/iTRAQ, DIA/DDA, MaxQuant output processing. Use when user mentions proteomics, mass spectrometry, protein expression, label-free quantification, TMT, iTRAQ, DIA, DDA, MaxQuant, protein identification, post-translational modification, PTM, phosphoproteomics, ubiquitomics, acetylomics, or protein abundance.
---

# Proteomics Analysis

Mass spectrometry-based proteomics data analysis covering label-free quantification (LFQ), tandem mass tag (TMT/iTRAQ) labeled quantification, and data-independent acquisition (DIA) workflows. The agent writes and executes Python code for the full pipeline: data loading, QC, normalization, imputation, differential expression, PTM analysis, enrichment, and visualization.

## Report-First Workflow

1. **Create report file immediately**: `[experiment]_proteomics_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## Cross-Reference: Other Skills

- **Multi-omics integration with transcriptomics** -> use multi-omics-integration skill
- **Systems-level pathway and network analysis** -> use systems-biology skill
- **Pathway enrichment on DE protein lists** -> use gene-enrichment skill
- **Protein interaction network construction** -> use network-pharmacologist skill

## When NOT to Use This Skill

- Integrating proteomics with transcriptomics or other omics layers → use `multi-omics-integration`
- Dynamic pathway modeling or systems-level network analysis → use `systems-biology`
- Deep multi-database pathway enrichment (GO/KEGG/Reactome) → use `gene-enrichment`
- Protein interaction network construction and topology analysis → use `network-pharmacologist`
- Protein 3D structure retrieval or binding site analysis → use `protein-structure-retrieval`
- Metabolomics data processing or metabolite identification → use `metabolomics-analysis`

## Available MCP Tools

### `mcp__uniprot__uniprot_data` (Protein Identification & Annotation)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_protein_info` | Full protein profile | `accession`, `format` |
| `search_proteins` | Search proteins by name/keyword | `query`, `organism`, `size` |
| `search_by_gene` | Find proteins by gene name | `gene`, `organism`, `size` |
| `get_protein_features` | Protein features (domains, sites, PTMs) | `accession` |
| `batch_protein_lookup` | Batch lookup 1-100 proteins | `accessions` |
| `get_protein_sequence` | Get protein sequence (FASTA/JSON) | `accession`, `format` |
| `analyze_sequence_composition` | Amino acid composition analysis | `accession` |
| `get_external_references` | Cross-database references | `accession` |

### `mcp__reactome__reactome_data` (Pathway Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `find_pathways_by_gene` | Pathways containing a gene | `gene_id`, `species` |
| `get_pathway_details` | Full pathway info | `pathway_id` |
| `get_pathway_participants` | Molecules in a pathway | `pathway_id` |

### `mcp__geneontology__go_data` (Gene Ontology)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_go_terms` | Search GO terms by keyword | `query`, `size`, `ontology` (molecular_function/biological_process/cellular_component), `include_obsolete` |
| `get_go_term` | Get full GO term details (definition, synonyms, xrefs) | `id` (GO:XXXXXXX) |
| `validate_go_id` | Check if GO ID is valid | `id` |
| `get_ontology_stats` | GO ontology statistics | -- |

## Python Environment

Python 3 with scipy, statsmodels, pandas, numpy, scikit-learn, matplotlib available in the container. All statistical methods implemented in Python using scipy.stats and statsmodels. No R required.

---

## Data Input Formats

| Format | Source | Key Columns | Notes |
|--------|--------|-------------|-------|
| **proteinGroups.txt** | MaxQuant | `Protein IDs`, `Gene names`, `LFQ intensity *` | Filter `Reverse`, `Potential contaminant`, `Only identified by site` |
| **evidence.txt** | MaxQuant | `Modified sequence`, `Intensity`, `Experiment` | Peptide-level for PTM analysis |
| **Spectronaut report** | Spectronaut | `PG.ProteinGroups`, `PG.Quantity` | Long or wide format, DIA output |
| **DIA-NN report** | DIA-NN | `Protein.Group`, `Genes`, `Precursor.Quantity` | Tab-separated main report |
| **Generic matrix** | Any | Protein IDs as rows, sample intensities as columns | CSV or TSV |

```python
import pandas as pd
import numpy as np

def load_proteomics_data(file_path, source="auto"):
    """Load proteomics data with auto-detection of search engine output."""
    df = pd.read_csv(file_path, sep='\t' if file_path.endswith('.txt') else ',', low_memory=False)
    if source == "auto":
        cols = set(df.columns)
        if 'Protein IDs' in cols and 'Gene names' in cols:
            source = "maxquant"
        elif 'PG.ProteinGroups' in cols:
            source = "spectronaut"
        elif 'Protein.Group' in cols:
            source = "diann"
        else:
            source = "generic"
    loaders = {"maxquant": load_maxquant, "spectronaut": load_spectronaut,
               "diann": load_diann, "generic": load_generic}
    return loaders[source](df)

def load_maxquant(df):
    n_before = len(df)
    for col in ['Reverse', 'Potential contaminant', 'Only identified by site']:
        if col in df.columns:
            df = df[df[col] != '+']
    print(f"Filtered: {n_before} -> {len(df)} protein groups")
    # Extract LFQ > iBAQ > raw intensity columns
    for prefix in ['LFQ intensity ', 'iBAQ ', 'Intensity ']:
        cols = [c for c in df.columns if c.startswith(prefix)]
        if cols:
            intensity_df = df[cols].copy()
            intensity_df.columns = [c.replace(prefix, '') for c in cols]
            break
    intensity_df.index = df['Protein IDs'].values
    gene_names = df['Gene names'].values if 'Gene names' in df.columns else None
    return intensity_df.replace(0, np.nan), gene_names

def load_spectronaut(df):
    if 'R.FileName' in df.columns:
        pivot = df.pivot_table(index='PG.ProteinGroups', columns='R.FileName', values='PG.Quantity', aggfunc='first')
        return pivot.replace(0, np.nan), None
    quant_cols = [c for c in df.columns if 'Quantity' in c and c != 'PG.Quantity']
    intensity_df = df.set_index('PG.ProteinGroups')[quant_cols].replace(0, np.nan)
    return intensity_df, None

def load_diann(df):
    protein_quant = df.pivot_table(index='Protein.Group', columns='Run', values='Precursor.Quantity', aggfunc='sum')
    return protein_quant.replace(0, np.nan), None

def load_generic(df):
    df = df.set_index(df.columns[0])
    return df.select_dtypes(include=[np.number]).replace(0, np.nan), None
```

---

## Analysis Pipeline

### Phase 1: Data Loading & QC

```python
intensity_df, gene_names = load_proteomics_data("proteinGroups.txt")
print(f"Proteins: {intensity_df.shape[0]}, Samples: {intensity_df.shape[1]}")

# Missing value assessment
missing_pct = intensity_df.isna().sum().sum() / intensity_df.size * 100
print(f"Total missing: {missing_pct:.1f}%")

# Filter: require >= 50% valid values per protein
min_valid = int(intensity_df.shape[1] * 0.5)
intensity_filtered = intensity_df[intensity_df.notna().sum(axis=1) >= min_valid].copy()
print(f"Proteins after filtering: {intensity_filtered.shape[0]}")

# Log2 transform and QC plots
log2_data = np.log2(intensity_filtered)

import matplotlib.pyplot as plt
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
# Box plot of distributions
axes[0,0].boxplot([log2_data[c].dropna().values for c in log2_data.columns],
                   labels=log2_data.columns)
axes[0,0].set_title('Log2 Intensity Distributions'); axes[0,0].tick_params(axis='x', rotation=45)
# Missing values per sample
miss_per_sample = intensity_filtered.isna().sum(axis=0) / intensity_filtered.shape[0] * 100
axes[0,1].bar(range(len(miss_per_sample)), miss_per_sample.values)
axes[0,1].set_title('Missing Values per Sample (%)')
# Protein count per sample
axes[1,0].bar(range(len(intensity_filtered.columns)), intensity_filtered.notna().sum(axis=0).values)
axes[1,0].set_title('Identified Proteins per Sample')
# Intensity histogram
vals = log2_data.values.flatten(); vals = vals[~np.isnan(vals)]
axes[1,1].hist(vals, bins=80, alpha=0.7); axes[1,1].set_title('Overall Intensity Distribution')
plt.tight_layout(); plt.savefig('qc_overview.png', dpi=150)
```

### Phase 2: Normalization

```python
def median_normalization(log2_df):
    """Subtract column median, re-center to global median."""
    global_median = log2_df.median().median()
    return log2_df.subtract(log2_df.median(axis=0), axis=1).add(global_median)

def quantile_normalization(log2_df):
    """Force identical distributions across samples."""
    rank_mean = log2_df.stack().groupby(
        log2_df.rank(method='first').stack().astype(int).values).mean()
    return log2_df.rank(method='min').stack().map(rank_mean).unstack()

def vsn_like_normalization(log2_df):
    """Variance-stabilizing normalization via rank-based inverse normal."""
    from scipy.stats import rankdata, norm
    result = log2_df.copy()
    for col in result.columns:
        valid = result[col].dropna()
        result.loc[valid.index, col] = norm.ppf(rankdata(valid.values) / (len(valid) + 1))
    return result

# Decision: check median range across samples
median_range = log2_data.median().max() - log2_data.median().min()
if median_range < 1.0:
    normalized = median_normalization(log2_data)  # default
elif median_range < 3.0:
    normalized = quantile_normalization(log2_data)
else:
    print("WARNING: large median differences -- check sample quality")
    normalized = median_normalization(log2_data)
```

### Phase 3: Missing Value Imputation

```python
from sklearn.impute import KNNImputer

def impute_minprob(log2_df, shift=1.8, scale=0.3):
    """MinProb: draw from left-shifted normal (MNAR assumption)."""
    imputed = log2_df.copy()
    for col in imputed.columns:
        valid = imputed[col].dropna()
        if len(valid) == 0: continue
        n_miss = imputed[col].isna().sum()
        if n_miss > 0:
            imputed.loc[imputed[col].isna(), col] = np.random.normal(
                valid.mean() - shift * valid.std(), valid.std() * scale, n_miss)
    return imputed

def impute_knn(log2_df, n_neighbors=5):
    """KNN imputation (MCAR assumption)."""
    imp = KNNImputer(n_neighbors=n_neighbors)
    arr = imp.fit_transform(log2_df.T.values)
    return pd.DataFrame(arr.T, index=log2_df.index, columns=log2_df.columns)

def impute_mixed(log2_df, group_labels):
    """Mixed: MinProb for low-abundance missing (MNAR), KNN for random missing (MCAR)."""
    imputed = log2_df.copy()
    global_mean = log2_df.mean().mean()
    for protein in log2_df.index:
        if log2_df.loc[protein].isna().sum() == 0: continue
        observed_mean = log2_df.loc[protein].dropna().mean()
        if observed_mean < global_mean - 1:  # MNAR heuristic
            row = impute_minprob(log2_df.loc[[protein]])
        else:
            valid_count = log2_df.loc[protein].notna().sum()
            if valid_count >= 2:
                row = impute_knn(log2_df.loc[[protein]], n_neighbors=min(5, valid_count - 1))
            else:
                row = impute_minprob(log2_df.loc[[protein]])
        imputed.loc[protein] = row.loc[protein]
    return imputed

# Default: mixed imputation
imputed = impute_mixed(normalized, group_labels)
```

### Phase 4: Differential Expression

```python
from scipy import stats
from statsmodels.stats.multitest import multipletests

def differential_expression(imputed_df, group_labels, group1, group2, gene_names=None):
    """Welch's t-test per protein with Benjamini-Hochberg correction."""
    s_g1 = [s for s, g in group_labels.items() if g == group1]
    s_g2 = [s for s, g in group_labels.items() if g == group2]
    results = []
    for protein in imputed_df.index:
        v1 = imputed_df.loc[protein, s_g1].astype(float).dropna().values
        v2 = imputed_df.loc[protein, s_g2].astype(float).dropna().values
        if len(v1) < 2 or len(v2) < 2: continue
        log2fc = np.mean(v1) - np.mean(v2)
        t_stat, p_val = stats.ttest_ind(v1, v2, equal_var=False)
        results.append({'protein': protein, 'log2FC': log2fc,
                        'mean_g1': np.mean(v1), 'mean_g2': np.mean(v2),
                        't_statistic': t_stat, 'pvalue': p_val})
    results_df = pd.DataFrame(results)
    reject, padj, _, _ = multipletests(results_df['pvalue'].dropna(), method='fdr_bh')
    results_df.loc[results_df['pvalue'].notna(), 'padj'] = padj
    if gene_names is not None:
        p2g = dict(zip(imputed_df.index, gene_names))
        results_df['gene'] = results_df['protein'].map(p2g)
    return results_df.sort_values('pvalue')

de_results = differential_expression(imputed, group_labels, 'treatment', 'control', gene_names)
sig = de_results[(de_results['padj'] < 0.05) & (de_results['log2FC'].abs() > 1)]
print(f"Significant: {len(sig)} (Up: {(sig['log2FC']>0).sum()}, Down: {(sig['log2FC']<0).sum()})")
de_results.to_csv('de_all_results.csv', index=False)
sig.to_csv('de_significant_proteins.csv', index=False)
```

### Phase 5: Enrichment Analysis

```python
from scipy.stats import hypergeom

def ora_enrichment(de_genes, bg_genes, gene_sets, min_overlap=3):
    """Over-Representation Analysis with hypergeometric test + BH correction."""
    N, n = len(bg_genes), len(de_genes)
    de_set, bg_set = set(de_genes), set(bg_genes)
    results = []
    for pathway, pathway_genes in gene_sets.items():
        K = len(pathway_genes & bg_set)
        if K < 5 or K > 500: continue
        k = len(de_set & pathway_genes & bg_set)
        if k < min_overlap: continue
        pval = hypergeom.sf(k - 1, N, K, n)
        results.append({'pathway': pathway, 'overlap': k, 'pathway_size': K,
                        'gene_ratio': k/n, 'pvalue': pval,
                        'genes': ';'.join(sorted(de_set & pathway_genes))})
    if not results: return pd.DataFrame()
    df = pd.DataFrame(results)
    _, padj, _, _ = multipletests(df['pvalue'], method='fdr_bh')
    df['padj'] = padj
    return df.sort_values('padj')

def load_gmt(gmt_path):
    """Load gene sets from GMT file."""
    gene_sets = {}
    with open(gmt_path) as f:
        for line in f:
            parts = line.strip().split('\t')
            gene_sets[parts[0]] = set(parts[2:])
    return gene_sets

# Rank proteins for GSEA: -log10(pvalue) * sign(log2FC)
de_results['rank_score'] = -np.log10(de_results['pvalue'].clip(lower=1e-300)) * np.sign(de_results['log2FC'])

# Reactome pathway enrichment for DE proteins:
# mcp__reactome__reactome_data(method: "find_pathways_by_gene", gene_id: "DE_GENE", species: "Homo sapiens")
#   -> Map DE proteins to Reactome pathways for enrichment context
# mcp__reactome__reactome_data(method: "get_pathway_participants", pathway_id: "R-HSA-XXXXX")
#   -> Get all pathway members to calculate enrichment overlap

# Annotate DE proteins with UniProt data:
# mcp__uniprot__uniprot_data(method: "batch_protein_lookup", accessions: ["P00533", "P04637", ...])
#   -> Batch retrieve protein annotations for all significant DE proteins
#
# mcp__uniprot__uniprot_data(method: "get_protein_features", accession: "UNIPROT_ACC")
#   -> Get domain, PTM, and functional site annotations for individual DE hits
#
# mcp__uniprot__uniprot_data(method: "get_external_references", accession: "UNIPROT_ACC")
#   -> Map UniProt accessions to gene names, Ensembl IDs, and pathway databases
#
# mcp__geneontology__go_data(method: "search_go_terms", query: "protein kinase activity", ontology: "molecular_function", size: 10)
#   -> Resolve GO terms from enrichment results to canonical IDs for DE protein annotation
#
# mcp__geneontology__go_data(method: "get_go_term", id: "GO:0006468")
#   -> Validate and retrieve full definition for GO terms enriched among DE proteins
```

### Phase 6: PTM-Specific Analysis

```python
def load_maxquant_ptm(path, loc_prob_cutoff=0.75):
    """Load MaxQuant Phospho (STY)Sites.txt with localization probability filter."""
    df = pd.read_csv(path, sep='\t', low_memory=False)
    for col in ['Reverse', 'Potential contaminant']:
        if col in df.columns: df = df[df[col] != '+']
    if 'Localization prob' in df.columns:
        df = df[df['Localization prob'] >= loc_prob_cutoff]
        print(f"Class I sites (prob >= {loc_prob_cutoff}): {len(df)}")
    return df

def ptm_differential(ptm_df, int_cols_g1, int_cols_g2):
    """Differential PTM analysis at the site level."""
    results = []
    for _, row in ptm_df.iterrows():
        v1 = np.log2(np.where(row[int_cols_g1].values.astype(float) == 0, np.nan, row[int_cols_g1].values.astype(float)))
        v2 = np.log2(np.where(row[int_cols_g2].values.astype(float) == 0, np.nan, row[int_cols_g2].values.astype(float)))
        v1, v2 = v1[np.isfinite(v1)], v2[np.isfinite(v2)]
        if len(v1) < 2 or len(v2) < 2: continue
        t_stat, p_val = stats.ttest_ind(v1, v2, equal_var=False)
        results.append({'gene': row.get('Gene names', ''), 'residue': row.get('Amino acid', ''),
                        'position': row.get('Position', ''), 'log2FC': np.mean(v1) - np.mean(v2),
                        'pvalue': p_val, 'loc_prob': row.get('Localization prob', np.nan)})
    df = pd.DataFrame(results)
    if len(df) > 0:
        _, padj, _, _ = multipletests(df['pvalue'].dropna(), method='fdr_bh')
        df.loc[df['pvalue'].notna(), 'padj'] = padj
    return df.sort_values('pvalue')

def kinase_substrate_enrichment(ptm_results, ks_db, padj_thresh=0.05):
    """KSEA: test whether substrates of each kinase are enriched among DE phosphosites."""
    sig_sites = set(zip(ptm_results[ptm_results['padj'] < padj_thresh]['gene'],
                        ptm_results[ptm_results['padj'] < padj_thresh]['position']))
    all_sites = set(zip(ptm_results['gene'], ptm_results['position']))
    N, n = len(all_sites), len(sig_sites)
    results = []
    for kinase, substrates in ks_db.items():
        K = len(set(substrates) & all_sites)
        if K < 3: continue
        k = len(set(substrates) & sig_sites)
        if k < 1: continue
        pval = hypergeom.sf(k - 1, N, K, n)
        results.append({'kinase': kinase, 'substrates_tested': K, 'sig_substrates': k, 'pvalue': pval})
    if not results: return pd.DataFrame()
    df = pd.DataFrame(results)
    _, padj, _, _ = multipletests(df['pvalue'], method='fdr_bh')
    df['padj'] = padj
    return df.sort_values('pvalue')
```

### Phase 7: Visualization

```python
from scipy.cluster.hierarchy import linkage, dendrogram
from sklearn.decomposition import PCA

def volcano_plot(de_results, padj_thresh=0.05, lfc_thresh=1.0, top_n=10):
    df = de_results.copy()
    df['-log10padj'] = -np.log10(df['padj'].clip(lower=1e-300))
    fig, ax = plt.subplots(figsize=(10, 8))
    df['cat'] = 'NS'
    df.loc[(df['padj'] < padj_thresh) & (df['log2FC'] > lfc_thresh), 'cat'] = 'Up'
    df.loc[(df['padj'] < padj_thresh) & (df['log2FC'] < -lfc_thresh), 'cat'] = 'Down'
    for cat, color in [('NS','#BBB'), ('Up','#E74C3C'), ('Down','#3498DB')]:
        s = df[df['cat'] == cat]
        ax.scatter(s['log2FC'], s['-log10padj'], c=color, s=8, alpha=0.6,
                   label=f'{cat} ({len(s)})', edgecolors='none')
    label_col = 'gene' if 'gene' in df.columns else 'protein'
    for _, r in df[df['cat']!='NS'].nsmallest(top_n, 'padj').iterrows():
        if pd.notna(r.get(label_col)):
            ax.annotate(r[label_col], (r['log2FC'], r['-log10padj']), fontsize=7)
    ax.axhline(-np.log10(padj_thresh), ls='--', color='grey', lw=0.8)
    ax.axvline(lfc_thresh, ls='--', color='grey', lw=0.8)
    ax.axvline(-lfc_thresh, ls='--', color='grey', lw=0.8)
    ax.set_xlabel('log2 Fold Change'); ax.set_ylabel('-log10(padj)')
    ax.set_title('Differential Protein Expression'); ax.legend()
    plt.tight_layout(); plt.savefig('volcano.png', dpi=300)

def heatmap_top(imputed_df, de_results, top_n=50):
    top = de_results.nsmallest(top_n, 'padj')['protein'].values
    data = imputed_df.loc[imputed_df.index.isin(top)].dropna()
    z = data.subtract(data.mean(axis=1), axis=0).divide(data.std(axis=1), axis=0)
    row_ord = dendrogram(linkage(z.values, method='ward'), no_plot=True)['leaves']
    col_ord = dendrogram(linkage(z.values.T, method='ward'), no_plot=True)['leaves']
    fig, ax = plt.subplots(figsize=(12, max(8, top_n*0.2)))
    ax.imshow(z.iloc[row_ord, col_ord].values, aspect='auto', cmap='RdBu_r', vmin=-2, vmax=2)
    ax.set_xticks(range(len(z.columns))); ax.set_xticklabels(z.columns.values[col_ord], rotation=45, ha='right', fontsize=8)
    ax.set_yticks(range(len(z.index))); ax.set_yticklabels(z.index.values[row_ord], fontsize=6)
    ax.set_title(f'Top {top_n} DE Proteins'); plt.tight_layout(); plt.savefig('heatmap.png', dpi=200)

def pca_plot(imputed_df, group_labels):
    data = imputed_df.dropna().T
    pca = PCA(n_components=2); coords = pca.fit_transform(data.values)
    fig, ax = plt.subplots(figsize=(8, 6))
    groups = [group_labels.get(s, '?') for s in data.index]
    for g in set(groups):
        mask = [i for i, x in enumerate(groups) if x == g]
        ax.scatter(coords[mask, 0], coords[mask, 1], s=80, label=g, edgecolors='black', lw=0.5)
    ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)')
    ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)')
    ax.legend(); ax.set_title('PCA - Sample Clustering')
    plt.tight_layout(); plt.savefig('pca.png', dpi=150)

def correlation_matrix(imputed_df):
    corr = imputed_df.corr()
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(corr.values, cmap='coolwarm', vmin=0.8, vmax=1.0)
    ax.set_xticks(range(len(corr))); ax.set_xticklabels(corr.columns, rotation=45, ha='right')
    ax.set_yticks(range(len(corr))); ax.set_yticklabels(corr.index)
    for i in range(len(corr)):
        for j in range(len(corr)):
            ax.text(j, i, f'{corr.values[i,j]:.3f}', ha='center', va='center', fontsize=7)
    plt.colorbar(im, ax=ax, shrink=0.7); plt.tight_layout(); plt.savefig('correlation.png', dpi=150)

volcano_plot(de_results); heatmap_top(imputed, de_results); pca_plot(imputed, group_labels); correlation_matrix(imputed)
```

---

## Quality Control Metrics

| Metric | Acceptable Range | Action if Out of Range |
|--------|-----------------|----------------------|
| **Protein count per sample** | >3000 (cell lines), >2000 (tissue) | Flag low-ID samples for exclusion |
| **CV within replicates** | <20% median CV | Check sample prep consistency |
| **Missing values** | <30% overall | Increase min valid value filter |
| **Dynamic range** | 4-6 orders of magnitude | Verify instrument performance |
| **Peptide coverage** | >2 unique peptides per protein | Filter single-peptide IDs |
| **Correlation (replicates)** | Pearson r > 0.95 | Investigate outlier samples |
| **PCA separation** | Groups cluster distinctly | Check for batch effects or swaps |

---

## Method Selection Decision Tree

### DDA vs DIA

```
DDA (Data-Dependent Acquisition):
  → More missing values (stochastic sampling), use mixed imputation
  → MaxQuant / FragPipe / Proteome Discoverer output
  → Match-between-runs reduces missingness

DIA (Data-Independent Acquisition):
  → Fewer missing values, KNN imputation preferred
  → Spectronaut / DIA-NN output
  → Higher quantitative reproducibility
```

### LFQ vs Labeled

```
Label-Free (LFQ):
  → Median or quantile normalization
  → Higher variability, need >= 3 replicates (>= 5 ideal)

TMT/iTRAQ (isobaric):
  → Within-plex: sample loading normalization
  → Between-plex: IRS normalization with bridge channel
  → Ratio compression: mitigate with SPS-MS3 data

SILAC (metabolic):
  → Heavy/light ratios already normalized
  → Log2(H/L) is primary measure, less imputation needed
```

### Normalization Choice

```
Medians aligned (range < 1 log2 unit) -> median normalization (default)
Distributions differ in shape          -> quantile normalization
Mean-variance non-linear              -> VSN-like normalization
TMT multi-plex                        -> within-plex SL + between-plex IRS
```

### Imputation Method Selection

```
Few missing values (< 10%):
  → KNN imputation (MCAR assumption valid)
  → Or complete-case analysis (discard proteins with any missing)

Moderate missing (10-30%), DDA data:
  → Mixed imputation (MinProb for MNAR + KNN for MCAR)
  → Assess per-protein: low-abundance missing = MNAR, random missing = MCAR

Moderate missing (10-30%), DIA data:
  → KNN imputation (DIA missing is more often MCAR)

High missing (> 30%):
  → Increase valid-value filter stringency first
  → Consider group-specific filtering: require N valid in at least one group
  → MinProb for remaining MNAR missing values

TMT data:
  → Very few missing within a plex (isobaric co-isolation)
  → Between-plex missing: treat as MCAR, use KNN
```

---

## Evidence Grading

| Tier | Criteria | Confidence |
|------|----------|------------|
| **T1** | padj < 0.01, \|log2FC\| > 1, >= 2 unique peptides, present in all replicates, pathway-confirmed | High |
| **T2** | padj < 0.05, \|log2FC\| > 0.58, >= 2 unique peptides, >= 70% replicate coverage | Medium-High |
| **T3** | padj < 0.05, any FC, 1 unique peptide or > 30% imputed values | Medium |
| **T4** | 0.05 < padj < 0.1, single peptide, < 50% sample coverage | Low |

```
T1 (HIGH): padj < 0.01, |log2FC| > 1, all replicates quantified,
   >= 2 unique peptides, enriched in >= 2 pathway databases
T2 (MEDIUM-HIGH): padj < 0.05, |log2FC| > 0.58, >= 70% replicate
   coverage, >= 2 unique peptides, single pathway DB support
T3 (MEDIUM): padj < 0.05, any FC, may have 1 peptide or imputed
   values, limited cross-validation
T4 (LOW): marginal significance, single peptide, poor coverage,
   flag for targeted validation (PRM/MRM/Western blot)
```

---

## Boundary Rules

### What This Skill Does (COMPUTE)

```
DO:
- Write and execute Python code for proteomics data analysis
- Load MaxQuant, Spectronaut, DIA-NN, FragPipe, Proteome Discoverer output
- Filter contaminants, reverse hits, single-site identifications
- Normalize intensities (median, quantile, VSN-like, IRS for TMT)
- Impute missing values (MinProb, KNN, mixed MNAR/MCAR)
- Run differential expression (Welch's t-test, BH correction)
- Perform PTM-specific analysis (phospho, acetyl, ubiquitin)
- Run kinase-substrate enrichment analysis (KSEA)
- Generate volcano plots, heatmaps, PCA, correlation matrices
- Perform ORA enrichment with hypergeometric test
- Calculate QC metrics (CV, dynamic range, coverage, correlation)
- Classify evidence by T1-T4 confidence tiers

DO NOT:
- Process raw MS data (mzML, raw files) or run search engines
- Perform spectral library generation or de novo sequencing
- Build protein interaction networks (use network-pharmacologist skill)
- Do deep multi-database pathway enrichment (use gene-enrichment skill)
- Assess target druggability (use target-research skill)
- Integrate with transcriptomics (use multi-omics-integration skill)
- Analyze protein structures (use protein-structure-retrieval skill)
```

### Tool Boundaries

| Task | Tool | Skill |
|------|------|-------|
| Protein quantification & DE | Python (scipy, statsmodels) | This skill |
| PTM site analysis & KSEA | Python (scipy) | This skill |
| Quick enrichment (ORA) | Python (scipy.stats.hypergeom) | This skill |
| Deep pathway enrichment | Multi-database ORA/GSEA | gene-enrichment |
| Protein interaction networks | STRING, NetworkX | network-pharmacologist |
| Multi-omics integration | Factor analysis, correlation | multi-omics-integration |
| Systems biology modeling | ODE, flux balance | systems-biology |
| Protein structure | PDB, AlphaFold | protein-structure-retrieval |

---

## Multi-Agent Workflow Examples

**"Analyze my MaxQuant proteinGroups.txt and find differentially expressed proteins"**
1. Proteomics Analysis -> Load MaxQuant, filter contaminants, normalize, impute, DE (Welch t-test + BH), volcano, heatmap, PCA
2. Gene Enrichment -> ORA/GSEA on up/down-regulated protein lists across GO/KEGG/Reactome
3. Systems Biology -> Network visualization of DE proteins, hub identification

**"I have phosphoproteomics data -- find differentially phosphorylated sites and predict kinase activity"**
1. Proteomics Analysis -> Load Phospho(STY)Sites.txt, filter by localization probability (class I >= 0.75), differential phosphosite analysis, KSEA
2. Network Pharmacologist -> Kinase-substrate network, signaling cascade mapping
3. Gene Enrichment -> Pathway enrichment on regulated phosphoproteins

**"Compare protein expression across conditions using TMT and identify enriched pathways"**
1. Proteomics Analysis -> Load TMT intensities, IRS normalization for multi-plex, pairwise DE, QC metrics
2. Gene Enrichment -> Pathway enrichment per comparison, shared and condition-specific pathways
3. Multi-Omics Integration -> Correlate protein and mRNA fold changes if RNA-seq available

**"Analyze DIA proteomics from Spectronaut and integrate with transcriptomics"**
1. Proteomics Analysis -> Load Spectronaut, normalize, KNN impute, DE, evidence grading
2. Multi-Omics Integration -> Protein-mRNA correlation, concordant/discordant regulation
3. Systems Biology -> Multi-layer network combining protein and transcript data

## Completeness Checklist

- [ ] Data loaded and source format identified (MaxQuant, Spectronaut, DIA-NN, or generic)
- [ ] Contaminants, reverse hits, and single-site IDs filtered
- [ ] QC metrics reported (protein count per sample, missing values, replicate correlation, dynamic range)
- [ ] Normalization method selected and applied with justification
- [ ] Missing value imputation performed with appropriate method (MinProb, KNN, or mixed)
- [ ] Differential expression computed with multiple testing correction (BH-adjusted p-values)
- [ ] Volcano plot, heatmap, and PCA generated and saved
- [ ] Evidence tier (T1-T4) assigned to significant DE proteins
- [ ] Pathway enrichment performed on significant protein lists
- [ ] Report file finalized with no `[Analyzing...]` placeholders remaining
