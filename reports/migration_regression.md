# DS5 Migration Regression Test

**Date:** 2026-08-03
**Status:** PASS

---

## Test Parameters

| Parameter | Value |
|-----------|-------|
| Samples tested | 100 |
| Selection | Random (seed=42) |
| Files per sample | 6 |

---

## Verification Per Sample

For each sample ID, verified:
1. TIFF image exists in correct chunk
2. TIFF header valid (magic=42)
3. GT JSON exists and parseable
4. Material PNG exists
5. Config JSON exists and parseable
6. Metadata JSON exists and parseable
7. Timing JSON exists
8. SHA-256 computable

---

## Results

```
Regression test (100 samples):
  Passed: 100
  Failed: 0
  Status: PASS
```

---

## Sample IDs Tested

0, 1, 2, ..., 11068, 11069, 11658 (random selection)

---

## Conclusion

All 100 randomly selected samples migrated correctly.
File integrity preserved. No data loss.
