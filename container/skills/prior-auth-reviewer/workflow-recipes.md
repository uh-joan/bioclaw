# Prior Authorization Workflow Recipes

Production-ready recipes for PA request processing, MCP orchestration, and decision automation.

---

## Recipe 1: Two-Stage Pipeline Architecture

**Description:** Split PA processing into two sequential stages — intake/assessment gathers and validates all data, then decision/notification renders the determination and generates output artifacts.

```
STAGE 1 — INTAKE & ASSESSMENT
┌─────────────────────────────────────────┐
│ 1. Parse PA request (provider, patient, │
│    drug, diagnosis, clinical notes)     │
│ 2. Parallel MCP validation (Recipe 2)  │
│ 3. Coverage policy lookup              │
│ 4. Clinical evidence extraction        │
│ 5. Write assessment.json waypoint      │
└──────────────────┬──────────────────────┘
                   │
                   ▼
STAGE 2 — DECISION & NOTIFICATION
┌─────────────────────────────────────────┐
│ 1. Load assessment.json                │
│ 2. Apply rubric scoring (Recipe 8)     │
│ 3. Render decision (APPROVE/DENY/PEND) │
│ 4. Generate notification letter        │
│ 5. Write audit trail                   │
└─────────────────────────────────────────┘
```

**Key Parameters:**
- `stage`: `"intake"` or `"decision"` — controls which half of the pipeline executes
- `pa_request_id`: unique identifier linking both stages
- `assessment_path`: file path to the intermediate `assessment.json` waypoint

**Expected Output:** Stage 1 produces `assessment.json`; Stage 2 produces a decision letter, audit log, and final `pa_decision.json`.

---

## Recipe 2: Parallel MCP Orchestration

**Description:** Fire NPI verification, ICD-10 validation, and CMS coverage lookup simultaneously to minimize wall-clock time on the intake stage. All three calls are independent and can execute in parallel.

```typescript
// Execute all three MCP calls in parallel
const [npiResult, icdResult, coverageResult] = await Promise.all([
  // Provider credential verification
  mcp__nlm__nlm_ct_codes({
    method: "npi-individuals",
    terms: request.provider_npi,
    maxList: 5
  }),

  // Diagnosis code validation
  mcp__nlm__nlm_ct_codes({
    method: "icd-10-cm",
    terms: request.icd10_code,
    maxList: 5
  }),

  // Formulary and coverage policy lookup
  mcp__medicare__medicare_info({
    method: "search_formulary",
    formulary_drug_name: request.drug_name
  })
]);

// Merge results into a single validation object
const validation = {
  provider_valid: npiResult.results.length > 0 && npiResult.results[0].status === "active",
  provider_specialty: npiResult.results[0]?.taxonomy_description ?? "UNKNOWN",
  diagnosis_valid: icdResult.results.length > 0,
  diagnosis_description: icdResult.results[0]?.name ?? "UNKNOWN",
  formulary_tier: coverageResult.results[0]?.tier ?? null,
  pa_required: coverageResult.results[0]?.prior_authorization === "Y",
  step_therapy: coverageResult.results[0]?.step_therapy === "Y",
  quantity_limit: coverageResult.results[0]?.quantity_limit === "Y",
  timestamp: new Date().toISOString()
};
```

**Key Parameters:**
- `request.provider_npi`: 10-digit NPI number or provider name
- `request.icd10_code`: ICD-10-CM code from the PA request (e.g., `"M06.9"`)
- `request.drug_name`: generic or brand drug name

**Expected Output:** A merged `validation` object with boolean flags for provider validity, diagnosis validity, formulary tier, and PA/step-therapy/QL requirements.

---

## Recipe 3: Provider Credential Verification via NLM MCP

**Description:** Look up a provider's NPI record to confirm active status, verify taxonomy/specialty is appropriate for the requested service, and flag mismatches.

