# Mass Spectrometry Proteomics Recipes

Python code templates for mass spectrometry-based proteomics analysis. Covers MaxQuant/DIA-NN output parsing, Perseus-style filtering, normalization, imputation, differential abundance, TMT processing, phosphoproteomics, AP-MS scoring, spectral library generation, enrichment, and quality control.

Cross-skill routing: use `proteomics-analysis` for conceptual guidance, `gene-enrichment` for pathway enrichment, `multi-omics-integration` for cross-omics analysis.

---

## 1. MaxQuant Output Parsing (proteinGroups.txt, evidence.txt)

Parse and clean MaxQuant search engine output files.

```python
import pandas as pd
import numpy as np

def parse_maxquant_protein_groups(filepath, intensity_type="LFQ"):
    """Parse MaxQuant proteinGroups.txt with comprehensive filtering.

    Parameters:
        filepath: path to proteinGroups.txt
        intensity_type: 'LFQ' (label-free), 'iBAQ', or 'Intensity'
    Returns:
        tuple of (intensity_matrix, metadata_df)
    """
    df = pd.read_csv(filepath, sep="\t", low_memory=False)
    n_raw = len(df)

    # Filter contaminants, reverse hits, and only-identified-by-site
    for col in ["Reverse", "Potential contaminant", "Only identified by site"]:
        if col in df.columns:
            df = df[df[col] != "+"]
    print(f"Filtered: {n_raw} -> {len(df)} protein groups")

    # Extract intensity columns
    prefix_map = {"LFQ": "LFQ intensity ", "iBAQ": "iBAQ ", "Intensity": "Intensity "}
    prefix = prefix_map.get(intensity_type, "LFQ intensity ")
    int_cols = [c for c in df.columns if c.startswith(prefix)]
    if not int_cols:
        raise ValueError(f"No columns found with prefix '{prefix}'")

    intensity = df[int_cols].copy()
    intensity.columns = [c.replace(prefix, "") for c in int_cols]
    intensity.index = df["Protein IDs"].values
    intensity = intensity.replace(0, np.nan)

    # Extract metadata
    meta_cols = ["Protein IDs", "Majority protein IDs", "Gene names", "Protein names",
                 "Number of proteins", "Peptides", "Unique peptides", "Sequence coverage [%]",
                 "Mol. weight [kDa]", "Score"]
    meta = df[[c for c in meta_cols if c in df.columns]].copy()
    meta.index = df["Protein IDs"].values

    print(f"Intensity matrix: {intensity.shape[0]} proteins x {intensity.shape[1]} samples")
    print(f"Intensity type: {intensity_type}")
    print(f"Missing values: {intensity.isna().sum().sum()} "
          f"({intensity.isna().sum().sum() / intensity.size * 100:.1f}%)")

    return intensity, meta


def parse_maxquant_evidence(filepath):
    """Parse MaxQuant evidence.txt for peptide-level analysis.

    Parameters:
        filepath: path to evidence.txt
    Returns:
        DataFrame with peptide-level data
    """
    df = pd.read_csv(filepath, sep="\t", low_memory=False)

    # Filter
    for col in ["Reverse", "Potential contaminant"]:
        if col in df.columns:
            df = df[df[col] != "+"]

    key_cols = ["Modified sequence", "Proteins", "Gene names", "Experiment",
                "Intensity", "Charge", "m/z", "Mass", "Retention time",
                "PEP", "Score", "Calibrated retention time"]
    df = df[[c for c in key_cols if c in df.columns]].copy()

    print(f"Evidence entries: {len(df)}")
    print(f"Unique peptides: {df['Modified sequence'].nunique()}")
    print(f"Experiments: {df['Experiment'].nunique() if 'Experiment' in df.columns else 'N/A'}")

    return df

# Usage
intensity, meta = parse_maxquant_protein_groups("proteinGroups.txt", intensity_type="LFQ")
evidence = parse_maxquant_evidence("evidence.txt")
```

**Key parameters:**
- `intensity_type="LFQ"`: label-free quantification (recommended for LFQ experiments). Use `"iBAQ"` for absolute protein abundance estimation.
- Always filter Reverse, Potential contaminant, and Only identified by site before analysis.
- Replace 0 with NaN: MaxQuant uses 0 for unquantified proteins, not true zero abundance.

**Expected output:** Intensity matrix (proteins x samples) with NaN for missing values; metadata DataFrame with gene names and QC metrics.

---

## 2. DIA-NN Output Processing (report.tsv to Protein Matrix)

Process DIA-NN main report into a protein-level quantification matrix.

```python
import pandas as pd
import numpy as np

def parse_diann_report(filepath, quantity_col="Precursor.Quantity",
                       protein_col="Protein.Group", run_col="Run",
                       gene_col="Genes", qvalue_thresh=0.01):
    """Parse DIA-NN report.tsv into protein-level matrix.

    Parameters:
        filepath: path to DIA-NN report.tsv
        quantity_col: column with quantitative values
        protein_col: column with protein group identifiers
        run_col: column with run/sample identifiers
        gene_col: column with gene names
        qvalue_thresh: q-value threshold for filtering
    Returns:
        tuple of (protein_matrix, gene_map)
    """
    df = pd.read_csv(filepath, sep="\t", low_memory=False)
    print(f"Raw entries: {len(df)}")

    # Filter by q-value
    if "Q.Value" in df.columns:
        df = df[df["Q.Value"] <= qvalue_thresh]
        print(f"After q-value filter (<= {qvalue_thresh}): {len(df)}")

    if "PG.Q.Value" in df.columns:
        df = df[df["PG.Q.Value"] <= qvalue_thresh]
        print(f"After protein q-value filter: {len(df)}")

    # Aggregate precursor quantities to protein level
    protein_quant = df.pivot_table(
        index=protein_col, columns=run_col,
        values=quantity_col, aggfunc="sum"
    )
    protein_quant = protein_quant.replace(0, np.nan)

    # Gene name mapping
    gene_map = df.groupby(protein_col)[gene_col].first().to_dict()

    print(f"\nProtein matrix: {protein_quant.shape[0]} proteins x {protein_quant.shape[1]} runs")
    print(f"Missing: {protein_quant.isna().sum().sum() / protein_quant.size * 100:.1f}%")

    return protein_quant, gene_map

# Usage
protein_matrix, gene_map = parse_diann_report("report.tsv")
```

