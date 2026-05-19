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

FEATURE_COLS = ["pace","shooting","passing","dribbling","defending",
                "physical","stamina","strength","agility","vision"]

_df     = None
_scaler = None
_X      = None

def _load():
    global _df, _scaler, _X
    if _df is None:
        _df     = pd.read_csv(CLEANED_PATH)
        _scaler = joblib.load(SCALER_PATH)
        _X      = _scaler.transform(_df[FEATURE_COLS])

def find_similar(player_attrs: dict, top_n: int = 5) -> list:
    """
    player_attrs: dict with keys matching FEATURE_COLS
    Returns list of dicts: {name, position, similarity_score, ...attrs}
    """
    _load()
    vec = pd.DataFrame([[player_attrs.get(c, 50) for c in FEATURE_COLS]], columns=FEATURE_COLS)
    vec_scaled = _scaler.transform(vec)
    sims = cosine_similarity(vec_scaled, _X)[0]
    top_idx = np.argsort(sims)[::-1][:top_n]
    results = []
    for i in top_idx:
        row = _df.iloc[i]
        results.append({
            "name": row["name"],
            "position": row["position"],
            "similarity": round(float(sims[i]) * 100, 1),
            **{c: int(row[c]) for c in FEATURE_COLS}
        })
    return results
