"""
Prints a full sklearn classification report for any saved model.
"""
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT)

from ml_models.evaluation.accuracy_metrics import evaluate_model

def print_report(model_path: str):
    result = evaluate_model(model_path)
    print(f"Accuracy : {result['accuracy']}")
    print(f"F1 Score : {result['f1']}")
    print("\nDetailed Classification Report:")
    print(result["report"])

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else \
        os.path.join(ROOT, "saved_models/best_classifier.pkl")
    print_report(path)
