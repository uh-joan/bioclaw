# ChIP-seq & ATAC-seq Analysis Recipes

Copy-paste-ready bash/Python/R code for ChIP-seq and ATAC-seq data processing and analysis.
Dependencies: `macs2`, `deeptools`, `samtools`, `bedtools`, `homer`, `idr`, Python (`pandas`, `numpy`, `scipy`, `pybedtools`), R (`DiffBind`, `ChIPseeker`, `chromVAR`, `methylKit`).

---

## 1. MACS2 Narrow Peak Calling (Transcription Factors)

Call sharp, focal peaks for transcription factors and histone marks like H3K4me3, H3K27ac.

```bash
macs2 callpeak \
  -t chip_treatment.bam \
  -c chip_input.bam \
  -f BAMPE \
  -g hs \
  --keep-dup auto \
  --outdir macs2_narrow \
  -n TF_sample \
  -q 0.05 \
  --call-summits
```

**Key Parameters:**
- `-f BAMPE`: Paired-end BAM; use `-f BAM` for single-end
- `-g hs`: Effective genome size (`hs` = human ~2.7e9, `mm` = mouse ~1.87e9, or exact integer)
- `--keep-dup auto`: MACS2 estimates duplication rate; use `1` for strict dedup or `all` to keep all
- `-q 0.05`: FDR cutoff; use `0.01` for stringent calling
- `--call-summits`: Report summit positions within peaks (useful for motif analysis)

**Expected Output:**
- `TF_sample_peaks.narrowPeak`: BED6+4 with peak coordinates, -log10(qvalue), fold-enrichment, summit offset
- `TF_sample_summits.bed`: Single-bp summit positions
- `TF_sample_peaks.xls`: Tab-delimited peak statistics
- `TF_sample_model.r`: R script to visualize fragment length model

---

## 2. MACS2 Broad Peak Calling (Histone Marks)

Call broad, diffuse peaks for marks like H3K36me3, H3K27me3, H3K9me3.

```bash
macs2 callpeak \
  -t chip_h3k27me3.bam \
  -c chip_input.bam \
  -f BAMPE \
  -g hs \
  --keep-dup auto \
  --broad \
  --broad-cutoff 0.1 \
  --outdir macs2_broad \
  -n H3K27me3_sample \
  --nomodel \
  --extsize 147
```

**Key Parameters:**
- `--broad`: Enable broad peak calling mode (merges nearby enriched regions)
- `--broad-cutoff 0.1`: Loose q-value for linking sub-peaks into broad domains; use `0.05` for stricter
- `--nomodel --extsize 147`: Skip fragment size estimation; set fixed extension (use for broad marks or low signal)
- Broad marks often need deeper sequencing (>30M reads) for reliable peak calls

**Expected Output:**
- `H3K27me3_sample_peaks.broadPeak`: BED6+3 with broad peak coordinates
- `H3K27me3_sample_peaks.gappedPeak`: Nested narrow peaks within broad regions

---

## 3. DiffBind: Differential Binding Analysis

Identify differentially bound regions between conditions using DiffBind (R/Bioconductor).

```r
library(DiffBind)

# Create sample sheet (CSV with columns: SampleID, Tissue, Factor, Condition, Replicate,
#   bamReads, ControlID, bamControl, Peaks, PeakCaller)
samples <- read.csv("diffbind_samplesheet.csv")
dba_obj <- dba(sampleSheet = samples)

# Count reads in consensus peaks (re-centers and resizes peaks to fixed width)
dba_obj <- dba.count(dba_obj, bUseSummarizeOverlaps = TRUE)

# Establish contrast
dba_obj <- dba.contrast(dba_obj, categories = DBA_CONDITION,
                        minMembers = 2)

# Run differential analysis (DESeq2 is default; edgeR also available)
dba_obj <- dba.analyze(dba_obj, method = DBA_DESEQ2)

# Extract results
results <- dba.report(dba_obj, th = 0.05, bCounts = TRUE)
results_df <- as.data.frame(results)

# Summary
cat(sprintf("Total DB sites: %d\n", nrow(results_df)))
cat(sprintf("  Gained: %d\n", sum(results_df$Fold > 0)))
cat(sprintf("  Lost: %d\n", sum(results_df$Fold < 0)))

# Visualizations
dba.plotMA(dba_obj)
dba.plotVolcano(dba_obj)
dba.plotHeatmap(dba_obj, contrast = 1, correlations = FALSE)
dba.plotPCA(dba_obj, DBA_CONDITION)

write.csv(results_df, "diffbind_results.csv", row.names = FALSE)
```

