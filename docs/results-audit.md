# Offline result audit

Each row is one result file; runs are not pooled or rescored. Transport/provider errors are excluded from graded/pass/fail; `rubric_pending` and `ungradable:*` are ungraded (not transport errors).

| Run | Split | SHA-256 result | Emitted | Unique | Errors | Graded | Pass | Fail | Ungraded | Historical |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| claude-haiku-4-5-20261007-024501 | data/splits/test.jsonl | 96bb417383e94af5bd63328a5fe763d5d6db09847d2d4cf9b99a1ca8ab1845a3 | 548 | 548 | 0 | 548 | 178 | 370 | 0 | yes |
| claude-opus-4-6-20261007-100805 | data/splits/test.jsonl | adc77253a171e832453ed63c78512c56abb045951c83fc609fcbfdcc268d4458 | 785 | 785 | 760 | 25 | 18 | 7 | 0 | yes |
| claude-opus-4-6-20261007-130018 | data/splits/test.jsonl | 526378c6c310560a9144dc7411f40732c81d311e265c05c7c2475c3142778260 | 785 | 785 | 757 | 28 | 28 | 0 | 0 | yes |
| claude-sonnet-4-5-20261007-130014 | data/splits/test.jsonl | cc88e781517cfa517cd206a4f8e091ee57eb3d3330793a54eac6219ce40dbea7 | 660 | 660 | 555 | 105 | 97 | 8 | 0 | yes |
| deepseek-v4.1-flash-20261006-135947 | data/splits/test.jsonl | a4143c4fbea493b0181aec081772b72cad49ca2a7c6cfa345b9fa34ffb9e4c62 | 785 | 785 | 0 | 776 | 90 | 686 | 9 | yes |
| glm-5.3-flash-merged | data/splits/test.jsonl | 1ac0d724fe60e900949cf5beafbfedc1bf638074f2e422806f7e284887be56f7 | 774 | 774 | 0 | 774 | 234 | 540 | 0 | yes |
| glm-5.3-merged | data/splits/test.jsonl | f3f87c6b4b063479982af6249217c26fbcfc37176ae09dce8009c90f7e95754b | 776 | 776 | 0 | 776 | 206 | 570 | 0 | yes |
| gpt-oss_120b-20261006-174542 | data/splits/test.jsonl | 494d9e772a7ed606c42ceafc6ca9464bbfad12902aa559b5b7de1e5a6a940756 | 785 | 785 | 0 | 776 | 19 | 757 | 9 | yes |
| gpt-oss_20b-20261006-141746 | data/splits/test.jsonl | 72ef6ed9f2816016ae46345c02313116f26ad5aa4e59da65a37141de19773855 | 785 | 785 | 0 | 776 | 54 | 722 | 9 | yes |
| karsastra-4b-20261007-034646 | data/splits/test.jsonl | 0b8a543cab31789f305d6962d262fda577aa4119dd7fffdcf2beb3505197ce39 | 785 | 785 | 0 | 776 | 355 | 421 | 9 | yes |
| qwen3.5_4b-20261006-155930 | data/splits/test.jsonl | ac3d1a8759afda5895efb2b02590d57b681372f2ec5a82e524e80ca5edf9e2ec | 785 | 785 | 0 | 776 | 90 | 686 | 9 | yes |
| qwen3.5_4b-20261006-160655 | data/splits/test.jsonl | a1eaddbeca43fab831538a096fc1446b9872cfac0944624e3363a3c11d33dfa6 | 785 | 785 | 0 | 776 | 90 | 686 | 9 | yes |
| karsastra-v2e-locked-20261007 | data/splits/test.jsonl | 6c35f95c7a98145b65402fb3421aeb7c7cbc9415c29fca9d3bd68da610f36e0b | 785 | 785 | 0 | 776 | 469 | 307 | 9 | yes |
| karsastra-v42-locked-20261011 | data/splits/test.jsonl | d016c1b4ca50821137f97b7d462bb543c57564495d8ed37377694108fbeb9e5b | 785 | 785 | 0 | 776 | 565 | 211 | 9 | yes |
| Karsastra v4.4 — October 13 extended-worker verdicts | data/splits/test-2026-10-11.jsonl | f40f59c0e35af55a40642c2befa9ea672582dc9bf2a57dfab9cc11639df0beb0 | 785 | 785 | 0 | 785 | 702 | 83 | 0 | yes |
| Karsastra v4.4 — offline strict-v1 regrade of October 13 responses | data/splits/test.jsonl | 110dcb1098cf2c1805401e897af76df740d85b53453901009cc63f379b5c8675 | 785 | 785 | 0 | 776 | 698 | 78 | 9 | yes |

