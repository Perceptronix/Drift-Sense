import sys
from pathlib import Path

import torch
import numpy as np
from torch.utils.data import DataLoader, Subset

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from siamese_dataset import SiameseLocalizationDataset
from siamese_model import SiameseCNN


DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

CHECKPOINT = ROOT / "outputs" / "siamese_baseline_best.pth"

SEARCH_SIZE = 256
BATCH_SIZE = 16

dataset = SiameseLocalizationDataset(
    start=0,
    end=5000,
    training=False
)

val_dataset = Subset(
    dataset,
    range(4000, 5000)
)

loader = DataLoader(
    val_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=0,
    pin_memory=True
)

model = SiameseCNN().to(DEVICE)

checkpoint = torch.load(
    CHECKPOINT,
    map_location=DEVICE
)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model.eval()

errors = []

with torch.no_grad():

    for batch in loader:

        reference = batch["reference"].to(
            DEVICE,
            non_blocking=True
        )

        search = batch["search"].to(
            DEVICE,
            non_blocking=True
        )

        target = batch["target"].to(
            DEVICE,
            non_blocking=True
        )

        prediction = model(
            reference,
            search
        )

        error = torch.abs(
            prediction - target
        )

        error = error * SEARCH_SIZE

        errors.append(
            error.cpu()
        )

errors = torch.cat(errors, dim=0)

x_error = errors[:, 0]
y_error = errors[:, 1]

mean_x = x_error.mean().item()
mean_y = y_error.mean().item()

mean_error = errors.mean(dim=1)

mean_pixel_error = mean_error.mean().item()
median_pixel_error = mean_error.median().item()

print()
print("=" * 55)
print("SIAMESE CNN BASELINE EVALUATION")
print("=" * 55)

print(f"Validation samples : {len(val_dataset)}")
print(f"Mean X error       : {mean_x:.2f} px")
print(f"Mean Y error       : {mean_y:.2f} px")
print(f"Mean pixel error   : {mean_pixel_error:.2f} px")
print(f"Median pixel error : {median_pixel_error:.2f} px")

print()
print("LOCALIZATION ACCURACY")
print("-" * 55)

for threshold in [1, 5, 10, 20, 30, 50]:

    accuracy = (
        (mean_error <= threshold)
        .float()
        .mean()
        .item()
        * 100
    )

    print(
        f"Within {threshold:>2} px : "
        f"{accuracy:6.2f}%"
    )

print()
print("ERROR DISTRIBUTION")
print("-" * 55)

print(
    f"Minimum error : "
    f"{mean_error.min().item():.2f} px"
)

print(
    f"Maximum error : "
    f"{mean_error.max().item():.2f} px"
)

print(
    f"90th percentile : "
    f"{torch.quantile(mean_error, 0.90).item():.2f} px"
)

print(
    f"95th percentile : "
    f"{torch.quantile(mean_error, 0.95).item():.2f} px"
)

print("=" * 55)