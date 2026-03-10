---
name: atac-seq-analysis
description: ATAC-seq chromatin accessibility analysis. Tn5 transposase insertion site correction, nucleosome-free region extraction, fragment size distribution QC, TSS enrichment scoring, peak calling with MACS3, differential accessibility with DiffBind and DESeq2, transcription factor footprinting with TOBIAS and HINT-ATAC, motif deviation analysis with chromVAR, single-cell ATAC-seq with ArchR and Signac, peak annotation with ChIPseeker and HOMER. Use when user asks about ATAC-seq, chromatin accessibility, open chromatin, Tn5, nucleosome-free regions, NFR, TSS enrichment, fragment size distribution, differential accessibility, footprinting, TOBIAS, chromVAR, scATAC-seq, ArchR, Signac, MACS3 ATAC parameters, or chromatin openness.
---

# ATAC-seq Chromatin Accessibility Analysis

Comprehensive pipeline for analyzing Assay for Transposase-Accessible Chromatin with sequencing (ATAC-seq) data. Covers bulk and single-cell modalities, from raw read processing through differential accessibility, transcription factor footprinting, and motif deviation scoring.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_atacseq_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as analysis completes
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- DNA methylation analysis (bisulfite-seq, 450K/EPIC arrays) -> use `epigenomics`
- ChIP-seq histone mark or TF binding analysis -> use `chipseq-analysis`
- Deep pathway enrichment on DA peak gene lists -> use `gene-enrichment`
- Single-cell RNA-seq clustering -> use `single-cell-analysis`
- Multi-omics integration (ATAC + RNA jointly) -> use `multi-omics-integration`

## Cross-Reference: Other Skills

- **ChIP-seq peak calling and histone code** -> use chipseq-analysis skill
- **Pathway enrichment on genes near DA peaks** -> use gene-enrichment skill
- **Joint scATAC + scRNA integration** -> use multi-omics-integration skill
- **Methylation at accessible regions** -> use epigenomics skill

---

## ATAC-seq Biology & Experimental Design

### How ATAC-seq Works

```
Tn5 transposase inserts sequencing adapters into accessible chromatin:
  - Tn5 binds as a dimer, creating a 9 bp duplication at the insertion site
  - The actual cutting sites are offset: +4 bp on the forward strand, -5 bp on the reverse strand
  - Correction for this offset is MANDATORY for footprinting and motif analysis
  - Fragments between two Tn5 insertions are sequenced as paired-end reads

Fragment size encodes nucleosome positioning:
  < 150 bp  -> nucleosome-free region (NFR)
  ~200 bp   -> mono-nucleosome
  ~400 bp   -> di-nucleosome
  ~600 bp   -> tri-nucleosome
```

### Experimental Design Considerations

| Factor | Recommendation |
|--------|----------------|
| Cell number | 50,000 standard; 500-5,000 for miniATAC/Omni-ATAC |
| Replicates | Minimum 2 biological replicates; 3+ for differential analysis |
| Sequencing depth | 50-75M read pairs per replicate (bulk) |
| Read length | PE 50 or PE 75 sufficient; PE 150 adds no benefit for most analyses |
| Protocol variant | Omni-ATAC preferred (reduced mitochondrial reads) |

---

## Phase 1: Read Processing & Alignment

### Adapter Trimming and Alignment

```bash
# Adapter trimming (Nextera adapters used in ATAC-seq)
trim_galore --paired --nextera -q 20 --length 20 \
  -o trimmed/ sample_R1.fastq.gz sample_R2.fastq.gz

# Alignment with Bowtie2 (sensitive settings for short fragments)
bowtie2 --very-sensitive -X 2000 --no-mixed --no-discordant \
  --threads 16 -x /ref/bowtie2/hg38 \
  -1 trimmed/sample_R1_val_1.fq.gz \
  -2 trimmed/sample_R2_val_2.fq.gz \
  | samtools sort -@ 8 -o sample.sorted.bam

samtools index sample.sorted.bam
```

**Key Bowtie2 parameters for ATAC-seq:**
- `-X 2000`: Maximum fragment length. Must be large enough to capture nucleosomal fragments.
- `--very-sensitive`: Enables more thorough alignment (equivalent to `-D 20 -R 3 -N 0 -L 20 -i S,1,0.50`).
- `--no-mixed --no-discordant`: Only report concordant paired alignments.

### Post-Alignment Filtering

```bash
# Remove mitochondrial reads (typically 30-80% in standard ATAC, <5% in Omni-ATAC)
samtools idxstats sample.sorted.bam | cut -f1 | grep -v chrM > chroms_to_keep.txt
samtools view -b -@ 8 sample.sorted.bam $(cat chroms_to_keep.txt | tr '\n' ' ') \
  > sample.noMT.bam

# Remove duplicates (mark but DO NOT remove for peak calling with --keep-dup all)
picard MarkDuplicates \
  INPUT=sample.noMT.bam \
  OUTPUT=sample.dedup.bam \
  METRICS_FILE=sample.dup_metrics.txt \
  REMOVE_DUPLICATES=true

# Filter: MAPQ >= 30, proper pairs, no secondary/supplementary alignments
samtools view -b -f 2 -F 1804 -q 30 sample.dedup.bam > sample.filtered.bam
samtools index sample.filtered.bam
```

**Filtering flags explained:**
- `-f 2`: Keep proper pairs only
- `-F 1804`: Remove unmapped (4), mate unmapped (8), not primary (256), fails QC (512), duplicate (1024)
- `-q 30`: MAPQ >= 30 (unique alignments)

### Blacklist Region Removal

