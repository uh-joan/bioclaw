# Chai-1 Recipes

> Copy-paste CLI commands and Python analysis templates for Chai-1 structure prediction.
> Parent skill: [SKILL.md](SKILL.md) — full prediction workflow and confidence interpretation.

---

## Recipe 1: Glycoprotein Structure Prediction

Predict a glycosylated protein with N-linked glycan at Asn297.

```bash
cat > glycoprotein.fasta << 'FASTA'
>protein|name=fc-domain
CPPCPAPELLGGPSVFLFPPKPKDTLMISRTPEVTCVVVDVSHEDPEVKFNWYVDGVEVHNAKTKPREEQYNSTYRVVSVLTVLHQDWLNGKEYKCKVSNKALPAPIEKTISKAKGQPREPQVYTLPPSRDELTKNQVSLTCLVKGFYPSDIAVEWESNGQPENNYKTTPPVLDSDGSFFLYSKLTVDKSRWQQGNVFSCSVMHEALHNHYTQKSLSLSPG
>glycan|name=n297-glycan
NAG(4-1 NAG(4-1 BMA(3-1 MAN)(6-1 MAN)))
FASTA

# Quick prediction (single-sequence, no MSA)
chai-lab fold glycoprotein.fasta glyco_results/

# Better: with MSA
chai-lab fold --use-msa-server glycoprotein.fasta glyco_results_msa/

# Analyze glycan orientation
python3 << 'PYTHON'
import numpy as np
import glob

scores_file = sorted(glob.glob("glyco_results/scores.model_idx_0.npz"))[0]
scores = np.load(scores_file, allow_pickle=True)

print("Glycoprotein Prediction")
print("=" * 45)
print(f"Aggregate score: {scores['aggregate_score'].item():.3f}")
print(f"pTM: {scores['ptm'].item():.3f}")
print(f"ipTM: {scores['iptm'].item():.3f}")

if "per_chain_ptm" in scores:
    chain_ptm = scores["per_chain_ptm"]
    print(f"\nPer-chain pTM:")
    for i, ptm in enumerate(chain_ptm):
        label = "protein" if i == 0 else "glycan"
        print(f"  Chain {i} ({label}): {ptm:.3f}")

if "per_chain_pair_iptm" in scores:
    print(f"\nProtein-glycan interface ipTM:")
    pair_iptm = scores["per_chain_pair_iptm"]
    if pair_iptm.ndim == 2:
        print(f"  {pair_iptm[0,1]:.3f}")
PYTHON
```

---

## Recipe 2: Restraint-Guided Complex from XL-MS Data

Use crosslinking mass spectrometry data to guide complex prediction.

```bash
# Protein complex FASTA
cat > complex.fasta << 'FASTA'
>protein|name=subunit-A
MFIRSTSUBUNITSEQUENCE
>protein|name=subunit-B
MSECONDSUBUNITSEQUENCE
FASTA

# Crosslink restraints from XL-MS experiment
cat > restraints.csv << 'CSV'
restraint_id,chainA,res_idxA,chainB,res_idxB,connection_type,confidence,min_distance,max_distance,comment
1,A,45,B,120,contact,0.9,0,30.0,DSS crosslink
2,A,78,B,95,contact,0.8,0,30.0,DSS crosslink
3,A,112,B,67,contact,0.7,0,30.0,DSS crosslink
4,A,23,A,89,contact,0.9,0,30.0,intra-chain crosslink
CSV

# Run with restraints
chai-lab fold --use-msa-server --constraint-path restraints.csv complex.fasta xl_results/

# Compare: run without restraints for reference
chai-lab fold --use-msa-server complex.fasta no_xl_results/

# Compare predictions
python3 << 'PYTHON'
import numpy as np

xl_scores = np.load("xl_results/scores.model_idx_0.npz", allow_pickle=True)
free_scores = np.load("no_xl_results/scores.model_idx_0.npz", allow_pickle=True)

print("Restraint-Guided vs Free Prediction")
print("=" * 50)
print(f"{'Metric':<20} {'With XL':>10} {'Without':>10}")
print("-" * 50)
print(f"{'Aggregate':<20} {xl_scores['aggregate_score'].item():>10.3f} {free_scores['aggregate_score'].item():>10.3f}")
print(f"{'pTM':<20} {xl_scores['ptm'].item():>10.3f} {free_scores['ptm'].item():>10.3f}")
print(f"{'ipTM':<20} {xl_scores['iptm'].item():>10.3f} {free_scores['iptm'].item():>10.3f}")

delta_iptm = xl_scores['iptm'].item() - free_scores['iptm'].item()
if delta_iptm > 0.05:
    print(f"\nRestraints IMPROVED interface prediction by {delta_iptm:.3f} ipTM")
elif delta_iptm < -0.05:
    print(f"\nWARNING: Restraints WORSENED prediction — check crosslink quality")
else:
    print(f"\nMinimal difference — restraints consistent with unguided prediction")
PYTHON
```

---

## Recipe 3: Antibody Fc with Core Fucosylated Biantennary Glycan

