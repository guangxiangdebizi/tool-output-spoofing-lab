# Novelty Audit

Date: 2026-06-08 Asia/Shanghai.

## Current decision

**Weak Go, with a narrowed claim.**

This direction is not empty. There is already substantial work on:

- indirect prompt injection against tool-using agents;
- malicious MCP/tool metadata;
- malicious tool code and plugin supply-chain risk;
- agent security benchmarks;
- RAG/retrieval poisoning;
- tool-use risk evaluation.

The strongest near-direct paper found so far is:

- **Trust No Tool: Evaluating and Defending LLM Agents under Untrusted Tool
  Feedback** (`arXiv:2605.17453`, 2026), local PDF:
  `papers/topsec-nlp/2026_trust_no_tool.pdf`.

That paper directly weakens any claim that "untrusted tool feedback" is
unstudied. It frames **cognitive poisoning**: a malicious tool behaves
plausibly during exploration, accumulates trust through benign-looking feedback,
and becomes harmful when hidden trigger conditions align with the final action.

Subsequent deep reads of Trust No Tool, MCP Security Bench, MCP-SafetyBench,
AgentDojo, InjecAgent, Greshake et al., and PoisonedRAG confirm the same
boundary:

- broad agent/tool prompt-injection novelty is blocked;
- broad untrusted-tool-feedback novelty is blocked;
- broad RAG/fabricated-evidence novelty is blocked;
- the remaining gap is **observation veracity as the controlled variable**,
  especially for non-instructional, schema-valid, low-free-text tool outputs.

So the broad claim "nobody has studied malicious tool outputs" is blocked.

## Narrow claim that still looks viable

The more defensible project is:

> A deterministic, local, multi-surface benchmark for **schema-valid but
> semantically fabricated tool observations**, with paired truthful/spoofed
> traces, an immutable truth oracle, and defense baselines focused on
> provenance, receipts, freshness, and independent corroboration.

This is narrower than existing prompt-injection benchmarks and distinct from
malicious-tool-code generation.

One-sentence paper positioning:

> Existing work shows that untrusted tool data can inject instructions,
> malicious tools/MCP servers can compromise agents, and untrusted tool feedback
> can create trajectory-conditioned risk. We isolate a complementary failure
> mode: agents accepting **schema-valid false observations** as ground truth
> when the output contains no explicit instruction.

## Most important close work

| Priority | Work | Why it matters | What it blocks | Remaining gap |
| --- | --- | --- | --- | --- |
| P0 | Trust No Tool, 2026 | Directly studies untrusted tool feedback and hidden-trigger compromise. | Blocks broad "first untrusted tool feedback benchmark" claim. | Need compare exact coverage: semantic false status/provenance/receipt values, field-level oracle, local reproducible multi-format suite. |
| P0 | MCP Security Bench, ICLR 2026 | Real MCP attack benchmark, including response handling, false-error escalation, user-impersonating responses, tool transfer. | Blocks broad "first MCP response attack benchmark" claim. | Our angle can avoid real-account dependencies and isolate schema-valid false observations with truth/oracle split. |
| P0 | MCP-SafetyBench / MCPSafety | Real MCP servers, server/host/user-layer attacks, function return injection, data tampering, tool poisoning. | Blocks broad "first malicious MCP/tool server benchmark" claim. | Existing focus is broader MCP attack taxonomy; false-observation veracity can be made first-class. |
| P0 | AgentDojo, 2024 | Mature dynamic benchmark for prompt injection attacks and defenses in LLM agents. | Blocks "first agent prompt-injection security benchmark" claim. | Default attacks emphasize malicious instructions in environment/tool data, not non-instructional factual lies. |
| P0 | InjecAgent, 2024 | Dedicated indirect prompt injection benchmark for tool-integrated agents. | Blocks "first IPI benchmark for tool agents" claim. | Our scenarios should include no-instruction spoofed facts and status values. |
| P0 | ToolEmu, 2023 | LM-emulated sandbox for LM agent risk evaluation. | Blocks "first tool-risk sandbox/evaluator" claim. | Need deterministic mock tools and independent truth oracle instead of LM-emulated truth. |
| P0 | MalTool, 2026 | Systematic malicious tool-code implementation study. | Blocks "malicious tool implementation is unexplored" claim. | We can abstract away code generation and focus on returned observation semantics. |
| P0 | Greshake et al., 2023 | Foundational indirect prompt injection against LLM-integrated apps. | Blocks "external content controlling LLM apps is new" claim. | Our target can be false structured facts, not instruction smuggling. |
| P1 | MCPTox, 2025 | Tool poisoning through MCP metadata. | Blocks metadata-poisoning novelty. | Post-selection result veracity remains separable. |
| P1 | PoisonedRAG / BIPIA / SafeRAG | Retrieval/RAG poisoning and indirect prompt injection. | Blocks RAG poisoning novelty. | Non-RAG APIs, status fields, receipts, shell/browser observations remain broader. |