```
# Step 1: NPI lookup
mcp__nlm__nlm_ct_codes(
  method: "npi-individuals",
  terms: "1234567890",       # NPI number or provider name
  maxList: 5
)

# Step 2: Parse and validate response fields
Expected response fields:
  - npi: "1234567890"
  - status: "active" | "deactivated"
  - name_prefix, first_name, last_name, credential
  - taxonomy_code: "207RR0500X"
  - taxonomy_description: "Internal Medicine, Rheumatology"
  - addresses: [{practice_address}, {mailing_address}]
  - enumeration_date: "2005-03-15"

# Step 3: Specialty appropriateness check
SPECIALTY_RULES = {
  "biologics_rheumatology": ["Rheumatology", "Internal Medicine"],
  "oncology_drugs": ["Medical Oncology", "Hematology/Oncology"],
  "psychiatric_meds": ["Psychiatry", "Psychiatry & Neurology"],
  "cardiology_devices": ["Cardiovascular Disease", "Interventional Cardiology"],
  "dermatology_biologics": ["Dermatology"]
}

if provider.taxonomy_description not in SPECIALTY_RULES[drug_category]:
    flag = "SPECIALTY_MISMATCH"
    # Does not auto-deny; flags for reviewer attention
```

**Key Parameters:**
- `terms`: NPI number (preferred) or "LastName, FirstName" format
- `drug_category`: maps the requested drug to a specialty rule set
- `maxList`: keep at 5; NPI numbers are unique so only 1 result expected for numeric lookup

**Expected Output:** Provider verification status (`VERIFIED`, `DEACTIVATED`, `NOT_FOUND`, `SPECIALTY_MISMATCH`) with the full provider record attached.

---

## Recipe 4: Diagnosis Code Validation via NLM MCP

**Description:** Validate the ICD-10-CM code from the PA request, navigate the code hierarchy to check parent/child relationships, and confirm the diagnosis supports the requested drug's indication.

```
# Step 1: Validate the submitted ICD-10 code
mcp__nlm__nlm_ct_codes(
  method: "icd-10-cm",
  terms: "M06.9",          # Code from PA request
  maxList: 5
)

# Expected response:
#   code: "M06.9"
#   name: "Rheumatoid arthritis, unspecified"
#   hierarchy: ["M00-M99", "M05-M14", "M06", "M06.9"]

# Step 2: Hierarchical navigation — check parent category
mcp__nlm__nlm_ct_codes(
  method: "icd-10-cm",
  terms: "M06",            # Parent code
  maxList: 20
)
# Returns all M06.x subcodes for context

# Step 3: Cross-reference diagnosis against drug indication
INDICATION_MAP = {
  "adalimumab": {
    "approved": ["M06.*", "M05.*", "L40.*", "K50.*", "K51.*", "M45.*", "H20.*"],
    "off_label": ["M08.*", "L73.2"]
  }
}

# Match logic: submitted ICD-10 code must match an approved indication pattern
import re
code = "M06.9"
drug = "adalimumab"
approved = any(re.match(p.replace("*", ".*"), code) for p in INDICATION_MAP[drug]["approved"])
off_label = any(re.match(p.replace("*", ".*"), code) for p in INDICATION_MAP[drug]["off_label"])

if approved:
    indication_status = "ON_LABEL"
elif off_label:
    indication_status = "OFF_LABEL_KNOWN"
else:
    indication_status = "OFF_LABEL_UNSUPPORTED"
```

**Key Parameters:**
- `terms`: ICD-10-CM code (e.g., `"M06.9"`) or free-text diagnosis description
- `INDICATION_MAP`: dictionary mapping drug names to lists of approved and known off-label ICD-10 patterns
- Wildcard `*` matches any sub-classification

**Expected Output:** `indication_status` of `ON_LABEL`, `OFF_LABEL_KNOWN`, or `OFF_LABEL_UNSUPPORTED`, plus the full ICD-10 hierarchy for the submitted code.

---

## Recipe 5: Medicare Coverage Policy Lookup (NCD/LCD by Procedure)

**Description:** Search for National Coverage Determinations (NCDs) and Local Coverage Determinations (LCDs) relevant to the requested procedure or drug. Uses the Medicare MCP to find applicable policies by CPT/HCPCS code.