Model the impact of Fc glycosylation on structure (relevant to ADCC/effector function).

```bash
cat > fc_glycosylated.fasta << 'FASTA'
>protein|name=fc-chain1
CPPCPAPELLGGPSVFLFPPKPKDTLMISRTPEVTCVVVDVSHEDPEVKFNWYVDGVEVHNAKTKPREEQYNSTYRVVSVLTVLHQDWLNGKEYKCKVSNKALPAPIEKTISKAKGQPREPQVYTLPPSRDELTKNQVSLTCLVKGFYPSDIAVEWESNGQPENNYKTTPPVLDSDGSFFLYSKLTVDKSRWQQGNVFSCSVMHEALHNHYTQKSLSLSPG
>protein|name=fc-chain2
CPPCPAPELLGGPSVFLFPPKPKDTLMISRTPEVTCVVVDVSHEDPEVKFNWYVDGVEVHNAKTKPREEQYNSTYRVVSVLTVLHQDWLNGKEYKCKVSNKALPAPIEKTISKAKGQPREPQVYTLPPSRDELTKNQVSLTCLVKGFYPSDIAVEWESNGQPENNYKTTPPVLDSDGSFFLYSKLTVDKSRWQQGNVFSCSVMHEALHNHYTQKSLSLSPG
>glycan|name=glycan-chain1
NAG(4-1 NAG(4-1 BMA(3-1 MAN(2-1 NAG(4-1 GAL)))(6-1 MAN(2-1 NAG(4-1 GAL)))))
>glycan|name=glycan-chain2
NAG(4-1 NAG(4-1 BMA(3-1 MAN(2-1 NAG(4-1 GAL)))(6-1 MAN(2-1 NAG(4-1 GAL)))))
FASTA

chai-lab fold --use-msa-server fc_glycosylated.fasta fc_glycan_results/

python3 << 'PYTHON'
import numpy as np

scores = np.load("fc_glycan_results/scores.model_idx_0.npz", allow_pickle=True)

print("Fc Glycosylation Analysis")
print("=" * 50)
print(f"Aggregate: {scores['aggregate_score'].item():.3f}")
print(f"pTM: {scores['ptm'].item():.3f}")
print(f"ipTM: {scores['iptm'].item():.3f}")

if "per_chain_pair_iptm" in scores:
    pair = scores["per_chain_pair_iptm"]
    if pair.ndim == 2 and pair.shape[0] >= 4:
        print(f"\nFc dimer interface (chain1-chain2): {pair[0,1]:.3f}")
        print(f"Chain1-glycan1 interface: {pair[0,2]:.3f}")
        print(f"Chain2-glycan2 interface: {pair[1,3]:.3f}")
        print(f"\nGlycan impacts FcγR binding site: check glycan proximity to CH2 domain")
PYTHON
```

---

## Recipe 4: Protein-Ligand with Covalent Bond

Predict a covalent inhibitor bound to a reactive cysteine with explicit bond restraint.

```bash
cat > covalent.fasta << 'FASTA'
>protein|name=egfr
MEGFRKINASEDOMAINSEQUENCE
>ligand|name=osimertinib
COc1cc2ncnc(Nc3ccc(F)c(Cl)c3)c2cc1NC(=O)/C=C/CN(C)C
FASTA

# Covalent bond restraint: Cys797 SG to acrylamide carbon
cat > covalent_restraint.csv << 'CSV'
restraint_id,chainA,res_idxA,atomA,chainB,res_idxB,atomB,connection_type,confidence,min_distance,max_distance,comment
1,A,797,SG,B,1,C18,covalent,1.0,1.0,2.0,Cys797 covalent bond
CSV

chai-lab fold --use-msa-server --constraint-path covalent_restraint.csv covalent.fasta covalent_results/
```

---

## Recipe 5: Quick Single-Sequence Screening (No MSA)

Rapidly screen multiple protein structures without waiting for MSA generation.

```bash
# Multiple queries in separate files
mkdir -p quick_screen/

for name in protein1 protein2 protein3; do
cat > quick_screen/${name}.fasta << FASTA
>protein|name=${name}
MSEQUENCEHERE
>ligand|name=drug
c1ccc(NC(=O)c2ccccc2)cc1
FASTA
done

# Run all — single-sequence mode (no --use-msa-server), fastest possible
for f in quick_screen/*.fasta; do
  name=$(basename "$f" .fasta)
  chai-lab fold "$f" "quick_results/${name}/" &
done
wait

# Rank all predictions
python3 << 'PYTHON'
import numpy as np, glob, os

print("Quick Screen Results (single-sequence mode)")
print("=" * 55)
print(f"{'Name':<20} {'Score':>7} {'pTM':>6} {'ipTM':>6}")
print("-" * 55)

for scores_file in sorted(glob.glob("quick_results/*/scores.model_idx_0.npz")):
    name = scores_file.split("/")[-2]
    scores = np.load(scores_file, allow_pickle=True)
    print(f"{name:<20} {scores['aggregate_score'].item():>7.3f} "
          f"{scores['ptm'].item():>6.3f} {scores['iptm'].item():>6.3f}")
PYTHON
```

