# Machine Learning Biomarker Panel Selection Recipes

Executable code templates for ML-driven biomarker panel discovery, feature selection, and clinical validation scoring.
Each recipe is production-ready Python with inline parameter documentation.

> **Parent skill**: [SKILL.md](SKILL.md) — full biomarker discovery and validation pipeline with MCP tools.
> **See also**: [drug-target-analyst](../drug-target-analyst/SKILL.md) for target validation, [clinical-trial-analyst](../clinical-trial-analyst/SKILL.md) for translational endpoints.

---

## Recipe 1: Mutual Information Feature Ranking

Rank biomarkers by mutual information with the clinical outcome. Non-parametric, captures nonlinear associations that Pearson correlation would miss.

```python
import numpy as np
import pandas as pd
from sklearn.feature_selection import mutual_info_classif

def rank_by_mutual_information(X, y, feature_names=None, n_neighbors=5, random_state=42):
    """
    Rank biomarker features by mutual information with outcome.

    Parameters
    ----------
    X : array-like, shape (n_samples, n_features)
        Biomarker measurements (expression, mutation status, methylation, etc.)
    y : array-like, shape (n_samples,)
        Binary outcome (0/1: non-responder/responder, alive/dead, etc.)
    feature_names : list of str, optional
        Names of features (gene symbols, biomarker IDs)
    n_neighbors : int
        Number of neighbors for MI estimation (default: 5; higher = smoother but slower)
    random_state : int
        Random seed for reproducibility

    Returns
    -------
    DataFrame with features ranked by mutual information score
    """
    X = np.asarray(X)
    y = np.asarray(y)

    if feature_names is None:
        feature_names = [f"feature_{i}" for i in range(X.shape[1])]

    # Compute mutual information
    mi_scores = mutual_info_classif(
        X, y,
        n_neighbors=n_neighbors,
        random_state=random_state,
    )

    # Build results DataFrame
    results = pd.DataFrame({
        "feature": feature_names,
        "mutual_information": mi_scores,
    }).sort_values("mutual_information", ascending=False).reset_index(drop=True)

    # Add rank and normalized score
    results["rank"] = range(1, len(results) + 1)
    max_mi = results["mutual_information"].max()
    results["normalized_mi"] = results["mutual_information"] / max_mi if max_mi > 0 else 0

    # Classification
    results["importance"] = results["normalized_mi"].apply(
        lambda x: "HIGH" if x >= 0.5 else "MODERATE" if x >= 0.2 else "LOW"
    )

    print(f"Mutual Information Feature Ranking")
    print(f"Samples: {X.shape[0]}, Features: {X.shape[1]}")
    print(f"Outcome balance: {np.mean(y):.1%} positive\n")
    print(results.head(20).to_string(index=False))

    return results


# Example usage
np.random.seed(42)
n_samples, n_features = 200, 50
X = np.random.randn(n_samples, n_features)
y = (X[:, 0] + 0.5 * X[:, 3] + np.random.randn(n_samples) * 0.5 > 0).astype(int)
feature_names = [f"GENE_{i}" for i in range(n_features)]

results = rank_by_mutual_information(X, y, feature_names)
```

**Key Parameters:**
- `n_neighbors`: Controls MI estimation smoothness (3-10; default 5 is robust for most datasets)
- Works with continuous and discrete features alike
- Non-parametric: captures nonlinear biomarker-outcome relationships

**Expected Output:**
- Ranked DataFrame with mutual information scores, normalized scores (0-1), and importance tier (HIGH/MODERATE/LOW)

---

## Recipe 2: LASSO Feature Selection

Sparse biomarker panel selection using L1-penalized logistic regression with cross-validated regularization.

```python
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegressionCV
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold

def lasso_feature_selection(X, y, feature_names=None, n_folds=5, max_features=20, random_state=42):
    """
    Select sparse biomarker panel using LASSO (L1 logistic regression).

    Parameters
    ----------
    X : array-like, shape (n_samples, n_features)
        Biomarker measurements
    y : array-like, shape (n_samples,)
        Binary outcome
    feature_names : list of str, optional
        Feature names
    n_folds : int
        Number of CV folds for regularization tuning (default: 5)
    max_features : int
        Maximum desired features in panel (informational; actual count depends on lambda)
    random_state : int
        Random seed

    Returns
    -------
    dict with selected features, coefficients, and model performance
    """
    X = np.asarray(X, dtype=float)
    y = np.asarray(y)

    if feature_names is None:
        feature_names = [f"feature_{i}" for i in range(X.shape[1])]

    # Standardize features (essential for L1 penalty to be meaningful)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Cross-validated LASSO logistic regression
    cv = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=random_state)
    model = LogisticRegressionCV(
        penalty="l1",
        solver="saga",           # Required for L1 penalty
        Cs=20,                   # Number of regularization values to test
        cv=cv,
        scoring="roc_auc",
        max_iter=5000,
        random_state=random_state,
        n_jobs=-1,
    )
    model.fit(X_scaled, y)

    # Extract selected features (non-zero coefficients)
    coefficients = model.coef_[0]
    selected_mask = coefficients != 0
    selected_features = np.array(feature_names)[selected_mask]
    selected_coefficients = coefficients[selected_mask]

    # Sort by absolute coefficient magnitude
    sort_idx = np.argsort(-np.abs(selected_coefficients))
    selected_features = selected_features[sort_idx]
    selected_coefficients = selected_coefficients[sort_idx]

    # Cross-validated AUC at best C
    best_auc = model.scores_[1].mean(axis=0).max()  # Mean across folds at best C
    best_C = model.C_[0]

    results_df = pd.DataFrame({
        "feature": selected_features,
        "coefficient": np.round(selected_coefficients, 4),
        "abs_coefficient": np.round(np.abs(selected_coefficients), 4),
        "direction": ["POSITIVE (risk)" if c > 0 else "NEGATIVE (protective)"
                      for c in selected_coefficients],
    })

    result = {
        "n_selected": len(selected_features),
        "n_total": len(feature_names),
        "best_C": round(best_C, 6),
        "cv_auc": round(best_auc, 4),
        "selected_panel": results_df,
    }

    print(f"LASSO Feature Selection")
    print(f"Selected {len(selected_features)}/{len(feature_names)} features")
    print(f"Best regularization C: {best_C:.6f}")
    print(f"Cross-validated AUC: {best_auc:.4f}\n")
    print(results_df.to_string(index=False))

    return result


# Example usage
np.random.seed(42)
n_samples, n_features = 300, 100
X = np.random.randn(n_samples, n_features)
# True signal in features 0, 5, 10
y = (2 * X[:, 0] - 1.5 * X[:, 5] + X[:, 10] + np.random.randn(n_samples) > 0).astype(int)
feature_names = [f"BIOMARKER_{i}" for i in range(n_features)]

result = lasso_feature_selection(X, y, feature_names)
```

