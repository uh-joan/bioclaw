---
name: geneontology
description: Gene Ontology (GO) specialist. Search GO terms, get term details, validate GO IDs, and explore ontology statistics across molecular function, biological process, and cellular component namespaces. Use when user mentions Gene Ontology, GO terms, molecular function, biological process, cellular component, GO enrichment, functional annotation, or GO:NNNNNNN IDs.
---

# Gene Ontology Specialist

Gene Ontology term data via the QuickGO API (EBI). Uses the `mcp__geneontology__go_data` tool for all queries.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_geneontology_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Full gene set enrichment analysis (ORA/GSEA across multiple databases) → use `gene-enrichment`
- KEGG pathway queries and metabolic pathway mapping → use `kegg-database`
- Reactome pathway details and reaction-level analysis → use `reactome-pathways`
- Protein functional annotations and sequence features → use `uniprot-protein-data`
- Gene expression analysis and differential expression → use `rnaseq-deseq2`
- Protein-protein interaction networks → use `protein-interactions`

## Available MCP Tool: `mcp__geneontology__go_data`

All Gene Ontology queries go through this single tool. Always use it instead of web searches for GO data.

### Methods

- `search_go_terms` -- Search GO terms by name, keyword, or description
- `get_go_term` -- Get detailed info for a specific GO term (definition, synonyms, xrefs)
- `validate_go_id` -- Check if a GO ID is valid and exists
- `get_ontology_stats` -- Get GO ontology statistics and evidence code reference

### Key Parameters

| Parameter | Used With | Description |
|-----------|-----------|-------------|
| `method` | All | Required. One of the 4 methods above |
| `query` | `search_go_terms` | Search text (function name, process, component) |
| `id` | `get_go_term`, `validate_go_id` | GO term ID (e.g., GO:0008150) or just the 7-digit number |
| `ontology` | `search_go_terms`, `get_ontology_stats` | Filter: molecular_function, biological_process, cellular_component, or all |
| `size` | `search_go_terms` | Max results 1-500 (default: 25) |
| `exact` | `search_go_terms` | Exact match only (boolean) |
| `include_obsolete` | `search_go_terms` | Include obsolete terms (boolean) |

### GO Namespaces

- **Molecular Function (F)**: Molecular activities of gene products (e.g., kinase activity, binding)
- **Biological Process (P)**: Larger biological programs (e.g., apoptosis, cell cycle)
- **Cellular Component (C)**: Cellular locations (e.g., nucleus, membrane)

### GO ID Format

GO identifiers follow the pattern `GO:NNNNNNN` (GO: followed by exactly 7 digits), e.g., `GO:0008150` (biological_process root).

### Example Calls

```
# Search for kinase-related terms
mcp__geneontology__go_data(method: "search_go_terms", query: "kinase activity", ontology: "molecular_function", size: 10)

# Get details for a specific GO term
mcp__geneontology__go_data(method: "get_go_term", id: "GO:0008150")

# Validate a GO ID
mcp__geneontology__go_data(method: "validate_go_id", id: "GO:0006915")

# Get ontology statistics
mcp__geneontology__go_data(method: "get_ontology_stats", ontology: "biological_process")
```

---

## Common Workflows

### Functional Annotation Lookup

Understand what a GO term means:

1. `search_go_terms` -- find the right GO term
2. `get_go_term` -- get full definition, synonyms, and cross-references

### GO Term Validation

Verify GO annotations in datasets:

1. `validate_go_id` -- check format and existence
2. `get_go_term` -- confirm the term is current (not obsolete)

### Ontology Exploration

Navigate the GO hierarchy:

1. `search_go_terms` with ontology filter -- find terms in a namespace
2. `get_go_term` -- get synonyms and related terms
3. `get_ontology_stats` -- understand namespace scope

---

## Cross-Reference with Other Skills

- Use `mcp__ensembl__ensembl_data` for genes annotated with GO terms
- Use `mcp__uniprot__uniprot_data` for protein GO annotations
- Use `mcp__kegg__kegg_data` for complementary pathway annotations
- Use `mcp__reactome__reactome_data` for pathway-level functional context
- Use `mcp__opentargets__opentargets_info` for disease associations of GO-annotated genes
- Use `mcp__pubmed__pubmed_articles` for literature on gene functions

## Completeness Checklist

- [ ] GO term search performed with appropriate ontology filter (BP/MF/CC)
- [ ] GO IDs validated for correctness and non-obsolete status
- [ ] Full term definitions retrieved with synonyms and cross-references
- [ ] Ontology namespace confirmed for each reported term
- [ ] Evidence codes reviewed and explained (experimental vs electronic annotation)
- [ ] Parent/child term relationships explored for context
- [ ] Related terms from complementary databases cross-referenced (KEGG, Reactome)
- [ ] Results synthesized into report (not raw tool output)
