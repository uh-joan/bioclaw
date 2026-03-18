#!/usr/bin/env python3
"""
Evaluation for Clinical Trial Outcome Predictor

*** THIS FILE IS FROZEN — DO NOT MODIFY ***

Evaluates the trained model on the held-out validation set.
The autoresearch agent must NOT modify this file.
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
    classification_report,
    confusion_matrix,
    average_precision_score,
    brier_score_loss,
)

from features import load_and_engineer_features

DATA_DIR = Path(__file__).parent / "data"
MODEL_PATH = Path(__file__).parent / "model.pkl"


def evaluate():
    """Evaluate model on held-out validation set."""

    # Load model bundle
    if not MODEL_PATH.exists():
        print("ERROR: model.pkl not found. Run train.py first.")
        sys.exit(1)

    with open(MODEL_PATH, "rb") as f:
        bundle = pickle.load(f)

    model = bundle["model"]
    scaler = bundle["scaler"]
    feature_names = bundle["feature_names"]

    # Load validation IDs
    val_ids_path = DATA_DIR / "val_ids.json"
    if not val_ids_path.exists():
        print("ERROR: data/val_ids.json not found. Create validation split first.")
        sys.exit(1)

    with open(val_ids_path) as f:
        val_ids = set(json.load(f))

    # Load features (same pipeline as training)
    X, y, current_features = load_and_engineer_features()
    raw = pd.read_csv(DATA_DIR / "trials_raw.csv")

    # Filter to validation set
    val_mask = raw["nct_id"].isin(val_ids)
    X_val = X[val_mask].copy()
    y_val = y[val_mask].copy()

    if len(X_val) == 0:
        print("ERROR: No validation samples found.")
        sys.exit(1)

    # Ensure feature alignment — use only features the model was trained on
    missing_features = set(feature_names) - set(X_val.columns)
    extra_features = set(X_val.columns) - set(feature_names)

    if missing_features:
        for f in missing_features:
            X_val[f] = 0  # Fill missing features with 0
    X_val = X_val[feature_names]  # Reorder to match training

    # Scale using training scaler
    X_val_scaled = scaler.transform(X_val)

    # Predictions
    y_pred_proba = model.predict_proba(X_val_scaled)[:, 1]
    y_pred = model.predict(X_val_scaled)

    # === METRICS ===
    auc_roc = roc_auc_score(y_val, y_pred_proba)
    avg_precision = average_precision_score(y_val, y_pred_proba)
    brier = brier_score_loss(y_val, y_pred_proba)

    # Precision at 80% recall
    precision_arr, recall_arr, _ = precision_recall_curve(y_val, y_pred_proba)
    # Find precision at recall >= 0.80
    mask_80 = recall_arr >= 0.80
    precision_at_80_recall = precision_arr[mask_80].max() if mask_80.any() else 0.0

    # Confusion matrix
    cm = confusion_matrix(y_val, y_pred)
    tn, fp, fn, tp = cm.ravel()

    # === OUTPUT (parsed by autoresearch loop) ===
    print("=" * 60)
    print("EVALUATION RESULTS")
    print("=" * 60)
    print(f"AUC-ROC: {auc_roc:.4f}")
    print(f"Precision@80%Recall: {precision_at_80_recall:.4f}")
    print(f"Average Precision: {avg_precision:.4f}")
    print(f"Brier Score: {brier:.4f}")
    print(f"Validation samples: {len(y_val)}")
    print(f"  Success: {y_val.sum()} ({y_val.mean():.1%})")
    print(f"  Failure: {(1-y_val).sum()} ({(1-y_val).mean():.1%})")
    print(f"Confusion Matrix:")
    print(f"  TP={tp} FP={fp}")
    print(f"  FN={fn} TN={tn}")
    print(f"Features used: {len(feature_names)}")
    print(f"Model type: {type(model).__name__}")
    print(f"Training CV AUC: {bundle.get('cv_auc_mean', 'N/A')}")
    print("=" * 60)

    # Machine-readable output for the autoresearch loop
    results = {
        "auc_roc": round(auc_roc, 6),
        "precision_at_80_recall": round(precision_at_80_recall, 6),
        "average_precision": round(avg_precision, 6),
        "brier_score": round(brier, 6),
        "n_val_samples": len(y_val),
        "n_features": len(feature_names),
        "model_type": type(model).__name__,
        "tp": int(tp),
        "fp": int(fp),
        "fn": int(fn),
        "tn": int(tn),
    }
    results_path = Path(__file__).parent / "last_eval.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)

    return results


if __name__ == "__main__":
    evaluate()
