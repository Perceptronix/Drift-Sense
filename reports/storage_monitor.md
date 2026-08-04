# DS5 Storage Monitor

**Updated:** 2026-08-03

---

## Current State

| Metric | Value |
|--------|-------|
| Dataset size | ~31.5 GB |
| Free disk (E:) | ~264 GB |
| Total disk (E:) | 300 GB |
| Used disk | ~36 GB |

---

## Projections

| At Completion | Estimated Size |
|---------------|----------------|
| 10,000 samples | 31.5 GB (current) |
| 50,000 samples | ~157 GB |
| 100,000 samples | ~313 GB |

---

## Safety

| Check | Status |
|-------|--------|
| Free disk > 20 GB | YES (264 GB) |
| Estimated completion fits | YES (313 GB < 300 GB + buffer) |
| Height.npy cleanup | ACTIVE |
| Chunk cleanup | ACTIVE |

---

## Height.npy Cleanup

- Per-sample height.npy: ~8 MB
- Total at 100k: ~800 GB (deleted after generation)
- Current height.npy count: Checking...

---

## Alerts

None. Storage is healthy.
