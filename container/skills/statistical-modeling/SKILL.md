---
name: statistical-modeling
description: Biostatistics and statistical modeling for biomedical research. Survival analysis, Cox regression, Kaplan-Meier, logistic regression, linear mixed models, power analysis, sample size calculation, Bayesian statistics, multiple testing correction, clinical trial statistics, meta-analysis statistics. Use when user mentions statistical analysis, survival analysis, Cox regression, Kaplan-Meier, logistic regression, mixed effects model, power analysis, sample size, Bayesian, biostatistics, hazard ratio, odds ratio, confidence interval, p-value, multiple testing, or meta-analysis.
---

# Statistical Modeling

> **Code recipes**: See [recipes.md](recipes.md), [data-wrangling-recipes.md](data-wrangling-recipes.md), [regression-recipes.md](regression-recipes.md), and [survival-recipes.md](survival-recipes.md) for executable code templates.

Biostatistics and statistical modeling for biomedical research. The agent writes and executes Python code for survival analysis, regression models, mixed effects models, power analysis, Bayesian approaches, meta-analysis, and diagnostic metrics. Uses statsmodels, scipy, lifelines, and scikit-learn for computation and matplotlib for visualization.

## Report-First Workflow

1. **Create report file immediately**: `[analysis]_statistical_modeling_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Analyzing...]`
3. **Populate progressively**: Update sections as data is gathered from MCP tools and analysis
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Analyzing...]` placeholders remain

## When NOT to Use This Skill
- Clinical trial protocol design and endpoint selection → use `clinical-trial-protocol-designer`
- Differential gene expression analysis (RNA-seq) → use `rnaseq-deseq2`
- Gene set enrichment and pathway analysis → use `gene-enrichment`
- GWAS summary statistics and variant interpretation → use `gwas-study-explorer`
- Systematic literature review and meta-analysis protocol → use `systematic-literature-reviewer`
- Clinical trial data extraction and analysis → use `clinical-trial-analyst`

## Cross-Reference: Other Skills

- **Clinical trial protocol design and endpoints** -> use clinical-trial-analyst skill
- **Differential expression analysis (RNA-seq)** -> use rnaseq-deseq2 skill
- **Gene set enrichment and pathway analysis** -> use gene-enrichment skill
- **GWAS summary statistics and variant interpretation** -> use gwas-study-explorer skill

## Python Environment

| Package | Purpose |
|---------|---------|
| `statsmodels` | GLMs, logistic regression, mixed effects, time series |
| `scipy` | Distributions, hypothesis tests, optimization, Bayesian priors |
| `lifelines` | Kaplan-Meier, Cox PH, log-rank test, parametric survival models |
| `scikit-learn` | ROC/AUC, calibration, cross-validation, classification metrics |
| `numpy` | Array operations, linear algebra |
| `pandas` | Data manipulation, I/O |
| `matplotlib` | Plotting (survival curves, forest plots, ROC curves) |

---

## Analysis Types & Method Selection

### Decision Tree: Outcome x Predictor x Design -> Method

```
1. OUTCOME TYPE:
   Time-to-event (survival, recurrence, death)
     - Single group survival curve -> Kaplan-Meier
     - Compare 2+ groups -> Log-rank test
     - Adjust for covariates -> Cox proportional hazards

   Binary (yes/no, disease/no disease, response/no response)
     - Unadjusted association -> Chi-square / Fisher's exact
     - Adjust for covariates -> Logistic regression
     - Clustered/repeated -> GEE or mixed logistic

   Continuous (blood pressure, gene expression, biomarker level)
     - Compare 2 groups -> t-test (or Wilcoxon if non-normal)
     - Compare 3+ groups -> ANOVA (or Kruskal-Wallis)
     - Adjust for covariates -> Linear regression / GLM
     - Repeated measures / clustered -> Linear mixed model

   Count (number of events, hospitalizations, mutations)
     - Poisson regression (if mean ~ variance)
     - Negative binomial (if overdispersed)

2. STUDY DESIGN MODIFIERS:
   - Repeated measures -> Mixed effects model
   - Clustered data (patients within sites) -> Mixed effects or GEE
   - Multi-center trial -> Random intercept for site
   - Longitudinal -> Mixed model with random slope
