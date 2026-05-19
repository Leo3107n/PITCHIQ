"""
Prediction Controller
Handles all business logic for position prediction and gap analysis.
Routes call these functions; they never touch request/response objects.
"""
from backend.services.prediction_service import predict_positions, gap_analysis
from backend.services.clustering_service import get_similar_players, get_cluster
from backend.services.recommendation_service import generate_recommendations
from backend.database.db import save_session


def handle_predict(attrs: dict, top_n: int = 5) -> dict:
    """
    Runs position prediction and returns ranked results.
    """
    predictions = predict_positions(attrs, top_n=top_n)
    return {"predictions": predictions}


def handle_gap_analysis(attrs: dict, position: str) -> dict:
    """
    Runs gap analysis for a specific position.
    """
    return gap_analysis(attrs, position)


def handle_full_analysis(attrs: dict, player_name: str = "",
                         player_age: int = 0, save: bool = True) -> dict:
    """
    Runs the complete analysis pipeline:
      predictions → gap analysis → similar players → cluster → training plan
    Optionally persists the session to the database.
    Returns a unified response dict.
    """
    # 1. Predict positions
    predictions = predict_positions(attrs, top_n=5)
    top_pos = predictions[0]["position"]

    # 2. Gap analysis for top position
    gap = gap_analysis(attrs, top_pos)

    # 3. Similar players
    similar = get_similar_players(attrs, top_n=5)

    # 4. Cluster info
    cluster = get_cluster(attrs)

    # 5. Training plan
    plan = generate_recommendations(gap["weaknesses"], top_pos)

    # 6. Overall rating
    overall = round(sum(attrs.values()) / len(attrs))

    result = {
        "overall_rating": overall,
        "attributes":     attrs,
        "top_position":   top_pos,
        "predictions":    predictions,
        "gap_analysis":   gap,
        "similar_players": similar,
        "cluster_info":   cluster,
        "training_plan":  plan,
    }

    # 7. Persist session
    if save:
        token = save_session(
            player_name=player_name,
            player_age=player_age,
            attrs=attrs,
            predictions=predictions,
            gap=gap,
            plan=plan,
            cluster=cluster,
        )
        result["session_token"] = token

    return result
