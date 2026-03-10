---
name: risk-management-specialist
description: Risk management specialist for drugs and medical devices. Risk management plans (RMP/REMS), risk-benefit assessment, risk categorization (ICH E2E), post-market risk mitigation, ETASU elements, labeling risk communication. Use when user mentions risk management, RMP, REMS, ETASU, risk-benefit, risk mitigation, risk categorization, boxed warning, black box warning, Dear Doctor letter, or risk communication.
---

# Risk Management Specialist

Risk management planning, risk-benefit assessment, and risk mitigation strategies for drugs and medical devices. Integrates safety data from multiple sources to build comprehensive risk profiles.

## Report-First Workflow

1. **Create report file immediately**: `[drug_or_device]_risk_management_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Adverse event signal detection and pharmacovigilance analysis → use `pharmacovigilance-specialist`
- FDA regulatory pathway and submission strategy → use `fda-consultant`
- EU MDR compliance and CE marking → use `mdr-745-consultant`
- ISO 14971 within a QMS audit context → use `iso-13485-consultant`
- Clinical trial safety data extraction and analysis → use `clinical-trial-analyst`
- Drug-drug interaction assessment → use `drug-interaction-analyst`

## Cross-Reference: Other Skills

- **Adverse event data & signal detection** → use pharmacovigilance-specialist skill
- **FDA regulatory pathway** → use fda-consultant skill
- **EU regulatory context (RMP per MDR)** → use mdr-745-consultant skill
- **QMS risk management (ISO 14971)** → use iso-13485-consultant skill
- **Clinical trial safety data** → use clinical-trial-analyst skill

## Available MCP Tools

### `mcp__fda__fda_info` (FDA Safety Data)

| Call | What it does |
|------|-------------|
| `method: "lookup_drug", search_type: "label"` | Current labeling — boxed warnings, contraindications, warnings & precautions |
| `method: "lookup_drug", search_type: "adverse_events"` | FAERS adverse event reports |
| `method: "lookup_drug", search_type: "adverse_events", count: "patient.reaction.reactionmeddrapt.exact"` | Top adverse reactions by frequency |
| `method: "lookup_drug", search_type: "adverse_events", search_term: "drug+AND+serious:1"` | Serious events only |
| `method: "lookup_drug", search_type: "adverse_events", search_term: "drug+AND+seriousnessdeath:1"` | Fatal events only |
| `method: "lookup_drug", search_type: "recalls"` | Recall history |
| `method: "lookup_device", search_type: "device_adverse_events"` | Device MDR reports |
| `method: "lookup_device", search_type: "device_recalls"` | Device recalls |

### `mcp__drugbank__drugbank_info` (Drug Pharmacology)

| Method | What it does |
|--------|-------------|
| `search_by_name` | Find drug by name |
| `get_drug_details` | Full profile — mechanism, pharmacodynamics, toxicity, contraindications |
| `get_drug_interactions` | All drug-drug interactions |
| `search_by_target` | Drugs acting on same target (class effect risk) |
| `get_similar_drugs` | Pharmacologically similar drugs |
| `get_pathways` | Metabolic pathways (interaction risk) |
| `search_by_category` | Drugs in same therapeutic category |

### `mcp__ema__ema_info` (EU Risk Management)

| Method | What it does |
|--------|-------------|
| `get_referrals` | EU-wide safety reviews (Article 31/20 referrals) |
| `get_dhpcs` | Direct Healthcare Professional Communications |
| `get_psusas` | Periodic Safety Update Single Assessments |
| `get_post_auth_procedures` | Post-authorization label changes, variations |
| `search_medicines` | EU-approved medicines with authorization status |

### `mcp__pubmed__pubmed_articles` (Risk Literature)

| Method | What it does |
|--------|-------------|
| `search_keywords` | Quick literature search |
| `search_advanced` | Filtered search by journal, date range |
| `get_article_metadata` | Full article details |

### `mcp__cdc__cdc_health_data` (Population Risk Data)

| Method | What it does |
|--------|-------------|
| `get_places_data` | Local disease prevalence (county/ZIP level) |
| `get_overdose_surveillance` | Drug overdose monitoring |
| `get_nndss_surveillance` | Notifiable disease surveillance |

---

## REMS (Risk Evaluation and Mitigation Strategies)

### When REMS Is Required

FDA requires REMS when the benefits of a drug outweigh risks but additional risk mitigation beyond labeling is needed.

**REMS triggers:**
- New safety information suggesting serious risk
- Drug with known serious risks where labeling alone is insufficient
- Narrow therapeutic index drugs
- Drugs with abuse/misuse potential
- Drugs with serious teratogenic risks

### REMS Components (21 CFR 314.520)

| Component | Description | Example |
|-----------|-------------|---------|
| **Medication Guide** | Patient-facing risk information | Antidepressant suicidality warning |
| **Communication Plan** | HCP outreach (Dear Doctor letters) | New safety information dissemination |
| **ETASU** | Elements to Assure Safe Use | Restricted distribution, prescriber certification |
| **Implementation System** | Infrastructure for ETASU | Patient registries, pharmacy certification |
| **Timetable for Assessments** | Periodic REMS effectiveness evaluation | Typically 18mo, 3yr, 7yr |

### ETASU Elements

| Element | When Used | Example |
|---------|-----------|---------|
| **Prescriber certification** | Specialized knowledge needed | Isotretinoin (iPLEDGE) |
| **Pharmacy certification** | Distribution controls needed | Clozapine (Clozapine REMS) |
| **Patient enrollment** | Monitoring required | Thalidomide (THALOMID REMS) |
| **Dispensing conditions** | Safety checks at each fill | Pregnancy test before isotretinoin |
| **Patient monitoring** | Ongoing lab/clinical monitoring | Clozapine ANC monitoring |
| **Limited distribution** | Specialty pharmacy only | Certain oncology drugs |

### REMS Assessment Workflow

```
1. mcp__fda__fda_info(method: "lookup_drug", search_term: "drug_name", search_type: "label")
   → Check current labeling: boxed warnings, REMS section, medication guide

