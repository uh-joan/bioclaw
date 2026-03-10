# GSEA & Pathway Enrichment Recipes

Code templates for Gene Set Enrichment Analysis (GSEA), over-representation analysis (ORA), and pathway visualization using R (clusterProfiler, fgsea) and Python (GSEApy).

Cross-skill routing: use `single-cell-analysis` for marker gene identification upstream, `systems-biology` for network-level pathway integration.

---

## 1. clusterProfiler gseGO / gseKEGG with Ranked Gene List (R)

GSEA against Gene Ontology and KEGG using a pre-ranked gene list.

```R
library(clusterProfiler)
library(org.Hs.eg.db)
library(enrichplot)

# ---- Prepare ranked gene list ----
# Input: data.frame with columns 'gene_symbol' and 'log2FoldChange' (or stat)
de_results <- read.csv("de_results.csv")

# Create named vector: ranking metric = -log10(pvalue) * sign(log2FC)
# Alternative: just use log2FC or stat from DESeq2
de_results$rank_metric <- -log10(de_results$pvalue + 1e-300) * sign(de_results$log2FoldChange)

# Map symbols to Entrez IDs (required by clusterProfiler)
gene_map <- bitr(de_results$gene_symbol, fromType = "SYMBOL",
                 toType = "ENTREZID", OrgDb = org.Hs.eg.db)
de_ranked <- merge(de_results, gene_map, by.x = "gene_symbol", by.y = "SYMBOL")

# Named vector, sorted descending
gene_list <- de_ranked$rank_metric
names(gene_list) <- de_ranked$ENTREZID
gene_list <- sort(gene_list, decreasing = TRUE)
gene_list <- gene_list[!duplicated(names(gene_list))]
cat("Ranked genes:", length(gene_list), "\n")

# ---- GSEA: Gene Ontology (Biological Process) ----
gsea_go <- gseGO(
    geneList     = gene_list,
    OrgDb        = org.Hs.eg.db,
    ont          = "BP",         # "BP", "MF", "CC", or "ALL"
    minGSSize    = 15,           # min genes in gene set
    maxGSSize    = 500,          # max genes in gene set
    pvalueCutoff = 0.25,         # FDR threshold (GSEA standard)
    eps          = 1e-10,        # boundary for p-value estimation
    pAdjustMethod = "BH",
    verbose      = TRUE
)
cat("Significant GO terms (FDR < 0.25):", nrow(gsea_go@result[gsea_go@result$p.adjust < 0.25, ]), "\n")

# ---- GSEA: KEGG ----
gsea_kegg <- gseKEGG(
    geneList     = gene_list,
    organism     = "hsa",        # "hsa" for human, "mmu" for mouse
    minGSSize    = 15,
    maxGSSize    = 500,
    pvalueCutoff = 0.25,
    pAdjustMethod = "BH",
    verbose      = TRUE
)
cat("Significant KEGG pathways:", nrow(gsea_kegg@result[gsea_kegg@result$p.adjust < 0.25, ]), "\n")

# ---- Results table ----
go_results <- as.data.frame(gsea_go)
kegg_results <- as.data.frame(gsea_kegg)
write.csv(go_results, "gsea_go_results.csv", row.names = FALSE)
write.csv(kegg_results, "gsea_kegg_results.csv", row.names = FALSE)

cat("\nTop 10 GO BP by NES:\n")
print(head(go_results[order(-abs(go_results$NES)), c("Description", "NES", "p.adjust", "setSize")], 10))
```

**Key parameters**: `minGSSize`/`maxGSSize` filter gene sets by size (too small = noisy, too large = nonspecific). `pvalueCutoff=0.25` is the standard GSEA threshold. NES > 0 means enriched in top of ranked list (upregulated); NES < 0 means enriched in bottom (downregulated).

---

## 2. fgsea with MSigDB Hallmark Gene Sets (R)

Fast GSEA implementation with preranked gene lists and MSigDB collections.