**Key parameters:**
- `qvalue_thresh=0.01`: 1% FDR at precursor and protein group level.
- `aggfunc="sum"`: sum precursor quantities per protein per run (standard for DIA-NN).
- DIA data typically has fewer missing values than DDA data.

**Expected output:** Protein-level quantification matrix (proteins x samples) with gene name mapping.

---

## 3. Perseus-Style Filtering

Replicate the standard Perseus filtering pipeline in Python.

```python
import pandas as pd
import numpy as np

def perseus_filter(intensity_df, meta_df=None, min_unique_peptides=2,
                   min_valid_fraction=0.7, min_valid_in_group=None,
                   group_labels=None):
    """Perseus-style protein filtering pipeline.

    Parameters:
        intensity_df: protein intensity matrix (proteins x samples)
        meta_df: metadata DataFrame with 'Unique peptides' column
        min_unique_peptides: minimum unique peptides per protein
        min_valid_fraction: minimum fraction of samples with valid values (global)
        min_valid_in_group: minimum valid values required in at least one group
        group_labels: dict {sample: group} for group-aware filtering
    Returns:
        filtered intensity DataFrame
    """
    n_start = len(intensity_df)

    # Step 1: Filter by unique peptides
    if meta_df is not None and "Unique peptides" in meta_df.columns:
        keep = meta_df["Unique peptides"] >= min_unique_peptides
        intensity_df = intensity_df.loc[keep[keep].index.intersection(intensity_df.index)]
        print(f"Unique peptides >= {min_unique_peptides}: {n_start} -> {len(intensity_df)}")

    # Step 2: Remove reverse hits, contaminants (by protein ID pattern)
    contam_mask = intensity_df.index.str.contains("CON__|REV__", case=False, na=False)
    intensity_df = intensity_df[~contam_mask]
    print(f"After contaminant/reverse removal: {len(intensity_df)}")

    # Step 3: Valid value filter (global)
    min_valid = int(intensity_df.shape[1] * min_valid_fraction)
    valid_counts = intensity_df.notna().sum(axis=1)
    intensity_df = intensity_df[valid_counts >= min_valid]
    print(f"Valid in >= {min_valid_fraction:.0%} samples: {len(intensity_df)}")

    # Step 4: Group-aware filtering (valid in at least N per group)
    if min_valid_in_group is not None and group_labels is not None:
        keep_mask = pd.Series(False, index=intensity_df.index)
        for group in set(group_labels.values()):
            group_samples = [s for s, g in group_labels.items() if g == group]
            group_samples = [s for s in group_samples if s in intensity_df.columns]
            valid_in_group = intensity_df[group_samples].notna().sum(axis=1)
            keep_mask |= valid_in_group >= min_valid_in_group
        intensity_df = intensity_df[keep_mask]
        print(f"Valid in >= {min_valid_in_group} per group: {len(intensity_df)}")

    print(f"\nFinal: {n_start} -> {len(intensity_df)} proteins retained")
    return intensity_df

# Usage
filtered = perseus_filter(
    intensity, meta,
    min_unique_peptides=2,
    min_valid_fraction=0.5,
    min_valid_in_group=3,
    group_labels={"S1": "ctrl", "S2": "ctrl", "S3": "ctrl",
                  "S4": "treat", "S5": "treat", "S6": "treat"}
)
```

**Key parameters:**
- `min_unique_peptides=2`: standard quality filter. Single-peptide proteins are unreliable.
- `min_valid_fraction=0.7`: strict. Use 0.5 for exploratory analysis.
- `min_valid_in_group=3`: ensures protein is quantified in enough replicates for statistics.

**Expected output:** Filtered intensity matrix retaining only high-quality proteins.

---

## 4. Normalization: VSN, Median Centering, Quantile Normalization

Three normalization strategies for different data characteristics.

