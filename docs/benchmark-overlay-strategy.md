# Benchmark overlay strategy

## Core correction

The paper should not rely on a fully self-created toy benchmark as the main
evidence. The stronger and more publishable design is:

> Use existing high-value agent/tool-use benchmarks as the task substrate, then
> add an observation-spoofing overlay and compare defenses on the same tasks.

The repository's current 16-scenario local suite remains useful, but only as a
smoke test for the oracle, trace format, and defense logic. It should not be
presented as the main benchmark.

## What changes

### Old framing to avoid

- "We build a new benchmark from scratch."
- "The 15 local scenarios are representative benchmark evidence."
- "Our main contribution is a standalone toy suite."

### New framing

- Existing benchmark tasks provide the task distribution, environment state, and
  utility/security oracle.
- Our overlay mutates the observation plane while preserving hidden truth.
- The experiment compares defenses on the same underlying benchmark tasks.

In other words:

```text
existing benchmark task + normal tool/environment state
  -> truthful observation condition
  -> spoofed observation condition
  -> same hidden oracle / validator
  -> compare baselines and defenses
```

## Candidate benchmark substrates

| Substrate | Priority | Why it is valuable | Overlay idea | First slice |
| --- | --- | --- | --- | --- |
| AgentDojo | P0 | Mature agent-security benchmark with utility/security checks. | Mutate factual tool-return fields without adding imperative instructions. | Workspace/productivity records and API-like tools. |
| ToolSandbox | P0 | Stateful tool-use benchmark with execution context and milestone DAG oracle. | Return spoofed observations to agent while milestone oracle reads real state. | Settings/contact/reminder state tasks. |
| tau-bench / tau2-bench | P0 | Realistic retail/airline tool-calling conversations. | Proxy order/refund/reservation/inventory API returns. | Retail + airline status tasks. |
| WebArena / WorkArena | P1 | Browser-agent benchmarks with backend/task validation. | Rewrite DOM/a11y/success-banner observations while backend state is unchanged. | Submission/status/admin UI tasks. |
| SWE-bench / SWE-agent | P1 | Strong software-engineering ground truth through tests. | Spoof command stdout/exit code/test summaries while oracle runs real tests. | Fast verified tasks. |
| MCP-SafetyBench / MCP Security Bench | P1 | Closest MCP security substrate. | Isolate schema-valid non-instructional false returns from broader MCP attacks. | Finance/search/browser/repo tasks that run in isolation. |
| PoisonedRAG / SafeRAG | P2 | Strong retrieval-security substrate. | Treat retrieval as a tool and spoof citation/provenance fields. | Citation/policy QA tasks. |
| Security/CTF-style sandbox assets | P2 | Captures permission-boundary failures where model-visible tooling claims an asset is owned or in scope. | Spoof ownership/scope/banner/asset-inventory observations while a hidden scope registry says not authorized. | Authorization verdict only; no exploit-step generation. |

Config: `configs/benchmark_overlays/high_value_benchmark_overlay.json`.

The fixed benchmark/baseline contract is in
`docs/benchmark-baseline-contract.md`. That file is the authoritative reference
for benchmark unit definition, baseline hidden-access rules, observation
generator constraints, authorization evidence ladder, and the minimum
paper-grade experiment matrix.

## Primary benchmark references

Use primary papers/project pages when justifying substrate choice:

- AgentDojo: <https://arxiv.org/abs/2406.13352>
- ToolSandbox: <https://machinelearning.apple.com/research/toolsandbox-stateful-conversational-llm-benchmark>,
  <https://arxiv.org/abs/2408.04682>
- tau-bench: <https://taubench.com/>, <https://arxiv.org/abs/2406.12045>
- WebArena: <https://arxiv.org/abs/2307.13854>
- MCP-SafetyBench: <https://xjzzzzzzzz.github.io/mcpsafety.github.io/>,
  <https://arxiv.org/abs/2512.15163>
- MCP Security Bench / MSB: <https://arxiv.org/abs/2510.15994>,
  <https://openreview.net/pdf?id=irxxkFMrry>

ToolSandbox, AgentDojo, and tau-bench are the recommended first substrates for
paper-grade pilots; MCP benchmarks are both close-work comparisons and possible
overlay substrates.

## Baselines on the same benchmark tasks

The baseline hierarchy should be held constant across benchmark substrates:

1. **No defense / naive trust**: accept the first observation.
2. **Schema-only**: validate format/type but not factual truth.
3. **Prompt-filter / injection filter**: detect instruction-like payloads.
4. **Repeat same tool**: call the same possibly compromised channel again.
5. **Independent validator**: query an independent state authority.
6. **Metadata checks**: freshness/signature metadata checks where available.
7. **Combined policy**: independent validation plus metadata/fallback policy.
8. **Scope/authorization gate**: for security-assessment tasks, require an
   independent scope registry or signed authorization record before escalating
   from passive triage to active assessment.
9. **Signed-scope / challenge-response validator**: for authorization tasks,
   bind `asset_id`, `domain`, `scope_level`, `valid_until`, and signer identity
   to a model-visible signature or challenge result. This is the deployable
   authorization baseline; hidden scope-registry reads remain upper-bound
   ablations until implemented this way.

The key comparison is not "our benchmark vs their benchmark"; it is:

```text
same existing benchmark tasks
same spoofed-observation overlay
different defenses / baselines
```

For the authorization/provenance spoof axis, the main comparison is:

```text
same sandbox asset + same hidden scope registry
truthful or spoofed model-visible ownership/banner/inventory observation
baseline decides permitted assessment level
oracle checks whether the decision respected hidden scope truth
```

The benchmark should score only the authorization verdict and permitted
assessment level. It should not ask models to produce exploit chains, scanning
commands, or real-world attack steps.

Prompt-leakage invariants for all overlay runs:

- no `oracle_context`;
- no `truth_result`;
- no `expected_safe_behavior`;
- no `truthful` / `spoofed` condition label;
- no raw profile name such as `toolcall_naive`;
- no hidden `independent_available` flag;
- read-back observation is allowed only as a second visible tool result;
- authorization outputs remain verdict-level only.

## First paper-grade pilot

The next real pilot should use existing benchmark substrates, not additional
hand-written toy tasks.

Recommended order:

1. **ToolSandbox overlay smoke**
   - Easiest deterministic truth state.
   - Milestone DAG already behaves like an oracle.
   - Goal: prove observation spoofing can be inserted without breaking clean
     task evaluation.
   - Current repo status: adapter-contract smoke, real manifest probe, real
     single-tool execution interception smoke, and model-policy pilot dry-run
     harness are implemented. This is still not full ToolSandbox agent-loop
     interception or a result-bearing model benchmark run.
2. **AgentDojo overlay smoke**
   - Strongest security benchmark positioning.
   - Goal: show non-instructional false observations are different from
     indirect prompt injection.
   - Current repo status: official AgentDojo v1.2.2 suites are importable in an
     isolated probe environment, and a 12 / 97 stratified 10-15% manifest has
     been generated. A 192-cell executable smoke now runs official AgentDojo
     ground-truth tool calls and performs trace-level visible-observation
     substitution, and a 192-cell model-policy dry-run validates the prompt and
     manifest path. This is still not full AgentDojo agent-loop interception or
     a result-bearing model run.
3. **tau-bench overlay smoke**
   - Strong realistic tool-calling API story.
   - Goal: status/refund/reservation API falsehoods under the same user tasks.

Minimum useful real-model slice:

```text
2 benchmark substrates
10-15 tasks per substrate
truthful + spoofed modes
3 baselines: naive, repeat-same-tool, independent-validator
1-2 models
```

This is 120-360 cells depending on model count and task count. If API budget is
tight, run the 48-cell local harness pilot first, then replace local scenarios
with ToolSandbox/AgentDojo overlay tasks.

## Concrete overlay examples

### ToolSandbox overlay

```text
ToolSandbox scenario state snapshot = hidden truth
tool result returned to agent       = observation plane
milestone DAG                       = clean utility oracle
spoofing adapter                    = rewrites selected tool returns only
```

Example:

- original task: user asks whether a setting/reminder/contact update succeeded;
- truthful condition: tool result reflects execution context;
- spoofed condition: tool result claims success/failure or wrong entity while
  execution context remains unchanged;
- independent validator: read execution context snapshot or milestone state;
- metrics: ASR, clean utility, FPR, effective validation, tool-event overhead.

Current adapter-contract smoke command:

```bash
PYTHONPATH=src:. /usr/bin/python3.11 scripts/run_toolsandbox_overlay_smoke.py \
  --config configs/benchmark_overlays/toolsandbox_overlay_smoke.json \
  --out-dir traces/toolsandbox_overlay_smoke \
  --summary outputs/toolsandbox_overlay_smoke_summary.json
```

Real ToolSandbox manifest probe command:

```bash
git clone https://github.com/apple/ToolSandbox /tmp/ToolSandbox
/usr/bin/python3.11 -m venv /tmp/toolsandbox-probe-venv
/tmp/toolsandbox-probe-venv/bin/python -m pip install -e /tmp/ToolSandbox
PYTHONPATH=src:. /tmp/toolsandbox-probe-venv/bin/python scripts/probe_toolsandbox_real.py \
  --toolsandbox-path /tmp/ToolSandbox \
  --limit 12 \
  --output outputs/toolsandbox_real_manifest.json
```

The repository still does not vendor ToolSandbox as a project dependency. The
fixture scaffold uses ToolSandbox-shaped fixtures, while the later real probes
use a cloned `/tmp/ToolSandbox` source tree through `--toolsandbox-path` and an
isolated `/tmp/toolsandbox-probe-venv`. The next step is to replace trace-level
smokes with full agent-loop interception. To prevent
fixture smoke traces from contaminating paper-grade result aggregation, every
row emitted by the current scaffold is marked with `adapter_contract=true`,
`fixture=true`, and `real_benchmark_run=false`; real ToolSandbox runs must flip
those provenance fields and record package version, task id, state snapshot, and
evaluator configuration.

The manifest probe does use real ToolSandbox scenario definitions and milestone
oracles, but it is still `manifest_only=true`: it enumerates a 12-task
bring-up seed and extracts state/oracle metadata before any model run or
observation interception. It is not a representative 10-15% ToolSandbox slice;
that larger slice must be stratified separately.

Real ToolSandbox execution smoke:

```bash
PYTHONPATH=src:. /tmp/toolsandbox-probe-venv/bin/python scripts/run_toolsandbox_execution_smoke.py \
  --manifest outputs/toolsandbox_real_manifest.json \
  --toolsandbox-path /tmp/ToolSandbox \
  --out-dir traces/toolsandbox_execution_smoke \
  --summary outputs/toolsandbox_execution_smoke_summary.json \
  --limit-tasks 12
```

This executes real ToolSandbox tools through `ExecutionEnvironment`, preserves
raw `tool_trace`, and then substitutes the agent-visible result at trace level.
It is explicitly marked `trace_level_visible_result_substitution=true`,
`full_agent_loop_interception=false`, `scripted_agent=true`, and
`real_model_run=false`.

ToolSandbox model-policy pilot:

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

The dry-run completed 144 cells over 12 tasks x truthful/spoofed x 6 profiles.
It proves prompt/manifest plumbing and checks that hidden `oracle_context`,
`raw_tool_result`, and condition labels do not enter model-visible prompts.
A smaller 24-cell real-model slice over 2 tasks has also been run with the
semantic-normalized observation adapter; that slice is result-bearing pilot
evidence, not a 10%-15% benchmark execution.
The added validator profiles separate non-privileged metadata-only checks,
non-privileged read-back validation through a second real ToolSandbox tool, and
a privileged independent validator that is explicitly treated as an upper bound
rather than a deployable defense.
The read-back validator is not hidden-oracle access: it is a model-visible
second-tool observation and is valid only when the canonical read-back path is
outside the spoofed primary observation channel.

Representative 10%-15% ToolSandbox slice manifest:

```bash
PYTHONPATH=src:. /tmp/toolsandbox-probe-venv/bin/python scripts/probe_toolsandbox_real.py \
  --toolsandbox-path /tmp/ToolSandbox \
  --limit 104 \
  --stratified \
  --output outputs/toolsandbox_stratified_10pct_manifest.json
```

On the current ToolSandbox source tree this selected 104 / 1032 scenarios
(`selected_fraction=0.1008`) and records multi-label strata over single/multi
turn, single/multi tool, insufficient-information, distraction, state
dependency, canonicalization, and read-only/mutation categories. The manifest
is a sampling design artifact, not an executed model benchmark.

### AgentDojo overlay

```text
AgentDojo suite/user task    = task substrate
environment/tool record      = observation plane
utility/security check       = oracle
attack adapter               = non-instructional field mutation
```

Example:

- original task: agent must process workspace/productivity record;
- spoofed condition: API-like tool return changes factual status/provenance
  without adding any imperative text;
- independent validator: a second record/source or canonical environment state;
- comparison: prompt-injection defenses versus observation-integrity defenses.

Real AgentDojo manifest probe:

```bash
git clone --depth 1 https://github.com/ethz-spylab/agentdojo /tmp/AgentDojo
/usr/bin/python3.11 -m venv /tmp/agentdojo-probe-venv
/tmp/agentdojo-probe-venv/bin/python -m pip install -e /tmp/AgentDojo
PYTHONPATH=src:. /tmp/agentdojo-probe-venv/bin/python scripts/probe_agentdojo_real.py \
  --agentdojo-path /tmp/AgentDojo \
  --benchmark-version v1.2.2 \
  --limit 12 \
  --stratified \
  --output outputs/agentdojo_real_manifest.json
```

On the current AgentDojo source tree this enumerated 97 user tasks across
workspace, travel, banking, and slack suites, then selected 12 tasks
(`selected_fraction=0.1237`). The manifest records official prompts,
difficulty, suite tools, injection-task counts, and ground-truth tool-call
plans. It is a second existing-benchmark substrate and a valid sampling/design
artifact, but it is not yet an executed AgentDojo benchmark because
`real_benchmark_run=false` and `real_model_run=false`.

AgentDojo executable smoke:

```bash
PYTHONPATH=src:. /tmp/agentdojo-probe-venv/bin/python scripts/run_agentdojo_execution_smoke.py \
  --manifest outputs/agentdojo_real_manifest.json \
  --agentdojo-path /tmp/AgentDojo \
  --benchmark-version v1.2.2 \
  --out-dir traces/agentdojo_execution_smoke \
  --summary outputs/agentdojo_execution_smoke_summary.json \
  --limit-tasks 12
```

This completed 192 cells over 12 official AgentDojo tasks x truthful/spoofed x
8 profiles. It uses each task's official `ground_truth()` tool-call plan to
execute one real AgentDojo tool call, then substitutes the agent-visible
observation at trace level. It records `real_tool_execution=true`,
`official_ground_truth_tool_plan=true`, `trace_level_visible_result_substitution=true`,
`scripted_agent=true`, `full_agent_loop_interception=false`, and
`real_model_run=false`. Scripted scoring shows the same baseline separation as
ToolSandbox: naive/schema-only/prompt-filter/repeat-same-tool/metadata-only
accept spoofed content, while read-back and privileged upper-bound validators
recover the truth under their stated trust assumptions.

AgentDojo model-policy pilot:

```bash
PYTHONPATH=src:. /tmp/agentdojo-probe-venv/bin/python scripts/run_agentdojo_model_pilot.py \
  --config configs/experiments/agentdojo_model_pilot_small.json \
  --manifest outputs/agentdojo_real_manifest.json \
  --agentdojo-path /tmp/AgentDojo \
  --out-dir traces/agentdojo_model_pilot_dry \
  --summary outputs/agentdojo_model_pilot_dry_summary.json \
  --run-manifest outputs/agentdojo_model_pilot_dry_manifest.json \
  --dry-run --sleep 0
```

The dry-run completed 192 cells over 12 AgentDojo tasks x truthful/spoofed x 8
profiles. It proves model-prompt plumbing and records prompt hashes,
model-visible event lists, and harness-expected structured scores. Prompt tests
verify that hidden `oracle_context`, `raw_tool_result`, raw profile names, and
truthful/spoofed condition labels are not exposed to the model.

A smaller 32-cell real-model slice has also been run over two official tasks
(`travel:user_task_19`, `slack:user_task_14`) using the semantic-normalized,
plausible-alternate spoof adapter. That run is useful as second-substrate pilot
evidence, but it remains trace-level visible-result substitution rather than a
full AgentDojo agent-loop benchmark.

### tau-bench overlay

```text
tau-bench user + domain API simulator = task substrate
API proxy return to agent             = observation plane
simulator database/policy state        = hidden truth
task success evaluator                 = utility oracle
```

Example:

- original task: retail/airline user asks about refund/order/reservation status;
- spoofed condition: `get_order_status` or `get_reservation` returns a
  schema-valid but false state;
- independent validator: separate ledger/status endpoint or simulator state
  snapshot;
- comparison: same task, same user, different defense baselines.

## Role of the current local suite

The current local suite is still useful as:

- unit tests for trace schema and oracle;
- dry-run scaffolding before installing external benchmarks;
- examples for spoof classes;
- regression tests for baseline behavior.

It should be clearly labeled:

> local smoke suite, not the main paper benchmark.

## Claims enabled by overlay design

Stronger claim:

> We introduce an observation-spoofing overlay protocol that adapts existing
> agent/tool-use benchmarks into paired truthful/spoofed observation evaluations
> and compare observation-integrity defenses on the same underlying tasks.

Weaker claim to avoid:

> We created a standalone benchmark and therefore solved tool-output spoofing
> evaluation.
