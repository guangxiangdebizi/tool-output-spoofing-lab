# Next steps

Current pushed baseline commit:

```text
68c248b add agentdojo full overlay results
```

## Current full benchmark run

The GitHub repository is public and Apache-2.0 licensed. The current full
ToolSandbox/AgentDojo observation-overlay runs execute on the remote cloud host,
not locally. They use the NewAPI-compatible endpoint through environment
variables; API keys are not stored in repo files.

Remote run shape:

- ToolSandbox: `configs/experiments/toolsandbox_model_full.json`, full
  `outputs/toolsandbox_full_manifest.json`, currently running as 2 stable task
  shards after high-concurrency shards hit exit 137 on the remote host.
- AgentDojo: `configs/experiments/agentdojo_model_full.json`, full
  `outputs/agentdojo_full_manifest.json`, completed 1552/1552 cells and pushed
  merged summary/manifest/CI artifacts.
- Merge ToolSandbox after completion with `scripts/merge_model_shards.py`, then
  run `scripts/summarize_model_results_with_ci.py` and update the paper tables.

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

1. Finish the remote full ToolSandbox/AgentDojo overlay runs, merge shard
   summaries, run prompt-leakage audits on the merged manifests, and add
   bootstrap confidence intervals.
2. Add at least one additional model once the first-model full run is merged.
3. Repair or clearly bound AgentDojo clean utility before aggregating it as
   defense-effectiveness evidence.
4. Implement deployable observation-integrity defenses:
   - request-bound receipts;
   - timestamp/freshness and nonce checks;
   - independent read-after-write;
   - cross-tool contradiction handling;
   - final-answer uncertainty gate.
5. Target USENIX Security 2027 Cycle 1 or NDSS 2027 fall only if full/candidate
   existing-benchmark evidence
   is strong by August 2026; otherwise aim for IEEE S&P 2027 second deadline.
