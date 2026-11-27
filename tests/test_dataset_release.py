"""Offline integrity checks for the public dataset release and its shards."""
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import audit


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


class DatasetReleaseTests(unittest.TestCase):
    def test_release_fingerprints_and_all_split_locks(self):
        release = json.loads((ROOT / "docs/dataset-release.json").read_text())
        self.assertEqual(len(release["files"]), 24)
        for item in release["files"]:
            with self.subTest(path=item["path"]):
                path = ROOT / item["path"]
                raw = path.read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(), item["sha256_file"])
                self.assertEqual(len(raw), item["bytes"])
                if item["kind"] == "split":
                    self.assertEqual(len(rows(path)), item["rows"])
                    audit.split_info(ROOT, item["path"], str(Path(item["path"]).with_suffix(".locked.json")))

    def test_10k_shards_are_exact_partition_and_results_cover_all(self):
        split = ROOT / "data/splits/test-10k.jsonl"
        parts = [ROOT / f"data/splits/test-10k-shard{i}.jsonl" for i in range(4)]
        self.assertEqual(b"".join(p.read_bytes() for p in parts), split.read_bytes())
        expected = {hashlib.sha256(r["question"].encode()).hexdigest()[:8]: r for r in rows(split)}
        self.assertEqual(len(expected), 10009)
        seen = set()
        for i in range(4):
            for result in rows(ROOT / f"eval/results/published/karsastra-shard{i}.jsonl"):
                task_id = result["id"]
                self.assertNotIn(task_id, seen)
                seen.add(task_id)
                self.assertEqual(result["question"], expected[task_id]["question"])
                self.assertEqual(result["gold"], expected[task_id]["answer"])
        self.assertEqual(seen, set(expected))

    def test_every_published_result_is_in_audit_manifest(self):
        release = json.loads((ROOT / "docs/dataset-release.json").read_text())
        manifest = json.loads((ROOT / "data/audit-manifest.json").read_text())
        runs = {r["path"]: r for r in manifest["runs"]}
        for item in release["files"]:
            if item["kind"] == "raw_result":
                self.assertIn(item["path"], runs)
                self.assertEqual(runs[item["path"]]["split"], f"data/splits/{item['split']}.jsonl")


if __name__ == "__main__":
    unittest.main()
