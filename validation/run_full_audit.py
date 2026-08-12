#!/usr/bin/env python3
"""DG2: Comprehensive DS1 audit — quality, reproducibility, and performance.

Produces:
  validation/reports/ds1_quality.json
  validation/reports/reproducibility.json
  validation/reports/performance.json
  validation/ds1/contact_sheet.png
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1] / "simulator"
sys.path.insert(0, str(ROOT / "src"))

import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

DS1 = Path(__file__).resolve().parents[1] / "datasets" / "ds1"
RPT = Path(__file__).resolve().parents[1] / "validation" / "reports"
RPT.mkdir(parents=True, exist_ok=True)
SIM = ROOT


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ──────────────────────────────────────────────────────────────────
# 1. DATASET QUALITY
# ──────────────────────────────────────────────────────────────────
def quality_analysis():
    print("=" * 60)
    print("DATASET QUALITY ANALYSIS")
    print("=" * 60)

    idx_path = DS1 / "dataset_index.json"
    if not idx_path.exists():
        print("ERROR: DS1 dataset_index.json not found")
        return {"error": "missing index"}
    idx = json.loads(idx_path.read_text())
    samples = idx.get("samples", [])

    # --- Structure balance ---
    from collections import Counter
    types = Counter(s["structure_type"] for s in samples)
    status_counts = Counter(s.get("status", "unknown") for s in samples)
    n_ok = status_counts.get("OK", 0)
    n_fail = status_counts.get("FAILED", 0)

    # --- Metadata completeness ---
    meta_missing = 0
    gt_missing = 0
    img_missing = 0
    for s in samples:
        sid = s["sample_index"]
        if not (DS1 / f"images/{sid:06d}.tiff").exists():
            img_missing += 1
        if not (DS1 / f"ground_truth/{sid:06d}_gt.json").exists():
            gt_missing += 1
        if not (DS1 / f"metadata/{sid:06d}_metadata.json").exists():
            meta_missing += 1

    # --- Height field stats ---
    heights = []
    for s in samples:
        npy = DS1 / f"ground_truth/{s['sample_index']:06d}_height.npy"
        if npy.exists():
            h = np.load(npy)
            heights.append({"min": float(h.min()), "mean": float(h.mean()), "max": float(h.max())})

    # --- CD measurements from GT ---
    cd_values = []
    for s in samples:
        gt_path = DS1 / f"ground_truth/{s['sample_index']:06d}_gt.json"
        if gt_path.exists():
            gt = json.loads(gt_path.read_text())
            for cd in gt.get("cd_measurements", []):
                if "cd_nm" in cd:
                    cd_values.append(cd["cd_nm"])

    # --- SHA-256 verification ---
    sums_path = DS1 / "SHA256SUMS"
    if sums_path.exists():
        lines = [l for l in sums_path.read_text().strip().splitlines() if l and not l.startswith("#")]
        valid = 0
        invalid = 0
        for line in lines:
            parts = line.split("  ", 1)
            if len(parts) == 2:
                h_expected, rel = parts
                full_path = DS1 / rel
                if full_path.exists() and sha256(full_path) == h_expected:
                    valid += 1
                else:
                    invalid += 1
        checksum_valid = invalid == 0
    else:
        checksum_valid = False
        valid = 0
        invalid = 0

    report = {
        "total_samples": len(samples),
        "status": {"OK": n_ok, "FAILED": n_fail},
        "structure_distribution": dict(types),
        "metadata_completeness": {"total": len(samples), "images_present": len(samples) - img_missing, "gt_present": len(samples) - gt_missing, "meta_present": len(samples) - meta_missing, "img_missing": img_missing, "gt_missing": gt_missing, "meta_missing": meta_missing},
        "height_stats": {"n_samples": len(heights), "overall_min": min(h["min"] for h in heights) if heights else 0, "overall_max": max(h["max"] for h in heights) if heights else 0, "overall_mean": float(np.mean([h["mean"] for h in heights])) if heights else 0},
        "cd_statistics": {"n_measurements": len(cd_values), "mean_cd_nm": float(np.mean(cd_values)) if cd_values else 0, "std_cd_nm": float(np.std(cd_values)) if cd_values else 0, "min_cd_nm": float(np.min(cd_values)) if cd_values else 0, "max_cd_nm": float(np.max(cd_values)) if cd_values else 0},
        "checksum_verification": {"verified": checksum_valid, "valid_files": valid, "invalid_files": invalid},
    }
    RPT.joinpath("ds1_quality.json").write_text(json.dumps(report, indent=2))

    print(f"Samples: {len(samples)} total, {n_ok} OK, {n_fail} FAILED")
    print(f"Files: images={len(samples)-img_missing}, gt={len(samples)-gt_missing}, meta={len(samples)-meta_missing}")
    print(f"Structures: {dict(types)}")
    print(f"Height: min={report['height_stats']['overall_min']:.1f}, max={report['height_stats']['overall_max']:.1f}")
    print(f"CD: mean={report['cd_statistics']['mean_cd_nm']:.1f}, std={report['cd_statistics']['std_cd_nm']:.1f}")
    print(f"Checksum: {valid} valid, {invalid} invalid")
    return report


# ──────────────────────────────────────────────────────────────────
# 2. REPRODUCIBILITY AUDIT
# ──────────────────────────────────────────────────────────────────
def reproducibility_audit():
    print("\n" + "=" * 60)
    print("REPRODUCIBILITY AUDIT")
    print("=" * 60)

    from semicon.geometry.raster import save_library
    from semicon.geometry.structures import build_structure_library
    from semicon.orchestration.config import load_config
    from semicon.orchestration.pipeline import build_context
    from semicon.orchestration.job import run_job

    lib = build_structure_library(fov_nm=320.0, cd_nm=40.0, height_nm=70.0)
    import tempfile, os
    tmp = tempfile.mkdtemp()
    lib_path = os.path.join(tmp, "lib.gds")
    save_library(lib, lib_path)

    context = build_context(lib_path, app_version="0.1.0", git_hash="dg2_test")
    cfg = load_config(None, defaults_path=str(SIM / "configs" / "defaults.yml"),
                      overrides={
                          "structure.structure_type": "iso_line",
                          "structure.width_nm": 320.0, "structure.height_nm_fov": 320.0,
                          "structure.pixel_size_nm": 1.0,
                          "variability.ler_3sigma_nm": 1.5,
                      })

    # Test 1: Same seed produces identical image bytes
    print("Test 1: Determinism (same seed → same image)")
    out1 = os.path.join(tmp, "run1")
    out2 = os.path.join(tmp, "run2")
    r1 = run_job(context, cfg, Path(out1), n_samples=1, master_seed=42, write_outputs=True)
    r2 = run_job(context, cfg, Path(out2), n_samples=1, master_seed=42, write_outputs=True)
    img1 = Path(out1) / "images" / "000000.tiff"
    img2 = Path(out2) / "images" / "000000.tiff"
    det1 = img1.read_bytes() == img2.read_bytes()
    # metadata must also match
    m1 = json.loads((Path(out1) / "metadata" / "000000_metadata.json").read_text())
    m2 = json.loads((Path(out2) / "metadata" / "000000_metadata.json").read_text())
    meta_det = m1 == m2
    print(f"  Image bytes identical: {det1}")
    print(f"  Metadata identical: {meta_det}")
    det1, meta_det = bool(det1), bool(meta_det)

    # Test 2: Different seed → different image
    print("\nTest 2: Different seed → different image")
    out3 = os.path.join(tmp, "run3")
    r3 = run_job(context, cfg, Path(out3), n_samples=1, master_seed=999, write_outputs=True)
    img3 = Path(out3) / "images" / "000000.tiff"
    diff = img1.read_bytes() != img3.read_bytes()
    print(f"  Different seed → different image: {diff}")

    # Test 3: Dataset SHA-256 completeness
    print("\nTest 3: DS1 checksum completeness")
    ds_idx = json.loads((DS1 / "dataset_index.json").read_text())
    all_match = True
    n_checked = 0
    for s in ds_idx["samples"]:
        sid = s["sample_index"]
        img_p = DS1 / f"images/{sid:06d}.tiff"
        if img_p.exists():
            n_checked += 1
    print(f"  Checked {n_checked} image files exist in DS1")

    elapsed = 0  # placeholder
    report = {
        "determinism_bitwise": det1,
        "determinism_metadata": meta_det,
        "different_seed_different_output": diff,
        "ds1_files_exist": n_checked,
    }
    RPT.joinpath("reproducibility.json").write_text(json.dumps(report, indent=2))
    print(f"\nAll checks passed: {det1 and meta_det and diff}")
    return report


# ──────────────────────────────────────────────────────────────────
# 3. PERFORMANCE PROFILING
# ──────────────────────────────────────────────────────────────────
def performance_audit():
    print("\n" + "=" * 60)
    print("PERFORMANCE PROFILING")
    print("=" * 60)

    import tracemalloc
    from semicon.geometry.raster import save_library
    from semicon.geometry.structures import build_structure_library
    from semicon.orchestration.config import load_config
    from semicon.orchestration.pipeline import build_context, run_pipeline

    lib = build_structure_library(fov_nm=1024.0, cd_nm=40.0, height_nm=70.0)
    import tempfile, os
    tmp = tempfile.mkdtemp()
    lib_path = os.path.join(tmp, "lib1024.gds")
    save_library(lib, lib_path)
    context = build_context(lib_path, app_version="0.1.0", git_hash="perf")

    cfg = load_config(None, defaults_path=str(SIM / "configs" / "defaults.yml"),
                      overrides={
                          "structure.structure_type": "iso_line",
                          "structure.width_nm": 1024.0, "structure.height_nm_fov": 1024.0,
                          "structure.pixel_size_nm": 1.0,
                          "physics.probe_diameter_nm": 2.0,
                          "variability.ler_3sigma_nm": 1.5,
                      })

    # Warm-up run
    run_pipeline(context, cfg, Path(tmp) / "warm", 0, "warm", 12345, write_outputs=False)

    # Memory profile
    tracemalloc.start()
    t0 = time.perf_counter()
    result = run_pipeline(context, cfg, Path(tmp) / "perf", 0, "perf", 12345, write_outputs=True)
    elapsed = time.perf_counter() - t0
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    per_img = elapsed

    # Parallel scaling (1, 2, 4 workers via sequential simulation)
    from semicon.orchestration.job import run_job
    times = {}
    for nw in [1, 2, 4]:
        t0 = time.perf_counter()
        out_dir = Path(tmp) / f"par{nw}"
        for i in range(nw):
            run_pipeline(context, cfg, out_dir, i, "par", 56789 + i, write_outputs=False)
        times[nw] = time.perf_counter() - t0
    speedup = {nw: times[1] / max(t, 1e-9) for nw, t in times.items()}

    print(f"\n1024×1024 single image: {per_img:.3f}s")
    print(f"Peak memory: {peak / 1024**2:.1f} MB")
    print(f"Parallel scaling (sequential simulated):")
    for nw, t in times.items():
        print(f"  {nw} workers: {t:.3f}s (speedup: {speedup[nw]:.1f}x)")

    report = {
        "image_size_pixels": [1024, 1024],
        "single_image_time_s": round(per_img, 3),
        "peak_memory_mb": round(peak / 1024**2, 1),
        "parallel_times": {str(k): round(v, 3) for k, v in times.items()},
        "parallel_speedup": {str(k): round(v, 2) for k, v in speedup.items()},
        "performance_budget": {"target_per_image_s": 3.0, "target_speedup": 3.5, "achieved": per_img <= 3.0 and speedup.get(4, 0) >= 3.5},
    }
    RPT.joinpath("performance.json").write_text(json.dumps(report, indent=2))

    budget = report["performance_budget"]
    status = "PASS" if budget["achieved"] else "FAIL"
    print(f"\nPerformance budget: {status} (per_image={per_img:.2f}s ≤ 3.0s; speedup_4w={speedup.get(4,0):.1f}x ≥ 3.5x)")
    return report


# ──────────────────────────────────────────────────────────────────
# 4. CONTACT SHEET
# ──────────────────────────────────────────────────────────────────
def make_contact_sheet():
    print("\n" + "=" * 60)
    print("CONTACT SHEET")
    print("=" * 60)
    from PIL import Image, ImageDraw

    idx = json.loads((DS1 / "dataset_index.json").read_text())
    labels = {s["sample_index"]: s["structure_type"] for s in idx["samples"]}
    n = min(len(labels), 50)
    cols, rows = 10, 5
    cell = 100
    sheet = Image.new("RGB", (cols * cell, rows * cell), (0, 0, 0))
    d = ImageDraw.Draw(sheet)
    for i in range(n):
        sid = list(labels.keys())[i]
        img = Image.open(DS1 / f"images/{sid:06d}.tiff")
        a = np.asarray(img).astype(np.float64)
        lo, hi = np.percentile(a, 1), np.percentile(a, 99)
        a = np.clip((a - lo) / (hi - lo + 1e-9), 0, 1) * 255
        thumb = Image.fromarray(a.astype(np.uint8)).resize((cell - 4, cell - 14), Image.LANCZOS)
        r, c = divmod(i, cols)
        sheet.paste(thumb, (c * cell + 2, r * cell + 2))
        d.text((c * cell + 2, r * cell + cell - 12), labels[sid][:10], fill=(255, 255, 0))
    out = RPT / "contact_sheet.png"
    sheet.save(out)
    print(f"  Saved {n}-sample contact sheet to {out}")


# ──────────────────────────────────────────────────────────────────
# 5. SUMMARY REPORT
# ──────────────────────────────────────────────────────────────────
def summary_report(quality, repro, perf):
    print("\n" + "=" * 60)
    print("DG2 VALIDATION SUMMARY")
    print("=" * 60)

    checks = []
    all_pass = True

    # DS1 completeness
    q = quality
    ds1_ok = q["status"]["OK"] == 50
    checks.append(("DS1: 50 images generated", ds1_ok))
    checks.append(("DS1: metadata complete", q["metadata_completeness"]["meta_present"] == 50))
    checks.append(("DS1: ground truth complete", q["metadata_completeness"]["gt_present"] == 50))
    checks.append(("DS1: structure balance", all(v == 5 for v in q["structure_distribution"].values())))
    checks.append(("DS1: checksums verified", q["checksum_verification"]["verified"]))

    # Reproducibility
    checks.append(("Determinism: bit-identical images", repro["determinism_bitwise"]))
    checks.append(("Determinism: identical metadata", repro["determinism_metadata"]))
    checks.append(("Different seed → different output", repro["different_seed_different_output"]))

    # Performance
    checks.append(("Performance: per_image ≤ 3.0s", perf["single_image_time_s"] <= 3.0))
    checks.append(("Performance: 4-worker speedup ≥ 3.5x", perf["parallel_speedup"].get("4", 0) >= 3.5))

    for label, ok in checks:
        status = "PASS" if ok else "FAIL"
        if not ok:
            all_pass = False
        print(f"  [{status}] {label}")

    print(f"\n{'='*60}")
    verdict = "PASS — Simulator certified for production-scale dataset generation"
    if not all_pass:
        verdict = "FAIL — See failures above"
    print(f"FINAL VERDICT: {verdict}")

    summary = {"checks": [{"label": l, "passed": bool(o)} for l, o in checks], "all_passed": bool(all_pass)}
    RPT.joinpath("dg2_summary.json").write_text(json.dumps(summary, indent=2))


# ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("DG2: Full Validation Audit")
    print("=" * 60)
    q = quality_analysis()
    r = reproducibility_audit()
    p = performance_audit()
    make_contact_sheet()
    summary_report(q, r, p)
