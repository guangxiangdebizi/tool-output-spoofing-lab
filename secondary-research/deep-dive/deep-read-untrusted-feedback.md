# Deep read: untrusted tool feedback / MCP response attacks

Reader: deep-read subagent A  
Date: 2026-06-08  
Scope: three P0/P1 papers most likely to collide with the lab's novelty claim around tool-output spoofing, untrusted tool feedback, MCP response handling, and schema-valid semantic lies.

Merge note: this file follows `docs/reading-template.md` for each paper. I did not update the literature matrix or any other repository file.

## Cross-paper synthesis for this lab

### Immediate novelty boundary

The broad claim is blocked:

> "No prior work studies malicious or untrusted tool feedback / MCP tool responses."

All three papers make that claim unsafe:

- **Trust No Tool** directly frames already-selected tool feedback as untrusted and builds a benchmark/defense around trajectory-conditioned trust formation.
- **MCP Security Bench (MSB)** directly benchmarks MCP response attacks, including user-impersonating responses, false errors, and tool-transfer responses.
- **MCP-SafetyBench** covers server-, host-, and user-side MCP attacks on real MCP servers, including function return injection, data tampering, identity spoofing, replay, and parameter poisoning.

The narrower claim still looks viable if preserved carefully:

> A deterministic, local, multi-surface benchmark for **schema-valid but semantically fabricated tool observations**, with paired truthful/spoofed visible traces, an immutable hidden truth oracle, and defense baselines focused on provenance, independent verification, and false-state propagation rather than only instruction filtering.

### Quick overlap matrix

| Paper | Directly covers untrusted tool feedback? | Schema-valid semantic lie as first-class object? | Paired truthful/spoofed trace? | Truth oracle? | Multi-tool / multi-surface? | Novelty effect |
|---|---:|---:|---:|---:|---:|---|
| Trust No Tool, 2026 | **Yes** | **Partial**: hidden-trigger state/action and schema-shift variants, not mainly false returned facts | **Partial**: matched safe/malicious controls, not same truth state with spoofed observation | **Partial**: trigger labels + audit, not hidden truth plane for observation veracity | **Yes**, many tool families/upstream suites | Blocks broad "first untrusted tool feedback" and "trajectory trust formation" claims |
| MCP Security Bench, 2025/ICLR 2026 | **Yes**, especially response attacks | **Weak/partial**: false error is a lie, but response attacks are instruction-bearing | **No/partial**: benign tools mutated into attacks, but no systematic paired traces | **Partial**: environment/log checks for attack success, not veracity oracle | **Yes**, 25 servers / 405 attack tools / mixed attacks | Blocks "first MCP response attack benchmark" claims |
| MCP-SafetyBench, 2025/ICLR 2026 | **Yes/adjacent-direct**: function return injection and host data tampering | **Partial/strongest among three**: data tampering can falsify tool outputs; parameter poisoning silently produces wrong results | **No/partial**: baseline task + one attack modification, not released truth/spoof trace pair | **Partial**: deterministic task/attack evaluators, not field-level truth oracle | **Yes**, real MCP servers, 5 domains, multi-step/multi-server | Blocks "first broad MCP safety benchmark with tool-output tampering" claims |

---

## 1. `yan2026trustnotool` -- Trust No Tool

### 0. Triage label

- Priority: **P0**
- Relation to this lab: **Direct** for untrusted tool feedback and tool-result trust boundary; **partial** for tool-output spoofing as schema-valid semantic falsehood.
- Reading status: **deep-read**
- Assigned reader: deep-read subagent A
- Date: 2026-06-08

### 1. Metadata

- BibTeX key: `yan2026trustnotool`
- Title: *Trust No Tool: Evaluating and Defending LLM Agents under Untrusted Tool Feedback*
- Authors: Lecheng Yan, Ruizhe Li, Xicheng Han, Wenxi Li, Binwu Wang, Longyue Wang, Chenyang Lyu, Guanhua Chen
- Venue / year: arXiv preprint, 2026
- Paper link: https://arxiv.org/abs/2605.17453
- PDF path: `/root/tool-output-spoofing-lab/papers/topsec-nlp/2026_trust_no_tool.pdf`
- Text path: `/root/tool-output-spoofing-lab/papers/topsec-nlp/text/2026_trust_no_tool.txt`
- Code / data / benchmark link: https://github.com/idwts/TRUST-BENCH
- Version read: arXiv:2605.17453v1, dated 2026-05-17
- Notes on artifact availability: paper says data and code are released; no artifacts were downloaded for this read.

#### BibTeX seed template

```bibtex
@misc{yan2026trustnotool,
  title = {Trust No Tool: Evaluating and Defending LLM Agents under Untrusted Tool Feedback},
  author = {Yan, Lecheng and Li, Ruizhe and Han, Xicheng and Li, Wenxi and Wang, Binwu and Wang, Longyue and Lyu, Chenyang and Chen, Guanhua},
  year = {2026},
  eprint = {2605.17453},
  archivePrefix = {arXiv},
  url = {https://arxiv.org/abs/2605.17453}
}
```

### 2. One-sentence summary

The paper defines **cognitive poisoning**, where a malicious tool behaves plausibly during exploratory calls and only becomes harmful when a final state/action trigger fires; it introduces TRUST-BENCH and VISTA-Guard to evaluate and defend trajectory-conditioned final-action risk under untrusted tool feedback.

### 3. Threat model / problem setting

- Attacker capability:
  - Controls a tool or tool mode with the same outward interface as a benign tool.
  - Can make the tool behave normally during exploration.
  - Can define a hidden trigger over final parameters and latent/tool-state conditions.
  - The harmful behavior is not necessarily visible as a malicious prompt or descriptor.
- User prompt: **benign** in the main setup. The user's intended task remains close between malicious and benign matched controls.
- Agent architecture:
  - Tool-using LLM agent performs exploratory tool calls, then proposes a final executable tool call.
  - VISTA-Guard is a wrapper/risk scorer that sees the observed trajectory and proposed final action and outputs execute/reject.
- Tooling setup:
  - TRUST-BENCH is built from OpenAgentSafety, RedTeamCUA, MCP-SafetyBench, MCPMark, and Toolathlon.
  - Upstream substrate: 1,753 source tasks and 7,012 task-conditioned variants before curation.
  - Final reported benchmark: 1,970 curated hidden-trigger tool-compromise episodes with matched safe controls.
