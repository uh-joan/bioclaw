---
name: alternative-splicing
description: Alternative splicing and isoform analysis specialist. Differential splicing event detection, PSI quantification, isoform switching, sashimi plot visualization. Use when user mentions alternative splicing, splicing analysis, exon skipping, skipped exon, SE, A5SS, A3SS, MXE, mutually exclusive exons, retained intron, RI, rMATS, SUPPA2, Leafcutter, PSI, percent spliced in, delta PSI, sashimi plot, isoform switching, IsoformSwitchAnalyzeR, splice site, splicing factor, RNA-binding protein, eCLIP, CLIP-seq, splicing regulatory elements, ESE, ESS, ISE, ISS, MaxEntScan, splice site strength, junction saturation, NMD, nonsense-mediated decay, RNA velocity, scVelo, aberrant splicing, splice-site variant, or cryptic splice site.
---

# Alternative Splicing and Isoform Analysis

Comprehensive pipeline for detecting and characterizing alternative splicing events from RNA-seq data. Covers event-level analysis (rMATS, SUPPA2, Leafcutter), isoform switching (IsoformSwitchAnalyzeR), visualization (sashimi plots), single-cell splicing, and clinical interpretation of splicing variants.

## Report-First Workflow

1. **Create report file immediately**: `[sample]_splicing_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as analysis proceeds
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill
- Differential gene expression (not splicing) -> use RNA-seq skill
- Long-read isoform discovery (ONT/PacBio) -> use long-read-sequencing skill
- Variant calling at splice sites -> use variant calling skill first, then this skill
- Single-cell clustering and cell-type annotation -> use single-cell-analysis skill
- Methylation at splicing regulators -> use methylation-analysis skill

## Cross-Reference: Other Skills
- **Expression quantification** -> use RNA-seq skill for read alignment and gene/transcript TPM
- **Long-read isoform validation** -> use long-read-sequencing skill for full-length transcripts
- **Splicing-derived neoantigens** -> use immunoinformatics skill for MHC binding prediction
- **Methylation at splice regulators** -> use methylation-analysis skill
- **Chromatin at alternative exons** -> use hic-analysis skill for 3D context

---

## Splicing Event Types

### Classification of Alternative Splicing Events

| Event | Abbreviation | Description | Frequency |
|-------|-------------|-------------|-----------|
| **Skipped Exon** | SE | Cassette exon included or excluded | Most common (~40%) |
| **Alternative 5' Splice Site** | A5SS | Two or more 5' splice sites for same exon | ~8% |
| **Alternative 3' Splice Site** | A3SS | Two or more 3' splice sites for same exon | ~8% |
| **Mutually Exclusive Exons** | MXE | One of two exons included, never both | ~5% |
| **Retained Intron** | RI | Intron retained in mature mRNA | ~5% (higher in plants) |
| **Alternative First Exon** | AFE | Different transcription start sites | ~15% |
| **Alternative Last Exon** | ALE | Different 3' ends / polyadenylation | ~10% |
| **Complex** | CE | Combination of multiple events | ~10% |

### PSI (Percent Spliced In) Definition

```
PSI (Ψ) = inclusion reads / (inclusion reads + exclusion reads)

For Skipped Exon (SE):
  PSI = (reads supporting inclusion) / (inclusion + exclusion reads)
  PSI = 1.0 → exon always included
  PSI = 0.0 → exon always skipped
  PSI = 0.5 → exon included in 50% of transcripts

ΔPSI = PSI(condition2) - PSI(condition1)
  ΔPSI > 0: increased inclusion in condition2
  ΔPSI < 0: increased skipping in condition2
  |ΔPSI| > 0.1 (10%): commonly used significance threshold
```

---

## Phase 1: Input Requirements

### RNA-seq Data Preparation

```
Required:
- RNA-seq BAM files (STAR-aligned recommended for junction reads)
- Genome annotation (GTF/GFF3)
- ≥2 biological replicates per condition (≥3 recommended)

Alignment considerations:
- STAR: recommended for splicing analysis (2-pass mode for novel junctions)
- HISAT2: acceptable alternative
- Do NOT use TopHat2 (deprecated) or simple aligners (BWA)

