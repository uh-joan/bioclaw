---
name: iso-13485-consultant
description: ISO 13485 QMS consultant for medical device manufacturers. Gap analysis, Quality Manual creation, procedure development, Medical Device Files, audit preparation. Use when user mentions ISO 13485, QMS, quality system, certification, FDA QMSR, EU MDR, quality manual, CAPA, design controls, medical device documentation, or audit prep.
---

# ISO 13485 Certification Consultant

QMS documentation and certification guidance for medical device manufacturers. Works alongside the fda-consultant skill — ISO 13485 covers the quality system, FDA consultant covers the regulatory submission pathway.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_iso-13485-consultant_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- FDA 510(k)/PMA/De Novo submission pathways → use `fda-consultant`
- EU MDR regulatory strategy and CE marking details → use `mdr-745-consultant`
- Risk management per ISO 14971 deep-dive → use `risk-management-specialist`
- QMS audit execution and findings management → use `qms-audit-expert`
- CAPA root cause analysis beyond procedure creation → use `capa-officer`
- GDPR and data privacy for connected devices → use `gdpr-privacy-expert`

## Cross-Reference: FDA Consultant Skill

- **QSR (21 CFR 820)** compliance details → use fda-consultant skill
- **510(k)/PMA/De Novo** submission pathways → use fda-consultant skill
- **Device classification & predicate search** → use `mcp__fda__fda_info(method: "lookup_device", search_type: "device_classification")`
- **Device recall/adverse event history** → use `mcp__fda__fda_info(method: "lookup_device", search_type: "device_recalls")`

## When to Use

- Starting ISO 13485 certification process
- Conducting gap analysis against ISO 13485
- Creating or updating QMS documentation
- Preparing for certification audit
- Transitioning from FDA QSR to QMSR (effective Feb 2, 2026)
- Harmonizing with EU MDR requirements
- Creating Medical Device Files

## Core Workflow

### 1. Assess Current State (Gap Analysis)

Work through documentation clause by clause:

1. Collect existing QMS documents from user
2. Check each of the 31 required procedures (see list below)
3. Mark status: Compliant / Partial / Non-compliant / N/A
4. Calculate compliance percentage per clause
5. Prioritize: Critical > High > Medium > Low
6. Create remediation plan with owners and dates

### 2. Understand Requirements

**Key clauses:**

| Clause | Title | Focus |
|--------|-------|-------|
| 4 | QMS | Documentation, risk management, software validation |
| 5 | Management | Quality policy, objectives, management review |
| 6 | Resources | Competence, training, infrastructure |
| 7 | Product Realization | Design, purchasing, production, traceability |
| 8 | Measurement | Audits, CAPA, complaints, data analysis |

### 3. Create Documentation (Priority Order)

**Phase 1 — Foundation (Critical):**
1. Quality Manual
2. Quality Policy and Objectives
3. Document Control procedure
4. Record Control procedure

**Phase 2 — Core Processes (High):**
5. Corrective and Preventive Action (CAPA)
6. Complaint Handling
7. Internal Audit
8. Management Review
9. Risk Management

**Phase 3 — Product Realization (High):**
10. Design and Development (if applicable)
11. Purchasing
12. Production and Service Provision
13. Control of Nonconforming Product

**Phase 4 — Supporting (Medium):**
14. Training and Competence
15. Calibration/Control of M&M Equipment
16. Process Validation
17. Product Identification and Traceability

**Phase 5 — Additional (Medium):**
18. Feedback and Post-Market Surveillance
19. Regulatory Reporting
20. Customer Communication
21. Data Analysis

**Phase 6 — Specialized (If Applicable):**
22. Installation
23. Servicing
24. Sterilization
25. Contamination Control

**Typical timeline:** 6-12 months for full implementation from scratch.

---

## The 31 Required Documented Procedures

