#!/usr/bin/env python3
"""Worker count benchmark for DS5 generation.

Runs 3 independent benchmarks (4, 6, 8 workers) with 1000 samples each.
Uses offset indices to avoid overlapping with production data.
Measures: wall-clock, CPU, memory, disk throughput, per-stage timing.
"""
from __future__ import annotations

import gc
import hashlib
import json
import os
import shutil
import sys
import time
import tracemalloc
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
SIM_SRC = ROOT / "simulator" / "src"
sys.path.insert(0, str(SIM_SRC))

import numpy as np

from semicon.geometry.raster import save_library
from semicon.geometry.structures import build_structure_library
from semicon.orchestration.config import load_config
from semicon.orchestration.pipeline import (
    APP_VERSION,
    RuntimeContext,
    build_context,
    run_pipeline,
)
from semicon.dataset.writer import write_sample

# ---------------------------------------------------------------------------
# Benchmark parameters
# ---------------------------------------------------------------------------
BENCHMARK_SEED = 5005
BENCHMARK_N_SAMPLES = 1000
BENCHMARK_INDEX_OFFSET = 90000  # Avoid overlap with production indices
BENCHMARK_STRUCTURE_DISTRIBUTION = {
    "dense_ls": 20.0,
    "contact": 15.0,
    "iso_line": 15.0,
    "via": 10.0,
    "fin": 10.0,
    "gate": 10.0,
    "trench": 8.0,
    "sti": 5.0,
    "bimaterial": 4.0,
    "pitch_std": 3.0,
}

DS5_WIDTH_NM = 1024.0
DS5_HEIGHT_NM = 1024.0
DS5_PIXEL_SIZE_NM = 1.0
DS5_CD_RANGE = (10.0, 500.0)
DS5_HEIGHT_RANGE = (20.0, 200.0)
DS5_PITCH_RANGE = (20.0, 1000.0)
DS5_BEAM_ENERGY_RANGE = (0.3, 30.0)
DS5_PROBE_CURRENT_RANGE = (1.0, 1000.0)
DS5_PROBE_DIAMETER_RANGE = (0.5, 10.0)
DS5_LER_3SIGMA_RANGE = (0.0, 5.0)
DS5_LER_XI_RANGE = (5.0, 100.0)
DS5_OVERLAY_RANGE = (0.0, 10.0)
DS5_CDU_SIGMA_RANGE = (0.0, 2.0)


# ---------------------------------------------------------------------------
# Sample plan (identical to production)
# ---------------------------------------------------------------------------
def build_sample_plan(n_samples, master_seed, structure_distribution):
    import random as _random
    rng = _random.Random(master_seed)
    total_weight = sum(structure_distribution.values())
    types = []
    for stype, weight in structure_distribution.items():
        count = int(round(n_samples * weight / total_weight))
        types.extend([stype] * count)
    while len(types) < n_samples:
        types.append("iso_line")
    types = types[:n_samples]
    rng.shuffle(types)

    plan = []
    for i, stype in enumerate(types):
        cd = rng.uniform(*DS5_CD_RANGE)
        height = rng.uniform(*DS5_HEIGHT_RANGE)
        pitch = rng.uniform(*DS5_PITCH_RANGE)
        beam_energy = rng.uniform(*DS5_BEAM_ENERGY_RANGE)
        probe_current = rng.uniform(*DS5_PROBE_CURRENT_RANGE)
        probe_diameter = rng.uniform(*DS5_PROBE_DIAMETER_RANGE)
        ler_3sigma = rng.uniform(*DS5_LER_3SIGMA_RANGE)
        ler_xi = rng.uniform(*DS5_LER_XI_RANGE)
        overlay = rng.uniform(*DS5_OVERLAY_RANGE)
        cdu_sigma = rng.uniform(*DS5_CDU_SIGMA_RANGE)
        plan.append({
            "sample_index": i,
            "structure_type": stype,
            "overrides": {
                "structure.structure_type": stype,
                "structure.cd_nm": cd,
                "structure.height_nm": height,
                "structure.pitch_nm": pitch,
                "structure.width_nm": DS5_WIDTH_NM,
                "structure.height_nm_fov": DS5_HEIGHT_NM,
                "structure.pixel_size_nm": DS5_PIXEL_SIZE_NM,
                "variability.ler_3sigma_nm": ler_3sigma,
                "variability.ler_xi_nm": ler_xi,
                "variability.overlay_dx_nm": overlay * rng.uniform(-1, 1),
                "variability.overlay_dy_nm": overlay * rng.uniform(-1, 1),
                "variability.cdu_sigma_nm": cdu_sigma,
                "physics.beam_energy_keV": beam_energy,
                "physics.probe_current_pA": probe_current,
                "physics.probe_diameter_nm": probe_diameter,
            },
        })
    return plan