**Key Parameters:**
- `penalty="l1"`: L1 regularization drives non-informative feature coefficients to exactly zero
- `Cs=20`: Tests 20 regularization strengths; `LogisticRegressionCV` selects the best by AUC
- `solver="saga"`: Required for L1 penalty; supports large datasets efficiently
- Features must be standardized (StandardScaler) for fair penalization

**Expected Output:**
- Sparse panel of selected biomarkers with coefficients, direction of effect, and cross-validated AUC

---

## Recipe 3: Random Forest Feature Importance with Permutation Validation

Two-stage importance: impurity-based (fast, biased toward high-cardinality) validated by permutation importance (unbiased but slower).

```python
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.model_selection import StratifiedKFold, cross_val_score

def random_forest_importance(X, y, feature_names=None, n_estimators=500,
                             n_repeats=10, n_folds=5, random_state=42):
    """
    Compute random forest feature importance with permutation validation.

    Parameters
    ----------
    X : array-like, shape (n_samples, n_features)
        Biomarker measurements
    y : array-like, shape (n_samples,)
        Binary outcome
    feature_names : list of str, optional
        Feature names
    n_estimators : int
        Number of trees (default: 500)
    n_repeats : int
        Permutation importance repeats (default: 10)
    n_folds : int
        CV folds for baseline AUC estimation
    random_state : int
        Random seed

    Returns
    -------
    DataFrame with impurity importance, permutation importance, and consensus ranking
    """
    X = np.asarray(X, dtype=float)
    y = np.asarray(y)

    if feature_names is None:
        feature_names = [f"feature_{i}" for i in range(X.shape[1])]

    # Train random forest
    rf = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=None,
        min_samples_leaf=5,
        random_state=random_state,
        n_jobs=-1,
    )
    rf.fit(X, y)

    # Impurity-based importance (Gini importance)
    gini_imp = rf.feature_importances_

    # Permutation importance (unbiased)
    perm_result = permutation_importance(
        rf, X, y,
        n_repeats=n_repeats,
        random_state=random_state,
        n_jobs=-1,
        scoring="roc_auc",
    )
    perm_imp_mean = perm_result.importances_mean
    perm_imp_std = perm_result.importances_std

    # Cross-validated AUC
    cv = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=random_state)
    cv_auc = cross_val_score(rf, X, y, cv=cv, scoring="roc_auc")

    # Build results
    results = pd.DataFrame({
        "feature": feature_names,
        "gini_importance": np.round(gini_imp, 6),
        "perm_importance_mean": np.round(perm_imp_mean, 6),
        "perm_importance_std": np.round(perm_imp_std, 6),
    })

    # Consensus rank: average of Gini rank and permutation rank
    results["gini_rank"] = results["gini_importance"].rank(ascending=False)
    results["perm_rank"] = results["perm_importance_mean"].rank(ascending=False)
    results["consensus_rank"] = ((results["gini_rank"] + results["perm_rank"]) / 2)
    results = results.sort_values("consensus_rank").reset_index(drop=True)

    # Flag features where Gini and permutation disagree strongly
    results["rank_agreement"] = np.where(
        np.abs(results["gini_rank"] - results["perm_rank"]) <= 5,
        "AGREE",
        "DISAGREE — validate further"
    )

    print(f"Random Forest Feature Importance")
    print(f"Trees: {n_estimators}, CV AUC: {cv_auc.mean():.4f} +/- {cv_auc.std():.4f}\n")
    print(results.head(20).to_string(index=False))

    return results


# Example usage
np.random.seed(42)
n_samples, n_features = 250, 40
X = np.random.randn(n_samples, n_features)
y = (X[:, 0] ** 2 + X[:, 3] - X[:, 7] + np.random.randn(n_samples) * 0.3 > 1).astype(int)
feature_names = [f"MARKER_{i}" for i in range(n_features)]

results = random_forest_importance(X, y, feature_names)
```

**Key Parameters:**
- `n_estimators=500`: More trees = more stable importance estimates (diminishing returns beyond 500)
- `n_repeats=10`: Permutation importance repeats for statistical reliability
- Gini importance is fast but biased toward continuous/high-cardinality features; permutation importance is unbiased
- Consensus rank averages both methods for robust feature selection

**Expected Output:**
- Ranked features with Gini importance, permutation importance (mean +/- std), consensus rank, and agreement flag

---

## Recipe 4: Cross-Validated ROC-AUC for Panel Performance

Evaluate a biomarker panel's discriminative performance using stratified k-fold cross-validation with confidence intervals.

