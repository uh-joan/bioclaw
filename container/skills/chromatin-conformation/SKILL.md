---
name: chromatin-conformation
description: Hi-C and 3D chromatin conformation analyst. Processes Hi-C, Micro-C, and related chromosome conformation capture data to map 3D genome organization. Contact matrix generation, normalization (ICE/KR), TAD detection, loop calling, A/B compartment analysis, differential Hi-C. Use when user mentions Hi-C, 3D genome, chromatin conformation, chromosome conformation capture, contact matrix, TADs, topologically associating domains, chromatin loops, A/B compartments, insulation score, cooler, Juicer, HiCExplorer, cooltools, compartment analysis, loop calling, HiCCUPS, APA analysis, aggregate peak analysis, Micro-C, 3C, 4C, 5C, cis/trans ratio, contact decay, interaction frequency, or 3D chromatin architecture.
---

# Hi-C and 3D Chromatin Conformation Analysis

Analysis of three-dimensional genome organization from Hi-C and related chromosome conformation capture experiments. Covers the full pipeline from raw reads to biological interpretation: alignment, contact matrix generation, normalization, feature detection (TADs, loops, compartments), differential analysis, and integration with epigenomic data.

## Report-First Workflow

1. **Create report file immediately**: `[sample]_hic_analysis_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as analysis proceeds
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill
- ChIP-seq peak calling and motif analysis -> use appropriate ChIP-seq skill
- Gene expression analysis -> use RNA-seq or single-cell-analysis skill
- Methylation at TAD boundaries -> use methylation-analysis skill (then integrate)
- ATAC-seq open chromatin -> use appropriate ATAC-seq skill

## Cross-Reference: Other Skills
- **Methylation at TAD boundaries** -> use methylation-analysis skill
- **Gene expression in compartments** -> use RNA-seq or single-cell-analysis skill
- **Structural variants from long reads** -> use long-read-sequencing skill
- **Splicing changes at TAD disruptions** -> use alternative-splicing skill

---

## Hi-C Protocol Overview

### Experimental Workflow

```
Cells → Crosslink (formaldehyde) → Restriction digest (DpnII/MboI/HindIII)
→ Proximity ligation → Reverse crosslink → Purify DNA → Sequence (PE 50-150 bp)
```

### Protocol Variants

| Protocol | Resolution | Fragmentation | Best For |
|----------|-----------|---------------|---------|
| **Hi-C (standard)** | 5-40 kb | Restriction enzyme (DpnII, MboI) | Genome-wide 3D structure |
| **Micro-C** | 1 kb (nucleosome) | MNase digestion | Ultra-high resolution, nucleosome contacts |
| **Hi-C 3.0** | 1-5 kb | DpnII + DdeI dual enzyme | Improved loop detection |
| **Capture Hi-C** | 1-5 kb at targets | Oligo capture enrichment | Promoter-enhancer interactions at specific loci |
| **PLAC-seq / HiChIP** | 1-5 kb | ChIP enrichment + proximity ligation | Protein-centric interactions (e.g., H3K27ac loops) |

### Sequencing Depth Guidelines

| Goal | Minimum Depth | Recommended | Resolution Achievable |
|------|--------------|-------------|----------------------|
| Compartments (A/B) | 50M read pairs | 100M | 100-250 kb |
| TADs | 100M read pairs | 300M | 25-40 kb |
| Loops | 300M read pairs | 1B+ | 5-10 kb |
| Micro-C fine structure | 500M read pairs | 2B+ | 1 kb |

---

## Phase 1: Read Alignment and Pair Processing

### Alignment Strategy

Hi-C reads contain chimeric junctions from proximity ligation. Standard aligners can handle this with appropriate settings.

```bash
# === Option A: BWA-MEM with chimeric read handling ===
# Align each mate independently for chimeric read recovery
bwa mem -5SP -t 16 reference.fa reads_R1.fastq.gz reads_R2.fastq.gz \
  | samtools view -bhS - > aligned.bam

# Parse alignments to extract Hi-C pairs
# Using pairtools (recommended pipeline)
pairtools parse \
  --min-mapq 30 \
  --walks-policy 5unique \
  --max-inter-align-gap 30 \
  --chroms-path chromsizes.txt \
  aligned.bam \
  -o parsed.pairs.gz

# === Option B: HiC-Pro pipeline ===
# Config file: config-hicpro.txt
# HiC-Pro handles alignment, filtering, and matrix generation end-to-end
HiC-Pro -i rawdata/ -o results/ -c config-hicpro.txt

# === Option C: Juicer pipeline ===
juicer.sh -d /path/to/experiment \
  -g hg38 \
  -s DpnII \
  -z reference.fa \
  -p chromsizes.txt \
  -y restriction_sites_DpnII.txt \
  -t 16
