"""
Assigns a player to a cluster and returns cluster statistics.
"""
import numpy as np
import pandas as pd
import joblib
import os

CLEANED_PATH = os.path.join(os.path.dirname(__file__), "../../dataset/processed/cleaned_players.csv")
SCALER_PATH  = os.path.join(os.path.dirname(__file__), "../../saved_models/scaler.pkl")
KMEANS_PATH  = os.path.join(os.path.dirname(__file__), "../../saved_models/kmeans_model.pkl")

# 10 core attributes accepted from the API
FEATURE_COLS = ["pace","shooting","passing","dribbling","defending",
                "physical","stamina","strength","agility","vision"]

# Scaler was fitted on 12 features — append defaults for the 2 extras
SCALER_COLS     = FEATURE_COLS + ["preferred_foot_encoded", "height_cm_norm"]
_FOOT_DEFAULT   = 1.0   # right-footed
_HEIGHT_DEFAULT = 1.80  # average height normalised

_df = _scaler = _km = None


def _load():
    global _df, _scaler, _km
    if _df is None:
        _df     = pd.read_csv(CLEANED_PATH)
        _scaler = joblib.load(SCALER_PATH)
        _km     = joblib.load(KMEANS_PATH)


def get_cluster_info(player_attrs: dict) -> dict:
    _load()
    row = [player_attrs.get(c, 50) for c in FEATURE_COLS] + [_FOOT_DEFAULT, _HEIGHT_DEFAULT]
    vec = pd.DataFrame([row], columns=SCALER_COLS)
    vec_scaled = _scaler.transform(vec)
    cluster_id = int(_km.predict(vec_scaled)[0])

    # Players in same cluster
    all_labels   = _km.labels_
    cluster_mask = all_labels == cluster_id
    cluster_df   = _df[cluster_mask]

    avg_attrs     = {c: round(float(cluster_df[c].mean()), 1) for c in FEATURE_COLS}
    top_positions = cluster_df["position"].value_counts().head(3).to_dict()

    return {
        "cluster_id":        cluster_id,
        "cluster_size":      int(cluster_mask.sum()),
        "avg_attributes":    avg_attrs,
        "dominant_positions": top_positions,
    }
