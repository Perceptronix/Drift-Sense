#!/usr/bin/env python3
"""DG4 Production Orchestrator: Generate DS5 (100,000 samples) with storage management.

Strategy:
  1. Generate in chunks of CHUNK_SIZE samples using the existing generate_ds5_final.py
  2. After each chunk, delete height.npy files (8 MB each, ~800 GB total for 100k)
     - height.npy is an intermediate physics buffer, NOT canonical ground truth
     - Per Phase 4.4 §1: edge maps, CD values, contours are the 5 GT components;
       height field is INPUT to GT derivation, not a GT component itself
     - Deletion after generation does not affect determinism or scientific fidelity
  3. The existing checkpoint.json ensures resume works across chunks
  4. Disk space is monitored before each chunk to prevent running out

Storage budget (E: drive, 298 GB free):
  - Per sample WITH height.npy:  ~10 MB  → 100k = ~1 TB (doesn't fit)
  - Per sample WITHOUT height.npy: ~2 MB  → 100k = ~200 GB (fits on E:)
  - Height.npy deletion saves ~800 GB

DS5 Spec (frozen Phase 5.5):
  - 100,000 images at 1024x1024, 16-bit, 1.0 nm/px
  - Weighted structure distribution (10 types)
  - Master seed: 5005
  - Splits: 70/15/15 (train/val/test)
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DS5_DIR = ROOT / "datasets" / "ds5_final_training"
GENERATE_SCRIPT = Path(__file__).resolve().parent / "generate_ds5_final.py"
LOG_DIR = ROOT / "logs" / "ds5_generation"

# Configuration
CHUNK_SIZE = 10_000         # samples per generation chunk
N_TOTAL = 100_000           # total DS5 samples
MASTER_SEED = 5005
WORKERS = 8                 # production: 8 parallel workers (benchmarked optimal)
MIN_FREE_GB = 15            # minimum free space to allow generation
HEIGHT_NPY_SIZE_MB = 8.0    # approximate size per height.npy file


def get_free_space_gb(path: Path) -> float:
    """Get free space on the drive containing path, in GB."""
    usage = shutil.disk_usage(str(path))
    return usage.free / (1024 ** 3)


def count_height_files(ds5_dir: Path) -> int:
    """Count height.npy files in ground_truth directory."""
    gt_dir = ds5_dir / "ground_truth"
    if not gt_dir.exists():
        return 0
    return len(list(gt_dir.glob("*_height.npy")))


def delete_height_files(ds5_dir: Path) -> int:
    """Delete all height.npy files from ground_truth. Returns count deleted."""
    gt_dir = ds5_dir / "ground_truth"
    if not gt_dir.exists():
        return 0
    deleted = 0
    for f in gt_dir.glob("*_height.npy"):
        f.unlink()
        deleted += 1
    return deleted


def load_checkpoint(ds5_dir: Path) -> dict:
    """Load checkpoint.json if it exists."""
    cp_path = ds5_dir / "checkpoint.json"
    if cp_path.exists():
        with open(cp_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"completed": [], "failed": {}, "total_generated": 0}


def run_generation_chunk(
    n_samples: int,
    master_seed: int,
    workers: int,
    out_dir: Path,
    resume: bool = True,
    max_new: int = None,
) -> int:
    """Run generate_ds5_final.py for n_samples. Returns exit code."""
    cmd = [
        sys.executable,
        str(GENERATE_SCRIPT),
        "--samples", str(n_samples),
        "--seed", str(master_seed),
        "--workers", str(workers),
        "--out", str(out_dir),
    ]
    if not resume:
        cmd.append("--no-resume")
    if max_new is not None:
        cmd.extend(["--max-new", str(max_new)])

    print(f"\n{'='*70}")
    print(f"Running generation: n_samples={n_samples}, max_new={max_new}, seed={master_seed}, workers={workers}")
    print(f"Output: {out_dir}")
    print(f"{'='*70}\n")

    result = subprocess.run(cmd, cwd=str(ROOT))
    return result.returncode


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="DG4: Production DS5 orchestrator with storage management")
    parser.add_argument("--total", type=int, default=N_TOTAL, help="Total samples to generate")
    parser.add_argument("--chunk-size", type=int, default=CHUNK_SIZE, help="Samples per chunk")
    parser.add_argument("--seed", type=int, default=MASTER_SEED, help="Master seed")
    parser.add_argument("--workers", type=int, default=WORKERS, help="Parallel workers")
    parser.add_argument("--skip-generation", action="store_true",
                        help="Skip generation, only do cleanup and report")
    parser.add_argument("--cleanup-only", action="store_true",
                        help="Only delete height.npy files and print stats")
    args = parser.parse_args()

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Ensure output directory exists
    DS5_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("DG4 PRODUCTION ORCHESTRATOR")
    print("=" * 70)
    print(f"  Target:     {args.total} samples")
    print(f"  Chunk size: {args.chunk_size}")
    print(f"  Master seed:{args.seed}")
    print(f"  Workers:    {args.workers}")
    print(f"  Output:     {DS5_DIR}")
    print()

    # Check initial state
    cp = load_checkpoint(DS5_DIR)
    already_done = len(cp.get("completed", []))
    print(f"  Already completed: {already_done}")

    if already_done > 0:
        hf = count_height_files(DS5_DIR)
        print(f"  Height.npy files on disk: {hf}")

    # Cleanup-only mode
    if args.cleanup_only:
        deleted = delete_height_files(DS5_DIR)
        print(f"\nDeleted {deleted} height.npy files")
        free = get_free_space_gb(DS5_DIR)
        print(f"Free space: {free:.1f} GB")
        return 0

    if not args.skip_generation:
        # Calculate chunks needed
        remaining = args.total - already_done
        if remaining <= 0:
            print("\nAll samples already generated!")
        else:
            n_chunks = (remaining + args.chunk_size - 1) // args.chunk_size
            print(f"  Remaining:  {remaining}")
            print(f"  Chunks:     {n_chunks}")
            print()

            chunk_num = 0
            for start_idx in range(already_done, args.total, args.chunk_size):
                chunk_num += 1
                chunk_end = min(start_idx + args.chunk_size, args.total)
                chunk_n = chunk_end - start_idx

                # Check disk space
                free_gb = get_free_space_gb(DS5_DIR)
                est_needed_gb = chunk_n * 10 / 1024  # ~10 MB per sample (incl height.npy)
                print(f"\n--- Chunk {chunk_num}/{n_chunks} ---")
                print(f"  Samples: {start_idx}–{chunk_end - 1} ({chunk_n} samples)")
                print(f"  Free space: {free_gb:.1f} GB (need ~{est_needed_gb:.1f} GB)")

                if free_gb < MIN_FREE_GB:
                    print(f"  WARNING: Low disk space ({free_gb:.1f} GB < {MIN_FREE_GB} GB minimum)")
                    # Try cleanup first
                    hf = count_height_files(DS5_DIR)
                    if hf > 0:
                        print(f"  Attempting cleanup: {hf} height.npy files ({hf * HEIGHT_NPY_SIZE_MB / 1024:.1f} GB)")
                        deleted = delete_height_files(DS5_DIR)
                        free_gb = get_free_space_gb(DS5_DIR)
                        print(f"  After cleanup: {free_gb:.1f} GB free")
                        if deleted > 0:
                            # Recompute checkpoint after deletion (checkpoint is unchanged,
                            # height.npy is not tracked in checkpoint)
                            print(f"  Deleted {deleted} height.npy files")

                    if free_gb < est_needed_gb + MIN_FREE_GB:
                        print(f"  ERROR: Insufficient space even after cleanup. Pausing.")
                        print(f"  Free: {free_gb:.1f} GB, Need: {est_needed_gb:.1f} GB + {MIN_FREE_GB} GB buffer")
                        return 1

                # Run generation for this chunk
                # Use total sample count + max_new to generate exactly chunk_n new samples
                t_start = time.time()
                rc = run_generation_chunk(
                    n_samples=args.total,
                    master_seed=args.seed,
                    workers=args.workers,
                    out_dir=DS5_DIR,
                    resume=True,
                    max_new=chunk_n,
                )
                elapsed = time.time() - t_start

                if rc != 0:
                    print(f"  WARNING: Generation script exited with code {rc}")
                    # Check if any new samples were completed
                    cp = load_checkpoint(DS5_DIR)
                    new_done = len(cp.get("completed", []))
                    print(f"  Completed so far: {new_done}/{args.total}")
                    if new_done == already_done:
                        print("  No new samples generated. Aborting.")
                        return 1
                    # Continue — some samples may have been generated

                # Post-chunk cleanup: delete height.npy files
                cp = load_checkpoint(DS5_DIR)
                done = len(cp.get("completed", []))
                hf = count_height_files(DS5_DIR)
                print(f"\n  Post-chunk status: {done}/{args.total} completed, {hf} height.npy files")

                if hf > 0:
                    freed_mb = hf * HEIGHT_NPY_SIZE_MB
                    print(f"  Deleting {hf} height.npy files (~{freed_mb:.0f} MB)...")
                    deleted = delete_height_files(DS5_DIR)
                    free_gb = get_free_space_gb(DS5_DIR)
                    print(f"  Deleted {deleted} files. Free space: {free_gb:.1f} GB")

                already_done = done
                if done >= args.total:
                    print(f"\n  All {args.total} samples generated!")
                    break

    # Final report
    print("\n" + "=" * 70)
    print("DG4 GENERATION STATUS")
    print("=" * 70)

    cp = load_checkpoint(DS5_DIR)
    done = len(cp.get("completed", []))
    failed = len(cp.get("failed", {}))
    hf = count_height_files(DS5_DIR)
    free_gb = get_free_space_gb(DS5_DIR)

    # Compute dataset size
    total_bytes = 0
    file_count = 0
    for root, dirs, files in os.walk(DS5_DIR):
        for fn in files:
            fp = Path(root) / fn
            if fn == "checkpoint.json" or fn.endswith(".tmp"):
                continue
            total_bytes += fp.stat().st_size
            file_count += 1

    print(f"  Completed:  {done}/{args.total}")
    print(f"  Failed:     {failed}")
    print(f"  Height.npy: {hf} files ({hf * HEIGHT_NPY_SIZE_MB / 1024:.1f} GB)")
    print(f"  Total size: {total_bytes / (1024**3):.1f} GB ({file_count} files)")
    print(f"  Free space: {free_gb:.1f} GB")
    print(f"  Splits:     {cp.get('splits', 'N/A')}")
    print("=" * 70)

    if done >= args.total:
        return 0
    else:
        print(f"\nGeneration incomplete: {done}/{args.total} samples")
        print("Re-run this script to resume from checkpoint.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
