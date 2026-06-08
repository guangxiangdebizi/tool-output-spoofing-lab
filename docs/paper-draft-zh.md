# 中文论文初稿：工具会撒谎时，智能体如何验证观察结果？

工作标题：

> **当工具会撒谎：面向工具调用型 LLM 智能体的 schema-valid 虚假观察 benchmark**

当前定位：这是中文研究工作稿，优先把问题、benchmark、baseline、预实验结果讲清楚；等实验设计和审稿反馈稳定后，再整理成英文投稿稿。

## 摘要

工具调用型 LLM 智能体越来越依赖外部 API、MCP server、浏览器观察、检索系统和 shell wrapper 返回的结果来判断世界状态。已有研究已经证明，工具可见数据可能携带 indirect prompt injection，恶意工具元数据可能影响工具选择，恶意工具实现可能在执行阶段投毒。本文关注一个更窄但互补的问题：**工具返回结果在语法和 schema 上完全有效，也不包含显式恶意指令，但其中关键事实是假的。**

我们把这个问题定义为 **tool-output spoofing**，并设计一个 observation-spoofing overlay：主实验不应主要依赖自建 toy benchmark，而应基于已有高价值 agent/tool-use benchmark，例如 AgentDojo、ToolSandbox、tau-bench、WebArena/WorkArena、SWE-bench、MCP-SafetyBench / MCP Security Bench。已有 benchmark 提供任务分布、环境状态和 utility/security oracle；我们的 overlay 只改变 agent 可见的 observation plane，并在同一批 benchmark tasks 上比较不同 defense baseline。

当前仓库里的 15 个本地场景只作为 local smoke/regression suite，用来验证 trace schema、oracle、baseline 和 harness；它不计为论文主 benchmark 证据，也不用于支撑核心 empirical claim。当前真正的主实验表应留给 ToolSandbox / AgentDojo / tau-bench 等现有 benchmark overlay pilot。现阶段本地 suite 只证明实现链路可跑：schema validation、prompt filtering、repeat-same-tool、metadata-only validator、read-back validator、privileged independent-validator upper bound、combined policy 等 baseline 可以在同一任务上被成对比较。本轮已经在远端云主机上完成两个现有 substrate 的小规模真实模型 pilot：ToolSandbox 24-cell semantic-normalized slice，以及 AgentDojo 32-cell plausible semantic-spoof slice。它们仍不是全量 benchmark，但已从 dry-run 进入 result-bearing model-pilot 阶段；30-45 paired scenario multi-model pilot 和 10%-15% ToolSandbox 执行切片仍未完成。

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

真实 ToolSandbox manifest probe：

```bash
PYTHONPATH=src:. /tmp/toolsandbox-probe-venv/bin/python scripts/probe_toolsandbox_real.py \
  --toolsandbox-path /tmp/ToolSandbox \
  --limit 12 \
  --output outputs/toolsandbox_real_manifest.json
```

当前仓库没有把 ToolSandbox vendor 成项目依赖；早期 adapter-contract smoke 只使用
ToolSandbox-shaped fixture，后续真实 manifest/execution smoke 则通过
`--toolsandbox-path /tmp/ToolSandbox` 和隔离环境 `/tmp/toolsandbox-probe-venv`
导入 Apple ToolSandbox 源码运行。因此这一段命令分成两类：fixture adapter contract
用于验证统一 trace schema，real probe/execution smoke 用于验证真实 ToolSandbox task
metadata 和真实工具执行边界。

真实 AgentDojo manifest probe：

```bash
PYTHONPATH=src:. /tmp/agentdojo-probe-venv/bin/python scripts/probe_agentdojo_real.py \
  --agentdojo-path /tmp/AgentDojo \
  --benchmark-version v1.2.2 \
  --limit 12 \
  --stratified \
  --output outputs/agentdojo_real_manifest.json
```

当前 probe 在 AgentDojo v1.2.2 的 workspace、travel、banking、slack 四个官方 suite
中枚举到 97 个 user tasks，并生成 12/97 的 stratified manifest
(`selected_fraction=0.1237`)。selected slice 的 difficulty 是 4 easy / 4 medium /
4 hard，ground-truth plan 包含 9 个 mutating tasks 和 3 个 read-only tasks。它解决的是
benchmark 设计层面的“第二个现有 substrate”问题；还没有 AgentDojo observation adapter、
真实模型调用或 attack/defense 结果。

