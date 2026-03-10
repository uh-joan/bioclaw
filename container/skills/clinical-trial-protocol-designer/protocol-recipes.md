# Clinical Trial Protocol Generation Recipes

Production-ready recipes for protocol design, sample size calculations, regulatory pathway selection, and document generation.

---

## Recipe 1: Waypoint-Based State Management

**Description:** Use JSON checkpoint files to persist state across multi-step protocol generation. Each major phase writes a waypoint so the process can resume, audit, or branch without re-running earlier steps.

```json
{
  "$schema": "protocol-waypoint-v1",
  "protocol_id": "PROTO-2026-0042",
  "created_at": "2026-03-10T09:00:00Z",
  "updated_at": "2026-03-10T11:45:00Z",
  "current_phase": "DESIGN_COMPLETE",
  "phases": {
    "PRECEDENT_RESEARCH": {
      "status": "complete",
      "completed_at": "2026-03-10T09:25:00Z",
      "output_file": "precedent_research.json",
      "summary": "Found 12 precedent trials; 5 analyzed in detail"
    },
    "DESIGN_SELECTION": {
      "status": "complete",
      "completed_at": "2026-03-10T09:50:00Z",
      "output_file": "study_design.json",
      "summary": "Phase 3, randomized, double-blind, placebo-controlled, superiority"
    },
    "POPULATION_DEFINITION": {
      "status": "complete",
      "completed_at": "2026-03-10T10:15:00Z",
      "output_file": "population.json",
      "summary": "18 inclusion, 12 exclusion criteria defined"
    },
    "SAMPLE_SIZE": {
      "status": "complete",
      "completed_at": "2026-03-10T10:40:00Z",
      "output_file": "sample_size.json",
      "summary": "N=604 (302 per arm), 80% power, alpha=0.05"
    },
    "ENDPOINTS": {
      "status": "complete",
      "completed_at": "2026-03-10T11:00:00Z",
      "output_file": "endpoints.json",
      "summary": "Primary: PFS (RECIST 1.1); 4 secondary endpoints"
    },
    "PROTOCOL_DOCUMENT": {
      "status": "in_progress",
      "started_at": "2026-03-10T11:15:00Z",
      "output_file": "protocol_draft.md",
      "sections_complete": [1, 2, 3, 4, 5],
      "sections_remaining": [6, 7, 8, 9, 10, 11, 12]
    },
    "SAP": {
      "status": "not_started",
      "output_file": null
    },
    "SAFETY_MONITORING": {
      "status": "not_started",
      "output_file": null
    }
  },
  "mcp_calls": [
    {"tool": "mcp__ctgov__ct_gov_studies", "method": "search", "timestamp": "2026-03-10T09:05:00Z"},
    {"tool": "mcp__pubmed__pubmed_articles", "method": "search_keywords", "timestamp": "2026-03-10T09:10:00Z"},
    {"tool": "mcp__fda__fda_info", "method": "lookup_drug", "timestamp": "2026-03-10T09:15:00Z"}
  ]
}
```

**Key Parameters:**
- `current_phase`: tracks which phase is active; used for resume logic
- `phases[].status`: one of `"not_started"`, `"in_progress"`, `"complete"`, `"error"`
- `phases[].output_file`: path to the phase-specific output artifact
- `mcp_calls`: append-only log of all MCP invocations for traceability

**Expected Output:** A `protocol_waypoint.json` file updated after each phase, enabling resume-from-checkpoint and full audit trail.

---

## Recipe 2: Device vs Drug Regulatory Pathway Branching

**Description:** Determine the correct regulatory pathway based on whether the investigational product is a device or a drug, then branch protocol requirements accordingly.

```
REGULATORY PATHWAY DECISION TREE
=================================

Is the investigational product a DEVICE or a DRUG/BIOLOGIC?

DEVICE PATH
├── What is the device risk class?
│   │
│   ├── Class I (low risk, general controls)
│   │   └── 510(k) Exempt or 510(k)
│   │       Protocol needs: performance testing, biocompatibility (if applicable)
│   │       Clinical trial: usually NOT required
│   │
│   ├── Class II (moderate risk, special controls)
│   │   ├── Predicate device exists?
│   │   │   ├── YES → 510(k) pathway
│   │   │   │   Protocol needs: substantial equivalence testing
│   │   │   │   Clinical trial: may be required (depends on guidance)
│   │   │   └── NO → De Novo classification
│   │   │       Protocol needs: clinical evidence of safety & effectiveness
│   │   │       Clinical trial: typically required
│   │   └── Novel technology?
│   │       └── De Novo → clinical trial usually required
│   │
│   └── Class III (high risk, premarket approval)
│       └── PMA pathway
│           Protocol needs: valid scientific evidence (usually RCT)
│           Clinical trial: REQUIRED
│           Pre-submission: IDE (Investigational Device Exemption) required
│
│   IDE Requirements:
│   - Significant risk device → FDA IDE approval required before trial
│   - Non-significant risk device → IRB approval only (abbreviated IDE)
│   - IDE application includes: protocol, device description, risk analysis,
│     manufacturing info, investigator agreements

DRUG/BIOLOGIC PATH
├── What is the product type?
│   │
│   ├── Small molecule drug
│   │   └── IND → Phase 1/2/3 → NDA
│   │       IND contents: CMC, pharmacology/toxicology, clinical protocol
│   │
│   ├── Biologic (protein, antibody, gene therapy, cell therapy)
│   │   └── IND → Phase 1/2/3 → BLA
│   │       Additional: potency assays, immunogenicity plan, lot release
│   │
│   └── Biosimilar
│       └── IND → analytical + clinical studies → 351(k) BLA
│           Protocol needs: PK/PD equivalence, immunogenicity comparison
│
│   IND Requirements:
│   - Pre-IND meeting (Type B) recommended for novel mechanisms
│   - 30-day FDA review period before trial may begin
│   - Annual IND reports required
│   - IND safety reports: 15-day for serious, 7-day for fatal/life-threatening

# MCP calls to determine pathway:
# For devices:
mcp__fda__fda_info(
  method: "lookup_device",
  search_term: "device_name",
  search_type: "device_classification"
)
# Returns: device_class, product_code, regulation_number, submission_type

# For drugs:
mcp__fda__fda_info(
  method: "lookup_drug",
  search_term: "drug_name",
  search_type: "label"
)
# Returns: approval pathway, application_number (NDA vs BLA)
```

