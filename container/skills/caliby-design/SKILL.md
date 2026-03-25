---
name: caliby-design
description: "Ensemble-conditioned protein sequence design using Caliby (Potts model inverse folding). Designs sequences from backbone structures or structural ensembles, outperforming ProteinMPNN on AlphaFold2 self-consistency. Uses Potts model sampling (captures pairwise correlations) instead of autoregressive decoding. Supports soluble model, ensemble conditioning, and sidechain packing. Use when user mentions Caliby, ensemble-conditioned design, Potts model inverse folding, better than ProteinMPNN, or ensemble sequence design."
---

# Caliby — Ensemble-Conditioned Inverse Folding

> **Code recipes**: See [recipes.md](recipes.md) for CLI commands.

Potts model-based protein sequence design from backbone structures. Outperforms ProteinMPNN on AlphaFold2 self-consistency by conditioning on synthetic structural ensembles (via Protpardelle partial diffusion). Captures global pairwise residue correlations instead of autoregressive left-to-right decoding.

**When to use Caliby vs ProteinMPNN:**
- **Caliby** — higher self-consistency (designed sequences more likely to refold correctly), ensemble conditioning, Potts model captures global correlations
- **ProteinMPNN** — faster, more established, richer constraint system (fixed positions, tied positions, AA bias, PSSM)

## Tool: Caliby CLI

```bash
git clone https://github.com/ProteinDesignLab/caliby.git && cd caliby
uv venv envs/caliby -p python3.12 && source envs/caliby/bin/activate
uv pip install -e . && source env_setup.sh
```

### Single-Structure Design

```bash
python3 caliby/eval/sampling/seq_des.py \
  ckpt_name_or_path=caliby \
  input_cfg.pdb_dir=my_pdbs/ \
  sampling_cfg_overrides.num_seqs_per_pdb=8 \
  out_dir=outputs/
```

### Ensemble-Conditioned Design (Better Self-Consistency)

```bash
# Step 1: Generate structural ensemble
python3 caliby/eval/sampling/generate_ensembles.py \
  input_cfg.pdb_dir=my_pdbs/ out_dir=ensembles/

# Step 2: Design on ensemble
python3 caliby/eval/sampling/seq_des_ensemble.py \
  ckpt_name_or_path=caliby \
  input_cfg.conformer_dir=ensembles/ \
  sampling_cfg_overrides.num_seqs_per_pdb=8 \
  out_dir=ensemble_designs/
```

### Key Parameters

| Parameter | Description |
|-----------|-------------|
| `ckpt_name_or_path` | Model: `caliby`, `soluble_caliby`, `solublecaliby_v1` |
| `sampling_cfg_overrides.num_seqs_per_pdb` | Sequences per structure |
| `sampling_cfg_overrides.omit_aas` | Exclude amino acids (e.g., `["C"]`) |
| `run_self_consistency_eval` | Auto-refold with AF2 and measure scRMSD |

### Output

- `seq_des_outputs.csv` — designed sequences with Potts energies
- Optional: packed CIF structures, self-consistency metrics (scRMSD, pLDDT, TM-score)

## Completeness Checklist

- [ ] Input backbone PDB(s) prepared
- [ ] Ensemble generated (for ensemble conditioning)
- [ ] Sequences designed with appropriate model variant
- [ ] Self-consistency evaluated (scRMSD < 2A, pLDDT > 0.8)
