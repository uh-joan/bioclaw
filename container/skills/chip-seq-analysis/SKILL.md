---
name: chip-seq-analysis
description: ChIP-seq analysis for transcription factor binding and histone modifications. Peak calling with MACS2 and MACS3 for narrow and broad peaks, input and IgG control normalization, de novo motif discovery with HOMER and MEME-ChIP, known motif enrichment, differential binding with DiffBind, super-enhancer identification with ROSE algorithm, peak annotation with ChIPseeker, signal visualization with deepTools, quality metrics including FRiP and strand cross-correlation and IDR, CUT&RUN and CUT&Tag analysis with SEACR and spike-in normalization. Use when user asks about ChIP-seq, ChIP sequencing, transcription factor binding, histone modification, histone marks, peak calling, MACS2, MACS3, narrow peaks, broad peaks, H3K27ac, H3K4me3, H3K27me3, H3K4me1, super-enhancer, ROSE, DiffBind, motif discovery, HOMER, MEME-ChIP, deepTools, CUT&RUN, CUT&Tag, SEACR, IDR, FRiP, or chromatin immunoprecipitation.
---

# ChIP-seq Analysis for TF Binding and Histone Modifications

Comprehensive pipeline for Chromatin Immunoprecipitation followed by sequencing. Covers transcription factor (TF) ChIP-seq with narrow peak calling, histone modification ChIP-seq with broad peak calling, and modern low-input alternatives (CUT&RUN, CUT&Tag).

## Report-First Workflow

1. **Create report file immediately**: `[topic]_chipseq_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as analysis completes
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- ATAC-seq chromatin accessibility analysis -> use `atac-seq-analysis`
- DNA methylation from bisulfite-seq or arrays -> use `epigenomics`
- Deep pathway enrichment on ChIP target genes -> use `gene-enrichment`
- Single-cell ChIP-seq or scCUT&Tag clustering -> use `single-cell-analysis`
- Multi-omics integration (ChIP + RNA-seq) -> use `multi-omics-integration`

## Cross-Reference: Other Skills

- **ATAC-seq open chromatin** -> use atac-seq-analysis skill
- **Pathway enrichment on TF target genes** -> use gene-enrichment skill
- **Gene regulatory network inference from ChIP data** -> use gene-regulatory-networks skill
- **Methylation at TF binding sites** -> use epigenomics skill

---

## ChIP-seq Experimental Context

### Antibody Types and Peak Characteristics

| Target Class | Examples | Peak Shape | Peak Caller Mode | Typical Peak Count |
|-------------|----------|------------|-------------------|--------------------|
| Transcription Factors | CTCF, p53, GATA1, MYC | Narrow, focal | MACS2/3 default (narrow) | 5,000 - 100,000 |
| Active histone marks | H3K4me3, H3K27ac, H3K9ac | Narrow-moderate | MACS2/3 default or `--broad` | 20,000 - 80,000 |
| Enhancer marks | H3K4me1 | Moderate | `--broad` | 30,000 - 100,000 |
| Broad repressive marks | H3K27me3, H3K9me3, H3K36me3 | Broad, diffuse | MACS2/3 `--broad` | 10,000 - 50,000 domains |
| RNA Pol II | POLR2A | Variable | Narrow (promoter) or broad (gene body) | 10,000 - 50,000 |

### Histone Mark Reference

| Mark | Activation | Location | Function | Peak Type |
|------|-----------|----------|----------|-----------|
| H3K4me3 | Activating | Promoters | Active transcription initiation | Narrow |
| H3K4me1 | Activating | Enhancers | Enhancer priming (active + poised) | Broad |
| H3K27ac | Activating | Enhancers, Promoters | Distinguishes active from poised | Narrow |
| H3K36me3 | Activating | Gene bodies | Transcription elongation | Broad |
| H3K9ac | Activating | Promoters | Active transcription | Narrow |
| H3K27me3 | Repressive | Promoters, gene bodies | Polycomb silencing (reversible) | Broad |
| H3K9me3 | Repressive | Heterochromatin | Constitutive silencing | Broad |

---

## Phase 1: Read Alignment and Filtering

### Alignment

```bash
# Bowtie2 alignment for ChIP-seq
bowtie2 --very-sensitive -p 16 -x /ref/bowtie2/hg38 \
  -1 sample_R1.fastq.gz -2 sample_R2.fastq.gz \
  | samtools sort -@ 8 -o sample.sorted.bam

# For single-end data
bowtie2 --very-sensitive -p 16 -x /ref/bowtie2/hg38 \
  -U sample.fastq.gz \
  | samtools sort -@ 8 -o sample.sorted.bam

samtools index sample.sorted.bam
```

### Filtering Pipeline

```bash
# Mark and remove PCR duplicates
picard MarkDuplicates \
  INPUT=sample.sorted.bam \
  OUTPUT=sample.dedup.bam \
  METRICS_FILE=sample.dup_metrics.txt \
  REMOVE_DUPLICATES=true

