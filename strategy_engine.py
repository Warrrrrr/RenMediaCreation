"""
Ren Media — Strategy Engine

Purpose:
Select and rank strategies from the canonical strategy registry.

Important:
- strategies.py is the single source of truth.
- This module must not create its own strategy IDs.
- This module must use the canonical field names from strategies.py.
"""

from strategies import (
    STRATEGIES,
    validate_strategy_ids,
)


# =============================================================================
# DEFAULT STRATEGY SELECTION
# =============================================================================

# These are canonical IDs from strategies.py only.
DEFAULT_STRATEGIES = [
    "curiosity_gaps",
    "scene_zoom_technique",
    "point_development",
    "contrast",
    "causal_progression",
]


# =============================================================================
# TOPIC SIGNALS
# =============================================================================

def _topic_text(topic):
    return str(topic or "").strip().lower()


def _contains_any(text, words):
    return any(word in text for word in words)


# =============================================================================
# STRATEGY SCORING
# =============================================================================

def _score_strategy(strategy_id, topic, audience, objective):
    """
    Lightweight deterministic relevance scoring.

    This is intentionally conservative.
    The engine should select fewer relevant strategies rather than
    dumping the entire strategy library into every video.
    """

    text = " ".join(
        [
            _topic_text(topic),
            _topic_text(audience),
            _topic_text(objective),
        ]
    )

    score = 0

    if strategy_id == "curiosity_gaps":
        score += 3

        if _contains_any(
            text,
            [
                "why",
                "how",
                "what happens",
                "secret",
                "mistake",
                "reason",
                "hidden",
                "actually",
            ],
        ):
            score += 2

    elif strategy_id == "scene_zoom_technique":
        score += 2

        if _contains_any(
            text,
            [
                "relationship",
                "dating",
                "marriage",
                "communication",
                "behavior",
                "conversation",
                "people",
                "social",
            ],
        ):
            score += 2

    elif strategy_id == "point_development":
        score += 3

    elif strategy_id == "contrast":
        score += 2

        if _contains_any(
            text,
            [
                "difference",
                "instead",
                "versus",
                "vs",
                "better",
                "worse",
                "mistake",
                "myth",
            ],
        ):
            score += 2

    elif strategy_id == "causal_progression":
        score += 2

        if _contains_any(
            text,
            [
                "cause",
                "causes",
                "why",
                "leads to",
                "result",
                "effect",
                "impact",
                "pattern",
                "consequence",
            ],
        ):
            score += 2

    elif strategy_id == "emotional_triggers":
        if _contains_any(
            text,
            [
                "love",
                "relationship",
                "breakup",
                "fear",
                "lonely",
                "emotion",
                "trust",
                "rejection",
                "attraction",
            ],
        ):
            score += 3

    elif strategy_id == "pattern_interrupts":
        score += 1

    elif strategy_id == "choice_architecture":
        if _contains_any(
            text,
            [
                "decision",
                "choice",
                "choose",
                "buy",
                "behavior",
                "habit",
            ],
        ):
            score += 3

    elif strategy_id == "small_audience_ask":
        # CTA is deliberately low priority.
        score += 1

    return score


# =============================================================================
# CONFLICTS
# =============================================================================

def _find_conflicts(selected_ids):
    """
    Identify obvious strategy conflicts.

    Returns human-readable conflict records.
    """

    conflicts = []

    selected = set(selected_ids)

    if (
        "emotional_triggers" in selected
        and "causal_progression" in selected
    ):
        conflicts.append(
            {
                "type": "intensity_precision",
                "strategies": [
                    "emotional_triggers",
                    "causal_progression",
                ],
                "message": (
                    "Emotional framing and causal reasoning are both active. "
                    "Keep emotional language from strengthening causal claims."
                ),
            }
        )

    if (
        "curiosity_gaps" in selected
        and "small_audience_ask" in selected
    ):
        conflicts.append(
            {
                "type": "retention_cta",
                "strategies": [
                    "curiosity_gaps",
                    "small_audience_ask",
                ],
                "message": (
                    "CTA should not interrupt an unresolved curiosity gap."
                ),
            }
        )

    return conflicts


# =============================================================================
# INTENSITY
# =============================================================================

def _default_intensity(strategy_id):
    """
    Conservative default intensity.

    The registry remains authoritative about the recommended range.
    """

    if strategy_id in {
        "pattern_interrupts",
        "small_audience_ask",
    }:
        return "LOW"

    if strategy_id in {
        "curiosity_gaps",
        "scene_zoom_technique",
        "contrast",
        "emotional_triggers",
    }:
        return "MEDIUM"

    return "MEDIUM"


