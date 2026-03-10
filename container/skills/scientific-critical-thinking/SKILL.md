---
name: scientific-critical-thinking
description: Systematic scientific rigor evaluation with methodology critique, bias detection, statistical assessment, evidence quality grading (GRADE framework), logical fallacy identification, and research design guidance. Use when asked to evaluate study quality, assess methodology, detect biases in research, critique statistical analyses, evaluate claims or evidence, review experimental designs, or assess the strength of scientific conclusions in drug development, clinical research, or basic science.
---

# Scientific Critical Thinking

Systematic frameworks for evaluating scientific evidence, detecting biases, and assessing research quality. Provides structured methodology critique, statistical assessment, evidence grading, and logical fallacy identification across drug development, clinical research, and basic science.

## Report-First Workflow

1. **Create report file immediately**: `[topic]_critical_analysis_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill

- Conducting a full PRISMA systematic review → use `systematic-literature-reviewer`
- Variant pathogenicity or genomic interpretation → use `variant-interpretation`
- Writing a clinical trial protocol from scratch → use `clinical-trial-protocol-designer`
- Post-market drug safety signal detection → use `pharmacovigilance-specialist`
- Complex statistical modeling or regression → use `statistical-modeling`
- Drafting manuscripts or scientific writing → use `scientific-writing`

## Cross-Reference: Other Skills

- **Systematic literature search and PRISMA** → use systematic-literature-reviewer skill
- **Variant pathogenicity assessment** → use variant-interpretation skill
- **Clinical trial protocol design** → use clinical-trial-protocol-designer skill
- **Drug safety signal assessment** → use pharmacovigilance-specialist skill
- **Statistical modeling and regression** → use statistical-modeling skill
- **Manuscript drafting and revision** → use scientific-writing skill

## Available MCP Tools

### `mcp__pubmed__pubmed_data`

| Method | Critical thinking use |
|--------|----------------------|
| `search_keywords` | Retrieve studies for quality evaluation |
| `search_advanced` | Targeted search for replication studies, methodology papers |
| `get_article_metadata` | Full study details for methodology critique |

### `mcp__biorxiv__biorxiv_data`

| Method | Critical thinking use |
|--------|----------------------|
| `search_preprints` | Identify preprints for peer-review quality assessment |
| `get_preprint_details` | Check preprint methodology before peer review |

### `mcp__ctgov__ctgov_data`

| Method | Critical thinking use |
|--------|----------------------|
| `search` | Retrieve trial design details for methodology critique |
| `get` | Full trial protocol for design evaluation |

### `mcp__opentargets__opentargets_data`

| Method | Critical thinking use |
|--------|----------------------|
| `get_target_disease_associations` | Assess overall evidence quality for a target-disease pair |
| `get_disease_details` | Evidence landscape and quality scores |

### `mcp__cbioportal__cbioportal_data`

| Method | Critical thinking use |
|--------|----------------------|
| `get_study_summary` | Validate study data availability and cohort details |
| `get_clinical_data` | Cross-check reported clinical characteristics |

---

## Core Capability 1: Methodology Critique

### Study Design Evaluation Matrix

| Design | Internal Validity | External Validity | Bias Susceptibility | Best For |
|--------|------------------|-------------------|---------------------|----------|
| **Systematic Review / Meta-Analysis** | Highest (aggregated) | Depends on included studies | Publication bias, inclusion criteria bias | Summarizing evidence base |
| **Randomized Controlled Trial (RCT)** | High | Moderate (strict eligibility) | Performance, attrition | Causal inference for interventions |
| **Prospective Cohort** | Moderate-High | High (real-world) | Confounding, selection | Natural history, risk factors |
| **Retrospective Cohort** | Moderate | Moderate | Recall, information bias | Rare exposures, long latency |
| **Case-Control** | Moderate | Limited | Recall bias, selection bias | Rare outcomes |
| **Cross-Sectional** | Low | High (prevalence) | Temporal ambiguity | Prevalence, hypothesis generation |
| **Case Series / Report** | Very Low | Very Low | No comparison group | Rare events, hypothesis generation |
| **Ecological Study** | Very Low | Limited | Ecological fallacy | Hypothesis generation only |
| **In Vitro / Animal** | N/A (pre-clinical) | Not applicable to humans | Species differences, dosing | Mechanism exploration |

### Design Assessment Checklist

#### Randomization Quality
- [ ] Method of sequence generation described (computer-generated, block, stratified)
- [ ] Allocation concealment mechanism specified (central, sealed envelopes)
- [ ] Baseline characteristics balanced across arms
- [ ] Stratification factors appropriate for known prognostic variables

#### Control Adequacy
- [ ] Control group appropriate (placebo, active comparator, standard of care)
- [ ] Justification for control choice documented
- [ ] Equipoise argument valid (genuine uncertainty exists)
- [ ] Hawthorne effect considered in unblinded designs

#### Blinding Assessment
- [ ] Participant blinding achieved and maintained
- [ ] Investigator/assessor blinding implemented
- [ ] Outcome assessor blinding for subjective endpoints
- [ ] Statistical analyst blinding until database lock
- [ ] Unblinding events documented and justified

#### Measurement Quality
- [ ] Primary outcome measure validated in study population
- [ ] Measurement instruments reliability established (kappa, ICC)
- [ ] Assessment schedule consistent across arms
- [ ] Surrogate endpoints have established surrogacy relationship
- [ ] Minimal clinically important difference (MCID) defined

#### Sampling Strategy
- [ ] Target population clearly defined
- [ ] Sampling method appropriate (random, consecutive, convenience)
- [ ] Sample representative of target population
- [ ] Inclusion/exclusion criteria justified and not overly restrictive
- [ ] Generalizability limitations acknowledged

---

## Core Capability 2: Bias Detection

### Cognitive Biases in Research

| Bias | Definition | Example in Research | Detection Strategy |
|------|-----------|--------------------|--------------------|
| **Confirmation bias** | Seeking/favoring evidence that confirms prior beliefs | Selectively citing studies supporting hypothesis | Check citation balance; look for disconfirming evidence cited |
| **Anchoring bias** | Over-relying on first piece of information encountered | Setting effect size expectations from pilot study | Verify assumptions against independent data sources |
| **Availability bias** | Overweighting easily recalled examples | Overestimating drug efficacy from memorable case | Check systematic data vs anecdotal claims |
| **Dunning-Kruger effect** | Overconfidence in areas of limited expertise | Statistician interpreting clinical significance | Verify domain expertise matches claims made |
| **Sunk cost fallacy** | Continuing investment based on past costs | Continuing failed trial due to development investment | Evaluate current evidence independent of investment history |
| **Bandwagon effect** | Adopting beliefs because others do | Following research trends without critical assessment | Evaluate evidence independent of popularity |
| **Optimism bias** | Overestimating favorable outcomes | Overpredicting treatment response rates | Compare predictions against historical base rates |

### Study-Level Biases

| Bias Category | Specific Bias | Definition | Pharma Research Example |
|---------------|--------------|-----------|------------------------|
| **Selection** | Sampling bias | Non-representative sample | Enrolling only treatment-responsive patients |
| **Selection** | Volunteer bias | Participants differ from non-volunteers | Healthier patients volunteer for exercise trials |
| **Selection** | Berkson's bias | Hospital-based selection distorts associations | Case-control studies using hospitalized controls |
| **Selection** | Collider bias | Conditioning on a common effect of exposure and outcome | Restricting analysis to hospitalized COVID patients |
| **Measurement** | Recall bias | Differential recall between groups | Cases remember exposures better than controls |
| **Measurement** | Observer bias | Knowledge of group influences assessment | Unblinded radiologist reading scans |
| **Measurement** | Misclassification | Incorrect categorization of exposure/outcome | Using ICD codes for complex diagnoses |
| **Measurement** | Lead-time bias | Earlier detection appears to prolong survival | Screening-detected cancers vs symptomatic detection |
| **Measurement** | Length-time bias | Screening preferentially detects slow-growing disease | Cancer screening overestimating benefit |
| **Analysis** | p-hacking | Manipulating analysis to achieve significance | Testing multiple statistical tests, reporting only p<0.05 |
| **Analysis** | HARKing | Hypothesizing After Results are Known | Presenting post-hoc findings as pre-specified |
| **Analysis** | Garden of forking paths | Multiple undisclosed analytical decisions | Choosing covariates, cutpoints, subgroups after seeing data |
| **Analysis** | Outcome switching | Changing primary outcome after data collection | Switching from OS to PFS when OS is negative |
| **Confounding** | Confounding by indication | Treatment choice related to prognosis | Sicker patients receive more aggressive treatment |
| **Confounding** | Time-varying confounding | Confounders change during follow-up | Treatment changes based on evolving biomarkers |
| **Confounding** | Residual confounding | Unmeasured or poorly measured confounders | Observational studies of lifestyle interventions |
| **Publication** | Publication bias | Positive results preferentially published | File-drawer effect for negative trials |
| **Publication** | Reporting bias | Selective outcome reporting | Omitting non-significant secondary endpoints |
| **Temporal** | Survivorship bias | Only successful cases visible | Analyzing only patients who completed treatment |
| **Temporal** | Immortal time bias | Misclassifying pre-treatment time as treated | New-user design violation in database studies |
| **Temporal** | Protopathic bias | Exposure caused by early disease symptoms | Drug started for early symptoms misattributed as cause |

### Bias Detection Workflow

```
For each study under evaluation:

1. IDENTIFY study design
   → Select appropriate bias checklist (RCT vs observational vs other)

2. ASSESS selection mechanisms
   → How were participants identified?
   → What were inclusion/exclusion criteria?
   → Were there differences between enrolled and eligible populations?

3. EVALUATE measurement procedures
   → Were outcomes assessed blindly?
   → Were validated instruments used?
   → Were assessment schedules identical across groups?

4. SCRUTINIZE analysis decisions
   → Was the analysis plan pre-registered?
   → Were all pre-specified outcomes reported?
   → Were subgroup analyses pre-specified?
   → Check ClinicalTrials.gov for protocol amendments:
     mcp__ctgov__ctgov_data(method: "get", nctId: "NCTxxxxxxxx")
     → Compare registered endpoints vs published endpoints

5. ASSESS confounding control
   → What adjustment methods were used?
   → Were key confounders measured and controlled?
   → Was there evidence of unmeasured confounding?

6. CHECK for publication/reporting bias
   → Search for registered but unpublished trials
   → Look for selective outcome reporting
   → Assess funnel plot asymmetry if multiple studies
```

---

## Core Capability 3: Statistical Assessment

### Sample Size Adequacy

| Study Type | Minimum for Feasibility | Adequate for Reliable Inference | Gold Standard |
|-----------|------------------------|-------------------------------|---------------|
| Phase 1 dose-escalation | 15-30 | 30-60 (3+3 or CRM) | mTPI/BOIN with 40+ |
| Phase 2 single-arm | 20-40 | 50-100 (Simon two-stage) | Randomized Phase 2 (100-200) |
| Phase 3 RCT | Power calculation required | 80% power at clinically meaningful effect | 90% power with interim analyses |
| Observational cohort | Events-per-variable >= 10 | EPV >= 20 | EPV >= 50 |
| Diagnostic accuracy | 30 per group minimum | Based on expected sensitivity/specificity | Prospective with consecutive enrollment |

### Statistical Test Selection Decision Tree

```
What type of outcome?
├── Continuous
│   ├── 2 groups
│   │   ├── Normal distribution? → Independent t-test (or paired t-test)
│   │   └── Non-normal? → Mann-Whitney U (or Wilcoxon signed-rank)
│   ├── >2 groups
│   │   ├── Normal? → ANOVA (one-way or repeated measures)
│   │   └── Non-normal? → Kruskal-Wallis (or Friedman)
│   └── Association with another continuous variable
│       ├── Linear relationship? → Pearson correlation / Linear regression
│       └── Non-linear or ordinal? → Spearman correlation
├── Binary / Categorical
│   ├── 2x2 table
│   │   ├── Expected counts >= 5? → Chi-squared test
│   │   └── Expected counts < 5? → Fisher's exact test
│   ├── Paired binary → McNemar's test
│   ├── Ordinal outcome → Cochran-Armitage trend test
│   └── Multiple predictors → Logistic regression
├── Time-to-Event
│   ├── Compare groups → Log-rank test (if PH holds)
│   ├── Adjusted analysis → Cox proportional hazards
│   ├── PH violated? → Restricted Mean Survival Time (RMST)
│   └── Competing risks? → Fine-Gray model or cause-specific hazards
└── Count Data
    ├── Equidispersion? → Poisson regression
    └── Overdispersion? → Negative binomial regression
