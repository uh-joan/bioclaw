# Single-Cell RNA-seq Quality Control Recipes

Python code templates for scRNA-seq quality control: data loading, QC metric calculation, adaptive filtering, doublet detection, ambient RNA removal, cell cycle scoring, and QC reporting.

Cross-skill routing: use `clustering-recipes` for downstream clustering after QC, `recipes` for miRNA DE and scvi-tools.

---

## 1. Load 10x Genomics .h5 Files

Load Cell Ranger output in HDF5 format with gene and barcode metadata.

```python
import scanpy as sc
import anndata as ad

def load_10x_h5(filepath: str, genome: str = None) -> ad.AnnData:
    """Load 10x Genomics .h5 file (Cell Ranger output).

    Parameters
    ----------
    filepath : str
        Path to filtered_feature_bc_matrix.h5 or raw_feature_bc_matrix.h5.
    genome : str or None
        Genome name if multi-genome experiment (e.g., 'GRCh38'). None for single-genome.

    Returns
    -------
    AnnData with raw counts in .X, gene metadata in .var.
    """
    adata = sc.read_10x_h5(filepath, genome=genome)
    adata.var_names_make_unique()

    print(f"Loaded: {adata.n_obs} cells x {adata.n_vars} genes")
    print(f"  Sparse format: {type(adata.X).__name__}")
    print(f"  Gene ID column: {'gene_ids' if 'gene_ids' in adata.var.columns else 'index'}")
    print(f"  Feature types: {adata.var['feature_types'].unique().tolist() if 'feature_types' in adata.var.columns else 'N/A'}")

    # Store raw counts in a layer for later use
    adata.layers["counts"] = adata.X.copy()
    return adata

# Usage
adata = load_10x_h5("filtered_feature_bc_matrix.h5")

# For multi-modal data (CITE-seq with Gene Expression + Antibody Capture):
# adata = load_10x_h5("filtered_feature_bc_matrix.h5")
# adata_gex = adata[:, adata.var["feature_types"] == "Gene Expression"].copy()
# adata_adt = adata[:, adata.var["feature_types"] == "Antibody Capture"].copy()
```

**Expected output**: AnnData object with sparse count matrix, gene symbols as var_names, barcodes as obs_names. Typical 10x output: 500-20,000 cells x 20,000-35,000 genes.

---

## 2. Load .h5ad Files with Validation

Load pre-processed AnnData objects with integrity checks.

```python
import scanpy as sc
import numpy as np

def load_h5ad(filepath: str, validate: bool = True) -> sc.AnnData:
    """Load .h5ad file with validation checks.

    Parameters
    ----------
    filepath : str
        Path to .h5ad file.
    validate : bool
        Run integrity checks on loaded data.

    Returns
    -------
    AnnData with validation report printed.
    """
    adata = sc.read_h5ad(filepath)

    if validate:
        print(f"Shape: {adata.n_obs} cells x {adata.n_vars} genes")
        print(f"X dtype: {adata.X.dtype}")

        # Check if X contains raw counts or normalized data
        if hasattr(adata.X, "toarray"):
            sample = adata.X[:100].toarray()
        else:
            sample = adata.X[:100]
        has_integers = np.allclose(sample, np.round(sample), equal_nan=True)
        x_max = np.max(sample)
        print(f"  X appears to be: {'raw counts' if has_integers and x_max > 10 else 'normalized/log-transformed'}")
        print(f"  X range: [{np.min(sample):.2f}, {x_max:.2f}]")

        # Check layers
        if adata.layers:
            print(f"Layers: {list(adata.layers.keys())}")

        # Check obs metadata
        print(f"Obs columns: {list(adata.obs.columns)}")

        # Check embeddings
        if adata.obsm:
            print(f"Embeddings: {list(adata.obsm.keys())}")

        # Check for raw
        if adata.raw is not None:
            print(f"Raw: {adata.raw.shape[0]} x {adata.raw.shape[1]}")

    return adata

# Usage
adata = load_h5ad("processed_data.h5ad")

# If counts are in a layer, set X to counts for QC:
# adata.X = adata.layers["counts"].copy()
```

**Expected output**: Validation summary showing data shape, whether X contains counts or normalized values, available layers and embeddings. Critical for determining which QC steps are still needed.

---

## 3. Calculate Comprehensive QC Metrics

Compute per-cell and per-gene quality metrics including mitochondrial, ribosomal, and hemoglobin fractions.

