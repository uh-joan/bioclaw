---
name: metabolomics-analysis
description: Metabolomics and metabolic profiling data analysis. LC-MS, GC-MS data processing, metabolite identification, pathway mapping, differential metabolite analysis, metabolic flux, HMDB, KEGG metabolic pathways, lipidomics, untargeted metabolomics, targeted metabolomics. Use when user mentions metabolomics, metabolite, LC-MS, GC-MS, metabolic profiling, lipidomics, metabolic flux, HMDB, metabolic pathway, metabolite identification, mass spectrometry metabolomics, or metabolome.
---

# Metabolomics Analysis

Metabolomics data analysis for LC-MS and GC-MS experiments. The agent writes and executes Python code for peak table processing, normalization, statistical analysis, metabolite identification, pathway mapping, biomarker discovery, and visualization. Supports both targeted and untargeted workflows, including lipidomics.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_metabolomics-analysis_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Gene-level pathway enrichment from integrated omics -> use `gene-enrichment`
- Systems-level network modeling and integration -> use `systems-biology`
- Multi-omics factor analysis with transcriptomics/proteomics -> use `multiomic-disease-characterization`
- Drug-metabolite interaction analysis -> use `drug-interaction-analyst`
- KEGG pathway lookup without metabolomics data processing -> use `kegg-database`
- Proteomics data processing (TMT, label-free quantification) -> use `proteomics-analysis`

## Cross-Reference: Other Skills

- **Gene-level pathway enrichment from integrated omics** -> use gene-enrichment skill
- **Systems-level network integration** -> use systems-biology skill
- **Multi-omics integration with transcriptomics** -> use multiomic-disease-characterization skill
- **Drug-metabolite interaction analysis** -> use drug-interaction-analyst skill
- **Disease context for metabolic signatures** -> use disease-research skill

## Python Environment

The container has `numpy`, `pandas`, `scipy`, `scikit-learn`, `matplotlib`, `seaborn`, `statsmodels` pre-installed. For specialized packages, install at runtime:

```python
import subprocess
subprocess.run(["pip", "install", "pyopenms", "ms_entropy"], check=True)
```

## Data Input Formats

| Format | Extension | Handling |
|--------|-----------|----------|
| **Peak table** | `.csv`, `.tsv` | Feature intensity matrix (features x samples) via `pd.read_csv` |
| **mzML** | `.mzML` | Parse with `pyopenms` for chromatograms and spectra |
| **MGF** | `.mgf` | Text parsing for MS2 spectral matching |
| **Vendor output** | `.csv` | Progenesis, MZmine, MetaboAnalyst — map columns to standard format |

Orientation heuristic: if nrows >> ncols, assume features x samples (correct). If ncols >> nrows, transpose. Check if row names contain m/z values, RT, or HMDB IDs to confirm.

## Available MCP Tools

### `mcp__kegg__kegg_data` (Compound Identification & Metabolic Pathways)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_compounds` | Search KEGG compounds by name or formula | `query` |
| `get_compound_info` | Compound details (formula, exact mass, pathways) | `compound_id` |
| `get_compound_reactions` | Reactions involving a compound | `compound_id` |
| `search_pathways` | Search metabolic pathways by keyword | `query` |
| `get_pathway_info` | Full pathway details (description, classes) | `pathway_id` |
| `get_pathway_compounds` | All compounds in a metabolic pathway | `pathway_id` |
| `get_pathway_reactions` | All reactions in a pathway | `pathway_id` |
| `search_reactions` | Search biochemical reactions | `query` |
| `get_reaction_info` | Reaction details (substrates, products, enzymes) | `reaction_id` |
| `search_enzymes` | Search enzymes catalyzing metabolic reactions | `query` |
| `get_enzyme_info` | Enzyme details (reactions, substrates, cofactors) | `enzyme_id` |
| `convert_identifiers` | Convert KEGG compound IDs to/from HMDB, PubChem, ChEBI | `identifiers`, `source_db`, `target_db` |
| `batch_entry_lookup` | Batch lookup of multiple KEGG entries | `entry_ids` |

### `mcp__reactome__reactome_data` (Pathway Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_pathways` | Search pathways by keyword | `query`, `species` |
| `get_pathway_participants` | Molecules in a pathway | `pathway_id` |
| `get_pathway_reactions` | Reactions in a pathway | `pathway_id` |