```bash
# Remove ENCODE blacklist regions (essential for ATAC-seq)
bedtools intersect -v -abam sample.filtered.bam \
  -b /ref/hg38-blacklist.v2.bed > sample.final.bam
samtools index sample.final.bam
```

Always use the most recent blacklist version (v2 for hg38). Blacklist regions contain anomalous signal in all experiments and inflate peak counts.

---

## Phase 2: Tn5 Insertion Site Correction

### The +4/-5 Offset

```
Tn5 cuts as a dimer, generating a 9 bp target site duplication.
The actual insertion point is offset from the read start:

Forward strand read (+):  shift read start by +4 bp
Reverse strand read (-):  shift read end by -5 bp

This correction is CRITICAL for:
  - Footprinting analysis (base-pair resolution)
  - Motif enrichment at insertion sites
  - Single-base-pair accessibility profiles

NOT needed for:
  - Peak calling (peaks are wide enough that 4-5 bp shift is negligible)
  - Fragment size distribution QC
  - TSS enrichment at coarse resolution
```

```python
import pysam
import os

def correct_tn5_offset(input_bam, output_bam):
    """Apply Tn5 insertion site correction (+4/-5 bp offset).

    Shifts read coordinates to reflect actual Tn5 cutting sites.
    Required for footprinting and base-pair resolution analysis.
    """
    infile = pysam.AlignmentFile(input_bam, "rb")
    outfile = pysam.AlignmentFile(output_bam, "wb", header=infile.header)

    shifted = 0
    for read in infile:
        if read.is_unmapped or read.is_secondary or read.is_supplementary:
            continue
        if read.is_reverse:
            read.reference_start = max(0, read.reference_start - 5)
        else:
            read.reference_start = read.reference_start + 4
        outfile.write(read)
        shifted += 1

    infile.close()
    outfile.close()
    pysam.sort("-o", output_bam, output_bam)
    pysam.index(output_bam)
    print(f"Tn5-corrected {shifted} reads -> {output_bam}")

correct_tn5_offset("sample.final.bam", "sample.tn5_corrected.bam")
```

### Generating Tn5 Insertion BED Files

```bash
# Convert BAM to Tn5 insertion sites (single-bp BED)
# Forward strand: start + 4
# Reverse strand: end - 5
alignmentSieve --bam sample.final.bam --ATACshift \
  --outFile sample.shifted.bam --numberOfProcessors 8

# Convert to BED of insertion points
bedtools bamtobed -i sample.shifted.bam | \
  awk 'BEGIN{OFS="\t"} {if($6=="+"){print $1,$2,$2+1,$4,$5,$6} else {print $1,$3-1,$3,$4,$5,$6}}' \
  > sample.insertions.bed
```

---

## Phase 3: Quality Control

### Fragment Size Distribution

```python
import pysam
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

def fragment_size_distribution(bam_file, max_size=1000, output_png="fragment_sizes.png"):
    """Plot fragment size distribution from paired-end ATAC-seq BAM.

    Expected pattern:
      - Strong peak < 150 bp (NFR)
      - Smaller peak ~200 bp (mono-nucleosome)
      - Diminishing peaks at ~400, ~600 bp (di/tri-nucleosome)
      - Periodicity of ~147-200 bp between peaks
    """
    sizes = []
    bamfile = pysam.AlignmentFile(bam_file, "rb")
    for read in bamfile:
        if (read.is_proper_pair and not read.is_reverse
                and not read.is_duplicate and read.mapping_quality >= 30):
            frag_size = abs(read.template_length)
            if 0 < frag_size <= max_size:
                sizes.append(frag_size)
    bamfile.close()

    size_counts = Counter(sizes)
    x = np.arange(1, max_size + 1)
    y = np.array([size_counts.get(i, 0) for i in x])

    fig, axes = plt.subplots(1, 2, figsize=(16, 5))

    # Full distribution
    axes[0].fill_between(x, y, alpha=0.6, color='steelblue')
    axes[0].axvline(150, color='red', linestyle='--', alpha=0.7, label='NFR boundary (150 bp)')
    axes[0].axvline(200, color='orange', linestyle='--', alpha=0.7, label='Mono-nuc (~200 bp)')
    axes[0].set_xlabel('Fragment Size (bp)')
    axes[0].set_ylabel('Count')
    axes[0].set_title('Fragment Size Distribution')
    axes[0].legend()

    # NFR fraction
    nfr_count = sum(c for s, c in size_counts.items() if s < 150)
    mono_count = sum(c for s, c in size_counts.items() if 150 <= s < 300)
    di_count = sum(c for s, c in size_counts.items() if 300 <= s < 500)
    total = len(sizes)
    fracs = [nfr_count/total, mono_count/total, di_count/total, 1 - (nfr_count+mono_count+di_count)/total]
    axes[1].bar(['NFR\n(<150)', 'Mono-nuc\n(150-300)', 'Di-nuc\n(300-500)', 'Other'],
                fracs, color=['#2ecc71', '#e74c3c', '#f39c12', '#95a5a6'])
    axes[1].set_ylabel('Fraction of Fragments')
    axes[1].set_title('Fragment Class Distribution')

    for i, f in enumerate(fracs):
        axes[1].text(i, f + 0.01, f'{f:.1%}', ha='center', fontsize=10)

    plt.tight_layout()
    plt.savefig(output_png, dpi=150)
    print(f"Total fragments: {total:,}")
    print(f"NFR fraction: {nfr_count/total:.1%}")
    print(f"NFR/mono-nuc ratio: {nfr_count/max(mono_count,1):.2f}")
    return size_counts

# QC interpretation:
# - NFR fraction > 30% is typical for good ATAC-seq
# - NFR/mono-nuc ratio > 2-3 indicates good library
# - No periodicity = potential over-transposition or cell lysis
# - Dominant mono-nuc peak = under-transposition
```