```python
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.preprocessing import StandardScaler

def evaluate_panel_auc(X, y, feature_names=None, n_folds=10, n_bootstraps=1000, random_state=42):
    """
    Evaluate biomarker panel performance with cross-validated AUC and bootstrap CI.

    Parameters
    ----------
    X : array-like, shape (n_samples, n_features)
        Selected biomarker panel measurements
    y : array-like, shape (n_samples,)
        Binary outcome
    feature_names : list of str, optional
        Panel feature names
    n_folds : int
        CV folds (default: 10)
    n_bootstraps : int
        Bootstrap iterations for CI (default: 1000)
    random_state : int
        Random seed

    Returns
    -------
    dict with AUC estimates, confidence intervals, and per-fold results
    """
    X = np.asarray(X, dtype=float)
    y = np.asarray(y)
    n_panel = X.shape[1]

    if feature_names is None:
        feature_names = [f"feature_{i}" for i in range(n_panel)]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Multiple classifiers for robustness
    classifiers = {
        "Logistic Regression": LogisticRegression(max_iter=2000, random_state=random_state),
        "Random Forest": RandomForestClassifier(n_estimators=200, random_state=random_state, n_jobs=-1),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=200, random_state=random_state),
    }

    cv = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=random_state)
    results = {}

    for name, clf in classifiers.items():
        fold_aucs = []
        for train_idx, test_idx in cv.split(X_scaled, y):
            clf.fit(X_scaled[train_idx], y[train_idx])
            y_prob = clf.predict_proba(X_scaled[test_idx])[:, 1]
            fold_auc = roc_auc_score(y[test_idx], y_prob)
            fold_aucs.append(fold_auc)

        mean_auc = np.mean(fold_aucs)
        std_auc = np.std(fold_aucs)

        # Bootstrap 95% CI
        rng = np.random.RandomState(random_state)
        boot_aucs = []
        for _ in range(n_bootstraps):
            idx = rng.choice(len(fold_aucs), size=len(fold_aucs), replace=True)
            boot_aucs.append(np.mean([fold_aucs[i] for i in idx]))
        ci_lower = np.percentile(boot_aucs, 2.5)
        ci_upper = np.percentile(boot_aucs, 97.5)

        results[name] = {
            "mean_auc": round(mean_auc, 4),
            "std_auc": round(std_auc, 4),
            "ci_95_lower": round(ci_lower, 4),
            "ci_95_upper": round(ci_upper, 4),
            "fold_aucs": [round(a, 4) for a in fold_aucs],
        }

    # Panel quality assessment (based on best classifier)
    best_clf = max(results, key=lambda k: results[k]["mean_auc"])
    best_auc = results[best_clf]["mean_auc"]

    if best_auc >= 0.90:
        quality = "EXCELLENT — strong discriminative panel (AUC >= 0.90)"
    elif best_auc >= 0.80:
        quality = "GOOD — clinically useful panel (AUC 0.80-0.90)"
    elif best_auc >= 0.70:
        quality = "MODERATE — suggestive but may need additional markers (AUC 0.70-0.80)"
    elif best_auc >= 0.60:
        quality = "WEAK — marginally better than chance (AUC 0.60-0.70)"
    else:
        quality = "POOR — panel does not discriminate (AUC < 0.60)"

    output = {
        "panel_size": n_panel,
        "panel_features": feature_names,
        "n_samples": len(y),
        "outcome_balance": round(np.mean(y), 3),
        "classifier_results": results,
        "best_classifier": best_clf,
        "best_auc": best_auc,
        "panel_quality": quality,
    }

    print(f"Biomarker Panel AUC Evaluation")
    print(f"Panel: {n_panel} features, {len(y)} samples, {np.mean(y):.1%} positive\n")
    for name, res in results.items():
        marker = " *** BEST" if name == best_clf else ""
        print(f"  {name}: AUC = {res['mean_auc']:.4f} +/- {res['std_auc']:.4f} "
              f"(95% CI: {res['ci_95_lower']:.4f}-{res['ci_95_upper']:.4f}){marker}")
    print(f"\nPanel quality: {quality}")

    return output


# Example usage
np.random.seed(42)
n_samples = 200
X_panel = np.random.randn(n_samples, 5)
y = (X_panel[:, 0] + X_panel[:, 2] - X_panel[:, 4] + np.random.randn(n_samples) * 0.5 > 0).astype(int)

result = evaluate_panel_auc(X_panel, y, feature_names=["TP53_mut", "BRCA1_expr", "PD-L1", "TMB", "MSI"])
```

**Key Parameters:**
- `n_folds=10`: 10-fold CV is standard; use 5-fold for small datasets (<100 samples)
- `n_bootstraps=1000`: Bootstrap resampling of fold AUCs for 95% CI estimation
- Tests multiple classifiers (logistic regression, random forest, gradient boosting) for robustness
- Reports best classifier and overall panel quality tier

**Expected Output:**
- AUC +/- std for each classifier, 95% bootstrap CI, best classifier, panel quality assessment

---

## Recipe 5: Mutation Sensitivity Analysis (DepMap CRISPR)

Mann-Whitney U test comparing CRISPR dependency scores between mutant and wild-type cell lines, with BH-FDR correction.

```python
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu
from statsmodels.stats.multitest import multipletests

def mutation_sensitivity_analysis(dependency_df, mutation_df, target_gene,
                                   min_mutant_lines=5, min_wt_lines=20):
    """
    Test whether mutations predict sensitivity to target gene knockout.

    Parameters
    ----------
    dependency_df : DataFrame
        DepMap CRISPR scores. Rows = cell lines, columns = genes.
        Values = log fold-change (negative = essential).
    mutation_df : DataFrame
        Binary mutation matrix. Rows = cell lines, columns = genes.
        Values = 1 (mutant) or 0 (wild-type).
    target_gene : str
        Gene whose dependency is being tested
    min_mutant_lines : int
        Minimum mutant cell lines for testing (default: 5)
    min_wt_lines : int
        Minimum wild-type cell lines (default: 20)

    Returns
    -------
    DataFrame with mutation associations sorted by significance
    """
    if target_gene not in dependency_df.columns:
        raise ValueError(f"Target gene '{target_gene}' not in dependency data")

    dep_scores = dependency_df[target_gene].dropna()

    results = []
    for mutation_gene in mutation_df.columns:
        mut_status = mutation_df[mutation_gene].dropna()

        # Shared cell lines
        shared = dep_scores.index.intersection(mut_status.index)
        if len(shared) < min_mutant_lines + min_wt_lines:
            continue

        mutant_scores = dep_scores[shared][mut_status[shared] == 1]
        wt_scores = dep_scores[shared][mut_status[shared] == 0]

        if len(mutant_scores) < min_mutant_lines or len(wt_scores) < min_wt_lines:
            continue

        # Mann-Whitney U test (two-sided)
        stat, p_value = mannwhitneyu(mutant_scores, wt_scores, alternative="two-sided")

        # Effect size: difference in medians
        median_diff = mutant_scores.median() - wt_scores.median()

        results.append({
            "mutation": mutation_gene,
            "n_mutant": len(mutant_scores),
            "n_wildtype": len(wt_scores),
            "median_LFC_mutant": round(mutant_scores.median(), 4),
            "median_LFC_wildtype": round(wt_scores.median(), 4),
            "median_difference": round(median_diff, 4),
            "mann_whitney_U": stat,
            "p_value": p_value,
        })

    results_df = pd.DataFrame(results)

    if results_df.empty:
        print(f"No mutations met minimum sample size requirements")
        return results_df

    # BH-FDR correction
    _, fdr, _, _ = multipletests(results_df["p_value"], method="fdr_bh")
    results_df["fdr_q_value"] = fdr

    # Classify sensitivity
    results_df["sensitivity"] = results_df.apply(
        lambda row: "SENSITIZING" if row["median_difference"] < -0.3 and row["fdr_q_value"] < 0.05
        else "RESISTANT" if row["median_difference"] > 0.3 and row["fdr_q_value"] < 0.05
        else "NOT SIGNIFICANT",
        axis=1,
    )

    results_df = results_df.sort_values("p_value").reset_index(drop=True)

    print(f"Mutation Sensitivity Analysis for {target_gene} Dependency")
    print(f"Tested {len(results_df)} mutations\n")
    sig = results_df[results_df["fdr_q_value"] < 0.05]
    print(f"Significant (FDR < 0.05): {len(sig)}")
    if not sig.empty:
        print(sig.to_string(index=False))

    return results_df


# Example usage (requires DepMap data)
# dependency = pd.read_csv("CRISPRGeneEffect.csv", index_col=0)
# mutations = pd.read_csv("OmicsSomaticMutationsMatrixDamaging.csv", index_col=0)
# results = mutation_sensitivity_analysis(dependency, mutations, "BRAF")
```

