"""
Ren Media V2 — Structured Strategy Library

Purpose:
- Store Ren Media's available psychological, persuasion,
  storytelling, attention, and structural strategies.
- Give the Strategy Engine enough information to decide
  WHEN a strategy belongs in a video.
- Prevent the model from treating every technique as mandatory.

Important:
This file is a knowledge library, not the decision engine.
The Strategy Engine decides what to use.
"""

STRATEGIES = {

    # ============================================================
    # ATTENTION / CURIOSITY
    # ============================================================

    "zeigarnik_effect": {
        "name": "Zeigarnik Effect / Macro Open Loop",
        "category": "attention",

        "primary_purpose":
            "Maintain attention through a meaningful unresolved question.",

        "use_when": [
            "The video contains a question with a real later payoff.",
            "The answer can be delayed without frustrating the viewer."
        ],

        "do_not_use_when": [
            "The viewer needs an immediate answer.",
            "There is no substantive later payoff.",
            "The unresolved question exists only to manufacture retention."
        ],

        "locations": [
            "hook",
            "setup",
            "midpoint",
            "pre_climax"
        ],

        "desired_response":
            "I want to know how this resolves.",

        "application":
            "Plant one concrete question and resolve it later with information that materially improves the viewer's understanding.",

        "good_example":
            "There's one reason this keeps happening, and it isn't the reason most people assume.",

        "bad_example":
            "Keep watching because there's a shocking secret coming.",

        "risks": [
            "fake suspense",
            "delayed answers",
            "retention manipulation"
        ],

        "evidence_requirements":
            "Do not make a scientific claim about the Zeigarnik effect unless appropriate evidence is available.",

        "intensity":
            "low-medium",

        "repetition":
            "Prefer one major unresolved question. Smaller loops must have distinct purposes and payoffs.",

        "keywords": [
            "why",
            "how",
            "reason",
            "secret",
            "mistake",
            "truth"
        ]
    },

    "curiosity_gaps": {
        "name": "Curiosity Gap / Micro Loop",
        "category": "curiosity",

        "primary_purpose":
            "Create a specific information gap that a later section can satisfy.",

        "use_when": [
            "A meaningful unanswered question exists.",
            "The payoff is reasonably close.",
            "The missing information matters to the viewer."
        ],

        "do_not_use_when": [
            "The answer is trivial.",
            "The payoff does not exist.",
            "The video repeatedly promises information it never delivers."
        ],

        "locations": [
            "hook",
            "transitions",
            "rehooks"
        ],

        "desired_response":
            "I need the missing piece.",

        "application":
            "Give enough context for the viewer to understand why the missing information matters, then provide the payoff.",

        "good_example":
            "The problem starts earlier than the argument itself. Here's where.",

        "bad_example":
            "You won't believe what happens next.",

        "risks": [
            "clickbait",
            "loop fatigue",
            "false promises"
        ],

        "evidence_requirements":
            "No special evidence is required unless the loop contains a factual claim.",

        "intensity":
            "low",

        "repetition":
            "Avoid announcing multiple unresolved loops within a short period.",

        "keywords": [
            "why",
            "what",
            "hidden",
            "missing",
            "reason"
        ]
    },

    "pattern_interrupts": {
        "name": "Pattern Interrupt",
        "category": "attention",

        "primary_purpose":
            "Refresh attention when presentation becomes predictable.",

        "use_when": [
            "A section has become rhythmically predictable.",
            "A transition benefits from a change in presentation."
        ],

        "do_not_use_when": [
            "The subject requires calm precision.",
            "The interruption would damage an important emotional payoff.",
            "The interruption exists only to create artificial excitement."
        ],

        "locations": [
            "transitions",
            "middle",
            "rehooks"
        ],

        "desired_response":
            "My attention has been refreshed.",

        "application":
            "Change rhythm, framing, example type, perspective, or question rather than inserting random shock.",

        "good_example":
            "After explaining the theory, switch to one ordinary Tuesday-night example.",

        "bad_example":
            "Suddenly announce something shocking that has nothing to do with the argument.",

        "risks": [
            "gimmickry",
            "constant interruption",
            "loss of coherence"
        ],

        "evidence_requirements":
            "No special evidence unless the pattern interrupt itself contains a factual claim.",

        "intensity":
            "low-medium",

        "repetition":
            "Vary the form. Do not repeat the same interruption pattern.",

        "keywords": [
            "attention",
            "boring",
            "predictable",
            "retention"
        ]
    },

    # ============================================================
    # EMOTION / RECOGNITION
    # ============================================================

    "emotional_triggers": {
        "name": "Emotion / Stakes",
        "category": "emotion",

        "primary_purpose":
            "Make information matter by connecting it to a genuine human consequence.",

        "use_when": [
            "The subject has a genuine human consequence.",
            "Emotion improves relevance or understanding."
        ],

        "do_not_use_when": [
            "Fear or outrage would distort the topic.",
            "The subject requires calm precision.",
            "Emotional escalation is being used merely for retention."
        ],

        "locations": [
            "hook",
            "problem",
            "stakes",
            "payoff"
        ],

        "desired_response":
            "This matters to me.",

        "application":
            "Use concrete consequences and calibrated emotion rather than escalating language for its own sake.",

        "good_example":
            "The frustrating part is that the harder you try to fix the wrong problem, the more exhausted you become.",

        "bad_example":
            "This destroys your entire life if you don't act NOW.",

        "risks": [
            "fearmongering",
            "emotional escalation",
            "manipulation"
        ],

        "evidence_requirements":
            "Emotional framing must not convert uncertain information into certainty.",

        "intensity":
            "medium",

        "repetition":
            "Vary emotional intensity. Allow neutral explanatory sections between stronger moments.",

        "keywords": [
            "fear",
            "frustration",
            "love",
            "money",
            "loss",
            "risk",
            "pain"
        ]
    },

    "self_verification_theory": {
        "name": "Self-Verification / Recognition",
        "category": "trust",

        "primary_purpose":
            "Help the viewer feel accurately understood before challenging their interpretation.",

        "use_when": [
            "The audience is likely to feel misunderstood.",
            "The video challenges a common explanation for the viewer's experience."
        ],

        "do_not_use_when": [
            "Validation would reinforce a harmful or unsupported belief.",
            "The writer would need to pretend to know the viewer's exact personal experience."
        ],

        "locations": [
            "setup",
            "problem"
        ],

        "desired_response":
            "This understands what I'm experiencing.",

        "application":
            "Describe a recognizable experience without claiming that every viewer has the same experience.",

        "good_example":
            "You can do everything that looks right on paper and still feel the relationship drifting.",

        "bad_example":
            "You're right about everything and everyone else is the problem.",

        "risks": [
            "over-validation",
            "reinforcing false beliefs",
            "pretending to know the viewer"
        ],

        "evidence_requirements":
            "Do not turn a relatable experience into a universal psychological claim.",

        "intensity":
            "medium",

        "repetition":
            "Primarily use early. Do not repeatedly tell the viewer that they are understood.",

        "keywords": [
            "feel",
            "experience",
            "struggle",
            "alone",
            "understood"
        ]
    },

    # ============================================================
    # PERSUASION — CIALDINI
    # ============================================================

    "reciprocity": {
        "name": "Reciprocity",
        "category": "persuasion",

        "primary_purpose":
            "Deliver genuine value before asking the viewer for attention or action.",

        "use_when": [
            "The video can provide useful value before a CTA.",
            "A practical insight can be delivered early."
        ],

        "do_not_use_when": [
            "Value is intentionally withheld to manufacture obligation.",
            "The viewer is pressured into feeling indebted."
        ],

        "locations": [
            "early value",
            "solution",
            "before CTA"
        ],

        "desired_response":
            "This video has already helped me.",

        "application":
            "Give the viewer something genuinely useful before asking for an action.",

        "good_example":
            "Give the viewer one practical adjustment they can use today before asking them to subscribe.",

        "bad_example":
            "I gave you this tip, so you owe me a subscription.",

        "risks": [
            "transactional framing",
            "manipulation",
            "manufactured obligation"
        ],

        "evidence_requirements":
            "Factual claims inside the value must still be supported.",

        "intensity":
            "low",

        "repetition":
            "Use as a structural principle rather than repeating the same persuasion tactic.",

        "keywords": [
            "value",
            "help",
            "tip",
            "useful"
        ]
    },

    "commitment_consistency": {
        "name": "Commitment and Consistency",
        "category": "persuasion",

        "primary_purpose":
            "Support follow-through through a small, genuine commitment.",

        "use_when": [
            "The viewer can make a harmless self-directed commitment.",
            "The commitment directly relates to the video's useful takeaway."
        ],

        "do_not_use_when": [
            "The commitment is intended to trap the viewer into another conclusion.",
            "The request is unrelated to the video's value."
        ],

        "locations": [
            "solution",
            "action step"
        ],

        "desired_response":
            "I'll actually try this.",

        "application":
            "Invite one small behavior that directly follows from the video's useful takeaway.",

        "good_example":
            "Tonight, notice one moment when you interrupt yourself before responding. That's the whole exercise.",

        "bad_example":
            "Say yes now, because then you'll have to agree with everything else.",

        "risks": [
            "coercive commitment",
            "engagement manipulation"
        ],

        "evidence_requirements":
            "Do not claim guaranteed behavioral effects without evidence.",

        "intensity":
            "low",

        "repetition":
            "Prefer one meaningful commitment instead of many micro-asks.",

        "keywords": [
            "commit",
            "try",
            "practice",
            "action"
        ]
    },

    "liking": {
        "name": "Liking",
        "category": "trust",

        "primary_purpose":
            "Build genuine rapport through relatability rather than manufactured authority.",

        "use_when": [
            "A genuine relatable observation improves trust.",
            "The creator has supplied a real personal experience."
        ],

        "do_not_use_when": [
            "The writer would need to invent a personal experience.",
            "False similarity or intimacy would be required."
        ],

        "locations": [
            "setup",
            "transition"
        ],

        "desired_response":
            "This feels human and relatable.",

        "application":
            "Use supplied experiences or broadly relatable observations without fabricating biography.",

        "good_example":
            "Imagine making the same mistake yourself. The scene can be hypothetical without pretending the narrator lived it.",

        "bad_example":
            "I made this mistake for ten years.",
            
        "risks": [
            "fabricated persona",
            "false intimacy"
        ],

        "evidence_requirements":
            "Personal history must come from supplied source material.",

        "intensity":
            "low",

        "repetition":
            "One or two authentic rapport moments are generally enough.",

        "keywords": [
            "relatable",
            "mistake",
            "human",
            "admit"
        ]
    },

    "authority": {
        "name": "Authority",
        "category": "trust",

        "primary_purpose":
            "Use genuine expertise or credible evidence to improve trust.",

        "use_when": [
            "The creator supplied relevant credentials.",
            "A real source is available."
        ],

        "do_not_use_when": [
            "Credentials would need to be invented.",
            "Researchers or institutions would need to be invented.",
            "A citation cannot be verified."
        ],

        "locations": [
            "claim setup",
            "evidence"
        ],

        "desired_response":
            "There is a credible reason to trust this claim.",

        "application":
            "Use verifiable sources or supplied credentials. Otherwise omit authority framing.",

        "good_example":
            "According to the source cited for this video, ...",

        "bad_example":
            "Harvard researchers proved this."

        ,

        "risks": [
            "fabricated citation",
            "false authority",
            "credential fabrication"
        ],

        "evidence_requirements":
            "HIGH — specific authority claims require verifiable source material.",

        "intensity":
            "low",

        "repetition":
            "Use only where evidence materially improves understanding.",

        "keywords": [
            "research",
            "study",
            "expert",
            "doctor",
            "professor"
        ]
    },

    "social_proof": {
        "name": "Social Proof",
        "category": "persuasion",

        "primary_purpose":
            "Show how other people behave or respond when that information is genuinely relevant.",

        "use_when": [
            "Real audience behavior or supplied evidence exists.",
            "The behavior of others genuinely helps explain the topic."
        ],

        "do_not_use_when": [
            "Statistics or testimonials would need to be invented.",
            "Popularity is being presented as proof of truth."
        ],

        "locations": [
            "evidence",
            "examples"
        ],

        "desired_response":
            "This behavior is recognizable in the relevant context.",

        "application":
            "Use verified examples or carefully calibrated language. Never invent numbers.",

        "good_example":
            "The examples reviewed for this video show this pattern repeatedly.",

        "bad_example":
            "87% of people do this."

        ,

        "risks": [
            "fake statistics",
            "false consensus",
            "popularity-as-proof"
        ],

        "evidence_requirements":
            "HIGH for numerical or survey claims.",

        "intensity":
            "low",

        "repetition":
            "Use sparingly.",

        "keywords": [
            "most people",
            "everyone",
            "common",
            "percentage",
            "survey"
        ]
    },

    "scarcity": {
        "name": "Scarcity",
        "category": "persuasion",

        "primary_purpose":
            "Highlight genuine rarity or limited availability when it materially matters.",

        "use_when": [
            "Something is genuinely scarce or uncommon."
        ],

        "do_not_use_when": [
            "Urgency would be manufactured.",
            "Rarity is being exaggerated.",
            "Fear of missing out is being manufactured."
        ],

        "locations": [
            "title",
            "hook",
            "offer context"
        ],

        "desired_response":
            "This is unusually limited or uncommon.",

        "application":
            "Describe genuine scarcity precisely. Never fake exclusivity.",

        "good_example":
            "Only use a limited-time claim when the limitation is real.",

        "bad_example":
            "This secret disappears tonight.",

        "risks": [
            "false urgency",
            "fear of missing out",
            "manipulation"
        ],

        "evidence_requirements":
            "Scarcity claims require a factual basis.",

        "intensity":
            "low",

        "repetition":
            "Rarely needed for informational content.",

        "keywords": [
            "rare",
            "limited",
            "exclusive",
            "last chance"
        ]
    },

    # ============================================================
    # NUDGE / CHOICE ARCHITECTURE
    # ============================================================

    "choice_architecture": {
        "name": "Choice Architecture / Nudge",
        "category": "persuasion",

        "primary_purpose":
            "Present options and consequences so the viewer can make a better-informed choice.",

        "use_when": [
            "The video gives practical choices.",
            "Comparing options improves decision quality."
        ],

        "do_not_use_when": [
            "The goal is to covertly force a conclusion.",
            "Important alternatives are intentionally hidden.",
            "The video pretends a value judgment is an objective fact."
        ],

        "locations": [
            "recommendations",
            "solution",
            "decision points"
        ],

        "desired_response":
            "I can see the trade-off clearly.",

        "application":
            "Present meaningful options, defaults, and consequences without disguising persuasion as neutral fact.",

        "good_example":
            "You can respond immediately, or wait until you actually have something useful to say. The trade-off is speed versus substance.",

        "bad_example":
            "There's only one sensible choice, so don't bother considering the others.",

        "risks": [
            "covert manipulation",
            "false binary",
            "hidden alternatives"
        ],

        "evidence_requirements":
            "Consequences should be supported when presented as factual.",

        "intensity":
            "low",

        "repetition":
            "Use where a genuine decision exists.",

        "keywords": [
            "choice",
            "option",
            "decision",
            "default",
            "trade-off"
        ]
    },

    # ============================================================
    # STORYTELLING
    # ============================================================

    "but_and_therefore": {
        "name": "But / Therefore Causal Story Progression",
        "category": "storytelling",

        "primary_purpose":
            "Keep events connected through obstacles and consequences rather than disconnected events.",

        "use_when": [
            "The video uses a narrative example.",
            "A sequence of events needs causal momentum."
        ],

        "do_not_use_when": [
            "The content is a straightforward factual explanation with no narrative sequence."
        ],

        "locations": [
            "stories",
            "examples",
            "case studies"
        ],

        "desired_response":
            "Each event changes what happens next.",

        "application":
            "Connect events using consequence, contrast, or causation instead of simply listing what happened.",

        "good_example":
            "He tried to fix the problem. But the fix created a new problem. Therefore, he changed the way he approached it.",

        "bad_example":
            "Then this happened. Then this happened. Then this happened.",

        "risks": [
            "forced causality",
            "artificial storytelling"
        ],

        "evidence_requirements":
            "Do not imply causation where the evidence only establishes sequence or association.",

        "intensity":
            "medium",

        "repetition":
            "Use naturally as story logic, not as a visible formula.",

        "keywords": [
            "but",
            "therefore",
            "because",
            "however",
            "consequence"
        ]
    },

    "scene_visualization": {
        "name": "Concrete Scene Visualization",
        "category": "storytelling",

        "primary_purpose":
            "Turn an abstract idea into a concrete, understandable situation.",

        "use_when": [
            "The concept is abstract.",
            "A hypothetical scene would make the idea easier to understand."
        ],

        "do_not_use_when": [
            "A scene would require fabricated personal experience.",
            "The scene adds drama without improving understanding."
        ],

        "locations": [
            "examples",
            "explanations",
            "transitions"
        ],

        "desired_response":
            "I can picture what this means.",

        "application":
            "Use location, action, thought, emotion, and dialogue for hypothetical or supplied scenes. Make hypothetical framing clear when needed.",

        "good_example":
            "Imagine standing in the kitchen after work. You see the mug beside the dishwasher, and suddenly the mug isn't the thing you're angry about anymore.",

        "bad_example":
            "I remember standing in my kitchen and feeling this exact thing when no such experience was supplied.",

        "risks": [
            "fabricated experience",
            "overdramatic detail"
        ],

        "evidence_requirements":
            "Personal details require user-supplied source material.",

        "intensity":
            "medium",

        "repetition":
            "Use concrete scenes strategically. Do not turn every point into a movie scene.",

        "keywords": [
            "imagine",
            "scene",
            "moment",
            "example",
            "conversation"
        ]
    },

    # ============================================================
    # STRUCTURE
    # ============================================================

    "point_development": {
        "name": "Full Point Development",
        "category": "structure",

        "primary_purpose":
            "Fully develop each major point before moving to the next.",

        "use_when": [
            "A point materially advances the argument."
        ],

        "do_not_use_when": [
            "The content is only a transition.",
            "The detail is minor and does not require development."
        ],

        "locations": [
            "body sections"
        ],

        "desired_response":
            "I understand the point and why it matters.",

        "application":
            "Develop the point through context, application, concrete example, and connection to the larger argument.",

        "good_example":
            "Explain what the idea is, show it in a concrete situation, explain why it matters, then connect it to what comes next.",

        "bad_example":
            "List five points with one sentence each.",

        "risks": [
            "overdevelopment",
            "repetition",
            "slow pacing"
        ],

        "evidence_requirements":
            "Claims still require appropriate support.",

        "intensity":
            "high",

        "repetition":
            "Applies structurally to substantive points.",

        "keywords": [
            "point",
            "explain",
            "example",
            "why",
            "how"
        ]
    },

    "point_ordering": {
        "name": "Point Ordering / Escalation",
        "category": "structure",

        "primary_purpose":
            "Order examples and ideas so the argument builds instead of peaking too early.",

        "use_when": [
            "Several comparable examples or points need ordering."
        ],

        "do_not_use_when": [
            "The strongest point must come first for clarity or safety."
        ],

        "locations": [
            "body sections"
        ],

        "desired_response":
            "Each example makes the argument clearer or stronger.",

        "application":
            "Order material according to the argument's needs, often building toward the most revealing point before synthesis.",

        "good_example":
            "Use a strong example, then the most revealing example, then a concise synthesis.",

        "bad_example":
            "Use the strongest example first and spend the remainder repeating it.",

        "risks": [
            "artificial escalation"
        ],

        "evidence_requirements":
            "No special evidence requirement.",

        "intensity":
            "low",

        "repetition":
            "Structural rather than verbal.",

        "keywords": [
            "strongest",
            "escalate",
            "sequence",
            "examples"
        ]
    },

    # ============================================================
    # CTA
    # ============================================================

    "small_audience_ask": {
        "name": "Small Audience Ask",
        "category": "cta",

        "primary_purpose":
            "Create a low-friction participation moment at a natural pause.",

        "use_when": [
            "A genuine reflection opportunity exists.",
            "The ask does not interrupt unresolved narrative tension."
        ],

        "do_not_use_when": [
            "The viewer is inside an unresolved narrative moment.",
            "The ask is unrelated.",
            "The purpose is purely engagement bait."
        ],

        "locations": [
            "midpoint",
            "late-middle"
        ],

        "desired_response":
            "I can participate without leaving the story.",

        "application":
            "Ask for a simple reflection only at a natural pause.",

        "good_example":
            "If you've caught yourself doing this, a simple 'yes' is enough.",

        "bad_example":
            "STOP THE VIDEO AND COMMENT RIGHT NOW BEFORE WE CONTINUE.",

        "risks": [
            "immersion break",
            "engagement bait"
        ],

        "evidence_requirements":
            "No special evidence requirement.",

        "intensity":
            "low",

        "repetition":
            "Normally one mid-video participation ask maximum.",

        "keywords": [
            "comment",
            "subscribe",
            "engage"
        ]
    }
}