**Key Parameters:**
- `bUseSummarizeOverlaps = TRUE`: Use Bioconductor counting (more accurate than default)
- `method = DBA_DESEQ2`: DESeq2 for differential analysis; `DBA_EDGER` for edgeR
- `th = 0.05`: FDR threshold for reporting
- `bCounts = TRUE`: Include raw count matrix in results

**Expected Output:**
- DataFrame with columns: Chr, Start, End, Conc, Conc_condition1, Conc_condition2, Fold, p.value, FDR
- MA plot, volcano plot, PCA, and heatmap visualizations

---

## 4. deepTools: Signal Heatmaps and Profiles

Compute signal matrices and generate publication-quality heatmaps and profile plots.

```bash
# Step 1: Compute matrix around TSSs (reference-point mode)
computeMatrix reference-point \
  --referencePoint TSS \
  -b 3000 -a 3000 \
  -R genes.bed \
  -S sample1.bw sample2.bw \
  --skipZeros \
  --missingDataAsZero \
  -o matrix_tss.gz \
  -p max

# Step 2: Plot heatmap
plotHeatmap \
  -m matrix_tss.gz \
  -o heatmap_tss.png \
  --colorMap RdBu_r \
  --whatToShow 'heatmap and colorbar' \
  --sortUsing mean \
  --zMin -2 --zMax 2 \
  --heatmapHeight 15

# Step 3: Plot profile (average signal)
plotProfile \
  -m matrix_tss.gz \
  -o profile_tss.png \
  --perGroup \
  --plotHeight 7 \
  --plotWidth 10

# Alternative: scale-regions mode (gene body)
computeMatrix scale-regions \
  -R genes.bed \
  -S sample1.bw sample2.bw \
  -b 3000 -a 3000 \
  --regionBodyLength 5000 \
  --skipZeros \
  -o matrix_scaled.gz \
  -p max

plotHeatmap -m matrix_scaled.gz -o heatmap_scaled.png --colorMap YlOrRd
```

**Key Parameters:**
- `reference-point --referencePoint TSS`: Center signal around TSS; also `TES`, `center`
- `scale-regions --regionBodyLength 5000`: Scale gene bodies to uniform length
- `-b 3000 -a 3000`: Upstream/downstream flanking regions in bp
- `--sortUsing mean`: Sort rows by mean signal; also `max`, `sum`, `region_length`
- `--colorMap RdBu_r`: Matplotlib colormap name
- `-p max`: Use all available CPU cores

**Expected Output:**
- Compressed matrix file (`.gz`) for reuse
- Heatmap PNG showing per-gene signal across conditions
- Profile PNG showing average signal curve around reference point

---

## 5. Signal Normalization with bamCoverage

Generate normalized bigWig signal tracks for visualization and downstream analysis.

```bash
# RPGC normalization (Reads Per Genomic Content / 1x depth)
bamCoverage \
  --bam chip_sample.bam \
  -o sample_rpgc.bw \
  --normalizeUsing RPGC \
  --effectiveGenomeSize 2913022398 \
  --binSize 10 \
  --extendReads \
  --ignoreDuplicates \
  -p max

# CPM normalization (Counts Per Million mapped reads)
bamCoverage \
  --bam chip_sample.bam \
  -o sample_cpm.bw \
  --normalizeUsing CPM \
  --binSize 10 \
  --extendReads \
  -p max

# BPM normalization (Bins Per Million - like CPM but per bin)
bamCoverage \
  --bam chip_sample.bam \
  -o sample_bpm.bw \
  --normalizeUsing BPM \
  --binSize 10 \
  --extendReads \
  -p max

# Input-subtracted signal (log2 ratio)
bamCompare \
  -b1 chip_treatment.bam \
  -b2 chip_input.bam \
  -o log2ratio.bw \
  --scaleFactorsMethod readCount \
  --operation log2ratio \
  --binSize 50 \
  --extendReads \
  -p max
```

