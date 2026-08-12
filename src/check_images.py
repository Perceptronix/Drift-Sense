import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from pathlib import Path

ROOT = Path(r"D:\Semicon\SEMICON-2026-Localization-DS5-v1")
OUTPUT = ROOT / "dataset_check.png"

images = sorted(ROOT.rglob("*_material.png"))

print("Total images:", len(images))

indices = [0, 1, 10, 100, 1000, 5000, 10000]
valid = [i for i in indices if i < len(images)]

fig, axes = plt.subplots(2, 4, figsize=(16, 8))
axes = axes.ravel()

for plot_idx, i in enumerate(valid):
    path = images[i]
    img = np.array(Image.open(path))

    print(f"\nSample {i}: {path.name}")
    print("Shape:", img.shape)
    print("Dtype:", img.dtype)
    print("Min:", img.min())
    print("Max:", img.max())
    print("Mean:", img.mean())
    print("Std:", img.std())
    print("Unique pixels:", len(np.unique(img)))

    axes[plot_idx].imshow(img, cmap="gray")
    axes[plot_idx].set_title(f"Sample {i}")
    axes[plot_idx].axis("off")

for i in range(len(valid), len(axes)):
    axes[i].axis("off")

plt.tight_layout()
plt.savefig(OUTPUT, dpi=150)
plt.close()

print("\nSaved visualization:")
print(OUTPUT)