"""Deterministic control-plane checks for Ren Media V2."""

import json
import re

from strategies import STRATEGIES, validate_strategy_ids
from claim_register import ClaimRegister, validate_claim_register, find_overclaiming_language


def parse_strategy_map(strategy_map):
    """Parse and normalize a user-approved strategy map."""
    if isinstance(strategy_map, dict):
        data = strategy_map
    else:
        text = str(strategy_map or "").strip()
        if not text:
            raise ValueError("Strategy map is empty.")
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError("Strategy map must be valid JSON.") from exc

    if not isinstance(data, dict):
        raise ValueError("Strategy map must be a JSON object.")

    selected = data.get("selected_strategy_ids")
    if not isinstance(selected, list):
        records = data.get("selected_strategies")
        if not isinstance(records, list):
            raise ValueError("Strategy map is missing selected strategies.")
        selected = [record.get("id") for record in records if isinstance(record, dict)]

    selected = [str(item).strip() for item in selected if str(item).strip()]
    if not selected:
        raise ValueError("Strategy map contains no selected strategies.")

    unknown = validate_strategy_ids(selected)
    if unknown:
        raise ValueError(f"Unknown strategy IDs: {unknown}")

    if len(selected) != len(set(selected)):
        raise ValueError("Strategy map contains duplicate strategy IDs.")

    return data, selected


def validate_approved_strategy_map(strategy_map):
    """Validate the exact map that will be used by downstream stages."""
    data, selected = parse_strategy_map(strategy_map)

    records = data.get("selected_strategies")
    if isinstance(records, list):
        record_ids = [
            str(record.get("id", "")).strip()
            for record in records
            if isinstance(record, dict)
        ]
        if record_ids and record_ids != selected:
            raise ValueError(
                "Strategy map selected_strategy_ids do not match selected_strategies."
            )

    return data, selected


def build_claim_register(claims):
    """Build and validate a ClaimRegister from normalized claim records."""
    register = ClaimRegister()
    for claim in claims or []:
        if not isinstance(claim, dict):
            raise ValueError("Claim records must be objects.")
        register.add(claim)

    errors = validate_claim_register(register)
    if errors:
        raise ValueError("Invalid claim register: " + " | ".join(errors))
    return register


def deterministic_script_checks(script_text):
    """Return deterministic review findings; never claim factual verification."""
    findings = []
    for match in find_overclaiming_language(script_text):
        findings.append({
            "type": "overclaiming_language",
            "text": match["text"],
            "risk": "medium",
            "message": "Certainty language requires evidence review.",
        })

    text = str(script_text or "")
    if re.search(r"\bI\s+(?:personally|once|have|had)\b", text, re.IGNORECASE):
        findings.append({
            "type": "personal_experience_claim",
            "risk": "high",
            "message": "Personal-experience language requires creator verification.",
        })

    return findings


def canonical_strategy_ids():
    return list(STRATEGIES.keys())