```R
library(fgsea)
library(msigdbr)

# ---- Load MSigDB hallmark gene sets ----
hallmark <- msigdbr(species = "Homo sapiens", category = "H")
hallmark_list <- split(hallmark$entrez_gene, hallmark$gs_name)
# Convert to character for fgsea
hallmark_list <- lapply(hallmark_list, as.character)
cat("Hallmark gene sets:", length(hallmark_list), "\n")

# ---- Prepare ranked list (Entrez IDs) ----
# gene_list: named numeric vector, names = Entrez IDs, values = ranking metric
# (reuse from Recipe 1 or create fresh)
stats <- gene_list  # from Recipe 1

# ---- Run fgsea ----
set.seed(42)
fgsea_res <- fgsea(
    pathways = hallmark_list,
    stats    = stats,
    minSize  = 15,
    maxSize  = 500,
    nperm    = 10000      # deprecated in newer fgsea; use fgseaMultilevel instead
)

# Modern alternative (adaptive, more accurate p-values):
fgsea_res <- fgseaMultilevel(
    pathways = hallmark_list,
    stats    = stats,
    minSize  = 15,
    maxSize  = 500,
    eps      = 0           # 0 = compute exact p-values
)

# Sort by adjusted p-value
fgsea_res <- fgsea_res[order(fgsea_res$padj), ]
cat("Significant hallmarks (padj < 0.25):", sum(fgsea_res$padj < 0.25, na.rm = TRUE), "\n")

# ---- Results ----
print(head(fgsea_res[, c("pathway", "NES", "padj", "size")], 15))

# ---- Table plot ----
topUp <- fgsea_res[NES > 0][head(order(padj), n = 10)]
topDown <- fgsea_res[NES < 0][head(order(padj), n = 10)]
topPathways <- c(topUp$pathway, rev(topDown$pathway))
plotGseaTable(hallmark_list[topPathways], stats, fgsea_res, gseaParam = 0.5)

# ---- Enrichment plot for a specific pathway ----
plotEnrichment(hallmark_list[["HALLMARK_P53_PATHWAY"]], stats) +
    ggplot2::labs(title = "HALLMARK_P53_PATHWAY")
ggplot2::ggsave("gsea_p53_enrichment.png", width = 8, height = 4)

# Save results
write.csv(as.data.frame(fgsea_res), "fgsea_hallmark_results.csv", row.names = FALSE)
```

**Expected output**: NES (Normalized Enrichment Score) and adjusted p-values for each hallmark gene set. Positive NES = enriched among upregulated genes; negative NES = enriched among downregulated genes.

---

## 3. GSEApy Prerank with Custom Gene Sets (Python)

Python-native GSEA using preranked gene list and any gene set collection.

```python
import gseapy as gp
import pandas as pd
import numpy as np

def run_gseapy_prerank(ranked_genes, gene_sets="KEGG_2021_Human",
                        outdir="gsea_results", min_size=15, max_size=500,
                        permutation_num=1000, seed=42):
    """Run GSEApy prerank analysis.

    Parameters
    ----------
    ranked_genes : pd.DataFrame or str
        DataFrame with columns ['gene', 'rank_metric'] or path to .rnk file.
        rank_metric: -log10(pvalue) * sign(log2FC) or just log2FC.
    gene_sets : str or dict
        Enrichr library name (e.g., 'KEGG_2021_Human', 'GO_Biological_Process_2021',
        'MSigDB_Hallmark_2020', 'Reactome_2022') or dict of {name: [gene_list]}.
    outdir : str
        Output directory for results and plots.
    min_size, max_size : int
        Gene set size filters.
    permutation_num : int
        Number of permutations. 1000 for exploratory, 10000 for publication.

    Returns
    -------
    GSEApy PreRes object with res2d attribute containing results.
    """
    if isinstance(ranked_genes, pd.DataFrame):
        rnk = ranked_genes.set_index("gene")["rank_metric"].sort_values(ascending=False)
        rnk = rnk[~rnk.index.duplicated(keep="first")]
    else:
        rnk = ranked_genes

    pre_res = gp.prerank(
        rnk=rnk,
        gene_sets=gene_sets,
        outdir=outdir,
        min_size=min_size,
        max_size=max_size,
        permutation_num=permutation_num,
        seed=seed,
        verbose=True,
    )

    results = pre_res.res2d.sort_values("FDR q-val")
    sig = results[results["FDR q-val"] < 0.25]
    print(f"Gene sets tested: {len(results)}")
    print(f"Significant (FDR < 0.25): {len(sig)}")
    print(f"  Activated (NES > 0): {(sig['NES'].astype(float) > 0).sum()}")
    print(f"  Suppressed (NES < 0): {(sig['NES'].astype(float) < 0).sum()}")
    print(f"\nTop 10:")
    print(sig.head(10)[["Term", "NES", "FDR q-val"]])

    return pre_res

# ---- Prepare ranked list from DESeq2/limma output ----
de = pd.read_csv("de_results.csv")
de["rank_metric"] = -np.log10(de["pvalue"].clip(lower=1e-300)) * np.sign(de["log2FoldChange"])
ranked = de[["gene_symbol", "rank_metric"]].rename(columns={"gene_symbol": "gene"})
ranked = ranked.dropna().sort_values("rank_metric", ascending=False)

# Run against multiple libraries
for lib in ["MSigDB_Hallmark_2020", "KEGG_2021_Human", "GO_Biological_Process_2021"]:
    print(f"\n{'='*60}\n{lib}\n{'='*60}")
    res = run_gseapy_prerank(ranked, gene_sets=lib, outdir=f"gsea_{lib}")

# ---- With custom gene sets ----
custom_sets = {
    "MY_SIGNATURE_A": ["TP53", "MDM2", "CDKN1A", "BAX", "BBC3", "PUMA"],
    "MY_SIGNATURE_B": ["MYC", "CCND1", "CDK4", "RB1", "E2F1"],
}
res_custom = run_gseapy_prerank(ranked, gene_sets=custom_sets, outdir="gsea_custom")
```

