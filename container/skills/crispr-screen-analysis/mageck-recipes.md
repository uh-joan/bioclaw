# MAGeCK & CRISPR Screen Analysis Recipes

Code templates for MAGeCK command-line workflows, CRISPR screen downstream analysis, quality control, and alternative screen analysis tools (JACKS, CRISPResso2).

Cross-skill routing: use `gene-enrichment` for pathway enrichment of screen hits, `systems-biology` for network analysis of essential genes.

---

## 1. MAGeCK count: Library File Preparation and Sample Label Mapping

Quantify sgRNA abundance from raw FASTQ files.

```bash
# ---- Library file format (tab-separated) ----
# Required columns: sgRNA_name, sgRNA_sequence, gene
# Example library.tsv:
# sgRNA          sequence             gene
# TP53_sg1       AACCGGTTAATCGCATGCG  TP53
# TP53_sg2       GCGATCGATCGTAGCTAGC  TP53
# NTC_001        AATCGATCGATCGATCGAT  Non-targeting
# NTC_002        TCGATCGATCGATCGATCG  Non-targeting

# ---- MAGeCK count ----
mageck count \
    --list-seq library.tsv \
    --fastq sample1_R1.fastq.gz sample2_R1.fastq.gz sample3_R1.fastq.gz \
            sample4_R1.fastq.gz sample5_R1.fastq.gz sample6_R1.fastq.gz \
    --sample-label T0_rep1,T0_rep2,T0_rep3,T14_rep1,T14_rep2,T14_rep3 \
    --output-prefix screen_counts \
    --norm-method median \
    --sgRNA-len 20 \
    --trim-5 CACCG \
    --control-sgrna NTC_guides.txt
    # NTC_guides.txt: one non-targeting sgRNA name per line

# Output files:
# screen_counts.count.txt        - raw count matrix (sgRNAs x samples)
# screen_counts.count_normalized.txt - normalized counts
# screen_counts_summary.txt      - mapping statistics per sample
```

```python
# ---- Verify count output ----
import pandas as pd

counts = pd.read_csv("screen_counts.count.txt", sep="\t")
print(f"Guides: {len(counts)}")
print(f"Columns: {list(counts.columns)}")
print(f"\nMapping summary:")
summary = pd.read_csv("screen_counts_summary.txt", sep="\t")
print(summary.to_string(index=False))

# Check for expected guide coverage
zero_count = (counts.iloc[:, 2:] == 0).sum()
print(f"\nZero-count guides per sample:")
print(zero_count)
```

**Key parameters**: `--sgRNA-len` must match your library design. `--trim-5 CACCG` removes the vector constant upstream of the guide. `--norm-method median` uses median-ratio normalization (robust to dropout). Always provide `--control-sgrna` for proper normalization anchoring.

---

## 2. MAGeCK test: RRA for Hit Identification

Robust Rank Aggregation to identify significantly enriched or depleted genes.

```bash
# ---- Basic MAGeCK test ----
mageck test \
    --count-table screen_counts.count.txt \
    --treatment-id T14_rep1,T14_rep2,T14_rep3 \
    --control-id T0_rep1,T0_rep2,T0_rep3 \
    --output-prefix mageck_test \
    --normcounts-to-file \
    --norm-method median \
    --gene-lfc-method median \
    --control-sgrna NTC_guides.txt \
    --adjust-method fdr

# Output files:
# mageck_test.gene_summary.txt   - gene-level RRA scores and LFC
# mageck_test.sgrna_summary.txt  - guide-level LFC and p-values
# mageck_test.normalized.txt     - normalized count matrix
```

```python
import pandas as pd

# ---- Parse gene-level results ----
gene_results = pd.read_csv("mageck_test.gene_summary.txt", sep="\t")

print(f"Genes tested: {len(gene_results)}")

# Negative selection (dropout) hits
neg_hits = gene_results[gene_results["neg|fdr"] < 0.05].sort_values("neg|fdr")
print(f"\nNegative selection hits (FDR < 0.05): {len(neg_hits)}")
print(neg_hits[["id", "neg|score", "neg|fdr", "neg|lfc"]].head(20).to_string(index=False))

# Positive selection (enrichment) hits
pos_hits = gene_results[gene_results["pos|fdr"] < 0.05].sort_values("pos|fdr")
print(f"\nPositive selection hits (FDR < 0.05): {len(pos_hits)}")
print(pos_hits[["id", "pos|score", "pos|fdr", "pos|lfc"]].head(20).to_string(index=False))

# ---- Parse guide-level results ----
sgrna_results = pd.read_csv("mageck_test.sgrna_summary.txt", sep="\t")
print(f"\nGuide-level summary:")
print(f"  Total guides: {len(sgrna_results)}")
print(f"  Mean LFC: {sgrna_results['LFC'].mean():.3f}")
print(f"  Median LFC: {sgrna_results['LFC'].median():.3f}")

# Check concordance for top hits
for gene in neg_hits["id"].head(5):
    guides = sgrna_results[sgrna_results["Gene"] == gene]
    n_neg = (guides["LFC"] < 0).sum()
    print(f"  {gene}: {n_neg}/{len(guides)} guides depleted, "
          f"LFCs: {guides['LFC'].values.round(2)}")
```

**Expected output**: `neg|fdr` and `pos|fdr` columns contain FDR-corrected p-values for depletion and enrichment respectively. `neg|score` is the RRA score (lower = more significant depletion). Check guide concordance for top hits to ensure signal is not driven by a single guide.

---

## 3. MAGeCK mle: Maximum Likelihood Estimation with Design Matrix

For complex experimental designs with multiple conditions, covariates, or time points.

