---
name: temporal-genomics
description: Time-series and temporal pattern analysis in genomics. Time-course differential expression, temporal clustering, circadian rhythms, changepoint detection, GAM modeling, trajectory analysis, dynamic time warping. Use when user mentions time series, time course, temporal, circadian rhythm, oscillation, longitudinal, changepoint, trajectory, pseudotime, dynamic expression, temporal clustering, impulse model, JTK_CYCLE, or temporal genomics.
---

# Temporal Genomics Analysis

Production-ready time-series and temporal pattern analysis methodology for genomic data. The agent writes and executes Python/R code for time-course differential expression, temporal clustering, circadian rhythm detection, changepoint analysis, GAM-based trend modeling, trajectory inference, and dynamic time warping. Uses Open Targets, PubMed, and pathway databases for biological annotation.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_temporal-genomics_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Standard two-condition differential expression -> use `rnaseq-analysis` or `differential-expression`
- Single-cell trajectory analysis exclusively -> use `single-cell-analysis`
- Survival / time-to-event analysis -> use `biostatistics`
- Phylogenetic divergence time estimation -> use `comparative-genomics`
- Longitudinal clinical data (non-genomic) -> use `biostatistics`

## Cross-Reference: Other Skills

- **RNA-seq quantification for time-course** -> use rnaseq-analysis skill
- **Single-cell pseudotime** -> use single-cell-analysis skill
- **Pathway analysis of temporal gene sets** -> use gene-enrichment skill
- **Statistical methods reference** -> use biostatistics skill

## Python/R Environment

Python: `numpy, pandas, scipy, matplotlib, seaborn, scikit-learn, statsmodels`. R: `DESeq2, maSigPro, limma, mgcv, rain`. Install at runtime as needed.

## Data Input Formats

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def load_timecourse_data(counts_file, metadata_file):
    """Load time-course expression data with sample metadata."""
    counts = pd.read_csv(counts_file, sep="\t", index_col=0)
    meta = pd.read_csv(metadata_file, sep="\t")

    # Validate required columns
    required = ["sample_id", "timepoint"]
    for col in required:
        if col not in meta.columns:
            raise ValueError(f"Metadata missing required column: {col}")

    # Sort by timepoint
    meta = meta.sort_values("timepoint")
    timepoints = sorted(meta["timepoint"].unique())
    n_reps = meta.groupby("timepoint").size()

    print(f"Genes: {counts.shape[0]:,}")
    print(f"Samples: {counts.shape[1]}")
    print(f"Timepoints: {len(timepoints)} ({timepoints})")
    print(f"Replicates per timepoint: {n_reps.to_dict()}")
    return counts, meta

def validate_experimental_design(meta):
    """Check experimental design quality for time-series analysis."""
    timepoints = sorted(meta["timepoint"].unique())
    n_tp = len(timepoints)
    reps = meta.groupby("timepoint").size()

    print("Experimental Design Assessment:")
    print("=" * 50)

    warnings = []
    if n_tp < 4:
        warnings.append("< 4 timepoints: Cannot reliably detect temporal patterns")
        warnings.append("  Minimum 4 for maSigPro, 6+ recommended")
    if reps.min() < 2:
        warnings.append(f"Some timepoints have < 2 replicates (min: {reps.min()})")
        warnings.append("  Replicates critical for statistical testing")
    if reps.std() > 1:
        warnings.append("Unbalanced design: replicates vary across timepoints")

    # Check spacing
    intervals = np.diff(timepoints)
    if len(set(intervals)) > 1:
        print(f"  Sampling intervals: {intervals} (irregular)")
        print("  Irregular spacing is fine for GAM/maSigPro, but problematic for FFT-based methods")
    else:
        print(f"  Sampling interval: {intervals[0]} (regular)")

    for w in warnings:
        print(f"  WARNING: {w}")

    print()
    print("Design recommendations:")
    print(f"  Timepoints: {n_tp} (minimum 4, ideal 6-8+)")
    print(f"  Replicates: {reps.min()}-{reps.max()} per timepoint (ideal: >= 3)")
    print(f"  Total samples: {len(meta)}")
