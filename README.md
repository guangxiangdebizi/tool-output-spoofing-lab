# Tool Output Spoofing Lab

Research scaffold for studying how AI agents can be deceived by fabricated,
tampered, stale, or malicious tool outputs.

## Thesis

Tool-integrated LLM agents often treat tool results as authoritative
observations. This lab studies the failure mode where the tool side returns
mocked or spoofed data and the agent converts that untrusted observation into
an incorrect report, decision, or action.

The intended research question is narrow:

> If the prompt is benign but the tool result is adversarial or fabricated,
> how reliably do agents detect, cross-check, or propagate the false state?

## Non-goals

- Not a phishing/scam toolkit.
- Not a real credential, production API, or third-party service testbed.
- Not focused on classic user-prompt jailbreaks unless they are embedded in
  tool results.
- Not designed to run destructive actions; scenarios should use local mocks.

## Repository map

```text
configs/
  benchmark_overlays/
  experiments/       Experiment matrices and model/tool settings.
  scenarios/         Scenario definitions consumed by mock tools.
docs/
  benchmark-overlay-strategy.md
  concept.md         Research framing and non-goals.
  threat-model.md    Assets, attackers, trust boundaries, attack classes.
  engineering-plan.md
  experiment-plan.md
  paper-draft.md     First full manuscript-style draft.
  paper-draft-zh.md  Current Chinese working draft.
  venue-strategy.md  Target venue and deadline strategy.
  literature-matrix.md
  reading-template.md
mocks/
  scenarios/         Example benign and spoofed tool outputs.
papers/              Downloaded public PDFs, grouped by lane.
secondary-research/
  deep-dive/         Subagent audit outputs.
src/tool_spoof_lab/
  mock_server.py     Local tool server returning configured observations.
  scenario.py        Scenario loading and validation helpers.
  oracle.py          Expected-behavior evaluator for traces.
  structured_oracle.py
  runner.py          Minimal deterministic runner for smoke tests.
tests/               Lightweight stdlib smoke tests.
traces/              Agent/tool traces; keep generated traces out of git.
outputs/             Reports and generated artifacts; keep large outputs out.
```

## First local smoke test

Use Python 3.10+; on this host the default `python` is 3.6, while
`/usr/bin/python3.11` is available.

```bash
PYTHONPATH=src /usr/bin/python3.11 -m tool_spoof_lab.runner --scenario configs/scenarios/minimal_false_success.json
PYTHONPATH=src /usr/bin/python3.11 -m tool_spoof_lab.oracle --trace traces/minimal_false_success.spoofed.naive_accepts_tool.trace.jsonl
PYTHONPATH=src /usr/bin/python3.11 scripts/run_mvp_matrix.py --config configs/experiments/mvp_matrix.json --out-dir traces
PYTHONPATH=src:. /usr/bin/python3.11 scripts/run_structured_partial.py --config configs/experiments/mvp_matrix.json --out-dir traces/structured_15scenario_partial --summary outputs/structured_partial_summary.json
PYTHONPATH=src:. /usr/bin/python3.11 scripts/run_real_toolcall_pilot.py --config configs/experiments/real_toolcall_pilot_small.json --out-dir traces/real_toolcall_pilot_dry --summary outputs/real_toolcall_pilot_dry_summary.json --manifest outputs/real_toolcall_pilot_dry_manifest.json --dry-run --sleep 0
PYTHONPATH=src:. /usr/bin/python3.11 scripts/run_toolsandbox_overlay_smoke.py --config configs/benchmark_overlays/toolsandbox_overlay_smoke.json --out-dir traces/toolsandbox_overlay_smoke --summary outputs/toolsandbox_overlay_smoke_summary.json
PYTHONPATH=src:. /tmp/toolsandbox-probe-venv/bin/python scripts/probe_toolsandbox_real.py --toolsandbox-path /tmp/ToolSandbox --limit 12 --output outputs/toolsandbox_real_manifest.json
PYTHONPATH=src:. /usr/bin/python3.11 scripts/run_toolsandbox_real_bringup.py --manifest outputs/toolsandbox_real_manifest.json --out-dir traces/toolsandbox_real_bringup --summary outputs/toolsandbox_real_bringup_summary.json
PYTHONPATH=src:. /usr/bin/python3.11 -m unittest discover -s tests -v
```

The scaffold intentionally avoids installing packages or downloading models on
this host.

## Current paper direction

The strongest narrowed claim is not "tool outputs are untrusted" in general;
that is already covered by nearby work. The current paper direction is:

> Adding an observation-spoofing overlay to existing agent/tool-use benchmarks:
> schema-valid but semantically false tool observations with paired
> hidden-truth/visible-observation traces and observation-integrity defenses.

Start with `docs/paper-draft-zh.md`, `docs/paper-draft.md`,
`docs/benchmark-overlay-strategy.md`, `docs/partial-pilot-results.md`,
`docs/novelty-audit.md`, and `docs/venue-strategy.md`.
