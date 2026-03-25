# Protenix Antibody Engineering Recipes

Recipes for antibody-antigen complex prediction using Protenix with inference-time scaling. Ab-Ag complexes are among the hardest prediction targets — Protenix's scaling strategy gives the biggest accuracy gains here.

> **Parent skill**: [SKILL.md](SKILL.md) — full antibody engineering pipeline.
> **See also**: [protenix-predict skill](../protenix-predict/SKILL.md) — standalone Protenix with full CLI reference.

---

## Recipe 1: Ab-Ag Complex with Inference Scaling

Predict antibody-antigen complex with maximum sampling for best accuracy.

```bash
cat > ab_ag.json << 'JSON'
[{
  "sequences": [
    {"proteinChain": {"sequence": "VHSEQUENCE", "count": 1}},
    {"proteinChain": {"sequence": "VLSEQUENCE", "count": 1}},
    {"proteinChain": {"sequence": "ANTIGENSEQUENCE", "count": 1}}
  ],
  "name": "antibody_antigen"
}]
JSON

# Full preprocessing for best MSA
protenix prep -i ab_ag.json -o ab_ag_prep/

# 200 candidates (Ab-Ag benefits most from scaling)
protenix pred -i ab_ag.json -o ab_ag_results/ \
  -n protenix_base_default_v1.0.0 \
  -s "[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]" \
  -e 10 -c 10 --use_msa --use_template

python3 << 'PYTHON'
import json, glob

candidates = []
for f in sorted(glob.glob("ab_ag_results/*_summary.json")):
    data = json.load(open(f))
    candidates.append(data)

candidates.sort(key=lambda c: -c.get("ranking_score", 0))

print(f"Ab-Ag Complex: {len(candidates)} candidates generated")
print("=" * 50)
print(f"Top-1 ipTM: {candidates[0].get('iptm', 0):.3f}")
print(f"Top-5 avg ipTM: {sum(c.get('iptm',0) for c in candidates[:5])/5:.3f}")
print(f"Median ipTM: {candidates[len(candidates)//2].get('iptm',0):.3f}")
print(f"\nScaling benefit: top-1 is {candidates[0].get('iptm',0) - candidates[len(candidates)//2].get('iptm',0):+.3f} vs median")
PYTHON
```

---

## Recipe 2: Humanized Antibody Variants — Structural Comparison

Compare parental vs humanized antibody structures using Protenix for highest accuracy.

```bash
# Predict both variants
for variant in parental humanized_v1 humanized_v2; do
  protenix pred -i ${variant}.json -o ${variant}_results/ \
    -n protenix_base_default_v1.0.0 -s "[0,1,2]" -e 5
done

# Compare VH-VL interface preservation
python3 << 'PYTHON'
import json, glob

for variant in ["parental", "humanized_v1", "humanized_v2"]:
    summaries = sorted(glob.glob(f"{variant}_results/*_summary.json"))
    if summaries:
        data = json.load(open(summaries[0]))
        print(f"{variant}: pTM={data.get('ptm',0):.3f} ipTM={data.get('iptm',0):.3f}")
PYTHON
```

---

## Recipe 3: Quick Antibody Screen with Mini Model

Screen many antibody candidates quickly before full-accuracy prediction.

```bash
# Generate JSONs for each candidate
for i in $(seq 1 10); do
  cat > abs/candidate_${i}.json << JSON
[{"sequences": [
  {"proteinChain": {"sequence": "VH${i}SEQUENCE", "count": 1}},
  {"proteinChain": {"sequence": "VL${i}SEQUENCE", "count": 1}}
], "name": "candidate_${i}"}]
JSON
done

# Quick screen with mini model (no MSA, ESM embeddings)
for f in abs/*.json; do
  name=$(basename "$f" .json)
  protenix pred -i "$f" -o mini_ab/${name}/ \
    -n protenix_mini_esm_v1.0.0 -s "[0]" -e 1 -c 3 &
done
wait

# Rank candidates by Fv fold quality (pTM)
# Re-run top 3 with full model + scaling (Recipe 1)
```