def get_strategy(strategy_key):
    """Return one strategy record by key."""
    return STRATEGIES.get(strategy_key)


def strategy_catalog_text(selected_keys=None):
    """
    Return a compact representation for prompts.

    If selected_keys is supplied, ONLY those strategies are returned.
    This is important: generation should not receive the entire strategy
    library unless there is a deliberate reason to do so.
    """

    if selected_keys is None:
        selected = STRATEGIES.items()
    else:
        selected = (
            (key, STRATEGIES[key])
            for key in selected_keys
            if key in STRATEGIES
        )

    blocks = []

    for key, strategy in selected:
        blocks.append(
            f"""
STRATEGY: {key}
NAME: {strategy["name"]}
CATEGORY: {strategy["category"]}
PURPOSE: {strategy["primary_purpose"]}
USE WHEN: {"; ".join(strategy["use_when"])}
DO NOT USE WHEN: {"; ".join(strategy["do_not_use_when"])}
LOCATIONS: {", ".join(strategy["locations"])}
DESIRED RESPONSE: {strategy["desired_response"]}
APPLICATION: {strategy["application"]}
GOOD EXAMPLE: {strategy["good_example"]}
BAD EXAMPLE: {strategy["bad_example"]}
RISKS: {"; ".join(strategy["risks"])}
EVIDENCE: {strategy["evidence_requirements"]}
INTENSITY: {strategy["intensity"]}
REPETITION: {strategy["repetition"]}
""".strip()
        )

    return "\n\n".join(blocks)
