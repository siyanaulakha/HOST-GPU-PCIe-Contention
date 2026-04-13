from pathlib import Path
import matplotlib.pyplot as plt
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

means = {}
labels = []
values = []

for group, files in groups.items():
    counts = []
    for f in files:
        bits = extract_bits(f)
        ones = sum(bits)
        counts.append(ones)
        labels.append(f.stem)
        values.append(ones)
    means[group] = stats.mean(counts)

plt.figure(figsize=(10, 5))
plt.bar(labels, values)
plt.xticks(rotation=45)
plt.ylabel("Number of detected 1s")
plt.title("Detected contention events across repeated runs")
plt.tight_layout()
plt.savefig("results/repeats/all_runs_bar.png", dpi=300)
plt.close()

plt.figure(figsize=(7, 5))
mean_labels = list(means.keys())
mean_values = [means[k] for k in mean_labels]
plt.bar(mean_labels, mean_values)
plt.ylabel("Mean number of detected 1s")
plt.title("Mean contention events by condition")
plt.tight_layout()
plt.savefig("results/repeats/mean_runs_bar.png", dpi=300)
plt.close()

print("Saved:")
print(" - results/repeats/all_runs_bar.png")
print(" - results/repeats/mean_runs_bar.png")
