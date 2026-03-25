# Boltz-2 Recipes

> Copy-paste CLI commands and Python analysis templates for Boltz-2 biomolecular prediction.
> Parent skill: [SKILL.md](SKILL.md) — full prediction workflow and confidence interpretation.

---

## Recipe 1: Protein-Ligand Docking with Affinity

Predict binding pose and affinity for a small molecule against a protein target.

```bash
# Write YAML input
cat > docking.yaml << 'YAML'
version: 1
sequences:
  - protein:
      id: A
      sequence: MTARGETPROTEINSEQUENCE
  - ligand:
      id: B
      smiles: 'c1ccc(NC(=O)c2ccccc2)cc1'
properties:
  - affinity:
      binder: B
YAML

# Run prediction with affinity
boltz predict docking.yaml \
  --out_dir results/ \
  --diffusion_samples 5 \
  --recycling_steps 10 \
  --use_msa_server \
  --output_format pdb \
  --diffusion_samples_affinity 5

# Analyze results
python3 << 'PYTHON'
import json, glob

# Confidence
conf_file = sorted(glob.glob("results/predictions/docking/confidence_*.json"))[0]
with open(conf_file) as f:
    conf = json.load(f)

print("Protein-Ligand Docking Results")
print("=" * 50)
print(f"Confidence score: {conf['confidence_score']:.3f}")
print(f"Complex pLDDT:    {conf['complex_plddt']:.3f}")
print(f"Ligand ipTM:      {conf['ligand_iptm']:.3f}")
print(f"ipTM:             {conf['iptm']:.3f}")
print()

if conf["ligand_iptm"] > 0.5:
    print("CONFIDENT POSE: Ligand binding mode likely reliable")
elif conf["ligand_iptm"] > 0.3:
    print("MODERATE POSE: Binding plausible, details uncertain")
else:
    print("LOW CONFIDENCE: Binding pose unreliable")

# Affinity
aff_file = sorted(glob.glob("results/predictions/docking/affinity_*.json"))[0]
with open(aff_file) as f:
    aff = json.load(f)

print(f"\nAffinity prediction:")
print(f"  log10(IC50) = {aff['affinity_pred_value']:.2f} uM")
ic50_nm = 10**(aff["affinity_pred_value"] + 3)  # convert uM to nM
print(f"  IC50 ≈ {ic50_nm:.0f} nM")
print(f"  Binding probability: {aff['affinity_probability_binary']:.3f}")

if aff["affinity_probability_binary"] > 0.7:
    print("  LIKELY BINDER")
elif aff["affinity_probability_binary"] > 0.4:
    print("  POSSIBLE BINDER")
else:
    print("  UNLIKELY BINDER")
PYTHON
```

---

## Recipe 2: Virtual Screening — Batch Compound Docking

Screen multiple compounds against a target with pocket conditioning.

```bash
# Create directory of YAML inputs (one per compound)
mkdir -p screen_inputs/

# Generate YAMLs programmatically
python3 << 'PYTHON'
compounds = {
    "compound_1": "c1ccc(NC(=O)c2ccccc2)cc1",
    "compound_2": "CC(=O)Oc1ccccc1C(=O)O",
    "compound_3": "c1ccc2c(c1)cc1ccc3ccccc3c1n2",
    "compound_4": "CC(C)NCC(O)c1ccc(O)c(O)c1",
    "compound_5": "O=C(O)c1ccc(N)cc1",
}

target_seq = "MTARGETSEQUENCEHERE"
pocket_residues = [45, 78, 82, 109, 153]  # known binding site

for name, smiles in compounds.items():
    contacts = "\n".join(f"        - [A, {r}]" for r in pocket_residues)
    yaml_content = f"""version: 1
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
    with open(f"screen_inputs/{name}.yaml", "w") as f:
        f.write(yaml_content)

print(f"Generated {len(compounds)} YAML inputs")
PYTHON

# Batch predict all compounds
boltz predict screen_inputs/ \
  --out_dir screen_results/ \
  --diffusion_samples 1 \
  --recycling_steps 3 \
  --use_msa_server \
  --output_format pdb

# Rank results
python3 << 'PYTHON'
import json, glob, os

results = []
for aff_file in sorted(glob.glob("screen_results/predictions/*/affinity_*.json")):
    name = aff_file.split("/")[-2]
    with open(aff_file) as f:
        aff = json.load(f)

    conf_file = glob.glob(f"screen_results/predictions/{name}/confidence_*.json")[0]
    with open(conf_file) as f:
        conf = json.load(f)

    results.append({
        "name": name,
        "affinity": aff["affinity_pred_value"],
        "binding_prob": aff["affinity_probability_binary"],
        "ligand_iptm": conf["ligand_iptm"],
        "plddt": conf["complex_plddt"],
    })

results.sort(key=lambda r: r["affinity"])

print("Virtual Screening Results (ranked by predicted affinity)")
print("=" * 75)
print(f"{'Compound':<20} {'log10 IC50':>10} {'P(bind)':>8} {'Lig ipTM':>9} {'pLDDT':>7}")
print("-" * 75)
for r in results:
    flag = " ***" if r["binding_prob"] > 0.7 and r["ligand_iptm"] > 0.4 else ""
    print(f"{r['name']:<20} {r['affinity']:>10.2f} {r['binding_prob']:>8.3f} "
          f"{r['ligand_iptm']:>9.3f} {r['plddt']:>7.3f}{flag}")

hits = [r for r in results if r["binding_prob"] > 0.5]
print(f"\nHits (P(bind) > 0.5): {len(hits)}/{len(results)}")
PYTHON
```

