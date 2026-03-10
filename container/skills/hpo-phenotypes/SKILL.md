---
name: hpo-phenotypes
description: Human Phenotype Ontology (HPO) specialist. Search phenotype terms, explore ontology hierarchy (ancestors, parents, children, descendants), validate IDs, compare phenotypes, and batch retrieve terms. Use when user mentions HPO, phenotype, clinical features, phenotypic abnormality, patient symptoms, rare disease phenotyping, or phenotype hierarchy.
---

# HPO Phenotype Specialist

Human phenotype vocabulary and hierarchy data via the HPO API (JAX). Uses the `mcp__hpo__hpo_data` tool for all queries.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_hpo-phenotypes_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Disease-target associations and drug evidence → use `disease-research`
- Rare disease differential diagnosis from phenotype profiles → use `rare-disease-diagnosis`
- Gene ontology and molecular function annotations → use `geneontology`
- Genomic variant interpretation for clinical phenotypes → use `variant-interpretation`
- Biomarker discovery from phenotypic data → use `biomarker-discovery`

## Available MCP Tool: `mcp__hpo__hpo_data`

All HPO queries go through this single tool. Always use it instead of web searches for HPO phenotype data.

### Methods

- `search_hpo_terms` -- Search phenotype terms by keyword, ID, or synonym
- `get_hpo_term` -- Get detailed info for a specific HPO term
- `get_all_hpo_terms` -- List HPO terms with pagination
- `get_hpo_ancestors` -- Get all ancestors of a term (up to root)
- `get_hpo_parents` -- Get direct parent terms
- `get_hpo_children` -- Get direct child terms
- `get_hpo_descendants` -- Get all descendants of a term
- `validate_hpo_id` -- Check if an HPO ID is valid and exists
- `get_hpo_term_path` -- Get full path from term to root
- `compare_hpo_terms` -- Find common ancestors between two terms
- `get_hpo_term_stats` -- Get hierarchy statistics for a term
- `batch_get_hpo_terms` -- Retrieve multiple HPO terms at once

### Key Parameters

| Parameter | Used With | Description |
|-----------|-----------|-------------|
| `method` | All | Required. One of the 12 methods above |
| `q` | `search_hpo_terms` | Search query (phenotype name, synonym, HP ID) |
| `id` | `get_hpo_term`, hierarchy methods, `validate_hpo_id`, `get_hpo_term_path`, `get_hpo_term_stats` | HPO term ID (e.g., HP:0001250) |
| `ids` | `batch_get_hpo_terms` | Array of HPO IDs |
| `id1`, `id2` | `compare_hpo_terms` | Two HPO IDs to compare |
| `max` | Most methods | Max results per page (default: 10-20) |
| `offset` | Most methods | Pagination offset |
| `category` | `search_hpo_terms` | Filter categories (e.g., terms, diseases, genes) |

### HPO ID Format

HPO identifiers follow the pattern `HP:NNNNNNN` (HP: followed by 7 digits), e.g., `HP:0001250` (Seizure).

### Example Calls

```
# Search for seizure-related phenotypes
mcp__hpo__hpo_data(method: "search_hpo_terms", q: "seizure", max: 10)

# Get details for a specific term
mcp__hpo__hpo_data(method: "get_hpo_term", id: "HP:0001250")

# Get children of a phenotype
mcp__hpo__hpo_data(method: "get_hpo_children", id: "HP:0001250")

# Compare two phenotypes
mcp__hpo__hpo_data(method: "compare_hpo_terms", id1: "HP:0001250", id2: "HP:0002069")

# Batch retrieve terms
mcp__hpo__hpo_data(method: "batch_get_hpo_terms", ids: ["HP:0001250", "HP:0002069", "HP:0001263"])
```

---

## Common Workflows

### Phenotype Characterization

Deep-dive into a clinical phenotype:

1. `search_hpo_terms` -- find the correct HPO term
2. `get_hpo_term` -- get definition, synonyms, cross-references
3. `get_hpo_children` -- explore more specific sub-phenotypes
4. `get_hpo_term_path` -- understand where it sits in the ontology

### Patient Phenotype Comparison

Compare phenotypic profiles:

1. `batch_get_hpo_terms` -- retrieve all patient phenotypes
2. `compare_hpo_terms` -- find common ancestors between phenotype pairs
3. `get_hpo_term_stats` -- understand specificity of each term

### Rare Disease Phenotyping

Map symptoms to HPO for diagnosis:

1. `search_hpo_terms` for each symptom -- find matching HPO terms
2. `get_hpo_ancestors` -- generalize phenotypes for broader matching
3. `get_hpo_descendants` -- find more specific sub-phenotypes

---

## Cross-Reference with Other Skills

- Use `mcp__opentargets__opentargets_info` for disease-phenotype associations
- Use `mcp__ensembl__ensembl_data` for genes associated with phenotypes
- Use `mcp__pubmed__pubmed_articles` for literature on clinical phenotypes
- Use `mcp__geneontology__go_data` for molecular function context of phenotype genes

## Completeness Checklist

- [ ] Correct HPO term IDs identified and validated for all phenotypes
- [ ] Ontology hierarchy explored (parents, children, ancestors) for each key term
- [ ] Cross-references to diseases and genes included where relevant
- [ ] Phenotype comparisons performed using common ancestor analysis
- [ ] Term specificity assessed (prefer most specific applicable term)
- [ ] Batch retrieval used for multi-phenotype profiles
- [ ] Synonyms and alternative names documented
- [ ] Report file created with all sections populated (no `[Analyzing...]` remaining)
