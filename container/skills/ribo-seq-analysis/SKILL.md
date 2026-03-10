---
name: ribo-seq-analysis
description: Ribosome profiling (Ribo-seq) analysis for translational regulation. Ribosome-protected fragments, translation efficiency, ORF discovery, ribosome stalling, P-site offset, triplet periodicity. Use when user mentions Ribo-seq, ribosome profiling, ribosome-protected fragments, RPF, translation efficiency, translational regulation, uORF, upstream ORF, ribosome occupancy, P-site, codon occupancy, translational control, polysome profiling, or ribosome footprinting.
---

# Ribo-seq Analysis

Production-ready ribosome profiling (Ribo-seq) analysis methodology. The agent writes and executes Python/R code for processing ribosome-protected fragments (RPFs), quality assessment of ribosome profiling data, translation efficiency calculation, ORF discovery (uORFs, dORFs, novel ORFs), ribosome pause site detection, and codon-resolution analysis. Uses Open Targets, PubMed, and pathway databases for biological annotation.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_ribo-seq-analysis_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Standard RNA-seq differential expression -> use `rnaseq-analysis`
- Proteomics (mass spectrometry) -> use `proteomics-analysis`
- RNA modifications (m6A effect on translation) -> use `epitranscriptomics`
- Single-cell transcriptomics -> use `single-cell-analysis`
- tRNA profiling / tRNA-seq -> use specialized pipeline

## Cross-Reference: Other Skills

- **RNA-seq expression for TE calculation** -> use rnaseq-analysis skill
- **m6A-mediated translational control** -> use epitranscriptomics skill
- **Pathway analysis of translationally regulated genes** -> use gene-enrichment skill
- **Time-course translational changes** -> use temporal-genomics skill

## Python Environment

Standard scientific Python: `numpy, pandas, scipy, matplotlib, seaborn, pysam, biopython`. For specialized tools, install at runtime: `subprocess.run(["pip", "install", "plastid"], check=True)`.

## Data Input Formats

```python
import pandas as pd
import numpy as np
import pysam
from collections import Counter

def load_ribo_data(ribo_bam, mrna_bam=None, gtf_path=None):
    """Load Ribo-seq and matched RNA-seq BAM files."""
    ribo_aln = pysam.AlignmentFile(ribo_bam, "rb")
    print(f"Ribo-seq reads: {ribo_aln.mapped:,}")

    if mrna_bam:
        mrna_aln = pysam.AlignmentFile(mrna_bam, "rb")
        print(f"RNA-seq reads: {mrna_aln.mapped:,}")
        return ribo_aln, mrna_aln

    return ribo_aln, None

def load_orf_predictions(orf_file, fmt="ribotish"):
    """Load ORF prediction results."""
    if fmt == "ribotish":
        df = pd.read_csv(orf_file, sep="\t")
    elif fmt == "orfrater":
        df = pd.read_csv(orf_file, sep="\t")
    elif fmt == "ribocode":
        df = pd.read_csv(orf_file, sep="\t")
    print(f"Loaded {len(df)} predicted ORFs")
    return df
```

---

## Analysis Pipeline

### Phase 1: Read Preprocessing

