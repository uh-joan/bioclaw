# Regression & Curve-Fitting Recipes for Bioinformatics

Executable Python code templates for regression modeling in biomedical contexts. Each recipe is self-contained with inline comments explaining every step.

---

## 1. Simple Linear Regression (scipy.stats.linregress)

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# Example: correlating gene expression with drug IC50
expression = np.array([2.1, 3.5, 4.2, 5.8, 6.1, 7.3, 8.0, 9.2, 10.1, 11.5])
ic50 = np.array([45.2, 38.1, 35.0, 28.5, 25.3, 20.1, 18.4, 14.2, 10.5, 8.1])

# Fit simple linear regression
slope, intercept, r_value, p_value, std_err = stats.linregress(expression, ic50)
r_squared = r_value ** 2

print(f"Slope: {slope:.3f} (SE: {std_err:.3f})")
print(f"Intercept: {intercept:.3f}")
print(f"R-squared: {r_squared:.4f}")
print(f"p-value: {p_value:.2e}")
print(f"Interpretation: each unit increase in expression is associated "
      f"with a {abs(slope):.1f} unit {'decrease' if slope < 0 else 'increase'} in IC50")

# Plot with regression line and confidence band
fig, ax = plt.subplots(figsize=(8, 6))
ax.scatter(expression, ic50, color="steelblue", s=60, label="Observed")
x_line = np.linspace(expression.min(), expression.max(), 100)
y_line = slope * x_line + intercept
ax.plot(x_line, y_line, color="red", label=f"y = {slope:.2f}x + {intercept:.2f}")

# 95% confidence interval for the regression line
n = len(expression)
x_mean = expression.mean()
se_line = std_err * np.sqrt(1/n + (x_line - x_mean)**2 / np.sum((expression - x_mean)**2))
t_crit = stats.t.ppf(0.975, df=n-2)
ax.fill_between(x_line, y_line - t_crit * se_line, y_line + t_crit * se_line,
                alpha=0.15, color="red", label="95% CI")

ax.set_xlabel("Gene Expression (log2 TPM)")
ax.set_ylabel("IC50 (uM)")
ax.set_title(f"Expression vs IC50 (R²={r_squared:.3f}, p={p_value:.2e})")
ax.legend()
plt.tight_layout()
plt.savefig("linear_regression.png", dpi=150)
```

---

## 2. Multiple Linear Regression (statsmodels OLS)

```python
import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
from scipy import stats

# Load dataset: predict continuous outcome from multiple predictors
df = pd.read_csv("biomarker_data.csv")

# Formula interface: outcome ~ predictor1 + predictor2 + categorical
model = smf.ols("biomarker_level ~ age + bmi + C(sex) + log_crp + smoking_years", data=df)
result = model.fit()
print(result.summary())

# Extract coefficients with 95% CIs
coef_df = pd.DataFrame({
    "coefficient": result.params,
    "std_err": result.bse,
    "t_stat": result.tvalues,
    "p_value": result.pvalues,
    "ci_lower": result.conf_int()[0],
    "ci_upper": result.conf_int()[1]
})
print(f"\nCoefficients:\n{coef_df.round(4)}")
print(f"\nR-squared: {result.rsquared:.4f}")
print(f"Adjusted R-squared: {result.rsquared_adj:.4f}")
print(f"F-statistic: {result.fvalue:.2f}, p = {result.f_pvalue:.2e}")

# Residual diagnostics: normality, homoscedasticity
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
# Residuals vs fitted
axes[0, 0].scatter(result.fittedvalues, result.resid, alpha=0.5, s=15)
axes[0, 0].axhline(0, color="red", linestyle="--")
axes[0, 0].set_title("Residuals vs Fitted")
# Q-Q plot
stats.probplot(result.resid, plot=axes[0, 1])
axes[0, 1].set_title("Q-Q Plot")
# Histogram of residuals
axes[1, 0].hist(result.resid, bins=30, edgecolor="black")
axes[1, 0].set_title("Residual Distribution")
# Scale-location plot
axes[1, 1].scatter(result.fittedvalues, np.sqrt(np.abs(result.resid)), alpha=0.5, s=15)
axes[1, 1].set_title("Scale-Location")
plt.tight_layout()
plt.savefig("ols_diagnostics.png", dpi=150)

# Multicollinearity check: Variance Inflation Factor
from statsmodels.stats.outliers_influence import variance_inflation_factor
X_numeric = df[["age", "bmi", "log_crp", "smoking_years"]].dropna()
X_const = sm.add_constant(X_numeric)
for i, col in enumerate(X_const.columns[1:]):
    vif = variance_inflation_factor(X_const.values, i + 1)
    print(f"  VIF({col}): {vif:.2f}" + (" *** HIGH" if vif > 5 else ""))
