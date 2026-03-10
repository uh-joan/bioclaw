# Mass Spectrometry & Spectral Matching Recipes

Code templates for LC-MS/MS data processing, spectral matching, molecular networking, and metabolite identification in metabolomics.

Cross-skill routing: use `systems-biology` for metabolic network integration, `gene-enrichment` for pathway enrichment of metabolite-associated genes.

---

## 1. XCMS Peak Picking: CentWave Parameters

Detect chromatographic peaks from raw LC-MS data using the CentWave algorithm.

```R
library(xcms)
library(MSnbase)

# ---- Load raw data ----
raw_files <- list.files("mzML/", pattern = "\\.mzML$", full.names = TRUE)
raw_data <- readMSData(raw_files, mode = "onDisk")
cat("Loaded", length(raw_files), "files\n")
cat("Scans:", length(raw_data), "\n")

# ---- CentWave peak detection ----
# Key parameters - adjust for your chromatography:
cwp <- CentWaveParam(
    ppm           = 10,       # Mass accuracy (5 for Orbitrap, 10-15 for QTOF)
    peakwidth     = c(5, 30), # Min/max peak width in seconds
                               # UHPLC: c(2, 20), HPLC: c(10, 60)
    snthresh      = 5,        # Signal-to-noise threshold (3-10)
    prefilter     = c(3, 100),# Min scans and min intensity for ROI detection
    mzdiff        = 0.01,     # Min m/z difference for overlapping peaks
    noise         = 100,      # Absolute noise cutoff
    integrate     = 1,        # Integration method: 1 = Mexican hat, 2 = descent
    mzCenterFun   = "wMean",  # m/z center method: wMean, mean, apex, wMeanApex3
    fitgauss      = FALSE     # Fit Gaussian to each peak (slower but more accurate)
)

# Run peak detection
xdata <- findChromPeaks(raw_data, param = cwp)

cat("Peaks detected:", nrow(chromPeaks(xdata)), "\n")
cat("Peaks per sample:", table(chromPeaks(xdata)[, "sample"]), "\n")

# ---- Quick diagnostic: peak width distribution ----
peaks <- as.data.frame(chromPeaks(xdata))
cat("\nPeak width (seconds):\n")
cat("  Median:", median(peaks$rtmax - peaks$rtmin), "\n")
cat("  Mean:", mean(peaks$rtmax - peaks$rtmin), "\n")
cat("  Range:", range(peaks$rtmax - peaks$rtmin), "\n")

# ---- Parameter optimization hint ----
# If too few peaks: decrease snthresh (3), widen peakwidth, decrease noise
# If too many peaks: increase snthresh (10), narrow peakwidth, increase noise
# Check EIC plots for representative features to validate parameters
```

**Key parameters**: `ppm` depends on instrument (5 for Orbitrap, 10-15 for QTOF, 20-25 for TOF). `peakwidth` must match your chromatography: UHPLC peaks are 2-20s, standard HPLC are 10-60s. `snthresh` of 5 is a good starting point; lower catches more low-abundance features but increases noise.

---

## 2. XCMS Grouping and Retention Time Correction

Align features across samples and correct retention time drift.

```R
library(xcms)

# ---- Retention time correction (Obiwarp) ----
# Obiwarp uses dynamic time warping on TIC profiles
owp <- ObiwarpParam(
    binSize    = 0.5,        # m/z bin size for TIC profile
    response   = 1,          # Flexibility (0 = rigid, 100 = very flexible)
    distFun    = "cor_opt",  # Distance function: cor, cor_opt, cov, euc
    gapInit    = 0.3,        # Initial gap penalty
    gapExtend  = 2.4         # Gap extension penalty
)

xdata <- adjustRtime(xdata, param = owp)

# Check RT correction
plotAdjustedRtime(xdata)
# Deviations should be < 5-10 seconds for good correction

# ---- Feature grouping (correspondence) ----
# Peak Density method groups peaks across samples
pdp <- PeakDensityParam(
    sampleGroups = xdata$sample_group,  # Sample group labels from phenodata
    bw           = 5,      # RT bandwidth for grouping (seconds)
                            # Should be ~1/3 of typical peak width
    minFraction  = 0.5,    # Min fraction of samples in a group with a peak
    minSamples   = 1,      # Min number of samples with peak
    binSize      = 0.01    # m/z bin size for density estimation
)

xdata <- groupChromPeaks(xdata, param = pdp)
cat("Features after grouping:", nrow(featureDefinitions(xdata)), "\n")

# ---- Fill missing peaks ----
# Re-integrate missing peaks at expected RT/m/z positions
xdata <- fillChromPeaks(xdata, param = ChromPeakAreaParam())
cat("Features after gap-filling:", nrow(featureDefinitions(xdata)), "\n")

# ---- Extract feature table ----
feature_table <- featureValues(xdata, value = "into", method = "maxint")
feature_defs <- featureDefinitions(xdata)

# Combine into annotated feature table
result <- cbind(
    mz = feature_defs$mzmed,
    rt = feature_defs$rtmed,
    as.data.frame(feature_table)
)
write.csv(result, "xcms_feature_table.csv")
cat("Final feature table:", nrow(result), "features x", ncol(feature_table), "samples\n")
```

**Expected output**: An aligned feature table with m/z, RT, and intensity per sample. RT correction should show small, smooth adjustments (< 10s). `minFraction=0.5` means a feature must appear in at least half the samples within a group.

---

## 3. MS/MS Spectral Matching with matchms (Python)

Match experimental MS2 spectra against reference libraries.

