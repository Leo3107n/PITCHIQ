"""
Analytics Controller
Handles business logic for the analytics overview endpoint.
"""
import sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT)

from backend.services.prediction_service import (
    predict_positions, gap_analysis, POSITION_PROFILES
)
from backend.services.clustering_service import get_similar_players


def handle_overview(attrs: dict) -> dict:
    predictions = predict_positions(attrs, top_n=5)
    top_pos     = predictions[0]["position"]
    gap         = gap_analysis(attrs, top_pos)
    similar     = get_similar_players(attrs, top_n=5)
    overall     = round(sum(attrs.values()) / len(attrs))

    return {
        "overall_rating":  overall,
        "attributes":      attrs,
        "top_position":    top_pos,
        "predictions":     predictions,
        "gap_analysis":    gap,
        "similar_players": similar,
    }


def handle_position_profiles() -> dict:
    return {"profiles": POSITION_PROFILES}
