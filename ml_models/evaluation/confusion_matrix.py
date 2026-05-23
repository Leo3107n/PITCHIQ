"""
Generates and optionally saves a confusion matrix for a trained classifier.
"""
import numpy as np
import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix

ENCODED_PATH = os.path.join(os.path.dirname(__file__), "../../dataset/processed/encoded_dataset.csv")
SCALER_PATH  = os.path.join(os.path.dirname(__file__), "../../saved_models/scaler.pkl")
ENCODER_PATH = os.path.join(os.path.dirname(__file__), "../../saved_models/label_encoder.pkl")

# Must match the 12 features the scaler was fitted on
FEATURE_COLS = [
    "pace", "shooting", "passing", "dribbling", "defending",
    "physical", "stamina", "strength", "agility", "vision",
    "preferred_foot_encoded", "height_cm_norm",
]


def get_confusion_matrix(model_path: str) -> tuple:
    """
    Returns (cm_array, class_labels).
    """
    df     = pd.read_csv(ENCODED_PATH)
    scaler = joblib.load(SCALER_PATH)
    le     = joblib.load(ENCODER_PATH)
    clf    = joblib.load(model_path)

    X = scaler.transform(df[FEATURE_COLS])
    y = df["position_encoded"].values

    _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    y_pred = clf.predict(X_test)

    cm = confusion_matrix(y_test, y_pred)
    return cm, list(le.classes_)


def print_confusion_matrix(model_path: str):
    cm, labels = get_confusion_matrix(model_path)
    col_w = max(len(l) for l in labels) + 2
    header = " " * col_w + "".join(f"{l:>{col_w}}" for l in labels)
    print(header)
    for i, row in enumerate(cm):
        print(f"{labels[i]:<{col_w}}" + "".join(f"{v:>{col_w}}" for v in row))


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else \
        os.path.join(os.path.dirname(__file__), "../../saved_models/best_classifier.pkl")
    print_confusion_matrix(path)
