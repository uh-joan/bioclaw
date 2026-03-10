---
name: flow-cytometry
description: Flow cytometry and mass cytometry (CyTOF) data analysis. FCS file processing, compensation, gating, clustering, dimensionality reduction, differential abundance. Use when user mentions flow cytometry, CyTOF, mass cytometry, FACS, FlowSOM, Phenograph, gating, compensation, spillover matrix, fluorescence-activated cell sorting, immune phenotyping, marker panel, or cell population analysis.
---

# Flow Cytometry Analysis

Production-ready flow and mass cytometry data analysis methodology. The agent writes and executes R/Python code for FCS file processing, compensation, transformation, manual and automated gating, unsupervised clustering, dimensionality reduction, differential analysis, and batch correction. Covers both fluorescence-based flow cytometry and CyTOF/mass cytometry workflows.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_flow-cytometry_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Single-cell RNA-seq clustering and annotation -> use `single-cell-analysis`
- CITE-seq (protein + RNA) -> use `single-cell-analysis` with CITE-seq module
- Spatial transcriptomics / imaging mass cytometry (IMC) -> use `spatial-transcriptomics`
- Microscopy image analysis -> use `image-analysis`
- Bulk proteomics -> use `proteomics-analysis`

## Cross-Reference: Other Skills

- **Single-cell transcriptomics integration** -> use single-cell-analysis skill
- **Immune cell type marker reference** -> use immune-repertoire-analysis skill
- **Statistical testing framework** -> use biostatistics skill

## R Environment

Core packages: `flowCore, FlowSOM, CATALYST, diffcyt, ggcyto, CytoNorm`. Install at runtime:
```r
if (!requireNamespace("BiocManager", quietly = TRUE)) install.packages("BiocManager")
BiocManager::install(c("flowCore", "FlowSOM", "CATALYST", "diffcyt", "ggcyto"))
```

For Python: `flowio, fcsparser, scanpy, phenograph`. Install: `pip install flowio fcsparser phenograph`.

## Data Input Formats

```r
library(flowCore)
library(FlowSOM)

load_fcs_data <- function(fcs_dir, pattern = "\\.fcs$") {
    fcs_files <- list.files(fcs_dir, pattern = pattern, full.names = TRUE)
    cat(sprintf("Found %d FCS files\n", length(fcs_files)))

    # Read as flowSet
    fs <- read.flowSet(fcs_files, transformation = FALSE, truncate_max_range = FALSE)

    # Summary
    cat(sprintf("Channels: %d\n", ncol(fs[[1]])))
    cat(sprintf("Total events: %s\n", format(sum(sapply(fs, nrow)), big.mark = ",")))

    # List channels
    channels <- colnames(fs[[1]])
    markers <- pData(parameters(fs[[1]]))$desc
    channel_info <- data.frame(channel = channels, marker = markers, stringsAsFactors = FALSE)
    print(channel_info)

    return(fs)
}

# Python alternative
def load_fcs_python(fcs_path):
    """Load FCS file using flowio."""
    import flowio
    fcs = flowio.FlowData(fcs_path)
    n_events = fcs.event_count
    channels = [fcs.channels[k]["PnN"] for k in sorted(fcs.channels.keys())]
    markers = [fcs.channels[k].get("PnS", "") for k in sorted(fcs.channels.keys())]
    data = np.array(fcs.events).reshape(n_events, len(channels))
    df = pd.DataFrame(data, columns=channels)
    print(f"Events: {n_events:,}, Channels: {len(channels)}")
    return df, channels, markers
```

---

## Analysis Pipeline

### Phase 1: Quality Control