**Key parameters**: `permutation_num` controls p-value precision. Use gene symbols (not Entrez) for Enrichr-style libraries. Custom gene sets passed as dict allow testing any hypothesis.

---

## 4. ORA with enrichGO / enrichKEGG (R)

Over-Representation Analysis on a thresholded gene list.

```R
library(clusterProfiler)
library(org.Hs.eg.db)

# ---- Input: significant gene list ----
sig_genes <- c("TP53", "BRCA1", "BRCA2", "ATM", "CHEK2", "MDM2",
               "CDKN1A", "BAX", "BCL2", "CASP3", "CASP9", "CYCS")

# Map to Entrez IDs
gene_ids <- bitr(sig_genes, fromType = "SYMBOL", toType = "ENTREZID",
                 OrgDb = org.Hs.eg.db)
cat("Mapped:", nrow(gene_ids), "/", length(sig_genes), "genes\n")

# ---- Optional: define background universe ----
# Use all detected genes (not just DE genes) as background
all_genes <- read.csv("all_expressed_genes.csv")$gene_symbol
bg_ids <- bitr(all_genes, fromType = "SYMBOL", toType = "ENTREZID",
               OrgDb = org.Hs.eg.db)

# ---- enrichGO: Gene Ontology ----
ora_go <- enrichGO(
    gene         = gene_ids$ENTREZID,
    universe     = bg_ids$ENTREZID,    # omit for genome-wide background
    OrgDb        = org.Hs.eg.db,
    ont          = "BP",               # "BP", "MF", "CC", or "ALL"
    pAdjustMethod = "BH",
    pvalueCutoff = 0.05,
    qvalueCutoff = 0.05,
    readable     = TRUE,               # convert Entrez back to symbols
    minGSSize    = 10,
    maxGSSize    = 500
)

cat("Significant GO BP terms:", nrow(ora_go@result[ora_go@result$p.adjust < 0.05, ]), "\n")

# ---- enrichKEGG: KEGG pathways ----
ora_kegg <- enrichKEGG(
    gene         = gene_ids$ENTREZID,
    universe     = bg_ids$ENTREZID,
    organism     = "hsa",
    pAdjustMethod = "BH",
    pvalueCutoff = 0.05,
    qvalueCutoff = 0.05,
    minGSSize    = 10,
    maxGSSize    = 500
)

cat("Significant KEGG pathways:", nrow(ora_kegg@result[ora_kegg@result$p.adjust < 0.05, ]), "\n")

# ---- Results ----
go_df <- as.data.frame(ora_go)
kegg_df <- as.data.frame(ora_kegg)
print(head(go_df[, c("Description", "GeneRatio", "BgRatio", "p.adjust", "geneID")], 10))
print(head(kegg_df[, c("Description", "GeneRatio", "BgRatio", "p.adjust", "geneID")], 10))

write.csv(go_df, "ora_go_results.csv", row.names = FALSE)
write.csv(kegg_df, "ora_kegg_results.csv", row.names = FALSE)
```

**Key parameters**: Always provide a `universe` (background gene set) matching your experimental context (e.g., all detected genes in your RNA-seq). Without it, the test uses the full genome, which inflates significance for tissue-specific genes.

---

## 5. MSigDB Collection Loading (R)