Minimum requirements:
- Read length: ≥75 bp (100-150 bp preferred for junction spanning)
- Depth: ≥30M reads per sample (≥50M for comprehensive splicing)
- Paired-end: strongly recommended (better junction evidence)
```

### STAR Alignment for Splicing

```bash
# STAR 2-pass alignment optimized for splicing detection
# Pass 1: discover novel junctions
STAR --runMode alignReads \
  --genomeDir star_index/ \
  --readFilesIn R1.fastq.gz R2.fastq.gz \
  --readFilesCommand zcat \
  --outSAMtype BAM SortedByCoordinate \
  --outSAMstrandField intronMotif \
  --outSJfilterReads All \
  --twopassMode Basic \
  --outFilterType BySJout \
  --outFilterMultimapNmax 20 \
  --outFilterMismatchNmax 999 \
  --outFilterMismatchNoverReadLmax 0.04 \
  --alignIntronMin 20 \
  --alignIntronMax 1000000 \
  --alignMatesGapMax 1000000 \
  --alignSJoverhangMin 8 \
  --alignSJDBoverhangMin 1 \
  --sjdbScore 1 \
  --runThreadN 16 \
  --outFileNamePrefix sample_

# Key output for splicing:
# sample_Aligned.sortedByCoord.out.bam — aligned reads
# sample_SJ.out.tab — splice junctions discovered
# sample_Log.final.out — alignment statistics
```

---

## Phase 2: Event-Level Analysis with rMATS

### rMATS (Replicate MATS)

```bash
# rMATS: gold standard for differential splicing event detection
# Requires: BAM files, GTF annotation

# Prepare BAM file lists (comma-separated per condition)
echo "ctrl1.bam,ctrl2.bam,ctrl3.bam" > b1.txt
echo "treat1.bam,treat2.bam,treat3.bam" > b2.txt

# Run rMATS
rmats.py \
  --b1 b1.txt \
  --b2 b2.txt \
  --gtf annotation.gtf \
  --od rmats_output/ \
  --tmp rmats_tmp/ \
  -t paired \
  --readLength 150 \
  --nthread 16 \
  --tstat 8 \
  --cstat 0.0001 \
  --libType fr-unstranded \
  --variable-read-length \
  --novelSS \
  --mil 50 \
  --mel 500

# Key parameters:
# -t paired: paired-end reads
# --readLength: read length
# --novelSS: allow novel splice sites (not just annotated)
# --mil/--mel: minimum/maximum exon length
# --cstat: FDR cutoff for counting (default 0.0001)
# --variable-read-length: handle variable read lengths
```

### rMATS Output Files

| File | Content | Use |
|------|---------|-----|
| `SE.MATS.JC.txt` | Skipped exon — junction counts only | Stringent analysis |
| `SE.MATS.JCEC.txt` | Skipped exon — junction + exon counts | Higher sensitivity |
| `A5SS.MATS.JC.txt` | Alternative 5' splice site — JC | |
| `A5SS.MATS.JCEC.txt` | Alternative 5' splice site — JCEC | |
| `A3SS.MATS.JC.txt` | Alternative 3' splice site — JC | |
| `A3SS.MATS.JCEC.txt` | Alternative 3' splice site — JCEC | |
| `MXE.MATS.JC.txt` | Mutually exclusive exons — JC | |
| `MXE.MATS.JCEC.txt` | Mutually exclusive exons — JCEC | |
| `RI.MATS.JC.txt` | Retained intron — JC | |
| `RI.MATS.JCEC.txt` | Retained intron — JCEC | |

### JC vs JCEC Counts

```
JC (Junction Counts only):
- Uses only reads spanning splice junctions
- More specific: directly measures splicing choices
- Lower sensitivity: requires junction-spanning reads
- Recommended for: high-confidence events, short exons

JCEC (Junction Counts + Exon body Counts):
- Uses both junction reads AND reads within the exon body
- Higher sensitivity: captures more events
- May include noise from exon-level expression changes
- Recommended for: comprehensive detection, long exons

Which to use:
- Default: report JCEC results (more events detected)
- Validation: require JC confirmation for highest confidence
- Short exons (<50 bp): JC may be more reliable
- Deep sequencing: JC often sufficient
```

### rMATS Filtering

```python
import pandas as pd

# Load rMATS results
se = pd.read_csv("SE.MATS.JCEC.txt", sep="\t")

# Standard filtering criteria
sig_se = se[
    (se["FDR"] < 0.05) &                    # FDR < 5%
    (abs(se["IncLevelDifference"]) > 0.1) &   # |ΔPSI| > 10%
    (se["IJC_SAMPLE_1"].str.split(",").apply(lambda x: sum(int(i) for i in x)) +
     se["SJC_SAMPLE_1"].str.split(",").apply(lambda x: sum(int(i) for i in x)) >= 10) &  # min total counts
    (se["IJC_SAMPLE_2"].str.split(",").apply(lambda x: sum(int(i) for i in x)) +
     se["SJC_SAMPLE_2"].str.split(",").apply(lambda x: sum(int(i) for i in x)) >= 10)
]

