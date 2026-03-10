# Biostatistical Test Recipes

Copy-paste-ready Python code for common biostatistical tests in bioinformatics.
Dependencies: `scipy`, `statsmodels`, `numpy`, `sklearn`.

---

## Decision Tree: Which Test Should I Use?

```
Comparing 2 groups?
  |-- Data normally distributed? (check with Shapiro-Wilk)
  |     |-- Yes --> Student's t-test (#2)
  |     |-- No  --> Mann-Whitney U (#1)
  |
Comparing 3+ groups?
  |-- One factor?  --> One-way ANOVA (#4)
  |-- Two factors? --> Two-way ANOVA (#5)
  |
Testing independence of categories?
  |-- Chi-square test (#3)
  |
Predicting binary outcome?
  |-- Logistic regression (#8)
  |
Predicting ordered outcome?
  |-- Ordinal logistic regression (#9)
  |
Correlation between continuous variables?
  |-- Normal data   --> Pearson (#7)
  |-- Non-normal     --> Spearman (#7)
  |
Multiple treatments vs one control?
  |-- Dunnett's test (#13)
  |
Multiple p-values to correct?
  |-- Multiple comparison correction (#10)
```

---

## 1. Mann-Whitney U Test

Non-parametric comparison of two independent groups.

```python
from scipy.stats import mannwhitneyu
stat, pval = mannwhitneyu(group1, group2, alternative='two-sided')
print(f"U={stat}, p={pval:.4e}")
```

**When to use:** Two independent groups, no normality assumption needed.
**Pitfalls:** Independent observations only. Does not test means -- tests stochastic ordering.
**Interpretation:** p < 0.05 means the groups differ in rank distributions.

---

## 2. Student's t-test

Parametric two-group comparison.

```python
from scipy.stats import ttest_ind, ttest_rel

# Independent samples
stat, pval = ttest_ind(group1, group2)

# Welch's t-test (unequal variances -- preferred default)
stat, pval = ttest_ind(group1, group2, equal_var=False)

# Paired t-test (same subjects, two conditions)
stat, pval = ttest_rel(before, after)
```

