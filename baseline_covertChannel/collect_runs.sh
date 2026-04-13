#!/bin/bash
set -e

OUTDIR="results/repeats"
DURATION=5

mkdir -p "$OUTDIR"

echo "=== Collecting idle runs ==="
for i in 1 2 3; do
  echo "Idle run $i..."
  timeout ${DURATION}s ./receiver 2 > "$OUTDIR/idle_run${i}.txt" || true
done

echo "=== Collecting pinned runs ==="
for i in 1 2 3; do
  echo "Pinned run $i..."
  ./sender 9 > /dev/null 2>&1 &
  SENDER_PID=$!
  sleep 1
  timeout ${DURATION}s ./receiver 2 > "$OUTDIR/pinned_run${i}.txt" || true
  kill $SENDER_PID 2>/dev/null || true
  wait $SENDER_PID 2>/dev/null || true
  sleep 1
done

echo "=== Collecting pageable runs ==="
for i in 1 2 3; do
  echo "Pageable run $i..."
  ./sender 10 > /dev/null 2>&1 &
  SENDER_PID=$!
  sleep 1
  timeout ${DURATION}s ./receiver 2 > "$OUTDIR/pageable_run${i}.txt" || true
  kill $SENDER_PID 2>/dev/null || true
  wait $SENDER_PID 2>/dev/null || true
  sleep 1
done

echo "Done. Files saved in $OUTDIR"
ls -1 "$OUTDIR"