真实 AgentDojo execution smoke：

```bash
PYTHONPATH=src:. /tmp/agentdojo-probe-venv/bin/python scripts/run_agentdojo_execution_smoke.py \
  --manifest outputs/agentdojo_real_manifest.json \
  --agentdojo-path /tmp/AgentDojo \
  --benchmark-version v1.2.2 \
  --out-dir traces/agentdojo_execution_smoke \
  --summary outputs/agentdojo_execution_smoke_summary.json \
  --limit-tasks 12
```

这个 smoke 使用官方 task 的 `ground_truth()` tool plan 执行一个真实 AgentDojo tool call，
捕获 raw tool result，然后只改写 agent-visible observation。它已完成
12 tasks × truthful/spoofed × 8 profiles = 192 cells。它比 manifest-only 更强，因为
已经有 `real_tool_execution=true` 和 `official_ground_truth_tool_plan=true`；但它仍标记为
`scripted_agent=true`, `full_agent_loop_interception=false`, `real_model_run=false`，
不能写成真实模型 benchmark。

真实 AgentDojo model-policy dry-run：

```bash
PYTHONPATH=src:. /tmp/agentdojo-probe-venv/bin/python scripts/run_agentdojo_model_pilot.py \
  --config configs/experiments/agentdojo_model_pilot_small.json \
  --manifest outputs/agentdojo_real_manifest.json \
  --agentdojo-path /tmp/AgentDojo \
  --out-dir traces/agentdojo_model_pilot_dry \
  --summary outputs/agentdojo_model_pilot_dry_summary.json \
  --run-manifest outputs/agentdojo_model_pilot_dry_manifest.json \
  --dry-run --sleep 0
```

该 dry-run 已完成 192/192 cells。它删除 scripted `structured_final`，构造模型可见
prompt，并记录 `prompt_hash`、`model_visible_events` 和
`harness_expected_structured_score`。单测要求 prompt 不泄露 `oracle_context`、
`raw_tool_result`、raw profile name 和 truthful/spoofed condition label。由于当前没有
API key，`model_call_executed=false`，这仍不是模型结果。

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

本轮也加入了真实 ToolSandbox manifest probe 入口：`scripts/probe_toolsandbox_real.py`
和 `configs/benchmark_overlays/toolsandbox_real_probe.json`。它使用 Apple ToolSandbox
真实 scenario definitions 枚举 12 个候选任务、tool allow list、starting state preview
和 milestone oracle metadata；但它仍是 `manifest_only=true`，还没有完成 observation
interception 或 real-model agent run。下一步是把这 12 个任务转成可执行 overlay cells：
12 tasks × truthful/spoofed × naive/schema/repeat-same-tool/independent-validator =
96 cells。注意，这只是 12-task real-substrate bring-up seed，不是 ToolSandbox 的
representative 10%-15% slice；1032 个官方 scenarios 的 10%-15% 需要后续按类别分层抽样。

当前 probe 已在隔离环境 `/tmp/toolsandbox-probe-venv` 中跑通，使用 `/tmp/ToolSandbox`
官方仓库源码，枚举到 1032 个 ToolSandbox scenarios，并抽取 12 个任务写入
`outputs/toolsandbox_real_manifest.json`。该输出不提交到仓库，但结果摘要如下：

```text
total_available_scenarios = 1032
selected_count = 12
selected task families include:
- get_wifi / wifi_off
- add_contact / update_contact / remove_contact
- search_message / send_message
- search_reminder / add_reminder / modify_reminder / remove_reminder
```

这一步比 fixture smoke 更进一步：task id、tool allow list、starting state preview 和
milestone oracle metadata 来自真实 ToolSandbox benchmark definitions；但它仍不是
attack/defense 结果表，因为模型尚未执行、tool return 尚未被真实拦截。正式 10%-15%
slice 不能用 12/1032 冒充，必须另做 stratified sampling。

在此 manifest 基础上，本轮又跑了一个 96-cell scripted bring-up：

