package taxeval

import (
	"bufio"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"math/rand"
	"os"
	"sort"
	"strings"
)

// Task is one eval item from the locked test split.
type Task struct {
	TaskType   string         `json:"task_type"`
	Table      string         `json:"table"`
	FactKey    string         `json:"fact_key"`
	Question   string         `json:"question"`
	Answer     string         `json:"answer"`
	AnswerType string         `json:"answer_type"`
	Template   string         `json:"template"`
	SourceRow  map[string]any `json:"source_row"`
	ID         string         `json:"-"` // sha256 prefix of question, set by loader
}

// LoadTasks reads a JSONL split file and assigns stable IDs.
func LoadTasks(path string) ([]Task, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, fmt.Errorf("open split: %w", err)
	}
	defer f.Close()

	var tasks []Task
	sc := bufio.NewScanner(f)
	sc.Buffer(make([]byte, 1024*1024), 1024*1024)
	lineNo := 0
	for sc.Scan() {
		lineNo++
		line := strings.TrimSpace(sc.Text())
		if line == "" {
			continue
		}
		var t Task
		if err := json.Unmarshal([]byte(line), &t); err != nil {
			return nil, fmt.Errorf("parse %s line %d: %w", path, lineNo, err)
		}
		t.ID = TaskID(t.Question)
		tasks = append(tasks, t)
	}
	if err := sc.Err(); err != nil {
		return nil, fmt.Errorf("scan %s: %w", path, err)
	}
	return tasks, nil
}

// TaskID returns the first 8 hex chars of sha256(question).
func TaskID(q string) string {
	h := sha256.Sum256([]byte(q))
	return hex.EncodeToString(h[:])[:8]
}

// VerifyLock checks the sorted-question hash and, when present, the SHA-256 of
// the split's raw bytes. Original question-only locks remain valid.
func VerifyLock(splitPath, lockPath string) (string, error) {
	raw, err := os.ReadFile(lockPath)
	if err != nil {
		return "", fmt.Errorf("read lock file: %w", err)
	}
	var lock struct {
		SHA256   string          `json:"sha256_questions"`
		FileHash json.RawMessage `json:"sha256_file"`
	}
	if err := json.Unmarshal(raw, &lock); err != nil {
		return "", fmt.Errorf("parse lock file: %w", err)
	}
	if lock.SHA256 == "" {
		return "", fmt.Errorf("lock file has no sha256_questions field")
	}

	tasks, err := LoadTasks(splitPath)
	if err != nil {
		return "", err
	}
	qs := make([]string, len(tasks))
	for i, t := range tasks {
		qs[i] = t.Question
	}
	sort.Strings(qs)
	joined := strings.Join(qs, "\n")
	h := sha256.Sum256([]byte(joined))
	actual := hex.EncodeToString(h[:])
	if actual != lock.SHA256 {
		return actual, fmt.Errorf("LOCK MISMATCH: split file sha256 %s != locked %s (test set changed since lock; refusing)",
			actual, lock.SHA256)
	}
	if lock.FileHash != nil {
		var expected string
		if err := json.Unmarshal(lock.FileHash, &expected); err != nil || len(expected) != 64 {
			return actual, fmt.Errorf("lock file has invalid sha256_file (expected 64 lowercase hex characters)")
		}
		decoded, err := hex.DecodeString(expected)
		if err != nil || hex.EncodeToString(decoded) != expected {
			return actual, fmt.Errorf("lock file has invalid sha256_file (expected 64 lowercase hex characters)")
		}
		bytes, err := os.ReadFile(splitPath)
		if err != nil {
			return actual, fmt.Errorf("read split file for sha256_file: %w", err)
		}
		fileHash := sha256.Sum256(bytes)
		fileActual := hex.EncodeToString(fileHash[:])
		if fileActual != expected {
			return actual, fmt.Errorf("LOCK MISMATCH: split file sha256_file %s != locked %s (test set changed since lock; refusing)", fileActual, expected)
		}
	}
	return actual, nil
}

// CountByType returns counts of tasks by answer_type (for the report).
func CountByType(tasks []Task) map[string]int {
	m := map[string]int{}
	for _, t := range tasks {
		m[t.AnswerType]++
	}
	return m
}

// ShuffleStable deterministically shuffles tasks in place (seeded by the task
// IDs, so order depends only on the task content).
func ShuffleStable(tasks []Task, seed int64) {
	r := rand.New(rand.NewSource(seed))
	r.Shuffle(len(tasks), func(i, j int) { tasks[i], tasks[j] = tasks[j], tasks[i] })
}
