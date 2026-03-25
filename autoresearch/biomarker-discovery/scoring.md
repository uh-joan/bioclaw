# Scoring Checklist: biomarker-discovery

Target: 0.9

## Criteria (per case)

### 1. BEST Category Accuracy (weight: 0.25)
Is the FDA BEST biomarker category (diagnostic/prognostic/predictive/monitoring/susceptibility) correctly assigned?
- Exact match = 1.0
- Related category (e.g., predictive vs pharmacodynamic) = 0.5
- Wrong category = 0

### 2. Validation Stage Assessment (weight: 0.25)
Is the biomarker correctly placed on the validation ladder (discovery/analytical/clinical/regulatory)?
- Correct stage with supporting evidence = 1.0
- Correct stage without evidence = 0.5
- Wrong stage (e.g., calling exploratory "clinically validated") = 0

### 3. Performance Metrics (weight: 0.20)
When applicable, are AUC/sensitivity/specificity values reasonable and correctly contextualized?
- Metrics present and within expected range = 1.0
- Metrics present but imprecise = 0.5
- Missing or fabricated = 0
- N/A (no quantitative data available) = assess based on correct acknowledgment of data gap

### 4. Limitations and Nuance (weight: 0.15)
Are expected limitations, controversies, or caveats documented?
- Key limitations from expected list captured = 1.0
- Partial coverage = 0.5
- Missing or glossed over = 0

### 5. Report Completeness (weight: 0.15)
Are all required_sections present?
- All present = 1.0
- Missing 1 = 0.5
- Missing 2+ = 0

## Override
If an exploratory biomarker (readiness-scoring-exercise) is called "clinically validated" or "ready for clinical use," case score = 0. Overstating biomarker readiness is dangerous.
If a validated companion diagnostic (HER2, BRCA) is called "exploratory," case score = 0.
