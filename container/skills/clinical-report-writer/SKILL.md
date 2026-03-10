---
name: clinical-report-writer
description: Clinical and regulatory report writer. ICH-E3 clinical study reports (CSR), CARE case reports, CONSORT/STROBE/PRISMA compliance, SAE narratives, clinical overview (Module 2.5), clinical summary (Module 2.7), investigator brochure, DSUR. Use when user mentions clinical study report, CSR, case report, CARE guidelines, SAE narrative, CONSORT, STROBE, clinical overview, clinical summary, investigator brochure, IB, DSUR, CIOMS form, or CTD Module 2.
---

# Clinical Report Writer

Produces regulatory-grade clinical documents following ICH, CONSORT, STROBE, CARE, and PRISMA standards.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_clinical-report-writer_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Systematic evidence review or meta-analysis → use `systematic-literature-reviewer`
- Trial design, sample size, or statistical analysis plan → use `clinical-trial-analyst`
- Writing a new clinical trial protocol from scratch → use `clinical-trial-protocol-designer`
- FDA submission strategy or regulatory pathway → use `fda-consultant`
- Drug safety signal detection or FAERS analysis → use `pharmacovigilance-specialist`
- EU MDR/IVDR regulatory documents → use `mdr-745-consultant`

## Cross-Reference: Other Skills

- **Systematic evidence review** → use systematic-literature-reviewer skill
- **Trial design and statistics** → use clinical-trial-analyst skill
- **Safety data (FAERS, signals)** → use pharmacovigilance-specialist skill
- **FDA submission pathway** → use fda-consultant skill
- **EU regulatory documents** → use mdr-745-consultant skill

## Available MCP Tools

### `mcp__ctgov__ct_gov_studies`

| Method | Report use |
|--------|-----------|
| `search` | Find trial registrations for reference |
| `get` | Full trial record — protocol, results, demographics, endpoints |

### `mcp__pubmed__pubmed_articles`

| Method | Report use |
|--------|-----------|
| `search_keywords` | Literature for background/discussion sections |
| `search_advanced` | Filtered evidence search |
| `get_article_metadata` | Citation details for reference lists |

### `mcp__fda__fda_info`

| Call | Report use |
|------|-----------|
| `lookup_drug`, `search_type: "label"` | Approved labeling for comparator/background |
| `lookup_drug`, `search_type: "adverse_events"` | Post-market safety context |

### `mcp__drugbank__drugbank_info`

| Method | Report use |
|--------|-----------|
| `get_drug_details` | Pharmacology background for IB, CSR |
| `get_drug_interactions` | Safety context |

### `mcp__biorxiv__biorxiv_info`

| Method | Report use |
|--------|-----------|
| `search_preprints` | Emerging evidence for discussion |

---

## ICH-E3 Clinical Study Report Structure

### Full CSR Sections

| Section | Title | Content |
|---------|-------|---------|
| **1** | Title Page | Study ID, phase, sponsor, dates, report date |
| **2** | Synopsis | 3-5 page summary (structured abstract) |
| **3** | Table of Contents | |
| **4** | List of Abbreviations | |
| **5** | Ethics | IRB/IEC approval, informed consent, GCP compliance |
| **6** | Investigators and Study Administrative Structure | Site list, CROs, DMC composition |
| **7** | Introduction | Disease background, rationale, study objectives |
| **8** | Study Objectives | Primary, secondary, exploratory |
| **9** | Investigational Plan | |
| 9.1 | Overall Study Design | Design diagram, randomization, blinding |
| 9.2 | Discussion of Study Design | Justification for design choices |
| 9.3 | Selection of Study Population | Inclusion/exclusion criteria |
| 9.4 | Treatments | Drug, dose, schedule, comparator, rescue medication |
| 9.5 | Efficacy and Safety Variables | Endpoints, assessment schedule |
| 9.6 | Data Quality Assurance | Monitoring, source verification, audit |
| 9.7 | Statistical Methods | Primary analysis, multiplicity, missing data, sensitivity |
| **10** | Study Patients | |
| 10.1 | Disposition | CONSORT flow diagram |
| 10.2 | Protocol Deviations | Major/minor, by site |
| 10.3 | Demographics and Baseline | |
| **11** | Efficacy Evaluation | |
| 11.1 | Primary Endpoint | Full analysis with CI, p-value, effect size |
| 11.2 | Secondary Endpoints | Pre-specified hierarchy |
| 11.3 | Subgroup Analyses | Forest plots, pre-specified only |
| 11.4 | Exploratory Analyses | Clearly labeled as hypothesis-generating |
| **12** | Safety Evaluation | |
| 12.1 | Adverse Events | Overall AE summary, SOC/PT tables |
| 12.2 | Deaths | Narratives for all deaths |
| 12.3 | Serious Adverse Events | Listing and narratives |
| 12.4 | Discontinuations due to AEs | |
| 12.5 | Clinical Laboratory Evaluations | Shift tables, clinically notable values |
| 12.6 | Vital Signs | |
| 12.7 | ECG | QTc analysis if applicable |
| **13** | Discussion and Overall Conclusions | |
| **14** | Tables, Figures, and Graphs | In-text and appendix |
| **15** | References | |
| **16** | Appendices | Protocol, SAP, CRF, individual patient data |

