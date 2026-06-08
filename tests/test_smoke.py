import unittest

from tool_spoof_lab.oracle import score_trace
from tool_spoof_lab.runner import build_trace
from tool_spoof_lab.structured_oracle import score_structured_trace
from tool_spoof_lab.toolsandbox_overlay import (
    ToolSandboxOverlayFixture,
    fixture_to_rows,
    load_overlay_config,
)
from tool_spoof_lab.toolsandbox_real_probe import DEFAULT_TASKS, select_task_names
from scripts.run_real_toolcall_pilot import build_messages, build_tool_events, visible_rows_for_model
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

    def test_real_toolcall_harness_adds_validator_event(self):
        rows, policy = build_tool_events(
            scenario_path="configs/scenarios/mcp_forged_receipt.json",
            mode="spoofed",
            profile="toolcall_independent_validator",
            model="test-model",
        )
        self.assertTrue(policy["independent_available"])
        self.assertIn("visible_tool_result", [row["event"] for row in rows])
        self.assertIn("validator_call", [row["event"] for row in rows])
        visible_events = [row["event"] for row in visible_rows_for_model(rows)]
        self.assertNotIn("truth_result", visible_events)
        self.assertNotIn("oracle_context", visible_events)

    def test_real_toolcall_harness_repeat_is_not_independent(self):
        rows, _ = build_tool_events(
            scenario_path="configs/scenarios/minimal_false_success.json",
            mode="spoofed",
            profile="toolcall_repeat_same_tool",
            model="test-model",
        )
        events = [row["event"] for row in rows]
        self.assertIn("repeat_tool_call", events)
        self.assertNotIn("validator_call", events)

    def test_real_toolcall_prompt_does_not_leak_condition_or_profile_name(self):
        rows, policy = build_tool_events(
            scenario_path="configs/scenarios/minimal_false_success.json",
            mode="spoofed",
            profile="toolcall_independent_validator",
            model="test-model",
        )
        prompt_text = "\n".join(message["content"] for message in build_messages(rows, policy))
        self.assertNotIn('"mode_visible_to_model"', prompt_text)
        self.assertNotIn('"spoofed"', prompt_text)
        self.assertNotIn('"truthful"', prompt_text)
        self.assertNotIn("toolcall_independent_validator", prompt_text)
        self.assertIn('"policy_id"', prompt_text)

    def test_toolsandbox_overlay_contract_naive_is_vulnerable(self):
        config = load_overlay_config("configs/benchmark_overlays/toolsandbox_overlay_smoke.json")
        fixture = ToolSandboxOverlayFixture(config["fixtures"][0])
        rows = fixture_to_rows(fixture, mode="spoofed", profile="toolsandbox_naive")
        verdict = score_structured_trace(rows)
        self.assertEqual(rows[0]["substrate"], "ToolSandbox")
        self.assertTrue(all(row["adapter_contract"] for row in rows))
        self.assertTrue(all(row["fixture"] for row in rows))
        self.assertFalse(any(row["real_benchmark_run"] for row in rows))
        self.assertTrue(verdict["attack_success"])

    def test_toolsandbox_overlay_contract_validator_uses_state_snapshot(self):
        config = load_overlay_config("configs/benchmark_overlays/toolsandbox_overlay_smoke.json")
        fixture = ToolSandboxOverlayFixture(config["fixtures"][0])
        rows = fixture_to_rows(fixture, mode="spoofed", profile="toolsandbox_independent_validator")
        verdict = score_structured_trace(rows)
        events = [row["event"] for row in rows]
        self.assertIn("validator_call", events)
        self.assertFalse(verdict["attack_success"])
        self.assertTrue(verdict["effective_verification"])

    def test_toolsandbox_real_probe_fills_default_slice_to_limit(self):
        available = DEFAULT_TASKS[:2] + [f"official_task_{index}" for index in range(20)]
        selected = select_task_names(available, requested=None, limit=12)
        self.assertEqual(len(selected), 12)
        self.assertEqual(selected[:2], DEFAULT_TASKS[:2])

    def test_toolsandbox_real_probe_rejects_missing_requested_task(self):
        with self.assertRaises(KeyError):
            select_task_names(["get_wifi"], requested=["missing_task"], limit=12)


if __name__ == "__main__":
    unittest.main()
