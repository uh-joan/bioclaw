# Scoring Checklist: peer-review

Target: 0.9

## Criteria (per case)

### 1. Decision Accuracy (weight: 0.25)
Does the overall recommendation (Accept/Minor/Major/Reject) match expected?
- Exact match = 1.0
- Adjacent decision = 0.5
- Off by 2+ = 0

### 2. ScholarEval Score Range (weight: 0.20)
Is the overall ScholarEval score (8-40) within the expected range?
- Within range = 1.0
- Within 3 points of bounds = 0.5
- Outside by >3 = 0

### 3. Major Issues Identified (weight: 0.25)
Are the expected major comments/flaws identified?
- >= 75% of expected major issues identified = 1.0
- 50-74% = 0.5
- < 50% = 0
- N/A (no major issues expected) = check no false major issues raised = 1.0

### 4. Integrity Flags (weight: 0.15)
For cases with data integrity/ethical concerns, are they flagged?
- Concern correctly flagged with recommendation = 1.0
- Concern noted but understated = 0.5
- Missed entirely = 0
- N/A (no integrity issues) = 1.0

### 5. Nuance and Calibration (weight: 0.15)
Does the review demonstrate calibrated judgment (not over-harsh on pilots, not under-critical on flawed studies)?
- Demonstrates appropriate calibration = 1.0
- Somewhat over/under-critical = 0.5
- Severely miscalibrated = 0

## Override
If fabricated references (ai-generated-text-suspect) or figure manipulation (figure-manipulation-suspect) are not flagged, case score = 0.
If a well-conducted pilot study is rejected solely for being "underpowered," deduct 0.3.
