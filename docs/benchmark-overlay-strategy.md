# Benchmark overlay strategy

This document is the compact strategy note for the open repository. Detailed
experiment rules live in `docs/benchmark-baseline-contract.md`; manuscript
claims and results live in `docs/paper-draft-zh.md`.

## Core principle

The paper should not use a self-created toy benchmark as the main evidence.
Instead:

```text
existing benchmark task + unchanged hidden state/oracle
  -> truthful model-visible observation
  -> spoofed model-visible observation
  -> same task, same hidden truth, different defense baselines
```

The local scenario suite is retained only for unit tests, smoke tests, and
regression examples. Paper-grade evidence must come from existing benchmark
substrates such as ToolSandbox and AgentDojo.

## Substrate priority

| Substrate | Priority | Role in this project |
| --- | --- | --- |
| AgentDojo | P0 | Existing agent-security benchmark substrate. Full 97-task overlay is complete, but still trace-final-decision rather than autonomous full agent loop. |
| ToolSandbox | P0 | Existing stateful tool-use benchmark substrate. Full overlay is running on the remote benchmark host. |
| tau-bench / tau2-bench | P1 | Next realistic business API substrate for order/refund/reservation status spoofing. |
| WebArena / WorkArena | P1 | Browser/UI observation spoofing: false DOM, a11y, or success-banner observations while backend truth is unchanged. |
| SWE-bench / SWE-agent | P1 | Shell/test-output spoofing: false stdout, exit code, or test summary while oracle reruns real tests. |
| MCP Security/Safety benchmarks | P1 | Close-work comparison and possible protocol-level response-integrity substrate. |
| PoisonedRAG / SafeRAG | P2 | Retrieval/citation provenance spoofing substrate. |

## Baseline hierarchy

The same hierarchy should be reused across substrates whenever possible:

1. `naive`: trust the first visible observation.
2. `schema-only`: validate format/type only.
3. `prompt-filter`: scan for instruction-like payloads.
4. `repeat-same-tool`: call the same channel again.
5. `metadata-only`: check freshness/provenance metadata without content truth.
6. `read-back validator`: query a split-channel canonical read path.
7. `independent authority`: query signed scope, registry, or challenge-response
   authority when deployable.
8. `combined policy`: compose validation and uncertainty gates.
9. `privileged oracle upper bound`: hidden-truth validator for ablation only,
   never a deployable defense claim.

## Prompt-leakage invariants

Model-visible prompts must not include:

- `oracle_context`;
- raw hidden `truth_result` or `raw_tool_result`;
- `truthful` / `spoofed` condition labels;
- hidden expected scores or success criteria;
- raw internal profile names;
- ground-truth tool-plan metadata, except as already manifested in visible tool
  events.

Read-back observations are allowed only as explicit second visible tool results.

## Current full-run command shape

ToolSandbox:

```bash
PYTHONPATH=src:. python3 scripts/run_toolsandbox_model_pilot.py \
  --config configs/experiments/toolsandbox_model_full.json \
  --manifest outputs/toolsandbox_full_manifest.json \
  --toolsandbox-path /tmp/ToolSandbox \
  --out-dir traces/toolsandbox_model_full \
  --summary outputs/toolsandbox_model_full_summary.json \
  --run-manifest outputs/toolsandbox_model_full_manifest.json
```

AgentDojo:

```bash
PYTHONPATH=src:. python3 scripts/run_agentdojo_model_pilot.py \
  --config configs/experiments/agentdojo_model_full.json \
  --manifest outputs/agentdojo_full_manifest.json \
  --agentdojo-path /tmp/AgentDojo \
  --out-dir traces/agentdojo_model_full \
  --summary outputs/agentdojo_model_full_summary.json \
  --run-manifest outputs/agentdojo_model_full_manifest.json
```

Shard summaries are merged with `scripts/merge_model_shards.py`; confidence
intervals are generated with `scripts/summarize_model_results_with_ci.py`.

## Claim boundary

The current ToolSandbox/AgentDojo runners perform scripted tool-plan or
ground-truth tool-plan trace construction followed by a model final-decision
prompt. They are real benchmark-substrate overlays, but they are not full
autonomous agent-loop interception. The manuscript must state this boundary in
the abstract, contributions, experiments, figures, and limitations unless a
separate autonomous-loop experiment is added.
