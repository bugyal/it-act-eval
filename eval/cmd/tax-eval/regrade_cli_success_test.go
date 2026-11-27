package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	taxeval "taxeval"
	"testing"
)

func TestCLIRegradeValidLockWithoutProvider(t *testing.T) {
	root := t.TempDir()
	dir := filepath.Join(root, "data", "splits")
	if err := os.MkdirAll(dir, 0755); err != nil {
		t.Fatal(err)
	}
	q := "Which code?"
	task, _ := json.Marshal(taxeval.Task{Question: q, Answer: "code 1001", AnswerType: "code"})
	os.WriteFile(filepath.Join(dir, "test-2026-10-11.jsonl"), append(task, '\n'), 0644)
	hash := sha256.Sum256([]byte(q))
	os.WriteFile(filepath.Join(dir, "test-2026-10-11.locked.json"), []byte(`{"sha256_questions":"`+hex.EncodeToString(hash[:])+`"}`), 0644)
	input := filepath.Join(root, "original.jsonl")
	output := filepath.Join(root, "regraded.jsonl")
	row, _ := json.Marshal(taxeval.ResultRecord{ID: taxeval.TaskID(q), Question: q, RawResponse: "code 1001"})
	os.WriteFile(input, append(row, '\n'), 0644)
	bin := filepath.Join(root, "tax-eval")
	if raw, err := exec.Command("go", "build", "-o", bin, ".").CombinedOutput(); err != nil {
		t.Fatalf("build: %v: %s", err, raw)
	}
	raw, err := exec.Command(bin, "-repo", root, "-split", "test-2026-10-11", "-regrade", input, "-regrade-out", output).CombinedOutput()
	if err != nil || !strings.Contains(string(raw), "lock OK") {
		t.Fatalf("regrade err=%v output=%s", err, raw)
	}
	regraded, err := os.ReadFile(output)
	if err != nil {
		t.Fatal(err)
	}
	var got taxeval.ResultRecord
	if err := json.Unmarshal(regraded[:len(regraded)-1], &got); err != nil {
		t.Fatal(err)
	}
	if !got.Pass || got.GraderVersion != taxeval.StrictGraderVersion {
		t.Fatalf("regraded: %+v", got)
	}
}
