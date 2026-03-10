---
name: alphafold-structures
description: AlphaFold protein structure prediction database specialist. Get predicted 3D structures, confidence scores, pLDDT analysis, batch operations, structure comparison, and visualization exports. Use when user mentions AlphaFold, protein structure prediction, pLDDT, predicted aligned error, protein folding, structural analysis, or 3D structure.
---

# AlphaFold Structure Specialist

Predicted protein structure data via the AlphaFold Protein Structure Database API (EBI). Uses the `mcp__alphafold__alphafold_data` tool for all queries.

## Report-First Workflow

1. **Create report file immediately**: `[protein]_alphafold_structure_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Experimental (X-ray/cryo-EM) structure retrieval and analysis -> use `pdb-structures`
- Protein sequence, function, and annotation lookups -> use `uniprot-protein-data`
- Protein-protein interaction networks -> use `protein-interactions` or `stringdb-interactions`
- Protein therapeutic design and scaffold engineering -> use `protein-therapeutic-design`
- Variant effect interpretation on protein structure -> use `variant-interpretation`

## Available MCP Tool: `mcp__alphafold__alphafold_data`

All AlphaFold queries go through this single tool. Always use it instead of web searches for AlphaFold data.

### Methods

- `get_structure` -- Get predicted structure for a UniProt accession
- `download_structure` -- Download structure in PDB or mmCIF format
- `check_availability` -- Check if AlphaFold has a prediction for a protein
- `search_structures` -- Search available structures by organism or keyword
- `list_by_organism` -- List all predictions for a given organism
- `get_organism_stats` -- Get prediction statistics for an organism
- `get_confidence_scores` -- Get per-residue pLDDT confidence scores
- `analyze_confidence_regions` -- Analyze structure into high/medium/low confidence regions
- `get_prediction_metadata` -- Get metadata (version, date, source) for a prediction
- `batch_structure_info` -- Get structure info for multiple UniProt accessions
- `batch_download` -- Download structures for multiple accessions
- `batch_confidence_analysis` -- Analyze confidence for multiple proteins
- `compare_structures` -- Compare confidence profiles between two proteins
- `find_similar_structures` -- Find structures with similar confidence patterns
- `get_coverage_info` -- Get residue coverage information for a prediction
- `validate_structure_quality` -- Assess overall quality of a predicted structure
- `export_for_pymol` -- Generate PyMOL visualization commands
- `export_for_chimerax` -- Generate ChimeraX visualization commands
- `get_api_status` -- Check AlphaFold API health

### Key Parameters

| Parameter | Used With | Description |
|-----------|-----------|-------------|
| `method` | All | Required. One of the methods above |
| `uniprot_id` | Most methods | UniProt accession (e.g., P04637, Q9Y6K9) |
| `uniprot_ids` | Batch methods | Array of UniProt accessions |
| `format` | `download_structure`, `batch_download` | pdb or mmcif (default: pdb) |
| `organism` | `search_structures`, `list_by_organism`, `get_organism_stats` | Organism scientific name or taxonomy ID |
| `query` | `search_structures` | Search keyword |
| `limit` | Various | Max results to return |
| `threshold` | `analyze_confidence_regions` | pLDDT threshold for region classification |
| `color_scheme` | `export_for_pymol`, `export_for_chimerax` | confidence, rainbow, or chain |

### pLDDT Confidence Score Ranges

- **Very high (>90)**: High confidence, suitable for atomic-level analysis
- **Confident (70-90)**: Good backbone prediction
- **Low (50-70)**: Caution needed, may be disordered
- **Very low (<50)**: Likely disordered or uncertain

### Example Calls

```
# Get structure for TP53
mcp__alphafold__alphafold_data(method: "get_structure", uniprot_id: "P04637")

# Analyze confidence regions
mcp__alphafold__alphafold_data(method: "analyze_confidence_regions", uniprot_id: "P04637")

# Compare two protein structures
mcp__alphafold__alphafold_data(method: "compare_structures", uniprot_ids: ["P04637", "P38398"])

# Export for PyMOL visualization
mcp__alphafold__alphafold_data(method: "export_for_pymol", uniprot_id: "P04637", color_scheme: "confidence")

# Batch analysis
mcp__alphafold__alphafold_data(method: "batch_confidence_analysis", uniprot_ids: ["P04637", "P38398", "Q9Y6K9"])
```

---

## Common Workflows

### Protein Structure Assessment

Evaluate a predicted structure:

1. `get_structure` -- get basic structure info
2. `get_confidence_scores` -- get per-residue pLDDT
3. `analyze_confidence_regions` -- identify reliable vs unreliable regions
4. `validate_structure_quality` -- overall quality assessment

### Multi-Protein Comparison

Compare predicted structures:

1. `batch_structure_info` -- get info for all proteins
2. `batch_confidence_analysis` -- compare confidence profiles
3. `compare_structures` -- pairwise comparison

### Structure Visualization Prep

Prepare structures for molecular viewers:

1. `download_structure` -- get PDB/mmCIF file
2. `export_for_pymol` or `export_for_chimerax` -- generate visualization scripts
3. `analyze_confidence_regions` -- identify regions to highlight

---

## Cross-Reference with Other Skills

- Use `mcp__uniprot__uniprot_data` to get UniProt accessions for gene names
- Use `mcp__pdb__pdb_data` for experimental (X-ray/cryo-EM) structures
- Use `mcp__stringdb__stringdb_data` for protein interaction context
- Use `mcp__ensembl__ensembl_data` for gene/transcript mapping
- Use `mcp__reactome__reactome_data` for pathway context of the protein

## Completeness Checklist

- [ ] Report file created with all section headers and placeholders populated
- [ ] UniProt accession confirmed for the target protein
- [ ] AlphaFold structure availability checked
- [ ] Per-residue pLDDT confidence scores retrieved and interpreted
- [ ] Confidence regions analyzed (very high / confident / low / very low)
- [ ] Structure quality validated with overall assessment
- [ ] Disordered or low-confidence regions identified and noted
- [ ] Comparison with experimental PDB structures performed (if available)
- [ ] Visualization commands generated (PyMOL or ChimeraX) if requested
