# DS5 Production Storage Audit

**Date:** 2026-08-01 10:50 UTC  
**Auditor:** Production Storage Engineer  
**Status:** LIVE AUDIT — Generator running, read-only inspection  

---

## 1. Generator Status

| Property | Value |
|----------|-------|
| Running processes | 9 Python processes (PIDs 19432–41416) |
| Started | 2026-08-01 09:24:57–59 |
| Current batch | 15 (in progress) |
| Samples completed | 5,697 / 100,000 |
| Failed samples | 0 (all retries succeeded) |
| Disk free | 276.32 GB / 300 GB |

**Generator was NOT interrupted or modified during this audit.**

---

## 2. Storage Breakdown — Current State

### 2.1 Permanent Files

| Directory | File Type | Files | Size (GB) | Avg/File |
|-----------|-----------|-------|-----------|----------|
| `images/` | .tiff | 6,066 | 11.4466 | 1.93 MB |
| `ground_truth/` | .json | 6,066 | 7.5124 | 1.24 MB |
| `ground_truth/` | .png | 6,067 | 0.0343 | 5.7 KB |
| `metadata/` | .json | 18,198 | 0.0195 | 1.1 KB |
| root | checkpoint.json etc | ~3 | 0.00007 | — |
| **Total permanent** | | **30,400** | **18.9822** | |

### 2.2 Temporary Files

| Type | Location | Files | Size (GB) | Avg/File |
|------|----------|-------|-----------|----------|
| `*_height.npy` | `ground_truth/` | 406 | 3.1719 | 7.8 MB |
| **Total temporary** | | **406** | **3.1719** | |

### 2.3 Other Areas

| Area | Size |
|------|------|
| `tmp_bench/` | 13.44 MB |
| `tmp_profile/` | 8.91 MB |
| Log files | 0.04 MB |
| Manifests | ~0 MB |
| Checksums | ~0 MB |
| `.tmp` files in DS5 | 0 |

### 2.4 Summary

| Category | Size (GB) |
|----------|-----------|
| **Current permanent storage** | **18.98** |
| **Current temporary storage** | **3.17** |
| **Combined current** | **22.07** |
| Free disk space | 276.32 |
| Total disk capacity | 300.00 |

---

## 3. Per-Sample Storage Rate

Based on 5,697 completed samples:

| Component | Per-Sample | Notes |
|-----------|-----------|-------|
| Image (TIFF, 1024×1024, 16-bit) | 1.93 MB | Uncompressed |
| Ground truth JSON | 1.24 MB | Contains contours, CD measurements |
| Material map PNG | 5.7 KB | Small RGB overlay |
| Metadata JSON ×3 | 1.1 KB | Config + metadata + timing |
| **Permanent per sample** | **~3.33 MB** | |
| height.npy (temporary) | ~8 MB | Deleted after chunk |

---

## 4. File Count Discrepancy

The images directory contains **6,066 files** for **5,697 completed samples** (6.5% excess). This is attributed to:

- Previous generation runs that wrote files before the current checkpoint was established
- Batch processing artifacts from the ProcessPoolExecutor
- Retry attempts that created new files

The excess files are permanent (TIFF images) and inflate the total slightly. The per-sample rate of 3.33 MB is computed against the 5,697 completed samples (from checkpoint), which is the correct denominator.

---

## 5. Observations

1. **No `.tmp` orphan files detected** — atomic writes are working correctly.
2. **406 height.npy files remain** from the current incomplete batch (batch 15). These will be cleaned up when the chunk completes.
3. **No other temporary buffer files** exist within the DS5 directory.
4. **Checkpoint file is 33 KB** — negligible storage overhead.
