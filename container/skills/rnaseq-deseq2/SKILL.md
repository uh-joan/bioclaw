---
name: rnaseq-deseq2
description: Production-ready RNA-seq differential expression analysis using PyDESeq2. Normalization, dispersion estimation, Wald testing, LFC shrinkage, and result filtering. Writes and executes Python code for the full DE pipeline. Use when user mentions RNA-seq, differential expression, DESeq2, PyDESeq2, count matrix, normalized counts, size factors, dispersion, Wald test, log2 fold change, LFC shrinkage, volcano plot, MA plot, differentially expressed genes, DEGs, padj, adjusted p-value, batch correction, design formula, or count-based DE analysis.
---

# RNA-seq DESeq2

> **Code recipes**: See [recipes.md](recipes.md) in this directory for copy-paste executable code templates.

Production-ready RNA-seq differential expression analysis using PyDESeq2. The agent writes and executes Python code for normalization, dispersion estimation, Wald testing, LFC shrinkage, and result filtering. Uses Open Targets for gene-disease annotation, PubMed for literature evidence, and NLM for gene ID resolution and cross-referencing.

## Report-First Workflow

1. **Create report file immediately**: `[comparison]_rnaseq_deseq2_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Pathway enrichment on DE gene lists (ORA/GSEA) → use `gene-enrichment`
- Single-cell differential expression analysis → use `single-cell-analysis`
- Multi-omics integration with DE results → use `multi-omics-integration`
- Target druggability assessment for top DE genes → use `target-research`
- Systems-level network analysis of DE genes → use `systems-biology`
- Bulk proteomics or metabolomics differential analysis → use `proteomics-analysis`

## Cross-Reference: Other Skills

- **Pathway enrichment on DE gene lists** -> use gene-enrichment skill
- **Single-cell differential expression** -> use single-cell-analysis skill
- **Multi-omics integration with DE results** -> use multi-omics-integration skill
- **Target druggability for top DE genes** -> use target-research skill
- **Systems-level network analysis of DE genes** -> use systems-biology skill

## Available MCP Tools

### `mcp__opentargets__opentargets_info` (Gene-Disease Annotation)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_targets` | Search targets by gene symbol/name | `query`, `size` |
| `search_diseases` | Search diseases by name/synonym | `query`, `size` |
| `get_target_disease_associations` | Evidence-scored target-disease links | `targetId` (Ensembl ID), `diseaseId` (EFO ID), `minScore`, `size` |
| `get_disease_targets_summary` | All targets for a disease | `diseaseId`, `minScore`, `size` |
| `get_target_details` | Full target info (function, pathways, tractability) | `id` (Ensembl ID) |
| `get_disease_details` | Full disease info (ontology, phenotypes) | `id` (EFO ID) |

### `mcp__pubmed__pubmed_articles` (DE Literature)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Quick keyword search | `keywords`, `num_results` |
| `search_advanced` | Filtered search | `term`, `journal`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Full article details | `pmid` |

### `mcp__nlm__nlm_ct_codes` (Gene ID Resolution & Cross-Referencing)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `ncbi-genes` | Resolve gene symbols to NCBI Gene IDs, retrieve gene info | `query`, `organism` |
| `search_icd10` | Search ICD-10 diagnosis codes | `query`, `limit` |
| `search_icd10pcs` | Search ICD-10-PCS procedure codes | `query`, `limit` |
| `search_cpt` | Search CPT procedure codes | `query`, `limit` |
| `search_hcpcs` | Search HCPCS codes | `query`, `limit` |
| `search_ndc` | Search NDC drug codes | `query`, `limit` |
| `search_rxnorm` | Search RxNorm drug identifiers | `query`, `limit` |
| `search_snomed` | Search SNOMED CT clinical terms | `query`, `limit` |
| `search_loinc` | Search LOINC lab/observation codes | `query`, `limit` |
| `search_mesh` | Search MeSH medical subject headings | `query`, `limit` |
| `search_umls` | Search UMLS unified medical language | `query`, `limit` |

### `mcp__gtex__gtex_data` (Tissue Expression & eQTLs)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_genes` | Search genes in GTEx | `query`, `page`, `pageSize` |
| `get_median_gene_expression` | Median expression per tissue | `gencodeId`, `tissueSiteDetailId` |
| `get_gene_expression` | Expression across tissues | `gencodeId`, `tissueSiteDetailId` |
| `get_tissue_info` | Available tissue metadata | — |

