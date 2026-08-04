# DS5 Hugging Face Layout

**Date:** 2026-08-03
**Status:** READY FOR UPLOAD

---

## Directory Structure

```
ds5_final_training/
  images/
    chunk_000/   (1,000 files)
    chunk_001/   (1,000 files)
    chunk_002/   (1,000 files)
    chunk_003/   (1,000 files)
    chunk_004/   (1,000 files)
    chunk_005/   (1,000 files)
    chunk_006/   (1,000 files)
    chunk_007/   (1,000 files)
    chunk_008/   (1,000 files)
    chunk_009/   (1,000 files)
    chunk_010/   (1,000 files)
    chunk_011/   (177 files)
  ground_truth/
    chunk_000/   (2,000 files)
    ...
    chunk_011/   (354 files)
  metadata/
    chunk_000/   (3,000 files)
    ...
    chunk_011/   (531 files)
  checkpoint.json
  README.md
```

---

## Hugging Face Compliance

| Requirement | Status |
|-------------|--------|
| Max 10,000 files per dir | PASS (max 3,000) |
| Deterministic paths | PASS |
| No scientific modifications | PASS |
| Future-proof for 100K | PASS |

---

## Chunk Configuration

| Parameter | Value |
|-----------|-------|
| Chunk size | 1,000 samples |
| Max files per chunk | 3,000 (metadata) |
| Chunk naming | chunk_NNN (3 digits) |
| Deterministic | YES (sample_id // 1000) |

---

## Future Scaling (100K samples)

| Chunks | Files per dir |
|--------|---------------|
| images | 100 chunks |
| ground_truth | 100 chunks |
| metadata | 100 chunks |

All directories will remain under 5,000 files.

---

## Upload Recommendation

1. Upload images first (largest files)
2. Upload ground truth second
3. Upload metadata third
4. Upload checkpoint.json last
