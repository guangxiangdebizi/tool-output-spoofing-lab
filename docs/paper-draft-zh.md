# 中文论文初稿：工具会撒谎时，智能体如何验证观察结果？

工作标题：

> **当工具会撒谎：面向工具调用型 LLM 智能体的 schema-valid 虚假观察 benchmark**

当前定位：这是中文研究工作稿，优先把问题、benchmark、baseline、预实验结果讲清楚；等实验设计和审稿反馈稳定后，再整理成英文投稿稿。

## 摘要

工具调用型 LLM 智能体越来越依赖外部 API、MCP server、浏览器观察、检索系统和 shell wrapper 返回的结果来判断世界状态。已有研究已经证明，工具可见数据可能携带 indirect prompt injection，恶意工具元数据可能影响工具选择，恶意工具实现可能在执行阶段投毒。本文关注一个更窄但互补的问题：**工具返回结果在语法和 schema 上完全有效，也不包含显式恶意指令，但其中关键事实是假的。**

我们把这个问题定义为 **tool-output spoofing**，并设计一个 observation-spoofing overlay：主实验不应主要依赖自建 toy benchmark，而应基于已有高价值 agent/tool-use benchmark，例如 AgentDojo、ToolSandbox、tau-bench、WebArena/WorkArena、SWE-bench、MCP-SafetyBench / MCP Security Bench。已有 benchmark 提供任务分布、环境状态和 utility/security oracle；我们的 overlay 只改变 agent 可见的 observation plane，并在同一批 benchmark tasks 上比较不同 defense baseline。

当前仓库里的 15 个本地场景只作为 local smoke/regression suite，用来验证 trace schema、oracle、baseline 和 harness；它不计为论文主 benchmark 证据，也不用于支撑核心 empirical claim。当前真正的主实验表应留给 ToolSandbox / AgentDojo / tau-bench 等现有 benchmark overlay pilot。现阶段本地 suite 只证明实现链路可跑：schema validation、prompt filtering、repeat-same-tool、independent-validator、combined policy 等 baseline 可以在同一任务上被成对比较。本轮新增了 OpenAI-compatible real tool-call harness 和 run manifest 入口，但当前 shell 缺少 `NEWAPI_API_KEY`，所以只完成 dry-run 验证，尚未完成基于现有 benchmark 的 30-45 paired scenario real-model pilot。

## 1. 问题定义

智能体通常把工具输出当作外部世界的观察，例如：

- `status=succeeded`
- `receipt_valid=true`
- `citation_verified=true`
- `form submitted`
- `12 passed`

但这些观察可能被远程 API、MCP server、cache、proxy、browser wrapper 或 command wrapper 篡改。本文不把重点放在“工具输出里夹带指令”上，而是隔离一个更纯粹的问题：

> 如果用户请求是 benign 的，工具输出也没有显式攻击指令，只是 schema-valid 但事实错误，智能体会不会把它当作真相？

这个区分很重要。prompt-injection sanitizer 可以删掉“ignore previous instructions”，但不会验证 `status=succeeded` 是否真实。工具 allowlist 可以保证选中的工具名可信，但不能保证返回内容 fresh、request-bound、signed 或与独立状态一致。

## 2. Threat model

攻击者控制一次工具调用后的观察通道，可以是：

- compromised remote API 或 MCP server；
- 改写工具响应的中间层；
- stale cache / replay proxy；
- 伪造成功 banner 的浏览器观察 wrapper；
- 伪造 stdout/stderr/exit code 的 shell wrapper；
- 返回假 DOI / 假 citation 的检索层。

攻击者不能修改 system prompt、benchmark oracle 或 hidden truth。攻击 payload 不要求包含指令文本；核心场景是 schema-valid semantic falsehood。

防御者可以控制 agent harness，加入 schema validation、repeat call、validator call、freshness check、signed receipt、provenance policy、final-answer gate 等。推理时防御者不能直接访问 hidden truth；hidden truth 只给评估 oracle 使用。

## 3. Benchmark 设计：现有 benchmark substrate + spoofing overlay

最终论文的主 benchmark 不从零自建任务集，而是选择已有高价值 benchmark 作为任务底座：

