# Research Orchestration

Started: 2026-06-08 Asia/Shanghai.

## Subagent lanes

| Lane | Output | Write scope |
| --- | --- | --- |
| Top security / NLP papers | `secondary-research/deep-dive/topsec-nlp-audit.md` | `papers/topsec-nlp/` |
| Benchmark / evaluation suites | `secondary-research/deep-dive/benchmark-eval-audit.md` | `papers/benchmarks/` |
| System security / threat model | `secondary-research/deep-dive/system-threat-model-audit.md` | `papers/systems-security/` |
| Core reading seed / templates | `secondary-research/deep-dive/core-reading-seed.md` | `papers/core/`, `docs/reading-template.md`, `docs/literature-matrix.md` |

## Main-agent local work

- Capture the exact idea and non-goals.
- Create no-GPU engineering scaffold.
- Create initial threat model, scenario matrix, runner, oracle, and smoke tests.
- Integrate subagent audit outputs after they complete.

## Initial search vocabulary

- tool-output spoofing
- malicious tool result
- compromised tool server
- untrusted tool feedback
- observation poisoning
- response-path attack
- indirect prompt injection
- RAG poisoning
- malicious plugin / MCP server
- agent security benchmark
