package main

import (
	"os"
	"path/filepath"
	"strings"
	"testing"

	taxeval "taxeval"
)

func TestCheckSplitLockVersionedAndUnlocked(t *testing.T) {
	root := t.TempDir()
	dir := filepath.Join(root, "data", "splits")
	if err := os.MkdirAll(dir, 0755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(dir, "test_v2.jsonl"), []byte(""), 0644); err != nil {
		t.Fatal(err)
	}
	// Missing versioned lock must fail closed, even when the old test.locked.json exists.
	if err := os.WriteFile(filepath.Join(dir, "test.locked.json"), []byte(`{"sha256_questions":"irrelevant"}`), 0644); err != nil {
		t.Fatal(err)
	}
	_, err := checkSplitLock(root, "test_v2", false)
	if err == nil || !strings.Contains(err.Error(), "test_v2.locked.json") {
		t.Fatalf("missing versioned lock: %v", err)
	}
	status, err := checkSplitLock(root, "test_v2", true)
	if err != nil || !strings.Contains(status, "WARNING") {
		t.Fatalf("unlocked status=%q err=%v", status, err)
	}
	if err := os.WriteFile(filepath.Join(dir, "test_v2.locked.json"), []byte(`{"sha256_questions":"wrong"}`), 0644); err != nil {
		t.Fatal(err)
	}
	status, err = checkSplitLock(root, "test_v2", true)
	if err != nil || !strings.Contains(status, "WARNING") {
		t.Fatalf("mismatched unlocked status=%q err=%v", status, err)
	}
}

func TestPendingTasksIgnoresOffSubsetResumeIDs(t *testing.T) {
	tasks := []taxeval.Task{{ID: "one"}, {ID: "two"}}
	done := map[string]bool{"one": true, "outside-a": true, "outside-b": true}
	pending := pendingTasks(tasks, done)
	if len(pending) != 1 || pending[0].ID != "two" {
		t.Fatalf("pending: %+v", pending)
	}
}

func TestValidateConcurrencyRejectsNonPositive(t *testing.T) {
	for _, n := range []int{0, -1} {
		if err := validateConcurrency(n); err == nil {
			t.Fatalf("concurrency %d accepted", n)
		}
	}
	if err := validateConcurrency(1); err != nil {
		t.Fatal(err)
	}
}
