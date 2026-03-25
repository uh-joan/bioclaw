# Proteina-Complexa Recipes

> Copy-paste CLI commands for atomistic binder and enzyme design.
> Parent skill: [SKILL.md](SKILL.md) — full Proteina-Complexa workflow.

---

## Recipe 1: Protein Binder with Beam Search

Design binders using inference-time search for highest quality.

```bash
complexa design configs/search_binder_local_pipeline.yaml \
  ++run_name=pdl1_binders \
  ++generation.task_name=02_PDL1 \
  ++generation.search_algorithm=beam-search \
  ++generation.num_designs=500
```

---

## Recipe 2: Quick Single-Pass Screening

Fast screening without inference-time search.

```bash
complexa design configs/search_binder_local_pipeline.yaml \
  ++run_name=quick_screen \
  ++generation.task_name=02_PDL1 \
  ++generation.search_algorithm=single-pass \
  ++generation.num_designs=2000
```

---

## Recipe 3: Small-Molecule Ligand Binder

Design proteins to bind a small-molecule ligand.

```bash
complexa design configs/ligand_binder_pipeline.yaml \
  ++run_name=atp_binder \
  ++generation.task_name=ATP \
  ++generation.search_algorithm=beam-search \
  ++generation.num_designs=500
```

---

## Recipe 4: AME Enzyme Scaffolding

Scaffold an enzyme active site around a catalytic motif + ligand.

```bash
complexa design configs/ame_pipeline.yaml \
  ++run_name=enzyme_design \
  ++generation.task_name=phosphoglycerate_kinase \
  ++generation.search_algorithm=beam-search \
  ++generation.num_designs=500
```

---

## Recipe 5: MCTS for Maximum Diversity

Use Monte Carlo tree search for diverse exploration.

```bash
complexa design configs/search_binder_local_pipeline.yaml \
  ++run_name=diverse_campaign \
  ++generation.task_name=02_PDL1 \
  ++generation.search_algorithm=mcts \
  ++generation.num_designs=1000
```

---

## Recipe 6: Analyze Results

```python
import pandas as pd

df = pd.read_csv("results/pdl1_binders/summary_metrics.csv")
print(f"Total: {len(df)}, Pass i_pAE<10: {len(df[df['i_pAE']<10])}")

top = df.nsmallest(10, "i_pAE")
for _, r in top.iterrows():
    print(f"  {r.get('name','?')}: i_pAE={r['i_pAE']:.1f} "
          f"i_pTM={r.get('i_pTM',0):.3f} scRMSD={r.get('scRMSD',0):.2f}A")
```
