---
name: clinical-trial-protocol-designer
description: Clinical trial protocol design specialist. Full protocol generation following NIH/FDA templates, study design selection, population definition, endpoint specification, sample size calculation, statistical analysis plan, safety monitoring plan, regulatory pathway selection. Use when user mentions protocol design, study design, write a protocol, trial protocol, protocol template, NIH protocol, study synopsis, sample size, power calculation, SAP, DSMB charter, IND protocol, or study schema.
---

# Clinical Trial Protocol Designer

Generates complete clinical trial protocols following NIH/FDA templates. Distinct from clinical-trial-analyst (which analyzes existing trials) — this skill CREATES new protocols.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_clinical-trial-protocol-designer_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Analyzing existing trial data or pipeline intelligence → use `clinical-trial-analyst`
- Writing a clinical study report (CSR) or IB for a completed trial → use `clinical-report-writer`
- FDA regulatory strategy or submission pathway → use `fda-consultant`
- Drug safety profiling or FAERS queries → use `pharmacovigilance-specialist`
- Systematic literature review for protocol rationale → use `systematic-literature-reviewer`

## Cross-Reference: Other Skills

- **Analyze existing trials (not design)** → use clinical-trial-analyst skill
- **FDA submission pathway** → use fda-consultant skill
- **EU clinical investigation requirements** → use mdr-745-consultant skill
- **Safety monitoring methodology** → use pharmacovigilance-specialist skill
- **Drug/device background information** → use drug-target-analyst or fda-consultant skill
- **Literature for protocol rationale** → use systematic-literature-reviewer skill

## Available MCP Tools

### `mcp__ctgov__ct_gov_studies`

| Method | Protocol design use |
|--------|-------------------|
| `search` | Find precedent trials (same condition/intervention) for design decisions |
| `get` | Full trial details — borrow eligibility criteria, endpoints, sample size rationale |
| `suggest` | Autocomplete condition/intervention terminology |

### `mcp__fda__fda_info`

| Call | Protocol design use |
|------|-------------------|
| `lookup_drug`, `search_type: "label"` | Approved comparator labeling, dosing, safety |
| `lookup_drug`, `search_type: "adverse_events"` | Expected safety profile for monitoring plan |
| `lookup_device`, `search_type: "device_classification"` | Device class → regulatory pathway |

### `mcp__pubmed__pubmed_articles`

| Method | Protocol design use |
|--------|-------------------|
| `search_keywords` | Literature for scientific rationale, prior evidence |
| `search_advanced` | Endpoint validation literature, disease epidemiology |

### `mcp__drugbank__drugbank_info`

| Method | Protocol design use |
|--------|-------------------|
| `get_drug_details` | Pharmacology for dose selection rationale |
| `get_drug_interactions` | Concomitant medication exclusions |
| `search_by_indication` | Comparator/standard of care identification |

### `mcp__opentargets__opentargets_info`

| Method | Protocol design use |
|--------|-------------------|
| `search_diseases` | Disease epidemiology, subtypes |
| `get_disease_details` | Known therapeutics (standard of care for comparator arm) |

---

## Protocol Design Workflow

### Step 1: Precedent Research

```
1. mcp__ctgov__ct_gov_studies(method: "search",
     condition: "disease_name",
     intervention: "drug_class_or_name",
     phase: "PHASE3",
     status: "completed",
     sort: "@relevance",
     pageSize: 20)
   → Find similar completed trials

2. For top 3-5 relevant trials:
   mcp__ctgov__ct_gov_studies(method: "get", nctId: "NCTxxxxxxxx")
   → Extract: design, eligibility, endpoints, sample size, duration

3. mcp__pubmed__pubmed_articles(method: "search_keywords",
     keywords: "disease_name drug_name randomized controlled trial",
     num_results: 15)
   → Published results from precedent trials

4. Identify patterns:
   - Most common primary endpoint
   - Typical control arm (placebo vs active comparator)
   - Standard eligibility criteria
   - Usual study duration
   - Sample sizes and observed effect sizes
```

### Step 2: Study Design Selection

#### Design Decision Tree

```
What is the research question?
├── Superiority (is new treatment better?)
│   ├── Phase 1 → Open-label, dose-escalation (3+3 or CRM)
│   ├── Phase 2 → Randomized, controlled (1:1 or 2:1)
│   └── Phase 3 → Randomized, double-blind, controlled
├── Non-inferiority (is new treatment at least as good?)
│   └── Randomized, double-blind, active-controlled
│       Define non-inferiority margin (M1, M2)
├── Equivalence (are two treatments the same?)
│   └── Randomized, double-blind, two-sided test
└── Descriptive (what happens?)
    └── Single-arm, open-label (Phase 2 or natural history)
```