---

## Recipe 3: Pocket-Conditioned Docking

Dock a ligand to a specific binding pocket defined by known contact residues.

```bash
cat > pocket_dock.yaml << 'YAML'
version: 1
sequences:
  - protein:
      id: A
      sequence: MTARGETSEQUENCE
  - ligand:
      id: B
      smiles: 'CC(=O)Oc1ccccc1C(=O)O'
constraints:
  - pocket:
      binder: B
      contacts:
        - [A, 45]
        - [A, 78]
        - [A, 82]
        - [A, 109]
        - [A, 153]
      max_distance: 6.0
YAML

boltz predict pocket_dock.yaml \
  --out_dir pocket_results/ \
  --diffusion_samples 10 \
  --use_potentials \
  --use_msa_server \
  --output_format pdb
```

---

## Recipe 4: Covalent Inhibitor Docking

Predict structure of a covalent inhibitor bound to a reactive cysteine.

```bash
cat > covalent.yaml << 'YAML'
version: 1
sequences:
  - protein:
      id: A
      sequence: MPROTEINWITHCYSTEINE
  - ligand:
      id: B
      smiles: 'C=CC(=O)Nc1cccc(NC(=O)c2ccc(F)cc2)c1'
constraints:
  - bond:
      - [A, 797, SG]     # Cysteine 797 sulfur (e.g., EGFR C797)
      - [B, 1, C3]        # Warhead carbon
YAML

boltz predict covalent.yaml \
  --out_dir covalent_results/ \
  --diffusion_samples 5 \
  --use_potentials \
  --use_msa_server \
  --output_format pdb

# Verify covalent bond
python3 << 'PYTHON'
from Bio.PDB import PDBParser
import glob

pdb_file = sorted(glob.glob("covalent_results/predictions/covalent/*.pdb"))[0]
parser = PDBParser(QUIET=True)
structure = parser.get_structure("cov", pdb_file)

# Find the covalent bond distance
residues = {r.get_id()[1]: r for r in structure[0].get_residues()}
cys = residues.get(797)
if cys and "SG" in cys:
    sg = cys["SG"]
    # Find closest ligand atom
    lig_atoms = [a for r in structure[0].get_residues()
                 for a in r.get_atoms()
                 if r.get_resname() not in ["ALA","ARG","ASN","ASP","CYS","GLN","GLU",
                                            "GLY","HIS","ILE","LEU","LYS","MET","PHE",
                                            "PRO","SER","THR","TRP","TYR","VAL"]]
    if lig_atoms:
        min_dist = min(sg - a for a in lig_atoms)
        print(f"Closest ligand atom to Cys797 SG: {min_dist:.2f} A")
        if min_dist < 2.5:
            print("COVALENT BOND FORMED: distance consistent with covalent attachment")
        else:
            print("WARNING: distance too long for covalent bond — check geometry")
PYTHON
```

---

## Recipe 5: Protein-DNA Complex

Predict a transcription factor bound to its DNA recognition sequence.

