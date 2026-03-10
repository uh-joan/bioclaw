# Survival Analysis Recipes (scikit-survival)

Python code templates for survival analysis using scikit-survival (sksurv). Covers Kaplan-Meier, Cox models, ensemble methods, evaluation metrics, competing risks, and model comparison pipelines.

Cross-skill routing: use `statistical-modeling` SKILL.md for lifelines-based survival analysis, `biostat-recipes` for general statistical tests.

---

## 1. Create Survival Outcome Array with Surv

Create the structured array required by all scikit-survival estimators.

```python
import numpy as np
from sksurv.util import Surv

# From separate arrays
event = np.array([True, False, True, True, False, True])
time = np.array([12.5, 24.0, 8.3, 15.1, 30.0, 5.7])
y = Surv.from_arrays(event, time)
print(y.dtype)  # [('event', '?'), ('time', '<f8')]

# From a DataFrame
import pandas as pd
df = pd.read_csv("survival_data.csv")
y = Surv.from_dataframe("event", "time", df)

# From indicator column (0/1 instead of bool)
y = Surv.from_arrays(df["status"].astype(bool), df["duration"])
print(f"Events: {y['event'].sum()}, Censored: {(~y['event']).sum()}")
```

---

## 2. Kaplan-Meier Estimator and Survival Curve

Non-parametric survival function estimation with confidence intervals.

```python
import matplotlib.pyplot as plt
from sksurv.nonparametric import kaplan_meier_estimator

# Estimate survival function
time_points, survival_prob = kaplan_meier_estimator(y["event"], y["time"])

# Plot survival curve
fig, ax = plt.subplots(figsize=(10, 6))
ax.step(time_points, survival_prob, where="post", label="KM estimate")
ax.set_xlabel("Time")
ax.set_ylabel("Survival Probability")
ax.set_title("Kaplan-Meier Survival Curve")
ax.set_ylim(0, 1.05)
ax.legend()
plt.tight_layout()
plt.savefig("km_curve_sksurv.png", dpi=150)

# With confidence intervals
time_points, survival_prob, ci = kaplan_meier_estimator(
    y["event"], y["time"], conf_type="log-log"
)
ax.fill_between(time_points, ci[0], ci[1], alpha=0.2, step="post")
```

---

## 3. Nelson-Aalen Cumulative Hazard Estimator

Non-parametric cumulative hazard estimation.

```python
from sksurv.nonparametric import nelson_aalen_estimator
import matplotlib.pyplot as plt

time_points, cum_hazard = nelson_aalen_estimator(y["event"], y["time"])

fig, ax = plt.subplots(figsize=(10, 6))
ax.step(time_points, cum_hazard, where="post", label="Nelson-Aalen")
ax.set_xlabel("Time")
ax.set_ylabel("Cumulative Hazard")
ax.set_title("Nelson-Aalen Cumulative Hazard Estimate")
ax.legend()
plt.tight_layout()
plt.savefig("nelson_aalen.png", dpi=150)
```

---

## 4. Cox Proportional Hazards Model (Basic Fit + Predict)

Fit a Cox PH model with covariates, extract coefficients, and predict risk scores.

```python
import pandas as pd
from sksurv.linear_model import CoxPHSurvivalAnalysis
from sksurv.util import Surv

df = pd.read_csv("survival_data.csv")
y = Surv.from_dataframe("event", "time", df)
X = df[["age", "treatment", "biomarker", "stage"]].copy()
X = X.astype(float)

# Fit model
cox = CoxPHSurvivalAnalysis(alpha=0.0001)
cox.fit(X, y)

# Coefficients (log hazard ratios)
import numpy as np
print("Covariate       | Coef     | HR")
for name, coef in zip(X.columns, cox.coef_):
    print(f"  {name:<14} | {coef:+.4f}  | {np.exp(coef):.4f}")

# Predict risk scores (higher = higher risk)
risk_scores = cox.predict(X)
print(f"\nRisk score range: {risk_scores.min():.3f} to {risk_scores.max():.3f}")

# Predict survival function for a new patient
surv_funcs = cox.predict_survival_function(X.iloc[:3])
for i, fn in enumerate(surv_funcs):
    print(f"Patient {i}: P(survive > 12) = {fn(12):.3f}")
```

---

## 5. Penalized Cox with Elastic Net (CoxnetSurvivalAnalysis)

Cox regression with elastic net penalty for high-dimensional data (many covariates).

