"""
Generates a synthetic FIFA-style player dataset for PitchIQ.
Run once to produce fifa_players.csv in this directory.
"""
import numpy as np
import pandas as pd
import random

random.seed(42)
np.random.seed(42)

POSITIONS = {
    "GK":  {"pace":40,"shooting":15,"passing":50,"dribbling":30,"defending":20,"physical":65,"stamina":55,"strength":60,"agility":40,"vision":45},
    "CB":  {"pace":55,"shooting":30,"passing":55,"dribbling":40,"defending":85,"physical":80,"stamina":65,"strength":80,"agility":50,"vision":55},
    "LB":  {"pace":75,"shooting":40,"passing":65,"dribbling":60,"defending":70,"physical":65,"stamina":75,"strength":60,"agility":70,"vision":60},
    "RB":  {"pace":75,"shooting":40,"passing":65,"dribbling":60,"defending":70,"physical":65,"stamina":75,"strength":60,"agility":70,"vision":60},
    "CDM": {"pace":60,"shooting":50,"passing":70,"dribbling":60,"defending":75,"physical":75,"stamina":80,"strength":70,"agility":60,"vision":65},
    "CM":  {"pace":65,"shooting":60,"passing":78,"dribbling":68,"defending":60,"physical":65,"stamina":80,"strength":60,"agility":68,"vision":75},
    "CAM": {"pace":70,"shooting":72,"passing":80,"dribbling":78,"defending":40,"physical":55,"stamina":75,"strength":50,"agility":78,"vision":85},
    "LW":  {"pace":85,"shooting":72,"passing":72,"dribbling":82,"defending":35,"physical":55,"stamina":78,"strength":50,"agility":85,"vision":72},
    "RW":  {"pace":85,"shooting":72,"passing":72,"dribbling":82,"defending":35,"physical":55,"stamina":78,"strength":50,"agility":85,"vision":72},
    "ST":  {"pace":78,"shooting":85,"passing":60,"dribbling":72,"defending":30,"physical":72,"stamina":72,"strength":72,"agility":72,"vision":65},
    "CF":  {"pace":75,"shooting":80,"passing":68,"dribbling":76,"defending":32,"physical":65,"stamina":74,"strength":62,"agility":76,"vision":72},
}

FIRST_NAMES = ["James","Carlos","Luca","Ahmed","Kwame","Diego","Yusuf","Mateo","Arjun","Finn",
               "Emre","Noa","Sven","Riku","Tomas","Ivan","Oluwaseun","Hamza","Javier","Kai"]
LAST_NAMES  = ["Silva","Müller","Okafor","Hernandez","Petrov","Nakamura","Diallo","Rossi","Khan","Andersen",
               "Ferreira","Becker","Mensah","Gomez","Ivanov","Tanaka","Osei","Hassan","Torres","Larsson"]

NATIONALITIES = ["Brazil","Germany","Nigeria","Spain","Russia","Japan","Senegal","Italy","Pakistan","Denmark",
                 "Portugal","Austria","Ghana","Mexico","Ukraine","South Korea","France","Egypt","Argentina","Sweden"]

rows = []
for _ in range(2000):
    pos = random.choice(list(POSITIONS.keys()))
    base = POSITIONS[pos]
    noise = lambda v: int(np.clip(v + np.random.normal(0, 8), 1, 99))
    age  = int(np.clip(np.random.normal(24, 4), 16, 38))
    height = int(np.clip(np.random.normal(180, 7), 160, 205))
    weight = int(np.clip(np.random.normal(75, 8), 55, 105))
    name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
    nationality = random.choice(NATIONALITIES)
    rows.append({
        "name": name,
        "age": age,
        "nationality": nationality,
        "height_cm": height,
        "weight_kg": weight,
        "position": pos,
        "pace": noise(base["pace"]),
        "shooting": noise(base["shooting"]),
        "passing": noise(base["passing"]),
        "dribbling": noise(base["dribbling"]),
        "defending": noise(base["defending"]),
        "physical": noise(base["physical"]),
        "stamina": noise(base["stamina"]),
        "strength": noise(base["strength"]),
        "agility": noise(base["agility"]),
        "vision": noise(base["vision"]),
    })

df = pd.DataFrame(rows)
df.to_csv("fifa_players.csv", index=False)
print(f"Generated {len(df)} player records -> fifa_players.csv")