**Key Parameters:**
- `product_type`: `"device"` or `"drug"` or `"biologic"` or `"combination"`
- `device_class`: I, II, or III (from FDA classification database)
- `predicate_exists`: boolean — determines 510(k) vs De Novo for Class II
- `significant_risk`: boolean — determines full IDE vs abbreviated IDE

**Expected Output:** A `regulatory_pathway` object specifying the submission type (510(k)/De Novo/PMA/IDE/IND/NDA/BLA), required pre-clinical data, and protocol-specific requirements for that pathway.

---

## Recipe 3: ClinicalTrials.gov Search Integration

**Description:** Search ClinicalTrials.gov for precedent trials to inform protocol design decisions. Filter by condition, phase, status, and intervention type to find the most relevant comparators.

```
# Step 1: Broad search for precedent trials
mcp__ctgov__ct_gov_studies(
  method: "search",
  condition: "non-small cell lung cancer",
  intervention: "pembrolizumab",
  phase: "PHASE3",
  status: "completed",
  sort: "@relevance",
  pageSize: 20
)

# Step 2: Get full details for top candidates
# Select the 3-5 most relevant trials from Step 1 results
for nctId in ["NCT02578680", "NCT02142738", "NCT03850444"]:
    mcp__ctgov__ct_gov_studies(
      method: "get",
      nctId: nctId
    )

# Step 3: Extract design parameters from precedent trials
precedent_analysis = {
  "trials_reviewed": 5,
  "design_patterns": {
    "most_common_primary_endpoint": "PFS (3/5 trials)",
    "control_arm": "platinum-doublet chemotherapy (4/5 trials)",
    "randomization_ratio": "1:1 (4/5), 2:1 (1/5)",
    "blinding": "open-label (3/5), double-blind (2/5)",
    "biomarker_stratification": "PD-L1 TPS (5/5 trials)"
  },
  "sample_sizes": {
    "range": "305 - 1274",
    "median": 616,
    "enrollment_durations_months": [18, 24, 30, 22, 26]
  },
  "eligibility_commonalities": [
    "Age >= 18",
    "ECOG PS 0-1",
    "Measurable disease per RECIST 1.1",
    "No prior systemic therapy for advanced/metastatic disease",
    "No active autoimmune disease",
    "No prior anti-PD-1/PD-L1 therapy"
  ],
  "observed_effect_sizes": {
    "median_PFS_experimental": "10.3 months (range: 6.9-16.7)",
    "median_PFS_control": "5.1 months (range: 4.2-6.0)",
    "hazard_ratio_range": "0.50 - 0.69"
  }
}

# Step 4: Use autocomplete for terminology standardization
mcp__ctgov__ct_gov_studies(
  method: "suggest",
  term: "non-small cell"
)
# Returns standardized condition terms for protocol use
```

**Key Parameters:**
- `condition`: disease or condition name (use `suggest` method to standardize)
- `intervention`: drug name, drug class, or device name
- `phase`: `"PHASE1"`, `"PHASE2"`, `"PHASE3"`, `"PHASE4"` (or `"EARLY_PHASE1"`)
- `status`: `"completed"` for precedent analysis, `"recruiting"` for competitive landscape
- `pageSize`: up to 100; use 20 for initial search, expand if needed

**Expected Output:** A `precedent_analysis` object summarizing design patterns, sample sizes, eligibility criteria, and observed effect sizes across comparable trials.

---

## Recipe 4: Sample Size Calculation — Two-Sample t-Test (Continuous Endpoints)

**Description:** Calculate sample size for trials with a continuous primary endpoint (e.g., change from baseline in HbA1c, blood pressure, pain score) using a two-sample t-test with Cohen's d effect size.

```
FORMULA: Two-sample t-test sample size
=======================================

N per arm = 2 * ((Z_alpha + Z_beta) / d)^2

Where:
  Z_alpha = Z-value for significance level
    - Two-sided alpha = 0.05 → Z_alpha = 1.960
    - Two-sided alpha = 0.025 → Z_alpha = 2.241
    - One-sided alpha = 0.025 → Z_alpha = 1.960

  Z_beta = Z-value for power
    - 80% power → Z_beta = 0.842
    - 85% power → Z_beta = 1.036
    - 90% power → Z_beta = 1.282

  d = Cohen's d effect size = (mu_1 - mu_2) / sigma_pooled
    - Small effect:  d = 0.2
    - Medium effect: d = 0.5
    - Large effect:  d = 0.8

WORKED EXAMPLE: HbA1c reduction trial
======================================

Given:
  - Expected HbA1c reduction in treatment arm: -1.2%
  - Expected HbA1c reduction in placebo arm:   -0.4%
  - Pooled standard deviation:                  1.5%
  - Alpha = 0.05 (two-sided)
  - Power = 80%

Step 1: Calculate Cohen's d
  d = |(-1.2) - (-0.4)| / 1.5
  d = 0.8 / 1.5
  d = 0.533

Step 2: Calculate N per arm
  N = 2 * ((1.960 + 0.842) / 0.533)^2
  N = 2 * (2.802 / 0.533)^2
  N = 2 * (5.257)^2
  N = 2 * 27.64
  N = 55.3
  N = 56 per arm (round up)

Step 3: Apply dropout adjustment (Recipe 6)
  dropout_rate = 0.15
  N_adjusted = 56 / (1 - 0.15) = 56 / 0.85 = 65.9 → 66 per arm

Step 4: Total enrollment
  N_total = 66 * 2 = 132 patients

OUTPUT JSON:
{
  "endpoint_type": "continuous",
  "test": "two_sample_t_test",
  "effect_size_cohens_d": 0.533,
  "mean_difference": 0.8,
  "pooled_sd": 1.5,
  "alpha": 0.05,
  "alpha_sides": "two-sided",
  "power": 0.80,
  "n_per_arm_unadjusted": 56,
  "dropout_rate": 0.15,
  "n_per_arm_adjusted": 66,
  "n_total": 132,
  "randomization_ratio": "1:1"
}
```

**Key Parameters:**
- `mu_1`, `mu_2`: expected means (or mean changes) in each arm
- `sigma_pooled`: pooled standard deviation — source from precedent trial publications
- `alpha`: significance level (0.05 is standard; use 0.025 for one-sided)
- `power`: 0.80 (standard) or 0.90 (for confirmatory Phase 3)
- `dropout_rate`: applied via Recipe 6

