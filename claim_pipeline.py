"""Runtime Claim Register integration for the Ren Media pipeline."""

import json
import os
import re

import requests

from claim_register import CLAIM_EXTRACTION_PROMPT
from control_plane import build_claim_register


GEMINI_URL = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/models/gemini-3.5-flash:generateContent"
)


def _parse_json(raw):
    text = str(raw or "").strip()

    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)

    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\[.*\]", text, flags=re.DOTALL)
        if not match:
            raise RuntimeError("Claim extractor returned invalid JSON.")
        value = json.loads(match.group(0))

    if not isinstance(value, list):
        raise RuntimeError("Claim extractor must return a JSON list.")

    return value


def _is_source_passage(source_context):
    return "CREATOR-SUPPLIED RESEARCH / PASSAGE:" in str(source_context or "")


def extract_claim_register(source_context):
    """Extract and validate source claims; topic-only flows receive an empty register."""
    if not _is_source_passage(source_context):
        return {
            "claims": [],
            "policy": {},
        }

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY.")

    prompt = CLAIM_EXTRACTION_PROMPT.format(
        source_text=str(source_context or "")
    )

    response = requests.post(
        GEMINI_URL,
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        json={
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        },
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
        raise RuntimeError("Gemini returned an unexpected claim-extraction response.")

    claims = _parse_json(raw)
    register = build_claim_register(claims)
    return register.to_dict()
