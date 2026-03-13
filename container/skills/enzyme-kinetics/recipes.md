# BRENDA Enzyme Recipes

> Copy-paste executable MCP call sequences for enzyme analysis.
> Parent skill: [SKILL.md](SKILL.md) — full enzyme analysis pipeline.

---

## Recipe 1: Full Enzyme Kinetic Profile

Complete kinetic characterization for a known EC number.

```
# 1. Identify the enzyme
mcp__brenda__brenda_enzymes(method: "get_enzyme_names", ec_number: "2.7.11.1")
mcp__brenda__brenda_enzymes(method: "get_reaction", ec_number: "2.7.11.1")

# 2. Get kinetic parameters (human)
mcp__brenda__brenda_enzymes(method: "get_km_value", ec_number: "2.7.11.1", organism: "Homo sapiens")
mcp__brenda__brenda_enzymes(method: "get_kcat_value", ec_number: "2.7.11.1", organism: "Homo sapiens")
mcp__brenda__brenda_enzymes(method: "get_kcat_km_value", ec_number: "2.7.11.1", organism: "Homo sapiens")

# 3. Inhibitors and cofactors
mcp__brenda__brenda_enzymes(method: "get_inhibitors", ec_number: "2.7.11.1")
mcp__brenda__brenda_enzymes(method: "get_ki_value", ec_number: "2.7.11.1", organism: "Homo sapiens")
mcp__brenda__brenda_enzymes(method: "get_cofactor", ec_number: "2.7.11.1")
```

**Output format:**

```
## Enzyme: [Name] (EC X.X.X.X)
**Reaction:** substrate₁ + substrate₂ → product₁ + product₂
**Cofactors:** [list]

| Substrate | Km (µM) | kcat (s⁻¹) | kcat/Km (M⁻¹s⁻¹) | Organism |
|-----------|---------|-----------|-------------------|----------|

| Inhibitor | Ki (nM) | Type | Reference |
|-----------|---------|------|-----------|
```

---

## Recipe 2: Substrate Discovery

Find which enzymes act on a specific substrate.

```
# 1. Search by substrate
mcp__brenda__brenda_enzymes(method: "search_by_substrate", substrate: "ATP")

# 2. For each enzyme found, get kinetic data
mcp__brenda__brenda_enzymes(method: "get_km_value", ec_number: "FOUND_EC", substrate: "ATP")
mcp__brenda__brenda_enzymes(method: "get_kcat_value", ec_number: "FOUND_EC", substrate: "ATP")

# 3. Get reaction context
mcp__brenda__brenda_enzymes(method: "get_reaction", ec_number: "FOUND_EC")
```

---

## Recipe 3: Cross-Organism Enzyme Comparison

Compare enzyme properties across species for engineering decisions.

```
# For each organism of interest:
organisms = ["Homo sapiens", "Escherichia coli", "Thermus thermophilus", "Saccharomyces cerevisiae"]

# Per organism:
mcp__brenda__brenda_enzymes(method: "get_km_value", ec_number: "EC_NUMBER", organism: "ORGANISM")
mcp__brenda__brenda_enzymes(method: "get_kcat_value", ec_number: "EC_NUMBER", organism: "ORGANISM")
mcp__brenda__brenda_enzymes(method: "get_kcat_km_value", ec_number: "EC_NUMBER", organism: "ORGANISM")
```

**Decision matrix:**
- Best kcat/Km → highest natural efficiency (engineering starting point)
- Thermophilic variant → thermostability scaffold
- E. coli variant → expression system compatibility

---

## Recipe 4: Inhibitor Profiling for Drug Discovery

Comprehensive inhibitor analysis for a drug target enzyme.

```
# 1. All known inhibitors
mcp__brenda__brenda_enzymes(method: "get_inhibitors", ec_number: "EC_NUMBER")

# 2. Quantitative Ki values
mcp__brenda__brenda_enzymes(method: "get_ki_value", ec_number: "EC_NUMBER", organism: "Homo sapiens")

# 3. Specific inhibitor deep dive
mcp__brenda__brenda_enzymes(method: "get_ki_value", ec_number: "EC_NUMBER", inhibitor: "INHIBITOR_NAME")

# 4. Cross-reference with ChEMBL
mcp__chembl__chembl_info(method: "target_search", query: "ENZYME_NAME", limit: 5)
mcp__chembl__chembl_info(method: "get_bioactivity", target_id: "CHEMBL_ID", limit: 50)

# 5. Literature on inhibitor design
mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "EC_NUMBER inhibitor design selectivity", num_results: 10)
```

---

## Recipe 5: Enzyme Engineering Baseline

Establish kinetic benchmarks before engineering.

```
# 1. Current performance
mcp__brenda__brenda_enzymes(method: "get_km_value", ec_number: "EC_NUMBER", organism: "SOURCE_ORGANISM")
mcp__brenda__brenda_enzymes(method: "get_kcat_value", ec_number: "EC_NUMBER", organism: "SOURCE_ORGANISM")

# 2. Best natural performance (any organism)
mcp__brenda__brenda_enzymes(method: "get_kcat_km_value", ec_number: "EC_NUMBER")
# -> Identify organism with highest kcat/Km as engineering benchmark

# 3. Active site and cofactor requirements
mcp__brenda__brenda_enzymes(method: "get_cofactor", ec_number: "EC_NUMBER")
mcp__uniprot__uniprot_data(method: "get_protein_features", accession: "UNIPROT_ACC")
# -> Catalytic residues that must be preserved during engineering

# 4. Engineering literature
mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "EC_NUMBER directed evolution rational design engineering", num_results: 15)

# 5. ESM structure for design input
mcp__esm__esm_protein(method: "fold", sequence: "ENZYME_SEQUENCE")
# -> Structure for inverse folding or variant scoring
```

---

## Recipe 6: CYP Enzyme Drug Metabolism

Characterize cytochrome P450 enzymes for drug metabolism context.

```
# Common CYP EC numbers:
# CYP3A4: 1.14.14.1 (mixed function monooxygenase family)
# CYP2D6: 1.14.14.1
# CYP2C9: 1.14.14.1

# 1. Substrates and kinetics
mcp__brenda__brenda_enzymes(method: "get_km_value", ec_number: "1.14.14.1", organism: "Homo sapiens")
mcp__brenda__brenda_enzymes(method: "get_kcat_value", ec_number: "1.14.14.1", organism: "Homo sapiens")

# 2. Inhibitors (DDI risk)
mcp__brenda__brenda_enzymes(method: "get_inhibitors", ec_number: "1.14.14.1", organism: "Homo sapiens")
mcp__brenda__brenda_enzymes(method: "get_ki_value", ec_number: "1.14.14.1", organism: "Homo sapiens")

# 3. Cofactor (heme requirement)
mcp__brenda__brenda_enzymes(method: "get_cofactor", ec_number: "1.14.14.1")

# 4. Cross-reference with DDI skill
# -> Hand off to drug-interaction-analyst for clinical DDI assessment
```

---

## Cross-Skill Routing

- ESM structure prediction for enzyme scaffolds → [esm-protein-design](../esm-protein-design/SKILL.md)
- Full protein design pipeline → [protein-therapeutic-design](../protein-therapeutic-design/SKILL.md)
- Drug-drug interactions via CYP enzymes → drug-interaction-analyst
- Small molecule inhibitor optimization → binder-discovery-specialist
