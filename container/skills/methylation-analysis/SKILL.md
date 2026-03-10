---
name: methylation-analysis
description: DNA methylation analyst for bisulfite sequencing and methylation array data. WGBS, RRBS, EM-seq alignment and methylation calling, DMR detection, CpG island annotation, methylation arrays (EPIC/450K), cell-type deconvolution from methylation. Use when user mentions DNA methylation, bisulfite sequencing, WGBS, RRBS, EM-seq, enzymatic methyl-seq, Bismark, bwa-meth, methylation calling, CpG methylation, CpG islands, DMR, differentially methylated regions, DML, methylKit, bsseq, BSmooth, DMRcate, dmrseq, Illumina EPIC, 450K array, minfi, sesame, methylation heatmap, imprinting, allele-specific methylation, EpiDISH, MethylCIBERSORT, cell-type deconvolution from methylation, CHG, CHH context, or methylation-expression correlation.
---

# DNA Methylation Analysis

Comprehensive pipeline for DNA methylation analysis from bisulfite/enzymatic sequencing and methylation arrays. Covers alignment, methylation extraction, differentially methylated region (DMR) detection, genomic annotation, array processing, integration with expression data, and cell-type deconvolution.

## Report-First Workflow

1. **Create report file immediately**: `[sample]_methylation_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as analysis proceeds
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill
- Nanopore native methylation calling -> use long-read-sequencing skill
- Hi-C chromatin organization -> use hic-analysis skill
- ChIP-seq histone modification analysis -> use appropriate ChIP-seq skill
- RNA-seq gene expression -> use RNA-seq skill
- Single-cell methylation (scBS-seq) -> specialized single-cell methylation pipeline

## Cross-Reference: Other Skills
- **ONT methylation** -> use long-read-sequencing skill for nanopore-native 5mC/5hmC
- **Methylation at TAD boundaries** -> use hic-analysis skill for 3D context
- **Expression correlation** -> use RNA-seq skill for expression quantification
- **Splicing and methylation** -> use alternative-splicing skill
- **Neoantigen silencing by methylation** -> use immunoinformatics skill

---

## Bisulfite Sequencing Overview

### Protocol Comparison

| Protocol | Coverage | Cost | Input DNA | Resolution | Best For |
|----------|---------|------|-----------|------------|---------|
| **WGBS** | Genome-wide | High | 200 ng - 1 ug | Single CpG | Comprehensive methylome |
| **RRBS** | CpG-rich regions | Low | 10-100 ng | Single CpG | CpG islands, promoters |
| **EM-seq** | Genome-wide | High | 10-200 ng | Single CpG | Low-input, less degradation |
| **Targeted panels** | Selected regions | Low | 10-100 ng | Single CpG | Specific loci, clinical |
| **EPIC array** | ~850K CpGs | Low | 250 ng | Probe-level | Large cohorts, EWAS |
| **450K array** | ~450K CpGs | Low | 500 ng | Probe-level | Legacy, large cohorts |

### Bisulfite vs Enzymatic Conversion

```
Bisulfite sequencing (BS-seq):
- Chemical conversion: sodium bisulfite converts unmethylated C → U (read as T)
- Methylated C (5mC and 5hmC) protected from conversion
- Drawback: DNA degradation (>90% loss), reduced complexity, biased fragmentation
- Cannot distinguish 5mC from 5hmC

Enzymatic methyl-seq (EM-seq):
- Enzymatic conversion: TET2 oxidizes 5mC/5hmC → 5caC, then APOBEC deaminates
- Unmethylated C protected, methylated C converted (opposite logic)
- Advantages: less DNA degradation, lower input, more uniform coverage
- Better library complexity, less GC bias
- Cannot distinguish 5mC from 5hmC (standard protocol)

Oxidative bisulfite (oxBS-seq):
- Chemical oxidation of 5hmC → 5fC, then bisulfite
- BS-seq - oxBS-seq = 5hmC levels
- Distinguishes 5mC from 5hmC
```

---

## Phase 1: Alignment

### Bismark (Standard)

```bash
# Step 1: Prepare bisulfite genome
bismark_genome_preparation --bowtie2 reference_genome/

# Step 2: Align reads
# Paired-end WGBS
bismark \
  --bowtie2 \
  --genome reference_genome/ \
  -1 reads_R1.fastq.gz \
  -2 reads_R2.fastq.gz \
  --multicore 8 \
  --nucleotide_coverage \
  -o bismark_output/

# Single-end RRBS (with RRBS-specific trimming)
# First trim with Trim Galore (RRBS mode)
trim_galore --rrbs --paired reads_R1.fastq.gz reads_R2.fastq.gz

bismark \
  --bowtie2 \
  --genome reference_genome/ \
  reads_R1_val_1.fq.gz \
  --multicore 8 \
  -o bismark_output/

