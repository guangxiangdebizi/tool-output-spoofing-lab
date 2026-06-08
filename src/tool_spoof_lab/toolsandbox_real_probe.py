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
    status = check_toolsandbox_available(path)
    if not status.available:
        raise RuntimeError(
            "ToolSandbox is not importable. Install it in an isolated environment "
            "or pass --toolsandbox-path pointing to a cloned https://github.com/apple/ToolSandbox. "
            f"Import error: {status.error}"
        )
    from tool_sandbox.common.tool_discovery import ToolBackend  # type: ignore
    from tool_sandbox.scenarios import named_scenarios  # type: ignore

    return named_scenarios(preferred_tool_backend=ToolBackend.DEFAULT)


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


def build_manifest(
    *,
    toolsandbox_path: str | Path | None = None,
    task_names: list[str] | None = None,
    limit: int | None = 12,
) -> dict[str, Any]:
    scenarios = load_real_scenarios(toolsandbox_path)
    selected = select_task_names(list(scenarios), task_names, limit=limit)
    tasks = []
    for name in selected:
        scenario = scenarios[name]
        tasks.append(
            {
                "task_id": name,
                "source": "apple/ToolSandbox",
                "real_benchmark_run": False,
                "manifest_only": True,
                "tool_allow_list": scenario.starting_context.tool_allow_list,
                "tool_deny_list": scenario.starting_context.tool_deny_list,
                "categories": [_enum_value(category) for category in scenario.categories],
                "max_messages": scenario.max_messages,
                "starting_state_preview": summarize_starting_state(scenario),
                "milestone_oracle": summarize_milestones(scenario),
            }
        )
    return {
        "substrate": "ToolSandbox",
        "source_repo": "https://github.com/apple/ToolSandbox",
        "manifest_only": True,
        "real_benchmark_run": False,
        "total_available_scenarios": len(scenarios),
        "selected_count": len(tasks),
        "selection_policy": "named default overlay candidates, capped by --limit",
        "tasks": tasks,
    }


def write_manifest(manifest: dict[str, Any], output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
