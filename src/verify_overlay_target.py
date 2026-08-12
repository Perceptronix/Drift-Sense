import json
from pathlib import Path
import cv2
import numpy as np

ROOT = Path(r"D:\Semicon\SEMICON-2026-Localization-DS5-v1")

metadata_root = ROOT / "metadata"
image_root = ROOT / "images"

samples = []

for path in sorted(metadata_root.rglob("*_metadata.json"))[:100]:
    try:
        with open(path, "r") as f:
            data = json.load(f)

        dx = data["variability"]["overlay_dx_nm"]
        dy = data["variability"]["overlay_dy_nm"]

        samples.append((path.stem.replace("_metadata", ""), dx, dy))

    except Exception:
        pass

print("Samples:", len(samples))
print()

for sample, dx, dy in samples[:20]:
    x = 128.0 + dx
    y = 128.0 + dy

    print(
        f"{sample}: "
        f"DX={dx:+7.3f} nm  "
        f"DY={dy:+7.3f} nm  "
        f"Target=({x:7.3f}, {y:7.3f})"
    )

dxs = np.array([x[1] for x in samples])
dys = np.array([x[2] for x in samples])

print("\nOVERLAY DISTRIBUTION")
print(f"DX min : {dxs.min():.3f}")
print(f"DX max : {dxs.max():.3f}")
print(f"DX mean: {dxs.mean():.3f}")
print(f"DX std : {dxs.std():.3f}")

print()

print(f"DY min : {dys.min():.3f}")
print(f"DY max : {dys.max():.3f}")
print(f"DY mean: {dys.mean():.3f}")
print(f"DY std : {dys.std():.3f}")