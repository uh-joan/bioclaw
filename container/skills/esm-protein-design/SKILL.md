---
name: esm-protein-design
description: "ESM protein language model specialist for structure prediction, sequence design, inverse folding, and variant effect scoring. Use when user mentions ESM, ESMFold, protein folding, inverse folding, protein generation, variant scoring, protein embeddings, ESM3, ESM-IF1, ESM C, or protein language model. Covers fold prediction, de novo sequence generation, conditional design, and mutation effect analysis via the ESM MCP server."
---

# ESM Protein Design

> **Code recipes**: See [recipes.md](recipes.md) for copy-paste executable code templates covering all ESM MCP operations.

ESM protein language model specialist for computational protein design, structure prediction, inverse folding, and variant effect scoring. Uses the ESM MCP server for GPU-accelerated inference — fold prediction, sequence generation, encoding/decoding, and log-likelihood scoring. Combines ESM capabilities with UniProt, PDB, AlphaFold, and PubMed for end-to-end protein engineering workflows.

## Report-First Workflow

1. **Create report file immediately**: `[protein]_esm_analysis_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## Cross-Reference: Other Skills

- **Full protein therapeutic design pipeline (RFdiffusion, ProteinMPNN, developability)** -> use protein-therapeutic-design skill
- **Antibody humanization, CDR engineering** -> use antibody-engineering skill
- **Small molecule binder discovery and ADMET** -> use binder-discovery-specialist skill
- **Protein structure retrieval and AlphaFold models** -> use protein-structure-retrieval skill
- **Enzyme kinetics and reaction data** -> use enzyme-kinetics skill
- **Cell type expression context** -> use cell-type-expression skill
- **Pharmacogenomics and drug-gene interactions** -> use pharmacogenomics-specialist skill (ClinPGx data)

## When NOT to Use This Skill

- Antibody CDR design or humanization → use `antibody-engineering`
- Small molecule hit-to-lead or ADMET → use `binder-discovery-specialist`
- Enzyme kinetics lookup (Km, kcat, inhibitors) → use `enzyme-kinetics`
- Cell type expression atlas queries → use `cell-type-expression`
- General protein structure retrieval → use `protein-structure-retrieval`

## Available MCP Tools

### `mcp__esm__esm_protein` (ESM Protein Language Model)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `fold` | Predict 3D structure from amino acid sequence | `sequence` |
| `inverse_fold` | Design sequences that fold into a target backbone | `coordinates`, `temperature` |
| `generate` | De novo protein sequence generation | `sequence`, `num_steps`, `temperature` |
| `encode` | Tokenize sequence into ESM token IDs | `sequence` |
| `decode` | Convert token IDs back to amino acid sequence | `tokens` |
| `logits` | Get per-position amino acid log-probabilities | `sequence` |
| `get_msa` | Retrieve multiple sequence alignment for a sequence | `sequence` |
| `forward_and_sample` | Forward pass with sampling for generative design | `sequence`, `temperature`, `return_embeddings`, `model` |

### `mcp__uniprot__uniprot_data` (Target Protein Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_proteins` | Search proteins by keyword | `query`, `organism`, `size` |
| `get_protein_info` | Full protein profile | `accession`, `format` |
| `get_protein_sequence` | Get protein sequence (FASTA/JSON) | `accession`, `format` |
| `get_protein_features` | Domain annotations, PTMs, sites | `accession` |
| `get_protein_structure` | Structural data (PDB IDs, AlphaFold) | `accession` |
| `get_protein_variants` | Known variants and mutations | `accession` |
| `analyze_sequence_composition` | Amino acid composition analysis | `accession` |

### `mcp__alphafold__alphafold_data` (Structure Validation)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_structure` | Get AlphaFold predicted structure | `uniprotId`, `format` |
| `get_confidence_scores` | Get pLDDT scores | `uniprotId` |
| `analyze_confidence_regions` | Identify high/low confidence regions | `uniprotId` |

### `mcp__pdb__pdb_data` (Experimental Structures)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_structures` | Search PDB for template structures | `query`, `limit` |
| `get_structure_info` | Structure details (resolution, chains) | `pdb_id`, `format` |
| `download_structure` | Download structure for design input | `pdb_id`, `format` |
| `search_by_uniprot` | Find PDB structures by UniProt ID | `uniprot_id`, `limit` |

