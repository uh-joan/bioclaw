# DESeq2 Recipes

Computational recipes for DESeq2 differential expression analysis in R. Every recipe is a complete, runnable code block.

**Related skills:** `rnaseq-deseq2` (experimental design), `enrichment-recipes` (downstream pathway analysis), `statistical-modeling` (non-DE statistical tests).

---

### Recipe: Basic DESeq2 Pipeline
**When to use:** Standard two-condition differential expression from a raw count matrix.
**Input:** Count matrix CSV (genes x samples), sample metadata CSV.
**Output:** DESeqResults table with log2FC, pvalue, padj for all genes.

```r
library(DESeq2)

# Load data
counts <- read.csv("counts.csv", row.names = 1)
metadata <- read.csv("metadata.csv", row.names = 1)

# Ensure sample order matches
counts <- counts[, rownames(metadata)]

# Create DESeqDataSet
dds <- DESeqDataSetFromMatrix(
  countData = round(counts),
  colData   = metadata,
  design    = ~ condition
)

# Set reference level
dds$condition <- relevel(dds$condition, ref = "control")

# Run DESeq2
dds <- DESeq(dds)

# Extract results
res <- results(dds, contrast = c("condition", "treatment", "control"))
res <- res[order(res$padj), ]

# Summary
summary(res)

# Save
write.csv(as.data.frame(res), "deseq2_results.csv")
```

**Common pitfalls:**
- Counts must be raw (unnormalized) integers; `round()` handles fractional counts from alignment tools.
- Column order in counts must match row order in metadata — always reorder explicitly.
- Forgetting `relevel()` means R picks the alphabetically first level as reference.

---

### Recipe: LFC Shrinkage
**When to use:** Reduce noise in log2FC estimates, especially for genes with low counts or high dispersion.
**Input:** Fitted DESeqDataSet from `DESeq()`.
**Output:** Shrunken log2FC estimates with reduced variance.

```r
library(DESeq2)
library(apeglm)

# After running DESeq(dds)
# Option 1: apeglm (recommended — better for ranking genes)
resultsNames(dds)  # check coefficient names
res_shrunk <- lfcShrink(dds,
  coef = "condition_treatment_vs_control",
  type = "apeglm"
)

# Option 2: normal shrinkage (works with any contrast specification)
res_shrunk_normal <- lfcShrink(dds,
  contrast = c("condition", "treatment", "control"),
  type = "normal"
)

# Option 3: ashr (alternative to apeglm, allows contrast specification)
library(ashr)
res_shrunk_ashr <- lfcShrink(dds,
  contrast = c("condition", "treatment", "control"),
  type = "ashr"
)
```

**Common pitfalls:**
- `apeglm` requires `coef` (not `contrast`) — use `resultsNames(dds)` to find the exact coefficient name.
- `normal` and `ashr` accept `contrast`; `apeglm` does not.
- Use `apeglm` for ranking and visualization; use `normal` when you need arbitrary contrasts.

---

### Recipe: Custom Contrasts
**When to use:** Comparing specific conditions beyond simple pairwise (e.g., treatment A vs treatment B, or averaged contrasts).
**Input:** DESeqDataSet with multi-level factor.
**Output:** Results for the specified comparison.

```r
# Simple contrast: treatmentA vs treatmentB
res_ab <- results(dds, contrast = c("condition", "treatmentA", "treatmentB"))

# Numeric contrast vector (for complex comparisons)
# Example: average of treatmentA and treatmentB vs control
resultsNames(dds)
# Suppose: "Intercept", "condition_treatmentA_vs_control", "condition_treatmentB_vs_control"
res_avg <- results(dds, contrast = c(0, 0.5, 0.5))

# Interaction contrast (see Multi-factor recipe below)
# Compare the treatment effect across two genotypes
res_interaction <- results(dds, name = "genotypeKO.conditiontreated")
```

**Common pitfalls:**
- Numeric contrast vector length must match `length(resultsNames(dds))`.
- Order of names in `contrast = c("factor", "numerator", "denominator")` — numerator is what you want in the positive direction.
- For complex contrasts, double-check with `resultsNames(dds)` before specifying.

---

### Recipe: Multi-factor Design
**When to use:** Accounting for batch effects, genotype, or other covariates alongside the condition of interest.
**Input:** Metadata with multiple variables.
**Output:** Results adjusted for additional variables.