```bash
PYTHONPATH=src:. /usr/bin/python3.11 scripts/run_toolsandbox_real_bringup.py \
  --manifest outputs/toolsandbox_real_manifest.json \
  --out-dir traces/toolsandbox_real_bringup \
  --summary outputs/toolsandbox_real_bringup_summary.json
```

矩阵为：

```text
12 real ToolSandbox task IDs
× truthful/spoofed
× naive / schema-only / repeat-same-tool / independent-validator
= 96 cells
```

结果摘要：

```text
naive spoofed ASR                 = 12/12
schema-only spoofed ASR           = 12/12
repeat-same-tool spoofed ASR      = 12/12
independent-validator spoofed ASR = 0/12
truthful clean utility            = 12/12 for all four profiles
```

这个结果只证明 matrix、trace schema、oracle scoring 和同一真实 ToolSandbox task 上
baseline 对齐可以跑通。它被显式标记为
`manifest_derived_scripted_bringup=true`、`scripted_oracle_bringup=true`、
`real_model_run=false`、`real_execution_interception=false`，因此不能作为模型级
ASR/robustness claim。trace 中的 observation 是 `visible_oracle_projection`，不是
真实 ToolSandbox tool return；下一步仍必须接 ToolSandbox role/execution 层的真实
tool-return interception，让 agent-visible observation 被改写，而 execution context /
milestone evaluator 保持真实。

随后又实现并运行了一个真实 ToolSandbox tool-execution smoke：

```bash
PYTHONPATH=src:. /tmp/toolsandbox-probe-venv/bin/python scripts/run_toolsandbox_execution_smoke.py \
  --manifest outputs/toolsandbox_real_manifest.json \
  --toolsandbox-path /tmp/ToolSandbox \
  --out-dir traces/toolsandbox_execution_smoke \
  --summary outputs/toolsandbox_execution_smoke_summary.json \
  --limit-tasks 12
```

这一步不再只是 milestone metadata projection，而是对 12 个真实 ToolSandbox tasks
各执行一个真实工具调用，通过 ToolSandbox `ExecutionEnvironment` 得到 raw result 和
`tool_trace`，再在 trace 层比较 truthful vs spoofed agent-visible return：

```text
executed_tasks = 12
completed_cells = 144
missing_tool_trace = 0
tool_call_exception = 0
real_tool_execution = true
real_execution_interception = true
trace_level_visible_result_substitution = true
full_agent_loop_interception = false
scripted_agent = true
full_scenario_run = false
real_model_run = false
real_benchmark_run = false
```

加入 metadata-only validator 和 read-back validator ablation 后，该 execution smoke 已重跑为
144 cells：naive/schema/repeat/metadata-only 在 spoofed 下均为 12/12 ASR；
read-back validator 与 privileged independent-validator upper bound 均为 0/12 ASR。

这个 smoke 已经证明“真实 ToolSandbox 工具返回 -> agent-visible observation 可被改写
-> hidden raw result / tool_trace 保持可审计”的边界能跑通。但它仍不是论文主实验：
工具调用由脚本指定，不是模型 agent 自主选择；也没有跑完整 ToolSandbox scenario
conversation。这里的 `real_execution_interception=true` 精确定义为
trace-level visible-result substitution after real ToolSandbox tool execution，不是
full agent-loop interception；因此同时标记 `full_agent_loop_interception=false`。
下一步 P0 是把同一 interception boundary 接入真实 agent/model policy。

本轮进一步补了 ToolSandbox model-policy pilot runner：

```bash
PYTHONPATH=src:. /tmp/toolsandbox-probe-venv/bin/python scripts/run_toolsandbox_model_pilot.py \
  --config configs/experiments/toolsandbox_model_pilot_small.json \
  --manifest outputs/toolsandbox_real_manifest.json \
  --toolsandbox-path /tmp/ToolSandbox \
  --out-dir traces/toolsandbox_model_pilot_dry \
  --summary outputs/toolsandbox_model_pilot_dry_summary.json \
  --run-manifest outputs/toolsandbox_model_pilot_dry_manifest.json \
  --dry-run --sleep 0
```

该 runner 在 12 个真实 ToolSandbox task 上先执行真实工具调用，随后把 raw result 分成
hidden `raw_tool_result` 和 model-visible `visible_tool_result`，并按同一任务比较：