### QC Metrics Decision Table

| Metric | Good | Acceptable | Poor | Action if Poor |
|--------|------|------------|------|----------------|
| Mitochondrial read % | < 5% (Omni-ATAC) | 5-40% | > 40% | Check cell lysis; use Omni-ATAC |
| Duplicate rate | < 20% | 20-40% | > 40% | Sequence deeper or improve library |
| NFR fraction | > 40% | 25-40% | < 25% | Over-digestion or nuclei quality issue |
| NFR/mono-nuc ratio | > 3 | 1.5-3 | < 1.5 | Adjust Tn5:DNA ratio |
| MAPQ >= 30 fraction | > 80% | 60-80% | < 60% | Check for contamination |
| FRiP (after peak calling) | > 30% | 15-30% | < 15% | Low signal-to-noise |
| TSS enrichment score | > 7 | 4-7 | < 4 | Poor library; may need to exclude |

### TSS Enrichment Score

```python
import pysam
import numpy as np
import matplotlib.pyplot as plt

def tss_enrichment_score(bam_file, tss_bed, flank=2000, output_png="tss_enrichment.png"):
    """Calculate TSS enrichment score from ATAC-seq data.

    TSS enrichment = (signal at TSS) / (mean signal at flanking regions)
    ENCODE standard: flanking = 100 bp windows at edges of +/- 2kb window

    Score interpretation:
      > 7: ideal
      4-7: acceptable
      < 4: poor quality, consider excluding
    """
    bamfile = pysam.AlignmentFile(bam_file, "rb")
    profile = np.zeros(2 * flank + 1)
    n_tss = 0

    with open(tss_bed) as f:
        for line in f:
            fields = line.strip().split('\t')
            chrom = fields[0]
            tss = int(fields[1])
            strand = fields[5] if len(fields) > 5 else '+'

            start = tss - flank
            end = tss + flank
            if start < 0:
                continue

            try:
                for read in bamfile.fetch(chrom, max(0, start), end):
                    if read.is_unmapped or read.mapping_quality < 30:
                        continue
                    # Use insertion site
                    if read.is_reverse:
                        ins = read.reference_end - 5
                    else:
                        ins = read.reference_start + 4
                    idx = ins - start
                    if 0 <= idx < len(profile):
                        if strand == '-':
                            idx = len(profile) - 1 - idx
                        profile[idx] += 1
                n_tss += 1
            except ValueError:
                continue

    bamfile.close()
    profile = profile / max(n_tss, 1)

    # Normalize by flanking signal (outer 100 bp on each side)
    flank_signal = np.mean(np.concatenate([profile[:100], profile[-100:]]))
    if flank_signal > 0:
        profile_norm = profile / flank_signal
    else:
        profile_norm = profile

    tss_score = profile_norm[flank]  # Value at center (TSS)

    fig, ax = plt.subplots(figsize=(10, 5))
    positions = np.arange(-flank, flank + 1)
    ax.plot(positions, profile_norm, color='steelblue', linewidth=0.5)
    ax.axvline(0, color='red', linestyle='--', alpha=0.5, label='TSS')
    ax.set_xlabel('Distance from TSS (bp)')
    ax.set_ylabel('Normalized Signal')
    ax.set_title(f'TSS Enrichment Score: {tss_score:.1f}')
    ax.legend()
    plt.tight_layout()
    plt.savefig(output_png, dpi=150)
    print(f"TSS enrichment score: {tss_score:.1f}")
    print(f"TSSs evaluated: {n_tss:,}")
    return tss_score, profile_norm
```

---

## Phase 4: Peak Calling with MACS3

### ATAC-seq-Specific MACS3 Parameters

```bash
# Standard ATAC-seq peak calling
macs3 callpeak \
  -t sample.final.bam \
  -f BAMPE \
  --nomodel \
  --shift -75 \
  --extsize 150 \
  --keep-dup all \
  -g hs \
  --qvalue 0.01 \
  -n sample_peaks \
  --outdir peaks/

# For broad accessible regions (optional, captures wider domains)
macs3 callpeak \
  -t sample.final.bam \
  -f BAMPE \
  --nomodel \
  --shift -75 \
  --extsize 150 \
  --keep-dup all \
  --broad \
  --broad-cutoff 0.05 \
  -g hs \
  -n sample_broad \
  --outdir peaks/
```

**Parameter rationale:**

| Parameter | Value | Why |
|-----------|-------|-----|
| `-f BAMPE` | Paired-end mode | Uses actual fragment sizes, not modeled extension |
| `--nomodel` | Skip model building | ATAC fragments are NOT ChIP fragments; model is inappropriate |
| `--shift -75` | Shift reads -75 bp | Centers the signal on the Tn5 insertion site |
| `--extsize 150` | Extend 150 bp | Creates a 150 bp window centered on insertion point |
| `--keep-dup all` | Keep all reads | PCR duplicates already removed upstream; biological duplicates are real |
| `-g hs` | Human effective genome | Use `mm` for mouse, `ce` for C. elegans, `dm` for Drosophila |
| `--qvalue 0.01` | FDR threshold | Stricter than default 0.05; use 0.05 for exploratory analysis |

### When to Use BAMPE vs BED

```
Decision: BAMPE vs BED format for MACS3

BAMPE (recommended for most ATAC-seq):
  - Uses actual paired-end fragment information
  - Most accurate representation of accessible regions
  - Use with: --nomodel --shift -75 --extsize 150

BED (Tn5 insertion sites):
  - Convert BAM to single-bp Tn5 insertion BED
  - Better for footprinting-resolution peak calling
  - Use with: --nomodel --shift -75 --extsize 150
  - Also used when BAM paired-end flags are inconsistent
```

