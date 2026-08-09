# =============================================================================
# PSYCHOLOGY TOOLKIT
# This is the ONLY file you need to touch to add a new psychological /
# storytelling technique. Add a new line in the format:
#     "key": "Name -- one or two sentences describing how to use it."
# Nothing in main.py needs to change for a new technique to start being used --
# it gets pulled in automatically.
# =============================================================================

PSYCHOLOGY_TECHNIQUES = {
    "zeigarnik_effect": "Zeigarnik Effect (macro open loop) -- plant one compelling question or tease early that only fully resolves near the end. The brain remembers unfinished business far better than finished business.",
    "pattern_interrupts": "Pattern Interrupts -- roughly every 60-90 seconds of runtime, insert a tone shift, a rhetorical question, or an unexpected turn to reset viewer attention.",
    "curiosity_gaps": "Curiosity Gaps (micro-loops) -- while the main open loop stays open, open and close smaller curiosity gaps throughout so momentum never fully rests.",
    "emotional_triggers": "Emotional Triggers -- connect ideas to a specific emotion (surprise, nostalgia, pride, mild injustice) since emotion carries a message further than the message alone.",
    "foot_in_the_door_content": "Foot-in-the-Door (content) -- early sections introduce small, easy-to-agree-with ideas; later sections build on that agreement to land bigger, more surprising claims.",
    "foot_in_the_door_audience": "Foot-in-the-Door (audience) -- place one small, low-friction ask of the viewer (guess an answer, comment one word) roughly two-thirds through, which primes them to say yes to the bigger subscribe ask at the end.",
    "self_verification_theory": "Self-Verification -- before introducing a new idea, validate the viewer's current experience or struggle so they feel seen and correctly understood; this builds the trust needed for them to accept what comes next.",
    "choice_architecture": "Choice Architecture (Nudge) -- don't tell the viewer what to conclude; frame the surrounding context so their own reasoning arrives at the intended conclusion.",
    "authority_and_social_proof": "Authority & Social Proof -- reinforce the core argument by referencing that experts or many people generally hold this view. IMPORTANT: never invent a specific named study, researcher, or statistic to do this -- use soft, generic phrasing only ('many psychologists point to...'), since a fabricated citation is worse for credibility than no citation at all.",

    # Add new techniques below this line:
}
