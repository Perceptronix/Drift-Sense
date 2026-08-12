# DS5 Disk Safety Report

**Date:** 2026-08-01 10:50 UTC  
**Auditor:** Production Storage Engineer  
**Status:** ⛔ DISK EXHAUSTION PREDICTED — Action required  

---

## 1. Current Disk State

| Metric | Value |
|--------|-------|
| Total capacity (E: drive) | 300.00 GB |
| Currently used | 23.68 GB |
| Currently free | 276.32 GB |
| DS5 dataset size | 22.07 GB |
| Other project files | ~1.61 GB |
| Available for DS5 growth | 276.32 GB |

---

## 2. Disk Exhaustion Analysis

### 2.1 Storage Budget

| Item | GB |
|------|-----|
| Disk capacity | 300.00 |
| Less: other project files | −1.61 |
| **Available for DS5** | **298.39** |
| Current DS5 permanent | −18.98 |
| **Remaining for permanent growth** | **279.41** |

### 2.2 Growth Rate

- Permanent data per sample: **3.33 MB**
- Samples fitting in remaining space: 279.41 GB / 3.33 MB = **83,906 samples**
- Total samples at capacity: 5,697 + 83,906 = **89,603 samples**

### 2.3 Chunk-Level Analysis

During each chunk, temporary height.npy files accumulate (up to 10K × 8 MB = 80 GB) before post-chunk cleanup. The peak storage occurs at the end of each chunk, just before cleanup.

**Available disk for DS5:** 298.39 GB

| Chunk | Start Samples | End Samples | Permanent (GB) | Peak w/ Temp (GB) | Fits? |
|-------|--------------|-------------|----------------|--------------------|----|
| 1 | 0 | 10,000 | 33.3 | 113.3 | ✅ Yes |
| 2 | 10,000 | 20,000 | 66.6 | 146.6 | ✅ Yes |
| 3 | 20,000 | 30,000 | 99.9 | 179.9 | ✅ Yes |
| 4 | 30,000 | 40,000 | 133.2 | 213.2 | ✅ Yes |
| 5 | 40,000 | 50,000 | 166.5 | 246.5 | ✅ Yes |
| 6 | 50,000 | 60,000 | 199.8 | 279.8 | ✅ Yes (marginal) |
| **7** | **60,000** | **70,000** | **233.1** | **313.1** | **⛔ NO** |

### 2.4 Exact Failure Point

At the start of chunk 7:
- Permanent data: 199.8 GB
- Free space: 298.39 − 199.8 = **98.59 GB**
- Per-sample cost during chunk: 3.33 MB (permanent) + 8 MB (temp) = **11.33 MB**
- Samples before disk fills: 98.59 GB / 11.33 MB ≈ **8,700 samples**
- **Disk exhaustion at sample ~68,700**

---

## 3. Storage Recovery After Cleanup

After each chunk completes, height.npy files are deleted:

| After Chunk | Permanent (GB) | Freed by Cleanup (GB) | Free Space (GB) |
|-------------|----------------|----------------------|-----------------|
| 1 | 33.3 | 80.0 | 265.1 |
| 2 | 66.6 | 80.0 | 231.8 |
| 3 | 99.9 | 80.0 | 198.5 |
| 4 | 133.2 | 80.0 | 165.2 |
| 5 | 166.5 | 80.0 | 131.9 |
| 6 | 199.8 | 80.0 | 98.6 |
| **7** | **233.1** | **N/A — disk full during chunk** | **0** |

---

## 4. Maximum Safe Dataset Size

### 4.1 With Current Chunk Size (10,000)

The last chunk must fit: permanent data + 80 GB temp peak

```
3.33 MB × (N − 10,000) + 80 GB ≤ 298.39 GB
3.33 MB × (N − 10,000) ≤ 218.39 GB
N − 10,000 ≤ 65,583
N ≤ 75,583
```

**Maximum safe: ~75,000 samples**

### 4.2 With Reduced Chunk Size

| Chunk Size | Peak Temp (GB) | Max Safe Samples |
|-----------|----------------|-----------------|
| 10,000 | 80 | ~75,000 |
| 5,000 | 40 | ~82,000 |
| 2,000 | 16 | ~86,000 |
| 1,000 | 8 | ~88,000 |
| 500 | 4 | ~89,000 |

Even with the smallest practical chunk size, **~89,000 samples is the hard limit** on a 300 GB disk.

### 4.3 Fundamental Constraint

The permanent data alone (3.33 MB × 100,000 = 317.7 GB) exceeds the disk capacity (298.39 GB available). **No amount of chunking or cleanup can make 100K samples fit on this disk.**

---

## 5. Risk Assessment

| Risk | Severity | Likelihood | Impact |
|------|----------|------------|--------|
| Disk exhaustion during chunk 7 | 🔴 CRITICAL | CERTAIN (if no change) | Generation aborts, potential checkpoint corruption |
| height.npy not cleaned up | 🟢 LOW | LOW | Cleanup code verified, triggers automatically |
| Orphaned .tmp files | 🟢 LOW | LOW | No .tmp files currently exist |
| Checkpoint file corruption | 🟡 MEDIUM | LOW | Atomic writes (tmp+replace) protect against this |

---

## 6. Recommendations

### Minimum Safe Operational Change (No Scientific Modification)

**Option A — Reduce dataset size (RECOMMENDED):**
- Set `--total 75000` instead of 100,000
- This fits comfortably on 300 GB with margin for temp files
- No change to image format, resolution, physics, or ground truth
- Permanent data: 249.8 GB, peak: 329.8 GB

**Option B — Reduce chunk size:**
- Change `CHUNK_SIZE` from 10,000 to 5,000
- Allows up to ~82,000 samples before disk fills
- Still falls short of 100K

**Option C — Use a larger disk:**
- Mount or attach a disk with ≥350 GB capacity
- No code changes needed
- 100K samples would fit with ~30 GB margin

**Option D — Compress images (format change):**
- Save as PNG instead of TIFF in the writer
- Would reduce per-sample from ~3.33 MB to ~1.5 MB
- 100K samples: ~150 GB — fits easily
- ⚠️ Changes the output format (not scientific content, but dataset format)

### Recommended Action

**Combine Options A and B for immediate safety:**
1. Reduce `--total` to 75,000 (fits on 300 GB)
2. Reduce `CHUNK_SIZE` to 5,000 (more frequent cleanup, more margin)
3. Plan for a larger disk if 100K samples are required

---

## 7. Current Generator Status

The generator is currently running and has completed 5,697 samples. At this rate:
- **No immediate danger** — plenty of free space (276 GB)
- Disk will fill around sample 68,700 (chunk 7)
- **Recommend pausing and reconfiguring before reaching chunk 7**

The generator can be safely paused at any chunk boundary. The checkpoint system ensures no work is lost.
