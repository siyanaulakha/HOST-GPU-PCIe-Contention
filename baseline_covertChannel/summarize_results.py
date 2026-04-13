from pathlib import Path
import statistics as stats

BASE = Path("results/repeats")

groups = {
    "Idle": sorted(BASE.glob("idle_run*.txt")),
    "Pageable": sorted(BASE.glob("pageable_run*.txt")),
    "Pinned": sorted(BASE.glob("pinned_run*.txt")),
}

def extract_bits(path: Path):
    text = path.read_text(errors="ignore")
    return [1 if ch == "1" else 0 for ch in text if ch in "01"]

def summarize_group(name, files):
    print(f"\n=== {name} ===")
    one_counts = []
    ratios = []

    for f in files:
        bits = extract_bits(f)
        total = len(bits)
        ones = sum(bits)
        ratio = ones / total if total else 0.0
        one_counts.append(ones)
        ratios.append(ratio)
        print(f"{f.name}: total={total}, ones={ones}, one_ratio={ratio:.6f}")

    if one_counts:
        print(f"{name} mean ones = {stats.mean(one_counts):.2f}")
        print(f"{name} std  ones = {stats.stdev(one_counts):.2f}" if len(one_counts) > 1 else f"{name} std ones = 0")
        print(f"{name} mean ratio = {stats.mean(ratios):.6f}")
        print(f"{name} std  ratio = {stats.stdev(ratios):.6f}" if len(ratios) > 1 else f"{name} std ratio = 0")

for name, files in groups.items():
    summarize_group(name, files)

