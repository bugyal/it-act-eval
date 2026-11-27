# Benchmark versions and reporting policy

IT Act Eval is a versioned evaluation project, not a promise that one fixed row count describes every experiment.

## Public benchmark snapshots

| Snapshot | Files | Question identity | Gold / grader |
|---|---|---|---|
| Original public release (October 7, 2026) | `data/splits/test.jsonl`, `test.locked.json` | 785 questions, originally locked October 5 | Original golds; the Go grader in `eval/` excludes four reasoned and five ungradable rows on a complete run |
| October 11, 2026 correction | `data/splits/test-2026-10-11.jsonl`, `test-2026-10-11.locked.json` | The **same** 785 questions | Five gold/answer-type corrections; historical workers also introduced keyword rubrics and status grading |

The sorted-question hash for both is `14ffaa7de68272d02371e2cc31a7afddce74c25f45458722818b6e61bb62ab81`.
That hash protects **questions only**. It does not protect gold answers, grading code, decoding settings, or model identity. The import provenance and audit reports additionally fingerprint the complete files.

The October 11 lock is preserved as recovered, including its historical `gold_sha`, `grader_sha`, and `benchmark_id`. These are provenance claims from that experiment, not an assertion that today's default Go grader is the extended worker grader. Do not use the current default grader to claim reproduction of a historical extended-grader score without explicitly identifying the protocol.

### Five corrected records

| Stable task ID | Original answer type | Revised answer type |
|---|---|---|
| `cb6e7856` | section | section_no_equivalent |
| `7195fc31` | section | section_no_equivalent |
| `3a2c4a61` | section | section_status |
| `e169ba1c` | section | section_status |
| `32561770` | section | section_status |

The original files have not been rewritten. The corrections make non-numeric status answers explicit; they are not additional test questions.

## Reporting rules

- Keep model version, benchmark snapshot, grader, and run identity separate. `test-v45` is a **test split name**, not evidence of a successfully trained v4.5 model.
- Count each run separately. Never select whichever retry passed each task and call the union a single run.
- Disjoint shards may be combined only after verifying unique IDs, full expected coverage, and matching task/gold content.
- Show passes, graded denominator, missing rows, runtime errors, and rubric exclusions. A completed traversal of 785 questions is not necessarily 785 graded answers.
- The offline audit recounts recorded verdicts and validates task membership/content. It does **not** authenticate model weights or prove that the recorded grader ran correctly.
- Endpoint and CLI model names are historical labels, not independent proof of the underlying provider model/version. Retain them verbatim rather than silently substituting a modern model name.
- Partial or error-heavy Claude CLI runs and pre-existing merged GLM artifacts are historical diagnostics, not a fair completed-run leaderboard. Tool-enabled CLI access also raises test-file leakage risks.
- Never call a final-answer-tolerant regrade a strict score. Changing what must appear in an answer changes the metric, even when the model responses are identical.

## Training overlap and scope

The original split is **within-fact / phrasing-held-out**, not fact-held-out: the training data deliberately contains the same statutory facts under different phrasings. See [split policy](../data/splits/README_split_policy.md). A high score is evidence about this benchmark, not unseen-law reasoning or professional tax advice.

The original question and answer files have been public since October 7. Neither their historical lock nor an exact-duplicate check proves that a later model never saw them. Do not claim perpetual blindness or absence of contamination.

Later `test-v2`, `test-v4`, `test-v45`, Hindi and `test-10k` experiments have different questions, distributions, and sometimes broader GST/company-law scope. Scores on them are not deltas against the original benchmark. This refresh publishes aggregate evidence for unreleased holdouts, **not their questions, golds, or raw responses**. This preserves the holdouts and avoids silently expanding the licensing scope of the original public release.

## Grader limitations

The preserved original grader is an entity-presence heuristic. It can accept an answer that includes required entities alongside contradictory material. Some branches validate only selected entities (for example, `nature_and_section` checks section references), and multi-part grading accepts a part with no recognized entities. It does not establish legal correctness, citation validity, or good reasoning. Keyword rubrics in later workers introduce their own false-positive risks. These limitations invalidate blanket claims such as “all required legal facts are verified.”

This refresh is an artifact/reproducibility audit, not a legal review of the gold answers or a new model-inference sweep.
