---
name: reactome-pathways
description: Reactome biological pathway database specialist. Search pathways, get pathway details, find pathways by gene or disease, explore hierarchy, participants, reactions, and protein interactions. Use when user mentions Reactome, biological pathways, pathway analysis, signaling pathways, metabolic pathways, pathway hierarchy, pathway participants, or systems biology.
---

# Reactome Pathway Specialist

Curated biological pathway data via the Reactome Content Service API. Uses the `mcp__reactome__reactome_data` tool for all queries.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_reactome_pathways_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Protein-protein interaction networks beyond Reactome context → use `stringdb-interactions`
- Complementary pathway data from KEGG database → use `kegg-database`
- Gene set enrichment analysis (ORA/GSEA) on gene lists → use `gene-enrichment`
- Systems-level network modeling and simulation → use `systems-biology`
- Drug target contextualization and druggability → use `target-research`
- Genomic details of pathway genes → use `ensembl-genomics`

## Available MCP Tool: `mcp__reactome__reactome_data`

All Reactome queries go through this single tool. Always use it instead of web searches for Reactome pathway data.

### Methods

- `search_pathways` -- Search pathways by name, description, or keywords
- `get_pathway_details` -- Get comprehensive information about a specific pathway
- `find_pathways_by_gene` -- Find all pathways containing a specific gene or protein
- `find_pathways_by_disease` -- Find disease-associated pathways and mechanisms
- `get_pathway_hierarchy` -- Get parent/child relationships for a pathway
- `get_pathway_participants` -- Get all molecules (proteins, genes, compounds) in a pathway
- `get_pathway_reactions` -- Get all biochemical reactions within a pathway
- `get_protein_interactions` -- Get protein-protein interactions within pathways

### Key Parameters

| Parameter | Used With | Description |
|-----------|-----------|-------------|
| `method` | All | Required. One of the 8 methods above |
| `query` | `search_pathways` | Search query (pathway name, process, keywords) |
| `type` | `search_pathways` | Entity type: pathway, reaction, protein, complex, disease |
| `size` | `search_pathways`, `find_pathways_by_disease` | Max results 1-100 (default: 20/25) |
| `id` | `get_pathway_details`, `get_pathway_hierarchy`, `get_pathway_participants`, `get_pathway_reactions` | Reactome stable ID (e.g., R-HSA-68886) or pathway name |
| `gene` | `find_pathways_by_gene` | Gene symbol or UniProt ID (e.g., BRCA1, P04637) |
| `species` | `find_pathways_by_gene` | Species name (default: Homo sapiens) |
| `disease` | `find_pathways_by_disease` | Disease name or DOID identifier |
| `pathwayId` | `get_protein_interactions` | Reactome pathway stable ID |
| `interactionType` | `get_protein_interactions` | protein-protein, regulatory, catalysis, or all |

### Reactome ID Format

Reactome stable IDs follow the pattern `R-{species}-{number}`:
- **R-HSA-** = Homo sapiens (human)
- **R-MMU-** = Mus musculus (mouse)
- **R-RNO-** = Rattus norvegicus (rat)

### Example Calls

```
# Search for apoptosis pathways
mcp__reactome__reactome_data(method: "search_pathways", query: "apoptosis", type: "pathway", size: 10)

# Get details for a specific pathway
mcp__reactome__reactome_data(method: "get_pathway_details", id: "R-HSA-109581")

# Find all pathways containing TP53
mcp__reactome__reactome_data(method: "find_pathways_by_gene", gene: "TP53", species: "Homo sapiens")

# Find cancer-related pathways
mcp__reactome__reactome_data(method: "find_pathways_by_disease", disease: "cancer", size: 20)

# Get pathway hierarchy
mcp__reactome__reactome_data(method: "get_pathway_hierarchy", id: "R-HSA-109581")

# Get all participants in a pathway
mcp__reactome__reactome_data(method: "get_pathway_participants", id: "R-HSA-109581")

# Get reactions in a pathway
mcp__reactome__reactome_data(method: "get_pathway_reactions", id: "R-HSA-109581")

# Get protein interactions in a pathway
mcp__reactome__reactome_data(method: "get_protein_interactions", pathwayId: "R-HSA-109581", interactionType: "all")
```

---

## Common Workflows

### Gene-to-Pathway Analysis

Map a gene's biological context:

1. `find_pathways_by_gene` -- find all pathways containing the gene
2. `get_pathway_details` for top pathways -- understand pathway function
3. `get_pathway_participants` -- identify co-participants (potential interactors)

### Disease Pathway Exploration

Understand disease mechanisms:

1. `find_pathways_by_disease` -- find disease-associated pathways
2. `get_pathway_hierarchy` -- understand pathway relationships
3. `get_pathway_reactions` -- identify specific biochemical steps
4. `get_protein_interactions` -- map interaction network within pathway

### Pathway Comparison

Compare pathways across conditions:

1. `search_pathways` for related terms -- find candidate pathways
2. `get_pathway_participants` for each -- compare molecular composition
3. `get_pathway_reactions` for each -- compare biochemical steps

### Drug Target Contextualization

Understand a drug target in pathway context:

1. `find_pathways_by_gene` with the target gene -- find relevant pathways
2. `get_pathway_hierarchy` -- see where pathways sit in biology
3. `get_protein_interactions` -- find interaction partners in pathway context

---

## Cross-Reference with Other Skills

- Use `mcp__ensembl__ensembl_data` for genomic details of pathway genes
- Use `mcp__uniprot__uniprot_data` for protein details of pathway participants
- Use `mcp__stringdb__stringdb_data` for interaction networks beyond Reactome
- Use `mcp__kegg__kegg_data` for complementary pathway data from KEGG
- Use `mcp__opentargets__opentargets_info` for disease associations of pathway members
- Use `mcp__pubmed__pubmed_articles` for literature on pathway biology

## Completeness Checklist

- [ ] Pathway search terms identified and queried via `search_pathways`
- [ ] Gene-to-pathway mapping completed for all genes of interest via `find_pathways_by_gene`
- [ ] Pathway details retrieved for top-ranked pathways via `get_pathway_details`
- [ ] Pathway hierarchy explored to contextualize findings via `get_pathway_hierarchy`
- [ ] Pathway participants listed and cross-referenced with query genes
- [ ] Reactions within key pathways retrieved and summarized
- [ ] Protein-protein interactions within pathway context assessed
- [ ] Disease-pathway associations checked if disease context is relevant
- [ ] Cross-references to complementary databases (KEGG, STRING, UniProt) noted
- [ ] Report file finalized with no `[Analyzing...]` placeholders remaining
