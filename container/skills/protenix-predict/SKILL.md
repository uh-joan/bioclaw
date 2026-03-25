---
name: protenix-predict
description: "Highest-accuracy biomolecular structure prediction using Protenix (open-source AF3-class). Predicts proteins, ligands, DNA, RNA, ions, glycans, and covalent modifications. Unique: outperforms AlphaFold3 on benchmarks, inference-time scaling for hard targets, mini models for fast screening, fully trainable/finetuneable. Use when user mentions Protenix, highest accuracy prediction, AF3-class, hard target prediction, antibody-antigen complex prediction, inference scaling, train structure prediction model, finetune prediction model, or best accuracy structure prediction."
---

# Protenix — AF3-Class Biomolecular Structure Prediction

> **Code recipes**: See [recipes.md](recipes.md) for copy-paste CLI commands and Python analysis templates.

Highest-accuracy open-source biomolecular structure prediction. Protenix is a fully open AF3-class model from ByteDance that predicts 3D structures of proteins, DNA, RNA, ligands, ions, glycans, and their complexes. First open-source model to outperform AlphaFold3 on benchmarks.

**When to use Protenix vs alternatives:**
- **Highest accuracy needed** → Protenix (outperforms AF3 on benchmarks)
- **Hard targets** (Ab-Ag, flexible complexes) → Protenix with inference-time scaling (50-200 samples)
- **Fast protein-only screening** → `colabfold-predict` (faster for protein-only)
- **Drug docking with binding affinity** → `boltz-predict` (unique affinity head)
- **Glycan-native syntax / experimental restraints** → `chai-predict` (more ergonomic glycan input)
- **Custom model training/finetuning** → Protenix (only tool with open training pipeline)
- **Fast screening with mini models** → Protenix-Mini (110-135M params, much faster)

## Report-First Workflow

1. **Create report file immediately**: `[complex]_protenix_prediction_report.md`
2. **Add placeholders**: Mark each section `[Predicting...]`
3. **Populate progressively**: Update as predictions complete
4. **Final verification**: Ensure no placeholders remain

## When NOT to Use This Skill

- Pre-computed AlphaFold DB structures → use `alphafold-structures`
- Protein-only fast screening → use `colabfold-predict` (faster)
- Binding affinity prediction → use `boltz-predict` (has affinity head)
- Sequence design from structure → use `proteinmpnn-design`

## Cross-Reference: Other Skills

- **Protein-only fast prediction** → use colabfold-predict
- **Drug docking + affinity** → use boltz-predict
- **Glycan-focused prediction** → use chai-predict (dedicated glycan syntax)
- **Sequence design from backbone** → use proteinmpnn-design
- **Design validation pipeline** → use protein-therapeutic-design

## Tool: Protenix CLI (`protenix pred`)

### Installation Check

```bash
protenix pred --help 2>/dev/null || pip install protenix
```

### Core Commands

| Command | Purpose |
|---------|---------|
| `protenix pred -i input.json -o output/` | Run structure prediction |
| `protenix json -i structure.pdb -o input.json` | Convert PDB/CIF to JSON input |
| `protenix msa -i input.json -o msa_dir/` | Generate MSAs |
| `protenix mt -i input.json -o mt_dir/` | MSA + template search |
| `protenix prep -i input.json -o prep_dir/` | Full preprocessing |

### Key Prediction Flags

| Flag | Default | Description |
|------|---------|-------------|
| `-i` | - | Input JSON file |
| `-o` | - | Output directory |
| `-n` | auto | Model name (e.g., `protenix_base_default_v1.0.0`) |
| `-s` | `[0]` | Seeds (list, e.g., `[0,1,2,3,4]` for 5 seeds) |
| `-c` | 10 | Recycle cycles |
| `-p` | 200 | Diffusion steps |
| `-e` | 5 | Samples per seed |
| `-d` | bf16 | Data type (bf16 or fp32) |
| `--use_msa` | true | Use MSA features |
| `--use_template` | true | Use structural templates |
| `--use_rna_msa` | false | Use RNA MSA |
| `--enable_cache` | false | Cache intermediate states (faster) |
| `--enable_fusion` | false | Kernel fusion (faster) |

### Model Variants

| Model | Params | Speed | Use when |
|-------|--------|-------|----------|
| `protenix_base_default_v1.0.0` | 368M | Standard | Best accuracy, general use |
| `protenix_base_20250630_v1.0.0` | 368M | Standard | Latest training data (Jun 2025) |
| `protenix_mini_esm_v1.0.0` | ~135M | ~3x faster | Fast screening, MSA-free (ESM2) |
| `protenix_mini_ism_v1.0.0` | ~135M | ~3x faster | Fast screening, MSA-free (ISM) |
| `protenix_tiny_v1.0.0` | ~110M | ~4x faster | Quickest screening |

## Input Format: JSON (AF Server-Compatible)

### Protein-Ligand Complex

```json
[
  {
    "sequences": [
      {
        "proteinChain": {
          "sequence": "MPROTEINSEQUENCE",
          "count": 1
        }
      },
      {
        "ligand": {
          "CCD": "ATP",
          "count": 1
        }
      }
    ],
    "name": "protein_atp"
  }
]
```

### Ligand via SMILES

```json
{
  "ligand": {
    "smiles": "CC(=O)Oc1ccccc1C(=O)O",
    "count": 1
  }
}
```

### Protein with Modifications

