---
name: microbiome-analyst
description: "16S/ITS/metagenomics analysis, alpha/beta diversity, dysbiosis scoring, taxonomic profiling, functional prediction, microbiome-drug interactions"
---

# Microbiome Analysis

Microbiome analysis and interpretation specialist for 16S rRNA, ITS amplicon, and shotgun metagenomics data. The agent writes and executes Python code for quality filtering, OTU/ASV processing, taxonomic profiling, alpha and beta diversity, differential abundance testing, dysbiosis scoring, functional prediction, and microbiome-drug interaction analysis. Handles compositionality-aware statistics, supports standard tools (QIIME2, mothur, DADA2 output formats), and integrates with metabolic pathway databases for functional interpretation.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_microbiome-analyst_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Single-cell level microbial community analysis -> use `single-cell-analysis`
- Host gene differential expression in microbiome studies -> use `rnaseq-deseq2`
- Advanced statistical modeling for microbiome data -> use `statistical-modeling`
- Multi-omics integration (metagenomics + metabolomics + host transcriptomics) -> use `multi-omics-integration`
- Biomarker discovery and classifier construction from signatures -> use `biomarker-discovery`
- Infectious disease pathogen identification and resistance profiling -> use `infectious-disease-analyst`

## Cross-Reference: Other Skills

- **Single-cell level microbial community analysis** -> use single-cell-analysis skill
- **Differential expression of host genes in microbiome studies** -> use rnaseq-deseq2 skill
- **Advanced statistical modeling for microbiome data** -> use statistical-modeling skill
- **Multi-omics integration (metagenomics + metabolomics + host transcriptomics)** -> use multi-omics-integration skill
- **Biomarker discovery from microbiome signatures** -> use biomarker-discovery skill

## Python Environment

The container has `numpy`, `pandas`, `scipy`, `scikit-learn`, `matplotlib`, `seaborn`, `statsmodels` pre-installed. For specialized packages, install at runtime:

```python
import subprocess
subprocess.run(["pip", "install", "scikit-bio", "biom-format"], check=True)
```

## Data Input Formats

| Format | Extension | Handling |
|--------|-----------|----------|
| **OTU/ASV table** | `.csv`, `.tsv`, `.biom` | Feature table (taxa x samples) via `pd.read_csv` or `biom.load_table` |
| **Taxonomy file** | `.csv`, `.tsv` | Mapping of feature IDs to taxonomic lineage (Kingdom;Phylum;...;Species) |
| **Phylogenetic tree** | `.nwk`, `.tre` | Newick format for UniFrac and Faith's PD |
| **Metadata** | `.csv`, `.tsv` | Sample metadata with grouping variables, clinical data |
| **QIIME2 artifacts** | `.qza` | Unzip to extract embedded `.biom` or `.tsv` files |
| **mothur output** | `.shared`, `.taxonomy` | Parse shared file as OTU table, taxonomy as lineage map |

Orientation heuristic: if column names look like sample IDs (e.g., SRR*, S1, S2) and row names look like OTU/ASV IDs (e.g., ASV001, OTU_123, d__Bacteria), the table is taxa x samples (correct). If inverted, transpose.

## Available MCP Tools

### `mcp__pubmed__pubmed_data` (Microbiome Literature)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search` | Search PubMed for microbiome literature | `query`, `max_results` |
| `fetch_details` | Fetch full abstract and metadata for articles | `pmids` |

### `mcp__kegg__kegg_data` (Microbial Metabolic Pathways)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_pathway` | Get pathway details (microbial metabolism, SCFA production) | `pathway_id` |
| `find_pathway` | Search pathways by keyword (e.g., butyrate, bile acid) | `query` |
| `get_genes_in_pathway` | Get all genes in a metabolic pathway | `pathway_id` |
| `search_compounds` | Search KEGG compounds (SCFAs, bile acids, tryptophan metabolites) | `query` |

### `mcp__geneontology__go_data` (Microbial Gene Function)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_go_terms` | Search GO terms for microbial functions | `query` |
| `get_go_term` | Get GO term details and relationships | `go_id` |

### `mcp__clinicaltrials__ct_data` (Microbiome Clinical Trials)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_studies` | Search clinical trials (FMT, probiotics, microbiome interventions) | `query`, `max_results` |

### `mcp__reactome__reactome_data` (Host-Microbiome Interaction Pathways)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_pathways` | Search host pathways affected by microbiome (immune, metabolism) | `query`, `species` |
| `get_pathway` | Get full pathway details | `pathway_id` |

### `mcp__ensembl__ensembl_data` (Host Genes in Microbiome Interactions)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_gene_info` | Get gene details for host genes involved in microbiome crosstalk | `gene_id` |
| `get_gene_by_symbol` | Look up host genes by symbol (e.g., TLR4, NOD2, FUT2) | `symbol`, `species` |

### `mcp__drugbank__drugbank_data` (Drug-Microbiome Interactions)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_drugs` | Search drugs with known microbiome effects | `query` |
| `get_drug` | Get drug details including metabolism and interactions | `drugbank_id` |

---

## Core Workflows

### Workflow 1: 16S rRNA Analysis Pipeline

Complete pipeline from quality-filtered reads to biological interpretation.

**Step 1: Load and validate feature table**

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.spatial.distance import braycurtis, pdist, squareform

def load_feature_table(file_path, taxonomy_path=None, metadata_path=None):
    """Load OTU/ASV table with optional taxonomy and metadata."""
    sep = '\t' if file_path.endswith(('.tsv', '.txt')) else ','
    data = pd.read_csv(file_path, sep=sep, index_col=0)

    # Orient as taxa x samples
    if data.shape[0] < data.shape[1]:
        # Likely already taxa x samples
        pass
    else:
        # Check if row names look like sample IDs
        if any(data.index.str.startswith(('SRR', 'ERR', 'S0', 'Sample'))):
            data = data.T

    taxonomy = None
    if taxonomy_path:
        taxonomy = pd.read_csv(taxonomy_path, sep='\t', index_col=0)
        common_taxa = data.index.intersection(taxonomy.index)
        data = data.loc[common_taxa]
        taxonomy = taxonomy.loc[common_taxa]

    metadata = None
    if metadata_path:
        metadata = pd.read_csv(metadata_path, sep=sep, index_col=0)
        common_samples = data.columns.intersection(metadata.index)
        data = data[common_samples]
        metadata = metadata.loc[common_samples]

    print(f"Feature table: {data.shape[0]} taxa x {data.shape[1]} samples")
    print(f"Total reads: {data.sum().sum():,.0f}")
    print(f"Reads per sample: {data.sum().min():,.0f} - {data.sum().max():,.0f} "
          f"(median: {data.sum().median():,.0f})")
    return data, taxonomy, metadata

data, taxonomy, metadata = load_feature_table(
    "otu_table.tsv", "taxonomy.tsv", "metadata.tsv")
```

**Step 2: Quality filtering**

```python
def filter_features(data, min_prevalence=0.1, min_total_count=10,
                    min_sample_depth=1000):
    """Filter low-quality features and low-depth samples."""
    # Remove low-depth samples
    sample_depths = data.sum(axis=0)
    keep_samples = sample_depths >= min_sample_depth
    data = data.loc[:, keep_samples]
    print(f"Samples after depth filter (>={min_sample_depth}): "
          f"{keep_samples.sum()}/{len(keep_samples)}")

    # Remove low-prevalence features
    prevalence = (data > 0).mean(axis=1)
    keep_taxa = (prevalence >= min_prevalence) & (data.sum(axis=1) >= min_total_count)
    data = data.loc[keep_taxa]
    print(f"Taxa after prevalence filter (>={min_prevalence:.0%}): "
          f"{keep_taxa.sum()}/{len(keep_taxa)}")

    return data

