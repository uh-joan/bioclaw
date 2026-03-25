# BioEmu Recipes

> CLI commands for conformational ensemble sampling.
> Parent skill: [SKILL.md](SKILL.md) — full BioEmu workflow.

---

## Recipe 1: Generate Conformational Ensemble

```bash
python -m bioemu.sample \
  --sequence MPROTEINSEQUENCEHERE \
  --num_samples 500 \
  --output_dir ensemble/ \
  --model_name v1.2

# Output: ensemble/samples.pdb + ensemble/samples.xtc
```

---

## Recipe 2: Steered Sampling (Higher Physical Quality)

```bash
python -m bioemu.sample \
  --sequence MPROTEINSEQUENCEHERE \
  --num_samples 500 \
  --output_dir steered/ \
  --steering_config src/bioemu/config/steering/physical_steering.yaml \
  --denoiser_config src/bioemu/config/denoiser/stochastic_dpm.yaml
```

---

## Recipe 3: Analyze Ensemble with MDTraj

```python
import mdtraj as md
import numpy as np

t = md.load('ensemble/samples.xtc', top='ensemble/samples.pdb')
print(f"Ensemble: {t.n_frames} conformations, {t.n_residues} residues")

# RMSD distribution (conformational diversity)
rmsd_to_first = md.rmsd(t, t, 0)
print(f"RMSD range: {rmsd_to_first.min():.2f} - {rmsd_to_first.max():.2f} nm")
print(f"Mean RMSD: {np.mean(rmsd_to_first):.2f} nm")

# Radius of gyration (compactness variation)
rg = md.compute_rg(t)
print(f"Rg range: {rg.min():.2f} - {rg.max():.2f} nm")

# Cluster conformations
from sklearn.cluster import KMeans
ca_indices = t.topology.select('name CA')
coords = t.xyz[:, ca_indices].reshape(t.n_frames, -1)
kmeans = KMeans(n_clusters=5, random_state=42).fit(coords)
print(f"\n5 conformational clusters:")
for i in range(5):
    members = np.sum(kmeans.labels_ == i)
    print(f"  Cluster {i}: {members} members ({100*members/t.n_frames:.0f}%)")
```

---

## Recipe 4: Compare Ensemble to Predicted Structure

```python
import mdtraj as md
import numpy as np

# Load predicted structure (from ColabFold/Boltz)
pred = md.load('predicted.pdb')

# Load BioEmu ensemble
ensemble = md.load('ensemble/samples.xtc', top='ensemble/samples.pdb')

# RMSD of each ensemble member to prediction
rmsds = md.rmsd(ensemble, pred, 0)
print(f"Ensemble RMSD to prediction: {np.mean(rmsds):.2f} ± {np.std(rmsds):.2f} nm")
print(f"Closest: {np.min(rmsds):.3f} nm, Farthest: {np.max(rmsds):.3f} nm")

fraction_close = np.mean(rmsds < 0.2)
print(f"Fraction within 2A of prediction: {fraction_close:.0%}")
```
