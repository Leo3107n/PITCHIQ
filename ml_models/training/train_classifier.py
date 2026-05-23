"""
PitchIQ - Master ML Training Pipeline
========================================
Runs the full pipeline end-to-end on the real male_players.csv dataset:
  1. Clean male_players.csv -> cleaned_players.csv
  2. Normalize -> normalized_players.csv + scaler.pkl
  3. Encode labels -> encoded_dataset.csv + label_encoder.pkl
  4. Train 5 classifiers (KNN, DT, RF, SVM, MLP)
  5. Train KMeans clustering
  6. Evaluate all models and pick the best
  7. Save best_classifier.pkl + model_comparison report

Usage (from project root):
    python ml_models/training/train_classifier.py
"""
import os
import sys
import shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT)

DIVIDER = "=" * 60


def section(title):
    print(f"\n{DIVIDER}")
    print(f"  {title}")
    print(DIVIDER)


def run():
    # ── 1. Clean real dataset ─────────────────────────────────────────
    section("STEP 1 - Clean male_players.csv")
    raw_csv = os.path.join(ROOT, "dataset", "raw", "male_players.csv")
    if not os.path.exists(raw_csv):
        print(f"ERROR: {raw_csv} not found.")
        print("Please place male_players.csv in dataset/raw/ and re-run.")
        sys.exit(1)

    from ml_models.preprocessing.clean_data import clean
    clean()

    # ── 2. Normalize ──────────────────────────────────────────────────
    section("STEP 2 - Normalize")
    from ml_models.preprocessing.normalize_data import normalize
    normalize()

    # ── 3. Encode labels ──────────────────────────────────────────────
    section("STEP 3 - Encode Labels")
    from ml_models.preprocessing.label_encoding import encode
    _, le = encode()
    print(f"  Positions: {list(le.classes_)}")

    # ── 4. Train classifiers ──────────────────────────────────────────
    section("STEP 4 - Train Classifiers")
    from ml_models.classification.knn_classifier   import train as train_knn
    from ml_models.classification.decision_tree    import train as train_dt
    from ml_models.classification.random_forest    import train as train_rf
    from ml_models.classification.svm_classifier   import train as train_svm
    from ml_models.classification.neural_network   import train as train_nn
    from ml_models.classification.gradient_boosting import train as train_gb

    print("\n[1/6] K-Nearest Neighbours")
    _, knn_acc = train_knn()
    print("\n[2/6] Decision Tree")
    _, dt_acc = train_dt()
    print("\n[3/6] Random Forest")
    _, rf_acc = train_rf()
    print("\n[4/6] Support Vector Machine")
    _, svm_acc = train_svm()
    print("\n[5/6] Neural Network (MLP)")
    _, nn_acc = train_nn()
    print("\n[6/6] Gradient Boosting")
    _, gb_acc = train_gb()

    # ── 5. Train KMeans ───────────────────────────────────────────────
    section("STEP 5 - KMeans Clustering")
    from ml_models.clustering.kmeans_clustering import train as train_km
    train_km()

    # ── 6. Evaluate ───────────────────────────────────────────────────
    section("STEP 6 - Model Evaluation")
    from ml_models.evaluation.model_comparison import compare_all
    results = compare_all()

    # Save metrics as JSON for instant API serving (no re-computation on requests)
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
            api_models[key] = {k: v for k, v in m.items() if k != "report"}

        valid    = {k: v for k, v in api_models.items() if "f1" in v}
        best_key = max(valid, key=lambda k: valid[k]["f1"]) if valid else None
        metrics_json = {"models": api_models, "best_model": best_key}

        os.makedirs(os.path.join(ROOT, "reports"), exist_ok=True)
        json_path = os.path.join(ROOT, "reports", "metrics.json")
        with open(json_path, "w") as f:
            json.dump(metrics_json, f, indent=2)
        print(f"  Metrics JSON saved -> {json_path}")

    # ── 7. Save best ──────────────────────────────────────────────────
    section("STEP 7 - Save Best Classifier")
    src_map = {
        "KNN":               "knn_model.pkl",
        "Decision Tree":     "decision_tree.pkl",
        "Random Forest":     "random_forest.pkl",
        "SVM":               "svm_model.pkl",
        "Neural Network":    "neural_network.pkl",
        "Gradient Boosting": "gradient_boosting.pkl",
    }
    if results:
        best_name = max(results, key=lambda k: results[k]["f1"])
        src  = os.path.join(ROOT, "saved_models", src_map[best_name])
        dest = os.path.join(ROOT, "saved_models", "best_classifier.pkl")
        shutil.copy(src, dest)
        print(f"  Best: {best_name}  "
              f"(Accuracy={results[best_name]['accuracy']:.4f}, "
              f"F1={results[best_name]['f1']:.4f})")
        print(f"  Saved -> best_classifier.pkl")

    print(f"\n{DIVIDER}")
    print("  PitchIQ ML Pipeline Complete")
    print(DIVIDER)


if __name__ == "__main__":
    run()
