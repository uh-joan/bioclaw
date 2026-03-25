# Scoring Checklist: immunotherapy-response-predictor

Target: 0.9

## Criteria (per case)

### 1. Response Tier Accuracy (weight: 0.30)
Does the assigned tier (HIGH/MODERATE/LOW) match expected?
- Exact match = 1.0
- Adjacent tier = 0.5
- Off by 2 tiers = 0

### 2. Component Score Accuracy (weight: 0.25)
Are TMB, MSI, PD-L1, and neoantigen sub-scores calculated correctly per the skill's scoring tables?
- All components within expected range = 1.0
- 1 component off = 0.75
- 2 components off = 0.5
- 3+ off = 0

### 3. Resistance/Sensitivity Modifiers (weight: 0.20)
Are resistance gene penalties (STK11, PTEN, JAK1/2, B2M) and sensitivity bonuses (POLE) correctly applied?
- Correct modifier applied when expected = 1.0
- Modifier mentioned but wrong magnitude = 0.5
- Modifier missed entirely = 0
- N/A (no modifiers expected) = 1.0

### 4. Cancer-Type Context (weight: 0.15)
Does the report note cancer-specific nuances (e.g., RCC responds despite low TMB, PDAC is immune-cold, SCLC benefits from IO+chemo regardless of PD-L1)?
- Key nuance from expected_details captured = 1.0
- Generic response without cancer-specific context = 0.5
- Ignores cancer biology = 0

### 5. Agent Recommendation (weight: 0.10)
Are appropriate ICI agents recommended?
- Matches expected agents = 1.0
- Partially correct = 0.5
- Wrong or no recommendation = 0

## Override
If a LOW case (PDAC, MSS CRC) receives HIGH tier, case score = 0. Over-prediction in immune-cold tumors is dangerous.
