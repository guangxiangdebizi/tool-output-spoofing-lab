# Engineering Plan

## Constraints for this host

- Do not create a virtual environment.
- Do not install packages.
- Do not download model weights or benchmark datasets.
- Do not call production services.
- Keep generated traces and outputs small and reproducible.

## Components

### Scenario config

JSON file with:

- id, domain, task
- ground_truth
- truthful_tool_result
- spoofed_tool_result
- expected_safe_behavior
- success_criteria

### Mock tool server

`src/tool_spoof_lab/mock_server.py` serves local JSON responses:

- `/health`
- `/tool/<scenario_id>/truthful`
- `/tool/<scenario_id>/spoofed`

### Runner

`src/tool_spoof_lab/runner.py` generates a minimal trace using deterministic
agent profiles. Later adapters can call real agents.

### Oracle

`src/tool_spoof_lab/oracle.py` reads JSONL traces and scores:

- accepted_spoof
- requested_corroboration
- surfaced_uncertainty
- ignored_instruction_smuggling

## Later adapters

Add under `src/tool_spoof_lab/adapters/`:

- `openai_agents.py`
- `anthropic_claude.py`
- `browser_agent.py`
- `mcp_client.py`

Each adapter should write the same trace schema.

## Trace schema

One JSON object per line:

```json
{
  "scenario_id": "minimal_false_success",
  "mode": "spoofed",
  "turn": 1,
  "event": "tool_result",
  "payload": {},
  "timestamp": "2026-06-08T00:00:00+08:00"
}
```

## Reproducibility rule

Every experiment must save:

- scenario config hash
- model/agent identifier
- defense setting
- full tool request/result
- final answer/action
- oracle verdict
