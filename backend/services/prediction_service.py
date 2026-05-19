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

# Position ideal attribute profiles — derived from real male_players.csv (75th percentile per position)
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

def predict_positions(player_attrs: dict, top_n: int = 5) -> list:
    """
    Returns list of {position, confidence} sorted descending.
    """
    _load()
    vec = pd.DataFrame([[player_attrs.get(c, 50) for c in FEATURE_COLS]], columns=FEATURE_COLS)
    vec_scaled = _scaler.transform(vec)
    proba = _clf.predict_proba(vec_scaled)[0]
    classes = _le.classes_
    ranked = sorted(zip(classes, proba), key=lambda x: x[1], reverse=True)[:top_n]
    return [{"position": pos, "confidence": round(float(conf) * 100, 1)} for pos, conf in ranked]

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
