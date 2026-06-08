from __future__ import annotations

import argparse
import json
from pathlib import Path

from tool_spoof_lab.runner import write_jsonl
from tool_spoof_lab.structured_oracle import score_structured_trace
from tool_spoof_lab.toolsandbox_real_bringup import PROFILES, build_bringup_trace
from tool_spoof_lab.toolsandbox_real_probe import load_manifest


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a scripted 96-cell bring-up matrix over real ToolSandbox manifest tasks."
    )
    parser.add_argument("--manifest", default="outputs/toolsandbox_real_manifest.json")
    parser.add_argument("--out-dir", default="traces/toolsandbox_real_bringup")
    parser.add_argument("--summary", default="outputs/toolsandbox_real_bringup_summary.json")
    args = parser.parse_args()

    manifest = load_manifest(args.manifest)
    out_dir = Path(args.out_dir)
    scored = []
    for task in manifest["tasks"]:
        for mode in ["truthful", "spoofed"]:
            for profile in PROFILES:
                rows = build_bringup_trace(task, mode=mode, profile=profile)
                trace_path = out_dir / f"{task['task_id']}.{mode}.{profile}.trace.jsonl"
                write_jsonl(trace_path, rows)
                scored.append({**score_structured_trace(rows), "trace": str(trace_path)})

    summary = {
        "manifest": args.manifest,
        "substrate": "ToolSandbox",
        "benchmark_source": "apple/ToolSandbox",
        "manifest_derived": True,
        "manifest_derived_scripted_bringup": True,
        "scripted_oracle_bringup": True,
        "real_benchmark_task": True,
        "real_benchmark_run": False,
        "real_model_run": False,
        "real_execution_interception": False,
        "completed_cells": len(scored),
        "profiles": PROFILES,
        "cells": scored,
    }
    summary_path = Path(args.summary)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(summary_path)


if __name__ == "__main__":
    main()
