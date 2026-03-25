# ColabFold Recipes

> Copy-paste CLI commands and Python analysis templates for ColabFold structure prediction.
> Parent skill: [SKILL.md](SKILL.md) — full prediction workflow and confidence interpretation.

---

## Recipe 1: Quick Monomer Prediction

Predict a single protein structure from sequence with minimal compute.

```bash
# Write sequence to FASTA
cat > query.fasta << 'FASTA'
>my_protein
MKFLVLLFNILCLFPVLAENQDKGMAHISMDQELRRFKDNREKTHFDYSIIFHQNVSSYK
FASTA

# Run quick prediction (1 model, 3 recycles)
colabfold_batch query.fasta results/ --num-models 1 --num-recycle 3

# Check results
ls results/*.pdb
cat results/*scores*.json | python3 -c "
import json, sys
scores = json.load(sys.stdin)
print(f'pLDDT: {sum(scores[\"plddt\"])/len(scores[\"plddt\"]):.1f}')
print(f'pTM: {scores.get(\"ptm\", \"N/A\")}')
"
```

---

## Recipe 2: High-Quality Prediction with Relaxation

Full 5-model ensemble with templates and AMBER relaxation for publication-grade structures.

```bash
cat > query.fasta << 'FASTA'
>my_protein
MSEQUENCEHERE
FASTA

colabfold_batch query.fasta results/ \
  --num-models 5 \
  --num-recycle 20 \
  --templates \
  --amber \
  --num-relax 1 \
  --rank ptm

# Best structure is results/*_relaxed_rank_001.pdb
```

---

## Recipe 3: Protein Complex (Multimer) Prediction

Predict the structure of a protein-protein complex.

```bash
# Chains separated by colon
cat > complex.fasta << 'FASTA'
>receptor_ligand_complex
RECEPTORSEQUENCE:LIGANDSEQUENCE
FASTA

colabfold_batch complex.fasta results/ \
  --model-type alphafold2_multimer_v3 \
  --num-recycle 10 \
  --num-models 5 \
  --rank multimer

# Check interface confidence
cat results/*scores*.json | python3 -c "
import json, sys
scores = json.load(sys.stdin)
print(f'ipTM: {scores.get(\"iptm\", \"N/A\")}')
print(f'pTM: {scores.get(\"ptm\", \"N/A\")}')
print(f'Mean pLDDT: {sum(scores[\"plddt\"])/len(scores[\"plddt\"]):.1f}')
"
```

---

## Recipe 4: Antibody-Antigen Complex

Predict antibody Fv bound to antigen (VH:VL:antigen format).

```bash
cat > ab_complex.fasta << 'FASTA'
>trastuzumab_her2
EVQLVESGGGLVQPGGSLRLSCAASGFNIKDTYIHWVRQAPGKGLEWVARIYPTNGYTRYADSVKGRFTISADTSKNTAYLQMNSLRAEDTAVYYCSRWGGDGFYAMDYWGQGTLVTVSS:DIQMTQSPSSLSASVGDRVTITCRASQDVNTAVAWYQQKPGKAPKLLIYSASFLYSGVPSRFSGSRSGTDFTLTISSLQPEDFATYYCQQHYTTPPTFGQGTKVEIK:ANTIGENSEQUENCE
FASTA

colabfold_batch ab_complex.fasta results/ \
  --model-type alphafold2_multimer_v3 \
  --num-recycle 10 \
  --num-models 5 \
  --rank multimer
```

---

## Recipe 5: Batch Mutant Screening

Predict structures for wildtype and multiple mutants, then compare.

