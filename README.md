# Tool Output Spoofing Lab

Research scaffold for studying how AI agents can be deceived by fabricated,
tampered, stale, or malicious tool outputs.

## Thesis

Tool-integrated LLM agents often treat tool results as authoritative
observations. This lab studies the failure mode where the tool side returns
mocked or spoofed data and the agent converts that untrusted observation into
an incorrect report, decision, or action.

![Tool-output spoofing overview](figures/figure1_tool_output_spoofing_overview.png)

Editable source for the overview figure is in
`figures/figure1_tool_output_spoofing_overview.svg`.

Additional paper figures are available in:

- `figures/figure2_benchmark_baseline_matrix.png`
- `figures/figure3_authorization_evidence_ladder.png`
- `figures/figure4_pilot_result_snapshot.png`
- `figures/figure7_observation_spoofing_overlay.png`

One important axis is authorization/provenance spoofing: a tool may falsely
report that a sandbox asset is owned, in scope, or backed by nginx/banner,
certificate, or asset-inventory evidence. The benchmark records whether an
agent escalates from passive triage to active assessment based on that
unverified observation. Local scenarios score authorization verdicts only; they
do not ask models to produce exploit steps.

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
  benchmark-baseline-contract.md
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
PYTHONPATH=src:. /usr/bin/python3.11 scripts/run_structured_partial.py --config configs/experiments/mvp_matrix.json --out-dir traces/structured_16scenario_partial --summary outputs/structured_16scenario_partial_summary.json
PYTHONPATH=src:. /usr/bin/python3.11 scripts/run_real_toolcall_pilot.py --config configs/experiments/real_toolcall_pilot_small.json --out-dir traces/real_toolcall_pilot_dry --summary outputs/real_toolcall_pilot_dry_summary.json --manifest outputs/real_toolcall_pilot_dry_manifest.json --dry-run --sleep 0
PYTHONPATH=src:. /usr/bin/python3.11 scripts/run_toolsandbox_overlay_smoke.py --config configs/benchmark_overlays/toolsandbox_overlay_smoke.json --out-dir traces/toolsandbox_overlay_smoke --summary outputs/toolsandbox_overlay_smoke_summary.json
PYTHONPATH=src:. /tmp/toolsandbox-probe-venv/bin/python scripts/probe_toolsandbox_real.py --toolsandbox-path /tmp/ToolSandbox --limit 12 --output outputs/toolsandbox_real_manifest.json
PYTHONPATH=src:. /usr/bin/python3.11 scripts/run_toolsandbox_real_bringup.py --manifest outputs/toolsandbox_real_manifest.json --out-dir traces/toolsandbox_real_bringup --summary outputs/toolsandbox_real_bringup_summary.json
PYTHONPATH=src:. /tmp/toolsandbox-probe-venv/bin/python scripts/run_toolsandbox_execution_smoke.py --manifest outputs/toolsandbox_real_manifest.json --toolsandbox-path /tmp/ToolSandbox --out-dir traces/toolsandbox_execution_smoke --summary outputs/toolsandbox_execution_smoke_summary.json --limit-tasks 12
PYTHONPATH=src:. /tmp/toolsandbox-probe-venv/bin/python scripts/run_toolsandbox_model_pilot.py --config configs/experiments/toolsandbox_model_pilot_small.json --manifest outputs/toolsandbox_real_manifest.json --toolsandbox-path /tmp/ToolSandbox --out-dir traces/toolsandbox_model_pilot_dry --summary outputs/toolsandbox_model_pilot_dry_summary.json --run-manifest outputs/toolsandbox_model_pilot_dry_manifest.json --dry-run --sleep 0
PYTHONPATH=src:. /tmp/toolsandbox-probe-venv/bin/python scripts/probe_toolsandbox_real.py --toolsandbox-path /tmp/ToolSandbox --limit 104 --stratified --output outputs/toolsandbox_stratified_10pct_manifest.json
PYTHONPATH=src:. /tmp/agentdojo-probe-venv/bin/python scripts/probe_agentdojo_real.py --agentdojo-path /tmp/AgentDojo --benchmark-version v1.2.2 --limit 12 --stratified --output outputs/agentdojo_real_manifest.json
PYTHONPATH=src:. /tmp/agentdojo-probe-venv/bin/python scripts/run_agentdojo_execution_smoke.py --manifest outputs/agentdojo_real_manifest.json --agentdojo-path /tmp/AgentDojo --benchmark-version v1.2.2 --out-dir traces/agentdojo_execution_smoke --summary outputs/agentdojo_execution_smoke_summary.json --limit-tasks 12
PYTHONPATH=src:. /tmp/agentdojo-probe-venv/bin/python scripts/run_agentdojo_model_pilot.py --config configs/experiments/agentdojo_model_pilot_small.json --manifest outputs/agentdojo_real_manifest.json --agentdojo-path /tmp/AgentDojo --out-dir traces/agentdojo_model_pilot_dry --summary outputs/agentdojo_model_pilot_dry_summary.json --run-manifest outputs/agentdojo_model_pilot_dry_manifest.json --dry-run --sleep 0
PYTHONPATH=src:. /usr/bin/python3.11 -m unittest discover -s tests -v
```

Generated traces and output manifests stay out of git. External benchmark
packages are installed only in isolated `/tmp/*-probe-venv` environments on the
remote cloud host, not vendored into this repository.

## Current paper direction

The strongest narrowed claim is not "tool outputs are untrusted" in general;
that is already covered by nearby work. The current paper direction is:

> Adding an observation-spoofing overlay to existing agent/tool-use benchmarks:
> schema-valid but semantically false tool observations with paired
> hidden-truth/visible-observation traces and observation-integrity defenses.

Start with `docs/paper-draft-zh.md`, `docs/paper-draft.md`,
`docs/benchmark-baseline-contract.md`, `docs/benchmark-overlay-strategy.md`,
`docs/partial-pilot-results.md`, `docs/novelty-audit.md`, and
`docs/venue-strategy.md`.

The Chinese draft is currently the most complete manuscript-style version. It
includes formal related work, benchmark-overlay design, defense baselines,
metrics, pilot result tables, limitations, responsible release notes, and
numbered references.

For manuscript numbers, use only `outputs/main_pilot_index.json` as the
canonical pilot-result index. Older summaries/manifests are retained for
traceability and may contain stale wording. `docs/paper-draft.md` is an older
English draft; `docs/paper-draft-zh.md` is the current working manuscript.

`docs/benchmark-baseline-contract.md` is the current fixed experiment contract:
it defines the benchmark unit, existing-benchmark grounding, observation
generator constraints, deployable vs upper-bound baselines, the
authorization/provenance evidence ladder, and the minimum paper-grade model-cell
matrix.

## License

The repository's original code, configs, docs, scripts, tests, traces, and
generated experiment outputs are released under the Apache License 2.0. See
`LICENSE`.

The `papers/` directory contains third-party public research PDFs retained for
research traceability. Those PDFs remain under their original authors',
publishers', or distributors' terms and are not relicensed by this repository.