```python
from matchms import Spectrum, calculate_scores
from matchms.similarity import CosineGreedy, ModifiedCosine
from matchms.importing import load_from_mgf, load_from_msp
from matchms.filtering import (default_filters, normalize_intensities,
                                 select_by_mz, select_by_relative_intensity,
                                 add_precursor_mz, add_losses)
import numpy as np
import pandas as pd

def load_and_filter_spectra(filepath, min_mz=50, max_mz=2000, min_peaks=5):
    """Load and clean MS2 spectra from MGF or MSP file.

    Parameters
    ----------
    filepath : str
        Path to .mgf or .msp spectral file.
    min_mz, max_mz : float
        m/z range filter.
    min_peaks : int
        Minimum number of peaks per spectrum.

    Returns
    -------
    list of matchms.Spectrum objects.
    """
    if filepath.endswith(".mgf"):
        spectra = list(load_from_mgf(filepath))
    elif filepath.endswith(".msp"):
        spectra = list(load_from_msp(filepath))
    else:
        raise ValueError(f"Unsupported format: {filepath}")

    # Apply standard filters
    filtered = []
    for s in spectra:
        s = default_filters(s)
        s = normalize_intensities(s)
        s = select_by_mz(s, mz_from=min_mz, mz_to=max_mz)
        s = select_by_relative_intensity(s, intensity_from=0.01)
        if s is not None and len(s.peaks.mz) >= min_peaks:
            filtered.append(s)

    print(f"Loaded {len(spectra)} spectra, {len(filtered)} passed filters")
    return filtered

def match_spectra(query_spectra, reference_spectra, method="modified_cosine",
                   tolerance=0.01, min_score=0.6, min_matched_peaks=4):
    """Match query spectra against a reference library.

    Parameters
    ----------
    query_spectra : list of Spectrum
        Experimental MS2 spectra.
    reference_spectra : list of Spectrum
        Reference library spectra.
    method : str
        'cosine' or 'modified_cosine'. Modified cosine accounts for precursor mass shifts.
    tolerance : float
        m/z tolerance for peak matching (Da).
    min_score : float
        Minimum similarity score to report (0-1).
    min_matched_peaks : int
        Minimum number of matched peaks between query and reference.

    Returns
    -------
    pd.DataFrame with matches, scores, and metadata.
    """
    if method == "modified_cosine":
        similarity = ModifiedCosine(tolerance=tolerance)
    else:
        similarity = CosineGreedy(tolerance=tolerance)

    scores = calculate_scores(reference_spectra, query_spectra, similarity,
                               is_symmetric=False)

    matches = []
    for i_query in range(len(query_spectra)):
        best_score = 0
        best_ref = None
        best_matched = 0

        for i_ref in range(len(reference_spectra)):
            score_tuple = scores.scores[i_ref][i_query]
            if isinstance(score_tuple, tuple):
                score_val, n_matched = score_tuple
            else:
                score_val = float(score_tuple)
                n_matched = 0

            if score_val > best_score and n_matched >= min_matched_peaks:
                best_score = score_val
                best_ref = i_ref
                best_matched = n_matched

        query_meta = query_spectra[i_query].metadata
        if best_score >= min_score and best_ref is not None:
            ref_meta = reference_spectra[best_ref].metadata
            matches.append({
                "query_id": query_meta.get("feature_id", f"query_{i_query}"),
                "query_precursor_mz": query_meta.get("precursor_mz", np.nan),
                "match_name": ref_meta.get("name", "Unknown"),
                "match_formula": ref_meta.get("formula", ""),
                "match_inchikey": ref_meta.get("inchikey", ""),
                "cosine_score": round(best_score, 4),
                "matched_peaks": best_matched,
                "msi_level": 2 if best_score >= 0.7 else 3,
            })
        else:
            matches.append({
                "query_id": query_meta.get("feature_id", f"query_{i_query}"),
                "query_precursor_mz": query_meta.get("precursor_mz", np.nan),
                "match_name": "No match",
                "cosine_score": best_score,
                "matched_peaks": best_matched,
                "msi_level": 4,
            })

    df = pd.DataFrame(matches)
    n_matched = (df["msi_level"] <= 3).sum()
    print(f"Matched: {n_matched}/{len(df)} spectra")
    print(f"  MSI Level 2 (score >= 0.7): {(df['msi_level'] == 2).sum()}")
    print(f"  MSI Level 3 (score 0.6-0.7): {(df['msi_level'] == 3).sum()}")
    print(f"  Unmatched (Level 4): {(df['msi_level'] == 4).sum()}")
    return df

# Usage
queries = load_and_filter_spectra("experimental_ms2.mgf")
library = load_and_filter_spectra("gnps_library.mgf")
results = match_spectra(queries, library, method="modified_cosine", min_score=0.6)
results.to_csv("spectral_matches.csv", index=False)
```

**Key parameters**: Modified cosine is preferred over standard cosine as it accounts for precursor mass differences (e.g., adducts). `tolerance=0.01` Da works for high-resolution data; use 0.05 for lower resolution. A cosine score >= 0.7 is considered a reliable match (MSI Level 2).

---

## 4. Cosine Similarity Scoring for Spectral Comparison

Low-level implementation for custom spectral similarity calculations.

