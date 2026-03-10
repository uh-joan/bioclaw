# Data Wrangling Recipes for Bioinformatics

Executable Python code templates for pandas-based data manipulation in bioinformatics contexts. Each recipe is self-contained with inline comments explaining every step.

---

## 1. Loading CSV/TSV/Excel with Proper Dtypes

```python
import pandas as pd

# CSV with explicit dtypes to prevent silent type coercion
# (e.g., sample IDs like "001" losing leading zeros)
df = pd.read_csv(
    "expression_data.csv",
    dtype={"sample_id": str, "gene_symbol": str},  # keep IDs as strings
    na_values=["NA", "N/A", "", ".", "null"],        # recognize common NA markers
    low_memory=False                                  # avoid mixed-type warnings
)
print(f"Loaded {df.shape[0]} rows x {df.shape[1]} columns")
print(f"Dtypes:\n{df.dtypes}")
print(f"Missing values per column:\n{df.isnull().sum()}")

# TSV (tab-delimited, common in bioinformatics tools like DESeq2 output)
deseq_results = pd.read_csv(
    "deseq2_results.tsv",
    sep="\t",
    index_col=0,                    # first column is gene ID
    dtype={"baseMean": float, "log2FoldChange": float, "padj": float}
)
print(f"DESeq2 results: {deseq_results.shape[0]} genes")

# Excel with specific sheet (clinical metadata often comes in Excel)
clinical = pd.read_excel(
    "patient_metadata.xlsx",
    sheet_name="Demographics",
    dtype={"patient_id": str, "age": float, "sex": str}
)
print(f"Clinical data: {clinical.shape[0]} patients")
```

---

## 2. Filtering Rows by Conditions (Numeric Thresholds, String Matching)

```python
import pandas as pd
import numpy as np

df = pd.read_csv("deseq2_results.csv")

# Filter by numeric threshold: significant DE genes
# padj < 0.05 AND absolute log2FC > 1 (2-fold change)
sig_genes = df[
    (df["padj"] < 0.05) &
    (df["log2FoldChange"].abs() > 1)
].copy()
print(f"Significant DE genes: {sig_genes.shape[0]} / {df.shape[0]}")

# Upregulated vs downregulated
up = sig_genes[sig_genes["log2FoldChange"] > 0]
down = sig_genes[sig_genes["log2FoldChange"] < 0]
print(f"  Upregulated: {up.shape[0]}, Downregulated: {down.shape[0]}")

# String matching: filter genes by name pattern
# Find all kinase genes (names containing "kinase" or ending in "K")
kinases = df[
    df["gene_symbol"].str.contains("kinase", case=False, na=False) |
    df["gene_symbol"].str.match(r"^[A-Z]+K\d*$", na=False)
]
print(f"Kinase genes found: {kinases.shape[0]}")

# Filter using isin() for a predefined gene list
target_genes = ["TP53", "BRCA1", "EGFR", "KRAS", "MYC", "PIK3CA"]
targets = df[df["gene_symbol"].isin(target_genes)]
print(f"Target genes found: {targets.shape[0]} / {len(target_genes)}")

# Combined: numeric + string filter
# High-expression kinases with significant changes
high_expr_kinases = df[
    (df["baseMean"] > 100) &
    (df["padj"] < 0.01) &
    df["gene_symbol"].str.contains("kinase", case=False, na=False)
]
print(f"High-expression significant kinases: {high_expr_kinases.shape[0]}")
```

---

## 3. Groupby Aggregations (Mean, Median, Count, Sum)

```python
import pandas as pd
import numpy as np

df = pd.read_csv("sample_expression.csv")

# Group by treatment condition and compute summary stats per gene
gene_stats = df.groupby("treatment").agg(
    mean_expr=("expression", "mean"),
    median_expr=("expression", "median"),
    std_expr=("expression", "std"),
    n_samples=("expression", "count"),
    total_expr=("expression", "sum")
).reset_index()
print("Per-treatment summary:")
print(gene_stats.to_string(index=False))

# Multiple groupby columns: gene x treatment
gene_treatment = df.groupby(["gene_symbol", "treatment"]).agg(
    mean_expr=("expression", "mean"),
    sem_expr=("expression", "sem"),        # standard error of the mean
    n=("expression", "count")
).reset_index()
print(f"\nGene x Treatment combos: {gene_treatment.shape[0]}")

# Named aggregation with multiple columns simultaneously
summary = df.groupby("sample_group").agg(
    avg_age=("age", "mean"),
    n_patients=("patient_id", "nunique"),   # count unique patients
    avg_expression=("expression", "mean"),
    max_expression=("expression", "max")
).reset_index()
print(f"\nSample group summary:\n{summary}")

# Custom aggregation: coefficient of variation per gene
cv_per_gene = df.groupby("gene_symbol")["expression"].agg(
    lambda x: x.std() / x.mean() if x.mean() != 0 else np.nan
).rename("cv").sort_values(ascending=False)
print(f"\nTop 5 most variable genes (by CV):")
print(cv_per_gene.head())
```