```

### Common Statistical Errors to Flag

| Error | What's Wrong | Correct Approach |
|-------|-------------|-----------------|
| Multiple t-tests instead of ANOVA | Inflated Type I error | ANOVA with post-hoc correction |
| No correction for multiple comparisons | False positives expected | Bonferroni, Holm, Benjamini-Hochberg |
| p-value as effect size | Statistical != clinical significance | Report effect sizes with confidence intervals |
| Reporting only p < 0.05 vs p >= 0.05 | Dichotomizing continuous evidence | Report exact p-values and effect sizes |
| Using parametric tests on skewed data | Violated assumptions | Transform data or use non-parametric alternatives |
| Ignoring clustering/nesting | Underestimated standard errors | Mixed-effects models, GEE |
| Stepwise variable selection | Overfitting, biased estimates | Pre-specified models, penalized regression (LASSO) |
| Excluding outliers without justification | Data manipulation | Sensitivity analysis with and without outliers |
| Interpreting non-significance as no effect | Absence of evidence != evidence of absence | Equivalence testing, confidence interval interpretation |
| Per-protocol instead of ITT analysis | Breaks randomization | ITT as primary, per-protocol as sensitivity |
| Ignoring missing data or using complete case | Biased estimates if data not MCAR | Multiple imputation, mixed models for repeated measures |
| Regression to the mean | Extreme values naturally move toward mean | Control group, ANCOVA |

### Effect Size Calculations (Python)

```python
"""Effect size calculations for critical evaluation of research findings."""
import numpy as np
from scipy import stats

def cohens_d(group1, group2):
    """
    Cohen's d for independent samples.
    Interpretation: 0.2 = small, 0.5 = medium, 0.8 = large (Cohen 1988)
    """
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    d = (np.mean(group1) - np.mean(group2)) / pooled_std

    # 95% CI for Cohen's d (Hedges & Olkin approximation)
    se_d = np.sqrt((n1 + n2) / (n1 * n2) + d**2 / (2 * (n1 + n2)))
    ci_low = d - 1.96 * se_d
    ci_high = d + 1.96 * se_d

    return {"d": round(d, 4), "CI_95": (round(ci_low, 4), round(ci_high, 4)),
            "interpretation": "small" if abs(d) < 0.5 else "medium" if abs(d) < 0.8 else "large"}

def hedges_g(group1, group2):
    """
    Hedges' g: bias-corrected Cohen's d for small samples (n < 20).
    Preferred over Cohen's d when sample sizes are unequal or small.
    """
    result = cohens_d(group1, group2)
    n1, n2 = len(group1), len(group2)
    df = n1 + n2 - 2
    correction = 1 - (3 / (4 * df - 1))  # Hedges correction factor
    g = result["d"] * correction
    ci_low = result["CI_95"][0] * correction
    ci_high = result["CI_95"][1] * correction
    return {"g": round(g, 4), "CI_95": (round(ci_low, 4), round(ci_high, 4)),
            "correction_factor": round(correction, 4)}

def odds_ratio(a, b, c, d):
    """
    Odds ratio from 2x2 contingency table.
          Outcome+  Outcome-
    Exp+     a         b
    Exp-     c         d

    Interpretation: OR=1 no association, OR>1 positive, OR<1 protective
    """
    or_val = (a * d) / (b * c) if (b * c) != 0 else float('inf')
    log_or = np.log(or_val) if or_val > 0 and or_val != float('inf') else float('nan')
    se_log_or = np.sqrt(1/a + 1/b + 1/c + 1/d) if all(v > 0 for v in [a,b,c,d]) else float('nan')
    ci_low = np.exp(log_or - 1.96 * se_log_or)
    ci_high = np.exp(log_or + 1.96 * se_log_or)
    return {"OR": round(or_val, 4), "CI_95": (round(ci_low, 4), round(ci_high, 4)),
            "log_OR": round(log_or, 4), "SE_log_OR": round(se_log_or, 4)}

def number_needed_to_treat(event_rate_control, event_rate_treatment):
    """
    NNT: number of patients to treat to prevent one additional adverse event.
    NNT < 10 generally considered clinically meaningful.
    Negative NNT = NNH (number needed to harm).
    """
    ard = event_rate_control - event_rate_treatment  # Absolute Risk Difference
    nnt = 1 / ard if ard != 0 else float('inf')
    # 95% CI using Wald method (approximate)
    se_ard = np.sqrt(event_rate_control * (1 - event_rate_control) / 100 +
                     event_rate_treatment * (1 - event_rate_treatment) / 100)
    ci_low_ard = ard - 1.96 * se_ard
    ci_high_ard = ard + 1.96 * se_ard
    ci_low_nnt = 1 / ci_high_ard if ci_high_ard != 0 else float('inf')
    ci_high_nnt = 1 / ci_low_ard if ci_low_ard != 0 else float('inf')
    return {"NNT": round(nnt, 1), "ARD": round(ard, 4),
            "CI_95_NNT": (round(ci_low_nnt, 1), round(ci_high_nnt, 1)),
            "interpretation": "NNT" if nnt > 0 else "NNH"}