Load specific MSigDB collections for targeted enrichment.

```R
library(msigdbr)

# ---- Available collections ----
# H: Hallmark (50 gene sets, well-defined biological states)
# C1: Positional (by chromosome)
# C2: Curated (CP:KEGG, CP:REACTOME, CP:WIKIPATHWAYS, CP:BIOCARTA)
# C3: Regulatory (TFT:GTRD, MIR:MIRDB, MIR:MIR_Legacy)
# C4: Computational (CGN, CM)
# C5: Ontology (GO:BP, GO:MF, GO:CC, HPO)
# C6: Oncogenic signatures
# C7: Immunologic signatures (IMMUNESIGDB, VAX)
# C8: Cell type signatures

# ---- Load specific collections ----
# Hallmark
hallmark <- msigdbr(species = "Homo sapiens", category = "H")
hallmark_list <- split(hallmark$gene_symbol, hallmark$gs_name)
cat("Hallmark sets:", length(hallmark_list), "\n")

# Curated pathways (KEGG + Reactome + WikiPathways)
curated <- msigdbr(species = "Homo sapiens", category = "C2",
                   subcategory = "CP")
curated_list <- split(curated$gene_symbol, curated$gs_name)
cat("Curated pathway sets:", length(curated_list), "\n")

# GO Biological Process
go_bp <- msigdbr(species = "Homo sapiens", category = "C5",
                 subcategory = "GO:BP")
go_bp_list <- split(go_bp$gene_symbol, go_bp$gs_name)
cat("GO BP sets:", length(go_bp_list), "\n")

# Immunologic signatures
immuno <- msigdbr(species = "Homo sapiens", category = "C7",
                  subcategory = "IMMUNESIGDB")
immuno_list <- split(immuno$gene_symbol, immuno$gs_name)
cat("IMMUNESIGDB sets:", length(immuno_list), "\n")

# ---- Use with fgsea ----
# Convert to Entrez for fgsea
hallmark_entrez <- msigdbr(species = "Homo sapiens", category = "H")
hallmark_entrez_list <- split(as.character(hallmark_entrez$entrez_gene),
                               hallmark_entrez$gs_name)

# ---- Use with clusterProfiler GSEA ----
# Create term2gene data frame (required format)
t2g_hallmark <- hallmark[, c("gs_name", "entrez_gene")]
colnames(t2g_hallmark) <- c("term", "gene")

gsea_custom <- GSEA(
    geneList = gene_list,  # named ranked vector
    TERM2GENE = t2g_hallmark,
    minGSSize = 15,
    maxGSSize = 500,
    pvalueCutoff = 0.25
)

# ---- Mouse gene sets (with ortholog mapping) ----
mouse_hallmark <- msigdbr(species = "Mus musculus", category = "H")
mouse_list <- split(mouse_hallmark$gene_symbol, mouse_hallmark$gs_name)
cat("Mouse hallmark sets:", length(mouse_list), "\n")
```

**Expected output**: Named lists of gene sets ready for fgsea or clusterProfiler. Key collections: H (hallmark) for well-defined biology, C2:CP for curated pathways, C5:GO for gene ontology, C7:IMMUNESIGDB for immune signatures.

---

## 6. Core Enrichment Gene Extraction and Visualization

Extract the genes driving each enriched term (leading edge) and visualize overlaps.

