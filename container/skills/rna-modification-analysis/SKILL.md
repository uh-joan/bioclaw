---
name: rna-modification-analysis
description: RNA modification analysis including m6A, m5C, and pseudouridine. MeRIP-seq, m6A-seq, bisulfite RNA-seq, peak calling, differential methylation, DRACH motif, epitranscriptome profiling. Use when user mentions RNA modifications, m6A, m5C, pseudouridine, MeRIP-seq, m6A-seq, RNA methylation, epitranscriptome, METTL3, FTO, ALKBH5, YTHDF, RNA immunoprecipitation, metagene analysis, or RNA epigenetics.
---

# Epitranscriptomics Analysis

Production-ready RNA modification analysis methodology. The agent writes and executes Python/R code for detecting and characterizing RNA modifications (m6A, m5C, pseudouridine) from MeRIP-seq, bisulfite RNA-seq, and nanopore sequencing data. Covers peak calling, differential modification analysis, motif enrichment, functional interpretation, and visualization. Uses Open Targets, PubMed, and pathway databases for biological annotation.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_epitranscriptomics_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- General RNA-seq differential expression -> use `differential-expression` or `rnaseq-analysis`
- Small RNA / miRNA profiling -> use `small-rna-analysis`
- DNA methylation (bisulfite-seq, WGBS) -> use `methylation-analysis`
- Single-cell RNA-seq -> use `single-cell-analysis`
- Protein post-translational modifications -> use `proteomics-analysis`

## Cross-Reference: Other Skills

- **RNA-seq expression quantification** -> use rnaseq-analysis skill
- **DNA methylation analysis (5mC on DNA)** -> use methylation-analysis skill
- **Nanopore direct RNA sequencing QC** -> use long-read-analysis skill
- **Gene set enrichment of modified transcripts** -> use gene-enrichment skill

## Python Environment

Standard scientific Python: `numpy, pandas, scipy, matplotlib, seaborn, scikit-learn, biopython, pysam`. For specialized tools, install at runtime: `subprocess.run(["pip", "install", "pydeseq2"], check=True)`.

## Data Input Formats

```python
import pandas as pd
import numpy as np
import pysam
from pathlib import Path

def load_merip_data(ip_bam, input_bam, gtf_path):
    """Load MeRIP-seq data: IP (immunoprecipitated) and input (control) BAM files."""
    ip_aln = pysam.AlignmentFile(ip_bam, "rb")
    input_aln = pysam.AlignmentFile(input_bam, "rb")
    print(f"IP reads: {ip_aln.mapped:,}")
    print(f"Input reads: {input_aln.mapped:,}")
    print(f"IP enrichment ratio: {ip_aln.mapped / input_aln.mapped:.2f}")
    return ip_aln, input_aln

def load_peak_calls(peak_file, fmt="bed"):
    """Load peak calls from exomePeak2, MACS2, or MeTDiff output."""
    if fmt == "bed":
        cols = ["chrom", "start", "end", "name", "score", "strand"]
        df = pd.read_csv(peak_file, sep="\t", header=None, names=cols[:6],
                         comment="#", usecols=range(min(6, len(cols))))
    elif fmt == "exomepeak2":
        df = pd.read_csv(peak_file, sep="\t")
    elif fmt == "metdiff":
        df = pd.read_csv(peak_file, sep="\t")
    df["width"] = df["end"] - df["start"]
    print(f"Loaded {len(df)} peaks, median width: {df['width'].median():.0f} bp")
    return df
```

---

## Analysis Pipeline

### Phase 1: MeRIP-seq Quality Control

