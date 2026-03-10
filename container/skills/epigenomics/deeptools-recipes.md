# deepTools NGS Signal Processing Recipes

Copy-paste-ready bash commands for NGS signal processing, normalization, QC, and visualization using deepTools.

> **Parent skill**: [SKILL.md](SKILL.md) — full epigenomics analysis pipeline with MCP tools.
> **See also**: [chipseq-recipes.md](chipseq-recipes.md) — MACS2 peak calling, DiffBind, ChIPseeker, HOMER, IDR, chromVAR.

---

## Recipe 1: bamCoverage with RPGC Normalization

Generate a normalized bigWig signal track using RPGC (Reads Per Genomic Content, also called 1x depth normalization) for cross-sample comparability.

```bash
bamCoverage \
  --bam chip_h3k27ac.bam \
  -o h3k27ac_rpgc.bw \
  --normalizeUsing RPGC \
  --effectiveGenomeSize 2913022398 \
  --binSize 10 \
  --extendReads \
  --ignoreDuplicates \
  --minMappingQuality 30 \
  --centerReads \
  --numberOfProcessors max
```

**Key Parameters:**
- `--normalizeUsing RPGC`: Reads Per Genomic Content; normalizes to 1x sequencing depth. Best for comparing signal intensity across samples with different sequencing depths
- `--effectiveGenomeSize`: Mappable genome size. Human GRCh38 = `2913022398`, Mouse mm10 = `2652783500`, Drosophila dm6 = `142573017`, C. elegans ce11 = `100286401`
- `--binSize 10`: Resolution in base pairs; 10 bp gives high resolution. Use 50 for faster processing or genome-wide views
- `--extendReads`: Extend single-end reads to estimated fragment size (auto-detected). For paired-end, omit or use `--extendReads` to extend each mate
- `--ignoreDuplicates`: Skip PCR/optical duplicate reads
- `--minMappingQuality 30`: Exclude low-confidence alignments (MAPQ < 30)
- `--centerReads`: Center each read (or fragment for PE) at its midpoint; useful for nucleosome-resolution analysis
- `--numberOfProcessors max`: Use all available CPU cores

**Expected Output:**
- BigWig file (`.bw`) with RPGC-normalized signal, loadable in IGV, UCSC Genome Browser, or deepTools downstream tools
- Signal values represent reads per bin normalized to 1x genome coverage

---

## Recipe 2: bamCoverage Normalization Method Comparison

Generate bigWig tracks with different normalization methods to understand when to use each.

```bash
# CPM: Counts Per Million mapped reads
# Best for: Comparing samples within the same experiment
# Limitation: Affected by highly enriched regions consuming reads
bamCoverage \
  --bam chip_sample.bam \
  -o sample_cpm.bw \
  --normalizeUsing CPM \
  --binSize 10 \
  --extendReads \
  --ignoreDuplicates \
  --numberOfProcessors max

# BPM: Bins Per Million (like TPM for RNA-seq)
# Best for: When you want per-bin normalization analogous to TPM
# Accounts for bin size differences in signal calculation
bamCoverage \
  --bam chip_sample.bam \
  -o sample_bpm.bw \
  --normalizeUsing BPM \
  --binSize 10 \
  --extendReads \
  --ignoreDuplicates \
  --numberOfProcessors max

# RPKM: Reads Per Kilobase per Million mapped reads
# Best for: Legacy compatibility; generally superseded by RPGC or BPM
bamCoverage \
  --bam chip_sample.bam \
  -o sample_rpkm.bw \
  --normalizeUsing RPKM \
  --binSize 10 \
  --extendReads \
  --ignoreDuplicates \
  --numberOfProcessors max

# RPGC: Reads Per Genomic Content (1x normalization)
# Best for: Cross-sample comparisons, especially between experiments
# Requires effective genome size
bamCoverage \
  --bam chip_sample.bam \
  -o sample_rpgc.bw \
  --normalizeUsing RPGC \
  --effectiveGenomeSize 2913022398 \
  --binSize 10 \
  --extendReads \
  --ignoreDuplicates \
  --numberOfProcessors max

# None: Raw coverage (no normalization)
# Best for: QC, when downstream tools handle normalization (e.g., DiffBind)
bamCoverage \
  --bam chip_sample.bam \
  -o sample_raw.bw \
  --normalizeUsing None \
  --binSize 10 \
  --extendReads \
  --numberOfProcessors max
```

