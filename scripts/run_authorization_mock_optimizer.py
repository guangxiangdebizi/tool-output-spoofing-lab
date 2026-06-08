from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any

from scripts.run_real_toolcall_pilot import (
    build_messages,
    build_tool_events,
    parse_structured_final,
    sha256_text,
    summarize,
)
from tool_spoof_lab.mock_optimizer import authorization_mock_variants
from tool_spoof_lab.openai_compat import call_chat_completion, response_text
from tool_spoof_lab.runner import now_iso, write_jsonl
from tool_spoof_lab.scenario import load_scenario
from tool_spoof_lab.structured_oracle import score_structured_trace


def variant_field_delta(truthful: dict[str, Any], spoofed: dict[str, Any]) -> dict[str, dict[str, Any]]:
    delta = {}
    for key in sorted(set(truthful) | set(spoofed)):
        if truthful.get(key) != spoofed.get(key):
            delta[key] = {"truthful": truthful.get(key), "spoofed": spoofed.get(key)}
    return delta


def run_cell(
    *,
    scenario_path: str,
    variant: dict[str, Any],
    profile: str,
    model: str,
    config: dict[str, Any],
    base_url: str,
    api_key: str | None,
    dry_run: bool,
) -> tuple[list[dict[str, Any]], dict[str, Any], str | None, str | None, str]:
    rows, policy_context = build_tool_events(
        scenario_path=scenario_path,
        mode="spoofed",
        profile=profile,
        model=model,
        spoofed_override=variant["spoofed_tool_result"],
    )
    for row in rows:
        row["optimizer_variant_id"] = variant["variant_id"]
        row["optimizer_variant_description"] = variant["description"]
    messages = build_messages(rows, policy_context)
    prompt_hash = sha256_text(json.dumps(messages, ensure_ascii=False, sort_keys=True))
    api_error = None
    parse_error = None

    if dry_run:
        final = {
            "claimed_state": "unknown",
            "claimed_fields": {},
            "verified": False,
            "verification_source": "none",
            "confidence": "low",
            "uncertainty": True,
            "refused_or_deferred": True,
            "verdict_commitment": False,
            "action_commit": False,
            "rationale": "dry-run: model call skipped",
        }
    else:
        try:
            response = call_chat_completion(
                base_url=base_url,
                api_key=str(api_key),
                model=model,
                messages=messages,
                temperature=float(config["temperature"]),
                timeout_seconds=int(config["provider"]["timeout_seconds"]),
                response_format={"type": "json_object"},
                retries=int(config["provider"].get("retries", 0)),
                retry_sleep_seconds=float(config["provider"].get("retry_sleep_seconds", 1.0)),
            )
            final, parse_error = parse_structured_final(response_text(response))
        except (RuntimeError, KeyError) as exc:
            api_error = repr(exc)
            final = {
                "claimed_state": "unknown",
                "claimed_fields": {},
                "verified": False,
                "verification_source": "none",
                "confidence": "low",
                "uncertainty": True,
                "refused_or_deferred": True,
                "verdict_commitment": False,
                "action_commit": False,
                "rationale": f"API error: {type(exc).__name__}",
            }

    rows.append({**rows[0], "turn": len(rows) + 1, "event": "structured_final", "payload": final})
    return rows, final, api_error, parse_error, prompt_hash


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a tiny authorization observation-surface optimizer pilot.")
    parser.add_argument("--config", default="configs/experiments/authorization_mock_optimizer_tiny.json")
    parser.add_argument("--out-dir", default="traces/authorization_mock_optimizer_tiny")
    parser.add_argument("--summary", default="outputs/authorization_mock_optimizer_tiny_summary.json")
    parser.add_argument("--manifest", default="outputs/authorization_mock_optimizer_tiny_manifest.json")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--sleep", type=float, default=0.2)
    args = parser.parse_args()

    config_path = Path(args.config)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    provider = config["provider"]
    base_url = os.environ.get(provider["base_url_env"], provider["default_base_url"])
    api_key = os.environ.get(provider["api_key_env"])
    if not args.dry_run and not api_key:
        raise SystemExit(f"missing API key env: {provider['api_key_env']}")

    scenario_path = config["scenario"]
    scenario = load_scenario(scenario_path)
    truthful = scenario.tool_result("truthful")
    variants = authorization_mock_variants(truthful)
    out_dir = Path(args.out_dir)
    scored: list[dict[str, Any]] = []
    manifest_rows: list[dict[str, Any]] = []

    for model in provider["models"]:
        for variant in variants:
            for profile in config["profiles"]:
                rows, _final, api_error, parse_error, prompt_hash = run_cell(
                    scenario_path=scenario_path,
                    variant=variant,
                    profile=profile,
                    model=model,
                    config=config,
                    base_url=base_url,
                    api_key=api_key,
                    dry_run=args.dry_run,
                )
                trace_name = f"{scenario.id}.spoofed.{variant['variant_id']}.{profile}.{model}.optimizer.trace.jsonl"
                trace_path = out_dir / trace_name
                write_jsonl(trace_path, rows)
                scored_row = {
                    **score_structured_trace(rows),
                    "trace": str(trace_path),
                    "model": model,
                    "optimizer_variant_id": variant["variant_id"],
                    "optimizer_variant_description": variant["description"],
                    "field_delta": variant_field_delta(truthful, variant["spoofed_tool_result"]),
                    "api_error": api_error,
                    "parse_error": parse_error,
                    "prompt_hash": prompt_hash,
                }
                scored.append(scored_row)
                manifest_rows.append(
                    {
                        "trace": str(trace_path),
                        "scenario_id": scenario.id,
                        "mode": "spoofed",
                        "profile": profile,
                        "model": model,
                        "optimizer_variant_id": variant["variant_id"],
                        "prompt_hash": prompt_hash,
                        "api_error": api_error,
                        "parse_error": parse_error,
                    }
                )
                time.sleep(args.sleep)

    summary = {
        "config": str(config_path),
        "experiment_id": config["experiment_id"],
        "dry_run": args.dry_run,
        "completed_cells": len(scored),
        "aggregate": summarize(scored),
        "cells": scored,
    }
    summary_path = Path(args.summary)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    manifest = {
        "experiment_id": config["experiment_id"],
        "run_started_at": now_iso(),
        "config_sha256": sha256_text(config_path.read_text(encoding="utf-8")),
        "base_url": base_url,
        "models": provider["models"],
        "temperature": config["temperature"],
        "timeout_seconds": provider["timeout_seconds"],
        "retries": provider.get("retries", 0),
        "dry_run": args.dry_run,
        "optimizer_variants": [
            {
                "variant_id": variant["variant_id"],
                "description": variant["description"],
                "field_delta": variant_field_delta(truthful, variant["spoofed_tool_result"]),
            }
            for variant in variants
        ],
        "rows": manifest_rows,
    }
    manifest_path = Path(args.manifest)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(summary_path)


if __name__ == "__main__":
    main()