```bash
cat > protein_dna.yaml << 'YAML'
version: 1
sequences:
  - protein:
      id: A
      sequence: MTRANSCRIPTIONFACTORSEQUENCE
  - dna:
      id: B
      sequence: ATCGAATTCGAT
  - dna:
      id: C
      sequence: ATCGAATTCGAT
YAML

boltz predict protein_dna.yaml \
  --out_dir dna_results/ \
  --diffusion_samples 5 \
  --recycling_steps 10 \
  --use_msa_server \
  --output_format pdb

# Check interface quality
python3 << 'PYTHON'
import json, glob

conf_file = sorted(glob.glob("dna_results/predictions/protein_dna/confidence_*.json"))[0]
with open(conf_file) as f:
    conf = json.load(f)

print("Protein-DNA Complex Prediction")
print("=" * 45)
print(f"Complex pLDDT: {conf['complex_plddt']:.3f}")
print(f"ipTM:          {conf['iptm']:.3f}")
print(f"pTM:           {conf['ptm']:.3f}")

# Per-chain pair interface scores
if "pair_chains_iptm" in conf:
    print("\nPairwise interface scores:")
    for pair, score in conf["pair_chains_iptm"].items():
        print(f"  {pair}: {score:.3f}")
PYTHON
```

---

## Recipe 6: Molecular Glue Ternary Complex

Model a molecular glue mediating interaction between E3 ligase and substrate.

```bash
cat > ternary.yaml << 'YAML'
version: 1
sequences:
  - protein:
      id: A
      sequence: ME3LIGASESEQUENCE
  - protein:
      id: B
      sequence: MSUBSTRATESEQUENCE
  - ligand:
      id: C
      smiles: 'O=C1CCC(N2C(=O)c3ccccc3C2=O)C(=O)N1'
properties:
  - affinity:
      binder: C
YAML

boltz predict ternary.yaml \
  --out_dir ternary_results/ \
  --diffusion_samples 10 \
  --recycling_steps 10 \
  --use_potentials \
  --use_msa_server \
  --output_format pdb

# Analyze ternary complex
python3 << 'PYTHON'
import json, glob

conf_file = sorted(glob.glob("ternary_results/predictions/ternary/confidence_*.json"))[0]
with open(conf_file) as f:
    conf = json.load(f)

print("Ternary Complex (E3:Substrate:Glue)")
print("=" * 50)
print(f"Complex pLDDT:   {conf['complex_plddt']:.3f}")
print(f"Protein ipTM:    {conf['protein_iptm']:.3f}")
print(f"Ligand ipTM:     {conf['ligand_iptm']:.3f}")
print()

# E3-substrate interface is the key metric for molecular glues
if "pair_chains_iptm" in conf:
    for pair, score in conf["pair_chains_iptm"].items():
        if "A" in pair and "B" in pair:
            print(f"E3-Substrate interface (A-B): {score:.3f}")
            if score > 0.5:
                print("  COOPERATIVE BINDING: Glue enhances E3-substrate interaction")
            else:
                print("  WEAK INTERFACE: Glue may not stabilize ternary complex")

aff_file = sorted(glob.glob("ternary_results/predictions/ternary/affinity_*.json"))[0]
with open(aff_file) as f:
    aff = json.load(f)
print(f"\nGlue affinity: log10(IC50) = {aff['affinity_pred_value']:.2f} uM")
print(f"Binding probability: {aff['affinity_probability_binary']:.3f}")
PYTHON
```

---

## Recipe 7: Template-Guided Prediction

Predict a complex guided by a known experimental structure.

```bash
# Download template from PDB first (via pdb-structures skill or wget)

cat > template_guided.yaml << 'YAML'
version: 1
sequences:
  - protein:
      id: A
      sequence: MPROTEINSEQUENCE
      templates:
        - cif_path: template.cif
          chain_id: A
          force: true
          threshold: 2.0
  - ligand:
      id: B
      smiles: 'c1ccc(NC(=O)c2ccccc2)cc1'
YAML

boltz predict template_guided.yaml \
  --out_dir template_results/ \
  --diffusion_samples 5 \
  --use_potentials \
  --output_format pdb
```

---

## Recipe 8: Confidence Analysis Script

Parse and compare Boltz outputs across multiple predictions.

