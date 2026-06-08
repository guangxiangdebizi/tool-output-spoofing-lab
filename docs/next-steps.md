# Next steps

Current pushed baseline commit:

```text
2e7485d add toolsandbox shard progress logs
```

## Current full benchmark run

The GitHub repository is public and Apache-2.0 licensed. The current full
ToolSandbox/AgentDojo observation-overlay runs execute on the remote cloud host,
not locally. They use the NewAPI-compatible endpoint through environment
variables; API keys are not stored in repo files.

Remote run shape:

- ToolSandbox: `configs/experiments/toolsandbox_model_full.json`, full
  `outputs/toolsandbox_full_manifest.json`, currently running as 5 stable task
  shards on the remote cloud host. As of 2026-06-09 00:10 CST, the trace
  directory contained 6272/12384 expected cells; `full_monitor` records progress
  and will merge shards after all `ts_full_stable_*` screens exit, then run CI,
  prompt-leakage audit, and paired-statistics diagnostics.
- AgentDojo: `configs/experiments/agentdojo_model_full.json`, full
  `outputs/agentdojo_full_manifest.json`, completed 1552/1552 cells and pushed
  merged summary/manifest/CI artifacts.
- Merge ToolSandbox after completion with `scripts/merge_model_shards.py`, then
  run `scripts/summarize_model_results_with_ci.py` and update the paper tables.

The ToolSandbox runner now treats only complete, real `model_chat_completion`
traces as reusable. Empty files, malformed JSONL, missing `structured_final`,
provider/API uncertainty stubs, and traces without `model_call_executed=true`
are recorded as invalid existing traces and rerun. This matters because earlier
remote high-concurrency attempts produced unusable or partial cells.

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
5. Target USENIX Security 2027 Cycle 1 or NDSS 2027 fall only if full
   existing-benchmark evidence is strong by August 2026; otherwise aim for
   IEEE S&P 2027 second deadline.