```r
flow_qc <- function(fs) {
    # Doublet discrimination: FSC-A vs FSC-H
    cat("=== Flow Cytometry QC ===\n")

    qc_results <- lapply(seq_along(fs), function(i) {
        ff <- fs[[i]]
        n_total <- nrow(ff)

        # Time vs signal stability
        if ("Time" %in% colnames(ff)) {
            time_data <- exprs(ff)[, "Time"]
            # Check for flow rate anomalies
            time_bins <- cut(time_data, breaks = 20)
            events_per_bin <- table(time_bins)
            cv_flow <- sd(events_per_bin) / mean(events_per_bin)
            cat(sprintf("  File %d: %s events, flow rate CV: %.2f\n",
                        i, format(n_total, big.mark = ","), cv_flow))
        }

        list(file = sampleNames(fs)[i], n_events = n_total)
    })

    cat("\nQC Checkpoints:\n")
    cat("  1. Doublet discrimination: Gate FSC-A vs FSC-H (singlets on diagonal)\n")
    cat("  2. Viability: Exclude dead cells (viability dye positive)\n")
    cat("  3. Time stability: Constant event rate over acquisition time\n")
    cat("  4. Margin events: Exclude events at detector max/min\n")
    cat("  5. Bead check: Verify instrument calibration beads\n")

    return(qc_results)
}

doublet_discrimination <- function(ff) {
    cat("Doublet Discrimination Strategy:\n")
    cat("  Step 1: FSC-A vs FSC-H gate (singlets cluster on diagonal)\n")
    cat("  Step 2: SSC-A vs SSC-H (optional, additional doublet removal)\n")
    cat("  Rationale: Doublets have disproportionately high Area vs Height\n")
    cat("  Expected singlet rate: 85-95% of total events\n")
    cat("  WARNING: Too stringent gating removes large cells (e.g., monocytes)\n")
}
```

### Phase 2: Compensation

```r
compute_compensation <- function(fs, controls_dir) {
    cat("=== Compensation ===\n")
    cat("Spillover matrix calculation from single-stained controls\n\n")

    # Load single-stained controls
    # Each control has one fluorochrome only
    # spillover() calculates the matrix from these

    cat("Compensation Workflow:\n")
    cat("  1. Acquire single-stained controls (one per fluorochrome)\n")
    cat("  2. Gate on positive population in each control\n")
    cat("  3. Calculate spillover coefficients\n")
    cat("  4. Apply compensation matrix to all samples\n\n")

    cat("Manual spillover matrix verification:\n")
    cat("  - After compensation, check that positive populations\n")
    cat("    do not spill into other channels\n")
    cat("  - Common problem pairs: FITC/PE, PE/PE-Cy7, APC/APC-Cy7\n")
    cat("  - Over-compensation: negative populations below zero\n")
    cat("  - Under-compensation: positive populations remain in wrong channel\n")

    # Apply compensation
    # fs_comp <- compensate(fs, spillover_matrix)
    return(NULL)
}

apply_compensation <- function(fs, spill_matrix) {
    # Apply and verify
    fs_comp <- compensate(fs, spill_matrix)

    cat("Post-compensation checks:\n")
    cat("  1. No negative population means below expected threshold\n")
    cat("  2. Positive controls single-positive only\n")
    cat("  3. FMO (Fluorescence Minus One) controls for gating boundaries\n")
    return(fs_comp)
}
```

### Phase 3: Transformation

```r
transform_data <- function(fs_comp, method = "logicle") {
    cat("=== Data Transformation ===\n\n")

    if (method == "logicle") {
        cat("Logicle (biexponential) transformation:\n")
        cat("  - Preferred for fluorescence flow cytometry\n")
        cat("  - Handles negative values from compensation\n")
        cat("  - Parameters: w (width), t (top), m (decades), a (additional neg decades)\n")
        cat("  - estimateLogicle() auto-estimates parameters per channel\n\n")

        # Estimate and apply
        # lgcl <- estimateLogicle(fs_comp[[1]], channels = fluorescent_channels)
        # fs_trans <- transform(fs_comp, lgcl)

    } else if (method == "arcsinh") {
        cat("Arcsinh transformation:\n")
        cat("  - Standard for CyTOF/mass cytometry\n")
        cat("  - arcsinh(x / cofactor)\n")
        cat("  - Cofactor: 5 (common for CyTOF), 150 (for flow cytometry)\n")
        cat("  - No negative value issues (mass cytometry has no compensation)\n\n")

        # asinh_trans <- arcsinhTransform(transformationId = "arcsinh",
        #                                 a = 0, b = 1/5, c = 0)
    }

    cat("Transformation Decision Tree:\n")
    cat("  +-- Fluorescence flow cytometry?\n")
    cat("  |   +-- YES: Logicle (biexponential)\n")
    cat("  |   |   +-- Has compensated negative values: logicle handles these\n")
    cat("  |   |   +-- Alternative: biexponential (flowjo_biexp)\n")
    cat("  |   +-- Special case: Log transform (only if all values positive)\n")
    cat("  +-- Mass cytometry (CyTOF)?\n")
    cat("      +-- YES: Arcsinh with cofactor 5\n")
    cat("      +-- Surface markers: cofactor 5\n")
    cat("      +-- Phospho markers: cofactor 5 or adjust per marker\n")

    return(NULL)
}
```