### `mcp__geo__geo_data` (GEO Public Datasets)

| Tool | Method | Use |
|------|--------|-----|
| `mcp__geo__geo_data` | `search_datasets` | Find reference RNA-seq datasets for comparison |
| | `search_by_gene` | Find datasets studying a specific gene |
| | `get_series_info` | Get details on a GSE series (design, samples, platform) |
| | `get_download_links` | Get FTP download URLs for raw/processed data |
| | `get_platform_info` | Check platform details (array vs sequencing) |

**GEO workflow:** Search GEO for reference datasets to validate DE analysis findings or find public data for meta-analysis.

```
mcp__geo__geo_data(method: "search_datasets", query: "DISEASE RNA-seq differential expression")
mcp__geo__geo_data(method: "get_series_info", series_id: "GSExxxxxx")
mcp__geo__geo_data(method: "get_download_links", series_id: "GSExxxxxx")
```

---

## 7-Step Differential Expression Pipeline

### Step 1: Question Parsing

```
1. Identify the biological question:
   - Which condition/treatment is being compared?
   - What is the reference (control) group?
   - Are there covariates or confounders (batch, sex, age)?
   - Is the user looking for up-regulated, down-regulated, or both?

2. Determine analysis parameters:
   - Significance threshold: padj < 0.05 (default), user may request stricter
   - Fold change cutoff: |log2FC| > 1 (default), user may adjust
   - Shrinkage method: apeglm (default), ashr, or normal

3. Confirm input data format:
   - CSV/TSV count matrix (genes x samples or samples x genes)
   - h5ad (AnnData) file with raw counts in .X or .layers['counts']
   - Metadata/coldata as separate file or embedded in h5ad .obs
```

### Step 2: Data Validation

```python
import pandas as pd
import numpy as np

# Auto-detect file format
def load_count_data(file_path):
    if file_path.endswith('.h5ad'):
        import anndata
        adata = anndata.read_h5ad(file_path)
        # Check for raw counts in .X or .layers
        if 'counts' in adata.layers:
            counts = pd.DataFrame(adata.layers['counts'].toarray() if hasattr(adata.layers['counts'], 'toarray') else adata.layers['counts'],
                                  index=adata.obs_names, columns=adata.var_names)
        else:
            counts = pd.DataFrame(adata.X.toarray() if hasattr(adata.X, 'toarray') else adata.X,
                                  index=adata.obs_names, columns=adata.var_names)
        metadata = adata.obs
        return counts.T, metadata  # PyDESeq2 expects genes x samples
    elif file_path.endswith('.tsv') or file_path.endswith('.txt'):
        counts = pd.read_csv(file_path, sep='\t', index_col=0)
    else:
        counts = pd.read_csv(file_path, index_col=0)

    # Validate: counts must be non-negative integers
    assert (counts >= 0).all().all(), "Count matrix contains negative values"
    assert (counts == counts.astype(int)).all().all(), "Count matrix contains non-integer values — ensure raw counts, not normalized"

    return counts, None

# Orientation check: genes should be rows, samples should be columns
# Heuristic: if rows >> columns, assume genes x samples (correct)
# If columns >> rows, transpose
if counts.shape[0] < counts.shape[1]:
    print("WARNING: More columns than rows — assuming samples x genes, transposing")
    counts = counts.T
```

### Step 3: Metadata Inspection (Biological Factors vs Batch)

```
1. Load and validate sample metadata (coldata):
   - Confirm all samples in count matrix have metadata entries
   - Identify the primary condition/treatment column
   - Detect potential batch variables (sequencing run, plate, date)

2. Batch effect detection logic:
   IF metadata contains columns like 'batch', 'run', 'plate', 'lane', 'date':
     → Flag as potential batch variable
     → Check confounding: is batch perfectly correlated with condition?
       - If YES: warn user, cannot separate batch from condition
       - If NO: include batch in design formula as covariate

3. Design formula construction:
   - Simple: ~ condition
   - With batch: ~ batch + condition
   - With multiple covariates: ~ batch + sex + condition
   - IMPORTANT: the variable of interest (condition) must be LAST in the formula
```

### Step 4: PyDESeq2 Execution

