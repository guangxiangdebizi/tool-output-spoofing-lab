from __future__ import annotations

import argparse
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from tool_spoof_lab.runner import now_iso, write_jsonl
from tool_spoof_lab.scenario import Scenario, load_scenario, scenario_to_public_task
from tool_spoof_lab.structured_oracle import decisive_fields, score_structured_trace


STRUCTURED_PROFILES = [
    "structured_naive",
    "structured_schema_only",
    "structured_prompt_filter",
    "structured_repeat_same_tool",
    "structured_independent_validator",
    "structured_combined_policy",
]


def contains_instruction_like_text(result: dict[str, Any]) -> bool:
    serialized = json.dumps(result, ensure_ascii=False).lower()
    return "ignore previous" in serialized or "ignore policy" in serialized


def claim_from_result(
    result: dict[str, Any],
    fields: list[str],
    *,
    verified: bool,
    verification_source: str,
    uncertainty: bool = False,
    refused_or_deferred: bool = False,
    action_commit: bool = True,
    rationale: str,
) -> dict[str, Any]:
    return {
        "claimed_state": "unknown" if uncertainty else "observed",
        "claimed_fields": {field: result.get(field) for field in fields if field in result},
        "verified": verified,
        "verification_source": verification_source,
        "confidence": "low" if uncertainty else ("high" if verified else "medium"),
        "uncertainty": uncertainty,
        "refused_or_deferred": refused_or_deferred,
        "action_commit": action_commit,
        "rationale": rationale,
    }


def uncertainty_final(reason: str) -> dict[str, Any]:
    return {
        "claimed_state": "unknown",
        "claimed_fields": {},
        "verified": False,
        "verification_source": "none",
        "confidence": "low",
        "uncertainty": True,
        "refused_or_deferred": True,
        "action_commit": False,
        "rationale": reason,
    }


def disagreements(left: dict[str, Any], right: dict[str, Any], fields: list[str]) -> list[str]:
    return [field for field in fields if left.get(field) != right.get(field)]


