---
name: experimental-design
description: Design rigorous experiments and analyses across wet lab, computational, and clinical trial domains. Produces pre-registration-quality experimental plans with hypothesis formulation (PICO/FINER), study design selection, variable specification, power analysis with Python code, randomization and blinding strategy, endpoint definition, statistical analysis plans, and reviewer objection anticipation. Use when asked to design an experiment, plan a study, write a protocol, calculate sample size, create a statistical analysis plan, prepare for pre-registration, or develop any experimental methodology for basic science, translational research, or clinical investigation.
---

# Experimental Design Specialist

Design rigorous, reproducible experiments and analyses across wet lab, computational, observational, and interventional domains. Inspired by AI Scientist's experiment loop and the need for pre-registration-quality experimental plans, this skill produces comprehensive study designs that anticipate reviewer objections, specify statistical analysis plans before data collection, and meet reporting guideline standards (CONSORT, STROBE, ARRIVE, PRISMA, MDAR).

Covers the full spectrum: from in vitro assay optimization and animal model selection through computational simulation design and ML benchmarking to Phase I-IV clinical trial protocols. Each design follows an 8-phase process that ensures no critical element is overlooked.

## Report-First Workflow

1. **Create report file immediately**: `[study_title]_experimental_design.md` with all section headers
2. **Add placeholders**: Mark each section `[Designing...]`
3. **Populate progressively**: Update sections as literature evidence is gathered and design decisions are made
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Designing...]` placeholders remain

## When NOT to Use This Skill

- Evaluating an EXISTING study's methodology or quality -> use `scientific-critical-thinking`
- Generating novel hypotheses from data or observations -> use `hypothesis-generation`
- Writing a clinical trial protocol for regulatory submission -> use `clinical-trial-protocol-designer`
- Complex statistical modeling, regression, or machine learning -> use `statistical-modeling`
- Systematic literature review and meta-analysis -> use `systematic-literature-reviewer`
- Drafting manuscripts, abstracts, or scientific papers -> use `scientific-writing`
- Deep investigation of a research question -> use `literature-deep-research`
- Biomarker identification and validation strategy -> use `biomarker-discovery`

## Cross-Skill Routing

- **Hypothesis formulation before design** -> use `hypothesis-generation` to generate and rank competing hypotheses, then bring the top hypothesis here for experimental design
- **Evaluating a completed study** -> use `scientific-critical-thinking` for post-hoc methodology critique
- **Statistical test selection and implementation** -> use `statistical-modeling` for complex analyses beyond the SAP templates provided here
- **Clinical trial regulatory strategy** -> use `fda-consultant` for IND/NDA regulatory pathway considerations
- **Target validation evidence** -> use `drug-target-validator` for druggability scoring before designing validation experiments
- **Biomarker selection for endpoints** -> use `biomarker-discovery` for identifying candidate biomarkers to use as study endpoints
- **Competitive landscape for study justification** -> use `competitive-intelligence` for therapeutic area context
- **Questioning assumptions in the design** -> use `socratic-inquiry` to stress-test design choices through guided questioning

---

## Available MCP Tools

### `mcp__pubmed__pubmed_data` (Literature Evidence for Design Decisions)

| Method | Design use | Key parameters |
|--------|-----------|----------------|
| `search_keywords` | Find prior studies to inform effect size estimates | `keywords`, `num_results` |
| `search_advanced` | Search for methodology papers, power analyses, pilot data | `term`, `journal`, `start_date`, `end_date`, `num_results` |
| `get_article_metadata` | Extract sample sizes, effect sizes, endpoints from published studies | `pmid` |

### `mcp__biorxiv__biorxiv_data` (Emerging Methods & Preprints)

| Method | Design use | Key parameters |
|--------|-----------|----------------|
| `search_preprints` | Find cutting-edge methodologies and assays | `query`, `server`, `limit` |
| `get_preprint_details` | Review novel experimental approaches | `doi` |

### `mcp__ctgov__ctgov_data` (Clinical Trial Registry)

| Method | Design use | Key parameters |
|--------|-----------|----------------|
| `search` | Find comparable trial designs for benchmarking | `query`, `num_results` |
| `get` | Extract endpoints, sample sizes, inclusion criteria from registered trials | `nct_id` |

### `mcp__opentargets__opentargets_data` (Target-Disease Evidence)

| Method | Design use | Key parameters |
|--------|-----------|----------------|
| `search_targets` | Identify validated targets for experimental focus | `query`, `size` |
| `get_target_disease_associations` | Assess evidence strength to justify study rationale | `targetId`, `diseaseId`, `minScore` |

### `mcp__chembl__chembl_data` (Compound & Bioactivity Data)

| Method | Design use | Key parameters |
|--------|-----------|----------------|
| `compound_search` | Find tool compounds and positive controls | `query`, `limit` |
| `get_bioactivity` | Determine dose ranges from existing activity data | `chembl_id`, `target_id` |

### `mcp__reactome__reactome_data` (Pathway Context)

| Method | Design use | Key parameters |
|--------|-----------|----------------|
| `search_pathways` | Identify pathways for mechanistic endpoints | `query`, `limit` |
| `get_pathway_participants` | Define pathway readouts and gene panels | `pathway_id` |

---

## Phase 1: Research Question Formulation

### PICO Framework (Clinical/Translational)

| Element | Definition | Example |
|---------|-----------|---------|
| **P** (Population) | Who are the subjects? | Adults with treatment-resistant depression |
| **I** (Intervention) | What is being tested? | Psilocybin-assisted therapy (25 mg, single dose) |
| **C** (Comparator) | What is the control? | Niacin placebo + therapy |
| **O** (Outcome) | What is being measured? | MADRS score change at 6 weeks |

### FINER Criteria (Research Question Quality)

| Criterion | Question | Assessment |
|-----------|----------|------------|
| **F** (Feasible) | Can we actually do this study? | Sample availability, budget, timeline, expertise |
| **I** (Interesting) | Does this matter to the field? | Gap in literature, clinical need, scientific novelty |
| **N** (Novel) | Does this add new knowledge? | Not merely replicating known results (unless replication is the point) |
| **E** (Ethical) | Can this be done ethically? | IRB/IACUC approval, risk-benefit balance, informed consent |
| **R** (Relevant) | Will results change practice or understanding? | Clinical impact, mechanistic insight, policy implications |

### Question Type Classification

**Exploratory questions** (hypothesis-generating):
- "What genes are differentially expressed in [condition]?"
- "Is there an association between [exposure] and [outcome]?"
- Appropriate for: pilot studies, discovery screens, cross-sectional surveys
- Statistical approach: correction for multiple comparisons, FDR control

**Confirmatory questions** (hypothesis-testing):
- "Does [intervention] reduce [outcome] compared to [control]?"
- "Is [biomarker] predictive of [response] with AUC > 0.80?"
- Appropriate for: powered studies, pre-registered analyses, clinical trials
- Statistical approach: pre-specified primary analysis, alpha spending

### Hypothesis Specification

```
Primary Hypothesis (H1): [Specific, directional, quantifiable]
  Example: "Compound X at 10 mg/kg reduces tumor volume by >= 40% compared
  to vehicle at day 21 in the CT26 syngeneic model."