```

### BWA-MEM Flags Explained

| Flag | Purpose |
|------|---------|
| `-5` | For split alignments, mark the shorter split as supplementary |
| `-S` | Skip mate rescue (not appropriate for Hi-C chimeric pairs) |
| `-P` | Skip pairing — mates are aligned independently |
| `-t 16` | Number of threads |

### Pair Deduplication and Filtering

```bash
# Sort pairs by genomic coordinates
pairtools sort --nproc 8 parsed.pairs.gz -o sorted.pairs.gz

# Mark and remove PCR duplicates
pairtools dedup \
  --max-mismatch 3 \
  --mark-dups \
  --output-stats dedup_stats.txt \
  sorted.pairs.gz \
  -o deduped.pairs.gz

# Filter: keep only uniquely mapped, non-duplicate pairs
pairtools select \
  '(pair_type == "UU") or (pair_type == "UR") or (pair_type == "RU")' \
  deduped.pairs.gz \
  -o filtered.pairs.gz

# Generate contact pairs index
pairix filtered.pairs.gz
```

### Pair Classification

| Pair Type | Meaning | Action |
|-----------|---------|--------|
| `UU` | Both mates uniquely mapped | Keep |
| `UR`/`RU` | One unique, one rescued | Keep (optional) |
| `DD` | PCR duplicate | Remove |
| `NN` | Neither mate mapped | Remove |
| `NM`/`MN` | One unmapped | Remove |
| `WW` | Walk (multiple ligations) | Parse or remove |

---

## Phase 2: Quality Control

### Essential QC Metrics

```bash
# Generate comprehensive QC stats with pairtools
pairtools stats filtered.pairs.gz -o qc_stats.txt

# Key metrics to extract:
# 1. Total reads → alignment rate
# 2. Unique valid pairs / total reads
# 3. Cis/trans ratio
# 4. Duplicate rate
# 5. Distance-dependent contact frequency
```

### QC Interpretation Table

| Metric | Good | Acceptable | Poor | Notes |
|--------|------|-----------|------|-------|
| **Alignment rate** | >90% | 70-90% | <70% | Low = contamination or poor quality |
| **Valid pair rate** | >50% | 30-50% | <30% | Fraction of aligned reads yielding valid pairs |
| **Duplicate rate** | <20% | 20-40% | >40% | High = low library complexity |
| **Cis/trans ratio** | >2.0 | 1.5-2.0 | <1.5 | Low cis/trans = poor crosslinking or ligation |
| **Cis >20 kb fraction** | >40% | 25-40% | <25% | Long-range cis contacts; low = dangling ends |
| **Short-range (<1 kb) cis** | <10% | 10-20% | >20% | High = undigested/self-ligation |

### Distance-Dependent Contact Decay (P(s) Curve)

```python
import cooler
import cooltools
import matplotlib.pyplot as plt
import numpy as np

# Load contact matrix
clr = cooler.Cooler("sample.mcool::resolutions/10000")

# Compute expected contact frequency vs genomic distance
expected = cooltools.expected_cis(
    clr,
    view_df=cooltools.lib.make_cooler_view(clr),
    nproc=8,
    chunksize=1_000_000
)

# Plot P(s) curve
fig, ax = plt.subplots(1, 1, figsize=(8, 6))
for chrom_data in expected.groupby("region1"):
    name, df = chrom_data
    ax.loglog(df["dist"], df["balanced.avg"], alpha=0.5, linewidth=0.5)

ax.set_xlabel("Genomic distance (bp)")
ax.set_ylabel("Contact frequency")
ax.set_title("P(s) — Distance-Dependent Contact Decay")
plt.savefig("ps_curve.png", dpi=150)
```

### P(s) Curve Interpretation

```
Expected behavior:
- Power-law decay: P(s) ~ s^(-1) for distances 100 kb - 10 Mb
- Slope around -1.0 to -1.2 in log-log space

Diagnostic patterns:
- Slope flatter than -0.8: excessive short-range contacts (poor digestion)
- Slope steeper than -1.5: over-digestion or poor ligation
- Bump at ~200 bp (Micro-C): nucleosome-nucleosome contacts (expected)
- Plateau at long distances: noise floor reached, need more sequencing
```

---

## Phase 3: Contact Matrix Generation

### Cooler Format (Recommended)

```bash
# Generate .cool matrix from pairs file
cooler cload pairs \
  chromsizes.txt:1000 \
  filtered.pairs.gz \
  sample_1kb.cool \
  --columns 2 3 4 5 \
  --assembly hg38

