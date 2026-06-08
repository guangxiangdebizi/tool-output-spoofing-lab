# Deep read: IPI / RAG 相邻核心论文

Reader: deep-read subagent B  
Date: 2026-06-08 Asia/Shanghai  
Scope: 四篇与 tool-output spoofing 最相邻的 prompt-injection / RAG-poisoning 论文。

## 项目视角

本文件按 `tool-output spoofing` 的窄化定义阅读：攻击者控制或篡改一个工具/检索/API/浏览器/命令返回的 observation，使 agent 把**schema-valid 但语义虚假的工具观测**当作环境真相，并在缺少独立校验的情况下传播 false state、汇报或执行错误动作。

四篇论文共同给出的约束：

- 不能声称“外部内容/工具返回值可劫持 agent”是新的；Greshake、InjecAgent、AgentDojo 已经系统化。
- 不能声称“第一个 agent prompt-injection benchmark”；AgentDojo 和 InjecAgent 已覆盖。
- 不能声称“检索证据被投毒后误导 LLM/RAG”是新的；PoisonedRAG 已覆盖 semantic false evidence in RAG。
- 仍可保留的空间：跨工具面的 **observation-veracity benchmark**，强调非指令型、结构化、成对 truthful/spoofed observation、隐藏真值 oracle、provenance/freshness/corroboration 防御，而不是只测 injected instruction ASR。

---

## 1. AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents

### 元数据

- BibTeX key: `debenedetti2024agentdojo`
- PDF: `/root/tool-output-spoofing-lab/papers/core/agentdojo-2024-prompt-injection-agent-benchmark.pdf`
- 版本读取: arXiv v3, 2024-11-24
- 关系: P0 adjacent/direct benchmark；最接近“agent 通过工具消费不可信数据”的动态评测框架。

### 方法核心

AgentDojo 是一个可扩展的动态 benchmark framework，而不是固定 prompt 列表。它把评测拆成：

- **Environment/state**: 真实可变的模拟状态，如 Workspace、Slack、Travel、Banking。
- **Tools**: agent 通过工具读写环境状态；工具输出被格式化进 LLM 上下文。
- **User task**: benign user instruction，带 deterministic utility function，用环境前后状态和模型输出判断是否完成。
- **Injection task**: attacker goal，带 deterministic security function，判断攻击者目标是否达成。
- **Attack placeholder**: 在环境状态里预留可由攻击者控制的位置；当 agent 调用相关工具时，恶意文本作为工具返回数据的一部分进入上下文。
- **Security testcase**: 同一环境内 user task 与 injection task 的组合；无攻击时则作为 utility testcase。

重要方法选择：AgentDojo 不用另一个 LLM 来裁判 utility/security，而是用环境状态上的确定性检查函数。这个设计专门规避“评测 LLM 也被 prompt injection 劫持”的问题。

### 威胁模型

- 用户任务是 benign 的，例如读邮件、订酒店、付账单、发 Slack。
- 外部攻击者不能直接改 system prompt，但能控制一部分工具返回的数据，如邮件内容、网页内容、Slack/web/page/listing 等。
- 攻击目标是让 agent 代表用户执行 malicious task，例如泄露安全码、发 phishing link、转账、预订高价酒店等。
- 攻击发生在 **tool output enters model context** 的边界：工具确实被调用，但 observation 中混有攻击者文本。
- Agent 使用正常工具权限执行用户/攻击者任务；安全性由环境状态变更和输出判断。

### 评测

基准规模：

- 4 个环境: Workspace、Slack、Travel、Banking。
- 97 个 user tasks。
- 27 个 injection targets。
- 629 个 security test cases。
- 工具数按表格分解为 Workspace 24、Slack 11、Travel 28、Banking 11，总和 74；正文/表述里有“70/74”轻微不一致，引用时建议写“约 70+ tools”或直接写“the four suites sum to 74 tools”。

指标：

- **Benign Utility**: 无攻击时完成 user task 的比例。
- **Utility Under Attack**: 有攻击时仍完成用户任务且无 adversarial side effects 的比例。
- **Targeted ASR**: attacker goal 被完成的比例。

模型：

- Closed-source: Gemini 1.5 Flash/Pro, Claude 3/3.5, GPT-3.5/4/4o 等。
- Open-source/tool-prompted: Llama 3 70B, Command R+ 等。

攻击：

