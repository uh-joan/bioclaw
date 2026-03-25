# RFdiffusion3 Recipes

> Copy-paste CLI commands for all-atom biomolecular design.
> Parent skill: [SKILL.md](SKILL.md) — full RFD3 workflow.

---

## Recipe 1: Protein Binder Design (All-Atom)

```bash
rfd3 design out_dir=binder_output/ \
  inputs=binder_spec.json \
  dump_trajectories=True
# Output: full atomistic PDBs with sidechains (no ProteinMPNN needed)
```

---

## Recipe 2: DNA-Binding Protein Design

```bash
# RFD3 jointly designs protein + predicts DNA conformation
rfd3 design out_dir=dna_binder/ \
  inputs=dna_design_spec.json
# Input spec includes DNA sequence; protein is generated de novo
```

---

## Recipe 3: Enzyme Active Site Scaffolding (90% Success)

```bash
# Catalytic triad scaffolding — all-atom with sidechain placement
rfd3 design out_dir=enzyme_scaffold/ \
  inputs=active_site_spec.json
# No separate ProteinMPNN step needed — sidechains are co-designed
```

---

## Recipe 4: Binder Design Campaign

```bash
# Generate 1000 all-atom binder designs
for i in $(seq 0 999); do
  rfd3 design out_dir=campaign/design_${i}/ \
    inputs=target_spec.json &
  # Limit parallelism
  [ $((i % 4)) -eq 3 ] && wait
done
wait

# All outputs have full sidechains — validate directly with Protenix
```

---

## Recipe 5: Compare RFD3 vs RFD1

```bash
# RFD3: all-atom, single step
rfd3 design out_dir=rfd3_out/ inputs=spec.json

# RFD1: backbone only, needs ProteinMPNN
python RFdiffusion/scripts/run_inference.py \
  'contigmap.contigs=[A1-150/0 80-100]' \
  inference.input_pdb=target.pdb \
  inference.output_prefix=rfd1_out/design \
  inference.num_designs=10

# Then ProteinMPNN for RFD1 outputs
python ProteinMPNN/protein_mpnn_run.py \
  --pdb_path rfd1_out/design_0.pdb \
  --out_folder rfd1_mpnn/ --num_seq_per_target 2

# RFD3 outputs already have sequences — validate both with ColabFold
```
