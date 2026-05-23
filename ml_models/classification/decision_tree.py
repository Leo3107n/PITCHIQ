"""
Decision Tree classifier for position prediction.
Uses 12 features: 10 attributes + preferred_foot_encoded + height_cm_norm.
"""
import pandas as pd
import joblib
import os
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

ENCODED_PATH = os.path.join(os.path.dirname(__file__), "../../dataset/processed/encoded_dataset.csv")
SCALER_PATH  = os.path.join(os.path.dirname(__file__), "../../saved_models/scaler.pkl")
MODEL_PATH   = os.path.join(os.path.dirname(__file__), "../../saved_models/decision_tree.pkl")

FEATURE_COLS = [
    "pace", "shooting", "passing", "dribbling", "defending",
    "physical", "stamina", "strength", "agility", "vision",
    "preferred_foot_encoded", "height_cm_norm",
]


def train():
    df = pd.read_csv(ENCODED_PATH)
    X = df[FEATURE_COLS]
    y = df["position_encoded"].values

    scaler = joblib.load(SCALER_PATH)
    X_scaled = scaler.transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )

    clf = DecisionTreeClassifier(
        max_depth=20,
        min_samples_leaf=3,
        class_weight="balanced",
        random_state=42,
    )
    clf.fit(X_train, y_train)

    acc = accuracy_score(y_test, clf.predict(X_test))
    print(f"Decision Tree accuracy: {acc:.4f}")

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(clf, MODEL_PATH)
    print(f"Model saved -> {MODEL_PATH}")
    return clf, acc


if __name__ == "__main__":
    train()