```python
import numpy as np
from sksurv.linear_model import CoxnetSurvivalAnalysis
from sklearn.preprocessing import StandardScaler

# Standardize features (important for penalized models)
scaler = StandardScaler()
X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=X.columns)

# Fit with elastic net (l1_ratio=1.0 is Lasso, 0.0 is Ridge)
coxnet = CoxnetSurvivalAnalysis(l1_ratio=0.5, alpha_min_ratio=0.01, n_alphas=100)
coxnet.fit(X_scaled, y)

# Coefficients at each alpha along the regularization path
print(f"Alphas tested: {len(coxnet.alphas_)}")
print(f"Coef shape: {coxnet.coef_.shape}")  # (n_alphas, n_features)

# Select best alpha via cross-validation
from sklearn.model_selection import GridSearchCV
from sksurv.metrics import concordance_index_censored

coxnet_cv = CoxnetSurvivalAnalysis(l1_ratio=0.5, fit_baseline_model=True)
alphas = coxnet.alphas_  # reuse the path
best_ci = 0
best_alpha = None
for a in alphas:
    coxnet_cv.set_params(alphas=[a])
    coxnet_cv.fit(X_scaled, y)
    pred = coxnet_cv.predict(X_scaled)
    ci = concordance_index_censored(y["event"], y["time"], pred)[0]
    if ci > best_ci:
        best_ci, best_alpha = ci, a

print(f"Best alpha: {best_alpha:.6f}, C-index: {best_ci:.4f}")

# Non-zero coefficients at best alpha
coxnet_cv.set_params(alphas=[best_alpha])
coxnet_cv.fit(X_scaled, y)
nonzero = X.columns[coxnet_cv.coef_.ravel() != 0]
print(f"Selected features ({len(nonzero)}): {list(nonzero)}")
```

---

## 6. Random Survival Forest

Ensemble tree-based survival model that captures non-linear effects.

```python
from sksurv.ensemble import RandomSurvivalForest
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42
)

rsf = RandomSurvivalForest(
    n_estimators=500,
    min_samples_split=10,
    min_samples_leaf=5,
    max_features="sqrt",
    n_jobs=-1,
    random_state=42,
)
rsf.fit(X_train, y_train)

# Evaluate concordance index
from sksurv.metrics import concordance_index_censored
pred = rsf.predict(X_test)
ci = concordance_index_censored(y_test["event"], y_test["time"], pred)
print(f"C-index: {ci[0]:.4f}")
print(f"Concordant: {ci[1]}, Discordant: {ci[2]}, Tied: {ci[3]}")

# Predict survival function for individual patients
surv_funcs = rsf.predict_survival_function(X_test.iloc[:3])
for i, fn in enumerate(surv_funcs):
    print(f"Patient {i}: P(survive > 24) = {fn(24):.3f}")
```

---

## 7. Gradient Boosting Survival Analysis

Gradient-boosted model for survival data with regularization control.

```python
from sksurv.ensemble import GradientBoostingSurvivalAnalysis
from sksurv.metrics import concordance_index_censored

gbs = GradientBoostingSurvivalAnalysis(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=3,
    min_samples_split=10,
    min_samples_leaf=5,
    subsample=0.8,
    random_state=42,
)
gbs.fit(X_train, y_train)

# Evaluate
pred_train = gbs.predict(X_train)
pred_test = gbs.predict(X_test)
ci_train = concordance_index_censored(y_train["event"], y_train["time"], pred_train)[0]
ci_test = concordance_index_censored(y_test["event"], y_test["time"], pred_test)[0]
print(f"C-index train: {ci_train:.4f}, test: {ci_test:.4f}")

# Staged prediction to find optimal n_estimators
import matplotlib.pyplot as plt
test_scores = []
for pred in gbs.staged_predict(X_test):
    ci = concordance_index_censored(y_test["event"], y_test["time"], pred)[0]
    test_scores.append(ci)

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(range(1, len(test_scores) + 1), test_scores)
ax.set_xlabel("Number of Boosting Iterations")
ax.set_ylabel("C-index (test)")
ax.set_title("GBS Performance vs Iterations")
plt.tight_layout()
plt.savefig("gbs_staged.png", dpi=150)
```

---

## 8. Concordance Index Evaluation (Harrell's and Uno's)

Compare model discrimination using concordance indices.

