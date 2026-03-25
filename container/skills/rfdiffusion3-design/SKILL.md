---
name: rfdiffusion3-design
description: "All-atom biomolecular design using RFdiffusion3. Generates novel proteins with full atomistic detail (backbone + sidechains jointly) for protein binders, DNA-binding proteins, enzymes, and small-molecule binders. 10x faster than RFdiffusion, 90% enzyme scaffolding success, joint protein-DNA design. Use when user mentions RFdiffusion3, RFD3, all-atom protein design, DNA binding protein design, all-atom enzyme design, RosettaCommons Foundry, or next-gen RFdiffusion."
---

# RFdiffusion3 — All-Atom Biomolecular Design

> **Code recipes**: See [recipes.md](recipes.md) for copy-paste CLI commands.

All-atom de novo protein design via diffusion from the Baker Lab. Third generation: generates backbone + sidechains + sequences jointly for proteins, ligands, and DNA/RNA. 10x faster than RFdiffusion v1, 90% enzyme active site scaffolding success (vs 39% for v1), 8.2 unique binder solutions per target (vs 1.4 for v1).

**When to use RFdiffusion3 vs alternatives:**
- **RFdiffusion3** — all-atom design, DNA binders, fastest Baker Lab diffusion, enzyme active sites
- **RFdiffusion (v1)** — backbone-only, motif scaffolding, symmetric oligomers (v1 features still relevant)
- **Proteina-Complexa** — atomistic + inference-time search, small-molecule ligands (stronger ligand support)
- **BoltzGen** — nanobodies/antibodies with scaffold libraries

## Cross-Reference: Other Skills

- **Backbone-only design (v1)** → use rfdiffusion-design
- **Sequence design for backbones** → use proteinmpnn-design (still useful for v1 outputs)
- **Design validation** → use protenix-predict or colabfold-predict
- **Enzyme active site context** → use enzyme-engineering skill

## Tool: RFD3 via RosettaCommons Foundry

```bash
pip install rc-foundry[rfd3]
foundry install rfd3 --checkpoint-dir ~/.foundry/checkpoints
```

### Core Command

```bash
rfd3 design out_dir=output/ inputs=design_spec.json
```

### Key Parameters

| Parameter | Description |
|-----------|-------------|
| `out_dir` | Output directory |
| `inputs` | JSON/YAML design spec |
| `dump_trajectories=True` | Save denoising trajectory |
| `prevalidate_inputs=True` | Check config before loading model |

## Input: JSON Design Spec

### Protein Binder Design

```json
{
  "target": {
    "pdb_path": "target.pdb",
    "chains": ["A"],
    "hotspot_residues": [56, 83, 91]
  },
  "binder": {
    "length_range": [70, 100]
  }
}
```

### DNA-Binding Protein Design

```json
{
  "dna_target": {
    "sequence": "ATCGAATTCGAT"
  },
  "binder": {
    "length_range": [80, 120]
  }
}
```

### Enzyme Active Site Scaffolding

```json
{
  "motif": {
    "pdb_path": "catalytic_site.pdb",
    "fixed_atoms": ["A:82:SG", "A:153:OG", "A:217:OD1"]
  },
  "scaffold": {
    "length_range": [150, 200]
  }
}
```

## Output

- PDB files with **full atomistic structures** (backbone + all side-chain atoms)
- Optional trajectory dumps (multi-model PDB)
- All designed residues have complete side chains (unlike RFdiffusion v1 poly-glycine)

## Key Capabilities

| Capability | RFD v1 | RFD3 |
|-----------|--------|------|
| Resolution | Backbone only (poly-GLY) | Full all-atom (14 atoms/residue) |
| Sequence design | Separate (ProteinMPNN) | Joint in diffusion |
| DNA binders | No | Yes |
| Enzyme success | 39% (16/41 benchmarks) | 90% (37/41) |
| Unique binders/target | 1.4 avg | 8.2 avg |
| Speed | Baseline | ~10x faster |
| Parameters | ~350M | 168M |

## Completeness Checklist

- [ ] Design spec JSON written
- [ ] RFD3 run completed
- [ ] Output PDBs inspected (full atomistic structures)
- [ ] Top designs validated with Protenix/ColabFold
- [ ] Report with structural analysis