**Key Parameters:**
- `--normalizeUsing RPGC`: Best for cross-sample comparison; requires `--effectiveGenomeSize`
- `--effectiveGenomeSize`: Human GRCh38 = 2913022398, Mouse mm10 = 2652783500
- `--binSize 10`: Resolution in bp; smaller = higher resolution but larger file
- `--extendReads`: Extend reads to fragment size (auto-detected for PE, or set `--extendReads 200`)
- `--ignoreDuplicates`: Exclude PCR/optical duplicates

**Expected Output:**
- BigWig (`.bw`) file for genome browser visualization
- `bamCompare` log2ratio track showing enrichment relative to input

---

## 6. Peak Annotation with ChIPseeker (R)

Annotate peaks with genomic features and visualize distribution relative to genes.

```r
library(ChIPseeker)
library(TxDb.Hsapiens.UCSC.hg38.knownGene)
library(org.Hs.eg.db)

txdb <- TxDb.Hsapiens.UCSC.hg38.knownGene

# Read peaks
peaks <- readPeakFile("macs2_narrow/TF_sample_peaks.narrowPeak")

# Annotate peaks with genomic features
peakAnno <- annotatePeak(peaks, tssRegion = c(-3000, 3000),
                         TxDb = txdb, annoDb = "org.Hs.eg.db")

# Visualization
plotAnnoPie(peakAnno)
plotAnnoBar(peakAnno)
plotDistToTSS(peakAnno, title = "Distribution of Peaks Relative to TSS")

# Functional profile of peak-associated genes
genes <- as.data.frame(peakAnno)$geneId
genes <- genes[!is.na(genes)]

# GO enrichment of peak-associated genes
library(clusterProfiler)
ego <- enrichGO(gene = genes, OrgDb = org.Hs.eg.db,
                ont = "BP", pAdjustMethod = "BH",
                pvalueCutoff = 0.05, readable = TRUE)
dotplot(ego, showCategory = 20)

# Export annotated peaks
write.csv(as.data.frame(peakAnno), "peaks_annotated.csv", row.names = FALSE)
```

**Key Parameters:**
- `tssRegion = c(-3000, 3000)`: Define promoter region as +/- 3kb from TSS
- `TxDb`: Transcript database; use `TxDb.Mmusculus.UCSC.mm10.knownGene` for mouse
- `annoDb = "org.Hs.eg.db"`: Gene annotation database for symbol mapping

**Expected Output:**
- Pie chart showing genomic feature distribution (Promoter, 5'UTR, Exon, Intron, 3'UTR, Intergenic)
- Bar plot of annotation categories
- TSS distance distribution plot
- Annotated peak table with gene assignments

---

## 7. Motif Analysis with HOMER

Discover enriched TF binding motifs in peak regions.

```bash
# De novo and known motif discovery
findMotifsGenome.pl \
  macs2_narrow/TF_sample_peaks.narrowPeak \
  hg38 \
  homer_output/ \
  -size 200 \
  -mask \
  -p 8 \
  -preparsedDir homer_preparsed/

# Use summit-centered regions for sharper motif discovery
awk '{print $1"\t"$2+$10-100"\t"$2+$10+100"\t"$4"\t"$5"\t"+"}' \
  macs2_narrow/TF_sample_peaks.narrowPeak > summits_200bp.bed

findMotifsGenome.pl summits_200bp.bed hg38 homer_summit_output/ \
  -size given -mask -p 8

# Scan specific motif in peaks
annotatePeaks.pl \
  macs2_narrow/TF_sample_peaks.narrowPeak \
  hg38 \
  -m homer_output/homerResults/motif1.motif \
  > motif_instances.txt
```

**Key Parameters:**
- `-size 200`: Extract 200bp centered on peak summit for motif analysis; use `given` to use actual peak coordinates
- `-mask`: Mask repeat regions to avoid repetitive element motifs
- `-p 8`: Number of parallel threads
- `-preparsedDir`: Cache pre-parsed genome for faster re-runs
- Default discovers both de novo motifs and matches to known motif databases (JASPAR, TRANSFAC)

**Expected Output:**
- `homerResults.html`: Interactive report with de novo motifs, p-values, % of targets with motif
- `knownResults.html`: Enrichment of known TF motifs
- `homerResults/motif*.motif`: Position weight matrices for discovered motifs
- Motif logos as PNG images