**When to Use Each:**

| Method | Formula | Best For | Limitation |
|--------|---------|----------|------------|
| **RPGC** | reads * scaling / bin | Cross-experiment comparison | Requires effective genome size |
| **CPM** | reads * 1M / total | Within-experiment comparison | Skewed by dominant peaks |
| **BPM** | reads * 1M / (total * binSize/1000) | Per-bin density comparison | Similar to CPM issues |
| **RPKM** | reads * 1M * 1000 / (total * binSize) | Legacy analyses | Superseded by RPGC |
| **None** | raw reads / bin | QC, external normalization | Not comparable across samples |

**Expected Output:**
- One bigWig file per normalization method
- RPGC is recommended as the default for most ChIP-seq and ATAC-seq analyses

---

## Recipe 3: bamCompare for ChIP-over-Input Log2 Ratio

Compute the log2 ratio of ChIP signal over input control to visualize enrichment above background.

```bash
bamCompare \
  -b1 chip_treatment.bam \
  -b2 chip_input.bam \
  -o chip_vs_input_log2ratio.bw \
  --operation log2ratio \
  --pseudocount 1 \
  --scaleFactorsMethod readCount \
  --binSize 50 \
  --extendReads \
  --ignoreDuplicates \
  --minMappingQuality 30 \
  --skipZeroOverZero \
  --numberOfProcessors max
```

**Key Parameters:**
- `-b1`: Treatment BAM (ChIP); `-b2`: Control BAM (input/IgG)
- `--operation log2ratio`: Compute log2(b1/b2). Alternatives: `ratio` (linear), `subtract` (b1 - b2), `add`, `mean`, `reciprocal_ratio`, `first`, `second`
- `--pseudocount 1`: Added to both numerator and denominator to avoid log(0). Use `0.1` for sharper contrast, `1` for conservative smoothing
- `--scaleFactorsMethod readCount`: Scale samples by total read count before comparison. Alternatives: `SES` (signal extraction scaling, better for samples with differential enrichment), `None` (no scaling)
- `--skipZeroOverZero`: Skip bins where both samples have zero reads (avoids 0/0 = NaN)
- `--binSize 50`: Larger bins (50 bp) reduce noise for ratio tracks; use 10 bp for high-resolution peaks

**Expected Output:**
- BigWig file with log2 ratio values: positive = enriched in ChIP, negative = depleted vs input, zero = equal
- Useful for genome browser visualization showing enrichment patterns
- Typical range: -2 to +5 for strong ChIP-seq enrichment

---

## Recipe 4: plotFingerprint for Library Complexity QC

Assess library complexity and ChIP enrichment quality using cumulative read distribution (fingerprint plot).

```bash
plotFingerprint \
  -b chip_h3k27ac.bam chip_h3k4me3.bam chip_input.bam \
  --labels H3K27ac H3K4me3 Input \
  -o fingerprint_qc.png \
  --plotTitle "Library Complexity & Enrichment QC" \
  --skipZeros \
  --numberOfSamples 500000 \
  --minMappingQuality 30 \
  --outQualityMetrics fingerprint_metrics.txt \
  --outRawCounts fingerprint_rawcounts.tab \
  --numberOfProcessors max
```

**Key Parameters:**
- `-b`: One or more BAM files to compare (ChIP samples + input control)
- `--labels`: Sample names for plot legend (must match number of BAM files)
- `--numberOfSamples 500000`: Number of genomic bins to sample; increase for more precise QC, decrease for speed
- `--outQualityMetrics`: Output file with JSE (Jensen-Shannon Enrichment) and other QC metrics
- `--outRawCounts`: Tab-separated raw count data for custom downstream analysis
- `--skipZeros`: Exclude bins with zero reads from the analysis

