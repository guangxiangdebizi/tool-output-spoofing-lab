#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/postprocess_full_model_run.sh \
    --summary-glob 'outputs/toolsandbox_model_full_shard*_summary.json' \
    --manifest-glob 'outputs/toolsandbox_model_full_shard*_manifest.json' \
    --summary-out outputs/toolsandbox_model_full_summary.json \
    --manifest-out outputs/toolsandbox_model_full_manifest.json \
    --ci-out outputs/toolsandbox_model_full_ci.json \
    --leakage-out outputs/prompt_leakage_audit_toolsandbox_full_gpt54.json \
    --stats-out outputs/toolsandbox_model_full_stats.json \
    --reference-profile toolsandbox_exec_naive

Runs the reproducible post-processing pipeline for a sharded full-overlay run:
merge shards -> Wilson CI -> prompt-leakage audit -> paired stats/utility funnel.
USAGE
}

SUMMARY_GLOB=""
MANIFEST_GLOB=""
SUMMARY_OUT=""
MANIFEST_OUT=""
CI_OUT=""
LEAKAGE_OUT=""
STATS_OUT=""
REFERENCE_PROFILE=""
PYTHON_BIN="${PYTHON:-python3.11}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --summary-glob) SUMMARY_GLOB="$2"; shift 2 ;;
    --manifest-glob) MANIFEST_GLOB="$2"; shift 2 ;;
    --summary-out) SUMMARY_OUT="$2"; shift 2 ;;
    --manifest-out) MANIFEST_OUT="$2"; shift 2 ;;
    --ci-out) CI_OUT="$2"; shift 2 ;;
    --leakage-out) LEAKAGE_OUT="$2"; shift 2 ;;
    --stats-out) STATS_OUT="$2"; shift 2 ;;
    --reference-profile) REFERENCE_PROFILE="$2"; shift 2 ;;
    --python) PYTHON_BIN="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

for value in SUMMARY_GLOB MANIFEST_GLOB SUMMARY_OUT MANIFEST_OUT CI_OUT LEAKAGE_OUT STATS_OUT REFERENCE_PROFILE; do
  if [[ -z "${!value}" ]]; then
    echo "missing required argument: ${value}" >&2
    usage >&2
    exit 2
  fi
done

export PYTHONPATH="${PYTHONPATH:-src:.}"

"$PYTHON_BIN" scripts/merge_model_shards.py \
  --summaries "$SUMMARY_GLOB" \
  --manifests "$MANIFEST_GLOB" \
  --summary-out "$SUMMARY_OUT" \
  --manifest-out "$MANIFEST_OUT"

"$PYTHON_BIN" scripts/summarize_model_results_with_ci.py \
  --summary "$SUMMARY_OUT" \
  --output "$CI_OUT"

"$PYTHON_BIN" scripts/audit_prompt_leakage.py \
  --manifest "$MANIFEST_OUT" \
  --output "$LEAKAGE_OUT"

"$PYTHON_BIN" scripts/analyze_model_full_stats.py \
  --summary "$SUMMARY_OUT" \
  --output "$STATS_OUT" \
  --reference-profile "$REFERENCE_PROFILE"
