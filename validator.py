"""
Ren Media V2 — Script Validator

Purpose:
- Inspect generated scripts before final approval.
- Detect high-risk fabrication and reasoning failures.
- Check strategy usage.
- Check structural compliance.
- Check rhetorical and emotional-pattern problems.

IMPORTANT:
This module does NOT rewrite the script.

It produces a structured validation request/result.

Gemini is used for semantic inspection because several checks
cannot be reliably performed with simple string matching.

Deterministic checks are also included where possible.
"""

import json
import re

from governance import (
    PERSONAL_EXPERIENCE_FIREWALL,
    CLAIM_TYPES,
    CLAIM_CALIBRATION_RULES,
    PSYCHOLOGY_CLAIM_FIREWALL,
    PSYCHOLOGY_PERFUME_CHECK,
    EMOTIONAL_INTENSITY,
    RHETORICAL_PATTERN_CONTROL,
    OPEN_LOOP_GOVERNANCE,
    CTA_GOVERNANCE,
    ETHICAL_GUARDRAILS,
    SCRIPT_STRUCTURE_GOVERNANCE,
    STRATEGY_GOVERNANCE,
    VALIDATION_SEVERITY,
)


# ============================================================
# VALIDATOR VERSION
# ============================================================

VALIDATOR_VERSION = "2.0"


# ============================================================
# RESULT FORMAT
# ============================================================

RESULT_SCHEMA = {
    "validator_version": VALIDATOR_VERSION,

    "overall_status": (
        "PASS | WARNING | CRITICAL"
    ),

    "critical": [],

    "warnings": [],

    "passes": [],

    "claims": [],

    "strategy_effectiveness": [],

    "open_loops": [],

    "rhetorical_patterns": [],

    "word_count": {
        "actual": 0,
        "target": 0,
        "within_tolerance": True,
    },
}


# ============================================================
# BASIC TEXT HELPERS
# ============================================================

def normalize_script(script):
    """Return a safe string representation of the script."""

    if script is None:
        return ""

    return str(script).strip()


def word_count(script):
    """Count words conservatively."""

    script = normalize_script(script)

    if not script:
        return 0

    return len(
        re.findall(
            r"\b[\w'-]+\b",
            script,
            flags=re.UNICODE,
        )
    )


def count_pattern(script, pattern):
    """
    Case-insensitive occurrence count.

    This is intentionally approximate.
    Semantic validation happens separately.
    """

    script = normalize_script(script)

    if not script:
        return 0

    return len(
        re.findall(
            re.escape(pattern),
            script,
            flags=re.IGNORECASE,
        )
    )


# ============================================================
# WORD COUNT VALIDATION
# ============================================================

def validate_word_count(
    script,
    target_words,
    tolerance=0.10,
):
    """
    Check whether the generated script is within the
    allowed word-count tolerance.

    Returns a structured result.
    """

    actual = word_count(script)

    try:
        target = int(target_words)
    except (TypeError, ValueError):
        target = 0

    if target <= 0:
        return {
            "actual": actual,
            "target": target,
            "within_tolerance": True,
            "status": "PASS",
            "reason": (
                "No valid target word count was supplied."
            ),
        }

    minimum = int(
        target * (1 - tolerance)
    )

    maximum = int(
        target * (1 + tolerance)
    )

    within = (
        minimum <= actual <= maximum
    )

    return {
        "actual": actual,
        "target": target,
        "minimum": minimum,
        "maximum": maximum,
        "within_tolerance": within,
        "status": (
            "PASS"
            if within
            else "WARNING"
        ),
        "reason": (
            f"Actual word count is {actual}; "
            f"target is {target}; "
            f"allowed range is {minimum}-{maximum}."
        ),
    }


# ============================================================
# DETERMINISTIC PERSONAL EXPERIENCE CHECK
# ============================================================

