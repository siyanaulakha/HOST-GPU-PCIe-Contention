from pathlib import Path
import matplotlib.pyplot as plt
import statistics as stats

FILES = {
    "Idle": "results/idle_signal.txt",
    "Pageable": "results/pageable_signal.txt",
    "Pinned": "results/pinned_signal.txt",
}

def extract_bits(path):
    text = Path(path).read_text(errors="ignore")
    bits = [int(ch) for ch in text if ch in "01"]
    return bits

summary = {}

for label, path in FILES.items():
    bits = extract_bits(path)
    ones = sum(bits)
    zeros = len(bits) - ones
    ratio = ones / len(bits) if bits else 0.0

    summary[label] = {
        "bits": bits,
        "total": len(bits),
        "ones": ones,
        "zeros": zeros,
        "one_ratio": ratio,
    }

print("\n=== Summary ===")
for label, s in summary.items():
    print(f"{label}: total={s['total']}, ones={s['ones']}, zeros={s['zeros']}, one_ratio={s['one_ratio']:.6f}")

# -------- Plot 1: total ones --------
labels = list(summary.keys())
ones_counts = [summary[k]["ones"] for k in labels]

plt.figure(figsize=(7, 5))
plt.bar(labels, ones_counts)
plt.ylabel("Number of detected 1s")
plt.title("Detected contention events by condition")
plt.tight_layout()
plt.savefig("results/ones_bar.png", dpi=300)
plt.close()

# -------- Plot 2: first 300 bits as traces --------
N = 300
plt.figure(figsize=(10, 5))
for i, label in enumerate(labels):
    bits = summary[label]["bits"][:N]
    y = [b + i * 1.5 for b in bits]  # vertical offset for readability
    x = list(range(len(bits)))
    plt.step(x, y, where="post", label=label)

plt.xlabel("Sample index")
plt.ylabel("Bitstream (offset)")
plt.title("First 300 detected samples")
plt.legend()
plt.tight_layout()
plt.savefig("results/bitstream_preview.png", dpi=300)
plt.close()

print("\nSaved:")
print(" - results/ones_bar.png")
print(" - results/bitstream_preview.png")