```python
import numpy as np
from scipy.spatial.distance import cosine as cosine_distance

def spectral_cosine_similarity(spec1_mz, spec1_int, spec2_mz, spec2_int,
                                 mz_tolerance=0.01, min_matched=3):
    """Compute cosine similarity between two MS2 spectra.

    Parameters
    ----------
    spec1_mz, spec1_int : array-like
        m/z and intensity arrays for spectrum 1.
    spec2_mz, spec2_int : array-like
        m/z and intensity arrays for spectrum 2.
    mz_tolerance : float
        Maximum m/z difference for peak matching (Da).
    min_matched : int
        Minimum matched peaks to return a valid score.

    Returns
    -------
    dict with score, n_matched, matched_peaks.
    """
    mz1, int1 = np.array(spec1_mz), np.array(spec1_int, dtype=float)
    mz2, int2 = np.array(spec2_mz), np.array(spec2_int, dtype=float)

    # Normalize to unit vector
    int1 = int1 / np.linalg.norm(int1) if np.linalg.norm(int1) > 0 else int1
    int2 = int2 / np.linalg.norm(int2) if np.linalg.norm(int2) > 0 else int2

    # Greedy peak matching
    used2 = set()
    matched = []
    dot_product = 0.0

    # Sort by intensity (match strongest peaks first)
    order1 = np.argsort(-int1)
    for i in order1:
        best_j, best_diff = None, mz_tolerance + 1
        for j in range(len(mz2)):
            if j in used2:
                continue
            diff = abs(mz1[i] - mz2[j])
            if diff < best_diff:
                best_diff = diff
                best_j = j
        if best_j is not None and best_diff <= mz_tolerance:
            used2.add(best_j)
            dot_product += int1[i] * int2[best_j]
            matched.append((mz1[i], mz2[best_j], int1[i], int2[best_j]))

    result = {
        "score": dot_product if len(matched) >= min_matched else 0.0,
        "n_matched": len(matched),
        "n_peaks_spec1": len(mz1),
        "n_peaks_spec2": len(mz2),
        "matched_peaks": matched,
    }
    return result

# Usage
score = spectral_cosine_similarity(
    spec1_mz=[85.03, 127.04, 145.05, 163.06],
    spec1_int=[100, 50, 80, 30],
    spec2_mz=[85.03, 127.04, 145.05, 181.07],
    spec2_int=[90, 60, 75, 25],
    mz_tolerance=0.02,
)
print(f"Cosine score: {score['score']:.4f}")
print(f"Matched peaks: {score['n_matched']}")

# ---- Entropy-based similarity (more robust for noisy spectra) ----
def spectral_entropy_similarity(mz1, int1, mz2, int2, mz_tolerance=0.01):
    """Spectral entropy similarity (Li et al., 2021)."""
    try:
        import ms_entropy
        spec1 = np.column_stack([mz1, int1])
        spec2 = np.column_stack([mz2, int2])
        score = ms_entropy.calculate_entropy_similarity(spec1, spec2, ms2_tolerance_in_da=mz_tolerance)
        return score
    except ImportError:
        print("Install ms_entropy: pip install ms_entropy")
        return None
```

**Expected output**: Cosine score between 0 (no similarity) and 1 (identical). Scores > 0.7 are typically considered reliable spectral matches. Entropy-based similarity is more robust to noise and missing peaks.

---

## 5. MSI Confidence Level Assignment

Systematic assignment of Metabolomics Standards Initiative identification confidence levels.

```python
import pandas as pd
import numpy as np

def assign_msi_levels(features_df, ms2_matches=None, standard_matches=None):
    """Assign MSI confidence levels to metabolite identifications.

    Parameters
    ----------
    features_df : pd.DataFrame
        Features with columns: feature_id, mz, rt, putative_name, hmdb_id,
        mass_ppm_error, formula.
    ms2_matches : pd.DataFrame or None
        MS2 spectral matching results with cosine_score column.
    standard_matches : pd.DataFrame or None
        Authentic standard matching results with rt_match and ms2_match columns.

    Returns
    -------
    pd.DataFrame with msi_level and evidence columns added.
    """
    result = features_df.copy()
    result["msi_level"] = 4  # Default: unknown
    result["evidence"] = "m/z and RT only"

    # Level 3: Putative class assignment based on mass
    has_formula = result["formula"].notna() & (result["formula"] != "")
    has_mass = result["mass_ppm_error"].notna() & (result["mass_ppm_error"] < 10)
    result.loc[has_formula & has_mass, "msi_level"] = 3
    result.loc[has_formula & has_mass, "evidence"] = (
        "Putative formula from accurate mass (" +
        result.loc[has_formula & has_mass, "mass_ppm_error"].round(1).astype(str) +
        " ppm)"
    )

    # Level 2: MS2 spectral match
    if ms2_matches is not None and len(ms2_matches) > 0:
        ms2_good = ms2_matches[ms2_matches["cosine_score"] >= 0.7]
        for _, match in ms2_good.iterrows():
            fid = match["query_id"]
            mask = result["feature_id"] == fid
            if mask.any():
                result.loc[mask, "msi_level"] = 2
                result.loc[mask, "evidence"] = (
                    f"MS2 library match: {match.get('match_name', 'unknown')} "
                    f"(cosine={match['cosine_score']:.3f}, "
                    f"peaks={match.get('matched_peaks', 'N/A')})"
                )
                if "match_name" in match:
                    result.loc[mask, "putative_name"] = match["match_name"]

    # Level 1: Authentic standard match
    if standard_matches is not None and len(standard_matches) > 0:
        for _, match in standard_matches.iterrows():
            fid = match["feature_id"]
            mask = result["feature_id"] == fid
            if mask.any() and match.get("rt_match", False) and match.get("ms2_match", False):
                result.loc[mask, "msi_level"] = 1
                result.loc[mask, "evidence"] = (
                    f"Authentic standard: RT match ({match.get('rt_error', 'N/A')}s), "
                    f"MS2 match (cosine={match.get('cosine_score', 'N/A')})"
                )

    # Summary
    print("MSI Level Distribution:")
    for level in [1, 2, 3, 4]:
        n = (result["msi_level"] == level).sum()
        pct = n / len(result) * 100
        labels = {1: "Identified", 2: "Putatively annotated",
                  3: "Putatively characterized class", 4: "Unknown"}
        print(f"  Level {level} ({labels[level]}): {n} ({pct:.1f}%)")

    return result

# Usage
features = pd.read_csv("feature_table_annotated.csv")
ms2 = pd.read_csv("spectral_matches.csv")
standards = pd.read_csv("standard_matches.csv")  # if available
annotated = assign_msi_levels(features, ms2_matches=ms2, standard_matches=standards)
annotated.to_csv("features_msi_levels.csv", index=False)
```

**Expected output**: Each feature receives an MSI level (1-4) with evidence documentation. Never claim Level 1 without authentic standard data run under identical conditions. Always report the proportion of Level 4 unknowns.

---

## 6. SIRIUS + CSI:FingerID Molecular Formula and Structure Prediction

Use SIRIUS for in silico molecular formula determination and CSI:FingerID for structure annotation.

```bash
# ---- Run SIRIUS 5+ from command line ----
# Input: .ms or .mgf file with MS1 and MS2 data

sirius \
    --input experimental.mgf \
    --output sirius_output/ \
    formula \
        --ppm-max 10 \
        --profile orbitrap \
        --candidates 5 \
        --elements-considered CHNOPSClBr \
    fingerid \
        --database bio \
    canopus \
    structure \
        --database bio

# ---- Or using .ms input format ----
# compound_1.ms:
# >compound compound_1
# >parentmass 362.1512
# >ionization [M+H]+
#
# >ms1
# 362.1512 100
#
# >ms2
# 85.0284 50
# 127.0390 80
# 145.0496 100
# 163.0601 30
```

