# BindCraft Protein Therapeutic Design Recipes

Recipes for end-to-end automated binder design within the protein therapeutic pipeline. BindCraft runs the entire hallucination → MPNN → AF2 validation → scoring → filtering loop unattended.

> **Parent skill**: [SKILL.md](SKILL.md) — full protein therapeutic design pipeline.
> **See also**: [bindcraft-design skill](../bindcraft-design/SKILL.md) — standalone BindCraft with full settings reference.

---

## Recipe 1: Automated Binder Campaign (Standard)

Launch a full binder campaign — BindCraft handles everything.

```bash
cat > settings_target/therapeutic_target.json << 'JSON'
{
  "design_path": "./campaign/therapeutic/",
  "binder_name": "therapeutic_binder",
  "starting_pdb": "./targets/target_trimmed.pdb",
  "chains": "A",
  "target_hotspot_residues": "56,83,91",
  "lengths": [65, 120],
  "number_of_final_designs": 100
}
JSON

python -u BindCraft/bindcraft.py \
  --settings settings_target/therapeutic_target.json \
  --filters BindCraft/settings_filters/default_filters.json \
  --advanced BindCraft/settings_advanced/default_4stage_multimer.json

# Runs unattended until 100 accepted designs
# Results in campaign/therapeutic/Accepted/ and final_design_stats.csv
```

---

## Recipe 2: BindCraft vs RFdiffusion — Run Both, Compare

For critical targets, run both approaches and merge the best candidates.

```bash
# Approach A: BindCraft (automated)
python -u BindCraft/bindcraft.py --settings settings_target/target.json

# Approach B: RFdiffusion pipeline (manual, more control)
python RFdiffusion/scripts/run_inference.py \
  inference.input_pdb=target.pdb \
  'contigmap.contigs=[A1-150/0 70-100]' \
  'ppi.hotspot_res=[A56,A83,A91]' \
  inference.output_prefix=rfd_campaign/backbone \
  inference.num_designs=1000
# Then ProteinMPNN → ColabFold → filter

# Compare: merge top candidates from both approaches
# Rank by shared metrics (i_pTM, pLDDT, Rosetta dG)
```

---

## Recipe 3: Peptide Therapeutic Design

Design short peptide binders (8-25 residues) for PPI inhibition.

```bash
cat > settings_target/ppi_peptide.json << 'JSON'
{
  "design_path": "./campaign/peptide/",
  "binder_name": "ppi_inhibitor",
  "starting_pdb": "./targets/ppi_interface.pdb",
  "chains": "A",
  "target_hotspot_residues": "30,45,60",
  "lengths": [10, 25],
  "number_of_final_designs": 200
}
JSON

python -u BindCraft/bindcraft.py \
  --settings settings_target/ppi_peptide.json \
  --filters BindCraft/settings_filters/peptide_filters.json \
  --advanced BindCraft/settings_advanced/peptide_3stage_multimer.json

# Peptide mode: helical bias, no cysteines, 3-stage algorithm
# For cyclic peptides, consider RFdiffusion (inference.cyclic=True) instead
```

---

## Recipe 4: Post-BindCraft Validation Cascade

After BindCraft, validate top designs with additional tools for maximum confidence.

```bash
# 1. BindCraft produces 100 accepted designs
# 2. Extract top 10 by i_pTM from final_design_stats.csv
# 3. Run through Boltz-2 for affinity estimation
# 4. Run through Protenix with inference scaling for highest accuracy

python3 << 'PYTHON'
import pandas as pd

df = pd.read_csv("campaign/therapeutic/final_design_stats.csv")
top10 = df.nlargest(10, "Average_i_pTM")

print("Top BindCraft designs for multi-tool validation:")
for _, row in top10.iterrows():
    print(f"  {row['Design']}: i_pTM={row['Average_i_pTM']:.3f} dG={row.get('Average_Rosetta_dG','N/A')}")

# Next: Boltz-2 affinity → Protenix scaling → experimental ordering
PYTHON
```
