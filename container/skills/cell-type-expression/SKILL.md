---
name: cell-type-expression
description: "Single-cell gene expression atlas specialist using CZ CELLxGENE. Use when user asks about cell types, single-cell RNA-seq, gene expression by cell type, tissue expression, cell atlas, scRNA-seq datasets, CELLxGENE, cell type markers, or tissue-specific expression. Covers dataset discovery, collection browsing, and cell type expression context for drug targets and biomarkers."
---

# CELLxGENE Atlas

> **Code recipes**: See [recipes.md](recipes.md) for copy-paste executable workflows.

Single-cell gene expression atlas specialist powered by CZ CELLxGENE Discover — the largest standardized collection of single-cell RNA-seq datasets. Browse collections, discover datasets by tissue/disease/organism, and retrieve cell-type-resolved expression data. Essential for understanding which cell types express a drug target, identifying biomarkers, and providing cellular context for protein engineering and pharmacogenomics.

## Report-First Workflow

1. **Create report file immediately**: `[gene/tissue]_cellxgene_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## Cross-Reference: Other Skills

- **Drug target validation and genetic evidence** -> use drug-target-validator skill
- **Protein expression and function data** -> use protein-interactions skill (UniProt, STRING)
- **Pharmacogenomics and drug-gene relationships** -> use pharmacogenomics-specialist skill (ClinPGx)
- **Variant interpretation in disease context** -> use variant-interpretation skill
- **Protein therapeutic design for expressed targets** -> use protein-therapeutic-design skill

## When NOT to Use This Skill

- Bulk RNA-seq or microarray data → use GEO MCP
- Protein-level expression (not transcript) → use UniProt via `protein-interactions`
- Variant pathogenicity classification → use `variant-interpretation`
- Drug interaction analysis → use `drug-interaction-analyst`

## Available MCP Tools

### `mcp__cellxgene__cellxgene_data` (CZ CELLxGENE Discover)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `list_collections` | Browse all curated collections | *(none)* |
| `get_collection` | Get details for a specific collection | `collection_id` |
| `list_datasets` | Browse all available datasets | *(none)* |
| `get_dataset_versions` | Get version history for a dataset | `dataset_id` |
| `get_dataset_version` | Get specific dataset version details | `dataset_version_id` |
| `get_collection_versions` | Get version history for a collection | `collection_id` |
| `get_collection_version` | Get specific collection version | `collection_version_id` |
| `get_dataset_manifest` | Get download manifest (H5AD, RDS files) | `dataset_id` |

### `mcp__uniprot__uniprot_data` (Protein Context)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_by_gene` | Find protein by gene name | `gene`, `organism`, `size` |
| `get_protein_info` | Full protein profile, tissue expression | `accession`, `format` |
| `search_by_localization` | Proteins by subcellular location | `location`, `organism`, `size` |

### `mcp__pubmed__pubmed_articles` (Literature)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Keyword search | `keywords`, `num_results` |
| `search_advanced` | Filtered search | `term`, `start_date`, `end_date`, `num_results` |

### `mcp__openalex__openalex_search` (Broader Literature)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_works` | Search academic works | `query`, `per_page` |

---

## Analysis Pipeline

### Phase 1: Collection Discovery

Find relevant single-cell datasets for a tissue, disease, or gene.

```
1. mcp__cellxgene__cellxgene_data(method: "list_collections")
   -> Browse all curated collections
   -> Filter by tissue (e.g., "lung", "brain", "liver"), disease, or organism
   -> Note collection IDs for relevant datasets

2. mcp__cellxgene__cellxgene_data(method: "get_collection", collection_id: "COLLECTION_ID")
   -> Collection metadata: title, description, DOI, datasets included
   -> Identify datasets with the tissue/cell type of interest

3. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_NAME single-cell RNA-seq TISSUE", num_results: 10)
   -> Published single-cell studies for this gene/tissue combination
```

### Phase 2: Dataset Exploration

Drill into specific datasets for cell type composition and metadata.

```
1. mcp__cellxgene__cellxgene_data(method: "list_datasets")
   -> All available datasets with tissue, organism, disease, assay type
   -> Filter for relevant datasets

2. mcp__cellxgene__cellxgene_data(method: "get_dataset_versions", dataset_id: "DATASET_ID")
   -> Version history — use latest version for most current data

3. mcp__cellxgene__cellxgene_data(method: "get_dataset_version", dataset_version_id: "VERSION_ID")
   -> Specific version details: cell count, gene count, cell types, assay

4. mcp__cellxgene__cellxgene_data(method: "get_dataset_manifest", dataset_id: "DATASET_ID")
   -> Download links for H5AD (AnnData) and RDS (Seurat) files
   -> Use for downstream analysis with scanpy or Seurat
```

### Phase 3: Gene Expression Context

Contextualize a target gene's expression across cell types and tissues.

