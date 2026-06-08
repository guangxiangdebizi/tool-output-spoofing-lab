from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any

from tool_spoof_lab.openai_compat import call_chat_completion, response_text
from tool_spoof_lab.oracle import load_jsonl
from tool_spoof_lab.runner import now_iso, write_jsonl
from tool_spoof_lab.structured_oracle import score_structured_trace
from tool_spoof_lab.toolsandbox_execution_smoke import (
    ToolExecutionRecord,
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


TOOL_EVENT_NAMES = {
    "toolsandbox_tool_call",
    "visible_tool_result",
    "repeat_tool_call",
    "validator_call",
}


def model_trace_path(out_dir: Path, task_id: str, mode: str, profile: str, model: str) -> Path:
    return out_dir / f"{task_id}.{mode}.{profile}.{model}.toolsandbox_model.trace.jsonl"


def load_reusable_trace(trace_path: Path) -> tuple[list[dict[str, Any]] | None, str | None]:
    if not trace_path.exists():
        return None, "missing"
    try:
        rows = load_jsonl(trace_path)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        return None, f"unreadable:{type(exc).__name__}"
    if not rows:
        return None, "empty"

    final_row = next((row for row in reversed(rows) if row.get("event") == "structured_final"), None)
    if final_row is None:
        return None, "missing_structured_final"
    if not isinstance(final_row.get("payload"), dict):
        return None, "bad_structured_final"

    final_decision_source = str(final_row.get("final_decision_source", ""))
    if final_decision_source != "model_chat_completion":
        return None, f"non_model_final:{final_decision_source or 'missing'}"
    if not bool(final_row.get("model_call_executed", False)):
        return None, "model_call_not_executed"
    return rows, None


def prompt_hash_from_trace(rows: list[dict[str, Any]]) -> str:
    prompt_rows = [row for row in rows if row.get("event") != "structured_final"]
    try:
        messages = build_messages(prompt_rows)
    except (KeyError, TypeError, ValueError):
        messages = [{"role": "user", "content": json.dumps(prompt_rows, ensure_ascii=False, sort_keys=True)}]
    return sha256_text(json.dumps(messages, ensure_ascii=False, sort_keys=True))


def existing_trace_record(
    *,
    trace_path: Path,
    rows: list[dict[str, Any]],
    task_id: str,
    mode: str,
    profile: str,
    model: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    score = score_structured_trace(rows)
    final_row = next((row for row in reversed(rows) if row.get("event") == "structured_final"), rows[-1])
    final_decision_source = str(final_row.get("final_decision_source", "existing_trace"))
    prompt_hash = prompt_hash_from_trace(rows)
    scored_row = {
        **score,
        "trace": str(trace_path),
        "model": model,
        "api_error": None,
        "parse_error": None,
        "prompt_hash": prompt_hash,
        "harness_expected_structured_score": score,
        "skipped_existing": True,
    }
    manifest_row = {
        "trace": str(trace_path),
        "task_id": task_id,
        "mode": mode,
        "profile": profile,
        "model": model,
        "prompt_hash": prompt_hash,
        "api_error": None,
        "parse_error": None,
        "model_call_executed": bool(final_row.get("model_call_executed", False)),
        "final_decision_source": final_decision_source,
        "skipped_existing": True,
        "tool_events": [row["event"] for row in rows if row.get("event") in TOOL_EVENT_NAMES],
        "model_visible_events": [row["event"] for row in visible_rows_for_model(rows)],
    }
    return scored_row, manifest_row


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
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="If a trace file already exists, load and score it instead of calling the model again.",
    )
    parser.add_argument(
        "--task-offset",
        type=int,
        default=0,
        help="Shard offset over selected tasks. Use with --task-stride for parallel full runs.",
    )
    parser.add_argument(
        "--task-stride",
        type=int,
        default=1,
        help="Shard stride over selected tasks. Each shard runs tasks[offset::stride].",
    )
    parser.add_argument("--sleep", type=float, default=0.2)
    parser.add_argument("--progress-every", type=int, default=100)
    args = parser.parse_args()
    if args.task_offset < 0:
        raise SystemExit("--task-offset must be >= 0")
    if args.task_stride < 1:
        raise SystemExit("--task-stride must be >= 1")
    if args.task_offset >= args.task_stride:
        raise SystemExit("--task-offset must be smaller than --task-stride")

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
    pre_shard_task_count = len(task_records)
    task_records = task_records[args.task_offset :: args.task_stride]
    task_ids = [task["task_id"] for task in task_records]
    profiles = list(config["profiles"])
    for profile in profiles:
        if profile not in PROFILES:
            raise ValueError(f"unknown profile in config: {profile}")

    execution_cache: dict[str, ToolExecutionRecord] = {}
    unsupported_tasks: list[dict[str, Any]] = []
    unsupported_task_ids: set[str] = set()
    invalid_existing_traces: list[dict[str, Any]] = []
    invalid_existing_trace_keys: set[str] = set()

    out_dir = Path(args.out_dir)
    scored: list[dict[str, Any]] = []
    manifest_rows: list[dict[str, Any]] = []
    cell_count = 0
    skipped_existing_count = 0
    rerun_invalid_existing_count = 0

    def report_progress(reason: str, force: bool = False) -> None:
        if not force and (args.progress_every <= 0 or cell_count % args.progress_every != 0):
            return
        print(
            json.dumps(
                {
                    "event": "progress",
                    "reason": reason,
                    "completed_cells": cell_count,
                    "skipped_existing": skipped_existing_count,
                    "rerun_invalid_existing": rerun_invalid_existing_count,
                    "unsupported_tasks": len(unsupported_tasks),
                },
                ensure_ascii=False,
                sort_keys=True,
            ),
            flush=True,
        )

    def note_invalid_existing(trace_path: Path, task_id: str, mode: str, profile: str, model: str, reason: str) -> None:
        nonlocal rerun_invalid_existing_count
        key = str(trace_path)
        if reason == "missing" or key in invalid_existing_trace_keys:
            return
        invalid_existing_trace_keys.add(key)
        rerun_invalid_existing_count += 1
        invalid_existing_traces.append(
            {
                "trace": key,
                "task_id": task_id,
                "mode": mode,
                "profile": profile,
                "model": model,
                "reason": reason,
            }
        )

    for model in provider["models"]:
        for task_id in task_ids:
            if args.limit_cells is not None and cell_count >= args.limit_cells:
                break
            if task_id in unsupported_task_ids:
                continue
            task_cells = [
                (mode, profile, model_trace_path(out_dir, task_id, mode, profile, model))
                for mode in config["modes"]
                for profile in profiles
            ]
            if args.skip_existing:
                existing_task_rows: dict[tuple[str, str], list[dict[str, Any]]] = {}
                for mode, profile, trace_path in task_cells:
                    existing_rows, reason = load_reusable_trace(trace_path)
                    if existing_rows is None:
                        note_invalid_existing(trace_path, task_id, mode, profile, model, str(reason))
                        break
                    existing_task_rows[(mode, profile)] = existing_rows
                else:
                    for mode, profile, trace_path in task_cells:
                        if args.limit_cells is not None and cell_count >= args.limit_cells:
                            break
                        scored_row, manifest_row = existing_trace_record(
                            trace_path=trace_path,
                            rows=existing_task_rows[(mode, profile)],
                            task_id=task_id,
                            mode=mode,
                            profile=profile,
                            model=model,
                        )
                        scored.append(scored_row)
                        manifest_rows.append(manifest_row)
                        cell_count += 1
                        skipped_existing_count += 1
                        report_progress("task_skip_existing")
                    continue

            if task_id not in execution_cache:
                try:
                    execution_cache[task_id] = execute_toolsandbox_tool(
                        task_id,
                        toolsandbox_path=args.toolsandbox_path,
                    )
                except Exception as exc:
                    unsupported_task_ids.add(task_id)
                    unsupported_tasks.append(
                        {
                            "task_id": task_id,
                            "error_type": type(exc).__name__,
                            "error": str(exc),
                        }
                    )
                    continue
            execution = execution_cache[task_id]
            for mode in config["modes"]:
                for profile in profiles:
                    if args.limit_cells is not None and cell_count >= args.limit_cells:
                        break
                    trace_path = model_trace_path(out_dir, task_id, mode, profile, model)
                    if args.skip_existing:
                        existing_rows, reason = load_reusable_trace(trace_path)
                        if existing_rows is not None:
                            scored_row, manifest_row = existing_trace_record(
                                trace_path=trace_path,
                                rows=existing_rows,
                                task_id=task_id,
                                mode=mode,
                                profile=profile,
                                model=model,
                            )
                            scored.append(scored_row)
                            manifest_rows.append(manifest_row)
                            cell_count += 1
                            skipped_existing_count += 1
                            report_progress("cell_skip_existing")
                            continue
                        note_invalid_existing(trace_path, task_id, mode, profile, model, str(reason))

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
                    report_progress("cell_completed")
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
        "skip_existing": args.skip_existing,
        "task_offset": args.task_offset,
        "task_stride": args.task_stride,
        "pre_shard_task_count": pre_shard_task_count,
        "selected_task_count": len(task_ids),
        "executable_task_count": len(execution_cache),
        "unsupported_task_count": len(unsupported_tasks),
        "unsupported_tasks": unsupported_tasks,
        "invalid_existing_trace_count": len(invalid_existing_traces),
        "invalid_existing_traces": invalid_existing_traces,
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
    report_progress("finished", force=True)
    print(summary_path)


if __name__ == "__main__":
    main()
