"""Ren Media V2.1 deterministic script validator.

The validator is deliberately conservative.

It does NOT pretend that regex can prove whether a factual claim is true.
Instead it catches observable structural, rhetorical, fabrication, and
governance failures and surfaces factual/psychological claims for review.

V2.1 adds:
- approved-strategy compliance checks
- outline adherence checks
- strategy-role effectiveness signals
- open-loop density checks
- claim-risk detection
- stronger rhetorical-pattern detection
- clearer CRITICAL / WARNING / PASS output

The validator never rewrites the script.
"""

import re

from governance import (
    PERSONAL_EXPERIENCE_FIREWALL,
    PSYCHOLOGY_FIREWALL,
    EMOTIONAL_RULES,
    RHETORICAL_RULES,
    CTA_RULES,
    ETHICAL_RULES,
)
from strategies import STRATEGIES


# ---------------------------------------------------------------------------
# Basic utilities
# ---------------------------------------------------------------------------

def _word_count(text):
    return len(re.findall(r"\b[\w'’-]+\b", text or ""))


def _find(pattern, text, flags=re.I):
    return list(re.finditer(pattern, text or "", flags))


def _normalise(text):
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def _contains_any(text, phrases):
    lowered = _normalise(text)
    return [p for p in phrases if p.lower() in lowered]


def _position_ratio(match, text):
    if not text:
        return 0.0
    return match.start() / max(1, len(text))


def _window_count(pattern, text, window_chars, flags=re.I):
    """Return maximum number of matches inside any rolling character window."""
    matches = _find(pattern, text, flags)

    if not matches:
        return 0

    starts = [m.start() for m in matches]
    maximum = 1

    left = 0
    for right in range(len(starts)):
        while starts[right] - starts[left] > window_chars:
            left += 1
        maximum = max(maximum, right - left + 1)

    return maximum


# ---------------------------------------------------------------------------
# Strategy-map parsing
# ---------------------------------------------------------------------------

def _extract_strategy_keys(strategy_map):
    """Extract approved strategy keys from the editable strategy-map text.

    The UI currently serialises entries like:

        - strategy_key | Strategy Name | role | intensity | ...

    This parser intentionally tolerates small formatting differences.
    """

    if not strategy_map:
        return []

    found = []

    for key in STRATEGIES:
        if re.search(
            rf"\b{re.escape(key)}\b",
            strategy_map,
            re.I,
        ):
            found.append(key)

    return found


def _strategy_evidence_terms(key):
    """Return useful observable signals for a strategy.

    These are NOT proof that the strategy worked.
    They are evidence signals used to identify obviously absent strategies.
    """

    strategy = STRATEGIES.get(key, {})

    terms = []

    # Strategy-specific keywords from the library.
    for keyword in strategy.get("keywords", []):
        terms.append(keyword)

    # A few structural signals are better than keywords alone.
    if key in {"zeigarnik_effect", "curiosity_gaps"}:
        terms.extend([
            "why",
            "how",
            "reason",
            "question",
            "answer",
            "later",
        ])

    elif key == "pattern_interrupts":
        terms.extend([
            "imagine",
            "consider",
            "here's the thing",
            "look at",
            "instead",
        ])

    elif key == "emotional_triggers":
        terms.extend([
            "feel",
            "fear",
            "frustrat",
            "pain",
            "risk",
            "loss",
            "matter",
        ])

    elif key == "self_verification_theory":
        terms.extend([
            "you feel",
            "you may",
            "you've probably",
            "you might",
            "many people",
        ])

    elif key == "choice_architecture":
        terms.extend([
            "option",
            "choice",
            "trade-off",
            "alternative",
            "you can",
        ])

    elif key == "foot_in_the_door_content":
        terms.extend([
            "first",
            "start with",
            "once you accept",
            "the larger implication",
        ])

    elif key == "foot_in_the_door_audience":
        terms.extend([
            "comment",
            "notice",
            "ask yourself",
            "think about",
        ])

    elif key == "reciprocity":
        terms.extend([
            "use this",
            "try this",
            "here's a practical",
            "you can do",
        ])

    elif key == "commitment_consistency":
        terms.extend([
            "try",
            "practice",
            "tonight",
            "today",
            "commit",
        ])

    elif key == "liking":
        terms.extend([
            "relatable",
            "human",
            "honest",
            "mistake",
        ])

    elif key == "scarcity":
        terms.extend([
            "rare",
            "limited",
            "uncommon",
        ])

    elif key == "authority":
        terms.extend([
            "research",
            "study",
            "expert",
            "evidence",
        ])

    elif key == "social_proof":
        terms.extend([
            "people",
            "common",
            "survey",
            "examples",
        ])

    elif key == "point_development":
        terms.extend([
            "because",
            "for example",
            "that means",
            "which means",
            "why this matters",
        ])

    elif key == "point_ordering":
        terms.extend([
            "first",
            "then",
            "more importantly",
            "finally",
            "most importantly",
        ])

    elif key == "zoom_into_the_moment":
        terms.extend([
            "imagine",
            "picture",
            "suppose",
            "you walk",
            "you sit",
            "you look",
        ])

    return list(dict.fromkeys(terms))