### `mcp__pubmed__pubmed_articles` (Literature)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Keyword search | `keywords`, `num_results` |
| `search_advanced` | Filtered search with date range | `term`, `start_date`, `end_date`, `num_results` |

---

## Design Pipeline

### Phase 1: Target Characterization

Gather sequence, structure, and functional context for the protein of interest.

```
1. mcp__uniprot__uniprot_data(method: "search_by_gene", gene: "TARGET_GENE", organism: "human", size: 5)
   -> Get UniProt accession, confirm identity

2. mcp__uniprot__uniprot_data(method: "get_protein_sequence", accession: "UNIPROT_ACC", format: "fasta")
   -> Get canonical sequence for ESM input

3. mcp__uniprot__uniprot_data(method: "get_protein_features", accession: "UNIPROT_ACC")
   -> Domain architecture, active sites, PTMs

4. mcp__pdb__pdb_data(method: "search_by_uniprot", uniprot_id: "UNIPROT_ACC", limit: 5)
   -> Find experimental structures as design templates

5. mcp__alphafold__alphafold_data(method: "get_confidence_scores", uniprotId: "UNIPROT_ACC")
   -> pLDDT scores for identifying well-ordered regions
```

### Phase 2: ESM Structure Prediction

Predict 3D structure from sequence using the ESM MCP server.

```
1. mcp__esm__esm_protein(method: "fold", sequence: "FULL_SEQUENCE")
   -> ESMFold structure prediction — single-sequence, no MSA needed
   -> Returns PDB coordinates with per-residue confidence

2. Compare ESMFold result against AlphaFold prediction:
   mcp__alphafold__alphafold_data(method: "get_structure", uniprotId: "UNIPROT_ACC", format: "pdb")
   -> AlphaFold structure for comparison

DECISION GATE: If ESMFold pLDDT < 70 for the target region, flag low confidence.
ESMFold is faster but less accurate than AF2 for natural proteins.
ESMFold excels for designed proteins with no homologs.
```

### Phase 3: Inverse Folding (Structure → Sequence)

Design novel sequences that fold into a target backbone.

```
1. Obtain target backbone coordinates:
   mcp__pdb__pdb_data(method: "download_structure", pdb_id: "XXXX", format: "pdb")
   -> Get experimental backbone coordinates

2. mcp__esm__esm_protein(method: "inverse_fold", coordinates: BACKBONE_COORDS, temperature: 0.2)
   -> Design high-confidence sequence (T=0.2, conservative)

3. mcp__esm__esm_protein(method: "inverse_fold", coordinates: BACKBONE_COORDS, temperature: 0.5)
   -> Design diverse sequence (T=0.5, exploratory)

4. Validate: fold each designed sequence back
   mcp__esm__esm_protein(method: "fold", sequence: "DESIGNED_SEQUENCE")
   -> Self-consistency check: RMSD < 2 Å to original backbone = high confidence

Temperature guide:
  T=0.1: Most native-like, highest recovery rate
  T=0.2: Standard design, good balance
  T=0.5: Maximum diversity, validate carefully
```

### Phase 4: De Novo Sequence Generation

Generate novel proteins from scratch or with constraints.

```
1. Unconditional generation:
   mcp__esm__esm_protein(method: "generate", sequence: "____...____", num_steps: 100, temperature: 0.7)
   -> Fully de novo protein (underscores = masked positions)

2. Conditional generation (fixed active site):
   mcp__esm__esm_protein(method: "generate", sequence: "____H____D____S____", num_steps: 100, temperature: 0.5)
   -> Fixed residues (H, D, S) at specific positions, scaffold generated around them

3. Validate each generated sequence:
   mcp__esm__esm_protein(method: "fold", sequence: "GENERATED_SEQUENCE")
   -> Confirm it folds into a stable structure (pLDDT > 80)
```

### Phase 5: Variant Effect Scoring

Score mutations using ESM log-likelihood ratios.

