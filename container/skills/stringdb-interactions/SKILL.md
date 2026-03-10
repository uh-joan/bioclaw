---
name: stringdb-interactions
description: STRING protein-protein interaction database specialist. Build interaction networks, find interaction partners, perform functional enrichment analysis, get protein annotations, find homologs across species, and search proteins. Use when user mentions STRING, protein interactions, interaction network, interaction partners, functional enrichment, GO enrichment, KEGG enrichment, protein network analysis, network biology, or systems biology.
---

# STRING Protein Interaction Specialist

Protein-protein interaction data and network analysis via the STRING database API. Uses the `mcp__stringdb__stringdb_data` tool for all queries.

## Report-First Workflow

1. **Create report file immediately**: `[protein]_stringdb_interactions_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill
- Detailed protein structure and function annotation → use `uniprot-protein-data`
- Genomic context and gene information → use `ensembl-genomics`
- Disease association and druggability of network members → use `drug-target-analyst`
- Drug and compound data for identified targets → use `drug-research`
- Pathway-level modeling and systems analysis → use `systems-biology`
- Literature context for protein interactions → use `literature-deep-research`

## Available MCP Tool: `mcp__stringdb__stringdb_data`

All STRING data queries go through this single tool. Always use it instead of web searches for STRING interaction data.

### Methods

- `get_protein_interactions` -- Get direct interaction partners for a protein with confidence scores and evidence breakdown
- `get_interaction_network` -- Build and analyze a network for multiple proteins with node/edge statistics
- `get_functional_enrichment` -- Perform GO, KEGG, Reactome enrichment on a protein set
- `get_protein_annotations` -- Get STRING annotations and functional information
- `find_homologs` -- Find homologous proteins across species
- `search_proteins` -- Search for proteins by name or identifier

### Key Parameters

| Parameter | Used With | Description |
|-----------|-----------|-------------|
| `method` | All | Required. One of the 6 methods above |
| `protein_id` | `get_protein_interactions`, `find_homologs` | Single protein identifier (gene name, UniProt ID, or STRING ID) |
| `protein_ids` | `get_interaction_network`, `get_functional_enrichment`, `get_protein_annotations` | Array of protein identifiers |
| `query` | `search_proteins` | Search term (protein name, gene name, identifier) |
| `species` | All | Species name or NCBI taxonomy ID (default: 9606 for human) |
| `limit` | `get_protein_interactions` (1-2000), `search_proteins` (1-100) | Max results (default: 10) |
| `required_score` | `get_protein_interactions`, `get_interaction_network` | Min confidence score 0-1000 (default: 400) |
| `network_type` | `get_interaction_network` | `functional` or `physical` (default: functional) |
| `add_nodes` | `get_interaction_network` | Additional interactors to add 0-100 (default: 0) |
| `background_string_identifiers` | `get_functional_enrichment` | Background protein set for enrichment |
| `target_species` | `find_homologs` | Array of target species for homolog search |

### Confidence Score Guide

| Score Range | Confidence Level |
|-------------|-----------------|
| 900-1000 | Highest confidence |
| 700-899 | High confidence |
| 400-699 | Medium confidence |
| 150-399 | Low confidence |

### Evidence Types

Each interaction has individual evidence channel scores:
- **experimental** -- Lab-verified interactions (co-IP, Y2H, etc.)
- **database** -- Curated pathway databases (KEGG, Reactome, BioCyc)
- **textmining** -- Co-mentioned in PubMed abstracts
- **coexpression** -- Correlated expression across conditions
- **neighborhood** -- Genomic proximity (prokaryotes)
- **fusion** -- Gene fusion events
- **cooccurrence** -- Phylogenetic co-occurrence

### Example Calls

```
# Get interaction partners for TP53
mcp__stringdb__stringdb_data(method: "get_protein_interactions", protein_id: "TP53", species: "9606", limit: 20, required_score: 700)

# Build network for cancer pathway proteins
mcp__stringdb__stringdb_data(method: "get_interaction_network", protein_ids: ["TP53", "BRCA1", "EGFR", "KRAS", "MYC"], species: "9606", required_score: 400, add_nodes: 5)

# Functional enrichment of a gene set
mcp__stringdb__stringdb_data(method: "get_functional_enrichment", protein_ids: ["TP53", "BRCA1", "BRCA2", "ATM", "CHEK2", "RAD51"], species: "9606")

# Get annotations for proteins
mcp__stringdb__stringdb_data(method: "get_protein_annotations", protein_ids: ["TP53", "MDM2", "CDKN2A"], species: "9606")

# Find homologs in mouse
mcp__stringdb__stringdb_data(method: "find_homologs", protein_id: "TP53", species: "9606", target_species: ["10090"])

# Search for a protein
mcp__stringdb__stringdb_data(method: "search_proteins", query: "insulin receptor", species: "9606", limit: 5)
```

---

## Common Workflows

### Interaction Discovery

To map the interaction landscape of a protein:

1. `get_protein_interactions` with high confidence (700+) -- find top partners
2. `get_interaction_network` with the key interactors -- build the subnetwork
3. `get_functional_enrichment` on the network -- identify enriched pathways

### Pathway-Level Network Analysis

To analyze a pathway or gene set:

1. `get_interaction_network` with all pathway members -- map connections
2. `get_functional_enrichment` -- validate pathway membership and discover new associations
3. `get_protein_annotations` -- get functional descriptions for all members

### Cross-Species Conservation

To assess conservation of an interaction:

1. `get_protein_interactions` in source species -- identify partners
2. `find_homologs` for the query protein -- find orthologs
3. `get_protein_interactions` for orthologs in target species -- compare networks

### Hub Protein Identification

To find hub proteins in a network:

1. `get_interaction_network` with `add_nodes: 10` -- expand the network
2. Look for proteins with highest degree (most edges)
3. `get_functional_enrichment` on hub proteins -- characterize functions

---

## Cross-Reference with Other Skills

- Use `mcp__uniprot__uniprot_data` for detailed protein info on STRING results
- Use `mcp__ensembl__ensembl_data` for genomic context of interacting genes
- Use `mcp__opentargets__opentargets_info` for disease associations of network members
- Use `mcp__chembl__chembl_info` for drug data on identified targets
- Use `mcp__pubmed__pubmed_articles` for literature on protein interactions

## Completeness Checklist
- [ ] Protein identifiers resolved and species confirmed
- [ ] Interaction partners retrieved at appropriate confidence threshold
- [ ] Interaction network built with edge statistics summarized
- [ ] Evidence types analyzed (experimental, database, textmining, coexpression)
- [ ] Functional enrichment performed (GO, KEGG, Reactome)
- [ ] Hub proteins identified and characterized
- [ ] Cross-species conservation assessed where relevant
- [ ] Network findings cross-referenced with disease associations
- [ ] Key interactions validated against literature evidence
