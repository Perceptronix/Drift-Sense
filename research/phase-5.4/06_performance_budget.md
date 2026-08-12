# Performance Budget

**Research Phase:** 5.4
**Document:** 06_performance_budget.md
**Date:** 2026-07-30

---

## 1. Reference Platform

| Component | Specification |
|---|---|
| CPU | 8+ cores, 3 GHz+ (x86-64) |
| RAM | 32 GB |
| Disk | SSD, 100+ GB free |
| OS | Linux (CI) / Windows 11 (dev) |
| Python | 3.11+ |

---

## 2. Memory Budget

| Item | Budget | Notes |
|---|---|---|
| HeightField (float64 1024²) | 8 MB | One per stage |
| MaterialMap (uint8 1024²) | 1 MB | |
| YieldMaps (2 × float64) | 16 MB | |
| PSF kernel + FFT workspace | ≤ 64 MB | 2× padded size |
| Intermediate peak | ≤ 128 MB | Worst stage |
| **Per-worker RSS budget** | **< 500 MB** | 4 workers < 2 GB total |
| Max image 4096² | < 4 GB/worker | Documented max |

**Acceptance:** RSS < 500 MB/worker for 1024² workload (measured via `memory_profiler`).

---

## 3. Runtime Budget (per image, sequential)

| Stage | Budget | Module |
|---|---|---|
| Config load + validation | < 50 ms | config_parser |
| Structure (raster) | < 50 ms | geo_raster |
| Process model | < 150 ms | geo_process |
| Variability | < 150 ms | geo_variability |
| Signal | < 200 ms | phys_signal |
| Degrade (FFT) | < 250 ms | phys_degrade |
| Formation | < 20 ms | phys_formation |
| Ground truth | < 150 ms | data_groundtruth (parallel) |
| Write + metadata | < 50 ms | data_writer |
| **Total sequential** | **< 3.0 s** | 1024×1024 |

**Acceptance:** p95 of per-image time < 3.0 s sequential; < 1.0 s effective at 4 workers.

---

## 4. Batch Throughput

| Dataset size | Sequential | 4 workers | Effective/image |
|---|---|---|---|
| 100 | < 5 min | < 2 min | < 1.2 s |
| 1,000 | < 50 min | < 15 min | < 0.9 s |
| 10,000 | < 8 hr | < 2.5 hr | < 0.9 s |
| 100,000 | < 3.5 days | < 1 day | < 0.9 s |

**Acceptance:** ≥ 3.5× speedup at 4 workers (Amdahl efficiency ≥ 87% at p = 0.95 parallelizable).

---

## 5. Parallel Scalability

| Workers | Target speedup | Efficiency |
|---|---|---|
| 2 | 1.9× | 95% |
| 4 | 3.5× | 87% |
| 8 | 6.0× | 75% |
| 16 | 9.0× | 56% |

**Bottleneck guards:** cache hits reduce per-image work; I/O to SSD; process isolation (RD3). Watch: FFT threads oversubscription — pin BLAS threads to 1 per worker (operational policy).

---

## 6. Cache Efficiency

| Metric | Target |
|---|---|
| Hit rate (repeated structure+params) | ≥ 50% |
| Hit latency | < 10 ms (disk load) |
| Memory cache (optional) | ≤ 2 GB total |
| Invalidation | Config-change → miss |

**Acceptance:** benchmark dataset with 30% repeated structures shows ≥ 50% cache hit and ≥ 1.5× end-to-end speedup vs no cache.

---

## 7. Storage Requirements

| Item | Size | Notes |
|---|---|---|
| TIFF image (1024², 16-bit, LZW) | < 3 MB | Lossless |
| GT JSON per sample | < 50 KB | Edges + CD + contours |
| Config + metadata JSON | < 100 KB | |
| Height field .npy | 8 MB | Optional artifact |
| **Per-sample total (core)** | **< 4 MB** | Image + GT + metadata |
| 100,000-sample dataset (core) | < 400 GB | |
| With optional height fields | + 800 GB | Flag-gated |

**Acceptance:** core per-sample < 4 MB; dataset_index for 100K < 100 MB; SHA256SUMS generation < 10 min for 100K.

---

## 8. Performance Profiling Gates

| Gate | Measure | Target |
|---|---|---|
| Step 3 (geometry) | raster+process+var | < 350 ms |
| Step 5 (physics) | signal+degrade+form | < 500 ms |
| M5 (batch) | 1000-image throughput | < 15 min @ 4W |
| M6 (production) | cache + parallel | ≥ 1.5× no-cache; ≥ 3.5× @ 4W |
| L5 (acceptance) | full budget | all above |

---

## 9. Performance Risk Register

| Risk | Mitigation |
|---|---|
| FFT memory blowup at 4096² | Pad-to-fast-size; chunk if needed; document max |
| BLAS thread oversubscription | Pin threads per worker |
| Disk I/O bottleneck at 100K | Batch writes; atomic renames; SSD |
| Cache memory growth | LRU + size cap |
| GT parallel overhead | Thread pool sized to cores; fallback sequential |

---

## Sources

- Phase 4.3 — Runtime estimates, RD3 (process pool), RD8 (cache), RD6 (perf).
- Phase 5.1 — Success metrics (performance category).
- Phase 5.2/5.3 — Module-level performance notes (PSF < 200 ms, etc.).
- [S7] G. Amdahl, "Validity of the single processor approach to achieving large scale computing capabilities," AFIPS, 1967.
- [S8] J. L. Hennessy, D. A. Patterson, *Computer Architecture: A Quantitative Approach*, 6th ed. Morgan Kaufmann, 2017.