---

## 4. Pivot Tables and Cross-Tabulations

```python
import pandas as pd
import numpy as np

df = pd.read_csv("long_format_expression.csv")

# Pivot from long to wide format (genes as rows, samples as columns)
# Common for creating expression matrices from melted data
expr_matrix = df.pivot_table(
    index="gene_symbol",
    columns="sample_id",
    values="expression",
    aggfunc="mean"       # handle duplicates by averaging
)
print(f"Expression matrix: {expr_matrix.shape[0]} genes x {expr_matrix.shape[1]} samples")

# Pivot with multiple values: mean and count
summary_pivot = df.pivot_table(
    index="gene_symbol",
    columns="treatment",
    values="expression",
    aggfunc=["mean", "count"]
)
print(f"\nSummary pivot shape: {summary_pivot.shape}")

# Cross-tabulation: patient counts by disease stage and treatment
clinical = pd.read_csv("clinical_data.csv")
xtab = pd.crosstab(
    clinical["disease_stage"],
    clinical["treatment_arm"],
    margins=True,           # add row/column totals
    margins_name="Total"
)
print(f"\nCross-tabulation:\n{xtab}")

# Normalized cross-tab (proportions per row)
xtab_norm = pd.crosstab(
    clinical["disease_stage"],
    clinical["treatment_arm"],
    normalize="index"       # normalize by row (stage)
)
print(f"\nNormalized (proportions per stage):\n{xtab_norm.round(3)}")
```

---

## 5. Merging/Joining DataFrames (Inner, Left, Outer)

```python
import pandas as pd

# Load expression data and clinical annotations
expr = pd.read_csv("expression_counts.csv")        # gene x sample counts
clinical = pd.read_csv("clinical_metadata.csv")     # patient demographics

# Inner join: only samples present in both datasets
merged_inner = pd.merge(
    expr, clinical,
    left_on="sample_id", right_on="patient_sample_id",
    how="inner"
)
print(f"Inner join: {merged_inner.shape[0]} rows "
      f"(expr had {expr.shape[0]}, clinical had {clinical.shape[0]})")

# Left join: keep all expression rows, fill missing clinical as NaN
merged_left = pd.merge(
    expr, clinical,
    left_on="sample_id", right_on="patient_sample_id",
    how="left"
)
missing_clinical = merged_left["patient_sample_id"].isna().sum()
print(f"Left join: {merged_left.shape[0]} rows, "
      f"{missing_clinical} samples missing clinical data")

# Outer join: keep everything from both
merged_outer = pd.merge(
    expr, clinical,
    left_on="sample_id", right_on="patient_sample_id",
    how="outer",
    indicator=True    # adds _merge column showing source
)
print(f"\nOuter join merge diagnostics:")
print(merged_outer["_merge"].value_counts())

# Multi-key merge: join on both gene and chromosome
annotations = pd.read_csv("gene_annotations.csv")
annotated = pd.merge(
    expr, annotations,
    on=["gene_symbol", "chromosome"],
    how="left"
)
print(f"\nAnnotated expression data: {annotated.shape}")

# Validate merge: check for unexpected duplicates
if annotated.shape[0] > expr.shape[0]:
    print("WARNING: merge introduced duplicates (many-to-many)")
    dupes = annotated[annotated.duplicated(subset=["sample_id", "gene_symbol"], keep=False)]
    print(f"  {dupes.shape[0]} duplicate rows detected")
```

---

## 6. Handling Missing Values (dropna, fillna, Interpolation)

