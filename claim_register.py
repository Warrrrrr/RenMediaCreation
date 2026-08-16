"""
Ren Media — Source Claim Register

Purpose:

Separate:

SOURCE CLAIM
    from
VERIFIED FACT

A supplied article, research passage, transcript or other source is
evidence of what the source says.

It is NOT automatically evidence that the claim itself is true.

This module does not perform independent fact checking.

It creates a structured register that downstream generation and
validation can use to avoid silently upgrading source claims into facts.
"""

import json
import re


# =============================================================================
# CLAIM TYPES
# =============================================================================

CLAIM_TYPES = {
    "fact",
    "inference",
    "interpretation",
    "example",
    "hypothesis",
    "source_report",
}


EVIDENCE_STATUS = {
    "source_supported",
    "source_partially_supported",
    "source_not_supported",
    "independent_verification_unknown",
}


SAFE_SCRIPT_STATUS = {
    "allowed_as_verified_fact",
    "allowed_with_calibrated_language",
    "source_attribution_required",
    "do_not_present_as_verified_fact",
}


# =============================================================================
# CLAIM RECORD
# =============================================================================

def make_claim(
    claim_id,
    claim,
    source_text="",
    claim_type="source_report",
    source_support="source_supported",
    independent_verification="unknown",
    safe_script_status="source_attribution_required",
    safe_wording="",
    source_location="",
):
    """
    Create one normalized claim record.

    Important:
    independent_verification defaults to UNKNOWN.

    A supplied source never becomes independently verified merely because
    the source states the claim confidently.
    """

    if claim_type not in CLAIM_TYPES:
        raise ValueError(
            f"Unknown claim type: {claim_type}"
        )

    if source_support not in EVIDENCE_STATUS:
        raise ValueError(
            f"Unknown source support status: {source_support}"
        )

    if safe_script_status not in SAFE_SCRIPT_STATUS:
        raise ValueError(
            f"Unknown safe script status: {safe_script_status}"
        )

    return {
        "claim_id": claim_id,
        "claim": claim.strip(),
        "source_text": source_text.strip(),
        "source_location": source_location.strip(),

        "claim_type": claim_type,

        "source_support": source_support,

        # Deliberately not converted into True/False.
        "independent_verification": independent_verification,

        "safe_script_status": safe_script_status,

        "safe_wording": safe_wording.strip(),

        "used_in_script": False,
    }


# =============================================================================
# DEFAULT SOURCE-CLAIM POLICY
# =============================================================================

def default_source_claim_policy():
    """
    Rules supplied to the generation/validation layer.

    These rules distinguish:
        source says X
    from:
        X is independently established.
    """

    return {
        "source_material_is_not_automatic_verification": True,

        "default_independent_verification": "unknown",

        "default_safe_script_status": (
            "source_attribution_required"
        ),

        "rules": [
            {
                "id": "SRC-001",
                "rule": (
                    "A creator-supplied source may establish that the source "
                    "makes a claim, but does not by itself establish that "
                    "the claim is independently verified."
                ),
            },
            {
                "id": "SRC-002",
                "rule": (
                    "Do not strengthen a source claim into stronger factual "
                    "language than the supplied material supports."
                ),
            },
            {
                "id": "SRC-003",
                "rule": (
                    "Do not convert association into causation."
                ),
            },
            {
                "id": "SRC-004",
                "rule": (
                    "Do not convert a reported statistic into an independently "
                    "verified statistic unless independent verification is "
                    "explicitly available."
                ),
            },
            {
                "id": "SRC-005",
                "rule": (
                    "When independent verification is unknown, use source-"
                    "attributed or appropriately calibrated language."
                ),
            },
            {
                "id": "SRC-006",
                "rule": (
                    "Do not use words such as 'proved', 'proves', 'proven', "
                    "'definitively', 'guarantees', or equivalent certainty "
                    "unless the supplied evidence genuinely supports that "
                    "level of certainty."
                ),
            },
        ],
    }


# =============================================================================
# SOURCE CLAIM EXTRACTION PROMPT
# =============================================================================