### Peak Filtering and Merging

```bash
# Remove peaks overlapping blacklist
bedtools intersect -v -a peaks/sample_peaks_peaks.narrowPeak \
  -b /ref/hg38-blacklist.v2.bed > peaks/sample_peaks.filtered.narrowPeak

# For multi-sample analysis: create consensus peak set
# Iterative overlap merge requiring peak in >= 2 samples
cat peaks/*_peaks.filtered.narrowPeak | \
  sort -k1,1 -k2,2n | \
  bedtools merge -d 250 | \
  awk '{print $1"\t"$2"\t"$3"\t"$1":"$2"-"$3}' > peaks/consensus_peaks.bed
```

---

## Phase 5: Nucleosome-Free and Nucleosomal Fragment Separation

### Fragment Size Classes

```python
import pysam
import os

def separate_fragments(bam_file, output_dir="fragment_classes"):
    """Separate ATAC-seq fragments by nucleosome occupancy class.

    Fragment classes:
      NFR:         < 150 bp   (nucleosome-free, regulatory signal)
      Mono-nuc:    150-300 bp (single nucleosome)
      Di-nuc:      300-500 bp (two nucleosomes)
      Tri-nuc:     500-700 bp (three nucleosomes)
    """
    os.makedirs(output_dir, exist_ok=True)

    classes = {
        'nfr': (0, 150),
        'mononuc': (150, 300),
        'dinuc': (300, 500),
        'trinuc': (500, 700),
    }

    infile = pysam.AlignmentFile(bam_file, "rb")
    outfiles = {}
    for name, _ in classes.items():
        outpath = os.path.join(output_dir, f"{name}.bam")
        outfiles[name] = pysam.AlignmentFile(outpath, "wb", header=infile.header)

    counts = {name: 0 for name in classes}
    for read in infile:
        if (read.is_unmapped or read.is_secondary or read.is_supplementary
                or not read.is_proper_pair or read.is_reverse):
            continue
        frag_size = abs(read.template_length)
        for name, (lo, hi) in classes.items():
            if lo <= frag_size < hi:
                outfiles[name].write(read)
                # Also write the mate
                counts[name] += 1
                break

    infile.close()
    for name, f in outfiles.items():
        f.close()
        outpath = os.path.join(output_dir, f"{name}.bam")
        pysam.sort("-o", outpath, outpath)
        pysam.index(outpath)

    total = sum(counts.values())
    print("Fragment class counts:")
    for name, count in counts.items():
        lo, hi = classes[name]
        print(f"  {name} ({lo}-{hi} bp): {count:,} ({count/max(total,1):.1%})")
    return counts

separate_fragments("sample.final.bam")
```

### Using NFR Fragments for Regulatory Analysis

```
NFR fragments (< 150 bp) represent true regulatory accessibility:
  - Use NFR-only BAM for TF footprinting (highest resolution)
  - Use NFR-only BAM for motif enrichment analysis
  - Peak calling on NFR fragments gives TF-bound regulatory elements
  - Nucleosomal fragments are useful for nucleosome positioning analysis

Mono-nucleosomal fragments are useful for:
  - Nucleosome occupancy mapping (NucleoATAC)
  - Identifying nucleosome-depleted regions at promoters
  - Comparing nucleosome positioning between conditions
```

---

## Phase 6: Differential Accessibility Analysis

### Using DiffBind with DESeq2

```r
# R code for DiffBind differential accessibility analysis
library(DiffBind)

# Create sample sheet
samples <- data.frame(
  SampleID = c("ctrl_1", "ctrl_2", "ctrl_3", "treat_1", "treat_2", "treat_3"),
  Condition = c("control", "control", "control", "treated", "treated", "treated"),
  bamReads = c("ctrl_1.bam", "ctrl_2.bam", "ctrl_3.bam",
               "treat_1.bam", "treat_2.bam", "treat_3.bam"),
  Peaks = c("ctrl_1_peaks.narrowPeak", "ctrl_2_peaks.narrowPeak", "ctrl_3_peaks.narrowPeak",
            "treat_1_peaks.narrowPeak", "treat_2_peaks.narrowPeak", "treat_3_peaks.narrowPeak"),
  PeakCaller = rep("narrow", 6)
)

# DiffBind workflow
dba_obj <- dba(sampleSheet = samples)

# Count reads in consensus peaks
dba_obj <- dba.count(dba_obj, minOverlap = 2)

# Normalize (default: RLE from DESeq2)
dba_obj <- dba.normalize(dba_obj, normalize = DBA_NORM_RLE)

# Set contrast
dba_obj <- dba.contrast(dba_obj, categories = DBA_CONDITION)

# Run differential analysis
dba_obj <- dba.analyze(dba_obj, method = DBA_DESEQ2)

# Extract results
results <- dba.report(dba_obj, th = 0.05, fold = 1)
da_peaks <- as.data.frame(results)

cat("Total DA peaks:", nrow(da_peaks), "\n")
cat("Gained accessibility:", sum(da_peaks$Fold > 0), "\n")
cat("Lost accessibility:", sum(da_peaks$Fold < 0), "\n")
```

### Python-Based Differential Accessibility

