---
name: ensembl-genomics
description: Ensembl genomic data specialist. Access genes, transcripts, sequences, variants, homologs, regulatory features, cross-references, phylogenetic trees, and assembly information from the Ensembl REST API. Use when user mentions Ensembl, gene lookup, transcript structure, DNA sequence, genomic coordinates, variants, VEP, homologs, orthologs, paralogs, gene trees, regulatory elements, cross-references, assembly info, karyotype, or comparative genomics.
---

# Ensembl Genomics Specialist

Genomic data retrieval and analysis via the Ensembl REST API. Uses the `mcp__ensembl__ensembl_data` tool for all queries.

## Report-First Workflow

1. **Create report file immediately**: `[gene_or_region]_ensembl-genomics_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Disease-target association scoring and evidence → use `drug-target-analyst`
- Variant clinical interpretation (ACMG classification) → use `variant-interpretation`
- GWAS SNP analysis and trait associations → use `gwas-snp-interpretation`
- Gene expression across tissues (GTEx) → use `gtex-expression`
- Protein structure and druggability assessment → use `protein-structure-retrieval`
- Regulatory genomics and epigenetic analysis → use `regulatory-genomics`

## Available MCP Tool: `mcp__ensembl__ensembl_data`

All Ensembl data queries go through this single tool. Always use it instead of web searches for Ensembl data.

### Methods

**Gene & Transcript Information:**
- `lookup_gene` -- Get detailed gene information by stable ID or symbol
- `get_transcripts` -- Get all transcripts for a gene with structural details
- `search_genes` -- Search for genes by name, description, or identifier

**Sequence Data:**
- `get_sequence` -- Fetch DNA sequence for genomic coordinates or gene/transcript ID
- `get_cds_sequence` -- Get coding sequence (CDS) for a transcript
- `translate_sequence` -- Convert DNA sequence to protein sequence (local codon table)

**Comparative Genomics:**
- `get_homologs` -- Find orthologous genes across species
- `get_gene_tree` -- Get phylogenetic tree for gene family (Newick, PhyloXML)

**Variant Analysis:**
- `get_variants` -- Get genetic variants in a genomic region
- `get_variant_consequences` -- Predict variant effects on genes/transcripts (VEP)

**Regulatory Features:**
- `get_regulatory_features` -- Get enhancers, promoters, TFBS in a region
- `get_motif_features` -- Get transcription factor binding site motifs

**Cross-References & Annotations:**
- `get_xrefs` -- Get external database cross-references (PDB, EMBL, RefSeq)
- `map_coordinates` -- Convert coordinates between genome assemblies

**Species & Assembly:**
- `list_species` -- Get available organisms and builds
- `get_assembly_info` -- Get genome assembly statistics
- `get_karyotype` -- Get chromosome information and karyotype

**Batch Processing:**
- `batch_gene_lookup` -- Look up multiple genes simultaneously (max 200)
- `batch_sequence_fetch` -- Fetch sequences for multiple regions (max 50)

### Key Parameters

| Parameter | Used With | Description |
|-----------|-----------|-------------|
| `method` | All | Required. One of the 19 methods above |
| `gene_id` | `lookup_gene`, `get_transcripts`, `get_homologs`, `get_gene_tree`, `get_xrefs` | Ensembl gene ID or symbol (e.g., ENSG00000139618, BRCA2) |
| `query` | `search_genes` | Search term (gene name, description, partial match) |
| `region` | `get_sequence`, `get_variants`, `get_regulatory_features`, `get_motif_features`, `map_coordinates` | Genomic region (chr:start-end) or feature ID |
| `transcript_id` | `get_cds_sequence` | Ensembl transcript ID |
| `sequence` | `translate_sequence` | DNA sequence to translate |
| `species` | Most methods | Species name (default: homo_sapiens) |
| `format` | Various | Output format (json, fasta, gff, vcf, newick, phyloxml) |
| `expand` | `lookup_gene` | Include transcript/exon details (default: false) |
| `canonical_only` | `get_transcripts` | Return only canonical transcript (default: false) |
| `feature` | `search_genes` | Feature type: gene or transcript (default: gene) |
| `biotype` | `search_genes` | Filter by biotype (e.g., protein_coding, lncRNA) |
| `limit` | `search_genes` | Max results 1-200 (default: 25) |
| `target_species` | `get_homologs` | Target species for ortholog search |
| `target_assembly` | `map_coordinates` | Target assembly name |
| `variants` | `get_variant_consequences` | Array of variant IDs or HGVS notation |
| `gene_ids` | `batch_gene_lookup` | Array of gene IDs (max 200) |
| `regions` | `batch_sequence_fetch` | Array of regions or feature IDs (max 50) |

### Example Calls

```
# Look up a gene by Ensembl ID
mcp__ensembl__ensembl_data(method: "lookup_gene", gene_id: "ENSG00000139618", expand: true)

