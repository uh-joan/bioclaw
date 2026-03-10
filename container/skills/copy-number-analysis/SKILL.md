---
name: copy-number-analysis
description: Copy number variant detection and analysis from sequencing and array data. CNVkit, GATK CNV, FACETS, Sequenza, ASCAT, GISTIC2, allele-specific copy number, ploidy estimation, purity estimation. Use when user mentions copy number, CNV, CNA, amplification, deletion, ploidy, purity, segmentation, LOH, loss of heterozygosity, allele-specific copy number, focal amplification, arm-level events, or copy number profiling.
---

# Copy Number Analysis

Production-ready copy number variant detection and analysis methodology. The agent writes and executes Python/R code for CNV detection from WGS, WES, and panel sequencing data, covering log2 ratio calculation, segmentation, allele-specific copy number, ploidy/purity estimation, recurrent CNA identification, and visualization. Uses Open Targets, PubMed, and cancer databases for biological annotation.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_copy-number-analysis_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- SNV/indel variant calling -> use `variant-calling`
- Structural variant detection (translocations, inversions) -> use `structural-variant-analysis`
- Somatic variant clinical interpretation -> use `cancer-variant-interpreter`
- Germline CNV in exome for rare disease -> use `rare-disease-diagnosis`
- Single-cell copy number (scDNA-seq) -> use `single-cell-analysis`

## Cross-Reference: Other Skills

- **Somatic variant interpretation** -> use cancer-variant-interpreter skill
- **Tumor mutational burden / microsatellite instability** -> use cancer-genomics skill
- **Structural variant calling** -> use structural-variant-analysis skill
- **Gene fusion detection** -> use fusion-detection skill

## Python/R Environment

Python: `numpy, pandas, scipy, matplotlib, seaborn, pysam`. R: `DNAcopy, GenomicRanges, ASCAT`. Install at runtime: `subprocess.run(["pip", "install", "cnvkit"], check=True)`.

## Data Input Formats

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def load_cnv_segments(seg_file, fmt="auto"):
    """Load CNV segmentation results from various tools."""
    if fmt == "auto":
        with open(seg_file, "r") as f:
            header = f.readline().strip().lower()
        if "log2" in header: fmt = "cnvkit"
        elif "segment_mean" in header: fmt = "gatk"
        elif "tcn" in header or "lcn" in header: fmt = "facets"
        else: fmt = "seg"  # CBS .seg format

    col_maps = {
        "cnvkit": {"chromosome": "chrom", "start": "start", "end": "end",
                   "log2": "log2ratio", "probes": "n_markers"},
        "gatk": {"CONTIG": "chrom", "START": "start", "END": "end",
                 "MEAN_LOG2_COPY_RATIO": "log2ratio", "NUM_POINTS_COPY_RATIO": "n_markers"},
        "facets": {"chrom": "chrom", "start": "start", "end": "end",
                   "cnlr.median": "log2ratio", "tcn.em": "total_cn", "lcn.em": "minor_cn"},
        "seg": {"chrom": "chrom", "loc.start": "start", "loc.end": "end",
                "seg.mean": "log2ratio", "num.mark": "n_markers"},
    }

    df = pd.read_csv(seg_file, sep="\t")
    df = df.rename(columns={k: v for k, v in col_maps.get(fmt, {}).items() if k in df.columns})
    df["width"] = df["end"] - df["start"]
    print(f"Loaded {len(df)} segments from {fmt} format")
    print(f"Chromosomes: {df['chrom'].nunique()}")
    return df