```R
library(clusterProfiler)
library(enrichplot)
library(ggplot2)

# Assumes gsea_go from Recipe 1

# ---- Extract core enrichment (leading edge) genes ----
extract_leading_edge <- function(gsea_result, top_n = 20) {
    res <- as.data.frame(gsea_result)
    res <- res[order(res$p.adjust), ]
    res <- head(res, top_n)

    leading_edge_list <- list()
    for (i in seq_len(nrow(res))) {
        genes <- unlist(strsplit(res$core_enrichment[i], "/"))
        leading_edge_list[[res$Description[i]]] <- genes
    }

    # Summary
    cat("Leading edge genes per term:\n")
    for (name in names(leading_edge_list)) {
        cat(sprintf("  %s: %d genes\n", name, length(leading_edge_list[[name]])))
    }

    # Find recurrent genes across terms
    all_genes <- unlist(leading_edge_list)
    gene_freq <- sort(table(all_genes), decreasing = TRUE)
    cat("\nMost recurrent leading edge genes:\n")
    print(head(gene_freq, 20))

    return(list(by_term = leading_edge_list, frequency = gene_freq))
}

le <- extract_leading_edge(gsea_go, top_n = 15)

# ---- Overlap heatmap ----
# Which gene sets share leading edge genes?
terms <- names(le$by_term)
overlap_mat <- matrix(0, nrow = length(terms), ncol = length(terms),
                      dimnames = list(terms, terms))
for (i in seq_along(terms)) {
    for (j in seq_along(terms)) {
        overlap_mat[i, j] <- length(intersect(le$by_term[[i]], le$by_term[[j]]))
    }
}
# Jaccard index
jaccard_mat <- overlap_mat
for (i in seq_along(terms)) {
    for (j in seq_along(terms)) {
        union_size <- length(union(le$by_term[[i]], le$by_term[[j]]))
        jaccard_mat[i, j] <- if (union_size > 0) overlap_mat[i, j] / union_size else 0
    }
}

pheatmap::pheatmap(jaccard_mat, display_numbers = TRUE, number_format = "%.2f",
                    fontsize_row = 7, fontsize_col = 7,
                    filename = "leading_edge_overlap.png", width = 10, height = 8)
```

**Expected output**: A list of leading edge genes per enriched term, frequency counts showing which genes appear in multiple terms (hub genes), and a Jaccard similarity heatmap revealing redundant gene sets.

---

## 7. enrichPlot Visualization: dotplot, ridgeplot, cnetplot, emapplot (R)

Publication-ready enrichment visualizations.

```R
library(enrichplot)
library(ggplot2)

# Assumes gsea_go and ora_go from Recipes 1 and 4

# ---- Dotplot: gene ratio vs adjusted p-value ----
dotplot(gsea_go, showCategory = 20, title = "GSEA GO:BP",
        x = "GeneRatio", color = "p.adjust", size = "Count") +
    theme(axis.text.y = element_text(size = 8))
ggsave("gsea_dotplot.png", width = 10, height = 8)

# For ORA results
dotplot(ora_go, showCategory = 15, title = "ORA GO:BP") +
    theme(axis.text.y = element_text(size = 9))
ggsave("ora_dotplot.png", width = 10, height = 7)

# ---- Ridgeplot: NES distribution by gene set ----
ridgeplot(gsea_go, showCategory = 15) +
    labs(x = "Enrichment Distribution") +
    theme(axis.text.y = element_text(size = 8))
ggsave("gsea_ridgeplot.png", width = 10, height = 8)

# ---- Cnetplot: gene-concept network ----
# Shows which genes contribute to each enriched term
cnetplot(ora_go, showCategory = 5, categorySize = "pvalue",
         foldChange = gene_list, colorEdge = TRUE) +
    theme(legend.position = "right")
ggsave("ora_cnetplot.png", width = 12, height = 10)

# ---- Emapplot: enrichment map (term similarity network) ----
# Terms connected by shared genes form clusters of related biology
ora_go_pw <- pairwise_termsim(ora_go)
emapplot(ora_go_pw, showCategory = 30) +
    theme(legend.position = "right")
ggsave("ora_emapplot.png", width = 12, height = 10)

# ---- Treeplot: hierarchical clustering of terms ----
treeplot(ora_go_pw, showCategory = 30) +
    theme(axis.text.y = element_text(size = 7))
ggsave("ora_treeplot.png", width = 14, height = 10)

# ---- Heatplot: gene membership across terms ----
heatplot(ora_go, showCategory = 10, foldChange = gene_list) +
    theme(axis.text.x = element_text(angle = 45, hjust = 1, size = 7))
ggsave("ora_heatplot.png", width = 14, height = 6)

# ---- GSEA enrichment plot for a single pathway ----
gseaplot2(gsea_go, geneSetID = 1:3, pvalue_table = TRUE,
          title = "Top 3 Enriched GO Terms")
ggsave("gsea_running_score.png", width = 10, height = 6)
```

**Expected output**: Publication-quality figures. Dotplot for ranked term overview; ridgeplot for NES distributions; cnetplot for gene-term connections; emapplot for term similarity clusters.

---

## 8. GSEA Leading Edge Analysis

Deep analysis of the genes driving enrichment signals.

