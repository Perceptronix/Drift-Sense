# Development Sequence & Testing Strategy

**Research Phase:** 5.3
**Document:** 07_development_sequence_and_testing.md
**Date:** 2026-07-30

---

## 1. Development Sequence Overview

The SEM Physics Engine is developed in 8 sequential steps. Timeline matches Phase 5.1 WBS packages 1.4–1.6 (phys_signal 4 wks, phys_degrade 2 wks, phys_formation 1 wk) plus validation:

```
Step 1: Toolchain + material library   (Week 0–0.5)
Step 2: physics_utils                 (Week 0.5–1)
Step 3: yield_computer + topography   (Week 1–2)
Step 4: edge_effects + charging       (Week 2–3.5)   → I4 verified
Step 5: psf_generator + blur_applier  (Week 3.5–4.5)
Step 6: shot_noise + detector_noise   (Week 4.5–5.5) → I5 verified
Step 7: image_former                  (Week 5.5–6)   → I6 verified
Step 8: validation suite              (Week 6–7)     → L1–L4 physics gates
```

---

## 2. Step-by-Step Specification

### Step 1: Toolchain & Material Library

| Aspect | Specification |
|---|---|
| **Objective** | Reproducible environment; material property system live |
| **Dependencies** | Phase 5.2 completed (geometry I1–I3); foundation |
| **Deliverables** | `pyproject.toml` physics deps, `semicon/physics/` skeleton, `_shared/material_properties.py`, `materials_v1.yml` (pinned), tests/data/materials_test.yml |
| **Unit tests** | All 7 IDs resolvable; unknown ID error; value bounds; η precompute matches Everhart polynomial |
| **Expected output** | Material library loads; SHA-256 hash registry created |
| **Completion criteria** | Material tests green; library hash recorded |

### Step 2: physics_utils

| Aspect | Specification |
|---|---|
| **Objective** | Shared kernels: angle math, PSF sizing, edge classification, vectorized helpers |
| **Dependencies** | Step 1 |
| **Deliverables** | `_shared/physics_utils.py` |
| **Unit tests** | cosθ clamps; PSF σ↔FWHM conversion; edge threshold classification; sampling kernel shapes |
| **Expected output** | Utility functions tested |
| **Completion criteria** | Utility tests green |

### Step 3: yield_computer + topography_engine

| Aspect | Specification |
|---|---|
| **Objective** | Core SE/BSE yield computation from geometry input |
| **Dependencies** | Steps 1–2; geometry HeightField/MaterialMap (I4 producer test fixtures) |
| **Deliverables** | `_signal/topography_engine.py`, `_signal/yield_computer.py` |
| **Unit tests** | Flat → cosθ=1; 45° slope → cosθ=0.7071; flat Si δ=δ₀ exactly; SE tilt formula analytic; BSE η by material; np.take material lookup |
| **Scientific tests (draft)** | Si δ(1 keV) ∈ [0.4, 0.8]; material contrast ordering |
| **Expected output** | SE1 + BSE yield maps for synthetic fixtures |
| **Completion criteria** | Yield tests green; **I4-input compatibility confirmed** (geometry output feeds yield_computer) |

### Step 4: Edge Effects + Charging → I4 Verified

| Aspect | Specification |
|---|---|
| **Objective** | Full phys_signal with edge brightening and charging |
| **Dependencies** | Step 3 |
| **Deliverables** | `_signal/edge_effects.py`, `_signal/charging_engine.py`, `_signal/signal_assembler.py`, `signal.py` (public) |
| **Unit tests** | Edge factor 1.5–3.0 applied only at edges; factor=1.0 identity; charging disabled identity; isolated-only guard; SE2 ratio; assembler postconditions (dims, finite, [0,10]) |
| **Interface tests (L2)** | `test_i4_geometry_physics.py`: real geometry HeightField_var → compute_yields; dimensions, dtype, values consistent |
| **Expected output** | YieldMaps from geometry engine output |
| **Completion criteria** | **I4 contract verified; L2 interface test green (Week 3.5)** |

### Step 5: PSF Generation & Blur

| Aspect | Specification |
|---|---|
| **Objective** | Gaussian PSF + FFT convolution |
| **Dependencies** | Step 4 |
| **Deliverables** | `_degrade/psf_generator.py`, `_degrade/blur_applier.py` |
| **Unit tests** | Kernel sum=1 ± 1e-12; FWHM ± 1%; delta → identity; conserved mean ± 1e-9; spatial/FFT cross-over consistency |
| **Property tests** | Hypothesis: random kernels → sum=1; convolution commutativity; mean conservation |
| **Expected output** | Blurred yield maps |
| **Completion criteria** | PSF tests green; performance < 200 ms at 1024×1024 |

### Step 6: Noise Models → I5 Verified

| Aspect | Specification |
|---|---|
| **Objective** | Shot noise + detector noise with determinism |
| **Dependencies** | Step 5; rng_utils seed chain |
| **Deliverables** | `_degrade/shot_noise.py`, `_degrade/detector_noise.py`, `_degrade/degrade_assembler.py`, `degrade.py` (public) |
| **Unit tests** | Poisson mean ±1%, var ≈ mean ±5%; Gaussian σ ±2%; disabled → identity; seeded reproducibility (bitwise) |
| **Interface tests (L2)** | `test_i5_physics_internal.py`: yield maps through degrade → postconditions |
| **Expected output** | YieldMaps_degraded |
| **Completion criteria** | **I5 contract verified (Week 5.5)** |

