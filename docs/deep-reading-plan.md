# Deep Reading Plan

## Status legend

- `seeded`: metadata and first-pass notes exist.
- `first-pass`: read enough to determine novelty impact.
- `deep-read`: filled against `docs/reading-template.md`.
- `replicate`: code/benchmark reproduction attempted.

## P0 read queue

| Order | Work | Current status | Owner/output |
| --- | --- | --- | --- |
| 1 | Trust No Tool | first-pass | `secondary-research/deep-dive/topsec-nlp-audit.md`; deep-read subagent A pending |
| 2 | MCP Security Bench | first-pass | `secondary-research/deep-dive/topsec-nlp-audit.md`; deep-read subagent A pending |
| 3 | MCP-SafetyBench | first-pass | `secondary-research/deep-dive/benchmark-eval-audit.md`; deep-read subagent A pending |
| 4 | AgentDojo | seeded | `secondary-research/deep-dive/core-reading-seed.md`; deep-read subagent B pending |
| 5 | InjecAgent | seeded | `secondary-research/deep-dive/core-reading-seed.md`; deep-read subagent B pending |
| 6 | Greshake et al. IPI | seeded | `secondary-research/deep-dive/core-reading-seed.md`; deep-read subagent B pending |
| 7 | ToolEmu | seeded | `secondary-research/deep-dive/core-reading-seed.md`; needs local deep read |
| 8 | MalTool | seeded | `secondary-research/deep-dive/core-reading-seed.md`; deep-read subagent C pending |
| 9 | CaMeL | first-pass | `secondary-research/deep-dive/system-threat-model-audit.md`; deep-read subagent C pending |
| 10 | PoisonedRAG / RAG security | seeded | `secondary-research/deep-dive/core-reading-seed.md`; deep-read subagent B pending |

## What to extract from every P0

1. Whether the decisive untrusted object is a tool result, tool metadata,
   retrieved document, tool code, browser observation, or model hallucination.
2. Whether the payload is an explicit instruction or a semantic falsehood.
3. Whether the evaluation has paired truthful/spoofed examples.
4. Whether the oracle is independent from the agent-visible observation.
5. Whether strict schema validation would pass or fail the attack.
6. Whether provenance, freshness, signatures, or independent corroboration are
   evaluated.
7. Exact novelty claims this work blocks.
8. Baselines/metrics our experiments must include.

## First paper outline if Weak-Go remains

1. Introduction: agent tool outputs as observations, not ground truth.
2. Related work: prompt injection, MCP security, malicious tools, RAG poisoning,
   untrusted tool feedback.
3. Threat model: tool-result veracity failure.
4. Benchmark: local deterministic five-suite setup.
5. Attacks: schema-valid semantic falsehoods plus instruction-smuggling
   controls.
6. Defenses: schema, PI filter, retry, cross-tool, receipts/provenance.
7. Results: ASR, utility, false positives, cost, failure analysis.
8. Discussion: deployment controls and limitations.
