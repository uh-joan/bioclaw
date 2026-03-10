---
name: capa-officer
description: CAPA (Corrective and Preventive Action) system manager for medical device and pharmaceutical QMS. Root cause analysis (5-Why, Fishbone, Fault Tree, FMEA), CAPA lifecycle management, effectiveness verification, FDA 21 CFR 820.100 compliance, common 483 observations. Use when user mentions CAPA, corrective action, preventive action, root cause analysis, RCA, 5-Why, Fishbone, Ishikawa, fault tree, FMEA, nonconformance, NCR, deviation, 483 observation, or effectiveness check.
---

# CAPA Officer

Corrective and Preventive Action system management per ISO 13485 (8.5.2/8.5.3) and FDA 21 CFR 820.100. Root cause analysis, CAPA lifecycle, effectiveness verification.

## Report-First Workflow

1. **Create report file immediately**: `capa_investigation_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- QMS standard requirements and clause interpretation → use `iso-13485-consultant`
- QMS audit findings and inspection readiness → use `qms-audit-expert`
- Device adverse events and MDR reporting → use `fda-consultant`
- Risk management file updates and FMEA → use `risk-management-specialist`
- EU MDR regulatory requirements → use `mdr-745-consultant`
- Post-market adverse event signal detection → use `adverse-event-detection`

## Available MCP Tools

### `mcp__fda__fda_info`

| Call | CAPA use |
|------|---------|
| `lookup_device`, `search_type: "device_recalls"` | Recall data — common CAPA triggers |
| `lookup_device`, `search_type: "device_adverse_events"` | MDR reports — CAPA triggers |
| `lookup_drug`, `search_type: "recalls"` | Drug recall history |
| `lookup_drug`, `search_type: "adverse_events"` | Drug ADR CAPA triggers |

### `mcp__pubmed__pubmed_articles`

| Method | CAPA use |
|--------|---------|
| `search_keywords` | Root cause investigation literature |
| `search_advanced` | Quality management best practices |

---

## CAPA Process Lifecycle

### Phase 1: Identification & Documentation

**CAPA Trigger Sources:**

| Source | Example | Urgency |
|--------|---------|---------|
| Customer complaint | Device malfunction report | High |
| Internal audit finding | Major nonconformity | High |
| External audit finding | Notified Body observation | Critical |
| FDA 483 observation | QSR deficiency | Critical |
| Adverse event / MDR | Patient injury | Critical |
| Recall | Field action | Critical |
| Process deviation | Out-of-spec result | Medium |
| Trend analysis | Rising complaint rate | Medium |
| Management review | KPI not meeting target | Low |
| Supplier nonconformance | Incoming inspection failure | Medium |

**Documentation Requirements:**
- CAPA ID (unique tracking number)
- Date initiated
- Source/trigger description
- Affected product(s) / process(es)
- Immediate containment actions taken
- Severity classification (Critical / Major / Minor)

### Phase 2: Investigation & Root Cause Analysis

#### RCA Method Selection Decision Tree

```
What type of problem?
├── Single event, clear failure mode
│   └── 5-Why Analysis
├── Complex event, multiple contributing factors
│   └── Fishbone (Ishikawa) Diagram
├── System/process failure with multiple pathways
│   └── Fault Tree Analysis (FTA)
├── Potential failure modes (preventive)
│   └── FMEA (Failure Mode and Effects Analysis)
├── Human error or procedural failure
│   └── Human Factors Analysis
└── Statistical process variation
    └── Statistical Process Control (SPC)
```

#### 5-Why Analysis

```
Problem: [State the problem clearly]

Why 1: Why did [problem] occur?
→ Because [cause 1]

Why 2: Why did [cause 1] occur?
→ Because [cause 2]

Why 3: Why did [cause 2] occur?
→ Because [cause 3]

Why 4: Why did [cause 3] occur?
→ Because [cause 4]

Why 5: Why did [cause 4] occur?
→ Because [ROOT CAUSE]

Verification: Does fixing [ROOT CAUSE] prevent [problem]? YES → proceed
```

**Common Pitfalls:**
- Stopping too early (symptom, not root cause)
- Jumping to "human error" (always ask WHY the error was possible)
- Single chain when multiple root causes exist (use branching 5-Why)

#### Fishbone (Ishikawa) — 6M Categories

| Category | Investigation Questions |
|----------|----------------------|
| **Man** (People) | Training adequate? Competence verified? Fatigue? Staffing levels? |
| **Machine** (Equipment) | Calibration current? Maintenance performed? Capability adequate? |
| **Method** (Process) | Procedure current? Procedure followed? Procedure adequate? |
| **Material** | Incoming inspection passed? Specification adequate? Supplier qualified? |
| **Measurement** | Test method validated? Equipment calibrated? Acceptance criteria clear? |
| **Mother Nature** (Environment) | Temperature/humidity controlled? ESD controls? Cleanroom class? |

#### Fault Tree Analysis (FTA)

```
Top Event: [Undesired outcome]
    ├── OR Gate: [Any one of these causes the top event]
    │   ├── AND Gate: [Both must occur]
    │   │   ├── Basic Event A
    │   │   └── Basic Event B
    │   └── Basic Event C
    └── OR Gate:
        ├── Basic Event D
        └── Undeveloped Event E (needs further analysis)
