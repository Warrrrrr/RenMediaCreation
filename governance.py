"""
Ren Media V2 — Governance Layer

This file contains the rules that govern:
- factual claims
- psychology claims
- fabricated personal experience
- emotional intensity
- rhetorical repetition
- open loops
- CTAs
- ethical persuasion

IMPORTANT:
This file is a rule library.

It does not generate scripts.
It does not call Gemini.
It does not rewrite content.

The validator and generation prompts will read these rules later.
"""


# ============================================================
# 1. PERSONAL EXPERIENCE FIREWALL
# ============================================================

PERSONAL_EXPERIENCE_FIREWALL = {

    "purpose": (
        "Prevent the system from inventing first-person experiences, "
        "memories, credentials, relationships, observations, or events."
    ),

    "rule": (
        "The narrator must never claim to have personally experienced "
        "something unless that experience was explicitly supplied by "
        "the user as source material."
    ),

    "prohibited_classes": [

        "Invented childhood memories",

        "Invented relationship experiences",

        "Invented professional experience",

        "Invented coaching or client experience",

        "Invented family experiences",

        "Invented observations",

        "Invented conversations",

        "Invented personal mistakes",

        "Invented personal transformations",

        "Invented credentials",

        "Invented years of experience",

        "Invented locations where the narrator supposedly lived or worked",

        "Invented statements such as 'I remember when...'",

        "Invented statements such as 'I used to think...'",

        "Invented statements such as 'In my own life...'",

        "Invented statements such as 'When I was...'",

        "Invented statements such as 'I've seen this countless times...'",
    ],

    "allowed_alternatives": [

        "Use a hypothetical scenario.",

        "Use a clearly identified example.",

        "Use a documented case when a source is available.",

        "Use 'imagine...' for illustrative scenes.",

        "Use 'for example...' when describing a hypothetical situation.",

        "Use neutral explanatory language."
    ],

    "severity": "CRITICAL",
}


# ============================================================
# 2. CLAIM TYPES
# ============================================================

CLAIM_TYPES = {

    "fact": {
        "definition": (
            "A statement presented as objectively true and "
            "supported by an identifiable source."
        ),

        "required_handling": (
            "Do not strengthen the claim beyond what the source supports."
        ),
    },

    "inference": {
        "definition": (
            "A conclusion reasonably drawn from available evidence."
        ),

        "required_handling": (
            "Signal that the statement is an inference when necessary."
        ),
    },

    "interpretation": {
        "definition": (
            "An explanation or interpretation of evidence, behavior, "
            "events, or findings."
        ),

        "required_handling": (
            "Do not present interpretation as an established fact."
        ),
    },

    "example": {
        "definition": (
            "A hypothetical or illustrative scenario used to explain "
            "an idea."
        ),

        "required_handling": (
            "Make clear that the scenario is an example or hypothetical."
        ),
    },

    "hypothesis": {
        "definition": (
            "A proposed explanation that has not been established "
            "as fact."
        ),

        "required_handling": (
            "Use appropriately cautious language."
        ),
    },
}


# ============================================================
# 3. CLAIM CALIBRATION
# ============================================================

CLAIM_CALIBRATION_RULES = {

    "core_rule": (
        "The strength of the language must not exceed the strength "
        "of the evidence."
    ),

    "avoid_unqualified_certainty": [

        "guarantees",

        "proves",

        "always",

        "never",

        "will definitely",

        "will cause",

        "causes",

        "destroys",

        "cures",

        "prevents",

        "makes you",

        "ensures",

        "scientifically proven"
    ],

    "preferred_calibration": [

        "research suggests",

        "research has found",

        "is associated with",

        "may",

        "can",

        "is one possible explanation",

        "evidence indicates",

        "in some cases",

        "one interpretation is",

        "this does not necessarily mean"
    ],

    "critical_rule": (
        "Never invent a percentage, study result, researcher, "
        "institution, experiment, sample size, date, or quotation."
    ),
}


