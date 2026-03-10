# Enrichment Recipes

Computational recipes for gene set enrichment and over-representation analysis. Python (gseapy) and R (clusterProfiler) code templates.

**Related skills:** `gene-enrichment` (conceptual guidance), `deseq2-recipes` (upstream DE analysis), `rnaseq-deseq2` (experimental design).

---

### Recipe: gseapy Enrichr (Over-Representation Analysis)
**When to use:** You have a gene list (e.g., significant DEGs) and want to test for enriched pathways/terms.
**Input:** List of gene symbols.
**Output:** Enrichment results table with p-values, odds ratios, overlapping genes.

```python
import gseapy as gp
import pandas as pd

# Gene list (e.g., significant DEGs from DESeq2)
gene_list = pd.read_csv("up_genes.txt", header=None)[0].tolist()

# GO Biological Process
go_results = gp.enrichr(
    gene_list=gene_list,
    gene_sets="GO_Biological_Process_2021",
    organism="human",
    outdir="enrichr_GO_BP",
    cutoff=0.05,
)
go_df = go_results.results
go_sig = go_df[go_df["Adjusted P-value"] < 0.05].sort_values("Adjusted P-value")
print(go_sig[["Term", "Adjusted P-value", "Odds Ratio", "Genes"]].head(20))

# KEGG pathways
kegg_results = gp.enrichr(
    gene_list=gene_list,
    gene_sets="KEGG_2021_Human",  # or "KEGG_2019_Mouse"
    organism="human",
    outdir="enrichr_KEGG",
    cutoff=0.05,
)

# Reactome pathways
reactome_results = gp.enrichr(
    gene_list=gene_list,
    gene_sets="Reactome_2022",
    organism="human",
    outdir="enrichr_Reactome",
    cutoff=0.05,
)

# WikiPathways
wiki_results = gp.enrichr(
    gene_list=gene_list,
    gene_sets="WikiPathways_2019_Human",  # or "WikiPathways_2019_Mouse"
    organism="human",
    outdir="enrichr_WikiPathways",
    cutoff=0.05,
)

# Multiple gene sets at once
multi_results = gp.enrichr(
    gene_list=gene_list,
    gene_sets=["GO_Biological_Process_2021", "KEGG_2021_Human", "Reactome_2022"],
    organism="human",
    outdir="enrichr_multi",
    cutoff=0.05,
)
```

**Common pitfalls:**
- Gene symbols must match the database (human symbols are uppercase, mouse are Title Case for some databases).
- Enrichr uses Fisher's exact test — it needs a discrete gene list, not a ranked list (use prerank for that).
- `cutoff` filters the output display, not the statistical test itself.

---

### Recipe: gseapy Prerank (GSEA with Pre-Ranked List)
**When to use:** Running GSEA on all genes ranked by fold change or significance — no arbitrary cutoff needed.
**Input:** DataFrame with gene names and ranking metric (log2FC or -log10(pval)*sign(FC)).
**Output:** GSEA enrichment scores, NES, FDR for each gene set.

```python
import gseapy as gp
import pandas as pd

# Load ranked gene list (from DESeq2 results)
deseq_results = pd.read_csv("deseq2_results.csv", index_col=0)
deseq_results = deseq_results.dropna(subset=["pvalue", "log2FoldChange"])

# Ranking method 1: signed -log10(pvalue) (recommended)
import numpy as np
deseq_results["rank"] = -np.log10(deseq_results["pvalue"]) * np.sign(deseq_results["log2FoldChange"])
deseq_results = deseq_results[np.isfinite(deseq_results["rank"])]
ranked = deseq_results[["rank"]].sort_values("rank", ascending=False)

# Ranking method 2: shrunken log2FC
# ranked = deseq_results[["log2FoldChange"]].sort_values("log2FoldChange", ascending=False)

# Run GSEA prerank
pre_res = gp.prerank(
    rnk=ranked,
    gene_sets="GO_Biological_Process_2021",
    processes=4,
    permutation_num=1000,
    outdir="gsea_prerank_GO",
    seed=42,
    min_size=15,
    max_size=500,
)

# Results
gsea_df = pre_res.res2d
gsea_sig = gsea_df[gsea_df["FDR q-val"] < 0.25].sort_values("NES", ascending=False)
print(gsea_sig[["Term", "NES", "FDR q-val", "FWER p-val"]].head(20))

# With MSigDB gene sets (Hallmark)
pre_res_hallmark = gp.prerank(
    rnk=ranked,
    gene_sets="MSigDB_Hallmark_2020",
    processes=4,
    permutation_num=1000,
    outdir="gsea_prerank_hallmark",
    seed=42,
)
```