### Phase 4: Manual Gating

```r
manual_gating_strategy <- function() {
    cat("=== Standard Immune Panel Gating Strategy ===\n\n")

    strategy <- list(
        step1 = list(
            gate = "FSC-A vs SSC-A",
            purpose = "Exclude debris (low FSC, low SSC)",
            note = "Gate on lymphocyte/monocyte cloud"
        ),
        step2 = list(
            gate = "FSC-A vs FSC-H",
            purpose = "Singlet discrimination (exclude doublets)",
            note = "Singlets fall on diagonal; doublets shifted right"
        ),
        step3 = list(
            gate = "Viability dye vs FSC-A",
            purpose = "Exclude dead cells (viability dye positive = dead)",
            note = "Use amine-reactive dye (e.g., Zombie Aqua, LIVE/DEAD)"
        ),
        step4 = list(
            gate = "CD45 vs SSC-A",
            purpose = "Identify leukocytes (CD45+)",
            note = "Excludes non-immune cells, RBCs, platelets"
        ),
        step5 = list(
            gate = "CD3 vs CD19/CD20",
            purpose = "T cells (CD3+) vs B cells (CD19/20+)",
            note = "Double-negative = NK cells, monocytes, etc."
        ),
        step6_T = list(
            gate = "CD4 vs CD8 (on CD3+ cells)",
            purpose = "Helper T (CD4+CD8-) vs Cytotoxic T (CD4-CD8+)",
            note = "CD4+CD8+ = double-positive (thymic or aberrant)"
        ),
        step7_activation = list(
            gate = "CD25, CD69, HLA-DR on T cell subsets",
            purpose = "Activation status",
            note = "CD25+CD127- = Treg markers"
        )
    )

    for (step_name in names(strategy)) {
        s <- strategy[[step_name]]
        cat(sprintf("  %s: %s\n", step_name, s$gate))
        cat(sprintf("    Purpose: %s\n", s$purpose))
        cat(sprintf("    Note: %s\n\n", s$note))
    }

    cat("Backgating Verification:\n")
    cat("  After gating, backgate identified populations onto FSC/SSC\n")
    cat("  to verify populations appear where expected:\n")
    cat("    - Lymphocytes: low FSC, low SSC\n")
    cat("    - Monocytes: medium FSC, medium SSC\n")
    cat("    - Granulocytes: high FSC, high SSC\n")
    cat("    - If a population appears in wrong scatter area, revisit gating\n")
}

# Automated gating with OpenCyto
automated_gating <- function(fs_trans, gating_template_csv) {
    cat("=== Automated Gating: OpenCyto ===\n\n")

    # OpenCyto gating template format:
    # alias,pop,parent,dims,gating_method,gating_args
    # nonDebris,+,root,FSC-A,mindensity,
    # singlets,+,nonDebris,FSC-A:FSC-H,singletGate,
    # live,-,singlets,viability,mindensity,
    # cd3,+,live,CD3,mindensity,

    cat("Gating methods available in OpenCyto:\n")
    cat("  mindensity: Finds minimum density between populations\n")
    cat("  flowClust: Model-based clustering (EM algorithm)\n")
    cat("  quantileGate: Gate at quantile threshold\n")
    cat("  singletGate: Specialized for doublet removal\n")
    cat("  tailgate: Gate at tail of distribution\n")
    cat("  flowDensity: Density-based gating (handles skewed data)\n\n")

    cat("Template CSV example:\n")
    cat("  alias,pop,parent,dims,gating_method,gating_args\n")
    cat("  nonDebris,+,root,FSC-A,mindensity,\n")
    cat("  singlets,+,nonDebris,FSC-A:FSC-H,singletGate,wider_gate=TRUE\n")
    cat("  live,-,singlets,Viability,mindensity,\n")
    cat("  CD3pos,+,live,CD3,mindensity,\n")
    cat("  CD4pos,+,CD3pos,CD4,mindensity,\n")
    cat("  CD8pos,+,CD3pos,CD8,mindensity,\n")

    return(NULL)
}
```

