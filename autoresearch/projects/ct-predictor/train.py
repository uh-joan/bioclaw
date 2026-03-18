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
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler

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

    The autoresearch agent should modify this function to engineer
    better features and improve AUC-ROC.
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

    # Handle missing values
    for col in available:
        missing_frac = X[col].isna().mean()
        if missing_frac > 0.1:
            X[f"{col}_missing"] = X[col].isna().astype(int)
        X[col] = X[col].fillna(X[col].median())

    # Categorical features (frequency encoding)
    for col in ["indication_area", "endpoint_type", "sponsor_type",
                "allocation", "masking", "intervention_type"]:
        if col in df.columns:
            freq = df[col].value_counts(normalize=True)
            X[f"{col}_freq"] = df[col].map(freq).fillna(0)

    # Engineered features
    if "ot_genetic_score" in X.columns and "phase" in X.columns:
        X["genetic_x_phase"] = X["ot_genetic_score"] * X["phase"]

    if "chembl_selectivity" in X.columns:
        X["log_selectivity"] = np.log1p(X["chembl_selectivity"])

    for col in ["chembl_best_ic50_nm", "bindingdb_ki_nm", "bindingdb_kd_nm"]:
        if col in X.columns:
            X[f"log_{col}"] = np.log1p(X[col])

    if "enrollment" in X.columns:
        X["log_enrollment"] = np.log1p(X["enrollment"])

    if "pubmed_target_pub_count" in X.columns and "pubmed_drug_pub_count" in X.columns:
        X["pub_ratio"] = (X["pubmed_drug_pub_count"] + 1) / (X["pubmed_target_pub_count"] + 1)

    genetic = [c for c in ["ot_genetic_score", "gwas_hit_count", "clinvar_pathogenic_count"] if c in X.columns]
    if len(genetic) > 1:
        X["total_genetic_evidence"] = X[genetic].sum(axis=1)

    safety = [c for c in ["fda_class_ae_count", "drugbank_interaction_count", "chembl_selectivity"] if c in X.columns]
    if len(safety) > 1:
        X["safety_risk_proxy"] = X[safety].sum(axis=1)

    reg = [c for c in ["fda_breakthrough", "fda_fast_track", "fda_orphan"] if c in X.columns]
    if reg:
        X["regulatory_advantage"] = X[reg].sum(axis=1)

    if "stringdb_interaction_degree" in X.columns and "reactome_pathway_count" in X.columns:
        X["network_importance"] = X["stringdb_interaction_degree"] * X["reactome_pathway_count"]

    if "medicare_indication_spend" in X.columns and "medicaid_indication_spend" in X.columns:
        X["total_healthcare_spend"] = X["medicare_indication_spend"] + X["medicaid_indication_spend"]

    return X, y

# ---------------------------------------------------------------------------
# Model definition — MODIFY THIS
# ---------------------------------------------------------------------------

MODEL = GradientBoostingClassifier(
    n_estimators=100,
    max_depth=4,
    learning_rate=0.1,
    min_samples_split=10,
    min_samples_leaf=5,
    subsample=0.8,
    random_state=42,
)

# ---------------------------------------------------------------------------
# Training loop (structure is stable, but agent can modify)
# ---------------------------------------------------------------------------

def main():
    start = time.time()

    # Load data
    df = pd.read_csv(DATA_DIR / "trials_raw.csv")

    # Build features
    X, y = build_features(df)
    feature_names = list(X.columns)

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

    # Scale
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)

    # Train
    MODEL.fit(X_scaled, y_train)

    # CV score (informational only — real eval is in prepare.py)
    cv = cross_val_score(MODEL, X_scaled, y_train, cv=5, scoring="roc_auc")

    elapsed = time.time() - start

    # Save model bundle
    bundle = {
        "model": MODEL,
        "scaler": scaler,
        "feature_names": feature_names,
    }
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(bundle, f)

    # Output in grep-friendly format
    print(f"cv_auc_roc:        {np.mean(cv):.6f}")
    print(f"cv_auc_std:        {np.std(cv):.6f}")
    print(f"train_n_features:  {len(feature_names)}")
    print(f"train_n_samples:   {len(X_train)}")
    print(f"training_seconds:  {elapsed:.1f}")
    print(f"train_model_type:  {type(MODEL).__name__}")

    # Top features
    importances = MODEL.feature_importances_
    top_idx = np.argsort(importances)[::-1][:10]
    print(f"\nTop 10 features:")
    for i, idx in enumerate(top_idx):
        print(f"  {i+1}. {feature_names[idx]}: {importances[idx]:.4f}")


if __name__ == "__main__":
    main()
