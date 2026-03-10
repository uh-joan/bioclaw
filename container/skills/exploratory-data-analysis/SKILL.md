---
name: exploratory-data-analysis
description: Systematic exploratory data analysis across scientific file formats. File profiling, data quality assessment, distribution analysis, anomaly detection, batch effect identification, QC metrics for genomics, proteomics, imaging, and tabular data. Use when user mentions explore this data, EDA, exploratory data analysis, what's in this file, data quality check, summarize this dataset, profile this data, investigate data quality, initial data exploration, data overview, describe this file, inspect data, data summary, check data quality, file profiling, dataset characterization, or preliminary analysis.
---

# Exploratory Data Analysis

Systematic exploratory data analysis for scientific datasets of any format. The agent writes and executes Python code to profile files, assess data quality, compute summary statistics, detect anomalies, identify batch effects, and generate standardized EDA reports. This is a methodology skill that teaches HOW to explore data, not a tutorial for any single library. Applies a universal protocol adapted to each file format.

## Report-First Workflow

1. **Create report file immediately**: `[dataset]_eda_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Differential expression analysis on RNA-seq count matrices -> use `rnaseq-deseq2`
- ACMG variant classification and pathogenicity scoring -> use `variant-interpretation`
- Pathway enrichment on gene lists -> use `gene-enrichment`
- Single-cell clustering, trajectory, and cell type annotation -> use `single-cell-analysis`
- Statistical modeling, hypothesis testing, regression -> use `statistical-modeling`
- Proteomics quantification and differential abundance -> use `proteomics-analysis`
- Metabolite identification and metabolic pathway mapping -> use `metabolomics-analysis`
- Phylogenetic tree construction and evolutionary analysis -> use `phylogenetics`
- Epigenomic peak calling and differential methylation -> use `epigenomics`
- Structural variant calling and characterization -> use `structural-variant-analysis`

## Cross-Reference: Other Skills

- **Statistical modeling after EDA** -> use statistical-modeling skill
- **Single-cell QC then clustering** -> use single-cell-analysis skill
- **Variant QC then annotation pipeline** -> use variant-analysis skill
- **RNA-seq QC then differential expression** -> use rnaseq-deseq2 skill
- **Proteomics QC then quantification** -> use proteomics-analysis skill
- **Phylogenetic sequence QC then tree building** -> use phylogenetics skill
- **Metabolomics QC then pathway analysis** -> use metabolomics-analysis skill
- **Epigenomic QC then peak analysis** -> use epigenomics skill

## Python Environment

Python 3 with `numpy`, `pandas`, `scipy`, `scikit-learn`, `matplotlib`, `seaborn`, `statsmodels` pre-installed. For specialized formats, install at runtime:

```python
import subprocess
subprocess.run(["pip", "install", "pysam", "scanpy", "pyopenms", "biopython", "tifffile"], check=True)
```

Only install what is needed for the specific file format being analyzed. Do not install all packages upfront.

---

## EDA Decision Tree

Given a file, identify its type and route to the appropriate analysis template. Always start with the Universal EDA Protocol (below), then apply format-specific analysis.

### File Type Routing

```
Input file received
  |
  +-- .csv / .tsv / .xlsx / .parquet
  |     -> Tabular Data EDA
  |
  +-- .fasta / .fa / .fq / .fastq / .fastq.gz
  |     -> Genomic Sequence EDA
  |
  +-- .bam / .sam / .cram
  |     -> Alignment EDA
  |
  +-- .vcf / .vcf.gz / .bcf
  |     -> Variant EDA
  |
  +-- .h5ad / .loom / .mtx (+ barcodes.tsv + genes.tsv)
  |     -> Gene Expression / Single-Cell EDA
  |
  +-- .pdb / .cif / .sdf / .mol / .mol2
  |     -> Molecular Structure EDA
  |
  +-- .mzML / .mgf / .mzXML
  |     -> Spectral / Mass Spec EDA
  |
  +-- .tif / .tiff / .nd2 / .czi / .ome.tif
  |     -> Bioimage EDA
  |
  +-- .bed / .gff / .gff3 / .gtf
  |     -> Genomic Annotation EDA
  |
  +-- Unknown extension
        -> Apply Universal EDA Protocol phases 1-3
        -> Attempt text vs binary detection
        -> If text: try pandas.read_csv with various separators
        -> If binary: check magic bytes for known formats