# Step 3: Deduplicate
deduplicate_bismark \
  --bam \
  --paired \
  bismark_output/reads_R1_bismark_bt2_pe.bam

# Step 4: Extract methylation
bismark_methylation_extractor \
  --paired-end \
  --comprehensive \
  --bedGraph \
  --CX \
  --cytosine_report \
  --genome_folder reference_genome/ \
  --multicore 8 \
  reads_R1_bismark_bt2_pe.deduplicated.bam

# Output files:
# CpG_context_*.txt        — per-read CpG methylation calls
# CHG_context_*.txt        — per-read CHG methylation calls (plants)
# CHH_context_*.txt        — per-read CHH methylation calls (plants)
# *.bedGraph.gz            — methylation percentages per CpG
# *.cov.gz                 — coverage file (chr, start, end, %meth, count_meth, count_unmeth)
# *_splitting_report.txt   — methylation extraction report
# *.cytosine_report.txt    — genome-wide CpG report
```

### bwa-meth (Alternative)

```bash
# bwa-meth: faster alternative using bwa-mem
# Index
bwameth.py index reference.fa

# Align
bwameth.py \
  --reference reference.fa \
  --threads 16 \
  reads_R1.fastq.gz reads_R2.fastq.gz \
  | samtools sort -@ 8 -o aligned.bam

samtools index aligned.bam

# Mark duplicates
samtools markdup aligned.bam dedup.bam
samtools index dedup.bam

# Extract methylation with MethylDackel
MethylDackel extract \
  --CHG --CHH \
  --minDepth 5 \
  --mergeContext \
  reference.fa \
  dedup.bam \
  -o methyldackel_output
```

### Aligner Comparison

| Tool | Backend | Speed | Memory | Special Features |
|------|---------|-------|--------|-----------------|
| **Bismark** | Bowtie2/HISAT2 | Moderate | Moderate | Full pipeline, excellent reports |
| **bwa-meth** | BWA-MEM | Fast | Low | Faster, standard BAM output |
| **BSBolt** | BWA-MEM2 | Very fast | Low | Newest, WGBS + RRBS modes |

### Alignment QC

| Metric | Good (WGBS) | Good (RRBS) | Poor | Notes |
|--------|-------------|-------------|------|-------|
| **Mapping rate** | >70% | >60% | <50% | Lower than WGS due to reduced complexity |
| **Duplicate rate** | <20% | <30% | >40% | RRBS tolerates more due to MspI sites |
| **Bisulfite conversion** | >99% | >99% | <98% | From non-CpG methylation in mammals |
| **CpG coverage ≥5x** | >80% | >50% | <30% | Minimum for reliable methylation calls |
| **Mean CpG coverage** | >10x | >20x | <5x | RRBS has higher per-site coverage |
| **M-bias** | Flat | Flat | Sloped | Position-dependent methylation artifacts |

### M-bias Detection and Correction

```bash
# Bismark generates M-bias plots automatically
# Check: bismark_methylation_extractor produces M-bias report

# If M-bias detected (methylation varies by read position):
bismark_methylation_extractor \
  --ignore 5 \              # ignore first 5 bp of R1
  --ignore_r2 5 \           # ignore first 5 bp of R2
  --ignore_3prime 3 \       # ignore last 3 bp of R1
  --ignore_3prime_r2 3 \    # ignore last 3 bp of R2
  --paired-end \
  --comprehensive \
  --bedGraph \
  dedup.bam

# Common M-bias patterns:
# - High methylation at read starts: adapter contamination or end repair
# - Decreasing methylation along read: quality-related bisulfite conversion failure
# - R2 artifacts: filled-in 3' end of R1 after end repair
```

---

## Phase 2: Methylation Calling and Filtering

### Methylation Level Calculation

```python
import pandas as pd
import numpy as np

# Load Bismark coverage file
# Format: chr, start, end, methylation_percentage, count_methylated, count_unmethylated
cov = pd.read_csv("sample.bismark.cov.gz", sep="\t",
                    names=["chr", "start", "end", "meth_pct", "count_meth", "count_unmeth"])

# Calculate total coverage
cov["coverage"] = cov["count_meth"] + cov["count_unmeth"]

# Filter by coverage
min_coverage = 5
max_coverage = np.percentile(cov["coverage"], 99.9)  # remove PCR-inflated sites
cov_filtered = cov[(cov["coverage"] >= min_coverage) & (cov["coverage"] <= max_coverage)]

