"""
Generates data-driven training recommendations based on gap analysis results.
"""

DRILL_LIBRARY = {
    "pace": [
        {"name": "Sprint Intervals", "duration": "20 min", "description": "10×40m sprints with 90s rest. Builds explosive acceleration."},
        {"name": "Resistance Band Sprints", "duration": "15 min", "description": "Sprint against resistance band to develop drive phase power."},
    ],
    "shooting": [
        {"name": "Finishing Drills", "duration": "25 min", "description": "50 shots from varied angles inside the box. Focus on placement."},
        {"name": "Long-Range Shooting", "duration": "20 min", "description": "Strike practice from 20–25m. Develop power and accuracy."},
    ],
    "passing": [
        {"name": "Rondo (5v2)", "duration": "20 min", "description": "Keep-ball drill to sharpen quick passing under pressure."},
        {"name": "Long-Pass Accuracy", "duration": "15 min", "description": "Switch play drills across 40m. Improve weight and direction."},
    ],
    "dribbling": [
        {"name": "Cone Slalom", "duration": "15 min", "description": "Weave through 10 cones at pace. Improves close control."},
        {"name": "1v1 Isolation", "duration": "20 min", "description": "Repeated 1v1 duels to build confidence in tight spaces."},
    ],
    "defending": [
        {"name": "Defensive Positioning", "duration": "20 min", "description": "Shadow defending and jockeying drills. Improve body shape."},
        {"name": "Tackle Timing", "duration": "15 min", "description": "Controlled tackle practice — slide and standing tackles."},
    ],
    "physical": [
        {"name": "Strength Circuit", "duration": "30 min", "description": "Squats, lunges, deadlifts. Build lower-body power."},
        {"name": "Plyometric Training", "duration": "20 min", "description": "Box jumps and broad jumps to develop explosive strength."},
    ],
    "stamina": [
        {"name": "Interval Running", "duration": "30 min", "description": "4×8 min at 80% max HR with 2 min recovery. Builds aerobic base."},
        {"name": "Fartlek Run", "duration": "25 min", "description": "Varied-pace continuous run to simulate match demands."},
    ],
    "strength": [
        {"name": "Upper Body Circuit", "duration": "25 min", "description": "Push-ups, rows, shoulder press. Improve physical presence."},
        {"name": "Core Stability", "duration": "20 min", "description": "Plank variations and rotational exercises for balance."},
    ],
    "agility": [
        {"name": "Ladder Drills", "duration": "15 min", "description": "Agility ladder patterns to sharpen footwork and coordination."},
        {"name": "T-Drill", "duration": "15 min", "description": "Classic T-drill for multi-directional speed."},
    ],
    "vision": [
        {"name": "Awareness Rondo", "duration": "20 min", "description": "Rondo with mandatory scan before receiving. Builds spatial awareness."},
        {"name": "Positional Play (Possession)", "duration": "25 min", "description": "11v11 positional game with points for switches of play."},
    ],
}

def generate_recommendations(weaknesses: list, position: str) -> dict:
    """
    weaknesses: list of {attribute, deficit, ...} from gap_analysis
    Returns weekly plan and drill list.
    """
    priority_attrs = [w["attribute"] for w in weaknesses[:4]]  # top 4 weaknesses
    drills = []
    for attr in priority_attrs:
        for drill in DRILL_LIBRARY.get(attr, []):
            drills.append({**drill, "focus_attribute": attr})

    # Build a 5-day weekly plan
    weekly_plan = []
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    for i, day in enumerate(days):
        day_drills = drills[i * 2: i * 2 + 2] if i * 2 < len(drills) else []
        weekly_plan.append({"day": day, "drills": day_drills, "rest": len(day_drills) == 0})

    return {
        "position": position,
        "priority_attributes": priority_attrs,
        "drills": drills,
        "weekly_plan": weekly_plan,
    }
