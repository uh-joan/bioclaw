---
name: kegg-database
description: KEGG database specialist. Search and retrieve pathways, genes, compounds, reactions, enzymes, diseases, drugs, modules, orthologs, glycans, and BRITE hierarchies. Use when user mentions KEGG, metabolic pathways, KEGG pathways, KEGG compounds, EC numbers, KEGG orthologs, KEGG modules, drug-drug interactions, BRITE, or biological pathway databases.
---

# KEGG Database Specialist

Comprehensive access to the KEGG (Kyoto Encyclopedia of Genes and Genomes) database via the KEGG REST API. Uses the `mcp__kegg__kegg_data` tool for all queries.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_kegg-database_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Curated human pathway analysis with reaction-level detail -> use `reactome-pathways`
- Protein-protein interaction networks and STRING scores -> use `stringdb-interactions`
- Genomic coordinates, gene models, and variant annotation -> use `ensembl-genomics`
- Protein sequence and functional annotation -> use `uniprot-protein-data`
- Drug target associations and disease evidence scoring -> use `drug-target-analyst`
- Metabolomics data processing (peak tables, statistics, visualization) -> use `metabolomics-analysis`

## Available MCP Tool: `mcp__kegg__kegg_data`

All KEGG queries go through this single tool. Always use it instead of web searches for KEGG data.

### Methods

#### Database & Organisms
- `get_database_info` -- Get release info and statistics for any KEGG database
- `list_organisms` -- Get all KEGG organisms with codes and names

#### Pathway Analysis
- `search_pathways` -- Search pathways by keywords
- `get_pathway_info` -- Get detailed pathway information
- `get_pathway_genes` -- Get all genes in a pathway
- `get_pathway_compounds` -- Get all compounds in a pathway
- `get_pathway_reactions` -- Get all reactions in a pathway

#### Gene Analysis
- `search_genes` -- Search genes by name/symbol
- `get_gene_info` -- Get detailed gene information with optional sequences
- `get_gene_orthologs` -- Find orthologous genes across organisms

#### Compound & Reaction Analysis
- `search_compounds` -- Search compounds by name, formula, or mass
- `get_compound_info` -- Get compound details
- `get_compound_reactions` -- Get reactions involving a compound
- `search_reactions` -- Search biochemical reactions
- `get_reaction_info` -- Get reaction details

#### Enzyme Analysis
- `search_enzymes` -- Search by EC number or name
- `get_enzyme_info` -- Get enzyme details

#### Disease & Drug Analysis
- `search_diseases` -- Search human diseases
- `get_disease_info` -- Get disease details
- `search_drugs` -- Search drugs
- `get_drug_info` -- Get drug details
- `get_drug_interactions` -- Find drug-drug interactions

#### Module & Orthology
- `search_modules` -- Search KEGG modules
- `get_module_info` -- Get module details
- `search_ko_entries` -- Search KEGG Orthology entries
- `get_ko_info` -- Get KO details

#### Glycan & BRITE
- `search_glycans` -- Search glycan structures
- `get_glycan_info` -- Get glycan details
- `search_brite` -- Search BRITE functional hierarchies
- `get_brite_info` -- Get BRITE entry details

#### Batch & Cross-Reference
- `batch_entry_lookup` -- Process multiple entries at once
- `convert_identifiers` -- Convert between KEGG and external database IDs
- `find_related_entries` -- Find cross-references between KEGG databases

### Key Parameters

| Parameter | Used With | Description |
|-----------|-----------|-------------|
| `method` | All | Required. One of the 33 methods above |
| `query` | All `search_*` methods | Search query string |
| `max_results` | All `search_*` methods | Max results 1-1000 (default: 50) |
| `organism_code` | `search_pathways`, `search_genes` | Organism code (e.g., hsa, mmu, eco) |
| `pathway_id` | `get_pathway_info`, `get_pathway_genes`, `get_pathway_compounds`, `get_pathway_reactions` | Pathway ID (e.g., hsa00010) |
| `gene_id` | `get_gene_info`, `get_gene_orthologs` | Gene ID (e.g., hsa:1956) |
| `compound_id` | `get_compound_info`, `get_compound_reactions` | Compound ID (e.g., C00002) |
| `reaction_id` | `get_reaction_info` | Reaction ID (e.g., R00001) |
| `ec_number` | `get_enzyme_info` | EC number (e.g., ec:1.1.1.1) |
| `disease_id` | `get_disease_info` | Disease ID (e.g., H00001) |
| `drug_id` | `get_drug_info` | Drug ID (e.g., D00001) |
| `drug_ids` | `get_drug_interactions` | Array of drug IDs (1-10) |
| `include_sequences` | `get_gene_info` | Include AA/NT sequences (boolean) |
| `target_organisms` | `get_gene_orthologs` | Target organism codes array |
| `search_type` | `search_compounds` | name, formula, exact_mass, mol_weight |
| `format` | `get_pathway_info`, `get_brite_info` | json, kgml, image, conf, htext |
| `entry_ids` | `batch_entry_lookup` | Entry IDs array (1-50) |
| `operation` | `batch_entry_lookup` | info, sequence, pathway, link |
| `source_db`, `target_db` | `convert_identifiers`, `find_related_entries` | Database names |

