package taxeval

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestLaunchScriptsDoNotSourcePrivateEnvOrSweepProviders(t *testing.T) {
	for _, name := range []string{"run_sweep.sh", "run_finish_legs.sh", "run_finish_legs2.sh"} {
		raw, err := os.ReadFile(filepath.Join(".", name))
		if err != nil {
			t.Fatal(err)
		}
		script := string(raw)
		for _, forbidden := range []string{"Projects/tax-model", ".hermes/", "/tmp/tax-eval", "source ", "openrouter/deepseek", "claude-opus-5-5"} {
			if strings.Contains(script, forbidden) {
				t.Errorf("%s contains legacy private/sweep reference %q", name, forbidden)
			}
		}
	}
}
