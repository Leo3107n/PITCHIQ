"""
Grid-search hyperparameter tuning for the Random Forest classifier.
Saves the best tuned model as saved_models/random_forest_tuned.pkl
"""
import os, sys
import pandas as pd
import joblib

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT)

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.metrics import accuracy_score

ENCODED_PATH = os.path.join(ROOT, "dataset/processed/encoded_dataset.csv")
SCALER_PATH  = os.path.join(ROOT, "saved_models/scaler.pkl")
MODEL_PATH   = os.path.join(ROOT, "saved_models/random_forest_tuned.pkl")

FEATURE_COLS = ["pace","shooting","passing","dribbling","defending",
                "physical","stamina","strength","agility","vision"]

PARAM_GRID = {
    "n_estimators": [100, 200, 300],
    "max_depth":    [None, 20, 30],
    "min_samples_split": [2, 5],
}


def tune():
    df     = pd.read_csv(ENCODED_PATH)
    scaler = joblib.load(SCALER_PATH)
    X      = scaler.transform(df[FEATURE_COLS])
    y      = df["position_encoded"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print("Running GridSearchCV (this may take a few minutes)...")
    gs = GridSearchCV(
        RandomForestClassifier(random_state=42, n_jobs=-1),
        PARAM_GRID,
        cv=5,
        scoring="f1_weighted",
        n_jobs=-1,
        verbose=1,
    )
    gs.fit(X_train, y_train)

    best = gs.best_estimator_
    acc  = accuracy_score(y_test, best.predict(X_test))
    print(f"\nBest params : {gs.best_params_}")
    print(f"CV F1 score : {gs.best_score_:.4f}")
    print(f"Test accuracy: {acc:.4f}")

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(best, MODEL_PATH)
    print(f"Tuned model saved -> {MODEL_PATH}")
    return best, acc


if __name__ == "__main__":
    tune()