- 默认强攻击是 “Important message” 类自然语言注入：把攻击任务包装成一条“给模型的重要消息”。
- 与 `ignore previous instructions`、InjecAgent prompt、TODO prompt 等比较。
- 还做 attacker knowledge ablation，如是否知道用户名和模型名。

关键结果：

- 当前强模型在 benign setting 也不到完美；GPT-4o benign utility 约 69%，Claude 3.5 Sonnet 约 78%。
- 能力强的模型更容易完成攻击者任务；GPT-4o 在 “Important message”/强攻击设定下 targeted ASR 很高。
- Table 3 给出 GPT-4o targeted ASR 约 47.69%，utility under attack 约 50.08%。
- Table 4 中 “Important message” 对 GPT-4o targeted ASR 约 57.7%，明显高于 TODO / ignore previous / InjecAgent prompt；“Max” 自适应选择进一步提升 untargeted disruption。

防御：

- Data delimiters: 用分隔符包住工具输出并提示不要服从其中指令。
- PI detector: 用外部 prompt-injection classifier 检查每次工具输出。
- Repeat prompt / prompt sandwiching: 每次 tool call 后重复用户指令。
- Tool filter: 先基于用户任务限制可用工具集合。

防御结果：

- PI detector 和 tool filter 能显著降低 targeted ASR，但 PI detector false positives 降低 utility。
- Tool filter 对“用户任务只需读、攻击任务需写”的案例特别有效；但当用户任务和攻击任务需要同一批工具、或工具集合不能预先计划时失效。
- 论文明确指出：如果攻击只是改变某个工具调用结果本身，而不进一步 hijack agent behavior，隔离类防御仍可能脆弱。这是我们可以接住的 gap。

### 与 tool-output spoofing 的关系

高度相关，但不等同。

- 决定性对象确实作为 **tool result / untrusted data returned by tools** 进入上下文。
- 主要 harmful content 是自然语言 **malicious instruction**，不是无指令、schema-valid、语义虚假的状态值。
- AgentDojo 有可变环境和 deterministic oracle，这对我们的评测设计非常有价值。
- 它没有系统比较“同一任务下 truthful observation vs spoofed observation”的成对轨迹。
- 它没有把观察值真伪作为独立变量，也没有覆盖 exit code、receipt id、API status、timestamp、browser DOM state、benchmark metric 等结构化假观测。
- 它评测的是攻击目标是否被执行；不专门测 false-state propagation、corroboration failure、receipt/provenance/freshness validation。

### 它阻断的 claim

不要再声称：

- “第一个动态 agent prompt-injection benchmark”。
- “第一个评测 LLM agents 在不可信工具数据下的安全性”。
- “第一个用状态环境和工具调用评测 indirect prompt injection”。
- “第一个比较 prompt-injection defenses 的 agent benchmark”。

它还削弱：

- “工具输出是安全评测中未被考虑的边界”——AgentDojo 明确把 untrusted tool data 作为注入入口。

### 还剩什么 gap

可保留差异：

- **Observation veracity**, not instruction following: 工具返回字段本身是假的，但不命令模型做任何事。
- **Paired truthful/spoofed traces**: 同一个 user task、同一个 tool call，唯一变量是 observation truthfulness。
- **Structured tool outputs**: JSON status、transaction receipt、scanner verdict、shell stdout/stderr/exit code、browser success banner、citation metadata。
- **Truth oracle independent from tool output**: 工具返回不可信，评测真值来自隐藏状态或单独 oracle。
- **Verification defenses**: read-after-write、cross-tool corroboration、signed envelopes、freshness/nonces、provenance hierarchy，而不只是 prompt filtering。

---

## 2. InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated Large Language Model Agents

### 元数据

- BibTeX key: `zhan2024injecagent`
- PDF: `/root/tool-output-spoofing-lab/papers/core/injecagent-2024-indirect-prompt-injection-tool-agents.pdf`
- 版本读取: arXiv v3, 2024-08-04
- 关系: P0 adjacent；专门 benchmark tool-integrated LLM agents 的 indirect prompt injection。

### 方法核心

InjecAgent 把 IPI for tool agents 形式化为：

1. benign user instruction 要求 agent 调用 user tool `Tu` 获取外部内容；
2. `Tu` 的返回 `RTu` 中包含 attacker instruction `Ia`；
3. 攻击者希望 agent 后续调用 attacker tool `Ta`，造成用户伤害或数据泄露；
4. 若 agent 执行攻击者指令对应工具调用，则攻击成功。

测试集构造：

