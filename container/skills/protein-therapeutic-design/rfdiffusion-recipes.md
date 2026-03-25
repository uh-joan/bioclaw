# RFdiffusion Protein Therapeutic Design Recipes

Recipes for de novo backbone generation in the protein therapeutic design pipeline. RFdiffusion generates the initial scaffolds that are then sequenced with ProteinMPNN and validated with structure prediction tools.

> **Parent skill**: [SKILL.md](SKILL.md) — full protein therapeutic design pipeline.
> **See also**: [rfdiffusion-design skill](../rfdiffusion-design/SKILL.md) — standalone RFdiffusion with full CLI and contig syntax.

---

## Recipe 1: De Novo Binder Campaign

Generate binder backbones targeting a therapeutic target, then sequence and validate.

```bash
# Step 1: RFdiffusion — 1000 binder backbones
python RFdiffusion/scripts/run_inference.py \
  inference.input_pdb=target.pdb \
  'contigmap.contigs=[A1-150/0 70-100]' \
  'ppi.hotspot_res=[A59,A83,A91]' \
  inference.output_prefix=campaign/backbone \
  inference.num_designs=1000

# Step 2: ProteinMPNN — 2 sequences per backbone
# (see proteinmpnn-recipes.md Recipe 1)

# Step 3: ColabFold validation — filter pLDDT > 80, RMSD < 1.5A
# (see colabfold-recipes.md Recipe 1)

# Step 4: Protenix final validation for top 10 candidates
# (see protenix-recipes.md Recipe 1)
```

---

## Recipe 2: Miniprotein Binder Design

Design small (40-60 residue) miniprotein binders — easier to produce, faster to validate.

```bash
python RFdiffusion/scripts/run_inference.py \
  inference.input_pdb=target.pdb \
  'contigmap.contigs=[A1-150/0 40-60]' \
  'ppi.hotspot_res=[A59,A83,A91]' \
  denoiser.noise_scale_ca=0.5 \
  denoiser.noise_scale_frame=0.5 \
  inference.output_prefix=miniprotein/design \
  inference.num_designs=2000

# Lower noise scale = more conservative, higher quality per design
# Compensate with more designs (2000)
```

---

## Recipe 3: Epitope-Focused Vaccine Scaffold

Scaffold a target epitope (e.g., viral surface patch) into a stable protein for vaccine display.

```bash
python RFdiffusion/scripts/run_inference.py \
  inference.input_pdb=antigen.pdb \
  'contigmap.contigs=[15-30/A120-145/15-30]' \
  inference.output_prefix=vaccine_scaffold/design \
  inference.num_designs=500

# Epitope A120-145 is preserved in 3D space
# Flanking regions (15-30 residues each) are designed to stabilize the epitope
```

---

## Recipe 4: Symmetric Nanoparticle Scaffold

Design symmetric oligomers for nanoparticle display (vaccine or drug delivery).

```bash
# C3 trimer — 60-mer nanoparticle building block
python RFdiffusion/scripts/run_inference.py \
  --config-name symmetry \
  inference.symmetry=c3 \
  'contigmap.contigs=[300]' \
  inference.output_prefix=nanoparticle/design \
  inference.num_designs=100

# Each 100-residue monomer is identical
# ProteinMPNN with --homooligomer 1 for symmetric sequence design
```