print(f"Total CpGs: {len(cov):,}")
print(f"CpGs ≥{min_coverage}x: {len(cov_filtered):,} ({len(cov_filtered)/len(cov)*100:.1f}%)")
print(f"Mean methylation: {cov_filtered['meth_pct'].mean():.1f}%")
print(f"Median coverage: {cov_filtered['coverage'].median():.0f}x")
```

### Methylation Context (CpG/CHG/CHH)

| Context | Pattern | Methylation in Mammals | Methylation in Plants | Notes |
|---------|---------|----------------------|----------------------|-------|
| **CpG** | 5'-CG-3' | 70-80% (genome-wide) | 20-40% | Primary, maintained by DNMT1 |
| **CHG** | 5'-C[ACT]G-3' | <1% | 5-10% | Plant-specific (CMT3) |
| **CHH** | 5'-C[ACT][ACT]-3' | <1% | 2-5% | De novo by DRM2 (plants) |

```
Mammalian CpG methylation patterns:
- Gene bodies: ~80% methylated (correlated with expression)
- CpG islands at promoters: <10% methylated (unmethylated = active)
- CpG island shores (±2 kb): variable, often differentially methylated
- CpG island shelves (±2-4 kb): moderate methylation
- Repetitive elements: >90% methylated (genome defense)
- Imprinted regions: ~50% methylated (allele-specific)

Non-CpG methylation in mammals:
- Enriched in embryonic stem cells and neurons
- Indicator of de novo methylation (DNMT3A/3B activity)
- If non-CpG >1%: consider biological significance in these cell types
- If non-CpG >2% genome-wide: check bisulfite conversion rate
```

---

## Phase 3: DMR Detection

### methylKit (R)

```r
library(methylKit)

# Read Bismark coverage files
# List of coverage files, sample IDs, treatment vector
file.list <- list("ctrl1.cov", "ctrl2.cov", "ctrl3.cov",
                  "treat1.cov", "treat2.cov", "treat3.cov")

# Read as methylRaw objects
myobj <- methRead(
  file.list,
  sample.id = list("ctrl1", "ctrl2", "ctrl3", "treat1", "treat2", "treat3"),
  assembly = "hg38",
  treatment = c(0, 0, 0, 1, 1, 1),
  context = "CpG",
  mincov = 5
)

# Filter by coverage
myobj.filtered <- filterByCoverage(
  myobj,
  lo.count = 5,     # minimum 5x coverage
  lo.perc = NULL,
  hi.count = NULL,
  hi.perc = 99.9    # remove top 0.1% (PCR duplicates)
)

# Normalize coverage between samples
myobj.norm <- normalizeCoverage(myobj.filtered, method = "median")

# Merge samples (keep CpGs covered in all samples)
meth <- unite(myobj.norm, destrand = FALSE, min.per.group = 2L)

# === Single CpG differential methylation (DML) ===
myDiff <- calculateDiffMeth(
  meth,
  overdispersion = "MN",    # methylKit default: "MN" (beta-binomial)
  adjust = "BH",
  test = "Chisq",
  mc.cores = 8
)

# Filter significant DMLs
myDiff.sig <- getMethylDiff(
  myDiff,
  difference = 25,     # minimum 25% methylation difference
  qvalue = 0.01,
  type = "all"         # "hyper" or "hypo" for directional
)

# === Tile-based DMR analysis ===
tiles <- tileMethylCounts(myobj.norm, win.size = 1000, step.size = 1000)
meth.tiles <- unite(tiles, destrand = FALSE)

myDiff.tiles <- calculateDiffMeth(meth.tiles, overdispersion = "MN", adjust = "BH")
myDiff.tiles.sig <- getMethylDiff(myDiff.tiles, difference = 25, qvalue = 0.01)

# Annotate with genomic features
library(genomation)
gene.obj <- readTranscriptFeatures("hg38_refseq.bed")
diffAnn <- annotateWithGeneParts(as(myDiff.sig, "GRanges"), gene.obj)
```

### bsseq / BSmooth (R)

```r
library(bsseq)

# Create BSseq object from Bismark cytosine reports
bs <- read.bismark(
  files = c("ctrl1.cov", "ctrl2.cov", "treat1.cov", "treat2.cov"),
  sampleNames = c("ctrl1", "ctrl2", "treat1", "treat2"),
  rmZeroCov = TRUE,
  strandCollapse = TRUE
)

# Filter: require coverage in all samples
bs.filtered <- bs[which(
  rowSums(getCoverage(bs) >= 5) == ncol(bs)
), ]

# BSmooth smoothing
bs.smooth <- BSmooth(
  bs.filtered,
  ns = 70,          # minimum CpGs in smoothing window
  h = 1000,         # smoothing bandwidth (bp)
  maxGap = 10000,   # max gap between CpGs
  mc.cores = 8,
  verbose = TRUE
)

# Compute t-statistics for DMR detection
bs.tstat <- BSmooth.tstat(
  bs.smooth,
  group1 = c("treat1", "treat2"),
  group2 = c("ctrl1", "ctrl2"),
  estimate.var = "group2",   # use control group for variance
  local.correct = TRUE
)

# Find DMRs
dmrs <- dmrFinder(
  bs.tstat,
  cutoff = c(-4.6, 4.6),   # t-statistic cutoff
  qcutoff = c(0.025, 0.975) # or quantile-based
)

