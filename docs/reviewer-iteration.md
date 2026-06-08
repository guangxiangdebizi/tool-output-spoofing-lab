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
