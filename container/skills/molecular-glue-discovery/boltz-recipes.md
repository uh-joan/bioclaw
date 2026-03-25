# Boltz-2 Molecular Glue & Degrader Recipes

Recipes for ternary complex modeling and degrader optimization using Boltz-2. Boltz-2 uniquely predicts protein-ligand-protein ternary complexes with affinity, making it ideal for molecular glue and PROTAC design.

> **Parent skill**: [SKILL.md](SKILL.md) — full molecular glue discovery pipeline.
> **See also**: [boltz-predict skill](../boltz-predict/SKILL.md) — standalone Boltz-2 prediction with full CLI reference.

---

## Recipe 1: Molecular Glue Ternary Complex (E3:Substrate:Glue)

Predict the ternary complex of a molecular glue bridging an E3 ligase to a neosubstrate.

```bash
cat > glue_ternary.yaml << 'YAML'
version: 1
sequences:
  - protein:
      id: A
      sequence: MCRBNSEQUENCE
  - protein:
      id: B
      sequence: MNEOSUBSTRATESEQUENCE
  - ligand:
      id: C
      smiles: 'O=C1CCC(N2C(=O)c3ccccc3C2=O)C(=O)N1'
properties:
  - affinity:
      binder: C
YAML

boltz predict glue_ternary.yaml \
  --out_dir ternary_results/ \
  --diffusion_samples 10 \
  --recycling_steps 10 \
  --use_potentials \
  --use_msa_server \
  --output_format pdb

# Analyze ternary complex quality
python3 << 'PYTHON'
import json, glob

conf = json.load(open(sorted(glob.glob("ternary_results/predictions/*/confidence_*.json"))[0]))
aff = json.load(open(sorted(glob.glob("ternary_results/predictions/*/affinity_*.json"))[0]))

print("Molecular Glue Ternary Complex Analysis")
print("=" * 55)
print(f"Complex pLDDT:     {conf['complex_plddt']:.3f}")
print(f"Protein ipTM:      {conf['protein_iptm']:.3f}")
print(f"Ligand ipTM:       {conf['ligand_iptm']:.3f}")
print(f"Overall ipTM:      {conf['iptm']:.3f}")

# Key metric: E3-substrate interface (mediated by glue)
if "pair_chains_iptm" in conf:
    print("\nPairwise interface scores:")
    for pair, score in conf["pair_chains_iptm"].items():
        label = ""
        if "A" in pair and "B" in pair:
            label = " ← E3:substrate (KEY: cooperativity metric)"
        elif "A" in pair and "C" in pair:
            label = " ← E3:glue"
        elif "B" in pair and "C" in pair:
            label = " ← substrate:glue"
        print(f"  {pair}: {score:.3f}{label}")

print(f"\nGlue affinity: log10(IC50) = {aff['affinity_pred_value']:.2f} uM")
print(f"Binding probability: {aff['affinity_probability_binary']:.3f}")

# Assessment
e3_sub = [v for k, v in conf.get("pair_chains_iptm", {}).items() if "A" in k and "B" in k]
if e3_sub and e3_sub[0] > 0.4:
    print("\nVERDICT: Ternary complex forms — glue induces E3:substrate proximity")
elif e3_sub and e3_sub[0] > 0.2:
    print("\nVERDICT: Weak ternary complex — optimize glue for better cooperativity")
else:
    print("\nVERDICT: No ternary complex — glue does not bridge E3 and substrate")
PYTHON
```

---

## Recipe 2: PROTAC Ternary Complex

Model a PROTAC bifunctional molecule bridging E3 ligase and target protein.

```bash
cat > protac.yaml << 'YAML'
version: 1
sequences:
  - protein:
      id: A
      sequence: MVHLSEQUENCE
  - protein:
      id: B
      sequence: MTARGETPROTEINSEQUENCE
  - ligand:
      id: C
      smiles: 'PROTAC_SMILES_E3WARHEAD_LINKER_TARGETWARHEAD'
properties:
  - affinity:
      binder: C
YAML

boltz predict protac.yaml \
  --out_dir protac_results/ \
  --diffusion_samples 10 \
  --recycling_steps 10 \
  --use_potentials \
  --use_msa_server \
  --output_format pdb

# Assess PROTAC ternary complex
python3 << 'PYTHON'
import json, glob

conf = json.load(open(sorted(glob.glob("protac_results/predictions/*/confidence_*.json"))[0]))

print("PROTAC Ternary Complex Assessment")
print("=" * 50)

if "pair_chains_iptm" in conf:
    for pair, score in conf["pair_chains_iptm"].items():
        if "A" in pair and "B" in pair:
            print(f"E3-Target proximity (A-B): {score:.3f}")
            if score > 0.3:
                print("  Target is within ubiquitination distance")
            else:
                print("  WARNING: Target too far — linker length may be wrong")

# Check if linker allows productive geometry
print(f"\nOverall iptm: {conf['iptm']:.3f}")
print(f"Ligand ipTM: {conf['ligand_iptm']:.3f}")

if conf["iptm"] > 0.4:
    print("\nPRODUCTIVE TERNARY: Geometry supports ubiquitin transfer")
else:
    print("\nINACTIVE GEOMETRY: Consider different linker length or exit vector")
PYTHON
```