# Create multi-resolution cooler (.mcool)
cooler zoomify \
  --balance \
  --resolutions 1000,5000,10000,25000,50000,100000,250000,500000,1000000 \
  --nproc 8 \
  sample_1kb.cool \
  -o sample.mcool

# Alternatively, load from pairs using cooler load
cooler load \
  -f pairs \
  --count-as-float \
  chromsizes.txt:10000 \
  filtered.pairs.gz \
  sample_10kb.cool
```

### Juicer .hic Format

```bash
# Generate .hic file from pairs
java -Xmx48g -jar juicer_tools.jar pre \
  --threads 16 \
  filtered.pairs.txt \
  sample.hic \
  chromsizes.txt

# Convert between formats
# .hic to .cool
hic2cool convert sample.hic sample.mcool -r 0
# .cool to .hic
cooler dump --join sample.cool | \
  java -jar juicer_tools.jar pre - sample.hic chromsizes.txt
```

### Format Comparison

| Feature | cooler (.cool/.mcool) | Juicer (.hic) |
|---------|----------------------|--------------|
| **Backend** | HDF5 | Custom binary |
| **Python API** | cooler, cooltools | hic-straw |
| **Multi-resolution** | .mcool (zoomify) | Built-in |
| **Normalization** | ICE (iterative_correction), built-in | KR, VC, VC_SQRT |
| **Tool ecosystem** | cooltools, chromosight | Juicer, HiCCUPS |
| **Random access** | Fast (HDF5 chunked) | Fast |
| **Recommended for** | Python workflows, cooltools | Java/Juicer workflows |

---

## Phase 4: Matrix Normalization

### Normalization Methods

```python
import cooler
import numpy as np

# === ICE (Iterative Correction and Eigenvector decomposition) ===
# Applied during cooler zoomify --balance, or manually:
cooler.balance_cooler(
    cooler.Cooler("sample.mcool::resolutions/10000"),
    cis_only=True,
    mad_max=5,        # filter bins with extreme coverage (MAD threshold)
    min_nnz=10,       # minimum non-zero contacts per bin
    min_count=0,      # minimum total count per bin
    ignore_diags=2,   # ignore first 2 diagonals
    tol=1e-5,         # convergence tolerance
    max_iters=200,
    store=True,
    store_name="weight"
)

# Access balanced matrix
clr = cooler.Cooler("sample.mcool::resolutions/10000")
mat = clr.matrix(balance=True).fetch("chr1:0-10000000")
```

```bash
# === KR (Knight-Ruiz) normalization — via Juicer ===
java -jar juicer_tools.jar addNorm \
  -k KR \
  sample.hic

# === VC (Vanilla Coverage) normalization ===
java -jar juicer_tools.jar addNorm \
  -k VC \
  sample.hic
```

### Normalization Method Comparison

| Method | Algorithm | Strengths | Limitations |
|--------|-----------|----------|-------------|
| **ICE** | Iterative matrix balancing | Robust, handles variable coverage, standard for cooltools | Assumes equal visibility; struggles with extreme CNVs |
| **KR** | Matrix balancing (Sinkhorn-like) | Fast convergence, mathematically equivalent to ICE | Requires connected matrix |
| **VC** | Divide by sqrt(row_sum * col_sum) | Simple, fast | Over-corrects high-coverage regions |
| **VC_SQRT** | Divide by sqrt(sqrt(row_sum * col_sum)) | Gentler correction than VC | Less rigorous |

### When to Use Each

```
Default choice: ICE (via cooler balance)
- Works for most Hi-C datasets
- Standard in cooltools ecosystem

Use KR when:
- Working within Juicer ecosystem
- Need fast normalization for very large matrices

Avoid VC/VC_SQRT:
- Generally inferior to ICE/KR
- Only use for backward compatibility

Special cases:
- Allele-specific Hi-C: normalize each haplotype independently
- Cancer samples with CNVs: use OneD or HiCNorm (CNV-aware)
- Cross-sample comparison: ensure consistent bin filtering
```

---

## Phase 5: TAD Detection

### Method 1: Insulation Score (Recommended)

```python
import cooltools
import cooler
import pandas as pd
import numpy as np

clr = cooler.Cooler("sample.mcool::resolutions/25000")

# Compute insulation score
insulation_df = cooltools.insulation(
    clr,
    window_bp=[100_000, 250_000, 500_000],  # multiple window sizes
    nproc=8,
    verbose=True
)

# Identify TAD boundaries (minima of insulation score)
# Boundaries are positions where insulation score has a local minimum
boundaries = insulation_df[insulation_df["is_boundary_250000"] == True]

# Boundary strength = depth of insulation score valley
# Stronger boundaries have more negative log2 insulation scores
strong_boundaries = boundaries[boundaries["boundary_strength_250000"] > 0.5]