```bash
# Create multi-query FASTA
cat > mutants.fasta << 'FASTA'
>wildtype
MORIGINALSEQUENCE
>L45A_mutant
MORIGINAASEQUENCE
>K78E_mutant
MORIGINALSEEUENCE
FASTA

# Quick screen (1 model each)
colabfold_batch mutants.fasta results/ --num-models 1 --num-recycle 3

# Compare pLDDT profiles
python3 << 'PYTHON'
import json, glob, os

results = {}
for f in sorted(glob.glob("results/*scores_rank_001*.json")):
    name = os.path.basename(f).split("_scores")[0]
    with open(f) as fh:
        scores = json.load(fh)
    plddt = scores["plddt"]
    results[name] = {
        "mean_plddt": sum(plddt) / len(plddt),
        "min_plddt": min(plddt),
        "ptm": scores.get("ptm", "N/A"),
    }

print(f"{'Name':<25} {'Mean pLDDT':>10} {'Min pLDDT':>10} {'pTM':>6}")
print("-" * 55)
for name, s in results.items():
    print(f"{name:<25} {s['mean_plddt']:>10.1f} {s['min_plddt']:>10.1f} {s['ptm']:>6}")
PYTHON
```

---

## Recipe 6: Conformational Sampling

Generate diverse conformations for flexible proteins using dropout and MSA subsampling.

```bash
cat > flexible.fasta << 'FASTA'
>flexible_protein
MSEQUENCEHERE
FASTA

colabfold_batch flexible.fasta conformations/ \
  --num-models 5 \
  --num-seeds 5 \
  --use-dropout \
  --max-msa "512:1024" \
  --num-recycle 3

# This produces 25 structures (5 models x 5 seeds)
# Cluster by RMSD to identify distinct conformational states
python3 << 'PYTHON'
import glob

pdbs = sorted(glob.glob("conformations/*.pdb"))
print(f"Generated {len(pdbs)} conformations:")
for p in pdbs:
    print(f"  {p}")
PYTHON
```

---

## Recipe 7: MSA-Only for Downstream Analysis

Generate MSAs without running structure prediction (useful for coevolution analysis).

```bash
cat > query.fasta << 'FASTA'
>target_protein
MSEQUENCEHERE
FASTA

# Generate MSA only
colabfold_batch query.fasta msa_output/ --msa-only

# MSA is saved as .a3m file
ls msa_output/*.a3m

# Count sequences in MSA (depth indicator)
grep -c "^>" msa_output/*.a3m
```

---

## Recipe 8: pLDDT and PAE Analysis Script

Parse ColabFold outputs for detailed confidence analysis.

```python
import json
import glob
import os

def analyze_prediction(results_dir, query_name):
    """Analyze ColabFold prediction results."""
    report = {"query": query_name, "models": []}

    for scores_file in sorted(glob.glob(f"{results_dir}/{query_name}*scores*.json")):
        with open(scores_file) as f:
            scores = json.load(f)

        plddt = scores["plddt"]
        model_info = {
            "file": os.path.basename(scores_file),
            "mean_plddt": sum(plddt) / len(plddt),
            "median_plddt": sorted(plddt)[len(plddt) // 2],
            "min_plddt": min(plddt),
            "max_plddt": max(plddt),
            "ptm": scores.get("ptm"),
            "iptm": scores.get("iptm"),
            "residues_above_90": sum(1 for p in plddt if p > 90),
            "residues_below_50": sum(1 for p in plddt if p < 50),
            "total_residues": len(plddt),
        }

        # Identify low-confidence regions (runs of pLDDT < 70)
        low_regions = []
        in_low = False
        start = 0
        for i, p in enumerate(plddt):
            if p < 70 and not in_low:
                in_low = True
                start = i + 1  # 1-indexed
            elif p >= 70 and in_low:
                in_low = False
                low_regions.append((start, i))
        if in_low:
            low_regions.append((start, len(plddt)))
        model_info["low_confidence_regions"] = low_regions

        # PAE analysis (if present)
        if "pae" in scores:
            pae = scores["pae"]
            flat_pae = [v for row in pae for v in row]
            model_info["mean_pae"] = sum(flat_pae) / len(flat_pae)
            model_info["max_pae"] = max(flat_pae)

        report["models"].append(model_info)

    return report


def print_report(report):
    """Print formatted prediction analysis."""
    print(f"\n{'='*60}")
    print(f"ColabFold Analysis: {report['query']}")
    print(f"{'='*60}")

    for i, m in enumerate(report["models"]):
        print(f"\nModel {i+1}: {m['file']}")
        print(f"  Mean pLDDT: {m['mean_plddt']:.1f}  |  pTM: {m['ptm'] or 'N/A'}")
        if m.get("iptm"):
            print(f"  ipTM: {m['iptm']:.3f}")
        print(f"  Residues >90 pLDDT: {m['residues_above_90']}/{m['total_residues']}"
              f" ({100*m['residues_above_90']/m['total_residues']:.0f}%)")
        print(f"  Residues <50 pLDDT: {m['residues_below_50']}/{m['total_residues']}"
              f" ({100*m['residues_below_50']/m['total_residues']:.0f}%)")
        if m["low_confidence_regions"]:
            regions = ", ".join(f"{s}-{e}" for s, e in m["low_confidence_regions"])
            print(f"  Low-confidence regions: {regions}")
        if m.get("mean_pae"):
            print(f"  Mean PAE: {m['mean_pae']:.1f} A")

    # Overall assessment
    best = max(report["models"], key=lambda m: m["mean_plddt"])
    print(f"\nBest model: {best['file']} (pLDDT {best['mean_plddt']:.1f})")
    if best["mean_plddt"] > 85:
        print("Assessment: HIGH CONFIDENCE — structure suitable for detailed analysis")
    elif best["mean_plddt"] > 70:
        print("Assessment: MODERATE CONFIDENCE — backbone reliable, sidechain caution")
    elif best["mean_plddt"] > 50:
        print("Assessment: LOW CONFIDENCE — fold topology may be correct, details uncertain")
    else:
        print("Assessment: VERY LOW CONFIDENCE — likely disordered or incorrect prediction")


# Usage:
# report = analyze_prediction("results/", "my_protein")
# print_report(report)
```

