# ColabFold Enzyme Engineering Recipes

Recipes for validating engineered enzyme variants using ColabFold structure prediction. Predict mutant structures and compare to wildtype for stability screening, active site geometry validation, and directed evolution library analysis.

> **Parent skill**: [SKILL.md](SKILL.md) — full enzyme engineering pipeline.
> **See also**: [colabfold-predict skill](../colabfold-predict/SKILL.md) — standalone ColabFold prediction skill with full CLI reference.

---

## Recipe 1: Mutant Stability Screening (Wildtype vs Variants)

Predict structures for wildtype and mutant enzymes, then compare pLDDT profiles to identify destabilizing mutations.

```bash
# Create FASTA with wildtype and mutants
cat > enzyme_variants.fasta << 'FASTA'
>wildtype_lipase
MWILDTYPESEQUENCEHERE
>T47A
MWILDTYPESEQUENCEHERE_WITH_T47A_SUBSTITUTION
>L112F
MWILDTYPESEQUENCEHERE_WITH_L112F_SUBSTITUTION
>G89P_thermostable
MWILDTYPESEQUENCEHERE_WITH_G89P_SUBSTITUTION
FASTA

# Quick screen all variants (1 model each)
colabfold_batch enzyme_variants.fasta stability_screen/ --num-models 1 --num-recycle 5

# Compare stability profiles
python3 << 'PYTHON'
import json, glob, os

variants = {}
for f in sorted(glob.glob("stability_screen/*scores_rank_001*.json")):
    name = os.path.basename(f).split("_scores")[0]
    with open(f) as fh:
        scores = json.load(fh)
    plddt = scores["plddt"]
    variants[name] = {
        "plddt": plddt,
        "mean": sum(plddt) / len(plddt),
        "ptm": scores.get("ptm", 0),
    }

# Find wildtype (first entry)
wt_name = list(variants.keys())[0]
wt = variants[wt_name]

print("Enzyme Mutant Stability Screen")
print("=" * 70)
print(f"Wildtype: {wt_name} (mean pLDDT {wt['mean']:.1f}, pTM {wt['ptm']:.3f})")
print()
print(f"{'Variant':<30} {'pLDDT':>7} {'Delta':>7} {'pTM':>7} {'Assessment':<18}")
print("-" * 70)

for name, v in variants.items():
    delta = v["mean"] - wt["mean"]
    if delta > 2:
        assessment = "STABILIZING"
    elif delta > -3:
        assessment = "NEUTRAL"
    elif delta > -8:
        assessment = "MILDLY DESTAB."
    else:
        assessment = "DESTABILIZING"

    marker = " ***" if assessment == "STABILIZING" else ""
    print(f"{name:<30} {v['mean']:>7.1f} {delta:>+7.1f} {v['ptm']:>7.3f} {assessment}{marker}")

# Per-residue pLDDT delta analysis
print(f"\nPer-Residue Destabilization Hotspots (|delta pLDDT| > 15):")
print("-" * 70)
for name, v in list(variants.items())[1:]:  # skip wildtype
    n = min(len(v["plddt"]), len(wt["plddt"]))
    hotspots = []
    for i in range(n):
        d = v["plddt"][i] - wt["plddt"][i]
        if abs(d) > 15:
            hotspots.append((i + 1, d))
    if hotspots:
        spots = ", ".join(f"res {pos} ({delta:+.0f})" for pos, delta in hotspots)
        print(f"  {name}: {spots}")
    else:
        print(f"  {name}: no major local destabilization")
PYTHON
```

**Decision criteria:**
- Delta pLDDT > +2 → **Potentially stabilizing** — prioritize for experimental testing
- Delta pLDDT -3 to +2 → **Neutral** — mutation tolerated structurally
- Delta pLDDT -3 to -8 → **Mildly destabilizing** — test only if activity gain justifies it
- Delta pLDDT < -8 → **Destabilizing** — discard unless rescuable with compensating mutations

---

