---
name: mdr-745-consultant
description: EU Medical Device Regulation (MDR 2017/745) specialist. Device classification (Annex VIII), technical documentation (Annex II/III), clinical evidence (CER, PMCF), EUDAMED, UDI, Notified Body assessment. Use when user mentions MDR, EU MDR, CE marking, Notified Body, EUDAMED, clinical evaluation report, CER, PMCF, Annex VIII, EU medical device, or European market.
---

# EU MDR 2017/745 Consultant

EU Medical Device Regulation specialist for market access in Europe. Uses `mcp__ema__ema_info` for EU regulatory data. Works alongside fda-consultant (US market) and iso-13485-consultant (QMS).

## Report-First Workflow

1. **Create report file immediately**: `[topic]_mdr-745-consultant_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- US FDA device submissions (510(k), De Novo, PMA) -> use `fda-consultant`
- Quality management system documentation (ISO 13485) -> use `iso-13485-consultant`
- Clinical trial design and endpoint analysis -> use `clinical-trial-analyst`
- Risk management file and ISO 14971 compliance -> use `risk-management-specialist`
- Drug safety and pharmacovigilance reporting -> use `pharmacovigilance-specialist`
- GDPR and data privacy for health data -> use `gdpr-privacy-expert`

## Cross-Reference: Other Skills

- **US market submission (510(k)/PMA)** → use fda-consultant skill
- **QMS documentation (ISO 13485)** → use iso-13485-consultant skill
- **Clinical trial data** → use clinical-trial-analyst skill
- **Drug safety / pharmacovigilance** → use pharmacovigilance-specialist skill

## Available MCP Tool: `mcp__ema__ema_info`

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_medicines` | Search EU-approved medicines | `active_substance`, `therapeutic_area`, `status`, `orphan`, `biosimilar`, `limit` |
| `get_medicine_by_name` | Get medicine by trade name | `name` |
| `get_orphan_designations` | Rare disease designations | `therapeutic_area`, `active_substance`, `year`, `status`, `limit` |
| `get_supply_shortages` | EU shortage tracking | `active_substance`, `medicine_name`, `status`, `limit` |
| `get_referrals` | EU-wide safety reviews | `safety`, `active_substance`, `status`, `year`, `limit` |
| `get_post_auth_procedures` | Label updates, extensions | `medicine_name`, `limit` |
| `get_dhpcs` | Safety communications to HCPs | `medicine_name`, `active_substance`, `year`, `limit` |
| `get_psusas` | Periodic Safety Update Reports | `active_substance`, `regulatory_outcome`, `limit` |
| `get_pips` | Paediatric Investigation Plans | `active_substance`, `therapeutic_area`, `year`, `limit` |
| `search_epar_documents` | EPAR document search | `medicine_name`, `document_type`, `language`, `limit` |
| `search_all_documents` | Full EMA document repository | `search_term`, `document_type`, `category`, `limit` |

---

## Device Classification (Annex VIII)

### Classification Rules

**Non-Invasive Devices:**
- **Rule 1**: Devices not touching patient or contacting only intact skin → Class I
- **Rule 2**: Channelling/storing for administration → Class depends on substance (IIa/IIb)
- **Rule 3**: Modifying biological/chemical composition of body fluids → IIa-III
- **Rule 4**: Contact with injured skin → I (mechanical barrier) to IIb (chronic wounds)

**Invasive Devices:**
- **Rule 5**: Invasive via body orifice, not surgical → I (transient) to IIa/IIb (longer term)
- **Rule 6**: Surgically invasive, transient → IIa (general) to III (direct heart/CNS contact)
- **Rule 7**: Surgically invasive, short-term → IIa to III
- **Rule 8**: Implantable/long-term surgically invasive → III (with exceptions)

**Active Devices:**
- **Rule 9**: Active therapeutic → IIa (general) to IIb (potentially hazardous)
- **Rule 10**: Active diagnostic → IIa to IIb
- **Rule 11**: Software → I to III (based on MDCG 2019-11 decision)
- **Rule 12**: Active delivering medicinal products → IIa to IIb
- **Rule 13**: All other active devices → I

