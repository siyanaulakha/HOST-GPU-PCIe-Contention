from pathlib import Path

BASE = Path("results/modulation")

def extract_bits(path: Path):
    text = path.read_text(errors="ignore")
    return [1 if ch == "1" else 0 for ch in text if ch in "01"]

files = sorted(BASE.glob("window*.txt"))

print("=== Modulation Summary ===")
for f in files:
    bits = extract_bits(f)
    total = len(bits)
    ones = sum(bits)
    ratio = ones / total if total else 0.0
    print(f"{f.name}: total={total}, ones={ones}, one_ratio={ratio:.6f}")
