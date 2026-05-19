"""
PitchIQ - Data Cleaning Pipeline (vectorised)
================================================
Reads male_players.csv and produces cleaned_players.csv
with the canonical 10-attribute schema used by all ML models.

Attribute mapping:
  pace      <- pace  (outfield) | avg(gk_speed, gk_reflexes) for GK
  shooting  <- shooting (outfield) | avg(gk_kicking, gk_handling) for GK
  passing   <- passing (outfield) | gk_kicking for GK
  dribbling <- dribbling (outfield) | movement_agility for GK
  defending <- defending (outfield) | avg(gk_positioning, gk_reflexes, gk_diving) for GK
  physical  <- physic (outfield) | power_strength for GK
  stamina   <- power_stamina  (all positions)
  strength  <- power_strength (all positions)
  agility   <- movement_agility (all positions)
  vision    <- mentality_vision (all positions)
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

FEATURE_COLS = [
    "pace", "shooting", "passing", "dribbling", "defending",
    "physical", "stamina", "strength", "agility", "vision"
]


def extract_primary_position(pos_str):
    if not isinstance(pos_str, str):
        return None
    for token in pos_str.split(","):
        token = token.strip().upper()
        if token in POSITION_MAP:
            return POSITION_MAP[token]
    return None


def clean():
    print("Reading male_players.csv ...")
    df = pd.read_csv(RAW_PATH, low_memory=False)
    print(f"  Raw rows: {len(df):,}  columns: {len(df.columns)}")

    # ── 1. Keep latest FIFA version per player ────────────────────────────────
    df = df.sort_values("fifa_version", ascending=False)
    df = df.drop_duplicates(subset="player_id", keep="first").copy()
    print(f"  After dedup (latest version per player): {len(df):,}")

    # ── 2. Extract primary position ───────────────────────────────────────────
    df["position"] = df["player_positions"].apply(extract_primary_position)
    df = df[df["position"].notna()].copy()
    print(f"  After position filter: {len(df):,}")

    is_gk = df["position"] == "GK"

    # ── 3. Build 10 canonical attributes (vectorised) ─────────────────────────

    # --- pace ---
    gk_pace = (
        df["goalkeeping_speed"].fillna(0) * 0.5 +
        df["goalkeeping_reflexes"].fillna(0) * 0.5
    )
    df["pace_clean"] = np.where(is_gk, gk_pace, df["pace"])

    # --- shooting ---
    gk_shoot = (
        df["goalkeeping_kicking"].fillna(0) * 0.6 +
        df["goalkeeping_handling"].fillna(0) * 0.4
    )
    df["shooting_clean"] = np.where(is_gk, gk_shoot, df["shooting"])

    # --- passing ---
    df["passing_clean"] = np.where(is_gk, df["goalkeeping_kicking"].fillna(0), df["passing"])

    # --- dribbling ---
    df["dribbling_clean"] = np.where(is_gk, df["movement_agility"].fillna(0), df["dribbling"])

    # --- defending ---
    gk_def = (
        df["goalkeeping_positioning"].fillna(0) * 0.4 +
        df["goalkeeping_reflexes"].fillna(0) * 0.4 +
        df["goalkeeping_diving"].fillna(0) * 0.2
    )
    df["defending_clean"] = np.where(is_gk, gk_def, df["defending"])

    # --- physical ---
    df["physical_clean"] = np.where(is_gk, df["power_strength"].fillna(0), df["physic"])

    # --- shared attributes (same for all positions) ---
    df["stamina_clean"]  = df["power_stamina"]
    df["strength_clean"] = df["power_strength"]
    df["agility_clean"]  = df["movement_agility"]
    df["vision_clean"]   = df["mentality_vision"]

    # ── 4. Build output dataframe ─────────────────────────────────────────────
    out = pd.DataFrame({
        "name":        df["short_name"].fillna("Unknown"),
        "age":         df["age"],
        "nationality": df["nationality_name"].fillna(""),
        "height_cm":   df["height_cm"],
        "weight_kg":   df["weight_kg"],
        "overall":     df["overall"],
        "position":    df["position"],
        "pace":        df["pace_clean"],
        "shooting":    df["shooting_clean"],
        "passing":     df["passing_clean"],
        "dribbling":   df["dribbling_clean"],
        "defending":   df["defending_clean"],
        "physical":    df["physical_clean"],
        "stamina":     df["stamina_clean"],
        "strength":    df["strength_clean"],
        "agility":     df["agility_clean"],
        "vision":      df["vision_clean"],
    })

    # ── 5. Drop rows with nulls in feature columns ────────────────────────────
    before = len(out)
    out = out.dropna(subset=FEATURE_COLS)
    print(f"  After dropping null attributes: {len(out):,}  (dropped {before - len(out):,})")

    # ── 6. Cast and clip all feature columns to int 1-99 ─────────────────────
    for col in FEATURE_COLS:
        out[col] = out[col].astype(float).round().astype(int).clip(1, 99)

    # ── 7. Cast meta columns ──────────────────────────────────────────────────
    for col in ["age", "height_cm", "weight_kg", "overall"]:
        out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0).astype(int)

    # ── 8. Dedup on name+position, keep highest overall ───────────────────────
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