```python
from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds import DeseqStats

# Prepare metadata
metadata = pd.DataFrame({'condition': sample_conditions}, index=sample_names)
# If batch variable present:
# metadata['batch'] = batch_labels

# Create DESeq dataset
dds = DeseqDataSet(
    counts=counts_df,           # genes x samples DataFrame
    metadata=metadata,
    design="~ condition",       # or "~ batch + condition" if batch present
    refit_cooks=True,
    n_cpus=4
)

# --- Size factor estimation ---
# Median-of-ratios normalization (same as R DESeq2)
dds.fit_size_factors()
print("Size factors:", dds.obsm["size_factors"])
# Check: size factors should be roughly centered around 1
# Outliers (< 0.1 or > 10) suggest library size issues

# --- Dispersion estimation ---
# Gene-wise dispersion → trend fitting → shrinkage toward trend
dds.fit_genewise_dispersions()
dds.fit_dispersion_trend()
dds.fit_dispersion_prior()
dds.fit_MAP_dispersions()

# --- Wald test ---
# Tests each gene: is the log2 fold change significantly different from zero?
dds.fit_LFC()
dds.calculate_cooks()

# Run statistical test
stat_res = DeseqStats(
    dds,
    contrast=["condition", "treatment", "control"],  # [factor, numerator, denominator]
    alpha=0.05,
    cooks_filter=True,
    independent_filter=True
)

# Wald test with Benjamini-Hochberg correction
stat_res.summary()

# --- LFC shrinkage ---
# Shrink log2 fold changes for low-count genes to reduce noise
# Uses the 'apeglm' method by default in PyDESeq2
stat_res.lfc_shrink(coeff="condition_treatment_vs_control")

# Extract results
results_df = stat_res.results_df
print(results_df.head())
# Columns: baseMean, log2FoldChange, lfcSE, stat, pvalue, padj
```

### Step 5: Results Filtering

```python
# Default thresholds
PADJ_THRESHOLD = 0.05
LFC_THRESHOLD = 1.0  # |log2FC| > 1 means > 2-fold change

# Filter significant DE genes
sig_genes = results_df[
    (results_df['padj'] < PADJ_THRESHOLD) &
    (results_df['log2FoldChange'].abs() > LFC_THRESHOLD)
].copy()

# Separate up- and down-regulated
up_genes = sig_genes[sig_genes['log2FoldChange'] > 0].sort_values('padj')
down_genes = sig_genes[sig_genes['log2FoldChange'] < 0].sort_values('padj')

print(f"Total DE genes (padj < {PADJ_THRESHOLD}, |log2FC| > {LFC_THRESHOLD}): {len(sig_genes)}")
print(f"  Up-regulated: {len(up_genes)}")
print(f"  Down-regulated: {len(down_genes)}")

# Top DE genes table
top_genes = sig_genes.sort_values('padj').head(20)
print(top_genes[['baseMean', 'log2FoldChange', 'lfcSE', 'pvalue', 'padj']])
```

### Step 6: Dispersion Analysis

```
1. Dispersion QC checks:
   - Plot dispersion estimates vs mean expression (dispersion plot)
   - Genes above the trend line have higher variability than expected
   - Genes below the trend line are well-behaved
   - The shrinkage step pulls gene-wise estimates toward the trend

2. Diagnostic criteria:
   - Gene-wise dispersions should scatter around the fitted trend
   - Extremely high dispersions (> 10) may indicate outlier samples
   - Very low dispersions for high-count genes are expected
   - If trend is flat or increasing, check for sample quality issues

3. Cook's distance:
   - Identifies samples that disproportionately influence a gene's result
   - Genes flagged by Cook's filter have padj set to NA
   - If many genes are flagged, investigate sample quality
```

### Step 7: Enrichment & Annotation

