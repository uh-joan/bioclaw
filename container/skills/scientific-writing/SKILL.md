---
name: scientific-writing
description: Scientific manuscript writing following IMRAD structure with 10 reporting guidelines (CONSORT, STROBE, PRISMA, STARD, TRIPOD, ARRIVE, CARE, SQUIRE, SPIRIT, CHEERS). Covers research articles, review papers, case reports, methods papers, and perspectives. Provides section-specific writing guidance, field-specific terminology, citation management, and figure/table best practices. Use when asked to write a scientific paper, draft a manuscript, structure a research article, write an abstract, prepare a methods section, or create any scientific document for publication.
---

# Scientific Writing

Guides writing of research manuscripts, reviews, and scientific documents following IMRAD structure and established reporting guidelines. Covers all major manuscript types with section-by-section writing guidance, field-specific terminology conventions, citation best practices, and figure/table formatting standards.

## Report-First Workflow

1. **Create manuscript file immediately**: `[topic]_scientific-writing_manuscript.md` with all section headers for the chosen manuscript type
2. **Add placeholders**: Mark each section `[Drafting...]`
3. **Populate progressively**: Draft sections as literature is gathered from MCP tools and user-supplied data
4. **Never show raw tool output**: Synthesize findings into polished manuscript prose
5. **Final verification**: Ensure no `[Drafting...]` placeholders remain

## When NOT to Use This Skill

- Peer review or manuscript critique -> use `peer-review`
- Clinical study reports (CSR, IB, DSUR) -> use `clinical-report-writer`
- PRISMA-compliant systematic review methodology -> use `systematic-literature-reviewer`
- Statistical analysis planning or interpretation -> use `scientific-critical-thinking`
- Grant proposal or funding application -> use `research-grants`
- Hypothesis generation or research question formulation -> use `hypothesis-generation`

## Cross-Reference: Other Skills

- **Reviewing a manuscript** -> use peer-review skill
- **Clinical study reports (CSR/SAE)** -> use clinical-report-writer skill
- **Systematic review methodology** -> use systematic-literature-reviewer skill
- **Statistical analysis guidance** -> use scientific-critical-thinking skill
- **Grant proposal writing** -> use research-grants skill
- **Hypothesis formulation** -> use hypothesis-generation skill

## Available MCP Tools

### `mcp__pubmed__pubmed_data` (Literature Search)

| Method | Manuscript use |
|--------|---------------|
| `search_keywords` | Find relevant literature for introduction and discussion |
| `search_advanced` | Targeted search with journal, date, author filters |
| `get_article_metadata` | Retrieve citation details for reference list |

### `mcp__biorxiv__biorxiv_data` (Recent Preprints)

| Method | Manuscript use |
|--------|---------------|
| `search_preprints` | Identify latest unpublished work in the field |
| `get_preprint_details` | Full preprint metadata for citation |

### `mcp__ctgov__ctgov_data` (Clinical Trial Registry)

| Method | Manuscript use |
|--------|---------------|
| `search` | Verify trial registration for clinical manuscripts |
| `get` | Retrieve full trial record for methods/results reference |

---

## Manuscript Types

### Type Selection

```
User request analysis:
+-- Original research with experimental/observational data
|   -> ORIGINAL RESEARCH ARTICLE (IMRAD)
|
+-- Synthesis of existing literature
|   +-- Narrative overview -> NARRATIVE REVIEW
|   +-- Formal search + screening -> SYSTEMATIC REVIEW
|   +-- Broad mapping of evidence -> SCOPING REVIEW
|   +-- Quantitative pooling -> META-ANALYSIS
|
+-- Single patient/case description
|   -> CASE REPORT (CARE guidelines)
|
+-- New technique, assay, or protocol
|   -> METHODS PAPER
|
+-- Brief findings or preliminary data
|   -> SHORT COMMUNICATION / LETTER
|
+-- Viewpoint or field commentary
    -> PERSPECTIVE / COMMENTARY / OPINION
```

**Ask the user which type they want if ambiguous.** Default to original research article for data-driven manuscripts, narrative review for synthesis requests.

---

## Original Research Article (IMRAD Structure)

### Section-by-Section Guidance

---

### Title

**Goal**: Convey the study's main finding or scope in minimal words.

| Rule | Rationale | Example |
|------|-----------|---------|
| Keep under 15 words (ideal) | Improves readability and indexing | "EGFR Inhibition Reduces Tumor Growth in KRAS-Wild-Type Colorectal Cancer" |
| Include key variables | Readers and search engines need specificity | Name the intervention AND outcome |
| Avoid abbreviations | Not all readers know them | Write "Randomized Controlled Trial" not "RCT" |
| Avoid questions | Declarative titles are stronger for research articles | "X Reduces Y" not "Does X Reduce Y?" |
| Avoid "A study of..." | Wastes words; all papers are studies | Start with the key finding or topic |
| Include study design for clinical papers | Required by many journals; aids filtering | "...A Double-Blind Randomized Controlled Trial" |
| Use specific terminology | Generic titles reduce discoverability | "Pembrolizumab" not "PD-1 Inhibitor" |

**Running title**: 40-60 characters, captures the essence.

---

### Abstract

**Structured abstract** (for original research): Background, Methods, Results, Conclusions.

**Unstructured abstract** (for reviews, perspectives): Single flowing paragraph.

