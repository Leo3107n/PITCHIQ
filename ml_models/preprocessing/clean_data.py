"""
PitchIQ - Data Cleaning Pipeline
===================================
Reads male_players.csv and produces cleaned_players.csv with 12 features.

Features:
  10 core attributes: pace, shooting, passing, dribbling, defending,
                      physical, stamina, strength, agility, vision
  2 extra features:   preferred_foot_encoded (Right=1, Left=0)
                      height_cm_norm (height / 100)

Position rule: PRIMARY position only (first listed in player_positions).
Multi-label expansion was removed — it creates identical feature vectors
with different labels, which confuses classifiers and drops accuracy.
"""

import pandas as pd
import numpy as np
import os

RAW_PATH = os.path.join(os.path.dirname(__file__), "../../dataset/raw/male_players.csv")
OUT_PATH = os.path.join(os.path.dirname(__file__), "../../dataset/processed/cleaned_players.csv")

POSITION_MAP = {
    "GK":  "GK",
    "CB":  "CB",  "LCB": "CB",  "RCB": "CB",
    "LB":  "LB",  "LWB": "LB",
    "RB":  "RB",  "RWB": "RB",
    "CDM": "CDM", "LDM": "CDM", "RDM": "CDM",
    "CM":  "CM",  "LCM": "CM",  "RCM": "CM",
    "CAM": "CAM", "LAM": "CAM", "RAM": "CAM",
    "LW":  "LW",  "LM":  "LW",  "LF":  "LW",
    "RW":  "RW",  "RM":  "RW",  "RF":  "RW",
    "ST":  "ST",  "LS":  "ST",  "RS":  "ST",
    "CF":  "CF",
}

ATTR_COLS    = ["pace","shooting","passing","dribbling","defending",
                "physical","stamina","strength","agility","vision"]
FEATURE_COLS = ATTR_COLS + ["preferred_foot_encoded", "height_cm_norm"]


def extract_primary_position(pos_str: str) -> str | None:
    """Returns the first valid canonical position from a comma-separated string."""
    if not isinstance(pos_str, str):
        return None
    for token in pos_str.split(","):
        mapped = POSITION_MAP.get(token.strip().upper())
        if mapped:
            return mapped
    return None


def clean():
    print("Reading male_players.csv ...")
    df = pd.read_csv(RAW_PATH, low_memory=False)
    print(f"  Raw rows: {len(df):,}  columns: {len(df.columns)}")

    # ── 1. Keep latest FIFA version per player ────────────────────────────────
    df = df.sort_values("fifa_version", ascending=False)
    df = df.drop_duplicates(subset="player_id", keep="first").copy()
    print(f"  After dedup (latest version per player): {len(df):,}")

    # ── 2. Extract PRIMARY position only ─────────────────────────────────────
    df["position"] = df["player_positions"].apply(extract_primary_position)
    df = df[df["position"].notna()].copy()
    print(f"  After position filter: {len(df):,}")

    is_gk = df["position"] == "GK"

    # ── 3. Build canonical attributes (vectorised) ────────────────────────────
    gk_pace = (df["goalkeeping_speed"].fillna(0) * 0.5 +
               df["goalkeeping_reflexes"].fillna(0) * 0.5)
    df["pace_clean"] = np.where(is_gk, gk_pace, df["pace"])

    gk_shoot = (df["goalkeeping_kicking"].fillna(0) * 0.6 +
                df["goalkeeping_handling"].fillna(0) * 0.4)
    df["shooting_clean"]  = np.where(is_gk, gk_shoot, df["shooting"])
    df["passing_clean"]   = np.where(is_gk, df["goalkeeping_kicking"].fillna(0), df["passing"])
    df["dribbling_clean"] = np.where(is_gk, df["movement_agility"].fillna(0), df["dribbling"])

    gk_def = (df["goalkeeping_positioning"].fillna(0) * 0.4 +
              df["goalkeeping_reflexes"].fillna(0) * 0.4 +
              df["goalkeeping_diving"].fillna(0) * 0.2)
    df["defending_clean"] = np.where(is_gk, gk_def, df["defending"])
    df["physical_clean"]  = np.where(is_gk, df["power_strength"].fillna(0), df["physic"])

    df["stamina_clean"]  = df["power_stamina"]
    df["strength_clean"] = df["power_strength"]
    df["agility_clean"]  = df["movement_agility"]
    df["vision_clean"]   = df["mentality_vision"]

    # ── 4. Extra features ─────────────────────────────────────────────────────
    df["preferred_foot_encoded"] = (
        df["preferred_foot"].str.strip().str.capitalize()
        .map({"Right": 1.0, "Left": 0.0})
        .fillna(0.5)
    )
    df["height_cm_norm"] = df["height_cm"].fillna(180) / 100.0

    # ── 5. Build output dataframe ─────────────────────────────────────────────
    out = pd.DataFrame({
        "name":                   df["short_name"].fillna("Unknown").values,
        "age":                    df["age"].values,
        "nationality":            df["nationality_name"].fillna("").values,
        "height_cm":              df["height_cm"].values,
        "weight_kg":              df["weight_kg"].values,
        "overall":                df["overall"].values,
        "position":               df["position"].values,
        "pace":                   df["pace_clean"].values,
        "shooting":               df["shooting_clean"].values,
        "passing":                df["passing_clean"].values,
        "dribbling":              df["dribbling_clean"].values,
        "defending":              df["defending_clean"].values,
        "physical":               df["physical_clean"].values,
        "stamina":                df["stamina_clean"].values,
        "strength":               df["strength_clean"].values,
        "agility":                df["agility_clean"].values,
        "vision":                 df["vision_clean"].values,
        "preferred_foot_encoded": df["preferred_foot_encoded"].values,
        "height_cm_norm":         df["height_cm_norm"].values,
    })

    # ── 6. Drop nulls in attribute columns ───────────────────────────────────
    before = len(out)
    out = out.dropna(subset=ATTR_COLS)
    print(f"  After dropping null attributes: {len(out):,}  (dropped {before - len(out):,})")

    # ── 7. Cast and clip ──────────────────────────────────────────────────────
    for col in ATTR_COLS:
        out[col] = out[col].astype(float).round().astype(int).clip(1, 99)
    for col in ["age", "height_cm", "weight_kg", "overall"]:
        out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0).astype(int)
    out["preferred_foot_encoded"] = out["preferred_foot_encoded"].astype(float)
    out["height_cm_norm"]         = out["height_cm_norm"].astype(float).round(3)

    # ── 8. Dedup on name+position (keep highest overall) ─────────────────────
    out = out.sort_values("overall", ascending=False)
    out = out.drop_duplicates(subset=["name", "position"], keep="first")
    print(f"  After name+position dedup: {len(out):,}")

    # ── 9. Position distribution ──────────────────────────────────────────────
    print("\n  Position distribution:")
    for pos, cnt in out["position"].value_counts().items():
        print(f"    {pos:5s}  {cnt:5,}")

    # ── 10. Save ──────────────────────────────────────────────────────────────
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    out.to_csv(OUT_PATH, index=False)
    print(f"\n  Saved {len(out):,} rows -> {OUT_PATH}")
    return out


if __name__ == "__main__":
    clean()
