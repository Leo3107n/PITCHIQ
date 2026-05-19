"""
Computes ideal position attribute profiles from the real cleaned dataset.
Uses the 75th percentile per position — represents a genuinely good player.
Outputs the POSITION_PROFILES dict used by prediction_service.py.

Usage (from project root):
    python ml_models/preprocessing/compute_profiles.py
"""
import pandas as pd
import numpy as np
import os

CLEANED = os.path.join(os.path.dirname(__file__), "../../dataset/processed/cleaned_players.csv")
FEATURE_COLS = ["pace","shooting","passing","dribbling","defending",
                "physical","stamina","strength","agility","vision"]


def compute():
    df = pd.read_csv(CLEANED)
    profiles = {}
    for pos in sorted(df["position"].unique()):
        sub = df[df["position"] == pos]
        profiles[pos] = {col: int(round(sub[col].quantile(0.75))) for col in FEATURE_COLS}

    print("POSITION_PROFILES = {")
    for pos, attrs in profiles.items():
        vals = ", ".join(f'"{k}":{v}' for k, v in attrs.items())
        print(f'    "{pos}":  {{{vals}}},')
    print("}")
    return profiles


if __name__ == "__main__":
    compute()