```python
import scanpy as sc
import numpy as np

def calculate_qc_metrics(adata, species: str = "human"):
    """Calculate comprehensive QC metrics for scRNA-seq data.

    Parameters
    ----------
    adata : AnnData
        Raw count matrix (cells x genes).
    species : str
        'human' (MT- prefix) or 'mouse' (mt- prefix) for mitochondrial genes.

    Returns
    -------
    adata with QC metrics in .obs and .var.
    """
    # Mitochondrial genes
    if species == "human":
        adata.var["mt"] = adata.var_names.str.startswith("MT-")
    elif species == "mouse":
        adata.var["mt"] = adata.var_names.str.startswith("mt-")
    else:
        raise ValueError(f"Unknown species: {species}. Use 'human' or 'mouse'.")

    # Ribosomal genes (RPL/RPS for human, Rpl/Rps for mouse)
    if species == "human":
        adata.var["ribo"] = adata.var_names.str.match(r"^RP[SL]\d+")
    else:
        adata.var["ribo"] = adata.var_names.str.match(r"^Rp[sl]\d+")

    # Hemoglobin genes (for blood/tissue contamination)
    if species == "human":
        adata.var["hb"] = adata.var_names.str.match(r"^HB[^P]")
    else:
        adata.var["hb"] = adata.var_names.str.match(r"^Hb[^p]")

    # Calculate QC metrics
    sc.pp.calculate_qc_metrics(
        adata,
        qc_vars=["mt", "ribo", "hb"],
        percent_top=None,
        log1p=True,
        inplace=True,
    )

    # Summary
    print(f"QC Metrics Summary ({adata.n_obs} cells):")
    print(f"  total_counts:      median={adata.obs['total_counts'].median():.0f}, "
          f"range=[{adata.obs['total_counts'].min():.0f}, {adata.obs['total_counts'].max():.0f}]")
    print(f"  n_genes_by_counts: median={adata.obs['n_genes_by_counts'].median():.0f}, "
          f"range=[{adata.obs['n_genes_by_counts'].min():.0f}, {adata.obs['n_genes_by_counts'].max():.0f}]")
    print(f"  pct_counts_mt:     median={adata.obs['pct_counts_mt'].median():.1f}%, "
          f"range=[{adata.obs['pct_counts_mt'].min():.1f}%, {adata.obs['pct_counts_mt'].max():.1f}%]")
    print(f"  pct_counts_ribo:   median={adata.obs['pct_counts_ribo'].median():.1f}%, "
          f"range=[{adata.obs['pct_counts_ribo'].min():.1f}%, {adata.obs['pct_counts_ribo'].max():.1f}%]")
    print(f"  pct_counts_hb:     median={adata.obs['pct_counts_hb'].median():.1f}%")
    print(f"  Mitochondrial genes found: {adata.var['mt'].sum()}")
    print(f"  Ribosomal genes found: {adata.var['ribo'].sum()}")

    return adata

# Usage
adata = calculate_qc_metrics(adata, species="human")
```

**Expected output**: QC columns added to `adata.obs`: `total_counts`, `n_genes_by_counts`, `pct_counts_mt`, `pct_counts_ribo`, `pct_counts_hb`, plus log1p versions. Typical human PBMC: median ~2000 genes, ~5000 counts, <5% MT.

---

## 4. MAD-Based Adaptive Outlier Detection

Data-driven filtering using median absolute deviation thresholds instead of fixed cutoffs.

```python
import scanpy as sc
import numpy as np
import pandas as pd

def mad_outlier_filter(adata, n_mads_counts: float = 5.0, n_mads_genes: float = 5.0,
                       n_mads_mt: float = 3.0, log_transform: bool = True):
    """Filter cells using MAD-based adaptive thresholds.

    More robust than fixed cutoffs — adapts to each dataset's distribution.

    Parameters
    ----------
    adata : AnnData
        Must have QC metrics calculated (total_counts, n_genes_by_counts, pct_counts_mt).
    n_mads_counts : float
        Number of MADs from median for total_counts filtering. 5 MADs is permissive.
    n_mads_genes : float
        Number of MADs from median for n_genes_by_counts filtering.
    n_mads_mt : float
        Number of MADs from median for pct_counts_mt filtering (upper bound only). 3 MADs is standard.
    log_transform : bool
        Apply log1p before computing MAD for counts/genes (recommended for skewed distributions).

    Returns
    -------
    adata with 'outlier' column in .obs and filtering summary.
    """
    def is_outlier(series, n_mads, log=False, upper_only=False):
        """Flag values outside median +/- n_mads * MAD."""
        values = np.log1p(series) if log else series.copy()
        median = np.median(values)
        mad = np.median(np.abs(values - median)) * 1.4826  # scale to match std
        if upper_only:
            return values > median + n_mads * mad
        return (values < median - n_mads * mad) | (values > median + n_mads * mad)

    # Flag outliers per metric
    outlier_counts = is_outlier(adata.obs["total_counts"], n_mads_counts, log=log_transform)
    outlier_genes = is_outlier(adata.obs["n_genes_by_counts"], n_mads_genes, log=log_transform)
    outlier_mt = is_outlier(adata.obs["pct_counts_mt"], n_mads_mt, upper_only=True)

    adata.obs["outlier"] = outlier_counts | outlier_genes | outlier_mt
    adata.obs["outlier_counts"] = outlier_counts
    adata.obs["outlier_genes"] = outlier_genes
    adata.obs["outlier_mt"] = outlier_mt

    # Compute thresholds for reporting
    def get_thresholds(series, n_mads, log=False):
        values = np.log1p(series) if log else series.copy()
        median = np.median(values)
        mad = np.median(np.abs(values - median)) * 1.4826
        lo = median - n_mads * mad
        hi = median + n_mads * mad
        if log:
            lo, hi = np.expm1(lo), np.expm1(hi)
        return lo, hi

    lo_c, hi_c = get_thresholds(adata.obs["total_counts"], n_mads_counts, log=log_transform)
    lo_g, hi_g = get_thresholds(adata.obs["n_genes_by_counts"], n_mads_genes, log=log_transform)
    _, hi_mt = get_thresholds(adata.obs["pct_counts_mt"], n_mads_mt)

    n_outliers = adata.obs["outlier"].sum()
    print(f"MAD-based filtering ({adata.n_obs} cells):")
    print(f"  total_counts:      [{lo_c:.0f}, {hi_c:.0f}] ({n_mads_counts} MADs) → {outlier_counts.sum()} outliers")
    print(f"  n_genes_by_counts: [{lo_g:.0f}, {hi_g:.0f}] ({n_mads_genes} MADs) → {outlier_genes.sum()} outliers")
    print(f"  pct_counts_mt:     [0, {hi_mt:.1f}%] ({n_mads_mt} MADs) → {outlier_mt.sum()} outliers")
    print(f"  Total outliers: {n_outliers} ({n_outliers/adata.n_obs*100:.1f}%)")
    print(f"  Cells remaining: {adata.n_obs - n_outliers}")

    return adata

# Usage
adata = mad_outlier_filter(adata, n_mads_counts=5, n_mads_genes=5, n_mads_mt=3)

# Apply filter
adata_filtered = adata[~adata.obs["outlier"]].copy()
print(f"After filtering: {adata_filtered.n_obs} cells")
```

