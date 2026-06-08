# Outputs

Generated reports, benchmark summaries, and plots go here.

Do not commit large outputs by default. Keep reproducible summaries in `docs/`
when they become part of the research record.

Canonical manuscript artifacts that are intentionally kept in git:

- `main_pilot_index.json`: current pilot result index for the Chinese draft.
- `toolsandbox_full_manifest.json`: full ToolSandbox overlay sampling manifest
  copied from the remote benchmark host.
- `agentdojo_full_manifest.json`: full AgentDojo overlay sampling manifest
  copied from the remote benchmark host.
- `*_model_full_summary.json` and `*_model_full_manifest.json`, once remote
  sharded full runs complete and are merged.

Large trace directories stay under `traces/` and remain ignored by default.