- 从 Ruan et al. / ToolEmu 的工具集合出发筛选 user tools。
- 生成 17 个 user cases，每个包含 user tool、user instruction、tool parameters、tool response template。
- tool response template 中有 `<Attacker Instruction>` placeholder，放在攻击者可修改且语义上合理的位置，如 review content、note body、shared page 等。
- 生成 62 个 attacker cases，分为 direct harm 和 data stealing。
- user cases 与 attacker cases 做 cross product，得到 17 × 62 = 1054 个 test cases。

攻击设定：

- **Base setting**: 直接把 attacker instruction 填入 placeholder。
- **Enhanced setting**: 在 attacker instruction 前加固定 hacking prompt，类似“ignore previous instructions”。

与 AgentDojo 的一个重要不同：InjecAgent 评测时假设 agent 已经正确执行了 user tool，并把含恶意内容的 Observation 放进 scratchpad；主要评估下一步动作，而不是完整环境中从零跑完整多工具流程。

### 威胁模型

- 用户是 benign 的，例如查询医生评价、读共享笔记、看产品评论。
- 攻击者能修改外部内容字段，但不能直接改用户指令或系统提示。
- 攻击者目标两大类：
  - **Direct harm**: 金融伤害、物理伤害、数据安全破坏，如转账、开门、移动私有文件。
  - **Data stealing**: 读取用户私密信息，再通过消息/邮件工具发给攻击者。
- 对 data stealing，论文拆成两步：
  - S1: 调用数据提取工具。
  - S2: 调用发送工具把数据传给攻击者。

### 评测

规模：

- 17 user tools / user cases。
- 62 attacker tools / attacker cases。
- 每个 setting 1054 test cases。
- 30 个 LLM agents。

模型/agent 类型：

- Prompted agents: ReAct prompt 包装不同 LLM，包括 Qwen、Mistral、Llama2、Claude-2、GPT-3.5、GPT-4 等。
- Fine-tuned agents: OpenAI fine-tuned/function-calling GPT-3.5 和 GPT-4。

指标：

- **Valid rate**: 输出是否可解析、是否符合 ReAct/tool format。
- **ASR-valid**: 在 valid outputs 中攻击成功比例。
- **ASR-all**: 所有 test cases 中攻击成功比例。
- 对 data stealing 分别报告 S1/S2 和 total。

关键结果：

- Prompted GPT-4: base ASR-valid 约 24%，enhanced 约 47%。
- Prompted Llama2-70B: base/enhanced ASR-valid 都超过 80%，说明强 ReAct agent 容易服从恶意 observation。
- Fine-tuned GPT-4: base 约 6.6%，enhanced 约 7.1%；比 prompted agents 更稳，但不为零。
- Enhanced hacking prompt 通常提高 ASR，但也可能触发部分模型的安全敏感性。
- 一旦完成数据提取，数据传输 S2 往往成功率极高；fine-tuned GPT-3.5/GPT-4 在 S2 上可达 100%。

分析发现：

- user case 对攻击成功的关联强于 attacker case。
  - Direct harm: user case Cramér's V 约 0.28，高于 attacker case 约 0.18。
  - Data stealing: user case 约 0.31，高于 attacker case 约 0.20。
- placeholder 的 **content freedom** 越高越危险；自由文本字段让恶意 instruction 更像正常内容。
- 失败输出中有两种典型模式：把恶意指令当普通内容返回给用户，或识别为异常/敏感而拒绝执行。

局限：

- 攻击最多两步，且多轮/长期 agent 场景未覆盖。
- Enhanced setting 只使用一个固定 hacking prompt。
- fine-tuned agents 只覆盖少数。
- 评测从“用户工具已被调用并返回 observation”开始，不完全覆盖真实 agent planning/path selection。

### 与 tool-output spoofing 的关系

非常接近 tool-output boundary，但核心仍是 **instruction injection**。

- 决定性攻击载荷作为 user tool response 的字段进入 agent context。
- 工具返回可以是结构化对象，如 review JSON/list，但恶意部分通常是自然语言 instruction。
- 用户任务 benign；攻击者借外部内容触发有害工具调用。
- 没有系统评估“工具返回语义上撒谎但不发指令”的情况。
- 没有成对 truthful/spoofed observations；也没有隐藏状态 oracle。
- 没有测试 provenance/freshness/signature/cross-tool corroboration。
- 其 “content freedom” 分析可迁移到我们：自由文本字段更适合 instruction smuggling；但我们的重点应扩展到低自由度字段，如 `success=true`、`exit_code=0`、`receipt_id`、`timestamp`、`citation_url`。

