"""
Ren Media — Canonical Strategy Registry

This is the single source of truth for strategy IDs.

Rules:
- Every strategy has exactly one canonical ID.
- Other modules must reference these IDs.
- Do not create strategy IDs inside prompts.
- Do not create strategy IDs inside validator.py.
- Do not silently rename existing psychology.py concepts.
"""

# =============================================================================
# CANONICAL STRATEGIES
# =============================================================================

STRATEGIES = {

    "emotional_triggers": {
        "name": "Emotional Triggers",
        "category": "emotion",
        "primary_purpose": "Create an emotionally meaningful response that supports the video's main idea.",
        "use_when": [
            "The topic naturally involves emotion.",
            "An emotional response helps the viewer understand or remember the point."
        ],
        "do_not_use_when": [
            "Emotion would exaggerate the evidence.",
            "The topic requires neutral factual treatment."
        ],
        "script_locations": [
            "hook",
            "development",
            "climax"
        ],
        "desired_viewer_response": "Emotional recognition or significance.",
        "how_to_apply": "Use concrete situations, consequences and emotionally recognizable experiences without manufacturing personal experiences.",
        "good_example": "Describe a recognizable relationship situation and explain why it matters.",
        "bad_example": "Artificially escalating emotion simply to create retention.",
        "risks": [
            "Emotional manipulation",
            "Overstatement"
        ],
        "evidence_requirements": "None for emotional framing itself. Factual claims still require appropriate support.",
        "intensity_guidance": "LOW to MEDIUM by default.",
        "repetition_guidance": "Vary emotional expression rather than repeating the same emotional pattern."
    },

    "scene_zoom_technique": {
        "name": "Scene Zoom Technique",
        "category": "visualization",
        "primary_purpose": "Turn an abstract idea into a concrete, recognizable situation.",
        "use_when": [
            "The viewer benefits from seeing how an idea appears in real life.",
            "The concept is abstract or difficult to visualize."
        ],
        "do_not_use_when": [
            "A concrete scene would distort the evidence.",
            "The point is already clear without visualization."
        ],
        "script_locations": [
            "setup",
            "development",
            "example"
        ],
        "desired_viewer_response": "Recognition and mental visualization.",
        "how_to_apply": "Zoom into a specific hypothetical or supplied situation without pretending it happened to the creator.",
        "good_example": "Imagine a couple having the same conversation after a long day...",
        "bad_example": "I remember sitting in my living room when this happened...",
        "risks": [
            "Fabricated personal experience",
            "Over-dramatization"
        ],
        "evidence_requirements": "Clearly distinguish hypothetical examples from documented events.",
        "intensity_guidance": "LOW to MEDIUM.",
        "repetition_guidance": "Use selectively."
    },

    "point_development": {
        "name": "Point Development",
        "category": "structure",
        "primary_purpose": "Develop an important idea deeply enough for the viewer to understand it.",
        "use_when": [
            "A point requires explanation rather than a brief statement."
        ],
        "do_not_use_when": [
            "The point is minor.",
            "Additional explanation would create unnecessary length."
        ],
        "script_locations": [
            "development"
        ],
        "desired_viewer_response": "Understanding.",
        "how_to_apply": "Explain what the point is, why it matters, how it works, what it looks like and how it connects to the next idea.",
        "good_example": "Explain a communication behavior, its consequence, a recognizable example and its connection to the next behavior.",
        "bad_example": "Repeating the same claim using different words.",
        "risks": [
            "Over-explaining",
            "Lecture-like pacing"
        ],
        "evidence_requirements": "Claims must follow the claim register and governance rules.",
        "intensity_guidance": "MEDIUM.",
        "repetition_guidance": "Each major point should be developed once."
    },

    "curiosity_gaps": {
        "name": "Curiosity Gaps",
        "category": "retention",
        "primary_purpose": "Create a meaningful unanswered question that encourages continued viewing.",
        "use_when": [
            "The question naturally follows from the video's promise."
        ],
        "do_not_use_when": [
            "The payoff cannot realistically be delivered.",
            "The device would feel manipulative."
        ],
        "script_locations": [
            "hook",
            "transitions",
            "section openings"
        ],
        "desired_viewer_response": "Curiosity.",
        "how_to_apply": "Raise a specific question or unresolved tension and provide its payoff later.",
        "good_example": "The interesting part is what happens when that pattern repeats...",
        "bad_example": "You won't believe what happens next.",
        "risks": [
            "Unnecessary suspense",
            "Unresolved promises"
        ],
        "evidence_requirements": "The eventual payoff must actually answer the question.",
        "intensity_guidance": "LOW to MEDIUM.",
        "repetition_guidance": "Avoid stacking too many unresolved questions."
    },

    "pattern_interrupts": {
        "name": "Pattern Interrupts",
        "category": "pacing",
        "primary_purpose": "Prevent monotonous presentation by changing the rhythm or presentation approach.",
        "use_when": [
            "The script becomes rhythmically predictable."
        ],
        "do_not_use_when": [
            "The interruption would distract from an important explanation."
        ],
        "script_locations": [
            "transitions",
            "long development sections"
        ],
        "desired_viewer_response": "Renewed attention.",
        "how_to_apply": "Change sentence rhythm, perspective, example type or presentation approach naturally.",
        "good_example": "After explaining a concept, shift into a concrete scenario.",
        "bad_example": "Insert a random dramatic sentence every few paragraphs.",
        "risks": [
            "Mechanical pacing",
            "Distraction"
        ],
        "evidence_requirements": "None for the structural technique itself.",
        "intensity_guidance": "LOW.",
        "repetition_guidance": "Use sparingly."
    },

    "contrast": {
        "name": "Contrast",
        "category": "reasoning",
        "primary_purpose": "Make an important distinction easier to understand.",
        "use_when": [
            "Two ideas, behaviors or outcomes are meaningfully different."
        ],
        "do_not_use_when": [
            "The distinction is artificial."
        ],
        "script_locations": [
            "setup",
            "development",
            "resolution"
        ],
        "desired_viewer_response": "Clarity.",
        "how_to_apply": "Place genuinely different approaches or outcomes side by side.",
        "good_example": "There is a difference between being quiet and avoiding a conversation.",
        "bad_example": "Inventing a false either/or distinction.",
        "risks": [
            "False dichotomy"
        ],
        "evidence_requirements": "Both sides must be represented accurately.",
        "intensity_guidance": "LOW to MEDIUM.",
        "repetition_guidance": "Use for major distinctions only."
    },

    "causal_progression": {
        "name": "Causal Progression",
        "category": "reasoning",
        "primary_purpose": "Show how one idea, behavior or condition can lead toward another.",
        "use_when": [
            "The source material supports a meaningful relationship between events or behaviors."
        ],
        "do_not_use_when": [
            "The evidence only demonstrates correlation or association.",
            "The causal chain is speculative."
        ],
        "script_locations": [
            "development",
            "resolution"
        ],
        "desired_viewer_response": "Understanding of relationships between ideas.",
        "how_to_apply": "Use appropriately calibrated language unless causation is actually established.",
        "good_example": "This pattern can contribute to...",
        "bad_example": "This behavior causes divorce, when the evidence only shows association.",
        "risks": [
            "Causal overclaiming"
        ],
        "evidence_requirements": "Causal language requires appropriate evidence.",
        "intensity_guidance": "MEDIUM.",
        "repetition_guidance": "Use only where necessary."
    },

    "choice_architecture": {
        "name": "Choice Architecture",
        "category": "decision",
        "primary_purpose": "Help the viewer understand how available choices influence behavior.",
        "use_when": [
            "The topic genuinely involves decisions or behavioral options."
        ],
        "do_not_use_when": [
            "The concept does not meaningfully involve choice."
        ],
        "script_locations": [
            "development",
            "practical takeaway"
        ],
        "desired_viewer_response": "Awareness of choices.",
        "how_to_apply": "Explain how options are presented and how that presentation can influence decisions.",
        "good_example": "Show how changing the available options changes the decision environment.",
        "bad_example": "Mention choice architecture merely because it is a psychology term.",
        "risks": [
            "Psychology perfume"
        ],
        "evidence_requirements": "Psychological claims require appropriate support.",
        "intensity_guidance": "LOW to MEDIUM.",
        "repetition_guidance": "Use only where relevant."
    },

    "small_audience_ask": {
        "name": "Small Audience Ask",
        "category": "CTA",
        "primary_purpose": "Invite a simple, relevant viewer action.",
        "use_when": [
            "A natural audience interaction fits the video."
        ],
        "do_not_use_when": [
            "It interrupts unresolved narrative tension."
        ],
        "script_locations": [
            "outro"
        ],
        "desired_viewer_response": "Simple participation.",
        "how_to_apply": "Ask for one relevant action rather than multiple competing actions.",
        "good_example": "If you've noticed this pattern, tell me which part sounds familiar.",
        "bad_example": "Like, subscribe, comment, share, join, download and buy.",
        "risks": [
            "CTA overload",
            "Narrative interruption"
        ],
        "evidence_requirements": "None.",
        "intensity_guidance": "LOW.",
        "repetition_guidance": "Normally once."
    },
}


