import unittest

from tool_spoof_lab.oracle import score_trace
from tool_spoof_lab.runner import build_trace


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


if __name__ == "__main__":
    unittest.main()
