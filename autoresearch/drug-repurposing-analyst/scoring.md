# Scoring Checklist: drug-repurposing-analyst

Target: 0.9

## Criteria (per case)

### 1. Composite Score Accuracy (weight: 0.25)
Does the repurposing score (0-100) fall within expected range?
- Within range = 1.0
- Within 10 points of bounds = 0.5
- Outside by >10 = 0

### 2. Score Interpretation Match (weight: 0.20)
Does the interpretation (Strong/Promising/Moderate/Weak/Not viable) match expected?
- Exact match = 1.0
- Adjacent tier = 0.5
- Off by 2+ = 0

### 3. Strategy Execution (weight: 0.20)
Were the three strategies (target-based, disease-driven, compound-based) applied?
- All 3 strategies with results = 1.0
- 2 strategies = 0.5
- 1 or none = 0

### 4. Evidence Quality Assessment (weight: 0.20)
Does the report correctly distinguish evidence levels (in vitro vs observational vs prospective RCT)?
- Correct evidence hierarchy with appropriate caution = 1.0
- Evidence cited but not properly weighted = 0.5
- In vitro treated as equivalent to clinical = 0

### 5. Failure Recognition (weight: 0.15)
For failed repurposing cases (HCQ-COVID, ibuprofen-AD), does the report identify failure reasons?
- Failure correctly identified with mechanistic explanation = 1.0
- Failure noted but poorly explained = 0.5
- Failed case rated as Strong candidate = 0
- N/A (successful repurposing) = 1.0

## Override
If HCQ-COVID receives "Strong candidate" (80+), case score = 0. This is the most prominent failed repurposing in recent history.
If a validated/approved repurposing (thalidomide-myeloma, sildenafil-PAH) receives "Not viable," case score = 0.