#### Randomization Methods

| Method | When to Use |
|--------|-------------|
| **Simple** | Large trials (>200 per arm) |
| **Block** | Small-medium trials, ensures balanced allocation |
| **Stratified** | Key prognostic factors that could confound (e.g., disease severity, center) |
| **Adaptive** | Response-adaptive, allocate more to better arm |
| **Minimization** | Multiple stratification factors, small trial |

#### Blinding

| Level | Who is Blinded | When |
|-------|---------------|------|
| **Open-label** | Nobody | Phase 1, surgical trials, device trials |
| **Single-blind** | Patient only | When assessor blinding is sufficient |
| **Double-blind** | Patient + investigator | Standard for Phase 2-3 drug trials |
| **Triple-blind** | Patient + investigator + analyst | Maximum bias protection |

### Step 3: Population Definition

#### Inclusion Criteria Template

```
1. Age: ≥18 years (or specify pediatric: ≥2 and <18)
2. Diagnosis: [ICD-10 code] confirmed by [method]
3. Disease severity/stage: [classification system and stage]
4. Prior treatment: [naive / failed ≥1 line / specific prior therapy]
5. Performance status: ECOG 0-1 (oncology) / NYHA I-II (cardiology)
6. Adequate organ function:
   - Hepatic: ALT/AST ≤3× ULN, bilirubin ≤1.5× ULN
   - Renal: eGFR ≥30 mL/min (or CrCl ≥30)
   - Hematologic: ANC ≥1500, platelets ≥100K, Hgb ≥9
7. Informed consent: Able to understand and willing to sign
8. Contraception: WOCBP must use effective contraception
```

#### Exclusion Criteria Template

```
1. Pregnancy or breastfeeding
2. Known hypersensitivity to study drug or excipients
3. Active infection requiring systemic treatment
4. Unstable cardiovascular disease within 6 months
5. Prior exposure to [specific drug class] within [washout period]
6. Concomitant medication: [CYP interactions, QTc-prolonging drugs]
7. Other active malignancy (oncology trials)
8. Participation in another interventional trial within [30 days]
9. Any condition that, in the investigator's opinion, would compromise safety
```

### Step 4: Endpoint Specification

#### Primary Endpoint Selection by Phase

| Phase | Typical Primary Endpoint | Assessment |
|-------|-------------------------|------------|
| **Phase 1** | MTD / RP2D (DLT rate <33%) | DLT window: usually cycle 1 (21-28 days) |
| **Phase 2** | ORR (RECIST 1.1), clinical response rate | Central review recommended |
| **Phase 3 (short survival)** | PFS (with OS as key secondary) | IRC-assessed, pre-specified OS interim |
| **Phase 3 (long survival)** | OS | Requires large sample, long follow-up |
| **Phase 3 (non-oncology)** | Disease-specific (HbA1c, blood pressure, event rate) | Clinically meaningful threshold |

#### Secondary Endpoints

```
Common secondary endpoints:
- Duration of response (DOR)
- Disease control rate (DCR = CR + PR + SD)
- Time to response (TTR)
- Patient-reported outcomes (PRO) — validated instrument required
- Quality of life (EQ-5D-5L, EORTC QLQ-C30)
- Biomarker endpoints (pharmacodynamic proof of concept)
- Safety (AE incidence, laboratory changes)
```

### Step 5: Sample Size Calculation

#### Survival Endpoint (Schoenfeld)

```
Required events = (Z_α + Z_β)² / (r × (1-r) × ln(HR)²)

Where:
  Z_α = 1.96 (two-sided α = 0.05) or 1.645 (one-sided α = 0.05)
  Z_β = 0.842 (power = 80%) or 1.282 (power = 90%)
  r = proportion randomized to experimental arm
  HR = target hazard ratio

Then:
  N = events / P(event)
  P(event) accounts for: accrual time, follow-up time, dropout rate

Example: HR=0.75, α=0.05 (two-sided), power=80%, 1:1 randomization
  events = (1.96 + 0.842)² / (0.5 × 0.5 × ln(0.75)²)
  events = 7.85 / (0.25 × 0.0827)
  events ≈ 380 events
  If P(event) = 70%, dropout = 10%: N ≈ 380 / 0.70 / 0.90 ≈ 604
```

#### Binary Endpoint

