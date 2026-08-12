import sys
from pathlib import Path

import cv2
import numpy as np
import torch
from torch.utils.data import Dataset

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from config import DATASET_ROOT


class SiameseLocalizationDataset(Dataset):
    def __init__(
        self,
        root=DATASET_ROOT,
        start=0,
        end=5000,
        reference_size=128,
        search_size=256,
        training=True
    ):
        self.root = Path(root)
        self.reference_size = reference_size
        self.search_size = search_size
        self.training = training
        self.samples = []

        image_root = self.root / "images"
        images = sorted(image_root.rglob("*.tiff"))

        for image_path in images:
            try:
                index = int(image_path.stem)
            except ValueError:
                continue

            if start <= index < end:
                self.samples.append(image_path)

        print(f"Siamese samples: {len(self.samples)}")

    def __len__(self):
        return len(self.samples)

    def _load_image(self, path):
        image = cv2.imread(
            str(path),
            cv2.IMREAD_UNCHANGED
        )

        if image is None:
            raise RuntimeError(f"Failed to read: {path}")

        image = image.astype(np.float32)

        mn = image.min()
        mx = image.max()

        image = (image - mn) / (mx - mn + 1e-8)

        return image

    def __getitem__(self, index):
        image_path = self.samples[index]

        image = self._load_image(image_path)

        h, w = image.shape

        ss = self.search_size
        rs = self.reference_size

        if h < ss or w < ss:
            raise RuntimeError(
                f"Image too small: {image.shape}"
            )

        search_x = np.random.randint(
            0,
            w - ss + 1
        )

        search_y = np.random.randint(
            0,
            h - ss + 1
        )

        search = image[
            search_y:search_y + ss,
            search_x:search_x + ss
        ].copy()

        max_x = ss - rs
        max_y = ss - rs

        ref_x = np.random.randint(
            0,
            max_x + 1
        )

        ref_y = np.random.randint(
            0,
            max_y + 1
        )

        reference = search[
            ref_y:ref_y + rs,
            ref_x:ref_x + rs
        ].copy()

        target_x = (
            ref_x + rs / 2
        ) / ss

        target_y = (
            ref_y + rs / 2
        ) / ss

        reference = torch.from_numpy(
            reference.astype(np.float32)
        ).unsqueeze(0)

        search = torch.from_numpy(
            search.astype(np.float32)
        ).unsqueeze(0)

        target = torch.tensor(
            [target_x, target_y],
            dtype=torch.float32
        )

        return {
            "reference": reference,
            "search": search,
            "target": target,
            "image_path": str(image_path)
        }


if __name__ == "__main__":
    dataset = SiameseLocalizationDataset(
        start=0,
        end=5000,
        training=False
    )

    print()
    print("Length:", len(dataset))

    sample = dataset[0]

    print()
    print("Reference")
    print("Shape:", sample["reference"].shape)
    print("Dtype:", sample["reference"].dtype)
    print("Min:", sample["reference"].min().item())
    print("Max:", sample["reference"].max().item())

    print()
    print("Search")
    print("Shape:", sample["search"].shape)
    print("Dtype:", sample["search"].dtype)
    print("Min:", sample["search"].min().item())
    print("Max:", sample["search"].max().item())

    print()
    print("Target")
    print(sample["target"])

    print()
    print("Image")
    print(sample["image_path"])