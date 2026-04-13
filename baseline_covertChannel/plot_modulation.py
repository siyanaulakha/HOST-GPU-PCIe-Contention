from pathlib import Path
import matplotlib.pyplot as plt

BASE = Path("results/modulation")

def extract_bits(path: Path):
    text = path.read_text(errors="ignore")
    return [1 if ch == "1" else 0 for ch in text if ch in "01"]

files = sorted(BASE.glob("window*.txt"))
labels = []
values = []

for f in files:
    bits = extract_bits(f)
    labels.append(f.stem)
    values.append(sum(bits))

plt.figure(figsize=(9,5))
plt.bar(labels, values)
plt.xticks(rotation=30)
plt.ylabel("Number of detected 1s")
plt.title("ON/OFF modulation demo")
plt.tight_layout()
plt.savefig("results/modulation/modulation_bar.png", dpi=300)
print("Saved results/modulation/modulation_bar.png")
