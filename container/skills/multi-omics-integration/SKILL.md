---
name: multi-omics-integration
description: Multi-omics data integration and cross-platform analysis. Integrating transcriptomics, proteomics, metabolomics, epigenomics data layers. MOFA-like factor analysis, correlation-based integration, pathway-level integration, cross-omics concordance, data fusion. Use when user mentions multi-omics, omics integration, data integration, cross-platform, MOFA, multi-modal omics, transcriptomics proteomics integration, data fusion, pan-omics, or integrative analysis.
---

# Multi-Omics Integration

> **Code recipes**: See [integration-recipes.md](integration-recipes.md) for copy-paste executable code templates covering MOFA2, DIABLO, SNF, MCIA, iCluster+, WGCNA, and more.

Computational methodology for integrating multiple omics data layers into unified biological models. Provides Python code templates for early, intermediate, and late integration strategies -- combining transcriptomics, proteomics, metabolomics, and epigenomics from the same or overlapping sample sets. All analysis runs as Python code inside the agent container.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_multi-omics-integration_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Single-cell multi-modal analysis (scRNA-seq + CITE-seq + ATAC-seq) → use `single-cell-analysis`
- Disease-focused multi-omic characterization with clinical context → use `multiomic-disease-characterization`
- Pathway topology modeling and network reconstruction → use `systems-biology`
- Proteomics-specific preprocessing (TMT, LFQ, DIA normalization) → use `proteomics-analysis`
- Metabolomics-specific preprocessing and annotation → use `metabolomics-analysis`
- Epigenomic data processing (ChIP-seq, ATAC-seq, bisulfite-seq) → use `epigenomics`

## Cross-Reference: Other Skills

- **Single-cell multi-modal analysis** -> use single-cell-analysis skill
- **Proteomics-specific preprocessing** -> use proteomics-analysis skill
- **Metabolomics-specific preprocessing** -> use metabolomics-analysis skill
- **Epigenomic data processing** -> use epigenomics skill
- **Disease-level multi-omic characterization** -> use multiomic-disease-characterization skill
- **Pathway topology and network modeling** -> use systems-biology skill

## Python Environment

```python
import subprocess
subprocess.check_call(["pip", "install", "-q",
    "numpy", "pandas", "scipy", "scikit-learn",
    "matplotlib", "seaborn", "statsmodels", "networkx"])
```

## Integration Strategies

| Strategy | When to Use | Pros | Cons |
|----------|-------------|------|------|
| **Early** (concatenation) | >80% sample overlap, <5k features/layer | Simple; captures cross-layer covariance | Scale differences dominate |
| **Intermediate** (factor analysis) | >50% overlap, want interpretable factors | Biologically interpretable; handles missing views | Needs tuning |
| **Late** (meta-analysis) | <50% overlap or different cohorts | Robust to platform differences | Loses cross-layer covariance |

---

## Available MCP Tools

### `mcp__reactome__reactome_data` (Pathway Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `find_pathways_by_gene` | Pathways containing a gene | `gene_id`, `species` |
| `get_pathway_details` | Full pathway info | `pathway_id` |
| `get_pathway_hierarchy` | Parent/child pathway tree | `pathway_id` |

### `mcp__kegg__kegg_data` (Cross-Omics Pathway Mapping)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_pathways` | Search KEGG pathways by keyword | `query` |
| `get_pathway_info` | Full pathway details (description, classes, modules) | `pathway_id` |
| `get_pathway_genes` | All genes in a pathway (for transcript/protein layer mapping) | `pathway_id` |
| `get_pathway_compounds` | All compounds in a pathway (for metabolomics layer mapping) | `pathway_id` |
| `get_pathway_reactions` | All reactions in a pathway (links enzymes to metabolites) | `pathway_id` |
| `search_modules` | Search functional modules | `query` |
| `get_module_info` | Module details (pathway context, components) | `module_id` |
| `convert_identifiers` | Convert between KEGG and external IDs | `identifiers`, `source_db`, `target_db` |