---

## Analysis Pipeline

### Phase 1: Data Import & QC

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# ---- Load and validate ----
def load_peak_table(file_path, metadata_path=None):
    sep = '\t' if file_path.endswith(('.tsv', '.txt')) else ','
    data = pd.read_csv(file_path, sep=sep, index_col=0)
    if data.shape[0] < data.shape[1]:
        print(f"Shape {data.shape}: transposing to features x samples")
        data = data.T
    metadata = pd.read_csv(metadata_path, index_col=0) if metadata_path else None
    if metadata is not None:
        common = data.columns.intersection(metadata.index)
        data, metadata = data[common], metadata.loc[common]
    print(f"Loaded: {data.shape[0]} features x {data.shape[1]} samples")
    return data, metadata

data, metadata = load_peak_table("peak_table.csv", "sample_metadata.csv")

# ---- Blank subtraction ----
def blank_subtraction(data, metadata, blank_label="Blank", fold_threshold=3):
    if 'sample_type' not in metadata.columns:
        return data
    blank_cols = metadata[metadata['sample_type'] == blank_label].index
    sample_cols = metadata[metadata['sample_type'] != blank_label].index
    if len(blank_cols) == 0:
        return data
    blank_mean = data[blank_cols].mean(axis=1)
    sample_mean = data[sample_cols].mean(axis=1)
    keep = (sample_mean > fold_threshold * blank_mean) | (blank_mean == 0)
    print(f"Blank subtraction: removed {(~keep).sum()} features")
    return data.loc[keep, sample_cols]

# ---- QC sample CV assessment ----
def assess_qc(data, metadata, qc_label="QC", cv_threshold=30):
    if 'sample_type' not in metadata.columns:
        return data
    qc_cols = metadata[metadata['sample_type'] == qc_label].index
    if len(qc_cols) < 3:
        return data
    cv = (data[qc_cols].std(axis=1) / data[qc_cols].mean(axis=1)) * 100
    reliable = cv < cv_threshold
    print(f"QC CV: {reliable.sum()}/{len(cv)} features with CV < {cv_threshold}%")
    return data.loc[reliable]

# ---- Missing value handling ----
def handle_missing(data, min_present=0.5):
    data = data.replace(0, np.nan)
    keep = data.notna().mean(axis=1) >= min_present
    data = data.loc[keep]
    from sklearn.impute import KNNImputer
    imputed = KNNImputer(n_neighbors=5).fit_transform(data.T)
    return pd.DataFrame(imputed.T, index=data.index, columns=data.columns)

data = blank_subtraction(data, metadata)
data = assess_qc(data, metadata)
data = handle_missing(data)
```

### Phase 2: Normalization & Scaling

```python
def normalize(data, method="pqn"):
    if method == "tic":
        sums = data.sum(axis=0)
        return data / sums * sums.median()
    elif method == "pqn":
        sums = data.sum(axis=0)
        tic = data / sums * sums.median()
        reference = tic.median(axis=1)
        quotients = tic.div(reference, axis=0)
        factors = quotients.median(axis=0)
        print(f"PQN factors range: {factors.min():.3f} - {factors.max():.3f}")
        return tic.div(factors, axis=1)
    elif method == "median":
        meds = data.median(axis=0)
        return data / meds * meds.median()

def transform_and_scale(data, transform="log2", scaling="pareto"):
    if transform in ("log2", "log10"):
        offset = data[data > 0].min().min() / 2
        data = np.log2(data + offset) if transform == "log2" else np.log10(data + offset)
    means = data.mean(axis=1)
    centered = data.sub(means, axis=0)
    if scaling == "pareto":
        return centered.div(np.sqrt(data.std(axis=1)), axis=0)
    elif scaling == "auto":
        return centered.div(data.std(axis=1), axis=0)
    elif scaling == "range":
        return centered.div(data.max(axis=1) - data.min(axis=1), axis=0)
    return centered

norm_data = normalize(data, method="pqn")
scaled_data = transform_and_scale(norm_data, transform="log2", scaling="pareto")
```

### Phase 3: Statistical Analysis

```python
from sklearn.decomposition import PCA
from sklearn.cross_decomposition import PLSRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import cross_val_score, LeaveOneOut
from statsmodels.stats.multitest import multipletests

