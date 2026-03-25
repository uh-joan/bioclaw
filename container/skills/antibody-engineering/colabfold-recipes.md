# ColabFold Antibody Recipes

Recipes for antibody structure prediction and validation using ColabFold-Multimer. These complement the antibody engineering pipeline in [SKILL.md](SKILL.md).

> **Parent skill**: [SKILL.md](SKILL.md) — full antibody engineering pipeline.
> **See also**: [colabfold-predict skill](../colabfold-predict/SKILL.md) — standalone ColabFold prediction skill with full CLI reference.

---

## Recipe 1: Antibody Fv Structure Prediction

Predict the VH-VL paired structure of an antibody Fv fragment.

```bash
# VH:VL as colon-separated chains
cat > fv.fasta << 'FASTA'
>trastuzumab_fv
EVQLVESGGGLVQPGGSLRLSCAASGFNIKDTYIHWVRQAPGKGLEWVARIYPTNGYTRYADSVKGRFTISADTSKNTAYLQMNSLRAEDTAVYYCSRWGGDGFYAMDYWGQGTLVTVSS:DIQMTQSPSSLSASVGDRVTITCRASQDVNTAVAWYQQKPGKAPKLLIYSASFLYSGVPSRFSGSRSGTDFTLTISSLQPEDFATYYCQQHYTTPPTFGQGTKVEIK
FASTA

colabfold_batch fv.fasta fv_pred/ \
  --model-type alphafold2_multimer_v3 \
  --num-recycle 10 \
  --num-models 5

# Assess VH-VL interface
cat fv_pred/*scores_rank_001*.json | python3 -c "
import json, sys
s = json.load(sys.stdin)
print(f'ipTM: {s.get(\"iptm\", \"N/A\")}')
print(f'pTM:  {s.get(\"ptm\", \"N/A\")}')
print(f'Mean pLDDT: {sum(s[\"plddt\"])/len(s[\"plddt\"]):.1f}')
"
```

---

## Recipe 2: Antibody-Antigen Complex Prediction

Predict the full antibody-antigen binding complex to assess paratope-epitope interface.

```bash
# Format: VH:VL:ANTIGEN
cat > ab_ag_complex.fasta << 'FASTA'
>antibody_antigen
VHSEQUENCEHERE:VLSEQUENCEHERE:ANTIGENSEQUENCEHERE
FASTA

colabfold_batch ab_ag_complex.fasta complex_pred/ \
  --model-type alphafold2_multimer_v3 \
  --num-recycle 10 \
  --num-models 5 \
  --rank multimer

# Analyze binding interface
python3 << 'PYTHON'
import json, glob
from Bio.PDB import PDBParser

# Read scores
scores_file = sorted(glob.glob("complex_pred/*scores_rank_001*.json"))[0]
with open(scores_file) as f:
    scores = json.load(f)

iptm = scores.get("iptm", 0)
ptm = scores.get("ptm", 0)
plddt = scores["plddt"]

print("Antibody-Antigen Complex Assessment")
print("=" * 50)
print(f"ipTM:  {iptm:.3f}")
print(f"pTM:   {ptm:.3f}")
print(f"Mean pLDDT: {sum(plddt)/len(plddt):.1f}")
print()

if iptm > 0.7:
    print("HIGH CONFIDENCE: Interface well-predicted — extract contact residues for epitope mapping")
elif iptm > 0.5:
    print("MODERATE: Binding plausible but interface details uncertain")
else:
    print("LOW CONFIDENCE: Interface unreliable — consider alternative docking approaches")

# Extract interface contacts from PDB
pdb_file = sorted(glob.glob("complex_pred/*rank_001*.pdb"))[0]
parser = PDBParser(QUIET=True)
structure = parser.get_structure("complex", pdb_file)

chains = list(structure[0].get_chains())
if len(chains) >= 3:
    ab_atoms = list(chains[0].get_atoms()) + list(chains[1].get_atoms())
    ag_atoms = list(chains[2].get_atoms())

    # Find contacts (< 4.5 A)
    contacts = []
    for ab_a in ab_atoms:
        for ag_a in ag_atoms:
            dist = ab_a - ag_a
            if dist < 4.5:
                contacts.append((ab_a.get_parent(), ag_a.get_parent(), dist))

    if contacts:
        ab_residues = set()
        ag_residues = set()
        for ab_r, ag_r, d in contacts:
            ab_residues.add(f"{ab_r.get_parent().id}:{ab_r.get_resname()}{ab_r.get_id()[1]}")
            ag_residues.add(f"{ag_r.get_resname()}{ag_r.get_id()[1]}")

        print(f"\nInterface contacts: {len(contacts)}")
        print(f"Antibody paratope residues: {', '.join(sorted(ab_residues))}")
        print(f"Antigen epitope residues: {', '.join(sorted(ag_residues))}")
PYTHON
```

