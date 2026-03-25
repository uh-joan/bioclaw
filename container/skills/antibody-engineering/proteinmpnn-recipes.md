# ProteinMPNN Antibody Engineering Recipes

Recipes for antibody sequence design using ProteinMPNN. Redesigns CDR loops while keeping framework regions fixed, designs humanized variants, and optimizes antibody-antigen interfaces.

> **Parent skill**: [SKILL.md](SKILL.md) — full antibody engineering pipeline.
> **See also**: [proteinmpnn-design skill](../proteinmpnn-design/SKILL.md) — standalone ProteinMPNN with full CLI reference.

---

## Recipe 1: CDR Loop Redesign with Fixed Framework

Redesign CDR loops while keeping the framework absolutely fixed — for affinity maturation or specificity engineering.

```bash
# Parse antibody Fv structure
python ProteinMPNN/helper_scripts/parse_multiple_chains.py \
  --input_path ab_pdbs/ --output_path parsed.jsonl

# Fix framework, design only CDR positions
# CDR-H1: 26-35, CDR-H2: 50-65, CDR-H3: 95-102 (Kabat approximate, 1-based sequential)
# CDR-L1: 24-34, CDR-L2: 50-56, CDR-L3: 89-97
python ProteinMPNN/helper_scripts/make_fixed_positions_dict.py \
  --input_path parsed.jsonl \
  --output_path cdr_design.jsonl \
  --chain_list "A B" \
  --position_list "26 27 28 29 30 31 32 33 34 35 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 95 96 97 98 99 100 101 102" \
  --specify_non_fixed  # these CDR positions will be redesigned

# Design with antigen as fixed context
python ProteinMPNN/helper_scripts/assign_fixed_chains.py \
  --input_path parsed.jsonl \
  --output_path chains.jsonl \
  --chain_list "A B"  # design VH (A) and VL (B), fix antigen (C)

python ProteinMPNN/protein_mpnn_run.py \
  --jsonl_path parsed.jsonl \
  --chain_id_jsonl chains.jsonl \
  --fixed_positions_jsonl cdr_design.jsonl \
  --out_folder cdr_redesign/ \
  --num_seq_per_target 32 \
  --sampling_temp "0.1 0.2" \
  --omit_AAs "CX" \
  --seed 37

# Validate with ColabFold-Multimer (see colabfold-recipes.md)
```

---

## Recipe 2: Humanization via ProteinMPNN

Use ProteinMPNN to design human-like sequences for a mouse antibody framework while preserving CDR identity. The backbone geometry constrains the design toward human germline-compatible sequences.

```bash
# Fix CDR loops (keep mouse CDRs), redesign framework to human-compatible
python ProteinMPNN/helper_scripts/make_fixed_positions_dict.py \
  --input_path parsed.jsonl \
  --output_path fix_cdrs.jsonl \
  --chain_list "A" \
  --position_list "26 27 28 29 30 31 32 33 34 35 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 95 96 97 98 99 100 101 102"
  # CDR positions are FIXED — framework will be redesigned

# Optional: bias toward human-frequent amino acids at framework positions
# (Use PSSM from human germline alignment)

python ProteinMPNN/protein_mpnn_run.py \
  --jsonl_path parsed.jsonl \
  --fixed_positions_jsonl fix_cdrs.jsonl \
  --out_folder humanized/ \
  --num_seq_per_target 16 \
  --sampling_temp "0.1" \
  --use_soluble_model \
  --seed 37

# Compare designed frameworks to human germline VH/VL databases
# Filter for highest human identity while maintaining CDR support
```

---

## Recipe 3: Antibody Interface Optimization

Redesign only the paratope contact residues for improved binding, keeping everything else fixed.

```bash
# Identify paratope contact residues (from Ab-Ag complex structure)
# These are the positions within 4.5A of antigen

python ProteinMPNN/helper_scripts/make_fixed_positions_dict.py \
  --input_path parsed.jsonl \
  --output_path paratope_only.jsonl \
  --chain_list "A" \
  --position_list "33 52 54 100 101 102" \
  --specify_non_fixed  # only redesign contact residues

python ProteinMPNN/protein_mpnn_run.py \
  --jsonl_path parsed.jsonl \
  --chain_id_jsonl chains.jsonl \
  --fixed_positions_jsonl paratope_only.jsonl \
  --out_folder paratope_opt/ \
  --num_seq_per_target 64 \
  --sampling_temp "0.1 0.15 0.2" \
  --seed 37

# Many samples (64) at low temperature — explore nearby sequence space
# Validate top designs with Boltz-2 for complex + affinity
```

---

## Recipe 4: Developability-Optimized Antibody Design

Redesign surface positions to remove developability liabilities (aggregation-prone patches, deamidation sites) while preserving binding.

```bash
# Fix CDRs + core, redesign surface framework for developability
# Omit asparagine-glycine (NG deamidation motif) by excluding N at positions before G

python ProteinMPNN/protein_mpnn_run.py \
  --jsonl_path parsed.jsonl \
  --fixed_positions_jsonl fix_cdrs_and_core.jsonl \
  --out_folder developability/ \
  --num_seq_per_target 16 \
  --sampling_temp "0.1" \
  --use_soluble_model \
  --omit_AAs "CMX" \
  --seed 37

# M = avoid methionine oxidation, C = avoid unpaired cysteines
# Compare aggregation propensity scores across designs
```