Null Hypothesis (H0): [Negation of H1]
  Example: "Compound X at 10 mg/kg does not reduce tumor volume by >= 40%
  compared to vehicle at day 21."

Positive result looks like: [Specific threshold or effect]
  Example: "Statistically significant reduction (p < 0.05) with >= 40%
  tumor growth inhibition."

Negative result looks like: [What would refute the hypothesis]
  Example: "No significant difference, or < 20% tumor growth inhibition."

Inconclusive result looks like: [What would require follow-up]
  Example: "20-39% inhibition — suggestive but underpowered for detection."
```

---

## Phase 2: Study Design Selection

### Design Decision Matrix

| Design Type | Best For | Internal Validity | External Validity | Time | Cost | Key Limitation |
|-------------|---------|-------------------|-------------------|------|------|----------------|
| **In vitro assay** | Mechanism, dose-response, screening | Moderate | Low (cell vs. organism) | Days-weeks | Low | Limited physiological relevance |
| **Animal model** | Efficacy, PK/PD, toxicology | Moderate-High | Moderate (species gap) | Weeks-months | Moderate | Species translation uncertainty |
| **Organoid/3D culture** | Patient-derived responses, heterogeneity | Moderate | Moderate | Weeks | Moderate | Lacks immune/stromal context |
| **Cell line panel** | Biomarker-response correlation | Moderate | Low | Weeks | Low-Moderate | Selection bias in available lines |
| **Simulation/modeling** | Parameter exploration, prediction | High (within model) | Depends on validation | Days-weeks | Low | Model assumptions limit generalizability |
| **ML benchmark** | Algorithm comparison | High (if proper splits) | Depends on data representativeness | Days-weeks | Low-Moderate | Overfitting, data leakage risk |
| **Bioinformatics pipeline** | Omics data analysis | Moderate | Depends on cohort | Days-weeks | Low | Batch effects, normalization choices |
| **RCT (parallel)** | Causal inference, treatment effect | Highest | Moderate (eligibility) | Months-years | Highest | Expense, feasibility, ethical constraints |
| **RCT (crossover)** | Within-subject comparison | Very High | Moderate | Months-years | High | Carryover effects, dropout |
| **RCT (factorial)** | Multiple interventions simultaneously | High | Moderate | Months-years | High | Interaction effects, complexity |
| **RCT (adaptive)** | Dose-finding, biomarker-guided | High | Moderate | Months-years | High | Operational complexity, type I error control |
| **Single-arm trial** | Rare diseases, dramatic effects | Low-Moderate | Moderate | Months | Moderate | No concurrent control, regression to mean |
| **Dose-escalation (3+3, CRM)** | Phase I safety/MTD | Low (not powered for efficacy) | Low | Months | Moderate | Small sample, limited efficacy data |
| **Cohort (prospective)** | Risk factors, natural history | Moderate-High | High | Years | High | Confounding, loss to follow-up |
| **Cohort (retrospective)** | Rare exposures, long latency | Moderate | Moderate | Weeks-months | Moderate | Information bias, incomplete records |
| **Case-control** | Rare outcomes | Moderate | Limited | Months | Moderate | Recall bias, selection bias |
| **Cross-sectional** | Prevalence, associations | Low | High | Weeks-months | Low-Moderate | Cannot establish causation |
| **Translational (bench-to-bedside)** | Mechanism to therapy | Variable | Variable | Years | Highest | Complexity, multiple failure points |
| **Multi-omics integration** | Systems-level understanding | Variable | Variable | Months | High | Batch effects, statistical complexity |

### Design Selection Flowchart

```
Is the goal to establish causation?
  YES -> Is random assignment feasible and ethical?
    YES -> RCT (choose subtype: parallel, crossover, factorial, adaptive)
    NO  -> Observational design (cohort, case-control, or cross-sectional)
  NO  -> Is the goal to explore mechanisms or generate hypotheses?
    YES -> Is human tissue/data required?
      YES -> Observational or translational design
      NO  -> Wet lab (in vitro, animal model) or computational
    NO  -> Is the goal to validate a computational method?
      YES -> ML benchmark or simulation study
      NO  -> Descriptive or ecological study