```python
def ribo_preprocessing(fastq_file, output_dir="ribo_processed"):
    """Ribo-seq read preprocessing pipeline."""
    cmds = f"""
    # Step 1: Adapter trimming (critical for short RPF reads)
    cutadapt \\
        -a AGATCGGAAGAGCACACGTCT \\
        --minimum-length 20 \\
        --maximum-length 35 \\
        -j 8 \\
        -o {output_dir}/trimmed.fastq.gz \\
        {fastq_file}

    # Step 2: rRNA removal (dominant contaminant in Ribo-seq)
    bowtie2 -x rRNA_index \\
        -U {output_dir}/trimmed.fastq.gz \\
        --un-gz {output_dir}/no_rRNA.fastq.gz \\
        -S /dev/null \\
        --no-unal \\
        -p 8
    # Typical rRNA content: 40-80% of raw reads
    # If rRNA > 90%, consider rRNA depletion optimization

    # Step 3: tRNA/snRNA/snoRNA removal (optional)
    bowtie2 -x ncRNA_index \\
        -U {output_dir}/no_rRNA.fastq.gz \\
        --un-gz {output_dir}/clean.fastq.gz \\
        -S /dev/null \\
        -p 8
    """

    print("Preprocessing QC Checkpoints:")
    print("  1. Raw reads: Minimum 20M for mammalian Ribo-seq")
    print("  2. After adapter trimming: Check size distribution")
    print("     Expected: Peak at 28-32 nt for RPFs")
    print("     If peak at 20-24 nt: Possible RNA degradation, not true RPFs")
    print("  3. rRNA removal: Expect 40-80% rRNA")
    print("     > 90% rRNA: Protocol issue, insufficient rRNA depletion")
    print("  4. Clean reads: Minimum 5M for quantification, 10M+ for ORF discovery")
    return cmds

def fragment_length_distribution(bam_file, output="frag_length_dist.png"):
    """Plot RPF fragment length distribution."""
    import matplotlib.pyplot as plt

    lengths = Counter()
    aln = pysam.AlignmentFile(bam_file, "rb")
    for read in aln.fetch():
        if not read.is_unmapped and not read.is_secondary:
            lengths[read.query_length] += 1
    aln.close()

    fig, ax = plt.subplots(figsize=(10, 5))
    x = sorted(lengths.keys())
    y = [lengths[k] for k in x]
    ax.bar(x, y, color="steelblue", edgecolor="white")
    ax.set_xlabel("Fragment Length (nt)")
    ax.set_ylabel("Read Count")
    ax.set_title("RPF Fragment Length Distribution")

    # Highlight expected RPF range
    ax.axvspan(28, 32, alpha=0.2, color="green", label="Expected RPF (28-32 nt)")
    ax.legend()
    plt.tight_layout()
    plt.savefig(output, dpi=150, bbox_inches="tight")
    plt.show()

    total = sum(y)
    rpf_range = sum(lengths[k] for k in range(28, 33))
    print(f"Reads in 28-32 nt range: {rpf_range:,} ({rpf_range/total:.1%})")
    print(f"Modal length: {max(lengths, key=lengths.get)} nt")
    return lengths
```

### Phase 2: Alignment

```python
def ribo_alignment(clean_fastq, genome_index, gtf, output_bam="ribo_aligned.bam"):
    """Align RPFs with STAR using Ribo-seq-specific parameters."""
    cmd = f"""
    STAR \\
        --runMode alignReads \\
        --genomeDir {genome_index} \\
        --readFilesIn {clean_fastq} \\
        --readFilesCommand zcat \\
        --outSAMtype BAM SortedByCoordinate \\
        --outFilterMultimapNmax 1 \\
        --outFilterMismatchNmax 2 \\
        --alignSJDBoverhangMin 1 \\
        --alignIntronMin 20 \\
        --alignIntronMax 1000000 \\
        --sjdbGTFfile {gtf} \\
        --outFileNamePrefix ribo_ \\
        --runThreadN 8 \\
        --outFilterType BySJout \\
        --quantMode GeneCounts

    # Index
    samtools index ribo_Aligned.sortedByCoord.out.bam
    """

    print("STAR Parameters for Ribo-seq:")
    print("  --outFilterMultimapNmax 1: Unique mappers only (critical for quantification)")
    print("  --outFilterMismatchNmax 2: Allow 2 mismatches (RPFs are short, 28-32 nt)")
    print("  --alignIntronMin 20: Allow spliced alignment")
    print("  Note: Short reads (28-32 nt) have lower mappability than RNA-seq (150 nt)")
    print("  Expected unique mapping rate: 50-80% (lower than RNA-seq)")
    return cmd
```

### Phase 3: Triplet Periodicity and P-site Calibration