data = filter_features(data)
```

**Step 3: Taxonomic assignment and aggregation**

```python
def parse_taxonomy(taxonomy_series, level="Genus"):
    """Parse semicolon-delimited taxonomy strings to specified level."""
    levels = ["Kingdom", "Phylum", "Class", "Order", "Family", "Genus", "Species"]
    idx = levels.index(level)

    parsed = {}
    for taxon_id, lineage in taxonomy_series.items():
        parts = str(lineage).split(';')
        parts = [p.strip().strip('_') for p in parts]
        if len(parts) > idx and parts[idx] and parts[idx] not in ('', 'unassigned', 'NA'):
            parsed[taxon_id] = parts[idx]
        else:
            # Use lowest assigned level
            assigned = [p for p in parts[:idx+1] if p and p not in ('', 'unassigned')]
            parsed[taxon_id] = assigned[-1] + "_unclassified" if assigned else "Unassigned"
    return pd.Series(parsed)

def aggregate_by_taxonomy(data, taxonomy_series, level="Genus"):
    """Collapse feature table to a given taxonomic level."""
    tax_map = parse_taxonomy(taxonomy_series, level)
    common = data.index.intersection(tax_map.index)
    data_mapped = data.loc[common].copy()
    data_mapped['taxon'] = tax_map.loc[common]
    collapsed = data_mapped.groupby('taxon').sum()
    print(f"Aggregated to {level}: {collapsed.shape[0]} unique taxa")
    return collapsed

genus_table = aggregate_by_taxonomy(data, taxonomy['Taxon'], level="Genus")
phylum_table = aggregate_by_taxonomy(data, taxonomy['Taxon'], level="Phylum")
```

**Literature and pathway lookup for identified taxa:**

```
mcp__pubmed__pubmed_data(method: "search", query: "Faecalibacterium prausnitzii butyrate gut health", max_results: 5)
-> Retrieve literature on key commensal taxa identified in the analysis

mcp__kegg__kegg_data(method: "find_pathway", query: "butyrate metabolism")
-> Find KEGG pathways for SCFA production by gut bacteria

mcp__kegg__kegg_data(method: "search_compounds", query: "butyric acid")
-> Look up butyrate compound details and associated reactions
```

---

### Workflow 2: Alpha Diversity Assessment

Alpha diversity quantifies within-sample richness and evenness. Multiple complementary metrics are required because no single index captures all aspects of diversity.

```python
def calculate_alpha_diversity(data):
    """Calculate multiple alpha diversity metrics per sample.

    Metrics:
    - Observed OTUs: count of taxa with >0 reads
    - Shannon (H'): accounts for both richness and evenness; range 0 to ln(S)
    - Simpson (1-D): probability two random reads are different taxa; range 0-1
    - Chao1: estimated true richness from singletons/doubletons
    - Pielou's evenness (J'): Shannon normalized by max possible; range 0-1
    """
    results = []
    for sample in data.columns:
        counts = data[sample].values.astype(float)
        counts = counts[counts > 0]
        total = counts.sum()

        # Observed OTUs
        observed = len(counts)

        # Shannon index
        proportions = counts / total
        shannon = -np.sum(proportions * np.log(proportions))

        # Simpson index (1 - D)
        simpson = 1 - np.sum(proportions ** 2)

        # Chao1
        singletons = np.sum(counts == 1)
        doubletons = np.sum(counts == 2)
        if doubletons > 0:
            chao1 = observed + (singletons ** 2) / (2 * doubletons)
        else:
            chao1 = observed + (singletons * (singletons - 1)) / 2

        # Pielou's evenness
        pielou = shannon / np.log(observed) if observed > 1 else 0

        results.append({
            'sample': sample,
            'observed_otus': observed,
            'shannon': round(shannon, 4),
            'simpson': round(simpson, 4),
            'chao1': round(chao1, 1),
            'pielou_evenness': round(pielou, 4),
            'total_reads': int(total)
        })

    return pd.DataFrame(results).set_index('sample')

alpha = calculate_alpha_diversity(data)
print(alpha.describe().round(3))
```

**Faith's Phylogenetic Diversity** (requires tree):

```python
def faiths_pd(data, tree_path):
    """Faith's PD: sum of branch lengths connecting observed taxa.
    Requires a phylogenetic tree in Newick format.
    """
    try:
        from skbio import TreeNode
        tree = TreeNode.read(tree_path)
    except ImportError:
        print("Install scikit-bio for Faith's PD: pip install scikit-bio")
        return None

    pd_values = {}
    for sample in data.columns:
        present = data.index[data[sample] > 0].tolist()
        if len(present) < 2:
            pd_values[sample] = 0
            continue
        subtree = tree.shear(present)
        pd_values[sample] = sum(n.length or 0 for n in subtree.traverse() if n.length)
    return pd.Series(pd_values, name='faiths_pd')
```

**Rarefaction curves:**

```python
def rarefaction_curve(data, steps=20, n_iter=10):
    """Generate rarefaction curves to assess sampling depth adequacy."""
    max_depth = int(data.sum(axis=0).min())
    depths = np.linspace(100, max_depth, steps, dtype=int)

    fig, ax = plt.subplots(figsize=(10, 6))
    for sample in data.columns:
        counts = data[sample].values.astype(int)
        pool = np.repeat(np.arange(len(counts)), counts)
        means = []
        for depth in depths:
            obs = []
            for _ in range(n_iter):
                subsample = np.random.choice(pool, size=depth, replace=False)
                obs.append(len(np.unique(subsample)))
            means.append(np.mean(obs))
        ax.plot(depths, means, alpha=0.5, linewidth=0.8)

    ax.set_xlabel('Sequencing Depth')
    ax.set_ylabel('Observed OTUs')
    ax.set_title('Rarefaction Curves')
    ax.axvline(x=max_depth, color='red', linestyle='--', alpha=0.5,
               label=f'Rarefaction depth: {max_depth:,}')
    ax.legend()
    plt.tight_layout()
    plt.savefig('rarefaction_curves.png', dpi=150)
    plt.close()
    print(f"Rarefaction curves saved (max depth: {max_depth:,})")

rarefaction_curve(data)
```

**Alpha diversity group comparison:**

```python
def compare_alpha_diversity(alpha_df, metadata, group_col, metrics=None):
    """Statistical comparison of alpha diversity between groups."""
    if metrics is None:
        metrics = ['shannon', 'simpson', 'observed_otus', 'chao1']
    merged = alpha_df.join(metadata[[group_col]])
    groups = merged[group_col].unique()

    results = []
    for metric in metrics:
        group_data = [merged.loc[merged[group_col] == g, metric].values for g in groups]

        if len(groups) == 2:
            stat, p = stats.mannwhitneyu(group_data[0], group_data[1],
                                          alternative='two-sided')
            test_name = 'Mann-Whitney U'
        else:
            stat, p = stats.kruskal(*group_data)
            test_name = 'Kruskal-Wallis'

        results.append({'metric': metric, 'test': test_name,
                        'statistic': round(stat, 3), 'p_value': round(p, 4)})

    results_df = pd.DataFrame(results)
    print(results_df.to_string(index=False))

    # Box plots
    fig, axes = plt.subplots(1, len(metrics), figsize=(4*len(metrics), 5))
    if len(metrics) == 1:
        axes = [axes]
    for ax, metric in zip(axes, metrics):
        sns.boxplot(data=merged, x=group_col, y=metric, ax=ax, palette='Set2')
        sns.stripplot(data=merged, x=group_col, y=metric, ax=ax,
                      color='black', size=3, alpha=0.5)
        p_val = results_df.loc[results_df['metric'] == metric, 'p_value'].values[0]
        ax.set_title(f'{metric}\n(p={p_val})')
    plt.tight_layout()
    plt.savefig('alpha_diversity_comparison.png', dpi=150)
    plt.close()
    return results_df