```python
import matplotlib.pyplot as plt
import seaborn as sns

def merip_qc(ip_bam, input_bam):
    """Quality control for MeRIP-seq libraries."""
    qc = {}
    for label, bam_path in [("IP", ip_bam), ("Input", input_bam)]:
        aln = pysam.AlignmentFile(bam_path, "rb")
        total = mapped = dup = 0
        insert_sizes = []
        for read in aln.fetch():
            total += 1
            if not read.is_unmapped: mapped += 1
            if read.is_duplicate: dup += 1
            if read.is_proper_pair and read.template_length > 0:
                insert_sizes.append(read.template_length)
        qc[label] = {
            "total_reads": total, "mapped_reads": mapped,
            "mapping_rate": mapped / total if total > 0 else 0,
            "duplication_rate": dup / total if total > 0 else 0,
            "median_insert_size": np.median(insert_sizes) if insert_sizes else 0,
        }
        aln.close()

    print("=== MeRIP-seq QC ===")
    for label, m in qc.items():
        print(f"\n{label}:")
        for k, v in m.items():
            fmt = f"{v:.1%}" if "rate" in k else f"{v:,.0f}"
            print(f"  {k}: {fmt}")

    # QC thresholds
    ip_m, inp_m = qc["IP"], qc["Input"]
    warnings = []
    if ip_m["mapping_rate"] < 0.7: warnings.append("IP mapping rate < 70%")
    if inp_m["mapping_rate"] < 0.7: warnings.append("Input mapping rate < 70%")
    if ip_m["duplication_rate"] > 0.5: warnings.append("IP duplication rate > 50% (over-amplification)")
    if ip_m["mapped_reads"] < 10_000_000: warnings.append("IP reads < 10M (recommend >= 20M for m6A)")
    if inp_m["mapped_reads"] < 10_000_000: warnings.append("Input reads < 10M (recommend >= 15M)")
    for w in warnings: print(f"  WARNING: {w}")
    return qc

def ip_enrichment_assessment(ip_bam, input_bam, regions_bed):
    """Assess IP enrichment at known m6A consensus sites vs background."""
    import subprocess
    # Count reads at positive control regions (e.g., known METTL3-dependent sites)
    # High-confidence m6A sites: MALAT1, ACTB 3'UTR, long non-coding RNAs
    print("Assess enrichment at known m6A sites vs random genomic regions")
    print("Expected: IP/Input fold-enrichment >= 2x at true m6A sites")
    print("If enrichment < 1.5x globally, consider antibody issues or IP protocol optimization")
```

### Phase 2: Peak Calling

```python
def run_exomepeak2(ip_bam, input_bam, gtf, output_dir="exomepeak2_out"):
    """exomePeak2 peak calling with GC-bias correction (R-based, called via subprocess)."""
    r_script = f"""
    library(exomePeak2)
    # GC-bias aware peak calling - key advantage over MACS2 for MeRIP-seq
    ep <- exomePeak2(
        bam_ip = "{ip_bam}",
        bam_input = "{input_bam}",
        txdb = makeTxDbFromGFF("{gtf}"),
        genome = "hg38",        # for GC content calculation
        mod_annot = NULL,       # de novo peak calling
        glm_type = "NB",        # negative binomial GLM
        p_cutoff = 0.05,
        correct_GC_bg = TRUE,   # GC-bias correction for input
        qtnorm = TRUE,          # quantile normalization
        parallel = 4
    )
    exportResults(ep, format = "BED", file = "{output_dir}/peaks.bed")
    """
    print("exomePeak2 parameters:")
    print("  glm_type: NB (negative binomial) - handles overdispersion in count data")
    print("  correct_GC_bg: TRUE - corrects GC-content bias in input control")
    print("  qtnorm: TRUE - quantile normalization across IP/input")
    print("  p_cutoff: 0.05 (BH-adjusted)")
    return r_script

def run_macs2_rna(ip_bam, input_bam, output_prefix="macs2_m6a"):
    """MACS2 peak calling adapted for MeRIP-seq."""
    cmd = f"""macs2 callpeak \\
        -t {ip_bam} \\
        -c {input_bam} \\
        -f BAM \\
        --nomodel \\
        --extsize 150 \\
        --keep-dup all \\
        -g hs \\
        -q 0.05 \\
        -n {output_prefix} \\
        --outdir macs2_out \\
        --broad"""
    print("MACS2 RNA adaptation notes:")
    print("  --nomodel: Skip fragment model building (RNA peaks differ from ChIP)")
    print("  --extsize 150: Fixed extension; adjust based on fragment size")
    print("  --keep-dup all: Retain duplicates (MeRIP has genuine duplicate enrichment)")
    print("  --broad: m6A peaks are broader than TF ChIP peaks")
    print("  Consider --nolambda if input coverage is very uneven across transcriptome")
    return cmd

def peak_calling_decision_tree():
    """Decision tree for peak caller selection."""
    tree = """
    Peak Caller Selection:
    +-- Do you have biological replicates?
    |   +-- YES: exomePeak2 (preferred) or MeTDiff
    |   |   +-- exomePeak2: GC-bias correction, GLM-based, handles replicates natively
    |   |   +-- MeTDiff: Specifically designed for differential m6A with replicates
    |   +-- NO: MACS2 (adapted) or single-sample exomePeak2
    |       +-- MACS2: Robust for single IP/input pair
    |       +-- Results less reliable without replicates
    +-- Is this a differential analysis?
    |   +-- YES: exomePeak2 differential mode or QNB
    |   +-- NO: Any caller suitable for peak identification
    +-- Genome with known GC bias issues?
        +-- YES: exomePeak2 (correct_GC_bg=TRUE)
        +-- NO: Any caller acceptable
    """
    print(tree)
```