**Expected Output:** A JSON object with all assumptions, intermediate calculations, and final N per arm (both unadjusted and dropout-adjusted).

---

## Recipe 5: Sample Size Calculation — Two-Proportion z-Test (Binary Endpoints)

**Description:** Calculate sample size for trials with a binary primary endpoint (e.g., overall response rate, clinical cure rate, event rate) using a two-proportion z-test with pooled proportions.

```
FORMULA: Two-proportion z-test sample size
============================================

N per arm = ((Z_alpha * sqrt(2 * p_bar * (1 - p_bar)) +
              Z_beta * sqrt(p1*(1-p1) + p2*(1-p2)))^2) / (p1 - p2)^2

Where:
  p1 = expected proportion in control arm
  p2 = expected proportion in treatment arm
  p_bar = (p1 + p2) / 2  (pooled proportion under H0)

WORKED EXAMPLE: Objective Response Rate (ORR) trial
=====================================================

Given:
  - Expected ORR in control arm (p1):    0.25 (25%)
  - Expected ORR in treatment arm (p2):  0.45 (45%)
  - Alpha = 0.05 (two-sided)
  - Power = 80%

Step 1: Calculate pooled proportion
  p_bar = (0.25 + 0.45) / 2 = 0.35

Step 2: Calculate numerator components
  Component A = Z_alpha * sqrt(2 * p_bar * (1 - p_bar))
               = 1.960 * sqrt(2 * 0.35 * 0.65)
               = 1.960 * sqrt(0.455)
               = 1.960 * 0.6745
               = 1.322

  Component B = Z_beta * sqrt(p1*(1-p1) + p2*(1-p2))
               = 0.842 * sqrt(0.25*0.75 + 0.45*0.55)
               = 0.842 * sqrt(0.1875 + 0.2475)
               = 0.842 * sqrt(0.4350)
               = 0.842 * 0.6595
               = 0.555

Step 3: Calculate N per arm
  N = (1.322 + 0.555)^2 / (0.45 - 0.25)^2
  N = (1.877)^2 / (0.20)^2
  N = 3.523 / 0.04
  N = 88.1
  N = 89 per arm (round up)

Step 4: Apply dropout adjustment
  dropout_rate = 0.10
  N_adjusted = 89 / (1 - 0.10) = 89 / 0.90 = 98.9 → 99 per arm

Step 5: Total enrollment
  N_total = 99 * 2 = 198 patients

OUTPUT JSON:
{
  "endpoint_type": "binary",
  "test": "two_proportion_z_test",
  "p_control": 0.25,
  "p_treatment": 0.45,
  "absolute_difference": 0.20,
  "p_bar_pooled": 0.35,
  "alpha": 0.05,
  "alpha_sides": "two-sided",
  "power": 0.80,
  "n_per_arm_unadjusted": 89,
  "dropout_rate": 0.10,
  "n_per_arm_adjusted": 99,
  "n_total": 198,
  "randomization_ratio": "1:1"
}
```

**Key Parameters:**
- `p1` (p_control): expected event/response rate in the control arm — source from precedent trials or natural history data
- `p2` (p_treatment): expected event/response rate in the treatment arm — source from Phase 2 data or mechanism-based estimate
- `absolute_difference`: p2 - p1 must be clinically meaningful (discuss with clinical team)
- `p_bar`: pooled proportion, calculated automatically

**Expected Output:** A JSON object with all assumptions, the pooled proportion, intermediate calculations, and final N per arm.

---

## Recipe 6: Dropout Rate Adjustment

**Description:** Inflate the calculated sample size to account for expected patient attrition (dropout, withdrawal, loss to follow-up). Apply after any base sample size calculation.

```
FORMULA:
  N_adjusted = ceil(N_baseline / (1 - dropout_rate))

DROPOUT RATE GUIDELINES BY TRIAL TYPE:
========================================

| Trial Type                     | Typical Dropout Rate | Rationale                          |
|-------------------------------|---------------------|------------------------------------|
| Oncology (advanced disease)    | 5-10%               | High motivation, short duration    |
| Oncology (adjuvant)            | 10-15%              | Longer duration, patients feel well |
| Chronic disease (cardiology)   | 10-20%              | Long follow-up, treatment fatigue  |
| CNS/psychiatry                 | 20-30%              | Adherence challenges, side effects |
| Rare disease                   | 5-10%               | Motivated patients, few options    |
| Pediatric                      | 10-15%              | Parental withdrawal                |
| Healthy volunteer (Phase 1)    | 5%                  | Short duration, financial incentive|
| Vaccine (large-scale)          | 10-15%              | Loss to follow-up                  |

WORKED EXAMPLE:
===============

Base sample size: N_baseline = 302 per arm
Trial type: Chronic disease (rheumatology), 52-week treatment period
Dropout rate estimate: 15%

N_adjusted = ceil(302 / (1 - 0.15))
N_adjusted = ceil(302 / 0.85)
N_adjusted = ceil(355.3)
N_adjusted = 356 per arm

Total enrollment: 356 * 2 = 712 patients
Additional patients needed for dropout: (356 - 302) * 2 = 108

OUTPUT JSON:
{
  "n_baseline_per_arm": 302,
  "dropout_rate": 0.15,
  "dropout_rate_source": "precedent trials in rheumatology (median 14.2%)",
  "n_adjusted_per_arm": 356,
  "n_total_adjusted": 712,
  "additional_patients_for_dropout": 108
}
```

**Key Parameters:**
- `N_baseline`: the sample size before dropout adjustment (from Recipe 4, 5, or Schoenfeld formula)
- `dropout_rate`: decimal between 0 and 1; source from precedent trials in the same disease area and duration
- Always use `ceil()` — round up to the next whole number

**Expected Output:** `N_adjusted` per arm and total, with the dropout rate and its source documented.

---

## Recipe 7: Sensitivity Analysis Scenarios

**Description:** Run the sample size calculation under alternative assumptions to test robustness. Standard scenarios include 90% power (instead of 80%) and reduced effect size (more conservative efficacy estimate).

