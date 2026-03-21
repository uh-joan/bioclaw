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
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier, VotingClassifier, HistGradientBoostingClassifier, ExtraTreesClassifier
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
        "ot_overall_score", "ot_target_tractability", "target_disease_score",
        "ot_genetic_score", "ot_somatic_score", "ot_literature_score",
        "ot_animal_model_score", "ot_known_drug_score", "ot_affected_pathway_score",
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
        "reactome_pathway_count", "stringdb_interaction_degree", "stringdb_betweenness",
        # Genomic
        "gtex_tissue_specificity", "gnomad_pli", "gnomad_loeuf",
        "clinvar_pathogenic_count", "gwas_hit_count", "gwas_best_pvalue",
        "depmap_essentiality", "cbioportal_mutation_freq",
        # Disease complexity
        "hpo_phenotype_count", "monarch_gene_count",
        # EMA
        "ema_approved_similar", "eu_filings_count",
        # PDB structure
        "pdb_structure_count", "pdb_has_ligand_bound",
        # AlphaFold
        "alphafold_available", "alphafold_confidence",
        # BRENDA (enzyme kinetics)
        "brenda_has_kinetics", "brenda_km_count",
        # CDC surveillance
        "cdc_has_surveillance", "nlm_condition_codes",
        # COSMIC (cancer)
        "cosmic_is_driver", "cosmic_mutation_count",
        # Ensembl
        "ensembl_transcript_count",
        # GEO datasets
        "geo_dataset_count",
        # Gene Ontology
        "go_biological_process_count", "go_molecular_function_count", "go_term_count",
        # KEGG pathways
        "kegg_pathway_count",
        # OpenTargets additional
        "ot_disease_association_count", "ot_safety_liability_count",
        # PDB structure
        # PubChem molecular descriptors
        "pubchem_complexity", "pubchem_hbond_acceptor", "pubchem_hbond_donor",
        "pubchem_molecular_weight", "pubchem_rotatable_bonds", "pubchem_xlogp",
        # Combination drug features
        "is_combination", "n_drugs", "combo_drug2_has_target",
        "combo_drug2_fda_approved", "combo_drug2_trial_count",
        "combo_drug2_max_phase", "combo_phase_ratio",
        "combo_drug2_pub_count", "combo_drug2_ot_score", "combo_drug2_pli",
        "combo_targets_interact", "combo_shared_pathways", "combo_targets_same_pathway",
        "combo_go_overlap", "combo_bp_overlap", "combo_shared_bp_count",
        # Safety signals
        "target_expression_breadth",
        "combo_drug2_target_disease_score", "combo_drug2_completed_trials",
        "combo_drug2_terminated_trials", "combo_drug2_fail_ratio",
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

    # One-hot encode endpoint_type (OS/PFS/ORR/etc. are strong success signals)
    if "endpoint_type" in df.columns:
        for val in df["endpoint_type"].dropna().unique():
            X[f"endpoint_{val}"] = (df["endpoint_type"] == val).astype(int)

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
                "clinvar_pathogenic_count", "gwas_hit_count"]:
        if col in X.columns:
            X[f"log_{col}"] = np.log1p(X[col])

    # Engineered interactions

    if "ot_overall_score" in X.columns and "phase" in X.columns:
        X["overall_score_x_phase"] = X["ot_overall_score"] * X["phase"]

    if "pubmed_target_pub_count" in X.columns and "pubmed_drug_pub_count" in X.columns:
        X["pub_ratio"] = (X["pubmed_drug_pub_count"] + 1) / (X["pubmed_target_pub_count"] + 1)

    genetic = [c for c in ["ot_overall_score", "gwas_hit_count", "clinvar_pathogenic_count"] if c in X.columns]
    if len(genetic) > 1:
        X["total_genetic_evidence"] = X[genetic].sum(axis=1)

    reg = [c for c in ["fda_prior_approval_class", "ema_approved_similar"] if c in X.columns]
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

    # Oncology × enrollment_per_site (top feature interactions)
    if "is_oncology" in X.columns and "enrollment_per_site" in X.columns:
        X["oncology_x_enr_per_site"] = X["is_oncology"] * X["enrollment_per_site"]
    if "is_oncology" in X.columns and "phase" in X.columns:
        X["oncology_x_phase"] = X["is_oncology"] * X["phase"]
    if "is_immunology" in X.columns and "enrollment_per_site" in X.columns:
        X["immunology_x_enr_per_site"] = X["is_immunology"] * X["enrollment_per_site"]
    if "competitor_trial_count" in X.columns and "phase" in X.columns:
        X["competitor_x_phase"] = X["competitor_trial_count"] * X["phase"]

    # === LEAKAGE GUARD: all target-encoding uses TRAINING labels only ===
    import json as _json
    _val_ids_path = DATA_DIR / "val_ids.json"
    if _val_ids_path.exists():
        with open(_val_ids_path) as _vf:
            _val_ids = set(_json.load(_vf))
        _is_train = ~df["nct_id"].isin(_val_ids)
    else:
        _is_train = pd.Series([True] * len(df))
    _is_train_arr = _is_train.values

    # Same-target historical success rate (TRAIN labels only)
    # "How have other drugs targeting the same gene performed?"
    _cache_path = DATA_DIR / "drug_target_cache.json"
    if _cache_path.exists():
        with open(_cache_path) as _f:
            _target_cache = {k: v for k, v in _json.load(_f).items() if v}
        _targets = df["intervention_name"].str.lower().str.strip().map(
            lambda d: _target_cache.get(str(d).split("+")[0].strip(), "")
        )
        _labels = y.values if hasattr(y, 'values') else y
        # Aggregate from training rows only
        target_success = {}
        target_count = {}
        for t, l, is_tr in zip(_targets, _labels, _is_train_arr):
            if t and is_tr:
                target_success[t] = target_success.get(t, 0) + l
                target_count[t] = target_count.get(t, 0) + 1

        # Global prior for Bayesian smoothing
        _total_success = sum(target_success.values())
        _total_count = sum(target_count.values())
        _global_rate = _total_success / _total_count if _total_count > 0 else 0.5
        _alpha = 5  # smoothing strength toward global prior

        same_target_rate = []
        same_target_n = []
        for t, l, is_tr in zip(_targets, _labels, _is_train_arr):
            if t and target_count.get(t, 0) > 0:
                if is_tr and target_count.get(t, 0) > 1:
                    # LOO for train rows
                    loo_n = target_count[t] - 1
                    loo_s = target_success[t] - l
                    rate = (loo_s + _alpha * _global_rate) / (loo_n + _alpha)
                    same_target_rate.append(rate)
                    same_target_n.append(loo_n)
                elif not is_tr:
                    # Val rows: plain group rate from training data
                    n = target_count[t]
                    s = target_success[t]
                    rate = (s + _alpha * _global_rate) / (n + _alpha)
                    same_target_rate.append(rate)
                    same_target_n.append(n)
                else:
                    same_target_rate.append(_global_rate)
                    same_target_n.append(0)
            else:
                same_target_rate.append(_global_rate)
                same_target_n.append(0)

        X["same_target_success_rate"] = same_target_rate
        X["same_target_trial_count"] = same_target_n

        # Drug2 success rate for combination therapies (split intervention_name on "+")
        _targets2 = df["intervention_name"].str.lower().str.strip().map(
            lambda d: _target_cache.get(str(d).split("+")[1].strip(), "") if "+" in str(d) else ""
        )
        combo2_rate = []
        for t2, l2, is_tr2 in zip(_targets2, _labels, _is_train_arr):
            if t2 and target_count.get(t2, 0) > 0:
                if is_tr2 and target_count.get(t2, 0) > 1:
                    loo_n2 = target_count[t2] - 1
                    loo_s2 = target_success[t2] - l2
                    rate2 = (loo_s2 + _alpha * _global_rate) / (loo_n2 + _alpha)
                elif not is_tr2:
                    n2 = target_count[t2]
                    s2 = target_success[t2]
                    rate2 = (s2 + _alpha * _global_rate) / (n2 + _alpha)
                else:
                    rate2 = _global_rate
            else:
                rate2 = _global_rate
            combo2_rate.append(rate2)
        X["combo_drug2_target_rate"] = combo2_rate

        # Both drugs proven: multiplicative signal
        if "same_target_success_rate" in X.columns:
            X["both_drugs_proven"] = X["same_target_success_rate"] * X["combo_drug2_target_rate"]


    # Safety risk: novel mechanism on ubiquitous target
    if "same_target_trial_count" in X.columns and "target_expression_breadth" in X.columns:
        # Novel target (few prior trials) × ubiquitous expression = high safety risk
        novelty = 1 / (X["same_target_trial_count"] + 1)  # Higher for novel targets
        X["safety_risk_novel_ubiquitous"] = novelty * X["target_expression_breadth"]

    if "ot_safety_liability_count" in X.columns and "target_expression_breadth" in X.columns:
        # Known safety issues × broad expression = compounding risk
        X["safety_risk_compound"] = X["ot_safety_liability_count"] * X["target_expression_breadth"] / 54

    # Genetic validation strength (matters most for novel targets)
    if "same_target_trial_count" in X.columns:
        genetic_evidence = X.get("clinvar_pathogenic_count", 0) + X.get("gwas_hit_count", 0) * 0.1
        novelty = 1 / (X["same_target_trial_count"] + 1)
        X["genetic_validation_for_novel"] = genetic_evidence * novelty

    # Combo quality score: drug2 evidence strength (high = proven combo partner)
    if "combo_drug2_fda_approved" in X.columns and "combo_drug2_completed_trials" in X.columns:
        X["combo_drug2_evidence"] = (
            X["combo_drug2_fda_approved"] * 3 +
            np.log1p(X.get("combo_drug2_completed_trials", 0)) +
            X.get("combo_drug2_max_phase", 0) / 4
        )

    # Combo mechanism complementarity (low GO overlap = good)
    if "combo_go_overlap" in X.columns and "is_combination" in X.columns:
        X["combo_complementary"] = X["is_combination"] * (1 - X["combo_go_overlap"])

    return X, y

