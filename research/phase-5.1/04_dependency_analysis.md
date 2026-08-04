# Dependency Analysis

**Research Phase:** 5.1
**Document:** 04_dependency_analysis.md
**Date:** 2026-07-30

---

## 1. Dependency Graph

```
                     ┌──────────┐
                     │ Stage 0  │
                     │ Found.   │
                     └────┬─────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │ geo_rstr │   │ img_io   │   │ config   │
    │ (1.1)    │   │ (0.4)    │   │ (2.2)    │
    └────┬─────┘   └────┬─────┘   └────┬─────┘
         │              │               │
         ▼              │               │
    ┌──────────┐        │               │
    │ geo_proc │        │               │
    │ (1.2)    │        │               │
    └────┬─────┘        │               │
         │              │               │
         ▼              │               │
    ┌──────────┐        │               │
    │ geo_var  │        │               │
    │ (1.3)    │        │               │
    └──┬───────┘        │               │
       │                │               │
       │                │               │
  ┌────┴────┐           │               │
  │         │           │               │
  ▼         ▼           │               │
┌────┐  ┌────────┐     │               │
│phys│  │  d_gt  │     │               │
│sig │  │  (2.1) │     │               │
│1.4 │  └────────┘     │               │
└─┬──┘                 │               │
  │                    │               │
  ▼                    │               │
┌──────┐              │               │
│phys  │              │               │
│degr  │              │               │
│(1.5) │              │               │
└─┬────┘              │               │
  │                   │               │
  ▼                   │               │
┌──────┐             │               │
│phys  │             │               │
│form  │             │               │
│(1.6) │             │               │
└─┬────┘             │               │
  │                  │               │
  ▼                  ▼               │
┌──────┐        ┌──────────┐        │
│writer│        │  orch    │        │
│(1.7) │◄───────│ pipeline │        │
└──────┘        │ (1.8)    │        │
                └────┬─────┘        │
                     │              │
                     ▼              ▼
                ┌──────────┐   ┌──────────┐
                │ orch_job │◄──│ config   │
                │ (2.3)    │   │ (2.2)    │
                └────┬─────┘   └──────────┘
                     │
                     ▼
                ┌──────────┐
                │  CLI     │
                │ (2.4)    │
                └──────────┘

Parallel branches:
  ┌── geo_var (1.3) ──┬── phys_sig (1.4) → phys_degr (1.5) → phys_form (1.6)
  │                    │
  │                    └── d_gt (2.1)
  │
  └── img_io (0.4) ── writer (1.7)
```

---

## 2. Critical Path Analysis

| Path | Work Packages | Duration on Critical Path | Critical? |
|---|---|---|---|
| 0.1→0.2→1.1→1.2→1.3→1.4→1.5→1.6→1.7→1.8 | 10 | 24 weeks (weeks 1–14 if parallelized) | **✅ CRITICAL** |
| 0.1→0.4→1.7 | 3 | 3 weeks | No (parallel to critical) |
| 0.1→0.3→1.3 | 3 | 3 weeks | No (parallel to critical) |
| 1.3→2.1 | 2 | 3 weeks | No (post-M1) |
| 1.8→2.2→2.3→2.4 | 4 | 7 weeks | No (Stage 2) |

**Critical path:** Foundation (0.1, 0.2) → Geometry (1.1, 1.2, 1.3) → Physics (1.4, 1.5, 1.6) → Dataset (1.7) → Orchestration (1.8)

**Critical path duration:** 24 weeks of sequential work, compressed to ~14 weeks wall clock with parallelization.

---

## 3. Parallel Development Opportunities

| Opportunity | Description | Speedup | Risk |
|---|---|---|---|
| **Geometry + Image I/O** | WP 1.1–1.3 and WP 0.4 proceed in parallel after M0 | N/A (already parallel) | None |
| **config_parser independent** | WP 2.2 can start at M0 (only needs 0.1) | Brings config readiness earlier | Low — config data model is frozen |
| **Ground truth parallel to physics** | WP 2.1 depends on 1.3, same as 1.4 | WP 2.1 runs concurrently with 1.4–1.6 | None (no data sharing) |
| **Production WPs in parallel** | 3.1, 3.2, 3.3 can be developed concurrently after M5 | Compresses Stage 3 by ~4 weeks | Low — independent enhancements |

---

## 4. Independent Modules (No Inter-Team Coordination)

| Module | Independent After | Can Develop Without |
|---|---|---|
| math_utils | M0 (week 1–3) | Everything (shared utility) |
| rng_utils | M0 (week 1–3) | Everything (shared utility) |
| image_io | M0 (week 1–3) | Everything (shared utility) |
| config_parser | M0 (week 1–3) | Everything (data model is frozen) |
| geo_raster | M0 | geo_process, physics, dataset |
| data_writer | M0 + image_io | Geometry, physics, orchestration |
| data_groundtruth | M1 (geo_variability) | Physics pipeline |
| geo_process | geo_raster | Physics, dataset |
| phys_signal | geo_variability | Dataset, orchestration |
| orch_pipeline | All core modules | Batch, production features |

---

## 5. High-Risk Dependencies

| Dependency | Risk | Why | Mitigation |
|---|---|---|---|
| geo_process → geo_raster | **Medium** | geo_process is the most complex module; any delay propagates to entire pipeline | Start geo_raster early; prototype geo_process core logic in week 2–3 |
| phys_signal → geo_variability (I4) | **Medium** | I4 is the certified boundary; both sides must be implemented and tested together | Implement I4 test harness first; test with synthetic data before real interface |
| orch_pipeline → all modules | **Medium** | Integration is the last step; integration bugs are expensive | Continuous integration from M0; test each module independently; module stubs for early integration |
| geo_variability → rng_utils | **Low/Medium** | LER determinism depends on correct RNG implementation | Unit test rng_utils with known seed → known output before geo_variability starts |

---

## 6. Recommended Development Team Structure

| Team | Modules | Size | Start Week |
|---|---|---|---|
| **Team A: Foundation** | math_utils, rng_utils, image_io, units, config_parser, testing framework | 1–2 devs | Week 1 |
| **Team B: Geometry** | geo_raster, geo_process, geo_variability, data_groundtruth | 2 devs | Week 3 |
| **Team C: Physics** | phys_signal, phys_degrade, phys_formation | 1–2 devs | Week 8 |
| **Team D: Integration** | data_writer, orch_pipeline, orch_job, CLI, validation, caching, parallel, checkpoint | 1–2 devs | Week 10 |

**Engineering Decision:** A 4-team structure maximizes parallelism while keeping communication overhead manageable. Teams B and D start sequentially after A; Teams C and D start after critical dependencies resolve.

---

## Sources

- [I6] F. Brooks, *The Mythical Man-Month*, 2nd ed. Addison-Wesley, 1995.
- [I7] E. Yourdon, *Death March*, 2nd ed. Prentice Hall, 2003.
- Phase 4.2 — Interface contracts (frozen, enabling independent module development).
- Phase 4.5 — Final certification (module readiness assessment).