### 它阻断的 claim

不要再声称：

- “第一个 indirect prompt injection benchmark for tool-integrated agents”。
- “第一个证明外部工具内容能导致 harmful tool calls”。
- “第一个把 benign user task + attacker-controlled external content 组合成 agent security cases”。
- “第一个比较 prompted vs fine-tuned tool agents 的 IPI vulnerability”。

它还削弱：

- “工具返回中嵌入攻击文本还没有系统评测”。

### 还剩什么 gap

可保留差异：

- **Non-instructional spoofing**: observation 没有“请转账/请发邮件/ignore previous”，只有假的事实或状态。
- **低自由度结构化字段**: API 状态码、付款成功字段、扫描结果布尔值、文件哈希、DOM state、benchmark score。
- **Truthful/spoofed divergence metric**: 同一 agent 在真实 observation 与伪造 observation 下决策是否分叉。
- **Corroboration behavior**: agent 是否调用独立工具核验，而不是只检测恶意语言。
- **完整多步环境 replay**: 不只从攻击 observation 后的下一步开始，而是记录 agent 如何在后续 reasoning 中传播 false state。

---

## 3. Greshake et al.: Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection

### 元数据

- BibTeX key: `greshake2023indirect`
- PDF: `/root/tool-output-spoofing-lab/papers/core/greshake-2023-indirect-prompt-injection.pdf`
- 版本读取: arXiv v2, 2023-05-05
- 关系: P0 foundational；间接提示注入的基础威胁模型和 taxonomy。

### 方法核心

该论文不是 benchmark，而是 taxonomy + proof-of-concept demonstrations。核心观点：

- LLM-integrated applications 把 retrieval/tool/API 输出拼进模型上下文，模糊了 data 与 instruction 的边界。
- 攻击者不需要直接访问用户的 chat interface；只要把 prompt 放到会被检索/读取的数据源中，就能远程影响其他用户的 LLM 应用。
- 在 LLM 应用中，retrieved prompt 近似“自然语言代码”；处理不可信数据类似执行 attacker-provided code。

攻击交付方式 taxonomy：

- **Passive retrieval**: 把 prompt 放在网页、社交媒体、公共文档、代码仓库文档中，等待搜索/检索触发。
- **Active delivery**: 邮件、消息、文档等主动送达会被 LLM agent 处理的渠道。
- **User-driven injection**: 诱导用户复制/粘贴含隐藏 prompt 的内容。
- **Hidden/obfuscated injection**: HTML comments、encoded payload、multi-stage payload、视觉/多模态隐藏等。

威胁 taxonomy：

- Information gathering / data theft。
- Fraud / phishing / scams。
- Intrusion / remote control / persistence / API calls。
- Malware / prompt worm / malicious link distribution。
- Manipulated content / wrong summaries / disinformation / biased output / source blocking / ads。
- Availability / DoS / API input-output sabotage。

### 威胁模型

- 攻击者控制会被 LLM-integrated app 读取的外部数据源。
- 用户 prompt 通常是 benign，如总结网页、询问信息、读取邮件。
- LLM 应用可能有搜索、浏览、读取 URL、读/写邮件、地址簿、memory、code completion 等能力。
- 攻击目标可以是 end-user、developer、automated system，甚至 LLM service availability。
- 攻击发生于 inference time；不要求训练数据投毒或模型参数访问。

### 评测

评测性质是 qualitative demonstrations：

- Synthetic applications: OpenAI API + LangChain/ReAct 或 GPT-4 chat prompt，连接 mock tools，如 search、view、retrieve URL、read/send email、address book、memory。
- Bing Chat / Edge sidebar: 用本地 HTML comments 等方式模拟网页内容被 sidebar 读取。
- GitHub Copilot: 在代码注释/文档上下文中测试对 completion 的污染。

展示的关键场景：

- 通过搜索或 URL side channel 诱导用户泄露信息。
- 让模型分发 phishing/malware links。
- 邮件 agent 读到 payload 后向地址簿联系人转发，形成 prompt worm。
- 让模型从攻击者服务器拉取新指令，形成 remote control。
- 把 payload 写入 memory，下次读取 memory 时自我再感染。
- 污染 code completion。
- 操纵搜索/总结输出：错误总结、偏置输出、source blocking、定向 disinformation、隐性广告。
- availability attack：让模型做耗时任务、破坏搜索 query、破坏搜索 result。

重要局限：

