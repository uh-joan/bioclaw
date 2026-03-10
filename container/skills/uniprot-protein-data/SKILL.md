---
name: uniprot-protein-data
description: UniProt protein data specialist. Search proteins, get details, sequences, features, domains, variants, pathways, interactions, homologs, orthologs, cross-references, literature, and taxonomy. Use when user mentions UniProt, protein accession, protein search, amino acid sequence, protein domains, protein structure PDB, protein variants, protein pathways, protein interactions, GO terms, subcellular localization, or protein comparison.
---

# UniProt Protein Data Specialist

Protein data retrieval and analysis via the UniProt REST API. Uses the `mcp__uniprot__uniprot_data` tool for all queries.

## Report-First Workflow

1. **Create report file immediately**: `protein_uniprot_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Disease-target association scoring and druggability assessment -> use `drug-target-analyst`
- Comprehensive multi-database target profiling (9 research paths) -> use `target-research`
- 3D protein structure retrieval and AlphaFold models -> use `protein-structure-retrieval` or `alphafold-structures`
- Protein-protein interaction network analysis -> use `protein-interactions`
- Variant pathogenicity classification (ACMG/AMP) -> use `variant-interpretation`
- Protein therapeutic design and antibody engineering -> use `protein-therapeutic-design` or `antibody-engineering`

## Available MCP Tool: `mcp__uniprot__uniprot_data`

All UniProt data queries go through this single tool. Always use it instead of web searches for UniProt data.

### Methods

**Core Search & Info:**
- `search_proteins` -- Search UniProt by name, keyword, or organism
- `get_protein_info` -- Full protein details by accession
- `search_by_gene` -- Find proteins by gene name/symbol
- `get_protein_sequence` -- FASTA or JSON sequence retrieval
- `get_protein_features` -- Domains, active sites, binding sites, keywords

**Comparative & Evolutionary:**
- `compare_proteins` -- Side-by-side comparison of 2-10 proteins
- `get_protein_homologs` -- Find homologous proteins across species
- `get_protein_orthologs` -- Identify orthologs by gene name
- `get_phylogenetic_info` -- Taxonomic lineage and evolutionary data

**Structure & Function:**
- `get_protein_structure` -- 3D structure info (PDB references, secondary structure)
- `get_protein_domains_detailed` -- InterPro, Pfam, SMART domain annotations
- `get_protein_variants` -- Disease-associated variants and mutations
- `analyze_sequence_composition` -- Amino acid composition, hydrophobicity

**Biological Context:**
- `get_protein_pathways` -- KEGG, Reactome pathway associations
- `get_protein_interactions` -- STRING, IntAct interaction networks
- `search_by_function` -- Search by GO terms or functional annotations
- `search_by_localization` -- Find proteins by subcellular location

**Batch & Advanced Search:**
- `batch_protein_lookup` -- Process up to 100 accessions
- `advanced_search` -- Multi-filter queries (length, mass, organism, keywords)
- `search_by_taxonomy` -- Search by NCBI taxonomy ID or name

**Cross-References & Literature:**
- `get_external_references` -- Links to PDB, EMBL, RefSeq, Ensembl, GO
- `get_literature_references` -- Associated publications and PubMed links
- `get_annotation_confidence` -- Entry type, existence evidence, annotation score

**Export & Utility:**
- `export_protein_data` -- Export in GFF, GenBank, EMBL, XML formats
- `validate_accession` -- Check if accession is valid and exists
- `get_taxonomy_info` -- Organism taxonomy and lineage

### Key Parameters

| Parameter | Used With | Description |
|-----------|-----------|-------------|
| `method` | All | Required. One of the 26 methods above |
| `accession` | Most methods | UniProt accession number (e.g., P04637) |
| `query` | `search_proteins`, `advanced_search` | Search query string |
| `gene` | `search_by_gene` | Gene name or symbol (e.g., BRCA1, TP53) |
| `organism` | Search methods | Organism name or taxonomy ID |
| `size` | Search methods | Number of results 1-500 (default: 25) |
| `format` | Various | Output format (json, tsv, fasta, xml, gff, genbank, embl) |
| `accessions` | `compare_proteins` (2-10), `batch_protein_lookup` (1-100) | Array of accessions |
| `goTerm` | `search_by_function` | GO term (e.g., GO:0005524) |
| `function` | `search_by_function` | Functional description or keyword |
| `localization` | `search_by_localization` | Subcellular location (e.g., nucleus) |
| `minLength` / `maxLength` | `advanced_search` | Sequence length range |
| `minMass` / `maxMass` | `advanced_search` | Molecular mass range (Da) |
| `keywords` | `advanced_search` | Array of keywords to filter |
| `taxonomyId` | `search_by_taxonomy` | NCBI taxonomy ID |
| `taxonomyName` | `search_by_taxonomy` | Taxonomic name (e.g., Mammalia) |

### Example Calls

```
# Search for a protein
mcp__uniprot__uniprot_data(method: "search_proteins", query: "insulin", organism: "Homo sapiens", size: 10)

# Get full protein info
mcp__uniprot__uniprot_data(method: "get_protein_info", accession: "P04637")

# Search by gene name
mcp__uniprot__uniprot_data(method: "search_by_gene", gene: "BRCA1", organism: "Homo sapiens")

