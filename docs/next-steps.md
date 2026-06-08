# Next steps

Current local commit:

```text
c33539a scaffold tool-output spoofing research lab
```

## Immediate unblock: GitHub private push

The local repository is ready. The remaining blocker is GitHub CLI
authentication:

```bash
gh auth status
# currently: HTTP 401 / invalid token
```

Re-authenticate interactively:

```bash
gh auth login -h github.com
```

Then create and push the private repository:

```bash
cd /root/tool-output-spoofing-lab
gh repo create tool-output-spoofing-lab --private --source=. --remote=origin --push
```

If the repository already exists, use:

```bash
cd /root/tool-output-spoofing-lab
git remote add origin git@github.com:guangxiangdebizi/tool-output-spoofing-lab.git
git push -u origin main
```

## What is intentionally not pushed

The following are intentionally ignored:

- downloaded PDFs under `papers/**/*.pdf`;
- generated traces under `traces/*.trace.jsonl`;
- generated summaries under `outputs/*` except `outputs/README.md`;
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
