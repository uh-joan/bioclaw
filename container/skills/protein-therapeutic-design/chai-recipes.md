# Chai-1 Protein Therapeutic Design Recipes

Recipes for glycoprotein design validation, restraint-guided complex prediction, and modified residue modeling using Chai-1. Chai-1's glycan support and restraint system complement the design pipeline for biologics that require glycosylation or have experimental constraint data.

> **Parent skill**: [SKILL.md](SKILL.md) — full protein therapeutic design pipeline.
> **See also**: [chai-predict skill](../chai-predict/SKILL.md) — standalone Chai-1 prediction with full CLI reference.

---

## Recipe 1: Glycoprotein Therapeutic Validation

Validate a designed glycoprotein therapeutic by predicting the protein + glycan structure together.

```bash
cat > glyco_therapeutic.fasta << 'FASTA'
>protein|name=designed-therapeutic
MDESIGNEDPROTEINSEQUENCEWITHGLYCOSITEASNXST
>glycan|name=n-linked
NAG(4-1 NAG(4-1 BMA(3-1 MAN(2-1 NAG(4-1 GAL(3-2 SIA))))(6-1 MAN(2-1 NAG(4-1 GAL(3-2 SIA))))))
FASTA

chai-lab fold --use-msa-server glyco_therapeutic.fasta glyco_validation/

python3 << 'PYTHON'
import numpy as np

scores = np.load("glyco_validation/scores.model_idx_0.npz", allow_pickle=True)
print("Glycoprotein Therapeutic Validation")
print("=" * 50)
print(f"Aggregate: {scores['aggregate_score'].item():.3f}")
print(f"pTM: {scores['ptm'].item():.3f}")

if "per_chain_ptm" in scores:
    chain_ptm = scores["per_chain_ptm"]
    print(f"Protein pTM: {chain_ptm[0]:.3f}")
    if len(chain_ptm) > 1:
        print(f"Glycan pTM: {chain_ptm[1]:.3f}")

if "per_chain_pair_iptm" in scores:
    pair = scores["per_chain_pair_iptm"]
    if pair.ndim == 2 and pair.shape[0] >= 2:
        print(f"Protein-glycan interface: {pair[0,1]:.3f}")
        if pair[0,1] > 0.4:
            print("Glycan interacts with protein surface — check for steric impact on binding site")
        else:
            print("Glycan is flexible/disordered — minimal impact on protein structure")
PYTHON
```

---

## Recipe 2: Restraint-Guided Binder Validation from Cryo-EM Data

Use low-resolution experimental data (cryo-EM density contacts) to guide designed binder complex prediction.

```bash
cat > binder_target.fasta << 'FASTA'
>protein|name=designed-binder
MDESIGNEDBINDERSEQUENCE
>protein|name=target
MTARGETPROTEINSEQUENCE
FASTA

# Restraints from cryo-EM or SAXS envelope data
cat > experimental_restraints.csv << 'CSV'
restraint_id,chainA,res_idxA,chainB,res_idxB,connection_type,confidence,min_distance,max_distance,comment
1,A,15,B,45,contact,0.9,0,12.0,cryo-EM density contact
2,A,22,B,78,contact,0.8,0,12.0,cryo-EM density contact
3,A,30,B,82,contact,0.9,0,12.0,cryo-EM density contact
4,A,35,B,90,contact,0.7,0,15.0,SAXS envelope
CSV

# With restraints
chai-lab fold --use-msa-server --constraint-path experimental_restraints.csv binder_target.fasta restrained/

# Without restraints (for comparison)
chai-lab fold --use-msa-server binder_target.fasta unrestrained/

python3 << 'PYTHON'
import numpy as np

r = np.load("restrained/scores.model_idx_0.npz", allow_pickle=True)
u = np.load("unrestrained/scores.model_idx_0.npz", allow_pickle=True)

print("Restraint Impact on Designed Binder Complex")
print("=" * 55)
print(f"{'Metric':<20} {'Restrained':>12} {'Free':>12}")
print("-" * 55)
print(f"{'ipTM':<20} {r['iptm'].item():>12.3f} {u['iptm'].item():>12.3f}")
print(f"{'pTM':<20} {r['ptm'].item():>12.3f} {u['ptm'].item():>12.3f}")
print(f"{'Score':<20} {r['aggregate_score'].item():>12.3f} {u['aggregate_score'].item():>12.3f}")
PYTHON
```

---

## Recipe 3: Modified Residue Therapeutic (PEGylation Site Assessment)

Predict structure with phosphorylated or chemically modified residues to assess impact on fold.

```bash
# Unmodified vs phosphorylated
cat > unmodified.fasta << 'FASTA'
>protein|name=therapeutic
MRKDESEESQATKELIRQFVGRTWCSYPGQITGSNMKSAT
FASTA

cat > phosphorylated.fasta << 'FASTA'
>protein|name=therapeutic-phospho
MRKDES(SEP)EESQAT(TPO)KELIRQFVGRTWCSYPGQITGS(SEP)NMKSAT
FASTA

chai-lab fold unmodified.fasta unmod_results/
chai-lab fold phosphorylated.fasta phospho_results/

python3 << 'PYTHON'
import numpy as np

u = np.load("unmod_results/scores.model_idx_0.npz", allow_pickle=True)
p = np.load("phospho_results/scores.model_idx_0.npz", allow_pickle=True)

print(f"Unmodified pTM:      {u['ptm'].item():.3f}")
print(f"Phosphorylated pTM:  {p['ptm'].item():.3f}")
delta = p['ptm'].item() - u['ptm'].item()
print(f"Delta: {delta:+.3f}")
if abs(delta) < 0.03:
    print("Phosphorylation does not significantly affect fold")
elif delta < -0.05:
    print("WARNING: Phosphorylation destabilizes — avoid these sites for PEGylation")
PYTHON
```

---

## Recipe 4: Quick Design Screening (Single-Sequence, No MSA)

Rapidly screen many designed protein variants without MSA generation overhead.

```bash
# Generate FASTAs for each design variant
for i in 1 2 3 4 5; do
cat > designs/design_v${i}.fasta << FASTA
>protein|name=design-v${i}
MDESIGNVARIANT${i}SEQUENCE
FASTA
done

# Run all in single-sequence mode (fastest)
for f in designs/*.fasta; do
  name=$(basename "$f" .fasta)
  chai-lab fold "$f" "screen_results/${name}/" &
done
wait

python3 << 'PYTHON'
import numpy as np, glob

print(f"{'Design':<20} {'Score':>7} {'pTM':>6}")
print("-" * 35)
for f in sorted(glob.glob("screen_results/*/scores.model_idx_0.npz")):
    name = f.split("/")[-2]
    s = np.load(f, allow_pickle=True)
    print(f"{name:<20} {s['aggregate_score'].item():>7.3f} {s['ptm'].item():>6.3f}")
PYTHON
```
