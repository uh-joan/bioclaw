# Scoring Checklist: clinical-decision-support

Target: 0.9

## Criteria (per case)

### 1. Drug Selection Accuracy (weight: 0.30)
Does the recommended drug match expected and align with current guidelines?
- Correct drug with guideline citation = 1.0
- Reasonable alternative with rationale = 0.5
- Contraindicated or inappropriate drug = 0

### 2. Interaction/Contraindication Detection (weight: 0.25)
Are clinically significant interactions and contraindications correctly identified?
- All expected interactions flagged = 1.0
- >= 50% flagged = 0.5
- Critical interaction missed = 0
- N/A (no interactions in case) = 1.0

### 3. Population-Specific Considerations (weight: 0.20)
Are patient-specific factors (age, race, renal function, comorbidities) correctly addressed?
- Correct adjustments for patient population = 1.0
- Partially addressed = 0.5
- Population factor ignored when clinically important = 0

### 4. Dose Accuracy (weight: 0.15)
For dosing cases, is the dose calculation correct?
- Correct dose with appropriate formulation = 1.0
- Dose in correct range but imprecise = 0.5
- Wrong dose = 0
- N/A = 1.0

### 5. Report Completeness (weight: 0.10)
Are required_sections present?
- All present = 1.0
- Missing 1 = 0.5
- Missing 2+ = 0

## Override
If pioglitazone is recommended for a patient with HF, case score = 0.
If ACE-I is recommended as monotherapy for a Black patient (population-specific guidance), deduct 0.3.
If a critical drug interaction in the polypharmacy case is missed (simvastatin + diltiazem), case score = 0.