# ---- PCA ----
def run_pca(data, metadata, group_col="group", n_components=5):
    pca = PCA(n_components=n_components)
    scores = pca.fit_transform(data.T.values)
    ev = pca.explained_variance_ratio_ * 100
    fig, ax = plt.subplots(figsize=(10, 8))
    for grp in metadata[group_col].unique():
        mask = metadata[group_col] == grp
        ax.scatter(scores[mask, 0], scores[mask, 1], label=grp, s=80, alpha=0.7)
    ax.set_xlabel(f"PC1 ({ev[0]:.1f}%)"); ax.set_ylabel(f"PC2 ({ev[1]:.1f}%)")
    ax.set_title("PCA Score Plot"); ax.legend()
    plt.savefig("pca_score_plot.png", dpi=150); plt.close()
    return scores, pca

# ---- PLS-DA with VIP scores ----
def run_plsda(data, metadata, group_col="group", n_components=2):
    X = data.T.values
    y = LabelEncoder().fit_transform(metadata[group_col])
    plsda = PLSRegression(n_components=n_components)
    plsda.fit(X, y)
    cv = LeaveOneOut() if len(y) < 30 else 10
    q2 = cross_val_score(PLSRegression(n_components=n_components), X, y, cv=cv, scoring='r2').mean()
    print(f"PLS-DA Q2: {q2:.3f}")
    # VIP scores
    W, T, Q = plsda.x_weights_, plsda.x_scores_, plsda.y_loadings_
    ss = np.sum(T**2 * Q**2, axis=1).sum()
    vips = np.sqrt(W.shape[0] * np.sum(W**2 * np.sum(T**2 * Q**2, axis=1), axis=1) / ss)
    vip_df = pd.DataFrame({'feature': data.index, 'VIP': vips}).sort_values('VIP', ascending=False)
    return vip_df, plsda, q2

# ---- Univariate differential analysis ----
def differential_analysis(data, metadata, group_col="group", g1="control", g2="treatment"):
    g1_cols = metadata[metadata[group_col] == g1].index
    g2_cols = metadata[metadata[group_col] == g2].index
    results = []
    for feat in data.index:
        v1 = data.loc[feat, g1_cols].astype(float).values
        v2 = data.loc[feat, g2_cols].astype(float).values
        t_stat, p_val = stats.ttest_ind(v2, v1, equal_var=False)
        results.append({'feature': feat, 'log2FC': v2.mean() - v1.mean(),
                        'p_value': p_val, 't_stat': t_stat})
    df = pd.DataFrame(results).set_index('feature')
    _, df['padj'], _, _ = multipletests(df['p_value'], method='fdr_bh')
    sig = df[(df['padj'] < 0.05) & (df['log2FC'].abs() > 1)].sort_values('padj')
    print(f"Significant: {len(sig)} ({(sig['log2FC']>0).sum()} up, {(sig['log2FC']<0).sum()} down)")
    return df, sig

scores, pca_model = run_pca(scaled_data, metadata)
vip_df, plsda_model, q2 = run_plsda(scaled_data, metadata)
results_df, sig_metabolites = differential_analysis(scaled_data, metadata)
```

### Phase 4: Metabolite Identification

Assign putative identities using accurate mass matching with adduct rules and ppm tolerance.

```python
ADDUCTS_POS = {'[M+H]+': 1.007276, '[M+Na]+': 22.989218, '[M+K]+': 38.963158, '[M+NH4]+': 18.034164}
ADDUCTS_NEG = {'[M-H]-': -1.007276, '[M+FA-H]-': 44.998201, '[M+Cl]-': 34.969402}

