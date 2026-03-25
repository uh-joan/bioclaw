# Scoring Checklist: pharmacovigilance-specialist

Target: 0.9

## Criteria (per case)

### 1. Safety Signal Accuracy (weight: 0.25)
Are the key safety signals/AEs correctly identified with appropriate incidence data?
- Key AEs from expected list identified with incidence ranges = 1.0
- AEs identified but incidence missing/wrong = 0.5
- Major safety signal missed = 0

### 2. Mechanism/Causality Assessment (weight: 0.20)
Is the mechanism of the AE correctly explained and causality appropriately assessed?
- Correct mechanism + appropriate causality assessment = 1.0
- Partially correct = 0.5
- Wrong mechanism or no causality assessment = 0

### 3. Regulatory Context (weight: 0.20)
Are boxed warnings, FDA communications, and regulatory history correct?
- Key regulatory facts from expected_details = 1.0
- Partial regulatory coverage = 0.5
- Missing or wrong regulatory information = 0

### 4. Clinical Recommendations (weight: 0.20)
Are monitoring recommendations and management strategies appropriate?
- Matches expected monitoring/management = 1.0
- Partially aligned = 0.5
- Missing or dangerous recommendations = 0

### 5. Report Completeness (weight: 0.15)
Are required_sections present?
- All present = 1.0
- Missing 1 = 0.5
- Missing 2+ = 0

## Override
If valproic acid pregnancy risk is rated as safe/low-risk, case score = 0.
If a class-wide safety signal (NSAID CV risk) is dismissed as single-drug issue, deduct 0.3.
