package main

import (
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"
)

func TestCLIRegradeWithoutBackendVerifiesVersionedLock(t *testing.T) {
	root := t.TempDir()
	dir := filepath.Join(root, "data", "splits")
	if err := os.MkdirAll(dir, 0755); err != nil {
		t.Fatal(err)
	}
	split := filepath.Join(dir, "test-2026-10-11.jsonl")
	if err := os.WriteFile(split, nil, 0644); err != nil {
		t.Fatal(err)
	}
	input := filepath.Join(root, "raw.jsonl")
	if err := os.WriteFile(input, []byte(`{"id":"x"}`+"\n"), 0644); err != nil {
		t.Fatal(err)
	}
	output := filepath.Join(root, "graded.jsonl")
	bin := filepath.Join(root, "tax-eval")
	build := exec.Command("go", "build", "-o", bin, ".")
	if raw, err := build.CombinedOutput(); err != nil {
		t.Fatalf("build: %v: %s", err, raw)
	}
	cmd := exec.Command(bin, "-repo", root, "-split", "test-2026-10-11", "-regrade", input, "-regrade-out", output)
	raw, err := cmd.CombinedOutput()
	if err == nil || !strings.Contains(string(raw), "test-2026-10-11.locked.json") {
		t.Fatalf("lock not enforced: err=%v output=%s", err, raw)
	}
	if _, err := os.Stat(output); !os.IsNotExist(err) {
		t.Fatalf("output created despite lock error: %v", err)
	}
}