**Key Parameters:**
- `min_mutant_lines=5`: Minimum mutant cell lines for statistical power
- `min_wt_lines=20`: Minimum wild-type cell lines for reliable comparison
- `median_difference < -0.3`: Mutant cells are more dependent (sensitizing mutation)
- BH-FDR correction for multiple testing

**Expected Output:**
- Ranked mutations by association with target dependency, with FDR-corrected p-values and sensitivity classification

---

## Recipe 6: Resistance Profiling by LFC Thresholds

Classify cell lines as sensitive, intermediate, or resistant based on CRISPR log fold-change thresholds.

```python
import numpy as np
import pandas as pd

def classify_sensitivity(dependency_df, gene, sensitive_threshold=-0.5,
                          resistant_threshold=-0.2):
    """
    Classify cell lines by sensitivity to gene knockout.

    Parameters
    ----------
    dependency_df : DataFrame
        DepMap CRISPR dependency scores (rows = cell lines, columns = genes)
    gene : str
        Target gene
    sensitive_threshold : float
        LFC below this = sensitive (default: -0.5)
    resistant_threshold : float
        LFC above this = resistant (default: -0.2)

    Returns
    -------
    DataFrame with cell line classifications and summary statistics
    """
    if gene not in dependency_df.columns:
        raise ValueError(f"Gene '{gene}' not found")

    scores = dependency_df[gene].dropna()

    classifications = pd.DataFrame({
        "cell_line": scores.index,
        "LFC": scores.values,
    })

    classifications["class"] = pd.cut(
        classifications["LFC"],
        bins=[-np.inf, sensitive_threshold, resistant_threshold, np.inf],
        labels=["SENSITIVE", "INTERMEDIATE", "RESISTANT"],
    )

    # Summary
    summary = classifications["class"].value_counts()
    total = len(classifications)

    print(f"Sensitivity Classification for {gene}")
    print(f"Total cell lines: {total}")
    print(f"  SENSITIVE (LFC < {sensitive_threshold}): {summary.get('SENSITIVE', 0)} ({summary.get('SENSITIVE', 0)/total:.1%})")
    print(f"  INTERMEDIATE ({sensitive_threshold} <= LFC < {resistant_threshold}): {summary.get('INTERMEDIATE', 0)} ({summary.get('INTERMEDIATE', 0)/total:.1%})")
    print(f"  RESISTANT (LFC >= {resistant_threshold}): {summary.get('RESISTANT', 0)} ({summary.get('RESISTANT', 0)/total:.1%})")
    print(f"\nMedian LFC: {scores.median():.4f}")
    print(f"Mean LFC: {scores.mean():.4f}")

    return classifications


# Example usage
# dependency = pd.read_csv("CRISPRGeneEffect.csv", index_col=0)
# results = classify_sensitivity(dependency, "BRAF")
```

**Key Parameters:**
- `sensitive_threshold=-0.5`: Cells with LFC below this are considered dependent (sensitive to knockout)
- `resistant_threshold=-0.2`: Cells with LFC above this are resistant (not dependent)
- Intermediate class captures cells with modest dependency

**Expected Output:**
- Cell line classification table with LFC values and sensitivity class, summary statistics

---

## Recipe 7: Lineage Enrichment (Fisher's Exact Test)

Test whether a biomarker is enriched in specific cancer lineages using Fisher's exact test.

```python
import numpy as np
import pandas as pd
from scipy.stats import fisher_exact
from statsmodels.stats.multitest import multipletests

def lineage_enrichment(biomarker_status, lineage_labels, biomarker_name="biomarker"):
    """
    Test biomarker enrichment across cancer lineages.

    Parameters
    ----------
    biomarker_status : Series
        Binary biomarker (1 = positive, 0 = negative), indexed by cell line
    lineage_labels : Series
        Cancer lineage labels, indexed by cell line
    biomarker_name : str
        Name for display

    Returns
    -------
    DataFrame with enrichment results per lineage
    """
    shared = biomarker_status.index.intersection(lineage_labels.index)
    bm = biomarker_status[shared]
    lin = lineage_labels[shared]

    lineages = lin.unique()
    results = []

    for lineage in lineages:
        in_lineage = lin == lineage
        bm_pos = bm == 1

        # 2x2 contingency table
        a = (in_lineage & bm_pos).sum()       # lineage + biomarker+
        b = (~in_lineage & bm_pos).sum()      # other + biomarker+
        c = (in_lineage & ~bm_pos).sum()      # lineage + biomarker-
        d = (~in_lineage & ~bm_pos).sum()     # other + biomarker-

        if a + c < 3:  # Skip lineages with < 3 cell lines
            continue

        odds_ratio, p_value = fisher_exact([[a, b], [c, d]], alternative="two-sided")
        prevalence = a / (a + c) if (a + c) > 0 else 0

        results.append({
            "lineage": lineage,
            "n_lines": int(a + c),
            "n_positive": int(a),
            "prevalence": round(prevalence, 3),
            "odds_ratio": round(odds_ratio, 3),
            "p_value": p_value,
        })

    results_df = pd.DataFrame(results)

    if results_df.empty:
        return results_df

    # FDR correction
    _, fdr, _, _ = multipletests(results_df["p_value"], method="fdr_bh")
    results_df["fdr_q_value"] = fdr

    results_df["enrichment"] = results_df.apply(
        lambda r: "ENRICHED" if r["odds_ratio"] > 2 and r["fdr_q_value"] < 0.05
        else "DEPLETED" if r["odds_ratio"] < 0.5 and r["fdr_q_value"] < 0.05
        else "NOT SIGNIFICANT",
        axis=1,
    )

    results_df = results_df.sort_values("p_value").reset_index(drop=True)

    print(f"Lineage Enrichment for {biomarker_name}")
    print(f"Tested {len(results_df)} lineages\n")
    sig = results_df[results_df["fdr_q_value"] < 0.05]
    if not sig.empty:
        print("Significant enrichments/depletions:")
        print(sig.to_string(index=False))
    else:
        print("No significant lineage associations found")

    return results_df


# Example usage
# biomarker = pd.Series({cell_line: mutation_status for ...})
# lineages = pd.Series({cell_line: "lung" for ...})
# results = lineage_enrichment(biomarker, lineages, "KRAS_G12D")
```

