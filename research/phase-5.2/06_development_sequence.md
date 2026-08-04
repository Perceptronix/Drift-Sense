# Development Sequence

**Research Phase:** 5.2
**Document:** 06_development_sequence.md
**Date:** 2026-07-30

---

## 1. Sequence Overview

The Geometry Engine is developed in 8 sequential steps. Each step is independently testable and gates the next:

```
Step 1: Toolchain + scaffold    (Week 0–0.5)
Step 2: gdsii_reader           (Week 0.5–1)
Step 3: polygon_rasterizer     (Week 1–2)
Step 4: mask_builder → I1      (Week 2–3)
Step 5: process internals → I2 (Week 3–8)
Step 6: corner_rounding + assemble (Week 8–9)
Step 7: variability → I3       (Week 9–12)
Step 8: validation suite       (Week 12–13)
```

*Timeline matches WBS packages 1.1–1.3 (Phase 5.1): geo_raster 3 wks, geo_process 5 wks, geo_variability 3 wks, plus validation.*

---

## 2. Step-by-Step Specification

### Step 1: Toolchain & Scaffold

| Aspect | Specification |
|---|---|
| **Objective** | Reproducible dev environment and package skeleton |
| **Dependencies** | None (Phase 5.1 environment frozen) |
| **Deliverables** | `pyproject.toml` with deps, `src/semicon/geometry/` skeleton, `tests/` scaffold, `.pre-commit-config.yaml`, CI workflow, `conftest.py` |
| **Unit tests** | Smoke: `import semicon.geometry` succeeds |
| **Expected output** | `pip install -e .` works; `pytest` discovers 0 tests |
| **Completion criteria** | Green CI on empty scaffold; black/ruff/mypy clean on scaffold |

### Step 2: gdsii_reader

| Aspect | Specification |
|---|---|
| **Objective** | Read + flatten GDSII into polygon lists (nm) |
| **Dependencies** | Step 1; gdspy; foundation.units |
| **Deliverables** | `_raster/gdsii_reader.py`; `read_layer(gdsii_path, layer) → list[Polygon]` |
| **Unit tests** | Test GDSII fixtures: single polygon, multi-layer, SREF, AREF, PATH→polygon conversion; missing file/layer errors; empty layer |
| **Expected output** | Correct polygon vertex arrays in nm for each fixture |
| **Completion criteria** | All parser tests pass; SREF/AREF flattening verified against known geometry |

### Step 3: polygon_rasterizer

| Aspect | Specification |
|---|---|
| **Objective** | Anti-aliased polygon → coverage map |
| **Dependencies** | Step 1; numpy; foundation.math_utils |
| **Deliverables** | `_raster/polygon_rasterizer.py`; `rasterize_polygons(...) → float32 coverage` |
| **Unit tests** | Unit square → exact coverage; rotated square; concave polygon (L-shape); hole (even-odd); 45° line edge coverage monotonic; translation invariance |
| **Property tests** | Hypothesis: random polygons → Σcoverage = area/pixel_area ± 1 px²; coverage ∈ [0,1] |
| **Expected output** | Coverage maps; property tests green |
| **Completion criteria** | Golden coverage tests + property tests pass |

### Step 4: mask_builder → I1 Complete

| Aspect | Specification |
|---|---|
| **Objective** | Public `rasterize()` satisfying I1 |
| **Dependencies** | Steps 2–3 |
| **Deliverables** | `_raster/mask_builder.py`; `raster.py` (public); `PixelMask` dataclass in foundation.datatypes |
| **Unit tests** | Threshold behavior (coverage 0.49 → 0, 0.51 → 1); dimension validation; FOV centering; values ∈ {0,1} |
| **Interface tests (L2)** | `test_i1_i2_i3.py`: rasterize output consumed by a stub process module — dimensions, dtype, pixel_size match |
| **Expected output** | PixelMask arrays for all 10 fixture GDSII files |
| **Completion criteria** | **M1 milestone (Week 3):** I1 contract verified; golden masks committed |

### Step 5: Process Internals → I2 Draft

| Aspect | Specification |
|---|---|
| **Objective** | Deposition, litho, etch, CMP, heightfield assembly for all structure types |
| **Dependencies** | Step 4 (PixelMask); scipy; scikit-image; foundation |
| **Deliverables** | `_process/*.py`; `process.py` (public); HeightField/MaterialMap dataclasses |
| **Unit tests** | LayerStack plan resolution; deposition conformal thickness; litho CD bias; etch trapezoid top/bottom CD; CMP planar top + over-polish; each structure type golden profile |
| **Scientific tests (L4, draft)** | Trapezoid angle recovered within 0.1°; conformal wall thickness ± 0.1 nm |
| **Expected output** | HeightField_det + MaterialMap_det for all 10 structure types |
| **Completion criteria** | I2 postconditions verified; golden profiles for 10 structure types committed |

