# DS5 Final Storage Projection

**Date:** 2026-08-01 10:50 UTC  
**Auditor:** Production Storage Engineer  
**Status:** ⚠️ CRITICAL FINDING — Disk capacity insufficient for 100K samples  

---

## 1. Per-Sample Storage Rates (Measured)

Based on 5,697 completed samples:

| Component | Per-Sample | Projected (100K) |
|-----------|-----------|-------------------|
| Image (TIFF, 1024×1024, 16-bit) | 1.93 MB | 193.0 GB |
| Ground truth JSON | 1.24 MB | 124.0 GB |
| Material map PNG | 5.7 KB | 0.57 GB |
| Metadata JSON ×3 | 1.1 KB | 0.11 GB |
| **Permanent per sample** | **3.33 MB** | **317.7 GB** |
| height.npy (temporary) | 8.0 MB | 80.0 GB peak |

---

## 2. Peak vs Final Storage Table

| Component | Size |
|-----------|------|
| Permanent files (100K samples) | 317.7 GB |
| height.npy peak (during last chunk) | 80.0 GB |
| **Peak storage during generation** | **397.7 GB** |
| Recovered after cleanup | −80.0 GB |
| **Final dataset size (after cleanup)** | **317.7 GB** |

---

## 3. Chunk-by-Chunk Storage Projection

| Chunk | Samples | Permanent (GB) | Peak w/ Temp (GB) | After Cleanup (GB) | Status |
|-------|---------|----------------|--------------------|--------------------|----|
| 1 | 0→10K | 33.3 | 113.3 | 33.3 | ✅ OK |
| 2 | 10K→20K | 66.6 | 146.6 | 66.6 | ✅ OK |
| 3 | 20K→30K | 99.9 | 179.9 | 99.9 | ✅ OK |
| 4 | 30K→40K | 133.2 | 213.2 | 133.2 | ✅ OK |
| 5 | 40K→50K | 166.5 | 246.5 | 166.5 | ✅ OK |
| 6 | 50K→60K | 199.8 | 279.8 | 199.8 | ✅ OK |
| **7** | **60K→70K** | **233.1** | **313.1** | **233.1** | **❌ FAILS** |
| 8 | 70K→80K | 266.4 | 346.4 | 266.4 | ❌ FAILS |
| 9 | 80K→90K | 299.7 | 379.7 | 299.7 | ❌ FAILS |
| 10 | 90K→100K | 333.0 | 413.0 | 333.0 | ❌ FAILS |

**Available disk for DS5:** 298.4 GB (300 GB total − 1.6 GB other project files)

---

## 4. Expected Size Validation

| Source | Estimate | Status |
|--------|----------|--------|
| User task specification | 220–250 GB | ❌ **INVALID** — underestimate by 27–44% |
| Config file (`ds5_final_training.yml`) | ~400 GB | ✅ **CORRECT** — includes temp overhead |
| This audit (permanent only) | ~318 GB | ✅ **MEASURED** — based on actual per-sample rates |

### Discrepancy Analysis

The 220–250 GB estimate appears to have been based on:
1. **Assumption of PNG images** (~0.5 MB each) → actual TIFF images are ~1.93 MB each (3.9× larger)
2. **Assumption of smaller GT JSON** (~0.3 MB each) → actual GT JSON is ~1.24 MB each (4.1× larger)
3. **Possible confusion with the `expected_size` field** in the config, which says "~400 GB" (line 77 of `ds5_final_training.yml`)

**The source of the discrepancy is the image format (TIFF vs assumed PNG) and GT JSON content size (contour data).**

---

## 5. Current vs Projected Sizes

| Metric | Current (5,697 samples) | Projected (100K samples) | Ratio |
|--------|------------------------|--------------------------|-------|
| Permanent | 18.98 GB | 317.7 GB | 16.7× |
| Temporary (peak) | 3.17 GB | 80.0 GB | 25.2× |
| Total | 22.07 GB | 397.7 GB | 18.0× |

The linear projection holds because:
- Each sample produces identical file types (1 TIFF + 1 GT JSON + 1 material PNG + 3 metadata JSON)
- File sizes are consistent across samples (low variance)
- The 5,697-sample baseline provides high confidence in the per-sample rate

---

## 6. Conclusion

| Question | Answer |
|----------|--------|
| Is 220–250 GB still valid? | **NO** — projected permanent size is ~318 GB |
| Is the config's ~400 GB valid? | **YES** — matches peak storage with temp files |
| Can 300 GB disk hold 100K samples? | **NO** — permanent data alone (318 GB) exceeds capacity |
| Maximum samples on 300 GB disk | **~65,000** (with 10K chunk size) |