```

---

## Analysis Pipeline

### Phase 1: CNVkit Workflow

```python
def cnvkit_workflow(tumor_bam, normal_bam=None, targets_bed=None,
                    reference_fasta=None, output_dir="cnvkit_out"):
    """Complete CNVkit workflow for copy number analysis."""

    if normal_bam:
        # Paired tumor-normal mode (preferred)
        cmd = f"""
        # Step 1: Generate reference from normal sample
        cnvkit.py batch {tumor_bam} \\
            --normal {normal_bam} \\
            --targets {targets_bed} \\
            --fasta {reference_fasta} \\
            --output-reference {output_dir}/reference.cnn \\
            --output-dir {output_dir}/ \\
            --scatter --diagram

        # Steps performed automatically:
        # 1. target/antitarget bin creation
        # 2. Coverage calculation for target and antitarget bins
        # 3. Reference construction from normal
        # 4. Log2 ratio calculation (tumor/reference)
        # 5. CBS segmentation
        # 6. Call copy number states
        """
    else:
        # Tumor-only mode (uses flat reference or panel of normals)
        cmd = f"""
        # Tumor-only: use panel of normals if available
        cnvkit.py batch {tumor_bam} \\
            --normal \\
            --targets {targets_bed} \\
            --fasta {reference_fasta} \\
            --output-dir {output_dir}/ \\
            --scatter --diagram
        """

    print("CNVkit Key Concepts:")
    print("  Target bins: Regions covered by capture probes (exome/panel)")
    print("  Antitarget bins: Regions between targets (off-target reads)")
    print("    - Antitarget reads provide additional coverage signal")
    print("    - Larger bins (average 100kb) compensate for sparse off-target reads")
    print("    - Particularly valuable for WES data")
    print()
    print("  Log2 ratio interpretation:")
    print("    0.0 = diploid (2 copies)")
    print("    0.58 = 3 copies (single gain)")
    print("    1.0 = 4 copies (double gain)")
    print("    -1.0 = 1 copy (hemizygous loss)")
    print("    -inf = 0 copies (homozygous deletion)")
    print("    Note: Impurity dilutes signal (see purity adjustment below)")
    return cmd

def cnvkit_segmentation_tuning():
    """CNVkit segmentation parameter guidance."""
    print("Segmentation Methods in CNVkit:")
    print("=" * 50)
    print()
    print("CBS (Circular Binary Segmentation) - Default:")
    print("  cnvkit.py segment sample.cnr -m cbs")
    print("  - Standard, well-validated algorithm (DNAcopy)")
    print("  - Parameters: alpha (significance), undo.splits")
    print("  - alpha=0.01 (default): conservative, fewer segments")
    print("  - alpha=0.001: more sensitive, more segments")
    print()
    print("HMM (Hidden Markov Model):")
    print("  cnvkit.py segment sample.cnr -m hmm")
    print("  - Better for noisy data or low-purity samples")
    print("  - Can incorporate BAF (B-allele frequency) information")
    print()
    print("Segmentation QC:")
    print("  - Examine residuals: well-fit segments have small residuals")
    print("  - Check for over-segmentation: too many short segments = noise")
    print("  - Check for under-segmentation: missed breakpoints")
    print("  - Minimum segment size: typically >= 3 bins for WES")
```

### Phase 2: GATK CNV Workflow

```python
def gatk_cnv_workflow(tumor_bam, pon_hdf5=None, intervals_list=None,
                       normal_bams=None):
    """GATK best practices CNV workflow."""

    # Panel of Normals construction
    pon_cmds = """
    # === Build Panel of Normals (PoN) ===
    # Step 1: Collect read counts for each normal sample
    for NORMAL in normal1.bam normal2.bam normal3.bam ... ; do
        gatk CollectReadCounts \\
            -I $NORMAL \\
            -L intervals.interval_list \\
            --interval-merging-rule OVERLAPPING_ONLY \\
            -O ${NORMAL%.bam}.counts.hdf5
    done

    # Step 2: Create PoN from normal counts
    gatk CreateReadCountPanelOfNormals \\
        -I normal1.counts.hdf5 \\
        -I normal2.counts.hdf5 \\
        -I normal3.counts.hdf5 \\
        -O pon.hdf5

    # Recommendation: >= 30 normals for robust PoN
    # Match: same capture kit, same sequencing platform, similar depth
    """

    # Tumor analysis
    tumor_cmds = f"""
    # === Tumor CNV Analysis ===
    # Step 1: Collect read counts
    gatk CollectReadCounts \\
        -I {tumor_bam} \\
        -L {intervals_list} \\
        --interval-merging-rule OVERLAPPING_ONLY \\
        -O tumor.counts.hdf5

    # Step 2: Denoise using PoN
    gatk DenoiseReadCounts \\
        -I tumor.counts.hdf5 \\
        --count-panel-of-normals {pon_hdf5 or 'pon.hdf5'} \\
        --standardized-copy-ratios tumor.standardized.tsv \\
        --denoised-copy-ratios tumor.denoised.tsv

    # Step 3: Collect allelic counts (for allele-specific CN)
    gatk CollectAllelicCounts \\
        -I {tumor_bam} \\
        -R reference.fa \\
        -L common_snps.interval_list \\
        -O tumor.allelicCounts.tsv

    # Step 4: Model segments
    gatk ModelSegments \\
        --denoised-copy-ratios tumor.denoised.tsv \\
        --allelic-counts tumor.allelicCounts.tsv \\
        --output tumor_segments/ \\
        --output-prefix tumor

    # Step 5: Call copy number
    gatk CallCopyRatioSegments \\
        -I tumor_segments/tumor.cr.seg \\
        -O tumor_segments/tumor.called.seg
    """

    print("GATK CNV vs CNVkit:")
    print("  GATK: Better PoN handling, integrated with GATK ecosystem")
    print("  CNVkit: Better off-target utilization, simpler setup")
    print("  Both: Use CBS segmentation, support tumor-only mode")
    return pon_cmds, tumor_cmds