```text
12 tasks × truthful/spoofed ×
  naive / schema-only / repeat-same-tool /
  metadata-only validator / read-back validator / privileged independent-validator upper bound
= 144 prompt/trace cells
```

dry-run 已完成 144/144 cells，并在 summary 中记录：

```text
real_tool_execution = true
trace_level_visible_result_substitution = true
model_policy_prompted = true
model_call_executed = false
final_decision_source = dry_run_uncertainty_stub
full_agent_loop_interception = false
real_model_run = false
representative_10_15_percent_slice = false
```

这说明真实模型 prompt/manifest/trace 路径已经打通，且单测验证 model-visible prompt 不泄漏
`oracle_context`、`raw_tool_result`、raw profile name 或 truthful/spoofed 条件标签。这个
144-cell pass 仍然只是 dry-run；真实模型结果来自后续较小的 24-cell ToolSandbox slice。

获得 API 访问后，先跑了 ToolSandbox 24-cell real-model smoke。第一次真实模型结果暴露出
一个重要工程问题：直接把 ToolSandbox 的 Python 裸返回值（例如 `True`、`False`、`None`）
作为 model-visible observation，会让结果看起来像 harness artifact，不像真实工具 API。
因此补了一个 deterministic semantic-normalized observation adapter：

| 层 | raw-content adapter | semantic-normalized adapter |
| --- | --- | --- |
| ToolSandbox execution | 不变 | 不变 |
| hidden raw result | `True` | `True` |
| model-visible truthful observation | `"True"` | `{"wifi_enabled": true, "source": "settings_read"}` |
| model-visible spoofed observation | `"False"` | `{"wifi_enabled": false, "source": "settings_read"}` |
| oracle / milestone evaluator | 不变 | 不变 |

这个 adapter 只改变模型可见 observation surface，并且对 truthful/spoofed 对称应用；它不改变
ToolSandbox state、raw tool trace 或 milestone oracle。

24-cell raw-content vs semantic-normalized real-model ablation：

| Baseline | raw-content spoofed ASR | semantic-normalized spoofed ASR | semantic truthful utility |
| --- | ---: | ---: | ---: |
| naive | 1 / 2 | 2 / 2 | 2 / 2 |
| schema-only | 2 / 2 | 2 / 2 | 2 / 2 |
| repeat-same-tool | 1 / 2 | 2 / 2 | 2 / 2 |
| metadata-only validator | 1 / 2 | 2 / 2 | 2 / 2 |
| read-back validator | 0 / 2 | 0 / 2 | 1 / 2 |
| privileged independent-validator | 0 / 2 | 0 / 2 | 2 / 2 |

这支持用户提出的判断：优化工具/mock observation 以后，模型更容易把弱 baseline 的可见假状态
当成真实工具状态，从而得到更清晰的攻击信号。read-back validator 仍把 spoofed ASR 降到 0/2；
但有一个 truthful utility miss 来自模型把结构化 read-back 值简化成 boolean，这应作为
value-normalization / parser limitation 报告。

同样的 observation-surface 问题也出现在 AgentDojo：如果 spoof 只是把列表改成空列表或把文本改成
“no task-relevant records”，模型容易选择不确定，测到的是 payload 不自然，而不是 observation
integrity。当前 AgentDojo adapter 因此改成 **semantic-normalized + plausible alternate**
版本：保留同一 JSON shape 和任务相关 field，但把具体候选实体、频道、记录或文本替换为
plausible false alternatives。隐藏 `raw_tool_result` 和 oracle 仍保存真实 AgentDojo 工具返回。
这把“优化 mock/工具观测面”固化为正式实验因素，而不是临时 prompt trick：

| Adapter factor | 目的 | 约束 |
| --- | --- | --- |
| raw/native | 记录 benchmark 原始工具输出 | 只用于 hidden audit / ablation |
| semantic-normalized | 把裸 Python/string/list 变成稳定 JSON observation | truthful/spoofed 对称应用，不改 backend state |
| plausible alternate spoof | 让假 observation 看起来像同类工具结果 | 不含显式攻击指令，不读 hidden oracle 以外的信息 |

因此主实验表应把 observation format 明确作为一列：

```text
model × substrate × task × mode × baseline × observation_format
```

