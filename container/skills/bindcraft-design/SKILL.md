---
name: bindcraft-design
description: "End-to-end automated protein binder design using BindCraft. Runs unattended: hallucinate backbone via AF2 backpropagation, ProteinMPNN sequence design, AF2 cross-validation, PyRosetta scoring, and multi-metric filtering in a single loop until target number of passing designs is reached. Supports hotspot targeting, peptide binders, hard targets, beta-sheet binders. Use when user mentions BindCraft, automated binder design, end-to-end binder, unattended binder design, AF2 hallucination, binder campaign, or one-click binder design."
---

# BindCraft — End-to-End Automated Binder Design

> **Code recipes**: See [recipes.md](recipes.md) for copy-paste CLI commands and settings templates.

Fully automated protein binder design pipeline. Given a target PDB, BindCraft runs unattended — hallucinating binder backbones via AF2 backpropagation, designing sequences with ProteinMPNN, cross-validating with AF2, scoring with PyRosetta, and filtering — until the requested number of passing designs is accumulated.

**When to use BindCraft vs RFdiffusion pipeline:**
- **BindCraft** — fully automated, single command, integrated scoring/filtering, runs unattended. Best for standard binder campaigns where you want results without manual intervention.
- **RFdiffusion + ProteinMPNN** — more control over each step, can use different validation tools (Boltz-2, Protenix), supports motif scaffolding and symmetric oligomers (which BindCraft doesn't). Better for custom workflows.

## Report-First Workflow

1. **Create report file immediately**: `[target]_bindcraft_design_report.md`
2. **Add placeholders**: Mark each section `[Designing...]`
3. **Populate progressively**: Update as designs accumulate
4. **Final verification**: Report accepted design count and top candidates

## When NOT to Use This Skill

- Motif scaffolding or symmetric oligomer design → use `rfdiffusion-design`
- Manual control over backbone generation → use `rfdiffusion-design`
- Sequence design from an existing backbone → use `proteinmpnn-design`
- Structure prediction only → use `colabfold-predict`, `boltz-predict`, `protenix-predict`
- Drug-ligand docking or affinity → use `boltz-predict`

## Cross-Reference: Other Skills

- **Manual binder design pipeline** → use rfdiffusion-design + proteinmpnn-design + colabfold-predict
- **Post-design affinity estimation** → use boltz-predict (binding affinity for top BindCraft outputs)
- **Post-design highest-accuracy validation** → use protenix-predict (inference scaling)
- **Peptide binder design** → BindCraft has a peptide mode (see recipes)
- **Full therapeutic pipeline context** → use protein-therapeutic-design skill

## Tool: BindCraft CLI

### Installation Check

```bash
conda activate BindCraft 2>/dev/null || {
  git clone https://github.com/martinpacesa/BindCraft.git
  cd BindCraft && bash install_bindcraft.sh --cuda '12.4' --pkg_manager 'conda'
}
```

### Core Command

```bash
python -u BindCraft/bindcraft.py \
  --settings settings_target/my_target.json \
  --filters settings_filters/default_filters.json \
  --advanced settings_advanced/default_4stage_multimer.json
```

### Three Config Files

| Config | Purpose | Required |
|--------|---------|----------|
| `--settings` | Target-specific: PDB path, chains, hotspots, lengths, design count | **Yes** |
| `--filters` | Acceptance thresholds for ~35+ metrics | No (defaults to `default_filters.json`) |
| `--advanced` | Design algorithm, AF2 parameters, loss weights | No (defaults to `default_4stage_multimer.json`) |

## Target Settings JSON

```json
{
  "design_path": "/path/to/output/",
  "binder_name": "my_target",
  "starting_pdb": "/path/to/target.pdb",
  "chains": "A",
  "target_hotspot_residues": "56,83,91",
  "lengths": [65, 120],
  "number_of_final_designs": 100
}
```

| Field | Description |
|-------|-------------|
| `design_path` | Output directory |
| `binder_name` | Name prefix for all outputs |
| `starting_pdb` | Target PDB file (trim to smallest relevant portion) |
| `chains` | Which chains to target |
| `target_hotspot_residues` | Residues to target: `"1,2-10"`, `"A1-10,B1-20"`, `"A"` (entire chain), or `null` (AF2 chooses) |
| `lengths` | `[min, max]` binder length range |
| `number_of_final_designs` | Stop after this many filter-passing designs |

## Advanced Settings Presets

| Preset | Use when |
|--------|----------|
| `default_4stage_multimer` | Standard — most targets |
| `default_4stage_multimer_hardtarget` | Difficult targets (enables initial guess bias) |
| `default_4stage_multimer_flexible` | Target has conformational flexibility |
| `betasheet_4stage_multimer` | Beta-sheet binders preferred |
| `peptide_3stage_multimer` | Short peptide binders (8-30 residues) |

## Filter Presets

| Preset | Stringency |
|--------|-----------|
| `default_filters.json` | Standard — balanced pass rate |
| `relaxed_filters.json` | More permissive — higher throughput |
| `peptide_filters.json` | Tuned for peptide binders |
| `no_filters.json` | Accept everything (for analysis) |

## Output Structure

```
design_path/
├── Accepted/          ← Final passing designs (PDBs)
│   ├── Animation/     ← HTML trajectory animations
│   └── Plots/         ← PNG trajectory plots
├── Rejected/          ← Designs that failed filters
├── Trajectory/        ← Raw + relaxed hallucinated backbones
├── MPNN/              ← MPNN-redesigned complexes
│   ├── Relaxed/       ← Relaxed MPNN complexes
│   └── Binder/        ← Binder monomer predictions
├── trajectory_stats.csv
├── mpnn_design_stats.csv
├── final_design_stats.csv     ← Key output: all accepted designs + metrics
└── failure_csv.csv            ← Filter failure breakdown
```

## Key Metrics in Output CSVs

| Metric | Range | Good value |
|--------|-------|-----------|
| `pLDDT` | 0-1 | > 0.8 |
| `i_pTM` | 0-1 | > 0.6 |
| `pAE` | Angstroms | < 10 |
| `i_pAE` | Angstroms | < 10 |
| `Rosetta_dG` | kcal/mol | < -30 |
| `Shape_complementarity` | 0-1 | > 0.55 |
| `Interface_SASA` | A² | > 500 |
| `Binder_pLDDT` | 0-1 | > 0.85 |
| `Binder_RMSD` | Angstroms | < 2.0 |

## The Internal Loop

```
while accepted < number_of_final_designs:
  1. Sample random length [min, max] and seed
  2. AF2 hallucination (4-stage: logits → softmax → onehot → PSSM)
     - Early terminate if pLDDT < 0.65 at stage checkpoints
  3. PyRosetta relax + clash check
  4. ProteinMPNN: 20 sequences per trajectory
  5. AF2 cross-validation (use OTHER model than design)
  6. Binder monomer prediction (folds independently?)
  7. Full PyRosetta scoring (~35 metrics)
  8. Filter check → Accepted/ or Rejected/
  9. Monitor acceptance rate → auto-halt if < 1%
```

## Tiered Execution (Timeout Resilience)

### Tier 1 — MUST COMPLETE (first 5 min)
```
1. Prepare target PDB (trim, identify hotspots)
2. Write target settings JSON
3. Start BindCraft run (it manages itself)
>>> CHECKPOINT: Report settings and initial status <<<
```

### Tier 2 — MONITORING (ongoing)
```
4. BindCraft runs autonomously — monitor trajectory_stats.csv
5. Report acceptance rate and first accepted designs
>>> CHECKPOINT: Interim progress report <<<
```

### Tier 3 — COMPLETION
```
6. BindCraft stops when target designs reached
7. Analyze final_design_stats.csv
8. Optional: run top designs through Boltz-2/Protenix for additional validation
>>> FINAL: Complete design report with top candidates <<<
```

## Completeness Checklist

- [ ] Target PDB prepared (trimmed to relevant domain)
- [ ] Hotspot residues identified
- [ ] Settings JSON written with appropriate lengths and design count
- [ ] Advanced settings preset chosen (default/hardtarget/peptide)
- [ ] BindCraft run launched
- [ ] Acceptance rate monitored
- [ ] final_design_stats.csv analyzed for top candidates
- [ ] Top candidates optionally validated with Boltz-2/Protenix
