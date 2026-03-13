---
name: enzyme-kinetics
description: "Enzyme kinetics and biochemistry specialist using the BRENDA database. Use when user asks about enzyme kinetics, Km values, kcat, catalytic efficiency, enzyme inhibitors, cofactors, substrate specificity, EC numbers, enzyme reactions, or metabolic enzymes. Covers kinetic parameter lookup, inhibitor profiling, organism comparison, and enzyme engineering context."
---

# BRENDA Enzymes

> **Code recipes**: See [recipes.md](recipes.md) for copy-paste executable workflows and analysis templates.

Enzyme kinetics and biochemistry specialist powered by the BRENDA database — the world's most comprehensive enzyme information system. Look up kinetic parameters (Km, kcat, kcat/Km), inhibitors, cofactors, substrates, and reaction details for any enzyme by EC number. Supports enzyme engineering, metabolic pathway analysis, and drug target characterization.

## Report-First Workflow

1. **Create report file immediately**: `[enzyme]_brenda_analysis_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## Cross-Reference: Other Skills

- **Protein therapeutic design for enzyme scaffolds** -> use protein-therapeutic-design skill
- **ESM structure prediction and sequence design for engineered enzymes** -> use esm-protein-design skill
- **Drug-target interactions and bioactivity data** -> use binder-discovery-specialist skill
- **Drug interaction analysis (CYP enzyme interactions)** -> use drug-interaction-analyst skill
- **Metabolomics and metabolite data** -> use HMDB MCP via relevant skill
- **Protein structure retrieval** -> use protein-structure-retrieval skill

## When NOT to Use This Skill

- Protein therapeutic design or binder engineering → use `protein-therapeutic-design`
- Drug-drug interactions via CYP enzymes → use `drug-interaction-analyst`
- Small molecule ADMET and medicinal chemistry → use `binder-discovery-specialist` or `medicinal-chemistry`
- Protein structure prediction → use `esm-protein-design` or `protein-structure-retrieval`

## Available MCP Tools

### `mcp__brenda__brenda_enzymes` (BRENDA Enzyme Database)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `get_km_value` | Michaelis constant (Km) for enzyme-substrate pairs | `ec_number`, `organism`, `substrate` |
| `get_kcat_value` | Turnover number (kcat) | `ec_number`, `organism`, `substrate` |
| `get_kcat_km_value` | Catalytic efficiency (kcat/Km) | `ec_number`, `organism`, `substrate` |
| `get_inhibitors` | Known enzyme inhibitors with Ki values | `ec_number`, `organism`, `inhibitor` |
| `get_cofactor` | Required cofactors and coenzymes | `ec_number`, `organism` |
| `get_ki_value` | Inhibition constant (Ki) for specific inhibitors | `ec_number`, `organism`, `inhibitor` |
| `search_by_substrate` | Find enzymes that act on a specific substrate | `substrate` |
| `get_enzyme_names` | Common and systematic enzyme names | `ec_number` |
| `get_organism` | Organisms in which the enzyme has been characterized | `ec_number` |
| `get_reaction` | Catalyzed reaction (substrates → products) | `ec_number` |

### `mcp__uniprot__uniprot_data` (Protein Sequence and Annotation)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_proteins` | Search proteins by keyword | `query`, `organism`, `size` |
| `get_protein_info` | Full protein profile | `accession`, `format` |
| `get_protein_sequence` | Get sequence for engineering | `accession`, `format` |
| `get_protein_features` | Active site, binding site, domain annotations | `accession` |

### `mcp__pubmed__pubmed_articles` (Literature)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Keyword search | `keywords`, `num_results` |
| `search_advanced` | Filtered search | `term`, `start_date`, `end_date`, `num_results` |

### `mcp__chembl__chembl_info` (Bioactivity Data)

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `target_search` | Search biological targets | `query`, `limit` |
| `get_bioactivity` | Compound-target activity data | `chembl_id`, `target_id`, `limit` |

---

## Analysis Pipeline

### Phase 1: Enzyme Identification

Confirm the enzyme identity and get its EC number.

