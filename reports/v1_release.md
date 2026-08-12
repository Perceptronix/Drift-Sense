# DS5 Version 1 Release

**Date:** 2026-08-03
**Version:** 1.0.0
**Status:** READY FOR PUBLICATION

---

## Dataset Overview

| Field | Value |
|-------|-------|
| Name | SEMICON-DS5 |
| Version | 1.0.0 |
| Samples | 11,064 |
| Resolution | 1024x1024 |
| Bit depth | 16-bit |
| Pixel size | 1.0 nm/px |
| Total size | 34.47 GB |

---

## Folder Structure

```
ds5_final_training/
  images/           # 11,064 TIFF files
  ground_truth/     # 11,064 GT JSON + Material PNG
  metadata/         # 11,064 x 3 (config, metadata, timing)
  checkpoint.json   # Checkpoint for resume
  README.md         # Dataset documentation
```

---

## Structure Distribution

| Structure Type | Weight | Count (approx) |
|---------------|--------|----------------|
| dense_ls | 20% | 2,213 |
| contact | 15% | 1,660 |
| iso_line | 15% | 1,660 |
| via | 10% | 1,106 |
| fin | 10% | 1,106 |
| gate | 10% | 1,106 |
| trench | 8% | 885 |
| sti | 5% | 553 |
| bimaterial | 4% | 443 |
| pitch_std | 3% | 332 |

---

## Parameter Ranges

| Parameter | Range |
|-----------|-------|
| CD | 10-500 nm |
| Height | 20-200 nm |
| Pitch | 20-1000 nm |
| Beam energy | 0.3-30 keV |
| Probe current | 1-1000 pA |
| Probe diameter | 0.5-10 nm |

---

## What's Included

- Synthetic SEM images (16-bit TIFF)
- Ground truth: CD measurements, contours, edge maps
- Material annotations (PNG masks)
- Full simulation metadata
- Checkpoint for automatic resume

---

## What's NOT Included (Planned for Full Release)

- Remaining 88,936 samples (to reach 100,000)
- Train/val/test splits
- Full statistics report

---

## Publication Checklist

- [x] All 11,064 samples verified
- [x] TIFF format correct
- [x] JSON valid
- [x] No duplicates
- [x] No corruption
- [x] Checkpoint preserved
- [x] Resume ready
- [ ] Hugging Face upload (pending)
- [ ] License file (pending)
- [ ] Dataset card (pending)
