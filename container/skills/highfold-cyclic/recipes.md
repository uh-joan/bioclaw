# HighFold Recipes

> CLI commands for cyclic peptide structure prediction.
> Parent skill: [SKILL.md](SKILL.md) — full HighFold workflow.

---

## Recipe 1: Cyclic Peptide Monomer Prediction

```bash
cat > cyclic_mono.fasta << 'FASTA'
>cyclic_peptide
GCSFPDQWAPRGL:
FASTA

colabfold_batch --templates --amber --model-type alphafold2 cyclic_mono.fasta mono_results/
```

---

## Recipe 2: Cyclic Peptide-Protein Complex

```bash
cat > cyclic_complex.fasta << 'FASTA'
>cyclic_peptide_target
GCSFPDQWAPRGL::MTARGETPROTEINSEQUENCE
FASTA

colabfold_batch --templates --amber --model-type alphafold2 cyclic_complex.fasta complex_results/
```

---

## Recipe 3: Disulfide-Bridged Cyclic Peptide

```bash
# HighFold auto-enumerates Cys-Cys pairings and picks best
cat > disulfide_cyclic.fasta << 'FASTA'
>disulfide_cyclic
GCTKDCPRRFFCSC:
FASTA

colabfold_batch --templates --amber --model-type alphafold2 disulfide_cyclic.fasta disulfide_results/
```

---

## Recipe 4: Validate RFdiffusion Cyclic Peptide Designs

After designing cyclic peptides with RFdiffusion, predict their structure with HighFold.

```bash
# For each designed cyclic peptide sequence:
for seq in DESIGN1SEQ DESIGN2SEQ DESIGN3SEQ; do
  echo ">design\n${seq}:" > temp.fasta
  colabfold_batch --templates --amber --model-type alphafold2 temp.fasta highfold_val/
done
```