- 无系统性 ASR。
- 许多实验是 synthetic 或本地模拟，避免向真实公共源投毒。
- 交互式攻击的触发率、说服力、用户研究都未量化。
- 对防御的讨论偏方向性：过滤、moderator、source verification、interpretability 都被认为不可靠或待研究。

### 与 tool-output spoofing 的关系

这是 tool-output spoofing 的概念祖先之一，但范围和焦点不同。

直接相关点：

- 明确指出 LLM 作为用户和信息/API 的中间层，输入和输出操作都可能被操纵。
- “Manipulated content” 部分已经展示错误总结、source blocking、disinformation、搜索 query/result sabotage；这接近 retrieval/browser observation 被污染后导致错误信念。
- Synthetic tools 包括 search/view/retrieve/email/memory，说明工具结果是攻击入口。

差异：

- 主要机制仍是 prompt/instruction injection，即外部内容命令模型改变行为。
- 没有专门研究工具服务端返回 schema-valid false result，例如 `payment_succeeded=true` 但环境未变化。
- 没有成对 truthful/spoofed tool traces。
- 没有 deterministic truth oracle 或 false-state propagation 指标。
- 没有系统评估结构化工具输出、exit codes、receipts、timestamps、signatures、cross-tool contradiction。

### 它阻断的 claim

不要再声称：

- “间接提示注入/远程外部内容控制 LLM app 是新问题”。
- “LLM-integrated apps 中 data/instruction boundary 被模糊是新观察”。
- “retrieved web/email/code 内容可触发 API/tool misuse 是新观察”。
- “LLM 可被外部内容操纵生成错误总结、disinformation、source blocking 是新观察”。
- “prompt worm、persistence、remote-control 风险是本项目首次提出”。

### 还剩什么 gap

可保留差异：

- 从 **prompt-as-code** 转为 **observation-as-fact**：攻击不命令模型，只伪造事实/状态/证明。
- 从 qualitative PoC 转为 deterministic benchmark。
- 从网页/邮件/检索自然语言扩展到 REST/MCP/shell/browser/RAG 多工具面。
- 从“模型是否服从外部指令”转为“模型是否把不可信 observation 当真值、是否校验”。
- 从 prompt-filtering 讨论扩展到 provenance/corroboration/freshness/signature 防御。

---

## 4. PoisonedRAG: Knowledge Corruption Attacks to Retrieval-Augmented Generation of Large Language Models

### 元数据

- BibTeX key: `zou2024poisonedrag`
- PDF: `/root/tool-output-spoofing-lab/papers/core/poisonedrag-2024-knowledge-corruption-rag.pdf`
- 版本读取: arXiv v3, 2024-08-13
- 关系: P0 adjacent/direct for retrieval surface；检索知识库投毒和 fabricated evidence 的强相邻工作。

### 方法核心

PoisonedRAG 研究 RAG 的 knowledge database 作为攻击面。攻击者选择 target question `Qi` 和 target answer `Ri`，向知识库注入少量 malicious texts，使 RAG 对目标问题输出攻击者指定答案。

论文把攻击形式化为优化问题：注入文本集合 `Γ` 后，RAG 从 `D ∪ Γ` 检索 top-k 文本，LLM 基于这些上下文生成 target answer。

核心设计是两个必要条件：

1. **Retrieval condition**: malicious text 必须能被 target question 检索进 top-k。
2. **Generation condition**: 当 malicious text 作为上下文时，LLM 应输出 target answer。

构造：

- 把 malicious text `P` 分成 `S ⊕ I`。
- `I`: 用 LLM 生成一段“知识文本”，让它支持 target answer；这是 generation condition。
- `S`: 让文本更像 target question，确保被 retriever 找到；这是 retrieval condition。
- Black-box setting: 直接用 target question 作为 `S`，即 `P = Q ⊕ I`。
- White-box setting: 若知道 retriever 参数，则优化 `S`，让 `S ⊕ I` 的 embedding 更接近 query。

关键区别：论文明确区分 prompt injection baseline 与 PoisonedRAG。PoisonedRAG 的主攻击不是“请输出 X”的指令，而是构造看似知识的虚假语料，使模型基于“证据”输出 X。

### 威胁模型

- 攻击者选择任意 target questions 和 target answers。
- 攻击者不能访问知识库内容，不能访问/查询 RAG 中的 LLM。
- Black-box: 也不能访问/查询 retriever。
- White-box: 可以访问 retriever 参数，例如 RAG 使用公开 retriever。
- 攻击者能向 knowledge database 注入少量文本，例如编辑 Wikipedia、发布虚假网页/新闻、企业内部知识库 insider 写入等。
- 攻击不修改 LLM 或 retriever 训练数据；只污染 RAG 知识库。

