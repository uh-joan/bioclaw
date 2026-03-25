# Protenix Protein Therapeutic Design Recipes

Recipes for highest-accuracy design validation using Protenix. Use when the design target is challenging (multi-domain, flexible) or when maximum prediction confidence is needed before experimental testing.

> **Parent skill**: [SKILL.md](SKILL.md) — full protein therapeutic design pipeline.
> **See also**: [protenix-predict skill](../protenix-predict/SKILL.md) — standalone Protenix with full CLI reference.

---

## Recipe 1: Design Validation with Inference Scaling

For critical designs (pre-synthesis candidates), validate with Protenix using inference-time scaling for maximum accuracy.

```bash
cat > design_validation.json << 'JSON'
[{
  "sequences": [
    {"proteinChain": {"sequence": "MDESIGNEDBINDERSEQUENCE", "count": 1}},
    {"proteinChain": {"sequence": "MTARGETSEQUENCE", "count": 1}}
  ],
  "name": "binder_target"
}]
JSON

# 50 candidates for high-confidence validation
protenix pred -i design_validation.json -o design_val/ \
  -n protenix_base_default_v1.0.0 \
  -s "[0,1,2,3,4]" -e 10 -c 10

python3 << 'PYTHON'
import json, glob

candidates = []
for f in sorted(glob.glob("design_val/*_summary.json")):
    data = json.load(open(f))
    candidates.append(data)

candidates.sort(key=lambda c: -c.get("ranking_score", 0))
best = candidates[0]

print("Design Validation (Protenix, 50 candidates)")
print("=" * 50)
print(f"Best ranking score: {best.get('ranking_score', 0):.3f}")
print(f"Best ipTM: {best.get('iptm', 0):.3f}")
print(f"Best pTM: {best.get('ptm', 0):.3f}")

if best.get("iptm", 0) > 0.7:
    print("\nHIGH CONFIDENCE: Design validated — proceed to synthesis")
elif best.get("iptm", 0) > 0.5:
    print("\nMODERATE: Design plausible — consider optimization")
else:
    print("\nLOW: Design may not form intended complex — redesign")
PYTHON
```

---

## Recipe 2: Rapid Design Screening with Mini Model

Screen many designs quickly with Protenix-Mini, then re-validate top candidates with full model.

```bash
# Screen 20 designs with mini model (ESM, no MSA)
for i in $(seq 1 20); do
  cat > designs/design_${i}.json << JSON
[{"sequences": [{"proteinChain": {"sequence": "MDESIGN${i}SEQUENCE", "count": 1}}], "name": "design_${i}"}]
JSON
  protenix pred -i designs/design_${i}.json -o mini_screen/design_${i}/ \
    -n protenix_mini_esm_v1.0.0 -s "[0]" -e 1 -c 3 &
done
wait

# Rank by pTM, re-run top 3 with full model
# (see Recipe 1 for full validation)
```

---

## Recipe 3: Multi-Tool Design Validation Cascade

The production pipeline: ProteinMPNN → ColabFold (fast screen) → Protenix (final validation).

```bash
# Step 1: Design with ProteinMPNN (see proteinmpnn-recipes.md)
# Step 2: Fast screen with ColabFold (see colabfold-recipes.md)
# Step 3: Final validation of ColabFold-passing designs with Protenix

# Only validate the designs that passed ColabFold self-consistency
cat > finalist.json << 'JSON'
[{"sequences": [{"proteinChain": {"sequence": "MFINALISTSEQUENCE", "count": 1}}], "name": "finalist"}]
JSON

protenix pred -i finalist.json -o final_val/ \
  -n protenix_base_default_v1.0.0 \
  -s "[0,1,2,3,4]" -e 10 -c 10

echo "Designs passing all three tools (ProteinMPNN score + ColabFold RMSD + Protenix ranking) are highest confidence"
```
