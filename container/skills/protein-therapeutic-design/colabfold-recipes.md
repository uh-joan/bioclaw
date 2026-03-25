# ColabFold Design Validation Recipes

Recipes for validating computationally designed proteins using ColabFold structure prediction. These complement the design pipeline in [SKILL.md](SKILL.md) by providing structural validation of designed sequences.

> **Parent skill**: [SKILL.md](SKILL.md) — full protein therapeutic design pipeline.
> **See also**: [colabfold-predict skill](../colabfold-predict/SKILL.md) — standalone ColabFold prediction skill with full CLI reference.

---

## Recipe 1: Design Self-Consistency Check (ProteinMPNN → ColabFold)

After designing a sequence with ProteinMPNN, predict its structure with ColabFold and compare to the target backbone. This is the most important validation step — a good design should refold to the target structure.

```bash
# Write designed sequence to FASTA
cat > designed_binder.fasta << 'FASTA'
>designed_binder_v1
MDESIGNEDSEQUENCEHERE
FASTA

# Predict with ColabFold (5 models for consensus)
colabfold_batch designed_binder.fasta validation/ --num-models 5 --num-recycle 10

# Compare to design target
python3 << 'PYTHON'
from Bio.PDB import PDBParser, Superimposer
import json, glob

parser = PDBParser(QUIET=True)

# Load design target backbone
target = parser.get_structure("target", "target_scaffold.pdb")
target_cas = [a for a in target.get_atoms() if a.get_name() == "CA"]

# Load best ColabFold prediction
pred_pdb = sorted(glob.glob("validation/*rank_001*.pdb"))[0]
pred = parser.get_structure("pred", pred_pdb)
pred_cas = [a for a in pred.get_atoms() if a.get_name() == "CA"]

# Compute RMSD
n = min(len(target_cas), len(pred_cas))
sup = Superimposer()
sup.set_atoms(target_cas[:n], pred_cas[:n])
sup.apply(pred.get_atoms())

# Read confidence
scores_file = sorted(glob.glob("validation/*scores_rank_001*.json"))[0]
with open(scores_file) as f:
    scores = json.load(f)
mean_plddt = sum(scores["plddt"]) / len(scores["plddt"])

print(f"CA RMSD to target: {sup.rms:.2f} A")
print(f"Mean pLDDT: {mean_plddt:.1f}")
print()

if sup.rms < 1.5 and mean_plddt > 80:
    print("PASS: Design refolds to target with high confidence")
elif sup.rms < 2.5 and mean_plddt > 70:
    print("MARGINAL: Moderate match — review interface and optimize")
else:
    print("FAIL: Design does not refold as intended — redesign needed")
PYTHON
```

**Decision criteria:**
- CA RMSD < 1.5 A + pLDDT > 80 → **Advance** to experimental validation
- CA RMSD 1.5-2.5 A or pLDDT 70-80 → **Iterate** (adjust ProteinMPNN temperature, add constraints)
- CA RMSD > 2.5 A or pLDDT < 70 → **Reject** and redesign scaffold

---

## Recipe 2: Batch Design Ranking

Screen multiple ProteinMPNN designs and rank by ColabFold confidence.

```bash
# Multiple designs in one FASTA
cat > candidates.fasta << 'FASTA'
>design_v1_temp01
MFIRSTDESIGNSEQUENCE
>design_v2_temp03
MSECONDDESIGNSEQUENCE
>design_v3_temp05
MTHIRDDESIGNSEQUENCE
FASTA

# Quick screen (1 model each for speed)
colabfold_batch candidates.fasta screen/ --num-models 1 --num-recycle 3 --stop-at-score 90

# Rank all designs
python3 << 'PYTHON'
import json, glob, os

designs = []
for f in sorted(glob.glob("screen/*scores_rank_001*.json")):
    name = os.path.basename(f).split("_scores")[0]
    with open(f) as fh:
        scores = json.load(fh)
    plddt = scores["plddt"]
    designs.append({
        "name": name,
        "mean_plddt": sum(plddt) / len(plddt),
        "ptm": scores.get("ptm", 0),
        "low_conf_frac": sum(1 for p in plddt if p < 70) / len(plddt),
    })

# Sort by mean pLDDT descending
designs.sort(key=lambda d: d["mean_plddt"], reverse=True)

print(f"{'Rank':<5} {'Design':<30} {'pLDDT':>7} {'pTM':>6} {'Low%':>6}")
print("-" * 58)
for i, d in enumerate(designs, 1):
    flag = " ***" if d["mean_plddt"] > 85 else ""
    print(f"{i:<5} {d['name']:<30} {d['mean_plddt']:>7.1f} {d['ptm']:>6.3f} {100*d['low_conf_frac']:>5.1f}%{flag}")

print(f"\nTop candidate: {designs[0]['name']} (pLDDT {designs[0]['mean_plddt']:.1f})")
PYTHON
```

---

## Recipe 3: Binder-Target Complex Validation

After designing a binder with RFdiffusion, validate the complex with ColabFold-Multimer.