def identify_features(mz_list, hmdb_masses, mode="positive", ppm=5):
    """Match observed m/z to HMDB monoisotopic masses. Returns MSI Level 3 hits."""
    adducts = ADDUCTS_POS if mode == "positive" else ADDUCTS_NEG
    matches = []
    for mz in mz_list:
        for adduct_name, adduct_mass in adducts.items():
            neutral = mz - adduct_mass
            tol = neutral * ppm / 1e6
            hits = hmdb_masses[(hmdb_masses['mass'] >= neutral - tol) &
                               (hmdb_masses['mass'] <= neutral + tol)]
            for _, h in hits.iterrows():
                ppm_err = abs(h['mass'] - neutral) / neutral * 1e6
                matches.append({'mz': mz, 'adduct': adduct_name, 'hmdb_id': h['hmdb_id'],
                                'name': h['name'], 'ppm_error': ppm_err, 'msi_level': 3})
    return pd.DataFrame(matches).sort_values('ppm_error') if matches else pd.DataFrame()
```

### Phase 4b: MS2 Spectral Matching

When MS2 data is available, spectral matching elevates identification from Level 3 to Level 2.

```python
def cosine_similarity(spec1, spec2, mz_tol=0.01):
    """Cosine similarity between two MS2 spectra (list of [mz, intensity] pairs)."""
    spec1 = np.array(spec1); spec2 = np.array(spec2)
    # Normalize intensities to unit vector
    spec1[:, 1] /= np.linalg.norm(spec1[:, 1])
    spec2[:, 1] /= np.linalg.norm(spec2[:, 1])
    # Match peaks within tolerance
    matched_product = 0.0
    for mz1, i1 in spec1:
        diffs = np.abs(spec2[:, 0] - mz1)
        if diffs.min() < mz_tol:
            matched_product += i1 * spec2[diffs.argmin(), 1]
    return matched_product

def match_ms2_to_library(query_spectra, library_spectra, score_threshold=0.7):
    """
    Match experimental MS2 spectra against a reference library.
    query_spectra: dict of {feature_id: [[mz, intensity], ...]}
    library_spectra: dict of {compound_name: {'spectrum': [...], 'hmdb_id': str}}
    """
    matches = []
    for feat_id, query in query_spectra.items():
        best_score, best_match = 0, None
        for name, ref in library_spectra.items():
            score = cosine_similarity(query, ref['spectrum'])
            if score > best_score:
                best_score, best_match = score, name
        if best_score >= score_threshold:
            matches.append({'feature': feat_id, 'match': best_match,
                            'cosine_score': best_score, 'msi_level': 2})
        else:
            matches.append({'feature': feat_id, 'match': best_match,
                            'cosine_score': best_score, 'msi_level': 3})
    return pd.DataFrame(matches)
```

### Phase 5: Pathway Analysis

KEGG metabolite set enrichment analysis (MSEA) using Fisher's exact test. Use the KEGG MCP tool to dynamically retrieve pathway-compound mappings:

```
mcp__kegg__kegg_data(method: "search_compounds", query: "L-carnitine")
→ Resolve metabolite name to KEGG compound ID (e.g., C00318)

mcp__kegg__kegg_data(method: "get_compound_info", compound_id: "C00318")
→ Get compound details including pathways, reactions, and exact mass

mcp__kegg__kegg_data(method: "get_pathway_compounds", pathway_id: "map00071")
→ Get all compounds in fatty acid beta-oxidation for MSEA background

mcp__kegg__kegg_data(method: "get_reaction_info", reaction_id: "R01280")
→ Get reaction substrates, products, and catalyzing enzymes
```

```python
KEGG_PATHWAYS = {
    'Glycolysis': ['C00031', 'C00036', 'C00074', 'C00084', 'C00111', 'C00118', 'C00186'],
    'TCA Cycle': ['C00022', 'C00024', 'C00036', 'C00042', 'C00122', 'C00149', 'C00158'],
    'Amino Acid Metabolism': ['C00025', 'C00037', 'C00041', 'C00049', 'C00064', 'C00065',
                              'C00073', 'C00078', 'C00079', 'C00082', 'C00123', 'C00148'],
    'Purine Metabolism': ['C00020', 'C00044', 'C00059', 'C00131', 'C00144', 'C00147'],
    'Glutathione Metabolism': ['C00051', 'C00127', 'C00320', 'C00669', 'C01879'],
    'Sphingolipid Metabolism': ['C00065', 'C00195', 'C00319', 'C00550', 'C01120'],
}

