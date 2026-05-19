import sys, os
ROOT = r'c:\Users\perao\OneDrive\Desktop\PitchIQ'
sys.path.insert(0, ROOT)

import joblib, pandas as pd

# Check label encoder
le = joblib.load(os.path.join(ROOT, 'saved_models', 'label_encoder.pkl'))
print(f"Label encoder classes: {list(le.classes_)}")
print(f"Label encoder size: {os.path.getsize(os.path.join(ROOT, 'saved_models', 'label_encoder.pkl'))} bytes")

# Check best classifier
clf = joblib.load(os.path.join(ROOT, 'saved_models', 'best_classifier.pkl'))
print(f"Best classifier type: {type(clf).__name__}")
print(f"Best classifier size: {os.path.getsize(os.path.join(ROOT, 'saved_models', 'best_classifier.pkl')) / 1024 / 1024:.1f} MB")

# Test prediction
from backend.services.prediction_service import predict_positions, gap_analysis, POSITION_PROFILES

striker = {"pace":80,"shooting":85,"passing":65,"dribbling":75,
           "defending":28,"physical":72,"stamina":74,"strength":70,"agility":78,"vision":68}
preds = predict_positions(striker)
print(f"\nStriker prediction: {[(p['position'], p['confidence']) for p in preds]}")

gk = {"pace":55,"shooting":20,"passing":55,"dribbling":35,"defending":60,
      "physical":70,"stamina":60,"strength":72,"agility":50,"vision":50}
gk_preds = predict_positions(gk)
print(f"GK prediction: {[(p['position'], p['confidence']) for p in gk_preds]}")

gap = gap_analysis(striker, "ST")
print(f"\nGap analysis (ST): strengths={[s['attribute'] for s in gap['strengths']]}")
print(f"Gap analysis (ST): weaknesses={[w['attribute'] for w in gap['weaknesses']]}")

print(f"\nST profile (real data): {POSITION_PROFILES['ST']}")
print(f"GK profile (real data): {POSITION_PROFILES['GK']}")

# Test clustering
from backend.services.clustering_service import get_similar_players, get_cluster
similar = get_similar_players(striker, top_n=5)
print(f"\nSimilar players: {[(p['name'], p['position'], p['similarity']) for p in similar]}")

cluster = get_cluster(striker)
print(f"Cluster: id={cluster['cluster_id']}, size={cluster['cluster_size']}, dominant={cluster['dominant_positions']}")

# Test recommendation
from backend.services.recommendation_service import generate_recommendations
weaknesses = [{"attribute":"pace","value":55,"ideal":75,"deficit":20},
              {"attribute":"shooting","value":50,"ideal":68,"deficit":18}]
plan = generate_recommendations(weaknesses, "ST")
print(f"\nTraining plan drills: {len(plan['drills'])}")
print(f"Weekly plan days: {len(plan['weekly_plan'])}")

print("\nALL CHECKS PASSED")