```

---

## Analysis Pipeline

### Phase 1: Time-Course Differential Expression

```python
def deseq2_lrt_timecourse(counts, meta, time_col="timepoint"):
    """DESeq2 Likelihood Ratio Test for time-course data."""
    r_script = f"""
    library(DESeq2)

    # LRT: Tests whether time has ANY effect on expression
    # Full model: ~ timepoint (or ~ spline(time, df=3) for continuous)
    # Reduced model: ~ 1 (intercept only)

    dds <- DESeqDataSetFromMatrix(
        countData = counts,
        colData = meta,
        design = ~ {time_col}
    )

    # LRT: compare full vs reduced model
    dds <- DESeq(dds, test = "LRT", reduced = ~ 1)
    res <- results(dds)

    # Genes with significant temporal variation
    sig_genes <- subset(res, padj < 0.05)
    cat(sprintf("Temporally varying genes: %d (padj < 0.05)\\n", nrow(sig_genes)))

    # For continuous time with splines:
    # library(splines)
    # design = ~ ns(time, df=3)  # natural splines
    # reduced = ~ 1
    """

    print("DESeq2 LRT for Time-Course:")
    print("  H0: Gene expression does not change over time")
    print("  H1: Gene expression varies with time")
    print("  LRT compares models, not specific contrasts")
    print("  Advantage: Single test captures any temporal pattern (not just linear)")
    print()
    print("  Design choices:")
    print("    Factorial (timepoint as factor): Most flexible, each timepoint independent")
    print("    Spline (continuous time): Smooth trends, fewer parameters")
    print("    Polynomial: Linear/quadratic trends (rigid)")
    print("  Recommendation: Factor for <= 8 timepoints, splines for more")
    return r_script

def masigpro_analysis(counts, meta, degree=3, time_col="timepoint",
                      group_col="condition"):
    """maSigPro: two-step regression for time-course data."""
    r_script = f"""
    library(maSigPro)

    # Step 1: Define experimental design
    design <- make.design.matrix(
        meta[, c("{time_col}", "{group_col}", "replicate")],
        degree = {degree}  # polynomial degree
    )

    # Step 2: Global regression (identify temporally significant genes)
    fit <- p.vector(counts, design,
                    Q = 0.05,          # FDR threshold
                    MT.adjust = "BH",  # Multiple testing correction
                    min.obs = 20)      # Minimum observations

    # Step 3: Stepwise regression (find best model for each gene)
    tstep <- T.fit(fit,
                   step.method = "backward",
                   alfa = 0.05)

    # Step 4: Get significant gene clusters
    sigs <- get.siggenes(tstep, rsq = 0.6, vars = "groups")
    # rsq = 0.6: Minimum R-squared for a gene to be considered well-fit
    """

    print("maSigPro Analysis:")
    print("  Two-step regression approach:")
    print("  Step 1: Global regression to select significant genes (p.vector)")
    print("  Step 2: Variable selection to find best model (T.fit)")
    print()
    print("  Polynomial degree:")
    print("    degree=2: Quadratic (up-down or down-up patterns)")
    print("    degree=3: Cubic (more complex patterns)")
    print("    degree=4: Quartic (maximum for most designs)")
    print("    Rule: degree < (n_timepoints - 1)")
    print()
    print("  Group comparisons:")
    print("    If group_col provided: Tests for differential temporal patterns")
    print("    between conditions (e.g., treated vs control over time)")
    print()
    print("  Advantages over DESeq2 LRT:")
    print("    - Explicitly models temporal patterns (polynomial)")
    print("    - Can compare temporal profiles between groups")
    print("    - Built-in clustering of temporal patterns")
    return r_script

def impulsede2_analysis(counts, meta, time_col="timepoint"):
    """ImpulseDE2: impulse model for gene activation/repression kinetics."""
    r_script = """
    library(ImpulseDE2)

    # ImpulseDE2 fits a double-sigmoid (impulse) model:
    # f(t) = h0 + (h1 - h0) * sigmoid(t, t1, beta1) * sigmoid(t, t2, beta2)
    # Captures: onset, peak, and offset of expression

    obj <- runImpulseDE2(
        matCountData = counts,
        dfAnnotation = meta,
        boolCaseCtrl = TRUE,      # Case-control design
        vecConfounders = NULL,
        scaNProc = 4,
        scaQThres = 0.05
    )

    # Output: Impulse model parameters per gene
    # h0: baseline expression
    # h1: peak expression
    # h2: final expression
    # t1: onset time
    # t2: offset time
    # beta1, beta2: slope parameters
    """

    print("ImpulseDE2 Model:")
    print("  Double-sigmoid captures transient expression changes:")
    print("  - Activation: h0 (low) -> h1 (high) -> h2 (return to baseline or new level)")
    print("  - Repression: h0 (high) -> h1 (low) -> h2 (recovery or maintained)")
    print()
    print("  Model parameters:")
    print("    h0, h1, h2: Expression levels at baseline, peak, final")
    print("    t1, t2: Transition timepoints")
    print("    beta1, beta2: Slopes of transitions")
    print()
    print("  Use cases:")
    print("    - Drug response kinetics (onset/offset)")
    print("    - Immune response (activation/resolution)")
    print("    - Differentiation (state transitions)")
    print("    - Stress response (acute/recovery)")
    return r_script