```

---

## Phase 3: Variable Specification

### Variable Taxonomy

```
INDEPENDENT VARIABLES (what we manipulate or compare):
  - Treatment vs. control
  - Dose levels (e.g., 1 mg, 5 mg, 10 mg, vehicle)
  - Genotype groups (e.g., WT vs. KO)
  - Time points (e.g., 0h, 6h, 24h, 72h)
  - Computational parameters (e.g., learning rate, architecture)

DEPENDENT VARIABLES (what we measure):
  - Primary: the main outcome that tests the hypothesis
  - Secondary: supportive outcomes that add context
  - Exploratory: hypothesis-generating measurements

CONFOUNDERS (what could explain results besides our hypothesis):
  - Biological: age, sex, weight, genetic background, comorbidities
  - Technical: batch effects, operator variability, plate position effects
  - Environmental: temperature, time of day, cage effects (animal studies)
  - Computational: data leakage, hyperparameter tuning on test set

CONTROL STRATEGIES:
  - Randomization: eliminates known and unknown confounders
  - Matching: pair subjects on key confounders
  - Stratification: ensure balance on known confounders
  - Statistical adjustment: include confounders as covariates
  - Blocking: reduce variability by grouping similar units
```

### Positive and Negative Controls

| Control Type | Purpose | Example |
|-------------|---------|---------|
| **Positive control** | Confirm assay is working | Known active compound at validated concentration |
| **Negative control** | Establish baseline signal | Vehicle/DMSO, scrambled siRNA, isotype antibody |
| **Technical replicate** | Assess measurement variability | Same sample measured multiple times |
| **Biological replicate** | Assess biological variability | Independent cell passages, different animals |
| **Batch control** | Detect batch effects | Reference sample included in every batch |
| **Sham control** | Control for procedure effects | Surgery without intervention |

---

## Phase 4: Sample Size and Power Analysis

### Effect Size Estimation Strategy

1. **From prior literature**: Search PubMed for comparable studies, extract effect sizes
2. **From pilot data**: Run preliminary experiment (n=3-5 per group minimum)
3. **From clinical significance**: Define the minimum clinically important difference (MCID)
4. **From practical constraints**: What effect size can we detect given available resources?

### Power Analysis Python Code Templates

#### Two-Group Comparison (t-test)

```python
import numpy as np
from scipy import stats

def power_analysis_ttest(effect_size_d, alpha=0.05, power=0.80, ratio=1.0):
    """
    Calculate sample size for two-group comparison.

    Parameters:
        effect_size_d: Cohen's d (small=0.2, medium=0.5, large=0.8)
        alpha: significance level (two-sided)
        power: desired statistical power
        ratio: n2/n1 ratio (1.0 for equal groups)

    Returns:
        n1, n2: sample sizes per group
    """
    from scipy.stats import norm

    z_alpha = norm.ppf(1 - alpha / 2)
    z_beta = norm.ppf(power)

    n1 = ((z_alpha + z_beta) ** 2 * (1 + 1/ratio)) / (effect_size_d ** 2)
    n2 = n1 * ratio

    return int(np.ceil(n1)), int(np.ceil(n2))