print(f"Total SE events tested: {len(se)}")
print(f"Significant SE events: {len(sig_se)}")
print(f"  Increased inclusion: {(sig_se['IncLevelDifference'] > 0).sum()}")
print(f"  Increased skipping: {(sig_se['IncLevelDifference'] < 0).sum()}")

# Key columns:
# ID, GeneID, geneSymbol, chr, strand
# exonStart_0base, exonEnd — alternative exon coordinates
# upstreamES, upstreamEE — upstream exon
# downstreamES, downstreamEE — downstream exon
# IJC_SAMPLE_1 — inclusion junction counts, condition 1
# SJC_SAMPLE_1 — skipping junction counts, condition 1
# IncFormLen, SkipFormLen — effective inclusion/skipping form lengths
# IncLevel1, IncLevel2 — PSI values per replicate
# IncLevelDifference — ΔPSI (condition2 - condition1)
# PValue, FDR — statistical significance
```

---

## Phase 3: Transcript-Level Analysis with SUPPA2

### SUPPA2 Pipeline

```bash
# SUPPA2: uses transcript quantification (Salmon/Kallisto) for splicing analysis
# Faster than rMATS, handles complex events well

# Step 1: Generate events from annotation
suppa.py generateEvents \
  -i annotation.gtf \
  -o suppa_events \
  -e SE SS MX RI FL \
  -f ioe

# Event types: SE (skipped exon), SS (alt splice sites), MX (MXE), RI (retained intron), FL (first/last exon)

# Step 2: Calculate PSI from transcript TPM
# Input: Salmon/Kallisto transcript quantification
suppa.py psiPerEvent \
  --ioe-file suppa_events_SE_strict.ioe \
  --expression-file transcript_tpm.tsv \
  -o suppa_psi

# Step 3: Differential splicing analysis
# Split TPM and PSI by condition
suppa.py diffSplice \
  --method empirical \
  --input suppa_psi.psi \
  --psi ctrl_psi.psi treat_psi.psi \
  --tpm ctrl_tpm.tsv treat_tpm.tsv \
  -gc \
  -o suppa_diff

# Output:
# suppa_diff.dpsi — ΔPSI values per event
# suppa_diff.psivec — PSI values per sample
```

### SUPPA2 Filtering

```python
import pandas as pd

# Load SUPPA2 differential results
dpsi = pd.read_csv("suppa_diff.dpsi", sep="\t")

# Filter significant events
# SUPPA2 uses empirical p-values
sig_events = dpsi[
    (dpsi["p-value"] < 0.05) &
    (abs(dpsi["dPSI"]) > 0.1)
]

print(f"Significant differential splicing events: {len(sig_events)}")
```

### SUPPA2 vs rMATS Comparison

| Feature | rMATS | SUPPA2 |
|---------|-------|--------|
| **Input** | BAM files | Transcript TPM (Salmon/Kallisto) |
| **Speed** | Slow (re-counts from BAM) | Fast (uses pre-computed TPM) |
| **Statistical model** | Likelihood ratio test | Empirical distribution |
| **Event types** | SE, A5SS, A3SS, MXE, RI | SE, A5SS, A3SS, MXE, RI, AF, AL |
| **Novel events** | Yes (with --novelSS) | No (annotation-dependent) |
| **Replicates needed** | ≥2 (≥3 recommended) | ≥3 (empirical distribution) |
| **Complex events** | Limited | Better (transcript-level) |
| **Recommendation** | Gold standard, publication | Fast exploration, complex events |

---

## Phase 4: Annotation-Free Analysis with Leafcutter

### Leafcutter Pipeline

```bash
# Leafcutter: intron-centric, annotation-free differential splicing
# Detects novel and annotated splicing changes

# Step 1: Extract junction reads from BAMs
for bam in *.bam; do
  regtools junctions extract \
    -a 8 \
    -m 50 \
    -M 500000 \
    -s 0 \
    "$bam" \
    -o "${bam%.bam}.junc"
done

# Step 2: Cluster introns
ls *.junc > junc_files.txt

python leafcutter_cluster_regtools.py \
  -j junc_files.txt \
  -m 50 \
  -l 500000 \
  -o leafcutter

