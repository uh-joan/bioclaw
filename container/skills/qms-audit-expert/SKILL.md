---
name: qms-audit-expert
description: QMS internal and external audit specialist. ISO 19011 audit methodology applied to ISO 13485, risk-based audit scheduling, audit program management, nonconformity classification, finding documentation, mock audit execution, certification audit preparation. Use when user mentions internal audit, external audit, audit finding, nonconformity, major finding, minor finding, audit checklist, audit trail, mock audit, ISO 19011, certification audit, surveillance audit, or audit preparation.
---

# QMS Audit Expert

Internal and external audit management per ISO 19011 applied to ISO 13485 QMS. Risk-based scheduling, audit execution, finding classification, and certification preparation.

## Report-First Workflow

1. **Create report file immediately**: `[scope]_audit_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## Cross-Reference: Other Skills

- **QMS standard requirements** → use iso-13485-consultant skill
- **CAPA from audit findings** → use capa-officer skill
- **FDA-specific audit (QSR/QMSR)** → use fda-consultant skill
- **EU MDR audit (Notified Body)** → use mdr-745-consultant skill

## When NOT to Use This Skill

- Interpreting specific ISO 13485 clause requirements → use `iso-13485-consultant`
- Root cause analysis and corrective action planning → use `capa-officer`
- FDA 21 CFR 820 compliance or QSR/QMSR gap analysis → use `fda-consultant`
- EU MDR conformity assessment or Notified Body expectations → use `mdr-745-consultant`
- Risk management file review (ISO 14971) → use `risk-management-specialist`
- GDPR or data privacy audit concerns → use `gdpr-privacy-expert`

## Available MCP Tools

### `mcp__fda__fda_info`

| Call | Audit use |
|------|----------|
| `lookup_device`, `search_type: "device_recalls"` | Pre-audit: check company recall history |
| `lookup_device`, `search_type: "device_adverse_events"` | Pre-audit: check MDR filing patterns |

### `mcp__pubmed__pubmed_articles`

| Method | Audit use |
|--------|----------|
| `search_keywords` | Quality management best practices, regulatory audit trends |

---

## Audit Program Management

### Risk-Based Audit Scheduling

| Risk Factor | Weight | Assessment |
|-------------|--------|-----------|
| **Product classification** | High | Class III/IIb = more frequent |
| **Previous audit findings** | High | Major NCRs = shorter interval |
| **Process complexity** | Medium | More complex = more frequent |
| **Complaint trends** | High | Rising complaints = trigger audit |
| **CAPA effectiveness** | Medium | Poor effectiveness = audit CAPA system |
| **Regulatory changes** | Medium | New regulations = gap audit |
| **Time since last audit** | Standard | Maximum 12 months between audits |

### Audit Frequency Matrix

| Risk Level | Internal Audit Interval | Coverage |
|------------|------------------------|----------|
| **High** | Every 6 months | Full scope |
| **Medium** | Every 9 months | Full scope with focus areas |
| **Low** | Every 12 months | Full scope (minimum per ISO 13485) |

### Annual Audit Schedule

All ISO 13485 clauses must be covered within 12 months. Recommended grouping:

| Quarter | Clauses | Focus Areas |
|---------|---------|-------------|
| Q1 | 4.1-4.2, 5.1-5.6 | QMS documentation, management responsibility |
| Q2 | 6.1-6.4, 7.1-7.4 | Resources, product realization, purchasing |
| Q3 | 7.5-7.6, 8.1-8.3 | Production, monitoring, nonconforming product |
| Q4 | 8.4-8.5, 7.3 | Data analysis, CAPA, design controls |

---

## Audit Execution

### Phase 1: Planning

| Element | Content |
|---------|---------|
| Audit scope | Clauses, processes, departments, products |
| Audit criteria | ISO 13485, applicable regulations (QSR, MDR), procedures |
| Audit team | Lead auditor + auditor(s), independence verified |
| Audit schedule | Date, time, auditee, clause, auditor assignment |
| Document review | Pre-audit review of procedures, prior audit reports, CAPAs |

### Auditor Independence Requirements

| Auditor May NOT Audit | Rationale |
|----------------------|-----------|
| Their own work | Self-review threat |
| Their own department | Familiarity threat |
| Processes they designed | Self-interest threat |
| Areas where they have CAPA ownership | Conflict of interest |

### Phase 2: Opening Meeting

- State audit scope, criteria, schedule
- Confirm logistics (escorts, lunch, confidentiality)
- Clarify finding classification definitions
- Confirm reporting timeline

### Phase 3: Evidence Collection

#### Audit Evidence Types

| Type | Examples | Strength |
|------|----------|----------|
| **Documents** | Procedures, work instructions, forms | Shows WHAT should happen |
| **Records** | Completed forms, logs, training records | Shows WHAT happened |
| **Observation** | Watching process execution | Shows WHAT actually happens |
| **Interview** | Asking personnel about their work | Shows understanding |

#### Audit Trail Technique

```
Start with a record (output) → trace back through:
1. Was the procedure followed?
2. Was the person trained?
3. Was the equipment calibrated?
4. Was the input material conforming?
5. Was the process validated?