```

### Per-Format: What to Compute

**Tabular data** (.csv, .tsv, .xlsx):
- Shape (rows x columns)
- Column dtypes (numeric, categorical, datetime, mixed)
- Missing value count and percentage per column
- Univariate distributions for numerics (mean, median, std, min, max, skewness, kurtosis)
- Value counts for categoricals (cardinality, top values, rare categories)
- Pairwise correlation matrix for numerics
- Outlier detection (IQR method and z-score)
- Duplicate row check

**Genomic sequences** (.fasta, .fastq):
- Sequence count
- Length distribution (min, max, mean, median, N50)
- GC content distribution
- Ambiguous base count (N content)
- Quality score distribution (FASTQ only: per-base, per-read mean)
- Adapter contamination hints (common adapter k-mers)
- Duplicate sequence rate (exact match on first 50bp)

**Alignments** (.bam, .sam, .cram):
- Total reads, mapped reads, mapping rate
- Properly paired rate (paired-end only)
- Duplicate rate
- Mapping quality distribution
- Insert size distribution (mean, median, std)
- Coverage per chromosome / per region
- Unmapped read count
- Supplementary / secondary alignment count

**Variants** (.vcf, .bcf):
- Total variant count
- Variant type distribution (SNV, indel, MNV, SV)
- Ts/Tv ratio (transition/transversion)
- Allele frequency spectrum (singleton, doubleton, common)
- Per-sample genotype counts (het, hom-ref, hom-alt, missing)
- FILTER field distribution (PASS rate)
- Chromosome distribution
- QUAL score distribution
- Multi-allelic site count

**Gene expression** (.h5ad, count matrices):
- Number of cells/samples and genes
- Library size distribution (total UMIs/counts per cell)
- Gene detection rate (genes per cell, cells per gene)
- Mitochondrial gene percentage per cell
- Ribosomal gene percentage per cell
- Highest-expressed genes (top 20 by total counts)
- Doublet score distribution (if applicable)
- Sparsity (fraction of zero entries)

**Molecular structures** (.pdb, .sdf, .mol):
- Atom count and element composition
- Bond type distribution (single, double, aromatic)
- Residue/chain count (proteins)
- Resolution and experimental method (PDB)
- Molecular weight
- Heavy atom count
- Lipinski Rule of Five (small molecules): MW, LogP, HBD, HBA
- Ring count and aromatic ring count

**Spectral data** (.mzML, .mgf):
- Spectrum count (MS1, MS2)
- m/z range (min, max)
- Retention time range
- Total ion current distribution
- Base peak intensity distribution
- Precursor ion m/z distribution (MS2)
- Charge state distribution
- Spectra per RT bin (density)

**Bioimages** (.tif, .nd2, .czi):
- Image dimensions (X, Y, Z, C, T)
- Number of channels
- Bit depth (8, 12, 16-bit)
- Pixel size / spatial resolution (if metadata present)
- Intensity histogram per channel
- Min/max/mean intensity per channel
- Saturation check (% pixels at max value)
- Blank frame detection

**Genomic annotations** (.bed, .gff, .gtf):
- Feature count by type (gene, exon, transcript, CDS)
- Chromosome distribution
- Feature length distribution
- Strand distribution (+/-)
- Gene biotype distribution (protein_coding, lncRNA, etc.)
- Overlapping feature count
- Source field distribution
- Attribute completeness (gene_name, gene_id coverage)

---

## Universal EDA Protocol

Apply these seven phases to ANY dataset regardless of format. Each phase builds on the previous.

### Phase 1: Metadata

Gather context before touching the data.

```python
import os, datetime

file_path = "data.csv"  # replace with actual path
stat = os.stat(file_path)
print(f"File: {os.path.basename(file_path)}")
print(f"Size: {stat.st_size / 1e6:.2f} MB")
print(f"Extension: {os.path.splitext(file_path)[1]}")
print(f"Modified: {datetime.datetime.fromtimestamp(stat.st_mtime)}")

# Check if text or binary
with open(file_path, "rb") as f:
    chunk = f.read(8192)
    is_text = not bool(chunk.translate(None, bytearray(range(7,14)) + bytearray(range(32,127)) + b'\r\n\t'))
print(f"Encoding: {'text' if is_text else 'binary'}")
```

Document: file name, size, format, source (if known), creation/modification date, expected contents.

### Phase 2: Structure

Determine the shape and schema of the data.

- **Tabular**: rows, columns, dtypes, index structure
- **Sequences**: count, length range, alphabet
- **Matrices**: dimensions, sparsity, value range
- **Hierarchical**: tree depth, node types, attribute names
- **Images**: dimensions, channels, dtype

Goal: answer "what are the dimensions and types of this data?"

### Phase 3: Completeness

Quantify what is missing or incomplete.

```python
# For tabular data
missing = df.isnull().sum()
missing_pct = (missing / len(df) * 100).round(2)
completeness = pd.DataFrame({
    "missing_count": missing,
    "missing_pct": missing_pct,
    "dtype": df.dtypes
}).sort_values("missing_pct", ascending=False)
print(completeness[completeness["missing_count"] > 0])
```

For non-tabular formats:
- **Sequences**: N content, truncated reads
- **Alignments**: unmapped reads, missing mate pairs
- **Variants**: missing genotypes, no-call rate
- **Expression**: zero-inflation, dropout rate
- **Annotations**: features without gene names or IDs

### Phase 4: Distributions

Summarize each variable or feature independently.

```python
# Numeric columns
desc = df.describe().T
desc["skewness"] = df.select_dtypes("number").skew()
desc["kurtosis"] = df.select_dtypes("number").kurtosis()
print(desc)