```

### Phase 3: Allele-Specific Copy Number

```python
def facets_analysis(tumor_bam, normal_bam, output_dir="facets_out"):
    """FACETS: allele-specific copy number with purity/ploidy estimation."""
    r_script = """
    library(facets)

    # Step 1: Generate pileup (SNP counts)
    # snp-pileup -g -q15 -Q20 -P100 -r25,0 \\
    #   dbsnp.vcf.gz normal.bam tumor.bam pileup.csv.gz

    # Step 2: Run FACETS
    pileup <- readSnpMatrix("pileup.csv.gz")
    xx <- preProcSample(pileup,
                        ndepth = 25,       # min normal depth
                        snp.nbhd = 250,    # SNP neighborhood size
                        cval = 150,        # critical value for segmentation
                        gbuild = "hg38")

    # Step 3: Process sample
    oo <- procSample(xx,
                     cval = 300,           # critical value for joining segments
                     min.nhet = 15)        # min het SNPs per segment

    # Step 4: Estimate purity and ploidy
    fit <- emcncf(oo)

    cat(sprintf("Purity: %.2f\\n", fit$purity))
    cat(sprintf("Ploidy: %.2f\\n", fit$ploidy))

    # Key outputs:
    # tcn.em = total copy number (estimated by EM)
    # lcn.em = lesser (minor) copy number
    # cf.em  = cellular fraction of the aberration
    """

    print("FACETS Key Outputs:")
    print("  tcn (total CN): Sum of major + minor allele copies")
    print("  lcn (minor CN): Copies of lesser allele")
    print("  Major CN = tcn - lcn")
    print()
    print("  Interpretation examples:")
    print("    tcn=2, lcn=1: Diploid, normal (AB)")
    print("    tcn=3, lcn=1: Gain (AAB or ABB)")
    print("    tcn=2, lcn=0: Copy-neutral LOH (AA)")
    print("    tcn=1, lcn=0: Hemizygous deletion (A)")
    print("    tcn=0, lcn=0: Homozygous deletion")
    print("    tcn=4, lcn=2: Tetraploid (AABB) or WGD")
    print()
    print("  cval tuning (critical value for segmentation):")
    print("    cval=100-150: High sensitivity (more segments, may over-segment)")
    print("    cval=200-300: Balanced (recommended default)")
    print("    cval=400-500: Conservative (fewer segments, may miss small events)")
    return r_script

def sequenza_analysis(tumor_bam, normal_bam):
    """Sequenza: allele-specific copy number with purity/ploidy grid search."""
    r_script = """
    library(sequenza)

    # Step 1: Process BAMs (create seqz file)
    # sequenza-utils bam2seqz -n normal.bam -t tumor.bam \\
    #   --fasta reference.fa -gc gc50Base.wig.gz -o tumor.seqz.gz

    # Step 2: Bin the seqz file
    # sequenza-utils seqz_binning --seqz tumor.seqz.gz -w 50 -o tumor.small.seqz.gz

    # Step 3: Load and analyze in R
    seqz <- sequenza.extract("tumor.small.seqz.gz")

    # Step 4: Fit cellularity and ploidy
    CP <- sequenza.fit(seqz)
    # Grid search over cellularity (0-1) and ploidy (1.5-6)

    # Step 5: Extract results at best cellularity/ploidy
    sequenza.results(
        sequenza.extract = seqz,
        cp.table = CP,
        sample.id = "tumor",
        out.dir = "sequenza_results/"
    )
    """

    print("Sequenza vs FACETS vs ASCAT:")
    print("  Sequenza: Grid search purity/ploidy, good visualization")
    print("  FACETS: EM-based estimation, handles low-purity better")
    print("  ASCAT: SNP array or WGS, GC/replication timing correction")
    print("  Recommendation: Run >= 2 tools and compare purity/ploidy estimates")
    return r_script
