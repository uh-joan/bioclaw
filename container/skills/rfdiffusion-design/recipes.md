# RFdiffusion Recipes

> Copy-paste CLI commands for de novo protein backbone generation.
> Parent skill: [SKILL.md](SKILL.md) — full RFdiffusion workflow and contig syntax.

---

## Recipe 1: Unconditional Backbone Generation

Generate novel protein backbones of a specified length.

```bash
# Generate 10 backbones, each exactly 100 residues
python RFdiffusion/scripts/run_inference.py \
  'contigmap.contigs=[100-100]' \
  inference.output_prefix=unconditional/design \
  inference.num_designs=10

# Variable length (100-200 residues, randomly sampled)
python RFdiffusion/scripts/run_inference.py \
  'contigmap.contigs=[100-200]' \
  inference.output_prefix=variable/design \
  inference.num_designs=10

ls unconditional/*.pdb  # 10 poly-glycine backbone PDBs
```

---

## Recipe 2: Binder Design with Hotspots

Design protein binders targeting specific residues on a target protein.

```bash
python RFdiffusion/scripts/run_inference.py \
  inference.input_pdb=target.pdb \
  'contigmap.contigs=[A1-150/0 70-100]' \
  'ppi.hotspot_res=[A59,A83,A91]' \
  inference.output_prefix=binders/design \
  inference.num_designs=1000

# A1-150 = fix target (chain A, residues 1-150)
# /0 = chain break
# 70-100 = generate 70-100 residue binder
# hotspot_res = binder must contact these target residues

# Next: ProteinMPNN → ColabFold validation
```

---

## Recipe 3: Motif Scaffolding

Embed a functional motif (e.g., binding epitope, catalytic site) into a new protein scaffold.

```bash
python RFdiffusion/scripts/run_inference.py \
  inference.input_pdb=motif_source.pdb \
  'contigmap.contigs=[10-40/A163-181/10-40]' \
  inference.output_prefix=scaffolds/design \
  inference.num_designs=200

# 10-40 new residues | motif A163-181 preserved | 10-40 new residues
# Motif is fixed in 3D space; scaffold is generated around it
```

---

## Recipe 4: Multi-Motif Scaffolding

Scaffold multiple discontinuous motifs into a single protein.

```bash
python RFdiffusion/scripts/run_inference.py \
  inference.input_pdb=motif_source.pdb \
  'contigmap.contigs=[5-15/A163-181/5-15/A200-215/5-15]' \
  inference.output_prefix=multi_motif/design \
  inference.num_designs=200

# Two motifs (A163-181 and A200-215) joined by designed linkers
```

---

## Recipe 5: Symmetric Oligomer (C3, C4, D2)

Design symmetric homo-oligomers with cyclic or dihedral symmetry.

```bash
# C3 trimer (total 300 residues = 100 per chain)
python RFdiffusion/scripts/run_inference.py \
  --config-name symmetry \
  inference.symmetry=c3 \
  'contigmap.contigs=[300]' \
  inference.output_prefix=c3_trimer/design \
  inference.num_designs=50

# C4 tetramer
python RFdiffusion/scripts/run_inference.py \
  --config-name symmetry \
  inference.symmetry=c4 \
  'contigmap.contigs=[400]' \
  inference.output_prefix=c4_tetramer/design \
  inference.num_designs=50

# D2 dihedral
python RFdiffusion/scripts/run_inference.py \
  --config-name symmetry \
  inference.symmetry=d2 \
  'contigmap.contigs=[400]' \
  inference.output_prefix=d2/design \
  inference.num_designs=50
```

---

## Recipe 6: Enzyme Active Site Scaffolding

Scaffold a catalytic triad/dyad with the specialized ActiveSite model.

```bash
# Input PDB has the catalytic residues as a minimal motif
python RFdiffusion/scripts/run_inference.py \
  inference.input_pdb=catalytic_residues.pdb \
  'contigmap.contigs=[10-20/A82-82/5-10/A153-153/5-10/A217-217/10-20]' \
  inference.ckpt_override_path=RFdiffusion/models/ActiveSite_ckpt.pt \
  inference.output_prefix=enzyme/design \
  inference.num_designs=500

# Individual catalytic residues (82, 153, 217) are fixed
# Linker residues (5-20) are generated between them
# ActiveSite checkpoint is optimized for very small motifs

# Next: ProteinMPNN with fixed catalytic residues → ColabFold validation
```