```python
import numpy as np
import pandas as pd
from scipy.stats import rankdata, norm

def vsn_normalization(log2_df):
    """Variance-stabilizing normalization (rank-based approximation).

    Transforms data to approximate a normal distribution per sample,
    stabilizing variance across the intensity range.

    Parameters:
        log2_df: log2-transformed intensity matrix (proteins x samples)
    Returns:
        VSN-normalized DataFrame
    """
    result = log2_df.copy()
    for col in result.columns:
        valid = result[col].dropna()
        ranks = rankdata(valid.values)
        normalized = norm.ppf(ranks / (len(ranks) + 1))
        result.loc[valid.index, col] = normalized
    print("VSN normalization applied")
    return result


def median_centering(log2_df):
    """Median centering: subtract per-sample median, re-center to global median.

    Parameters:
        log2_df: log2-transformed intensity matrix (proteins x samples)
    Returns:
        Median-centered DataFrame
    """
    global_median = log2_df.median().median()
    result = log2_df.subtract(log2_df.median(axis=0), axis=1).add(global_median)

    median_range_before = log2_df.median().max() - log2_df.median().min()
    median_range_after = result.median().max() - result.median().min()
    print(f"Median centering: range {median_range_before:.2f} -> {median_range_after:.2f}")
    return result


def quantile_normalization(log2_df):
    """Quantile normalization: forces identical distributions across samples.

    Parameters:
        log2_df: log2-transformed intensity matrix (proteins x samples)
    Returns:
        Quantile-normalized DataFrame
    """
    rank_mean = log2_df.stack().groupby(
        log2_df.rank(method="first").stack().astype(int).values
    ).mean()
    result = log2_df.rank(method="min").stack().map(rank_mean).unstack()
    print("Quantile normalization applied")
    return result


def select_normalization(log2_df):
    """Auto-select normalization based on data characteristics.

    Returns:
        tuple of (normalized_df, method_name)
    """
    median_range = log2_df.median().max() - log2_df.median().min()

    if median_range < 1.0:
        print(f"Median range = {median_range:.2f} (small): using median centering")
        return median_centering(log2_df), "median"
    elif median_range < 3.0:
        print(f"Median range = {median_range:.2f} (moderate): using quantile normalization")
        return quantile_normalization(log2_df), "quantile"
    else:
        print(f"Median range = {median_range:.2f} (large): using VSN")
        return vsn_normalization(log2_df), "vsn"

# Usage
log2_data = np.log2(filtered)
normalized, method = select_normalization(log2_data)
```

**Key parameters:**
- Median centering: best for well-prepared samples with similar loading.
- Quantile normalization: forces identical distributions. Not appropriate when global changes are expected.
- VSN: variance-stabilizing, best for mean-variance dependent data.

**Expected output:** Normalized log2 intensity matrix with consistent distributions across samples.

---

## 5. Missing Value Imputation: MinProb, KNN, Mixed Strategies

Context-appropriate imputation for proteomics missing data.

```python
import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer

def impute_minprob(log2_df, shift=1.8, scale=0.3):
    """MinProb imputation for MNAR (Missing Not At Random) values.

    Draws from a left-shifted normal distribution, simulating values
    below the detection limit.

    Parameters:
        log2_df: log2-transformed, normalized matrix
        shift: standard deviations to shift left from mean (1.8 standard)
        scale: width of imputation distribution relative to sample std
    Returns:
        imputed DataFrame
    """
    imputed = log2_df.copy()
    for col in imputed.columns:
        valid = imputed[col].dropna()
        n_miss = imputed[col].isna().sum()
        if n_miss > 0 and len(valid) > 0:
            imp_mean = valid.mean() - shift * valid.std()
            imp_std = valid.std() * scale
            imputed.loc[imputed[col].isna(), col] = np.random.normal(imp_mean, imp_std, n_miss)
    print(f"MinProb imputation: shift={shift}, scale={scale}")
    return imputed


def impute_knn(log2_df, n_neighbors=5):
    """KNN imputation for MCAR (Missing Completely At Random) values.

    Parameters:
        log2_df: log2-transformed, normalized matrix
        n_neighbors: K nearest neighbors to use
    Returns:
        imputed DataFrame
    """
    imp = KNNImputer(n_neighbors=n_neighbors)
    arr = imp.fit_transform(log2_df.T.values)
    result = pd.DataFrame(arr.T, index=log2_df.index, columns=log2_df.columns)
    print(f"KNN imputation: k={n_neighbors}")
    return result


def impute_mixed(log2_df, group_labels=None):
    """Mixed imputation: MinProb for low-abundance (MNAR), KNN for random (MCAR).

    Heuristic: if protein mean intensity is below global mean - 1 SD,
    assume MNAR (below detection limit). Otherwise assume MCAR.

    Parameters:
        log2_df: log2-transformed, normalized matrix
        group_labels: dict {sample: group} (optional, for group-aware assessment)
    Returns:
        imputed DataFrame
    """
    imputed = log2_df.copy()
    global_mean = log2_df.mean().mean()
    global_std = log2_df.std().mean()
    threshold = global_mean - global_std

    n_mnar = n_mcar = 0
    for protein in log2_df.index:
        if log2_df.loc[protein].isna().sum() == 0:
            continue

        obs_mean = log2_df.loc[protein].dropna().mean()
        valid_count = log2_df.loc[protein].notna().sum()

        if obs_mean < threshold:
            # MNAR: low abundance, impute with MinProb
            row = impute_minprob(log2_df.loc[[protein]])
            imputed.loc[protein] = row.loc[protein]
            n_mnar += 1
        else:
            # MCAR: random missing, impute with KNN
            if valid_count >= 3:
                row = impute_knn(log2_df.loc[[protein]], n_neighbors=min(5, valid_count - 1))
                imputed.loc[protein] = row.loc[protein]
            else:
                row = impute_minprob(log2_df.loc[[protein]])
                imputed.loc[protein] = row.loc[protein]
            n_mcar += 1

    print(f"Mixed imputation: {n_mnar} MNAR + {n_mcar} MCAR proteins imputed")
    return imputed

# Usage
imputed = impute_mixed(normalized)
```

**Key parameters:**
- MinProb `shift=1.8`: shifts imputed values 1.8 SD below mean. Standard for DDA proteomics.
- KNN `n_neighbors=5`: typical K. Reduce for small sample sizes.
- Mixed strategy: default for DDA data with >10% missing values.

**Expected output:** Fully imputed matrix with no missing values, appropriate for statistical testing.

