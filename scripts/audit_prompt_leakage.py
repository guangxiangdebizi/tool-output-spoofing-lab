from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.run_real_toolcall_pilot import build_messages as build_local_messages
from scripts.run_real_toolcall_pilot import build_tool_events
from tool_spoof_lab.agentdojo_model_pilot import build_messages as build_agentdojo_messages
from tool_spoof_lab.toolsandbox_model_pilot import build_messages as build_toolsandbox_messages


DEFAULT_FORBIDDEN_PATTERNS = [
    '"mode": "truthful"',
    '"mode": "spoofed"',
    '"truthful"',
    '"spoofed"',
    "oracle_context",
    "raw_tool_result",
    "truth_result",
    "readback_raw_content",
    "ground_truth",
    "success_criteria",
    "harness_expected_structured_score",
]


def local_policy_context(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_valid": None,
        "prompt_filter_triggered": None,
        "freshness_checked": False,
        "signature_checked": False,
    }


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def manifest_rows(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("rows", "runs", "cells", "manifest"):
        value = manifest.get(key)
        if isinstance(value, list):
            return value
    raise ValueError("manifest does not contain rows/runs/cells")


def model_visible_events(manifest_row: dict[str, Any], trace_rows: list[dict[str, Any]]) -> list[str]:
    events = manifest_row.get("model_visible_events")
    if isinstance(events, list):
        return [str(event) for event in events]
    hidden = {"oracle_context", "truth_result", "raw_tool_result", "structured_final"}
    return [str(row.get("event")) for row in trace_rows if row.get("event") not in hidden]


def prompt_text_for_manifest(path: Path, manifest_row: dict[str, Any], trace_rows: list[dict[str, Any]]) -> str:
    path_name = path.name
    if path_name.startswith("toolsandbox_"):
        return "\n".join(message["content"] for message in build_toolsandbox_messages(trace_rows))
    if path_name.startswith("agentdojo_"):
        return "\n".join(message["content"] for message in build_agentdojo_messages(trace_rows))
    if path_name.startswith("real_toolcall_"):
        scenario_id = str(manifest_row.get("scenario_id"))
        scenario_path = Path("configs/scenarios") / f"{scenario_id}.json"
        if scenario_path.exists():
            rows, policy_context = build_tool_events(
                scenario_path=str(scenario_path),
                mode=str(manifest_row.get("mode")),
                profile=str(manifest_row.get("profile")),
                model=str(manifest_row.get("model")),
            )
            return "\n".join(message["content"] for message in build_local_messages(rows, policy_context))
        return "\n".join(message["content"] for message in build_local_messages(trace_rows, local_policy_context(trace_rows)))
    return json.dumps(trace_rows, ensure_ascii=False, sort_keys=True)


def audit_manifest(path: Path, forbidden_patterns: list[str]) -> dict[str, Any]:
    manifest = load_json(path)
    rows = manifest_rows(manifest)
    violations = []
    event_counts: dict[str, int] = {}
    readback_visible = 0
    checked = 0
    for row in rows:
        trace_path = Path(str(row.get("trace", "")))
        if not trace_path.exists():
            violations.append({"trace": str(trace_path), "pattern": "missing_trace"})
            continue
        checked += 1
        trace_rows = load_jsonl(trace_path)
        visible_events = model_visible_events(row, trace_rows)
        for event in visible_events:
            event_counts[event] = event_counts.get(event, 0) + 1
        readback_cell = False
        if "validator_call" in visible_events:
            validator_payloads = [
                trace_row.get("payload", {})
                for trace_row in trace_rows
                if trace_row.get("event") == "validator_call"
            ]
            if any(payload.get("verification_source") == "independent_readback" for payload in validator_payloads):
                readback_cell = True
        prompt_text = prompt_text_for_manifest(path, row, trace_rows)
        if readback_cell:
            readback_visible += 1
        for pattern in forbidden_patterns:
            if pattern in prompt_text:
                violations.append(
                    {
                        "trace": str(trace_path),
                        "pattern": pattern,
                        "visible_events": visible_events,
                    }
                )
    return {
        "manifest": str(path),
        "checked_cells": checked,
        "declared_cells": len(rows),
        "event_counts": event_counts,
        "forbidden_patterns": forbidden_patterns,
        "readback_visible_cells": readback_visible,
        "violation_count": len(violations),
        "violations": violations[:50],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit model-visible events for hidden oracle leakage.")
    parser.add_argument("--manifest", action="append", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--forbidden-pattern", action="append", default=[])
    args = parser.parse_args()

    forbidden = DEFAULT_FORBIDDEN_PATTERNS + args.forbidden_pattern
    runs = [audit_manifest(Path(path), forbidden) for path in args.manifest]
    output = {
        "audit_id": "prompt_leakage_audit_v1",
        "all_clear": all(run["violation_count"] == 0 for run in runs),
        "runs": runs,
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
