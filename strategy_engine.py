"""
Ren Media V2 — Strategy Selection Engine

Purpose:
- Select a small number of appropriate strategies for a video.
- Prevent the entire psychology library from being injected into every prompt.
- Assign a practical strategy budget.
- Assign intensity.
- Detect obvious strategy conflicts.

Important:
This engine is deterministic.
It does NOT call Gemini.

Gemini may help analyze the topic, but the final strategy selection
is controlled here so that the system remains predictable.
"""

from strategies import STRATEGIES


# ============================================================
# STRATEGY BUDGET
# ============================================================

def calculate_strategy_budget(video_length_minutes):
    """
    Establish a reasonable maximum number of active strategies.

    This is intentionally conservative.

    The goal is not to maximize the number of psychological
    techniques. The goal is to make each selected technique
    useful and noticeable without making the script feel engineered.
    """

    try:
        minutes = float(video_length_minutes)
    except (TypeError, ValueError):
        minutes = 10

    if minutes <= 5:
        return 3

    if minutes <= 8:
        return 4

    if minutes <= 12:
        return 5

    if minutes <= 18:
        return 6

    return 7


# ============================================================
# KEYWORD SIGNALS
# ============================================================

STRATEGY_SIGNALS = {

    "zeigarnik_effect": [
        "why",
        "secret",
        "hidden",
        "reason",
        "mistake",
        "truth",
        "explained",
        "reveal",
    ],

    "curiosity_gaps": [
        "why",
        "how",
        "reason",
        "hidden",
        "secret",
        "mistake",
        "truth",
    ],

    "pattern_interrupts": [
        "mistake",
        "myth",
        "wrong",
        "unexpected",
        "surprising",
        "actually",
    ],

    "emotional_triggers": [
        "love",
        "relationship",
        "breakup",
        "money",
        "failure",
        "success",
        "fear",
        "regret",
        "lonely",
        "stress",
        "career",
    ],

    "self_verification_theory": [
        "relationship",
        "dating",
        "confidence",
        "identity",
        "lonely",
        "rejected",
        "misunderstood",
        "social",
    ],

    "reciprocity": [
        "guide",
        "tips",
        "how to",
        "help",
        "learn",
        "strategy",
        "steps",
    ],

    "commitment_consistency": [
        "habit",
        "discipline",
        "change",
        "improve",
        "practice",
        "goal",
        "routine",
    ],

    "liking": [
        "relationship",
        "dating",
        "mistake",
        "story",
        "personal",
        "experience",
    ],

    "authority": [
        "research",
        "science",
        "study",
        "psychology",
        "expert",
        "evidence",
        "history",
    ],

    "social_proof": [
        "people",
        "popular",
        "common",
        "trend",
        "everyone",
        "mistake",
        "behavior",
    ],

    "scarcity": [
        "limited",
        "rare",
        "exclusive",
        "availability",
    ],

    "choice_architecture": [
        "choice",
        "decision",
        "option",
        "options",
        "choose",
        "should i",
        "which",
        "compare",
        "comparison",
    ],

    "but_and_therefore": [
        "story",
        "mistake",
        "journey",
        "case study",
        "what happened",
        "how it happened",
    ],

    "scene_visualization": [
        "imagine",
        "story",
        "example",
        "situation",
        "relationship",
        "dating",
        "work",
        "conversation",
    ],

    "point_development": [
        "why",
        "how",
        "guide",
        "explained",
        "steps",
        "mistakes",
        "things",
        "reasons",
    ],

    "point_ordering": [
        "top",
        "best",
        "worst",
        "mistakes",
        "reasons",
        "things",
        "steps",
        "ways",
    ],

    "small_audience_ask": [
        "opinion",
        "experience",
        "agree",
        "comment",
    ],
}


# ============================================================
# DEFAULT ROLES
# ============================================================