## Recipe 2: Active Site Geometry Validation

After rational design of active site mutations, verify that the catalytic residues maintain proper geometry in the predicted structure.

```bash
# Predict mutant structure
cat > active_site_mutant.fasta << 'FASTA'
>lipase_W104H_S153A
MMUTANTSEQUENCEHERE
FASTA

colabfold_batch active_site_mutant.fasta active_site_pred/ --num-models 5 --num-recycle 10

# Validate active site geometry
python3 << 'PYTHON'
from Bio.PDB import PDBParser
import glob, math

def distance(a1, a2):
    """Euclidean distance between two atoms."""
    d = a1.get_vector() - a2.get_vector()
    return d.norm()

def angle(a1, a2, a3):
    """Angle at a2 between a1-a2-a3 in degrees."""
    v1 = a1.get_vector() - a2.get_vector()
    v2 = a3.get_vector() - a2.get_vector()
    cos_angle = (v1 * v2) / (v1.norm() * v2.norm())
    cos_angle = max(-1.0, min(1.0, cos_angle))
    return math.degrees(math.acos(cos_angle))

parser = PDBParser(QUIET=True)

# Define catalytic residues (adjust for your enzyme)
# Example: serine hydrolase catalytic triad (Ser-His-Asp)
catalytic_residues = {
    "Ser": 153,   # nucleophile
    "His": 263,   # base
    "Asp": 217,   # acid
}

# Also check oxyanion hole residues if relevant
oxyanion_residues = [82, 153]  # backbone NH stabilizes tetrahedral intermediate

print("Active Site Geometry Validation")
print("=" * 60)

# Analyze each model
for pdb_file in sorted(glob.glob("active_site_pred/*rank_00*.pdb"))[:3]:
    structure = parser.get_structure("mut", pdb_file)
    residues = {r.get_id()[1]: r for r in structure[0].get_residues()}
    model_name = pdb_file.split("/")[-1].split(".")[0]

    print(f"\n{model_name}:")

    # Catalytic triad distances
    ser = residues.get(catalytic_residues["Ser"])
    his = residues.get(catalytic_residues["His"])
    asp = residues.get(catalytic_residues["Asp"])

    if ser and his and asp:
        # Ser OG - His NE2 distance (should be ~2.6-3.2 A for H-bond)
        try:
            ser_og = ser["OG"] if "OG" in ser else ser["CB"]
            his_ne2 = his["NE2"] if "NE2" in his else his["CB"]
            asp_od1 = asp["OD1"] if "OD1" in asp else asp["CB"]

            d_ser_his = distance(ser_og, his_ne2)
            d_his_asp = distance(his_ne2, asp_od1)
            a_triad = angle(ser_og, his_ne2, asp_od1)

            print(f"  Ser{catalytic_residues['Ser']}-His{catalytic_residues['His']}: {d_ser_his:.2f} A "
                  f"{'OK' if 2.4 < d_ser_his < 3.5 else 'WARNING'}")
            print(f"  His{catalytic_residues['His']}-Asp{catalytic_residues['Asp']}: {d_his_asp:.2f} A "
                  f"{'OK' if 2.4 < d_his_asp < 3.5 else 'WARNING'}")
            print(f"  Triad angle: {a_triad:.1f} deg "
                  f"{'OK' if 90 < a_triad < 150 else 'WARNING: unusual geometry'}")
        except KeyError as e:
            print(f"  Missing atom: {e} — check residue identity")
    else:
        missing = [n for n, r in catalytic_residues.items() if residues.get(r) is None]
        print(f"  WARNING: Catalytic residue(s) not found: {missing}")

# Reference distances from wildtype (update with your values)
print("\nReference (wildtype expected):")
print("  Ser-His: 2.6-3.2 A (hydrogen bond)")
print("  His-Asp: 2.6-3.2 A (hydrogen bond)")
print("  Triad angle: 100-140 deg")
PYTHON
```

---

## Recipe 3: Directed Evolution Library Structural Analysis