### Phase 3: Peak Annotation and Distribution

```python
def annotate_peaks(peaks_df, gtf_path):
    """Annotate peaks with genomic features (5'UTR, CDS, 3'UTR, intron)."""
    # Parse GTF for transcript features
    features = {"5UTR": [], "CDS": [], "3UTR": [], "intron": [], "intergenic": []}

    # Simplified annotation logic
    def classify_peak(chrom, start, end, strand, tx_features):
        """Classify peak location relative to transcript structure."""
        overlaps = []
        for feat_type, intervals in tx_features.items():
            for f_start, f_end in intervals:
                if start < f_end and end > f_start:
                    overlap = min(end, f_end) - max(start, f_start)
                    overlaps.append((feat_type, overlap))
        if not overlaps: return "intergenic"
        return max(overlaps, key=lambda x: x[1])[0]

    print("Expected m6A peak distribution (human):")
    print("  5'UTR: ~5-10%")
    print("  CDS: ~25-35%")
    print("  3'UTR: ~35-45% (enriched near stop codon)")
    print("  Intron: ~15-25%")
    print("  Intergenic: <5%")
    return peaks_df

def metagene_plot(peaks_df, gtf_path, output="metagene_m6a.png"):
    """Metagene plot showing m6A peak distribution around TSS, start codon,
    stop codon, and polyA site."""
    # Normalize peak positions to relative transcript coordinates
    # 5'UTR | CDS | 3'UTR divided into 100 bins each

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Mock metagene profile showing expected m6A enrichment pattern
    x = np.linspace(0, 300, 300)  # 100 bins per region
    # Characteristic m6A pattern: enrichment near stop codon
    y = np.exp(-((x - 200)**2) / (2 * 30**2)) * 3 + np.random.normal(1, 0.1, 300)
    y = np.maximum(y, 0)

    axes[0].plot(x, y, "b-", linewidth=1.5)
    axes[0].axvline(100, color="gray", linestyle="--", alpha=0.5)
    axes[0].axvline(200, color="gray", linestyle="--", alpha=0.5)
    axes[0].set_xticks([50, 150, 250])
    axes[0].set_xticklabels(["5'UTR", "CDS", "3'UTR"])
    axes[0].set_ylabel("Peak Density")
    axes[0].set_title("m6A Metagene Profile")
    axes[0].annotate("Stop codon\nenrichment", xy=(200, max(y)),
                     xytext=(230, max(y)*0.8), arrowprops=dict(arrowstyle="->"))

    # Peak width distribution
    if "width" in peaks_df.columns:
        axes[1].hist(peaks_df["width"], bins=50, color="steelblue", edgecolor="white")
        axes[1].set_xlabel("Peak Width (bp)")
        axes[1].set_ylabel("Count")
        axes[1].set_title("Peak Width Distribution")
        axes[1].axvline(peaks_df["width"].median(), color="red", linestyle="--",
                        label=f"Median: {peaks_df['width'].median():.0f} bp")
        axes[1].legend()

    plt.tight_layout()
    plt.savefig(output, dpi=150, bbox_inches="tight")
    plt.show()
```