CLAIM_EXTRACTION_PROMPT = """
You are extracting claims from creator-supplied source material.

IMPORTANT:

The source material is NOT automatically verified fact.

Your job is to identify what the source CLAIMS, not to decide that
the claim is true.

For every meaningful factual, scientific, historical, statistical,
psychological or research-related claim, create a claim record.

SOURCE MATERIAL:
{source_text}

Return JSON only:

[
  {{
    "claim_id": "SRC-001",
    "claim": "...",
    "source_support": "source_supported",
    "claim_type": "source_report",
    "safe_script_status": "source_attribution_required",
    "safe_wording": "...",
    "source_location": "..."
  }}
]

Rules:

1. If the source explicitly states something, mark it source_supported.
2. source_supported means:
   "the supplied source supports the statement that this source makes."

   It does NOT mean:
   "the statement has been independently verified."

3. Do not invent verification.
4. Set independent verification to "unknown" unless the supplied
   material itself provides adequate independent verification.
5. Do not upgrade correlation to causation.
6. Do not upgrade an estimate into a certainty.
7. Do not upgrade a reported research result into universal truth.
8. Preserve important numbers exactly as supplied.
9. If a number is supplied but independently unverified, its safe wording
   must make that limitation clear.
"""


# =============================================================================
# CLAIM REGISTER
# =============================================================================

class ClaimRegister:

    def __init__(self, claims=None):
        self.claims = claims or []

    def add(self, claim):
        self.claims.append(claim)

    def all(self):
        return list(self.claims)

    def get(self, claim_id):
        for claim in self.claims:
            if claim.get("claim_id") == claim_id:
                return claim

        return None

    def mark_used(self, claim_id):
        claim = self.get(claim_id)

        if claim is None:
            raise KeyError(
                f"Unknown claim ID: {claim_id}"
            )

        claim["used_in_script"] = True

    def to_dict(self):
        return {
            "claims": self.all(),
            "policy": default_source_claim_policy(),
        }

    def to_json(self):
        return json.dumps(
            self.to_dict(),
            indent=2,
            ensure_ascii=False,
        )


# =============================================================================
# CLAIM REGISTER VALIDATION
# =============================================================================

def validate_claim_register(register):
    """
    Verify that the register follows the source/evidence boundary.

    This does not determine whether a claim is factually true.
    It verifies that the system has not represented unknown verification
    as established verification.
    """

    errors = []

    if not isinstance(register, ClaimRegister):
        raise TypeError(
            "register must be a ClaimRegister."
        )

    for claim in register.all():

        claim_id = claim.get("claim_id", "<unknown>")

        if not claim.get("claim"):
            errors.append(
                f"{claim_id}: missing claim text."
            )

        if claim.get("independent_verification") in {
            True,
            "true",
            "verified",
            "yes",
        }:
            errors.append(
                f"{claim_id}: independent verification cannot be "
                f"assumed from source material."
            )

        if (
            claim.get("source_support") == "source_supported"
            and claim.get("independent_verification") == "unknown"
            and claim.get("safe_script_status")
            == "allowed_as_verified_fact"
        ):
            errors.append(
                f"{claim_id}: source-supported claim with unknown "
                f"independent verification cannot be marked as an "
                f"allowed verified fact."
            )

    return errors


# =============================================================================
# SIMPLE TEXT SAFETY CHECK
# =============================================================================

OVERCLAIMING_LANGUAGE = [
    r"\bproved\b",
    r"\bproves\b",
    r"\bproven\b",
    r"\bdefinitively\b",
    r"\bguarantees\b",
    r"\bguaranteed\b",
    r"\bguarantee\b",
    r"\b100%\b",
    r"\bsingle strongest predictor\b",
    r"\bthe data proves\b",
    r"\bthe research proves\b",
]


def find_overclaiming_language(text):
    """
    Find language that deserves review.

    This is deliberately a review detector, not a claim truth detector.
    """

    matches = []

    text = str(text or "")

    for pattern in OVERCLAIMING_LANGUAGE:

        for match in re.finditer(
            pattern,
            text,
            flags=re.IGNORECASE,
        ):
            matches.append({
                "text": match.group(0),
                "start": match.start(),
                "end": match.end(),
            })

    return matches


# =============================================================================
# EXAMPLE: THE 93.6% PROBLEM
# =============================================================================

def example_gottman_claim():
    """
    Demonstrates how the 93.6% claim should be represented.

    This is NOT asserting whether the historical claim is true.

    It only demonstrates the source/evidence distinction.
    """

    return make_claim(
        claim_id="SRC-EXAMPLE-001",

        claim=(
            "Gottman reported a 93.6% prediction figure."
        ),

        source_text=(
            "Creator-supplied research passage reporting the figure."
        ),

        claim_type="source_report",

        source_support="source_supported",

        independent_verification="unknown",

        safe_script_status=(
            "source_attribution_required"
        ),

        safe_wording=(
            "The supplied source reports a 93.6% prediction figure, "
            "but that figure should not be presented as independently "
            "verified unless the evidence has been independently checked."
        ),

        source_location="creator-supplied research",
    )
