from __future__ import annotations

import argparse

from tool_spoof_lab.toolsandbox_real_probe import build_manifest, write_manifest


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Probe real Apple ToolSandbox scenarios and emit a manifest-only overlay candidate slice."
    )
    parser.add_argument(
        "--toolsandbox-path",
        help="Path to a cloned https://github.com/apple/ToolSandbox repo, if tool_sandbox is not installed.",
    )
    parser.add_argument(
        "--tasks",
        nargs="*",
        help="Optional exact ToolSandbox scenario names. Defaults to a small overlay-candidate slice.",
    )
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument(
        "--stratified",
        action="store_true",
        help="Select a deterministic multi-label stratified slice instead of the named bring-up seed.",
    )
    parser.add_argument(
        "--output",
        default="outputs/toolsandbox_real_manifest.json",
        help="Output manifest path. outputs/ is ignored by git.",
    )
    args = parser.parse_args()

    manifest = build_manifest(
        toolsandbox_path=args.toolsandbox_path,
        task_names=args.tasks,
        limit=args.limit,
        stratified=args.stratified,
    )
    write_manifest(manifest, args.output)
    print(args.output)


if __name__ == "__main__":
    main()