**Interpretation:**
- **Input/IgG control**: Should follow the diagonal (uniform coverage, no enrichment)
- **Sharp marks (H3K4me3, TFs)**: Strong deviation from diagonal; sharp curve = good enrichment
- **Broad marks (H3K27me3, H3K36me3)**: Moderate deviation; less extreme than TFs
- **JSE metric**: 0 = no enrichment (input-like); 1 = maximum enrichment. Minimum 0.3 for usable ChIP-seq
- **Poor library**: Curve far above diagonal at left side = extreme duplication / low complexity

**Expected Output:**
- Fingerprint PNG plot comparing cumulative read distributions
- `fingerprint_metrics.txt`: JSE, AUC, and Synthetic Contamination metrics per sample
- Quick visual QC: all ChIP samples should curve away from the diagonal more than input

---

## Recipe 5: multiBamSummary + plotCorrelation for Sample Correlation

Compute genome-wide signal correlation between samples and visualize as a heatmap.

```bash
# Step 1: Compute read coverage across genome-wide bins for all samples
multiBamSummary bins \
  --bamfiles \
    ctrl_rep1.bam ctrl_rep2.bam ctrl_rep3.bam \
    treat_rep1.bam treat_rep2.bam treat_rep3.bam \
  --labels \
    Ctrl_R1 Ctrl_R2 Ctrl_R3 \
    Treat_R1 Treat_R2 Treat_R3 \
  --binSize 10000 \
  --distanceBetweenBins 0 \
  --minMappingQuality 30 \
  --ignoreDuplicates \
  --outFileName multibam_results.npz \
  --outRawCounts multibam_rawcounts.tab \
  --numberOfProcessors max

# Step 2: Plot Pearson correlation heatmap
plotCorrelation \
  --corData multibam_results.npz \
  --corMethod pearson \
  --whatToPlot heatmap \
  --plotFile correlation_heatmap_pearson.png \
  --outFileCorMatrix correlation_matrix_pearson.tab \
  --plotTitle "Pearson Correlation of Read Counts" \
  --plotNumbers \
  --colorMap RdYlBu_r \
  --plotHeight 9 \
  --plotWidth 11

# Step 3: Plot Spearman correlation heatmap (rank-based, robust to outliers)
plotCorrelation \
  --corData multibam_results.npz \
  --corMethod spearman \
  --whatToPlot heatmap \
  --plotFile correlation_heatmap_spearman.png \
  --outFileCorMatrix correlation_matrix_spearman.tab \
  --plotTitle "Spearman Correlation of Read Counts" \
  --plotNumbers \
  --colorMap RdYlBu_r

# Alternative: Scatter plot for pairwise comparison
plotCorrelation \
  --corData multibam_results.npz \
  --corMethod pearson \
  --whatToPlot scatterplot \
  --plotFile correlation_scatter.png \
  --plotTitle "Pairwise Sample Scatter"
```

**Key Parameters:**
- `--binSize 10000`: Genome divided into 10 kb bins for correlation computation. Use 1000 for peak-level resolution (slower)
- `--distanceBetweenBins 0`: No gaps between bins (contiguous tiling). Use 1000 to skip regions and speed up computation
- `--corMethod pearson`: Standard linear correlation; `spearman` for rank-based (robust to outliers, better for non-linear relationships)
- `--whatToPlot heatmap`: Clustered correlation heatmap; `scatterplot` for pairwise scatter plots
- `--plotNumbers`: Display correlation values in heatmap cells
- `--colorMap RdYlBu_r`: Red = high correlation, blue = low

**Expected Output:**
- Correlation heatmap PNG showing sample-to-sample similarity
- Tab-separated correlation matrix for downstream analysis
- Replicates should cluster together (Pearson > 0.95 for good replicates)
- Conditions should separate from each other but show within-group consistency

---

## Recipe 6: multiBigwigSummary + plotPCA for Signal PCA

Perform PCA on bigWig signal across samples to identify batch effects and condition separation.