# Filter: MAPQ >= 30, proper pairs (PE) or mapped (SE), no secondary/supplementary
# For paired-end:
samtools view -b -f 2 -F 1804 -q 30 sample.dedup.bam > sample.filtered.bam
# For single-end:
samtools view -b -F 1796 -q 30 sample.dedup.bam > sample.filtered.bam

# Remove blacklist regions
bedtools intersect -v -abam sample.filtered.bam \
  -b /ref/hg38-blacklist.v2.bed > sample.final.bam
samtools index sample.final.bam
```

---

## Phase 2: Quality Control Metrics

### Strand Cross-Correlation (phantompeakqualtools)

```bash
# Run phantompeakqualtools for NSC and RSC metrics
run_spp.R -c=sample.final.bam -savp=sample_cc_plot.pdf \
  -out=sample_cc_metrics.txt -tmpdir=/tmp -p=8

# Output columns: filename, numReads, estFragLen, corr_estFragLen,
#                  phantomPeak, corr_phantomPeak, argmin_corr,
#                  min_corr, NSC, RSC, QualityTag
```

**Cross-correlation metrics interpretation:**

| Metric | Good | Acceptable | Poor |
|--------|------|------------|------|
| NSC (Normalized Strand Coefficient) | > 1.1 | 1.05 - 1.1 | < 1.05 |
| RSC (Relative Strand Correlation) | > 1.0 | 0.8 - 1.0 | < 0.8 |
| QualityTag | 2 | 1 | 0 or -1 |

```
Cross-correlation plot interpretation:
  - Should show a clear peak at the fragment length (~200 bp for standard ChIP)
  - A second peak at read length (phantom peak) is normal
  - RSC = (CC at fragment length - CC minimum) / (CC at read length - CC minimum)
  - NSC = CC at fragment length / CC minimum
  - Low NSC/RSC = weak enrichment relative to background
```

### FRiP (Fraction of Reads in Peaks)

```bash
# Calculate FRiP after peak calling
total_reads=$(samtools view -c -F 4 sample.final.bam)
reads_in_peaks=$(bedtools intersect -a sample.final.bam -b peaks.narrowPeak -u -f 0.20 | \
  samtools view -c)
frip=$(echo "scale=4; $reads_in_peaks / $total_reads" | bc)
echo "FRiP: $frip"
```

| Experiment Type | Good FRiP | Minimum FRiP |
|----------------|-----------|--------------|
| TF ChIP-seq | > 5% | > 1% |
| H3K4me3 | > 15% | > 5% |
| H3K27ac | > 15% | > 5% |
| H3K27me3 | > 20% | > 10% |
| H3K36me3 | > 30% | > 15% |

### IDR (Irreproducible Discovery Rate)

```bash
# IDR analysis for replicate concordance (ENCODE standard)
# Step 1: Call peaks on individual replicates with relaxed threshold
macs2 callpeak -t rep1.bam -c input.bam -f BAM -g hs \
  --nomodel --extsize 200 -p 1e-3 -n rep1 --outdir peaks/

macs2 callpeak -t rep2.bam -c input.bam -f BAM -g hs \
  --nomodel --extsize 200 -p 1e-3 -n rep2 --outdir peaks/

# Step 2: Sort peaks by -log10(p-value)
sort -k8,8nr peaks/rep1_peaks.narrowPeak > peaks/rep1_sorted.narrowPeak
sort -k8,8nr peaks/rep2_peaks.narrowPeak > peaks/rep2_sorted.narrowPeak

# Step 3: Run IDR
idr --samples peaks/rep1_sorted.narrowPeak peaks/rep2_sorted.narrowPeak \
  --input-file-type narrowPeak \
  --rank p.value \
  --output-file peaks/idr_output.txt \
  --plot \
  --log-output-file peaks/idr_log.txt

# IDR threshold: peaks with IDR < 0.05 are reproducible
awk '$5 >= 540' peaks/idr_output.txt > peaks/idr_conservative.narrowPeak
```

```
IDR interpretation:
  - IDR < 0.01: Highly reproducible (most stringent)
  - IDR < 0.05: Reproducible (ENCODE standard)
  - IDR 0.05-0.1: Borderline
  - IDR > 0.1: Irreproducible

Self-consistency IDR (pseudo-replicates of same sample):
  - Used when biological replicates unavailable
  - Split BAM 50/50, call peaks on each half, run IDR
  - If N(IDR < 0.05) from true replicates < N(self-consistency) / 2: FAIL
```

### Comprehensive QC Summary

```python
import pandas as pd