# Step 3: Differential splicing
# Create groups file
echo -e "ctrl1\tctrl\nctrl2\tctrl\nctrl3\tctrl" > groups.txt
echo -e "treat1\ttreat\ntreat2\ttreat\ntreat3\ttreat" >> groups.txt

Rscript leafcutter_ds.R \
  --num_threads 8 \
  --min_samples_per_intron 3 \
  --min_samples_per_group 2 \
  --min_coverage 10 \
  leafcutter_perind_numers.counts.gz \
  groups.txt \
  -o leafcutter_diff

# Step 4: Annotate clusters with gene names
python map_clusters_to_genes.py \
  leafcutter_diff_cluster_significance.txt \
  annotation.gtf \
  leafcutter_annotated.txt
```

### Leafcutter Output Interpretation

```python
import pandas as pd

# Cluster-level results
clusters = pd.read_csv("leafcutter_diff_cluster_significance.txt", sep="\t")

# Filter significant clusters
sig_clusters = clusters[clusters["p.adjust"] < 0.05]

# Per-intron results (effect sizes within clusters)
introns = pd.read_csv("leafcutter_diff_effect_sizes.txt", sep="\t")

# Leafcutter concept:
# - Clusters = groups of overlapping introns that share splice sites
# - Tests whether the RATIO of intron usage changes between conditions
# - Does not require annotation → detects novel splicing
# - Complementary to rMATS (different statistical framework)

# Key advantage: detects complex splicing changes that involve
# multiple junctions simultaneously (not just binary inclusion/exclusion)
```

---

## Phase 5: Isoform Switching Analysis

### IsoformSwitchAnalyzeR (R)

```r
library(IsoformSwitchAnalyzeR)

# Import Salmon quantification
salmonQuant <- importRdata(
  isoformCountMatrix = salmon_counts,
  isoformRepExpression = salmon_tpm,
  designMatrix = data.frame(
    sampleID = sample_names,
    condition = c(rep("ctrl", 3), rep("treat", 3))
  ),
  isoformExonAnnotation = "annotation.gtf"
)

# Pre-filter low-expression isoforms
salmonQuant <- preFilter(
  salmonQuant,
  geneExpressionCutoff = 1,      # gene TPM > 1
  isoformExpressionCutoff = 0,    # include all expressed isoforms
  removeSingleIsoformGenes = TRUE
)

# Test for isoform switching
salmonQuant <- isoformSwitchTestDEXSeq(
  salmonQuant,
  reduceToSwitchingGenes = TRUE
)

# Analyze switching consequences
# Extract amino acid sequences
salmonQuant <- extractSequence(
  salmonQuant,
  pathToOutput = "isoform_sequences/"
)

# Run external tools for functional annotation
# CPC2: coding potential
# Pfam: protein domains
# SignalP: signal peptides
# IUPred2A: intrinsically disordered regions
# (Run externally, then import results)

# Analyze consequences
salmonQuant <- analyzeSwitchConsequences(
  salmonQuant,
  consequencesToAnalyze = c(
    "tss", "tts", "intron_retention",
    "coding_potential", "ORF_seq_similarity",
    "NMD_status", "domains_identified",
    "signal_peptide_identified",
    "idr_identified"
  )
)

# Summary of switching consequences
consequence_summary <- extractSwitchSummary(salmonQuant)

# Visualize specific switches
switchPlot(
  salmonQuant,
  gene = "GENE_OF_INTEREST",
  condition1 = "ctrl",
  condition2 = "treat"
)
```

### Isoform Switch Consequences

| Consequence | Detection | Biological Impact |
|-------------|-----------|------------------|
| **NMD sensitivity** | Premature stop codon >50 nt upstream of last exon junction | Transcript likely degraded by NMD |
| **Domain loss/gain** | Pfam domain annotation comparison | Altered protein function |
| **Coding potential change** | CPC2 or CPAT prediction | Shift from coding to non-coding (or vice versa) |
| **Signal peptide loss** | SignalP prediction | Altered protein localization |
| **IDR change** | IUPred2A prediction | Altered protein-protein interactions |
| **ORF change** | Sequence comparison | Different protein product |
| **5' UTR change** | TSS annotation | Altered translational regulation |
| **3' UTR change** | TTS annotation | Altered miRNA regulation, stability |

---

## Phase 6: Visualization

### Sashimi Plots

```bash
# rmats2sashimiplot: generate sashimi plots from rMATS events
rmats2sashimiplot \
  --b1 ctrl1.bam,ctrl2.bam,ctrl3.bam \
  --b2 treat1.bam,treat2.bam,treat3.bam \
  --event-type SE \
  -e SE.MATS.JCEC.txt \
  --l1 Control \
  --l2 Treatment \
  -o sashimi_plots/ \
  --exon_s 1 \
  --intron_s 5 \
  --font-size 8