```

---

## Survival Analysis

### Kaplan-Meier Estimation

```python
import pandas as pd
import numpy as np
from lifelines import KaplanMeierFitter
import matplotlib.pyplot as plt

df = pd.read_csv("survival_data.csv")

fig, ax = plt.subplots(figsize=(10, 7))
kmf = KaplanMeierFitter()

for group_name in df["group"].unique():
    mask = df["group"] == group_name
    kmf.fit(
        durations=df.loc[mask, "time"],
        event_observed=df.loc[mask, "event"],
        label=group_name
    )
    kmf.plot_survival_function(ax=ax, ci_show=True)
    median = kmf.median_survival_time_
    print(f"{group_name}: Median survival = {median:.1f}")
    print(f"  Survival at 12 months: {kmf.predict(12):.3f}")

ax.set_xlabel("Time (months)")
ax.set_ylabel("Survival Probability")
ax.set_title("Kaplan-Meier Survival Curves")
ax.legend()
plt.tight_layout()
plt.savefig("km_curves.png", dpi=150)
```

### Cox Proportional Hazards

```python
from lifelines import CoxPHFitter

cox_df = df[["time", "event", "treatment", "age", "sex", "stage"]].copy()

cph = CoxPHFitter()
cph.fit(cox_df, duration_col="time", event_col="event")
cph.print_summary()

# Extract hazard ratios and CIs
summary = cph.summary
print("\nHazard Ratios:")
for var in summary.index:
    hr = summary.loc[var, "exp(coef)"]
    lower = summary.loc[var, "exp(coef) lower 95%"]
    upper = summary.loc[var, "exp(coef) upper 95%"]
    p = summary.loc[var, "p"]
    print(f"  {var}: HR = {hr:.3f} (95% CI: {lower:.3f}-{upper:.3f}), p = {p:.4f}")

# PH assumption test — if violated, consider stratification or time-varying coefficients
ph_test = cph.check_assumptions(cox_df, p_value_threshold=0.05, show_plots=False)

# Forest plot
fig, ax = plt.subplots(figsize=(8, 5))
cph.plot(ax=ax)
ax.axvline(x=0, color="black", linestyle="--", linewidth=0.5)
ax.set_title("Cox PH Forest Plot (log Hazard Ratios)")
plt.tight_layout()
plt.savefig("cox_forest_plot.png", dpi=150)
```

### Log-Rank Test

```python
from lifelines.statistics import logrank_test, multivariate_logrank_test

group_a = df[df["group"] == "A"]
group_b = df[df["group"] == "B"]

results = logrank_test(
    group_a["time"], group_b["time"],
    event_observed_A=group_a["event"],
    event_observed_B=group_b["event"]
)
print(f"Log-rank test statistic: {results.test_statistic:.4f}")
print(f"p-value: {results.p_value:.6f}")

# Multi-group comparison
multi_result = multivariate_logrank_test(df["time"], df["group"], df["event"])
print(f"Multivariate log-rank p-value: {multi_result.p_value:.6f}")
```

---

## Regression Models

### Logistic Regression

```python
import statsmodels.api as sm
from sklearn.metrics import roc_auc_score, roc_curve

X = df[["age", "bmi", "smoking", "biomarker_level"]].copy()
X = sm.add_constant(X)
y = df["disease_status"]  # 0 or 1

model = sm.Logit(y, X)
result = model.fit()
print(result.summary2())

# Odds ratios with 95% CI
params = result.params
conf = result.conf_int()
odds_ratios = np.exp(params)
ci_lower = np.exp(conf[0])
ci_upper = np.exp(conf[1])

print("\nOdds Ratios:")
for var in params.index:
    print(f"  {var}: OR = {odds_ratios[var]:.3f} "
          f"(95% CI: {ci_lower[var]:.3f}-{ci_upper[var]:.3f}), "
          f"p = {result.pvalues[var]:.4f}")

# ROC/AUC
y_pred_prob = result.predict(X)
auc = roc_auc_score(y, y_pred_prob)
print(f"\nAUC: {auc:.3f}")