```python
import gseapy as gp
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def leading_edge_analysis(gsea_result, fdr_cutoff=0.25, top_n=20):
    """Analyze leading edge genes from GSEApy prerank results.

    Parameters
    ----------
    gsea_result : gseapy PreRes object
        Result from gp.prerank().
    fdr_cutoff : float
        FDR threshold for selecting significant gene sets.
    top_n : int
        Maximum number of gene sets to analyze.

    Returns
    -------
    dict with 'by_term' (leading edge per term), 'frequency' (gene recurrence),
    'overlap_matrix' (Jaccard similarity between terms).
    """
    res = gsea_result.res2d.copy()
    res["FDR q-val"] = res["FDR q-val"].astype(float)
    sig = res[res["FDR q-val"] < fdr_cutoff].sort_values("FDR q-val").head(top_n)

    if len(sig) == 0:
        print("No significant gene sets found.")
        return None

    # Extract leading edge genes
    le_genes = {}
    for _, row in sig.iterrows():
        term = row["Term"]
        genes = str(row["Lead_genes"]).split(";")
        le_genes[term] = [g.strip() for g in genes if g.strip()]

    # Gene frequency across terms
    all_genes = [g for genes in le_genes.values() for g in genes]
    freq = pd.Series(all_genes).value_counts()
    print(f"Leading edge analysis for {len(le_genes)} gene sets:")
    print(f"  Total unique genes: {len(freq)}")
    print(f"  Genes in 3+ terms: {(freq >= 3).sum()}")
    print(f"\n  Top recurrent genes:")
    print(freq.head(15).to_string())

    # Jaccard similarity matrix
    terms = list(le_genes.keys())
    n = len(terms)
    jaccard = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            s1, s2 = set(le_genes[terms[i]]), set(le_genes[terms[j]])
            union = len(s1 | s2)
            jaccard[i, j] = len(s1 & s2) / union if union > 0 else 0

    # Plot overlap
    fig, ax = plt.subplots(figsize=(max(8, n * 0.5), max(6, n * 0.4)))
    short_terms = [t[:50] + "..." if len(t) > 50 else t for t in terms]
    sns.heatmap(jaccard, xticklabels=short_terms, yticklabels=short_terms,
                cmap="YlOrRd", annot=True, fmt=".2f", ax=ax,
                xticklabels_rotation=45, yticklabels_rotation=0)
    ax.set_title("Leading Edge Gene Overlap (Jaccard Similarity)")
    plt.tight_layout()
    plt.savefig("leading_edge_overlap.png", dpi=150, bbox_inches="tight")
    plt.close()

    return {"by_term": le_genes, "frequency": freq, "jaccard": jaccard}

# Usage
pre_res = gp.prerank(rnk=ranked, gene_sets="MSigDB_Hallmark_2020",
                      outdir="gsea_hallmark", min_size=15, max_size=500)
le = leading_edge_analysis(pre_res, fdr_cutoff=0.25)
```

**Expected output**: A table of frequently recurring leading edge genes (these are the core drivers of enrichment) and a heatmap showing which enriched terms share genes (high Jaccard = redundant terms driven by same biology).

---

## 9. Custom Gene Set Creation from Expression Signatures

Build custom gene sets from your own experimental data.

