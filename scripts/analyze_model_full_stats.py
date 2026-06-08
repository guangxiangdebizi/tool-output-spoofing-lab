from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


DEFAULT_METRICS = [
    "attack_success",
    "accepted_false_state",
    "clean_utility",
    "clean_utility_exact",
    "clean_utility_semantic",
    "false_positive_refusal",
]


def rows_from_summary(summary: dict[str, Any]) -> list[dict[str, Any]]:
    if isinstance(summary.get("cells"), list):
        return list(summary["cells"])
    if isinstance(summary.get("scored"), list):
        return list(summary["scored"])
    raise KeyError("summary has neither cells nor scored")


def profile_label(profile: str) -> str:
    for prefix in ("agentdojo_exec_", "toolsandbox_exec_"):
        if profile.startswith(prefix):
            return profile.removeprefix(prefix)
    return profile


def exact_mcnemar_p(a_only: int, b_only: int) -> float | None:
    n = a_only + b_only
    if n == 0:
        return None
    k = min(a_only, b_only)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / (2**n)
    return min(1.0, 2.0 * tail)


def paired_rows(
    rows: list[dict[str, Any]],
    *,
    mode: str,
    metric: str,
    reference_profile: str,
) -> list[dict[str, Any]]:
    by_profile: dict[str, dict[tuple[str, str], dict[str, Any]]] = {}
    for row in rows:
        if str(row.get("mode")) != mode:
            continue
        profile = str(row.get("agent_profile"))
        key = (str(row.get("model")), str(row.get("scenario_id")))
        by_profile.setdefault(profile, {})[key] = row

    reference = by_profile.get(reference_profile, {})
    out = []
    for profile, items in sorted(by_profile.items()):
        if profile == reference_profile:
            continue
        common_keys = sorted(set(reference) & set(items))
        both_true = a_only = b_only = both_false = 0
        for key in common_keys:
            a = bool(reference[key].get(metric))
            b = bool(items[key].get(metric))
            if a and b:
                both_true += 1
            elif a and not b:
                a_only += 1
            elif not a and b:
                b_only += 1
            else:
                both_false += 1
        n = len(common_keys)
        a_successes = both_true + a_only
        b_successes = both_true + b_only
        out.append(
            {
                "mode": mode,
                "metric": metric,
                "reference_profile": reference_profile,
                "comparison_profile": profile,
                "reference_label": profile_label(reference_profile),
                "comparison_label": profile_label(profile),
                "paired_n": n,
                "reference_successes": a_successes,
                "comparison_successes": b_successes,
                "both_true": both_true,
                "reference_only": a_only,
                "comparison_only": b_only,
                "both_false": both_false,
                "reference_rate": a_successes / n if n else None,
                "comparison_rate": b_successes / n if n else None,
                "comparison_minus_reference": (b_successes - a_successes) / n if n else None,
                "exact_mcnemar_p": exact_mcnemar_p(a_only, b_only),
            }
        )
    return out


def funnel(rows: list[dict[str, Any]], mode: str) -> list[dict[str, Any]]:
    by_profile: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        if str(row.get("mode")) == mode:
            by_profile.setdefault(str(row.get("agent_profile")), []).append(row)

    out = []
    for profile, items in sorted(by_profile.items()):
        n = len(items)
        api_or_parse = sum(int(bool(row.get("api_error") or row.get("parse_error"))) for row in items)
        uncertainty_or_refusal = sum(
            int(bool(row.get("uncertainty") or row.get("refused_or_deferred") or not row.get("action_commit")))
            for row in items
        )
        no_true_fields = sum(int(not bool(row.get("true_field_accepts"))) for row in items)
        false_field_accepts = sum(int(bool(row.get("false_field_accepts"))) for row in items)
        out.append(
            {
                "mode": mode,
                "agent_profile": profile,
                "profile_label": profile_label(profile),
                "n": n,
                "api_or_parse_errors": api_or_parse,
                "uncertain_refused_or_no_commit": uncertainty_or_refusal,
                "no_true_field_accepts": no_true_fields,
                "false_field_accepts": false_field_accepts,
                "action_commit": sum(int(bool(row.get("action_commit"))) for row in items),
                "clean_utility": sum(int(bool(row.get("clean_utility"))) for row in items),
                "clean_utility_exact": sum(int(bool(row.get("clean_utility_exact"))) for row in items),
                "clean_utility_semantic": sum(int(bool(row.get("clean_utility_semantic"))) for row in items),
                "semantic_projection_used": sum(int(bool(row.get("semantic_projection_used"))) for row in items),
                "semantic_only_utility": sum(
                    int(bool(row.get("clean_utility_semantic")) and not bool(row.get("clean_utility_exact")))
                    for row in items
                ),
                "false_positive_refusal": sum(int(bool(row.get("false_positive_refusal"))) for row in items),
                "attack_success": sum(int(bool(row.get("attack_success"))) for row in items),
                "accepted_false_state": sum(int(bool(row.get("accepted_false_state"))) for row in items),
                "verification_attempted": sum(int(bool(row.get("verification_attempted"))) for row in items),
                "effective_verification": sum(int(bool(row.get("effective_verification"))) for row in items),
                "mean_tool_call_count": (
                    sum(int(row.get("tool_call_count", 0)) for row in items) / n if n else None
                ),
            }
        )
    return out


def add_holm_adjusted_p(rows: list[dict[str, Any]]) -> None:
    families: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for row in rows:
        if row.get("exact_mcnemar_p") is None:
            row["holm_adjusted_p"] = None
            continue
        key = (str(row["mode"]), str(row["metric"]), str(row["reference_profile"]))
        families.setdefault(key, []).append(row)

    for items in families.values():
        ordered = sorted(items, key=lambda row: float(row["exact_mcnemar_p"]))
        running_max = 0.0
        m = len(ordered)
        for rank, row in enumerate(ordered, start=1):
            adjusted = min(1.0, (m - rank + 1) * float(row["exact_mcnemar_p"]))
            running_max = max(running_max, adjusted)
            row["holm_adjusted_p"] = running_max


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create paired tests and utility diagnostics from a model full-run summary."
    )
    parser.add_argument("--summary", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--reference-profile", default="agentdojo_exec_naive")
    parser.add_argument("--metric", action="append", default=[])
    args = parser.parse_args()

    summary_path = Path(args.summary)
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    rows = rows_from_summary(summary)
    metrics = args.metric or DEFAULT_METRICS
    paired = []
    for mode in sorted({str(row.get("mode")) for row in rows}):
        for metric in metrics:
            paired.extend(
                paired_rows(
                    rows,
                    mode=mode,
                    metric=metric,
                    reference_profile=args.reference_profile,
                )
            )
    add_holm_adjusted_p(paired)

    output = {
        "analysis_id": "model_full_stats_v1",
        "source_summary": str(summary_path),
        "reference_profile": args.reference_profile,
        "paired_test": "exact McNemar/binomial sign test over discordant paired tasks",
        "multiple_testing_correction": "Holm correction within each (mode, metric, reference_profile) family",
        "denominator_policy": "paired tests use common (model, scenario_id) cells between the reference and comparison profile",
        "paired_comparisons": paired,
        "clean_utility_funnel": funnel(rows, "truthful"),
        "spoofed_security_funnel": funnel(rows, "spoofed"),
    }
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(out_path)


if __name__ == "__main__":
    main()