```python
import pandas as pd
import numpy as np

df = pd.read_csv("expression_with_missing.csv")

# Diagnose missingness pattern
print("Missing values per column:")
print(df.isnull().sum().sort_values(ascending=False))
print(f"\nRows with any missing: {df.isnull().any(axis=1).sum()} / {df.shape[0]}")
pct_missing = (df.isnull().sum() / len(df) * 100).round(1)
print(f"\nPercent missing:\n{pct_missing[pct_missing > 0]}")

# Strategy 1: Drop rows where critical columns are missing
df_clean = df.dropna(subset=["gene_symbol", "expression"])
print(f"\nAfter dropping missing gene/expression: {df_clean.shape[0]} rows")

# Strategy 2: Fill numeric columns with column median (robust to outliers)
numeric_cols = df.select_dtypes(include=[np.number]).columns
df_filled = df.copy()
for col in numeric_cols:
    median_val = df[col].median()
    n_filled = df[col].isnull().sum()
    df_filled[col] = df[col].fillna(median_val)
    if n_filled > 0:
        print(f"  Filled {n_filled} missing in '{col}' with median={median_val:.3f}")

# Strategy 3: Interpolation for time-series data (growth curves)
# Forward-fill then linear interpolation for temporal measurements
ts_df = pd.read_csv("growth_curve.csv")
ts_df = ts_df.sort_values(["sample_id", "timepoint"])
ts_df["od600_interp"] = ts_df.groupby("sample_id")["od600"].transform(
    lambda x: x.interpolate(method="linear", limit_direction="both")
)
print(f"\nInterpolated growth curve: "
      f"{ts_df['od600'].isnull().sum()} -> {ts_df['od600_interp'].isnull().sum()} missing")

# Strategy 4: Flag and separate incomplete cases for sensitivity analysis
df["is_complete"] = ~df.isnull().any(axis=1)
print(f"\nComplete cases: {df['is_complete'].sum()} / {df.shape[0]}")
```

---

## 7. Column Transformations (apply, map, log-transform)

```python
import pandas as pd
import numpy as np

df = pd.read_csv("expression_data.csv")

# Log2 transform expression values (standard for RNA-seq)
# Add pseudocount of 1 to handle zeros
df["log2_expression"] = np.log2(df["expression"] + 1)
print(f"Expression range: {df['expression'].min():.1f} - {df['expression'].max():.1f}")
print(f"Log2 range: {df['log2_expression'].min():.2f} - {df['log2_expression'].max():.2f}")

# Z-score normalization per gene (across samples)
df["zscore"] = df.groupby("gene_symbol")["expression"].transform(
    lambda x: (x - x.mean()) / x.std() if x.std() > 0 else 0
)

# Map categorical values to numeric codes
stage_map = {"I": 1, "II": 2, "III": 3, "IV": 4}
df["stage_numeric"] = df["disease_stage"].map(stage_map)
# Warn about unmapped values
unmapped = df["disease_stage"][df["stage_numeric"].isna()].unique()
if len(unmapped) > 0:
    print(f"WARNING: unmapped stages: {unmapped}")

# Apply custom function: classify expression level
def classify_expression(val):
    """Bin expression into low/medium/high based on quantiles."""
    if val < 10:
        return "low"
    elif val < 100:
        return "medium"
    else:
        return "high"

df["expr_category"] = df["expression"].apply(classify_expression)
print(f"\nExpression categories:\n{df['expr_category'].value_counts()}")

# Vectorized conditional: fold-change direction
df["direction"] = np.where(
    df["log2FoldChange"] > 0, "up",
    np.where(df["log2FoldChange"] < 0, "down", "unchanged")
)
print(f"\nDirection counts:\n{df['direction'].value_counts()}")

# Rank transform (useful for non-parametric analyses)
df["expression_rank"] = df.groupby("sample_id")["expression"].rank(
    method="average", ascending=False
)
```

---

## 8. String Operations on Gene Names / Sample IDs

