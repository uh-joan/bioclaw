#!/usr/bin/env python3
"""
Data preparation and evaluation for Clinical Trial Outcome Predictor.

*** THIS FILE IS FROZEN — DO NOT MODIFY ***

This is the equivalent of Karpathy's prepare.py. It handles:
1. Data loading and validation split
2. The ground-truth evaluation function (evaluate_auc)

The agent may NOT modify this file. Doing so would compromise
the integrity of the evaluation metric.
"""

import json
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (
    roc_auc_score,
    precision_recall_curve,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

DATA_DIR = Path(__file__).parent / "data"
RAW_CSV = DATA_DIR / "trials_raw.csv"
VAL_IDS_PATH = DATA_DIR / "val_ids.json"
MODEL_PATH = Path(__file__).parent / "model.pkl"

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_raw() -> pd.DataFrame:
    """Load the raw trial dataset."""
    if not RAW_CSV.exists():
        print("ERROR: data/trials_raw.csv not found. Run data collection first.")
        sys.exit(1)
    return pd.read_csv(RAW_CSV)


def get_val_ids() -> set:
    """Load the frozen validation trial IDs."""
    if not VAL_IDS_PATH.exists():
        print("ERROR: data/val_ids.json not found. Run split.py first.")
        sys.exit(1)
    with open(VAL_IDS_PATH) as f:
        return set(json.load(f))


def get_train_mask(df: pd.DataFrame) -> pd.Series:
    """Boolean mask for training rows."""
    val_ids = get_val_ids()
    return ~df["nct_id"].isin(val_ids)


def get_val_mask(df: pd.DataFrame) -> pd.Series:
    """Boolean mask for validation rows."""
    val_ids = get_val_ids()
    return df["nct_id"].isin(val_ids)

# ---------------------------------------------------------------------------
# Evaluation (ground truth — DO NOT MODIFY)
# ---------------------------------------------------------------------------

def evaluate_auc() -> dict:
    """
    Evaluate the trained model on the held-out validation set.

    Loads model.pkl, runs predictions on validation set, computes metrics.
    Prints results in a grep-friendly format matching Karpathy's convention.

    Returns dict with all metrics.
    """
    if not MODEL_PATH.exists():
        print("ERROR: model.pkl not found. Run train.py first.")
        sys.exit(1)

    with open(MODEL_PATH, "rb") as f:
        bundle = pickle.load(f)

    model = bundle["model"]
    scaler = bundle["scaler"]
    feature_names = bundle["feature_names"]

    # Load data and get validation set
    df = load_raw()
    val_mask = get_val_mask(df)

    # Import train.py's feature engineering (it defines build_features)
    # This is safe: we call their function but evaluate with our frozen logic
    from train import build_features
    X, y = build_features(df)

    X_val = X[val_mask].copy()
    y_val = y[val_mask].copy()

    if len(X_val) == 0:
        print("ERROR: No validation samples found.")
        sys.exit(1)

    # Align features to what the model was trained on
    for feat in feature_names:
        if feat not in X_val.columns:
            X_val[feat] = 0
    X_val = X_val[feature_names]

    # Scale and predict
    X_val_scaled = scaler.transform(X_val)
    y_pred_proba = model.predict_proba(X_val_scaled)[:, 1]
    y_pred = model.predict(X_val_scaled)

    # Metrics
    auc_roc = roc_auc_score(y_val, y_pred_proba)
    avg_precision = average_precision_score(y_val, y_pred_proba)
    brier = brier_score_loss(y_val, y_pred_proba)

    precision_arr, recall_arr, _ = precision_recall_curve(y_val, y_pred_proba)
    mask_80 = recall_arr >= 0.80
    p_at_80r = float(precision_arr[mask_80].max()) if mask_80.any() else 0.0

    cm = confusion_matrix(y_val, y_pred)
    tn, fp, fn, tp = cm.ravel()

    # === OUTPUT in grep-friendly format (like Karpathy's val_bpb) ===
    print(f"auc_roc:           {auc_roc:.6f}")
    print(f"p_at_80_recall:    {p_at_80r:.6f}")
    print(f"avg_precision:     {avg_precision:.6f}")
    print(f"brier_score:       {brier:.6f}")
    print(f"n_val_samples:     {len(y_val)}")
    print(f"n_features:        {len(feature_names)}")
    print(f"model_type:        {type(model).__name__}")
    print(f"tp:                {tp}")
    print(f"fp:                {fp}")
    print(f"fn:                {fn}")
    print(f"tn:                {tn}")

    return {
        "auc_roc": auc_roc,
        "p_at_80_recall": p_at_80r,
        "avg_precision": avg_precision,
        "brier_score": brier,
        "n_features": len(feature_names),
        "model_type": type(model).__name__,
    }


if __name__ == "__main__":
    evaluate_auc()