**Common pitfalls:**
- GSEA uses FDR < 0.25 as default threshold (not 0.05) — this is by design.
- Ranking must use all genes, not just significant ones.
- Remove Inf/-Inf values from the ranking metric before running.
- `min_size` and `max_size` filter gene sets by number of overlapping genes.

---

### Recipe: clusterProfiler enrichGO (R)
**When to use:** GO enrichment in R with built-in redundancy reduction via simplify().
**Input:** Vector of Entrez IDs or gene symbols.
**Output:** Enrichment results with simplified GO terms.

```r
library(clusterProfiler)
library(org.Hs.eg.db)  # or org.Mm.eg.db for mouse

# Convert symbols to Entrez IDs if needed
gene_symbols <- readLines("up_genes.txt")
gene_entrez <- bitr(gene_symbols,
  fromType = "SYMBOL",
  toType   = "ENTREZID",
  OrgDb    = org.Hs.eg.db
)$ENTREZID

# Background: all expressed genes
bg_symbols <- readLines("background_genes.txt")
bg_entrez <- bitr(bg_symbols,
  fromType = "SYMBOL",
  toType   = "ENTREZID",
  OrgDb    = org.Hs.eg.db
)$ENTREZID

# GO Biological Process enrichment
ego <- enrichGO(
  gene          = gene_entrez,
  universe      = bg_entrez,
  OrgDb         = org.Hs.eg.db,
  ont           = "BP",       # "BP", "MF", "CC", or "ALL"
  pAdjustMethod = "BH",
  pvalueCutoff  = 0.05,
  qvalueCutoff  = 0.1,
  readable      = TRUE        # Convert Entrez IDs to symbols in output
)

# Simplify redundant GO terms
ego_simple <- simplify(ego, cutoff = 0.7, by = "p.adjust", select_fun = min)

# View results
head(as.data.frame(ego_simple), 20)

# Save
write.csv(as.data.frame(ego_simple), "GO_BP_enrichment.csv", row.names = FALSE)
```

**Common pitfalls:**
- `OrgDb` must match your organism: `org.Hs.eg.db` (human), `org.Mm.eg.db` (mouse), `org.Rn.eg.db` (rat).
- `simplify()` cutoff (0.7) controls how aggressively redundant terms are merged — lower = more aggressive.
- Always provide a background (`universe`) — using all expressed genes, not the whole genome.

---

### Recipe: clusterProfiler enrichKEGG (R)
**When to use:** KEGG pathway enrichment in R.
**Input:** Vector of Entrez IDs.
**Output:** Enriched KEGG pathways.

```r
library(clusterProfiler)

# KEGG enrichment (requires Entrez IDs)
kk <- enrichKEGG(
  gene         = gene_entrez,
  universe     = bg_entrez,
  organism     = "hsa",       # "hsa" = human, "mmu" = mouse
  pAdjustMethod = "BH",
  pvalueCutoff = 0.05,
  qvalueCutoff = 0.1
)

# Convert Entrez IDs to symbols in results
library(org.Hs.eg.db)
kk <- setReadable(kk, OrgDb = org.Hs.eg.db, keyType = "ENTREZID")

head(as.data.frame(kk), 20)

# GSEA with KEGG (using ranked list)
# Prepare named ranked vector
deseq_df <- read.csv("deseq2_results.csv", row.names = 1)
deseq_df <- deseq_df[!is.na(deseq_df$pvalue), ]
gene_map <- bitr(rownames(deseq_df),
  fromType = "SYMBOL", toType = "ENTREZID", OrgDb = org.Hs.eg.db)
deseq_mapped <- merge(deseq_df, gene_map, by.x = "row.names", by.y = "SYMBOL")

ranked_vec <- deseq_mapped$log2FoldChange
names(ranked_vec) <- deseq_mapped$ENTREZID
ranked_vec <- sort(ranked_vec, decreasing = TRUE)

kk_gsea <- gseKEGG(
  geneList     = ranked_vec,
  organism     = "hsa",
  minGSSize    = 15,
  maxGSSize    = 500,
  pvalueCutoff = 0.25,
  verbose      = FALSE
)
head(as.data.frame(kk_gsea))
```