# Filter DMRs
dmrs.filtered <- subset(dmrs, n >= 3 & abs(areaStat) > 10)
# n >= 3: minimum 3 CpGs per DMR
# areaStat: sum of t-statistics (larger = stronger DMR)
```

### DMRcate (R)

```r
library(DMRcate)
library(limma)

# From methylation matrix (beta values or M-values)
# Design matrix
design <- model.matrix(~ group, data = pheno)

# Fit linear model
myannotation <- cpg.annotate(
  datatype = "array",       # or "sequencing"
  object = mvals,           # M-values matrix (CpGs x samples)
  what = "M",
  arraytype = "EPIC",       # or "450K"
  analysis.type = "differential",
  design = design,
  coef = 2,                 # column in design matrix
  fdr = 0.05
)

# Find DMRs using Gaussian kernel smoothing
dmrcate.results <- dmrcate(
  myannotation,
  lambda = 1000,     # Gaussian kernel bandwidth (bp)
  C = 2,             # scaling factor
  min.cpgs = 3,      # minimum CpGs per DMR
  pcutoff = "fdr"
)

# Extract ranges
dmr.ranges <- extractRanges(dmrcate.results, genome = "hg38")

# View top DMRs
head(dmr.ranges[order(dmr.ranges$Stouffer), ])
```

### dmrseq (R)

```r
library(dmrseq)

# dmrseq: permutation-based DMR inference
# Input: BSseq object
dmrs <- dmrseq(
  bs = bs.filtered,
  testCovariate = "Type",     # column in pData(bs) indicating groups
  cutoff = 0.10,              # effect size cutoff (methylation difference)
  BPPARAM = BiocParallel::MulticoreParam(8)
)

# Results include:
# - areaStat: statistic summarizing DMR significance
# - direction: hyper or hypo
# - L: number of CpGs in DMR
# - pvalue, qvalue: statistical significance

# Filter significant DMRs
sig.dmrs <- dmrs[dmrs$qvalue < 0.05, ]
```

### DMR Caller Comparison

| Tool | Method | Strengths | Limitations | Best For |
|------|--------|----------|-------------|---------|
| **methylKit** | Logistic regression / chi-square | Simple, fast, single-CpG + tiles | Requires equal coverage | Large cohorts, quick analysis |
| **bsseq/BSmooth** | Local smoothing + t-test | Handles low coverage, smooth profiles | Needs ≥3 samples/group | WGBS with moderate coverage |
| **DMRcate** | Gaussian kernel smoothing + limma | Works with arrays and sequencing | Assumes probe/CpG density | EPIC/450K arrays, WGBS |
| **dmrseq** | Permutation-based | Rigorous FDR control, no parametric assumptions | Slow for large genomes | Publication-quality DMRs |

### DMR Caller Decision Guide

```
Choose methylKit when:
- Quick exploratory analysis needed
- Large number of samples (>20)
- Both single-CpG and region-level analysis desired
- Working with RRBS (good CpG density at target regions)

Choose bsseq/BSmooth when:
- WGBS data with moderate coverage (5-15x)
- Smoothing needed for noisy low-coverage data
- Paired design or complex experimental setup
- Want to visualize smoothed methylation profiles

Choose DMRcate when:
- Methylation array data (EPIC/450K)
- Combined array + sequencing analysis
- Standard two-group comparison with limma framework
- Integration with existing limma/minfi workflows

Choose dmrseq when:
- Need rigorous statistical inference
- Publication-quality results required
- Permutation-based FDR control desired
- Smaller sample sizes (can work with n=2 per group)
```

### DMR Filtering Guidelines

| Parameter | Recommended | Minimum | Notes |
|-----------|------------|---------|-------|
| **Minimum CpGs** | ≥5 | ≥3 | More CpGs = more robust DMR |
| **Methylation difference** | ≥25% | ≥10% | Biological significance threshold |
| **FDR (q-value)** | <0.05 | <0.1 | Multiple testing correction |
| **DMR length** | >100 bp | >50 bp | Very short DMRs may be artifacts |
| **Coverage per CpG** | ≥5x all samples | ≥3x | Higher = more confident |

---

## Phase 4: Genomic Annotation

### CpG Island / Shore / Shelf Classification

```python
import pandas as pd
import pybedtools

# Define genomic regions
# CpG island: high CpG density, typically unmethylated at promoters
# CpG shore: ±2 kb flanking island
# CpG shelf: 2-4 kb flanking island
# Open sea: >4 kb from nearest island

cpg_islands = pybedtools.BedTool("cpg_islands_hg38.bed")

# Extend islands to create shores and shelves
shores_up = cpg_islands.slop(l=2000, r=0, g="chromsizes.txt").subtract(cpg_islands)
shores_down = cpg_islands.slop(l=0, r=2000, g="chromsizes.txt").subtract(cpg_islands)
shores = shores_up.cat(shores_down).sort().merge()

