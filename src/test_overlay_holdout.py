import sys
from pathlib import Path

import torch
from torch.utils.data import DataLoader

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from overlay_model import OverlayModel
from overlay_dataset import OverlayDataset


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    print("Device:", device)
    if torch.cuda.is_available():
        print("GPU:", torch.cuda.get_device_name(0))

    dataset = OverlayDataset(start=5000, end=11177)

    print("\nIndependent holdout samples:", len(dataset))

    loader = DataLoader(
        dataset,
        batch_size=32,
        shuffle=False,
        num_workers=0
    )

    model = OverlayModel().to(device)

    checkpoint = torch.load(
        ROOT / "outputs" / "best_overlay_model.pth",
        map_location=device
    )

    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    errors = []

    with torch.no_grad():
        for batch in loader:
            images = batch["image"].to(device)
            targets = batch["target"].float().to(device)

            predictions = model(images)

            diff = predictions - targets

            pixel_error = torch.sqrt(
                diff[:, 0] ** 2 +
                diff[:, 1] ** 2
            )

            errors.append(pixel_error.cpu())

    errors = torch.cat(errors)

    print("\n" + "=" * 50)
    print("INDEPENDENT OVERLAY HOLDOUT")
    print("=" * 50)

    print(f"Samples          : {len(errors)}")
    print(f"Mean error       : {errors.mean():.2f} px")
    print(f"Median error     : {errors.median():.2f} px")
    print(f"Minimum error    : {errors.min():.2f} px")
    print(f"Maximum error    : {errors.max():.2f} px")
    print(f"90th percentile  : {torch.quantile(errors, 0.90):.2f} px")
    print(f"95th percentile  : {torch.quantile(errors, 0.95):.2f} px")

    print("\n## LOCALIZATION ACCURACY")

    for threshold in [1, 2, 5, 10]:
        accuracy = (errors <= threshold).float().mean() * 100
        print(f"Within {threshold:2d} px : {accuracy:.2f}%")


if __name__ == "__main__":
    main()