# Filter to specific event
rmats2sashimiplot \
  --b1 ctrl1.bam,ctrl2.bam,ctrl3.bam \
  --b2 treat1.bam,treat2.bam,treat3.bam \
  --event-type SE \
  -e filtered_events.txt \
  --l1 Control \
  --l2 Treatment \
  -o sashimi_single/
```

### ggsashimi (Python/R)

```bash
# ggsashimi: publication-quality sashimi plots
ggsashimi.py \
  -b ctrl1.bam,ctrl2.bam,ctrl3.bam,treat1.bam,treat2.bam,treat3.bam \
  -c chr1:1000000-1010000:+ \
  -g annotation.gtf \
  -o sashimi_output.pdf \
  --labels ctrl1,ctrl2,ctrl3,treat1,treat2,treat3 \
  --palette Blues_r,Reds_r \
  --alpha 0.5 \
  --min-coverage 5 \
  --shrink

# Key parameters:
# -c: coordinates (chr:start-end:strand)
# --shrink: shrink introns for better visualization
# --min-coverage: minimum junction read count to display
# --palette: color scheme per group
```

### Visualization Best Practices

```
Sashimi plot elements:
1. Read coverage track (y-axis: read depth)
2. Junction arcs (thickness proportional to junction read count)
3. Gene model (exons as boxes, introns as lines)
4. Minimum junction count label on each arc

What to show:
- Include all replicates (or representative samples)
- Show both conditions side by side
- Label junction read counts
- Include gene model with alternative exon highlighted
- Add PSI values and statistical significance

Color conventions:
- Inclusion junctions: one color (e.g., blue)
- Exclusion junctions: contrasting color (e.g., red)
- Alternative exon: highlighted (e.g., orange box)
```

---

## Phase 7: Splicing QC

### Junction Saturation

```bash
# RSeQC: junction saturation analysis
junction_saturation.py \
  -i aligned.bam \
  -r annotation.bed \
  -o junction_saturation

# Interpretation:
# Curve should plateau — indicates sufficient depth for junction detection
# If still rising at maximum depth → need more sequencing for splicing analysis
# Known junctions should saturate faster than novel junctions
```

### Splice Site Strength (MaxEntScan)

```python
# MaxEntScan: score splice site strength
# Higher score = stronger splice site = more efficiently recognized

import maxentpy

# Score 5' splice site (9-mer: 3 exonic + 6 intronic)
score_5ss = maxentpy.score5("CAGGTAAGT")  # consensus = CAGGUAAGU

# Score 3' splice site (23-mer: 20 intronic + 3 exonic)
score_3ss = maxentpy.score3("TTTTTTTTTTTTTTTTTTTTCAG")

# Interpretation:
# 5'SS scores: typically 0-12, consensus ~11
# 3'SS scores: typically 0-15, consensus ~13
# Weak splice site: <5 (for 5'SS) or <5 (for 3'SS)
# Strong splice site: >8 (for 5'SS) or >8 (for 3'SS)

# Alternative exons often have weaker splice sites than constitutive exons
# → more susceptible to regulation by splicing factors
```

### Splicing QC Metrics

| Metric | Good | Acceptable | Poor | Notes |
|--------|------|-----------|------|-------|
| **Junction reads (%)** | >40% | 20-40% | <20% | Fraction of reads spanning junctions |
| **Known junction rate** | >85% | 70-85% | <70% | Fraction matching annotated junctions |
| **Novel junction rate** | 5-15% | 15-25% | >25% | High novel rate may indicate alignment artifacts |
| **Junction saturation** | Plateau reached | Near plateau | Still rising | Sufficient depth for junction detection |
| **GT-AG junctions** | >98% | 95-98% | <95% | Canonical splice sites |
| **Reads per junction** | >10 (median) | 5-10 | <5 | Support per junction |

---

## Phase 8: Integration with RBP Data

### eCLIP/CLIP-seq Integration

```python
import pandas as pd
import pybedtools

# Identify RBP binding near differentially spliced exons
# eCLIP data from ENCODE

# Load differential splicing events
se_events = pd.read_csv("SE.MATS.JCEC.txt", sep="\t")
sig_events = se_events[(se_events["FDR"] < 0.05) & (abs(se_events["IncLevelDifference"]) > 0.1)]