---

## Recipe 9: Design Self-Consistency Check

Validate a designed protein by predicting its structure and comparing to the design target.

```bash
# Step 1: Predict the designed sequence
cat > designed.fasta << 'FASTA'
>designed_binder
MDESIGNEDSEQUENCEHERE
FASTA

colabfold_batch designed.fasta prediction/ --num-models 5 --num-recycle 10

# Step 2: Compare predicted vs target structure
python3 << 'PYTHON'
"""
Compare predicted structure to design target using CA RMSD.
Requires: pip install biopython
"""
from Bio.PDB import PDBParser, Superimposer
import glob

parser = PDBParser(QUIET=True)

# Load design target
target = parser.get_structure("target", "target_scaffold.pdb")
target_cas = [a for a in target.get_atoms() if a.get_name() == "CA"]

# Load best ColabFold prediction
pred_pdb = sorted(glob.glob("prediction/*rank_001*.pdb"))[0]
pred = parser.get_structure("pred", pred_pdb)
pred_cas = [a for a in pred.get_atoms() if a.get_name() == "CA"]

# Align and compute RMSD
n = min(len(target_cas), len(pred_cas))
sup = Superimposer()
sup.set_atoms(target_cas[:n], pred_cas[:n])
sup.apply(pred.get_atoms())

print(f"CA RMSD: {sup.rms:.2f} A over {n} residues")
if sup.rms < 1.5:
    print("PASS: Predicted structure matches design target — high self-consistency")
elif sup.rms < 3.0:
    print("MARGINAL: Moderate deviation — review binding interface regions")
else:
    print("FAIL: Large deviation — design may not fold as intended")
PYTHON
```

---

## Recipe 10: Export AlphaFold3-Compatible JSON

Generate AF3-compatible input for advanced features (ligands, nucleic acids).

```bash
cat > af3_input.fasta << 'FASTA'
>protein_dna_complex
MPROTEINSEQUENCE:dna|ATCGATCGATCG
FASTA

# Generate AF3 JSON (for submission to AF3 server)
colabfold_batch af3_input.fasta output/ --af3-json

# The JSON file can be submitted to AlphaFold3 for prediction
# with non-protein molecules (DNA, RNA, ligands)
cat output/*.json
```
