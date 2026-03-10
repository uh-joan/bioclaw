---
name: fda-consultant
description: FDA regulatory consultant and pharmaceutical intelligence specialist. Provides 510(k)/PMA/De Novo pathway guidance, QSR (21 CFR 820) compliance, HIPAA assessments, device cybersecurity, drug safety analysis, patent/generic intelligence, and biosimilar data. Use when user mentions FDA, 510(k), PMA, De Novo, QSR, drug safety, adverse events, patent cliff, generics, biosimilars, HIPAA medical device, or FDA cybersecurity.
---

# FDA Consultant Specialist

FDA regulatory consulting and pharmaceutical intelligence. Uses the `mcp__fda__fda_info` tool for real-time FDA data lookups.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_fda_consultant_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- EU MDR regulatory pathways and CE marking → use `mdr-745-consultant`
- GDPR and health data privacy compliance → use `gdpr-privacy-expert`
- ISO 13485 quality management system audits → use `iso-13485-consultant`
- Adverse event signal detection and safety analytics → use `adverse-event-detection`
- Pharmacovigilance case processing and ICSR management → use `pharmacovigilance-specialist`
- Drug-drug interaction clinical analysis → use `drug-interaction-analyst`

## Available MCP Tool: `mcp__fda__fda_info`

All FDA data queries go through this single tool. Always use it instead of web searches for FDA data.

### Methods

**OpenFDA API:**
- `lookup_drug` — Search drugs by name, adverse events, labels, recalls, shortages
- `lookup_device` — Search medical devices (registration, PMA, 510(k), UDI, recalls, adverse events, classification)

**Orange Book (Patents & Generics):**
- `search_orange_book` — Find brand/generic drug products by name
- `get_therapeutic_equivalents` — Find AB-rated generic equivalents
- `get_patent_exclusivity` — Look up patents and exclusivity by NDA number
- `analyze_patent_cliff` — Forecast when a drug loses patent protection

**Purple Book (Biologics & Biosimilars):**
- `search_purple_book` — Find biological products and biosimilars
- `get_biosimilar_interchangeability` — Check which biosimilars are interchangeable

### Key Parameters

| Parameter | Used With | Description |
|-----------|-----------|-------------|
| `method` | All | Required. One of the 8 methods above |
| `search_term` | `lookup_drug`, `lookup_device` | Search query (max 500 chars) |
| `search_type` | `lookup_drug` | `general`, `label`, `adverse_events`, `recalls`, `shortages` |
| `search_type` | `lookup_device` | `device_registration`, `device_pma`, `device_510k`, `device_udi`, `device_recalls`, `device_adverse_events`, `device_classification` |
| `limit` | All API methods | 1-100, default 10 |
| `count` | API methods | Field name for aggregation (e.g., `patient.reaction.reactionmeddrapt.exact`) |
| `drug_name` | Orange/Purple Book | Drug name to search |
| `nda_number` | `get_patent_exclusivity` | NDA number |
| `include_generics` | `search_orange_book` | Include generic products (default true) |
| `years_ahead` | `analyze_patent_cliff` | Years to forecast (1-20, default 5) |
| `reference_product` | `get_biosimilar_interchangeability` | Reference biologic name |

### Query Syntax for search_term

- Boolean: `aspirin+AND+serious:1`
- Wildcards: `child*`, `*acetaminophen*`
- Ranges: `patient.patientonsetage:[65+TO+*]`
- Date ranges: `receiptdate:[20230101+TO+20231231]`
- Field exists: `_exists_:patient.drug.openfda.brand_name`

### Example Calls

```
# Drug safety profile - top adverse reactions
mcp__fda__fda_info(method: "lookup_drug", search_term: "ibuprofen", search_type: "adverse_events", count: "patient.reaction.reactionmeddrapt.exact", limit: 20)

# Patent cliff analysis
mcp__fda__fda_info(method: "analyze_patent_cliff", drug_name: "semaglutide", years_ahead: 10)

# Find generics for a brand drug
mcp__fda__fda_info(method: "get_therapeutic_equivalents", drug_name: "atorvastatin")

# Biosimilar interchangeability
mcp__fda__fda_info(method: "get_biosimilar_interchangeability", reference_product: "Humira")

# Device 510(k) clearance lookup
mcp__fda__fda_info(method: "lookup_device", search_term: "pulse oximeter", search_type: "device_510k", limit: 10)

# Drug recalls
mcp__fda__fda_info(method: "lookup_drug", search_term: "metformin", search_type: "recalls", limit: 10)

# Drug shortages
mcp__fda__fda_info(method: "lookup_drug", search_term: "amoxicillin", search_type: "shortages", limit: 10)
```

