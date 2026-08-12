import sys
import json
from pathlib import Path

import cv2
import numpy as np
import torch
from torch.utils.data import Dataset

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from config import DATASET_ROOT
from augmentations import augment_sample


class DinoV2HeatmapDataset(Dataset):
    def __init__(self, root=DATASET_ROOT, start=0, end=5000, augment=True):
        self.root = Path(root)
        self.augment = augment
        self.samples = []

        image_root = self.root / "images"
        metadata_root = self.root / "metadata"

        images = sorted(image_root.rglob("*.tiff"))

        skipped = 0

        for image_path in images:
            try:
                index = int(image_path.stem)
            except ValueError:
                continue

            if not (start <= index < end):
                continue

            chunk = image_path.parent.name
            metadata_path = metadata_root / chunk / f"{image_path.stem}_metadata.json"

            if not metadata_path.exists():
                skipped += 1
                continue

            try:
                with open(metadata_path, "r") as f:
                    metadata = json.load(f)

                variability = metadata.get("variability", {})

                dx = variability.get("overlay_dx_nm")
                dy = variability.get("overlay_dy_nm")

                if dx is None or dy is None:
                    skipped += 1
                    continue

                self.samples.append(
                    (image_path, metadata_path, float(dx), float(dy))
                )

            except Exception:
                skipped += 1

        print(f"Base samples found : {end - start}")
        print(f"Valid samples      : {len(self.samples)}")
        print(f"Skipped samples    : {skipped}")
        print(f"Dataset            : {len(self.samples) * 5 if augment else len(self.samples)}")

    def __len__(self):
        return len(self.samples) * 5 if self.augment else len(self.samples)

    def _make_heatmap(self, x, y, size=64, sigma=1.5):
        scale = size / 256.0

        cx = x * scale
        cy = y * scale

        yy, xx = np.mgrid[0:size, 0:size]

        heatmap = np.exp(
            -((xx - cx) ** 2 + (yy - cy) ** 2)
            / (2 * sigma ** 2)
        )

        heatmap /= heatmap.max() + 1e-8

        return torch.from_numpy(
            heatmap.astype(np.float32)
        ).unsqueeze(0)

    def __getitem__(self, index):
        base_index = index // 5
        aug_index = index % 5

        image_path, metadata_path, dx, dy = self.samples[base_index]

        image = cv2.imread(
            str(image_path),
            cv2.IMREAD_UNCHANGED
        )

        if image is None:
            raise RuntimeError(f"Failed to read {image_path}")

        image = image.astype(np.float32)

        image -= image.min()
        image /= image.max() + 1e-8

        image = torch.from_numpy(image).unsqueeze(0)

        # Convert 1024 image to 256 model input
        image = torch.nn.functional.interpolate(
            image.unsqueeze(0),
            size=(256, 256),
            mode="bilinear",
            align_corners=False
        ).squeeze(0)

        # Center of 256x256 image
        center_x = 128.0
        center_y = 128.0

        # Dataset pixel size = 1 nm/px
        target_x = center_x + dx
        target_y = center_y + dy

        # Apply only image-side augmentation here.
        # Metadata overlay target remains the ground-truth displacement.
        if self.augment and aug_index > 0:
            image = augment_sample(image, None)

        target_x = float(np.clip(target_x, 0, 255))
        target_y = float(np.clip(target_y, 0, 255))

        heatmap = self._make_heatmap(
            target_x,
            target_y
        )

        displacement = torch.tensor(
            [dx, dy],
            dtype=torch.float32
        )

        return {
            "image": image,
            "heatmap": heatmap,
            "point": torch.tensor(
                [target_x, target_y],
                dtype=torch.float32
            ),
            "displacement": displacement,
            "sample": image_path.stem,
            "image_path": str(image_path)
        }


if __name__ == "__main__":
    dataset = DinoV2HeatmapDataset()

    print("\nDataset test")

    sample = dataset[0]

    print("Image:")
    print(" Shape:", sample["image"].shape)
    print(" Min:", sample["image"].min().item())
    print(" Max:", sample["image"].max().item())

    print("\nHeatmap:")
    print(" Shape:", sample["heatmap"].shape)
    print(" Min:", sample["heatmap"].min().item())
    print(" Max:", sample["heatmap"].max().item())

    print("\nPoint:")
    print(sample["point"])

    print("\nDisplacement:")
    print(sample["displacement"])

    print("\nSample:")
    print(sample["sample"])