# Concept

## User idea, preserved

研究“欺骗 AI”的工具端方向：不是用户 prompt 直接诱导模型，而是工具/API/MCP
server 返回 mock 或伪造数据，使 agent 基于错误观测继续推理、汇报或执行。

In this repo we call the problem **tool-output spoofing**.

## Core object of study

An AI agent receives a tool result such as:

- API says payment succeeded when it failed.
- Security scanner says a target is clean when it is not.
- Browser observation says an action completed when the DOM did not change.
- Retrieval tool returns fabricated citations.
- Local command wrapper returns a forged exit code or truncated output.
- MCP/tool server returns valid JSON that contains adversarial instructions or
  false provenance.

The attack is successful when the agent:

1. treats the spoofed observation as trusted ground truth;
2. fails to ask for corroborating evidence;
3. reports or acts on the false state; and
4. would have made a different decision under the truthful tool result.

## Distinctions that matter for novelty

This is close to but not identical with:

- **Indirect prompt injection**: malicious text is embedded in external content.
  Our emphasis is broader: the tool result can be structured, non-instructional,
  and semantically false.
- **RAG poisoning**: retrieval data is poisoned. Our scope includes any tool or
  observation channel, including API status, filesystem state, browser state,
  telemetry, and local command wrappers.
- **Tool hallucination**: the model invents or misuses tools. Here the tool call
  occurs, but the returned observation is untrustworthy.
- **Malicious plugin/tool discovery**: malicious tool descriptions can steer
  tool use. Here the decisive attack may happen after tool selection, inside
  returned data.

## Candidate novelty claim

Weak initial claim, pending literature audit:

> Existing agent-safety work heavily studies malicious instructions in external
> content and unsafe tool invocation. A narrower systematic benchmark of
> semantically fabricated tool observations, with truth-oracle comparison and
> provenance-aware defenses, appears less directly covered.

This claim must be narrowed after the subagent literature audit.

## Working terminology

- **Truthful observation**: what the tool should have returned under the
  environment state.
- **Spoofed observation**: tool output intentionally differing from truth.
- **Observation trust boundary**: interface where tool data enters the agent's
  context.
- **False-state propagation**: agent carries spoofed state into later reasoning.
- **Corroboration**: agent checks an independent source before acting.