# Look up a gene by symbol
mcp__ensembl__ensembl_data(method: "lookup_gene", gene_id: "BRCA2")

# Search for genes
mcp__ensembl__ensembl_data(method: "search_genes", query: "BRCA", species: "homo_sapiens", limit: 10)

# Get transcripts for a gene
mcp__ensembl__ensembl_data(method: "get_transcripts", gene_id: "ENSG00000139618", canonical_only: true)

# Fetch DNA sequence by region
mcp__ensembl__ensembl_data(method: "get_sequence", region: "7:140424943-140624564", species: "homo_sapiens", format: "fasta")

# Get CDS for a transcript
mcp__ensembl__ensembl_data(method: "get_cds_sequence", transcript_id: "ENST00000380152")

# Translate DNA to protein
mcp__ensembl__ensembl_data(method: "translate_sequence", sequence: "ATGCGATCGATCG")

# Find orthologs
mcp__ensembl__ensembl_data(method: "get_homologs", gene_id: "ENSG00000139618", target_species: "mus_musculus")

# Get gene tree
mcp__ensembl__ensembl_data(method: "get_gene_tree", gene_id: "ENSG00000139618", format: "newick")

# Get variants in a region
mcp__ensembl__ensembl_data(method: "get_variants", region: "7:140424943-140425943", species: "homo_sapiens")

# Predict variant consequences (VEP)
mcp__ensembl__ensembl_data(method: "get_variant_consequences", variants: ["rs699"])

# Get regulatory features
mcp__ensembl__ensembl_data(method: "get_regulatory_features", region: "7:140424943-140625943")

# Get cross-references
mcp__ensembl__ensembl_data(method: "get_xrefs", gene_id: "ENSG00000139618", external_db: "PDB")

# Map coordinates between assemblies
mcp__ensembl__ensembl_data(method: "map_coordinates", region: "7:140424943-140624564", target_assembly: "GRCh37")

# List available species
mcp__ensembl__ensembl_data(method: "list_species", division: "vertebrates")

# Get assembly info
mcp__ensembl__ensembl_data(method: "get_assembly_info", species: "homo_sapiens", bands: true)

# Get karyotype
mcp__ensembl__ensembl_data(method: "get_karyotype", species: "homo_sapiens")

# Batch gene lookup
mcp__ensembl__ensembl_data(method: "batch_gene_lookup", gene_ids: ["ENSG00000139618", "ENSG00000141510"])

# Batch sequence fetch
mcp__ensembl__ensembl_data(method: "batch_sequence_fetch", regions: ["ENSG00000139618", "ENSG00000141510"], format: "fasta")
```

---

## Common Workflows

### Gene Characterization

To fully characterize a gene:

1. `lookup_gene` with `expand: true` -- get gene details with transcripts/exons
2. `get_xrefs` -- find external database links (UniProt, PDB, OMIM)
3. `get_homologs` -- check conservation across species
4. `get_sequence` -- retrieve the genomic sequence

### Variant Impact Assessment

To assess the impact of variants:

1. `get_variants` -- find variants in the region of interest
2. `get_variant_consequences` -- predict functional effects (VEP)
3. `get_regulatory_features` -- check if variants overlap regulatory elements
4. `lookup_gene` -- get context on affected genes

### Cross-Species Comparison

To compare genes across species:

1. `lookup_gene` -- get source gene information
2. `get_homologs` with different `target_species` -- find orthologs
3. `get_gene_tree` -- visualize evolutionary relationships
4. `batch_gene_lookup` -- compare multiple genes simultaneously

### Assembly Liftover

To convert coordinates between genome builds:

1. `get_assembly_info` -- verify source and target assemblies
2. `map_coordinates` -- perform the liftover
3. `get_sequence` -- verify the sequence at new coordinates

---

## Cross-Reference with Other Skills

- Use `mcp__opentargets__opentargets_info` for disease associations of Ensembl genes
- Use `mcp__pubmed__pubmed_articles` for literature on genes/variants found
- Use `mcp__chembl__chembl_info` for drug target data on identified proteins
- Use `mcp__drugbank__drugbank_info` for drug-gene interaction context

---

## Completeness Checklist

- [ ] Gene resolved to Ensembl stable ID with correct species
- [ ] Canonical transcript identified and structural details retrieved
- [ ] Cross-references obtained (UniProt, PDB, RefSeq, OMIM)
- [ ] Genomic sequence fetched for region of interest
- [ ] Variant consequences predicted via VEP where applicable
- [ ] Ortholog/homolog conservation assessed across relevant species
- [ ] Regulatory features checked for regions overlapping variants
- [ ] Assembly version confirmed and coordinates validated
- [ ] Batch queries used for multi-gene analyses (max 200 genes)
