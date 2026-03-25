# Mosaic Recipes

> Python templates for gradient-based hallucination binder design.
> Parent skill: [SKILL.md](SKILL.md) — full Mosaic workflow.

---

## Recipe 1: Standard Binder Hallucination (Nipah-Winning Config)

```python
import jax
from mosaic.structure_prediction import TargetChain
from mosaic.models.protenix import Protenix2025
from mosaic.optimizers import simplex_APGM, sharpening
import mosaic.losses.structure_prediction as sp
from mosaic.losses.inverse_folding import InverseFoldingSequenceRecovery
from mosaic.models.inverse_folding import ProteinMPNN
import math

target_seq = "MTARGETSEQUENCE"
binder_length = 80

model = Protenix2025()
mpnn = ProteinMPNN()
features, _ = model.binder_features(binder_length=binder_length, chains=[TargetChain(target_seq)])

loss = model.build_loss(
    loss=(sp.BinderTargetContact() + sp.WithinBinderContact()
          + 10.0 * InverseFoldingSequenceRecovery(mpnn, temp=0.001)
          + 0.05 * sp.TargetBinderPAE() + 0.05 * sp.BinderTargetPAE()
          + 0.4 * sp.WithinBinderPAE()
          + 0.025 * sp.IPTMLoss() + 0.025 * sp.pTM()
          + 0.1 * sp.PLDDTLoss()),
    features=features, recycling_steps=2
)

# Phase 1: Soft optimization
key = jax.random.PRNGKey(42)
pssm = jax.nn.softmax(0.5 * jax.random.gumbel(key, (binder_length, 20)))
_, pssm = simplex_APGM(loss, pssm, n_steps=100, stepsize=0.2*math.sqrt(binder_length), momentum=0.3)

# Phase 2-3: Sharpening
_, pssm = sharpening(loss, pssm, n_steps=50, stepsize=0.5*math.sqrt(binder_length), scale=1.25)
_, pssm = sharpening(loss, pssm, n_steps=15, stepsize=0.5*math.sqrt(binder_length), scale=1.4)

sequence = "".join("ACDEFGHIKLMNPQRSTVWY"[i] for i in pssm.argmax(axis=1))
print(f"Designed: {sequence}")
```

---

## Recipe 2: Batch Design with Modal (GPU Cloud)

```bash
# hallucinate.py uses Modal for distributed GPU runs
uvx modal run hallucinate.py --workers 4 --max-time-hours 2.0
# Generates multiple designs in parallel on cloud GPUs
```

---

## Recipe 3: Custom Loss — Maximize Helicity

```python
from mosaic.losses.structure_prediction import SecondaryStructure

loss = model.build_loss(
    loss=(sp.BinderTargetContact() + sp.WithinBinderContact()
          + 10.0 * InverseFoldingSequenceRecovery(mpnn, temp=0.001)
          + 1.0 * SecondaryStructure(target_fraction_helix=0.8)),
    features=features, recycling_steps=2
)
```

---

## Recipe 4: Swap Structure Predictor (Boltz-2)

```python
from mosaic.models.boltz import Boltz2

model = Boltz2()  # Instead of Protenix2025
features, _ = model.binder_features(binder_length=80, chains=[TargetChain(target_seq)])
# Same loss composition works with any predictor
```