```

---

## 3. Logistic Regression (sklearn + statsmodels)

```python
import pandas as pd
import numpy as np
import statsmodels.api as sm
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.metrics import roc_auc_score, classification_report
import matplotlib.pyplot as plt

df = pd.read_csv("patient_outcomes.csv")

# --- Statsmodels: for inference (p-values, odds ratios, CIs) ---
X = df[["age", "tumor_size", "marker_level", "stage_numeric"]].copy()
X = sm.add_constant(X)
y = df["response"]  # binary: 0 = no response, 1 = response

logit_model = sm.Logit(y, X)
logit_result = logit_model.fit()
print(logit_result.summary2())

# Odds ratios with 95% CIs
or_df = pd.DataFrame({
    "odds_ratio": np.exp(logit_result.params),
    "ci_lower": np.exp(logit_result.conf_int()[0]),
    "ci_upper": np.exp(logit_result.conf_int()[1]),
    "p_value": logit_result.pvalues
})
print(f"\nOdds Ratios:\n{or_df.round(3)}")

# --- Sklearn: for prediction performance (cross-validation) ---
X_sk = df[["age", "tumor_size", "marker_level", "stage_numeric"]].values
y_sk = df["response"].values

clf = LogisticRegression(penalty="l2", C=1.0, max_iter=1000, random_state=42)
cv_auc = cross_val_score(clf, X_sk, y_sk, cv=5, scoring="roc_auc")
print(f"\n5-fold CV AUC: {cv_auc.mean():.3f} (+/- {cv_auc.std():.3f})")

# Fit on full data for ROC plot
clf.fit(X_sk, y_sk)
y_prob = clf.predict_proba(X_sk)[:, 1]
print(f"Training AUC: {roc_auc_score(y_sk, y_prob):.3f}")
print(f"\nClassification Report:\n{classification_report(y_sk, clf.predict(X_sk))}")
```

---

## 4. Ordinal Logistic Regression (statsmodels OrderedModel)

```python
import pandas as pd
import numpy as np
from statsmodels.miscmodels.ordinal_model import OrderedModel

df = pd.read_csv("toxicity_grades.csv")

# Ordinal outcome: toxicity grade (0=none, 1=mild, 2=moderate, 3=severe)
# Predictors: dose level, age, weight, renal function
X = df[["dose_mg", "age", "weight_kg", "egfr"]].copy()
y = df["toxicity_grade"]  # ordered categories: 0, 1, 2, 3

# Fit proportional odds model (logit link)
model = OrderedModel(y, X, distr="logit")
result = model.fit(method="bfgs", disp=False)
print(result.summary())

# Extract odds ratios for predictors (not thresholds)
predictor_names = X.columns.tolist()
params = result.params[:len(predictor_names)]
conf = result.conf_int()[:len(predictor_names)]
pvals = result.pvalues[:len(predictor_names)]

print("\nCumulative Odds Ratios (proportional odds):")
for i, name in enumerate(predictor_names):
    or_val = np.exp(params.iloc[i])
    ci_lo = np.exp(conf.iloc[i, 0])
    ci_hi = np.exp(conf.iloc[i, 1])
    print(f"  {name}: OR = {or_val:.3f} (95% CI: {ci_lo:.3f}-{ci_hi:.3f}), "
          f"p = {pvals.iloc[i]:.4f}")

# Predicted probabilities for a specific patient profile
new_patient = pd.DataFrame({
    "dose_mg": [100], "age": [65], "weight_kg": [70], "egfr": [45]
})
pred_probs = result.predict(new_patient)
print(f"\nPredicted probabilities for new patient:")
for grade, prob in enumerate(pred_probs[0]):
    print(f"  Grade {grade}: {prob:.3f} ({prob*100:.1f}%)")