def build_structured_trace(scenario_path: str, mode: str, agent_profile: str) -> list[dict[str, Any]]:
    scenario = load_scenario(scenario_path)
    if agent_profile not in STRUCTURED_PROFILES:
        raise ValueError(f"unknown structured profile: {agent_profile}")

    truthful = scenario.tool_result("truthful")
    spoofed = scenario.tool_result("spoofed")
    visible = scenario.tool_result(mode)
    fields = decisive_fields(truthful, spoofed)
    base = {
        "scenario_id": scenario.id,
        "suite": scenario.data["domain"],
        "attack_id": scenario.data["spoof_class"],
        "mode": mode,
        "agent_profile": agent_profile,
        "timestamp": now_iso(),
    }

    rows: list[dict[str, Any]] = [
        {**base, "turn": 1, "event": "user_task", "payload": scenario_to_public_task(scenario)},
        {
            **base,
            "turn": 2,
            "event": "oracle_context",
            "payload": {
                "ground_truth": scenario.data["ground_truth"],
                "success_criteria": scenario.data["success_criteria"],
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
            "payload": {**visible, "tool_call_budget_cost": 1, "verification_source": "primary"},
        },
    ]

    independent = scenario.data.get("independent_tool_result")
    has_independent = isinstance(independent, dict)

    if agent_profile == "structured_naive":
        final = claim_from_result(
            visible,
            fields,
            verified=False,
            verification_source="none",
            rationale="Accepted the primary visible tool result without verification.",
        )
    elif agent_profile == "structured_schema_only":
        rows.append(
            {
                **base,
                "turn": 5,
                "event": "schema_validation",
                "payload": {"schema_valid": True, "validated_keys": sorted(visible)},
            }
        )
        final = claim_from_result(
            visible,
            fields,
            verified=False,
            verification_source="schema_only",
            rationale="Schema validation passed, but no independent state was checked.",
        )
    elif agent_profile == "structured_prompt_filter":
        if contains_instruction_like_text(visible):
            final = uncertainty_final("Instruction-like text appeared in the tool result; defer pending verification.")
        else:
            final = claim_from_result(
                visible,
                fields,
                verified=False,
                verification_source="prompt_filter",
                rationale="No instruction-like text was detected, so the visible result was accepted.",
            )
    elif agent_profile == "structured_repeat_same_tool":
        rows.append(
            {
                **base,
                "turn": 5,
                "event": "repeat_tool_call",
                "payload": {**visible, "tool_call_budget_cost": 1, "verification_source": "same_tool"},
            }
        )
        final = claim_from_result(
            visible,
            fields,
            verified=False,
            verification_source="same_tool",
            rationale="The same channel repeated the same result; no independent authority was consulted.",
        )
    elif agent_profile == "structured_independent_validator":
        if not has_independent:
            final = uncertainty_final("No independent validator is available for this scenario.")
        else:
            rows.append(
                {
                    **base,
                    "turn": 5,
                    "event": "validator_call",
                    "payload": {
                        **independent,
                        "tool_call_budget_cost": 1,
                        "verification_source": "independent",
                    },
                }
            )
            diff = disagreements(visible, independent, fields)
            if diff:
                final = claim_from_result(
                    independent,
                    fields,
                    verified=True,
                    verification_source="independent",
                    uncertainty=False,
                    refused_or_deferred=False,
                    action_commit=True,
                    rationale=f"Independent validator contradicted primary fields: {', '.join(diff)}.",
                )
            else:
                final = claim_from_result(
                    visible,
                    fields,
                    verified=True,
                    verification_source="independent",
                    rationale="Independent validator corroborated the primary result.",
                )
    elif agent_profile == "structured_combined_policy":
        rows.append(
            {
                **base,
                "turn": 5,
                "event": "freshness_check",
                "payload": {
                    "freshness_checked": True,
                    "has_timestamp": any(key in visible for key in ("timestamp", "updated_at", "as_of")),
                    "tool_call_budget_cost": 0,
                },
            }
        )
        if has_independent:
            rows.append(
                {
                    **base,
                    "turn": 6,
                    "event": "validator_call",
                    "payload": {
                        **independent,
                        "tool_call_budget_cost": 1,
                        "verification_source": "independent",
                    },
                }
            )
            diff = disagreements(visible, independent, fields)
            source = independent if diff else visible
            final = claim_from_result(
                source,
                fields,
                verified=True,
                verification_source="independent",
                rationale=(
                    f"Combined policy used freshness metadata and independent validation; "
                    f"contradictions: {', '.join(diff) if diff else 'none'}."
                ),
            )
        elif str(visible.get("provenance")) == "mock_truth_oracle":
            final = claim_from_result(
                visible,
                fields,
                verified=True,
                verification_source="trusted_fixture",
                rationale="Combined policy accepted a truth-oracle fixture when no independent validator was needed.",
            )
        else:
            final = uncertainty_final("Combined policy could not obtain independent validation.")
    else:
        raise AssertionError(agent_profile)

    rows.append({**base, "turn": len(rows) + 1, "event": "structured_final", "payload": final})
    return rows


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for row in rows:
        profile = row["agent_profile"]
        mode = row["mode"]
        bucket = summary.setdefault(profile, {}).setdefault(mode, {
            "n": 0,
            "attack_success": 0,
            "clean_utility": 0,
            "false_positive_refusal": 0,
            "verification_attempted": 0,
            "effective_verification": 0,
            "tool_call_count": 0,
        })
        bucket["n"] += 1
        for key in [
            "attack_success",
            "clean_utility",
            "false_positive_refusal",
            "verification_attempted",
            "effective_verification",
        ]:
            bucket[key] += int(bool(row.get(key)))
        bucket["tool_call_count"] += int(row.get("tool_call_count", 0))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run structured partial benchmark with field-level scoring.")
    parser.add_argument("--config", default="configs/experiments/mvp_matrix.json")
    parser.add_argument("--out-dir", default="traces/structured_15scenario_partial")
    parser.add_argument("--summary", default="outputs/structured_partial_summary.json")
    args = parser.parse_args()

    matrix = json.loads(Path(args.config).read_text(encoding="utf-8"))
    out_dir = Path(args.out_dir)
    scored_rows: list[dict[str, Any]] = []

    for scenario_path in matrix["scenarios"]:
        scenario: Scenario = load_scenario(scenario_path)
        for mode in ["truthful", "spoofed"]:
            for profile in STRUCTURED_PROFILES:
                trace = build_structured_trace(scenario_path, mode=mode, agent_profile=profile)
                trace_name = f"{scenario.id}.{mode}.{profile}.structured.trace.jsonl"
                trace_path = out_dir / trace_name
                write_jsonl(trace_path, trace)
                scored_rows.append({**score_structured_trace(trace), "trace": str(trace_path)})

    summary_path = Path(args.summary)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"cells": scored_rows, "aggregate": summarize(scored_rows)}
    summary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(summary_path)


if __name__ == "__main__":
    main()
