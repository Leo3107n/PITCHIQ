"""
Wraps the ML clustering layer for use by Flask routes.
"""
import sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT)

from ml_models.clustering.similarity_engine import find_similar
from ml_models.clustering.cluster_analysis  import get_cluster_info

def get_similar_players(player_attrs: dict, top_n: int = 5) -> list:
    return find_similar(player_attrs, top_n=top_n)

def get_cluster(player_attrs: dict) -> dict:
    return get_cluster_info(player_attrs)
