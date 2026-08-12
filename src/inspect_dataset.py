from pathlib import Path
import json

DATASET_ROOT = Path(r"D:\Semicon\SEMICON-2026-Localization-DS5-v1")


def read_json(pattern):
    files = sorted(DATASET_ROOT.rglob(pattern))

    print(f"\nFound {len(files)} files matching {pattern}")

    if not files:
        return None

    path = files[0]

    print(f"Reading: {path}\n")

    with open(path, "r") as f:
        data = json.load(f)

    print(json.dumps(data, indent=4)[:10000])

    return data


metadata = read_json("*_metadata.json")
config = read_json("*_config.json")