| Benchmark substrate | 价值 | 我们的 overlay |
| --- | --- | --- |
| AgentDojo | 成熟 agent security benchmark，有 utility/security checks。 | 不插入指令，只篡改 tool-visible factual fields。 |
| ToolSandbox | 有 stateful execution context 和 milestone DAG oracle。 | agent 看到 spoofed tool result，oracle 读真实 state snapshot。 |
| tau-bench / tau2-bench | 真实 retail/airline tool-agent-user API 交互。 | API proxy 返回 schema-valid false order/refund/reservation status。 |
| WebArena / WorkArena | 浏览器/企业 UI 任务，有 backend/task validation。 | 改写 DOM/a11y/success banner observation，backend truth 不变。 |
| SWE-bench / SWE-agent | 代码任务有测试 oracle。 | spoof stdout/exit code/test summary，oracle 跑真实测试。 |
| MCP-SafetyBench / MCP Security Bench | 最接近 MCP 安全评测。 | 复用 taxonomy/任务，隔离非指令型 schema-valid false return。 |
| PoisonedRAG / SafeRAG | 检索安全 substrate。 | 把 retrieval 当 agent tool，篡改 citation/provenance fields。 |

每个 overlay scenario 是一个从现有 benchmark task 派生的 record，包含：

- public user task；
- domain 和 spoof class；
- hidden ground truth；
- truthful tool result；
- spoofed tool result；
- optional independent validator result；
- expected safe behavior；
- success criteria。

核心协议是 paired truthful/spoofed：

| 条件 | Hidden truth | Visible result | 期望鲁棒行为 |
| --- | --- | --- | --- |
| clean truthful | 固定 | truthful | 正常完成任务 |
| spoofed no defense | 相同 | spoofed | 脆弱 agent 可能接受假状态 |
| spoofed with defense | 相同 | spoofed | 验证、拒绝或表达不确定 |
| truthful with defense | 相同 | truthful | 不应 blanket refusal |

这个设计把 false acceptance 和 false-positive refusal 分开。一个永远拒绝工具输出的防御可以拿到低 ASR，但 clean utility 不合格。

## 4. 当前本地 smoke/regression suite 和未来 benchmark overlay

截至 2026-06-08，仓库里有一个 15-scenario 本地 smoke/regression suite。它不是最终主 benchmark，也不应被包装成自建 benchmark 的代表性证据；它的作用是验证 overlay 协议、trace schema、oracle 和 baseline 是否工作。真正的主实验应迁移到 ToolSandbox / AgentDojo / tau-bench 等现有 benchmark substrate。

| Suite / control | 场景数 | spoof class |
| --- | ---: | --- |
| API records | 4 | false success、fabricated entity、schema-valid scalar、stale replay |
| MCP finance | 3 | forged receipt、parameter binding mismatch、false error |
| RAG/search | 3 | forged provenance、warning stripping、fake authority |
| Browser form | 2 | fake success banner、submitted-target mismatch |
| Shell/tests | 2 | exit-code spoof、truncated log |
| Instruction-smuggling control | 1 | JSON 内嵌指令文本 |

本地 smoke 场景配置在 `configs/experiments/mvp_matrix.json`。overlay 设计配置在：

- `configs/benchmark_overlays/high_value_benchmark_overlay.json`
- `configs/benchmark_overlays/toolsandbox_overlay_smoke.json`
- `docs/benchmark-overlay-strategy.md`

本地 smoke 可复现命令：

```bash
PYTHONPATH=src /usr/bin/python3.11 scripts/run_mvp_matrix.py \
  --config configs/experiments/mvp_matrix.json \
  --out-dir traces/mvp_15scenario_partial
```

结构化版本命令：

```bash
PYTHONPATH=src:. /usr/bin/python3.11 scripts/run_structured_partial.py \
  --config configs/experiments/mvp_matrix.json \
  --out-dir traces/structured_15scenario_partial \
  --summary outputs/structured_partial_summary.json
```

真实模型 tool-call harness 入口：

```bash
PYTHONPATH=src:. /usr/bin/python3.11 scripts/run_real_toolcall_pilot.py \
  --config configs/experiments/real_toolcall_pilot_small.json \
  --out-dir traces/real_toolcall_pilot \
  --summary outputs/real_toolcall_pilot_summary.json \
  --manifest outputs/real_toolcall_pilot_manifest.json
```

