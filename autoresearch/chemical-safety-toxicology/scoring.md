# Scoring Checklist: chemical-safety-toxicology

Target: 0.9

## Criteria (per case)

### 1. Risk Classification Accuracy (weight: 0.25)
Does the risk classification (Critical / High / Medium / Low) match expected?
- Exact match = 1.0
- Adjacent level = 0.5
- Off by 2+ = 0

### 2. Structural Alert Detection (weight: 0.20)
Are PAINS, Brenk, and toxicophore alerts correctly identified?
- All expected alerts identified = 1.0
- >= 50% identified = 0.5
- Major alerts missed = 0
- N/A (no alerts expected) = correctly confirms clean profile = 1.0

### 3. Drug-Likeness Assessment (weight: 0.15)
Are Lipinski/Veber rules correctly applied with violation count?
- Correct violation count and compliance assessment = 1.0
- Off by 1 violation = 0.5
- Wrong assessment = 0

### 4. Mechanism-Based Safety (weight: 0.25)
For cases with specific toxicity mechanisms (hERG, DILI, genotoxicity), is the mechanism correctly identified?
- Correct mechanism with supporting data = 1.0
- Partially correct = 0.5
- Wrong mechanism or missed critical toxicity = 0

### 5. Pipeline Phase Completeness (weight: 0.15)
Are the required phases from the 8-phase pipeline addressed?
- All required phases documented = 1.0
- Missing 1 phase = 0.5
- Missing 2+ = 0

## Override
If a withdrawn/Critical compound (terfenadine, NDMA) receives "Low" risk, case score = 0.
If a clean compound (aspirin, hypothetical clean candidate) receives "Critical," case score = 0.
If curcumin PAINS alerts are not flagged, deduct 0.3 (this is the canonical PAINS example).