### Phase 5: Unsupervised Clustering

```r
flowsom_clustering <- function(fs_trans, markers, n_clusters = 20, n_metaclusters = 10) {
    cat("=== FlowSOM Clustering ===\n\n")

    cat("FlowSOM workflow:\n")
    cat("  1. Build self-organizing map (SOM): Organizes cells into nodes\n")
    cat(sprintf("  2. SOM grid: %dx%d = %d nodes (default 10x10)\n",
                ceiling(sqrt(n_clusters)), ceiling(sqrt(n_clusters)), n_clusters))
    cat(sprintf("  3. Metaclustering: Consensus clustering into %d metaclusters\n", n_metaclusters))
    cat("  4. Each metacluster = cell population\n\n")

    # FlowSOM code
    r_code <- sprintf('
    library(FlowSOM)
    # Build FlowSOM
    fsom <- FlowSOM(fs_trans,
                    colsToUse = markers,     # marker channels to use
                    nClus = %d,              # number of metaclusters
                    xdim = 10, ydim = 10,    # SOM grid dimensions
                    seed = 42)

    # Get cluster assignments
    clusters <- GetMetaclusters(fsom)

    # Marker expression per cluster
    mfi <- GetClusterMFIs(fsom, prettyColnames = TRUE)
    print(mfi)

    # Star chart visualization
    PlotStars(fsom, backgroundValues = clusters)
    ', n_metaclusters)

    cat("Key parameters:\n")
    cat("  nClus: Number of metaclusters (final populations)\n")
    cat("    - Start with expected populations + 2-3 extra\n")
    cat("    - Over-clustering then merging is better than under-clustering\n")
    cat("  xdim, ydim: SOM grid dimensions\n")
    cat("    - 10x10 (100 nodes) for < 500K events\n")
    cat("    - 15x15 (225 nodes) for > 1M events\n")
    cat("  colsToUse: Select lineage markers, exclude viability/scatter\n")

    return(NULL)
}

phenograph_clustering <- function(data, markers, k = 30) {
    cat("=== PhenoGraph Clustering ===\n\n")

    python_code <- """
    import phenograph
    import pandas as pd

    # PhenoGraph: Louvain community detection on k-nearest neighbor graph
    communities, graph, Q = phenograph.cluster(
        data[markers].values,
        k=30,              # k nearest neighbors
        directed=False,
        primary_metric='euclidean',
        n_jobs=-1
    )

    data['phenograph_cluster'] = communities
    print(f"Found {len(set(communities))} clusters")
    print(f"Modularity Q = {Q:.3f}")  # Higher Q = better separation
    """

    cat("PhenoGraph vs FlowSOM:\n")
    cat("  PhenoGraph:\n")
    cat("    + No need to specify number of clusters\n")
    cat("    + Finds rare populations better\n")
    cat("    - Slower (graph construction is O(n*k))\n")
    cat("    - k parameter affects resolution\n")
    cat("  FlowSOM:\n")
    cat("    + Very fast (scales to millions of events)\n")
    cat("    + Reproducible (deterministic with seed)\n")
    cat("    - Must specify number of metaclusters\n")
    cat("    - May merge rare populations\n")

    return(NULL)
}
```

