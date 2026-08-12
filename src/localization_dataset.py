import json
import sys
from pathlib import Path

import cv2
import numpy as np
import torch
from torch.utils.data import Dataset

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from config import DATASET_ROOT
from augmentations import augment_sample


class LocalizationDataset(Dataset):
    def __init__(
        self,
        root=DATASET_ROOT,
        start=0,
        end=5000,
        variants=5,
        augment=True
    ):
        self.root = Path(root)
        self.variants = variants
        self.augment = augment
        self.samples = []

        image_root = self.root / "images"
        gt_root = self.root / "ground_truth"

        images = sorted(image_root.rglob("*.tiff"))

        for image_path in images:
            try:
                index = int(image_path.stem)
            except ValueError:
                continue

            if start <= index < end:
                gt_path = (
                    gt_root /
                    image_path.parent.name /
                    f"{image_path.stem}_gt.json"
                )

                if gt_path.exists():
                    self.samples.append(
                        (image_path, gt_path)
                    )

        print(f"Base samples: {len(self.samples)}")
        print(f"Effective samples: {len(self.samples) * variants}")

    def __len__(self):
        return len(self.samples) * self.variants

    def __getitem__(self, index):
        base_index = index // self.variants
        variant = index % self.variants

        image_path, gt_path = self.samples[base_index]

        image = cv2.imread(
            str(image_path),
            cv2.IMREAD_UNCHANGED
        )

        if image is None:
            raise RuntimeError(
                f"Failed to read {image_path}"
            )

        image = image.astype(np.float32)

        image_min = image.min()
        image_max = image.max()

        image = (
            image - image_min
        ) / (
            image_max - image_min + 1e-8
        )

        with open(gt_path, "r") as f:
            target = json.load(f)

        contours = target.get("contours", [])

        if self.augment and variant > 0:
            levels = [
                "low",
                "medium",
                "high",
                "medium"
            ]

            level = levels[(variant - 1) % len(levels)]

            image, contours = augment_sample(
                image,
                contours,
                level=level,
                geometry=True
            )

        image = torch.from_numpy(
            image.copy()
        ).unsqueeze(0)

        target = dict(target)
        target["contours"] = contours

        return {
            "image": image,
            "target": target,
            "image_path": str(image_path),
            "variant": variant
        }


if __name__ == "__main__":
    dataset = LocalizationDataset()

    print("\nLength:", len(dataset))

    for i in range(5):
        sample = dataset[i]

        print(
            f"Sample {i}:",
            sample["target"]["sample"],
            "Variant:",
            sample["variant"],
            "Shape:",
            sample["image"].shape,
            "Min:",
            sample["image"].min().item(),
            "Max:",
            sample["image"].max().item(),
            "Contours:",
            len(sample["target"]["contours"])
        )