---

## Recipe 3: Neosubstrate Selectivity Screen

Screen multiple potential neosubstrates against E3 ligase + glue to predict selectivity.

```bash
python3 << 'PYTHON'
import os

neosubstrates = {
    "IKZF1": "MIKZF1SEQUENCE",
    "IKZF3": "MIKZF3SEQUENCE",
    "CK1a": "MCK1ASEQUENCE",
    "GSPT1": "MGSPT1SEQUENCE",
}

e3_seq = "MCRBNSEQUENCE"
glue_smiles = "O=C1CCC(N2C(=O)c3ccccc3C2=O)C(=O)N1"

os.makedirs("selectivity_screen/", exist_ok=True)
for name, sub_seq in neosubstrates.items():
    yaml = f"""version: 1
sequences:
  - protein:
      id: A
      sequence: {e3_seq}
  - protein:
      id: B
      sequence: {sub_seq}
  - ligand:
      id: C
      smiles: '{glue_smiles}'
properties:
  - affinity:
      binder: C
"""
    with open(f"selectivity_screen/{name}.yaml", "w") as f:
        f.write(yaml)
PYTHON

boltz predict selectivity_screen/ \
  --out_dir selectivity_results/ \
  --diffusion_samples 5 \
  --use_potentials \
  --use_msa_server \
  --output_format pdb

# Selectivity analysis
python3 << 'PYTHON'
import json, glob

print("Neosubstrate Selectivity Profile")
print("=" * 70)
print(f"{'Substrate':<15} {'E3:Sub ipTM':>12} {'Lig ipTM':>10} {'P(bind)':>8} {'Degraded?':<12}")
print("-" * 70)

for conf_file in sorted(glob.glob("selectivity_results/predictions/*/confidence_*.json")):
    name = conf_file.split("/")[-2]
    conf = json.load(open(conf_file))

    aff_file = glob.glob(f"selectivity_results/predictions/{name}/affinity_*.json")[0]
    aff = json.load(open(aff_file))

    e3_sub = 0
    if "pair_chains_iptm" in conf:
        for pair, score in conf["pair_chains_iptm"].items():
            if "A" in pair and "B" in pair:
                e3_sub = score

    degraded = "YES" if e3_sub > 0.35 and aff["affinity_probability_binary"] > 0.5 else "NO"
    print(f"{name:<15} {e3_sub:>12.3f} {conf['ligand_iptm']:>10.3f} "
          f"{aff['affinity_probability_binary']:>8.3f} {degraded}")
PYTHON
```

---

## Recipe 4: Glue SAR — Analog Series Comparison

Compare molecular glue analogs to optimize cooperativity and selectivity.

```bash
python3 << 'PYTHON'
import os

glue_analogs = {
    "lenalidomide": "O=C1CCC(N2C(=O)c3ccccc3C2=O)C(=O)N1",
    "pomalidomide": "O=C1CCC(N2C(=O)c3cc(N)ccc3C2=O)C(=O)N1",
    "thalidomide": "O=C1CCC(N2C(=O)c3ccccc3C2=O)C(=O)N1",
    "analog_1": "O=C1CCC(N2C(=O)c3cc(F)ccc3C2=O)C(=O)N1",
    "analog_2": "O=C1CCC(N2C(=O)c3cc(Cl)ccc3C2=O)C(=O)N1",
}

os.makedirs("glue_sar/", exist_ok=True)
for name, smiles in glue_analogs.items():
    yaml = f"""version: 1
sequences:
  - protein:
      id: A
      sequence: MCRBNSEQUENCE
  - protein:
      id: B
      sequence: MIKZF1SEQUENCE
  - ligand:
      id: C
      smiles: '{smiles}'
properties:
  - affinity:
      binder: C
"""
    with open(f"glue_sar/{name}.yaml", "w") as f:
        f.write(yaml)
PYTHON

boltz predict glue_sar/ \
  --out_dir sar_results/ \
  --diffusion_samples 5 \
  --use_potentials \
  --use_msa_server \
  --output_format pdb

python3 << 'PYTHON'
import json, glob

print("Molecular Glue SAR — Analog Comparison")
print("=" * 65)
print(f"{'Analog':<20} {'Cooperativity':>13} {'Affinity':>10} {'P(bind)':>8}")
print("-" * 65)

for aff_file in sorted(glob.glob("sar_results/predictions/*/affinity_*.json")):
    name = aff_file.split("/")[-2]
    aff = json.load(open(aff_file))
    conf = json.load(open(glob.glob(f"sar_results/predictions/{name}/confidence_*.json")[0]))

    e3_sub = 0
    if "pair_chains_iptm" in conf:
        for pair, score in conf["pair_chains_iptm"].items():
            if "A" in pair and "B" in pair:
                e3_sub = score

    print(f"{name:<20} {e3_sub:>13.3f} {aff['affinity_pred_value']:>10.2f} "
          f"{aff['affinity_probability_binary']:>8.3f}")
PYTHON
```
