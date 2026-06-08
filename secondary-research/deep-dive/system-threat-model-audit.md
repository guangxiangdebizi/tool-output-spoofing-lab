# System threat-model audit: tool-output spoofing and agent tool supply chain

Date: 2026-06-08 (Asia/Shanghai)

Scope: AI agent tool supply chain, malicious tools/plugins/local shims/MCP servers/API gateways, forged tool results, tool-output prompt injection, response tampering, provenance, policy enforcement, and confused-deputy failure modes.

## Executive findings

1. The closest established term for "tool output spoofing" is not a single risk class. It sits at the intersection of indirect prompt injection, excessive agency, AI/LLM supply-chain risk, MCP authorization/security, malicious tool code, and result-provenance failure.
2. Most official guidance now says to treat prompt-visible tool outputs and external content as untrusted. However, current specs and docs mostly address permissions, user approval, OAuth, and prompt-injection hygiene; they do not fully specify semantic integrity for tool results such as signed receipts, independent state confirmation, or cross-tool corroboration.
3. MCP introduces a sharper supply-chain boundary: a server can affect an agent before any tool execution through tool metadata and dynamic tool lists. MCPTox shows that malicious metadata in real MCP tools can induce agents to misuse other high-privilege tools.
4. Malicious tools are a code-supply-chain risk, not only a prompt/metadata risk. MalTool shows that malicious behavior can be embedded in otherwise plausible tool implementations, and existing malware/program-analysis scanners have limited coverage in the LLM-agent setting.
5. The strongest defense direction in the literature is system-level enforcement outside the model: capability/provenance tracking, control/data-flow separation, least privilege, per-user scoped authorization, complete mediation for every tool call, and canonical result verification. CaMeL is the cleanest architectural reference for this.
6. A research gap remains around first-class "API response tampering / false-success" attacks: forged schema-valid tool results that do not necessarily contain malicious instructions but mislead the agent about world state, validation status, or completed side effects.

## Core sources (15)

