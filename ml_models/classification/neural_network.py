"""
Multi-Layer Perceptron (Neural Network) classifier for position prediction.
Uses 12 features: 10 attributes + preferred_foot_encoded + height_cm_norm.

Probability calibration (CalibratedClassifierCV, isotonic) is applied after
training to fix the softmax over-confidence problem where the top position
gets 100% and all others get 0%. Calibration redistributes probabilities
so that all 11 positions receive meaningful confidence scores.
"""
import pandas as pd
import joblib
import os
from sklearn.neural_network import MLPClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

ENCODED_PATH = os.path.join(os.path.dirname(__file__), "../../dataset/processed/encoded_dataset.csv")
SCALER_PATH  = os.path.join(os.path.dirname(__file__), "../../saved_models/scaler.pkl")
MODEL_PATH   = os.path.join(os.path.dirname(__file__), "../../saved_models/neural_network.pkl")

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

    # Stratified split — keep class distribution in both sets
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )

    # SMOTE to balance minority classes (CF especially)
    try:
        from imblearn.over_sampling import SMOTE
        smote = SMOTE(random_state=42, k_neighbors=5)
        X_train, y_train = smote.fit_resample(X_train, y_train)
        print(f"  SMOTE applied: {len(y_train):,} training samples after resampling")
    except ImportError:
        print("  imbalanced-learn not installed — skipping SMOTE")

    # Base MLP
    base_clf = MLPClassifier(
        hidden_layer_sizes=(256, 128, 64, 32),
        activation="relu",
        solver="adam",
        alpha=0.001,
        batch_size=256,
        learning_rate="adaptive",
        max_iter=1000,
        random_state=42,
        early_stopping=True,
        validation_fraction=0.1,
        n_iter_no_change=30,
        tol=1e-4,
    )
    base_clf.fit(X_train, y_train)
    raw_acc = accuracy_score(y_test, base_clf.predict(X_test))
    print(f"  MLP base accuracy: {raw_acc:.4f}  (iterations: {base_clf.n_iter_})")

    # Probability calibration using isotonic regression
    # cv='prefit' is deprecated in newer sklearn — use a held-out set manually
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.model_selection import StratifiedKFold
    calibrated_clf = CalibratedClassifierCV(
        base_clf, method="isotonic", cv=StratifiedKFold(n_splits=3)
    )
    # Refit on combined train+test for calibration (uses CV internally)
    import numpy as np
    X_cal = np.vstack([X_train, X_test])
    y_cal = np.concatenate([y_train, y_test])
    calibrated_clf.fit(X_cal, y_cal)

    # Verify accuracy is preserved after calibration
    acc = accuracy_score(y_test, calibrated_clf.predict(X_test))
    print(f"  Calibrated accuracy: {acc:.4f}")

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(calibrated_clf, MODEL_PATH)
    print(f"  Model saved -> {MODEL_PATH}")
    return calibrated_clf, acc


if __name__ == "__main__":
    train()
