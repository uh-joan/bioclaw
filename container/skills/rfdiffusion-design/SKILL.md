---
name: rfdiffusion-design
description: "De novo protein backbone generation using RFdiffusion. Generates novel 3D protein backbones via denoising diffusion, conditioned on targets, motifs, symmetry, or fold topology. Covers binder design, motif scaffolding, symmetric oligomers, active site scaffolding, fold-conditioned generation, partial diffusion, and macrocyclic peptides. Use when user mentions RFdiffusion, de novo backbone, protein backbone generation, binder design, motif scaffolding, scaffold generation, symmetric oligomer design, diffusion-based protein design, or novel fold generation."
---

# RFdiffusion — De Novo Protein Backbone Generation

> **Code recipes**: See [recipes.md](recipes.md) for copy-paste CLI commands and contig syntax examples.

De novo protein backbone generation via denoising diffusion from the Baker Lab. Generates novel 3D protein backbones (N, CA, C, O coordinates) either unconditionally or conditioned on targets, structural motifs, symmetry, or fold topology. Outputs poly-glycine backbones that are then sequenced with ProteinMPNN and validated with structure prediction tools.

**The full de novo design pipeline:**
```
RFdiffusion (this skill) → ProteinMPNN (sequence) → ColabFold/Boltz/Protenix (validate) → Experiment
```

## Report-First Workflow

1. **Create report file immediately**: `[target]_rfdiffusion_design_report.md`
2. **Add placeholders**: Mark each section `[Designing...]`
3. **Populate progressively**: Update as designs are generated
4. **Final verification**: Ensure no placeholders remain

## When NOT to Use This Skill

- Sequence design from an existing backbone → use `proteinmpnn-design`
- Structure prediction from sequence → use `colabfold-predict`, `boltz-predict`, `protenix-predict`
- Protein-ligand docking → use `boltz-predict`
- Antibody humanization → use `antibody-engineering`

## Cross-Reference: Other Skills

- **Sequence design for generated backbones** → use proteinmpnn-design skill
- **Structure prediction validation** → use colabfold-predict (fast) or protenix-predict (highest accuracy)
- **Protein-ligand complex after design** → use boltz-predict
- **Full therapeutic design pipeline** → use protein-therapeutic-design skill (orchestrates all tools)
- **Enzyme active site scaffolding** → use enzyme-engineering skill (context) then this skill (backbone)

## Tool: RFdiffusion CLI (`run_inference.py`)

### Installation Check

```bash
python RFdiffusion/scripts/run_inference.py --help 2>/dev/null || {
  git clone https://github.com/RosettaCommons/RFdiffusion.git
  # Follow install instructions in README
}
```

### Core Command

```bash
python RFdiffusion/scripts/run_inference.py \
  'contigmap.contigs=[CONTIG_STRING]' \
  inference.output_prefix=output/design \
  inference.num_designs=10
```

### Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `contigmap.contigs` | - | Design specification (see Contig Syntax below) |
| `inference.input_pdb` | - | Input PDB (target, motif source) |
| `inference.output_prefix` | - | Output path prefix |
| `inference.num_designs` | 1 | Number of backbones to generate |
| `diffuser.T` | 50 | Diffusion timesteps (more = slower but potentially better) |
| `denoiser.noise_scale_ca` | 1.0 | Translation noise (lower = less diverse, higher quality) |
| `denoiser.noise_scale_frame` | 1.0 | Rotation noise |
| `ppi.hotspot_res` | - | Target hotspot residues for binder design |
| `inference.ckpt_override_path` | auto | Override model checkpoint |
| `potentials.guiding_potentials` | - | Auxiliary potentials (ROG, contacts) |
| `contigmap.length` | - | Force total length (e.g., `55-55`) |
| `scaffoldguided.scaffoldguided` | False | Enable fold conditioning |
| `inference.cyclic` | False | Macrocyclic peptide design |

### Model Checkpoints

| Checkpoint | Auto-selected for |
|------------|-------------------|
| `Base_ckpt.pt` | Unconditional, motif scaffolding |
| `Complex_base_ckpt.pt` | Binder design (PPI) |
| `Complex_Fold_base_ckpt.pt` | Fold-conditioned binder design |
| `ActiveSite_ckpt.pt` | Very small motifs / enzyme active sites |
| `InpaintSeq_ckpt.pt` | Inpaint sequence tasks |

## Contig Syntax

The contig string defines what to build. It is the core specification language.

### Basic Elements

| Syntax | Meaning |
|--------|---------|
| `150-150` | Generate exactly 150 new residues |
| `100-200` | Generate 100-200 residues (random per design) |
| `A10-25` | Use residues 10-25 from chain A of input PDB |
| `/` | Segment separator (no chain break) |
| `/0 ` | Chain break (space after 0 required) |

### Common Patterns

**Unconditional — novel protein of specific length:**
```
'contigmap.contigs=[150-150]'
```

**Binder design — target + new binder chain:**
```
'contigmap.contigs=[A1-150/0 70-100]'
# Chain A (target) fixed, chain break, 70-100 residue binder
```

**Motif scaffolding — embed motif in new scaffold:**
```
'contigmap.contigs=[10-40/A163-181/10-40]'
# 10-40 new residues, motif from A163-181, 10-40 new residues
```

**Multi-motif scaffolding:**
```
'contigmap.contigs=[5-15/A163-181/5-15/A200-215/5-15]'
```

**Partial diffusion — diversify existing structure:**
```
'contigmap.contigs=[A1-100]' diffuser.partial_T=20
# Noise and denoise chain A (100 residues) for 20 steps
```

## Output Files