DEFAULT_ROLES = {

    "zeigarnik_effect": "macro attention loop",

    "curiosity_gaps": "micro curiosity",

    "pattern_interrupts": "attention refresh",

    "emotional_triggers": "emotional relevance",

    "self_verification_theory": "audience recognition",

    "reciprocity": "value before ask",

    "commitment_consistency": "action reinforcement",

    "liking": "rapport",

    "authority": "credible evidence",

    "social_proof": "contextual social evidence",

    "scarcity": "genuine rarity",

    "choice_architecture": "decision clarity",

    "but_and_therefore": "narrative causality",

    "scene_visualization": "concrete example",

    "point_development": "complete explanation",

    "point_ordering": "argument progression",

    "small_audience_ask": "low-friction participation",
}


# ============================================================
# STRATEGY CONFLICTS
# ============================================================

CONFLICTS = [

    {
        "strategies": [
            "scarcity",
            "emotional_triggers",
        ],
        "condition": "high_high",
        "severity": "warning",
        "reason":
            "High scarcity combined with high emotional intensity can create artificial urgency."
    },

    {
        "strategies": [
            "social_proof",
            "authority",
        ],
        "condition": "high_high",
        "severity": "warning",
        "reason":
            "Using both as dominant persuasion devices can make the script feel like an authority stack rather than an explanation."
    },

    {
        "strategies": [
            "zeigarnik_effect",
            "curiosity_gaps",
        ],
        "condition": "both_high",
        "severity": "warning",
        "reason":
            "Both create unresolved information. Using both aggressively can overload the script with open loops."
    },

    {
        "strategies": [
            "pattern_interrupts",
            "emotional_triggers",
        ],
        "condition": "both_high",
        "severity": "warning",
        "reason":
            "Frequent pattern interruption combined with high emotional intensity can make the script feel manufactured."
    },

    {
        "strategies": [
            "scarcity",
        ],
        "condition": "informational",
        "severity": "critical",
        "reason":
            "Scarcity should not be selected for ordinary educational content unless genuine scarcity is part of the subject."
    },
]


# ============================================================
# HELPERS
# ============================================================

def normalize_text(*parts):
    """
    Combine topic information into one lowercase search string.
    """
    return " ".join(
        str(part or "")
        for part in parts
    ).lower().strip()


def score_strategy(strategy_key, text):
    """
    Calculate a simple deterministic relevance score.

    This is deliberately transparent.

    It does not pretend to understand the topic at a deep semantic level.
    It simply identifies useful signals and applies conservative rules.
    """

    signals = STRATEGY_SIGNALS.get(strategy_key, [])

    score = 0

    for signal in signals:
        if signal.lower() in text:
            score += 1

    return score


def base_priority(strategy_key):
    """
    Structural priority.

    Some strategies are useful across many videos, while others
    should only appear when the topic strongly supports them.
    """

    priorities = {

        "zeigarnik_effect": 5,

        "curiosity_gaps": 4,

        "pattern_interrupts": 2,

        "emotional_triggers": 3,

        "self_verification_theory": 2,

        "reciprocity": 2,

        "commitment_consistency": 2,

        "liking": 1,

        "authority": 2,

        "social_proof": 1,

        "scarcity": 0,

        "choice_architecture": 2,

        "but_and_therefore": 2,

        "scene_visualization": 3,

        "point_development": 4,

        "point_ordering": 2,

        "small_audience_ask": 1,
    }

    return priorities.get(strategy_key, 0)


def assign_intensity(
    strategy_key,
    rank,
    topic,
    audience,
    objective,
):
    """
    Assign LOW / MEDIUM / HIGH.

    High is intentionally difficult to obtain.

    A strategy being relevant does not mean it should dominate.
    """

    text = normalize_text(
        topic,
        audience,
        objective,
    )

    # Never make scarcity high by default.
    if strategy_key == "scarcity":
        return "LOW"

    # Structural strategies are normally low/medium.
    if strategy_key in {
        "point_development",
        "point_ordering",
        "but_and_therefore",
    }:
        return "MEDIUM"

    # Curiosity can be important but should not dominate.
    if strategy_key == "zeigarnik_effect":
        return "MEDIUM"

    if strategy_key == "curiosity_gaps":
        return "MEDIUM"

    if strategy_key == "emotional_triggers":

        emotional_terms = [
            "love",
            "relationship",
            "breakup",
            "fear",
            "loss",
            "regret",
            "failure",
            "lonely",
            "pain",
        ]

        matches = sum(
            1
            for term in emotional_terms
            if term in text
        )

        if matches >= 3:
            return "MEDIUM"

        return "LOW"

    if strategy_key == "authority":
        if any(
            word in text
            for word in [
                "research",
                "science",
                "study",
                "evidence",
                "psychology",
            ]
        ):
            return "MEDIUM"

        return "LOW"

    if strategy_key == "scene_visualization":
        return "MEDIUM"

    if strategy_key == "self_verification_theory":
        return "MEDIUM"

    if strategy_key == "choice_architecture":
        return "MEDIUM"

    return "LOW"


