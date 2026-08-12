# Phase 5.2 Final Report: Geometry Engine Implementation Blueprint

**SEMICON 2026 Research Repository**
**Applied Materials**
**Date:** 2026-07-30
**Classification:** Implementation-Planning

---

## Executive Summary

Phase 5.2 answers: **"How should the Geometry Engine be implemented from the first line of code to a fully validated module?"**

The certified Geometry Engine (Phase 3) is translated into a complete, frozen implementation blueprint: 8 internal modules, 5 libraries selected with alternatives and migration paths, 10 algorithm mappings (A1–A10) tied to frozen scientific specifications, a canonical source tree, an 8-step risk-driven development sequence, 5 test tiers, and a fully specified toolchain.

---

## 1. Key Results

### 1.1 Module Breakdown (Document 02)

| Public Module | Interface | Internal Modules |
|---|---|---|
| `geo_raster` | I1 | gdsii_reader, polygon_rasterizer, mask_builder |
| `geo_process` | I2 | layer_stack, deposition, lithography, etch, cmp, corner_rounding, heightfield_gen |
| `geo_variability` | I3 | edge_detector, ler_generator, overlay_engine, cdu_engine, variability_applier |

### 1.2 Library Selection (Document 03)

| Library | Role | Alternative(s) |
|---|---|---|
| **gdspy** | GDSII parsing | gdstk (migration path), python-gdsii, custom |
| **NumPy/SciPy** | Numerical core | — (non-negotiable) |
| **scikit-image** | Distance transform, contours | OpenCV (rejected: float32 breaks determinism) |
| **Pillow** | Image I/O (fixtures) | tifffile, imageio |

### 1.3 Algorithm Mapping (Document 04)

| # | Algorithm | Frozen Spec | Complexity |
|---|---|---|---|
| A1 | Edge-function supersampling rasterization | Phase 3.1, I1 | O(P·S²) |
| A2 | Ordered ProcessPlan height-field generation | Phase 3.2, I2 | O(M·N·steps) |
| A3 | Per-column trapezoid sidewall carving | Phase 3.2 | O(M·N) |
| A5 | Chebyshev isosurface conformal deposition | Phase 3.2 | O(M·N) |
| A6 | Clip + local-erosion CMP | Phase 3.2 | O(M·N) |
| A7 | 1D spectral-synthesis LER (exponential ACF) | Phase 3.3 | O(L log L) |
| A8 | Separable spline overlay translation | Phase 3.3 | O(M·N) |
| A9 | Edge-adjacent material update | Phase 1/3.1 | O(edge band) |

### 1.4 Development Sequence (Document 06)

| Step | Week | Deliverable | Gate |
|---|---|---|---|
| 1 | 0–0.5 | Scaffold + toolchain | CI green |
| 2 | 0.5–1 | gdsii_reader | Parser tests |
| 3 | 1–2 | polygon_rasterizer | Golden + property |
| 4 | 2–3 | **I1 PixelMask** | M1 |
| 5 | 3–8 | Process internals | Golden profiles ×10 |
| 6 | 8–9 | Corners + I2 | I2 verified |
| 7 | 9–12 | **I3 variability** | M1 complete |
| 8 | 12–13 | Validation suite | L1–L4 pass |

### 1.5 Testing Strategy (Document 07)

| Tier | Purpose | Tool | Gate |
|---|---|---|---|
| 1 Unit | Per-function | pytest | L0 |
| 2 Golden | Regression pinning | pytest-regressions + hashes | L0/L1 |
| 3 Property | Invariant discovery | hypothesis | L0 |
| 4 Numerical | Scientific accuracy | pytest + analytic refs | L4 |
| 5 Regression | Release gate | full suite + CI | L1–L4 |

---

## 2. Frozen Tolerances (Geometry Scientific Validation)

| Metric | Tolerance |
|---|---|
| CD accuracy | 0.1 nm |
| LER 3σ | ± 0.3 nm |
| LER correlation length ξ | ± 10% |
| LER left–right correlation ρ | ± 0.05 |
| Overlay shift | ± 0.1 nm |
| Trapezoid sidewall angle | ± 0.1° |
| Conformal thickness | ± 0.1 nm |
| Corner radius | ± 0.2 nm |
| CDU batch spread | ± 0.1 nm |

---

## 3. Engineering Decisions Frozen (17)

| ID | Decision | Document |
|---|---|---|
| GD1–GD17 | Module hierarchy, library stack, algorithms A1–A10, public/private API, 8-step sequence, 5 test tiers, toolchain | 02–07, 08 |

---

## 4. Geometry Engine Implementable Without Revisiting Research

**Certification:** An engineering team can implement `geo_raster`, `geo_process`, and `geo_variability` from Phase 5.2 alone because:

1. Every algorithm maps to a frozen specification.
2. Every library choice has a justified alternative + migration path.
3. Every internal module has defined I/O, dependencies, and validation.
4. The 8-step sequence produces testable increments.
5. Scientific tolerances are numerically frozen.

---

## 5. Knowledge Required for Phase 5.3

Phase 5.3 must answer: **"How should the SEM Physics Engine be implemented?"**

| Question | Why It Matters |
|---|---|
| 1. **Internal module breakdown** for phys_signal, phys_degrade, phys_formation — what sub-modules implement SE yield, BSE yield, edge brightening, charging, PSF, shot noise, detector noise, digitization? | Structure of the implementation |
| 2. **Algorithm mapping** for each certified physics model — how is the universal SE yield model computed per pixel? How is topographic contrast (cos⁻¹θ) evaluated on a 2.5D height field? How is the PSF kernel generated and applied? | Scientific fidelity |
| 3. **Library selection** — which convolution method (spatial vs FFT), which RNG for Poisson noise, which interpolation for surface normals? | Performance and determinism |
| 4. **Material property table** — what are the exact δ₀, η, Λ, E_b values for the 7 materials (Si, SiO₂, SiN, Cu, W, PR, vacuum)? | Physics calibration |
| 5. **Testing strategy** — how are yields validated against published literature values? How is the I4 boundary (geometry → physics) tested? | Quality gates |
| 6. **Source tree** — `semicon/physics/` layout consistent with `semicon/geometry/` conventions? | Consistency |
| 7. **Development sequence** — risk-driven order for physics modules? | Incremental validation |

**Phase 5.3 begins where Phase 5.2 ends: at the I4 boundary.**

---

## 6. Document Map

```
research/phase-5.2/
│
├── 01_executive_summary.md              ← Blueprint overview
├── 02_geometry_module_breakdown.md       ← 8 internal modules
├── 03_library_and_dependency_selection.md ← gdspy, numpy, scipy, skimage
├── 04_algorithm_mapping.md              ← A1–A10 algorithm specifications
├── 05_repository_structure.md           ← Source tree, public/private API
├── 06_development_sequence.md           ← 8-step development plan
├── 07_testing_and_tooling.md            ← 5 test tiers + toolchain
├── 08_engineering_conclusions.md       ← 17 frozen decisions (GD1–GD17)
├── 09_complete_reference_list.md        ← 11 references
└── 10_phase5_2_final_report.md          ← This consolidated report
```

---

## 7. Cumulative Repository Status

| Metric | Count |
|---|---|
| Research phases | **19** (Phase 1 – Phase 5.2) |
| Total documents | **180** |
| Geometry Engine blueprint | **Complete — frozen** |
| Next phase | **5.3: SEM Physics Engine Implementation Blueprint** |

---

*End of Phase 5.2 Final Report — Geometry Engine Implementation Blueprint*