compare_alpha_diversity(alpha, metadata, group_col='group')
```

---

### Workflow 3: Beta Diversity Analysis

Beta diversity quantifies between-sample compositional differences. Different distance metrics capture different ecological signals.

```python
def calculate_beta_diversity(data, metric="bray_curtis"):
    """Calculate pairwise distance matrix.

    Supported metrics:
    - bray_curtis: abundance-weighted, most common for microbiome
    - jaccard: presence/absence only
    - aitchison: CLR-transformed Euclidean (compositionality-aware)
    """
    # Relative abundance
    rel_abund = data.div(data.sum(axis=0), axis=1)

    if metric == "bray_curtis":
        dist_matrix = squareform(pdist(rel_abund.T.values, metric='braycurtis'))
    elif metric == "jaccard":
        binary = (data > 0).astype(float)
        dist_matrix = squareform(pdist(binary.T.values, metric='jaccard'))
    elif metric == "aitchison":
        # CLR transform (add pseudocount for zeros)
        pseudo = data + 0.5
        log_data = np.log(pseudo)
        clr = log_data.sub(log_data.mean(axis=0), axis=1)
        dist_matrix = squareform(pdist(clr.T.values, metric='euclidean'))
    else:
        raise ValueError(f"Unknown metric: {metric}")

    dm = pd.DataFrame(dist_matrix, index=data.columns, columns=data.columns)
    return dm


def pcoa_plot(dist_matrix, metadata, group_col, title="PCoA"):
    """Principal Coordinates Analysis visualization."""
    from sklearn.manifold import MDS

    # Classical MDS (equivalent to PCoA)
    mds = MDS(n_components=2, dissimilarity='precomputed', random_state=42,
              normalized_stress=False)
    coords = mds.fit_transform(dist_matrix.values)

    # Calculate variance explained (eigenvalue approximation)
    H = np.eye(len(dist_matrix)) - np.ones_like(dist_matrix.values) / len(dist_matrix)
    B = -0.5 * H @ (dist_matrix.values ** 2) @ H
    eigvals = np.sort(np.linalg.eigvalsh(B))[::-1]
    eigvals_pos = eigvals[eigvals > 0]
    var_explained = eigvals_pos[:2] / eigvals_pos.sum() * 100

    fig, ax = plt.subplots(figsize=(10, 8))
    groups = metadata.loc[dist_matrix.index, group_col]
    for grp in groups.unique():
        mask = groups == grp
        ax.scatter(coords[mask, 0], coords[mask, 1], label=grp, s=80, alpha=0.7)
    ax.set_xlabel(f'PCoA1 ({var_explained[0]:.1f}%)')
    ax.set_ylabel(f'PCoA2 ({var_explained[1]:.1f}%)')
    ax.set_title(title)
    ax.legend()
    plt.tight_layout()
    plt.savefig('pcoa_plot.png', dpi=150)
    plt.close()
    return coords, var_explained


def nmds_plot(dist_matrix, metadata, group_col, title="NMDS"):
    """Non-metric Multidimensional Scaling visualization."""
    from sklearn.manifold import MDS

    nmds = MDS(n_components=2, dissimilarity='precomputed', random_state=42,
               metric=False, max_iter=1000, n_init=10)
    coords = nmds.fit_transform(dist_matrix.values)
    stress = nmds.stress_

    fig, ax = plt.subplots(figsize=(10, 8))
    groups = metadata.loc[dist_matrix.index, group_col]
    for grp in groups.unique():
        mask = groups == grp
        ax.scatter(coords[mask, 0], coords[mask, 1], label=grp, s=80, alpha=0.7)
    ax.set_xlabel('NMDS1')
    ax.set_ylabel('NMDS2')
    ax.set_title(f'{title} (stress={stress:.3f})')
    ax.legend()
    plt.tight_layout()
    plt.savefig('nmds_plot.png', dpi=150)
    plt.close()
    print(f"NMDS stress: {stress:.3f} {'(good)' if stress < 0.1 else '(acceptable)' if stress < 0.2 else '(poor)'}")
    return coords, stress

bc_dm = calculate_beta_diversity(data, metric="bray_curtis")
pcoa_plot(bc_dm, metadata, group_col='group', title="PCoA (Bray-Curtis)")
```

**UniFrac distances** (requires tree):

```python
def weighted_unifrac(data, tree_path):
    """Weighted UniFrac: accounts for abundance and phylogeny.
    Requires scikit-bio and a rooted phylogenetic tree.
    """
    try:
        from skbio import TreeNode
        from skbio.diversity import beta_diversity
        tree = TreeNode.read(tree_path)

        # Align feature IDs with tree tips
        tip_names = {tip.name for tip in tree.tips()}
        common = [t for t in data.index if t in tip_names]
        data_aligned = data.loc[common]

        dm = beta_diversity('weighted_unifrac', data_aligned.T.values.astype(int),
                            ids=data_aligned.columns.tolist(), tree=tree,
                            otu_ids=common)
        return dm.to_data_frame()
    except ImportError:
        print("Install scikit-bio for UniFrac: pip install scikit-bio")
        return None
```

**PERMANOVA:**

```python
def permanova(dist_matrix, metadata, group_col, n_permutations=999):
    """PERMANOVA: test whether group centroids differ in multivariate space.

    Uses the adonis-like approach (Anderson 2001):
    F = (SS_between / (k-1)) / (SS_within / (N-k))
    """
    groups = metadata.loc[dist_matrix.index, group_col]
    unique_groups = groups.unique()
    n = len(groups)
    k = len(unique_groups)

    D_sq = dist_matrix.values ** 2

    # Total sum of squares
    ss_total = D_sq.sum() / (2 * n)

    # Within-group sum of squares
    ss_within = 0
    for grp in unique_groups:
        mask = (groups == grp).values
        n_g = mask.sum()
        ss_within += D_sq[np.ix_(mask, mask)].sum() / (2 * n_g)

    ss_between = ss_total - ss_within
    f_obs = (ss_between / (k - 1)) / (ss_within / (n - k))

    # Permutation test
    f_perms = []
    for _ in range(n_permutations):
        perm_groups = np.random.permutation(groups.values)
        ss_w_perm = 0
        for grp in unique_groups:
            mask = perm_groups == grp
            n_g = mask.sum()
            ss_w_perm += D_sq[np.ix_(mask, mask)].sum() / (2 * n_g)
        ss_b_perm = ss_total - ss_w_perm
        f_perms.append((ss_b_perm / (k - 1)) / (ss_w_perm / (n - k)))

    p_value = (np.sum(np.array(f_perms) >= f_obs) + 1) / (n_permutations + 1)
    r_squared = ss_between / ss_total

    print(f"PERMANOVA: F={f_obs:.3f}, R2={r_squared:.3f}, p={p_value:.4f}")
    print(f"  Groups explain {r_squared:.1%} of total variance")
    return {'F': f_obs, 'R2': r_squared, 'p_value': p_value, 'n_permutations': n_permutations}

permanova(bc_dm, metadata, group_col='group')
```

---

### Workflow 4: Differential Abundance Testing

Microbiome data is compositional (relative abundances sum to 1), which means standard statistical tests can produce spurious results. Use compositionality-aware methods.

**The compositionality problem:** An increase in one taxon forces decreases in relative abundances of all others, even if their absolute abundances are unchanged. This creates false negative correlations and inflates differential abundance false positives. The Aitchison framework (CLR/ILR transforms) and specialized tools (ANCOM-BC, ALDEx2) address this.

```python
def differential_abundance_deseq2_style(data, metadata, group_col,
                                         ref_group, test_group):
    """DESeq2-inspired differential abundance using negative binomial model.

    Note: For rigorous analysis, prefer ANCOM-BC or ALDEx2 which explicitly
    handle compositionality. DESeq2 on microbiome data can have elevated FPR
    when library sizes vary dramatically.
    """
    from statsmodels.stats.multitest import multipletests

    g1_cols = metadata[metadata[group_col] == ref_group].index
    g2_cols = metadata[metadata[group_col] == test_group].index

    results = []
    for taxon in data.index:
        c1 = data.loc[taxon, g1_cols].values.astype(float)
        c2 = data.loc[taxon, g2_cols].values.astype(float)

        # Add pseudocount for log transform
        c1_log = np.log2(c1 + 1)
        c2_log = np.log2(c2 + 1)

        log2fc = c2_log.mean() - c1_log.mean()
        stat, p = stats.mannwhitneyu(c1, c2, alternative='two-sided')

        results.append({'taxon': taxon, 'log2FC': log2fc, 'p_value': p,
                        'mean_ref': c1.mean(), 'mean_test': c2.mean()})

    df = pd.DataFrame(results).set_index('taxon')
    _, df['padj'], _, _ = multipletests(df['p_value'], method='fdr_bh')
    df = df.sort_values('padj')

    sig = df[(df['padj'] < 0.05) & (df['log2FC'].abs() > 1)]
    print(f"Differential taxa: {len(sig)} (padj<0.05, |log2FC|>1)")
    print(f"  Enriched in {test_group}: {(sig['log2FC'] > 0).sum()}")
    print(f"  Enriched in {ref_group}: {(sig['log2FC'] < 0).sum()}")
    return df, sig