```
# Step 1: Validate the procedure code
mcp__nlm__nlm_ct_codes(
  method: "hcpcs-LII",
  terms: "J0135",            # HCPCS code for adalimumab
  maxList: 5
)
# Confirms: J0135 = "Injection, adalimumab, 20 mg"

# Step 2: Search Medicare formulary for the drug
mcp__medicare__medicare_info(
  method: "search_formulary",
  formulary_drug_name: "adalimumab"
)
# Returns: tier, PA flag, step therapy flag, quantity limits

# Step 3: Check Part B ASP pricing (for buy-and-bill drugs)
mcp__medicare__medicare_info(
  method: "get_asp_pricing",
  search_term: "adalimumab"
)
# Returns: ASP per unit, payment limit, effective quarter

# Step 4: Check spending data for cost context
mcp__medicare__medicare_info(
  method: "search_spending",
  spending_drug_name: "adalimumab",
  spending_type: "part_b"
)

# Step 5: Assemble coverage determination
coverage_policy = {
  "hcpcs_code": "J0135",
  "hcpcs_description": "Injection, adalimumab, 20 mg",
  "formulary_status": formulary_result,
  "asp_pricing": asp_result,
  "annual_spending": spending_result,
  "coverage_conditions": [
    "Diagnosis must be FDA-approved indication",
    "Step therapy: must have tried methotrexate for >=3 months",
    "Quantity limit: 40mg every other week (standard dosing)"
  ],
  "ncd_reference": "NCD 110.5 (if applicable)",
  "lcd_reference": "LCD L38865 (contractor-specific)"
}
```

**Key Parameters:**
- `hcpcs_code`: the CPT or HCPCS Level II code for the procedure/drug
- `formulary_drug_name`: generic name for formulary search
- `spending_type`: `"part_b"` for physician-administered drugs, `"part_d"` for self-administered

**Expected Output:** A `coverage_policy` object containing formulary status, pricing, applicable NCDs/LCDs, and coverage conditions that must be met.

---

## Recipe 6: CPT/HCPCS Procedure Code Validation

**Description:** Validate the procedure or supply code submitted on the PA request. Confirm the code is active, matches the requested service, and is billable under the applicable benefit.

```
# Step 1: HCPCS Level II code lookup (drugs, supplies, services)
mcp__nlm__nlm_ct_codes(
  method: "hcpcs-LII",
  terms: "J0135",
  maxList: 5
)
# Response:
#   code: "J0135"
#   short_description: "Injection, adalimumab, 20 mg"
#   long_description: "Injection, adalimumab, 20 mg"
#   status: "active"
#   effective_date: "2003-01-01"

# Step 2: For CPT codes, cross-reference with the drug/diagnosis
# CPT codes are numeric (e.g., 96413 = chemotherapy infusion)
# HCPCS J-codes are drug-specific

# Step 3: Validate code-to-diagnosis mapping
CODE_DIAGNOSIS_RULES = {
  "J0135": {
    "valid_icd10": ["M06.*", "M05.*", "L40.*", "K50.*", "K51.*", "M45.*"],
    "benefit_category": "Part B",
    "site_of_service": ["office", "outpatient_hospital", "home_infusion"],
    "units_per_dose": 1,      # 20mg per unit
    "max_units_per_claim": 2  # 40mg standard dose = 2 units
  },
  "96413": {
    "valid_icd10": ["C*", "D*"],
    "benefit_category": "Part B",
    "site_of_service": ["office", "outpatient_hospital"],
    "description": "Chemotherapy administration, IV infusion, first hour"
  }
}

validation_result = {
  "code_valid": True,
  "code_active": status == "active",
  "diagnosis_compatible": icd10_code matches valid_icd10 patterns,
  "benefit_category": "Part B",
  "units_requested_valid": requested_units <= max_units_per_claim,
  "site_of_service_valid": submitted_site in valid sites
}
```

**Key Parameters:**
- `terms`: HCPCS Level II code (e.g., `"J0135"`) or CPT code (e.g., `"96413"`)
- `CODE_DIAGNOSIS_RULES`: mapping of procedure codes to valid diagnosis patterns and billing rules
- `max_units_per_claim`: prevents over-billing

**Expected Output:** A `validation_result` with boolean checks for code validity, diagnosis compatibility, benefit category, unit limits, and site of service.

---

## Recipe 7: Clinical Evidence Extraction from Medical Records

**Description:** Extract structured data points from unstructured clinical notes submitted with a PA request. Identifies prior treatments tried, treatment durations, outcomes, contraindications, and lab values relevant to medical necessity.