# ============================================================
# 4. PSYCHOLOGY CLAIM FIREWALL
# ============================================================

PSYCHOLOGY_CLAIM_FIREWALL = {

    "purpose": (
        "Prevent psychological concepts from being presented "
        "as magical laws or universal guarantees."
    ),

    "rules": [

        (
            "A named psychological effect must contribute "
            "to understanding the topic."
        ),

        (
            "Do not introduce a psychological term merely "
            "because it sounds authoritative."
        ),

        (
            "Do not imply that one psychological mechanism "
            "explains every person's behavior."
        ),

        (
            "Do not convert a correlation into causation."
        ),

        (
            "Do not use a psychological label as proof."
        ),

        (
            "Do not imply that identifying a psychological "
            "effect gives the creator diagnostic authority."
        ),

        (
            "Do not present psychology as deterministic "
            "when the underlying phenomenon is probabilistic "
            "or context-dependent."
        ),
    ],

    "high_risk_language": [

        "your brain automatically",

        "your brain is programmed to",

        "humans always",

        "humans are wired to",

        "this guarantees",

        "this proves",

        "this makes people",

        "your subconscious will",

        "everyone does this",

        "everyone reacts this way",
    ],
}


# ============================================================
# 5. PSYCHOLOGY PERFUME CHECK
# ============================================================

PSYCHOLOGY_PERFUME_CHECK = {

    "purpose": (
        "Detect psychology terminology that has been added "
        "for sophistication rather than explanatory value."
    ),

    "rule": (
        "A psychology concept should answer at least one useful "
        "question: What is happening? Why might it happen? "
        "How does it affect the viewer's understanding? "
        "Or what practical implication follows?"
    ),

    "failure_conditions": [

        "Concept is named but never explained.",

        "Concept is named but does not affect the argument.",

        "Concept is used only to make the script sound scientific.",

        "Multiple psychology terms are stacked without explanation.",

        "A familiar idea is unnecessarily renamed with jargon.",

        "The psychology term could be removed without changing "
        "the viewer's understanding."
    ],

    "validator_action": (
        "Flag the concept for review rather than automatically deleting it."
    ),
}


# ============================================================
# 6. EMOTIONAL INTENSITY
# ============================================================

EMOTIONAL_INTENSITY = {

    "levels": {

        "LOW": {
            "description": (
                "Calm, observational, explanatory."
            ),

            "appropriate_for": [
                "definitions",
                "context",
                "transitions",
                "evidence",
                "practical instructions"
            ],
        },

        "MEDIUM": {
            "description": (
                "Emotionally engaging but controlled."
            ),

            "appropriate_for": [
                "important discoveries",
                "recognition moments",
                "examples",
                "consequences",
                "key transitions"
            ],
        },

        "HIGH": {
            "description": (
                "Strong emotional emphasis reserved for "
                "genuinely important moments."
            ),

            "appropriate_for": [
                "major revelation",
                "central conflict",
                "turning point",
                "important consequence"
            ],
        },
    },

    "rules": [

        (
            "Do not maintain HIGH emotional intensity for long "
            "continuous sections."
        ),

        (
            "Emotional intensity should rise and fall rather "
            "than remain permanently elevated."
        ),

        (
            "Do not make every paragraph sound like a revelation."
        ),

        (
            "The climax should have room to feel like a climax."
        ),

        (
            "Use calm sections to create contrast."
        ),
    ],
}


# ============================================================
# 7. RHETORICAL PATTERN CONTROL
# ============================================================

