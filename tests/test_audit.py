"""Offline end-to-end audit contracts. No provider or network needed."""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit.py"


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.tasks = [{"question": "Question B", "answer": "Gold B"},
                      {"question": "Question A", "answer": "Gold A"}]
        self.write_split()
        self.rows = [self.row(0, graded=True, passed=True),
                     self.row(1, graded=True, passed=False)]
        self.write_rows()

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def write_split(self):
        self.write("split.jsonl", "".join(json.dumps(t) + "\n" for t in self.tasks))
        digest = hashlib.sha256("\n".join(sorted(t["question"] for t in self.tasks)).encode()).hexdigest()
        self.write("split.locked.json", json.dumps({"sha256_questions": digest, "n_test": len(self.tasks)}))

    def row(self, index, graded=True, passed=False, error=""):
        t = self.tasks[index]
        return {"id": hashlib.sha256(t["question"].encode()).hexdigest()[:8],
                "question": t["question"], "gold": t["answer"],
                "graded": graded, "pass": passed, "error": error,
                "model": "example", "backend": "local"}

    def write_rows(self, path="result.jsonl", rows=None):
        self.write(path, "".join(json.dumps(row) + "\n" for row in (self.rows if rows is None else rows)))

    def call(self, *extra):
        return subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root),
                               "--split", "split.jsonl", "--lock", "split.locked.json",
                               "--result", "result.jsonl", *extra], capture_output=True, text=True)

    def test_writes_deterministic_reports_only_on_explicit_request_and_check_is_read_only(self):
        report = self.call()
        self.assertEqual(report.returncode, 0, report.stderr)
        self.assertFalse((self.root / "report.json").exists())
        args = ("--json-out", "report.json", "--md-out", "report.md")
        created = self.call(*args)
        self.assertEqual(created.returncode, 0, created.stderr)
        data = json.loads((self.root / "report.json").read_text())
        self.assertEqual(data["runs"][0]["emitted"], 2)
        self.assertEqual(data["runs"][0]["unique"], 2)
        self.assertEqual(data["runs"][0]["graded"], 2)
        self.assertEqual(data["runs"][0]["pass"], 1)
        self.assertEqual(data["runs"][0]["fail"], 1)
        self.assertEqual(data["runs"][0]["sha256_result"], hashlib.sha256((self.root / "result.jsonl").read_bytes()).hexdigest())
        self.assertEqual(self.call(*args, "--check").returncode, 0)
        self.assertEqual(self.call(*args).returncode, 0)
        self.assertEqual((self.root / "report.json").read_bytes(), json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True).encode() + b"\n")
        self.write("report.md", "stale")
        stale = self.call(*args, "--check")
        self.assertNotEqual(stale.returncode, 0)
        self.assertEqual((self.root / "report.md").read_text(), "stale")

    def test_ungradable_and_rubric_pending_are_ungraded_not_transport_errors(self):
        self.rows = [self.row(0, graded=False, error="rubric_pending"),
                     self.row(1, graded=True, passed=True, error="ungradable: missing rubric")]
        self.write_rows()
        result = self.call()
        self.assertEqual(result.returncode, 0, result.stderr)
        run = json.loads(result.stdout)["runs"][0]
        self.assertEqual((run["errors"], run["ungraded"], run["graded"], run["pass"]), (0, 2, 0, 0))

    def test_error_rows_are_reported_but_excluded_from_graded(self):
        self.rows[0]["error"] = "provider timeout"
        self.rows[0]["graded"] = True
        self.write_rows()
        result = self.call()
        self.assertEqual(result.returncode, 0, result.stderr)
        run = json.loads(result.stdout)["runs"][0]
        self.assertEqual((run["errors"], run["graded"], run["pass"], run["fail"]), (1, 1, 0, 1))

    def test_duplicate_task_id_rejected(self):
        self.tasks.append(dict(self.tasks[0]))
        self.write_split()
        result = self.call()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate task id", result.stderr)

    def test_duplicate_result_id_rejected(self):
        self.rows.append(dict(self.rows[0]))
        self.write_rows()
        result = self.call()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate result id", result.stderr)

    def test_foreign_result_id_rejected(self):
        self.rows[0]["id"] = "ffffffff"
        self.write_rows()
        result = self.call()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("foreign result id", result.stderr)

    def test_bad_lock_rejected(self):
        self.write("split.locked.json", '{"sha256_questions":"bad","n_test":2}')
        result = self.call()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("LOCK MISMATCH", result.stderr)

    def test_full_file_lock_rejects_gold_only_mutation(self):
        split = self.root / "split.jsonl"
        lock = json.loads((self.root / "split.locked.json").read_text())
        lock["sha256_file"] = hashlib.sha256(split.read_bytes()).hexdigest()
        self.write("split.locked.json", json.dumps(lock))
        valid = self.call()
        self.assertEqual(valid.returncode, 0, valid.stderr)
        self.assertEqual(json.loads(valid.stdout)["runs"][0]["split"]["sha256_questions"], lock["sha256_questions"])
        self.tasks[0]["answer"] = "changed gold"
        self.write("split.jsonl", "".join(json.dumps(t) + "\n" for t in self.tasks))
        result = self.call()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("sha256_file", result.stderr)

    def test_full_file_lock_rejects_invalid_hash_values(self):
        lock = json.loads((self.root / "split.locked.json").read_text())
        for value in (None, 42, False, [], {}, "", "deadbeef", "z" * 64, "A" * 64):
            with self.subTest(value=value):
                self.write("split.locked.json", json.dumps({**lock, "sha256_file": value}))
                result = self.call()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("sha256_file", result.stderr)

    def test_full_file_lock_verifies_raw_bytes_not_just_questions(self):
        split = self.root / "split.jsonl"
        lock = json.loads((self.root / "split.locked.json").read_text())
        lock["sha256_file"] = hashlib.sha256(split.read_bytes()).hexdigest()
        self.write("split.locked.json", json.dumps(lock))
        self.write("split.jsonl", split.read_text().replace('{"question"', '{ "question"', 1))
        result = self.call()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("sha256_file", result.stderr)

    def test_empty_results_rejected(self):
        self.write("result.jsonl", "")
        result = self.call()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("empty JSONL", result.stderr)

    def test_question_mismatch_rejected(self):
        self.rows[0]["question"] = "another question"
        self.write_rows()
        result = self.call()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("question mismatch", result.stderr)

    def test_gold_mismatch_rejected(self):
        self.rows[0]["gold"] = "other gold"
        self.write_rows()
        result = self.call()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("gold mismatch", result.stderr)

    def test_manifest_supports_per_run_split_lock_and_independent_result_files(self):
        self.write_rows("second.jsonl", [self.row(0, graded=True, passed=False)])
        alt = [{"question": "Different split question", "answer": "new gold"}]
        alt_hash = hashlib.sha256(alt[0]["question"].encode()).hexdigest()
        self.write("alternate.jsonl", json.dumps(alt[0]) + "\n")
        self.write("alternate.locked.json", json.dumps({"sha256_questions": alt_hash, "n_test": 1}))
        alt_row = {"id": alt_hash[:8], "question": alt[0]["question"], "gold": alt[0]["answer"], "graded": True, "pass": True}
        self.write_rows("alternate-result.jsonl", [alt_row])
        self.write("manifest.json", json.dumps({"runs": [
            {"path": "result.jsonl", "split": "split.jsonl", "lock": "split.locked.json", "label": "Original", "historical": True},
            {"path": "second.jsonl", "split": "split.jsonl", "lock": "split.locked.json", "label": "Retry"},
            {"path": "alternate-result.jsonl", "split": "alternate.jsonl", "lock": "alternate.locked.json", "label": "Corrected", "note": "Different gold"}]}))
        result = subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root),
                                 "--manifest", "manifest.json"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        runs = json.loads(result.stdout)["runs"]
        self.assertEqual([r["pass"] for r in runs], [1, 0, 1])
        self.assertEqual([r["emitted"] for r in runs], [2, 1, 1])
        self.assertTrue(runs[0]["historical"])
        self.assertEqual(runs[2]["split"]["path"], "alternate.jsonl")

    def test_reports_cannot_overwrite_manifest(self):
        self.write("manifest.json", json.dumps({"runs": [{"path": "result.jsonl", "split": "split.jsonl", "lock": "split.locked.json"}]}))
        before = (self.root / "manifest.json").read_bytes()
        result = subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root),
                                 "--manifest", "manifest.json", "--json-out", "manifest.json", "--md-out", "report.md"], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.root / "manifest.json").read_bytes(), before)

    def test_malformed_line_rejected_instead_of_skipped(self):
        self.write("result.jsonl", json.dumps(self.rows[0]) + "\n{" )
        result = self.call()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid JSON", result.stderr)


if __name__ == "__main__":
    unittest.main()
