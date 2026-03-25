---
name: pepmlm-design
description: "Sequence-only peptide binder design using PepMLM (ESM-2 based). Generates linear peptide binders from target protein sequence alone — no 3D structure needed. Ideal for intrinsically disordered proteins and undruggable targets. Validated for targeted protein degradation (ubiquibodies). Use when user mentions PepMLM, sequence-only peptide design, peptide binder no structure, peptide degrader, ubiquibody, targeted degradation peptide, or structure-free peptide design."
---

# PepMLM — Sequence-Only Peptide Binder Design

> **Code recipes**: See [recipes.md](recipes.md) for Python templates.

Generates linear peptide binders from target protein sequence alone — no 3D structure required. Based on ESM-2-650M fine-tuned with span masking on protein-peptide pairs. Uniquely applicable to intrinsically disordered proteins and targets without stable structures. Validated for targeted protein degradation via ubiquibodies (uAbs) with ~40% experimental hit rate.

**When to use PepMLM vs alternatives:**
- **PepMLM** — no target structure available, disordered proteins, quick peptide generation from sequence
- **BindCraft/BoltzGen** — target structure available, higher-confidence designs
- **RFdiffusion** — cyclic peptides with backbone control (needs structure)

## Tool: PepMLM (Python/HuggingFace)

```bash
pip install transformers torch
```

```python
from transformers import AutoTokenizer, AutoModelForMaskedLM

tokenizer = AutoTokenizer.from_pretrained("TianlaiChen/PepMLM-650M")
model = AutoModelForMaskedLM.from_pretrained("TianlaiChen/PepMLM-650M")
```

### Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `peptide_length` | 15 | Length of generated peptide |
| `top_k` | 3 | Top-k sampling diversity (higher = more diverse) |
| `num_binders` | 4 | Number of peptides to generate |

### Output

DataFrame with columns: `Binder` (amino acid sequence), `Pseudo Perplexity` (lower = more confident).

## Completeness Checklist

- [ ] Target protein sequence provided
- [ ] Peptide length chosen (8-50 residues)
- [ ] Multiple peptides generated with top-k sampling
- [ ] Ranked by pseudo-perplexity
- [ ] Top candidates validated with AlphaFold-Multimer or Boltz-2
