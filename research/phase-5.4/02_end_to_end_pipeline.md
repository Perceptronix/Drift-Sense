# End-to-End Pipeline Integration

**Research Phase:** 5.4
**Document:** 02_end_to_end_pipeline.md
**Date:** 2026-07-30

---

## 1. Pipeline Overview

The complete simulator executes 10 stages per image, passing immutable data objects across 8 certified interfaces (I1–I8):

```
┌─────────────────────────────────────────────────────────────────────┐
│                       MASTER PIPELINE (orch_pipeline)               │
│                                                                     │
│  Stage 0: Config Load      D1 Config (validated, defaults applied)  │
│      │                                                              │
│  Stage 1: Structure Gen    [M2] PixelMask (D3)           ── I1 ──►  │
│      │                    GDSII → mask                           │
│  Stage 2: Process Model    [M2] HeightField_det + MaterialMap_det  │
│      │                    mask → geometry              ── I2 ──►  │
│  Stage 3: Variability      [M3] HeightField_var + MaterialMap_var  │
│      │                    + variability                 ── I3 ──►  │
│  Stage 4: Signal Gen       [M4] YieldMaps               ── I4 ──►  │
│      │                    geometry → SE/BSE yields               │
│  Stage 5: Degrade          [M5] YieldMaps_degraded      ── I5 ──►  │
│      │                    PSF + noise                             │
│  Stage 6: Image Form       [M6] SEMImage (D8)           ── I6 ──►  │
│      │                    yields → digitized image                │
│  Stage 7: Ground Truth     [M7] GroundTruth (D9)  (parallel)       │
│      │                    geometry → labels              ── I7 ──►  │
│  Stage 8: Metadata         [D10] Metadata (config + seeds +        │
│      │                           versions + timing)               │
│  Stage 9: Packaging        [M8] Files + dataset index    ── I8 ──►  │
│                            canonical dataset layout               │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Stage-by-Stage Specification

### Stage 0: Configuration Load

| Aspect | Specification |
|---|---|
| **Inputs** | YAML config path; CLI overrides |
| **Outputs** | `Config` (D1) — fully resolved, validated |
| **Module** | config_parser (M9) |
| **Frozen refs** | Phase 4.2 D1; Phase 4.3 config section |
| **Validation** | Schema validation, default resolution, cross-field checks; failure → exit with clear error |
| **Determinism** | Config snapshot serialized verbatim into metadata (later stage) |

### Stage 1: Structure Generation

| Aspect | Specification |
|---|---|
| **Inputs** | Config.structure, seed chain |
| **Outputs** | `PixelMask` (D3, M×N uint8) |
| **Module** | geo_raster (M1) via `rasterize()` |
| **Interface** | **I1** — frozen (Phase 4.2) |
| **Validation** | Dimensions, pixel_size, values ∈ {0,1}; structure library resolution |
| **Frozen refs** | Phase 3.1; Phase 5.2 A1 |

### Stage 2: Process Model

| Aspect | Specification |
|---|---|
| **Inputs** | PixelMask, LayerStack (D4), ProcessConfig |
| **Outputs** | `HeightField_det` (D5), `MaterialMap_det` (D6) |
| **Module** | geo_process (M2) via `build_geometry()` |
| **Interface** | **I2** — frozen |
| **Validation** | Dimensions, finite values, trapezoid invariant, material IDs |
| **Frozen refs** | Phase 3.2; Phase 5.2 A2–A6 |

### Stage 3: Variability

| Aspect | Specification |
|---|---|
| **Inputs** | HeightField_det, MaterialMap_det, VariabilityConfig, structure_seed |
| **Outputs** | `HeightField_var`, `MaterialMap_var`, `VariabilityRecord` |
| **Module** | geo_variability (M3) via `apply_variability()` |
| **Interface** | **I3** — frozen |
| **Validation** | LER stats, overlay shift, CDU spread; dimensions preserved |
| **Frozen refs** | Phase 3.3; Phase 5.2 A7–A9 |

### Stage 4: Signal Generation

| Aspect | Specification |
|---|---|
| **Inputs** | HeightField_var, MaterialMap_var, PhysicsConfig |
| **Outputs** | `YieldMaps` (D7: se_yield, bse_yield) |
| **Module** | phys_signal (M4) via `compute_yields()` |
| **Interface** | **I4** — the certified geometry↔physics boundary |
| **Validation** | Dimensions, finite, yield ∈ [0,10]; I4 compatibility test |
| **Frozen refs** | Phase 2.2/2.3; Phase 5.3 P1–P6 |

### Stage 5: Degradation

| Aspect | Specification |
|---|---|
| **Inputs** | YieldMaps, DegradationConfig, noise_seed |
| **Outputs** | `YieldMaps_degraded` |
| **Module** | phys_degrade (M5) via `degrade_yields()` |
| **Interface** | **I5** — frozen |
| **Validation** | PSF width, noise stats, clamped range |
| **Frozen refs** | Phase 2.4; Phase 5.3 P7–P9 |

### Stage 6: Image Formation

| Aspect | Specification |
|---|---|
| **Inputs** | YieldMaps_degraded, DetectorConfig |
| **Outputs** | `SEMImage` (D8), `FormationRecord` |
| **Module** | phys_formation (M6) via `form_image()` |
| **Interface** | **I6** — frozen |
| **Validation** | Bit depth, value range, saturation fraction |
| **Frozen refs** | Phase 2.5; Phase 5.3 P10 |

### Stage 7: Ground Truth (Parallel)

| Aspect | Specification |
|---|---|
| **Inputs** | HeightField_var, MaterialMap_var, GTConfig |
| **Outputs** | `GroundTruth` (D9) |
| **Module** | data_groundtruth (M7) |
| **Interface** | **I7** — frozen |
| **Parallelism** | Runs concurrently with Stages 4–6 (RD5: M4+M7 after M3) |
| **Validation** | CD accuracy, edge positions, contour integrity |
| **Frozen refs** | Phase 4.4 doc 04 |

### Stage 8: Metadata Assembly

| Aspect | Specification |
|---|---|
| **Inputs** | Config snapshot, seed chain, versions, timing records, warnings |
| **Outputs** | `Metadata` (D10) |
| **Module** | assembled by orch_pipeline from records |
| **Validation** | All mandatory fields present (Phase 4.4 doc 05) |
| **Frozen refs** | Phase 4.4 doc 05; Phase 4.3 RD7 |

### Stage 9: Dataset Packaging

| Aspect | Specification |
|---|---|
| **Inputs** | SEMImage, GroundTruth, Metadata, Config |
| **Outputs** | Files on disk + `FileList` + `DatasetIndexEntry` |
| **Module** | data_writer (M8) via `write_sample()` |
| **Interface** | **I8** — frozen |
| **Validation** | Valid TIFF/JSON; naming convention; index updated |
| **Frozen refs** | Phase 4.4 doc 02/03 |

---

## 3. Cross-Stage Data Invariants

| Invariant | Where Enforced | Frozen Ref |
|---|---|---|
| All array dimensions = M×N | Every module | Phase 4.2 |
| Same coordinate system (Row=Y, Col=X, top-left origin) | Every module | Phase 4.2 |
| Material IDs ∈ {0..6} | I2, I4, I7 | Phase 1 |
| float64 height fields (nm) | I2, I3, I4 | Phase 3.1 |
| yield ∈ [0, 10] | I4, I5 | Phase 2.2 |
| image values ∈ [0, 2^bits−1] | I6 | Phase 2.5 |
| No NaN/Inf anywhere | All stages | Phase 4.2 postconditions |

---

## 4. Module Communication Model

| Pattern | Decision | Reference |
|---|---|---|
| **Direct function calls** | Master controller calls each module's public function in sequence | Phase 4.1 AD4 |
| **Immutable data objects** | No module mutates another's output | Phase 4.1 AD5 |
| **Data-object handoff** | D-objects passed by value (or frozen reference) | Phase 4.2 D1–D10 |
| **No shared state** | No global mutable state; seeds and configs passed explicitly | Phase 4.3 RD4 |
| **Interface ownership** | Each producer validates its own output before return | Phase 4.2 |

---

## 5. Pipeline Validation Checks

| Check | At Stage | Method | Gate |
|---|---|---|---|
| Config validated | 0 | schema + cross-field | L1 |
| Postconditions I1–I3 | 1–3 | module validators | L1/L2 |
| Postconditions I4–I6 | 4–6 | module validators | L1/L2 |
| GT accuracy | 7 | CD ± 0.1 nm | L4 |
| Metadata complete | 8 | mandatory-field check | L1 |
| Files valid | 9 | TIFF/JSON round-trip | L1 |
| Determinism | all | SHA-256 repeat | L5 |

---

## Sources

- Phase 4.1 — Architecture (AD4, AD5, layers).
- Phase 4.2 — Interfaces I1–I8; data objects D1–D10.
- Phase 4.3 — Runtime (RD5, RD4).
- Phase 4.4 — Dataset spec (docs 02–05).
- Phase 5.2 — Geometry blueprint.
- Phase 5.3 — Physics blueprint.
- [S1] M. Fowler, *Patterns of Enterprise Application Architecture*, Addison-Wesley, 2002.