| Rule | Detail |
|------|--------|
| Word count | 150-300 words (check target journal) |
| Background | 2-3 sentences: context + knowledge gap |
| Methods | Study design, setting, participants (N), intervention, primary outcome, statistical approach |
| Results | Primary outcome with effect size, 95% CI, and p-value; key secondary outcomes |
| Conclusions | 1-2 sentences: what this means, clinical/scientific implications |
| No citations | Abstracts are self-contained |
| No undefined abbreviations | Define any abbreviation at first use within the abstract |
| Trial registration | Include registration number (e.g., NCT12345678) if applicable |

**Common abstract pitfalls**:
- Overstating results (using "significant" loosely)
- Including results not in the main paper
- Vague conclusions ("further research is needed" alone is insufficient)
- Missing the primary outcome effect size

---

### Introduction (3-Paragraph Structure)

The introduction funnels from broad to specific. Three paragraphs is the classic structure; some journals allow four.

**Paragraph 1: Broad Context**
- Why does this field matter?
- Prevalence, burden, or scientific importance
- Establish the general topic area
- 3-5 citations to reviews or landmark papers

**Paragraph 2: Narrow to the Gap**
- What is currently known?
- What is unknown, controversial, or insufficient?
- What have previous studies attempted and where did they fall short?
- The gap statement is the most important sentence in the introduction
- 5-8 citations to relevant primary literature

**Paragraph 3: Study Objective**
- What did you do and why?
- State the specific aim, hypothesis, or research question
- Briefly mention the approach (study design)
- Optional: state the expected contribution
- End with a clear objective statement: "We aimed to..." or "The objective of this study was to..."

| Do | Avoid |
|----|-------|
| Build logical narrative from broad to specific | Exhaustive literature review (save for discussion) |
| State the gap explicitly | Vague statements like "little is known" without specificity |
| End with a clear objective | Revealing results in the introduction |
| Cite primary sources | Over-relying on reviews for specific claims |

---

### Methods

**Cardinal rule**: Another scientist must be able to reproduce your study from the Methods section alone.

#### Study Design and Setting

- Name the design explicitly (e.g., "prospective cohort study," "double-blind RCT," "cross-sectional survey")
- Describe the setting (single center vs. multicenter, country, time period)
- Reference the applicable reporting guideline (e.g., "reported following CONSORT 2010")

#### Participants

- Eligibility criteria (inclusion and exclusion)
- Recruitment method and dates
- Sample size justification (power calculation with alpha, beta, expected effect size, and dropout rate)
- Informed consent process

#### Interventions / Exposures

- Detailed description: what, how, when, how long
- For drugs: generic name (INN), dose, route, frequency, duration, manufacturer
- For surgical/device: technique, model, settings
- Comparator/control description with equal detail
- Blinding: who was blinded, how was it maintained

#### Outcomes

- Primary outcome: definition, measurement method, time point
- Secondary outcomes: listed in order of importance
- Outcome assessors: blinded or unblinded
- Clinically meaningful difference defined a priori

#### Statistical Analysis

| Element | Required Detail |
|---------|----------------|
| Software | Name and version (e.g., "R v4.3.1, R Foundation") |
| Primary analysis | Test used, model specification |
| Significance threshold | alpha level (typically 0.05, two-sided) |
| Multiple testing | Correction method if >1 primary endpoint |
| Missing data | How handled (complete case, imputation method) |
| Sensitivity analyses | Pre-specified, listed |
| Subgroup analyses | Pre-specified or exploratory (state which) |
| Effect measures | OR, RR, HR, mean difference, with 95% CI |
| Sample size | Calculation with assumptions stated |

#### Ethics and Registration

- IRB/Ethics committee name and approval number
- Informed consent statement
- Clinical trial registration number and registry
- Data availability statement
- Funding sources and role of funder

---

### Results

**Cardinal rule**: Report findings without interpretation. The Results section presents data; the Discussion interprets it.

#### Structure

1. **Participant flow first**: Enrollment, allocation, follow-up, analysis (reference CONSORT flow diagram for RCTs)
2. **Baseline characteristics**: Table 1 with demographics and clinical characteristics by group
3. **Primary outcome**: Effect size with 95% CI and exact p-value
4. **Secondary outcomes**: In pre-specified order
5. **Subgroup and sensitivity analyses**: Clearly labeled
6. **Adverse events / harms**: For intervention studies

#### Statistical Reporting Standards

| Reporting Element | Correct Format | Incorrect Format |
|------------------|---------------|-----------------|
| P-values | p = 0.032 | p < 0.05 |
| P-values (very small) | p < 0.001 | p = 0.000 |
| Confidence intervals | 95% CI [1.23, 4.56] or 95% CI: 1.23-4.56 | CI = 1.23-4.56 |
| Effect sizes | HR = 0.72, 95% CI [0.58, 0.89], p = 0.003 | HR was significant |
| Means | Mean (SD) = 42.3 (11.7) | Mean = 42.3 +/- 11.7 (ambiguous: SD or SEM?) |
| Medians | Median (IQR) = 34 (21-48) | Median = 34 |
| Counts | 127 of 450 patients (28.2%) | 28.2% of patients |

#### Writing Results Prose

- Text complements figures and tables; do not repeat every number from a table
- Refer to tables and figures parenthetically: "Survival was longer in the treatment group (Table 2; Figure 1)"
- Use past tense for completed analyses
- State the direction and magnitude of effects, not just significance
- Report all pre-specified outcomes, including null findings

---

### Discussion (Hourglass Structure)

The discussion mirrors the introduction in reverse: starts specific, broadens, then narrows to conclusion.

**Paragraph 1: Key Finding Restated (1 paragraph)**
- Open with the principal finding
- State it plainly without repeating statistics
- Relate directly to the study objective from the introduction