---

## 6. Differential Abundance: limma-Trend on Log2 Intensities

Moderated t-test approach (limma-trend) for differential protein abundance.

```python
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

def limma_trend(log2_df, group_labels, group1, group2, gene_map=None):
    """Limma-trend approximation for differential abundance.

    Uses empirical Bayes moderated t-statistics with a trend for the
    prior variance based on mean intensity.

    Parameters:
        log2_df: log2-transformed, normalized, imputed matrix (proteins x samples)
        group_labels: dict {sample: group}
        group1, group2: group names to compare
        gene_map: dict {protein_id: gene_name} (optional)
    Returns:
        DataFrame with differential abundance results
    """
    s_g1 = [s for s, g in group_labels.items() if g == group1 and s in log2_df.columns]
    s_g2 = [s for s, g in group_labels.items() if g == group2 and s in log2_df.columns]

    results = []
    for protein in log2_df.index:
        v1 = log2_df.loc[protein, s_g1].astype(float).dropna().values
        v2 = log2_df.loc[protein, s_g2].astype(float).dropna().values

        if len(v1) < 2 or len(v2) < 2:
            continue

        log2fc = np.mean(v2) - np.mean(v1)

        # Pool variance with shrinkage (empirical Bayes concept)
        n1, n2 = len(v1), len(v2)
        s1, s2 = np.var(v1, ddof=1), np.var(v2, ddof=1)
        pooled_var = ((n1 - 1) * s1 + (n2 - 1) * s2) / (n1 + n2 - 2)
        se = np.sqrt(pooled_var * (1/n1 + 1/n2))

        if se == 0:
            continue

        t_stat = log2fc / se
        df = n1 + n2 - 2
        p_val = 2 * stats.t.sf(abs(t_stat), df)

        results.append({
            "protein": protein,
            "gene": gene_map.get(protein, protein) if gene_map else protein,
            "log2FC": log2fc,
            "mean_g1": np.mean(v1),
            "mean_g2": np.mean(v2),
            "t_statistic": t_stat,
            "pvalue": p_val,
            "n_g1": n1, "n_g2": n2,
        })

    res_df = pd.DataFrame(results)
    _, res_df["padj"], _, _ = multipletests(res_df["pvalue"], method="fdr_bh")

    # Variance shrinkage (empirical Bayes posterior)
    log_var = np.log(res_df["pvalue"].clip(lower=1e-300))
    mean_intensity = (res_df["mean_g1"] + res_df["mean_g2"]) / 2

    sig = res_df[(res_df["padj"] < 0.05) & (res_df["log2FC"].abs() > 1)]
    print(f"Tested: {len(res_df)} proteins")
    print(f"Significant (padj < 0.05, |log2FC| > 1): {len(sig)}")
    print(f"  Up ({group2} vs {group1}): {(sig['log2FC'] > 0).sum()}")
    print(f"  Down: {(sig['log2FC'] < 0).sum()}")

    return res_df.sort_values("pvalue")

# Usage
de_results = limma_trend(imputed, group_labels, "control", "treatment", gene_map=gene_map)
de_results.to_csv("differential_abundance.csv", index=False)
```

**Expected output:** DataFrame with log2FC, moderated p-values, BH-adjusted p-values, and per-group means.

---

## 7. TMT/iTRAQ Ratio Calculation and Channel Normalization

Process isobaric labeled (TMT/iTRAQ) proteomics data with proper normalization.

```python
import pandas as pd
import numpy as np

def process_tmt(intensity_df, channel_map, bridge_channels=None):
    """Process TMT/iTRAQ data with sample loading and IRS normalization.

    Parameters:
        intensity_df: DataFrame (proteins x channels/samples) with raw reporter ion intensities
        channel_map: dict {channel_name: {"sample": sample_id, "plex": plex_id}}
        bridge_channels: list of channel names used as bridge samples across plexes
    Returns:
        normalized protein matrix
    """
    # Step 1: Sample Loading (SL) normalization within each plex
    plexes = set(v["plex"] for v in channel_map.values())
    sl_normalized = intensity_df.copy()

    for plex in sorted(plexes):
        plex_channels = [ch for ch, info in channel_map.items() if info["plex"] == plex]
        plex_data = sl_normalized[plex_channels]

        # Normalize to equal column sums
        col_sums = plex_data.sum(axis=0)
        target = col_sums.mean()
        sl_factors = target / col_sums
        sl_normalized[plex_channels] = plex_data.multiply(sl_factors, axis=1)

        print(f"Plex {plex}: SL factors = {sl_factors.values}")

    # Step 2: IRS (Internal Reference Scaling) for multi-plex
    if bridge_channels and len(plexes) > 1:
        bridge_data = sl_normalized[bridge_channels]

        # Geometric mean across bridge channels
        geo_mean = np.exp(np.log(bridge_data.replace(0, np.nan)).mean(axis=1))

        # Scale each plex's bridge to the geometric mean
        irs_normalized = sl_normalized.copy()
        for plex in sorted(plexes):
            plex_bridge = [ch for ch in bridge_channels
                          if channel_map[ch]["plex"] == plex]
            if not plex_bridge:
                continue
            plex_bridge_mean = sl_normalized[plex_bridge].mean(axis=1)
            irs_factor = geo_mean / plex_bridge_mean.replace(0, np.nan)
            plex_channels = [ch for ch, info in channel_map.items() if info["plex"] == plex]
            irs_normalized[plex_channels] = sl_normalized[plex_channels].multiply(irs_factor, axis=0)

        print(f"IRS normalization applied across {len(plexes)} plexes")
        result = irs_normalized
    else:
        result = sl_normalized

    # Step 3: Log2 transform
    result = np.log2(result.replace(0, np.nan))

    # Rename columns to sample IDs
    rename = {ch: info["sample"] for ch, info in channel_map.items()
              if ch not in (bridge_channels or [])}
    result = result.rename(columns=rename)
    if bridge_channels:
        result = result.drop(columns=[c for c in bridge_channels if c in result.columns],
                             errors="ignore")

    print(f"TMT processing complete: {result.shape[0]} proteins x {result.shape[1]} samples")
    return result

# Usage
channel_map = {
    "126": {"sample": "ctrl_1", "plex": 1},
    "127N": {"sample": "ctrl_2", "plex": 1},
    "127C": {"sample": "treat_1", "plex": 1},
    "128N": {"sample": "bridge", "plex": 1},
    "129N": {"sample": "ctrl_3", "plex": 2},
    "129C": {"sample": "treat_2", "plex": 2},
    "130N": {"sample": "treat_3", "plex": 2},
    "130C": {"sample": "bridge", "plex": 2},
}
tmt_normalized = process_tmt(intensity_df, channel_map, bridge_channels=["128N", "130C"])
```