```bash
# ---- Create design matrix ----
# design_matrix.txt (tab-separated):
# Samples       baseline    treatment
# T0_rep1       1           0
# T0_rep2       1           0
# T0_rep3       1           0
# T14_drug_rep1 1           1
# T14_drug_rep2 1           1
# T14_drug_rep3 1           1

# ---- MAGeCK mle ----
mageck mle \
    --count-table screen_counts.count.txt \
    --design-matrix design_matrix.txt \
    --output-prefix mageck_mle \
    --norm-method median \
    --control-sgrna NTC_guides.txt \
    --genes-varmodeling 1000 \
    --permutation-round 10

# Output:
# mageck_mle.gene_summary.txt  - beta scores (effect sizes) per condition
# mageck_mle.sgrna_summary.txt - guide-level results
```

```python
import pandas as pd
import numpy as np

# ---- Parse MLE results ----
mle_results = pd.read_csv("mageck_mle.gene_summary.txt", sep="\t")

# Beta scores represent the effect size of each condition on gene fitness
# Negative beta = gene depletion (essential under that condition)
# Positive beta = gene enrichment

print("MLE gene-level columns:", list(mle_results.columns))

# Filter for treatment effect
# Column naming: {condition}|beta, {condition}|z, {condition}|p-value, {condition}|fdr
treatment_hits = mle_results[mle_results["treatment|fdr"] < 0.05].sort_values("treatment|fdr")
print(f"\nSignificant treatment effects (FDR < 0.05): {len(treatment_hits)}")
print(treatment_hits[["Gene", "treatment|beta", "treatment|z", "treatment|fdr"]].head(20).to_string(index=False))

# Sensitizers (negative beta = depleted with treatment, not without)
sensitizers = treatment_hits[treatment_hits["treatment|beta"] < -0.5]
print(f"\nSensitizers (beta < -0.5): {len(sensitizers)}")

# Resistance genes (positive beta = enriched with treatment)
resistance = treatment_hits[treatment_hits["treatment|beta"] > 0.5]
print(f"Resistance genes (beta > 0.5): {len(resistance)}")

# ---- Multi-condition comparison ----
# For designs with multiple treatment conditions:
# Plot beta scores across conditions
import matplotlib.pyplot as plt

if "conditionA|beta" in mle_results.columns and "conditionB|beta" in mle_results.columns:
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.scatter(mle_results["conditionA|beta"], mle_results["conditionB|beta"],
               s=5, alpha=0.3, c="gray")
    sig = mle_results[(mle_results["conditionA|fdr"] < 0.05) | (mle_results["conditionB|fdr"] < 0.05)]
    ax.scatter(sig["conditionA|beta"], sig["conditionB|beta"], s=15, alpha=0.6, c="red")
    ax.set_xlabel("Condition A beta"); ax.set_ylabel("Condition B beta")
    ax.axhline(0, ls="--", c="black", lw=0.5); ax.axvline(0, ls="--", c="black", lw=0.5)
    ax.set_title("Beta Score Comparison")
    plt.savefig("mle_beta_comparison.png", dpi=150, bbox_inches="tight")
```

**Key parameters**: `--genes-varmodeling 1000` uses top 1000 genes for variance estimation. `--permutation-round 10` controls p-value accuracy. Design matrix rows must match sample labels in the count table exactly.

---

## 4. MAGeCK pathway: Gene Set Enrichment on Screen Results

Test whether predefined gene sets are collectively enriched or depleted.

```bash
# ---- MAGeCK pathway ----
mageck pathway \
    --gene-ranking mageck_test.gene_summary.txt \
    --gmt-file pathways.gmt \
    --output-prefix mageck_pathway \
    --single-ranking
    # --single-ranking uses neg|rank for analysis

# GMT file format (tab-separated):
# PATHWAY_NAME\tDESCRIPTION\tGENE1\tGENE2\tGENE3...
```

```python
import pandas as pd

# ---- Parse pathway results ----
pathway_results = pd.read_csv("mageck_pathway.pathway_results.txt", sep="\t")
sig_pathways = pathway_results[pathway_results["FDR"] < 0.25].sort_values("FDR")

print(f"Tested pathways: {len(pathway_results)}")
print(f"Significant (FDR < 0.25): {len(sig_pathways)}")
print(sig_pathways[["Pathway", "NES", "FDR", "Size"]].head(15).to_string(index=False))

# ---- Alternative: GSEApy on MAGeCK gene rankings ----
import gseapy as gp
import numpy as np

gene_summary = pd.read_csv("mageck_test.gene_summary.txt", sep="\t")

# Create ranking from RRA scores (lower score = more depleted)
gene_summary["rank_metric"] = -np.log10(gene_summary["neg|score"].clip(lower=1e-300))
ranked = gene_summary[["id", "rank_metric"]].rename(columns={"id": "gene"})
ranked = ranked.sort_values("rank_metric", ascending=False)

# Run GSEA
for lib in ["KEGG_2021_Human", "GO_Biological_Process_2021", "Reactome_2022"]:
    res = gp.prerank(rnk=ranked.set_index("gene")["rank_metric"],
                      gene_sets=lib, outdir=f"screen_gsea_{lib}",
                      min_size=15, max_size=500, permutation_num=1000)
    sig = res.res2d[res.res2d["FDR q-val"].astype(float) < 0.25]
    print(f"\n{lib}: {len(sig)} significant gene sets")
    if len(sig) > 0:
        print(sig.head(10)[["Term", "NES", "FDR q-val"]].to_string(index=False))
```