Source paths, split/lock SHA-256, and question-lock digests are in the JSON report.

- **claude-haiku-4-5-20261007-024501**: Historical endpoint/CLI alias; not independently authenticated. Per-file recount, not a fresh inference run. Partial or error-heavy CLI evidence; do not treat as a completed baseline or combine retries by best verdict.
- **claude-opus-4-6-20261007-100805**: Historical endpoint/CLI alias; not independently authenticated. Per-file recount, not a fresh inference run. Partial or error-heavy CLI evidence; do not treat as a completed baseline or combine retries by best verdict.
- **claude-opus-4-6-20261007-130018**: Historical endpoint/CLI alias; not independently authenticated. Per-file recount, not a fresh inference run. Partial or error-heavy CLI evidence; do not treat as a completed baseline or combine retries by best verdict.
- **claude-sonnet-4-5-20261007-130014**: Historical endpoint/CLI alias; not independently authenticated. Per-file recount, not a fresh inference run. Partial or error-heavy CLI evidence; do not treat as a completed baseline or combine retries by best verdict.
- **deepseek-v4.1-flash-20261006-135947**: Historical endpoint/CLI alias; not independently authenticated. Per-file recount, not a fresh inference run.
- **glm-5.3-flash-merged**: Historical endpoint/CLI alias; not independently authenticated. Per-file recount, not a fresh inference run. Pre-existing merged artifact; not a single run and unsuitable for head-to-head ranking.
- **glm-5.3-merged**: Historical endpoint/CLI alias; not independently authenticated. Per-file recount, not a fresh inference run. Pre-existing merged artifact; not a single run and unsuitable for head-to-head ranking.
- **gpt-oss_120b-20261006-174542**: Historical endpoint/CLI alias; not independently authenticated. Per-file recount, not a fresh inference run.
- **gpt-oss_20b-20261006-141746**: Historical endpoint/CLI alias; not independently authenticated. Per-file recount, not a fresh inference run.
- **karsastra-4b-20261007-034646**: Historical endpoint/CLI alias; not independently authenticated. Per-file recount, not a fresh inference run.
- **qwen3.5_4b-20261006-155930**: Historical endpoint/CLI alias; not independently authenticated. Per-file recount, not a fresh inference run. Earlier run retained independently; do not pool with the later run.
- **qwen3.5_4b-20261006-160655**: Historical endpoint/CLI alias; not independently authenticated. Per-file recount, not a fresh inference run.
- **karsastra-v2e-locked-20261007**: Recovered SFT evaluation on original 785-question gold snapshot. Four reasoned and five ungradable rows excluded from graded denominator.
- **karsastra-v42-locked-20261011**: Recovered SFT evaluation on original 785-question gold snapshot. Four reasoned and five ungradable rows excluded from graded denominator.
- **Karsastra v4.4 — October 13 extended-worker verdicts**: 785/785 graded under the later keyword/status worker grading protocol; not the original 776-gradeable protocol. Recovered from completed Kaggle output, all questions/golds match revised snapshot.
- **Karsastra v4.4 — offline strict-v1 regrade of October 13 responses**: Derived offline from karsastra-v44-locked-20261013.jsonl using original public golds and unchanged Go strict-v1 grader. Not a new inference run or an independent sample.