### Phase 6: Dimensionality Reduction

```r
dimred_cytometry <- function(data, markers) {
    cat("=== Dimensionality Reduction ===\n\n")

    cat("UMAP for cytometry:\n")
    r_umap <- '
    library(uwot)
    umap_result <- umap(data[, markers],
                        n_neighbors = 15,     # Local structure (15-30 typical)
                        min_dist = 0.2,       # Minimum distance (0.1-0.5)
                        n_components = 2,
                        metric = "euclidean",
                        n_epochs = 500,       # More epochs for large datasets
                        n_threads = 4)
    '

    cat("tSNE for cytometry:\n")
    r_tsne <- '
    library(Rtsne)
    # Subsample if > 50K events (tSNE is O(n^2))
    n_sub <- min(nrow(data), 50000)
    idx <- sample(nrow(data), n_sub)

    tsne_result <- Rtsne(data[idx, markers],
                         perplexity = 30,      # 5-50, scales with n
                         theta = 0.5,          # Speed/accuracy tradeoff (0=exact, 0.5=fast)
                         max_iter = 1000,
                         num_threads = 4,
                         check_duplicates = FALSE)
    '

    cat("Parameter guidance:\n")
    cat("  UMAP:\n")
    cat("    n_neighbors = 15: Good default; increase for more global structure\n")
    cat("    min_dist = 0.2: Lower = tighter clusters; higher = more spread\n")
    cat("    Scales well to millions of events\n\n")
    cat("  tSNE:\n")
    cat("    perplexity = 30: Standard; increase for large datasets\n")
    cat("    opt_perplexity: Use opt_perplexity for cytometry (auto-selects)\n")
    cat("    Subsample to 50K-100K events for speed\n")
    cat("    WARNING: tSNE distances between clusters are NOT meaningful\n\n")

    cat("UMAP vs tSNE for cytometry:\n")
    cat("  UMAP: Faster, preserves global structure better, recommended\n")
    cat("  tSNE: Better local structure, well-established in cytometry literature\n")
    cat("  Both: Always color by cluster assignment AND individual markers\n")
}
```

### Phase 7: Differential Analysis

```r
diffcyt_analysis <- function(fs_trans, experiment_info, markers_info) {
    cat("=== Differential Analysis: diffcyt Framework ===\n\n")

    r_code <- '
    library(diffcyt)

    # Prepare data
    d_se <- prepareData(fs_trans, experiment_info, markers_info)
    d_se <- transformData(d_se, cofactor = 5)  # arcsinh cofactor

    # Generate features
    # DA: Differential Abundance testing
    d_counts <- calcCounts(d_se)

    # DS: Differential State (marker expression) testing
    d_medians <- calcMedians(d_se)

    # --- Differential Abundance (DA) ---
    # Which cell populations change in proportion between conditions?
    design_matrix <- createDesignMatrix(experiment_info, cols_design = "condition")
    contrast_matrix <- createContrast(c(0, 1))  # condition2 vs condition1

    res_DA <- testDA_edgeR(d_counts, design_matrix, contrast_matrix)
    # Alternative: testDA_GLMM for paired/repeated measures designs
    # res_DA <- testDA_GLMM(d_counts, formula = ~ condition + (1|patient_id))

    # --- Differential State (DS) ---
    # Which markers change expression within a population?
    res_DS <- testDS_limma(d_counts, d_medians, design_matrix, contrast_matrix)
    # Alternative: testDS_LMM for paired designs

    # Extract results
    table_DA <- rowData(res_DA)
    table_DS <- rowData(res_DS)
    '

    cat("diffcyt test selection:\n")
    cat("  Differential Abundance (DA):\n")
    cat("    testDA_edgeR: Unpaired comparison (edgeR framework)\n")
    cat("    testDA_GLMM: Paired/longitudinal (generalized linear mixed model)\n")
    cat("    testDA_voom: Alternative unpaired (limma-voom)\n\n")
    cat("  Differential State (DS):\n")
    cat("    testDS_limma: Unpaired marker expression comparison\n")
    cat("    testDS_LMM: Paired marker expression (linear mixed model)\n\n")

    cat("Interpretation:\n")
    cat("  DA significant: Cell population proportion changes between conditions\n")
    cat("  DS significant: Marker expression within population changes\n")
    cat("  Combine DA + DS for comprehensive immune profiling\n")
}
```

