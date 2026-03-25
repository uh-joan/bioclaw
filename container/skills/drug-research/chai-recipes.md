# Chai-1 Drug Research Recipes

Recipes for glycoprotein drug structural context and restraint-guided drug-target complex prediction using Chai-1. Use when the drug target is a glycoprotein or when experimental structural data (crosslinks, known contacts) is available to guide prediction.

> **Parent skill**: [SKILL.md](SKILL.md) — full drug research report pipeline.
> **See also**: [chai-predict skill](../chai-predict/SKILL.md) — standalone Chai-1 prediction with full CLI reference.

---

## Recipe 1: Glycoprotein Drug Target Structure

Many drug targets are glycoproteins (receptors, enzymes). Predict the target structure including glycosylation to assess how glycans affect drug binding accessibility.

```bash
cat > glyco_target.fasta << 'FASTA'
>protein|name=glycoprotein-target
MTARGETPROTEINSEQUENCEWITHGLYCOSYLATIONSITES
>ligand|name=drug
DRUG_SMILES_HERE
>glycan|name=n-glycan-site1
NAG(4-1 NAG(4-1 BMA(3-1 MAN)(6-1 MAN)))
FASTA

chai-lab fold --use-msa-server glyco_target.fasta target_glyco_results/

python3 << 'PYTHON'
import numpy as np

scores = np.load("target_glyco_results/scores.model_idx_0.npz", allow_pickle=True)
print("Glycoprotein Target + Drug Complex")
print("=" * 50)
print(f"Aggregate: {scores['aggregate_score'].item():.3f}")
print(f"ipTM: {scores['iptm'].item():.3f}")

if "per_chain_pair_iptm" in scores:
    pair = scores["per_chain_pair_iptm"]
    if pair.ndim == 2 and pair.shape[0] >= 3:
        print(f"\nProtein-drug interface: {pair[0,1]:.3f}")
        print(f"Protein-glycan interface: {pair[0,2]:.3f}")
        print(f"Drug-glycan proximity: {pair[1,2]:.3f}")
        if pair[1,2] > 0.2:
            print("\nWARNING: Glycan may shield drug binding site — consider glycan-free target regions")
        else:
            print("\nGlycan does not interfere with drug binding site")
PYTHON
```

---

## Recipe 2: Biologic Drug with Glycosylation Profile

For antibody or protein drugs, model the drug itself with its glycosylation to assess manufacturing-relevant glycoform impact.

```bash
cat > biologic_drug.fasta << 'FASTA'
>protein|name=therapeutic-antibody-fc
FCDOMAINSEQUENCE
>glycan|name=g0f
NAG(4-1 NAG(4-1 BMA(3-1 MAN)(6-1 MAN)))(6-1 FUC)
FASTA

chai-lab fold --use-msa-server biologic_drug.fasta biologic_results/

# Compare different glycoforms (G0F vs G1F vs G2F)
# G1F has one galactose, G2F has two — affects CDC activity
```

---

## Recipe 3: Drug-Target with Known Binding Site from Literature

Use literature-derived binding contacts as restraints to guide drug-target complex prediction (when no crystal structure exists).

```bash
cat > drug_target.fasta << 'FASTA'
>protein|name=target
MTARGETSEQUENCE
>ligand|name=drug
DRUG_SMILES
FASTA

# Known binding residues from mutagenesis studies in literature
cat > literature_restraints.csv << 'CSV'
restraint_id,chainA,res_idxA,chainB,res_idxB,connection_type,confidence,min_distance,max_distance,comment
1,B,,A,120,pocket,0.9,0,6.0,mutagenesis abolishes binding
2,B,,A,145,pocket,0.8,0,6.0,key H-bond from SAR
3,B,,A,200,pocket,0.9,0,6.0,mutagenesis reduces potency 100x
4,B,,A,267,pocket,0.7,0,8.0,photoaffinity labeling hit
CSV

chai-lab fold --use-msa-server --constraint-path literature_restraints.csv drug_target.fasta restrained_dock/
```