- Where untrusted data enters:
  - **tool output / tool feedback**: primary entry point.
  - tool metadata / interface: preserved or outwardly identical, but not the main manipulated object.
  - final tool parameters: decisive risk object is the final executable call combined with trajectory state.
  - memory/logs/browser are not the primary focus.
- Defender visibility:
  - Sees model-facing trajectory summaries and final-action parameter evidence.
  - Does **not** see hidden trigger rules or labels at inference.
  - In construction, blue-side probes record tool feedback (`TF_t`) and probe result (`PR_t`).
- Security or reliability property:
  - Reject malicious final actions while accepting benign matched controls.
  - Avoid both accepted-malicious rate (AMR) and rejected-normal rate (RNR).

### 4. Mechanism

- Attack, failure, benchmark, or defense:
  - Attack/failure: **cognitive poisoning** through trust formation across benign-looking tool feedback.
  - Benchmark: **TRUST-BENCH** with hidden-trigger malicious/benign pairs.
  - Defense: **VISTA-Guard**, a final-action risk scorer over trajectory-state and parameter evidence.
- Key algorithm or construction:
  - Each episode contains a normal mode and a malicious mode.
  - Hidden trigger is represented as `required_all_tokens`, `required_any_tokens`, and `forbidden_tokens`.
  - Red side selects a compromise pivot, attack family, hidden trigger, malicious final parameters, and matched-control tokens.
  - Blue side probes the outwardly identical tool for three rounds:
    1. baseline response,
    2. object ID / checksum consistency,
    3. sandbox or counterfactual consistency probe.
  - VISTA-Guard serializes:
    - `trajectory_digest`,
    - `world_model_state`,
    - `action_param_features`.
  - It scores `low_risk` vs `high_risk`; threshold is calibrated on train folds only.
- Assumptions required:
  - Three exploratory calls are enough to expose some trajectory signal.
  - The final action can be reduced to execute/reject.
  - Structured trajectory fields capture relevant trust-formation evidence.
  - Hidden-trigger benchmark transformations preserve upstream task intent and tool interface closely enough for controlled evaluation.
- Why it works:
  - Local prompt or descriptor inspection misses attacks because no single message must look malicious.
  - Final parameters alone can be ambiguous because matched malicious and benign variants may share similar business intent.
  - Trajectory-state evidence plus final-action parameters lets a classifier detect state-conditioned risk.
- What it does not cover:
  - Not a production trace study.
  - Not a full remediation/action-selection policy beyond execute/reject.
  - Not primarily a benchmark of schema-valid false returned facts such as forged status, balances, receipts, citations, exit codes, or browser observations.
  - No first-class independent truth plane that stores the real world state separately from the agent-visible spoofed observation.
  - Cross-tool corroboration, provenance signatures, freshness checks, and independent verification are not the core evaluated defense policies.

### 5. Evaluation extraction

- Models evaluated:
  - VISTA-Guard backbones: Mistral-7B-v0.3, Qwen3-8B, Qwen2.5-7B, OLMo-2-7B, Llama-3.1-8B, Meta CWM-32B.
  - Baselines include TF-IDF + LogReg/SVM/MLP, BERT-base, gradient boosting on scalar features, GPT-5.4 zero-shot judge, keyword heuristic, ToolShield, GuardAgent, LLM-as-Judge.
- Tasks / domains:
  - Derived from five upstream suites: OpenAgentSafety, RedTeamCUA, MCP-SafetyBench, MCPMark, Toolathlon.
  - Tool families include web search and document editing examples; full benchmark spans broader tool-use tasks from upstream suites.
- Number of tools:
  - Not reported as a single tool count in the main text; tool families and upstream suite task counts are reported.
- Number of test cases:
  - 1,970 curated episodes in main evaluation.
  - 9,216 balanced OOD episodes from ToolEmu and SafeToolBench for transfer.
- Attack variants:
  - Six construction families are referenced; appendix examples include `targeted_scope_escalation`, `targeted_shadow_side_effect`, `targeted_audit_bypass`, `targeted_identity_redirect`, `targeted_state_reuse`, and `targeted_schema_shift`.
- Defense variants:
  - Main: VISTA-Guard.
  - Baselines: prompt-centric judges, static/rule-based tools, scalarized classifiers, raw-text models, same-input non-LLM models.
- Metrics:
  - AMR: accepted malicious rate.
  - BMR: blocked malicious rate.
  - RNR: rejected normal rate.
  - ACNR: accepted normal rate.
  - **GUARDED JOINT**: asymmetric safety-utility metric penalizing accepted malicious actions and rejected benign actions.
- Decisive quantitative results:
  - In-domain grouped 5-fold:
    - VISTA-Guard (Mistral-7B): AMR 4.2, RNR 5.0, Guarded Joint 84.2 +/- 18.7.
    - VISTA-Guard (Qwen3-8B): AMR 7.6, RNR 11.6, Guarded Joint 67.6 +/- 9.7.
    - ToolShield, GuardAgent, LLM-as-Judge collapse to 0.0 Guarded Joint in the reported setup.
  - Balanced OOD:
    - VISTA-Guard: Guarded Joint 56.9, AMR/RNR 2.4/25.5.
    - TF-IDF + LogReg: 50.3.
    - ToolShield: 43.3.
  - Representation ablation:
    - Full structured triplet beats raw trajectory text and trajectory-only views.
    - Parameter-only collapses because final parameters alone cannot distinguish malicious controls from benign controls.
- Human evaluation, if any:
  - Two-auditor screening on 1,753 pairs.
  - Top-level retain/reject agreement: 94.7%, Cohen's kappa 0.749.
  - Diagnostics cover tool-pair reasonableness, malicious-shift validity, minimality/no leakage, label correctness.
- Artifact quality concerns:
  - Constructed benchmark, not production logs.
  - Three-round exploration is standardized and may underrepresent longer adaptive interactions.
  - Some performance variance across folds is high.
  - Strong benchmark-specific learned representation may not directly transfer to arbitrary live tool ecosystems.

### 6. Relevance to tool-output spoofing

