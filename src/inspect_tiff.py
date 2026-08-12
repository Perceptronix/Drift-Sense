from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(r"D:\Semicon\SEMICON-2026-Localization-DS5-v1")

files = sorted(ROOT.rglob("*.tiff"))

print("Total TIFF files:", len(files))

indices = [0, 1, 10, 100, 1000, 5000, 10000]

for i in indices:
    if i >= len(files):
        continue

    path = files[i]

    print("\n" + "=" * 60)
    print("Sample:", i)
    print("File:", path)

    try:
        img = Image.open(path)

        print("Format:", img.format)
        print("Mode:", img.mode)
        print("Size:", img.size)

        arr = np.array(img)

        print("Shape:", arr.shape)
        print("Dtype:", arr.dtype)
        print("Min:", arr.min())
        print("Max:", arr.max())
        print("Mean:", arr.mean())
        print("Std:", arr.std())

        if arr.size < 20_000_000:
            print("Unique values:", len(np.unique(arr)))
        else:
            print("Unique values: skipped")

    except Exception as e:
        print("ERROR:", e)