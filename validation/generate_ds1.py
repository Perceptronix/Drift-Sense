#!/usr/bin/env python3
"""DG2: Generate the official DS1 development dataset (50 images, seed=1001)."""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "simulator"
sys.path.insert(0, str(ROOT / "src"))

from semicon.geometry.raster import save_library
from semicon.geometry.structures import build_structure_library
from semicon.orchestration.config import load_config
from semicon.orchestration.job import run_job
from semicon.orchestration.pipeline import build_context, APP_VERSION


def main() -> int:
    out = ROOT.parent / "datasets" / "ds1"
    out.mkdir(parents=True, exist_ok=True)

    lib_path = out / "_lib.gds"
    lib = build_structure_library(fov_nm=320.0, cd_nm=40.0, height_nm=70.0)
    save_library(lib, lib_path)

    context = build_context(
        str(lib_path),
        app_version=APP_VERSION,
        git_hash="dg2",
    )

    cfg = load_config(
        None,
        defaults_path=str(ROOT / "configs" / "defaults.yml"),
        overrides={
            "structure.structure_type": "iso_line",
            "structure.cd_nm": 40.0,
            "structure.height_nm": 70.0,
            "structure.pitch_nm": None,
            "structure.width_nm": 320.0,
            "structure.height_nm_fov": 320.0,
            "structure.pixel_size_nm": 1.0,
            "variability.enabled": True,
            "variability.ler_3sigma_nm": 1.5,
            "variability.ler_xi_nm": 20.0,
            "physics.noise_enabled": True,
            "physics.counts_per_electron": 200.0,
            "dataset.structure_distribution.iso_line": 5,
            "dataset.structure_distribution.dense_ls": 5,
            "dataset.structure_distribution.contact": 5,
            "dataset.structure_distribution.via": 5,
            "dataset.structure_distribution.trench": 5,
            "dataset.structure_distribution.fin": 5,
            "dataset.structure_distribution.gate": 5,
            "dataset.structure_distribution.sti": 5,
            "dataset.structure_distribution.bimaterial": 5,
            "dataset.structure_distribution.pitch_std": 5,
            "dataset.random_parameters": True,
            "dataset.cd_range": [20, 80],
            "dataset.height_range": [40, 120],
            "dataset.pitch_range": [60, 200],
        },
    )

    print("Generating DS1 (50 images, seed=1001)...")
    t0 = time.perf_counter()
    job = run_job(context, cfg, out, n_samples=50, master_seed=1001, config_path="ds1_v1.0.0")
    elapsed = time.perf_counter() - t0

    print(f"Completed: {job.n_ok} OK / {job.n_failed} failed in {elapsed:.1f}s ({elapsed/50:.2f}s/img)")
    if job.failures:
        print("Failures:", job.failures)

    return 0 if job.n_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
