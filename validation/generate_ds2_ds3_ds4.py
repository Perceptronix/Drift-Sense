#!/usr/bin/env python3
"""DG3: Generate DS2, DS3, DS4 datasets with validation.

DS2: Unit-Test (100 images, seed=2002, fixed golden references)
DS3: Validation (1000 images, seed=3003, parameter sweep)
DS4: Scientific Benchmark (200 images, seed=4004, calibration set)
"""
from __future__ import annotations

import hashlib
import io
import json
import sys
import time
from pathlib import Path

ROOT_SIM = Path(__file__).resolve().parents[1] / "simulator"
sys.path.insert(0, str(ROOT_SIM / "src"))

import numpy as np
import io as _io
sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from semicon.geometry.raster import save_library
from semicon.geometry.structures import build_structure_library
from semicon.orchestration.config import load_config
from semicon.orchestration.job import run_job
from semicon.orchestration.pipeline import build_context, APP_VERSION

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASETS = PROJECT_ROOT / "datasets"
LIB_PATH = DATASETS / "_lib_validation.gds"


def ensure_library():
    if not LIB_PATH.exists():
        lib = build_structure_library(fov_nm=320.0, cd_nm=40.0, height_nm=70.0)
        save_library(lib, LIB_PATH)
    return str(LIB_PATH)


def make_context():
    return build_context(ensure_library(), app_version=APP_VERSION, git_hash="dg3")


def base_cfg():
    return load_config(
        None,
        defaults_path=str(ROOT_SIM / "configs" / "defaults.yml"),
        overrides={
            "structure.width_nm": 320.0,
            "structure.height_nm_fov": 320.0,
            "structure.pixel_size_nm": 1.0,
            "variability.enabled": True,
            "variability.ler_3sigma_nm": 1.5,
            "variability.ler_xi_nm": 20.0,
            "physics.noise_enabled": True,
            "physics.counts_per_electron": 200.0,
        },
    )


def dist_configs():
    """Default uniform distribution over all 10 structure types."""
    return {s: 1 for s in [
        "iso_line", "dense_ls", "contact", "via", "trench",
        "fin", "gate", "sti", "bimaterial", "pitch_std",
    ]}


def generate_ds(name: str, n_samples: int, master_seed: int, dist_override=None) -> dict:
    ctx = make_context()
    cfg = base_cfg()
    out_dir = DATASETS / name
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg_overrides = {
        "structure.structure_type": "iso_line",
        "dataset.structure_distribution": dist_override or dist_configs(),
        "dataset.random_parameters": True,
        "dataset.cd_range": [20, 80],
        "dataset.height_range": [40, 120],
        "dataset.pitch_range": [60, 200],
    }
    for k, v in cfg_overrides.items():
        cfg.merged()[k.split(".")[0]] = cfg.merged().get(k.split(".")[0], {})
        parts = k.split(".")
        node = cfg.merged()
        for p in parts[:-1]:
            if not isinstance(node.get(p), dict):
                node[p] = {}
            node = node[p]
        node[parts[-1]] = v

    from semicon.orchestration.config import load_config as lc
    cfg2 = lc(None, defaults_path=str(ROOT_SIM / "configs" / "defaults.yml"), overrides=cfg_overrides)

    print(f"\n{'='*60}")
    print(f"Generating {name} ({n_samples} images, seed={master_seed})")
    print(f"{'='*60}")

    t0 = time.perf_counter()
    job = run_job(ctx, cfg2, out_dir, n_samples=n_samples, master_seed=master_seed, config_path=name)
    elapsed = time.perf_counter() - t0

    print(f"Completed: {job.n_ok} OK / {job.n_failed} failed in {elapsed:.1f}s ({elapsed/n_samples:.2f}s/img)")
    return {
        "name": name,
        "n_total": n_samples,
        "n_ok": job.n_ok,
        "n_failed": job.n_failed,
        "time_s": round(elapsed, 1),
        "time_per_image_s": round(elapsed / n_samples, 3),
        "seed": master_seed,
    }


def validate_ds(name: str):
    """Compute and print dataset statistics."""
    ds_path = DATASETS / name
    idx_path = ds_path / "dataset_index.json"
    if not idx_path.exists():
        print(f"  WARNING: {name} index not found")
        return {}
    idx = json.loads(idx_path.read_text())
    samples = idx.get("samples", [])

    from collections import Counter
    types = Counter(s["structure_type"] for s in samples)
    statuses = Counter(s.get("status", "?") for s in samples)

    # Checksum verification
    sums_path = ds_path / "SHA256SUMS"
    n_check = 0
    n_valid = 0
    if sums_path.exists():
        lines = [l for l in sums_path.read_text().strip().splitlines() if l and not l.startswith("#")]
        for line in lines:
            h_expected, rel = line.split("  ", 1)
            p = ds_path / rel
            if p.exists():
                h = hashlib.sha256(p.read_bytes()).hexdigest()
                n_check += 1
                if h == h_expected:
                    n_valid += 1

    print(f"\n{name} Statistics:")
    print(f"  Samples: {len(samples)} total, {statuses.get('OK', 0)} OK, {statuses.get('FAILED', 0)} FAILED")
    print(f"  Structure distribution: {dict(types)}")
    print(f"  Checksums: {n_valid}/{n_check} valid")

    return {
        "n_samples": len(samples),
        "status": dict(statuses),
        "structure_distribution": dict(types),
        "checksum_valid": n_valid,
        "checksum_total": n_check,
    }


if __name__ == "__main__":
    results = []
    results.append(generate_ds("ds2_unit_test", 100, 2002))
    results.append(generate_ds("ds3_validation", 1000, 3003))
    results.append(generate_ds("ds4_scientific_benchmark", 200, 4004))

    for r in results:
        validate_ds(r["name"])

    summary = {"datasets": results}
    summary_path = PROJECT_ROOT / "validation" / "reports" / "dg3_generation_report.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2))
    print(f"\nSummary written to {summary_path}")
