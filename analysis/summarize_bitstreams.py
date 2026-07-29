#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import statistics
from pathlib import Path


def longest_run(bits: str, target: str) -> int:
    longest = 0
    current = 0

    for bit in bits:
        if bit == target:
            current += 1
            longest = max(longest, current)
        else:
            current = 0

    return longest


def run_lengths(bits: str) -> list[int]:
    if not bits:
        return []

    lengths: list[int] = []
    current = bits[0]
    length = 1

    for bit in bits[1:]:
        if bit == current:
            length += 1
        else:
            lengths.append(length)
            current = bit
            length = 1

    lengths.append(length)
    return lengths


def summarize(path: Path) -> dict[str, object]:
    bits = "".join(path.read_text(errors="replace").split())

    if not bits:
        raise ValueError(f"{path}: empty bitstream")

    invalid = sorted(set(bits) - {"0", "1"})

    if invalid:
        raise ValueError(
            f"{path}: contains non-binary characters: {invalid}"
        )

    ones = bits.count("1")
    zeros = len(bits) - ones
    transitions = sum(
        left != right for left, right in zip(bits, bits[1:])
    )
    runs = run_lengths(bits)

    return {
        "path": str(path),
        "bits": len(bits),
        "ones": ones,
        "zeros": zeros,
        "one_fraction": ones / len(bits),
        "zero_fraction": zeros / len(bits),
        "transitions": transitions,
        "transition_rate": (
            transitions / (len(bits) - 1)
            if len(bits) > 1
            else 0.0
        ),
        "runs": len(runs),
        "mean_run_length": statistics.fmean(runs),
        "median_run_length": statistics.median(runs),
        "longest_zero_run": longest_run(bits, "0"),
        "longest_one_run": longest_run(bits, "1"),
    }


def render_markdown(rows: list[dict[str, object]]) -> str:
    lines = [
        "# Saved bitstream summary",
        "",
        "| Trace | Bits | Ones | One fraction | Transitions | "
        "Transition rate | Longest 0 run | Longest 1 run |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]

    for row in rows:
        lines.append(
            f"| {Path(str(row['path'])).name} "
            f"| {row['bits']} "
            f"| {row['ones']} "
            f"| {float(row['one_fraction']):.6f} "
            f"| {row['transitions']} "
            f"| {float(row['transition_rate']):.6f} "
            f"| {row['longest_zero_run']} "
            f"| {row['longest_one_run']} |"
        )

    lines += [
        "",
        "> These are decoded-bitstream statistics, not PCIe latency, "
        "bitrate, BER, or independent-trial classification results.",
        "",
    ]

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--json", type=Path)
    parser.add_argument("--csv", type=Path)
    parser.add_argument("--markdown", type=Path)
    args = parser.parse_args()

    rows = [summarize(path) for path in args.files]

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(
            json.dumps({"bitstreams": rows}, indent=2) + "\n"
        )

    if args.csv:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        with args.csv.open("w", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=list(rows[0].keys()),
            )
            writer.writeheader()
            writer.writerows(rows)

    markdown = render_markdown(rows)

    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(markdown)

    print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