```python
import pandas as pd
import numpy as np
from scipy.stats import mannwhitneyu
from statsmodels.stats.multitest import multipletests

def count_reads_in_peaks(bam_files, peak_bed, sample_names):
    """Count reads in consensus peaks for all samples."""
    import pysam

    peaks = pd.read_csv(peak_bed, sep='\t', header=None,
                        names=['chr', 'start', 'end', 'peak_id'])
    count_matrix = pd.DataFrame(index=peaks['peak_id'], columns=sample_names)

    for sample, bam_path in zip(sample_names, bam_files):
        bamfile = pysam.AlignmentFile(bam_path, "rb")
        counts = []
        for _, peak in peaks.iterrows():
            try:
                n = bamfile.count(peak['chr'], peak['start'], peak['end'])
            except ValueError:
                n = 0
            counts.append(n)
        bamfile.close()
        count_matrix[sample] = counts

    count_matrix = count_matrix.astype(int)
    return count_matrix

def differential_accessibility_deseq2_style(count_matrix, condition_labels, alpha=0.05):
    """Differential accessibility using DESeq2-like approach in Python.

    For production analysis, use R DiffBind. This provides a
    Mann-Whitney fallback for environments without R.
    """
    groups = list(set(condition_labels))
    assert len(groups) == 2, "Exactly 2 conditions required"

    g1_samples = [s for s, c in zip(count_matrix.columns, condition_labels) if c == groups[0]]
    g2_samples = [s for s, c in zip(count_matrix.columns, condition_labels) if c == groups[1]]

    # Size factor normalization (median-of-ratios)
    geometric_means = np.exp(np.log(count_matrix.replace(0, np.nan) + 1).mean(axis=1))
    ratios = count_matrix.add(1).div(geometric_means, axis=0)
    size_factors = ratios.median(axis=0)
    normalized = count_matrix.div(size_factors, axis=1)

    results = []
    for peak in count_matrix.index:
        g1_vals = normalized.loc[peak, g1_samples].values.astype(float)
        g2_vals = normalized.loc[peak, g2_samples].values.astype(float)

        mean_g1 = g1_vals.mean()
        mean_g2 = g2_vals.mean()
        log2fc = np.log2((mean_g2 + 1) / (mean_g1 + 1))

        try:
            _, pval = mannwhitneyu(g1_vals, g2_vals, alternative='two-sided')
        except ValueError:
            pval = 1.0

        results.append({
            'peak': peak,
            'mean_g1': mean_g1,
            'mean_g2': mean_g2,
            'log2FoldChange': log2fc,
            'pvalue': pval
        })

    results_df = pd.DataFrame(results).set_index('peak')
    _, results_df['padj'], _, _ = multipletests(results_df['pvalue'], method='fdr_bh')

    sig = results_df[(results_df['padj'] < alpha) &
                     (results_df['log2FoldChange'].abs() > 1)].sort_values('padj')

    print(f"Tested peaks: {len(results_df)}")
    print(f"DA peaks (padj < {alpha}, |log2FC| > 1): {len(sig)}")
    print(f"  Gained accessibility: {(sig['log2FoldChange'] > 0).sum()}")
    print(f"  Lost accessibility: {(sig['log2FoldChange'] < 0).sum()}")
    return results_df, sig
```

---

## Phase 7: Transcription Factor Footprinting

### TOBIAS Footprinting Pipeline

```bash
# TOBIAS: Transcription factor Occupancy prediction By Investigation of ATAC-seq Signal

# Step 1: Bias correction (correct Tn5 sequence preference)
TOBIAS ATACorrect \
  --bam sample.final.bam \
  --genome /ref/hg38.fa \
  --peaks peaks/consensus_peaks.bed \
  --outdir tobias/ \
  --cores 16

# Step 2: Calculate footprint scores
TOBIAS FootprintScores \
  --signal tobias/sample_corrected.bw \
  --regions peaks/consensus_peaks.bed \
  --output tobias/sample_footprints.bw \
  --cores 16

# Step 3: Identify bound/unbound motif sites
TOBIAS BINDetect \
  --motifs /ref/JASPAR2024_CORE_vertebrates.pfm \
  --signals tobias/control_footprints.bw tobias/treated_footprints.bw \
  --genome /ref/hg38.fa \
  --peaks peaks/consensus_peaks.bed \
  --outdir tobias/bindetect/ \
  --cond_names control treated \
  --cores 16

# Step 4: Visualize aggregate footprint
TOBIAS PlotAggregate \
  --TFBS tobias/bindetect/CTCF/CTCF_overview.txt \
  --signals tobias/control_corrected.bw tobias/treated_corrected.bw \
  --output tobias/CTCF_footprint.pdf \
  --share_y both \
  --plot_boundaries
```

**TOBIAS output interpretation:**

| File | Content |
|------|---------|
| `*_corrected.bw` | Tn5-bias-corrected signal track |
| `*_footprints.bw` | Footprint score track |
| `bindetect_results.txt` | Differential binding scores per TF |
| `*_overview.txt` | Per-motif-site binding classification |

```
BINDetect differential binding score interpretation:
  Score > 0: More bound in condition 2 (treated)
  Score < 0: More bound in condition 1 (control)
  |Score| > 0.1 with pvalue < 0.05: Differentially bound TF

Aggregate footprint plot interpretation:
  - V-shaped dip at motif center = TF protection from Tn5
  - Deep, narrow dip = strong, site-specific binding
  - Shallow dip = weak or transient binding
  - No dip = motif present but TF not bound
  - Flanking shoulders = positioned nucleosomes adjacent to bound TF
```

### HINT-ATAC Footprinting