### Step 7: Image Formation → I6 Verified

| Aspect | Specification |
|---|---|
| **Objective** | Digitization to SEMImage |
| **Dependencies** | Step 6 |
| **Deliverables** | `_formation/image_former.py`, `formation.py` (public) |
| **Unit tests** | Known yield → known DN; round-half-even; clip bounds; saturation fraction; uint dtype |
| **Interface tests (L2)** | `test_i6_physics_image.py`: SEMImage bit depth, dimensions, value range |
| **Golden tests** | Line/space + contact SEM images (16-bit TIFF) committed |
| **Expected output** | SEMImage from real geometry + physics pipeline |
| **Completion criteria** | **I6 contract verified (Week 6)** |

### Step 8: Validation Suite

| Aspect | Specification |
|---|---|
| **Objective** | Complete L1–L4 physics validation |
| **Dependencies** | Steps 1–7 |
| **Deliverables** | `tests/module/`, `tests/interface/`, `tests/pipeline/`, `tests/scientific/`; regression hashes |
| **Scientific validation (L4)** | Published-value yield checks; noise statistics; PSF width; edge-brightening ratio; charging bounds; determinism across full physics pipeline |
| **Expected output** | Physics validation report; regression baseline committed |
| **Completion criteria** | **Physics Engine certified ready for I4 integration with Geometry (Week 7)** |

---

## 3. Testing Strategy

### 3.1 Test Tier Architecture

| Tier | Purpose | Tool | Gate |
|---|---|---|---|
| **1 Unit** | Per-function correctness | pytest | L0 |
| **2 Golden-reference image** | Output pinning | pytest-regressions + hashes | L0/L1 |
| **3 Numerical tolerance** | Analytic-accuracy | pytest with `pytest.approx` | L4 |
| **4 Scientific validation** | Physics vs published values | pytest (literature assertions) | L4 |
| **5 Regression suite** | Release gate | full suite + CI | L1–L4 |
| **6 I4 compatibility** | Geometry→physics boundary | pytest (real geometry fixtures) | L2 |

### 3.2 Scientific Validation Criteria (L4)

| Metric | Target | Method |
|---|---|---|
| Si SE yield (1 keV, flat) | δ ∈ [0.4, 0.8] | Published range (Seiler 1983; Reimer 1998) |
| Si BSE yield (1 keV) | η ∈ [0.15, 0.25] | Everhart polynomial + literature |
| Material contrast ordering | Cu SE < Si SE; W BSE > Cu BSE > Si BSE | Empirical yield comparison |
| Edge brightening | edge/flat ratio = configured factor ± 0.5% | Edge-pixel statistics |
| PSF FWHM | configured probe ± 1% | Line-profile measurement |
| Shot-noise statistics | mean ±1%; var ≈ mean ±5% | Empirical over 10⁵ pixels |
| Detector-noise σ | configured ± 2% | Empirical |
| Charging modulation | bounded ±50%; disabled → identity | Direct comparison |
| Digitization | DN bounds exact; saturation fraction = recorded | Direct check |
| Determinism | SHA-256 identical across runs | Full-pipeline repeat |

### 3.3 Golden-Reference Image Tests

| Test | Reference | Purpose |
|---|---|---|
| Flat Si yield map | `reference_yields/flat_si_se.npy` | Baseline signal |
| 45° slope yield | `reference_yields/slope45_se.npy` | Topographic contrast |
| Line/space SEM | `reference_images/ls_sem.tiff` | End-to-end pinning |
| Contact array SEM | `reference_images/contact_sem.tiff` | High-density pinning |
| Noise-off SEM | `reference_images/noise_off.tiff` | Determinism baseline |

### 3.4 I4 Compatibility Tests

The most important boundary test: **the geometry engine's actual output must feed the physics engine exactly as specified.**

| Test | Verifies |
|---|---|
| HeightField dimensions = yield dimensions | Dimension invariant |
| MaterialMap IDs ∈ {0..6} accepted by yield lookup | ID domain |
| Vacuum (ID 0) regions produce zero signal | Vacuum semantics |
| Edge/feature structures produce expected contrast | End-to-end I4 |
| Deterministic: same geometry input → same yield | Determinism across boundary |

---

## 4. Tooling

| Tool | Role | Why |
|---|---|---|
| Python 3.11+ | Runtime | Phase 5.1 frozen |
| setuptools + pyproject.toml | Build | PEP 517/518 |
| pytest 7+ | Tests | Standard; parametrize; approx |
| hypothesis | Property tests | Shrinking; recorded examples |
| black + isort | Formatting | Deterministic |
| ruff | Lint | Fast; docstring rules |
| mypy --strict | Types | Safety |
| cProfile / line_profiler | Profiling | Hot-spot analysis at gates |
| memory_profiler | Memory | Peak-RSS budgets |
| Sphinx + numpydoc | Docs | Auto API docs |

---

## Sources

- [I8] S. McConnell, *Code Complete*, 2nd ed., 2004.
- [G9] J. B. Rainsberger, *JUnit Recipes*, Manning, 2004.
- [G10] D. MacIver, *Property-Based Testing with PropEr, Erlang, and Hypothesis*, 2019.
- Phase 4.5, Document 08 — Validation strategy.
- Phase 5.1, Document 05 — Validation gates.
- Phase 5.2, Document 07 — Testing conventions (reused).
- [P1] Seiler (1983); [P8] Reimer (1998) — yield reference values.