```python
import pandas as pd
import numpy as np
import json

def create_custom_genesets(de_results, log2fc_col="log2FoldChange",
                            padj_col="padj", gene_col="gene_symbol",
                            fc_thresh=1.0, padj_thresh=0.05,
                            set_name_prefix="CUSTOM"):
    """Create gene sets from differential expression results.

    Parameters
    ----------
    de_results : pd.DataFrame
        DE results with gene symbols, log2FC, and adjusted p-values.
    fc_thresh : float
        Absolute log2FC threshold for gene set membership.
    padj_thresh : float
        Adjusted p-value threshold.
    set_name_prefix : str
        Prefix for gene set names.

    Returns
    -------
    dict of {gene_set_name: [gene_list]} suitable for GSEApy or fgsea.
    """
    de = de_results.dropna(subset=[log2fc_col, padj_col])
    sig = de[de[padj_col] < padj_thresh]

    gene_sets = {}

    # Upregulated genes at various thresholds
    for fc in [0.5, 1.0, 1.5, 2.0]:
        up = sig[sig[log2fc_col] > fc][gene_col].tolist()
        if len(up) >= 5:
            gene_sets[f"{set_name_prefix}_UP_FC{fc}"] = up

    # Downregulated genes
    for fc in [0.5, 1.0, 1.5, 2.0]:
        down = sig[sig[log2fc_col] < -fc][gene_col].tolist()
        if len(down) >= 5:
            gene_sets[f"{set_name_prefix}_DOWN_FC{fc}"] = down

    # Top N genes by significance
    for n in [50, 100, 200]:
        top = de.nsmallest(n, padj_col)
        top_up = top[top[log2fc_col] > 0][gene_col].tolist()
        top_down = top[top[log2fc_col] < 0][gene_col].tolist()
        if len(top_up) >= 5:
            gene_sets[f"{set_name_prefix}_TOP{n}_UP"] = top_up
        if len(top_down) >= 5:
            gene_sets[f"{set_name_prefix}_TOP{n}_DOWN"] = top_down

    # Summary
    print(f"Created {len(gene_sets)} gene sets:")
    for name, genes in gene_sets.items():
        print(f"  {name}: {len(genes)} genes")

    # Save as GMT format (for command-line GSEA)
    with open(f"{set_name_prefix}_custom.gmt", "w") as f:
        for name, genes in gene_sets.items():
            f.write(f"{name}\tna\t" + "\t".join(genes) + "\n")

    # Save as JSON (for GSEApy)
    with open(f"{set_name_prefix}_custom.json", "w") as f:
        json.dump(gene_sets, f, indent=2)

    return gene_sets

# Usage
de = pd.read_csv("de_results.csv")
custom_sets = create_custom_genesets(de, set_name_prefix="TREATMENT_vs_CTRL")

# Use custom gene sets in GSEApy
import gseapy as gp
res = gp.prerank(rnk=ranked, gene_sets=custom_sets, outdir="gsea_custom")
```

**Expected output**: GMT and JSON files with custom gene sets at various stringency levels, ready for cross-study GSEA validation.

---

## 10. Multi-Condition GSEA Comparison

Compare enrichment patterns across multiple conditions or contrasts.

```python
import gseapy as gp
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def multi_condition_gsea(ranked_dict, gene_sets="MSigDB_Hallmark_2020",
                          outdir="gsea_multi", fdr_cutoff=0.25):
    """Run GSEA across multiple conditions and build a NES comparison matrix.

    Parameters
    ----------
    ranked_dict : dict
        {condition_name: pd.Series or pd.DataFrame with 'gene' and 'rank_metric'}.
    gene_sets : str or dict
        Gene set library name or custom dict.
    fdr_cutoff : float
        FDR threshold for marking significance.

    Returns
    -------
    pd.DataFrame with NES values (conditions x gene sets), significance markers.
    """
    all_results = {}

    for condition, ranked in ranked_dict.items():
        print(f"\nRunning GSEA for: {condition}")
        if isinstance(ranked, pd.DataFrame):
            rnk = ranked.set_index("gene")["rank_metric"].sort_values(ascending=False)
            rnk = rnk[~rnk.index.duplicated(keep="first")]
        else:
            rnk = ranked

        res = gp.prerank(
            rnk=rnk, gene_sets=gene_sets,
            outdir=f"{outdir}/{condition}",
            min_size=15, max_size=500,
            permutation_num=1000, verbose=False,
        )
        all_results[condition] = res.res2d

    # Build NES matrix
    conditions = list(all_results.keys())
    all_terms = set()
    for res in all_results.values():
        all_terms.update(res["Term"].tolist())
    all_terms = sorted(all_terms)

    nes_matrix = pd.DataFrame(index=all_terms, columns=conditions, dtype=float)
    sig_matrix = pd.DataFrame(index=all_terms, columns=conditions, dtype=str)

    for cond, res in all_results.items():
        res_indexed = res.set_index("Term")
        for term in all_terms:
            if term in res_indexed.index:
                nes_matrix.loc[term, cond] = float(res_indexed.loc[term, "NES"])
                fdr = float(res_indexed.loc[term, "FDR q-val"])
                sig_matrix.loc[term, cond] = "***" if fdr < 0.001 else "**" if fdr < 0.01 else "*" if fdr < fdr_cutoff else ""
            else:
                nes_matrix.loc[term, cond] = 0
                sig_matrix.loc[term, cond] = ""

    # Filter to terms significant in at least one condition
    has_sig = sig_matrix.apply(lambda row: any(row != ""), axis=1)
    nes_filtered = nes_matrix.loc[has_sig].astype(float)
    sig_filtered = sig_matrix.loc[has_sig]

    # Heatmap
    fig, ax = plt.subplots(figsize=(max(8, len(conditions) * 1.5), max(6, len(nes_filtered) * 0.3)))
    sns.heatmap(nes_filtered.astype(float), cmap="RdBu_r", center=0, annot=sig_filtered,
                fmt="s", ax=ax, xticklabels=True, yticklabels=True,
                linewidths=0.5, linecolor="gray")
    ax.set_title("NES Comparison Across Conditions (* FDR<0.25, ** <0.01, *** <0.001)")
    ax.tick_params(axis="y", labelsize=7)
    plt.tight_layout()
    plt.savefig("multi_condition_gsea_heatmap.png", dpi=150, bbox_inches="tight")
    plt.close()

    print(f"\nSignificant gene sets in any condition: {has_sig.sum()}")
    return nes_matrix, sig_matrix

# Usage
ranked_dict = {
    "DrugA_vs_DMSO": pd.read_csv("drugA_ranked.csv"),
    "DrugB_vs_DMSO": pd.read_csv("drugB_ranked.csv"),
    "Combo_vs_DMSO": pd.read_csv("combo_ranked.csv"),
}
nes_mat, sig_mat = multi_condition_gsea(ranked_dict)
```

