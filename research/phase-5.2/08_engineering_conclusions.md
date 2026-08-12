# Engineering Conclusions

**Research Phase:** 5.2
**Document:** 08_engineering_conclusions.md
**Date:** 2026-07-30

---

## 1. Frozen Implementation Decisions

| # | Decision | Value | Justification |
|---|---|---|---|
| **GD1** | Internal module hierarchy | 8 internal modules across 3 public modules | Single responsibility per file (Doc 02) |
| **GD2** | GDSII library | **gdspy** | Mature, full GDSII support, deterministic (Doc 03) |
| **GD3** | Numerical core | NumPy + SciPy + scikit-image | Ecosystem standard; tested ndimage ops (Doc 03) |
| **GD4** | Image I/O | Pillow | Standard; 16-bit TIFF/PNG for fixtures (Doc 03) |
| **GD5** | Rasterization algorithm | Edge-function supersampling (8×8), threshold 0.5 | Anti-aliased; simple; deterministic (Doc 04, A1) |
| **GD6** | Height field generation | Ordered ProcessPlan execution | Matches layer-stack semantics (Doc 04, A2) |
| **GD7** | Etch sidewall | Per-column trapezoid carving | Analytic profile fidelity (Doc 04, A3) |
| **GD8** | Deposition | Chebyshev isosurface offset | Uniform thickness in 2.5D (Doc 04, A5) |
| **GD9** | CMP | Clip + local erosion | Global/local planarization (Doc 04, A6) |
| **GD10** | LER generation | 1D spectral synthesis (exponential ACF) | Exact correlation control (Doc 04, A7) |
| **GD11** | Overlay | Separable spline, order=1; integer+frac split | Deterministic, lossless integer shift (Doc 04, A8) |
| **GD12** | Variability order | CDU → LER → SWA → overlay | Overlay last keeps consistency (Doc 02) |
| **GD13** | Material update | Edge-adjacent-only band | Efficiency without ID corruption (Doc 04, A9) |
| **GD14** | Public/private API | Public `raster/process/variability`; private `_raster/_process/_variability` | Stable contract, free internals (Doc 05) |
| **GD15** | Development sequence | 8 steps, foundation-first, risk-driven | Incremental validation (Doc 06) |
| **GD16** | Testing tiers | 5 tiers (unit, golden, property, numerical, regression) | Defense in depth (Doc 07) |
| **GD17** | Toolchain | pytest, black, ruff, mypy --strict, Sphinx | Phase 5.1 baseline (Doc 07) |

---

## 2. Frozen Module Layout

```
semicon.geometry/
├── raster.py                    ← public, I1
├── _raster/  (gdsii_reader, polygon_rasterizer, mask_builder)
├── process.py                   ← public, I2
├── _process/ (layer_stack, deposition, lithography, etch, cmp, corner_rounding, heightfield_gen)
├── variability.py               ← public, I3
└── _variability/ (edge_detector, ler_generator, overlay_engine, cdu_engine, variability_applier)
```

---

## 3. Frozen Library Stack

| Library | Version Pin | Purpose |
|---|---|---|
| gdspy | ≥1.6,<2.0 | GDSII parsing |
| numpy | ≥1.25,<2.0 | Numerical core |
| scipy | ≥1.11,<2.0 | ndimage, fft |
| scikit-image | ≥0.21,<1.0 | Distance transform, contours |
| pillow | ≥10,<11 | Image I/O (fixtures) |
| pytest, hypothesis | dev | Testing |
| black, ruff, mypy | dev | Quality |
| sphinx | dev | Docs |

---

## 4. Frozen Development Sequence

| Step | Deliverable | Gate |
|---|---|---|
| 1 | Scaffold + toolchain | CI green |
| 2 | gdsii_reader | Parser tests |
| 3 | polygon_rasterizer | Golden + property |
| 4 | **I1** mask_builder | M1 |
| 5 | Process internals | Golden profiles ×10 |
| 6 | Corners + assembly | I2 verified |
| 7 | **I3** variability | M1 complete |
| 8 | Validation suite | L1–L4 pass |

---

## 5. Frozen Testing Strategy

| Tier | Purpose | Gate | Tools |
|---|---|---|---|
| 1 Unit | Per-function correctness | L0 | pytest |
| 2 Golden | Regression pinning | L0/L1 | pytest-regressions + hashes |
| 3 Property | Invariant discovery | L0 | hypothesis |
| 4 Numerical | Scientific accuracy | L4 | pytest + analytic refs |
| 5 Regression | Release gate | L1–L4 | Full suite + CI |

**Key tolerances frozen:**
- CD accuracy: 0.1 nm
- LER 3σ: ±0.3 nm; ξ: ±10%; ρ: ±0.05
- Overlay: ±0.1 nm
- Trapezoid angle: ±0.1°
- Corner radius: ±0.2 nm

---

## 6. Explicit Deferrals (Future Optimizations)

| Item | Deferred To | Reason |
|---|---|---|
| Sweep-line rasterization | After profiling (Phase C) | Supersampling sufficient for FOV sizes |
| Euclidean 3D offset deposition | After profiling | 2.5D Chebyshev adequate for planar structures |
| LER PSD template reuse | After profiling | Edge lengths vary; caching adds complexity |
| gdstk migration | If gdspy unmaintained | Drop-in successor path documented |

---

## 7. Certification Statement

The Geometry Engine implementation blueprint is **frozen and complete**. An engineering team can implement `geo_raster`, `geo_process`, and `geo_variability` from this phase alone — without revisiting Phases 1–4 — because:

1. Every algorithm (A1–A10) maps to a frozen scientific specification.
2. Every library choice has a justified alternative and migration path.
3. Every internal module has a defined responsibility, I/O, dependency, and validation.
4. The 8-step sequence produces testable increments with explicit completion criteria.
5. Tolerances for scientific validation are numerically frozen.

---

## Sources

- Phase 3.1–3.4 — Geometry Engine (certified).
- Phase 4.2 — Interfaces I1–I3.
- Phase 5.1 — Roadmap WBS 1.1–1.3.
- Documents 01–07 of this phase.