### `mcp__stringdb__stringdb_data` (Network-Based Integration & Enrichment)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_interaction_network` | Build interaction network from protein list | `protein_ids`, `species`, `required_score`, `network_type`, `add_nodes` |
| `get_functional_enrichment` | GO/KEGG/Reactome enrichment for protein set | `protein_ids`, `species`, `background_string_identifiers` |
| `get_protein_annotations` | Get functional annotations | `protein_ids`, `species` |
| `search_proteins` | Search proteins by name | `query`, `species`, `limit` |

---

## Analysis Pipeline

### Phase 1: Per-Layer Preprocessing

Standardize each layer independently: log-transform counts, impute missing values, filter low-variance features, z-score normalize.

```python
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.impute import KNNImputer

def preprocess_omics_layer(df, layer_name, log_transform=True,
                           impute_method="knn", var_filter_q=0.2):
    """Preprocess a single omics layer (samples x features)."""
    qc = {"layer": layer_name, "n_samples": df.shape[0],
          "n_features_raw": df.shape[1],
          "missing_frac": round(df.isna().sum().sum() / df.size, 4)}

    if log_transform:
        df = np.log2(df.clip(lower=0) + 1)

    if qc["missing_frac"] > 0:
        if impute_method == "knn":
            imp = KNNImputer(n_neighbors=5)
            df = pd.DataFrame(imp.fit_transform(df), index=df.index, columns=df.columns)
        else:
            df = df.fillna(df.median())

    # Filter low-variance features by MAD
    mads = df.apply(lambda x: np.median(np.abs(x - np.median(x))))
    df = df[mads[mads >= mads.quantile(var_filter_q)].index]
    qc["n_features_kept"] = df.shape[1]

    # Z-score normalize
    scaler = StandardScaler()
    df_scaled = pd.DataFrame(scaler.fit_transform(df), index=df.index, columns=df.columns)

    print(f"[{layer_name}] {qc['n_features_raw']} -> {qc['n_features_kept']} features | "
          f"missing: {qc['missing_frac']:.1%}")
    return df_scaled, qc
```

### Phase 2: Sample Matching & QC

Align samples across layers and assess completeness to choose integration strategy.

```python
def match_samples(layer_dict):
    """Find shared samples across omics layers, return matched DataFrames."""
    layer_samples = {n: set(df.index) for n, df in layer_dict.items()}
    all_samples = set.union(*layer_samples.values())
    shared = set.intersection(*layer_samples.values())

    # Presence matrix
    presence = pd.DataFrame(
        {n: [s in samps for s in sorted(all_samples)]
         for n, samps in layer_samples.items()},
        index=sorted(all_samples))

    # Pairwise overlaps
    names = list(layer_dict.keys())
    pairwise = {}
    for i, n1 in enumerate(names):
        for n2 in names[i+1:]:
            pairwise[f"{n1} x {n2}"] = len(layer_samples[n1] & layer_samples[n2])

    completeness = len(shared) / len(all_samples) if all_samples else 0
    print(f"Samples: {len(all_samples)} total | {len(shared)} shared | "
          f"completeness: {completeness:.1%}")

    matched = {n: df.loc[sorted(shared)] for n, df in layer_dict.items()}

    # Recommend strategy
    if completeness >= 0.8:
        rec = "early"
    elif completeness >= 0.5:
        rec = "intermediate"
    elif len(shared) >= 20:
        rec = "late"
    else:
        rec = "insufficient"
    print(f"Recommended strategy: {rec}")

    return matched, presence, {"completeness": completeness, "n_shared": len(shared),
                                "recommendation": rec, "pairwise": pairwise}
```

### Phase 3: Correlation-Based Integration

Cross-omics correlation matrices and canonical correlation analysis (CCA).

