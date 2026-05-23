"""
Finds the N most similar players to a given attribute vector using cosine similarity.
"""
import numpy as np
import pandas as pd
import joblib
import os
from sklearn.metrics.pairwise import cosine_similarity

CLEANED_PATH = os.path.join(os.path.dirname(__file__), "../../dataset/processed/cleaned_players.csv")
SCALER_PATH  = os.path.join(os.path.dirname(__file__), "../../saved_models/scaler.pkl")

# 10 core attributes accepted from the API
FEATURE_COLS = ["pace","shooting","passing","dribbling","defending",
                "physical","stamina","strength","agility","vision"]

# Scaler was fitted on 12 features — append defaults for the 2 extras
SCALER_COLS     = FEATURE_COLS + ["preferred_foot_encoded", "height_cm_norm"]
_FOOT_DEFAULT   = 1.0   # right-footed
_HEIGHT_DEFAULT = 1.80  # average height normalised

_df     = None
_scaler = None
_X      = None   # pre-scaled matrix of all players (12 features)


def _load():
    global _df, _scaler, _X
    if _df is None:
        _df     = pd.read_csv(CLEANED_PATH)
        _scaler = joblib.load(SCALER_PATH)
        # Build 12-feature matrix for all players
        _X = _scaler.transform(_df[SCALER_COLS])


def find_similar(player_attrs: dict, top_n: int = 5) -> list:
    """
    player_attrs: dict with 10 core attribute keys.
    Returns list of dicts: {name, position, similarity, ...10 attrs}
    """
    _load()
    row = [player_attrs.get(c, 50) for c in FEATURE_COLS] + [_FOOT_DEFAULT, _HEIGHT_DEFAULT]
    vec = pd.DataFrame([row], columns=SCALER_COLS)
    vec_scaled = _scaler.transform(vec)

    sims = cosine_similarity(vec_scaled, _X)[0]
    top_idx = np.argsort(sims)[::-1][:top_n]

    results = []
    for i in top_idx:
        row_data = _df.iloc[i]
        results.append({
            "name":       row_data["name"],
            "position":   row_data["position"],
            "similarity": round(float(sims[i]) * 100, 1),
            **{c: int(row_data[c]) for c in FEATURE_COLS}
        })
    return results
