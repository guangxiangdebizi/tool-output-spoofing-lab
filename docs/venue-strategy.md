# Venue strategy

Date checked: 2026-06-08 Asia/Shanghai.

This direction should be pitched primarily as a security/systems benchmark and
defense paper, not as a generic LLM-agent prompt-injection paper.

## Recommended target order

| Rank | Venue | Why it fits | Timing implication |
| --- | --- | --- | --- |
| 1 | USENIX Security 2027 | Strong fit for secure systems, empirical attacks/defenses, artifact-heavy benchmark. | Cycle 1 registration/submission: 2026-08-18 / 2026-08-25 per official USENIX page. |
| 2 | IEEE S&P 2027 | Strong fit if we emphasize security properties, threat model, and defense principles. | First 2027 paper deadline is 2026-06-11, too soon for this project; second deadline is 2026-11-17. |
| 3 | NDSS 2027 fall cycle | Good fast-cycle security target for agent/tool protocol attacks and defenses. | Fall submission deadline: 2026-08-19. |
| 4 | ACM CCS 2027 | Good security target, but 2026 cycles are already effectively missed for new work as of 2026-06-08. | Use if experiments need a longer runway. |
| 5 | NeurIPS Datasets & Benchmarks | Fit if the artifact and benchmark design are stronger than the security defense novelty. | Use only if benchmark size/quality becomes the central contribution. |

## Why not lead with NLP-only venues

ACL/EMNLP-style venues may like the agent-evaluation angle, but the strongest
novelty is not model architecture or language understanding. The core is a
systems-security trust boundary: hidden truth vs. visible observation, result
provenance, receipt/freshness controls, and action integrity. Security venues
are more natural if the experiments are rigorous.

## Submission standard to hit

For USENIX/S&P/NDSS, the paper needs:

1. a threat model that explicitly distinguishes prompt injection, tool
   hallucination, metadata poisoning, malicious tool code, and result veracity;
2. a benchmark large enough that it is not dismissed as a toy prompt suite;
3. at least two or three real agent/model families, not only deterministic
   stubs;
4. defenses beyond prompt warnings: independent verification, signed receipts,
   freshness, contradiction handling;
5. utility/overhead tradeoffs on truthful cases;
6. public artifact or at least reviewable local mock suite; and
7. strong related-work positioning against Trust No Tool, MCP Security Bench,
   MCP-SafetyBench, AgentDojo, InjecAgent, ToolEmu, and CaMeL.

## Practical timeline

| Window | Milestone |
| --- | --- |
| 2026-06-08 to 2026-06-20 | Finish scaffold, final scenario schema, 20-30 MVP scenarios, real-agent adapter smoke tests. |
| 2026-06-21 to 2026-07-10 | Expand to 100+ paired scenarios; implement defenses; run pilot on 2-3 models. |
| 2026-07-11 to 2026-07-31 | Full experiment matrix on selected models; analyze failure modes; freeze benchmark. |
| 2026-08-01 to 2026-08-15 | Write security-venue paper, figures, artifact docs, ethics/reproducibility appendix. |
| 2026-08-18/25 | USENIX Security 2027 Cycle 1 registration/submission target if evidence is strong. |
| 2026-08-19 | NDSS 2027 fall backup if the paper is ready but better suited to NDSS. |
| 2026-11-10/17 | IEEE S&P 2027 second deadline if more experiments are needed. |

## Source links checked

- USENIX Security 2027 page: https://www.usenix.org/conference/usenixsecurity27
- IEEE S&P 2027 CFP: https://sp2027.ieee-security.org/cfpapers.html
- NDSS 2027 CFP: https://www.ndss-symposium.org/ndss2027/submissions/call-for-papers/
- ACM CCS 2026 CFP for current-cycle context: https://www.sigsac.org/ccs/CCS2026/call-for/call-for-papers.html