```python
from scipy.stats import spearmanr, pearsonr
from sklearn.cross_decomposition import CCA
from statsmodels.stats.multitest import multipletests

def cross_omics_correlation(layer1, layer2, l1_name="L1", l2_name="L2",
                            method="spearman", top_n=50):
    """Cross-omics feature-feature correlation with FDR correction."""
    var1 = layer1.var().nlargest(top_n).index
    var2 = layer2.var().nlargest(top_n).index
    L1, L2 = layer1[var1], layer2[var2]

    corr_func = spearmanr if method == "spearman" else pearsonr
    corr_mat = np.zeros((len(var1), len(var2)))
    pval_mat = np.zeros_like(corr_mat)

    for i in range(len(var1)):
        for j in range(len(var2)):
            r, p = corr_func(L1.iloc[:, i], L2.iloc[:, j])
            corr_mat[i, j], pval_mat[i, j] = r, p

    corr_df = pd.DataFrame(corr_mat, index=var1, columns=var2)
    reject, adj_p, _, _ = multipletests(pval_mat.flatten(), method="fdr_bh")

    sig = []
    for idx, (i, j) in enumerate(np.ndindex(len(var1), len(var2))):
        if reject[idx]:
            sig.append({f"{l1_name}_feature": var1[i], f"{l2_name}_feature": var2[j],
                       "r": corr_mat[i, j], "adj_p": adj_p[idx]})

    sig_df = pd.DataFrame(sig).sort_values("adj_p") if sig else pd.DataFrame()
    print(f"Cross-correlation ({l1_name} x {l2_name}): {len(sig_df)} significant pairs")
    return corr_df, sig_df


def run_cca(layer1, layer2, n_components=5, top_n=100):
    """Regularized CCA between two omics layers."""
    var1 = layer1.var().nlargest(top_n).index
    var2 = layer2.var().nlargest(top_n).index
    n_comp = min(n_components, len(var1), len(var2), layer1.shape[0] - 1)

    cca = CCA(n_components=n_comp, max_iter=1000)
    X_c, Y_c = cca.fit_transform(layer1[var1].values, layer2[var2].values)

    canon_corrs = [round(pearsonr(X_c[:, k], Y_c[:, k])[0], 4)
                   for k in range(n_comp)]
    print(f"CCA canonical correlations: {canon_corrs}")

    return {"canonical_correlations": canon_corrs,
            "x_loadings": pd.DataFrame(cca.x_loadings_, index=var1,
                                        columns=[f"CC{k+1}" for k in range(n_comp)]),
            "y_loadings": pd.DataFrame(cca.y_loadings_, index=var2,
                                        columns=[f"CC{k+1}" for k in range(n_comp)])}
```

### Phase 4: Factor Analysis (MOFA-like)

Multi-view factor analysis via alternating least squares. Discovers shared and layer-specific latent factors.

