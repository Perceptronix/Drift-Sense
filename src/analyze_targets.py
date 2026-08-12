import json
import numpy as np
from pathlib import Path

ROOT = Path(r"D:\Semicon\SEMICON-2026-Localization-DS5-v1")

json_files = sorted(ROOT.rglob("*_gt.json"))

print("Total GT files:", len(json_files))

xs = []
ys = []
contour_counts = []

for path in json_files:
    try:
        with open(path, "r") as f:
            data = json.load(f)

        contours = data.get("contours", [])

        count = 0

        for contour in contours:
            for point in contour:
                if len(point) >= 2:
                    x, y = point[:2]

                    if np.isfinite(x) and np.isfinite(y):
                        xs.append(x)
                        ys.append(y)
                        count += 1

        contour_counts.append(count)

    except Exception as e:
        print("Error:", path)
        print(e)

xs = np.array(xs)
ys = np.array(ys)

print("\nCoordinate statistics")
print("--------------------")

print("Points:", len(xs))

print("\nX")
print("Min:", xs.min())
print("Max:", xs.max())
print("Mean:", xs.mean())
print("Std:", xs.std())

print("\nY")
print("Min:", ys.min())
print("Max:", ys.max())
print("Mean:", ys.mean())
print("Std:", ys.std())

print("\nContour points per sample")
print("Min:", min(contour_counts))
print("Max:", max(contour_counts))
print("Mean:", np.mean(contour_counts))

print("\nSamples with contours:", len(contour_counts))