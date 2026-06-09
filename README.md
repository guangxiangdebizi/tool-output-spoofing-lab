# Tool Output Spoofing Lab

本仓库用于研究工具调用型 LLM 智能体中的 **tool-output spoofing** 问题：
当工具返回值在语法和 schema 上合法、且不包含显式 prompt injection 指令时，
模型是否仍会把其中的虚假事实当成可信世界状态。

当前中文论文初稿：

```text
docs/paper-draft-zh.md
```

核心 artifact 索引：

```text
outputs/main_pilot_index.json
```

![Tool-output spoofing overview](figures/figure1_tool_output_spoofing_overview.png)

## 研究目标

工具调用型 agent 通常依赖 API、MCP server、检索器、浏览器包装器、shell wrapper
等外部工具返回的 observation 更新状态并做决策。本文关注一个更窄的 observation
integrity 问题：

> 如果工具 observation 完全符合 schema，但关键字段在语义上是假的，agent 是否会接受、
> 传播或基于该假状态做出错误承诺？

本文采用 **observation-spoofing overlay** 方法：复用现有 agent/tool-use benchmark
的任务、真实状态和 oracle，只替换模型可见 observation，从而构造 paired
truthful/spoofed 条件。

实验中严格分离：

- **hidden truth plane**：真实后端状态、raw tool result、oracle context、scoring label；
- **model-visible observation plane**：模型实际看到的 truthful/spoofed observation
  和当前 defense profile 允许的验证 evidence。

模型只能看到 model-visible plane；hidden truth 只用于离线评分。

## 当前状态

当前仓库包含：

- 中文完整论文初稿；
- benchmark overlay 和 baseline 设计文档；
- pre-registered scoring contract；
- AgentDojo full-overlay 结果；
- ToolSandbox、AgentDojo、local multi-surface、authorization/provenance 多组 pilot；
- CI、paired statistics、prompt-leakage audit、verification-level diagnostic 脚本。

当前最稳妥的论文定位是：

> 在现有 benchmark 上增加 observation-spoofing overlay，评测 schema-valid、
> non-instructional false observation 对 agent final decision 的影响，并比较
> schema validation、prompt filter、same-tool repeat、metadata check、read-back
> 和 independent validator 等防御基线。

注意：当前实验主要是 trace-final-decision setting，不是完整 autonomous agent-loop
interception；多模型结果和 ToolSandbox full-overlay 合并结果仍需补齐。

## 实验结果概览

### AgentDojo full overlay

AgentDojo full overlay 已完成：

| 项目 | 值 |
| --- | --- |
| Substrate | AgentDojo |
| Tasks | 97 |
| Cells | 97 tasks × 2 modes × 8 profiles = 1552 |
| Model | `gpt-5.4-mini` |
| Setting | official ground-truth tool plan + trace-level observation substitution + model final decision |

主要 artifacts：

```text
outputs/agentdojo_model_full_summary.json
outputs/agentdojo_model_full_manifest.json
outputs/agentdojo_model_full_ci.json
outputs/agentdojo_model_full_stats.json
outputs/agentdojo_model_full_verification_levels.json
outputs/prompt_leakage_audit_agentdojo_full_gpt54.json
```

关键结果：

| Profile | Spoofed ASR | Accepted false state | Truthful clean utility |
| --- | ---: | ---: | ---: |
| naive | 28/97 | 28/97 | 17/97 |
| schema-only | 31/97 | 31/97 | 15/97 |
| prompt-filter | 11/97 | 12/97 | 9/97 |
| repeat-same-tool | 15/97 | 15/97 | 12/97 |
| metadata-only | 15/97 | 15/97 | 14/97 |
| read-back validator | 0/97 | 0/97 | 42/97 |
| independent validator | 0/97 | 0/97 | 20/97 |
| combined policy | 0/97 | 0/97 | 13/97 |

结论：