```python
from sklearn.decomposition import PCA

def multi_view_factor_analysis(layer_dict, n_factors=10, max_iter=200, tol=1e-4):
    """Simplified MOFA-like multi-view factor analysis via alternating LS."""
    samples = list(layer_dict.values())[0].index
    n_samples = len(samples)

    # Initialize via concatenated PCA
    concat = pd.concat(list(layer_dict.values()), axis=1)
    n_f = min(n_factors, n_samples - 1)
    Z = PCA(n_components=n_f).fit_transform(concat.values)

    weights = {}
    for it in range(max_iter):
        # Update weights per layer
        ZtZ_inv = np.linalg.pinv(Z.T @ Z)
        for name, df in layer_dict.items():
            weights[name] = (ZtZ_inv @ Z.T @ df.values).T

        # Update factors
        Z_new = np.zeros_like(Z)
        for name, df in layer_dict.items():
            W = weights[name]
            Z_new += df.values @ W @ np.linalg.pinv(W.T @ W)
        Z_new /= len(layer_dict)

        delta = np.linalg.norm(Z_new - Z) / (np.linalg.norm(Z) + 1e-10)
        Z = Z_new
        if delta < tol:
            print(f"Converged at iteration {it + 1}")
            break

    # Variance explained per layer per factor
    factor_cols = [f"Factor{k+1}" for k in range(n_f)]
    activity = {}
    for name, df in layer_dict.items():
        total_var = np.var(df.values) * df.size
        W = weights[name]
        activity[name] = [np.var(np.outer(Z[:, k], W[:, k])) *
                          Z.shape[0] * W.shape[0] / total_var
                          for k in range(n_f)]

    activity_df = pd.DataFrame(activity, index=factor_cols).T
    print("\nVariance explained per layer:")
    for name in layer_dict:
        print(f"  {name}: {sum(activity[name]):.1%}")

    factors_df = pd.DataFrame(Z, index=samples, columns=factor_cols)
    weights_df = {n: pd.DataFrame(W, index=layer_dict[n].columns, columns=factor_cols)
                  for n, W in weights.items()}
    return {"factors": factors_df, "weights": weights_df, "factor_activity": activity_df}


def classify_factors(factor_activity, threshold=0.01):
    """Classify factors as shared (active in 2+ layers) or layer-specific."""
    result = {}
    for factor in factor_activity.columns:
        active = factor_activity.index[factor_activity[factor] > threshold].tolist()
        ftype = "shared" if len(active) >= 2 else ("specific" if len(active) == 1 else "inactive")
        result[factor] = {"type": ftype, "active_in": active}
        if ftype != "inactive":
            print(f"  {factor}: {ftype} -> {', '.join(active)}")
    return result
```

### Phase 5: Pathway-Level Integration

Score pathway activity per sample per layer, then measure pathway concordance across layers.

**STRING enrichment for cross-omics gene sets:** After identifying top features per layer, use STRING to enrich overlapping gene sets:
```
mcp__stringdb__stringdb_data(method: "get_functional_enrichment", protein_ids: ["TOP_RNA_GENE1", "TOP_PROT_GENE2", "TOP_METAB_ENZYME3"], species: 9606)
→ Pathway enrichment across omics layers to identify shared biological themes
```

**KEGG cross-omics pathway mapping:** Use KEGG to build pathway gene AND compound sets for cross-layer scoring:
```
mcp__kegg__kegg_data(method: "get_pathway_genes", pathway_id: "hsa04010")
→ Gene members for transcript/protein layer pathway scoring

mcp__kegg__kegg_data(method: "get_pathway_compounds", pathway_id: "hsa04010")
→ Compound members for metabolomics layer pathway scoring — enables cross-layer pathway concordance
```

**Reactome pathway-level integration:** Use Reactome to build pathway gene sets for cross-layer scoring:
```
mcp__reactome__reactome_data(method: "find_pathways_by_gene", gene_id: "HUB_GENE", species: "Homo sapiens")
→ Reactome pathways for hub genes identified from factor analysis or cross-layer correlation

mcp__reactome__reactome_data(method: "get_pathway_details", pathway_id: "R-HSA-XXXXX")
→ Full pathway description and hierarchy context for pathway-level integration scoring
```

```python
def compute_pathway_scores(layer_df, pathway_sets, method="mean_z"):
    """Compute pathway activity scores (samples x pathways) from z-scored layer."""
    scores = {}
    for pw, genes in pathway_sets.items():
        present = [g for g in genes if g in layer_df.columns]
        if len(present) < 3:
            continue
        if method == "mean_z":
            scores[pw] = layer_df[present].mean(axis=1)
        elif method == "ssgsea":
            ranked = layer_df.rank(axis=1)
            out = [c for c in layer_df.columns if c not in present]
            scores[pw] = ranked[present].mean(axis=1) - ranked[out].mean(axis=1)
    result = pd.DataFrame(scores)
    print(f"Scored {result.shape[1]}/{len(pathway_sets)} pathways")
    return result


def pathway_concordance(layer_scores_dict, method="spearman"):
    """Assess pathway activity concordance across layers."""
    names = list(layer_scores_dict.keys())
    shared_pw = sorted(set.intersection(
        *[set(df.columns) for df in layer_scores_dict.values()]))

    results = []
    for pw in shared_pw:
        rs = []
        for i, n1 in enumerate(names):
            for n2 in names[i+1:]:
                r, _ = (spearmanr if method == "spearman" else pearsonr)(
                    layer_scores_dict[n1][pw], layer_scores_dict[n2][pw])
                rs.append(r)
        results.append({"pathway": pw, "mean_r": np.mean(rs),
                        "min_r": np.min(rs), "n_concordant": sum(r > 0.3 for r in rs)})

    df = pd.DataFrame(results).sort_values("mean_r", ascending=False)
    print(f"Pathway concordance: {len(shared_pw)} pathways | "
          f"highly concordant (r>0.5): {(df['mean_r'] > 0.5).sum()}")
    return df
```

