# Boltz-2 Binder Discovery Recipes

Recipes for structure-based virtual screening and hit-to-lead optimization using Boltz-2. Complements the binder discovery pipeline in [SKILL.md](SKILL.md) by adding docking, affinity prediction, and pocket-conditioned screening.

> **Parent skill**: [SKILL.md](SKILL.md) — full binder discovery cascade.
> **See also**: [boltz-predict skill](../boltz-predict/SKILL.md) — standalone Boltz-2 prediction with full CLI reference.

---

## Recipe 1: Hit Discovery — Screen Compound Library

After mining hits from ChEMBL/PubChem via MCP tools, dock all candidates and rank by binding probability.

```bash
# Generate docking inputs from MCP-retrieved compounds
python3 << 'PYTHON'
import os

# Compounds from ChEMBL bioactivity search + PubChem similarity expansion
compounds = {
    "CHEMBL_hit1": "Cc1ccc(NC(=O)c2ccncc2)cc1",
    "CHEMBL_hit2": "O=C(Nc1ccccc1)c1ccc(F)cc1",
    "PubChem_analog1": "Cc1cc(NC(=O)c2ccncc2)ccc1O",
    "PubChem_analog2": "O=C(Nc1ccc(F)cc1)c1ccc(Cl)cc1",
    "scaffold_hop1": "O=C(Nc1ccccc1)c1ccco1",
}

target_seq = "MTARGETSEQUENCE"
# Pocket residues from PDB co-crystal or literature
pocket = [45, 78, 82, 109, 153, 156]

os.makedirs("hit_screen/", exist_ok=True)
for name, smiles in compounds.items():
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
    with open(f"hit_screen/{name}.yaml", "w") as f:
        f.write(yaml)
print(f"Generated {len(compounds)} screening inputs")
PYTHON

# Batch dock (quick mode for screening)
boltz predict hit_screen/ \
  --out_dir hit_results/ \
  --diffusion_samples 1 \
  --recycling_steps 3 \
  --use_msa_server \
  --output_format pdb

# Rank hits
python3 << 'PYTHON'
import json, glob

results = []
for aff_file in sorted(glob.glob("hit_results/predictions/*/affinity_*.json")):
    name = aff_file.split("/")[-2]
    aff = json.load(open(aff_file))
    conf_file = glob.glob(f"hit_results/predictions/{name}/confidence_*.json")[0]
    conf = json.load(open(conf_file))

    results.append({
        "name": name,
        "ic50_nm": 10**(aff["affinity_pred_value"]+3),
        "prob": aff["affinity_probability_binary"],
        "lig_iptm": conf["ligand_iptm"],
        "plddt": conf["complex_plddt"],
    })

results.sort(key=lambda r: -r["prob"])

print("Hit Discovery Screen — Ranked by Binding Probability")
print("=" * 75)
print(f"{'Compound':<25} {'P(bind)':>8} {'IC50 nM':>10} {'Lig ipTM':>9} {'pLDDT':>7} {'Call':<10}")
print("-" * 75)
for r in results:
    if r["prob"] > 0.7 and r["lig_iptm"] > 0.4:
        call = "HIT ***"
    elif r["prob"] > 0.5:
        call = "POSSIBLE"
    else:
        call = "INACTIVE"
    print(f"{r['name']:<25} {r['prob']:>8.3f} {r['ic50_nm']:>10.0f} {r['lig_iptm']:>9.3f} {r['plddt']:>7.3f} {call}")

hits = [r for r in results if r["prob"] > 0.5 and r["lig_iptm"] > 0.3]
print(f"\nConfirmed hits: {len(hits)}/{len(results)}")
print("Next: re-dock hits with --diffusion_samples 10 for high-quality poses")
PYTHON
```

---

## Recipe 2: Hit-to-Lead Affinity Ranking

After identifying hits, re-dock with high-quality settings and rank by predicted potency for lead selection.

```bash
# Re-dock confirmed hits with more samples
boltz predict confirmed_hits/ \
  --out_dir lead_ranking/ \
  --diffusion_samples 10 \
  --recycling_steps 10 \
  --use_potentials \
  --use_msa_server \
  --output_format pdb \
  --diffusion_samples_affinity 5 \
  --affinity_mw_correction

# Rank by affinity for lead selection
python3 << 'PYTHON'
import json, glob

results = []
for aff_file in sorted(glob.glob("lead_ranking/predictions/*/affinity_*.json")):
    name = aff_file.split("/")[-2]
    aff = json.load(open(aff_file))
    conf_file = glob.glob(f"lead_ranking/predictions/{name}/confidence_*.json")[0]
    conf = json.load(open(conf_file))

    results.append({
        "name": name,
        "ic50_nm": 10**(aff["affinity_pred_value"]+3),
        "log_ic50": aff["affinity_pred_value"],
        "prob": aff["affinity_probability_binary"],
        "lig_iptm": conf["ligand_iptm"],
    })

results.sort(key=lambda r: r["ic50_nm"])

print("Hit-to-Lead Ranking — by Predicted Potency")
print("=" * 65)
print(f"{'Rank':<5} {'Compound':<25} {'IC50 (nM)':>10} {'P(bind)':>8} {'Lig ipTM':>9}")
print("-" * 65)
for i, r in enumerate(results, 1):
    print(f"{i:<5} {r['name']:<25} {r['ic50_nm']:>10.0f} {r['prob']:>8.3f} {r['lig_iptm']:>9.3f}")

if results:
    lead = results[0]
    print(f"\nRecommended lead: {lead['name']} (IC50 ≈ {lead['ic50_nm']:.0f} nM)")
PYTHON
```