```python
from sksurv.metrics import concordance_index_censored, concordance_index_ipcw

# Harrell's C-index (standard)
pred = cox.predict(X_test)
c_harrell = concordance_index_censored(
    y_test["event"], y_test["time"], pred
)
print(f"Harrell's C-index: {c_harrell[0]:.4f}")
print(f"  Concordant pairs: {c_harrell[1]}")
print(f"  Discordant pairs: {c_harrell[2]}")
print(f"  Tied risk: {c_harrell[3]}")

# Uno's C-index (accounts for censoring distribution)
# Requires training set y to estimate censoring weights
tau = y_test["time"].max() * 0.9  # restrict to 90th percentile of follow-up
c_uno = concordance_index_ipcw(
    y_train, y_test, pred, tau=tau
)
print(f"Uno's C-index: {c_uno[0]:.4f}")
print(f"  (tau={tau:.1f})")
```

---

## 9. Time-Dependent AUC at Specific Time Points

Evaluate model discrimination at clinically relevant time horizons.

```python
from sksurv.metrics import cumulative_dynamic_auc
import matplotlib.pyplot as plt
import numpy as np

# Define time points of interest (e.g., 6, 12, 24, 36 months)
times = np.array([6, 12, 24, 36])
# Filter to times within observed range
times = times[times < y_test["time"].max()]

pred = cox.predict(X_test)

# Compute time-dependent AUC
auc_values, mean_auc = cumulative_dynamic_auc(
    y_train, y_test, pred, times
)

print(f"Mean AUC: {mean_auc:.4f}")
for t, auc in zip(times, auc_values):
    print(f"  AUC at t={t}: {auc:.4f}")

# Plot AUC over time
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(times, auc_values, marker="o")
ax.axhline(0.5, color="grey", linestyle="--", label="Random")
ax.set_xlabel("Time")
ax.set_ylabel("Time-dependent AUC")
ax.set_title("Cumulative/Dynamic AUC")
ax.set_ylim(0.4, 1.0)
ax.legend()
plt.tight_layout()
plt.savefig("time_dependent_auc.png", dpi=150)
```

---

## 10. Integrated Brier Score

Evaluate calibration and overall predictive accuracy over the full time range.

```python
from sksurv.metrics import integrated_brier_score, brier_score
import numpy as np

# Predict survival functions (needed for Brier score, not risk scores)
surv_funcs = cox.predict_survival_function(X_test)

# Define evaluation time grid
times = np.linspace(
    y_test["time"].min() + 1,
    y_test["time"].max() * 0.9,
    50
)

# Convert survival functions to matrix of probabilities at each time
surv_matrix = np.row_stack([fn(times) for fn in surv_funcs])

# Integrated Brier Score (lower is better; 0.25 = random for 50% event rate)
ibs = integrated_brier_score(y_train, y_test, surv_matrix, times)
print(f"Integrated Brier Score: {ibs:.4f}")

# Brier score at individual time points
for t_idx in [0, len(times) // 4, len(times) // 2, 3 * len(times) // 4, -1]:
    t = times[t_idx]
    preds_at_t = surv_matrix[:, t_idx]
    _, bs = brier_score(y_train, y_test, preds_at_t, t)
    print(f"  Brier score at t={t:.1f}: {bs[0]:.4f}")
```

---

## 11. Model Comparison Pipeline (Cox vs RSF vs GBS)

Compare multiple survival models on the same data using concordance index and IBS.

```python
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sksurv.linear_model import CoxPHSurvivalAnalysis
from sksurv.ensemble import RandomSurvivalForest, GradientBoostingSurvivalAnalysis
from sksurv.metrics import (
    concordance_index_censored, integrated_brier_score
)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42
)

models = {
    "Cox PH": CoxPHSurvivalAnalysis(alpha=0.001),
    "RSF": RandomSurvivalForest(n_estimators=300, max_features="sqrt",
                                 min_samples_leaf=5, random_state=42, n_jobs=-1),
    "GBS": GradientBoostingSurvivalAnalysis(n_estimators=200, learning_rate=0.05,
                                             max_depth=3, random_state=42),
}

times = np.linspace(
    y_test["time"].min() + 1,
    y_test["time"].max() * 0.9,
    50
)

results = []
for name, model in models.items():
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    ci = concordance_index_censored(y_test["event"], y_test["time"], pred)[0]

    surv_funcs = model.predict_survival_function(X_test)
    surv_matrix = np.row_stack([fn(times) for fn in surv_funcs])
    ibs = integrated_brier_score(y_train, y_test, surv_matrix, times)

    results.append({"Model": name, "C-index": ci, "IBS": ibs})
    print(f"{name}: C-index={ci:.4f}, IBS={ibs:.4f}")

results_df = pd.DataFrame(results).sort_values("C-index", ascending=False)
print("\n", results_df.to_string(index=False))
```