```

### Power Analysis (Python)

```python
"""Power analysis for evaluating whether studies were adequately powered."""
from scipy import stats
import numpy as np

def power_two_sample_ttest(n1, n2, effect_size, alpha=0.05, alternative="two-sided"):
    """
    Post-hoc power for two-sample t-test.
    Use to evaluate if a non-significant result was due to inadequate power.

    Parameters:
        n1, n2: sample sizes per group
        effect_size: Cohen's d (standardized mean difference)
        alpha: significance level
        alternative: 'two-sided', 'greater', 'less'
    """
    df = n1 + n2 - 2
    ncp = effect_size * np.sqrt(n1 * n2 / (n1 + n2))  # non-centrality parameter

    if alternative == "two-sided":
        critical_t = stats.t.ppf(1 - alpha / 2, df)
        power = 1 - stats.nct.cdf(critical_t, df, ncp) + stats.nct.cdf(-critical_t, df, ncp)
    elif alternative == "greater":
        critical_t = stats.t.ppf(1 - alpha, df)
        power = 1 - stats.nct.cdf(critical_t, df, ncp)
    else:
        critical_t = stats.t.ppf(alpha, df)
        power = stats.nct.cdf(critical_t, df, ncp)

    return {"power": round(power, 4),
            "adequate": power >= 0.80,
            "interpretation": f"{'Adequately' if power >= 0.80 else 'Under'}powered "
                             f"({power:.1%}) to detect d={effect_size} with n={n1}+{n2}"}

def sample_size_two_proportions(p1, p2, alpha=0.05, power=0.80, ratio=1):
    """
    Required sample size for comparing two proportions.
    Use to evaluate if a study planned adequate enrollment.

    Parameters:
        p1: expected proportion in control group
        p2: expected proportion in treatment group
        alpha: significance level
        power: desired power (0.80 or 0.90 standard)
        ratio: allocation ratio (n2/n1)
    """
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)
    p_bar = (p1 + ratio * p2) / (1 + ratio)
    n1 = ((z_alpha * np.sqrt((1 + ratio) * p_bar * (1 - p_bar)) +
           z_beta * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2) / ratio)) ** 2) / (p1 - p2) ** 2
    n1 = int(np.ceil(n1))
    n2 = int(np.ceil(n1 * ratio))
    return {"n_control": n1, "n_treatment": n2, "total": n1 + n2,
            "effect_size_ARD": round(abs(p1 - p2), 4),
            "assumptions": f"alpha={alpha}, power={power}, p1={p1}, p2={p2}"}

def power_survival_logrank(n_events, hazard_ratio, alpha=0.05, allocation_ratio=1):
    """
    Power for log-rank test based on number of events (Schoenfeld method).
    Use to evaluate if a survival analysis had adequate events.

    Parameters:
        n_events: total observed events
        hazard_ratio: target or observed HR
        alpha: significance level
        allocation_ratio: n_treatment / n_control
    """
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    r = allocation_ratio / (1 + allocation_ratio)
    theta = np.log(hazard_ratio)
    z_stat = abs(theta) * np.sqrt(n_events * r * (1 - r))
    power = 1 - stats.norm.cdf(z_alpha - z_stat) + stats.norm.cdf(-z_alpha - z_stat)
    return {"power": round(power, 4),
            "adequate": power >= 0.80,
            "events_for_80pct": int(np.ceil((z_alpha + stats.norm.ppf(0.80)) ** 2 /
                                            (r * (1 - r) * theta ** 2))),
            "events_for_90pct": int(np.ceil((z_alpha + stats.norm.ppf(0.90)) ** 2 /
                                            (r * (1 - r) * theta ** 2))),
            "interpretation": f"Study had {power:.1%} power with {n_events} events "
                             f"to detect HR={hazard_ratio}"}

def minimum_detectable_effect(n1, n2, alpha=0.05, power=0.80):
    """
    Minimum detectable effect size (Cohen's d) given sample sizes.
    Use to evaluate what effect a study was actually powered to detect.
    """
    from scipy.optimize import brentq
    def power_func(d):
        result = power_two_sample_ttest(n1, n2, d, alpha)
        return result["power"] - power
    try:
        mde = brentq(power_func, 0.001, 5.0)
        return {"MDE_cohens_d": round(mde, 4),
                "interpretation": f"With n={n1}+{n2}, study could detect d>={mde:.3f} "
                                 f"at {power:.0%} power (alpha={alpha})"}
    except ValueError:
        return {"MDE_cohens_d": None, "interpretation": "Could not compute MDE for given parameters"}
```

---

## Core Capability 4: Evidence Quality Grading

### GRADE Framework

#### Starting Certainty by Study Design

| Study Design | Starting Level | Rationale |
|-------------|---------------|-----------|
| Randomized controlled trials | High | Randomization controls confounding |
| Observational studies (cohort, case-control) | Low | Susceptible to confounding and bias |
| Case series, case reports | Very Low | No comparison group |
| Expert opinion, mechanism-based reasoning | Very Low | Highest risk of bias |

#### Downgrade Factors (each can reduce certainty by 1 or 2 levels)

| Factor | -1 (Serious) | -2 (Very Serious) |
|--------|-------------|-------------------|
| **Risk of bias** | Most information from studies at moderate RoB | Most information from studies at high RoB |
| **Inconsistency** | Point estimates vary, I-squared 50-75% | Conflicting directions, I-squared >75% |
| **Indirectness** | Moderate differences in PICO from question | Major differences, relying on surrogate outcomes |
| **Imprecision** | CI crosses one clinically important threshold | CI crosses both thresholds, very small sample |
| **Publication bias** | Suspected (asymmetric funnel, sponsor bias) | Strongly suspected (missing large negative trials) |

#### Upgrade Factors (observational studies only, each +1 level)

| Factor | Criteria | Example |
|--------|---------|---------|
| **Large effect** | RR >2 or <0.5 with no plausible confounders | Smoking and lung cancer (RR ~15-30) |
| **Dose-response** | Clear gradient demonstrated | Higher pack-years, higher cancer risk |
| **Residual confounding** | All plausible confounders would reduce effect | Healthy-user bias would work against observed benefit |

#### GRADE Evidence Assessment Workflow

```
Step 1: Rate each outcome separately
  └── Identify critical and important outcomes (max 7)