**Paragraphs 2-4: Comparison with Literature (2-3 paragraphs)**
- How do findings compare with previous studies?
- Where do they agree? Where do they differ?
- Possible explanations for discrepancies
- Cite specific studies with their key findings

**Paragraphs 5-6: Mechanisms and Implications (1-2 paragraphs)**
- Biological or theoretical explanation for findings
- Clinical implications: how should practice change?
- Policy implications if relevant
- Be appropriately speculative but label speculation clearly

**Paragraph 7: Limitations (1 paragraph)**
- Be honest and specific
- Address threats to internal validity (bias, confounding)
- Address threats to external validity (generalizability)
- Do not dismiss limitations; explain their likely impact
- Do not introduce new limitations that undermine the entire study

**Paragraph 8: Conclusion and Future Directions (1 paragraph)**
- Restate the main conclusion (without copying the abstract)
- Suggest 1-2 specific next steps for the field
- Avoid overstatement: match conclusions to the strength of evidence
- Do not introduce new data or results

| Do | Avoid |
|----|-------|
| Interpret findings in context of existing literature | Repeating results with statistics |
| Discuss mechanisms that explain findings | Unfounded speculation without labeling it |
| Be specific about limitations | "This study has limitations" without listing them |
| Match conclusion strength to evidence | "This proves..." for observational studies |
| Suggest concrete future studies | "More research is needed" as the only future direction |

---

### References

See Citation Best Practices section below.

---

## Review Article Types

### Narrative Review

| Section | Content |
|---------|---------|
| **Abstract** | Unstructured, single paragraph, 150-250 words |
| **Introduction** | Scope definition, why this review is needed now |
| **Search Strategy** | Brief description of how literature was identified (not PRISMA-level) |
| **Body Sections** | Organized thematically or chronologically; use descriptive subheadings |
| **Synthesis** | Integrate findings across studies; identify patterns and contradictions |
| **Future Directions** | Unanswered questions, promising research avenues |
| **Conclusion** | Summary of current understanding |

### Systematic Review (PRISMA 2020)

| Section | Content |
|---------|---------|
| **Registration** | PROSPERO or OSF registration number |
| **Eligibility** | PICO criteria explicitly stated |
| **Search Strategy** | Full search strings for each database; date of last search |
| **Screening** | PRISMA flow diagram with numbers at each stage |
| **Data Extraction** | Variables extracted, tools used, duplicate extraction |
| **Risk of Bias** | Tool used (RoB 2, ROBINS-I, NOS), assessment per study |
| **Synthesis** | Narrative synthesis with summary tables; meta-analysis if quantitative pooling performed |
| **Certainty of Evidence** | GRADE assessment for each outcome |

### Scoping Review

| Section | Content |
|---------|---------|
| **Framework** | Arksey and O'Malley or JBI methodology |
| **Mapping** | Charting table with study characteristics |
| **Gap Analysis** | Where evidence is lacking |

### Meta-Analysis (additional to PRISMA)

| Element | Requirement |
|---------|-------------|
| **Effect measure** | Standardized (OR, RR, HR, SMD) with justification |
| **Model** | Fixed-effects or random-effects with justification |
| **Heterogeneity** | I-squared, Q-test, tau-squared |
| **Forest plot** | Individual study estimates + pooled estimate |
| **Publication bias** | Funnel plot, Egger's test, trim-and-fill |
| **Sensitivity analyses** | Leave-one-out, subgroup, meta-regression |
| **GRADE** | Certainty of evidence for each outcome |

---

## Case Report (CARE Guidelines)

| Section | Content | Writing Tips |
|---------|---------|-------------|
| **Title** | Diagnosis and intervention, include "case report" | Be specific: "Nivolumab-Induced Myocarditis in a Patient with Melanoma: A Case Report" |
| **Keywords** | 2-5 MeSH-compatible keywords | |
| **Abstract** | Structured: Introduction, Case Presentation, Discussion, Conclusion | 150-200 words |
| **Introduction** | Brief background, why this case is reportable (novelty, rarity, teaching value) | 1-2 paragraphs maximum |
| **Patient Information** | Demographics, chief complaint, medical history, family history, comorbidities | De-identify carefully |
| **Clinical Findings** | Physical exam findings, relevant positives AND negatives | |
| **Timeline** | Chronological table of key events (symptom onset through follow-up) | Use a visual timeline figure |
| **Diagnostic Assessment** | Tests performed, results, diagnostic reasoning, differential diagnosis | Explain why other diagnoses were excluded |
| **Therapeutic Intervention** | Treatment type, dose, route, duration, rationale, changes made | |
| **Follow-up and Outcomes** | Clinician-assessed outcomes, patient-reported outcomes, adherence, adverse events | State follow-up duration |
| **Discussion** | Literature comparison, strengths and limitations, clinical implications | 3-4 paragraphs |
| **Patient Perspective** | Patient's own words if available and consented | Optional but encouraged |
| **Informed Consent** | Statement of consent for publication | Required by most journals |

---

## Methods Paper

| Section | Content |
|---------|---------|
| **Abstract** | Emphasize what the method does, how it improves on existing approaches, and validation results |
| **Introduction** | Current methods and their limitations; what gap this method fills |
| **Method Description** | Step-by-step protocol with sufficient detail for replication |
| **Validation** | Benchmarking against existing methods; performance metrics |
| **Implementation** | Software availability, hardware requirements, runtime |
| **Example Application** | Demonstration on real or representative data |
| **Limitations** | Conditions where the method may fail or underperform |
| **Data and Code Availability** | Repository links, version numbers, licenses |

