from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))

from bit_metrics import compute, normalize_bits  # noqa: E402
from classify_states import evaluate  # noqa: E402
from common import parse_values, summarize_values  # noqa: E402
from quantify_signals import pairwise  # noqa: E402


class AnalysisTest(unittest.TestCase):
    def test_parser_and_summary(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "trace.txt"
            path.write_text("# comment\n10\nlatency_cycles: 20\nsample 2 = 30.5\n")
            values = parse_values(path)
            self.assertEqual(values, [10.0, 20.0, 30.5])
            summary = summarize_values(values, str(path))
            self.assertEqual(summary.n, 3)
            self.assertAlmostEqual(summary.median, 20.0)

    def test_nonfinite_samples_are_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "trace.txt"
            path.write_text("10\n1e309\n20\n")

            values = parse_values(path)

            self.assertEqual(values, [10.0, 20.0])
            summary = summarize_values(values, str(path))
            self.assertEqual(summary.n, 2)

    def test_pairwise_change(self) -> None:
        a = summarize_values([1, 2, 3, 4], "a")
        b = summarize_values([3, 4, 5, 6], "b")
        result = pairwise(a, b)
        self.assertGreater(result["mean_delta"], 0)
        self.assertGreater(result["cohens_d"], 0)

    def test_classifier(self) -> None:
        idle = [1, 1.1, 0.9, 1.0, 1.2, 1.1, 0.8, 1.0]
        cont = [5, 5.1, 4.9, 5.0, 5.2, 5.1, 4.8, 5.0]
        result = evaluate(idle, cont)
        self.assertEqual(result["accuracy"], 1.0)
        self.assertEqual(result["fp"], 0)
        self.assertEqual(result["fn"], 0)

    def test_bit_metrics(self) -> None:
        result = compute("0101", "0111", 0.4)
        self.assertEqual(result["bit_errors"], 1)
        self.assertAlmostEqual(result["bit_error_rate"], 0.25)
        self.assertAlmostEqual(result["gross_bitrate_bits_per_second"], 10.0)
        self.assertEqual(normalize_bits("bits: 0 1 x 0 1"), "0101")


if __name__ == "__main__":
    unittest.main()
