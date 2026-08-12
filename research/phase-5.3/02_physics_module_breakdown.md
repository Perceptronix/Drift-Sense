# Physics Module Breakdown

**Research Phase:** 5.3
**Document:** 02_physics_module_breakdown.md
**Date:** 2026-07-30

---

## 1. Module Hierarchy

The SEM Physics Engine's three public interfaces (I4–I6) are implemented by three public modules, internally decomposed into 9 implementation modules:

```
semicon.physics
│
├── signal.py           ← PUBLIC: phys_signal (M4, I4 producer)
│   ├── yield_computer.py      (internal)
│   ├── topography_engine.py   (internal)
│   ├── edge_effects.py        (internal)
│   ├── charging_engine.py     (internal)
│   └── signal_assembler.py    (internal)
│
├── degrade.py          ← PUBLIC: phys_degrade (M5, I5 producer)
│   ├── psf_generator.py       (internal)
│   ├── blur_applier.py        (internal)
│   ├── shot_noise.py          (internal)
│   ├── detector_noise.py      (internal)
│   └── degrade_assembler.py   (internal)
│
├── formation.py        ← PUBLIC: phys_formation (M6, I6 producer)
│   └── image_former.py        (internal)
│
└── _shared/
    ├── material_properties.py ← Material property records + lookup
    └── physics_utils.py       ← Angle math, sampling kernels, PSF sizing
```

---

## 2. phys_signal (M4) Internal Modules

### 2.1 material_properties

| Aspect | Specification |
|---|---|
| **Responsibility** | Define material property records (δ₀, Λ, η, Z, E_b); provide lookup by material ID; validate against Phase 2 certified table |
| **Inputs** | Material ID (uint8) or material name |
| **Outputs** | `MaterialRecord` frozen dataclass |
| **Dependencies** | semicon.foundation.units |
| **Validation strategy** | Unit tests: all 7 IDs resolvable; unknown ID → error; values within certified bounds (see Document 05) |

### 2.2 yield_computer

| Aspect | Specification |
|---|---|
| **Responsibility** | Compute per-pixel SE yield δ and BSE yield η from material, surface normal, beam energy |
| **Inputs** | HeightField, MaterialMap, beam_energy_keV, physics_config |
| **Outputs** | δ_map, η_map (M×N float64) |
| **Dependencies** | material_properties; topography_engine (normals); physics_utils |
| **Validation strategy** | Flat Si at 1 keV → δ within published range [0.4, 0.8]; material contrast ordering Cu > Si for BSE; see Document 07 |

**Algorithm:** Per-pixel:
- SE: δ = δ₀·(cosθ)^(−f)·exp(Λ·(1−cosθ)), where θ = angle between surface normal and beam axis; f = tilt exponent (default 1.0; certified)
- BSE: η(Z) from Everhart polynomial per material Z

### 2.3 topography_engine

| Aspect | Specification |
|---|---|
| **Responsibility** | Compute surface normals and local incidence angle θ from height field gradient |
| **Inputs** | HeightField (float64 nm), pixel_size_nm |
| **Outputs** | cosθ map (M×N float64, ∈ (0, 1]), surface normal components |
| **Dependencies** | scipy.ndimage (sobel/central differences); physics_utils |
| **Validation strategy** | Flat surface → cosθ = 1.0; 45° slope → cosθ = cos(45°) ± 0.5%; vertical wall → cosθ → 0+ clamped |

**Numerical care:** Gradient via central differences; clamp cosθ to [ε, 1] with ε = 1e-6 to avoid division by zero; height-field edges padded with reflect.

### 2.4 edge_effects

| Aspect | Specification |
|---|---|
| **Responsibility** | Apply edge brightening enhancement and sidewall emission boost |
| **Inputs** | δ_map, cosθ map, edge mask (from height-field gradient), config (edge_brightening factor, enabled flag) |
| **Outputs** | δ_map enhanced |
| **Dependencies** | physics_utils (edge classification) |
| **Validation strategy** | Edge pixels scaled by configured factor [1.5, 3.0]; flat regions unchanged; factor 1.0 = identity |

### 2.5 charging_engine

| Aspect | Specification |
|---|---|
| **Responsibility** | Apply surface-charging yield modulation (isolated structures only — certified caveat) |
| **Inputs** | δ_map, η_map, charging_config (enabled, potential_model, isolated_mask) |
| **Outputs** | Modulated δ_map, η_map |
| **Dependencies** | material_properties; physics_utils |
| **Validation strategy** | Disabled → identity; enabled + isolated structure → potential-dependent modulation; dense structures → documented warning (out of scope) |

### 2.6 signal_assembler

| Aspect | Specification |
|---|---|
| **Responsibility** | Assemble final YieldMaps: SE = SE1 + SE2 (BSE-induced); validate I4 postconditions |
| **Inputs** | δ_map (topographic + edge + charging), η_map, bse_contribution_config |
| **Outputs** | `YieldMaps` (se_yield, bse_yield; M×N float64) |
| **Dependencies** | All phys_signal internals |
| **Validation strategy** | I4 interface test: dimensions, finite values, yield ∈ [0, 10]; SE2 adds positive contribution scaled by η |

**SE composition:** se_yield = SE1(δ from topography/material) + SE2(η · g_SE_bulk), where g_SE_bulk is the SE-generation efficiency of BSEs in the bulk (certified configurable factor).

