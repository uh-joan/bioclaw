---
name: boltzgen-design
description: "De novo binder design using BoltzGen (built on Boltz-2). Designs nanobodies, antibodies, proteins, peptides, cyclotides, and small-molecule binders with integrated inverse folding, Boltz-2 refolding validation, and diversity-optimized filtering. Supports binding site specification, exclusion zones, disulfide bonds, secondary structure constraints, and cyclic peptides. 67% experimental success rate. Use when user mentions BoltzGen, nanobody design, antibody CDR design, cyclotide design, small molecule binder design, de novo nanobody, de novo antibody binder, or protein binder with constraints."
---

# BoltzGen — De Novo Binder Design (Boltz-2 Ecosystem)

> **Code recipes**: See [recipes.md](recipes.md) for copy-paste CLI commands and YAML templates.

End-to-end de novo binder design built on Boltz-2. Designs nanobodies, antibodies (Fab), proteins, peptides, cyclotides, and small-molecule binders. Full pipeline: diffusion backbone generation → custom inverse folding → Boltz-2 refolding validation → analysis → diversity-optimized filtering. 67% experimental success rate for nanomolar nanobody binders.

**When to use BoltzGen vs alternatives:**
- **BoltzGen** — best for nanobodies, antibodies (CDR redesign with scaffold libraries), cyclotides, small-molecule binders, rich constraint YAML
- **BindCraft** — best for general protein binders, automated AF2 hallucination loop, PyRosetta scoring
- **RFdiffusion** — best for motif scaffolding, symmetric oligomers, manual pipeline control
- **Proteina-Complexa** — best for atomistic binder + enzyme design, inference-time search

## Report-First Workflow

1. **Create report file immediately**: `[target]_boltzgen_design_report.md`
2. **Populate progressively** as pipeline completes
3. **Final**: report top candidates from diversity-optimized set

## Cross-Reference: Other Skills

- **General protein binder design** → use bindcraft-design or rfdiffusion-design
- **Backbone-only design + manual pipeline** → use rfdiffusion-design + proteinmpnn-design
- **Post-design affinity estimation** → use boltz-predict
- **Atomistic enzyme + binder design** → use proteina-complexa-design

## Tool: BoltzGen CLI

```bash
pip install boltzgen
boltzgen run design_spec.yaml --output out/ --protocol protein-anything --num_designs 10000 --budget 60
```

### Key Commands

| Command | Purpose |
|---------|---------|
| `boltzgen run spec.yaml --output out/` | Full pipeline |
| `boltzgen check spec.yaml` | Validate YAML |
| `boltzgen configure spec.yaml --output out/` | Generate configs without running |
| `boltzgen execute out/` | Run pre-configured pipeline |
| `boltzgen merge run_a/ run_b/ --output merged/` | Merge parallel runs |

### Protocols

| Protocol | Target type |
|----------|------------|
| `protein-anything` | Protein targets (general binders) |
| `nanobody-anything` | Nanobody CDR design with scaffold libraries |
| `antibody-anything` | Fab antibody CDR design with scaffold libraries |
| `peptide-anything` | Peptide binders |
| `protein-small_molecule` | Small-molecule binders (with affinity) |

## YAML Design Spec

### Protein Binder

```yaml
entities:
  - name: target
    type: structure
    source: target.cif
    chains:
      A:
        include: 1..150
        binding_types:
          binding: "56,83,91"
  - name: binder
    type: protein
    sequence: 80..120
```

### Nanobody (CDR Redesign)

```yaml
entities:
  - name: target
    type: structure
    source: target.cif
    chains:
      A:
        include: all
        binding_types:
          binding: "56,83,91"
  - name: nanobody
    type: scaffold
    scaffold: caplacizumab
    # CDR loops automatically redesigned with variable-length insertions
```

### Cyclotide with Disulfides

```yaml
entities:
  - name: target
    type: structure
    source: target.cif
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
```

### Small-Molecule Binder

```yaml
entities:
  - name: ligand
    type: ligand
    ccd: ATP
  - name: binder
    type: protein
    sequence: 80..120
```

## Output Structure

```
out/
├── final_ranked_designs/
│   ├── final_60_designs/          ← Top diversity-optimized set
│   ├── all_designs_metrics.csv    ← All metrics
│   └── results_overview.pdf       ← Summary plots
├── intermediate_designs/           ← Raw backbones
├── intermediate_designs_inverse_folded/
│   ├── refold_cif/                ← Boltz-2 refolded complexes
│   └── refold_design_cif/         ← Binder-alone refolds
└── filter.ipynb                    ← Interactive filtering notebook
```

## Completeness Checklist

- [ ] Target CIF/PDB prepared with binding site residues identified
- [ ] YAML design spec written with appropriate protocol
- [ ] BoltzGen run completed (10,000+ designs recommended)
- [ ] Diversity-optimized final set extracted
- [ ] Top candidates analyzed from metrics CSV
- [ ] Optional: Boltz-2 affinity for small-molecule binders
