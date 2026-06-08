# Reviewer iteration log

This file records internal reviewer-style criticism and resulting revisions.

## Round 0: self-review before external/subagent critique

### Main weaknesses

1. **Novelty is fragile.** Trust No Tool, MCP Security Bench, MCP-SafetyBench,
   AgentDojo, InjecAgent, and CaMeL are close. The paper must not claim broad
   novelty around untrusted tool outputs or MCP response attacks.
2. **Current code is only an MVP.** Two local scenarios and deterministic agent
   stubs are enough for a scaffold, not for a top-tier claim.
3. **Defense claims need actual implementation.** Provenance, signed receipts,
   freshness, and cross-tool verification are currently planned, not measured.
4. **Benchmark size is underspecified.** A serious submission needs a target
   number of scenarios, model families, and suite coverage.
5. **Venue strategy must account for real deadlines.** S&P 2027 first deadline
   is too soon as of 2026-06-08; USENIX Security 2027 Cycle 1 and NDSS 2027 fall
   are the realistic fast targets.

### Changes made after self-review

- Added `docs/paper-draft.md` with a full first manuscript draft and narrowed
  contribution claims.
- Added `docs/venue-strategy.md` with target venues and current deadline
  implications.
- Kept "Weak Go" language and emphasized exact differentiator:
  schema-valid false observations with paired hidden-truth/visible-observation
  traces.

## Round 1: attempted subagent critique

Two independent reviewer subagents were launched to inspect the repository and
produce rejection risks plus concrete modifications. Both failed due to the
configured model backend, not due to repository state:

1. The configured model backend returned HTTP 521.
2. The second attempt disconnected before `response.completed`.

Because the external reviewer path was unavailable, the main agent performed a
local strict-review pass instead of blocking all progress.

## Round 1 local strict-review findings

### Reject risks

1. The title and abstract must avoid sounding like "first untrusted tool
   output paper"; that claim is blocked by Trust No Tool, MSB,
   MCP-SafetyBench, AgentDojo, and InjecAgent.
2. A two-scenario MVP is not enough for a top-tier paper; the benchmark must
   become a multi-suite artifact with at least 150-300 paired scenario records
   or a smaller but deeply realistic domain-specific suite.
3. Prompt-filter comparisons are only useful if the semantic-falsehood cases
   contain no instruction-like text. The paper must separate instruction
   smuggling controls from the core no-instruction attack set.
4. Cross-tool verification must be budget-controlled; otherwise reviewers will
   say the defense simply sees more evidence.
5. Defense implementation must include clean-utility measurements on truthful
   cases; blanket skepticism is not acceptable.
6. The artifact must not leak API keys, SSH credentials, GitHub tokens, or live
   service endpoints.

### Revisions made after local review

- Expanded the MVP matrix from two scenarios to five vertical suites plus one
  instruction-smuggling control:
  - API false success;
  - MCP forged receipt;
  - RAG forged citation;
  - browser fake success banner;
  - shell exit-code spoof;
  - instruction-smuggling JSON control.
- Added deterministic baseline profiles:
  - naive accept;
  - schema-only;
  - prompt-filter-only;
  - provenance/corroboration cautious policy;
  - cross-tool verifier.
- Updated oracle scoring to use per-scenario success criteria instead of only
  generic keywords.
- Recorded that subagent review remains incomplete because the configured
  external model backend failed twice.

## Round 2: subagent reviewer critique after initial pilots

A reviewer subagent completed a USENIX/S&P-style review after the six-scenario
NewAPI smoke pilot and the first benchmark draft.

### Reviewer decision

**Reject for current top-tier submission; Weak Go as a research direction.**

The core reason was not that the idea is weak. The issue was that the evidence
was still underpowered:

1. The six-scenario model pilot was a smoke test, not a benchmark-scale
   experiment.
2. The model harness passed `visible_tool_result` directly in user JSON, so it
   was closer to single-observation reading comprehension than a full
   tool-using agent benchmark.
3. The `verification_required` prompt was too strong as a defense baseline
   because it directly warned that tool outputs may be stale, forged, or
   semantically false.
4. The oracle was keyword-based and could mis-score negated or mixed answers.
5. Several spoofed fixtures leaked obvious fake markers.
6. Close work such as Trust No Tool, MCP Security Bench, MCP-SafetyBench,
   AgentDojo, InjecAgent, ToolEmu, CaMeL, and AttriGuard still compresses the
   novelty claim.

