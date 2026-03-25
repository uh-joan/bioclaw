# ProteinMPNN Recipes

> Copy-paste CLI commands and Python analysis templates for ProteinMPNN sequence design.
> Parent skill: [SKILL.md](SKILL.md) — full inverse folding workflow and parameter guide.

---

## Recipe 1: Basic Sequence Design from PDB

Design 8 sequences for a backbone structure at conservative temperature.

```bash
# Design sequences
python ProteinMPNN/protein_mpnn_run.py \
  --pdb_path target.pdb \
  --out_folder design_output/ \
  --num_seq_per_target 8 \
  --sampling_temp "0.1" \
  --seed 37 \
  --model_name "v_48_020"

# Parse results
python3 << 'PYTHON'
designs = []
with open("design_output/seqs/target.fa") as f:
    header, seq = None, None
    for line in f:
        if line.startswith(">"):
            if header and seq and "sample=" in header:
                score = float(header.split("score=")[1].split(",")[0])
                recovery = float(header.split("seq_recovery=")[1]) if "seq_recovery" in header else 0
                designs.append({"header": header.strip(">").strip(), "seq": seq, "score": score, "recovery": recovery})
            header = line
            seq = ""
        else:
            seq = (seq or "") + line.strip()
    if header and seq and "sample=" in header:
        score = float(header.split("score=")[1].split(",")[0])
        recovery = float(header.split("seq_recovery=")[1]) if "seq_recovery" in header else 0
        designs.append({"header": header.strip(">").strip(), "seq": seq, "score": score, "recovery": recovery})

designs.sort(key=lambda d: d["score"])

print("ProteinMPNN Designs (ranked by score)")
print("=" * 65)
print(f"{'Rank':<5} {'Score':>7} {'Recovery':>9} {'Length':>7}")
print("-" * 65)
for i, d in enumerate(designs, 1):
    print(f"{i:<5} {d['score']:>7.4f} {d['recovery']:>9.4f} {len(d['seq']):>7}")

print(f"\nBest design: score={designs[0]['score']:.4f}, recovery={designs[0]['recovery']:.4f}")
print(f"Sequence: {designs[0]['seq'][:60]}...")
PYTHON
```

---

## Recipe 2: Design with Fixed Residues (Catalytic Site / Binding Hotspots)

Fix key residues while redesigning the rest — essential for enzyme active sites and binding interfaces.

```bash
# Parse PDB
python ProteinMPNN/helper_scripts/parse_multiple_chains.py \
  --input_path pdb_folder/ \
  --output_path parsed.jsonl

# Fix specific positions (1-based sequential numbering)
python ProteinMPNN/helper_scripts/make_fixed_positions_dict.py \
  --input_path parsed.jsonl \
  --output_path fixed_pos.jsonl \
  --chain_list "A" \
  --position_list "82 153 217"  # catalytic triad positions

# Design with fixed residues
python ProteinMPNN/protein_mpnn_run.py \
  --jsonl_path parsed.jsonl \
  --fixed_positions_jsonl fixed_pos.jsonl \
  --out_folder constrained_output/ \
  --num_seq_per_target 16 \
  --sampling_temp "0.1 0.2" \
  --seed 37
```

---

## Recipe 3: Multi-Chain Interface Design

Design interface residues on chain A while holding chain B fixed — for binder design.

```bash
# Parse PDB
python ProteinMPNN/helper_scripts/parse_multiple_chains.py \
  --input_path pdb_folder/ \
  --output_path parsed.jsonl

# Chain A = design, Chain B = fixed context
python ProteinMPNN/helper_scripts/assign_fixed_chains.py \
  --input_path parsed.jsonl \
  --output_path chains.jsonl \
  --chain_list "A"  # design chain A only

python ProteinMPNN/protein_mpnn_run.py \
  --jsonl_path parsed.jsonl \
  --chain_id_jsonl chains.jsonl \
  --out_folder interface_output/ \
  --num_seq_per_target 16 \
  --sampling_temp "0.1" \
  --seed 37
```

---

## Recipe 4: Homooligomer Design (Symmetric)

Design a homodimer/trimer with identical sequences across chains.

```bash
python ProteinMPNN/protein_mpnn_run.py \
  --pdb_path homodimer.pdb \
  --out_folder homo_output/ \
  --num_seq_per_target 8 \
  --sampling_temp "0.1" \
  --homooligomer 1 \
  --seed 37

# All chains will have identical sequences
```

---

## Recipe 5: Soluble Protein Design (No Hydrophobic Patches)

Use the soluble model to avoid transmembrane-like hydrophobic surface patches.