```

### Phase 4: Ploidy and Purity Estimation

```python
def purity_ploidy_interpretation(purity, ploidy):
    """Interpret tumor purity and ploidy estimates."""
    print(f"Estimated Purity: {purity:.2f}")
    print(f"Estimated Ploidy: {ploidy:.2f}")
    print()

    # Expected log2 ratios given purity and ploidy
    def expected_log2(cn, purity, ploidy):
        """Calculate expected log2 ratio for a given copy number state."""
        # log2((purity * cn + (1-purity) * 2) / (purity * ploidy + (1-purity) * 2))
        tumor_signal = purity * cn + (1 - purity) * 2
        expected_diploid = purity * ploidy + (1 - purity) * 2
        return np.log2(tumor_signal / expected_diploid)

    print("Expected log2 ratios (purity-adjusted):")
    print(f"  {'CN':>4} | {'log2 ratio':>10} | {'Status'}")
    print(f"  {'-'*4}-+-{'-'*10}-+-{'-'*20}")
    for cn in [0, 1, 2, 3, 4, 5, 6, 8]:
        l2 = expected_log2(cn, purity, ploidy)
        status = {0: "HomDel", 1: "HetLoss", 2: "Diploid", 3: "Gain",
                  4: "Amp", 5: "Amp", 6: "HighAmp", 8: "HighAmp"}.get(cn, "")
        print(f"  {cn:>4} | {l2:>10.3f} | {status}")

    print()
    print("Purity considerations:")
    if purity < 0.2:
        print("  WARNING: Very low purity (<20%). CNV calls may be unreliable.")
        print("  Consider: tumor enrichment, microdissection, or computational deconvolution.")
    elif purity < 0.4:
        print("  Low purity (20-40%). Use tools robust to low purity (FACETS, ASCAT).")
        print("  Amplifications detectable; deletions may be missed.")
    elif purity < 0.7:
        print("  Moderate purity (40-70%). Most CNV tools perform well.")
    else:
        print("  High purity (>70%). All tools should work well.")

    print()
    print("Ploidy considerations:")
    if ploidy > 2.8:
        print(f"  Ploidy {ploidy:.1f}: Likely whole-genome duplication (WGD) event.")
        print("  Near-tetraploid tumors common in: breast, ovarian, serous cancers.")
        print("  Adjust CN thresholds: 'neutral' = ploidy, not 2.")
    elif ploidy < 1.8:
        print(f"  Ploidy {ploidy:.1f}: Near-haploid. Rare but seen in some ALL subtypes.")
```

### Phase 5: Focal vs Arm-Level Events

```python
def classify_events(segments_df, arm_threshold=0.5, focal_max=3e6):
    """Classify CNV events as focal, arm-level, or chromosomal."""
    # Chromosome arm lengths (hg38, approximate)
    arm_lengths = {
        "1p": 121.5e6, "1q": 127.5e6, "2p": 93.4e6, "2q": 149.7e6,
        "3p": 90.5e6, "3q": 107.7e6, "4p": 50.1e6, "4q": 140.6e6,
        "5p": 48.8e6, "5q": 132.4e6, "6p": 58.6e6, "6q": 112.5e6,
        "7p": 60.1e6, "7q": 99.2e6, "8p": 45.0e6, "8q": 101.6e6,
        "9p": 43.4e6, "9q": 98.1e6, "10p": 39.8e6, "10q": 95.2e6,
        "11p": 51.1e6, "11q": 84.2e6, "12p": 35.5e6, "12q": 97.5e6,
        "13q": 97.0e6, "14q": 88.3e6, "15q": 84.0e6, "16p": 36.5e6,
        "16q": 54.0e6, "17p": 25.1e6, "17q": 58.5e6, "18p": 18.5e6,
        "18q": 59.5e6, "19p": 26.2e6, "19q": 32.7e6, "20p": 28.5e6,
        "20q": 35.5e6, "21q": 34.2e6, "22q": 35.7e6,
    }

    for idx, seg in segments_df.iterrows():
        width = seg["end"] - seg["start"]
        if width <= focal_max:
            segments_df.at[idx, "event_type"] = "focal"
        elif width > focal_max:
            segments_df.at[idx, "event_type"] = "arm-level"

    print("Event Classification:")
    print(f"  Focal events (<= {focal_max/1e6:.0f} Mb): {(segments_df['event_type']=='focal').sum()}")
    print(f"  Arm-level events: {(segments_df['event_type']=='arm-level').sum()}")
    print()
    print("Clinically significant focal events to check:")
    print("  Amplifications: ERBB2 (17q12), MYC (8q24), EGFR (7p11), CCND1 (11q13)")
    print("  Deletions: CDKN2A/B (9p21), RB1 (13q14), PTEN (10q23), TP53 (17p13)")
    return segments_df