```python
import pandas as pd

df = pd.read_csv("gene_results.csv")

# Standardize gene symbols: uppercase, strip whitespace
df["gene_clean"] = (
    df["gene_symbol"]
    .str.strip()           # remove leading/trailing spaces
    .str.upper()           # standardize to uppercase
    .str.replace(r"\s+", "", regex=True)  # remove internal spaces
)
print(f"Cleaned {(df['gene_symbol'] != df['gene_clean']).sum()} gene names")

# Extract gene family from symbol (e.g., "BRCA1" -> "BRCA")
df["gene_family"] = df["gene_clean"].str.extract(r"^([A-Z]+)", expand=False)
print(f"\nTop gene families:\n{df['gene_family'].value_counts().head(10)}")

# Parse sample IDs with structured format: "PROJ-SITE01-PAT042-T1"
df["project"] = df["sample_id"].str.split("-").str[0]
df["site"] = df["sample_id"].str.split("-").str[1]
df["patient_num"] = df["sample_id"].str.extract(r"PAT(\d+)", expand=False).astype(int)
df["timepoint"] = df["sample_id"].str.extract(r"(T\d+)$", expand=False)
print(f"\nParsed sample IDs:")
print(f"  Projects: {df['project'].nunique()}")
print(f"  Sites: {df['site'].nunique()}")
print(f"  Patients: {df['patient_num'].nunique()}")
print(f"  Timepoints: {df['timepoint'].unique()}")

# Replace Ensembl IDs with gene symbols using a mapping file
id_map = pd.read_csv("ensembl_to_symbol.csv")  # columns: ensembl_id, gene_symbol
mapping = dict(zip(id_map["ensembl_id"], id_map["gene_symbol"]))
df["gene_symbol"] = df["ensembl_id"].map(mapping)
unmapped = df["gene_symbol"].isna().sum()
print(f"\nMapped {df.shape[0] - unmapped} / {df.shape[0]} Ensembl IDs to gene symbols")

# Detect and handle versioned Ensembl IDs (ENSG00000141510.18 -> ENSG00000141510)
df["ensembl_base"] = df["ensembl_id"].str.replace(r"\.\d+$", "", regex=True)
```

---

## 9. Multi-Index Operations

```python
import pandas as pd
import numpy as np

df = pd.read_csv("multi_condition_expression.csv")

# Create multi-index from treatment and timepoint
df_mi = df.set_index(["treatment", "timepoint", "gene_symbol"])
df_mi = df_mi.sort_index()   # always sort multi-index for performance
print(f"Multi-index levels: {df_mi.index.names}")
print(f"Shape: {df_mi.shape}")

# Select with multi-index: all genes at timepoint 24h under drug treatment
subset = df_mi.loc[("drug", 24), :]
print(f"\nDrug @ 24h: {subset.shape[0]} genes")

# Cross-section: select across a specific level
# All data for gene TP53 regardless of treatment/timepoint
tp53 = df_mi.xs("TP53", level="gene_symbol")
print(f"\nTP53 entries: {tp53.shape[0]}")

# Aggregate within multi-index levels
# Mean expression per treatment x gene (averaging across timepoints)
mean_by_treatment = df_mi.groupby(level=["treatment", "gene_symbol"])["expression"].mean()
print(f"\nMean per treatment x gene: {mean_by_treatment.shape[0]} entries")

# Unstack: convert one index level to columns
# Pivot treatment into columns for easy comparison
wide = mean_by_treatment.unstack(level="treatment")
wide["fold_change"] = wide["drug"] / wide["control"]
wide["log2FC"] = np.log2(wide["fold_change"])
top_changed = wide.nlargest(10, "log2FC")
print(f"\nTop 10 upregulated genes:\n{top_changed[['log2FC']].round(2)}")

# Stack: convert columns back to index level (wide -> long)
long = wide[["drug", "control"]].stack().rename("expression").reset_index()
print(f"\nRe-stacked shape: {long.shape}")
```

---

## 10. Reading and Writing Various Bioinformatics Formats

