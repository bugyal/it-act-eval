# Refresh audit — November 27, 2026

## Was the public repository up to date?

**No.** Before this refresh its history ended at `30f97fdd2adc1b4c301832bd4116c642cd856eca` (October 7, 2026; license addition), following the initial public export `6afe2a244dd3691e6ad6ffc2777c81d77fe28088`. It did not include the later v2e, v4.2, or v4.4 raw results, the corrected gold snapshot, or the broader holdout findings.

The name is now **IT Act Eval**, with canonical slug `bugyal/it-act-eval`. The old name remains only where useful as historical provenance. Dataset size belongs in version metadata, not the project name.

## Recovery record

Old Karsastra training/evaluation conversations were used as pointers, then checked against files, locks, and the lab's stored evaluation evidence. The original public-export conversation was October 7; the October 13 evaluation and October 16 benchmark-correction discussions explain the later v4.4 result and denominator problem. A chat's claim was not treated as a score artifact.

| Date / stage | Evidence recovered | Public action |
|---|---|---|
| October 7: v2e SFT | Raw original-benchmark result: 469/776 | Import unchanged raw output, fingerprint, recount |
| October 11: v4.2 SFT evaluation | Raw original-benchmark result: 565/776 | Import unchanged raw output; do not relabel as a later regrade |
| October 11: gold/grader audit | Same original questions, five corrected answers/types | Preserve original files and publish separate corrected snapshot |
| October 13: v4.4 evaluation | Kaggle `ashishbhatt1st/v44-eval-4b-kg3`, `results/karsastra-4b-v44-20261013-035249.jsonl` | Selectively recover this small result file only; validate all 785 IDs/questions/golds; 702/785 recorded passes |
| October 17: broader holdouts | Two independent 185-row runs; four disjoint shards covering 10,009 rows | Recompute aggregate counts; publish source hashes, not private questions/golds/responses |
| Later v4.5 training work | Training data/manifests and incomplete-run discussion exist | No verified completed v4.5-model evaluation recovered; no score invented |

The v4.4 file had disappeared from the inspected local output directory but was still retrievable from Kaggle. Its SHA-256 is `f40f59c0e35af55a40642c2befa9ea672582dc9bf2a57dfab9cc11639df0beb0`. No model weights were downloaded and no training or inference job was launched.

[Import provenance](import-provenance.json) records exact source paths and full-byte hashes. The source Git commit identifies code context only: ignored result artifacts are independently identified by their content hashes, not assumed to be committed in that source repository.

## Original vs revised scoring

Both public snapshots have question SHA-256 `14ffaa7de68272d02371e2cc31a7afddce74c25f45458722818b6e61bb62ab81`. Exactly five records change gold answer and answer type; the questions do not change. Historical worker keyword/status grading also makes previously excluded rows gradeable.

- v2e and v4.2 raw results use the original golds and have 776 graded answers.
- v4.4 raw results use revised golds and record 785 graded answers, 702 passing.
- Offline regrading the v4.4 responses against the original golds/strict grader gives 698/776. This is 89.9% on the old gradeable subset, versus the worker's 89.4% on all 785. They are not contradictory and must not share a denominator label.
- The source lock's historical `grader_sha` is not the current default grader's identity. Preserve it as historical metadata, not a false reproducibility guarantee.

See [protocol details](protocols.md). The default core grading semantics are preserved; this refresh does not silently replace the original grader with the later keyword implementation.

## Archive exclusions and downgraded claims

- `eval/results/claude-sonnet-4-5-20261007-074039.jsonl` has an unterminated JSON record at **line 126**. The file is retained untouched as historical evidence and excluded from the valid-run manifest. The audit rejects it; it does not silently skip the bad line.
- Other partial/error-heavy Claude files are audited separately, not merged into a headline. The older Sonnet 96.6% figure is not a completed-run score. Later pooled Sonnet artifacts mix clean and degraded/refusal eras, with conflicting denominators and potential test-file access; these were not imported as a fair baseline.
- The two pre-existing GLM `*-merged.jsonl` artifacts remain marked as merged historical evidence. Their internal selection policy is not reconstructed or endorsed.
- The two existing Qwen files are independent records, not two populations to pool. Their counts must not be double-counted as benchmark coverage.
- The initial Karsastra result itself contains nonzero compliance-bundle passes, so the blanket “every model scored zero” statement was not defensible even as a description of all rows in the old README.
- The old reports remain visible with explicit supersession notices. Their “in flight” statements describe October snapshots, not live jobs.
- Historical model labels are retained verbatim. Their presence in a response file does not independently establish provider/model identity.

## Broader holdouts and privacy boundary

The newer heldout datasets were not part of the original public export. This refresh publishes aggregate-only evidence to preserve test confidentiality and avoid silently expanding data licensing scope.

The `test-10k` raw files have **10,009 distinct IDs, 10,002 graded rows, 2,151 strict passes, and seven rubric-ungradable rows**, not seven transport errors. Strict accuracy is 21.5057% among graded rows or 21.4907% over all rows. The archived alternative final-tolerant count is 6,716/10,009 (67.1%); an older provisional 68.4% field is not promoted to the current result. The alternate grader was not independently reconstructed in this refresh.

`test-v45` is the name of an evaluation split. Both recovered 185-row files evaluate the **v4.4** model and independently record 93 passing rows. It would be false to present these as a successfully trained v4.5 model.

The later holdouts test different task families. Lower scores are evidence of generalization limits, not a like-for-like regression from the original benchmark. Public readers can inspect the aggregate evidence and source fingerprints but cannot independently reproduce private-holdout scores from this checkout.

## Verification scope

The refresh verifies file integrity, lock membership, gold/question consistency, independent per-run counts, and executable offline tooling. It also adds regression coverage for malformed/duplicate/foreign result rows, lock failures, and standalone harness operation. GitHub Actions checks the generated reports for drift and runs Python and Go tests without model calls.

This does **not** certify every gold answer as legally correct, prove absence of training contamination, authenticate historical model weights, or turn the benchmark into production-readiness evidence.