# Categorical columns
for col in df.select_dtypes(["object", "category"]).columns:
    print(f"\n--- {col} ---")
    print(f"Unique: {df[col].nunique()}")
    print(df[col].value_counts().head(10))
```

Key questions:
- Are numeric distributions normal, skewed, bimodal, or uniform?
- Are there unexpected value ranges (negative counts, future dates)?
- Do categorical variables have rare levels that should be grouped?
- Are there constant or near-constant columns (zero variance)?

### Phase 5: Relationships

Explore associations between variables.

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Correlation matrix for numeric columns
numeric_df = df.select_dtypes("number")
if numeric_df.shape[1] <= 30:
    corr = numeric_df.corr()
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr, cmap="RdBu_r", center=0, vmin=-1, vmax=1, ax=ax)
    plt.tight_layout()
    plt.savefig("correlation_matrix.png", dpi=150)
    plt.close()
```

For high-dimensional data:
- PCA or UMAP for dimensionality reduction
- Cluster analysis (hierarchical clustering on samples)
- Feature importance via mutual information or variance

### Phase 6: Quality Assessment

Identify technical artifacts and anomalies.

**Always check for:**
1. Batch effects — systematic differences between processing groups
2. Sample swaps — unexpected correlation structure
3. Outlier samples — samples far from the group on QC metrics
4. Technical duplicates — identical or near-identical observations
5. Data entry errors — impossible values, unit mismatches
6. Confounders — variables that correlate with both predictor and outcome

```python
from sklearn.decomposition import PCA
from scipy.stats import median_abs_deviation

# PCA for outlier detection
pca = PCA(n_components=min(10, numeric_df.shape[1]))
pcs = pca.fit_transform(numeric_df.dropna())

# Flag outlier samples (>3 MADs from median on PC1 or PC2)
for i in range(min(2, pcs.shape[1])):
    med = np.median(pcs[:, i])
    mad = median_abs_deviation(pcs[:, i])
    outliers = np.abs(pcs[:, i] - med) > 3 * mad
    if outliers.any():
        print(f"PC{i+1} outliers: {np.where(outliers)[0].tolist()}")
```

### Phase 7: Report Generation

Compile findings into a structured report.

```python
report_sections = [
    "## Dataset Overview",
    "## Data Quality Summary",
    "## Distribution Analysis",
    "## Relationship Analysis",
    "## Anomalies and Concerns",
    "## Recommendations for Next Steps",
]
```

Every EDA report MUST include:
1. One-paragraph dataset summary (what, where, how many)
2. Data quality verdict (clean / minor issues / major concerns)
3. Top 3-5 findings with evidence
4. Specific recommendations for downstream analysis
5. Explicit list of caveats or limitations

---

## Format-Specific EDA Templates

### Template: Tabular Data (pandas DataFrame)

```python
import pandas as pd
import numpy as np

df = pd.read_csv("data.csv")  # or read_excel, read_parquet

# Structure
print(f"Shape: {df.shape}")
print(f"\nDtypes:\n{df.dtypes}")
print(f"\nMemory: {df.memory_usage(deep=True).sum() / 1e6:.1f} MB")

# Completeness
print(f"\nMissing values:\n{df.isnull().sum()[df.isnull().sum() > 0]}")

# Distributions
print(f"\nNumeric summary:\n{df.describe().T}")
print(f"\nCategorical summary:")
for col in df.select_dtypes(["object", "category"]).columns:
    print(f"  {col}: {df[col].nunique()} unique, top={df[col].mode()[0]}")

# Duplicates
print(f"\nDuplicate rows: {df.duplicated().sum()}")

# Correlations (top pairs)
corr = df.select_dtypes("number").corr()
upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
high_corr = [(upper.columns[j], upper.index[i], upper.iloc[i, j])
             for i in range(len(upper)) for j in range(len(upper.columns))
             if abs(upper.iloc[i, j]) > 0.8]
if high_corr:
    print(f"\nHighly correlated pairs (|r| > 0.8):")
    for c1, c2, r in sorted(high_corr, key=lambda x: -abs(x[2])):
        print(f"  {c1} <-> {c2}: {r:.3f}")
```

### Template: VCF Exploration