```bash
python ProteinMPNN/protein_mpnn_run.py \
  --pdb_path scaffold.pdb \
  --out_folder soluble_output/ \
  --num_seq_per_target 8 \
  --sampling_temp "0.1" \
  --use_soluble_model \
  --omit_AAs "CX" \
  --seed 37

# --omit_AAs "CX" avoids free cysteines (common for soluble expression)
```

---

## Recipe 6: Full Design-Predict-Validate Pipeline

The gold standard: design with ProteinMPNN, predict with ColabFold, compare to target.

```bash
# Step 1: Design sequences
python ProteinMPNN/protein_mpnn_run.py \
  --pdb_path target_backbone.pdb \
  --out_folder mpnn_designs/ \
  --num_seq_per_target 8 \
  --sampling_temp "0.1" \
  --seed 37

# Step 2: Extract designed sequences to ColabFold FASTA
python3 << 'PYTHON'
designs = []
with open("mpnn_designs/seqs/target_backbone.fa") as f:
    header, seq = None, None
    for line in f:
        if line.startswith(">"):
            if header and seq and "sample=" in header:
                sample = header.split("sample=")[1].split(",")[0]
                designs.append((f"design_{sample}", seq))
            header = line
            seq = ""
        else:
            seq = (seq or "") + line.strip()
    if header and seq and "sample=" in header:
        sample = header.split("sample=")[1].split(",")[0]
        designs.append((f"design_{sample}", seq))

# Write ColabFold input
with open("validation_input.fasta", "w") as f:
    for name, seq in designs:
        f.write(f">{name}\n{seq}\n")
print(f"Wrote {len(designs)} designs to validation_input.fasta")
PYTHON

# Step 3: Predict structures with ColabFold
colabfold_batch validation_input.fasta validation_results/ \
  --num-models 1 --num-recycle 3 --stop-at-score 85

# Step 4: Compare predicted vs target backbone
python3 << 'PYTHON'
from Bio.PDB import PDBParser, Superimposer
import json, glob

parser = PDBParser(QUIET=True)
target = parser.get_structure("target", "target_backbone.pdb")
target_cas = [a for a in target.get_atoms() if a.get_name() == "CA"]

print("Design-Predict-Validate Results")
print("=" * 65)
print(f"{'Design':<15} {'RMSD (A)':>9} {'pLDDT':>7} {'pTM':>6} {'Verdict':<15}")
print("-" * 65)

for scores_file in sorted(glob.glob("validation_results/*scores_rank_001*.json")):
    name = scores_file.split("/")[-1].split("_scores")[0]
    with open(scores_file) as f:
        scores = json.load(f)

    mean_plddt = sum(scores["plddt"]) / len(scores["plddt"])
    ptm = scores.get("ptm", 0)

    # RMSD to target
    pred_pdbs = glob.glob(f"validation_results/{name}*rank_001*.pdb")
    if pred_pdbs:
        pred = parser.get_structure("pred", pred_pdbs[0])
        pred_cas = [a for a in pred.get_atoms() if a.get_name() == "CA"]
        n = min(len(target_cas), len(pred_cas))
        sup = Superimposer()
        sup.set_atoms(target_cas[:n], pred_cas[:n])
        rmsd = sup.rms
    else:
        rmsd = float("inf")

    if rmsd < 1.5 and mean_plddt > 80:
        verdict = "PASS ***"
    elif rmsd < 2.5 and mean_plddt > 70:
        verdict = "MARGINAL"
    else:
        verdict = "FAIL"

    print(f"{name:<15} {rmsd:>9.2f} {mean_plddt:>7.1f} {ptm:>6.3f} {verdict}")
PYTHON
```

---

## Recipe 7: Temperature Sweep for Diversity Analysis

Generate sequences across multiple temperatures to explore the fitness landscape.

