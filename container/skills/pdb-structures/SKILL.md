---
name: pdb-structures
description: Protein Data Bank (PDB) experimental structure specialist. Search and retrieve experimentally determined protein structures (X-ray, cryo-EM, NMR), quality metrics, and structure files. Use when user mentions PDB, crystal structure, cryo-EM structure, X-ray crystallography, experimental protein structure, resolution, or R-factor.
---

# PDB Structure Specialist

Experimentally determined protein structure data via the RCSB PDB APIs. Uses the `mcp__pdb__pdb_data` tool for all queries.

## Report-First Workflow

1. **Create report file immediately**: `[protein]_pdb-structures_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Predicted protein structures (no experimental data available) → use `alphafold-structures`
- Protein sequence annotation, function, and pathway context → use `uniprot-protein-data`
- Protein-protein interaction networks → use `protein-interactions`
- Protein therapeutic design (antibody engineering, biologics) → use `protein-therapeutic-design`
- Structural variant analysis in genomic context → use `structural-variant-analysis`

## Available MCP Tool: `mcp__pdb__pdb_data`

All PDB queries go through this single tool. Always use it instead of web searches for PDB structure data.

### Methods

- `search_structures` -- Full-text search across PDB entries
- `get_structure_info` -- Get detailed info for a specific PDB entry
- `download_structure` -- Download structure coordinates (PDB/mmCIF/FASTA)
- `search_by_uniprot` -- Find PDB structures for a UniProt accession
- `get_structure_quality` -- Get quality metrics (resolution, R-factor, clashscore)

### Key Parameters

| Parameter | Used With | Description |
|-----------|-----------|-------------|
| `method` | All | Required. One of the 5 methods above |
| `query` | `search_structures` | Search text (protein name, organism, ligand, etc.) |
| `pdb_id` | `get_structure_info`, `download_structure`, `get_structure_quality` | 4-character PDB ID (e.g., 1TUP, 6LU7) |
| `uniprot_id` | `search_by_uniprot` | UniProt accession (e.g., P04637) |
| `format` | `download_structure` | pdb, mmcif, or fasta (default: pdb) |
| `rows` | `search_structures` | Max results 1-100 (default: 10) |

### PDB ID Format

PDB IDs are 4-character alphanumeric codes (e.g., `1TUP`, `6LU7`, `7BV2`).

### Example Calls

```
# Search for TP53 structures
mcp__pdb__pdb_data(method: "search_structures", query: "TP53 human", rows: 10)

# Get info for a specific structure
mcp__pdb__pdb_data(method: "get_structure_info", pdb_id: "1TUP")

# Download structure file
mcp__pdb__pdb_data(method: "download_structure", pdb_id: "1TUP", format: "pdb")

# Find structures by UniProt accession
mcp__pdb__pdb_data(method: "search_by_uniprot", uniprot_id: "P04637")

# Check structure quality
mcp__pdb__pdb_data(method: "get_structure_quality", pdb_id: "1TUP")
```

---

## Common Workflows

### Structure Quality Assessment

Evaluate experimental structure reliability:

1. `get_structure_info` -- get resolution, method, release date
2. `get_structure_quality` -- get R-factor, clashscore, Ramachandran stats

### Gene-to-Structure Mapping

Find experimental structures for a protein:

1. Use `mcp__uniprot__uniprot_data` to get UniProt accession
2. `search_by_uniprot` -- find all PDB entries
3. `get_structure_quality` for top hits -- pick best resolution

### Experimental vs Predicted Comparison

Compare PDB (experimental) with AlphaFold (predicted):

1. `search_by_uniprot` -- find experimental structures
2. Use `mcp__alphafold__alphafold_data` `get_structure` -- get predicted structure
3. Compare coverage and confidence

---

## Cross-Reference with Other Skills

- Use `mcp__alphafold__alphafold_data` for predicted structures (when no experimental structure exists)
- Use `mcp__uniprot__uniprot_data` for protein annotations and UniProt accessions
- Use `mcp__stringdb__stringdb_data` for protein interaction context
- Use `mcp__reactome__reactome_data` for pathway context
- Use `mcp__pubmed__pubmed_articles` for publications citing a PDB structure

## Completeness Checklist

- [ ] Protein target resolved to UniProt accession for cross-referencing
- [ ] PDB search performed with relevant keywords and organism filters
- [ ] Structure quality assessed (resolution, R-factor, clashscore, Ramachandran)
- [ ] Best-resolution structure selected and justified
- [ ] Experimental method noted (X-ray, cryo-EM, NMR) with method-specific quality metrics
- [ ] Ligand and binding site information extracted where applicable
- [ ] AlphaFold predicted structure compared for coverage gaps
- [ ] Report file verified: no `[Analyzing...]` placeholders remain
