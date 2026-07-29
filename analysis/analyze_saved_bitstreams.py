#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
import re
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

TRACE_ROOT = Path("baseline_covertChannel/results")
OUTPUT_ROOT = Path("results/generated")

METADATA_PATTERN = re.compile(
    r"^\s*(bytes|THRESHOLD|TIMES_REPEAT)\s*:\s*(\d+)\s*$",
    re.IGNORECASE,
)


def extract_trace(path: Path) -> dict[str, Any]:
    lines = path.read_text(errors="replace").splitlines()

    candidates = [
        line.strip()
        for line in lines
        if len(line.strip()) >= 64
        and set(line.strip()) <= {"0", "1"}
    ]

    if len(candidates) != 1:
        raise ValueError(
            f"{path}: expected exactly one binary trace; "
            f"found {len(candidates)}"
        )

    metadata: dict[str, int] = {}

    for line in lines:
        match = METADATA_PATTERN.match(line)
        if match:
            metadata[match.group(1).lower()] = int(match.group(2))

    bits = candidates[0]
    ones = bits.count("1")
    zeros = len(bits) - ones
    transitions = sum(
        left != right
        for left, right in zip(bits, bits[1:])
    )

    return {
        "path": str(path),
        "samples": len(bits),
        "ones": ones,
        "zeros": zeros,
        "positive_rate": ones / len(bits),
        "positive_percent": 100.0 * ones / len(bits),
        "transitions": transitions,
        "transition_rate": (
            transitions / (len(bits) - 1)
            if len(bits) > 1
            else 0.0
        ),
        "bytes": metadata.get("bytes"),
        "threshold": metadata.get("threshold"),
        "times_repeat": metadata.get("times_repeat"),
    }


def load_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    baseline = {
        "idle": TRACE_ROOT / "idle_signal.txt",
        "pageable": TRACE_ROOT / "pageable_signal.txt",
        "pinned": TRACE_ROOT / "pinned_signal.txt",
    }

    for condition, path in baseline.items():
        row = extract_trace(path)
        row.update(
            family="baseline",
            condition=condition,
            run=1,
        )
        rows.append(row)

    for path in sorted((TRACE_ROOT / "repeats").glob("*_run*.txt")):
        condition, run_text = path.stem.rsplit("_run", 1)
        row = extract_trace(path)
        row.update(
            family="repeats",
            condition=condition,
            run=int(run_text),
        )
        rows.append(row)

    for path in sorted(
        (TRACE_ROOT / "modulation").glob("window*_*.txt")
    ):
        window_text, condition = path.stem.rsplit("_", 1)
        window = int(window_text.removeprefix("window"))

        row = extract_trace(path)
        row.update(
            family="modulation",
            condition=condition,
            run=window,
        )
        rows.append(row)

    return rows