```bash
# Step 1: Summarize bigWig signals across genome-wide bins
multiBigwigSummary bins \
  --bwfiles \
    ctrl_rep1_rpgc.bw ctrl_rep2_rpgc.bw ctrl_rep3_rpgc.bw \
    treat_rep1_rpgc.bw treat_rep2_rpgc.bw treat_rep3_rpgc.bw \
  --labels \
    Ctrl_R1 Ctrl_R2 Ctrl_R3 \
    Treat_R1 Treat_R2 Treat_R3 \
  --binSize 10000 \
  --distanceBetweenBins 0 \
  --outFileName multibw_results.npz \
  --outRawCounts multibw_rawcounts.tab \
  --numberOfProcessors max

# Alternative: Summarize over BED regions (peaks, promoters, enhancers)
multiBigwigSummary BED-file \
  --BED consensus_peaks.bed \
  --bwfiles \
    ctrl_rep1_rpgc.bw ctrl_rep2_rpgc.bw \
    treat_rep1_rpgc.bw treat_rep2_rpgc.bw \
  --labels Ctrl_R1 Ctrl_R2 Treat_R1 Treat_R2 \
  --outFileName multibw_peaks.npz \
  --numberOfProcessors max

# Step 2: PCA plot
plotPCA \
  --corData multibw_results.npz \
  --plotFile pca_bigwig.png \
  --plotTitle "PCA of ChIP-seq Signal" \
  --plotHeight 8 \
  --plotWidth 10 \
  --outFileNameData pca_coordinates.tab \
  --rowCenter

# Step 3: PCA on peak-specific regions
plotPCA \
  --corData multibw_peaks.npz \
  --plotFile pca_peaks.png \
  --plotTitle "PCA of Signal at Peak Regions" \
  --plotHeight 8 \
  --plotWidth 10 \
  --rowCenter
```

**Key Parameters:**
- `multiBigwigSummary bins`: Genome-wide binning for unbiased PCA; `BED-file` mode focuses on specific regions (peaks, promoters)
- `--binSize 10000`: 10 kb bins for genome-wide; not applicable for BED-file mode
- `--rowCenter`: Center each bin's values across samples before PCA (removes position-specific bias)
- `--outFileNameData`: Export PC coordinates for custom plotting with ggplot2 or matplotlib
- Use RPGC-normalized bigWigs for comparable signal across samples

**Expected Output:**
- PCA scatter plot showing sample clustering
- PC1 and PC2 coordinates in tab-separated file for custom visualization
- Replicates should cluster tightly; conditions should separate along PC1 or PC2
- Outlier samples indicate batch effects or QC issues

---

## Recipe 7: computeMatrix Reference-Point (Signal Around TSS/TES)

Compute signal matrices centered on reference points (TSS, TES, peak summits) for heatmap and profile generation.

```bash
# Signal around TSS (Transcription Start Site)
computeMatrix reference-point \
  --referencePoint TSS \
  -b 3000 \
  -a 3000 \
  -R genes.bed \
  -S h3k4me3_rpgc.bw h3k27ac_rpgc.bw h3k27me3_rpgc.bw \
  --samplesLabel H3K4me3 H3K27ac H3K27me3 \
  --skipZeros \
  --missingDataAsZero \
  --binSize 50 \
  -o matrix_tss.gz \
  --outFileSortedRegions regions_sorted_tss.bed \
  --numberOfProcessors max

# Signal around TES (Transcription End Site)
computeMatrix reference-point \
  --referencePoint TES \
  -b 3000 \
  -a 3000 \
  -R genes.bed \
  -S h3k36me3_rpgc.bw \
  --samplesLabel H3K36me3 \
  --skipZeros \
  --missingDataAsZero \
  -o matrix_tes.gz \
  --numberOfProcessors max

# Signal around peak summits (center of peaks)
computeMatrix reference-point \
  --referencePoint center \
  -b 2000 \
  -a 2000 \
  -R peak_summits.bed \
  -S chip_rpgc.bw input_rpgc.bw \
  --samplesLabel ChIP Input \
  --skipZeros \
  --missingDataAsZero \
  --sortRegions descend \
  --sortUsing mean \
  -o matrix_summits.gz \
  --numberOfProcessors max
```