---

## Short Communication / Letter

| Feature | Guidance |
|---------|----------|
| **Length** | 1000-2000 words (journal-specific) |
| **Structure** | Abbreviated IMRAD; may omit separate Introduction and Discussion headings |
| **Figures/Tables** | Usually limited to 1-2 |
| **References** | Usually limited to 10-20 |
| **Scope** | Preliminary findings, negative results, methodological notes, replications |

---

## Perspective / Commentary / Opinion

| Feature | Guidance |
|---------|----------|
| **Length** | 1000-3000 words |
| **Structure** | Free-form with logical argument flow; use subheadings |
| **Tone** | Authoritative but balanced; acknowledge opposing views |
| **Evidence** | Support opinions with citations; distinguish evidence from opinion |
| **Call to Action** | End with specific recommendations for the field, policy, or practice |
| **Disclosure** | Conflicts of interest are especially important in opinion pieces |

---

## 10 Reporting Guidelines with Checklists

### 1. CONSORT 2010 (Randomized Controlled Trials)

| Item | Section | Required Content | Common Deficiency |
|------|---------|-----------------|-------------------|
| 1a | Title | Identified as randomized trial | Missing "randomized" |
| 2a | Introduction | Scientific background and rationale | Too brief, no gap statement |
| 3a | Methods | Pre-specified primary and secondary outcomes | Outcome switching |
| 4a | Methods | Trial design (parallel, crossover, factorial) | Not stated |
| 5 | Methods | Interventions described with replication detail | Insufficient detail |
| 6a | Methods | Randomization: sequence generation method | Not described |
| 7a | Methods | Allocation concealment mechanism | Omitted |
| 8a | Methods | Who generated sequence, enrolled, assigned | Unclear roles |
| 9 | Methods | Blinding: who was blinded, how | Incomplete description |
| 10 | Methods | Statistical methods for primary and secondary outcomes | Missing power calculation |
| 11a | Results | Blinding: who was blinded and how | Blinding failures not reported |
| 13a | Results | CONSORT flow diagram with numbers | Missing or incomplete |
| 15 | Results | Baseline demographic table by group | Significance testing on baseline (inappropriate) |
| 17a | Results | Each outcome: effect size with CI and p-value | p-value without CI |
| 19 | Results | All harms or unintended effects | Safety data omitted |
| 20 | Discussion | Limitations: sources of bias, imprecision | Too brief |
| 22 | Other | Where full protocol can be accessed | Missing |
| 23 | Other | Registration number and registry name | Not reported |

### 2. STROBE (Observational Studies)

| Item | Section | Required Content |
|------|---------|-----------------|
| 1 | Title | Indicate study design in title or abstract |
| 3 | Methods | State study design early in the paper |
| 4 | Methods | Setting: locations, dates of recruitment, follow-up |
| 5 | Methods | Participants: eligibility criteria, sources, selection methods |
| 6 | Methods | Clearly define all variables (exposures, outcomes, confounders) |
| 7 | Methods | Data sources and measurement methods |
| 8 | Methods | Describe efforts to address potential sources of bias |
| 10 | Methods | Explain how sample size was arrived at |
| 12 | Methods | Statistical methods including confounding control |
| 13 | Results | Report participant numbers at each study stage (flow diagram) |
| 14 | Results | Descriptive data: characteristics, missing data |
| 15 | Results | Outcome data: event numbers or summary measures |
| 16 | Results | Main results: unadjusted and adjusted estimates with CI and p |
| 18 | Results | Other analyses: subgroup, interaction, sensitivity |
| 19 | Discussion | Key results with reference to objectives |
| 20 | Discussion | Limitations: discuss direction and magnitude of bias |
| 21 | Discussion | Cautious interpretation considering objectives, limitations, multiplicity |

### 3. PRISMA 2020 (Systematic Reviews and Meta-Analyses)

| Item | Section | Required Content |
|------|---------|-----------------|
| 1 | Title | Identify as systematic review, meta-analysis, or both |
| 2 | Abstract | Structured summary: objectives, data sources, eligibility, synthesis, results |
| 5 | Methods | Eligibility: PICO criteria, study types, date limits |
| 6 | Methods | Information sources: databases, registers, date of last search |
| 7 | Methods | Full search strategy for at least one database |
| 8 | Methods | Selection process: screening stages, reviewers, software |
| 9 | Methods | Data collection: extraction forms, number of extractors, consensus |
| 11 | Methods | Risk of bias assessment tool and process |
| 13 | Methods | Synthesis methods: meta-analysis model, heterogeneity measures |
| 15 | Results | PRISMA flow diagram with numbers at each stage |
| 16 | Results | Study characteristics table |
| 18 | Results | Individual study results (forest plot for meta-analyses) |
| 19 | Results | Synthesis results: pooled estimate, CI, heterogeneity, prediction interval |
| 21 | Results | Publication bias assessment (funnel plot, statistical tests) |
| 22 | Results | Certainty of evidence (GRADE for each outcome) |
| 23 | Discussion | General interpretation in context of other evidence |
| 24 | Discussion | Limitations at review and outcome level |
| 27 | Other | Registration and protocol: PROSPERO number, deviations from protocol |

### 4. STARD (Diagnostic Accuracy Studies)