```
1. Gene annotation with MCP tools:
   mcp__nlm__nlm_ct_codes(method: "ncbi-genes", query: "TOP_GENE_SYMBOL", organism: "human")
   → Resolve gene symbol, get functional description

   mcp__opentargets__opentargets_info(method: "search_targets", query: "TOP_GENE_SYMBOL", size: 5)
   → Ensembl ID, target class, known disease associations

   mcp__opentargets__opentargets_info(method: "get_target_details", id: "ENSG00000xxxxx")
   → Full gene profile: function, pathways, tractability, GO terms

2. Disease context for DE genes:
   mcp__opentargets__opentargets_info(method: "get_target_disease_associations", targetId: "ENSG00000xxxxx", diseaseId: "EFO_xxxxxxx")
   → Is this DE gene already linked to the disease of interest?

3. Reference expression context:
   mcp__gtex__gtex_data(method: "search_genes", query: "TOP_GENE_SYMBOL")
   → Get GENCODE ID for GTEx reference expression

   mcp__gtex__gtex_data(method: "get_median_gene_expression", gencodeId: "ENSG00000xxxxx.xx")
   → Normal tissue expression baseline — compare DE results against GTEx reference to assess whether changes are tissue-appropriate or aberrant

4. Literature evidence:
   mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_SYMBOL differential expression DISEASE_CONTEXT", num_results: 10)
   → Published DE studies mentioning this gene

5. Pathway enrichment (hand off to gene-enrichment skill):
   → Pass up-regulated gene list for ORA/GSEA
   → Pass down-regulated gene list separately
   → Pass full ranked list (by -log10(padj) * sign(log2FC)) for GSEA

6. gseapy for programmatic enrichment:
   import gseapy as gp
   enr = gp.enrichr(gene_list=up_gene_symbols, gene_sets='KEGG_2021_Human', organism='human')
   → Quick enrichment directly in the Python pipeline
```

---

## PyDESeq2 Code Template

### Complete Executable Pipeline

```python
import pandas as pd
import numpy as np
from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds import DeseqStats

# ---- 1. Load data ----
counts_df = pd.read_csv("counts.csv", index_col=0)  # genes x samples
metadata = pd.read_csv("metadata.csv", index_col=0)  # samples x covariates

# Ensure sample order matches
common_samples = counts_df.columns.intersection(metadata.index)
counts_df = counts_df[common_samples]
metadata = metadata.loc[common_samples]

# ---- 2. Validate ----
assert (counts_df >= 0).all().all(), "Negative counts detected"
assert counts_df.shape[1] == metadata.shape[0], "Sample count mismatch"
print(f"Genes: {counts_df.shape[0]}, Samples: {counts_df.shape[1]}")
print(f"Conditions: {metadata['condition'].value_counts().to_dict()}")

# ---- 3. Filter low-count genes ----
# Keep genes with at least 10 counts total across all samples
keep = counts_df.sum(axis=1) >= 10
counts_df = counts_df[keep]
print(f"Genes after filtering: {counts_df.shape[0]}")

# ---- 4. Create DESeq dataset ----
dds = DeseqDataSet(
    counts=counts_df,
    metadata=metadata,
    design="~ condition",
    refit_cooks=True,
    n_cpus=4
)

# ---- 5. Run full pipeline ----
dds.fit_size_factors()
dds.fit_genewise_dispersions()
dds.fit_dispersion_trend()
dds.fit_dispersion_prior()
dds.fit_MAP_dispersions()
dds.fit_LFC()
dds.calculate_cooks()

# ---- 6. Statistical testing ----
stat_res = DeseqStats(
    dds,
    contrast=["condition", "treatment", "control"],
    alpha=0.05,
    cooks_filter=True,
    independent_filter=True
)
stat_res.summary()
stat_res.lfc_shrink(coeff="condition_treatment_vs_control")

# ---- 7. Extract and filter results ----
results_df = stat_res.results_df
sig = results_df[(results_df['padj'] < 0.05) & (results_df['log2FoldChange'].abs() > 1)]
sig_sorted = sig.sort_values('padj')

print(f"\nSignificant DE genes: {len(sig)}")
print(f"Up-regulated: {(sig['log2FoldChange'] > 0).sum()}")
print(f"Down-regulated: {(sig['log2FoldChange'] < 0).sum()}")
print(sig_sorted.head(20))

# ---- 8. Save results ----
results_df.to_csv("deseq2_all_results.csv")
sig_sorted.to_csv("deseq2_significant_genes.csv")
```

---

## Input Handling

### Supported Formats

| Format | Extension | Detection | Notes |
|--------|-----------|-----------|-------|
| **CSV count matrix** | `.csv` | Default `pd.read_csv` | First column = gene IDs, columns = samples |
| **TSV count matrix** | `.tsv`, `.txt` | Tab-separated detection | Common for STAR/HTSeq output |
| **h5ad (AnnData)** | `.h5ad` | `anndata.read_h5ad` | Check `.X` or `.layers['counts']` for raw counts |
| **Feature counts** | `.txt` | Tab-separated, skip header lines | featureCounts output has extra annotation columns |

### Orientation Detection