```

#### FMEA (Failure Mode and Effects Analysis)

| Column | Definition |
|--------|-----------|
| Process Step | The step being analyzed |
| Potential Failure Mode | How could it fail? |
| Potential Effect | What happens if it fails? |
| **Severity (S)** | 1-10 (10 = catastrophic) |
| Potential Cause | Why would it fail? |
| **Occurrence (O)** | 1-10 (10 = very frequent) |
| Current Controls | Detection/prevention methods |
| **Detection (D)** | 1-10 (10 = no detection capability) |
| **RPN** | S × O × D (1-1000) |
| Recommended Actions | For high RPN items |

**RPN Thresholds:**
- RPN ≥ 200: Immediate action required
- RPN 100-199: Action recommended
- RPN < 100: Monitor
- Any Severity = 9 or 10: Action required regardless of RPN

### Phase 3: CAPA Plan

| Element | Content |
|---------|---------|
| Root cause statement | Clear, verified root cause |
| Corrective action | Action to eliminate the root cause |
| Preventive action | Action to prevent recurrence in similar processes |
| Owner | Named individual responsible |
| Due date | Realistic completion date |
| Resources needed | Budget, equipment, training |
| Risk assessment update | How does this change the risk profile? |

### Phase 4: Implementation

- Execute actions per plan
- Update affected documents (procedures, work instructions, forms)
- Train affected personnel (with records)
- Notify regulatory if required (MDR vigilance, FDA reporting)
- Update risk management file if risk profile changed

### Phase 5: Effectiveness Verification

| Timeframe | Verification Activity |
|-----------|---------------------|
| **Immediate** (0-30 days) | Confirm action implemented, documents updated, training completed |
| **Short-term** (30-60 days) | Monitor for recurrence, check process metrics |
| **Long-term** (60-90 days) | Statistical confirmation of improvement, trend analysis |

**Effectiveness Criteria:**
- Problem has NOT recurred
- Process metrics improved or maintained
- No adverse effects from the change
- Similar issues in other processes also addressed (preventive)

### Phase 6: Closure

- Management approval of effectiveness evidence
- Final CAPA record completed
- Lessons learned documented
- Quality KPIs updated

---

## FDA 21 CFR 820.100 Requirements

| Requirement | Section |
|-------------|---------|
| Procedures for CAPA system | 820.100(a) |
| Analyze quality data to identify existing/potential causes | 820.100(a)(1) |
| Investigate cause of nonconformities | 820.100(a)(2) |
| Identify action needed | 820.100(a)(3) |
| Verify or validate corrective/preventive action | 820.100(a)(4) |
| Implement and record changes | 820.100(a)(5) |
| Ensure information submitted for management review | 820.100(a)(6) |
| Disseminate information to those responsible for quality | 820.100(a)(7) |

### Common FDA 483 Observations (CAPA-related)

1. **No procedure** — CAPA process not documented
2. **Inadequate investigation** — Root cause not identified (stopped at symptom)
3. **No effectiveness check** — Actions taken but never verified
4. **Timeliness** — CAPAs open for months/years with no progress
5. **Scope too narrow** — Corrective action for one product but not similar products
6. **Data not analyzed** — Quality data collected but never trended or reviewed
7. **Management review gap** — CAPA status not reported to management

---

## CAPA Metrics & KPIs

| Metric | Target | Red Flag |
|--------|--------|----------|
| **Average cycle time** | <60 days | >90 days |
| **On-time closure rate** | >85% | <70% |
| **First-time effectiveness** | >80% | <60% |
| **Recurrence rate** | <5% | >15% |
| **Overdue CAPAs** | 0 | Any >30 days past due |
| **Open CAPAs** | Trend stable/decreasing | Trend increasing |

---

## Multi-Agent Workflow Examples

**"We received a 483 observation about our CAPA system"**
1. CAPA Officer → Assess current CAPA procedure against 820.100, identify gaps, create compliant process
2. ISO 13485 Consultant → Map to ISO 13485 8.5.2/8.5.3 requirements
3. QMS Audit Expert → Prepare for follow-up inspection, mock audit

**"Customer complaint about device malfunction — initiate CAPA"**
1. CAPA Officer → Document, investigate (5-Why/Fishbone), plan corrective action
2. FDA Consultant → Check if MDR filing required, recall assessment
3. Risk Management Specialist → Update risk management file, FMEA

---

## Completeness Checklist

- [ ] CAPA trigger source identified and severity classified (Critical/Major/Minor)
- [ ] Immediate containment actions documented
- [ ] Root cause analysis method selected and completed (5-Why, Fishbone, FTA, or FMEA)
- [ ] Root cause verified (fixing it would prevent recurrence)
- [ ] Corrective and preventive actions defined with owners and due dates
- [ ] Affected documents, procedures, and training records updated
- [ ] Effectiveness verification plan established with timeframes (30/60/90 days)
- [ ] FDA 21 CFR 820.100 requirements addressed
- [ ] Management review notification included
- [ ] CAPA metrics tracked (cycle time, on-time closure, recurrence rate)