```python
def triplet_periodicity_analysis(bam_file, gtf_path, output="periodicity.png"):
    """Validate 3-nt periodicity and calibrate P-site offset."""

    print("Triplet Periodicity (3-nt Periodicity):")
    print("=" * 50)
    print("  The hallmark of true ribosome footprints")
    print("  Ribosomes advance 3 nt per codon -> RPF 5' ends show 3-nt periodicity")
    print("  Periodicity should be visible relative to CDS start codon")
    print()

    def calculate_periodicity(bam_file, cds_starts, read_length=28):
        """Count RPF 5' end positions relative to CDS start codons."""
        frame_counts = Counter()  # frame 0, 1, 2
        aln = pysam.AlignmentFile(bam_file, "rb")
        for read in aln.fetch():
            if read.is_unmapped or read.is_secondary: continue
            if read.query_length != read_length: continue
            # Calculate position relative to nearest CDS start
            pos_5prime = read.reference_start if not read.is_reverse else read.reference_end
            # Frame assignment
            # frame_counts[pos_5prime % 3] += 1
        aln.close()
        return frame_counts

    print("P-site Offset Calibration:")
    print("  P-site = position of amino acid being incorporated")
    print("  Offset from RPF 5' end depends on fragment length:")
    print()
    print("  Fragment Length | Typical P-site Offset")
    print("  --------------|---------------------")
    print("  26 nt          | 12")
    print("  27 nt          | 12")
    print("  28 nt          | 12")
    print("  29 nt          | 12")
    print("  30 nt          | 12 or 13")
    print("  31 nt          | 13")
    print("  32 nt          | 13")
    print()
    print("  Calibration method:")
    print("  1. For each fragment length, plot 5' end distance from start codons")
    print("  2. The offset = distance from 5' end to the peak in frame 0")
    print("  3. Typically 12 nt for 28-29 nt fragments (standard for mammalian)")
    print()
    print("  Tools for automatic P-site calibration:")
    print("    plastid: psite command (Python)")
    print("    RiboWaltz: R package, automated offset detection")
    print("    ribosome: R package")

def periodicity_score(frame_counts):
    """Calculate periodicity score from frame counts."""
    total = sum(frame_counts.values())
    if total == 0: return 0
    f0 = frame_counts.get(0, 0) / total
    print(f"Frame distribution: F0={frame_counts.get(0,0)}, "
          f"F1={frame_counts.get(1,0)}, F2={frame_counts.get(2,0)}")
    print(f"Frame 0 fraction: {f0:.3f}")
    print(f"  > 0.5: Good periodicity")
    print(f"  > 0.6: Excellent periodicity")
    print(f"  < 0.4: Poor periodicity, check data quality")
    return f0
```

### Phase 4: Translation Efficiency