```
1. mcp__brenda__brenda_enzymes(method: "get_enzyme_names", ec_number: "EC_NUMBER")
   -> Systematic and common names, synonyms

2. mcp__brenda__brenda_enzymes(method: "get_reaction", ec_number: "EC_NUMBER")
   -> Catalyzed reaction: substrates → products, reaction type

3. mcp__brenda__brenda_enzymes(method: "get_organism", ec_number: "EC_NUMBER")
   -> All organisms with characterized enzyme — identify best-studied sources

4. mcp__uniprot__uniprot_data(method: "search_proteins", query: "EC_NUMBER enzyme_name", organism: "human", size: 5)
   -> UniProt entries for cross-referencing sequence and annotation data

If EC number is unknown, use the enzyme name or substrate to find it:
   mcp__brenda__brenda_enzymes(method: "search_by_substrate", substrate: "SUBSTRATE_NAME")
   -> Find enzymes that act on the substrate of interest
```

### Phase 2: Kinetic Parameters

Collect Km, kcat, and catalytic efficiency data.

```
1. mcp__brenda__brenda_enzymes(method: "get_km_value", ec_number: "EC_NUMBER", organism: "Homo sapiens")
   -> Km values for human enzyme with all known substrates

2. mcp__brenda__brenda_enzymes(method: "get_kcat_value", ec_number: "EC_NUMBER", organism: "Homo sapiens")
   -> Turnover number for human enzyme

3. mcp__brenda__brenda_enzymes(method: "get_kcat_km_value", ec_number: "EC_NUMBER", organism: "Homo sapiens")
   -> Catalytic efficiency — the gold standard for comparing enzyme performance

4. For specific substrate of interest:
   mcp__brenda__brenda_enzymes(method: "get_km_value", ec_number: "EC_NUMBER", substrate: "SUBSTRATE_NAME")
   -> Km across all organisms for this substrate

ANALYSIS:
  - Km < 10 µM: very high affinity
  - Km 10-100 µM: moderate affinity
  - Km > 1 mM: low affinity
  - kcat/Km > 10^6 M⁻¹s⁻¹: near diffusion limit (catalytically perfect)
  - kcat/Km 10^3-10^6: efficient
  - kcat/Km < 10^3: slow, potential engineering target
```

### Phase 3: Inhibitor and Cofactor Profiling

```
1. mcp__brenda__brenda_enzymes(method: "get_inhibitors", ec_number: "EC_NUMBER")
   -> All known inhibitors — competitive, non-competitive, uncompetitive, irreversible

2. mcp__brenda__brenda_enzymes(method: "get_ki_value", ec_number: "EC_NUMBER", organism: "Homo sapiens")
   -> Ki values for quantitative inhibitor comparison

3. mcp__brenda__brenda_enzymes(method: "get_cofactor", ec_number: "EC_NUMBER")
   -> Required cofactors — metal ions, coenzymes (NAD+, FAD, PLP, etc.)

4. mcp__chembl__chembl_info(method: "target_search", query: "ENZYME_NAME", limit: 5)
   -> ChEMBL target ID for additional bioactivity data

5. mcp__chembl__chembl_info(method: "get_bioactivity", target_id: "CHEMBL_TARGET_ID", limit: 50)
   -> Published IC50, Ki, EC50 data from medicinal chemistry literature

ANALYSIS:
  - Ki < 1 nM: potent inhibitor (drug candidate)
  - Ki 1-100 nM: moderate inhibitor
  - Ki > 1 µM: weak inhibitor
  - Identify inhibitor mechanism (competitive vs allosteric) for drug design context
```

### Phase 4: Cross-Organism Comparison

Compare enzyme properties across species for engineering context.

```
1. For top organisms of interest (human, E. coli, yeast, thermophiles):
   mcp__brenda__brenda_enzymes(method: "get_km_value", ec_number: "EC_NUMBER", organism: "ORGANISM")
   mcp__brenda__brenda_enzymes(method: "get_kcat_value", ec_number: "EC_NUMBER", organism: "ORGANISM")

2. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "EC_NUMBER enzyme engineering thermostable directed evolution", num_results: 10)
   -> Published engineering efforts for this enzyme class
```