PERSONAL_EXPERIENCE_PATTERNS = [

    r"\bi remember\b",

    r"\bi used to\b",

    r"\bin my own life\b",

    r"\bin my life\b",

    r"\bwhen i was\b",

    r"\bwhen i first\b",

    r"\bi spent years\b",

    r"\bi've spent years\b",

    r"\bi have spent years\b",

    r"\bi learned this the hard way\b",

    r"\bi made this mistake\b",

    r"\bi made the same mistake\b",

    r"\bi've made this mistake\b",

    r"\bi have made this mistake\b",

    r"\bi've seen this\b",

    r"\bi have seen this\b",

    r"\bin my experience\b",

    r"\bfrom my experience\b",

    r"\bmy clients\b",

    r"\bmy patients\b",

    r"\bmy students\b",

    r"\bpeople i've coached\b",

    r"\bpeople i coached\b",
]


def detect_personal_experience_language(script):
    """
    Detect likely first-person experiential claims.

    IMPORTANT:
    Detection is not automatically proof of fabrication.

    The user may legitimately provide personal source material.

    Therefore this function flags occurrences for review.
    """

    script = normalize_script(script)

    findings = []

    for pattern in PERSONAL_EXPERIENCE_PATTERNS:

        matches = re.finditer(
            pattern,
            script,
            flags=re.IGNORECASE,
        )

        for match in matches:

            start = max(
                0,
                match.start() - 100,
            )

            end = min(
                len(script),
                match.end() + 180,
            )

            excerpt = script[start:end].strip()

            findings.append({
                "type":
                    "possible_personal_experience",

                "matched_pattern":
                    pattern,

                "excerpt":
                    excerpt,

                "severity":
                    "CRITICAL",
            })

    return findings


# ============================================================
# RHETORICAL PATTERN CHECK
# ============================================================

def detect_rhetorical_patterns(script):
    """
    Detect repeated rhetorical templates.

    The purpose is not to ban a sentence construction.

    It is to identify excessive repetition.
    """

    script = normalize_script(script)

    findings = []

    for item in RHETORICAL_PATTERN_CONTROL[
        "patterns_to_monitor"
    ]:

        pattern = item["pattern"]

        count = count_pattern(
            script,
            pattern,
        )

        if count >= 3:

            findings.append({
                "pattern": pattern,

                "count": count,

                "severity": "WARNING",

                "reason": item["rule"],
            })

        elif count > 0:

            findings.append({
                "pattern": pattern,

                "count": count,

                "severity": "PASS",

                "reason":
                    "Pattern detected within normal usage range.",
            })

    return findings


# ============================================================
# OPEN LOOP HEURISTIC
# ============================================================

OPEN_LOOP_MARKERS = [

    "but there's one problem",

    "but here's what",

    "the real reason",

    "and this is where",

    "but there's something else",

    "we'll come back to that",

    "later i'll show you",

    "in a moment you'll see",

    "the answer comes later",

    "but before we get there",

    "here's where it gets interesting",
]


def detect_open_loop_markers(script):
    """
    Approximate open-loop detection.

    This is not a semantic proof.

    Gemini validation will perform the deeper inspection.
    """

    script = normalize_script(script)

    findings = []

    for marker in OPEN_LOOP_MARKERS:

        count = count_pattern(
            script,
            marker,
        )

        if count > 0:

            findings.append({
                "marker": marker,
                "count": count,
                "severity": "WARNING"
                if count >= 3
                else "PASS",
            })

    return findings


# ============================================================
# ETHICAL KEYWORD CHECK
# ============================================================

ETHICAL_RISK_PATTERNS = [

    r"\bguaranteed\b",

    r"\bguarantee\b",

    r"\b100% guaranteed\b",

    r"\bthis will always\b",

    r"\byou will definitely\b",

    r"\bscientifically proven\b",

    r"\bproven to work for everyone\b",

    r"\bact now or regret it\b",

    r"\bonly today\b",

    r"\blast chance\b",
]


