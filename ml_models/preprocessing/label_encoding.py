"""
Encodes the 'position' column with LabelEncoder and saves encoder + encoded CSV.
"""
import pandas as pd
import joblib
import os

CLEANED_PATH  = os.path.join(os.path.dirname(__file__), "../../dataset/processed/cleaned_players.csv")
ENCODED_PATH  = os.path.join(os.path.dirname(__file__), "../../dataset/processed/encoded_dataset.csv")
ENCODER_PATH  = os.path.join(os.path.dirname(__file__), "../../saved_models/label_encoder.pkl")

def encode():
    from sklearn.preprocessing import LabelEncoder
    df = pd.read_csv(CLEANED_PATH)
    le = LabelEncoder()
    df["position_encoded"] = le.fit_transform(df["position"])
    os.makedirs(os.path.dirname(ENCODER_PATH), exist_ok=True)
    joblib.dump(le, ENCODER_PATH)
    df.to_csv(ENCODED_PATH, index=False)
    print(f"Encoded dataset saved -> {ENCODED_PATH}")
    print(f"Classes: {list(le.classes_)}")
    return df, le

if __name__ == "__main__":
    encode()
