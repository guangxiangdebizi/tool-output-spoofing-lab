# Tool-output spoofing / malicious tool-result manipulation: top security/NLP literature audit

检索日期：2026-06-08（Asia/Shanghai）。范围限定为原始论文、官方会议/期刊页面、ACL Anthology、OpenReview、USENIX/NDSS/NeurIPS proceedings、arXiv 原文。未运行重实验；仅做公开 PDF 下载与摘要级精读初筛。

## 0. Executive conclusion

**Verdict: Weak Go**，但只能在明显收窄后做。

宽泛命题“工具输出是不可信观测；恶意/被攻陷工具返回伪造结果会诱导 LLM agent 错误计划、错误报告、越权动作或错误安全判断”已经被多条近邻工作覆盖：

- **最接近已有工作**：**Trust No Tool: Evaluating and Defending LLM Agents under Untrusted Tool Feedback**。它直接把“工具反馈不可信”作为核心问题，提出 hidden-trigger tool-compromise / cognitive poisoning benchmark 和 trajectory-aware defense。
- **最接近 MCP/工具返回值方向**：**Invisible Threats from MCP / TIP**、**MCP Security Bench (MSB)**、**MCP-SafetyBench**。它们明确覆盖 MCP tool response / function return injection / data tampering / user-impersonating response / false-error escalation。
- **最接近 supply-chain/intermediary 篡改方向**：**Your Agent Is Mine**。它研究 LLM API router 可读写/伪造 in-flight JSON、tool-call arguments、model outputs 等。
- **经典基础线**：**AgentDojo**、**InjecAgent**、**ASB** 已把工具返回的外部数据/observation 作为 indirect prompt injection 入口。

因此需要避免的 novelty claim：

1. “首次指出 tool outputs / observations 是不可信输入。”
2. “首次研究恶意或被攻陷工具返回内容误导 LLM agent。”
3. “首次构建 MCP tool-response / function-return attack benchmark。”
4. “首次提出基于控制流/数据流隔离或 provenance 的 prompt-injection 防御。”

仍可能成立的 narrowed claim：

- 聚焦**非指令型 semantic spoofing / mock scam**：工具返回“格式正确、无 prompt-injection 指令、但事实或安全结论伪造”的数据，例如 fake scanner says safe、fake unit tests pass、fake price/medical/security API result、fake compliance evidence。
- 聚焦**工具观测真伪验证**而不是 prompt injection 过滤：cross-tool consistency、signed/verifiable tool results、replayable evidence、provenance/attestation、uncertainty-aware final action gating。
- 聚焦某一高价值垂直场景：安全扫描/CI/CD/医疗检索/财务交易，证明现有 AgentDojo/MSB/MCP-SafetyBench 类型 benchmark 没有细粒度覆盖“无恶意文本指令的伪造观测”。

## 1. Downloaded PDFs

已下载到 `/root/tool-output-spoofing-lab/papers/topsec-nlp/`。

