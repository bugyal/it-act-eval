# Eval harness (historical strict grader)

Run from `eval/` with Go installed; the default `-repo ..` expects `../data/splits/test.jsonl` and `test.locked.json`. A versioned split such as `-split test-2026-10-11` requires the corresponding `test-2026-10-11.locked.json`. A missing or mismatched test lock fails closed. `-allow-unlocked` prints a warning and is **not comparable** to locked results. Non-test splits without a lock are explicitly reported as unverified.

```sh
cd eval
go test ./...
# Offline: one original JSONL, one locked split, one independent output file.
go run ./cmd/tax-eval -repo .. -split test \
  -regrade path/to/original.jsonl -regrade-out path/to/regraded-strict.jsonl
```

`-regrade` never invokes a provider and refuses to overwrite the source or any existing output. It verifies the named split lock, matches every row's ID and question to the split, uses that split's gold/answer type, then applies the **original** `Grade` function separately to each response row; it does not choose the best attempt, deduplicate rows, or merge runs. Empty responses remain ungraded API-error rows. New run/regrade rows carry `grader_version: "strict-v1"`; historical rows without the field are not retroactively identified by metadata. Regrading against revised gold changes scores, so always record the split name and lock alongside the result file. `strict-v1` is an identifier for this historical implementation, **not** the later keyword grader; do not silently substitute another grading algorithm.

To run **one** model, explicitly supply the endpoint choice and model. This may incur charges; there is no automatic multi-provider sweep:

```sh
cd eval
export OPENROUTER_API_KEY=... # only if choosing openrouter; use your own credentials
TAX_EVAL_BACKEND=openrouter TAX_EVAL_MODEL='provider/model' TAX_EVAL_CONFIRM_RUN=yes \
  ./run_sweep.sh -split test -out ./results -concurrency 1 -limit 3
```

Or invoke `go run ./cmd/tax-eval -repo .. -backend custom -base-url http://127.0.0.1:11434/v1 -model your-local-model -concurrency 1 -out ./results` for a local OpenAI-compatible endpoint. Other preset backends and their required key variable names are listed with `go run ./cmd/tax-eval -h` and in `cmd/tax-eval/main.go`. No scripts load private dotfiles. The old finish-leg scripts are disabled; select and authorize a single run instead. `-resume-from` accepts comma-separated files from the **same model and split**; only answered IDs in the selected task subset are skipped. `-concurrency` must be positive.

**Limitations.** The historical entity extractor is strict but not a legal correctness adjudicator; it can miss paraphrases or accept a matching entity in incorrect reasoning. `reasoned` golds are rubric-pending/ungraded. `-report` / `BuildReport` is a **legacy convenience report, not an audit leaderboard**: it merges all JSONL files in `-out` by model, keeping the first task ID, and does not isolate split versions, run attempts, or grader versions. For a public comparison, keep raw files and split-lock provenance separate and calculate per-file metrics with explicit denominators and grader versions.