```
SCENARIO FRAMEWORK:
====================

Base case:
  - Power: 80%, Alpha: 0.05 (two-sided), Effect size: from Phase 2 data
  - N_base = calculated from Recipe 4 or 5

Scenario 1: INCREASED POWER (90%)
  - Rationale: Regulatory preference for confirmatory Phase 3 trials
  - Change: Z_beta = 1.282 (instead of 0.842)
  - All other parameters unchanged
  - Typical increase: ~30-35% more patients than 80% power

Scenario 2: REDUCED EFFECT SIZE
  - Rationale: Phase 2 effect sizes often shrink in Phase 3
  - Change: reduce Cohen's d by 20-25%, or reduce absolute difference by 25%
  - Rule of thumb: Phase 3 effect ≈ 75% of Phase 2 observed effect
  - Typical increase: ~75-80% more patients than base case

Scenario 3: COMBINED (90% power + reduced effect)
  - Worst-case planning scenario
  - Typical increase: ~130-150% more patients than base case

WORKED EXAMPLE (continuous endpoint, from Recipe 4):
=====================================================

Base case: d=0.533, 80% power → N=56 per arm

Scenario 1: 90% power
  N = 2 * ((1.960 + 1.282) / 0.533)^2
  N = 2 * (3.242 / 0.533)^2
  N = 2 * (6.083)^2
  N = 2 * 37.00
  N = 74 per arm (+32%)

Scenario 2: Reduced effect (d = 0.533 * 0.75 = 0.400)
  N = 2 * ((1.960 + 0.842) / 0.400)^2
  N = 2 * (2.802 / 0.400)^2
  N = 2 * (7.005)^2
  N = 2 * 49.07
  N = 99 per arm (+77%)

Scenario 3: 90% power + reduced effect
  N = 2 * ((1.960 + 1.282) / 0.400)^2
  N = 2 * (3.242 / 0.400)^2
  N = 2 * (8.105)^2
  N = 2 * 65.69
  N = 132 per arm (+136%)

OUTPUT JSON (sensitivity table):
{
  "base_case": {
    "power": 0.80, "effect_size": 0.533, "n_per_arm": 56, "n_total": 112
  },
  "scenario_90_power": {
    "power": 0.90, "effect_size": 0.533, "n_per_arm": 74, "n_total": 148,
    "increase_vs_base": "32%"
  },
  "scenario_reduced_effect": {
    "power": 0.80, "effect_size": 0.400, "n_per_arm": 99, "n_total": 198,
    "increase_vs_base": "77%"
  },
  "scenario_combined": {
    "power": 0.90, "effect_size": 0.400, "n_per_arm": 132, "n_total": 264,
    "increase_vs_base": "136%"
  },
  "recommendation": "Target N=99 per arm (reduced effect scenario) as primary; budget for N=132 per arm (combined scenario) as contingency."
}
```

**Key Parameters:**
- `effect_reduction_factor`: typically 0.75 (i.e., Phase 3 effect = 75% of Phase 2 observed effect)
- `power_scenarios`: [0.80, 0.85, 0.90] — always include 90% for regulatory discussions
- `recommendation`: state which scenario to use for enrollment target vs budget planning

**Expected Output:** A sensitivity table with N per arm for each scenario, percentage increase vs base case, and a recommendation for which scenario to use for planning.

---

## Recipe 8: Inclusion/Exclusion Criteria Generation

**Description:** Generate protocol-ready inclusion and exclusion criteria with specific lab value thresholds expressed as multiples of the upper limit of normal (ULN) or absolute values, tailored to the therapeutic area.

```
INCLUSION CRITERIA TEMPLATE (with ULN thresholds)
===================================================

GENERAL CRITERIA:
1. Age >= [18] years at the time of informed consent
2. Histologically or cytologically confirmed [disease] per [classification system]
3. [Disease stage/severity]: [Stage IV / ECOG PS 0-1 / NYHA Class I-II / DAS28 > 3.2]
4. Measurable disease per [RECIST 1.1 / RANO / disease-specific criteria]
5. Prior therapy: [treatment-naive / failed >= 1 prior line / specific prior therapy required]

ORGAN FUNCTION CRITERIA (lab values within [14] days of enrollment):

| System       | Parameter         | Threshold                     | Notes                                |
|-------------|-------------------|-------------------------------|--------------------------------------|
| Hepatic     | ALT (SGPT)        | <= 3.0 x ULN                  | <= 5.0 x ULN if liver metastases     |
| Hepatic     | AST (SGOT)        | <= 3.0 x ULN                  | <= 5.0 x ULN if liver metastases     |
| Hepatic     | Total bilirubin   | <= 1.5 x ULN                  | <= 3.0 x ULN if Gilbert syndrome     |
| Hepatic     | Albumin           | >= 2.5 g/dL                   |                                      |
| Renal       | eGFR (CKD-EPI)    | >= 30 mL/min/1.73m2           | >= 60 for nephrotoxic agents         |
| Renal       | Serum creatinine  | <= 1.5 x ULN                  | Alternative to eGFR                  |
| Hematologic | ANC               | >= 1,500 /uL                  | >= 1,000 /uL if bone marrow involved |
| Hematologic | Platelets         | >= 100,000 /uL                | >= 75,000 /uL if bone marrow involved|
| Hematologic | Hemoglobin        | >= 9.0 g/dL                   | No transfusion within 7 days         |
| Coagulation | INR               | <= 1.5 x ULN                  | Unless on anticoagulation            |
| Coagulation | aPTT              | <= 1.5 x ULN                  | Unless on anticoagulation            |
| Cardiac     | QTcF              | <= 470 ms (F) / <= 450 ms (M) | Fridericia correction preferred      |
| Cardiac     | LVEF              | >= 50%                        | By ECHO or MUGA within 28 days      |
| Pancreatic  | Lipase            | <= 1.5 x ULN                  | For GI-targeted therapies            |
| Thyroid     | TSH               | Within normal limits          | For immunotherapy trials             |

REPRODUCTIVE CRITERIA:
7. Women of childbearing potential (WOCBP): negative serum pregnancy test within
   [7] days of first dose AND agreement to use [highly effective contraception]
   during treatment and for [X] months after last dose
8. Male patients with WOCBP partners: agreement to use [barrier contraception]
   during treatment and for [X] months after last dose
9. Not breastfeeding

CONSENT:
10. Able to understand and willing to sign written informed consent
11. Willing to comply with scheduled visits, treatment plan, and laboratory tests


EXCLUSION CRITERIA TEMPLATE
============================

DISEASE-RELATED:
1. Known active CNS metastases (treated and stable >= [4] weeks allowed)
2. Leptomeningeal disease
3. Prior treatment with [specific drug class] within [washout period]
4. Known [KRAS G12C / EGFR / BRAF] mutation (if selecting for specific biomarker)

MEDICAL HISTORY:
5. Active autoimmune disease requiring systemic treatment within [2] years
   (replacement therapy, e.g., thyroxine, is permitted)
6. History of (non-infectious) pneumonitis requiring systemic steroids
7. Active infection requiring systemic antibacterial, antifungal, or antiviral therapy
8. Known HIV infection with CD4 < [200] or detectable viral load
9. Active hepatitis B (HBsAg+ or detectable HBV DNA) or hepatitis C (detectable HCV RNA)
10. Unstable cardiovascular: MI, unstable angina, stroke, or TIA within [6] months
11. Uncontrolled hypertension: systolic > [160] mmHg or diastolic > [100] mmHg
    despite optimal medical management

CONCOMITANT MEDICATION:
12. Systemic corticosteroids > [10] mg/day prednisone equivalent within [14] days
    (physiologic replacement doses permitted)
13. Strong CYP3A4 inhibitors or inducers within [14] days or [5 half-lives]
14. Live vaccine within [30] days of first dose

GENERAL:
15. Participation in another interventional clinical trial within [30] days
    or [5 half-lives of the investigational agent], whichever is longer
16. Known hypersensitivity to study drug or any excipient
17. Any condition that, in the investigator's opinion, would jeopardize patient
    safety or interfere with protocol compliance
```

