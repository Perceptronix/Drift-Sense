# Execution Pipeline

**Research Phase:** 4.3
**Document:** 02_execution_pipeline.md
**Date:** 2026-07-30

---

## 1. Execution Lifecycle

The complete system execution follows a well-defined lifecycle with 10 phases:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    0. APPLICATION STARTUP                                │
│  Parse command-line arguments. Load environment. Set up logging.        │
│  Initialize RNG from entropy or seed.                                   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    1. CONFIGURATION LOADING                              │
│  Read config file. Parse YAML/TOML → Config object.                     │
│  Validate schema (L1). Validate ranges (L2). Resolve defaults.          │
│  Load structure library entries. Load material property tables.         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    2. RESOURCE ALLOCATION                                │
│  Determine worker count (batch parallelism).                            │
│  Allocate output directory. Initialize dataset index.                   │
│  Verify disk space. Check dependency versions.                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    3. JOB EXPANSION                                      │
│  Expand batch config → array of (structure, parameters, seed) jobs.     │
│  Sort by estimated duration (optional).                                 │
│  Write job manifest to output directory.                                │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    4. PIPELINE EXECUTION (PER JOB)                       │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  For each job in batch:                                          │   │
│  │  4a. Generate deterministic geometry  (M2 Process Model)         │   │
│  │  4b. Apply manufacturing variability (M3 Variability Engine)    │   │
│  │  4c. Compute SEM signal           (M4 Signal Generator)          │   │
│  │  4d. Apply degradation             (M5 Degradation Model)        │   │
│  │  4e. Form image                   (M6 Image Former)              │   │
│  │  4f. Generate ground truth        (M7 Ground Truth Generator)    │   │
│  │  4g. Write output                 (M8 Dataset Writer)            │   │
│  │  4h. Report progress                                              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    5. VALIDATION                                         │
│  5a. Verify all expected files exist.                                   │
│  5b. Validate image properties (dimensions, bit depth, format).        │
│  5c. Run regression checks (if reference available).                   │
│  5d. Generate validation report.                                        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    6. DATASET FINALIZATION                               │
│  Finalize dataset index. Write summary statistics.                      │
│  Clean up temporary files.                                              │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    7. EXPORT                                             │
│  Generate dataset archive (optional).                                   │
│  Write completion manifest.                                             │
│  Log final statistics.                                                  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    8. SHUTDOWN                                           │
│  Release resources. Close log files.                                    │
│  Report exit code (0 = success).                                        │
└─────────────────────────────────────────────────────────────────────────┘
```

**Engineering Decision:** The pipeline is explicitly sequential within a job. Parallelism is achieved by running multiple independent jobs concurrently, not by parallelizing within a job.

---

## 2. State Transitions

Each job in the batch progresses through these states:

```
PENDING → RUNNING → COMPLETED
                  → FAILED (with retry)
                  → CACHED (if result already exists)
```

| State | Meaning | Transitions To |
|---|---|---|
| **PENDING** | Waiting to be executed | RUNNING |
| **RUNNING** | Pipeline executing | COMPLETED, FAILED |
| **COMPLETED** | Output files written successfully | — |
| **FAILED** | Non-recoverable error encountered | (dead) |
| **CACHED** | Output exists and cache valid | COMPLETED |

---

## 3. Lifecycle Responsibility

| Phase | Responsible | Notes |
|---|---|---|
| 0. Startup | Runtime entry point (CLI) | Minimal logic |
| 1. Config load | M9 Config Parser | Error → abort before any work |
| 2. Resource allocation | Orchestration layer | Validates environment |
| 3. Job expansion | Job Manager (orch_job) | Deterministic |
| 4. Pipeline execution | Pipeline Controller (orch_pipeline) | Per-job |
| 5. Validation | Validation subsystem | After all jobs complete |
| 6. Dataset finalization | Dataset Writer | Index, statistics |
| 7. Export | Dataset Writer | Optional archiving |
| 8. Shutdown | Runtime entry point | Cleanup |

---

## 4. Execution Guarantees

| Guarantee | Description |
|---|---|
| **At-most-once** | Each job is executed once. If a job fails, it is not retried automatically (re-run from last checkpoint manually). |
| **No side effects between jobs** | Jobs do not share state, files, or RNG state. Each job's output is independently verifiable. |
| **Deterministic per seed** | Same config + same seed → same output, regardless of execution order or parallelism. |
| **Isolated failures** | A single job failure does not affect other running or pending jobs. |

---

## 5. Phases and Their Time Budgets

| Phase | Fraction of Total Time | Scaling |
|---|---|---|
| Config load + validation | < 1% | O(1) |
| Job expansion | < 1% | O(N_jobs) |
| Pipeline execution (per image) | > 95% | O(M × N × N_layers) |
| Validation | 1–5% | O(N_jobs) |
| Dataset finalization | < 1% | O(N_jobs) |

**Inference:** Optimization effort should focus entirely on pipeline execution per image (Phase 4). All other phases are negligible in total runtime.

---

## Sources

- [R1] I. Foster, *Designing and Building Parallel Programs*, Addison-Wesley, 1995.
- [R5] J. K. Ousterhout, *A Philosophy of Software Design*, Yaknyam Press, 2018.
- Phase 4.1, Document 03 — Module decomposition.
- Phase 4.2, Documents 02, 04 — Module interfaces, API contracts.
