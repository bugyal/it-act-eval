#!/bin/sh
# One explicitly selected model only. Never automatically launch a paid sweep.
set -eu
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
: "${TAX_EVAL_BACKEND:?Set TAX_EVAL_BACKEND to one backend}"
: "${TAX_EVAL_MODEL:?Set TAX_EVAL_MODEL to one model ID}"
: "${TAX_EVAL_CONFIRM_RUN:?Set TAX_EVAL_CONFIRM_RUN=yes to authorize model requests}"
if [ "$TAX_EVAL_CONFIRM_RUN" != yes ]; then
  printf '%s\n' 'TAX_EVAL_CONFIRM_RUN must equal yes' >&2
  exit 2
fi
cd "$SCRIPT_DIR"
exec go run ./cmd/tax-eval -repo "$REPO_ROOT" -backend "$TAX_EVAL_BACKEND" -model "$TAX_EVAL_MODEL" "$@"