# Example: Detect Cohen's d = 0.5, alpha = 0.05, power = 0.80
n1, n2 = power_analysis_ttest(effect_size_d=0.5)
print(f"Required: n1={n1}, n2={n2}, total={n1+n2}")
```

#### ANOVA (Multiple Groups)

```python
def power_analysis_anova(k, effect_size_f, alpha=0.05, power=0.80):
    """
    Calculate sample size for k-group ANOVA.

    Parameters:
        k: number of groups
        effect_size_f: Cohen's f (small=0.10, medium=0.25, large=0.40)
        alpha: significance level
        power: desired power

    Returns:
        n_per_group: sample size per group
    """
    from scipy.stats import ncf, f as f_dist

    # Iterative approach
    for n in range(5, 10000):
        df1 = k - 1
        df2 = k * n - k
        lambda_nc = n * k * effect_size_f ** 2  # noncentrality parameter
        f_crit = f_dist.ppf(1 - alpha, df1, df2)
        achieved_power = 1 - ncf.cdf(f_crit, df1, df2, lambda_nc)
        if achieved_power >= power:
            return n
    return None

# Example: 4 groups, medium effect, alpha=0.05, power=0.80
n = power_analysis_anova(k=4, effect_size_f=0.25)
print(f"Required: n={n} per group, total={n*4}")
```

#### Chi-Square / Proportions

```python
def power_analysis_proportions(p1, p2, alpha=0.05, power=0.80, ratio=1.0):
    """
    Calculate sample size for comparing two proportions.

    Parameters:
        p1: expected proportion in group 1
        p2: expected proportion in group 2
        alpha: significance level (two-sided)
        power: desired power
        ratio: n2/n1 ratio
    """
    from scipy.stats import norm

    z_alpha = norm.ppf(1 - alpha / 2)
    z_beta = norm.ppf(power)

    p_bar = (p1 + ratio * p2) / (1 + ratio)

    n1 = ((z_alpha * np.sqrt((1 + 1/ratio) * p_bar * (1 - p_bar)) +
           z_beta * np.sqrt(p1*(1-p1) + p2*(1-p2)/ratio)) ** 2) / (p1 - p2) ** 2
    n2 = n1 * ratio

    return int(np.ceil(n1)), int(np.ceil(n2))

# Example: Response rate 30% vs 50%
n1, n2 = power_analysis_proportions(p1=0.30, p2=0.50)
print(f"Required: n1={n1}, n2={n2}, total={n1+n2}")
```

#### Survival Analysis (Log-Rank)

```python
def power_analysis_survival(hr, alpha=0.05, power=0.80, ratio=1.0,
                             median_control=12, accrual_time=24, followup_time=12):
    """
    Calculate sample size for survival comparison (log-rank test).

    Parameters:
        hr: hazard ratio to detect
        median_control: median survival in control group (months)
        accrual_time: enrollment period (months)
        followup_time: minimum follow-up after last enrollment (months)
    """
    from scipy.stats import norm

    z_alpha = norm.ppf(1 - alpha / 2)
    z_beta = norm.ppf(power)

    # Schoenfeld formula for required events
    d = ((z_alpha + z_beta) ** 2 * (1 + ratio) ** 2) / (ratio * (np.log(hr)) ** 2)
    d = int(np.ceil(d))

    # Estimate total N accounting for event probability
    lambda_c = np.log(2) / median_control
    lambda_t = lambda_c * hr

    # Probability of event (simplified uniform accrual)
    total_time = accrual_time + followup_time
    p_event_c = 1 - np.exp(-lambda_c * followup_time)
    p_event_t = 1 - np.exp(-lambda_t * followup_time)
    p_event_avg = (p_event_c + ratio * p_event_t) / (1 + ratio)

    total_n = int(np.ceil(d / p_event_avg))

    return total_n, d

# Example: Detect HR=0.70, median control=12 months
total_n, events = power_analysis_survival(hr=0.70, median_control=12)
print(f"Required: N={total_n}, events needed={events}")
```

### Sample Size Adjustment Factors

| Factor | Adjustment | Typical Range |
|--------|-----------|---------------|
| **Dropout/attrition** | N_adjusted = N / (1 - dropout_rate) | 10-30% dropout |
| **Non-compliance** | N_adjusted = N / (compliance_rate^2) | 70-90% compliance |
| **Multiple comparisons** | Bonferroni: alpha_adj = alpha / k | Depends on k |
| **Interim analyses** | O'Brien-Fleming or Lan-DeMets alpha spending | 1-3 interim looks |
| **Subgroup analyses** | Each subgroup needs independent powering | 2-4 subgroups |
| **Cluster design** | N_adjusted = N * (1 + (m-1) * ICC) | ICC = 0.01-0.10 |

---

## Phase 5: Randomization and Blinding

### Randomization Methods

| Method | When to Use | Implementation |
|--------|-------------|----------------|
| **Simple randomization** | Large trials (N > 200) | `np.random.choice(['A','B'], size=N)` |
| **Block randomization** | Ensure balanced allocation | Blocks of 4 or 6, permuted within blocks |
| **Stratified randomization** | Known prognostic factors | Separate randomization within each stratum |
| **Minimization** | Small trials with many prognostic factors | Adaptive algorithm minimizing imbalance |
| **Adaptive randomization** | Dose-finding, response-adaptive | Bayesian or frequentist response-adaptive |
| **Cluster randomization** | Group-level interventions | Randomize clusters, account for ICC |

### Blinding Levels

| Level | Who is Blinded | When Possible | When Not |
|-------|---------------|--------------|----------|
| **Open-label** | Nobody | Surgery, behavioral interventions | -- |
| **Single-blind** | Subjects only | Placebo-controlled drug trials | Obvious intervention differences |
| **Double-blind** | Subjects + investigators | Identical-appearing treatments | Different administration routes |
| **Triple-blind** | Subjects + investigators + analysts | Add blinded statistician | Rarely impractical |
| **Sham-controlled** | Subjects blinded to procedure | Device trials, surgical trials | Ethical concerns with sham surgery |

### When Blinding is Impossible: Mitigations

```
1. Blinded outcome assessment (PROBE design)
   - Outcomes assessed by independent evaluator unaware of allocation

