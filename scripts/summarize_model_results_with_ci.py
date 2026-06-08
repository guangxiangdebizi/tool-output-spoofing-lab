from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


METRICS = [
    "attack_success",
    "accepted_false_state",
    "clean_utility",
    "clean_utility_exact",
    "clean_utility_semantic",
    "false_positive_refusal",
    "verification_attempted",
    "effective_verification",
]


def wilson_interval(successes: int, n: int, z: float = 1.959963984540054) -> tuple[float | None, float | None]:
    if n <= 0:
        return None, None
    phat = successes / n
    denom = 1 + z * z / n
    center = (phat + z * z / (2 * n)) / denom
    margin = z * math.sqrt((phat * (1 - phat) + z * z / (4 * n)) / n) / denom
    return max(0.0, center - margin), min(1.0, center + margin)


def rows_from_summary(summary: dict[str, Any]) -> list[dict[str, Any]]:
    if isinstance(summary.get("cells"), list):
        return list(summary["cells"])
    if isinstance(summary.get("scored"), list):
        return list(summary["scored"])
    raise KeyError("summary has neither cells nor scored")


def summarize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for row in rows:
        key = (str(row.get("model")), str(row.get("agent_profile")), str(row.get("mode")))
        buckets.setdefault(key, []).append(row)

    out = []
    for (model, profile, mode), items in sorted(buckets.items()):
        n = len(items)
        metric_summary = {}
        for metric in METRICS:
            successes = sum(int(bool(item.get(metric))) for item in items)
            lo, hi = wilson_interval(successes, n)
            metric_summary[metric] = {
                "successes": successes,
                "n": n,
                "rate": successes / n if n else None,
                "wilson95_low": lo,
                "wilson95_high": hi,
            }
        api_errors = sum(int(bool(item.get("api_error") or item.get("parse_error"))) for item in items)
        tool_calls = [int(item.get("tool_call_count", 0)) for item in items]
        out.append(
            {
                "model": model,
                "agent_profile": profile,
                "mode": mode,
                "n": n,
                "api_or_parse_errors": api_errors,
                "mean_tool_call_count": sum(tool_calls) / n if n else None,
                "metrics": metric_summary,
            }
        )
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize model-policy result JSON with Wilson 95% intervals.")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    summary = json.loads(Path(args.summary).read_text(encoding="utf-8"))
    rows = rows_from_summary(summary)
    output = {
        "source_summary": args.summary,
        "interval": "Wilson score 95%",
        "denominator_policy": "attempted cells; API/parse errors are counted separately and remain in denominators",
        "groups": summarize(rows),
    }
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(out_path)


if __name__ == "__main__":
    main()
