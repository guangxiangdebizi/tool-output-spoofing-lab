from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .runner import now_iso
from .structured_oracle import decisive_fields, score_structured_trace


REQUIRED_FIXTURE_KEYS = {
    "id",
    "source_task_id",
    "user_task",
    "suite",
    "spoof_class",
    "hidden_state",
    "milestone_oracle",
    "truthful_observation",
    "spoofed_observation",
    "independent_validator",
}


@dataclass(frozen=True)
class ToolSandboxOverlayFixture:
    data: dict[str, Any]

    @property
    def id(self) -> str:
        return str(self.data["id"])

    def observation(self, mode: str) -> dict[str, Any]:
        if mode == "truthful":
            return dict(self.data["truthful_observation"])
        if mode == "spoofed":
            return dict(self.data["spoofed_observation"])
        raise ValueError(f"unknown mode: {mode}")


def load_overlay_config(path: str | Path) -> dict[str, Any]:
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    if config.get("substrate") != "ToolSandbox":
        raise ValueError("expected ToolSandbox overlay config")
    fixtures = config.get("fixtures")
    if not isinstance(fixtures, list) or not fixtures:
        raise ValueError("ToolSandbox overlay config requires non-empty fixtures")
    for fixture in fixtures:
        if not isinstance(fixture, dict):
            raise ValueError("fixture must be an object")
        missing = REQUIRED_FIXTURE_KEYS.difference(fixture)
        if missing:
            raise ValueError(f"fixture {fixture.get('id')} missing keys: {sorted(missing)}")
    return config


def fixture_to_rows(
    fixture: ToolSandboxOverlayFixture,
    *,
    mode: str,
    profile: str,
    model: str = "adapter_contract",
) -> list[dict[str, Any]]:
    truthful = fixture.observation("truthful")
    spoofed = fixture.observation("spoofed")
    visible = fixture.observation(mode)
    fields = decisive_fields(truthful, spoofed)
    base = {
        "scenario_id": fixture.id,
        "source_task_id": fixture.data["source_task_id"],
        "suite": fixture.data["suite"],
        "substrate": "ToolSandbox",
        "benchmark_source": "toolsandbox_shaped_fixture",
        "adapter_contract": True,
        "fixture": True,
        "real_benchmark_run": False,
        "attack_id": fixture.data["spoof_class"],
        "mode": mode,
        "agent_profile": profile,
        "model": model,
        "timestamp": now_iso(),
    }
    rows: list[dict[str, Any]] = [
        {
            **base,
            "turn": 1,
            "event": "user_task",
            "payload": {
                "task": fixture.data["user_task"],
                "source_task_id": fixture.data["source_task_id"],
                "substrate": "ToolSandbox",
                "benchmark_source": "toolsandbox_shaped_fixture",
                "adapter_contract": True,
                "fixture": True,
                "real_benchmark_run": False,
            },
        },
        {
            **base,
            "turn": 2,
            "event": "oracle_context",
            "payload": {
                "ground_truth": fixture.data["hidden_state"],
                "milestone_oracle": fixture.data["milestone_oracle"],
                "truthful_tool_result": truthful,
                "spoofed_tool_result": spoofed,
                "decisive_fields": fields,
            },
        },
        {**base, "turn": 3, "event": "truth_result", "payload": truthful},
        {
            **base,
            "turn": 4,
            "event": "visible_tool_result",
            "payload": {**visible, "tool_call_budget_cost": 1},
        },
    ]
    if profile in {"toolsandbox_independent_validator", "toolsandbox_combined_policy"}:
        rows.append(
            {
                **base,
                "turn": 5,
                "event": "validator_call",
                "payload": {
                    **fixture.data["independent_validator"],
                    "tool_call_budget_cost": 1,
                    "verification_source": "independent",
                    "validator_kind": "toolsandbox_state_snapshot",
                },
            }
        )
    final_source = visible
    verification_source = "none"
    verified = False
    if profile in {"toolsandbox_independent_validator", "toolsandbox_combined_policy"}:
        final_source = dict(fixture.data["independent_validator"])
        verification_source = "independent"
        verified = True
    final = {
        "claimed_state": "observed",
        "claimed_fields": {field: final_source.get(field) for field in fields if field in final_source},
        "verified": verified,
        "verification_source": verification_source,
        "confidence": "high" if verified else "medium",
        "uncertainty": False,
        "refused_or_deferred": False,
        "action_commit": True,
        "rationale": "ToolSandbox overlay adapter contract smoke final.",
    }
    rows.append({**base, "turn": len(rows) + 1, "event": "structured_final", "payload": final})
    return rows


def score_fixture(fixture: ToolSandboxOverlayFixture, *, mode: str, profile: str) -> dict[str, Any]:
    rows = fixture_to_rows(fixture, mode=mode, profile=profile)
    return score_structured_trace(rows)
