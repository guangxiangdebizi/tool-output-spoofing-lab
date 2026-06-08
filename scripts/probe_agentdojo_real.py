from __future__ import annotations

import argparse

from tool_spoof_lab.agentdojo_real_probe import (
    DEFAULT_BENCHMARK_VERSION,
    DEFAULT_SUITES,
    build_manifest,
    write_manifest,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Probe real AgentDojo suites and emit a manifest-only tool-output-spoofing overlay slice."
    )
    parser.add_argument(
        "--agentdojo-path",
        help="Path to a cloned https://github.com/ethz-spylab/agentdojo repo, if agentdojo is not installed.",
    )
    parser.add_argument("--benchmark-version", default=DEFAULT_BENCHMARK_VERSION)
    parser.add_argument("--suites", nargs="*", default=DEFAULT_SUITES)
    parser.add_argument(
        "--tasks",
        nargs="*",
        help="Optional AgentDojo task IDs. Use either task_id or suite:task_id.",
    )
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument(
        "--stratified",
        action="store_true",
        help="Select a deterministic 10-15% stratified slice instead of highest-priority bring-up tasks.",
    )
    parser.add_argument(
        "--output",
        default="outputs/agentdojo_real_manifest.json",
        help="Output manifest path. outputs/ is ignored by git.",
    )
    args = parser.parse_args()

    manifest = build_manifest(
        agentdojo_path=args.agentdojo_path,
        benchmark_version=args.benchmark_version,
        suites=args.suites,
        task_ids=args.tasks,
        limit=args.limit,
        stratified=args.stratified,
    )
    write_manifest(manifest, args.output)
    print(args.output)


if __name__ == "__main__":
    main()
