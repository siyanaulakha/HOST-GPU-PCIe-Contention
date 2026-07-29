# Host–GPU PCIe Contention Characterization

CUDA experiments for measuring receiver-visible timing changes caused by contention on a shared host–GPU PCIe transfer path.

## Current evidence boundary

The public baseline contains CUDA sender/receiver programs, repeat/modulation scripts, and saved idle, pageable, and pinned traces. The available repository organization supports a qualitative claim that contention is observable and that pinned-memory behavior produced clearer separation in the evaluated setup.

It does **not** yet support a reviewed numerical claim for bitrate, bit-error rate, cross-VM operation, or portability across systems.

## Repository hygiene

The original tree appears to track compiled `receiver`/`sender` files and a backup file such as `idle_signal.txt~`. Remove generated binaries and editor backups from Git history going forward. Keep raw measurements, plots, and reviewed summaries clearly separated.

## CPU-only analysis

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v

python3 analysis/quantify_signals.py \
  baseline_covertChannel/results/idle_signal.txt \
  baseline_covertChannel/results/pageable_signal.txt \
  baseline_covertChannel/results/pinned_signal.txt \
  --markdown results/generated/timing_summary.md \
  --json results/generated/timing_summary.json \
  --csv results/generated/timing_summary.csv
```

The parser treats the last numeric token on each non-comment line as the measurement by default. Verify this policy against the CUDA output format before publication.

## State classification

```bash
python3 analysis/classify_states.py \
  baseline_covertChannel/results/idle_signal.txt \
  baseline_covertChannel/results/pinned_signal.txt \
  --output results/generated/state_classification.json
```

The classifier calibrates on the first half of each trace and evaluates on the second half. This is a simple reproducible baseline, not a security-proof classifier.

## Bit metrics

```bash
python3 analysis/bit_metrics.py \
  --expected 01010101 \
  --observed 01000101 \
  --duration-seconds 0.8
```

Only report bitrate and BER when the expected bitstream, decoded bitstream, and measured transmission duration are preserved.

## GPU reproduction

```bash
cd baseline_covertChannel
make clean
make
```

Capture the environment before every session:

```bash
bash scripts/capture_environment.sh results/raw_local/environment.txt
```

Record GPU, driver, CUDA toolkit, host compiler, PCIe generation/link width, transfer size/direction, allocation mode, power state, trial count, and experiment session.

## Claim policy

Safe after reviewed trace analysis:

- host–GPU contention was receiver-observable in the evaluated setup;
- pinned-memory measurements showed stronger timing separation than pageable-memory measurements, when supported by the computed statistics;
- sender-driven ON/OFF modulation was visible in saved traces.

Requires new measurement:

- channel bitrate and BER;
- false-positive/false-negative rates across independent sessions;
- cross-process or cross-VM behavior;
- generalization across systems;
- practical exploitability.
