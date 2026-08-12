import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from config import DATASET_ROOT

gt_root = Path(DATASET_ROOT) / "ground_truth"

files = sorted(gt_root.rglob("*_gt.json"))

print(f"GT files: {len(files)}")

for i, path in enumerate(files[:20]):
    with open(path, "r") as f:
        data = json.load(f)

    contours = data.get("contours")

    print("\n" + "=" * 60)
    print(path.name)
    print("contours type:", type(contours).__name__)

    if contours is None:
        print("NO CONTOURS")
        continue

    print("number of contours:", len(contours))

    valid = 0
    points = 0

    for contour in contours:
        if isinstance(contour, list):
            for p in contour:
                if (
                    isinstance(p, list)
                    and len(p) >= 2
                    and isinstance(p[0], (int, float))
                    and isinstance(p[1], (int, float))
                ):
                    valid += 1
                    points += 1

    print("valid points:", valid)

    if contours:
        print("first contour type:", type(contours[0]).__name__)
        print("first contour length:", len(contours[0]))
        print("first 3 points:", contours[0][:3])