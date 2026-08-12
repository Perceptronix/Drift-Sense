import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from config import DATASET_ROOT

gt = (
    Path(DATASET_ROOT)
    / "ground_truth"
    / "chunk_000"
    / "000000_gt.json"
)

with open(gt, "r") as f:
    data = json.load(f)

print("FILE:", gt)
print("\nTOP-LEVEL KEYS:")
for k, v in data.items():
    print(f"{k}: {type(v).__name__}")

print("\nFULL TARGET:")
print(json.dumps(data, indent=2)[:12000])