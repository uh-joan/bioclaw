# RFdiffusion Enzyme Engineering Recipes

Recipes for de novo enzyme scaffold generation using RFdiffusion. Design novel protein backbones that embed catalytic residues in the correct 3D geometry, then sequence with ProteinMPNN and validate.

> **Parent skill**: [SKILL.md](SKILL.md) — full enzyme engineering pipeline.
> **See also**: [rfdiffusion-design skill](../rfdiffusion-design/SKILL.md) — standalone RFdiffusion with full CLI and contig syntax.

---

## Recipe 1: Catalytic Triad Scaffolding (ActiveSite Model)

Design a novel enzyme scaffold around a catalytic triad using the specialized ActiveSite checkpoint.

```bash
# Input: minimal PDB with only the catalytic residues (Ser, His, Asp)
# positioned in correct 3D geometry

python RFdiffusion/scripts/run_inference.py \
  inference.input_pdb=catalytic_triad.pdb \
  'contigmap.contigs=[10-20/A82-82/5-10/A153-153/5-10/A217-217/10-20]' \
  inference.ckpt_override_path=RFdiffusion/models/ActiveSite_ckpt.pt \
  inference.output_prefix=enzyme_scaffold/design \
  inference.num_designs=500

# Individual catalytic residues (82, 153, 217) are fixed in space
# Linker segments (5-20 residues) are generated around them
# ActiveSite model handles very small, sparse motifs

# Next: ProteinMPNN with fixed catalytic residues
python ProteinMPNN/protein_mpnn_run.py \
  --pdb_path enzyme_scaffold/design_0.pdb \
  --fixed_positions_jsonl fixed_catalytic.jsonl \
  --out_folder enzyme_seqs/ \
  --num_seq_per_target 4 \
  --sampling_temp "0.1"
```

---

## Recipe 2: Substrate Binding Pocket Design

Design a new enzyme scaffold with a pre-shaped substrate binding pocket.

```bash
# Input: catalytic residues + key pocket-lining residues
python RFdiffusion/scripts/run_inference.py \
  inference.input_pdb=pocket_motif.pdb \
  'contigmap.contigs=[8-15/A45-48/3-8/A78-82/3-8/A109-112/3-8/A153-156/8-15]' \
  inference.ckpt_override_path=RFdiffusion/models/ActiveSite_ckpt.pt \
  inference.output_prefix=pocket_design/design \
  inference.num_designs=500

# Multiple motif segments define the pocket geometry
# RFdiffusion generates a scaffold that maintains the pocket shape

# Validate: dock substrate with Boltz-2 after ProteinMPNN sequencing
```

---

## Recipe 3: De Novo Enzyme from Theozyme

Full pipeline from a computational theozyme (transition state model) to a designed enzyme.

```bash
# Step 1: RFdiffusion scaffolds the theozyme
python RFdiffusion/scripts/run_inference.py \
  inference.input_pdb=theozyme.pdb \
  'contigmap.contigs=[15-25/A1-1/5-10/A2-2/5-10/A3-3/15-25]' \
  inference.ckpt_override_path=RFdiffusion/models/ActiveSite_ckpt.pt \
  inference.output_prefix=theozyme_scaffold/design \
  inference.num_designs=1000

# Step 2: ProteinMPNN sequences (fix catalytic residues)
# Step 3: ColabFold self-consistency check
# Step 4: Boltz-2 dock substrate to verify active site accessibility
# Step 5: Protenix highest-accuracy validation of top candidates
```

---

## Recipe 4: Enzyme Partial Diffusion (Scaffold Diversification)

Diversify an existing enzyme scaffold to explore stability/activity landscape.

```bash
python RFdiffusion/scripts/run_inference.py \
  inference.input_pdb=existing_enzyme.pdb \
  'contigmap.contigs=[A1-250]' \
  diffuser.partial_T=15 \
  inference.output_prefix=diversified/design \
  inference.num_designs=100

# partial_T=15: modest diversification, preserves overall fold
# The active site geometry will shift — validate with ColabFold
# Use ProteinMPNN with fixed catalytic residues on diversified backbones
```