fpr, tpr, _ = roc_curve(y, y_pred_prob)
fig, ax = plt.subplots(figsize=(7, 7))
ax.plot(fpr, tpr, label=f"AUC = {auc:.3f}")
ax.plot([0, 1], [0, 1], "k--", label="Random")
ax.set_xlabel("False Positive Rate")
ax.set_ylabel("True Positive Rate")
ax.set_title("ROC Curve")
ax.legend()
plt.tight_layout()
plt.savefig("roc_curve.png", dpi=150)
```

### Linear Regression & GLMs

```python
import statsmodels.formula.api as smf

# OLS linear regression
model = smf.ols("outcome ~ age + treatment + biomarker + C(site)", data=df)
result = model.fit()
print(result.summary())

# Residual diagnostics: residuals vs fitted, Q-Q plot, histogram
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
axes[0].scatter(result.fittedvalues, result.resid, alpha=0.5, s=10)
axes[0].axhline(0, color="red", linestyle="--")
axes[0].set_title("Residuals vs Fitted")
from scipy import stats
stats.probplot(result.resid, plot=axes[1])
axes[2].hist(result.resid, bins=30, edgecolor="black")
axes[2].set_title("Residual Distribution")
plt.tight_layout()
plt.savefig("regression_diagnostics.png", dpi=150)

# Poisson GLM for count data with rate ratios
poisson_model = smf.glm("event_count ~ age + treatment", data=df,
    family=sm.families.Poisson(), offset=np.log(df["person_years"]))
poisson_result = poisson_model.fit()
for var in poisson_result.params.index:
    rr = np.exp(poisson_result.params[var])
    ci = np.exp(poisson_result.conf_int().loc[var])
    print(f"  {var}: RR = {rr:.3f} (95% CI: {ci[0]:.3f}-{ci[1]:.3f})")
```

### Mixed Effects Models

```python
import statsmodels.formula.api as smf

mixed_model = smf.mixedlm(
    "outcome ~ time + treatment + time:treatment",
    data=df, groups=df["subject_id"], re_formula="~time"
)
mixed_result = mixed_model.fit(reml=True)
print(mixed_result.summary())

# Fixed effects with CIs
for var in mixed_result.fe_params.index:
    coef = mixed_result.fe_params[var]
    se = mixed_result.bse_fe[var]
    print(f"  {var}: {coef:.4f} (95% CI: {coef-1.96*se:.4f}-{coef+1.96*se:.4f}), p={mixed_result.pvalues[var]:.4f}")

# ICC = var(random intercept) / (var(random intercept) + var(residual))
icc = mixed_result.cov_re.iloc[0, 0] / (mixed_result.cov_re.iloc[0, 0] + mixed_result.scale)
print(f"\nICC: {icc:.4f} ({icc*100:.1f}% of variance is between subjects)")
```

---

## Multiple Testing Correction

```python
import numpy as np
from scipy import stats

def adjust_pvalues(pvalues, method="bh"):
    """Adjust p-values: 'bonferroni', 'holm', or 'bh' (Benjamini-Hochberg)."""
    pvals = np.array(pvalues)
    n = len(pvals)
    sorted_idx = np.argsort(pvals)
    sorted_pvals = pvals[sorted_idx]

    if method == "bonferroni":
        adjusted = np.minimum(sorted_pvals * n, 1.0)
    elif method == "holm":
        adjusted = np.zeros(n)
        for i in range(n):
            adjusted[i] = sorted_pvals[i] * (n - i)
        for i in range(1, n):
            adjusted[i] = max(adjusted[i], adjusted[i - 1])
        adjusted = np.minimum(adjusted, 1.0)
    elif method == "bh":
        adjusted = np.zeros(n)
        for i in range(n):
            adjusted[i] = sorted_pvals[i] * n / (i + 1)
        for i in range(n - 2, -1, -1):
            adjusted[i] = min(adjusted[i], adjusted[i + 1])
        adjusted = np.minimum(adjusted, 1.0)

    result = np.zeros(n)
    result[sorted_idx] = adjusted
    return result

