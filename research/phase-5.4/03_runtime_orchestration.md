# Runtime Orchestration

**Research Phase:** 5.4
**Document:** 03_runtime_orchestration.md
**Date:** 2026-07-30

---

## 1. Orchestration Components

Two orchestration modules (Phase 4.1 M9/M10) control execution:

| Component | Module | Responsibility |
|---|---|---|
| **Master Pipeline Controller** | orch_pipeline (M9) | Execute Stages 0–9 for one image |
| **Job Manager** | orch_job (M10) | Batch orchestration, workers, checkpoint, progress |

```
CLI
 │
 ▼
Job Manager (orch_job) ── job manifest, worker pool, checkpoint, resume
 │
 ├── Worker 1 → Master Pipeline (orch_pipeline) → image
 ├── Worker 2 → Master Pipeline (orch_pipeline) → image
 ├── ...       (process-isolated, RD3)
 │
 └── Result aggregation → DatasetIndex, reports
```

---

## 2. Master Pipeline Controller

| Aspect | Specification |
|---|---|
| **Role** | Execute the 10-stage pipeline for a single image deterministically |
| **Public API** | `run_pipeline(config) → PipelineResult{SEMImage, GroundTruth, Metadata, FileList}` |
| **Execution model** | Sequential stages; Stage 7 (GT) on a parallel thread pool when enabled (RD5) |
| **Input** | Validated Config (D1) + resolved seed chain |
| **Output** | PipelineResult — immutable record of all artifacts + timing |
| **Timing capture** | Per-stage wall time + peak memory, recorded into Metadata (Phase 4.4 doc 05) |

**Controller responsibilities:**

| Responsibility | Implementation |
|---|---|
| Ordering | Fixed stage order (Doc 02) — never conditional on data |
| Data handoff | Pass D-objects between stages; no module-to-module calls |
| Seed derivation | Compute stage seeds from image seed before dispatch |
| Error propagation | Catch module errors → classify (transient/permanent) → raise to job manager |
| Logging | Structured log per stage (start/end/duration/warnings) |
| Validation | Run postcondition checks per stage (cheap, always on) |

---

## 3. Module Scheduling

| Schedule | Decision | Frozen Ref |
|---|---|---|
| Stage 7 parallel with 4–6 | RD5: M4+M7 after M3 — GT independent of physics | Phase 4.3 |
| No other parallelism per image | Single-image pipeline is sequential (RD4 determinism) | Phase 4.3 |
| Cross-image parallelism | Worker pool at job level (RD3 process isolation) | Phase 4.3 |
| Cache before variability | geo_raster/geo_process outputs cached per structure params (RD8) | Phase 4.3 |

**Scheduling order for a batch (worker-level):**

```
Job Manager:
  1. Read job manifest (list of (config, seed) tuples)
  2. For each worker: dispatch next unprocessed sample
  3. Worker: cache lookup → run_pipeline → write files → report
  4. On completion: aggregate dataset index, stats, reports
```

---

## 4. Error Handling

| Error Class | Examples | Handling |
|---|---|---|
| **Config error** | Invalid schema, unknown material, out-of-range param | Fail-fast before any work; report all errors |
| **Transient** | Disk full, transient I/O, worker crash | Retry up to 3× with backoff; then mark sample failed |
| **Permanent** | Invalid GDSII, physics model failure, numerical instability | Mark sample failed immediately; log full trace; continue batch |
| **Critical** | Corrupt config, library mismatch, seed collision | Abort batch; preserve all completed samples |

**Error taxonomy (operational policy):**

| Code | Meaning | Action |
|---|---|---|
| `OK` | Completed successfully | Recorded |
| `RETRY` | Transient; retry | Backoff retry ≤ 3 |
| `FAILED` | Permanent per-sample failure | Recorded in index; batch continues |
| `ABORT` | Batch-level fatal | Stop, checkpoint, report |

---

## 5. Checkpoint & Recovery

| Aspect | Decision | Frozen Ref |
|---|---|---|
| **Checkpoint granularity** | Per-image (output file written = checkpoint) | Phase 4.3 RD10 |
| **Resume** | `--resume` scans dataset directory; skips samples whose files exist and match config+seed | Phase 4.3 |
| **Manifest journal** | `job_manifest.json` updated after each sample — source of truth for resume | Phase 4.3 |
| **Crash recovery** | On restart, compare manifest vs disk; re-run missing/partial samples | Phase 4.3 |
| **Partial file detection** | Writer writes to temp name then atomic rename (`.tmp` → final) | Operational policy |
| **Idempotency** | Same sample regenerated → identical output (determinism makes resume safe) | Phase 4.3 RD2 |

---

## 6. Logging

| Level | Content | Destination |
|---|---|---|
| DEBUG | Per-stage arrays dims, intermediate hashes | console (dev) |
| INFO | Per-image: sample id, stages, durations | console + log file |
| WARNING | Advisory precondition violations, saturation > threshold, charging skipped | log file + metadata.warnings |
| ERROR | Failed sample, exception trace | log file |
| CRITICAL | Batch abort | log file + stderr |

**Structured format:** JSON-lines (`{"ts","level","sample","stage","msg","dur_ms"}`) — machine-parseable, consistent with metadata style (operational policy).

---

## 7. Progress Tracking

| Metric | Source | UI |
|---|---|---|
| Samples completed / total | manifest counter | progress bar (CLI) |
| Per-image timing (mean/p90) | timing records | summary table |
| Failure count by code | manifest | summary table |
| Throughput (images/s) | rolling window | progress bar |
| ETA | completed rate + remaining | progress bar |

---

## 8. Reproducibility at Runtime

| Mechanism | Implementation | Frozen Ref |
|---|---|---|
| Seed chain | master → structure → image → stage (hash-derived) | Phase 4.3 RD7 |
| Config snapshot | Full resolved config serialized per sample | Phase 4.3 |
| Version pinning | app version, git hash, library hashes in metadata | Phase 4.3 |
| Deterministic libraries | NumPy/SciPy pinned; PCG64 RNG | Phase 5.3 |
| Fixed reduction order | All reductions with explicit axis/order | Phase 4.3 RD6 |
| Platform recording | hostname, OS, Python version in metadata | Phase 4.4 doc 05 |
| Cross-platform caveat | Bitwise determinism guaranteed on same platform; cross-platform tolerance documented | Phase 4.3 |

---

## 9. Module Communication Protocol

| Communication | Mechanism | Data |
|---|---|---|
| Controller → module | Direct function call with kwargs | D-objects + config + seeds |
| Module → controller | Return value (D-object) + optional warning list | Validated output |
| Controller → job manager | Result record (sample id, artifacts, timing, warnings) | Structured dict |
| Job manager → CLI | Aggregate report | Dict/JSON |
| None (forbidden) | Module-to-module direct calls outside I-interfaces | — |

**Frozen rule:** No module imports or calls another module except through the master controller's certified interface sequence. This keeps the system a strict pipeline (Phase 4.1 AD1/AD4).

---

## Sources

- Phase 4.1 — Architecture decisions AD1, AD4, AD5.
- Phase 4.3 — Runtime decisions RD1–RD13 (parallelism, checkpoint, cache, seeds).
- Phase 4.4 — Metadata specification (provenance, timing).
- Phase 5.1 — WBS packages 1.8, 2.3 (orch_pipeline, orch_job).
- [S3] B. Burns, *Designing Distributed Systems*, O'Reilly, 2018 (worker pool, checkpointing patterns).
- [S4] J. Kleppmann, *Designing Data-Intensive Applications*, O'Reilly, 2017 (idempotency, journals).
