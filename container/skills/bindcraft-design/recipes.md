# BindCraft Recipes

> Copy-paste CLI commands and settings templates for automated binder design.
> Parent skill: [SKILL.md](SKILL.md) — full BindCraft workflow and settings guide.

---

## Recipe 1: Standard Binder Design Campaign

Design 100 binders targeting specific hotspot residues on a protein target.

```bash
# Write target settings
cat > settings_target/my_target.json << 'JSON'
{
  "design_path": "./designs/my_target/",
  "binder_name": "my_target",
  "starting_pdb": "./targets/my_target.pdb",
  "chains": "A",
  "target_hotspot_residues": "56,83,91",
  "lengths": [65, 120],
  "number_of_final_designs": 100
}
JSON

# Run (unattended — will stop when 100 accepted designs reached)
python -u BindCraft/bindcraft.py \
  --settings settings_target/my_target.json \
  --filters BindCraft/settings_filters/default_filters.json \
  --advanced BindCraft/settings_advanced/default_4stage_multimer.json

# Monitor progress
tail -f designs/my_target/trajectory_stats.csv | head -5
```

---

## Recipe 2: Hard Target (Low Initial Success Rate)

For targets where default settings produce few passing designs, enable initial guess bias.

```bash
cat > settings_target/hard_target.json << 'JSON'
{
  "design_path": "./designs/hard_target/",
  "binder_name": "hard_target",
  "starting_pdb": "./targets/hard_target.pdb",
  "chains": "A",
  "target_hotspot_residues": "120,145,200",
  "lengths": [80, 150],
  "number_of_final_designs": 50
}
JSON

python -u BindCraft/bindcraft.py \
  --settings settings_target/hard_target.json \
  --filters BindCraft/settings_filters/relaxed_filters.json \
  --advanced BindCraft/settings_advanced/default_4stage_multimer_hardtarget.json

# hardtarget preset enables predict_initial_guess=true
# relaxed_filters increases pass rate for difficult targets
```

---

## Recipe 3: Peptide Binder Design

Design short peptide binders (8-30 residues) with helical bias.

```bash
cat > settings_target/peptide_target.json << 'JSON'
{
  "design_path": "./designs/peptide/",
  "binder_name": "peptide_binder",
  "starting_pdb": "./targets/target.pdb",
  "chains": "A",
  "target_hotspot_residues": "30,45,60",
  "lengths": [10, 25],
  "number_of_final_designs": 200
}
JSON

python -u BindCraft/bindcraft.py \
  --settings settings_target/peptide_target.json \
  --filters BindCraft/settings_filters/peptide_filters.json \
  --advanced BindCraft/settings_advanced/peptide_3stage_multimer.json

# peptide preset: 3-stage algorithm, high helicity (0.95), no cysteines,
# initial_guess enabled, no Rg loss, tighter acceptance monitoring
```

---

## Recipe 4: Let AF2 Choose the Binding Site

Design binders without specifying hotspots — AF2 finds the best binding site.

```bash
cat > settings_target/auto_site.json << 'JSON'
{
  "design_path": "./designs/auto_site/",
  "binder_name": "auto_binder",
  "starting_pdb": "./targets/target.pdb",
  "chains": "A",
  "target_hotspot_residues": null,
  "lengths": [65, 120],
  "number_of_final_designs": 50
}
JSON

python -u BindCraft/bindcraft.py \
  --settings settings_target/auto_site.json

# null hotspot = AF2 discovers optimal binding interface
# Useful for exploring unknown targets
```

---

## Recipe 5: Beta-Sheet Binder Design

Bias designs toward beta-sheet content (useful when target interface is a beta-sheet).

```bash
python -u BindCraft/bindcraft.py \
  --settings settings_target/my_target.json \
  --filters BindCraft/settings_filters/default_filters.json \
  --advanced BindCraft/settings_advanced/betasheet_4stage_multimer.json
```

---

## Recipe 6: Analyze BindCraft Results

Parse the output CSVs to find top candidates.

```python
import pandas as pd

# Load accepted designs
df = pd.read_csv("designs/my_target/final_design_stats.csv")

print(f"Accepted designs: {len(df)}")
print(f"\nTop 10 by i_pTM (interface confidence):")
top = df.nlargest(10, "Average_i_pTM")
for _, row in top.iterrows():
    print(f"  {row['Design']: <30} i_pTM={row['Average_i_pTM']:.3f} "
          f"pLDDT={row['Average_pLDDT']:.3f} "
          f"dG={row.get('Average_Rosetta_dG', 'N/A')}")

# Check failure reasons
failures = pd.read_csv("designs/my_target/failure_csv.csv")
print(f"\nTop failure reasons:")
print(failures.nlargest(5, "Count")[["Filter", "Count"]].to_string(index=False))
```

---

## Recipe 7: Flexible Target (Conformational Heterogeneity)

For targets that change conformation upon binding, remove template sequence during design.

```bash
python -u BindCraft/bindcraft.py \
  --settings settings_target/flexible_target.json \
  --filters BindCraft/settings_filters/relaxed_filters.json \
  --advanced BindCraft/settings_advanced/default_4stage_multimer_flexible.json

# flexible preset: rm_template_seq_design/predict=true
# allows target backbone flexibility during hallucination and validation
```

---

## Recipe 8: BindCraft → Boltz-2 Affinity Validation

After BindCraft generates accepted designs, run top candidates through Boltz-2 for affinity estimation.

```bash
# Extract top BindCraft designs
python3 << 'PYTHON'
import pandas as pd, os

df = pd.read_csv("designs/my_target/final_design_stats.csv")
top = df.nlargest(10, "Average_i_pTM")

os.makedirs("boltz_validation/", exist_ok=True)
for _, row in top.iterrows():
    name = row["Design"]
    pdb_path = f"designs/my_target/Accepted/{name}.pdb"
    # Convert to Boltz YAML with affinity prediction
    # (Extract sequences from PDB, write YAML)
    print(f"Prepared {name} for Boltz-2 affinity validation")
PYTHON

# Run Boltz-2 on each (see boltz-predict recipes)
# boltz predict boltz_validation/ --diffusion_samples_affinity 5
```

---

## Recipe 9: Multi-Chain Target

Target a specific chain in a multi-chain complex.

```bash
cat > settings_target/multichain.json << 'JSON'
{
  "design_path": "./designs/multichain/",
  "binder_name": "multichain",
  "starting_pdb": "./targets/complex.pdb",
  "chains": "A",
  "target_hotspot_residues": "A56,A83",
  "lengths": [70, 100],
  "number_of_final_designs": 50
}
JSON

# Only chain A is targeted; other chains are ignored
python -u BindCraft/bindcraft.py --settings settings_target/multichain.json
```

---

## Recipe 10: SLURM HPC Submission

Submit BindCraft as a SLURM job for long-running campaigns.

```bash
# Edit bindcraft.slurm to set GPU partition, time limit, etc.
sbatch BindCraft/bindcraft.slurm \
  --settings './settings_target/my_target.json' \
  --filters './settings_filters/default_filters.json' \
  --advanced './settings_advanced/default_4stage_multimer.json'

# Monitor
squeue -u $USER
tail -f designs/my_target/trajectory_stats.csv
```