# Usage
raw_pvalues = [0.001, 0.013, 0.029, 0.032, 0.05, 0.10, 0.20, 0.45]
print("Raw p-values:", raw_pvalues)
print("Bonferroni:  ", adjust_pvalues(raw_pvalues, "bonferroni").round(4))
print("Holm:        ", adjust_pvalues(raw_pvalues, "holm").round(4))
print("BH (FDR):    ", adjust_pvalues(raw_pvalues, "bh").round(4))
```

### Method Selection

```
- Bonferroni: Few tests (< 20), strict family-wise error rate control
- Holm: More powerful than Bonferroni, same FWER control
- Benjamini-Hochberg (BH): Many tests (genomics, screening), controls FDR
- Clinical trials: primary endpoint = no correction; co-primary = Bonferroni/hierarchical;
  secondary = pre-specified hierarchy; exploratory = BH/FDR
```

---

## Power Analysis & Sample Size

```python
from scipy import stats
import numpy as np

def power_two_sample_ttest(effect_size, alpha=0.05, power=0.80, ratio=1.0):
    """Sample size for two-sample t-test. effect_size = Cohen's d."""
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)
    n1 = ((z_alpha + z_beta) ** 2 * (1 + 1 / ratio)) / effect_size ** 2
    n2 = n1 * ratio
    return int(np.ceil(n1)), int(np.ceil(n2))

def power_chi_square(p1, p2, alpha=0.05, power=0.80, ratio=1.0):
    """Sample size for chi-square test of two proportions."""
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)
    p_bar = (p1 + ratio * p2) / (1 + ratio)
    n1 = ((z_alpha * np.sqrt((1 + ratio) * p_bar * (1 - p_bar))
           + z_beta * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2) / ratio)) ** 2) / (p1 - p2) ** 2
    n2 = n1 * ratio
    return int(np.ceil(n1)), int(np.ceil(n2))

def power_survival_logrank(hr, prob_event, alpha=0.05, power=0.80, ratio=1.0):
    """Sample size for log-rank test (Schoenfeld formula)."""
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)
    total_events = ((z_alpha + z_beta) ** 2 * (1 + ratio) ** 2) / (ratio * (np.log(hr)) ** 2)
    total_events = int(np.ceil(total_events))
    total_n = int(np.ceil(total_events / prob_event))
    n1 = int(np.ceil(total_n / (1 + ratio)))
    n2 = total_n - n1
    return n1, n2, total_events

# Usage
print("=== Two-sample t-test ===")
for d in [0.2, 0.5, 0.8]:
    n1, n2 = power_two_sample_ttest(d)
    print(f"  Cohen's d = {d}: n1 = {n1}, n2 = {n2}")

print("\n=== Chi-square (two proportions) ===")
n1, n2 = power_chi_square(p1=0.30, p2=0.20)
print(f"  p1=0.30, p2=0.20: n1 = {n1}, n2 = {n2}")

