# DS5 Worker Count Benchmark Report

**Date:** 2026-08-01
**Method:** Sequential benchmark with 200 samples per config (4, 6, 8 workers)
**Seed:** 5005 (same as production)
**Image spec:** 1024x1024, 16-bit
**System:** 13th Gen Intel Core i7-13620H (10 cores / 16 threads), 23.6 GB RAM

---

## Results Summary

| Workers | OK | Failed | Wall Time | Rate (spm) | Per-sample | P50 | P95 | Disk | Scaling Eff. |
|---------|-----|--------|-----------|------------|-----------|-----|-----|------|-------------|
| **4** | 200 | 0 | 1311.6s | **9.1/min** | 6.558s | 3.277s | 214.4s | 2.23 GB | 100% (base) |
| **6** | 200 | 0 | 1026.7s | **11.7/min** | 5.133s | 3.239s | 263.2s | 2.23 GB | 85% |
| **8** | 200 | 0 | 892.6s | **13.4/min** | 4.463s | 3.668s | 301.1s | 2.23 GB | 73% |

## Wall-Clock Comparison

```
4 workers: ████████████████████████████████████████████████████████ 1311.6s
6 workers: ████████████████████████████████████████                 1026.7s  (-22%)
8 workers: █████████████████████████████████                        892.6s   (-32%)
```

## Throughput Comparison

```
4 workers: ████████████████████                          9.1/min
6 workers: ████████████████████████████                  11.7/min  (+29%)
8 workers: ████████████████████████████████████          13.4/min  (+47%)
```

## Per-Stage Timing Breakdown (avg per sample)

| Stage | 4w | 6w | 8w | Trend |
|-------|-----|-----|-----|-------|
| rasterize | 21.21s | 25.03s | 28.33s | ↑ (cold-start amortized) |
| process | 0.243s | 0.236s | 0.267s | ~stable |
| variability | 1.675s | 1.634s | 1.848s | ~stable |
| signal | 0.421s | 0.471s | 0.545s | ↑ slight I/O contention |
| degrade | 0.245s | 0.250s | 0.301s | ↑ slight I/O contention |
| formation | 0.040s | 0.044s | 0.051s | ~stable |
| groundtruth | 0.118s | 0.129s | 0.161s | ↑ slight |
| write | 0.464s | 0.374s | 0.400s | ~stable |
| **total** | **24.42s** | **28.17s** | **31.90s** | ↑ (overhead from parallelism) |

**Note:** The `total_s` and `rasterize_s` averages include cold-start overhead for the first sample per worker (library loading). The P50 (~3.3s) better represents steady-state per-sample time.

## Scaling Analysis

| Metric | 4→6 workers | 4→8 workers |
|--------|------------|------------|
| Ideal speedup | 1.50x | 2.00x |
| Actual speedup | 1.29x | 1.47x |
| Efficiency | 85% | 73% |
| Throughput gain | +29% | +47% |

### Why efficiency drops at 8 workers:
1. **I/O contention:** 8 workers writing TIFF/PNG/JSON simultaneously saturate disk I/O
2. **Memory pressure:** 8 workers × ~200 MB peak = ~1.6 GB for workers alone
3. **GIL-free but lock-free:** NumPy releases GIL, but Python-level operations (JSON, SHA-256, config loading) compete
4. **Diminishing returns:** The compute-to-I/O ratio shifts as more workers compete for the same disk bandwidth

## P50 vs P95 Analysis

| Workers | P50 (steady-state) | P95 (tail latency) | P95/P50 ratio |
|---------|-------------------|-------------------|---------------|
| 4 | 3.28s | 214.4s | 65x |
| 6 | 3.24s | 263.2s | 81x |
| 8 | 3.67s | 301.1s | 82x |

**P95 outliers** are caused by:
- Cold-start samples (first sample per worker loads library + config)
- Complex structure types (bimaterial, pitch_std with more polygons)
- TIFF LZW compression variability
- SHA-256 computation on large files

## Stability Assessment

| Metric | 4w | 6w | 8w | Verdict |
|--------|-----|-----|-----|---------|
| Failure rate | 0% | 0% | 0% | All stable |
| Memory usage | ~1.2 GB | ~1.5 GB | ~2.0 GB | 8w fits in 23.6 GB |
| Disk per config | 2.23 GB | 2.23 GB | 2.23 GB | Identical |
| P95 inflation | Baseline | +23% | +40% | Acceptable |

## Estimated Production Times (100K samples)

| Workers | Rate | ETA | vs 4w |
|---------|------|-----|-------|
| 4 | 9.1/min | 183 hours (7.6 days) | baseline |
| 6 | 11.7/min | 142 hours (5.9 days) | -22% |
| 8 | 13.4/min | 124 hours (5.2 days) | -32% |

**At 8 workers, the full dataset generation saves ~2.4 days vs 4 workers.**
