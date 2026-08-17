import unittest

from claim_register import ClaimRegister, validate_claim_register
from control_plane import (
    build_claim_register,
    canonical_strategy_ids,
    deterministic_script_checks,
    validate_approved_strategy_map,
)
from validator import _enforce_strategy_scope, _validate_claim_register_payload


class ControlPlaneTests(unittest.TestCase):

    def test_rejects_unknown_strategy_id(self):
        with self.assertRaises(ValueError):
            validate_approved_strategy_map({"selected_strategy_ids": ["not_a_real_strategy"]})

    def test_rejects_mismatched_strategy_records(self):
        with self.assertRaises(ValueError):
            validate_approved_strategy_map({
                "selected_strategy_ids": ["curiosity_gaps"],
                "selected_strategies": [{"id": "contrast"}],
            })

    def test_accepts_canonical_strategy_map(self):
        data, ids = validate_approved_strategy_map({
            "selected_strategy_ids": ["curiosity_gaps", "contrast"],
            "selected_strategies": [
                {"id": "curiosity_gaps"},
                {"id": "contrast"},
            ],
        })
        self.assertEqual(ids, ["curiosity_gaps", "contrast"])
        self.assertEqual(data["selected_strategy_ids"], ids)

    def test_deterministic_check_flags_certainty_language(self):
        findings = deterministic_script_checks("The research proves this always works.")
        self.assertTrue(any(item["type"] == "overclaiming_language" for item in findings))

    def test_deterministic_check_flags_personal_experience(self):
        findings = deterministic_script_checks("I personally tested this and it always works.")
        self.assertTrue(any(item["type"] == "personal_experience_claim" for item in findings))

    def test_claim_register_rejects_unverified_fact_status(self):
        with self.assertRaises(ValueError):
            build_claim_register([{
                "claim_id": "SRC-001",
                "claim": "A source says X.",
                "source_support": "source_supported",
                "independent_verification": "unknown",
                "safe_script_status": "allowed_as_verified_fact",
            }])

    def test_strategy_boundary_rejects_unknown_edited_map(self):
        with self.assertRaises(ValueError):
            validate_approved_strategy_map({"selected_strategy_ids": ["not_a_real_strategy"]})

    def test_validator_accepts_valid_claim_register(self):
        claims = {"claims": [{
            "claim_id": "SRC-001",
            "claim": "The supplied source reports X.",
            "source_support": "source_supported",
            "independent_verification": "unknown",
            "safe_script_status": "source_attribution_required",
        }]}
        self.assertEqual(_validate_claim_register_payload(claims), [])

    def test_validator_rejects_claim_register_that_upgrades_source_to_fact(self):
        claims = {"claims": [{
            "claim_id": "SRC-001",
            "claim": "The supplied source reports X.",
            "source_support": "source_supported",
            "independent_verification": "unknown",
            "safe_script_status": "allowed_as_verified_fact",
        }]}
        with self.assertRaises(ValueError):
            _validate_claim_register_payload(claims)

    def test_validator_escalates_unsupported_factual_claim(self):
        result = {
            "status": "PASS",
            "claims": [{
                "claim": "The brain stops rational thought during conflict",
                "classification": "fact",
                "evidence_status": "unsupported",
                "risk": "high",
            }],
        }
        result = _enforce_strategy_scope(result, [])
        self.assertEqual(result["status"], "CRITICAL")
        self.assertTrue(result["critical"])

    def test_validator_does_not_escalate_source_only_claim(self):
        result = {
            "status": "PASS",
            "claims": [{
                "claim": "The supplied source reports X",
                "classification": "fact",
                "evidence_status": "source_only",
                "risk": "medium",
            }],
        }
        result = _enforce_strategy_scope(result, [])
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result.get("critical", []), [])

    def test_registry_is_non_empty(self):
        self.assertTrue(canonical_strategy_ids())


if __name__ == "__main__":
    unittest.main()
