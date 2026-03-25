# Scoring Checklist: delphi-method

Target: 0.9

## Criteria (per case)

### 1. Consensus Estimate Range (weight: 0.25)
Does the final consensus estimate fall within expected range?
- Within range = 1.0
- Within 10% of bounds = 0.5
- Outside by >10% = 0

### 2. Panel Process Fidelity (weight: 0.20)
Were all 4 Delphi rounds executed with proper structure?
- All 4 rounds with 5+ expert perspectives = 1.0
- 3 rounds or <5 experts = 0.5
- <3 rounds = 0

### 3. Convergence Measurement (weight: 0.20)
Are IQR/CV convergence metrics calculated and convergence level correctly assessed?
- Convergence metrics present and assessment matches expected (strong/moderate/low) = 1.0
- Metrics present but assessment off = 0.5
- No convergence measurement = 0

### 4. Minority Report (weight: 0.15)
For cases where minority positions are expected, are they preserved?
- Minority positions documented with reasoning = 1.0
- Minority noted but without reasoning = 0.5
- Minority suppressed or absent when expected = 0
- N/A (strong consensus, no minority expected) = 1.0

### 5. Evidence-Grounded Reasoning (weight: 0.20)
Do expert assessments cite specific evidence (trial data, base rates, publications)?
- >= 3 specific evidence citations across panel = 1.0
- 1-2 citations = 0.5
- Pure opinion without evidence anchoring = 0

## Override
If a high-consensus question (BRCA testing) shows IQR suggesting non-convergence, or a controversial question (rapamycin longevity) shows false strong consensus, deduct 0.3 — the skill must reflect actual uncertainty levels honestly.