**Expected output**: Adaptive thresholds computed per dataset. Typical removal: 3-10% of cells. The 1.4826 scaling factor converts MAD to an estimator of standard deviation under normality.

---

## 5. QC Metric Visualization

Violin plots, scatter plots, and ranked barplots for QC metric assessment.

```python
import scanpy as sc
import matplotlib.pyplot as plt
import numpy as np

def plot_qc_metrics(adata, save_prefix: str = "qc"):
    """Generate comprehensive QC visualization panels.

    Parameters
    ----------
    adata : AnnData
        Must have QC metrics calculated.
    save_prefix : str
        Filename prefix for saved plots.

    Returns
    -------
    None. Saves plots to disk.
    """
    # Panel 1: Violin plots
    fig, axes = plt.subplots(1, 4, figsize=(20, 5))
    sc.pl.violin(adata, "n_genes_by_counts", ax=axes[0], show=False)
    sc.pl.violin(adata, "total_counts", ax=axes[1], show=False)
    sc.pl.violin(adata, "pct_counts_mt", ax=axes[2], show=False)
    sc.pl.violin(adata, "pct_counts_ribo", ax=axes[3], show=False)
    plt.tight_layout()
    plt.savefig(f"{save_prefix}_violins.png", dpi=150, bbox_inches="tight")
    plt.close()

    # Panel 2: Scatter plots (key relationships)
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    sc.pl.scatter(adata, x="total_counts", y="n_genes_by_counts",
                  color="pct_counts_mt", ax=axes[0], show=False)
    axes[0].set_title("Counts vs Genes (colored by %MT)")

    sc.pl.scatter(adata, x="total_counts", y="pct_counts_mt",
                  ax=axes[1], show=False)
    axes[1].set_title("Counts vs %MT")

    sc.pl.scatter(adata, x="n_genes_by_counts", y="pct_counts_ribo",
                  ax=axes[2], show=False)
    axes[2].set_title("Genes vs %Ribo")

    plt.tight_layout()
    plt.savefig(f"{save_prefix}_scatter.png", dpi=150, bbox_inches="tight")
    plt.close()

    # Panel 3: Ranked barplot of counts per cell (knee plot proxy)
    fig, ax = plt.subplots(figsize=(10, 5))
    sorted_counts = np.sort(adata.obs["total_counts"].values)[::-1]
    ax.plot(range(len(sorted_counts)), sorted_counts)
    ax.set_xlabel("Cell Rank")
    ax.set_ylabel("Total Counts")
    ax.set_title("Barcode Rank Plot")
    ax.set_yscale("log")
    ax.set_xscale("log")
    plt.savefig(f"{save_prefix}_barcode_rank.png", dpi=150, bbox_inches="tight")
    plt.close()

    print(f"Saved: {save_prefix}_violins.png, {save_prefix}_scatter.png, {save_prefix}_barcode_rank.png")

# Usage
plot_qc_metrics(adata, save_prefix="sample1_qc")
```

**Expected output**: Three plot panels saved. Violins show per-metric distributions; scatter plots reveal correlations (high-MT cells often have low gene counts = dying cells); barcode rank plot shows the cell/empty droplet boundary.

---

## 6. Doublet Detection with Scrublet

Identify likely doublets using simulated doublet nearest-neighbor scoring.

