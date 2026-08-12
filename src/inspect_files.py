from pathlib import Path
from collections import Counter

ROOT = Path(r"D:\Semicon\SEMICON-2026-Localization-DS5-v1")

files = [p for p in ROOT.rglob("*") if p.is_file()]

print("Total files:", len(files))

print("\nFile extensions:")
extensions = Counter(p.suffix.lower() for p in files)

for ext, count in extensions.most_common():
    print(f"{ext or '[no extension]':15} {count}")

print("\nPNG filename patterns:")

pngs = [p for p in files if p.suffix.lower() == ".png"]

patterns = Counter()

for p in pngs:
    name = p.name

    if "_" in name:
        pattern = name[name.find("_"):]
        patterns[pattern] += 1
    else:
        patterns["[no suffix]"] += 1

for pattern, count in patterns.most_common():
    print(f"{pattern:30} {count}")

print("\nFirst 30 PNG files:")

for p in pngs[:30]:
    print(p)