```python
def calculate_translation_efficiency(ribo_counts, mrna_counts, min_rpkm=1.0):
    """Calculate Translation Efficiency (TE = RPF RPKM / mRNA RPKM)."""

    print("Translation Efficiency Calculation:")
    print("=" * 50)
    print("  TE = RPF_RPKM / mRNA_RPKM")
    print("  Interpretation:")
    print("    TE > 1: Translationally up-regulated (more RPFs than expected from mRNA)")
    print("    TE = 1: Translation proportional to mRNA level")
    print("    TE < 1: Translationally down-regulated")
    print()

    # Merge Ribo-seq and RNA-seq counts
    merged = ribo_counts.merge(mrna_counts, on="gene_id", suffixes=("_ribo", "_mrna"))

    # Filter low-expression genes
    merged = merged[(merged["rpkm_ribo"] >= min_rpkm) & (merged["rpkm_mrna"] >= min_rpkm)]

    # Calculate TE
    merged["te"] = merged["rpkm_ribo"] / merged["rpkm_mrna"]
    merged["log2_te"] = np.log2(merged["te"])

    print(f"Genes with sufficient expression: {len(merged)}")
    print(f"Median TE: {merged['te'].median():.3f}")
    print(f"TE range: {merged['te'].min():.3f} - {merged['te'].max():.3f}")

    return merged

def differential_te(ribo_counts_c1, mrna_counts_c1,
                     ribo_counts_c2, mrna_counts_c2,
                     method="deseq2_interaction"):
    """Differential translation efficiency analysis."""

    if method == "deseq2_interaction":
        r_script = """
        library(DESeq2)

        # Combine RPF and mRNA counts into one matrix
        # Columns: RPF_cond1_rep1, RPF_cond1_rep2, ..., mRNA_cond1_rep1, ...
        countData <- cbind(rpf_counts, mrna_counts)

        # Design: interaction term captures TE changes
        colData <- data.frame(
            condition = factor(rep(c("control", "treated"), each = n_reps * 2)),
            assay = factor(rep(rep(c("RPF", "mRNA"), each = n_reps), 2)),
            row.names = colnames(countData)
        )

        dds <- DESeqDataSetFromMatrix(countData, colData, design = ~ condition + assay + condition:assay)
        dds <- DESeq(dds)

        # The interaction term (condition:assay) captures TE changes
        # Positive log2FC interaction = TE increased in treated
        res <- results(dds, name = "conditiontreated.assayRPF")
        """

        print("DESeq2 Interaction Model for Differential TE:")
        print("  Design: ~ condition + assay + condition:assay")
        print("  condition: biological condition (control vs treated)")
        print("  assay: data type (RPF vs mRNA)")
        print("  condition:assay: INTERACTION term = differential TE")
        print()
        print("  Interpretation of interaction term:")
        print("    log2FC > 0: TE increased in treated (translational up-regulation)")
        print("    log2FC < 0: TE decreased in treated (translational down-regulation)")
        print("    padj < 0.05: Statistically significant TE change")

    elif method == "riborex":
        print("Riborex: Dedicated differential TE tool")
        print("  Uses DESeq2/edgeR/Voom internally")
        print("  Input: RPF count matrix + mRNA count matrix + condition vector")
        print("  Advantage: Purpose-built, handles TE-specific statistics")
        r_script = """
        library(riborex)
        res <- riborex(mrna_counts, rpf_counts, condition,
                       engine = "DESeq2")
        """

    elif method == "xtail":
        print("Xtail: Alternative differential TE tool")
        print("  Tests for TE changes using probability distributions")
        print("  Provides separate p-values for mRNA, RPF, and TE changes")
        r_script = """
        library(xtail)
        res <- xtail(mrna_counts, rpf_counts, condition,
                     bins = 10000)
        """

    print()
    print("Method comparison:")
    print("  DESeq2 interaction: Most flexible, handles complex designs")
    print("  Riborex: Simpler interface, good for standard two-condition comparison")
    print("  Xtail: Decomposition of mRNA/RPF/TE changes, visualization tools")
    print("  Recommendation: DESeq2 interaction for complex designs, Riborex for simple")
    return r_script
```

### Phase 5: ORF Discovery

```python
def orf_discovery(ribo_bam, gtf, genome_fa, output_dir="orf_discovery"):
    """Discover novel translated ORFs from Ribo-seq data."""

    tools = {
        "RiboCode": f"""
        # RiboCode: statistical test for translated ORFs
        RiboCode_onestep \\
            -g {gtf} \\
            -r {ribo_bam} \\
            -f {genome_fa} \\
            -l no \\
            -o {output_dir}/ribocode
        # Uses Wilcoxon signed-rank test for 3-nt periodicity
        # Output: annotated ORFs with p-values
        """,

        "Ribo-TISH": f"""
        # Ribo-TISH: Translation Initiation Site Hunter
        ribo-tish predict \\
            -b {ribo_bam} \\
            -g {gtf} \\
            -f {genome_fa} \\
            --longest \\
            -o {output_dir}/ribotish_pred.txt
        # Tests multiple strategies: TIS hunting, frame testing
        # Good for uORF and alternative TIS detection
        """,

        "ORFquant": """
        # ORFquant: Quantifies ORF translation from Ribo-seq
        # R-based, integrates with DESeq2
        # Identifies and quantifies translated ORFs
        # Particularly good for isoform-level ORF annotation
        """,
    }

    print("ORF Types Detected:")
    print("=" * 50)
    print("  uORF: Upstream ORF (in 5'UTR)")
    print("    - Typically regulatory: represses main CDS translation")
    print("    - ~50% of human mRNAs have translated uORFs")
    print("    - Often < 100 codons")
    print("  dORF: Downstream ORF (in 3'UTR)")
    print("    - Less common, may produce functional micropeptides")
    print("  Internal ORF: Within CDS, different frame")
    print("    - Overlapping ORFs, dual-coding regions")
    print("  lncRNA ORFs: Small ORFs in annotated non-coding RNAs")
    print("    - Produce micropeptides/microproteins")
    print("    - Typically < 100 aa")
    print("  Extended/truncated CDS: Alternative start sites")
    print("    - N-terminal extensions or truncations")
    print()
    print("ORF Validation Criteria:")
    print("  1. 3-nt periodicity within ORF (primary evidence)")
    print("  2. RPF enrichment at start codon (translation initiation)")
    print("  3. Sufficient RPF coverage (>= 5 reads spanning ORF)")
    print("  4. AUG or near-cognate start codon (CUG, GUG, UUG)")
    print("  5. Conservation across species (PhyloCSF, CPC2)")
    print("  6. Mass spectrometry peptide evidence (strongest validation)")
    return tools
```