```

### Phase 2: Temporal Clustering

```python
def stem_clustering(expression_matrix, n_profiles=50, n_timepoints=None):
    """STEM: Short Time-series Expression Miner."""
    print("STEM Clustering:")
    print("=" * 50)
    print("  Designed specifically for short time series (3-8 timepoints)")
    print("  Algorithm:")
    print("  1. Define a set of model temporal profiles (e.g., up-up-down, etc.)")
    print("  2. Assign each gene to the closest model profile")
    print("  3. Test which profiles have more genes than expected (permutation)")
    print("  4. Significant profiles = biologically meaningful temporal patterns")
    print()
    print(f"  n_profiles={n_profiles}: Number of candidate model profiles")
    print("  Higher n_profiles -> finer resolution but more multiple testing")
    print()
    print("  Output:")
    print("    - Significant profiles (p < 0.05 after Bonferroni)")
    print("    - Gene assignments to each profile")
    print("    - Profile visualization (expression trend + gene membership)")
    print()
    print("  Limitation: Requires equal-spacing or treats timepoints as ordinal")
    print("  For unequal spacing, use GP-based clustering or GAMs")

def gp_clustering(expression_matrix, timepoints, n_clusters=10):
    """Gaussian Process-based temporal clustering."""
    print("Gaussian Process (GP) Clustering:")
    print("=" * 50)
    print("  Models each gene's expression as a smooth function of time")
    print("  Handles irregular sampling naturally")
    print()
    print("  GP kernel selection:")
    print("    RBF (squared exponential): Smooth, infinitely differentiable")
    print("      Good default for biological processes")
    print("    Matern 3/2: Less smooth, allows sharper transitions")
    print("      Better for rapid expression changes")
    print("    Periodic: For circadian/oscillatory patterns")
    print()
    print("  Clustering approach:")
    print("    1. Fit GP to each gene (learn lengthscale, variance)")
    print("    2. Compute GP-based distance between genes")
    print("    3. Cluster using hierarchical clustering or DP mixture model")
    print()

    # Python implementation with GPy
    python_code = """
    import GPy
    from sklearn.cluster import AgglomerativeClustering

    # Fit GP per gene
    kernel = GPy.kern.RBF(1, lengthscale=1.0, variance=1.0)
    X = timepoints.reshape(-1, 1)

    for gene in expression_matrix.index:
        Y = expression_matrix.loc[gene].values.reshape(-1, 1)
        m = GPy.models.GPRegression(X, Y, kernel.copy())
        m.optimize()
        # Extract hyperparameters: lengthscale, variance
    """
    return python_code

def temporal_heatmap(expression_matrix, gene_order, timepoints,
                     output="temporal_heatmap.png"):
    """Generate heatmap with temporal ordering and clustering."""
    fig, ax = plt.subplots(figsize=(12, 10))

    # Z-score normalize per gene
    z_scores = expression_matrix.subtract(expression_matrix.mean(axis=1), axis=0)
    z_scores = z_scores.div(expression_matrix.std(axis=1), axis=0)

    sns.heatmap(z_scores.loc[gene_order], cmap="RdBu_r", center=0,
                xticklabels=timepoints, yticklabels=False,
                cbar_kws={"label": "Z-score"}, ax=ax)
    ax.set_xlabel("Timepoint")
    ax.set_ylabel("Genes (clustered)")
    ax.set_title("Temporal Expression Heatmap")
    plt.tight_layout()
    plt.savefig(output, dpi=150, bbox_inches="tight")
    plt.show()