## Deep-read confirmed differentiators

From `secondary-research/deep-dive/deep-read-untrusted-feedback.md`:

- Trust No Tool is direct, but its core variable is trajectory-conditioned
  final-action risk under hidden triggers, not a field-level truth/visible
  observation split.
- MSB has response attacks, but response attacks often conflate false claims
  with instruction-bearing payloads such as false errors plus directions.
- MCP-SafetyBench covers function-return injection/data tampering, but the
  benchmark is broad MCP safety rather than a local multi-surface veracity
  benchmark.

From `secondary-research/deep-dive/deep-read-ipi-rag.md`:

- AgentDojo and InjecAgent force us to treat prompt-injection-through-tools as
  already well benchmarked.
- Greshake et al. block any claim that indirect external content control is
  new.
- PoisonedRAG blocks broad "semantic false evidence" claims for RAG/search, but
  not structured non-RAG tool observations such as receipts, exit codes,
  scanner verdicts, and browser state.

## Claims to avoid

Do not claim:

- "First work on LLM agent security."
- "First prompt injection attack via tool output."
- "First malicious MCP server/tool benchmark."
- "First malicious tool/plugin attack."
- "First study of untrusted tool feedback."
- "First retrieval poisoning / fabricated evidence attack."

## Claims that may survive

Potentially viable after deeper reading:

1. **Observation-veracity benchmark**: first benchmark that treats the
   truthfulness of tool observations as an independent experimental variable
   across REST/MCP/RAG/browser/shell surfaces.
2. **Paired truth/spoof protocol**: every task has matched truthful and spoofed
   traces, with identical user intent and an immutable hidden truth plane.
3. **Schema-valid semantic lies**: focus on outputs that pass schema validation
   and contain no explicit malicious instruction, but are semantically false.
4. **Receipt/provenance defenses**: compare prompt-injection filters against
   verification controls: signed result envelopes, independent read-after-write,
   cross-tool corroboration, freshness, and trust hierarchy.
5. **Human approval deception**: test whether agent-generated summaries mislead
   user approval when prior tool results are false.

## Required experiment invariants

To stay novel, every core scenario should satisfy:

1. The user task is benign.
2. The tool schema and tool name are unchanged.
3. The spoofed output is valid according to the schema.
4. At least one P0 setting contains no imperative/instructional attack text.
5. The hidden truth state and agent-visible observation are stored separately.
6. The oracle scores from hidden truth, not from model-visible output.
7. The run records whether the agent propagated, verified, contradicted, or
   acted on the false state.

## Go / No-Go rule after full deep-read

Go if the deep read confirms no existing benchmark simultaneously provides:

- local deterministic tool servers;
- paired truthful/spoofed observations;
- independent truth oracle;
- schema-valid non-instructional semantic falsehoods;
- multi-surface coverage: MCP/REST, RAG/search, browser observation,
  shell/test output;
- defense comparison between prompt-centric and provenance/corroboration
  controls.

No-Go if Trust No Tool, MCP Security Bench, or MCP-SafetyBench already provide
that exact combination.

## Immediate next experiment shape

Build the MVP around five small local suites:

1. `api_records`: fabricated entity, stale state, schema-valid false value.
2. `mcp_finance`: parameter poisoning, return injection, rug pull.
3. `rag_search`: retrieval poisoning, conflicting sources, forged citation.
4. `browser_form`: fake success banner / DOM-state mismatch.
5. `shell_tests`: exit-code/stdout spoofing against a tiny repo.

The first paper-ready measurement should compare:

- no defense;
- prompt-injection filter;
- strict schema validation;
- repeat same tool;
- independent cross-check;
- signed/provenance result envelope;
- combined policy.
