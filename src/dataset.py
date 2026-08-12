import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from config import DATASET_ROOT


class DatasetScanner:
    def __init__(self, root):
        self.root = Path(root)
        self.samples = []

    def scan(self):
        image_files = sorted(self.root.rglob("*_material.png"))

        for img_path in image_files:
            json_path = img_path.with_name(
                img_path.name.replace("_material.png", "_gt.json")
            )

            if json_path.exists():
                self.samples.append((img_path, json_path))

        return self.samples

    def inspect_sample(self, index=0):
        image_path, json_path = self.samples[index]

        print(f"\nImage : {image_path.name}")
        print(f"JSON  : {json_path.name}\n")

        with open(json_path, "r") as f:
            data = json.load(f)

        print("Keys in JSON:\n")
        for key in data.keys():
            print(key)

        return data


if __name__ == "__main__":
    scanner = DatasetScanner(DATASET_ROOT)

    scanner.scan()

    print(f"\nFound {len(scanner.samples)} samples\n")

    sample = scanner.inspect_sample(0)

    print("\nEdge Summary:\n")
    print(json.dumps(sample["edge_map_summary"], indent=4))