import sys
from pathlib import Path

import matplotlib.pyplot as plt
import torch

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from heatmap import create_heatmap, heatmap_to_point


x = 156.0
y = 187.0

heatmap = create_heatmap(
    x,
    y,
    size=64,
    sigma=2.0
)

prediction = heatmap_to_point(heatmap)

print("Ground truth:")
print(f"X: {x}")
print(f"Y: {y}")

print("\nHeatmap:")
print("Shape:", heatmap.shape)
print("Min:", heatmap.min().item())
print("Max:", heatmap.max().item())

print("\nRecovered point:")
print("X:", prediction[0].item())
print("Y:", prediction[1].item())

plt.figure(figsize=(6, 6))

plt.imshow(
    heatmap.squeeze().numpy(),
    cmap="hot"
)

plt.title("Localization Heatmap")
plt.xlabel("X")
plt.ylabel("Y")

plt.tight_layout()

output = ROOT / "outputs" / "heatmap_test.png"

plt.savefig(
    output,
    dpi=150
)

plt.close()

print("\nSaved:")
print(output)