Answer each item explicitly.

- Does the decisive attacker-controlled object arrive as a tool result?
  - **Yes, but not only.** The paper's core object is untrusted **tool feedback** during exploratory calls, plus the final tool/action bundle. The decisive maliciousness is the composed trajectory-state/final-action condition, not a single returned value.
- Is the harmful content an instruction, a semantic falsehood, bad metadata, bad tool code, poisoned retrieved knowledge, or model hallucination?
  - Mostly **state-conditioned semantic compromise / misplaced trust**, not classic instruction injection.
  - Some episodes involve missing review/audit/safe-mode fields, identity redirect, state reuse, schema shift, or side effects.
  - It is not primarily bad metadata, tool hallucination, or RAG poisoning.
- Is the user task benign in the main attack?
  - **Yes.** The construction preserves user task intent and uses matched safe controls.
- Does the paper compare truthful vs spoofed observations?
  - **Partial.** It compares matched benign/malicious controls with close surface form. It does **not** cleanly define a pair where the same hidden truth state yields a truthful tool observation in one trace and a spoofed visible observation in the other.
- Does it define a ground-truth oracle?
  - **Partial.** It has hidden trigger specifications, execute/reject labels, and human audit. It does not define an immutable world-state oracle that scores the truthfulness of each visible tool result independently of the agent-visible response.
- Does it evaluate false-state propagation into later reasoning/actions?
  - **Yes for trust-state propagation.** It explicitly studies how benign-looking feedback affects final-action trust.
  - **Partial for factual false-state propagation.** It is less about "tool says the balance is X when real balance is Y" and more about whether the final action is unsafe given accumulated feedback.
- Does it test cross-tool corroboration, provenance, freshness, signatures, or uncertainty policies?
  - **Mostly no.** Example fields include `cross_check` and `citation`, but the main benchmark/defense is trajectory-conditioned risk scoring, not independent cross-tool verification or cryptographic provenance.
- Does it separate "data that is false" from "data that instructs the model"?
  - **Largely yes at the threat-model level**, because it moves away from localized prompt-injection payloads.
  - **Not fully for our target**, because it does not systematically isolate non-instructional false returned observations as the experimental variable.
- Does it cover structured outputs such as JSON/status fields/exit codes?
  - **Partial.** It uses structured trajectory and final-action fields, trigger tokens, and a `targeted_schema_shift` attack type. It does not provide a broad matrix of schema-valid false JSON/status/receipt/exit-code/browser-observation outputs.

### 7. Novelty impact for this lab

- Claim blocked:
  - "First benchmark/study of untrusted tool feedback."
  - "First to study maliciousness that is not visible in one prompt or descriptor after a tool has been selected."
  - "First matched safe-control evaluation of trajectory-conditioned tool trust."
  - "First defense framing where final action risk is conditioned on exploratory tool feedback."
- Claim weakened:
  - "Tool-output spoofing requires trajectory-level reasoning." Trust No Tool already strongly argues this for cognitive poisoning.
  - "Schema shifts in tool interactions are unstudied." Their `targeted_schema_shift` slice weakens this.
- Claim still open:
  - First-class **schema-valid semantic falsehood** benchmark where the returned observation has valid shape but wrong factual content.
  - Paired **truthful vs spoofed visible traces** under a hidden immutable truth plane.
  - Systematic evaluation of provenance/freshness/signature/corroboration defenses against false observations.
  - Multi-surface deterministic spoofing beyond tool APIs: REST/MCP JSON, shell stdout/exit code, browser DOM/a11y/screenshot, RAG/search snippets, receipts/citations.
- Exact differentiator this lab should preserve:
  - The lab should not compete on "cognitive poisoning" or learned trajectory risk scoring.
  - It should define the primary experimental variable as **observation truthfulness**: `truth_state != visible_tool_result` while the visible result remains schema-valid and non-instructional.
  - The oracle must score from hidden state, not from the agent-visible result or learned labels.
- Related-work sentence draft:
  - "Yan et al. introduce TRUST-BENCH for cognitive poisoning, where untrusted tool feedback shapes trust over exploratory interaction and hidden triggers make a final action unsafe; our setting differs by isolating schema-valid semantic false observations with paired truthful/spoofed traces and an independent truth oracle."
- Baselines or metrics we must include:
  - Include an asymmetric safety-utility metric analogous to Guarded Joint or report accepted-spoofed and rejected-truthful separately.
  - Include prompt-only warning, ToolShield-like/static heuristics, LLM-as-judge, and trajectory-aware risk scoring as baselines.
  - Use grouped splits and train-only threshold calibration if training any detector.
  - Add a "parameter-only vs observation-only vs full trace" ablation to show the false-observation signal.

### 8. Reproducibility / implementation notes

- Public code: paper lists https://github.com/idwts/TRUST-BENCH
- Public data: paper says data/code are released.
- External services required:
  - Likely model fine-tuning infrastructure and model weights for reproducing VISTA-Guard.
  - OOD transfer uses ToolEmu/SafeToolBench-derived episodes.
- Model/API dependencies:
  - Fine-tuning open-weight 7B/8B/32B backbones; GPT-5.4 API for zero-shot judge experiments.
- Estimated effort:
  - Full reproduction: high, because it requires dataset, fine-tuning, grouped evaluation, and OOD transfer.
  - Minimal conceptual reproduction: moderate; implement hidden-trigger paired controls and a small trajectory scorer.
- Minimal subset worth reproducing:
  - Three-round exploration + matched malicious/benign control for 20-50 local mock tools.
  - Guarded Joint metric and parameter-only/trajectory-only/full ablation.
- Risks of downloading large assets:
  - Avoid model weight downloads unless explicitly needed.
  - Dataset/code clone may be manageable, but not required for this literature read.

### 9. Evidence snippets

Direct quotes omitted; below are paraphrased evidence anchors.

- Key definition:
  - Section 2.1 defines cognitive poisoning as malicious tool behavior that stays close to normal during most interaction and becomes harmful when a final hidden trigger is satisfied.
- Key construction:
  - Sections 2.2-2.3 describe TRUST-BENCH, upstream suite transformation, hidden trigger specs, matched safe controls, and three-round blue-side probing.