shelves_up = cpg_islands.slop(l=4000, r=0, g="chromsizes.txt").subtract(
    cpg_islands.slop(l=2000, r=0, g="chromsizes.txt"))
shelves_down = cpg_islands.slop(l=0, r=4000, g="chromsizes.txt").subtract(
    cpg_islands.slop(l=0, r=2000, g="chromsizes.txt"))
shelves = shelves_up.cat(shelves_down).sort().merge()

# Annotate DMRs
dmrs = pybedtools.BedTool("significant_dmrs.bed")
dmrs_at_islands = dmrs.intersect(cpg_islands, wa=True, u=True)
dmrs_at_shores = dmrs.intersect(shores, wa=True, u=True)
dmrs_at_shelves = dmrs.intersect(shelves, wa=True, u=True)
```

### Annotation with R

```r
library(annotatr)

# Build annotation set
annots <- build_annotations(genome = "hg38",
  annotations = c(
    "hg38_cpgs",            # CpG islands, shores, shelves, open sea
    "hg38_basicgenes",      # promoters, exons, introns, intergenic
    "hg38_genes_firstexons",
    "hg38_enhancers_fantom"  # FANTOM5 enhancers
  ))

# Annotate DMRs
dmr.gr <- makeGRangesFromDataFrame(dmrs, keep.extra.columns = TRUE)
dm_annotated <- annotate_regions(
  regions = dmr.gr,
  annotations = annots,
  ignore.strand = TRUE,
  quiet = FALSE
)

# Summarize annotation distribution
annot_summary <- summarize_annotations(
  annotated_regions = dm_annotated,
  quiet = FALSE
)
```

### Expected Methylation by Genomic Context

| Region | Normal Methylation | Significance of Change |
|--------|-------------------|----------------------|
| **CpG island (promoter)** | <10% | Hypermethylation → gene silencing (tumor suppressor loss) |
| **CpG island (intragenic)** | Variable | Often methylated in gene bodies of active genes |
| **CpG shore** | Variable (30-70%) | Most tissue-specific DMRs occur at shores |
| **CpG shelf** | 60-80% | Moderate methylation, less variable |
| **Open sea** | 70-90% | High baseline methylation |
| **Gene body** | 60-80% | Positively correlated with expression |
| **Promoter (non-island)** | Variable | Methylation inversely correlated with expression |
| **Enhancer** | Variable | Active enhancers tend to be hypomethylated |
| **Repetitive elements** | >90% | Hypomethylation → genome instability |

---

## Phase 5: Methylation Array Analysis

### minfi Pipeline (R)

```r
library(minfi)

# Read IDAT files
rgSet <- read.metharray.exp(targets = targets, extended = TRUE)

# QC
qcReport(rgSet, pdf = "qc_report.pdf")
detP <- detectionP(rgSet)

# Remove failed probes (detection p-value > 0.01)
keep <- colMeans(detP < 0.01) > 0.95
rgSet <- rgSet[, keep]

# Preprocessing and normalization
# Option 1: Noob (within-array, recommended for most cases)
mSet <- preprocessNoob(rgSet)

# Option 2: Functional normalization (between-array, for heterogeneous samples)
grSet <- preprocessFunnorm(rgSet)

# Option 3: Quantile normalization (between-array, homogeneous samples)
grSet <- preprocessQuantile(rgSet)

# Get beta values (0-1 methylation percentage)
betas <- getBeta(grSet)

# Get M-values (log2 ratio, better for statistical testing)
mvals <- getM(grSet)

# Filter probes
# Remove SNP probes
grSet <- dropLociWithSnps(grSet, snps = c("SBE", "CpG"), maf = 0.05)

# Remove cross-reactive probes (Pidsley et al. 2016)
xreactive <- read.csv("cross_reactive_probes_EPIC.csv")
grSet <- grSet[!rownames(grSet) %in% xreactive$probe, ]

# Remove sex chromosome probes (if analyzing mixed sexes)
grSet <- grSet[!seqnames(grSet) %in% c("chrX", "chrY"), ]
```

### sesame Pipeline (R)

```r
library(sesame)

# sesame: more recent, handles EPIC v2
# Read and process IDAT files
betas <- openSesame(idat_dir, func = getBetas)

# Step-by-step processing
sdf <- readIDATpair(prefix)
sdf <- pOOBAH(sdf)           # P-value detection
sdf <- noob(sdf)             # Background correction
sdf <- dyeBiasNL(sdf)        # Dye bias correction

betas <- getBetas(sdf)

# Differential methylation with limma
library(limma)
design <- model.matrix(~ group, data = pheno)
fit <- lmFit(mvals, design)
fit <- eBayes(fit)
results <- topTable(fit, coef = 2, number = Inf, sort.by = "p")