def _strategy_effectiveness(script, selected_keys):
    """Produce evidence signals for every approved strategy.

    Important: absence of keyword evidence does NOT prove that the strategy
    failed. It produces a WARNING asking for human review.
    """

    results = []

    lowered = _normalise(script)

    for key in selected_keys:
        strategy = STRATEGIES.get(key)

        if not strategy:
            results.append({
                "key": key,
                "status": "WARNING",
                "message": f"Approved strategy '{key}' is not present in the strategy library.",
            })
            continue

        terms = _strategy_evidence_terms(key)
        matched = [term for term in terms if term.lower() in lowered]

        if matched:
            results.append({
                "key": key,
                "status": "PASS",
                "message": (
                    f"{strategy['name']} has observable execution signals "
                    f"({', '.join(matched[:4])})."
                ),
            })
        else:
            results.append({
                "key": key,
                "status": "WARNING",
                "message": (
                    f"{strategy['name']} was approved but no clear execution "
                    "signal was detected. Review the script manually."
                ),
            })

    return results


# ---------------------------------------------------------------------------
# Outline adherence
# ---------------------------------------------------------------------------

def _outline_sections(outline):
    """Extract likely section labels from the editable outline."""

    if not outline:
        return []

    sections = []

    for line in outline.splitlines():
        line = line.strip()

        if not line:
            continue

        # Existing outline format:
        # [SECTION NAME] -- description
        match = re.match(r"^\[([^\]]+)\]", line)

        if match:
            sections.append(match.group(1).strip())
            continue

        # Also tolerate numbered headings:
        # 1. Hook ...
        match = re.match(r"^\d+\.\s*([^-\n]+)", line)

        if match:
            candidate = match.group(1).strip()
            if candidate:
                sections.append(candidate)

    return sections


def _check_outline_adherence(script, outline):
    """Look for major outline loss.

    Because the final script intentionally contains no headings, this cannot
    prove exact beat-by-beat adherence. It checks whether the outline's major
    concepts appear to have survived.
    """

    if not outline:
        return {
            "status": "WARNING",
            "message": "No approved outline was supplied to the validator.",
        }

    sections = _outline_sections(outline)

    if not sections:
        return {
            "status": "WARNING",
            "message": "The outline format could not be parsed reliably.",
        }

    script_words = set(
        re.findall(r"\b[a-zA-Z]{5,}\b", _normalise(script))
    )

    represented = 0

    for section in sections:
        meaningful_words = [
            w.lower()
            for w in re.findall(r"\b[a-zA-Z]{5,}\b", section)
            if w.lower() not in {
                "section",
                "purpose",
                "content",
                "beat",
                "hook",
                "setup",
                "climax",
                "resolution",
                "outro",
                "cta",
            }
        ]

        if not meaningful_words:
            continue

        overlap = sum(
            1 for word in meaningful_words
            if word in script_words
        )

        if overlap >= max(1, min(2, len(meaningful_words))):
            represented += 1

    coverage = represented / max(1, len(sections))

    if coverage >= 0.65:
        return {
            "status": "PASS",
            "message": (
                f"Major outline concepts appear represented "
                f"({represented}/{len(sections)} detected)."
            ),
        }

    if coverage >= 0.40:
        return {
            "status": "WARNING",
            "message": (
                f"Only {represented}/{len(sections)} major outline concepts "
                "were clearly detected. Review whether approved beats were lost."
            ),
        }

    return {
        "status": "CRITICAL",
        "message": (
            f"Only {represented}/{len(sections)} major outline concepts "
            "were detected. The generated script may have substantially "
            "departed from the approved structure."
        ),
    }


# ---------------------------------------------------------------------------
# Main validator
# ---------------------------------------------------------------------------

