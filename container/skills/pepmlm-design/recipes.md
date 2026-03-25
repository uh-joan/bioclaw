# PepMLM Recipes

> Python templates for sequence-only peptide binder design.
> Parent skill: [SKILL.md](SKILL.md) — full PepMLM workflow.

---

## Recipe 1: Generate Peptide Binders

```python
from transformers import AutoTokenizer, AutoModelForMaskedLM
import torch

tokenizer = AutoTokenizer.from_pretrained("TianlaiChen/PepMLM-650M")
model = AutoModelForMaskedLM.from_pretrained("TianlaiChen/PepMLM-650M")

target_seq = "MTARGETPROTEINSEQUENCE"
peptide_length = 15
num_binders = 8
top_k = 3

# Append mask tokens
input_seq = target_seq + "<mask>" * peptide_length
inputs = tokenizer(input_seq, return_tensors="pt")

results = []
for _ in range(num_binders):
    with torch.no_grad():
        logits = model(**inputs).logits
    # Sample from top-k at peptide positions
    peptide_logits = logits[0, -peptide_length:]
    topk = torch.topk(peptide_logits, top_k, dim=-1)
    sampled_ids = topk.indices[torch.arange(peptide_length), torch.randint(0, top_k, (peptide_length,))]
    peptide = tokenizer.decode(sampled_ids).replace(" ", "")
    results.append(peptide)

for i, pep in enumerate(results):
    print(f"Binder {i+1}: {pep}")
```

---

## Recipe 2: Validate with ColabFold

```bash
# Write designed peptides as complexes for ColabFold-Multimer
python3 -c "
target = 'MTARGETSEQUENCE'
peptides = ['PEPTIDE1', 'PEPTIDE2', 'PEPTIDE3']
with open('pepmlm_validation.fasta', 'w') as f:
    for i, pep in enumerate(peptides):
        f.write(f'>pepmlm_{i}\n{target}:{pep}\n')
"

colabfold_batch pepmlm_validation.fasta validation/ \
  --model-type alphafold2_multimer_v3 --num-models 3 --num-recycle 10
```

---

## Recipe 3: Targeted Degradation (Ubiquibody Design)

```python
# Design peptide binder, then fuse to E3 ligase domain
target_seq = "MUNDRUGGABLETARGETSEQUENCE"
# Generate peptides (Recipe 1)
# Top peptide: DESIGNEDPEPTIDE

# Construct ubiquibody: E3 ligase domain + linker + peptide binder
e3_domain = "MCHIPDELTATPRSEQUENCE"
linker = "GGGGS" * 3
ubiquibody = e3_domain + linker + "DESIGNEDPEPTIDE"
print(f"Ubiquibody: {len(ubiquibody)} residues")
# Validate folding with ColabFold or Boltz-2
```
