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

- Expanded the local partial benchmark from 6 to 15 scenarios, matching a 10%
  slice of a 150-scenario-pair benchmark target.
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
  smoke pilot rather than the 10% benchmark slice.
- Added `configs/experiments/partial_pilot_newapi_smoke6.json` to preserve the
  old smoke-pilot configuration separately from the new 15-scenario pilot
  config.
- Updated `docs/paper-draft.md` to include concrete benchmark counts,
  baseline access assumptions, pilot result tables, and the remaining
  limitations.
- Updated `docs/partial-pilot-results.md` with the deterministic 10% slice and
  explicit non-paper-grade limitations.

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