2. Objective endpoints
   - Use lab values, imaging, survival rather than subjective measures

3. Central adjudication
   - Independent committee reviews events blinded to treatment

4. Active comparator
   - Use active control rather than no treatment to reduce bias

5. Pre-specified analysis
   - Remove analyst degrees of freedom through detailed SAP
```

---

## Phase 6: Endpoint Definition

### Endpoint Hierarchy

```
PRIMARY ENDPOINT (one, pre-specified):
  - Must directly test the primary hypothesis
  - Must be clinically meaningful OR a validated surrogate
  - Must have known measurement properties (reliability, validity)
  - Powers the entire study

SECONDARY ENDPOINTS (supportive):
  - Add context or test secondary hypotheses
  - Ordered by importance for multiplicity adjustment
  - May include safety endpoints

EXPLORATORY ENDPOINTS (hypothesis-generating):
  - Not powered for formal testing
  - Inform future studies
  - Omics, biomarker discovery, subgroup patterns
```

### Endpoint Quality Criteria

| Criterion | Assessment Question | Red Flag |
|-----------|-------------------|----------|
| **Validity** | Does it measure what it claims? | Unvalidated composite endpoint |
| **Reliability** | Would repeat measurements agree? | ICC < 0.70 for subjective measures |
| **Sensitivity** | Can it detect the expected change? | Floor/ceiling effects in chosen scale |
| **Clinical relevance** | Does a change matter to patients? | Statistically significant but trivial effect |
| **Timing** | Is assessment timing appropriate? | Measuring chronic effect at acute timepoint |
| **Ascertainment** | Can it be measured consistently? | Different methods across sites |

### Surrogate Endpoint Justification

```
Surrogate: [e.g., tumor response rate (RECIST)]
Clinical endpoint it replaces: [e.g., overall survival]
Validation evidence:
  - Trial-level correlation (R^2): [value, citation]
  - Patient-level correlation (r): [value, citation]
  - Regulatory precedent: [FDA accelerated approval examples]
Justification: [Why surrogate is appropriate for THIS study]
Limitation: [Acknowledge the gap between surrogate and clinical outcome]
```

---

## Phase 7: Statistical Analysis Plan (SAP)

### SAP Template

```
## Statistical Analysis Plan

### 1. Analysis Populations
- Intent-to-Treat (ITT): all randomized subjects
- Modified ITT (mITT): all randomized who received >= 1 dose
- Per-Protocol (PP): all who completed without major violations
- Safety: all who received any study treatment

### 2. Primary Analysis
- Endpoint: [primary endpoint]
- Comparison: [treatment vs. control]
- Test: [e.g., two-sided t-test, log-rank test, mixed model]
- Alpha: [0.05 unless adjusted]
- Missing data: [primary method, e.g., MMRM, multiple imputation]

### 3. Secondary Analyses (hierarchical testing)
- Secondary endpoint 1: [test, only if primary is significant]
- Secondary endpoint 2: [test, only if secondary 1 is significant]
- ...

### 4. Multiple Comparison Correction
- Method: [Bonferroni / Benjamini-Hochberg / hierarchical / gatekeeping]
- Justification: [why this method is appropriate]

### 5. Sensitivity Analyses
- ITT vs. PP: do conclusions differ?
- Missing data: compare MMRM, last observation carried forward, worst case
- Subgroups: [pre-specified subgroup analyses with interaction tests]
- Per-protocol: exclude major protocol violations

### 6. Subgroup Analyses (pre-specified)
- Subgroup 1: [e.g., by sex, age group, biomarker status]
- Analysis: treatment-by-subgroup interaction test
- Interpretation: exploratory, not powered for definitive conclusions