1. Risk Management (4.1.5)
2. Software Validation (4.1.6)
3. Control of Documents (4.2.4)
4. Control of Records (4.2.5)
5. Internal Communication (5.5.3)
6. Management Review (5.6.1)
7. Human Resources/Competence (6.2)
8. Infrastructure Maintenance (6.3) — when applicable
9. Contamination Control (6.4.2) — when applicable
10. Customer Communication (7.2.3)
11. Design and Development (7.3.1-10) — when applicable
12. Purchasing (7.4.1)
13. Verification of Purchased Product (7.4.3)
14. Production Control (7.5.1)
15. Product Cleanliness (7.5.2) — when applicable
16. Installation (7.5.3) — when applicable
17. Servicing (7.5.4) — when applicable
18. Process Validation (7.5.6) — when applicable
19. Sterilization Validation (7.5.7) — when applicable
20. Product Identification (7.5.8)
21. Traceability (7.5.9)
22. Customer Property (7.5.10) — when applicable
23. Preservation of Product (7.5.11)
24. Control of M&M Equipment (7.6)
25. Feedback (8.2.1)
26. Complaint Handling (8.2.2)
27. Regulatory Reporting (8.2.3)
28. Internal Audit (8.2.4)
29. Process Monitoring (8.2.5)
30. Product Monitoring (8.2.6)
31. Control of Nonconforming Product (8.3)
32. Corrective Action (8.5.2)
33. Preventive Action (8.5.3)

---

## Quality Manual Structure

A compliant Quality Manual must contain:

- **Section 0:** Document control, approvals
- **Section 1:** Introduction, company overview
- **Section 2:** Scope and exclusions (must justify any exclusions)
- **Section 3:** Quality Policy (must be signed by top management)
- **Sections 4-8:** Address each ISO 13485 clause at policy level
- **Appendix A:** Procedure list (all 31+ procedures)
- **Appendix B:** Organization chart
- **Appendix C:** Process interaction map

### Exclusions

You CAN exclude (with justification):
- Design and Development — if contract manufacturer only
- Installation — if product requires no installation
- Servicing — if not offered
- Sterilization — if non-sterile product

Justification must be in the Quality Manual and explain why the exclusion does not affect the ability to provide safe, effective devices.

**Good:** "Clause 7.3 Design and Development is excluded. ABC Company operates as a contract manufacturer producing devices per complete design specifications provided by customers. All design activities are the customer's responsibility."

**Bad:** "We don't do design."

---

## Medical Device File (MDF)

Per ISO 13485 Clause 4.2.3, each device type/family needs an MDF containing:

1. General description and intended use
2. Label and instructions for use specifications
3. Product specifications
4. Manufacturing specifications
5. Purchasing, manufacturing, servicing procedures
6. Measuring and monitoring procedures
7. Installation requirements (if applicable)
8. Risk management file(s)
9. Verification and validation information
10. Design and development file(s)

The MDF replaces separate DHF/DMR/DHR under FDA QMSR harmonization.

---

## Design Controls Workflow (ISO 13485 Clause 7.3)

Same as FDA QSR 820.30 — these are now harmonized:

1. **Design Input** — User needs, intended use, regulatory requirements, risk analysis
2. **Design Output** — Specifications, drawings, software architecture
3. **Design Review** — Reviews at each phase milestone with records
4. **Design Verification** — Testing against specifications
5. **Design Validation** — Confirm device meets user needs in actual/simulated use
6. **Design Transfer** — Release to production with DMR/MDF complete
7. **Design Changes** — Controlled via change procedure, re-verify/validate as needed

---

## CAPA Process (Clause 8.5.2/8.5.3)

1. **Identify** — Document nonconformity, complaint, audit finding, or trend
2. **Investigate** — Root cause analysis (5 Whys, Fishbone, Fault Tree)
3. **Plan** — Define corrective/preventive actions with owner and deadline
4. **Implement** — Execute actions, update documentation
5. **Verify** — Confirm implementation complete and correct
6. **Effectiveness** — Monitor for recurrence (30-90 days typical)
7. **Close** — Management approval and closure

