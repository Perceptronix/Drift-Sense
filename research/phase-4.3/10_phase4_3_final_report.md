# Phase 4.3 Final Report: Runtime Execution & Orchestration

**SEMICON 2026 Research Repository**
**Applied Materials**
**Date:** 2026-07-30
**Classification:** Research-Only (Phase 4.3)

---

## Executive Summary

Phase 4.3 answers: **"How should the simulator execute efficiently, reproducibly, and reliably from configuration to dataset generation?"**

The complete runtime model is specified: a 10-phase execution pipeline, sequential per-image processing with embarrassingly parallel batch execution, hierarchical seed-based reproducibility, per-image checkpointing, structured logging with three channels, and deterministic height field caching.

---

## 1. Key Results

### 1.1 Execution Lifecycle (Document 02)

| Phase | Action | Time |
|---|---|---|
| 0. Startup | Parse CLI, init logging | < 1 s |
| 1. Configuration | Load, validate, resolve, load libraries | < 1 s |
| 2. Resource allocation | Workers, directory, disk check | < 1 s |
| 3. Job expansion | Config → job manifest | < 1 s |
| 4. Pipeline execution | Per-image M2→M8 (batch loop) | > 95% |
| 5. Validation | Check outputs, regressions | 1–5% |
| 6. Dataset finalization | Index, statistics | < 1 s |
| 7. Export | Archive (optional) | Variable |
| 8. Shutdown | Cleanup, exit | < 1 s |

### 1.2 Scheduling (Document 03)

| Mode | Use | Workers |
|---|---|---|
| **Single** | 1 image, debugging | 1 |
| **Batch** | N structures × R repetitions | Static pool |
| **Sweep** | Parameter grid | Dynamic pool |

### 1.3 Parallelism (Document 04)

| Level | Parallel? | Mechanism | Speedup |
|---|---|---|---|
| Across jobs | ✅ Yes | Multiprocessing pool | linear up to N_cores |
| Within pipeline (M4 + M7) | ✅ Yes | Concurrent execution | 10–15% |
| Within stage (vector ops) | ✅ Yes | NumPy (implicit) | 5–10× vs pure Python |
| Across pipeline stages | ❌ No | Sequential by design | — |
| GPU | ❌ No | Not required | — |

### 1.4 Reproducibility (Document 05)

| Component | Method |
|---|---|
| **Seed** | Hierarchical: master → structure → image → stage |
| **Config** | Resolved snapshot (YAML → resolved JSON) |
| **Version** | Git commit + dependency pinning |
| **Environment** | Platform + Python version recorded |

### 1.5 Checkpoint & Recovery (Document 06)

| Aspect | Strategy |
|---|---|
| **Granularity** | Per image (output file = checkpoint) |
| **Restart** | Subtract completed from manifest |
| **Transient failure** | Retry up to 3× |
| **Crash recovery** | Detect incomplete files → re-run |

### 1.6 Monitoring (Document 07)

| Channel | Content | Format |
|---|---|---|
| **Progress** | Counters, ETA, rate | Console (3 levels) |
| **Logging** | All events, debug | Structured JSON |
| **Telemetry** | Performance metrics | JSON summary |

### 1.7 Caching (Document 07)

| Cache | Eligible? | Cache Key |
|---|---|---|
| Layer stack | ✅ Yes | Static |
| Material tables | ✅ Yes | Static |
| GDSII rasterization | ✅ Yes | Hash(inputs) |
| Deterministic height field | ✅ Yes | Hash(inputs) |
| Variable height field | ❌ No | Seed-dependent |
| Yield maps | ❌ No | Physics-parameter-dependent |

---

## 2. Frozen Runtime Decisions