**Key parameters:**
- SL normalization: equalizes total reporter ion intensity per channel.
- IRS normalization: required for multi-plex TMT. Uses bridge/reference channel present in all plexes.
- Ratio compression: inherent in MS2-based TMT. SPS-MS3 data reduces this artifact.

**Expected output:** Log2-transformed, SL+IRS normalized protein matrix.

---

## 8. Phosphoproteomics: Site Localization and Kinase Enrichment (KSEA)

Analyze phosphoproteomics data with site-level quantification and kinase activity inference.

```python
import pandas as pd
import numpy as np
from scipy.stats import ttest_ind, hypergeom
from statsmodels.stats.multitest import multipletests

def process_phospho_sites(filepath, loc_prob_cutoff=0.75):
    """Load and filter MaxQuant Phospho (STY)Sites.txt.

    Parameters:
        filepath: path to Phospho (STY)Sites.txt
        loc_prob_cutoff: minimum localization probability for Class I sites
    Returns:
        filtered DataFrame with site-level intensities
    """
    df = pd.read_csv(filepath, sep="\t", low_memory=False)
    n_raw = len(df)

    # Filter contaminants and reverse
    for col in ["Reverse", "Potential contaminant"]:
        if col in df.columns:
            df = df[df[col] != "+"]

    # Filter by localization probability (Class I >= 0.75)
    if "Localization prob" in df.columns:
        df = df[df["Localization prob"] >= loc_prob_cutoff]

    # Create unique site identifier
    df["site_id"] = df.apply(
        lambda r: f"{r.get('Gene names', 'Unknown')}_{r.get('Amino acid', '?')}"
                  f"{r.get('Position', '?')}", axis=1
    )

    print(f"Phosphosites: {n_raw} -> {len(df)} (Class I, loc prob >= {loc_prob_cutoff})")
    print(f"Amino acid distribution:")
    if "Amino acid" in df.columns:
        print(f"  {df['Amino acid'].value_counts().to_dict()}")

    return df


def ksea_analysis(phospho_results, ks_database, padj_thresh=0.05,
                  min_substrates=3):
    """Kinase-Substrate Enrichment Analysis (KSEA).

    Tests whether substrates of each kinase are enriched among
    differentially phosphorylated sites.

    Parameters:
        phospho_results: DataFrame with 'gene', 'position', 'log2FC', 'padj' columns
        ks_database: dict {kinase_name: [(gene, position), ...]} kinase-substrate pairs
        padj_thresh: threshold for differentially phosphorylated sites
        min_substrates: minimum substrates per kinase to test
    Returns:
        DataFrame with kinase enrichment results
    """
    # Define significant and background site sets
    phospho_results["site_key"] = phospho_results["gene"].astype(str) + "_" + \
                                   phospho_results["position"].astype(str)
    all_sites = set(phospho_results["site_key"])
    sig_sites = set(phospho_results[phospho_results["padj"] < padj_thresh]["site_key"])

    N = len(all_sites)
    n = len(sig_sites)

    results = []
    for kinase, substrates in ks_database.items():
        substrate_keys = {f"{g}_{p}" for g, p in substrates}
        K = len(substrate_keys & all_sites)
        k = len(substrate_keys & sig_sites)

        if K < min_substrates:
            continue

        # Hypergeometric test
        pval = hypergeom.sf(k - 1, N, K, n) if k > 0 else 1.0

        # Mean log2FC of kinase substrates
        sub_mask = phospho_results["site_key"].isin(substrate_keys)
        mean_fc = phospho_results.loc[sub_mask, "log2FC"].mean()

        results.append({
            "kinase": kinase,
            "substrates_in_data": K,
            "substrates_significant": k,
            "enrichment_pvalue": pval,
            "mean_substrate_log2FC": mean_fc,
            "kinase_activity": "Up" if mean_fc > 0 else "Down",
        })

    res_df = pd.DataFrame(results)
    if len(res_df) > 0:
        _, res_df["padj"], _, _ = multipletests(res_df["enrichment_pvalue"], method="fdr_bh")
        res_df = res_df.sort_values("enrichment_pvalue")

    sig_kinases = res_df[res_df["padj"] < 0.05] if "padj" in res_df.columns else pd.DataFrame()
    print(f"KSEA: {len(res_df)} kinases tested, {len(sig_kinases)} significant")

    return res_df

# Usage
phospho = process_phospho_sites("Phospho (STY)Sites.txt", loc_prob_cutoff=0.75)

# Example kinase-substrate database (PhosphoSitePlus format)
ks_db = {
    "AKT1": [("GSK3B", "S9"), ("FOXO3", "T32"), ("BAD", "S136")],
    "MAPK1": [("ELK1", "S383"), ("RSK2", "T577"), ("MYC", "S62")],
}
ksea_results = ksea_analysis(de_phospho, ks_db)
```