def msea(sig_kegg_ids, all_kegg_ids, pathway_db=KEGG_PATHWAYS, min_overlap=2):
    """Over-representation analysis for metabolite pathways (Fisher's exact)."""
    N, n = len(set(all_kegg_ids)), len(set(sig_kegg_ids))
    results = []
    for name, compounds in pathway_db.items():
        pw = set(compounds)
        K = len(pw & set(all_kegg_ids))
        k = len(pw & set(sig_kegg_ids))
        if k < min_overlap:
            continue
        table = np.array([[k, n-k], [K-k, N-n-K+k]])
        _, p = stats.fisher_exact(table, alternative='greater')
        results.append({'pathway': name, 'overlap': k, 'detected': K, 'ratio': f"{k}/{K}", 'p_value': p})
    df = pd.DataFrame(results)
    if len(df):
        _, df['padj'], _, _ = multipletests(df['p_value'], method='fdr_bh')
        df = df.sort_values('padj')
    return df
```

### Phase 6: Biomarker Discovery

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegressionCV
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.model_selection import StratifiedKFold

# ---- Single-metabolite ROC ----
def single_roc(data, metadata, group_col="group", g1="control", g2="treatment"):
    mask = metadata[group_col].isin([g1, g2])
    y = (metadata.loc[mask, group_col] == g2).astype(int)
    roc = [{'feature': f, 'AUC': max(roc_auc_score(y, data.loc[f, y.index]), 1 - roc_auc_score(y, data.loc[f, y.index]))} for f in data.index]
    return pd.DataFrame(roc).sort_values('AUC', ascending=False)

# ---- Random forest importance ----
def rf_importance(data, metadata, group_col="group"):
    X, y = data.T.values, LabelEncoder().fit_transform(metadata[group_col])
    rf = RandomForestClassifier(n_estimators=500, random_state=42, n_jobs=-1)
    rf.fit(X, y)
    acc = cross_val_score(rf, X, y, cv=StratifiedKFold(5, shuffle=True, random_state=42)).mean()
    imp = pd.DataFrame({'feature': data.index, 'importance': rf.feature_importances_}).sort_values('importance', ascending=False)
    print(f"RF CV Accuracy: {acc:.3f}")
    return imp

# ---- LASSO panel ----
def lasso_panel(data, metadata, group_col="group"):
    X, y = data.T.values, LabelEncoder().fit_transform(metadata[group_col])
    lasso = LogisticRegressionCV(penalty='l1', solver='saga', cv=5, Cs=20, max_iter=10000, random_state=42)
    lasso.fit(X, y)
    coefs = pd.DataFrame({'feature': data.index, 'coef': lasso.coef_[0]})
    selected = coefs[coefs['coef'] != 0].sort_values('coef', key=abs, ascending=False)
    print(f"LASSO selected {len(selected)}/{len(data.index)} features")
    return selected
```

### Phase 7: Visualization

