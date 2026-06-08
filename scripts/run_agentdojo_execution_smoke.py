from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from tool_spoof_lab.agentdojo_execution_smoke import (
    PROFILES,
    build_interception_trace,
    execute_agentdojo_observation,
    score_interception_trace,
    summarize,
)


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a scripted AgentDojo execution smoke over manifest-selected official tasks."
    )
    parser.add_argument("--manifest", default="outputs/agentdojo_real_manifest.json")
    parser.add_argument("--agentdojo-path", default="/tmp/AgentDojo")
    parser.add_argument("--benchmark-version", default="v1.2.2")
    parser.add_argument("--out-dir", default="traces/agentdojo_execution_smoke")
    parser.add_argument("--summary", default="outputs/agentdojo_execution_smoke_summary.json")
    parser.add_argument("--limit-tasks", type=int, default=None)
    args = parser.parse_args()

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    tasks = manifest["tasks"][: args.limit_tasks] if args.limit_tasks else manifest["tasks"]
    out_dir = Path(args.out_dir)
    records: list[dict[str, Any]] = []
    execution_cache = {}
    for task in tasks:
        cache_key = (task["suite"], task["task_id"])
        if cache_key not in execution_cache:
            execution_cache[cache_key] = execute_agentdojo_observation(
                task["suite"],
                task["task_id"],
                agentdojo_path=args.agentdojo_path,
                benchmark_version=args.benchmark_version,
            )
        execution = execution_cache[cache_key]
        for mode in ["truthful", "spoofed"]:
            for profile in PROFILES:
                rows = build_interception_trace(execution, mode=mode, profile=profile)
                score = score_interception_trace(rows)
                trace_path = out_dir / f"{task['suite']}.{task['task_id']}.{mode}.{profile}.jsonl"
                write_jsonl(trace_path, rows)
                records.append(
                    {
                        "suite": task["suite"],
                        "task_id": task["task_id"],
                        "mode": mode,
                        "profile": profile,
                        "trace_path": str(trace_path),
                        "score": score,
                    }
                )
    summary = {
        "substrate": "AgentDojo",
        "source_manifest": args.manifest,
        "benchmark_version": args.benchmark_version,
        "task_count": len(tasks),
        "profiles": PROFILES,
        "modes": ["truthful", "spoofed"],
        "completed_cells": len(records),
        "expected_cells": len(tasks) * 2 * len(PROFILES),
        "real_agentdojo_task": True,
        "real_tool_execution": True,
        "real_execution_interception": True,
        "trace_level_visible_result_substitution": True,
        "official_ground_truth_tool_plan": True,
        "full_agent_loop_interception": False,
        "scripted_agent": True,
        "real_model_run": False,
        "real_benchmark_run": False,
        "representative_10_15_percent_slice": False,
        **summarize(records),
    }
    Path(args.summary).parent.mkdir(parents=True, exist_ok=True)
    Path(args.summary).write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(args.summary)


if __name__ == "__main__":
    main()
