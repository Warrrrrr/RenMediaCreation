# =============================================================================
# PSYCHOLOGY TOOLKIT
# This is the ONLY file you need to touch to add a new psychological /
# storytelling technique. Add a new entry in this format:
#     "key": {
#         "name": "Technique Name",
#         "explanation": "What it is and why it works.",
#         "example": "A concrete example of it in use.",
#     }
# Nothing in main.py needs to change for a new technique to start being used --
# it gets pulled in automatically.
# =============================================================================

PSYCHOLOGY_TECHNIQUES = {

    "zeigarnik_effect": {
        "name": "Zeigarnik Effect (Macro Open Loop)",
        "explanation": "People remember unfinished tasks far better than finished ones. An unresolved question creates mental tension that keeps someone engaged until it gets resolved.",
        "example": "Plant a question early -- \"By the end of this, you'll know the one question her subconscious asks that decides if you're a partner or a friend\" -- and don't answer it until near the end.",
    },

    "pattern_interrupts": {
        "name": "Pattern Interrupts",
        "explanation": "Attention settles into a predictable rhythm and drifts. A sudden shift in tone, rhythm, or subject jolts it back, roughly every 60-90 seconds of runtime.",
        "example": "Right when an explanation starts feeling like a lecture, cut in with: \"And that's exactly where it goes wrong for most guys.\"",
    },

    "curiosity_gaps": {
        "name": "Curiosity Gaps (Micro-Loops)",
        "explanation": "Show enough to make someone want more, withhold enough that they keep watching to close the gap themselves. Used in small doses throughout, alongside the one big Zeigarnik loop.",
        "example": "\"There's one specific moment where her interest either locks in or quietly disappears -- and it's not the moment you'd guess.\" (don't reveal which moment yet)",
    },

    "emotional_triggers": {
        "name": "Emotional Triggers",
        "explanation": "Connect an idea to a specific emotion -- surprise, nostalgia, pride, mild injustice -- since emotion carries a message further than the message alone.",
        "example": "\"The frustrating part is most guys correct the wrong thing entirely -- so the harder they try, the worse it gets.\" (mild injustice/frustration)",
    },

    "foot_in_the_door_content": {
        "name": "Foot-in-the-Door (Content)",
        "explanation": "Early sections introduce small, easy-to-agree-with ideas; later sections build on that agreement to land bigger, more surprising claims.",
        "example": "Start with something almost everyone agrees with (\"First dates are nerve-wracking\") before building to the bigger claim (\"and that nervous energy is the exact thing sabotaging you\").",
    },

    "foot_in_the_door_audience": {
        "name": "Foot-in-the-Door (Audience)",
        "explanation": "Place one small, low-friction ask of the viewer roughly two-thirds through -- a small 'yes' primes them to say yes to the bigger subscribe ask at the end.",
        "example": "\"Comment 'yes' if you've felt this exact thing happen to you.\"",
    },

    "self_verification_theory": {
        "name": "Self-Verification Theory",
        "explanation": "Before introducing a new idea, validate the viewer's current experience or struggle so they feel seen and correctly understood -- this builds the trust needed for them to accept what comes next.",
        "example": "\"You've probably done everything right on paper and still watched it fall apart -- that's not you doing something wrong. That's a completely different problem.\"",
    },

    "choice_architecture": {
        "name": "Choice Architecture (Nudge)",
        "explanation": "Don't tell the viewer what to conclude -- frame the surrounding context so their own reasoning arrives at the intended conclusion.",
        "example": "\"One version of you replies in three seconds, every time. Another version has a life that occasionally makes her wait. Only one of those people gets missed.\" (never says \"stop texting back so fast\" directly)",
    },

    "scene_zoom_technique": {
        "name": "Zoom Into the Moment",
        "explanation": "When telling a scene or example, drop the wide 'helicopter view' summary and zoom into one specific moment using five elements: Location (name where you physically are), Actions (active verbs -- what's physically happening), Thoughts (raw, unfiltered internal monologue, not formal), Emotions (show the physical reaction, not just naming the feeling), and Dialogue (quote what was actually said).",
        "example": "Not \"she seemed disappointed\" but: \"She's standing in the doorway, one hand still on the frame, and she just says, 'Oh. I thought you'd remember.' Then she looks down at her phone instead of at you.\"",
    },

    # --- Robert Cialdini's six principles of influence ---
    # Authority and Social Proof carry a real fabrication risk (see caution
    # baked into each) since "invoking authority" in text tends to tempt
    # invented-sounding citations. The other four are lower-risk.

    "cialdini_reciprocity": {
        "name": "Reciprocity (Cialdini)",
        "explanation": "People feel obligated to return value once they've received it first. Give the viewer something genuinely useful early, for free, before any ask.",
        "example": "Deliver one complete, standalone insight in the first third of the video that works even if someone stops watching there -- the value comes before the ask, not after.",
    },

    "cialdini_commitment_consistency": {
        "name": "Commitment & Consistency (Cialdini)",
        "explanation": "Once someone states or commits to a small position, they feel internal pressure to stay consistent with it going forward.",
        "example": "The audience foot-in-the-door comment ask doubles as this -- once someone has publicly typed 'yes,' they're primed to keep agreeing with the direction the rest of the video takes.",
    },

    "cialdini_liking": {
        "name": "Liking (Cialdini)",
        "explanation": "People are more persuaded by voices they like or relate to. A brief, relatable, slightly self-deprecating admission builds this before the argument lands.",
        "example": "\"I got this completely wrong for years before I understood it\" -- one line, not a full personal-story detour.",
    },

    "cialdini_scarcity": {
        "name": "Scarcity (Cialdini)",
        "explanation": "Things seem more valuable when they're rare, hard to find, or not widely known -- pairs naturally with the Forbidden and Warning title frames.",
        "example": "\"This is the one adjustment almost nobody teaches, because it's not the flashy part.\"",
    },

    "cialdini_authority": {
        "name": "Authority (Cialdini)",
        "explanation": "People defer to credible expertise. IMPORTANT: never invent a specific named study, researcher, or credential to manufacture this -- use soft, generic phrasing only. A fabricated citation is worse for credibility than none at all.",
        "example": "\"Most people who study attraction professionally will tell you the same thing\" -- not \"a Harvard study found...\" unless that study is real and verifiable.",
    },

    "cialdini_social_proof": {
        "name": "Social Proof (Cialdini)",
        "explanation": "People look to others' behavior to decide their own. IMPORTANT: never invent specific statistics or numbers to manufacture this -- use soft, generic phrasing only.",
        "example": "\"This pattern shows up constantly, in relationship after relationship\" -- not \"87% of women reported...\" unless that statistic is real and verifiable.",
    },

    # Add new techniques below this line:
}