# Create BED of alternative exons with flanking intronic regions
exon_regions = []
for _, row in sig_events.iterrows():
    chrom = row["chr"]
    # Upstream intron (250 bp)
    exon_regions.append(f"{chrom}\t{max(0, row['exonStart_0base'] - 250)}\t{row['exonStart_0base']}\t{row['ID']}_upstream_intron")
    # Exon body
    exon_regions.append(f"{chrom}\t{row['exonStart_0base']}\t{row['exonEnd']}\t{row['ID']}_exon")
    # Downstream intron (250 bp)
    exon_regions.append(f"{chrom}\t{row['exonEnd']}\t{row['exonEnd'] + 250}\t{row['ID']}_downstream_intron")

exon_bed = pybedtools.BedTool("\n".join(exon_regions), from_string=True)

# Intersect with eCLIP peaks
eclip_peaks = pybedtools.BedTool("RBP_eCLIP_peaks.bed")
overlaps = exon_bed.intersect(eclip_peaks, wa=True, wb=True)

# Count RBP binding events per region type
overlap_df = overlaps.to_dataframe()
# Analyze which RBPs are enriched near differentially spliced exons
```

### Splicing Regulatory Elements

| Element | Location | Function | Example Motifs |
|---------|----------|----------|---------------|
| **ESE** (Exonic Splicing Enhancer) | Exon | Promotes exon inclusion | SR protein binding (SRSF1: GGAGGA) |
| **ESS** (Exonic Splicing Silencer) | Exon | Promotes exon skipping | hnRNP binding (hnRNPA1: UAGGG[AU]) |
| **ISE** (Intronic Splicing Enhancer) | Intron | Promotes inclusion of adjacent exon | U-rich elements, G-runs |
| **ISS** (Intronic Splicing Silencer) | Intron | Promotes skipping of adjacent exon | PTBP1 binding (UCUU), hnRNP sites |

### Key Splicing Factors

| Factor | Type | Binding Motif | Function | Cancer Relevance |
|--------|------|--------------|----------|-----------------|
| **SRSF1** | SR protein | GGAGGA, GA-rich | Promotes inclusion | Oncogenic when overexpressed |
| **SRSF2** | SR protein | CCNG, C-rich | Context-dependent | Mutated in MDS/AML (P95H/L/R) |
| **hnRNPA1** | hnRNP | UAGGGA/U | Promotes skipping | Overexpressed in many cancers |
| **PTBP1** | hnRNP | UCUUC, CU-rich | Promotes skipping, RI | Regulates EMT splicing |
| **RBFOX2** | Fox family | UGCAUG | Tissue-specific splicing | Altered in cancer EMT |
| **QKI** | STAR family | ACUAAY | Promotes inclusion | Tumor suppressor in glioblastoma |
| **MBNL1** | Muscleblind | YGCY | Opposes CELF1 | Sequestered in myotonic dystrophy |
| **U2AF1** | Spliceosome | 3'SS AG recognition | Core splicing | Mutated in MDS (S34F) |
| **SF3B1** | Spliceosome | Branch point | Core splicing | Mutated in MDS, CLL (K700E) |

---

## Phase 9: Single-Cell Splicing

### RNA Velocity (scVelo)

```python
import scvelo as scv
import scanpy as sc

# Load count matrices (requires separate spliced/unspliced quantification)
# From velocyto or STARsolo
adata = scv.read("sample.loom", cache=True)
# or from AnnData with spliced/unspliced layers
adata = sc.read_h5ad("adata_with_velocity.h5ad")

# Preprocess
scv.pp.filter_and_normalize(adata, min_shared_counts=20, n_top_genes=2000)
scv.pp.moments(adata, n_pcs=30, n_neighbors=30)

# Estimate RNA velocity
# Stochastic model (faster)
scv.tl.velocity(adata, mode="stochastic")
# or Dynamical model (more accurate)
scv.tl.recover_dynamics(adata, n_jobs=8)
scv.tl.velocity(adata, mode="dynamical")

# Velocity graph and embedding
scv.tl.velocity_graph(adata)
scv.pl.velocity_embedding_stream(adata, basis="umap", color="cell_type")

# Gene-specific velocity
scv.pl.velocity(adata, var_names=["GENE1", "GENE2"], basis="umap")

