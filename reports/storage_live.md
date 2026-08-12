# DS5 Storage Live

**Last Updated:** 2026-08-01 17:10 UTC  

---

## Current Storage State

| Component | Size (GB) | Files |
|-----------|-----------|-------|
| images/ (.tiff) | ~15.0 | ~8,200 |
| ground_truth/ (.json) | ~9.0 | ~8,200 |
| ground_truth/ (.png) | ~0.05 | ~8,200 |
| ground_truth/ (_height.npy) | ~7.84 | 2,511 |
| metadata/ (.json) | 0.02 | 19,998 |
| root files | ~0 | ~3 |
| **Total dataset** | **28.77** | **34,327** |

---

## Disk State

| Metric | Value |
|--------|-------|
| Total capacity | 300.00 GB |
| Currently used | 31.38 GB |
| Currently free | 268.62 GB |
| DS5 dataset | ~30.2 GB |
| Other project files | ~1.19 GB |

---

## Temporary Files

| Type | Count | Size (GB) | Status |
|------|-------|-----------|--------|
| height.npy | 1,002 | 3.17 | ⏳ Pending chunk cleanup |
| .tmp files | 0 | 0 | ✅ Clean |

**height.npy cleanup status:** Will execute automatically when current chunk (batch 17) completes.

---

## Storage Projection

| Milestone | Permanent (GB) | Peak w/ Temp (GB) | Free After Cleanup (GB) |
|-----------|----------------|--------------------|-----------------------|
| Current (6,553) | 25.60 | 28.77 | — |
| 10,000 (chunk 1) | 33.3 | 113.3 | 265.1 |
| 50,000 (chunk 5) | 166.5 | 246.5 | 131.9 |
| 60,000 (chunk 6) | 199.8 | 279.8 | 98.6 |
| **68,700 (limit)** | **228.8** | **298.4** | **0** |
| 100,000 (target) | 317.7 | 397.7 | ⛔ EXCEEDS DISK |

---

## ⚠️ Disk Safety Warning

**Disk will fill around sample 68,700** (chunk 7). The 300 GB disk cannot hold 100K samples at current per-sample size (3.33 MB permanent + 8 MB temp).

**Recommendation:** Reduce `--total` to 75,000 or use a larger disk.

---

## Storage History

| Timestamp | Dataset (GB) | Free (GB) | height.npy (GB) | Notes |
|-----------|-------------|-----------|-----------------|-------|
| 10:48 | 22.07 | 276.32 | 3.17 | Baseline |
| 12:00 | 28.77 | 270.04 | 3.17 | +6.7 GB in 72 min |