### Changes made after Round 2 critique

- Expanded the local smoke suite from 6 to 15 scenarios. This was later
  explicitly downgraded from benchmark evidence to regression/smoke coverage.
- Added nine new scenario records:
  - `api_fabricated_entity`
  - `api_schema_valid_false_value`
  - `api_stale_replay`
  - `mcp_parameter_binding_mismatch`
  - `mcp_false_error_blocks_action`
  - `rag_warning_stripping`
  - `rag_conflicting_source_fake_authority`
  - `browser_submitted_target_mismatch`
  - `shell_truncated_log_spoof`
- Ran the deterministic 15-scenario matrix:
  - 15 scenarios x 2 modes x 5 baselines = 150 cells.
  - naive ASR: 15/15 spoofed cases.
  - schema-only ASR: 15/15 spoofed cases.
  - prompt-filter-only ASR: 14/15 spoofed cases; it only blocked the
    instruction-smuggling control.
  - provenance/corroboration policy ASR: 0/15 spoofed cases.
  - cross-tool verifier ASR: 0/15 spoofed cases.
- Reclassified the earlier `gpt-5.4-mini` run as a six-scenario real-model
  smoke pilot rather than benchmark evidence.
- Added `configs/experiments/partial_pilot_newapi_smoke6.json` to preserve the
  old smoke-pilot configuration separately from the new 15-scenario pilot
  config.
- Updated `docs/paper-draft.md` to include concrete benchmark counts,
  baseline access assumptions, pilot result tables, and the remaining
  limitations.
- Updated `docs/partial-pilot-results.md` with deterministic local smoke results
  and explicit non-paper-grade limitations.

### Remaining blockers before a reviewer could move above Reject

The current state still should not be represented as top-tier-ready. The next
iteration needs:

1. a real tool-call harness instead of direct observation-in-context prompts;
2. a 30-45 paired-scenario model pilot, not only deterministic stubs;
3. at least two models;
4. structured final-answer schema and field-level oracle scoring;
5. truthful clean-utility and false-positive refusal measurement;
6. actual repeat-same-tool, independent-validator, signed-receipt, freshness,
   and combined defenses under fixed budgets;
7. plausible spoofed fixtures with fewer obvious fake markers; and
8. close-work comparison or ablation against Trust No Tool / MCP benchmarks
   where feasible.

## Round 3: structured oracle and Chinese working draft

After the Round 2 reviewer noted that the artifact was still keyword-scored and
did not measure clean utility/FPR, the following changes were made:

- Added `src/tool_spoof_lab/structured_oracle.py` for field-level scoring.
- Added `scripts/run_structured_partial.py`, which emits explicit
  `visible_tool_result`, `repeat_tool_call`, `validator_call`,
  `freshness_check`, and `structured_final` events.
- Added structured tests in `tests/test_smoke.py`.
- Ran the 15-scenario structured local smoke suite:
  - 15 scenarios x 2 modes x 6 structured profiles = 180 cells.
  - naive ASR: 15/15; clean utility: 15/15.
  - schema-only ASR: 15/15; clean utility: 15/15.
  - prompt-filter ASR: 14/15; clean utility: 15/15.
  - repeat-same-tool ASR: 15/15; clean utility: 15/15.
  - independent-validator ASR: 0/15; clean utility: 13/15; FPR: 2/15.
  - combined-policy ASR: 0/15; clean utility: 15/15; FPR: 0/15.
- Added `docs/paper-draft-zh.md` as the current Chinese working draft.
- Updated `docs/paper-draft.md` and `docs/partial-pilot-results.md` with
  structured results and the remaining limitations.

This addresses part of the previous P0 list: structured final-answer schema,
field-level oracle, repeat-same-tool comparison, explicit validator event, and
truthful clean utility/FPR are now present for the local scripted slice. It does
not yet address the larger P0 requirements: real model agent harness, 30-45
paired real-model pilot, multiple models, signed receipts, and close-work
ablation.

## Round 4: subagent review of Chinese draft and structured slice

A third reviewer subagent reviewed the Chinese working draft, structured oracle,
structured runner, and tests.

### Reviewer decision

**Borderline as an artifact/research draft; Weak Reject as a USENIX Security /
IEEE S&P / CCS submission today.**

The reviewer explicitly confirmed that the Chinese draft now clearly includes:

- benchmark definition;
- 15-scenario local smoke suite;
- baseline design;
- deterministic 150-cell results;
- structured 180-cell results;
- real-model smoke pilot;
- honest claim boundaries.

The reviewer also confirmed that the structured oracle and 180-cell structured
local smoke run materially address part of the prior P0 list:

- field-level decisive fields;
- structured final-answer scoring;
- false-field and true-field acceptance;
- ASR, clean utility, FPR, and effective verification;
- explicit `visible_tool_result`, `repeat_tool_call`, `validator_call`,
  `freshness_check`, and `structured_final` events;
- smoke tests covering structured naive, validator, and truthful utility.

### Remaining P0 from Round 4

The work is still not Weak Accept because:

1. main results are still scripted baselines, not true model-driven tool-calling
   agents;
2. independent validator data is still scenario-provided rather than a runtime
   budgeted validator service;
3. freshness is currently a metadata event, not a real security decision;
4. signed receipt verification is not implemented;
5. the benchmark has only 15 hand-written scenarios;
6. real-model evidence is still only the six-scenario smoke pilot.

The next three highest-impact changes are:

1. implement a real tool-call harness and run a 30-45 paired-scenario
   real-model pilot with at least two models;
2. expand structured scoring into a paper-grade run manifest with forced final
   schema validation, per-suite metrics, token/latency/tool budgets, retry and
   timeout policy, trace hashes, and confidence intervals;
3. implement real signed-receipt, freshness, independent read-after-write, and
   combined-policy baselines with fail-open/fail-closed behavior and truthful
   utility/FPR reporting.

## Round 5: real tool-call harness scaffold

To address the Round 4 P0 that the real-model smoke pilot was direct
observation-in-context prompting rather than a true tool-call harness, the
repository now includes:

- `configs/experiments/real_toolcall_pilot_small.json`
- `scripts/run_real_toolcall_pilot.py`
- `src/tool_spoof_lab/openai_compat.py`

The new runner builds harness-controlled tool events before asking the model
for a structured final decision. It records:

- primary visible tool calls;
- schema validation events;
- prompt-filter checks;
- repeat-same-tool calls;
- independent validator calls;
- freshness metadata checks;
- signature metadata checks;
- structured final decisions;
- summary metrics; and
- a run manifest with config hash, model, temperature, max tokens, timeout,
  retries, tool budget, prompt hash, trace path, and API/parse errors.

Dry-run status:

- Command executed with `--dry-run --sleep 0`.
- Expected cells without limit: 96.
- Completed dry-run cells: 96.
- The current shell had no `NEWAPI_API_KEY`, so no new result-bearing model
  cells were executed in this round.

This moves the artifact closer to a paper-grade agent harness, but the main P0
remains open until the 96-cell local-harness real-model pilot and the later 30-45
paired-scenario multi-model pilot are actually run.

Reviewer follow-up identified and fixed two leakage risks before any real-model
run:

- the model-visible prompt no longer exposes `truthful` / `spoofed` mode;
- the model-visible prompt no longer exposes raw profile names such as
  `toolcall_naive`; it uses policy ids and natural-language policy
  instructions instead.

It also identified limitations that remain intentionally documented:

- this is still a harness-controlled tool-event evaluation, not an autonomous
  API function-calling loop;
- signature and freshness events are metadata checks until real cryptographic
  signatures, freshness windows, nonces, and request binding are implemented.

## Round 6: targeted review after leakage fixes

A targeted subagent review checked the P0 issues found in Round 5. Result:
**passed targeted review**.

Confirmed fixes:

1. The model-visible prompt no longer leaks `truthful` / `spoofed` mode. The
   runner uses an opaque `condition_id`.
2. The model-visible prompt no longer leaks raw `toolcall_*` profile names. It
   uses `policy_id` plus natural-language policy instructions.
3. Dry-run documentation no longer includes `--limit-cells 12`, and the
   dry-run artifacts are consistent: expected 96, completed 96, manifest rows
   96.
4. `schema_validation_result()` is stricter than the prior placeholder: all
   required keys from the truthful result must be present, and non-null fields
   must match type.
5. Signed/freshness language has been downgraded to metadata checks until real
   cryptographic signatures, freshness windows, nonces, and request binding are
   implemented.

The targeted reviewer reported no remaining P0 in this fix list. The next-stage
P0 remains unchanged: run a real-model 48/96-cell pilot, then scale to 30-45
paired scenarios and at least two models.