| Item | Section | Required Content |
|------|---------|-----------------|
| 1 | Title | Identify as diagnostic accuracy study |
| 3 | Methods | Study design: cross-sectional, cohort, case-control |
| 5 | Methods | Participants: eligibility criteria, setting, recruitment |
| 7 | Methods | Index test: methods, thresholds, who performed, blinding |
| 8 | Methods | Reference standard: definition, rationale, who performed, blinding |
| 10 | Methods | Planned analysis: sample size, handling of indeterminate results |
| 14 | Results | Participant flow diagram (STARD-specific) |
| 17 | Results | Time interval between index test and reference standard |
| 19 | Results | Cross-tabulation (2x2 table) of index test vs reference standard |
| 20 | Results | Sensitivity, specificity, LR+, LR-, PPV, NPV with 95% CI |
| 21 | Results | Estimates of diagnostic accuracy at each threshold (if multiple) |
| 24 | Discussion | Limitations including spectrum bias, verification bias |

### 5. TRIPOD (Prediction Model Studies)

| Item | Section | Required Content |
|------|---------|-----------------|
| 1 | Title | Identify development, validation, or both; name the outcome |
| 3a | Methods | Source of data: cohort, registry, trial |
| 4a | Methods | Participants: eligibility, treatment, setting |
| 6a | Methods | Outcome definition, blinding of outcome assessment |
| 7a | Methods | Candidate predictors: definition, timing of measurement |
| 10 | Methods | Statistical methods: model building, variable selection, handling of missing data |
| 10d | Methods | Internal validation: cross-validation, bootstrapping |
| 14 | Results | Model performance: discrimination (C-statistic/AUC), calibration (calibration plot, Hosmer-Lemeshow) |
| 15 | Results | Model specification: final model with coefficients or hazard ratios |
| 16 | Results | Model updating/recalibration if validation study |
| 18 | Discussion | Limitations: overfitting risk, transportability |
| 21 | Other | Model available for use: supplementary material, web calculator, code repository |

### 6. ARRIVE 2.0 (Animal Research)

| Item | Section | Required Content |
|------|---------|-----------------|
| 1 | Methods | Species, strain, sex, age, weight |
| 2 | Methods | Source, breeding, housing conditions, diet, light cycle |
| 3 | Methods | Sample size per group with power calculation |
| 4 | Methods | Randomization: method of allocation to groups |
| 5 | Methods | Blinding: who was blinded during allocation, conduct, outcome assessment |
| 6 | Methods | Outcome measures: primary and secondary with definitions |
| 7 | Methods | Statistical methods: test, software, significance threshold |
| 8 | Methods | Experimental procedures: detail sufficient for replication |
| 9 | Results | Baseline data: body weight, health status at study start |
| 10 | Results | Numbers analyzed: animals excluded and reasons |
| 11 | Results | Outcomes with effect sizes and variability measures |
| 14 | Ethics | Ethics committee approval, animal welfare regulations followed |
| 15 | Other | Adverse events, humane endpoints, unexpected deaths |

### 7. CARE (Case Reports)

| Item | Section | Required Content |
|------|---------|-----------------|
| 1 | Title | Diagnosis/condition and "case report" |
| 3 | Introduction | Why this case is unique, rare, or instructive |
| 4 | Patient | De-identified demographics, symptoms, medical/family history |
| 5 | Clinical | Physical examination findings (pertinent positives and negatives) |
| 6 | Timeline | Chronological table or figure of key events |
| 7 | Diagnostic | Tests, diagnostic challenges, reasoning, differential |
| 8 | Treatment | Intervention details: type, dose, route, duration, changes, rationale |
| 9 | Outcomes | Clinician and patient-reported outcomes, follow-up, adverse events |
| 10 | Discussion | Literature context, strengths, limitations, conclusions |
| 11 | Patient | Patient perspective (if available and consented) |
| 12 | Consent | Informed consent statement |

### 8. SQUIRE 2.0 (Quality Improvement Studies)

| Item | Section | Required Content |
|------|---------|-----------------|
| 1 | Title | Indicate this is a quality improvement study |
| 4 | Introduction | Nature and significance of the local problem |
| 5 | Introduction | Available knowledge: evidence summary informing the intervention |
| 6 | Introduction | Rationale: informal or formal frameworks used |
| 7 | Introduction | Specific aims: measurable, time-bound objectives |
| 8 | Methods | Context: site characteristics, organizational culture, history of change |
| 9 | Methods | Intervention: what was done, by whom, how, when |
| 10 | Methods | Study of the intervention: approach to assessing impact (e.g., PDSA cycles) |
| 11 | Methods | Measures: process, outcome, and balancing measures with operational definitions |
| 12 | Methods | Analysis: qualitative and quantitative methods, run charts or SPC |
| 14 | Results | Process measures: adherence, fidelity |
| 15 | Results | Outcome measures: changes over time |
| 17 | Discussion | Summary: key findings, relationship to context |
| 18 | Discussion | Interpretation: mechanisms, comparison to literature |
| 19 | Discussion | Limitations: threats to validity, generalizability |

### 9. SPIRIT 2013 (Clinical Trial Protocols)