print(f"Total boundaries (250 kb window): {len(boundaries)}")
print(f"Strong boundaries: {len(strong_boundaries)}")
```

### Insulation Score Parameter Guide

| Parameter | Values | Effect |
|-----------|--------|--------|
| **window_bp** | 100 kb - 1 Mb | Smaller = more boundaries (finer TADs); Larger = fewer (major TADs) |
| **Resolution** | 10-50 kb | Must be ≤ window_bp / 5; finer resolution = more precise boundaries |
| **boundary_strength threshold** | 0.1-1.0 | Higher = only strongest boundaries retained |

### Method 2: TopDom

```bash
# R-based TAD caller
# Input: Hi-C matrix in dense format + bin coordinates
Rscript -e '
library(TopDom)
# Load matrix and bins
td <- TopDom(matrix.file = "hic_matrix_25kb.txt",
             window.size = 5)  # 5 bins = 125 kb at 25 kb resolution
# Output: domains and boundaries
write.table(td$domain, "topdom_domains.bed", sep="\t", quote=FALSE)
write.table(td$bed, "topdom_boundaries.bed", sep="\t", quote=FALSE)
'
```

### Method 3: HiCExplorer

```bash
# Find TADs using HiCExplorer
hicFindTADs \
  --matrix sample_25kb.cool \
  --outPrefix sample_tads \
  --correctForMultipleTesting fdr \
  --minDepth 150000 \
  --maxDepth 600000 \
  --step 75000 \
  --thresholdComparisons 0.05 \
  --delta 0.01 \
  --numberOfProcessors 8

# Output files:
# sample_tads_domains.bed     — TAD coordinates
# sample_tads_boundaries.bed  — boundary positions
# sample_tads_score.bedgraph  — insulation scores
# sample_tads_zscore.bedgraph — z-normalized scores
```

### Method 4: Armatus

```bash
# Armatus: multiscale TAD detection using dynamic programming
armatus -i sample_25kb.cool \
  -g 1.0 \
  -r 25000 \
  -o armatus_tads

# -g: gamma parameter (higher = larger TADs)
# Typical range: 0.5-2.0
```

### TAD Caller Comparison

| Method | Approach | Resolution | Strengths | Notes |
|--------|----------|-----------|----------|-------|
| **Insulation score** | Sliding diamond | 10-50 kb | Simple, interpretable, tunable window | Default recommendation |
| **TopDom** | Statistical change-point | 25-50 kb | Fast, few parameters | Good for quick analysis |
| **HiCExplorer** | Multi-scale insulation | 10-50 kb | Full pipeline, many QC tools | Feature-rich but complex |
| **Armatus** | Dynamic programming | 10-50 kb | Optimal segmentation, multi-scale | Gamma parameter tuning needed |

### TAD QC Checklist

```
- [ ] TAD sizes follow expected distribution (median 0.5-2 Mb for mammalian cells)
- [ ] Boundaries enriched for CTCF (if ChIP-seq available)
- [ ] Boundaries enriched for active histone marks (H3K4me3, H3K36me3)
- [ ] Insulation score distribution is bimodal (boundary vs interior)
- [ ] Nested TAD structure visible at finer resolutions
- [ ] Known locus-specific TADs are recovered (positive controls)
- [ ] Boundary count scales appropriately with window size
```

---

## Phase 6: Chromatin Loop / Interaction Calling

### Method 1: cooltools.dots() (Recommended for cooler)

```python
import cooltools
import cooler
import bioframe

clr = cooler.Cooler("sample.mcool::resolutions/10000")

# Compute expected for normalization
view_df = cooltools.lib.make_cooler_view(clr)
expected = cooltools.expected_cis(clr, view_df=view_df, nproc=8)

# Call dots (loops)
dots = cooltools.dots(
    clr,
    expected=expected,
    view_df=view_df,
    max_loci_separation=10_000_000,  # max loop size (10 Mb)
    max_nans_tolerated=1,
    nproc=8
)

# Filter significant loops
# FDR correction already applied
significant_loops = dots[dots["la_exp.lowleft.qval"] < 0.1]

print(f"Loops called: {len(significant_loops)}")
print(f"Median loop size: {(significant_loops['end2'] - significant_loops['start1']).median() / 1000:.0f} kb")
```

### Method 2: chromosight

```bash
# Pattern-based loop detection (template matching)
chromosight detect \
  --pattern loops \
  --min-dist 20000 \
  --max-dist 2000000 \
  --threads 8 \
  --pearson 0.4 \
  sample_10kb.cool \
  chromosight_loops