### Phase 6: Concordance Analysis

Measure agreement between specific layer pairs where biology sets the expected direction.

```python
def mrna_protein_concordance(rna_df, prot_df, gene_map=None):
    """Assess mRNA-protein concordance (expected positive correlation)."""
    if gene_map:
        prot_df = prot_df.rename(columns=gene_map)
    shared = sorted(set(rna_df.columns) & set(prot_df.columns))
    print(f"Shared genes: {len(shared)}")

    results = []
    for gene in shared:
        r, p = spearmanr(rna_df[gene], prot_df[gene])
        results.append({"gene": gene, "spearman_r": round(r, 4), "p": p})

    df = pd.DataFrame(results)
    _, adj_p, _, _ = multipletests(df["p"], method="fdr_bh")
    df["adj_p"] = adj_p
    df = df.sort_values("spearman_r", ascending=False)

    n_pos = (df["spearman_r"] > 0).sum()
    print(f"  Concordant (r>0): {n_pos}/{len(shared)} ({n_pos/len(shared):.1%})")
    print(f"  Median r: {df['spearman_r'].median():.3f}")
    return df


def methylation_expression_concordance(meth_df, expr_df, probe_gene_map):
    """Assess methylation-expression anti-correlation (expected negative)."""
    results = []
    for probe, gene in probe_gene_map.items():
        if probe not in meth_df.columns or gene not in expr_df.columns:
            continue
        r, p = spearmanr(meth_df[probe], expr_df[gene])
        results.append({"probe": probe, "gene": gene, "spearman_r": round(r, 4), "p": p})

    df = pd.DataFrame(results)
    if df.empty:
        return df

    _, adj_p, _, _ = multipletests(df["p"], method="fdr_bh")
    df["adj_p"] = adj_p
    n_neg = (df["spearman_r"] < 0).sum()
    print(f"Methylation-expression: {len(df)} pairs | "
          f"anti-correlated: {n_neg} ({n_neg/len(df):.1%})")
    return df.sort_values("spearman_r")
```

### Phase 7: Network-Based Integration

Multi-layer network construction from cross-omics correlations with community detection.

**STRING network overlay:** Use STRING to build a PPI backbone for the multi-omics network:
```
mcp__stringdb__stringdb_data(method: "get_interaction_network", protein_ids: ["HUB_GENE_1", "HUB_GENE_2", "HUB_GENE_3"], species: 9606, required_score: 400, network_type: "physical", add_nodes: 10)
→ PPI network from STRING to overlay on cross-omics correlation network, validating community structure with known physical interactions
```