## Round 7: benchmark-substrate correction

User feedback identified a major positioning issue: the main benchmark should
not be primarily self-created toy scenarios. A more valuable CCF-A-style design
should build on existing high-value benchmarks and compare different baselines
on the same tasks.

Resulting strategy change:

- The 15-scenario local suite is now explicitly labeled a smoke suite.
- The main benchmark is reframed as an **observation-spoofing overlay** for
  existing agent/tool-use benchmarks.
- Added `docs/benchmark-overlay-strategy.md`.
- Added `configs/benchmark_overlays/high_value_benchmark_overlay.json`.
- Updated the Chinese draft, English draft, experiment plan, novelty audit, and
  README to reflect this shift.

Priority substrates:

1. ToolSandbox: deterministic execution context and milestone oracle.
2. AgentDojo: strong security benchmark positioning.
3. tau-bench / tau2-bench: realistic retail/airline tool-calling API tasks.
4. WebArena/WorkArena, SWE-bench/SWE-agent, MCP-SafetyBench/MSB, and RAG
   security benchmarks as second-wave overlays or close-work comparisons.

Remaining P0 after this correction:

1. implement at least one real overlay adapter, preferably ToolSandbox first;
2. run a small existing-benchmark overlay pilot;
3. then run the real-model 48/96-cell pilot on benchmark-derived tasks rather
   than only local smoke scenarios.

Environment note from this run:

- cwd: `/root/tool-output-spoofing-lab`
- hostname: `iZ6we8fiuw0w22z1nbjy18Z`
- user: `root`
- OS: Alibaba Cloud Linux 3.2104
- virtualization: KVM

This appears to be a remote Alibaba Cloud VM rather than a local laptop. The
current shell did not expose `NEWAPI_API_KEY` or `OPENAI_API_KEY`, so result-
bearing API experiments were not run in this turn.

## Round 8: ToolSandbox adapter-contract scaffold

The first existing-benchmark substrate work has started with ToolSandbox.

Added:

- `configs/benchmark_overlays/toolsandbox_overlay_smoke.json`
- `src/tool_spoof_lab/toolsandbox_overlay.py`
- `scripts/run_toolsandbox_overlay_smoke.py`

The current environment does not have ToolSandbox installed, so this is an
adapter-contract smoke scaffold rather than a real ToolSandbox benchmark run.
It verifies that ToolSandbox-shaped state snapshots / milestone oracles can be
mapped into the unified trace format:

```text
state snapshot / milestone oracle -> hidden truth
agent-visible tool return         -> observation plane
snapshot read                     -> independent validator
```

Smoke status:

- `scripts/run_toolsandbox_overlay_smoke.py` completed.
- `tests/test_smoke.py` includes ToolSandbox overlay contract tests.
- naive profile is vulnerable on spoofed observation.
- independent validator uses the state snapshot and blocks attack success.

Round 8 reviewer risk: fixture traces could contaminate real benchmark result
aggregation if they only say `substrate=ToolSandbox`. Fix: all emitted
adapter-contract rows now include row-level provenance fields
`adapter_contract=true`, `fixture=true`, and `real_benchmark_run=false`. Real
ToolSandbox integrations must flip these fields and include package/task/evaluator
metadata.

Remaining P0: install/use the real ToolSandbox package and replace fixtures with
10-15 real ToolSandbox tasks and state snapshots.

## Round 9: Real ToolSandbox manifest probe

Implemented a manifest-only probe for the real Apple ToolSandbox repository:

- `configs/benchmark_overlays/toolsandbox_real_probe.json`
- `src/tool_spoof_lab/toolsandbox_real_probe.py`
- `scripts/probe_toolsandbox_real.py`

Probe command used on this VM:

```bash
git clone https://github.com/apple/ToolSandbox /tmp/ToolSandbox
/usr/bin/python3.11 -m venv /tmp/toolsandbox-probe-venv
/tmp/toolsandbox-probe-venv/bin/python -m pip install \
  polars==0.20.31 networkx==3.2.1 numpy==1.26.4 scipy==1.13.1 \
  attrs dill==0.3.8 StrEnum==0.4.15 tqdm rouge-score==0.1.2 \
  rapidfuzz==3.9.3 phonenumbers==8.13.39 pint==0.23 geopy==2.4.1 \
  holidays==0.51 ccy==1.3.1 decorator==5.1.1 typing_extensions==4.12.2 \
  pydantic==2.7.4 pyyaml==6.0.1 requests==2.32.3 jsonschema==4.19.2 \
  langchain-core==0.1.14 langsmith==0.0.83 jsonpatch==1.33 \
  tenacity==8.4.1 anyio httpx sniffio distro jiter openai==1.17.0 \
  anthropic==0.26.1
PYTHONPATH=src:. /tmp/toolsandbox-probe-venv/bin/python scripts/probe_toolsandbox_real.py \
  --toolsandbox-path /tmp/ToolSandbox \
  --limit 12 \
  --output outputs/toolsandbox_real_manifest.json
```