def aldex2_style(data, metadata, group_col, ref_group, test_group,
                 n_mc=128):
    """ALDEx2-inspired analysis: Monte Carlo sampling from Dirichlet distribution
    followed by CLR transformation. Handles compositionality and count uncertainty.
    """
    from statsmodels.stats.multitest import multipletests

    g1_idx = metadata[metadata[group_col] == ref_group].index
    g2_idx = metadata[metadata[group_col] == test_group].index

    # Monte Carlo CLR instances
    all_effects = []
    for _ in range(n_mc):
        # Sample from Dirichlet (counts + 0.5 prior)
        mc_data = np.zeros_like(data.values, dtype=float)
        for j in range(data.shape[1]):
            counts_plus_prior = data.iloc[:, j].values + 0.5
            mc_data[:, j] = np.random.dirichlet(counts_plus_prior)

        # CLR transform
        log_data = np.log2(mc_data)
        clr = log_data - log_data.mean(axis=0, keepdims=True)

        clr_df = pd.DataFrame(clr, index=data.index, columns=data.columns)
        g1_vals = clr_df[g1_idx].mean(axis=1)
        g2_vals = clr_df[g2_idx].mean(axis=1)
        all_effects.append(g2_vals - g1_vals)

    effects = pd.concat(all_effects, axis=1)
    result = pd.DataFrame({
        'effect_mean': effects.mean(axis=1),
        'effect_sd': effects.std(axis=1),
    }, index=data.index)
    result['effect_size'] = result['effect_mean'] / result['effect_sd']

    # Welch's t-test on CLR values across MC instances
    p_values = []
    for taxon in data.index:
        clr_g1 = []
        clr_g2 = []
        for mc_idx in range(n_mc):
            counts_plus = data.loc[taxon].values + 0.5
            mc_sample = np.random.dirichlet(counts_plus)
            log_mc = np.log2(mc_sample)
            clr_mc = log_mc - log_mc.mean()
            g1_pos = [data.columns.get_loc(s) for s in g1_idx if s in data.columns]
            g2_pos = [data.columns.get_loc(s) for s in g2_idx if s in data.columns]
            clr_g1.extend(clr_mc[g1_pos])
            clr_g2.extend(clr_mc[g2_pos])
        _, p = stats.ttest_ind(clr_g1, clr_g2, equal_var=False)
        p_values.append(p)

    result['p_value'] = p_values
    _, result['padj'], _, _ = multipletests(result['p_value'], method='fdr_bh')
    result = result.sort_values('padj')

    sig = result[(result['padj'] < 0.05) & (result['effect_size'].abs() > 1)]
    print(f"ALDEx2-style: {len(sig)} significant taxa (padj<0.05, |effect|>1)")
    return result, sig


def lefse_style(data, metadata, group_col, lda_threshold=2.0):
    """LEfSe-inspired analysis: Kruskal-Wallis + Wilcoxon + LDA effect size.
    Identifies taxa that are both statistically different and biologically relevant.
    """
    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
    from statsmodels.stats.multitest import multipletests

    rel_abund = data.div(data.sum(axis=0), axis=1)
    groups = metadata.loc[data.columns, group_col]
    unique_groups = groups.unique()

    results = []
    for taxon in rel_abund.index:
        values = rel_abund.loc[taxon]
        group_vals = [values[groups == g].values for g in unique_groups]

        # Kruskal-Wallis
        if len(unique_groups) == 2:
            _, kw_p = stats.mannwhitneyu(group_vals[0], group_vals[1],
                                          alternative='two-sided')
        else:
            _, kw_p = stats.kruskal(*group_vals)

        if kw_p >= 0.05:
            continue

        # LDA effect size
        X = values.values.reshape(-1, 1)
        y = groups.values
        try:
            lda = LinearDiscriminantAnalysis()
            lda.fit(X, y)
            lda_score = abs(lda.coef_[0][0]) * np.log10(max(values.mean(), 1e-10))
        except Exception:
            lda_score = 0

        # Identify enriched group
        mean_abund = {g: values[groups == g].mean() for g in unique_groups}
        enriched = max(mean_abund, key=mean_abund.get)

        results.append({
            'taxon': taxon, 'kw_p': kw_p, 'lda_score': abs(lda_score),
            'enriched_in': enriched,
            **{f'mean_{g}': mean_abund[g] for g in unique_groups}
        })

    df = pd.DataFrame(results)
    if len(df):
        sig = df[df['lda_score'] >= lda_threshold].sort_values('lda_score', ascending=False)
        print(f"LEfSe-style: {len(sig)} biomarker taxa (LDA>={lda_threshold})")
        return sig
    return pd.DataFrame()
```

**Rarefaction vs. normalization debate:**

```
When to rarefy:
- Alpha diversity (rarefaction is standard practice, avoids richness-depth confounding)
- Beta diversity with large depth differences (>10x between samples)
- Quick exploratory analysis

When NOT to rarefy:
- Differential abundance testing (use raw counts with DESeq2/ANCOM-BC/ALDEx2)
- When sample sizes are small (discarding data is costly)
- Shotgun metagenomics (normalize by total reads or use TPM)

Alternatives to rarefaction:
- CSS (cumulative sum scaling): metagenomeSeq
- TMM (trimmed mean of M-values): from edgeR
- CLR (centered log-ratio): compositionality-aware
- GMPR (geometric mean of pairwise ratios): designed for sparse microbiome data
```

---

### Workflow 5: Dysbiosis Scoring

Quantify the degree of microbial community disruption relative to a healthy reference.

```python
def firmicutes_bacteroidetes_ratio(phylum_table):
    """Calculate Firmicutes/Bacteroidetes (F/B) ratio.

    Interpretation:
    - Healthy adults: F/B typically 1-3
    - Obesity-associated: F/B > 3 in some studies (controversial)
    - IBD-associated: often decreased Firmicutes, increased Proteobacteria
    - Elderly: F/B often increases with age

    CAUTION: F/B ratio is an oversimplification. Many studies fail to replicate
    the obesity-F/B association. Use as one component, not sole indicator.
    """
    firmicutes = phylum_table.loc['Firmicutes'] if 'Firmicutes' in phylum_table.index else 0
    bacteroidetes = phylum_table.loc['Bacteroidetes'] if 'Bacteroidetes' in phylum_table.index else 0

    ratio = (firmicutes + 1) / (bacteroidetes + 1)  # +1 pseudocount
    return ratio


def dysbiosis_index(data, reference_healthy=None, method="bray_curtis"):
    """Calculate dysbiosis index as distance from healthy reference centroid.

    If no reference provided, uses the median community profile as reference.
    """
    rel_abund = data.div(data.sum(axis=0), axis=1)

    if reference_healthy is not None:
        ref_profile = reference_healthy.div(reference_healthy.sum(axis=0), axis=1).median(axis=1)
    else:
        ref_profile = rel_abund.median(axis=1)

    # Align taxa
    common = rel_abund.index.intersection(ref_profile.index)
    rel_abund = rel_abund.loc[common]
    ref = ref_profile.loc[common].values

    scores = {}
    for sample in rel_abund.columns:
        sample_profile = rel_abund[sample].values
        scores[sample] = braycurtis(sample_profile, ref)

    return pd.Series(scores, name='dysbiosis_index')