```python
import networkx as nx

def build_multi_layer_network(cross_corr_list, corr_thresh=0.5, p_thresh=0.05):
    """Build network from cross-omics correlations.

    cross_corr_list: list of dicts with keys layer1, layer2, sig_df.
    """
    G = nx.Graph()
    for entry in cross_corr_list:
        l1, l2 = entry["layer1"], entry["layer2"]
        for _, row in entry["sig_df"].iterrows():
            f1, f2 = row.iloc[0], row.iloc[1]
            r = row["r"]
            p = row.get("adj_p", 1.0)
            if abs(r) >= corr_thresh and p < p_thresh:
                n1, n2 = f"{l1}:{f1}", f"{l2}:{f2}"
                G.add_node(n1, layer=l1)
                G.add_node(n2, layer=l2)
                G.add_edge(n1, n2, weight=abs(r), correlation=r)

    print(f"Network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges, "
          f"{nx.number_connected_components(G)} components")
    return G


def detect_communities(G):
    """Louvain community detection with cross-layer composition analysis."""
    if G.number_of_nodes() == 0:
        return {}, pd.DataFrame()

    communities = nx.community.louvain_communities(G, seed=42)
    comm_map = {}
    comp = []
    for i, comm in enumerate(communities):
        for node in comm:
            comm_map[node] = i
        layers = {}
        for node in comm:
            l = G.nodes[node].get("layer", "?")
            layers[l] = layers.get(l, 0) + 1
        comp.append({"community": i, "size": len(comm), "n_layers": len(layers), **layers})

    comp_df = pd.DataFrame(comp)
    multi = (comp_df["n_layers"] > 1).sum()
    print(f"Communities: {len(communities)} | {multi} span multiple layers")
    return comm_map, comp_df
```

### Phase 8: Biomarker Discovery

Multi-omics feature selection and integrative clustering for biomarker panels.

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.cluster import SpectralClustering
from sklearn.metrics import silhouette_score
from sklearn.metrics.pairwise import rbf_kernel, euclidean_distances

def multi_omics_feature_selection(layer_dict, labels, n_top=20, n_folds=5):
    """Select top features per layer via RF, evaluate individual and combined AUC."""
    selected, perf = {}, {}
    for name, df in layer_dict.items():
        y = labels.loc[df.index].values
        rf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
        rf.fit(df.values, y)
        top = pd.Series(rf.feature_importances_, index=df.columns).nlargest(n_top)
        selected[name] = top
        cv = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)
        scores = cross_val_score(rf, df[top.index].values, y, cv=cv, scoring="roc_auc")
        perf[name] = {"auc": f"{scores.mean():.3f} +/- {scores.std():.3f}"}
        print(f"  {name}: AUC = {perf[name]['auc']}")

    # Combined
    combined = pd.concat(
        [layer_dict[n][sel.index].rename(columns=lambda c: f"{n}:{c}")
         for n, sel in selected.items()], axis=1)
    y = labels.loc[combined.index].values
    rf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    cv = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)
    scores = cross_val_score(rf, combined.values, y, cv=cv, scoring="roc_auc")
    perf["combined"] = {"auc": f"{scores.mean():.3f} +/- {scores.std():.3f}"}
    print(f"  Combined: AUC = {perf['combined']['auc']}")
    return selected, combined, perf


def integrative_clustering(layer_dict, k_range=(2, 6)):
    """SNF-inspired integrative clustering: fuse per-layer similarities, then cluster."""
    samples = list(layer_dict.values())[0].index

    # Per-layer RBF similarity with adaptive bandwidth
    sims = []
    for df in layer_dict.values():
        dists = euclidean_distances(df.values)
        med = np.median(dists[np.triu_indices_from(dists, k=1)])
        gamma = 1.0 / (2 * med**2) if med > 0 else 1.0
        sims.append(rbf_kernel(df.values, gamma=gamma))

    fused = np.mean(sims, axis=0)
    fused /= (fused.sum(axis=1, keepdims=True) + 1e-10)

    results = {}
    for k in range(k_range[0], k_range[1] + 1):
        labels = SpectralClustering(n_clusters=k, affinity="precomputed",
                                     random_state=42).fit_predict(fused)
        sil = silhouette_score(1 - fused, labels, metric="precomputed")
        results[k] = {"labels": pd.Series(labels, index=samples), "silhouette": round(sil, 4)}
        print(f"  k={k}: silhouette = {sil:.3f}")

    best = max(results, key=lambda k: results[k]["silhouette"])
    print(f"Best k={best} (silhouette={results[best]['silhouette']:.3f})")
    return results, pd.DataFrame(fused, index=samples, columns=samples)
