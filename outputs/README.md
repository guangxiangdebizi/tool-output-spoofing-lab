# Outputs

Generated reports, benchmark summaries, and plots go here.

Do not commit large outputs by default. Generated traces stay under `traces/`
and remain ignored. The open repository keeps only the result artifacts that
are directly referenced by the current manuscript or needed to reproduce the
reported tables.

Canonical manuscript artifacts that are intentionally kept in git:

- `main_pilot_index.json`: current pilot result index for the Chinese draft.
- `toolsandbox_full_manifest.json`: full ToolSandbox overlay sampling manifest
  copied from the remote benchmark host.
- `agentdojo_full_manifest.json`: full AgentDojo overlay sampling manifest
  copied from the remote benchmark host.
- `*_model_full_summary.json` and `*_model_full_manifest.json`, once remote
  sharded full runs complete and are merged.
- `*_model_full_ci.json`, once generated with
  `scripts/summarize_model_results_with_ci.py`.
- `toolsandbox_real_manifest.json` and `agentdojo_real_manifest.json`: real
  benchmark substrate manifests used by the pilot/full runners.
- Current real-model pilot summaries/manifests referenced from
  `main_pilot_index.json`.
- `prompt_leakage_audit_expanded_gpt54.json` and
  `readback_scoring_ablation.json`: scoring/leakage control artifacts.

Old dry-run, smoke-only, and superseded intermediate summaries were removed
from git during repository cleanup.