After a round of directed evolution, predict structures for beneficial hits to understand structural basis of improvement.

```bash
# Top hits from screening
cat > evo_round2_hits.fasta << 'FASTA'
>parent_round1
MPARENTSEQUENCEHERE
>hit_A3_2x_activity
MHITSEQUENCE_A3_HERE
>hit_B7_thermostable
MHITSEQUENCE_B7_HERE
>hit_C2_broad_substrate
MHITSEQUENCE_C2_HERE
FASTA

colabfold_batch evo_round2_hits.fasta evo_structures/ --num-models 3 --num-recycle 5

# Structural comparison of hits vs parent
python3 << 'PYTHON'
import json, glob, os
from Bio.PDB import PDBParser, Superimposer

parser = PDBParser(QUIET=True)

# Load all predictions
structures = {}
scores = {}
for f in sorted(glob.glob("evo_structures/*scores_rank_001*.json")):
    name = os.path.basename(f).split("_scores")[0]
    with open(f) as fh:
        scores[name] = json.load(fh)
    pdb_file = f.replace("_scores_rank_001", "_unrelaxed_rank_001").replace(".json", ".pdb")
    if not os.path.exists(pdb_file):
        pdb_candidates = glob.glob(f"evo_structures/{name}*rank_001*.pdb")
        pdb_file = pdb_candidates[0] if pdb_candidates else None
    if pdb_file:
        structures[name] = parser.get_structure(name, pdb_file)

names = list(scores.keys())
parent_name = names[0]
parent_plddt = scores[parent_name]["plddt"]

print("Directed Evolution Structural Analysis")
print("=" * 70)
print(f"Parent: {parent_name} (pLDDT {sum(parent_plddt)/len(parent_plddt):.1f})")
print()

for name in names[1:]:
    hit_plddt = scores[name]["plddt"]
    n = min(len(parent_plddt), len(hit_plddt))

    # Global metrics
    delta_plddt = sum(hit_plddt[:n])/n - sum(parent_plddt[:n])/n

    # RMSD to parent
    rmsd = "N/A"
    if name in structures and parent_name in structures:
        parent_cas = [a for a in structures[parent_name].get_atoms() if a.get_name() == "CA"]
        hit_cas = [a for a in structures[name].get_atoms() if a.get_name() == "CA"]
        m = min(len(parent_cas), len(hit_cas))
        if m > 10:
            sup = Superimposer()
            sup.set_atoms(parent_cas[:m], hit_cas[:m])
            rmsd = f"{sup.rms:.2f}"

    print(f"{name}:")
    print(f"  Mean pLDDT: {sum(hit_plddt)/len(hit_plddt):.1f} (delta {delta_plddt:+.1f})")
    print(f"  CA RMSD to parent: {rmsd} A")

    # Find regions that changed most
    changes = []
    window = 5  # sliding window
    for i in range(0, n - window):
        local_delta = sum(hit_plddt[i:i+window])/window - sum(parent_plddt[i:i+window])/window
        if abs(local_delta) > 10:
            changes.append((i+1, i+window, local_delta))

    if changes:
        print(f"  Structural changes (|delta pLDDT| > 10):")
        for start, end, d in changes:
            direction = "stabilized" if d > 0 else "destabilized"
            print(f"    Residues {start}-{end}: {direction} ({d:+.1f})")
    print()
PYTHON
```

---

## Recipe 4: Thermostability Prediction via Conformational Rigidity

Use ColabFold's pLDDT as a proxy for local rigidity — higher pLDDT correlates with more rigid, often more thermostable regions. Compare mesophilic and designed thermostable variants.