```

---

## 5. Polynomial Regression

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# Example: dose-response curve (nonlinear relationship)
dose = np.array([0, 0.1, 0.5, 1, 2, 5, 10, 20, 50, 100])
response = np.array([0.02, 0.05, 0.15, 0.32, 0.55, 0.78, 0.88, 0.93, 0.97, 0.99])

# Compare polynomial degrees 1-4
fig, ax = plt.subplots(figsize=(10, 7))
ax.scatter(dose, response, color="black", s=80, zorder=5, label="Observed")

best_degree, best_aic = 1, np.inf
x_plot = np.linspace(0, 100, 200).reshape(-1, 1)

for degree in range(1, 5):
    # Transform features to polynomial
    poly = PolynomialFeatures(degree=degree, include_bias=False)
    X_poly = poly.fit_transform(dose.reshape(-1, 1))
    X_plot_poly = poly.transform(x_plot)

    # Fit linear regression on polynomial features
    reg = LinearRegression()
    reg.fit(X_poly, response)
    y_pred = reg.predict(X_poly)
    y_plot = reg.predict(X_plot_poly)

    r2 = r2_score(response, y_pred)
    n = len(dose)
    k = degree + 1  # number of parameters
    rss = np.sum((response - y_pred) ** 2)
    aic = n * np.log(rss / n) + 2 * k  # AIC for model comparison
    print(f"Degree {degree}: R² = {r2:.4f}, AIC = {aic:.2f}")

    if aic < best_aic:
        best_aic = aic
        best_degree = degree

    ax.plot(x_plot, y_plot, label=f"Degree {degree} (R²={r2:.3f})")

ax.set_xlabel("Dose (uM)")
ax.set_ylabel("Response (fraction)")
ax.set_title(f"Polynomial Regression (best degree = {best_degree} by AIC)")
ax.legend()
plt.tight_layout()
plt.savefig("polynomial_regression.png", dpi=150)
print(f"\nBest polynomial degree by AIC: {best_degree}")
```

---

## 6. Spline Regression (scipy interpolate)

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline, BSpline, make_interp_spline
from scipy import stats

# Nonlinear biomarker trajectory over time
time = np.array([0, 1, 2, 3, 4, 6, 8, 12, 16, 20, 24, 30, 36])
biomarker = np.array([5.2, 8.1, 12.3, 15.8, 14.2, 11.5, 9.8, 8.1, 7.5, 7.2, 7.0, 6.8, 6.5])

# Smoothing spline: s controls smoothness (higher = smoother)
# s=0 interpolates all points; larger s allows more deviation
spline_smooth = UnivariateSpline(time, biomarker, s=5)
spline_interp = UnivariateSpline(time, biomarker, s=0)  # exact interpolation

# B-spline with specified degree
bspline = make_interp_spline(time, biomarker, k=3)  # cubic B-spline

# Evaluate on fine grid
t_fine = np.linspace(0, 36, 200)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Left: compare spline fits
axes[0].scatter(time, biomarker, color="black", s=60, zorder=5, label="Observed")
axes[0].plot(t_fine, spline_smooth(t_fine), "r-", label="Smoothing spline (s=5)")
axes[0].plot(t_fine, spline_interp(t_fine), "b--", label="Interpolating spline (s=0)")
axes[0].plot(t_fine, bspline(t_fine), "g:", label="Cubic B-spline")
axes[0].set_xlabel("Time (months)")
axes[0].set_ylabel("Biomarker Level")
axes[0].set_title("Spline Regression Fits")
axes[0].legend()

# Right: derivative (rate of change)
deriv = spline_smooth.derivative()
axes[1].plot(t_fine, deriv(t_fine), "r-", linewidth=2)
axes[1].axhline(0, color="gray", linestyle="--")
axes[1].set_xlabel("Time (months)")
axes[1].set_ylabel("Rate of Change")
axes[1].set_title("Biomarker Rate of Change (1st derivative)")

# Find peak: where derivative crosses zero
roots = deriv.roots()
if len(roots) > 0:
    peak_time = roots[0]
    peak_val = spline_smooth(peak_time)
    axes[1].axvline(peak_time, color="red", linestyle=":", alpha=0.5)
    print(f"Peak biomarker: {peak_val:.2f} at time = {peak_time:.1f} months")

plt.tight_layout()
plt.savefig("spline_regression.png", dpi=150)

# Spline-based integration (area under curve)
auc = spline_smooth.integral(0, 36)
print(f"AUC (0-36 months): {auc:.2f}")
```

---

## 7. Cox Proportional Hazards Regression (lifelines)

```python
import pandas as pd
import numpy as np
from lifelines import CoxPHFitter, KaplanMeierFitter
from lifelines.statistics import logrank_test
import matplotlib.pyplot as plt

df = pd.read_csv("survival_data.csv")

# Prepare covariates: continuous + dummy-encoded categorical
cox_df = df[["time", "event", "age", "sex", "treatment",
             "tumor_size", "biomarker_level"]].copy()
# Encode sex as numeric (0/1)
cox_df["sex"] = (cox_df["sex"] == "M").astype(int)

# Fit Cox PH model
cph = CoxPHFitter(penalizer=0.01)  # small L2 penalty for stability
cph.fit(cox_df, duration_col="time", event_col="event")
cph.print_summary()

# Hazard ratios with CIs
hr_df = cph.summary[["exp(coef)", "exp(coef) lower 95%", "exp(coef) upper 95%", "p"]].copy()
hr_df.columns = ["HR", "HR_lower", "HR_upper", "p_value"]
print(f"\nHazard Ratios:\n{hr_df.round(3)}")

# Check proportional hazards assumption
print("\n--- PH Assumption Test ---")
ph_results = cph.check_assumptions(cox_df, p_value_threshold=0.05, show_plots=False)

