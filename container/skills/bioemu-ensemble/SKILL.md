---
name: bioemu-ensemble
description: "Protein conformational ensemble sampling using BioEmu (Microsoft). Generates equilibrium conformational ensembles from sequence alone — approximates Boltzmann distribution at ~1 kcal/mol accuracy, orders of magnitude faster than MD. Use when user mentions BioEmu, conformational ensemble, protein dynamics sampling, equilibrium distribution, conformational states, protein flexibility analysis, Boltzmann sampling, or fast MD alternative."
---

# BioEmu — Protein Conformational Ensemble Sampling

> **Code recipes**: See [recipes.md](recipes.md) for CLI commands and analysis templates.

Generates equilibrium conformational ensembles from amino acid sequence alone. Approximates the Boltzmann distribution at ~1 kcal/mol accuracy — orders of magnitude faster than molecular dynamics. Produces diverse structural states a protein naturally occupies. Published in *Science* (2025).

**When to use BioEmu vs alternatives:**
- **BioEmu** — rapid conformational ensemble (minutes vs days for MD), monomers, no ligands
- **Molecular dynamics** (GROMACS/OpenMM) — full dynamics/kinetics, ligand binding, multi-chain
- **Structure prediction** (ColabFold/Boltz/Protenix) — single static structure, not ensemble

## Tool: BioEmu CLI

```bash
pip install bioemu

python -m bioemu.sample \
  --sequence MPROTEINSEQUENCE \
  --num_samples 100 \
  --output_dir ensemble_output/
```

### Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--sequence` | - | Amino acid sequence (or FASTA/A3M file) |
| `--num_samples` | - | Number of conformations to generate |
| `--output_dir` | - | Output directory |
| `--model_name` | v1.1 | Model version (v1.0, v1.1, v1.2) |
| `--filter_samples` | True | Remove unphysical structures |
| `--batch_size_100` | 10 | Batch size (20 for A100 80GB) |
| `--steering_config` | None | Physical steering YAML (improves quality) |

### Output

- PDB + XTC trajectory files of conformational ensemble
- Filtered to remove clashes and chain breaks (default)
- Optional side-chain reconstruction via `bioemu.sidechain_relax`

### Performance

| Protein size | Time (A100, 1000 samples) |
|-------------|--------------------------|
| 100 residues | ~4 min |
| 300 residues | ~40 min |
| 600 residues | ~150 min |

## Completeness Checklist

- [ ] Protein sequence provided
- [ ] Ensemble generated (100+ samples recommended)
- [ ] Unphysical samples filtered
- [ ] Conformational diversity analyzed (clustering, RMSD distribution)
- [ ] Functional states identified (if applicable)