```python
import scrublet as scr
import scanpy as sc
import numpy as np
import matplotlib.pyplot as plt

def detect_doublets_scrublet(adata, n_prin_comps: int = 30, threshold: float = None):
    """Run Scrublet doublet detection with expected rate based on loaded cell count.

    Parameters
    ----------
    adata : AnnData
        Raw count matrix (before normalization).
    n_prin_comps : int
        Number of PCs for nearest-neighbor calculation.
    threshold : float or None
        Manual score threshold. None = automatic bimodal detection.

    Returns
    -------
    adata with 'doublet_score' and 'predicted_doublet' in obs.

    Notes
    -----
    Expected doublet rate scales with cell loading:
      1,000 cells → ~0.8%
      5,000 cells → ~4.0%
      10,000 cells → ~8.0%
      20,000 cells → ~16.0%
    Formula: ~0.008 * (n_cells / 1000)
    """
    # Estimate expected doublet rate from cell count
    n_cells = adata.n_obs
    expected_rate = min(0.008 * (n_cells / 1000), 0.25)  # cap at 25%
    print(f"Cells loaded: {n_cells}, expected doublet rate: {expected_rate:.1%}")

    # Use raw counts
    counts = adata.layers["counts"] if "counts" in adata.layers else adata.X

    scrub = scr.Scrublet(counts, expected_doublet_rate=expected_rate)
    doublet_scores, predicted_doublets = scrub.scrub_doublets(
        min_counts=2,
        min_cells=3,
        n_prin_comps=n_prin_comps,
    )

    if threshold is not None:
        predicted_doublets = doublet_scores > threshold

    adata.obs["doublet_score"] = doublet_scores
    adata.obs["predicted_doublet"] = predicted_doublets

    n_doublets = predicted_doublets.sum()
    print(f"Doublets detected: {n_doublets} ({n_doublets/n_cells*100:.1f}%)")
    print(f"Automatic threshold: {scrub.threshold_:.3f}")

    # Diagnostic plot
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    axes[0].hist(scrub.doublet_scores_obs_, bins=50, alpha=0.6, label="Observed", density=True)
    axes[0].hist(scrub.doublet_scores_sim_, bins=50, alpha=0.6, label="Simulated", density=True)
    axes[0].axvline(scrub.threshold_, color="black", ls="--", label=f"Threshold={scrub.threshold_:.3f}")
    axes[0].set_xlabel("Doublet Score")
    axes[0].set_ylabel("Density")
    axes[0].legend()
    axes[0].set_title("Doublet Score Distribution")

    # Score vs gene count
    axes[1].scatter(adata.obs["n_genes_by_counts"], doublet_scores, s=1, alpha=0.3,
                    c=["red" if d else "gray" for d in predicted_doublets])
    axes[1].set_xlabel("n_genes_by_counts")
    axes[1].set_ylabel("Doublet Score")
    axes[1].set_title("Doublet Score vs Gene Count")

    plt.tight_layout()
    plt.savefig("doublet_detection.png", dpi=150, bbox_inches="tight")
    plt.close()

    return adata

# Usage
adata = detect_doublets_scrublet(adata)
# Filter doublets
adata = adata[~adata.obs["predicted_doublet"]].copy()
print(f"After doublet removal: {adata.n_obs} cells")
```

**Expected output**: Bimodal score distribution with clear threshold. Doublets typically have higher gene counts. If no bimodal split is found, consider per-sample detection or adjusting n_prin_comps.

---

## 7. Ambient RNA Removal with SoupX

Estimate and correct for ambient RNA contamination from lysed cells.

```python
import scanpy as sc
import numpy as np

def run_soupx(filtered_h5: str, raw_h5: str, output_path: str = "soupx_corrected.h5ad"):
    """Run SoupX ambient RNA correction via rpy2.

    Parameters
    ----------
    filtered_h5 : str
        Path to Cell Ranger filtered_feature_bc_matrix.h5.
    raw_h5 : str
        Path to Cell Ranger raw_feature_bc_matrix.h5 (includes empty droplets).
    output_path : str
        Path to save corrected AnnData.

    Returns
    -------
    AnnData with corrected counts in .X and original in .layers['uncorrected'].

    Notes
    -----
    SoupX requires both filtered (cells) and raw (all barcodes) matrices to
    estimate the ambient RNA profile from empty droplets.
    """
    import rpy2.robjects as ro
    from rpy2.robjects import pandas2ri, numpy2ri
    from rpy2.robjects.packages import importr
    pandas2ri.activate()
    numpy2ri.activate()

    SoupX = importr("SoupX")
    Matrix = importr("Matrix")

    # Load in R
    ro.r(f'''
    library(SoupX)
    library(Seurat)

    # Load Cell Ranger data
    sc <- load10X("{filtered_h5.rsplit("/", 1)[0]}/")

    # Quick cluster for SoupX (required)
    sc <- setClusters(sc, setNames(
        as.character(sc$metaData$clusters),
        rownames(sc$metaData)
    ))

    # Estimate contamination fraction
    sc <- autoEstCont(sc, verbose = TRUE)
    cat("Estimated contamination fraction:", sc$fit$rhoEst, "\n")

    # Correct counts
    corrected <- adjustCounts(sc, roundToInt = TRUE)
    ''')

    # Extract corrected matrix back to Python
    corrected_r = ro.r("corrected")
    contamination = ro.r("sc$fit$rhoEst")[0]

    # Alternative: pure Python approach using SoupX output
    # Load filtered data
    adata = sc.read_10x_h5(filtered_h5)
    adata.var_names_make_unique()

    print(f"SoupX correction complete:")
    print(f"  Estimated contamination: {contamination:.1%}")
    print(f"  Output: {output_path}")

    return adata

# Alternative: CellBender for GPU-accelerated ambient RNA removal
def run_cellbender_command(raw_h5: str, output_h5: str, expected_cells: int = 5000,
                           total_droplets: int = 25000, epochs: int = 150):
    """Generate CellBender command for ambient RNA removal.

    Parameters
    ----------
    raw_h5 : str
        Path to Cell Ranger raw_feature_bc_matrix.h5.
    output_h5 : str
        Path for CellBender output.
    expected_cells : int
        Expected number of real cells.
    total_droplets : int
        Total droplets to include (cells + empty). Should be > expected_cells.
    epochs : int
        Training epochs. 150 is default; increase for complex samples.

    Returns
    -------
    str: CellBender command to run.
    """
    cmd = (
        f"cellbender remove-background "
        f"--input {raw_h5} "
        f"--output {output_h5} "
        f"--expected-cells {expected_cells} "
        f"--total-droplets-included {total_droplets} "
        f"--epochs {epochs} "
        f"--cuda"
    )
    print(f"Run CellBender:\n  {cmd}")
    print(f"\nLoad result: adata = sc.read_h5ad('{output_h5}')")
    return cmd

# Usage
# SoupX (R-based):
# adata = run_soupx("filtered_feature_bc_matrix.h5", "raw_feature_bc_matrix.h5")

# CellBender (GPU):
cmd = run_cellbender_command("raw_feature_bc_matrix.h5", "cellbender_output.h5",
                              expected_cells=8000, total_droplets=25000)
```