def cnv_annotation(segments_df, gene_bed):
    """Annotate CNV segments with overlapping genes and dosage sensitivity."""
    print("Dosage Sensitivity Scores:")
    print("  pHaplo: Probability of haploinsufficiency (loss sensitivity)")
    print("    > 0.86 = likely haploinsufficient (ClinGen calibrated)")
    print("  pTriplo: Probability of triplosensitivity (gain sensitivity)")
    print("    > 0.94 = likely triplosensitive")
    print()
    print("Key databases for CNV interpretation:")
    print("  ClinGen Dosage Sensitivity Map: curated gene-level scores")
    print("  DECIPHER: developmental disorder CNVs")
    print("  DGV (Database of Genomic Variants): population CNV frequency")
    print("  gnomAD SV: structural variant population frequencies")
    print("  COSMIC: cancer-associated copy number changes")
    return segments_df
```

### Phase 6: GISTIC2.0 for Recurrent CNAs

```python
def gistic2_analysis(seg_file, markers_file, output_dir="gistic2_out"):
    """GISTIC2.0: identify recurrent CNAs across a cohort."""
    cmd = f"""
    gistic2 \\
        -b {output_dir} \\
        -seg {seg_file} \\
        -mk {markers_file} \\
        -refgene hg38.mat \\
        -genegistic 1 \\
        -smallmem 1 \\
        -broad 1 \\
        -brlen 0.5 \\
        -conf 0.90 \\
        -armpeel 1 \\
        -savegene 1 \\
        -gcm extreme \\
        -ta 0.1 \\
        -td 0.1 \\
        -js 4 \\
        -qvt 0.25 \\
        -rx 0
    """

    print("GISTIC2.0 Key Parameters:")
    print("=" * 50)
    print(f"  -ta 0.1: Amplification threshold (log2 ratio >= 0.1)")
    print(f"  -td 0.1: Deletion threshold (log2 ratio <= -0.1)")
    print(f"  -qvt 0.25: q-value threshold for significance")
    print(f"  -conf 0.90: Confidence level for wide peak boundaries")
    print(f"  -broad 1: Enable broad (arm-level) analysis")
    print(f"  -brlen 0.5: Broad event length threshold (fraction of arm)")
    print(f"  -js 4: Join segment size (merge nearby segments)")
    print()
    print("GISTIC2.0 Outputs:")
    print("  all_lesions.conf_90.txt: All significant regions (focal + broad)")
    print("  amp_genes.conf_90.txt: Genes in amplified peaks")
    print("  del_genes.conf_90.txt: Genes in deleted peaks")
    print("  scores.gistic: Per-marker G-scores and q-values")
    print("  broad_significance_results.txt: Arm-level events")
    print()
    print("Minimum cohort size: >= 25 samples for reliable recurrence calls")
    print("Ideal: >= 50-100 samples for robust GISTIC analysis")
    return cmd