```python
import pandas as pd
import gzip, re

# Parse VCF (no pysam needed)
opener = gzip.open if vcf_path.endswith(".gz") else open
records = []
with opener(vcf_path, "rt") as f:
    for line in f:
        if line.startswith("#"):
            continue
        parts = line.strip().split("\t", 8)
        chrom, pos, vid, ref, alt, qual, filt = parts[:7]
        records.append({"CHROM": chrom, "POS": int(pos), "REF": ref,
                        "ALT": alt, "QUAL": float(qual) if qual != "." else None,
                        "FILTER": filt})
df = pd.DataFrame(records)

# Variant types
def var_type(ref, alt):
    if len(ref) == 1 and len(alt) == 1: return "SNV"
    elif len(ref) > len(alt): return "DEL"
    elif len(ref) < len(alt): return "INS"
    return "COMPLEX"
df["TYPE"] = df.apply(lambda r: var_type(r.REF, r.ALT), axis=1)
print(f"Total variants: {len(df)}")
print(f"Type distribution:\n{df['TYPE'].value_counts()}")

# Ts/Tv ratio
transitions = {"AG", "GA", "CT", "TC"}
snvs = df[df.TYPE == "SNV"]
ts = snvs.apply(lambda r: r.REF + r.ALT in transitions, axis=1).sum()
tv = len(snvs) - ts
print(f"Ts/Tv ratio: {ts/tv:.2f}" if tv > 0 else "No transversions")

# Chromosome distribution
print(f"\nVariants per chromosome:\n{df['CHROM'].value_counts().head(25)}")
print(f"FILTER distribution:\n{df['FILTER'].value_counts()}")
```

### Template: BAM/CRAM Exploration

```python
import pysam

bam = pysam.AlignmentFile(bam_path, "rb")

total = mapped = paired = proper = dup = supp = 0
mapq_vals = []
isizes = []

for read in bam.fetch(until_eof=True):
    total += 1
    if not read.is_unmapped:
        mapped += 1
        mapq_vals.append(read.mapping_quality)
    if read.is_paired: paired += 1
    if read.is_proper_pair: proper += 1
    if read.is_duplicate: dup += 1
    if read.is_supplementary: supp += 1
    if read.is_proper_pair and not read.is_supplementary and 0 < abs(read.template_length) < 2000:
        isizes.append(abs(read.template_length))

import numpy as np
print(f"Total reads: {total:,}")
print(f"Mapped: {mapped:,} ({mapped/total*100:.1f}%)")
print(f"Properly paired: {proper:,} ({proper/max(paired,1)*100:.1f}%)")
print(f"Duplicates: {dup:,} ({dup/total*100:.1f}%)")
print(f"Supplementary: {supp:,}")
print(f"MAPQ: median={np.median(mapq_vals):.0f}, mean={np.mean(mapq_vals):.1f}")
if isizes:
    print(f"Insert size: median={np.median(isizes):.0f}, mean={np.mean(isizes):.0f}, std={np.std(isizes):.0f}")
bam.close()
```

### Template: AnnData / h5ad Exploration

```python
import scanpy as sc
import numpy as np

adata = sc.read_h5ad(h5ad_path)
print(f"Cells: {adata.n_obs:,}, Genes: {adata.n_vars:,}")
print(f"Obs columns: {list(adata.obs.columns)}")
print(f"Var columns: {list(adata.var.columns)}")
print(f"Layers: {list(adata.layers.keys()) if adata.layers else 'none'}")
print(f"Obsm: {list(adata.obsm.keys()) if adata.obsm else 'none'}")

# QC metrics
adata.var["mt"] = adata.var_names.str.startswith(("MT-", "mt-"))
sc.pp.calculate_qc_metrics(adata, qc_vars=["mt"], inplace=True, percent_top=[20])

print(f"\nTotal counts per cell: median={adata.obs['total_counts'].median():.0f}, "
      f"mean={adata.obs['total_counts'].mean():.0f}")
print(f"Genes per cell: median={adata.obs['n_genes_by_counts'].median():.0f}")
print(f"Mito %: median={adata.obs['pct_counts_mt'].median():.1f}%, "
      f"max={adata.obs['pct_counts_mt'].max():.1f}%")
print(f"Sparsity: {1 - (adata.X.nnz / np.prod(adata.X.shape)):.2%}" if hasattr(adata.X, 'nnz') else "")

# Top expressed genes
sc.pl.highest_expr_genes(adata, n_top=20, save="_top_genes.png", show=False)

# Violin plots of QC
sc.pl.violin(adata, ["n_genes_by_counts", "total_counts", "pct_counts_mt"],
             multi_panel=True, save="_qc_violin.png", show=False)
```

### Template: FASTA/FASTQ Exploration