```
# Input: raw clinical notes text from the PA request
clinical_notes = """
Patient has been on methotrexate 15mg weekly for 4 months with inadequate
response. DAS28-CRP remains 4.2 (moderate activity). Prior trial of
sulfasalazine was discontinued after 6 weeks due to GI intolerance.
Contraindicated for leflunomide due to hepatic impairment (ALT 3.2x ULN).
Current medications: prednisone 5mg daily, folic acid 1mg daily.
"""

# Extraction template — parse into structured fields
extracted_evidence = {
  "prior_treatments": [
    {
      "drug": "methotrexate",
      "dose": "15mg weekly",
      "duration": "4 months",
      "outcome": "inadequate_response",
      "objective_measure": "DAS28-CRP 4.2 (moderate activity)",
      "still_active": true
    },
    {
      "drug": "sulfasalazine",
      "dose": null,
      "duration": "6 weeks",
      "outcome": "discontinued_adverse_event",
      "adverse_event": "GI intolerance",
      "still_active": false
    }
  ],
  "contraindications": [
    {
      "drug": "leflunomide",
      "reason": "hepatic impairment",
      "supporting_lab": "ALT 3.2x ULN"
    }
  ],
  "current_medications": [
    {"drug": "prednisone", "dose": "5mg daily"},
    {"drug": "folic acid", "dose": "1mg daily"}
  ],
  "lab_values": {
    "ALT": {"value": "3.2x ULN", "status": "elevated"},
    "DAS28_CRP": {"value": 4.2, "interpretation": "moderate_disease_activity"}
  },
  "step_therapy_satisfied": true,
  "step_therapy_rationale": "Tried methotrexate >=3 months with inadequate response; sulfasalazine intolerant; leflunomide contraindicated"
}
```

