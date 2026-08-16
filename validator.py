import json
import re

from claim_register import validate_claim_register, ClaimRegister


# =============================================================================
# VALIDATOR
#
# The validator evaluates the APPROVED strategy map only.
#
# It must never:
#   - select additional strategies
#   - scan the entire strategy library
#   - treat mention of a technique as successful execution
#
# The approved strategy map is authoritative.
# =============================================================================


def _json_safe(value):
    try:
        return json.dumps(
            value,
            indent=2,
            ensure_ascii=False,
        )
    except Exception:
        return str(value)


def _extract_approved_strategies(strategy_map):
    """
    Extract only the strategies explicitly present in the approved strategy map.

    Supports:
      - dict strategy maps
      - list strategy maps
      - JSON strings
      - plain text containing strategy records

    This function deliberately does NOT import the strategy library.
    """

    if strategy_map is None:
        return []

    original = strategy_map

    if isinstance(strategy_map, str):

        text = strategy_map.strip()

        # Try JSON first.
        try:
            parsed = json.loads(text)
            return _extract_approved_strategies(parsed)
        except Exception:
            pass

        # Plain-text fallback.
        strategies = []

        patterns = [
            r'"key"\s*:\s*"([^"]+)"',
            r'"id"\s*:\s*"([^"]+)"',
            r'"strategy_key"\s*:\s*"([^"]+)"',
            r'"strategy_id"\s*:\s*"([^"]+)"',
            r'\bstrategy[_\s-]*key\s*[:=]\s*([A-Za-z0-9_-]+)',
            r'\bid\s*[:=]\s*([A-Za-z0-9_-]+)',
        ]

        for pattern in patterns:
            matches = re.findall(
                pattern,
                text,
                flags=re.IGNORECASE,
            )

            for match in matches:

                if match not in strategies:
                    strategies.append(match)

        return strategies

    if isinstance(strategy_map, dict):

        # Common container fields.
        for field in (
            "selected_strategies",
            "strategies",
            "selected",
            "strategy_selection",
            "strategy_map",
            "active_strategies",
        ):

            if field in strategy_map:
                result = _extract_approved_strategies(
                    strategy_map[field]
                )

                if result:
                    return result

        # A single strategy record.
        for field in (
            "key",
            "id",
            "strategy_key",
            "strategy_id",
        ):

            if field in strategy_map:
                return [str(strategy_map[field])]

        return []

    if isinstance(strategy_map, list):

        strategies = []

        for item in strategy_map:

            if isinstance(item, str):

                value = item.strip()

                if value and value not in strategies:
                    strategies.append(value)

            elif isinstance(item, dict):

                found = _extract_approved_strategies(item)

                for value in found:
                    if value not in strategies:
                        strategies.append(value)

        return strategies

    return []


def _build_strategy_instruction(strategy_map):
    """
    Creates the exact strategy scope supplied to Gemini.

    No strategy library is loaded here.
    """

    approved = _extract_approved_strategies(strategy_map)

    if not approved:
        return (
            "NO APPROVED STRATEGIES WERE IDENTIFIED.\n"
            "Do not invent or evaluate strategies."
        )

    return "\n".join(
        f"- {strategy}"
        for strategy in approved
    )


def _validate_claim_register_payload(claim_register):
    """Validate the claim register without deciding whether claims are true."""
    if claim_register is None:
        return []
    if isinstance(claim_register, str):
        try:
            claim_register = json.loads(claim_register)
        except json.JSONDecodeError as exc:
            raise ValueError("Claim register must be valid JSON.") from exc
    if not isinstance(claim_register, dict):
        raise ValueError("Claim register must be a JSON object.")
    claims = claim_register.get("claims", [])
    if not isinstance(claims, list):
        raise ValueError("Claim register claims must be a list.")
    register = ClaimRegister(claims)
    errors = validate_claim_register(register)
    if errors:
        raise ValueError("Invalid claim register: " + " | ".join(errors))
    return []


# =============================================================================
# VALIDATION PROMPT
# =============================================================================