**Key Parameters:**
- Fisher's exact test: exact p-value for 2x2 contingency tables (no approximation)
- `odds_ratio > 2` + `FDR < 0.05`: enriched in lineage
- `odds_ratio < 0.5` + `FDR < 0.05`: depleted in lineage

**Expected Output:**
- Per-lineage enrichment results with odds ratios, FDR-corrected p-values, and enrichment classification

---

## Recipe 8: Elastic Net Regularization for Correlated Biomarkers

L1+L2 combined regularization handles correlated features better than pure LASSO. Useful when biomarker panels include correlated gene expression or protein levels.

```python
import numpy as np
import pandas as pd
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold, cross_val_score

def elastic_net_selection(X, y, feature_names=None, l1_ratio=0.5,
                           n_folds=5, n_alphas=50, random_state=42):
    """
    Elastic net feature selection for correlated biomarker panels.

    Parameters
    ----------
    X : array-like, shape (n_samples, n_features)
        Biomarker measurements
    y : array-like, shape (n_samples,)
        Binary outcome
    feature_names : list of str, optional
        Feature names
    l1_ratio : float
        L1/L2 balance (0 = pure L2/Ridge, 1 = pure L1/LASSO, 0.5 = equal mix)
    n_folds : int
        CV folds
    n_alphas : int
        Number of alpha values to search
    random_state : int
        Random seed

    Returns
    -------
    dict with selected features and performance metrics
    """
    X = np.asarray(X, dtype=float)
    y = np.asarray(y)

    if feature_names is None:
        feature_names = [f"feature_{i}" for i in range(X.shape[1])]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Search over alpha values
    alphas = np.logspace(-5, 1, n_alphas)
    cv = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=random_state)

    best_alpha = None
    best_auc = 0
    best_model = None

    for alpha in alphas:
        model = SGDClassifier(
            loss="log_loss",
            penalty="elasticnet",
            alpha=alpha,
            l1_ratio=l1_ratio,
            max_iter=5000,
            random_state=random_state,
        )
        aucs = cross_val_score(model, X_scaled, y, cv=cv, scoring="roc_auc")
        mean_auc = aucs.mean()

        if mean_auc > best_auc:
            best_auc = mean_auc
            best_alpha = alpha
            best_model = model

    # Refit best model on all data
    best_model.set_params(alpha=best_alpha)
    best_model.fit(X_scaled, y)

    coefficients = best_model.coef_[0]
    selected_mask = coefficients != 0
    selected_features = np.array(feature_names)[selected_mask]
    selected_coefficients = coefficients[selected_mask]

    sort_idx = np.argsort(-np.abs(selected_coefficients))
    selected_features = selected_features[sort_idx]
    selected_coefficients = selected_coefficients[sort_idx]

    results_df = pd.DataFrame({
        "feature": selected_features,
        "coefficient": np.round(selected_coefficients, 4),
        "abs_coefficient": np.round(np.abs(selected_coefficients), 4),
    })

    print(f"Elastic Net Selection (l1_ratio={l1_ratio})")
    print(f"Best alpha: {best_alpha:.6f}")
    print(f"CV AUC: {best_auc:.4f}")
    print(f"Selected: {len(selected_features)}/{len(feature_names)} features\n")
    print(results_df.to_string(index=False))

    return {
        "l1_ratio": l1_ratio,
        "best_alpha": best_alpha,
        "cv_auc": round(best_auc, 4),
        "n_selected": len(selected_features),
        "selected_panel": results_df,
    }


# Example
np.random.seed(42)
n = 200
X = np.random.randn(n, 30)
# Introduce correlation: features 1 and 2 are correlated with feature 0
X[:, 1] = X[:, 0] * 0.8 + np.random.randn(n) * 0.3
X[:, 2] = X[:, 0] * 0.6 + np.random.randn(n) * 0.5
y = (X[:, 0] + X[:, 5] + np.random.randn(n) * 0.5 > 0).astype(int)

result = elastic_net_selection(X, y, l1_ratio=0.5)
```

**Key Parameters:**
- `l1_ratio=0.5`: Balance between L1 (sparsity) and L2 (correlation handling). 0.5 is a good default.
  - 0.1-0.3: Keeps more correlated features (grouped selection)
  - 0.7-0.9: More aggressive sparsity (closer to LASSO)
- Elastic net keeps correlated features together (L1 alone would arbitrarily drop one)

**Expected Output:**
- Selected features with coefficients, optimal regularization parameters, cross-validated AUC

---

## Recipe 9: Panel Size Optimization (AUC vs Panel Size Curve)

Find the minimal informative panel by incrementally adding features and detecting the AUC elbow point.