---

## Recipe 3: Scaffold Hopping Validation

After generating scaffold hops via PubChem similarity search, validate that new scaffolds maintain binding.

```bash
# Write YAML for each scaffold variant with same pocket
python3 << 'PYTHON'
import os

scaffolds = {
    "original_pyridine": "O=C(Nc1ccccc1)c1ccncc1",
    "hop_furan": "O=C(Nc1ccccc1)c1ccco1",
    "hop_thiophene": "O=C(Nc1ccccc1)c1cccs1",
    "hop_pyrimidine": "O=C(Nc1ccccc1)c1ccncn1",
    "hop_indole": "O=C(Nc1ccccc1)c1cc2ccccc2[nH]1",
}

target_seq = "MTARGETSEQUENCE"
pocket = [45, 78, 82, 109, 153]

os.makedirs("scaffold_hops/", exist_ok=True)
for name, smiles in scaffolds.items():
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
    with open(f"scaffold_hops/{name}.yaml", "w") as f:
        f.write(yaml)
PYTHON

boltz predict scaffold_hops/ \
  --out_dir hop_results/ \
  --diffusion_samples 5 \
  --use_potentials \
  --use_msa_server \
  --output_format pdb

# Compare scaffolds
python3 << 'PYTHON'
import json, glob

print("Scaffold Hopping Validation")
print("=" * 70)
print(f"{'Scaffold':<25} {'IC50 nM':>10} {'P(bind)':>8} {'Lig ipTM':>9} {'vs Orig':>8}")
print("-" * 70)

results = {}
for aff_file in sorted(glob.glob("hop_results/predictions/*/affinity_*.json")):
    name = aff_file.split("/")[-2]
    aff = json.load(open(aff_file))
    conf_file = glob.glob(f"hop_results/predictions/{name}/confidence_*.json")[0]
    conf = json.load(open(conf_file))
    results[name] = {
        "ic50": 10**(aff["affinity_pred_value"]+3),
        "prob": aff["affinity_probability_binary"],
        "lig_iptm": conf["ligand_iptm"],
    }

orig = results.get("original_pyridine", list(results.values())[0])
for name, r in results.items():
    ratio = r["ic50"] / orig["ic50"] if orig["ic50"] > 0 else 0
    status = f"{ratio:.1f}x" if ratio >= 1 else f"{1/ratio:.1f}x better"
    print(f"{name:<25} {r['ic50']:>10.0f} {r['prob']:>8.3f} {r['lig_iptm']:>9.3f} {status:>8}")
PYTHON
```

---

## Recipe 4: ADMET-Filtered Docking Prioritization

After ADMET filtering (from MCP data), dock the surviving compounds to confirm structural binding.

```bash
# Compounds that passed ADMET filters from the binder discovery pipeline
# Now validate with structural docking before experimental testing

boltz predict admet_passed/ \
  --out_dir docking_validation/ \
  --diffusion_samples 5 \
  --recycling_steps 10 \
  --use_potentials \
  --use_msa_server \
  --output_format pdb

# Final prioritization combining ADMET + docking
python3 << 'PYTHON'
import json, glob

print("Final Compound Prioritization (ADMET + Docking)")
print("=" * 55)

results = []
for conf_file in sorted(glob.glob("docking_validation/predictions/*/confidence_*.json")):
    name = conf_file.split("/")[-2]
    conf = json.load(open(conf_file))

    aff_files = glob.glob(f"docking_validation/predictions/{name}/affinity_*.json")
    aff = json.load(open(aff_files[0])) if aff_files else {}

    results.append({
        "name": name,
        "lig_iptm": conf["ligand_iptm"],
        "prob": aff.get("affinity_probability_binary", 0),
        "ic50_nm": 10**(aff["affinity_pred_value"]+3) if aff.get("affinity_pred_value") else None,
    })

# Tier compounds: ADMET passed + structurally validated
for r in results:
    if r["lig_iptm"] > 0.4 and r["prob"] > 0.6:
        r["tier"] = "PRIORITY 1 — test first"
    elif r["lig_iptm"] > 0.3 or r["prob"] > 0.5:
        r["tier"] = "PRIORITY 2 — backup"
    else:
        r["tier"] = "DEPRIORITIZE — weak binding"

results.sort(key=lambda r: (-r["prob"], -r["lig_iptm"]))
for r in results:
    ic50 = f"{r['ic50_nm']:.0f} nM" if r["ic50_nm"] else "N/A"
    print(f"  {r['name']}: {r['tier']} (IC50≈{ic50})")
PYTHON
```