Result:

- `total_available_scenarios=1032`
- `selected_count=12`
- selected bring-up seed includes `get_wifi`, `wifi_off`, add/update/remove
  contact, search/send message, and search/add/modify/remove reminder tasks.

This is stronger than the fixture smoke because task IDs, tool allow lists,
starting state previews, and milestone oracle metadata come from the real
ToolSandbox definitions. It is still `manifest_only=true` and
`real_benchmark_run=false`: no model executed, no tool return was intercepted,
and no attack/defense ASR can be claimed from this probe.

Reviewer correction: this is a 12-task engineering bring-up seed, not a
representative 10-15% sample of ToolSandbox. Since the probe found 1032
available scenarios, a literal 10-15% slice would require roughly 103-155 tasks
and stratification over scenario category, tool count, turn count, state
mutation/read-only, distraction/no-distraction, and insufficient-information
variants. The 12-task seed is only meant to validate the executable overlay
adapter before scaling.

Next P0: convert the manifest slice into executable overlay cells:

```text
12 real ToolSandbox tasks
truthful + spoofed modes
naive / schema-only / repeat-same-tool / independent-validator
= 96 cells before adding a second model or second substrate
```

## Round 10: 96-cell scripted ToolSandbox bring-up

Added:

- `src/tool_spoof_lab/toolsandbox_real_bringup.py`
- `scripts/run_toolsandbox_real_bringup.py`

Command:

```bash
PYTHONPATH=src:. /usr/bin/python3.11 scripts/run_toolsandbox_real_bringup.py \
  --manifest outputs/toolsandbox_real_manifest.json \
  --out-dir traces/toolsandbox_real_bringup \
  --summary outputs/toolsandbox_real_bringup_summary.json
```

Result:

- `completed_cells=96`
- real ToolSandbox task IDs and milestone-oracle metadata are used.
- `manifest_derived_scripted_bringup=true`
- `scripted_oracle_bringup=true`
- `real_benchmark_task=true`
- `real_benchmark_run=false`
- `real_model_run=false`
- `real_execution_interception=false`

Aggregate:

```text
naive spoofed ASR                 = 12/12
schema-only spoofed ASR           = 12/12
repeat-same-tool spoofed ASR      = 12/12
independent-validator spoofed ASR = 0/12
truthful clean utility            = 12/12 for all four profiles
```

Interpretation: this validates the 12-task × 2-mode × 4-baseline matrix,
provenance fields, trace schema, and oracle scoring over real ToolSandbox task
metadata. It does not yet prove model behavior or executable observation
interception. The emitted observation event is intentionally named
`visible_oracle_projection`, not `visible_tool_result`, because this runner
projects milestone metadata into the unified scoring schema rather than
intercepting natural ToolSandbox tool returns.

Remaining P0: implement the ToolSandbox role/execution interception path so
agent-visible tool returns can be changed while the real execution context and
milestone evaluator remain authoritative.

## Round 11: Real ToolSandbox tool-execution interception smoke

Added:

- `src/tool_spoof_lab/toolsandbox_execution_smoke.py`
- `scripts/run_toolsandbox_execution_smoke.py`

Command:

```bash
PYTHONPATH=src:. /tmp/toolsandbox-probe-venv/bin/python scripts/run_toolsandbox_execution_smoke.py \
  --manifest outputs/toolsandbox_real_manifest.json \
  --toolsandbox-path /tmp/ToolSandbox \
  --out-dir traces/toolsandbox_execution_smoke \
  --summary outputs/toolsandbox_execution_smoke_summary.json \
  --limit-tasks 12
```

Result:

- `executed_tasks=12`
- `completed_cells=144`
- `missing_tool_trace=0`
- `tool_call_exception=0`
- `real_tool_execution=true`
- `real_execution_interception=true`
- `trace_level_visible_result_substitution=true`
- `full_agent_loop_interception=false`
- `scripted_agent=true`
- `full_scenario_run=false`
- `real_model_run=false`
- `real_benchmark_run=false`