| Item | Section | Required Content |
|------|---------|-----------------|
| 1 | Admin | Descriptive title: population, intervention, acronym |
| 2a | Admin | Trial registration: number, registry, date |
| 5a | Admin | Funding sources and their role |
| 6a | Introduction | Background: rationale for the trial |
| 7 | Introduction | Objectives and hypotheses |
| 8 | Methods | Trial design: type, allocation ratio, framework (superiority/non-inferiority) |
| 9 | Methods | Study setting: description of sites |
| 10 | Methods | Eligibility criteria |
| 11a | Methods | Intervention: precise details for each arm |
| 12 | Methods | Outcomes: primary and secondary with time points and definitions |
| 13 | Methods | Timeline: schedule of enrollment, interventions, assessments (SPIRIT figure) |
| 14 | Methods | Sample size: target, power, assumptions |
| 15 | Methods | Recruitment strategies |
| 16a | Methods | Randomization: sequence generation, allocation concealment |
| 17a | Methods | Blinding: who is blinded, procedure for unblinding |
| 20a | Methods | Statistical analysis plan: primary analysis, interim analyses, stopping rules |
| 22 | Methods | Data management: collection, entry, coding, security |
| 23 | Ethics | Research ethics approval |
| 29 | Ethics | Consent procedures |
| 31a | Other | Dissemination: publication policy, authorship eligibility |

### 10. CHEERS 2022 (Health Economic Evaluations)

| Item | Section | Required Content |
|------|---------|-----------------|
| 1 | Title | Identify as economic evaluation and state interventions compared |
| 4 | Introduction | Describe the health condition and current practice |
| 5 | Methods | Type of economic evaluation: CUA, CEA, CBA, CMA |
| 6 | Methods | Study perspective: healthcare system, societal, payer |
| 7 | Methods | Time horizon and justification |
| 8 | Methods | Discount rate for costs and outcomes with justification |
| 9 | Methods | Population and subgroups |
| 10 | Methods | Setting and location |
| 11 | Methods | Comparators: justify selection |
| 12 | Methods | Health outcomes: QALYs, DALYs, LYG, natural units |
| 13 | Methods | Measurement and valuation of outcomes (utility weights source) |
| 14 | Methods | Resource use and cost: quantities and unit costs, currency, price year |
| 16 | Methods | Model structure: diagram, assumptions, cycle length, software |
| 17 | Methods | Analytic methods: handling uncertainty, heterogeneity |
| 18 | Results | Study parameters: base case values, distributions, data sources (table) |
| 19 | Results | Incremental costs, outcomes, and ICER |
| 20 | Results | Sensitivity analyses: one-way, probabilistic (cost-effectiveness acceptability curve) |
| 22 | Discussion | Limitations: model assumptions, data gaps |
| 24 | Other | Source of funding and conflicts of interest |

---

## Reporting Guideline Quick-Reference Table

| Guideline | Study Type | Key Items | Checklist URL |
|-----------|-----------|-----------|---------------|
| CONSORT | Randomized controlled trials | Flow diagram, ITT, randomization, blinding | consort-statement.org |
| STROBE | Observational studies (cohort, case-control, cross-sectional) | Design, setting, participants, variables, bias | strobe-statement.org |
| PRISMA | Systematic reviews and meta-analyses | Search strategy, PICO, forest plots, heterogeneity | prisma-statement.org |
| STARD | Diagnostic accuracy studies | Index test, reference standard, 2x2 table | stard-statement.org |
| TRIPOD | Prediction model studies | Development, validation, calibration, discrimination | tripod-statement.org |
| ARRIVE | Animal research | Species, housing, sample size, randomization, blinding | arriveguidelines.org |
| CARE | Case reports | Timeline, diagnostic assessment, intervention, consent | care-statement.org |
| SQUIRE | Quality improvement studies | Context, intervention, PDSA, measures | squire-statement.org |
| SPIRIT | Clinical trial protocols | Eligibility, interventions, outcomes, sample size, SPIRIT figure | spirit-statement.org |
| CHEERS | Health economic evaluations | Perspective, time horizon, discount rate, sensitivity analysis | ispor.org/cheers |

---

## Field-Specific Terminology Guides

### Biomedical Sciences

| Convention | Rule | Example |
|------------|------|---------|
| Gene symbols (human) | Italicized, all caps | *BRCA1*, *TP53*, *EGFR* |
| Gene symbols (mouse) | Italicized, first letter cap | *Trp53*, *Brca1* |
| Protein names | Roman (not italic), caps per convention | BRCA1 protein, p53, EGFR |
| Gene nomenclature authority | Follow HGNC (human), MGI (mouse) | |
| Statistical reporting | APA style: F(1,48) = 7.23, p = 0.010 | |
| Units | SI units preferred; use standard abbreviations | mg/kg, mmol/L, kDa |
| Species names | Italicized at first mention, abbreviated thereafter | *Escherichia coli* then *E. coli* |
| Amino acid changes | Three-letter or one-letter code | p.Val600Glu or V600E |
| Nucleotide variants | HGVS nomenclature | c.1799T>A, g.140453136A>T |

### Molecular Biology

| Convention | Rule |
|------------|------|
| DNA sequences | Lowercase italics for short sequences; 5'-ATCG-3' notation |
| RNA | Lowercase; distinguish mRNA, miRNA, lncRNA, siRNA |
| Enzymes | Use EC number at first mention; italicize gene, roman for protein |
| Restriction enzymes | Roman, capitalized: EcoRI, BamHI, HindIII |
| Plasmids | Lowercase "p" prefix, roman: pBR322, pUC19 |
| Vectors | Describe backbone, promoter, selection marker |

### Chemistry

| Convention | Rule |
|------------|------|
| IUPAC naming | Use systematic names at first mention; common names acceptable after |
| Stereochemistry | (R)/(S) for absolute; (+)/(-) for optical rotation; E/Z for alkenes |
| Concentrations | mol/L (M), not molar; specify v/v, w/v, w/w |
| pH | Lowercase "p", capital "H"; report temperature |
| Buffers | Composition, pH, temperature |