---

## 8. FRiP Calculation (Fraction of Reads in Peaks)

Calculate the fraction of reads falling within called peaks -- key QC metric for ChIP-seq/ATAC-seq.

```python
import subprocess
import pandas as pd

def calculate_frip(bam_path, peak_path):
    """Calculate FRiP (Fraction of Reads in Peaks).

    ENCODE minimum: FRiP >= 0.01 (1%) for TFs, >= 0.05 (5%) for histone marks.
    Good experiments: FRiP 0.1-0.3 for TFs, 0.3-0.7 for histone marks.
    """
    # Total mapped reads (exclude unmapped, secondary, supplementary, duplicates)
    cmd_total = f"samtools view -c -F 1804 {bam_path}"
    total_reads = int(subprocess.check_output(cmd_total, shell=True).strip())

    # Reads in peaks
    cmd_in_peaks = f"bedtools intersect -a {bam_path} -b {peak_path} -u -f 0.20 | samtools view -c -"
    reads_in_peaks = int(subprocess.check_output(cmd_in_peaks, shell=True).strip())

    frip = reads_in_peaks / total_reads if total_reads > 0 else 0

    print(f"Total mapped reads: {total_reads:,}")
    print(f"Reads in peaks:     {reads_in_peaks:,}")
    print(f"FRiP:               {frip:.4f} ({frip*100:.2f}%)")

    # Quality assessment
    if frip >= 0.05:
        quality = "PASS"
    elif frip >= 0.01:
        quality = "MARGINAL"
    else:
        quality = "FAIL"
    print(f"Quality:            {quality}")

    return {"total_reads": total_reads, "reads_in_peaks": reads_in_peaks,
            "frip": frip, "quality": quality}

# Example usage
frip_result = calculate_frip("chip_sample.bam", "macs2_narrow/TF_sample_peaks.narrowPeak")
```

**Key Parameters:**
- `-F 1804`: Exclude unmapped (4), not primary (256), fails QC (512), duplicate (1024)
- `-f 0.20`: Minimum overlap fraction (20% of read must overlap peak)

**Expected Output:**
- FRiP value (float between 0 and 1)
- Quality classification: PASS (>=5%), MARGINAL (1-5%), FAIL (<1%)

---

## 9. IDR (Irreproducible Discovery Rate) for Replicate Concordance

Assess replicate agreement and generate a conservative peak set.

```bash
# Step 1: Call peaks on individual replicates (relaxed threshold)
macs2 callpeak -t rep1.bam -c input.bam -f BAMPE -g hs \
  --keep-dup all -p 0.01 --nomodel --extsize 147 \
  -n rep1 --outdir idr_peaks/

macs2 callpeak -t rep2.bam -c input.bam -f BAMPE -g hs \
  --keep-dup all -p 0.01 --nomodel --extsize 147 \
  -n rep2 --outdir idr_peaks/

# Step 2: Sort peaks by -log10(p-value) (column 8 in narrowPeak)
sort -k8,8nr idr_peaks/rep1_peaks.narrowPeak > rep1_sorted.narrowPeak
sort -k8,8nr idr_peaks/rep2_peaks.narrowPeak > rep2_sorted.narrowPeak

# Step 3: Run IDR
idr --samples rep1_sorted.narrowPeak rep2_sorted.narrowPeak \
    --input-file-type narrowPeak \
    --rank p.value \
    --output-file idr_output.narrowPeak \
    --plot \
    --log-output-file idr_log.txt

# Step 4: Filter by IDR threshold
# ENCODE uses IDR < 0.05 for optimal set
awk '{if($5 >= 540) print $0}' idr_output.narrowPeak > idr_optimal.narrowPeak
# IDR < 0.05 corresponds to -125*log2(0.05) = 540 in the scaled IDR score (column 5)

echo "Optimal peaks (IDR < 0.05): $(wc -l < idr_optimal.narrowPeak)"
```

**Key Parameters:**
- Use relaxed peak calling (`-p 0.01`) for IDR input -- IDR handles the thresholding
- `--rank p.value`: Rank peaks by p-value; also `signal.value`, `q.value`
- IDR score in column 5 is `-125 * log2(IDR)`: 540 = IDR 0.05, 830 = IDR 0.01
- `--plot`: Generate diagnostic IDR plot

