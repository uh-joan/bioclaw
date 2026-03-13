# ESM MCP Server Recipes

> Copy-paste executable code templates for the ESM MCP server.
> Parent skill: [SKILL.md](SKILL.md) — full ESM protein design pipeline.
> See also: protein-therapeutic-design [esm-recipes.md](../protein-therapeutic-design/esm-recipes.md) for local ESM Python library recipes.

These recipes use the ESM **MCP server** (`mcp__esm__esm_protein`), not the Python library directly. The MCP server handles GPU inference and returns structured results.

---

## Recipe 1: Structure Prediction (Fold)

Predict 3D structure from an amino acid sequence.

```
mcp__esm__esm_protein(method: "fold", sequence: "MKTLLILAVFCLAQGGSEAEAPTGTDEKALESNG")
```

**When to use:** Single-sequence structure prediction. Faster than AlphaFold2, no MSA required. Ideal for designed proteins with no evolutionary data.

**Output:** PDB coordinates with per-residue confidence scores.

**Quality check:** pLDDT > 80 = high confidence. pLDDT < 70 = low confidence, consider AlphaFold2 instead.

---

## Recipe 2: Inverse Folding (Backbone → Sequence)

Design a new amino acid sequence that folds into a target backbone structure.

```
# Step 1: Get backbone coordinates from PDB
mcp__pdb__pdb_data(method: "download_structure", pdb_id: "1UBQ", format: "pdb")

# Step 2: Conservative design (high recovery)
mcp__esm__esm_protein(method: "inverse_fold", coordinates: BACKBONE_COORDS, temperature: 0.2)

# Step 3: Diverse design (more novelty)
mcp__esm__esm_protein(method: "inverse_fold", coordinates: BACKBONE_COORDS, temperature: 0.5)

# Step 4: Validate — fold designed sequence back
mcp__esm__esm_protein(method: "fold", sequence: "DESIGNED_SEQUENCE")
# Success: RMSD < 2 Å between folded design and original backbone
```

**Temperature guide:**
| Temperature | Recovery | Diversity | Use Case |
|------------|----------|-----------|----------|
| 0.1 | ~60-70% | Low | Conservative redesign, stabilization |
| 0.2 | ~40-60% | Medium | Standard design |
| 0.5 | ~20-40% | High | De novo design, novelty |

---

## Recipe 3: De Novo Sequence Generation

Generate novel protein sequences from scratch or with positional constraints.

```
# Unconditional: 80-residue protein from scratch
mcp__esm__esm_protein(method: "generate", sequence: "________________________________________________________________________________", num_steps: 80, temperature: 0.7)

# Conditional: fix catalytic triad (H30, D55, S75), scaffold around them
# Positions 30, 55, 75 have fixed AAs; rest are underscores
mcp__esm__esm_protein(method: "generate", sequence: "_____________________________H________________________D___________________S____", num_steps: 80, temperature: 0.5)
```

**Constraint patterns:**
- `_` (underscore) = masked position, ESM3 generates
- Explicit amino acid letter = fixed position, preserved during generation
- Mix fixed and masked for conditional design (active sites, binding motifs)

---

## Recipe 4: Variant Effect Scoring via Log-Likelihood

Score mutations using ESM log-probabilities.

```
# Step 1: Get log-probabilities for wild-type sequence
mcp__esm__esm_protein(method: "logits", sequence: "WILD_TYPE_SEQUENCE")

# Output: 20-dimensional probability vector per position
# For each mutation X→Y at position i:
#   LLR = log P(Y | context) - log P(X | context)
#   LLR < -2: likely deleterious
#   LLR ~ 0: neutral
#   LLR > 0: potentially favorable
```

**Interpretation:**
| LLR Score | Interpretation | Action |
|-----------|---------------|--------|
| < -3.0 | Strongly deleterious | Avoid this mutation |
| -3.0 to -1.0 | Likely deleterious | Caution, validate experimentally |
| -1.0 to 1.0 | Neutral | Tolerated position |
| > 1.0 | Potentially favorable | Consider for optimization |

---

## Recipe 5: Protein Embeddings for Comparison

Extract embeddings for protein similarity analysis.

```
# Get embeddings for two proteins
mcp__esm__esm_protein(method: "forward_and_sample", sequence: "PROTEIN_A_SEQUENCE", return_embeddings: true, temperature: 0.01)
mcp__esm__esm_protein(method: "forward_and_sample", sequence: "PROTEIN_B_SEQUENCE", return_embeddings: true, temperature: 0.01)

# Compute cosine similarity from returned embeddings
# > 0.9: very similar (same family)
# 0.7-0.9: related (similar fold/function)
# < 0.7: distinct proteins
```