```python
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler

def optimize_panel_size(X, y, feature_ranking, feature_names=None,
                         max_panel_size=None, n_folds=10, random_state=42):
    """
    Find optimal panel size by plotting AUC vs number of features.

    Parameters
    ----------
    X : array-like, shape (n_samples, n_features)
        All candidate biomarker measurements
    y : array-like, shape (n_samples,)
        Binary outcome
    feature_ranking : list of int
        Feature indices sorted by importance (most important first)
    feature_names : list of str, optional
        Feature names
    max_panel_size : int, optional
        Maximum panel size to test (default: min(30, n_features))
    n_folds : int
        CV folds
    random_state : int
        Random seed

    Returns
    -------
    dict with AUC curve, optimal panel size, and elbow detection
    """
    X = np.asarray(X, dtype=float)
    y = np.asarray(y)
    n_features = X.shape[1]

    if feature_names is None:
        feature_names = [f"feature_{i}" for i in range(n_features)]

    if max_panel_size is None:
        max_panel_size = min(30, n_features)

    scaler = StandardScaler()
    cv = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=random_state)

    panel_sizes = []
    mean_aucs = []
    std_aucs = []

    for k in range(1, max_panel_size + 1):
        selected_idx = feature_ranking[:k]
        X_k = scaler.fit_transform(X[:, selected_idx])

        clf = LogisticRegression(max_iter=2000, random_state=random_state)
        aucs = cross_val_score(clf, X_k, y, cv=cv, scoring="roc_auc")

        panel_sizes.append(k)
        mean_aucs.append(aucs.mean())
        std_aucs.append(aucs.std())

    # Elbow detection: find where marginal AUC gain drops below threshold
    marginal_gains = np.diff(mean_aucs)
    threshold = 0.005  # 0.5% AUC gain threshold

    elbow_idx = len(mean_aucs) - 1  # default: use all
    for i, gain in enumerate(marginal_gains):
        if i >= 2 and all(g < threshold for g in marginal_gains[i:i+3] if i+3 <= len(marginal_gains)):
            elbow_idx = i + 1  # +1 because marginal_gains is offset by 1
            break

    optimal_size = panel_sizes[elbow_idx]
    optimal_auc = mean_aucs[elbow_idx]
    max_auc = max(mean_aucs)
    max_auc_size = panel_sizes[mean_aucs.index(max_auc)]

    # Results table
    curve_df = pd.DataFrame({
        "panel_size": panel_sizes,
        "mean_auc": [round(a, 4) for a in mean_aucs],
        "std_auc": [round(s, 4) for s in std_aucs],
        "marginal_gain": [None] + [round(g, 4) for g in marginal_gains],
    })

    # Selected panel features
    optimal_features = [feature_names[i] for i in feature_ranking[:optimal_size]]

    print(f"Panel Size Optimization")
    print(f"Elbow point: {optimal_size} features (AUC = {optimal_auc:.4f})")
    print(f"Maximum AUC: {max_auc:.4f} at {max_auc_size} features")
    print(f"AUC retained at elbow: {optimal_auc/max_auc:.1%} of maximum\n")
    print(f"Optimal panel ({optimal_size} features): {', '.join(optimal_features)}\n")
    print(curve_df.head(20).to_string(index=False))

    return {
        "optimal_panel_size": optimal_size,
        "optimal_auc": round(optimal_auc, 4),
        "max_auc": round(max_auc, 4),
        "max_auc_panel_size": max_auc_size,
        "auc_retained": round(optimal_auc / max_auc, 4) if max_auc > 0 else 0,
        "optimal_features": optimal_features,
        "curve": curve_df,
    }


# Example
np.random.seed(42)
n_samples, n_features = 200, 30
X = np.random.randn(n_samples, n_features)
y = (X[:, 0] + X[:, 1] + 0.5 * X[:, 2] + np.random.randn(n_samples) * 0.5 > 0).astype(int)

# Assume features are pre-ranked by importance
ranking = list(range(n_features))  # 0 is most important
result = optimize_panel_size(X, y, ranking)
```

**Key Parameters:**
- `feature_ranking`: Pre-ranked feature indices (from mutual information, LASSO, or random forest)
- `threshold=0.005`: Marginal AUC gain below 0.5% for 3 consecutive features triggers elbow
- Incrementally adds features from most to least important

**Expected Output:**
- Optimal panel size (elbow point), AUC at elbow vs maximum, selected features, full AUC-vs-size curve

---

## Recipe 10: Biomarker Readiness Scoring

Composite 0-100 readiness score combining clinical trial evidence, active recruiting status, PubMed literature, and OpenAlex citations.

