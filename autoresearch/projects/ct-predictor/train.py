#!/usr/bin/env python3
"""
Clinical Trial Outcome Predictor — train.py

This is the ONLY file the autoresearch agent modifies.
Everything is here: feature engineering, model definition, training.

Run:  python train.py > run.log 2>&1
Eval: python prepare.py  (extracts auc_roc from grep-friendly output)
"""

import json
import pickle
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier, VotingClassifier, HistGradientBoostingClassifier
from sklearn.feature_selection import SelectKBest, mutual_info_classif
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.svm import SVC

# ---------------------------------------------------------------------------
# Paths (do not change)
# ---------------------------------------------------------------------------

DATA_DIR = Path(__file__).parent / "data"
MODEL_PATH = Path(__file__).parent / "model.pkl"

# ---------------------------------------------------------------------------
# Feature engineering — MODIFY THIS
# ---------------------------------------------------------------------------

def build_features(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """
    Build feature matrix X and label vector y from raw trial data.
    """
    y = df["label"].astype(int)

    # === Numeric features ===
    numeric_cols = [
        # Trial design
        "phase", "enrollment", "num_arms", "has_dmc",
        "num_secondary_endpoints", "num_sites", "has_biomarker_selection",
        "competitor_trial_count", "prior_phase_success",
        # OpenTargets
        "ot_genetic_score", "ot_somatic_score", "ot_literature_score",
        "ot_animal_model_score", "ot_known_drug_score",
        "ot_affected_pathway_score", "ot_overall_score", "ot_target_tractability",
        # ChEMBL
        "chembl_selectivity", "chembl_best_ic50_nm", "chembl_num_assays",
        "chembl_max_phase", "chembl_moa_count",
        # DrugBank
        "drugbank_interaction_count", "drugbank_target_count",
        "drugbank_enzyme_count", "drugbank_transporter_count",
        "drugbank_half_life_hours", "drugbank_molecular_weight",
        # BindingDB
        "bindingdb_ki_nm", "bindingdb_kd_nm", "bindingdb_num_measurements",
        # ClinPGx
        "clinpgx_guideline_count", "clinpgx_actionable",
        "clinpgx_cyp_substrate_count",
        # FDA
        "fda_prior_approval_class", "fda_breakthrough", "fda_fast_track",
        "fda_orphan", "fda_class_ae_count",
        # Publication signals
        "pubmed_target_pub_count", "pubmed_drug_pub_count",
        "openalex_citation_velocity", "biorxiv_preprint_count",
        # Healthcare spend
        "medicare_indication_spend", "medicaid_indication_spend",
        # Pathway/network
        "reactome_pathway_count", "stringdb_interaction_degree",
        "stringdb_betweenness",
        # Genomic
        "gtex_tissue_specificity", "gnomad_pli", "gnomad_loeuf",
        "clinvar_pathogenic_count", "gwas_hit_count", "gwas_best_pvalue",
        "depmap_essentiality", "cbioportal_mutation_freq",
        # Disease complexity
        "hpo_phenotype_count", "monarch_gene_count",
        # EMA
        "ema_approved_similar", "eu_filings_count",
    ]

    available = [c for c in numeric_cols if c in df.columns]
    X = df[available].copy()

    # Force numeric conversion (real data may have strings)
    for col in available:
        X[col] = pd.to_numeric(X[col], errors='coerce')

    # Handle missing values — add missingness indicator for high-missing cols
    for col in available:
        missing_frac = X[col].isna().mean()
        if missing_frac > 0.1:
            X[f"{col}_missing"] = X[col].isna().astype(int)
        med = X[col].median()
        X[col] = X[col].fillna(med if pd.notna(med) else 0)

    # One-hot encode indication_area (low cardinality, 8 values)
    if "indication_area" in df.columns:
        for val in df["indication_area"].dropna().unique():
            X[f"is_{val}"] = (df["indication_area"] == val).astype(int)

    # Normalized sponsor_type: merge industry variants
    if "sponsor_type" in df.columns:
        st = df["sponsor_type"].str.lower().str.strip().fillna("unknown")
        for val in ["industry", "nih", "other"]:
            X[f"sponsor_{val}"] = (st == val).astype(int)

    # Frequency encode lower-signal categoricals
    for col in ["allocation", "masking", "intervention_type"]:
        if col in df.columns:
            freq = df[col].value_counts(normalize=True)
            X[f"{col}_freq"] = df[col].map(freq).fillna(0)

    # Log transforms for skewed features
    for col in ["chembl_best_ic50_nm", "bindingdb_ki_nm", "bindingdb_kd_nm",
                "enrollment", "pubmed_target_pub_count", "pubmed_drug_pub_count",
                "medicare_indication_spend", "medicaid_indication_spend",
                "chembl_selectivity", "bindingdb_num_measurements",
                "openalex_citation_velocity", "biorxiv_preprint_count",
                "stringdb_betweenness", "reactome_pathway_count",
                "clinvar_pathogenic_count", "gwas_hit_count"]:
        if col in X.columns:
            X[f"log_{col}"] = np.log1p(X[col])

    # Engineered interactions
    if "ot_genetic_score" in X.columns and "phase" in X.columns:
        X["genetic_x_phase"] = X["ot_genetic_score"] * X["phase"]

    if "ot_overall_score" in X.columns and "phase" in X.columns:
        X["overall_score_x_phase"] = X["ot_overall_score"] * X["phase"]

    if "pubmed_target_pub_count" in X.columns and "pubmed_drug_pub_count" in X.columns:
        X["pub_ratio"] = (X["pubmed_drug_pub_count"] + 1) / (X["pubmed_target_pub_count"] + 1)

    genetic = [c for c in ["ot_genetic_score", "gwas_hit_count", "clinvar_pathogenic_count"] if c in X.columns]
    if len(genetic) > 1:
        X["total_genetic_evidence"] = X[genetic].sum(axis=1)

    reg = [c for c in ["fda_breakthrough", "fda_fast_track", "fda_orphan"] if c in X.columns]
    if reg:
        X["regulatory_advantage"] = X[reg].sum(axis=1)

    if "medicare_indication_spend" in X.columns and "medicaid_indication_spend" in X.columns:
        X["total_healthcare_spend"] = X["medicare_indication_spend"] + X["medicaid_indication_spend"]
        X["log_total_healthcare_spend"] = np.log1p(X["total_healthcare_spend"])

    # Drug maturity × target evidence
    if "chembl_max_phase" in X.columns and "ot_overall_score" in X.columns:
        X["drug_maturity_x_evidence"] = X["chembl_max_phase"] * X["ot_overall_score"]

    # Phase × regulatory advantage
    if "phase" in X.columns and "regulatory_advantage" in X.columns:
        X["phase_x_regulatory"] = X["phase"] * X["regulatory_advantage"]

    # ChEMBL selectivity × target tractability
    if "chembl_selectivity" in X.columns and "ot_target_tractability" in X.columns:
        X["selectivity_x_tractability"] = X["chembl_selectivity"] * X["ot_target_tractability"]

    # Prior approval + prior phase success combined
    prior = [c for c in ["fda_prior_approval_class", "prior_phase_success", "chembl_max_phase"] if c in X.columns]
    if len(prior) > 1:
        X["prior_evidence_score"] = X[prior].mean(axis=1)

    # Genetic evidence × target tractability
    if "total_genetic_evidence" in X.columns and "ot_target_tractability" in X.columns:
        X["genetic_x_tractability"] = X["total_genetic_evidence"] * X["ot_target_tractability"]

    # DepMap essentiality × ChEMBL max phase (cancer-relevant)
    if "depmap_essentiality" in X.columns and "chembl_max_phase" in X.columns:
        X["depmap_x_maxphase"] = X["depmap_essentiality"] * X["chembl_max_phase"]

    # Phase squared (non-linear phase effect)
    if "phase" in X.columns:
        X["phase_sq"] = X["phase"] ** 2

    # Enrollment per site (trial efficiency)
    if "enrollment" in X.columns and "num_sites" in X.columns:
        denom = X["num_sites"].clip(lower=1)
        X["enrollment_per_site"] = X["enrollment"] / denom
        X["log_enrollment_per_site"] = np.log1p(X["enrollment_per_site"])

    # Biomarker selection × target evidence (precision medicine signal)
    if "has_biomarker_selection" in X.columns and "ot_overall_score" in X.columns:
        X["biomarker_x_evidence"] = X["has_biomarker_selection"] * X["ot_overall_score"]

    # Prior phase success × phase (compounding success signal)
    if "prior_phase_success" in X.columns and "phase" in X.columns:
        X["prior_success_x_phase"] = X["prior_phase_success"] * X["phase"]

    # Citation velocity × preprint count (research momentum)
    if "openalex_citation_velocity" in X.columns and "biorxiv_preprint_count" in X.columns:
        X["research_momentum"] = X["openalex_citation_velocity"] + X["biorxiv_preprint_count"]
        X["log_research_momentum"] = np.log1p(X["research_momentum"])

    # DMC presence × num sites (rigor signal)
    if "has_dmc" in X.columns and "num_sites" in X.columns:
        X["dmc_x_sites"] = X["has_dmc"] * np.log1p(X["num_sites"])

    return X, y

# ---------------------------------------------------------------------------
# Model definition — MODIFY THIS
# ---------------------------------------------------------------------------

MODEL = HistGradientBoostingClassifier(
    max_iter=1000,
    max_depth=2,
    learning_rate=0.02,
    min_samples_leaf=5,
    l2_regularization=0.1,
    random_state=42,
)

K_FEATURES = 999  # select all non-constant features (effectively no MI filter)

# ---------------------------------------------------------------------------
# Training loop (structure is stable, but agent can modify)
# ---------------------------------------------------------------------------

def main():
    start = time.time()

    # Load data
    df = pd.read_csv(DATA_DIR / "trials_raw.csv")

    # Build features
    X, y = build_features(df)
    all_feature_names = list(X.columns)

    # Train/val split
    val_ids_path = DATA_DIR / "val_ids.json"
    if val_ids_path.exists():
        with open(val_ids_path) as f:
            val_ids = set(json.load(f))
        train_mask = ~df["nct_id"].isin(val_ids)
    else:
        train_mask = pd.Series([True] * len(df))

    X_train = X[train_mask].copy()
    y_train = y[train_mask].copy()

    # Drop constant features (zero variance) before MI selection
    non_const = [f for f in all_feature_names if X_train[f].std() > 0]
    X_train_nc = X_train[non_const]

    # MI-based feature selection: pick top K from non-constant features
    selector = SelectKBest(mutual_info_classif, k=min(K_FEATURES, len(non_const)))
    selector.fit(X_train_nc, y_train)
    feature_names_selected = [non_const[i] for i in selector.get_support(indices=True)]

    # Keep only selected features
    X_train_sel = X_train[feature_names_selected]

    # Scale selected features
    scaler = RobustScaler()
    X_scaled = scaler.fit_transform(X_train_sel)

    # Train
    MODEL.fit(X_scaled, y_train)

    # CV score (informational only — real eval is in prepare.py)
    cv = cross_val_score(MODEL, X_scaled, y_train, cv=5, scoring="roc_auc")

    elapsed = time.time() - start

    # Save model bundle — feature_names holds only selected features
    # prepare.py will align val features to this list, then scale + predict
    bundle = {
        "model": MODEL,
        "scaler": scaler,
        "feature_names": feature_names_selected,
    }
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(bundle, f)

    # Output in grep-friendly format
    print(f"cv_auc_roc:        {np.mean(cv):.6f}")
    print(f"cv_auc_std:        {np.std(cv):.6f}")
    print(f"train_n_features:  {len(feature_names_selected)}")
    print(f"train_n_samples:   {len(X_train)}")
    print(f"training_seconds:  {elapsed:.1f}")
    print(f"train_model_type:  {type(MODEL).__name__}")

    print(f"\nSelected features:")
    for f in feature_names_selected:
        print(f"  - {f}")


if __name__ == "__main__":
    main()
