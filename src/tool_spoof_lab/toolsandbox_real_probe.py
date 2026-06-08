from __future__ import annotations

import importlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_TASKS = [
    "get_wifi",
    "wifi_off",
    "add_contact_with_name_and_phone_number",
    "update_contact_with_id_and_phone_number",
    "remove_contact_with_id",
    "search_message_with_recency_latest",
    "send_message_with_phone_number_and_content",
    "send_message_with_contact_content_cellular_off",
    "search_reminder_with_recency_upcoming",
    "add_reminder_content_and_date_and_time",
    "modify_reminder_with_recency_latest",
    "remove_reminder_with_recency_latest",
]

_SCENARIO_CACHE: dict[str, dict[str, Any]] = {}


@dataclass(frozen=True)
class ToolSandboxImportStatus:
    available: bool
    error: str | None = None


def add_toolsandbox_path(path: str | Path | None) -> None:
    if path:
        sys.path.insert(0, str(Path(path).resolve()))


def check_toolsandbox_available(path: str | Path | None = None) -> ToolSandboxImportStatus:
    add_toolsandbox_path(path)
    try:
        importlib.import_module("tool_sandbox.scenarios")
        importlib.import_module("tool_sandbox.common.tool_discovery")
    except Exception as exc:  # pragma: no cover - exact optional dependency varies by machine.
        return ToolSandboxImportStatus(False, f"{type(exc).__name__}: {exc}")
    return ToolSandboxImportStatus(True)


def load_real_scenarios(path: str | Path | None = None) -> dict[str, Any]:
    cache_key = str(Path(path).resolve()) if path else "__default__"
    if cache_key in _SCENARIO_CACHE:
        return _SCENARIO_CACHE[cache_key]
    status = check_toolsandbox_available(path)
    if not status.available:
        raise RuntimeError(
            "ToolSandbox is not importable. Install it in an isolated environment "
            "or pass --toolsandbox-path pointing to a cloned https://github.com/apple/ToolSandbox. "
            f"Import error: {status.error}"
        )
    from tool_sandbox.common.tool_discovery import ToolBackend  # type: ignore
    from tool_sandbox.scenarios import named_scenarios  # type: ignore

    scenarios = named_scenarios(preferred_tool_backend=ToolBackend.DEFAULT)
    _SCENARIO_CACHE[cache_key] = scenarios
    return scenarios


def _enum_value(value: Any) -> str:
    return str(getattr(value, "value", value))


def dataframe_preview(dataframe: Any, *, max_rows: int = 3) -> list[dict[str, Any]]:
    try:
        return dataframe.head(max_rows).to_dicts()
    except Exception:
        return []


def summarize_milestones(scenario: Any) -> list[dict[str, Any]]:
    milestones = getattr(scenario.evaluation.milestone_matcher, "milestones", [])
    summary: list[dict[str, Any]] = []
    for index, milestone in enumerate(milestones):
        constraints = []
        for constraint in getattr(milestone, "snapshot_constraints", []):
            constraints.append(
                {
                    "database_namespace": _enum_value(constraint.database_namespace),
                    "snapshot_constraint": getattr(
                        constraint.snapshot_constraint, "__name__", str(constraint.snapshot_constraint)
                    ),
                    "reference_milestone_node_index": constraint.reference_milestone_node_index,
                    "target_preview": dataframe_preview(constraint.target_dataframe),
                }
            )
        summary.append({"milestone_index": index, "snapshot_constraints": constraints})
    return summary


def summarize_starting_state(scenario: Any) -> dict[str, Any]:
    from tool_sandbox.common.execution_context import DatabaseNamespace  # type: ignore

    context = scenario.starting_context
    summary: dict[str, Any] = {}
    for namespace in [
        DatabaseNamespace.SETTING,
        DatabaseNamespace.CONTACT,
        DatabaseNamespace.MESSAGING,
        DatabaseNamespace.REMINDER,
    ]:
        db = context.get_database(namespace)
        summary[_enum_value(namespace)] = {
            "rows": db.height if hasattr(db, "height") else None,
            "preview": dataframe_preview(db),
        }
    return summary