print("\n=== Log-rank (survival) ===")
n1, n2, events = power_survival_logrank(hr=0.70, prob_event=0.60)
print(f"  HR=0.70, event rate=60%: n1={n1}, n2={n2}, events needed={events}")
```

### Effect Size Guidelines

```
Cohen's d:  0.2 = small, 0.5 = medium, 0.8 = large
OR / HR:    1.2 = small, 1.5 = medium, 2.0 = large
No pilot data: use clinically meaningful difference, consult literature,
use conservative (smaller) effect size to avoid underpowering.
```

---

## Meta-Analysis

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

def meta_analysis(effects, se, method="random"):
    """Inverse-variance weighted meta-analysis (fixed or DerSimonian-Laird)."""
    effects, se = np.array(effects, float), np.array(se, float)
    w = 1.0 / se ** 2
    pooled_f = np.sum(w * effects) / np.sum(w)
    se_f = 1.0 / np.sqrt(np.sum(w))
    Q = np.sum(w * (effects - pooled_f) ** 2)
    df = len(effects) - 1
    p_het = 1 - stats.chi2.cdf(Q, df) if df > 0 else 1.0
    I2 = max(0, (Q - df) / Q * 100) if Q > 0 else 0.0

    if method == "fixed":
        return {"pooled": pooled_f, "se": se_f, "ci_lower": pooled_f - 1.96 * se_f,
                "ci_upper": pooled_f + 1.96 * se_f, "Q": Q, "p_het": p_het,
                "I2": I2, "method": "Fixed-effects"}

    tau2 = max(0, (Q - df) / (np.sum(w) - np.sum(w**2) / np.sum(w)))
    w_re = 1.0 / (se ** 2 + tau2)
    pooled_re = np.sum(w_re * effects) / np.sum(w_re)
    se_re = 1.0 / np.sqrt(np.sum(w_re))
    return {"pooled": pooled_re, "se": se_re, "ci_lower": pooled_re - 1.96 * se_re,
            "ci_upper": pooled_re + 1.96 * se_re, "tau2": tau2, "Q": Q,
            "p_het": p_het, "I2": I2, "method": "Random-effects (DL)"}

def forest_plot(study_names, effects, se, meta_result, outcome_label="Effect"):
    """Forest plot with study-level and pooled diamond."""
    effects, se = np.array(effects), np.array(se)
    k = len(study_names)
    fig, ax = plt.subplots(figsize=(10, max(4, k * 0.6 + 2)))
    y_pos = np.arange(k, 0, -1)
    ax.errorbar(effects, y_pos, xerr=1.96 * se, fmt="o", color="black", capsize=3)
    p = meta_result["pooled"]
    ax.fill([meta_result["ci_lower"], p, meta_result["ci_upper"], p],
            [0, 0.3, 0, -0.3], color="red", alpha=0.7)
    ax.set_yticks(list(y_pos) + [0])
    ax.set_yticklabels(list(study_names) + ["Pooled"])
    ax.axvline(x=0, color="gray", linestyle="--", linewidth=0.5)
    ax.set_xlabel(outcome_label)
    ax.set_title(f"Forest Plot ({meta_result['method']}), "
                 f"I2={meta_result['I2']:.1f}%")
    plt.tight_layout()
    plt.savefig("forest_plot.png", dpi=150)

# Usage: meta-analysis of log odds ratios
study_names = ["Study A", "Study B", "Study C", "Study D", "Study E"]
log_or = np.array([0.35, 0.52, 0.18, 0.41, 0.29])
se_log_or = np.array([0.12, 0.18, 0.15, 0.10, 0.20])

result = meta_analysis(log_or, se_log_or, method="random")
print(f"Pooled OR: {np.exp(result['pooled']):.3f} "
      f"(95% CI: {np.exp(result['ci_lower']):.3f}-{np.exp(result['ci_upper']):.3f})")
print(f"Heterogeneity: Q={result['Q']:.2f}, I2={result['I2']:.1f}%, p={result['p_het']:.4f}")

forest_plot(study_names, log_or, se_log_or, result, outcome_label="log(OR)")
```

### Heterogeneity Interpretation

```
I-squared: 0-25% low, 25-50% moderate, 50-75% substantial, 75-100% considerable
When I2 is high: check clinical/methodological heterogeneity, run subgroup
analysis, leave-one-out sensitivity analysis, consider if pooling is appropriate.
```

---

## Bayesian Approaches

```python
from scipy import stats
import numpy as np
import matplotlib.pyplot as plt

def bayesian_proportion(successes, total, prior_a=1, prior_b=1, credible_level=0.95):
    """Bayesian estimation of a proportion with Beta-Binomial conjugacy."""
    post_a = prior_a + successes
    post_b = prior_b + (total - successes)
    posterior = stats.beta(post_a, post_b)
    alpha_tail = (1 - credible_level) / 2

    result = {
        "posterior_mean": posterior.mean(),
        "posterior_median": posterior.median(),
        "posterior_mode": (post_a - 1) / (post_a + post_b - 2) if (post_a > 1 and post_b > 1) else None,
        "ci_lower": posterior.ppf(alpha_tail),
        "ci_upper": posterior.ppf(1 - alpha_tail),
        "prob_gt_50pct": 1 - posterior.cdf(0.5),
        "prior": f"Beta({prior_a}, {prior_b})",
        "posterior": f"Beta({post_a}, {post_b})"
    }
    return result, posterior

# Usage: 23 responders out of 40 patients
result, posterior = bayesian_proportion(successes=23, total=40)
print(f"Posterior mean: {result['posterior_mean']:.3f}")
print(f"95% Credible Interval: ({result['ci_lower']:.3f}, {result['ci_upper']:.3f})")
print(f"P(response rate > 50%): {result['prob_gt_50pct']:.3f}")

# Visualization
x = np.linspace(0, 1, 500)
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(x, stats.beta(1, 1).pdf(x), "b--", label=f"Prior: {result['prior']}")
ax.plot(x, posterior.pdf(x), "r-", lw=2, label=f"Posterior: {result['posterior']}")
ax.fill_between(x, posterior.pdf(x),
    where=(x >= result["ci_lower"]) & (x <= result["ci_upper"]),
    alpha=0.2, color="red", label="95% CrI")
ax.set_xlabel("Response Rate"); ax.set_ylabel("Density")
ax.set_title("Bayesian Estimation"); ax.legend()
plt.tight_layout()
plt.savefig("bayesian_posterior.png", dpi=150)
```

