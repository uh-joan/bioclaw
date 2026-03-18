#!/usr/bin/env python3
"""
Feature Engineering for Clinical Trial Outcome Predictor

This file is MUTABLE — the autoresearch agent modifies it to improve AUC-ROC.

Reads data/trials_raw.csv and outputs a feature matrix + labels suitable for
sklearn models.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import LabelEncoder, StandardScaler

DATA_DIR = Path(__file__).parent / "data"


def load_and_engineer_features() -> tuple[pd.DataFrame, pd.Series, list[str]]:
    """
    Load raw trial data and engineer features for the classifier.

    Returns:
        X: Feature matrix (DataFrame)
        y: Labels (Series, 1=success, 0=failure)
        feature_names: List of feature names
    """
    df = pd.read_csv(DATA_DIR / "trials_raw.csv")

    # === Target variable ===
    y = df["label"].astype(int)

    # === Numeric features — use directly ===
    numeric_cols = [
        # Trial design
        "phase",
        "enrollment",
        "num_arms",
        "has_dmc",
        "num_secondary_endpoints",
        "num_sites",
        "has_biomarker_selection",
        "competitor_trial_count",
        "prior_phase_success",

        # OpenTargets
        "ot_genetic_score",
        "ot_somatic_score",
        "ot_literature_score",
        "ot_animal_model_score",
        "ot_known_drug_score",
        "ot_affected_pathway_score",
        "ot_overall_score",
        "ot_target_tractability",

        # ChEMBL
        "chembl_selectivity",
        "chembl_best_ic50_nm",
        "chembl_num_assays",
        "chembl_max_phase",
        "chembl_moa_count",

        # DrugBank
        "drugbank_interaction_count",
        "drugbank_target_count",
        "drugbank_enzyme_count",
        "drugbank_transporter_count",
        "drugbank_half_life_hours",
        "drugbank_molecular_weight",

        # BindingDB
        "bindingdb_ki_nm",
        "bindingdb_kd_nm",
        "bindingdb_num_measurements",

        # ClinPGx
        "clinpgx_guideline_count",
        "clinpgx_actionable",
        "clinpgx_cyp_substrate_count",

        # FDA
        "fda_prior_approval_class",
        "fda_breakthrough",
        "fda_fast_track",
        "fda_orphan",
        "fda_class_ae_count",

        # Publication signals
        "pubmed_target_pub_count",
        "pubmed_drug_pub_count",
        "openalex_citation_velocity",
        "biorxiv_preprint_count",

        # Healthcare spend
        "medicare_indication_spend",
        "medicaid_indication_spend",

        # Pathway/network
        "reactome_pathway_count",
        "stringdb_interaction_degree",
        "stringdb_betweenness",

        # Genomic
        "gtex_tissue_specificity",
        "gnomad_pli",
        "gnomad_loeuf",
        "clinvar_pathogenic_count",
        "gwas_hit_count",
        "gwas_best_pvalue",
        "depmap_essentiality",
        "cbioportal_mutation_freq",

        # Disease complexity
        "hpo_phenotype_count",
        "monarch_gene_count",

        # EMA
        "ema_approved_similar",
        "eu_filings_count",
    ]

    # Filter to columns that exist in the data
    available_numeric = [c for c in numeric_cols if c in df.columns]
    X = df[available_numeric].copy()

    # === Handle missing values ===
    # Strategy: fill with median for numeric, add missingness indicators for
    # columns with >10% missing
    for col in available_numeric:
        missing_frac = X[col].isna().mean()
        if missing_frac > 0.1:
            X[f"{col}_missing"] = X[col].isna().astype(int)
        X[col] = X[col].fillna(X[col].median())

    # === Categorical features ===
    cat_cols = ["indication_area", "endpoint_type", "sponsor_type",
                "allocation", "masking", "intervention_type"]
    for col in cat_cols:
        if col in df.columns:
            # Frequency encoding: replace category with its frequency
            freq = df[col].value_counts(normalize=True)
            X[f"{col}_freq"] = df[col].map(freq).fillna(0)

    # === Engineered features ===

    # Genetic evidence × phase interaction
    if "ot_genetic_score" in X.columns and "phase" in X.columns:
        X["genetic_x_phase"] = X["ot_genetic_score"] * X["phase"]

    # Selectivity ratio (lower = more selective = better)
    if "chembl_selectivity" in X.columns:
        X["log_selectivity"] = np.log1p(X["chembl_selectivity"])

    # Potency: log-transform IC50/Ki (highly skewed)
    for col in ["chembl_best_ic50_nm", "bindingdb_ki_nm", "bindingdb_kd_nm"]:
        if col in X.columns:
            X[f"log_{col}"] = np.log1p(X[col])

    # Enrollment log (diminishing returns of bigger trials)
    if "enrollment" in X.columns:
        X["log_enrollment"] = np.log1p(X["enrollment"])

    # Publication momentum: target pubs relative to drug pubs
    if "pubmed_target_pub_count" in X.columns and "pubmed_drug_pub_count" in X.columns:
        X["pub_ratio"] = (X["pubmed_drug_pub_count"] + 1) / (X["pubmed_target_pub_count"] + 1)

    # Total genetic evidence (multi-source)
    genetic_cols = ["ot_genetic_score", "gwas_hit_count", "clinvar_pathogenic_count"]
    available_genetic = [c for c in genetic_cols if c in X.columns]
    if len(available_genetic) > 1:
        X["total_genetic_evidence"] = X[available_genetic].sum(axis=1)

    # Safety risk proxy
    safety_cols = ["fda_class_ae_count", "drugbank_interaction_count", "chembl_selectivity"]
    available_safety = [c for c in safety_cols if c in X.columns]
    if len(available_safety) > 1:
        X["safety_risk_proxy"] = X[available_safety].sum(axis=1)

    # Regulatory advantage score
    reg_cols = ["fda_breakthrough", "fda_fast_track", "fda_orphan"]
    available_reg = [c for c in reg_cols if c in X.columns]
    if available_reg:
        X["regulatory_advantage"] = X[available_reg].sum(axis=1)

    # Target network importance
    if "stringdb_interaction_degree" in X.columns and "reactome_pathway_count" in X.columns:
        X["network_importance"] = (
            X["stringdb_interaction_degree"] * X["reactome_pathway_count"]
        )

    # Healthcare unmet need proxy
    if "medicare_indication_spend" in X.columns and "medicaid_indication_spend" in X.columns:
        X["total_healthcare_spend"] = (
            X["medicare_indication_spend"] + X["medicaid_indication_spend"]
        )

    feature_names = list(X.columns)
    return X, y, feature_names