**Key Parameters:**
- ULN multiples: standard is 3x ULN for hepatic (5x if liver mets); adjust per drug toxicity profile
- `eGFR threshold`: 30 mL/min is standard; increase to 60 for nephrotoxic agents
- `washout period`: 5 half-lives of prior therapy or 30 days, whichever is longer
- Cardiac thresholds: include QTcF and LVEF if drug has known cardiac risk

**Expected Output:** Complete, protocol-ready inclusion and exclusion criteria sections with all lab thresholds specified.

---

## Recipe 9: Schedule of Activities Table Generation

**Description:** Generate the Schedule of Activities (SoA) table — the visits-by-assessments matrix that defines every procedure at every study visit. This is typically Protocol Appendix B.

```
SCHEDULE OF ACTIVITIES (visits x assessments matrix)
=====================================================

Legend:
  X = required at this visit
  - = not performed
  * = if clinically indicated
  W = within window (+/- days)

| Assessment              | Screening | Baseline | Wk 2   | Wk 4   | Wk 8   | Wk 12  | Wk 16  | Wk 24  | Wk 36  | Wk 48  | EOT  | FU-30d | FU-90d |
|                         | D-28 to-1 | D1 (C1D1)| C1D15  | C2D1   | C3D1   | C4D1   | C5D1   | C7D1   | C10D1  | C13D1  |      |        |        |
|-------------------------|-----------|----------|--------|--------|--------|--------|--------|--------|--------|--------|------|--------|--------|
| **Informed consent**    | X         | -        | -      | -      | -      | -      | -      | -      | -      | -      | -    | -      | -      |
| **Eligibility review**  | X         | X        | -      | -      | -      | -      | -      | -      | -      | -      | -    | -      | -      |
| **Medical history**     | X         | -        | -      | -      | -      | -      | -      | -      | -      | -      | -    | -      | -      |
| **Demographics**        | X         | -        | -      | -      | -      | -      | -      | -      | -      | -      | -    | -      | -      |
| **Physical exam**       | X         | X        | -      | X      | X      | X      | X      | X      | X      | X      | X    | -      | -      |
| **Vital signs**         | X         | X        | X      | X      | X      | X      | X      | X      | X      | X      | X    | X      | -      |
| **Height**              | X         | -        | -      | -      | -      | -      | -      | -      | -      | -      | -    | -      | -      |
| **Weight**              | X         | X        | -      | X      | X      | X      | -      | X      | -      | X      | X    | -      | -      |
| **ECOG PS**             | X         | X        | -      | X      | X      | X      | X      | X      | X      | X      | X    | -      | -      |
| **12-lead ECG**         | X         | X        | -      | X      | -      | X      | -      | X      | -      | X      | X    | -      | -      |
| **ECHO/MUGA (LVEF)**    | X         | -        | -      | -      | -      | X      | -      | X      | -      | X      | X    | -      | -      |
| **CT/MRI (tumor)**      | X         | -        | -      | -      | X      | -      | -      | X      | -      | X      | X    | -      | -      |
| **Pregnancy test**      | X         | X        | -      | X      | X      | X      | X      | X      | X      | X      | X    | -      | -      |
| **CBC w/ diff**         | X         | X        | X      | X      | X      | X      | X      | X      | X      | X      | X    | X      | -      |
| **CMP**                 | X         | X        | -      | X      | X      | X      | X      | X      | X      | X      | X    | X      | -      |
| **Coagulation (INR)**   | X         | X        | -      | X      | -      | X      | -      | X      | -      | X      | X    | -      | -      |
| **Urinalysis**          | X         | -        | -      | X      | -      | X      | -      | X      | -      | X      | X    | -      | -      |
| **Thyroid (TSH, fT4)**  | X         | -        | -      | -      | X      | -      | -      | X      | -      | X      | X    | -      | -      |
| **Biomarker sample**    | -         | X        | -      | -      | X      | -      | -      | X      | -      | X      | X    | -      | -      |
| **PK sample**           | -         | X        | X      | X      | X      | -      | -      | X      | -      | -      | -    | -      | -      |
| **Study drug admin**    | -         | X        | X      | X      | X      | X      | X      | X      | X      | X      | -    | -      | -      |
| **Con-med review**      | X         | X        | X      | X      | X      | X      | X      | X      | X      | X      | X    | X      | -      |
| **AE assessment**       | -         | X        | X      | X      | X      | X      | X      | X      | X      | X      | X    | X      | X      |
| **PRO (EQ-5D-5L)**      | -         | X        | -      | -      | X      | -      | -      | X      | -      | X      | X    | -      | -      |
| **PRO (EORTC QLQ-C30)** | -         | X        | -      | -      | X      | -      | -      | X      | -      | X      | X    | -      | -      |
| **Survival follow-up**  | -         | -        | -      | -      | -      | -      | -      | -      | -      | -      | -    | -      | X      |

Visit Windows:
  - Screening: Day -28 to Day -1 (28-day window)
  - On-treatment visits: +/- 3 days for weekly, +/- 7 days for monthly
  - Imaging: +/- 7 days
  - EOT visit: within 7 days of last dose
  - Follow-up 30-day: 30 +/- 7 days after last dose (safety)
  - Follow-up 90-day: 90 +/- 14 days after last dose (survival/late AEs)

CUSTOMIZATION PARAMETERS:
  cycle_length_days: 28          # Adjust for 21-day or 14-day cycles
  total_treatment_duration: 48   # Weeks
  imaging_frequency: "q8w"       # Every 8 weeks; change to q6w or q12w as needed
  pk_sampling_visits: [1, 2, 3, 4, 7]  # Cycle numbers for PK collection
  pro_frequency: "q8w"           # PRO collection frequency
```