---

## Recipe 6: Modified Residues (Phosphorylation, Selenomethionine)

Predict structure with post-translational modifications.

```bash
cat > phospho_protein.fasta << 'FASTA'
>protein|name=phosphorylated-kinase
MRKDES(SEP)EESQAT(TPO)KELIRQFVGRTWCSYPGQITGS(SEP)NMKSAT
FASTA

# SEP = phosphoserine, TPO = phosphothreonine
chai-lab fold --use-msa-server phospho_protein.fasta phospho_results/
```

---

## Recipe 7: Protein-DNA Complex

Predict a transcription factor bound to its DNA recognition element.

```bash
cat > protein_dna.fasta << 'FASTA'
>protein|name=transcription-factor
MTFSEQUENCEHERE
>protein|name=dna-sense
ATCGAATTCGAT
>protein|name=dna-antisense
ATCGAATTCGAT
FASTA

chai-lab fold --use-msa-server protein_dna.fasta dna_results/
```

---

## Recipe 8: Confidence Analysis Script

Parse and compare Chai-1 outputs across predictions.

```python
import numpy as np
import glob
import os

def analyze_chai_results(results_dir):
    """Analyze all Chai-1 predictions in a results directory."""
    print(f"{'Sample':<12} {'Score':>7} {'pTM':>6} {'ipTM':>6} {'Clashes':>8}")
    print("-" * 45)

    for scores_file in sorted(glob.glob(f"{results_dir}/scores.model_idx_*.npz")):
        idx = scores_file.split("model_idx_")[1].split(".")[0]
        scores = np.load(scores_file, allow_pickle=True)

        clash = scores.get("has_inter_chain_clashes", np.array(False)).item()
        clash_str = "YES" if clash else "no"

        print(f"  model_{idx:<5} {scores['aggregate_score'].item():>7.3f} "
              f"{scores['ptm'].item():>6.3f} {scores['iptm'].item():>6.3f} "
              f"{clash_str:>8}")

    # Best model
    best_score = 0
    best_idx = 0
    for scores_file in sorted(glob.glob(f"{results_dir}/scores.model_idx_*.npz")):
        idx = int(scores_file.split("model_idx_")[1].split(".")[0])
        scores = np.load(scores_file, allow_pickle=True)
        s = scores["aggregate_score"].item()
        if s > best_score:
            best_score = s
            best_idx = idx

    print(f"\nBest: model_{best_idx} (score {best_score:.3f})")
    print(f"Structure: {results_dir}/pred.model_idx_{best_idx}.cif")

# Usage:
# analyze_chai_results("glyco_results/")
```

---

## Recipe 9: Cross-Validate Chai-1 vs Boltz-2 vs ColabFold

Run all three prediction tools on the same complex for consensus analysis.

```bash
# Same protein-ligand complex across all three tools

# Chai-1 (supports glycans + restraints)
cat > chai_input.fasta << 'FASTA'
>protein|name=target
MPROTEINSEQUENCE
>ligand|name=drug
c1ccc(NC(=O)c2ccccc2)cc1
FASTA
chai-lab fold --use-msa-server chai_input.fasta chai_out/

# Boltz-2 (has affinity prediction)
cat > boltz_input.yaml << 'YAML'
version: 1
sequences:
  - protein:
      id: A
      sequence: MPROTEINSEQUENCE
  - ligand:
      id: B
      smiles: 'c1ccc(NC(=O)c2ccccc2)cc1'
properties:
  - affinity:
      binder: B
YAML
boltz predict boltz_input.yaml --out_dir boltz_out/ --diffusion_samples 5 --use_msa_server

# ColabFold (protein-only, for backbone reference)
cat > cf_input.fasta << 'FASTA'
>target_protein
MPROTEINSEQUENCE
FASTA
colabfold_batch cf_input.fasta cf_out/ --num-models 5 --num-recycle 10

echo "All three predictions complete — compare structures and confidence"
```

---

## Recipe 10: Pocket Restraint for Guided Docking

Guide a ligand into a specific binding site using pocket restraints.

```bash
cat > pocket_input.fasta << 'FASTA'
>protein|name=kinase
MKINASESEQUENCE
>ligand|name=inhibitor
CC(=O)Oc1ccccc1C(=O)O
FASTA

# Pocket restraint: ligand (chain B) near specific protein residues
cat > pocket_restraint.csv << 'CSV'
restraint_id,chainA,res_idxA,chainB,res_idxB,connection_type,confidence,min_distance,max_distance,comment
1,B,,A,45,pocket,1.0,0,6.0,ATP site
2,B,,A,78,pocket,1.0,0,6.0,ATP site
3,B,,A,82,pocket,1.0,0,6.0,hinge region
4,B,,A,153,pocket,1.0,0,6.0,DFG motif
CSV

chai-lab fold --use-msa-server --constraint-path pocket_restraint.csv pocket_input.fasta pocket_results/
```
