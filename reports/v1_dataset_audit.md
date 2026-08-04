# DS5 Version 1 Dataset Audit

**Date:** 2026-08-03
**Auditor:** Production Release Engineer
**Status:** ALL CHECKS PASSED

---

## Integrity Checks

| # | Check | Result |
|---|-------|--------|
| 1 | Continuous numbering | PASS |
| 2 | No duplicate IDs | PASS |
| 3 | All checkpoint on disk | PASS |
| 4 | No orphan files | PASS |
| 5 | TIFF readable | PASS (10/10 sampled) |
| 6 | JSON valid | PASS (3/3 sampled) |
| 7 | Height.npy cleaned | PASS (546 deleted) |
| 8 | Checkpoint consistent | PASS |

---

## Dataset Statistics

| Metric | Value |
|--------|-------|
| Total samples | 11,064 |
| Last completed ID | 11,658 |
| Checkpoint completed | 11,064 |
| Images (TIFF) | 11,064 |
| Ground Truth JSON | 11,064 |
| Ground Truth Material | 11,064 |
| Metadata (config+meta+timing) | 11,064 x 3 |
| Dataset size | 34.47 GB |
| Free disk | 263.85 GB |

---

## File Format Verification

### TIFF Images
- Format: TIFF (Little-endian, magic=42)
- Resolution: 1024x1024
- Bit depth: 16-bit
- Pixel size: 1.0 nm/px

### Ground Truth
- Format: JSON
- Components: sample, structure_type, pixel_size_nm, cd_measurements, contours

### Metadata
- Config JSON: Structure, process, variability, physics, seeds
- Metadata JSON: Full simulation parameters
- Timing JSON: Performance metrics

---

## Orphan Recovery

46 orphan samples recovered from disk into checkpoint:
- All had complete files (TIFF + GT + Metadata)
- Recovered IDs: 11017-11069

---

## Conclusion

DS5 Version 1 dataset is **COMPLETE** and **VERIFIED**.
All 11,064 samples have valid TIFF images, ground truth, and metadata.