**Key Parameters:**
- `--referencePoint TSS`: Center on transcription start site. Options: `TSS`, `TES`, `center` (midpoint of region)
- `-b 3000 -a 3000`: Show 3 kb upstream and 3 kb downstream of reference point
- `-R genes.bed`: BED file with genomic regions (genes, peaks, enhancers). Multiple BED files can be provided for grouped heatmaps
- `-S *.bw`: One or more bigWig signal files
- `--skipZeros`: Exclude regions with zero signal across all samples
- `--missingDataAsZero`: Treat missing bigWig data as zero (avoids NaN gaps)
- `--binSize 50`: Resolution of the matrix; 50 bp is standard, 10 bp for high-resolution
- `--sortRegions descend --sortUsing mean`: Sort regions by mean signal for cleaner heatmaps
- `--outFileSortedRegions`: Save the sorted region order for consistent plotting across matrices

**Expected Output:**
- Compressed matrix file (`.gz`) containing signal values at each position relative to reference point
- Sorted regions BED file preserving the ordering used in the matrix
- Matrix is input for `plotHeatmap` and `plotProfile` commands

---

## Recipe 8: computeMatrix Scale-Regions (Signal Across Gene Bodies)

Compute signal across gene bodies scaled to uniform length, with flanking regions.

```bash
# Scale gene bodies to 5 kb, with 3 kb flanking on each side
computeMatrix scale-regions \
  -R expressed_genes.bed silent_genes.bed \
  -S h3k36me3_rpgc.bw h3k27me3_rpgc.bw \
  --samplesLabel H3K36me3 H3K27me3 \
  --regionBodyLength 5000 \
  -b 3000 \
  -a 3000 \
  --startLabel TSS \
  --endLabel TES \
  --skipZeros \
  --missingDataAsZero \
  --binSize 50 \
  --sortRegions descend \
  --sortUsing mean \
  --sortUsingSamples 1 \
  -o matrix_genebody.gz \
  --outFileSortedRegions regions_sorted_genebody.bed \
  --numberOfProcessors max

# Scale enhancer regions to 2 kb
computeMatrix scale-regions \
  -R active_enhancers.bed poised_enhancers.bed \
  -S h3k4me1_rpgc.bw h3k27ac_rpgc.bw \
  --samplesLabel H3K4me1 H3K27ac \
  --regionBodyLength 2000 \
  -b 1000 \
  -a 1000 \
  --startLabel "5'" \
  --endLabel "3'" \
  --skipZeros \
  --missingDataAsZero \
  -o matrix_enhancers.gz \
  --numberOfProcessors max
```

**Key Parameters:**
- `--regionBodyLength 5000`: Scale all gene bodies to 5 kb (regardless of actual gene length). Standard values: 5000 for genes, 2000 for enhancers/peaks
- `-b 3000 -a 3000`: Flanking regions upstream of start and downstream of end (not scaled)
- `--startLabel TSS --endLabel TES`: Labels for the scaled region boundaries on plots
- `--sortUsingSamples 1`: Sort regions by signal in the first sample (1-indexed)
- Multiple `-R` files create grouped heatmaps (e.g., expressed vs silent genes side by side)
- Use for broad marks (H3K36me3 across gene bodies, H3K27me3 domains) where reference-point mode loses information

**Expected Output:**
- Matrix file with signal across scaled regions plus flanking
- Gene bodies of different lengths are stretched/compressed to the same size for comparison
- Reveals positional enrichment patterns: 5' bias (promoter marks), 3' bias (elongation marks), or uniform (domain marks)

---

## Recipe 9: plotHeatmap for Publication-Quality Visualization

Generate publication-ready heatmaps from computeMatrix output with customizable appearance.

