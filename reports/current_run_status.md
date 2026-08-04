# DS5 Current Production Run Status

**Audit Time:** 2026-08-01 (approx 12:00 UTC)
**Generator Status:** RUNNING

---

## Run Summary

| Metric | Value |
|--------|-------|
| **Total Target** | 100,000 samples |
| **Completed (checkpoint)** | 5,500 |
| **On-disk images** | 5,614 |
| **In-progress batch** | Batch 12 (indices 5500-5999) |
| **Batch progress** | ~114/500 samples written to disk |
| **Failed samples** | 0 |
| **Completion** | 5.5% |
| **Remaining** | 94,500 samples |

## Worker Configuration

| Parameter | Value |
|-----------|-------|
| **Active workers** | 4 |
| **Worker PIDs** | 6164, 14152, 17420, 26252 |
| **Main process PID** | 8596 |
| **Worker start time** | 2026-08-01 01:20:07 |
| **CPU** | 13th Gen Intel Core i7-13620H (10 cores / 16 threads) |
| **Worker CPU utilization** | ~50% each (I/O-bound phases) |

## Timing

| Metric | Value |
|--------|-------|
| **Start time** | 2026-08-01 01:20:07 |
| **Elapsed** | ~10.6 hours |
| **Average batch time (500 samples)** | 2,748s (~46 min) |
| **Average rate (production batches)** | 11.0 samples/min |
| **Per-sample (single-core equiv)** | 3.8s |

### Batch-by-Batch Timing

| Batch | Total Done | Batch Time (s) | Rate (samples/min) |
|-------|-----------|----------------|---------------------|
| 1 | 300 | 1,447 | 20.7 |
| 2 | 500 | 4,827 | 6.2 |
| 3 | 1,000 | 2,574 | 11.7 |
| 4 | 1,500 | 2,534 | 11.8 |
| 5 | 2,000 | 2,762 | 10.9 |
| 6 | 2,500 | 3,488 | 8.6 |
| 7 | 3,000 | 2,376 | 12.6 |
| 8 | 3,500 | 2,877 | 10.4 |
| 9 | 4,000 | 2,430 | 12.3 |
| 10 | 4,500 | 2,879 | 10.4 |
| 11 | 5,000 | 2,385 | 12.6 |
| 12 | 5,500 | 2,951 | 10.2 |

**Trend:** Rate has stabilized at ~10-12 samples/min across recent batches.

## System Resources

| Resource | Value |
|----------|-------|
| **Total RAM** | 23.6 GB |
| **Used RAM** | 21.4 GB (90.7%) |
| **Free RAM** | 2.2 GB |
| **Disk (E:)** | 300 GB total |
| **Disk free** | 236.9 GB (79.0%) |
| **Dataset size** | 61.5 GB |

### Memory Warning

**CRITICAL:** Only 2.2 GB free RAM. Each worker uses ~170 MB peak. With4 workers = ~680 MB for workers + ~212 MB for main process = ~900 MB Python total. The remaining ~20.5 GB is used by OS, disk cache, and other processes.

Adding workers to 6 or 8 requires ~340-680 MB additional RAM. With only 2.2 GB free, this is **tight** but feasible if other processes are minimal. Disk cache will shrink dynamically.

## File Integrity

| Artifact Type | Count | Checkpoint Match |
|---------------|-------|------------------|
| Images (.tiff) | 5,614 | +114 (in-progress batch) |
| Ground truth (.json) | 5,614 | +114 |
| Metadata (.json) | 5,614 | +114 |
| Height maps (.npy) | 5,614 | +114 |
| Material maps (.png) | 5,614 | +114 |

All artifact counts are consistent. The 114-file delta between checkpoint (5,500) and on-disk files (5,614) represents samples written during the current batch (12) that have not yet been checkpointed.

## Checkpoint Integrity

- **Checkpoint file:** `datasets/ds5_final_training/checkpoint.json`
- **Completed entries:** 5,500 (list of integer indices)
- **Failed entries:** 0
- **Last batch ID:** 12
- **Resume-safe:** YES - checkpoint保存 after each batch completion

## ETA

| Scenario | Workers | Estimated Completion |
|----------|---------|---------------------|
| Current rate (11/min) | 4 | ~144 hours (6.0 days) |
| Optimistic (15/min) | 4 | ~106 hours (4.4 days) |
| With 8 workers (est. 22/min) | 8 | ~72 hours (3.0 days) |

## Decision Required

The generator is actively producing samples. Before benchmarking can begin, a **graceful shutdown** is required to:

1. Allow the current batch (12) to complete
2. Ensure checkpoint is saved
3. Free resources for benchmark runs
4. Preserve all 5,500+ completed samples

**Recommended action:** Wait for batch 12 to complete, then stop the generator before starting benchmarks.