# Concordance index (discrimination)
c_index = cph.concordance_index_
print(f"\nConcordance index: {c_index:.3f}")

# Forest plot
fig, ax = plt.subplots(figsize=(8, 5))
cph.plot(ax=ax)
ax.axvline(0, color="black", linestyle="--", linewidth=0.5)
ax.set_title(f"Cox PH Forest Plot (C-index = {c_index:.3f})")
plt.tight_layout()
plt.savefig("cox_forest.png", dpi=150)

# Adjusted survival curves for specific covariate profiles
fig2, ax2 = plt.subplots(figsize=(8, 6))
cph.plot_partial_effects_on_outcome(
    covariates="treatment",
    values=[0, 1],
    ax=ax2
)
ax2.set_title("Adjusted Survival by Treatment")
plt.tight_layout()
plt.savefig("cox_adjusted_survival.png", dpi=150)
```

---

## 8. Mixed Effects Models (statsmodels MixedLM)

```python
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt

df = pd.read_csv("longitudinal_study.csv")

# Random intercept model: patients within centers
# Fixed: treatment, time, treatment:time interaction
# Random: intercept per subject (accounts for repeated measures)
model_ri = smf.mixedlm(
    "outcome ~ treatment * time + age + C(sex)",
    data=df,
    groups=df["subject_id"],
    re_formula="~1"          # random intercept only
)
result_ri = model_ri.fit(reml=True)
print("=== Random Intercept Model ===")
print(result_ri.summary())

# Random intercept + random slope model
# Each subject has their own baseline AND trajectory
model_rs = smf.mixedlm(
    "outcome ~ treatment * time + age + C(sex)",
    data=df,
    groups=df["subject_id"],
    re_formula="~time"       # random intercept + random slope for time
)
result_rs = model_rs.fit(reml=True)
print("\n=== Random Intercept + Slope Model ===")
print(result_rs.summary())

# Compare models using AIC/BIC
print(f"\nModel Comparison:")
print(f"  Random intercept:      AIC={result_ri.aic:.1f}, BIC={result_ri.bic:.1f}")
print(f"  Random intercept+slope: AIC={result_rs.aic:.1f}, BIC={result_rs.bic:.1f}")
better = "intercept+slope" if result_rs.aic < result_ri.aic else "intercept only"
print(f"  Better model (by AIC): {better}")

# Fixed effects table
best = result_rs if result_rs.aic < result_ri.aic else result_ri
fe = pd.DataFrame({
    "coef": best.fe_params,
    "se": best.bse_fe,
    "p_value": best.pvalues
})
fe["ci_lower"] = fe["coef"] - 1.96 * fe["se"]
fe["ci_upper"] = fe["coef"] + 1.96 * fe["se"]
print(f"\nFixed Effects:\n{fe.round(4)}")

# ICC: proportion of variance explained by between-subject differences
var_random = best.cov_re.iloc[0, 0]
var_residual = best.scale
icc = var_random / (var_random + var_residual)
print(f"\nICC: {icc:.3f} ({icc*100:.1f}% of variance is between-subject)")

# Plot individual trajectories colored by treatment
fig, ax = plt.subplots(figsize=(10, 7))
for subj in df["subject_id"].unique()[:20]:
    subj_data = df[df["subject_id"] == subj]
    color = "steelblue" if subj_data["treatment"].iloc[0] == 1 else "salmon"
    ax.plot(subj_data["time"], subj_data["outcome"], alpha=0.3, color=color)
ax.set_xlabel("Time")
ax.set_ylabel("Outcome")
ax.set_title("Individual Trajectories by Treatment")
plt.tight_layout()
plt.savefig("mixed_effects_trajectories.png", dpi=150)
```

---

## 9. Model Comparison (AIC, BIC, Likelihood Ratio Test)

```python
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats

df = pd.read_csv("model_comparison_data.csv")

# Fit nested models (Model 1 is nested within Model 2)
model1 = smf.ols("outcome ~ age + sex", data=df).fit()
model2 = smf.ols("outcome ~ age + sex + biomarker_A", data=df).fit()
model3 = smf.ols("outcome ~ age + sex + biomarker_A + biomarker_B + biomarker_C", data=df).fit()

# AIC / BIC comparison table
models = {"Base (age+sex)": model1,
          "+Biomarker A": model2,
          "+Biomarkers A,B,C": model3}

comparison = pd.DataFrame({
    name: {
        "R_squared": m.rsquared,
        "Adj_R_squared": m.rsquared_adj,
        "AIC": m.aic,
        "BIC": m.bic,
        "n_params": m.df_model + 1,
        "Log_Likelihood": m.llf
    }
    for name, m in models.items()
}).T
print("Model Comparison:")
print(comparison.round(3))

