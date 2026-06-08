from __future__ import annotations

import importlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_SUITES = ["workspace", "travel", "banking", "slack"]
DEFAULT_BENCHMARK_VERSION = "v1.2.2"


@dataclass(frozen=True)
class AgentDojoImportStatus:
    available: bool
    error: str | None = None


def add_agentdojo_path(path: str | Path | None) -> None:
    if path:
        sys.path.insert(0, str(Path(path).resolve() / "src"))
        sys.path.insert(0, str(Path(path).resolve()))


def check_agentdojo_available(path: str | Path | None = None) -> AgentDojoImportStatus:
    add_agentdojo_path(path)
    try:
        importlib.import_module("agentdojo.task_suite.load_suites")
    except Exception as exc:  # pragma: no cover - optional dependency varies by machine.
        return AgentDojoImportStatus(False, f"{type(exc).__name__}: {exc}")
    return AgentDojoImportStatus(True)


def _value(value: Any) -> Any:
    if hasattr(value, "value"):
        return value.value
    return value


def _stringify(value: Any) -> str | None:
    if value is None:
        return None
    if hasattr(value, "name"):
        return str(value.name).lower()
    return str(_value(value))


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if hasattr(value, "model_dump"):
        return _json_safe(value.model_dump())
    if hasattr(value, "dict"):
        return _json_safe(value.dict())
    if hasattr(value, "value"):
        return _json_safe(value.value)
    return repr(value)


def _load_suite(benchmark_version: str, suite_name: str) -> Any:
    from agentdojo.task_suite.load_suites import get_suite  # type: ignore

    return get_suite(benchmark_version, suite_name)


def _ground_truth_calls(task: Any, environment: Any) -> tuple[list[dict[str, Any]], str | None]:
    try:
        calls = task.ground_truth(environment)
    except Exception as exc:  # pragma: no cover - exact task failure is dependency-specific.
        return [], f"{type(exc).__name__}: {exc}"
    return [_json_safe(call) for call in calls], None


def _tool_names(tools: list[Any]) -> list[str]:
    return [str(getattr(tool, "name", repr(tool))) for tool in tools]


def _task_metadata(
    *,
    suite_name: str,
    benchmark_version: str,
    task_id: str,
    task: Any,
    suite: Any,
    environment: Any,
) -> dict[str, Any]:
    ground_truth_calls, ground_truth_error = _ground_truth_calls(task, environment)
    ground_truth_functions = [str(call.get("function")) for call in ground_truth_calls if isinstance(call, dict)]
    mutating_prefixes = ("send_", "reserve_", "book_", "pay_", "transfer_", "create_", "delete_", "update_", "add_", "remove_")
    read_only = not any(function.startswith(mutating_prefixes) for function in ground_truth_functions)
    return {
        "task_id": task_id,
        "suite": suite_name,
        "benchmark_version": benchmark_version,
        "prompt": getattr(task, "PROMPT", ""),
        "difficulty": _stringify(getattr(task, "DIFFICULTY", None)),
        "ground_truth_output": getattr(task, "GROUND_TRUTH_OUTPUT", ""),
        "ground_truth_calls": ground_truth_calls,
        "ground_truth_error": ground_truth_error,
        "ground_truth_call_count": len(ground_truth_calls),
        "ground_truth_functions": ground_truth_functions,
        "read_only_by_ground_truth": read_only,
        "tool_count": len(suite.tools),
        "tool_names": _tool_names(suite.tools),
        "injection_task_count": len(suite.injection_tasks),
        "injection_task_ids": list(suite.injection_tasks)[:20],
    }


def load_real_tasks(
    *,
    agentdojo_path: str | Path | None = None,
    benchmark_version: str = DEFAULT_BENCHMARK_VERSION,
    suites: list[str] | None = None,
) -> list[dict[str, Any]]:
    status = check_agentdojo_available(agentdojo_path)
    if not status.available:
        raise RuntimeError(
            "AgentDojo is not importable. Install it in an isolated environment or pass "
            "--agentdojo-path pointing to a cloned https://github.com/ethz-spylab/agentdojo. "
            f"Import error: {status.error}"
        )
    task_rows: list[dict[str, Any]] = []
    for suite_name in suites or DEFAULT_SUITES:
        suite = _load_suite(benchmark_version, suite_name)
        environment = suite.load_and_inject_default_environment({})
        for task_id, task in suite.user_tasks.items():
            task_rows.append(
                _task_metadata(
                    suite_name=suite_name,
                    benchmark_version=benchmark_version,
                    task_id=task_id,
                    task=task,
                    suite=suite,
                    environment=environment,
                )
            )
    return task_rows


def _task_score(task: dict[str, Any]) -> tuple[int, int, str, str]:
    priority = 0
    priority += 4 if not task.get("read_only_by_ground_truth") else 0
    priority += int(task.get("ground_truth_call_count") or 0)
    difficulty = str(task.get("difficulty") or "")
    priority += {"hard": 3, "medium": 2, "easy": 1}.get(difficulty.lower(), 0)
    return (-priority, int(task.get("ground_truth_call_count") or 0), str(task.get("suite")), str(task.get("task_id")))


