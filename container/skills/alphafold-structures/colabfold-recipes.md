# ColabFold Fallback & Validation Recipes

Recipes for when a protein is not in the AlphaFold Database, or when you want to cross-validate an AlphaFold DB entry with a fresh ColabFold prediction.

> **Parent skill**: [SKILL.md](SKILL.md) — AlphaFold Database queries and structure analysis.
> **See also**: [colabfold-predict skill](../colabfold-predict/SKILL.md) — standalone ColabFold prediction skill with full CLI reference.

---

## Recipe 1: AlphaFold DB Miss → ColabFold Fallback

When a protein is not in the AlphaFold Database, predict its structure from sequence using ColabFold.

```bash
# Step 1: Confirm protein is NOT in AlphaFold DB
# (agent would have checked via mcp__alphafold__alphafold_data check_availability)

# Step 2: Get sequence from UniProt or user input
cat > missing_protein.fasta << 'FASTA'
>novel_protein_XYZ
MSEQUENCENOTINALPHAFOLDDB
FASTA

# Step 3: Predict with ColabFold (templates enabled to leverage PDB homologs)
colabfold_batch missing_protein.fasta fallback_pred/ \
  --num-models 5 \
  --num-recycle 10 \
  --templates

# Step 4: Analyze — same output format as AlphaFold DB (PDB with pLDDT in B-factor)
python3 << 'PYTHON'
import json, glob

scores_file = sorted(glob.glob("fallback_pred/*scores_rank_001*.json"))[0]
with open(scores_file) as f:
    scores = json.load(f)

plddt = scores["plddt"]
ptm = scores.get("ptm", 0)

print("ColabFold Fallback Prediction")
print("=" * 50)
print(f"Mean pLDDT: {sum(plddt)/len(plddt):.1f}")
print(f"pTM: {ptm:.3f}")
print(f"Residues: {len(plddt)}")
print()

# Confidence region analysis (same scale as AlphaFold DB)
very_high = sum(1 for p in plddt if p > 90)
confident = sum(1 for p in plddt if 70 <= p <= 90)
low = sum(1 for p in plddt if 50 <= p < 70)
very_low = sum(1 for p in plddt if p < 50)

print("Confidence Regions:")
print(f"  Very high (>90):  {very_high:>4} residues ({100*very_high/len(plddt):.0f}%)")
print(f"  Confident (70-90):{confident:>4} residues ({100*confident/len(plddt):.0f}%)")
print(f"  Low (50-70):      {low:>4} residues ({100*low/len(plddt):.0f}%)")
print(f"  Very low (<50):   {very_low:>4} residues ({100*very_low/len(plddt):.0f}%)")

# Identify disordered regions
print("\nDisordered regions (pLDDT < 50, 5+ consecutive residues):")
run_start = None
for i, p in enumerate(plddt):
    if p < 50 and run_start is None:
        run_start = i
    elif p >= 50 and run_start is not None:
        if i - run_start >= 5:
            print(f"  Residues {run_start+1}-{i}: {i-run_start} residues, "
                  f"mean pLDDT {sum(plddt[run_start:i])/(i-run_start):.1f}")
        run_start = None
if run_start and len(plddt) - run_start >= 5:
    print(f"  Residues {run_start+1}-{len(plddt)}: {len(plddt)-run_start} residues (C-terminal)")

print(f"\nPDB file: {sorted(glob.glob('fallback_pred/*rank_001*.pdb'))[0]}")
print("Note: pLDDT stored in B-factor column, same format as AlphaFold DB")
PYTHON
```

---

## Recipe 2: Cross-Validate AlphaFold DB Entry with ColabFold

Run a fresh ColabFold prediction and compare to the AlphaFold DB entry to assess reliability. Useful when the AlphaFold DB pLDDT is borderline or the protein has unusual features.

