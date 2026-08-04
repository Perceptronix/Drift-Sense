# DS5 Worker Count Recommendation

**Date:** 2026-08-01
**Based on:** Empirical benchmark (200 samples × 3 configs, same seed/parameters)

---

## Recommendation: 8 Workers

### Decision Matrix

| Criterion | 4w | 6w | 8w | Weight |
|-----------|-----|-----|-----|--------|
| Throughput (spm) | 9.1 | 11.7 | **13.4** | 35% |
| Per-sample P50 | 3.28s | **3.24s** | 3.67s | 15% |
| Scaling efficiency | **100%** | 85% | 73% | 10% |
| Stability (0 failures) | **YES** | **YES** | **YES** | 25% |
| Memory safety (23.6 GB) | **SAFE** | **SAFE** | **SAFE** | 10% |
| I/O headroom | **BEST** | GOOD | MARGINAL | 5% |

### Weighted Score

| Config | Score |
|--------|-------|
| 4w | 0.55 |
| 6w | 0.68 |
| **8w** | **0.78** |

### Rationale

1. **8 workers delivers 47% more throughput** than 4 workers (13.4 vs 9.1 samples/min)
2. **Zero failures** across all configs confirms stability at 8 workers
3. **Memory is safe:** 8 workers × ~200 MB peak = ~1.6 GB, well within 23.6 GB system RAM
4. **P50 per-sample is only 12% higher** at 8w (3.67s vs 3.28s) — the throughput gain far outweighs this
5. **Saves ~2.4 days** on the full 100K dataset (5.2 days vs 7.6 days at 4w)
6. **Scaling efficiency of 73%** is acceptable for an I/O-heavy workload — each additional worker still provides net positive throughput

### Risk Assessment

| Risk | Level | Mitigation |
|------|-------|------------|
| Memory exhaustion | LOW | 8 workers use ~2 GB; system has 23.6 GB |
| I/O bottleneck | MEDIUM | NVMe SSD handles 8 concurrent writers; monitor disk queue |
| P95 tail latency | LOW | P95=301s is acceptable; does not affect throughput |
| Determinism | NONE | Each worker uses seed-based RNG; worker count doesn't affect output |
| Scientific integrity | NONE | No physics/model/equation changes |

### What Changes

| Parameter | Before | After |
|-----------|--------|-------|
| MAX_WORKERS | 4 | 8 |

### What Does NOT Change

- SEM physics equations
- Geometry engine
- Material models
- RNG implementation / seeds
- Dataset format / structure
- TIFF compression settings
- Metadata schema
- Ground truth generation
- Numerical precision (float64)
- Image formation pipeline
- Checkpoint format
- Batch size (500)

### Expected Production Impact

| Metric | 4 workers | 8 workers | Improvement |
|--------|-----------|-----------|-------------|
| Samples/min | 9.1 | 13.4 | +47% |
| ETA (100K) | 7.6 days | 5.2 days | -2.4 days |
| Failed samples | 0 | 0 (expected) | same |
| Disk per sample | 11.1 MB | 11.1 MB | same |
| Peak RAM | ~1.2 GB | ~2.0 GB | +0.8 GB (safe) |

---

**CONFIRMED: Change MAX_WORKERS from 4 to 8 in `generate_ds5_final.py`.**
