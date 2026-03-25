# BoltzGen Recipes

> Copy-paste CLI commands and YAML templates for de novo binder design.
> Parent skill: [SKILL.md](SKILL.md) — full BoltzGen workflow.

---

## Recipe 1: Nanobody Design Campaign

Design nanobodies against a target using pre-built scaffold libraries.

```bash
cat > nanobody_spec.yaml << 'YAML'
entities:
  - name: target
    type: structure
    source: target.cif
    chains:
      A:
        include: all
        binding_types:
          binding: "56,83,91"
          not_binding: "1..10,200..250"
  - name: nanobody
    type: scaffold
    scaffold: caplacizumab
YAML

boltzgen run nanobody_spec.yaml \
  --output nanobody_campaign/ \
  --protocol nanobody-anything \
  --num_designs 10000 \
  --budget 60
```

---

## Recipe 2: Antibody Fab Design

Design antibody Fab CDR loops against a target.

```bash
cat > fab_spec.yaml << 'YAML'
entities:
  - name: target
    type: structure
    source: target.cif
    chains:
      A:
        include: all
        binding_types:
          binding: "45,78,82"
  - name: antibody
    type: scaffold
    scaffold: adalimumab
YAML

boltzgen run fab_spec.yaml \
  --output fab_campaign/ \
  --protocol antibody-anything \
  --num_designs 10000 \
  --budget 60
```

---

## Recipe 3: Cyclotide Binder with Disulfides

Design a cyclic peptide with three disulfide bonds.

```bash
cat > cyclotide_spec.yaml << 'YAML'
entities:
  - name: target
    type: structure
    source: target.cif
    chains:
      A:
        include: all
        binding_types:
          binding: "30,45,60"
  - name: cyclotide
    type: protein
    sequence: 10C6C3C4C6C3
    cyclic: true
constraints:
  - bond:
      atom1: [B, 3, SG]
      atom2: [B, 24, SG]
  - bond:
      atom1: [B, 10, SG]
      atom2: [B, 21, SG]
  - bond:
      atom1: [B, 14, SG]
      atom2: [B, 28, SG]
YAML

boltzgen run cyclotide_spec.yaml \
  --output cyclotide/ \
  --protocol peptide-anything \
  --num_designs 20000 \
  --budget 60
```

---

## Recipe 4: Small-Molecule Binder with Affinity

Design a protein to bind a small molecule, with Boltz-2 affinity prediction.

```bash
cat > sm_binder_spec.yaml << 'YAML'
entities:
  - name: ligand
    type: ligand
    ccd: ATP
  - name: binder
    type: protein
    sequence: 80..120
YAML

boltzgen run sm_binder_spec.yaml \
  --output sm_binder/ \
  --protocol protein-small_molecule \
  --num_designs 10000 \
  --budget 60
```

---

## Recipe 5: Protein Binder with Exclusion Zones

Design a binder that avoids specific target regions.

```bash
cat > exclusion_spec.yaml << 'YAML'
entities:
  - name: target
    type: structure
    source: target.cif
    chains:
      A:
        include: all
        binding_types:
          binding: "56,83,91"
          not_binding: "1..20,180..200"
  - name: binder
    type: protein
    sequence: 70..110
    residue_constraints:
      1:
        disallowed: [C, M]
YAML

boltzgen run exclusion_spec.yaml \
  --output exclusion_binder/ \
  --protocol protein-anything \
  --num_designs 10000 \
  --budget 60
```

---

## Recipe 6: Analyze Results

```python
import pandas as pd

df = pd.read_csv("nanobody_campaign/final_ranked_designs/all_designs_metrics.csv")
print(f"Total designs: {len(df)}")

# Top by refolding RMSD (lower = better self-consistency)
top = df.nsmallest(10, "refolding_rmsd")
for _, r in top.iterrows():
    print(f"  {r.get('name','?')}: RMSD={r['refolding_rmsd']:.2f}A "
          f"i_pTM={r.get('iptm',0):.3f} pLDDT={r.get('plddt',0):.3f}")
```