```python
import pandas as pd
import json
import os

def parse_sirius_results(sirius_dir):
    """Parse SIRIUS output for molecular formula and structure predictions.

    Parameters
    ----------
    sirius_dir : str
        SIRIUS output directory.

    Returns
    -------
    pd.DataFrame with compound predictions.
    """
    results = []

    for compound_dir in os.listdir(sirius_dir):
        compound_path = os.path.join(sirius_dir, compound_dir)
        if not os.path.isdir(compound_path):
            continue

        entry = {"compound_id": compound_dir}

        # Formula candidates
        formula_file = os.path.join(compound_path, "formula_candidates.tsv")
        if os.path.exists(formula_file):
            formulas = pd.read_csv(formula_file, sep="\t")
            if len(formulas) > 0:
                best = formulas.iloc[0]
                entry["molecular_formula"] = best.get("molecularFormula", "")
                entry["sirius_score"] = best.get("SiriusScore", np.nan)
                entry["zodiac_score"] = best.get("ZodiacScore", np.nan)

        # CSI:FingerID structure candidates
        structure_file = os.path.join(compound_path, "structure_candidates.tsv")
        if os.path.exists(structure_file):
            structures = pd.read_csv(structure_file, sep="\t")
            if len(structures) > 0:
                best = structures.iloc[0]
                entry["structure_name"] = best.get("name", "")
                entry["structure_smiles"] = best.get("smiles", "")
                entry["structure_inchikey"] = best.get("InChIkey2D", "")
                entry["csi_score"] = best.get("CSI:FingerIDScore", np.nan)
                entry["confidence"] = best.get("ConfidenceScore", np.nan)

        # CANOPUS compound class
        canopus_file = os.path.join(compound_path, "canopus_summary.tsv")
        if os.path.exists(canopus_file):
            canopus = pd.read_csv(canopus_file, sep="\t")
            if len(canopus) > 0:
                entry["compound_class"] = canopus.iloc[0].get("most specific class", "")
                entry["superclass"] = canopus.iloc[0].get("superclass", "")

        results.append(entry)

    df = pd.DataFrame(results)
    print(f"SIRIUS results: {len(df)} compounds")
    print(f"  With formula: {df['molecular_formula'].notna().sum()}")
    print(f"  With structure: {df['structure_name'].notna().sum()}")
    if "compound_class" in df.columns:
        print(f"  With CANOPUS class: {df['compound_class'].notna().sum()}")
    return df

# Usage
sirius_results = parse_sirius_results("sirius_output/")
sirius_results.to_csv("sirius_annotations.csv", index=False)
```

**Key parameters**: `--profile orbitrap` sets mass accuracy expectations. `--database bio` restricts structure search to biologically relevant compounds. SIRIUS score > 0 and CSI:FingerID confidence > 0.7 indicate reliable predictions.

---

## 7. GNPS Molecular Networking via Feature-Based Molecular Networking (FBMN)

Build molecular networks from MS2 spectral similarity to discover structural families.

```python
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

def build_molecular_network(mgf_file, quant_table, cosine_threshold=0.7,
                             min_matched_peaks=4, max_shift=200,
                             top_k=10):
    """Build a molecular network from MS2 spectral similarity.

    Parameters
    ----------
    mgf_file : str
        Path to MGF file with MS2 spectra.
    quant_table : str
        Path to feature quantification table (feature_id, mz, rt, intensities).
    cosine_threshold : float
        Minimum cosine similarity for network edge.
    min_matched_peaks : int
        Minimum shared peaks between spectra.
    max_shift : float
        Maximum precursor mass difference (Da) for modified cosine.
    top_k : int
        Keep only top-K neighbors per node.

    Returns
    -------
    networkx.Graph, pd.DataFrame of edges.
    """
    from matchms.importing import load_from_mgf
    from matchms.similarity import ModifiedCosine
    from matchms.filtering import default_filters, normalize_intensities
    from matchms import calculate_scores

    # Load spectra
    spectra = list(load_from_mgf(mgf_file))
    spectra = [normalize_intensities(default_filters(s)) for s in spectra if s is not None]
    spectra = [s for s in spectra if s is not None and len(s.peaks.mz) >= min_matched_peaks]
    print(f"Spectra for networking: {len(spectra)}")

    # Calculate all-vs-all similarity
    similarity = ModifiedCosine(tolerance=0.02)
    scores = calculate_scores(spectra, spectra, similarity, is_symmetric=True)

    # Build edges
    edges = []
    for i in range(len(spectra)):
        neighbors = []
        for j in range(i + 1, len(spectra)):
            score_tuple = scores.scores[i][j]
            if isinstance(score_tuple, tuple):
                cosine, n_matched = score_tuple
            else:
                cosine = float(score_tuple)
                n_matched = 0

            precursor_diff = abs(
                float(spectra[i].get("precursor_mz") or 0) -
                float(spectra[j].get("precursor_mz") or 0)
            )

            if cosine >= cosine_threshold and n_matched >= min_matched_peaks and precursor_diff <= max_shift:
                neighbors.append((j, cosine, n_matched, precursor_diff))

        # Top-K filtering
        neighbors.sort(key=lambda x: -x[1])
        for j, cosine, n_matched, diff in neighbors[:top_k]:
            edges.append({
                "node1": spectra[i].get("feature_id", str(i)),
                "node2": spectra[j].get("feature_id", str(j)),
                "cosine": cosine,
                "matched_peaks": n_matched,
                "mass_diff": round(diff, 4),
            })

    edges_df = pd.DataFrame(edges)
    print(f"Network edges: {len(edges_df)}")

    # Build networkx graph
    G = nx.Graph()
    for s in spectra:
        fid = s.get("feature_id", "unknown")
        G.add_node(fid, precursor_mz=float(s.get("precursor_mz") or 0))
    for _, edge in edges_df.iterrows():
        G.add_edge(edge["node1"], edge["node2"],
                   weight=edge["cosine"], mass_diff=edge["mass_diff"])

    # Component analysis
    components = list(nx.connected_components(G))
    print(f"Connected components: {len(components)}")
    print(f"  Singletons: {sum(1 for c in components if len(c) == 1)}")
    print(f"  Clusters (>1 node): {sum(1 for c in components if len(c) > 1)}")
    print(f"  Largest cluster: {max(len(c) for c in components)} nodes")

    # Plot network
    fig, ax = plt.subplots(figsize=(12, 10))
    pos = nx.spring_layout(G, k=0.5, seed=42)
    node_sizes = [max(20, G.degree(n) * 10) for n in G.nodes()]
    nx.draw_networkx(G, pos, node_size=node_sizes, font_size=5,
                     node_color="lightblue", edge_color="gray", alpha=0.7, ax=ax)
    ax.set_title(f"Molecular Network ({len(G.nodes())} nodes, {len(G.edges())} edges)")
    plt.savefig("molecular_network.png", dpi=150, bbox_inches="tight")
    plt.close()

    return G, edges_df

# Usage
G, edges = build_molecular_network("features_ms2.mgf", "feature_table.csv")
edges.to_csv("network_edges.csv", index=False)
```