```r
# Design with batch correction
dds <- DESeqDataSetFromMatrix(
  countData = counts,
  colData   = metadata,
  design    = ~ batch + condition
)
# Variable of interest (condition) should be LAST in the formula

dds <- DESeq(dds)
res <- results(dds, contrast = c("condition", "treatment", "control"))

# Interaction design: does treatment effect differ by genotype?
dds_int <- DESeqDataSetFromMatrix(
  countData = counts,
  colData   = metadata,
  design    = ~ genotype + condition + genotype:condition
)
dds_int <- DESeq(dds_int)

# Main effect of condition (in reference genotype)
res_main <- results(dds_int, contrast = c("condition", "treatment", "control"))

# Interaction term: difference in treatment effect between genotypes
res_interaction <- results(dds_int, name = "genotypeKO.conditiontreatment")

# Treatment effect specifically in KO genotype
res_ko <- results(dds_int,
  contrast = list(
    c("condition_treatment_vs_control", "genotypeKO.conditiontreatment")
  )
)
```

**Common pitfalls:**
- Variable of interest must be last in the design formula for proper coefficient naming.
- Interaction terms use `.` to join factor levels — check `resultsNames(dds)`.
- With unbalanced designs, interaction models may have low power.

---

### Recipe: Filtering Results
**When to use:** Selecting significant DEGs by adjusted p-value, fold change, and expression level.
**Input:** DESeqResults object.
**Output:** Filtered gene lists.

```r
res_df <- as.data.frame(res)
res_df <- res_df[!is.na(res_df$padj), ]

# Standard filter: padj < 0.05, |log2FC| > 1
sig <- res_df[res_df$padj < 0.05 & abs(res_df$log2FoldChange) > 1, ]

# Strict filter: padj < 0.01, |log2FC| > 1.5, baseMean > 10
sig_strict <- res_df[
  res_df$padj < 0.01 &
  abs(res_df$log2FoldChange) > 1.5 &
  res_df$baseMean > 10,
]

# Relaxed for enrichment: padj < 0.05, |log2FC| > 0.5
sig_relaxed <- res_df[
  res_df$padj < 0.05 &
  abs(res_df$log2FoldChange) > 0.5,
]

# Count results
cat(sprintf("Total tested: %d\n", nrow(res_df)))
cat(sprintf("Significant (standard): %d\n", nrow(sig)))
cat(sprintf("  Up-regulated: %d\n", sum(sig$log2FoldChange > 0)))
cat(sprintf("  Down-regulated: %d\n", sum(sig$log2FoldChange < 0)))
```

**Common pitfalls:**
- Always remove NAs from padj before filtering — genes with low counts or outliers get NA.
- `log2FoldChange > 1` means 2-fold change; `> 0.585` means 1.5-fold change.
- baseMean filter removes genes with very low expression that may be unreliable.

---

### Recipe: Dispersion Estimates
**When to use:** Inspecting dispersion for QC, identifying overdispersed genes, or extracting dispersion values.
**Input:** Fitted DESeqDataSet.
**Output:** Dispersion values, dispersion plot.

```r
# Plot dispersion estimates
plotDispEsts(dds, main = "Dispersion Estimates")

# Extract dispersion values
dispersions <- mcols(dds)$dispersion
gene_disp <- data.frame(
  gene       = rownames(dds),
  dispersion = dispersions,
  baseMean   = mcols(dds)$baseMean
)
gene_disp <- gene_disp[order(-gene_disp$dispersion), ]

# Flag high-dispersion genes (> 95th percentile)
thresh <- quantile(dispersions, 0.95, na.rm = TRUE)
high_disp <- gene_disp[gene_disp$dispersion > thresh, ]

# Filter out high-dispersion genes before re-running
dds_filtered <- dds[!rownames(dds) %in% high_disp$gene, ]
dds_filtered <- DESeq(dds_filtered)
```

**Common pitfalls:**
- High dispersion may indicate biological variability, not just noise — inspect before removing.
- Dispersion plot should show points converging to the fitted curve; widespread scatter suggests poor model fit.

---

### Recipe: Volcano Plot
**When to use:** Visualizing the distribution of fold changes and significance.
**Input:** DESeqResults data frame.
**Output:** Publication-ready volcano plot.

