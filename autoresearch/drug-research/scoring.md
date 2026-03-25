# Scoring Checklist: drug-research

Target: 0.9

## Criteria (per case)

### 1. Section Completeness (weight: 0.25)
Are all 11 mandatory sections present and populated?
- 11/11 sections populated (no [Analyzing...] remaining) = 1.0
- 10/11 = 0.75
- 9/11 = 0.5
- < 9 = 0.25
- For investigational/withdrawn drugs: sparse sections acceptable if noted as "insufficient data — [reason]"

### 2. Compound Disambiguation (weight: 0.15)
Are database IDs correctly resolved?
- >= 3 IDs resolved (PubChem CID, ChEMBL, DrugBank, FDA, CAS) = 1.0
- 2 IDs = 0.5
- 0-1 IDs = 0

### 3. Mechanism-Target Accuracy (weight: 0.20)
Does the MOA and primary target match expected?
- Correct mechanism + correct primary target = 1.0
- Correct mechanism, wrong/missing target = 0.5
- Wrong mechanism = 0

### 4. Evidence Grading (weight: 0.15)
Are T1-T4 evidence tiers correctly assigned per section?
- Tiers present and appropriate for compound type (T1 for approved, T2-T3 for investigational) = 1.0
- Tiers present but some misassigned = 0.5
- No evidence grading = 0

### 5. Clinical Relevance (weight: 0.25)
Are the key differentiating details captured?
- Key trials identified by name = +0.25
- Safety signals/boxed warnings documented = +0.25
- PGx relevance noted when applicable = +0.25
- Competitive context or withdrawal reason documented = +0.25
- Sum of applicable items / number of applicable items

## Case Score
Weighted average of criteria 1-5.

## Round Score
Average of all case scores.

## Hallucination Guard
If the report fabricates trial names, invents approval dates, or attributes wrong mechanisms, deduct 0.5 from case score per fabrication.
