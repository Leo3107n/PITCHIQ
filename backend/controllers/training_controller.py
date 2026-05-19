"""
Training Controller
Handles business logic for training plan generation.
"""
from backend.services.prediction_service import predict_positions, gap_analysis
from backend.services.recommendation_service import generate_recommendations


def handle_training_plan(attrs: dict, position: str = None) -> dict:
    """
    Generates a personalised training plan.
    If position is not provided, uses the top predicted position.
    """
    if not position:
        preds    = predict_positions(attrs, top_n=1)
        position = preds[0]["position"]

    gap  = gap_analysis(attrs, position)
    plan = generate_recommendations(gap["weaknesses"], position)

    return {
        "gap_analysis":  gap,
        "training_plan": plan,
    }
