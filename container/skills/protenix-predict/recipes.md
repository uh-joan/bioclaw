# Protenix Recipes

> Copy-paste CLI commands and Python analysis templates for Protenix biomolecular prediction.
> Parent skill: [SKILL.md](SKILL.md) — full prediction workflow and confidence interpretation.

---

## Recipe 1: Standard Protein-Ligand Prediction

```bash
cat > protein_ligand.json << 'JSON'
[{
  "sequences": [
    {"proteinChain": {"sequence": "MPROTEINSEQUENCE", "count": 1}},
    {"ligand": {"smiles": "CC(=O)Oc1ccccc1C(=O)O", "count": 1}}
  ],
  "name": "target_drug"
}]
JSON

protenix pred -i protein_ligand.json -o results/ -n protenix_base_default_v1.0.0 -s "[0]" -e 5

python3 << 'PYTHON'
import json, glob

for f in sorted(glob.glob("results/*_summary.json")):
    data = json.load(open(f))
    print(f"Ranking: {data.get('ranking_score', 'N/A')}")
    print(f"pTM: {data.get('ptm', 'N/A')}")
    print(f"ipTM: {data.get('iptm', 'N/A')}")
    print(f"pLDDT: {data.get('plddt', 'N/A')}")
PYTHON
```

---

## Recipe 2: Inference-Time Scaling for Hard Targets

Generate 100+ candidates for hard targets (Ab-Ag, multi-domain) — accuracy improves log-linearly with samples.

```bash
cat > hard_target.json << 'JSON'
[{
  "sequences": [
    {"proteinChain": {"sequence": "MVHSEQUENCE", "count": 1}},
    {"proteinChain": {"sequence": "MVLSEQUENCE", "count": 1}},
    {"proteinChain": {"sequence": "MANTIGENSEQUENCE", "count": 1}}
  ],
  "name": "ab_ag_complex"
}]
JSON

# 10 seeds × 10 samples = 100 candidates
protenix pred -i hard_target.json -o scaled_results/ \
  -n protenix_base_default_v1.0.0 \
  -s "[0,1,2,3,4,5,6,7,8,9]" -e 10 -c 10 -p 200

# Rank all 100 candidates
python3 << 'PYTHON'
import json, glob

candidates = []
for f in sorted(glob.glob("scaled_results/*_summary.json")):
    data = json.load(open(f))
    candidates.append({
        "file": f,
        "score": data.get("ranking_score", 0),
        "iptm": data.get("iptm", 0),
        "ptm": data.get("ptm", 0),
    })

candidates.sort(key=lambda c: -c["score"])

print(f"Inference Scaling: {len(candidates)} candidates")
print("=" * 55)
print(f"{'Rank':<5} {'Score':>7} {'ipTM':>6} {'pTM':>6}")
print("-" * 55)
for i, c in enumerate(candidates[:10], 1):
    print(f"{i:<5} {c['score']:>7.3f} {c['iptm']:>6.3f} {c['ptm']:>6.3f}")

print(f"\nBest: {candidates[0]['file']}")
print(f"Top-1 vs median improvement: {candidates[0]['score'] - candidates[len(candidates)//2]['score']:+.3f}")
PYTHON
```

---

## Recipe 3: Quick Screening with Mini Model

Use Protenix-Mini (ESM-based, no MSA needed) for rapid screening.

```bash
# Screen multiple targets quickly
for target in target1 target2 target3; do
  protenix pred -i ${target}.json -o mini_results/${target}/ \
    -n protenix_mini_esm_v1.0.0 \
    -s "[0]" -e 1 -c 3 &
done
wait

# Rank results
python3 << 'PYTHON'
import json, glob

print("Mini Model Quick Screen")
print("=" * 50)
for d in sorted(glob.glob("mini_results/*/)):
    name = d.rstrip("/").split("/")[-1]
    for f in glob.glob(f"{d}*_summary.json"):
        data = json.load(open(f))
        print(f"  {name}: score={data.get('ranking_score',0):.3f} "
              f"pTM={data.get('ptm',0):.3f} ipTM={data.get('iptm',0):.3f}")
PYTHON
```

---

## Recipe 4: PDB to JSON Conversion and Re-Prediction

Convert an existing PDB structure to Protenix JSON and predict from sequence alone for validation.

```bash
# Convert known structure to JSON (extracts sequences + entities)
protenix json -i known_structure.pdb -o reprediction_input.json

# Predict from sequence
protenix pred -i reprediction_input.json -o reprediction/ \
  -n protenix_base_default_v1.0.0 -s "[0]" -e 5

echo "Compare reprediction/*.cif to known_structure.pdb for accuracy assessment"
```

---

## Recipe 5: Protein-DNA Complex with RNA MSA