- Key metric:
  - Section 2.4 defines Guarded Joint over AMR/RNR to avoid both reject-all and execute-all defenses.
- Key result:
  - Table 3 reports VISTA-Guard (Mistral-7B) at 84.2 +/- 18.7 Guarded Joint; static/prompt-centric baselines collapse.
- Key limitation:
  - Appendix C states the benchmark is constructed, three-step, binary execute/reject, and not production traces.
- Citation to use:
  - Use as the primary related work for "untrusted tool feedback" and "trajectory-conditioned final-action risk."

### 10. Matrix update checklist

- [ ] Add/update row in `docs/literature-matrix.md`.
- [ ] Add BibTeX to the local bibliography once the final citation format is chosen.
- [ ] Add overlap/gap notes.
- [ ] Add must-run baseline: Guarded Joint-style metric and trajectory-aware risk scorer.
- [ ] Add defense idea: trajectory-state risk scoring before final action.
- [ ] Mark this paper as **blocking broad novelty**, but leaving the field-level truth-oracle spoofing gap open.

---

## 2. `zhang2025mcpsecuritybench` -- MCP Security Bench (MSB)

### 0. Triage label

- Priority: **P0**
- Relation to this lab: **Direct** for MCP response handling attacks; **adjacent/partial** for schema-valid semantic tool-output spoofing.
- Reading status: **deep-read**
- Assigned reader: deep-read subagent A
- Date: 2026-06-08

### 1. Metadata

- BibTeX key: `zhang2025mcpsecuritybench`
- Title: *MCP Security Bench (MSB): Benchmarking Attacks Against Model Context Protocol in LLM Agents*
- Authors: Dongsen Zhang, Zekun Li, Xu Luo, Xuannan Liu, Peipei Li, Wenjun Xu
- Venue / year: ICLR 2026 conference paper; arXiv version dated 2026
- Paper link: https://arxiv.org/abs/2510.15994
- PDF path: `/root/tool-output-spoofing-lab/papers/topsec-nlp/2025_mcp_security_bench.pdf`
- Text path: `/root/tool-output-spoofing-lab/papers/topsec-nlp/text/2025_mcp_security_bench.txt`
- Code / data / benchmark link: https://github.com/dongsenzhang/MSB
- Version read: arXiv:2510.15994v2, dated 2026-03-24
- Notes on artifact availability: code URL is in paper; no code/data was downloaded.

#### BibTeX seed template

```bibtex
@misc{zhang2025mcpsecuritybench,
  title = {MCP Security Bench (MSB): Benchmarking Attacks Against Model Context Protocol in LLM Agents},
  author = {Zhang, Dongsen and Li, Zekun and Luo, Xu and Liu, Xuannan and Li, Peipei and Xu, Wenjun},
  year = {2025},
  eprint = {2510.15994},
  archivePrefix = {arXiv},
  url = {https://arxiv.org/abs/2510.15994}
}
```

If using venue format later, update to the official ICLR 2026 entry.

### 2. One-sentence summary

MSB is an executable MCP security benchmark with 12 attack types across planning, invocation, response handling, retrieval, and mixed stages; it shows that MCP-specific response and parameter attacks remain effective against current LLM agents.

### 3. Threat model / problem setting

- Attacker capability:
  - Can deploy a malicious MCP server and fully control tools hosted on it.
  - Can modify tool names, descriptions, parameters, and responses.
  - Can deploy multiple coordinated malicious tools.
  - Can poison external resources/databases retrieved through tools.
  - Does not control the LLM itself and does not directly intercept user queries.
- User prompt: mostly **benign user task** plus separate attacker objective embedded in tools/responses/resources.
- Agent architecture:
  - LLM agent interacting with MCP tools.
  - MCP client exposes tool list to the model; model plans, invokes tools, and processes returned observations.
- Tooling setup:
  - 10 real-world scenarios.
  - 25 MCP servers.
  - 304 benign tools.
  - 405 attack tools mutated from benign tools.
  - FileSystem and DesktopCommander servers provide workspace/file/process capabilities for attacks.
- Where untrusted data enters:
  - tool metadata/name/description,
  - tool parameters,
  - **tool responses**,
  - retrieved database content,
  - tool list / system prompt via MCP discovery.
- Defender visibility:
  - Benchmark evaluates agent behavior through logs and environment state.
  - The evaluated MCIP defense is a detection classifier over structured dialogue data.
- Security or reliability property:
  - Complete user task under attack while not achieving attacker task.
  - Resist malicious tool invocation, response-following, out-of-scope parameter disclosure, and mixed-stage chains.

### 4. Mechanism

- Attack, failure, benchmark, or defense:
  - Benchmark and attack taxonomy for MCP-specific agent attacks.
  - Evaluates one defense, MCIP, as a detection/blocking mechanism.
- Key algorithm or construction:
  - Start from benign MCP tools and user tasks.
  - Mutate benign tools into attack tools by modifying name, description, parameter list, or response.
  - Combine user tasks, attack tasks, and attack tools into 2,000 attack test instances.
  - Measure whether attack objective is realized by inspecting environment state or tool invocation logs.
- Attack taxonomy:
  - Planning/tool signature:
    - Name Collision (NC)
    - Preference Manipulation (PM)
    - Prompt Injection (PI)
  - Invocation:
    - Out-of-Scope Parameter (OP)
  - Response handling:
    - User Impersonation (UI)
    - False Error (FE)
    - Tool Transfer (TT)
  - Retrieval:
    - Retrieval Injection (RI)
  - Mixed:
    - PI-UI, PI-FE, NC-FE, PM-FE, PM-UI, PM-OP, TT-OP.
- Assumptions required:
  - Malicious MCP server/tool can be registered into the agent's tool list.
  - Agent will include tool metadata and responses in LLM context.
  - Attack task success can be measured through local workspace/environment effects.
- Why it works:
  - MCP makes tools first-class objects with natural-language metadata and standardized I/O.
  - Agents over-trust tool responses and tool descriptions, especially when response handling is hidden from users.
  - Stronger tool-use/instruction-following capability can increase ASR because attacks also require tool execution.