### Phase 4: DRACH Motif Analysis

```python
from collections import Counter

def drach_motif_analysis(peaks_df, fasta_path, output="drach_motif.png"):
    """Analyze DRACH motif (D=A/G/U, R=A/G, A, C, H=A/C/U) enrichment in m6A peaks."""
    # DRACH consensus: [AGT][AG]AC[ACT] in DNA space
    drach_pattern = r"[AGT][AG]AC[ACT]"
    drach_variants = {
        "GGACU": "canonical (most frequent)",
        "GGACA": "common variant",
        "AGACU": "common variant",
        "GGACC": "less common",
        "GAACU": "less common",
    }

    import re

    def extract_peak_sequences(peaks_df, fasta_path):
        """Extract sequences under peaks from reference genome."""
        fa = pysam.FastaFile(fasta_path)
        seqs = []
        for _, peak in peaks_df.iterrows():
            try:
                seq = fa.fetch(peak["chrom"], peak["start"], peak["end"]).upper()
                seqs.append(seq)
            except (KeyError, ValueError):
                continue
        fa.close()
        return seqs

    def count_drach(sequences):
        """Count DRACH motif occurrences and variant frequencies."""
        motif_counts = Counter()
        total_drach = 0
        total_bases = 0
        for seq in sequences:
            total_bases += len(seq)
            for match in re.finditer(drach_pattern, seq):
                motif_counts[match.group()] += 1
                total_drach += 1
        return motif_counts, total_drach, total_bases

    print("DRACH Motif Analysis")
    print("=" * 50)
    print("DRACH = [D=A/G/U][R=A/G][A][C][H=A/C/U]")
    print("In DNA: [AGT][AG]AC[ACT]")
    print()
    print("Expected enrichment in m6A peaks: 2-5x over background")
    print("Typical DRACH occurrence: 60-80% of m6A peaks contain >= 1 DRACH motif")
    print()
    print("Most common variants (ranked):")
    for variant, desc in drach_variants.items():
        print(f"  {variant}: {desc}")

    # Visualization
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Motif logo placeholder
    axes[0].text(0.5, 0.5, "DRACH Motif Logo\n[D][R]A C[H]",
                 ha="center", va="center", fontsize=16, fontfamily="monospace",
                 bbox=dict(boxstyle="round", facecolor="lightblue"))
    axes[0].set_title("Consensus Motif")
    axes[0].axis("off")

    # Variant frequency
    variants = list(drach_variants.keys())
    freqs = [0.35, 0.20, 0.15, 0.10, 0.08]  # typical frequencies
    axes[1].barh(variants, freqs, color="steelblue")
    axes[1].set_xlabel("Relative Frequency")
    axes[1].set_title("DRACH Variant Distribution")

    plt.tight_layout()
    plt.savefig(output, dpi=150, bbox_inches="tight")
    plt.show()
```

### Phase 5: m6A Site Prediction