# Likelihood Ratio Test: compare nested models
def likelihood_ratio_test(model_restricted, model_full):
    """LRT for nested models. Tests whether full model is significantly better."""
    lr_stat = 2 * (model_full.llf - model_restricted.llf)
    df_diff = model_full.df_model - model_restricted.df_model
    p_value = stats.chi2.sf(lr_stat, df_diff)
    return lr_stat, df_diff, p_value

# Test: does adding biomarker_A improve the model?
lr, df_diff, p = likelihood_ratio_test(model1, model2)
print(f"\nLRT: Base vs +Biomarker A")
print(f"  Chi-square = {lr:.3f}, df = {df_diff}, p = {p:.4f}")
print(f"  {'Significant' if p < 0.05 else 'Not significant'}: "
      f"biomarker A {'does' if p < 0.05 else 'does not'} improve the model")

# Test: do biomarkers B and C add further value beyond A?
lr2, df2, p2 = likelihood_ratio_test(model2, model3)
print(f"\nLRT: +Biomarker A vs +Biomarkers A,B,C")
print(f"  Chi-square = {lr2:.3f}, df = {df2}, p = {p2:.4f}")
print(f"  {'Significant' if p2 < 0.05 else 'Not significant'}")

# Delta AIC interpretation
best_aic = min(m.aic for m in models.values())
print(f"\nDelta AIC (from best model):")
for name, m in models.items():
    delta = m.aic - best_aic
    support = "strong" if delta < 2 else "moderate" if delta < 7 else "weak"
    print(f"  {name}: delta_AIC = {delta:.1f} ({support} support)")
```

---

## 10. Residual Diagnostics and Q-Q Plots

```python
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
import matplotlib.pyplot as plt

df = pd.read_csv("regression_data.csv")
result = smf.ols("outcome ~ age + treatment + biomarker", data=df).fit()

# Comprehensive residual analysis
fig, axes = plt.subplots(2, 3, figsize=(18, 12))

# 1. Residuals vs Fitted (check linearity and homoscedasticity)
axes[0, 0].scatter(result.fittedvalues, result.resid, alpha=0.4, s=15)
axes[0, 0].axhline(0, color="red", linestyle="--")
# Add LOWESS smooth to detect patterns
from statsmodels.nonparametric.smoothers_lowess import lowess
smooth = lowess(result.resid, result.fittedvalues, frac=0.3)
axes[0, 0].plot(smooth[:, 0], smooth[:, 1], "r-", linewidth=2)
axes[0, 0].set_xlabel("Fitted Values")
axes[0, 0].set_ylabel("Residuals")
axes[0, 0].set_title("Residuals vs Fitted")

# 2. Q-Q plot (check normality of residuals)
stats.probplot(result.resid, dist="norm", plot=axes[0, 1])
axes[0, 1].set_title("Q-Q Plot")

# 3. Histogram of residuals with normal overlay
axes[0, 2].hist(result.resid, bins=30, density=True, edgecolor="black", alpha=0.7)
x_norm = np.linspace(result.resid.min(), result.resid.max(), 100)
axes[0, 2].plot(x_norm, stats.norm.pdf(x_norm, result.resid.mean(), result.resid.std()),
                "r-", linewidth=2)
axes[0, 2].set_title("Residual Distribution")

# 4. Scale-location plot (check homoscedasticity)
standardized_resid = result.get_influence().resid_studentized_internal
axes[1, 0].scatter(result.fittedvalues, np.sqrt(np.abs(standardized_resid)),
                   alpha=0.4, s=15)
axes[1, 0].set_xlabel("Fitted Values")
axes[1, 0].set_ylabel("sqrt(|Standardized Residuals|)")
axes[1, 0].set_title("Scale-Location")

# 5. Residuals vs each predictor (check linearity per predictor)
for i, var in enumerate(["age", "biomarker"]):
    ax_idx = (1, 1) if i == 0 else (1, 2)
    axes[ax_idx].scatter(df[var], result.resid, alpha=0.4, s=15)
    axes[ax_idx].axhline(0, color="red", linestyle="--")
    axes[ax_idx].set_xlabel(var)
    axes[ax_idx].set_ylabel("Residuals")
    axes[ax_idx].set_title(f"Residuals vs {var}")

plt.tight_layout()
plt.savefig("residual_diagnostics.png", dpi=150)

# Formal tests
# Shapiro-Wilk: test normality of residuals
shapiro_stat, shapiro_p = stats.shapiro(result.resid[:5000])  # limit for large samples
print(f"Shapiro-Wilk normality test: W = {shapiro_stat:.4f}, p = {shapiro_p:.4f}")

