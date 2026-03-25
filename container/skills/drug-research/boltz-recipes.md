# Boltz-2 Drug Research Recipes

Recipes for structural and affinity prediction in drug research workflows using Boltz-2. Complements the drug research pipeline in [SKILL.md](SKILL.md) by adding ligand docking, binding affinity prediction, and structural characterization of drug-target interactions.

> **Parent skill**: [SKILL.md](SKILL.md) — full drug research report pipeline.
> **See also**: [boltz-predict skill](../boltz-predict/SKILL.md) — standalone Boltz-2 prediction with full CLI reference.

---

## Recipe 1: Drug-Target Binding Pose + Affinity

After gathering compound and target data from MCP tools, predict how the drug binds and estimate potency.

```bash
# After retrieving target sequence from UniProt and drug SMILES from PubChem/ChEMBL
cat > drug_target.yaml << 'YAML'
version: 1
sequences:
  - protein:
      id: A
      sequence: MTARGETPROTEINSEQUENCE
  - ligand:
      id: B
      smiles: 'DRUG_SMILES_FROM_PUBCHEM'
properties:
  - affinity:
      binder: B
YAML

boltz predict drug_target.yaml \
  --out_dir drug_binding/ \
  --diffusion_samples 5 \
  --recycling_steps 10 \
  --use_msa_server \
  --use_potentials \
  --output_format pdb \
  --diffusion_samples_affinity 5

# Extract for drug report Section 3 (Mechanism) and Section 5 (ADMET context)
python3 << 'PYTHON'
import json, glob

conf = json.load(open(sorted(glob.glob("drug_binding/predictions/*/confidence_*.json"))[0]))
aff = json.load(open(sorted(glob.glob("drug_binding/predictions/*/affinity_*.json"))[0]))

print("Drug-Target Structural Analysis (for Report Sections 3-4)")
print("=" * 60)
print(f"Binding confidence (ligand ipTM): {conf['ligand_iptm']:.3f}")
print(f"Complex pLDDT: {conf['complex_plddt']:.3f}")
print(f"Predicted IC50: {10**(aff['affinity_pred_value']+3):.0f} nM (log10={aff['affinity_pred_value']:.2f} uM)")
print(f"Binding probability: {aff['affinity_probability_binary']:.3f}")
print()
print("For report:")
print(f"  Section 3 (MoA): Drug binds target with {'high' if conf['ligand_iptm'] > 0.5 else 'moderate' if conf['ligand_iptm'] > 0.3 else 'low'} confidence")
print(f"  Section 4 (Targets): Predicted potency ~{10**(aff['affinity_pred_value']+3):.0f} nM")
PYTHON
```

---

## Recipe 2: Investigational Drug — Structure When No Crystal Exists

For investigational compounds with no experimental co-crystal structure, predict the binding mode.

```bash
# Use development code to search for sequence and SMILES via MCP tools
# Example: LY3437943 (tirzepatide analog)

cat > investigational.yaml << 'YAML'
version: 1
sequences:
  - protein:
      id: A
      sequence: MRECEPTORSEQUENCE
  - ligand:
      id: B
      smiles: 'INVESTIGATIONAL_COMPOUND_SMILES'
constraints:
  - pocket:
      binder: B
      contacts:
        - [A, 120]   # Known binding pocket residues from literature
        - [A, 145]
        - [A, 200]
        - [A, 267]
      max_distance: 8.0
properties:
  - affinity:
      binder: B
YAML

boltz predict investigational.yaml \
  --out_dir investigational_results/ \
  --diffusion_samples 10 \
  --use_potentials \
  --use_msa_server \
  --output_format pdb
```

---

## Recipe 3: Competitive Drug Comparison (Section 11)

Compare binding poses and affinities of multiple drugs against the same target for the Comparative Analysis section.

```bash
mkdir -p competitive_inputs/

python3 << 'PYTHON'
# Drugs from ChEMBL/DrugBank for the same target
drugs = {
    "drug_approved": "SMILES_OF_APPROVED_DRUG",
    "drug_phase3": "SMILES_OF_PHASE3_COMPOUND",
    "drug_subject": "SMILES_OF_COMPOUND_BEING_RESEARCHED",
}

target_seq = "MTARGETSEQUENCE"
pocket = [120, 145, 200, 267]  # shared binding site

for name, smiles in drugs.items():
    contacts = "\n".join(f"        - [A, {r}]" for r in pocket)
    yaml = f"""version: 1
sequences:
  - protein:
      id: A
      sequence: {target_seq}
  - ligand:
      id: B
      smiles: '{smiles}'
constraints:
  - pocket:
      binder: B
      contacts:
{contacts}
      max_distance: 6.0
properties:
  - affinity:
      binder: B
"""
    with open(f"competitive_inputs/{name}.yaml", "w") as f:
        f.write(yaml)
PYTHON

boltz predict competitive_inputs/ \
  --out_dir competitive_results/ \
  --diffusion_samples 5 \
  --use_msa_server \
  --output_format pdb

# Rank for Section 11 (Comparative Analysis)
python3 << 'PYTHON'
import json, glob

print("Competitive Binding Comparison (Report Section 11)")
print("=" * 70)
print(f"{'Drug':<25} {'IC50 (nM)':>10} {'P(bind)':>8} {'Lig ipTM':>9} {'Rank':<5}")
print("-" * 70)

results = []
for aff_file in sorted(glob.glob("competitive_results/predictions/*/affinity_*.json")):
    name = aff_file.split("/")[-2]
    aff = json.load(open(aff_file))
    conf_file = glob.glob(f"competitive_results/predictions/{name}/confidence_*.json")[0]
    conf = json.load(open(conf_file))
    results.append({
        "name": name,
        "ic50_nm": 10**(aff["affinity_pred_value"]+3),
        "prob": aff["affinity_probability_binary"],
        "lig_iptm": conf["ligand_iptm"],
    })

results.sort(key=lambda r: r["ic50_nm"])
for i, r in enumerate(results, 1):
    print(f"{r['name']:<25} {r['ic50_nm']:>10.0f} {r['prob']:>8.3f} {r['lig_iptm']:>9.3f} #{i}")
PYTHON
```

---

## Recipe 4: Drug with Known Covalent Mechanism

For drugs that bind covalently (e.g., osimertinib, ibrutinib), predict the covalent binding mode.

```bash
cat > covalent_drug.yaml << 'YAML'
version: 1
sequences:
  - protein:
      id: A
      sequence: MEGFRSEQUENCE
  - ligand:
      id: B
      smiles: 'COc1cc2ncnc(Nc3ccc(F)c(Cl)c3)c2cc1NC(=O)/C=C/CN(C)C'
constraints:
  - bond:
      - [A, 797, SG]     # EGFR Cys797
      - [B, 1, C18]       # Acrylamide warhead carbon
YAML

boltz predict covalent_drug.yaml \
  --out_dir covalent_results/ \
  --diffusion_samples 5 \
  --use_potentials \
  --use_msa_server \
  --output_format pdb
```
