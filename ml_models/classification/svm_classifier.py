"""
Support Vector Machine classifier for position prediction.
Uses 12 features: 10 attributes + preferred_foot_encoded + height_cm_norm.
Tuned: C=50 (higher margin penalty), RBF kernel.
"""
import pandas as pd
import joblib
import os
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

ENCODED_PATH = os.path.join(os.path.dirname(__file__), "../../dataset/processed/encoded_dataset.csv")
SCALER_PATH  = os.path.join(os.path.dirname(__file__), "../../saved_models/scaler.pkl")
MODEL_PATH   = os.path.join(os.path.dirname(__file__), "../../saved_models/svm_model.pkl")

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

    # SMOTE to balance minority classes
    try:
        from imblearn.over_sampling import SMOTE
        smote = SMOTE(random_state=42, k_neighbors=5)
        X_train, y_train = smote.fit_resample(X_train, y_train)
        print(f"  SMOTE applied: {len(y_train):,} training samples after resampling")
    except ImportError:
        print("  imbalanced-learn not installed — skipping SMOTE")

    # C=50 gives tighter margin → better separation on this dataset
    clf = SVC(
        kernel="rbf",
        C=50,
        gamma="scale",
        probability=True,
        random_state=42,
        class_weight="balanced",   # handles remaining imbalance after SMOTE
    )
    clf.fit(X_train, y_train)

    acc = accuracy_score(y_test, clf.predict(X_test))
    print(f"SVM accuracy: {acc:.4f}")

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(clf, MODEL_PATH)
    print(f"Model saved -> {MODEL_PATH}")
    return clf, acc


if __name__ == "__main__":
    train()