# Breusch-Pagan: test homoscedasticity
from statsmodels.stats.diagnostic import het_breuschpagan
bp_stat, bp_p, _, _ = het_breuschpagan(result.resid, result.model.exog)
print(f"Breusch-Pagan heteroscedasticity: LM = {bp_stat:.4f}, p = {bp_p:.4f}")

# Durbin-Watson: test autocorrelation
from statsmodels.stats.stattools import durbin_watson
dw = durbin_watson(result.resid)
print(f"Durbin-Watson: {dw:.3f} (2.0 = no autocorrelation)")

# Cook's distance: identify influential observations
influence = result.get_influence()
cooks_d = influence.cooks_distance[0]
threshold = 4 / len(df)
influential = np.where(cooks_d > threshold)[0]
print(f"\nInfluential observations (Cook's D > {threshold:.4f}): {len(influential)}")
```

---

## 11. Confidence and Prediction Intervals

```python
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt

df = pd.read_csv("prediction_data.csv")

# Fit regression model
result = smf.ols("outcome ~ age + biomarker", data=df).fit()

# Generate new data points for prediction
new_data = pd.DataFrame({
    "age": np.linspace(df["age"].min(), df["age"].max(), 100),
    "biomarker": df["biomarker"].median()  # hold biomarker at median
})

# Confidence interval: uncertainty about the MEAN response
# (where the regression line is)
ci_pred = result.get_prediction(new_data)
ci_frame = ci_pred.summary_frame(alpha=0.05)

# Prediction interval: uncertainty about INDIVIDUAL observations
# (wider than CI, includes residual variance)
pi_frame = ci_pred.summary_frame(alpha=0.05)

fig, ax = plt.subplots(figsize=(10, 7))

# Plot observed data
ax.scatter(df["age"], df["outcome"], alpha=0.3, s=20, color="gray", label="Observed")

# Plot fitted line
ax.plot(new_data["age"], ci_frame["mean"], "b-", linewidth=2, label="Fitted")

# 95% Confidence interval (for the mean)
ax.fill_between(
    new_data["age"],
    ci_frame["mean_ci_lower"],
    ci_frame["mean_ci_upper"],
    alpha=0.3, color="blue", label="95% CI (mean)"
)

# 95% Prediction interval (for individual observations)
ax.fill_between(
    new_data["age"],
    ci_frame["obs_ci_lower"],
    ci_frame["obs_ci_upper"],
    alpha=0.1, color="red", label="95% PI (individual)"
)

ax.set_xlabel("Age")
ax.set_ylabel("Outcome")
ax.set_title("Regression with Confidence and Prediction Intervals")
ax.legend()
plt.tight_layout()
plt.savefig("confidence_prediction_intervals.png", dpi=150)

# Print predictions for specific new patients
patients = pd.DataFrame({
    "age": [30, 50, 70],
    "biomarker": [df["biomarker"].median()] * 3
})
preds = result.get_prediction(patients).summary_frame(alpha=0.05)
print("Predictions for specific patients:")
for i, age in enumerate([30, 50, 70]):
    print(f"  Age {age}: predicted = {preds.iloc[i]['mean']:.2f}, "
          f"95% CI = ({preds.iloc[i]['mean_ci_lower']:.2f}, {preds.iloc[i]['mean_ci_upper']:.2f}), "
          f"95% PI = ({preds.iloc[i]['obs_ci_lower']:.2f}, {preds.iloc[i]['obs_ci_upper']:.2f})")
```

---

## 12. Penalized Regression (Ridge, Lasso, Elastic Net)

```python
import numpy as np
import pandas as pd
from sklearn.linear_model import RidgeCV, LassoCV, ElasticNetCV
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
import matplotlib.pyplot as plt

df = pd.read_csv("high_dimensional_data.csv")

# Separate features and outcome
feature_cols = [c for c in df.columns if c.startswith("gene_")]
X = df[feature_cols].values
y = df["outcome"].values
print(f"Features: {X.shape[1]}, Samples: {X.shape[0]}")

# Standardize features (essential for penalized regression)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Ridge (L2): shrinks coefficients, keeps all features
ridge = RidgeCV(alphas=np.logspace(-4, 4, 50), cv=5)
ridge.fit(X_scaled, y)
print(f"\nRidge: alpha = {ridge.alpha_:.4f}, "
      f"R² = {ridge.score(X_scaled, y):.4f}")

# Lasso (L1): shrinks some coefficients to exactly zero (feature selection)
lasso = LassoCV(alphas=np.logspace(-4, 1, 50), cv=5, max_iter=10000)
lasso.fit(X_scaled, y)
n_nonzero = np.sum(lasso.coef_ != 0)
print(f"Lasso: alpha = {lasso.alpha_:.4f}, "
      f"R² = {lasso.score(X_scaled, y):.4f}, "
      f"features selected = {n_nonzero}/{X.shape[1]}")

