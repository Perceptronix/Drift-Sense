# DS5 Production Pipeline - Performance Audit

**Date:** 2026-07-31
**Scope:** Static code analysis of the entire DS5 generation pipeline
**Baseline:** 50 samples in 194.5s wall-clock (4 workers) = 15.56s single-core equivalent per sample
**Target:** 100,000 samples at 1024x1024 16-bit

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Pipeline Architecture Overview](#2-pipeline-architecture-overview)
3. [Bottleneck Analysis](#3-bottleneck-analysis)
4. [Detailed Findings](#4-detailed-findings)
5. [Worker Utilization Analysis](#5-worker-utilization-analysis)
6. [Memory Analysis](#6-memory-analysis)
7. [Optimization Roadmap](#7-optimization-roadmap)

---

## 1. Executive Summary

The DS5 pipeline generates 100,000 synthetic SEM images through a 10-stage physics simulation. The current implementation achieves **15.4 samples/min** with 4 parallel workers. At this rate, the full dataset requires approximately **10.8 hours** of wall-clock time.

The audit identified **16 bottlenecks** across three categories: I/O overhead (dominant), compute inefficiency, and parallelization underutilization. The two highest-impact findings are:

1. **Redundant SHA-256 computation** - every sample's files are hashed twice (once at write, once at finalization), wasting ~10-15% of I/O time.
2. **Worker count ceiling** - the CPU has 10 cores / 16 threads but the pipeline uses only 4 workers, leaving 60-75% of compute capacity idle.

Combined safe optimizations could reduce wall-clock time from **~10.8 hours to ~3.5-5 hours** (2-3x speedup) without modifying any scientific model, equation, random number generation, numerical precision, or output.

---

## 2. Pipeline Architecture Overview

### 2.1 Call Chain

```
run_ds5_production.py (DG4 orchestrator)
  |
  +-- subprocess.run() -> generate_ds5_final.py
  |     |
  |     +-- ProcessPoolExecutor(max_workers=4)
  |           |
  |           +-- _worker_init(): loads GDS library + config defaults (once per worker)
  |           +-- _generate_sample(): per-sample pipeline
  |                 |
  |                 +-- load_config() + _apply_overrides() + validate()  [per-sample]
  |                 +-- run_pipeline():
  |                 |     S1: raster.rasterize()         -> MaskSet
  |                 |     S2: process.build_geometry()    -> h_det, mat_det
  |                 |     S3: variability.apply()         -> h_var, mat_var
  |                 |     S4: signal.compute_yields()     -> YieldMaps
  |                 |     S5: degrade.degrade_yields()    -> se_degraded
  |                 |     S6: formation.form_image()      -> SEMImage
  |                 |     S7: build_ground_truth()        -> GroundTruth
  |                 |     S8: _assemble_metadata()        -> dict
  |                 |     S9: write_sample()              -> disk artifacts
  |                 |
  |                 +-- return result dict (pickled to parent)
  |
  +-- Checkpoint.save() every 500 samples
  +-- SHA256SUMS over all files (post-generation)
```

### 2.2 Per-Sample Disk Artifacts

| File | Format | Size (approx) | Write Method |
|------|--------|---------------|--------------|
| `{idx:06d}.tiff` | TIFF LZW | ~500KB-1.5MB | Pillow `save(compression="tiff_lzw")` |
| `{idx:06d}_gt.json` | JSON (indented) | ~2-5KB | Atomic write (tmp + rename) |
| `{idx:06d}_height.npy` | NumPy .npy | ~8.3MB | `np.save()` |
| `{idx:06d}_material.png` | PNG lossless | ~200-500KB | Pillow `save(compress_level=6)` |
| `{idx:06d}_config.json` | JSON (indented) | ~1-2KB | Atomic write (tmp + rename) |
| `{idx:06d}_metadata.json` | JSON (indented) | ~1-3KB | Atomic write (tmp + rename) |
| `{idx:06d}_timing.json` | JSON (indented) | ~0.2KB | Atomic write (tmp + rename) |

**Per-sample total I/O:** ~10-11MB written, ~7 files created (each with atomic tmp+rename)

### 2.3 Observed Performance (50-sample run)

- Wall-clock: 194.5s with 4 workers
- Per-sample wall-clock: 3.89s
- Single-core equivalent: 15.56s per sample
- Throughput: 15.4 samples/min
- Estimated full-run wall-clock: ~10.8 hours
- 0 failures across all 50 samples

---

## 3. Bottleneck Analysis

### 3.1 Bottleneck Distribution (Estimated per-sample time breakdown)

| Category | Est. % of Single-Core Time | Est. Time (s) |
|----------|---------------------------|---------------|
| S9: Disk I/O (TIFF, PNG, NPY, JSON) | 20-25% | 3.1-3.9s |
| SHA-256 computation (per-sample) | 10-15% | 1.6-2.3s |
| S5: Degrade (FFT blur + noise) | 12-18% | 1.9-2.8s |
| S3: Variability (random fields + warp) | 10-15% | 1.6-2.3s |
| S4: Signal (yield computation + EDT) | 8-12% | 1.2-1.9s |
| Config load + validate (per-sample) | 5-8% | 0.8-1.2s |
| S2: Process (recipes + copies) | 5-8% | 0.8-1.2s |
| S1: Rasterize (polygon rasterization) | 3-5% | 0.5-0.8s |
| S7: Ground truth (contour finding) | 3-5% | 0.5-0.8s |
| S8: Metadata assembly | 2-3% | 0.3-0.5s |
| Checkpoint serialization | 2-5% | 0.3-0.8s |
| Multiprocessing overhead (pickle) | 3-5% | 0.5-0.8s |

---

## 4. Detailed Findings

### Finding 1: Redundant SHA-256 Computation

| Attribute | Value |
|-----------|-------|
| **File** | `simulator/src/semicon/dataset/writer.py:21-26, 85` |
| **Function** | `_sha256()`, called from `write_sample()` line 85 |
| **Runtime %** | 10-15% of per-sample time |
| **Why slow** | `_sha256()` reads every artifact file in 1MB chunks and computes SHA-256. It is called for all 7 files per sample (line 85 dict comprehension), requiring a full read-back of every file just written. This means each TIFF (~1MB), NPY (~8MB), PNG (~300KB), and JSON files are read from disk a second time purely for checksumming. |
| **Safe optimization** | Defer SHA-256 computation to the finalization pass (`finalize_dataset`), which already walks all files and computes SHA-256SUMS. Remove the per-sample `_sha256()` call from `write_sample()`. Alternatively, compute hashes incrementally during the write (hash the data buffer before writing to disk) to avoid the read-back. |
| **Expected speedup** | 10-15% reduction in per-sample time (~1.5-2.3s saved per sample). Over 100K samples: ~42-64 minutes saved. |
| **Risk level** | LOW - SHA-256 is only used for integrity verification. The finalization pass already provides full coverage. Removing per-sample hashing does not change any output. |
| **Bit-identical output** | YES - TIFF, PNG, NPY, and JSON contents are unchanged. Only the per-sample `artifacts` dict entries are omitted (still computed at finalization). |

---

### Finding 2: Worker Count Underutilization

| Attribute | Value |
|-----------|-------|
| **File** | `validation/generate_ds5_final.py:94` (MAX_WORKERS=4) |
| **Function** | `ProcessPoolExecutor(max_workers=max_workers)` line 563 |
| **Runtime %** | N/A (structural) |
| **Why slow** | The CPU has 10 physical cores / 16 threads. With only 4 workers, 60-75% of compute capacity is idle. The per-sample pipeline is CPU-bound (NumPy/SciPy operations dominate) with minimal inter-worker communication, so scaling to 8-12 workers should be near-linear. |
| **Safe optimization** | Increase `MAX_WORKERS` to 8 (conservative) or 12 (aggressive). Monitor memory usage (each worker uses ~200-400MB peak). On a 16-thread CPU, 8 workers ensures each core has work while leaving headroom for the OS and I/O threads. |
| **Expected speedup** | 1.5-2x wall-clock reduction (8 workers) or 2-2.5x (12 workers). From ~10.8h to ~5.4h (8W) or ~4.3h (12W). |
| **Risk level** | LOW - `ProcessPoolExecutor` with `initializer` already handles worker lifecycle. Each sample is independent. Memory is the only constraint (8 workers x ~400MB = ~3.2GB). |
| **Bit-identical output** | YES - worker count does not affect deterministic outputs (each sample uses its own `SeedManager` derived from master seed). |

---

### Finding 3: Per-Sample Config Reload

| Attribute | Value |
|-----------|-------|
| **File** | `validation/generate_ds5_final.py:257-260` |
| **Function** | `_generate_sample()` |
| **Runtime %** | 5-8% |
| **Why slow** | Every call to `_generate_sample()` loads the defaults YAML from disk (`load_config(None, defaults_path=...)`), performs deep-merge, applies overrides, and validates. The base config never changes between samples -- only the overrides differ. YAML parsing and `copy.deepcopy()` in `_deep_merge` are repeated unnecessarily 100K times. |
| **Safe optimization** | In `_worker_init()`, load and parse the base config once. In `_generate_sample()`, use the cached base config dict and only apply overrides + validate. This eliminates 100K YAML reads and 100K deep-merges. |
| **Expected speedup** | 5-8% (~0.8-1.2s per sample, ~13-20 minutes total). |
| **Risk level** | LOW - config is immutable within a worker. The base config is loaded once per worker in `_worker_init()` already for the library; extending it to include the parsed config dict is trivial. |
| **Bit-identical output** | YES - config values are identical; only the loading path changes. |

---

### Finding 4: Library Checksum Recomputation

| Attribute | Value |
|-----------|-------|
| **File** | `simulator/src/semicon/orchestration/pipeline.py:196` |
| **Function** | `_assemble_metadata()` |
| **Runtime %** | 1-2% |
| **Why slow** | `library_checksum()` is called inside `_assemble_metadata()` for every sample. This function computes SHA-256 of the material library, which is constant across all samples. The library is loaded once per worker but the checksum is recomputed per sample. |
| **Safe optimization** | Compute `library_checksum()` once in `_worker_init()` and store it in the worker-global context. Pass it to `_assemble_metadata()` as a parameter. |
| **Expected speedup** | 1-2% (~0.2-0.3s per sample). |
| **Risk level** | LOW - material library does not change within a worker. |
| **Bit-identical output** | YES - checksum value is identical. |

---

### Finding 5: TIFF LZW Compression Overhead

| Attribute | Value |
|-----------|-------|
| **File** | `simulator/src/semicon/foundation/image_io.py:16-22` |
| **Function** | `save_tiff()` |
| **Runtime %** | 8-12% |
| **Why slow** | `Pillow.save(compression="tiff_lzw")` performs LZW compression on a 1024x1024 uint16 image (~2MB uncompressed). LZW is CPU-intensive for 16-bit scientific images with continuous gradients (typical SEM content). The compression ratio is modest for SEM images (typically 1.5-2.5x), but the encoding cost is significant. |
| **Safe optimization** | Option A: Use `compression="tiff_adobe_deflate"` (zlib/DEFLATE) which is often faster for scientific images and achieves similar ratios. Option B: Use `compression="tiff_lzw", compress_level=1` (fastest LZW level). Option C: Write uncompressed TIFF (fastest, larger files). All produce valid TIFF files readable by standard tools. Note: this changes file hashes but not image pixel data. |
| **Expected speedup** | 5-10% reduction in per-sample time (~0.8-1.5s saved per sample). |
| **Risk level** | LOW-MEDIUM - changes file bytes (hash changes) but not pixel values. If downstream consumers depend on LZW specifically, this could cause issues. DEFLATE is widely supported. |
| **Bit-identical output** | PIXEL-IDENTICAL YES, FILE-IDENTICAL NO (different compression produces different bytes). |

---

### Finding 6: Degradation Pipeline Memory Copies

| Attribute | Value |
|-----------|-------|
| **File** | `simulator/src/semicon/physics/_degrade/noise_models.py:32-61` |
| **Function** | `degrade_signal()` |
| **Runtime %** | 3-5% (memory allocation overhead within the 12-18% S5 time) |
| **Why slow** | `degrade_signal()` creates 6-7 intermediate full-image arrays (1024x1024 float64 = 8MB each): padded array, FFT result, shot noise `means`, Poisson `counts` (int64), division result, Gaussian noise array, addition result, and clip result. Each allocation triggers Python memory manager + OS page allocation. |
| **Safe optimization** | Reuse a pre-allocated scratch buffer across the chain. For example, allocate one `blurred` array and mutate it in-place through each stage: `np.maximum(signal * cpe, 0.0, out=blurred)` then reuse for Poisson output. Note: `generator.poisson()` and `generator.normal()` cannot write in-place (they allocate internally), but the surrounding operations can be chained to reduce temporaries. |
| **Expected speedup** | 2-4% of S5 time (~0.5-1s per sample). |
| **Risk level** | LOW - in-place operations preserve mathematical equivalence. Poisson/Normal RNG outputs are inherently the same regardless of buffer reuse. |
| **Bit-identical output** | YES - numerical results are identical (same RNG seeds, same operations). |

---

### Finding 7: Variability Applier Array Copies

| Attribute | Value |
|-----------|-------|
| **File** | `simulator/src/semicon/geometry/_variability/variability_applier.py:68-69` |
| **Function** | `apply_variability()` |
| **Runtime %** | 2-3% (within the 10-15% S3 time) |
| **Why slow** | Lines 68-69 copy both `height_field.data` and `material_map.data` at entry, creating two full MxN arrays (8MB float64 + 1MB uint8 = 9MB). These copies are needed because `map_coordinates` modifies the arrays, but the originals are also needed for gradient computation. However, the gradient is computed on `H` (the copy) anyway, so the original `height_field.data` copy could be eliminated if gradient is computed before warping. |
| **Safe optimization** | Compute the gradient fields first (which only read `H`), then warp `H` in-place. This eliminates one 8MB allocation. For `material_map`, the copy is necessary (integer interpolation requires a new array). |
| **Expected speedup** | 1-2% (~0.2-0.4s per sample). |
| **Risk level** | LOW - gradient computation reads H but does not modify it. Warp modifies H but gradient is already computed. |
| **Bit-identical output** | YES - same computation order, same values. |

---

### Finding 8: Process Simulator Redundant Copies

| Attribute | Value |
|-----------|-------|
| **File** | `simulator/src/semicon/geometry/_process/process_simulator.py:106-110` |
| **Function** | `height_field()`, `material_map()` |
| **Runtime %** | 2-3% (within S2 time) |
| **Why slow** | `height_field()` returns `HeightField(self.H.copy())` and `material_map()` returns `MaterialMap(self.mat.copy())`. These are defensive copies to prevent external mutation. Additionally, `etch()` at line 67 creates `top = self.H.copy()` for the sidewall angle computation. The `corner_round()` creates a `median_filter` output array. Total: 3-4 full MxN copies per recipe step. |
| **Safe optimization** | Use `np.array(self.H, copy=False)` with `readonly` flag instead of `.copy()` in the output methods. For `etch()`, compute the distance transform on the mask (not a copy of H) -- the current approach copies H to compute the top surface, but this could use a view if the etch pattern is applied differently. |
| **Expected speedup** | 1-2% (~0.2-0.3s per sample). |
| **Risk level** | LOW-MEDIUM - removing copies requires ensuring no external code mutates the returned arrays. Given the frozen dataclass pattern in datatypes.py, this is likely safe but requires careful verification. |
| **Bit-identical output** | YES - same values, fewer copies. |

---

### Finding 9: Checkpoint Serialization Overhead

| Attribute | Value |
|-----------|-------|
| **File** | `validation/generate_ds5_final.py:119-163` |
| **Function** | `Checkpoint.save()`, `Checkpoint.load()`, `Checkpoint.completed_set` |
| **Runtime %** | 2-5% (grows with dataset size) |
| **Why slow** | The `completed` list grows to 100K integers. `completed_set` (line 162-163) creates a new `set` from this list every time it is accessed -- and it is accessed in every batch completion check, every coverage verification, and every integrity check. `save()` serializes the full 100K list to JSON (~1MB). `load()` deserializes it back. The list-vs-set design means O(n) membership testing where O(1) is needed. |
| **Safe optimization** | Maintain `completed` as a `set` internally and only convert to `list` for JSON serialization. Or store as a sorted list and use `bisect` for O(log n) membership testing. Also, `completed_set` property should cache the set. |
| **Expected speedup** | 1-3% early, growing to 3-5% near completion (~0.3-0.8s per batch of 500). |
| **Risk level** | LOW - internal data structure change, no output impact. |
| **Bit-identical output** | YES - checkpoint content is semantically identical. |

---

### Finding 10: Ground Truth Contour Finding (skimage)

| Attribute | Value |
|-----------|-------|
| **File** | `simulator/src/semicon/dataset/groundtruth.py:81-83` |
| **Function** | `_contours_from_edges()` using `skimage.measure.find_contours()` |
| **Runtime %** | 3-5% |
| **Why slow** | `skimage.measure.find_contours()` uses a pure-Python marching squares implementation. For a 1024x1024 edge map, this traces iso-valued contours through the full image. The function is well-optimized in C for the inner loop, but the Python-level contour tracing and list management add overhead. |
| **Safe optimization** | The contours are only used for visualization/metadata -- they do not affect the SEM image or core ground truth. If contour precision can tolerate minor differences, `skimage.measure.find_contours()` could be replaced with a vectorized marching squares or the contours could be downsampled (e.g., every 4th pixel) before tracing. However, this changes contour coordinates. |
| **Expected speedup** | 2-4% (~0.3-0.6s per sample). |
| **Risk level** | MEDIUM - changes contour coordinates. If downstream consumers require exact contour positions, this is not safe. If contours are for visualization only, the risk is low. |
| **Bit-identical output** | NO - contour coordinates may differ. |

---

### Finding 11: Polygon Rasterizer Supersampling Loop

| Attribute | Value |
|-----------|-------|
| **File** | `simulator/src/semicon/geometry/_raster/polygon_rasterizer.py:85-86` |
| **Function** | `rasterize_polygon()` supersampling path |
| **Runtime %** | 1-2% (within S1 time) |
| **Why slow** | The supersampling path iterates `ss x ss` times (default `ss=4` = 16 iterations), each creating a full MxN meshgrid and running point-in-polygon. For simple axis-aligned rectangles (fast path, line 63), this is bypassed. But for non-rectangular polygons (via, bimaterial), all16 sub-pixel evaluations are performed. |
| **Safe optimization** | The `point_in_polygon` inner loop (line 25) uses Python-level iteration over polygon edges. This could be vectorized using the shoelace formula or by pre-computing edge arrays. Also, the 16 meshgrid evaluations could be batched into a single 3D array operation. |
| **Expected speedup** | 1-2% (~0.2-0.3s per sample, only for non-rectangular structures). |
| **Risk level** | LOW - rasterization result is binary (pixel inside/outside), so vectorization preserves the output. |
| **Bit-identical output** | YES for fast path. MAY DIFFER for general path due to floating-point ordering in vectorized operations (within numerical tolerance). |

---

### Finding 12: Signal Assembler Intermediate Allocations

| Attribute | Value |
|-----------|-------|
| **File** | `simulator/src/semicon/physics/_signal/signal_assembler.py:55-78` |
| **Function** | `assemble_signal()` |
| **Runtime %** | 2-3% (within S4 time) |
| **Why slow** | Each step allocates a new full-image array: `se = se1 + se2` (line 55), `se = apply_edge_effects(se, ...)` (line 61, returns new array), `se = apply_charging(se, ...)` (line 70, returns new array), `se = np.clip(se, ...)` (line 78, returns new array). Total: 4 intermediate allocations of 8MB each (32MB). |
| **Safe optimization** | Use in-place operations where possible: `se += se2` instead of `se = se1 + se2`. For `apply_edge_effects` and `apply_charging`, the functions return new arrays by design (they create ramps/fields). The clip could use `np.clip(se, 0, MAX, out=se)` for in-place. |
| **Expected speedup** | 1-2% (~0.2-0.3s per sample). |
| **Risk level** | LOW - in-place `+=` is numerically equivalent for float64 addition. In-place clip is also equivalent. |
| **Bit-identical output** | YES - floating-point addition is commutative and associative within the same precision. |

---

### Finding 13: Multiprocessing Serialization Overhead

| Attribute | Value |
|-----------|-------|
| **File** | `validation/generate_ds5_final.py:568-587` |
| **Function** | `ProcessPoolExecutor` future result collection |
| **Runtime %** | 3-5% |
| **Why slow** | Each `_generate_sample()` call returns a dict containing `artifacts` (7-entry dict of SHA-256 strings), `timing` (10-entry dict of floats), and status strings. These are serialized via `pickle` across the process boundary. For 500 samples per batch, this is 500 pickled dicts. More significantly, the `result.artifacts` dict contains SHA-256 hashes that could be deferred. |
| **Safe optimization** | Minimize the data returned from workers. Return only `sample_index`, `status`, `structure_type`, and `timing` (small dicts). Defer SHA-256 computation to finalization. This reduces pickle payload by ~60%. |
| **Expected speedup** | 1-2% (~0.2-0.3s per sample). |
| **Risk level** | LOW - the artifacts dict is only used for reporting, not for scientific output. |
| **Bit-identical output** | YES - output files are unchanged. Only the inter-process data transfer is reduced. |

---

### Finding 14: Atomic Write Overhead for Small JSON Files

| Attribute | Value |
|-----------|-------|
| **File** | `simulator/src/semicon/dataset/writer.py:29-33` |
| **Function** | `_atomic_write_text()` |
| **Runtime %** | 2-3% |
| **Why slow** | Each of the 4 JSON files per sample uses atomic write (create `.tmp`, write, `os.replace`). For files under 5KB, the filesystem metadata operations (create, truncate, rename) dominate the actual write time. With 4 files x 100K samples = 400K atomic write operations, the overhead is non-trivial. |
| **Safe optimization** | For small JSON files (<10KB) that are only written once and never concurrently read, direct `write_text()` is safe (the atomic pattern protects against concurrent readers, which does not apply to per-sample writes). Alternatively, batch all 4 JSON files into a single multi-document JSON file. |
| **Expected speedup** | 1-2% (~0.2-0.3s per sample). |
| **Risk level** | LOW - files are written once and read later. No concurrent access during generation. |
| **Bit-identical output** | YES - JSON content is identical. |

---

### Finding 15: Edge Effects Distance Transform

| Attribute | Value |
|-----------|-------|
| **File** | `simulator/src/semicon/physics/_signal/edge_effects.py:43` |
| **Function** | `apply_edge_effects()` |
| **Runtime %** | 3-5% (within S4 time) |
| **Why slow** | `ndimage.distance_transform_edt(1 - edges)` computes the Euclidean distance transform of the binary edge mask. For a 1024x1024 image, this is an O(N*M) algorithm with internal allocation of float64 distance arrays. The `1 - edges` creates a temporary uint8 array. The EDT is invoked for every sample even when edge effects are disabled (the guard at line 40 checks `edges.any()` but the EDT runs after the check). |
| **Safe optimization** | The early exit at line 40 (`if not edges.any(): return se_map`) already avoids the EDT when no edges exist. For patterns with edges, the EDT could use `scipy.ndimage.distance_transform_edt` with `sampling=` parameter to exploit the 1nm pixel size (already the case). No major optimization possible without changing the algorithm. |
| **Expected speedup** | 0-2% (already optimized with early exit). |
| **Risk level** | N/A - the operation is already guarded. |
| **Bit-identical output** | N/A. |

---

### Finding 16: Random Field FFT Allocations

| Attribute | Value |
|-----------|-------|
| **File** | `simulator/src/semicon/geometry/_variability/random_fields.py:19-57` |
| **Function** | `exponential_random_field()`, `gaussian_random_field()` |
| **Runtime %** | 3-5% (within S3 time) |
| **Why slow** | `exponential_random_field()` allocates 6 full MxN float64 arrays (`FY`, `FX`, `k`, `psd`, `phase`, `Z`) plus the IFFT complex result. `gaussian_random_field()` allocates 2 (white noise + filtered). For a 1024x1024 image, this is ~48MB of temporary allocations per field. LER and CDU each call one of these, totaling ~64-96MB of temporaries. |
| **Safe optimization** | Reuse the white noise array across both fields (allocate once, filter twice with different sigmas). Pre-compute the frequency grid (`FY`, `FX`, `k`) once per worker since the image shape never changes. Cache the frequency grid in the worker-global context. |
| **Expected speedup** | 1-2% (~0.2-0.3s per sample). |
| **Risk level** | LOW - frequency grid is deterministic given image shape. Reusing white noise with different filters produces independent fields. |
| **Bit-identical output** | YES - same RNG seeds produce same white noise, same filters produce same outputs. |

---

## 5. Worker Utilization Analysis

### 5.1 Current Configuration

| Parameter | Value |
|-----------|-------|
| CPU | 10 physical cores / 16 threads (Intel) |
| `MAX_WORKERS` (generate_ds5_final.py) | 4 |
| `WORKERS` (run_ds5_production.py) | 2 (defined but not passed to subprocess) |
| Actual workers used | 4 (default from generate_ds5_final.py) |
| CPU utilization | 25% (4/16 threads) |
| Idle capacity | 75% |

### 5.2 Scaling Projection

| Workers | Est. Wall-Clock (100K samples) | CPU Utilization | Memory (peak) |
|---------|-------------------------------|-----------------|---------------|
| 4 (current) | ~10.8 hours | 25% | ~1.6 GB |
| 8 | ~5.4 hours | 50% | ~3.2 GB |
| 12 | ~3.6 hours | 75% | ~4.8 GB |
| 16 | ~2.7 hours | 100% | ~6.4 GB |

### 5.3 Scaling Constraints

1. **Memory**: Each worker uses ~200-400MB peak (NumPy arrays + Python overhead). At 16 workers: ~3.2-6.4GB total. Well within typical 16-32GB system RAM.
2. **Disk I/O**: With 16 workers writing concurrently, disk write throughput becomes the bottleneck. An NVMe SSD sustains ~1-3 GB/s writes. At ~11MB per sample x 16 workers = ~176MB/batch, this is manageable. A SATA SSD (~500MB/s) may bottleneck at 12+ workers.
3. **GIL**: All heavy operations use NumPy/SciPy (C/Fortran, GIL-released). Worker processes bypass the GIL entirely via `multiprocessing`.
4. **Determinism**: Each worker uses a deterministic `SeedManager` derived from the master seed + sample index. Worker count does not affect determinism.

---

## 6. Memory Analysis

### 6.1 Per-Sample Peak Memory

| Stage | Peak Allocation | Lifetime |
|-------|----------------|----------|
| S1: Rasterize | MaskSet (layer_masks dict) | Until S2 completes |
| S2: Process | H (8MB) + mat (1MB) + copies | Until S3 completes |
| S3: Variability | H_var (8MB) + mat_var (1MB) + fields (~64MB) | Until S4 completes |
| S4: Signal | se + se1 + se2 + eta (~32MB) | Until S5 completes |
| S5: Degrade | blurred + intermediates (~64MB) | Until S6 completes |
| S6: Formation | image (2MB uint16) | Until S9 completes |
| S7: Ground truth | edge_map + contours (~10MB) | Until S9 completes |
| S9: Write | TIFF buffer (~2MB) | During write only |

**Peak memory per sample:** ~120-160MB (S3-S5 overlap)
**Peak memory per worker:** ~200-400MB (including Python overhead + import cache)
**Total with 4 workers:** ~800MB-1.6GB
**Total with 12 workers:** ~2.4-4.8GB

### 6.2 Memory Opportunities

The S3-S5 stages hold all intermediate arrays simultaneously within `run_pipeline()`. Early deallocation (explicit `del` of stage outputs after they are no longer needed) could reduce peak by ~30-40MB per sample, but the benefit is marginal compared to the engineering effort.

---

## 7. Optimization Roadmap

### 7.1 Priority Matrix

| # | Optimization | Speedup | Effort | Risk | Bit-Identical | Priority |
|---|-------------|---------|--------|------|---------------|----------|
| 1 | Increase workers to 8 | 2x wall-clock | trivial | LOW | YES | P0 |
| 2 | Defer per-sample SHA-256 | 10-15% | low | LOW | YES | P0 |
| 3 | Cache base config per worker | 5-8% | low | LOW | YES | P1 |
| 4 | Cache library checksum | 1-2% | trivial | LOW | YES | P1 |
| 5 | Reduce pickle payload | 1-2% | low | LOW | YES | P1 |
| 6 | Optimize TIFF compression | 5-10% | low | LOW-MED | PIXEL-YES | P1 |
| 7 | Checkpoint set optimization | 1-3% | low | LOW | YES | P2 |
| 8 | Variability array copy reduction | 1-2% | medium | LOW | YES | P2 |
| 9 | Process simulator copy reduction | 1-2% | medium | LOW-MED | YES | P2 |
| 10 | Degradation pipeline scratch reuse | 2-4% | medium | LOW | YES | P2 |
| 11 | Signal assembler in-place ops | 1-2% | medium | LOW | YES | P2 |
| 12 | Random field freq-grid caching | 1-2% | low | LOW | YES | P2 |
| 13 | Atomic write simplification | 1-2% | low | LOW | YES | P3 |
| 14 | Polygon rasterizer vectorization | 1-2% | high | LOW | MAYBE | P3 |
| 15 | Ground truth contour optimization | 2-4% | high | MEDIUM | NO | P3 |
| 16 | Edge effects (already optimized) | 0% | - | - | - | N/A |

### 7.2 Recommended Implementation Order

**Phase 1 (Quick wins, <1 day each):**
1. Increase `MAX_WORKERS` from 4 to 8 in `generate_ds5_final.py`
2. Remove per-sample SHA-256 from `write_sample()`, rely on finalization pass
3. Cache parsed base config in `_worker_init()` and reuse in `_generate_sample()`
4. Cache `library_checksum()` result in worker context

**Phase 2 (Medium effort, 1-2 days each):**
5. Reduce pickle payload (return minimal result dict from workers)
6. Switch TIFF compression from LZW to DEFLATE or reduce compression level
7. Optimize `Checkpoint` to use set internally
8. Cache frequency grids for random field generation in worker context

**Phase 3 (Higher effort, 2-5 days each):**
9. In-place operations in degradation pipeline and signal assembler
10. Eliminate redundant array copies in variability applier and process simulator
11. Batch JSON writes or remove atomic pattern for per-sample files

**Phase 4 (Optional, evaluate benefit first):**
12. Vectorize polygon rasterizer inner loop
13. Optimize ground truth contour finding

### 7.3 Combined Impact Projection

| Scenario | Workers | Per-Sample Time | Wall-Clock (100K) | Speedup |
|----------|---------|-----------------|-------------------|---------|
| Current | 4 | 15.56s (single-core) | ~10.8 hours | 1x |
| Phase 1 only | 8 | ~12s (after SHA-256 + config caching) | ~4.2 hours | 2.6x |
| Phase 1+2 | 8 | ~10s | ~3.5 hours | 3.1x |
| Phase 1+2+3 | 12 | ~9s | ~2.1 hours | 5.1x |

### 7.4 Risk Assessment Summary

- **Total optimizations proposed:** 16 (including 1 already optimized)
- **Bit-identical output guaranteed:** 12 of 16
- **Pixel-identical, file-different:** 1 (TIFF compression change)
- **May change auxiliary output:** 1 (contour coordinates)
- **Already optimal:** 1 (edge effects early exit)
- **Scientific risk:** ZERO - no equations, models, RNG, precision, or physics changes
- **Dataset structure risk:** ZERO - output schema, format, and splits unchanged

---

## Appendix A: Files Analyzed

| File | Lines | Role |
|------|-------|------|
| `validation/run_ds5_production.py` | 286 | DG4 orchestrator |
| `validation/generate_ds5_final.py` | 904 | Main generation script with multiprocessing |
| `simulator/generate.py` | 27 | CLI shim |
| `simulator/src/semicon/orchestration/pipeline.py` | 205 | 10-stage pipeline |
| `simulator/src/semicon/orchestration/job.py` | 156 | Sequential batch runner |
| `simulator/src/semicon/orchestration/cli.py` | 196 | CLI interface |
| `simulator/src/semicon/orchestration/config.py` | 130 | Config system |
| `simulator/src/semicon/dataset/writer.py` | 142 | Dataset writer |
| `simulator/src/semicon/dataset/groundtruth.py` | 143 | Ground truth generation |
| `simulator/src/semicon/dataset/splitter.py` | 35 | Train/val/test splitting |
| `simulator/src/semicon/foundation/image_io.py` | 40 | TIFF/PNG I/O |
| `simulator/src/semicon/foundation/rng_utils.py` | 63 | Seed management |
| `simulator/src/semicon/foundation/math_utils.py` | 109 | Math helpers |
| `simulator/src/semicon/foundation/datatypes.py` | 294 | Data objects |
| `simulator/src/semicon/geometry/raster.py` | 40 | Rasterization interface |
| `simulator/src/semicon/geometry/process.py` | 31 | Process interface |
| `simulator/src/semicon/geometry/variability.py` | 27 | Variability interface |
| `simulator/src/semicon/geometry/structures.py` | 196 | Structure library |
| `simulator/src/semicon/geometry/_raster/gdsii.py` | 297 | GDSII reader/writer |
| `simulator/src/semicon/geometry/_raster/mask_builder.py` | 76 | Mask builder |
| `simulator/src/semicon/geometry/_raster/polygon_rasterizer.py` | 109 | Polygon rasterizer |
| `simulator/src/semicon/geometry/_process/process_simulator.py` | 111 | Process simulator |
| `simulator/src/semicon/geometry/_process/recipes.py` | 121 | Process recipes |
| `simulator/src/semicon/geometry/_variability/random_fields.py` | 63 | Random field synthesis |
| `simulator/src/semicon/geometry/_variability/variability_applier.py` | 128 | Variability engine |
| `simulator/src/semicon/physics/signal.py` | 30 | Signal interface |
| `simulator/src/semicon/physics/formation.py` | 22 | Formation interface |
| `simulator/src/semicon/physics/degrade.py` | 28 | Degrade interface |
| `simulator/src/semicon/physics/_signal/topography_engine.py` | 23 | Topography computation |
| `simulator/src/semicon/physics/_signal/yield_computer.py` | 36 | Yield computation |
| `simulator/src/semicon/physics/_signal/edge_effects.py` | 47 | Edge effects |
| `simulator/src/semicon/physics/_signal/charging_engine.py` | 48 | Charging model |
| `simulator/src/semicon/physics/_signal/signal_assembler.py` | 93 | Signal assembly |
| `simulator/src/semicon/physics/_formation/image_former.py` | 51 | Image digitization |
| `simulator/src/semicon/physics/_degrade/psf_generator.py` | 32 | PSF generation + blur |
| `simulator/src/semicon/physics/_degrade/noise_models.py` | 62 | Shot + detector noise |
| `simulator/src/semicon/physics/_shared/material_properties.py` | 147 | Material library |

**Total lines analyzed:** ~4,800+ across 36 source files.

---

*This audit is based on static code analysis only. No profiling or benchmarking was performed. Runtime percentages are estimates based on algorithmic complexity analysis, known NumPy/SciPy operation costs, and the observed 50-sample baseline.*