**Expected Output:**
- `idr_output.narrowPeak`: All peaks with IDR scores
- `idr_optimal.narrowPeak`: Reproducible peaks passing IDR threshold
- IDR diagnostic plot showing replicate concordance

---

## 10. Super-Enhancer Calling with ROSE

Identify super-enhancers from H3K27ac ChIP-seq using the ROSE algorithm.

```bash
# Prerequisites: ROSE (https://github.com/stjude/ROSE)
# Requires: H3K27ac peaks (exclude promoters), H3K27ac BAM, input BAM

# Step 1: Remove promoter peaks (within 2.5kb of TSS)
# ROSE does this internally, but for transparency:
bedtools intersect -a h3k27ac_peaks.bed -b promoters_2500bp.bed -v > enhancer_peaks.bed

# Step 2: Run ROSE
python ROSE_main.py \
  -g hg38 \
  -i h3k27ac_peaks.gff \
  -r h3k27ac.bam \
  -c input.bam \
  -o rose_output/ \
  -s 12500 \
  -t 2500

# Alternative: Manual ROSE-like implementation in Python
```

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def call_super_enhancers(peaks_df, signal_col="signal", stitch_distance=12500):
    """ROSE-like super-enhancer calling.

    Stitches nearby enhancers, ranks by signal, applies inflection-point cutoff.

    Args:
        peaks_df: DataFrame with chr, start, end, signal columns
        signal_col: Column name for signal intensity
        stitch_distance: Maximum distance (bp) to stitch adjacent peaks
    """
    # Sort by position
    peaks = peaks_df.sort_values(["chr", "start"]).reset_index(drop=True)

    # Stitch nearby peaks
    stitched = []
    current = peaks.iloc[0].to_dict()
    for i in range(1, len(peaks)):
        row = peaks.iloc[i]
        if (row["chr"] == current["chr"] and
            row["start"] - current["end"] <= stitch_distance):
            current["end"] = max(current["end"], row["end"])
            current[signal_col] += row[signal_col]
        else:
            stitched.append(current)
            current = row.to_dict()
    stitched.append(current)
    stitched_df = pd.DataFrame(stitched)

    # Rank by signal and find inflection point
    stitched_df = stitched_df.sort_values(signal_col).reset_index(drop=True)
    stitched_df["rank"] = range(1, len(stitched_df) + 1)
    signals_norm = stitched_df[signal_col] / stitched_df[signal_col].max()

    # Inflection: point where slope of rank-signal curve exceeds 1
    slopes = np.diff(signals_norm) / np.diff(stitched_df["rank"].values.astype(float))
    cutoff_idx = np.where(slopes > 1.0 / len(stitched_df))[0]
    cutoff_rank = cutoff_idx[-1] + 1 if len(cutoff_idx) > 0 else len(stitched_df) - 1

    stitched_df["is_super"] = stitched_df["rank"] > cutoff_rank
    n_se = stitched_df["is_super"].sum()
    n_te = (~stitched_df["is_super"]).sum()

    print(f"Stitched enhancers: {len(stitched_df)}")
    print(f"Super-enhancers: {n_se} ({n_se/len(stitched_df)*100:.1f}%)")
    print(f"Typical enhancers: {n_te}")

    # Hockey stick plot
    fig, ax = plt.subplots(figsize=(8, 6))
    te = stitched_df[~stitched_df["is_super"]]
    se = stitched_df[stitched_df["is_super"]]
    ax.scatter(te["rank"], te[signal_col], c="grey", s=5, label=f"Typical ({n_te})")
    ax.scatter(se["rank"], se[signal_col], c="red", s=10, label=f"Super ({n_se})")
    ax.axvline(cutoff_rank, color="black", linestyle="--", linewidth=0.8)
    ax.set_xlabel("Enhancer Rank"); ax.set_ylabel("Signal")
    ax.set_title("Super-Enhancer Calling (ROSE)"); ax.legend()
    plt.tight_layout(); plt.savefig("super_enhancers.png", dpi=150)

    return stitched_df