**Common pitfalls:**
- KEGG requires Entrez IDs — convert from symbols first.
- KEGG organism codes: "hsa" (human), "mmu" (mouse), "rno" (rat). Full list: https://www.genome.jp/kegg/catalog/org_list.html
- KEGG API can be slow or unavailable — retry if connection fails.

---

### Recipe: Converting Gene IDs
**When to use:** Switching between Ensembl, Entrez, and Symbol IDs for different tools.
**Input:** Gene IDs in one format.
**Output:** Mapped gene IDs in the target format.

```python
# Python: using mygene
import mygene
mg = mygene.MyGeneInfo()

# Ensembl to Symbol + Entrez
gene_ids = ["ENSG00000141510", "ENSG00000171862", "ENSG00000141736"]
result = mg.querymany(gene_ids, scopes="ensembl.gene", fields="symbol,entrezgene", species="human")
for hit in result:
    print(f"{hit['query']} -> {hit.get('symbol', 'NA')} (Entrez: {hit.get('entrezgene', 'NA')})")

# Symbol to Entrez
symbols = ["TP53", "PTEN", "BRCA1"]
result = mg.querymany(symbols, scopes="symbol", fields="entrezgene", species="human")

# Batch conversion with pandas
import pandas as pd
df = pd.DataFrame(result)
id_map = df[["query", "symbol", "entrezgene"]].dropna()
```

```r
# R: using clusterProfiler::bitr or AnnotationDbi
library(org.Hs.eg.db)  # or org.Mm.eg.db

# Symbol to Entrez
gene_map <- bitr(gene_symbols,
  fromType = "SYMBOL",
  toType   = "ENTREZID",
  OrgDb    = org.Hs.eg.db
)

# Ensembl to Symbol + Entrez
ens_map <- bitr(ensembl_ids,
  fromType = "ENSEMBL",
  toType   = c("SYMBOL", "ENTREZID"),
  OrgDb    = org.Hs.eg.db
)

# Check available key types
keytypes(org.Hs.eg.db)
# Common: SYMBOL, ENTREZID, ENSEMBL, REFSEQ, UNIPROT, GENENAME
```

**Common pitfalls:**
- Not all IDs map 1:1 — some Ensembl IDs map to multiple symbols (or none).
- Version suffixes on Ensembl IDs (e.g., ENSG00000141510.15) must be stripped: `gsub("\\..*", "", ids)`.
- Mouse symbols are typically Title Case (Tp53), human are uppercase (TP53).

---

### Recipe: Background Gene Set
**When to use:** Defining the statistical background for over-representation analysis.
**Input:** All genes tested in your experiment.
**Output:** Proper background gene set.

```python
# Python: background from DESeq2 results (all tested genes)
import pandas as pd

deseq_results = pd.read_csv("deseq2_results.csv", index_col=0)
background = deseq_results.index.tolist()

# Use background in enrichr
import gseapy as gp
enr = gp.enrichr(
    gene_list=sig_genes,
    gene_sets="GO_Biological_Process_2021",
    organism="human",
    background=background,  # critical for correct statistics
    outdir="enrichr_with_bg",
    cutoff=0.05,
)
```

```r
# R: background from DESeq2 results
res_df <- as.data.frame(res)
background <- rownames(res_df[!is.na(res_df$padj), ])

# Convert to Entrez for clusterProfiler
bg_entrez <- bitr(background,
  fromType = "SYMBOL", toType = "ENTREZID", OrgDb = org.Hs.eg.db
)$ENTREZID

# Pass as universe
ego <- enrichGO(
  gene     = gene_entrez,
  universe = bg_entrez,
  OrgDb    = org.Hs.eg.db,
  ont      = "BP"
)
```

