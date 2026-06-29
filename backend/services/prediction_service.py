"""
Loads the best classifier and returns top-N position predictions with confidence scores.
"""
import numpy as np
import pandas as pd
import joblib
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT)

from backend.config import Config

FEATURE_COLS = ["pace","shooting","passing","dribbling","defending",
                "physical","stamina","strength","agility","vision"]

SCALER_COLS     = FEATURE_COLS + ["preferred_foot_encoded", "height_cm_norm"]
_FOOT_DEFAULT   = 1.0
_HEIGHT_DEFAULT = 1.80

# Position ideal attribute profiles — derived from real male_players.csv (75th percentile)
POSITION_PROFILES = {
    "GK":  {"pace":55,"shooting":64,"passing":64,"dribbling":44,"defending":67,"physical":67,"stamina":35,"strength":67,"agility":44,"vision":44},
    "CB":  {"pace":65,"shooting":41,"passing":53,"dribbling":55,"defending":69,"physical":75,"stamina":69,"strength":81,"agility":60,"vision":49},
    "LB":  {"pace":76,"shooting":52,"passing":62,"dribbling":66,"defending":64,"physical":70,"stamina":75,"strength":70,"agility":74,"vision":58},
    "RB":  {"pace":76,"shooting":51,"passing":61,"dribbling":65,"defending":65,"physical":70,"stamina":76,"strength":70,"agility":73,"vision":58},
    "CDM": {"pace":67,"shooting":57,"passing":64,"dribbling":66,"defending":67,"physical":74,"stamina":77,"strength":75,"agility":70,"vision":65},
    "CM":  {"pace":69,"shooting":61,"passing":67,"dribbling":68,"defending":61,"physical":69,"stamina":75,"strength":69,"agility":73,"vision":68},
    "CAM": {"pace":73,"shooting":65,"passing":68,"dribbling":71,"defending":47,"physical":62,"stamina":69,"strength":64,"agility":78,"vision":70},
    "LW":  {"pace":80,"shooting":64,"passing":64,"dribbling":71,"defending":44,"physical":63,"stamina":70,"strength":64,"agility":80,"vision":65},
    "RW":  {"pace":81,"shooting":64,"passing":64,"dribbling":70,"defending":44,"physical":63,"stamina":71,"strength":64,"agility":80,"vision":64},
    "ST":  {"pace":75,"shooting":68,"passing":57,"dribbling":67,"defending":34,"physical":70,"stamina":69,"strength":77,"agility":72,"vision":60},
    "CF":  {"pace":79,"shooting":68,"passing":66,"dribbling":73,"defending":40,"physical":64,"stamina":71,"strength":67,"agility":82,"vision":69},
}

_clf    = None
_scaler = None
_le     = None


def _load():
    global _clf, _scaler, _le
    if _clf is None:
        _clf    = joblib.load(os.path.join(Config.MODELS_DIR, "best_classifier.pkl"))
        _scaler = joblib.load(os.path.join(Config.MODELS_DIR, "scaler.pkl"))
        _le     = joblib.load(os.path.join(Config.MODELS_DIR, "label_encoder.pkl"))


def _profile_similarity_scores(player_attrs: dict) -> dict:
    """
    Compute a cosine-similarity score between the player's attributes and each
    position's ideal profile. Returns a dict {position: score} normalised to sum=1.
    These scores spread probability mass across plausible positions.
    """
    player_vec = np.array([player_attrs.get(c, 50) for c in FEATURE_COLS], dtype=float)
    scores = {}
    for pos, profile in POSITION_PROFILES.items():
        ideal_vec = np.array([profile[c] for c in FEATURE_COLS], dtype=float)
        dot   = np.dot(player_vec, ideal_vec)
        norm  = np.linalg.norm(player_vec) * np.linalg.norm(ideal_vec)
        scores[pos] = float(dot / norm) if norm > 0 else 0.0
    # Shift to positive and normalise
    vals = np.array(list(scores.values()))
    vals = vals - vals.min() + 1e-6
    vals = vals / vals.sum()
    return dict(zip(scores.keys(), vals))


def predict_positions(player_attrs: dict, top_n: int = 5) -> list:
    """
    Returns list of {position, confidence} sorted descending.

    Strategy:
    1. Get raw predict_proba from the classifier.
    2. If the top probability > 85% (overconfident), blend with profile-similarity
       scores (70% classifier + 30% similarity). This redistributes confidence
       to similar positions instead of collapsing everything to 0%.
    3. Always normalise to sum = 100%.
    """
    _load()
    row        = [player_attrs.get(c, 50) for c in FEATURE_COLS] + [_FOOT_DEFAULT, _HEIGHT_DEFAULT]
    vec        = pd.DataFrame([row], columns=SCALER_COLS)
    vec_scaled = _scaler.transform(vec)
    clf_proba  = _clf.predict_proba(vec_scaled)[0]
    classes    = list(_le.classes_)

    # Build a dict {position: clf_probability}
    clf_dict = {pos: float(p) for pos, p in zip(classes, clf_proba)}

    # If model is over-confident, blend with profile similarity
    top_prob = max(clf_dict.values())
    if top_prob > 0.85:
        sim_scores = _profile_similarity_scores(player_attrs)

        # Blend: 70% classifier, 30% profile similarity
        alpha = 0.70
        blended = {}
        for pos in POSITION_PROFILES:
            blended[pos] = alpha * clf_dict.get(pos, 0.0) + (1 - alpha) * sim_scores.get(pos, 0.0)

        # Re-normalise to sum = 1
        total = sum(blended.values())
        proba_dict = {pos: v / total for pos, v in blended.items()}
    else:
        proba_dict = clf_dict

    # Sort and take top_n, then re-normalise the subset to sum to 100%
    ranked = sorted(proba_dict.items(), key=lambda x: x[1], reverse=True)[:top_n]
    subset_total = sum(conf for _, conf in ranked)
    if subset_total > 0:
        ranked = [(pos, conf / subset_total) for pos, conf in ranked]
    return [{"position": pos, "confidence": round(conf * 100, 1)} for pos, conf in ranked]


def gap_analysis(player_attrs: dict, position: str) -> dict:
    """
    Compares player attributes against the ideal profile for a position.
    Returns strengths, weaknesses, and per-attribute gaps.
    """
    profile = POSITION_PROFILES.get(position, {})
    gaps = {}
    strengths = []
    weaknesses = []
    for attr, ideal in profile.items():
        player_val = player_attrs.get(attr, 50)
        diff = player_val - ideal
        gaps[attr] = {"player": player_val, "ideal": ideal, "gap": diff}
        if diff >= 3:
            strengths.append({"attribute": attr, "value": player_val, "ideal": ideal, "surplus": diff})
        elif diff <= -5:
            weaknesses.append({"attribute": attr, "value": player_val, "ideal": ideal, "deficit": abs(diff)})
    weaknesses.sort(key=lambda x: x["deficit"], reverse=True)
    strengths.sort(key=lambda x: x["surplus"], reverse=True)
    return {"position": position, "gaps": gaps, "strengths": strengths, "weaknesses": weaknesses}