### Phase 8: Batch Correction and CyTOF Specifics

```r
batch_correction <- function() {
    cat("=== Batch Correction: CytoNorm ===\n\n")

    r_code <- '
    library(CytoNorm)

    # CytoNorm uses reference samples (same biological sample run in each batch)
    # to learn and apply batch correction

    # Step 1: Train model on reference samples
    model <- CytoNorm.train(
        files = ref_files,           # Reference FCS files (one per batch)
        labels = batch_labels,       # Batch identifiers
        channels = markers,          # Channels to correct
        transformList = transform_list,
        FlowSOM.params = list(nCells = 10000, xdim = 5, ydim = 5, nClus = 10),
        normMethod.train = QuantileNorm.train
    )

    # Step 2: Apply to all files
    CytoNorm.normalize(
        model = model,
        files = all_files,
        labels = all_batch_labels,
        transformList = transform_list,
        outputDir = "normalized/"
    )
    '

    cat("Batch correction decision:\n")
    cat("  +-- Do you have reference samples across batches?\n")
    cat("  |   +-- YES: CytoNorm (preferred)\n")
    cat("  |   +-- NO: Consider alternative approaches\n")
    cat("  |       +-- Bead normalization (CyTOF only)\n")
    cat("  |       +-- Quantile normalization (aggressive)\n")
    cat("  |       +-- Harmony (if integrated with scRNA-seq workflow)\n")
    cat("  +-- CyTOF-specific:\n")
    cat("      +-- Bead normalization: normalizer in premessa package\n")
    cat("      +-- Debarcoding: CATALYST::assignPrelim() + applyCutoffs()\n")
}

cytof_specifics <- function() {
    cat("=== CyTOF/Mass Cytometry Specifics ===\n\n")

    cat("Signal processing:\n")
    cat("  1. Bead normalization: Correct for signal drift during acquisition\n")
    cat("     - Uses embedded normalization beads (140Ce, 151Eu, 153Eu, etc.)\n")
    cat("     - premessa::normalize_data() or Fluidigm normalizer\n")
    cat("  2. Debarcoding: Deconvolute multiplexed samples\n")
    cat("     - CATALYST::assignPrelim() -> applyCutoffs()\n")
    cat("     - Yield: typically 50-80% of events assigned\n")
    cat("  3. Cleanup gates:\n")
    cat("     - Event length: 10-75 (remove aggregates)\n")
    cat("     - DNA intercalator (191Ir/193Ir): gate on singlet DNA+ events\n")
    cat("     - Cisplatin (195Pt) viability: low Pt = live cells\n")
    cat("     - Residual (140Ce): remove bead events\n\n")

    cat("No compensation needed for CyTOF:\n")
    cat("  - Mass cytometry has minimal channel crosstalk\n")
    cat("  - Spillover occurs but is typically < 3% (vs 10-50% in flow)\n")
    cat("  - CATALYST::computeSpillmat() for mass cytometry spillover correction\n\n")

    cat("Marker panel design:\n")
    cat("  Backbone markers (present in all panels): lineage definition\n")
    cat("    CD45, CD3, CD4, CD8, CD19, CD14, CD16, CD56\n")
    cat("  Variable markers: phenotyping, activation, function\n")
    cat("  Metal assignment:\n")
    cat("    - High-expression markers -> lower-sensitivity metals\n")
    cat("    - Low-expression markers -> higher-sensitivity metals (e.g., 169Tm, 174Yb)\n")
    cat("    - Avoid neighboring masses for co-expressed markers (reduce spillover)\n")
}
```

