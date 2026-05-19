"""
Clustering Controller
Handles business logic for player similarity and cluster analysis.
"""
from backend.services.clustering_service import get_similar_players, get_cluster


def handle_similar_players(attrs: dict, top_n: int = 5) -> dict:
    players = get_similar_players(attrs, top_n=top_n)
    return {"similar_players": players}


def handle_cluster_info(attrs: dict) -> dict:
    return get_cluster(attrs)