Each link in the chain is an audit evidence point.
```

#### Sampling Strategy

| Population Size | Minimum Sample |
|----------------|---------------|
| 1-8 | All |
| 9-25 | 5-8 |
| 26-50 | 8-13 |
| 51-100 | 13-20 |
| 101-500 | 20-32 |
| 501+ | 32-50 |

### Phase 4: Finding Classification

| Classification | Definition | Examples |
|---------------|------------|---------|
| **Major Nonconformity** | Absence or total breakdown of a system requirement; creates doubt about product safety/performance | No CAPA procedure exists; design controls not implemented; management review never conducted |
| **Minor Nonconformity** | Single lapse or partial non-fulfillment that doesn't affect system effectiveness | One training record missing; one calibration overdue; single document not at latest revision |
| **Observation** | Area for improvement; technically compliant but could be better | Process works but is inefficient; procedure could be clearer |
| **Opportunity for Improvement (OFI)** | Suggestion for enhancement beyond requirements | Industry best practice not yet adopted |

#### Classification Decision Tree

```
Does the finding indicate:
├── Complete absence of a required element?
│   └── MAJOR
├── Systematic failure across multiple instances?
│   └── MAJOR
├── Direct risk to product safety/performance?
│   └── MAJOR
├── Single instance of non-fulfillment?
│   └── MINOR
├── Pattern of minor findings in same area?
│   └── Consider upgrading to MAJOR
├── Compliant but could improve?
│   └── OBSERVATION / OFI
└── Multiple minors in same clause?
    └── Consider MAJOR (systemic issue)
```

### Phase 5: Closing Meeting

- Present findings (classified, with objective evidence)
- Allow auditee to verify factual accuracy
- Agree on CAPA timeline expectations
- Confirm report distribution

### Phase 6: Audit Report

| Section | Content |
|---------|---------|
| Header | Audit ID, date, scope, team, auditees |
| Executive Summary | Overall assessment, number of findings by type |
| Findings | Each finding with: clause, requirement, evidence, classification |
| Positive Observations | What works well (important for morale) |
| Previous Audit Follow-up | Status of prior findings |
| Conclusions | Overall conformity statement, recommendation |
| Distribution | Report recipients |

---

## Certification Audit Preparation

### Stage 1 (Documentation Review)

Auditor reviews QMS documentation remotely before on-site visit.

**What they check:**
- [ ] Quality Manual complete and approved
- [ ] All required procedures documented
- [ ] Scope and exclusions justified
- [ ] Quality policy signed by top management
- [ ] Organization chart current

### Stage 2 (On-Site Assessment)

**Common focus areas by clause:**

| Clause | What Auditors Look For |
|--------|----------------------|
| 4.2 | Document control evidence — how do you manage revisions? |
| 5.6 | Management review minutes — all required inputs covered? |
| 7.3 | Design controls — can you trace from user need to verified output? |
| 7.4 | Supplier controls — qualification records, incoming inspection |
| 7.5.6 | Process validation — IQ/OQ/PQ records |
| 8.2.2 | Complaint handling — from receipt to investigation to resolution |
| 8.2.4 | Internal audit — program, records, independence |
| 8.5.2/3 | CAPA — root cause analysis, effectiveness checks |

### Mock Audit Protocol

```
1. Select 2-3 high-risk clauses
2. Prepare audit checklist (clause → requirement → question → evidence needed)
3. Conduct mock audit exactly like real audit:
   - Opening meeting (5 min)
   - Evidence collection (2-3 hours per clause)
   - Finding classification
   - Closing meeting (15 min)
4. Issue mock audit report
5. Initiate CAPAs for any findings
6. Verify CAPAs closed before real audit
```

---

## Surveillance vs. Re-certification

| Audit Type | Frequency | Scope |
|-----------|-----------|-------|
| **Initial certification** | Once | Full QMS, all clauses |
| **Surveillance** | Annually (2 per cycle) | Partial scope, rotates clauses |
| **Re-certification** | Every 3 years | Full QMS, all clauses |
| **Special/Unannounced** | As triggered | Specific concern areas |

---

## Multi-Agent Workflow Examples

**"Prepare for our ISO 13485 certification audit"**
1. QMS Audit Expert → Mock audit, finding classification, gap identification
2. ISO 13485 Consultant → Verify procedure completeness, Quality Manual review
3. CAPA Officer → Close any open CAPAs before audit

**"We received a major nonconformity — what now?"**
1. QMS Audit Expert → Classify finding, verify evidence, set CAPA timeline
2. CAPA Officer → Root cause analysis, corrective action plan, effectiveness verification
3. FDA Consultant → Assess regulatory impact if finding affects device safety

## Completeness Checklist

- [ ] Audit scope, criteria, and applicable standards defined
- [ ] Auditor independence verified (no self-review or familiarity threats)
- [ ] Risk-based audit schedule established with frequency justified
- [ ] Audit checklist prepared mapping clauses to requirements, questions, and evidence
- [ ] All findings classified correctly (Major, Minor, Observation, OFI) with objective evidence
- [ ] Previous audit findings reviewed and follow-up status documented
- [ ] CAPA timelines established for all nonconformities
- [ ] Audit report completed with all required sections (header, findings, positive observations, conclusions)
- [ ] Report file finalized with no `[Analyzing...]` placeholders remaining
