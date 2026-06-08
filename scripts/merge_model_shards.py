from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path
from typing import Any

from tool_spoof_lab.toolsandbox_model_pilot import summarize


def _expand(patterns: list[str]) -> list[Path]:
    paths: list[Path] = []
    for pattern in patterns:
        matches = sorted(glob.glob(pattern))
        if matches:
            paths.extend(Path(match) for match in matches)
        else:
            paths.append(Path(pattern))
    return paths


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _cells(summary: dict[str, Any]) -> list[dict[str, Any]]:
    if isinstance(summary.get("cells"), list):
        return list(summary["cells"])
    if isinstance(summary.get("scored"), list):
        return list(summary["scored"])
    raise KeyError("summary has neither cells nor scored list")


def _manifest_rows(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    if isinstance(manifest.get("rows"), list):
        return list(manifest["rows"])
    if isinstance(manifest.get("runs"), list):
        return list(manifest["runs"])
    raise KeyError("manifest has neither rows nor runs list")


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge sharded ToolSandbox/AgentDojo model-policy outputs.")
    parser.add_argument("--summaries", nargs="+", required=True, help="Shard summary paths or glob patterns.")
    parser.add_argument("--manifests", nargs="*", default=[], help="Shard manifest paths or glob patterns.")
    parser.add_argument("--summary-out", required=True)
    parser.add_argument("--manifest-out")
    args = parser.parse_args()

    summary_paths = _expand(args.summaries)
    if not summary_paths:
        raise SystemExit("no summaries matched")
    summaries = [_load_json(path) for path in summary_paths]
    all_cells = [cell for summary in summaries for cell in _cells(summary)]

    merged = {
        **{key: value for key, value in summaries[0].items() if key not in {"aggregate", "cells", "scored"}},
        "merged_from_shards": [str(path) for path in summary_paths],
        "completed_cells": len(all_cells),
        "expected_cells_without_limit": sum(int(summary.get("expected_cells_without_limit", 0)) for summary in summaries),
        "aggregate": summarize(all_cells),
    }
    if "cells" in summaries[0]:
        merged["cells"] = all_cells
    else:
        merged["scored"] = all_cells
    if "selected_task_count" in summaries[0]:
        merged["selected_task_count"] = sum(int(summary.get("selected_task_count", 0)) for summary in summaries)
        merged["executable_task_count"] = sum(int(summary.get("executable_task_count", 0)) for summary in summaries)
        unsupported = []
        for summary in summaries:
            unsupported.extend(summary.get("unsupported_tasks", []))
        merged["unsupported_task_count"] = len(unsupported)
        merged["unsupported_tasks"] = unsupported
    if "task_count" in summaries[0]:
        merged["task_count"] = sum(int(summary.get("task_count", 0)) for summary in summaries)

    summary_out = Path(args.summary_out)
    summary_out.parent.mkdir(parents=True, exist_ok=True)
    summary_out.write_text(json.dumps(merged, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    if args.manifests and args.manifest_out:
        manifest_paths = _expand(args.manifests)
        manifests = [_load_json(path) for path in manifest_paths]
        rows = [row for manifest in manifests for row in _manifest_rows(manifest)]
        row_key = "rows" if "rows" in manifests[0] else "runs"
        merged_manifest = {
            **{key: value for key, value in manifests[0].items() if key not in {"rows", "runs"}},
            "merged_from_shards": [str(path) for path in manifest_paths],
            row_key: rows,
        }
        manifest_out = Path(args.manifest_out)
        manifest_out.parent.mkdir(parents=True, exist_ok=True)
        manifest_out.write_text(json.dumps(merged_manifest, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    print(summary_out)


if __name__ == "__main__":
    main()
