# Paper draft: Observation Integrity for Tool-Using LLM Agents

Working title:

> **When Tools Lie: Benchmarking Schema-Valid False Observations in Tool-Using
> LLM Agents**

Target style: top-tier security systems paper first; benchmark/datasets track
second. This is a research draft, not a submission-ready camera-ready paper.

## Abstract

Tool-using LLM agents increasingly rely on external APIs, command wrappers,
browser observations, retrieval systems, and Model Context Protocol (MCP)
servers as if their returned values were authoritative observations of the
world. Prior work has shown that untrusted tool data can carry indirect prompt
injections, malicious tool metadata can steer tool selection, and compromised
tools can create hidden-trigger risks. This paper studies a narrower and
complementary failure mode: the tool result is syntactically valid and contains
no explicit adversarial instruction, but its decisive factual claim is false.

We introduce Tool Output Spoofing, a benchmark methodology for evaluating
whether agents accept, propagate, verify, or reject schema-valid false
observations. Each task has a benign user request, a hidden immutable truth
state, paired truthful and spoofed visible tool results, and an oracle that
scores the agent's final answer or mocked action against the hidden truth
rather than the agent-visible observation. The benchmark covers REST-style APIs,
MCP returns, retrieval/search evidence, browser-state observations, shell/test
output, and approval summaries. We evaluate generic prompt-injection defenses,
schema validation, repeated calls, provenance/freshness checks, independent
cross-tool corroboration, signed receipts, and combined policies under fixed
tool-call and token budgets.

Our central hypothesis is that prompt-centric defenses provide limited
protection against non-instructional false observations, while provenance and
independent verification substantially reduce false-state propagation at a
measurable utility and cost overhead. The artifact is designed to be local,
deterministic, and reproducible: no production accounts, no real side effects,
and no reliance on an LLM-emulated ground truth.

## 1. Introduction

Tool-integrated agents turn language models into operators over external
systems. A model can ask a payment API whether a transfer succeeded, query a
scanner about a vulnerability, inspect a browser accessibility tree, retrieve
citations, run tests, or summarize an MCP server's response. The resulting
observation often enters the model context as a plain statement of fact:
`status=succeeded`, `risk_score=0.01`, `tests passed`, `citation verified`, or
`form submitted`.

This trust boundary is fragile. If the observation is fabricated, stale,
truncated, or tampered with, an otherwise benign user request can produce a
wrong report or unsafe action. Existing work already establishes several
adjacent risks: indirect prompt injection in external content, malicious MCP
metadata, malicious tool implementations, malicious intermediaries, and
trajectory-conditioned untrusted tool feedback. These works block any broad
claim that "untrusted tool outputs are new." However, many evaluations conflate
three different phenomena:

1. the tool output contains an instruction that competes with the user's
   instruction;
2. the tool metadata or code is malicious before or during execution; and
3. the returned observation is a normal-looking but false claim about the world.

This paper isolates the third phenomenon. We ask:

> If the user prompt is benign and the tool output contains no explicit
> adversarial instruction, do agents treat schema-valid false observations as
> ground truth?