```

### Phase 3: Circadian Rhythm Detection

```python
def jtk_cycle_analysis(expression_matrix, timepoints, period_range=(20, 28)):
    """JTK_CYCLE: non-parametric circadian rhythm detection."""
    r_script = """
    source("JTK_CYCLEv3.1.R")

    # JTK_CYCLE parameters
    jtkdist(n_timepoints, n_reps)   # Generate null distribution
    periods <- seq(20, 28, by=2)     # Test periods (hours)
    jtk.init(periods, n_timepoints)

    # Run for each gene
    results <- apply(expression_matrix, 1, function(x) {
        jtkx(x)
        return(c(JTK.ADJP, JTK.PERIOD, JTK.LAG, JTK.AMP))
    })
    """

    print("JTK_CYCLE Analysis:")
    print("=" * 50)
    print("  Non-parametric test for rhythmic expression")
    print("  Tests for periodicity at specified period lengths")
    print()
    print("  Key outputs per gene:")
    print("    ADJ.P: Adjusted p-value (BH correction)")
    print("    PER: Best-fit period (hours)")
    print("    LAG/PHASE: Time of peak expression (hours)")
    print("    AMP: Amplitude (fold-change from trough to peak)")
    print()
    print("  Design requirements:")
    print("    Minimum: 2 full cycles (48h for circadian)")
    print("    Sampling: Every 2-4 hours")
    print("    Replicates: >= 2 per timepoint recommended")
    print()
    print("  Interpretation:")
    print("    padj < 0.05: Significantly rhythmic")
    print("    Amplitude > 0.5 (log2): Biologically meaningful oscillation")
    print("    Period = 24h: Circadian; period != 24h: Ultradian/infradian")

def rain_analysis(expression_matrix, timepoints, period=24):
    """RAIN: Rhythmicity Analysis Incorporating Non-parametric methods."""
    r_script = f"""
    library(rain)

    results <- rain(t(expression_matrix),
                    deltat = diff(timepoints)[1],  # Sampling interval (hours)
                    period = {period},              # Expected period
                    measure.sequence = rep(n_reps, n_timepoints),
                    method = "independent",
                    peak.border = c(0.1, 0.9))     # Asymmetric peak allowed

    # RAIN advantages over JTK_CYCLE:
    # 1. Detects asymmetric waveforms (not just sinusoidal)
    # 2. Handles unequal sampling
    # 3. More sensitive to non-sinusoidal oscillations
    """

    print("RAIN vs JTK_CYCLE:")
    print("  RAIN: Detects asymmetric rhythms (e.g., sharp rise, slow decay)")
    print("  JTK_CYCLE: Faster, well-validated, but assumes symmetry")
    print("  Use both and compare: concordant results are most reliable")
    return r_script

def cosinor_analysis(expression_vector, timepoints, period=24):
    """Cosinor regression for circadian parameter estimation."""
    from scipy.optimize import curve_fit

    def cosinor_model(t, mesor, amplitude, acrophase):
        """Cosinor: y(t) = mesor + amplitude * cos(2*pi*t/period + acrophase)"""
        return mesor + amplitude * np.cos(2 * np.pi * t / period + acrophase)

    print("Cosinor Regression:")
    print("  Model: y(t) = MESOR + A * cos(2*pi*t/T + phi)")
    print("  Parameters:")
    print("    MESOR: Midline Estimating Statistic Of Rhythm (mean level)")
    print("    A (Amplitude): Half the peak-to-trough difference")
    print("    phi (Acrophase): Time of peak (in radians)")
    print("    T (Period): Fixed (usually 24h for circadian)")
    print()
    print("  Advantages: Provides interpretable parameters (amplitude, phase)")
    print("  Limitations: Assumes sinusoidal waveform")
    print("  Extension: Cosinor2 (harmonic terms for non-sinusoidal)")

    # Fit
    try:
        popt, pcov = curve_fit(cosinor_model, timepoints, expression_vector,
                               p0=[np.mean(expression_vector), 1.0, 0.0])
        mesor, amplitude, acrophase = popt
        phase_hours = (-acrophase / (2 * np.pi) * period) % period
        print(f"\n  Fitted parameters:")
        print(f"    MESOR: {mesor:.3f}")
        print(f"    Amplitude: {amplitude:.3f}")
        print(f"    Acrophase: {phase_hours:.1f} hours")
    except RuntimeError:
        print("  Fit did not converge - gene may not be rhythmic")
    return popt if 'popt' in dir() else None
