import torch
import numpy as np
from torch.utils.data import DataLoader, random_split
from overlay_dataset import OverlayDataset
from overlay_model import OverlayModel

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
VAL_SIZE = 1000
BATCH_SIZE = 32

dataset = OverlayDataset()

train_size = len(dataset) - VAL_SIZE

_, val_ds = random_split(
    dataset,
    [train_size, VAL_SIZE],
    generator=torch.Generator().manual_seed(42)
)

loader = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False)

model = OverlayModel().to(DEVICE)

checkpoint = torch.load(
    "outputs/best_overlay_model.pth",
    map_location=DEVICE
)

if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
    model.load_state_dict(checkpoint["model_state_dict"])
else:
    model.load_state_dict(checkpoint)

model.eval()

errors = []

with torch.no_grad():
    for batch in loader:
        images = batch["image"].to(DEVICE)
        targets = batch["target"].to(DEVICE)

        predictions = model(images)

        error = torch.sqrt(
            torch.sum((predictions - targets) ** 2, dim=1)
        )

        errors.extend(error.cpu().numpy())

errors = np.array(errors)

print()
print("Validation samples :", len(errors))
print("Mean pixel error   :", f"{errors.mean():.2f} px")
print("Median pixel error :", f"{np.median(errors):.2f} px")
print("Minimum error      :", f"{errors.min():.2f} px")
print("Maximum error      :", f"{errors.max():.2f} px")
print("90th percentile    :", f"{np.percentile(errors, 90):.2f} px")
print("95th percentile    :", f"{np.percentile(errors, 95):.2f} px")

print()
print("## OVERLAY LOCALIZATION ACCURACY")
print()

for t in [1, 2, 5, 10]:
    print(
        f"Within {t:2d} px : "
        f"{(errors <= t).mean() * 100:.2f}%"
    )