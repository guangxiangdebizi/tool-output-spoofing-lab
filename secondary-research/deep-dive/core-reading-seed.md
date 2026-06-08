# Core Reading Seed

Date: 2026-06-08

Scope: seed the literature deep-read structure for the tool-output spoofing
lab. The core set below is intentionally limited to eight resources. One
near-core extra is listed as metadata only because it is useful for the
tool-selection boundary.

Downloaded core PDFs are under `papers/core/`.

## Recommended deep-reading order

1. `debenedetti2024agentdojo` - closest benchmark framing for agents consuming
   untrusted tool data.
2. `zhan2024injecagent` - strongest benchmark specifically for indirect prompt
   injection in tool-integrated agents.
3. `greshake2023indirect` - foundational taxonomy and real-world LLM-integrated
   application attack framing.
4. `ruan2023toolemu` - core agent/tool risk benchmark and evaluator design.
5. `zou2024poisonedrag` - retrieval poisoning baseline for fabricated evidence.
6. `hu2026maltool` - malicious tool/plugin code taxonomy and dataset framing.
7. `mo2025ama` - malicious tool metadata / selection-time attack surface.
8. `xu2024relytoolbench` - tool hallucination taxonomy and reliability metrics.

Optional after the core eight: `shi2025toolhijacker`, because it sits between
RAG/document poisoning and malicious tool selection.

## Core resource summaries

### P0 - AgentDojo

- BibTeX key: `debenedetti2024agentdojo`
- Title: AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks
  and Defenses for LLM Agents
- Link: https://arxiv.org/abs/2406.13352
- PDF: `papers/core/agentdojo-2024-prompt-injection-agent-benchmark.pdf`
- Why core: AgentDojo directly frames agents executing tools over untrusted
  data. It reports 97 realistic tasks and 629 security test cases, with both
  attacks and defenses.
- Relevance: closest benchmark baseline. The decisive overlap is the
  observation boundary where external tools return data that can hijack the
  agent.
- Novelty pressure: blocks broad claims about first dynamic security benchmark
  for prompt injection in LLM agents.
- Gap to preserve: our benchmark should isolate semantic false observations
  such as false success, forged provenance, stale replay, and metric tampering,
  including paired truthful/spoofed traces and an explicit truth oracle.
- Deep-read targets:
  - task/security-property definitions;
  - attack and defense taxonomy;
  - whether any cases are non-instructional false tool results;
  - metrics that can be reused or must be distinguished.

### P0 - InjecAgent

- BibTeX key: `zhan2024injecagent`
- Title: InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated
  Large Language Model Agents
- Link: https://arxiv.org/abs/2403.02691
- PDF: `papers/core/injecagent-2024-indirect-prompt-injection-tool-agents.pdf`
- Why core: benchmark dedicated to indirect prompt injection in tool-integrated
  agents. The paper reports 1,054 test cases, 17 user tools, 62 attacker tools,
  and 30 evaluated agents.
- Relevance: strong adjacent/direct evidence that benign user tasks plus
  attacker-controlled external content can cause harmful tool-mediated actions.
- Novelty pressure: blocks broad "first IPI benchmark for tool agents" claims.
- Gap to preserve: distinguish adversarial instructions from semantically false
  tool outputs. The lab should ask whether the agent accepts a false state even
  when no explicit instruction appears.
- Deep-read targets:
  - harm vs private-data exfiltration taxonomy;
  - agent prompting styles and ASR metrics;
  - data construction process;
  - defense or mitigation results, if any.

### P0 - Greshake et al. indirect prompt injection

- BibTeX key: `greshake2023indirect`
- Title: Not what you've signed up for: Compromising Real-World LLM-Integrated
  Applications with Indirect Prompt Injection
- Link: https://arxiv.org/abs/2302.12173
- PDF: `papers/core/greshake-2023-indirect-prompt-injection.pdf`
- Why core: foundational treatment of indirect prompt injection against
  LLM-integrated applications, including external data that changes application
  behavior and API/tool calls.
- Relevance: sets the security lens: LLM applications blur data and
  instructions. It is essential for related work and threat-model wording.
- Novelty pressure: blocks "indirect prompt injection is new" and "retrieved
  external content can control tools/APIs is new".
- Gap to preserve: tool-output spoofing is broader than instruction injection:
  a JSON field, exit code, API status, browser observation, or citation can be
  false without telling the model to ignore instructions.
- Deep-read targets:
  - taxonomy of impacts;
  - real-world attack examples involving retrieval and tool/API calls;
  - mitigation discussion;
  - language for separating data/instruction channels.

### P0 - ToolEmu