# Also detects other patterns:
# --pattern borders    (TAD boundaries)
# --pattern hairpins   (stripe/flame patterns)
# --pattern stripes    (architectural stripes)
```

### Method 3: HiCCUPS (Juicer)

```bash
# GPU-accelerated loop calling
java -Xmx64g -jar juicer_tools.jar hiccups \
  --threads 8 \
  --cpu \
  -r 5000,10000,25000 \
  -k KR \
  -f 0.1,0.1,0.1 \
  -p 2,4,2 \
  -i 7,5,3 \
  -d 20000,20000,50000 \
  sample.hic \
  hiccups_output/

# Parameters:
# -r: resolutions to analyze
# -k: normalization (KR recommended)
# -f: FDR threshold per resolution
# -p: peak width
# -i: window size for neighborhood
# -d: minimum distance between loop anchors
```

### Loop Caller Comparison

| Method | Input Format | Speed | Strengths | Best For |
|--------|-------------|-------|----------|---------|
| **cooltools.dots()** | .cool/.mcool | Moderate | Statistical rigor, cooltools ecosystem | Python workflows |
| **chromosight** | .cool | Fast | Template matching, detects multiple pattern types | Exploratory, pattern discovery |
| **HiCCUPS** | .hic | Fast (GPU) | Gold standard, well-validated | Publication-ready loop lists |

### APA (Aggregate Peak Analysis)

```python
import cooltools
import cooler
import matplotlib.pyplot as plt
import numpy as np

clr = cooler.Cooler("sample.mcool::resolutions/10000")

# Load loop coordinates (BED-like: chrom1, start1, end1, chrom2, start2, end2)
import pandas as pd
loops = pd.read_csv("loops.bedpe", sep="\t",
                     names=["chrom1","start1","end1","chrom2","start2","end2"])

# Compute APA (pileup of contact signal around loop anchors)
pileup = cooltools.pileup(
    clr,
    features_df=loops,
    view_df=cooltools.lib.make_cooler_view(clr),
    expected_df=expected,
    flank=100_000,  # 100 kb flanking region
    nproc=8
)

# Average across all loops
apa_matrix = np.nanmean(pileup, axis=2)

# Plot APA
fig, ax = plt.subplots(1, 1, figsize=(6, 6))
im = ax.imshow(
    np.log2(apa_matrix),
    cmap="coolwarm",
    vmin=-1, vmax=1
)
ax.set_title("APA — Aggregate Peak Analysis")
plt.colorbar(im, label="log2(observed/expected)")
plt.savefig("apa_plot.png", dpi=150)

