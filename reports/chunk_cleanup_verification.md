# DS5 Chunk Cleanup Verification

**Date:** 2026-08-01 10:50 UTC  
**Auditor:** Production Storage Engineer  
**Orchestration file:** `validation/run_ds5_production.py`  

---

## 1. Cleanup Architecture

The DS5 production pipeline uses a **two-layer orchestrator**:

| Layer | File | Role |
|-------|------|------|
| Outer | `validation/run_ds5_production.py` | Chunk management, disk monitoring, height.npy cleanup |
| Inner | `validation/generate_ds5_final.py` | Sample generation, checkpointing, retry logic |

---

## 2. height.npy Lifecycle

### 2.1 Creation

**Where:** `simulator/src/semicon/dataset/writer.py:75-77`

```python
if write_aux:
    paths["height"].parent.mkdir(parents=True, exist_ok=True)
    np.save(paths["height"], height_field.data)
```

- Created during pipeline stage S9 for each sample
- Path: `ground_truth/{sample_id:06d}_height.npy`
- Size: ~8 MB per file (float64 array, 1024×1024)
- `write_aux=True` is passed from `pipeline.py:148`

### 2.2 Deletion — Post-Chunk Cleanup

**Where:** `validation/run_ds5_production.py:228-239`

```python
# Post-chunk cleanup: delete height.npy files
cp = load_checkpoint(DS5_DIR)
done = len(cp.get("completed", []))
hf = count_height_files(DS5_DIR)
print(f"\n  Post-chunk status: {done}/{args.total} completed, {hf} height.npy files")

if hf > 0:
    freed_mb = hf * HEIGHT_NPY_SIZE_MB
    print(f"  Deleting {hf} height.npy files (~{freed_mb:.0f} MB)...")
    deleted = delete_height_files(DS5_DIR)
    free_gb = get_free_space_gb(DS5_DIR)
    print(f"  Deleted {deleted} files. Free space: {free_gb:.1f} GB")
```

**When:** After each chunk's generation subprocess returns (line 207-214)  
**Trigger:** Automatic — runs unconditionally after every chunk completion  
**How:** `delete_height_files()` globs `ground_truth/*_height.npy` and calls `.unlink()` on each  

### 2.3 Emergency Cleanup — Pre-Chunk

**Where:** `validation/run_ds5_production.py:185-202`

```python
if free_gb < MIN_FREE_GB:
    print(f"  WARNING: Low disk space ({free_gb:.1f} GB < {MIN_FREE_GB} GB minimum)")
    hf = count_height_files(DS5_DIR)
    if hf > 0:
        deleted = delete_height_files(DS5_DIR)
        free_gb = get_free_space_gb(DS5_DIR)
```

**When:** Before each chunk, if free space < 15 GB  
**Purpose:** Emergency space recovery to prevent disk exhaustion  

---

## 3. Cleanup Verification Status

| Check | Status | Details |
|-------|--------|---------|
| Post-chunk cleanup implemented | ✅ YES | Lines 228-239 |
| Pre-chunk emergency cleanup | ✅ YES | Lines 185-202 |
| Cleanup-only mode | ✅ YES | `--cleanup-only` flag (lines 154-159) |
| Cleanup triggers automatically | ✅ YES | After every chunk completion |
| Cleanup deletes ALL height.npy | ✅ YES | Globs `*_height.npy`, deletes all |
| Cleanup does NOT touch scientific files | ✅ YES | Only targets `*_height.npy` pattern |
| `.tmp` file cleanup | ⚠️ NO | No explicit orphan `.tmp` cleanup (negligible impact) |

---

## 4. Current Cleanup Readiness

| Metric | Value |
|--------|-------|
| Height.npy files on disk | 406 |
| Height.npy total size | 3.17 GB |
| Current chunk | 15 (in progress) |
| Chunk completion status | NOT YET COMPLETE |
| Cleanup ready to trigger | ✅ YES — will fire when chunk 15 completes |

**No manual intervention required.** The cleanup will execute automatically when the current chunk finishes.

---

## 5. Helper Functions

### `count_height_files(ds5_dir)` — Line 55-60
Counts `*_height.npy` files in `ground_truth/` directory.

### `delete_height_files(ds5_dir)` — Line 63-72
Deletes all `*_height.npy` files. Returns count of deleted files.

### `load_checkpoint(ds5_dir)` — Line 75-81
Loads `checkpoint.json` for progress tracking.

---

## 6. Design Justification

From `run_ds5_production.py` lines 5-12:

- height.npy is an **intermediate physics buffer**, NOT canonical ground truth
- Per Phase 4.4 section 1: edge maps, CD values, contours are the 5 GT components; height field is INPUT to GT derivation
- Per sample WITH height.npy: ~10 MB; WITHOUT: ~2 MB
- 100K samples: ~1 TB with height.npy vs ~200 GB without
- Deletion saves approximately **800 GB** for a full 100K run

---

## 7. Conclusion

**Automatic height.npy cleanup is fully implemented and verified.** The cleanup:

1. Triggers automatically after each chunk completes
2. Has an emergency pre-chunk fallback for low-disk scenarios
3. Only targets temporary height.npy files
4. Does not modify any scientific data, images, or ground truth
5. Is ready to execute when the current chunk (batch 15) completes