### KEGG ID Formats

| Type | Format | Example |
|------|--------|---------|
| Pathway | map/org + 5 digits | hsa00010, map00010 |
| Gene | org:number | hsa:1956 |
| Compound | C + 5 digits | C00002 |
| Reaction | R + 5 digits | R00001 |
| Enzyme | ec:x.x.x.x | ec:1.1.1.1 |
| Disease | H + 5 digits | H00001 |
| Drug | D + 5 digits | D00001 |
| Module | M + 5 digits | M00001 |
| KO | K + 5 digits | K00001 |
| Glycan | G + 5 digits | G00001 |

### Common Organism Codes

| Code | Organism |
|------|----------|
| hsa | Homo sapiens (human) |
| mmu | Mus musculus (mouse) |
| rno | Rattus norvegicus (rat) |
| dme | Drosophila melanogaster |
| sce | Saccharomyces cerevisiae |
| eco | Escherichia coli K-12 |

### Example Calls

```
# Search for glycolysis pathways in human
mcp__kegg__kegg_data(method: "search_pathways", query: "glycolysis", organism_code: "hsa")

# Get pathway details
mcp__kegg__kegg_data(method: "get_pathway_info", pathway_id: "hsa00010")

# Get genes in a pathway
mcp__kegg__kegg_data(method: "get_pathway_genes", pathway_id: "hsa00010")

# Search for a gene
mcp__kegg__kegg_data(method: "search_genes", query: "BRCA1", organism_code: "hsa")

# Get gene info with sequences
mcp__kegg__kegg_data(method: "get_gene_info", gene_id: "hsa:672", include_sequences: true)

# Search compounds by formula
mcp__kegg__kegg_data(method: "search_compounds", query: "C6H12O6", search_type: "formula")

# Get drug-drug interactions
mcp__kegg__kegg_data(method: "get_drug_interactions", drug_ids: ["D00001", "D00002"])

# Find gene orthologs in mouse
mcp__kegg__kegg_data(method: "get_gene_orthologs", gene_id: "hsa:1956", target_organisms: ["mmu"])

# Convert KEGG gene IDs to UniProt
mcp__kegg__kegg_data(method: "convert_identifiers", source_db: "hsa", target_db: "uniprot")

# Batch lookup multiple entries
mcp__kegg__kegg_data(method: "batch_entry_lookup", entry_ids: ["hsa:1956", "hsa:672", "hsa:7157"], operation: "info")
```

---

## Common Workflows

### Metabolic Pathway Analysis

1. `search_pathways` -- find relevant metabolic pathways
2. `get_pathway_info` -- get pathway details
3. `get_pathway_genes` + `get_pathway_compounds` -- list all components
4. `get_pathway_reactions` -- map the reaction steps

### Drug Target Investigation

1. `search_genes` -- find the target gene
2. `get_gene_info` -- understand gene function
3. `find_related_entries` (gene -> pathway) -- find associated pathways
4. `search_drugs` -- find drugs targeting this pathway
5. `get_drug_interactions` -- check for DDI

### Cross-Species Gene Analysis

1. `get_gene_info` -- get gene details
2. `get_gene_orthologs` with target species -- find orthologs
3. `batch_entry_lookup` on orthologs -- compare gene details
4. `convert_identifiers` -- map to external databases

### Compound-Centric Analysis

1. `search_compounds` -- find the compound
2. `get_compound_info` -- get details (formula, mass, structure)
3. `get_compound_reactions` -- find reactions involving it
4. `find_related_entries` (compound -> pathway) -- find associated pathways

---

## Cross-Reference with Other Skills

- Use `mcp__reactome__reactome_data` for complementary curated pathway data
- Use `mcp__ensembl__ensembl_data` for genomic details of KEGG genes
- Use `mcp__uniprot__uniprot_data` for protein details
- Use `mcp__stringdb__stringdb_data` for protein interaction networks
- Use `mcp__chembl__chembl_info` for bioactivity data on KEGG compounds
- Use `mcp__opentargets__opentargets_info` for disease-target associations
- Use `mcp__pubmed__pubmed_articles` for literature on pathways and genes

## Completeness Checklist

- [ ] Subject disambiguated with canonical KEGG IDs (pathway, gene, compound, drug)
- [ ] Organism code specified for species-specific queries (e.g., hsa, mmu, eco)
- [ ] Cross-references to external databases resolved (UniProt, PubChem, ChEBI)
- [ ] Pathway components fully enumerated (genes, compounds, reactions)
- [ ] Batch lookups used for multi-entry queries instead of sequential calls
- [ ] KEGG ID formats validated before queries (correct prefix and digit count)
- [ ] Results synthesized into report sections, not raw tool output
- [ ] Related pathways and cross-database links documented for context
