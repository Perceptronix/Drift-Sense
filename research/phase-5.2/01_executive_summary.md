# Phase 5.2 Executive Summary: Geometry Engine Implementation Blueprint

**SEMICON 2026 Research Repository**
**Applied Materials**
**Date:** 2026-07-30
**Classification:** Implementation-Planning

---

## Purpose

This phase answers: **"How should the Geometry Engine be implemented from the first line of code to a fully validated module?"**

The certified Geometry Engine (Phase 3.4) is translated into a complete implementation blueprint — internal module breakdown, library selection, algorithm mapping, repository structure, development sequence, and testing strategy. This is **implementation specification, not production code**.

---

## Blueprint Summary

| Dimension | Recommendation |
|---|---|
| **Internal modules** | 8 modules (M1a–M1f internal decomposition) |
| **GDSII parsing** | **gdspy** (primary), python-gdsii (alternative) |
| **Numerical core** | NumPy + SciPy |
| **Image processing** | scikit-image (distance transform, edge detection) |
| **Rasterization** | Custom polygon rasterizer (anti-aliased edge function) |
| **Development order** | 8 steps, foundation-first, risk-driven |
| **Testing** | 5 tiers: unit, golden, property, numerical, regression |
| **Toolchain** | Python 3.11, setuptools, pytest, black, ruff, mypy, Sphinx |

---

## Key Blueprint Decisions

### 1. Module Hierarchy (8 internal modules)

```
geo_raster (public: M1)
├── gdsii_reader        ← GDSII parsing (gdspy wrapper)
├── polygon_rasterizer  ← Anti-aliased edge-function rasterization
└── mask_builder        ← FOV selection, layer extraction, mask validation

geo_process (public: M2)
├── layer_stack         ← LayerStack definition, material resolution
├── deposition          ← Conformal / isotropic / PVD deposition
├── lithography         ← Patterning, CD bias, resist profile
├── etch                ← Anisotropic / isotropic etch, sidewall synthesis
├── cmp                 ← Planarization, over-polish
├── corner_rounding     ← Top/bottom corner radius application
└── heightfield_gen     ← HeightField + MaterialMap assembly

geo_variability (public: M3)
├── edge_detector       ← Height-field gradient edge localization
├── ler_generator       ← Exponential-ACF Gaussian field (rng_utils)
├── overlay_engine      ← Translational overlay shift
├── cdu_engine          ← CD distribution sampling
└── variability_applier ← Edge displacement + material update
```

### 2. Algorithm Mapping Highlights

| Frozen Specification | Implementation Algorithm |
|---|---|
| GDSII → PixelMask | Edge-function polygon fill with 8×8 sub-pixel supersampling |
| Conformal deposition | Chebyshev distance transform + isosurface fill |
| Trapezoidal etch profile | Per-pixel sidewall sweep with arctan slope from angle |
| CMP planarization | Global height reduction with local polish window |
| Corner rounding | Quadratic/circular fillet via distance-field sculpting |
| LER generation | Gaussian random field via spectral synthesis (1D per line, exponential ACF) |
| Overlay | Integer-plus-fractional pixel translation (separable interpolation) |
| Material encoding | uint8 ID map updated only at edge-adjacent pixels |

### 3. Library Rationale

| Library | Selected | Alternatives | Why |
|---|---|---|---|
| **gdspy** | ✅ | python-gdsii, gdstk | Mature, active, supports all GDSII data types, clean geometry API |
| **NumPy** | ✅ | — | Non-negotiable numerical foundation |
| **SciPy** | ✅ | — | ndimage, FFT, sparse for process ops |
| **scikit-image** | ✅ | OpenCV, custom | `distance_transform_edt`, `find_contours`, clean array API |
| **Pillow** | ✅ | tifffile | Standard PNG/TIFF I/O in Foundation layer |

### 4. Development Sequence (8 Steps)

```
Step 1: Toolchain + scaffold    → pyproject.toml, CI, package skeleton
Step 2: gdsii_reader           → parse test GDSII files
Step 3: polygon_rasterizer     → PixelMask from polygons (golden tests)
Step 4: mask_builder           → I1-complete: GDSII → PixelMask
Step 5: layer_stack + deposition + etch + cmp → HeightField_det
Step 6: corner_rounding + heightfield_gen → I2-complete
Step 7: edge_detector + ler_generator + overlay + cdu → I3-complete
Step 8: full validation suite  → L1–L4 gates for Geometry Engine
```

---

## Phase 5.3 Knowledge Required

Phase 5.3 must answer: **"How should the SEM Physics Engine be implemented?"** — the same blueprint treatment for phys_signal (M4), phys_degrade (M5), and phys_formation (M6): internal module breakdown, algorithm mapping of the certified physics models, library selection, and testing strategy.

---

## Conventions Used

This phase distinguishes three levels throughout:

| Level | Meaning |
|---|---|
| **Frozen Specification** | Certified decision from Phases 1–4 — cannot change |
| **Implementation Decision** | New decision made here — frozen for Phase 5.2's scope |
| **Future Optimization** | Noted but explicitly deferred |

---

## Sources

- Phase 3.1–3.4 — Geometry Engine (certified).
- Phase 4.2 — Interface contracts I1–I3.
- Phase 5.1 — Implementation roadmap, WBS packages 1.1–1.3.
- [G1] H. Koppelaar, *gdspy: A Python Library for GDSII*, 2015.
- [G2] J. D. Foley et al., *Computer Graphics: Principles and Practice*, 3rd ed. Addison-Wesley, 1995.