```bash
cat > protein_dna.json << 'JSON'
[{
  "sequences": [
    {"proteinChain": {"sequence": "MTFSEQUENCE", "count": 1}},
    {"dnaSequence": {"sequence": "ATCGAATTCGAT", "count": 1}},
    {"dnaSequence": {"sequence": "ATCGAATTCGAT", "count": 1}}
  ],
  "name": "tf_dna"
}]
JSON

protenix pred -i protein_dna.json -o dna_results/ -n protenix_base_default_v1.0.0 -s "[0]" -e 5
```

---

## Recipe 6: Covalent Ligand Prediction

```bash
cat > covalent.json << 'JSON'
[{
  "sequences": [
    {"proteinChain": {"sequence": "MPROTEINSEQUENCE", "count": 1}},
    {"ligand": {"smiles": "C=CC(=O)Nc1cccc(NC(=O)c2ccc(F)cc2)c1", "count": 1}}
  ],
  "covalent_bonds": [
    ["A", 797, "SG", "B", 1, "C3"]
  ],
  "name": "covalent_inhibitor"
}]
JSON

protenix pred -i covalent.json -o covalent_results/ -n protenix_base_default_v1.0.0 -s "[0]" -e 5
```

---

## Recipe 7: Constraint-Guided Pocket Docking

```bash
cat > pocket.json << 'JSON'
[{
  "sequences": [
    {"proteinChain": {"sequence": "MPROTEINSEQUENCE", "count": 1}},
    {"ligand": {"smiles": "c1ccccc1", "count": 1}}
  ],
  "constraint": {
    "pocket": [
      {"binder": "B", "contacts": [
        {"chain": "A", "res_idx": 45},
        {"chain": "A", "res_idx": 78},
        {"chain": "A", "res_idx": 82}
      ]}
    ]
  },
  "name": "pocket_dock"
}]
JSON

protenix pred -i pocket.json -o pocket_results/ -n protenix_base_default_v1.0.0 -s "[0]" -e 10
```

---

## Recipe 8: Antibody-Antigen with Maximum Sampling

Best practice for Ab-Ag complexes — inference scaling gives the biggest accuracy gains here.

```bash
cat > ab_ag.json << 'JSON'
[{
  "sequences": [
    {"proteinChain": {"sequence": "EVQLVESGGGLVQPGGSLRLSCAASGFNIKDTYIHWVRQAPGKGLEWVARIYPTNGYTRYADSVKGRFTISADTSKNTAYLQMNSLRAEDTAVYYCSRWGGDGFYAMDYWGQGTLVTVSS", "count": 1}},
    {"proteinChain": {"sequence": "DIQMTQSPSSLSASVGDRVTITCRASQDVNTAVAWYQQKPGKAPKLLIYSASFLYSGVPSRFSGSRSGTDFTLTISSLQPEDFATYYCQQHYTTPPTFGQGTKVEIK", "count": 1}},
    {"proteinChain": {"sequence": "MANTIGENSEQUENCE", "count": 1}}
  ],
  "name": "trastuzumab_her2"
}]
JSON

# Full preprocessing
protenix prep -i ab_ag.json -o ab_ag_prep/

# Maximum sampling: 200 candidates
protenix pred -i ab_ag.json -o ab_ag_results/ \
  -n protenix_base_default_v1.0.0 \
  -s "[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]" \
  -e 10 -c 10 --use_msa --use_template
```

---

## Recipe 9: Multi-Tool Consensus (Protenix + Boltz + ColabFold)

Run the same complex through multiple tools for maximum confidence.

```bash
# Protenix (highest accuracy)
protenix pred -i complex.json -o protenix_out/ -n protenix_base_default_v1.0.0 -s "[0,1,2]" -e 5

# Boltz-2 (has affinity)
boltz predict complex.yaml --out_dir boltz_out/ --diffusion_samples 5 --use_msa_server

# ColabFold (protein backbone reference)
colabfold_batch complex.fasta cf_out/ --num-models 5 --num-recycle 10

echo "Compare all three for consensus — agreement across tools = high confidence"
```

---

## Recipe 10: Modified Protein with Ions

```bash
cat > modified.json << 'JSON'
[{
  "sequences": [
    {
      "proteinChain": {
        "sequence": "MRKDESEESQATKELIRQFVG",
        "modifications": [
          {"ptmType": "CCD_SEP", "ptmPosition": 6},
          {"ptmType": "CCD_TPO", "ptmPosition": 12}
        ],
        "count": 1
      }
    },
    {"ion": {"CCD": "MG", "count": 2}},
    {"ion": {"CCD": "ZN", "count": 1}}
  ],
  "name": "metalloprotein"
}]
JSON

protenix pred -i modified.json -o modified_results/ -n protenix_base_default_v1.0.0 -s "[0]" -e 5
```