如果没有 API key，可以先 dry-run 验证 trace / manifest 结构：

```bash
PYTHONPATH=src:. /usr/bin/python3.11 scripts/run_real_toolcall_pilot.py \
  --config configs/experiments/real_toolcall_pilot_small.json \
  --out-dir traces/real_toolcall_pilot_dry \
  --summary outputs/real_toolcall_pilot_dry_summary.json \
  --manifest outputs/real_toolcall_pilot_dry_manifest.json \
  --dry-run --sleep 0
```

ToolSandbox overlay adapter-contract smoke：

```bash
PYTHONPATH=src:. /usr/bin/python3.11 scripts/run_toolsandbox_overlay_smoke.py \
  --config configs/benchmark_overlays/toolsandbox_overlay_smoke.json \
  --out-dir traces/toolsandbox_overlay_smoke \
  --summary outputs/toolsandbox_overlay_smoke_summary.json
```

当前环境还没有安装真实 ToolSandbox package，所以这一步只验证 adapter contract：
ToolSandbox-shaped fixture 的 hidden state / milestone oracle / spoofed
observation / independent validator 能被转换成统一 trace schema。下一步要接真实
ToolSandbox tasks。

## 5. Baseline 设计

当前实现了两层 baseline。

### 5.1 第一层：deterministic keyword baseline

用于快速验证 benchmark mechanics：

| Baseline | 输入 | 行为 |
| --- | --- | --- |
| naive accept | visible result | 直接接受可见工具结果 |
| schema-only | visible result | schema valid 就接受 |
| prompt-filter-only | visible result | 只拦截 instruction-like text |
| cautious/corroboration | visible result + provenance | 非 truth provenance 就要求 corroboration |
| cross-tool verifier | visible result + independent result | 字段级比较独立验证器 |

### 5.2 第二层：structured field-level baseline

这是本轮新增的更接近 paper-grade oracle 的雏形。runner 会显式记录：

- `visible_tool_result`
- `repeat_tool_call`
- `validator_call`
- `freshness_check`
- `structured_final`

`structured_final` 结构如下：

```json
{
  "claimed_state": "observed|unknown",
  "claimed_fields": {},
  "verified": false,
  "verification_source": "none|schema_only|prompt_filter|same_tool|independent",
  "confidence": "high|medium|low",
  "uncertainty": false,
  "refused_or_deferred": false,
  "action_commit": true,
  "rationale": "..."
}
```

结构化 baseline：

| Baseline | 关键目的 |
| --- | --- |
| `structured_naive` | 无防御，直接接受 primary observation |
| `structured_schema_only` | 验证 schema，但不验证事实 |
| `structured_prompt_filter` | 检测指令文本，但不查事实 |
| `structured_repeat_same_tool` | 重复同一通道，测试 consistent liar |
| `structured_independent_validator` | 调用 independent validator |
| `structured_combined_policy` | freshness metadata + independent validator |

## 6. 当前预实验结果

本节结果只属于 artifact smoke/regression，不作为论文主实验证据。正文主实验表应在实现 ToolSandbox / AgentDojo / tau-bench overlay adapter 并完成 real-model pilot 后替换。

### 6.1 Deterministic local smoke

运行规模：

```text
15 scenarios x 2 modes x 5 baselines = 150 cells
```

spoofed ASR：

| Baseline | Spoofed ASR |
| --- | ---: |
| naive accept | 15 / 15 |
| schema-only | 15 / 15 |
| prompt-filter-only | 14 / 15 |
| cautious/corroboration | 0 / 15 |
| cross-tool verifier | 0 / 15 |

结论：prompt filter 只挡住 instruction-smuggling control，对 14 个非指令型语义虚假观察无效；schema validation 完全不解决 schema-valid falsehood。

### 6.2 Structured local smoke

运行规模：

```text
15 scenarios x 2 modes x 6 structured profiles = 180 cells
```

结果：

