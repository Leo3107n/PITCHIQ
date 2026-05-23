"""
Computes per-class and overall accuracy metrics for a trained classifier.
"""
import numpy as np
import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, classification_report
)

ENCODED_PATH = os.path.join(os.path.dirname(__file__), "../../dataset/processed/encoded_dataset.csv")
SCALER_PATH  = os.path.join(os.path.dirname(__file__), "../../saved_models/scaler.pkl")
ENCODER_PATH = os.path.join(os.path.dirname(__file__), "../../saved_models/label_encoder.pkl")

# Must match the 12 features the scaler was fitted on
FEATURE_COLS = [
    "pace", "shooting", "passing", "dribbling", "defending",
    "physical", "stamina", "strength", "agility", "vision",
    "preferred_foot_encoded", "height_cm_norm",
]


def evaluate_model(model_path: str) -> dict:
    """
    Loads a saved classifier and evaluates it on the held-out test split.
    Returns a dict with accuracy, precision, recall, f1, and per-class report.
    """
    df      = pd.read_csv(ENCODED_PATH)
    scaler  = joblib.load(SCALER_PATH)
    le      = joblib.load(ENCODER_PATH)
    clf     = joblib.load(model_path)

    X = scaler.transform(df[FEATURE_COLS])
    y = df["position_encoded"].values

    _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    y_pred = clf.predict(X_test)

    return {
        "accuracy":  round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred, average="weighted", zero_division=0), 4),
        "recall":    round(recall_score(y_test, y_pred, average="weighted", zero_division=0), 4),
        "f1":        round(f1_score(y_test, y_pred, average="weighted", zero_division=0), 4),
        "report":    classification_report(y_test, y_pred, target_names=le.classes_, zero_division=0),
    }


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else \
        os.path.join(os.path.dirname(__file__), "../../saved_models/best_classifier.pkl")
    result = evaluate_model(path)
    print(f"Accuracy : {result['accuracy']}")
    print(f"Precision: {result['precision']}")
    print(f"Recall   : {result['recall']}")
    print(f"F1       : {result['f1']}")
    print("\nPer-class report:")
    print(result["report"])