---

## 12. Competing Risks Analysis (Cumulative Incidence)

Estimate cumulative incidence when multiple event types compete.

```python
import numpy as np
import matplotlib.pyplot as plt
from sksurv.nonparametric import CumulativeIncidenceFunction

# Event indicator: 0 = censored, 1 = event of interest, 2 = competing event
event_indicator = np.array([1, 0, 2, 1, 2, 0, 1, 2, 1, 0])
time = np.array([5, 10, 7, 12, 3, 15, 8, 6, 9, 20])

# Compute cumulative incidence for each event type
cif = CumulativeIncidenceFunction()
cif.fit(event_indicator, time)

fig, ax = plt.subplots(figsize=(10, 6))
for event_type, (times_e, cuminc_e) in cif.cumulative_incidence_.items():
    ax.step(times_e, cuminc_e, where="post", label=f"Event {event_type}")

ax.set_xlabel("Time")
ax.set_ylabel("Cumulative Incidence")
ax.set_title("Competing Risks: Cumulative Incidence Functions")
ax.set_ylim(0, 1.0)
ax.legend()
plt.tight_layout()
plt.savefig("competing_risks_cif.png", dpi=150)
```

---

## 13. Cross-Validated Hyperparameter Tuning with Survival Scorer

Grid search with a concordance-index-based scorer for survival models.

```python
import numpy as np
from sklearn.model_selection import GridSearchCV, KFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sksurv.ensemble import GradientBoostingSurvivalAnalysis
from sksurv.metrics import concordance_index_censored

# Define a custom scorer compatible with sklearn GridSearchCV
def c_index_scorer(estimator, X, y):
    """Scorer that returns Harrell's C-index."""
    pred = estimator.predict(X)
    return concordance_index_censored(y["event"], y["time"], pred)[0]

# Parameter grid
param_grid = {
    "n_estimators": [100, 200, 300],
    "learning_rate": [0.01, 0.05, 0.1],
    "max_depth": [2, 3, 4],
    "min_samples_leaf": [5, 10, 20],
}

gbs = GradientBoostingSurvivalAnalysis(random_state=42, subsample=0.8)
cv = KFold(n_splits=5, shuffle=True, random_state=42)

grid_search = GridSearchCV(
    gbs, param_grid, scoring=c_index_scorer,
    cv=cv, n_jobs=-1, verbose=1
)
grid_search.fit(X_train, y_train)

print(f"Best C-index (CV): {grid_search.best_score_:.4f}")
print(f"Best params: {grid_search.best_params_}")

# Evaluate best model on test set
best_pred = grid_search.predict(X_test)
ci_test = concordance_index_censored(y_test["event"], y_test["time"], best_pred)[0]
print(f"Test C-index: {ci_test:.4f}")
```

---

## 14. Feature Importance via Permutation

Assess which features contribute most to model predictions.

```python
import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance
from sksurv.metrics import concordance_index_censored
import matplotlib.pyplot as plt

def c_index_scorer(estimator, X, y):
    """Scorer for permutation importance."""
    pred = estimator.predict(X)
    return concordance_index_censored(y["event"], y["time"], pred)[0]

# Compute permutation importance on test set
result = permutation_importance(
    rsf, X_test, y_test,
    scoring=c_index_scorer,
    n_repeats=30,
    random_state=42,
    n_jobs=-1,
)

# Summarize and sort by importance
importance_df = pd.DataFrame({
    "feature": X.columns,
    "importance_mean": result.importances_mean,
    "importance_std": result.importances_std,
}).sort_values("importance_mean", ascending=False)

print("Feature Importance (permutation, C-index drop):")
for _, row in importance_df.iterrows():
    print(f"  {row['feature']:<20} {row['importance_mean']:.4f} +/- {row['importance_std']:.4f}")

# Plot
fig, ax = plt.subplots(figsize=(8, 6))
ax.barh(importance_df["feature"], importance_df["importance_mean"],
        xerr=importance_df["importance_std"], color="steelblue")
ax.set_xlabel("Mean C-index Decrease")
ax.set_title("Permutation Feature Importance (RSF)")
ax.invert_yaxis()
plt.tight_layout()
plt.savefig("feature_importance_surv.png", dpi=150)
```