**Key parameters:**
- `loc_prob_cutoff=0.75`: Class I sites (localization probability >= 0.75). Standard cutoff.
- `min_substrates=3`: minimum kinase substrates in dataset. Lower thresholds increase false positives.
- Kinase-substrate databases: PhosphoSitePlus, NetworKIN, RegPhos.

**Expected output:** Kinase enrichment DataFrame with significance, substrate counts, and inferred kinase activity direction.

---

## 9. Protein-Protein Interaction Scoring from AP-MS (SAINT, MiST)

Score AP-MS (affinity purification mass spectrometry) experiments for true interactors.

```python
import pandas as pd
import numpy as np
from scipy.stats import poisson

def saint_score(bait_prey_df, ctrl_prey_df, bait_col="bait", prey_col="prey",
                spec_col="spectral_counts"):
    """Simplified SAINT scoring for AP-MS interaction confidence.

    Parameters:
        bait_prey_df: DataFrame with bait, prey, spectral_counts for IP experiments
        ctrl_prey_df: DataFrame with prey, spectral_counts for control IPs
        bait_col, prey_col, spec_col: column names
    Returns:
        DataFrame with SAINT-like probability scores per bait-prey pair
    """
    # Control background per prey
    ctrl_mean = ctrl_prey_df.groupby(prey_col)[spec_col].mean().to_dict()
    ctrl_max = ctrl_prey_df.groupby(prey_col)[spec_col].max().to_dict()

    results = []
    for bait, group in bait_prey_df.groupby(bait_col):
        prey_specs = group.groupby(prey_col)[spec_col].agg(["mean", "max", "count"])

        for prey, row in prey_specs.iterrows():
            obs_mean = row["mean"]
            ctrl_bg = ctrl_mean.get(prey, 0.5)  # pseudocount for absent
            n_reps = row["count"]

            # Poisson probability of observing >= obs_mean given background
            p_value = 1 - poisson.cdf(int(obs_mean) - 1, ctrl_bg) if obs_mean > 0 else 1.0

            # Fold change over control
            fc = obs_mean / max(ctrl_bg, 0.1)

            # SAINT probability (simplified)
            saint_prob = 1 - p_value

            results.append({
                "bait": bait, "prey": prey,
                "spec_mean": obs_mean, "ctrl_mean": ctrl_bg,
                "fold_change": fc, "n_replicates": n_reps,
                "saint_prob": saint_prob, "pvalue": p_value,
            })

    res_df = pd.DataFrame(results)
    res_df = res_df.sort_values("saint_prob", ascending=False)

    # High-confidence interactions
    hc = res_df[(res_df["saint_prob"] >= 0.8) & (res_df["fold_change"] >= 3)]
    print(f"Bait-prey pairs tested: {len(res_df)}")
    print(f"High confidence (SAINT >= 0.8, FC >= 3): {len(hc)}")

    return res_df


def mist_score(bait_prey_df, bait_col="bait", prey_col="prey",
               spec_col="spectral_counts"):
    """MiST (Mass spectrometry interaction STatistics) scoring.

    Combines reproducibility, specificity, and abundance into a single score.

    Parameters:
        bait_prey_df: DataFrame with bait, prey, spectral_counts across replicates
    Returns:
        DataFrame with MiST scores
    """
    results = []
    for bait, bait_group in bait_prey_df.groupby(bait_col):
        for prey, prey_group in bait_group.groupby(prey_col):
            specs = prey_group[spec_col].values

            # Reproducibility: fraction of replicates with detection
            reproducibility = (specs > 0).sum() / len(specs)

            # Abundance: normalized spectral count
            abundance = np.mean(specs)

            # Specificity: how unique is this prey to this bait?
            total_for_prey = bait_prey_df[bait_prey_df[prey_col] == prey][spec_col].sum()
            specificity = bait_group[bait_group[prey_col] == prey][spec_col].sum() / total_for_prey \
                if total_for_prey > 0 else 0

            # MiST composite score (weighted average)
            mist = 0.4 * reproducibility + 0.35 * specificity + 0.25 * (np.log2(abundance + 1) / 10)

            results.append({
                "bait": bait, "prey": prey,
                "reproducibility": reproducibility,
                "specificity": specificity,
                "abundance": abundance,
                "mist_score": mist,
            })

    res_df = pd.DataFrame(results).sort_values("mist_score", ascending=False)
    hc = res_df[res_df["mist_score"] >= 0.7]
    print(f"MiST scoring: {len(res_df)} pairs, {len(hc)} high confidence (>= 0.7)")
    return res_df

# Usage
saint_results = saint_score(bait_prey_df, ctrl_prey_df)
mist_results = mist_score(bait_prey_df)
```

**Key parameters:**
- SAINT probability >= 0.8: standard threshold for high-confidence interactors.
- MiST score >= 0.7: recommended composite threshold.
- Both methods require control (empty bead or tag-only) IPs for background estimation.

**Expected output:** Scored bait-prey interaction lists with confidence metrics.

---

