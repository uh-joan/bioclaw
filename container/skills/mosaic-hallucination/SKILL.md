---
name: mosaic-hallucination
description: "Modular hallucination-based protein binder design using Mosaic. Optimizes a PSSM against composable loss terms (IPTM, PAE, contacts, inverse folding recovery) via gradient backpropagation through structure prediction models (Boltz-2, Protenix, AF2). Won Adaptyv Nipah competition with 90% in vitro success rate. Use when user mentions Mosaic, hallucination-based design, PSSM optimization, gradient-based binder design, composable loss protein design, Adaptyv competition, or Escalante Bio."
---

# Mosaic — Modular Hallucination-Based Binder Design

> **Code recipes**: See [recipes.md](recipes.md) for Python templates.

Modular framework for gradient-based protein binder design. Optimizes a soft PSSM via backpropagation through frozen structure prediction models (Boltz-2, Protenix, AF2, OpenFold3). User-composable loss functions: IPTM, PAE, contacts, inverse folding recovery (ProteinMPNN), pLDDT, and custom terms. Won the Adaptyv Nipah binder competition with 90% in vitro success (9/10 designs bound).

**When to use Mosaic vs alternatives:**
- **Mosaic** — maximum control over optimization objective, swappable predictors, research/experimental
- **BindCraft** — production-ready automated pipeline, less tuning needed
- **BoltzGen** — generative (sampling), not hallucination; faster per design, needs more candidates

## Tool: Mosaic (Python API)

```bash
uv sync --group jax-cuda  # Install with JAX CUDA support
```

### Core Usage

```python
from mosaic.structure_prediction import TargetChain
from mosaic.models.protenix import Protenix2025
from mosaic.optimizers import simplex_APGM
import mosaic.losses.structure_prediction as sp
from mosaic.losses.inverse_folding import InverseFoldingSequenceRecovery

model = Protenix2025()
features, _ = model.binder_features(binder_length=80, chains=[TargetChain(target_seq)])

loss = model.build_loss(
    loss=sp.BinderTargetContact() + sp.WithinBinderContact()
         + 10.0 * InverseFoldingSequenceRecovery(mpnn, temp=0.001)
         + 0.05 * sp.TargetBinderPAE() + 0.4 * sp.WithinBinderPAE()
         + 0.025 * sp.IPTMLoss() + 0.1 * sp.PLDDTLoss(),
    features=features, recycling_steps=2
)

_, optimized_pssm = simplex_APGM(loss_function=loss, x=initial_pssm,
    n_steps=100, stepsize=0.2, momentum=0.3)
sequence = "".join("ACDEFGHIKLMNPQRSTVWY"[i] for i in optimized_pssm.argmax(axis=1))
```

### Composable Loss Terms

| Term | Weight (Nipah winning) | Purpose |
|------|----------------------|---------|
| `BinderTargetContact()` | 1.0 | Interface contacts |
| `WithinBinderContact()` | 1.0 | Binder compactness |
| `InverseFoldingSequenceRecovery()` | **10.0** | Designability (critical) |
| `TargetBinderPAE()` | 0.05 | Interface PAE |
| `WithinBinderPAE()` | 0.4 | Internal PAE |
| `IPTMLoss()` | 0.025 | Interface pTM |
| `PLDDTLoss()` | 0.1 | Local confidence |

## Completeness Checklist

- [ ] Target sequence provided
- [ ] Loss function composed with appropriate weights
- [ ] PSSM optimization completed (100+ steps)
- [ ] Discrete sequence extracted via argmax
- [ ] Refolding validation (Boltz-2/Protenix/AF2)
