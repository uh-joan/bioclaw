# Scoring Checklist: drug-target-analyst

Target: 0.9

## Criteria (per case)

### 1. Target Identification Accuracy (weight: 0.20)
Is the target correctly identified with protein class, gene name, and biological function?
- Correct class + gene + function = 1.0
- 2 of 3 correct = 0.5
- Fundamentally wrong = 0

### 2. Disease Association Strength (weight: 0.20)
Does the assessment match expected association strength (strong/moderate/limited)?
- Correct strength with supporting evidence types (genetic, clinical, preclinical) = 1.0
- Correct strength without evidence breakdown = 0.5
- Wrong assessment = 0

### 3. Druggability Assessment (weight: 0.20)
Does the report correctly characterize druggability and existing compounds?
- Correct druggability level + existing drugs listed + modalities identified = 1.0
- Partially correct (right level but incomplete drug list) = 0.5
- Wrong druggability assessment = 0

### 4. Safety and Challenge Characterization (weight: 0.20)
Are known safety concerns and target-specific challenges documented?
- Key safety concerns from expected list + challenges noted = 1.0
- Partial safety coverage = 0.5
- Missing safety assessment = 0

### 5. Report Completeness (weight: 0.20)
Are all required_sections present?
- All present = 1.0
- Missing 1 = 0.5
- Missing 2+ = 0

## Override
If a fully validated target (EGFR, PD-1, BCL-2) with approved drugs is called "undruggable" or "no existing compounds," case score = 0.
If a preclinical target (GRK2, GPBAR1) is called "fully validated" with approved drugs, case score = 0.