```
Heuristic for genes x samples vs samples x genes:
- IF nrows >> ncols (e.g., 20000 x 6): genes x samples (CORRECT for PyDESeq2)
- IF ncols >> nrows (e.g., 6 x 20000): samples x genes → TRANSPOSE
- IF ambiguous: check if row names look like gene symbols/Ensembl IDs
- ALWAYS confirm with user if orientation is unclear
```

---

## Batch Effect Detection

### Decision Logic

```
1. Scan metadata columns for batch-like variables:
   - Column names containing: batch, run, lane, plate, flowcell, date, site, center
   - Categorical variables with fewer levels than samples

2. Confounding check:
   - Cross-tabulate batch x condition
   - IF each batch contains only one condition level:
     → CONFOUNDED: cannot separate batch from condition
     → Warn user: "Batch is perfectly confounded with condition. Cannot correct."
   - IF batches contain multiple conditions:
     → INCLUDE in design: ~ batch + condition

3. Design formula rules:
   - Variable of interest MUST be last term
   - Batch/covariates go before the condition
   - Do NOT include variables with as many levels as samples (= saturated model)
   - Continuous covariates (age, RIN) are included as-is
   - Categorical covariates (batch, sex) are auto-converted to dummy variables
```

---

## Multiple Testing Correction

### Benjamini-Hochberg (BH) Procedure

```
- PyDESeq2 applies BH correction by default (same as R DESeq2)
- Controls the False Discovery Rate (FDR) at the specified alpha level
- padj column = BH-adjusted p-values

Independent filtering (enabled by default):
- Removes genes with very low mean counts BEFORE multiple testing correction
- Increases statistical power by reducing the number of tests
- Threshold is automatically optimized to maximize discoveries at alpha = 0.05
```

### Interpretation Guide

| padj range | Interpretation | Recommendation |
|------------|---------------|----------------|
| < 0.001 | Very strong evidence | High-confidence DE gene |
| 0.001 - 0.01 | Strong evidence | Reliable DE gene |
| 0.01 - 0.05 | Moderate evidence | DE gene (standard threshold) |
| 0.05 - 0.1 | Suggestive | Consider for exploratory analysis only |
| > 0.1 | Not significant | Do not report as DE |

---

## Result Interpretation

### Volcano Plot Logic

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 8))

# Classify genes
results_df['category'] = 'Not significant'
results_df.loc[(results_df['padj'] < 0.05) & (results_df['log2FoldChange'] > 1), 'category'] = 'Up-regulated'
results_df.loc[(results_df['padj'] < 0.05) & (results_df['log2FoldChange'] < -1), 'category'] = 'Down-regulated'

colors = {'Not significant': 'grey', 'Up-regulated': 'red', 'Down-regulated': 'blue'}
for cat, color in colors.items():
    subset = results_df[results_df['category'] == cat]
    ax.scatter(subset['log2FoldChange'], -np.log10(subset['pvalue']),
               c=color, alpha=0.5, s=5, label=f"{cat} ({len(subset)})")

ax.axhline(-np.log10(0.05), ls='--', color='black', lw=0.5)
ax.axvline(1, ls='--', color='black', lw=0.5)
ax.axvline(-1, ls='--', color='black', lw=0.5)
ax.set_xlabel('log2 Fold Change')
ax.set_ylabel('-log10(p-value)')
ax.set_title('Volcano Plot')
ax.legend()
plt.tight_layout()
plt.savefig('volcano_plot.png', dpi=150)
```

### MA Plot Logic

```python
fig, ax = plt.subplots(figsize=(10, 6))

colors_ma = results_df['padj'].apply(lambda p: 'red' if p < 0.05 else 'grey')
ax.scatter(np.log10(results_df['baseMean'] + 1), results_df['log2FoldChange'],
           c=colors_ma, alpha=0.3, s=3)