| File | Content |
|------|---------|
| `design_N.pdb` | Backbone structure (poly-glycine, designed residues as GLY) |
| `design_N.trb` | Metadata: contig mapping, residue indices, config |
| `traj/design_N_pX0_traj.pdb` | Denoising trajectory (model predictions at each step) |
| `traj/design_N_Xt-1_traj.pdb` | Intermediate states trajectory |

**Important**: RFdiffusion outputs **backbone only** (poly-glycine). Use ProteinMPNN to assign sequences.

## Design Strategies

### Binder Design Campaign (Standard)

```bash
# Generate ~1000 backbones
python RFdiffusion/scripts/run_inference.py \
  inference.input_pdb=target.pdb \
  'contigmap.contigs=[A1-150/0 70-100]' \
  'ppi.hotspot_res=[A59,A83,A91]' \
  inference.output_prefix=binders/design \
  inference.num_designs=1000

# Then: ProteinMPNN → ColabFold/AF2 validation → experimental
```

### Motif Scaffolding

```bash
python RFdiffusion/scripts/run_inference.py \
  inference.input_pdb=motif_source.pdb \
  'contigmap.contigs=[10-40/A163-181/10-40]' \
  inference.output_prefix=scaffolds/design \
  inference.num_designs=100
```

### Symmetric Oligomer

```bash
python RFdiffusion/scripts/run_inference.py \
  --config-name symmetry \
  inference.symmetry=c4 \
  'contigmap.contigs=[360]' \
  inference.output_prefix=c4_oligo/design \
  inference.num_designs=50
```

### Fold-Conditioned Design

```bash
# Generate secondary structure files
python RFdiffusion/helper_scripts/make_secstruc_adj.py \
  --input_pdb template.pdb --out_dir ss_files/

python RFdiffusion/scripts/run_inference.py \
  scaffoldguided.scaffoldguided=True \
  scaffoldguided.scaffold_dir=ss_files/ \
  'contigmap.contigs=[A1-150/0 70-100]' \
  inference.output_prefix=fold_cond/design \
  inference.num_designs=100
```

### Enzyme Active Site Scaffolding

```bash
python RFdiffusion/scripts/run_inference.py \
  inference.input_pdb=active_site_motif.pdb \
  'contigmap.contigs=[10-20/A82-82/5-10/A153-153/5-10/A217-217/10-20]' \
  inference.ckpt_override_path=RFdiffusion/models/ActiveSite_ckpt.pt \
  inference.output_prefix=enzyme_scaffold/design \
  inference.num_designs=500
```

### Macrocyclic Peptide Binder

```bash
python RFdiffusion/scripts/run_inference.py \
  inference.input_pdb=target.pdb \
  'contigmap.contigs=[A1-100/0 8-15]' \
  'ppi.hotspot_res=[A30,A45,A60]' \
  inference.cyclic=True \
  'inference.cyc_chains=["b"]' \
  inference.output_prefix=cyclic/design \
  inference.num_designs=200
```

## Common Workflows

### 1. Full Binder Design Pipeline

1. **RFdiffusion**: Generate 1,000-10,000 backbones targeting hotspot residues
2. **ProteinMPNN**: 2 sequences per backbone (T=0.1)
3. **ColabFold/AF2**: Predict structure, filter on pae_interaction < 10
4. **Boltz-2**: Optional affinity estimation for filtered designs
5. **Experimental**: Order top ~50-100 designs for expression + binding assays

### 2. Motif Scaffolding → Validation

1. **RFdiffusion**: Scaffold a functional motif in 100-500 new backbones
2. **ProteinMPNN**: Design sequences (fix motif residues)
3. **ColabFold**: Self-consistency check (RMSD to target backbone < 1.5A)
4. **Protenix**: High-accuracy validation for top candidates

### 3. Partial Diffusion (Structure Diversification)

1. Start with an existing design or natural protein
2. **RFdiffusion** with `partial_T=10-30`: Add noise and denoise
3. Output: Structurally diverse variants of the input
4. **ProteinMPNN** + validation as usual

## Tiered Execution (Timeout Resilience)

### Tier 1 — MUST COMPLETE (first 5 min)
```
1. Prepare input PDB and contig string
2. Generate 10 backbones (quick test)
3. Inspect outputs for reasonable geometry
>>> CHECKPOINT: Save initial backbones <<<
```

### Tier 2 — HIGH VALUE (next 15 min)
```
4. Generate 100-500 backbones
5. Run ProteinMPNN on all backbones
6. Quick ColabFold validation of top 10
>>> CHECKPOINT: Save designed sequences + validation <<<
```

### Tier 3 — COMPLETE PICTURE (remaining time)
```
7. Generate 1000+ backbones for full campaign
8. ProteinMPNN + ColabFold/Protenix full pipeline
9. Rank all validated designs
>>> FINAL CHECKPOINT: Complete design report <<<
```

## Completeness Checklist

**Tier 1 (minimum viable design):**
- [ ] Input PDB and contig string prepared
- [ ] RFdiffusion run completed (at least 10 backbones)
- [ ] Output PDBs inspected for reasonable geometry
- [ ] Report file saved with backbone descriptions

**Tier 2 (standard campaign):**
- [ ] 100+ backbones generated
- [ ] ProteinMPNN sequences designed for all backbones
- [ ] Top designs validated with structure prediction
- [ ] Self-consistent designs identified

**Tier 3 (full campaign):**
- [ ] 1000+ backbones generated
- [ ] Full ProteinMPNN + validation pipeline completed
- [ ] Designs ranked by prediction confidence
- [ ] Final candidates recommended for experimental testing
