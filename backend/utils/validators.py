FEATURE_COLS = ["pace","shooting","passing","dribbling","defending",
                "physical","stamina","strength","agility","vision"]

def validate_player_input(data: dict) -> tuple[bool, str]:
    """Returns (is_valid, error_message)."""
    if not data:
        return False, "No data provided."
    for col in FEATURE_COLS:
        if col not in data:
            return False, f"Missing field: {col}"
        try:
            val = int(data[col])
        except (ValueError, TypeError):
            return False, f"Field '{col}' must be an integer."
        if not (1 <= val <= 99):
            return False, f"Field '{col}' must be between 1 and 99."
    return True, ""