```bash
# Format: designed_binder:target_protein
cat > complex.fasta << 'FASTA'
>binder_target_complex
MDESIGNEDBINDERSEQUENCE:MTARGETPROTEINSEQUENCE
FASTA

colabfold_batch complex.fasta complex_pred/ \
  --model-type alphafold2_multimer_v3 \
  --num-recycle 10 \
  --num-models 5 \
  --rank multimer

# Analyze interface
python3 << 'PYTHON'
import json, glob

scores_file = sorted(glob.glob("complex_pred/*scores_rank_001*.json"))[0]
with open(scores_file) as f:
    scores = json.load(f)

plddt = scores["plddt"]
iptm = scores.get("iptm", 0)
ptm = scores.get("ptm", 0)
multimer_score = 0.8 * iptm + 0.2 * ptm if iptm else ptm

print(f"ipTM: {iptm:.3f}")
print(f"pTM:  {ptm:.3f}")
print(f"Multimer score (0.8*ipTM + 0.2*pTM): {multimer_score:.3f}")
print(f"Mean pLDDT: {sum(plddt)/len(plddt):.1f}")
print()

if iptm > 0.75:
    print("CONFIDENT INTERFACE: Complex likely forms as predicted")
elif iptm > 0.5:
    print("MODERATE INTERFACE: Some binding plausible, interface details uncertain")
else:
    print("WEAK INTERFACE: Binding mode unreliable — redesign interface")

# PAE analysis across chains
if "pae" in scores:
    pae = scores["pae"]
    # Assuming first chain ends before second starts
    # Check inter-chain PAE (off-diagonal blocks)
    n = len(pae)
    # Simple heuristic: look at mean PAE
    flat_pae = [v for row in pae for v in row]
    print(f"\nMean PAE: {sum(flat_pae)/len(flat_pae):.1f} A")
PYTHON
```

**Interface quality thresholds:**
- ipTM > 0.75 → **High confidence** — proceed to experimental testing
- ipTM 0.5-0.75 → **Moderate** — consider redesigning interface hotspot residues
- ipTM < 0.5 → **Low confidence** — redesign binder or change binding mode

---

## Recipe 4: Miniprotein Stability Pre-Screen

Screen miniprotein designs for fold stability before synthesis.

```bash
cat > miniproteins.fasta << 'FASTA'
>mini_3helix_v1
EELKRKLAELKRKLAELKRKLA
>mini_3helix_v2
KELLRKLAELLRKLAELLRKLA
>mini_beta_v1
KLIVIWINGDKGYNGLAEVGK
FASTA

# Predict all
colabfold_batch miniproteins.fasta mini_screen/ --num-models 3 --num-recycle 5

# Stability assessment
python3 << 'PYTHON'
import json, glob, os

print("Miniprotein Stability Screen")
print("=" * 60)
print(f"{'Name':<25} {'pLDDT':>7} {'pTM':>6} {'Assessment':<20}")
print("-" * 60)

for f in sorted(glob.glob("mini_screen/*scores_rank_001*.json")):
    name = os.path.basename(f).split("_scores")[0]
    with open(f) as fh:
        scores = json.load(fh)
    plddt = scores["plddt"]
    mean_plddt = sum(plddt) / len(plddt)
    ptm = scores.get("ptm", 0)

    if mean_plddt > 85 and ptm > 0.8:
        assessment = "STABLE — synthesize"
    elif mean_plddt > 70:
        assessment = "MARGINAL — optimize"
    else:
        assessment = "UNSTABLE — discard"

    print(f"{name:<25} {mean_plddt:>7.1f} {ptm:>6.3f} {assessment}")
PYTHON
```

---

## Recipe 5: Per-Region Confidence for Interface Design

Analyze pLDDT specifically at the designed binding interface to assess local confidence.

```python
import json

def interface_confidence(scores_file, interface_residues):
    """
    Assess ColabFold confidence at specific interface residues.

    Args:
        scores_file: path to ColabFold *scores*.json
        interface_residues: list of 0-indexed residue positions at the interface
    """
    with open(scores_file) as f:
        scores = json.load(f)

    plddt = scores["plddt"]
    interface_plddt = [plddt[i] for i in interface_residues if i < len(plddt)]
    non_interface_plddt = [plddt[i] for i in range(len(plddt)) if i not in interface_residues]

    print(f"Interface residues ({len(interface_residues)}):")
    print(f"  Mean pLDDT: {sum(interface_plddt)/len(interface_plddt):.1f}")
    print(f"  Min pLDDT:  {min(interface_plddt):.1f}")
    print(f"  Residues <70: {sum(1 for p in interface_plddt if p < 70)}")
    print(f"\nNon-interface ({len(non_interface_plddt)} residues):")
    print(f"  Mean pLDDT: {sum(non_interface_plddt)/len(non_interface_plddt):.1f}")

    # Flag if interface is much less confident than core
    delta = (sum(non_interface_plddt)/len(non_interface_plddt)) - (sum(interface_plddt)/len(interface_plddt))
    if delta > 15:
        print(f"\nWARNING: Interface pLDDT {delta:.0f} points below core — interface may be poorly defined")
    elif delta > 5:
        print(f"\nCAUTION: Interface slightly less confident than core ({delta:.0f} pt gap)")
    else:
        print(f"\nGOOD: Interface confidence comparable to core")

# Usage:
# interface_confidence("results/binder_scores_rank_001.json", [10, 11, 12, 35, 36, 37, 42, 43])
```
