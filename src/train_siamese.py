import sys
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Subset

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from siamese_dataset import SiameseLocalizationDataset
from siamese_model import SiameseCNN


DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

BATCH_SIZE = 16
EPOCHS = 15
LR = 1e-3

torch.manual_seed(42)

dataset = SiameseLocalizationDataset(
    start=0,
    end=5000,
    training=True
)

train_dataset = Subset(
    dataset,
    range(0, 4000)
)

val_dataset = Subset(
    dataset,
    range(4000, 5000)
)

train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True,
    num_workers=0,
    pin_memory=True
)

val_loader = DataLoader(
    val_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=0,
    pin_memory=True
)

model = SiameseCNN().to(DEVICE)

criterion = nn.MSELoss()

optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=LR,
    weight_decay=1e-4
)

best_val_loss = float("inf")

print()
print("Device:", DEVICE)

if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))

print("Train samples:", len(train_dataset))
print("Validation samples:", len(val_dataset))
print()

for epoch in range(EPOCHS):

    model.train()

    train_loss = 0.0

    for batch in train_loader:

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

        optimizer.zero_grad()

        prediction = model(
            reference,
            search
        )

        loss = criterion(
            prediction,
            target
        )

        loss.backward()

        optimizer.step()

        train_loss += loss.item()

    train_loss /= len(train_loader)

    model.eval()

    val_loss = 0.0
    pixel_errors = []

    with torch.no_grad():

        for batch in val_loader:

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

            loss = criterion(
                prediction,
                target
            )

            val_loss += loss.item()

            error = torch.abs(
                prediction - target
            )

            error_pixels = error * 256.0

            pixel_errors.append(
                error_pixels.detach().cpu()
            )

    val_loss /= len(val_loader)

    pixel_errors = torch.cat(
        pixel_errors,
        dim=0
    )

    mean_x = pixel_errors[:, 0].mean().item()
    mean_y = pixel_errors[:, 1].mean().item()

    mean_error = pixel_errors.mean().item()

    print(
        f"Epoch {epoch + 1:02d}/{EPOCHS} | "
        f"Train Loss: {train_loss:.6f} | "
        f"Val Loss: {val_loss:.6f} | "
        f"Mean Pixel Error: {mean_error:.2f}px | "
        f"X: {mean_x:.2f}px | "
        f"Y: {mean_y:.2f}px"
    )

    if val_loss < best_val_loss:

        best_val_loss = val_loss

        torch.save(
            {
                "epoch": epoch + 1,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "val_loss": val_loss,
                "mean_pixel_error": mean_error
            },
            ROOT / "outputs" / "siamese_baseline_best.pth"
        )

        print("  Saved best model")


print()
print("Training complete.")
print("Best validation loss:", best_val_loss)