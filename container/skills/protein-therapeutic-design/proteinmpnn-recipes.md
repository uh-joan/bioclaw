# ProteinMPNN Protein Therapeutic Design Recipes

Recipes for the core design step in the protein therapeutic pipeline: designing sequences from scaffold structures using ProteinMPNN, then validating with structure prediction.

> **Parent skill**: [SKILL.md](SKILL.md) — full protein therapeutic design pipeline.
> **See also**: [proteinmpnn-design skill](../proteinmpnn-design/SKILL.md) — standalone ProteinMPNN with full CLI reference.

---

## Recipe 1: Miniprotein Binder Design Pipeline

Full pipeline: take a designed miniprotein scaffold, design sequences with ProteinMPNN, validate with ColabFold.

```bash
# Step 1: Design sequences from scaffold (binder bound to target)
python ProteinMPNN/protein_mpnn_run.py \
  --pdb_path binder_target_complex.pdb \
  --pdb_path_chains "A" \
  --out_folder binder_designs/ \
  --num_seq_per_target 16 \
  --sampling_temp "0.1" \
  --use_soluble_model \
  --omit_AAs "CX" \
  --seed 37

# Chain A = designed binder, Chain B = fixed target context
# ProteinMPNN sees the target but only designs chain A

# Step 2: Validate with ColabFold (see colabfold-recipes.md Recipe 1)
# Step 3: Filter by RMSD < 1.5A and pLDDT > 80
```

---

## Recipe 2: Interface Hotspot Redesign

Redesign only the interface residues while keeping the core fixed. Useful for affinity maturation of designed binders.

```bash
# Parse and fix core positions
python ProteinMPNN/helper_scripts/parse_multiple_chains.py \
  --input_path pdb_folder/ --output_path parsed.jsonl

# Fix everything except interface (specify only designable positions)
python ProteinMPNN/helper_scripts/make_fixed_positions_dict.py \
  --input_path parsed.jsonl \
  --output_path fixed.jsonl \
  --chain_list "A" \
  --position_list "10 11 12 35 36 37 42 43 44" \
  --specify_non_fixed  # these are the positions TO DESIGN (not fixed)

python ProteinMPNN/protein_mpnn_run.py \
  --jsonl_path parsed.jsonl \
  --fixed_positions_jsonl fixed.jsonl \
  --out_folder interface_redesign/ \
  --num_seq_per_target 32 \
  --sampling_temp "0.1 0.2" \
  --seed 37
```

---

## Recipe 3: Repeat Protein Design with Symmetry

Design a repeat protein (e.g., designed ankyrin repeat) with tied positions across repeats.

```bash
# For identical repeat units, tie corresponding positions
python ProteinMPNN/protein_mpnn_run.py \
  --pdb_path repeat_protein.pdb \
  --out_folder repeat_output/ \
  --num_seq_per_target 8 \
  --sampling_temp "0.1" \
  --homooligomer 1 \
  --seed 37

# If repeat units are on the same chain, use --tied_positions_jsonl instead
```

---

## Recipe 4: Scaffold → ProteinMPNN → ColabFold → Boltz Full Loop

The complete design-predict-validate pipeline using all tools.

```bash
# 1. Design sequences from RFdiffusion scaffold
python ProteinMPNN/protein_mpnn_run.py \
  --pdb_path rfdiffusion_scaffold.pdb \
  --pdb_path_chains "A" \
  --out_folder mpnn_out/ \
  --num_seq_per_target 8 \
  --sampling_temp "0.1" \
  --use_soluble_model \
  --seed 37

# 2. Extract designed binder sequences
python3 -c "
seqs = []
with open('mpnn_out/seqs/rfdiffusion_scaffold.fa') as f:
    h, s = None, ''
    for line in f:
        if line.startswith('>'):
            if h and s and 'sample=' in h:
                n = h.split('sample=')[1].split(',')[0]
                score = h.split('score=')[1].split(',')[0]
                seqs.append((f'design_{n}_score{score}', s.split('/')[0]))  # chain A only
            h, s = line, ''
        else: s += line.strip()
    if h and s and 'sample=' in h:
        n = h.split('sample=')[1].split(',')[0]
        score = h.split('score=')[1].split(',')[0]
        seqs.append((f'design_{n}_score{score}', s.split('/')[0]))
with open('designs_for_cf.fasta', 'w') as f:
    for name, seq in seqs:
        f.write(f'>{name}\n{seq}\n')
print(f'{len(seqs)} designs extracted')
"

# 3. ColabFold self-consistency check (protein-only, fast)
colabfold_batch designs_for_cf.fasta cf_validation/ --num-models 1 --num-recycle 3

# 4. For top designs, run Boltz-2 with target + ligand (if applicable)
# See boltz-recipes.md for protein-ligand complex prediction
```