def select_task_names(
    available_names: list[str],
    requested: list[str] | None,
    *,
    limit: int | None = None,
) -> list[str]:
    available = set(available_names)
    if requested:
        selected = [name for name in requested if name in available]
    else:
        selected = [name for name in DEFAULT_TASKS if name in available]
    if limit is not None:
        if not requested and len(selected) < limit:
            selected_set = set(selected)
            selected.extend(name for name in sorted(available_names) if name not in selected_set)
        selected = selected[:limit]
    missing = [] if requested is None else [name for name in requested if name not in available]
    if missing:
        raise KeyError(f"ToolSandbox scenarios not found: {missing}")
    return selected


def scenario_metadata(name: str, scenario: Any) -> dict[str, Any]:
    categories = [_enum_value(category) for category in scenario.categories]
    tool_allow_list = list(scenario.starting_context.tool_allow_list)
    mutating_keywords = ("add_", "modify_", "remove_", "send_", "set_", "turn_on", "turn_off", "_off")
    read_only = not any(str(tool).startswith(mutating_keywords) for tool in tool_allow_list)
    return {
        "task_id": name,
        "categories": categories,
        "tool_allow_count": len(tool_allow_list),
        "single_turn": "SINGLE_USER_TURN" in categories,
        "multi_turn": "MULTIPLE_USER_TURN" in categories,
        "single_tool": "SINGLE_TOOL_CALL" in categories,
        "multi_tool": "MULTIPLE_TOOL_CALL" in categories,
        "insufficient_information": "INSUFFICIENT_INFORMATION" in categories,
        "distraction": any("DISTRACTION_TOOLS" in category for category in categories),
        "state_dependency": "STATE_DEPENDENCY" in categories,
        "canonicalization": "CANONICALIZATION" in categories,
        "read_only_by_allow_list": read_only,
    }


def _task_score(metadata: dict[str, Any]) -> tuple[int, int, str]:
    priority = 0
    if metadata["task_id"] in DEFAULT_TASKS:
        priority -= 1000
    priority += int(metadata["tool_allow_count"])
    priority += 3 if metadata["multi_tool"] else 0
    priority += 2 if metadata["multi_turn"] else 0
    priority += 2 if metadata["state_dependency"] else 0
    priority += 1 if metadata["insufficient_information"] else 0
    return (priority, metadata["tool_allow_count"], metadata["task_id"])


def select_stratified_task_names(
    scenarios: dict[str, Any],
    *,
    target_count: int,
) -> tuple[list[str], dict[str, Any]]:
    if target_count <= 0:
        return [], {"target_count": target_count, "strata": {}}
    metadata = {name: scenario_metadata(name, scenario) for name, scenario in scenarios.items()}
    strata: dict[str, list[str]] = {
        "single_turn": [name for name, item in metadata.items() if item["single_turn"]],
        "multi_turn": [name for name, item in metadata.items() if item["multi_turn"]],
        "single_tool": [name for name, item in metadata.items() if item["single_tool"]],
        "multi_tool": [name for name, item in metadata.items() if item["multi_tool"]],
        "insufficient_information": [name for name, item in metadata.items() if item["insufficient_information"]],
        "distraction": [name for name, item in metadata.items() if item["distraction"]],
        "no_distraction": [name for name, item in metadata.items() if not item["distraction"]],
        "state_dependency": [name for name, item in metadata.items() if item["state_dependency"]],
        "canonicalization": [name for name, item in metadata.items() if item["canonicalization"]],
        "read_only": [name for name, item in metadata.items() if item["read_only_by_allow_list"]],
        "mutation": [name for name, item in metadata.items() if not item["read_only_by_allow_list"]],
    }
    quotas = {
        key: min(len(names), max(1, round(target_count * len(names) / len(scenarios))))
        for key, names in strata.items()
        if names
    }
    selected: list[str] = []
    selected_set: set[str] = set()
    candidate_lists = {
        key: sorted(names, key=lambda name: _task_score(metadata[name]))
        for key, names in strata.items()
        if names
    }
    selected_by_stratum = {key: 0 for key in candidate_lists}
    cursors = {key: 0 for key in candidate_lists}
    stratum_order = sorted(candidate_lists, key=lambda item: (-quotas.get(item, 0), item))
    while len(selected) < target_count:
        progress = False
        for key in stratum_order:
            if selected_by_stratum[key] >= quotas.get(key, 0):
                continue
            candidates = candidate_lists[key]
            while cursors[key] < len(candidates) and candidates[cursors[key]] in selected_set:
                cursors[key] += 1
            if cursors[key] >= len(candidates):
                continue
            name = candidates[cursors[key]]
            selected.append(name)
            selected_set.add(name)
            selected_by_stratum[key] += 1
            progress = True
            if len(selected) >= target_count:
                break
        if not progress:
            break
    if len(selected) < target_count:
        for name in sorted(scenarios, key=lambda name: _task_score(metadata[name])):
            if name in selected_set:
                continue
            selected.append(name)
            selected_set.add(name)
            if len(selected) >= target_count:
                break
    counts = {
        key: {
            "available": len(names),
            "selected": sum(1 for name in selected if name in set(names)),
            "quota": quotas.get(key, 0),
        }
        for key, names in strata.items()
    }
    return selected, {
        "target_count": target_count,
        "available_count": len(scenarios),
        "selected_count": len(selected),
        "selection_policy": "deterministic multi-label stratified slice over ToolSandbox scenario categories",
        "strata": counts,
    }


