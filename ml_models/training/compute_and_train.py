"""
PitchIQ - Full Retraining Script
===================================
Computes real position profiles from cleaned_players.csv,
then retrains all models on the real 51,878-player dataset.

Usage (from project root):
    python ml_models/training/compute_and_train.py
"""
import sys, os, shutil
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT)

import pandas as pd
import numpy as np

CLEANED      = os.path.join(ROOT, 'dataset', 'processed', 'cleaned_players.csv')
FEATURE_COLS = ["pace","shooting","passing","dribbling","defending",
                "physical","stamina","strength","agility","vision"]
DIVIDER      = "=" * 60

# ── Step 1: Compute real position profiles ────────────────────────────────────
print(DIVIDER)
print("  STEP 1 - Compute Position Profiles")
print(DIVIDER)
df = pd.read_csv(CLEANED)
profiles = {}
for pos in sorted(df['position'].unique()):
    sub = df[df['position'] == pos]
    profiles[pos] = {col: int(round(sub[col].quantile(0.75))) for col in FEATURE_COLS}

os.makedirs(os.path.join(ROOT, 'reports'), exist_ok=True)
with open(os.path.join(ROOT, 'reports', 'position_profiles.txt'), 'w') as f:
    f.write("Real FIFA Position Profiles (75th percentile)\n")
    f.write(DIVIDER + "\n\n")
    for pos, attrs in profiles.items():
        f.write(f"{pos}: {attrs}\n")

for pos, attrs in profiles.items():
    vals = ", ".join(f'"{k}":{v}' for k, v in attrs.items())
    print(f'  "{pos}": {{{vals}}}')
print("  Saved -> reports/position_profiles.txt")

# ── Step 2: Normalize ─────────────────────────────────────────────────────────
print(f"\n{DIVIDER}")
print("  STEP 2 - Normalize")
print(DIVIDER)
from ml_models.preprocessing.normalize_data import normalize
normalize()

# ── Step 3: Encode ────────────────────────────────────────────────────────────
print(f"\n{DIVIDER}")
print("  STEP 3 - Encode Labels")
print(DIVIDER)
from ml_models.preprocessing.label_encoding import encode
_, le = encode()
print(f"  Positions: {list(le.classes_)}")

# ── Step 4: Train classifiers ─────────────────────────────────────────────────
print(f"\n{DIVIDER}")
print("  STEP 4 - Train Classifiers")
print(DIVIDER)
from ml_models.classification.knn_classifier import train as train_knn
from ml_models.classification.decision_tree  import train as train_dt
from ml_models.classification.random_forest  import train as train_rf
from ml_models.classification.svm_classifier import train as train_svm
from ml_models.classification.neural_network import train as train_nn

print("\n[1/5] KNN");           _, knn_acc = train_knn()
print("\n[2/5] Decision Tree"); _, dt_acc  = train_dt()
print("\n[3/5] Random Forest"); _, rf_acc  = train_rf()
print("\n[4/5] SVM");           _, svm_acc = train_svm()
print("\n[5/5] Neural Network");_, nn_acc  = train_nn()

# ── Step 5: KMeans ────────────────────────────────────────────────────────────
print(f"\n{DIVIDER}")
print("  STEP 5 - KMeans Clustering")
print(DIVIDER)
from ml_models.clustering.kmeans_clustering import train as train_km
train_km()

# ── Step 6: Evaluate ──────────────────────────────────────────────────────────
print(f"\n{DIVIDER}")
print("  STEP 6 - Evaluate All Models")
print(DIVIDER)
from ml_models.evaluation.model_comparison import compare_all
results = compare_all()

# ── Step 6b: Save metrics as JSON for instant API serving ─────────────────────
import json
if results:
    key_map = {
        "KNN":            "knn",
        "Decision Tree":  "decision_tree",
        "Random Forest":  "random_forest",
        "SVM":            "svm",
        "Neural Network": "neural_network",
    }
    api_models = {}
    for display_name, m in results.items():
        key = key_map.get(display_name, display_name.lower().replace(" ", "_"))
        m_copy = {k: v for k, v in m.items() if k != "report"}
        api_models[key] = m_copy

    valid    = {k: v for k, v in api_models.items() if "f1" in v}
    best_key = max(valid, key=lambda k: valid[k]["f1"]) if valid else None

    metrics_json = {"models": api_models, "best_model": best_key}
    json_path = os.path.join(ROOT, "reports", "metrics.json")
    with open(json_path, "w") as f:
        json.dump(metrics_json, f, indent=2)
    print(f"  Metrics JSON saved -> {json_path}")

# ── Step 7: Save best ─────────────────────────────────────────────────────────
print(f"\n{DIVIDER}")
print("  STEP 7 - Save Best Classifier")
print(DIVIDER)
src_map = {
    "KNN":            "knn_model.pkl",
    "Decision Tree":  "decision_tree.pkl",
    "Random Forest":  "random_forest.pkl",
    "SVM":            "svm_model.pkl",
    "Neural Network": "neural_network.pkl",
}
if results:
    best_name = max(results, key=lambda k: results[k]["f1"])
    src  = os.path.join(ROOT, "saved_models", src_map[best_name])
    dest = os.path.join(ROOT, "saved_models", "best_classifier.pkl")
    shutil.copy(src, dest)
    print(f"  Best: {best_name}  "
          f"(Accuracy={results[best_name]['accuracy']:.4f}, "
          f"F1={results[best_name]['f1']:.4f})")
    print("  Saved -> best_classifier.pkl")

print(f"\n{DIVIDER}")
print("  TRAINING COMPLETE")
print(DIVIDER)
