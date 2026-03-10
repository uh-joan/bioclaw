---
name: gtex-expression
description: GTEx gene expression and eQTL specialist. Query tissue-specific gene expression, median expression, top expressed genes, eQTL associations, tissue metadata, variants, and gene information from GTEx Portal. Use when user mentions GTEx, tissue expression, eQTL, expression quantitative trait loci, tissue-specific, gene expression across tissues, or genotype-tissue expression.
---

# GTEx Expression Specialist

Genotype-tissue expression data via the GTEx Portal API (v2). Uses the `mcp__gtex__gtex_data` tool for all queries.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_gtex-expression_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Interpreting GWAS SNPs and variant annotations → use `gwas-snp-interpretation`
- Looking up protein structure or function → use `uniprot-protein-data`
- Gene enrichment or pathway analysis → use `gene-enrichment`
- Querying Ensembl for gene/variant annotations → use `ensembl-genomics`
- Drug target discovery from genetic associations → use `gwas-drug-discoverer`

## Available MCP Tool: `mcp__gtex__gtex_data`

All GTEx queries go through this single tool. Always use it instead of web searches for GTEx data.

### Methods

- `search_genes` -- Search genes by symbol, name, or GENCODE ID
- `get_gene_expression` -- Get expression data across tissues for a gene
- `get_median_gene_expression` -- Get median expression per tissue
- `get_top_expressed_genes` -- Get highest expressed genes in a tissue
- `get_single_tissue_eqtls` -- Get eQTL associations for a gene in a tissue
- `get_multi_tissue_eqtls` -- Get multi-tissue eQTL (Metasoft) results
- `get_tissue_info` -- List all GTEx tissues with metadata
- `get_variants` -- Look up variants in a genomic region
- `get_gene_info` -- Get detailed gene information

### Key Parameters

| Parameter | Used With | Description |
|-----------|-----------|-------------|
| `method` | All | Required. One of the 9 methods above |
| `query` | `search_genes` | Gene search query (symbol, name, GENCODE ID) |
| `gencodeId` | Expression/eQTL methods, `get_gene_info` | GENCODE gene ID (e.g., ENSG00000141510.16) |
| `geneSymbol` | `get_gene_info` | Gene symbol (e.g., TP53) |
| `tissueSiteDetailId` | `get_gene_expression`, `get_top_expressed_genes`, `get_single_tissue_eqtls` | Tissue ID (e.g., Muscle_Skeletal, Brain_Cortex, Whole_Blood) |
| `chr` | `get_variants` | Chromosome (e.g., chr1) |
| `start`, `end` | `get_variants` | Genomic region coordinates (1-based) |
| `variantId` | `get_multi_tissue_eqtls` | Variant ID for filtering |
| `datasetId` | Most methods | GTEx dataset (default: gtex_v8) |
| `filterMtGene` | `get_top_expressed_genes` | Filter mitochondrial genes (default: true) |
| `limit` | `get_top_expressed_genes` | Max results (default: 50) |
| `page`, `pageSize` | `search_genes` | Pagination (default: 0, 50) |

### Common Tissue IDs

Brain_Cortex, Brain_Cerebellum, Heart_Left_Ventricle, Liver, Lung, Muscle_Skeletal, Whole_Blood, Adipose_Subcutaneous, Kidney_Cortex, Pancreas, Skin_Sun_Exposed_Lower_leg, Thyroid

Use `get_tissue_info` to get the complete list.

### Example Calls

```
# Search for a gene
mcp__gtex__gtex_data(method: "search_genes", query: "TP53")

# Get expression across all tissues
mcp__gtex__gtex_data(method: "get_median_gene_expression", gencodeId: "ENSG00000141510.16")

# Get top expressed genes in brain cortex
mcp__gtex__gtex_data(method: "get_top_expressed_genes", tissueSiteDetailId: "Brain_Cortex", limit: 20)

# Get eQTL for a gene in a tissue
mcp__gtex__gtex_data(method: "get_single_tissue_eqtls", gencodeId: "ENSG00000141510.16", tissueSiteDetailId: "Whole_Blood")

# Look up variants in a region
mcp__gtex__gtex_data(method: "get_variants", chr: "chr17", start: 7668402, end: 7687550)
```

---

## Common Workflows

### Tissue Expression Profiling

Understand where a gene is expressed:

1. `search_genes` -- find the GENCODE ID
2. `get_median_gene_expression` -- see expression across all tissues
3. `get_gene_expression` with specific tissue -- get detailed distribution

### eQTL Analysis

Find regulatory variants:

1. `search_genes` -- get GENCODE ID
2. `get_single_tissue_eqtls` -- find eQTLs in tissue of interest
3. `get_multi_tissue_eqtls` -- see if eQTL is shared across tissues
4. `get_variants` -- get variant details in the region

### Tissue-Specific Gene Discovery

Find key genes in a tissue:

1. `get_tissue_info` -- list available tissues
2. `get_top_expressed_genes` -- find highly expressed genes
3. `get_gene_info` for top hits -- get gene details

---

## Cross-Reference with Other Skills

- Use `mcp__ensembl__ensembl_data` for gene/variant annotations
- Use `mcp__uniprot__uniprot_data` for protein-level information of expressed genes
- Use `mcp__opentargets__opentargets_info` for disease associations of eQTL genes
- Use `mcp__geneontology__go_data` for functional annotations of tissue-specific genes
- Use `mcp__pubmed__pubmed_articles` for literature on tissue-specific expression

---

## Completeness Checklist

- [ ] Gene resolved to GENCODE ID via `search_genes`
- [ ] Median expression across all tissues retrieved and summarized
- [ ] Disease-relevant tissues identified and expression levels compared
- [ ] eQTL analysis performed in tissues of interest
- [ ] Multi-tissue eQTL patterns assessed for tissue specificity vs sharing
- [ ] Top expressed genes in key tissues identified for context
- [ ] Tissue metadata reviewed to confirm correct tissue IDs used
- [ ] Cross-references to Ensembl, UniProt, or Open Targets included where relevant
- [ ] Report file created with no remaining `[Analyzing...]` placeholders
