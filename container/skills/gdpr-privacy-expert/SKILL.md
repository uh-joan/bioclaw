---
name: gdpr-privacy-expert
description: GDPR and health data privacy specialist. Data Protection Impact Assessments (DPIA), Article 9 health data lawful basis, data processing agreements, cross-border transfers (SCCs, adequacy decisions), data subject rights, breach notification, privacy by design for MedTech/pharma. Use when user mentions GDPR, data protection, DPIA, privacy, personal data, health data, data processing agreement, DPA, data breach, cross-border transfer, SCCs, consent management, right to erasure, data subject rights, or privacy impact assessment.
---

# GDPR & Data Privacy Expert

GDPR compliance for healthcare, MedTech, and pharmaceutical organizations. Data protection impact assessments, lawful basis analysis for health data, and cross-border transfer mechanisms.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_gdpr_privacy_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- EU MDR device regulatory requirements and CE marking → use `mdr-745-consultant`
- FDA cybersecurity and US data protection for devices → use `fda-consultant`
- ISO 13485 quality management system documentation → use `iso-13485-consultant`
- Clinical trial protocol design and endpoints → use `clinical-trial-protocol-designer`
- Risk management and FMEA for medical devices → use `risk-management-specialist`
- QMS audit preparation and CAPA processes → use `qms-audit-expert`

## Cross-Reference: Other Skills

- **EU MDR device data requirements** → use mdr-745-consultant skill
- **EU regulatory filings** → use mdr-745-consultant skill
- **ISO 27001 information security** → (use ISMS controls to implement GDPR technical measures)
- **FDA cybersecurity (US data protection)** → use fda-consultant skill
- **Clinical trial data protection** → use clinical-trial-analyst skill

## Available MCP Tools

### `mcp__ema__ema_info`

| Method | Privacy use |
|--------|-----------|
| `search_medicines` | Identify medicines with EU marketing authorization (determines EEA data scope) |
| `get_referrals` | EU safety reviews that may involve patient data processing |
| `get_post_auth_procedures` | Post-authorization obligations requiring data processing |

### `mcp__eu_filings__eu-filings`

| Method | Privacy use |
|--------|-----------|
| `search_companies` | Identify EU entities (data controllers/processors) |
| `get_company_by_lei` | Company legal entity identification |
| `get_country_companies` | Entities in specific EU member states |
| `search_uk_companies` | UK entities (UK GDPR applies separately post-Brexit) |

### `mcp__pubmed__pubmed_articles`

| Method | Privacy use |
|--------|-----------|
| `search_keywords` | GDPR healthcare literature, privacy impact studies |
| `search_advanced` | Data protection in clinical trials, health data regulation |

---

## GDPR Fundamentals for Healthcare

### Key Definitions

| Term | GDPR Definition | Healthcare Example |
|------|----------------|-------------------|
| **Personal data** | Any information relating to identified/identifiable person | Patient name, DOB, medical record number |
| **Special category data** | Genetic, biometric, health data (Article 9) | Diagnosis, lab results, genomic data, imaging |
| **Controller** | Determines purposes and means of processing | Hospital, pharma sponsor, device manufacturer |
| **Processor** | Processes on behalf of controller | CRO, cloud provider, data analytics firm |
| **Data subject** | The individual whose data is processed | Patient, clinical trial participant, HCP |
| **Processing** | Any operation on personal data | Collection, storage, analysis, sharing, deletion |

### Lawful Basis for Health Data (Article 9)

Standard Article 6 lawful basis is NOT sufficient for health data. Must also satisfy Article 9(2):

| Article 9(2) | Basis | Healthcare Application |
|-------------|-------|----------------------|
| **(a)** | Explicit consent | Clinical trial participation, optional research use |
| **(b)** | Employment law obligations | Occupational health processing |
| **(c)** | Vital interests (data subject unable to consent) | Emergency medical treatment |
| **(g)** | Substantial public interest (with member state law) | Public health surveillance, disease registries |
| **(h)** | Healthcare provision (by or under professional) | Treatment, diagnosis, health system management |
| **(i)** | Public health (with safeguards) | Pharmacovigilance, cross-border health threats |
| **(j)** | Scientific/historical research (with safeguards) | Clinical research, epidemiology, rare disease registries |

### Most Common Bases by Activity

| Activity | Article 6 Basis | Article 9 Basis |
|----------|----------------|-----------------|
| Patient treatment | Legitimate interest / contract | 9(2)(h) healthcare provision |
| Clinical trial | Legitimate interest | 9(2)(a) explicit consent + 9(2)(j) research |
| Pharmacovigilance | Legal obligation | 9(2)(i) public health |
| Post-market surveillance | Legal obligation | 9(2)(i) public health |
| Device registry | Legitimate interest | 9(2)(j) scientific research |
| Marketing to HCPs | Legitimate interest | N/A (no health data typically) |

---

## Data Protection Impact Assessment (DPIA)

### When DPIA is Required (Article 35)

| Trigger | Example |
|---------|---------|
| Systematic/extensive profiling with significant effects | AI-based diagnostic decisions |
| Large-scale processing of special category data | Hospital EHR system, clinical trial database |
| Systematic monitoring of public area | Patient monitoring devices |
| New technology | AI/ML-based medical devices, genomic analysis |
| Cross-border processing of health data | Multi-site clinical trials |

### DPIA Structure

| Section | Content |
|---------|---------|
| **1. Description** | Nature, scope, context, purpose of processing |
| **2. Necessity & proportionality** | Why this processing is needed, why less invasive alternatives won't work |
| **3. Risk assessment** | Risks to data subjects: likelihood × severity |
| **4. Risk mitigation** | Technical and organizational measures |
| **5. DPO opinion** | Data Protection Officer's assessment |
| **6. Consultation** | Data subject views (if appropriate) |

