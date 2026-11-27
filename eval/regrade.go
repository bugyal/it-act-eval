package taxeval

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
)

// StrictGraderVersion identifies the historical entity-extraction Grade implementation.
// It is not the later keyword grader; changing Grade's semantics requires a new version.
const StrictGraderVersion = "strict-v1"

// RegradeResults grades each original row independently against the named split.
// It never selects a best response, merges attempts, or modifies the source.
func RegradeResults(splitPath, inputPath, outputPath string) error {
	inAbs, err := filepath.Abs(inputPath)
	if err != nil {
		return err
	}
	outAbs, err := filepath.Abs(outputPath)
	if err != nil {
		return err
	}
	if inAbs == outAbs {
		return fmt.Errorf("regrade output must differ from input")
	}
	tasks, err := LoadTasks(splitPath)
	if err != nil {
		return err
	}
	byID := make(map[string]Task, len(tasks))
	for _, task := range tasks {
		if _, exists := byID[task.ID]; exists {
			return fmt.Errorf("duplicate task id %s in split", task.ID)
		}
		byID[task.ID] = task
	}
	f, err := os.Open(inputPath)
	if err != nil {
		return err
	}
	defer f.Close()
	var output bytes.Buffer
	sc := bufio.NewScanner(f)
	sc.Buffer(make([]byte, 1024*1024), 4*1024*1024)
	lineNo := 0
	for sc.Scan() {
		lineNo++
		var rec ResultRecord
		if err := json.Unmarshal(sc.Bytes(), &rec); err != nil {
			return fmt.Errorf("result line %d: %w", lineNo, err)
		}
		task, ok := byID[rec.ID]
		if !ok || rec.Question != task.Question {
			return fmt.Errorf("result line %d: task id/question not in split: %s", lineNo, rec.ID)
		}
		rec.Gold, rec.AnswerType, rec.FactKey, rec.Template, rec.TaskType = task.Answer, task.AnswerType, task.FactKey, task.Template, task.TaskType
		rec.GraderVersion = StrictGraderVersion
		if rec.RawResponse != "" {
			g := Grade(task, rec.RawResponse)
			rec.Pass, rec.ScoreParts, rec.Graded = g.Pass, g.ScoreParts, g.Graded
			rec.Missing, rec.ExtractedGold, rec.ExtractedModel = g.MissingGold, g.ExtractGold, g.ExtractModel
			rec.Error = g.Reason
		} else {
			// No model response: retain the original API error and do not grade.
			rec.Pass, rec.ScoreParts, rec.Graded = false, 0, false
			rec.Missing, rec.ExtractedGold, rec.ExtractedModel = nil, "", ""
		}
		b, err := json.Marshal(rec)
		if err != nil {
			return err
		}
		output.Write(b)
		output.WriteByte('\n')
	}
	if err := sc.Err(); err != nil {
		return err
	}
	if lineNo == 0 {
		return fmt.Errorf("empty results file")
	}
	out, err := os.OpenFile(outputPath, os.O_WRONLY|os.O_CREATE|os.O_EXCL, 0644)
	if err != nil {
		return err
	}
	if _, err = out.Write(output.Bytes()); err != nil {
		out.Close()
		os.Remove(outputPath)
		return err
	}
	if err = out.Close(); err != nil {
		os.Remove(outputPath)
		return err
	}
	return nil
}