- BibTeX key: `ruan2023toolemu`
- Title: Identifying the Risks of LM Agents with an LM-Emulated Sandbox
- Link: https://arxiv.org/abs/2309.15817
- PDF: `papers/core/toolemu-2023-lm-emulated-sandbox.pdf`
- Why core: core agent/tool safety benchmark. It uses an LM-emulated sandbox
  and an LM-based evaluator to identify high-stakes failures across 36 tools
  and 144 test cases.
- Relevance: close on tool-use risk and safety evaluation methodology.
- Novelty pressure: blocks broad "first tool-use risk benchmark/evaluator"
  claims.
- Gap to preserve: our lab should use concrete truthful/spoofed tool-result
  pairs and a deterministic oracle where possible, not only LM-emulated
  environments.
- Deep-read targets:
  - failure taxonomy;
  - evaluator prompt and validation;
  - human-evaluation result interpretation;
  - which failure cases involve untrustworthy returned observations.

### P0 - PoisonedRAG

- BibTeX key: `zou2024poisonedrag`
- Title: PoisonedRAG: Knowledge Corruption Attacks to Retrieval-Augmented
  Generation of Large Language Models
- Link: https://arxiv.org/abs/2402.07867
- PDF: `papers/core/poisonedrag-2024-knowledge-corruption-rag.pdf`
- Why core: canonical retrieval poisoning work for RAG systems. It frames the
  knowledge database as an attack surface and reports high ASR from injecting a
  small number of malicious texts.
- Relevance: retrieval is one kind of tool output. Fabricated retrieved
  evidence and forged citations are important subclasses for this lab.
- Novelty pressure: blocks broad "poisoning retrieved evidence for LLM answers"
  claims.
- Gap to preserve: our scope spans non-RAG tools and structured observations:
  payment status, scanner results, browser state, logs, metrics, and command
  outputs.
- Deep-read targets:
  - target-answer objective;
  - black-box vs white-box assumptions;
  - defense failures;
  - whether it records provenance/truth or only answer ASR.

### P0 - MalTool

- BibTeX key: `hu2026maltool`
- Title: MalTool: Malicious Tool Attacks on LLM Agents
- Link: https://arxiv.org/abs/2602.12194
- PDF: `papers/core/maltool-2026-malicious-tool-attacks.pdf`
- Why core: directly covers malicious tools in LLM-agent settings, with a
  taxonomy of malicious behaviors based on confidentiality, integrity, and
  availability, plus generated malicious-tool datasets.
- Relevance: malicious tool code can implement output fabrication, data
  exfiltration, or integrity attacks after the agent selects the tool.
- Novelty pressure: blocks broad "malicious tools/plugins for LLM agents are
  unstudied" claims.
- Gap to preserve: our lab can abstract away code-generation and installation
  concerns and focus on the semantic trust boundary of returned observations.
- Deep-read targets:
  - taxonomy categories that map to false outputs;
  - standalone vs embedded malicious tool implementations;
  - detector baselines and why they fail;
  - any explicit result-spoofing examples.

### P1 - Attractive Metadata Attack

- BibTeX key: `mo2025ama`
- Title: Attractive Metadata Attack: Inducing LLM Agents to Invoke Malicious
  Tools
- Link: https://arxiv.org/abs/2508.02110
- PDF: `papers/core/attractive-metadata-attack-2025-malicious-tools.pdf`
- Why core: covers a stealthy malicious tool/plugin surface where metadata
  such as names, descriptions, and schemas manipulates tool selection.
- Relevance: explains how an attacker gets the agent to call the malicious tool
  before output spoofing begins.
- Novelty pressure: blocks claims around metadata manipulation and malicious
  tool invocation.
- Gap to preserve: our attack is post-selection: the called tool's returned
  observation is false or adversarial.
- Deep-read targets:
  - metadata fields and optimization loop;
  - reported ASR/privacy leakage metrics;
  - prompt-level, auditor, and structured-protocol defense discussion;
  - relationship to MCP-style tools.

### P1 - RelyToolBench / Relign

- BibTeX key: `xu2024relytoolbench`
- Title: Reducing Tool Hallucination via Reliability Alignment
- Link: https://arxiv.org/abs/2412.04141
- PDF: `papers/core/relytoolbench-2024-tool-hallucination-reliability-alignment.pdf`
- Why core: defines tool hallucination categories and proposes a benchmark and
  reliability-alignment defense.
- Relevance: needed to draw a clean boundary between model-side tool
  hallucination and environment/tool-side output spoofing.
- Novelty pressure: blocks broad "first tool hallucination taxonomy or
  benchmark" claims.
- Gap to preserve: in our problem, the tool call and returned object exist; the
  returned observation is untrustworthy. Hallucination baselines may still be
  useful for metrics and "defer/ask clarification" defenses.
- Deep-read targets:
  - selection vs usage hallucination definitions;
  - hallucination-aware success metrics;
  - Relign's indecisive actions;
  - transferability to uncertainty/corroboration policies.