def detect_obvious_ethics_risks(script):
    """
    Detect obvious high-risk persuasion language.

    This does not replace semantic ethical review.
    """

    script = normalize_script(script)

    findings = []

    for pattern in ETHICAL_RISK_PATTERNS:

        matches = list(
            re.finditer(
                pattern,
                script,
                flags=re.IGNORECASE,
            )
        )

        for match in matches:

            start = max(
                0,
                match.start() - 80,
            )

            end = min(
                len(script),
                match.end() + 120,
            )

            findings.append({
                "pattern":
                    match.group(0),

                "excerpt":
                    script[start:end].strip(),

                "severity":
                    "CRITICAL",
            })

    return findings


# ============================================================
# PSYCHOLOGY TERM CHECK
# ============================================================

PSYCHOLOGY_TERMS = [

    "zeigarnik effect",

    "self-verification",

    "social proof",

    "reciprocity",

    "commitment and consistency",

    "commitment consistency",

    "scarcity",

    "authority",

    "liking",

    "choice architecture",

    "nudge",

    "cognitive bias",

    "confirmation bias",

    "availability heuristic",

    "anchoring",

    "loss aversion",

    "halo effect",

    "mere exposure effect",

    "dunning-kruger",

    "dunning kruger",

]


def detect_psychology_terms(script):
    """
    Identify psychology terminology for semantic review.

    Merely mentioning a term is NOT a failure.
    """

    script = normalize_script(script)

    findings = []

    for term in PSYCHOLOGY_TERMS:

        count = count_pattern(
            script,
            term,
        )

        if count > 0:

            findings.append({
                "term": term,
                "count": count,
                "requires_explanation_review": True,
            })

    return findings


# ============================================================
# STRATEGY EFFECTIVENESS PROMPT
# ============================================================

def build_strategy_effectiveness_prompt(
    script,
    strategy_map,
):
    """
    Build a Gemini instruction for checking whether the
    approved strategies actually performed their intended jobs.
    """

    selected = strategy_map.get(
        "selected",
        [],
    )

    strategy_text = []

    for item in selected:

        strategy_text.append(
            {
                "strategy":
                    item.get("strategy"),

                "name":
                    item.get("name"),

                "role":
                    item.get("role"),

                "intensity":
                    item.get("intensity"),

                "desired_response":
                    item.get(
                        "desired_response"
                    ),
            }
        )

    payload = {
        "selected_strategies":
            strategy_text,

        "script":
            normalize_script(script),

        "instruction": (
            "For each approved strategy, determine whether "
            "the script actually uses it for its assigned role. "
            "Do not reward mere terminology. "
            "A strategy passes only when its intended function "
            "is visible in the writing."
        ),

        "required_fields": [
            "strategy",
            "used",
            "evidence",
            "effectiveness",
            "problem",
        ],
    }

    return json.dumps(
        payload,
        indent=2,
        ensure_ascii=False,
    )


# ============================================================
# MASTER VALIDATION PROMPT
# ============================================================