---

## Recipe 3: CDR Loop Confidence Analysis

Assess ColabFold confidence specifically at CDR loops — the most important regions for binding.

```python
import json

def cdr_confidence(scores_file, vh_length, cdr_regions):
    """
    Analyze pLDDT at CDR loops from ColabFold prediction.

    Args:
        scores_file: path to ColabFold scores JSON
        vh_length: length of VH chain (to offset VL positions)
        cdr_regions: dict mapping CDR name to (start, end) 0-indexed positions
            e.g., {"CDR-H1": (26, 35), "CDR-H2": (50, 65), "CDR-H3": (95, 102),
                   "CDR-L1": (24, 34), "CDR-L2": (50, 56), "CDR-L3": (89, 97)}
            VL positions are relative to VL chain start.
    """
    with open(scores_file) as f:
        scores = json.load(f)
    plddt = scores["plddt"]

    print("CDR Loop Confidence Analysis")
    print("=" * 55)
    print(f"{'CDR':<10} {'Residues':<12} {'Mean pLDDT':>10} {'Min pLDDT':>10} {'Status':<12}")
    print("-" * 55)

    for cdr_name, (start, end) in cdr_regions.items():
        # Offset VL CDRs by VH length + 1 (for chain break in ColabFold)
        if cdr_name.startswith("CDR-L"):
            offset = vh_length
        else:
            offset = 0

        region_plddt = plddt[offset + start : offset + end + 1]
        if not region_plddt:
            print(f"{cdr_name:<10} {'N/A':<12} {'N/A':>10} {'N/A':>10}")
            continue

        mean_p = sum(region_plddt) / len(region_plddt)
        min_p = min(region_plddt)

        if mean_p > 80:
            status = "CONFIDENT"
        elif mean_p > 60:
            status = "MODERATE"
        else:
            status = "LOW"

        print(f"{cdr_name:<10} {start}-{end:<8} {mean_p:>10.1f} {min_p:>10.1f} {status:<12}")

    # Overall framework confidence
    all_cdr_positions = set()
    for cdr_name, (start, end) in cdr_regions.items():
        offset = vh_length if cdr_name.startswith("CDR-L") else 0
        all_cdr_positions.update(range(offset + start, offset + end + 1))

    framework_plddt = [plddt[i] for i in range(len(plddt)) if i not in all_cdr_positions]
    cdr_plddt = [plddt[i] for i in all_cdr_positions if i < len(plddt)]

    print(f"\nFramework mean pLDDT: {sum(framework_plddt)/len(framework_plddt):.1f}")
    print(f"CDR mean pLDDT:       {sum(cdr_plddt)/len(cdr_plddt):.1f}")

# Usage with Kabat numbering approximate positions:
# cdr_confidence(
#     "fv_pred/antibody_scores_rank_001.json",
#     vh_length=120,  # adjust to actual VH length
#     cdr_regions={
#         "CDR-H1": (26, 35), "CDR-H2": (50, 65), "CDR-H3": (95, 102),
#         "CDR-L1": (24, 34), "CDR-L2": (50, 56), "CDR-L3": (89, 97),
#     }
# )
```

