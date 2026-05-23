"""
Canonical feature column list used across all ML models.

Fix 1: Added preferred_foot_encoded (Right=1, Left=0) and height_cm_norm
       These two features resolve the LB/RB and LW/RW confusion that
       capped accuracy at ~66%.
"""

# 10 original attributes + 2 new structural features
FEATURE_COLS = [
    "pace", "shooting", "passing", "dribbling", "defending",
    "physical", "stamina", "strength", "agility", "vision",
    "preferred_foot_encoded",   # Fix 1: Right=1, Left=0
    "height_cm_norm",           # Fix 1: height_cm / 100 (keeps scale ~1.6-2.0)
]


def get_features():
    return FEATURE_COLS
