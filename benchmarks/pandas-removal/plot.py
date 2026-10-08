import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

root = Path(__file__).parent
summary = json.loads((root / "results/summary.json").read_text())
labels, ratios, values = [], [], []
for row in summary[:3]:
    before, after = row["pandas"]["median_ms"], row["records"]["median_ms"]
    labels.append(f"Time · {row['size']} views")
    ratios.append(after / before * 100)
    values.append(f"{before:.2f} → {after:.2f} ms")
row = summary[2]
before, after = row["pandas"]["peak_rss_kib"] / 1024, row["records"]["peak_rss_kib"] / 1024
labels.append("Peak RSS · 300 views")
ratios.append(after / before * 100)
values.append(f"{before:.1f} → {after:.1f} MiB")

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
fig, ax = plt.subplots(figsize=(9, 3.2), layout="constrained")
ys = list(range(4))[::-1]
ax.barh(ys, [100] * 4, color="#e2e8f0", height=0.55, label="#706")
ax.barh(ys, ratios, color="#2563eb", height=0.36, label="Python records")
for y, ratio, value in zip(ys, ratios, values, strict=True):
    ax.text(103, y, value, va="center", color="#0f172a", fontsize=10)
    ax.text(ratio - 2, y, f"{ratio:.0f}%", va="center", ha="right", color="white", fontsize=9)
ax.set_yticks(ys, labels)
ax.set_xlim(0, 146)
ax.set_xticks([0, 25, 50, 75, 100], ["0%", "25%", "50%", "75%", "100%"])
ax.set_xlabel("Gray: #706 (100%). Blue: Python records. Lower is better.", loc="left")
ax.set_title("Remove pandas: less memory per process, less work per call", loc="left", weight="bold", pad=16)
ax.tick_params(axis="both", length=0)
for spine in ax.spines.values():
    spine.set_visible(False)
fig.savefig(root / "comparison.png", dpi=180, facecolor="white")