```python
import gzip
from collections import Counter

opener = gzip.open if fasta_path.endswith(".gz") else open
is_fastq = any(fasta_path.endswith(ext) for ext in [".fastq", ".fq", ".fastq.gz", ".fq.gz"])

lengths, gc_contents, quals = [], [], []
seq_count = 0

with opener(fasta_path, "rt") as f:
    if is_fastq:
        while True:
            header = f.readline().strip()
            if not header: break
            seq = f.readline().strip()
            f.readline()  # +
            qual = f.readline().strip()
            seq_count += 1
            lengths.append(len(seq))
            gc = (seq.count("G") + seq.count("C")) / max(len(seq), 1)
            gc_contents.append(gc)
            quals.append(sum(ord(c) - 33 for c in qual) / max(len(qual), 1))
    else:
        seq = ""
        for line in f:
            if line.startswith(">"):
                if seq:
                    lengths.append(len(seq))
                    gc_contents.append((seq.count("G") + seq.count("C")) / max(len(seq), 1))
                    seq_count += 1
                seq = ""
            else:
                seq += line.strip().upper()
        if seq:
            lengths.append(len(seq))
            gc_contents.append((seq.count("G") + seq.count("C")) / max(len(seq), 1))
            seq_count += 1

import numpy as np
print(f"Sequences: {seq_count:,}")
print(f"Length: min={min(lengths)}, max={max(lengths)}, median={np.median(lengths):.0f}, "
      f"mean={np.mean(lengths):.0f}")
# N50
sorted_lens = sorted(lengths, reverse=True)
cumsum = np.cumsum(sorted_lens)
n50 = sorted_lens[np.searchsorted(cumsum, cumsum[-1] / 2)]
print(f"N50: {n50:,}")
print(f"GC content: mean={np.mean(gc_contents)*100:.1f}%, std={np.std(gc_contents)*100:.1f}%")
if quals:
    print(f"Mean quality: {np.mean(quals):.1f}, median={np.median(quals):.1f}")
```

### Template: PDB Structure Exploration

```python
from collections import Counter

atoms, residues, chains = [], set(), set()
resolution = method = None

with open(pdb_path) as f:
    for line in f:
        if line.startswith("ATOM") or line.startswith("HETATM"):
            element = line[76:78].strip()
            resname = line[17:20].strip()
            chain = line[21]
            resseq = line[22:26].strip()
            atoms.append(element)
            residues.add((chain, resseq, resname))
            chains.add(chain)
        elif line.startswith("REMARK   2 RESOLUTION"):
            try:
                resolution = float(line.split()[-2])
            except (ValueError, IndexError):
                pass
        elif line.startswith("EXPDTA"):
            method = line[10:].strip()

element_counts = Counter(atoms)
print(f"Atoms: {len(atoms):,}")
print(f"Element distribution: {dict(element_counts.most_common(10))}")
print(f"Residues: {len(residues):,}")
print(f"Chains: {len(chains)} ({', '.join(sorted(chains))})")
if resolution: print(f"Resolution: {resolution} A")
if method: print(f"Method: {method}")

# Amino acid composition
aa_counts = Counter(r[2] for r in residues if len(r[2]) == 3)
print(f"Residue types: {dict(aa_counts.most_common(20))}")

# Molecular weight estimate (rough, for protein)
avg_aa_mw = 110  # average amino acid molecular weight
protein_residues = sum(1 for r in residues if r[2] in {
    "ALA","ARG","ASN","ASP","CYS","GLN","GLU","GLY","HIS","ILE",
    "LEU","LYS","MET","PHE","PRO","SER","THR","TRP","TYR","VAL"})
print(f"Estimated MW: {protein_residues * avg_aa_mw / 1000:.1f} kDa")
```

### Template: CSV/TSV with Mixed Types (Auto-Detection)

```python
import pandas as pd
import numpy as np

# Auto-detect separator
with open(file_path, "r") as f:
    sample = f.read(4096)
sep = "\t" if sample.count("\t") > sample.count(",") else ","
df = pd.read_csv(file_path, sep=sep, nrows=5)  # peek first
df = pd.read_csv(file_path, sep=sep)

# Auto-classify columns
col_types = {}
for col in df.columns:
    s = df[col].dropna()
    if s.empty:
        col_types[col] = "empty"
    elif pd.api.types.is_numeric_dtype(s):
        if s.nunique() <= 10 and s.nunique() / len(s) < 0.01:
            col_types[col] = "categorical_numeric"
        else:
            col_types[col] = "numeric"
    else:
        # Try datetime
        try:
            pd.to_datetime(s.head(100), infer_datetime_format=True)
            col_types[col] = "datetime"
        except (ValueError, TypeError):
            if s.nunique() / max(len(s), 1) > 0.5:
                col_types[col] = "high_cardinality_text"
            else:
                col_types[col] = "categorical"

for ctype in set(col_types.values()):
    cols = [c for c, t in col_types.items() if t == ctype]
    print(f"\n{ctype.upper()} ({len(cols)} columns): {cols[:10]}")

# Flag potential ID columns (unique per row)
id_cols = [c for c in df.columns if df[c].nunique() == len(df)]
if id_cols:
    print(f"\nPotential ID columns: {id_cols}")

# Flag constant columns
const_cols = [c for c in df.columns if df[c].nunique() <= 1]
if const_cols:
    print(f"Constant columns (drop candidates): {const_cols}")
```