Key requirements:
- Must address root cause, not symptoms
- Must verify no adverse effects from changes
- Must document all steps
- CAPA system must feed into management review

---

## Key Regulatory Cross-References

### FDA QMSR (United States)
- 21 CFR Part 820 harmonized with ISO 13485 as of Feb 2, 2026
- Medical Device File replaces DHF/DMR/DHR
- Use fda-consultant skill for device classification and submission pathway

### EU MDR 2017/745
- Requires ISO 13485-certified QMS (or equivalent)
- Technical documentation requirements (Annex II/III)
- CE marking via Notified Body
- Post-market surveillance (PMS) plan required

### Canada (SOR/98-282)
- ISO 13485 certification required for MDEL
- Device classification system (Class I-IV)

---

## Audit Preparation Checklist

Before certification audit, verify:

- [ ] All 31 procedures documented and approved
- [ ] Quality Manual complete with all required content
- [ ] Medical Device Files complete for all products
- [ ] Internal audit completed with findings addressed
- [ ] Management review completed (minutes documented)
- [ ] Personnel trained on QMS procedures (training records)
- [ ] Records maintained per retention requirements
- [ ] CAPA system functional with effectiveness demonstrated
- [ ] Complaint system operational with records
- [ ] Document control system working (approval, distribution, revision)
- [ ] Risk management files complete per ISO 14971
- [ ] Supplier qualification records current

### Document Retention

- Design documents: Life of device + 5-10 years
- Manufacturing records: Life of device
- Complaint records: Life of device + 5-10 years
- CAPA records: 5-10 years minimum
- Calibration records: Retention period of equipment + 1 calibration cycle

Always comply with applicable regulatory requirements which may specify longer periods.

---

## Common Mistakes

1. **Copying ISO text verbatim** — Write YOUR processes in your own words
2. **Procedures too detailed** — Procedures define WHAT; detailed HOW goes in Work Instructions
3. **Documents in isolation** — Ensure cross-references and consistency across QMS
4. **Forgetting records** — Every procedure must specify what records to maintain
5. **Inadequate approval** — Quality Manual needs top management signature
6. **Poor exclusion justification** — Must explain why and demonstrate no impact on safety

---

## Two-Agent Workflow with FDA Consultant

For a complete medical device regulatory package, use both skills together:

**Scenario: "Help us get our device to market in the US"**

1. **FDA Consultant** → Determine device classification, identify predicate, choose submission pathway (510(k)/De Novo/PMA)
2. **ISO 13485 Consultant** → Build the QMS documentation required to support the submission

**Scenario: "We got a 483 observation about our CAPA system"**

1. **ISO 13485 Consultant** → Review CAPA procedure against 8.5.2/8.5.3, identify gaps, create compliant procedure
2. **FDA Consultant** → Check device recall/adverse event history via `mcp__fda__fda_info`, assess regulatory risk

**Scenario: "Transitioning from QSR to QMSR"**

1. **ISO 13485 Consultant** → Gap analysis against ISO 13485, create/update Quality Manual, consolidate DHF/DMR/DHR into MDF
2. **FDA Consultant** → Verify current device listings, check compliance status via FDA databases

## Completeness Checklist

- [ ] Gap analysis performed clause-by-clause (Clauses 4-8) with compliance status
- [ ] All applicable procedures identified from the 31 required procedures list
- [ ] Exclusions justified in writing with safety impact assessment
- [ ] Quality Manual structure verified (Sections 0-8, Appendices A-C)
- [ ] Medical Device File (MDF) contents confirmed for each device type/family
- [ ] CAPA process documented with root cause analysis methodology
- [ ] Design controls workflow mapped (if applicable)
- [ ] Audit preparation checklist completed with all items addressed
- [ ] Regulatory cross-references verified (FDA QMSR, EU MDR, Canada)
- [ ] Report file created with all sections populated (no `[Analyzing...]` remaining)
