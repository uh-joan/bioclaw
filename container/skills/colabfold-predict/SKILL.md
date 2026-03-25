---
name: colabfold-predict
description: Protein structure prediction using ColabFold (AlphaFold2 + MMseqs2). Predicts 3D structures from amino acid sequences for monomers and complexes, with pLDDT and PAE confidence metrics. Use when user mentions structure prediction, fold a protein, predict structure, ColabFold, AlphaFold2 prediction, multimer prediction, protein complex structure, predict folding, or run AlphaFold.
---

# ColabFold Structure Prediction

> **Code recipes**: See [recipes.md](recipes.md) for copy-paste CLI commands and Python analysis templates.

Protein structure prediction specialist using ColabFold — AlphaFold2/Multimer with fast MMseqs2 MSA generation. Predicts 3D structures from amino acid sequences for monomers and protein complexes. Outputs PDB/mmCIF files with per-residue pLDDT confidence scores and Predicted Aligned Error (PAE) matrices.

**Key distinction from `alphafold-structures`**: That skill queries the AlphaFold *Database* (pre-computed structures for known UniProt proteins). This skill *runs predictions* for arbitrary sequences — novel designs, mutants, engineered variants, and complexes not in any database.

**When to use Boltz-2 instead**: If your prediction involves small-molecule ligands, DNA/RNA, covalent modifications, binding affinity estimation, or pocket-conditioned docking, use the `boltz-predict` skill instead. ColabFold is faster for protein-only predictions.

**When to use Chai-1 instead**: If your prediction involves glycans/glycoproteins, experimental restraints (crosslinks, known contacts), or you need fast single-sequence mode without MSA, use the `chai-predict` skill instead.

**When to use Protenix instead**: If you need the highest possible accuracy (outperforms AF3), are predicting hard targets (Ab-Ag complexes), or want to apply inference-time scaling (100+ candidates), use the `protenix-predict` skill.

## Report-First Workflow

1. **Create report file immediately**: `[protein]_colabfold_prediction_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Predicting...]`
3. **Populate progressively**: Update sections as predictions complete
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Predicting...]` placeholders remain

## When NOT to Use This Skill

- Retrieving pre-computed AlphaFold DB structures for known UniProt proteins -> use `alphafold-structures`
- Experimental (X-ray/cryo-EM) structure retrieval -> use `pdb-structures`
- Protein sequence/function lookups -> use UniProt tools
- Protein design (generating new sequences) -> use `protein-therapeutic-design`
- Antibody-specific modeling and engineering -> use `antibody-engineering`

## Cross-Reference: Other Skills

- **Pre-computed AlphaFold structures for known proteins** -> use alphafold-structures skill
- **Experimental structures** -> use pdb-structures skill
- **Protein design then structure validation** -> use protein-therapeutic-design skill (design) then this skill (validate)
- **Antibody-antigen complex prediction** -> use antibody-engineering skill (design) then this skill (predict complex)
- **Enzyme mutant screening** -> use enzyme-engineering skill (design) then this skill (predict mutant structures)

## Tool: ColabFold CLI (`colabfold_batch`)

ColabFold is available as a command-line tool. All predictions are run via Bash.

### Installation Check

```bash
# Verify ColabFold is available
colabfold_batch --help 2>/dev/null || pip install colabfold[alphafold]
```

### Core Commands

| Command | Purpose |
|---------|---------|
| `colabfold_batch input.fasta output_dir/` | Predict structures from FASTA |
| `colabfold_batch input.fasta output_dir/ --msa-only` | Generate MSA only (faster) |
| `colabfold_batch msas/ output_dir/` | Predict from pre-computed MSAs |
| `colabfold_search input.fasta db_path/ msas/` | Local MSA search (no API) |

### Key Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--num-models` | 5 | Number of AlphaFold2 models to run (1-5) |
| `--num-recycle` | 3 | Recycling iterations (more = better, slower) |
| `--num-seeds` | 1 | Random seeds for diversity |
| `--model-type` | auto | `alphafold2_ptm` (monomer) or `alphafold2_multimer_v3` (complex) |
| `--templates` | off | Use PDB templates for prediction |
| `--amber` | off | AMBER relaxation of predicted structures |
| `--num-relax` | 0 | Number of top structures to relax |
| `--stop-at-score` | 100 | Early stopping when pLDDT reaches threshold |
| `--msa-mode` | `mmseqs2_uniref_env` | MSA database: `mmseqs2_uniref_env`, `mmseqs2_uniref`, `single_sequence` |
| `--use-dropout` | off | Enable dropout for conformational sampling |
| `--max-msa` | - | Subsample MSA (e.g., `"512:1024"`) for diversity |
| `--rank` | auto | Ranking metric: `plddt`, `ptm`, `iptm`, `multimer` |
| `--cpu` | off | CPU-only mode (slow but no GPU needed) |
| `--zip` | off | Bundle outputs into ZIP |

