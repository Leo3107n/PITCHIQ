"""
Standalone script to retrain only the KMeans clustering model.
"""
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT)

from ml_models.clustering.kmeans_clustering import train

if __name__ == "__main__":
    train()
    print("KMeans clustering model retrained.")
