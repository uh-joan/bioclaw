# Boltz-2 Protein Therapeutic Design Recipes

Recipes for validating designed protein therapeutics using Boltz-2. Complements the design pipeline in [SKILL.md](SKILL.md) with ligand-aware complex prediction, template-forced validation, and binding affinity estimation.

> **Parent skill**: [SKILL.md](SKILL.md) — full protein therapeutic design pipeline.
> **See also**: [boltz-predict skill](../boltz-predict/SKILL.md) — standalone Boltz-2 prediction with full CLI reference.

---

## Recipe 1: Designed Binder + Ligand Complex Validation

After designing a protein binder (via RFdiffusion/ProteinMPNN), predict the full ternary complex: designed binder + target + small-molecule ligand occupying the active site.

```bash
cat > binder_ligand.yaml << 'YAML'
version: 1
sequences:
  - protein:
      id: A
      sequence: MDESIGNEDBINDERSEQUENCE
  - protein:
      id: B
      sequence: MTARGETPROTEINSEQUENCE
  - ligand:
      id: C
      smiles: 'LIGAND_SMILES_IN_ACTIVE_SITE'
YAML

boltz predict binder_ligand.yaml \
  --out_dir binder_validation/ \
  --diffusion_samples 10 \
  --recycling_steps 10 \
  --use_potentials \
  --use_msa_server \
  --output_format pdb

python3 << 'PYTHON'
import json, glob

conf = json.load(open(sorted(glob.glob("binder_validation/predictions/*/confidence_*.json"))[0]))

print("Designed Binder + Target + Ligand Complex")
print("=" * 55)
print(f"Complex pLDDT:  {conf['complex_plddt']:.3f}")
print(f"Protein ipTM:   {conf['protein_iptm']:.3f}")
print(f"Ligand ipTM:    {conf['ligand_iptm']:.3f}")

if "pair_chains_iptm" in conf:
    for pair, score in conf["pair_chains_iptm"].items():
        if "A" in pair and "B" in pair:
            print(f"\nBinder-Target interface: {score:.3f}")
            if score > 0.6:
                print("  CONFIDENT: Designed binder engages target as intended")
            elif score > 0.3:
                print("  MODERATE: Some binding, may need interface optimization")
            else:
                print("  WEAK: Binder does not engage target — redesign needed")
PYTHON
```

---

## Recipe 2: Template-Forced Design Validation

Validate a designed protein by forcing the backbone to stay near the design target, then checking if the predicted structure is consistent.

```bash
# Save design target as CIF/PDB first
cat > template_forced.yaml << 'YAML'
version: 1
sequences:
  - protein:
      id: A
      sequence: MDESIGNEDSEQUENCE
      templates:
        - cif_path: design_target.cif
          chain_id: A
          force: true
          threshold: 2.0
YAML

boltz predict template_forced.yaml \
  --out_dir template_results/ \
  --diffusion_samples 5 \
  --use_potentials \
  --output_format pdb

# Compare forced vs free prediction
cat > free_pred.yaml << 'YAML'
version: 1
sequences:
  - protein:
      id: A
      sequence: MDESIGNEDSEQUENCE
YAML

boltz predict free_pred.yaml \
  --out_dir free_results/ \
  --diffusion_samples 5 \
  --output_format pdb

# Compare
python3 << 'PYTHON'
from Bio.PDB import PDBParser, Superimposer
import json, glob

parser = PDBParser(QUIET=True)

forced_pdb = sorted(glob.glob("template_results/predictions/*/*.pdb"))[0]
free_pdb = sorted(glob.glob("free_results/predictions/*/*.pdb"))[0]

forced = parser.get_structure("f", forced_pdb)
free = parser.get_structure("u", free_pdb)

f_cas = [a for a in forced.get_atoms() if a.get_name() == "CA"]
u_cas = [a for a in free.get_atoms() if a.get_name() == "CA"]

n = min(len(f_cas), len(u_cas))
sup = Superimposer()
sup.set_atoms(f_cas[:n], u_cas[:n])

print(f"Template-forced vs free prediction RMSD: {sup.rms:.2f} A")
if sup.rms < 1.5:
    print("CONSISTENT: Free prediction matches design target — high confidence in fold")
elif sup.rms < 3.0:
    print("MODERATE: Some deviation — design may need stabilizing mutations")
else:
    print("DIVERGENT: Free prediction differs from target — design likely misfolded")
PYTHON
```

---

## Recipe 3: Designed Enzyme + Substrate Docking

For designed enzymes, dock the substrate into the active site to validate catalytic geometry.

```bash
cat > enzyme_substrate.yaml << 'YAML'
version: 1
sequences:
  - protein:
      id: A
      sequence: MDESIGNEDENZYMESEQUENCE
  - ligand:
      id: B
      smiles: 'SUBSTRATE_SMILES'
constraints:
  - pocket:
      binder: B
      contacts:
        - [A, 82]    # catalytic residue 1
        - [A, 153]   # catalytic residue 2
        - [A, 217]   # catalytic residue 3
      max_distance: 6.0
YAML

boltz predict enzyme_substrate.yaml \
  --out_dir enzyme_dock/ \
  --diffusion_samples 10 \
  --use_potentials \
  --output_format pdb

python3 << 'PYTHON'
import json, glob

conf = json.load(open(sorted(glob.glob("enzyme_dock/predictions/*/confidence_*.json"))[0]))

print(f"Enzyme-Substrate Docking:")
print(f"  Ligand ipTM: {conf['ligand_iptm']:.3f}")
print(f"  Complex pLDDT: {conf['complex_plddt']:.3f}")

if conf["ligand_iptm"] > 0.5:
    print("  SUBSTRATE DOCKED: Active site accommodates substrate")
else:
    print("  POOR DOCKING: Active site geometry may need redesign")
PYTHON
```

---

## Recipe 4: Cyclic Peptide Therapeutic Structure

Predict structure of a designed cyclic peptide therapeutic.

```bash
cat > cyclic_therapeutic.yaml << 'YAML'
version: 1
sequences:
  - protein:
      id: A
      sequence: GCSFPDQWAPRGL
      cyclic: true
  - protein:
      id: B
      sequence: MTARGETPROTEINSEQUENCE
YAML

boltz predict cyclic_therapeutic.yaml \
  --out_dir cyclic_results/ \
  --diffusion_samples 10 \
  --use_potentials \
  --use_msa_server \
  --output_format pdb

python3 << 'PYTHON'
import json, glob

conf = json.load(open(sorted(glob.glob("cyclic_results/predictions/*/confidence_*.json"))[0]))

print("Cyclic Peptide-Target Complex")
print(f"  ipTM: {conf['iptm']:.3f}")
print(f"  Complex pLDDT: {conf['complex_plddt']:.3f}")

if "pair_chains_iptm" in conf:
    for pair, score in conf["pair_chains_iptm"].items():
        print(f"  Interface {pair}: {score:.3f}")
PYTHON
```
