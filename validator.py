import json
import re

from claim_register import validate_claim_register, ClaimRegister


def _json_safe(value):
    try:
        return json.dumps(value, indent=2, ensure_ascii=False)
    except Exception:
        return str(value)


def _extract_approved_strategies(strategy_map):
    if strategy_map is None:
        return []
    if isinstance(strategy_map, str):
        text = strategy_map.strip()
        try:
            return _extract_approved_strategies(json.loads(text))
        except Exception:
            patterns = [
                r'"key"\s*:\s*"([^"]+)"',
                r'"id"\s*:\s*"([^"]+)"',
                r'"strategy_key"\s*:\s*"([^"]+)"',
                r'"strategy_id"\s*:\s*"([^"]+)"',
            ]
            result = []
            for pattern in patterns:
                for value in re.findall(pattern, text, flags=re.IGNORECASE):
                    if value not in result:
                        result.append(value)
            return result
    if isinstance(strategy_map, dict):
        for field in ("selected_strategies", "strategies", "selected", "strategy_selection", "strategy_map", "active_strategies"):
            if field in strategy_map:
                result = _extract_approved_strategies(strategy_map[field])
                if result:
                    return result
        for field in ("key", "id", "strategy_key", "strategy_id"):
            if field in strategy_map:
                return [str(strategy_map[field])]
        return []
    if isinstance(strategy_map, list):
        result = []
        for item in strategy_map:
            for value in _extract_approved_strategies(item):
                if value not in result:
                    result.append(value)
        return result
    return []


def _build_strategy_instruction(strategy_map):
    approved = _extract_approved_strategies(strategy_map)
    return "\n".join(f"- {key}" for key in approved) or "NO APPROVED STRATEGIES WERE IDENTIFIED."


def _validate_claim_register_payload(claim_register):
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
    errors = validate_claim_register(ClaimRegister(claims))
    if errors:
        raise ValueError("Invalid claim register: " + " | ".join(errors))
    return []


VALIDATION_PROMPT_TEMPLATE = """
You are the quality-control layer of a professional YouTube writing system.

Inspect the generated script against the APPROVED PLAN and SOURCE CLAIM REGISTER.
Do not redesign the strategy or select new strategies.

APPROVED STRATEGIES
{approved_strategies}

TOPIC
{topic}

APPROVED OUTLINE
{outline}

GENERATED SCRIPT
{script}

SOURCE CLAIM REGISTER
{claim_register}

GOVERNANCE
{governance}

STRATEGY VALIDATION
For each approved strategy, evaluate actual execution, job completion, appropriateness and overuse. Do not treat keyword presence as execution.

CLAIM COVERAGE GATE
Identify every important factual, scientific, historical, statistical, psychological, medical, financial, legal, or research-based assertion introduced by the generated script.

For EACH important assertion, determine whether it is:
- directly supported by a supplied Claim Register claim;
- independently verified;
- clearly framed as interpretation or opinion;
- clearly framed as a hypothetical/example rather than a factual assertion; or
- unsupported by the available evidence.

A claim is NOT covered merely because it is related to the topic or resembles a supplied claim. Specific numbers, physiological mechanisms, causal explanations, prevalence statements, predictions, or claims about what people generally do or feel require their own support.

If an important factual assertion is unsupported, classify it as unsupported and set its risk appropriately. The validator status MUST be CRITICAL when any important unsupported factual assertion would require the audience to treat it as true.

Do not silently convert source-only material into independently verified fact.

PERSONAL EXPERIENCE
Flag invented personal memories, professional experience, client experiences, credentials, or first-person stories.

OUTPUT
Return valid JSON only:
{{
  "status": "PASS|WARNING|CRITICAL",
  "approved_strategy_keys": [],
  "strategy_evaluation": [],
  "critical": [],
  "warnings": [],
  "passes": [],
  "claims": []
}}

Each claim object must use:
{{
  "claim": "Short description",
  "classification": "fact|interpretation|hypothetical|opinion",
  "evidence_status": "supported|uncertain|unsupported|source_only",
  "risk": "none|low|medium|high",
  "safe_wording_required": false,
  "reason": "Short explanation"
}}
"""


def validate_script(script, topic="", outline="", strategy_map=None, governance="", governance_rules="", length_minutes=10, target_minutes=None, claim_register=None):
    approved_keys = _extract_approved_strategies(strategy_map)
    if target_minutes is not None:
        length_minutes = target_minutes
    if not governance and governance_rules:
        governance = governance_rules

    _validate_claim_register_payload(claim_register)
    claim_text = _json_safe(claim_register or {"claims": [], "policy": {}})
    prompt = VALIDATION_PROMPT_TEMPLATE.format(
        approved_strategies=_build_strategy_instruction(strategy_map),
        topic=topic,
        outline=outline,
        script=script,
        claim_register=claim_text,
        governance=governance,
    )

    import os
    import requests

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY.")
    response = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent",
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=120,
    )
    response.raise_for_status()
    data = response.json()
    try:
        raw = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError, TypeError):
        raise RuntimeError("Gemini returned an unexpected validator response.")
    return _enforce_strategy_scope(_parse_validator_json(raw), approved_keys)


def _parse_validator_json(raw):
    text = str(raw or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise RuntimeError("Validator returned invalid JSON.")
        try:
            result = json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            raise RuntimeError("Validator returned invalid JSON.") from exc
    if not isinstance(result, dict):
        raise RuntimeError("Validator JSON must be an object.")
    return result


def _enforce_strategy_scope(result, approved_keys):
    approved_set = {str(key).strip() for key in approved_keys if str(key).strip()}
    result["approved_strategy_keys"] = list(approved_keys)
    evaluations = result.get("strategy_evaluation", [])
    if not isinstance(evaluations, list):
        evaluations = []
    filtered = []
    seen = set()
    for evaluation in evaluations:
        if not isinstance(evaluation, dict):
            continue
        key = str(evaluation.get("strategy_key", "")).strip()
        if key not in approved_set or key in seen:
            continue
        seen.add(key)
        filtered.append(evaluation)
    existing = {item.get("strategy_key") for item in filtered}
    for key in approved_keys:
        if key not in existing:
            filtered.append({
                "strategy_key": key,
                "executed": False,
                "job_completed": False,
                "locations": [],
                "assessment": "The validator did not produce a valid evaluation for this approved strategy.",
                "status": "WARNING",
            })
    result["strategy_evaluation"] = filtered

    claims = result.get("claims", [])
    if not isinstance(claims, list):
        claims = []
    unsupported = [
        claim for claim in claims
        if isinstance(claim, dict)
        and str(claim.get("classification", "fact")).lower() == "fact"
        and str(claim.get("evidence_status", "")).lower() == "unsupported"
        and str(claim.get("risk", "low")).lower() in {"medium", "high"}
    ]
    if unsupported:
        result["status"] = "CRITICAL"
        critical = result.get("critical", [])
        if not isinstance(critical, list):
            critical = []
        for claim in unsupported:
            message = f"Unsupported factual claim requires evidence: {claim.get('claim', 'unspecified claim')}"
            if message not in critical:
                critical.append(message)
        result["critical"] = critical
    return result


def validation_status(validation):
    if not isinstance(validation, dict):
        return "CRITICAL"
    status = str(validation.get("status", "")).upper().strip()
    if status in {"CRITICAL", "FAIL", "FAILED", "BLOCK"}:
        return "CRITICAL"
    critical = validation.get("critical", [])
    if isinstance(critical, list) and critical:
        return "CRITICAL"
    return "PASS"