def chipseq_qc_summary(samples):
    """Generate ChIP-seq QC summary table.

    samples: list of dicts with keys:
      name, total_reads, mapped_reads, dup_rate, mapq30_reads,
      nsc, rsc, num_peaks, frip, idr_peaks
    """
    qc = pd.DataFrame(samples)

    qc['mapping_rate'] = qc['mapped_reads'] / qc['total_reads']
    qc['usable_fraction'] = qc['mapq30_reads'] / qc['total_reads']

    # Flag issues
    flags = []
    for _, row in qc.iterrows():
        issues = []
        if row['mapping_rate'] < 0.7:
            issues.append('LOW_MAPPING')
        if row['dup_rate'] > 0.5:
            issues.append('HIGH_DUPS')
        if row.get('nsc', 1.1) < 1.05:
            issues.append('LOW_NSC')
        if row.get('rsc', 1.0) < 0.8:
            issues.append('LOW_RSC')
        if row.get('frip', 0.05) < 0.01:
            issues.append('LOW_FRIP')
        flags.append('; '.join(issues) if issues else 'PASS')
    qc['flags'] = flags

    print(qc.to_string(index=False))
    return qc
```

---

## Phase 3: Peak Calling with MACS2/MACS3

### Narrow Peaks (Transcription Factors)

```bash
# TF ChIP-seq: narrow peak calling
macs2 callpeak \
  -t chip_sample.bam \
  -c input_control.bam \
  -f BAM \
  -g hs \
  --nomodel --extsize 200 \
  -q 0.01 \
  --call-summits \
  -n tf_peaks \
  --outdir peaks/

# For paired-end data, use BAMPE
macs2 callpeak \
  -t chip_sample.bam \
  -c input_control.bam \
  -f BAMPE \
  -g hs \
  -q 0.01 \
  --call-summits \
  -n tf_peaks \
  --outdir peaks/
```

### Broad Peaks (Histone Modifications)

```bash
# Broad histone marks: H3K27me3, H3K36me3, H3K9me3
macs2 callpeak \
  -t chip_h3k27me3.bam \
  -c input_control.bam \
  -f BAM \
  -g hs \
  --broad \
  --broad-cutoff 0.1 \
  --nomodel --extsize 200 \
  -n h3k27me3_peaks \
  --outdir peaks/

# H3K4me1 (enhancer mark): can use broad or narrow depending on resolution needed
macs2 callpeak \
  -t chip_h3k4me1.bam \
  -c input_control.bam \
  -f BAM \
  -g hs \
  --broad \
  --broad-cutoff 0.05 \
  --nomodel --extsize 200 \
  -n h3k4me1_peaks \
  --outdir peaks/
```

### Peak Calling Decision Tree

```
What is your target?
|
+-> Transcription Factor (CTCF, p53, MYC, etc.)
|   -> macs2 callpeak [default narrow mode]
|   -> --call-summits for sub-peak resolution
|   -> -q 0.01 (stringent) or -q 0.05 (exploratory)
|
+-> Active mark at promoters (H3K4me3, H3K9ac)
|   -> macs2 callpeak [default narrow mode]
|   -> These peaks are typically sharp and well-defined
|
+-> Active enhancer mark (H3K27ac)
|   -> macs2 callpeak [default narrow mode]
|   -> Or --broad if studying super-enhancers
|
+-> Enhancer priming (H3K4me1)
|   -> macs2 callpeak --broad --broad-cutoff 0.05
|   -> Peaks are wider than active marks
|
+-> Repressive marks (H3K27me3, H3K9me3)
|   -> macs2 callpeak --broad --broad-cutoff 0.1
|   -> Very broad domains, may be megabase-scale
|
+-> Transcription elongation (H3K36me3)
|   -> macs2 callpeak --broad --broad-cutoff 0.1
|   -> Covers gene bodies of actively transcribed genes
|
+-> RNA Pol II
|   -> Two strategies:
|      (a) Narrow mode for promoter-proximal pausing peaks
|      (b) Broad mode for gene body signal (traveling ratio)
```

### Input/IgG Control Normalization

```
Control selection priority:
1. Input DNA from same chromatin prep (BEST)
2. IgG control from same chromatin prep
3. Input from a different prep of same cell type (ACCEPTABLE)
4. No control (NOT RECOMMENDED - high false positive rate)

Control requirements:
  - Sequence to similar or greater depth than ChIP sample
  - Process identically (same fragmentation, library prep)
  - Same cell type and growth conditions

MACS2 handles control normalization internally:
  - Estimates local background from control at multiple scales
  - Uses lambda_local = max(lambda_BG, lambda_1k, lambda_5k, lambda_10k)
  - lambda_BG = total control reads / genome size
  - lambda_Xk = control reads in X kb window centered on peak
```

---

## Phase 4: De Novo Motif Discovery

### HOMER findMotifsGenome

```bash
# De novo and known motif analysis with HOMER
findMotifsGenome.pl peaks/tf_peaks_summits.bed hg38 \
  motif_results/ \
  -size 200 \
  -mask \
  -p 16 \
  -preparsedDir /ref/homer_preparsed/

