# Scoring Checklist: fda-consultant

Target: 0.9

## Criteria (per case)

### 1. Regulatory Pathway Accuracy (weight: 0.30)
Is the correct pathway/classification/mechanism identified?
- Correct pathway with rationale = 1.0
- Correct pathway without rationale = 0.5
- Wrong pathway = 0

### 2. Key Facts Accuracy (weight: 0.25)
Are the specific regulatory facts correct (dates, designations, requirements)?
- Key facts from expected_details match = 1.0
- Most facts correct with 1 error = 0.5
- Multiple factual errors = 0

### 3. Practical Recommendations (weight: 0.20)
Are actionable recommendations provided (what to file, what studies needed, what strategy)?
- Clear actionable guidance = 1.0
- General guidance without specifics = 0.5
- No recommendations = 0

### 4. Cross-Reference Quality (weight: 0.15)
Does the report reference relevant FDA guidance documents, precedents, or similar cases?
- Specific precedent/guidance cited = 1.0
- General regulatory awareness shown = 0.5
- No regulatory context = 0

### 5. Report Completeness (weight: 0.10)
Are all required_sections present?
- All present = 1.0
- Missing 1 = 0.5
- Missing 2+ = 0

## Override
If a Class III device (e.g., pacemaker) is recommended for 510(k) instead of PMA, case score = 0.
If accelerated approval is recommended without mentioning confirmatory trial requirement, deduct 0.3.