```

### Phase 4: Changepoint Detection

```python
def changepoint_detection(time_series, method="pelt"):
    """Detect changepoints in temporal expression data."""
    print("Changepoint Detection Methods:")
    print("=" * 50)
    print()

    if method == "pelt":
        python_code = """
        import ruptures as rpt

        # PELT (Pruned Exact Linear Time)
        algo = rpt.Pelt(model="rbf", min_size=3, jump=1).fit(signal)
        result = algo.predict(pen=penalty)
        # pen (penalty): Controls sensitivity
        #   Higher penalty -> fewer changepoints (conservative)
        #   Lower penalty -> more changepoints (sensitive)
        #   BIC: pen = n_params * log(n) (good default)
        """
        print("  PELT (Pruned Exact Linear Time):")
        print("    - Exact algorithm, O(n) on average")
        print("    - Requires penalty parameter (controls number of changepoints)")
        print("    - Penalty selection: BIC, AIC, or cross-validation")

    elif method == "binseg":
        python_code = """
        import ruptures as rpt

        # Binary Segmentation
        algo = rpt.Binseg(model="l2", min_size=3, jump=1).fit(signal)
        result = algo.predict(n_bkps=5)  # Specify number of changepoints
        """
        print("  Binary Segmentation:")
        print("    - Approximate, O(n*log(n))")
        print("    - Specify number of changepoints directly")
        print("    - Less accurate than PELT but faster")

    elif method == "bottomup":
        python_code = """
        import ruptures as rpt

        # Bottom-Up
        algo = rpt.BottomUp(model="l2", min_size=3, jump=1).fit(signal)
        result = algo.predict(n_bkps=5)
        """
        print("  Bottom-Up:")
        print("    - Merges adjacent segments iteratively")
        print("    - Good when many small changes expected")

    print()
    print("  Cost function selection:")
    print("    'l2': Mean shift (detect changes in mean level)")
    print("    'l1': Median shift (robust to outliers)")
    print("    'rbf': Kernel-based (detects distributional changes)")
    print("    'linear': Linear trend changes")
    print("    'normal': Mean and variance changes simultaneously")
    print()
    print("  Application to genomics:")
    print("    - Detect treatment response onset/offset times")
    print("    - Identify developmental stage transitions")
    print("    - Find breakpoints in longitudinal expression data")
    return python_code

def segmented_regression(timepoints, expression, n_breakpoints=1):
    """Segmented (piecewise) linear regression."""
    r_script = f"""
    library(segmented)

    # Fit linear model
    lm_fit <- lm(expression ~ timepoint, data = df)

    # Fit segmented model with {n_breakpoints} breakpoint(s)
    seg_fit <- segmented(lm_fit,
                         seg.Z = ~ timepoint,
                         npsi = {n_breakpoints},  # number of breakpoints
                         control = seg.control(it.max = 100))

    # Results
    summary(seg_fit)
    breakpoint <- seg_fit$psi[, "Est."]  # Estimated breakpoint
    slopes <- slope(seg_fit)              # Slopes of each segment
    """

    print("Segmented Regression:")
    print("  Fits piecewise linear model with breakpoints")
    print("  Automatically estimates breakpoint location")
    print("  Useful for: dose-response transitions, developmental switches")
    print(f"  npsi={n_breakpoints}: Number of breakpoints to fit")
    print("  Davies test: Tests whether a breakpoint exists (vs simple linear)")
    return r_script