```bash
# HINT-ATAC: footprinting optimized for ATAC-seq bias correction

# Step 1: Find footprints within peaks
rgt-hint footprinting \
  --atac-seq \
  --paired-end \
  --organism hg38 \
  --output-location hint_output/ \
  sample.final.bam \
  peaks/sample_peaks.narrowPeak

# Step 2: Motif matching at footprints
rgt-motifanalysis matching \
  --organism hg38 \
  --input-files hint_output/sample.final.bed \
  --output-location hint_output/motif_match/

# Step 3: Differential footprinting between conditions
rgt-hint differential \
  --organism hg38 \
  --bc \
  --nc 16 \
  --mpbs-files hint_output/control_mpbs.bed hint_output/treated_mpbs.bed \
  --reads-files control.bam treated.bam \
  --conditions control treated \
  --output-location hint_output/differential/
```

---

## Phase 8: Motif Deviation Analysis (chromVAR)

### chromVAR Workflow

```r
# R code for chromVAR motif deviation analysis
library(chromVAR)
library(motifmatchr)
library(BSgenome.Hsapiens.UCSC.hg38)
library(JASPAR2024)

# Load count matrix (peaks x samples)
counts <- readRDS("peak_counts.rds")  # SummarizedExperiment object

# Or create from scratch
peak_gr <- makeGRangesFromDataFrame(peaks_df)
fragment_counts <- getCounts(bam_files, peak_gr, paired = TRUE, by_rg = FALSE)

# Add GC bias
fragment_counts <- addGCBias(fragment_counts, genome = BSgenome.Hsapiens.UCSC.hg38)

# Get JASPAR motifs
pfm_list <- getMatrixSet(JASPAR2024, opts = list(
  collection = "CORE",
  tax_group = "vertebrates",
  all_versions = FALSE
))

# Find motif matches in peaks
motif_matches <- matchMotifs(pfm_list, fragment_counts,
                              genome = BSgenome.Hsapiens.UCSC.hg38)

# Compute deviations
deviations <- computeDeviations(object = fragment_counts,
                                 annotations = motif_matches)

# Extract deviation scores and variability
dev_scores <- deviationScores(deviations)    # z-scores per motif per sample
dev_zscores <- deviationScores(deviations)
variability <- computeVariability(deviations)

# Top variable motifs
top_var <- variability[order(-variability$variability), ]
head(top_var, 20)
```

### chromVAR Differential Analysis in Python

```python
import pandas as pd
import numpy as np
from scipy.stats import ttest_ind
from statsmodels.stats.multitest import multipletests

def chromvar_differential(deviation_matrix, metadata, group_col, alpha=0.05):
    """Identify TF motifs with differential chromVAR deviation scores.

    deviation_matrix: motifs x samples, z-score values from chromVAR
    """
    groups = metadata[group_col].unique()
    assert len(groups) == 2

    g1 = metadata[metadata[group_col] == groups[0]].index
    g2 = metadata[metadata[group_col] == groups[1]].index

    results = []
    for motif in deviation_matrix.index:
        g1_vals = deviation_matrix.loc[motif, g1].values
        g2_vals = deviation_matrix.loc[motif, g2].values
        mean_diff = g2_vals.mean() - g1_vals.mean()
        _, pval = ttest_ind(g1_vals, g2_vals)
        results.append({
            'motif': motif,
            'mean_dev_g1': g1_vals.mean(),
            'mean_dev_g2': g2_vals.mean(),
            'mean_diff': mean_diff,
            'pvalue': pval
        })

    results_df = pd.DataFrame(results).set_index('motif')
    _, results_df['padj'], _, _ = multipletests(results_df['pvalue'], method='fdr_bh')
    sig = results_df[results_df['padj'] < alpha].sort_values('padj')

    print(f"Significant motif deviations: {len(sig)}/{len(results_df)}")
    print(f"  Gained activity: {(sig['mean_diff'] > 0).sum()}")
    print(f"  Lost activity: {(sig['mean_diff'] < 0).sum()}")
    return results_df, sig
```

---

## Phase 9: Peak Annotation

### ChIPseeker Annotation

```r
# R code for peak annotation with ChIPseeker
library(ChIPseeker)
library(TxDb.Hsapiens.UCSC.hg38.knownGene)
library(org.Hs.eg.db)

txdb <- TxDb.Hsapiens.UCSC.hg38.knownGene

# Read peaks
peaks <- readPeakFile("peaks/consensus_peaks.narrowPeak")

# Annotate peaks relative to genomic features
peakAnno <- annotatePeak(peaks, TxDb = txdb,
                          tssRegion = c(-3000, 3000),
                          annoDb = "org.Hs.eg.db")

# Visualize annotation distribution
plotAnnoPie(peakAnno)
plotAnnoBar(peakAnno)
plotDistToTSS(peakAnno, title = "Distribution of ATAC-seq peaks relative to TSS")

# Extract annotated data frame
anno_df <- as.data.frame(peakAnno)

# Genomic feature distribution summary
cat("Peak annotation summary:\n")
print(peakAnno@annoStat)
```

### HOMER Peak Annotation

```bash
# HOMER annotatePeaks for genomic feature annotation
annotatePeaks.pl peaks/consensus_peaks.bed hg38 \
  -annStats peaks/annotation_stats.txt \
  -go peaks/go_enrichment/ \
  -genomeOntology peaks/genome_ontology/ \
  > peaks/annotated_peaks.txt

# Motif enrichment in peaks
findMotifsGenome.pl peaks/consensus_peaks.bed hg38 peaks/motifs/ \
  -size 200 -mask -p 16

# Known motif results: peaks/motifs/knownResults.html
# De novo motif results: peaks/motifs/homerResults.html
```

### Peak Annotation Feature Expectations