```python
import json, glob, os

def analyze_boltz_results(results_dir):
    """Analyze all Boltz predictions in a results directory."""
    predictions = {}

    for conf_file in sorted(glob.glob(f"{results_dir}/predictions/*/confidence_*.json")):
        name = conf_file.split("/")[-2]
        with open(conf_file) as f:
            conf = json.load(f)

        entry = {
            "confidence": conf["confidence_score"],
            "plddt": conf["complex_plddt"],
            "ptm": conf["ptm"],
            "iptm": conf["iptm"],
            "ligand_iptm": conf.get("ligand_iptm", None),
            "protein_iptm": conf.get("protein_iptm", None),
        }

        # Check for affinity
        aff_files = glob.glob(f"{results_dir}/predictions/{name}/affinity_*.json")
        if aff_files:
            with open(aff_files[0]) as f:
                aff = json.load(f)
            entry["affinity"] = aff.get("affinity_pred_value")
            entry["binding_prob"] = aff.get("affinity_probability_binary")

        predictions[name] = entry

    # Print summary
    print(f"{'Name':<25} {'Conf':>5} {'pLDDT':>6} {'ipTM':>5} {'LigipTM':>8} {'Affinity':>9} {'P(bind)':>8}")
    print("-" * 72)
    for name, p in sorted(predictions.items(), key=lambda x: -x[1]["confidence"]):
        lig = f"{p['ligand_iptm']:.3f}" if p["ligand_iptm"] is not None else "  N/A"
        aff = f"{p['affinity']:.2f}" if p.get("affinity") is not None else "    N/A"
        bind = f"{p['binding_prob']:.3f}" if p.get("binding_prob") is not None else "  N/A"
        print(f"{name:<25} {p['confidence']:>5.3f} {p['plddt']:>6.3f} {p['iptm']:>5.3f} {lig:>8} {aff:>9} {bind:>8}")

    return predictions

# Usage:
# analyze_boltz_results("screen_results/")
```

---

## Recipe 9: Cyclic Peptide Structure Prediction

Predict structure of a cyclic peptide therapeutic.

```bash
cat > cyclic_peptide.yaml << 'YAML'
version: 1
sequences:
  - protein:
      id: A
      sequence: GCSFPDQWAPRGL
      cyclic: true
YAML

boltz predict cyclic_peptide.yaml \
  --out_dir cyclic_results/ \
  --diffusion_samples 10 \
  --use_potentials \
  --output_format pdb
```

---

## Recipe 10: Compare Boltz vs ColabFold for Protein Complex

Run both Boltz and ColabFold on the same protein complex to cross-validate.

```bash
# Boltz prediction
cat > complex_boltz.yaml << 'YAML'
version: 1
sequences:
  - protein:
      id: A
      sequence: MFIRSTPROTEIN
  - protein:
      id: B
      sequence: MSECONDPROTEIN
YAML

boltz predict complex_boltz.yaml \
  --out_dir boltz_complex/ \
  --diffusion_samples 5 \
  --recycling_steps 10 \
  --use_msa_server \
  --output_format pdb

# ColabFold prediction (same complex)
cat > complex_cf.fasta << 'FASTA'
>protein_complex
MFIRSTPROTEIN:MSECONDPROTEIN
FASTA

colabfold_batch complex_cf.fasta colabfold_complex/ \
  --model-type alphafold2_multimer_v3 \
  --num-models 5 \
  --num-recycle 10

# Compare
python3 << 'PYTHON'
import json, glob
from Bio.PDB import PDBParser, Superimposer

parser = PDBParser(QUIET=True)

# Boltz confidence
boltz_conf = sorted(glob.glob("boltz_complex/predictions/*/confidence_*.json"))[0]
with open(boltz_conf) as f:
    bc = json.load(f)

# ColabFold confidence
cf_scores = sorted(glob.glob("colabfold_complex/*scores_rank_001*.json"))[0]
with open(cf_scores) as f:
    cc = json.load(f)

print("Boltz-2 vs ColabFold Comparison")
print("=" * 50)
print(f"{'Metric':<20} {'Boltz-2':>10} {'ColabFold':>10}")
print("-" * 50)
print(f"{'pLDDT':<20} {bc['complex_plddt']:>10.3f} {sum(cc['plddt'])/len(cc['plddt'])/100:>10.3f}")
print(f"{'ipTM':<20} {bc['iptm']:>10.3f} {cc.get('iptm', 0):>10.3f}")
print(f"{'pTM':<20} {bc['ptm']:>10.3f} {cc.get('ptm', 0):>10.3f}")

# RMSD between predictions
boltz_pdb = sorted(glob.glob("boltz_complex/predictions/*/*.pdb"))[0]
cf_pdb = sorted(glob.glob("colabfold_complex/*rank_001*.pdb"))[0]

b_struct = parser.get_structure("boltz", boltz_pdb)
c_struct = parser.get_structure("cf", cf_pdb)

b_cas = [a for a in b_struct.get_atoms() if a.get_name() == "CA"]
c_cas = [a for a in c_struct.get_atoms() if a.get_name() == "CA"]

n = min(len(b_cas), len(c_cas))
if n > 10:
    sup = Superimposer()
    sup.set_atoms(b_cas[:n], c_cas[:n])
    print(f"\n{'CA RMSD':<20} {sup.rms:>10.2f} A")

    if sup.rms < 2.0:
        print("CONCORDANT: Both methods agree on structure")
    else:
        print("DIVERGENT: Methods disagree — check per-chain confidence")
PYTHON
```