def community_state_types(data, n_clusters=4):
    """Identify Community State Types (CSTs) via Dirichlet Multinomial Mixture
    approximation using K-means on CLR-transformed data.

    Originally developed for vaginal microbiome (Ravel et al. 2011),
    applicable to any body site for identifying discrete community configurations.
    """
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score

    rel_abund = data.div(data.sum(axis=0), axis=1)
    clr = np.log(rel_abund + 1e-6)
    clr = clr.sub(clr.mean(axis=0), axis=1)

    # Evaluate cluster solutions
    results = {}
    for k in range(2, n_clusters + 1):
        km = KMeans(n_clusters=k, random_state=42, n_init=20)
        labels = km.fit_predict(clr.T.values)
        sil = silhouette_score(clr.T.values, labels)
        results[k] = {'labels': pd.Series(labels, index=data.columns, name=f'CST_k{k}'),
                       'silhouette': sil}
        print(f"  k={k}: silhouette={sil:.3f}")

    best_k = max(results, key=lambda k: results[k]['silhouette'])
    print(f"Best k={best_k}")

    # Characterize CSTs by dominant taxa
    best_labels = results[best_k]['labels']
    for cst in range(best_k):
        cst_samples = best_labels[best_labels == cst].index
        mean_abund = rel_abund[cst_samples].mean(axis=1).sort_values(ascending=False)
        top3 = mean_abund.head(3)
        print(f"  CST-{cst} ({len(cst_samples)} samples): "
              f"{', '.join(f'{t} ({v:.1%})' for t, v in top3.items())}")

    return results[best_k]['labels'], results


def proteobacteria_bloom_score(phylum_table):
    """Detect Proteobacteria bloom — a marker of dysbiosis across body sites.

    Proteobacteria expansion (especially Enterobacteriaceae) is associated with:
    - Inflammatory bowel disease
    - C. difficile infection
    - Antibiotic-induced dysbiosis
    - Necrotizing enterocolitis in neonates

    Score: relative abundance of Proteobacteria (>15% is concerning)
    """
    total = phylum_table.sum(axis=0)
    proteo = phylum_table.loc['Proteobacteria'] if 'Proteobacteria' in phylum_table.index else 0
    score = proteo / total
    return score
```

---

### Workflow 6: Functional Prediction

Predict community functional capacity from 16S rRNA data or analyze functional profiles from shotgun metagenomics.

```python
def picrust2_style_prediction(genus_table, genome_content_db):
    """Simplified functional prediction from 16S data.

    Real PICRUSt2 workflow:
    1. Place ASVs into reference tree (EPA-ng)
    2. Predict gene family abundances (hidden state prediction)
    3. Weight by ASV abundance
    4. Map to MetaCyc pathways (MinPath)

    This simplified version uses genus-level KEGG module assignments.
    For production use, run PICRUSt2 externally and import results.
    """
    rel_abund = genus_table.div(genus_table.sum(axis=0), axis=1)

    predicted = pd.DataFrame(0, index=list(genome_content_db.values())[0].keys(),
                              columns=genus_table.columns)
    for genus in rel_abund.index:
        if genus in genome_content_db:
            for pathway, copy_number in genome_content_db[genus].items():
                predicted.loc[pathway] += rel_abund.loc[genus] * copy_number

    return predicted


# Key SCFA production pathways to query via KEGG
SCFA_PATHWAYS = {
    'butyrate': {
        'producers': ['Faecalibacterium', 'Roseburia', 'Eubacterium',
                       'Anaerostipes', 'Coprococcus', 'Butyricicoccus'],
        'kegg_modules': ['M00579', 'M00209'],  # Butyrate synthesis
        'key_genes': ['but', 'buk', 'bcd', 'crt'],
    },
    'propionate': {
        'producers': ['Bacteroides', 'Prevotella', 'Akkermansia',
                       'Phascolarctobacterium', 'Dialister'],
        'kegg_modules': ['M00741'],  # Propanoate metabolism
        'key_genes': ['mmdA', 'lcdA', 'pduP'],
    },
    'acetate': {
        'producers': ['Blautia', 'Bifidobacterium', 'Ruminococcus',
                       'Lactobacillus', 'Streptococcus'],
        'kegg_modules': ['M00618'],  # Acetate synthesis
        'key_genes': ['pta', 'ackA', 'acs'],
    },
}

def scfa_producer_score(genus_table):
    """Score SCFA production capacity based on known producer abundances."""
    rel_abund = genus_table.div(genus_table.sum(axis=0), axis=1)
    scores = {}
    for scfa, info in SCFA_PATHWAYS.items():
        producers = [p for p in info['producers'] if p in rel_abund.index]
        if producers:
            scores[scfa] = rel_abund.loc[producers].sum(axis=0)
        else:
            scores[scfa] = pd.Series(0, index=rel_abund.columns)
    return pd.DataFrame(scores)
```

**KEGG pathway lookup for functional prediction:**

```
mcp__kegg__kegg_data(method: "get_pathway", pathway_id: "map00650")
-> Butyrate metabolism pathway details

mcp__kegg__kegg_data(method: "get_genes_in_pathway", pathway_id: "map00650")
-> Genes involved in butyrate metabolism for functional annotation

mcp__kegg__kegg_data(method: "find_pathway", query: "short chain fatty acid")
-> Find SCFA-related metabolic pathways

mcp__kegg__kegg_data(method: "search_compounds", query: "bile acid")
-> Search bile acid compounds for microbiome-bile acid interaction analysis
```

**GO annotation for microbial functions:**

```
mcp__geneontology__go_data(method: "search_go_terms", query: "anaerobic fermentation")
-> Find GO terms related to anaerobic metabolism in gut bacteria

mcp__geneontology__go_data(method: "get_go_term", go_id: "GO:0015891")
-> Get details on siderophore transport (iron acquisition in pathogens)
```

---

### Workflow 7: Microbiome-Drug Interactions

Drug metabolism by gut bacteria and drug-induced dysbiosis.

```python
# Known drug-microbiome interactions
DRUG_MICROBIOME_INTERACTIONS = {
    'metformin': {
        'effect': 'Increases Akkermansia, decreases Intestinibacter',
        'mechanism': 'AMPK activation, bile acid metabolism alteration',
        'clinical': 'GI side effects partly microbiome-mediated',
        'taxa_affected': {'Akkermansia': 'increase', 'Intestinibacter': 'decrease',
                          'Escherichia': 'increase'},
    },
    'proton_pump_inhibitors': {
        'effect': 'Decreased diversity, increased oral taxa in gut',
        'mechanism': 'Increased gastric pH allows oral bacteria survival',
        'clinical': 'Increased CDI risk, SIBO',
        'taxa_affected': {'Streptococcus': 'increase', 'Enterococcus': 'increase',
                          'Clostridium': 'decrease'},
    },
    'antibiotics_broad_spectrum': {
        'effect': 'Dramatic diversity loss, Proteobacteria bloom',
        'mechanism': 'Direct bactericidal/bacteriostatic activity',
        'clinical': 'CDI risk, antibiotic-associated diarrhea',
        'taxa_affected': {'Bacteroides': 'decrease', 'Enterobacteriaceae': 'increase',
                          'Clostridioides': 'increase'},
    },
    'nsaids': {
        'effect': 'Increased intestinal permeability, dysbiosis',
        'mechanism': 'COX inhibition, direct mucosal damage',
        'clinical': 'NSAID enteropathy, ulceration',
        'taxa_affected': {'Erysipelotrichaceae': 'increase',
                          'Lactobacillus': 'decrease'},
    },
    'statins': {
        'effect': 'Modulates bile acid metabolism, possible prebiotic effect',
        'mechanism': 'Bile acid pool alteration via cholesterol pathway',
        'clinical': 'May contribute to statin intolerance symptoms',
        'taxa_affected': {'Bacteroides': 'variable', 'Faecalibacterium': 'increase'},
    },
}

