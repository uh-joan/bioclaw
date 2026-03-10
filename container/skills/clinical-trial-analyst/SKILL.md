---
name: clinical-trial-analyst
description: Clinical trial design and analysis specialist. Survival analysis, endpoint selection, sample size calculation, interim analyses, adaptive designs, FDA/EMA regulatory considerations. Use when user mentions clinical trials, trial design, survival analysis, Kaplan-Meier, hazard ratio, PFS, OS, sample size, interim analysis, adaptive design, DSMB, or trial pipeline.
---

# Clinical Trial Analyst

Clinical trial design, statistical analysis, and pipeline intelligence. Uses `mcp__ctgov__ct_gov_studies` for trial data and `mcp__pubmed__pubmed_articles` for literature evidence.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_clinical-trial-analyst_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Writing a full clinical trial protocol from scratch → use `clinical-trial-protocol-designer`
- Drafting regulatory documents (CSR, IB, DSUR) → use `clinical-report-writer`
- FDA submission strategy or regulatory pathway advice → use `fda-consultant`
- Post-market safety signal detection or FAERS analysis → use `pharmacovigilance-specialist`
- Comprehensive single-drug monographs → use `drug-research`
- Competitive landscape and patent/exclusivity analysis → use `competitive-intelligence`

## Cross-Reference: Other Skills

- **FDA regulatory pathway** for the drug/device under study → use fda-consultant skill
- **EU regulatory context** → use mdr-745-consultant skill
- **Drug safety signals** that may affect trial design → use pharmacovigilance-specialist skill
- **Device classification** for device trials → use `mcp__fda__fda_info(method: "lookup_device")`

## Available MCP Tools

