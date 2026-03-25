# Scoring Checklist: rare-disease-diagnosis

Target: 0.9

## Criteria (per case)

### 1. Primary Diagnosis Accuracy (weight: 0.30)
Does the top-ranked differential match the expected diagnosis?
- Exact match at rank 1 = 1.0
- Correct diagnosis at rank 2-3 = 0.5
- Not in top 3 = 0

### 2. Gene Identification (weight: 0.20)
Is the correct causative gene identified and prioritized?
- Correct primary gene in top panel = 1.0
- Correct gene mentioned but not prioritized = 0.5
- Gene missed = 0
- For multi-gene conditions (e.g., Noonan): primary gene identified = 1.0, any valid gene = 0.75

### 3. HPO Phenotype Standardization (weight: 0.15)
Are clinical features correctly mapped to HPO terms with IDs?
- >= 3 key HPO terms from expected list present with HP: IDs = 1.0
- 1-2 key terms present = 0.5
- No HPO standardization = 0

### 4. Differential Diagnosis Quality (weight: 0.15)
Does the differential include the expected alternative diagnoses?
- >= 2 expected differentials listed = 1.0
- 1 expected differential = 0.5
- None = 0

### 5. Report Completeness (weight: 0.20)
Are all required_sections present and populated?
- All present = 1.0
- Missing 1 = 0.5
- Missing 2+ = 0

## Case Score
Weighted average of criteria 1-5.

## Round Score
Average of all case scores.

## Nuance Guard
For ambiguous cases (huntington-reduced-penetrance, cftr-atypical): if the report fails to note diagnostic uncertainty or nuance specified in expected_details, deduct 0.2 from case score.