# Key output files:
# motif_results/homerResults.html     - De novo motifs
# motif_results/knownResults.html     - Known motif enrichment
# motif_results/homerResults/         - Individual motif logos
# motif_results/knownResults.txt      - Tab-separated known motif table
```

**HOMER parameters for different scenarios:**

| Scenario | `-size` | Additional Flags |
|----------|---------|------------------|
| TF binding motifs | `200` (or `-size given` for actual peak size) | `-mask` |
| Histone mark motifs | `500` or `1000` | `-mask` |
| Motifs in promoters only | `200` | `-mask -bg promoter_background.bed` |
| Comparing two peak sets | `200` | `-bg other_peaks.bed` |
| Finding co-binding motifs | `200` | `-nomotif` (skip de novo, faster) |

### MEME-ChIP

```bash
# Extract peak sequences
bedtools getfasta -fi /ref/hg38.fa -bed peaks/tf_peaks_summits.bed \
  -fo peaks/peak_sequences.fa

# MEME-ChIP analysis (de novo + known motif enrichment)
meme-chip \
  -oc meme_results/ \
  -db /ref/motif_databases/JASPAR2024_CORE_vertebrates.meme \
  -db /ref/motif_databases/HOCOMOCOv11_core_HUMAN_mono.meme \
  -meme-maxw 20 \
  -meme-nmotifs 10 \
  -meme-minw 6 \
  peaks/peak_sequences.fa

# Key output files:
# meme_results/meme-chip.html       - Combined results
# meme_results/meme_out/meme.html   - De novo MEME results
# meme_results/dreme_out/dreme.html - De novo DREME results (short motifs)
# meme_results/centrimo_out/        - Central motif enrichment
# meme_results/tomtom_out/          - Match de novo to known motifs
```

### Known Motif Enrichment Testing

```python
import pandas as pd
import numpy as np
from scipy.stats import fisher_exact
from statsmodels.stats.multitest import multipletests

def known_motif_enrichment(peak_sequences, background_sequences, motif_pwms, threshold=0.8):
    """Test enrichment of known motifs in peaks vs background.

    motif_pwms: dict of motif_name -> position weight matrix (numpy array)
    threshold: fraction of max PWM score to call a match
    """
    results = []
    for motif_name, pwm in motif_pwms.items():
        max_score = pwm.max(axis=1).sum()
        score_threshold = max_score * threshold

        peak_hits = sum(1 for seq in peak_sequences
                       if scan_pwm(seq, pwm, score_threshold))
        bg_hits = sum(1 for seq in background_sequences
                     if scan_pwm(seq, pwm, score_threshold))

        peak_total = len(peak_sequences)
        bg_total = len(background_sequences)

        table = [[peak_hits, peak_total - peak_hits],
                 [bg_hits, bg_total - bg_hits]]
        odds, pval = fisher_exact(table, alternative='greater')

        results.append({
            'motif': motif_name,
            'peak_fraction': peak_hits / peak_total,
            'bg_fraction': bg_hits / bg_total,
            'odds_ratio': odds,
            'pvalue': pval
        })

    results_df = pd.DataFrame(results)
    _, results_df['padj'], _, _ = multipletests(results_df['pvalue'], method='fdr_bh')
    return results_df.sort_values('padj')

def scan_pwm(sequence, pwm, threshold):
    """Scan a sequence for PWM matches above threshold."""
    base_to_idx = {'A': 0, 'C': 1, 'G': 2, 'T': 3}
    seq = sequence.upper()
    motif_len = pwm.shape[0]
    for i in range(len(seq) - motif_len + 1):
        score = sum(pwm[j, base_to_idx.get(seq[i+j], 0)]
                   for j in range(motif_len))
        if score >= threshold:
            return True
    return False
```

---

## Phase 5: Differential Binding Analysis (DiffBind)

### DiffBind Workflow

```r
# R code for DiffBind differential binding analysis
library(DiffBind)

# Sample sheet
samples <- data.frame(
  SampleID = c("ctrl_1", "ctrl_2", "ctrl_3", "treat_1", "treat_2", "treat_3"),
  Condition = c("control", "control", "control", "treated", "treated", "treated"),
  Replicate = c(1, 2, 3, 1, 2, 3),
  bamReads = c("ctrl_1.bam", "ctrl_2.bam", "ctrl_3.bam",
               "treat_1.bam", "treat_2.bam", "treat_3.bam"),
  ControlID = rep("input", 6),
  bamControl = rep("input.bam", 6),
  Peaks = c("ctrl_1_peaks.narrowPeak", "ctrl_2_peaks.narrowPeak",
            "ctrl_3_peaks.narrowPeak", "treat_1_peaks.narrowPeak",
            "treat_2_peaks.narrowPeak", "treat_3_peaks.narrowPeak"),
  PeakCaller = rep("narrow", 6)
)

# DiffBind analysis
dba_obj <- dba(sampleSheet = samples)

# Show correlation heatmap of peak overlap
plot(dba_obj)

# Count reads in consensus peaks
dba_obj <- dba.count(dba_obj, minOverlap = 2)