This is the first run that executes real ToolSandbox tools through
`ExecutionEnvironment` and records raw `tool_trace` / raw result before
constructing truthful or spoofed agent-visible observations. It is stronger than
the metadata bring-up, but it is still not model evidence because tool calls are
scripted and the full scenario conversation is not run.

Reviewer precision note: `real_execution_interception=true` in this smoke means
trace-level visible-result substitution after real ToolSandbox tool execution.
It does not mean full in-process agent-loop interception, so the summary also
records `full_agent_loop_interception=false`.

Remaining P0: replace the scripted tool-call plan with a real model/agent policy
over the same interception boundary, then run the 12-task pilot as a true
model-agent experiment.

## Round 12: reviewer audit, ToolSandbox model-policy dry-run, and 10% manifest

A new reviewer-style subagent audit checked the current benchmark/baseline
state after the ToolSandbox execution smoke.

### Reviewer decision

**Weak Reject.** The benchmark direction is now correct because it is based on
existing benchmark substrate + overlay, but the evidence is still engineering
bring-up rather than USENIX/S&P-grade benchmark evidence.

### Reviewer-confirmed supportable claims

- The main benchmark framing has moved away from self-built toy scenarios and
  toward ToolSandbox / AgentDojo / tau-bench overlays.
- Real Apple ToolSandbox scenario definitions are importable; current manifest
  probe found 1032 available scenarios and selected a 12-task bring-up seed.
- The same 12 real ToolSandbox task IDs can be compared across truthful/spoofed
  modes and four baselines.
- Real ToolSandbox single-tool execution through `ExecutionEnvironment` works,
  and raw result / tool_trace can be preserved while the trace-level visible
  observation is substituted.
- The Chinese draft contains benchmark, baseline, current result, and limitation
  sections.

### Reviewer reject risks

- 12 / 1032 tasks is not a 10%-15% ToolSandbox run.
- The 12-task selection is named/default bring-up, not stratified sampling.
- There is no result-bearing ToolSandbox real-model pilot yet.
- There is no full ToolSandbox agent loop or full scenario conversation.
- The independent validator remains oracle-adjacent because it uses raw
  truthful execution result rather than a deployed independent authority.
- Only one existing benchmark substrate has been partially integrated.

### Changes after this audit

Added:

- `src/tool_spoof_lab/toolsandbox_model_pilot.py`
- `scripts/run_toolsandbox_model_pilot.py`
- `configs/experiments/toolsandbox_model_pilot_small.json`

Dry-run command:

```bash
PYTHONPATH=src:. /tmp/toolsandbox-probe-venv/bin/python scripts/run_toolsandbox_model_pilot.py \
  --config configs/experiments/toolsandbox_model_pilot_small.json \
  --manifest outputs/toolsandbox_real_manifest.json \
  --toolsandbox-path /tmp/ToolSandbox \
  --out-dir traces/toolsandbox_model_pilot_dry \
  --summary outputs/toolsandbox_model_pilot_dry_summary.json \
  --run-manifest outputs/toolsandbox_model_pilot_dry_manifest.json \
  --dry-run --sleep 0
```

Result:

- `completed_cells=144`
- `expected_cells_without_limit=144`
- `selected_task_count=12`
- `selected_fraction=0.0116`
- `real_tool_execution=true`
- `trace_level_visible_result_substitution=true`
- `model_policy_prompted=true`
- `model_call_executed=false`
- `final_decision_source=dry_run_uncertainty_stub`
- `full_agent_loop_interception=false`
- `real_model_run=false`
- `representative_10_15_percent_slice=false`

The dry-run does not produce model ASR because the shell has no
`NEWAPI_API_KEY`, but it now exercises the ToolSandbox-specific model prompt,
manifest, and trace path. Tests verify that model-visible prompts do not leak
`oracle_context`, `raw_tool_result`, raw profile names, or truthful/spoofed
condition labels.

Also added stratified ToolSandbox manifest selection:

```bash
PYTHONPATH=src:. /tmp/toolsandbox-probe-venv/bin/python scripts/probe_toolsandbox_real.py \
  --toolsandbox-path /tmp/ToolSandbox \
  --limit 104 \
  --stratified \
  --output outputs/toolsandbox_stratified_10pct_manifest.json
```