**Special Rules:**
- **Rule 14**: Devices incorporating medicinal substance → III
- **Rule 15**: Contraceptive/STI prevention devices → IIb to III
- **Rule 16**: Disinfecting/sterilizing devices → IIa to IIb
- **Rule 17**: Devices utilizing non-viable tissues/cells → III
- **Rule 18**: Blood bags → IIb
- **Rule 19**: Devices incorporating nanomaterials → IIa to III (by exposure risk)
- **Rule 20**: Invasive devices for substance intake via body orifice → I to IIa
- **Rule 21**: Substances introduced into the body → III
- **Rule 22**: Active therapeutic with integrated diagnostic (companion diagnostics) → III

### Software Classification (MDCG 2019-11)

```
Does it provide information used to make decisions?
├── YES → What decisions?
│   ├── Diagnosis or treatment of individual patients →
│   │   ├── May cause death or irreversible deterioration → Class III
│   │   ├── May cause serious deterioration → Class IIb
│   │   └── Other situations → Class IIa
│   └── Not for individual diagnosis/treatment → Class IIa
└── NO → Class I (or not a medical device)
```

### Quick Classification Table

| Device Type | Typical Class | Route |
|-------------|--------------|-------|
| Bandages, wheelchair | I | Self-declaration |
| Surgical gloves, hearing aid | I (sterile/measuring) | Annex IX Ch I/III |
| Infusion pump, ultrasound | IIa | Annex IX |
| Ventilator, X-ray | IIb | Annex IX |
| Hip implant, pacemaker, AI diagnostic | III | Annex IX + Annex X |

---

## Technical Documentation (Annex II/III)

### Annex II: Full Technical Documentation

**Required for ALL devices:**

1. **Device Description and Specification**
   - Intended purpose, indications, contraindications
   - Operating principles, materials
   - All variants and accessories
   - UDI-DI assignment

2. **Information from Manufacturer**
   - Label, IFU in all required languages
   - Implant card (if applicable)

3. **Design and Manufacturing**
   - Design stages with verification/validation at each
   - Complete manufacturing process
   - Facility information
   - Qualified suppliers

4. **General Safety and Performance Requirements (GSPR)**
   - Compliance matrix for ALL applicable GSPRs (Annex I)
   - Standards and common specifications used
   - Justification for inapplicable GSPRs

5. **Benefit-Risk Analysis and Risk Management**
   - ISO 14971 risk management file
   - Benefit-risk determination
   - Residual risk acceptability

6. **Product Verification and Validation**
   - Pre-clinical testing (bench, biocompatibility, electrical safety)
   - Software verification and validation (IEC 62304)
   - Clinical evaluation (see below)

### Annex III: Post-Market Surveillance Documentation

1. **PMS Plan** — Systematic collection and analysis of field data
2. **PMS Report** (Class I) or **PSUR** (Class IIa/IIb/III) — Periodic safety reporting
3. **PMCF Plan and Report** — Ongoing clinical data collection
4. **Trend Reporting** — Statistical trend analysis of incidents
5. **Serious Incident Reporting** — Via EUDAMED within regulatory timelines

---

## Clinical Evidence

### Evidence Hierarchy

1. **Systematic reviews / Meta-analyses** (highest)
2. **Randomized controlled trials**
3. **Prospective cohort studies**
4. **Retrospective studies**
5. **Case series / Case reports**
6. **Expert opinion / Bench data** (lowest)

### Clinical Evaluation Report (CER) Structure

1. **Scope** — Device, intended purpose, target population
2. **Clinical Background** — State of the art, current knowledge
3. **Literature Review** — Systematic search, appraisal, analysis
   - Use `mcp__pubmed__pubmed_articles` for literature search
4. **Clinical Investigation Data** — Own clinical trials
   - Use `mcp__ctgov__ct_gov_studies` for trial data
5. **Post-Market Data** — PMCF, vigilance, complaints
6. **Overall Conclusions** — Benefit-risk, conformity with GSPRs
7. **Date and Signature** — Qualified evaluator

### When Clinical Investigation is Required