```
1. Get wild-type log-probabilities:
   mcp__esm__esm_protein(method: "logits", sequence: "WILD_TYPE_SEQUENCE")
   -> Per-position amino acid probabilities

2. For each mutation, compare WT vs mutant probability:
   - Log-likelihood ratio = log P(mutant_aa | context) - log P(wt_aa | context)
   - Negative = deleterious, Positive = potentially beneficial, ~0 = neutral

3. mcp__esm__esm_protein(method: "forward_and_sample", sequence: "SEQUENCE", temperature: 0.01, return_embeddings: true)
   -> Get embeddings for detailed positional analysis

4. Cross-reference with known variants:
   mcp__uniprot__uniprot_data(method: "get_protein_variants", accession: "UNIPROT_ACC")
   -> Validate ESM predictions against known pathogenic/benign variants
```

### Phase 6: Protein Embeddings and Similarity

Extract embeddings for downstream ML or protein comparison.

```
1. mcp__esm__esm_protein(method: "forward_and_sample", sequence: "SEQUENCE_A", return_embeddings: true)
   -> Per-residue embeddings for protein A

2. mcp__esm__esm_protein(method: "forward_and_sample", sequence: "SEQUENCE_B", return_embeddings: true)
   -> Per-residue embeddings for protein B

3. Compute cosine similarity between mean-pooled embeddings
   -> >0.9 = very similar, 0.7-0.9 = related, <0.7 = distinct

Use cases:
  - Protein family clustering
  - Binding interface prediction
  - Active site residue classification
  - Fitness landscape mapping
```

---

## ESM Model Selection Guide

| Model | Parameters | Access | Best For |
|-------|-----------|--------|----------|
| **esm3_sm_open_v1** | 1.4B | Local (open weights) | Prototyping, screening, high-throughput |
| **esm3-medium** | 7B | Forge API | Production design, balanced quality/cost |
| **esm3-large** | 98B | Forge API | Novel fold generation, final candidates |
| **ESM C 300M** | 300M | Local | Embeddings, downstream ML, fast |
| **ESM C 600M** | 600M | Local | Better embeddings, 2x slower |

When using the MCP server, the `model` parameter in `forward_and_sample` selects which model to use.

---

## Quality Assessment Criteria

| Metric | Excellent | Good | Needs Redesign |
|--------|----------|------|---------------|
| **ESMFold pLDDT** | > 90 | 70-90 | < 70 |
| **Self-consistency RMSD** | < 1.0 Å | 1.0-2.0 Å | > 2.0 Å |
| **Inverse folding recovery** | > 50% | 30-50% | < 30% |
| **Variant LLR (deleterious)** | < -3.0 | -3.0 to -1.0 | > -1.0 |

---

## Multi-Agent Workflow Examples

**"Predict the structure of my designed protein and check stability"**
1. ESM Protein Design -> ESMFold structure prediction, per-residue confidence
2. Protein Therapeutic Design -> Developability scoring, aggregation check
3. Protein Structure Retrieval -> Compare against known structures

**"Design a new sequence for this enzyme scaffold"**
1. ESM Protein Design -> Inverse folding from PDB backbone, multiple temperatures
2. BRENDA Enzymes -> Get kinetic benchmarks for the enzyme class
3. Protein Therapeutic Design -> Sequence optimization, expression system selection

**"Score all possible mutations at position 42 of my protein"**
1. ESM Protein Design -> Log-likelihood scoring for all 19 substitutions
2. Variant Interpretation -> ACMG classification for clinically relevant variants
3. Drug Interaction Analyst -> Check if mutant affects drug binding

**"Compare my designed protein against natural homologs"**
1. ESM Protein Design -> Embeddings for designed protein
2. Protein Structure Retrieval -> Find natural homologs via UniProt
3. ESM Protein Design -> Embeddings for homologs, cosine similarity matrix

## Completeness Checklist

- [ ] Target protein characterized (sequence, structure, domains)
- [ ] ESMFold structure predicted with confidence assessment
- [ ] Design approach selected (inverse folding, de novo, conditional)
- [ ] Multiple designs generated at varying temperatures
- [ ] Self-consistency validation performed (fold designed sequences back)
- [ ] Variant effects scored where relevant
- [ ] Comparison against known structures or homologs included
- [ ] Report file finalized with no `[Analyzing...]` placeholders