Result:

- `selected_count=104`
- `total_available_scenarios=1032`
- `selected_fraction=0.1008`
- `target_10_percent_stratified_manifest=true`, `executed_10_15_percent_slice=false`, `strict_quota_satisfied=false`
- strata recorded over single/multiple user turn, single/multiple tool call,
  insufficient information, distraction/no-distraction, state dependency,
  canonicalization, and read-only/mutation.

This manifest is not executed yet; it is the scaling design for the next
larger ToolSandbox pilot after API/model access is available and the scripted
tool-call map is expanded.

Remaining P0:

1. run the 144-cell ToolSandbox model-policy pilot with a real API key;
2. expand from 12-task bring-up to the 104-task stratified manifest;
3. implement a non-oracle independent validator service;
4. integrate AgentDojo or tau-bench as a second existing benchmark substrate;
5. add confidence intervals, cost/latency accounting, and close-work
   crosswalks.

## Round 13: validator honesty ablation

The previous reviewer flagged `toolsandbox_exec_independent_validator` as
oracle-adjacent because it exposes the raw truthful ToolSandbox execution result
through a `validator_call`. To make the baseline hierarchy more honest, the
ToolSandbox execution/model pilot now separates:

- `toolsandbox_exec_metadata_validator`: non-privileged metadata-only check.
  It records `verification_source=metadata_only`,
  `validator_kind=trace_metadata_only`, `validator_privilege=non_privileged`,
  and `content_verified=false`.
- `toolsandbox_exec_readback_validator`: non-privileged read-back validator.
  It executes a second real ToolSandbox read tool in the same execution context
  and records `verification_source=independent_readback` and
  `validator_privilege=non_privileged_readback`.
- `toolsandbox_exec_independent_validator`: privileged upper-bound validator.
  It records `validator_kind=raw_toolsandbox_execution_result` and
  `validator_privilege=privileged_upper_bound`.

The ToolSandbox model-policy dry-run was re-run with six profiles:

```text
12 tasks x truthful/spoofed x
  naive / schema-only / repeat-same-tool /
  metadata-only validator / read-back validator / privileged independent-validator upper bound
= 144 cells
```

Dry-run summary:

- `completed_cells=144`
- `expected_cells_without_limit=144`
- metadata-only validator spoofed ASR in scripted scoring: 12 / 12
- read-back validator spoofed ASR in scripted scoring: 0 / 12
- privileged independent-validator spoofed ASR in scripted scoring: 0 / 12
- `real_model_run=false`
- `model_call_executed=false`

Interpretation: metadata-only validation and same-channel repetition do not
verify semantic truth. A content-level independent authority is required.
Read-back validation is the current deployability-oriented ToolSandbox
baseline; the raw-result validator remains only an upper-bound ablation. The
next paper-grade step is to run the read-back baseline with real model calls and
then scale it to the 104-task manifest.

## Round 14: AgentDojo second-substrate manifest

To address the concern that the experiment design was still anchored on a
single existing benchmark substrate, the repo now includes a real AgentDojo
manifest probe:

```bash
PYTHONPATH=src:. /tmp/agentdojo-probe-venv/bin/python scripts/probe_agentdojo_real.py \
  --agentdojo-path /tmp/AgentDojo \
  --benchmark-version v1.2.2 \
  --limit 12 \
  --stratified \
  --output outputs/agentdojo_real_manifest.json
```

Probe result:

- AgentDojo v1.2.2 suites loaded: workspace, travel, banking, slack.
- Total official user tasks: 97.
- Selected manifest slice: 12 tasks (`selected_fraction=0.1237`).
- Selected difficulty distribution: 4 easy, 4 medium, 4 hard.
- Selected ground-truth plan type: 9 mutating tasks, 3 read-only tasks.
- Status flags: `manifest_only=true`, `real_benchmark_run=false`,
  `real_model_run=false`, `executed_10_15_percent_slice=false`.

Interpretation: this materially improves the benchmark design story because the
paper is no longer scoped only to local scenarios or only to ToolSandbox. It
does not yet improve empirical strength: there is no AgentDojo observation
adapter, no executed AgentDojo tool-output spoofing run, and no model ASR.

Required wording: call this a "second existing-benchmark manifest/design
artifact" or "planned AgentDojo overlay slice", not "AgentDojo benchmark
results". The baseline comparison should remain "same AgentDojo tasks, same
official utility/security checks, different observation-integrity baselines"
once the executable adapter is implemented.