def build_manifest(
    *,
    toolsandbox_path: str | Path | None = None,
    task_names: list[str] | None = None,
    limit: int | None = 12,
    stratified: bool = False,
) -> dict[str, Any]:
    scenarios = load_real_scenarios(toolsandbox_path)
    stratification = None
    if stratified and task_names:
        raise ValueError("--stratified cannot be combined with explicit --tasks")
    if stratified:
        target_count = limit or max(1, round(len(scenarios) * 0.10))
        selected, stratification = select_stratified_task_names(scenarios, target_count=target_count)
    else:
        selected = select_task_names(list(scenarios), task_names, limit=limit)
    tasks = []
    for name in selected:
        scenario = scenarios[name]
        metadata = scenario_metadata(name, scenario)
        tasks.append(
            {
                "task_id": name,
                "source": "apple/ToolSandbox",
                "real_benchmark_run": False,
                "manifest_only": True,
                "tool_allow_list": scenario.starting_context.tool_allow_list,
                "tool_deny_list": scenario.starting_context.tool_deny_list,
                "categories": metadata["categories"],
                "sampling_metadata": metadata,
                "max_messages": scenario.max_messages,
                "starting_state_preview": summarize_starting_state(scenario),
                "milestone_oracle": summarize_milestones(scenario),
            }
        )
    selected_fraction = len(tasks) / float(len(scenarios)) if scenarios else None
    strict_quota_satisfied = bool(
        stratification
        and all(
            item["selected"] >= item["quota"]
            for item in stratification["strata"].values()
            if item["quota"] > 0
        )
    )
    return {
        "substrate": "ToolSandbox",
        "source_repo": "https://github.com/apple/ToolSandbox",
        "manifest_only": True,
        "real_benchmark_run": False,
        "total_available_scenarios": len(scenarios),
        "selected_count": len(tasks),
        "selected_fraction": selected_fraction,
        "target_10_percent_stratified_manifest": bool(
            stratified and selected_fraction is not None and 0.10 <= selected_fraction <= 0.15
        ),
        "executed_10_15_percent_slice": False,
        "strict_quota_satisfied": strict_quota_satisfied,
        "representative_10_15_percent_slice": False,
        "selection_policy": (
            "deterministic multi-label coverage manifest over ToolSandbox categories"
            if stratified
            else "named default overlay candidates, capped by --limit"
        ),
        "stratification": stratification,
        "tasks": tasks,
    }


def write_manifest(manifest: dict[str, Any], output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def load_manifest(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))