```r
library(ggplot2)
library(ggrepel)

res_df <- as.data.frame(res)
res_df$gene <- rownames(res_df)
res_df <- res_df[!is.na(res_df$padj), ]

# Classify genes
res_df$status <- "NS"
res_df$status[res_df$padj < 0.05 & res_df$log2FoldChange > 1] <- "Up"
res_df$status[res_df$padj < 0.05 & res_df$log2FoldChange < -1] <- "Down"
res_df$status <- factor(res_df$status, levels = c("Down", "NS", "Up"))

# Top genes to label
top_genes <- head(res_df[order(res_df$padj), ], 10)

ggplot(res_df, aes(x = log2FoldChange, y = -log10(pvalue), color = status)) +
  geom_point(alpha = 0.5, size = 1) +
  scale_color_manual(values = c("Down" = "#2166ac", "NS" = "grey70", "Up" = "#b2182b")) +
  geom_vline(xintercept = c(-1, 1), linetype = "dashed", color = "grey40") +
  geom_hline(yintercept = -log10(0.05), linetype = "dashed", color = "grey40") +
  geom_text_repel(data = top_genes, aes(label = gene),
    size = 3, max.overlaps = 15, color = "black") +
  labs(x = "log2 Fold Change", y = "-log10(p-value)",
    title = "Volcano Plot", color = "Status") +
  theme_minimal() +
  theme(legend.position = "top")

ggsave("volcano_plot.pdf", width = 8, height = 6)
```

**Common pitfalls:**
- Use `pvalue` (not `padj`) for y-axis; padj can create visual artifacts with many ties.
- `ggrepel` prevents label overlap but may drop labels — increase `max.overlaps` if needed.
- Dashed lines should match your significance thresholds (adjust if using |LFC| > 0.5).

---

### Recipe: MA Plot
**When to use:** Visualizing fold change as a function of mean expression, comparing shrinkage effects.
**Input:** DESeqResults (shrunken and unshrunken).
**Output:** Side-by-side MA plots.

```r
# Basic MA plot
plotMA(res, ylim = c(-5, 5), main = "Unshrunken LFC")

# Shrunken MA plot
res_shrunk <- lfcShrink(dds, coef = "condition_treatment_vs_control", type = "apeglm")
plotMA(res_shrunk, ylim = c(-5, 5), main = "Shrunken LFC (apeglm)")

# Side-by-side comparison
par(mfrow = c(1, 2))
plotMA(res, ylim = c(-5, 5), main = "Unshrunken")
plotMA(res_shrunk, ylim = c(-5, 5), main = "apeglm Shrinkage")
par(mfrow = c(1, 1))

# Custom ggplot2 MA plot
library(ggplot2)
res_df <- as.data.frame(res_shrunk)
res_df$sig <- ifelse(!is.na(res_df$padj) & res_df$padj < 0.05, "Sig", "NS")

ggplot(res_df, aes(x = log10(baseMean), y = log2FoldChange, color = sig)) +
  geom_point(alpha = 0.4, size = 0.8) +
  scale_color_manual(values = c("NS" = "grey60", "Sig" = "red3")) +
  geom_hline(yintercept = 0, color = "blue", linewidth = 0.5) +
  labs(x = "log10(Mean Expression)", y = "log2 Fold Change") +
  theme_minimal()
```

**Common pitfalls:**
- Set `ylim` to avoid extreme outliers compressing the plot.
- Shrinkage primarily affects low-count genes — the MA plot makes this visible.

---

### Recipe: Extracting Gene Lists
**When to use:** Preparing gene lists for enrichment analysis (ORA or GSEA input).
**Input:** DESeqResults.
**Output:** Gene lists formatted for enrichment tools.

```r
res_df <- as.data.frame(res)
res_df$gene <- rownames(res_df)
res_df <- res_df[!is.na(res_df$padj), ]

# Up-regulated genes (for ORA)
up_genes <- res_df$gene[res_df$padj < 0.05 & res_df$log2FoldChange > 1]

# Down-regulated genes (for ORA)
down_genes <- res_df$gene[res_df$padj < 0.05 & res_df$log2FoldChange < -1]

# All significant genes (for ORA)
sig_genes <- res_df$gene[res_df$padj < 0.05 & abs(res_df$log2FoldChange) > 1]

# Ranked gene list for GSEA (by signed -log10 p-value)
res_df$rank_score <- -log10(res_df$pvalue) * sign(res_df$log2FoldChange)
ranked <- res_df[order(-res_df$rank_score), c("gene", "rank_score")]
ranked <- ranked[is.finite(ranked$rank_score), ]

# Alternative GSEA ranking: by log2FC (shrunken)
res_shrunk_df <- as.data.frame(res_shrunk)
res_shrunk_df$gene <- rownames(res_shrunk_df)
ranked_lfc <- res_shrunk_df[order(-res_shrunk_df$log2FoldChange), c("gene", "log2FoldChange")]
ranked_lfc <- ranked_lfc[!is.na(ranked_lfc$log2FoldChange), ]

# Save for external tools
writeLines(up_genes, "up_genes.txt")
writeLines(down_genes, "down_genes.txt")
write.csv(ranked, "ranked_genes.csv", row.names = FALSE)

# Background gene list (all expressed genes)
background <- res_df$gene
writeLines(background, "background_genes.txt")
```