# ---------------------------------------------------------------------------
# Model definition — MODIFY THIS
# ---------------------------------------------------------------------------

_gbm = HistGradientBoostingClassifier(
    max_iter=1000,
    max_depth=7,
    learning_rate=0.02,
    min_samples_leaf=4,
    l2_regularization=0.0,
    max_leaf_nodes=31,
    random_state=42,
)
_lr = LogisticRegression(C=0.5, max_iter=1000, random_state=42, solver="lbfgs")
_et = ExtraTreesClassifier(n_estimators=200, max_depth=20, min_samples_leaf=4, random_state=42, n_jobs=-1)
_et2 = ExtraTreesClassifier(n_estimators=200, max_depth=20, min_samples_leaf=4, random_state=7, n_jobs=-1)
_et3 = ExtraTreesClassifier(n_estimators=200, max_depth=20, min_samples_leaf=4, random_state=13, n_jobs=-1)
_et4 = ExtraTreesClassifier(n_estimators=200, max_depth=20, min_samples_leaf=4, random_state=99, max_features=0.7, n_jobs=-1)
_et5 = ExtraTreesClassifier(n_estimators=200, max_depth=20, min_samples_leaf=4, random_state=31, max_features=0.7, n_jobs=-1)
_et6 = ExtraTreesClassifier(n_estimators=200, max_depth=20, min_samples_leaf=4, random_state=53, max_features=0.7, n_jobs=-1)
_et7 = ExtraTreesClassifier(n_estimators=200, max_depth=20, min_samples_leaf=4, random_state=71, max_features=0.5, n_jobs=-1)
_et8 = ExtraTreesClassifier(n_estimators=200, max_depth=20, min_samples_leaf=4, random_state=89, max_features=0.5, n_jobs=-1)
MODEL = VotingClassifier(
    estimators=[("gbm", _gbm), ("et", _et), ("et2", _et2), ("et3", _et3), ("et4", _et4), ("et5", _et5), ("et6", _et6), ("et7", _et7), ("et8", _et8)],
    voting="soft",
    weights=[3, 2, 2, 2, 2, 2, 2, 2, 2],
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

    # Drop constant features (zero variance)
    non_const = [f for f in all_feature_names if X_train[f].std() > 0]

    # MI-based feature selection only when K < n_features (MI is O(n^2*d) — skip if unnecessary)
    if K_FEATURES < len(non_const):
        selector = SelectKBest(mutual_info_classif, k=K_FEATURES)
        selector.fit(X_train[non_const], y_train)
        feature_names_selected = [non_const[i] for i in selector.get_support(indices=True)]
    else:
        feature_names_selected = non_const

    # Keep only selected features
    X_train_sel = X_train[feature_names_selected]

    # Scale selected features
    scaler = RobustScaler()
    X_scaled = scaler.fit_transform(X_train_sel)

    # Train
    MODEL.fit(X_scaled, y_train)

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
    print(f"cv_auc_roc:        N/A")
    print(f"train_n_features:  {len(feature_names_selected)}")
    print(f"train_n_samples:   {len(X_train)}")
    print(f"training_seconds:  {elapsed:.1f}")
    print(f"train_model_type:  {type(MODEL).__name__}")

    print(f"\nSelected features:")
    for f in feature_names_selected:
        print(f"  - {f}")


if __name__ == "__main__":
    main()