# Bacterial drug metabolism
BACTERIAL_DRUG_METABOLISM = {
    'digoxin': {
        'metabolizer': 'Eggerthella lenta',
        'reaction': 'Reduction of digoxin to dihydrodigoxin (inactive)',
        'gene': 'cgr operon (cardiac glycoside reductase)',
        'clinical': 'Variable drug bioavailability; high E. lenta -> low drug levels',
    },
    'levodopa': {
        'metabolizer': 'Enterococcus faecalis',
        'reaction': 'Decarboxylation to dopamine (in gut, before absorption)',
        'gene': 'tyrDC (tyrosine decarboxylase)',
        'clinical': 'Reduced drug efficacy in Parkinsons patients',
    },
    'irinotecan': {
        'metabolizer': 'Multiple Firmicutes/Bacteroidetes',
        'reaction': 'Beta-glucuronidase reactivates SN-38 in gut',
        'gene': 'gus (beta-glucuronidase)',
        'clinical': 'Severe diarrhea; inhibiting bacterial beta-glucuronidase reduces toxicity',
    },
    'sulfasalazine': {
        'metabolizer': 'Colonic anaerobes',
        'reaction': 'Azoreductase cleaves azo bond -> 5-ASA + sulfapyridine',
        'gene': 'azoreductase genes',
        'clinical': 'Prodrug activation requires gut bacteria; germ-free animals dont activate',
    },
}

def assess_drug_microbiome_impact(genus_table, drug_name):
    """Assess how a drug may be affecting the microbiome based on known interactions."""
    drug_key = drug_name.lower().replace(' ', '_')
    if drug_key not in DRUG_MICROBIOME_INTERACTIONS:
        print(f"No known interaction data for '{drug_name}'")
        return None

    interaction = DRUG_MICROBIOME_INTERACTIONS[drug_key]
    rel_abund = genus_table.div(genus_table.sum(axis=0), axis=1)

    report = {
        'drug': drug_name,
        'known_effect': interaction['effect'],
        'mechanism': interaction['mechanism'],
        'clinical_relevance': interaction['clinical'],
        'affected_taxa_detected': {},
    }

    for taxon, direction in interaction['taxa_affected'].items():
        if taxon in rel_abund.index:
            abund = rel_abund.loc[taxon]
            report['affected_taxa_detected'][taxon] = {
                'expected_direction': direction,
                'mean_abundance': f"{abund.mean():.2%}",
                'present_in': f"{(abund > 0).sum()}/{len(abund)} samples",
            }

    return report
```

**Drug-microbiome lookup via MCP tools:**

```
mcp__drugbank__drugbank_data(method: "search_drugs", query: "metformin")
-> Get drug details including known effects on gut microbiome

mcp__drugbank__drugbank_data(method: "get_drug", drugbank_id: "DB00331")
-> Full metformin profile: pharmacokinetics, metabolism, interactions

mcp__pubmed__pubmed_data(method: "search", query: "metformin gut microbiome Akkermansia clinical trial", max_results: 5)
-> Literature on metformin-microbiome axis

mcp__clinicaltrials__ct_data(method: "search_studies", query: "fecal microbiota transplantation Clostridioides difficile", max_results: 5)
-> Active FMT clinical trials for CDI

mcp__ensembl__ensembl_data(method: "get_gene_by_symbol", symbol: "NOD2", species: "homo_sapiens")
-> Host NOD2 gene info (innate immune receptor for bacterial peptidoglycan)

mcp__reactome__reactome_data(method: "search_pathways", query: "toll-like receptor signaling", species: "Homo sapiens")
-> Host immune pathways activated by microbial ligands (LPS, flagellin)
```

---

## Microbiome Health Scoring

Composite score (0-100) integrating multiple dimensions of microbiome health. Use as a summary metric, always report sub-scores and interpretation caveats.

```python
def microbiome_health_score(data, metadata, taxonomy, alpha_df,
                             reference_healthy=None, temporal_data=None):
    """Calculate composite Microbiome Health Score (MHS) on a 0-100 scale.

    Components (weights):
    1. Alpha diversity (25%) — richness and evenness
    2. Taxonomic composition (25%) — beneficial vs. pathogenic taxa
    3. Functional capacity (20%) — metabolic pathway coverage
    4. Stability/resilience (15%) — temporal consistency
    5. Clinical correlation (15%) — association with outcomes

    Scores are percentile-ranked against the reference distribution.
    """
    scores = {}

    # --- 1. Alpha diversity score (25%) ---
    shannon = alpha_df['shannon']
    # Percentile within study or against healthy reference
    if reference_healthy is not None:
        ref_alpha = calculate_alpha_diversity(reference_healthy)
        ref_mean, ref_sd = ref_alpha['shannon'].mean(), ref_alpha['shannon'].std()
    else:
        ref_mean, ref_sd = shannon.mean(), shannon.std()

    diversity_score = stats.norm.cdf(shannon, loc=ref_mean, scale=ref_sd) * 100
    scores['alpha_diversity'] = diversity_score.clip(0, 100)

    # --- 2. Taxonomic composition score (25%) ---
    rel_abund = data.div(data.sum(axis=0), axis=1)
    genus_table = aggregate_by_taxonomy(data, taxonomy['Taxon'], level='Genus')
    genus_rel = genus_table.div(genus_table.sum(axis=0), axis=1)

    # Beneficial taxa (higher = better)
    beneficial = ['Faecalibacterium', 'Bifidobacterium', 'Lactobacillus',
                  'Akkermansia', 'Roseburia', 'Eubacterium', 'Ruminococcus',
                  'Coprococcus', 'Blautia']
    # Potentially pathogenic taxa (higher = worse)
    pathogenic = ['Clostridioides', 'Klebsiella', 'Escherichia',
                  'Enterococcus', 'Pseudomonas', 'Staphylococcus',
                  'Fusobacterium', 'Campylobacter']

    ben_score = sum(genus_rel.loc[g] for g in beneficial if g in genus_rel.index)
    path_score = sum(genus_rel.loc[g] for g in pathogenic if g in genus_rel.index)

    composition_raw = (ben_score - path_score + 1) / 2  # Normalize to 0-1 range
    scores['taxonomic_composition'] = (composition_raw.clip(0, 1) * 100)

    # --- 3. Functional capacity score (20%) ---
    scfa_scores = scfa_producer_score(genus_table)
    total_scfa = scfa_scores.sum(axis=1)
    func_percentile = total_scfa.rank(pct=True) * 100
    scores['functional_capacity'] = func_percentile

    # --- 4. Stability/resilience score (15%) ---
    if temporal_data is not None and len(temporal_data) > 1:
        # Bray-Curtis distance between consecutive time points
        stability_scores = {}
        for sample_id in temporal_data:
            timepoints = temporal_data[sample_id]
            if len(timepoints) < 2:
                stability_scores[sample_id] = 50  # neutral
                continue
            dists = []
            for i in range(len(timepoints) - 1):
                d = braycurtis(timepoints[i], timepoints[i + 1])
                dists.append(d)
            # Lower distance = more stable = higher score
            stability_scores[sample_id] = (1 - np.mean(dists)) * 100
        scores['stability'] = pd.Series(stability_scores)
    else:
        # No temporal data: assign neutral score
        scores['stability'] = pd.Series(50, index=data.columns)

    # --- 5. Clinical correlation score (15%) ---
    # Proxy: dysbiosis index inverted
    dysbiosis = dysbiosis_index(data, reference_healthy)
    clinical_score = (1 - dysbiosis) * 100
    scores['clinical_correlation'] = clinical_score.clip(0, 100)

    # --- Composite score ---
    weights = {
        'alpha_diversity': 0.25,
        'taxonomic_composition': 0.25,
        'functional_capacity': 0.20,
        'stability': 0.15,
        'clinical_correlation': 0.15,
    }

    composite = pd.DataFrame(scores)
    composite['MHS'] = sum(composite[k] * w for k, w in weights.items())
    composite['MHS'] = composite['MHS'].clip(0, 100).round(1)

    # Interpretation
    composite['interpretation'] = pd.cut(
        composite['MHS'],
        bins=[0, 25, 50, 75, 100],
        labels=['Severe dysbiosis', 'Moderate dysbiosis',
                'Mildly altered', 'Healthy']
    )

    print("\nMicrobiome Health Score Summary:")
    print(f"  Mean MHS: {composite['MHS'].mean():.1f}")
    print(f"  Range: {composite['MHS'].min():.1f} - {composite['MHS'].max():.1f}")
    for cat in ['Healthy', 'Mildly altered', 'Moderate dysbiosis', 'Severe dysbiosis']:
        n = (composite['interpretation'] == cat).sum()
        if n > 0:
            print(f"  {cat}: {n} samples ({n/len(composite):.0%})")

    return composite
