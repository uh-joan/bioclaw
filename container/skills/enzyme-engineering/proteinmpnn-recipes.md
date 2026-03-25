# ProteinMPNN Enzyme Engineering Recipes

Recipes for enzyme sequence redesign using ProteinMPNN. Designs new sequences for enzyme backbones while preserving catalytic residues, active site geometry, and key structural features.

> **Parent skill**: [SKILL.md](SKILL.md) — full enzyme engineering pipeline.
> **See also**: [proteinmpnn-design skill](../proteinmpnn-design/SKILL.md) — standalone ProteinMPNN with full CLI reference.

---

## Recipe 1: Active Site Redesign with Fixed Catalytic Residues

Redesign the enzyme scaffold while keeping the catalytic triad/dyad absolutely fixed.

```bash
# Parse PDB
python ProteinMPNN/helper_scripts/parse_multiple_chains.py \
  --input_path enzyme_pdbs/ --output_path parsed.jsonl

# Fix catalytic residues (example: serine hydrolase triad Ser153, His263, Asp217)
python ProteinMPNN/helper_scripts/make_fixed_positions_dict.py \
  --input_path parsed.jsonl \
  --output_path fixed_catalytic.jsonl \
  --chain_list "A" \
  --position_list "82 153 217 263"  # catalytic + oxyanion hole

# Design with soluble model, no cysteines
python ProteinMPNN/protein_mpnn_run.py \
  --jsonl_path parsed.jsonl \
  --fixed_positions_jsonl fixed_catalytic.jsonl \
  --out_folder enzyme_redesign/ \
  --num_seq_per_target 16 \
  --sampling_temp "0.1 0.2" \
  --use_soluble_model \
  --omit_AAs "CX" \
  --seed 37

# Validate: predict with ColabFold, check active site RMSD
# See colabfold-recipes.md Recipe 2 (active site geometry validation)
```

---

## Recipe 2: Thermostability Design

Redesign surface residues for improved thermostability while keeping the core and active site fixed.

```bash
# Fix core + active site, design only surface positions
python ProteinMPNN/helper_scripts/make_fixed_positions_dict.py \
  --input_path parsed.jsonl \
  --output_path surface_only.jsonl \
  --chain_list "A" \
  --position_list "5 8 12 15 23 27 34 38 45 52 67 71 89 95 110 125 140" \
  --specify_non_fixed  # these are the surface positions TO DESIGN

python ProteinMPNN/protein_mpnn_run.py \
  --jsonl_path parsed.jsonl \
  --fixed_positions_jsonl surface_only.jsonl \
  --out_folder thermo_designs/ \
  --num_seq_per_target 16 \
  --sampling_temp "0.1" \
  --use_soluble_model \
  --seed 37

# Bias toward stabilizing residues (Pro in loops, salt bridges)
python ProteinMPNN/helper_scripts/make_bias_AA.py \
  --output_path thermo_bias.jsonl \
  --AA_list "P E K R D" \
  --bias_list "0.3 0.2 0.2 0.2 0.2"

python ProteinMPNN/protein_mpnn_run.py \
  --jsonl_path parsed.jsonl \
  --fixed_positions_jsonl surface_only.jsonl \
  --bias_AA_jsonl thermo_bias.jsonl \
  --out_folder thermo_biased/ \
  --num_seq_per_target 16 \
  --sampling_temp "0.1" \
  --seed 37
```

---

## Recipe 3: Substrate Tunnel Redesign

Redesign residues lining the substrate access tunnel to alter specificity, while keeping the active site and core fixed.

```bash
# Tunnel-lining residues to redesign (from tunnel analysis)
python ProteinMPNN/helper_scripts/make_fixed_positions_dict.py \
  --input_path parsed.jsonl \
  --output_path tunnel_design.jsonl \
  --chain_list "A" \
  --position_list "45 48 52 78 81 85 109 112 156 159" \
  --specify_non_fixed  # tunnel positions to redesign

python ProteinMPNN/protein_mpnn_run.py \
  --jsonl_path parsed.jsonl \
  --fixed_positions_jsonl tunnel_design.jsonl \
  --out_folder tunnel_output/ \
  --num_seq_per_target 32 \
  --sampling_temp "0.1 0.2 0.3" \
  --seed 37

# Higher diversity (T=0.3) for tunnel residues — more exploration of specificity
# Validate: dock substrate with Boltz-2 (see boltz-recipes.md) to check access
```

---

## Recipe 4: Consensus Design for Directed Evolution Library

Generate diverse starting sequences as seeds for directed evolution rounds.

```bash
# Many sequences at higher temperature for diversity
python ProteinMPNN/protein_mpnn_run.py \
  --pdb_path wildtype_enzyme.pdb \
  --out_folder evo_library/ \
  --num_seq_per_target 64 \
  --sampling_temp "0.2 0.3" \
  --use_soluble_model \
  --seed 37

# Analyze sequence diversity
python3 << 'PYTHON'
from collections import Counter

seqs = []
with open("evo_library/seqs/wildtype_enzyme.fa") as f:
    h, s = None, ""
    for line in f:
        if line.startswith(">"):
            if h and s and "sample=" in h:
                seqs.append(s)
            h, s = line, ""
        else:
            s += line.strip()
    if h and s and "sample=" in h:
        seqs.append(s)

# Position-wise conservation
n = len(seqs[0]) if seqs else 0
print(f"Library: {len(seqs)} sequences, {n} positions")
print(f"\nVariable positions (< 80% conservation):")
for pos in range(n):
    aa_counts = Counter(s[pos] for s in seqs if pos < len(s))
    most_common_frac = aa_counts.most_common(1)[0][1] / len(seqs)
    if most_common_frac < 0.8:
        top3 = ", ".join(f"{aa}:{c}" for aa, c in aa_counts.most_common(3))
        print(f"  Position {pos+1}: {top3} (conservation={most_common_frac:.0%})")
PYTHON
```
