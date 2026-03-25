# Scoring Checklist: reproducibility-audit

Target: 0.9

## Criteria (per case)

### 1. Overall Score Accuracy (weight: 0.25)
Does the reproducibility score (0-100) fall within the expected range?
- Within expected range = 1.0
- Within 10 points of range bounds = 0.5
- Outside by >10 points = 0

### 2. Rating Classification (weight: 0.15)
Does the rating match expected (Highly reproducible / Moderately / Questionable / Low / Not reproducible)?
- Exact match = 1.0
- Adjacent rating = 0.5
- Off by 2+ = 0

### 3. Dimension Score Accuracy (weight: 0.25)
Are the 8 dimension scores (each 0-10) within expected ranges?
- >= 6 dimensions within range = 1.0
- 4-5 dimensions within range = 0.5
- < 4 = 0

### 4. Red Flag Detection (weight: 0.20)
Are the expected red flags identified?
- >= 75% of expected red flags identified = 1.0
- 50-74% identified = 0.5
- < 50% = 0
- N/A (no red flags expected) = check that report confirms no red flags (1.0 if confirmed)

### 5. GRIM/SPRITE Tests (weight: 0.15)
When applicable, are consistency tests correctly applied?
- GRIM/SPRITE tests applied with correct pass/fail results = 1.0
- Tests applied but with calculation errors = 0.5
- Tests not applied when expected = 0
- N/A (no numerical data to test) = 1.0

## Override
If a retracted/fabricated case (retracted-paper-signals) receives "Highly reproducible" or "Moderately reproducible," case score = 0.
If a gold-standard case (well-designed-rct, open-science-exemplar) receives "Low" or "Not reproducible," case score = 0.