# se_results = call_super_enhancers(peaks_df, signal_col="fold_enrichment")
```

**Key Parameters:**
- `stitch_distance = 12500`: ROSE default; stitches enhancers within 12.5kb
- `-t 2500`: Exclude peaks within 2.5kb of TSS (promoters)
- Signal column should be fold-enrichment or read count from ChIP-seq
- Inflection point defines the boundary between typical and super-enhancers

**Expected Output:**
- Table of stitched enhancers with super-enhancer classification
- Hockey stick plot showing signal rank vs intensity with cutoff line
- Super-enhancers typically comprise 2-5% of all enhancers but drive >50% of enhancer activity

---

## 11. methylKit: DMR Detection from Bisulfite Sequencing

Detect differentially methylated regions from WGBS or RRBS data using methylKit (R).

```r
library(methylKit)

# Read coverage files (Bismark, BSMap, or methylKit format)
file_list <- list(
  "sample1.CpG_report.txt", "sample2.CpG_report.txt",
  "sample3.CpG_report.txt", "sample4.CpG_report.txt"
)
sample_ids <- c("ctrl_1", "ctrl_2", "treat_1", "treat_2")
treatment <- c(0, 0, 1, 1)

obj <- methRead(file_list, sample.id = sample_ids,
                assembly = "hg38", treatment = treatment,
                context = "CpG", mincov = 10)

# QC: coverage and methylation statistics
getMethylationStats(obj[[1]], plot = TRUE, both.strands = FALSE)
getCoverageStats(obj[[1]], plot = TRUE, both.strands = FALSE)

# Filter by coverage (remove extremely high coverage -- possible PCR bias)
filtered <- filterByCoverage(obj, lo.count = 10, lo.perc = NULL,
                             hi.count = NULL, hi.perc = 99.9)

# Normalize coverage between samples
normalized <- normalizeCoverage(filtered, method = "median")

# Merge samples to get sites covered in all
meth_merged <- unite(normalized, destrand = FALSE)

# Tile into regions (optional: for regional analysis)
tiles <- tileMethylCounts(obj, win.size = 1000, step.size = 1000)
tiles_merged <- unite(tiles, destrand = FALSE)

# Differential methylation at CpG level
dm <- calculateDiffMeth(meth_merged, overdispersion = "MN", test = "Chisq",
                        adjust = "BH")

# Extract significant DMPs
hyper <- getMethylDiff(dm, difference = 25, qvalue = 0.01, type = "hyper")
hypo  <- getMethylDiff(dm, difference = 25, qvalue = 0.01, type = "hypo")
all_sig <- getMethylDiff(dm, difference = 25, qvalue = 0.01, type = "all")

cat(sprintf("Hypermethylated: %d\nHypomethylated: %d\nTotal DMPs: %d\n",
            nrow(hyper), nrow(hypo), nrow(all_sig)))

# Differential methylation at region level
dm_tiles <- calculateDiffMeth(tiles_merged, overdispersion = "MN",
                              test = "Chisq", adjust = "BH")
dmr <- getMethylDiff(dm_tiles, difference = 25, qvalue = 0.01)
cat(sprintf("DMRs: %d\n", nrow(dmr)))

# Export
write.csv(as.data.frame(all_sig), "methylkit_dmps.csv", row.names = FALSE)
write.csv(as.data.frame(dmr), "methylkit_dmrs.csv", row.names = FALSE)
```

**Key Parameters:**
- `mincov = 10`: Minimum coverage per site (ENCODE recommends 10x for WGBS)
- `hi.perc = 99.9`: Remove top 0.1% coverage (likely PCR duplicates)
- `overdispersion = "MN"`: Model overdispersion; use `"none"` if samples are very similar
- `difference = 25`: Minimum methylation difference (25 percentage points)
- `qvalue = 0.01`: FDR-corrected significance threshold
- `win.size = 1000`: Window size for tiling (1kb default for DMR detection)

**Expected Output:**
- Per-CpG DMP table with chr, start, end, q-value, methylation difference
- Per-region DMR table for tiled analysis
- Separate hyper/hypo-methylated site lists

---

## 12. chromVAR: TF Deviation Scores from ATAC-seq

Compute transcription factor accessibility deviation scores from ATAC-seq count matrices.

```r
library(chromVAR)
library(motifmatchr)
library(BSgenome.Hsapiens.UCSC.hg38)
library(JASPAR2020)
library(TFBSTools)

# Load peak count matrix (peaks x samples)
counts <- readRDS("peak_counts.rds")  # SummarizedExperiment or matrix