### Prior Selection

```
Non-informative: Beta(1,1) = Uniform; Beta(0.5,0.5) = Jeffreys
Weakly informative: Beta(2,2); Normal(0, 10)
Informative: Beta(a,b) where a/(a+b) = prior estimate, a+b = confidence
ALWAYS run sensitivity analysis with at least 2 different priors.
```

---

## Diagnostic Metrics

```python
import numpy as np
from sklearn.metrics import (
    confusion_matrix, roc_auc_score, roc_curve,
    precision_recall_curve, average_precision_score, calibration_curve
)
import matplotlib.pyplot as plt

def diagnostic_metrics(y_true, y_pred_prob, threshold=0.5):
    """Sensitivity, specificity, PPV, NPV, AUC, likelihood ratios."""
    y_pred = (np.array(y_pred_prob) >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    ppv = tp / (tp + fp) if (tp + fp) > 0 else 0
    npv = tn / (tn + fn) if (tn + fn) > 0 else 0
    auc = roc_auc_score(y_true, y_pred_prob)
    lr_pos = sensitivity / (1 - specificity) if specificity < 1 else float("inf")
    lr_neg = (1 - sensitivity) / specificity if specificity > 0 else float("inf")

    return {"sensitivity": sensitivity, "specificity": specificity,
            "ppv": ppv, "npv": npv, "accuracy": (tp + tn) / (tp + tn + fp + fn),
            "auc": auc, "lr_positive": lr_pos, "lr_negative": lr_neg}

def plot_diagnostic_suite(y_true, y_pred_prob):
    """ROC, precision-recall, and calibration plots in a single figure."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fpr, tpr, _ = roc_curve(y_true, y_pred_prob)
    axes[0].plot(fpr, tpr, label=f"AUC = {roc_auc_score(y_true, y_pred_prob):.3f}")
    axes[0].plot([0, 1], [0, 1], "k--")
    axes[0].set_title("ROC Curve"); axes[0].legend()
    prec, rec, _ = precision_recall_curve(y_true, y_pred_prob)
    axes[1].plot(rec, prec, label=f"AP = {average_precision_score(y_true, y_pred_prob):.3f}")
    axes[1].set_title("Precision-Recall"); axes[1].legend()
    prob_true, prob_pred = calibration_curve(y_true, y_pred_prob, n_bins=10)
    axes[2].plot(prob_pred, prob_true, "o-", label="Model")
    axes[2].plot([0, 1], [0, 1], "k--")
    axes[2].set_title("Calibration"); axes[2].legend()
    plt.tight_layout()
    plt.savefig("diagnostic_suite.png", dpi=150)

# Usage
metrics = diagnostic_metrics(y_true, y_pred_prob)
for k, v in metrics.items():
    print(f"  {k}: {v:.3f}" if isinstance(v, float) else f"  {k}: {v}")
plot_diagnostic_suite(y_true, y_pred_prob)
```

---

## Common Pitfalls

