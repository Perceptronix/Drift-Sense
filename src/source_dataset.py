import json
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torch.utils.data import Dataset


class SEMSourceDataset(Dataset):
    def __init__(self, dataset_root, transform=None, limit=None):
        self.root = Path(dataset_root)
        self.transform = transform
        self.samples = []

        image_files = sorted(self.root.rglob("*_material.png"))

        for image_path in image_files:
            gt_path = image_path.with_name(
                image_path.name.replace("_material.png", "_gt.json")
            )

            metadata_path = self.root / "metadata"
            metadata_files = list(
                metadata_path.rglob(
                    image_path.name.replace("_material.png", "_metadata.json")
                )
            )

            config_files = list(
                metadata_path.rglob(
                    image_path.name.replace("_material.png", "_config.json")
                )
            )

            if gt_path.exists() and metadata_files and config_files:
                self.samples.append({
                    "image": image_path,
                    "gt": gt_path,
                    "metadata": metadata_files[0],
                    "config": config_files[0]
                })

            if limit and len(self.samples) >= limit:
                break

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        sample = self.samples[index]

        image = Image.open(sample["image"]).convert("L")

        with open(sample["gt"], "r") as f:
            gt = json.load(f)

        with open(sample["metadata"], "r") as f:
            metadata = json.load(f)

        with open(sample["config"], "r") as f:
            config = json.load(f)

        if self.transform:
            image = self.transform(image)

        if not torch.is_tensor(image):
            image = torch.from_numpy(
                np.array(image, dtype=np.float32)
            ).unsqueeze(0) / 255.0

        return {
            "image": image,
            "gt": gt,
            "metadata": metadata,
            "config": config,
            "image_path": str(sample["image"])
        }


if __name__ == "__main__":
    dataset_root = r"D:\Semicon\SEMICON-2026-Localization-DS5-v1"

    dataset = SEMSourceDataset(dataset_root)

    print("Dataset size:", len(dataset))

    sample = dataset[0]

    print("\nImage")
    print("Shape:", sample["image"].shape)
    print("Dtype:", sample["image"].dtype)
    print("Min:", sample["image"].min().item())
    print("Max:", sample["image"].max().item())

    print("\nGround truth")
    print("Sample:", sample["gt"]["sample"])
    print("Structure:", sample["gt"]["structure_type"])
    print("Contours:", len(sample["gt"]["contours"]))

    print("\nMetadata")
    print("CD:", sample["metadata"]["structure"]["cd_nm"])
    print("Height:", sample["metadata"]["structure"]["height_nm"])
    print("Pitch:", sample["metadata"]["structure"]["pitch_nm"])

    print("\nConfig")
    print("Pixel size:", sample["config"]["structure"]["pixel_size_nm"])