```bash
# Step 1: Download AlphaFold DB structure (agent does this via MCP tool)
# Assume AlphaFold DB PDB is saved as alphafold_db.pdb

# Step 2: Run ColabFold prediction on the same sequence
cat > same_sequence.fasta << 'FASTA'
>protein_to_validate
MSEQUENCEFROMALPHAFOLDDBTOREPREDICT
FASTA

colabfold_batch same_sequence.fasta repredict/ \
  --num-models 5 \
  --num-recycle 10

# Step 3: Compare predictions
python3 << 'PYTHON'
from Bio.PDB import PDBParser, Superimposer
import json, glob

parser = PDBParser(QUIET=True)

# Load AlphaFold DB structure (pLDDT in B-factor)
af_db = parser.get_structure("afdb", "alphafold_db.pdb")
af_db_cas = [a for a in af_db.get_atoms() if a.get_name() == "CA"]
af_db_plddt = [a.get_bfactor() for a in af_db_cas]

# Load ColabFold prediction
cf_pdb = sorted(glob.glob("repredict/*rank_001*.pdb"))[0]
cf = parser.get_structure("cf", cf_pdb)
cf_cas = [a for a in cf.get_atoms() if a.get_name() == "CA"]

cf_scores_file = sorted(glob.glob("repredict/*scores_rank_001*.json"))[0]
with open(cf_scores_file) as f:
    cf_scores = json.load(f)
cf_plddt = cf_scores["plddt"]

# Structural alignment
n = min(len(af_db_cas), len(cf_cas))
sup = Superimposer()
sup.set_atoms(af_db_cas[:n], cf_cas[:n])
sup.apply(cf.get_atoms())

print("AlphaFold DB vs ColabFold Cross-Validation")
print("=" * 60)
print(f"CA RMSD: {sup.rms:.2f} A over {n} residues")
print(f"AlphaFold DB  mean pLDDT: {sum(af_db_plddt)/len(af_db_plddt):.1f}")
print(f"ColabFold     mean pLDDT: {sum(cf_plddt)/len(cf_plddt):.1f}")
print()

if sup.rms < 1.0:
    print("CONCORDANT: Both methods agree — high confidence in structure")
elif sup.rms < 2.5:
    print("MINOR DIFFERENCES: Mostly agrees, check divergent regions below")
else:
    print("DIVERGENT: Significant disagreement — interpret with caution")

# Find regions where predictions disagree
print(f"\nRegions with pLDDT disagreement (|delta| > 15):")
m = min(len(af_db_plddt), len(cf_plddt))
disagreements = []
window = 5
for i in range(0, m - window):
    af_local = sum(af_db_plddt[i:i+window]) / window
    cf_local = sum(cf_plddt[i:i+window]) / window
    if abs(af_local - cf_local) > 15:
        disagreements.append((i+1, i+window, af_local, cf_local))

if disagreements:
    for start, end, af_p, cf_p in disagreements:
        better = "ColabFold" if cf_p > af_p else "AlphaFold DB"
        print(f"  Residues {start}-{end}: AFDB={af_p:.0f}, CF={cf_p:.0f} ({better} more confident)")
else:
    print("  None — pLDDT profiles are consistent")

# Consensus confidence (average of both methods)
print(f"\nConsensus regions (both methods pLDDT > 80):")
consensus_high = sum(1 for i in range(m) if af_db_plddt[i] > 80 and cf_plddt[i] > 80)
print(f"  {consensus_high}/{m} residues ({100*consensus_high/m:.0f}%) — high confidence in both")
PYTHON
```

---

## Recipe 3: Variant Structure vs AlphaFold DB Wildtype

Predict a mutant with ColabFold and compare to the AlphaFold DB wildtype structure to see what the mutation changed.

```bash
# Predict mutant
cat > mutant.fasta << 'FASTA'
>P53_R175H_mutant
MMUTANTSEQUENCEHERE
FASTA

colabfold_batch mutant.fasta mutant_pred/ --num-models 3 --num-recycle 10

# Compare to AlphaFold DB wildtype (downloaded via MCP tool as wildtype_afdb.pdb)
python3 << 'PYTHON'
from Bio.PDB import PDBParser, Superimposer
import json, glob

parser = PDBParser(QUIET=True)

# Wildtype from AlphaFold DB
wt = parser.get_structure("wt", "wildtype_afdb.pdb")
wt_cas = [a for a in wt.get_atoms() if a.get_name() == "CA"]
wt_plddt = [a.get_bfactor() for a in wt_cas]

# Mutant from ColabFold
mut_pdb = sorted(glob.glob("mutant_pred/*rank_001*.pdb"))[0]
mut = parser.get_structure("mut", mut_pdb)
mut_cas = [a for a in mut.get_atoms() if a.get_name() == "CA"]

mut_scores = sorted(glob.glob("mutant_pred/*scores_rank_001*.json"))[0]
with open(mut_scores) as f:
    scores = json.load(f)
mut_plddt = scores["plddt"]

# Align
n = min(len(wt_cas), len(mut_cas))
sup = Superimposer()
sup.set_atoms(wt_cas[:n], mut_cas[:n])
sup.apply(mut.get_atoms())

print("Variant vs AlphaFold DB Wildtype")
print("=" * 55)
print(f"Global CA RMSD: {sup.rms:.2f} A")
print(f"WT  mean pLDDT: {sum(wt_plddt)/len(wt_plddt):.1f} (AlphaFold DB)")
print(f"Mut mean pLDDT: {sum(mut_plddt)/len(mut_plddt):.1f} (ColabFold)")
print()

# Per-residue CA displacement after alignment
print("Local structural changes (CA displacement > 2 A):")
for i in range(n):
    disp = wt_cas[i] - mut_cas[i]
    if disp > 2.0:
        print(f"  Residue {i+1}: {disp:.2f} A displacement, "
              f"pLDDT WT={wt_plddt[i]:.0f} -> Mut={mut_plddt[i]:.0f}")

# pLDDT changes near mutation site
# (user should specify mutation_position)
mutation_position = 175  # example: R175H
radius = 10  # residues around mutation
start = max(0, mutation_position - radius - 1)
end = min(n, mutation_position + radius)

wt_local = wt_plddt[start:end]
mut_local = mut_plddt[start:end]
print(f"\nLocal pLDDT around mutation site (residues {start+1}-{end}):")
print(f"  WT:  {sum(wt_local)/len(wt_local):.1f}")
print(f"  Mut: {sum(mut_local)/len(mut_local):.1f}")
print(f"  Delta: {sum(mut_local)/len(mut_local) - sum(wt_local)/len(wt_local):+.1f}")
PYTHON
```