Step 2: Assign starting certainty
  └── RCT → High; Observational → Low

Step 3: Assess downgrade factors
  ├── Risk of bias → Use Cochrane RoB 2 (RCT) or ROBINS-I (observational)
  ├── Inconsistency → Calculate I-squared, inspect forest plot
  ├── Indirectness → Compare study PICO to review question
  ├── Imprecision → Check CI width and optimal information size
  └── Publication bias → Funnel plot, trial registry search

Step 4: Assess upgrade factors (observational only)
  ├── Large effect magnitude?
  ├── Dose-response gradient?
  └── Residual confounding direction?

Step 5: Assign final certainty
  └── High / Moderate / Low / Very Low

Step 6: Formulate recommendation strength
  ├── Strong: "We recommend..." (benefits clearly outweigh harms)
  └── Conditional: "We suggest..." (balance of benefits and harms is close)
```

### Oxford Centre for Evidence-Based Medicine (CEBM) Levels

| Level | Therapy/Prevention | Prognosis | Diagnosis |
|-------|-------------------|-----------|-----------|
| **1a** | SR of RCTs | SR of inception cohort studies | SR of Level 1 diagnostic studies |
| **1b** | Individual RCT (narrow CI) | Individual inception cohort (>80% follow-up) | Validating cohort with good reference |
| **2a** | SR of cohort studies | SR of retrospective cohort or untreated controls | SR of Level >2 diagnostic studies |
| **2b** | Individual cohort study | Retrospective cohort, follow-up of RCT controls | Exploratory cohort with good reference |
| **3a** | SR of case-control studies | — | Non-consecutive study, no reference applied |
| **3b** | Individual case-control | — | Case-control or poor/non-independent reference |
| **4** | Case series | Case series or poor quality prognostic cohort | — |
| **5** | Expert opinion | Expert opinion | Expert opinion |

### Risk of Bias Assessment Tools

| Tool | Study Type | Domains | Rating |
|------|-----------|---------|--------|
| **Cochrane RoB 2** | RCTs | Randomization, deviations, missing data, measurement, selection | Low / Some Concerns / High |
| **ROBINS-I** | Non-randomized interventional | Confounding, selection, classification, deviations, missing data, measurement, reporting | Low / Moderate / Serious / Critical |
| **Newcastle-Ottawa** | Observational (cohort, case-control) | Selection, comparability, outcome/exposure | 0-9 stars |
| **QUADAS-2** | Diagnostic accuracy | Patient selection, index test, reference standard, flow/timing | Low / High / Unclear |
| **AMSTAR 2** | Systematic reviews | Protocol, search, selection, data extraction, ROB, synthesis, publication bias | High / Moderate / Low / Critically Low |
| **JBI Critical Appraisal** | Qualitative, case series, prevalence | Design-specific checklist items | Include / Exclude / Seek info |

---

## Core Capability 5: Logical Fallacy Identification

### Causal Reasoning Fallacies

| Fallacy | Definition | Scientific Example | How to Counter |
|---------|-----------|-------------------|---------------|
| **Post hoc ergo propter hoc** | Assumes temporal sequence implies causation | "Drug given before recovery, therefore drug caused recovery" | Require control group; apply Bradford Hill criteria |
| **Correlation does not equal causation** | Conflating association with causal effect | "Countries with higher chocolate consumption win more Nobel Prizes" | Identify confounders; test causal mechanisms |
| **Ecological fallacy** | Applying group-level findings to individuals | "Country with high drug use has low mortality, therefore drug is protective for individuals" | Use individual-level data; multi-level analysis |
| **Simpson's paradox** | Trend reverses when data is aggregated/disaggregated | Treatment appears better overall but worse in every subgroup due to confounding | Stratify by confounders; use adjusted analyses |
| **Reverse causation** | Effect mistaken for cause | "Depression causes inflammation" vs "Inflammation causes depression" | Prospective design, Mendelian randomization |
| **Regression to the mean** | Extreme values naturally revert toward average | Patients selected for high blood pressure show improvement without treatment | Include control group; ANCOVA; avoid selecting on extreme values |

### Statistical and Quantitative Fallacies

| Fallacy | Definition | Scientific Example | How to Counter |
|---------|-----------|-------------------|---------------|
| **Base rate neglect** | Ignoring prior probability | Positive screening test in low-prevalence population (high false positive rate) | Calculate positive predictive value using Bayes' theorem |
| **Texas sharpshooter** | Drawing targets after shooting | Post-hoc subgroup shows significance in failed trial | Pre-register subgroups; adjust for multiplicity |
| **Cherry-picking** | Selecting favorable data points | Reporting only the 3-month timepoint where drug looked best | Report all pre-specified timepoints; examine full time course |
| **Gambler's fallacy** | Expecting past events to affect future probability | "Trial has failed 3 times, so it's due for success" | Each trial is independent; base decisions on current evidence |
| **Prosecutor's fallacy** | Confusing P(evidence given innocence) with P(innocence given evidence) | Confusing P(data given H0) with P(H0 given data) | Use proper Bayesian reasoning; distinguish p-values from posterior probabilities |
| **Will Rogers phenomenon** | Stage migration artificially improves outcomes in all groups | Improved diagnostic imaging reclassifies patients, improving stage-specific survival without real benefit | Compare overall outcomes, not just stage-specific |

### Argumentative Fallacies in Scientific Discourse

| Fallacy | Definition | Scientific Example | How to Counter |
|---------|-----------|-------------------|---------------|
| **Appeal to authority** | Accepting claim based on authority rather than evidence | "The Nobel laureate says this drug works" | Evaluate evidence quality, not the source's prestige |
| **Appeal to nature** | Assuming natural = safe/effective | "Herbal supplement is natural, therefore safe" | Require same evidence standard for all interventions |
| **False dichotomy** | Presenting only two options when more exist | "Either accept this treatment or do nothing" | Identify full range of alternatives |
| **Straw man** | Misrepresenting opponent's argument | "Critics say all animal research is useless" | Address actual arguments with actual evidence |
| **Ad hominem** | Attacking the person instead of the argument | "Industry-funded study is automatically biased" | Evaluate methodology, not just funding source |
| **Moving the goalposts** | Changing criteria after evidence is presented | "That trial doesn't count because it wasn't long enough" | Establish evaluation criteria before reviewing evidence |
| **Nirvana fallacy** | Rejecting option because it's not perfect | "This treatment only helps 30% of patients, so it's useless" | Compare against alternatives, not perfection |
| **Appeal to tradition** | "We've always done it this way" | Continuing outdated treatment without evidence review | Evaluate current evidence systematically |

---

## Core Capability 6: Research Design Guidance

### Question Refinement Frameworks

#### PICO (Therapy/Prevention)

| Component | Question | Example |
|-----------|---------|---------|
| **P**opulation | Who? | Adults with treatment-resistant depression |
| **I**ntervention | What treatment? | Psilocybin-assisted therapy |
| **C**omparison | Versus what? | SSRI + psychotherapy |
| **O**utcome | Measuring what? | MADRS score at 6 weeks |

#### FINER (Research Feasibility)

| Criterion | Question | Red Flag |
|-----------|---------|----------|
| **F**easible | Can it be done with available resources? | Requires 10,000 patients in rare disease |
| **I**nteresting | Does it matter to stakeholders? | Already answered definitively |
| **N**ovel | Does it add new knowledge? | Replicates known finding without added value |
| **E**thical | Can it be done ethically? | Equipoise not established |
| **R**elevant | Will it change practice? | Effect too small to be clinically meaningful |

### Design Selection Guide

```
What is the research question?
├── Does intervention X cause outcome Y?
│   ├── Ethical to randomize? → RCT
│   │   ├── Can participants be blinded? → Double-blind RCT
│   │   └── Cannot blind? → Open-label with blinded outcome assessment
│   └── Cannot randomize?
│       ├── Exposure assigned by policy/event → Quasi-experimental (RDD, DiD, ITS)
│       └── Exposure is self-selected → Prospective cohort + propensity score
├── Is exposure X associated with outcome Y?
│   ├── Outcome is rare → Case-control study
│   ├── Exposure is rare → Cohort study
│   └── Both common → Cross-sectional (prevalence only)
├── What is the prognosis for condition X?
│   └── Inception cohort study
├── How accurate is diagnostic test X?
│   └── Cross-sectional diagnostic accuracy study (STARD)
└── What is the prevalence of X?
    └── Cross-sectional survey (representative sample)