### Phase 6: Ribosome Stalling and Pause Sites

```python
def ribosome_pause_detection(bam_file, gtf, output="pause_sites.tsv"):
    """Detect ribosome pause/stall sites."""
    print("Ribosome Pause Site Detection:")
    print("=" * 50)
    print()
    print("Method: Identify positions with disproportionately high RPF density")
    print("  1. Calculate per-codon RPF density across each CDS")
    print("  2. Normalize to gene-level mean density")
    print("  3. Identify outliers: Z-score > 3 or density > 5x gene mean")
    print()
    print("Common causes of ribosome pausing:")
    print("  - Rare codons: Low cognate tRNA availability")
    print("  - Proline stretches: Poly-Pro (PPP) causes peptidyl transfer stalling")
    print("  - Signal recognition particle (SRP) binding")
    print("  - mRNA secondary structure downstream of ribosome")
    print("  - Amino acid starvation (specific codons depleted)")
    print("  - Cotranslational folding events")
    print()

    def detect_pauses(p_site_counts, gene_cds_length, z_threshold=3.0):
        """Identify pause sites from P-site counts per codon."""
        mean_density = np.mean(p_site_counts)
        std_density = np.std(p_site_counts)
        if std_density == 0: return []

        z_scores = (p_site_counts - mean_density) / std_density
        pauses = np.where(z_scores > z_threshold)[0]
        return [(pos, z_scores[pos], p_site_counts[pos]) for pos in pauses]

    print("Pause site visualization:")
    print("  1. Ribosome density profile along CDS (per-codon resolution)")
    print("  2. Metagene around pause sites (aggregate pattern)")
    print("  3. Codon identity at pause sites vs background")

def metagene_analysis(bam_file, gtf, region="start_codon", window=50,
                      output="metagene.png"):
    """Metagene analysis around start/stop codons."""
    import matplotlib.pyplot as plt

    print(f"Metagene Analysis: {region}")
    print("=" * 50)
    print()
    print("Expected patterns:")
    print("  Start codon metagene:")
    print("    - Sharp peak at start codon (AUG)")
    print("    - 3-nt periodicity visible downstream")
    print("    - Upstream: low RPF density (5'UTR, unless uORFs present)")
    print()
    print("  Stop codon metagene:")
    print("    - Peak at stop codon (ribosome pauses during termination)")
    print("    - Rapid drop-off after stop codon")
    print("    - Downstream: no RPFs (unless readthrough or dORFs)")
    print()

    # Generate metagene profile
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Start codon
    x = np.arange(-window, window + 1)
    # Simulated expected profile
    y_start = np.zeros(len(x))
    for i in range(window, len(x), 3):
        y_start[i] = np.random.exponential(5)
    y_start[window] = 15  # Peak at start codon
    axes[0].bar(x, y_start, width=1, color="steelblue")
    axes[0].axvline(0, color="red", linestyle="--", label="Start codon")
    axes[0].set_xlabel("Position relative to start codon (nt)")
    axes[0].set_ylabel("RPF density")
    axes[0].set_title("Start Codon Metagene")
    axes[0].legend()

    # Stop codon
    y_stop = np.zeros(len(x))
    for i in range(0, window, 3):
        y_stop[i] = np.random.exponential(5)
    y_stop[window] = 12  # Peak at stop codon
    axes[1].bar(x, y_stop, width=1, color="coral")
    axes[1].axvline(0, color="red", linestyle="--", label="Stop codon")
    axes[1].set_xlabel("Position relative to stop codon (nt)")
    axes[1].set_ylabel("RPF density")
    axes[1].set_title("Stop Codon Metagene")
    axes[1].legend()

    plt.tight_layout()
    plt.savefig(output, dpi=150, bbox_inches="tight")
    plt.show()
```