```python
import requests
import pandas as pd

def score_biomarker_readiness(biomarker_name, disease_name=None):
    """
    Compute a composite biomarker readiness score (0-100).

    Components:
    - Clinical trials evidence (35 points max)
    - Active recruiting trials (20 points max)
    - PubMed literature (30 points max)
    - OpenAlex citations (15 points max)

    Parameters
    ----------
    biomarker_name : str
        Biomarker name (gene symbol, protein name, or assay name)
    disease_name : str, optional
        Disease context for more specific scoring

    Returns
    -------
    dict with composite score, component scores, and readiness tier
    """
    query = f"{biomarker_name} biomarker"
    if disease_name:
        query += f" {disease_name}"

    # 1. Clinical trials (35 points)
    ct_url = "https://clinicaltrials.gov/api/v2/studies"
    ct_params = {
        "query.term": query,
        "pageSize": 100,
        "format": "json",
    }
    try:
        ct_resp = requests.get(ct_url, params=ct_params, timeout=15)
        ct_data = ct_resp.json()
        total_trials = ct_data.get("totalCount", 0)
        studies = ct_data.get("studies", [])

        # Count by phase
        phase_counts = {"PHASE1": 0, "PHASE2": 0, "PHASE3": 0, "PHASE4": 0}
        recruiting_count = 0
        for study in studies:
            phase = study.get("protocolSection", {}).get("designModule", {}).get("phases", [])
            status = study.get("protocolSection", {}).get("statusModule", {}).get("overallStatus", "")
            for p in phase:
                if p in phase_counts:
                    phase_counts[p] += 1
            if status in ("RECRUITING", "ENROLLING_BY_INVITATION"):
                recruiting_count += 1

        # Score: phase-weighted
        trial_score = min(35, (
            phase_counts["PHASE3"] * 8 +
            phase_counts["PHASE2"] * 4 +
            phase_counts["PHASE1"] * 2 +
            phase_counts["PHASE4"] * 3
        ))
    except Exception:
        total_trials = 0
        trial_score = 0
        recruiting_count = 0
        phase_counts = {}

    # 2. Active recruiting (20 points)
    recruiting_score = min(20, recruiting_count * 4)

    # 3. PubMed literature (30 points)
    pubmed_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    pubmed_params = {
        "db": "pubmed",
        "term": f"{biomarker_name}[Title/Abstract] AND biomarker[Title/Abstract]",
        "rettype": "count",
        "retmode": "json",
    }
    try:
        pm_resp = requests.get(pubmed_url, params=pubmed_params, timeout=10)
        pubmed_count = int(pm_resp.json().get("esearchresult", {}).get("count", 0))
        # Log-scaled: 1 pub = 5 pts, 10 = 15 pts, 100 = 25 pts, 500+ = 30 pts
        import math
        literature_score = min(30, int(5 * math.log2(pubmed_count + 1)))
    except Exception:
        pubmed_count = 0
        literature_score = 0

    # 4. OpenAlex citations (15 points)
    oa_url = "https://api.openalex.org/works"
    oa_params = {
        "search": f"{biomarker_name} biomarker",
        "per_page": 50,
    }
    try:
        oa_resp = requests.get(oa_url, params=oa_params, timeout=10)
        oa_works = oa_resp.json().get("results", [])
        total_citations = sum(w.get("cited_by_count", 0) for w in oa_works[:50])
        # Log-scaled
        import math
        citation_score = min(15, int(3 * math.log2(total_citations + 1)))
    except Exception:
        total_citations = 0
        citation_score = 0

    # Composite score
    composite = trial_score + recruiting_score + literature_score + citation_score

    # Readiness tier
    if composite >= 70:
        tier = "HIGH READINESS — validated biomarker with strong clinical and literature evidence"
    elif composite >= 40:
        tier = "MODERATE READINESS — emerging biomarker with growing evidence base"
    else:
        tier = "EARLY READINESS — exploratory biomarker, needs further validation"

    result = {
        "biomarker": biomarker_name,
        "disease": disease_name or "general",
        "composite_score": composite,
        "readiness_tier": tier,
        "components": {
            "clinical_trials": {"score": trial_score, "max": 35, "total_trials": total_trials},
            "active_recruiting": {"score": recruiting_score, "max": 20, "count": recruiting_count},
            "pubmed_literature": {"score": literature_score, "max": 30, "count": pubmed_count},
            "openalex_citations": {"score": citation_score, "max": 15, "total_citations": total_citations},
        },
    }

    print(f"\nBiomarker Readiness: {biomarker_name}")
    if disease_name:
        print(f"Disease context: {disease_name}")
    print(f"\nComposite Score: {composite}/100")
    print(f"Tier: {tier}\n")
    print(f"  Clinical trials:   {trial_score:3d}/35  ({total_trials} total trials)")
    print(f"  Active recruiting: {recruiting_score:3d}/20  ({recruiting_count} recruiting)")
    print(f"  PubMed literature: {literature_score:3d}/30  ({pubmed_count} publications)")
    print(f"  OpenAlex citations:{citation_score:3d}/15  ({total_citations} citations)")

    return result


# Example
# result = score_biomarker_readiness("PD-L1", "non-small cell lung cancer")
```

**Key Parameters:**
- Weights: clinical trials (35), active recruiting (20), PubMed literature (30), OpenAlex citations (15) = 100 total
- Tier thresholds: High (>=70), Moderate (40-69), Early (<40)
- PubMed and citation scores are log-scaled to avoid saturation for well-studied biomarkers

**Expected Output:**
- Composite readiness score (0-100), readiness tier, component breakdown with raw counts

---

## Recipe 11: Survival Association (Cox Proportional Hazards)

Cox regression for biomarker-survival association testing. Reports hazard ratio with 95% CI and log-rank p-value.

```python
import numpy as np
import pandas as pd

def biomarker_survival_association(time, event, biomarker, biomarker_name="biomarker",
                                    continuous=True, cutoff_percentile=50):
    """
    Test biomarker association with survival using Cox proportional hazards.

    Parameters
    ----------
    time : array-like
        Survival/follow-up time
    event : array-like
        Event indicator (1 = event/death, 0 = censored)
    biomarker : array-like
        Biomarker values (continuous or binary)
    biomarker_name : str
        Name for display
    continuous : bool
        If True, use continuous biomarker. If False, dichotomize at cutoff.
    cutoff_percentile : int
        Percentile for dichotomization if continuous=False (default: 50 = median)

    Returns
    -------
    dict with hazard ratio, 95% CI, p-value, and model summary
    """
    from lifelines import CoxPHFitter
    from lifelines.statistics import logrank_test

    time = np.asarray(time, dtype=float)
    event = np.asarray(event, dtype=int)
    biomarker = np.asarray(biomarker, dtype=float)

    # Remove missing values
    mask = ~(np.isnan(time) | np.isnan(event) | np.isnan(biomarker))
    time = time[mask]
    event = event[mask]
    biomarker = biomarker[mask]

    # Dichotomize if requested
    if not continuous:
        cutoff = np.percentile(biomarker, cutoff_percentile)
        biomarker_binary = (biomarker >= cutoff).astype(int)
        label = f"{biomarker_name}_high"
    else:
        # Standardize continuous biomarker for interpretable HR
        biomarker_binary = None
        biomarker_std = (biomarker - biomarker.mean()) / biomarker.std()
        label = f"{biomarker_name}_std"

    # Cox regression
    df = pd.DataFrame({
        "time": time,
        "event": event,
        label: biomarker_std if continuous else biomarker_binary,
    })

    cph = CoxPHFitter()
    cph.fit(df, duration_col="time", event_col="event")

    hr = np.exp(cph.params_[label])
    ci = np.exp(cph.confidence_intervals_.loc[label].values)
    p_value = cph.summary.loc[label, "p"]

    # Log-rank test (for dichotomized biomarker)
    logrank_p = None
    if not continuous:
        high_group = df[df[label] == 1]
        low_group = df[df[label] == 0]
        lr_result = logrank_test(
            high_group["time"], low_group["time"],
            high_group["event"], low_group["event"],
        )
        logrank_p = lr_result.p_value

    # PH assumption check
    ph_test = cph.check_assumptions(df, p_value_threshold=0.05, show_plots=False)

    result = {
        "biomarker": biomarker_name,
        "analysis_type": "continuous (per SD)" if continuous else f"dichotomized (>= {cutoff_percentile}th percentile)",
        "n_subjects": len(time),
        "n_events": int(event.sum()),
        "hazard_ratio": round(hr, 3),
        "ci_95_lower": round(ci[0], 3),
        "ci_95_upper": round(ci[1], 3),
        "cox_p_value": p_value,
        "logrank_p_value": logrank_p,
    }

    # Interpretation
    if p_value < 0.05:
        if hr > 1:
            result["interpretation"] = f"ADVERSE — higher {biomarker_name} associated with worse survival (HR={hr:.2f})"
        else:
            result["interpretation"] = f"PROTECTIVE — higher {biomarker_name} associated with better survival (HR={hr:.2f})"
    else:
        result["interpretation"] = f"NOT SIGNIFICANT — no survival association detected (HR={hr:.2f}, p={p_value:.3f})"

    print(f"\nSurvival Association: {biomarker_name}")
    print(f"N = {len(time)}, Events = {int(event.sum())}")
    print(f"HR = {hr:.3f} (95% CI: {ci[0]:.3f}-{ci[1]:.3f})")
    print(f"Cox p-value: {p_value:.4f}")
    if logrank_p is not None:
        print(f"Log-rank p-value: {logrank_p:.4f}")
    print(f"Interpretation: {result['interpretation']}")

    return result


# Example usage (requires lifelines: pip install lifelines)
# np.random.seed(42)
# n = 200
# time = np.random.exponential(24, n)  # months
# biomarker = np.random.randn(n)
# event = (np.random.rand(n) < 0.7).astype(int)
# result = biomarker_survival_association(time, event, biomarker, "TP53_expression", continuous=True)
```

