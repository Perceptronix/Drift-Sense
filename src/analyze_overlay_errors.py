import sys
from pathlib import Path

import torch
from torch.utils.data import DataLoader

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from overlay_dataset import OverlayDataset
from overlay_model import OverlayModel

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

dataset = OverlayDataset(start=5000, end=11177)

loader = DataLoader(
    dataset,
    batch_size=32,
    shuffle=False,
    num_workers=0
)

model = OverlayModel().to(device)

ckpt = torch.load(
    ROOT / "outputs" / "best_overlay_model.pth",
    map_location=device,
    weights_only=False
)

model.load_state_dict(ckpt["model_state_dict"])
model.eval()

results = []

with torch.no_grad():
    for batch in loader:
        images = batch["image"].to(device)
        targets = batch["target"].float().to(device)

        predictions = model(images)

        errors = torch.sqrt(
            (predictions[:, 0] - targets[:, 0]) ** 2 +
            (predictions[:, 1] - targets[:, 1]) ** 2
        )

        for i in range(len(errors)):
            results.append({
                "path": batch["image_path"][i],
                "actual_dx": targets[i, 0].item(),
                "actual_dy": targets[i, 1].item(),
                "pred_dx": predictions[i, 0].item(),
                "pred_dy": predictions[i, 1].item(),
                "error": errors[i].item()
            })

results.sort(key=lambda x: x["error"], reverse=True)

print("\n" + "=" * 80)
print("WORST OVERLAY PREDICTIONS")
print("=" * 80)

for i, r in enumerate(results[:20]):
    print(
        f"\n{i + 1:02d} | "
        f"{Path(r['path']).stem} | "
        f"Error={r['error']:.2f}px"
    )

    print(
        f"   Actual : "
        f"DX={r['actual_dx']:+.3f}, "
        f"DY={r['actual_dy']:+.3f}"
    )

    print(
        f"   Pred   : "
        f"DX={r['pred_dx']:+.3f}, "
        f"DY={r['pred_dy']:+.3f}"
    )

print("\n" + "=" * 80)
print(f"Total samples analyzed: {len(results)}")
print("=" * 80)