```

---

## Visualization Templates

### Taxonomic Composition (Stacked Bar Plot)

```python
def stacked_barplot(data, taxonomy, metadata, group_col,
                    level="Phylum", top_n=10):
    """Stacked bar plot of taxonomic composition by sample or group."""
    agg = aggregate_by_taxonomy(data, taxonomy['Taxon'], level=level)
    rel_abund = agg.div(agg.sum(axis=0), axis=1)

    # Keep top N taxa, collapse rest to "Other"
    mean_abund = rel_abund.mean(axis=1).sort_values(ascending=False)
    top_taxa = mean_abund.head(top_n).index
    other = rel_abund.loc[~rel_abund.index.isin(top_taxa)].sum(axis=0)
    plot_data = rel_abund.loc[top_taxa].copy()
    plot_data.loc['Other'] = other

    # Order samples by group
    sample_order = metadata.sort_values(group_col).index
    sample_order = [s for s in sample_order if s in plot_data.columns]
    plot_data = plot_data[sample_order]

    fig, ax = plt.subplots(figsize=(max(12, len(sample_order) * 0.3), 6))
    colors = plt.cm.Set3(np.linspace(0, 1, len(plot_data)))
    bottom = np.zeros(len(sample_order))

    for i, (taxon, row) in enumerate(plot_data.iterrows()):
        ax.bar(range(len(sample_order)), row.values, bottom=bottom,
               color=colors[i], label=taxon, width=1.0, edgecolor='white',
               linewidth=0.3)
        bottom += row.values

    ax.set_xlim(-0.5, len(sample_order) - 0.5)
    ax.set_ylim(0, 1)
    ax.set_ylabel('Relative Abundance')
    ax.set_title(f'{level}-Level Composition')
    ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=8)

    # Add group labels
    groups = metadata.loc[sample_order, group_col]
    group_boundaries = []
    prev_group = None
    for i, g in enumerate(groups):
        if g != prev_group:
            group_boundaries.append((i, g))
            prev_group = g
    for start, grp in group_boundaries:
        ax.axvline(x=start - 0.5, color='black', linewidth=1, alpha=0.5)
        ax.text(start + 1, -0.05, grp, fontsize=8, ha='left',
                transform=ax.get_xaxis_transform())

    ax.set_xticks([])
    plt.tight_layout()
    plt.savefig('taxonomic_composition.png', dpi=150, bbox_inches='tight')
    plt.close()

stacked_barplot(data, taxonomy, metadata, group_col='group', level='Phylum')
```

### Heatmap of Differentially Abundant Taxa

```python
def taxa_heatmap(data, sig_taxa, metadata, group_col, top_n=30):
    """Heatmap of significantly differential taxa with group annotation."""
    rel_abund = data.div(data.sum(axis=0), axis=1)
    log_abund = np.log10(rel_abund + 1e-6)

    taxa_to_plot = sig_taxa.head(top_n).index if hasattr(sig_taxa, 'index') else sig_taxa[:top_n]
    taxa_to_plot = [t for t in taxa_to_plot if t in log_abund.index]

    col_order = metadata.sort_values(group_col).index
    col_order = [s for s in col_order if s in log_abund.columns]

    palette = dict(zip(metadata[group_col].unique(), sns.color_palette("Set1")))
    col_colors = metadata.loc[col_order, group_col].map(palette)

    g = sns.clustermap(
        log_abund.loc[taxa_to_plot, col_order],
        col_cluster=False, row_cluster=True,
        cmap='RdBu_r', center=log_abund.loc[taxa_to_plot, col_order].values.mean(),
        figsize=(12, max(8, len(taxa_to_plot) * 0.3)),
        col_colors=col_colors,
        xticklabels=False, yticklabels=True,
        cbar_kws={'label': 'log10(relative abundance)'}
    )
    g.savefig('taxa_heatmap.png', dpi=150, bbox_inches='tight')
    plt.close()

taxa_heatmap(data, sig_taxa_df, metadata, group_col='group')
```

---

## Key Microbiome Knowledge

### Major Phyla and Clinical Associations

| Phylum | Key Genera | Role | Disease Associations |
|--------|-----------|------|---------------------|
| **Firmicutes** | Faecalibacterium, Roseburia, Ruminococcus, Clostridium, Lactobacillus | SCFA production, carbohydrate fermentation | Decreased in IBD; F/B ratio altered in obesity (debated) |
| **Bacteroidetes** | Bacteroides, Prevotella, Alistipes | Polysaccharide degradation, propionate production | Prevotella enriched in high-fiber diets; Bacteroides in Western diets |
| **Proteobacteria** | Escherichia, Klebsiella, Helicobacter | Facultative anaerobes, bloom in dysbiosis | Expansion is a signature of dysbiosis across diseases |
| **Actinobacteria** | Bifidobacterium, Collinsella | Acetate/lactate production, immune modulation | Bifidobacterium depletion in elderly, post-antibiotics |
| **Verrucomicrobia** | Akkermansia | Mucin degradation, barrier integrity | Decreased in obesity, T2D; inversely correlates with metabolic syndrome |
| **Fusobacteria** | Fusobacterium | Diverse metabolism | F. nucleatum enriched in colorectal cancer |

### Key SCFA Producers

| SCFA | Primary Producers | Function |
|------|-------------------|----------|
| **Butyrate** | Faecalibacterium prausnitzii, Roseburia intestinalis, Eubacterium rectale | Colonocyte energy source (70%), barrier integrity, anti-inflammatory (Treg induction), HDAC inhibition |
| **Propionate** | Bacteroides spp., Prevotella spp., Akkermansia muciniphila | Gluconeogenesis substrate, satiety signaling (GPR41/43), anti-inflammatory |
| **Acetate** | Bifidobacterium spp., Blautia spp., most anaerobes | Most abundant SCFA, systemic energy, appetite regulation, pathogen resistance |

### Disease-Specific Microbiome Signatures

```
Inflammatory Bowel Disease (IBD):
- Decreased: Faecalibacterium, Roseburia, Ruminococcus (butyrate producers)
- Increased: Escherichia, Fusobacterium, Ruminococcus gnavus
- Reduced alpha diversity, increased beta diversity dispersion

Clostridioides difficile Infection (CDI):
- Dramatic diversity loss
- Loss of secondary bile acid producers (Clostridium scindens)
- FMT restores diversity and secondary bile acid metabolism

Obesity / Metabolic Syndrome:
- F/B ratio findings inconsistent across studies
- More consistent: reduced gene richness, reduced Akkermansia
- Functional: reduced butyrate production capacity, altered bile acid metabolism

Colorectal Cancer:
- Enriched: Fusobacterium nucleatum, Peptostreptococcus, Porphyromonas
- Depleted: Roseburia, Lachnospiraceae
- F. nucleatum promotes tumor growth via FadA adhesin and Wnt signaling

