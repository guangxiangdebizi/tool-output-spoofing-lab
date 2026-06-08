from __future__ import annotations

import argparse
import json
from pathlib import Path

from tool_spoof_lab.runner import write_jsonl
from tool_spoof_lab.toolsandbox_overlay import (
    ToolSandboxOverlayFixture,
    fixture_to_rows,
    load_overlay_config,
)
from tool_spoof_lab.structured_oracle import score_structured_trace


PROFILES = [
    "toolsandbox_naive",
    "toolsandbox_independent_validator",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run ToolSandbox overlay adapter-contract smoke fixtures.")
    parser.add_argument("--config", default="configs/benchmark_overlays/toolsandbox_overlay_smoke.json")
    parser.add_argument("--out-dir", default="traces/toolsandbox_overlay_smoke")
    parser.add_argument("--summary", default="outputs/toolsandbox_overlay_smoke_summary.json")
    args = parser.parse_args()

    config = load_overlay_config(args.config)
    out_dir = Path(args.out_dir)
    scored = []
    for fixture_data in config["fixtures"]:
        fixture = ToolSandboxOverlayFixture(fixture_data)
        for mode in ["truthful", "spoofed"]:
            for profile in PROFILES:
                rows = fixture_to_rows(fixture, mode=mode, profile=profile)
                trace_path = out_dir / f"{fixture.id}.{mode}.{profile}.trace.jsonl"
                write_jsonl(trace_path, rows)
                scored.append({**score_structured_trace(rows), "trace": str(trace_path)})

    summary = {
        "config": args.config,
        "substrate": "ToolSandbox",
        "adapter_contract": True,
        "completed_cells": len(scored),
        "cells": scored,
    }
    summary_path = Path(args.summary)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(summary_path)


if __name__ == "__main__":
    main()