# ============================================================
# CONFLICT DETECTION
# ============================================================

def detect_conflicts(selected_strategies):
    """
    Detect conflicts between selected strategies.

    Returns a list of structured conflict records.
    """

    selected = {
        item["strategy"]
        for item in selected_strategies
    }

    conflicts = []

    for conflict in CONFLICTS:

        required = set(conflict["strategies"])

        if not required.issubset(selected):
            continue

        # Single-strategy informational restriction.
        if conflict["condition"] == "informational":
            conflicts.append({
                "severity": conflict["severity"],
                "strategies": conflict["strategies"],
                "reason": conflict["reason"],
            })
            continue

        intensity = {
            item["strategy"]: item["intensity"]
            for item in selected_strategies
        }

        if conflict["condition"] == "high_high":

            if all(
                intensity.get(strategy) == "HIGH"
                for strategy in required
            ):
                conflicts.append({
                    "severity": conflict["severity"],
                    "strategies": conflict["strategies"],
                    "reason": conflict["reason"],
                })

        elif conflict["condition"] == "both_high":

            if all(
                intensity.get(strategy) == "HIGH"
                for strategy in required
            ):
                conflicts.append({
                    "severity": conflict["severity"],
                    "strategies": conflict["strategies"],
                    "reason": conflict["reason"],
                })

    return conflicts


# ============================================================
# MAIN ENGINE
# ============================================================

def select_strategies(
    topic,
    audience="",
    objective="",
    video_length_minutes=10,
):
    """
    Select the strategy map for a video.

    Inputs:
        topic
        audience
        objective
        video_length_minutes

    Returns:
        {
            "budget": int,
            "selected": [...],
            "excluded": [...],
            "conflicts": [...]
        }
    """

    budget = calculate_strategy_budget(
        video_length_minutes
    )

    text = normalize_text(
        topic,
        audience,
        objective,
    )

    candidates = []

    for strategy_key, strategy in STRATEGIES.items():

        score = score_strategy(
            strategy_key,
            text,
        )

        priority = base_priority(
            strategy_key
        )

        total_score = (
            score * 2
            + priority
        )

        # Scarcity is deliberately excluded unless
        # the subject explicitly indicates genuine scarcity.
        if strategy_key == "scarcity":
            scarcity_signals = [
                "limited",
                "rare",
                "exclusive",
                "availability",
            ]

            if not any(
                signal in text
                for signal in scarcity_signals
            ):
                total_score = -999

        candidates.append({
            "strategy": strategy_key,
            "score": total_score,
            "signal_score": score,
            "priority": priority,
        })

    candidates.sort(
        key=lambda item: (
            item["score"],
            item["priority"],
        ),
        reverse=True,
    )

    # --------------------------------------------------------
    # Select candidates
    # --------------------------------------------------------

    selected = []

    for candidate in candidates:

        if len(selected) >= budget:
            break

        if candidate["score"] <= 0:
            continue

        strategy_key = candidate["strategy"]

        intensity = assign_intensity(
            strategy_key,
            len(selected) + 1,
            topic,
            audience,
            objective,
        )

        selected.append({
            "strategy": strategy_key,
            "name": STRATEGIES[strategy_key]["name"],
            "category": STRATEGIES[strategy_key]["category"],
            "role": DEFAULT_ROLES.get(
                strategy_key,
                "supporting strategy",
            ),
            "intensity": intensity,
            "score": candidate["score"],
            "locations": STRATEGIES[
                strategy_key
            ]["locations"],
            "desired_response": STRATEGIES[
                strategy_key
            ]["desired_response"],
        })

    # --------------------------------------------------------
    # Essential structural strategy
    # --------------------------------------------------------
    #
    # A script needs point development, but we don't want
    # to allow the engine to crowd out stronger topic-specific
    # strategies.
    #

    if (
        len(selected) < budget
        and "point_development"
        not in {
            item["strategy"]
            for item in selected
        }
    ):
        selected.append({
            "strategy": "point_development",
            "name": STRATEGIES[
                "point_development"
            ]["name"],
            "category": "structure",
            "role": DEFAULT_ROLES[
                "point_development"
            ],
            "intensity": "MEDIUM",
            "score": base_priority(
                "point_development"
            ),
            "locations": STRATEGIES[
                "point_development"
            ]["locations"],
            "desired_response": STRATEGIES[
                "point_development"
            ]["desired_response"],
        })

    # --------------------------------------------------------
    # Prevent excessive overlap
    # --------------------------------------------------------

    selected = reduce_redundancy(
        selected,
        budget,
    )

    conflicts = detect_conflicts(
        selected
    )

    selected_keys = {
        item["strategy"]
        for item in selected
    }

    excluded = []

    for strategy_key in STRATEGIES:

        if strategy_key not in selected_keys:

            excluded.append({
                "strategy": strategy_key,
                "reason": (
                    "Not selected for this video's "
                    "current strategy budget."
                ),
            })

    return {
        "budget": budget,
        "selected": selected,
        "excluded": excluded,
        "conflicts": conflicts,
    }