```python
# ---- Volcano plot ----
def volcano_plot(results_df, padj_thresh=0.05, fc_thresh=1.0, top_labels=10):
    fig, ax = plt.subplots(figsize=(10, 8))
    df = results_df.copy()
    df['neg_log_p'] = -np.log10(df['padj'].clip(lower=1e-300))
    for cat, color, cond in [('Increased', '#E74C3C', (df['padj']<padj_thresh)&(df['log2FC']>fc_thresh)),
                              ('Decreased', '#3498DB', (df['padj']<padj_thresh)&(df['log2FC']<-fc_thresh)),
                              ('NS', '#BBBBBB', ~((df['padj']<padj_thresh)&(df['log2FC'].abs()>fc_thresh)))]:
        ax.scatter(df.loc[cond, 'log2FC'], df.loc[cond, 'neg_log_p'], c=color, s=20, alpha=0.6, label=f"{cat} ({cond.sum()})")
    ax.axhline(-np.log10(padj_thresh), ls='--', color='black', lw=0.5)
    ax.axvline(fc_thresh, ls='--', color='black', lw=0.5)
    ax.axvline(-fc_thresh, ls='--', color='black', lw=0.5)
    ax.set_xlabel('log2 Fold Change'); ax.set_ylabel('-log10(padj)')
    ax.set_title('Differential Metabolites'); ax.legend()
    plt.savefig('volcano_plot.png', dpi=150); plt.close()

# ---- Heatmap ----
def metabolite_heatmap(data, sig_features, metadata, group_col="group", top_n=50):
    feats = sig_features.head(top_n).index
    col_order = metadata.sort_values(group_col).index
    palette = dict(zip(metadata[group_col].unique(), sns.color_palette("Set1")))
    col_colors = metadata.loc[col_order, group_col].map(palette)
    g = sns.clustermap(data.loc[feats, col_order], col_cluster=False, cmap='RdBu_r', center=0,
                       figsize=(12, max(8, top_n*0.25)), col_colors=col_colors, xticklabels=False)
    g.savefig('metabolite_heatmap.png', dpi=150, bbox_inches='tight'); plt.close()

# ---- Box plots ----
def box_plots(data, metadata, sig_features, group_col="group", top_n=9):
    feats = sig_features.head(top_n).index
    ncols, nrows = 3, int(np.ceil(top_n / 3))
    fig, axes = plt.subplots(nrows, ncols, figsize=(12, 4*nrows))
    for i, (feat, ax) in enumerate(zip(feats, axes.flatten())):
        pd_df = pd.DataFrame({'intensity': data.loc[feat], 'group': metadata.loc[data.columns, group_col]})
        sns.boxplot(data=pd_df, x='group', y='intensity', ax=ax, palette='Set1')
        sns.stripplot(data=pd_df, x='group', y='intensity', ax=ax, color='black', size=4, alpha=0.5)
        ax.set_title(feat, fontsize=9)
    plt.tight_layout(); plt.savefig('box_plots.png', dpi=150); plt.close()

volcano_plot(results_df)
metabolite_heatmap(scaled_data, sig_metabolites, metadata)
box_plots(scaled_data, metadata, sig_metabolites)
```

---

## Identification Confidence Levels (MSI)

The Metabolomics Standards Initiative defines four levels:

| MSI Level | Name | Requirements |
|-----------|------|-------------|
| **Level 1** | Identified compound | Matched to authentic reference standard under identical conditions (same instrument, chromatography). RT + MS1 + MS2 match required. |
| **Level 2** | Putatively annotated | MS2 spectral library match (HMDB, MassBank, METLIN, GNPS) without authentic standard. Report cosine similarity score. |
| **Level 3** | Putatively characterized class | Assigned to chemical class based on physicochemical properties or diagnostic fragments (e.g., m/z 184.07 for phosphatidylcholines). |
| **Level 4** | Unknown | Detected and quantified but unidentified. Characterized only by m/z and retention time. |

NEVER claim Level 1 without authentic standard data. NEVER report Level 2-3 as confirmed identifications. ALWAYS report the proportion of Level 4 unknowns.

### Reporting Template

```
When presenting results, use this format for each identified metabolite:

  Metabolite: L-Carnitine
  MSI Level: 2 (putatively annotated)
  Evidence: MS2 cosine similarity 0.87 vs HMDB0000062 (MassBank)
  m/z: 162.1125 [M+H]+
  RT: 1.23 min
  log2FC: 1.45 (increased in treatment)
  padj: 0.003
  VIP: 1.82
  Pathway: Fatty acid beta-oxidation (KEGG: map00071)
  Tier: T1

For unknown features (Level 4):
  Feature: mz_342.1156_4.23min
  MSI Level: 4 (unknown)
  m/z: 342.1156
  RT: 4.23 min
  Putative formula: C12H22O11 (mass error 1.2 ppm)
  log2FC: -2.01
  padj: 0.0001
  Tier: T4 — prioritize for MS2 acquisition
```

---

## Batch Effect Detection and Correction

```
Metabolomics batch effect decision logic:

1. Detect batch variables in metadata:
   - Columns: batch, run_order, plate, injection_date, instrument
   - QC sample drift across run order indicates batch effects

2. Assess severity:
   - PCA colored by batch: if batch separates more than biology -> severe
   - QC sample clustering: QCs should cluster tightly regardless of batch

3. Correction methods (in order of preference):
   - QC-LOESS: fit LOESS curve to QC samples per feature, correct samples
   - ComBat: parametric batch correction (from sva/pycombat)
   - Median centering per batch: simple but effective for mild effects

4. Validation after correction:
   - QC samples should cluster in PCA
   - Biological groups should separate, not batches
   - Feature CVs in QCs should decrease after correction
```