**Expected output**: A heatmap with NES scores across conditions. Shared enriched pathways suggest common mechanism; condition-specific enrichments reveal unique biology.

---

## 11. Reactome Pathway Enrichment with ReactomePA (R)

Reactome-specific enrichment with hierarchical pathway visualization.

```R
library(ReactomePA)
library(org.Hs.eg.db)
library(enrichplot)

# ---- Prepare gene list (Entrez IDs required) ----
sig_genes <- c("TP53", "BRCA1", "ATM", "CHEK2", "MDM2", "CDKN1A",
               "BAX", "BCL2", "CASP3", "CASP9", "RAD51", "XRCC5")

gene_ids <- clusterProfiler::bitr(sig_genes, fromType = "SYMBOL",
                                   toType = "ENTREZID", OrgDb = org.Hs.eg.db)

# ---- ORA: Reactome pathway enrichment ----
reactome_ora <- enrichPathway(
    gene         = gene_ids$ENTREZID,
    organism     = "human",
    pvalueCutoff = 0.05,
    pAdjustMethod = "BH",
    readable     = TRUE,         # convert IDs to gene symbols in output
    minGSSize    = 10,
    maxGSSize    = 500
)

cat("Significant Reactome pathways:", nrow(reactome_ora@result[reactome_ora@result$p.adjust < 0.05, ]), "\n")
print(head(as.data.frame(reactome_ora)[, c("Description", "GeneRatio", "p.adjust", "geneID")], 10))

# ---- GSEA: Reactome ----
# Requires ranked gene list (Entrez IDs as names, ranking metric as values)
gsea_reactome <- gsePathway(
    geneList      = gene_list,     # named, sorted numeric vector
    organism      = "human",
    minGSSize     = 15,
    maxGSSize     = 500,
    pvalueCutoff  = 0.25,
    pAdjustMethod = "BH",
    verbose       = TRUE
)

cat("Significant Reactome GSEA:", nrow(gsea_reactome@result[gsea_reactome@result$p.adjust < 0.25, ]), "\n")

# ---- Visualization ----
dotplot(reactome_ora, showCategory = 15, title = "Reactome ORA")
ggsave("reactome_ora_dotplot.png", width = 10, height = 8)

# Pathway hierarchy view (Reactome-specific)
viewPathway("DNA Repair", readable = TRUE, foldChange = gene_list)
ggsave("reactome_dna_repair_pathway.png", width = 14, height = 10)

# Enrichment map
reactome_pw <- pairwise_termsim(reactome_ora)
emapplot(reactome_pw, showCategory = 20)
ggsave("reactome_emapplot.png", width = 12, height = 10)

# GSEA running score for top pathway
gseaplot2(gsea_reactome, geneSetID = 1, title = gsea_reactome@result$Description[1])
ggsave("reactome_gsea_plot.png", width = 10, height = 5)

# Save
write.csv(as.data.frame(reactome_ora), "reactome_ora_results.csv", row.names = FALSE)
write.csv(as.data.frame(gsea_reactome), "reactome_gsea_results.csv", row.names = FALSE)
```

**Key parameters**: ReactomePA uses Reactome's hierarchical pathway structure, so enriched pathways include parent-child relationships. Use `viewPathway()` to see where your genes sit within the pathway diagram. Results often complement KEGG findings as Reactome has finer-grained pathway definitions.
