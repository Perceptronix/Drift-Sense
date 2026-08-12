# DS5 Performance Live

**Last Updated:** 2026-08-02 06:24 UTC  

---

## Current Performance

| Metric | Value | Trend |
|--------|-------|-------|
| Samples/min | 0 | ⛔ STOPPED |
| Images/hour | 0 | ⛔ STOPPED |
| CPU utilization | Idle | — |
| RAM utilization | Idle | — |
| Disk free | 239.64 GB | Stable (no writes) |

**Generator running with 2 workers. OOM root cause fixed.**

---

## Worker Pool

| Worker | PID | Memory (MB) | CPU (sec) | Status |
|--------|-----|-------------|-----------|--------|
| Main | 40624 | 45.0 | 4.2 | 🟢 Coordinator |
| Worker 1 | 20056 | 146.4 | 3281.9 | 🟢 Active |
| Worker 2 | 23944 | 153.7 | 3442.8 | 🟢 Active |
| Worker 3 | 24464 | 135.0 | 3389.9 | 🟢 Active |
| Worker 4 | 29732 | 154.8 | 3427.9 | 🟢 Active |
| Worker 5 | 31228 | 113.5 | 3384.0 | 🟢 Active |
| Worker 6 | 36888 | 155.0 | 3449.6 | 🟢 Active |
| Worker 7 | 38724 | 145.7 | 3250.4 | 🟢 Active |
| Worker 8 | 42792 | 142.2 | 3443.4 | 🟢 Active |

**Total worker memory:** ~1,191 MB  
**Average worker CPU:** ~3,380 sec  
**All 8 workers active and balanced** ✅

---

## Bottleneck Analysis

- **Current bottleneck:** Disk I/O (TIFF write + JSON serialization per sample)
- **RAM headroom:** 3.9 GB available (16.5% margin)
- **CPU headroom:** 17% available
- **No memory pressure detected**
- **No worker crashes or restarts detected**

---

## Performance History

| Timestamp | Samples/min | CPU% | RAM% | Notes |
|-----------|-------------|------|------|-------|
| 12:00 | 96 | 83 | 83.5 | Baseline measurement |