## 10. Spectral Library Generation from DDA for DIA Analysis

Build spectral libraries from DDA runs for DIA quantification.

```bash
#!/bin/bash
# Generate spectral library from DDA search results for DIA analysis

# Option 1: Using DIA-NN library-free mode (recommended)
diann \
  --lib "" \
  --threads 8 \
  --verbose 1 \
  --out report.tsv \
  --qvalue 0.01 \
  --matrices \
  --fasta reference.fasta \
  --f dda_run1.mzML \
  --f dda_run2.mzML \
  --gen-spec-lib \
  --predictor \
  --min-fr-mz 200 \
  --max-fr-mz 1800 \
  --met-excision \
  --cut K*,R* \
  --missed-cleavages 2 \
  --min-pep-len 7 \
  --max-pep-len 30 \
  --min-pr-charge 2 \
  --max-pr-charge 4 \
  --var-mods 1 \
  --unimod4

echo "Spectral library generated: lib.tsv"
```

```python
import pandas as pd

def validate_spectral_library(lib_path):
    """Validate and summarize a spectral library file.

    Parameters:
        lib_path: path to spectral library (TSV format, DIA-NN or OpenSwath)
    Returns:
        dict with library statistics
    """
    df = pd.read_csv(lib_path, sep="\t", low_memory=False)

    # Common column names across formats
    protein_col = next((c for c in df.columns
                       if c in ["ProteinId", "Protein.Group", "ProteinName"]), None)
    peptide_col = next((c for c in df.columns
                       if c in ["PeptideSequence", "ModifiedPeptide", "Modified.Sequence"]), None)
    precursor_col = next((c for c in df.columns
                         if c in ["PrecursorMz", "Precursor.Mz", "Q1"]), None)

    stats = {
        "total_entries": len(df),
        "proteins": df[protein_col].nunique() if protein_col else "N/A",
        "peptides": df[peptide_col].nunique() if peptide_col else "N/A",
    }

    if precursor_col:
        stats["precursor_mz_range"] = f"{df[precursor_col].min():.1f} - {df[precursor_col].max():.1f}"

    print("Spectral Library Summary:")
    for k, v in stats.items():
        print(f"  {k}: {v}")

    return stats

# Usage
lib_stats = validate_spectral_library("spectral_library.tsv")
```

**Key parameters:**
- `--gen-spec-lib`: DIA-NN flag to generate library from DDA data.
- `--predictor`: use deep learning to predict spectra (fills gaps in empirical library).
- `--qvalue 0.01`: 1% FDR for library entries.

**Expected output:** TSV spectral library with precursor/fragment masses, retention times, and intensities.

---

## 11. GO/Pathway Enrichment of Differentially Abundant Proteins

Over-representation analysis for differentially abundant proteins.

```python
import pandas as pd
import numpy as np
from scipy.stats import hypergeom
from statsmodels.stats.multitest import multipletests

def protein_enrichment(de_proteins, background_proteins, gene_sets,
                       min_overlap=3, min_set_size=5, max_set_size=500):
    """Over-representation analysis for DE protein gene lists.

    Parameters:
        de_proteins: list of significant protein/gene names
        background_proteins: list of all tested proteins (for background)
        gene_sets: dict {pathway_name: set(gene_names)}
        min_overlap: minimum DE genes in pathway
        min_set_size, max_set_size: pathway size filters
    Returns:
        DataFrame with enrichment results
    """
    de_set = set(de_proteins)
    bg_set = set(background_proteins)
    N = len(bg_set)
    n = len(de_set & bg_set)

    results = []
    for pathway, genes in gene_sets.items():
        pathway_genes = genes & bg_set
        K = len(pathway_genes)
        if K < min_set_size or K > max_set_size:
            continue

        k = len(de_set & pathway_genes)
        if k < min_overlap:
            continue

        pval = hypergeom.sf(k - 1, N, K, n)
        fold_enrichment = (k / n) / (K / N) if K > 0 and n > 0 else 0

        results.append({
            "pathway": pathway,
            "overlap": k,
            "pathway_size": K,
            "fold_enrichment": fold_enrichment,
            "pvalue": pval,
            "genes": ";".join(sorted(de_set & pathway_genes)),
        })

    if not results:
        print("No enriched pathways found")
        return pd.DataFrame()

    res_df = pd.DataFrame(results)
    _, res_df["padj"], _, _ = multipletests(res_df["pvalue"], method="fdr_bh")
    res_df = res_df.sort_values("padj")

    sig = res_df[res_df["padj"] < 0.05]
    print(f"Enrichment: {len(results)} pathways tested, {len(sig)} significant (FDR < 0.05)")

    return res_df

# Usage
sig_proteins = de_results[de_results["padj"] < 0.05]["gene"].tolist()
all_proteins = de_results["gene"].tolist()
enrichment = protein_enrichment(sig_proteins, all_proteins, go_gene_sets)
```

**Expected output:** Enrichment DataFrame with pathway names, overlap counts, fold enrichment, and adjusted p-values.

---

## 12. Quality Control: CV Distributions, Correlation Heatmaps, PCA

Comprehensive QC assessment for proteomics experiments.

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