# =============================================================================
# REGISTRY HELPERS
# =============================================================================

def get_strategy(strategy_id):
    """Return one canonical strategy record."""
    return STRATEGIES.get(strategy_id)


def get_all_strategy_ids():
    """Return every canonical strategy ID."""
    return list(STRATEGIES.keys())


def get_all_strategies():
    """Return the complete canonical registry."""
    return STRATEGIES.copy()


def strategy_exists(strategy_id):
    """Check whether an ID belongs to the canonical registry."""
    return strategy_id in STRATEGIES


def validate_strategy_ids(strategy_ids):
    """
    Return unknown strategy IDs.

    This is deliberately strict.
    Unknown IDs are not silently converted or renamed.
    """
    return [
        strategy_id
        for strategy_id in strategy_ids
        if strategy_id not in STRATEGIES
    ]


# =============================================================================
# STARTUP INTEGRITY CHECK
# =============================================================================

_REQUIRED_FIELDS = {
    "name",
    "category",
    "primary_purpose",
    "use_when",
    "do_not_use_when",
    "script_locations",
    "desired_viewer_response",
    "how_to_apply",
    "good_example",
    "bad_example",
    "risks",
    "evidence_requirements",
    "intensity_guidance",
    "repetition_guidance",
}


def validate_registry():
    """
    Verify that every canonical strategy contains the required fields.

    Raises ValueError if the registry is malformed.
    """

    for strategy_id, strategy in STRATEGIES.items():

        missing = _REQUIRED_FIELDS - set(strategy.keys())

        if missing:
            raise ValueError(
                f"Strategy '{strategy_id}' is missing fields: "
                f"{sorted(missing)}"
            )

    return True


validate_registry()