RHETORICAL_PATTERN_CONTROL = {

    "purpose": (
        "Prevent repetitive AI-like rhetorical structures."
    ),

    "patterns_to_monitor": [

        {
            "pattern": "It isn't X, it's Y",
            "rule": (
                "Do not repeatedly use this construction. "
                "Maximum two occurrences in a typical script."
            ),
        },

        {
            "pattern": "The truth is...",
            "rule": (
                "Use sparingly. Repeated use becomes predictable."
            ),
        },

        {
            "pattern": "Here's the thing...",
            "rule": (
                "Avoid repetitive use as a transition."
            ),
        },

        {
            "pattern": "But here's where it gets interesting...",
            "rule": (
                "Avoid as a generic suspense device."
            ),
        },

        {
            "pattern": "You might think X, but Y",
            "rule": (
                "Do not use repeatedly as the primary argument structure."
            ),
        },

        {
            "pattern": "Imagine...",
            "rule": (
                "Use when visualization genuinely improves understanding, "
                "not as a default opening mechanism."
            ),
        },

        {
            "pattern": "What if I told you...",
            "rule": (
                "Avoid as a generic hook template."
            ),
        },

        {
            "pattern": "The reason is simple...",
            "rule": (
                "Avoid repeated use."
            ),
        },
    ],

    "core_rule": (
        "Rhetorical devices should serve communication rather than "
        "announce that the script is trying to persuade the viewer."
    ),
}


# ============================================================
# 8. OPEN LOOP GOVERNANCE
# ============================================================

OPEN_LOOP_GOVERNANCE = {

    "definition": (
        "An open loop creates a meaningful unanswered question "
        "that the viewer expects the script to resolve."
    ),

    "rules": [

        (
            "Every meaningful open loop should eventually receive "
            "a payoff."
        ),

        (
            "Do not create an open loop solely to delay information "
            "that could reasonably be provided immediately."
        ),

        (
            "Do not stack many open loops close together."
        ),

        (
            "The viewer should understand why the unanswered "
            "question matters."
        ),

        (
            "A payoff should actually answer or resolve the "
            "question that was created."
        ),
    ],

    "warning_threshold": {
        "max_new_loops_per_90_seconds": 2
    },
}


# ============================================================
# 9. CTA GOVERNANCE
# ============================================================

CTA_GOVERNANCE = {

    "rules": [

        (
            "The CTA must not interrupt an unresolved important "
            "story beat or explanation."
        ),

        (
            "The viewer should understand the value of the video "
            "before being asked for an action."
        ),

        (
            "The CTA should be proportionate to the relationship "
            "the creator has established with the viewer."
        ),

        (
            "Do not use fear, shame, deception, or fabricated "
            "urgency to force engagement."
        ),

        (
            "Do not manufacture controversy solely to increase comments."
        ),

        (
            "A comment request should give the viewer a genuine "
            "reason to participate."
        ),
    ],

    "preferred_actions": [

        "subscribe",

        "watch another relevant video",

        "comment with a genuine opinion",

        "try a practical exercise",

        "share with someone who would genuinely benefit",
    ],
}


# ============================================================
# 10. ETHICAL PERSUASION GUARDRAILS
# ============================================================

ETHICAL_GUARDRAILS = {

    "core_principle": (
        "Persuasion should improve attention and understanding "
        "without deliberately deceiving, coercing, or exploiting "
        "the viewer."
    ),

    "prohibited": [

        "fabricated evidence",

        "fabricated personal experience",

        "fabricated authority",

        "fabricated scarcity",

        "fabricated social proof",

        "fake testimonials",

        "fake statistics",

        "fake research",

        "deliberately misleading titles",

        "deliberately misleading thumbnails",

        "fear manufactured solely for engagement",

        "shame used solely to force engagement",

        "false promises",

        "guaranteed outcomes without evidence",

        "manipulation of vulnerable audiences through deception",
    ],

    "nudge_rule": (
        "Nudges may simplify or guide a decision, but must not "
        "hide material information or intentionally remove "
        "meaningful user choice."
    ),

    "persuasion_rule": (
        "The system may make content more compelling. "
        "It must not make false content appear true."
    ),
}


# ============================================================
# 11. SCRIPT STRUCTURE GOVERNANCE
# ============================================================

