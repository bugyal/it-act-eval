package taxeval

import (
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestRegradeResultsUsesLockedGoldAndPreservesIndependentRows(t *testing.T) {
	dir := t.TempDir()
	q := "Which code?"
	id := TaskID(q)
	split := filepath.Join(dir, "test.jsonl")
	task := Task{Question: q, Answer: "code 1001", AnswerType: "code"}
	b, _ := json.Marshal(task)
	if err := os.WriteFile(split, append(b, '\n'), 0644); err != nil {
		t.Fatal(err)
	}
	input := filepath.Join(dir, "source.jsonl")
	rows := []ResultRecord{
		{ID: id, Question: q, Gold: "code 1002", AnswerType: "code", RawResponse: "code 1001", Pass: false, Error: "old grader", Model: "test-model"},
		{ID: id, Question: q, Gold: "code 1002", AnswerType: "code", RawResponse: "code 1002", Pass: true, Model: "test-model"},
		{ID: id, Question: q, RawResponse: "", Error: "API failure", Model: "test-model"},
	}
	var lines []byte
	for _, r := range rows {
		b, _ := json.Marshal(r)
		lines = append(lines, append(b, '\n')...)
	}
	if err := os.WriteFile(input, lines, 0644); err != nil {
		t.Fatal(err)
	}
	output := filepath.Join(dir, "graded.jsonl")
	if err := RegradeResults(split, input, output); err != nil {
		t.Fatal(err)
	}
	raw, err := os.ReadFile(output)
	if err != nil {
		t.Fatal(err)
	}
	gotLines := strings.Split(strings.TrimSpace(string(raw)), "\n")
	if len(gotLines) != 3 {
		t.Fatalf("want 3 independent rows, got %d", len(gotLines))
	}
	var got []ResultRecord
	for _, line := range gotLines {
		var r ResultRecord
		if err := json.Unmarshal([]byte(line), &r); err != nil {
			t.Fatal(err)
		}
		got = append(got, r)
	}
	if !got[0].Graded || !got[0].Pass || got[0].Gold != "code 1001" || got[0].Error != "" {
		t.Fatalf("first: %+v", got[0])
	}
	if got[0].GraderVersion != StrictGraderVersion {
		t.Fatalf("version: %+v", got[0])
	}
	if !got[1].Graded || got[1].Pass {
		t.Fatalf("second should fail independently: %+v", got[1])
	}
	if got[2].Graded || got[2].Error != "API failure" {
		t.Fatalf("API failure should be retained: %+v", got[2])
	}
	sourceAgain, _ := os.ReadFile(input)
	if string(sourceAgain) != string(lines) {
		t.Fatal("source modified")
	}
}

func TestRegradeResultsFailsClosedOnUnknownIDAndDoesNotWrite(t *testing.T) {
	dir := t.TempDir()
	split := filepath.Join(dir, "split.jsonl")
	input := filepath.Join(dir, "input.jsonl")
	output := filepath.Join(dir, "output.jsonl")
	task, _ := json.Marshal(Task{Question: "known", Answer: "code 1001", AnswerType: "code"})
	os.WriteFile(split, append(task, '\n'), 0644)
	row, _ := json.Marshal(ResultRecord{ID: "unknown", Question: "unknown", RawResponse: "code 1001"})
	os.WriteFile(input, append(row, '\n'), 0644)
	if err := RegradeResults(split, input, output); err == nil {
		t.Fatal("unknown ID accepted")
	}
	if _, err := os.Stat(output); !os.IsNotExist(err) {
		t.Fatalf("output unexpectedly created: %v", err)
	}
}

func TestRegradeResultsRefusesOverwrite(t *testing.T) {
	dir := t.TempDir()
	p := filepath.Join(dir, "same.jsonl")
	os.WriteFile(p, nil, 0644)
	if err := RegradeResults(p, p, p); err == nil {
		t.Fatal("source overwrite accepted")
	}
}