# ---------------------------------------------------------------------------
# Worker function
# ---------------------------------------------------------------------------
_WORKER_CTX: Optional[RuntimeContext] = None
_WORKER_DEFAULTS: Optional[str] = None


def _worker_init(lib_path: str, defaults_path: str) -> None:
    global _WORKER_CTX, _WORKER_DEFAULTS
    _WORKER_CTX = build_context(lib_path, app_version=APP_VERSION, git_hash="bench")
    _WORKER_DEFAULTS = defaults_path


def _generate_sample(item, out_dir, master_seed, dataset_name, offset):
    global _WORKER_CTX, _WORKER_DEFAULTS
    idx = item["sample_index"] + offset  # Apply offset
    try:
        from semicon.orchestration.config import _apply_overrides, _to_config, validate
        base_cfg = load_config(None, defaults_path=_WORKER_DEFAULTS)
        merged = base_cfg.merged()
        merged = _apply_overrides(merged, item["overrides"])
        cfg = validate(_to_config(merged))

        t0 = time.perf_counter()
        result = run_pipeline(
            _WORKER_CTX, cfg, Path(out_dir), idx,
            dataset_name, master_seed, write_outputs=True,
        )
        elapsed = time.perf_counter() - t0

        return {
            "sample_index": idx,
            "structure_type": item["structure_type"],
            "status": result.status,
            "error": result.error,
            "timing": result.timing,
            "wall_time": elapsed,
        }
    except Exception as exc:
        return {
            "sample_index": idx,
            "structure_type": item["structure_type"],
            "status": "FAILED",
            "error": f"{type(exc).__name__}: {exc}",
            "timing": {},
            "wall_time": 0,
        }


# ---------------------------------------------------------------------------
# Benchmark runner
# ---------------------------------------------------------------------------
@dataclass
class BenchmarkResult:
    workers: int
    n_samples: int
    wall_clock_s: float
    samples_per_min: float
    per_sample_s: float
    n_ok: int
    n_failed: int
    failures: List[str] = field(default_factory=list)
    stage_timings: Dict[str, List[float]] = field(default_factory=dict)
    peak_memory_mb: float = 0.0
    total_disk_bytes: int = 0
    timing_samples: List[float] = field(default_factory=list)
    avg_stage_times: Dict[str, float] = field(default_factory=dict)