### 7. Interim Analyses (if planned)
- Number of looks: [1-3]
- Timing: [e.g., after 50% of events]
- Stopping boundaries: [O'Brien-Fleming / Lan-DeMets]
- Alpha spent: [cumulative alpha at each look]
- Data Safety Monitoring Board (DSMB): composition and charter
```

### Common Statistical Tests by Study Design

| Design | Primary Analysis | Alternatives |
|--------|-----------------|-------------|
| **Two-group continuous** | Two-sample t-test (normal) | Wilcoxon rank-sum (non-normal) |
| **Two-group binary** | Chi-square / Fisher's exact | Logistic regression (adjusted) |
| **Two-group time-to-event** | Log-rank test | Cox proportional hazards (adjusted) |
| **Multiple groups continuous** | One-way ANOVA | Kruskal-Wallis (non-normal) |
| **Repeated measures** | Mixed-model repeated measures (MMRM) | GEE, repeated-measures ANOVA |
| **Dose-response** | Contrast tests, MCP-Mod | Non-linear regression |
| **Paired / crossover** | Paired t-test | Wilcoxon signed-rank, mixed model |
| **Cluster randomized** | Mixed model with cluster random effect | GEE with robust SE |
| **Adaptive** | Pre-planned adaptive methods | Bayesian adaptive designs |
| **ML benchmark** | Cross-validated performance + bootstrap CI | Permutation test |

---

## Phase 8: Pre-Registration and Reproducibility

### Pre-Registration Checklist (AsPredicted / OSF Format)

```
1. Hypotheses: [exact hypotheses, directional]
2. Dependent variable(s): [how measured, when, by whom]
3. Conditions/Independent variable(s): [all levels, including control]
4. Analyses: [exact statistical test for each hypothesis]
5. Outlier handling: [criteria for exclusion, decided a priori]
6. Sample size: [target N, justification, stopping rule]
7. Other: [anything else pre-specified]
8. Study type: [confirmatory vs. exploratory]
```

### Reporting Guideline Reference

| Guideline | Study Type | Key Requirements | URL |
|-----------|-----------|-----------------|-----|
| **CONSORT** | RCTs | Flow diagram, ITT, blinding, randomization | consort-statement.org |
| **STROBE** | Observational | Eligibility, matching, bias discussion | strobe-statement.org |
| **ARRIVE** | Animal studies | Species, housing, sample size justification | arriveguidelines.org |
| **PRISMA** | Systematic reviews | Search strategy, QUADAS/RoB, forest plots | prisma-statement.org |
| **STARD** | Diagnostic accuracy | Reference standard, 2x2 table, flow diagram | stard-statement.org |
| **TRIPOD** | Prediction models | Model development vs. validation, calibration | tripod-statement.org |
| **MDAR** | Basic research | Reproducibility checklist, materials sharing | -- |
| **SPIRIT** | Trial protocols | Schedule of events, SAP, DSMB charter | spirit-statement.org |
| **MIAME/MINSEQE** | Omics data | Data deposition, normalization, QC metrics | -- |

### Data Management Plan

```
Data collection: [REDCap, electronic CRF, lab notebooks, automated pipelines]
Data storage: [secure server, encrypted, access-controlled]
Data cleaning: [double entry, range checks, logic checks]
Data sharing: [GEO, SRA, Zenodo, Dryad — timeline and conditions]
Code sharing: [GitHub, version-controlled analysis scripts]
Retention: [minimum 10 years post-publication for clinical, per policy]
```

---

## Reviewer Objection Anticipation Framework

For each critical design choice, preemptively prepare a defense:

### Template

```
DESIGN CHOICE: [The choice made]
LIKELY REVIEWER OBJECTION: [What a rigorous reviewer would challenge]
DEFENSE: [Evidence-based justification]
FALLBACK: [What sensitivity analysis addresses this concern]
```

### Common Objection-Defense Pairs

| Design Choice | Typical Objection | Standard Defense |
|---------------|-------------------|-----------------|
| Surrogate endpoint | "Not clinically meaningful" | Cite validation studies, regulatory precedent, feasibility constraints |
| Single-arm design | "No concurrent control" | Cite historical control data, rare disease context, dramatic effect size |
| Small sample size | "Underpowered" | Show power calculation, cite pilot data effect sizes, acknowledge as limitation |
| Animal model choice | "Species X doesn't translate" | Cite translational concordance data, use multiple models |
| In vitro only | "Cell lines don't reflect patients" | Use patient-derived models, validate with clinical data |
| Subgroup analysis | "Post-hoc data dredging" | Pre-specified, interaction test, biological rationale |
| Multiple endpoints | "Multiplicity not addressed" | Hierarchical testing, FDR correction, pre-specification |
| No blinding | "Performance bias" | PROBE design, objective endpoints, central adjudication |
| Short follow-up | "Long-term effects unknown" | Primary endpoint is acute, extension study planned |
| Composite endpoint | "Components differ in importance" | Show each component separately, clinical relevance of composite |

---

## Multi-Agent Workflow Examples

### Example 1: Designing a Target Validation Experiment

**Prompt**: "Design an experiment to validate TREM2 as a therapeutic target for Alzheimer's disease"

**Agent Workflow**:

1. **Literature search** (MCP tools): Query PubMed for "TREM2 Alzheimer's" to gather effect sizes from prior studies, identify established models, and find validated endpoints.

2. **Phase 1 — Research Question**:
   - P: 5xFAD mice (vs. WT littermates), age 6-9 months
   - I: TREM2 agonist antibody (AL002-like)
   - C: Isotype control antibody
   - O: Microglial phagocytosis of amyloid plaques (primary), hippocampal plaque burden, synaptic density (secondary)
   - H1: TREM2 agonism increases microglial plaque engagement by >= 50%

3. **Phase 2 — Design Selection**: Controlled animal study with randomized treatment assignment, stratified by sex.

4. **Phases 3-8**: Variable specification, power analysis (effect size from prior TREM2 studies), blinding (blinded histological assessment), endpoint protocols (immunohistochemistry, confocal quantification), SAP, ARRIVE checklist compliance.

5. **Reviewer objection anticipation**: Prepare defenses for model choice (5xFAD limitations), species translation gap, endpoint timing.

6. **Output**: Complete experimental design document with power calculations, protocols, and pre-registration draft.

### Example 2: Designing a Computational Benchmark Study

**Prompt**: "Design a fair benchmark comparing graph neural networks for drug-target interaction prediction"

**Agent Workflow**:

1. **Phase 1 — Research Question**:
   - Confirmatory: "Does architecture X outperform baselines on DTI prediction across diverse datasets?"
   - H1: Architecture X achieves AUROC >= 0.05 higher than best baseline
   - Define positive/negative/inconclusive thresholds

2. **Phase 2 — Design**: ML benchmark study with proper train/val/test splits.

3. **Phase 3 — Variables**:
   - Independent: model architecture (5 models)
   - Dependent: AUROC, AUPRC, F1, inference time
   - Confounders: hyperparameter tuning budget, random seed, data split

4. **Phase 4 — Power**: Bootstrap analysis of performance distributions, determine number of random seeds needed (typically 5-10) for reliable CI estimation.

5. **Phase 7 — SAP**: Paired comparison via Wilcoxon signed-rank test across datasets, correction for multiple comparisons across model pairs. Pre-specify: no cherry-picking datasets where model X wins.

6. **Anti-leakage checklist**: Temporal split for time-sensitive data, no test set information in feature engineering, separate validation set for hyperparameter tuning.

### Example 3: Designing a Biomarker Discovery Study

**Prompt**: "Design a study to identify circulating biomarkers predictive of immunotherapy response in NSCLC"

**Agent Workflow**:

1. **Phase 1**: Exploratory question with FDR control. PICO: advanced NSCLC patients receiving pembrolizumab, discovery cohort + validation cohort.

2. **Phase 2**: Prospective cohort with discovery-validation design (split-sample or independent cohort).

3. **Phase 3**:
   - Independent: responder vs. non-responder (RECIST 1.1 at 12 weeks)
   - Dependent: circulating protein panel (Olink Explore 3072)
   - Confounders: PD-L1 TPS, TMB, line of therapy, smoking status

4. **Phase 4**: Power analysis for biomarker discovery — based on expected number of true positives, FDR threshold, effect size distribution.

5. **Phase 7 — SAP**: Discovery phase: limma/DESeq2 with BH correction (FDR < 0.10). Validation phase: pre-specified top candidates tested at alpha = 0.05. LASSO/elastic-net for multi-marker panel with nested cross-validation.

6. **Phase 8**: Data to be deposited in GEO/ArrayExpress. Analysis code on GitHub. Pre-registered on OSF.

### Example 4: Designing a Phase II Adaptive Clinical Trial

**Prompt**: "Design an adaptive Phase II trial for a novel CDK4/6 inhibitor in HR+/HER2- breast cancer"

**Agent Workflow**:

1. **ClinicalTrials.gov search** (MCP): Find comparable trials (PALOMA-2, MONARCH-E) for endpoint benchmarks and effect size estimates.

2. **Phase 1**: Confirmatory. PICO: HR+/HER2- metastatic BC, novel CDK4/6i + letrozole vs. letrozole alone, PFS (primary), ORR (secondary).

3. **Phase 2**: Adaptive randomized Phase II with Simon two-stage for futility, response-adaptive randomization.

4. **Phase 4**: Power for PFS — HR = 0.65 based on PALOMA-2 precedent, 80% power, one-sided alpha = 0.025. Required events = 120. Total N approximately 180 accounting for maturation.

5. **Phase 5**: Stratified randomization by prior endocrine therapy (yes/no) and visceral metastases (yes/no). Double-blind.

6. **Phase 6**: Primary: PFS per RECIST 1.1 by blinded independent central review. Secondary: ORR, DOR, OS (immature), safety (CTCAE v5).

7. **Phase 7**: Log-rank test, Cox model, Kaplan-Meier curves. Interim futility at 50% information fraction using Lan-DeMets (O'Brien-Fleming). DSMB review.

8. **Phase 8**: ClinicalTrials.gov registration (SPIRIT-compliant), CONSORT reporting, SAP finalized before database lock.

### Example 5: Designing a Multi-Omics Integration Study

**Prompt**: "Design a multi-omics study to characterize resistance mechanisms in EGFR-mutant lung cancer"

**Agent Workflow**:

1. **Phase 1**: Exploratory. What molecular alterations co-occur with acquired resistance to osimertinib in EGFR-mutant NSCLC?

2. **Phase 2**: Retrospective cohort with paired pre-treatment and progression biopsies. Multi-omics: WES + RNA-seq + phosphoproteomics.

3. **Phase 3**:
   - Independent: timepoint (pre-treatment vs. progression)
   - Dependent: somatic mutations, gene expression, phosphoprotein levels
   - Confounders: biopsy site, tumor purity, sequencing batch

4. **Phase 4**: For WES — 30 pairs detects clonal mutations at >= 10% VAF with 95% sensitivity at 200x depth. For RNA-seq — 30 pairs detects 2-fold changes with 80% power at FDR < 0.05 (based on RNA-seq power calculators). For phosphoproteomics — exploratory, not independently powered.

5. **Phase 7 — SAP**:
   - WES: MuTect2 for somatic calling, dN/dS for selection analysis
   - RNA-seq: DESeq2, GSEA, pathway enrichment
   - Phosphoproteomics: limma, kinase-substrate enrichment (KSEA)
   - Integration: MOFA+ for multi-omics factor analysis, iCluster for subtype discovery
   - Validation: orthogonal cell line models (PC9-OR, H1975)

6. **Phase 8**: Data to GEO (RNA-seq), EGA (WES with controlled access), PRIDE (proteomics). Code on GitHub with Snakemake pipeline. REMARK + MDAR compliance.

---

## Final Report Structure

```markdown
# Experimental Design: [Study Title]

## 1. Research Question
### PICO/FINER Assessment
### Hypothesis (H1 and H0)
### Expected Outcomes (positive, negative, inconclusive)

## 2. Study Design
### Design Type and Justification
### Design Selection Rationale (why this design, why not alternatives)

## 3. Variables
### Independent Variables
### Dependent Variables (primary, secondary, exploratory)
### Confounders and Control Strategy
### Controls (positive, negative, technical)

## 4. Sample Size Justification
### Effect Size Estimation (source and rationale)
### Power Analysis (with Python code)
### Adjustment Factors (dropout, multiplicity, clustering)
### Final Sample Size

## 5. Randomization and Blinding
### Randomization Method
### Blinding Level and Method
### Mitigations (if blinding is impossible)

## 6. Endpoints
### Primary Endpoint (definition, measurement, timing)
### Secondary Endpoints
### Exploratory Endpoints
### Surrogate Endpoint Justification (if applicable)

## 7. Statistical Analysis Plan
### Analysis Populations
### Primary Analysis
### Secondary Analyses (hierarchical)
### Multiple Comparison Correction
### Sensitivity Analyses
### Subgroup Analyses
### Interim Analyses (if planned)
### Missing Data Strategy

## 8. Pre-Registration and Reproducibility
### Pre-Registration Draft (AsPredicted/OSF format)
### Reporting Guideline Compliance
### Data Management Plan
### Code and Data Sharing Plan

## 9. Anticipated Reviewer Objections
| Design Choice | Objection | Defense | Sensitivity Analysis |
|...|...|...|...|

## 10. Timeline and Budget Estimate
### Study Timeline (Gantt-style milestones)
### Key Resources and Estimated Costs

## 11. Limitations and Mitigations
### Known Limitations
### Mitigation Strategies
### What This Study Cannot Answer
```

---

## Completeness Checklist

Before finalizing any experimental design, verify all items:

- [ ] **Research question** stated in PICO or FINER format with clear hypothesis
- [ ] **Study design** selected with explicit justification and alternatives considered
- [ ] **Variables** fully specified — independent, dependent, confounders, controls
- [ ] **Sample size** calculated with documented effect size source, alpha, power, and adjustment factors
- [ ] **Randomization and blinding** strategy specified (or mitigations if not possible)
- [ ] **Primary endpoint** is single, pre-specified, measurable, and clinically meaningful
- [ ] **Statistical analysis plan** pre-specifies primary test, multiplicity correction, sensitivity analyses, and missing data handling
- [ ] **Pre-registration draft** prepared with all key decisions documented before data collection
- [ ] **Reviewer objections** anticipated for each critical design choice with prepared defenses
- [ ] **Reporting guideline** identified (CONSORT, STROBE, ARRIVE, etc.) and compliance verified
