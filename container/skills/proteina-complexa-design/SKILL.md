---
name: proteina-complexa-design
description: "Fully atomistic protein binder and enzyme design using Proteina-Complexa (NVIDIA). Generates structures and sequences jointly in a single pass for protein targets, small-molecule ligand targets, and motif+ligand enzyme scaffolding. Supports inference-time search (beam search, MCTS) with AF2/RF3 reward models. 41/41 enzyme design success, ICLR 2026 oral. Use when user mentions Proteina-Complexa, atomistic binder design, enzyme design with ligand, motif scaffolding with ligand, AME design, inference-time search protein design, or NVIDIA protein design."
---

# Proteina-Complexa — Atomistic Binder & Enzyme Design

> **Code recipes**: See [recipes.md](recipes.md) for copy-paste CLI commands.

Fully atomistic generative model for protein binder and enzyme design from NVIDIA. Generates backbone, side chains, and sequences jointly. Supports protein targets, small-molecule ligand targets, and motif+ligand (AME) enzyme scaffolding. Uses inference-time search (beam search, MCTS) with AF2/RF3 reward models for test-time compute scaling.

**When to use Proteina-Complexa vs alternatives:**
- **Proteina-Complexa** — atomistic design (backbone+sidechains+sequence), enzyme active sites with ligands, inference-time search scaling
- **RFdiffusion3** — all-atom diffusion, DNA binders, faster single-pass, Baker Lab ecosystem
- **BoltzGen** — nanobodies/antibodies (scaffold libraries), cyclotides, Boltz-2 ecosystem
- **BindCraft** — automated AF2-based binder campaigns, PyRosetta scoring

## Cross-Reference: Other Skills

- **Backbone-only design** → use rfdiffusion-design or rfdiffusion3-design
- **Nanobody/antibody scaffold design** → use boltzgen-design
- **Automated binder campaigns** → use bindcraft-design
- **Post-design validation** → use protenix-predict or boltz-predict

## Tool: Complexa CLI

```bash
pip install proteina-complexa  # or uv install
complexa init && complexa download --all
```

### Key Commands

| Command | Purpose |
|---------|---------|
| `complexa design config.yaml` | Full pipeline: generate → filter → evaluate → analyze |
| `complexa generate config.yaml` | Generate designs only |
| `complexa filter config.yaml` | Filter by metrics |
| `complexa evaluate config.yaml` | AF2/RF3 evaluation |
| `complexa analyze config.yaml` | Compute metrics and rank |
| `complexa target list` | List available benchmark targets |

### Search Algorithms

| Algorithm | Use when |
|-----------|----------|
| `single-pass` | Quick screening (fastest) |
| `best-of-n` | Moderate quality with N replicas |
| `beam-search` | Highest quality (prune at denoising checkpoints) |
| `fk-steering` | Boltzmann-weighted selection |
| `mcts` | Maximum exploration for diverse campaigns |

## Input: Hydra YAML Config

### Protein Target Binder

```yaml
generation:
  task_name: PDL1
  search_algorithm: beam-search
  num_designs: 1000
  binder_length: [70, 120]
target:
  target_path: targets/pdl1.pdb
  target_input: A1-115
  hotspot_residues: [56, 83, 91]
```

### Small-Molecule Ligand Binder

```yaml
generation:
  task_name: ATP_binder
  search_algorithm: beam-search
  model: ligand  # LoRA-finetuned ligand model
target:
  target_path: targets/atp.pdb
  ligand: ATP
  SMILES: "c1nc(c2c(n1)n(cn2)[C@@H]3[C@@H]([C@@H]([C@H](O3)COP(=O)(O)OP(=O)(O)OP(=O)(O)O)O)O)N"
```

### AME Enzyme Scaffolding (Motif + Ligand)

```yaml
generation:
  task_name: phosphoglycerate_kinase
  search_algorithm: beam-search
  model: ame  # LoRA-finetuned AME model
target:
  target_path: targets/pgk_motif.pdb
  contig_atoms: "B:82:SG,B:153:OG,B:217:OD1"  # catalytic atoms
```

## Output

- PDB files with full atomistic structures (backbone + sidechains + sequences)
- CSV with per-design metrics: i_pAE, i_pTM, pLDDT, scRMSD, motif RMSD, sequence recovery
- Summary plots and diversity analysis (Foldseek + MMseqs2 clustering)

## Completeness Checklist

- [ ] Target PDB and hotspot residues prepared
- [ ] Config YAML written with appropriate search algorithm
- [ ] Pipeline completed (generate → filter → evaluate → analyze)
- [ ] Top candidates ranked from metrics CSV
- [ ] Diversity analysis reviewed