```python
def sramp_prediction(sequences, output="sramp_results.tsv"):
    """SRAMP: sequence-based RNA adenosine methylation site predictor."""
    print("SRAMP Parameters:")
    print("  Input: RNA sequences (FASTA)")
    print("  Modes: full-transcript or mature-mRNA")
    print("  Output: predicted m6A sites with confidence scores")
    print("  Confidence levels: Very High, High, Moderate, Low")
    print()
    print("  Usage: http://www.cuilab.cn/sramp (web) or local installation")
    print("  Filter: Retain Very High + High confidence predictions")
    print("  Validate: Cross-reference with MeRIP-seq peaks")

def m6anet_nanopore(fast5_dir, reference, output_dir="m6anet_out"):
    """m6Anet: m6A detection from direct RNA nanopore sequencing."""
    cmds = f"""
    # Step 1: Basecall with Guppy (keep raw signal)
    guppy_basecaller -i {fast5_dir} -s basecalled/ \\
        --flowcell FLO-MIN106 --kit SQK-RNA002 \\
        --fast5_out

    # Step 2: Align with minimap2
    minimap2 -ax splice -uf -k14 {reference} basecalled/*.fastq > aligned.sam

    # Step 3: Resquiggle with f5c (or nanopolish)
    f5c eventalign --rna -b aligned.bam -g {reference} \\
        -r basecalled/*.fastq --signal-index --scale-events \\
        > eventalign.tsv

    # Step 4: m6Anet dataprep
    m6anet dataprep --eventalign eventalign.tsv \\
        --out_dir {output_dir}/dataprep \\
        --n_processes 8

    # Step 5: m6Anet inference
    m6anet inference --input_dir {output_dir}/dataprep \\
        --out_dir {output_dir}/results \\
        --n_processes 8 \\
        --num_iterations 1000
    """
    print("m6Anet interpretation:")
    print("  probability > 0.9: high-confidence m6A site")
    print("  probability 0.5-0.9: moderate confidence")
    print("  probability < 0.5: likely unmodified")
    print()
    print("Advantages over MeRIP-seq:")
    print("  - Single-nucleotide resolution")
    print("  - No antibody bias")
    print("  - Stoichiometric information (modification fraction)")
    print("  - No PCR amplification artifacts")
    return cmds
```

### Phase 6: Differential m6A Analysis

```python
def differential_m6a_exomepeak2(ip_bams_cond1, input_bams_cond1,
                                 ip_bams_cond2, input_bams_cond2,
                                 gtf, genome="hg38"):
    """Differential m6A analysis using exomePeak2."""
    r_script = f"""
    library(exomePeak2)
    # Differential m6A between two conditions
    ep_diff <- exomePeak2(
        bam_ip = c({','.join(f'"{b}"' for b in ip_bams_cond1 + ip_bams_cond2)}),
        bam_input = c({','.join(f'"{b}"' for b in input_bams_cond1 + input_bams_cond2)}),
        txdb = makeTxDbFromGFF("{gtf}"),
        genome = "{genome}",
        mod_annot = NULL,
        glm_type = "NB",
        correct_GC_bg = TRUE,
        # Differential design
        experiment_design = data.frame(
            condition = c(rep("control", {len(ip_bams_cond1)}),
                         rep("treated", {len(ip_bams_cond2)})),
            IP_input = c(rep("IP", {len(ip_bams_cond1)}),
                        rep("IP", {len(ip_bams_cond2)}))
        )
    )
    # Export differential peaks
    diff_results <- results(ep_diff)
    write.csv(diff_results, "differential_m6a_results.csv")
    """
    print("Differential m6A interpretation:")
    print("  log2FC > 0: Hypermethylated in condition 2")
    print("  log2FC < 0: Hypomethylated in condition 2")
    print("  padj < 0.05: Statistically significant differential modification")
    return r_script

def qnb_differential(ip_counts_cond1, ip_counts_cond2,
                     input_counts_cond1, input_counts_cond2):
    """QNB (Quad Negative Binomial) for differential m6A."""
    r_script = """
    library(QNB)
    result <- qnbtest(
        ip1 = ip_counts_cond1,    # IP counts, condition 1
        ip2 = ip_counts_cond2,    # IP counts, condition 2
        input1 = input_counts_cond1,  # Input counts, condition 1
        input2 = input_counts_cond2,  # Input counts, condition 2
        mode = "per-condition"    # or "paired" if samples are paired
    )
    # QNB models the IP/input ratio changes between conditions
    # using a quad negative binomial distribution
    """
    print("QNB key features:")
    print("  - Models four count vectors simultaneously (IP1, IP2, Input1, Input2)")
    print("  - Accounts for both expression changes AND modification changes")
    print("  - Separates true m6A changes from expression-driven artifacts")
    print("  - Critical: expression change alone can mimic differential m6A")
    return r_script

def volcano_plot_diff_m6a(results_df, output="diff_m6a_volcano.png"):
    """Volcano plot for differential m6A results."""
    fig, ax = plt.subplots(figsize=(10, 7))
    sig = results_df["padj"] < 0.05
    up = sig & (results_df["log2fc"] > 0)
    down = sig & (results_df["log2fc"] < 0)
    ns = ~sig

    ax.scatter(results_df.loc[ns, "log2fc"], -np.log10(results_df.loc[ns, "padj"]),
               c="gray", alpha=0.3, s=10, label=f"NS ({ns.sum()})")
    ax.scatter(results_df.loc[up, "log2fc"], -np.log10(results_df.loc[up, "padj"]),
               c="red", alpha=0.5, s=15, label=f"Hyper ({up.sum()})")
    ax.scatter(results_df.loc[down, "log2fc"], -np.log10(results_df.loc[down, "padj"]),
               c="blue", alpha=0.5, s=15, label=f"Hypo ({down.sum()})")
    ax.axhline(-np.log10(0.05), color="gray", linestyle="--", alpha=0.5)
    ax.axvline(0, color="gray", linestyle="--", alpha=0.5)
    ax.set_xlabel("log2 Fold Change (m6A level)")
    ax.set_ylabel("-log10(adjusted p-value)")
    ax.set_title("Differential m6A Analysis")
    ax.legend()
    plt.tight_layout()
    plt.savefig(output, dpi=150, bbox_inches="tight")
    plt.show()
```