---

## Reporting Guidelines

### CONSORT 2010 (RCTs)

| Item | Required Content | Common Deficiency |
|------|-----------------|-------------------|
| **1a** | Title identifies as RCT | Missing "randomized" |
| **2a** | Scientific background and rationale | Too brief |
| **3a** | Pre-specified primary and secondary outcomes | Outcome switching |
| **6a** | Randomization: sequence generation | Not described |
| **7a** | Allocation concealment mechanism | Omitted |
| **8a** | Who generated sequence, enrolled, assigned | Unclear roles |
| **11a** | Blinding: who was blinded | Incomplete description |
| **13a** | CONSORT flow diagram | Missing or incomplete |
| **17a** | For each outcome: results with effect size and CI | p-value without CI |
| **22** | Where full protocol can be accessed | Missing |

### STROBE (Observational)

| Category | Key Items |
|----------|-----------|
| **Title** | Indicate study design (cohort, case-control, cross-sectional) |
| **Methods** | Setting, participants, variables, data sources, bias handling, sample size, statistical methods |
| **Results** | Participant flow, descriptive data, outcome data, main results, other analyses |
| **Discussion** | Key findings, limitations, interpretation, generalizability |

### CARE (Case Reports)

| Section | Content |
|---------|---------|
| **Title** | Diagnosis/intervention in title, "case report" identified |
| **Keywords** | 2-5 keywords |
| **Introduction** | Brief background, why this case is reportable |
| **Patient Information** | Demographics, main symptoms, medical history, comorbidities |
| **Clinical Findings** | Physical exam, relevant findings |
| **Timeline** | Dates of key events (onset, diagnosis, treatment, outcome) |
| **Diagnostic Assessment** | Tests performed, diagnostic challenges, differential diagnosis |
| **Therapeutic Intervention** | Type, dosing, duration, changes |
| **Follow-up and Outcomes** | Clinician-assessed and patient-reported, adherence, adverse events |
| **Discussion** | Strengths/limitations, relevant literature, rationale for conclusions |
| **Patient Perspective** | If available and consented |

---

## SAE Narrative Template

```
CASE IDENTIFICATION
Study: [Protocol Number]
Subject: [Subject ID]
Site: [Site Number / Investigator]
Date of Event: [DD-MMM-YYYY]
Date Reported: [DD-MMM-YYYY]

DEMOGRAPHICS
Age: [X] years | Sex: [M/F] | Race: [Race] | Weight: [X] kg

EVENT DESCRIPTION
[Subject ID], a [age]-year-old [sex] enrolled in [study name], experienced
[SAE term] on [date], [X] days after starting study treatment.

RELEVANT MEDICAL HISTORY
- [Condition 1] (onset: [date])
- [Condition 2]
- [Relevant concomitant medications]

STUDY TREATMENT
Drug: [Study drug], Dose: [X mg], Route: [PO/IV], Start: [date]
Last dose before event: [date], Duration of exposure: [X days]

EVENT DETAILS
[Detailed clinical description: onset, symptoms, progression, workup,
findings, treatment of the event, clinical course, resolution/outcome]

Laboratory data:
- [Relevant labs with dates and values]
- [Baseline → event → resolution values]

OUTCOME
[Recovered / Recovered with sequelae / Not recovered / Fatal / Unknown]
Resolution date: [DD-MMM-YYYY]

CAUSALITY ASSESSMENT
Investigator assessment: [Related / Not related / Possibly related]
Sponsor assessment: [Related / Not related / Possibly related]
Rationale: [Temporal relationship, mechanism, dechallenge, rechallenge,
alternative explanations]

REGULATORY CLASSIFICATION
Serious criteria met: [Death / Life-threatening / Hospitalization /
Disability / Congenital anomaly / Other medically important]
Expected/Unexpected per IB: [Expected / Unexpected]
Reportable: [Yes — 15-day / Yes — 7-day / No]
```