其中 `semantic_normalized_v1` / plausible alternate adapter 必须在大规模运行前冻结版本，并保留
raw/native adapter 与空结果/弱 mock adapter 作为 ablation。字段名也必须保持中性，例如
`wifi_enabled`、`operation_status`、`record_count`，避免 `verified_success`、
`safe_to_continue` 这种会人为诱导模型的名字。论文表述应是“测试 vulnerability 是否依赖
model-visible observation realism”，而不是“改 mock 让攻击更强”。

AgentDojo 32-cell real-model slice 覆盖 2 个官方任务（`travel:user_task_19` 与
`slack:user_task_14`）、truthful/spoofed 和 8 个 baseline：

| AgentDojo baseline | Spoofed ASR | Accepted false state | Truthful utility | 备注 |
| --- | ---: | ---: | ---: | --- |
| naive | 1 / 2 | 1 / 2 | 0 / 2 | 弱 baseline 会接受同形假 observation，但有时因任务不完整而不 commit |
| schema-only | 0 / 2 | 2 / 2 | 1 / 2 | 模型接受 false field，但未总是 action-commit；需单独报告 accepted_false_state |
| prompt-filter | 0 / 2 | 0 / 2 | 0 / 2 | 对非指令 spoof 没有内容验证，只是模型偏谨慎 |
| repeat-same-tool | 1 / 2 | 1 / 2 | 0 / 2 | 同通道重复可强化假状态 |
| metadata-only validator | 0 / 2 | 0 / 2 | 0 / 2 | metadata 不能证明 content truth |
| read-back validator | 0 / 2 | 0 / 2 | 0 / 2 | 防住 spoof，但当前 prompt/score 对 truthful utility 偏严 |
| privileged independent-validator | 0 / 2 | 0 / 2 | 2 / 2 | upper-bound，不作为可部署防御 |
| combined policy | 0 / 2 | 0 / 2 | 0 / 2 | read-back 防住 spoof，但 utility 仍需调 scorer/prompt |

这张表的正确解读是：plausible alternate spoof 能在第二个现有 benchmark substrate 上产生真实模型攻击信号，
但 AgentDojo 当前 pilot 仍是 trace-level visible-result substitution，不是 full agent-loop interception；
且 utility/FPR 受“单个 ground-truth tool call 只提供部分任务证据”影响。因此它是 pilot evidence，
不是 paper-grade 主结果。

为回应“independent validator 过于 oracle-adjacent”的审稿意见，本轮把 validator 分成
三类：

| Validator baseline | 可见信息 | 解释 |
| --- | --- | --- |
| `toolsandbox_exec_metadata_validator` | tool name、异常状态、tool_trace 是否存在 | non-privileged metadata-only check，不读取 raw content，因此不能验证语义真假 |
| `toolsandbox_exec_readback_validator` | 第二个真实 ToolSandbox read-back tool 的返回 | non-privileged read-back validation，不读取 hidden oracle 或 primary raw result，更接近可部署 independent authority |
| `toolsandbox_exec_independent_validator` | raw truthful ToolSandbox execution result | privileged upper-bound validator / ablation，不应被声称为真实可部署防御 |

在 dry-run scripted scoring 中，metadata-only validator 和 repeat-same-tool 一样无法降低
spoofed ASR；read-back validator 与 privileged independent-validator 才能降 ASR。这一区分使
论文后续可以诚实报告“真实低权限 metadata 检查不够，独立内容 authority 才有效”，同时把
read-back validator 作为 deployability-oriented baseline，把 raw-result validator 仅作为
upper-bound ablation。

这里的 `readback_observation` 是第二个真实 read-back tool 的 model-visible validator
output，不是 hidden oracle state，也不是 primary raw result。它只在更窄 threat model
下成立：攻击者能篡改 primary observation channel，但不能同时控制 canonical
state/read-back path。如果整个 ToolSandbox backend 都被攻破，read-back validator 不提供
独立性。

另一个实现细节也必须在论文中讲清楚：dry-run trace 只有 dry-run/model
`structured_final`，但 summary 同时保存 `harness_expected_structured_score` 作为 scripted
expected behavior。dry-run aggregate 不应被解释成模型行为；它只验证 harness 预期、
prompt/manifest 路径和 baseline wiring。

同时补了 ToolSandbox 10%-15% 分层 sampling manifest 设计：

