---
name: prior-auth-reviewer
description: Prior authorization and medical necessity review specialist. PA request evaluation, CMS coverage policy lookup (NCDs, LCDs), ICD-10/CPT validation, formulary coverage, medical necessity determination, provider verification, authorization decisions. Use when user mentions prior authorization, prior auth, PA review, medical necessity, coverage determination, NCD, LCD, formulary exception, step therapy, quantity limits, payer review, or claims adjudication.
---

# Prior Authorization Reviewer

Automates payer-side review of prior authorization requests using CMS coverage policies, clinical coding validation, and evidence-based medical necessity assessment.

## Report-First Workflow

1. **Create report file immediately**: `[drug]_prior_auth_review_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Drug clinical evidence and trial data → use `clinical-trial-analyst`
- Drug safety profile and adverse event analysis → use `pharmacovigilance-specialist`
- FDA approval status and regulatory history → use `fda-consultant`
- Drug alternatives and therapeutic substitution → use `clinical-decision-support`
- Clinical guideline-based treatment recommendations → use `clinical-guidelines`
- Pharmacogenomic dosing adjustments → use `pharmacogenomics-specialist`

## Available MCP Tools

### `mcp__medicare__medicare_info`

| Method | PA review use |
|--------|-------------|
| `search_providers` | Verify prescriber credentials, specialty, practice location |
| `search_prescribers` | Part D prescriber verification, prescribing patterns |
| `search_formulary` | Part D formulary tier, prior auth requirements, step therapy, quantity limits |
| `search_spending` | Drug spending data (cost context for PA decisions) |
| `get_asp_pricing` | Part B drug ASP pricing (buy-and-bill drugs) |
| `compare_asp_pricing` | Compare pricing across therapeutic alternatives |
| `get_formulary_trend` | Track formulary coverage changes over time |
| `search_hospitals` | Hospital/facility verification |
| `get_hospital_star_rating` | Provider quality metrics |

### `mcp__medicaid__medicaid_info`

| Method | PA review use |
|--------|-------------|
| `get_nadac_pricing` | National average drug acquisition cost |
| `compare_drug_pricing` | Multi-drug cost comparison for alternatives |
| `search_state_formulary` | State Medicaid formulary coverage |
| `get_drug_utilization` | Prescription utilization trends by state |
| `get_drug_rebate_info` | Drug rebate program participation |
| `get_federal_upper_limits` | FUL pricing for generics |

### `mcp__nlm__nlm_ct_codes`

| Method | PA review use |
|--------|-------------|
| `icd-10-cm` | Validate diagnosis codes on PA request |
| `hcpcs-LII` | Validate procedure/equipment codes |
| `npi-individuals` | Provider NPI verification |
| `npi-organizations` | Facility NPI verification |
| `rx-terms` | Drug name/form/strength validation |
| `conditions` | Medical condition cross-references |

### `mcp__fda__fda_info`

| Call | PA review use |
|------|-------------|
| `lookup_drug`, `search_type: "label"` | FDA-approved indications (on-label vs off-label) |
| `lookup_drug`, `search_type: "shortages"` | Drug shortage status (expedite PA if in shortage) |
| `get_therapeutic_equivalents` | TE-rated generic alternatives |

### `mcp__drugbank__drugbank_info`

| Method | PA review use |
|--------|-------------|
| `search_by_indication` | Drugs indicated for the condition |
| `get_similar_drugs` | Therapeutic alternatives |
| `get_drug_interactions` | Interaction check for step therapy alternatives |

### `mcp__pubmed__pubmed_articles`

Literature evidence for off-label use requests.

---

## PA Review Workflow

### Step 1: Request Validation

```
1. Verify provider:
   mcp__nlm__nlm_ct_codes(method: "npi-individuals", terms: "provider_name_or_NPI", maxList: 5)
   → Confirm NPI is active and specialty is appropriate

2. Validate diagnosis:
   mcp__nlm__nlm_ct_codes(method: "icd-10-cm", terms: "diagnosis_code", maxList: 5)
   → Confirm ICD-10 code is valid and matches condition

3. Validate drug/procedure:
   mcp__nlm__nlm_ct_codes(method: "rx-terms", terms: "drug_name", maxList: 5)
   → Confirm drug name, strength, form

4. Check FDA approval:
   mcp__fda__fda_info(method: "lookup_drug", search_term: "drug_name", search_type: "label")
   → Is the requested indication FDA-approved?
```

### Step 2: Coverage Policy Check

```
1. Check formulary status:
   mcp__medicare__medicare_info(method: "search_formulary", formulary_drug_name: "drug_name")
   → Tier, prior auth requirement, step therapy, quantity limits

2. For Medicaid:
   mcp__medicaid__medicaid_info(method: "search_state_formulary", state: "XX", drug_name: "drug_name")
   → State formulary coverage status

3. Check coverage policies:
   - Is the drug on formulary for this indication?
   - Are there step therapy requirements?
   - Are there quantity limits?
   - Is the drug covered for this specific ICD-10 code?
