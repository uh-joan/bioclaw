# Scoring Checklist: clinical-trial-analyst

Target: 0.9

## Criteria (per case)

### 1. Endpoint Selection Appropriateness (weight: 0.25)
Is the recommended primary endpoint appropriate for the disease/regulatory context?
- Matches expected endpoint with justification = 1.0
- Acceptable alternative endpoint with justification = 0.75
- Correct endpoint but weak/missing justification = 0.5
- Inappropriate endpoint = 0

### 2. Statistical Design Validity (weight: 0.25)
Is the design methodologically sound?
- Correct design type (RCT/single-arm/NI/adaptive) + alpha control + power = 1.0
- Correct design but missing alpha spending or multiplicity = 0.5
- Wrong design type for the scenario = 0

### 3. Critical Issues Addressed (weight: 0.25)
Does the report address the must_address items from expected_details?
- All must_address items covered = 1.0
- >= 50% covered = 0.5
- < 50% covered = 0

### 4. Sample Size Reasonableness (weight: 0.10)
Is the proposed N within the expected range?
- Within expected range = 1.0
- Within 2x of range bounds = 0.5
- Outside 2x = 0

### 5. Report Completeness (weight: 0.15)
Are all required_sections present?
- All present = 1.0
- Missing 1 = 0.5
- Missing 2+ = 0

## Case Score
Weighted average of criteria 1-5.

## Round Score
Average of all case scores.

## Design Flaw Override
If the design has an uncontrolled type I error (e.g., no alpha spending with interim analyses, no multiplicity correction when required), deduct 0.3 from case score.
