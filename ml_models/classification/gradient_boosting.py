"""
Gradient Boosting classifier for position prediction.
Uses sklearn's HistGradientBoostingClassifier — fast, handles imbalance natively,
typically the best performer on tabular data with 10-15 features.

Why Gradient Boosting beats SVM/MLP here:
  - Builds trees sequentially, each correcting the previous one's errors
  - HistGradientBoosting uses histogram binning → fast on 50k+ rows
  - Native support for class_weight='balanced' → no SMOTE needed
  - Robust to feature scale differences (no StandardScaler needed, but we use it anyway)
"""
import pandas as pd
import joblib
import os
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

ENCODED_PATH = os.path.join(os.path.dirname(__file__), "../../dataset/processed/encoded_dataset.csv")
SCALER_PATH  = os.path.join(os.path.dirname(__file__), "../../saved_models/scaler.pkl")
MODEL_PATH   = os.path.join(os.path.dirname(__file__), "../../saved_models/gradient_boosting.pkl")

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

    clf = HistGradientBoostingClassifier(
        max_iter=500,
        max_depth=8,
        learning_rate=0.05,
        min_samples_leaf=20,
        l2_regularization=0.1,
        class_weight="balanced",
        random_state=42,
        early_stopping=True,
        validation_fraction=0.1,
        n_iter_no_change=20,
        verbose=0,
    )
    clf.fit(X_train, y_train)

    acc = accuracy_score(y_test, clf.predict(X_test))
    print(f"Gradient Boosting accuracy: {acc:.4f}  (iterations: {clf.n_iter_})")

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(clf, MODEL_PATH)
    print(f"Model saved -> {MODEL_PATH}")
    return clf, acc


if __name__ == "__main__":
    train()
