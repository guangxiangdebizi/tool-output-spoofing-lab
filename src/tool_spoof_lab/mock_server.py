from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .scenario import Scenario, load_scenario


class ToolSpoofHandler(BaseHTTPRequestHandler):
    scenarios: dict[str, Scenario] = {}

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler name
        path = urlparse(self.path).path.strip("/").split("/")
        if path == ["health"]:
            self._send_json(200, {"ok": True, "scenarios": sorted(self.scenarios)})
            return

        if len(path) == 3 and path[0] == "tool":
            _, scenario_id, mode = path
            scenario = self.scenarios.get(scenario_id)
            if scenario is None:
                self._send_json(404, {"error": "unknown scenario", "scenario_id": scenario_id})
                return
            try:
                self._send_json(200, scenario.tool_result(mode))
            except ValueError as exc:
                self._send_json(400, {"error": str(exc)})
            return

        self._send_json(404, {"error": "not found"})

    def log_message(self, fmt: str, *args) -> None:
        return


def load_scenarios(paths: list[str]) -> dict[str, Scenario]:
    scenarios = {}
    for raw_path in paths:
        scenario = load_scenario(Path(raw_path))
        scenarios[scenario.id] = scenario
    return scenarios


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve local mock tool outputs.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8765, type=int)
    parser.add_argument("--scenario", action="append", required=True)
    args = parser.parse_args()

    ToolSpoofHandler.scenarios = load_scenarios(args.scenario)
    server = ThreadingHTTPServer((args.host, args.port), ToolSpoofHandler)
    print(f"serving {len(ToolSpoofHandler.scenarios)} scenarios on http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
