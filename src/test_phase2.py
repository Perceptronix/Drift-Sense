import sys
from pathlib import Path

import cv2
import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from config import DATASET_ROOT
from localization_dataset import LocalizationDataset


dataset = LocalizationDataset(
    root=DATASET_ROOT,
    start=0,
    end=5000,
    variants=5,
    augment=True
)

sample_ids = [0, 1, 2, 3, 4]

fig, axes = plt.subplots(
    5,
    5,
    figsize=(18, 18)
)

for row, base_id in enumerate(sample_ids):

    for variant in range(5):

        index = base_id * 5 + variant

        sample = dataset[index]

        image = sample["image"].squeeze().numpy()
        target = sample["target"]

        ax = axes[row, variant]

        ax.imshow(
            image,
            cmap="gray"
        )

        for contour in target["contours"]:
            pts = np.asarray(
                contour,
                dtype=np.float32
            )

            if len(pts) > 1:
                ax.plot(
                    pts[:, 0],
                    pts[:, 1],
                    linewidth=0.5
                )

        if variant == 0:
            title = "Original"
        elif variant == 1:
            title = "Low"
        elif variant == 2:
            title = "Medium"
        elif variant == 3:
            title = "High"
        else:
            title = "Medium 2"

        ax.set_title(
            f"Sample {base_id} - {title}"
        )

        ax.axis("off")

plt.tight_layout()

output = ROOT / "outputs" / "phase2_final.png"

output.parent.mkdir(
    parents=True,
    exist_ok=True
)

plt.savefig(
    output,
    dpi=150,
    bbox_inches="tight"
)

plt.close()

print("Saved:", output)