---

## Red Flags to Always Check

These issues should be flagged prominently in every EDA report. Missing any of these can invalidate downstream analyses.

### 1. Batch Effects

Systematic technical variation between groups of samples processed differently.

```python
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# Color PCA by batch variable
pca = PCA(n_components=2)
pcs = pca.fit_transform(data_matrix)

fig, ax = plt.subplots(figsize=(8, 6))
for batch in batch_labels.unique():
    mask = batch_labels == batch
    ax.scatter(pcs[mask, 0], pcs[mask, 1], label=batch, alpha=0.7)
ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)")
ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)")
ax.legend(title="Batch")
plt.savefig("batch_effect_pca.png", dpi=150)
plt.close()
```

**Interpretation**: If samples cluster by batch rather than biological condition, batch correction is required before any biological analysis. Check if batch correlates with biological groups (confounded design).

### 2. Sample Swaps

Mislabeled samples that appear in the wrong group.

```python
# Correlation between expected replicates
import seaborn as sns

corr = data_matrix.T.corr()
fig, ax = plt.subplots(figsize=(10, 8))
sns.clustermap(corr, cmap="RdBu_r", vmin=-1, vmax=1, figsize=(10, 10))
plt.savefig("sample_correlation.png", dpi=150)
plt.close()
```

**Interpretation**: Biological replicates should correlate more highly with each other than with other groups. A sample that clusters with the wrong group is likely swapped. For genomics, check sex markers (XIST expression, Y-chromosome coverage) against reported sex.

### 3. Outlier Samples

Samples with extreme values on QC metrics that may distort analysis.

```python
from scipy.stats import median_abs_deviation
import numpy as np

# MAD-based outlier detection on key QC metrics
for metric_name, metric_values in qc_metrics.items():
    med = np.median(metric_values)
    mad = median_abs_deviation(metric_values)
    if mad == 0:
        continue
    outlier_mask = np.abs(metric_values - med) > 3 * mad
    if outlier_mask.any():
        print(f"OUTLIER on {metric_name}: {np.where(outlier_mask)[0].tolist()}")
        print(f"  Median: {med:.2f}, MAD: {mad:.2f}")
        print(f"  Outlier values: {metric_values[outlier_mask].tolist()}")
```

**Threshold**: >3 MADs from median is the standard cutoff. Report outliers but do not automatically remove them -- the decision requires domain context.

### 4. Data Leakage

Information from the test set contaminating the training set.

**Check for:**
- Duplicate or near-duplicate rows across train/test splits
- Features derived from the target variable
- Temporal leakage (future data used to predict past events)
- Group leakage (same patient/subject in both train and test)

```python
# Check for duplicate rows between train and test
if "split" in df.columns:
    train = df[df["split"] == "train"]
    test = df[df["split"] == "test"]
    overlap = pd.merge(train, test, how="inner",
                       on=[c for c in train.columns if c != "split"])
    if len(overlap) > 0:
        print(f"WARNING: {len(overlap)} duplicate rows between train and test!")
```

### 5. Survivorship Bias in Filtered Data

When upstream filtering removes informative observations.

**Check for:**
- Unusually high quality scores (suggests aggressive prior filtering)
- Missing low-quality categories entirely
- Non-uniform distributions where uniform is expected
- Document what filters were applied upstream if metadata is available

### 6. Simpson's Paradox

A trend that appears in subgroups but reverses when groups are combined.

```python
# Check if a relationship reverses when stratified
for group_col in categorical_cols:
    for x_col in numeric_cols[:5]:
        overall_corr = df[x_col].corr(df[target_col])
        group_corrs = df.groupby(group_col).apply(
            lambda g: g[x_col].corr(g[target_col]) if len(g) > 10 else np.nan
        ).dropna()
        sign_flip = (group_corrs * np.sign(overall_corr) < 0).any()
        if sign_flip:
            print(f"SIMPSON'S PARADOX: {x_col} vs {target_col}, stratified by {group_col}")
            print(f"  Overall r={overall_corr:.3f}, Group r's: {group_corrs.to_dict()}")
```

### 7. Confounding Variables

Variables that associate with both predictor and outcome, creating spurious relationships.

**Always examine:**
- Correlation between potential confounders and the main predictor
- Correlation between potential confounders and the outcome
- Whether adjusting for the confounder changes the predictor-outcome relationship

Common confounders by domain:
- **Genomics**: ancestry, sex, age, sequencing batch, library prep method
- **Clinical**: age, sex, BMI, comorbidities, medications, study site
- **Single-cell**: cell cycle phase, mitochondrial content, library size
- **Imaging**: acquisition date, instrument, operator, staining batch