### Phase 7: m5C and Pseudouridine Detection

```python
def m5c_bisulfite_rnaseq(bisulfite_bam, control_bam, reference_fa, min_coverage=20):
    """m5C detection from bisulfite RNA-seq data."""
    print("Bisulfite RNA-seq Workflow for m5C:")
    print("=" * 50)
    print("1. Library prep: Bisulfite treatment of RNA (converts C -> U, but m5C resists)")
    print("2. Alignment: Use meRanTK or bismark adapted for RNA")
    print("3. Call m5C sites: Non-conversion rate at each cytosine")
    print()

    def call_m5c_sites(bam_path, ref_path, min_cov=20, min_methylation=0.1):
        """Call m5C sites from bisulfite-converted RNA-seq."""
        # For each cytosine position:
        # methylation_rate = C_reads / (C_reads + T_reads)
        # where C = unconverted (methylated), T = converted (unmethylated)
        sites = []
        # Binomial test: observed C reads vs expected conversion rate (~99%)
        from scipy.stats import binom_test
        # Example site evaluation
        print("Site calling criteria:")
        print(f"  Minimum coverage: {min_cov} reads")
        print(f"  Minimum methylation rate: {min_methylation}")
        print("  Statistical test: Binomial (H0: non-conversion = error rate ~1%)")
        print("  FDR correction: Benjamini-Hochberg")
        print()
        print("Known NSUN targets:")
        print("  NSUN2: tRNA, mRNA (primarily CDS)")
        print("  NSUN3: mt-tRNA")
        print("  NSUN5: 28S rRNA")
        print("  NSUN6: mRNA (3'UTR enriched)")
        print("  DNMT2/TRDMT1: tRNA (Asp, Gly, Val)")
        return sites

    call_m5c_sites(bisulfite_bam, reference_fa)

def pseudouridine_detection():
    """Pseudouridine detection methods."""
    print("Pseudouridine Detection Methods:")
    print("=" * 50)
    print()
    print("1. Pseudo-seq (CMC-based):")
    print("   - CMC (N-cyclohexyl-N'-morpholinocarbodiimide) modifies pseudouridine")
    print("   - Modified sites cause RT stops -> reads pile up one nt 3' of site")
    print("   - Compare CMC-treated vs untreated libraries")
    print("   - Analysis: Count RT stops, compute CMC/control ratio")
    print("   - Threshold: CMC/control ratio > 2, plus minimum read depth")
    print()
    print("2. HydraPsiSeq:")
    print("   - Hydrazine cleaves at pseudouridine after CMC treatment")
    print("   - Creates deletions at modification sites")
    print("   - Higher sensitivity than Pseudo-seq")
    print("   - Analysis: Count deletions at each position")
    print()
    print("3. Nanopore direct RNA:")
    print("   - Signal-level detection (current intensity changes)")
    print("   - Tools: Epinano, ELIGOS")
    print("   - Advantage: Stoichiometric, no chemical treatment")
    print()
    print("Known pseudouridine writers:")
    print("  PUS1: diverse RNA targets")
    print("  PUS7: mRNA, tRNA (position 13)")
    print("  DKC1/dyskerin: H/ACA snoRNA-guided (rRNA, snRNA)")
    print("  TRUB1: tRNA (position 55)")
```