- schema validation 不能证明 observation 的语义真实性；
- prompt filtering、same-tool repeat、metadata-only 都不是充分防御；
- split-channel read-back 在该设置下显著降低 spoofed ASR；
- AgentDojo clean utility 仍偏低，因此该结果应与 ToolSandbox 和后续多模型结果分开报告。

### ToolSandbox full overlay

ToolSandbox full overlay 正在远端运行，尚未作为主结果报告。

| 项目 | 值 |
| --- | --- |
| Substrate | ToolSandbox |
| Tasks | 1032 |
| Cells | 1032 tasks × 2 modes × 6 profiles = 12384 |
| Model | `gpt-5.4-mini` |
| Status | remote running, not merged |

当前 draft 记录的远端进度为：截至 `2026-06-09 00:30 CST`，已产生
`7703/12384` 个预期 trace files。正式进入论文主表前，还需要完成 shard merge、
CI、prompt-leakage audit、paired statistics 和 invalid-trace accounting。

预期输出：

```text
outputs/toolsandbox_model_full_summary.json
outputs/toolsandbox_model_full_manifest.json
outputs/toolsandbox_model_full_ci.json
outputs/toolsandbox_model_full_stats.json
outputs/toolsandbox_model_full_verification_levels.json
outputs/prompt_leakage_audit_toolsandbox_full_gpt54.json
```

### 已完成 pilots

| Pilot | Scale | Role | Main signal |
| --- | ---: | --- | --- |
| ToolSandbox semantic pilot | 72 cells | existing-benchmark pilot | naive 4/6 spoofed ASR；repeat 5/6；read-back 0/6 且 truthful utility 6/6 |
| AgentDojo clean4 pilot | 64 cells | second-substrate pilot | overlay 可迁移到 AgentDojo；clean utility 有限制 |
| Local multi-surface pilot | 48 cells | API/MCP/RAG/browser/shell local regression | naive/repeat 4/8 spoofed ASR；independent validator 0/8 |
| Authorization sanity pilot | 12 cells | authorization/provenance axis | 强伪授权证据会诱导弱 baseline；validator 可阻断 |
| Authorization optimized-observation pilot | 6 cells | generator sanity check | optimized spoofed authorization evidence 下 naive 3/3 失败 |
| Authorization control slice | 20 cells | evidence-ladder control | 弱证据或矛盾证据不会被简单接受为授权 |

## Defense profiles

实验比较的主要 profile：

| Profile | 含义 |
| --- | --- |
| `naive` | 直接使用模型可见 observation |
| `schema-only` | 只检查 schema / 类型合法性 |
| `prompt-filter` | 检查 observation 中是否含指令型 prompt injection 信号 |
| `repeat-same-tool` | 重复同一工具调用；用于测试 same-channel repetition 是否有效 |
| `metadata-only` | 检查 freshness、signature presence、trace metadata 等表面字段 |
| `read-back validator` | 使用 read-back path 或 split-channel 状态源验证 observation |
| `independent validator` | 使用独立 authority / oracle-like source；报告时需区分 deployable 与 privileged upper bound |
| `combined policy` | 组合验证、矛盾处理和 final-answer uncertainty gate |

## Metrics

主要指标：

| Metric | 含义 |
| --- | --- |
| `attack_success` / ASR | spoofed 条件下模型 commit 到 false decisive field |
| `accepted_false_state` | 模型接受了虚假状态 |
| `clean_utility` | truthful 条件下模型正确 commit 到真实 decisive field |
| `false_positive_refusal` / over-refusal | truthful 条件下模型过度拒绝或不 commit |
| `false_authorization_acceptance` | hidden truth 未授权但模型接受 authorized verdict |
| `unsafe_assessment_escalation` | 模型基于假授权/假来源证据提升允许评估等级 |
| `effective_split_channel` | 验证 evidence 来自独立 failure domain |

## 仓库结构