### Phase 7: A-site, P-site, E-site Assignment

```python
def ribosome_site_assignment():
    """Explain and implement A-site, P-site, E-site assignment."""
    print("Ribosome Site Assignment:")
    print("=" * 50)
    print()
    print("  Ribosome architecture (5' -> 3'):")
    print("  |----- E-site ----- P-site ----- A-site -----|")
    print("   Exit site      Peptidyl site   Aminoacyl site")
    print("   (tRNA exits)   (peptide bond)  (new tRNA enters)")
    print()
    print("  RPF coverage and site offsets:")
    print("  5'end ----[12 nt]---- P-site ----[3 nt]---- A-site")
    print()
    print("  For a 28-nt RPF:")
    print("    P-site = 5'end + 12 (codon being decoded)")
    print("    A-site = 5'end + 15 (incoming aminoacyl-tRNA)")
    print("    E-site = 5'end + 9  (exiting deacylated tRNA)")
    print()
    print("  Which site to use for analysis:")
    print("    P-site: Standard for most analyses (translation efficiency, pausing)")
    print("    A-site: Codon decoding rate, tRNA availability studies")
    print("    E-site: Rarely used, specialized studies only")
    print()

    def assign_psite(read_5prime, read_length, offset_table):
        """Assign P-site position from RPF 5' end."""
        offset = offset_table.get(read_length, 12)  # default 12
        return read_5prime + offset

    print("  Offset table (calibrate per experiment):")
    print("  Read length | P-site offset | A-site offset")
    print("  ------------|--------------|---------------")
    print("  26          | 12           | 15")
    print("  27          | 12           | 15")
    print("  28          | 12           | 15")
    print("  29          | 12           | 15")
    print("  30          | 13           | 16")
    print("  31          | 13           | 16")
    print("  32          | 13           | 16")
```

### Phase 8: Codon-Resolution Analysis

```python
def codon_occupancy_analysis(psite_counts_per_codon, codon_table):
    """Analyze ribosome occupancy at codon resolution."""
    print("Codon Occupancy Analysis:")
    print("=" * 50)
    print()
    print("  Codon occupancy = normalized RPF density per codon identity")
    print("  High occupancy = slow decoding (ribosome spends more time)")
    print("  Low occupancy = fast decoding")
    print()
    print("  Factors affecting decoding rate:")
    print("    1. tRNA abundance (major factor)")
    print("       - Codons with rare tRNAs: higher occupancy (slower)")
    print("       - Codons with abundant tRNAs: lower occupancy (faster)")
    print("    2. Wobble base pairing (less efficient)")
    print("    3. Codon context effects (neighboring codons)")
    print("    4. mRNA structure downstream of ribosome")
    print()

    def normalize_codon_counts(raw_counts, method="mean_gene"):
        """Normalize codon-level RPF counts."""
        if method == "mean_gene":
            # Normalize by gene-level mean to remove expression effects
            pass
        elif method == "total_codons":
            # Normalize by total codon usage frequency
            pass
        return raw_counts

    print("  Codon optimality and TE:")
    print("    CUB (Codon Usage Bias): Preference for optimal codons")
    print("    CAI (Codon Adaptation Index): Measure of codon optimality")
    print("    tAI (tRNA Adaptation Index): Based on tRNA gene copy numbers")
    print("    CSC (Codon Stabilization Coefficient): Codon effect on mRNA stability")

def quality_metrics_summary():
    """Summary of Ribo-seq quality metrics and thresholds."""
    print("Ribo-seq Quality Metrics:")
    print("=" * 50)
    metrics = {
        "Fragment length peak": ("28-32 nt", "Peak should be sharp, not broad"),
        "rRNA contamination": ("< 60%", "High rRNA indicates poor depletion"),
        "Unique mapping rate": ("> 50%", "Low rate = short reads, low complexity"),
        "CDS read fraction": ("> 60%", "Most RPFs should map to CDS"),
        "3-nt periodicity (Frame 0)": ("> 50%", "> 60% excellent, < 40% poor"),
        "Start codon peak": ("Visible", "Sharp peak at AUG = good initiation signal"),
        "5'UTR:CDS ratio": ("< 0.2", "High ratio suggests noise or abundant uORFs"),
        "Metagene uniformity": ("Flat CDS profile", "Large waves indicate bias"),
        "Correlation between replicates": ("r > 0.95", "Pearson on log RPF counts"),
    }
    print(f"\n  {'Metric':<35} {'Threshold':<15} {'Notes'}")
    print(f"  {'-'*35} {'-'*15} {'-'*35}")
    for metric, (threshold, note) in metrics.items():
        print(f"  {metric:<35} {threshold:<15} {note}")
```