**Expected output**: Pathways enriched among screen hits. Negative NES indicates collective depletion (essential pathway); positive NES indicates collective enrichment. Cross-validate with Recipe 2 individual gene hits.

---

## 5. MAGeCK flute: Downstream Visualization (FluteMLE, FluteRRA)

Comprehensive visualization suite for MAGeCK results.

```R
library(MAGeCKFlute)

# ---- FluteRRA: visualize MAGeCK test results ----
# Input: gene_summary from mageck test
FluteRRA(
    gene_summary  = "mageck_test.gene_summary.txt",
    sgrna_summary = "mageck_test.sgrna_summary.txt",
    prefix        = "flute_rra",
    organism      = "hsa",           # "hsa", "mmu", etc.
    outdir        = "flute_output/",
    incorporateDepmap = FALSE,        # set TRUE to overlay DepMap data
    omitEssential = TRUE,             # remove common essentials from plots
    top           = 10,               # number of top genes to label
    pvalueCutoff  = 0.05
)

# Output includes:
# - Volcano plot (neg|score vs LFC)
# - Rank plot
# - sgRNA LFC distribution per gene
# - Pathway enrichment bubble plots
# - 9-square plot (RRA rank vs LFC)

# ---- FluteMLE: visualize MAGeCK mle results ----
FluteMLE(
    gene_summary  = "mageck_mle.gene_summary.txt",
    prefix        = "flute_mle",
    organism      = "hsa",
    outdir        = "flute_output/",
    treatname     = "treatment",      # condition name from design matrix
    top           = 10,
    pvalueCutoff  = 0.05,
    incorporateDepmap = FALSE
)

# Output includes:
# - Beta score distribution
# - 9-square plot (beta vs significance)
# - Pathway enrichment on significant genes
# - Essential gene benchmarking
```

```python
# ---- Python alternative: custom MAGeCK visualization ----
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

gene_results = pd.read_csv("mageck_test.gene_summary.txt", sep="\t")

# 9-square plot (rank vs LFC)
fig, ax = plt.subplots(figsize=(10, 8))
neg_log_rra = -np.log10(gene_results["neg|score"].clip(lower=1e-300))
colors = np.where(gene_results["neg|fdr"] < 0.05, "blue",
          np.where(gene_results["pos|fdr"] < 0.05, "red", "gray"))
ax.scatter(gene_results["neg|lfc"], neg_log_rra, c=colors, s=8, alpha=0.5)

# Label top hits
for _, row in gene_results.nsmallest(10, "neg|fdr").iterrows():
    ax.annotate(row["id"], (row["neg|lfc"], -np.log10(max(row["neg|score"], 1e-300))),
                fontsize=7, alpha=0.8)

ax.set_xlabel("Median Log2 Fold Change")
ax.set_ylabel("-log10(RRA Score)")
ax.set_title("MAGeCK RRA Gene-Level Results")
ax.axhline(-np.log10(0.05), ls="--", c="black", lw=0.5)
plt.savefig("mageck_9square.png", dpi=150, bbox_inches="tight")
plt.close()
```

**Expected output**: FluteMLE/FluteRRA produce comprehensive multi-panel reports including volcano plots, pathway bubbles, and essential gene benchmarks. The Python alternative generates a 9-square plot for quick visual assessment.

---

## 6. JACKS: Joint Analysis of CRISPR Knockouts

Alternative to MAGeCK that models guide efficacy jointly across replicates.

```python
# JACKS uses a Bayesian hierarchical model to jointly estimate:
# 1. Gene essentiality scores
# 2. Per-guide efficacy (how well each guide cuts)

# ---- Install ----
# pip install jacks

import jacks.jacks as jacks_module
import pandas as pd
import numpy as np

def run_jacks(count_file, replicate_map_file, guidemap_file, ctrl_genes=None):
    """Run JACKS analysis on CRISPR screen data.

    Parameters
    ----------
    count_file : str
        Tab-separated count matrix (guides x samples). First column = guide ID.
    replicate_map_file : str
        Tab-separated: replicate_id, sample_id, control_or_treatment.
        Example:
        T0_rep1    T0    ctrl
        T14_rep1   T14   treatment
    guidemap_file : str
        Tab-separated: guide_id, gene, guide_sequence.
    ctrl_genes : list or None
        Non-targeting control gene names for calibration.

    Returns
    -------
    tuple of (gene_scores, gene_pvalues, guide_efficacy).
    """
    # Load data
    counts = pd.read_csv(count_file, sep="\t", index_col=0)
    replicate_map = pd.read_csv(replicate_map_file, sep="\t", header=None,
                                 names=["replicate", "sample", "condition"])
    guidemap = pd.read_csv(guidemap_file, sep="\t", index_col=0)

    # JACKS expects: counts_dict, gene_guide_dict, replicate_map
    gene_guide = guidemap.groupby("gene").apply(lambda x: x.index.tolist()).to_dict()

    # Run JACKS
    jacks_results = jacks_module.run_JACKS(
        data=counts,
        gene_grna_group=guidemap["gene"].to_dict(),
        cond_sample_map=replicate_map.set_index("replicate")["sample"].to_dict(),
        ctrl_samples=[r for r, c in zip(replicate_map["replicate"],
                      replicate_map["condition"]) if c == "ctrl"],
    )

    # Extract results
    gene_scores = jacks_results[0]  # JACKS gene scores (log-scale)
    gene_stds = jacks_results[1]    # Standard deviations
    guide_efficacy = jacks_results[4]  # Per-guide efficacy estimates

    # Convert to DataFrame
    results_df = pd.DataFrame({
        "gene": list(gene_scores.keys()),
        "jacks_score": [gene_scores[g] for g in gene_scores],
        "jacks_std": [gene_stds[g] for g in gene_scores],
    })
    results_df["z_score"] = results_df["jacks_score"] / results_df["jacks_std"]

    # Calibrate against controls
    if ctrl_genes:
        ctrl_scores = results_df[results_df["gene"].isin(ctrl_genes)]["jacks_score"]
        ctrl_mean = ctrl_scores.mean()
        ctrl_std = ctrl_scores.std()
        results_df["calibrated_z"] = (results_df["jacks_score"] - ctrl_mean) / ctrl_std

    results_df = results_df.sort_values("jacks_score")
    print(f"JACKS results: {len(results_df)} genes")
    print(f"Top depleted genes:")
    print(results_df.head(15)[["gene", "jacks_score", "jacks_std", "z_score"]].to_string(index=False))

    return results_df, guide_efficacy

# Usage
results, efficacy = run_jacks(
    "screen_counts.count.txt",
    "replicate_map.txt",
    "guide_map.txt",
    ctrl_genes=["Non-targeting"]
)
```