**Expected output**: A molecular network graph where nodes are MS2 spectra and edges represent spectral similarity. Connected components represent structural families (molecular families). Mass differences on edges indicate structural modifications (e.g., 14 Da = CH2 extension, 176 Da = glucuronide).

---

## 8. Accurate Mass Search with PPM Tolerance Calculation

Match observed m/z to database entries with appropriate mass accuracy.

```python
import pandas as pd
import numpy as np

def ppm_to_da(mz, ppm):
    """Convert ppm tolerance to Daltons at a given m/z."""
    return mz * ppm / 1e6

def da_to_ppm(mz, da):
    """Convert Dalton tolerance to ppm at a given m/z."""
    return da / mz * 1e6

def accurate_mass_search(observed_mz_list, database_df, ppm_tolerance=5,
                          mode="positive"):
    """Search observed m/z values against a metabolite database.

    Parameters
    ----------
    observed_mz_list : list of float
        Observed m/z values.
    database_df : pd.DataFrame
        Database with columns: compound_id, name, monoisotopic_mass, formula.
    ppm_tolerance : float
        Mass accuracy tolerance in ppm.
    mode : str
        Ionization mode: 'positive' or 'negative'.

    Returns
    -------
    pd.DataFrame with all matches within tolerance.
    """
    # Define adducts based on ionization mode
    adducts = {
        "positive": {
            "[M+H]+": 1.007276,
            "[M+Na]+": 22.989218,
            "[M+K]+": 38.963158,
            "[M+NH4]+": 18.034164,
            "[M+2H]2+": 1.007276,  # divide neutral mass by 2
            "[M+H-H2O]+": 1.007276 - 18.010565,
        },
        "negative": {
            "[M-H]-": -1.007276,
            "[M+FA-H]-": 44.998201,
            "[M+Cl]-": 34.969402,
            "[M-H-H2O]-": -1.007276 - 18.010565,
            "[M+CH3COO]-": 59.013851,
            "[M-2H]2-": -1.007276,  # divide neutral mass by 2
        },
    }

    adduct_set = adducts.get(mode, adducts["positive"])
    matches = []

    for obs_mz in observed_mz_list:
        for adduct_name, adduct_mass in adduct_set.items():
            # Calculate neutral mass from observed m/z
            if "2+" in adduct_name or "2-" in adduct_name:
                neutral_mass = (obs_mz - adduct_mass) * 2
            else:
                neutral_mass = obs_mz - adduct_mass

            tol_da = ppm_to_da(neutral_mass, ppm_tolerance)

            # Search database
            hits = database_df[
                (database_df["monoisotopic_mass"] >= neutral_mass - tol_da) &
                (database_df["monoisotopic_mass"] <= neutral_mass + tol_da)
            ]

            for _, hit in hits.iterrows():
                mass_error_ppm = da_to_ppm(
                    neutral_mass,
                    abs(hit["monoisotopic_mass"] - neutral_mass)
                )
                matches.append({
                    "observed_mz": obs_mz,
                    "adduct": adduct_name,
                    "neutral_mass_calc": neutral_mass,
                    "database_mass": hit["monoisotopic_mass"],
                    "mass_error_ppm": round(mass_error_ppm, 2),
                    "compound_id": hit["compound_id"],
                    "compound_name": hit["name"],
                    "formula": hit.get("formula", ""),
                })

    result = pd.DataFrame(matches)
    if len(result) > 0:
        result = result.sort_values(["observed_mz", "mass_error_ppm"])
    print(f"Searched {len(observed_mz_list)} m/z values, found {len(result)} matches")
    print(f"Unique compounds: {result['compound_id'].nunique()}")
    return result

# Usage
sig_features = pd.read_csv("significant_features.csv")
hmdb_db = pd.read_csv("hmdb_masses.csv")  # compound_id, name, monoisotopic_mass, formula
matches = accurate_mass_search(
    sig_features["mz"].tolist(), hmdb_db,
    ppm_tolerance=5, mode="positive"
)
matches.to_csv("mass_search_results.csv", index=False)
```

**Expected output**: All possible compound matches within ppm tolerance, ranked by mass error. Multiple adducts may match the same compound -- cross-validate with retention time and MS2 data to narrow candidates.

---

## 9. Adduct Annotation

Identify and group adduct clusters from the same metabolite.