# =============================================================================
# BUDGET
# =============================================================================

def _strategy_budget(length_minutes):
    """
    Conservative maximum number of active strategies.

    This prevents the system from turning a short video into a catalogue
    of techniques.
    """

    try:
        length = float(length_minutes)
    except (TypeError, ValueError):
        length = 10

    if length <= 5:
        return 3

    if length <= 10:
        return 5

    if length <= 15:
        return 6

    return 7


# =============================================================================
# STRATEGY SELECTION
# =============================================================================

def select_strategies(
    topic,
    audience="",
    objective="",
    length_minutes=10,
):
    """
    Select a small set of relevant strategies from the canonical registry.

    Returns a structured strategy map.
    """

    # -------------------------------------------------------------------------
    # Verify registry first.
    # -------------------------------------------------------------------------

    selected_candidates = []

    for strategy_id in STRATEGIES:

        score = _score_strategy(
            strategy_id,
            topic,
            audience,
            objective,
        )

        if score > 0:
            selected_candidates.append(
                (
                    strategy_id,
                    score,
                )
            )

    # -------------------------------------------------------------------------
    # Guarantee the core structural strategies if they exist.
    # -------------------------------------------------------------------------

    for strategy_id in DEFAULT_STRATEGIES:

        if strategy_id in STRATEGIES:

            existing = [
                item[0]
                for item in selected_candidates
            ]

            if strategy_id not in existing:
                selected_candidates.append(
                    (
                        strategy_id,
                        _score_strategy(
                            strategy_id,
                            topic,
                            audience,
                            objective,
                        ),
                    )
                )

    # -------------------------------------------------------------------------
    # Sort by relevance.
    # -------------------------------------------------------------------------

    selected_candidates.sort(
        key=lambda item: item[1],
        reverse=True,
    )

    budget = _strategy_budget(length_minutes)

    selected_candidates = selected_candidates[:budget]

    selected_ids = [
        strategy_id
        for strategy_id, _score in selected_candidates
    ]

    # -------------------------------------------------------------------------
    # Strict registry validation.
    # -------------------------------------------------------------------------

    unknown_ids = validate_strategy_ids(selected_ids)

    if unknown_ids:
        raise ValueError(
            f"Strategy engine produced unknown strategy IDs: "
            f"{unknown_ids}"
        )

    # -------------------------------------------------------------------------
    # Build strategy records.
    # -------------------------------------------------------------------------

    selected = []

    for strategy_id, score in selected_candidates:

        strategy = STRATEGIES[strategy_id]

        selected.append(
            {
                "id": strategy_id,
                "name": strategy["name"],
                "role": strategy["primary_purpose"],
                "score": score,
                "intensity": _default_intensity(strategy_id),
                "locations": strategy["script_locations"],
                "desired_viewer_response": (
                    strategy["desired_viewer_response"]
                ),
                "use_when": strategy["use_when"],
                "do_not_use_when": strategy["do_not_use_when"],
                "risks": strategy["risks"],
            }
        )

    # -------------------------------------------------------------------------
    # Conflicts.
    # -------------------------------------------------------------------------

    conflicts = _find_conflicts(selected_ids)

    # -------------------------------------------------------------------------
    # Return canonical strategy map.
    # -------------------------------------------------------------------------

    return {
        "selected_strategies": selected,
        "selected_strategy_ids": selected_ids,
        "budget": budget,
        "conflicts": conflicts,
        "excluded_strategy_ids": [
            strategy_id
            for strategy_id in STRATEGIES
            if strategy_id not in selected_ids
        ],
    }


# =============================================================================
# ALIASES
# =============================================================================

def build_strategy_map(
    topic,
    audience="",
    objective="",
    length_minutes=10,
):
    return select_strategies(
        topic=topic,
        audience=audience,
        objective=objective,
        length_minutes=length_minutes,
    )


def generate_strategy_map(
    topic,
    audience="",
    objective="",
    length_minutes=10,
):
    return select_strategies(
        topic=topic,
        audience=audience,
        objective=objective,
        length_minutes=length_minutes,
    )


def choose_strategies(
    topic,
    audience="",
    objective="",
    length_minutes=10,
):
    return select_strategies(
        topic=topic,
        audience=audience,
        objective=objective,
        length_minutes=length_minutes,
    )


def select_strategy_map(
    topic,
    audience="",
    objective="",
    length_minutes=10,
):
    return select_strategies(
        topic=topic,
        audience=audience,
        objective=objective,
        length_minutes=length_minutes,
    )