---

## EDA Report Template

Use this template for every EDA report. Copy the structure and fill in findings.

```markdown
# Exploratory Data Analysis Report: [DATASET NAME]

**Date:** [DATE]
**Analyst:** NanoClaw Agent
**File(s):** [FILE PATHS]

## 1. Dataset Overview

| Property | Value |
|----------|-------|
| File format | [format] |
| File size | [size] |
| Dimensions | [rows x cols / sequences / variants / etc.] |
| Source | [origin if known] |
| Date range | [if applicable] |

[1-2 paragraph description of what this dataset contains]

## 2. Data Quality Summary

**Overall verdict:** [CLEAN / MINOR ISSUES / MAJOR CONCERNS]

| Quality Metric | Value | Status |
|---------------|-------|--------|
| Completeness | [% non-missing] | [OK/WARN/FAIL] |
| Duplicates | [count] | [OK/WARN/FAIL] |
| Outlier samples | [count] | [OK/WARN/FAIL] |
| Batch effects | [detected/not detected] | [OK/WARN/FAIL] |
| Format issues | [description] | [OK/WARN/FAIL] |

### Missing Data Pattern
[Description and heatmap if applicable]

## 3. Distribution Analysis

### Numeric Variables
[Summary statistics table]
[Key distribution findings: skewed variables, bimodal distributions, unexpected ranges]

### Categorical Variables
[Cardinality summary]
[Imbalanced categories, rare levels]

## 4. Relationship Analysis

### Correlations
[Top correlated pairs]
[Unexpected associations]

### Dimensionality Reduction
[PCA/UMAP results]
[Cluster structure]

## 5. Anomalies and Concerns

1. [Anomaly 1 with evidence]
2. [Anomaly 2 with evidence]
3. [Anomaly 3 with evidence]

## 6. Recommendations

1. **[Action 1]**: [Why and what to do]
2. **[Action 2]**: [Why and what to do]
3. **[Action 3]**: [Why and what to do]

## 7. Appendix: Auto-Generated Statistics

[Full describe() output or equivalent]
[Full missing value table]
[Full correlation matrix]
```

### Auto-Generated Summary Statistics

Always produce these tables programmatically and embed in the report:

```python
# Generate summary statistics as markdown table
def df_to_markdown(df, float_fmt=".2f"):
    """Convert DataFrame to markdown table string."""
    cols = df.columns.tolist()
    header = "| " + " | ".join([""] + cols) + " |"
    sep = "|" + "|".join(["---"] * (len(cols) + 1)) + "|"
    rows = []
    for idx, row in df.iterrows():
        vals = [str(idx)] + [f"{v:{float_fmt}}" if isinstance(v, float) else str(v) for v in row]
        rows.append("| " + " | ".join(vals) + " |")
    return "\n".join([header, sep] + rows)

stats_md = df_to_markdown(df.describe().T)
```

### Key Visualizations to Always Include

1. **Missing value heatmap** (for tabular data with missing values)
2. **Distribution plots** (histograms or violin plots of key numeric variables)
3. **Correlation heatmap** (for datasets with >2 numeric columns)
4. **PCA/UMAP plot** (for high-dimensional data, colored by available metadata)
5. **QC metric violin plots** (for omics data: library size, gene count, mito %)

Save all plots as PNG with dpi=150. Name them descriptively: `eda_missing_heatmap.png`, `eda_distributions.png`, `eda_correlation.png`, `eda_pca.png`, `eda_qc_violin.png`.

---

## Domain-Specific EDA Checklists

### RNA-seq Bulk

| Metric | Expected Range | Red Flag |
|--------|---------------|----------|
| Library size | 10M-100M reads | <5M or >200M |
| Mapping rate | >80% | <70% |
| rRNA contamination | <5% | >10% |
| Exonic rate | >60% | <40% |
| 3'/5' bias | <2x | >3x (degradation) |
| Gene body coverage | Uniform | Strong 3' or 5' bias |
| Detected genes | 12k-16k (human) | <8k or >20k |
| Inter-sample correlation | >0.9 (replicates) | <0.8 between replicates |
| PC1 variance | Biological condition | Batch or library prep |

Flag samples where `mapping_rate < 0.7`, `detected_genes < 8000`, or `rrna_pct > 10`. Build a QC DataFrame from `total_reads`, `mapped_reads`, `exonic_reads`, and gene detection counts, then use `describe().T` to summarize.

### Single-Cell RNA-seq

| Metric | Expected Range | Red Flag |
|--------|---------------|----------|
| Cells per sample | 1k-20k (10x) | <500 or >30k |
| Genes per cell | 500-5000 | <200 (empty) or >6000 (doublet) |
| UMIs per cell | 1k-30k | <500 or >50k |
| Mitochondrial % | <10% | >20% (dying cells) |
| Ribosomal % | 10-40% | >60% (contamination) |
| Doublet score | <0.3 | >0.5 (likely doublet) |
| Cells passing QC | >80% | <50% |
| Ambient RNA (SoupX) | <10% | >20% |

