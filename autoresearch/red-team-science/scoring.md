# Scoring Checklist: red-team-science

Target: 0.9

## Criteria (per case)

### 1. Adversarial Severity Score Range (weight: 0.20)
Is the 0-100 severity score within expected range?
- Within range = 1.0
- Within 10 points = 0.5
- Outside by >10 = 0

### 2. Vulnerability Identification (weight: 0.30)
Are the key expected vulnerabilities identified?
- >= 75% of expected vulnerabilities found = 1.0
- 50-74% = 0.5
- < 50% = 0

### 3. Attack Mode Execution (weight: 0.20)
Were the required attack modes applied?
- All required modes executed with structured output = 1.0
- >= 50% of modes = 0.5
- < 50% = 0

### 4. Hidden Assumption Extraction (weight: 0.15)
Are non-obvious hidden assumptions identified?
- >= 2 expected hidden assumptions identified = 1.0
- 1 identified = 0.5
- None = 0

### 5. Mitigation Quality (weight: 0.15)
Are actionable mitigations proposed for identified vulnerabilities?
- Specific, actionable mitigations for top vulnerabilities = 1.0
- Generic mitigations = 0.5
- No mitigations = 0

## Override
If the well-validated case (imatinib-CML) receives severity >50, case score = 0 — over-attacking proven therapies erodes credibility.
If a clearly speculative claim (AI 3-5 year timeline) receives severity <30, case score = 0 — failed to identify obvious vulnerabilities.
