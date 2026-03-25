# Scoring Checklist: drug-target-validator

Target: 0.9

## Criteria (per case)

### 1. GO/NO-GO Tier Accuracy (weight: 0.30)
Does the tier (GO / CONDITIONAL GO / CAUTION / NO-GO) match expected?
- Exact match = 1.0
- Adjacent tier = 0.5
- Off by 2+ = 0

### 2. Validation Score Range (weight: 0.25)
Is the 0-100 score within the expected range?
- Within range = 1.0
- Within 10 points of bounds = 0.5
- Outside by >10 = 0

### 3. Dimension Score Accuracy (weight: 0.25)
Are the 6 dimension scores (disease association, druggability, safety, clinical precedent, validation evidence, DepMap) reasonable?
- >= 4 dimensions within expected ranges = 1.0
- 2-3 within range = 0.5
- < 2 = 0

### 4. Report Completeness (weight: 0.20)
Are all 10 phases documented?
- All 10 phases + GO/NO-GO report template = 1.0
- 8-9 phases = 0.5
- < 8 = 0

## Override
If a clinically validated target (EGFR, PD-1, HER2, PCSK9) with approved drugs receives NO-GO, case score = 0.
If a preclinical target (GRK2, GPBAR1) with no clinical candidates receives GO, case score = 0.