**Key Parameters:**
- `cycle_length_days`: 14, 21, or 28 — determines visit spacing
- `imaging_frequency`: driven by expected response kinetics (q6w for fast-growing tumors, q12w for slow)
- `pk_sampling_visits`: front-loaded to characterize PK early
- Visit windows: tighter for safety labs, wider for imaging

**Expected Output:** A complete SoA table in markdown format, ready for insertion into Protocol Section 4 or Appendix B.

---

## Recipe 10: FDA 12-Section Protocol Structure

**Description:** Generate the full FDA-recommended protocol structure with all 12 sections, sub-sections, and content guidance. This follows the ICH E6(R2) and FDA guidance for IND protocols.

```
FDA PROTOCOL TEMPLATE — 12 SECTIONS
=====================================

SECTION 1: TITLE PAGE
  - Full protocol title (descriptive, includes phase, design, population)
  - Protocol number: [SPONSOR]-[COMPOUND]-[INDICATION]-[PHASE]-[SEQ]
    Example: ACME-ACM101-NSCLC-P3-001
  - IND/IDE number (if assigned)
  - Sponsor name and address
  - Medical monitor name and contact
  - Protocol version and date
  - Amendment history table

SECTION 2: COMPLIANCE STATEMENT
  - ICH E6(R2) GCP compliance
  - 21 CFR Parts 50, 56, 312 (drugs) or 812 (devices)
  - Declaration of Helsinki
  - Local regulatory requirements
  - Institutional Review Board / Ethics Committee approval

SECTION 3: SYNOPSIS
  - 2-3 page structured summary:
    | Element           | Content                                    |
    |-------------------|--------------------------------------------|
    | Title             | Full descriptive title                      |
    | Phase             | Phase [1/2/3]                               |
    | Indication        | [Disease and population]                    |
    | Objectives        | Primary, secondary, exploratory (1 line each)|
    | Design            | [Randomized, double-blind, placebo-controlled, etc.] |
    | Population        | Key inclusion/exclusion (3-5 bullets)       |
    | Sample Size       | N = [X], [power]% power, alpha = [X]        |
    | Duration          | Treatment: [X] weeks; Follow-up: [X] months |
    | Primary Endpoint  | [Endpoint] assessed by [method] at [time]   |
    | Statistical Method| [Test/model] for primary analysis            |

SECTION 4: BACKGROUND AND RATIONALE
  - Disease epidemiology and unmet need
  - Current standard of care
  - Investigational product: mechanism of action, nonclinical data
  - Clinical data to date (Phase 1/2 results if applicable)
  - Rationale for study design, dose, and population
  - Benefit-risk assessment

SECTION 5: OBJECTIVES AND ENDPOINTS
  - Primary objective → Primary endpoint
  - Secondary objectives → Secondary endpoints (rank-ordered)
  - Exploratory objectives → Exploratory endpoints
  - Endpoint definitions with assessment method and timing

SECTION 6: STUDY DESIGN
  - Overall design description with schema diagram
  - Randomization: method, ratio, stratification factors
  - Blinding: level, unblinding procedures, emergency unblinding
  - Treatment arms: dose, route, schedule, duration
  - Dose modifications: reductions, holds, discontinuation criteria
  - Study periods: screening, treatment, follow-up

SECTION 7: STUDY INTERVENTION
  - Investigational product: formulation, storage, preparation, administration
  - Comparator/placebo: matching, formulation
  - Dose and schedule
  - Dose modification guidelines (tables)
  - Concomitant medications: permitted, prohibited, cautionary
  - Treatment compliance monitoring

SECTION 8: STUDY OPERATIONS
  - Schedule of Activities (Recipe 9)
  - Visit procedures (detailed per-visit instructions)
  - Screening and enrollment procedures
  - Randomization and drug assignment
  - Study drug accountability
  - Discontinuation: of study drug vs withdrawal from study

SECTION 9: STATISTICAL CONSIDERATIONS
  - Analysis populations (ITT, mITT, per-protocol, safety)
  - Sample size and power (Recipes 4-7)
  - Primary analysis: method, model, covariates
  - Secondary analyses
  - Multiplicity adjustment
  - Interim analyses: timing, alpha spending function
  - Subgroup analyses (pre-specified)
  - Missing data: estimand, sensitivity analyses (Recipe 12)

SECTION 10: STUDY GOVERNANCE
  - Data and Safety Monitoring Board (DSMB) charter
  - Stopping rules: efficacy, futility, safety
  - Adverse event reporting: definitions, grading, attribution, timelines
  - Serious adverse event reporting: 24-hour notification, IND safety reports
  - Protocol deviations: major vs minor, reporting
  - Regulatory reporting: annual IND report, development safety update report (DSUR)

SECTION 11: REFERENCES
  - Numbered reference list (Vancouver style)
  - Key references: pivotal trials, FDA guidance documents, disease guidelines

SECTION 12: APPENDICES
  - A: Informed Consent Form template
  - B: Schedule of Events (detailed)
  - C: Investigational product information
  - D: Performance status scales (ECOG, Karnofsky)
  - E: Response criteria (RECIST 1.1, RANO, etc.)
  - F: CTCAE version for AE grading
  - G: Contraceptive guidance
  - H: Country-specific requirements
```

**Key Parameters:**
- `protocol_number`: follow sponsor's naming convention
- `phase`: determines which sections require the most detail (Phase 1 emphasizes safety; Phase 3 emphasizes efficacy)
- `regulatory_pathway`: IND (drugs) or IDE (devices) — changes compliance references

**Expected Output:** A complete protocol document skeleton with all 12 sections populated with section-specific content guidance, ready for clinical team review and completion.

---

