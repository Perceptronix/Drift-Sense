import sys
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, random_split

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from overlay_model import OverlayModel
from overlay_dataset import OverlayDataset


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    print("Device:", device)
    if torch.cuda.is_available():
        print("GPU:", torch.cuda.get_device_name(0))

    dataset = OverlayDataset()

    n = len(dataset)
    train_n = int(n * 0.8)
    val_n = n - train_n

    generator = torch.Generator().manual_seed(5005)

    train_set, val_set = random_split(
        dataset,
        [train_n, val_n],
        generator=generator
    )

    print("Train samples:", len(train_set))
    print("Validation samples:", len(val_set))

    train_loader = DataLoader(
        train_set,
        batch_size=16,
        shuffle=True,
        num_workers=0,
        pin_memory=torch.cuda.is_available()
    )

    val_loader = DataLoader(
        val_set,
        batch_size=16,
        shuffle=False,
        num_workers=0,
        pin_memory=torch.cuda.is_available()
    )

    model = OverlayModel().to(device)

    criterion = nn.SmoothL1Loss()
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=1e-4,
        weight_decay=1e-4
    )

    best_loss = float("inf")
    epochs = 20

    output_dir = ROOT / "outputs"
    output_dir.mkdir(exist_ok=True)

    for epoch in range(epochs):
        model.train()

        train_loss = 0.0

        for batch in train_loader:
            images = batch["image"].to(device, non_blocking=True)
            targets = batch["target"].float().to(device, non_blocking=True)

            optimizer.zero_grad(set_to_none=True)

            predictions = model(images)

            loss = criterion(predictions, targets)

            loss.backward()
            optimizer.step()

            train_loss += loss.item() * images.size(0)

        train_loss /= len(train_set)

        model.eval()

        val_loss = 0.0
        errors = []

        with torch.no_grad():
            for batch in val_loader:
                images = batch["image"].to(device, non_blocking=True)
                targets = batch["target"].float().to(device, non_blocking=True)

                predictions = model(images)

                loss = criterion(predictions, targets)

                val_loss += loss.item() * images.size(0)

                diff = predictions - targets

                pixel_error = torch.sqrt(
                    diff[:, 0] ** 2 +
                    diff[:, 1] ** 2
                )

                errors.append(pixel_error.cpu())

        val_loss /= len(val_set)

        errors = torch.cat(errors)

        mean_error = errors.mean().item()
        median_error = errors.median().item()

        within_1 = (errors <= 1).float().mean().item() * 100
        within_2 = (errors <= 2).float().mean().item() * 100
        within_5 = (errors <= 5).float().mean().item() * 100
        within_10 = (errors <= 10).float().mean().item() * 100

        print(
            f"Epoch {epoch + 1:02d}/{epochs} | "
            f"Train Loss: {train_loss:.6f} | "
            f"Val Loss: {val_loss:.6f} | "
            f"Mean Error: {mean_error:.2f}px | "
            f"Median: {median_error:.2f}px"
        )

        print(
            f"  ≤1px: {within_1:.2f}% | "
            f"≤2px: {within_2:.2f}% | "
            f"≤5px: {within_5:.2f}% | "
            f"≤10px: {within_10:.2f}%"
        )

        if val_loss < best_loss:
            best_loss = val_loss

            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "val_loss": val_loss,
                    "epoch": epoch + 1
                },
                output_dir / "best_overlay_model.pth"
            )

            print("  Saved best model")

    print("\nTraining complete.")
    print("Best validation loss:", best_loss)


if __name__ == "__main__":
    main()