package taxeval

import (
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestVerifyLockRejectsGoldOnlyMutationWithFileHash(t *testing.T) {
	dir := t.TempDir()
	split := filepath.Join(dir, "test.jsonl")
	lockPath := filepath.Join(dir, "test.locked.json")
	original := []byte("{\"question\":\"Q\",\"answer\":\"original\"}\n")
	if err := os.WriteFile(split, original, 0o644); err != nil {
		t.Fatal(err)
	}
	lock, err := json.Marshal(map[string]any{
		"n_test": 1, "sha256_questions": shaHex("Q"), "sha256_file": shaHex(string(original)),
	})
	if err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(lockPath, lock, 0o644); err != nil {
		t.Fatal(err)
	}
	if got, err := VerifyLock(split, lockPath); err != nil || got != shaHex("Q") {
		t.Fatalf("valid full-file lock should verify: hash=%s err=%v", got, err)
	}
	if err := os.WriteFile(split, []byte("{\"question\":\"Q\",\"answer\":\"changed\"}\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	got, err := VerifyLock(split, lockPath)
	if err == nil || !strings.Contains(err.Error(), "sha256_file") {
		t.Fatalf("gold-only change must fail file verification: hash=%s err=%v", got, err)
	}
	if got != shaHex("Q") {
		t.Fatalf("question hash changed with gold only: %s", got)
	}
}

func TestVerifyLockRejectsInvalidFileHashValues(t *testing.T) {
	dir := t.TempDir()
	split := filepath.Join(dir, "test.jsonl")
	lockPath := filepath.Join(dir, "test.locked.json")
	if err := os.WriteFile(split, []byte("{\"question\":\"Q\",\"answer\":\"gold\"}\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	for name, value := range map[string]string{
		"null": "null", "number": "42", "boolean": "false", "array": "[]", "object": "{}",
		"empty": `""`, "short": `"deadbeef"`, "nonhex": `"` + strings.Repeat("z", 64) + `"`,
		"uppercase": `"` + strings.Repeat("A", 64) + `"`,
	} {
		t.Run(name, func(t *testing.T) {
			lock := []byte(`{"sha256_questions":"` + shaHex("Q") + `","sha256_file":` + value + `}`)
			if err := os.WriteFile(lockPath, lock, 0o644); err != nil {
				t.Fatal(err)
			}
			if _, err := VerifyLock(split, lockPath); err == nil || !strings.Contains(err.Error(), "sha256_file") {
				t.Fatalf("invalid sha256_file %s should fail: %v", value, err)
			}
		})
	}
}