def build_validation_prompt(
    script,
    strategy_map,
    outline="",
    topic="",
    audience="",
    objective="",
    target_words=0,
):
    """
    Construct the semantic validation request.

    Gemini should inspect the script.

    It must NOT rewrite it.
    """

    governance = {

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

        "rhetorical_patterns":
            RHETORICAL_PATTERN_CONTROL,

        "open_loops":
            OPEN_LOOP_GOVERNANCE,

        "cta":
            CTA_GOVERNANCE,

        "ethics":
            ETHICAL_GUARDRAILS,

        "structure":
            SCRIPT_STRUCTURE_GOVERNANCE,

        "strategy":
            STRATEGY_GOVERNANCE,
    }

    validation_instruction = """
You are the Ren Media V2 script validator.

Your job is to INSPECT the supplied script.

You are NOT the writer.

Do NOT rewrite the script.

Do NOT improve the script.

Do NOT silently correct mistakes.

Identify problems precisely so another stage or the human
can decide what to do.

You must distinguish between:

CRITICAL
A serious integrity, fabrication, safety, deception, or
major reasoning failure.

WARNING
A quality problem requiring review but not necessarily
making the script unusable.

PASS
No detected problem in that category.

IMPORTANT:

1. Never assume a statistic is true merely because it sounds
   plausible.

2. Never assume a psychological claim is true merely because
   it uses scientific terminology.

3. Treat first-person experiences as potentially fabricated
   unless explicitly supplied as source material.

4. Distinguish correlation from causation.

5. Distinguish research findings from interpretations.

6. Do not reward psychological terminology simply because
   it appears sophisticated.

7. Check whether every approved strategy actually performs
   its assigned role.

8. Check whether open loops eventually receive meaningful
   payoffs.

9. Check whether rhetorical patterns are becoming repetitive.

10. Check whether emotional intensity varies naturally.

11. Check whether the CTA interrupts unresolved narrative
    tension.

12. Check whether persuasion remains honest.

13. Do not invent sources to justify your validation.

14. Do not make claims about evidence that was not supplied.

Return JSON only.

Required top-level fields:

{
  "overall_status": "PASS | WARNING | CRITICAL",

  "critical": [],

  "warnings": [],

  "passes": [],

  "claims": [],

  "strategy_effectiveness": [],

  "open_loops": [],

  "rhetorical_patterns": [],

  "emotional_intensity": {},

  "cta": {},

  "ethics": {},

  "structure": {},

  "word_count": {}
}

Each critical/warning finding should contain:

{
  "type": "",
  "location": "",
  "problem": "",
  "why_it_matters": "",
  "recommended_action": ""
}

Do not rewrite the offending passage.
"""

    payload = {

        "instruction":
            validation_instruction,

        "video_context": {

            "topic":
                topic,

            "audience":
                audience,

            "objective":
                objective,

            "target_words":
                target_words,
        },

        "approved_outline":
            outline,

        "approved_strategy_map":
            strategy_map,

        "governance":
            governance,

        "script":
            normalize_script(script),
    }

    return json.dumps(
        payload,
        indent=2,
        ensure_ascii=False,
    )


# ============================================================
# RESULT NORMALIZATION
# ============================================================

def normalize_validation_result(result):
    """
    Normalize Gemini's response into the expected structure.

    If Gemini returns a dictionary, preserve its useful fields.

    If it returns malformed data, return a safe failure result
    rather than pretending validation succeeded.
    """

    if not isinstance(result, dict):

        return {
            "validator_version":
                VALIDATOR_VERSION,

            "overall_status":
                "CRITICAL",

            "critical": [
                {
                    "type":
                        "validator_output_error",

                    "location":
                        "validator",

                    "problem":
                        "Validator returned an invalid result.",

                    "why_it_matters":
                        "The script cannot be treated as validated.",

                    "recommended_action":
                        "Run validation again.",
                }
            ],

            "warnings": [],

            "passes": [],

            "claims": [],

            "strategy_effectiveness": [],

            "open_loops": [],

            "rhetorical_patterns": [],

            "emotional_intensity": {},

            "cta": {},

            "ethics": {},

            "structure": {},

            "word_count": {},
        }

    normalized = dict(
        RESULT_SCHEMA
    )

    normalized.update(result)

    normalized[
        "validator_version"
    ] = VALIDATOR_VERSION

    return normalized


# ============================================================
# LOCAL PRECHECK
# ============================================================

