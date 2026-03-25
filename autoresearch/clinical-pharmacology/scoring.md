# Scoring Checklist: clinical-pharmacology

Target: 0.9

## Criteria (per case)

### 1. Quantitative Accuracy (weight: 0.30)
Are the PK parameters, doses, or calculations correct?
- Key numeric values match expected (within reasonable range) = 1.0
- Directionally correct but imprecise = 0.5
- Wrong values or calculations = 0

### 2. Mechanistic Explanation (weight: 0.20)
Is the PK/PD rationale correct (CYP enzymes, clearance pathways, absorption mechanisms)?
- Correct mechanism with specific enzyme/pathway = 1.0
- Partially correct = 0.5
- Wrong mechanism = 0

### 3. Clinical Recommendation Quality (weight: 0.25)
Are the dosing recommendations, TDM strategies, or management plans clinically sound?
- Matches expected recommendations = 1.0
- Reasonable but incomplete = 0.5
- Dangerous or wrong recommendation = 0

### 4. Special Population Awareness (weight: 0.15)
For dose adjustment cases, are population-specific factors correctly addressed?
- Correct identification of impacted population + appropriate adjustment = 1.0
- Population identified but adjustment wrong = 0.5
- Population factor missed = 0
- N/A = 1.0

### 5. Report Completeness (weight: 0.10)
Are all required_sections present?
- All present = 1.0
- Missing 1 = 0.5
- Missing 2+ = 0

## Override
If a NTI drug (warfarin, lithium, vancomycin) dose recommendation omits TDM requirement, deduct 0.3 from case score. Monitoring is non-negotiable for NTI drugs.