```bash
# Standard heatmap with color bar
plotHeatmap \
  -m matrix_tss.gz \
  -o heatmap_publication.png \
  --colorMap RdBu_r \
  --whatToShow 'heatmap and colorbar' \
  --sortRegions descend \
  --sortUsing mean \
  --sortUsingSamples 1 \
  --zMin -2 --zMax 2 \
  --heatmapHeight 15 \
  --heatmapWidth 5 \
  --xAxisLabel "Distance from TSS (bp)" \
  --refPointLabel TSS \
  --regionsLabel "All genes" \
  --plotTitle "Histone Mark Signal at TSS" \
  --dpi 300

# Multi-group heatmap (e.g., expressed vs silent genes)
plotHeatmap \
  -m matrix_genebody.gz \
  -o heatmap_groups.png \
  --colorMap YlOrRd \
  --whatToShow 'heatmap and colorbar' \
  --sortRegions descend \
  --sortUsing mean \
  --perGroup \
  --zMin 0 --zMax 5 \
  --heatmapHeight 12 \
  --kmeans 4 \
  --outFileSortedRegions heatmap_kmeans_clusters.bed \
  --dpi 300

# Heatmap with profile on top
plotHeatmap \
  -m matrix_tss.gz \
  -o heatmap_with_profile.png \
  --colorMap Blues \
  --whatToShow 'plot, heatmap and colorbar' \
  --sortRegions descend \
  --sortUsing mean \
  --zMin 0 --zMax 4 \
  --heatmapHeight 12 \
  --plotTitle "ChIP-seq Signal" \
  --yAxisLabel "Signal" \
  --dpi 300

# SVG output for vector graphics (editable in Illustrator/Inkscape)
plotHeatmap \
  -m matrix_tss.gz \
  -o heatmap_vector.svg \
  --colorMap RdBu_r \
  --whatToShow 'heatmap and colorbar' \
  --zMin -2 --zMax 2 \
  --dpi 300
```

**Key Parameters:**
- `--colorMap RdBu_r`: Diverging colormap for log2 ratios; `YlOrRd` / `Blues` for signal intensity; `viridis` for perceptually uniform. Full list: any matplotlib colormap name
- `--zMin / --zMax`: Fixed color scale bounds; essential for cross-figure comparisons. Omit for auto-scaling
- `--whatToShow`: `'heatmap and colorbar'` (default), `'plot, heatmap and colorbar'` (adds profile on top), `'heatmap only'`
- `--kmeans 4`: K-means clustering of regions into 4 groups; useful for identifying distinct signal patterns
- `--perGroup`: Sort and display each region group (from multiple BED files) independently
- `--heatmapHeight 15`: Height in cm; adjust for number of regions
- `--dpi 300`: Publication-quality resolution (300 for print, 150 for screen)
- Output as `.svg` for editable vector graphics

**Expected Output:**
- High-resolution heatmap PNG or SVG
- K-means cluster assignments saved as BED file (with `--outFileSortedRegions`)
- Profile plot showing average signal when using `'plot, heatmap and colorbar'`

---

## Recipe 10: plotProfile for Average Signal with Confidence Intervals

Generate average signal profile plots with standard error or confidence intervals.

```bash
# Basic profile plot
plotProfile \
  -m matrix_tss.gz \
  -o profile_tss.png \
  --plotTitle "Average Signal at TSS" \
  --yAxisLabel "RPGC signal" \
  --refPointLabel TSS \
  --perGroup \
  --plotHeight 7 \
  --plotWidth 10 \
  --dpi 300

# Profile with confidence interval (standard error shading)
plotProfile \
  -m matrix_tss.gz \
  -o profile_with_ci.png \
  --plotTitle "Signal Profile with SE" \
  --yAxisLabel "Signal (RPGC)" \
  --refPointLabel TSS \
  --perGroup \
  --plotType se \
  --plotHeight 8 \
  --plotWidth 12 \
  --colors red blue green \
  --dpi 300

# Profile overlaying multiple samples on same plot
plotProfile \
  -m matrix_tss.gz \
  -o profile_overlay.png \
  --plotTitle "Histone Marks at TSS" \
  --yAxisLabel "Signal" \
  --refPointLabel TSS \
  --plotType lines \
  --plotHeight 7 \
  --plotWidth 10 \
  --legendLocation upper-right \
  --dpi 300

# Profile for scaled regions (gene body)
plotProfile \
  -m matrix_genebody.gz \
  -o profile_genebody.png \
  --plotTitle "Signal Across Gene Body" \
  --yAxisLabel "RPGC signal" \
  --startLabel TSS \
  --endLabel TES \
  --perGroup \
  --plotType fill \
  --plotHeight 8 \
  --plotWidth 12 \
  --dpi 300

# K-means clustered profiles
plotProfile \
  -m matrix_tss.gz \
  -o profile_kmeans.png \
  --kmeans 3 \
  --plotTitle "Clustered Signal Profiles" \
  --perGroup \
  --plotHeight 8 \
  --plotWidth 10 \
  --outFileSortedRegions profile_cluster_regions.bed \
  --dpi 300
```