**Common pitfalls:**
- For GSEA, use all genes (not just significant) — the method needs the full ranked list.
- Remove Inf/-Inf values from rank scores (from pvalue = 0).
- Use shrunken LFC for ranking when available — reduces noise-driven ranks.

---

### Recipe: Confidence Intervals for DEG Proportions
**When to use:** Reporting the proportion of DEGs with uncertainty (e.g., "5-8% of genes are DE").
**Input:** DESeqResults with significance calls.
**Output:** Wilson confidence interval for the proportion of DEGs.

```r
# Count DEGs
n_tested <- sum(!is.na(res$padj))
n_sig <- sum(res$padj < 0.05 & abs(res$log2FoldChange) > 1, na.rm = TRUE)

# Wilson CI (better than Wald for proportions)
prop_test <- prop.test(n_sig, n_tested, correct = FALSE)
ci <- prop_test$conf.int

cat(sprintf("DEGs: %d / %d (%.1f%%)\n", n_sig, n_tested, 100 * n_sig / n_tested))
cat(sprintf("95%% Wilson CI: [%.1f%%, %.1f%%]\n", 100 * ci[1], 100 * ci[2]))

# By direction
n_up <- sum(res$padj < 0.05 & res$log2FoldChange > 1, na.rm = TRUE)
n_down <- sum(res$padj < 0.05 & res$log2FoldChange < -1, na.rm = TRUE)
ci_up <- prop.test(n_up, n_tested, correct = FALSE)$conf.int
ci_down <- prop.test(n_down, n_tested, correct = FALSE)$conf.int

cat(sprintf("Up: %d (%.1f%%, CI [%.1f%%, %.1f%%])\n",
  n_up, 100 * n_up / n_tested, 100 * ci_up[1], 100 * ci_up[2]))
cat(sprintf("Down: %d (%.1f%%, CI [%.1f%%, %.1f%%])\n",
  n_down, 100 * n_down / n_tested, 100 * ci_down[1], 100 * ci_down[2]))
```

**Common pitfalls:**
- Wilson CI is preferred over Wald CI for proportions, especially when proportion is near 0 or 1.
- `correct = FALSE` gives the standard Wilson interval; `correct = TRUE` adds Yates continuity correction.

---

### Recipe: Venn Diagrams
**When to use:** Comparing DEG overlap across conditions, timepoints, or methods.
**Input:** Multiple DEG lists.
**Output:** Venn diagram and intersection gene lists.

```r
library(VennDiagram)
library(ggVennDiagram)

# Assume you have results from multiple comparisons
sig_A <- rownames(res_A)[!is.na(res_A$padj) & res_A$padj < 0.05 & abs(res_A$log2FoldChange) > 1]
sig_B <- rownames(res_B)[!is.na(res_B$padj) & res_B$padj < 0.05 & abs(res_B$log2FoldChange) > 1]
sig_C <- rownames(res_C)[!is.na(res_C$padj) & res_C$padj < 0.05 & abs(res_C$log2FoldChange) > 1]

# ggVennDiagram (ggplot2-based, recommended)
gene_lists <- list(
  "Condition A" = sig_A,
  "Condition B" = sig_B,
  "Condition C" = sig_C
)
ggVennDiagram(gene_lists, label_alpha = 0) +
  scale_fill_gradient(low = "white", high = "steelblue") +
  theme(legend.position = "none")
ggsave("venn_diagram.pdf", width = 6, height = 6)

# Extract intersections
shared_all <- Reduce(intersect, gene_lists)
shared_AB <- intersect(sig_A, sig_B)
unique_A <- setdiff(sig_A, union(sig_B, sig_C))

cat(sprintf("Shared across all: %d\n", length(shared_all)))
cat(sprintf("A & B only: %d\n", length(setdiff(shared_AB, sig_C))))
cat(sprintf("Unique to A: %d\n", length(unique_A)))
```

**Common pitfalls:**
- Venn diagrams work for up to ~5 sets; beyond that, use UpSet plots (`UpSetR` package).
- Ensure you are comparing the same gene ID type across all lists.
- Compare up and down regulated separately for biological interpretation.

---

### Recipe: Batch Effect Handling
**When to use:** Samples processed in different batches, sequencing runs, or by different operators.
**Input:** Metadata with batch variable.
**Output:** Batch-corrected DE results.