def run_benchmark(
    n_workers: int,
    plan: List[Dict],
    lib_path: str,
    defaults_path: str,
    master_seed: int,
) -> BenchmarkResult:
    """Run a single benchmark with the given worker count."""
    out_dir = ROOT / "datasets" / f"benchmark_{n_workers}w"
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    dataset_name = f"benchmark_{n_workers}w"

    print(f"\n{'='*60}")
    print(f"BENCHMARK: {n_workers} workers, {len(plan)} samples")
    print(f"Output: {out_dir}")
    print(f"{'='*60}")

    gc.collect()
    tracemalloc.start()

    t_start = time.time()
    results = []
    all_stage_timings = {}

    with ProcessPoolExecutor(
        max_workers=n_workers,
        initializer=_worker_init,
        initargs=(lib_path, defaults_path),
    ) as executor:
        futures = {
            executor.submit(
                _generate_sample, item, str(out_dir), master_seed, dataset_name, BENCHMARK_INDEX_OFFSET
            ): item["sample_index"]
            for item in plan
        }
        done_count = 0
        for future in as_completed(futures):
            idx = futures[future]
            try:
                result = future.result(timeout=600)
                results.append(result)
                done_count += 1
                if done_count % 100 == 0:
                    elapsed = time.time() - t_start
                    rate = done_count / (elapsed / 60)
                    print(f"  [{done_count}/{len(plan)}] {rate:.1f} samples/min")
            except Exception as exc:
                results.append({
                    "sample_index": idx + BENCHMARK_INDEX_OFFSET,
                    "status": "FAILED",
                    "error": str(exc),
                    "timing": {},
                    "wall_time": 0,
                })
                done_count += 1

    wall_clock = time.time() - t_start

    _, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Compute disk usage
    total_disk = 0
    for root_dir, dirs, files in os.walk(out_dir):
        for fn in files:
            total_disk += (Path(root_dir) / fn).stat().st_size

    # Aggregate timing data
    n_ok = sum(1 for r in results if r["status"] == "OK")
    n_failed = sum(1 for r in results if r["status"] == "FAILED")
    failures = [f"{r['sample_index']}: {r.get('error', '?')}" for r in results if r["status"] == "FAILED"]
    timing_samples = [r["wall_time"] for r in results if r["wall_time"] > 0]

    # Aggregate per-stage timings
    for r in results:
        if r.get("timing"):
            for stage, t in r["timing"].items():
                if stage not in all_stage_timings:
                    all_stage_timings[stage] = []
                all_stage_timings[stage].append(t)

    avg_stage = {k: float(np.mean(v)) for k, v in all_stage_timings.items()}

    bench = BenchmarkResult(
        workers=n_workers,
        n_samples=len(plan),
        wall_clock_s=wall_clock,
        samples_per_min=n_ok / (wall_clock / 60) if wall_clock > 0 else 0,
        per_sample_s=wall_clock / n_ok if n_ok > 0 else 0,
        n_ok=n_ok,
        n_failed=n_failed,
        failures=failures[:10],  # First 10 failures
        stage_timings=all_stage_timings,
        peak_memory_mb=peak_memory / (1024 * 1024),
        total_disk_bytes=total_disk,
        timing_samples=timing_samples,
        avg_stage_times=avg_stage,
    )

    print(f"\n  Result: {n_ok}/{len(plan)} OK, {n_failed} failed")
    print(f"  Wall-clock: {wall_clock:.1f}s ({wall_clock/60:.1f} min)")
    print(f"  Rate: {bench.samples_per_min:.1f} samples/min")
    print(f"  Per-sample: {bench.per_sample_s:.2f}s")
    print(f"  Peak memory: {bench.peak_memory_mb:.1f} MB")
    print(f"  Disk: {total_disk / (1024*1024):.1f} MB")
    if avg_stage:
        print(f"  Stage timings (avg per sample):")
        for stage in sorted(avg_stage.keys()):
            print(f"    {stage}: {avg_stage[stage]*1000:.1f}ms")

    return bench