```bash
python ProteinMPNN/protein_mpnn_run.py \
  --pdb_path target.pdb \
  --out_folder temp_sweep/ \
  --num_seq_per_target 8 \
  --sampling_temp "0.1 0.15 0.2 0.25 0.3" \
  --seed 37

# Analyze diversity
python3 << 'PYTHON'
from collections import defaultdict

temps = defaultdict(list)
with open("temp_sweep/seqs/target.fa") as f:
    header, seq = None, None
    for line in f:
        if line.startswith(">"):
            if header and seq and "T=" in header:
                t = header.split("T=")[1].split(",")[0]
                score = float(header.split("score=")[1].split(",")[0])
                temps[t].append({"seq": seq, "score": score})
            header = line
            seq = ""
        else:
            seq = (seq or "") + line.strip()
    if header and seq and "T=" in header:
        t = header.split("T=")[1].split(",")[0]
        score = float(header.split("score=")[1].split(",")[0])
        temps[t].append({"seq": seq, "score": score})

print("Temperature vs Design Quality")
print("=" * 55)
print(f"{'Temp':<6} {'N':>3} {'Mean Score':>11} {'Diversity':>10}")
print("-" * 55)

for t in sorted(temps.keys()):
    designs = temps[t]
    mean_score = sum(d["score"] for d in designs) / len(designs)
    # Hamming diversity: average pairwise differences
    total_diff, pairs = 0, 0
    for i, d1 in enumerate(designs):
        for d2 in designs[i+1:]:
            n = min(len(d1["seq"]), len(d2["seq"]))
            total_diff += sum(1 for a, b in zip(d1["seq"][:n], d2["seq"][:n]) if a != b) / n
            pairs += 1
    diversity = total_diff / pairs if pairs else 0
    print(f"{t:<6} {len(designs):>3} {mean_score:>11.4f} {diversity:>10.1%}")
PYTHON
```

---

## Recipe 8: Score Existing Sequences Against Backbone

Evaluate how well native or engineered sequences fit a backbone without designing new ones.

```bash
python ProteinMPNN/protein_mpnn_run.py \
  --pdb_path structure.pdb \
  --out_folder score_output/ \
  --score_only 1 \
  --save_score 1 \
  --save_probs 1 \
  --seed 37

# Analyze per-position probabilities
python3 << 'PYTHON'
import numpy as np

probs = np.load("score_output/probs/structure.npz")
# probs contains per-position amino acid probability distributions

print("Positions with strongest backbone constraint (lowest entropy):")
# MPNN alphabet: ACDEFGHIKLMNPQRSTVWYX
for chain_key in sorted(probs.files):
    p = probs[chain_key]  # [L, 21]
    entropy = -np.sum(p * np.log(p + 1e-10), axis=1)
    constrained = np.argsort(entropy)[:10]
    print(f"\n{chain_key} — most constrained positions:")
    for pos in constrained:
        best_aa_idx = np.argmax(p[pos])
        aa = "ACDEFGHIKLMNPQRSTVWYX"[best_aa_idx]
        print(f"  Position {pos+1}: {aa} (prob={p[pos, best_aa_idx]:.3f}, entropy={entropy[pos]:.3f})")
PYTHON
```

---

## Recipe 9: Amino Acid Bias (Composition Control)

Control amino acid composition — e.g., bias toward polar residues for solubility, or exclude cysteines.

```bash
# Global bias: favor charged residues, disfavor hydrophobic
python ProteinMPNN/helper_scripts/make_bias_AA.py \
  --output_path aa_bias.jsonl \
  --AA_list "D E K R" \
  --bias_list "0.5 0.5 0.5 0.5"

python ProteinMPNN/protein_mpnn_run.py \
  --pdb_path target.pdb \
  --out_folder biased_output/ \
  --num_seq_per_target 8 \
  --sampling_temp "0.1" \
  --bias_AA_jsonl aa_bias.jsonl \
  --omit_AAs "CWX" \
  --seed 37
```

---

## Recipe 10: Multi-Temperature Design with Validation Pipeline

Production-grade workflow: design at multiple temperatures, validate all, select best.

```bash
# Design
python ProteinMPNN/protein_mpnn_run.py \
  --pdb_path target.pdb \
  --out_folder production/ \
  --num_seq_per_target 16 \
  --sampling_temp "0.1 0.2" \
  --use_soluble_model \
  --omit_AAs "CX" \
  --seed 37

# Extract all designs to FASTA for validation
python3 -c "
designs = []
with open('production/seqs/target.fa') as f:
    h, s = None, None
    for line in f:
        if line.startswith('>'):
            if h and s and 'sample=' in h:
                t = h.split('T=')[1].split(',')[0]
                n = h.split('sample=')[1].split(',')[0]
                designs.append((f'T{t}_s{n}', s))
            h, s = line, ''
        else:
            s = (s or '') + line.strip()
    if h and s and 'sample=' in h:
        t = h.split('T=')[1].split(',')[0]
        n = h.split('sample=')[1].split(',')[0]
        designs.append((f'T{t}_s{n}', s))

with open('all_designs.fasta', 'w') as f:
    for name, seq in designs:
        f.write(f'>{name}\n{seq}\n')
print(f'Wrote {len(designs)} designs for validation')
"

# Validate with ColabFold
colabfold_batch all_designs.fasta validation/ --num-models 1 --num-recycle 3

echo "Compare validation/*/scores*.json against target.pdb for RMSD + pLDDT filtering"
```