```

---

## Integration Method Selection Guide

```
START -> How many layers?
  |
  2 layers -> CCA / correlation (Phase 3) + concordance (Phase 6)
  |           Want pathway view? -> Phase 5
  |           Want biomarkers?   -> Phase 8
  |
  3+ layers -> Sample overlap > 50%?
               YES -> MOFA-like factor analysis (Phase 4) + pathway (Phase 5)
               NO  -> Late integration via pathway scores (Phase 5) or network (Phase 7)
               Want biomarkers? -> Integrative clustering (Phase 8)
```

| Scenario | Phases | Rationale |
|----------|--------|-----------|
| RNA-seq + proteomics, same patients | 1-3, 6 | Direct mRNA-protein concordance |
| 3+ omics, high overlap | 1-2, 4-5, 8 | MOFA finds shared factors |
| Different cohorts per layer | 1-2, 5, 7 | Pathway-level tolerates partial overlap |
| Discovery biomarkers | 1-2, 3/4, 8 | Feature selection + integrative clustering |
| Regulatory mechanisms | 1-2, 6-7 | Methylation-expression + network topology |
| Time-series multi-omics | 1-2, 3, 5 | Correlation at matched time points + pathway dynamics |
| Single-cell multi-modal | 1-2, 4, 7 | Factor analysis on shared cells + network view |

**Quality checkpoints before proceeding:**
- After Phase 1: Each layer should have >100 features retained and <30% missing data
- After Phase 2: At least 20 shared samples for meaningful correlation
- After Phase 3/4: Check that top correlations or factor loadings are biologically plausible
- After Phase 8: Validate biomarker panel stability with repeated cross-validation

---

## Concordance Interpretation

| Layer Pair | Expected | Typical r | Discordance Meaning |
|------------|----------|-----------|---------------------|
| mRNA - Protein | Positive | 0.3-0.6 | Post-transcriptional regulation, protein stability |
| Promoter methylation - mRNA | Negative | -0.2 to -0.5 | Context-dependent; gene body methylation can be positive |
| Enhancer accessibility - mRNA | Positive | 0.2-0.5 | Depends on enhancer-promoter contact |
| Phosphoproteome - Proteome | Weak positive | 0.1-0.3 | Phosphorylation is rapid and transient |
| Metabolite - Enzyme mRNA | Variable | 0.0-0.3 | Flux depends on kinetics, not just abundance |

**Sources of low concordance:**
1. **Technical:** Different sample preparation protocols, batch effects, platform-specific biases, normalization artifacts
2. **Biological:** Post-transcriptional regulation (miRNA, RNA-binding proteins), protein half-life differences (minutes to weeks), feedback loops, compartmentalization
3. **Temporal:** Layers measured at different time points after perturbation -- mRNA responds in hours, protein in days, metabolites in minutes

**When discordance is informative:**
- High mRNA / low protein: rapid turnover or translational repression -- investigate miRNA targets and ubiquitin ligases
- Low methylation / no expression: needs additional activating signals -- check histone marks and transcription factor availability
- Metabolite uncorrelated with enzyme: allosteric or post-translational flux control -- consider metabolic control analysis
- Protein up / mRNA unchanged: protein stabilization, reduced degradation -- check autophagy and proteasome status

**Expected concordance rates in practice:**
- Healthy tissue mRNA-protein: 50-70% genes show positive correlation
- Cancer mRNA-protein: 40-60% concordant (more post-transcriptional dysregulation)
- Promoter methylation-expression: 30-50% show expected anti-correlation
- Cross-tissue comparisons generally show higher concordance than within-tissue variation

---

## Evidence Grading & Multi-Agent Examples

### Evidence Grading

| Grade | Criteria |
|-------|----------|
| **High** | Concordant across 3+ layers, significant in factor analysis, replicated |
| **Moderate** | Concordant in 2 layers, or 1 layer with pathway support |
| **Low** | Single layer only or contradictory cross-layer evidence |
| **Discordant** | Opposite direction across layers (investigate post-transcriptional regulation) |

### Multi-Agent Workflow Examples

**"Integrate RNA-seq and proteomics from my patient cohort"**
1. Multi-Omics Integration -> Phase 1-3 + Phase 6 (mRNA-protein concordance)
2. Single-Cell Analysis -> Deconvolve bulk signal if scRNA-seq available
3. Systems Biology -> Pathway enrichment on concordant/discordant gene sets

**"Run MOFA-like analysis on three omics layers"**
1. Multi-Omics Integration -> Phase 1-2 + Phase 4 (factor analysis)
2. Systems Biology -> Map factor loadings to pathways
3. Multiomic Disease Characterization -> Contextualize factors with known disease biology

**"Find multi-omics biomarkers for treatment response"**
1. Multi-Omics Integration -> Full pipeline, emphasis on Phase 8
2. Proteomics Analysis -> Deep QC before integration
3. Metabolomics Analysis -> Metabolite annotation before integration

**"Compare methylation and expression in tumor vs normal"**
1. Multi-Omics Integration -> Phase 1-2 + Phase 6 (methylation-expression)
2. Epigenomics -> DMR analysis, CpG island context
3. Systems Biology -> Pathway enrichment on epigenetically silenced genes

**"Build a multi-omics network for my disease model"**
1. Multi-Omics Integration -> Phase 1-3 + Phase 7 (network + communities)
2. Systems Biology -> Overlay pathway annotations on communities
3. Multiomic Disease Characterization -> Validate hubs against known disease drivers

**"Integrate spatial transcriptomics with bulk proteomics"**
1. Multi-Omics Integration -> Phase 1-2 (match spatial spots to bulk) + Phase 5 (pathway-level)
2. Single-Cell Analysis -> Deconvolve spatial spots into cell types
3. Proteomics Analysis -> Map protein abundance to spatial regions via deconvolution

---

## GEO Public Data Integration

### `mcp__geo__geo_data` (Multi-Omic Dataset Discovery)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_datasets` | Find multi-omic datasets (expression + methylation, proteomics + transcriptomics) | `query`, `organism`, `study_type` |
| `get_series_info` | Get study design details (platforms, sample counts, multi-layer availability) | `accession` |
| `search_by_gene` | Find gene-specific datasets across multiple omics platforms | `gene`, `organism` |