# Create RangedSummarizedExperiment if needed
library(GenomicRanges)
peaks <- GRanges(seqnames = peak_df$chr,
                 ranges = IRanges(start = peak_df$start, end = peak_df$end))
se <- SummarizedExperiment(assays = list(counts = count_matrix),
                           rowRanges = peaks)

# Add GC bias
se <- addGCBias(se, genome = BSgenome.Hsapiens.UCSC.hg38)

# Filter low-count peaks
se <- filterPeaks(se, non_overlapping = TRUE)

# Get JASPAR motifs
pfm <- getMatrixSet(JASPAR2020, opts = list(collection = "CORE",
                                             tax_group = "vertebrates",
                                             all_versions = FALSE))

# Match motifs in peaks
motif_matches <- matchMotifs(pfm, se, genome = BSgenome.Hsapiens.UCSC.hg38)

# Compute deviations
dev <- computeDeviations(object = se, annotations = motif_matches)

# Extract deviation scores and variability
dev_scores <- deviationScores(dev)
variability <- computeVariability(dev)

# Top variable TFs
top_var <- variability[order(-variability$variability), ]
cat("Top 20 variable TFs:\n")
print(head(top_var, 20))

# Plot variability
plotVariability(variability, use_plotly = FALSE, n = 25)

# Differential TF activity between conditions
library(limma)
condition <- factor(c("ctrl", "ctrl", "ctrl", "treat", "treat", "treat"))
design <- model.matrix(~ condition)
fit <- eBayes(lmFit(dev_scores, design))
diff_tf <- topTable(fit, coef = 2, number = Inf, sort.by = "p")
sig_tf <- diff_tf[diff_tf$adj.P.Val < 0.05, ]
cat(sprintf("Differentially active TFs: %d\n", nrow(sig_tf)))

# Heatmap of top variable TF deviations
library(pheatmap)
top_tfs <- head(top_var, 30)$name
pheatmap(dev_scores[top_tfs, ],
         scale = "row",
         annotation_col = data.frame(Condition = condition,
                                     row.names = colnames(dev_scores)),
         main = "TF Deviation Scores (chromVAR)")

write.csv(diff_tf, "chromvar_differential_tfs.csv", row.names = TRUE)
```

**Key Parameters:**
- `addGCBias`: Critical -- corrects for GC content bias in ATAC-seq
- `filterPeaks(non_overlapping = TRUE)`: Remove overlapping peaks to avoid double-counting
- JASPAR `collection = "CORE"`: Curated non-redundant motifs; `all_versions = FALSE` avoids redundancy
- Deviation z-scores: positive = more accessible than expected, negative = less accessible

**Expected Output:**
- Deviation z-score matrix (TFs x samples)
- Variability scores ranking TFs by cross-sample variation
- Differential TF activity table with limma statistics
- Heatmap of top variable TF deviations across samples

---

## Quick Reference

| Task | Recipe | Key tool/function |
|------|--------|-------------------|
| Narrow peak calling (TFs) | #1 | `macs2 callpeak` |
| Broad peak calling (histones) | #2 | `macs2 callpeak --broad` |
| Differential binding | #3 | `DiffBind::dba.analyze()` |
| Signal heatmaps | #4 | `deepTools computeMatrix + plotHeatmap` |
| Signal normalization | #5 | `bamCoverage --normalizeUsing` |
| Peak annotation | #6 | `ChIPseeker::annotatePeak()` |
| Motif discovery | #7 | `findMotifsGenome.pl` |
| FRiP QC metric | #8 | `samtools + bedtools` |
| Replicate concordance | #9 | `idr --samples` |
| Super-enhancers | #10 | ROSE / hockey-stick inflection |
| Bisulfite-seq DMR | #11 | `methylKit::calculateDiffMeth()` |
| TF deviation scores | #12 | `chromVAR::computeDeviations()` |

---

## Cross-Skill Routing

- Methylation array data (450K, EPIC, beta values) --> `epigenomics` recipes
- Statistical test details and assumptions --> `biostat-recipes`
- Pathway enrichment on peak-associated gene lists --> `gene-enrichment`
- Integration with expression or proteomics data --> `multi-omics-integration`
- Single-cell ATAC-seq clustering and analysis --> `single-cell-analysis`