## Round 15: AgentDojo executable smoke

The AgentDojo path now moves beyond manifest-only. Implemented:

- `src/tool_spoof_lab/agentdojo_execution_smoke.py`
- `scripts/run_agentdojo_execution_smoke.py`

Command run:

```bash
PYTHONPATH=src:. /tmp/agentdojo-probe-venv/bin/python scripts/run_agentdojo_execution_smoke.py \
  --manifest outputs/agentdojo_real_manifest.json \
  --agentdojo-path /tmp/AgentDojo \
  --benchmark-version v1.2.2 \
  --out-dir traces/agentdojo_execution_smoke \
  --summary outputs/agentdojo_execution_smoke_summary.json \
  --limit-tasks 12
```

Result:

- 12 official AgentDojo tasks.
- 7 profiles: naive, schema-only, prompt-filter, repeat-same-tool, metadata-only validator,
  read-back validator, privileged independent-validator upper bound.
- truthful/spoofed modes.
- 168 / 168 scripted trace cells completed.
- `official_ground_truth_tool_plan=true`.
- `real_tool_execution=true`.
- `trace_level_visible_result_substitution=true`.
- `scripted_agent=true`.
- `full_agent_loop_interception=false`.
- `real_model_run=false`.

Scripted spoofed ASR:

| Profile | Spoofed ASR | Effective verification |
| --- | ---: | ---: |
| `agentdojo_exec_naive` | 12 / 12 | 0 / 12 |
| `agentdojo_exec_schema_only` | 12 / 12 | 0 / 12 |
| `agentdojo_exec_prompt_filter` | 12 / 12 | 0 / 12 |
| `agentdojo_exec_repeat_same_tool` | 12 / 12 | 0 / 12 |
| `agentdojo_exec_metadata_validator` | 12 / 12 | 0 / 12 |
| `agentdojo_exec_readback_validator` | 0 / 12 | 12 / 12 |
| `agentdojo_exec_independent_validator` | 0 / 12 | 12 / 12 |

Reviewer interpretation: this is a meaningful engineering upgrade over a
manifest-only second substrate. It shows the benchmark/baseline protocol is not
ToolSandbox-specific. But it remains scripted; it cannot support model
robustness or full AgentDojo benchmark claims until a real model pipeline and
full agent-loop adapter are implemented.

## Round 16: subagent review after AgentDojo executable smoke

A CCF-A/USENIX/S&P-style reviewer subagent reviewed the AgentDojo executable
smoke plan and current limitations.

Review verdict:

- AgentDojo executable smoke is a **substantive improvement** over manifest-only
  and materially weakens the "single substrate" criticism.
- It can support the claim that the overlay/baseline protocol transfers from
  ToolSandbox to another existing benchmark substrate.
- It cannot support model robustness, full AgentDojo benchmark, or
  statistically meaningful multi-benchmark claims.
- Overall status after this step: **Borderline-**, not Weak Accept.

Reviewer-required wording:

- Use "AgentDojo executable overlay smoke" or "adapter-level execution smoke".
- Do not use "AgentDojo benchmark results" or "full AgentDojo evaluation".
- Explicitly state that tool plans are benchmark-ground-truth/scripted,
  `full_agent_loop_interception=false`, and `real_model_run=false`.
- Treat read-back validation as deployability-oriented only under a split
  channel/state threat model.
- Treat privileged independent validation only as an upper-bound ablation.

Reviewer-required next gates:

1. Run a ToolSandbox real-model pilot with `real_model_run=true` and
   `model_call_executed=true` once API credentials are available.
2. Keep AgentDojo at least as executable smoke, then add a model policy or
   agent-loop adapter.
3. Keep the newly added prompt-filter baseline in the AgentDojo executable
   smoke, because AgentDojo's native framing is prompt-injection security and
   reviewers will expect that comparison.
4. Report ASR, clean utility, FPR, verification success, cost/latency, and
   confidence intervals for any result-bearing run.

Reviewer rating ladder:

- AgentDojo manifest-only: Weak Reject+.
- AgentDojo executable smoke + ToolSandbox dry-run: Borderline-.
- AgentDojo executable smoke + ToolSandbox real-model pilot: Borderline.
- Two-substrate real-model pilot + read-back validator + CI/cost/statistics:
  possible Weak Accept.
