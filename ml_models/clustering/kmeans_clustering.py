"""
K-Means clustering to group players by playing style.
"""
import pandas as pd
import numpy as np
import joblib
import os
from sklearn.cluster import KMeans

CLEANED_PATH = os.path.join(os.path.dirname(__file__), "../../dataset/processed/cleaned_players.csv")
SCALER_PATH  = os.path.join(os.path.dirname(__file__), "../../saved_models/scaler.pkl")
MODEL_PATH   = os.path.join(os.path.dirname(__file__), "../../saved_models/kmeans_model.pkl")

FEATURE_COLS = ["pace","shooting","passing","dribbling","defending",
                "physical","stamina","strength","agility","vision"]

N_CLUSTERS = 8

def train():
    df = pd.read_csv(CLEANED_PATH)
    scaler = joblib.load(SCALER_PATH)
    X_scaled = scaler.transform(df[FEATURE_COLS])

    km = KMeans(n_clusters=N_CLUSTERS, random_state=42, n_init=10)
    km.fit(X_scaled)

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(km, MODEL_PATH)
    print(f"KMeans model saved -> {MODEL_PATH}  (inertia={km.inertia_:.2f})")
    return km

if __name__ == "__main__":
    train()