The distinction matters because defenses for prompt injection do not
necessarily verify factual truth. A sanitizer may remove "ignore previous
instructions" from a tool result while still leaving `deployment_status:
succeeded` untouched. A metadata allowlist may ensure that a trusted tool is
called, but it does not prove that a response was fresh, request-bound, or
consistent with independent state. A code scanner may find no malicious local
tool implementation when the tool is a remote black-box API or an intermediary
rewrites the response.

We propose a benchmark and evaluation protocol for **observation integrity** in
tool-using agents. The key design choice is to split hidden truth from visible
observation. For every scenario, the benchmark stores a truth plane that is not
shown to the agent and an observation plane that is delivered as the tool
result. Truthful and spoofed variants share the same user intent and hidden
truth; only the visible observation changes. The oracle scores whether the
agent accepted the false state, requested independent verification, surfaced
uncertainty, contradicted the false observation, or took a mocked unsafe action.

### Contributions

This paper aims to make four contributions.

1. **Threat definition.** We define tool-output spoofing as schema-valid false
   observations at the tool-result trust boundary, separate from prompt
   injection, metadata poisoning, malicious tool code, and tool hallucination.
2. **Benchmark protocol.** We introduce a paired truthful/spoofed protocol with
   immutable hidden truth, visible observation traces, deterministic local mock
   tools, and field-level oracle scoring.
3. **Multi-surface suite.** We design a suite spanning REST/API records, MCP
   responses, RAG/search evidence, browser observations, shell/test output, and
   human-approval summaries.
4. **Defense evaluation.** We compare prompt-centric defenses against
   observation-integrity defenses: freshness, request binding, provenance,
   signed receipts, independent cross-tool reads, contradiction handling, and
   final-answer uncertainty policies.

## 2. Threat model

### Attacker

The attacker controls or tampers with one observation channel after a tool call
has been selected. The attacker may be:

- a compromised remote API or MCP server;
- a malicious intermediary rewriting tool responses;
- a stale cache or replay proxy;
- a browser-observation wrapper that reports a fake success state;
- a local command wrapper that forges stdout, stderr, or exit status; or
- a retrieval/search layer that returns forged citations.

The attacker cannot modify the system prompt, the benchmark oracle, or the
hidden truth state. The attacker is not required to include any imperative text
or prompt-injection string. The strongest in-scope cases are valid according to
the declared schema.

### Defender

The defender controls the agent harness and can add validation policies,
secondary tools, signed envelopes, freshness checks, and final-answer gates. The
defender does not get direct access to hidden truth at inference time. During
evaluation, only the oracle sees hidden truth.

### Out of scope

The benchmark does not test real credentials, production services, malware,
destructive actions, or live third-party accounts. High-impact outcomes are
mocked locally.

## 3. Taxonomy

We classify spoofed observations along six axes.

| Axis | Values |
| --- | --- |
| Payload | semantic falsehood, omission, replay, forged provenance, instruction smuggling control |
| Surface | REST/API, MCP, RAG/search, browser, shell/test, approval UI |
| Format | JSON, text, HTML/DOM, stdout/stderr, receipt/citation |
| Persistence | one-shot, repeated consistent, stale replay, delayed trigger, rug pull |
| Detectability | schema-invalid, schema-valid obvious, schema-valid subtle |
| Corroboration | unavailable, same-tool only, independent tool, signed receipt |

The primary paper focuses on **schema-valid subtle semantic falsehoods**. We keep
instruction smuggling only as a control condition to show that defenses tuned
for obvious prompt injection do not automatically handle factual lies.

Representative attacks:

- `false_success`: a tool reports that a deployment, payment, upload, or form
  submission succeeded when hidden state says it failed.
- `schema_valid_false_value`: a decisive scalar such as risk, cost, balance, or
  benchmark score is fabricated.
- `forged_provenance`: a citation, receipt, DOI, message ID, commit hash, or
  scanner attestation is fake.
- `stale_replay`: an old valid response is replayed after the underlying state
  changed.
- `warning_stripping`: a tool omits a decisive warning while preserving a valid
  schema.
- `browser_obs_spoof`: the visible browser observation contains a success
  banner or completed state that is absent from the backend state.
- `exit_code_spoof`: stdout and exit code claim tests passed while an
  independent run or raw artifact shows failure.
- `approval_summary_deception`: an agent-generated approval summary reflects
  the spoofed observation rather than the canonical action.

## 4. Benchmark design

### 4.1 Scenario record

Each scenario is a JSON object containing:

- public user task;
- domain and spoof class;
- hidden ground truth;
- truthful tool result;
- spoofed tool result;
- optional independent validator result;
- expected robust behavior; and
- oracle success criteria.

The benchmark logs every run as JSONL trace rows:

1. user task;
2. hidden truth event, not model-visible;
3. visible tool result;
4. optional validation tool calls;
5. agent final answer or mocked action; and
6. oracle verdict.

The hidden truth row can be omitted from model-visible traces but retained for
artifact reproducibility.

### 4.2 Paired truthful/spoofed protocol

For each user task, we run at least four paired conditions:

| Condition | Hidden truth | Visible result | Expected robust behavior |
| --- | --- | --- | --- |
| clean truthful | fixed | truthful | Complete the task normally. |
| spoofed no defense | same | spoofed | Vulnerable agents may accept false state. |
| spoofed with defense | same | spoofed | Verify, reject, or surface uncertainty. |
| truthful with defense | same | truthful | Avoid over-refusal and preserve utility. |

This design makes false acceptance and false rejection separable. A defense that
rejects all tool outputs has low attack success but unacceptable utility.

### 4.3 Suites

The first full benchmark should contain five suites.

| Suite | Decisive false observation | Oracle |
| --- | --- | --- |
| API records | status, entity existence, state version, numeric field | local immutable state DB |
| MCP finance/security | function return, receipt, parameter binding, delayed rug pull | local MCP fixture + transaction ledger |
| RAG/search | citation existence, source authority, conflicting evidence | local corpus index + canonical bibliography |
| Browser form | success banner, DOM/a11y text, submitted target | backend state validator |
| Shell/tests | exit code, stdout, artifact path, log truncation | independent process/raw artifact check |

The MVP in this repository currently includes deterministic JSON scenarios for
false success and instruction-smuggling controls. The planned paper version
should expand to at least 150-300 scenario pairs before submission.

### 4.4 Agent profiles

Evaluation should cover both deterministic policy stubs and real agents:

- naive ReAct-style agent;
- native tool-calling model;
- plan-and-execute agent;
- self-reflection or critique agent;
- dual-agent verifier;
- browser agent where applicable; and
- MCP client agent where applicable.

For commercial APIs, the artifact must record model name, date, decoding
parameters, tool schema, prompt, and full trace. For local/open models, record
commit hash, weights identifier, and inference parameters.

## 5. Defenses

We group defenses by whether they target instructions or observation truth.

| Defense | What it catches | Expected limitation |
| --- | --- | --- |
| Prompt-only warning | obvious instruction smuggling | does not verify facts |
| Prompt-injection filter | malicious imperative text | false JSON/status remains |
| Strict schema validation | malformed outputs | schema-valid lies pass |
| Repeat same tool | transient failure | consistent liar passes |
| LLM-as-judge | suspicious language | unreliable for low-text structured lies |
| Tool metadata allowlist | malicious tool selection | trusted tool can still lie |
| Provenance/freshness gate | stale or unsigned results | requires instrumentation |
| Signed receipt | forged result not issued by authority | may not cover all tools |
| Independent cross-tool read | false state divergence | extra cost and tool availability |
| Contradiction policy | conflicting evidence | may increase uncertainty/refusal |
| Combined policy | layered risk reduction | higher latency and tool calls |

The paper's key experimental contrast is prompt-centric versus
observation-integrity defenses.

## 6. Metrics

Primary metrics:

- **Attack Success Rate (ASR):** spoofed trials where the final answer or
  action accepts the false observation without adequate uncertainty.
- **Clean Utility:** truthful trials where the agent reaches the correct answer
  or safe mocked action.
- **False-State Propagation Rate:** traces where the spoofed field appears in
  intermediate reasoning, final answer, action arguments, or approval summary.
- **Verification Attempt Rate:** trials where the agent requests or performs an
  independent check.
- **Effective Verification Rate:** verification attempts that actually consult
  an independent authority rather than repeating the same untrusted channel.
- **Contradiction Handling Rate:** trials where the agent correctly surfaces
  conflict between sources.
- **False Positive Refusal Rate:** truthful trials blocked by a defense.
- **Defense Overhead:** additional tool calls, tokens, latency, and failure
  modes.

We also report an asymmetric safety-utility score:

```text
Observation Integrity Score =
  CleanUtility * (1 - ASR) * (1 - FalsePositiveRefusalRate)