Type 2 Diabetes:
- Reduced butyrate producers
- Increased Lactobacillus (paradoxically)
- Decreased Akkermansia muciniphila
- Altered branched-chain amino acid metabolism
```

---

## Evidence Grading

### Microbiome Evidence Tiers

| Tier | Study Type | Examples | Weight |
|------|-----------|----------|--------|
| **T1** | Interventional studies, RCTs | FMT trials, probiotic RCTs, diet interventions with microbiome endpoints | Highest |
| **T2** | Prospective cohorts | Longitudinal birth cohorts, pre-disease sampling with incident outcomes | High |
| **T3** | Cross-sectional / observational | Case-control 16S studies, single-timepoint metagenomics | Moderate |
| **T4** | In silico prediction | PICRUSt2 functional prediction, network inference, computational modeling | Lowest |

### Evidence Grading Logic

```
T1 criteria (INTERVENTIONAL):
  - Randomized controlled trial or crossover design
  - Microbiome is primary or secondary endpoint
  - Adequate sample size (power calculation reported)
  - Causal inference possible
  - Examples: FMT for CDI (T1), targeted dietary intervention with microbiome monitoring

T2 criteria (PROSPECTIVE COHORT):
  - Longitudinal sampling before outcome occurs
  - Temporal precedence established
  - Confounders measured and adjusted
  - Examples: birth cohort with allergy outcomes, pre-diagnostic cancer cohort

T3 criteria (CROSS-SECTIONAL):
  - Single timepoint comparison
  - Cannot establish causation (chicken-or-egg problem)
  - Medication and diet confounders often uncontrolled
  - Examples: IBD vs. healthy 16S study, obesity case-control

T4 criteria (IN SILICO):
  - Computational prediction without direct measurement
  - PICRUSt2 functional prediction from 16S (accuracy ~80% for well-characterized environments)
  - Network inference from co-occurrence (many false positives)
  - Requires experimental validation to upgrade
```

### Reporting Template

```
When presenting microbiome findings, use this format:

  Finding: Faecalibacterium prausnitzii depletion in disease group
  Evidence tier: T3 (cross-sectional 16S comparison)
  Effect size: Mean relative abundance 2.1% (disease) vs 8.3% (healthy)
  Statistical test: ALDEx2, padj=0.003, effect_size=1.8
  Biological context: Major butyrate producer; depletion associated with
    reduced anti-inflammatory signaling (butyrate -> Treg induction)
  Literature support: Sokol et al. 2008 (PNAS); Quevrain et al. 2016 (Gut)
  Limitations: Cross-sectional design; cannot determine if depletion is
    cause or consequence of disease
  Actionable: Consider butyrate supplementation or F. prausnitzii-containing
    next-generation probiotics (experimental, T4 evidence for efficacy)
```

---

## Boundary Rules

```
DO:
- Write and execute Python code for full microbiome analysis pipelines
- Process OTU/ASV tables, taxonomy files, phylogenetic trees
- Calculate alpha diversity (Shannon, Simpson, Chao1, Faith's PD, evenness)
- Calculate beta diversity (Bray-Curtis, Jaccard, Aitchison, UniFrac)
- Run PERMANOVA, ANOSIM, betadisper for group comparisons
- Perform differential abundance (ALDEx2-style, LEfSe-style, DESeq2-style)
- Score dysbiosis (F/B ratio, dysbiosis index, CST, Proteobacteria bloom)
- Predict functional capacity (SCFA production, pathway inference)
- Assess drug-microbiome interactions
- Generate publication-ready visualizations (stacked bars, PCoA, heatmaps, rarefaction)
- Apply compositionality-aware methods (CLR, ALDEx2, ANCOM-BC logic)

DO NOT:
- Perform raw sequence processing (demultiplexing, primer trimming, denoising)
- Run DADA2 or QIIME2 pipelines (those are upstream)
- Do host gene expression analysis (hand off to rnaseq-deseq2 skill)
- Build protein interaction networks (use systems-biology or protein-interactions skill)
- Perform multi-omics integration (use multi-omics-integration skill)
- Make clinical treatment recommendations (report evidence, not prescriptions)
```

### Multi-Agent Workflow Examples

**"Analyze my 16S rRNA data comparing IBD patients to healthy controls"**
1. Microbiome Analysis -> Full pipeline: quality filtering, alpha/beta diversity, PERMANOVA, differential abundance, dysbiosis scoring
2. Biomarker Discovery -> Build diagnostic classifier from microbiome signatures
3. Literature Deep Research -> Validate findings against published IBD microbiome studies

**"Characterize the gut microbiome changes in our drug trial"**
1. Microbiome Analysis -> Baseline vs. post-treatment comparison, drug-microbiome interaction assessment, SCFA producer scoring
2. Statistical Modeling -> Mixed-effects models for longitudinal microbiome changes
3. Clinical Trial Analyst -> Contextualize microbiome endpoints within trial design

**"Integrate metagenomics with metabolomics from the same cohort"**
1. Microbiome Analysis -> Taxonomic and functional profiling from metagenomics
2. Metabolomics Analysis -> Metabolite identification and pathway enrichment
3. Multi-Omics Integration -> Cross-layer correlation, pathway concordance, integrative clustering

**"Score microbiome health for a wellness cohort and identify intervention targets"**
1. Microbiome Analysis -> Microbiome Health Score, CST assignment, functional capacity, dysbiosis index
2. Biomarker Discovery -> Identify taxa most predictive of low MHS
3. Disease Research -> Literature context for depleted beneficial taxa and intervention options

**"Predict functional capacity from 16S data and validate with KEGG pathways"**
1. Microbiome Analysis -> SCFA producer scoring, PICRUSt2-style prediction, pathway mapping
2. KEGG Database -> Validate predicted pathways against KEGG reference maps
3. Systems Biology -> Metabolic network context for predicted functions

---

## GEO Public Data Integration

### `mcp__geo__geo_data` (Microbiome Dataset Discovery)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_datasets` | Find 16S rRNA and shotgun metagenomics datasets | `query`, `organism`, `study_type` |
| `get_series_info` | Get microbiome study details (sequencing platform, sample size, study design) | `accession` |
| `get_download_links` | Download public microbiome data for reference comparisons | `accession` |

**Workflow — GEO for microbiome reference data:**
Search GEO for public 16S rRNA and shotgun metagenomics datasets for reference comparisons. Use `search_datasets` to find relevant microbiome studies, `get_series_info` to review study design and sequencing details, and `get_download_links` to obtain data for benchmarking or meta-analysis.

```
mcp__geo__geo_data(method: "search_datasets", query: "16S rRNA gut microbiome")
→ Find public 16S rRNA datasets for reference comparisons

mcp__geo__geo_data(method: "get_series_info", accession: "GSExxxxx")
→ Review microbiome study design: sequencing platform, sample counts, metadata availability

mcp__geo__geo_data(method: "get_download_links", accession: "GSExxxxx")
→ Download microbiome data for benchmarking against user's dataset
```

## Completeness Checklist

- [ ] Data orientation validated (taxa x samples) and input format confirmed
- [ ] Rarefaction applied for alpha diversity; raw counts used for differential abundance
- [ ] Alpha diversity calculated (Shannon, Simpson, Chao1, evenness) with group comparisons
- [ ] Beta diversity computed (Bray-Curtis, Jaccard) with PERMANOVA significance test
- [ ] Compositionality-aware method used for differential abundance (ALDEx2, ANCOM-BC, or LEfSe)
- [ ] Dysbiosis scoring performed (F/B ratio, dysbiosis index, Proteobacteria bloom)
- [ ] Functional prediction or SCFA producer scoring completed where applicable
- [ ] Evidence tier (T1-T4) assigned to each finding based on study design
- [ ] Drug-microbiome interactions assessed if medication data available
- [ ] Publication-ready visualizations generated (stacked bars, PCoA, heatmap)
