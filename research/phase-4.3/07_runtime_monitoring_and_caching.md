# Runtime Monitoring and Caching

**Research Phase:** 4.3
**Document:** 07_runtime_monitoring_and_caching.md
**Date:** 2026-07-30

---

## 1. Monitoring Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         RUNTIME MONITOR                                 │
│                                                                         │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐              │
│  │  Progress    │  │  Logger      │  │  Telemetry       │              │
│  │  Reporter    │──│  (structured)│──│  Collector       │              │
│  └─────────────┘  └──────────────┘  └──────────────────┘              │
│         │                │                      │                       │
│         ▼                ▼                      ▼                       │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐              │
│  │ Console     │  │ Log files    │  │ Performance      │              │
│  │ (CLI)       │  │ (disk)       │  │ stats (JSON)     │              │
│  └─────────────┘  └──────────────┘  └──────────────────┘              │
└─────────────────────────────────────────────────────────────────────────┘
```

**Engineering Decision:** Three independent monitoring channels: progress (user-facing), logging (diagnostics), telemetry (performance).

---

## 2. Progress Reporting

### 2.1 Reporting Levels

| Level | Content | Format | User |
|---|---|---|---|
| **Minimal** | Counters only | `[42/1000]` | Scripts, automation |
| **Normal** | Counters + ETA + rate | `[42/1000] ETA 12:30 rate=3.2 img/s` | Interactive CLI |
| **Verbose** | Per-image details | `Image 42: iso_line cd=50nm seed=0x7a3b (1.2s)` | Debugging |

### 2.2 Progress Events

| Event | When | Data |
|---|---|---|
| `job_started` | Worker begins job | job_id, structure, seed, timestamp |
| `job_completed` | Worker finishes job | job_id, duration, output_path |
| `job_failed` | Worker fails | job_id, error, retry_count |
| `stage_progress` | Pipeline stage completes | job_id, stage, duration |
| `batch_progress` | Aggregate | completed, total, rate, ETA |
| `batch_complete` | All jobs done | total, success, failed, wall_time |

---

## 3. Structured Logging

### 3.1 Log Format

All log entries follow a structured JSON format for automated processing:

```json
{
    "timestamp": "2026-07-30T14:30:00.123Z",
    "level": "INFO",
    "module": "geo_variability",
    "job_id": "0042",
    "message": "LER applied: 3σ=2.4nm, ξ=25nm",
    "data": {
        "ler_3sigma_nm": 2.4,
        "ler_xi_nm": 25,
        "n_edges": 2,
        "duration_ms": 152
    }
}
```

### 3.2 Log Levels

| Level | Purpose | Examples |
|---|---|---|
| **ERROR** | Failures that stop or degrade execution | Config error, file write failure, missing data |
| **WARN** | Non-fatal anomalies | LER > 0.5×CD, saturation > 10%, unknown keys |
| **INFO** | Normal lifecycle events | Job start/completion, pipeline stage, file output |
| **DEBUG** | Detailed diagnostic data | Per-pixel statistics, intermediate array shapes, seed values |

### 3.3 Log File Organization

| File | Contents | Created By |
|---|---|---|
| `run_YYYY-MM-DD_HHMMSS.log` | All events (aggregated) | Main process |
| `worker_{id}.log` | Per-worker events | Worker process |
| `errors.log` | ERROR level only | Main process (filtered) |

---

## 4. Performance Telemetry

### 4.1 Metrics Collected

| Metric | Unit | Collection Method |
|---|---|---|
| Wall clock per image | seconds | Timer around pipeline execution |
| Per-stage time | seconds | Timer per module |
| Images per second (batch) | img/s | Rolling counter |
| Memory usage | MB | RSS per process |
| Peak memory | MB | Max RSS |
| Disk writes | MB | Accumulated output size |

### 4.2 Telemetry Output

```json
// telemetry.json (written at batch completion)
{
    "batch": {
        "n_images": 1000,
        "wall_time_s": 1423.0,
        "total_cpu_time_s": 5640.0,
        "avg_time_per_image_ms": 1423.0,
        "min_time_per_image_ms": 980.0,
        "max_time_per_image_ms": 2450.0,
        "images_per_second": 0.70
    },
    "breakdown": {
        "geometry": {"total_s": 2100, "avg_ms": 2100},
        "physics": {"total_s": 2800, "avg_ms": 2800},
        "dataset": {"total_s": 740, "avg_ms": 740}
    },
    "resource": {
        "avg_memory_mb": 245,
        "peak_memory_mb": 412,
        "total_disk_written_mb": 2850
    }
}
```

---

## 5. Self-Check Mode

A `--self-check` mode runs a minimal pipeline with a fixed seed and compares the output to a known reference:

```
$ python -m semicon.sim --self-check
[Self-check] Running minimal pipeline (iso_line, seed=42)...
[Self-check] Image hash: 7a3b... (expected: 7a3b...)
[Self-check] ✓ Passed: 1/1 tests
[Self-check] System integrity verified.
```

| Check | What It Tests |
|---|---|
| **Config parsing** | Default config loads and validates |
| **GDSII rasterization** | Known GDSII → known pixel mask |
| **Process model** | Known parameters → known height field |
| **Variability** | Known seed → known LER pattern |
| **Signal generation** | Known height field → known yield map |
| **Degradation + formation** | Known yield → known image pixel values |
| **Output** | Known image → known file format |

**Inference:** Self-check mode provides a quick (< 5 s) system integrity test. All stages must pass. The reference output hash is pinned in code.

---

## 6. Caching Strategy

### 6.1 What May Be Cached

| Artifact | Cache Eligible? | Condition | Typical Size |
|---|---|---|---|
| **Layer stack specification** | ✅ Yes | Always (static) | < 1 KB |
| **Material property tables** | ✅ Yes | Always (static) | < 10 KB |
| **GDSII rasterization (pixel mask)** | ✅ Yes | Same GDSII + layer + dims | 1 MB |
| **Deterministic height field** | ✅ Yes | Same process params | 8 MB |
| **Variable height field** | ⚠️ Yes | Same variability params + same seed | 8 MB |
| **Yield maps** | ❌ No | Physics params rarely repeat within batch | 16 MB each |
| **SEM image** | ❌ No | Output — never cached (written to disk) | 2 MB |

**Engineering Decision:** Cache deterministic height fields (M2 output) when the same structure is generated repeatedly with different seeds for variability. The cache key is a hash of the input parameters.

### 6.2 Cache Invalidation

| Event | Action |
|---|---|
| Config parameter changes | Cache cleared (entire run) |
| Structure definition changes | Cache cleared (that structure only) |
| Software version changes | Cache invalidated (by version key) |
| `--no-cache` flag supplied | Cache disabled for this run |
| Disk cache exceeds limit | LRU eviction |

### 6.3 Cache Key Derivation

```
cache_key = SHA-256(
    struct_type +
    struct_parameters (sorted key=value) +
    geometry_config +
    layer_stack_hash +
    software_version
)
```

### 6.4 Cache Performance Impact

| Scenario | Without Cache | With Cache | Speedup |
|---|---|---|---|
| 1000 images, same structure, different LER seeds | 1000 × full pipeline | 1 × geometry + 1000 × LER → physics | ~2–3× (geometry ~40% of time) |
| 1000 images, different structures | 1000 × full pipeline | Minimal (no repeats) | ~1× |

**Inference:** Caching provides meaningful speedup for repeated structures with different variability seeds. For unique structures, caching adds no benefit and minimal overhead.

---

## Sources

- [R5] J. K. Ousterhout, *A Philosophy of Software Design*, Yaknyam Press, 2018.
- [R12] P. J. Plauger, *The Standard C Library*, Prentice Hall, 1992 (logging and error handling patterns).
- [R13] C. Evans, *Software Engineering for Science*, CRC Press, 2017.
- Phase 4.2, Document 10 — Final report with data objects.
- Phase 4.1, Document 05 — Layered architecture.