def validate_script(
    script,
    target_words=None,
    selected_strategy_keys=None,
    outline=None,
    strategy_map=None,
):
    critical = []
    warnings = []
    passed = []

    script = script or ""

    words = _word_count(script)

    # -----------------------------------------------------------------------
    # 1. Length
    # -----------------------------------------------------------------------

    if target_words:
        ratio = words / max(1, target_words)

        if ratio < 0.90 or ratio > 1.10:
            critical.append(
                f"Length is {words} words versus a target of "
                f"{target_words} (outside ±10%)."
            )
        else:
            passed.append("Length is within ±10% of target.")

    # -----------------------------------------------------------------------
    # 2. Personal-experience firewall
    # -----------------------------------------------------------------------

    personal_patterns = [
        r"\bI remember\b",
        r"\bI used to\b",
        r"\bI spent years\b",
        r"\bin my life\b",
        r"\bin my relationship\b",
        r"\bmy relationship\b",
        r"\bmy marriage\b",
        r"\bmy clients?\b",
        r"\bmy patients?\b",
        r"\bwhen I was\b",
        r"\bI once\b",
        r"\bI learned this\b",
        r"\bI made this mistake\b",
        r"\bI've made this mistake\b",
    ]

    personal_matches = []

    for pattern in personal_patterns:
        personal_matches.extend(_find(pattern, script))

    if personal_matches:
        critical.append(
            "Possible fabricated first-person experience or biography. "
            "Every first-person lived claim must come from supplied source material."
        )
    else:
        passed.append(
            "No obvious fabricated first-person lived-experience pattern detected."
        )

    # -----------------------------------------------------------------------
    # 3. Numeric / evidence-sensitive claims
    # -----------------------------------------------------------------------

    percentages = _find(
        r"\b\d+(?:\.\d+)?\s*%"
        r"|\b(?:ninety|eighty|seventy|sixty|fifty|forty|thirty|twenty)"
        r"\s*percent\b",
        script,
    )

    statistics = _find(
        r"\b(?:\d+(?:\.\d+)?\s*(?:times|people|couples|participants|"
        r"years|months|days|studies))\b",
        script,
    )

    if percentages or statistics:
        warnings.append(
            "Specific numerical/statistical claims detected. "
            "Verify each claim against a real source before publication."
        )
    else:
        passed.append("No obvious precise numerical claims detected.")

    # -----------------------------------------------------------------------
    # 4. Strong causal / certainty language
    # -----------------------------------------------------------------------

    causal = _find(
        r"\b(?:causes?|caused|proves?|proven|guarantees?|guaranteed|"
        r"will make you|makes you|always leads to|will inevitably|"
        r"ensures?|ensured|prevents?)\b",
        script,
    )

    if causal:
        warnings.append(
            "Strong causal or certainty language detected. "
            "Check whether the evidence supports the strength of each claim."
        )
    else:
        passed.append("No obvious strong causal/guarantee language detected.")

    # -----------------------------------------------------------------------
    # 5. Psychology / physiology claims
    # -----------------------------------------------------------------------

    physiology = _find(
        r"\b(?:heart rate|nervous system|cortisol|dopamine|"
        r"immune system|physiological|physiology|chemical|"
        r"brain|amygdala|nervous system|hormone|hormonal)\b",
        script,
    )

    if physiology:
        warnings.append(
            "Psychology/physiology terminology detected. "
            "Verify that any mechanism described is supported and "
            "not presented as universal certainty."
        )

    # -----------------------------------------------------------------------
    # 6. Psychology perfume / named-technique misuse
    # -----------------------------------------------------------------------

    technique_jargon = _find(
        r"\b(?:open loop|macro loop|micro loop|rehook|pattern interrupt|"
        r"foot[- ]in[- ]the[- ]door|Zeigarnik|Cialdini|nudge|"
        r"choice architecture|self[- ]verification|social proof|"
        r"reciprocity|commitment and consistency)\b",
        script,
    )

    if technique_jargon:
        critical.append(
            "Psychology/storytelling technique terminology appears in the "
            "narration. Execute the technique; do not name the technique to viewers."
        )
    else:
        passed.append(
            "No obvious psychology/storytelling technique jargon detected in narration."
        )

    # -----------------------------------------------------------------------
    # 7. Rhetorical repetition
    # -----------------------------------------------------------------------

    it_is_not = _find(
        r"\b(?:it isn't|it is not)\b"
        r"[^.!?]{0,100}"
        r"\b(?:it's|it is)\b",
        script,
    )

    truth_is = _find(r"\bthe truth is\b", script)

    heres_the = _find(
        r"\bbut here's (?:the|what|why|where)\b",
        script,
    )

    this_is = _find(
        r"\bthis is (?:why|where|the moment|the reason)\b",
        script,
    )

    if len(it_is_not) > 3:
        warnings.append(
            "The 'It isn't X, it's Y' construction is repeated more than three times."
        )

    if len(truth_is) > 2:
        warnings.append(
            "The 'The truth is...' construction is repeated more than twice."
        )

    if len(heres_the) > 2:
        warnings.append(
            "Repeated 'But here's...' transition pattern detected."
        )

    if len(this_is) > 3:
        warnings.append(
            "Repeated 'This is...' rhetorical transition pattern detected."
        )

    # -----------------------------------------------------------------------
    # 8. Open-loop density
    # -----------------------------------------------------------------------

    loop_patterns = [
        r"\byou(?:'ll| will) (?:find out|learn|discover|see)\b",
        r"\bthe answer comes later\b",
        r"\bthere's (?:one|another|a) (?:reason|thing|problem)\b",
        r"\bbut we'll get to that\b",
        r"\bwe'll come back to that\b",
        r"\bhere's what happens next\b",
        r"\bthe real reason\b",
        r"\bthe answer is coming\b",
    ]

    loop_count = 0

    for pattern in loop_patterns:
        loop_count += len(_find(pattern, script))

    if loop_count > 8:
        warnings.append(
            f"Approximately {loop_count} open-loop announcement signals detected. "
            "Review for promise fatigue and unresolved questions."
        )

    # Roughly 90 seconds at 150 WPM = 225 words.
    dense_loop_max = max(
        _window_count(
            "|".join(f"(?:{p})" for p in loop_patterns),
            script,
            225 * 6,
        ),
        0,
    )

    if dense_loop_max > 2:
        warnings.append(
            "More than two open-loop announcement signals occur within a "
            "rough 90-second window. Review for excessive suspense stacking."
        )

    # -----------------------------------------------------------------------
    # 9. CTA governance
    # -----------------------------------------------------------------------

    cta = _find(
        r"\b(?:subscribe|hit the subscribe button|"
        r"like and subscribe|comment below|"
        r"type ['\"]?(?:yes|no)['\"]?|"
        r"let me know in the comments)\b",
        script,
    )

    if cta:
        early_ctas = [
            m for m in cta
            if _position_ratio(m, script) < 0.70
        ]

        if early_ctas:
            warnings.append(
                "A CTA appears before the final third. "
                "Check that it does not interrupt unresolved narrative tension."
            )
        else:
            passed.append("Main CTA appears late in the script.")

        if len(cta) > 2:
            warnings.append(
                f"{len(cta)} CTA/engagement prompts detected. "
                "Review whether the audience is being asked too often."
            )

    # -----------------------------------------------------------------------
    # 10. Emotional intensity
    # -----------------------------------------------------------------------

    emotional = _find(
        r"\b(?:terrifying|terrified|destroy|destroying|destroyed|"
        r"dead|death|poison|poisonous|doomed|catastrophic|"
        r"life[- ]?changing|you won't stand a chance|"
        r"you'll regret|nightmare|horrifying|disaster)\b",
        script,
    )

    if len(emotional) >= 8:
        critical.append(
            "High-intensity language is unusually concentrated. "
            "Reduce escalation unless the topic genuinely warrants it."
        )
    elif len(emotional) >= 5:
        warnings.append(
            "High-intensity language appears frequently. "
            "Check that emotional escalation is balanced with explanation."
        )

    # -----------------------------------------------------------------------
    # 11. Personal manipulation / ethical warning signals
    # -----------------------------------------------------------------------

    manipulation = _find(
        r"\b(?:act now|before it's too late|don't miss out|"
        r"you have no choice|only smart people|"
        r"everyone else is doing it|"
        r"if you don't, you'll regret it)\b",
        script,
    )

    if manipulation:
        warnings.append(
            "Potential artificial urgency, coercive framing, or manufactured "
            "social pressure detected. Review against the ethical guardrails."
        )

    # -----------------------------------------------------------------------
    # 12. Approved strategy effectiveness
    # -----------------------------------------------------------------------

    if selected_strategy_keys is None and strategy_map:
        selected_strategy_keys = _extract_strategy_keys(strategy_map)

    selected_strategy_keys = selected_strategy_keys or []

    if selected_strategy_keys:
        strategy_results = _strategy_effectiveness(
            script,
            selected_strategy_keys,
        )

        for result in strategy_results:
            if result["status"] == "WARNING":
                warnings.append(result["message"])
            elif result["status"] == "PASS":
                passed.append(result["message"])

    else:
        strategy_results = []

        warnings.append(
            "No approved strategy keys were supplied to the validator. "
            "Strategy effectiveness cannot be checked."
        )

    # -----------------------------------------------------------------------
    # 13. Outline adherence
    # -----------------------------------------------------------------------

    outline_result = _check_outline_adherence(script, outline)

    if outline_result["status"] == "CRITICAL":
        critical.append(outline_result["message"])
    elif outline_result["status"] == "WARNING":
        warnings.append(outline_result["message"])
    else:
        passed.append(outline_result["message"])

    # -----------------------------------------------------------------------
    # 14. Final status
    # -----------------------------------------------------------------------

    if critical:
        status = "CRITICAL"
    elif warnings:
        status = "WARNING"
    else:
        status = "PASS"

    if not critical:
        passed.append(
            "No deterministic critical failure detected by the validator."
        )

    return {
        "status": status,
        "critical": critical,
        "warnings": warnings,
        "passed": passed,
        "word_count": words,
        "strategy_results": strategy_results,
        "outline_result": outline_result,
        "selected_strategy_keys": selected_strategy_keys,
    }