**Common pitfalls:**
- Using the whole genome as background inflates significance — always use expressed/tested genes.
- Background must be a superset of your gene list — all query genes should be in the background.
- Enrichr web interface uses the whole genome by default; the API lets you specify background.

---

### Recipe: Interpreting and Filtering Enrichment Results
**When to use:** Understanding output columns and narrowing results to relevant terms.
**Input:** Enrichment results table.
**Output:** Filtered, interpreted results.

```python
import pandas as pd

df = enr_results.results  # gseapy enrichr output
# Key columns: Term, Overlap ("k/K"), P-value, Adjusted P-value, Odds Ratio, Genes
# For GSEA: NES (enrichment direction/magnitude), FDR q-val (use < 0.25), Lead edge genes

# Parse overlap and filter
df[["k", "K"]] = df["Overlap"].str.split("/", expand=True).astype(int)
df["gene_ratio"] = df["k"] / df["K"]
sig = df[(df["Adjusted P-value"] < 0.05) & (df["k"] >= 3)].sort_values("Adjusted P-value")

# Filter by pathway keywords
immune = sig[sig["Term"].str.contains("immune|inflammatory|cytokine", case=False)]
```

```r
# R: clusterProfiler filtering
library(dplyr)
ego_filtered <- ego_simple
ego_filtered@result <- ego_filtered@result %>%
  filter(p.adjust < 0.01, Count >= 5)

# Filter by keyword
immune_terms <- ego_simple@result %>%
  filter(grepl("immune|inflammatory|cytokine", Description, ignore.case = TRUE))

# Extract genes for a specific term
term_genes <- unlist(strsplit(
  ego_simple@result$geneID[ego_simple@result$Description == "immune response"], "/"))
```

**Common pitfalls:**
- Use Adjusted P-value (not raw) for significance decisions.
- High odds ratio with few overlapping genes can be misleading — check overlap count.
- Filter after `simplify()`, not before. Very broad terms may be uninformative despite low p-values.

---

### Recipe: Dot Plot Visualization
**When to use:** Creating publication-ready enrichment summary plots.
**Input:** Enrichment results.
**Output:** Dot plot showing top enriched terms.

```python
# gseapy dot plot
import gseapy as gp
import matplotlib.pyplot as plt
from gseapy import dotplot

ax = dotplot(
    enr_results.res2d,
    column="Adjusted P-value",
    title="GO Biological Process",
    size=6,
    top_term=15,
    figsize=(8, 10),
    cutoff=0.05,
)
plt.tight_layout()
plt.savefig("enrichr_dotplot.pdf", dpi=300, bbox_inches="tight")
```

```r
# clusterProfiler dot plot
library(clusterProfiler)
library(enrichplot)

# Basic dot plot
dotplot(ego_simple, showCategory = 15, title = "GO Biological Process") +
  theme(axis.text.y = element_text(size = 10))
ggsave("dotplot_GO.pdf", width = 10, height = 8)

# KEGG dot plot
dotplot(kk, showCategory = 15, title = "KEGG Pathways")

# Customized dot plot
dotplot(ego_simple, showCategory = 15,
  x = "GeneRatio",
  color = "p.adjust",
  size = "Count",
  font.size = 10,
  title = "GO BP Enrichment"
) +
  scale_color_gradient(low = "red", high = "blue") +
  theme_minimal()
ggsave("dotplot_custom.pdf", width = 10, height = 8)

# Bar plot alternative
barplot(ego_simple, showCategory = 15, title = "GO Biological Process")
```

**Common pitfalls:**
- Long term names get cut off — truncate or increase figure width.
- Dot size and color should encode different variables (e.g., size = gene count, color = p-value).
- Show 10-20 terms maximum for readability.

---

### Recipe: Comparing Enrichment Across Conditions
**When to use:** Comparing pathway enrichment side-by-side for multiple conditions/contrasts.
**Input:** Multiple gene lists from different comparisons.
**Output:** Comparative enrichment plot.

