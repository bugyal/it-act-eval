#!/bin/sh
# Historical multi-leg launcher intentionally disabled: choose one model explicitly.
printf '%s\n' 'This historical paid multi-model launcher is disabled. Use eval/run_sweep.sh with explicit TAX_EVAL_BACKEND, TAX_EVAL_MODEL, TAX_EVAL_CONFIRM_RUN=yes.' >&2
exit 2
