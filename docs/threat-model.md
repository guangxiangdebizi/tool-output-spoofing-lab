# Threat Model

## Assets

- Agent final answer correctness.
- Integrity of decisions derived from tool observations.
- Integrity of external actions, even in this lab they are mocked.
- Provenance of observations and citations.
- Separation between tool data and tool instructions.

## Attacker capabilities

The main attacker controls one or more observation channels:

1. **Compromised tool server**: returns valid JSON with false fields.
2. **Malicious plugin/MCP server**: follows the tool protocol but fabricates
   content or embeds adversarial instructions.
3. **Network/API response tampering**: swaps, truncates, or replays responses.
4. **Local wrapper manipulation**: command shim forges stdout, stderr, exit
   status, timestamps, or file paths.
5. **Retrieval/browser observation poisoning**: external page or search result
   provides false evidence.

Assume the attacker cannot directly edit the system prompt or policy, cannot
modify the evaluator oracle, and cannot access production secrets in this lab.

## Trust boundaries

```text
user task
  -> agent planner
  -> tool call request
  -> tool transport / server / wrapper       attacker may control this side
  -> tool result enters model context        key observation boundary
  -> reasoning and action selection
  -> final answer / next tool call
```

## Attack classes

| Class | Spoofed signal | Example local scenario | Expected robust behavior |
| --- | --- | --- | --- |
| False success | Status says completed | Payment/deploy/delete succeeded | Verify via independent state read |
| False failure | Status says failed | Backup failed | Retry/check logs before reporting |
| Forged provenance | Citations/paths are fake | Paper or file path exists | Check URL/file exists and matches |
| Metric tampering | Scores/costs are false | Benchmark result inflated | Require raw trace or recomputation |
| Instruction smuggling | Tool result includes commands | JSON field says ignore policy | Treat as data, not instruction |
| Replay/staleness | Old valid result reused | Old scan says clean | Check timestamp/freshness |
| Partial omission | Critical field missing | Authz says user role only | Detect schema anomaly |
| Cross-tool contradiction | Tool A lies, tool B truthful | Scanner vs raw log disagree | Surface uncertainty |

## Defender capabilities

- Schema validation and required fields.
- Typed separation of observation data and natural-language content.
- Independent corroboration before high-impact conclusions.
- Freshness, nonce, timestamp, and signature checks.
- Tool provenance logging.
- Truth oracle during evaluation.
- Policy that forces uncertainty instead of confident action when observations
  contradict.

## Out-of-scope

- Stealing real credentials.
- Attacking third-party services.
- Unapproved testing against production APIs.
- Generating malware or persistence.