# Filter significant DMLs
sig_probes <- results[results$adj.P.Val < 0.05 & abs(results$logFC) > 1, ]
```

### Array QC Checklist

```
Pre-processing QC:
- [ ] Detection p-values: <5% failed probes per sample
- [ ] Median intensity: comparable across samples (check density plots)
- [ ] Sex prediction matches reported sex (minfi::getSex)
- [ ] Age prediction reasonable (methylclock)
- [ ] No batch effects visible in PCA (check plate, chip position)
- [ ] Bisulfite conversion control probes: all green

Probe filtering:
- [ ] Failed probes removed (detection p > 0.01)
- [ ] Cross-reactive probes removed (~44K for EPIC)
- [ ] SNP-affected probes removed
- [ ] Sex chromosome probes handled appropriately
- [ ] Probes remaining after filtering: >750K (EPIC), >400K (450K)
```

---

## Phase 6: Integration with Gene Expression

### Methylation-Expression Correlation

```r
# Correlate promoter methylation with gene expression
library(GenomicRanges)

# Get promoter methylation (TSS ± 1500 bp)
promoter.meth <- summarize_promoter_methylation(betas, annotation, tss_flank = 1500)

# Match with expression data (TPM from RNA-seq)
common_genes <- intersect(rownames(promoter.meth), rownames(expression))

# Compute per-gene correlation
cors <- sapply(common_genes, function(gene) {
  m <- promoter.meth[gene, ]
  e <- expression[gene, ]
  if (sd(m) == 0 | sd(e) == 0) return(NA)
  cor(m, e, method = "spearman")
})

# Expected: negative correlation for CpG island promoters
# Typical r ~ -0.3 to -0.6 for regulated genes
median_cor <- median(cors, na.rm = TRUE)
cat("Median methylation-expression correlation:", median_cor, "\n")
```

### Interpretation Guidelines

```
Methylation-expression relationships:

1. Promoter CpG island methylation (most studied):
   - Inverse correlation: methylation UP → expression DOWN
   - Classic tumor suppressor silencing mechanism
   - Look for: promoter hypermethylation + gene downregulation

2. Gene body methylation:
   - Positive correlation: methylation UP → expression UP
   - Marks actively transcribed genes
   - Prevents spurious intragenic transcription

3. Enhancer methylation:
   - Inverse correlation: methylation DOWN → enhancer active → target gene UP
   - Requires enhancer-gene linkage (from Hi-C or correlation)

4. CpG shore methylation:
   - Often most variable and tissue-specific
   - Correlations can be positive or negative depending on context

Integration approach:
- Identify DMRs that overlap promoters of differentially expressed genes
- Concordant changes (hypermethylation + downregulation, or vice versa)
  suggest methylation-driven regulation
- Discordant changes suggest other regulatory mechanisms dominate
```

---

## Phase 7: Cell-Type Deconvolution from Methylation

### EpiDISH

```r
library(EpiDISH)

# Reference-based deconvolution
# Uses reference methylation profiles for known cell types

# Blood cell-type deconvolution (Houseman method)
# Using centDHSbloodDMC.m reference (blood cell types)
frac <- epidish(
  beta.m = betas,          # sample beta values matrix
  ref.m = centDHSbloodDMC.m,  # reference profiles
  method = "RPC"           # Robust Partial Correlation
)$estF

# Alternative methods:
# method = "CBS" — Constrained projection (Houseman)
# method = "CP"  — Cibersort-like

# Cell types estimated (blood):
# CD8T, CD4T, NK, Bcell, Mono, Neutrophil (Gran)

# Visualization
barplot(t(frac), col = rainbow(ncol(frac)), legend = TRUE,
        main = "Cell-type composition from methylation")
```

### MethylCIBERSORT

```r
# MethylCIBERSORT: tumor immune microenvironment deconvolution
# Specialized reference profiles for tumor-infiltrating immune cells

# Step 1: Generate signature matrix from reference methylation profiles
# Step 2: Run CIBERSORT deconvolution
# Requires CIBERSORT license for full version

# Simplified approach with EpiDISH tumor reference:
library(EpiDISH)
# Using tumor-specific reference profiles
# centBloodSub.m for blood cell subtypes
frac <- epidish(
  beta.m = tumor_betas,
  ref.m = centBloodSub.m,
  method = "RPC"
)$estF

# Tumor purity estimation:
# If immune fraction is estimated, purity = 1 - sum(immune fractions)
```

### Deconvolution QC

```
Quality checks:
- [ ] Cell-type fractions sum to ~1.0 (within 0.05)
- [ ] No negative fractions (constraint violation)
- [ ] Expected cell types present for tissue type
- [ ] Fractions correlate with FACS data (if available)
- [ ] Batch effects not driving composition differences

Caveats:
- Reference profiles must match cell types in sample
- Works best for blood and blood-derived tissues
- Tumor deconvolution less reliable (mixed tumor + immune)
- Low accuracy for rare cell types (<5% abundance)
- Different reference panels give different results
```

---

## Phase 8: Imprinting and Allele-Specific Methylation

### Allele-Specific Methylation Detection

```python
import pysam
import numpy as np
from collections import defaultdict