ax.axhline(0, color='black', lw=0.5)
ax.axhline(1, ls='--', color='blue', lw=0.5)
ax.axhline(-1, ls='--', color='blue', lw=0.5)
ax.set_xlabel('log10(Mean Expression)')
ax.set_ylabel('log2 Fold Change')
ax.set_title('MA Plot (red = padj < 0.05)')
plt.tight_layout()
plt.savefig('ma_plot.png', dpi=150)
```

### Top DE Genes Table Format

```
| Rank | Gene | baseMean | log2FC | lfcSE | padj | Direction |
|------|------|----------|--------|-------|------|-----------|
| 1 | GENE_A | 1523.4 | 3.21 | 0.42 | 1.2e-12 | Up |
| 2 | GENE_B | 892.1 | -2.87 | 0.38 | 3.5e-11 | Down |
| 3 | GENE_C | 2104.7 | 2.54 | 0.35 | 8.7e-10 | Up |
```

---

## Boundary Rules

### What This Skill Does (COMPUTE)

```
DO:
- Write and execute PyDESeq2 Python code for differential expression
- Normalize counts (median-of-ratios via size factors)
- Estimate dispersions (gene-wise, trend, MAP shrinkage)
- Run Wald test with Benjamini-Hochberg correction
- Apply LFC shrinkage (apeglm)
- Filter results by padj and log2FC thresholds
- Generate volcano plots, MA plots, top gene tables
- Detect and handle batch effects in design formula
- Load CSV, TSV, and h5ad input formats
- Use gseapy for quick pathway enrichment on DE results
- Annotate top genes via MCP tools (Open Targets, NLM, PubMed)

DO NOT:
- Perform alignment or read mapping (upstream of this skill)
- Run single-cell DE analysis (use single-cell-analysis skill)
- Do deep pathway enrichment (hand off to gene-enrichment skill)
- Build protein interaction networks (use systems-biology skill)
- Assess target druggability (use target-research skill)
- Use edgeR or limma — this skill uses PyDESeq2 exclusively
```

### Tool Boundaries

| Task | Tool | Skill |
|------|------|-------|
| Differential expression | PyDESeq2 (Python) | This skill |
| Quick enrichment | gseapy (Python) | This skill |
| Deep pathway enrichment | ORA/GSEA multi-database | gene-enrichment |
| Gene annotation | MCP tools (Open Targets, NLM) | This skill |
| Network analysis | NetworkX, STRING | systems-biology |
| Single-cell DE | scanpy, pseudobulk | single-cell-analysis |
| Multi-omics integration | Factor analysis, correlation | multi-omics-integration |
| Target assessment | Open Targets, ChEMBL, DrugBank | target-research |

---

## Multi-Agent Workflow Examples

**"Run differential expression on my RNA-seq count matrix and find enriched pathways"**
1. RNA-seq DESeq2 -> Load counts, validate, run PyDESeq2 pipeline, filter DE genes, volcano/MA plots
2. Gene Enrichment -> ORA/GSEA on up- and down-regulated gene lists across GO/KEGG/Reactome/MSigDB
3. Systems Biology -> Network visualization of DE genes in enriched pathways, hub gene identification

**"Compare treatment vs control RNA-seq with batch correction, then assess druggable targets"**
1. RNA-seq DESeq2 -> Detect batch variable, include in design formula, run DE with batch correction
2. Target Research -> Target validation evidence for top DE genes
3. Drug Target Analyst -> Druggability assessment, existing compounds for top DE targets

**"Analyze RNA-seq data from cancer samples and identify therapeutic targets"**
1. RNA-seq DESeq2 -> DE analysis between tumor and normal, LFC shrinkage, result filtering
2. Gene Enrichment -> Pathway enrichment on DE genes, cancer hallmark gene sets
3. Systems Biology -> Protein interaction network of DE genes, identify hub nodes
4. Target Research -> Druggability and clinical evidence for hub DE genes

**"I have an h5ad file with bulk RNA-seq counts — find what's differentially expressed"**
1. RNA-seq DESeq2 -> Load h5ad, extract raw counts from .X or .layers, parse metadata from .obs, run full PyDESeq2 pipeline
2. Gene Enrichment -> Enrichment analysis on significant DE gene lists
3. Disease Research -> Disease associations for top DE genes via Open Targets

## Completeness Checklist

- [ ] Input data validated (raw integer counts, correct orientation, no negative values)
- [ ] Sample metadata inspected and design formula constructed (batch variables assessed)
- [ ] Low-count gene filtering applied before analysis
- [ ] PyDESeq2 pipeline executed (size factors, dispersion, Wald test, LFC shrinkage)
- [ ] Results filtered by padj and log2FC thresholds with up/down counts reported
- [ ] Volcano plot and MA plot generated and saved
- [ ] Top DE genes annotated via MCP tools (Open Targets, NLM, PubMed)
- [ ] Dispersion QC assessed (trend fit, Cook's distance outliers)
- [ ] Results CSV files saved (all results and significant genes)
- [ ] Report file finalized with no `[Analyzing...]` placeholders remaining