### `mcp__ctgov__ct_gov_studies`

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search` | Search clinical trials | `condition`, `intervention`, `phase`, `status`, `location`, `lead`, `ages`, `studyType`, `allocation`, `masking`, `purpose`, `start`, `primComp`, `sort`, `pageSize` |
| `get` | Get full trial details by NCT ID | `nctId` |
| `suggest` | Autocomplete terms | `input`, `dictionary` (Condition/InterventionName/LeadSponsorName) |

**Search tips:**
- Use OR operator: `condition: "breast cancer OR lung cancer"`
- Date ranges: `start: "2023-01-01_2025-12-31"`
- Complex queries: `complexQuery: "AREA[InterventionName]pembrolizumab AND AREA[Phase]PHASE3"`
- Sort by: `@relevance`, `LastUpdatePostDate`, `EnrollmentCount`

### `mcp__pubmed__pubmed_articles`

| Method | What it does | Key parameters |
|--------|-------------|----------------|
| `search_keywords` | Quick keyword search | `keywords`, `num_results` |
| `search_advanced` | Filtered search | `term`, `title`, `author`, `journal`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Full article details | `pmid` |
| `get_article_pdf` | PDF download link | `pmid` |

---

## Endpoint Selection

### FDA-Recommended Hierarchy (Oncology)

1. **Overall Survival (OS)** — Gold standard, direct clinical benefit. Requires longer follow-up. Can be confounded by crossover.
2. **Progression-Free Survival (PFS)** — Earlier readout. Surrogacy for OS varies by disease. Subject to assessment bias.
3. **Objective Response Rate (ORR)** — Accelerated approval pathway. Requires confirmatory trial with OS/PFS.
4. **Patient-Reported Outcomes (PRO)** — Increasingly important. Must be validated instrument.

### Endpoint by Phase

- **Phase 1**: Maximum Tolerated Dose (DLT rate < 33%)
- **Phase 2**: ORR (CR + PR per RECIST 1.1), assessed every 8 weeks
- **Phase 3 (survival > 24mo, no crossover)**: OS
- **Phase 3 (shorter survival or crossover expected)**: PFS

### Critical: OS as Safety Endpoint (FDA 2024 Guidance)

When PFS is primary, OS MUST be pre-specified as a safety endpoint with:
- Planned interim analysis timepoints
- Stopping boundaries for harm (O'Brien-Fleming)
- Independent DMC review

---

## Sample Size Calculation

### Survival Endpoint (Schoenfeld Method)

Required events = (Z_alpha + Z_beta)^2 / (r * (1-r) * log(HR)^2)

Where:
- Z_alpha = 1.96 (two-sided alpha=0.05) or 2.33 (one-sided alpha=0.01)
- Z_beta = 0.84 (power=0.80) or 1.28 (power=0.90)
- r = allocation ratio / (1 + allocation ratio)
- HR = target hazard ratio

Then convert events to sample size using expected event probability (accounting for enrollment time, follow-up, and dropout).

### Binary Endpoint (Response Rate)

Use normal approximation or Fisher's exact. Effect size = (p_treatment - p_control) / pooled_SD.

### Key Considerations

- Always inflate for dropout (typically 10-15%)
- Consider crossover when estimating event rates
- For adaptive designs, plan sample size re-estimation at interim

---

## Interim Analysis

### Alpha Spending Functions

| Method | Behavior | When to use |
|--------|----------|-------------|
| **O'Brien-Fleming** | Conservative early, liberal late | Standard for Phase 3 |
| **Pocock** | Constant boundary | When early stopping equally important |
| **Lan-DeMets** | Flexible analysis timing | When interim timing uncertain |

### DMC Responsibilities (per FDA Guidance)

1. Review unblinded efficacy and safety data
2. Monitor OS as safety endpoint even when not primary
3. Recommend stopping for overwhelming efficacy, futility, or safety (OS detriment)
4. Protect trial integrity
5. Maintain confidentiality

---

## Adaptive Designs

| Type | Description | Preserves Type I Error? |
|------|-------------|------------------------|
| Sample size re-estimation | Adjust N based on observed variance | Yes (if blinded) |
| Seamless Phase 2/3 | Dose selection → confirmatory in one trial | Yes (with proper alpha control) |
| Biomarker enrichment | Restrict to biomarker+ if all-comer fails | Yes (with pre-specified rules) |
| Response-adaptive randomization | Shift allocation toward better arm | Requires careful design |

---

## Critical Pitfalls (Sharp Edges)

### 1. PFS-OS Discordance (CRITICAL)

PFS gains do NOT always translate to OS benefit — can even show harm.

**Examples (FDA 2024):**
- PI3K inhibitors: PFS improvement but OS detriment in hematologic malignancies
- PARP inhibitors: PFS benefit but potential OS harm in ovarian cancer

**Why:** Treatment toxicity catches up, post-progression therapies differ, PFS gain may be purely radiographic.

**Solution:** Pre-specify OS as safety endpoint. Plan crossover handling (RPSFT, IPCW). Ensure adequate OS follow-up before publication.

### 2. Post-Hoc Subgroup Fishing (CRITICAL)

Testing enough subgroups guarantees false positives. With 20 subgroups at alpha=0.05, expect 1 false positive.

**Solution:** Pre-specify max 3-5 subgroups in SAP. Adjust for multiplicity (Bonferroni/Holm). Report ALL subgroups via forest plot.

### 3. Proportional Hazards Violation (HIGH)

When survival curves cross, a single HR is meaningless.

**Common in:** Immunotherapy (delayed separation of curves).

**Solution:** Test PH assumption (Schoenfeld residuals). If violated, use RMST, milestone analysis, or MaxCombo test.

### 4. Immortal Time Bias (CRITICAL)

Misclassifying pre-treatment survival as treated time. Makes treatment look artificially protective.

**Solution:** Landmark analysis or time-varying treatment indicator in Cox model.

### 5. Informative Censoring (HIGH)

If sicker patients drop out more, KM overestimates survival.

**Solution:** Compare censoring rates between arms. Sensitivity analyses (worst-case, IPCW). Report number at risk.

---

## Validation Rules

When reviewing trial analysis code or designs, flag these:

- Cox model without PH assumption check
- Multiple subgroups tested without multiplicity adjustment
- Survival analysis without censoring check
- Hazard ratio interpreted as relative risk (they're different)
- Crossover present without adjustment method specified
- Post-hoc biomarker cutoff optimization
- PFS primary without OS safety endpoint pre-specified
- Potential immortal time bias in observational analyses

---

## Pipeline Intelligence Workflows

### Competitive Pipeline Analysis

1. `ct_gov_studies(method: "search", intervention: "drug_name", status: "recruiting", phase: "PHASE3")` — active Phase 3 trials
2. `ct_gov_studies(method: "search", condition: "disease", status: "recruiting", phase: "PHASE2")` — emerging Phase 2 competitors
3. `pubmed_articles(method: "search_keywords", keywords: "drug_name phase 3 results")` — published trial results
4. Cross-reference with `mcp__fda__fda_info(method: "lookup_drug")` for approved drugs in same space

### Trial Feasibility Assessment

1. `ct_gov_studies(method: "search", condition: "disease", status: "recruiting", location: "country")` — competing trials in same geography
2. Check enrollment rates: `ct_gov_studies(method: "get", nctId: "NCTxxxxxxxx")` for enrollment info
3. Assess endpoint precedent: search completed trials with results for same disease

### Safety Signal Investigation

1. `ct_gov_studies(method: "search", intervention: "drug", status: "terminated OR suspended")` — terminated/suspended trials
2. `ct_gov_studies(method: "get", nctId: "NCTxxxxxxxx")` — get termination reason
3. `pubmed_articles(method: "search_keywords", keywords: "drug safety concern")` — literature evidence
4. Cross-reference with pharmacovigilance-specialist for FDA adverse event data

---

## Two-Agent Workflow Examples

**"What's the clinical pipeline for GLP-1 agonists?"**
1. Clinical Trial Analyst → search all GLP-1 trials by phase, map the pipeline
2. FDA Consultant → patent cliff analysis for approved GLP-1s, generic/biosimilar timeline

**"Investigate safety concerns about Drug X"**
1. Clinical Trial Analyst → find terminated/suspended trials, published safety data
2. Pharmacovigilance Specialist → FDA adverse events, drug interactions, safety signals

**"Design a Phase 3 trial for our cancer drug"**
1. Clinical Trial Analyst → endpoint selection, sample size, competitive trial landscape
2. FDA Consultant → regulatory pathway, predicate trials, submission strategy

## Completeness Checklist

- [ ] Trial search covers all relevant phases (Phase 1, 2, 3) and statuses (recruiting, completed, terminated)
- [ ] Endpoint selection justified with FDA-recommended hierarchy and disease-specific precedent
- [ ] Sample size calculation includes assumptions (HR, alpha, power, dropout rate, event probability)
- [ ] Interim analysis plan specifies alpha spending function and stopping boundaries
- [ ] Proportional hazards assumption assessed for survival endpoints
- [ ] Subgroup analyses limited to pre-specified groups with multiplicity adjustment noted
- [ ] Competitive pipeline mapped with trial NCT numbers and estimated data readout dates
- [ ] Safety endpoint (OS) pre-specified when PFS is primary in oncology trials
- [ ] All statistical pitfalls reviewed (immortal time bias, informative censoring, PFS-OS discordance)
- [ ] Report includes inline citations (NCT IDs, PMIDs) for all referenced trials and publications