# Correlation heatmap of read counts (more informative than overlap)
plot(dba_obj)

# Normalize using library size and background subtraction
dba_obj <- dba.normalize(dba_obj,
  normalize = DBA_NORM_RLE,    # DESeq2's median-of-ratios
  library = DBA_LIBSIZE_FULL,  # or DBA_LIBSIZE_PEAKREADS
  background = TRUE            # Subtract non-peak background
)

# Set up contrast
dba_obj <- dba.contrast(dba_obj, categories = DBA_CONDITION,
                         minMembers = 2)

# Analyze with DESeq2 and edgeR
dba_obj <- dba.analyze(dba_obj, method = DBA_ALL_METHODS)

# Compare methods
dba.plotVenn(dba_obj, contrast = 1, method = DBA_ALL_METHODS)

# Report (DESeq2 results)
db_peaks <- dba.report(dba_obj, method = DBA_DESEQ2, th = 0.05, fold = 1)
db_df <- as.data.frame(db_peaks)
write.csv(db_df, "differential_binding_results.csv", row.names = FALSE)

cat("Differentially bound peaks:", nrow(db_df), "\n")
cat("Gained binding:", sum(db_df$Fold > 0), "\n")
cat("Lost binding:", sum(db_df$Fold < 0), "\n")

# MA plot
dba.plotMA(dba_obj, method = DBA_DESEQ2)

# Volcano plot
dba.plotVolcano(dba_obj, method = DBA_DESEQ2)

# PCA plot
dba.plotPCA(dba_obj, DBA_CONDITION, label = DBA_ID)
```

### DiffBind Normalization Options

| Method | When to Use |
|--------|-------------|
| `DBA_NORM_RLE` (DESeq2 default) | Standard for most ChIP-seq experiments |
| `DBA_NORM_TMM` (edgeR default) | Alternative normalization, compare with RLE |
| `DBA_NORM_LIB` | Simple library size; when global binding is expected to differ |
| `background = TRUE` | Recommended; corrects for non-specific enrichment |
| `DBA_LIBSIZE_PEAKREADS` | Use reads in peaks only for normalization |
| `DBA_LIBSIZE_FULL` | Use all mapped reads for normalization |

---

## Phase 6: Super-Enhancer Identification (ROSE)

### ROSE Algorithm

```bash
# ROSE: Ranking Of Super-Enhancers
# Requires: H3K27ac (or H3K4me1 or MED1) ChIP-seq peaks

# Step 1: Stitch enhancers within 12.5 kb (excluding TSS +/- 2.5 kb)
python ROSE_main.py \
  -g hg38 \
  -i h3k27ac_peaks.gff \
  -r h3k27ac.bam \
  -c input.bam \
  -o rose_output/ \
  -s 12500 \
  -t 2500

# Output:
# rose_output/*_AllEnhancers.table.txt       - All stitched enhancers with signal
# rose_output/*_SuperEnhancers.table.txt     - Super-enhancers only
# rose_output/*_Enhancers_withSuper.bed       - BED file with SE annotation
# rose_output/*_Plot_points.png               - Hockey stick plot
```

### Super-Enhancer Analysis in Python

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def identify_super_enhancers(enhancer_signals, output_png="se_hockey_stick.png"):
    """Identify super-enhancers using the ROSE hockey-stick algorithm.

    enhancer_signals: DataFrame with columns ['enhancer_id', 'signal']
    Signal is typically H3K27ac ChIP signal over input, stitched across
    constituent enhancers within 12.5 kb.
    """
    # Sort by signal
    sorted_df = enhancer_signals.sort_values('signal').reset_index(drop=True)
    sorted_df['rank'] = range(len(sorted_df))

    # Normalize rank and signal to [0, 1]
    sorted_df['rank_norm'] = sorted_df['rank'] / sorted_df['rank'].max()
    sorted_df['signal_norm'] = sorted_df['signal'] / sorted_df['signal'].max()

    # Find inflection point (tangent line with slope = 1)
    # This is where the derivative of the curve exceeds 1
    dx = np.diff(sorted_df['rank_norm'].values)
    dy = np.diff(sorted_df['signal_norm'].values)
    slopes = dy / dx

    # Find first point where slope >= 1
    inflection_idx = np.argmax(slopes >= 1)
    if inflection_idx == 0 and slopes[0] < 1:
        inflection_idx = len(slopes) - 1  # No clear inflection

    threshold = sorted_df.iloc[inflection_idx]['signal']
    sorted_df['is_super_enhancer'] = sorted_df['signal'] >= threshold

    n_se = sorted_df['is_super_enhancer'].sum()
    n_typical = (~sorted_df['is_super_enhancer']).sum()
    print(f"Super-enhancers: {n_se}")
    print(f"Typical enhancers: {n_typical}")
    print(f"Signal threshold: {threshold:.1f}")

    # Hockey stick plot
    fig, ax = plt.subplots(figsize=(8, 6))
    typical = sorted_df[~sorted_df['is_super_enhancer']]
    se = sorted_df[sorted_df['is_super_enhancer']]
    ax.scatter(typical['rank'], typical['signal'], c='grey', s=2, alpha=0.5, label='Typical')
    ax.scatter(se['rank'], se['signal'], c='red', s=5, alpha=0.7, label='Super-enhancer')
    ax.axhline(threshold, color='black', linestyle='--', alpha=0.5)
    ax.set_xlabel('Enhancer Rank')
    ax.set_ylabel('H3K27ac Signal')
    ax.set_title(f'Super-Enhancer Identification (n={n_se})')
    ax.legend()
    plt.tight_layout()
    plt.savefig(output_png, dpi=150)

    return sorted_df

def annotate_super_enhancers(se_df, gene_annotation, max_distance=50000):
    """Assign super-enhancers to nearest genes within distance threshold."""
    assignments = []
    for _, se in se_df[se_df['is_super_enhancer']].iterrows():
        same_chr = gene_annotation[gene_annotation['chr'] == se.get('chr', '')]
        if len(same_chr) == 0:
            continue
        se_center = (se.get('start', 0) + se.get('end', 0)) / 2
        distances = (same_chr['tss'] - se_center).abs()
        nearest_idx = distances.idxmin()
        dist = distances.min()
        if dist <= max_distance:
            assignments.append({
                'enhancer_id': se['enhancer_id'],
                'gene': same_chr.loc[nearest_idx, 'gene'],
                'distance_to_tss': dist,
                'signal': se['signal']
            })
    return pd.DataFrame(assignments)
```