VALIDATION_PROMPT_TEMPLATE = """
You are the quality-control layer of a professional YouTube writing system.

Your job is to inspect the generated script against the APPROVED PLAN.

You are NOT allowed to redesign the strategy.

You are NOT allowed to select new strategies.

You are NOT allowed to scan the entire psychology or strategy library.

============================================================
APPROVED STRATEGIES
============================================================

Only these strategies are approved for this video:

{approved_strategies}

Anything not listed above is OUT OF SCOPE.

If another strategy appears in the script, do NOT add it to the
selected strategy list.

============================================================
TOPIC
============================================================

{topic}

============================================================
APPROVED OUTLINE
============================================================

{outline}

============================================================
GENERATED SCRIPT
============================================================

{script}

============================================================
SOURCE CLAIM REGISTER
============================================================

{claim_register}

The Claim Register distinguishes what a supplied source says from what has been
independently verified. Treat independent verification marked "unknown" as unknown.
Do not classify a source-supported claim as an independently verified fact.

============================================================
GOVERNANCE
============================================================

{governance}

============================================================
STRATEGY VALIDATION
============================================================

For EACH approved strategy, determine:

1. Was the strategy actually executed?
2. Where in the script was it executed?
3. Did it perform the JOB assigned to it?
4. Was it used appropriately?
5. Was it overused?
6. Did it damage clarity, credibility or ethics?

IMPORTANT:

Finding a word, phrase or concept associated with a strategy does NOT
mean the strategy was successfully executed.

For example:

If a strategy is "curiosity_gaps", merely asking a question does not
automatically mean the curiosity strategy succeeded.

The question must create a meaningful information gap that the script
later resolves.

If a strategy is "scene_zoom_technique", merely mentioning a scene does
not automatically mean the strategy succeeded.

The scene must serve the intended viewer-understanding purpose.

Evaluate execution, not keyword presence.

============================================================
SOURCE / CLAIM CHECK
============================================================

Identify factual or research-based claims that appear in the script.

For each important claim determine whether the script:

- presents the claim cautiously;
- attributes it appropriately;
- overstates certainty;
- turns correlation into causation;
- presents supplied-source material as independently verified fact;
- uses stronger wording than the supplied evidence supports.

Never assume that creator-supplied research is independently verified.

============================================================
PERSONAL EXPERIENCE CHECK
============================================================

Flag invented:

- personal memories;
- professional experience;
- client experiences;
- credentials;
- first-person stories.

Do not flag ordinary first-person narration unless it falsely implies
real experience by the creator.

============================================================
OUTPUT
============================================================

Return valid JSON only.

Use exactly this structure:

{{
  "status": "PASS",
  "approved_strategy_keys": [],
  "strategy_evaluation": [],
  "critical": [],
  "warnings": [],
  "passes": [],
  "claims": []
}}

STATUS RULES:

PASS:
No critical blocking problem.

WARNING:
There are issues worth reviewing but they do not necessarily block use.

CRITICAL:
A serious factual, ethical, fabrication, or structural failure exists.

============================================================
STRATEGY EVALUATION FORMAT
============================================================

Each approved strategy must produce exactly one object:

{{
  "strategy_key": "example_strategy",
  "executed": true,
  "job_completed": true,
  "locations": ["opening", "section 2"],
  "assessment": "Short explanation",
  "status": "PASS"
}}

Use:

PASS
WARNING
CRITICAL

Do NOT include strategies that are not in the approved list.

============================================================
CLAIM FORMAT
============================================================

Each important claim should use:

{{
  "claim": "Short description of claim",
  "classification": "fact",
  "evidence_status": "supported|uncertain|unsupported|source_only",
  "risk": "none|low|medium|high",
  "safe_wording_required": false,
  "reason": "Short explanation"
}}

============================================================
FINAL RULE
============================================================

The APPROVED STRATEGY MAP is the boundary of this validation task.

Do not expand it.

Do not replace it.

Do not infer additional approved strategies from the script.

Return JSON only.
"""


# =============================================================================
# VALIDATION
# =============================================================================