## Input Formats

### Monomer (single chain)

```
>protein_name
MKFLVLLFNILCLFPVLAENQDKGMAHISMDQELRRFKDNREKTHFDYSIIFHQNVSSYKCEYFNPISINYRTEIDKPCQHSQCSMPDDIHPADIPLKDLDIQYPEETFGYRCECRPGYYLANKQFWEKRQPDNYTSYLIFKEIEEKIIPTAPN
```

### Complex (multimer — colon-separated chains)

```
>complex_name
FIRSTCHAINSEQUENCE:SECONDCHAINSEQUENCE
```

### Heteromer (different chains)

```
>antibody_antigen
VHSEQUENCE:VLSEQUENCE:ANTIGENSEQUENCE
```

### Homomer (same chain repeated)

```
>homodimer
MONOMERSEQUENCE:MONOMERSEQUENCE
```

### Batch (multiple queries in one FASTA)

```
>query1
SEQUENCE1
>query2
SEQUENCE2A:SEQUENCE2B
```

## Output Files

For each query, ColabFold produces:

| File | Content |
|------|---------|
| `*_relaxed_rank_001.pdb` | Best-ranked relaxed structure (if `--amber`) |
| `*_unrelaxed_rank_001.pdb` | Best-ranked unrelaxed structure |
| `*_scores_rank_001.json` | pLDDT, pTM, PAE matrix for best model |
| `*_coverage.png` | MSA coverage plot |
| `*_plddt.png` | Per-residue pLDDT plot |
| `*_pae.png` | Predicted Aligned Error heatmap |
| `*.a3m` | Generated MSA |
| `*_env/` | Environmental sequence MSA |

### Interpreting Confidence

**pLDDT (per-residue confidence, 0-100):**
- >90: Very high confidence — reliable for atomic-level analysis
- 70-90: Confident — good backbone, some sidechain uncertainty
- 50-70: Low confidence — may be disordered or flexible
- <50: Very low — likely disordered, do not interpret structurally

**pTM (predicted TM-score, 0-1):**
- >0.8: High-quality overall fold prediction
- 0.5-0.8: Moderate confidence
- <0.5: Low confidence in global fold

**ipTM (interface pTM, multimer only, 0-1):**
- >0.8: Confident protein-protein interface
- 0.6-0.8: Moderate interface confidence
- <0.6: Unreliable interface prediction

**PAE (Predicted Aligned Error):**
- Low PAE between domains: confident relative orientation
- High PAE between domains: uncertain relative positioning (may be flexible linker)

## Prediction Strategies

### Quick Prediction (screening)

For rapid assessment of many candidates:
```bash
colabfold_batch input.fasta output/ --num-models 1 --num-recycle 3 --stop-at-score 80
```

### High-Quality Prediction

For publication-grade structures:
```bash
colabfold_batch input.fasta output/ --num-models 5 --num-recycle 20 --templates --amber --num-relax 1
```

### Conformational Sampling

