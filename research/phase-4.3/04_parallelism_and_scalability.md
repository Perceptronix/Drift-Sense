# Parallelism and Scalability

**Research Phase:** 4.3
**Document:** 04_parallelism_and_scalability.md
**Date:** 2026-07-30

---

## 1. Parallelism Analysis

### 1.1 Where Parallelism is Safe

| Granularity | Mechanism | Safe? | Rationale |
|---|---|---|---|
| **Between jobs** (different structures, different seeds) | Process pool | ✅ Yes | No shared state; no communication; embarrassingly parallel |
| **Within a single pipeline** (one image) | None — sequential | ✅ Always | Pipeline is inherently sequential; each stage depends on the previous |
| **Within a single stage** (e.g., per-pixel operations) | Vectorization | ✅ Yes | NumPy operations are already vectorized and parallelized internally |
| **Between stages** (pipeline parallelism) | — | ❌ No | Each stage depends on the previous stage's output |

**Engineering Decision:** The only safe parallelism model is **data parallelism across independent jobs**. No parallel execution within a single pipeline.

### 1.2 Why Within-Pipeline Parallelism is Not Safe

| Attempted Parallelism | Problem |
|---|---|
| Run geometry and physics simultaneously | Physics needs geometry output |
| Process model and LER simultaneously | LER needs process model output |
| Multiple layers in parallel | Each layer depends on previous layer's topography |
| Signal and ground truth simultaneously | Ground truth needs height field (which is signal input too — but they don't modify it, so this could be safe as independent consumers of the same input) |

**Exception — Independent consumers:** Signal generation (M4) and ground truth generation (M7) can run in **parallel** after variability (M3), because both consume the same HeightField_var and MaterialMap_var without modifying them. This is the only safe intra-pipeline parallelism opportunity.

```
  M3 Variability
       │
       ├────▶ M4 Signal Gen ──▶ M5 Degrade ──▶ M6 Image Form
       │
       │
       └────▶ M7 Ground Truth
```

This saves ~10–15% of pipeline time (the M7 path runs concurrently with M4→M5→M6).

---

## 2. Scalability Model

### 2.1 Resource Requirements per Pipeline

| Resource | Per Image (1024×1024) | Scaling |
|---|---|---|
| CPU time | 0.5–3 s (geometry + physics) | O(M × N × N_layers) |
| Memory | 50–300 MB (height field, intermediate arrays) | O(M × N) |
| Disk (image + metadata) | 2–10 MB | O(M × N) |
| Disk (ground truth, if enabled) | 1–20 MB | O(M × N) |

### 2.2 Scaling Predictions

| N_images | Sequential Wall Time | 4 Workers | 16 Workers |
|---|---|---|---|
| 1 | 2 s | 2 s | 2 s |
| 10 | 20 s | 5 s | 2 s |
| 100 | 3.3 min | 50 s | 13 s |
| 1,000 | 33 min | 8 min | 2 min |
| 10,000 | 5.6 h | 1.4 h | 21 min |
| 100,000 | 56 h | 14 h | 3.5 h |
| 1,000,000 | 23 days | 6 days | 1.5 days |

**Inference:** For typical datasets (<10,000 images), single workstation with 16 cores is sufficient. Beyond that, HPC or cloud scaling is needed.

### 2.3 Memory Scaling

| N_workers | Memory per Worker | Total Memory (worst case) |
|---|---|---|
| 1 | 300 MB | 300 MB |
| 4 | 300 MB | 1.2 GB |
| 16 | 300 MB | 4.8 GB |
| 64 | 300 MB | 19.2 GB |

**Inference:** Memory is unlikely to be a bottleneck. Even 64 workers on a single machine fit within 32 GB RAM.

---

## 3. Shared Resource Management

While jobs are independent, they share three resources that need management:

| Resource | Management Strategy |
|---|---|
| **Output directory** | Each job writes to a unique path. Directory creation is atomic (mkdir + lock). |
| **Random number generators** | Each job has its own seeded RNG. No shared RNG state. |
| **Logging** | Workers log to their own per-process log files. The aggregator merges sorted logs post-execution. |

---

## 4. GPU Acceleration Assessment

| Stage | GPU Suitable? | Rationale |
|---|---|---|
| Geometry (rasterizer, process model) | ❌ No | CPU-bound; polygon rasterization, height field operations are memory-bandwidth bound on CPU |
| LER generation | ❌ No | Small convolution kernels; CPU is sufficient |
| Signal generation (per-pixel yield) | ⚠️ Partial | Per-pixel operations are embarrassingly parallel but memory-bound |
| PSF convolution | ✅ Yes | 2D convolution is GPU-amenable |
| Image formation | ❌ No | Trivial arithmetic; CPU overhead is negligible |

**Engineering Decision:** GPU is **not required** for the initial implementation. PSF convolution (the only GPU-amenable stage) runs in < 50 ms on CPU. GPU acceleration would be a Phase D optimization.

---

## 5. Scalability Bottlenecks

| Bottleneck | Likelihood | Mitigation |
|---|---|---|
| **Disk I/O** (many concurrent writes) | Low–Medium | Dedicated output thread/process; buffered writes |
| **Memory** (large images, many workers) | Low | Already bounded at 300 MB per worker |
| **Process startup overhead** | Low | Reuse worker processes (pool) rather than fork per job |
| **File system metadata** (millions of files) | Medium for >10⁵ images | Group files into subdirectories; use HDF5 for extremely large datasets |

---

## Sources

- [R1] I. Foster, *Designing and Building Parallel Programs*, Addison-Wesley, 1995.
- [R3] B. Wilkinson, M. Allen, *Parallel Programming*, 2nd ed. Prentice Hall, 2005.
- [R4] M. J. Quinn, *Parallel Programming in C with MPI and OpenMP*, McGraw-Hill, 2003.
- [R6] J. L. Hennessy, D. A. Patterson, *Computer Architecture: A Quantitative Approach*, 6th ed. Morgan Kaufmann, 2017.
- Phase 4.2 — Interface contracts.
