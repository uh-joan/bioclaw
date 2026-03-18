#!/usr/bin/env python3
"""
Model Training for Clinical Trial Outcome Predictor

This file is MUTABLE — the autoresearch agent modifies it to improve AUC-ROC.

Trains a classifier on the feature-engineered dataset and saves model.pkl.
"""

import json
import pickle
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler

from features import load_and_engineer_features

DATA_DIR = Path(__file__).parent / "data"
MODEL_PATH = Path(__file__).parent / "model.pkl"


def get_train_ids() -> set:
    """Get training trial IDs (exclude validation set)."""
    val_ids_path = DATA_DIR / "val_ids.json"
    if val_ids_path.exists():
        with open(val_ids_path) as f:
            val_ids = set(json.load(f))
    else:
        val_ids = set()

    raw = pd.read_csv(DATA_DIR / "trials_raw.csv")
    all_ids = set(raw["nct_id"].tolist())
    return all_ids - val_ids


def train():
    """Train the model and save to model.pkl."""
    start = time.time()

    # Load features
    X, y, feature_names = load_and_engineer_features()

    # Filter to training set only
    raw = pd.read_csv(DATA_DIR / "trials_raw.csv")
    val_ids_path = DATA_DIR / "val_ids.json"
    if val_ids_path.exists():
        with open(val_ids_path) as f:
            val_ids = set(json.load(f))
        train_mask = ~raw["nct_id"].isin(val_ids)
    else:
        # No validation split yet — use all data with cross-validation
        train_mask = pd.Series([True] * len(raw))

    X_train = X[train_mask].copy()
    y_train = y[train_mask].copy()

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)

    # === MODEL ===
    # Baseline: Gradient Boosting Classifier
    # The autoresearch agent should iterate on this
    model = GradientBoostingClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        min_samples_split=10,
        min_samples_leaf=5,
        subsample=0.8,
        random_state=42,
    )

    model.fit(X_train_scaled, y_train)

    # Cross-validation on training set (for monitoring, not for evaluation)
    cv_scores = cross_val_score(
        model, X_train_scaled, y_train, cv=5, scoring="roc_auc"
    )

    elapsed = time.time() - start

    # Save model bundle
    bundle = {
        "model": model,
        "scaler": scaler,
        "feature_names": feature_names,
        "cv_auc_mean": float(np.mean(cv_scores)),
        "cv_auc_std": float(np.std(cv_scores)),
        "n_features": len(feature_names),
        "n_train_samples": len(X_train),
        "training_time_seconds": elapsed,
    }
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(bundle, f)

    # Print training summary
    print(f"Training complete in {elapsed:.1f}s")
    print(f"Features: {len(feature_names)}")
    print(f"Training samples: {len(X_train)}")
    print(f"CV AUC-ROC: {np.mean(cv_scores):.4f} ± {np.std(cv_scores):.4f}")
    print(f"Model: {type(model).__name__}")
    print(f"Saved to {MODEL_PATH}")

    # Print top feature importances
    importances = model.feature_importances_
    top_idx = np.argsort(importances)[::-1][:10]
    print("\nTop 10 features:")
    for i, idx in enumerate(top_idx):
        print(f"  {i+1}. {feature_names[idx]}: {importances[idx]:.4f}")

    return bundle


if __name__ == "__main__":
    train()