**Cross-Organism Comparison Table:**

| Organism | Km (µM) | kcat (s⁻¹) | kcat/Km (M⁻¹s⁻¹) | Notes |
|----------|---------|-----------|-------------------|-------|
| H. sapiens | — | — | — | Clinical relevance |
| E. coli | — | — | — | Expression host |
| T. thermophilus | — | — | — | Thermostability |

### Phase 5: Engineering Context

Synthesize kinetic data for enzyme engineering or drug design applications.

```
1. mcp__uniprot__uniprot_data(method: "get_protein_features", accession: "UNIPROT_ACC")
   -> Active site residues, binding site, catalytic mechanism

2. mcp__pubmed__pubmed_articles(method: "search_advanced", term: "EC_NUMBER directed evolution rational design", start_date: "2020-01-01", num_results: 15)
   -> Recent engineering successes and strategies

3. mcp__uniprot__uniprot_data(method: "get_protein_variants", accession: "UNIPROT_ACC")
   -> Known variants affecting activity — natural mutagenesis data
```

---

## Kinetic Parameter Reference

| Parameter | Symbol | Units | What it measures |
|-----------|--------|-------|-----------------|
| Michaelis constant | Km | µM, mM | Substrate affinity (lower = tighter binding) |
| Turnover number | kcat | s⁻¹ | Max catalytic rate per enzyme molecule |
| Catalytic efficiency | kcat/Km | M⁻¹s⁻¹ | Overall enzyme performance metric |
| Inhibition constant | Ki | nM, µM | Inhibitor potency (lower = more potent) |
| IC50 | IC50 | nM, µM | Concentration for 50% inhibition (assay-dependent) |

**Enzyme Performance Tiers:**

| Tier | kcat/Km (M⁻¹s⁻¹) | Examples |
|------|-------------------|---------|
| Catalytically perfect | > 10⁸ | Carbonic anhydrase, triosephosphate isomerase |
| Very efficient | 10⁶-10⁸ | Most metabolic enzymes |
| Efficient | 10⁴-10⁶ | Typical drug targets |
| Moderate | 10²-10⁴ | Engineered enzymes (before optimization) |
| Slow | < 10² | De novo designed enzymes |

---

## Multi-Agent Workflow Examples

**"What are the kinetic parameters of human CYP3A4?"**
1. BRENDA Enzymes -> Km, kcat for major substrates; inhibitors; cofactors
2. Drug Interaction Analyst -> Clinical DDI context for CYP3A4 inhibitors/inducers
3. Protein Structure Retrieval -> CYP3A4 active site structure

**"Engineer a more thermostable lipase"**
1. BRENDA Enzymes -> Compare kinetics across thermophilic organisms
2. ESM Protein Design -> Inverse folding from thermophilic variant backbone
3. Protein Therapeutic Design -> Developability scoring for engineered variants

**"Find inhibitors for this metabolic enzyme as drug candidates"**
1. BRENDA Enzymes -> Known inhibitors, Ki values, mechanism
2. Binder Discovery Specialist -> Expand with ChEMBL bioactivity, ADMET filtering
3. Medicinal Chemistry -> SAR analysis and lead optimization

**"What enzyme converts this substrate?"**
1. BRENDA Enzymes -> search_by_substrate to identify enzyme(s)
2. BRENDA Enzymes -> Full kinetic profile for identified enzyme
3. Protein Interactions -> Metabolic pathway context via STRING

## Completeness Checklist

- [ ] Enzyme identified with EC number, reaction, and organism sources
- [ ] Km, kcat, and kcat/Km values collected for relevant substrates
- [ ] Inhibitor profile assembled with Ki/IC50 values and mechanisms
- [ ] Cofactor requirements documented
- [ ] Cross-organism comparison included where relevant
- [ ] Engineering context provided (active site, published engineering efforts)
- [ ] Report file finalized with no `[Analyzing...]` placeholders
