import json
from pathlib import Path

ROOT = Path(r"D:\Semicon\SEMICON-2026-Localization-DS5-v1")
files = list((ROOT / "metadata").rglob("*.json"))

terms = [
    "localization",
    "reference",
    "search",
    "coordinate",
    "position",
    "offset",
    "overlay",
    "target"
]

count = 0

for path in files:
    try:
        text = path.read_text(errors="ignore")
    except:
        continue

    low = text.lower()

    if any(t in low for t in terms):
        print("\n" + "=" * 80)
        print(path)

        try:
            data = json.loads(text)

            def walk(obj, prefix=""):
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        key = str(k).lower()
                        if any(t in key for t in terms):
                            print(f"{prefix}{k}: {v}")
                        walk(v, prefix + str(k) + ".")
                elif isinstance(obj, list):
                    for i, v in enumerate(obj):
                        walk(v, prefix + f"[{i}].")

            walk(data)

        except:
            for line in text.splitlines():
                if any(t in line.lower() for t in terms):
                    print(line[:500])

        count += 1

        if count >= 20:
            break

print("\nFiles inspected:", count)