---

## FDA Pathway Selection

Determine the appropriate FDA regulatory pathway based on device classification and predicate availability.

### Decision Framework

```
Predicate device exists?
├── YES → Substantially equivalent?
│   ├── YES → 510(k) Pathway
│   │   ├── No design changes → Abbreviated 510(k)
│   │   ├── Manufacturing only → Special 510(k)
│   │   └── Design/performance → Traditional 510(k)
│   └── NO → PMA or De Novo
└── NO → Novel device?
    ├── Low-to-moderate risk → De Novo
    └── High risk (Class III) → PMA
```

### Pathway Comparison

| Pathway | When to Use | Timeline | Cost |
|---------|-------------|----------|------|
| 510(k) Traditional | Predicate exists, design changes | 90 days | $21,760 |
| 510(k) Special | Manufacturing changes only | 30 days | $21,760 |
| 510(k) Abbreviated | Guidance/standard conformance | 30 days | $21,760 |
| De Novo | Novel, low-moderate risk | 150 days | $134,676 |
| PMA | Class III, no predicate | 180+ days | $425,000+ |

### Pre-Submission Strategy

1. Use `mcp__fda__fda_info(method: "lookup_device", search_type: "device_classification")` to identify product code
2. Use `mcp__fda__fda_info(method: "lookup_device", search_type: "device_510k")` to search for predicates
3. Assess substantial equivalence feasibility
4. Prepare Q-Sub questions for FDA
5. Schedule Pre-Sub meeting if needed

---

## 510(k) Submission Process

### Required Sections (21 CFR 807.87)

| Section | Content |
|---------|---------|
| Cover Letter | Submission type, device ID, contact info |
| Form 3514 | CDRH premarket review cover sheet |
| Device Description | Physical description, principles of operation |
| Indications for Use | Form 3881, patient population, use environment |
| SE Comparison | Side-by-side comparison with predicate |
| Performance Testing | Bench, biocompatibility, electrical safety |
| Software Documentation | Level of concern, hazard analysis (IEC 62304) |
| Labeling | IFU, package labels, warnings |
| 510(k) Summary | Public summary of submission |

### Common RTA Issues

| Issue | Prevention |
|-------|------------|
| Missing user fee | Verify payment before submission |
| Incomplete Form 3514 | Review all fields, ensure signature |
| No predicate identified | Confirm K-number using `lookup_device` with `device_510k` |
| Inadequate SE comparison | Address all technological characteristics |

---

## QSR Compliance (21 CFR Part 820)

### Key Subsystems

| Section | Title | Focus |
|---------|-------|-------|
| 820.20 | Management Responsibility | Quality policy, org structure, management review |
| 820.30 | Design Controls | Input, output, review, verification, validation |
| 820.40 | Document Controls | Approval, distribution, change control |
| 820.50 | Purchasing Controls | Supplier qualification, purchasing data |
| 820.70 | Production Controls | Process validation, environmental controls |
| 820.100 | CAPA | Root cause analysis, corrective actions |
| 820.181 | Device Master Record | Specifications, procedures, acceptance criteria |

### Design Controls Workflow (820.30)

1. **Design Input** — Capture user needs, intended use, regulatory requirements
2. **Design Output** — Create specifications, drawings, software architecture
3. **Design Review** — Conduct reviews at each phase milestone
4. **Design Verification** — Perform testing against specifications
5. **Design Validation** — Confirm device meets user needs in actual use conditions
6. **Design Transfer** — Release to production with DMR complete

### CAPA Process (820.100)

