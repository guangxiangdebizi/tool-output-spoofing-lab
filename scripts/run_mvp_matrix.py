from __future__ import annotations

import argparse
import json
from pathlib import Path

from tool_spoof_lab.oracle import score_trace
from tool_spoof_lab.runner import build_trace, write_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local MVP spoofing matrix.")
    parser.add_argument("--config", default="configs/experiments/mvp_matrix.json")
    parser.add_argument("--out-dir", default="traces")
    args = parser.parse_args()

    matrix = json.loads(Path(args.config).read_text(encoding="utf-8"))
    out_dir = Path(args.out_dir)
    summaries = []

    for scenario_path in matrix["scenarios"]:
        for mode in ["truthful", "spoofed"]:
            for agent_profile in matrix["agent_profiles"]:
                rows = build_trace(scenario_path, mode=mode, agent_profile=agent_profile)
                trace_name = f"{rows[0]['scenario_id']}.{mode}.{agent_profile}.trace.jsonl"
                trace_path = out_dir / trace_name
                write_jsonl(trace_path, rows)
                summaries.append({**score_trace(rows), "trace": str(trace_path)})

    summary_path = Path("outputs") / "mvp_matrix_summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summaries, ensure_ascii=False, indent=2), encoding="utf-8")
    print(summary_path)


if __name__ == "__main__":
    main()
