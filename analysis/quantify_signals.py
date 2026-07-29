#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

from common import Summary, cohens_d, summarize_file


def pairwise(a: Summary, b: Summary) -> dict[str, float | str]:
    absolute = b.mean - a.mean
    percent = 100.0 * absolute / a.mean if a.mean else math.nan
    return {
        "baseline": a.path,
        "comparison": b.path,
        "mean_delta": absolute,
        "mean_change_percent": percent,
        "cohens_d": cohens_d(a, b),
    }


def render_markdown(summaries: list[Summary], comparisons: list[dict[str, float | str]]) -> str:
    lines = [
        "# PCIe timing summary",
        "",
        "| Trace | Samples | Mean | Median | Std. dev. | 95% CI | Min | Max | P05 | P95 | MAD |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for s in summaries:
        lines.append(
            f"| {Path(s.path).name} | {s.n} | {s.mean:.6g} | {s.median:.6g} | {s.stdev:.6g} | "
            f"[{s.ci95_low:.6g}, {s.ci95_high:.6g}] | {s.minimum:.6g} | {s.maximum:.6g} | "
            f"{s.p05:.6g} | {s.p95:.6g} | {s.mad:.6g} |"
        )
    lines += ["", "## Pairwise comparisons", ""]
    for c in comparisons:
        lines.append(
            f"- `{Path(str(c['baseline'])).name}` → `{Path(str(c['comparison'])).name}`: "
            f"mean delta **{c['mean_delta']:.6g}**, change **{c['mean_change_percent']:.3f}%**, "
            f"Cohen's d **{c['cohens_d']:.4g}**"
        )
    lines += [
        "",
        "> The default parser uses the last numeric token on each non-comment line. Verify this against the CUDA log format before publication.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--numeric-index", type=int, default=-1)
    parser.add_argument("--markdown", type=Path)
    parser.add_argument("--json", type=Path)
    parser.add_argument("--csv", type=Path)
    args = parser.parse_args()

    summaries = [summarize_file(path, numeric_index=args.numeric_index) for path in args.files]
    comparisons = [pairwise(a, b) for i, a in enumerate(summaries) for b in summaries[i + 1 :]]

    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(render_markdown(summaries, comparisons), encoding="utf-8")
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(
            json.dumps(
                {"summaries": [s.to_dict() for s in summaries], "comparisons": comparisons},
                indent=2,
                allow_nan=True,
            ),
            encoding="utf-8",
        )
    if args.csv:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        with args.csv.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(summaries[0].to_dict()))
            writer.writeheader()
            writer.writerows(s.to_dict() for s in summaries)

    print(render_markdown(summaries, comparisons))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
