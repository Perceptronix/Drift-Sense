# Engineering Conclusions

**Research Phase:** 5.3
**Document:** 08_engineering_conclusions.md
**Date:** 2026-07-30

---

## 1. Frozen Implementation Decisions

| # | Decision | Value | Justification |
|---|---|---|---|
| **PD1** | Internal module hierarchy | 9 modules across 3 public + shared | Single responsibility (Doc 02) |
| **PD2** | Numerical core | NumPy + SciPy (fftconvolve, ndimage) | Ecosystem standard; determinism (Doc 03) |
| **PD3** | Convolution | FFT (`fftconvolve`, mode='same'); spatial cross-over K<15 | Performance + accuracy (Doc 04, P7) |
| **PD4** | PSF normalization | **Sum = 1** (conserved mean) | Phase 4.5 verification decision; I5 postcondition (Doc 04, P7) |
| **PD5** | RNG | `numpy.random.Generator` (PCG64) via rng_utils | Deterministic, modern (Doc 03) |
| **PD6** | Noise seeds | Derived from `noise_seed` chain | Phase 4.3 reproducibility (Doc 03) |
| **PD7** | SE yield algorithm | δ = δ₀·(cosθ)^(−f)·exp(Λ·(1−cosθ)) | Certified universal model (Doc 04, P2) |
| **PD8** | BSE yield algorithm | Everhart polynomial on material Z, precomputed | Certified model (Doc 04, P3) |
| **PD9** | SE composition | SE = SE1 + η·g_bulk·SE1 | Certified SE1+SE2 model (Doc 04, P4) |
| **PD10** | Edge brightening | Smooth ramp, factor ∈ [1.5, 3.0] | Certified mechanism (Doc 04, P5) |
| **PD11** | Charging scope | Isolated structures only; warning otherwise | Certified caveat (Doc 04, P6) |
| **PD12** | Degradation order | PSF blur → shot noise → detector noise → clamp | Frozen order (Doc 02) |
| **PD13** | Digitization | round-half-even; clip to [0, 2^bits−1] | Deterministic (Doc 04, P10) |
| **PD14** | Material library | YAML pinned `materials_v1.yml` → frozen dataclass records | Extensible, versioned (Doc 05) |
| **PD15** | Material lookup | `np.take(property_array, material_map)` | Vectorized O(M·N) (Doc 05) |
| **PD16** | Material ID immutability | IDs 0–6 immutable; extensions use ≥ 7 | Certified encoding (Doc 05) |
| **PD17** | Repository layout | `_signal/_degrade/_formation/_shared` | Phase 5.2 conventions (Doc 06) |
| **PD18** | Development sequence | 8 steps, I4-boundary-first | Risk-driven (Doc 07) |
| **PD19** | Testing tiers | 6 tiers incl. I4 compatibility + literature validation | Defense in depth (Doc 07) |
| **PD20** | Toolchain | pytest, hypothesis, black, ruff, mypy, cProfile, memory_profiler, Sphinx | Phase 5.1 baseline + profiling (Doc 07) |

---

## 2. Frozen Module Hierarchy

```
semicon.physics/
├── signal.py                 ← public, I4
├── _signal/  (yield_computer, topography_engine, edge_effects, charging_engine, signal_assembler)
├── degrade.py                ← public, I5
├── _degrade/ (psf_generator, blur_applier, shot_noise, detector_noise, degrade_assembler)
├── formation.py              ← public, I6
├── _formation/ (image_former)
└── _shared/   (material_properties, physics_utils)
```

---

## 3. Frozen Library Stack

| Library | Version Pin | Purpose |
|---|---|---|
| numpy | ≥1.25,<2.0 | Array core, PCG64 RNG |
| scipy | ≥1.11,<2.0 | fftconvolve, ndimage, gradients |
| scikit-image | ≥0.21,<1.0 | PSF sizing, charging masks |
| pillow | ≥10,<11 | Image I/O (golden fixtures) |
| pyyaml | ≥6,<7 | Material library |
| cProfile / line_profiler / memory_profiler | dev | Profiling |
| pytest, hypothesis | dev | Testing |
| black, ruff, mypy | dev | Quality |
| sphinx + numpydoc | dev | Docs |

---

## 4. Frozen Development Sequence

| Step | Week | Deliverable | Gate |
|---|---|---|---|
| 1 | 0–0.5 | Toolchain + material library | Material tests green |
| 2 | 0.5–1 | physics_utils | Utility tests |
| 3 | 1–2 | yield_computer + topography | Yield tests; I4-input compat |
| 4 | 2–3.5 | edge effects + charging | **I4 verified** |
| 5 | 3.5–4.5 | PSF + blur | PSF tests; < 200 ms |
| 6 | 4.5–5.5 | noise models | **I5 verified** |
| 7 | 5.5–6 | image_former | **I6 verified**; golden images |
| 8 | 6–7 | validation suite | **L1–L4 physics gates pass** |

---

## 5. Frozen Testing Strategy

| Tier | Purpose | Gate | Tools |
|---|---|---|---|
| 1 Unit | Per-function | L0 | pytest |
| 2 Golden-reference image | Output pinning | L0/L1 | pytest-regressions + hashes |
| 3 Numerical tolerance | Analytic accuracy | L4 | pytest.approx |
| 4 Scientific validation | Published-value checks | L4 | literature assertions |
| 5 Regression suite | Release gate | L1–L4 | full suite + CI |
| 6 I4 compatibility | Geometry→physics boundary | L2 | real geometry fixtures |

**Key scientific tolerances frozen:**
- Si δ(1 keV) ∈ [0.4, 0.8]; Si η ∈ [0.15, 0.25]
- Material contrast ordering (Cu SE < Si SE; W BSE > Cu BSE > Si BSE)
- Edge brightening ratio = factor ± 0.5%
- PSF FWHM ± 1%; noise statistics ±1–2%; determinism bitwise

---

## 6. Explicit Deferrals (Future Optimizations)

| Item | Deferred To | Reason |
|---|---|---|
| PyFFTW | Profiling (Phase C) | fftconvolve adequate |
| Numba JIT | Profiling (Phase C) | first-call determinism caveat |
| GPU (CuPy/PyTorch) | Rejected for v1 | RD6: GPU not required |
| Separable Gaussian PSF | Profiling | 2D FFT adequate |
| Dense-pattern charging | Out of v1 scope | Certified caveat |

---

## 7. Certification Statement

The SEM Physics Engine implementation blueprint is **frozen and complete**. An engineering team can implement `phys_signal`, `phys_degrade`, and `phys_formation` from this phase alone — without revisiting Phases 1–4 or Phase 5.2 — because:

1. Every algorithm (P1–P10) maps to a certified physics specification.
2. Every library choice has a justified alternative.
3. Every internal module has defined responsibility, I/O, dependency, and validation.
4. The 8-step sequence is risk-driven (I4 boundary tested first) with explicit gates.
5. Material properties are frozen, versioned, and validated against literature.
6. Scientific tolerances are numerically pinned.

---

## Sources

- Phase 2.2–2.5 — Physics specifications (certified).
- Phase 2.6 — SEM Physics Engine certification.
- Phase 4.2 — Interfaces I4–I6.
- Phase 5.2 — Geometry Engine blueprint (frozen).
- Phase 5.1 — Roadmap.
- Documents 01–07 of this phase.