def detect_allele_specific_methylation(bam_path, vcf_path, methylation_bed):
    """
    Detect allele-specific methylation using heterozygous SNPs.

    Approach:
    1. Find heterozygous SNPs in the methylation data
    2. Assign reads to alleles based on SNP genotype
    3. Compare methylation between alleles
    """
    # Load heterozygous SNPs
    vcf = pysam.VariantFile(vcf_path)
    het_snps = {}
    for rec in vcf:
        gt = rec.samples[0]["GT"]
        if gt == (0, 1) or gt == (1, 0):
            het_snps[(rec.chrom, rec.pos)] = (rec.ref, rec.alts[0])

    # For each CpG near a het SNP, separate reads by allele
    bam = pysam.AlignmentFile(bam_path, "rb")

    allele_meth = defaultdict(lambda: {"ref": [], "alt": []})

    for (chrom, pos), (ref, alt) in het_snps.items():
        for read in bam.fetch(chrom, pos - 1, pos):
            # Determine allele
            read_base = get_base_at_position(read, pos)
            if read_base == ref:
                allele = "ref"
            elif read_base == alt:
                allele = "alt"
            else:
                continue

            # Get methylation calls for CpGs on this read
            cpg_meth = extract_cpg_methylation(read, chrom)
            for cpg_pos, meth_status in cpg_meth:
                allele_meth[(chrom, cpg_pos)][allele].append(meth_status)

    # Test for allele-specific methylation
    results = []
    for (chrom, pos), data in allele_meth.items():
        if len(data["ref"]) >= 5 and len(data["alt"]) >= 5:
            ref_meth = np.mean(data["ref"])
            alt_meth = np.mean(data["alt"])
            diff = abs(ref_meth - alt_meth)
            if diff > 0.3:  # 30% difference threshold
                results.append({
                    "chrom": chrom, "pos": pos,
                    "ref_methylation": ref_meth,
                    "alt_methylation": alt_meth,
                    "difference": diff
                })

    return pd.DataFrame(results)
```

### Known Imprinted Regions (Human)

| Gene/Region | Chr | Expressed Allele | Methylated Allele | Clinical Significance |
|-------------|-----|-----------------|-------------------|----------------------|
| **H19/IGF2** | 11p15.5 | H19: maternal, IGF2: paternal | ICR: paternal | Beckwith-Wiedemann, Silver-Russell |
| **SNRPN/UBE3A** | 15q11.2 | SNRPN: paternal, UBE3A: maternal | SNRPN: maternal | Prader-Willi, Angelman |
| **MEST** | 7q32.2 | Paternal | Maternal | Growth regulation |
| **PLAGL1** | 6q24 | Paternal | Maternal | Transient neonatal diabetes |
| **KCNQ1OT1** | 11p15.5 | Paternal | Maternal | Beckwith-Wiedemann |
| **GRB10** | 7p12.1 | Maternal (brain) | Paternal | Growth regulation |

---

## Phase 9: Visualization

### Methylation Heatmaps

```r
library(pheatmap)

# Select top DMRs or variable CpGs
top_cpgs <- rownames(head(sig_results, 100))
meth_matrix <- betas[top_cpgs, ]

# Annotation
annotation_col <- data.frame(
  Group = pheno$group,
  row.names = colnames(meth_matrix)
)

# Plot heatmap
pheatmap(
  meth_matrix,
  annotation_col = annotation_col,
  clustering_method = "ward.D2",
  clustering_distance_rows = "euclidean",
  color = colorRampPalette(c("blue", "white", "red"))(100),
  show_rownames = FALSE,
  main = "Top 100 DMRs"
)
```

### Genome Browser Tracks

```bash
# Convert methylation to bigWig for genome browser
# bedGraph to bigWig
sort -k1,1 -k2,2n methylation.bedGraph > sorted.bedGraph
bedGraphToBigWig sorted.bedGraph chromsizes.txt methylation.bw

# View in IGV or UCSC Genome Browser
# Color scale: blue (unmethylated) to red (methylated)
```

### Volcano Plot

```r
library(ggplot2)

# DMR volcano plot
ggplot(dmr_results, aes(x = meth_diff, y = -log10(qvalue))) +
  geom_point(aes(color = significant), alpha = 0.5) +
  scale_color_manual(values = c("grey" = "grey60", "hyper" = "red", "hypo" = "blue")) +
  geom_hline(yintercept = -log10(0.05), linetype = "dashed") +
  geom_vline(xintercept = c(-0.25, 0.25), linetype = "dashed") +
  labs(x = "Methylation difference", y = "-log10(q-value)",
       title = "Differential Methylation") +
  theme_minimal()
