# Experiment Plan

## Research questions

RQ1. How often do agents accept semantically fabricated tool observations when
the user prompt is benign?

RQ2. Which spoof classes are most likely to propagate into final answers or
mocked actions?

RQ3. Do generic prompt-injection defenses help when the attack is not an
explicit instruction but a false structured fact?

RQ4. Which low-cost defenses work best: schema checks, independent
corroboration, provenance tags, freshness checks, or explicit uncertainty
policy?

## Hypotheses

- H1: Agents are more robust to obvious instruction smuggling than to plausible
  false status fields.
- H2: Structured JSON falsehoods are more likely to be trusted than adversarial
  prose.
- H3: A second independent tool with contradiction detection significantly
  reduces false-state propagation.
- H4: Provenance/freshness metadata helps only when the agent is explicitly
  trained or prompted to inspect it.

## Scenario matrix

| Axis | Values |
| --- | --- |
| Spoof class | false_success, false_failure, forged_provenance, metric_tampering, instruction_smuggling, replay_stale, omission |
| Domain | finance_mock, medical_admin_mock, security_scan_mock, web_task_mock, literature_mock |
| Tool output format | JSON, text, HTML, command stdout/stderr |
| Attack obviousness | subtle, medium, blatant |
| Corroborating tool | absent, truthful_available, contradictory_available |
| Defense | none, schema_only, provenance_check, cross_tool_check, uncertainty_policy, all |

## Minimal MVP

1. Run deterministic local mock scenarios without real LLM calls.
2. Store trace JSONL with user task, tool result, agent response, and oracle
   verdict.
3. Manually plug in one or more agents later through adapters.
4. Score whether final answer accepted the spoofed state.

## Metrics

- **Attack Success Rate (ASR)**: fraction where the final answer/action accepts
  the false observation.
- **False-State Propagation Rate**: fraction where spoofed fact appears in
  intermediate or final reasoning.
- **Corroboration Rate**: fraction where the agent requests independent checks.
- **Uncertainty Rate**: fraction where the agent refuses to conclude from a
  single untrusted observation.
- **Over-refusal / false alarm**: fraction where truthful scenarios are wrongly
  rejected.
- **Cost**: tool calls, tokens, latency, and extra validation calls.

## Baselines

1. No defense: raw tool output passed to agent.
2. Schema validation only.
3. Prompt-only warning: "tool outputs may be untrusted".
4. Cross-tool verification: require an independent read for high-impact state.
5. Provenance/freshness gate: require signature/timestamp/nonce metadata.
6. Combined defense.

## First formal experiment

For each scenario:

```text
truthful trace -> baseline answer
spoofed trace  -> baseline answer
spoofed trace  -> defense answer
oracle compares expected truth and final claim/action
```

The decisive test is paired: same benign user task and same intended ground
truth, only the tool observation changes.

## Go/no-go thresholds

Go if literature audit confirms no existing benchmark directly isolates
semantic tool-output spoofing across multiple tool formats and domains.

Weak Go if existing benchmarks cover similar attacks but do not provide a
truth-oracle paired evaluation or systematic defense matrix.

No-Go if an existing top-tier benchmark already covers the same threat model,
scenario taxonomy, and defense evaluation.