```

### Phase 7: Visualization

```python
def genome_wide_cn_plot(segments_df, output="cnv_genome_plot.png"):
    """Genome-wide copy number plot with chromosome ideograms."""
    chrom_order = [f"chr{i}" for i in range(1, 23)] + ["chrX", "chrY"]
    chrom_lengths = {
        "chr1": 248.9e6, "chr2": 242.2e6, "chr3": 198.3e6, "chr4": 190.2e6,
        "chr5": 181.5e6, "chr6": 170.8e6, "chr7": 159.3e6, "chr8": 145.1e6,
        "chr9": 138.4e6, "chr10": 133.8e6, "chr11": 135.1e6, "chr12": 133.3e6,
        "chr13": 114.4e6, "chr14": 107.0e6, "chr15": 101.9e6, "chr16": 90.3e6,
        "chr17": 83.3e6, "chr18": 80.4e6, "chr19": 58.6e6, "chr20": 64.4e6,
        "chr21": 46.7e6, "chr22": 50.8e6, "chrX": 156.0e6, "chrY": 57.2e6,
    }

    # Calculate cumulative positions
    cum_offset = {}
    offset = 0
    for chrom in chrom_order:
        cum_offset[chrom] = offset
        offset += chrom_lengths.get(chrom, 0)

    fig, ax = plt.subplots(figsize=(20, 5))

    # Plot segments
    for _, seg in segments_df.iterrows():
        chrom = seg["chrom"] if seg["chrom"].startswith("chr") else f"chr{seg['chrom']}"
        if chrom not in cum_offset: continue
        x_start = cum_offset[chrom] + seg["start"]
        x_end = cum_offset[chrom] + seg["end"]
        l2 = seg["log2ratio"]

        color = "red" if l2 > 0.2 else ("blue" if l2 < -0.2 else "gray")
        ax.plot([x_start, x_end], [l2, l2], color=color, linewidth=2, solid_capstyle="butt")

    # Chromosome boundaries
    for chrom in chrom_order:
        if chrom in cum_offset:
            ax.axvline(cum_offset[chrom], color="lightgray", linewidth=0.5)

    # Labels
    tick_pos = [cum_offset[c] + chrom_lengths.get(c, 0)/2 for c in chrom_order if c in cum_offset]
    tick_labels = [c.replace("chr", "") for c in chrom_order if c in cum_offset]
    ax.set_xticks(tick_pos)
    ax.set_xticklabels(tick_labels, fontsize=8)

    ax.axhline(0, color="black", linewidth=0.5)
    ax.axhline(0.58, color="red", linewidth=0.5, linestyle="--", alpha=0.3)
    ax.axhline(-1.0, color="blue", linewidth=0.5, linestyle="--", alpha=0.3)
    ax.set_ylabel("Log2 Ratio")
    ax.set_title("Genome-Wide Copy Number Profile")
    ax.set_ylim(-3, 3)

    plt.tight_layout()
    plt.savefig(output, dpi=150, bbox_inches="tight")
    plt.show()

def cn_heatmap_cohort(samples_segments, sample_names, output="cn_heatmap.png"):
    """Copy number heatmap across a cohort (samples x genomic position)."""
    # Bin genome into fixed windows
    bin_size = 1_000_000  # 1 Mb bins
    print("Generating cohort CN heatmap:")
    print(f"  Bin size: {bin_size/1e6:.0f} Mb")
    print(f"  Samples: {len(sample_names)}")
    print("  Color scale: blue (loss) - white (neutral) - red (gain)")
    print("  Cluster samples by CN profile similarity (Ward linkage)")

def allele_specific_plot(segments_df, output="allele_specific_cn.png"):
    """Plot allele-specific copy number (total CN + minor CN)."""
    if "total_cn" not in segments_df.columns or "minor_cn" not in segments_df.columns:
        print("Allele-specific CN requires FACETS, Sequenza, or ASCAT output")
        return

    fig, axes = plt.subplots(2, 1, figsize=(20, 8), sharex=True)

    # Total copy number
    axes[0].set_ylabel("Total CN")
    axes[0].set_title("Allele-Specific Copy Number")
    axes[0].axhline(2, color="gray", linestyle="--")

    # Minor allele copy number (LOH when = 0)
    axes[1].set_ylabel("Minor CN")
    axes[1].set_xlabel("Genomic Position")
    axes[1].axhline(0, color="red", linestyle="--", alpha=0.5, label="LOH")
    axes[1].legend()

    plt.tight_layout()
    plt.savefig(output, dpi=150, bbox_inches="tight")
    plt.show()
```

### Phase 8: Array-Based CNV Detection

```python
def array_cnv_analysis():
    """CNV detection from SNP arrays and array CGH."""
    print("Array-Based CNV Detection:")
    print("=" * 50)
    print()
    print("SNP Arrays (Illumina, Affymetrix):")
    print("  PennCNV:")
    print("    - HMM-based, uses LRR (Log R Ratio) and BAF (B Allele Freq)")
    print("    - detect_cnv.pl -test sample.txt -hmm hh550.hmm -pfb hh550.pfb")
    print("    - Strengths: Well-validated, handles mosaicism")
    print("    - QC: LRR_SD < 0.35, |WF| < 0.05, BAF_drift < 0.01")
    print()
    print("  QuantiSNP:")
    print("    - Objective Bayes HMM")
    print("    - Better for low-level mosaicism than PennCNV")
    print("    - MaxCopyNumber: default 4 (increase for cancer)")
    print()
    print("Array CGH:")
    print("    - Uses DNAcopy (CBS) for segmentation")
    print("    - GLAD: adaptive weights for different array densities")
    print()
    print("WGS vs WES vs Panel for CNV detection:")
    print("  WGS: Best resolution, uniform coverage, detects all sizes")
    print("  WES: Good for focal events in exonic regions, needs PoN")
    print("  Panel: Limited to targeted regions, focal events only")
    print("  SNP array: Genome-wide, cost-effective, limited resolution (~50kb)")