def run_local_precheck(
    script,
    target_words=0,
):
    """
    Run inexpensive deterministic checks before Gemini.

    These checks are intentionally conservative.

    They identify things that are obvious enough to flag locally.
    They do not claim to understand the entire script.
    """

    script = normalize_script(script)

    critical = []
    warnings = []
    passes = []

    # --------------------------------------------------------
    # Word count
    # --------------------------------------------------------

    length_result = validate_word_count(
        script,
        target_words,
    )

    if (
        length_result["status"]
        == "WARNING"
    ):

        warnings.append({
            "type":
                "word_count",

            "location":
                "entire script",

            "problem":
                length_result["reason"],

            "why_it_matters":
                "Large deviations can affect pacing and delivery.",

            "recommended_action":
                "Adjust the script length before final approval.",
        })

    else:

        passes.append({
            "type":
                "word_count",

            "reason":
                length_result["reason"],
        })

    # --------------------------------------------------------
    # Personal experience
    # --------------------------------------------------------

    experience_findings = (
        detect_personal_experience_language(
            script
        )
    )

    if experience_findings:

        critical.extend(
            [
                {
                    "type":
                        finding["type"],

                    "location":
                        "detected first-person passage",

                    "problem":
                        (
                            "Possible personal experience "
                            "claim detected."
                        ),

                    "why_it_matters":
                        (
                            "The system must not invent "
                            "the narrator's experiences."
                        ),

                    "recommended_action":
                        (
                            "Verify that the experience "
                            "was supplied as source material."
                        ),

                    "excerpt":
                        finding["excerpt"],
                }

                for finding
                in experience_findings
            ]
        )

    else:

        passes.append({
            "type":
                "personal_experience",

            "reason":
                "No obvious first-person experience markers detected.",
        })

    # --------------------------------------------------------
    # Ethical risk
    # --------------------------------------------------------

    ethics_findings = (
        detect_obvious_ethics_risks(
            script
        )
    )

    if ethics_findings:

        critical.extend(
            [
                {
                    "type":
                        "obvious_persuasion_risk",

                    "location":
                        "detected passage",

                    "problem":
                        (
                            f"Potentially misleading persuasion "
                            f"language detected: "
                            f"{finding['pattern']}"
                        ),

                    "why_it_matters":
                        (
                            "The system should not manufacture "
                            "certainty or urgency."
                        ),

                    "recommended_action":
                        (
                            "Review the claim and remove "
                            "unsupported certainty or urgency."
                        ),

                    "excerpt":
                        finding["excerpt"],
                }

                for finding
                in ethics_findings
            ]
        )

    # --------------------------------------------------------
    # Rhetorical patterns
    # --------------------------------------------------------

    rhetorical_findings = (
        detect_rhetorical_patterns(
            script
        )
    )

    for finding in rhetorical_findings:

        if finding["severity"] == "WARNING":

            warnings.append({
                "type":
                    "rhetorical_repetition",

                "location":
                    "multiple locations",

                "problem":
                    (
                        f"The pattern "
                        f"'{finding['pattern']}' "
                        f"appears {finding['count']} times."
                    ),

                "why_it_matters":
                    (
                        "Repeated templates can make the "
                        "script feel formulaic."
                    ),

                "recommended_action":
                    (
                        "Rewrite some instances using "
                        "different sentence structures."
                    ),
            })

    # --------------------------------------------------------
    # Psychology terms
    # --------------------------------------------------------

    psychology_findings = (
        detect_psychology_terms(
            script
        )
    )

    if psychology_findings:

        warnings.append({
            "type":
                "psychology_review",

            "location":
                "multiple locations",

            "problem":
                (
                    "Psychology terminology was detected "
                    "and requires semantic review."
                ),

            "why_it_matters":
                (
                    "A named concept should contribute "
                    "real explanatory value."
                ),

            "recommended_action":
                (
                    "Verify that each concept is explained "
                    "and materially improves understanding."
                ),

            "terms":
                psychology_findings,
        })

    # --------------------------------------------------------
    # Open loops
    # --------------------------------------------------------

    loop_findings = (
        detect_open_loop_markers(
            script
        )
    )

    for finding in loop_findings:

        if finding["severity"] == "WARNING":

            warnings.append({
                "type":
                    "open_loop_density",

                "location":
                    "multiple locations",

                "problem":
                    (
                        f"The marker "
                        f"'{finding['marker']}' "
                        f"appears {finding['count']} times."
                    ),

                "why_it_matters":
                    (
                        "Too many unresolved promises can "
                        "make the viewer feel manipulated "
                        "or confused."
                    ),

                "recommended_action":
                    (
                        "Review whether every loop has "
                        "a meaningful payoff."
                    ),
            })

    # --------------------------------------------------------
    # Overall local status
    # --------------------------------------------------------

    if critical:

        overall_status = "CRITICAL"

    elif warnings:

        overall_status = "WARNING"

    else:

        overall_status = "PASS"

    return {

        "validator_version":
            VALIDATOR_VERSION,

        "overall_status":
            overall_status,

        "critical":
            critical,

        "warnings":
            warnings,

        "passes":
            passes,

        "claims":
            [],

        "strategy_effectiveness":
            [],

        "open_loops":
            loop_findings,

        "rhetorical_patterns":
            rhetorical_findings,

        "emotional_intensity":
            {},

        "cta":
            {},

        "ethics":
            {
                "local_check":
                    (
                        "complete"
                    ),
            },

        "structure":
            {},

        "word_count":
            length_result,
    }


