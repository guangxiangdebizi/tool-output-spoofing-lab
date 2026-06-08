# Benchmark overlay strategy

## Core correction

The paper should not rely on a fully self-created toy benchmark as the main
evidence. The stronger and more publishable design is:

> Use existing high-value agent/tool-use benchmarks as the task substrate, then
> add an observation-spoofing overlay and compare defenses on the same tasks.

The repository's current 15-scenario local suite remains useful, but only as a
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

Config: `configs/benchmark_overlays/high_value_benchmark_overlay.json`.

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

The key comparison is not "our benchmark vs their benchmark"; it is:

```text
same existing benchmark tasks
same spoofed-observation overlay
different defenses / baselines
```

## First paper-grade pilot

The next real pilot should use existing benchmark substrates, not additional
hand-written toy tasks.

Recommended order:

1. **ToolSandbox overlay smoke**
   - Easiest deterministic truth state.
   - Milestone DAG already behaves like an oracle.
   - Goal: prove observation spoofing can be inserted without breaking clean
     task evaluation.
   - Current repo status: adapter-contract smoke scaffold implemented in
     `src/tool_spoof_lab/toolsandbox_overlay.py`,
     `scripts/run_toolsandbox_overlay_smoke.py`, and
     `configs/benchmark_overlays/toolsandbox_overlay_smoke.json`. This is not
     yet the real ToolSandbox package integration.
2. **AgentDojo overlay smoke**
   - Strongest security benchmark positioning.
   - Goal: show non-instructional false observations are different from
     indirect prompt injection.
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