| # | Local PDF | Venue/year | Paper/source | PDF link |
|---|---|---:|---|---|
| 1 | `2026_trust_no_tool.pdf` | arXiv 2026 | [Trust No Tool: Evaluating and Defending LLM Agents under Untrusted Tool Feedback](https://arxiv.org/abs/2605.17453) | [PDF](https://arxiv.org/pdf/2605.17453) |
| 2 | `2026_tip_mcp_response_injection.pdf` | arXiv 2026 | [Invisible Threats from Model Context Protocol: Generating Stealthy Injection Payload via Tree-based Adaptive Search](https://arxiv.org/abs/2603.24203) | [PDF](https://arxiv.org/pdf/2603.24203) |
| 3 | `2026_mcp_security_bench.pdf` | ICLR 2026 poster | [MCP Security Bench (MSB): Benchmarking Attacks Against Model Context Protocol in LLM Agents](https://openreview.net/forum?id=irxxkFMrry) | [PDF](https://openreview.net/pdf?id=irxxkFMrry) |
| 4 | `2026_mcp_safetybench.pdf` | ICLR 2026 poster | [MCP-SafetyBench: A Benchmark for Safety Evaluation of Large Language Models with Real-World MCP Servers](https://openreview.net/forum?id=7XYjeL46co) | [PDF](https://openreview.net/pdf?id=7XYjeL46co) |
| 5 | `2026_your_agent_is_mine.pdf` | arXiv 2026 | [Your Agent Is Mine: Measuring Malicious Intermediary Attacks on the LLM Supply Chain](https://arxiv.org/abs/2604.08407) | [PDF](https://arxiv.org/pdf/2604.08407) |
| 6 | `2026_maltool.pdf` | arXiv 2026 | [MalTool: Malicious Tool Attacks on LLM Agents](https://arxiv.org/abs/2602.12194) | [PDF](https://arxiv.org/pdf/2602.12194) |
| 7 | `2026_toolhijacker.pdf` | NDSS 2026 | [Prompt Injection Attack to Tool Selection in LLM Agents](https://www.ndss-symposium.org/ndss-paper/prompt-injection-attack-to-tool-selection-in-llm-agents/) | [PDF](https://www.ndss-symposium.org/wp-content/uploads/2026-s675-paper.pdf) |
| 8 | `2025_attractive_metadata_attack.pdf` | NeurIPS 2025 poster | [Attractive Metadata Attack: Inducing LLM Agents to Invoke Malicious Tools](https://openreview.net/forum?id=oLGtPYdRzU) | [PDF](https://openreview.net/pdf?id=oLGtPYdRzU) |
| 9 | `2025_toolcommander.pdf` | NAACL 2025 long | [From Allies to Adversaries: Manipulating LLM Tool-Calling through Adversarial Injection](https://aclanthology.org/2025.naacl-long.101/) | [PDF](https://aclanthology.org/2025.naacl-long.101.pdf) |
| 10 | `2025_agent_security_bench.pdf` | ICLR 2025 | [Agent Security Bench (ASB): Formalizing and Benchmarking Attacks and Defenses in LLM-based Agents](https://openreview.net/forum?id=V4y0CpX4hK) | [PDF](https://openreview.net/pdf?id=V4y0CpX4hK) |
| 11 | `2024_agentdojo.pdf` | NeurIPS 2024 Datasets & Benchmarks | [AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents](https://proceedings.neurips.cc/paper_files/paper/2024/hash/97091a5177d8dc64b1da8bf3e1f6fb54-Abstract-Datasets_and_Benchmarks_Track.html) | [PDF](https://proceedings.neurips.cc/paper_files/paper/2024/file/97091a5177d8dc64b1da8bf3e1f6fb54-Paper-Datasets_and_Benchmarks_Track.pdf) |
| 12 | `2024_injecagent.pdf` | Findings of ACL 2024 | [InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated Large Language Model Agents](https://aclanthology.org/2024.findings-acl.624/) | [PDF](https://aclanthology.org/2024.findings-acl.624.pdf) |
| 13 | `2023_not_what_signed_up_for.pdf` | ACM AISec 2023 / CCS workshop | [Not What You’ve Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection](https://dl.acm.org/doi/10.1145/3605764.3623985) | [PDF](https://arxiv.org/pdf/2302.12173) |
| 14 | `2025_poisonedrag.pdf` | USENIX Security 2025 | [PoisonedRAG: Knowledge Corruption Attacks to Retrieval-Augmented Generation of Large Language Models](https://www.usenix.org/conference/usenixsecurity25/presentation/zou-poisonedrag) | [PDF](https://www.usenix.org/system/files/usenixsecurity25-zou-poisonedrag.pdf) |
| 15 | `2025_camel.pdf` | arXiv 2025 | [Defeating Prompt Injections by Design](https://arxiv.org/abs/2503.18813) | [PDF](https://arxiv.org/pdf/2503.18813) |

## 2. Per-paper audit

### 1) Trust No Tool: Evaluating and Defending LLM Agents under Untrusted Tool Feedback

- **Venue/year/link/PDF**: arXiv 2026; [abs](https://arxiv.org/abs/2605.17453); [PDF](https://arxiv.org/pdf/2605.17453).
- **Core method**: Defines **cognitive poisoning**: a malicious tool behaves plausibly during exploration, accumulates trust through benign-looking feedback, then becomes harmful when hidden state conditions align with final executable action. Builds **TRUST-BENCH** with 1,970 hidden-trigger tool-compromise episodes and matched controls; proposes **GUARDED JOINT** metric and **VISTA-GUARD**, a trajectory-aware final-action risk scorer.
- **Covers tool-output spoofing?** **Very high / closest.** This is explicitly about untrusted tool feedback, not just direct user prompt injection. It treats the tool response trajectory as a potentially deceptive observation source.
- **Blocks novelty claim**: Blocks “first study of LLM agents under untrusted/malicious tool feedback,” “first hidden-trigger compromised-tool benchmark,” and “first trajectory-level defense for trust built from tool feedback.”
- **Remaining work**: More room if the new work targets **non-instructional factual mock results** with real external verifiability, e.g. fake security scanner outputs, fake CI logs, fake API measurements, signed result provenance, or cross-tool consistency checks. The paper is broad and benchmark/defense oriented, but not a full solution for result authenticity.

### 2) Invisible Threats from Model Context Protocol: Generating Stealthy Injection Payload via Tree-based Adaptive Search

- **Venue/year/link/PDF**: arXiv 2026; [abs](https://arxiv.org/abs/2603.24203); [PDF](https://arxiv.org/pdf/2603.24203).
- **Core method**: Studies compromised third-party MCP servers that embed semantically coherent prompt-injection payloads inside legitimate-looking tool response fields. Proposes **TIP**: tree-structured black-box search over payloads, with coarse-to-fine optimization, path-aware feedback, and defense-aware exploration.
- **Covers tool-output spoofing?** **High.** The attack surface is specifically **malicious manipulation of tool responses** in MCP. The manipulated response is treated as trusted context by the agent.
- **Blocks novelty claim**: Blocks “MCP tool response manipulation is underexplored/novel” and “compromised MCP server returns malicious response to control an agent.”
- **Remaining work**: TIP is still mostly **prompt-injection payload optimization**. It leaves space for attacks/defenses where the returned data contains no explicit instruction but is semantically false or provenance-forged.

### 3) MCP Security Bench (MSB): Benchmarking Attacks Against Model Context Protocol in LLM Agents

- **Venue/year/link/PDF**: ICLR 2026 poster; [OpenReview](https://openreview.net/forum?id=irxxkFMrry); [PDF](https://openreview.net/pdf?id=irxxkFMrry).
- **Core method**: End-to-end MCP security benchmark across task planning, tool invocation, and response handling. Taxonomy includes name collision, preference manipulation, prompt injection in tool descriptions, out-of-scope parameters, **user-impersonating responses**, **false-error escalation**, **tool-transfer**, retrieval injection, and mixed attacks. Uses real MCP tools rather than pure simulation and introduces Net Resilient Performance.
- **Covers tool-output spoofing?** **Very high.** It has a dedicated **Tool Response Attack** stage, including fabricated error messages and user-impersonating responses.
- **Blocks novelty claim**: Blocks “first MCP benchmark covering tool responses/return handling” and “first taxonomy of tool response attacks in MCP agents.”
- **Remaining work**: Its response attacks are mostly instruction-bearing response manipulations. A deeper benchmark for **truthfulness/integrity of returned facts** and evidence-level replay/verification could still differentiate.

### 4) MCP-SafetyBench: A Benchmark for Safety Evaluation of Large Language Models with Real-World MCP Servers

- **Venue/year/link/PDF**: ICLR 2026 poster; [OpenReview](https://openreview.net/forum?id=7XYjeL46co); [PDF](https://openreview.net/pdf?id=7XYjeL46co).
- **Core method**: Real-world MCP-server benchmark with multi-turn tasks across browser automation, financial analysis, location navigation, repository management, and web search. Defines 20 attack types across server/host/user sides.
- **Covers tool-output spoofing?** **High.** Explicitly includes **Function Return Injection** (“unsafe instructions in tool return values”) and **Data Tampering** (“modify tool outputs or intermediate messages”), with examples like falsified financial API results.
- **Blocks novelty claim**: Blocks “first real MCP benchmark with function-return injection/data tampering” and “first cross-domain MCP safety benchmark involving modified tool outputs.”
- **Remaining work**: It is broad safety benchmarking, not a focused treatment of mock/fabricated tool data as an epistemic problem. There is room for specialized metrics and defenses for factual observation authenticity.

### 5) Your Agent Is Mine: Measuring Malicious Intermediary Attacks on the LLM Supply Chain

- **Venue/year/link/PDF**: arXiv 2026; [abs](https://arxiv.org/abs/2604.08407); [PDF](https://arxiv.org/pdf/2604.08407).
- **Core method**: Studies malicious LLM API routers/intermediaries with plaintext access to in-flight JSON payloads. Formalizes payload injection and secret exfiltration; measures paid/free routers; implements **Mine**, a proxy for attacks against public agent frameworks; evaluates client-side defenses.
- **Covers tool-output spoofing?** **High, via intermediary rather than tool server.** The router can read, rewrite, or fabricate tool-call payloads, arguments, and returned model/tool-call outputs before the client executes or observes them.
- **Blocks novelty claim**: Blocks “malicious intermediary can fabricate/tamper tool-call outputs in LLM agents” and “tool-call JSON lacks end-to-end integrity.”
- **Remaining work**: Less about a malicious tool endpoint returning fake observations; more about router-in-the-middle. A tool-result authenticity framework can still distinguish itself if it handles endpoint provenance and observation validation.

### 6) MalTool: Malicious Tool Attacks on LLM Agents

- **Venue/year/link/PDF**: arXiv 2026; [abs](https://arxiv.org/abs/2602.12194); [PDF](https://arxiv.org/pdf/2602.12194).
- **Core method**: Systematic study of malicious tool **code implementations**. Builds a CIA-style taxonomy for malicious tool behaviors in LLM-agent settings; uses coding LLMs plus automated verifiers to synthesize standalone and Trojanized malicious tools; evaluates existing malware/program-analysis/MCP-tool detectors.
- **Covers tool-output spoofing?** **Medium-high.** It is about malicious tools as code, including integrity violations such as memory/database poisoning, file deletion, remote program download, credential abuse, and DoS. It is not centered on “fake returned result deceives the LLM,” but it covers malicious tool-side behavior.
- **Blocks novelty claim**: Blocks “first systematic study/dataset of malicious tool implementations in LLM agents.”
- **Remaining work**: Does not deeply model the LLM’s belief update from plausible-but-false observations. A semantic spoofing benchmark/defense could build on this rather than compete with it.

### 7) Prompt Injection Attack to Tool Selection in LLM Agents / ToolHijacker

- **Venue/year/link/PDF**: NDSS 2026; [official page](https://www.ndss-symposium.org/ndss-paper/prompt-injection-attack-to-tool-selection-in-llm-agents/); [PDF](https://www.ndss-symposium.org/wp-content/uploads/2026-s675-paper.pdf).
- **Core method**: **ToolHijacker** injects a malicious tool document into a tool library to manipulate two-stage retrieval/selection and force selection of an attacker-chosen tool. It formulates tool-document crafting as an optimization problem and evaluates defenses.
- **Covers tool-output spoofing?** **Medium.** It targets tool selection, not return-value spoofing. However, it is part of the same malicious-tool pipeline: get the agent to invoke the attacker-controlled tool.
- **Blocks novelty claim**: Blocks “first prompt-injection attack on tool selection/retrieval for malicious tool invocation.”
- **Remaining work**: Once malicious tool execution is obtained, what false/forged outputs do to agent plans remains less central here.

### 8) Attractive Metadata Attack: Inducing LLM Agents to Invoke Malicious Tools

- **Venue/year/link/PDF**: NeurIPS 2025 poster; [OpenReview](https://openreview.net/forum?id=oLGtPYdRzU); [PDF](https://openreview.net/pdf?id=oLGtPYdRzU).
- **Core method**: Identifies tool metadata—names, descriptions, parameter schemas—as an attack surface. Proposes **AMA**, a black-box in-context learning framework to generate high-utility-looking metadata that makes agents prefer malicious tools without direct model access.
- **Covers tool-output spoofing?** **Medium.** Focus is pre-execution tool selection, not post-execution fabricated results.
- **Blocks novelty claim**: Blocks “malicious tools can be preferentially selected by metadata manipulation” and “tool metadata alone is a stealthy attack surface.”
- **Remaining work**: Tool-return integrity and fabricated observations are mostly downstream of the attack studied here.

### 9) From Allies to Adversaries: Manipulating LLM Tool-Calling through Adversarial Injection / ToolCommander

- **Venue/year/link/PDF**: NAACL 2025 long; [ACL Anthology](https://aclanthology.org/2025.naacl-long.101/); [PDF](https://aclanthology.org/2025.naacl-long.101.pdf).
- **Core method**: **ToolCommander** performs two-stage adversarial tool injection: first inject malicious tools to collect user queries, then dynamically updates tools based on stolen info to improve subsequent attacks. Demonstrates privacy theft, DoS, and unscheduled tool calling.
- **Covers tool-output spoofing?** **Medium.** It manipulates tool-calling/scheduling and uses tool responses in the attack flow, but does not primarily study fabricated result semantics.
- **Blocks novelty claim**: Blocks “malicious tool injection can manipulate tool scheduling and trigger privacy/DoS/unscheduled calls.”
- **Remaining work**: A mock-result / fabricated-observation benchmark would need to separate itself from scheduling attacks and focus on downstream reasoning correctness.

### 10) Agent Security Bench (ASB): Formalizing and Benchmarking Attacks and Defenses in LLM-based Agents

- **Venue/year/link/PDF**: ICLR 2025; [OpenReview](https://openreview.net/forum?id=V4y0CpX4hK); [PDF](https://openreview.net/pdf?id=V4y0CpX4hK).
- **Core method**: Comprehensive agent-security framework across 10 scenarios, 400+ tools, 27 attack/defense methods, and 7 metrics. Covers DPI, **IPI**, memory poisoning, Plan-of-Thought backdoor, mixed attacks, and defenses.
- **Covers tool-output spoofing?** **Medium-high.** ASB explicitly defines IPI as malicious instructions embedded in **tool responses/observations** and recognizes fabricated responses/hidden triggers as compromised data patterns.
- **Blocks novelty claim**: Blocks “first holistic agent-security benchmark including tool-response observations as an attack surface.”
- **Remaining work**: ASB is broad and largely prompt-injection oriented. It leaves room for fine-grained semantic falsification without injected instructions, especially with real tool execution/provenance.

### 11) AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents

- **Venue/year/link/PDF**: NeurIPS 2024 Datasets & Benchmarks; [proceedings](https://proceedings.neurips.cc/paper_files/paper/2024/hash/97091a5177d8dc64b1da8bf3e1f6fb54-Abstract-Datasets_and_Benchmarks_Track.html); [PDF](https://proceedings.neurips.cc/paper_files/paper/2024/file/97091a5177d8dc64b1da8bf3e1f6fb54-Paper-Datasets_and_Benchmarks_Track.pdf).
- **Core method**: Dynamic benchmark for agents executing tools over untrusted data. Provides 97 realistic tasks, 629 security test cases, and attack/defense paradigms. Tests whether data returned by external tools hijacks agents into malicious tasks.
- **Covers tool-output spoofing?** **High for untrusted tool outputs; lower for malicious tool endpoints.** It treats external tool-returned data as untrusted and adversarial, but the standard attack is indirect prompt injection in data, not a tool server lying about computed results.
- **Blocks novelty claim**: Blocks “first to benchmark LLM agents where external tool outputs are adversarial/untrusted.”
- **Remaining work**: Good baseline for any new work. To differentiate, evaluate cases where the tool output is syntactically/semantically normal and contains no instruction, but the claimed observation is false.

### 12) InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated Large Language Model Agents

- **Venue/year/link/PDF**: Findings of ACL 2024; [ACL Anthology](https://aclanthology.org/2024.findings-acl.624/); [PDF](https://aclanthology.org/2024.findings-acl.624.pdf).
- **Core method**: Benchmark for indirect prompt injection in tool-integrated agents. Includes 1,054 test cases, 17 user tools, 62 attacker tools, attack intentions such as direct harm and data exfiltration, and tool response templates with attacker-controlled content.
- **Covers tool-output spoofing?** **High for tool-response prompt injection.** The malicious content is embedded in tool response templates and returned as observations.
- **Blocks novelty claim**: Blocks “first benchmark for IPI in tool-integrated LLM agents using tool responses.”
- **Remaining work**: Does not focus on mock/fabricated result values without prompt-injection strings.

### 13) Not What You’ve Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection

- **Venue/year/link/PDF**: ACM AISec 2023 / CCS workshop; [ACM DOI](https://dl.acm.org/doi/10.1145/3605764.3623985); [PDF](https://arxiv.org/pdf/2302.12173).
- **Core method**: Seminal indirect prompt injection taxonomy for LLM-integrated apps. Shows remote attackers can place prompts in data later retrieved by LLM apps; studies data theft, worming, information ecosystem contamination, and real-world systems.
- **Covers tool-output spoofing?** **Medium.** It covers untrusted retrieved data/outputs influencing LLM-integrated applications, but predates the MCP/tool-server framing and does not focus on fabricated tool results as a separate trust boundary.
- **Blocks novelty claim**: Blocks broad “untrusted external data returned to LLM app can hijack behavior” framing.
- **Remaining work**: Active malicious tools, tool-result provenance, and non-instructional fake observations remain beyond its main focus.

### 14) PoisonedRAG: Knowledge Corruption Attacks to Retrieval-Augmented Generation of Large Language Models

- **Venue/year/link/PDF**: USENIX Security 2025; [official page](https://www.usenix.org/conference/usenixsecurity25/presentation/zou-poisonedrag); [PDF](https://www.usenix.org/system/files/usenixsecurity25-zou-poisonedrag.pdf).
- **Core method**: Knowledge corruption attack against RAG. Injects a small number of malicious texts into a large knowledge database to induce attacker-chosen target answers for target questions; formulates attack as optimization and evaluates defenses.
- **Covers tool-output spoofing?** **Medium-low / adjacent.** RAG retriever output is a tool-like observation, and the attack causes false answers from corrupted retrieved content. But the adversary poisons the knowledge base, not necessarily a live tool returning fabricated results.
- **Blocks novelty claim**: Blocks “retrieved external knowledge can be poisoned to make LLMs report false facts.”
- **Remaining work**: Live API/tool result fabrication, agentic action sequences, and runtime trust decisions are still distinct.

### 15) Defeating Prompt Injections by Design / CaMeL

- **Venue/year/link/PDF**: arXiv 2025; [abs](https://arxiv.org/abs/2503.18813); [PDF](https://arxiv.org/pdf/2503.18813).
- **Core method**: Defense architecture that separates trusted control/data flow from untrusted data. Extracts program/control structure from the trusted user query; untrusted retrieved/tool data cannot influence program flow; capability metadata tracks provenance and enforces security policies at tool calls.
- **Covers tool-output spoofing?** **Medium-high as defense.** It directly treats tool outputs/web content as untrusted data and prevents them from controlling actions or exfiltrating private data.
- **Blocks novelty claim**: Blocks “first control/data-flow or capability-based defense for prompt injection from untrusted tool outputs.”
- **Remaining work**: CaMeL enforces policy over flows; it does not prove the factual truth of an observation. A result-authenticity / semantic spoofing defense could complement it.

## 3. Synthesis by attack surface

| Attack surface | Existing coverage | Implication |
|---|---|---|
| External data returned by tools contains malicious instructions | Not What You’ve Signed Up For, AgentDojo, InjecAgent, ASB, CaMeL | Very mature; do not claim novelty here. |
| MCP tool response / function return injection | TIP, MSB, MCP-SafetyBench | Directly overlaps with “tool result manipulation.” |
| Tool output/intermediate message tampering | MCP-SafetyBench, MSB, Your Agent Is Mine | Directly blocks broad “fabricated tool output” novelty. |
| Malicious tool selection / metadata poisoning | ToolHijacker, Attractive Metadata Attack, ToolCommander | Covers how attacker-controlled tools get invoked. |
| Malicious tool code implementation | MalTool | Covers actual malicious code in tools, but less about agent belief in fake observations. |
| Knowledge/retrieval corruption | PoisonedRAG | Adjacent; strong baseline for false-report outcomes. |
| Defense via data/control isolation | CaMeL | Strong baseline defense; new defenses must go beyond prompt/data separation. |

## 4. Recommended narrowed research direction

If continuing, frame the work as:

> LLM agents need **observation integrity** for tool results, not only prompt-injection resistance. We study non-instructional, semantically plausible, schema-valid but false tool outputs that induce incorrect reports/actions/security judgments, and evaluate defenses that verify or cross-check the truth/provenance of observations.

Concrete differentiators:

1. **No explicit malicious instruction in returned text**: no “ignore previous instructions”; only false values/evidence.
2. **Replayable evidence contracts**: every decisive tool observation must be reproducible, signed, or cross-validated.
3. **Security-critical tools**: scanners, CI/test tools, dependency analyzers, IAM/cloud audit tools, medical/finance APIs.
4. **Metrics beyond attack success**: false acceptance of fabricated evidence, unnecessary action rate, failure to escalate uncertainty, cross-tool disagreement handling.
5. **Baselines**: AgentDojo, ASB, MSB, MCP-SafetyBench, CaMeL-style policy isolation, LLM-as-judge response filtering, simple majority/cross-tool verification.

Bottom line: **Weak Go** only if positioned as **semantic observation spoofing / evidence-integrity for tool outputs**. The broad “untrusted tool outputs can deceive agents” claim is already too close to Trust No Tool, TIP, MSB, MCP-SafetyBench, and AgentDojo/InjecAgent.
