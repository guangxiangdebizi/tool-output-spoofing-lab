# CCF-A reviewer gap analysis

This note records a deliberately harsh USENIX Security / IEEE S&P / NDSS /
CCS-style review of the current manuscript state. It is a planning artifact,
not a claim that the listed gaps are solved.

## Current safe claims

- The paper defines a meaningful observation-integrity problem:
  schema-valid, non-instructional, semantically false tool observations.
- The overlay protocol is clear: keep hidden truth and the original benchmark
  oracle fixed, and replace only the model-visible observation plane.
- Current pilots show that weak baselines can accept false observations, while
  read-back or authority-style validators can reduce false acceptance in the
  tested settings.
- The prompt-leakage audit is a strong artifact-level control: current pilot
  prompts do not obviously expose hidden oracle, mode labels, raw results, or
  expected scores.

## Claims that are not yet supported

- Full benchmark-level evaluation. Current canonical completed evidence is
  still small: ToolSandbox 72 cells over 6 tasks and AgentDojo 64 cells over 4
  tasks.
- Full autonomous LLM-agent risk. The current runners evaluate model final
  decisions over scripted tool-plan traces, not autonomous planning,
  tool-selection, recovery, and long-horizon agent loops.
- General deployability of independent validators. Privileged oracle access,
  hidden registries, and deployable signed/read-back authorities must be
  separated.
- AgentDojo defense effectiveness. Current AgentDojo clean utility is too low
  for aggregate defense-effectiveness claims.
- Cross-model robustness. Canonical completed pilots are mainly on
  `gpt-5.4-mini`.
- Optimized observation generation as a main result. It is currently validated
  only in tiny local authorization settings.

## P0 gaps before a CCF-A full-paper submission

1. Run at least two existing benchmark substrates with 30-45 paired tasks total.
2. Add at least two models, preferably three: strong closed model, cheaper/small
   closed model, and a reproducible open/local model.
3. Freeze a pre-registered scoring contract, especially restricted read-back
   projection.
4. Split validators into deployable signed/read-back authority and privileged
   oracle upper bound.
5. Repair AgentDojo clean utility or explicitly downgrade AgentDojo to
   portability/feasibility evidence.
6. Add 95% confidence intervals, paired tests, parse/API error accounting, and
   cost/latency/tool-call overhead.
7. Make the non-autonomous trace-final-decision boundary explicit in title,
   abstract, contributions, experiments, and limitations unless a full
   autonomous-agent-loop experiment is added.
8. Align full-run configs with the paper's intended model/baseline matrix.
9. Add validator-independence ablations.
10. Rewrite novelty around overlay protocol, paired hidden-truth/visible-trace
    methodology, field-level schema-valid falsehood, and authorization
    provenance drift; do not claim first study of untrusted tool feedback.

## Required figures still missing

| Figure | Purpose |
| --- | --- |
| End-to-end evaluation harness dataflow | Show benchmark task, real execution, hidden truth, overlay, model-visible trace, model decision, and oracle scoring. |
| Current pilot vs full agent-loop gap | Distinguish scripted trace final-decision evaluation from future autonomous agent-loop interception. |
| Validator independence graph | Show failure-domain sharing among primary tool, repeat same-channel, metadata-only, read-back, independent authority, and privileged oracle. |
| Per-substrate overlay instantiation | Show which parts are implemented for ToolSandbox/AgentDojo and which remain planned for tau/Web/SWE/RAG. |
| Scoring pipeline and projection boundary | Pre-register exact-primary vs restricted read-back projection and show forbidden paths. |
| Defense policy lattice | Order baselines by evidence strength, deployability, hidden access, and cost. |
| Experimental matrix completion heatmap | Mark done pilot, running, planned, and missing cells across substrates, models, baselines, and generators. |

## Required experiments and tables

- Main result table by substrate, model, mode, and baseline with ASR, accepted
  false state, clean utility, over-refusal, effective verification, and tool
  cost.
- Per-substrate table; ToolSandbox and AgentDojo should not be prematurely
  aggregated.
- Per-model robustness table.
- Generator ablation: truthful, static, random schema-valid, plausible
  template, optimized.
- Validator independence ablation: no validator, repeat same tool, same-backend
  read-back, split-channel read-back, signed authority, privileged oracle.
- Clean utility repair table that separates original task difficulty,
  truthful-overlay success, defense truthful success, parser errors, and API
  errors.
- Cost/latency/tool-call overhead table.
- Prompt leakage audit table by substrate and pilot.

## Statistical requirements

- Paired bootstrap or McNemar test for paired defense comparisons.
- Wilson or exact binomial intervals for small-sample proportions.
- Holm-Bonferroni correction for multiple baseline comparisons.
- Hierarchical bootstrap or mixed-effects logistic regression for
  substrate/model/task grouping if the final run is large enough.
- Report effect sizes, not only p-values.

## Formalism gaps

- Define tool-output spoofing with state `s`, truthful observation `y`, spoofed
  observation `y_tilde`, schema `K`, model-visible prompt `v`, model decision
  `d`, and oracle `O`.
- Define schema-valid, semantic falsehood, non-instructional payload, and
  field-level edit.
- Formalize attacker control: primary-only, validator-aware, stale replay,
  binding mismatch, provenance forgery, and adaptive generator budget.
- Formalize deployable vs privileged defenses.
- State read-back validity assumptions: primary and read-back channels must not
  share the same compromised failure domain.
- Give deterministic accepted-false-state scoring rules.
- Define authorization evidence ladder monotonicity and verified-positive
  controls.
- Formalize API/parse error handling and denominator policy.

## Top reject reasons to preempt

1. The evaluation is not a full autonomous agent benchmark.
2. Main evidence is underpowered.
3. Only one model is used.
4. AgentDojo clean utility is too low.
5. Independent validator may be an oracle.
6. Read-back projection may look post-hoc.
7. Novelty overlaps with Trust No Tool and MCP/tool-security work.
8. Authorization experiments are tiny and local.
9. No confidence intervals or paired tests.
10. Full configs currently do not yet encode a paper-grade multi-model matrix.