---

## Parameter Reference Tables

### Differential TE Methods

| Method | Model | Replicates Required | Complex Designs | Best For |
|--------|-------|-------------------|-----------------|----------|
| DESeq2 interaction | NB GLM | >= 2 per condition | Yes (any formula) | Complex/multi-factor |
| Riborex | NB (DESeq2/edgeR) | >= 2 per condition | No | Simple two-condition |
| Xtail | Probability-based | >= 2 per condition | No | Decomposed TE changes |
| deltaTE | Simple ratio | >= 2 per condition | No | Quick exploration |
| Babel | Mixed model | >= 3 per condition | Limited | Protein vs mRNA comparison |

### ORF Discovery Tools

| Tool | Detection Method | Strengths | Limitations |
|------|-----------------|-----------|-------------|
| RiboCode | 3-nt periodicity test | Statistical rigor, handles noise | Requires good periodicity |
| Ribo-TISH | TIS + frame test | Sensitive TIS detection | May call false uORFs |
| ORFquant | Bayesian model | Isoform-aware, quantification | Computationally heavy |
| RibORF | Logistic regression | Machine learning-based | Needs training data |
| PRICE | Statistical model | Good for non-AUG starts | Less validated |

---

## Evidence Grading

| Tier | Evidence Type | Example |
|------|-------------|---------|
| **T1** | Ribo-seq + mass spec peptide validation | Novel ORF with detected peptide |
| **T2** | Ribo-seq with strong periodicity + conservation | uORF with PhyloCSF support |
| **T3** | Ribo-seq periodicity, single experiment | TE change with replicate support |
| **T4** | Low coverage or poor periodicity | Exploratory ORF from shallow data |

---

## Multi-Agent Workflow Examples

**"Identify translationally regulated genes under stress conditions"**
1. Ribo-seq Analysis -> Differential TE between stress and control using DESeq2 interaction
2. RNA-seq Analysis -> Matched RNA-seq for expression normalization
3. Gene Enrichment -> Pathway analysis of translationally up/down-regulated genes
4. Epitranscriptomics -> m6A changes driving translational regulation

**"Discover novel translated ORFs in lncRNAs"**
1. Ribo-seq Analysis -> ORF discovery with RiboCode + Ribo-TISH
2. Comparative Genomics -> PhyloCSF conservation of candidate ORFs
3. Proteomics -> Mass spec validation of predicted micropeptides

**"Investigate codon-level translational control during differentiation"**
1. Ribo-seq Analysis -> Codon occupancy analysis, tRNA adaptation index
2. Temporal Genomics -> Time-course TE changes during differentiation
3. Gene Enrichment -> Codon usage bias in differentially translated genes

## Completeness Checklist

- [ ] RPF fragment length distribution verified (peak at 28-32 nt)
- [ ] rRNA contamination rate assessed (< 60% expected)
- [ ] 3-nt periodicity validated (Frame 0 fraction > 50%)
- [ ] P-site offset calibrated for each fragment length
- [ ] CDS read enrichment confirmed (> 60% of mapped reads)
- [ ] Metagene profiles at start/stop codons generated
- [ ] Translation efficiency calculated if RNA-seq available
- [ ] Differential TE analysis if multiple conditions
- [ ] ORF discovery performed if requested (uORFs, novel ORFs)
- [ ] Quality metrics reported and interpreted
- [ ] Evidence tier assigned to all key findings (T1-T4)
- [ ] Report file created with all sections populated (no `[Analyzing...]` remaining)
