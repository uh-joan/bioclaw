# Scoring Checklist: precision-medicine-stratifier

Target: 0.9

## Criteria (per case)

### 1. Risk Tier Accuracy (weight: 0.25)
Does the assigned tier (VERY HIGH / HIGH / INTERMEDIATE / LOW) match expected?
- Exact match = 1.0
- Adjacent tier = 0.5
- Off by 2+ tiers = 0

### 2. Component Score Accuracy (weight: 0.25)
Are the 4 component scores (Genetic Risk, Clinical Risk, Molecular Features, PGx Risk) within expected ranges?
- All 4 within range = 1.0
- 3 within range = 0.75
- 2 within range = 0.5
- 1 or 0 = 0

### 3. PGx Risk Detection (weight: 0.20)
For cases with pgx_critical=true, is the pharmacogenomic risk correctly identified and addressed?
- PGx risk identified with correct recommendation (e.g., dose reduction, drug switch, contraindication) = 1.0
- PGx risk mentioned but recommendation wrong/incomplete = 0.5
- PGx risk missed = 0
- N/A (no PGx risk in case) = 1.0

### 4. Treatment Recommendation Quality (weight: 0.20)
Do recommendations align with expected key_recommendations?
- >= 2 key recommendations matched = 1.0
- 1 matched = 0.5
- None matched = 0

### 5. Report Completeness (weight: 0.10)
Are all 9 phases documented in the report?
- All phases addressed = 1.0
- 7-8 phases = 0.5
- < 7 = 0

## Override
If a pgx_critical case (DPYD, HLA-B*57:01, CYP2D6 PM for tamoxifen) receives standard dosing recommendation without PGx adjustment, case score = 0. These are safety-critical errors.