---

## 3. phys_degrade (M5) Internal Modules

### 3.1 psf_generator

| Aspect | Specification |
|---|---|
| **Responsibility** | Generate 2D Gaussian PSF kernel from probe diameter / FWHM |
| **Inputs** | probe_diameter_nm (FWHM), pixel_size_nm, kernel_radius_multiplier |
| **Outputs** | PSF kernel (2D float64, sum-normalized = 1) |
| **Dependencies** | numpy |
| **Validation strategy** | Sum = 1 ± 1e-12 (conserved mean); FWHM matches input ± 1%; radial symmetry |

**Implementation decision (from Phase 4.5 verification):** PSF normalized to **sum = 1** (conserved mean) — matches the I5 postcondition "no systematic DC shift."

### 3.2 blur_applier

| Aspect | Specification |
|---|---|
| **Responsibility** | Convolve yield maps with PSF |
| **Inputs** | YieldMap (M×N), PSF kernel (K×K), boundary_mode |
| **Outputs** | Blurred YieldMap |
| **Dependencies** | scipy.signal.fftconvolve; numpy |
| **Validation strategy** | Zero-diameter (delta PSF) → identity; known square → analytic convolution match; conserved mean (sum preserved ± 1e-9) |

**Implementation decision:** FFT convolution (`fftconvolve`, mode='same') with kernel zero-padded to FFT-friendly size. For very small kernels (K < 15) spatial convolution is used (cross-over threshold, implementation decision).

### 3.3 shot_noise

| Aspect | Specification |
|---|---|
| **Responsibility** | Apply Poisson shot noise per pixel |
| **Inputs** | YieldMap, electrons_per_pixel (scaling to counts), seed |
| **Outputs** | Noisy YieldMap |
| **Dependencies** | rng_utils (seeded Generator) |
| **Validation strategy** | Mean preserved (±1%); variance ≈ mean (Poisson); seeded → reproducible; disabled → identity |

**Implementation decision:** Convert yield → electron count n = yield · gain_counts; sample n' ~ Poisson(n); convert back n'/gain_counts. RNG from rng_utils chain (`noise_seed`).

### 3.4 detector_noise

| Aspect | Specification |
|---|---|
| **Responsibility** | Apply additive Gaussian read noise |
| **Inputs** | YieldMap, σ_read (in yield units), seed |
| **Outputs** | Noisy YieldMap |
| **Dependencies** | rng_utils |
| **Validation strategy** | Mean shift ≈ 0 ± small; σ measured = configured ± 2%; disabled → identity |

### 3.5 degrade_assembler

| Aspect | Specification |
|---|---|
| **Responsibility** | Apply degradation chain in order; clamp; validate I5 postconditions |
| **Inputs** | YieldMaps, DegradationConfig, seed chain |
| **Outputs** | `YieldMaps_degraded` |
| **Dependencies** | All phys_degrade internals |
| **Validation strategy** | I5 interface test: dims, finite, yield ∈ [0, 10] clamped, zero-probe → no blur, noise-off → no noise |

**Degradation order (frozen as implementation decision):**
```
1. PSF blur
2. Shot noise
3. Detector noise
4. Clamp to [0, 10]
```

---

## 4. phys_formation (M6) Internal Module

### 4.1 image_former

| Aspect | Specification |
|---|---|
| **Responsibility** | Map degraded yield to digitized pixel values |
| **Inputs** | YieldMaps_degraded, DetectorConfig (gain, offset, bit_depth, saturate_enabled) |
| **Outputs** | `SEMImage` (uint16 or uint8), `FormationRecord` |
| **Dependencies** | numpy; physics_utils |
| **Validation strategy** | Known yield → known DN; clipping to [0, 2^bits−1]; saturation fraction recorded; round-half-even determinism |

**Algorithm:** I = clip(round(gain·Y + offset), 0, 2^bits−1). Round-half-even (numpy default `np.round`) for determinism.

---

## 5. Module Dependency Graph

```
material_properties ← yield_computer ← signal_assembler ← phys_signal (I4)
        ↑
topography_engine ← edge_effects ← charging_engine
        ↑
physics_utils (shared) ← psf_generator ← blur_applier ← phys_degrade (I5)
                        shot_noise ← detector_noise ← degrade_assembler
                                 image_former ← phys_formation (I6)

External: rng_utils (foundation) → shot_noise, detector_noise
          math_utils (foundation) → topography_engine, psf_generator
```

**Rule:** Physics modules import geometry **data-object types only** (`HeightField`, `MaterialMap`, `PixelMask` from foundation.datatypes). No geometry algorithms.

---

## 6. Validation Responsibility Map

| Gate | Who Tests | What |
|---|---|---|
| **L0 unit** | Internal module owner | Each internal module |
| **L1 module** | Module lead | Public API: signal/degrade/formation contract |
| **L2 interface** | Module leads (pair) | I4 (geometry→physics), I5, I6 |
| **L4 scientific** | Scientific lead | Yield vs published values; noise statistics; PSF width |
| **L5 acceptance** | Program manager | Full physics validation suite |

---

## Sources

- Phase 2.2, 2.3, 2.4, 2.5 — Physics specifications.
- Phase 2.6 — SEM Physics Engine certification.
- Phase 4.2 — Interfaces I4, I5, I6.
- Phase 5.2 — Geometry Engine blueprint (I4 producer, frozen).