```bash
cat > thermo_comparison.fasta << 'FASTA'
>mesophilic_parent
MMESOPHILICSEQUENCE
>designed_thermostable
MTHERMOSTABLESEQUENCE
FASTA

colabfold_batch thermo_comparison.fasta thermo_pred/ --num-models 3 --num-recycle 10

python3 << 'PYTHON'
import json, glob, os

variants = {}
for f in sorted(glob.glob("thermo_pred/*scores_rank_001*.json")):
    name = os.path.basename(f).split("_scores")[0]
    with open(f) as fh:
        scores = json.load(fh)
    variants[name] = scores["plddt"]

names = list(variants.keys())
meso = variants[names[0]]
thermo = variants[names[1]]
n = min(len(meso), len(thermo))

print("Thermostability Structural Comparison")
print("=" * 60)
print(f"Mesophilic:   mean pLDDT {sum(meso)/len(meso):.1f}")
print(f"Thermostable: mean pLDDT {sum(thermo)/len(thermo):.1f}")
print(f"Delta:        {sum(thermo[:n])/n - sum(meso[:n])/n:+.1f}")
print()

# Identify regions where thermostable variant is more rigid
print("Regions rigidified in thermostable variant (delta pLDDT > +5):")
window = 7
for i in range(0, n - window):
    d = sum(thermo[i:i+window])/window - sum(meso[i:i+window])/window
    if d > 5:
        print(f"  Residues {i+1}-{i+window}: +{d:.1f} pLDDT (rigidified)")

# Identify regions that became more flexible (potential concern)
print("\nRegions destabilized in thermostable variant (delta pLDDT < -5):")
found = False
for i in range(0, n - window):
    d = sum(thermo[i:i+window])/window - sum(meso[i:i+window])/window
    if d < -5:
        print(f"  Residues {i+1}-{i+window}: {d:.1f} pLDDT (more flexible)")
        found = True
if not found:
    print("  None — thermostable design preserved or improved all regions")

# B-factor-like summary per secondary structure region
print(f"\nOverall: {'GOOD' if sum(thermo)/len(thermo) > sum(meso)/len(meso) else 'CHECK'}"
      f" — thermostable variant {'more' if sum(thermo)/len(thermo) > sum(meso)/len(meso) else 'less'}"
      f" rigid by pLDDT")
PYTHON
```

---

## Recipe 5: Substrate Channel / Tunnel Validation

After engineering mutations near the substrate access channel, verify the tunnel geometry is preserved.

```python
from Bio.PDB import PDBParser, NeighborSearch
import glob

def validate_channel(pdb_file, channel_residues, min_clearance=4.0):
    """
    Check that substrate channel residues maintain adequate clearance.

    Args:
        pdb_file: ColabFold predicted PDB
        channel_residues: list of residue numbers lining the channel
        min_clearance: minimum CA-CA distance (A) for channel patency
    """
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("enzyme", pdb_file)
    residues = {r.get_id()[1]: r for r in structure[0].get_residues()}

    print(f"Substrate Channel Validation: {pdb_file}")
    print("=" * 55)

    # Check pairwise distances between channel-lining residues
    channel_cas = []
    for rnum in channel_residues:
        if rnum in residues and "CA" in residues[rnum]:
            channel_cas.append((rnum, residues[rnum]["CA"]))

    constrictions = []
    for i, (r1, a1) in enumerate(channel_cas):
        for r2, a2 in channel_cas[i+1:]:
            dist = a1 - a2
            if dist < min_clearance and abs(r1 - r2) > 3:  # not sequential neighbors
                constrictions.append((r1, r2, dist))

    if constrictions:
        print("CONSTRICTIONS DETECTED:")
        for r1, r2, d in sorted(constrictions, key=lambda x: x[2]):
            print(f"  Res {r1} - Res {r2}: {d:.2f} A (< {min_clearance} A)")
        print("\nWARNING: Channel may be occluded — review mutations near these residues")
    else:
        print(f"All channel residues maintain > {min_clearance} A clearance")
        print("Channel geometry: PRESERVED")

# Usage:
# validate_channel(
#     "active_site_pred/mutant_unrelaxed_rank_001.pdb",
#     channel_residues=[45, 78, 82, 109, 153, 156, 217, 263],
#     min_clearance=4.0
# )
```
