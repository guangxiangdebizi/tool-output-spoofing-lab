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
- `figures/figure8_validator_independence_graph.png`
- `figures/figure9_pilot_vs_agent_loop_gap.png`
- `figures/figure10_end_to_end_harness_dataflow.svg`
- `figures/figure11_scoring_projection_boundary.svg`
- `figures/figure12_experiment_completion_heatmap.svg`
- `figures/figure13_per_substrate_overlay_instantiation.svg`

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
  threat-model.md    Assets, attackers, trust boundaries, attack classes.
  paper-draft-zh.md  Current Chinese working draft.
  pre_registered_scoring_contract.md
  ccfa-review-gap-analysis.md
  novelty-audit.md
  literature-matrix.md
mocks/
  scenarios/         Example benign and spoofed tool outputs.
papers/              Downloaded public PDFs, grouped by lane.
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

## Minimal local validation

Use Python 3.10+; on this host the default `python` is 3.6, while
`/usr/bin/python3.11` is available.

```bash
PYTHONPATH=src:. /usr/bin/python3.11 -m unittest discover -s tests -v
```

Generated traces stay out of git. External benchmark packages are installed only
in isolated `/tmp/*-probe-venv` environments on the remote cloud host, not
vendored into this repository.

## Full benchmark run shape

The current paper-grade runs use existing benchmark substrates, not the local
smoke suite:

```bash
PYTHONPATH=src:. python3 scripts/run_toolsandbox_model_pilot.py \
  --config configs/experiments/toolsandbox_model_full.json \
  --manifest outputs/toolsandbox_full_manifest.json \
  --toolsandbox-path /tmp/ToolSandbox \
  --out-dir traces/toolsandbox_model_full \
  --summary outputs/toolsandbox_model_full_summary.json \
  --run-manifest outputs/toolsandbox_model_full_manifest.json

PYTHONPATH=src:. python3 scripts/run_agentdojo_model_pilot.py \
  --config configs/experiments/agentdojo_model_full.json \
  --manifest outputs/agentdojo_full_manifest.json \
  --agentdojo-path /tmp/AgentDojo \
  --out-dir traces/agentdojo_model_full \
  --summary outputs/agentdojo_model_full_summary.json \
  --run-manifest outputs/agentdojo_model_full_manifest.json
```

`outputs/agentdojo_model_full_*.json` is the first completed full-overlay run.
ToolSandbox full results are generated on the remote benchmark host and then
post-processed with:

```bash
scripts/postprocess_full_model_run.sh \
  --summary-glob 'outputs/toolsandbox_model_full_shard*_summary.json' \
  --manifest-glob 'outputs/toolsandbox_model_full_shard*_manifest.json' \
  --summary-out outputs/toolsandbox_model_full_summary.json \
  --manifest-out outputs/toolsandbox_model_full_manifest.json \
  --ci-out outputs/toolsandbox_model_full_ci.json \
  --leakage-out outputs/prompt_leakage_audit_toolsandbox_full_gpt54.json \
  --stats-out outputs/toolsandbox_model_full_stats.json \
  --reference-profile toolsandbox_exec_naive
```

## Current paper direction

The strongest narrowed claim is not "tool outputs are untrusted" in general;
that is already covered by nearby work. The current paper direction is:

> Adding an observation-spoofing overlay to existing agent/tool-use benchmarks:
> schema-valid but semantically false tool observations with paired
> hidden-truth/visible-observation traces and observation-integrity defenses.

Start with `docs/paper-draft-zh.md`,
`docs/benchmark-baseline-contract.md`, `docs/benchmark-overlay-strategy.md`,
`docs/ccfa-review-gap-analysis.md`, `docs/novelty-audit.md`,
`docs/literature-matrix.md`, `docs/threat-model.md`, and
`docs/trace-schema.md`.

The Chinese draft is currently the most complete manuscript-style version. It
includes formal related work, benchmark-overlay design, defense baselines,
metrics, pilot result tables, limitations, responsible release notes, and
numbered references.

For manuscript numbers, use only `outputs/main_pilot_index.json` and the
explicitly listed full-run artifacts under `outputs/`. Older dry-run and
intermediate summaries are intentionally not kept in the open repository.

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