```

---

## Decision Trees

### Overall Methylation Analysis Strategy

```
Input: Methylation data
│
├── What data type?
│   ├── WGBS/RRBS/EM-seq FASTQ
│   │   ├── Align: Bismark or bwa-meth
│   │   ├── Extract: bismark_methylation_extractor or MethylDackel
│   │   └── DMR calling: methylKit, bsseq, dmrseq
│   │
│   ├── EPIC/450K IDAT files
│   │   ├── Process: minfi or sesame
│   │   ├── Normalize: Noob, Funnorm, or Quantile
│   │   ├── DMR calling: DMRcate, bumphunter
│   │   └── Deconvolution: EpiDISH
│   │
│   └── Nanopore
│       └── Use long-read-sequencing skill
│
├── Coverage sufficient?
│   ├── WGBS: ≥5x per CpG in ≥80% of CpGs → proceed
│   ├── RRBS: ≥10x per CpG at target regions → proceed
│   └── Insufficient → consider array or increase sequencing
│
├── DMR detection
│   ├── Two groups, replicates → methylKit, bsseq, dmrseq
│   ├── Complex design → limma-based (DMRcate)
│   ├── No replicates → methylKit (no statistics, descriptive only)
│   └── Time series → linear mixed models
│
├── Annotation
│   ├── CpG context: island, shore, shelf, open sea
│   ├── Genomic feature: promoter, gene body, enhancer, intergenic
│   └── Functional: overlap with TF binding, histone marks
│
├── Integration
│   ├── Expression → methylation-expression correlation
│   ├── Hi-C → methylation at TAD boundaries
│   └── Variants → allele-specific methylation
│
└── Deconvolution (if bulk tissue)
    ├── Blood → EpiDISH with blood reference
    ├── Tumor → MethylCIBERSORT or EpiDISH with tumor reference
    └── Other tissues → custom reference required
```

### DMR Caller Selection Tree

```
Which DMR caller?
│
├── Data type?
│   ├── Sequencing (WGBS/RRBS/EM-seq)
│   │   ├── Quick analysis → methylKit (tiles)
│   │   ├── Low coverage (<10x) → bsseq/BSmooth (smoothing helps)
│   │   ├── Rigorous stats → dmrseq (permutation-based)
│   │   └── Complex design → limma + custom regions
│   │
│   └── Array (EPIC/450K)
│       ├── Standard two-group → DMRcate
│       ├── Complex design → DMRcate with limma
│       └── Quick look → bumphunter
│
├── Number of replicates?
│   ├── n ≥ 3 per group → any method
│   ├── n = 2 per group → bsseq or dmrseq (handle small n)
│   └── n = 1 per group → descriptive only (no p-values)
│
└── Priority?
    ├── Speed → methylKit
    ├── Statistical rigor → dmrseq
    ├── Smooth profiles → bsseq
    └── Array + sequencing unified → DMRcate
```

---

## Troubleshooting

```
Low mapping rate (<50%):
├── Adapter contamination → trim with Trim Galore
├── Wrong genome → verify species, assembly version
├── Over-conversion → check spike-in conversion rate
└── Poor read quality → check FASTQ quality scores

High duplicate rate (>30% for WGBS):
├── Low library complexity → increase input DNA
├── Over-amplification → reduce PCR cycles
└── RRBS: expected at MspI sites → use deduplication

Bisulfite conversion <98%:
├── Check non-CpG methylation (CHG/CHH)
│   ├── If CHG/CHH >2% in mammals → conversion problem
│   └── If CHG/CHH <1% → conversion OK, recalculate
├── Check lambda spike-in → should be 0% methylated
└── Reagent quality → fresh bisulfite solution, check pH

Few DMRs detected:
├── Low statistical power → increase replicates
├── Thresholds too strict → relax to 15% difference, FDR 0.1
├── Low coverage → merge nearby CpGs, use smoothing
└── Biology: subtle differences → use more sensitive method (dmrseq)

Batch effects:
├── Check PCA → samples clustering by batch?
├── ComBat correction → limma::removeBatchEffect or sva::ComBat
├── Include batch in model → design = ~ batch + group
└── Array: check chip position effects → normalize with Funnorm
```

## Completeness Checklist

- [ ] Protocol identified (WGBS/RRBS/EM-seq/Array)
- [ ] Alignment completed (Bismark/bwa-meth) with QC
- [ ] Bisulfite conversion rate verified (>99%)
- [ ] M-bias checked and corrected if needed
- [ ] Coverage filtered (≥5x per CpG)
- [ ] DMRs detected with appropriate tool
- [ ] DMRs annotated (CpG context, genomic features)
- [ ] Methylation-expression integration (if RNA-seq available)
- [ ] Cell-type deconvolution performed (if bulk tissue)
- [ ] Visualization: heatmaps, volcano plots, browser tracks
- [ ] Allele-specific methylation checked (if phased data available)
- [ ] Imprinting regions assessed (if relevant)