### Pharmacology

| Convention | Rule |
|------------|------|
| Drug names | Use INN (International Nonproprietary Name) as generic name |
| Brand names | Capitalize, use only once with INN at first mention |
| Dosing | mg/kg body weight; mg/m2 for oncology |
| PK parameters | Cmax, Tmax, AUC0-inf, t1/2, CL, Vd |
| PD parameters | EC50, IC50, Emax, Ki, Kd |
| Receptor nomenclature | Follow IUPHAR/BPS Guide to Pharmacology |

---

## Figure and Table Best Practices

### Figures

| Element | Standard |
|---------|----------|
| Resolution | 300 DPI minimum (600 DPI for line art) |
| Format | Vector (SVG, EPS, PDF) preferred; TIFF for raster |
| Color | Colorblind-safe palettes (avoid red-green only); test with colorblindness simulator |
| Legends | Complete: what is shown, what symbols/colors mean, statistical annotations, N per group |
| Labels | Axis labels with units; font size readable at final print size |
| Scale bars | Required for microscopy and imaging |
| Panels | Label A, B, C...; reference each panel in legend and text |
| Statistical annotations | Use exact p-values or standard symbols: * p<0.05, ** p<0.01, *** p<0.001 (define in legend) |
| Error bars | Define clearly: SD, SEM, or 95% CI (SEM and CI are not interchangeable) |
| CONSORT flow diagram | Required for RCTs; use standard template |
| Forest plot | Required for meta-analyses; include I-squared and pooled estimate |

### Tables

| Element | Standard |
|---------|----------|
| Gridlines | Horizontal rules only (top, under header, bottom); no vertical lines |
| Units | In column headers, not repeated in cells |
| Abbreviations | Define all in table footnote |
| Numbers | Align decimals; consistent decimal places within columns |
| Table 1 | Baseline characteristics: do not test for statistical significance between randomized groups |
| Footnotes | Use symbols in order: *, dagger, double-dagger, section, then superscript letters |
| Spanning headers | Use for grouping related columns |
| Missing data | Report N for each cell; indicate how missing data were handled |

### Supplementary Materials

| Material | When to Use |
|----------|-------------|
| Supplementary tables | Full datasets, sensitivity analyses, extended baseline characteristics |
| Supplementary figures | Additional forest plots, subgroup analyses, calibration plots |
| Supplementary methods | Detailed protocols, search strategies, statistical code |
| Data availability | Raw data in repository (Zenodo, Dryad, Figshare) or upon reasonable request |
| Code availability | Analysis code in GitHub/GitLab with version tag |
| CONSORT/PRISMA checklist | Completed checklist with page numbers |

---

## Citation Best Practices

### Source Selection

| Principle | Rationale |
|-----------|-----------|
| Prefer primary sources over reviews | Reviews summarize; cite the original finding |
| Recent references (>50% within 5 years) | Demonstrates currency for active fields |
| Include seminal/foundational papers | Shows awareness of field history |
| Balanced citations | Avoid excessive self-citation (>10% is a red flag for reviewers) |
| Cite contradictory evidence | Shows objectivity; strengthens discussion |
| Use DOIs or PMIDs | Ensures verifiability |
| Avoid citing abstracts as primary evidence | Conference abstracts are not peer-reviewed |
| Cite preprints cautiously | Label as "preprint" and note lack of peer review |

### Citation Placement

| Context | Citation Style |
|---------|---------------|
| Factual claim | Cite at end of clause or sentence: "...increases survival [1]." |
| Comparing studies | Name authors: "Smith et al. [1] found X, whereas Jones et al. [2] reported Y." |
| Method borrowed from another study | Cite at method description: "...as previously described [1]." |
| Multiple supporting references | Group: [1-3] or [1,4,7] |
| Controversial claim | Cite both sides: "Some studies support X [1-3], while others do not [4,5]." |

### Reference Management

- Use citation manager (Zotero, Mendeley, EndNote)
- Check journal citation format before formatting (Vancouver numbered, APA author-date, etc.)
- Verify all references are actually cited in text (and vice versa)
- Check retraction status of key references via Retraction Watch
- Ensure DOIs resolve correctly

---

## Common Writing Pitfalls

### Language and Style

| Pitfall | Problem | Fix |
|---------|---------|-----|
| Passive voice overuse | Obscures who did what | Use active voice: "We measured..." not "Measurements were taken..." |
| Hedging excess | Weakens claims unnecessarily | "Our data suggest" is fine; "Our data might perhaps potentially suggest" is not |
| Jargon without definition | Excludes readers outside subspecialty | Define specialized terms at first use |
| Tense inconsistency | Confuses timeline | Methods/Results: past tense; established facts: present tense |
| Dangling modifiers | Creates ambiguity | "Using mass spectrometry, the proteins were identified" -> "Using mass spectrometry, we identified the proteins" |
| Nominalizations | Wordy and weak | "We performed an investigation of" -> "We investigated" |
| Redundancy | Wastes word count | "A total of 50 patients" -> "50 patients" |
| Anthropomorphism | Attributes intent to objects | "This study aims to" -> "We aimed to" |

### Logical and Structural