For flexible proteins or multiple states:
```bash
colabfold_batch input.fasta output/ --num-models 5 --num-seeds 5 --use-dropout --max-msa "512:1024"
```

### Complex / Multimer

For protein-protein complexes:
```bash
colabfold_batch complex.fasta output/ --model-type alphafold2_multimer_v3 --num-recycle 10
```

### MSA-Only (for downstream tools)

Generate alignments without prediction:
```bash
colabfold_batch input.fasta output/ --msa-only
```

## Common Workflows

### 1. Design Validation Pipeline

Validate computationally designed proteins:

1. Receive designed sequence from `protein-therapeutic-design` or `enzyme-engineering`
2. Write sequence to FASTA file
3. Run ColabFold prediction
4. Check pLDDT — design is promising if mean pLDDT > 80
5. Compare predicted structure to design target (if available)
6. Report confidence per-region

### 2. Mutant Screening

Compare wildtype vs mutant structures:

1. Predict wildtype structure
2. Predict mutant structure(s)
3. Compare pLDDT profiles — drops indicate destabilization
4. Check PAE for domain-domain orientation changes
5. Flag mutations that reduce pLDDT by >10 in functional regions

### 3. Antibody-Antigen Complex

Predict antibody binding mode:

1. Format FASTA: `VH:VL:ANTIGEN` (colon-separated)
2. Run with `--model-type alphafold2_multimer_v3 --num-recycle 10`
3. Assess ipTM — >0.6 suggests plausible interface
4. Analyze PAE between antibody and antigen chains
5. Extract interface residues from predicted structure

### 4. Novel Protein Characterization

For proteins not in AlphaFold DB:

1. Check `alphafold-structures` skill first (may already exist)
2. If not available, write sequence to FASTA
3. Run ColabFold with templates enabled
4. Analyze confidence regions
5. Cross-reference low-confidence regions with known disorder predictions

### 5. Homomer / Oligomeric State

Predict quaternary structure:

1. Format FASTA with repeated chains: `SEQ:SEQ` (dimer), `SEQ:SEQ:SEQ` (trimer)
2. Run with multimer model
3. Check ipTM for interface quality
4. Compare different oligomeric states to find the most confident prediction

## Tiered Execution (Timeout Resilience)

### Tier 1 — MUST COMPLETE (first 5 min)
```
1. Write FASTA input file
2. Run quick prediction (--num-models 1 --num-recycle 3)
3. Extract pLDDT, pTM scores and write to report
>>> CHECKPOINT: Write initial prediction results <<<
```

### Tier 2 — HIGH VALUE (next 10 min)
```
4. Run full prediction (--num-models 5 --num-recycle 10)
5. Compare model rankings
6. Analyze PAE for domain confidence
>>> CHECKPOINT: Write detailed structural analysis <<<
```

### Tier 3 — COMPLETE PICTURE (remaining time)
```
7. AMBER relaxation of top model
8. Conformational sampling (dropout mode)
9. Template-guided prediction for comparison
>>> FINAL CHECKPOINT: Write complete report <<<
```

## Completeness Checklist

**Tier 1 (minimum viable prediction):**
- [ ] Input sequence(s) validated and FASTA file written
- [ ] ColabFold prediction completed (at least 1 model)
- [ ] pLDDT scores extracted and interpreted
- [ ] pTM score reported (and ipTM for complexes)
- [ ] Report file saved with initial results

**Tier 2 (standard prediction):**
- [ ] Multiple models ranked and compared
- [ ] PAE matrix analyzed for domain confidence
- [ ] Low-confidence regions identified and annotated
- [ ] MSA coverage assessed (deep MSA = more reliable)
- [ ] Cross-referenced with AlphaFold DB if protein is known

**Tier 3 (complete analysis):**
- [ ] AMBER-relaxed structure generated
- [ ] Conformational diversity sampled (if relevant)
- [ ] Template comparison performed
- [ ] Visualization files prepared (PDB + confidence coloring)
- [ ] Structural insights summarized in executive assessment
