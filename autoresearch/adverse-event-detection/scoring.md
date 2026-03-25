# Scoring Checklist: adverse-event-detection

Target: 0.9

## Criteria (per case)

### 1. Signal Detection Accuracy (weight: 0.25)
Does the report correctly identify whether a signal exists (true positive) or doesn't (true negative)?
- Correct signal/no-signal determination = 1.0
- Ambiguous conclusion when signal is clear = 0.5
- Wrong conclusion (false positive on negative control, or missed known signal) = 0

### 2. Disproportionality Computation (weight: 0.25)
Are the 2x2 table and statistical measures (PRR, ROR, IC, EBGM) present and correctly structured?
- All 4 measures computed with 2x2 table shown = 1.0
- 2-3 measures with table = 0.75
- 1 measure or table missing = 0.5
- No quantitative analysis = 0

### 3. Signal Score and Classification (weight: 0.20)
Does the Safety Signal Score fall within expected range and classification tier match?
- Score within range AND classification matches = 1.0
- Score within range OR classification matches (not both) = 0.5
- Neither matches = 0

### 4. Biological Plausibility (weight: 0.15)
Is the mechanistic explanation correct?
- Mechanism described and matches expected = 1.0
- Partial mechanism (correct pathway, incomplete explanation) = 0.5
- Wrong mechanism or missing = 0

### 5. Nuance and Context (weight: 0.15)
Does the report capture the expected nuances (controversy, risk factors, class effects, demographic patterns)?
- Key nuance from expected_details captured = 1.0
- Generic analysis without case-specific nuance = 0.5
- Missing or wrong context = 0

## Override
If the negative control (aspirin-alopecia) is classified as a signal (MODERATE or higher), case score = 0. False positive signals are as dangerous as missed signals.
