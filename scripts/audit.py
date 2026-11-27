#!/usr/bin/env python3
"""Reproducible, offline per-file audit of locked IT Act evaluation results.

Run from any directory; manifest paths and CLI paths are relative to --root (the
repository by default). No model calls, grading, pooling, or inferred credentials.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class AuditError(ValueError):
    pass


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def resolve(root, name):
    if not isinstance(name, str) or not name:
        raise AuditError("path must be a non-empty string")
    path = (root / name).resolve()
    if not path.is_relative_to(root):
        raise AuditError("path escapes repository root: " + name)
    return path


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise AuditError(f"{path}: {exc}") from exc


def read_jsonl(path):
    try:
        lines = path.read_bytes().splitlines()
    except OSError as exc:
        raise AuditError(f"{path}: {exc}") from exc
    if not lines or not any(line.strip() for line in lines):
        raise AuditError(f"{path}: empty JSONL file")
    for index, line in enumerate(lines, 1):
        if not line.strip():
            raise AuditError(f"{path}:{index}: blank JSONL row")
        try:
            row = json.loads(line)
        except (UnicodeError, ValueError) as exc:
            raise AuditError(f"{path}:{index}: invalid JSON: {exc}") from exc
        if not isinstance(row, dict):
            raise AuditError(f"{path}:{index}: expected JSON object")
        yield index, row


def split_info(root, split, lock):
    path, lock_path = resolve(root, split), resolve(root, lock)
    tasks = {}
    questions = []
    for line, task in read_jsonl(path):
        question, answer = task.get("question"), task.get("answer")
        if not isinstance(question, str) or not question or not isinstance(answer, str):
            raise AuditError(f"{path}:{line}: missing question or answer")
        task_id = sha256(question.encode("utf-8"))[:8]
        if task_id in tasks:
            raise AuditError(f"{path}:{line}: duplicate task id {task_id}")
        if "id" in task and task["id"] != task_id:
            raise AuditError(f"{path}:{line}: task id does not match question")
        tasks[task_id] = task
        questions.append(question)
    locked = read_json(lock_path)
    if not isinstance(locked, dict) or not isinstance(locked.get("sha256_questions"), str):
        raise AuditError(f"{lock_path}: missing sha256_questions")
    digest = sha256("\n".join(sorted(questions)).encode("utf-8"))
    if locked["sha256_questions"] != digest:
        raise AuditError(f"LOCK MISMATCH: {path} sha256 {digest} != {lock_path} {locked['sha256_questions']}")
    if "n_test" in locked and (type(locked["n_test"]) is not int or locked["n_test"] != len(tasks)):
        raise AuditError(f"{lock_path}: n_test does not match split count")
    return tasks, {"path": split, "sha256_questions": digest,
                   "sha256_split": sha256(path.read_bytes()), "lock": lock,
                   "sha256_lock": sha256(lock_path.read_bytes()), "tasks": len(tasks)}


def audit_run(root, run):
    path = resolve(root, run["path"])
    tasks, split = split_info(root, run["split"], run["lock"])
    seen = set()
    stats = {key: 0 for key in ("emitted", "unique", "errors", "graded", "pass", "fail", "ungraded")}
    for line, row in read_jsonl(path):
        stats["emitted"] += 1
        rid = row.get("id")
        if not isinstance(rid, str) or not rid:
            raise AuditError(f"{path}:{line}: missing result id")
        if rid in seen:
            raise AuditError(f"{path}:{line}: duplicate result id {rid}")
        seen.add(rid)
        if rid not in tasks:
            raise AuditError(f"{path}:{line}: foreign result id {rid}")
        task = tasks[rid]
        if "question" in row and row["question"] != task["question"]:
            raise AuditError(f"{path}:{line}: question mismatch for id {rid}")
        if "gold" in row and row["gold"] != task["answer"]:
            raise AuditError(f"{path}:{line}: gold mismatch for id {rid}")
        if not isinstance(row.get("graded"), bool):
            raise AuditError(f"{path}:{line}: graded must be boolean")
        if "pass" in row and not isinstance(row["pass"], bool):
            raise AuditError(f"{path}:{line}: pass must be boolean")
        error = row.get("error", "")
        if not isinstance(error, str):
            raise AuditError(f"{path}:{line}: error must be a string")
        if error == "rubric_pending" or error.startswith("ungradable:"):
            stats["ungraded"] += 1
        elif error:
            stats["errors"] += 1
        elif row["graded"]:
            if "pass" not in row:
                raise AuditError(f"{path}:{line}: graded row missing pass")
            stats["graded"] += 1
            stats["pass" if row["pass"] else "fail"] += 1
        else:
            stats["ungraded"] += 1
    stats["unique"] = len(seen)
    return {"label": run.get("label", run["path"]), "note": run.get("note", ""),
            "historical": run.get("historical", False), "path": run["path"],
            "sha256_result": sha256(path.read_bytes()), "split": split, **stats}


def markdown(report):
    def cell(value):
        return str(value).replace("|", "\\|").replace("\n", " ")
    out = ["# Offline result audit", "", "Each row is one result file; runs are not pooled or rescored. Transport/provider errors are excluded from graded/pass/fail; `rubric_pending` and `ungradable:*` are ungraded (not transport errors).", "", "| Run | Split | SHA-256 result | Emitted | Unique | Errors | Graded | Pass | Fail | Ungraded | Historical |", "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|"]
    for run in report["runs"]:
        values = [run["label"], run["split"]["path"], run["sha256_result"],
                  *(run[key] for key in ("emitted", "unique", "errors", "graded", "pass", "fail", "ungraded")),
                  "yes" if run["historical"] else "no"]
        out.append("| " + " | ".join(cell(v) for v in values) + " |")
    out += ["", "Source paths, split/lock SHA-256, and question-lock digests are in the JSON report.", ""]
    for run in report["runs"]:
        if run["note"]:
            out.append(f"- **{cell(run['label'])}**: {cell(run['note'])}")
    if out[-1] != "":
        out.append("")
    return "\n".join(out)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--manifest", help="JSON object with runs array (path, split, lock, optional label/note/historical)")
    parser.add_argument("--split", help="split JSONL relative to root")
    parser.add_argument("--lock", help="question lock JSON relative to root")
    parser.add_argument("--result", action="append", default=[], help="explicit result JSONL; repeatable")
    parser.add_argument("--results-glob", help="result pattern relative to root, matching files sorted")
    parser.add_argument("--json-out", help="output JSON relative to root")
    parser.add_argument("--md-out", help="output Markdown relative to root")
    parser.add_argument("--check", action="store_true", help="compare generated bytes with existing outputs without writing")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    if not root.is_dir():
        parser.error("--root must be an existing directory")
    if bool(args.json_out) != bool(args.md_out) or (args.check and not args.json_out):
        parser.error("--json-out and --md-out must be supplied together (also for --check)")
    if args.manifest:
        if args.split or args.lock or args.result or args.results_glob:
            parser.error("--manifest cannot be combined with split/result flags")
        doc = read_json(resolve(root, args.manifest))
        if not isinstance(doc, dict) or not isinstance(doc.get("runs"), list) or not doc["runs"]:
            raise AuditError("manifest must contain a non-empty runs array")
        runs = doc["runs"]
    else:
        if not args.split or not args.lock or not (args.result or args.results_glob):
            parser.error("provide --manifest or --split, --lock, and --result/--results-glob")
        paths = list(args.result)
        if args.results_glob:
            resolve(root, args.results_glob)
            paths += [p.relative_to(root).as_posix() for p in sorted(root.glob(args.results_glob)) if p.is_file()]
        if not paths:
            raise AuditError("no result files matched")
        runs = [{"path": p, "split": args.split, "lock": args.lock} for p in paths]
    seen_paths = set()
    for run in runs:
        if not isinstance(run, dict) or not all(isinstance(run.get(k), str) and run[k] for k in ("path", "split", "lock")):
            raise AuditError("each run needs non-empty path, split, lock strings")
        if any(k in run and not isinstance(run[k], str) for k in ("label", "note")) or type(run.get("historical", False)) is not bool:
            raise AuditError("label/note must be strings and historical must be boolean")
        path = resolve(root, run["path"])
        if path in seen_paths:
            raise AuditError(f"duplicate run path: {run['path']}")
        seen_paths.add(path)
    output_paths = [resolve(root, name) for name in (args.json_out, args.md_out)] if args.json_out else []
    input_paths = seen_paths | {resolve(root, r[k]) for r in runs for k in ("split", "lock")}
    if args.manifest:
        input_paths.add(resolve(root, args.manifest))
    if len(set(output_paths)) != len(output_paths) or any(p in input_paths for p in output_paths):
        raise AuditError("output paths must be distinct and cannot overwrite input data")
    report = {"schema_version": 1, "runs": [audit_run(root, run) for run in runs]}
    content = (json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n", markdown(report))
    if output_paths:
        if args.check:
            for path, text in zip(output_paths, content):
                if not path.is_file() or path.read_bytes() != text.encode("utf-8"):
                    raise AuditError(f"stale or missing generated report: {path}")
        else:
            for path, text in zip(output_paths, content):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(content[0])


if __name__ == "__main__":
    try:
        main()
    except (AuditError, OSError, KeyError, TypeError) as exc:
        print(f"audit: {exc}", file=sys.stderr)
        sys.exit(1)