---

## Recipe 7: Fold-Conditioned Binder Design

Design binders constrained to a specific fold topology.

```bash
# Step 1: Generate secondary structure and adjacency files from a template
python RFdiffusion/helper_scripts/make_secstruc_adj.py \
  --input_pdb fold_template.pdb \
  --out_dir ss_adj_files/

# Step 2: Generate fold-conditioned binders
python RFdiffusion/scripts/run_inference.py \
  inference.input_pdb=target.pdb \
  scaffoldguided.scaffoldguided=True \
  scaffoldguided.scaffold_dir=ss_adj_files/ \
  'contigmap.contigs=[A1-150/0 70-100]' \
  'ppi.hotspot_res=[A59,A83,A91]' \
  inference.output_prefix=fold_binder/design \
  inference.num_designs=200
```

---

## Recipe 8: Partial Diffusion (Diversify Existing Design)

Take an existing protein and generate structural variants via partial noise+denoise.

```bash
# Input: existing protein structure
# partial_T=20 means add noise for 20 steps (out of 50), then denoise
python RFdiffusion/scripts/run_inference.py \
  inference.input_pdb=existing_design.pdb \
  'contigmap.contigs=[A1-100]' \
  diffuser.partial_T=20 \
  inference.output_prefix=diversified/design \
  inference.num_designs=50

# Lower partial_T = closer to original (subtle variations)
# Higher partial_T = more divergent (broader exploration)
```

---

## Recipe 9: Macrocyclic Peptide Binder

Design cyclic peptide binders (8-15 residues).

```bash
python RFdiffusion/scripts/run_inference.py \
  inference.input_pdb=target.pdb \
  'contigmap.contigs=[A1-100/0 8-15]' \
  'ppi.hotspot_res=[A30,A45,A60]' \
  inference.cyclic=True \
  'inference.cyc_chains=["b"]' \
  inference.output_prefix=cyclic_peptide/design \
  inference.num_designs=500

# Chain B (the peptide) is cyclized
# Use Chai-1 for cyclic peptide structure validation
```

---

## Recipe 10: Full Binder Design Campaign (RFdiffusion → ProteinMPNN → ColabFold)

Production binder design workflow following the Baker Lab pipeline.

```bash
# Step 1: Generate 1000 backbones
python RFdiffusion/scripts/run_inference.py \
  inference.input_pdb=target.pdb \
  'contigmap.contigs=[A1-150/0 70-100]' \
  'ppi.hotspot_res=[A59,A83,A91]' \
  inference.output_prefix=campaign/backbone \
  inference.num_designs=1000

# Step 2: Design sequences with ProteinMPNN (2 per backbone)
for pdb in campaign/backbone_*.pdb; do
  name=$(basename "$pdb" .pdb)
  python ProteinMPNN/protein_mpnn_run.py \
    --pdb_path "$pdb" \
    --pdb_path_chains "B" \
    --out_folder campaign/mpnn/${name}/ \
    --num_seq_per_target 2 \
    --sampling_temp "0.1" \
    --seed 37
done

# Step 3: Extract all designed binder sequences for validation
python3 << 'PYTHON'
import glob

designs = []
for fa in sorted(glob.glob("campaign/mpnn/*/seqs/*.fa")):
    with open(fa) as f:
        h, s = None, ""
        for line in f:
            if line.startswith(">"):
                if h and s and "sample=" in h:
                    name = fa.split("/")[-3] + "_" + h.split("sample=")[1].split(",")[0]
                    binder_seq = s.split("/")[-1] if "/" in s else s  # chain B
                    designs.append((name, binder_seq))
                h, s = line, ""
            else:
                s += line.strip()
        if h and s and "sample=" in h:
            name = fa.split("/")[-3] + "_" + h.split("sample=")[1].split(",")[0]
            binder_seq = s.split("/")[-1] if "/" in s else s
            designs.append((name, binder_seq))

with open("campaign/all_binder_seqs.fasta", "w") as f:
    for name, seq in designs:
        f.write(f">{name}\n{seq}\n")
print(f"Extracted {len(designs)} binder sequences for validation")
PYTHON

# Step 4: Validate with ColabFold (predict binder+target complex)
# Filter: pae_interaction < 10, pLDDT > 80, RMSD to target backbone < 2A

# Step 5: Optional — Boltz-2 affinity for top candidates
# Step 6: Optional — Protenix with inference scaling for final candidates
```