```
N per arm = (Z_α × √(2×p̄×(1-p̄)) + Z_β × √(p₁×(1-p₁) + p₂×(1-p₂)))² / (p₁ - p₂)²

Where:
  p₁ = expected control rate
  p₂ = expected treatment rate
  p̄ = (p₁ + p₂) / 2
```

#### Non-Inferiority Margin

```
M1 = entire treatment effect from superiority trial (placebo comparison)
M2 = acceptable fraction of M1 to retain (typically 50%)

Non-inferiority margin = M2

Requires: FDA Type B meeting discussion on margin selection
```

### Step 6: Statistical Analysis Plan (SAP)

| Section | Content |
|---------|---------|
| Analysis populations | ITT, mITT, per-protocol, safety |
| Primary analysis | Method, model, covariates, handling of missing data |
| Multiplicity | Hierarchical testing, gate-keeping, alpha allocation |
| Sensitivity analyses | Tipping point, MMRM vs LOCF, per-protocol |
| Subgroup analyses | Pre-specified (≤5), forest plot display |
| Interim analyses | Number, timing, alpha spending function |
| Missing data | Estimand framework (ICH E9(R1)), sensitivity analyses |

---

## NIH Protocol Template Sections

| Section | Title |
|---------|-------|
| 1 | Study Title |
| 2 | Study Synopsis (1-2 pages) |
| 3 | Schema (study design diagram) |
| 4 | Schedule of Activities |
| 5 | Study Objectives and Endpoints |
| 6 | Study Design |
| 7 | Study Population |
| 8 | Study Intervention |
| 9 | Study Assessments and Procedures |
| 10 | Statistical Considerations |
| 11 | Safety Monitoring |
| 12 | Data Management |
| 13 | Quality Assurance |
| 14 | Ethics |
| 15 | Study Administration |
| Appendix A | Informed Consent Template |
| Appendix B | Schedule of Events |
| Appendix C | Study Drug Information |

---

## Safety Monitoring Plan

### DSMB Requirements

| Trial Characteristic | DSMB Required? |
|---------------------|----------------|
| Phase 3 with mortality endpoint | Yes |
| Phase 3 with serious morbidity | Yes |
| Phase 2 with novel mechanism | Recommended |
| First-in-human | Recommended (or SRC) |
| Vulnerable population | Yes |
| Blinded trial with interim analyses | Yes |

### Stopping Rules

| Rule | When to Apply |
|------|-------------|
| **O'Brien-Fleming** (efficacy) | Conservative early, spend little alpha initially |
| **Futility** (non-binding) | If conditional power <20% at interim, consider stopping |
| **Safety** (OS harm) | If HR for OS favors control at any interim |
| **Toxicity** | If DLT rate exceeds threshold (e.g., >33% at MTD) |

---

## Multi-Agent Workflow Examples

**"Design a Phase 3 trial for our cancer drug"**
1. Clinical Trial Protocol Designer → Full protocol: design, population, endpoints, sample size, SAP
2. Clinical Trial Analyst → Competitive landscape, precedent trial designs, endpoint validation
3. FDA Consultant → IND requirements, regulatory pathway, FDA meeting strategy
4. Pharmacovigilance Specialist → Expected safety profile for monitoring plan

**"Write a study synopsis for investor presentation"**
1. Clinical Trial Protocol Designer → Synopsis (2-page structured summary)
2. Drug Target Analyst → Scientific rationale, mechanism of action
3. Clinical Trial Analyst → Market landscape, competitive trials

## Recipe Files

- **[protocol-recipes.md](protocol-recipes.md)** — Clinical trial protocol generation recipes. Includes waypoint-based state management, device vs drug regulatory pathway branching, ClinicalTrials.gov search integration, sample size calculations (t-test and z-test), dropout rate adjustment, sensitivity analysis scenarios, inclusion/exclusion criteria generation, Schedule of Activities table, FDA 12-section protocol structure, adverse event classification framework, and statistical analysis plan outline.

## Completeness Checklist

- [ ] Precedent trials searched and design decisions justified from existing evidence
- [ ] Study design selected with rationale (superiority, non-inferiority, equivalence, descriptive)
- [ ] Randomization method and blinding level specified
- [ ] Inclusion/exclusion criteria complete with organ function thresholds
- [ ] Primary endpoint defined with assessment method and timing
- [ ] Sample size calculation documented with all assumptions and inflation factors
- [ ] Statistical analysis plan includes analysis populations, multiplicity, and missing data handling
- [ ] Safety monitoring plan includes DSMB requirements and stopping rules
- [ ] Protocol follows NIH template structure with all required sections
- [ ] Comparator arm justified (placebo vs active) with ethical rationale
