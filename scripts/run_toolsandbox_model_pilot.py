from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any

from tool_spoof_lab.openai_compat import call_chat_completion, response_text
from tool_spoof_lab.runner import now_iso, write_jsonl
from tool_spoof_lab.structured_oracle import score_structured_trace
from tool_spoof_lab.toolsandbox_execution_smoke import (
    PROFILES,
    build_interception_trace,
    execute_toolsandbox_tool,
)
from tool_spoof_lab.toolsandbox_model_pilot import (
    build_messages,
    parse_structured_final,
    sha256_text,
    summarize,
    uncertainty_final,
    visible_rows_for_model,
)
from tool_spoof_lab.toolsandbox_real_probe import load_manifest


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a ToolSandbox model-policy pilot over real tool-execution observations."
    )
    parser.add_argument("--config", default="configs/experiments/toolsandbox_model_pilot_small.json")
    parser.add_argument("--manifest", default="outputs/toolsandbox_real_manifest.json")
    parser.add_argument("--toolsandbox-path", default="/tmp/ToolSandbox")
    parser.add_argument("--out-dir", default="traces/toolsandbox_model_pilot")
    parser.add_argument("--summary", default="outputs/toolsandbox_model_pilot_summary.json")
    parser.add_argument("--run-manifest", default="outputs/toolsandbox_model_pilot_manifest.json")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit-cells", type=int, default=None)
    parser.add_argument("--limit-tasks", type=int, default=None)
    parser.add_argument("--sleep", type=float, default=0.2)
    args = parser.parse_args()

    config_path = Path(args.config)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    provider = config["provider"]
    base_url = os.environ.get(provider["base_url_env"], provider["default_base_url"])
    api_key = os.environ.get(provider["api_key_env"])
    if not args.dry_run and not api_key:
        raise SystemExit(f"missing API key env: {provider['api_key_env']}")

    source_manifest = load_manifest(args.manifest)
    task_records = source_manifest["tasks"]
    if args.limit_tasks is not None:
        task_records = task_records[: args.limit_tasks]
    else:
        task_records = task_records[: int(config["limit_tasks"])]
    task_ids = [task["task_id"] for task in task_records]
    profiles = list(config["profiles"])
    for profile in profiles:
        if profile not in PROFILES:
            raise ValueError(f"unknown profile in config: {profile}")

    execution_cache = {
        task_id: execute_toolsandbox_tool(task_id, toolsandbox_path=args.toolsandbox_path)
        for task_id in task_ids
    }

    out_dir = Path(args.out_dir)
    scored: list[dict[str, Any]] = []
    manifest_rows: list[dict[str, Any]] = []
    cell_count = 0

    for model in provider["models"]:
        for task_id in task_ids:
            execution = execution_cache[task_id]
            for mode in config["modes"]:
                for profile in profiles:
                    if args.limit_cells is not None and cell_count >= args.limit_cells:
                        break
                    scripted_rows = build_interception_trace(execution, mode=mode, profile=profile, model=model)
                    harness_expected_score = score_structured_trace(scripted_rows)
                    rows = [row for row in scripted_rows if row["event"] != "structured_final"]
                    for row in rows:
                        row.update(
                            {
                                "model_policy_prompted": True,
                                "model_final_decision_prompted": True,
                                "scripted_tool_call_plan": True,
                                "autonomous_tool_selection": False,
                                "scripted_agent": False,
                                "scripted_final_stub": args.dry_run,
                                "real_model_run": not args.dry_run,
                            }
                        )
                    messages = build_messages(rows)
                    prompt_hash = sha256_text(json.dumps(messages, ensure_ascii=False, sort_keys=True))
                    api_error = None
                    parse_error = None
                    if args.dry_run:
                        model_call_executed = False
                        final_decision_source = "dry_run_uncertainty_stub"
                        final = uncertainty_final("dry-run: model call skipped")
                    else:
                        try:
                            response = call_chat_completion(
                                base_url=base_url,
                                api_key=str(api_key),
                                model=model,
                                messages=messages,
                                temperature=float(config["temperature"]),
                                timeout_seconds=int(provider["timeout_seconds"]),
                                response_format={"type": "json_object"},
                                retries=int(provider.get("retries", 0)),
                                retry_sleep_seconds=float(provider.get("retry_sleep_seconds", 1.0)),
                            )
                            model_call_executed = True
                            final_decision_source = "model_chat_completion"
                            final, parse_error = parse_structured_final(response_text(response))
                        except (RuntimeError, KeyError) as exc:
                            model_call_executed = False
                            final_decision_source = "api_error_uncertainty_stub"
                            api_error = repr(exc)
                            final = uncertainty_final(f"API error: {type(exc).__name__}")

                    rows.append({**rows[0], "turn": len(rows) + 1, "event": "structured_final", "payload": final})
                    for row in rows:
                        row.update(
                            {
                                "model_call_executed": model_call_executed,
                                "final_decision_source": final_decision_source,
                            }
                        )
                    trace_path = out_dir / f"{task_id}.{mode}.{profile}.{model}.toolsandbox_model.trace.jsonl"
                    write_jsonl(trace_path, rows)
                    scored_row = {
                        **score_structured_trace(rows),
                        "trace": str(trace_path),
                        "model": model,
                        "api_error": api_error,
                        "parse_error": parse_error,
                        "prompt_hash": prompt_hash,
                        "harness_expected_structured_score": harness_expected_score,
                    }
                    scored.append(scored_row)
                    manifest_rows.append(
                        {
                            "trace": str(trace_path),
                            "task_id": task_id,
                            "mode": mode,
                            "profile": profile,
                            "model": model,
                            "prompt_hash": prompt_hash,
                            "api_error": api_error,
                            "parse_error": parse_error,
                            "model_call_executed": model_call_executed,
                            "final_decision_source": final_decision_source,
                            "tool_events": [row["event"] for row in rows if row["event"] in {
                                "toolsandbox_tool_call",
                                "visible_tool_result",
                                "repeat_tool_call",
                                "validator_call",
                            }],
                            "model_visible_events": [row["event"] for row in visible_rows_for_model(rows)],
                        }
                    )
                    cell_count += 1
                    time.sleep(args.sleep)
                if args.limit_cells is not None and cell_count >= args.limit_cells:
                    break
            if args.limit_cells is not None and cell_count >= args.limit_cells:
                break
        if args.limit_cells is not None and cell_count >= args.limit_cells:
            break

    expected_without_limit = len(provider["models"]) * len(task_ids) * len(config["modes"]) * len(profiles)
    common = {
        "config": str(config_path),
        "experiment_id": config["experiment_id"],
        "substrate": "ToolSandbox",
        "benchmark_source": "apple/ToolSandbox",
        "source_manifest": args.manifest,
        "dry_run": args.dry_run,
        "real_tool_execution": True,
        "real_execution_interception": True,
        "trace_level_visible_result_substitution": True,
        "model_policy_prompted": True,
        "model_final_decision_prompted": True,
        "model_call_executed": not args.dry_run,
        "final_decision_source": "model_chat_completion" if not args.dry_run else "dry_run_uncertainty_stub",
        "scripted_tool_call_plan": True,
        "autonomous_tool_selection": False,
        "full_agent_loop_interception": False,
        "full_scenario_run": False,
        "scripted_agent": False,
        "scripted_final_stub": args.dry_run,
        "real_model_run": not args.dry_run,
        "real_benchmark_run": False,
        "representative_10_15_percent_slice": False,
        "selected_task_count": len(task_ids),
        "total_available_scenarios": source_manifest.get("total_available_scenarios"),
        "selected_fraction": (
            len(task_ids) / float(source_manifest["total_available_scenarios"])
            if source_manifest.get("total_available_scenarios")
            else None
        ),
        "expected_cells_without_limit": expected_without_limit,
        "completed_cells": len(scored),
    }
    summary = {
        **common,
        "aggregate": summarize(scored),
        "cells": scored,
    }
    summary_path = Path(args.summary)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    run_manifest = {
        **common,
        "run_started_at": now_iso(),
        "config_sha256": sha256_text(config_path.read_text(encoding="utf-8")),
        "base_url": base_url,
        "models": provider["models"],
        "temperature": config["temperature"],
        "timeout_seconds": provider["timeout_seconds"],
        "retries": provider.get("retries", 0),
        "tool_budget": config.get("tool_budget", {}),
        "rows": manifest_rows,
    }
    manifest_path = Path(args.run_manifest)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(run_manifest, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(summary_path)


if __name__ == "__main__":
    main()
