# CCF-A reviewer gap analysis

This note records a deliberately harsh USENIX Security / IEEE S&P / NDSS /
CCS-style review of the current manuscript state. It is a planning artifact,
not a claim that the listed gaps are solved.

## Current safe claims

- The paper defines a meaningful observation-integrity problem:
  schema-valid, non-instructional, semantically false tool observations.
- The overlay protocol is clear: keep hidden truth and the original benchmark
  oracle fixed, and replace only the model-visible observation plane.
- Current pilots and the completed AgentDojo 1552-cell full overlay show that
  weak baselines can accept false observations, while read-back or
  authority-style validators can reduce false acceptance in the tested
  trace-final-decision setting.
- The prompt-leakage audit is a strong artifact-level control: current pilot
  prompts do not obviously expose hidden oracle, mode labels, raw results, or
  expected scores.

## Claims that are not yet supported

- Two-substrate full benchmark-level evaluation. AgentDojo 97-task full overlay
  is complete, but ToolSandbox full overlay is still running and the paper still
  lacks multi-model full/candidate-slice evidence.
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
| End-to-end evaluation harness dataflow | Show benchmark task, real execution, hidden truth, overlay, model-visible trace, model decision, and oracle scoring. Partially covered by Figure 7/9; still needs a camera-ready deterministic vector version. |
| Current pilot vs full agent-loop gap | Covered by `figures/figure9_pilot_vs_agent_loop_gap.png`; should be redrawn as vector before final submission if image text artifacts remain. |
| Validator independence graph | Covered by `figures/figure8_validator_independence_graph.png`; should be redrawn as vector before final submission if image text artifacts remain. |
| Per-substrate overlay instantiation | Show which parts are implemented for ToolSandbox/AgentDojo and which remain planned for tau/Web/SWE/RAG. |
| Scoring pipeline and projection boundary | Pre-register exact-primary vs restricted read-back projection and show forbidden paths. |
| Defense policy lattice | Order baselines by evidence strength, deployability, hidden access, and cost. |
| Experimental matrix completion heatmap | Mark done pilot, running, planned, and missing cells across substrates, models, baselines, and generators. |

## Latest strict reviewer update

A reused CCF-A reviewer subagent restated the main decision as: the project is
promising and now has real full-overlay evidence on AgentDojo, but it is still
not a CCF-A full paper until ToolSandbox full results, multi-model robustness,
pre-registered scoring, and statistical tests are integrated. The manuscript
should therefore avoid the phrase "full agent benchmark" unless an autonomous
agent-loop interception experiment is added. The safest current framing is:

> Observation-spoofing overlay protocol plus first full-substrate evidence that
> schema-valid, non-instructional false tool observations are a real
> trace-final-decision failure mode; read-back/split-channel validation is a
> strong candidate defense, but deployability and clean utility require further
> evidence.

Priority route from the reviewer:

1. Finish ToolSandbox full overlay and report it separately from AgentDojo.
2. Add confidence intervals and paired tests before making comparative claims.
3. Add at least one additional model only after the `gpt-5.4-mini` full
   ToolSandbox+AgentDojo result is merged and inspected.
4. Replace or supplement raster concept figures with camera-ready vector figures
   for final submission.
5. Keep AgentDojo as portability/full-substrate evidence unless clean utility is
   repaired enough to support defense-effectiveness claims.

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