---

## CTD Module 2 Documents

### Module 2.5: Clinical Overview

| Section | Content |
|---------|---------|
| 2.5.1 | Product Development Rationale |
| 2.5.2 | Overview of Biopharmaceutics |
| 2.5.3 | Overview of Clinical Pharmacology |
| 2.5.4 | Overview of Efficacy |
| 2.5.5 | Overview of Safety |
| 2.5.6 | Benefits and Risks Conclusions |

### Module 2.7: Clinical Summary

| Section | Content |
|---------|---------|
| 2.7.1 | Summary of Biopharmaceutic Studies |
| 2.7.2 | Summary of Clinical Pharmacology Studies |
| 2.7.3 | Summary of Clinical Efficacy |
| 2.7.4 | Summary of Clinical Safety |
| 2.7.5 | Literature References |
| 2.7.6 | Individual Study Synopses |

### Investigator Brochure (IB)

| Section | Content |
|---------|---------|
| 1 | Summary |
| 2 | Introduction |
| 3 | Physical, Chemical, Pharmaceutical Properties |
| 4 | Nonclinical Studies |
| 5 | Effects in Humans (PK, PD, safety, efficacy) |
| 6 | Summary of Data and Guidance for the Investigator |
| 7 | References |

Update frequency: At least annually or when significant new information arises.

---

## DSUR (Development Safety Update Report)

Annual safety report for drugs under investigation (ICH E2F).

| Section | Content |
|---------|---------|
| 1 | Introduction |
| 2 | Worldwide Marketing Authorization Status |
| 3 | Actions Taken for Safety Reasons |
| 4 | Changes to Reference Safety Information |
| 5 | Ongoing and Completed Clinical Trials |
| 6 | Estimated Cumulative Exposure |
| 7 | Data in Line Listings and Summary Tabulations |
| 8-15 | Significant Findings (clinical trials, observational, non-clinical, literature, other) |
| 16 | Overall Safety Assessment |
| 17 | Summary of Important Risks |
| 18 | Benefit-Risk Analysis |
| 19 | Conclusions |

---

## Multi-Agent Workflow Examples

**"Write a CSR for our Phase 3 trial"**
1. Clinical Report Writer → ICH-E3 structure, SAE narratives, CONSORT flow
2. Clinical Trial Analyst → Statistical analysis, endpoint interpretation, subgroup analyses
3. Systematic Literature Reviewer → Background/discussion literature review

**"Prepare an IB update with new safety data"**
1. Clinical Report Writer → IB structure, Section 5 update with new human data
2. Pharmacovigilance Specialist → FAERS data, new safety signals to incorporate
3. Chemical Safety & Toxicology → Updated nonclinical toxicology summary

## Completeness Checklist

- [ ] Document type identified (CSR, IB, DSUR, case report, clinical overview/summary)
- [ ] Applicable reporting guideline selected (ICH-E3, CONSORT, STROBE, CARE, PRISMA)
- [ ] All required sections per guideline included with content
- [ ] SAE narratives follow structured template (case ID, demographics, event, causality)
- [ ] References cited with PubMed IDs or ClinicalTrials.gov NCT numbers
- [ ] Safety data tables include incidence rates, SOC/PT coding, and severity grading
- [ ] CONSORT flow diagram or patient disposition included for RCTs
- [ ] Regulatory cross-references verified (CTD module numbers, ICH section numbers)
- [ ] No placeholder text or `[Analyzing...]` markers remain in final document
- [ ] Report reviewed for internal consistency (numbers match across synopsis, body, and tables)