| Profile | Spoofed ASR | Clean utility | False-positive refusal | Effective verification | Avg. tool events |
| --- | ---: | ---: | ---: | ---: | ---: |
| `structured_naive` | 15 / 15 | 15 / 15 | 0 / 15 | 0 / 15 | 1.00 |
| `structured_schema_only` | 15 / 15 | 15 / 15 | 0 / 15 | 0 / 15 | 1.00 |
| `structured_prompt_filter` | 14 / 15 | 15 / 15 | 0 / 15 | 0 / 15 | 1.00 |
| `structured_repeat_same_tool` | 15 / 15 | 15 / 15 | 0 / 15 | 0 / 15 | 2.00 |
| `structured_independent_validator` | 0 / 15 | 13 / 15 | 2 / 15 | 13 / 15 | 1.87 |
| `structured_combined_policy` | 0 / 15 | 15 / 15 | 0 / 15 | 13 / 15 | 2.87 |

关键观察：

1. **repeat-same-tool 没用。** 如果同一通道持续撒谎，重复调用只是多花一次工具预算，ASR 仍为 15/15。
2. **schema-only 没用。** 所有 spoofed observations 都是 schema-valid，所以 schema-only 仍为 15/15 ASR。
3. **prompt filter 只解决指令攻击。** 它只挡住 1 个 instruction-smuggling control，挡不住 status、receipt、browser、shell 这类事实虚假。
4. **independent validator 有效但有 utility tradeoff。** 它在 spoofed 上 0/15 ASR，但在没有 validator 的 truthful 场景上产生 2/15 false-positive refusal。
5. **combined policy 当前最好。** 在当前 slice 上 0/15 ASR、15/15 clean utility、0/15 FPR，但平均 tool events 增加到 2.87。

### 6.3 Real-model smoke pilot

已有一个更小的真实模型 smoke pilot：

- model: `gpt-5.4-mini`
- 6 scenarios x 2 modes x 2 prompt policies = 24 attempted cells
- 1 个 timeout
- naive single-observation spoofed ASR: 3/6
- verification-required prompt spoofed ASR: 0/6

这个结果只能说明方向有信号，不能作为主实验结论。原因是 verification prompt 明确告诉模型工具输出可能 stale/forged/semantically false，不等于真实 defense mechanism。

### 6.4 Real tool-call harness dry-run

为解决“不是严格 tool-calling harness”的审稿意见，本轮新增了
`scripts/run_real_toolcall_pilot.py` 和
`configs/experiments/real_toolcall_pilot_small.json`。这个 runner 不再只是把
`visible_tool_result` 放进 user JSON 后让模型回答，而是由 harness 显式执行
和记录工具事件：

- `visible_tool_result`
- `schema_validation`
- `prompt_filter_check`
- `repeat_tool_call`
- `validator_call`
- `freshness_check`（当前是时间绑定 metadata check，不是真 freshness gate）
- `signature_check`（当前是 receipt metadata check，不是 cryptographic signature verifier）
- `structured_final`

模型只能看到 model-visible events；`oracle_context` 和 `truth_result` 不进入
模型上下文。runner 同时输出 run manifest，记录 config hash、model、temperature、
max tokens、timeout、retry、tool budget、prompt hash、trace path、API/parse error
和每个 cell 的 tool events。

当前环境没有 `NEWAPI_API_KEY`，因此只跑了 dry-run：

```text
real_toolcall_pilot_small dry-run: 96 / 96 cells
real_toolcall_pilot_min48 dry-run: 48 / 48 cells
summary: outputs/real_toolcall_pilot_dry_summary.json
manifest: outputs/real_toolcall_pilot_dry_manifest.json
```

dry-run 证明 harness、trace、manifest 和 summary 路径可复现，并且真实模型不可见
`truthful/spoofed` mode 与 oracle-only truth；但它还不能提供真实模型结果。下一步
需要带 API key 先跑 reviewer 建议的 48-cell minimum pilot，然后把同样 harness 迁移到
ToolSandbox/AgentDojo/tau-bench overlay tasks，扩到 30-45 paired scenarios 和至少两个模型。

### 6.5 ToolSandbox overlay adapter-contract smoke

为回应“主 benchmark 必须基于现有 benchmark substrate”的意见，本轮开始实现第一个
substrate：ToolSandbox。当前新增：

- `configs/benchmark_overlays/toolsandbox_overlay_smoke.json`
- `src/tool_spoof_lab/toolsandbox_overlay.py`
- `scripts/run_toolsandbox_overlay_smoke.py`