```python
import pandas as pd
import numpy as np

# --- BED format (0-based, tab-separated: chrom, start, end, name, score, strand) ---
bed = pd.read_csv(
    "peaks.bed", sep="\t",
    header=None,
    names=["chrom", "start", "end", "name", "score", "strand"],
    dtype={"chrom": str, "start": int, "end": int}
)
bed["length"] = bed["end"] - bed["start"]
print(f"BED: {bed.shape[0]} regions, median length = {bed['length'].median():.0f} bp")

# --- GFF/GTF format (gene annotations) ---
gtf = pd.read_csv(
    "annotations.gtf", sep="\t", comment="#",
    header=None,
    names=["seqname", "source", "feature", "start", "end",
           "score", "strand", "frame", "attributes"]
)
# Extract gene_id from attributes column
gtf["gene_id"] = gtf["attributes"].str.extract(r'gene_id "([^"]+)"', expand=False)
genes_only = gtf[gtf["feature"] == "gene"]
print(f"GTF: {genes_only.shape[0]} genes")

# --- VCF format (variant calls, skip ## header lines) ---
# Count header lines to skip
with open("variants.vcf") as f:
    skip_lines = sum(1 for line in f if line.startswith("##"))
vcf = pd.read_csv(
    "variants.vcf", sep="\t",
    skiprows=skip_lines,
    dtype={"#CHROM": str, "POS": int}
)
vcf.rename(columns={"#CHROM": "CHROM"}, inplace=True)
print(f"VCF: {vcf.shape[0]} variants across {vcf['CHROM'].nunique()} chromosomes")

# --- FASTA ID parsing (extract IDs from headers for joining) ---
fasta_ids = []
with open("sequences.fasta") as f:
    for line in f:
        if line.startswith(">"):
            seq_id = line.strip().lstrip(">").split()[0]
            fasta_ids.append(seq_id)
fasta_df = pd.DataFrame({"seq_id": fasta_ids})
print(f"FASTA: {len(fasta_ids)} sequences")

# --- Writing results ---
# Save as TSV (bioinformatics standard)
results = pd.DataFrame({"gene": ["TP53", "BRCA1"], "pvalue": [0.001, 0.05]})
results.to_csv("results.tsv", sep="\t", index=False)

# Save as Excel with multiple sheets
with pd.ExcelWriter("analysis_results.xlsx", engine="openpyxl") as writer:
    bed.to_excel(writer, sheet_name="Peaks", index=False)
    genes_only.to_excel(writer, sheet_name="Genes", index=False)
print("Results written to TSV and Excel")
```

---

## 11. Quantile Normalization Across Samples

```python
import pandas as pd
import numpy as np

def quantile_normalize(df):
    """
    Quantile normalize a gene-by-sample expression matrix.
    Each column (sample) gets same distribution.
    """
    # Rank values within each column
    rank_mean = df.stack().groupby(
        df.rank(method="first").stack().astype(int)
    ).mean()
    # Map ranks back to normalized values
    normalized = df.rank(method="min").stack().astype(int).map(rank_mean).unstack()
    return normalized

# Load raw counts matrix (genes as rows, samples as columns)
counts = pd.read_csv("raw_counts.csv", index_col=0)
print(f"Raw counts: {counts.shape[0]} genes x {counts.shape[1]} samples")
print(f"  Column means before: {counts.mean().round(1).tolist()[:5]}...")

# Apply quantile normalization
normalized = quantile_normalize(counts)
print(f"  Column means after:  {normalized.mean().round(1).tolist()[:5]}...")

# Verify: all columns should have identical distribution
for col in normalized.columns[:3]:
    print(f"  {col}: mean={normalized[col].mean():.2f}, "
          f"median={normalized[col].median():.2f}, "
          f"std={normalized[col].std():.2f}")
```

---

## 12. Filtering Low-Expression Genes

```python
import pandas as pd
import numpy as np

counts = pd.read_csv("count_matrix.csv", index_col=0)
print(f"Input: {counts.shape[0]} genes x {counts.shape[1]} samples")

# Strategy 1: Remove genes with total count below threshold
min_total = 10
mask_total = counts.sum(axis=1) >= min_total
print(f"  Genes with total >= {min_total}: {mask_total.sum()}")

# Strategy 2: Require minimum CPM in minimum number of samples
# (standard DESeq2/edgeR pre-filter)
lib_sizes = counts.sum(axis=0)
cpm = counts.div(lib_sizes, axis=1) * 1e6
min_cpm = 1.0
min_samples = 3  # at least 3 samples above threshold
mask_cpm = (cpm >= min_cpm).sum(axis=1) >= min_samples
print(f"  Genes with CPM >= {min_cpm} in >= {min_samples} samples: {mask_cpm.sum()}")

# Strategy 3: Remove genes with zero variance (uninformative)
mask_var = counts.var(axis=1) > 0
print(f"  Genes with non-zero variance: {mask_var.sum()}")

# Combine filters
combined_mask = mask_total & mask_cpm & mask_var
filtered = counts.loc[combined_mask]
print(f"\nAfter filtering: {filtered.shape[0]} genes "
      f"(removed {counts.shape[0] - filtered.shape[0]})")
```

