#!/bin/bash
set -e

OUTDIR="results/modulation"
DURATION=5

mkdir -p "$OUTDIR"

run_off() {
  local name=$1
  echo "Running OFF window: $name"
  timeout ${DURATION}s ./receiver 2 > "$OUTDIR/${name}.txt" || true
}

run_on() {
  local name=$1
  echo "Running ON window: $name"
  ./sender 9 > /dev/null 2>&1 &
  SENDER_PID=$!
  sleep 1
  timeout ${DURATION}s ./receiver 2 > "$OUTDIR/${name}.txt" || true
  kill $SENDER_PID 2>/dev/null || true
  wait $SENDER_PID 2>/dev/null || true
  sleep 1
}

run_off "window1_off"
run_on  "window2_on"
run_off "window3_off"
run_on  "window4_on"
run_off "window5_off"
run_on  "window6_on"

echo "Done. Files saved in $OUTDIR"
ls -1 "$OUTDIR"
