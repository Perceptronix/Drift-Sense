# DS5 Final Worker Configuration

**Date:** 2026-08-01
**Status:** LOCKED

---

## Configuration Change

| File | Line | Before | After |
|------|------|--------|-------|
| `validation/generate_ds5_final.py` | 94 | `MAX_WORKERS = 4` | `MAX_WORKERS = 8` |

## Change Justification

Empirical benchmark (200 samples × 3 configs):
- **8 workers: 13.4 samples/min** (+47% vs 4w baseline of 9.1/min)
- 0 failures, memory safe (2.0 GB peak vs 23.6 GB available)
- Saves ~2.4 days on full 100K dataset generation

## Bit-Identicality Assurance

The worker count change does NOT affect:
- Random number generation (each worker uses seed-based RNG from master seed 5005)
- Physics equations
- Geometry generation
- Material properties
- Image formation
- TIFF compression
- Ground truth computation
- Numerical precision (float64)

Each sample's output is fully determined by (config, library, material_library, seed), NOT by worker count or processing order.

## Production State

| Metric | Value |
|--------|-------|
| Checkpoint | 5,662 completed, 338 failed |
| Failed samples | Will be retried on resume (batch 12 casualties) |
| Resume-safe | YES |
| Data integrity | VERIFIED (checkpoint matches on-disk files) |