---

## Phase 7: Peak Annotation with ChIPseeker

```r
# R code for ChIPseeker peak annotation
library(ChIPseeker)
library(TxDb.Hsapiens.UCSC.hg38.knownGene)
library(org.Hs.eg.db)
library(clusterProfiler)

txdb <- TxDb.Hsapiens.UCSC.hg38.knownGene

# Read and annotate peaks
peaks <- readPeakFile("peaks/tf_peaks.narrowPeak")
peakAnno <- annotatePeak(peaks, TxDb = txdb,
                          tssRegion = c(-3000, 3000),
                          annoDb = "org.Hs.eg.db",
                          level = "gene")

# Visualization
plotAnnoPie(peakAnno)
plotAnnoBar(peakAnno)
plotDistToTSS(peakAnno)

# Compare peak annotations across samples/conditions
peak_list <- list(
  control = readPeakFile("peaks/ctrl_peaks.narrowPeak"),
  treated = readPeakFile("peaks/treat_peaks.narrowPeak")
)
peakAnnoList <- lapply(peak_list, annotatePeak, TxDb = txdb,
                        tssRegion = c(-3000, 3000))
plotAnnoBar(peakAnnoList)

# Gene enrichment on peak-associated genes
genes <- as.data.frame(peakAnno)$geneId
ego <- enrichGO(gene = genes, OrgDb = org.Hs.eg.db,
                 ont = "BP", pAdjustMethod = "BH", pvalueCutoff = 0.05)
dotplot(ego, showCategory = 20)
```

---

## Phase 8: Signal Visualization with deepTools

### Generate Normalized Signal Tracks

```bash
# Create normalized bigWig from ChIP BAM
bamCoverage -b chip.bam -o chip.bw \
  --normalizeUsing RPGC \
  --effectiveGenomeSize 2913022398 \
  --binSize 10 \
  --extendReads 200 \
  -p 16

# Create input-subtracted signal track
bamCompare -b1 chip.bam -b2 input.bam \
  -o chip_vs_input.bw \
  --scaleFactorsMethod readCount \
  --operation log2ratio \
  --binSize 50 \
  --extendReads 200 \
  -p 16
```

### Heatmaps and Profile Plots

```bash
# Compute matrix: signal at peak centers
computeMatrix reference-point \
  -S chip_vs_input.bw \
  -R peaks/tf_peaks_summits.bed \
  --beforeRegionStartLength 5000 \
  --afterRegionStartLength 5000 \
  --binSize 25 \
  --missingDataAsZero \
  -o peak_matrix.gz \
  -p 16

# Heatmap sorted by signal
plotHeatmap -m peak_matrix.gz \
  -out peak_heatmap.png \
  --colorMap YlOrRd \
  --sortUsing mean \
  --whatToShow 'heatmap and colorbar' \
  --heatmapHeight 15

# Profile plot comparing multiple samples
computeMatrix reference-point \
  -S ctrl_chip.bw treat_chip.bw \
  -R peaks/consensus_peaks.bed \
  --beforeRegionStartLength 5000 \
  --afterRegionStartLength 5000 \
  --binSize 25 \
  -o comparison_matrix.gz \
  -p 16

plotProfile -m comparison_matrix.gz \
  -out comparison_profile.png \
  --perGroup \
  --plotTitle "ChIP Signal at Peaks"

# Scale regions: signal across gene bodies
computeMatrix scale-regions \
  -S h3k36me3.bw \
  -R /ref/hg38_genes.bed \
  --beforeRegionStartLength 3000 \
  --afterRegionStartLength 3000 \
  --regionBodyLength 5000 \
  --binSize 25 \
  -o gene_body_matrix.gz \
  -p 16

plotHeatmap -m gene_body_matrix.gz \
  -out gene_body_heatmap.png \
  --colorMap Blues
```