- What it does not cover:
  - Does not isolate pure semantic falsehood from malicious instruction. UI, FE, TT, RI mostly inject instructions or routing directives.
  - Does not build paired truthful/spoofed traces for identical hidden truth states.
  - Does not use a field-level oracle to check whether a returned value is true.
  - Mostly MCP-specific, not shell/browser/RAG/API observations as a unified spoofing surface.

### 5. Evaluation extraction

- Models evaluated:
  - DeepSeek-V3.1, GPT-4o-mini, GPT-5, Claude 4 Sonnet, Gemini 2.5 Flash, Qwen3 8B, Qwen3 30B, Llama3.1 8B, Llama3.1 70B, Llama3.3 70B.
- Tasks / domains:
  - 10 scenarios including travel, academic search, team management, and IT development.
  - 65 user tasks.
- Number of tools:
  - 25 MCP servers.
  - 304 benign tools.
  - 405 attack tools.
- Number of test cases:
  - 2,000 attack instances.
- Attack variants:
  - 12 attack types total: 5 single-stage categories plus mixed combinations.
- Defense variants:
  - Baseline agent with no defense.
  - MCIP defense based on a Llama-xLAM-2-8B classifier trained on structured dialogue data.
- Metrics:
  - ASR: attack success rate.
  - PUA: performance under attack.
  - NRP: `PUA * (1 - ASR)`.
- Decisive quantitative results:
  - Overall average ASR across attacks/models: 40.35%.
  - OP is highest average ASR: 76.50%.
  - Response attacks:
    - UI average ASR: 45.69%.
    - FE average ASR: 39.21%.
  - RI average ASR: 20.00%; PI average ASR: 20.21%.
  - Mixed attacks often amplify components; PI-UI average ASR: 56.07%, PI-FE: 52.86%, TT-OP: 53.75%.
  - Defense:
    - MCIP reduces average ASR from 40.35% to 28.69%.
    - PUA drops from 56.50% to 48.91%.
    - NRP rises only from 33.70% to 34.88%.
- Human evaluation, if any:
  - Not a central human-evaluation paper. Tool construction and examples are described, but primary evaluation is automated through environment/log checks.
- Artifact quality concerns:
  - Response attacks often replace outputs with blatant instruction-bearing strings.
  - Some attack tools have no normal functionality in UI/FE, which affects PUA interpretation.
  - NRP can obscure whether failures are malicious acceptance or benign task failure; report ASR and PUA separately if reused.

### 6. Relevance to tool-output spoofing

Answer each item explicitly.

- Does the decisive attacker-controlled object arrive as a tool result?
  - **Yes for UI, FE, TT, and RI.** The paper explicitly models malicious `tau_r` / tool response content entering the observation sequence.
  - **No for all attacks.** Planning and invocation attacks operate through names/descriptions/parameters.
- Is the harmful content an instruction, a semantic falsehood, bad metadata, bad tool code, poisoned retrieved knowledge, or model hallucination?
  - Mostly **instruction-bearing tool responses** and bad metadata.
  - UI: response impersonates the user and inserts a new malicious task.
  - FE: fabricated error message plus malicious instruction. This is a semantic lie about error state, but the harmful mechanism is instruction-following.
  - TT: response claims a tool has been replaced and routes the agent to another tool.
  - RI: poisoned retrieved knowledge contains malicious instructions.
  - OP: parameter surface causes leakage through an out-of-scope parameter.
- Is the user task benign in the main attack?
  - **Yes.** User tasks are ordinary tasks; attack objectives are introduced through malicious MCP artifacts.
- Does the paper compare truthful vs spoofed observations?
  - **No, not in our strict sense.** It mutates benign tools into attack tools and evaluates adversarial environments, but it does not provide paired traces where only the visible tool observation is truthful vs spoofed against a fixed truth state.
- Does it define a ground-truth oracle?
  - **Partial.** It checks environment state and tool invocation logs for attack/user-task success. It does not define a truth oracle for tool-result veracity.
- Does it evaluate false-state propagation into later reasoning/actions?
  - **Partial.** FE/TT/UI show response strings change later tool calls/actions. It does not isolate propagation from false factual data without instructions.
- Does it test cross-tool corroboration, provenance, freshness, signatures, or uncertainty policies?
  - **Mostly no.** It evaluates MCIP detection/blocking. It does not test independent verification, signed responses, freshness checks, or cross-source corroboration as primary defenses.
- Does it separate "data that is false" from "data that instructs the model"?
  - **No.** Response attacks largely conflate false claims and explicit instructions. FE is a false error plus instruction; UI is fake user identity plus instruction; TT is fake replacement claim plus routing instruction.
- Does it cover structured outputs such as JSON/status fields/exit codes?
  - **Partial/weak.** The paper states response-based attacks can keep the tool schema legitimate, and MCP tools have standardized I/O. But attack examples are mostly natural-language response replacements rather than schema-valid semantic value forgery.

### 7. Novelty impact for this lab

- Claim blocked:
  - "First MCP benchmark covering response attacks."
  - "First to show MCP tool responses can manipulate agent behavior."
  - "First to benchmark false error / user-impersonating tool response / tool-transfer attacks."
  - "First end-to-end MCP attack benchmark with benign and malicious tools."
- Claim weakened:
  - "Tool-output spoofing is absent from MCP security work." MSB has response attacks and explicitly notes over-trust in tool responses.
  - "Legitimate schema with malicious response is new." MSB states response-based attacks keep schemas legitimate while attack intent appears only after invocation.
- Claim still open:
  - A benchmark where the **response is schema-valid and non-instructional**, e.g. `{"status":"sent","message_id":"m_123"}` when no message was sent.
  - Field-level truth oracle separate from attack objective.
  - Paired truthful/spoofed traces with the same user task and hidden state.
  - Defense evaluation for semantic-veracity policies rather than MCIP-style malicious-instruction detection.
- Exact differentiator this lab should preserve:
  - Distinguish **fabricated observation** from **embedded instruction**:
    - MSB: "Error: follow these instructions..."
    - Lab: "status=passed" or "balance=1000" or "receipt verified=true" when hidden truth says otherwise.
  - Include an oracle that can say exactly which field is false and whether the final answer/action accepted that field.