```r
library(clusterProfiler)
library(org.Hs.eg.db)

# Convert gene lists to Entrez
up_A_entrez <- bitr(up_genes_A, fromType = "SYMBOL", toType = "ENTREZID", OrgDb = org.Hs.eg.db)$ENTREZID
up_B_entrez <- bitr(up_genes_B, fromType = "SYMBOL", toType = "ENTREZID", OrgDb = org.Hs.eg.db)$ENTREZID
up_C_entrez <- bitr(up_genes_C, fromType = "SYMBOL", toType = "ENTREZID", OrgDb = org.Hs.eg.db)$ENTREZID

# compareCluster for multi-condition comparison
gene_clusters <- list(
  "Condition_A" = up_A_entrez,
  "Condition_B" = up_B_entrez,
  "Condition_C" = up_C_entrez
)

cc <- compareCluster(
  geneClusters  = gene_clusters,
  fun           = "enrichGO",
  OrgDb         = org.Hs.eg.db,
  ont           = "BP",
  pAdjustMethod = "BH",
  pvalueCutoff  = 0.05,
  readable      = TRUE
)

# Dot plot comparison
dotplot(cc, showCategory = 10, title = "GO BP Comparison Across Conditions") +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))
ggsave("compare_enrichment.pdf", width = 12, height = 10)

# KEGG comparison
cc_kegg <- compareCluster(
  geneClusters  = gene_clusters,
  fun           = "enrichKEGG",
  organism      = "hsa",
  pvalueCutoff  = 0.05
)
dotplot(cc_kegg, showCategory = 10, title = "KEGG Comparison")
```

```python
# Python: run enrichr per condition, then combine
import gseapy as gp
import pandas as pd

conditions = {"Cond_A": up_genes_A, "Cond_B": up_genes_B, "Cond_C": up_genes_C}
all_results = []
for name, genes in conditions.items():
    enr = gp.enrichr(gene_list=genes, gene_sets="GO_Biological_Process_2021",
                     organism="human", outdir=f"enrichr_{name}", cutoff=0.05)
    df = enr.results.copy()
    df["Condition"] = name
    all_results.append(df)

combined = pd.concat(all_results)
combined_sig = combined[combined["Adjusted P-value"] < 0.05]
```

**Common pitfalls:**
- `compareCluster` applies multiple testing correction across all clusters — p-values may differ from individual analyses.
- Ensure gene ID types are consistent across all conditions.
- Heatmap approach assumes terms are comparable across conditions — use the same gene set database for all.

---

## Parameter Reference

| Parameter | Tool | Default | When to change |
|-----------|------|---------|----------------|
| `gene_sets` | gseapy | varies | Match to organism and database version (e.g., KEGG_2021_Human) |
| `organism` | gseapy | "human" | Set to "mouse", "rat", etc. as needed |
| `background` | gseapy enrichr | genome | Set to all expressed genes for proper statistics |
| `cutoff` | gseapy | 0.05 | Adjusts output filtering, not the test itself |
| `permutation_num` | gseapy prerank | 1000 | Increase to 10000 for publication; decrease for speed |
| `min_size` / `max_size` | gseapy prerank | 15 / 500 | Adjust to include/exclude very small or large gene sets |
| `ont` | clusterProfiler | "BP" | "MF" (molecular function), "CC" (cellular component), "ALL" |
| `pvalueCutoff` | clusterProfiler | 0.05 | Relax to 0.1 for exploratory analysis |
| `qvalueCutoff` | clusterProfiler | 0.2 | Additional FDR filter on top of p.adjust |
| `simplify cutoff` | clusterProfiler | 0.7 | Lower (e.g., 0.5) for more aggressive redundancy removal |
| `readable` | clusterProfiler | FALSE | Set TRUE to convert Entrez IDs to symbols in output |
| `universe` | clusterProfiler | genome | Set to all expressed/tested genes |
| `organism` | enrichKEGG | "hsa" | "mmu" (mouse), "rno" (rat) — KEGG organism codes |
