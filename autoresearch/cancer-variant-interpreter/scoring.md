# Scoring Checklist: cancer-variant-interpreter

Target: 0.9 (allow 1 partial miss in 10 cases)

## Criteria (per case)

### 1. Tier Classification Accuracy (weight: 0.30)
Does the AMP/ASCO/CAP tier match expected?
- Exact match = 1.0
- Off by one tier (e.g., Tier I vs Tier II) = 0.5
- Off by two+ tiers = 0

### 2. Therapeutic Associations (weight: 0.25)
Are the key FDA-approved therapies identified?
- Recall = (identified therapies in expected list) / (total expected therapies)
- Must include companion diagnostic mention if applicable

### 3. Resistance Mechanisms (weight: 0.15)
Are known resistance mutations documented?
- >= 2 resistance mechanisms identified from expected list = 1.0
- 1 mechanism = 0.5
- None = 0
- N/A for Tier III/IV cases = 1.0 (skip)

### 4. Report Completeness (weight: 0.15)
Are all required_sections present and populated (no [Analyzing...] placeholders)?
- All present = 1.0
- Missing 1 = 0.5
- Missing 2+ = 0

### 5. Actionability Rating (weight: 0.15)
Does the HIGH/MODERATE/LOW/UNKNOWN rating match expected?
- Exact match = 1.0
- Off by one level = 0.5
- Off by two+ = 0

## Case Score
Weighted average of criteria 1-5.

## Round Score
Average of all case scores.

## Over-classification Guard
If a VUS/Tier III case is classified as Tier I or II, case score = 0 regardless of other criteria. This is the most dangerous failure mode.