**Key parameters**: JACKS explicitly models guide efficacy, making it more robust to variable guide quality than MAGeCK RRA. Best used when you have matched replicate structure. The `guide_efficacy` output can identify poorly-performing guides for library optimization.

---

## 7. CRISPResso2: Amplicon Editing Quantification

Quantify indel frequencies and editing outcomes for individual guide validation.

```bash
# ---- Single amplicon analysis ----
CRISPResso \
    --fastq_r1 sample_R1.fastq.gz \
    --fastq_r2 sample_R2.fastq.gz \
    --amplicon_seq ATCGATCGATCG...FULL_AMPLICON_SEQUENCE...GCTAGCTAGCTA \
    --guide_seq AACCGGTTAATCGCATGCG \
    --output_folder crispresso_output/ \
    --name TP53_sg1 \
    --min_frequency_alleles_around_cut_to_plot 0.05 \
    --quantification_window_size 10 \
    --plot_window_size 20

# ---- Batch analysis (multiple guides/samples) ----
# Create batch file (tab-separated):
# name    fastq_r1               fastq_r2               amplicon_seq    guide_seq
# TP53_s1 TP53_sample1_R1.fq.gz  TP53_sample1_R2.fq.gz  ATCG...        AACCGG...
# TP53_s2 TP53_sample2_R1.fq.gz  TP53_sample2_R2.fq.gz  ATCG...        AACCGG...

CRISPRessoBatch \
    --batch_settings batch_file.txt \
    --output_folder crispresso_batch/ \
    --min_average_read_quality 30 \
    --min_single_bp_quality 20
```

```python
import pandas as pd
import json
import os

def parse_crispresso_results(output_dir):
    """Parse CRISPResso2 output to extract editing efficiency.

    Parameters
    ----------
    output_dir : str
        CRISPResso output directory.

    Returns
    -------
    dict with editing metrics.
    """
    # Load quantification
    quant_file = os.path.join(output_dir, "CRISPResso_quantification_of_editing_frequency.txt")
    quant = pd.read_csv(quant_file, sep="\t")

    total_reads = quant["Reads_aligned"].sum()
    nhej = quant.loc[quant["Reference"] == "Reference", "Unmodified%"].values
    modified = quant.loc[quant["Reference"] == "Reference", "Modified%"].values

    results = {
        "total_aligned_reads": total_reads,
        "unmodified_pct": float(nhej[0]) if len(nhej) > 0 else None,
        "modified_pct": float(modified[0]) if len(modified) > 0 else None,
    }

    # Parse allele frequencies
    allele_file = os.path.join(output_dir, "Alleles_frequency_table.zip")
    if os.path.exists(allele_file):
        alleles = pd.read_csv(allele_file, sep="\t", compression="zip")
        results["n_unique_alleles"] = len(alleles)
        results["top_allele_pct"] = alleles.iloc[0]["#Reads"] / total_reads * 100 if total_reads > 0 else 0

    print(f"Editing efficiency: {results['modified_pct']:.1f}%")
    print(f"Total reads: {results['total_aligned_reads']}")
    return results

# Usage
for sample_dir in os.listdir("crispresso_batch/"):
    full_path = os.path.join("crispresso_batch/", sample_dir)
    if os.path.isdir(full_path):
        print(f"\n{sample_dir}:")
        parse_crispresso_results(full_path)
```

**Expected output**: Editing efficiency (% modified reads), indel size distribution, and allele frequency table. Use to validate individual guide performance from pooled screen hits.

---

## 8. Quality Metrics: Gini Index, Zero-Count Guides, Mapping Rate