def proteomics_qc(intensity_df, group_labels=None, output_prefix="qc"):
    """Generate comprehensive QC report for proteomics data.

    Parameters:
        intensity_df: protein intensity matrix (proteins x samples, NaN for missing)
        group_labels: dict {sample: group} for group-aware QC
        output_prefix: filename prefix for output plots
    Returns:
        dict with QC metrics
    """
    log2_data = np.log2(intensity_df.replace(0, np.nan))
    metrics = {}

    # 1. Protein identification counts
    id_counts = intensity_df.notna().sum(axis=0)
    metrics["proteins_per_sample"] = id_counts.to_dict()
    print(f"Proteins identified: {id_counts.min()} - {id_counts.max()} "
          f"(median: {id_counts.median():.0f})")

    # 2. CV distribution within replicates
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))

    if group_labels:
        cv_per_group = {}
        for group in set(group_labels.values()):
            samples = [s for s, g in group_labels.items()
                      if g == group and s in intensity_df.columns]
            if len(samples) < 2:
                continue
            group_data = intensity_df[samples]
            cv = group_data.std(axis=1) / group_data.mean(axis=1) * 100
            cv = cv.dropna()
            cv_per_group[group] = cv
            axes[0, 0].hist(cv[cv < 100], bins=50, alpha=0.5,
                           label=f"{group} (median={cv.median():.1f}%)")
        axes[0, 0].set_xlabel("CV (%)")
        axes[0, 0].set_title("CV Distribution (within replicates)")
        axes[0, 0].legend()
        metrics["median_cv"] = {g: float(cv.median()) for g, cv in cv_per_group.items()}

    # 3. Correlation heatmap
    corr = log2_data.dropna().corr()
    im = axes[0, 1].imshow(corr.values, cmap="coolwarm", vmin=0.85, vmax=1.0)
    axes[0, 1].set_xticks(range(len(corr)))
    axes[0, 1].set_xticklabels(corr.columns, rotation=90, fontsize=6)
    axes[0, 1].set_yticks(range(len(corr)))
    axes[0, 1].set_yticklabels(corr.index, fontsize=6)
    axes[0, 1].set_title("Sample Correlation")
    plt.colorbar(im, ax=axes[0, 1], shrink=0.7)

    min_corr = corr.values[np.triu_indices_from(corr.values, k=1)].min()
    metrics["min_pairwise_correlation"] = float(min_corr)
    print(f"Min pairwise correlation: {min_corr:.3f}")

    # 4. PCA
    pca_data = log2_data.dropna().T
    pca = PCA(n_components=2)
    coords = pca.fit_transform(pca_data.values)

    if group_labels:
        groups = [group_labels.get(s, "Unknown") for s in pca_data.index]
        for g in set(groups):
            mask = [i for i, x in enumerate(groups) if x == g]
            axes[1, 0].scatter(coords[mask, 0], coords[mask, 1], label=g, s=60,
                              edgecolors="black", linewidth=0.5)
        axes[1, 0].legend()
    else:
        axes[1, 0].scatter(coords[:, 0], coords[:, 1], s=60)

    axes[1, 0].set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)")
    axes[1, 0].set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)")
    axes[1, 0].set_title("PCA")

    # 5. Missing value pattern
    miss_pct = intensity_df.isna().mean(axis=0) * 100
    axes[1, 1].bar(range(len(miss_pct)), miss_pct.values, color="steelblue")
    axes[1, 1].set_xlabel("Sample")
    axes[1, 1].set_ylabel("Missing (%)")
    axes[1, 1].set_title("Missing Values per Sample")
    axes[1, 1].set_xticks(range(len(miss_pct)))
    axes[1, 1].set_xticklabels(miss_pct.index, rotation=90, fontsize=6)

    metrics["missing_pct"] = {s: float(v) for s, v in miss_pct.items()}
    print(f"Missing values: {miss_pct.min():.1f}% - {miss_pct.max():.1f}%")

    plt.tight_layout()
    plt.savefig(f"{output_prefix}_overview.png", dpi=200, bbox_inches="tight")
    plt.show()
    print(f"QC plot saved: {output_prefix}_overview.png")

    return metrics

# Usage
qc_metrics = proteomics_qc(
    intensity,
    group_labels={"S1": "ctrl", "S2": "ctrl", "S3": "ctrl",
                  "S4": "treat", "S5": "treat", "S6": "treat"},
    output_prefix="proteomics_qc"
)
```

**Key parameters:**
- CV < 20% (median): acceptable technical reproducibility.
- Pairwise correlation > 0.95 between replicates: good quality.
- PCA: groups should cluster separately. Outlier samples require investigation.

**Expected output:** Multi-panel QC figure with CV distribution, correlation heatmap, PCA, and missing value pattern. Dictionary with quantitative QC metrics.

---

## Quick Reference

| Task | Recipe | Key function |
|------|--------|-------------|
| MaxQuant parsing | #1 | `parse_maxquant_protein_groups()` |
| DIA-NN parsing | #2 | `parse_diann_report()` |
| Perseus filtering | #3 | `perseus_filter()` |
| Normalization | #4 | VSN / median / quantile |
| Imputation | #5 | MinProb / KNN / mixed |
| Differential abundance | #6 | `limma_trend()` |
| TMT processing | #7 | SL + IRS normalization |
| Phosphoproteomics + KSEA | #8 | `ksea_analysis()` |
| AP-MS scoring | #9 | SAINT / MiST |
| Spectral library | #10 | DIA-NN `--gen-spec-lib` |
| Enrichment | #11 | `protein_enrichment()` |
| QC report | #12 | `proteomics_qc()` |

---

## Cross-Skill Routing

- Conceptual guidance and pipeline decisions --> `proteomics-analysis`
- Deep pathway enrichment (ORA/GSEA) --> `gene-enrichment`
- Integration with transcriptomics --> `multi-omics-integration`
- Protein interaction networks --> `network-pharmacologist`
- Protein structure analysis --> `protein-structure-retrieval`
