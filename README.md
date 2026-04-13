# HOST-GPU-PCIe-Contention

This repository studies PCIe bus contention between the host and GPU as a basis for observable side-channel behavior. The baseline experiment demonstrates that contention on the shared host–GPU PCIe path can be externally observed through transfer latency measurements, and that pinned-memory transfers amplify the signal more clearly than pageable-memory transfers.

## Repository Overview

The repository currently contains a baseline implementation and saved experiment outputs.

```text
HOST-GPU-PCIe-Contention/
└── baseline_covertChannel/
    ├── src/
    │   ├── sender.cu
    │   └── receiver.cu
    ├── scripts/
    │   ├── analyze_bits.py
    │   ├── collect_runs.sh
    │   ├── modulated_demo.sh
    │   ├── plot_modulation.py
    │   ├── plot_repeats.py
    │   ├── summarize_modulation.py
    │   └── summarize_results.py
    ├── results/
    │   ├── repeats/
    │   ├── modulation/
    │   ├── idle_signal.txt
    │   ├── pageable_signal.txt
    │   ├── pinned_signal.txt
    │   ├── bitstream_preview.png
    │   ├── ones_bar.png
    │   └── notes.txt
    ├── Makefile
    └── .gitignore
```
## Baseline Experiment

The baseline experiment consists of two CUDA programs:

* **Receiver**: measures transfer latency and records timing behavior
* **Sender**: generates PCIe contention to influence the receiver’s observations

The main idea is to compare receiver-side timing under different conditions:

* idle / no sender activity
* contention from sender activity
* pageable-memory transfer behavior
* pinned-memory transfer behavior

This establishes whether shared PCIe resource contention is measurable and whether it can serve as a side-channel signal.

## Key Observations from the Baseline

The baseline results show:

* measurable latency differences between idle and contention conditions
* clearer signal behavior with pinned-memory transfers compared to pageable-memory transfers
* observable ON/OFF modulation patterns under sender-driven activity

These results support the feasibility of PCIe-contention-based side-channel observation.

## Folder Description

### `baseline_covertChannel/src/`

Contains the CUDA source code for the sender and receiver programs.

### `baseline_covertChannel/scripts/`

Contains helper scripts for:

* collecting repeated runs
* analyzing extracted bit patterns
* summarizing results
* plotting repeat and modulation results

### `baseline_covertChannel/results/`

Contains saved outputs and plots from the baseline experiment.

* `repeats/` stores repeated-run outputs and related plots
* `modulation/` stores outputs from sender ON/OFF modulation experiments
* top-level `.txt` and `.png` files summarize baseline observations

## Build Instructions

### Requirements

* NVIDIA GPU with CUDA support
* CUDA toolkit
* `nvcc`
* compatible host compiler for CUDA 11.5
  In this setup, `g++-10` was used as the host compiler.

### Build

From inside `baseline_covertChannel`:

```bash
make clean
make
```

This generates:

* `receiver.out`
* `sender.out`

## Running the Baseline

From inside `baseline_covertChannel`:

```bash
./receiver.out
./receiver.out 1
./sender.out
./sender.out 1
```

Depending on the experiment, the receiver may be run alone for baseline measurement or together with the sender to induce contention.

## Analysis

The scripts in `scripts/` can be used to:

* collect repeated measurements
* analyze observed bit patterns
* summarize modulation windows
* generate plots for repeated runs and modulation experiments

Example workflow:

1. run receiver in idle and contention settings
2. save output traces
3. process traces using the analysis scripts
4. generate plots to compare observable behavior

## Results Included

The repository currently includes saved baseline outputs such as:

* idle signal traces
* pageable and pinned signal traces
* repeated-run measurements
* modulation-window outputs
* summary plots

These are retained to document the baseline behavior and support reproducibility.

## Extension Plan

The `main` branch preserves the baseline experiment.

Future extended work may be added separately to avoid modifying the baseline implementation directly. This can include:

* raw latency plotting in cycles
* bitrate and BER characterization
* message decoding experiments
* modified modulation or transfer configurations

## Notes

This repository is organized to preserve the baseline experiment cleanly before further extension. The baseline folder is intended to remain a stable reference point for subsequent experiments and analysis.

## Author

Siya Naulakha

```
```