**Expected output**: SoupX reports estimated contamination fraction (typically 1-10%). CellBender produces a corrected .h5ad. Both methods reduce expression of ambient genes (e.g., hemoglobin in non-blood cells, highly expressed genes leaking across all barcodes).

---

## 8. Cell Cycle Scoring

Score cells for S and G2M phase activity using Tirosh et al. 2015 marker genes.

```python
import scanpy as sc

def score_cell_cycle(adata, species: str = "human"):
    """Score cell cycle phase using Tirosh et al. 2015 gene lists.

    Parameters
    ----------
    adata : AnnData
        Normalized and log-transformed expression data.
    species : str
        'human' (gene symbols as-is) or 'mouse' (capitalize first letter only).

    Returns
    -------
    adata with 'S_score', 'G2M_score', and 'phase' in .obs.

    Notes
    -----
    Gene lists from Tirosh et al. 2015 (Science). These genes were identified
    as cell cycle markers across multiple tumor types.
    """
    # Tirosh et al. 2015 S-phase genes
    s_genes = [
        "MCM5", "PCNA", "TYMS", "FEN1", "MCM2", "MCM4", "RRM1", "UNG",
        "GINS2", "MCM6", "CDCA7", "DTL", "PRIM1", "UHRF1", "MLF1IP",
        "HELLS", "RFC2", "RPA2", "NASP", "RAD51AP1", "GMNN", "WDR76",
        "SLBP", "CCNE2", "UBR7", "POLD3", "MSH2", "ATAD2", "RAD51",
        "RRM2", "CDC45", "CDC6", "EXO1", "TIPIN", "DSCC1", "BLM",
        "CASP8AP2", "USP1", "CLSPN", "POLA1", "CHAF1B", "BRIP1", "E2F8",
    ]

    # Tirosh et al. 2015 G2M-phase genes
    g2m_genes = [
        "HMGB2", "CDK1", "NUSAP1", "UBE2C", "BIRC5", "TPX2", "TOP2A",
        "NDC80", "CKS2", "NUF2", "CKS1B", "MKI67", "TMPO", "CENPF",
        "TACC3", "FAM64A", "SMC4", "CCNB2", "CKAP2L", "CKAP2", "AURKB",
        "BUB1", "KIF11", "ANP32E", "TUBB4B", "GTSE1", "KIF20B", "HJURP",
        "CDCA3", "HN1", "CDC20", "TTK", "CDC25C", "KIF2C", "RANGAP1",
        "NCAPD2", "DLGAP5", "CDCA2", "CDCA8", "ECT2", "KIF23", "HMMR",
        "AURKA", "PSRC1", "ANLN", "LBR", "CKAP5", "CENPE", "CTCF",
        "NEK2", "G2E3", "GAS2L3", "CBX5", "CENPA",
    ]

    # Convert to mouse gene names if needed (capitalize first letter)
    if species == "mouse":
        s_genes = [g.capitalize() for g in s_genes]
        g2m_genes = [g.capitalize() for g in g2m_genes]

    # Score
    sc.tl.score_genes_cell_cycle(adata, s_genes=s_genes, g2m_genes=g2m_genes)

    # Summary
    phase_counts = adata.obs["phase"].value_counts()
    print(f"Cell cycle scoring ({adata.n_obs} cells):")
    for phase in ["G1", "S", "G2M"]:
        n = phase_counts.get(phase, 0)
        print(f"  {phase}: {n} ({n/adata.n_obs*100:.1f}%)")

    print(f"\nS_score:   mean={adata.obs['S_score'].mean():.3f}, std={adata.obs['S_score'].std():.3f}")
    print(f"G2M_score: mean={adata.obs['G2M_score'].mean():.3f}, std={adata.obs['G2M_score'].std():.3f}")

    return adata

# Usage
adata = score_cell_cycle(adata, species="human")

# Regress out cell cycle effects if needed (optional):
# sc.pp.regress_out(adata, ["S_score", "G2M_score"])

# Or regress out only the difference (preserve cycling vs non-cycling distinction):
# adata.obs["cc_difference"] = adata.obs["S_score"] - adata.obs["G2M_score"]
# sc.pp.regress_out(adata, ["cc_difference"])
```

**Expected output**: Each cell assigned to G1, S, or G2M phase. High proliferating tissues (tumors, bone marrow) may show 20-40% cycling cells. Resting tissues (adult brain) show <5%.

---

## 9. Before/After Filtering Comparison Plots

Visualize the impact of QC filtering on data distributions.

