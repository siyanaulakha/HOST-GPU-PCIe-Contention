#!/usr/bin/env bash
set -euo pipefail
OUT="${1:-results/raw_local/environment.txt}"
mkdir -p "$(dirname "$OUT")"
{
  echo "timestamp=$(date -Is)"
  echo "hostname=$(hostname)"
  echo "kernel=$(uname -a)"
  echo "git_commit=$(git rev-parse HEAD 2>/dev/null || echo unknown)"
  echo
  echo "=== NVIDIA SMI ==="
  nvidia-smi || true
  echo
  echo "=== NVCC ==="
  nvcc --version || true
  echo
  echo "=== PCIe GPU link ==="
  nvidia-smi --query-gpu=name,driver_version,pci.bus_id,pcie.link.gen.current,pcie.link.gen.max,pcie.link.width.current,pcie.link.width.max,pstate,power.limit --format=csv || true
  echo
  echo "=== Compiler ==="
  g++ --version | head -n 1 || true
  gcc --version | head -n 1 || true
  echo
  echo "=== CPU ==="
  lscpu || true
} | tee "$OUT"