## Recipe 11: Adverse Event Classification Framework

**Description:** Define the adverse event (AE) classification system for the protocol, including severity grading (CTCAE 1-5), attribution scale, SAE definitions, and 24-hour reporting rules.

```
ADVERSE EVENT SEVERITY GRADING (CTCAE v5.0)
=============================================

| Grade | Severity          | Definition                                                |
|-------|-------------------|-----------------------------------------------------------|
| 1     | Mild              | Asymptomatic or mild symptoms; clinical or diagnostic     |
|       |                   | observations only; intervention not indicated             |
| 2     | Moderate          | Minimal, local, or noninvasive intervention indicated;    |
|       |                   | limiting age-appropriate instrumental ADL                 |
| 3     | Severe            | Medically significant but not immediately life-threatening;|
|       |                   | hospitalization or prolongation indicated; disabling;      |
|       |                   | limiting self-care ADL                                    |
| 4     | Life-threatening  | Urgent intervention indicated                             |
| 5     | Death             | Death related to AE                                       |

ADL = Activities of Daily Living
  Instrumental ADL: cooking, shopping, managing finances, using telephone
  Self-care ADL: bathing, dressing, feeding, toileting, taking medications


ATTRIBUTION SCALE (CAUSALITY ASSESSMENT)
=========================================

| Category      | Definition                                                        |
|--------------|-------------------------------------------------------------------|
| Definite      | Temporal relationship + known mechanism + positive rechallenge     |
|               | + no alternative explanation                                      |
| Probable      | Temporal relationship + known mechanism + clinically consistent    |
|               | + alternative explanation unlikely                                |
| Possible      | Temporal relationship exists + could be explained by study drug    |
|               | OR by other factors (concurrent disease, concomitant medication)  |
| Unlikely      | Temporal relationship exists but alternative explanation more     |
|               | likely (concurrent disease, concomitant medication)              |
| Unrelated     | No temporal relationship OR clearly caused by another etiology    |

Rule: Grade >= 3 with attribution "possible" or higher → expedited reporting


SERIOUS ADVERSE EVENT (SAE) CRITERIA
======================================

An AE is SERIOUS if it meets ANY of the following:
  1. Results in death
  2. Is life-threatening (at the time of the event)
  3. Requires inpatient hospitalization or prolongation of existing hospitalization
  4. Results in persistent or significant disability/incapacity
  5. Is a congenital anomaly/birth defect
  6. Is a medically important event that may jeopardize the patient or
     require intervention to prevent one of the outcomes listed above

EXCEPTIONS (do NOT qualify as SAE):
  - Elective hospitalization for pre-existing condition (unless worsened)
  - Planned hospitalization per protocol (e.g., protocol-required biopsy)
  - Emergency room visit < 24 hours that does not meet other SAE criteria


SAE REPORTING TIMELINES
========================

| Event Type                            | Notification Timeline  | Report To            |
|--------------------------------------|----------------------|----------------------|
| Fatal or life-threatening SAE         | Within 24 hours      | Sponsor, IRB, DSMB   |
| All other SAEs                        | Within 24 hours      | Sponsor              |
| IND Safety Report (sponsor → FDA)     | 15 calendar days     | FDA (7 days if fatal)|
| Annual IND Report                     | Within 60 days of    | FDA                  |
|                                       | IND anniversary      |                      |
| DSUR (Development Safety Update)      | Annually             | All regulatory       |
|                                       |                      | authorities          |

SAE REPORT CONTENT:
  - Patient ID (not name)
  - Event term (MedDRA preferred term)
  - Onset date and resolution date (or "ongoing")
  - Severity grade (CTCAE)
  - Attribution to study drug
  - Action taken with study drug (none, held, reduced, discontinued)
  - Outcome (resolved, resolving, not resolved, fatal, unknown)
  - Narrative description (clinical course, relevant labs, imaging)


ADVERSE EVENT OF SPECIAL INTEREST (AESI)
==========================================

Define protocol-specific AESIs based on drug mechanism and class effects:

| AESI Category                | Monitoring Requirements              |
|-----------------------------|--------------------------------------|
| Immune-related AEs (irAEs)   | Thyroid Q12W, LFTs Q4W, symptoms Q2W |
| Cardiac events (QTc, LVEF)   | ECG Q4W, ECHO Q12W                   |
| Hepatotoxicity               | LFTs Q2W x 12W, then Q4W            |
| Infusion reactions            | Monitor during + 1h post-infusion    |
| Cytokine release syndrome    | IL-6, CRP, ferritin at onset         |
| Tumor lysis syndrome          | Electrolytes, uric acid, LDH pre-dose|

Each AESI requires:
  - Specific grading criteria (may differ from standard CTCAE)
  - Management algorithm (hold/resume/discontinue thresholds)
  - Expedited reporting regardless of seriousness
```

**Key Parameters:**
- `ctcae_version`: currently v5.0 (released 2017); specify in the protocol
- `attribution_threshold`: typically "possible" or higher triggers expedited reporting
- `aesi_list`: defined based on drug mechanism, class effects, and nonclinical findings
- `reporting_timeline`: 24 hours to sponsor for all SAEs; 7 days to FDA if fatal

**Expected Output:** Complete AE classification section for Protocol Section 10 (Safety Monitoring), including grading scale, attribution criteria, SAE definitions, reporting timelines, and AESI monitoring requirements.

---

## Recipe 12: Statistical Analysis Plan Outline

**Description:** Generate the SAP framework covering primary analysis (ITT), sensitivity analyses (per-protocol), subgroup analyses, and missing data handling strategies including MMRM, MICE, and tipping point analysis.