**When to use:** Two groups, continuous data, approximately normal.
**Pitfalls:** Check normality with Shapiro-Wilk (#6) first. Use Welch's by default. Paired requires matched observations.
**Interpretation:** p < 0.05 means group means differ. df = n1+n2-2 (independent) or n-1 (paired).

---

## 3. Chi-square Test of Independence

```python
from scipy.stats import chi2_contingency
chi2, pval, dof, expected = chi2_contingency(contingency_table)
```

**When to use:** Two categorical variables, testing association.
**Pitfalls:** All expected frequencies >= 5. If not, use Fisher's exact: `fisher_exact(table)`. Input must be counts, not proportions.
**Interpretation:** p < 0.05 means variables are not independent.

---

## 4. One-way ANOVA

Compare means across 3+ groups.

```python
from scipy.stats import f_oneway
F, pval = f_oneway(group1, group2, group3)

# Post-hoc: Tukey HSD for pairwise comparisons
from scipy.stats import tukey_hsd
result = tukey_hsd(group1, group2, group3)
```

**When to use:** 3+ independent groups, continuous normally distributed data.
**Pitfalls:** Significant result only means "at least one differs" -- follow with post-hoc. Non-normal data: use `kruskal(g1, g2, g3)`. Check equal variances: `levene(g1, g2, g3)`.
**Interpretation:** p < 0.05 means at least one group mean differs. Report F(df_between, df_within).

---

## 5. Two-way ANOVA (with Interaction)

Tests effects of two factors and their interaction.

```python
import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols

# Example: gene expression by treatment and genotype
df = pd.DataFrame({
    'expression': [5.2, 5.8, 6.1, 7.3, 7.8, 8.1, 4.9, 5.1, 5.5, 6.8, 7.2, 7.5],
    'treatment':  ['ctrl','ctrl','ctrl','drug','drug','drug'] * 2,
    'genotype':   ['WT']*6 + ['KO']*6,
})

model = ols('expression ~ C(treatment) * C(genotype)', data=df).fit()
table = sm.stats.anova_lm(model, typ=2)  # Type II SS

print(table)
```

**When to use:** Two categorical independent variables, one continuous dependent variable.

**Pitfalls:**
- Type II SS (`typ=2`) is preferred for unbalanced designs.
- Type III SS (`typ=3`) requires sum-to-zero coding -- set `sum` contrasts first.
- Significant interaction means main effects should be interpreted cautiously.

**Interpretation:** Check interaction term first. If significant, main effects are conditional. Report F and p for each factor and interaction.

---

## 6. Shapiro-Wilk Normality Test

```python
from scipy.stats import shapiro
W, pval = shapiro(data)
```

**When to use:** Before parametric tests. Best for n < 5000.
**Pitfalls:** Very sensitive with large samples (always rejects). Non-significant does not prove normality.
**Interpretation:** p > 0.05 = consistent with normality. p < 0.05 = deviates from normal.

---

## 7. Correlation: Spearman and Pearson

```python
from scipy.stats import spearmanr, pearsonr

r, pval = pearsonr(x, y)       # linear, assumes normality
rho, pval = spearmanr(x, y)    # rank-based, no normality needed

# Correlation matrix
corr_matrix = df.corr(method='spearman')
```

**When to use:** Pearson for linear + normal. Spearman for monotonic or non-normal.
**Pitfalls:** Pearson sensitive to outliers. r = 0 means no *linear* relationship only.
**Interpretation:** |r|: 0.1-0.3 small, 0.3-0.5 medium, 0.5+ large. Sign = direction.

---

## 8. Logistic Regression

Binary outcome prediction. Use for case/control, responder/non-responder.

```python
import numpy as np
import pandas as pd
import statsmodels.api as sm

df = pd.DataFrame({
    'outcome': [1, 0, 1, 1, 0, 0, 1, 0, 1, 1],
    'age':     [45, 52, 38, 61, 55, 42, 67, 48, 59, 63],
    'score':   [7.2, 3.1, 6.8, 8.5, 4.2, 3.8, 9.1, 5.0, 7.8, 8.0],
})

X = sm.add_constant(df[['age', 'score']])
model = sm.Logit(df['outcome'], X).fit()

print(model.summary())

# Odds ratios with 95% CI
odds_ratios = np.exp(model.params)
ci = np.exp(model.conf_int())
ci.columns = ['OR_2.5%', 'OR_97.5%']
ci['OR'] = odds_ratios
print(ci)

# Predict probabilities
probs = model.predict(X)
print(f"Predicted probabilities:\n{probs.values}")
```

**When to use:** Binary dependent variable, one or more continuous/categorical predictors.

**Pitfalls:**
- Requires sufficient events per predictor (rule of thumb: >= 10 events per variable).
- Multicollinearity between predictors inflates standard errors.
- Check model fit with Hosmer-Lemeshow or AIC.

**Interpretation:** OR > 1 means increased odds of outcome per unit increase in predictor. OR < 1 means decreased odds. CI crossing 1.0 means not significant.

---

## 9. Ordinal Logistic Regression

For ordered categorical outcomes (e.g., none/mild/moderate/severe).

```python
import numpy as np
import pandas as pd
from statsmodels.miscmodels.ordinal_model import OrderedModel

df = pd.DataFrame({
    'severity': pd.Categorical([0, 1, 2, 2, 1, 0, 2, 1, 0, 2],
                                categories=[0, 1, 2], ordered=True),
    'dose':     [10, 20, 30, 40, 15, 5, 35, 25, 8, 45],
    'age':      [45, 52, 61, 58, 48, 40, 63, 55, 42, 65],
})

X = df[['dose', 'age']]
y = df['severity']

model = OrderedModel(y, X, distr='logit').fit(method='bfgs')
print(model.summary())

# Odds ratios
print("Odds ratios:")
print(np.exp(model.params))
```

**When to use:** Ordered categorical outcome with 3+ levels.

**Pitfalls:**
- Assumes proportional odds (same OR across all thresholds). Test this assumption with Brant test.
- Small sample sizes per category lead to unstable estimates.
- Use `method='bfgs'` if default optimization fails to converge.

**Interpretation:** OR > 1 for a predictor means higher values increase odds of being in a higher severity category.

---

## 10. Multiple Comparison Correction

Adjust p-values when performing many simultaneous tests (e.g., testing thousands of genes).

```python
import numpy as np
from statsmodels.stats.multitest import multipletests

# Example: p-values from testing 10 genes
pvals = np.array([0.001, 0.01, 0.03, 0.04, 0.05, 0.10, 0.20, 0.50, 0.70, 0.90])

# Benjamini-Hochberg (FDR) -- most common in genomics
reject, pvals_bh, _, _ = multipletests(pvals, alpha=0.05, method='fdr_bh')
print("BH-adjusted p-values:", pvals_bh)
print("Rejected (FDR < 0.05):", reject)

# Bonferroni -- most conservative
reject, pvals_bonf, _, _ = multipletests(pvals, alpha=0.05, method='bonferroni')
print("Bonferroni-adjusted:", pvals_bonf)

# Holm-Bonferroni -- less conservative than Bonferroni, still controls FWER
reject, pvals_holm, _, _ = multipletests(pvals, alpha=0.05, method='holm')
print("Holm-adjusted:", pvals_holm)
```

**Methods summary:**

| Method | Controls | Use when |
|--------|----------|----------|
| `fdr_bh` | False discovery rate | Genomics, many tests (default choice) |
| `bonferroni` | Family-wise error rate | Few comparisons, strict control needed |
| `holm` | Family-wise error rate | Like Bonferroni but more powerful |

**Pitfalls:**
- Always correct BEFORE interpreting significance.
- FDR at 0.05 means 5% of *rejected* hypotheses are expected to be false positives.
- Bonferroni at 0.05 means 5% chance of *any* false positive across all tests.

---

## 11. Cohen's d Effect Size

Quantifies the magnitude of difference between two groups, independent of sample size.

```python
import numpy as np

def cohens_d(group1, group2):
    """Calculate Cohen's d for two independent groups."""
    n1, n2 = len(group1), len(group2)
    var1 = np.var(group1, ddof=1)
    var2 = np.var(group2, ddof=1)
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    return (np.mean(group1) - np.mean(group2)) / pooled_std

group1 = np.array([12.3, 14.1, 15.8, 13.2, 16.0])
group2 = np.array([18.1, 19.3, 17.5, 20.2, 18.8])

d = cohens_d(group1, group2)
print(f"Cohen's d: {d:.4f}")
```

**Interpretation thresholds (Cohen, 1988):**

| |d| | Effect size |
|-----|-------------|
| 0.2 | Small |
| 0.5 | Medium |
| 0.8 | Large |

**Pitfalls:**
- Always report alongside p-value. A significant p-value with tiny d is meaningless biologically.
- For unequal group sizes, pooled SD is still appropriate.
- For paired designs, use the SD of differences instead.

---

## 12. Power Analysis / Sample Size Calculation

Determine required sample size before running an experiment.

```python
from statsmodels.stats.power import TTestIndPower, TTestPower

analysis = TTestIndPower()

# How many subjects per group for a medium effect?
n = analysis.solve_power(effect_size=0.5, alpha=0.05, power=0.8, alternative='two-sided')
print(f"Required n per group: {np.ceil(n):.0f}")

# What power do I have with my current sample?
power = analysis.solve_power(effect_size=0.5, alpha=0.05, nobs1=30, alternative='two-sided')
print(f"Power with n=30: {power:.4f}")

# What effect size can I detect?
d = analysis.solve_power(alpha=0.05, power=0.8, nobs1=50, alternative='two-sided')
print(f"Detectable effect size with n=50: {d:.4f}")

# Power for proportions (e.g., response rates)
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize
es = proportion_effectsize(0.3, 0.5)  # 30% vs 50% response rate
n = NormalIndPower().solve_power(effect_size=es, alpha=0.05, power=0.8)
print(f"Required n per group (proportions): {np.ceil(n):.0f}")
```

**When to use:** Before starting any experiment. Required for grant applications and IRB submissions.

**Pitfalls:**
- Effect size estimate must come from pilot data or literature, not the same dataset.
- Power < 0.8 is underpowered. Power > 0.95 may indicate overinvestment in sample size.
- Adjust for dropout: multiply n by 1/(1 - dropout_rate).

---

## 13. Dunnett's Test

Compare multiple treatment groups against a single control. More powerful than Bonferroni for this specific design.

```python
import numpy as np
from scipy.stats import dunnett

control = np.array([4.2, 3.8, 4.5, 4.1, 3.9])
treatment_a = np.array([6.1, 5.8, 6.3, 5.9, 6.2])
treatment_b = np.array([5.0, 4.8, 5.2, 4.9, 5.1])
treatment_c = np.array([4.3, 4.1, 4.4, 4.0, 4.2])

result = dunnett(treatment_a, treatment_b, treatment_c, control=control)

print(f"Statistics: {result.statistic}")
print(f"P-values: {result.pvalue}")
```

**When to use:** Multiple treatments vs one control. Common in dose-response studies.

**Pitfalls:**
- Control group must be specified explicitly.
- Only compares each treatment to control, not treatments to each other (use Tukey HSD for all pairwise).
- Requires scipy >= 1.10.

---

## 14. Skewness and Kurtosis

```python
from scipy.stats import skew, kurtosis, skewtest, kurtosistest

sk = skew(data)                # positive = right-skewed, negative = left-skewed
kurt = kurtosis(data)          # excess kurtosis (0 = normal)
z_skew, p_skew = skewtest(data)       # requires n >= 8
z_kurt, p_kurt = kurtosistest(data)    # requires n >= 20
```

**Interpretation:** |skew| > 1 is highly skewed. Positive kurtosis = heavy tails. High skewness suggests log-transform or non-parametric tests.

---

## 15. Transition/Transversion Ratio (Ts/Tv)

```python
def tstv_ratio(vcf_df):
    """Calculate Ts/Tv from DataFrame with REF and ALT columns.
    Expected: ~2.0-2.1 (WGS), ~2.8-3.0 (WES). < 1.5 = poor quality.
    """
    transitions = {('A','G'), ('G','A'), ('C','T'), ('T','C')}
    snvs = vcf_df[(vcf_df['REF'].str.len() == 1) & (vcf_df['ALT'].str.len() == 1)]
    ts = snvs.apply(lambda r: (r['REF'], r['ALT']) in transitions, axis=1).sum()
    tv = len(snvs) - ts
    return ts / tv if tv > 0 else float('inf')
```

---

## 16. Wilson Confidence Interval for Proportions

Better than the normal approximation, especially for small samples or proportions near 0 or 1.

```python
from statsmodels.stats.proportion import proportion_confint

count = 8    # number of successes
nobs = 25    # total observations

# Wilson score interval (recommended)
ci_low, ci_high = proportion_confint(count, nobs, alpha=0.05, method='wilson')
print(f"Proportion: {count/nobs:.4f}")
print(f"95% CI (Wilson): [{ci_low:.4f}, {ci_high:.4f}]")

# Other methods for comparison
for method in ['wilson', 'normal', 'agresti_coull', 'beta', 'jeffreys']:
    lo, hi = proportion_confint(count, nobs, alpha=0.05, method=method)
    print(f"  {method:16s}: [{lo:.4f}, {hi:.4f}]")
```

**When to use:** Reporting confidence intervals for proportions (mutation rates, response rates, allele frequencies).

**Pitfalls:**
- Normal approximation (`method='normal'`) fails for small n or extreme proportions. Always prefer Wilson.
- For comparing two proportions, use `proportions_ztest` or Fisher's exact test instead.

---

## 17. AIC Model Comparison

Lower AIC = better fit (penalized for complexity).

```python
from statsmodels.formula.api import ols

model1 = ols('y ~ x1', data=df).fit()
model2 = ols('y ~ x1 + x2', data=df).fit()

# Compare
for name, m in [('m1', model1), ('m2', model2)]:
    print(f"{name}  AIC={m.aic:.2f}  BIC={m.bic:.2f}  R2={m.rsquared:.4f}")
```

**Interpretation:** delta_AIC < 2 = equivalent. 2-7 = some evidence. > 10 = strong evidence against worse model.
**Pitfalls:** AIC is relative. Only compare models on same data. Use BIC for large n.

---

## Quick Reference Table

| Test | Function | Assumptions |
|------|----------|-------------|
| Mann-Whitney U | `mannwhitneyu(g1, g2)` | Independent, ordinal+ |
| t-test (ind.) | `ttest_ind(g1, g2)` | Normal, independent |
| t-test (paired) | `ttest_rel(g1, g2)` | Normal, paired |
| Welch's t-test | `ttest_ind(g1, g2, equal_var=False)` | Normal |
| Chi-square | `chi2_contingency(table)` | Expected freq >= 5 |
| Fisher's exact | `fisher_exact(table)` | 2x2, small samples |
| One-way ANOVA | `f_oneway(g1, g2, g3)` | Normal, equal var |
| Kruskal-Wallis | `kruskal(g1, g2, g3)` | Independent, ordinal+ |
| Shapiro-Wilk | `shapiro(data)` | n < 5000 |
| Pearson | `pearsonr(x, y)` | Normal, linear |
| Spearman | `spearmanr(x, y)` | Monotonic |
| Logistic reg. | `sm.Logit(y, X).fit()` | Binary outcome |
| Ordinal reg. | `OrderedModel(y, X)` | Ordered outcome |
| Dunnett's | `dunnett(*groups, control=c)` | scipy >= 1.10 |
| Bonferroni | `multipletests(p, method='bonferroni')` | Any |
| BH FDR | `multipletests(p, method='fdr_bh')` | Any |

---

## Cross-Skill Routing

- Study design and methodology --> `statistical-modeling`
- Power analysis planning and experimental design --> `experimental-design`
- Differential expression statistics --> `deseq2-recipes`
- Methylation-specific statistics --> `methylation-recipes`