```
Typical ATAC-seq peak genomic distribution:
  Promoters (< 3kb from TSS):  20-40%
  Introns (gene body):         30-50%
  Intergenic:                  15-30%
  Exons:                       2-5%
  5' UTR:                      1-3%
  3' UTR:                      1-3%
  Downstream (< 3kb):          1-5%

Red flags:
  - > 50% promoter peaks: May indicate NFR-only fragments or promoter bias
  - > 50% intergenic: Possible contamination or very cell-type-specific enhancers
  - Very few peaks (< 10,000): Quality issue or too-strict threshold
  - > 300,000 peaks: Relaxed threshold or background noise
```

---

## Phase 10: Single-Cell ATAC-seq Integration

### ArchR Pipeline

```r
# R code for scATAC-seq analysis with ArchR
library(ArchR)
addArchRGenome("hg38")
set.seed(42)

# Create Arrow files from fragments
ArrowFiles <- createArrowFiles(
  inputFiles = c("ctrl_fragments.tsv.gz", "treat_fragments.tsv.gz"),
  sampleNames = c("control", "treated"),
  minTSS = 4,          # Minimum TSS enrichment score per cell
  minFrags = 1000,     # Minimum fragments per cell
  addTileMat = TRUE,   # 500 bp tile matrix
  addGeneScoreMat = TRUE  # Gene activity scores
)

# Create ArchR project
proj <- ArchRProject(ArrowFiles = ArrowFiles, outputDirectory = "archr_output")

# QC filtering
proj <- filterDoublets(proj)

# Dimensionality reduction (Iterative LSI)
proj <- addIterativeLSI(proj,
  useMatrix = "TileMatrix",
  name = "IterativeLSI",
  iterations = 4,
  clusterParams = list(resolution = 0.2, n.start = 10),
  varFeatures = 25000,
  dimsToUse = 1:30
)

# Clustering
proj <- addClusters(proj, reducedDims = "IterativeLSI",
                     method = "Seurat", resolution = 0.8)

# UMAP embedding
proj <- addUMAP(proj, reducedDims = "IterativeLSI",
                 name = "UMAP", nNeighbors = 30, minDist = 0.5)

# Peak calling per cluster (using MACS2)
proj <- addGroupCoverages(proj, groupBy = "Clusters")
proj <- addReproduciblePeakSet(proj, groupBy = "Clusters",
                                 peakMethod = "Macs2")
proj <- addPeakMatrix(proj)

# Motif deviations (chromVAR within ArchR)
proj <- addMotifAnnotations(proj, motifSet = "cisbp", name = "Motif")
proj <- addBgdPeaks(proj)
proj <- addDeviationsMatrix(proj, peakAnnotation = "Motif")

# Gene activity scores
gene_scores <- getMatrixFromProject(proj, useMatrix = "GeneScoreMatrix")

# Marker peaks per cluster
markerPeaks <- getMarkerFeatures(proj,
  useMatrix = "PeakMatrix",
  groupBy = "Clusters",
  bias = c("TSSEnrichment", "log10(nFrags)"),
  testMethod = "wilcoxon"
)
```

### Signac Pipeline

```r
# R code for scATAC-seq analysis with Signac
library(Signac)
library(Seurat)
library(GenomicRanges)
library(EnsDb.Hsapiens.v86)

# Create Seurat object from 10x output
counts <- Read10X_h5("filtered_peak_bc_matrix.h5")
metadata <- read.csv("singlecell.csv", header = TRUE, row.names = 1)
fragments <- CreateFragmentObject("fragments.tsv.gz", cells = colnames(counts))

chrom_assay <- CreateChromatinAssay(
  counts = counts,
  sep = c(":", "-"),
  genome = "hg38",
  fragments = fragments,
  min.cells = 10,
  min.features = 200
)

obj <- CreateSeuratObject(counts = chrom_assay, assay = "peaks", meta.data = metadata)

# QC metrics
annotations <- GetGRangesFromEnsDb(ensdb = EnsDb.Hsapiens.v86)
seqlevelsStyle(annotations) <- "UCSC"
Annotation(obj) <- annotations

obj <- NucleosomeSignal(obj)
obj <- TSSEnrichment(obj, fast = FALSE)

# Filter cells
obj <- subset(obj,
  nCount_peaks > 3000 &
  nCount_peaks < 100000 &
  nucleosome_signal < 4 &
  TSS.enrichment > 2
)

# Normalization and dim reduction (TF-IDF + SVD)
obj <- RunTFIDF(obj)
obj <- FindTopFeatures(obj, min.cutoff = "q0")
obj <- RunSVD(obj)

# Check LSI components (first component often correlates with depth - exclude it)
DepthCor(obj)
obj <- RunUMAP(obj, reduction = "lsi", dims = 2:30)
obj <- FindNeighbors(obj, reduction = "lsi", dims = 2:30)
obj <- FindClusters(obj, algorithm = 3, resolution = 0.5)

# Gene activity
gene_activities <- GeneActivity(obj)
obj[["RNA"]] <- CreateAssayObject(counts = gene_activities)
obj <- NormalizeData(obj, assay = "RNA")

# Differential peaks
da_peaks <- FindMarkers(obj, ident.1 = "cluster_1", ident.2 = "cluster_2",
                         test.use = "LR", latent.vars = "nCount_peaks")

# Motif analysis with chromVAR
obj <- RunChromVAR(obj, genome = BSgenome.Hsapiens.UCSC.hg38)
differential_motifs <- FindMarkers(obj, assay = "chromvar",
                                    ident.1 = "cluster_1", ident.2 = "cluster_2")
```

### ArchR vs Signac Decision Guide