```bash
PYTHONPATH=src:. /tmp/toolsandbox-probe-venv/bin/python scripts/probe_toolsandbox_real.py \
  --toolsandbox-path /tmp/ToolSandbox \
  --limit 104 \
  --stratified \
  --output outputs/toolsandbox_stratified_10pct_manifest.json
```

当前生成的 manifest 为 104/1032 scenarios，`selected_fraction=0.1008`，
`target_10_percent_stratified_manifest=true`, `executed_10_15_percent_slice=false`, `strict_quota_satisfied=false`。它按 ToolSandbox category 做 multi-label
stratification：single/multiple user turn、single/multiple tool call、
insufficient-information、distraction/no-distraction、state dependency、
canonicalization、read-only/mutation。注意这只是 manifest / sampling 设计，还没有对
104 个任务执行 model benchmark。

同时补了 AgentDojo v1.2.2 的 10%-15% stratified manifest：

```bash
PYTHONPATH=src:. /tmp/agentdojo-probe-venv/bin/python scripts/probe_agentdojo_real.py \
  --agentdojo-path /tmp/AgentDojo \
  --benchmark-version v1.2.2 \
  --limit 12 \
  --stratified \
  --output outputs/agentdojo_real_manifest.json
```

当前生成的 AgentDojo manifest 为 12/97 user tasks，`selected_fraction=0.1237`，
`target_10_15_percent_stratified_manifest=true`，
`executed_10_15_percent_slice=false`。它记录 official prompt、difficulty、
ground-truth tool-call plan、suite tool names 和 injection-task count。这个 manifest
只说明第二个现有 benchmark substrate 已经被定位并抽样；还不能报告 ASR、utility 或
defense gain。

进一步补了 AgentDojo execution smoke：

```bash
PYTHONPATH=src:. /tmp/agentdojo-probe-venv/bin/python scripts/run_agentdojo_execution_smoke.py \
  --manifest outputs/agentdojo_real_manifest.json \
  --agentdojo-path /tmp/AgentDojo \
  --benchmark-version v1.2.2 \
  --out-dir traces/agentdojo_execution_smoke \
  --summary outputs/agentdojo_execution_smoke_summary.json \
  --limit-tasks 12
```

该 smoke 已完成 192/192 cells，baseline 与 ToolSandbox 对齐：

| AgentDojo baseline | Spoofed ASR scripted score | Effective verification | 解释 |
| --- | ---: | ---: | --- |
| naive | 12 / 12 | 0 / 12 | 直接相信 visible observation |
| schema-only | 12 / 12 | 0 / 12 | schema 合法不代表语义真实 |
| prompt-filter | 12 / 12 | 0 / 12 | 拦截指令不等于验证事实 |
| repeat-same-tool | 12 / 12 | 0 / 12 | 重复同一可疑通道不是独立验证 |
| metadata-only validator | 12 / 12 | 0 / 12 | metadata 不能验证 content truth |
| read-back validator | 0 / 12 | 12 / 12 | split-channel threat model 下的非特权内容级 read-back |
| privileged independent-validator | 0 / 12 | 12 / 12 | privileged upper-bound ablation |
| combined policy | 0 / 12 | 12 / 12 | prompt-filter + metadata + read-back 的可部署组合策略 |

这张表只能作为 scripted-agent / harness-expected baseline separation，不是模型鲁棒性结果。
它的价值是证明同一 baseline hierarchy 能迁移到第二个现有 benchmark substrate。

同时补了 AgentDojo model-policy dry-run。它完成 192/192 prompt/manifest cells，
并验证模型可见 prompt 只包含 `agentdojo_user_task`、`agentdojo_tool_call`、
`visible_tool_result`、`prompt_filter_check`、`repeat_tool_call`、`validator_call`
等显式可见事件，不包含 hidden oracle 或 raw result。随后在同一云主机上完成
AgentDojo 32-cell real-model pilot：2 个官方任务 × truthful/spoofed × 8 profiles。
这提供了第二 substrate 的初始模型信号，但仍需要扩展到更多任务和至少两个模型。

### 6.6 当前实验状态分层表