# ============================================================
# REDUNDANCY CONTROL
# ============================================================

def reduce_redundancy(
    selected,
    budget,
):
    """
    Prevent multiple strategies from doing essentially
    the same job.

    This is deliberately simple and transparent.
    """

    groups = [
        {
            "zeigarnik_effect",
            "curiosity_gaps",
        },

        {
            "emotional_triggers",
            "self_verification_theory",
        },

        {
            "authority",
            "social_proof",
        },
    ]

    kept = []

    for item in selected:

        current = item["strategy"]

        already_has_group_member = False

        for group in groups:

            if current not in group:
                continue

            for existing in kept:

                if existing["strategy"] in group:
                    already_has_group_member = True
                    break

            if already_has_group_member:
                break

        if already_has_group_member:
            continue

        kept.append(item)

        if len(kept) >= budget:
            break

    return kept


# ============================================================
# HUMAN-READABLE MAP
# ============================================================

def format_strategy_map(strategy_map):
    """
    Convert the structured strategy map into a clean prompt/UI
    representation.
    """

    lines = []

    lines.append(
        f"STRATEGY BUDGET: {strategy_map['budget']}"
    )

    lines.append("")
    lines.append("SELECTED STRATEGIES:")

    for index, item in enumerate(
        strategy_map["selected"],
        start=1,
    ):

        lines.append(
            f"{index}. {item['name']}"
        )

        lines.append(
            f"   Key: {item['strategy']}"
        )

        lines.append(
            f"   Role: {item['role']}"
        )

        lines.append(
            f"   Intensity: {item['intensity']}"
        )

        lines.append(
            "   Locations: "
            + ", ".join(
                item["locations"]
            )
        )

        lines.append(
            f"   Desired response: "
            f"{item['desired_response']}"
        )

    if strategy_map["conflicts"]:

        lines.append("")
        lines.append("CONFLICTS / WARNINGS:")

        for conflict in strategy_map[
            "conflicts"
        ]:

            lines.append(
                f"- {conflict['severity'].upper()}: "
                f"{conflict['reason']}"
            )

    return "\n".join(lines)


# ============================================================
# SIMPLE SELF TEST
# ============================================================

if __name__ == "__main__":

    example = select_strategies(
        topic="Why women lose interest fast",
        audience="adult men",
        objective="Explain possible relationship and communication patterns",
        video_length_minutes=10,
    )

    print(format_strategy_map(example))