```python
def qc_loess_correction(data, metadata, run_order_col='run_order', qc_label='QC'):
    """QC-LOESS signal drift correction."""
    from statsmodels.nonparametric.smoothers_lowess import lowess
    qc_mask = metadata['sample_type'] == qc_label
    qc_order = metadata.loc[qc_mask, run_order_col].values
    all_order = metadata[run_order_col].values
    corrected = data.copy()
    for feat in data.index:
        qc_vals = data.loc[feat, qc_mask].values
        if np.std(qc_vals) == 0:
            continue
        fitted = lowess(qc_vals, qc_order, frac=0.7, return_sorted=False)
        interp = np.interp(all_order, qc_order, fitted)
        median_qc = np.median(qc_vals)
        corrected.loc[feat] = data.loc[feat] * (median_qc / interp)
    return corrected
```

---

## Lipidomics-Specific Workflow

### Lipid Class Identification

```python
LIPID_MARKERS = {
    'PC':  {'head_mz': 184.0733, 'mode': 'pos', 'range': (600, 900)},
    'LPC': {'head_mz': 184.0733, 'mode': 'pos', 'range': (450, 600)},
    'SM':  {'head_mz': 184.0733, 'mode': 'pos', 'range': (650, 850)},
    'Cer': {'frag_mz': 264.2686, 'mode': 'pos', 'range': (500, 700)},
    'TAG': {'adduct': '[M+NH4]+', 'mode': 'pos', 'range': (750, 1000)},
}

def classify_lipids(mz_list, ms2_data=None, mode="pos"):
    results = []
    for mz in mz_list:
        cls, evidence = "Unclassified", "none"
        for name, m in LIPID_MARKERS.items():
            if m['mode'] != mode:
                continue
            if m['range'][0] <= mz <= m['range'][1]:
                if ms2_data and mz in ms2_data and 'head_mz' in m:
                    if any(abs(f - m['head_mz']) < 0.01 for f in ms2_data[mz]):
                        cls, evidence = name, f"MS2 head group {m['head_mz']}"
                        break
                cls, evidence = name, f"m/z range {m['range']}"
        results.append({'mz': mz, 'class': cls, 'evidence': evidence})
    return pd.DataFrame(results)
```

### Lipid Pathway Activity Markers

Key lipid ratios to calculate as pathway activity proxies:

| Ratio | Biological Meaning |
|-------|-------------------|
| LPC/PC | PLA2 activity, inflammation |
| PC/PE | Membrane integrity, PEMT activity |
| Ceramide/SM | Sphingomyelinase activity, apoptosis |
| C16:1/C16:0 | SCD1 desaturase index |

Map to KEGG pathways: glycerophospholipid metabolism (map00564), sphingolipid metabolism (map00600), arachidonic acid metabolism (map00590).

Cross-validate with Reactome:
```
mcp__reactome__reactome_data(method: "search_pathways", query: "sphingolipid metabolism", species: "Homo sapiens")
→ Reactome pathway IDs for cross-referencing KEGG metabolite set enrichment results

mcp__reactome__reactome_data(method: "get_pathway_participants", pathway_id: "R-HSA-XXXXX")
→ All molecules (metabolites, proteins, complexes) in the pathway for overlap calculation
```

---

## Evidence Grading & Multi-Agent Examples

### Metabolomics Evidence Tiers

| Tier | ID Level | Stats | Pathway | Confidence |
|------|----------|-------|---------|------------|
| **T1** | MSI Level 1 | padj < 0.01, VIP > 1.5 | KEGG enrichment padj < 0.05 | High |
| **T2** | MSI Level 2 (cosine > 0.7) | padj < 0.05, VIP > 1.0 | Mapped to known pathway | Medium-High |
| **T3** | MSI Level 3 | padj < 0.05 | Putative pathway | Medium |
| **T4** | MSI Level 4 | padj < 0.05 | None | Low |

### Evidence Grading Logic