Use `scanpy.pp.calculate_qc_metrics` with `qc_vars=["mt", "ribo"]`. Standard thresholds: min_genes=200, max_genes=6000, min_counts=500, max_mt=20%. Report cells passing QC vs total. See AnnData template above for code.

### GWAS

| Metric | Expected Range | Red Flag |
|--------|---------------|----------|
| Sample call rate | >97% | <95% |
| SNP call rate | >98% | <95% |
| HWE p-value | >1e-6 (controls) | <1e-10 |
| MAF distribution | Uniform below 0.5 | Spike at specific values |
| Heterozygosity | Within 3 SD of mean | Extreme outliers (contamination) |
| Relatedness (IBD) | pi_hat < 0.2 | pi_hat > 0.25 (1st-degree relative) |
| PCA: population | Clusters match reported ancestry | Unexpected population clusters |
| Genomic inflation (lambda) | 1.0-1.05 | >1.1 (population stratification) |

SNP-level QC: filter on call rate >0.98, HWE p >1e-6, MAF >0.01. Sample-level QC: call rate >0.97, heterozygosity within 3 SD of mean. Run PCA and color by reported ancestry to check population stratification. Compute genomic inflation factor (lambda) from association test statistics.

### Proteomics

| Metric | Expected Range | Red Flag |
|--------|---------------|----------|
| Peptide count | 20k-50k (DDA) | <10k |
| Protein count | 3k-8k (DDA) | <2k |
| Missing value % | <30% (DDA) | >50% |
| Missing pattern | Random (MAR) | Structured (MNAR: low-abundance bias) |
| CV (technical reps) | <20% | >30% |
| Normalization | Equal medians | Shifted distributions between samples |
| Peptides/protein | >2 median | <1.5 median |

Key checks: correlate missing rate per protein with mean intensity (negative correlation = MNAR pattern, needs imputation-aware methods). Compare sample medians -- if CV >10%, apply median normalization. Count peptides per protein and flag single-peptide identifications.

### Methylation (EPIC/450K Array)

| Metric | Expected Range | Red Flag |
|--------|---------------|----------|
| Detection p-value | >99% probes pass | <95% (poor quality) |
| Beta value range | 0-1, bimodal | Uniform or spike at 0.5 |
| Probe failure rate | <1% | >5% |
| Sex check | Predicted matches reported | Mismatch (sample swap) |
| Bisulfite conversion | >90% | <80% |
| Bead count | >3 per probe | <3 (unreliable) |
| SNP probe PCA | Clusters match genotype | Unexpected clustering |

Check beta value distribution for expected bimodality (most probes at <0.2 or >0.8, few in 0.2-0.8 range). Compute probe failure rate (NA percentage). For sex check, extract X-chromosome probe medians and cluster samples -- should separate clearly into two groups matching reported sex. Use SNP probes for sample identity verification.

---

## Cross-References to Related Skills

After completing EDA, route to the appropriate analysis skill:

| If EDA reveals... | Then use skill... |
|-------------------|-------------------|
| RNA-seq count matrix ready for DE | `rnaseq-deseq2` |
| Single-cell data ready for clustering | `single-cell-analysis` |
| Variants ready for annotation/filtering | `variant-analysis` |
| Proteomics intensity matrix ready for DA | `proteomics-analysis` |
| Metabolomics peak table ready for analysis | `metabolomics-analysis` |
| Methylation data ready for DMR analysis | `epigenomics` |
| Sequences ready for phylogenetic analysis | `phylogenetics` |
| Data needing statistical modeling | `statistical-modeling` |
| Multi-omics datasets needing integration | `multi-omics-integration` |

---

## Implementation Notes

### Performance for Large Files

- For files >1 GB: read in chunks (`pd.read_csv(..., chunksize=100000)`)
- For BAM files: sample a fraction of reads rather than iterating all
- For VCF files: use tabix indexing for region-based queries
- For h5ad files: use `backed="r"` mode for out-of-core access
- Set a maximum of 1M rows for correlation analysis; sample if larger

### Handling Unknown Formats

Check file magic bytes (first 4-16 bytes) against known signatures. Try reading as text with UTF-8/Latin-1. Try CSV with common delimiters (tab, comma, semicolon). For binary, check for HDF5 (`\x89HDF`), gzip (`\x1f\x8b`), or BAM (`BAM\1`) signatures.

### Reproducibility

Print Python version and key package versions at start. Set random seeds for stochastic operations. Save all plots as PNG (dpi=150) with descriptive filenames. Record exact file paths and sizes.