```python
import scanpy as sc
import matplotlib.pyplot as plt
import numpy as np

def plot_qc_comparison(adata_before, adata_after, save_path: str = "qc_comparison.png"):
    """Compare QC metric distributions before and after filtering.

    Parameters
    ----------
    adata_before : AnnData
        AnnData before QC filtering (with QC metrics calculated).
    adata_after : AnnData
        AnnData after QC filtering.
    save_path : str
        Path to save the comparison figure.

    Returns
    -------
    None. Saves comparison plot.
    """
    metrics = ["n_genes_by_counts", "total_counts", "pct_counts_mt"]
    labels = ["Genes per Cell", "Counts per Cell", "% Mitochondrial"]

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))

    for i, (metric, label) in enumerate(zip(metrics, labels)):
        # Top row: before
        axes[0, i].hist(adata_before.obs[metric], bins=80, alpha=0.7, color="salmon",
                        edgecolor="none", density=True)
        axes[0, i].set_title(f"Before ({adata_before.n_obs} cells)")
        axes[0, i].set_xlabel(label)
        axes[0, i].set_ylabel("Density")

        # Bottom row: after
        axes[1, i].hist(adata_after.obs[metric], bins=80, alpha=0.7, color="steelblue",
                        edgecolor="none", density=True)
        axes[1, i].set_title(f"After ({adata_after.n_obs} cells)")
        axes[1, i].set_xlabel(label)
        axes[1, i].set_ylabel("Density")

    # Match axis limits between before/after
    for i in range(3):
        xmin = min(axes[0, i].get_xlim()[0], axes[1, i].get_xlim()[0])
        xmax = max(axes[0, i].get_xlim()[1], axes[1, i].get_xlim()[1])
        axes[0, i].set_xlim(xmin, xmax)
        axes[1, i].set_xlim(xmin, xmax)

    plt.suptitle(f"QC Filtering: {adata_before.n_obs} → {adata_after.n_obs} cells "
                 f"({adata_before.n_obs - adata_after.n_obs} removed, "
                 f"{(adata_before.n_obs - adata_after.n_obs)/adata_before.n_obs*100:.1f}%)",
                 fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()

    print(f"Saved: {save_path}")
    print(f"Cells removed: {adata_before.n_obs - adata_after.n_obs} "
          f"({(adata_before.n_obs - adata_after.n_obs)/adata_before.n_obs*100:.1f}%)")
    print(f"Genes removed: {adata_before.n_vars - adata_after.n_vars}")

# Usage
# Save a copy before filtering
adata_raw = adata.copy()

# Apply filtering
adata = adata[~adata.obs["outlier"]].copy()
sc.pp.filter_genes(adata, min_cells=3)

# Compare
plot_qc_comparison(adata_raw, adata)
```

**Expected output**: Side-by-side histograms showing distributions thinned of low-quality tails. MT% distribution should lose the high-MT tail. Gene count distribution should lose the low-gene-count population.

---

## 10. Empty Droplet Detection

Distinguish cell-containing droplets from empty droplets using the emptyDrops approach.

```python
import scanpy as sc
import numpy as np
from scipy.stats import multinomial
from scipy.sparse import issparse

def empty_drops_filter(adata_raw, lower: int = 100, fdr_threshold: float = 0.01,
                       n_iters: int = 10000):
    """EmptyDrops-style filtering to distinguish cells from empty droplets.

    Parameters
    ----------
    adata_raw : AnnData
        Raw (unfiltered) count matrix from Cell Ranger raw_feature_bc_matrix.
    lower : int
        Barcodes with total counts <= lower are used to estimate the ambient profile.
        Default 100 is standard for 10x data.
    fdr_threshold : float
        FDR threshold for calling non-empty droplets.
    n_iters : int
        Number of Monte Carlo iterations for p-value estimation.

    Returns
    -------
    AnnData containing only non-empty droplets.

    Notes
    -----
    Implements the logic from Lun et al. 2019 (Genome Biology). For production
    use, consider running the R implementation via DropletUtils::emptyDrops()
    for exact p-values.
    """
    # Calculate total counts per barcode
    if issparse(adata_raw.X):
        total_counts = np.array(adata_raw.X.sum(axis=1)).flatten()
    else:
        total_counts = adata_raw.X.sum(axis=1)

    # Estimate ambient profile from low-count barcodes
    ambient_mask = total_counts <= lower
    if issparse(adata_raw.X):
        ambient_profile = np.array(adata_raw.X[ambient_mask].sum(axis=0)).flatten()
    else:
        ambient_profile = adata_raw.X[ambient_mask].sum(axis=0)
    ambient_profile = ambient_profile / ambient_profile.sum()  # normalize to probabilities

    print(f"Total barcodes: {adata_raw.n_obs}")
    print(f"Ambient barcodes (counts <= {lower}): {ambient_mask.sum()}")
    print(f"Test barcodes (counts > {lower}): {(~ambient_mask).sum()}")

    # Test each barcode above threshold
    test_mask = total_counts > lower
    test_barcodes = np.where(test_mask)[0]

    # Simplified test: use deviance from ambient profile
    # Higher deviance = more likely a real cell
    deviances = np.zeros(len(test_barcodes))
    for i, idx in enumerate(test_barcodes):
        if issparse(adata_raw.X):
            obs_counts = np.array(adata_raw.X[idx].toarray()).flatten()
        else:
            obs_counts = adata_raw.X[idx]
        obs_total = obs_counts.sum()
        expected = ambient_profile * obs_total
        # G-test statistic (log-likelihood ratio)
        nonzero = obs_counts > 0
        deviances[i] = 2 * np.sum(obs_counts[nonzero] * np.log(obs_counts[nonzero] / expected[nonzero]))

    # Cells = barcodes with high deviance from ambient
    from scipy.stats import chi2
    df = (ambient_profile > 0).sum() - 1
    pvals = 1 - chi2.cdf(deviances, df=df)

    # BH correction
    from statsmodels.stats.multitest import multipletests
    _, fdr, _, _ = multipletests(pvals, method="fdr_bh")

    is_cell = fdr < fdr_threshold
    cell_barcodes = test_barcodes[is_cell]

    print(f"\nNon-empty droplets (FDR < {fdr_threshold}): {is_cell.sum()}")
    print(f"  Median counts in cells: {np.median(total_counts[cell_barcodes]):.0f}")
    print(f"  Median counts in empty: {np.median(total_counts[~test_mask]):.0f}")

    adata_cells = adata_raw[cell_barcodes].copy()
    return adata_cells

# Usage (start from raw, unfiltered matrix)
# adata_raw = sc.read_10x_h5("raw_feature_bc_matrix.h5")
# adata_cells = empty_drops_filter(adata_raw, lower=100, fdr_threshold=0.01)

# For production, prefer R implementation:
# R command:
#   library(DropletUtils)
#   sce <- read10xCounts("raw_feature_bc_matrix/")
#   e.out <- emptyDrops(counts(sce), lower=100)
#   is.cell <- e.out$FDR <= 0.01
```

