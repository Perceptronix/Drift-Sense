import sys
from pathlib import Path

import cv2
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from localization_dataset import LocalizationDataset
from augmentations import augment


dataset = LocalizationDataset(start=0, end=5000)

sample = dataset[0]

image = sample["image"].squeeze(0).numpy()

low = augment(image, "low")
medium = augment(image, "medium")
high = augment(image, "high")

fig, axes = plt.subplots(1, 4, figsize=(16, 4))

axes[0].imshow(image, cmap="gray")
axes[0].set_title("Original")

axes[1].imshow(low, cmap="gray")
axes[1].set_title("Low")

axes[2].imshow(medium, cmap="gray")
axes[2].set_title("Medium")

axes[3].imshow(high, cmap="gray")
axes[3].set_title("High")

for ax in axes:
    ax.axis("off")

output = ROOT / "outputs"
output.mkdir(exist_ok=True)

path = output / "augmentation_test.png"

plt.tight_layout()
plt.savefig(path, dpi=150)
plt.close()

print(f"Saved: {path}")