def validate_script(
    script,
    topic="",
    outline="",
    strategy_map=None,
    governance="",
    governance_rules="",
    length_minutes=10,
    target_minutes=None,
    claim_register=None,
):
    """
    Validate a generated script against the approved strategy map.

    This function intentionally does not import strategies.py or psychology.py.

    The approved strategy map supplied by the user/system is the only
    strategy scope used by the validator.
    """

    approved_keys = _extract_approved_strategies(
        strategy_map
    )

    approved_text = _build_strategy_instruction(
        strategy_map
    )

    if not governance and governance_rules:
        governance = governance_rules

    if target_minutes is not None:
        length_minutes = target_minutes

    _validate_claim_register_payload(claim_register)
    claim_text = _json_safe(claim_register or {"claims": [], "policy": {}})

    prompt = VALIDATION_PROMPT_TEMPLATE.format(
        approved_strategies=approved_text,
        topic=topic,
        outline=outline,
        script=script,
        claim_register=claim_text,
        governance=governance,
    )

    # Import here so validator.py remains independent of the application's
    # Gemini integration.
    import os
    import requests

    api_key = os.environ.get("GEMINI_API_KEY", "")

    if not api_key:
        raise RuntimeError(
            "Missing GEMINI_API_KEY."
        )

    url = (
        "https://generativelanguage.googleapis.com/"
        "v1beta/models/gemini-3.5-flash:generateContent"
    )

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
    }

    body = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    response = requests.post(
        url,
        headers=headers,
        json=body,
        timeout=120,
    )

    response.raise_for_status()

    data = response.json()

    try:
        raw = (
            data["candidates"][0]
            ["content"]["parts"][0]
            ["text"]
            .strip()
        )

    except (KeyError, IndexError, TypeError):

        raise RuntimeError(
            "Gemini returned an unexpected validator response."
        )

    result = _parse_validator_json(raw)

    # -------------------------------------------------------------------------
    # HARD SAFETY CHECK
    #
    # Even if Gemini attempts to add strategies, the Python layer removes
    # anything outside the approved strategy map.
    # -------------------------------------------------------------------------

    result = _enforce_strategy_scope(
        result,
        approved_keys,
    )

    return result


# =============================================================================
# JSON PARSER
# =============================================================================

def _parse_validator_json(raw):
    """
    Parse Gemini JSON while tolerating markdown fences.
    """

    text = str(raw or "").strip()

    if text.startswith("```"):
        text = re.sub(
            r"^```(?:json)?\s*",
            "",
            text,
            flags=re.IGNORECASE,
        )

        text = re.sub(
            r"\s*```$",
            "",
            text,
        )

    try:
        result = json.loads(text)

    except json.JSONDecodeError:

        # Try to recover the first JSON object.
        match = re.search(
            r"\{.*\}",
            text,
            flags=re.DOTALL,
        )

        if not match:
            raise RuntimeError(
                "Validator returned invalid JSON."
            )

        try:
            result = json.loads(
                match.group(0)
            )
        except json.JSONDecodeError:
            raise RuntimeError(
                "Validator returned invalid JSON."
            )

    if not isinstance(result, dict):
        raise RuntimeError(
            "Validator JSON must be an object."
        )

    return result


# =============================================================================
# HARD STRATEGY SCOPE ENFORCEMENT
# =============================================================================

def _enforce_strategy_scope(
    result,
    approved_keys,
):
    """
    Final Python-side guard.

    Gemini cannot expand the approved strategy scope.
    """

    approved_set = {
        str(key).strip()
        for key in approved_keys
        if str(key).strip()
    }

    # -------------------------------------------------------------------------
    # Approved strategy keys
    # -------------------------------------------------------------------------

    result["approved_strategy_keys"] = list(
        approved_keys
    )

    # -------------------------------------------------------------------------
    # Strategy evaluations
    # -------------------------------------------------------------------------

    evaluations = result.get(
        "strategy_evaluation",
        [],
    )

    if not isinstance(evaluations, list):
        evaluations = []

    filtered = []

    seen = set()

    for evaluation in evaluations:

        if not isinstance(evaluation, dict):
            continue

        key = str(
            evaluation.get("strategy_key", "")
        ).strip()

        if key not in approved_set:
            continue

        if key in seen:
            continue

        seen.add(key)

        filtered.append(evaluation)

    # Ensure every approved strategy has an evaluation.
    existing = {
        item.get("strategy_key")
        for item in filtered
    }

    for key in approved_keys:

        if key not in existing:

            filtered.append(
                {
                    "strategy_key": key,
                    "executed": False,
                    "job_completed": False,
                    "locations": [],
                    "assessment": (
                        "The validator did not produce a valid "
                        "evaluation for this approved strategy."
                    ),
                    "status": "WARNING",
                }
            )

    result["strategy_evaluation"] = filtered

    return result


# =============================================================================
# SIMPLE HELPERS FOR MAIN.PY
# =============================================================================

def validation_status(validation):

    if not isinstance(validation, dict):
        return "CRITICAL"

    status = str(
        validation.get("status", "")
    ).upper().strip()

    if status in {
        "CRITICAL",
        "FAIL",
        "FAILED",
        "BLOCK",
    }:
        return "CRITICAL"

    critical = validation.get(
        "critical",
        [],
    )

    if isinstance(critical, list) and critical:
        return "CRITICAL"

    return "PASS"
