# Caliby Recipes

> CLI commands for ensemble-conditioned inverse folding.
> Parent skill: [SKILL.md](SKILL.md) — full Caliby workflow.

---

## Recipe 1: Standard Sequence Design

```bash
python3 caliby/eval/sampling/seq_des.py \
  ckpt_name_or_path=caliby \
  input_cfg.pdb_dir=backbone_pdbs/ \
  sampling_cfg_overrides.num_seqs_per_pdb=8 \
  out_dir=designs/
```

---

## Recipe 2: Ensemble-Conditioned Design (Best Quality)

```bash
# Generate ensemble (Protpardelle partial diffusion)
python3 caliby/eval/sampling/generate_ensembles.py \
  input_cfg.pdb_dir=backbone_pdbs/ \
  out_dir=ensembles/

# Design on ensemble
python3 caliby/eval/sampling/seq_des_ensemble.py \
  ckpt_name_or_path=caliby \
  input_cfg.conformer_dir=ensembles/ \
  sampling_cfg_overrides.num_seqs_per_pdb=8 \
  out_dir=ensemble_designs/
```

---

## Recipe 3: Soluble Protein Design (No Hydrophobic Patches)

```bash
python3 caliby/eval/sampling/seq_des.py \
  ckpt_name_or_path=soluble_caliby \
  input_cfg.pdb_dir=backbone_pdbs/ \
  sampling_cfg_overrides.num_seqs_per_pdb=8 \
  ++sampling_cfg_overrides.omit_aas='["C"]' \
  out_dir=soluble_designs/
```

---

## Recipe 4: With Self-Consistency Evaluation

```bash
python3 caliby/eval/sampling/seq_des.py \
  ckpt_name_or_path=caliby \
  input_cfg.pdb_dir=backbone_pdbs/ \
  sampling_cfg_overrides.num_seqs_per_pdb=4 \
  run_self_consistency_eval=true \
  out_dir=sc_eval/

# Output includes scRMSD, pLDDT, TM-score per design
```

---

## Recipe 5: Compare Caliby vs ProteinMPNN

```bash
# Caliby
python3 caliby/eval/sampling/seq_des.py \
  ckpt_name_or_path=caliby \
  input_cfg.pdb_dir=test_pdbs/ \
  sampling_cfg_overrides.num_seqs_per_pdb=8 \
  run_self_consistency_eval=true \
  out_dir=caliby_out/

# ProteinMPNN
python ProteinMPNN/protein_mpnn_run.py \
  --pdb_path test_pdbs/target.pdb \
  --out_folder mpnn_out/ \
  --num_seq_per_target 8 \
  --sampling_temp "0.1"

# Compare self-consistency: Caliby typically shows lower scRMSD and higher pLDDT
```
