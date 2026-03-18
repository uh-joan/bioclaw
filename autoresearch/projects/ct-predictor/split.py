#!/usr/bin/env python3
"""
Create train/validation split for the CT predictor dataset.

Run ONCE after data collection to create data/val_ids.json.
Uses stratified split to maintain class balance.
"""

import json
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

DATA_DIR = Path(__file__).parent / "data"


def create_split(val_fraction: float = 0.2, seed: int = 42):
    """Create a stratified train/val split."""
    raw = pd.read_csv(DATA_DIR / "trials_raw.csv")

    if "label" not in raw.columns:
        raise ValueError("Dataset missing 'label' column")
    if "nct_id" not in raw.columns:
        raise ValueError("Dataset missing 'nct_id' column")

    _, val = train_test_split(
        raw["nct_id"],
        test_size=val_fraction,
        stratify=raw["label"],
        random_state=seed,
    )

    val_ids = val.tolist()
    val_path = DATA_DIR / "val_ids.json"
    with open(val_path, "w") as f:
        json.dump(val_ids, f, indent=2)

    n_total = len(raw)
    n_val = len(val_ids)
    n_train = n_total - n_val
    print(f"Split: {n_train} train / {n_val} val (total: {n_total})")
    print(f"Class balance (train): {raw[~raw['nct_id'].isin(val_ids)]['label'].mean():.1%} success")
    print(f"Class balance (val):   {raw[raw['nct_id'].isin(val_ids)]['label'].mean():.1%} success")
    print(f"Saved to {val_path}")


if __name__ == "__main__":
    create_split()