# Latent time (pseudotime from velocity)
scv.tl.latent_time(adata)
scv.pl.scatter(adata, color="latent_time", color_map="gnuplot")
```

### Velocyto (Spliced/Unspliced Quantification)

```bash
# Generate spliced/unspliced count matrices from BAM
velocyto run \
  -b filtered_barcodes.tsv \
  -o velocyto_output/ \
  -m repeat_mask.gtf \
  possorted_genome_bam.bam \
  annotation.gtf

# For 10x Chromium:
velocyto run10x \
  -m repeat_mask.gtf \
  cellranger_output_dir/ \
  annotation.gtf

# Output: .loom file with spliced, unspliced, ambiguous layers
```

### Single-Cell Splicing Considerations

```
Challenges:
- Low read counts per gene per cell → noisy PSI estimates
- Dropout: many genes undetected in individual cells
- Need to aggregate cells for robust splicing quantification
- Imputation may introduce artifacts

Approaches:
1. Pseudobulk: aggregate cells by cluster, then run standard tools
2. Brie2: Bayesian single-cell splicing quantification
3. Leafcutter-sc: adapted Leafcutter for single-cell data
4. RNA velocity: uses spliced/unspliced ratio as dynamic readout

Best practice:
- Pseudobulk analysis as primary approach (most robust)
- Single-cell methods for exploratory/hypothesis generation
- Validate key findings with independent methods (RT-PCR, long reads)
```

---

## Phase 10: Clinical Interpretation

### Splice-Site Variant Classification

```python
# Assess impact of variants on splicing

# Canonical splice sites: first 2 bp of intron (GT at 5', AG at 3')
# Disruption is almost always pathogenic

# Extended splice region:
# 5' splice site: exon[-3:-1] + intron[+1:+8]
# 3' splice site: intron[-14:-1] + exon[+1:+1]

def classify_splice_variant(chrom, pos, ref, alt, transcript):
    """
    Classify variant impact on splicing.

    Categories (ACMG-relevant):
    - PVS1: null variant in splice site (donor +1/+2, acceptor -1/-2)
    - PS3: functional studies show aberrant splicing
    - PM5: novel missense in same splice region as known pathogenic
    - PP3: in silico predictions support splicing impact
    """
    # Canonical splice sites (±1-2): almost certainly pathogenic
    if is_canonical_splice(pos, transcript):
        return "PVS1_applicable", "Canonical splice site disrupted"

    # Extended splice region: MaxEntScan scoring
    ref_score = maxentscan_score(ref_sequence)
    alt_score = maxentscan_score(alt_sequence)
    delta_score = alt_score - ref_score

    if delta_score < -3:
        return "PP3_supporting", f"MaxEntScan Δ={delta_score:.1f} (strong reduction)"
    elif delta_score < -1.5:
        return "PP3_supporting", f"MaxEntScan Δ={delta_score:.1f} (moderate reduction)"
    else:
        return "benign_likely", f"MaxEntScan Δ={delta_score:.1f} (minimal impact)"
```

### Aberrant Splicing in Cancer

| Cancer Type | Common Splicing Alterations | Mechanism |
|-------------|---------------------------|-----------|
| **MDS/AML** | SF3B1 K700E, SRSF2 P95H, U2AF1 S34F mutations | Spliceosome component mutations |
| **Breast cancer** | CD44 isoform switching (CD44v → CD44s) | EMT-associated |
| **Lung cancer** | FGFR2 IIIb→IIIc switch | Epithelial-mesenchymal transition |
| **Glioblastoma** | hnRNPH-driven aberrant splicing | RBP overexpression |
| **CLL** | SF3B1 mutation → aberrant 3' splice sites | Branch point recognition altered |
| **General** | Exon skipping in tumor suppressors (e.g., BRCA1 exon 11) | Loss of function |
| **General** | Intron retention → NMD → downregulation | Pseudogene-like mechanism |

### Aberrant Splicing Detection from RNA-seq

```
Pipeline for clinical aberrant splicing:
1. Standard alignment (STAR 2-pass)
2. rMATS analysis: tumor vs matched normal (or panel of normals)
3. Focus on:
   - Events in known cancer genes
   - Events creating premature stop codons (NMD candidates)
   - Events disrupting functional protein domains
   - Events creating novel ORFs (potential neoantigens)
4. Validate top candidates with RT-PCR or long-read sequencing