```
T1 criteria (HIGH confidence):
  - MSI Level 1 or Level 2 with cosine > 0.9
  - padj < 0.01 AND VIP > 1.5 AND top 20 in random forest
  - Confirmed in KEGG pathway with enrichment padj < 0.05
  - Consistent direction across multivariate and univariate methods
  - Supported by published metabolomics literature

T2 criteria (MEDIUM-HIGH confidence):
  - MSI Level 2 with cosine > 0.7
  - padj < 0.05 AND (VIP > 1.0 OR AUC > 0.8)
  - Mapped to known metabolic pathway in KEGG or HMDB

T3 criteria (MEDIUM confidence):
  - MSI Level 3 (compound class only)
  - padj < 0.05 in at least one statistical test
  - Putative pathway assignment based on class membership

T4 criteria (LOW confidence — flag for follow-up):
  - MSI Level 4 (unknown, m/z + RT only)
  - Statistically significant but no structural information
  - Prioritize for targeted MS2 acquisition in validation study
```

### Boundary Rules

```
DO:
- Write and execute Python code for full metabolomics pipelines
- Process peak tables, mzML files, and vendor export formats
- Normalize (TIC, PQN, median), transform (log), and scale (Pareto, auto)
- Run PCA, PLS-DA, univariate tests, fold change analysis
- Match features to HMDB by accurate mass and adduct rules
- Perform MS2 spectral matching when fragment data is available
- Run metabolite set enrichment analysis (MSEA) against KEGG
- Build biomarker panels (ROC, random forest, LASSO)
- Generate publication-ready figures (volcano, heatmap, PCA, box plots)
- Classify lipids by class and calculate pathway activity ratios
- Correct batch effects using QC-LOESS or ComBat

DO NOT:
- Perform raw data conversion (mzML conversion is upstream)
- Run chromatographic peak picking (use MZmine/XCMS upstream)
- Do gene-level enrichment (hand off to gene-enrichment skill)
- Build protein interaction networks (use systems-biology skill)
- Perform multi-omics factor analysis (use multiomic-disease-characterization)
```

### Multi-Agent Workflow Examples

**"Analyze my LC-MS metabolomics data comparing disease vs healthy controls"**
1. Metabolomics Analysis -> QC, normalization, PCA, PLS-DA, differential analysis, volcano plot, heatmap
2. Gene Enrichment -> MSEA on significant KEGG compound IDs
3. Disease Research -> Disease associations for enriched metabolic pathways

**"Identify biomarkers from untargeted metabolomics of patient plasma"**
1. Metabolomics Analysis -> Full pipeline: PCA/PLS-DA, univariate testing, ROC, random forest, LASSO panel
2. Disease Research -> Literature context for candidate biomarkers
3. Systems Biology -> Metabolite-gene network integration

**"Process lipidomics data and map altered lipids to pathways"**
1. Metabolomics Analysis -> Lipid class ID, differential analysis, lipid ratios, sphingolipid/glycerophospholipid pathway mapping
2. Gene Enrichment -> Enrichment of lipid metabolism genes from multi-omics
3. Drug Interaction Analyst -> Drug effects on lipid metabolism enzymes

**"Compare metabolic profiles between treatment arms in a clinical trial"**
1. Metabolomics Analysis -> Batch-corrected normalization, multi-group PCA, pairwise differential analysis, biomarker panel
2. Multiomic Disease Characterization -> Integrate with transcriptomics/proteomics from same cohort

**"Perform metabolic flux estimation from isotope tracing data"**
1. Metabolomics Analysis -> Load isotopologue distributions, correct for natural abundance, estimate fractional enrichment and relative flux
2. Systems Biology -> Flux balance modeling and metabolic network context

## Completeness Checklist

- [ ] Data orientation validated (features x samples) and QC checks performed
- [ ] Blank subtraction and QC CV assessment applied where applicable
- [ ] Normalization method selected and justified (TIC, PQN, or median)
- [ ] Batch effects assessed and corrected if detected (QC-LOESS, ComBat)
- [ ] PCA and PLS-DA performed with Q2 cross-validation reported
- [ ] Differential analysis completed with FDR correction (padj < 0.05)
- [ ] MSI identification levels assigned (Level 1-4) with no overclaimed IDs
- [ ] Metabolite set enrichment analysis (MSEA) run against KEGG pathways
- [ ] Evidence tier (T1-T4) assigned to each reported metabolite finding
- [ ] Publication-ready figures generated (volcano, heatmap, PCA, box plots)