```

### Step 3: Medical Necessity Assessment

```
1. Has the patient tried required step therapy?
   mcp__drugbank__drugbank_info(method: "search_by_indication", query: "condition", limit: 10)
   → Identify first-line alternatives the patient should have tried

2. Is there a clinical reason to skip step therapy?
   - Contraindication to first-line agent
   - Prior adverse reaction documented
   - Drug-drug interaction with current medications
   - Patient population exclusion (pregnancy, pediatric, renal impairment)

3. For off-label requests:
   mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "drug_name condition randomized controlled trial", num_results: 10)
   → Published evidence supporting off-label use
```

### Step 4: Cost Analysis

```
1. mcp__medicare__medicare_info(method: "search_spending", spending_drug_name: "drug_name", spending_type: "part_d")
   → Average cost per claim

2. mcp__medicaid__medicaid_info(method: "get_nadac_pricing", drug_name: "drug_name")
   → National average acquisition cost

3. mcp__fda__fda_info(method: "get_therapeutic_equivalents", search_term: "drug_name")
   → Generic alternatives available?

4. mcp__medicaid__medicaid_info(method: "compare_drug_pricing", drug_names: ["drug_a", "drug_b"])
   → Cost comparison with alternatives
```

### Step 5: Decision

| Decision | Criteria |
|----------|----------|
| **APPROVE** | On-label, on-formulary, step therapy met, medical necessity established |
| **APPROVE with conditions** | Quantity limit applied, duration limit, re-authorization required |
| **PEND** | Need additional information (clinical notes, prior treatment records) |
| **DENY — formulary** | Non-formulary, therapeutic alternative available |
| **DENY — step therapy** | Required step therapy not attempted, no clinical exception |
| **DENY — medical necessity** | Indication not supported by evidence |

---

## Decision Policy Framework

### Enforcement Levels

| Policy | Description | Application |
|--------|-------------|-------------|
| **STRICT** | Exact match to coverage criteria required | High-cost biologics, specialty drugs |
| **STANDARD** | Policy criteria with clinical judgment | Most formulary drugs |
| **LENIENT** | Approve if reasonable evidence exists | Palliative care, rare diseases, pediatric |

### Exception Criteria

| Exception Type | Documentation Required |
|---------------|----------------------|
| **Contraindication** | Clinical note documenting contraindication to step therapy drug |
| **Prior failure** | Documentation of trial duration and outcome |
| **Interaction** | Drug interaction report showing incompatibility |
| **Clinical urgency** | Provider attestation of time-sensitive need |
| **Age/weight** | Patient demographics outside step therapy drug's labeled population |

---

## Formulary Tier Structure

| Tier | Description | Cost-Sharing |
|------|-------------|-------------|
| **Tier 1** | Preferred generics | Lowest copay |
| **Tier 2** | Non-preferred generics | Low copay |
| **Tier 3** | Preferred brands | Moderate copay |
| **Tier 4** | Non-preferred brands | Higher copay |
| **Tier 5** | Specialty | Coinsurance (25-33%) |
| **Tier 6** | Biosimilars (some plans) | Variable |

### Step Therapy Logic

```
Standard step therapy sequence:
1. Patient must try Tier 1 generic for ≥30 days
2. If failure/intolerance, try Tier 2 generic for ≥30 days
3. If failure/intolerance, Tier 3 brand approved
4. Tier 4/5 requires documented failure of Tier 1-3 alternatives
```

---

## Shortage Handling

```
mcp__fda__fda_info(method: "lookup_drug", search_term: "drug_name", search_type: "shortages")
→ If drug in active shortage:
  - Expedite PA for therapeutic alternatives
  - Waive step therapy requirements
  - Consider quantity limit exceptions
```

---

## Multi-Agent Workflow Examples

**"Review PA request for adalimumab for rheumatoid arthritis"**
1. Prior Auth Reviewer → Formulary check, step therapy (methotrexate trial required?), coverage policy
2. Clinical Decision Support → Drug interactions, alternative biologics
3. Pharmacovigilance Specialist → Safety profile comparison of adalimumab vs alternatives

**"Formulary exception request for off-label drug use"**
1. Prior Auth Reviewer → Coverage policy, off-label evidence requirement
2. Clinical Trial Analyst → Published trial evidence supporting the off-label use
3. FDA Consultant → Compendia listing status, FDA guidance on off-label use

## Completeness Checklist

- [ ] Provider credentials verified via NPI lookup
- [ ] Diagnosis ICD-10 code validated and matched to requested drug indication
- [ ] Drug name, strength, and form confirmed via RxNorm
- [ ] FDA approval status checked (on-label vs off-label determination)
- [ ] Formulary status and tier verified (Medicare Part D or state Medicaid)
- [ ] Step therapy requirements assessed with prior treatment history reviewed
- [ ] Cost analysis performed with therapeutic alternatives compared
- [ ] Medical necessity determination documented with supporting evidence
- [ ] Drug shortage status checked for expedited processing if applicable
- [ ] PA decision rendered (Approve/Deny/Pend) with rationale documented
