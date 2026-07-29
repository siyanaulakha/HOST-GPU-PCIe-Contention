# PCIe contention experiment protocol

## Freeze the environment

Record for every session:

- Git commit;
- GPU model and driver;
- CUDA toolkit and host compiler;
- PCIe generation and negotiated link width;
- CPU model, governor, and power profile;
- GPU P-state and power limit;
- transfer size, direction, repetition count, and allocation mode;
- whether displays or unrelated GPU applications were active.

Use `scripts/capture_environment.sh`.

## Conditions

Collect at least:

1. receiver idle baseline;
2. receiver with pageable sender contention;
3. receiver with pinned sender contention.

Use identical receiver parameters and equal trial counts. Prefer at least 30 independent trials per condition and repeat the complete experiment across three sessions.

## Raw data

Preserve one sample per line or a clearly documented table format. Do not overwrite raw traces. Store local raw runs under `results/raw_local/<session>/`, which is ignored by Git.

## Analysis

- verify the parser column manually;
- report sample count, mean, median, standard deviation, 95% CI, P05/P95, and MAD;
- report percent change and Cohen's d;
- calibrate classification thresholds separately from evaluation data;
- preserve expected/decoded bits and measured duration for BER/bitrate.

## Publication boundary

A single trace is evidence of an observation, not evidence of robustness. Claims about portability, exploitability, or cross-VM operation require dedicated experiments.