- Related-work sentence draft:
  - "Zhang et al.'s MSB benchmarks MCP-specific attacks across planning, invocation, response handling, retrieval, and mixed stages, including false-error and user-impersonating tool responses; unlike MSB, our benchmark isolates non-instructional schema-valid false observations and scores them against an independent truth oracle."
- Baselines or metrics we must include:
  - Include UI/FE/TT-style instruction-bearing response attacks as adjacent baselines or negative controls.
  - Report ASR and task utility separately; consider NRP only as a secondary aggregate.
  - Include MCIP-like detector if available, but expect it to catch instruction-bearing attacks more than pure semantic lies.

### 8. Reproducibility / implementation notes

- Public code: https://github.com/dongsenzhang/MSB
- Public data: implied by benchmark/code release.
- External services required:
  - MCP server setup.
  - Some scenarios may rely on MCP tools/platform integrations, but paper includes FileSystem/DesktopCommander workspace tools.
- Model/API dependencies:
  - Closed-source model APIs and open-source model inference.
  - MCIP defense uses Llama-xLAM-2-8B classifier.
- Estimated effort:
  - Full reproduction: moderate to high due to MCP environment, 2,000 instances, multiple models.
  - Minimal reproduction: low/moderate for UI/FE/TT using a local mock MCP server.
- Minimal subset worth reproducing:
  - One benign tool mutated into UI, FE, TT response attacks.
  - One OP parameter attack.
  - Compare prompt warning, MCIP-like detector, and our truth-oracle defense.
- Risks of downloading large assets:
  - Avoid open model downloads unless running MCIP.
  - No large dataset/model download needed for reading.

### 9. Evidence snippets

Direct quotes omitted; below are paraphrased evidence anchors.

- Key definition:
  - Section 4.3 defines tool response attacks as malicious instructions embedded in a tool response that is added to the observation sequence.
- Key table/metric:
  - Table 1 lists UI, FE, TT, and RI as response-stage attacks.
  - Section 5.2 defines ASR, PUA, and NRP.
- Key result:
  - Table 3 reports average ASR 40.35%, OP 76.50%, UI 45.69%, FE 39.21%.
  - Table 4 reports MCIP lowering ASR but also lowering PUA, with only small NRP improvement.
- Key limitation for our novelty:
  - Appendix examples show response attacks as instruction-bearing response replacements, not pure false structured values.
- Citation to use:
  - Use as the primary related work for MCP response-handling attacks and false-error/user-impersonation baselines.

### 10. Matrix update checklist

- [ ] Add/update row in `docs/literature-matrix.md`.
- [ ] Add BibTeX to the local bibliography once the final citation format is chosen.
- [ ] Add overlap/gap notes.
- [ ] Add must-run baseline: UI/FE/TT response-instruction attacks vs pure semantic spoofing.
- [ ] Add defense idea: MCIP-style detection may over-reject; measure utility loss.
- [ ] Mark this paper as **blocking broad MCP response attack novelty**, but leaving non-instructional schema-valid false-observation gap open.

---

## 3. `zong2025mcpsafetybench` -- MCP-SafetyBench

### 0. Triage label

- Priority: **P0**
- Relation to this lab: **Direct/adjacent**. Direct for MCP data tampering, function return injection, parameter poisoning, identity spoofing, replay, and real MCP server safety evaluation; partial for strict tool-output spoofing because false-observation veracity is not isolated as the primary variable.
- Reading status: **deep-read**
- Assigned reader: deep-read subagent A
- Date: 2026-06-08

### 1. Metadata

- BibTeX key: `zong2025mcpsafetybench`
- Title: *MCP-SafetyBench: A Benchmark for Safety Evaluation of Large Language Models with Real-World MCP Servers*
- Authors: Xuanjun Zong, Zhiqi Shen, Lei Wang, Yunshi Lan, Chao Yang
- Venue / year: ICLR 2026 conference paper; arXiv version dated 2026
- Paper link: https://arxiv.org/abs/2512.15163
- PDF path: `/root/tool-output-spoofing-lab/papers/benchmarks/mcp-safetybench.pdf`
- Text path: no repository text found; read via temporary extraction at `/tmp/mcp-safetybench.txt`
- Code / data / benchmark link: https://github.com/xjzzzzzzzz/MCPSafety
- Version read: arXiv:2512.15163v2, dated 2026-03-05
- Notes on artifact availability: paper says benchmark is available on GitHub; no artifacts were downloaded. `pdftotext` was used only for temporary local extraction.

#### BibTeX seed template

```bibtex
@misc{zong2025mcpsafetybench,
  title = {MCP-SafetyBench: A Benchmark for Safety Evaluation of Large Language Models with Real-World MCP Servers},
  author = {Zong, Xuanjun and Shen, Zhiqi and Wang, Lei and Lan, Yunshi and Yang, Chao},
  year = {2025},
  eprint = {2512.15163},
  archivePrefix = {arXiv},
  url = {https://arxiv.org/abs/2512.15163}
}
```

If using venue format later, update to the official ICLR 2026 entry.

### 2. One-sentence summary

MCP-SafetyBench builds a real-MCP-server, multi-step benchmark with 20 attack types across MCP server, host, and user sides, and finds that leading LLM agents remain vulnerable with a strong safety-utility trade-off.

### 3. Threat model / problem setting

- Attacker capability:
  - Varies by side:
    - MCP server side: attacker tampers with tool descriptions, manifests, implementations, returns, versions, dependencies, or tool overlap.
    - MCP host side: attacker modifies planning/message-routing logic or intermediate messages.
    - User side: attacker supplies malicious prompts/files/external data.
  - Attack may be stealthy or disruptive.
- User prompt: mixed:
  - Baseline tasks are benign.
  - Attack modifications may be injected at server, host, or user layer.
- Agent architecture:
  - ReAct-style LLM agent in a multi-step MCP environment.
  - Agent uses real MCP servers and logs full execution traces.
- Tooling setup:
  - Built on MCP-Universe.
  - Five domains:
    - financial analysis,
    - location navigation,
    - repository management,
    - browser automation,
    - web search.
  - Real-world MCP servers and multi-server coordination.
- Where untrusted data enters:
  - tool metadata/manifests,
  - tool descriptions/schema hints,
  - **tool return values**,
  - host intermediate messages,
  - identity metadata,
  - replayed interactions,
  - user prompts/files/external data.