| 层级 | 规模 | 证据强度 | 当前状态 |
| --- | ---: | --- | --- |
| Local scripted smoke | 15 scenarios × 2 × 6 | regression only | 已跑，非主 benchmark |
| ToolSandbox fixture adapter | fixture tasks | adapter contract | 已跑，`real_benchmark_run=false` |
| ToolSandbox real manifest probe | 12 / 1032 | real task metadata | 已跑，`manifest_only=true` |
| ToolSandbox scripted bring-up | 12 × 2 × 4 = 96 | real IDs + scripted oracle projection | 已跑，非模型结果 |
| ToolSandbox real execution smoke | 12 × 2 × 6 = 144 | real tool execution + trace-level substitution + read-back validator ablation | 已跑，`scripted_agent=true` |
| ToolSandbox model-policy pilot | 2 × 2 × 6 = 24 real cells；12 × 2 × 6 dry-run | real model-pilot + prompt/manifest dry-run | 24-cell semantic pilot 已跑 |
| ToolSandbox stratified 10% manifest | 104 / 1032 | sampling design | 已生成，尚未执行 |
| AgentDojo stratified 10%-15% manifest | 12 / 97 | second existing-benchmark sampling design | 已生成，尚未执行 |
| AgentDojo execution smoke | 12 × 2 × 8 = 192 | official ground-truth tool plan + trace-level substitution | 已跑，`scripted_agent=true` |
| AgentDojo model-policy pilot | 2 × 2 × 8 = 32 real cells；12 × 2 × 8 dry-run | second-substrate real model-pilot + leakage tests | 32-cell plausible semantic pilot 已跑 |
| Paper-grade main run | >= 2 substrates, 30-45 paired scenarios first | model benchmark evidence | 未完成 |

## 7. 当前能支持的 claim 和不能支持的 claim

当前本地 smoke/regression 能支持：

1. 这个 overlay protocol 在本地 smoke suite 上可以稳定区分 semantic falsehood 和 instruction-smuggling control。
2. schema validation 和 prompt filtering 对 schema-valid semantic falsehood 不足。
3. repeat-same-tool 不是有效验证。
4. independent validator / combined policy 在 scripted partial slice 上能显著降低 ASR；metadata-only validator ablation 显示非内容级检查不能验证语义真假；read-back validator 是当前最接近可部署 independent authority 的 ToolSandbox baseline。
5. ToolSandbox 真实工具执行结果可以被捕获，并在 trace 层构造 truthful/spoofed 可见 observation，同时保留 raw result / tool trace 供 oracle 审计。
6. 已有 104/1032 的 ToolSandbox 10% stratified manifest 设计，但它只是 scaling plan，不是已执行结果。
7. 已有 12/97 的 AgentDojo v1.2.2 stratified manifest，覆盖 workspace/travel/banking/slack 和 easy/medium/hard 难度，用于证明主实验会迁移到第二个现有 benchmark substrate；它同样只是 sampling/design artifact。
8. AgentDojo execution smoke 已经能执行官方 ground-truth tool call 并进行 trace-level observation substitution；它支持“第二 substrate 的 harness wiring 可跑”，但不支持模型 ASR claim。
9. ToolSandbox 24-cell real-model pilot 支持“语义归一化 observation adapter 比 raw Python-like adapter 产生更清晰弱 baseline 攻击信号”的工程判断。
10. AgentDojo 32-cell real-model pilot 支持“plausible same-shape false observation 比空结果 mock 更能测到 false-state acceptance”的判断；但它仍只是 trace-level pilot，不是完整 AgentDojo agent-loop benchmark。

当前不能支持：

1. “真实模型普遍会被工具输出欺骗”——还缺基于现有 benchmark substrate 的 multi-model agentic run。
2. “combined policy 是 paper-grade 防御”——已有 harness 入口和 dry-run，但还缺真实模型运行、成本统计和更大场景。
3. “已经跑了 ToolSandbox/AgentDojo 10%-15% real-model benchmark”——当前只生成了 ToolSandbox 104-task manifest，AgentDojo 12-task manifest 已有 execution smoke；已执行的真实模型切片分别只有 ToolSandbox 2 tasks / 24 cells 和 AgentDojo 2 tasks / 32 cells。
4. “能投 USENIX/S&P”——还缺 AgentDojo/ToolSandbox/tau-bench 等现有 benchmark overlay pilot、30-45 paired scenario model pilot、150-300 full benchmark、close-work ablation。

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