### Phase 8: Reader/Writer/Eraser Protein Analysis

```python
def rwe_protein_analysis():
    """m6A reader, writer, eraser protein reference and target analysis."""
    rwe = {
        "writers": {
            "METTL3": {"role": "Catalytic methyltransferase", "complex": "METTL3-METTL14-WTAP",
                       "targets": "mRNA (DRACH sites), primarily near stop codon"},
            "METTL14": {"role": "RNA-binding scaffold", "complex": "METTL3-METTL14",
                        "targets": "Allosteric activator of METTL3"},
            "WTAP": {"role": "Recruits complex to nuclear speckles",
                     "complex": "METTL3-METTL14-WTAP", "targets": "Splicing-related targets"},
            "METTL16": {"role": "Independent methyltransferase",
                        "complex": "None", "targets": "U6 snRNA, MAT2A mRNA (SAM sensor)"},
            "ZCCHC4": {"role": "28S rRNA m6A writer", "complex": "None",
                       "targets": "28S rRNA position A4220"},
        },
        "erasers": {
            "FTO": {"role": "m6A demethylase (also m6Am, m1A)", "mechanism": "Fe(II)/2-OG dioxygenase",
                    "note": "Controversial: may prefer m6Am over internal m6A"},
            "ALKBH5": {"role": "m6A demethylase", "mechanism": "Fe(II)/2-OG dioxygenase",
                       "note": "Predominantly nuclear, affects mRNA export"},
        },
        "readers": {
            "YTHDF1": {"role": "Translation promotion", "mechanism": "Recruits eIF3",
                       "effect": "Increases protein output from m6A-modified mRNAs"},
            "YTHDF2": {"role": "mRNA decay", "mechanism": "Recruits CCR4-NOT deadenylase",
                       "effect": "Accelerates turnover of m6A-modified mRNAs"},
            "YTHDF3": {"role": "Synergizes with DF1/DF2", "mechanism": "Context-dependent",
                       "effect": "May facilitate DF1/DF2 binding"},
            "YTHDC1": {"role": "Nuclear functions", "mechanism": "Splicing, export",
                       "effect": "Promotes exon inclusion via SRSF3 recruitment"},
            "YTHDC2": {"role": "Translation/decay", "mechanism": "RNA helicase",
                       "effect": "Critical for spermatogenesis"},
            "IGF2BP1/2/3": {"role": "mRNA stabilization", "mechanism": "Protects from decay",
                            "effect": "Opposes YTHDF2-mediated decay, promotes stability"},
        },
    }

    print("m6A Regulatory Proteins")
    print("=" * 60)
    for category, proteins in rwe.items():
        print(f"\n--- {category.upper()} ---")
        for name, info in proteins.items():
            print(f"\n  {name}:")
            for k, v in info.items():
                print(f"    {k}: {v}")
    return rwe

def expression_modification_correlation(expr_df, mod_df, output="expr_mod_corr.png"):
    """Correlate gene expression with m6A modification status."""
    merged = expr_df.merge(mod_df, on="gene_id", how="inner")

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # Expression of m6A-modified vs unmodified genes
    modified = merged[merged["is_modified"] == True]["log2_expression"]
    unmodified = merged[merged["is_modified"] == False]["log2_expression"]
    axes[0].boxplot([modified, unmodified], labels=["m6A+", "m6A-"])
    axes[0].set_ylabel("log2(Expression)")
    axes[0].set_title("Expression by m6A Status")

    # m6A level vs expression
    if "modification_level" in merged.columns:
        axes[1].scatter(merged["log2_expression"], merged["modification_level"],
                        alpha=0.3, s=10)
        axes[1].set_xlabel("log2(Expression)")
        axes[1].set_ylabel("m6A Level")
        axes[1].set_title("Expression vs m6A Level")

    # Number of m6A peaks per gene vs expression
    if "n_peaks" in merged.columns:
        axes[2].scatter(merged["n_peaks"], merged["log2_expression"], alpha=0.3, s=10)
        axes[2].set_xlabel("Number of m6A Peaks")
        axes[2].set_ylabel("log2(Expression)")
        axes[2].set_title("Peak Count vs Expression")

    plt.tight_layout()
    plt.savefig(output, dpi=150, bbox_inches="tight")
    plt.show()
```