Comprehensive QC metrics for CRISPR screen data.

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def comprehensive_screen_qc(count_file, library_file=None, ntc_label="Non-targeting"):
    """Compute full QC metrics for a CRISPR screen.

    Parameters
    ----------
    count_file : str
        Tab-separated count matrix (guides x samples).
    library_file : str or None
        Guide library with gene annotations.
    ntc_label : str
        Label for non-targeting control genes.

    Returns
    -------
    pd.DataFrame with QC metrics per sample.
    """
    counts = pd.read_csv(count_file, sep="\t", index_col=0)
    if "Gene" in counts.columns:
        gene_col = counts["Gene"]
        counts = counts.drop("Gene", axis=1)
    elif library_file:
        lib = pd.read_csv(library_file, sep="\t", index_col=0)
        gene_col = lib["gene"]
    else:
        gene_col = None

    qc = pd.DataFrame(index=counts.columns)

    # Basic counts
    qc["total_reads"] = counts.sum()
    qc["total_guides_detected"] = (counts > 0).sum()
    qc["pct_guides_detected"] = qc["total_guides_detected"] / len(counts) * 100
    qc["zero_count_guides"] = (counts == 0).sum()
    qc["pct_zero"] = qc["zero_count_guides"] / len(counts) * 100

    # Distribution metrics
    qc["mean_count"] = counts.mean()
    qc["median_count"] = counts.median()
    qc["max_count"] = counts.max()

    # Gini index (inequality of guide representation)
    def gini(arr):
        arr = np.sort(arr.astype(float))
        n = len(arr)
        idx = np.arange(1, n + 1)
        total = np.sum(arr)
        if total == 0:
            return 1.0
        return (2 * np.sum(idx * arr) / (n * total)) - (n + 1) / n

    qc["gini_index"] = counts.apply(gini)

    # Top guide concentration
    qc["top10_pct"] = counts.apply(lambda x: x.nlargest(10).sum() / x.sum() * 100)
    qc["top100_pct"] = counts.apply(lambda x: x.nlargest(100).sum() / x.sum() * 100)

    # NTC behavior
    if gene_col is not None:
        ntc_mask = gene_col.str.contains(ntc_label, case=False, na=False)
        ntc_counts = counts.loc[ntc_mask]
        qc["ntc_mean"] = ntc_counts.mean()
        qc["ntc_median"] = ntc_counts.median()
        qc["ntc_cv"] = ntc_counts.std() / ntc_counts.mean()

    # Replicate correlation
    corr = counts.corr(method="pearson")

    # Print results
    print("=" * 80)
    print("CRISPR Screen QC Report")
    print("=" * 80)
    print(f"Library size: {len(counts)} guides")
    print(f"\nPer-sample metrics:")
    print(qc.round(2).to_string())
    print(f"\nReplicate correlations:")
    print(corr.round(3).to_string())

    # Quality flags
    print("\nQuality flags:")
    for sample in qc.index:
        flags = []
        if qc.loc[sample, "pct_zero"] > 5:
            flags.append(f"HIGH_ZERO_GUIDES ({qc.loc[sample, 'pct_zero']:.1f}%)")
        if qc.loc[sample, "gini_index"] > 0.2:
            flags.append(f"HIGH_GINI ({qc.loc[sample, 'gini_index']:.3f})")
        if qc.loc[sample, "total_reads"] < 10_000_000:
            flags.append(f"LOW_READS ({qc.loc[sample, 'total_reads']:,})")
        if flags:
            print(f"  {sample}: {', '.join(flags)}")
        else:
            print(f"  {sample}: PASS")

    # QC plots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Count distribution
    for col in counts.columns:
        axes[0, 0].hist(np.log10(counts[col] + 1), bins=50, alpha=0.4, label=col)
    axes[0, 0].set_xlabel("log10(count+1)"); axes[0, 0].set_title("Count Distribution")
    axes[0, 0].legend(fontsize=6)

    # Gini barplot
    qc["gini_index"].plot.bar(ax=axes[0, 1], color="steelblue")
    axes[0, 1].axhline(0.2, ls="--", c="red", label="Threshold (0.2)")
    axes[0, 1].set_title("Gini Index"); axes[0, 1].legend()

    # Zero-count barplot
    qc["pct_zero"].plot.bar(ax=axes[1, 0], color="coral")
    axes[1, 0].axhline(5, ls="--", c="red", label="Threshold (5%)")
    axes[1, 0].set_title("% Zero-Count Guides"); axes[1, 0].legend()

    # Correlation heatmap
    import seaborn as sns
    sns.heatmap(corr, annot=True, fmt=".3f", cmap="YlGnBu", ax=axes[1, 1])
    axes[1, 1].set_title("Replicate Correlation")

    plt.tight_layout()
    plt.savefig("screen_qc_report.png", dpi=150, bbox_inches="tight")
    plt.close()

    return qc, corr

# Usage
qc_metrics, correlations = comprehensive_screen_qc(
    "screen_counts.count.txt", ntc_label="Non-targeting"
)
```

**Expected output**: QC table with flags per sample. Good screens: Gini < 0.1, zero-count < 1%, replicate r > 0.95, total reads > 10M.

---

## 9. Normalization Strategies: Median Ratio, Total Count, Control Guides

Compare and select normalization approaches.

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def compare_normalizations(counts, ntc_guides=None, pseudocount=0.5):
    """Apply and compare multiple normalization strategies.

    Parameters
    ----------
    counts : pd.DataFrame
        Raw guide count matrix (guides x samples).
    ntc_guides : list or None
        Non-targeting control guide names.
    pseudocount : float
        Added before log transformation.

    Returns
    -------
    dict of {method_name: normalized_counts_df}.
    """
    results = {}

    # 1. Total count normalization
    target = counts.sum().median()
    tc_norm = counts * (target / counts.sum())
    results["total_count"] = tc_norm

    # 2. Median ratio normalization (DESeq2-style)
    log_counts = np.log(counts + pseudocount)
    geo_mean = log_counts.mean(axis=1)
    valid = geo_mean > np.log(pseudocount)
    ratios = log_counts.loc[valid].subtract(geo_mean[valid], axis=0)
    size_factors = np.exp(ratios.median(axis=0))
    mr_norm = counts / size_factors
    results["median_ratio"] = mr_norm
    print(f"Median ratio size factors: {size_factors.to_dict()}")

    # 3. Control-based normalization
    if ntc_guides and len(ntc_guides) > 0:
        ntc = counts.loc[counts.index.isin(ntc_guides)]
        ntc_median = ntc.median()
        ref = ntc_median.median()
        ctrl_factors = ref / ntc_median
        ctrl_norm = counts * ctrl_factors
        results["control_based"] = ctrl_norm
        print(f"Control-based factors: {ctrl_factors.to_dict()}")

    # 4. Upper-quartile normalization
    q75 = counts[counts > 0].quantile(0.75)
    uq_factors = q75.median() / q75
    uq_norm = counts * uq_factors
    results["upper_quartile"] = uq_norm

    # Compare distributions after normalization
    fig, axes = plt.subplots(1, len(results), figsize=(5 * len(results), 4))
    if len(results) == 1:
        axes = [axes]
    for ax, (method, norm_counts) in zip(axes, results.items()):
        for col in norm_counts.columns:
            ax.hist(np.log2(norm_counts[col] + pseudocount), bins=50, alpha=0.3, label=col)
        ax.set_title(method); ax.set_xlabel("log2(normalized count)")
        ax.legend(fontsize=6)
    plt.tight_layout()
    plt.savefig("normalization_comparison.png", dpi=150, bbox_inches="tight")
    plt.close()

    return results

# Usage
norm_methods = compare_normalizations(counts, ntc_guides=ntc_guide_list)
# Select best method:
# - Dropout screens with many depleted guides: control_based
# - Balanced screens: median_ratio (default)
# - Quick exploration: total_count
```