```

### Bias Minimization Strategies by Design

| Strategy | RCT | Cohort | Case-Control |
|----------|-----|--------|-------------|
| **Selection bias** | Randomization + concealment | Consecutive enrollment | Population-based controls |
| **Confounding** | Randomization (balances known + unknown) | Multivariable adjustment, propensity scores | Matching, stratification |
| **Performance bias** | Blinding participants/providers | Standardized protocols | N/A |
| **Detection bias** | Blinded outcome assessment | Blinded outcome assessment | Blinded exposure assessment |
| **Attrition bias** | ITT analysis, minimize dropout | Complete follow-up strategies | N/A |
| **Reporting bias** | Pre-registration (ClinicalTrials.gov) | Pre-registration (PROSPERO, OSF) | Pre-registration |

### Pre-Registration and Transparency Requirements

| Element | Where to Register | What to Specify |
|---------|------------------|----------------|
| **Clinical trials** | ClinicalTrials.gov, ISRCTN, EU-CTR | Design, endpoints, sample size, analysis plan |
| **Systematic reviews** | PROSPERO, OSF | PICO, search strategy, quality tool, synthesis method |
| **Observational studies** | OSF, AsPredicted | Hypothesis, variables, analysis plan, exclusion criteria |
| **Analysis code** | GitHub, OSF, Zenodo | Full analysis scripts, version-controlled |
| **Data** | Repositories (Dryad, Figshare, Zenodo) | De-identified datasets when ethically permissible |

---

## Core Capability 7: Claim Evaluation

### Bradford Hill Criteria for Causation

| Criterion | Definition | Assessment Question | Strength of Evidence |
|-----------|-----------|--------------------|--------------------|
| **Strength** | Large effect size | Is the association strong (large RR/OR)? | Stronger = more likely causal |
| **Consistency** | Replicated across settings | Has it been observed by different researchers, in different populations? | Consistent replication strengthens causation |
| **Specificity** | Specific exposure-outcome link | Is the exposure specifically linked to this outcome? | Weakest criterion; many causes are non-specific |
| **Temporality** | Exposure precedes outcome | Did the exposure definitely come before the outcome? | Mandatory criterion; cannot be causal without temporal sequence |
| **Biological gradient** | Dose-response relationship | Does more exposure lead to more outcome? | Strong evidence if present |
| **Plausibility** | Biologically plausible mechanism | Is there a known mechanism? | Depends on current knowledge (evolving) |
| **Coherence** | Consistent with known biology | Does it fit with what we know about the disease? | Absence does not refute causation |
| **Experiment** | Experimental evidence supports | Does removing/modifying exposure change outcome? | Strong if available (intervention studies) |
| **Analogy** | Similar exposures cause similar outcomes | Are there analogous cause-effect relationships? | Weakest criterion; suggestive only |

### Bradford Hill Assessment Workflow

```
For each causal claim:

1. TEMPORALITY (mandatory)
   → Does exposure clearly precede outcome?
   → If no → Causation cannot be established → STOP

2. STRENGTH
   → What is the effect size (RR, OR, HR)?
   → RR > 2 or < 0.5 suggests causation (though weak associations can be causal)

3. CONSISTENCY
   → Search for replication:
     mcp__pubmed__pubmed_data(method: "search_keywords",
       keywords: "[exposure] [outcome] replication OR meta-analysis")
   → How many independent studies confirm the finding?

4. BIOLOGICAL GRADIENT
   → Is there dose-response evidence?
   → Check for monotonic relationship between exposure level and outcome

5. PLAUSIBILITY
   → Is the mechanism known?
   → Check target-disease biology:
     mcp__opentargets__opentargets_data(method: "get_target_disease_associations")

6. COHERENCE
   → Does the finding contradict established knowledge?
   → If contradictory, is there an explanation?

7. EXPERIMENT
   → Is there interventional evidence?
   → Search clinical trials:
     mcp__ctgov__ctgov_data(method: "search", intervention: "[exposure]")

8. SPECIFICITY and ANALOGY (weaker criteria, note but don't overweight)

9. OVERALL JUDGMENT
   → How many criteria are satisfied?
   → Temporality + Strength + Consistency + Biological gradient = strong case
   → Temporality alone = insufficient
```

### Reporting Guideline Compliance

| Guideline | Study Type | Key Items | Items Count |
|-----------|-----------|-----------|-------------|
| **CONSORT** | RCTs | Flow diagram, randomization, blinding, ITT, outcomes | 25 items |
| **STROBE** | Observational (cohort, case-control, cross-sectional) | Study design, setting, participants, variables, bias, statistics | 22 items |
| **PRISMA** | Systematic reviews / meta-analyses | Search strategy, study selection, data extraction, ROB, synthesis | 27 items |
| **STARD** | Diagnostic accuracy | Index test, reference standard, flow diagram, accuracy measures | 30 items |
| **ARRIVE** | Animal research | Study design, sample size, randomization, blinding, outcomes | 21 items |
| **SPIRIT** | Clinical trial protocols | Objectives, design, participants, interventions, outcomes, analysis | 33 items |
| **TRIPOD** | Prediction models | Source of data, participants, outcome, predictors, sample size, performance | 22 items |
| **CARE** | Case reports | Timeline, diagnostic assessment, interventions, outcomes, lessons | 13 items |
| **SQUIRE** | Quality improvement | Problem description, context, intervention, study of intervention, measures | 18 items |
| **MOOSE** | Meta-analyses of observational studies | Search strategy, study selection, quality assessment, heterogeneity | 35 items |

#### CONSORT Compliance Quick Check (RCTs)

- [ ] Title identifies study as randomized
- [ ] CONSORT flow diagram with numbers at each stage
- [ ] Randomization: sequence generation, allocation concealment described
- [ ] Blinding: who was blinded, how assessed
- [ ] Primary outcome clearly defined with pre-specified analysis
- [ ] Sample size calculation with assumptions
- [ ] ITT analysis performed
- [ ] All randomized participants accounted for
- [ ] Harms/adverse events reported
- [ ] Trial registration number and protocol provided
- [ ] Funding and conflict of interest disclosed

#### STROBE Compliance Quick Check (Observational)

- [ ] Study design indicated in title/abstract
- [ ] Setting, locations, dates described
- [ ] Eligibility criteria with sources and methods of selection
- [ ] Variables clearly defined (exposures, outcomes, confounders)
- [ ] Bias: efforts to address sources of bias described
- [ ] Sample size: rationale provided
- [ ] Statistical methods: confounding adjustment, missing data handling
- [ ] Descriptive data: characteristics by group, missing data
- [ ] Main results: unadjusted and adjusted estimates with CI
- [ ] Limitations discussed including direction and magnitude of bias
- [ ] Funding and conflict of interest disclosed

---

## Research Quality Score (0-100)

### Scoring Framework

| Dimension | Max Points | Criteria |
|-----------|-----------|----------|
| **Study Design** | 25 | Appropriate design for question, adequate controls, blinding, randomization quality |
| **Statistical Rigor** | 20 | Correct tests, adequate power, effect sizes reported, appropriate adjustments |
| **Bias Control** | 20 | Selection, measurement, and analysis biases minimized; confounding addressed |
| **Evidence Level** | 15 | GRADE certainty rating, position in study hierarchy |
| **Reproducibility** | 10 | Methods detail sufficient, data/code availability, pre-registration status |
| **Logical Coherence** | 10 | No logical fallacies, valid causal reasoning, conclusions match evidence |

### Detailed Scoring Rubric

#### Study Design (0-25)

| Score | Criteria |
|-------|---------|
| 22-25 | RCT or SR/MA with appropriate design, proper randomization, adequate blinding, clear controls |
| 17-21 | Well-designed cohort or quasi-experimental; RCT with minor design issues |
| 12-16 | Case-control with population-based controls; cohort with some design limitations |
| 7-11 | Cross-sectional, case series with reasonable methodology |
| 0-6 | Ecological study, poorly designed case series, expert opinion without evidence |

#### Statistical Rigor (0-20)

| Score | Criteria |
|-------|---------|
| 17-20 | Correct tests, adequate power (>80%), effect sizes with CI, pre-specified analysis plan |
| 13-16 | Mostly correct tests, reasonable power, some effect sizes, minor analytical issues |
| 9-12 | Some statistical errors, underpowered, limited effect size reporting |
| 5-8 | Multiple statistical errors, severely underpowered, p-values without effect sizes |
| 0-4 | Inappropriate tests, no power consideration, selective reporting |

#### Bias Control (0-20)

| Score | Criteria |
|-------|---------|
| 17-20 | All major biases addressed, confounding controlled, sensitivity analyses performed |
| 13-16 | Most biases addressed, reasonable confounding control, some sensitivity analyses |
| 9-12 | Some biases addressed, partial confounding control |
| 5-8 | Major biases unaddressed, minimal confounding control |
| 0-4 | No bias assessment, confounding ignored |

#### Evidence Level (0-15)

| Score | Criteria |
|-------|---------|
| 13-15 | GRADE High or Moderate; SR/MA of high-quality RCTs or large well-conducted RCT |
| 9-12 | GRADE Moderate or Low; individual RCT or large prospective cohort |
| 5-8 | GRADE Low; retrospective cohort, case-control |
| 0-4 | GRADE Very Low; case series, expert opinion, ecological |

#### Reproducibility (0-10)

| Score | Criteria |
|-------|---------|
| 9-10 | Pre-registered, open data, open code, detailed methods, independent replication available |
| 6-8 | Pre-registered or open data, adequate methods detail |
| 3-5 | Methods described but not sufficient for replication, no data/code sharing |
| 0-2 | Insufficient methods detail, no registration, no data sharing |

#### Logical Coherence (0-10)

| Score | Criteria |
|-------|---------|
| 9-10 | No logical fallacies, conclusions proportionate to evidence, limitations acknowledged |
| 6-8 | Minor logical issues, conclusions mostly supported, some limitations discussed |
| 3-5 | Notable logical gaps, conclusions partially overreach evidence |
| 0-2 | Major fallacies, conclusions unsupported by evidence |

### Quality Tiers

| Tier | Score Range | Interpretation | Action |
|------|-----------|----------------|--------|
| **High Quality** | 80-100 | Conclusions well-supported by evidence | Results can inform decision-making |
| **Moderate Quality** | 60-79 | Conclusions conditionally supported | Consider with caveats; seek additional evidence |
| **Low Quality** | 40-59 | Conclusions questionable, major concerns | Treat with skepticism; do not base decisions solely on this |
| **Very Low Quality** | 0-39 | Conclusions unreliable | Evidence insufficient for any conclusion; new studies needed |

### Quality Score Report Template

```
## Research Quality Assessment

**Study**: [Title, Authors, Year, Journal]
**PMID/DOI**: [identifier]
**Study Design**: [RCT / Cohort / Case-Control / etc.]

### Score Breakdown

| Dimension | Score | Max | Key Issues |
|-----------|-------|-----|------------|
| Study Design | _/25 | 25 | [issues] |
| Statistical Rigor | _/20 | 20 | [issues] |
| Bias Control | _/20 | 20 | [issues] |
| Evidence Level | _/15 | 15 | [issues] |
| Reproducibility | _/10 | 10 | [issues] |
| Logical Coherence | _/10 | 10 | [issues] |
| **TOTAL** | **_/100** | 100 | |

### Quality Tier: [High/Moderate/Low/Very Low]

### GRADE Certainty: [High/Moderate/Low/Very Low]

### Key Strengths
1. [strength]
2. [strength]

### Critical Concerns
1. [concern with impact on conclusions]
2. [concern with impact on conclusions]

### Bias Assessment Summary
- Selection bias: [Low/Moderate/High risk] — [explanation]
- Measurement bias: [Low/Moderate/High risk] — [explanation]
- Analysis bias: [Low/Moderate/High risk] — [explanation]
- Confounding: [Low/Moderate/High risk] — [explanation]

### Conclusion Validity
[Are the authors' conclusions supported by the evidence? What caveats apply?]
```

---

## Multi-Agent Workflow Examples

**"Evaluate the evidence for Drug X in Disease Y"**
1. Scientific Critical Thinking → Assess evidence quality, detect biases, grade evidence (this skill)
2. Systematic Literature Reviewer → PRISMA-compliant search and screening
3. Clinical Trial Analyst → Trial design adequacy, endpoint appropriateness

**"Critique this research paper"**
1. Scientific Critical Thinking → Methodology critique, bias detection, statistical assessment, logical fallacy check (this skill)
2. Statistical Modeling → Verify statistical analyses, re-run if data available

**"Is this claim supported by evidence?"**
1. Scientific Critical Thinking → Bradford Hill criteria, logical fallacy check, evidence grading (this skill)
2. Systematic Literature Reviewer → Comprehensive evidence search
3. Pharmacovigilance Specialist → If claim involves drug safety

**"Review our experimental design before submission"**
1. Scientific Critical Thinking → Design evaluation, bias identification, power assessment (this skill)
2. Clinical Trial Protocol Designer → Protocol structure and regulatory alignment
3. Scientific Writing → Manuscript quality and reporting guideline compliance

---

## Completeness Checklist

- [ ] Study design identified and appropriateness evaluated
- [ ] Randomization, blinding, and control adequacy assessed (if applicable)
- [ ] All relevant biases systematically evaluated (selection, measurement, analysis, confounding)
- [ ] Statistical methods appropriate for data type and research question
- [ ] Sample size adequacy / power assessment completed
- [ ] Effect sizes reported with confidence intervals (not just p-values)
- [ ] Multiple comparisons addressed if applicable
- [ ] Evidence quality graded using GRADE framework
- [ ] Position in study hierarchy (CEBM levels) identified
- [ ] Risk of bias assessed using appropriate tool (RoB 2, ROBINS-I, NOS, QUADAS-2)
- [ ] Logical fallacies checked (causal reasoning, statistical, argumentative)
- [ ] Bradford Hill criteria applied for causal claims
- [ ] Reporting guideline compliance evaluated (CONSORT, STROBE, PRISMA as applicable)
- [ ] Research Quality Score computed with dimension breakdown
- [ ] Conclusions assessed for proportionality to evidence strength
- [ ] Limitations and alternative explanations considered
- [ ] Reproducibility indicators checked (pre-registration, data/code availability)
- [ ] Cross-skill routing applied where deeper analysis needed
