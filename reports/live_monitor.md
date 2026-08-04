# DS5 Live Monitor

**Last Updated:** 2026-08-02 22:07 UTC  
**Status:** 🟢 RUNNING (1 worker, stable)  

---

## Current Status

```
=====================================================
DS5 LIVE STATUS — 2026-08-02 22:07 UTC
=====================================================

Completed:    9,905 / 100,000
Remaining:    90,095
Progress:     9.9%

Workers:      1 active (3 Python processes) ✅
Disk:         264.57 GB free
RAM:          ~77% used

Dataset Size: ~35.0 GB
height.npy:   3,722 files (pending chunk cleanup)

Checkpoint:   Verified ✅
Health:       🟢 STABLE
=====================================================
```

**Progress confirmed.** 1-worker generator completing batches. Rogue 8-worker launches killed (2 separate incidents). 261 failed samples from rogue launches will be retried. Chunk cleanup will trigger at 10,000 samples.

---

## Crash & Recovery Timeline

| Time | Event |
|------|-------|
| 12:39 | Batch 17 completed (7,053), Batch 18 started |
| ~14:00 | **1st crash** — OOM likely |
| 14:42 | **1st restart** — resumed from 7,179 |
| ~17:00 | **2nd crash** — during batch 19 |
| 17:10 | **2nd restart** — resumed from 8,172 |
| ~20:50 | **3rd crash** — during batch 19 |
| 20:54 | **3rd restart** — resumed from 8,421 |
| 14:43 | First progress: 7,179 samples, batch 18 in progress |

---

## Progress History

| Time | Completed | Progress | Rate | Disk Free | RAM | height.npy | Health |
|------|-----------|----------|------|-----------|-----|------------|--------|
| 10:48 | 6,053 | 6.1% | — | 276.3 GB | — | — | 🟢 |
| 12:00 | 6,553 | 6.6% | 96/min | 270.0 GB | 83% | 1,002 | 🟢 |
| 12:10 | 6,553 | 6.6% | 96/min | 268.6 GB | 83% | 1,108 | 🟢 |
| 14:03 | 7,053 | 7.1% | 64/min | 264.7 GB | 91% | 1,462 | 🟡 |
| 14:40 | 7,053 | 7.1% | 0/min | 264.1 GB | 83% | 1,518 | ⛔ |
| 14:43 | 7,179 | 7.2% | Starting | 263.8 GB | — | 1,547 | 🟢 |
| 15:37 | 7,679 | 7.7% | 167/min | 257.1 GB | 79% | 2,156 | 🟢 |
| ~17:00 | 8,172 | 8.2% | 0/min | 253.2 GB | — | 2,511 | ⛔ |
| 17:10 | 8,172 | 8.2% | Starting | 253.2 GB | — | 2,511 | 🟢 |
| ~20:50 | 8,421 | 8.4% | 0/min | 250.5 GB | — | 2,760 | ⛔ |
| 20:54 | 8,421 | 8.4% | Starting | 250.5 GB | — | 2,760 | 🟢 |
| ~21:40 | 8,832 | 8.8% | 0/min | 246.0 GB | — | 3,172 | ⛔ |
| 21:45 | 8,832 | 8.8% | Starting | 246.0 GB | — | 3,172 | 🟢 |
| ~00:40 | 8,832 | 8.8% | 0/min | 243.4 GB | — | 3,410 | ⛔ |
| 00:44 | 9,071 | 9.1% | Starting | 243.4 GB | — | 3,410 | 🟢 |
| ~06:20 | 9,071 | 9.1% | 0/min | 239.6 GB | — | 3,754 | ⛔ |
| 06:25 | 9,415 | 9.4% | Starting | 239.6 GB | — | 3,761 | 🟢 |
| 20:47 | 9,415 | 9.4% | 0/min | 239.5 GB | — | 3,768 | ⛔ |
| 21:00 | 9,567 | 9.6% | Running | 268.3 GB | 81% | 0 | 🟢 |
| 21:43 | 9,666 | 9.7% | Running | 267.2 GB | 77% | 0 | 🟢 |
| 22:07 | 9,905 | 9.9% | Running | 264.6 GB | 77% | 3,722 | 🟢 |

---

## Alerts

### ⛔ CRASH 1 — 14:00 UTC (RESOLVED)
OOM likely. Restarted at 14:42 from checkpoint 7,179.

### ⛔ CRASH 2 — ~17:00 UTC (RESOLVED)
**Generator crashed again** during batch 19. Checkpoint saved at 8,172 (493 of 500 batch samples completed). Restarted at 17:10 from checkpoint 8,172. No data loss.

### ⛔ CRASH 3 — ~20:50 UTC (RESOLVED)
**Generator crashed again** during batch 19. Checkpoint saved at 8,421 (249 of 500 batch samples completed). Restarted at 20:54 from checkpoint 8,421. No data loss.

### ⛔ CRASH 4 — ~21:40 UTC (RESOLVED)
**Generator crashed again** during batch 19. Checkpoint saved at 8,832 (411 of 500 batch samples completed). Restarted at 21:45 from checkpoint 8,832. No data loss.

### ⛔ CRASH 5 — ~00:40 UTC (RESOLVED)
**Generator crashed again** during batch 19. Checkpoint still at 8,832 (no new samples completed before crash). Restarted at 00:43. No data loss.

**Pattern:** 5 crashes in ~10 hours. Crash intervals: 3.5h → 2.5h → 1h → 3h. Batch 19 has been interrupted 4 times — still not completed. Effective throughput severely degraded. Checkpoint ensures zero data loss. Monitor continues tracking.

### ⛔ CRASH 6 — ~06:20 UTC (RESOLVED)
Generator crashed. Restarted at 06:24. Resumed from 9,415. No data loss.

### ⛔ CRASH 7 — ~06:30 UTC (NOT RESTARTED)
Generator crashed again within minutes of restart. **Down for 14+ hours.** No restart. Awaiting manual intervention.