```json
{
  "proteinChain": {
    "sequence": "MRKDESEESQATKELIR",
    "modifications": [
      {"ptmType": "CCD_SEP", "ptmPosition": 6},
      {"ptmType": "CCD_TPO", "ptmPosition": 12}
    ],
    "count": 1
  }
}
```

### DNA/RNA

```json
{
  "dnaSequence": {
    "sequence": "ATCGATCG",
    "count": 1
  }
}
```

### Glycan (Multi-CCD)

```json
{
  "ligand": {
    "CCD": "NAG_BMA_MAN",
    "count": 1
  }
}
```

### Covalent Bond

```json
{
  "covalent_bonds": [
    ["A", 153, "SG", "B", 1, "C3"]
  ]
}
```

### Constraints

```json
{
  "constraint": {
    "contact": [
      {"chainA": "A", "res_idxA": 45, "chainB": "B", "res_idxB": 78, "distogram_range": [0, 8]}
    ],
    "pocket": [
      {"binder": "B", "contacts": [{"chain": "A", "res_idx": 45}, {"chain": "A", "res_idx": 82}]}
    ]
  }
}
```

## Output Files

| File | Content |
|------|---------|
| `*.cif` | Predicted structures (per seed × sample) |
| `*_summary.json` | Confidence metrics: pLDDT, pTM, ipTM, PDE, clash, disorder |

### Confidence Metrics

| Metric | Range | Interpretation |
|--------|-------|---------------|
| `ranking_score` | 0-1 | Combined score for ranking samples |
| `ptm` | 0-1 | Predicted TM-score (global fold) |
| `iptm` | 0-1 | Interface TM-score |
| `plddt` | 0-1 | Per-residue local confidence |
| `global_pde` | Angstroms | Global predicted distance error (lower = better) |
| `chain_ptm` | 0-1 per chain | Per-chain fold quality |
| `chain_pair_iptm` | 0-1 per pair | Pairwise interface quality |
| `has_clash` | bool | Steric clash detected |

## Prediction Strategies

### Quick Screening (Mini Model)

```bash
protenix pred -i input.json -o quick/ -n protenix_mini_esm_v1.0.0 -s "[0]" -e 1 -c 3
```

### Standard Prediction

```bash
protenix pred -i input.json -o standard/ -n protenix_base_default_v1.0.0 -s "[0]" -e 5
```

### High-Accuracy (Inference-Time Scaling)

For hard targets — generate many samples and pick the best:
```bash
protenix pred -i input.json -o scaled/ -n protenix_base_default_v1.0.0 \
  -s "[0,1,2,3,4,5,6,7,8,9]" -e 10 -c 10 -p 200
# 10 seeds × 10 samples = 100 candidates
```

### Ab-Ag Complex (Maximum Effort)

```bash
protenix pred -i ab_ag.json -o ab_ag/ -n protenix_base_default_v1.0.0 \
  -s "[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]" -e 10 -c 10
# 200 candidates — log-linear accuracy improvement
```

## Common Workflows

### 1. Standard Complex Prediction

1. Get sequences from UniProt, ligand from PubChem/ChEMBL
2. Write JSON input
3. Run `protenix prep` for MSA + templates
4. Run `protenix pred` with base model
5. Rank samples by `ranking_score`

### 2. Hard Target with Inference Scaling

1. Write JSON input for the complex
2. Run with many seeds (10-20) and samples per seed (10)
3. 100-200 candidates generated
4. Top-ranked candidate has log-linear accuracy improvement
5. Especially effective for Ab-Ag, multi-domain, flexible complexes

### 3. Fast Screening with Mini Models

1. Write JSON inputs for many candidates
2. Run with mini model (3x faster, minimal accuracy loss)
3. Rank candidates
4. Re-run top candidates with base model for final accuracy

### 4. PDB → Prediction Comparison

1. Convert known PDB structure to JSON: `protenix json -i known.pdb`
2. Predict from sequence only
3. Compare prediction to known structure for validation

## Tiered Execution (Timeout Resilience)

### Tier 1 — MUST COMPLETE (first 5 min)
```
1. Write JSON input
2. Quick prediction with mini model (1 seed, 1 sample)
3. Extract ranking_score, pTM, ipTM
>>> CHECKPOINT: Write initial prediction <<<
```

### Tier 2 — HIGH VALUE (next 15 min)
```
4. Base model prediction (1 seed, 5 samples)
5. MSA + template preprocessing
6. Analyze per-chain confidence
>>> CHECKPOINT: Write standard prediction <<<
```

### Tier 3 — COMPLETE PICTURE (remaining time)
```
7. Inference scaling (5+ seeds, 10 samples each)
8. Rank all candidates
9. Cross-validate with Boltz-2/ColabFold
>>> FINAL CHECKPOINT: Write scaled prediction report <<<
```

## Completeness Checklist

**Tier 1 (minimum viable prediction):**
- [ ] JSON input written with correct entity types
- [ ] Protenix prediction completed (at least 1 sample)
- [ ] Confidence metrics extracted (ranking_score, pTM, ipTM)
- [ ] Report file saved

**Tier 2 (standard prediction):**
- [ ] MSA + templates used for full accuracy
- [ ] Multiple samples ranked
- [ ] Per-chain and pairwise interface confidence assessed
- [ ] Constraints applied if experimental data available

**Tier 3 (maximum accuracy):**
- [ ] Inference-time scaling applied (50-200 candidates)
- [ ] Best candidate identified from scaled sampling
- [ ] Cross-validated with alternative tools
- [ ] Final structural assessment with confidence summary