def summarize_groups(
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    groups: dict[
        tuple[str, str],
        list[dict[str, Any]],
    ] = defaultdict(list)

    for row in rows:
        groups[(row["family"], row["condition"])].append(row)

    summaries: list[dict[str, Any]] = []

    for (family, condition), group in sorted(groups.items()):
        rates = [float(row["positive_rate"]) for row in group]
        counts = [int(row["ones"]) for row in group]
        n = len(group)

        stdev_rate = statistics.stdev(rates) if n > 1 else 0.0
        stdev_count = statistics.stdev(counts) if n > 1 else 0.0

        ci_low = None
        ci_high = None

        # Exact two-sided 95% t critical value for df=2.
        # The repository currently contains three repeated runs per group.
        if n == 3:
            margin = 4.302652729 * stdev_rate / math.sqrt(n)
            mean_rate = statistics.fmean(rates)
            # A rate is bounded to the interval [0, 1].
            ci_low = max(0.0, mean_rate - margin)
            ci_high = min(1.0, mean_rate + margin)

        summaries.append(
            {
                "family": family,
                "condition": condition,
                "runs": n,
                "mean_ones": statistics.fmean(counts),
                "median_ones": statistics.median(counts),
                "stdev_ones": stdev_count,
                "minimum_ones": min(counts),
                "maximum_ones": max(counts),
                "mean_positive_rate": statistics.fmean(rates),
                "mean_positive_percent": (
                    100.0 * statistics.fmean(rates)
                ),
                "stdev_positive_rate": stdev_rate,
                "ci95_rate_low": ci_low,
                "ci95_rate_high": ci_high,
            }
        )

    return summaries


def baseline_comparisons(
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    baseline = {
        row["condition"]: row
        for row in rows
        if row["family"] == "baseline"
    }

    comparisons = []

    for left, right in [
        ("pageable", "idle"),
        ("pinned", "idle"),
        ("pinned", "pageable"),
    ]:
        left_rate = float(baseline[left]["positive_rate"])
        right_rate = float(baseline[right]["positive_rate"])

        comparisons.append(
            {
                "numerator": left,
                "denominator": right,
                "rate_ratio": left_rate / right_rate,
                "percent_increase": (
                    100.0 * (left_rate - right_rate) / right_rate
                ),
            }
        )

    return comparisons


def modulation_leave_one_out(
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    modulation = [
        row for row in rows if row["family"] == "modulation"
    ]

    labels = {"off", "on"}
    observed = {row["condition"] for row in modulation}

    if observed != labels:
        raise ValueError(
            f"expected OFF and ON modulation traces; found {observed}"
        )

    predictions: list[dict[str, Any]] = []

    for index, held_out in enumerate(modulation):
        training = [
            row
            for other_index, row in enumerate(modulation)
            if other_index != index
        ]

        off_rates = [
            float(row["positive_rate"])
            for row in training
            if row["condition"] == "off"
        ]
        on_rates = [
            float(row["positive_rate"])
            for row in training
            if row["condition"] == "on"
        ]

        if not off_rates or not on_rates:
            raise ValueError(
                "insufficient modulation windows for leave-one-out"
            )

        off_mean = statistics.fmean(off_rates)
        on_mean = statistics.fmean(on_rates)
        threshold = (off_mean + on_mean) / 2.0
        rate = float(held_out["positive_rate"])

        if on_mean >= off_mean:
            predicted = "on" if rate >= threshold else "off"
        else:
            predicted = "on" if rate <= threshold else "off"

        predictions.append(
            {
                "path": held_out["path"],
                "window": held_out["run"],
                "actual": held_out["condition"],
                "predicted": predicted,
                "positive_rate": rate,
                "training_threshold": threshold,
            }
        )

    tp = sum(
        item["actual"] == "on" and item["predicted"] == "on"
        for item in predictions
    )
    tn = sum(
        item["actual"] == "off" and item["predicted"] == "off"
        for item in predictions
    )
    fp = sum(
        item["actual"] == "off" and item["predicted"] == "on"
        for item in predictions
    )
    fn = sum(
        item["actual"] == "on" and item["predicted"] == "off"
        for item in predictions
    )

    total = len(predictions)

    return {
        "method": "leave-one-window-out threshold classification",
        "windows": total,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "accuracy": (tp + tn) / total,
        "false_positive_rate": fp / (fp + tn) if fp + tn else 0.0,
        "false_negative_rate": fn / (fn + tp) if fn + tp else 0.0,
        "predictions": predictions,
    }


def write_csv(
    path: Path,
    rows: list[dict[str, Any]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0].keys()),
        )
        writer.writeheader()
        writer.writerows(rows)


def render_markdown(
    rows: list[dict[str, Any]],
    groups: list[dict[str, Any]],
    comparisons: list[dict[str, Any]],
    modulation: dict[str, Any],
) -> str:
    lines = [
        "# Saved Thresholded-Bitstream Analysis",
        "",
        "Each saved trace contains binary threshold decisions, not "
        "raw latency samples.",
        "",
        "A `1` means the receiver measurement exceeded the configured "
        "cycle threshold.",
        "",
        "## Per-trace results",
        "",
        "| Family | Condition | Run/window | Samples | Ones | "
        "Positive rate |",
        "|---|---|---:|---:|---:|---:|",
    ]

    for row in rows:
        lines.append(
            f"| {row['family']} | {row['condition']} "
            f"| {row['run']} | {row['samples']} | {row['ones']} "
            f"| {row['positive_percent']:.6f}% |"
        )

    lines.extend(
        [
            "",
            "## Group summaries",
            "",
            "| Family | Condition | Runs | Mean ones | SD ones | "
            "Mean positive rate |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )

    for group in groups:
        lines.append(
            f"| {group['family']} | {group['condition']} "
            f"| {group['runs']} "
            f"| {group['mean_ones']:.3f} "
            f"| {group['stdev_ones']:.3f} "
            f"| {group['mean_positive_percent']:.6f}% |"
        )

    lines.extend(
        [
            "",
            "## Baseline amplification",
            "",
            "| Comparison | Rate ratio | Increase |",
            "|---|---:|---:|",
        ]
    )

    for item in comparisons:
        lines.append(
            f"| {item['numerator']} / {item['denominator']} "
            f"| {item['rate_ratio']:.6f}x "
            f"| {item['percent_increase']:.3f}% |"
        )

    lines.extend(
        [
            "",
            "## ON/OFF modulation classification",
            "",
            f"- Method: {modulation['method']}",
            f"- Windows: {modulation['windows']}",
            f"- Accuracy: {100.0 * modulation['accuracy']:.3f}%",
            f"- False-positive rate: "
            f"{100.0 * modulation['false_positive_rate']:.3f}%",
            f"- False-negative rate: "
            f"{100.0 * modulation['false_negative_rate']:.3f}%",
            "",
            "## Claim boundary",
            "",
            "These values measure threshold-positive sample counts and "
            "rates. They do not provide raw latency distributions, "
            "bandwidth, bitrate, or BER.",
            "",
        ]
    )

    return "\n".join(lines)


def main() -> int:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    rows = load_rows()
    groups = summarize_groups(rows)
    comparisons = baseline_comparisons(rows)
    modulation = modulation_leave_one_out(rows)

    payload = {
        "trace_semantics": (
            "binary threshold decisions; 1 means measured cycles "
            "exceeded the receiver threshold"
        ),
        "traces": rows,
        "group_summaries": groups,
        "baseline_comparisons": comparisons,
        "modulation_classification": modulation,
    }

    write_csv(
        OUTPUT_ROOT / "saved_bitstream_traces.csv",
        rows,
    )

    write_csv(
        OUTPUT_ROOT / "saved_bitstream_groups.csv",
        groups,
    )

    (
        OUTPUT_ROOT / "saved_bitstream_analysis.json"
    ).write_text(json.dumps(payload, indent=2) + "\n")

    markdown = render_markdown(
        rows,
        groups,
        comparisons,
        modulation,
    )

    (
        OUTPUT_ROOT / "saved_bitstream_analysis.md"
    ).write_text(markdown)

    print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
