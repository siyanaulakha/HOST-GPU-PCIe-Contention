#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
TRACE_DIR="${1:-baseline_covertChannel/results}"
OUT_DIR="${2:-results/generated}"
mkdir -p "$OUT_DIR"
python3 analysis/quantify_signals.py \
  "$TRACE_DIR/idle_signal.txt" \
  "$TRACE_DIR/pageable_signal.txt" \
  "$TRACE_DIR/pinned_signal.txt" \
  --markdown "$OUT_DIR/timing_summary.md" \
  --json "$OUT_DIR/timing_summary.json" \
  --csv "$OUT_DIR/timing_summary.csv"
python3 analysis/classify_states.py \
  "$TRACE_DIR/idle_signal.txt" \
  "$TRACE_DIR/pinned_signal.txt" \
  --output "$OUT_DIR/idle_vs_pinned_classification.json"