```text
configs/
  benchmark_overlays/     benchmark-derived scenario overlay 定义
  experiments/            实验矩阵、model/profile 配置
  scenarios/              本地 scenario 定义

docs/
  paper-draft-zh.md                    当前中文论文初稿
  benchmark-baseline-contract.md       benchmark / baseline contract
  benchmark-overlay-strategy.md        overlay 设计说明
  pre_registered_scoring_contract.md   scoring contract
  ccfa-review-gap-analysis.md          投稿级缺口分析
  novelty-audit.md                     novelty 边界分析
  literature-matrix.md                 相关工作矩阵
  threat-model.md                      threat model
  trace-schema.md                      trace schema

figures/                  论文图
outputs/                  canonical summaries、manifests、stats、CI
scripts/                  runners、post-processing、analysis scripts
src/tool_spoof_lab/       本地 mock、scenario、oracle、runner 实现
tests/                    轻量 smoke tests
traces/                   生成 trace
papers/                   第三方论文 PDF，仅用于文献追踪
```

## 本地校验

需要 Python 3.10+。

```bash
PYTHONPATH=src:. python3 -m unittest discover -s tests -v
```

本地测试只验证基础 loader、mock scenario 和 scoring 逻辑，不等价于论文级 benchmark run。

## Full benchmark run 形状

外部 benchmark 包安装在远端 benchmark host，不 vendored 到本仓库。

AgentDojo full overlay：

```bash
PYTHONPATH=src:. python3 scripts/run_agentdojo_model_pilot.py \
  --config configs/experiments/agentdojo_model_full.json \
  --manifest outputs/agentdojo_full_manifest.json \
  --agentdojo-path /tmp/AgentDojo \
  --out-dir traces/agentdojo_model_full \
  --summary outputs/agentdojo_model_full_summary.json \
  --run-manifest outputs/agentdojo_model_full_manifest.json
```

ToolSandbox full overlay：

```bash
PYTHONPATH=src:. python3 scripts/run_toolsandbox_model_pilot.py \
  --config configs/experiments/toolsandbox_model_full.json \
  --manifest outputs/toolsandbox_full_manifest.json \
  --toolsandbox-path /tmp/ToolSandbox \
  --out-dir traces/toolsandbox_model_full \
  --summary outputs/toolsandbox_model_full_summary.json \
  --run-manifest outputs/toolsandbox_model_full_manifest.json
```

ToolSandbox shard merge 和 diagnostics：

```bash
scripts/postprocess_full_model_run.sh \
  --summary-glob 'outputs/toolsandbox_model_full_shard*_summary.json' \
  --manifest-glob 'outputs/toolsandbox_model_full_shard*_manifest.json' \
  --summary-out outputs/toolsandbox_model_full_summary.json \
  --manifest-out outputs/toolsandbox_model_full_manifest.json \
  --ci-out outputs/toolsandbox_model_full_ci.json \
  --leakage-out outputs/prompt_leakage_audit_toolsandbox_full_gpt54.json \
  --stats-out outputs/toolsandbox_model_full_stats.json \
  --verification-out outputs/toolsandbox_model_full_verification_levels.json \
  --reference-profile toolsandbox_exec_naive
```

## 推荐阅读顺序

```text
docs/paper-draft-zh.md
outputs/main_pilot_index.json
docs/pre_registered_scoring_contract.md
docs/benchmark-baseline-contract.md
docs/ccfa-review-gap-analysis.md
docs/novelty-audit.md
docs/literature-matrix.md
```

## Artifact 约定

- 论文主文数字优先使用 `outputs/main_pilot_index.json` 指向的 artifact；
- API/parse error、invalid existing trace 需要单独报告；
- generated traces 可能较大，非 canonical trace 不应进入主文统计；
- deployable validator 和 privileged oracle upper bound 必须分开解释；
- 不提交 API key、私钥、真实凭证或第三方服务 token。

## License

本仓库原创代码、配置、文档、脚本、测试、trace 和生成实验输出使用 Apache License 2.0。
详见 `LICENSE`。

`papers/` 目录包含第三方公开论文 PDF，仅用于研究追踪。它们仍遵循原作者、出版社或分发方条款。