2. mcp__fda__fda_info(method: "lookup_drug", search_term: "drug_name+AND+serious:1", search_type: "adverse_events", count: "patient.reaction.reactionmeddrapt.exact", limit: 25)
   → Top serious adverse events

3. mcp__drugbank__drugbank_info(method: "get_drug_details", drugbank_id: "DBxxxxx")
   → Toxicity profile, contraindications, mechanism

4. mcp__drugbank__drugbank_info(method: "get_drug_interactions", drugbank_id: "DBxxxxx")
   → Interaction risks requiring mitigation

5. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "drug_name REMS risk management", num_results: 10)
   → Published REMS evaluations and effectiveness studies
```

---

## EU Risk Management Plan (RMP)

### RMP Structure (GVP Module V)

| Part | Content |
|------|---------|
| **Part I** | Product overview |
| **Part II** | Safety specification |
| **Part III** | Pharmacovigilance plan |
| **Part IV** | Plans for post-authorization efficacy studies |
| **Part V** | Risk minimization measures |
| **Part VI** | Summary of the RMP |
| **Part VII** | Annexes |

### Safety Specification (Part II)

#### Module SI: Epidemiology of Indications

Target population characteristics, disease incidence/prevalence, comorbidities.

#### Module SII: Non-Clinical Safety

Relevant non-clinical findings not yet confirmed clinically.

#### Module SIII: Clinical Trial Exposure

Patient exposure by age, sex, ethnicity, duration. Identify limitations.

#### Module SIV: Populations Not Studied

- Pediatric
- Elderly (>65, >75, >85)
- Pregnant/lactating
- Hepatic/renal impairment
- Immunocompromised
- Genetic polymorphisms

#### Module SV: Post-Authorization Experience

Cumulative post-market exposure estimates, spontaneous reports.

#### Module SVI: Additional EU Requirements

Potential for misuse, off-label use, medication errors.

#### Module SVII: Identified and Potential Risks

Per ICH E2E:
- **Identified risks**: Adverse reactions confirmed by adequate evidence
- **Potential risks**: Suspected but not confirmed — signals from non-clinical, pharmacological class, epidemiological
- **Missing information**: Gaps that represent safety concerns

#### Module SVIII: Summary of Safety Concerns

| Category | Description | Example |
|----------|-------------|---------|
| **Important identified risks** | Confirmed ADRs requiring risk minimization | Hepatotoxicity (confirmed by clinical data) |
| **Important potential risks** | Suspected risks needing further characterization | Cardiovascular events (signal from class effect) |
| **Missing information** | Knowledge gaps | Long-term use >2 years, pediatric safety |

### EU RMP Investigation Workflow

```
1. mcp__ema__ema_info(method: "search_medicines", active_substance: "drug_name")
   → EU authorization status, therapeutic area

2. mcp__ema__ema_info(method: "get_referrals", active_substance: "drug_name", safety: true)
   → EU safety referrals (Article 31/20 reviews)

3. mcp__ema__ema_info(method: "get_dhpcs", active_substance: "drug_name")
   → Safety communications — what risks were communicated to HCPs?

4. mcp__ema__ema_info(method: "get_psusas", active_substance: "drug_name")
   → PSUSA outcomes — were additional risk minimization measures required?

5. mcp__ema__ema_info(method: "get_post_auth_procedures", medicine_name: "trade_name")
   → Post-authorization variations (label changes from new safety data)
```

---

## Risk-Benefit Assessment Framework

### Structured Benefit-Risk Assessment (FDA)

| Dimension | Assessment |
|-----------|-----------|
| **Analysis of condition** | Severity, unmet need, available alternatives |
| **Current treatment options** | Efficacy and safety of existing therapies |
| **Benefit** | Clinical trial efficacy, magnitude of effect, durability |
| **Risk** | Type, severity, frequency, reversibility of adverse events |
| **Risk management** | Can risks be managed? REMS feasibility? |

### Quantitative Approaches

**Number Needed to Treat (NNT) vs Number Needed to Harm (NNH):**

```
NNT = 1 / (event_rate_control - event_rate_treatment)   [for benefit]
NNH = 1 / (event_rate_treatment - event_rate_control)   [for harm]