**Key Parameters:**
- `clinical_notes`: raw text from the submitted PA request (provider's clinical justification)
- `prior_treatments[].outcome`: one of `"adequate_response"`, `"inadequate_response"`, `"discontinued_adverse_event"`, `"discontinued_other"`
- `step_therapy_satisfied`: boolean — automatically set to `true` if prior treatment attempts meet payer criteria

**Expected Output:** A structured `extracted_evidence` object with prior treatments, contraindications, current medications, lab values, and a step therapy determination.

---

## Recipe 8: Rubric-Driven Decision Framework

**Description:** Score the PA request across weighted dimensions and map the aggregate confidence to a decision. Thresholds: APPROVE if confidence > 85%, DENY if confidence < 30%, PEND otherwise.

```json
{
  "scoring_rubric": {
    "dimensions": [
      {
        "name": "provider_credentials",
        "weight": 0.10,
        "score": null,
        "rules": {
          "100": "NPI active, specialty matches drug category",
          "50": "NPI active, specialty is general (not specialty-specific)",
          "0": "NPI deactivated or not found"
        }
      },
      {
        "name": "diagnosis_validity",
        "weight": 0.15,
        "score": null,
        "rules": {
          "100": "ICD-10 valid and maps to on-label indication",
          "50": "ICD-10 valid, off-label but compendia-supported",
          "0": "ICD-10 invalid or no indication match"
        }
      },
      {
        "name": "formulary_compliance",
        "weight": 0.20,
        "score": null,
        "rules": {
          "100": "Drug on formulary, no restrictions or all restrictions met",
          "50": "Drug on formulary with unmet step therapy or QL",
          "0": "Drug not on formulary, no exception criteria met"
        }
      },
      {
        "name": "step_therapy",
        "weight": 0.20,
        "score": null,
        "rules": {
          "100": "All required step therapy agents tried with documented failure/intolerance",
          "50": "Partial step therapy with clinical justification for skip",
          "0": "No step therapy attempted, no exception documented"
        }
      },
      {
        "name": "clinical_evidence",
        "weight": 0.20,
        "score": null,
        "rules": {
          "100": "Strong evidence: FDA-approved indication + clinical notes support necessity",
          "50": "Moderate evidence: off-label with published RCT support",
          "0": "No evidence: off-label, no supporting literature"
        }
      },
      {
        "name": "cost_efficiency",
        "weight": 0.15,
        "score": null,
        "rules": {
          "100": "Requested drug is lowest-cost option or generic available",
          "75": "Brand requested but no generic/biosimilar available",
          "25": "Higher-cost option requested when lower-cost alternative exists",
          "0": "Specialty tier drug with available Tier 1-3 alternatives"
        }
      }
    ],
    "thresholds": {
      "APPROVE": ">= 85",
      "PEND": ">= 30 and < 85",
      "DENY": "< 30"
    }
  },
  "calculation": "confidence = sum(dimension.score * dimension.weight for each dimension)",
  "example": {
    "provider_credentials": {"score": 100, "weighted": 10.0},
    "diagnosis_validity": {"score": 100, "weighted": 15.0},
    "formulary_compliance": {"score": 50, "weighted": 10.0},
    "step_therapy": {"score": 100, "weighted": 20.0},
    "clinical_evidence": {"score": 100, "weighted": 20.0},
    "cost_efficiency": {"score": 75, "weighted": 11.25},
    "total_confidence": 86.25,
    "decision": "APPROVE"
  }
}
```

**Key Parameters:**
- `dimensions[].weight`: must sum to 1.0
- `dimensions[].score`: integer 0-100 assigned per the rules
- `thresholds`: APPROVE >= 85, DENY < 30, PEND is 30-84

**Expected Output:** A `confidence` score (0-100) and a `decision` of `APPROVE`, `DENY`, or `PEND`.

---

## Recipe 9: Waypoint JSON Structure for Assessment Persistence

**Description:** Write the intermediate assessment state to `assessment.json` at the end of Stage 1. This waypoint file is the contract between the intake and decision stages, enabling restart, audit, and human review.

```json
{
  "$schema": "assessment-waypoint-v1",
  "pa_request_id": "PA-20260310-00142",
  "created_at": "2026-03-10T14:32:00Z",
  "updated_at": "2026-03-10T14:35:22Z",
  "status": "ASSESSMENT_COMPLETE",
  "request": {
    "provider_npi": "1234567890",
    "provider_name": "Dr. Jane Smith",
    "patient_id": "PAT-88291",
    "drug_name": "adalimumab",
    "drug_strength": "40mg/0.8mL",
    "hcpcs_code": "J0135",
    "icd10_code": "M06.9",
    "diagnosis_description": "Rheumatoid arthritis, unspecified",
    "quantity_requested": 2,
    "days_supply": 28,
    "site_of_service": "office"
  },
  "validation": {
    "provider_verified": true,
    "provider_specialty": "Rheumatology",
    "provider_specialty_match": true,
    "icd10_valid": true,
    "icd10_hierarchy": ["M00-M99", "M05-M14", "M06", "M06.9"],
    "indication_status": "ON_LABEL",
    "hcpcs_valid": true,
    "hcpcs_description": "Injection, adalimumab, 20 mg"
  },
  "coverage": {
    "formulary_status": "on_formulary",
    "tier": 5,
    "pa_required": true,
    "step_therapy_required": true,
    "quantity_limit": "2 units per 28 days",
    "ncd_reference": null,
    "lcd_reference": "LCD L38865"
  },
  "clinical_evidence": {
    "prior_treatments": [
      {
        "drug": "methotrexate",
        "duration": "4 months",
        "outcome": "inadequate_response",
        "documented": true
      }
    ],
    "contraindications": [
      {"drug": "leflunomide", "reason": "hepatic impairment"}
    ],
    "step_therapy_satisfied": true,
    "supporting_literature": []
  },
  "cost_analysis": {
    "asp_per_unit": 1025.50,
    "total_cost_per_claim": 2051.00,
    "generic_available": false,
    "biosimilar_available": true,
    "biosimilar_names": ["adalimumab-atto", "adalimumab-bwwd"],
    "cost_comparison_note": "Biosimilars available at ~15-20% lower cost"
  },
  "recommendation": {
    "decision": "APPROVE",
    "confidence": 86.25,
    "rubric_scores": {
      "provider_credentials": 100,
      "diagnosis_validity": 100,
      "formulary_compliance": 50,
      "step_therapy": 100,
      "clinical_evidence": 100,
      "cost_efficiency": 75
    },
    "flags": ["BIOSIMILAR_AVAILABLE"],
    "notes": "Step therapy met via documented methotrexate failure. Consider biosimilar substitution."
  },
  "mcp_call_log": [
    {"tool": "mcp__nlm__nlm_ct_codes", "method": "npi-individuals", "timestamp": "2026-03-10T14:32:01Z", "success": true},
    {"tool": "mcp__nlm__nlm_ct_codes", "method": "icd-10-cm", "timestamp": "2026-03-10T14:32:01Z", "success": true},
    {"tool": "mcp__medicare__medicare_info", "method": "search_formulary", "timestamp": "2026-03-10T14:32:01Z", "success": true},
    {"tool": "mcp__medicare__medicare_info", "method": "get_asp_pricing", "timestamp": "2026-03-10T14:32:05Z", "success": true},
    {"tool": "mcp__nlm__nlm_ct_codes", "method": "hcpcs-LII", "timestamp": "2026-03-10T14:32:05Z", "success": true}
  ]
}
```

**Key Parameters:**
- `$schema`: version identifier for waypoint format (`"assessment-waypoint-v1"`)
- `status`: one of `"INTAKE_STARTED"`, `"VALIDATION_COMPLETE"`, `"ASSESSMENT_COMPLETE"`, `"DECISION_RENDERED"`
- `recommendation.confidence`: float 0-100 from the rubric scoring
- `mcp_call_log`: array of every MCP call made, for audit trail

**Expected Output:** A `assessment.json` file written to the working directory, readable by Stage 2 and by human reviewers.

---

## Recipe 10: Notification Letter Generation

**Description:** Generate approval, denial, or pending notification letters using templates with variable substitution. Letters follow CMS-mandated content requirements for Medicare/Medicaid PA notifications.

```markdown
# APPROVAL LETTER TEMPLATE

---
Authorization Number: {{auth_number}}
Date: {{decision_date}}
---

RE: Prior Authorization Approval

Dear {{provider_name}} (NPI: {{provider_npi}}),

This letter confirms that the prior authorization request for the following
has been **APPROVED**:

| Field | Detail |
|-------|--------|
| Patient | {{patient_name}} (ID: {{patient_id}}) |
| Drug | {{drug_name}} {{drug_strength}} |
| HCPCS | {{hcpcs_code}} — {{hcpcs_description}} |
| Diagnosis | {{icd10_code}} — {{diagnosis_description}} |
| Quantity | {{quantity_approved}} units per {{days_supply}} days |
| Effective | {{effective_date}} through {{expiration_date}} |

**Authorization Number: {{auth_number}}**

This authorization is valid for {{authorization_duration}} from the effective
date. A new prior authorization request must be submitted before the
expiration date for continued coverage.

{{#if conditions}}
**Conditions of Approval:**
{{#each conditions}}
- {{this}}
{{/each}}
{{/if}}

---

# DENIAL LETTER TEMPLATE

---
Authorization Number: {{auth_number}}
Date: {{decision_date}}
---

RE: Prior Authorization Denial

Dear {{provider_name}} (NPI: {{provider_npi}}),

The prior authorization request for the following has been **DENIED**:

| Field | Detail |
|-------|--------|
| Patient | {{patient_name}} (ID: {{patient_id}}) |
| Drug | {{drug_name}} {{drug_strength}} |
| Diagnosis | {{icd10_code}} — {{diagnosis_description}} |

**Reason for Denial:** {{denial_reason}}

**Clinical Rationale:** {{clinical_rationale}}

**Coverage Policy Reference:** {{policy_reference}}

**Your Appeal Rights:**
You or the patient may appeal this decision within {{appeal_window_days}} days
of receipt of this notice. To file an appeal:
1. Submit a written request for reconsideration
2. Include any additional clinical documentation supporting medical necessity
3. Send to: {{appeal_address}}

For expedited appeal (if delay could jeopardize health): call {{expedited_phone}}.

---

# PEND LETTER TEMPLATE

---
Reference: {{auth_number}}
Date: {{decision_date}}
---

RE: Additional Information Required — Prior Authorization Request

Dear {{provider_name}} (NPI: {{provider_npi}}),

The prior authorization request for **{{drug_name}}** for patient
**{{patient_name}}** requires additional information before a determination
can be made.

**Information Needed:**
{{#each missing_items}}
- [ ] {{this}}
{{/each}}

Please submit the requested documentation within **{{response_deadline_days}}
calendar days** of this notice. If documentation is not received by
**{{response_deadline_date}}**, this request will be denied.

Submit documentation to: {{submission_address}}
Fax: {{submission_fax}}
```

**Key Parameters:**
- `{{auth_number}}`: generated per Recipe 11 format
- `{{appeal_window_days}}`: typically 60 days for standard, 72 hours for expedited (Medicare)
- `{{response_deadline_days}}`: typically 14 days for pend requests
- `{{missing_items}}`: array of specific documents/information needed

**Expected Output:** A complete notification letter in markdown, ready for rendering to PDF or print.

---

## Recipe 11: Authorization Number Formatting

**Description:** Generate a unique, deterministic authorization number in the format `PA-YYYYMMDD-XXXXX` where the date is the decision date and the suffix is a zero-padded sequential or hash-based identifier.

```typescript
function generateAuthNumber(
  decisionDate: Date,
  requestId: string
): string {
  // Format date portion: YYYYMMDD
  const year = decisionDate.getFullYear();
  const month = String(decisionDate.getMonth() + 1).padStart(2, "0");
  const day = String(decisionDate.getDate()).padStart(2, "0");
  const datePart = `${year}${month}${day}`;

  // Generate 5-digit suffix from request ID
  // Option A: Sequential (if you have a counter)
  // const suffix = String(sequentialCounter).padStart(5, "0");

  // Option B: Hash-based (deterministic, no counter needed)
  const crypto = require("crypto");
  const hash = crypto.createHash("sha256").update(requestId).digest("hex");
  const numericHash = parseInt(hash.substring(0, 8), 16) % 100000;
  const suffix = String(numericHash).padStart(5, "0");

  return `PA-${datePart}-${suffix}`;
}

// Examples:
// generateAuthNumber(new Date("2026-03-10"), "REQ-001") => "PA-20260310-73821"
// generateAuthNumber(new Date("2026-03-10"), "REQ-002") => "PA-20260310-41056"
```

**Key Parameters:**
- `decisionDate`: the date the PA decision is rendered (not the request date)
- `requestId`: unique identifier for the PA request; used as hash input for the suffix
- Format: `PA-YYYYMMDD-XXXXX` (always 18 characters)

**Expected Output:** A string like `"PA-20260310-73821"` that is unique per request and deterministic (same input always produces the same number).

---

## Recipe 12: Audit Trail Generation

**Description:** Produce a timestamped decision log capturing every MCP call result, scoring decision, and the final determination. This log supports regulatory compliance, appeal review, and quality assurance.

```json
{
  "audit_trail": {
    "auth_number": "PA-20260310-73821",
    "pa_request_id": "REQ-001",
    "reviewer": "nanoclaw-prior-auth-agent",
    "review_started": "2026-03-10T14:32:00Z",
    "review_completed": "2026-03-10T14:35:45Z",
    "review_duration_seconds": 225,
    "events": [
      {
        "timestamp": "2026-03-10T14:32:00Z",
        "event": "INTAKE_STARTED",
        "detail": "PA request received for adalimumab (J0135) for M06.9"
      },
      {
        "timestamp": "2026-03-10T14:32:01Z",
        "event": "MCP_CALL",
        "tool": "mcp__nlm__nlm_ct_codes",
        "method": "npi-individuals",
        "input": {"terms": "1234567890", "maxList": 5},
        "result_summary": "NPI active, Rheumatology",
        "success": true,
        "latency_ms": 342
      },
      {
        "timestamp": "2026-03-10T14:32:01Z",
        "event": "MCP_CALL",
        "tool": "mcp__nlm__nlm_ct_codes",
        "method": "icd-10-cm",
        "input": {"terms": "M06.9", "maxList": 5},
        "result_summary": "Valid — Rheumatoid arthritis, unspecified",
        "success": true,
        "latency_ms": 287
      },
      {
        "timestamp": "2026-03-10T14:32:01Z",
        "event": "MCP_CALL",
        "tool": "mcp__medicare__medicare_info",
        "method": "search_formulary",
        "input": {"formulary_drug_name": "adalimumab"},
        "result_summary": "Tier 5, PA required, step therapy required",
        "success": true,
        "latency_ms": 456
      },
      {
        "timestamp": "2026-03-10T14:32:05Z",
        "event": "VALIDATION_COMPLETE",
        "detail": "Provider verified, ICD-10 valid (ON_LABEL), HCPCS valid"
      },
      {
        "timestamp": "2026-03-10T14:33:10Z",
        "event": "EVIDENCE_EXTRACTED",
        "detail": "Prior methotrexate trial (4mo, inadequate response), leflunomide contraindicated"
      },
      {
        "timestamp": "2026-03-10T14:34:00Z",
        "event": "RUBRIC_SCORED",
        "scores": {
          "provider_credentials": 100,
          "diagnosis_validity": 100,
          "formulary_compliance": 50,
          "step_therapy": 100,
          "clinical_evidence": 100,
          "cost_efficiency": 75
        },
        "confidence": 86.25
      },
      {
        "timestamp": "2026-03-10T14:34:01Z",
        "event": "DECISION_RENDERED",
        "decision": "APPROVE",
        "confidence": 86.25,
        "flags": ["BIOSIMILAR_AVAILABLE"],
        "auth_number": "PA-20260310-73821"
      },
      {
        "timestamp": "2026-03-10T14:35:45Z",
        "event": "NOTIFICATION_GENERATED",
        "letter_type": "approval",
        "output_file": "PA-20260310-73821_approval_letter.md"
      }
    ],
    "summary": {
      "total_mcp_calls": 5,
      "mcp_success_rate": "100%",
      "decision": "APPROVE",
      "confidence": 86.25,
      "review_duration_seconds": 225
    }
  }
}
```

**Key Parameters:**
- `events[].event`: one of `INTAKE_STARTED`, `MCP_CALL`, `VALIDATION_COMPLETE`, `EVIDENCE_EXTRACTED`, `RUBRIC_SCORED`, `DECISION_RENDERED`, `NOTIFICATION_GENERATED`, `HUMAN_OVERRIDE`
- `events[].latency_ms`: MCP call round-trip time for performance monitoring
- `summary`: rollup statistics for QA dashboards

**Expected Output:** A `audit_trail.json` file containing the complete chronological record of the PA review.

---

## Recipe 13: Human-in-the-Loop Override Mechanism

**Description:** When the automated rubric produces a PEND result (confidence 30-84%) or when policy requires human review (e.g., high-cost drugs, off-label requests), present the recommendation to a human reviewer and allow override with documented reason.

```
# Step 1: Generate the review summary for the human reviewer
review_summary:
  auth_number: PA-20260310-73821
  drug: adalimumab 40mg
  diagnosis: M06.9 (Rheumatoid arthritis, unspecified)
  automated_recommendation: PEND
  confidence: 62.5
  flags:
    - BIOSIMILAR_AVAILABLE
    - STEP_THERAPY_PARTIAL
  key_findings:
    - Provider verified (Rheumatology)
    - ICD-10 valid, ON_LABEL indication
    - Step therapy: methotrexate tried 4 months (meets 3-month minimum)
    - Step therapy: sulfasalazine tried 6 weeks only (policy requires 8 weeks)
    - Leflunomide contraindicated (hepatic impairment)
    - Biosimilar alternatives available at lower cost
  question_for_reviewer: >
    Sulfasalazine was tried for 6 weeks (policy requires 8 weeks minimum)
    but was discontinued due to GI intolerance. Leflunomide is contraindicated.
    Should the 6-week trial with documented intolerance satisfy step therapy?

# Step 2: Present to reviewer and capture override
human_decision:
  reviewer_id: "reviewer_jane_doe"
  override_action: "APPROVE"       # or "DENY" or "MAINTAIN_PEND"
  override_reason: >
    6-week sulfasalazine trial with documented GI intolerance is clinically
    sufficient. Requiring 8 full weeks when the patient cannot tolerate the
    drug is not medically appropriate. Leflunomide is contraindicated.
    Step therapy exception granted per clinical judgment.
  conditions:
    - "Approve for 6 months with re-authorization required"
    - "Recommend biosimilar adalimumab-atto if available at pharmacy"
  timestamp: "2026-03-10T15:10:00Z"

# Step 3: Update audit trail with override
audit_event:
  timestamp: "2026-03-10T15:10:00Z"
  event: "HUMAN_OVERRIDE"
  original_recommendation: "PEND"
  original_confidence: 62.5
  override_decision: "APPROVE"
  reviewer_id: "reviewer_jane_doe"
  override_reason: "Step therapy exception — documented intolerance at 6 weeks"
  conditions_added:
    - "6-month approval with re-auth"
    - "Biosimilar recommendation"

# Step 4: Re-generate notification with override decision
# Use Recipe 10 approval template with the override conditions added
```

**Key Parameters:**
- `override_action`: `"APPROVE"`, `"DENY"`, or `"MAINTAIN_PEND"` — the human reviewer's decision
- `override_reason`: free-text clinical justification (required for audit compliance)
- `conditions`: optional array of conditions the reviewer attaches to the decision
- `reviewer_id`: identifies the human reviewer for accountability

**Expected Output:** An updated `assessment.json` with the human override recorded, a new audit trail event, and a regenerated notification letter reflecting the override decision.
