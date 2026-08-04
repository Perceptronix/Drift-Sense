# Job Scheduling Strategy

**Research Phase:** 4.3
**Document:** 03_job_scheduling_strategy.md
**Date:** 2026-07-30

---

## 1. Scheduling Models Compared

| Model | Description | Complexity | Overhead | Suitability | Verdict |
|---|---|---|---|---|---|
| **Sequential (single-process)** | Process jobs one at a time | Minimal | None | Development; <100 images | **Default mode** |
| **Process pool (static)** | Pre-allocate N workers; assign jobs | Low | Low | 100–10⁵ images | **Recommended for batch** |
| **Process pool (dynamic)** | Workers request next job when idle | Moderate | Low | Any size; variable runtimes | **Recommended for sweeps** |
| **DAG scheduler** | Multi-stage pipeline with dependencies | High | High | Not needed (no pipeline branches) | Rejected |
| **Cluster (HPC)** | Distributed across nodes | Very high | High | >10⁶ images | Future consideration |
| **Cloud/container** | Orchestrated containers (Kubernetes) | Very high | High | Production deployment | Future consideration |

**Engineering Decision:** Sequential for single-image; static process pool for batch; dynamic process pool for parameter sweeps.

---

## 2. Scheduling Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                          JOB MANAGER (orch_job)                        │
│                                                                        │
│  Config → [JobExpander] → JobList → [Scheduler] → Worker Pool         │
│                                   │          ┌─────────┐              │
│                                   │          │ Worker1 │              │
│                                   ├──────────┤ Worker2 │ ← run pipeline│
│                                   │          │ Worker3 │              │
│                                   │          └─────────┘              │
│  Results ← [ResultAggregator] ←──────────────┘                       │
└────────────────────────────────────────────────────────────────────────┘
```

**Engineering Decision:** The job manager owns scheduling. Workers are independent processes that execute a single pipeline run. The manager does not communicate with workers during execution (no RPC, no shared state).

---

## 3. Job Expansion

### 3.1 From Batch Configuration to Jobs

```
Batch Config:
  structures:
    - type: "iso_line"
      repetitions: 1000
      parameters: {cd_nm: 30, height_nm: 50}
    - type: "iso_line"
      repetitions: 1000
      parameters: {cd_nm: 50, height_nm: 100}

Job Expander Output (JobList):
  Job 0000: {structure_index: 0, realization: 0, seed: 0x7a3b...}
  Job 0001: {structure_index: 0, realization: 1, seed: 0x9c1f...}
  ...
  Job 1999: {structure_index: 1, realization: 999, seed: 0xd4e8...}
```

### 3.2 Seed Assignment

Each job receives a deterministic seed derived from the master seed, structure index, and realization index (see Document 05).

### 3.3 Job Manifest

The expanded job list is written to a JSON manifest file:

```
output_directory/
├── job_manifest.json            ← All jobs: {id, structure, params, seed}
├── job_manifest_schema.json     ← Schema for the manifest
└── images/                      ← Output images (created during execution)
```

**Inference:** The manifest is the complete record of what was requested. It is written before any execution begins, providing a fixed reference for the run.

---

## 4. Execution Modes

| Mode | Config Structure | Worker Count | Typical Use |
|---|---|---|---|
| **single** | One structure, one image | 1 | Debugging, validation |
| **batch** | One or more structures, R repetitions each | auto = min(N_structures, N_cores) | Dataset generation |
| **sweep** | One structure with parameter arrays | auto | Parameter studies |
| **list** | Explicit job list file | auto | Production runs |

### 4.1 Batch Mode

```
for structure in config.structures:
    for r in range(structure.repetitions):
        job = {pipeline_id, structure_params, seed}
add job to pool
```

### 4.2 Sweep Mode

```
for cd in [20, 30, 40, 50]:
    for angle in [85, 86, 87, 88]:
        for ler in [1.0, 2.0, 3.0]:
            job = {type: "iso_line", cd, angle, ler}
add job to pool
```

---

## 5. Worker Pool Configuration

| Parameter | Default | Range | Description |
|---|---|---|---|
| **worker_count** | `min(4, cpu_count())` | 1–cpu_count() | Number of parallel workers |
| **batch_size** | None (full list) | — | Jobs assigned to workers on startup |
| **dynamic_poll_interval_s** | 1.0 | 0.1–10 | Poll interval for dynamic pool |
| **max_retries** | 0 | 0–3 | Max retries per failed job |
| **fail_fast** | False | {True, False} | Abort on first failure (batch mode) |

---

## 6. Scheduling Performance

| N_images | Sequential | 4 Workers | 16 Workers | Notes |
|---|---|---|---|---|
| 1 | 1× | — | — | Single image |
| 100 | 100× | ~25× | ~7× | Batch; near-linear scaling |
| 10,000 | 10000× | ~2500× | ~625× | Batch; memory-bound on 16W |
| 100,000 | — | ~25000× | ~6250× | Requires large memory |

**Inference:** Linear speedup up to N_workers = N_cores. No hyperthreading benefit (CPU-bound per-pipeline operations are mostly memory bandwidth).

---

## Sources

- [R1] I. Foster, *Designing and Building Parallel Programs*, Addison-Wesley, 1995.
- [R3] B. Wilkinson, M. Allen, *Parallel Programming*, 2nd ed. Prentice Hall, 2005.
- [R4] M. J. Quinn, *Parallel Programming in C with MPI and OpenMP*, McGraw-Hill, 2003.
- Phase 4.2, Document 05 — Configuration model.