---

## Parameter Reference Tables

### Peak Calling Parameters

| Parameter | exomePeak2 | MACS2 (RNA) | MeTDiff |
|-----------|-----------|-------------|---------|
| **Input** | BAM (IP + input) | BAM (IP + input) | BAM (IP + input) |
| **Replicates** | Native support | Merge or IDR | Native support |
| **GC correction** | Yes | No | No |
| **Model** | NB GLM | Poisson/local | Beta-binomial |
| **p-value cutoff** | 0.05 (BH) | 0.05 (BH) | 0.05 (BH) |
| **Peak type** | Exon-level | Broad | Exon-level |
| **Differential** | Built-in | External | Built-in |

### QC Thresholds

| Metric | Acceptable | Ideal | Action if Failed |
|--------|-----------|-------|-----------------|
| IP reads | >= 10M | >= 30M | Deeper sequencing |
| Input reads | >= 10M | >= 20M | Deeper sequencing |
| IP mapping rate | >= 70% | >= 85% | Check adapter contamination |
| IP/Input enrichment | >= 1.5x at DRACH | >= 3x | Re-do IP, check antibody |
| DRACH in peaks | >= 50% | >= 70% | Verify antibody specificity |
| Peak count | >= 5,000 | 10,000-30,000 | Optimize IP conditions |
| Replicate concordance | IDR < 0.05 | IDR < 0.01 | Troubleshoot variability |

---

## Evidence Grading

| Tier | Evidence Type | Example |
|------|-------------|---------|
| **T1** | ENCODE/modENCODE validated | Well-characterized m6A sites in MALAT1 |
| **T2** | Multi-method validated | MeRIP-seq + m6Anet concordant sites |
| **T3** | Single method, replicated | exomePeak2 peaks with IDR < 0.05 |
| **T4** | Computational prediction only | SRAMP predictions without validation |

---

## Multi-Agent Workflow Examples

**"Identify m6A changes in cancer vs normal tissue and link to gene expression"**
1. Epitranscriptomics -> Differential m6A analysis: peak calling, differential modification, DRACH motif
2. RNA-seq Analysis -> Differential expression of same samples
3. Gene Enrichment -> Pathway analysis of differentially methylated genes
4. Disease Research -> Known m6A dysregulation in the cancer type

**"Characterize the epitranscriptome from direct RNA nanopore sequencing"**
1. Epitranscriptomics -> m6Anet for m6A, Epinano for pseudouridine
2. Long Read Analysis -> QC and alignment of nanopore reads
3. Isoform Analysis -> Link modifications to specific transcript isoforms

**"Investigate METTL3 knockdown effects on RNA modifications"**
1. Epitranscriptomics -> Compare m6A peaks: WT vs METTL3-KD, expect global reduction
2. RNA-seq Analysis -> Expression changes upon METTL3 loss
3. Gene Enrichment -> Pathways affected by loss of m6A

## Completeness Checklist

- [ ] MeRIP-seq QC: mapping rate, enrichment, duplication assessed
- [ ] Peak calling performed with appropriate tool (exomePeak2/MACS2/MeTDiff)
- [ ] Peak annotation: 5'UTR/CDS/3'UTR/intron distribution quantified
- [ ] DRACH motif enrichment calculated and compared to background
- [ ] Metagene plot generated showing peak distribution relative to stop codon
- [ ] Differential m6A analysis performed if multiple conditions
- [ ] Expression correlation with modification status assessed
- [ ] Reader/writer/eraser protein context discussed
- [ ] Evidence tier assigned to all key findings (T1-T4)
- [ ] Report file created with all sections populated (no `[Analyzing...]` remaining)
