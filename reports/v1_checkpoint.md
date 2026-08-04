# DS5 Version 1 Checkpoint

**Date:** 2026-08-03
**Status:** VERIFIED

---

## Checkpoint State

| Field | Value |
|-------|-------|
| File | datasets/ds5_final_training/checkpoint.json |
| Completed samples | 11,064 |
| Failed samples | 0 |
| Last completed ID | 11,658 |
| Next sample ID | 11,064 (first gap) |
| Current batch | 27 |
| Resume point | Sample 11,064 |

---

## Resume Configuration

| Parameter | Value |
|-----------|-------|
| Master seed | 5005 |
| Workers | 8 |
| Checkpoint interval | 500 |
| Chunk size | 10,000 |
| Resume enabled | YES |

---

## Seed Continuity

- Master seed: 5005 (frozen)
- Deterministic generation: VERIFIED
- `build_sample_plan()` uses `random.Random(5005)`
- No scientific changes: VERIFIED

---

## Resume Command

```bash
python validation/generate_ds5_final.py \
  --samples 100000 \
  --seed 5005 \
  --workers 8 \
  --out datasets/ds5_final_training
```

---

## Status

Checkpoint is **VALID** and ready for resume.