### 评测

数据集/知识库：

- Natural Questions (NQ): 2,681,468 clean texts。
- HotpotQA: 5,233,329 clean texts。
- MS-MARCO: 8,841,823 clean texts。

默认设置：

- 每个 target question 注入 `N=5` malicious texts。
- RAG top-k 默认 `k=5`。
- 目标问题：每个数据集随机选 10 个 close-ended questions，重复 10 次，共 100 target questions。
- target answer 由 GPT-4 生成并人工检查不同于 ground truth。

模型和 retriever：

- LLM: PaLM 2、GPT-3.5、GPT-4、LLaMA-2 7B/13B、Vicuna 7B/13B/33B 等。
- Retriever: Contriever、Contriever-ms、ANCE。

指标：

- **ASR**: target questions 中输出 attacker-chosen target answer 的比例。
- **Precision/Recall/F1**: malicious texts 是否被检索进 top-k。
- #Queries / runtime: 构造文本成本。

关键结果：

- 注入 5 条文本即可在百万级知识库中取得高 ASR。
- NQ black-box: 多个 LLM 上 ASR 约 0.88-0.97；PaLM 2/GPT-4 约 0.97。
- HotpotQA black-box: 多个 LLM 上 ASR 约 0.93-0.99。
- MS-MARCO black-box: 多个 LLM 上 ASR 约 0.89-0.96。
- PoisonedRAG 明显优于 Naive Attack、Corpus Poisoning、GCG、Disinformation-only、Prompt Injection baseline；原因是它同时满足 retrieval 与 generation 条件。
- Prompt injection baseline 有非零 ASR，但弱于 PoisonedRAG；这反过来说明“虚假知识”本身是有效攻击，不只是 injected instruction。

扩展评测：

- Advanced RAG:
  - Self-RAG / CRAG 仍受影响；ASR 大致在 0.70-0.87 区间，说明“更会评估/反思检索质量”的 RAG 不足以阻止相关且虚假的知识。
- Wikipedia-based chatbot:
  - 用 2018-12-20 英文 Wikipedia dump 构建 21,015,324 texts 的知识库，PoisonedRAG 仍有约 0.91-1.0 ASR/F1。
- LLM agent:
  - 用 ReAct Agent 做 QA；black-box attack 在 NQ、HotpotQA、MS-MARCO 上 ASR 分别约 0.72、0.58、0.52。

防御：

- Paraphrasing query: 降低但不能消除攻击；例如 NQ black-box ASR 从 0.97 降到约 0.87。
- Perplexity detection: ROC/AUC 很差；malicious texts 由 GPT-4 生成且质量正常，不像低质量异常文本。
- Duplicate text filtering: 基本无效，因为每条 `I` 都可多样化。
- Knowledge expansion: 增大 k 仍不能完全防御；即使 k=50，在 HotpotQA 上仍有显著 ASR，且会增加 LLM 上下文成本。

局限：

- 主要是 close-ended QA；open-ended answers 难以自动评估。
- ASR 用 substring matching，并有人评验证相近，但不是通用语义真值评估。
- 目标是最终 answer corruption，不是 agent 多工具决策。
- RAG-only；不覆盖一般 API/command/browser/status observation。

### 与 tool-output spoofing 的关系

这是四篇里最接近“非指令型语义假观测”的工作，但只覆盖 RAG surface。

直接相关：

- Retrieval result 是一种 tool output / observation。
- harmful content 主要是 **semantic falsehood / malicious knowledge**，不是显式指令。
- 攻击目标是让模型基于虚假证据输出错误答案。
- 评测中有 clean knowledge 与 poisoned knowledge 的对照，且 target answer 与 ground truth 不同。

差异：

- 只研究 RAG/knowledge database，不覆盖 REST/MCP/API/shell/browser/tool-server result。
- 观察对象是自然语言 corpus，不是 schema-valid structured tool response。
- 没有 paired truthful/spoofed trace protocol；不是每个工具调用都有同形 truthful/spoofed observation。
- 真值主要是 QA ground truth / target answer，不是隐藏环境状态或 action oracle。
- 没有评估 agent 是否独立校验证据、检查 provenance、freshness、signatures、read-after-write。
- 没有测试 downstream false-state propagation 到后续工具动作，例如基于假 scanner verdict 部署、基于假 payment receipt 汇报成功。