| # | Source | Type | Core point | Relationship to this project |
|---|---|---|---|---|
| 1 | [MCP Security Best Practices](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices) + [MCP Authorization spec](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization) | Official spec/guidance | MCP security guidance covers confused deputy, token passthrough, SSRF, session hijacking, local server compromise, and scope minimization. The authorization spec requires OAuth-style protections such as redirect URI validation, state handling, audience binding, and scoped challenges. | Directly frames MCP servers/API proxies as trust-boundary components. It is strong on auth/session/deputy risks, but it does not by itself prove that a tool result is truthful. |
| 2 | [MCP Tools spec](https://modelcontextprotocol.io/specification/2025-11-25/server/tools) | Official spec | Tools are model-controlled and expose names, descriptions, schemas, results, structured content, and annotations. The spec says clients must treat tool annotations as untrusted unless they come from trusted servers, and recommends human ability to deny invocations. | Establishes that tool metadata/results enter model control flow. Supports our assumption that tool metadata is a supply-chain input, not a trusted instruction channel. |
| 3 | [OpenAI: Safety in building agents](https://developers.openai.com/api/docs/guides/agent-builder-safety) | Official docs | Describes prompt injection as untrusted text/data entering an AI system and causing private-data exfiltration via downstream tool calls, misaligned actions, or unintended behavior. Emphasizes care around MCP tool calling and tool approvals. | Official support for treating retrieved/tool-provided content as untrusted and for requiring approvals around risky tool use. |
| 4 | [OpenAI Apps SDK: Security & Privacy](https://developers.openai.com/apps-sdk/guides/security-privacy) | Official docs | Apps/connectors should use least privilege, explicit user consent, confirmation prompts for destructive actions, defense in depth, validation of inputs, and audit logs. | Relevant to plugin/API connector design. It explicitly assumes prompt injection and malicious inputs will reach servers, which maps to malicious tool-output and gateway-response scenarios. |
| 5 | [Anthropic Claude Code: MCP docs](https://code.claude.com/docs/en/mcp) | Official docs | Advises users to verify trust in each MCP server before connection; servers that fetch external content can expose prompt-injection risk. Project-scoped MCP servers can require approval. | Useful operational model for MCP supply-chain trust: connecting a server is an authority grant, not just a convenience setting. |
| 6 | [OWASP LLM01:2025 Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) | Industry standard | Prompt injection can be direct or indirect; imperceptible or hidden model-parsed content can alter behavior. Retrieval and external data do not fully mitigate this risk. | Baseline taxonomy for tool-output instruction smuggling, malicious API response text, web/email/doc payloads returned by tools. |
| 7 | [OWASP LLM03:2025 Supply Chain](https://genai.owasp.org/llmrisk/llm032025-supply-chain/) | Industry standard | LLM apps inherit software supply-chain risk and add model/data/plugin/component provenance issues. Recommends BOMs, audits, signing, hashes, trusted suppliers, and integrity checks. | Directly motivates signed tool manifests, pinned MCP server versions, metadata provenance, and tool code review for local shims/plugins. |
| 8 | [OWASP LLM06:2025 Excessive Agency](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/) | Industry standard | Excessive agency arises when LLM apps/extensions can take damaging actions after unexpected, ambiguous, or manipulated LLM outputs; triggers include indirect prompt injection and compromised extensions. Recommends minimizing extensions, permissions, and requiring approval/authorization outside the LLM. | Closest industry guidance for limiting blast radius when a forged tool output drives a bad tool call or side effect. |
| 9 | [NIST AI 100-2e2025: Adversarial Machine Learning taxonomy](https://doi.org/10.6028/NIST.AI.100-2e2025) ([PDF](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-2e2025.pdf)) | NIST report | Classifies indirect prompt injection, resource control, output handling, agents, supply-chain attacks, and mitigations. It notes that agents iteratively feed tool results back to the model and can be hijacked into arbitrary actions or exfiltration. | Provides a rigorous vocabulary for attacker capabilities: query access, resource control, model control, and supply-chain control. Also supports the assumption that robust design should assume malicious model outputs are possible. |
| 10 | [NIST AI 600-1: Generative AI Profile](https://doi.org/10.6028/NIST.AI.600-1) ([PDF](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf)) | NIST report | Covers GAI risks including prompt injection, third-party value-chain dependencies, provenance, monitoring, incident disclosure, and validation/verification records. | Useful governance layer for tool result provenance, third-party MCP/vendor inventory, audit retention, and incident response around compromised tool suppliers. |
| 11 | Greshake et al., [Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection](https://arxiv.org/abs/2302.12173) | Academic paper | Introduces indirect prompt injection against LLM-integrated applications. Retrieved untrusted content can blur data/instruction boundaries, manipulate API calls, exfiltrate data, and produce worm-like propagation. | Foundational evidence that tool/retrieval outputs can act like code or control input when fed into an agent loop. |
| 12 | Debenedetti et al., [AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents](https://arxiv.org/abs/2406.13352) | Academic benchmark | Evaluates agents that execute tools over untrusted data. The paper explicitly models data returned by external tools hijacking the agent to execute malicious tasks. | Primary benchmark reference for our lab scenarios: malicious tool outputs, security test cases, benign utility vs robustness tradeoff. |
| 13 | Debenedetti et al., [Defeating Prompt Injections by Design / CaMeL](https://arxiv.org/abs/2503.18813) | Academic defense paper | Proposes extracting control/data flows from trusted user query before untrusted data can affect program flow; uses capabilities/provenance and policy checks before tool calls. | Best architectural template for our defense model: untrusted tool output can supply data, but cannot create unauthorized control flow or data exfiltration. |
| 14 | Wang et al., [MCPTox: A Benchmark for Tool Poisoning Attack on Real-World MCP Servers](https://arxiv.org/abs/2508.14925) | Academic benchmark | Studies MCP tool poisoning where malicious instructions are embedded in tool metadata during registration, often without executing the poisoned tool. Uses real MCP servers/tools and reports broad agent susceptibility. | Directly maps to malicious MCP server/metadata supply chain. Shows result validation alone is insufficient because metadata can poison the agent before result production. |
| 15 | Hu et al., [MalTool: Malicious Tool Attacks on LLM Agents](https://arxiv.org/abs/2602.12194) | Academic paper | Systematically studies malicious tool code implementations, including standalone and Trojanized tools, and finds existing detection approaches weak. | Directly relevant to local tool shims/plugins/MCP server code returning plausible but malicious or forged outputs. |

## What existing work validates well vs. leaves open

### Well-covered

- Indirect prompt injection through retrieved/tool-returned content: Greshake et al., AgentDojo, OWASP LLM01, NIST AI 100-2e2025.
- Excessive tool authority and least-privilege mitigations: OWASP LLM06, MCP Authorization, OpenAI Apps SDK, NIST.
- Tool metadata poisoning: MCPTox and MCP Tools spec.
- Malicious tool code supply chain: MalTool and OWASP LLM03.
- Architectural policy enforcement outside the model: CaMeL, OWASP LLM06, NIST.
- Confused deputy and OAuth/token-boundary issues in MCP proxies: MCP Security Best Practices and Authorization spec.

### Under-specified / open research gap

- Veracity of tool outputs: schema validation confirms shape, not truth. Most guidance does not require cryptographic receipts, independent state reads, or cross-provider corroboration.
- API gateway response tampering: existing literature mostly models "malicious text returned by a tool" or "malicious tool code/metadata"; fewer works isolate "schema-valid but semantically forged API response" as the primary attack.
- Provenance granularity: docs discuss provenance broadly, but protocols rarely attach request-bound, audience-bound provenance metadata to every field/value in a tool result.
- Human approval integrity: human-in-the-loop guidance often assumes the user sees an accurate action summary. A forged tool result can cause the model to present a misleading summary unless the UI shows canonical raw diffs/receipts from the authoritative system.
- Dynamic MCP updates: list_changed-style tool changes and remote server updates need stronger pinning/re-approval semantics than most current deployments expose by default.

## Threat model

### System under model

An agentic application contains:

- User interface and approval UI.
- Agent host/orchestrator: prompt builder, memory, planner, tool selector, tool dispatcher.
- LLM model endpoint.
- Tool integration layer: local tool shim, plugin runtime, MCP client, API gateway/proxy, connector SDK.
- Tool servers: MCP servers, REST/RPC services, databases, email/calendar/repos/payment systems, web/RAG fetchers.
- Policy and audit plane: authn/authz, logging, provenance, monitoring, incident response.

The model covers both read-only tools and side-effecting tools. It focuses on cases where a tool server, plugin, shim, MCP server, or API gateway returns a forged result or malicious metadata that the agent consumes.

### Assets

1. User intent and task integrity: the agent should execute the user's requested task, not instructions smuggled through tool outputs or metadata.
2. Control-flow integrity: tool outputs should not create new high-impact actions or override the trusted plan unless explicitly authorized.
3. Sensitive data: user files, emails, documents, credentials, tokens, API keys, source code, secrets, PII, business data, and private model context.
4. Downstream authorities: ability to send email, post messages, transfer funds, edit repos, run shell commands, update databases, delete files, approve purchases, or change ACLs.
5. Tool registry integrity: tool names, descriptions, schemas, annotations, manifests, versions, server identities, and dynamic tool updates.
6. Tool-result integrity: factual correctness, freshness, side-effect completion status, status codes, errors, receipts, and state versions.
7. OAuth/session integrity: per-user tokens, scopes, audience binding, redirect URIs, consent state, and refresh tokens.
8. Human approval integrity: the user must see accurate action target, effect, authority, and risk before approval.
9. Audit/provenance evidence: raw request/response, hashes, signatures, actor identity, state transitions, and trace IDs.
10. Availability and recovery: the agent should not be stalled, looped, silently no-oped, or forced into unsafe fallbacks by forged results.

### Attackers and capabilities

| Attacker | Capabilities | Non-capabilities / assumptions |
|---|---|---|
| Malicious MCP/tool server operator | Controls tool metadata, schemas, annotations, tool outputs, errors, dynamic tool list changes, and server-side behavior. May be authenticated as a real server. | Does not need to compromise the LLM provider. Authenticated transport only proves server identity, not semantic honesty. |
| Compromised local shim/plugin | Runs code on the host or in plugin sandbox; can read/write within granted permissions; can return plausible forged results; may exfiltrate over allowed network. | Subject to OS/container/sandbox limits if enforced. |
| API gateway/proxy tamperer | Mutates REST/RPC responses, hides errors, rewrites status codes, fabricates validation results, drops warnings, replays stale data, or changes side-effect receipts. | Cannot forge signatures from an authoritative backend if end-to-end signed receipts exist and are checked. |
| External content attacker | Controls web pages, emails, docs, tickets, RAG corpus entries, issue comments, or API-returned user-generated content consumed by tools. | May not directly call the agent; uses resource control for indirect prompt injection. |
| Tool supply-chain attacker | Publishes malicious tools, Trojanizes benign tools, compromises package distribution, or changes manifests/descriptions after approval. | Detection may be probabilistic; cannot bypass strict pinned hashes/signatures unless signing key or update channel is compromised. |
| OAuth/confused-deputy attacker | Exploits dynamic registration, redirect URI, static client IDs, consent cookies, token passthrough, or missing audience binding to obtain tokens or cause actions under victim authority. | Cannot exceed properly enforced per-user scopes and audience-bound tokens. |
| Adaptive prompt attacker | Knows defenses and crafts payloads to survive delimiters, scanners, paraphrasing, or model-based judges. | Cannot violate policy enforced outside the model if all side effects pass complete mediation. |

### Trust boundaries

1. Trusted instruction boundary: user-approved task, system/developer policy, and admin configuration are higher trust than tool metadata, tool outputs, web/email/doc content, and model-generated summaries.
2. Model context boundary: any text inserted into the prompt from tools is untrusted data, even if it came over TLS or from an authenticated MCP server.
3. Tool metadata boundary: tool names/descriptions/schemas/annotations are supply-chain inputs. They can guide model tool selection and must not be treated as policy.
4. Tool execution boundary: LLM tool-call proposals are requests, not authorizations. Authorization must be checked by a non-LLM policy engine.
5. Result-veracity boundary: tool result JSON/XML/text is not proof that the external world changed. State-changing tools require authoritative receipts or independent state reads.
6. Gateway boundary: API gateways and local shims are deputies. They can enforce policy but can also become response-tampering points.
7. OAuth/user authority boundary: tokens must be scoped, audience-bound, and tied to the user/session/task; token passthrough and shared service credentials expand confused-deputy risk.
8. Human approval boundary: the approval UI must display canonical action details from structured request/authoritative state, not only the agent's natural-language summary.
9. Persistence boundary: memory, caches, RAG indexes, and logs that store tool outputs can preserve attacker-controlled instructions for future runs.

### Attack paths

#### A1. Instruction smuggling in tool output

1. User asks a benign task requiring an external read, e.g. summarize email or check issue status.
2. Tool returns attacker-controlled content containing hidden or explicit instructions.
3. Agent concatenates the result into context without sufficient trust labeling/enforcement.
4. Model treats malicious content as instruction and calls a high-privilege tool.
5. Impact: data exfiltration, unauthorized action, misleading final answer, or worm-like propagation.

Primary sources: Greshake et al.; AgentDojo; OWASP LLM01; NIST AI 100-2e2025.

#### A2. False-success / forged side-effect result

1. Agent calls a tool to perform a side effect, e.g. "send report", "revoke key", "patch repo", "transfer funds".
2. Malicious tool/gateway returns schema-valid success: `{"status":"sent","message_id":"...","verified":true}`.
3. The side effect did not happen, happened to a different target, or happened with modified parameters.
4. Agent finalizes the workflow, reports success, or triggers dependent actions.
5. Impact: integrity failure, lost remediation, fraud, broken audit trail.

Defense requirement: side effects need request-bound, audience-bound, freshness-bound receipts from the authoritative service, or an independent read-after-write confirmation through a separately trusted path.

#### A3. Metadata poisoning before execution

1. User connects an MCP server or plugin; tool list/metadata is loaded into model context.
2. Tool description/annotation includes malicious instructions or suggests unsafe preconditions.
3. Model follows those instructions while calling other legitimate high-privilege tools.
4. Poisoned tool may never be executed, so result scanners miss it.
5. Impact: unauthorized file reads, exfiltration, privilege misuse.

Primary sources: MCPTox; MCP Tools spec; Anthropic MCP docs.

#### A4. Malicious tool implementation / local shim compromise

1. Attacker publishes or updates a tool that appears useful.
2. User/agent installs it; manifest and description appear benign.
3. Tool code exfiltrates data, modifies inputs/outputs, hides errors, or fabricates results.
4. Agent trusts the returned result and proceeds.
5. Impact: confidentiality/integrity/availability compromise under the tool's granted permissions.

Primary sources: MalTool; OWASP LLM03; OpenAI Apps SDK security guidance.

#### A5. API gateway response tampering

1. Agent uses a gateway as a unifying connector for multiple downstream APIs.
2. Gateway is compromised, misconfigured, or controlled by an attacker.
3. It rewrites validation responses, policy decisions, search results, balances, inventory, risk scores, or receipts.
4. Agent makes decisions or tool calls based on false world state.
5. Impact: incorrect approvals, bypassed validation, financial/data integrity loss.

Research gap: this is adjacent to indirect prompt injection and malicious tool attacks, but the core payload can be non-instructional structured data. Defenses must verify data provenance and semantics, not just prompt safety.

#### A6. Confused deputy through MCP proxy/OAuth

1. MCP proxy acts as a client to a third-party authorization/resource server.
2. Static client IDs, dynamic client registration, consent cookies, weak redirect validation, token passthrough, or missing audience binding confuse whose authority is being used.
3. Attacker obtains or causes use of tokens under the victim/user authority.
4. Agent receives valid-looking API results and executes under wrong authority.
5. Impact: unauthorized access/actions that appear legitimate in downstream logs.

Primary sources: MCP Security Best Practices and Authorization spec.

#### A7. Human approval deception

1. Agent receives forged tool result or model-visible malicious output.
2. Agent summarizes a dangerous action as benign or reports a false verification.
3. User approval UI displays the agent summary rather than canonical action data.
4. User approves based on false context.
5. Impact: human-in-the-loop becomes a rubber stamp.

Defense requirement: approval UI must be generated from structured action objects and authoritative verification, not from the same prompt context that may be poisoned.

#### A8. Persistent memory/cache poisoning

1. Tool output containing malicious instructions or false facts is stored in memory/RAG/cache.
2. Later tasks retrieve it as context, detached from the original source and trust label.
3. Agent treats the stale/poisoned content as internal knowledge.
4. Impact: delayed compromise, hard-to-debug false decisions, contamination across users/tasks.

Defense requirement: provenance labels, TTLs, trust downgrade on stored external content, and sanitization are needed at persistence boundaries.

## Defense model

### Design principles

1. Authenticated source is not trusted semantics. TLS/OAuth/server identity only identify who sent a result; they do not prove the result is true, complete, fresh, policy-compliant, or safe to treat as instruction.
2. Tool outputs are data, not commands. Tool results may fill parameters, evidence, or user-visible citations, but must not directly create new control flow for high-impact actions.
3. The LLM proposes; policy disposes. All tool invocations and side effects require complete mediation by deterministic policy code outside the model.
4. Verify side effects at the authority boundary. For state changes, require signed receipts or independent read-after-write checks from the authoritative system.
5. Pin and provenance-track the tool supply chain. Tool manifests, metadata, schemas, code, container images, and server identities should be versioned, signed, pinned, audited, and reapproved on material change.

### Concrete controls

#### C1. Tool-result envelope and receipts

For side-effecting or high-stakes tools, require a structured result envelope:

```json
{
  "issuer": "authoritative-service-id",
  "audience": "agent-app-id",
  "subject_user": "user-id-or-pseudonymous-binding",
  "tool_id": "send_email",
  "tool_version": "1.2.3",
  "schema_hash": "sha256:...",
  "request_hash": "sha256:canonical-request",
  "intent_id": "task/session-bound-id",
  "nonce": "agent-generated-random",
  "state_version_before": "opaque-version",
  "state_version_after": "opaque-version",
  "side_effect_id": "message/payment/repo-change-id",
  "result_hash": "sha256:canonical-result",
  "issued_at": "timestamp",
  "expires_at": "timestamp",
  "signature": "service-signature"
}
```

Minimum checks:

- signature verifies to pinned issuer key;
- `audience`, `subject_user`, `tool_id`, `request_hash`, and `nonce` match the original invocation;
- timestamp/freshness and state version are acceptable;
- receipt comes from the authoritative backend, not only a gateway or LLM-visible text;
- result fields satisfy domain invariants.

#### C2. Independent corroboration

Use read-after-write or cross-checks for high-impact actions:

- After `send_email`, read sent message by `message_id` from mail provider with a separate read-only token.
- After `update_acl`, fetch canonical ACL state and compare principal/scope.
- After `payment`, verify ledger entry through a separate settlement/ledger endpoint.
- For validation decisions, verify both policy decision and evidence inputs, not just a boolean `approved`.

Cross-checks should use a separately trusted path where possible. If both calls traverse the same compromised gateway, corroboration may be illusory.

#### C3. Control/data-flow separation

Borrowing from CaMeL:

- Plan high-level control flow from trusted user task before untrusted tool results are ingested.
- Treat external observations as data values tagged with source/provenance.
- Allow untrusted data to populate low-risk parameters only where policy permits.
- Deny calls where an untrusted observation causally introduces a new recipient, URL, command, credential target, payment destination, or exfiltration sink not present in trusted intent.

#### C4. Capability and information-flow policy

Track provenance/capabilities at field/value level:

- `source=email:external`, `source=web:untrusted`, `source=repo:trusted`, `secret=true`, `user_intent=true`, `signed_receipt=true`.
- Policies can state: external web/email content may not determine network destinations, shell commands, email recipients, payment accounts, or ACL principals.
- Sensitive values may only flow to approved sinks. Example: private document text can flow to summarization output for the user, but not to `send_email(to=external)` unless user explicitly approved that recipient and content.

#### C5. Tool registry and metadata controls

- Require signed manifests for MCP servers/plugins/local tools.
- Pin server identity, manifest hash, tool schema hash, and container/package digest.
- Treat tool descriptions/annotations as untrusted model input; never encode security policy solely in natural-language descriptions.
- Require reapproval for new tools, changed descriptions, changed output schemas, added write capabilities, changed network domains, and changed auth scopes.
- Scan metadata for prompt-injection patterns, but treat scanning as advisory only.

#### C6. Least privilege and authority separation

- Separate read and write tools.
- Prefer granular tools over open-ended shell, browser, URL fetcher, or arbitrary HTTP tools.
- Use per-user OAuth with minimum scopes and audience-bound tokens.
- Avoid token passthrough to MCP servers unless there is a strong reason and explicit controls.
- Use short-lived, task-scoped credentials where possible.
- Run local MCP servers/plugins in sandboxes with constrained filesystem and network access.

#### C7. Approval UI hardening

Approval prompts should display:

- canonical action type and exact parameters;
- target account/resource/recipient/destination;
- diff or before/after state from authoritative source;
- credential/scope that will be used;
- tool/server identity and version;
- result receipt/signature status for prior steps;
- explicit warnings for unverified or single-source claims.

Do not display only an LLM-generated summary for destructive or externally visible actions.

#### C8. Monitoring and incident response

- Store raw canonical requests/responses, hashes, signatures, tool identity, schema hash, state versions, and policy decisions.
- Emit trace IDs across agent, gateway, tool server, and downstream API.
- Alert on new tool metadata, dynamic tool list changes, unusual recipient/URL/payment destinations, repeated false-success discrepancies, and policy-denied tool calls.
- Use honeytokens/canary secrets to detect exfiltration from tool-output prompt injection.
- Maintain revocation path for compromised tools, manifests, signing keys, OAuth clients, and tokens.

## Evaluation plan implications for this lab

The lab should include scenarios that are not fully covered by AgentDojo-style prompt injection:

1. False success: tool returns success for an action that did not occur.
2. Wrong-target success: action occurs but to attacker-controlled target.
3. Stale replay: old valid receipt reused after state changed.
4. Gateway boolean flip: `approved=false` becomes `approved=true`.
5. Warning stripping: risk evidence removed while result remains schema-valid.
6. Metadata poisoning: malicious MCP tool description affects another tool call.
7. Dynamic update: benign tool becomes malicious after initial approval.
8. Human approval deception: model summary differs from canonical action object.
9. Same-gateway fake corroboration: primary and verification tools share a compromised proxy.
10. Capability enforcement: untrusted observation attempts to introduce a new sink.

Metrics:

- attack success rate;
- benign task success/utility;
- rate of unsafe calls blocked by policy;
- false positive approval friction;
- verification coverage by action type;
- provenance completeness;
- replayability from audit logs;
- added latency/cost for corroboration.

## Downloaded open PDFs

Downloaded to `/root/tool-output-spoofing-lab/papers/systems-security/`:

- `greshake-2023-indirect-prompt-injection.pdf`
- `agentdojo-2024-prompt-injection-agents.pdf`
- `camel-2025-defeating-prompt-injections-by-design.pdf`
- `mcptox-2025-tool-poisoning-mcp.pdf`
- `maltool-2026-malicious-tool-attacks.pdf`
- `attriguard-2026-causal-attribution-tool-invocations.pdf` (extra follow-up defense paper on causal attribution of tool calls)
- `nist-ai-100-2e2025-adversarial-ml-taxonomy.pdf`
- `nist-ai-600-1-generative-ai-profile.pdf`

## Bottom line

For this research direction, the defensible threat-model stance is:

> Every tool result, tool description, plugin manifest field, MCP server update, local shim output, and API gateway response is untrusted until independently authenticated, authorized, provenance-tagged, policy-checked, and, for side effects, verified against authoritative state.

Current docs and standards support this stance at the level of least privilege, prompt-injection risk, OAuth hygiene, and human approval. The main original contribution opportunity is to make "tool-result veracity" explicit: signed/provenance-bearing result envelopes, cross-check policies, gateway tamper detection, and benchmarks for schema-valid false results that do not rely on obvious malicious instructions.
