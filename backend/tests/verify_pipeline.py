"""
Quick end-to-end verification of the full PitchIQ pipeline.
Run from project root: python backend/tests/verify_pipeline.py
"""
import sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT)

import pandas as pd, joblib

PASS = "[PASS]"
FAIL = "[FAIL]"

errors = []

def check(label, condition, detail=""):
    if condition:
        print(f"  {PASS}  {label}")
    else:
        print(f"  {FAIL}  {label}  {detail}")
        errors.append(label)

print("=" * 60)
print("  PitchIQ Pipeline Verification")
print("=" * 60)

# ── Dataset ───────────────────────────────────────────────────────────────────
print("\n[1] Dataset")
for fname in ["cleaned_players.csv", "normalized_players.csv", "encoded_dataset.csv"]:
    p = os.path.join(ROOT, "dataset", "processed", fname)
    if os.path.exists(p):
        df = pd.read_csv(p)
        check(fname, len(df) > 40000, f"only {len(df)} rows")
    else:
        check(fname, False, "file missing")

# ── Saved models ──────────────────────────────────────────────────────────────
print("\n[2] Saved Models")
for fname in ["best_classifier.pkl","scaler.pkl","label_encoder.pkl","kmeans_model.pkl"]:
    p = os.path.join(ROOT, "saved_models", fname)
    check(fname, os.path.exists(p) and os.path.getsize(p) > 1000)

# ── Label encoder has all 11 positions ────────────────────────────────────────
print("\n[3] Label Encoder")
try:
    le = joblib.load(os.path.join(ROOT, "saved_models", "label_encoder.pkl"))
    check("11 positions encoded", len(le.classes_) == 11, f"got {list(le.classes_)}")
except Exception as e:
    check("label_encoder load", False, str(e))

# ── Prediction service ────────────────────────────────────────────────────────
print("\n[4] Prediction Service")
try:
    from backend.services.prediction_service import predict_positions, gap_analysis, POSITION_PROFILES

    # Striker profile
    striker = {"pace":80,"shooting":85,"passing":65,"dribbling":75,
               "defending":28,"physical":72,"stamina":74,"strength":70,"agility":78,"vision":68}
    preds = predict_positions(striker)
    check("predict_positions returns 5", len(preds) == 5)
    check("confidences sum ~100", abs(sum(p["confidence"] for p in preds) - 100) < 1)
    check("top position is attacking", preds[0]["position"] in ["ST","CF","LW","RW","CAM"])

    # GK profile
    gk = {"pace":55,"shooting":20,"passing":55,"dribbling":35,"defending":60,
          "physical":70,"stamina":60,"strength":72,"agility":50,"vision":50}
    gk_preds = predict_positions(gk)
    check("GK profile predicts GK", gk_preds[0]["position"] == "GK")

    # Gap analysis
    gap = gap_analysis(striker, "ST")
    check("gap_analysis has gaps", len(gap["gaps"]) == 10)
    check("POSITION_PROFILES uses real data", POSITION_PROFILES["ST"]["shooting"] < 80,
          f"shooting={POSITION_PROFILES['ST']['shooting']} (should be real 75th pct ~68)")

except Exception as e:
    check("prediction_service", False, str(e))

# ── Clustering service ────────────────────────────────────────────────────────
print("\n[5] Clustering Service")
try:
    from backend.services.clustering_service import get_similar_players, get_cluster
    attrs = {"pace":80,"shooting":85,"passing":65,"dribbling":75,
             "defending":28,"physical":72,"stamina":74,"strength":70,"agility":78,"vision":68}
    similar = get_similar_players(attrs, top_n=5)
    check("similar_players returns 5", len(similar) == 5)
    check("similarity scores valid", all(0 <= p["similarity"] <= 100 for p in similar))
    check("real player names", any(len(p["name"]) > 2 for p in similar))

    cluster = get_cluster(attrs)
    check("cluster_id valid", 0 <= cluster["cluster_id"] <= 10)
    check("cluster_size > 0", cluster["cluster_size"] > 0)
except Exception as e:
    check("clustering_service", False, str(e))

# ── Recommendation service ────────────────────────────────────────────────────
print("\n[6] Recommendation Service")
try:
    from backend.services.recommendation_service import generate_recommendations
    weaknesses = [
        {"attribute": "pace",     "value": 55, "ideal": 75, "deficit": 20},
        {"attribute": "shooting", "value": 50, "ideal": 68, "deficit": 18},
        {"attribute": "stamina",  "value": 55, "ideal": 69, "deficit": 14},
    ]
    plan = generate_recommendations(weaknesses, "ST")
    check("plan has drills", len(plan["drills"]) > 0)
    check("plan has weekly_plan", len(plan["weekly_plan"]) == 5)
    check("priority_attributes correct", "pace" in plan["priority_attributes"])
except Exception as e:
    check("recommendation_service", False, str(e))

# ── Summary ───────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
if errors:
    print(f"  FAILED: {len(errors)} check(s)")
    for e in errors:
        print(f"    - {e}")
else:
    print("  ALL CHECKS PASSED")
print("=" * 60)