**Key Parameters:**
- `--plotType`: `lines` (default, mean only), `se` (mean with standard error shading), `fill` (filled area under curve), `std` (mean with standard deviation), `overlapped_lines` (individual sample lines), `heatmap` (profile as heatmap)
- `--perGroup`: Plot each region group (from multiple BED inputs) separately
- `--colors red blue green`: Custom colors per sample; accepts color names or hex codes (`#FF0000`)
- `--legendLocation`: Position: `upper-right`, `upper-left`, `best`, `none` (hide legend)
- `--kmeans 3`: Cluster regions into 3 groups and plot separate profiles per cluster
- `--startLabel TSS --endLabel TES`: Labels for scaled region boundaries

**Expected Output:**
- Profile PNG showing average signal curves across genomic regions
- Shaded confidence intervals when using `--plotType se` or `std`
- K-means cluster regions saved to BED file for downstream analysis

---

## Recipe 11: bamPEFragmentSize for Fragment Size Distribution

Analyze paired-end fragment size distribution for ChIP-seq and ATAC-seq quality control.

```bash
# Fragment size histogram
bamPEFragmentSize \
  --bamfiles \
    chip_h3k4me3.bam \
    chip_h3k27ac.bam \
    atac_sample.bam \
    chip_input.bam \
  --samplesLabel H3K4me3 H3K27ac ATAC-seq Input \
  --histogram fragment_sizes.png \
  --plotTitle "Fragment Size Distribution" \
  --maxFragmentLength 1000 \
  --numberOfProcessors max \
  --outRawFragmentLengths fragment_lengths.tab \
  --table fragment_size_metrics.txt

# ATAC-seq specific: check for nucleosomal laddering
bamPEFragmentSize \
  --bamfiles atac_sample.bam \
  --samplesLabel ATAC-seq \
  --histogram atac_fragment_sizes.png \
  --plotTitle "ATAC-seq Fragment Size Distribution" \
  --maxFragmentLength 1500 \
  --plotFileFormat pdf \
  --numberOfProcessors max
```

**Key Parameters:**
- `--maxFragmentLength 1000`: Maximum fragment size to include in plot (default: 1000). Use 1500 for ATAC-seq to see di/tri-nucleosomal fragments
- `--histogram`: Output plot file path (PNG, PDF, SVG)
- `--outRawFragmentLengths`: Tab-separated raw fragment length data for custom plotting
- `--table`: Summary statistics table (median, mean, std, MAD per sample)

**Interpretation:**
- **ChIP-seq**: Expect peak at ~150-200 bp (mono-nucleosome) for histone marks; ~200-300 bp for TFs with crosslinking
- **ATAC-seq nucleosomal pattern**: Peaks at ~200 bp (mono-nucleosome), ~400 bp (di-nucleosome), ~600 bp (tri-nucleosome). Sub-nucleosomal peak at ~100-150 bp (open chromatin)
- **Input/IgG**: Broad distribution centered ~200-300 bp (random fragmentation)
- **Red flag**: Very narrow distribution or peak at fragment size boundaries suggests size selection artifacts

**Expected Output:**
- Histogram PNG showing fragment size distribution for each sample
- Summary metrics table with median, mean, and standard deviation
- Raw fragment length data for custom downstream analysis

---

## Recipe 12: alignmentSieve for Fragment Size Filtering

Filter BAM files by fragment size to isolate specific chromatin fractions (nucleosomal, sub-nucleosomal).

