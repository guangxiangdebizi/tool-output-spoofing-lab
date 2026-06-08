# Reading Template

Purpose: make every paper readout comparable, claim-focused, and easy to
merge into `docs/literature-matrix.md`. Use one Markdown file per paper under
`secondary-research/deep-dive/`, or one clearly separated section if batching.

## 0. Triage label

- Priority: P0 / P1 / P2
- Relation to this lab:
  - Direct: compromised/spoofed tool observation or tool-result trust boundary.
  - Adjacent: indirect prompt injection, malicious tools/plugins, RAG poisoning,
    tool selection, tool hallucination, agent safety benchmark.
  - Background: survey, taxonomy, general LLM security, general agent benchmark.
- Reading status: skimmed / first-pass / deep-read / replicated / parked
- Assigned reader:
- Date:

## 1. Metadata

- BibTeX key:
- Title:
- Authors:
- Venue / year:
- Paper link:
- PDF path:
- Code / data / benchmark link:
- Version read:
- Notes on artifact availability:

### BibTeX seed template

```bibtex
@misc{bibkey,
  title = {...},
  author = {...},
  year = {...},
  eprint = {...},
  archivePrefix = {arXiv},
  url = {...}
}
```

If the work is peer-reviewed, replace `@misc` with the official conference or
journal entry once verified.

## 2. One-sentence summary

What exact problem does the work solve, and what is its main claim?

## 3. Threat model / problem setting

- Attacker capability:
- User prompt: benign / adversarial / mixed / unclear
- Agent architecture:
- Tooling setup:
- Where untrusted data enters:
  - user prompt
  - retrieved document
  - tool output
  - tool metadata
  - tool code
  - browser observation
  - memory / logs / other
- Defender visibility:
- Security or reliability property:

## 4. Mechanism

- Attack, failure, benchmark, or defense:
- Key algorithm or construction:
- Assumptions required:
- Why it works:
- What it does not cover:

## 5. Evaluation extraction

- Models evaluated:
- Tasks / domains:
- Number of tools:
- Number of test cases:
- Attack variants:
- Defense variants:
- Metrics:
- Decisive quantitative results:
- Human evaluation, if any:
- Artifact quality concerns:

## 6. Relevance to tool-output spoofing

Answer each item explicitly.

- Does the decisive attacker-controlled object arrive as a tool result?
- Is the harmful content an instruction, a semantic falsehood, bad metadata,
  bad tool code, poisoned retrieved knowledge, or model hallucination?
- Is the user task benign in the main attack?
- Does the paper compare truthful vs spoofed observations?
- Does it define a ground-truth oracle?
- Does it evaluate false-state propagation into later reasoning/actions?
- Does it test cross-tool corroboration, provenance, freshness, signatures, or
  uncertainty policies?
- Does it separate "data that is false" from "data that instructs the model"?
- Does it cover structured outputs such as JSON/status fields/exit codes?

## 7. Novelty impact for this lab

- Claim blocked:
- Claim weakened:
- Claim still open:
- Exact differentiator this lab should preserve:
- Related-work sentence draft:
- Baselines or metrics we must include:

## 8. Reproducibility / implementation notes

- Public code:
- Public data:
- External services required:
- Model/API dependencies:
- Estimated effort:
- Minimal subset worth reproducing:
- Risks of downloading large assets:

## 9. Evidence snippets

Keep direct quotes short. Prefer paraphrase plus exact section/table/figure.

- Key definition:
- Key table/metric:
- Key limitation:
- Citation to use:

## 10. Matrix update checklist

- [ ] Add/update row in `docs/literature-matrix.md`.
- [ ] Add BibTeX to the local bibliography once the final citation format is
      chosen.
- [ ] Add overlap/gap notes.
- [ ] Add any must-run baseline to experiment planning.
- [ ] Add any defense idea to the defense matrix.
- [ ] Mark whether this paper blocks, weakens, or only contextualizes the
      candidate novelty claim.