| # | Decision | Value | Document |
|---|---|---|---|
| RD1 | Execution model | Sequential per image; multiprocessing per batch | 02 |
| RD2 | Pipeline lifecycle | 10 phases (0–8) | 02 |
| RD3 | Scheduling | Static pool (batch); dynamic pool (sweep) | 03 |
| RD4 | Worker parallelism | Independent samples only | 04 |
| RD5 | Intra-pipeline parallelism | M4 + M7 concurrent after M3 | 04 |
| RD6 | GPU | Not required | 04 |
| RD7 | Reproducibility | Hierarchical seed; config snapshot; version pinning | 05 |
| RD8 | Checkpoint | Per-image (output file itself) | 06 |
| RD9 | Recovery | Resume from last completed | 06 |
| RD10 | Logging | Structured JSON + progress + telemetry | 07 |
| RD11 | Progress | 3 levels (minimal, normal, verbose) | 07 |
| RD12 | Caching | Deterministic height fields only | 07 |

---

## 3. Phase 4.3 Success Criteria

| Criterion | Status | Evidence |
|---|---|---|
| ✓ Frozen runtime execution model | **Achieved** | 10-phase lifecycle, sequential per image (Document 02) |
| ✓ Frozen scheduling strategy | **Achieved** | Single, batch, sweep modes defined (Document 03) |
| ✓ Frozen reproducibility requirements | **Achieved** | Hierarchical seed, config snapshot, version pinning (Document 05) |
| ✓ Frozen checkpoint and recovery strategy | **Achieved** | Per-image checkpoint, resume, transient retry (Document 06) |
| ✓ Frozen monitoring and logging model | **Achieved** | 3-channel monitoring: progress, logs, telemetry (Document 07) |
| ✓ Frozen caching policy | **Achieved** | Deterministic height fields; hash-based invalidation (Document 07) |

---

## 4. Complete System Execution (Startup to Dataset)

```
START
  │
  ├── CLI entry point
  ├── Load config (YAML/TOML → Config)
  ├── Validate (schema, range, consistency)
  ├── Allocate resources (workers, directory)
  ├── Expand jobs (config → job_manifest)
  │
  ├── For each job (sequential or parallel):
  │   ├── M2 Process Model (pixel mask → height field)
  │   ├── M3 Variability Engine (height field → variable geometry)
  │   │
  │   ├── (parallel branch)            (parallel branch)
  │   │   ├── M4 Signal Gen            ├── M7 Ground Truth
  │   │   ├── M5 Degradation           └── (end)
  │   │   └── M6 Image Former
  │   │
  │   └── M8 Dataset Writer (image + GT + metadata → files)
  │
  ├── Validate outputs
  ├── Finalize dataset index
  ├── Export (optional archive)
  └── Shutdown
```

---

## 5. Knowledge Required for Phase 4.4

Phase 4.3 defines **how the system executes**. Phase 4.4 must answer:

1. **Dataset packaging format:** How are generated images organized, annotated, and distributed — file naming, directory layout, index format, ground-truth encoding?

2. **Metadata and annotation schema:** What metadata must accompany each dataset — structure parameters, physics parameters, ground-truth labels, data provenance?

3. **Output distribution:** How are datasets packaged for downstream consumption — single archive, HDF5, directory tree, cloud storage?

4. **Final integration audit:** Is the complete system — architecture, contracts, execution, dataset packaging — consistent and implementation-ready?

**Phase 4.4 is the final integration phase. After Phase 4.4, the project is fully specified for implementation.**

---

## 6. Phase 4.3 Document Map

```
research/phase-4.3/
│
├── 01_executive_summary.md              ← Runtime model overview
├── 02_execution_pipeline.md            ← 10-phase lifecycle
├── 03_job_scheduling_strategy.md       ← Single, batch, sweep modes
├── 04_parallelism_and_scalability.md   ← Worker pools, scaling predictions
├── 05_reproducibility_strategy.md      ← Hierarchical seed manager
├── 06_checkpoint_and_recovery.md       ← Per-image checkpoint, resume
├── 07_runtime_monitoring_and_caching.md ← 3-channel monitoring, caching
├── 08_engineering_conclusions.md       ← 13 frozen runtime decisions
├── 09_complete_reference_list.md        ← 14 references
└── 10_phase4_3_final_report.md          ← This consolidated report
```

---

*End of Phase 4.3 Final Report — Runtime Execution & Orchestration*
