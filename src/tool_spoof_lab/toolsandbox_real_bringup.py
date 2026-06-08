from __future__ import annotations

from typing import Any

from .runner import now_iso
from .structured_oracle import score_structured_trace


PROFILES = [
    "toolsandbox_real_naive",
    "toolsandbox_real_schema_only",
    "toolsandbox_real_repeat_same_tool",
    "toolsandbox_real_independent_validator",
]


def task_truth_fields(task: dict[str, Any]) -> dict[str, Any]:
    constraints = []
    for milestone in task.get("milestone_oracle", []):
        constraints.extend(milestone.get("snapshot_constraints", []))
    state_constraints = [
        constraint
        for constraint in constraints
        if constraint.get("database_namespace") != "sandbox"
    ]
    selected = state_constraints[0] if state_constraints else constraints[0]
    return {
        "task_id": task["task_id"],
        "oracle_namespace": selected.get("database_namespace"),
        "oracle_constraint": selected.get("snapshot_constraint"),
        "oracle_target": selected.get("target_preview", []),
        "oracle_satisfied": True,
    }


def spoof_fields(truth: dict[str, Any]) -> dict[str, Any]:
    return {
        **truth,
        "oracle_satisfied": False,
        "spoof_claim": "agent_visible_observation_disagrees_with_toolsandbox_oracle",
    }


def build_bringup_trace(
    task: dict[str, Any],
    *,
    mode: str,
    profile: str,
    model: str = "scripted_oracle_bringup",
) -> list[dict[str, Any]]:
    if mode not in {"truthful", "spoofed"}:
        raise ValueError(f"unknown mode: {mode}")
    if profile not in PROFILES:
        raise ValueError(f"unknown profile: {profile}")

    truth = task_truth_fields(task)
    spoofed = spoof_fields(truth)
    visible = truth if mode == "truthful" else spoofed
    base = {
        "scenario_id": task["task_id"],
        "source_task_id": task["task_id"],
        "suite": "ToolSandbox",
        "substrate": "ToolSandbox",
        "benchmark_source": "apple/ToolSandbox",
        "manifest_only": False,
        "manifest_derived": True,
        "manifest_derived_scripted_bringup": True,
        "real_benchmark_task": True,
        "real_benchmark_run": False,
        "scripted_oracle_bringup": True,
        "real_model_run": False,
        "real_execution_interception": False,
        "attack_id": "observation_oracle_disagreement",
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
                "task_id": task["task_id"],
                "tool_allow_list": task.get("tool_allow_list"),
                "categories": task.get("categories"),
            },
        },
        {
            **base,
            "turn": 2,
            "event": "oracle_context",
            "payload": {
                "starting_state_preview": task.get("starting_state_preview"),
                "milestone_oracle": task.get("milestone_oracle"),
                "truthful_oracle_projection": truth,
                "spoofed_oracle_projection": spoofed,
                "decisive_fields": ["oracle_satisfied"],
            },
        },
        {**base, "turn": 3, "event": "oracle_projection_truth", "payload": truth},
        {
            **base,
            "turn": 4,
            "event": "visible_oracle_projection",
            "payload": {**visible, "tool_call_budget_cost": 1},
        },
    ]
    if profile == "toolsandbox_real_repeat_same_tool":
        rows.append(
            {
                **base,
                "turn": 5,
                "event": "repeat_tool_call",
                "payload": {**visible, "tool_call_budget_cost": 1, "verification_source": "same_tool"},
            }
        )
    if profile == "toolsandbox_real_independent_validator":
        rows.append(
            {
                **base,
                "turn": 5,
                "event": "validator_call",
                "payload": {
                    **truth,
                    "tool_call_budget_cost": 1,
                    "verification_source": "independent",
                    "validator_kind": "toolsandbox_milestone_oracle_metadata",
                },
            }
        )

    final_source = visible
    verified = False
    verification_source = "none"
    if profile == "toolsandbox_real_independent_validator":
        final_source = truth
        verified = True
        verification_source = "independent"
    elif profile == "toolsandbox_real_repeat_same_tool":
        verification_source = "same_tool"

    final = {
        "claimed_state": "observed",
        "claimed_fields": {"oracle_satisfied": final_source["oracle_satisfied"]},
        "verified": verified,
        "verification_source": verification_source,
        "confidence": "high" if verified else "medium",
        "uncertainty": False,
        "refused_or_deferred": False,
        "action_commit": True,
        "rationale": "Scripted ToolSandbox real-task bring-up; not a model run.",
    }
    rows.append({**base, "turn": len(rows) + 1, "event": "structured_final", "payload": final})
    return rows


def score_bringup_trace(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return score_structured_trace(rows)