```
1. MULTIPLE COMPARISONS WITHOUT CORRECTION
   Testing 20 biomarkers at alpha=0.05 -> expect 1 false positive.
   ALWAYS apply BH/Bonferroni. Report both raw and adjusted p-values.

2. P-HACKING / DATA DREDGING
   Do not try multiple analyses and report only significant ones.
   Pre-register analysis plan. Distinguish confirmatory from exploratory.

3. CONFOUNDING
   Age, sex, severity often confound treatment effects.
   Use multivariable models. Cannot adjust for unmeasured confounders.

4. SIMPSON'S PARADOX
   Association can reverse when aggregated vs stratified.
   Always check results within clinically meaningful subgroups.

5. IMMORTAL TIME BIAS
   Time between cohort entry and treatment start misclassified.
   Use time-varying covariates or landmark analysis.

6. OVERFITTING
   Need ~10 events per predictor in regression.
   Use cross-validation or bootstrap. Penalized regression when predictors >> events.

7. MISINTERPRETING SIGNIFICANCE
   p < 0.05 does NOT mean clinically important.
   Always report effect sizes with confidence intervals.

8. SURVIVAL ANALYSIS PITFALLS
   PH assumption violation: check Schoenfeld residuals.
   Informative censoring: censored patients differ from observed.
   Competing risks: death from other causes prevents event of interest.
```

---

## Evidence Grading Framework

| Tier | Criteria | Confidence |
|------|----------|------------|
| **T1** | Pre-specified, adequate power, appropriate model, corrected, clinically meaningful, validated | High |
| **T2** | Appropriate model, corrected p-values, adequate N, but exploratory or single-cohort | Medium-High |
| **T3** | Correct test but limited power, no validation, or marginal significance | Medium |
| **T4** | Exploratory, uncorrected, underpowered, or assumptions violated | Low |

---

## Boundary Rules

```
DO:
- Write and execute Python code for survival analysis (KM, Cox, log-rank)
- Fit logistic regression, linear regression, GLMs, mixed effects models
- Perform power analysis and sample size calculations
- Run meta-analysis (fixed/random effects) with forest plots
- Apply multiple testing corrections (Bonferroni, BH, Holm)
- Compute diagnostic metrics (sensitivity, specificity, ROC, calibration)
- Implement basic Bayesian estimation with conjugate priors
- Generate publication-ready statistical plots
- Interpret hazard ratios, odds ratios, coefficients, and CIs

DO NOT:
- Design clinical trial protocols (use clinical-trial-analyst skill)
- Perform differential gene expression (use rnaseq-deseq2 skill)
- Run pathway enrichment analysis (use gene-enrichment skill)
- Interpret GWAS summary statistics (use gwas-study-explorer skill)
- Perform machine learning / deep learning model training
- Provide definitive clinical recommendations from statistical output alone
```

---

## Multi-Agent Workflow Examples

**"Analyze survival data from our clinical trial with Cox regression and generate a forest plot"**
1. Statistical Modeling -> Load data, fit KM curves, log-rank test, Cox PH with covariates, PH assumption check, forest plot
2. Clinical Trial Analyst -> Contextualize endpoints, regulatory interpretation

**"Calculate sample size for a phase III trial comparing two treatments on overall survival"**
1. Statistical Modeling -> Log-rank power analysis, sensitivity across HR and event rate assumptions
2. Clinical Trial Analyst -> Study design, enrollment timeline, interim analysis planning

**"Run a meta-analysis of published hazard ratios for drug X vs placebo"**
1. Statistical Modeling -> DerSimonian-Laird random-effects meta-analysis, heterogeneity assessment, forest plot, sensitivity analysis
2. Clinical Trial Analyst -> Evidence synthesis, quality assessment, clinical interpretation

**"Build a logistic regression model to predict treatment response from baseline biomarkers"**
1. Statistical Modeling -> Logistic regression, ROC/AUC, calibration, cross-validation, diagnostic metrics
2. Gene Enrichment -> Pathway analysis of significant biomarkers
3. GWAS Study Explorer -> Genetic variant associations for predictive biomarkers

## Completeness Checklist
- [ ] Outcome type identified and appropriate method selected
- [ ] Data assumptions checked (normality, proportional hazards, linearity)
- [ ] Model fitted with covariates justified
- [ ] Effect sizes reported with 95% confidence intervals
- [ ] Multiple testing correction applied where appropriate
- [ ] Model diagnostics completed (residuals, goodness-of-fit)
- [ ] Sensitivity analyses performed (alternative models, outlier exclusion)
- [ ] Publication-ready figures generated (forest plot, ROC, KM curves)
- [ ] Evidence tier assigned to each finding (T1-T4)