### 它阻断的 claim

不要再声称：

- “第一个研究 RAG 知识库投毒/检索证据投毒”。
- “第一个证明少量恶意检索文本能让 LLM 输出攻击者指定答案”。
- “第一个用语义虚假知识而不是 prompt instruction 攻击 RAG”。
- “第一个 fabricated citations/evidence 风险方向”。

它还强烈削弱：

- “非指令型虚假内容误导 LLM 是未被研究的”——PoisonedRAG 已经在 RAG QA 上系统证明。

### 还剩什么 gap

可保留差异：

- **Beyond RAG**: API status、transaction receipts、browser DOM observations、shell/test outputs、scanner logs、MCP tool returns。
- **Structured semantic lies**: `{"paid": true}`、`{"vulnerable": false}`、`{"exit_code": 0}`、`{"citation_verified": true}`，而不是自然语言知识段落。
- **Agent decision divergence**: 对比 truthful vs spoofed observation 下 agent 的计划、工具调用、最终汇报是否分叉。
- **Receipt/provenance defenses**: 签名响应、nonce/timestamp/freshness、independent read-after-write、cross-tool corroboration。
- **Multi-surface benchmark**: 把 PoisonedRAG 作为 RAG/search 子套件，而不是整个项目。

---

## Cross-paper synthesis for novelty

### 这四篇共同已经覆盖

| 已覆盖主题 | 覆盖论文 | 对我们的影响 |
| --- | --- | --- |
| 外部内容可间接 prompt-inject LLM app | Greshake | 不能把 IPI 本身说成新 |
| 工具 agent 会因工具返回的不可信文本执行恶意工具调用 | InjecAgent, AgentDojo | 不能说工具返回攻击未被 benchmark |
| 动态状态环境、工具调用、deterministic utility/security checks | AgentDojo | 我们应承认并复用这种评测思想 |
| prompt-injection defenses in agents | AgentDojo | prompt filter/delimiter/tool-filter 应作为 baseline，而不是 novelty |
| RAG 知识库投毒、虚假证据误导回答 | PoisonedRAG | RAG fabricated evidence 不是新颖主张 |
| 错误总结/disinformation/source manipulation | Greshake, PoisonedRAG | 不能泛称“LLM 被虚假信息误导”是新 |

### 仍可主张的窄化空间

建议把项目 claim 锁定为：

> 一个 deterministic, local, multi-surface benchmark for schema-valid but semantically fabricated tool observations, using paired truthful/spoofed traces and an independent truth oracle, with defenses centered on provenance, freshness, receipts, and cross-tool corroboration.

必要限定：

- 不说“first tool-output attack”。
- 不说“first untrusted tool data benchmark”。
- 不说“first RAG poisoning / fabricated evidence attack”。
- 说“we isolate observation veracity as the experimental variable across non-RAG and RAG tool surfaces”。

### 我们必须保留的 differentiators

1. **Observation truthfulness is the variable**  
   user task、agent、tool schema、tool-call path 尽量相同；唯一变化是工具 observation 是否 truthful。

2. **No injected command required**  
   样例应包含完全没有“ignore previous / please do X”的 spoofed output，例如：
   - payment says succeeded while ledger unchanged;
   - scanner says clean while raw finding exists;
   - tests say pass while failing assertion exists;
   - browser success banner appears while DB not updated;
   - citation metadata says verified while URL/body mismatch.

3. **Independent truth plane**  
   工具返回可被攻击者控制；评测 oracle 必须来自隐藏状态、raw trace、secondary source 或 signed ground truth。

4. **False-state propagation metric**  
   不只看最终答案是否错，还记录 agent 是否：
   - 采纳 spoofed state；
   - 在 scratchpad/summary 中传播；
   - 基于它做下一步工具调用；
   - 未请求独立证据；
   - 在 contradictory evidence 下仍自信。

5. **Verification defenses, not only prompt defenses**  
   Prompt-injection defenses 应作为 negative/weak baselines。主防御应包括：
   - read-after-write;
   - cross-tool corroboration;
   - provenance hierarchy;
   - signed result envelope;
   - freshness timestamp / nonce;
   - uncertainty policy when observations conflict.

---

## 相关工作怎么写的建议

### 建议结构

把 related work 分成四段，按“从已知到 gap”的顺序写：

1. **Indirect prompt injection in LLM-integrated applications**  
   引 Greshake：外部检索/邮件/网页/代码内容可在 inference time 作为指令控制 LLM app，造成 data theft、fraud、worms、content manipulation、DoS。承认 data/instruction boundary 是基础问题。

