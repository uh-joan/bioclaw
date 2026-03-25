# Scoring Checklist: drug-interaction-analyst

Target: 0.9

## Criteria (per case)

### 1. Severity Classification Accuracy (weight: 0.25)
Does the severity rating match expected (Contraindicated / Major / Moderate / Minor)?
- Exact match = 1.0
- Adjacent severity = 0.5
- Off by 2+ = 0

### 2. Mechanism Identification (weight: 0.25)
Is the correct interaction mechanism identified (CYP enzyme, transporter, pharmacodynamic)?
- Correct CYP/transporter/PD mechanism with specific enzyme = 1.0
- Correct pathway but wrong enzyme = 0.5
- Wrong mechanism = 0

### 3. Clinical Management (weight: 0.25)
Are appropriate management recommendations provided?
- >= 2 expected management actions matched = 1.0
- 1 matched = 0.5
- None matched or dangerous recommendation = 0

### 4. Alternative Drug Suggestions (weight: 0.15)
Are safer alternatives recommended when applicable?
- Correct alternatives with rationale = 1.0
- Alternatives mentioned without rationale = 0.5
- No alternatives when expected = 0
- N/A (no alternatives needed) = 1.0

### 5. Report Completeness (weight: 0.10)
Are all required_sections present?
- All present = 1.0
- Missing 1 = 0.5
- Missing 2+ = 0

## Override
If the negative control (amoxicillin + acetaminophen) is classified as Major or Contraindicated, case score = 0.
If a Contraindicated pair (simvastatin + clarithromycin, MAOI + tyramine) is classified as Minor, case score = 0.