**Use cases:**
- Cluster designed variants by functional similarity
- Find the closest natural homolog to a designed protein
- Quality control: designed protein should embed near target family

---

## Recipe 6: Sequence Tokenization (Encode/Decode)

Convert between amino acid sequences and ESM token IDs.

```
# Encode: sequence → tokens
mcp__esm__esm_protein(method: "encode", sequence: "MKTLLILAVFCLAQ")

# Decode: tokens → sequence
mcp__esm__esm_protein(method: "decode", tokens: [20, 11, 17, ...])
```

**When to use:** Preprocessing for custom pipelines, debugging tokenization issues, or building hybrid workflows that mix MCP calls with local computation.

---

## Recipe 7: MSA Retrieval

Get multiple sequence alignment for evolutionary context.

```
mcp__esm__esm_protein(method: "get_msa", sequence: "PROTEIN_SEQUENCE")
```

**When to use:** When you need evolutionary conservation data to complement ESM predictions. MSA depth indicates how well-studied the protein family is — deeper MSA = more reliable evolutionary signal.

---

## Recipe 8: Full Design-Validate-Score Pipeline

End-to-end workflow: design a protein, predict its structure, and score variants.

```
# 1. Get target structure
mcp__pdb__pdb_data(method: "download_structure", pdb_id: "TARGET_PDB", format: "pdb")

# 2. Inverse fold: design 3 sequences at different temperatures
mcp__esm__esm_protein(method: "inverse_fold", coordinates: COORDS, temperature: 0.1)
mcp__esm__esm_protein(method: "inverse_fold", coordinates: COORDS, temperature: 0.3)
mcp__esm__esm_protein(method: "inverse_fold", coordinates: COORDS, temperature: 0.5)

# 3. Fold each design back (self-consistency check)
mcp__esm__esm_protein(method: "fold", sequence: "DESIGN_1")
mcp__esm__esm_protein(method: "fold", sequence: "DESIGN_2")
mcp__esm__esm_protein(method: "fold", sequence: "DESIGN_3")

# 4. Score mutations at key positions for the best design
mcp__esm__esm_protein(method: "logits", sequence: "BEST_DESIGN")

# 5. Get embeddings for functional comparison
mcp__esm__esm_protein(method: "forward_and_sample", sequence: "BEST_DESIGN", return_embeddings: true)

# Success criteria:
#   - Self-consistency RMSD < 2 Å
#   - pLDDT > 80 at binding interface
#   - Active site residues maintain geometry
```

---

## Recipe 9: Saturation Mutagenesis Scan

Score all possible single-point mutations at every position.

```
# 1. Get baseline log-probabilities
mcp__esm__esm_protein(method: "logits", sequence: "YOUR_PROTEIN_SEQUENCE")

# 2. For each position i (1 to L):
#    For each amino acid a (A, C, D, E, F, G, H, I, K, L, M, N, P, Q, R, S, T, V, W, Y):
#      LLR[i][a] = logit[i][a] - logit[i][wt_aa[i]]

# 3. Build heatmap:
#    Rows = positions, Columns = 20 amino acids
#    Color: blue (favorable) → white (neutral) → red (deleterious)

# 4. Identify:
#    - Conserved positions (all mutations deleterious) → structural core
#    - Tolerant positions (most mutations neutral) → surface, loop regions
#    - Positions favoring specific substitutions → optimization targets
```

**Output format:**

```
Position | WT | Most deleterious | Most tolerated | Conservation score
---------|----|-----------------|--------------------|-------------------
   1     | M  | M→P (-4.2)      | M→L (-0.1)        | High (core)
  15     | A  | A→W (-1.8)      | A→G (+0.3)        | Low (surface)
```

---

## Cross-Skill Routing

- Full protein therapeutic design pipeline → [protein-therapeutic-design](../protein-therapeutic-design/SKILL.md)
- Local ESM Python library recipes → [esm-recipes.md](../protein-therapeutic-design/esm-recipes.md)
- Enzyme kinetics for designed enzymes → [enzyme-kinetics](../enzyme-kinetics/SKILL.md)
- Cell type expression context → [cell-type-expression](../cell-type-expression/SKILL.md)
