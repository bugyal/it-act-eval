# Public evaluation datasets

These are **test-only snapshots**, with original JSONL bytes preserved from the research workspace. Questions and gold answers are now public: these are **not blind holdouts** for models that may have seen this release. Do not pool these rows into training, validation, or a claim of uncontaminated evaluation; keep benchmark versions and run identities separate. The original benchmark and these later splits have different distributions, and a split name such as `test-v45` is not a model version.

| Split (`data/splits/`) | Rows | Coverage / families |
|---|---:|---|
| `test-v2.jsonl` | 199 | Act-2025 calculations, section renumbering and boundaries; facts intentionally shared with earlier training under different phrasings |
| `test-v4.jsonl` | 620 | Act-2025 rules, calculations, procedures, Hinglish and multipart questions |
| `test-v45.jsonl` | 185 | ICAI-inspired, GST/company-law and mock-test-derived chains |
| `hindi_eval.jsonl` | 85 | Hindi questions across calculations, TDS, deductions and procedure |
| `test-10k.jsonl` | 10,009 | Comprehensive TDS/payment-code, tax, GST and company-law evaluation |
| `test-10k-shard0.jsonl` | 2,800 | First contiguous partition of `test-10k` |
| `test-10k-shard1.jsonl` | 2,800 | Second contiguous partition |
| `test-10k-shard2.jsonl` | 2,800 | Third contiguous partition |
| `test-10k-shard3.jsonl` | 1,609 | Final contiguous partition |

Each JSONL line is one object with `question`, `answer` (gold), `answer_type`, `task_type`, `fact_key`, `template`, and provenance (`source_row` on the smaller splits; `source_url` on `test-10k`). `table` is also present, sometimes empty. Task IDs are the first eight hex characters of SHA-256 of the UTF-8 question. The four shards concatenate to the 10,009-row file; do not count them as additional questions. Every split has a sibling `.locked.json`: `n_test`, `sha256_questions` (SHA-256 of sorted **original** questions joined by newline, no trailing newline), `sha256_file` (exact JSONL bytes), and `source_lock` (unaltered historical lock metadata). Historical locks use different recipes, especially normalized question-plus-gold for `test-10k`; their hashes must **not** be equated with the compatible question hash.

Raw, byte-preserved outputs are in `eval/results/published/`: one Karsastra result per `test-10k-shard0..3` and two **separate** 185-row runs (`karsastra-run1.jsonl`, `karsastra-run2-acct2.jsonl`) for `test-v45`. Each result record contains `id`, `question`, `gold`, response/verdict metadata. Treat these as recorded historical outputs, not freshly verified legal answers, model identity, or an independently reproduced score. `docs/dataset-release.json` maps each source path to its destination and SHA-256; generated locks additionally record the original lock-file hash. All result IDs are unique within their own run and match the corresponding split's ID/question/gold; the four 10k runs together cover each of the 10,009 IDs once.

**Known limitations:** The current checkout's `eval/grade.go` does not implement several `test-v4` answer types (297/620 rows, including `schedule`, `rule`, `renumbering`, `deadline`, `hinglish`, and others), so do not interpret a default-grader traversal as a complete comparable grade. The first `test-v45` row asks about withdrawals of **Rs 1,37,50,000** but its gold calculates a **Rs 1,07,50,000 excess over Rs 3,00,00,000**, even though the stated withdrawal is below that threshold. This is a visible source-quality inconsistency; the gold and all result bytes are preserved, not silently repaired. No legal re-audit is claimed.