### Multi-Sample Correlation

```bash
# Genome-wide sample correlation
multiBamSummary bins \
  --bamfiles ctrl_1.bam ctrl_2.bam treat_1.bam treat_2.bam input.bam \
  --labels ctrl_1 ctrl_2 treat_1 treat_2 input \
  --binSize 10000 \
  -o sample_correlation.npz \
  -p 16

# Correlation heatmap
plotCorrelation -in sample_correlation.npz \
  --corMethod spearman \
  --whatToPlot heatmap \
  --skipZeros \
  -o correlation_heatmap.png

# PCA
plotPCA -in sample_correlation.npz \
  -o sample_pca.png
```

---

## Phase 9: CUT&RUN and CUT&Tag Analysis

### Key Differences from Standard ChIP-seq

| Feature | ChIP-seq | CUT&RUN | CUT&Tag |
|---------|----------|---------|---------|
| Cell input | 10^6 - 10^7 | 10^4 - 10^5 | 10^4 - 10^5 |
| Background | High (sonication) | Low (targeted cleavage) | Very low |
| Fragment size | 200-600 bp | ~150 bp (TF), variable (histone) | ~150 bp |
| Sequencing depth | 20-40M reads | 3-8M reads | 3-8M reads |
| Peak caller | MACS2/3 | SEACR (preferred) | SEACR (preferred) |
| Control | Input DNA | IgG CUT&RUN | IgG CUT&Tag |
| Spike-in | Not standard | E. coli carry-over | E. coli carry-over |

### SEACR Peak Calling

```bash
# Convert BAM to BedGraph for SEACR
bedtools genomecov -ibam cutnrun_sample.bam -bg > sample.bedgraph
bedtools genomecov -ibam cutnrun_igg.bam -bg > igg.bedgraph

# SEACR with IgG control (stringent mode)
bash SEACR.sh sample.bedgraph igg.bedgraph non stringent \
  seacr_peaks_stringent

# SEACR without control (top 1% of signal, relaxed)
bash SEACR.sh sample.bedgraph 0.01 non stringent \
  seacr_peaks_top1pct

# SEACR output format:
# chr  start  end  total_signal  max_signal  max_signal_region
```

**SEACR mode selection:**

| Mode | When to Use |
|------|-------------|
| `stringent` | TF binding, focal marks (H3K4me3, H3K27ac). Peaks must pass both global and local thresholds. |
| `relaxed` | Broad marks (H3K27me3). Peaks need to pass only global threshold. |
| With control (IgG) | Preferred when IgG CUT&RUN/CUT&Tag is available |
| Without control (FDR) | Use numeric threshold (0.01 = top 1%) when no IgG available |

### Spike-In Normalization for CUT&RUN/CUT&Tag

```bash
# E. coli DNA is carried over during CUT&RUN/CUT&Tag as natural spike-in
# Map reads to E. coli genome to get spike-in counts

# Align to combined human + E. coli reference
bowtie2 --very-sensitive --no-mixed --no-discordant -p 16 \
  -x /ref/hg38_ecoli_combined \
  -1 sample_R1.fastq.gz -2 sample_R2.fastq.gz \
  | samtools sort -@ 8 -o sample_combined.bam

# Count E. coli reads (spike-in)
ecoli_reads=$(samtools view -c -F 4 sample_combined.bam ecoli_chr)

# Calculate scale factor
# scale_factor = min(ecoli_reads across samples) / ecoli_reads_this_sample
# Apply to human-aligned BAM for normalization

# Create normalized bigWig
bamCoverage -b sample_human.bam -o sample_normalized.bw \
  --scaleFactor $scale_factor \
  --binSize 10 \
  --extendReads \
  -p 16
```

```python
def calculate_spike_in_factors(ecoli_counts):
    """Calculate spike-in normalization scale factors.

    ecoli_counts: dict of sample_name -> number of E. coli aligned reads

    Principle: Samples with more E. coli reads had more efficient
    cutting/tagmentation, so their human signal should be scaled DOWN.
    """
    min_ecoli = min(ecoli_counts.values())
    scale_factors = {sample: min_ecoli / count
                    for sample, count in ecoli_counts.items()}

    print("Spike-in scale factors:")
    for sample, factor in scale_factors.items():
        print(f"  {sample}: {factor:.4f} ({ecoli_counts[sample]:,} E. coli reads)")

    return scale_factors
```

---

## Phase 10: Chromatin State Analysis

