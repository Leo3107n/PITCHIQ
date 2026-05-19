"""
Tests the evaluation endpoint directly without Flask — isolates the exact error.
Run: python reports/test_eval_api.py
"""
import sys, os, traceback, io

ROOT = r'c:\Users\perao\OneDrive\Desktop\PitchIQ'
sys.path.insert(0, ROOT)

OUT_FILE = os.path.join(ROOT, 'reports', 'eval_test_output.txt')

# Redirect all output to file AND stdout
class Tee:
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush()
    def flush(self):
        for f in self.files:
            f.flush()

os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
log = open(OUT_FILE, 'w', encoding='utf-8')
sys.stdout = Tee(sys.__stdout__, log)
sys.stderr = Tee(sys.__stderr__, log)

print("=" * 60)
print("Testing evaluation pipeline step by step")
print("=" * 60)

# Step 1: Check files exist
print("\n[1] Checking model files...")
import joblib
models_dir = os.path.join(ROOT, 'saved_models')
for fname in ['knn_model.pkl','decision_tree.pkl','random_forest.pkl','svm_model.pkl','neural_network.pkl','best_classifier.pkl']:
    path = os.path.join(models_dir, fname)
    exists = os.path.exists(path)
    size   = os.path.getsize(path) / 1024 if exists else 0
    print(f"  {'OK' if exists else 'MISSING':6s}  {fname}  ({size:.0f} KB)")

# Step 2: Check dataset
print("\n[2] Checking encoded dataset...")
import pandas as pd
enc_path = os.path.join(ROOT, 'dataset', 'processed', 'encoded_dataset.csv')
if os.path.exists(enc_path):
    df = pd.read_csv(enc_path)
    print(f"  OK  encoded_dataset.csv  ({len(df):,} rows)")
    print(f"  Columns: {list(df.columns)}")
    print(f"  position_encoded unique: {sorted(df['position_encoded'].unique())}")
else:
    print("  MISSING  encoded_dataset.csv")

# Step 3: Try evaluate_model directly
print("\n[3] Testing evaluate_model() on KNN...")
try:
    from ml_models.evaluation.accuracy_metrics import evaluate_model
    result = evaluate_model(os.path.join(models_dir, 'knn_model.pkl'))
    print(f"  Accuracy : {result['accuracy']}")
    print(f"  F1       : {result['f1']}")
    print(f"  Precision: {result['precision']}")
    print(f"  Recall   : {result['recall']}")
    print("  OK")
except Exception as e:
    print(f"  ERROR: {e}")
    traceback.print_exc()

# Step 4: Try handle_all_metrics
print("\n[4] Testing handle_all_metrics()...")
try:
    from backend.controllers.evaluation_controller import handle_all_metrics
    result = handle_all_metrics()
    print(f"  best_model: {result.get('best_model')}")
    for name, m in result.get('models', {}).items():
        if 'error' in m:
            print(f"  ERROR in {name}: {m['error']}")
        else:
            print(f"  {name:15s}  acc={m['accuracy']:.4f}  f1={m['f1']:.4f}")
    print("  OK")
except Exception as e:
    print(f"  ERROR: {e}")
    traceback.print_exc()

# Step 5: Try Flask app import
print("\n[5] Testing Flask app creation...")
try:
    from backend.app import create_app
    app = create_app()
    print("  Flask app created OK")

    # Test the endpoint directly via test client
    with app.test_client() as client:
        r = client.get('/api/evaluate/models')
        print(f"  GET /api/evaluate/models -> {r.status_code}")
        if r.status_code == 200:
            data = r.get_json()
            print(f"  best_model: {data.get('best_model')}")
            print(f"  models: {list(data.get('models', {}).keys())}")
        else:
            print(f"  Response: {r.data.decode()[:500]}")
except Exception as e:
    print(f"  ERROR: {e}")
    traceback.print_exc()

print("\n" + "=" * 60)
print("Done")
print("=" * 60)