# ---------------------------------------------------------------------------
# Bit-identity verification
# ---------------------------------------------------------------------------
def verify_bit_identical(dir_a: Path, dir_b: Path, n_samples: int = 5) -> bool:
    """Compare first n_samples images bit-by-bit between two benchmark dirs."""
    print(f"\nVerifying bit-identity (first {n_samples} samples)...")
    imgs_a = sorted((dir_a / "images").glob("*.tiff"))[:n_samples]
    imgs_b = sorted((dir_b / "images").glob("*.tiff"))[:n_samples]

    if len(imgs_a) != len(imgs_b):
        print(f"  FAIL: different image counts ({len(imgs_a)} vs {len(imgs_b)})")
        return False

    all_match = True
    for a, b in zip(imgs_a, imgs_b):
        ha = hashlib.sha256(a.read_bytes()).hexdigest()
        hb = hashlib.sha256(b.read_bytes()).hexdigest()
        match = ha == hb
        if not match:
            print(f"  MISMATCH: {a.name}")
            all_match = False

    if all_match:
        print(f"  PASS: all {n_samples} images are bit-identical")
    return all_match


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    import argparse
    parser = argparse.ArgumentParser(description="Benchmark worker counts")
    parser.add_argument("--workers", type=int, nargs="+", default=[4, 6, 8],
                        help="Worker counts to benchmark")
    parser.add_argument("--samples", type=int, default=BENCHMARK_N_SAMPLES,
                        help="Samples per benchmark")
    parser.add_argument("--verify-only", action="store_true",
                        help="Only verify existing benchmark results")
    args = parser.parse_args()

    lib_path_val = str(ROOT / "datasets" / "ds5_final_training" / "_lib_validation.gds")
    defaults_path = str(ROOT / "simulator" / "configs" / "defaults.yml")

    if not Path(lib_path_val).exists():
        print("Building structure library...")
        lib = build_structure_library(fov_nm=DS5_WIDTH_NM, cd_nm=40.0, height_nm=70.0)
        save_library(lib, Path(lib_path_val))

    plan = build_sample_plan(args.samples, BENCHMARK_SEED, BENCHMARK_STRUCTURE_DISTRIBUTION)
    print(f"Sample plan: {len(plan)} samples, {len(set(p['structure_type'] for p in plan))} structure types")

    results = []

    if not args.verify_only:
        for n_workers in args.workers:
            gc.collect()
            time.sleep(2)  # Let system settle between benchmarks

            bench = run_benchmark(
                n_workers=n_workers,
                plan=plan,
                lib_path=lib_path_val,
                defaults_path=defaults_path,
                master_seed=BENCHMARK_SEED,
            )
            results.append(bench)

    # Save results
    results_data = []
    for r in results:
        d = {
            "workers": r.workers,
            "n_samples": r.n_samples,
            "wall_clock_s": round(r.wall_clock_s, 2),
            "samples_per_min": round(r.samples_per_min, 2),
            "per_sample_s": round(r.per_sample_s, 3),
            "n_ok": r.n_ok,
            "n_failed": r.n_failed,
            "failures": r.failures,
            "peak_memory_mb": round(r.peak_memory_mb, 1),
            "total_disk_mb": round(r.total_disk_bytes / (1024*1024), 1),
            "avg_stage_times": {k: round(v, 4) for k, v in r.avg_stage_times.items()},
        }
        results_data.append(d)

    results_path = ROOT / "reports" / "benchmark_results.json"
    with open(results_path, "w") as f:
        json.dump(results_data, f, indent=2)
    print(f"\nResults saved to {results_path}")

    # Bit-identity verification
    if len(results) >= 2:
        dir_a = ROOT / "datasets" / f"benchmark_{results[0].workers}w"
        dir_b = ROOT / "datasets" / f"benchmark_{results[1].workers}w"
        verify_bit_identical(dir_a, dir_b, n_samples=5)

    # Summary
    print(f"\n{'='*70}")
    print("BENCHMARK SUMMARY")
    print(f"{'='*70}")
    print(f"{'Workers':>8} {'Rate':>10} {'Per-sample':>12} {'Memory':>10} {'Disk':>10} {'OK':>6}")
    print(f"{'-'*8} {'-'*10} {'-'*12} {'-'*10} {'-'*10} {'-'*6}")
    for r in results:
        print(f"{r.workers:>8} {r.samples_per_min:>9.1f}/m {r.per_sample_s:>10.2f}s "
              f"{r.peak_memory_mb:>8.0f}MB {r.total_disk_bytes/1024/1024:>8.0f}MB {r.n_ok:>6}")

    # Scaling efficiency
    if len(results) >= 2:
        base = results[0]
        print(f"\nScaling efficiency (relative to {base.workers} workers):")
        for r in results:
            ideal_speedup = r.workers / base.workers
            actual_speedup = base.per_sample_s / r.per_sample_s if r.per_sample_s > 0 else 0
            efficiency = actual_speedup / ideal_speedup * 100 if ideal_speedup > 0 else 0
            print(f"  {r.workers} workers: {actual_speedup:.2f}x speedup (ideal {ideal_speedup:.2f}x, "
                  f"efficiency {efficiency:.0f}%)")

    # Cleanup
    print(f"\nCleaning up benchmark directories...")
    for r in results:
        d = ROOT / "datasets" / f"benchmark_{r.workers}w"
        if d.exists():
            shutil.rmtree(d)
            print(f"  Deleted {d.name}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