| Criterion | ArchR | Signac |
|-----------|-------|--------|
| Large datasets (>100K cells) | Better (Arrow-based, on-disk) | Slower (in-memory) |
| Integration with Seurat | Indirect | Native |
| Peak calling | Built-in (MACS2) | External |
| Dimensionality reduction | Iterative LSI | TF-IDF + SVD |
| Memory usage | Low (disk-backed) | High (RAM) |
| Multi-sample analysis | Native | Manual |
| Documentation | Extensive tutorials | Seurat ecosystem docs |
| Custom genomes | Supported | Supported |

---

## Phase 11: Visualization

### Signal Tracks with deepTools

```bash
# Convert BAM to normalized bigWig
bamCoverage -b sample.final.bam \
  -o sample.bw \
  --normalizeUsing RPGC \
  --effectiveGenomeSize 2913022398 \
  --binSize 10 \
  --numberOfProcessors 16

# Compute matrix around TSS
computeMatrix reference-point \
  -S control.bw treated.bw \
  -R /ref/hg38_tss.bed \
  --beforeRegionStartLength 3000 \
  --afterRegionStartLength 3000 \
  --binSize 10 \
  -o tss_matrix.gz \
  -p 16

# Heatmap
plotHeatmap -m tss_matrix.gz \
  -out tss_heatmap.png \
  --colorMap RdBu_r \
  --whatToShow 'heatmap and colorbar' \
  --zMin 0 --zMax auto

# Profile plot
plotProfile -m tss_matrix.gz \
  -out tss_profile.png \
  --perGroup
```

### Volcano Plot for DA Peaks

```python
import matplotlib.pyplot as plt
import numpy as np

def volcano_plot_da(results_df, alpha=0.05, fc_cutoff=1.0,
                    output_png="da_volcano.png"):
    """Volcano plot for differential accessibility results."""
    results_df = results_df.copy()
    results_df['-log10padj'] = -np.log10(results_df['padj'].clip(1e-300))

    sig_up = results_df[(results_df['padj'] < alpha) & (results_df['log2FoldChange'] > fc_cutoff)]
    sig_down = results_df[(results_df['padj'] < alpha) & (results_df['log2FoldChange'] < -fc_cutoff)]
    ns = results_df[~results_df.index.isin(sig_up.index.union(sig_down.index))]

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.scatter(ns['log2FoldChange'], ns['-log10padj'], c='grey', alpha=0.3, s=5, label='NS')
    ax.scatter(sig_up['log2FoldChange'], sig_up['-log10padj'], c='#e74c3c', alpha=0.6, s=10,
               label=f'Gained ({len(sig_up)})')
    ax.scatter(sig_down['log2FoldChange'], sig_down['-log10padj'], c='#2980b9', alpha=0.6, s=10,
               label=f'Lost ({len(sig_down)})')
    ax.axhline(-np.log10(alpha), color='grey', linestyle='--', alpha=0.5)
    ax.axvline(fc_cutoff, color='grey', linestyle='--', alpha=0.5)
    ax.axvline(-fc_cutoff, color='grey', linestyle='--', alpha=0.5)
    ax.set_xlabel('log2 Fold Change')
    ax.set_ylabel('-log10(adjusted p-value)')
    ax.set_title('Differential Accessibility')
    ax.legend()
    plt.tight_layout()
    plt.savefig(output_png, dpi=150)
    print(f"Saved: {output_png}")
```

---

## Evidence Grading Framework

| Tier | Criteria | Confidence |
|------|----------|------------|
| **T1** | DA peak confirmed by footprinting + motif enrichment + expression correlation, padj < 0.01, |log2FC| > 2 | High |
| **T2** | DA peak with consistent motif deviation (chromVAR), replicated across samples, padj < 0.05 | Medium-High |
| **T3** | DA peak (padj < 0.05, |log2FC| > 1), single condition or unreplicated | Medium |
| **T4** | Marginal DA (padj 0.05-0.1 or |log2FC| < 1), no motif or footprinting support | Low |

---

## Boundary Rules

```
DO:
- Process ATAC-seq BAM files: filtering, Tn5 correction, fragment separation
- Call peaks with MACS3 using ATAC-specific parameters
- Calculate and interpret QC metrics (fragment sizes, TSS enrichment, FRiP)
- Run differential accessibility analysis (DiffBind/DESeq2 or Python fallback)
- Perform TF footprinting (TOBIAS, HINT-ATAC)
- Run chromVAR motif deviation analysis
- Annotate peaks (ChIPseeker, HOMER)
- Guide scATAC-seq analysis (ArchR, Signac)

DO NOT:
- Perform read alignment from raw FASTQ (upstream step)
- Run single-cell RNA-seq clustering (use single-cell-analysis skill)
- Deep pathway enrichment on DA gene lists (use gene-enrichment skill)
- ChIP-seq specific analysis (use chipseq-analysis skill)
- Multi-omics integration (use multi-omics-integration skill)
```

## Completeness Checklist

- [ ] BAM filtering completed (MAPQ, duplicates, mitochondrial, blacklist)
- [ ] Fragment size distribution plotted and QC metrics assessed
- [ ] TSS enrichment score calculated and interpreted
- [ ] Tn5 offset correction applied (if footprinting or base-pair analysis)
- [ ] Peak calling with ATAC-specific MACS3 parameters completed
- [ ] NFR vs nucleosomal fragments separated (if required)
- [ ] Differential accessibility analysis performed with appropriate statistics
- [ ] TF footprinting completed (TOBIAS or HINT-ATAC)
- [ ] Motif deviation scores computed (chromVAR)
- [ ] Peaks annotated to genomic features (ChIPseeker/HOMER)
- [ ] Visualizations generated (fragment sizes, TSS enrichment, volcano, heatmaps)
- [ ] Evidence tier assigned to major findings