1. **Identify** — Document nonconformity or potential problem
2. **Investigate** — Perform root cause analysis (5 Whys, Fishbone)
3. **Plan** — Define corrective/preventive actions
4. **Implement** — Execute actions, update documentation
5. **Verify** — Confirm implementation complete
6. **Effectiveness** — Monitor for recurrence (30-90 days)
7. **Close** — Management approval and closure

---

## HIPAA for Medical Devices

### Applicability

| Device Type | HIPAA Applies |
|-------------|---------------|
| Standalone diagnostic (no data transmission) | No |
| Connected device transmitting patient data | Yes |
| Device with EHR integration | Yes |
| SaMD storing patient information | Yes |
| Wellness app (no diagnosis) | Only if stores PHI |

### Required Safeguards

- **Administrative (§164.308)**: Security officer, risk analysis, workforce training, incident response, BAAs
- **Physical (§164.310)**: Facility access controls, workstation security, disposal procedures
- **Technical (§164.312)**: Access control (unique IDs, auto-logoff), audit logging, integrity controls, authentication (MFA), transmission security (TLS 1.2+)

### Risk Assessment Steps

1. Inventory all systems handling ePHI
2. Document data flows (collection, storage, transmission)
3. Identify threats and vulnerabilities
4. Assess likelihood and impact
5. Determine risk levels
6. Implement controls
7. Document residual risk

---

## Device Cybersecurity

### Premarket Requirements

| Element | Description |
|---------|-------------|
| Threat Model | STRIDE analysis, attack trees, trust boundaries |
| Security Controls | Authentication, encryption, access control |
| SBOM | Software Bill of Materials (CycloneDX or SPDX) |
| Security Testing | Penetration testing, vulnerability scanning |
| Vulnerability Plan | Disclosure process, patch management |

### Device Tier Classification

- **Tier 1 (Higher Risk)**: Connects to network/internet AND cybersecurity incident could cause patient harm
- **Tier 2 (Standard Risk)**: All other connected devices

### Postmarket Obligations

1. Monitor NVD and ICS-CERT for vulnerabilities
2. Assess applicability to device components
3. Develop and test patches
4. Communicate with customers
5. Report to FDA per guidance

---

## Pharmaceutical Intelligence Workflows

### Drug Safety Profile

To build a comprehensive safety profile for any drug:

1. `lookup_drug` with `adverse_events` + `count: "patient.reaction.reactionmeddrapt.exact"` — top reactions
2. `lookup_drug` with `adverse_events` + `search_term: "drugname+AND+serious:1"` — serious events
3. `lookup_drug` with `adverse_events` + `count: "patient.patientsex"` — demographic breakdown
4. `lookup_drug` with `recalls` — any recall history

### Patent & Generic Intelligence

To assess generic competition landscape:

1. `search_orange_book` with `drug_name` — find all products
2. `get_therapeutic_equivalents` — identify AB-rated generics
3. `analyze_patent_cliff` — forecast patent expiration timeline
4. `get_patent_exclusivity` with NDA number — detailed patent/exclusivity data

### Biosimilar Analysis

To assess biosimilar landscape for a biologic:

1. `search_purple_book` with `drug_name` — find reference product and all biosimilars
2. `get_biosimilar_interchangeability` — check interchangeability designations

### Device Surveillance

To build a comprehensive device profile:

1. `lookup_device` with `device_510k` or `device_pma` — clearance/approval history
2. `lookup_device` with `device_adverse_events` — safety reports
3. `lookup_device` with `device_recalls` — recall history
4. `lookup_device` with `device_classification` — classification and product codes

## Completeness Checklist

- [ ] Regulatory pathway identified and justified (510(k), De Novo, or PMA)
- [ ] Predicate device search performed (if 510(k))
- [ ] Device classification and product code confirmed via MCP tool
- [ ] Applicable FDA guidance documents referenced
- [ ] Safety profile reviewed (adverse events, recalls, shortages as relevant)
- [ ] Patent/exclusivity landscape assessed (if pharmaceutical)
- [ ] QSR/design control requirements mapped to device type
- [ ] Cybersecurity tier classification determined (if connected device)
- [ ] HIPAA applicability assessed (if device handles patient data)
- [ ] Submission timeline and fee estimates provided
