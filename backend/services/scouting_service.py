"""
Scouting Service
=================
Builds a prompt from ML pipeline output and calls the OpenAI API
to generate a 3-paragraph, under-220-word plain-English scouting report.

Every distinct failure mode maps to a specific ScoutingReportError with
a user-facing message — the route converts these to clean HTTP 502 responses.
"""
import os
import sys
import logging

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT)

from backend.config import Config

logger = logging.getLogger("pitchiq.scouting")

# Import OpenAI at module level so tests can patch backend.services.scouting_service.OpenAI
try:
    from openai import (
        OpenAI,
        APITimeoutError,
        RateLimitError,
        APIConnectionError,
        AuthenticationError,
    )
    _OPENAI_AVAILABLE = True
except ImportError:
    _OPENAI_AVAILABLE = False

POSITION_LABELS = {
    "GK": "Goalkeeper", "CB": "Centre-Back", "LB": "Left-Back",
    "RB": "Right-Back",  "CDM": "Defensive Midfielder",
    "CM": "Central Midfielder", "CAM": "Attacking Midfielder",
    "LW": "Left Winger", "RW": "Right Winger",
    "ST": "Striker",     "CF": "Centre-Forward",
}


class ScoutingReportError(Exception):
    """Raised for every distinct LLM failure mode with a user-facing message."""
    def __init__(self, message: str, retry: bool = True):
        super().__init__(message)
        self.user_message = message
        self.retry = retry


def _build_prompt(context: dict) -> str:
    """
    Converts the structured ML output into a tightly scoped scout brief.
    Only uses numbers/labels the ML pipeline already computed.
    """
    player_name = context.get("player_name") or "The player"
    player_age  = context.get("player_age")
    attrs       = context.get("attributes", {})
    predictions = context.get("predictions", [])
    gap         = context.get("gap_analysis", {})
    similar     = context.get("similar_players", [])

    # Top position
    top_pos      = predictions[0]["position"] if predictions else "Unknown"
    top_conf     = predictions[0]["confidence"] if predictions else 0
    top_label    = POSITION_LABELS.get(top_pos, top_pos)
    other_pos    = ", ".join(
        f"{p['position']} ({p['confidence']:.1f}%)"
        for p in predictions[1:3]
    ) if len(predictions) > 1 else "none"

    # Strengths and weaknesses from gap analysis
    strengths  = gap.get("strengths", [])
    weaknesses = gap.get("weaknesses", [])
    str_text   = ", ".join(
        f"{s['attribute']} ({s['value']}, +{s['surplus']} above ideal)"
        for s in strengths[:4]
    ) or "none identified"
    weak_text  = ", ".join(
        f"{w['attribute']} ({w['value']}, -{w['deficit']} below ideal)"
        for w in weaknesses[:4]
    ) or "none identified"

    # Similar real players
    sim_text = ", ".join(
        f"{p['name']} ({p['position']}, {p['similarity']:.1f}% similarity)"
        for p in similar[:3]
    ) or "no close matches found"

    # Overall rating
    overall = round(sum(attrs.values()) / len(attrs)) if attrs else 0

    age_clause = f"aged {player_age}" if player_age and player_age > 0 else ""
    name_age   = f"{player_name}{', ' + age_clause if age_clause else ''}"

    prompt = f"""You are a professional football scout writing a concise player report.

PLAYER DATA (from ML analysis — do NOT invent any statistics not listed here):
- Name/Age: {name_age}
- Overall Rating: {overall}/99
- Primary Position: {top_pos} – {top_label} ({top_conf:.1f}% confidence)
- Other Viable Positions: {other_pos}
- Key Strengths: {str_text}
- Priority Weaknesses: {weak_text}
- Statistically Similar Players: {sim_text}
- Raw Attributes: {', '.join(f"{k}={v}" for k, v in attrs.items())}

TASK:
Write a scouting report in exactly 3 short paragraphs, under 220 words total.
- Paragraph 1: Overall profile and why the ML model projects this position as the best fit.
- Paragraph 2: Key strengths and how they would show up in a real match.
- Paragraph 3: The 2-3 most important development areas, each framed as a concrete next step.

RULES:
- Do NOT use headers, bullet points, or lists — plain paragraphs only.
- Do NOT invent statistics, positions, or player names not given above.
- Write like a human scout, not a data report. Be specific and direct.
- Maximum 220 words. Start immediately — no preamble like "Here is the report:"."""

    return prompt


def generate_scouting_report(context: dict) -> str:
    """
    Calls the OpenAI API and returns the report text.
    Raises ScoutingReportError for every distinct failure mode.
    """
    api_key = Config.OPENAI_API_KEY
    if not api_key:
        raise ScoutingReportError(
            "AI scouting reports are not configured (no API key). "
            "Set OPENAI_API_KEY in backend/.env to enable this feature.",
            retry=False,
        )

    if not _OPENAI_AVAILABLE:
        raise ScoutingReportError(
            "OpenAI package is not installed. Run: pip install openai",
            retry=False,
        )

    prompt = _build_prompt(context)
    logger.info("Generating scouting report for: %s", context.get("player_name", "Anonymous"))

    try:
        openai_client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            timeout=25.0,
        )
        response = openai_client.chat.completions.create(
            model=Config.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=350,
            temperature=0.7,
        )
    except AuthenticationError:
        raise ScoutingReportError(
            "Invalid API key. Please check your OPENAI_API_KEY in backend/.env.",
            retry=False,
        )
    except APITimeoutError:
        raise ScoutingReportError(
            "The AI service timed out. Please try again.",
            retry=True,
        )
    except RateLimitError:
        raise ScoutingReportError(
            "The AI service is rate-limited. Please try again in a moment.",
            retry=True,
        )
    except APIConnectionError:
        raise ScoutingReportError(
            "Could not reach the AI service. Check your internet connection.",
            retry=True,
        )
    except Exception as e:
        logger.error("Unexpected OpenAI error: %s", e)
        raise ScoutingReportError(
            "The AI service returned an unexpected error. Please try again.",
            retry=True,
        )

    content = response.choices[0].message.content if response.choices else ""
    if not content or not content.strip():
        raise ScoutingReportError(
            "The AI returned an empty response. Please try again.",
            retry=True,
        )

    report = content.strip()
    logger.info("Scouting report generated (%d chars)", len(report))
    return report
