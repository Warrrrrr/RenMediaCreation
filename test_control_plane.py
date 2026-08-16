import unittest

from control_plane import (
    canonical_strategy_ids,
    deterministic_script_checks,
    validate_approved_strategy_map,
)


class ControlPlaneTests(unittest.TestCase):

    def test_rejects_unknown_strategy_id(self):
        with self.assertRaises(ValueError):
            validate_approved_strategy_map({
                "selected_strategy_ids": ["not_a_real_strategy"]
            })

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
        findings = deterministic_script_checks(
            "The research proves this always works."
        )
        self.assertTrue(
            any(item["type"] == "overclaiming_language" for item in findings)
        )

    def test_registry_is_non_empty(self):
        self.assertTrue(canonical_strategy_ids())


if __name__ == "__main__":
    unittest.main()
