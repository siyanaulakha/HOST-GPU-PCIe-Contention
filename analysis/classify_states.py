#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import parse_values


def split(values: list[float]) -> tuple[list[float], list[float]]:
    if len(values) < 4:
        raise ValueError("each trace needs at least four samples for calibration/evaluation")
    cut = len(values) // 2
    return values[:cut], values[cut:]


def classify(value: float, threshold: float, high_is_contended: bool) -> int:
    return int(value >= threshold) if high_is_contended else int(value <= threshold)


def evaluate(idle: list[float], contended: list[float]) -> dict[str, float | int | bool]:
    idle_cal, idle_eval = split(idle)
    cont_cal, cont_eval = split(contended)
    idle_center = sum(idle_cal) / len(idle_cal)
    cont_center = sum(cont_cal) / len(cont_cal)
    threshold = (idle_center + cont_center) / 2.0
    high_is_contended = cont_center >= idle_center

    tn = sum(classify(v, threshold, high_is_contended) == 0 for v in idle_eval)
    fp = len(idle_eval) - tn
    tp = sum(classify(v, threshold, high_is_contended) == 1 for v in cont_eval)
    fn = len(cont_eval) - tp
    total = tn + fp + tp + fn
    accuracy = (tn + tp) / total if total else 0.0
    fpr = fp / (fp + tn) if fp + tn else 0.0
    fnr = fn / (fn + tp) if fn + tp else 0.0
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "threshold": threshold,
        "high_is_contended": high_is_contended,
        "calibration_idle_samples": len(idle_cal),
        "calibration_contended_samples": len(cont_cal),
        "evaluation_idle_samples": len(idle_eval),
        "evaluation_contended_samples": len(cont_eval),
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "tp": tp,
        "accuracy": accuracy,
        "false_positive_rate": fpr,
        "false_negative_rate": fnr,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("idle", type=Path)
    parser.add_argument("contended", type=Path)
    parser.add_argument("--numeric-index", type=int, default=-1)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = evaluate(
        parse_values(args.idle, numeric_index=args.numeric_index),
        parse_values(args.contended, numeric_index=args.numeric_index),
    )
    text = json.dumps(result, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
        print(f"wrote {args.output}")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
