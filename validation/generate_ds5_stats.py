#!/usr/bin/env python3
"""DG4: Validate and produce statistics for DS5 after generation is complete.

Usage: python validation/generate_ds5_stats.py
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "simulator"
sys.path.insert(0, str(ROOT / "src"))

import numpy as np
import io as _io
sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

DS5 = Path(__file__).resolve().parents[1] / "datasets" / "ds5_final_training"
REPORTS = Path(__file__).resolve().parents[1] / "validation" / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    t0 = time.perf_counter()
    idx_path = DS5 / "dataset_index.json"
    if not idx_path.exists():
        print("ERROR: dataset_index.json not found in DS5")
        return 1
    idx = json.loads(idx_path.read_text())
    samples = idx.get("samples", [])
    n_total = len(samples)
    print(f"DS5 Statistics: {n_total} samples found")

    # --- Sample status ---
    from collections import Counter
    statuses = Counter(s.get("status", "?") for s in samples)
    types = Counter(s.get("structure_type", "?") for s in samples)
    n_ok = statuses.get("OK", 0)
    n_fail = statuses.get("FAILED", 0)

    # --- File completeness ---
    n_images = sum(1 for s in samples if (DS5 / f"images/{s['sample_index']:06d}.tiff").exists())
    n_gt = sum(1 for s in samples if (DS5 / f"ground_truth/{s['sample_index']:06d}_gt.json").exists())
    n_meta = sum(1 for s in samples if (DS5 / f"metadata/{s['sample_index']:06d}_metadata.json").exists())

    # --- Checksum verification ---
    sums_path = DS5 / "SHA256SUMS"
    n_valid = 0
    n_check = 0
    if sums_path.exists():
        lines = [l for l in sums_path.read_text().strip().splitlines() if l and not l.startswith("#")]
        for line in lines:
            parts = line.split("  ", 1)
            if len(parts) == 2:
                h_exp, rel = parts
                p = DS5 / rel
                if p.exists():
                    n_check += 1
                    if sha256(p) == h_exp:
                        n_valid += 1

    # --- Height statistics ---
    heights = []
    for s in samples[:500]:  # sample first 500 for speed
        npy = DS5 / f"ground_truth/{s['sample_index']:06d}_height.npy"
        if npy.exists():
            h = np.load(npy)
            heights.append(float(h.mean()))

    # --- CD statistics ---
    cds = []
    for s in samples[:500]:
        gt_p = DS5 / f"ground_truth/{s['sample_index']:06d}_gt.json"
        if gt_p.exists():
            gt = json.loads(gt_p.read_text())
            for c in gt.get("cd_measurements", []):
                if "cd_nm" in c:
                    cds.append(c["cd_nm"])

    # --- Disk usage ---
    total_bytes = 0
    for root_dir, _, files in os.walk(DS5):
        for f in files:
            fp = os.path.join(root_dir, f)
            if fp.endswith((".tiff", ".json", ".npy", ".png")):
                total_bytes += os.path.getsize(fp)

    elapsed = time.perf_counter() - t0

    report = {
        "n_samples": n_total,
        "status": dict(statuses),
        "structure_distribution": dict(types),
        "completeness": {
            "images": n_images,
            "ground_truth": n_gt,
            "metadata": n_meta,
            "all_present": n_images == n_total and n_gt == n_total and n_meta == n_total,
        },
        "checksum": {
            "verified": n_valid,
            "total": n_check,
            "valid": n_valid == n_check,
        },
        "height_stats": {
            "n_samples": len(heights),
            "mean_nm": round(float(np.mean(heights)), 2) if heights else 0,
            "std_nm": round(float(np.std(heights)), 2) if heights else 0,
        },
        "cd_statistics": {
            "n_measurements": len(cds),
            "mean_nm": round(float(np.mean(cds)), 1) if cds else 0,
            "std_nm": round(float(np.std(cds)), 1) if cds else 0,
            "min_nm": round(float(np.min(cds)), 1) if cds else 0,
            "max_nm": round(float(np.max(cds)), 1) if cds else 0,
        },
        "storage": {
            "total_bytes": total_bytes,
            "total_gb": round(total_bytes / 1024**3, 2),
        },
    }

    RPT = REPORTS
    RPT.joinpath("ds5_statistics.json").write_text(json.dumps(report, indent=2))

    # --- Summary ---
    print(f"\nDS5 Dataset Statistics (elapsed validation: {elapsed:.1f}s)")
    print(f"  Samples: {n_total} total, {n_ok} OK, {n_fail} FAILED")
    print(f"  Files: images={n_images}/{n_total}, gt={n_gt}/{n_total}, meta={n_meta}/{n_total}")
    print(f"  Structures: {dict(types)}")
    print(f"  Checksums: {n_valid}/{n_check} valid")
    print(f"  Height: mean={report['height_stats']['mean_nm']:.1f}nm")
    print(f"  CD: mean={report['cd_statistics']['mean_nm']:.1f}nm, std={report['cd_statistics']['std_nm']:.1f}nm")
    print(f"  Storage: {report['storage']['total_gb']:.2f} GB")
    print(f"\n  ALL CHECKS {'PASSED' if (n_ok == n_total and n_valid == n_check and n_images == n_total) else 'FAILED'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