# Elastic Net: combination of L1 and L2
enet = ElasticNetCV(l1_ratio=[0.1, 0.3, 0.5, 0.7, 0.9], cv=5, max_iter=10000)
enet.fit(X_scaled, y)
n_nonzero_en = np.sum(enet.coef_ != 0)
print(f"Elastic Net: alpha = {enet.alpha_:.4f}, l1_ratio = {enet.l1_ratio_:.1f}, "
      f"R² = {enet.score(X_scaled, y):.4f}, features = {n_nonzero_en}")

# Top selected features from Lasso
coef_df = pd.DataFrame({
    "gene": feature_cols,
    "lasso_coef": lasso.coef_,
    "ridge_coef": ridge.coef_
})
selected = coef_df[coef_df["lasso_coef"] != 0].sort_values("lasso_coef", key=abs, ascending=False)
print(f"\nTop Lasso-selected features:\n{selected.head(10).to_string(index=False)}")

# Coefficient path plot (Lasso)
alphas_path = np.logspace(-4, 1, 100)
coefs = []
for a in alphas_path:
    from sklearn.linear_model import Lasso
    l = Lasso(alpha=a, max_iter=10000)
    l.fit(X_scaled, y)
    coefs.append(l.coef_)
coefs = np.array(coefs)

fig, ax = plt.subplots(figsize=(10, 6))
for i in range(min(20, X.shape[1])):  # plot top 20 features
    ax.plot(np.log10(alphas_path), coefs[:, i], linewidth=0.8)
ax.axvline(np.log10(lasso.alpha_), color="black", linestyle="--", label="Selected alpha")
ax.set_xlabel("log10(alpha)")
ax.set_ylabel("Coefficient Value")
ax.set_title("Lasso Coefficient Path")
ax.legend()
plt.tight_layout()
plt.savefig("lasso_path.png", dpi=150)
```

---

## 13. Generalized Additive Models (GAM) for Nonlinear Effects

```python
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy.interpolate import BSpline
import matplotlib.pyplot as plt

df = pd.read_csv("nonlinear_data.csv")

# Manual GAM approximation using basis splines in statsmodels
# Create B-spline basis functions for the nonlinear predictor
from patsy import dmatrix

# Generate spline basis with 4 knots for 'age'
# bs() creates B-spline basis; cr() creates natural cubic spline basis
formula = "outcome ~ bs(age, df=5) + bs(biomarker, df=4) + treatment"
model = smf.ols(formula, data=df)
result = model.fit()
print(result.summary())
print(f"\nR-squared: {result.rsquared:.4f}")
print(f"AIC: {result.aic:.1f}")

# Compare with linear model
linear_result = smf.ols("outcome ~ age + biomarker + treatment", data=df).fit()
print(f"\nLinear model: R² = {linear_result.rsquared:.4f}, AIC = {linear_result.aic:.1f}")
print(f"Spline model: R² = {result.rsquared:.4f}, AIC = {result.aic:.1f}")
print(f"Nonlinearity improves fit: {'Yes' if result.aic < linear_result.aic else 'No'}")

# Plot partial effects: age
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Partial effect of age (holding biomarker at median, treatment at 0)
age_range = np.linspace(df["age"].min(), df["age"].max(), 100)
pred_data = pd.DataFrame({
    "age": age_range,
    "biomarker": df["biomarker"].median(),
    "treatment": 0
})
predictions = result.get_prediction(pred_data).summary_frame(alpha=0.05)
axes[0].plot(age_range, predictions["mean"], "b-", linewidth=2)
axes[0].fill_between(age_range, predictions["mean_ci_lower"],
                     predictions["mean_ci_upper"], alpha=0.2)
axes[0].scatter(df["age"], df["outcome"], alpha=0.1, s=10, color="gray")
axes[0].set_xlabel("Age")
axes[0].set_ylabel("Outcome")
axes[0].set_title("Partial Effect of Age (spline)")

# Partial effect of biomarker
bio_range = np.linspace(df["biomarker"].min(), df["biomarker"].max(), 100)
pred_data2 = pd.DataFrame({
    "age": df["age"].median(),
    "biomarker": bio_range,
    "treatment": 0
})
predictions2 = result.get_prediction(pred_data2).summary_frame(alpha=0.05)
axes[1].plot(bio_range, predictions2["mean"], "r-", linewidth=2)
axes[1].fill_between(bio_range, predictions2["mean_ci_lower"],
                     predictions2["mean_ci_upper"], alpha=0.2)
axes[1].set_xlabel("Biomarker")
axes[1].set_ylabel("Outcome")
axes[1].set_title("Partial Effect of Biomarker (spline)")

