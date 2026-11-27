# IT Act Eval

Versioned evaluation datasets, deterministic grading, and auditable historical results for Indian tax-law compliance. Formerly **itact-785**; canonical repository: [bugyal/it-act-eval](https://github.com/bugyal/it-act-eval).

**Updated November 27, 2026:** recovered later Karsastra SFT evaluations, preserved the original public benchmark, added a corrected-gold snapshot, and replaced stale headline claims with per-run evidence. This is an artifact audit, **not a new model-inference sweep or independent legal review**.

## Recovered Karsastra results

The original benchmark has 785 questions about the Income-tax Act, 2025 transition: payment codes, section/form mappings, rates, thresholds, dates, and compliance bundles. Its original grader scores 776 questions, excluding four reasoned and five ungradable records.

| Historical model/run | Gold / grading protocol | Pass / graded | Accuracy |
|---|---|---:|---:|
| Initial Karsastra 4B, October 7 | Original public snapshot / original grader | 355 / 776 | 45.7% |
| Karsastra v2e, October 7 | Original public snapshot / original grader | 469 / 776 | 60.4% |
| Karsastra v4.2, October 11 | Original public snapshot / original grader | 565 / 776 | 72.8% |
| Karsastra v4.4, October 13 | Corrected snapshot / extended worker grader | 702 / 785 | 89.4% |

These are historical artifacts, not a controlled experiment isolating training changes. **The last row uses a different gold/grader protocol.** Regrading its saved responses against the original public golds with the preserved original strict grader gives **698/776 (89.9%)**. That is an offline regrade of the same answers, not another model run.

See the [per-file audit](docs/results-audit.md), [machine-readable evidence](docs/results-audit.json), and [import provenance](docs/import-provenance.json). Later raw outputs are under `eval/results/recovered/`.

### Broader holdouts tell a different story

| Experiment using the v4.4 model | Recorded strict result | Qualification |
|---|---:|---|
| `test-v45`, 185 questions | 93/185 — 50.27% | Same total in two separate runs; **not** a v4.5-trained model |
| `test-10k`, 10,009 questions | 2,151/10,002 graded — 21.51% | Seven rubric-ungradable rows; 2,151/10,009 = 21.49% over all rows |

These holdouts have different distributions and broader computation/GST/company-law coverage. They are **not directly comparable** to the original mapping benchmark. An archived final-answer-tolerant analysis reports 6,716/10,009 (67.1%); that changes the grading policy and is **not** the strict score or a regrade newly reproduced here.

[Aggregate evidence and source fingerprints](docs/heldout-results.json) are published without releasing private holdout questions, golds, or responses. Those holdout scores therefore cannot be independently reproduced from this public checkout. No completed, verified v4.5-model evaluation was recovered.

## What happened to the frontier-model headline?

The old “best frontier model: 30.2%” and “every model scores zero on compliance bundles” claims are withdrawn as current conclusions. The early table mixed completed traversals, partial CLI samples, error-heavy attempts, and merged artifacts. Later Claude outputs also have protocol/era and potential test-file leakage concerns. There is no defensible completed-run frontier ranking in this refresh.

The archived GLM-5.3-flash merged file records 234/774, but is not a full 785-row run. The old Sonnet 96.6% figure was a partial sample; one underlying file is truncated. See [the refresh audit](docs/refresh-audit.md). Model names in raw files are historical endpoint/CLI aliases, **not independently authenticated provider identities**.

## Reproduce offline

Requires Python 3.11+ and the Go version in `eval/go.mod`. No API key or GPU is needed.

```bash
git clone https://github.com/bugyal/it-act-eval.git
cd it-act-eval
python3 -m unittest discover -s tests -v
python3 scripts/audit.py --manifest data/audit-manifest.json \
  --json-out docs/results-audit.json --md-out docs/results-audit.md --check
(cd eval && GOWORK=off go test ./...)
```

To regenerate the audit, use the same command without `--check`. It checks the question lock, task IDs, matching question/gold content, and hashes, then recounts stored verdicts **per file**. It does not pick the best response from retries, authenticate models, or independently validate grading verdicts.

For fresh inference and offline regrading, see [the harness instructions](eval/README.md). Supply your own endpoint and credentials explicitly; inference may cost money. The legacy pooled `-report` output is not the audited results table.

## Repository map

```text
data/splits/test.jsonl                    Original public 785-task snapshot, unchanged
data/splits/test.locked.json              Original question lock, unchanged
data/splits/test-2026-10-11.jsonl          Same questions, five gold/type corrections
data/splits/test-2026-10-11.locked.json    Recovered corrected-snapshot metadata
data/audit-manifest.json                  Explicit run-to-snapshot selection
eval/                                    Original Go grader, runner, tests, offline regrade
eval/results/recovered/                  Later original-benchmark raw outputs
scripts/audit.py                          Offline per-file integrity/verdict audit
docs/results-audit.{json,md}              Reproducible audit output
docs/heldout-results.json                 Aggregate-only private holdout evidence
docs/protocols.md                         Versions, denominators, grading limitations
docs/refresh-audit.md                     Recovery findings and exclusions
```

## Interpretation and limitations

- The original split is **within-fact / phrasing-held-out**, not fact-held-out: models train on the same statutory facts under different wording. See [split policy](data/splits/README_split_policy.md).
- Questions and answers have been public since October 7. A lock does not prove that later models never saw them; no blanket contamination-free claim is made.
- The question hash does **not** lock golds or grader code. Corrected golds are a separate snapshot; the audit also hashes complete files.
- Entity-presence and keyword heuristics can accept contradictions or miss meaningful errors. They do not measure persuasive legal drafting, case-law research, professional judgment, or real-client reliability. [Detailed limitations](docs/protocols.md).
- Golds carry the original source metadata. This refresh has not independently revalidated current law, source licensing, or every gold answer. This is not tax advice.
- Training data, weights, private customer information, and unreleased holdout questions are outside this refresh.

## Historical reports and license

The [P2 report](docs/p2-findings-report.md) and [old aggregate table](eval/results/baseline_scores.md) are retained with supersession notices, not silently presented as current results.

Existing dataset, results, and docs: [CC BY-4.0](LICENSE). Harness and new audit code: [Apache-2.0](eval/LICENSE-CODE). Curated by [Prasthana Lab](https://github.com/bugyal).