```r
# Method 1: Include batch in DESeq2 design (preferred)
dds <- DESeqDataSetFromMatrix(
  countData = counts,
  colData   = metadata,
  design    = ~ batch + condition  # batch first, condition last
)
dds <- DESeq(dds)
res <- results(dds, contrast = c("condition", "treatment", "control"))

# Method 2: Use sva for unknown batch effects
library(sva)
mod <- model.matrix(~ condition, data = metadata)
mod0 <- model.matrix(~ 1, data = metadata)
norm_counts <- counts(dds, normalized = TRUE)
svobj <- svaseq(norm_counts, mod, mod0, n.sv = 2)

# Add surrogate variables to metadata
metadata$SV1 <- svobj$sv[, 1]
metadata$SV2 <- svobj$sv[, 2]
dds_sva <- DESeqDataSetFromMatrix(
  countData = counts,
  colData   = metadata,
  design    = ~ SV1 + SV2 + condition
)
dds_sva <- DESeq(dds_sva)
res_sva <- results(dds_sva, contrast = c("condition", "treatment", "control"))

# Visualize batch effect with PCA (before/after)
vsd <- vst(dds, blind = TRUE)
plotPCA(vsd, intgroup = c("condition", "batch"))

# removeBatchEffect for visualization only (NOT for DE)
library(limma)
mat <- assay(vsd)
mat_corrected <- removeBatchEffect(mat, batch = vsd$batch)
assay(vsd) <- mat_corrected
plotPCA(vsd, intgroup = "condition")
```

**Common pitfalls:**
- Never use batch-corrected counts as input to DESeq2 — include batch in the design formula instead.
- `removeBatchEffect` is for visualization/PCA only, not for DE analysis.
- If batch is confounded with condition, no statistical method can separate them.

---

### Recipe: Count Data Preprocessing
**When to use:** Before running DESeq2 — filtering low-count genes and verifying data quality.
**Input:** Raw count matrix.
**Output:** Filtered count matrix ready for DESeq2.

```r
# Filter low-count genes
# Rule of thumb: keep genes with >= 10 counts in >= N samples
# where N = smallest group size
min_samples <- min(table(metadata$condition))
keep <- rowSums(counts >= 10) >= min_samples
counts_filtered <- counts[keep, ]
cat(sprintf("Genes before filtering: %d\n", nrow(counts)))
cat(sprintf("Genes after filtering: %d\n", nrow(counts_filtered)))

# Alternative: DESeq2's independent filtering (automatic)
# DESeq2 automatically filters by default via results()
# To adjust: results(dds, independentFiltering = TRUE, alpha = 0.05)

# Check library sizes
lib_sizes <- colSums(counts_filtered)
barplot(lib_sizes / 1e6, las = 2, main = "Library Sizes (millions)",
  ylab = "Reads (millions)", col = "steelblue")

# Check for outlier samples via PCA
dds_qc <- DESeqDataSetFromMatrix(counts_filtered, metadata, ~ condition)
vsd <- vst(dds_qc, blind = TRUE)
plotPCA(vsd, intgroup = "condition")

# Normalized counts (for downstream use, NOT for DESeq2 input)
dds_qc <- estimateSizeFactors(dds_qc)
norm_counts <- counts(dds_qc, normalized = TRUE)
write.csv(norm_counts, "normalized_counts.csv")
```

**Common pitfalls:**
- DESeq2 expects raw counts — never normalize before input.
- Pre-filtering is optional (DESeq2 handles it) but improves speed and multiple testing correction.
- VST/rlog are for visualization and clustering, not for DE testing.

---

## Parameter Reference

| Parameter | Default | When to change |
|-----------|---------|----------------|
| `alpha` (in `results()`) | 0.1 | Set to 0.05 for standard significance threshold |
| `lfcThreshold` (in `results()`) | 0 | Set > 0 for testing against a minimum fold change (e.g., 0.585 for 1.5-fold) |
| `independentFiltering` | TRUE | Set FALSE to disable automatic low-count gene filtering |
| `cooksCutoff` | TRUE | Set FALSE to keep outlier genes in results |
| `pAdjustMethod` | "BH" | Change to "bonferroni" for very conservative testing |
| `altHypothesis` | "greaterAbs" | Use "greater" or "less" for one-sided tests |
| `shrinkage type` | (none by default) | Use "apeglm" for coef-based, "ashr" or "normal" for contrast-based |
| `minReplicatesForReplace` | 7 | Lower to allow outlier replacement with fewer replicates |
| `fitType` | "parametric" | Use "local" or "mean" if parametric fit fails |
| `test` | "Wald" | Use "LRT" for likelihood ratio test (multi-level factors, reduced models) |
| `blind` (in `vst`/`rlog`) | TRUE | Set FALSE when using for visualization after fitting a model |
