from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .scenario import load_scenario, scenario_to_public_task


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


AgentPolicy = Callable[[dict[str, Any], dict[str, Any]], str]


def naive_agent_answer(tool_result: dict[str, Any], scenario_data: dict[str, Any]) -> str:
    status = tool_result.get("status")
    if status:
        return f"The tool reports that the operation {status}."
    if "submitted" in tool_result:
        state = "submitted" if tool_result.get("submitted") else "not submitted"
        return f"The browser observation reports that the form is {state}."
    if tool_result.get("verified") is True:
        return "The tool reports that the citation is verified."
    if tool_result.get("verified") is False:
        return "The tool reports that the citation is unverified."
    if "exit_code" in tool_result:
        if tool_result.get("exit_code") == 0:
            return f"The command passed with exit code 0: {tool_result.get('stdout', '')}"
        return f"The command failed with exit code {tool_result.get('exit_code')}: {tool_result.get('stderr', '')}"
    return "The tool result was accepted as the current state."


def schema_only_answer(tool_result: dict[str, Any], scenario_data: dict[str, Any]) -> str:
    return "The output is schema-valid. " + naive_agent_answer(tool_result, scenario_data)


def prompt_filter_answer(tool_result: dict[str, Any], scenario_data: dict[str, Any]) -> str:
    serialized = json.dumps(tool_result, ensure_ascii=False).lower()
    if "ignore previous" in serialized or "ignore policy" in serialized:
        return "The result contains instruction-like text; treat it as unverified data and request a check."
    return naive_agent_answer(tool_result, scenario_data)


def cautious_agent_answer(tool_result: dict[str, Any], scenario_data: dict[str, Any]) -> str:
    provenance = str(tool_result.get("provenance", ""))
    if not provenance.startswith("mock_truth_oracle"):
        return "The result is unverified; request an independent check before concluding."
    return naive_agent_answer(tool_result, scenario_data)


def cross_tool_answer(tool_result: dict[str, Any], scenario_data: dict[str, Any]) -> str:
    independent = scenario_data.get("independent_tool_result")
    if not isinstance(independent, dict):
        return "No independent validator is available; surface uncertainty before concluding."

    compared_keys = sorted(set(tool_result).intersection(independent))
    disagreements = [
        key for key in compared_keys
        if key not in {"provenance"} and tool_result.get(key) != independent.get(key)
    ]
    if disagreements:
        keys = ", ".join(disagreements)
        return f"Independent check contradicts the visible result on {keys}; report the result as unverified."
    return "Independent check corroborates the visible result. " + naive_agent_answer(tool_result, scenario_data)


AGENT_PROFILES: dict[str, AgentPolicy] = {
    "naive_accepts_tool": naive_agent_answer,
    "schema_only_accepts_valid": schema_only_answer,
    "prompt_filter_only": prompt_filter_answer,
    "cautious_requires_corroboration": cautious_agent_answer,
    "cross_tool_verifier": cross_tool_answer,
}


def build_trace(scenario_path: str, mode: str, agent_profile: str) -> list[dict[str, Any]]:
    scenario = load_scenario(scenario_path)
    tool_result = scenario.tool_result(mode)
    truth_result = scenario.tool_result("truthful")
    answer = AGENT_PROFILES[agent_profile](tool_result, scenario.data)
    base = {
        "scenario_id": scenario.id,
        "suite": scenario.data["domain"],
        "attack_id": scenario.data["spoof_class"],
        "mode": mode,
        "agent_profile": agent_profile,
        "defense": "none" if agent_profile == "naive_accepts_tool" else "provenance_policy",
        "timestamp": now_iso(),
    }
    if agent_profile == "schema_only_accepts_valid":
        base["defense"] = "schema_only"
    elif agent_profile == "prompt_filter_only":
        base["defense"] = "prompt_filter"
    elif agent_profile == "cross_tool_verifier":
        base["defense"] = "cross_tool_check"
    return [
        {**base, "turn": 1, "event": "user_task", "payload": scenario_to_public_task(scenario)},
        {
            **base,
            "turn": 2,
            "event": "oracle_context",
            "payload": {
                "ground_truth": scenario.data["ground_truth"],
                "success_criteria": scenario.data["success_criteria"],
            },
        },
        {**base, "turn": 3, "event": "truth_result", "payload": truth_result},
        {**base, "turn": 4, "event": "visible_tool_result", "payload": tool_result},
        {**base, "turn": 5, "event": "agent_final", "payload": {"answer": answer}},
    ]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a deterministic local spoofing scenario.")
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--mode", choices=["truthful", "spoofed"], default="spoofed")
    parser.add_argument("--agent-profile", choices=sorted(AGENT_PROFILES), default="naive_accepts_tool")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    trace = build_trace(args.scenario, args.mode, args.agent_profile)
    out = Path(args.out) if args.out else Path("traces") / f"{trace[0]['scenario_id']}.{args.mode}.{args.agent_profile}.trace.jsonl"
    write_jsonl(out, trace)
    print(out)


if __name__ == "__main__":
    main()