```

---

## Parameter Reference Tables

### Tool Comparison

| Feature | CNVkit | GATK CNV | FACETS | Sequenza | ASCAT |
|---------|--------|----------|--------|----------|-------|
| **Input** | BAM | BAM | Pileup | BAM/seqz | BAM/array |
| **Paired mode** | Yes | Yes | Yes | Yes | Yes |
| **Tumor-only** | Yes | Yes (PoN) | No | No | No |
| **Allele-specific** | Limited | Yes | Yes | Yes | Yes |
| **Purity/ploidy** | Manual | No | EM | Grid search | ASPCF |
| **Off-target reads** | Yes | No | No | No | No |
| **Best for** | WES | WES/WGS | WES | WES/WGS | Array/WGS |

### CNV Call Thresholds

| Copy Number State | Log2 Ratio (pure) | Log2 Ratio (50% purity) | Clinical Significance |
|-------------------|-------------------|------------------------|----------------------|
| Homozygous deletion (0) | -inf | -1.0 | Loss of function |
| Hemizygous loss (1) | -1.0 | -0.42 | Haploinsufficiency |
| Diploid (2) | 0.0 | 0.0 | Normal |
| Single gain (3) | 0.58 | 0.22 | Possible oncogene activation |
| Amplification (4) | 1.0 | 0.42 | Likely oncogene activation |
| High amplification (>=6) | >= 1.58 | >= 0.74 | Therapeutic target (e.g., ERBB2) |

---

## Evidence Grading

| Tier | Evidence Type | Example |
|------|-------------|---------|
| **T1** | Clinically validated | ERBB2 amplification for trastuzumab eligibility |
| **T2** | Guideline-supported | 1p/19q co-deletion in oligodendroglioma |
| **T3** | Published cohort studies | GISTIC peaks from TCGA pan-cancer |
| **T4** | Novel/exploratory | Patient-specific focal events |

---

## Multi-Agent Workflow Examples

**"Characterize copy number landscape of a tumor sample"**
1. Copy Number Analysis -> CNVkit or GATK CNV, segmentation, purity/ploidy estimation
2. Cancer Variant Interpreter -> Interpret focal amplifications/deletions (actionable targets)
3. Structural Variant Analysis -> Complement with SV calls (breakpoint resolution)

**"Identify recurrent CNAs across a cancer cohort and compare to TCGA"**
1. Copy Number Analysis -> Per-sample CNV calling, GISTIC2.0 for recurrence
2. Gene Enrichment -> Pathway analysis of genes in recurrent CNA regions
3. Disease Research -> Compare to published TCGA landscape for the cancer type

**"Assess tumor purity and ploidy for accurate variant calling"**
1. Copy Number Analysis -> FACETS/Sequenza for purity and ploidy estimation
2. Variant Calling -> Use purity/ploidy to adjust variant allele frequency expectations
3. Cancer Variant Interpreter -> Clonality assessment using CN-adjusted VAFs

## Completeness Checklist

- [ ] Appropriate tool selected for data type (WGS/WES/panel/array)
- [ ] Tumor-normal paired or panel of normals used (if available)
- [ ] Log2 ratios calculated and segmentation performed
- [ ] Purity and ploidy estimated (FACETS, Sequenza, or ASCAT)
- [ ] Allele-specific copy number assessed (LOH, cn-LOH)
- [ ] Events classified: focal vs arm-level
- [ ] Clinically relevant CNVs annotated (ERBB2, MYC, CDKN2A, etc.)
- [ ] Genome-wide CN plot generated
- [ ] GISTIC2.0 run if cohort analysis (>= 25 samples)
- [ ] Evidence tier assigned to all key findings (T1-T4)
- [ ] Report file created with all sections populated (no `[Analyzing...]` remaining)
