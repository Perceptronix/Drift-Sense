# Implementation Milestones

**Research Phase:** 5.1
**Document:** 03_implementation_milestones.md
**Date:** 2026-07-30

---

## 1. Milestone Map

```
Week:  0    3    7    12   14   17   22   30   36
       |    |    |    |    |    |    |    |    |
       S0   M0   M1   M2   M3   M4   M5   M6   M7
       ↑    ↑    ↑    ↑    ↑    ↑    ↑    ↑    ↑
       |    |    |    |    |    |    |    |    |
      Start  |    |    |    |    |    |    |  Final Release
            Fndn  |    |    |    |    |    Production
                 Geom   |    |    |    Release
                       Phys   |    |    |
                             E2E  |    |
                                GT   |
                                    Batch
```

---

## 2. Milestone Descriptions

### 2.1 M0: Foundation Complete (Week 3)

| Aspect | Specification |
|---|---|
| **Objective** | Core utility libraries are tested and frozen |
| **Modules implemented** | math_utils, rng_utils, image_io, units |
| **Success criteria** | All utility functions pass unit tests; RNG produces deterministic sequences from fixed seeds |
| **Exit criteria** | All 4 modules merged to main; test coverage > 80%; `pytest` discovers all tests |
| **Expected output** | Test reports; no user-facing functionality yet |

**Work packages:** 0.1–0.6

### 2.2 M1: Geometry Pipeline (Week 7)

| Aspect | Specification |
|---|---|
| **Objective** | Geometry Engine produces variable height fields from GDSII input |
| **Modules implemented** | geo_raster (M1), geo_process (M2), geo_variability (M3) |
| **Success criteria** | All 10 structure types produce correct HeightField and MaterialMap; LER 3σ matches configuration within tolerance; overlay shift verified |
| **Exit criteria** | Geometry unit tests pass for all structure types; known GDSII + seed → known HeightField |
| **Expected output** | HeightField, MaterialMap (NumPy arrays on disk for inspection) |

**Work packages:** 1.1–1.3

### 2.3 M2: Physics Pipeline (Week 12)

| Aspect | Specification |
|---|---|
| **Objective** | Physics Engine produces SEM images from height field input |
| **Modules implemented** | phys_signal (M4), phys_degrade (M5), phys_formation (M6) |
| **Success criteria** | SE/BSE yields match expected values for test structures; PSF blur measurable; noise statistics match Poisson/Gaussian; digitization correct |
| **Exit criteria** | Physics unit tests pass; I4 interface test (geometry output → physics test harness) passes |
| **Expected output** | SEMImage (TIFF) from known HeightField |

**Work packages:** 1.4–1.6

### 2.4 M3: Single-Image Pipeline (Week 14)

| Aspect | Specification |
|---|---|
| **Objective** | Complete end-to-end pipeline: config → SEM image → file output |
| **Modules implemented** | All Stage 1 modules (M1–M8) + orch_pipeline |
| **Success criteria** | Pipeline runs from config to image file; regression test passes (fixed seed → known output hash); image visually plausible |
| **Exit criteria** | `run_pipeline(config)` produces valid TIFF; at least 5 structure types verified visually; pipeline timing recorded |
| **Expected output** | Single-image output file: `images/*.tiff`, `metadata/*_config.json`, `metadata/*_metadata.json` |

**Work packages:** 1.7–1.8

### 2.5 M4: Ground Truth (Week 17)

| Aspect | Specification |
|---|---|
| **Objective** | Ground truth labels for all structure types |
| **Modules implemented** | data_groundtruth (M7) |
| **Success criteria** | CD values accurate within 0.1 nm; edge positions match height field; contours extract correctly for all 10 structure types; material segmentation matches material map |
| **Exit criteria** | Ground truth unit tests pass for all structure types; CD accuracy regression test |
| **Expected output** | Full per-sample directory: image + GT + config + metadata |

**Work packages:** 2.1

### 2.6 M5: Batch Execution (Week 22)

| Aspect | Specification |
|---|---|
| **Objective** | Multi-image dataset generation with config management |
| **Modules implemented** | config_parser (M9), orch_job (M10 batch), CLI, validation L1–L3, self-check |
| **Success criteria** | Batch of 100 images generates correctly; dataset index valid; validation suite L1–L3 passes; self-check passes; progress reported in real time |
| **Exit criteria** | `semicon-sim batch --config example.yml` produces full dataset directory tree; CLI `--self-check` passes |
| **Expected output** | Complete dataset directory: 100 images + GT + configs + metadata + index + splits |

**Work packages:** 2.2–2.6

### 2.7 M6: Production Release (Week 30)

| Aspect | Specification |
|---|---|
| **Objective** | Production-ready system with caching, parallel execution, and checkpoint |
| **Modules implemented** | caching (WP 3.1), worker pool (3.2), checkpoint (3.3), regression L4–L5 (3.4) |
| **Success criteria** | Cache accelerates repeated structures (>2× speedup); parallel batch achieves near-linear speedup; checkpoint resume works after mid-batch kill; regression L4–L5 passes |
| **Exit criteria** | 1000-image batch completes with 4 workers; cache hit rate > 50% for repeated structures; resume test passes |
| **Expected output** | Production-quality system performance |

**Work packages:** 3.1–3.4

### 2.8 M7: Final Release (Week 36)

| Aspect | Specification |
|---|---|
| **Objective** | Fully documented, packaged, distributable system |
| **Modules implemented** | Documentation (3.5), distribution packaging (3.6), performance profiling (3.7) |
| **Success criteria** | API docs published; user guide written; `pip install .` in fresh environment works; all 160 tests pass; per-image time < 3 s at 1024×1024 |
| **Exit criteria** | All gates L0–L5 passed; acceptance test suite passes; performance targets met |
| **Expected output** | pip-installable package; complete documentation; validated dataset |

**Work packages:** 3.5–3.7

---

## 3. Milestone Dependency Table

| Milestone | Depends On | Work Packages | Week |
|---|---|---|---|
| M0: Foundation | None | 0.1–0.6 | 3 |
| M1: Geometry | M0 | 1.1–1.3 | 7 |
| M2: Physics | M1 (I4) | 1.4–1.6 | 12 |
| M3: Single-Image | M2 + data_writer (1.7) | 1.7–1.8 | 14 |
| M4: Ground Truth | M1 (I7) | 2.1 | 17 |
| M5: Batch | M3 + M4 + config | 2.2–2.6 | 22 |
| M6: Production | M5 | 3.1–3.4 | 30 |
| M7: Final | M6 | 3.5–3.7 | 36 |

---

## 4. Incremental Validation Strategy

Each milestone is a **working, testable increment**:

```
M0 → M1 → M2 → M3 → M4 → M5 → M6 → M7
│    │    │    │    │    │    │    │
│    │    │    │    │    │    │    └─ Full production system
│    │    │    │    │    │    └─ Production features
│    │    │    │    │    └─ Batch execution
│    │    │    │    └─ Ground truth labels
│    │    │    └─ End-to-end: config → image
│    │    └─ SEM image from height field
│    └─ Variable geometry from GDSII
└─ Reusable utilities
```

**Key insight:** Every milestone produces something visible or measurable. No milestone is "architecture only" or "documentation only" — each milestone delivers functional progress.

---

## Sources

- [I1] P. Rook, "Controlling Software Projects," *Software Engineering Journal*, 1986.
- [I5] T. Gilb, *Competitive Engineering: A Handbook for Systems Engineering, Requirements Engineering, and Software Engineering Using Planguage*, Addison-Wesley, 2005.
- Phase 4.5, Document 08 — Final certification (implementation order, effort estimates).
