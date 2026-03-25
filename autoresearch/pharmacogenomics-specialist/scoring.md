# Scoring Checklist: pharmacogenomics-specialist

Target: 1.0 (safety-critical — dosing errors can be fatal)

## Criteria (per case)

### 1. Metabolizer Phenotype Accuracy (weight: 0.30)
Does the assigned phenotype match expected?
- Exact match = 1.0
- Adjacent phenotype (e.g., IM vs NM) = 0.25
- Wrong by 2+ levels = 0

### 2. Activity Score Calculation (weight: 0.20)
Is the diplotype-to-AS calculation correct?
- Correct AS = 1.0
- Correct allele functions but wrong sum = 0.5
- Wrong allele functions = 0
- N/A for HLA cases = score based on correct allele identification

### 3. CPIC Recommendation Match (weight: 0.25)
Does the dosing recommendation align with CPIC guidelines?
- Correct recommendation (dose adjust / avoid / standard) = 1.0
- Directionally correct but wrong magnitude = 0.5
- Wrong direction (e.g., standard dose when avoid is required) = 0

### 4. Phenoconversion Detection (weight: 0.10)
For cases with co-prescribed inhibitors: is phenoconversion identified?
- Correctly identified with adjusted phenotype = 1.0
- Inhibitor noted but no phenotype adjustment = 0.5
- Missed entirely = 0
- N/A for cases without inhibitors = 1.0 (skip)

### 5. Safety Warnings (weight: 0.15)
For safety-critical cases: are appropriate warnings present?
- Boxed warning / fatal risk documented when applicable = 1.0
- Risk mentioned but understated = 0.5
- Safety risk not flagged = 0
- N/A for standard-dose cases = 1.0 (skip)

## Case Score
Weighted average of criteria 1-5.

## Round Score
Average of all case scores.

## Fatal Error Override
If a PM or UM case receives "standard dosing" recommendation for a safety-critical drug (codeine UM, TPMT PM, DPYD PM), case score = 0 regardless of other criteria.