```

### Phase 5: GAM Modeling

```python
def gam_temporal_modeling(expression_df, time_col="timepoint", group_col=None):
    """Generalized Additive Models for smooth temporal trends."""
    r_script = """
    library(mgcv)

    # Basic GAM: smooth temporal trend
    gam_fit <- gam(expression ~ s(timepoint, k=10, bs="cr"),
                   data = df, family = nb(), method = "REML")

    # With group comparison:
    gam_fit_group <- gam(expression ~ s(timepoint, by=condition, k=10, bs="cr")
                         + condition,
                         data = df, family = nb(), method = "REML")

    # Summary and diagnostics
    summary(gam_fit)
    gam.check(gam_fit)  # Residual diagnostics
    """

    print("GAM for Temporal Genomics:")
    print("=" * 50)
    print()
    print("  Smooth function s() specification:")
    print("    s(time, k=10): Thin plate regression spline, max 10 basis functions")
    print("    s(time, k=10, bs='cr'): Cubic regression spline")
    print("    s(time, k=10, bs='cc'): Cyclic cubic spline (for periodic data)")
    print("    s(time, k=10, bs='tp'): Thin plate spline (default, isotropic)")
    print()
    print("  Basis dimension k:")
    print("    k sets MAXIMUM flexibility (actual smoothness selected by penalty)")
    print("    k=3-4: Nearly linear (few inflection points)")
    print("    k=5-8: Moderate flexibility (default recommendation)")
    print("    k=10-15: High flexibility (many timepoints)")
    print("    Rule: k < n_unique_timepoints")
    print("    If k is too low: underfitting (misses real patterns)")
    print("    If k is too high: computational cost, but penalty prevents overfitting")
    print()
    print("  Method:")
    print("    REML: Restricted Maximum Likelihood (recommended, less prone to overfitting)")
    print("    GCV: Generalized Cross-Validation (tends to undersmooth)")
    print()
    print("  Family:")
    print("    nb(): Negative binomial (for count data, e.g., RNA-seq)")
    print("    gaussian(): For log-transformed normalized expression")
    print("    tw(): Tweedie (flexible for various distributions)")
    print()
    print("  Group comparison:")
    print("    s(time, by=condition): Separate smooth per condition")
    print("    Test: Does the difference smooth deviate from zero?")
    print("    Use: itsadug::plot_diff() for visualizing condition differences")
    return r_script

def gam_qc_checks():
    """GAM diagnostic checks."""
    print("GAM Diagnostic Checks:")
    print("  1. gam.check(): Residual plots, basis dimension test")
    print("     - k-index < 1: k may be too low, increase k")
    print("     - p-value < 0.05: k is likely too low")
    print("  2. Residual patterns: Should be random, no temporal autocorrelation")
    print("  3. Effective degrees of freedom (edf):")
    print("     - edf close to 1: Nearly linear (could use lm instead)")
    print("     - edf close to k-1: May need higher k")
    print("  4. Concurvity: Check for confounding between smooths")
    print("     - concurvity(gam_fit, full=TRUE)")
    print("     - Values > 0.8: Problematic confounding")
```

### Phase 6: Trajectory Modeling

```python
def pseudotime_vs_realtime():
    """Compare pseudotime and real time approaches."""
    print("Pseudotime vs Real Time:")
    print("=" * 50)
    print()
    print("  Pseudotime (single-cell):")
    print("    - Infers ordering from transcriptomic similarity")
    print("    - No actual time information needed")
    print("    - Tools: Monocle3, Slingshot, PAGA, DPT")
    print("    - Use when: Single-cell data, continuous differentiation")
    print("    - Limitation: Cannot determine absolute time scale")
    print()
    print("  Real time (bulk or single-cell):")
    print("    - Actual experimental timepoints")
    print("    - Use methods in this skill (DESeq2 LRT, maSigPro, GAM)")
    print("    - Advantage: Quantitative timing, rate estimation")
    print("    - Limitation: Discrete snapshots, population-averaged (if bulk)")
    print()
    print("  Combining both:")
    print("    1. Collect single-cell data at real timepoints")
    print("    2. Infer pseudotime within each timepoint")
    print("    3. Anchor pseudotime to real time for calibration")
    print("    4. Tools: Waddington-OT, moscot")

def dynamic_time_warping(expr_a, expr_b, timepoints):
    """Dynamic Time Warping for temporal expression pattern comparison."""
    from scipy.spatial.distance import euclidean

    print("Dynamic Time Warping (DTW):")
    print("=" * 50)
    print()
    print("  Compares two temporal expression profiles allowing for")
    print("  non-linear time warping (stretching/compressing)")
    print()
    print("  Applications:")
    print("    - Compare gene expression dynamics across species")
    print("    - Align developmental stages between organisms")
    print("    - Find genes with similar temporal patterns but shifted timing")
    print("    - Cluster genes by temporal shape (DTW distance)")
    print()

    python_code = """
    from dtaidistance import dtw
    import numpy as np

    # Compute DTW distance
    distance = dtw.distance(expr_a, expr_b)

    # Get warping path
    path = dtw.warping_path(expr_a, expr_b)

    # DTW distance matrix for clustering
    from dtaidistance import dtw_ndim
    ds = dtw.distance_matrix(expression_matrix)

    # Hierarchical clustering on DTW distances
    from scipy.cluster.hierarchy import linkage, fcluster
    Z = linkage(ds, method='ward')
    clusters = fcluster(Z, t=n_clusters, criterion='maxclust')
    """

    print("  Parameters:")
    print("    window: Sakoe-Chiba band width (limits warping)")
    print("      None: No constraint (global warping)")
    print("      int: Maximum warping distance in timepoints")
    print("    Recommendation: window = n_timepoints // 3")
    return python_code