- Defender visibility:
  - Benchmark logs full execution trace.
  - Evaluators score task success and attack success after execution.
  - The only mitigation tested in main paper is a safety prompt prepended to user requests.
- Security or reliability property:
  - Complete the user goal and prevent the attack goal.
  - Outcomes are dual-labeled as task pass/fail and attack success/failure.

### 4. Mechanism

- Attack, failure, benchmark, or defense:
  - Benchmark taxonomy and evaluation suite, not a full defense paper.
  - Safety-prompt mitigation is tested as a lightweight baseline.
- Key algorithm or construction:
  - Select tasks from MCP-Universe and preserve goal, context, available tools, and output schema.
  - Pair each baseline task with exactly one MCP-layer attack modification.
  - Package each case with category, user query, output schema, attack metadata, and associated evaluators.
  - Execute under standardized MCP pipeline, log trace, and run task/attack evaluators.
- Attack taxonomy:
  - MCP server-side:
    - Tool Poisoning: parameter, command, filesystem, redirection, network request, function dependency.
    - Function Overlapping.
    - Preference Manipulation.
    - Tool Shadowing.
    - Function Return Injection.
    - Rug Pull Attack.
  - MCP host-side:
    - Intent Injection.
    - Data Tampering.
    - Identity Spoofing.
    - Replay Injection.
  - User-side:
    - Malicious Code Execution.
    - Credential Theft.
    - Remote Access Control.
    - Retrieval-Agent Deception.
    - Excessive Privileges Misuse.
- Assumptions required:
  - MCP server/host/user layers can be instrumented to inject attacks.
  - Task and attack success can be checked deterministically through evaluators.
  - Realistic tasks can be adapted from MCP-Universe while preserving useful semantics.
- Why it works:
  - MCP agents rely on third-party server metadata and outputs.
  - Multi-step/multi-server workflows enlarge the attack window and introduce state/routing ambiguity.
  - Host-side coordination and identity/message handling are especially brittle.
- What it does not cover:
  - Does not isolate schema-valid false tool output as the central benchmark axis.
  - Does not provide paired truthful/spoofed observations for every case.
  - Safety prompt is too weak to be a serious defense baseline for semantic veracity.
  - Some tasks have low TSR under attack, making attack success and task difficulty interact.

### 5. Evaluation extraction

- Models evaluated:
  - Proprietary: GPT-5, GPT-4.1, GPT-4o, o4-mini, Claude-4.0-Sonnet, Claude-3.7-Sonnet, Gemini-2.5-Pro, Gemini-2.5-Flash, Grok-4.
  - Open-source/open-weight APIs: GLM-4.5, Kimi-K2, Qwen3-235B, DeepSeek-V3.1.
- Tasks / domains:
  - 245 test examples over five domains:
    - Financial Analysis: 53
    - Location Navigation: 53
    - Repository Management: 56
    - Browser Automation: 30
    - Web Search: 53
- Number of tools:
  - Real MCP servers from MCP-Universe; paper emphasizes real-world server integration but does not summarize a single total tool count in the extracted main table.
- Number of test cases:
  - 245 distinct test examples.
  - 3 repetitions per task in the evaluation configuration.
- Attack variants:
  - 20 attack types.
  - Attack strategy distribution:
    - Disruption: 46.53%.
    - Stealth: 53.47%.
  - Attack source distribution:
    - MCP server: 74.69%.
    - MCP host: 12.24%.
    - User: 13.06%.
- Defense variants:
  - Baseline ReAct agent.
  - Safety-prompt mitigation only.
- Metrics:
  - TSR: task success rate.
  - ASR: attack success rate.
  - DSR is discussed as `1 - ASR`.
  - Dual-label evaluation: `success(G)` and `attack_success(A)`.
- Decisive quantitative results:
  - Overall ASR across models ranges from 29.80% (Qwen3-235B) to 48.16% (o4-mini).
  - Negative safety-utility correlation: Pearson r = -0.572, p = 0.041 between TSR and DSR.
  - Financial Analysis is especially vulnerable: average ASR 46.59%.
  - Web Search is lower: average ASR 30.33%.
  - Host-side attacks average ASR 81.94%.
  - Identity Injection reaches 100% ASR across all 13 models.
  - Tool Redirection reaches 70.63% ASR.
  - Safety prompt reduces weighted ASR from 39.88% to 38.65%, not statistically significant.
  - Safety prompt helps some explicit high-risk attacks but can worsen Preference Manipulation and Function Overlapping.
- Human evaluation, if any:
  - Attack examples are generated through template + Cursor synthesis + human review for plausibility and feasibility.
  - Main scoring is automated by task/attack evaluators.
- Artifact quality concerns:
  - Only 245 cases; good realism but smaller than MSB.
  - Benchmark is broad; each individual attack type may have few examples.
  - Low TSR under attack makes model comparisons sensitive to refusal/failure modes.
  - Safety prompt is a weak mitigation; the paper is stronger as benchmark/taxonomy than as defense evaluation.

### 6. Relevance to tool-output spoofing

Answer each item explicitly.

- Does the decisive attacker-controlled object arrive as a tool result?
  - **Yes for Function Return Injection and Data Tampering.**
  - **Partial for Parameter Poisoning / Tool Redirection / Rug Pull.** Some attacks alter manifest/schema/tool behavior so the resulting call or returned result becomes wrong.
  - **No for all attacks**, since many are metadata, host, or user input attacks.
- Is the harmful content an instruction, a semantic falsehood, bad metadata, bad tool code, poisoned retrieved knowledge, or model hallucination?
  - Broad mix:
    - Function Return Injection: unsafe instructions embedded in tool return payload.
    - Data Tampering: tool outputs/intermediate messages are modified, causing falsified results or incorrect actions.
    - Parameter Poisoning: defaults/schema hints silently produce incorrect results.
    - Identity Spoofing: forged identity metadata.
    - Replay Injection: stale but previously valid interaction reused.
    - Retrieval-Agent Deception: poisoned public data sources.
    - Tool Poisoning/Shadowing/Rug Pull: bad metadata or changed server behavior.
- Is the user task benign in the main attack?
  - **Mostly yes for server/host-side attacks.** The task is a normal MCP-Universe task paired with an attack modification.
  - User-side attacks may include malicious user-controlled inputs.
