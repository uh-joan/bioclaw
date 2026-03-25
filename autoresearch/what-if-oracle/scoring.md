# Scoring Checklist: what-if-oracle

Target: 0.9

## Criteria (per case)

### 1. Scenario Branch Quality (weight: 0.25)
Are the expected branches modeled (best/likely/worst/wildcard/contrarian)?
- >= 80% of expected branches present = 1.0
- 60-79% = 0.5
- < 60% = 0

### 2. Probability Coherence (weight: 0.20)
Do branch probabilities sum to ~100% and reflect reasonable estimates?
- Probabilities sum to 95-105% with reasonable assignments = 1.0
- Sum correct but assignments questionable = 0.5
- Probabilities don't sum or are obviously wrong = 0

### 3. Decision Confidence Score (weight: 0.20)
Is the Decision Confidence Score within expected range?
- Within range = 1.0
- Within 10 points = 0.5
- Outside by >10 = 0

### 4. Trigger Conditions and Hedges (weight: 0.20)
Are trigger conditions (when to pivot) and hedge strategies defined?
- Both triggers and hedges present = 1.0
- One of the two = 0.5
- Neither = 0

### 5. Report Completeness (weight: 0.15)
Are required_sections present?
- All present = 1.0
- Missing 1 = 0.5
- Missing 2+ = 0

## Override
If probabilities don't sum within 80-120% range, deduct 0.3 — basic quantitative coherence is mandatory.
If only 2 branches modeled (binary thinking), deduct 0.2 — the skill explicitly requires multi-branch analysis.