```

### Phase 7: Phase and Amplitude Estimation

```python
def phase_amplitude_analysis(expression_matrix, timepoints, period=24):
    """Estimate phase and amplitude for oscillatory genes."""

    def circular_mean_phase(phases):
        """Calculate circular mean of phase angles."""
        sin_mean = np.mean(np.sin(phases))
        cos_mean = np.mean(np.cos(phases))
        return np.arctan2(sin_mean, cos_mean)

    print("Phase and Amplitude Analysis:")
    print("=" * 50)
    print()
    print("  Phase: Time of peak expression within the cycle")
    print("    Circular variable (0-24h for circadian)")
    print("    Requires circular statistics for averaging/comparison")
    print()
    print("  Amplitude: Magnitude of oscillation")
    print("    Relative amplitude = (max - min) / mean")
    print("    Robust amplitude = (Q75 - Q25) / median")
    print()
    print("  Phase enrichment analysis:")
    print("    1. Fit cosinor to each rhythmic gene -> get phase")
    print("    2. Test whether genes in a pathway cluster at specific phase")
    print("    3. Rayleigh test for phase uniformity (circular statistics)")
    print("    4. Watson-Williams test for phase differences between conditions")
    print()

    def plot_phase_distribution(phases, gene_groups, output="phase_plot.png"):
        """Polar plot of gene phase distribution."""
        fig, ax = plt.subplots(subplot_kw=dict(projection='polar'), figsize=(8, 8))

        for group_name, group_phases in gene_groups.items():
            theta = np.array(group_phases) / period * 2 * np.pi
            ax.hist(theta, bins=24, alpha=0.5, label=group_name)

        ax.set_theta_zero_location("N")  # 0h at top
        ax.set_theta_direction(-1)  # Clockwise
        ax.set_xticks(np.linspace(0, 2*np.pi, 24, endpoint=False))
        ax.set_xticklabels([f"{h}h" for h in range(24)])
        ax.set_title("Gene Phase Distribution")
        ax.legend(loc="upper right")
        plt.tight_layout()
        plt.savefig(output, dpi=150, bbox_inches="tight")
        plt.show()

    print("  Visualization options:")
    print("    Polar/rose plot: Phase distribution of rhythmic genes")
    print("    Ribbon plot: Expression trend with confidence interval")
    print("    Heatmap: Genes ordered by phase (columns = time)")
```

### Phase 8: Visualization

```python
def temporal_visualizations(expression_df, meta, sig_genes, output_dir="plots"):
    """Generate comprehensive temporal visualizations."""

    def ribbon_plot(gene_id, expression_df, meta, output=None):
        """Expression trend with confidence ribbon."""
        fig, ax = plt.subplots(figsize=(10, 5))
        # Calculate mean and SEM per timepoint
        gene_data = expression_df.loc[gene_id]
        for condition in meta["condition"].unique():
            cond_samples = meta[meta["condition"] == condition]["sample_id"]
            tp_means = []
            tp_sems = []
            for tp in sorted(meta["timepoint"].unique()):
                tp_samples = meta[(meta["condition"] == condition) &
                                  (meta["timepoint"] == tp)]["sample_id"]
                values = gene_data[tp_samples]
                tp_means.append(values.mean())
                tp_sems.append(values.sem())

            timepoints = sorted(meta["timepoint"].unique())
            tp_means = np.array(tp_means)
            tp_sems = np.array(tp_sems)
            ax.plot(timepoints, tp_means, "-o", label=condition)
            ax.fill_between(timepoints, tp_means - tp_sems, tp_means + tp_sems, alpha=0.2)

        ax.set_xlabel("Timepoint")
        ax.set_ylabel("Expression")
        ax.set_title(f"{gene_id} Expression Over Time")
        ax.legend()
        plt.tight_layout()
        if output:
            plt.savefig(output, dpi=150, bbox_inches="tight")
        plt.show()

    print("Temporal Visualization Guide:")
    print("  1. Ribbon plot: Mean +/- SEM per timepoint per condition")
    print("  2. Heatmap: Genes (rows) x Timepoints (columns), Z-scored")
    print("     Order genes by cluster, phase, or peak time")
    print("  3. Phase plot (polar): For circadian data")
    print("  4. Impulse fit: Overlay fitted impulse model on data")
    print("  5. Cluster profiles: Averaged expression per temporal cluster")
    print("  6. Sankey/alluvial: Track cluster membership changes")
