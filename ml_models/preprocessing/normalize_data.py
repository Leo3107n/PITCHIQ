"""
Normalizes feature columns using StandardScaler and saves scaler + normalized CSV.
Fix 1: Scaler now includes preferred_foot_encoded and height_cm_norm.
"""
import pandas as pd
import joblib
import os

CLEANED_PATH = os.path.join(os.path.dirname(__file__), "../../dataset/processed/cleaned_players.csv")
NORM_PATH    = os.path.join(os.path.dirname(__file__), "../../dataset/processed/normalized_players.csv")
SCALER_PATH  = os.path.join(os.path.dirname(__file__), "../../saved_models/scaler.pkl")

FEATURE_COLS = [
    "pace", "shooting", "passing", "dribbling", "defending",
    "physical", "stamina", "strength", "agility", "vision",
    "preferred_foot_encoded",
    "height_cm_norm",
]


def normalize():
    from sklearn.preprocessing import StandardScaler
    df = pd.read_csv(CLEANED_PATH)
    scaler = StandardScaler()
    df_norm = df.copy()
    df_norm[FEATURE_COLS] = scaler.fit_transform(df[FEATURE_COLS])
    os.makedirs(os.path.dirname(SCALER_PATH), exist_ok=True)
    joblib.dump(scaler, SCALER_PATH)
    df_norm.to_csv(NORM_PATH, index=False)
    print(f"Normalized dataset saved -> {NORM_PATH}")
    print(f"Scaler saved -> {SCALER_PATH}  (features: {FEATURE_COLS})")
    return df_norm, scaler


if __name__ == "__main__":
    normalize()