| Pitfall | Problem | Fix |
|---------|---------|-----|
| Mismatch between abstract and paper | Reviewers check this first | Write abstract last; verify every claim appears in the paper |
| Introduction too long | Reads like a review article | 3-4 paragraphs maximum; save depth for discussion |
| Methods too brief | Cannot reproduce the study | Include all details; use supplementary methods for extended protocols |
| Results and discussion mixed | Blurs findings vs. interpretation | Keep them separate unless journal requires combined section |
| Overclaiming | Conclusions exceed evidence | Match claim strength to study design: RCT -> "demonstrates"; observational -> "suggests" |
| Undisclosed limitations | Reviewers will find them | Address limitations proactively and honestly |
| Selective reporting | Only positive results shown | Report all pre-specified outcomes including null findings |

---

## Manuscript Preparation Workflow

### Step 1: Determine Manuscript Type

```
1. Identify the type of data/content:
   - Experimental/clinical data -> Original research article
   - Literature synthesis -> Review article (determine subtype)
   - Single patient -> Case report
   - New method/tool -> Methods paper
   - Brief finding -> Short communication
   - Opinion/viewpoint -> Perspective

2. Select the applicable reporting guideline (see quick-reference table)

3. Confirm target journal requirements:
   - Word/page limits
   - Abstract format (structured vs. unstructured)
   - Reference style (Vancouver, APA, etc.)
   - Figure/table limits
   - Required sections or statements
```

### Step 2: Create Manuscript Template

```
1. Create file: [topic]_scientific-writing_manuscript.md
2. Add all required sections for the chosen manuscript type
3. Add the appropriate reporting guideline checklist as an appendix
4. Mark each section [Drafting...]
```

### Step 3: Literature Search for Context

```
1. Search for relevant literature:
   mcp__pubmed__pubmed_data(keywords: "TOPIC", num_results: 30)

2. Search for recent preprints:
   mcp__biorxiv__biorxiv_data(query: "TOPIC", limit: 20)

3. Verify trial registrations if clinical:
   mcp__ctgov__ctgov_data(condition: "CONDITION", intervention: "INTERVENTION")

4. Retrieve metadata for key references:
   mcp__pubmed__pubmed_data(pmid: "PMID")
```

### Step 4: Draft Sections

```
Recommended drafting order:
1. Methods (most objective; easiest to write first)
2. Results (flows from methods)
3. Introduction (now you know what to introduce)
4. Discussion (now you know what to discuss)
5. Abstract (summary of completed sections)
6. Title (refined based on final content)
7. References (compiled throughout, verified at end)
```

### Step 5: Apply Reporting Guideline Checklist

```
1. Go through the applicable checklist item by item
2. Verify each item is addressed in the manuscript
3. Note page/line numbers for each item (many journals require this)
4. Flag any items that cannot be addressed and explain why
```

### Step 6: Final Review

```
1. Internal consistency: numbers match across abstract, text, tables, figures
2. All figures and tables referenced in text
3. All references cited in text and listed in references (and vice versa)
4. Reporting guideline checklist complete
5. Author contributions statement (CRediT taxonomy)
6. Conflicts of interest disclosure
7. Data availability statement
8. Ethical approval and consent statements
9. Funding acknowledgment
10. No [Drafting...] placeholders remain
```

---

## Multi-Agent Workflow Examples

**"Write a research article on our clinical trial results"**
1. Scientific Writing -> IMRAD structure, CONSORT checklist, statistical reporting standards
2. Clinical Report Writer -> ICH-E3 context if CSR is also needed
3. Scientific Critical Thinking -> Statistical analysis verification and interpretation

**"Draft a systematic review on X"**
1. Scientific Writing -> Manuscript structure, PRISMA checklist, meta-analysis reporting
2. Systematic Literature Reviewer -> PRISMA-compliant search and screening methodology
3. Scientific Critical Thinking -> Quality assessment and evidence synthesis

**"Write up our animal study for publication"**
1. Scientific Writing -> IMRAD structure, ARRIVE 2.0 checklist, methods detail
2. Peer Review -> Pre-submission manuscript critique

**"Prepare a case report for journal submission"**
1. Scientific Writing -> CARE-compliant structure, timeline figure, discussion
2. Clinical Report Writer -> If regulatory SAE narrative is also needed

**"Write a health economics paper"**
1. Scientific Writing -> Manuscript structure, CHEERS checklist, sensitivity analysis reporting
2. Research Grants -> If HTA submission is also planned

---

## Completeness Checklist

- [ ] Manuscript type identified and confirmed with user
- [ ] Applicable reporting guideline selected from the 10 supported guidelines
- [ ] All required sections for the manuscript type drafted with content
- [ ] Title follows guidelines: concise, informative, no abbreviations, includes study design if clinical
- [ ] Abstract within word limit; structured or unstructured as appropriate; includes primary outcome with effect size
- [ ] Introduction follows 3-paragraph funnel: context -> gap -> objective
- [ ] Methods sufficiently detailed for reproducibility; includes ethics, registration, statistics
- [ ] Results report effect sizes with 95% CI and exact p-values; no interpretation
- [ ] Discussion follows hourglass: key finding -> literature comparison -> mechanisms -> limitations -> conclusion
- [ ] All figures have complete legends, appropriate resolution, and colorblind-safe palettes
- [ ] All tables use horizontal rules only, units in headers, footnotes for abbreviations
- [ ] Citations are primarily from primary sources; >50% within 5 years; seminal papers included
- [ ] Reporting guideline checklist completed with page/line references
- [ ] Field-specific terminology follows established conventions (HGNC, IUPAC, INN)
- [ ] Author contributions (CRediT), conflicts of interest, funding, data availability statements present
- [ ] Internal consistency verified: numbers match across abstract, text, tables, and figures
- [ ] No `[Drafting...]` placeholders remain in final document