**Workflow — GEO for multi-omic dataset discovery:**
Search GEO for multi-omic datasets (expression + methylation, proteomics + transcriptomics) for integration analysis. Use `search_datasets` to find studies with multiple data layers, `get_series_info` to confirm platform coverage and sample overlap, and `search_by_gene` to locate datasets containing specific genes of interest across omics types.

```
mcp__geo__geo_data(method: "search_datasets", query: "multi-omics transcriptomics proteomics integration")
→ Discover public multi-omic datasets for integration analysis

mcp__geo__geo_data(method: "get_series_info", accession: "GSExxxxx")
→ Confirm study design: number of samples, platforms used, multi-layer availability

mcp__geo__geo_data(method: "search_by_gene", gene: "TP53", organism: "Homo sapiens")
→ Find datasets with TP53 measurements across expression, methylation, and protein platforms
```

## Completeness Checklist

- [ ] Per-layer preprocessing completed with QC metrics (features retained, missing fraction) for each omics layer
- [ ] Sample matching performed and completeness ratio calculated across all layers
- [ ] Integration strategy (early/intermediate/late) selected based on sample overlap and justified
- [ ] Cross-omics correlations computed with FDR correction and significant pairs reported
- [ ] Factor analysis or CCA results include biologically interpretable loadings
- [ ] Pathway-level integration scored and concordance assessed across layers
- [ ] Network-based integration includes community detection with cross-layer composition
- [ ] Biomarker discovery includes cross-validated AUC for individual and combined layer panels
- [ ] All figures and tables synthesized into report (no raw tool output)
- [ ] Report file verified: no `[Analyzing...]` placeholders remain