# APA score: center pixel / mean of lower-left corner
center = apa_matrix[apa_matrix.shape[0]//2, apa_matrix.shape[1]//2]
corner = np.nanmean(apa_matrix[-5:, :5])
apa_score = center / corner
print(f"APA score: {apa_score:.2f}")  # >1 indicates enrichment at loops
```

### APA Score Interpretation

| APA Score | Interpretation |
|-----------|---------------|
| >2.0 | Strong loop enrichment (excellent) |
| 1.5-2.0 | Moderate enrichment (good) |
| 1.0-1.5 | Weak enrichment (marginal) |
| ~1.0 | No enrichment (loops not validated) |
| <1.0 | Depletion (artifact or wrong loop set) |

---

## Phase 7: A/B Compartment Analysis

### Eigenvector Decomposition

```python
import cooltools
import cooler
import bioframe
import numpy as np
import pandas as pd

clr = cooler.Cooler("sample.mcool::resolutions/100000")

# Get expected for O/E transformation
view_df = cooltools.lib.make_cooler_view(clr)
expected = cooltools.expected_cis(clr, view_df=view_df, nproc=8)

# Compute eigenvectors (A/B compartments)
# GC content or gene density used to orient eigenvector sign
eigvals, eigvecs = cooltools.eigs_cis(
    clr,
    view_df=view_df,
    n_eigs=3,           # compute top 3 eigenvectors
    phasing_track_col="GC",  # orient by GC content
    nproc=8
)

# E1 (first eigenvector) separates A and B compartments
# Positive E1 = A compartment (active, gene-rich, open chromatin)
# Negative E1 = B compartment (inactive, gene-poor, closed chromatin)

# Add to genome annotation
compartments = eigvecs[["chrom", "start", "end", "E1"]].copy()
compartments["compartment"] = np.where(compartments["E1"] > 0, "A", "B")

# Summary statistics
a_fraction = (compartments["compartment"] == "A").mean()
print(f"A compartment: {a_fraction:.1%}")
print(f"B compartment: {1-a_fraction:.1%}")
```

### GC Content Phasing Track

```python
import bioframe

# Fetch GC content for phasing (orients eigenvector sign)
# A compartments correlate with high GC content
bins = clr.bins()[:]
gc_cov = bioframe.frac_gc(bins[["chrom", "start", "end"]],
                           bioframe.load_fasta("hg38.fa"))
bins["GC"] = gc_cov

# Alternatively, use gene density
# A compartments correlate with high gene density
```

### Compartment Strength (Saddle Plot)

```python
import cooltools

# Compute saddle plot — quantifies compartmentalization strength
saddle_data, saddle_binedges = cooltools.saddle(
    clr,
    expected,
    eigvecs["E1"],
    view_df=view_df,
    n_bins=50,
    qrange=(0.02, 0.98)
)

# Visualize saddle plot
import matplotlib.pyplot as plt

fig, ax = plt.subplots(1, 1, figsize=(6, 6))
im = ax.imshow(
    np.log2(saddle_data),
    cmap="coolwarm",
    vmin=-1, vmax=1,
    extent=[saddle_binedges[0], saddle_binedges[-1],
            saddle_binedges[-1], saddle_binedges[0]]
)
ax.set_xlabel("E1 (B ← → A)")
ax.set_ylabel("E1 (B ← → A)")
ax.set_title("Saddle Plot — Compartment Strength")
plt.colorbar(im, label="log2(observed/expected)")
plt.savefig("saddle_plot.png", dpi=150)

# Compartment strength:
# AA/BB enrichment (corners) vs AB depletion (off-diagonal)
# Stronger checkerboard = stronger compartmentalization
```

### Compartment Switching Detection

```python
# Compare compartments between two conditions
comp_cond1 = pd.read_csv("condition1_compartments.tsv", sep="\t")
comp_cond2 = pd.read_csv("condition2_compartments.tsv", sep="\t")

merged = comp_cond1.merge(comp_cond2, on=["chrom", "start", "end"],
                           suffixes=("_c1", "_c2"))

# Detect switching events
merged["switch"] = "stable"
merged.loc[(merged["E1_c1"] > 0) & (merged["E1_c2"] < 0), "switch"] = "A_to_B"
merged.loc[(merged["E1_c1"] < 0) & (merged["E1_c2"] > 0), "switch"] = "B_to_A"

a_to_b = (merged["switch"] == "A_to_B").sum()
b_to_a = (merged["switch"] == "B_to_A").sum()
print(f"A->B switches: {a_to_b}")
print(f"B->A switches: {b_to_a}")

# Biological significance:
# A->B: genes in these regions may be silenced
# B->A: genes in these regions may be activated
# Integrate with RNA-seq to confirm expression changes
```

---

## Phase 8: Differential Hi-C Analysis

### multiHiCcompare

```r
library(multiHiCcompare)

# Load Hi-C data for multiple replicates per condition
# Input: sparse upper-triangular matrices (chr, start1, start2, IF)
hicexp <- make_hicexp(
  data_list = list(ctrl_rep1, ctrl_rep2, treat_rep1, treat_rep2),
  groups = c(0, 0, 1, 1),
  zero.p = 0.8,       # filter bins with >80% zeros
  A.min = 5            # minimum average count
)

# Joint normalization (cyclic loess)
hicexp <- cyclic_loess(hicexp, verbose = TRUE, parallel = TRUE)

# Differential interaction detection
hicexp <- hic_exactTest(hicexp)

# Extract results
results <- results(hicexp)
sig_interactions <- results[results$p.adj < 0.05, ]

# Summary
cat("Significant differential interactions:", nrow(sig_interactions), "\n")
cat("Gained:", sum(sig_interactions$logFC > 0), "\n")
cat("Lost:", sum(sig_interactions$logFC < 0), "\n")
```

### SELFISH (Self-similarity-based method)

```python
# SELFISH: finds differential interactions based on local similarity
# Compares contact matrices using self-similarity metric
import selfish

# Load two Hi-C matrices (dense numpy arrays, same resolution)
mat1 = np.load("condition1_chr1_25kb.npy")
mat2 = np.load("condition2_chr1_25kb.npy")

# Run SELFISH
diff_matrix = selfish.selfish(mat1, mat2, resolution=25000)

# Significant differences have high SELFISH score
```

### dcHiC (Differential Compartment Analysis)

```bash
# dcHiC: specifically designed for compartment-level differential analysis
# Detects differential compartments across conditions

# Step 1: Create input config
# sample_name condition  matrix_path  resolution
echo -e "ctrl\tcontrol\tctrl.mcool\t100000" > dcHiC_input.txt
echo -e "treat\ttreatment\ttreat.mcool\t100000" >> dcHiC_input.txt

# Step 2: Run dcHiC
Rscript dcHiC.R \
  --input dcHiC_input.txt \
  --output dcHiC_results/ \
  --genome hg38 \
  --pcatype cis \
  --fdr 0.05

# Output: differential compartment regions with p-values and effect sizes
```

### Differential Analysis Decision Guide

```
Choose multiHiCcompare when:
- Multiple biological replicates per condition (recommended: ≥2)
- Want interaction-level differential analysis
- Working at 25-100 kb resolution
- Need rigorous statistical framework (exact test)

Choose SELFISH when:
- No or few replicates
- Want local region-level differences (not single interactions)
- Working with dense matrices

Choose dcHiC when:
- Specifically interested in compartment-level changes
- Comparing cell types or developmental stages
- Want compartment switching with statistical confidence
```

---

## Phase 9: Integration with Epigenomic Data

### CTCF and Cohesin at TAD Boundaries

```python
import pyBigWig
import numpy as np
import pandas as pd

# Load TAD boundaries
boundaries = pd.read_csv("tad_boundaries.bed", sep="\t",
                          names=["chrom", "start", "end"])

# Load ChIP-seq signal (bigWig)
bw_ctcf = pyBigWig.open("CTCF_ChIP.bw")
bw_h3k4me3 = pyBigWig.open("H3K4me3_ChIP.bw")

# Aggregate signal around boundaries
flank = 500_000  # 500 kb flanking
n_bins = 100

profile_ctcf = np.zeros(n_bins)
profile_h3k4me3 = np.zeros(n_bins)

for _, row in boundaries.iterrows():
    center = (row["start"] + row["end"]) // 2
    start = center - flank
    end = center + flank
    if start < 0:
        continue
    try:
        vals_ctcf = bw_ctcf.values(row["chrom"], start, end)
        vals_h3k4 = bw_h3k4me3.values(row["chrom"], start, end)
        # Bin the values
        binned_ctcf = np.nanmean(np.array(vals_ctcf).reshape(n_bins, -1), axis=1)
        binned_h3k4 = np.nanmean(np.array(vals_h3k4).reshape(n_bins, -1), axis=1)
        profile_ctcf += binned_ctcf
        profile_h3k4me3 += binned_h3k4
    except:
        continue

profile_ctcf /= len(boundaries)
profile_h3k4me3 /= len(boundaries)

# Expected: CTCF peaks sharply at boundaries; H3K4me3 enriched at A-compartment side
```

### Histone Marks and Compartments

| Mark | Expected Location | Compartment Association |
|------|------------------|------------------------|
| H3K4me3 | Promoters | A compartment |
| H3K27ac | Active enhancers/promoters | A compartment |
| H3K36me3 | Gene bodies (transcribed) | A compartment |
| H3K9me3 | Constitutive heterochromatin | B compartment |
| H3K27me3 | Polycomb-repressed | B compartment (facultative) |
| CTCF | TAD boundaries, loop anchors | Boundary elements |
| RAD21/SMC3 | Cohesin at loop anchors | Boundary/loop anchors |

---

## Phase 10: Visualization

### Contact Matrix Heatmaps

```python
import cooler
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LogNorm

clr = cooler.Cooler("sample.mcool::resolutions/25000")

# Fetch a region
region = "chr1:50000000-55000000"
mat = clr.matrix(balance=True).fetch(region)

# Plot
fig, ax = plt.subplots(1, 1, figsize=(8, 8))
im = ax.matshow(
    mat,
    cmap="YlOrRd",
    norm=LogNorm(vmin=0.001, vmax=0.1),
    extent=[50, 55, 55, 50]
)
ax.set_xlabel("Position (Mb)")
ax.set_ylabel("Position (Mb)")
ax.set_title(f"Hi-C Contact Matrix — {region}")
plt.colorbar(im, label="Balanced contact frequency", shrink=0.7)
plt.savefig("contact_matrix.png", dpi=150)
```

### HiGlass Interactive Visualization

```bash
# Start HiGlass server with Docker
docker pull higlass/higlass-docker

# Ingest cooler file
docker exec higlass-container python \
  higlass-server/manage.py ingest_tileset \
  --filename /data/sample.mcool \
  --filetype cooler \
  --datatype matrix

# Access at http://localhost:8989
```

### Multi-Track Visualization with HiCExplorer

```bash
# Plot Hi-C matrix with tracks
hicPlotMatrix \
  --matrix sample_25kb.cool \
  --region chr1:50000000-55000000 \
  --log1p \
  --colorMap YlOrRd \
  --dpi 150 \
  --outFileName hic_matrix_plot.png

# Plot TADs on matrix
hicPlotTADs \
  --tracks tracks.ini \
  --region chr1:50000000-55000000 \
  --outFileName tad_plot.png \
  --dpi 150

# tracks.ini example:
# [hic]
# file = sample_25kb.cool
# title = Hi-C
# transform = log1p
# colormap = YlOrRd
#
# [tads]
# file = tad_boundaries.bed
# type = domains
#
# [insulation]
# file = insulation_score.bedgraph
# type = line
#
# [ctcf]
# file = CTCF_ChIP.bw
# type = bigwig
```

---

## Decision Trees

### Overall Analysis Strategy

```
Input: Hi-C paired-end FASTQ files
│
├─ What resolution do you need?
│  ├─ Compartments only → 100 kb, 50M+ read pairs
│  ├─ TADs → 25-50 kb, 100M+ read pairs
│  ├─ Loops → 5-10 kb, 300M+ read pairs
│  └─ Fine structure (Micro-C) → 1 kb, 500M+ read pairs
│
├─ Which pipeline?
│  ├─ Python/cooltools → BWA-MEM + pairtools + cooler + cooltools
│  ├─ Juicer ecosystem → Juicer pipeline + Juicer Tools
│  └─ HiCExplorer → BWA-MEM + HiCExplorer suite
│
├─ QC passed? (cis/trans >2, dup rate <20%)
│  ├─ Yes → proceed
│  └─ No → troubleshoot library
│
├─ Normalization
│  ├─ Standard → ICE (cooler) or KR (Juicer)
│  └─ CNV-affected → OneD or HiCNorm
│
├─ Feature detection
│  ├─ TADs → insulation score (cooltools) or HiCExplorer
│  ├─ Loops → cooltools.dots() or HiCCUPS
│  ├─ Compartments → cooltools.eigs_cis()
│  └─ All of the above
│
├─ Differential analysis?
│  ├─ Interaction-level → multiHiCcompare (need replicates)
│  ├─ Compartment-level → dcHiC
│  └─ Region-level → SELFISH
│
└─ Integration
   ├─ ChIP-seq → boundary/loop anchor enrichment
   ├─ RNA-seq → expression vs compartment/TAD
   └─ Methylation → methylation at boundaries
```

### Troubleshooting Decision Tree

```
Low cis/trans ratio (<1.5):
├─ Check crosslinking: insufficient → increase formaldehyde time/concentration
├─ Check ligation: inefficient → optimize ligation conditions
└─ Check restriction digest: incomplete → try different enzyme or optimize digestion time

High duplicate rate (>40%):
├─ Low library complexity → increase input DNA
├─ Over-amplification → reduce PCR cycles
└─ Shallow sequencing → need more unique molecules, not more reads

Few loops detected:
├─ Insufficient depth → need 300M+ valid pairs for 5-10 kb loops
├─ Wrong resolution → try coarser resolution (10-25 kb)
├─ Normalization artifacts → check ICE weights, filter low-coverage bins
└─ Biology: some cell types have fewer loops (e.g., embryonic cells)

Noisy insulation scores:
├─ Low coverage → increase sequencing depth or use coarser resolution
├─ Window too small → increase insulation window size
└─ Poor normalization → check ICE convergence, filter problematic bins
```

---

## Micro-C Specific Considerations

```
Micro-C differences from standard Hi-C:
- MNase fragmentation instead of restriction enzymes
- Nucleosome-resolution contacts (1 kb achievable)
- Better signal-to-noise for loops and fine structures
- Requires higher sequencing depth (2B+ read pairs for 1 kb resolution)

Pipeline adjustments for Micro-C:
- Alignment: same BWA-MEM -5SP pipeline
- Pair processing: same pairtools workflow
- Resolution: can go to 1 kb (Hi-C typically limited to 5 kb)
- Expected P(s): characteristic nucleosome bump at ~200 bp
- Loop calling: higher sensitivity, more loops detectable
- TADs: sharper boundaries due to better resolution

QC specific to Micro-C:
- MNase digestion control: fragment size ~150 bp (mono-nucleosome)
- Higher cis/trans ratio expected (>3.0)
- Shorter-range cis contacts more prevalent
```

## Completeness Checklist

- [ ] Protocol and enzyme identified (DpnII/MboI/MNase)
- [ ] Alignment with chimeric read handling (BWA-MEM -5SP)
- [ ] Pair processing: parsing, sorting, deduplication (pairtools)
- [ ] QC metrics evaluated: cis/trans ratio, duplicate rate, P(s) curve
- [ ] Contact matrix generated in appropriate format (.cool or .hic)
- [ ] Normalization applied (ICE or KR)
- [ ] TAD boundaries detected and validated (insulation score or alternative)
- [ ] Loops called and APA validation performed
- [ ] A/B compartments computed with saddle plot
- [ ] Integration with ChIP-seq at boundaries (if available)
- [ ] Differential analysis performed (if comparing conditions)
- [ ] Contact matrices and features visualized