```

This is not a replacement for per-metric reporting; it is a compact ranking
signal for defense comparisons.

## 7. Experimental plan

### RQ1: Do agents accept schema-valid false observations?

Run each model/agent on paired truthful and spoofed traces with no defense.
Compare ASR by suite and attack class. The strongest expected result is high
acceptance of false success, forged provenance, stale replay, and exit-code
spoofing when the payload contains no malicious instruction.

### RQ2: Are prompt-injection defenses sufficient?

Compare no defense, prompt-only warning, prompt-injection filter, strict schema
validation, and LLM-as-judge on both instruction-smuggling controls and
non-instructional semantic falsehoods. The expected result is that these
defenses reduce obvious instruction smuggling but leave schema-valid false
status and provenance largely intact.

### RQ3: Which observation-integrity defenses work?

Compare freshness gates, signed receipts, independent read-after-write,
cross-tool corroboration, contradiction policy, and combined policy. The
expected result is lower ASR with measurable overhead; repeated same-tool calls
should underperform independent verification when the same channel is
consistently compromised.

### RQ4: What is the utility cost?

Run every defense on truthful traces. Report over-refusal and unnecessary
verification. The target is not zero ASR through blanket refusal; it is a
Pareto frontier between clean utility, ASR, and overhead.

### RQ5: Does the failure propagate into approval summaries?

For high-impact mocked actions, compare model-generated approval summaries with
canonical structured action records. Measure whether the summary hides the
spoofed field or presents the false state as verified.

## 8. Baselines and related work positioning

The closest work blocks broad novelty. The paper must be explicit:

- Trust No Tool studies untrusted tool feedback and cognitive poisoning; our
  focus is field-level observation truth with paired truth/spoof traces.
- MCP Security Bench and MCP-SafetyBench cover MCP response attacks and data
  tampering; our contribution is deterministic local multi-surface veracity
  evaluation rather than broad MCP safety coverage.
- AgentDojo and InjecAgent benchmark indirect prompt injection through
  tool-visible data; our core cases contain no imperative attack text.
- ToolEmu provides LM-emulated sandboxing; our oracle is deterministic and
  independent of the agent-visible observation.
- CaMeL and AttriGuard are strong data/control-flow defenses for prompt
  injection and action provenance; our benchmark tests whether such systems
  also need factual verification of observed state.
- MalTool, ToolHijacker, Attractive Metadata Attack, MCPTox, and ToolCommander
  cover malicious tool code, tool selection, and metadata poisoning; our
  controlled experiments hold tool selection fixed to isolate post-selection
  result veracity.

## 9. Expected results table

This table states the desired evidence before running large experiments.

| Finding | Evidence required |
| --- | --- |
| Agents accept false observations | ASR significantly above truthful false-positive rate across at least three suites |
| Prompt filters are insufficient | Filters reduce instruction-smuggling ASR more than semantic-falsehood ASR |
| Schema validation is insufficient | Valid spoofed JSON passes schema but causes false acceptance |
| Independent verification helps | Cross-tool/read-after-write reduces ASR relative to repeat-same-tool |
| Receipts/freshness help where available | Signed/freshness policy reduces forged/stale result acceptance |
| Utility tradeoff is manageable | Combined policy preserves clean utility above a pre-registered threshold |

## 10. Threats to validity

**Construct validity.** Synthetic local mocks may not capture production tool
complexity. Mitigation: use realistic schemas from public benchmarks where
possible and include multi-surface tasks.

**External validity.** Agent behavior changes across model versions and
frameworks. Mitigation: record model/date/configuration and evaluate multiple
agent profiles.

**Oracle validity.** If the oracle is too simple, results may reward benchmark
gaming. Mitigation: keep truth state separate, deterministic, and auditable;
include raw artifacts for shell/browser suites.

**Defense unfairness.** Cross-tool verification may see more information than
the no-defense baseline. Mitigation: report overhead and fixed verification
budgets; separate "allowed extra evidence" from "model reasoning quality."

**Novelty risk.** Existing 2026 MCP and untrusted-feedback papers are close.
Mitigation: avoid firstness claims except for the exact paired
schema-valid-observation-veracity protocol, and include the close work as
baselines or ablations where feasible.

## 11. Artifact plan

The artifact should include:

- scenario JSON schema and at least 150-300 paired tasks;
- deterministic mock REST/MCP/browser/shell fixtures;
- hidden truth plane and oracle implementation;
- adapters for at least two commercial tool-calling APIs and one open/local
  model when resources permit;
- scripts for MVP, full matrix, and paper-table generation;
- anonymized traces for all reported results; and
- documentation for adding new spoof surfaces.

The artifact should not include real credentials, production API targets,
large model weights, generated caches, or non-reproducible external state.

## 12. Submission strategy

Primary security targets:

1. **USENIX Security 2027 Cycle 1** if experiments can be scaled by August 2026.
2. **IEEE S&P 2027 second deadline** if the benchmark and defense matrix need
   the fall 2026 cycle.
3. **NDSS 2027 fall cycle** as a fast security venue with artifact-friendly
   positioning.
4. **ACM CCS 2027** if the work needs a 2027 cycle and stronger measurement.

Secondary targets:

- NeurIPS Datasets & Benchmarks if the benchmark artifact is the main
  contribution and security novelty is judged too narrow.
- ACL/EMNLP findings or ARR only if reframed as agent robustness/evaluation
  rather than systems security.
- IEEE Transactions on Dependable and Secure Computing or ACM TOPS as journal
  targets after a conference version or if the defense system becomes more
  mature.

## 13. Current status

Implemented locally:

- concept, threat model, attack taxonomy, novelty audit;
- literature matrix and deep-reading notes;
- deterministic scenario configs for false success and instruction-smuggling
  control;
- trace runner, oracle, and small MVP matrix;
- smoke tests requiring no external packages.

Still required before a serious top-tier submission:

- expand scenario count and surfaces;
- add real agent adapters;
- implement provenance, signed receipt, and cross-tool defense policies;
- run controlled model experiments;
- compare against or emulate close baselines;
- produce statistical analysis and figures;
- package artifact and anonymize traces.