### Risk Assessment Matrix

| | Low Severity | Medium Severity | High Severity |
|---|---|---|---|
| **High Likelihood** | Medium Risk | High Risk | Very High Risk |
| **Medium Likelihood** | Low Risk | Medium Risk | High Risk |
| **Low Likelihood** | Low Risk | Low Risk | Medium Risk |

**Severity factors for health data:**
- Discrimination risk (genetic information, mental health)
- Physical harm risk (if data used for treatment decisions)
- Financial harm (insurance discrimination)
- Reputational harm (sensitive diagnoses)
- Loss of autonomy (profiling without consent)

---

## Cross-Border Data Transfers

### Transfer Mechanisms (Chapter V)

| Mechanism | When to Use | Status |
|-----------|------------|--------|
| **Adequacy decision** | Transfer to country with adequate protection | UK, Japan, South Korea, Israel, Canada (commercial), others |
| **Standard Contractual Clauses (SCCs)** | No adequacy decision, contract-based safeguard | Most common mechanism. Use EU Commission 2021 SCCs |
| **Binding Corporate Rules (BCRs)** | Intra-group transfers within multinational | Complex, requires DPA approval |
| **Derogations (Article 49)** | Explicit consent, contractual necessity, public interest | Case-by-case, not for systematic transfers |

### US Transfers (Post-Schrems II)

| Consideration | Assessment |
|--------------|------------|
| **EU-US Data Privacy Framework** | Adequacy decision adopted July 2023. Self-certification required. |
| **SCCs + supplementary measures** | Alternative if not DPF certified. Requires Transfer Impact Assessment (TIA). |
| **Supplementary measures** | Encryption in transit + at rest, pseudonymization, access controls, contractual restrictions on government access |

---

## Clinical Trial Data Protection

### ICH GCP + GDPR Alignment

| GCP Requirement | GDPR Requirement | Resolution |
|-----------------|------------------|------------|
| Informed consent | Consent as lawful basis (Article 9(2)(a)) | Combined ICF covering both |
| Source data verification | Right to access (Article 15) | Monitor access to pseudonymized data |
| Record retention (≥15-25 years) | Storage limitation principle | Retention justified by legal obligation |
| Pseudonymization | Data minimization + DPIA | Subject coding, key held by investigator |
| Adverse event reporting | Legal obligation + public health | Lawful basis under Article 9(2)(i) |

### Data Subject Rights in Clinical Trials

| Right | Applicability | Limitations |
|-------|--------------|-------------|
| **Access** (Art. 15) | Yes — participant can see their data | May provide coded data only |
| **Rectification** (Art. 16) | Yes — correct inaccurate data | Cannot alter source data (GCP violation) |
| **Erasure** (Art. 17) | Limited — research exemption (Art. 17(3)(d)) | Cannot erase if needed for research integrity |
| **Portability** (Art. 20) | Yes for consent-based processing | Structured, machine-readable format |
| **Withdrawal** (Art. 7(3)) | Yes — can withdraw consent | Data collected before withdrawal may be retained |
| **Objection** (Art. 21) | Limited for research (Art. 21(6)) | Can object unless processing necessary for public interest |

---

## Medical Device Data Protection (MDR + GDPR)

### Device Data Processing Categories

| Data Type | MDR Requirement | GDPR Consideration |
|-----------|----------------|-------------------|
| UDI data | EUDAMED registration | Personal data if linked to patient |
| Vigilance reports | Incident reporting | Pseudonymize before submission |
| PMCF data | Clinical follow-up | Consent or research lawful basis |
| Implant card data | Patient information | Right to access, portability |
| Complaint data | QMS requirement | Retention vs storage limitation |

---

## Breach Notification

### Timeline

| Action | Deadline | To Whom |
|--------|---------|---------|
| Internal assessment | Within hours of discovery | DPO, incident response team |
| DPA notification (Article 33) | 72 hours from awareness | Supervisory authority |
| Data subject notification (Article 34) | Without undue delay | Affected individuals (if high risk) |

### Assessment Criteria

```
Is it a personal data breach?
├── YES → Assess risk to data subjects
│   ├── LOW risk (encrypted data, no access possible)
│   │   └── Document internally, NO notification required
│   ├── RISK to rights and freedoms
│   │   └── Notify DPA within 72 hours
│   └── HIGH risk (unencrypted health data, large scale)
│       └── Notify DPA within 72 hours + notify data subjects
└── NO → Document, no action
```

---

## Multi-Agent Workflow Examples

**"We're launching a clinical trial in 5 EU countries — assess data protection"**
1. GDPR Privacy Expert → DPIA, lawful basis analysis, cross-border transfer assessment, ICF privacy language
2. Clinical Trial Analyst → Trial design context, data collection requirements
3. MDR 745 Consultant → EU regulatory data obligations

**"Our medical device collects patient data — GDPR compliance check"**
1. GDPR Privacy Expert → DPIA, consent mechanism, data retention policy, breach procedures
2. MDR 745 Consultant → MDR post-market data obligations
3. ISO 13485 Consultant → QMS data management procedures

## Completeness Checklist

- [ ] Lawful basis identified for both Article 6 and Article 9 (health data)
- [ ] DPIA necessity assessed against Article 35 triggers
- [ ] Data controller and processor roles clearly identified
- [ ] Cross-border transfer mechanism determined (adequacy, SCCs, BCRs, DPF)
- [ ] Data subject rights obligations mapped to processing activity
- [ ] Breach notification procedures and timelines documented
- [ ] Data retention periods defined with legal justification
- [ ] Technical and organizational security measures specified
- [ ] Data processing agreements (DPA) requirements outlined
- [ ] Privacy by design principles applied to system/process recommendations
