"""
Random Forest classifier for position prediction.
Uses 12 features: 10 attributes + preferred_foot_encoded + height_cm_norm.
Tuned: 300 estimators, class_weight='balanced_subsample'.
"""
import pandas as pd
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

ENCODED_PATH = os.path.join(os.path.dirname(__file__), "../../dataset/processed/encoded_dataset.csv")
SCALER_PATH  = os.path.join(os.path.dirname(__file__), "../../saved_models/scaler.pkl")
MODEL_PATH   = os.path.join(os.path.dirname(__file__), "../../saved_models/random_forest.pkl")

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

    clf = RandomForestClassifier(
        n_estimators=300,
        max_depth=15,
        min_samples_leaf=5,
        class_weight="balanced_subsample",  # handles CF imbalance without SMOTE
        random_state=42,
        n_jobs=-1,
    )
    clf.fit(X_train, y_train)

    acc = accuracy_score(y_test, clf.predict(X_test))
    print(f"Random Forest accuracy: {acc:.4f}")

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(clf, MODEL_PATH)
    print(f"Model saved -> {MODEL_PATH}")
    return clf, acc


if __name__ == "__main__":
    train()