## Near-core extra

### P1-extra - ToolHijacker

- BibTeX key: `shi2025toolhijacker`
- Title: Prompt Injection Attack to Tool Selection in LLM Agents
- Link: https://arxiv.org/abs/2504.19793
- PDF: not downloaded; fetch only if the tool-selection boundary needs a deep
  read.
- Why it is listed: very relevant to retrieve-then-select tool libraries, but
  not counted in the core eight because the main attack is tool selection
  rather than spoofed outputs.
- Use: read if the novelty boundary around tool-library documents or
  retrieval-based tool selection becomes important.

## BibTeX seed entries

```bibtex
@misc{greshake2023indirect,
  title = {Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection},
  author = {Kai Greshake and Sahar Abdelnabi and Shailesh Mishra and Christoph Endres and Thorsten Holz and Mario Fritz},
  year = {2023},
  eprint = {2302.12173},
  archivePrefix = {arXiv},
  url = {https://arxiv.org/abs/2302.12173}
}

@misc{zhan2024injecagent,
  title = {InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated Large Language Model Agents},
  author = {Qiusi Zhan and Zhixiang Liang and Zifan Ying and Daniel Kang},
  year = {2024},
  eprint = {2403.02691},
  archivePrefix = {arXiv},
  url = {https://arxiv.org/abs/2403.02691}
}

@misc{debenedetti2024agentdojo,
  title = {AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents},
  author = {Edoardo Debenedetti and Jie Zhang and Mislav Balunovic and Luca Beurer-Kellner and Marc Fischer and Florian Tramer},
  year = {2024},
  eprint = {2406.13352},
  archivePrefix = {arXiv},
  url = {https://arxiv.org/abs/2406.13352}
}

@misc{ruan2023toolemu,
  title = {Identifying the Risks of LM Agents with an LM-Emulated Sandbox},
  author = {Yangjun Ruan and Honghua Dong and Andrew Wang and Silviu Pitis and Yongchao Zhou and Jimmy Ba and Yann Dubois and Chris J. Maddison and Tatsunori Hashimoto},
  year = {2023},
  eprint = {2309.15817},
  archivePrefix = {arXiv},
  url = {https://arxiv.org/abs/2309.15817}
}

@misc{zou2024poisonedrag,
  title = {PoisonedRAG: Knowledge Corruption Attacks to Retrieval-Augmented Generation of Large Language Models},
  author = {Wei Zou and Runpeng Geng and Binghui Wang and Jinyuan Jia},
  year = {2024},
  eprint = {2402.07867},
  archivePrefix = {arXiv},
  url = {https://arxiv.org/abs/2402.07867}
}

@misc{hu2026maltool,
  title = {MalTool: Malicious Tool Attacks on LLM Agents},
  author = {Yuepeng Hu and Yuqi Jia and Mengyuan Li and Dawn Song and Neil Gong},
  year = {2026},
  eprint = {2602.12194},
  archivePrefix = {arXiv},
  url = {https://arxiv.org/abs/2602.12194}
}

@misc{mo2025ama,
  title = {Attractive Metadata Attack: Inducing LLM Agents to Invoke Malicious Tools},
  author = {Kanghua Mo and Li Hu and Yucheng Long and Zhihao Li},
  year = {2025},
  eprint = {2508.02110},
  archivePrefix = {arXiv},
  url = {https://arxiv.org/abs/2508.02110}
}

@misc{xu2024relytoolbench,
  title = {Reducing Tool Hallucination via Reliability Alignment},
  author = {Hongshen Xu and Zichen Zhu and Lei Pan and Zihan Wang and Su Zhu and Da Ma and Ruisheng Cao and Lu Chen and Kai Yu},
  year = {2024},
  eprint = {2412.04141},
  archivePrefix = {arXiv},
  url = {https://arxiv.org/abs/2412.04141}
}

@misc{shi2025toolhijacker,
  title = {Prompt Injection Attack to Tool Selection in LLM Agents},
  author = {Jiawen Shi and Zenghui Yuan and Guiyao Tie and Pan Zhou and Neil Zhenqiang Gong and Lichao Sun},
  year = {2025},
  eprint = {2504.19793},
  archivePrefix = {arXiv},
  url = {https://arxiv.org/abs/2504.19793}
}
```

## Working novelty boundary after seed search

The safest provisional claim is not that tool-using-agent security is new.
AgentDojo, InjecAgent, ToolEmu, MalTool, AMA, and ToolHijacker already cover
large parts of that space.

The more defensible niche is:

> A paired benchmark for semantically fabricated tool observations, where the
> user request is benign, the selected tool returns syntactically valid but
> false data, and an oracle compares truthful vs spoofed observations to measure
> false-state propagation, corroboration, and provenance-aware defenses.

Each deep read should try to falsify or narrow this boundary.