---

## Recipe 4: Humanization Variant Comparison

Compare ColabFold predictions of parental vs humanized antibody to check structural preservation.

```bash
# Predict both parental and humanized Fv
cat > humanization_variants.fasta << 'FASTA'
>parental_mouse
PARENTALVH:PARENTALVL
>humanized_v1
HUMANIZEDVH_V1:HUMANIZEDVL_V1
>humanized_v2
HUMANIZEDVH_V2:HUMANIZEDVL_V2
FASTA

colabfold_batch humanization_variants.fasta humanization/ \
  --model-type alphafold2_multimer_v3 \
  --num-models 3 \
  --num-recycle 10

# Compare all variants
python3 << 'PYTHON'
import json, glob, os

print("Humanization Variant Comparison")
print("=" * 65)
print(f"{'Variant':<25} {'pLDDT':>7} {'ipTM':>7} {'pTM':>7} {'Status':<15}")
print("-" * 65)

results = []
for f in sorted(glob.glob("humanization/*scores_rank_001*.json")):
    name = os.path.basename(f).split("_scores")[0]
    with open(f) as fh:
        scores = json.load(fh)
    plddt = scores["plddt"]
    results.append({
        "name": name,
        "plddt": sum(plddt) / len(plddt),
        "iptm": scores.get("iptm", 0),
        "ptm": scores.get("ptm", 0),
    })

# Use parental as reference
parental = results[0]
for r in results:
    delta_plddt = r["plddt"] - parental["plddt"]
    if abs(delta_plddt) < 3 and r["iptm"] > 0.7:
        status = "PRESERVED"
    elif delta_plddt < -5:
        status = "DESTABILIZED"
    else:
        status = "CHECK"
    print(f"{r['name']:<25} {r['plddt']:>7.1f} {r['iptm']:>7.3f} {r['ptm']:>7.3f} {status:<15}")

print(f"\nReference (parental): pLDDT {parental['plddt']:.1f}")
print("PRESERVED = pLDDT within 3 pts of parental + ipTM > 0.7")
PYTHON
```

---

## Recipe 5: Bispecific Format Validation

Predict structure of bispecific antibody formats (e.g., two scFvs linked).

```bash
# scFv1-linker-scFv2 as single chain, or VH1:VL1:VH2:VL2 as multimer
cat > bispecific.fasta << 'FASTA'
>tandem_scfv
VH1SEQUENCE:VL1SEQUENCE:VH2SEQUENCE:VL2SEQUENCE
FASTA

colabfold_batch bispecific.fasta bispecific_pred/ \
  --model-type alphafold2_multimer_v3 \
  --num-recycle 10 \
  --num-models 3

# Check that both Fv domains fold independently
python3 << 'PYTHON'
import json, glob

scores_file = sorted(glob.glob("bispecific_pred/*scores_rank_001*.json"))[0]
with open(scores_file) as f:
    scores = json.load(f)

plddt = scores["plddt"]
iptm = scores.get("iptm", 0)

print(f"Bispecific prediction:")
print(f"  Mean pLDDT: {sum(plddt)/len(plddt):.1f}")
print(f"  ipTM: {iptm:.3f}")

# Check for low-confidence linker/junction regions
low_runs = []
run_start = None
for i, p in enumerate(plddt):
    if p < 50 and run_start is None:
        run_start = i
    elif p >= 50 and run_start is not None:
        if i - run_start > 3:  # runs of 4+ low-confidence residues
            low_runs.append((run_start + 1, i))
        run_start = None

if low_runs:
    print(f"\nDisordered/flexible regions (pLDDT < 50):")
    for s, e in low_runs:
        print(f"  Residues {s}-{e} — likely linker or unstructured junction")
PYTHON
```