**Expected output**: Normalized count distributions per method. Median ratio is the default for most screens. Control-based is preferred when a large fraction of guides are depleted (as in strong dropout screens), because median ratio assumes most guides are unchanged.

---

## 10. Essential/Non-Essential Gene Benchmarking (Hart et al.)

Benchmark screen quality using curated reference gene sets.

```python
import pandas as pd
import numpy as np
from scipy.stats import gaussian_kde
from sklearn.metrics import roc_auc_score, precision_recall_curve, average_precision_score
import matplotlib.pyplot as plt

def benchmark_essentials(gene_results, lfc_col="neg|lfc",
                          essential_file=None, nonessential_file=None):
    """Benchmark screen against Hart et al. reference gene sets.

    Parameters
    ----------
    gene_results : pd.DataFrame
        MAGeCK gene_summary or equivalent with gene names and LFC.
    lfc_col : str
        Column with log fold change values.
    essential_file : str or None
        Path to essential gene list (one per line). Uses built-in if None.
    nonessential_file : str or None
        Path to non-essential gene list.

    Returns
    -------
    dict with NNMD, AUROC, AUPRC, and threshold metrics.
    """
    # Hart et al. 2015/2017 core essential genes (abbreviated)
    CORE_ESSENTIAL = [
        "RPL5", "RPL11", "RPL14", "RPL23A", "RPS6", "RPS14", "RPS19",
        "POLR2A", "POLR2B", "POLR2D", "SF3B1", "SF3B3", "SNRPD1",
        "PSMA1", "PSMA2", "PSMA3", "PSMB1", "PSMB2", "PSMD1",
        "EEF2", "EIF3A", "EIF3B", "EIF4A3",
        "PCNA", "RFC2", "RFC4", "MCM2", "MCM4", "MCM7",
        "CDC45", "CDK1", "CDK7", "CCNA2", "CCNB1",
        "RPA1", "RPA2", "NUP93", "NUP107", "NUP133",
        "COPS5", "COPS6", "UBA1", "UBE2I",
        # ... extend with full list from file
    ]

    NON_ESSENTIAL = [
        "ADRA1A", "ADRA1B", "ADRB1", "ADRB3",
        "CHRM1", "CHRM2", "CHRM4", "CHRM5",
        "DRD1", "DRD2", "DRD3", "DRD4", "DRD5",
        "GRM2", "GRM3", "GRM4", "GRM6", "GRM7", "GRM8",
        "HTR1A", "HTR1B", "HTR2A", "HTR2B", "HTR5A",
        "OPRD1", "OPRK1", "OPRM1",
        "OR1A1", "OR1A2", "OR2A4", "OR2B6", "OR2W1",
        "TAS1R1", "TAS1R2", "TAS1R3", "TAS2R1",
        # ... extend with full list from file
    ]

    if essential_file:
        CORE_ESSENTIAL = open(essential_file).read().strip().split("\n")
    if nonessential_file:
        NON_ESSENTIAL = open(nonessential_file).read().strip().split("\n")

    # Match to screen data
    gene_col = "id" if "id" in gene_results.columns else "Gene"
    ess_lfc = gene_results[gene_results[gene_col].isin(CORE_ESSENTIAL)][lfc_col].dropna()
    noness_lfc = gene_results[gene_results[gene_col].isin(NON_ESSENTIAL)][lfc_col].dropna()

    print(f"Essential genes found: {len(ess_lfc)}/{len(CORE_ESSENTIAL)}")
    print(f"Non-essential genes found: {len(noness_lfc)}/{len(NON_ESSENTIAL)}")

    if len(ess_lfc) < 10 or len(noness_lfc) < 10:
        print("WARNING: Insufficient reference genes for reliable benchmarking.")
        return None

    # NNMD (Null-Normalized Median Distance)
    nnmd = (noness_lfc.median() - ess_lfc.median()) / ess_lfc.mad()

    # AUROC
    labels = np.concatenate([np.ones(len(ess_lfc)), np.zeros(len(noness_lfc))])
    scores = np.concatenate([-ess_lfc.values, -noness_lfc.values])
    auroc = roc_auc_score(labels, scores)

    # AUPRC
    auprc = average_precision_score(labels, scores)

    metrics = {
        "nnmd": nnmd,
        "auroc": auroc,
        "auprc": auprc,
        "ess_median_lfc": ess_lfc.median(),
        "noness_median_lfc": noness_lfc.median(),
        "ess_mad": ess_lfc.mad(),
    }

    # Quality assessment
    print(f"\n{'='*50}")
    print(f"Screen Quality Benchmarks")
    print(f"{'='*50}")
    print(f"NNMD:  {nnmd:.2f}  {'GOOD' if nnmd > 2.5 else 'ACCEPTABLE' if nnmd > 1.5 else 'POOR'}")
    print(f"AUROC: {auroc:.3f} {'GOOD' if auroc > 0.90 else 'ACCEPTABLE' if auroc > 0.80 else 'POOR'}")
    print(f"AUPRC: {auprc:.3f} {'GOOD' if auprc > 0.85 else 'ACCEPTABLE' if auprc > 0.70 else 'POOR'}")
    print(f"Essential median LFC: {ess_lfc.median():.3f}")
    print(f"Non-essential median LFC: {noness_lfc.median():.3f}")

    # Plot
    fig, axes = plt.subplots(1, 3, figsize=(16, 4))

    # Distribution plot
    axes[0].hist(ess_lfc, bins=40, alpha=0.6, color="red", density=True, label="Essential")
    axes[0].hist(noness_lfc, bins=40, alpha=0.6, color="blue", density=True, label="Non-essential")
    axes[0].set_xlabel("Log2 Fold Change"); axes[0].legend()
    axes[0].set_title(f"NNMD = {nnmd:.2f}")

    # ROC curve
    from sklearn.metrics import roc_curve
    fpr, tpr, _ = roc_curve(labels, scores)
    axes[1].plot(fpr, tpr, color="darkblue")
    axes[1].plot([0, 1], [0, 1], "k--", lw=0.5)
    axes[1].set_xlabel("FPR"); axes[1].set_ylabel("TPR")
    axes[1].set_title(f"ROC (AUC = {auroc:.3f})")

    # PR curve
    prec, rec, _ = precision_recall_curve(labels, scores)
    axes[2].plot(rec, prec, color="darkgreen")
    axes[2].set_xlabel("Recall"); axes[2].set_ylabel("Precision")
    axes[2].set_title(f"PR (AP = {auprc:.3f})")

    plt.tight_layout()
    plt.savefig("screen_benchmarks.png", dpi=150, bbox_inches="tight")
    plt.close()

    return metrics

# Usage
gene_summary = pd.read_csv("mageck_test.gene_summary.txt", sep="\t")
metrics = benchmark_essentials(gene_summary, lfc_col="neg|lfc")
```