---

## Parameter Reference Tables

### Transformation Parameters

| Method | Platform | Formula | Cofactor | Use Case |
|--------|----------|---------|----------|----------|
| Logicle | Flow (fluorescence) | Biexponential | Auto-estimated | Compensated data with negatives |
| Arcsinh | CyTOF | arcsinh(x/cofactor) | 5 | Mass cytometry ion counts |
| Log | Flow (simple) | log10(x) | N/A | Positive-only data |
| Biexponential | Flow (FlowJo) | FlowJo-style | Width basis | Matching FlowJo gates |

### Clustering Method Comparison

| Method | Speed | Cluster # | Rare Populations | Best For |
|--------|-------|-----------|-----------------|----------|
| FlowSOM | Very fast | User-defined | May miss | Large datasets, discovery |
| PhenoGraph | Moderate | Auto | Detects well | Moderate datasets, rare cells |
| SPADE | Moderate | User-defined | Enriches | Rare population focus |
| ClusterX | Fast | Auto | Good | Density-based populations |
| flowMeans | Fast | Auto (k-means) | May miss | Simple datasets |

### QC Thresholds

| Metric | Acceptable | Ideal | Action if Failed |
|--------|-----------|-------|-----------------|
| Singlet rate | >= 80% | >= 90% | Check sample prep, reduce concentration |
| Viability | >= 70% | >= 90% | Improve sample handling |
| Event count per sample | >= 10,000 | >= 50,000 | Acquire more events |
| CV of bead signal (CyTOF) | < 20% | < 10% | Instrument maintenance |
| Spillover (flow) | < 30% max | < 15% | Optimize panel, use brighter fluors |
| Batch reference correlation | r > 0.9 | r > 0.95 | CytoNorm correction needed |

---

## Evidence Grading

| Tier | Evidence Type | Example |
|------|-------------|---------|
| **T1** | Validated clinical panel | EuroFlow panels for leukemia/lymphoma |
| **T2** | Published consensus gating | HIPC standardized gating strategies |
| **T3** | Automated clustering, replicated | FlowSOM with consistent populations across batches |
| **T4** | Exploratory clustering | Novel population from single experiment |

---

## Multi-Agent Workflow Examples

**"Characterize immune cell populations in tumor vs normal tissue by CyTOF"**
1. Flow Cytometry -> Full CyTOF pipeline: normalization, debarcoding, FlowSOM clustering, diffcyt DA/DS
2. Single-Cell Analysis -> Integration with scRNA-seq for transcriptomic annotation of clusters
3. Gene Enrichment -> Pathway analysis of differentially expressed markers

**"Monitor immune reconstitution post-transplant with flow cytometry time course"**
1. Flow Cytometry -> Gating, population quantification at each timepoint
2. Temporal Genomics -> Time-series analysis of population frequencies
3. Immune Repertoire -> TCR/BCR repertoire diversity at each timepoint

**"Design and validate a 40-marker CyTOF panel for immune profiling"**
1. Flow Cytometry -> Panel design: metal-marker assignment, antibody titration, spillover assessment
2. Biostatistics -> Power analysis for differential abundance detection

## Completeness Checklist

- [ ] FCS files loaded and channel/marker mapping verified
- [ ] QC performed: doublet discrimination, viability, time stability
- [ ] Compensation applied (flow) or bead normalization applied (CyTOF)
- [ ] Transformation applied (logicle for flow, arcsinh for CyTOF)
- [ ] Gating strategy documented (manual or automated with OpenCyto)
- [ ] Unsupervised clustering performed (FlowSOM or PhenoGraph)
- [ ] Cluster annotation with marker expression (MFI heatmap)
- [ ] Dimensionality reduction visualization (UMAP/tSNE)
- [ ] Differential analysis if multiple conditions (diffcyt DA/DS)
- [ ] Batch correction applied if multi-batch (CytoNorm)
- [ ] Evidence tier assigned to all key findings (T1-T4)
- [ ] Report file created with all sections populated (no `[Analyzing...]` remaining)