**Key Parameters:**
- `continuous=True`: Test continuous biomarker (HR per standard deviation increase)
- `continuous=False`: Dichotomize at specified percentile (default: median split)
- Reports both Cox regression p-value and log-rank p-value (for dichotomized analysis)
- Automatically checks proportional hazards assumption

**Expected Output:**
- Hazard ratio with 95% CI, Cox p-value, log-rank p-value, clinical interpretation

---

## Recipe 12: Multi-Omics Feature Integration

Combine mutation, expression, and methylation features into a unified biomarker panel with modality-aware feature selection.

```python
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score

def integrate_multiomics_panel(
    mutations_df,
    expression_df,
    methylation_df,
    y,
    sample_ids,
    n_top_per_modality=10,
    n_folds=5,
    random_state=42,
):
    """
    Integrate multi-omics data for biomarker panel selection.

    Parameters
    ----------
    mutations_df : DataFrame
        Binary mutation matrix (samples x genes), values 0/1
    expression_df : DataFrame
        Gene expression matrix (samples x genes), continuous values
    methylation_df : DataFrame
        Methylation beta values (samples x CpG sites), values 0-1
    y : Series or array
        Binary outcome indexed by sample ID
    sample_ids : list
        Sample IDs present in all data modalities
    n_top_per_modality : int
        Number of top features to select per data modality (default: 10)
    n_folds : int
        CV folds
    random_state : int
        Random seed

    Returns
    -------
    dict with integrated panel, per-modality contributions, and combined AUC
    """
    from sklearn.feature_selection import mutual_info_classif

    y = np.asarray([y[s] for s in sample_ids])

    modality_results = {}

    for name, df in [("mutation", mutations_df), ("expression", expression_df), ("methylation", methylation_df)]:
        # Align to shared samples
        X_mod = df.loc[sample_ids].values
        feature_names = list(df.columns)

        # Rank by mutual information
        mi = mutual_info_classif(X_mod, y, random_state=random_state)
        ranking = np.argsort(-mi)
        top_idx = ranking[:n_top_per_modality]

        top_features = [feature_names[i] for i in top_idx]
        top_mi = mi[top_idx]

        # Per-modality AUC
        scaler = StandardScaler()
        X_top = scaler.fit_transform(X_mod[:, top_idx])
        cv = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=random_state)
        clf = RandomForestClassifier(n_estimators=200, random_state=random_state, n_jobs=-1)
        aucs = cross_val_score(clf, X_top, y, cv=cv, scoring="roc_auc")

        modality_results[name] = {
            "features": top_features,
            "mi_scores": [round(m, 4) for m in top_mi],
            "X_selected": X_top,
            "mean_auc": round(aucs.mean(), 4),
            "std_auc": round(aucs.std(), 4),
        }

    # Combine all modalities
    X_combined = np.hstack([modality_results[mod]["X_selected"] for mod in modality_results])
    combined_features = []
    for mod in modality_results:
        combined_features.extend([f"{mod}:{f}" for f in modality_results[mod]["features"]])

    # Combined panel AUC
    clf_combined = RandomForestClassifier(n_estimators=200, random_state=random_state, n_jobs=-1)
    combined_aucs = cross_val_score(clf_combined, X_combined, y, cv=cv, scoring="roc_auc")

    # Summary
    print(f"Multi-Omics Biomarker Panel Integration")
    print(f"Samples: {len(y)}, Outcome balance: {y.mean():.1%} positive\n")

    print(f"Per-Modality Performance:")
    for mod, res in modality_results.items():
        print(f"  {mod:12s}: AUC = {res['mean_auc']:.4f} +/- {res['std_auc']:.4f} "
              f"({len(res['features'])} features)")

    print(f"\n  {'COMBINED':12s}: AUC = {combined_aucs.mean():.4f} +/- {combined_aucs.std():.4f} "
          f"({len(combined_features)} features)")

    improvement = combined_aucs.mean() - max(r["mean_auc"] for r in modality_results.values())
    print(f"\n  Integration gain: {improvement:+.4f} AUC vs best single modality")

    return {
        "modality_results": {mod: {"features": res["features"], "mean_auc": res["mean_auc"]}
                            for mod, res in modality_results.items()},
        "combined_features": combined_features,
        "combined_auc": round(combined_aucs.mean(), 4),
        "combined_std": round(combined_aucs.std(), 4),
        "integration_gain": round(improvement, 4),
        "n_total_features": len(combined_features),
    }


# Example usage (requires aligned multi-omics data)
# result = integrate_multiomics_panel(
#     mutations_df=mutation_matrix,
#     expression_df=expression_matrix,
#     methylation_df=methylation_matrix,
#     y=outcome_series,
#     sample_ids=shared_samples,
# )
```

**Key Parameters:**
- `n_top_per_modality=10`: Select top features per data type to avoid one modality dominating
- Mutual information ranking within each modality (non-parametric, captures nonlinear effects)
- Reports per-modality AUC and combined AUC to quantify integration benefit
- Feature names prefixed with modality (e.g., "mutation:BRAF", "expression:EGFR") for traceability

**Expected Output:**
- Per-modality feature lists and AUC, combined panel AUC, integration gain over best single modality