### Combinatorial Histone Mark Interpretation

```python
def assign_chromatin_states(mark_signals):
    """Assign chromatin states from combinatorial histone marks.

    mark_signals: DataFrame, rows=regions, columns=histone marks, values=signal/input

    Chromatin state definitions:
      Active Promoter:   H3K4me3(+) H3K27ac(+) H3K27me3(-)
      Bivalent Promoter: H3K4me3(+) H3K27me3(+) H3K27ac(-)
      Active Enhancer:   H3K4me1(+) H3K27ac(+) H3K4me3(-)
      Poised Enhancer:   H3K4me1(+) H3K27ac(-) H3K4me3(-)
      Polycomb Repressed: H3K27me3(+) H3K4me3(-) H3K9me3(-)
      Heterochromatin:   H3K9me3(+)
      Transcribed:       H3K36me3(+)
      Quiescent:         All marks low
    """
    states = []
    medians = {col: mark_signals[col].median() for col in mark_signals.columns
                if col in ['H3K4me3','H3K4me1','H3K27ac','H3K27me3','H3K36me3','H3K9me3']}

    for idx, row in mark_signals.iterrows():
        k4me3 = row.get('H3K4me3', 0) > medians.get('H3K4me3', 0)
        k4me1 = row.get('H3K4me1', 0) > medians.get('H3K4me1', 0)
        k27ac = row.get('H3K27ac', 0) > medians.get('H3K27ac', 0)
        k27me3 = row.get('H3K27me3', 0) > medians.get('H3K27me3', 0)
        k36me3 = row.get('H3K36me3', 0) > medians.get('H3K36me3', 0)
        k9me3 = row.get('H3K9me3', 0) > medians.get('H3K9me3', 0)

        if k4me3 and k27ac and not k27me3:
            state = 'Active_Promoter'
        elif k4me3 and k27me3:
            state = 'Bivalent_Promoter'
        elif k4me1 and k27ac and not k4me3:
            state = 'Active_Enhancer'
        elif k4me1 and not k27ac and not k4me3:
            state = 'Poised_Enhancer'
        elif k27me3 and not k4me3 and not k9me3:
            state = 'Polycomb_Repressed'
        elif k9me3:
            state = 'Heterochromatin'
        elif k36me3:
            state = 'Transcribed'
        else:
            state = 'Quiescent'

        states.append({'region': idx, 'chromatin_state': state})

    state_df = pd.DataFrame(states).set_index('region')
    print("Chromatin state distribution:")
    print(state_df['chromatin_state'].value_counts())
    return state_df
```

---

## Evidence Grading Framework

| Tier | Criteria | Confidence |
|------|----------|------------|
| **T1** | Peak replicated (IDR < 0.05), DiffBind padj < 0.01, motif match at summit, expression correlation confirmed | High |
| **T2** | Peak in >= 2 replicates, DiffBind padj < 0.05, fold > 2, motif enrichment in peak set | Medium-High |
| **T3** | Peak called in single replicate, marginal enrichment, or FRiP-challenged sample | Medium |
| **T4** | Broad domain boundary, no replicate support, low NSC/RSC sample | Low |

---

## Boundary Rules

```
DO:
- Call peaks with MACS2/3 (narrow and broad modes)
- Calculate QC metrics (FRiP, NSC, RSC, IDR)
- Run differential binding analysis (DiffBind)
- Identify super-enhancers (ROSE algorithm)
- Run de novo motif discovery (HOMER, MEME-ChIP)
- Annotate peaks (ChIPseeker)
- Visualize signal (deepTools heatmaps, profiles)
- Analyze CUT&RUN/CUT&Tag with SEACR and spike-in normalization
- Assign chromatin states from combinatorial marks

DO NOT:
- Perform read alignment from raw FASTQ (upstream step)
- Run ATAC-seq specific analysis (use atac-seq-analysis skill)
- Deep pathway enrichment on peak gene lists (use gene-enrichment skill)
- Build gene regulatory networks (use gene-regulatory-networks skill)
- Single-cell ChIP/CUT&Tag analysis (use single-cell-analysis skill)
```

## Completeness Checklist

- [ ] Reads aligned and filtered (duplicates, MAPQ, blacklist)
- [ ] QC metrics computed: FRiP, NSC/RSC, library complexity
- [ ] Peaks called with appropriate mode (narrow vs broad)
- [ ] IDR analysis for replicate concordance
- [ ] Input/IgG control properly used for background subtraction
- [ ] Differential binding analysis completed (DiffBind)
- [ ] Motif discovery performed (HOMER or MEME-ChIP)
- [ ] Peaks annotated to genomic features (ChIPseeker)
- [ ] Signal visualized (deepTools heatmaps/profiles)
- [ ] Super-enhancer identification (if H3K27ac data)
- [ ] CUT&RUN/CUT&Tag: spike-in normalization applied, SEACR used
- [ ] Evidence tier assigned to major findings
