# Next steps

Current pushed baseline commit:

```text
8bf9079 add prompt leakage audit and core paper figures
```

## Current full benchmark run

The GitHub repository is public and Apache-2.0 licensed. The current full
ToolSandbox/AgentDojo observation-overlay runs execute on the remote cloud host,
not locally. They use the NewAPI-compatible endpoint through environment
variables; API keys are not stored in repo files.

Remote run shape:

- ToolSandbox: `configs/experiments/toolsandbox_model_full.json`, full
  `outputs/toolsandbox_full_manifest.json`, 6 task shards.
- AgentDojo: `configs/experiments/agentdojo_model_full.json`, full
  `outputs/agentdojo_full_manifest.json`, 2 task shards.
- Merge after completion with `scripts/merge_model_shards.py`.

## What is intentionally not pushed

The following are intentionally ignored:

- downloaded PDFs under `papers/**/*.pdf`;
- generated traces under `traces/*.trace.jsonl`;
- generated large traces under `traces/`;
- generated summaries under `outputs/*` except explicitly unignored canonical
  paper artifacts;
- Python caches.

The paper notes and literature matrices contain the useful distilled content.

## Next research work

To make this top-tier viable, prioritize:

1. Expand from 6 MVP scenarios to 150-300 paired truthful/spoofed records, or
   pick one high-value vertical such as CI/security scanning and make it deeply
   realistic.
2. Implement real agent adapters for at least two commercial tool-calling APIs
   and one local/open model.
3. Implement real observation-integrity defenses:
   - request-bound receipts;
   - timestamp/freshness and nonce checks;
   - independent read-after-write;
   - cross-tool contradiction handling;
   - final-answer uncertainty gate.
4. Run a pilot matrix before any full benchmark:

```bash
PYTHONPATH=src /usr/bin/python3.11 scripts/run_mvp_matrix.py \
  --config configs/experiments/mvp_matrix.json \
  --out-dir traces
```

Run the real-model partial pilot, intentionally much smaller than a full
benchmark:

```bash
export NEWAPI_API_KEY=...
PYTHONPATH=src /usr/bin/python3.11 scripts/run_newapi_partial_pilot.py \
  --config configs/experiments/partial_pilot_newapi.json \
  --out-dir traces/newapi_partial_pilot \
  --summary outputs/newapi_partial_pilot_summary.json
```

5. Target USENIX Security 2027 Cycle 1 or NDSS 2027 fall only if pilot evidence
   is strong by August 2026; otherwise aim for IEEE S&P 2027 second deadline.
