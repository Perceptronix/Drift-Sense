# DS5 Checkpoint Live

**Last Updated:** 2026-08-02 06:24 UTC  

---

## Checkpoint State

| Field | Value |
|-------|-------|
| Completed samples | 9,567 |
| Failed samples | 0 |
| Total generated | 9,567 |
| Last batch ID | 19 (in progress, chunk 1) |
| Start time | 1785510011.937 (2026-08-01 09:24:59 UTC) |
| Status | 🟢 RUNNING — Fixed (2 workers) |

---

## Crash Summary

| Crash | Time | Completed Before | New Samples | Batch Progress |
|-------|------|-----------------|-------------|----------------|
| 1 | ~14:00 | 7,053 | 126 → 7,179 | Partial |
| 2 | ~17:00 | 8,172 | 249 → 8,421 | Partial |
| 3 | ~20:50 | 8,421 | 411 → 8,832 | Partial |
| 4 | ~21:40 | 8,832 | 0 | None |
| 5 | ~00:40 | 8,832 | 0 | None |

**Batch 19 has been interrupted 4 times and still not completed.** Effective throughput severely degraded.

---

## Crash & Recovery

- **Crash:** ~14:00 UTC during batch 18 (RAM at 90.6% → OOM likely)
- **Batch 18 progress before crash:** 126 samples completed (7,053 → 7,179)
- **Restart:** 14:42 UTC — resumed from checkpoint at 7,179
- **Resume point:** Sample 7,179 (safe — checkpoint intact)
- **height.npy orphaned:** 1,547 files (~4.7 GB) — pending chunk cleanup

---

## Checkpoint Integrity

| Check | Status |
|-------|--------|
| File exists | ✅ |
| JSON valid | ✅ |
| Completed list sequential | ✅ (0–6552 with known gaps from retries) |
| Failed dict empty | ✅ |
| No corruption detected | ✅ |

---

## Seed Continuity

| Property | Value |
|----------|-------|
| Master seed | 5005 |
| Sample plan | Deterministic (seed-based) |
| Resume mechanism | Checkpoint-driven (completed list) |
| Deterministic sequence | ✅ Verified |

---

## Resume Point

The checkpoint correctly tracks:
- **Completed:** 6,553 sample indices (list of ints)
- **Failed:** {} (empty — all retries succeeded)
- **Last batch:** 17 (currently processing batch 17/204)

**If the generator restarts:** It will resume from sample 6,553, regenerating any samples that were in-progress during the crash (batch 17's remaining samples).

---

## Checkpoint History

| Timestamp | Completed | Batch | Elapsed (min) | Notes |
|-----------|-----------|-------|---------------|-------|
| 10:48 | 6,053 | 16 | 0 | Resume from prior run |
| 12:00 | 6,553 | 17 | 68.1 | +500 samples in 68 min |