# ============================================================
# COMBINE LOCAL + GEMINI RESULTS
# ============================================================

def combine_validation_results(
    local_result,
    semantic_result,
):
    """
    Combine deterministic and semantic validation.

    CRITICAL always wins.

    WARNING wins over PASS.
    """

    semantic_result = normalize_validation_result(
        semantic_result
    )

    combined = normalize_validation_result(
        {}
    )

    combined[
        "critical"
    ] = (
        local_result.get(
            "critical",
            []
        )
        +
        semantic_result.get(
            "critical",
            []
        )
    )

    combined[
        "warnings"
    ] = (
        local_result.get(
            "warnings",
            []
        )
        +
        semantic_result.get(
            "warnings",
            []
        )
    )

    combined[
        "passes"
    ] = (
        local_result.get(
            "passes",
            []
        )
        +
        semantic_result.get(
            "passes",
            []
        )
    )

    combined[
        "claims"
    ] = semantic_result.get(
        "claims",
        []
    )

    combined[
        "strategy_effectiveness"
    ] = semantic_result.get(
        "strategy_effectiveness",
        []
    )

    combined[
        "open_loops"
    ] = semantic_result.get(
        "open_loops",
        local_result.get(
            "open_loops",
            []
        ),
    )

    combined[
        "rhetorical_patterns"
    ] = semantic_result.get(
        "rhetorical_patterns",
        local_result.get(
            "rhetorical_patterns",
            []
        ),
    )

    combined[
        "emotional_intensity"
    ] = semantic_result.get(
        "emotional_intensity",
        {},
    )

    combined[
        "cta"
    ] = semantic_result.get(
        "cta",
        {},
    )

    combined[
        "ethics"
    ] = semantic_result.get(
        "ethics",
        {},
    )

    combined[
        "structure"
    ] = semantic_result.get(
        "structure",
        {},
    )

    combined[
        "word_count"
    ] = local_result.get(
        "word_count",
        {},
    )

    if combined["critical"]:

        combined[
            "overall_status"
        ] = "CRITICAL"

    elif combined["warnings"]:

        combined[
            "overall_status"
        ] = "WARNING"

    else:

        combined[
            "overall_status"
        ] = "PASS"

    return combined


# ============================================================
# DISPLAY SUMMARY
# ============================================================

def validation_summary(result):
    """
    Produce a simple human-readable summary.

    This is for the UI later.
    """

    result = normalize_validation_result(
        result
    )

    return {

        "status":
            result["overall_status"],

        "critical_count":
            len(
                result.get(
                    "critical",
                    []
                )
            ),

        "warning_count":
            len(
                result.get(
                    "warnings",
                    []
                )
            ),

        "pass_count":
            len(
                result.get(
                    "passes",
                    []
                )
            ),
    }


# ============================================================
# SELF TEST
# ============================================================

if __name__ == "__main__":

    test_script = """
    Imagine you walk
