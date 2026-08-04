# Phase 4.3 Executive Summary: Runtime Execution & Orchestration

**SEMICON 2026 Research Repository**
**Applied Materials**
**Date:** 2026-07-30
**Classification:** Research-Only (Phase 4.3)

---

## Purpose

This phase answers: **"How should the simulator execute efficiently, reproducibly, and reliably from configuration to dataset generation?"**

Phases 4.1 and 4.2 defined the **architecture** and **contracts**. This phase defines **runtime orchestration** — how the system actually runs: pipeline lifecycle, scheduling, parallelism, reproducibility, checkpointing, monitoring, and caching.

---

## Key Findings

### 1. Runtime Model Summary

| Aspect | Recommendation |
|---|---|
| **Execution model** | Single-process pipeline for one image; multiprocessing for batch |
| **Scheduling** | Sequential within a job; parallel across independent jobs |
| **Parallelism** | Independent samples only (embarrassingly parallel geometry + physics) |
| **Reproducibility** | Config snapshot + seed manager + environment record for every image |
| **Checkpointing** | Per-structure checkpoint file; restart from last completed structure |
| **Monitoring** | Structured JSON logging + progress bar + resource telemetry |
| **Caching** | Height field caching enabled when variability is disabled; invalidated on config change |

### 2. Execution Lifecycle

```
START → Init → Config Load → Validate → Resource Alloc → [Pipeline per structure] → Dataset Assembly → Validate → Export → END
                                ↑_______________batch loop_______________↓
```

### 3. Scheduling Model

| Mode | Use Case | Execution | Scale |
|---|---|---|---|
| **Single** | Development, debugging | 1 structure, 1 image | 1 image |
| **Batch** | Dataset generation | N structures, 1–R images each | 10–10⁵ images |
| **Sweep** | Parameter studies | 1 structure, parameter grid | 10²–10⁵ images |
| **Continuous** | Production | Read config stream, generate | Unlimited |

### 4. Reproducibility: The Seed Manager

The seed manager ensures deterministic execution:

```
Master Seed (from config)
  → Per-structure seeds: seed_m = hash(master_seed, structure_index)
    → Per-realization seeds: seed_r = hash(seed_m, realization_index)
      → Per-stage seeds: seed_s = hash(seed_r, stage_id) + stage_offset
```

**Inference:** The hierarchical seed scheme guarantees that changing any parameter (adding a structure, changing a seed, modifying any config value) changes downstream seeds, preventing accidental correlation between runs.

### 5. Parallelism Policy

| Resource | Parallelism Strategy | Safe? |
|---|---|---|
| CPU (single structure) | None — single sequential pipeline | ✅ Always |
| CPU (batch) | Multiprocessing: one process per structure | ✅ (no shared state) |
| GPU | Per-pixel operations in physics only; no GPU across structures | ⚠️ Limited applicability |
| Memory | Each process uses independent 50–500 MB | ✅ Predictable |

---

## Phase 4.4 Knowledge Required

Phase 4.4 must answer:

1. **Dataset packaging format:** How are generated images organized, annotated, and distributed — file naming, directory layout, index format, ground-truth encoding?

2. **Metadata and annotation schema:** What metadata must accompany each dataset — structure parameters, physics parameters, ground-truth labels, data provenance?

3. **Output distribution:** How are datasets packaged for downstream consumption — single archive, HDF5, directory tree, cloud storage?

4. **Final integration audit:** Is the complete system — architecture, contracts, execution, dataset packaging — consistent and implementation-ready?

---

## Sources

- [R1] I. Foster, *Designing and Building Parallel Programs*, Addison-Wesley, 1995.
- [R2] M. Snir et al., *MPI: The Complete Reference*, MIT Press, 1998.
- [R3] B. Wilkinson, M. Allen, *Parallel Programming*, 2nd ed. Prentice Hall, 2005.
- [R5] J. K. Ousterhout, *A Philosophy of Software Design*, Yaknyam Press, 2018.
- Phase 4.1 — System architecture.
- Phase 4.2 — Interface contracts, data objects.