def select_stratified_tasks(
    tasks: list[dict[str, Any]],
    *,
    target_count: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if target_count <= 0:
        return [], {"target_count": target_count, "available_count": len(tasks), "selected_count": 0, "strata": {}}
    target_count = min(target_count, len(tasks))
    strata: dict[str, list[dict[str, Any]]] = {}
    for task in tasks:
        strata.setdefault(f"suite:{task['suite']}", []).append(task)
        difficulty = str(task.get("difficulty") or "unknown").lower()
        strata.setdefault(f"difficulty:{difficulty}", []).append(task)
        strata.setdefault("read_only" if task.get("read_only_by_ground_truth") else "mutation", []).append(task)
        call_count = int(task.get("ground_truth_call_count") or 0)
        strata.setdefault("single_call" if call_count <= 1 else "multi_call", []).append(task)

    quotas = {
        key: min(len(items), max(1, round(target_count * len(items) / len(tasks))))
        for key, items in strata.items()
        if items
    }
    selected: list[dict[str, Any]] = []
    selected_ids: set[tuple[str, str]] = set()
    candidate_lists = {key: sorted(items, key=_task_score) for key, items in strata.items()}
    selected_by_stratum = {key: 0 for key in candidate_lists}
    cursors = {key: 0 for key in candidate_lists}
    stratum_order = sorted(candidate_lists, key=lambda key: (-quotas.get(key, 0), key))

    while len(selected) < target_count:
        progress = False
        for key in stratum_order:
            if selected_by_stratum[key] >= quotas.get(key, 0):
                continue
            candidates = candidate_lists[key]
            while cursors[key] < len(candidates):
                candidate = candidates[cursors[key]]
                candidate_id = (str(candidate["suite"]), str(candidate["task_id"]))
                if candidate_id not in selected_ids:
                    break
                cursors[key] += 1
            if cursors[key] >= len(candidates):
                continue
            candidate = candidates[cursors[key]]
            selected.append(candidate)
            selected_ids.add((str(candidate["suite"]), str(candidate["task_id"])))
            selected_by_stratum[key] += 1
            progress = True
            if len(selected) >= target_count:
                break
        if not progress:
            break

    if len(selected) < target_count:
        for candidate in sorted(tasks, key=_task_score):
            candidate_id = (str(candidate["suite"]), str(candidate["task_id"]))
            if candidate_id in selected_ids:
                continue
            selected.append(candidate)
            selected_ids.add(candidate_id)
            if len(selected) >= target_count:
                break

    strata_counts = {
        key: {
            "available": len(items),
            "selected": sum(
                1
                for task in selected
                if (str(task["suite"]), str(task["task_id"]))
                in {(str(item["suite"]), str(item["task_id"])) for item in items}
            ),
            "quota": quotas.get(key, 0),
        }
        for key, items in strata.items()
    }
    return selected, {
        "target_count": target_count,
        "available_count": len(tasks),
        "selected_count": len(selected),
        "selection_policy": "deterministic stratified slice over suite, difficulty, mutating/read-only, and call-count strata",
        "strata": strata_counts,
    }


def select_tasks(
    tasks: list[dict[str, Any]],
    *,
    requested: list[str] | None = None,
    limit: int | None = 12,
    stratified: bool = False,
) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    if stratified and requested:
        raise ValueError("--stratified cannot be combined with explicit --tasks")
    if requested:
        requested_set = set(requested)
        selected = [
            task
            for task in tasks
            if task["task_id"] in requested_set or f"{task['suite']}:{task['task_id']}" in requested_set
        ]
        found = {task["task_id"] for task in selected} | {f"{task['suite']}:{task['task_id']}" for task in selected}
        missing = [task_id for task_id in requested if task_id not in found]
        if missing:
            raise KeyError(f"AgentDojo tasks not found: {missing}")
        return selected[:limit] if limit is not None else selected, None
    if stratified:
        target_count = limit or max(1, round(len(tasks) * 0.10))
        return select_stratified_tasks(tasks, target_count=target_count)
    return sorted(tasks, key=_task_score)[:limit] if limit is not None else sorted(tasks, key=_task_score), None


def build_manifest(
    *,
    agentdojo_path: str | Path | None = None,
    benchmark_version: str = DEFAULT_BENCHMARK_VERSION,
    suites: list[str] | None = None,
    task_ids: list[str] | None = None,
    limit: int | None = 12,
    stratified: bool = False,
) -> dict[str, Any]:
    tasks = load_real_tasks(
        agentdojo_path=agentdojo_path,
        benchmark_version=benchmark_version,
        suites=suites or DEFAULT_SUITES,
    )
    selected, stratification = select_tasks(tasks, requested=task_ids, limit=limit, stratified=stratified)
    selected_fraction = len(selected) / float(len(tasks)) if tasks else None
    strict_quota_satisfied = bool(
        stratification
        and all(
            item["selected"] >= item["quota"]
            for item in stratification["strata"].values()
            if item["quota"] > 0
        )
    )
    return {
        "substrate": "AgentDojo",
        "source_repo": "https://github.com/ethz-spylab/agentdojo",
        "paper": "https://arxiv.org/abs/2406.13352",
        "benchmark_version": benchmark_version,
        "suite_names": suites or DEFAULT_SUITES,
        "manifest_only": True,
        "real_benchmark_run": False,
        "real_model_run": False,
        "overlay_target": "tool-visible factual/status-field spoofing overlay on existing AgentDojo user tasks; distinct from AgentDojo's native indirect-prompt-injection attacks",
        "total_available_user_tasks": len(tasks),
        "selected_count": len(selected),
        "selected_fraction": selected_fraction,
        "target_10_15_percent_stratified_manifest": bool(
            stratified and selected_fraction is not None and 0.10 <= selected_fraction <= 0.15
        ),
        "executed_10_15_percent_slice": False,
        "strict_quota_satisfied": strict_quota_satisfied,
        "representative_10_15_percent_slice": False,
        "selection_policy": (
            "deterministic stratified manifest over AgentDojo suites, difficulty, mutating/read-only tasks, and call-count"
            if stratified
            else "highest-priority overlay candidates, capped by --limit"
        ),
        "stratification": stratification,
        "tasks": selected,
    }


def write_manifest(manifest: dict[str, Any], output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def load_manifest(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))