Benefit-Risk Ratio = NNH / NNT
  > 1 = benefit exceeds risk
  < 1 = risk exceeds benefit
```

**Incremental Net Health Benefit (INHB):**

```
INHB = (ΔBenefit / threshold) - ΔRisk
  Positive = favorable benefit-risk
  Negative = unfavorable benefit-risk
```

### Risk Categorization Matrix

| Severity / Frequency | Very Common (>10%) | Common (1-10%) | Uncommon (0.1-1%) | Rare (<0.1%) |
|---|---|---|---|---|
| **Life-threatening/Fatal** | Unacceptable | High | High | Medium |
| **Serious/Disabling** | High | High | Medium | Medium |
| **Moderate** | Medium | Medium | Low | Low |
| **Mild** | Low | Low | Low | Acceptable |

---

## Risk Communication

### Labeling Risk Hierarchy

| Level | Location | When Used |
|-------|----------|-----------|
| **Boxed Warning** | Top of prescribing information | Most serious risks — may cause death or serious injury |
| **Contraindications** | Section 4 | Conditions where risk clearly outweighs benefit |
| **Warnings & Precautions** | Section 5 | Clinically significant risks requiring monitoring |
| **Adverse Reactions** | Section 6 | All adverse events observed in clinical trials |
| **Medication Guide** | Patient handout | When REMS requires patient information |

### Risk Communication Workflow

```
1. mcp__fda__fda_info(method: "lookup_drug", search_term: "drug_name", search_type: "label")
   → Current labeling hierarchy (boxed warning, contraindications, W&P)

2. mcp__ema__ema_info(method: "get_dhpcs", active_substance: "drug_name")
   → EU safety communications (compare US vs EU risk messaging)

3. mcp__pubmed__pubmed_articles(method: "search_keywords", keywords: "drug_name risk communication patient understanding", num_results: 10)
   → Literature on patient/HCP understanding of the risk

4. mcp__cdc__cdc_health_data(method: "get_places_data", measure_id: "CONDITION", state: "XX")
   → Population-level disease prevalence to contextualize risk
```

---

## ISO 14971 Risk Management (Medical Devices)

### Risk Management Process

1. **Risk Analysis** — Identify hazards, estimate risk (severity × probability)
2. **Risk Evaluation** — Compare against acceptability criteria
3. **Risk Control** — Implement measures (inherent safety → protective → information)
4. **Residual Risk Evaluation** — Accept or further mitigate
5. **Risk-Benefit Analysis** — For residual risks exceeding criteria
6. **Production & Post-Production** — Monitor and update throughout lifecycle

### Risk Acceptability (ALARP Principle)

```
                    ┌─────────────────┐
                    │  UNACCEPTABLE   │  Risk must be reduced
                    │    REGION       │  regardless of benefit
                    ├─────────────────┤
                    │  ALARP REGION   │  As Low As Reasonably
                    │  (tolerable)    │  Practicable — reduce
                    │                 │  unless cost grossly
                    │                 │  disproportionate
                    ├─────────────────┤
                    │   BROADLY       │  No further risk
                    │   ACCEPTABLE    │  reduction needed
                    └─────────────────┘
```

### Risk Control Hierarchy

1. **Inherent safety by design** — Eliminate the hazard entirely
2. **Protective measures** — Guards, alarms, interlocks
3. **Information for safety** — Warnings, instructions, training

---

## Multi-Agent Workflow Examples

**"Build a risk management plan for our new drug"**
1. Risk Management Specialist → REMS assessment, risk categorization, labeling analysis, EU RMP structure
2. Pharmacovigilance Specialist → FAERS data, signal detection, drug interactions
3. Clinical Trial Analyst → Trial safety data, adverse event rates for NNH calculation
4. FDA Consultant → Regulatory requirements, submission pathway for REMS

**"Compare risk profiles of two competing drugs"**
1. Risk Management Specialist (Agent 1) → Full risk profile for Drug A
2. Risk Management Specialist (Agent 2) → Full risk profile for Drug B
3. Lead Agent → Head-to-head risk-benefit comparison

**"EU RMP update after new safety signal"**
1. Risk Management Specialist → RMP update assessment, risk communication plan
2. Pharmacovigilance Specialist → Signal characterization, FAERS + EudraVigilance data
3. MDR 745 Consultant → EU regulatory procedures, PRAC timeline

## Completeness Checklist

- [ ] Current labeling reviewed (boxed warnings, contraindications, warnings & precautions)
- [ ] FAERS adverse event data queried and top serious events identified
- [ ] Drug pharmacology profile retrieved (mechanism, toxicity, interactions)
- [ ] REMS status assessed — components, ETASU elements, and effectiveness
- [ ] EU RMP structure evaluated (safety specification, risk minimization measures)
- [ ] Risk-benefit assessment completed (NNT/NNH or qualitative framework)
- [ ] Risk categorization matrix populated (severity vs frequency)
- [ ] Risk communication hierarchy documented (labeling levels, DHPC history)
- [ ] ISO 14971 risk management process applied if medical device context
- [ ] Report file finalized with no `[Analyzing...]` placeholders remaining