```python
import pandas as pd
import numpy as np
from itertools import combinations

# Complete adduct tables
ADDUCTS = {
    "positive": {
        "[M+H]+": {"mass_diff": 1.007276, "charge": 1, "mult": 1},
        "[M+Na]+": {"mass_diff": 22.989218, "charge": 1, "mult": 1},
        "[M+K]+": {"mass_diff": 38.963158, "charge": 1, "mult": 1},
        "[M+NH4]+": {"mass_diff": 18.034164, "charge": 1, "mult": 1},
        "[M+H-H2O]+": {"mass_diff": -17.002740, "charge": 1, "mult": 1},
        "[M+2H]2+": {"mass_diff": 1.007276, "charge": 2, "mult": 1},
        "[2M+H]+": {"mass_diff": 1.007276, "charge": 1, "mult": 2},
        "[2M+Na]+": {"mass_diff": 22.989218, "charge": 1, "mult": 2},
    },
    "negative": {
        "[M-H]-": {"mass_diff": -1.007276, "charge": 1, "mult": 1},
        "[M+FA-H]-": {"mass_diff": 44.998201, "charge": 1, "mult": 1},
        "[M+Cl]-": {"mass_diff": 34.969402, "charge": 1, "mult": 1},
        "[M+CH3COO]-": {"mass_diff": 59.013851, "charge": 1, "mult": 1},
        "[M-H-H2O]-": {"mass_diff": -19.018390, "charge": 1, "mult": 1},
        "[M-2H]2-": {"mass_diff": -1.007276, "charge": 2, "mult": 1},
        "[2M-H]-": {"mass_diff": -1.007276, "charge": 1, "mult": 2},
    },
}

def annotate_adducts(feature_df, mz_col="mz", rt_col="rt",
                      mode="positive", ppm_tol=10, rt_tol=5):
    """Group features into adduct clusters from the same metabolite.

    Parameters
    ----------
    feature_df : pd.DataFrame
        Feature table with m/z and retention time columns.
    mode : str
        Ionization mode.
    ppm_tol : float
        Mass tolerance for adduct grouping.
    rt_tol : float
        RT tolerance in seconds for co-elution requirement.

    Returns
    -------
    pd.DataFrame with adduct_group and adduct_annotation columns.
    """
    adducts = ADDUCTS[mode]
    features = feature_df.copy().reset_index(drop=True)
    features["adduct_group"] = -1
    features["adduct_annotation"] = ""

    group_id = 0
    assigned = set()

    for i in range(len(features)):
        if i in assigned:
            continue

        mz_i = features.loc[i, mz_col]
        rt_i = features.loc[i, rt_col]

        # Try each primary adduct for feature i
        for adduct1_name, adduct1 in adducts.items():
            neutral_i = (mz_i * adduct1["charge"] - adduct1["mass_diff"]) / adduct1["mult"]

            cluster = [(i, adduct1_name)]

            for j in range(i + 1, len(features)):
                if j in assigned:
                    continue

                mz_j = features.loc[j, mz_col]
                rt_j = features.loc[j, rt_col]

                # Must co-elute
                if abs(rt_i - rt_j) > rt_tol:
                    continue

                # Try each adduct for feature j
                for adduct2_name, adduct2 in adducts.items():
                    if adduct2_name == adduct1_name:
                        continue
                    neutral_j = (mz_j * adduct2["charge"] - adduct2["mass_diff"]) / adduct2["mult"]
                    ppm_err = abs(neutral_i - neutral_j) / neutral_i * 1e6
                    if ppm_err < ppm_tol:
                        cluster.append((j, adduct2_name))
                        break

            if len(cluster) > 1:
                for idx, adduct_name in cluster:
                    features.loc[idx, "adduct_group"] = group_id
                    features.loc[idx, "adduct_annotation"] = adduct_name
                    assigned.add(idx)
                group_id += 1

    n_grouped = (features["adduct_group"] >= 0).sum()
    n_groups = features["adduct_group"].max() + 1 if n_grouped > 0 else 0
    print(f"Adduct annotation results:")
    print(f"  Features grouped: {n_grouped}/{len(features)}")
    print(f"  Adduct clusters: {n_groups}")
    print(f"  Ungrouped features: {len(features) - n_grouped}")

    if n_grouped > 0:
        print(f"\nAdduct distribution:")
        print(features[features["adduct_group"] >= 0]["adduct_annotation"].value_counts().to_string())

    return features

# Usage
features = pd.read_csv("feature_table.csv")
annotated = annotate_adducts(features, mode="positive", ppm_tol=10, rt_tol=5)
annotated.to_csv("features_adduct_annotated.csv", index=False)
```

**Expected output**: Features from the same metabolite (co-eluting, mass-consistent across adduct rules) are grouped. This reduces the effective feature count and prevents counting adducts as independent metabolites.

---

## 10. Isotope Pattern Validation

Validate metabolite identifications by checking isotope pattern agreement.