SCRIPT_STRUCTURE_GOVERNANCE = {

    "rule": (
        "The approved outline is the structural authority for "
        "script generation."
    ),

    "rules": [

        (
            "The script generator must not invent a new major "
            "section that is absent from the approved outline."
        ),

        (
            "The script should preserve the approved beat order "
            "unless the user explicitly changes the outline."
        ),

        (
            "Each major point should be sufficiently developed "
            "to be understandable."
        ),

        (
            "Do not pad the script merely to reach a word count."
        ),

        (
            "If the target length cannot be achieved naturally, "
            "prefer removing or shortening a weak beat rather "
            "than compressing every sentence."
        ),
    ],
}


# ============================================================
# 12. STRATEGY GOVERNANCE
# ============================================================

STRATEGY_GOVERNANCE = {

    "rules": [

        (
            "Only strategies selected in the approved strategy map "
            "should guide the script."
        ),

        (
            "A strategy may be used only for the role assigned to it."
        ),

        (
            "A strategy should not appear merely because it exists "
            "in the psychology library."
        ),

        (
            "High-intensity strategies should be used sparingly."
        ),

        (
            "Multiple strategies should not be used to perform "
            "the same function unnecessarily."
        ),

        (
            "The strategy map may be edited by the user before "
            "outline generation."
        ),

        (
            "User-approved strategy changes become authoritative "
            "for subsequent stages."
        ),
    ],
}


# ============================================================
# 13. VALIDATION SEVERITY
# ============================================================

VALIDATION_SEVERITY = {

    "CRITICAL": {
        "description": (
            "A failure that can materially damage factual integrity, "
            "trust, safety, or the core promise of the script."
        ),

        "examples": [

            "fabricated personal experience",

            "fabricated statistic",

            "fabricated research",

            "unsupported guarantee",

            "serious factual overstatement",

            "deliberately deceptive persuasion",
        ],
    },

    "WARNING": {
        "description": (
            "A quality problem that should be reviewed but does "
            "not necessarily make the entire script unusable."
        ),

        "examples": [

            "rhetorical repetition",

            "excessive emotional intensity",

            "psychology terminology without sufficient explanation",

            "open-loop density",

            "weak CTA placement",

            "minor claim-calibration issue",
        ],
    },

    "PASS": {
        "description": (
            "The inspected area contains no detected issue "
            "requiring intervention."
        ),
    },
}


# ============================================================
# 14. MASTER GOVERNANCE OBJECT
# ============================================================

GOVERNANCE = {

    "personal_experience_firewall":
        PERSONAL_EXPERIENCE_FIREWALL,

    "claim_types":
        CLAIM_TYPES,

    "claim_calibration":
        CLAIM_CALIBRATION_RULES,

    "psychology_claim_firewall":
        PSYCHOLOGY_CLAIM_FIREWALL,

    "psychology_perfume_check":
        PSYCHOLOGY_PERFUME_CHECK,

    "emotional_intensity":
        EMOTIONAL_INTENSITY,

    "rhetorical_pattern_control":
        RHETORICAL_PATTERN_CONTROL,

    "open_loop_governance":
        OPEN_LOOP_GOVERNANCE,

    "cta_governance":
        CTA_GOVERNANCE,

    "ethical_guardrails":
        ETHICAL_GUARDRAILS,

    "script_structure":
        SCRIPT_STRUCTURE_GOVERNANCE,

    "strategy_governance":
        STRATEGY_GOVERNANCE,

    "validation_severity":
        VALIDATION_SEVERITY,
}


# ============================================================
# SIMPLE SELF TEST
# ============================================================

if __name__ == "__main__":

    print("Ren Media V2 Governance loaded successfully.")

    print(
        f"Governance categories: {len(GOVERNANCE)}"
    )

    print(
        "Personal experience firewall: OK"
    )

    print(
        "Claim calibration: OK"
    )

    print(
        "Psychology firewall: OK"
    )

    print(
        "Emotional intensity control: OK"
    )

    print(
        "Rhetorical pattern control: OK"
    )

    print(
        "Open-loop governance: OK"
    )

    print(
        "CTA governance: OK"
    )

    print(
        "Ethical guardrails: OK"
    )