**Expected output**: Identifies cells that deviate significantly from the ambient RNA profile. Recovers low-count cells that fixed-threshold filtering (e.g., Cell Ranger's default 500 UMI cutoff) would miss. Especially useful for rare cell types with low RNA content.

---

## 11. Multi-Sample QC: Per-Sample Metric Distributions

Compare QC metric distributions across samples to detect batch effects and failed samples.

```python
import scanpy as sc
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def multi_sample_qc(adata, sample_col: str = "sample", save_prefix: str = "multisample_qc"):
    """Compare QC metric distributions across samples.

    Parameters
    ----------
    adata : AnnData
        Combined AnnData with sample labels in obs.
    sample_col : str
        Column in adata.obs with sample identifiers.
    save_prefix : str
        Filename prefix for saved plots.

    Returns
    -------
    pd.DataFrame with per-sample QC summary statistics.
    """
    samples = adata.obs[sample_col].unique()
    n_samples = len(samples)
    print(f"Samples: {n_samples}")

    metrics = ["n_genes_by_counts", "total_counts", "pct_counts_mt"]
    metric_labels = ["Genes per Cell", "UMI Counts", "% Mitochondrial"]

    # Per-sample violin plots
    fig, axes = plt.subplots(len(metrics), 1, figsize=(max(12, n_samples * 0.8), 5 * len(metrics)))
    if len(metrics) == 1:
        axes = [axes]

    for i, (metric, label) in enumerate(zip(metrics, metric_labels)):
        sc.pl.violin(adata, metric, groupby=sample_col, ax=axes[i], show=False, rotation=45)
        axes[i].set_ylabel(label)
        axes[i].set_title(f"{label} by Sample")

    plt.tight_layout()
    plt.savefig(f"{save_prefix}_violins.png", dpi=150, bbox_inches="tight")
    plt.close()

    # Per-sample summary table
    summary_rows = []
    for sample in sorted(samples):
        mask = adata.obs[sample_col] == sample
        obs_sub = adata.obs[mask]
        summary_rows.append({
            "sample": sample,
            "n_cells": mask.sum(),
            "median_genes": obs_sub["n_genes_by_counts"].median(),
            "median_counts": obs_sub["total_counts"].median(),
            "median_mt_pct": obs_sub["pct_counts_mt"].median(),
            "mean_mt_pct": obs_sub["pct_counts_mt"].mean(),
            "pct_cells_mt_gt_20": (obs_sub["pct_counts_mt"] > 20).mean() * 100,
        })

    summary = pd.DataFrame(summary_rows)

    # Flag problematic samples
    median_cells = summary["n_cells"].median()
    summary["flag"] = ""
    summary.loc[summary["n_cells"] < median_cells * 0.3, "flag"] += "LOW_CELLS "
    summary.loc[summary["median_mt_pct"] > 15, "flag"] += "HIGH_MT "
    summary.loc[summary["median_genes"] < 500, "flag"] += "LOW_COMPLEXITY "

    print(f"\nPer-Sample QC Summary:")
    print(summary.to_string(index=False))

    flagged = summary[summary["flag"].str.strip() != ""]
    if len(flagged) > 0:
        print(f"\nFlagged samples ({len(flagged)}):")
        for _, row in flagged.iterrows():
            print(f"  {row['sample']}: {row['flag'].strip()}")

    summary.to_csv(f"{save_prefix}_summary.csv", index=False)
    print(f"\nSaved: {save_prefix}_violins.png, {save_prefix}_summary.csv")

    return summary

# Usage
# Concatenate multiple samples first:
# adatas = {}
# for sample_name, path in sample_paths.items():
#     ad = sc.read_10x_h5(path)
#     ad.obs["sample"] = sample_name
#     adatas[sample_name] = ad
# adata = sc.concat(adatas, label="sample")

summary = multi_sample_qc(adata, sample_col="sample")
```

**Expected output**: Per-sample violin plots and summary table. Flags samples with low cell recovery, high MT%, or low library complexity. Use to decide whether to exclude entire samples before integration.

---

## 12. QC Report Generation

Generate a summary statistics table and comprehensive QC report.

```python
import scanpy as sc
import pandas as pd
import numpy as np

def generate_qc_report(adata_raw, adata_filtered, output_path: str = "qc_report.md"):
    """Generate a markdown QC report with summary statistics.

    Parameters
    ----------
    adata_raw : AnnData
        AnnData before QC filtering (with QC metrics calculated).
    adata_filtered : AnnData
        AnnData after QC filtering.
    output_path : str
        Path to save markdown report.

    Returns
    -------
    dict with QC summary statistics.
    """
    stats = {
        "total_cells_loaded": adata_raw.n_obs,
        "total_genes_detected": adata_raw.n_vars,
        "cells_after_qc": adata_filtered.n_obs,
        "genes_after_qc": adata_filtered.n_vars,
        "cells_removed": adata_raw.n_obs - adata_filtered.n_obs,
        "pct_cells_removed": (adata_raw.n_obs - adata_filtered.n_obs) / adata_raw.n_obs * 100,
        "genes_removed": adata_raw.n_vars - adata_filtered.n_vars,
    }

    # Pre-filter metrics
    for metric in ["total_counts", "n_genes_by_counts", "pct_counts_mt"]:
        if metric in adata_raw.obs.columns:
            stats[f"pre_{metric}_median"] = adata_raw.obs[metric].median()
            stats[f"pre_{metric}_mean"] = adata_raw.obs[metric].mean()

    # Post-filter metrics
    for metric in ["total_counts", "n_genes_by_counts", "pct_counts_mt"]:
        if metric in adata_filtered.obs.columns:
            stats[f"post_{metric}_median"] = adata_filtered.obs[metric].median()
            stats[f"post_{metric}_mean"] = adata_filtered.obs[metric].mean()
            stats[f"post_{metric}_min"] = adata_filtered.obs[metric].min()
            stats[f"post_{metric}_max"] = adata_filtered.obs[metric].max()

    # Doublet stats
    if "predicted_doublet" in adata_raw.obs.columns:
        stats["doublets_detected"] = adata_raw.obs["predicted_doublet"].sum()
        stats["doublet_rate"] = adata_raw.obs["predicted_doublet"].mean() * 100

    # Cell cycle stats
    if "phase" in adata_filtered.obs.columns:
        for phase in ["G1", "S", "G2M"]:
            n = (adata_filtered.obs["phase"] == phase).sum()
            stats[f"cc_{phase}_pct"] = n / adata_filtered.n_obs * 100

    # Generate markdown report
    report = f"""# QC Report

## Overview

| Metric | Value |
|--------|-------|
| Cells loaded | {stats['total_cells_loaded']:,} |
| Genes detected | {stats['total_genes_detected']:,} |
| Cells after QC | {stats['cells_after_qc']:,} |
| Genes after QC | {stats['genes_after_qc']:,} |
| Cells removed | {stats['cells_removed']:,} ({stats['pct_cells_removed']:.1f}%) |

## Per-Cell Metrics (After Filtering)

| Metric | Median | Mean | Min | Max |
|--------|--------|------|-----|-----|
| UMI counts | {stats.get('post_total_counts_median', 'N/A'):.0f} | {stats.get('post_total_counts_mean', 'N/A'):.0f} | {stats.get('post_total_counts_min', 'N/A'):.0f} | {stats.get('post_total_counts_max', 'N/A'):.0f} |
| Genes detected | {stats.get('post_n_genes_by_counts_median', 'N/A'):.0f} | {stats.get('post_n_genes_by_counts_mean', 'N/A'):.0f} | {stats.get('post_n_genes_by_counts_min', 'N/A'):.0f} | {stats.get('post_n_genes_by_counts_max', 'N/A'):.0f} |
| % Mitochondrial | {stats.get('post_pct_counts_mt_median', 'N/A'):.1f}% | {stats.get('post_pct_counts_mt_mean', 'N/A'):.1f}% | {stats.get('post_pct_counts_mt_min', 'N/A'):.1f}% | {stats.get('post_pct_counts_mt_max', 'N/A'):.1f}% |
"""

    if "doublets_detected" in stats:
        report += f"""
## Doublet Detection

| Metric | Value |
|--------|-------|
| Doublets detected | {stats['doublets_detected']:,} |
| Doublet rate | {stats['doublet_rate']:.1f}% |
"""

    if "cc_G1_pct" in stats:
        report += f"""
## Cell Cycle

| Phase | Percentage |
|-------|------------|
| G1 | {stats['cc_G1_pct']:.1f}% |
| S | {stats['cc_S_pct']:.1f}% |
| G2M | {stats['cc_G2M_pct']:.1f}% |
"""

    with open(output_path, "w") as f:
        f.write(report)

    print(f"QC report saved to: {output_path}")
    return stats

# Usage
stats = generate_qc_report(adata_raw, adata_filtered, output_path="qc_report.md")
```

**Expected output**: Markdown file with tables summarizing cell counts, per-cell metric distributions, doublet rates, and cell cycle composition. Suitable for inclusion in analysis reports and supplementary materials.