```python
import numpy as np
import re

def calculate_theoretical_isotopes(formula, n_isotopes=3):
    """Calculate theoretical isotope pattern from molecular formula.

    Parameters
    ----------
    formula : str
        Molecular formula (e.g., 'C6H12O6').
    n_isotopes : int
        Number of isotope peaks to calculate (M, M+1, M+2, ...).

    Returns
    -------
    list of (mass_offset, relative_intensity) tuples.
    """
    # Parse formula
    elements = re.findall(r'([A-Z][a-z]?)(\d*)', formula)
    composition = {}
    for elem, count in elements:
        if elem:
            composition[elem] = int(count) if count else 1

    # Natural isotope abundances (simplified)
    # (mass_diff, abundance relative to monoisotopic)
    isotope_data = {
        "C": (1.003355, 0.01082),  # 13C
        "H": (1.006277, 0.000115), # 2H
        "N": (0.997035, 0.00364),  # 15N
        "O": (2.004246, 0.00205),  # 18O (skipping 17O)
        "S": (1.995796, 0.0449),   # 34S
        "Cl": (1.997050, 0.3200),  # 37Cl
        "Br": (1.997953, 0.9726),  # 81Br
    }

    # Approximate isotope pattern (binomial model for M+1)
    # P(M+1) ≈ sum(n_i * abundance_i) for each element
    m_plus_1 = 0
    for elem, count in composition.items():
        if elem in isotope_data:
            _, abundance = isotope_data[elem]
            m_plus_1 += count * abundance

    # M+2 (simplified)
    m_plus_2 = m_plus_1 ** 2 / 2

    pattern = [(0, 1.0), (1, m_plus_1), (2, m_plus_2)]
    return pattern[:n_isotopes]

def validate_isotope_pattern(observed_mz, observed_int, formula,
                               charge=1, mz_tol=0.005, int_tol=0.3):
    """Validate observed isotope pattern against theoretical.

    Parameters
    ----------
    observed_mz : list of float
        Observed m/z values in the isotope envelope.
    observed_int : list of float
        Observed intensities.
    formula : str
        Molecular formula.
    charge : int
        Charge state.
    mz_tol : float
        m/z tolerance in Da for matching isotope peaks.
    int_tol : float
        Relative intensity tolerance (fraction). 0.3 = 30% deviation allowed.

    Returns
    -------
    dict with validation results.
    """
    theoretical = calculate_theoretical_isotopes(formula)

    # Normalize observed intensities
    obs_mz = np.array(observed_mz)
    obs_int = np.array(observed_int, dtype=float)
    obs_int = obs_int / obs_int[0] if obs_int[0] > 0 else obs_int

    results = {
        "formula": formula,
        "n_theoretical": len(theoretical),
        "matched_isotopes": 0,
        "mz_errors": [],
        "int_errors": [],
        "passes": True,
    }

    for i, (mass_offset, theo_int) in enumerate(theoretical):
        expected_mz = observed_mz[0] + mass_offset / charge

        # Find closest observed peak
        if i < len(obs_mz):
            mz_error = abs(obs_mz[i] - expected_mz)
            int_error = abs(obs_int[i] - theo_int) / max(theo_int, 0.001)

            results["mz_errors"].append(mz_error)
            results["int_errors"].append(int_error)

            if mz_error <= mz_tol and int_error <= int_tol:
                results["matched_isotopes"] += 1
            else:
                results["passes"] = False
        else:
            if theo_int > 0.05:  # Only fail if expected isotope is significant
                results["passes"] = False

    return results

# Usage
result = validate_isotope_pattern(
    observed_mz=[162.1125, 163.1159, 164.1192],
    observed_int=[100, 8.5, 0.4],
    formula="C7H15NO3",
    charge=1,
)
print(f"Formula: {result['formula']}")
print(f"Isotopes matched: {result['matched_isotopes']}/{result['n_theoretical']}")
print(f"Validation: {'PASS' if result['passes'] else 'FAIL'}")
```

**Expected output**: Validation result (PASS/FAIL) for each isotope pattern. Isotope pattern agreement increases confidence in molecular formula assignment. Chlorine- and bromine-containing compounds have distinctive M+2 patterns.

---

## 11. Blank Subtraction and Background Filtering

Remove contaminant features using blank/solvent control samples.

```python
import pandas as pd
import numpy as np

def blank_filter(feature_table, metadata, sample_type_col="sample_type",
                  blank_label="blank", fold_threshold=3, frequency_threshold=0.8):
    """Remove features likely originating from blanks/solvents.

    Parameters
    ----------
    feature_table : pd.DataFrame
        Feature intensities (features x samples).
    metadata : pd.DataFrame
        Sample metadata with sample_type column.
    blank_label : str
        Label for blank samples in sample_type column.
    fold_threshold : float
        Minimum fold change of sample vs blank mean to retain feature.
    frequency_threshold : float
        Features present in this fraction of blanks are considered contaminants
        (even if fold change is high in some samples).

    Returns
    -------
    pd.DataFrame with contaminant features removed.
    """
    blank_samples = metadata[metadata[sample_type_col] == blank_label].index
    study_samples = metadata[metadata[sample_type_col] != blank_label].index

    blank_data = feature_table[blank_samples.intersection(feature_table.columns)]
    study_data = feature_table[study_samples.intersection(feature_table.columns)]

    print(f"Blank samples: {len(blank_data.columns)}")
    print(f"Study samples: {len(study_data.columns)}")

    # Mean intensity in blanks and samples
    blank_mean = blank_data.mean(axis=1)
    study_mean = study_data.mean(axis=1)

    # Frequency in blanks
    blank_freq = (blank_data > 0).sum(axis=1) / len(blank_data.columns)

    # Fold change
    fold_change = study_mean / (blank_mean + 1e-10)

    # Flag contaminants
    is_contaminant = (
        (fold_change < fold_threshold) |
        ((blank_freq >= frequency_threshold) & (fold_change < fold_threshold * 2))
    )

    n_removed = is_contaminant.sum()
    n_retained = (~is_contaminant).sum()
    print(f"\nBlank subtraction results:")
    print(f"  Contaminants removed: {n_removed} ({n_removed/len(feature_table)*100:.1f}%)")
    print(f"  Features retained: {n_retained}")

    # Diagnostic: top contaminants
    contaminant_features = feature_table.index[is_contaminant]
    contam_df = pd.DataFrame({
        "feature": contaminant_features,
        "blank_mean": blank_mean[is_contaminant],
        "study_mean": study_mean[is_contaminant],
        "fold_change": fold_change[is_contaminant],
        "blank_frequency": blank_freq[is_contaminant],
    }).sort_values("blank_mean", ascending=False)
    print(f"\nTop contaminants:")
    print(contam_df.head(10).to_string(index=False))

    filtered = feature_table.loc[~is_contaminant, study_data.columns]
    return filtered

# Usage
feature_table = pd.read_csv("feature_table.csv", index_col=0)
metadata = pd.read_csv("sample_metadata.csv", index_col=0)
clean_data = blank_filter(feature_table, metadata, fold_threshold=3)
clean_data.to_csv("feature_table_blank_subtracted.csv")
```

**Expected output**: Features with high blank intensity relative to study samples are removed. Common contaminants include plasticizers (phthalates), detergents, and solvent impurities.

---

## 12. Lipidomics: Lipid Class Identification with LipidSearch/MS-DIAL Output