### Step 6: Corner Rounding + Assembly

| Aspect | Specification |
|---|---|
| **Objective** | Corner fillets; final I2 assembly through heightfield_gen |
| **Dependencies** | Step 5 |
| **Deliverables** | `_process/corner_rounding.py`; `heightfield_gen.py` completes ProcessPlan execution |
| **Unit tests** | Top/bottom corner radius within 0.2 nm; profile continuity (no spikes); heightfield_gen orchestration order |
| **Expected output** | Realistic fin/gate/contact profiles with rounded corners |
| **Completion criteria** | Full I2 contract; **intermediate gate Week 9** |

### Step 7: Variability → I3 Complete

| Aspect | Specification |
|---|---|
| **Objective** | LER, CDU, overlay, variability application |
| **Dependencies** | Step 6; foundation.rng_utils; scipy.fft |
| **Deliverables** | `_variability/*.py`; `variability.py` (public); VariabilityRecord dataclass |
| **Unit tests** | Edge detector edge positions; LER stats (3σ ± 0.3 nm, ξ ± 10%, ρ ± 0.05, mean ≈ 0); overlay shift ± 0.1 nm; CDU batch spread = σ ± 0.1 nm; application order (CDU→LER→SWA→overlay) |
| **Determinism tests** | Same seed → identical HeightField_var (bitwise); different seed → different |
| **Expected output** | Variable height fields for all structure types; VariabilityRecord |
| **Completion criteria** | I3 contract verified; **M1 completion (Week 12–13)** |

### Step 8: Full Validation Suite

| Aspect | Specification |
|---|---|
| **Objective** | Complete L1–L4 validation for the Geometry Engine |
| **Dependencies** | Steps 1–7 |
| **Deliverables** | `tests/module/`, `tests/interface/`, `tests/pipeline/`, `tests/scientific/`; golden reference hashes; regression script |
| **Validation** | L1 module contracts; L2 interface pairs (I1, I2, I3); L3 pipeline GDSII→HeightField_var; L4 scientific (LER PSD fit, CD accuracy, trapezoid fidelity) |
| **Expected output** | Full validation report; regression hash baseline committed |
| **Completion criteria** | **Geometry Engine certified ready for I4 integration (Week 13)** |

---

## 3. Dependency Table

| Step | Requires | Provides | Gate |
|---|---|---|---|
| 1 | — | Scaffold, toolchain | CI green |
| 2 | 1 | Polygon extraction | Parser tests |
| 3 | 1 | Coverage rasterization | Golden + property |
| 4 | 2, 3 | **I1 PixelMask** | M1 |
| 5 | 4 | **I2 HeightField_det** | Intermediate |
| 6 | 5 | I2 complete (corners) | Intermediate |
| 7 | 6 | **I3 HeightField_var** | M1 complete |
| 8 | 1–7 | Validation suite | L1–L4 |

---

## 4. Parallelization Within the Sequence

| Opportunity | Description |
|---|---|
| Steps 2–3 can start concurrently | gdsii_reader and polygon_rasterizer have no mutual dependency (only both feed Step 4) |
| Structure-type golden tests in Step 5 | Can be written in parallel by a second developer as process modules complete |
| Validation suite (Step 8) scaffold | Can begin at Step 4 (module-level tests for raster) |

---

## 5. Completion Criteria Summary

| Step | Completion = | Deliverable |
|---|---|---|
| 1 | `pip install -e .` + green CI | Scaffold |
| 2 | Parser tests green | Polygon extraction |
| 3 | Golden + property green | Coverage rasterizer |
| 4 | **I1 verified** | PixelMask |
| 5 | Golden profiles × 10 | HeightField_det + MaterialMap_det |
| 6 | I2 verified | Corner-rounded profiles |
| 7 | **I3 verified** | HeightField_var + VariabilityRecord |
| 8 | **L1–L4 pass; hashes committed** | Certified Geometry Engine |

---

## Sources

- Phase 5.1, Document 02 — WBS packages 1.1–1.3.
- Phase 5.1, Document 03 — Milestones M1 (Geometry, Week 13).
- Phase 5.1, Document 05 — Validation gates L0–L4.
- [I8] S. McConnell, *Code Complete*, 2nd ed., 2004 (incremental development).
- [I2] B. Boehm, "A Spiral Model of Software Development," 1988 (risk-driven ordering).