# Get protein sequence in FASTA
mcp__uniprot__uniprot_data(method: "get_protein_sequence", accession: "P04637", format: "fasta")

# Get features and domains
mcp__uniprot__uniprot_data(method: "get_protein_features", accession: "P04637")

# Compare multiple proteins
mcp__uniprot__uniprot_data(method: "compare_proteins", accessions: ["P04637", "P04626", "P38398"])

# Find homologs
mcp__uniprot__uniprot_data(method: "get_protein_homologs", accession: "P04637", organism: "Mus musculus")

# Find orthologs
mcp__uniprot__uniprot_data(method: "get_protein_orthologs", accession: "P04637")

# Get 3D structure info
mcp__uniprot__uniprot_data(method: "get_protein_structure", accession: "P04637")

# Detailed domain analysis
mcp__uniprot__uniprot_data(method: "get_protein_domains_detailed", accession: "P04637")

# Get disease variants
mcp__uniprot__uniprot_data(method: "get_protein_variants", accession: "P04637")

# Analyze sequence composition
mcp__uniprot__uniprot_data(method: "analyze_sequence_composition", accession: "P04637")

# Get pathway associations
mcp__uniprot__uniprot_data(method: "get_protein_pathways", accession: "P04637")

# Get interactions
mcp__uniprot__uniprot_data(method: "get_protein_interactions", accession: "P04637")

# Search by GO term
mcp__uniprot__uniprot_data(method: "search_by_function", goTerm: "GO:0005524", organism: "Homo sapiens", size: 10)

# Search by localization
mcp__uniprot__uniprot_data(method: "search_by_localization", localization: "mitochondria", organism: "Homo sapiens")

# Batch lookup
mcp__uniprot__uniprot_data(method: "batch_protein_lookup", accessions: ["P04637", "P04626", "P38398", "P00533"])

# Advanced search with filters
mcp__uniprot__uniprot_data(method: "advanced_search", query: "kinase", organism: "Homo sapiens", minLength: 200, maxLength: 500, keywords: ["Phosphorylation"])

# Search by taxonomy
mcp__uniprot__uniprot_data(method: "search_by_taxonomy", taxonomyName: "Mammalia", size: 10)

# Get cross-references
mcp__uniprot__uniprot_data(method: "get_external_references", accession: "P04637")

# Get literature
mcp__uniprot__uniprot_data(method: "get_literature_references", accession: "P04637")

# Check annotation confidence
mcp__uniprot__uniprot_data(method: "get_annotation_confidence", accession: "P04637")

# Export in GFF format
mcp__uniprot__uniprot_data(method: "export_protein_data", accession: "P04637", format: "gff")

# Validate accession
mcp__uniprot__uniprot_data(method: "validate_accession", accession: "P04637")

# Get taxonomy info
mcp__uniprot__uniprot_data(method: "get_taxonomy_info", accession: "P04637")
```

---

## Common Workflows

### Protein Characterization

To fully characterize a protein:

1. `get_protein_info` -- get full details
2. `get_protein_features` -- domains, active sites, binding sites
3. `get_protein_structure` -- PDB structures
4. `get_protein_pathways` -- biological pathways
5. `get_protein_interactions` -- interaction partners
6. `get_external_references` -- cross-database links

### Disease Variant Analysis

To investigate disease-associated variants:

1. `get_protein_info` -- baseline protein data
2. `get_protein_variants` -- all known variants and mutations
3. `get_protein_domains_detailed` -- map variants to domains
4. `get_literature_references` -- supporting publications

### Comparative Proteomics

To compare proteins across species:

1. `search_by_gene` -- find protein in target organism
2. `get_protein_orthologs` -- identify orthologs
3. `compare_proteins` -- side-by-side comparison
4. `get_phylogenetic_info` -- evolutionary context
5. `analyze_sequence_composition` -- composition differences

### Drug Target Assessment

To assess a protein as a drug target:

1. `get_protein_info` -- full annotation
2. `get_protein_domains_detailed` -- druggable domains
3. `get_protein_structure` -- structural data for docking
4. `get_protein_variants` -- resistance/sensitivity variants
5. `get_protein_pathways` -- pathway context
6. `get_annotation_confidence` -- confidence in annotations

---

## Cross-Reference with Other Skills

- Use `mcp__ensembl__ensembl_data` for genomic context of UniProt genes
- Use `mcp__opentargets__opentargets_info` for disease associations
- Use `mcp__chembl__chembl_info` for drug activity data on protein targets
- Use `mcp__pubmed__pubmed_articles` for literature on proteins
- Use `mcp__drugbank__drugbank_info` for drug-protein interaction data

## Completeness Checklist

- [ ] Protein accession validated and confirmed as reviewed (Swiss-Prot) entry
- [ ] Full protein info retrieved (function, subcellular location, tissue specificity)
- [ ] Domain architecture documented (InterPro, Pfam, SMART annotations)
- [ ] Disease-associated variants cataloged with clinical significance
- [ ] Pathway associations retrieved (KEGG, Reactome)
- [ ] Protein-protein interactions listed (STRING, IntAct)
- [ ] Cross-references to external databases collected (PDB, Ensembl, RefSeq)
- [ ] Sequence composition and key features (active sites, binding sites, PTMs) documented
- [ ] Ortholog/homolog analysis completed if comparative context requested
- [ ] No `[Analyzing...]` placeholders remain in the report
