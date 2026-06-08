import unittest

from tool_spoof_lab.oracle import score_trace
from tool_spoof_lab.runner import build_trace
from tool_spoof_lab.structured_oracle import score_structured_trace
from scripts.run_structured_partial import build_structured_trace


class SmokeTests(unittest.TestCase):
    def test_naive_agent_accepts_spoofed_false_success(self):
        rows = build_trace(
            "configs/scenarios/minimal_false_success.json",
            mode="spoofed",
            agent_profile="naive_accepts_tool",
        )
        verdict = score_trace(rows)
        self.assertTrue(verdict["attack_success"])

    def test_cautious_agent_surfaces_uncertainty(self):
        rows = build_trace(
            "configs/scenarios/minimal_false_success.json",
            mode="spoofed",
            agent_profile="cautious_requires_corroboration",
        )
        verdict = score_trace(rows)
        self.assertFalse(verdict["attack_success"])
        self.assertTrue(verdict["requested_corroboration"])

    def test_cross_tool_verifier_catches_forged_receipt(self):
        rows = build_trace(
            "configs/scenarios/mcp_forged_receipt.json",
            mode="spoofed",
            agent_profile="cross_tool_verifier",
        )
        verdict = score_trace(rows)
        self.assertFalse(verdict["attack_success"])
        self.assertTrue(verdict["requested_corroboration"] or verdict["surfaced_uncertainty"])

    def test_structured_naive_accepts_false_status(self):
        rows = build_structured_trace(
            "configs/scenarios/minimal_false_success.json",
            mode="spoofed",
            agent_profile="structured_naive",
        )
        verdict = score_structured_trace(rows)
        self.assertTrue(verdict["attack_success"])
        self.assertEqual(verdict["false_field_accepts"], ["exit_code", "status"])

    def test_structured_validator_uses_true_status(self):
        rows = build_structured_trace(
            "configs/scenarios/mcp_forged_receipt.json",
            mode="spoofed",
            agent_profile="structured_independent_validator",
        )
        verdict = score_structured_trace(rows)
        self.assertFalse(verdict["attack_success"])
        self.assertTrue(verdict["effective_verification"])
        self.assertEqual(verdict["verification_source"], "independent")

    def test_structured_catches_truthful_over_refusal(self):
        rows = build_structured_trace(
            "configs/scenarios/minimal_false_success.json",
            mode="truthful",
            agent_profile="structured_combined_policy",
        )
        verdict = score_structured_trace(rows)
        self.assertTrue(verdict["clean_utility"])
        self.assertFalse(verdict["false_positive_refusal"])


if __name__ == "__main__":
    unittest.main()
