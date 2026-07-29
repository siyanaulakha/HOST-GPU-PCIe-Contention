#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def normalize_bits(value: str) -> str:
    path = Path(value)
    text = path.read_text(encoding="utf-8", errors="replace") if path.is_file() else value
    bits = "".join(re.findall(r"[01]", text))
    if not bits:
        raise ValueError("no bits found")
    return bits


def compute(expected: str, observed: str, duration_seconds: float | None) -> dict[str, float | int]:
    n = min(len(expected), len(observed))
    if n == 0:
        raise ValueError("empty bitstream")
    errors = sum(a != b for a, b in zip(expected[:n], observed[:n]))
    result: dict[str, float | int] = {
        "expected_bits": len(expected),
        "observed_bits": len(observed),
        "compared_bits": n,
        "bit_errors": errors,
        "bit_error_rate": errors / n,
    }
    if duration_seconds is not None:
        if duration_seconds <= 0:
            raise ValueError("duration must be positive")
        result["duration_seconds"] = duration_seconds
        result["gross_bitrate_bits_per_second"] = n / duration_seconds
        result["goodput_bits_per_second"] = (n - errors) / duration_seconds
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected", required=True)
    parser.add_argument("--observed", required=True)
    parser.add_argument("--duration-seconds", type=float)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = compute(normalize_bits(args.expected), normalize_bits(args.observed), args.duration_seconds)
    text = json.dumps(result, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
        print(f"wrote {args.output}")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