**Expected output**: NNMD > 2.5 and AUROC > 0.90 indicate a high-quality screen with clear separation between essential and non-essential genes. Poor scores may indicate insufficient coverage, batch effects, or library quality issues.

---

## 11. Positive vs Negative Selection Screen Design Considerations

Decision framework and analysis adjustments for different screen types.

```python
import pandas as pd
import numpy as np

def analyze_screen_by_type(gene_results, screen_type="dropout",
                            fdr_thresh=0.05, lfc_thresh=0.5):
    """Interpret screen results based on screen design type.

    Parameters
    ----------
    gene_results : pd.DataFrame
        MAGeCK gene_summary output.
    screen_type : str
        'dropout' (negative selection), 'enrichment' (positive selection),
        'bidirectional' (both directions informative).
    fdr_thresh : float
        FDR cutoff for hit calling.
    lfc_thresh : float
        Minimum absolute LFC for hit calling.

    Returns
    -------
    pd.DataFrame of hits with interpretation.
    """
    configs = {
        "dropout": {
            "primary_direction": "negative",
            "score_col": "neg|score",
            "fdr_col": "neg|fdr",
            "lfc_col": "neg|lfc",
            "lfc_sign": -1,
            "interpretation": "Gene required for fitness; knockout impairs growth",
        },
        "enrichment": {
            "primary_direction": "positive",
            "score_col": "pos|score",
            "fdr_col": "pos|fdr",
            "lfc_col": "pos|lfc" if "pos|lfc" in gene_results.columns else "neg|lfc",
            "lfc_sign": 1,
            "interpretation": "Gene confers resistance; knockout enriched under selection",
        },
        "bidirectional": {
            "primary_direction": "both",
            "interpretation": "Both depleted and enriched genes are informative",
        },
    }

    cfg = configs[screen_type]
    print(f"Screen type: {screen_type}")
    print(f"Primary direction: {cfg['primary_direction']}")
    print(f"Biological interpretation: {cfg['interpretation']}")

    if screen_type == "bidirectional":
        # Call hits in both directions
        neg_hits = gene_results[
            (gene_results["neg|fdr"] < fdr_thresh) &
            (gene_results["neg|lfc"] < -lfc_thresh)
        ].copy()
        neg_hits["direction"] = "depleted"
        neg_hits["interpretation"] = "Essential/fitness gene"

        pos_hits = gene_results[
            (gene_results["pos|fdr"] < fdr_thresh) &
            (gene_results["neg|lfc"] > lfc_thresh)
        ].copy()
        pos_hits["direction"] = "enriched"
        pos_hits["interpretation"] = "Growth suppressor / resistance gene"

        all_hits = pd.concat([neg_hits, pos_hits])
        print(f"\nDepleted hits: {len(neg_hits)}")
        print(f"Enriched hits: {len(pos_hits)}")
    else:
        fdr_col = cfg["fdr_col"]
        lfc_col = cfg["lfc_col"]
        sign = cfg["lfc_sign"]

        all_hits = gene_results[
            (gene_results[fdr_col] < fdr_thresh) &
            (gene_results[lfc_col] * sign > lfc_thresh * sign)
        ].copy()
        all_hits["direction"] = cfg["primary_direction"]
        all_hits["interpretation"] = cfg["interpretation"]
        print(f"\nHits: {len(all_hits)}")

    return all_hits.sort_values(cfg.get("fdr_col", "neg|fdr"))

# Usage
# Dropout screen (essentiality)
dropout_hits = analyze_screen_by_type(gene_summary, screen_type="dropout")

# Drug resistance screen
resistance_hits = analyze_screen_by_type(gene_summary, screen_type="enrichment")

# Bidirectional analysis
all_hits = analyze_screen_by_type(gene_summary, screen_type="bidirectional")
```

