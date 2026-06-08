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
  is complete, but ToolSandbox full overlay is still running. As of
  2026-06-09 00:30 CST it had produced 7703/12384 expected
  `gpt-5.4-mini` ToolSandbox trace files under five remote shards. The paper
  still lacks the merged ToolSandbox result and multi-model evidence.
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

1. Complete and merge at least two existing benchmark substrates with full
   overlay artifacts; do not substitute candidate slices for the full runs.
2. Add at least two models, preferably three: strong closed model, cheaper/small
   closed model, and a reproducible open/local model.
3. Keep the pre-registered scoring contract frozen and make full-run artifacts
   explicitly emit projection/non-decisive field metadata instead of leaving it
   implicit in scorer code.
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
| End-to-end evaluation harness dataflow | Covered by `figures/figure10_end_to_end_harness_dataflow.svg`; keep this as the camera-ready deterministic vector version. |
| Current pilot vs full agent-loop gap | Covered by `figures/figure9_pilot_vs_agent_loop_gap.png`; should be redrawn as vector before final submission if image text artifacts remain. |
| Validator independence graph | Covered by `figures/figure8_validator_independence_graph.png`; should be redrawn as vector before final submission if image text artifacts remain. |
| Per-substrate overlay instantiation | Covered by `figures/figure13_per_substrate_overlay_instantiation.svg`; update ToolSandbox status after merge. |
| Scoring pipeline and projection boundary | Covered by `figures/figure11_scoring_projection_boundary.svg`; still need to keep the scoring contract frozen before final multi-model runs. |
| Defense policy lattice | Order baselines by evidence strength, deployability, hidden access, and cost. |
| Experimental matrix completion heatmap | Covered by `figures/figure12_experiment_completion_heatmap.svg`; update the ToolSandbox status after the remote run finishes. |

## Latest strict reviewer update

A reused CCF-A reviewer subagent restated the main decision as: the project is
promising and now has real full-overlay evidence on AgentDojo, but it is still
not a CCF-A full paper until ToolSandbox full results, multi-model robustness,
explicit artifact-level scoring contract, and statistical tests are integrated. The manuscript
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
   AgentDojo full now has Wilson CI plus exact paired McNemar/binomial tests
   with Holm correction in `outputs/agentdojo_model_full_stats.json`;
   ToolSandbox needs the same treatment after merge.
3. Add at least one additional model only after the `gpt-5.4-mini` full
   ToolSandbox+AgentDojo result is merged and inspected.
4. Replace or supplement raster concept figures with camera-ready vector figures
   for final submission.
5. Keep AgentDojo as portability/full-substrate evidence unless clean utility is
   repaired enough to support defense-effectiveness claims.

## Current remote-run gate

The current ToolSandbox full run is a required gate before the manuscript can
claim two existing-benchmark full-overlay evidence. The run uses
`gpt-5.4-mini`, `configs/experiments/toolsandbox_model_full.json`, and full
`outputs/toolsandbox_full_manifest.json` on the remote cloud host. It is
sharded across five `ts_full_stable_*` screens, with `full_monitor` configured
to merge shard summaries, compute CI, run prompt-leakage audit, and generate
paired-statistics diagnostics after completion.

Important reviewer-facing nuance: failed earlier cells must not be silently
counted as robustness. The runner now reuses only completed real model traces
whose final event came from `model_chat_completion`; empty, malformed,
provider-error, missing-final, or non-executed traces are marked invalid and
rerun. The paper should report `invalid_existing_trace_count`, API/parse
errors, and final attempted denominators when the merged result is available.

As of the latest remote check, `outputs/full_monitor.log` shows the monitor is
alive and the trace directory contains 7703 files, but shard summaries do not
exist yet because the five shard screens are still running. The main paper
should therefore continue to report ToolSandbox as an in-progress gate, not as
a result.

The reproducible post-processing command now lives in
`scripts/postprocess_full_model_run.sh`, so the paper should refer to that
script instead of relying on an opaque remote-only monitor.

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
  errors. AgentDojo now has a first utility funnel artifact in
  `outputs/agentdojo_model_full_stats.json`, but it must be turned into a
  camera-ready table and replicated for ToolSandbox.
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
  `d`, and oracle `O`. Covered in `docs/paper-draft-zh.md` Section 3.1; final
  English version should preserve the same symbols.
- Define schema-valid, semantic falsehood, non-instructional payload, and
  field-level edit. Mostly covered; still needs a concise final-paper glossary.
- Formalize attacker control: primary-only, validator-aware, stale replay,
  binding mismatch, provenance forgery, and adaptive generator budget. Section
  3.2 now covers primary-only, validator-aware, failure-domain cases, and
  adaptive-generator budget; stale replay/binding/provenance remain examples in
  the threat model.
- Formalize deployable vs privileged defenses.
- State read-back validity assumptions: primary and read-back channels must not
  share the same compromised failure domain. Covered in Section 3.2 with
  \(P(F_v=1\mid F_p=1)\ll 1\).
- Give deterministic accepted-false-state scoring rules. Covered by the
  commit/hedge/reject/irrelevant rubric in Section 3.1.
- Define authorization evidence ladder monotonicity and verified-positive
  controls.
- Formalize API/parse error handling and denominator policy. Partly covered in
  Section 7 and CI/stats artifacts; final tables should include an explicit
  denominator footnote.

## Pre-registration and artifact contract

`docs/pre_registered_scoring_contract.md` now freezes the intended full-run
scoring contract: required per-cell fields, decisive fields, restricted
projection paths, accepted-false-state rubric, verification five-level fields,
API/parse error denominator policy, paired tests, and readiness gates. Remaining
implementation work is to emit `allowed_projection_paths`,
`non_decisive_fields`, and the five verification levels directly in future
merged full-run artifacts rather than leaving them implicit in scorer code.

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
