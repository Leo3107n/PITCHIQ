"""
Compares all trained classifiers side-by-side and identifies the best one.
Saves a comparison report to reports/model_comparison.txt
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT)

from ml_models.evaluation.accuracy_metrics import evaluate_model

MODELS = {
    "KNN":            "saved_models/knn_model.pkl",
    "Decision Tree":  "saved_models/decision_tree.pkl",
    "Random Forest":  "saved_models/random_forest.pkl",
    "SVM":            "saved_models/svm_model.pkl",
    "Neural Network": "saved_models/neural_network.pkl",
}

REPORT_PATH = os.path.join(ROOT, "reports", "model_comparison.txt")


def compare_all() -> dict:
    results = {}
    print(f"\n{'Model':<20} {'Accuracy':>10} {'Precision':>10} {'Recall':>10} {'F1':>10}")
    print("-" * 62)

    for name, rel_path in MODELS.items():
        full_path = os.path.join(ROOT, rel_path)
        if not os.path.exists(full_path):
            print(f"{name:<20} {'(not trained)':>10}")
            continue
        try:
            m = evaluate_model(full_path)
            results[name] = m
            print(f"{name:<20} {m['accuracy']:>10.4f} {m['precision']:>10.4f} "
                  f"{m['recall']:>10.4f} {m['f1']:>10.4f}")
        except Exception as e:
            print(f"{name:<20} ERROR: {e}")

    if not results:
        return {}

    best_name = max(results, key=lambda k: results[k]["f1"])
    best      = results[best_name]
    print(f"\nBest model: {best_name}  (F1={best['f1']:.4f}, Accuracy={best['accuracy']:.4f})")

    # Write report
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w") as f:
        f.write("PitchIQ — Model Comparison Report\n")
        f.write("=" * 62 + "\n\n")
        f.write(f"{'Model':<20} {'Accuracy':>10} {'Precision':>10} {'Recall':>10} {'F1':>10}\n")
        f.write("-" * 62 + "\n")
        for name, m in results.items():
            f.write(f"{name:<20} {m['accuracy']:>10.4f} {m['precision']:>10.4f} "
                    f"{m['recall']:>10.4f} {m['f1']:>10.4f}\n")
        f.write(f"\nBest: {best_name}  (F1={best['f1']:.4f})\n\n")
        f.write("Per-class report for best model:\n")
        f.write(best["report"])

    print(f"Report saved -> {REPORT_PATH}")
    return results


if __name__ == "__main__":
    compare_all()
