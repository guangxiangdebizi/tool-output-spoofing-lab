from __future__ import annotations

import argparse
import json
from pathlib import Path

from tool_spoof_lab.runner import write_jsonl
from tool_spoof_lab.structured_oracle import score_structured_trace
from tool_spoof_lab.toolsandbox_execution_smoke import (
    PROFILES,
    build_interception_trace,
    execute_toolsandbox_tool,
)
from tool_spoof_lab.toolsandbox_real_probe import load_manifest


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a scripted smoke matrix with real ToolSandbox tool execution and visible-result interception."
    )
    parser.add_argument("--manifest", default="outputs/toolsandbox_real_manifest.json")
    parser.add_argument("--toolsandbox-path", default="/tmp/ToolSandbox")
    parser.add_argument("--out-dir", default="traces/toolsandbox_execution_smoke")
    parser.add_argument("--summary", default="outputs/toolsandbox_execution_smoke_summary.json")
    parser.add_argument("--limit-tasks", type=int, default=12)
    args = parser.parse_args()

    manifest = load_manifest(args.manifest)
    out_dir = Path(args.out_dir)
    scored = []
    execution_records = []
    for task in manifest["tasks"][: args.limit_tasks]:
        execution = execute_toolsandbox_tool(task["task_id"], toolsandbox_path=args.toolsandbox_path)
        execution_records.append(execution.__dict__)
        for mode in ["truthful", "spoofed"]:
            for profile in PROFILES:
                rows = build_interception_trace(execution, mode=mode, profile=profile)
                trace_path = out_dir / f"{task['task_id']}.{mode}.{profile}.trace.jsonl"
                write_jsonl(trace_path, rows)
                scored.append({**score_structured_trace(rows), "trace": str(trace_path)})

    summary = {
        "manifest": args.manifest,
        "substrate": "ToolSandbox",
        "benchmark_source": "apple/ToolSandbox",
        "real_tool_execution": True,
        "real_execution_interception": True,
        "trace_level_visible_result_substitution": True,
        "full_agent_loop_interception": False,
        "full_scenario_run": False,
        "scripted_agent": True,
        "real_model_run": False,
        "real_benchmark_run": False,
        "completed_cells": len(scored),
        "executed_tasks": len(execution_records),
        "profiles": PROFILES,
        "execution_records": execution_records,
        "cells": scored,
    }
    summary_path = Path(args.summary)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(summary_path)


if __name__ == "__main__":
    main()