Parse and analyze lipid identification results from dedicated lipidomics software.

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def process_lipidomics_results(lipid_file, format="msdial"):
    """Parse lipidomics identification results and summarize by lipid class.

    Parameters
    ----------
    lipid_file : str
        Output file from LipidSearch or MS-DIAL.
    format : str
        'msdial' or 'lipidsearch'.

    Returns
    -------
    pd.DataFrame with parsed lipid annotations and class summaries.
    """
    if format == "msdial":
        df = pd.read_csv(lipid_file, sep="\t")
        # MS-DIAL columns: Metabolite name, Adduct type, Average Rt(min),
        #                   Average Mz, MS/MS spectrum, etc.
        name_col = "Metabolite name"
        mz_col = "Average Mz"
        rt_col = "Average Rt(min)"
    elif format == "lipidsearch":
        df = pd.read_csv(lipid_file)
        name_col = "LipidMolec"
        mz_col = "ObsMz"
        rt_col = "RT"
    else:
        raise ValueError(f"Unknown format: {format}")

    # Parse lipid class from name (e.g., "PC 34:1" -> class="PC")
    def parse_lipid_class(name):
        if pd.isna(name) or name == "" or name == "Unknown":
            return "Unknown"
        # Match patterns like PC, PE, SM, TAG, DAG, Cer, etc.
        import re
        match = re.match(r'^([A-Za-z]+(?:\s)?[A-Za-z]*)', str(name))
        if match:
            cls = match.group(1).strip()
            # Standardize
            class_map = {
                "PC": "PC", "LPC": "LPC", "LysoPC": "LPC",
                "PE": "PE", "LPE": "LPE", "LysoPE": "LPE",
                "PS": "PS", "PI": "PI", "PG": "PG", "PA": "PA",
                "SM": "SM", "Cer": "Cer", "CerP": "CerP",
                "HexCer": "HexCer", "GlcCer": "GlcCer",
                "TAG": "TAG", "TG": "TAG", "DAG": "DAG", "DG": "DAG",
                "MAG": "MAG", "MG": "MAG",
                "CE": "CE", "ChE": "CE",
                "FA": "FA", "CAR": "CAR",
            }
            for key, value in class_map.items():
                if cls.startswith(key):
                    return value
            return cls
        return "Unknown"

    def parse_chain_composition(name):
        """Extract total carbon and double bonds from lipid name."""
        import re
        match = re.search(r'(\d+):(\d+)', str(name))
        if match:
            return int(match.group(1)), int(match.group(2))
        return None, None

    df["lipid_class"] = df[name_col].apply(parse_lipid_class)
    chain_info = df[name_col].apply(parse_chain_composition)
    df["total_carbons"] = [c[0] for c in chain_info]
    df["total_db"] = [c[1] for c in chain_info]

    # Summary
    class_counts = df["lipid_class"].value_counts()
    print(f"Lipid identification results:")
    print(f"  Total features: {len(df)}")
    print(f"  Identified lipids: {(df['lipid_class'] != 'Unknown').sum()}")
    print(f"  Lipid classes: {df['lipid_class'].nunique()}")
    print(f"\nLipid class distribution:")
    print(class_counts.to_string())

    # Lipid class barplot
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    class_counts[class_counts.index != "Unknown"].plot.bar(ax=axes[0], color="steelblue")
    axes[0].set_title("Lipid Class Distribution")
    axes[0].set_ylabel("Count")

    # Carbon number vs double bond bubble plot
    known = df[df["lipid_class"] != "Unknown"].dropna(subset=["total_carbons", "total_db"])
    if len(known) > 0:
        for cls in known["lipid_class"].unique()[:8]:
            subset = known[known["lipid_class"] == cls]
            axes[1].scatter(subset["total_carbons"], subset["total_db"],
                          label=cls, alpha=0.6, s=30)
        axes[1].set_xlabel("Total Carbons")
        axes[1].set_ylabel("Double Bonds")
        axes[1].set_title("Chain Composition")
        axes[1].legend(fontsize=7, bbox_to_anchor=(1.05, 1))

    plt.tight_layout()
    plt.savefig("lipidomics_overview.png", dpi=150, bbox_inches="tight")
    plt.close()

    return df

# ---- Lipid pathway activity ratios ----
def calculate_lipid_ratios(lipid_data, intensity_cols):
    """Calculate biologically meaningful lipid ratios.

    Parameters
    ----------
    lipid_data : pd.DataFrame
        Lipid feature table with lipid_class and intensity columns.
    intensity_cols : list
        Sample intensity column names.

    Returns
    -------
    pd.DataFrame with ratio metrics per sample.
    """
    ratios = pd.DataFrame(index=intensity_cols)

    class_sums = lipid_data.groupby("lipid_class")[intensity_cols].sum()

    if "LPC" in class_sums.index and "PC" in class_sums.index:
        ratios["LPC_PC_ratio"] = class_sums.loc["LPC"] / class_sums.loc["PC"]
        # Interpretation: elevated LPC/PC indicates PLA2 activity, inflammation

    if "PC" in class_sums.index and "PE" in class_sums.index:
        ratios["PC_PE_ratio"] = class_sums.loc["PC"] / class_sums.loc["PE"]
        # Interpretation: altered PC/PE indicates membrane remodeling, PEMT activity

    if "Cer" in class_sums.index and "SM" in class_sums.index:
        ratios["Cer_SM_ratio"] = class_sums.loc["Cer"] / class_sums.loc["SM"]
        # Interpretation: elevated Cer/SM indicates sphingomyelinase activity, apoptosis

    if "DAG" in class_sums.index and "TAG" in class_sums.index:
        ratios["DAG_TAG_ratio"] = class_sums.loc["DAG"] / class_sums.loc["TAG"]
        # Interpretation: elevated DAG/TAG indicates lipolysis or lipogenesis disruption

    print("Lipid pathway activity ratios:")
    print(ratios.describe().round(3).to_string())
    return ratios

# Usage
lipid_df = process_lipidomics_results("msdial_output.txt", format="msdial")
intensity_cols = [c for c in lipid_df.columns if c.startswith("Sample")]
ratios = calculate_lipid_ratios(lipid_df, intensity_cols)
```

**Expected output**: Lipid class distribution, chain composition plot, and pathway activity ratios. Key ratios: LPC/PC (PLA2/inflammation), Cer/SM (sphingomyelinase/apoptosis), PC/PE (membrane integrity). Map to KEGG pathways: glycerophospholipid metabolism (map00564), sphingolipid metabolism (map00600).