```bash
# ATAC-seq: Extract nucleosome-free fragments (< 150 bp)
# These represent open chromatin / TF footprints
alignmentSieve \
  --bam atac_sample.bam \
  -o atac_nfr.bam \
  --minFragmentLength 0 \
  --maxFragmentLength 150 \
  --ATACshift \
  --numberOfProcessors max
samtools index atac_nfr.bam

# ATAC-seq: Extract mono-nucleosomal fragments (150-300 bp)
# These represent positioned nucleosomes
alignmentSieve \
  --bam atac_sample.bam \
  -o atac_mono_nuc.bam \
  --minFragmentLength 150 \
  --maxFragmentLength 300 \
  --numberOfProcessors max
samtools index atac_mono_nuc.bam

# ATAC-seq: Extract di-nucleosomal fragments (300-500 bp)
alignmentSieve \
  --bam atac_sample.bam \
  -o atac_di_nuc.bam \
  --minFragmentLength 300 \
  --maxFragmentLength 500 \
  --numberOfProcessors max
samtools index atac_di_nuc.bam

# ChIP-seq: Filter for nucleosomal fragments only (remove sub-nucleosomal)
alignmentSieve \
  --bam chip_h3k27ac.bam \
  -o chip_nucleosomal.bam \
  --minFragmentLength 150 \
  --maxFragmentLength 1000 \
  --minMappingQuality 30 \
  --ignoreDuplicates \
  --numberOfProcessors max
samtools index chip_nucleosomal.bam

# Generate signal tracks for each fraction
for frac in atac_nfr atac_mono_nuc atac_di_nuc; do
  bamCoverage \
    --bam ${frac}.bam \
    -o ${frac}_rpgc.bw \
    --normalizeUsing RPGC \
    --effectiveGenomeSize 2913022398 \
    --binSize 10 \
    --numberOfProcessors max
done

echo "Fragment size fractions:"
for f in atac_nfr.bam atac_mono_nuc.bam atac_di_nuc.bam; do
  count=$(samtools view -c -F 1804 $f)
  echo "  $f: $count reads"
done
```

**Key Parameters:**
- `--minFragmentLength / --maxFragmentLength`: Fragment size boundaries for filtering
- `--ATACshift`: Apply Tn5 transposase offset correction (+4 bp on + strand, -5 bp on - strand). Essential for ATAC-seq; do NOT use for ChIP-seq
- `--minMappingQuality 30`: Filter low-quality alignments
- `--ignoreDuplicates`: Skip PCR duplicates

**Fragment Size Ranges:**

| Fraction | Size Range | Represents | Use For |
|----------|-----------|------------|---------|
| **NFR** | 0-150 bp | Nucleosome-free regions | TF footprinting, open chromatin |
| **Mono-nucleosome** | 150-300 bp | Single nucleosomes | Nucleosome positioning, histone marks |
| **Di-nucleosome** | 300-500 bp | Two adjacent nucleosomes | Chromatin compaction analysis |
| **Tri-nucleosome** | 500-700 bp | Three nucleosomes | Heterochromatin, compacted regions |

**Expected Output:**
- Filtered BAM files containing only fragments in the specified size range
- Indexed BAM files ready for signal track generation or peak calling
- Read counts per fraction for assessing ATAC-seq library composition (expect ~50-70% NFR for good libraries)

---

## Quick Reference

| Task | Recipe | Key Command |
|------|--------|-------------|
| RPGC normalization | #1 | `bamCoverage --normalizeUsing RPGC` |
| Normalization comparison | #2 | `bamCoverage` (CPM/BPM/RPKM/RPGC) |
| ChIP/input ratio | #3 | `bamCompare --operation log2ratio` |
| Library complexity QC | #4 | `plotFingerprint` |
| Sample correlation | #5 | `multiBamSummary + plotCorrelation` |
| Signal PCA | #6 | `multiBigwigSummary + plotPCA` |
| Signal at TSS/TES | #7 | `computeMatrix reference-point` |
| Signal across gene bodies | #8 | `computeMatrix scale-regions` |
| Publication heatmap | #9 | `plotHeatmap` |
| Average signal profile | #10 | `plotProfile` |
| Fragment size QC | #11 | `bamPEFragmentSize` |
| Fragment size filtering | #12 | `alignmentSieve` |

---

## Cross-Skill Routing

- Peak calling (MACS2), differential binding (DiffBind), motif analysis (HOMER) --> [chipseq-recipes.md](chipseq-recipes.md)
- DNA methylation analysis and epigenetic clocks --> [recipes.md](recipes.md)
- Full epigenomics analysis pipeline --> parent [SKILL.md](SKILL.md)
- Statistical test selection and multiple testing correction --> `biostat-recipes`
- Pathway enrichment on peak-associated gene lists --> `gene-enrichment`