- **Class III** and **Class IIb** implantables: Clinical investigation generally expected unless equivalent device + sufficient literature
- **Novel technology**: Where no clinical data exists
- **New intended purpose**: Extending claims beyond existing evidence
- **Equivalence route**: Must demonstrate equivalence per 3 criteria (clinical, technical, biological) AND have a contract with equivalent device manufacturer

### PMCF (Post-Market Clinical Follow-up)

Required for ALL classes. Methods:
- PMCF studies (prospective data collection)
- Registries
- Patient surveys
- Literature review (ongoing)

For Class III and implantables: PMCF summary of safety and clinical performance (SSCP) published in EUDAMED.

---

## EUDAMED and UDI

### EUDAMED Modules

1. **Actor Registration** — Manufacturer, authorized rep, importer
2. **UDI/Device Registration** — Device information, UDI-DI
3. **Notified Body and Certificates** — Certificate data
4. **Clinical Investigations** — Study registration
5. **Vigilance** — Incident reporting
6. **Market Surveillance** — Authority actions

### UDI Requirements

- **UDI-DI**: Device identifier (model/version) — assigned by issuing entity (GS1, HIBCC, ICCBBA)
- **UDI-PI**: Production identifier (lot, serial, expiry)
- **Basic UDI-DI**: Key for EUDAMED (device family level)
- Must be on label + packaging, and in EUDAMED
- Class III implantables: UDI on device itself

---

## Conformity Assessment Routes

| Class | Route | Notified Body? |
|-------|-------|----------------|
| I | Self-declaration (Annex IV) | No |
| I (sterile) | Annex IX Ch I + III | Yes (sterile aspects) |
| I (measuring) | Annex IX Ch I + III | Yes (metrological aspects) |
| I (reusable surgical) | Annex IX Ch I + III | Yes (reprocessing) |
| IIa | Annex IX (QMS) or Annex XI Part A | Yes |
| IIb | Annex IX or Annex X + Annex XI Part A | Yes |
| III | Annex IX + Annex X (type examination) | Yes + Annex X |

---

## Key Timelines

| Milestone | Date |
|-----------|------|
| MDR entered into force | May 25, 2017 |
| MDR application date | May 26, 2021 |
| Extended transition (MDD certificates) | Dec 31, 2027 (Class III/IIb implantable) / Dec 31, 2028 (others) |
| FDA QMSR harmonization with ISO 13485 | Feb 2, 2026 |

---

## Multi-Agent Workflows

**"Get our device CE marked and FDA cleared"**
1. MDR 745 Consultant → classify device per Annex VIII, identify conformity assessment route, outline technical documentation
2. FDA Consultant → classify device per FDA, identify predicate, recommend 510(k)/De Novo/PMA
3. ISO 13485 Consultant → QMS documentation supporting both markets

**"Prepare clinical evidence for our Class IIb implant"**
1. MDR 745 Consultant → CER structure, GSPR compliance matrix, equivalence assessment
2. Clinical Trial Analyst → search existing trials, literature evidence, design PMCF study

**"EU safety review — our device has adverse events"**
1. MDR 745 Consultant → check EMA referrals, DHPCs, PSUSA obligations, EUDAMED vigilance reporting
2. Pharmacovigilance Specialist → cross-reference FDA adverse events, drug interaction data
3. FDA Consultant → check US recall history via `mcp__fda__fda_info`

## Completeness Checklist

- [ ] Device classified per Annex VIII with applicable rule(s) cited
- [ ] Conformity assessment route identified (Annex IX, X, XI) with Notified Body requirement
- [ ] GSPR compliance matrix addressed for all applicable requirements (Annex I)
- [ ] Clinical evidence strategy defined (CER, equivalence, or clinical investigation)
- [ ] UDI-DI and Basic UDI-DI assignments documented
- [ ] EUDAMED registration requirements listed per applicable modules
- [ ] Post-market surveillance plan outlined (PMS, PSUR, PMCF)
- [ ] Transition timeline assessed against extended deadlines (2027/2028)
- [ ] Software classification evaluated per MDCG 2019-11 if applicable