**Expected output**: Hit list with biological interpretation based on screen design. Dropout screens identify essential genes; enrichment screens identify resistance genes. Always specify the screen type before interpreting LFC direction.

---

## 12. Base Editing Screen Analysis: BE-Hive Quantification

Analysis workflow for base editing screens using CRISPResso2 and custom variant calling.

```python
import pandas as pd
import numpy as np
import os

def analyze_base_editing_screen(crispresso_dir, guides_df, target_base="C",
                                 edit_base="T", window_start=-5, window_end=5):
    """Quantify base editing outcomes from CRISPResso2 output.

    Parameters
    ----------
    crispresso_dir : str
        Directory containing CRISPResso2 batch output.
    guides_df : pd.DataFrame
        Guide annotations with columns: guide_name, gene, target_position,
        expected_amino_acid_change.
    target_base : str
        Base being edited (C for CBE, A for ABE).
    edit_base : str
        Expected edited base (T for CBE, G for ABE).
    window_start, window_end : int
        Editing window relative to cut site (typically -5 to +5 for CBEs).

    Returns
    -------
    pd.DataFrame with per-guide editing efficiency and variant frequencies.
    """
    results = []

    for _, guide in guides_df.iterrows():
        guide_dir = os.path.join(crispresso_dir, f"CRISPResso_on_{guide['guide_name']}")
        if not os.path.isdir(guide_dir):
            continue

        # Load allele frequency table
        allele_file = None
        for f in os.listdir(guide_dir):
            if f.startswith("Alleles_frequency_table") and f.endswith(".zip"):
                allele_file = os.path.join(guide_dir, f)
                break

        if allele_file is None:
            continue

        alleles = pd.read_csv(allele_file, sep="\t", compression="zip")
        total_reads = alleles["#Reads"].sum()

        # Count target base conversions in editing window
        n_edited = 0
        n_bystander = 0
        n_indel = 0
        n_unmodified = 0

        for _, allele in alleles.iterrows():
            aligned = allele.get("Aligned_Sequence", "")
            ref = allele.get("Reference_Sequence", "")
            reads = allele["#Reads"]

            if pd.isna(aligned) or pd.isna(ref):
                continue

            # Check for indels
            if "-" in aligned or "-" in ref:
                n_indel += reads
                continue

            # Count base edits in window
            has_target_edit = False
            has_bystander = False
            for pos in range(max(0, len(ref) // 2 + window_start),
                           min(len(ref), len(ref) // 2 + window_end)):
                if pos < len(ref) and pos < len(aligned):
                    if ref[pos] == target_base and aligned[pos] == edit_base:
                        has_target_edit = True
                    elif ref[pos] != aligned[pos] and ref[pos] != "-" and aligned[pos] != "-":
                        has_bystander = True

            if has_target_edit:
                n_edited += reads
            elif has_bystander:
                n_bystander += reads
            else:
                n_unmodified += reads

        results.append({
            "guide_name": guide["guide_name"],
            "gene": guide["gene"],
            "total_reads": total_reads,
            "editing_efficiency": n_edited / total_reads * 100 if total_reads > 0 else 0,
            "indel_rate": n_indel / total_reads * 100 if total_reads > 0 else 0,
            "bystander_rate": n_bystander / total_reads * 100 if total_reads > 0 else 0,
            "unmodified_rate": n_unmodified / total_reads * 100 if total_reads > 0 else 0,
            "target_aa_change": guide.get("expected_amino_acid_change", "N/A"),
        })

    results_df = pd.DataFrame(results)

    # Gene-level aggregation
    gene_summary = results_df.groupby("gene").agg(
        n_guides=("guide_name", "count"),
        mean_editing=("editing_efficiency", "mean"),
        max_editing=("editing_efficiency", "max"),
        mean_indel=("indel_rate", "mean"),
    ).sort_values("mean_editing", ascending=False)

    print(f"Base editing screen results:")
    print(f"  Guides analyzed: {len(results_df)}")
    print(f"  Genes targeted: {len(gene_summary)}")
    print(f"  Mean editing efficiency: {results_df['editing_efficiency'].mean():.1f}%")
    print(f"  Mean indel rate: {results_df['indel_rate'].mean():.1f}%")
    print(f"\nTop genes by editing efficiency:")
    print(gene_summary.head(20).to_string())

    return results_df, gene_summary

# Usage
guides = pd.read_csv("base_editing_library.csv")
edit_results, gene_edit = analyze_base_editing_screen(
    "crispresso_batch_output/", guides,
    target_base="C", edit_base="T",
    window_start=-5, window_end=5
)
```

**Key parameters**: CBE (cytosine base editors) convert C>T in a window ~4-8 nt from the PAM. ABE (adenine base editors) convert A>G. The `window_start`/`window_end` should match your editor's activity window. Bystander edits (unintended base changes in the window) should be tracked as they may confound functional interpretation.