Filtering for clinical relevance:
- |ΔPSI| > 0.2 (20% change — more stringent for clinical)
- FDR < 0.01
- Gene in cancer gene census (COSMIC) or ClinVar
- Event creates functional consequence (NMD, domain loss)
```

---

## Decision Trees

### Overall Splicing Analysis Strategy

```
Input: RNA-seq data (≥2 conditions, replicates)
│
├── What analysis?
│   ├── Differential splicing events → Phase 2 (rMATS) or Phase 3 (SUPPA2)
│   ├── Annotation-free discovery → Phase 4 (Leafcutter)
│   ├── Isoform switching → Phase 5 (IsoformSwitchAnalyzeR)
│   └── Single-cell splicing → Phase 9 (scVelo, pseudobulk)
│
├── Which tool?
│   ├── Publication-quality, event-level → rMATS (gold standard)
│   ├── Fast exploration, transcript-level → SUPPA2
│   ├── Novel events, intron-centric → Leafcutter
│   └── Functional consequences → IsoformSwitchAnalyzeR
│
├── Filtering
│   ├── |ΔPSI| > 0.1 (standard) or > 0.2 (stringent)
│   ├── FDR < 0.05 (standard) or < 0.01 (stringent)
│   └── Minimum junction/read support ≥10
│
├── Visualization
│   ├── Sashimi plots → rmats2sashimiplot or ggsashimi
│   ├── Volcano plot → ΔPSI vs -log10(FDR)
│   └── Heatmap → PSI values across samples
│
├── Integration
│   ├── RBP binding → eCLIP/CLIP-seq overlap
│   ├── Splice site strength → MaxEntScan
│   ├── Regulatory elements → ESE/ESS motif analysis
│   └── Expression → gene-level + isoform-level changes
│
└── Clinical (if applicable)
    ├── Splice-site variants → MaxEntScan, SpliceAI
    ├── Cancer-specific → known splicing alterations per cancer type
    └── Neoantigens → immunoinformatics skill for novel peptides
```

### Splicing Tool Selection Decision Tree

```
What is the primary question?
│
├── "Which exons are differentially included/excluded?"
│   └── rMATS → event-level analysis with JC and JCEC counts
│
├── "What transcript isoforms change between conditions?"
│   └── SUPPA2 → transcript-level PSI from Salmon/Kallisto
│
├── "Are there novel, unannotated splicing changes?"
│   └── Leafcutter → annotation-free, intron-centric
│
├── "What are the functional consequences of isoform switches?"
│   └── IsoformSwitchAnalyzeR → domain loss, NMD, coding potential
│
├── "How does splicing vary across single cells?"
│   └── Pseudobulk + rMATS (robust) or scVelo (dynamic)
│
└── "Is this variant likely to disrupt splicing?"
    └── MaxEntScan (splice site scoring) + SpliceAI (deep learning)
```

---

## Troubleshooting

```
Few significant events detected:
├── Low sequencing depth → need ≥30M reads for splicing
├── Low replicate count → add more biological replicates
├── Wrong alignment → ensure STAR 2-pass mode with splice-aware settings
├── Stringent thresholds → relax to |ΔPSI| > 0.05, FDR < 0.1
└── Biology: subtle splicing changes → use SUPPA2 (higher sensitivity)

High false positive rate:
├── No replicate filtering → require replicates to agree
├── Low junction counts → increase minimum count threshold
├── Mapping artifacts → check multi-mapping reads
└── Batch effects → include batch in model or use combat

rMATS errors:
├── "BAM file not indexed" → samtools index *.bam
├── "Read length mismatch" → use --variable-read-length
├── "Out of memory" → reduce --tstat threads, increase RAM
└── "No events detected" → check GTF annotation matches genome build

Sashimi plot issues:
├── Empty plots → check BAM coordinate range matches event
├── No junction arcs → reads not spanning junction, increase depth
├── Wrong strand → verify strandedness in alignment
└── Scale issues → use --intron_s to shrink introns
```

## Completeness Checklist

- [ ] RNA-seq aligned with splice-aware aligner (STAR 2-pass recommended)
- [ ] Splicing QC: junction saturation, GT-AG rate, junction read fraction
- [ ] Differential splicing analysis completed (rMATS and/or SUPPA2)
- [ ] Results filtered: |ΔPSI| > 0.1, FDR < 0.05, minimum read support
- [ ] Event types characterized (SE, A5SS, A3SS, MXE, RI)
- [ ] Sashimi plots generated for top events
- [ ] Isoform switching consequences analyzed (if applicable)
- [ ] RBP binding data integrated (if eCLIP/CLIP available)
- [ ] Splice site strength evaluated (MaxEntScan)
- [ ] Clinical relevance assessed (if disease context)
- [ ] Results validated or validation experiments planned
