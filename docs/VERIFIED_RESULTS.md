# Verified PCIe Contention Results

## Experimental interpretation

The saved traces contain binary threshold decisions rather than raw latency
samples. Each trace contains 200,000 receiver measurements.

A value of `1` indicates that the measured host-to-device transfer time exceeded
the configured threshold of 30,000 cycles.

The transfer size recorded in the traces is 32,768 bytes.

## Repeated-condition experiment

Three independent saved traces are available for each condition.

| Condition | Mean positive rate | Standard deviation |
|---|---:|---:|
| Idle | 0.5090% | 0.4656 percentage points |
| Pageable contention | 0.2795% | 0.0670 percentage points |
| Pinned contention | 66.3998% | 0.9290 percentage points |

Pinned contention therefore produced approximately 130.45 times the
threshold-positive event rate observed during the repeated idle experiment.

Pageable contention was not consistently distinguishable from idle in the saved
repeated traces and should be treated as an inconclusive result.

## ON/OFF modulation experiment

Three sender-OFF and three sender-ON windows were evaluated.

| State | Mean positive rate |
|---|---:|
| OFF | 1.9307% |
| ON | 68.8635% |

A leave-one-window-out threshold classifier correctly separated all six saved
windows:

- Correct windows: 6/6
- False positives: 0
- False negatives: 0

This is a proof-of-concept evaluation over six windows, not a claim of general
100% real-world classification accuracy.

## Baseline traces

The original single baseline traces showed:

| Condition | Positive rate |
|---|---:|
| Idle | 0.1080% |
| Pageable contention | 0.5085% |
| Pinned contention | 2.5380% |

These single traces were collected under conditions that differ from the later
repeated experiment and are therefore reported separately.

## Claim boundaries

The saved data supports claims about threshold-positive timing-event rates.

It does not currently support claims about:

- complete raw latency distributions;
- PCIe bandwidth degradation;
- covert-channel bitrate;
- bit-error rate;
- reliable pageable-contention classification;
- production-level classification accuracy.