2. **Agent benchmarks for prompt injection over tool outputs**  
   引 InjecAgent 和 AgentDojo：前者系统构造 tool-integrated agents 的 1054 IPI cases；后者提供动态状态环境、97 user tasks、629 security cases、deterministic utility/security checks 和 defense comparison。强调它们主要测 attacker-written instructions embedded in external/tool data 是否触发 harmful tool calls。

3. **Retrieval / RAG poisoning and fabricated evidence**  
   引 PoisonedRAG：知识库注入少量 malicious texts 即可让 RAG 对目标问题输出攻击者指定答案；这是 RAG/search observation spoofing 的强基线。承认“semantic false evidence in retrieval”已经被系统研究。

4. **Our gap: observation-veracity spoofing across tool surfaces**  
   转折：以上工作主要研究 external content as instructions 或 RAG natural-language evidence；我们隔离的是 tool observation 的 truthfulness，特别是 schema-valid、低自由度、非指令型字段，以及 agent 是否做 provenance/corroboration。

### 可直接改写的英文 related-work 句子

可以在论文中用类似表述：

> Prior work on indirect prompt injection shows that untrusted external content can steer LLM-integrated applications at inference time, including applications with retrieval, email, memory, and API access. Agent-focused benchmarks such as InjecAgent and AgentDojo further quantify how malicious instructions embedded in tool-returned content can induce harmful tool calls under benign user tasks.

接 PoisonedRAG：

> A separate line of work studies poisoning of retrieval corpora. PoisonedRAG demonstrates that a small number of malicious texts can satisfy both retrieval and generation conditions, causing RAG systems to produce attacker-chosen answers without relying solely on explicit injected instructions.

然后定义 gap：

> Our focus is complementary: rather than injecting instructions into external content or poisoning only retrieval corpora, we isolate the semantic integrity of tool observations themselves. The spoofed outputs in our benchmark are schema-valid observations such as statuses, receipts, verdicts, timestamps, citations, logs, and browser states; they need not contain imperative text. Each task is evaluated under paired truthful and spoofed observations against an independent truth oracle, enabling measurement of false-state propagation and the effectiveness of provenance, freshness, and corroboration defenses.

### Baselines / comparisons we should include

从这四篇抽出的必须 baseline：

- **Prompt-injection attack strings**:
  - `ignore previous instructions`;
  - InjecAgent enhanced hacking prompt;
  - AgentDojo “Important message” style prompt.
- **Prompt-centric defenses**:
  - delimiters/data marking;
  - prompt-injection detector;
  - repeat user prompt / prompt sandwiching;
  - tool filter / least-privilege tool subset。
- **RAG sub-suite baseline**:
  - PoisonedRAG-style target question + malicious knowledge for search/RAG cases。
- **Metrics to borrow/adapt**:
  - AgentDojo: benign utility, utility under attack, targeted ASR。
  - InjecAgent: ASR-valid vs ASR-all if model output parsing can fail。
  - PoisonedRAG: retrieval precision/recall/F1 for RAG cases。
  - Our added metrics: decision divergence, false-state propagation, corroboration rate, unsupported-confidence rate, oracle mismatch rate。

### Claims to avoid in paper intro

避免：

- “Prompt injection through tools has not been studied.”
- “No benchmark evaluates LLM agents under untrusted tool outputs.”
- “RAG poisoning / fabricated retrieved evidence is new.”
- “External data can act as instructions for LLM apps is new.”
- “Defenses against prompt injection are absent.”

建议替代：

- “Existing benchmarks emphasize malicious instructions embedded in untrusted content; we study schema-valid semantic lies in tool observations.”
- “Existing RAG poisoning work focuses on natural-language retrieval corpora; we generalize observation integrity to non-RAG tool surfaces and structured outputs.”
- “Existing prompt-centric defenses are insufficiently targeted at veracity; we compare them with provenance and corroboration controls.”

### 最短相关工作定位

如果篇幅有限，可压缩成一句：

> Greshake et al., InjecAgent, and AgentDojo establish that untrusted external/tool-returned text can inject instructions into LLM applications and agents, while PoisonedRAG shows that poisoned retrieved knowledge can corrupt RAG answers; our benchmark instead treats the truthfulness of schema-valid tool observations as the controlled variable across multiple tool surfaces and evaluates whether agents verify, propagate, or act on spoofed state.

