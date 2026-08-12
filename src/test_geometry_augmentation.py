import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from localization_dataset import LocalizationDataset
from augmentations import augment_sample


dataset = LocalizationDataset(
    start=0,
    end=5000,
    training=False
)

sample = dataset[0]

image = sample["image"].squeeze(0).numpy()

contours = [
    np.asarray(c, dtype=np.float32)
    for c in sample["target"]["contours"]
]

augmented, new_contours = augment_sample(
    image,
    contours,
    geometry=True,
    noise=False
)

fig, axes = plt.subplots(
    1,
    2,
    figsize=(14, 7)
)

axes[0].imshow(
    image,
    cmap="gray"
)

for contour in contours:
    if len(contour) > 1:
        axes[0].plot(
            contour[:, 0],
            contour[:, 1],
            linewidth=0.5
        )

axes[0].set_title("Original + Ground Truth")
axes[0].axis("off")


axes[1].imshow(
    augmented,
    cmap="gray"
)

for contour in new_contours:
    if len(contour) > 1:
        axes[1].plot(
            contour[:, 0],
            contour[:, 1],
            linewidth=0.5
        )

axes[1].set_title(
    "Augmented + Transformed Ground Truth"
)

axes[1].axis("off")

plt.tight_layout()

output = ROOT / "outputs" / "geometry_test.png"

output.parent.mkdir(
    exist_ok=True
)

plt.savefig(
    output,
    dpi=150,
    bbox_inches="tight"
)

plt.close()

print(f"Saved: {output}")