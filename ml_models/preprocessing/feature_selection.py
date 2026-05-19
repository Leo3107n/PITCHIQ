"""
Utility: returns the canonical feature column list used across all models.
"""
FEATURE_COLS = [
    "pace", "shooting", "passing", "dribbling", "defending",
    "physical", "stamina", "strength", "agility", "vision"
]

def get_features():
    return FEATURE_COLS