```

---

## Parameter Reference Tables

### Method Selection Guide

| Method | Min Timepoints | Replicates | Pattern Type | Best For |
|--------|---------------|------------|-------------|----------|
| DESeq2 LRT | 3 | >= 2 | Any | General temporal variation |
| maSigPro | 4 | >= 2 | Polynomial | Group x time interaction |
| ImpulseDE2 | 4 | >= 2 | Impulse | Transient activation/repression |
| JTK_CYCLE | 6 (2 cycles) | >= 1 | Periodic | Circadian rhythms |
| RAIN | 6 (2 cycles) | >= 1 | Periodic (asymmetric) | Non-sinusoidal rhythms |
| GAM (mgcv) | 5+ | >= 2 | Smooth/flexible | Complex non-linear trends |
| STEM | 3-8 | >= 1 | Model profiles | Short time series |

### Circadian Analysis Requirements

| Parameter | Minimum | Ideal | Notes |
|-----------|---------|-------|-------|
| Duration | 48h (2 cycles) | 72h+ (3 cycles) | More cycles = more power |
| Sampling interval | 4h | 2h | Higher resolution improves detection |
| Replicates per timepoint | 1 | 3+ | Critical for statistical power |
| Total samples | 12 | 36+ | Duration x sampling x replicates |
| Entrainment | 12:12 LD | 12:12 LD then DD | DD for intrinsic rhythms |

---

## Evidence Grading

| Tier | Evidence Type | Example |
|------|-------------|---------|
| **T1** | Replicated time-course with validation | RT-qPCR validation of temporal genes |
| **T2** | Multiple method concordance | DESeq2 LRT + maSigPro agreeing |
| **T3** | Single method, adequate design | GAM fit with >= 6 timepoints, 3 reps |
| **T4** | Underpowered or unreplicated | < 3 timepoints or no replicates |

---

## Multi-Agent Workflow Examples

**"Identify genes with circadian expression patterns in liver tissue"**
1. Temporal Genomics -> JTK_CYCLE + RAIN analysis, phase/amplitude estimation
2. Gene Enrichment -> Pathway enrichment of phase-specific gene sets
3. Disease Research -> Known circadian genes (clock genes) as positive controls

**"Characterize transcriptional response kinetics to drug treatment"**
1. Temporal Genomics -> ImpulseDE2 for onset/offset, maSigPro for temporal clusters
2. RNA-seq Analysis -> Per-timepoint normalization and quality control
3. Gene Enrichment -> Temporal pathway activation waves (early vs late response)

**"Compare developmental gene expression trajectories between wild-type and mutant"**
1. Temporal Genomics -> maSigPro with group x time interaction, DTW for pattern shifts
2. Gene Enrichment -> Stage-specific pathway analysis
3. Differential Expression -> Pairwise comparisons at each timepoint for validation

## Completeness Checklist

- [ ] Experimental design validated (timepoints, replicates, spacing)
- [ ] Appropriate method selected for design and question
- [ ] Time-course differential expression performed (DESeq2 LRT or equivalent)
- [ ] Temporal clustering applied to significant genes
- [ ] Circadian analysis performed if relevant (JTK_CYCLE or RAIN)
- [ ] GAM models fit for key genes or pathways
- [ ] Temporal visualizations generated (heatmap, ribbon plots, phase plots)
- [ ] Multiple testing correction applied
- [ ] Biological validation strategy discussed
- [ ] Evidence tier assigned to all key findings (T1-T4)
- [ ] Report file created with all sections populated (no `[Analyzing...]` remaining)