```
STATISTICAL ANALYSIS PLAN (SAP) — OUTLINE
============================================

1. INTRODUCTION
   - Protocol reference and version
   - SAP version and date (SAP finalized BEFORE database lock)
   - Responsible statistician

2. ANALYSIS POPULATIONS

   | Population     | Definition                                           | Used For          |
   |---------------|------------------------------------------------------|-------------------|
   | ITT           | All randomized patients, analyzed as randomized       | Primary efficacy  |
   | mITT          | All randomized who received >= 1 dose and had >= 1   | Sensitivity       |
   |               | post-baseline assessment                              |                   |
   | Per-Protocol  | mITT who completed >= 80% of planned treatment        | Sensitivity       |
   |               | without major protocol deviations                     |                   |
   | Safety        | All patients who received >= 1 dose, analyzed as      | Safety analyses   |
   |               | treated (regardless of randomization)                 |                   |

3. PRIMARY ANALYSIS

   Endpoint: [Primary endpoint definition]
   Population: ITT
   Method: [depends on endpoint type]

   For time-to-event (PFS, OS):
     - Kaplan-Meier estimation per arm
     - Stratified log-rank test (stratified by randomization factors)
     - Cox proportional hazards model: HR and 95% CI
     - Covariates: stratification factors
     - Censoring rules: defined per endpoint

   For continuous (change from baseline):
     - Mixed Model for Repeated Measures (MMRM)
     - Model: change = treatment + visit + treatment*visit + baseline + stratification factors
     - Unstructured covariance matrix
     - Kenward-Roger degrees of freedom
     - Primary contrast: treatment difference at Week [X]

   For binary (response rate):
     - Cochran-Mantel-Haenszel test stratified by randomization factors
     - Logistic regression for adjusted odds ratio
     - 95% CI for treatment difference (Miettinen-Nurminen method)

4. MULTIPLICITY ADJUSTMENT

   Hierarchical (gatekeeping) testing procedure:
   1. Primary endpoint at alpha = 0.05 (two-sided)
   2. If significant → test Key Secondary Endpoint 1 at alpha = 0.05
   3. If significant → test Key Secondary Endpoint 2 at alpha = 0.05
   4. Remaining secondary endpoints: descriptive only (nominal p-values)

   Alternative: Hochberg step-up procedure for co-primary endpoints
   Alternative: Bonferroni for independent secondary endpoints

5. SENSITIVITY ANALYSES

   a. Per-protocol population analysis
      - Same method as primary, applied to PP population
      - Consistency with ITT result supports robustness

   b. Alternative missing data methods (see Section 8)

   c. Unstratified analysis
      - Remove stratification factors to assess their impact

   d. Covariate-adjusted analysis
      - Add pre-specified prognostic covariates to the primary model

6. SUBGROUP ANALYSES

   Pre-specified subgroups (forest plot display):
   - Age: < 65 vs >= 65 years
   - Sex: male vs female
   - Race: White vs non-White
   - Geographic region: North America vs Europe vs Asia-Pacific
   - Disease severity: [disease-specific categories]
   - Biomarker status: [positive vs negative]
   - Prior therapy: [0 vs >= 1 prior line]

   Rules:
   - Maximum 8-10 pre-specified subgroups
   - Interaction test p-values reported (not multiplicity adjusted)
   - Subgroup analyses are exploratory; no confirmatory claims
   - Forest plot with HR/OR and 95% CI per subgroup

7. INTERIM ANALYSES

   Number of interim analyses: [1-2]
   Timing: after [50%] and [75%] of target events (for event-driven trials)

   Alpha spending function:
   - Efficacy: O'Brien-Fleming (conservative early, preserves final alpha)
     - At 50% events: boundary Z = 2.963 (p ≈ 0.003)
     - At 75% events: boundary Z = 2.359 (p ≈ 0.018)
     - At final:      boundary Z = 2.014 (p ≈ 0.044)
   - Futility: non-binding (conditional power < 20% → recommend stopping)
   - Safety: no formal boundary; DSMB reviews unblinded safety at each interim

   DSMB recommendation options: Continue, Modify, Stop for efficacy,
   Stop for futility, Stop for safety

8. MISSING DATA HANDLING

   Estimand framework (ICH E9(R1)):
   - Treatment policy strategy: include all data regardless of treatment changes
   - Hypothetical strategy: estimate effect if all patients had adhered
   - Composite strategy: count non-adherence as treatment failure

   Primary approach: MMRM (inherently handles intermittent missing data
   under MAR assumption)

   Sensitivity analyses:

   a. MICE (Multiple Imputation by Chained Equations):
      - Generate M=50 imputed datasets
      - Imputation model includes: treatment, visit, baseline, stratification factors,
        and auxiliary variables correlated with outcome
      - Analyze each dataset; combine results using Rubin's rules
      - Provides valid inference under MAR

   b. Tipping Point Analysis:
      - For treatment arm: impute missing values as [delta] worse than predicted
      - Increase delta from 0 upward until treatment effect is no longer significant
      - Report the delta at which p > 0.05
      - Clinical interpretation: "results are robust unless missing patients in
        the treatment arm are at least [delta] units worse than predicted"

      Implementation:
        for delta in [0, 0.1, 0.2, 0.5, 1.0, 2.0]:
            imputed_data = MICE_impute(data)
            imputed_data[treatment_arm & missing] += delta
            result = analyze(imputed_data)
            record(delta, result.p_value, result.estimate)
        tipping_point = min(delta where p > 0.05)

   c. Pattern Mixture Models:
      - Classify patients by dropout pattern
      - Model outcome conditional on dropout pattern
      - Sensitivity: MNAR (missing not at random) assumptions

   d. Return to Baseline:
      - Impute missing post-baseline values with baseline value
      - Conservative (penalizes missing data)

   e. Worst-case imputation:
      - Treatment arm missing → worst observed value
      - Control arm missing → best observed value
      - Most conservative; rarely changes conclusions if primary result is strong

9. TABLES, FIGURES, AND LISTINGS (TFL) SHELL
   - Demographic and baseline characteristics (Table 14.1.x)
   - Primary endpoint analysis (Table 14.2.1, Figure 14.2.1)
   - Secondary endpoint analyses (Tables 14.2.x)
   - Subgroup forest plots (Figure 14.2.x)
   - Adverse event summary tables (Tables 14.3.x)
   - Laboratory shift tables (Tables 14.3.x)
   - Patient disposition CONSORT diagram (Figure 14.1.1)
```

**Key Parameters:**
- `primary_analysis_method`: MMRM (continuous), stratified log-rank (time-to-event), CMH test (binary)
- `multiplicity_method`: hierarchical gatekeeping is most common; Hochberg for co-primary
- `interim_analysis_count`: 1-2 for Phase 3; none for most Phase 2
- `alpha_spending`: O'Brien-Fleming (standard); Lan-DeMets for flexible timing
- `mice_imputations`: M=50 minimum for stable results; M=100 for high-stakes analyses
- `tipping_point_deltas`: start at 0, increment in clinically meaningful units

**Expected Output:** A complete SAP outline ready for statistical team expansion, with methodology specified for every analysis type and missing data scenario.