```
1. mcp__uniprot__uniprot_data(method: "search_by_gene", gene: "GENE_NAME", organism: "human", size: 3)
   -> Confirm gene identity and protein function

2. mcp__uniprot__uniprot_data(method: "get_protein_info", accession: "UNIPROT_ACC", format: "json")
   -> Tissue expression from UniProt (bulk-level, protein-level)

3. mcp__cellxgene__cellxgene_data(method: "list_collections")
   -> Find collections with datasets covering tissues where the gene is expressed
   -> Cell-type resolution adds granularity beyond bulk tissue data

4. mcp__pubmed__pubmed_articles(method: "search_advanced", term: "GENE_NAME scRNA-seq cell type expression", start_date: "2022-01-01", num_results: 10)
   -> Recent single-cell studies on this gene's expression pattern

SYNTHESIS:
  - Which cell types express the gene? (On-target effect)
  - Which cell types do NOT express it? (Safety — off-target)
  - Is expression cell-type-specific or ubiquitous?
  - Does expression change in disease states?
```

### Phase 4: Drug Target Cell Type Assessment

For a drug target, assess which cell types would be affected.

```
1. Identify expressing cell types from Phase 3

2. mcp__cellxgene__cellxgene_data(method: "list_collections")
   -> Find disease-specific collections (e.g., "COVID-19", "cancer", "fibrosis")
   -> Compare target expression in healthy vs disease tissue

3. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "GENE_NAME drug target cell type specificity therapeutic window", num_results: 10)
   -> Published evidence on cell-type-selective targeting

4. Cross-reference with pharmacogenomics:
   -> Hand off to pharmacogenomics-specialist for drug-gene interaction context
```

---

## Dataset Types in CELLxGENE

| Assay | Resolution | Throughput | Best For |
|-------|-----------|-----------|----------|
| **10x Chromium** | Single cell | High (10K-100K cells) | Cell type discovery, atlas building |
| **Smart-seq2** | Single cell | Low (100-1000 cells) | Full-length transcripts, isoform analysis |
| **CITE-seq** | Single cell + protein | Medium | Joint RNA + protein surface markers |
| **Spatial transcriptomics** | Sub-cellular to spot | Medium | Tissue architecture, spatial context |
| **snRNA-seq** | Single nucleus | High | Tissues hard to dissociate (brain, muscle) |

---

## Common Cell Type Markers

| Cell Type | Key Markers | Tissue |
|-----------|------------|--------|
| T cells | CD3D, CD3E, CD4, CD8A | Blood, lymph, tumor |
| B cells | CD19, CD79A, MS4A1 | Blood, lymph |
| Macrophages | CD68, CD163, MARCO | All tissues |
| Fibroblasts | COL1A1, VIM, DCN | Connective tissue |
| Epithelial | EPCAM, KRT18, CDH1 | Mucosal surfaces |
| Endothelial | PECAM1, VWF, CDH5 | Vasculature |
| Neurons | RBFOX3, MAP2, SYP | Brain, peripheral nerves |
| Hepatocytes | ALB, HNF4A, CYP3A4 | Liver |

---

## Multi-Agent Workflow Examples

**"Which cell types express my drug target PCSK9?"**
1. CELLxGENE Atlas -> Find liver datasets, identify hepatocyte-specific expression
2. Drug Target Validator -> Genetic evidence, GWAS associations
3. Protein Interactions -> PCSK9 interaction network (LDLR binding)

**"Find single-cell datasets for lung fibrosis"**
1. CELLxGENE Atlas -> Browse collections for IPF/fibrosis, list datasets with cell types
2. Variant Interpretation -> Check fibrosis-associated variants in expressed genes
3. Protein Therapeutic Design -> Design binder for fibrosis target

**"Is my designed protein's target expressed in off-target tissues?"**
1. CELLxGENE Atlas -> Expression across all available tissues and cell types
2. Protein Therapeutic Design -> Assess targeting strategy given expression profile
3. Drug Interaction Analyst -> Check metabolizing enzyme expression in affected tissues

**"Compare gene expression between healthy and disease tissue at single-cell level"**
1. CELLxGENE Atlas -> Find matched healthy/disease collections
2. CELLxGENE Atlas -> Get dataset manifests for download and analysis
3. Variant Interpretation -> Disease-associated variants in differentially expressed genes

## Completeness Checklist

- [ ] Relevant collections and datasets identified
- [ ] Target gene expression profiled across cell types
- [ ] Cell-type specificity assessed (on-target vs off-target)
- [ ] Disease context included where relevant (healthy vs disease expression)
- [ ] Dataset download links provided (H5AD/RDS) for further analysis
- [ ] Cross-referenced with protein-level data (UniProt)
- [ ] Literature support for cell-type expression patterns
- [ ] Report file finalized with no `[Analyzing...]` placeholders