- Does the paper compare truthful vs spoofed observations?
  - **No/partial.** Each baseline task is paired with one attack modification, but the benchmark is not organized as paired truthful/spoofed visible traces for the same hidden truth state.
- Does it define a ground-truth oracle?
  - **Partial.** It has deterministic task and attack evaluators and machine-checkable output schema.
  - It does not define a per-field oracle for whether each tool-returned fact is true.
- Does it evaluate false-state propagation into later reasoning/actions?
  - **Partial.** Data Tampering, Replay Injection, Identity Spoofing, and Parameter Poisoning can cause downstream wrong actions.
  - However, the benchmark reports attack success, not a dedicated false-state propagation metric.
- Does it test cross-tool corroboration, provenance, freshness, signatures, or uncertainty policies?
  - **Mostly no.** Multi-server coordination exists, but defense evaluation does not focus on provenance, signatures, freshness, or independent corroboration.
- Does it separate "data that is false" from "data that instructs the model"?
  - **Partially.** Data Tampering is explicitly about falsified outputs/intermediate messages, and Parameter Poisoning can silently produce incorrect results.
  - Function Return Injection and many tool-poisoning variants remain instruction/metadata attacks.
- Does it cover structured outputs such as JSON/status fields/exit codes?
  - **Partial.** Tasks include output schemas and deterministic evaluators; MCP tools/manifests are structured.
  - The paper does not foreground schema-valid false JSON/status/exit-code observations as a separate class.

### 7. Novelty impact for this lab

- Claim blocked:
  - "First comprehensive MCP safety benchmark with real MCP servers."
  - "First benchmark covering data tampering or function return injection in MCP."
  - "First multi-step/multi-server MCP attack taxonomy across server, host, and user sides."
  - "First to evaluate MCP agents with task and attack evaluators."
- Claim weakened:
  - "Schema hints or parameter poisoning causing incorrect results are unstudied."
  - "Host-side output/message tampering is not covered in existing MCP safety work."
  - "Replay/identity spoofing around MCP observations is unstudied."
- Claim still open:
  - Fine-grained, local, deterministic benchmark for **schema-valid non-instructional false observations** with a hidden truth plane.
  - Explicit truthful/spoofed trace pairs and a diff of visible vs oracle state.
  - Quantitative metrics for:
    - false claim acceptance,
    - false-state propagation,
    - independent verification rate,
    - provenance/freshness handling,
    - over-trust in one compromised result channel.
  - Cross-surface comparison beyond MCP: shell, browser, REST, RAG/search, filesystem/logs.
- Exact differentiator this lab should preserve:
  - Use MCP-SafetyBench's taxonomy as coverage pressure, but narrow the lab to **veracity of observations** rather than "any MCP attack."
  - Treat Data Tampering, Parameter Poisoning, Identity Spoofing, Replay Injection, and Function Return Injection as adjacent baselines; then show what changes when the attack contains no malicious instruction and passes schema validation.
- Related-work sentence draft:
  - "MCP-SafetyBench evaluates 20 MCP attack types on real MCP servers, including function return injection and host-side data tampering; our work narrows this broad taxonomy to schema-valid semantic observation forgery and evaluates paired truthful/spoofed traces against a field-level truth oracle."
- Baselines or metrics we must include:
  - Include Data Tampering and Parameter Poisoning examples as direct prior-overlap baselines.
  - Report TSR/ASR or utility/attack separately, but add oracle-inconsistency and false-observation acceptance.
  - Include safety prompt as a weak baseline, expecting little effect on non-instructional semantic lies.

### 8. Reproducibility / implementation notes

- Public code: https://github.com/xjzzzzzzzz/MCPSafety
- Public data: benchmark repository listed in paper.
- External services required:
  - Real MCP server setup from MCP-Universe; possible domain-specific dependencies.
- Model/API dependencies:
  - Closed-source APIs and open-source model endpoints/weights depending on reproduction scope.
- Estimated effort:
  - Full reproduction: high because it uses real MCP servers, multi-step agents, 13 models, and repeated runs.
  - Minimal reproduction: moderate; implement a few local MCP tasks with task/attack evaluators.
- Minimal subset worth reproducing:
  - One Data Tampering case with falsified financial API response.
  - One Parameter Poisoning case where a ticker/default silently changes.
  - One Replay Injection case using stale but valid-looking result.
  - Safety prompt baseline to show weakness against semantic lies.
- Risks of downloading large assets:
  - Avoid downloading any model weights for this literature step.
  - If later reproducing, prefer local mock MCP servers over full real-server setup first.

### 9. Evidence snippets

Direct quotes omitted; below are paraphrased evidence anchors.

- Key definition:
  - Section 3.2 and Appendix A define 20 attacks across MCP server, host, and user sides.
  - Appendix A defines Data Tampering as modified tool outputs/intermediate messages that lead the host to accept falsified results or take incorrect actions.
- Key table/metric:
  - Table 2 compares attack-type coverage across MCP safety benchmarks.
  - Section 3.5 defines deterministic task/attack evaluators over execution traces.
- Key result:
  - Table 4 reports overall ASR for 13 models; Qwen3-235B has the lowest overall ASR at 29.80%, o4-mini the highest at 48.16%.
  - Appendix/Table 10 gives per-attack-type ASR; Identity Injection is 100% across models.
- Key limitation for our novelty:
  - The benchmark is broad and realistic but does not isolate non-instructional schema-valid false tool observations as the main variable.
- Citation to use:
  - Use as the primary related work for broad real-MCP-server safety evaluation and for Data Tampering / Function Return Injection overlap.

### 10. Matrix update checklist

- [ ] Add/update row in `docs/literature-matrix.md`.
- [ ] Add BibTeX to the local bibliography once the final citation format is chosen.
- [ ] Add overlap/gap notes.
- [ ] Add must-run baseline: MCP Data Tampering / Parameter Poisoning / Replay Injection variants.
- [ ] Add defense idea: safety prompt is insufficient; test provenance/corroboration instead.
- [ ] Mark this paper as **blocking broad MCP safety benchmark novelty**, but leaving paired truth-oracle schema-valid spoofing open.

