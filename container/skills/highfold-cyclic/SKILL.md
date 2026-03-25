---
name: highfold-cyclic
description: "Cyclic peptide structure prediction using HighFold. Modified AlphaFold2 with cyclic position offset encoding for accurate prediction of head-to-tail cyclized peptides and disulfide-bridged cyclic peptides, both as monomers and in complex with protein targets. Use when user mentions HighFold, cyclic peptide structure, cyclic peptide prediction, macrocyclic structure, head-to-tail cyclization prediction, or disulfide cyclic peptide."
---

# HighFold — Cyclic Peptide Structure Prediction

> **Code recipes**: See [recipes.md](recipes.md) for CLI commands.

Modified AlphaFold2 with Cyclic Position Offset Encoding Matrix (CycPOEM) for accurate cyclic peptide structure prediction. Handles head-to-tail cyclization and disulfide bridge constraints. Predicts both monomer cyclic peptide structures and cyclic peptide-protein complexes.

**When to use HighFold vs alternatives:**
- **HighFold** — cyclic peptide structure prediction (monomers and complexes)
- **ColabFold** — linear proteins/peptides (not cyclic-aware)
- **Chai-1** — cyclic polymers supported but less specialized
- **RFdiffusion** — cyclic peptide *design* (not prediction)

## Tool: HighFold (ColabFold-based)

```bash
# Built on LocalColabFold
colabfold_batch --templates --amber --model-type alphafold2 input.fasta output/
```

### Input Format

FASTA with colon-separated chains. First chain = cyclic peptide (terminated with `:`):

```
>cyclic_peptide_complex
CYCLICPEPTIDESEQUENCE::TARGETPROTEINSEQUENCE
```

### Output

Standard AlphaFold outputs: PDB files with predicted structures, pLDDT, pTM scores.

## Completeness Checklist

- [ ] Cyclic peptide sequence prepared
- [ ] FASTA written with correct chain separator syntax
- [ ] HighFold prediction completed
- [ ] pLDDT and pTM assessed
- [ ] Structure inspected for correct cyclization geometry
