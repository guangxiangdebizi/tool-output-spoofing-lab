from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REQUIRED_KEYS = {
    "id",
    "domain",
    "spoof_class",
    "task",
    "ground_truth",
    "truthful_tool_result",
    "spoofed_tool_result",
    "expected_safe_behavior",
    "success_criteria",
}


@dataclass(frozen=True)
class Scenario:
    path: Path
    data: dict[str, Any]

    @property
    def id(self) -> str:
        return str(self.data["id"])

    def tool_result(self, mode: str) -> dict[str, Any]:
        if mode == "truthful":
            return dict(self.data["truthful_tool_result"])
        if mode == "spoofed":
            return dict(self.data["spoofed_tool_result"])
        raise ValueError(f"unknown mode: {mode}")


def load_scenario(path: str | Path) -> Scenario:
    scenario_path = Path(path)
    data = json.loads(scenario_path.read_text(encoding="utf-8"))
    missing = REQUIRED_KEYS.difference(data)
    if missing:
        raise ValueError(f"{scenario_path} missing required keys: {sorted(missing)}")
    return Scenario(path=scenario_path, data=data)


def scenario_to_public_task(scenario: Scenario) -> dict[str, Any]:
    return {
        "scenario_id": scenario.id,
        "domain": scenario.data["domain"],
        "spoof_class": scenario.data["spoof_class"],
        "task": scenario.data["task"],
    }