---

## 13. Melting Wide Expression Matrices to Long Format

```python
import pandas as pd

# Wide format: genes as rows, samples as columns
wide = pd.read_csv("expression_matrix.csv", index_col=0)
print(f"Wide format: {wide.shape}")

# Melt to long format for plotting and groupby operations
long = wide.reset_index().melt(
    id_vars=["gene_symbol"],      # keep gene as identifier
    var_name="sample_id",          # column names become sample_id
    value_name="expression"        # values become expression
)
print(f"Long format: {long.shape}")
print(long.head())

# Parse sample metadata from sample IDs
# e.g., "Control_Rep1" -> treatment="Control", replicate="Rep1"
long["treatment"] = long["sample_id"].str.rsplit("_", n=1).str[0]
long["replicate"] = long["sample_id"].str.rsplit("_", n=1).str[1]
print(f"\nTreatments: {long['treatment'].unique()}")
print(f"Replicates per treatment:\n{long.groupby('treatment')['replicate'].nunique()}")

# Now easy to compute per-gene per-treatment statistics
stats = long.groupby(["gene_symbol", "treatment"]).agg(
    mean=("expression", "mean"),
    std=("expression", "std"),
    n=("expression", "count")
).reset_index()
print(f"\nSummary stats: {stats.shape[0]} gene-treatment combinations")
```

---

## 14. Efficient Column-Wise Operations with eval and query

```python
import pandas as pd
import numpy as np

df = pd.read_csv("large_expression_dataset.csv")

# Use .query() for readable, fast filtering (uses numexpr under the hood)
sig = df.query("padj < 0.05 and log2FoldChange.abs() > 1")
print(f"Significant genes: {sig.shape[0]}")

# Chain multiple conditions readably
subset = df.query(
    "baseMean > 100 and "
    "padj < 0.01 and "
    "chromosome == 'chr17'"
)
print(f"Filtered subset: {subset.shape[0]}")

# Use .eval() for fast column creation without intermediate copies
df.eval("neg_log10_pval = -1 * @np.log10(padj)", inplace=True)
df.eval("mean_tpm = (tpm_rep1 + tpm_rep2 + tpm_rep3) / 3", inplace=True)
df.eval("is_significant = padj < 0.05 and log2FoldChange.abs() > 1", inplace=True)
print(f"\nNew columns: neg_log10_pval, mean_tpm, is_significant")
print(f"Significant genes: {df['is_significant'].sum()}")

# Volcano plot coordinates in one step
df.eval("""
    volcano_x = log2FoldChange
    volcano_y = -1 * @np.log10(padj)
""", inplace=True)
```

---

## 15. Rolling Window and Cumulative Operations for Genomic Data

```python
import pandas as pd
import numpy as np

# Sliding window analysis along chromosome
df = pd.read_csv("coverage.bedgraph", sep="\t",
                  header=None, names=["chrom", "start", "end", "coverage"])

# Sort by genomic position
df = df.sort_values(["chrom", "start"]).reset_index(drop=True)

# Per-chromosome rolling mean (smoothing coverage tracks)
df["coverage_smooth"] = df.groupby("chrom")["coverage"].transform(
    lambda x: x.rolling(window=10, center=True, min_periods=1).mean()
)

# Cumulative coverage for saturation analysis
df["cumulative_bases"] = df.groupby("chrom")["coverage"].cumsum()

# Find regions with coverage significantly above local average
df["local_mean"] = df.groupby("chrom")["coverage"].transform(
    lambda x: x.rolling(window=50, center=True, min_periods=10).mean()
)
df["local_std"] = df.groupby("chrom")["coverage"].transform(
    lambda x: x.rolling(window=50, center=True, min_periods=10).std()
)
df["z_score"] = (df["coverage"] - df["local_mean"]) / df["local_std"]
hotspots = df[df["z_score"] > 3]
print(f"Coverage hotspots (z > 3): {hotspots.shape[0]} regions")
print(f"  Per chromosome:\n{hotspots['chrom'].value_counts().head()}")
```
