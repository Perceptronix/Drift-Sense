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


class OverlayDataset(Dataset):
    def __init__(self, root=DATASET_ROOT, start=0, end=5000, image_size=256):
        self.root = Path(root)
        self.image_size = image_size
        self.samples = []

        image_root = self.root / "images"
        gt_root = self.root / "ground_truth"
        metadata_root = self.root / "metadata"

        images = sorted(image_root.rglob("*.tiff"))

        for image_path in images:
            try:
                index = int(image_path.stem)
            except ValueError:
                continue

            if not (start <= index < end):
                continue

            gt_path = gt_root / image_path.parent.name / f"{image_path.stem}_gt.json"
            metadata_path = metadata_root / image_path.parent.name / f"{image_path.stem}_metadata.json"

            if gt_path.exists() and metadata_path.exists():
                self.samples.append(
                    (image_path, gt_path, metadata_path)
                )

        print(f"Base samples found : {len(images)}")
        print(f"Valid samples      : {len(self.samples)}")
        print(f"Skipped samples    : {len(images) - len(self.samples)}")
        print(f"Dataset            : {len(self.samples)}")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        image_path, gt_path, metadata_path = self.samples[index]

        image = cv2.imread(str(image_path), cv2.IMREAD_UNCHANGED)

        if image is None:
            raise RuntimeError(f"Failed to read: {image_path}")

        image = image.astype(np.float32)

        image = cv2.resize(
            image,
            (self.image_size, self.image_size),
            interpolation=cv2.INTER_AREA
        )

        image_min = image.min()
        image_max = image.max()

        image = (image - image_min) / (
            image_max - image_min + 1e-8
        )

        image = torch.from_numpy(image).unsqueeze(0).float()

        with open(metadata_path, "r") as f:
            metadata = json.load(f)

        variability = metadata["variability"]

        dx = float(variability["overlay_dx_nm"])
        dy = float(variability["overlay_dy_nm"])

        target = torch.tensor(
            [dx, dy],
            dtype=torch.float32
        )

        return {
            "image": image,
            "target": target,
            "image_path": str(image_path)
        }


if __name__ == "__main__":
    dataset = OverlayDataset()

    print("\nLength:", len(dataset))

    sample = dataset[0]

    print("\nImage")
    print("Shape:", sample["image"].shape)
    print("Dtype:", sample["image"].dtype)
    print("Min:", sample["image"].min().item())
    print("Max:", sample["image"].max().item())

    print("\nTarget")
    print(sample["target"])

    print("\nImage")
    print(sample["image_path"])