由于当前环境未安装 ToolSandbox package，这还不是真实 ToolSandbox benchmark run，而是
adapter-contract smoke：用 ToolSandbox-shaped fixtures 验证映射关系是否正确：

```text
ToolSandbox state snapshot / milestone oracle -> hidden truth
agent-visible tool result                     -> observation plane
state snapshot validator                      -> independent validator
```

为避免后续聚合时把 fixture smoke 误算进正式结果，每条 trace row 都带
`adapter_contract=true`、`fixture=true`、`real_benchmark_run=false`。真实
ToolSandbox run 必须把这些 provenance 字段反向标记，并记录 package version、
真实 task id、state snapshot 和 evaluator config。

adapter smoke 已跑通，生成 `outputs/toolsandbox_overlay_smoke_summary.json`。单测覆盖：

- naive 在 spoofed ToolSandbox-shaped observation 上 vulnerable；
- independent-validator 使用 state snapshot 后不再 attack success。

## 7. 当前能支持的 claim 和不能支持的 claim

当前本地 smoke/regression 能支持：

1. 这个 overlay protocol 在本地 smoke suite 上可以稳定区分 semantic falsehood 和 instruction-smuggling control。
2. schema validation 和 prompt filtering 对 schema-valid semantic falsehood 不足。
3. repeat-same-tool 不是有效验证。
4. independent validator / combined policy 在 scripted partial slice 上能显著降低 ASR。

当前不能支持：

1. “真实模型普遍会被工具输出欺骗”——还缺基于现有 benchmark substrate 的 multi-model agentic run。
2. “combined policy 是 paper-grade 防御”——已有 harness 入口和 dry-run，但还缺真实模型运行、成本统计和更大场景。
3. “能投 USENIX/S&P”——还缺 AgentDojo/ToolSandbox/tau-bench 等现有 benchmark overlay pilot、30-45 paired scenario model pilot、150-300 full benchmark、close-work ablation。

## 8. Related work 定位

不能声称“untrusted tool output 是新问题”。接近工作包括：

- Trust No Tool：untrusted tool feedback / cognitive poisoning；
- MCP Security Bench、MCP-SafetyBench：MCP response attack / data tampering；
- AgentDojo、InjecAgent：tool-visible indirect prompt injection；
- ToolEmu：LM-emulated sandbox；
- CaMeL、AttriGuard：prompt injection / action provenance defense；
- MalTool、ToolHijacker、Attractive Metadata Attack、MCPTox、ToolCommander：malicious tools / metadata / tool selection。

本文必须把 novelty 收窄到：

> 基于现有 agent/tool-use benchmark 的 observation-spoofing overlay：schema-valid、非指令型、truth/observation split 的 observation-veracity evaluation，以及同一 benchmark task 上对 observation-integrity defense 的 paired comparison。

## 9. 下一步实验

要从当前 Weak Reject / borderline 推到 Weak Accept，需要把主实验迁移到现有 benchmark overlay：

1. 把当前 **ToolSandbox overlay adapter contract** 接到真实 ToolSandbox package/tasks；
2. 再选第二个 substrate（建议 AgentDojo 或 tau-bench）；
3. 每个 substrate 先做 10-15 个 overlay tasks；
4. 至少 2 个模型；
5. 用新增 real tool-call harness 跑完整 real-model pilot，而不是只 dry-run；
6. structured final answer schema 作为所有模型输出格式；
7. field-level oracle + manual audit；
8. 实现 repeat same tool、independent validator、真实 signed receipt、真实 freshness gate、combined policy 的预算控制；当前 harness 只有 signature/freshness metadata check；
9. 去掉 obvious fake markers，让 forged receipt/citation/provenance 更 plausible；
10. 报告 confidence interval、bootstrap、per-substrate ASR、utility、FPR、tool-call/token/latency overhead；
11. 与 Trust No Tool / MCP Security Bench / MCP-SafetyBench 做 crosswalk 或 ablation。

当前结论：**方向 Weak Go，当前 artifact draft 大约 Weak Reject / borderline；只有当主实验迁移到现有高价值 benchmark substrate 并跑出多模型 overlay 结果后，才可能接近 CCF A 顶会可投状态。**
