from __future__ import annotations

import math
import re
import statistics
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

NUMBER = re.compile(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?")


@dataclass(frozen=True)
class Summary:
    path: str
    n: int
    mean: float
    median: float
    stdev: float
    minimum: float
    maximum: float
    p05: float
    p95: float
    mad: float
    ci95_low: float
    ci95_high: float

    def to_dict(self) -> dict[str, str | int | float]:
        return asdict(self)


def percentile(values: list[float], q: float) -> float:
    if not values:
        return math.nan
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = q * (len(ordered) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def parse_values(path: Path, *, numeric_index: int = -1) -> list[float]:
    values: list[float] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        # A long line containing only 0/1 characters is a decoded
        # bitstream, not a numeric latency sample.
        if len(stripped) >= 64 and set(stripped) <= {"0", "1"}:
            raise ValueError(
                f"{path}:{line_no} is a binary bitstream, "
                "not a per-sample timing trace"
            )

        matches = NUMBER.findall(stripped)
        if not matches:
            continue
        try:
            token = matches[numeric_index]
        except IndexError as exc:
            raise ValueError(
                f"line {line_no} in {path} has only "
                f"{len(matches)} numeric tokens"
            ) from exc

        value = float(token)

        if not math.isfinite(value):
            print(
                f"WARNING: skipping non-finite sample in "
                f"{path}:{line_no}: {token}",
                file=sys.stderr,
            )
            continue

        values.append(value)
    return values


def summarize_values(values: list[float], path: str = "<memory>") -> Summary:
    if not values:
        raise ValueError(f"no numeric samples found in {path}")
    n = len(values)
    mean = statistics.fmean(values)
    stdev = statistics.stdev(values) if n > 1 else 0.0
    med = statistics.median(values)
    abs_dev = [abs(v - med) for v in values]
    half = 1.96 * stdev / math.sqrt(n) if n > 1 else 0.0
    return Summary(
        path=path,
        n=n,
        mean=mean,
        median=med,
        stdev=stdev,
        minimum=min(values),
        maximum=max(values),
        p05=percentile(values, 0.05),
        p95=percentile(values, 0.95),
        mad=statistics.median(abs_dev),
        ci95_low=mean - half,
        ci95_high=mean + half,
    )


def summarize_file(path: Path, *, numeric_index: int = -1) -> Summary:
    return summarize_values(parse_values(path, numeric_index=numeric_index), str(path))


def cohens_d(a: Summary, b: Summary) -> float:
    if a.n < 2 or b.n < 2:
        return math.nan
    pooled_variance = (((a.n - 1) * a.stdev**2) + ((b.n - 1) * b.stdev**2)) / (a.n + b.n - 2)
    pooled = math.sqrt(pooled_variance)
    return (b.mean - a.mean) / pooled if pooled else math.nan