plt.tight_layout()
plt.savefig("gam_partial_effects.png", dpi=150)
```

---

## 14. Robust Regression (Outlier-Resistant)

```python
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt

df = pd.read_csv("data_with_outliers.csv")

# Standard OLS (sensitive to outliers)
ols_result = smf.ols("outcome ~ predictor", data=df).fit()

# Robust regression using M-estimator (Huber's T)
# Downweights observations with large residuals
rlm_huber = smf.rlm("outcome ~ predictor", data=df, M=sm.robust.norms.HuberT())
rlm_result = rlm_huber.fit()

# Bisquare (Tukey's biweight): more aggressive outlier downweighting
rlm_bisquare = smf.rlm("outcome ~ predictor", data=df, M=sm.robust.norms.TukeyBiweight())
rlm_bi_result = rlm_bisquare.fit()

print("=== OLS ===")
print(f"  Slope: {ols_result.params['predictor']:.4f}, "
      f"Intercept: {ols_result.params['Intercept']:.4f}")

print("=== Huber M-estimator ===")
print(f"  Slope: {rlm_result.params['predictor']:.4f}, "
      f"Intercept: {rlm_result.params['Intercept']:.4f}")

print("=== Tukey Bisquare ===")
print(f"  Slope: {rlm_bi_result.params['predictor']:.4f}, "
      f"Intercept: {rlm_bi_result.params['Intercept']:.4f}")

# Identify downweighted observations (potential outliers)
weights = rlm_result.weights
outliers = df[weights < 0.5]
print(f"\nOutliers detected (weight < 0.5): {len(outliers)}")

# Plot comparison
fig, ax = plt.subplots(figsize=(10, 7))
ax.scatter(df["predictor"], df["outcome"], alpha=0.4, s=20)
x_range = np.linspace(df["predictor"].min(), df["predictor"].max(), 100)
ax.plot(x_range, ols_result.params["Intercept"] + ols_result.params["predictor"] * x_range,
        "r-", label="OLS", linewidth=2)
ax.plot(x_range, rlm_result.params["Intercept"] + rlm_result.params["predictor"] * x_range,
        "g--", label="Huber", linewidth=2)
ax.plot(x_range, rlm_bi_result.params["Intercept"] + rlm_bi_result.params["predictor"] * x_range,
        "b:", label="Bisquare", linewidth=2)
# Mark outliers
if len(outliers) > 0:
    ax.scatter(outliers["predictor"], outliers["outcome"],
               s=80, facecolors="none", edgecolors="red", linewidths=2, label="Outliers")
ax.set_xlabel("Predictor")
ax.set_ylabel("Outcome")
ax.set_title("OLS vs Robust Regression")
ax.legend()
plt.tight_layout()
plt.savefig("robust_regression.png", dpi=150)
```

---

## 15. Negative Binomial Regression (Count Data with Overdispersion)

```python
import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats

df = pd.read_csv("count_data.csv")

# Check for overdispersion: variance >> mean suggests negative binomial
print("Outcome summary:")
print(f"  Mean: {df['count'].mean():.2f}")
print(f"  Variance: {df['count'].var():.2f}")
print(f"  Var/Mean ratio: {df['count'].var() / df['count'].mean():.2f}")
print(f"  Overdispersed: {'Yes' if df['count'].var() > df['count'].mean() * 1.5 else 'No'}")

# Poisson regression (assumes var = mean)
poisson = smf.glm("count ~ age + treatment + exposure",
                   data=df,
                   family=sm.families.Poisson()).fit()

# Negative binomial (accounts for overdispersion)
# alpha parameter controls overdispersion (0 = Poisson)
negbin = smf.glm("count ~ age + treatment + exposure",
                  data=df,
                  family=sm.families.NegativeBinomial(alpha=1.0)).fit()

print("\n=== Poisson Regression ===")
print(f"AIC: {poisson.aic:.1f}")
for var in poisson.params.index:
    rr = np.exp(poisson.params[var])
    ci = np.exp(poisson.conf_int().loc[var])
    print(f"  {var}: RR = {rr:.3f} ({ci[0]:.3f}-{ci[1]:.3f}), p = {poisson.pvalues[var]:.4f}")

print("\n=== Negative Binomial Regression ===")
print(f"AIC: {negbin.aic:.1f}")
for var in negbin.params.index:
    rr = np.exp(negbin.params[var])
    ci = np.exp(negbin.conf_int().loc[var])
    print(f"  {var}: RR = {rr:.3f} ({ci[0]:.3f}-{ci[1]:.3f}), p = {negbin.pvalues[var]:.4f}")

print(f"\nBetter model (by AIC): "
      f"{'Negative Binomial' if negbin.aic < poisson.aic else 'Poisson'}")
```
