# Phase 5.3 Executive Summary: SEM Physics Engine Implementation Blueprint

**SEMICON 2026 Research Repository**
**Applied Materials**
**Date:** 2026-07-30
**Classification:** Implementation-Planning

---

## Purpose

This phase answers: **"How should the SEM Physics Engine be implemented from the first line of code to a fully validated module?"**

The certified SEM Physics Engine (Phase 2.6) is translated into a complete implementation blueprint — internal module breakdown, library selection, algorithm mapping, material property library design, repository structure, development sequence, testing strategy, and toolchain. This is **implementation specification, not production code**.

---

## Blueprint Summary

| Dimension | Recommendation |
|---|---|
| **Internal modules** | 9 modules across 3 public modules |
| **Numerical core** | NumPy + SciPy (FFT convolution) |
| **RNG for noise** | rng_utils (foundation) + NumPy Generator |
| **Interpolation** | scipy.ndimage (map_coordinates) |
| **Material library** | YAML file + frozen dataclass records |
| **Development order** | 8 steps, risk-driven, I4-boundary-first |
| **Testing** | 6 tiers incl. I4 compatibility + published-value validation |

---

## Key Blueprint Decisions

### 1. Module Hierarchy (9 internal modules)

```
phys_signal (public: M4)
├── yield_computer       ← SE + BSE yield per pixel
├── topography_engine    ← cos⁻¹θ topographic contrast, surface normals
├── edge_effects         ← edge brightening, sidewall emission
├── charging_engine      ← surface potential modulation
└── signal_assembler     ← SE (SE1+SE2) + BSE → YieldMaps

phys_degrade (public: M5)
├── psf_generator        ← Gaussian beam kernel
├── blur_applier         ← FFT convolution
├── shot_noise           ← Poisson per pixel (seeded)
├── detector_noise       ← Gaussian read noise (seeded)
└── degrade_assembler    ← order + clamping → YieldMaps_degraded

phys_formation (public: M6)
└── image_former         ← gain/offset, saturation, digitization → SEMImage

shared:
├── material_properties  ← Material property records + lookup
└── physics_utils        ← sampling kernels, PSF sizing, angle math
```

### 2. Algorithm Mapping Highlights

| Frozen Specification | Implementation Algorithm |
|---|---|
| Universal SE yield δ(θ) | δ = δ₀·(cosθ)^(−f)·exp(Λ·(1−cosθ)) per pixel from surface normal |
| BSE yield η | η(Z) = 0.0254 + 0.016·Z − 1.86×10⁻⁴·Z² + 8.3×10⁻⁷·Z³ (Everhart) per material |
| SE2 (BSE-induced SE) | SE2 = η · g(SE generation in bulk) scaled contribution |
| PSF blur | 2D Gaussian kernel, FFT convolution (pad + crop) |
| Shot noise | Poisson sampling per pixel: y ~ Poisson(λ=signal) |
| Detector noise | Additive Gaussian: y + N(0, σ_read²) |
| Edge brightening | Enhancement factor ×1.5–3.0 at edge-angle pixels |
| Charging | Surface-potential ± modulation on yield, isolated structures only |
| Digitization | I = clip(gain·Y + offset, 0, 2^bits−1), round-half-even |

### 3. Material Property Library

| Material ID | Material | δ₀ | Λ (nm) | η | Z | E_b (keV) |
|---|---|---|---|---|---|---|
| 0 | Vacuum | 0.0 | 0.0 | 0.0 | 0 | 0 |
| 1 | Silicon (Si) | 0.15 | 2.5 | 0.19 | 14 | 0.0018 |
| 2 | SiO₂ | 0.16 | 2.8 | 0.19 | 10.8 (avg) | 0.0040 |
| 3 | Si₃N₄ | 0.15 | 2.6 | 0.20 | 10.4 (avg) | 0.0035 |
| 4 | Copper (Cu) | 0.12 | 1.8 | 0.31 | 29 | 0.0011 |
| 5 | Tungsten (W) | 0.10 | 1.5 | 0.50 | 74 | 0.0010 |
| 6 | Photoresist | 0.20 | 4.0 | 0.03 | 5 (avg) | 0.0060 |

*(Values are Phase 2-certified reference ranges; final tuning pinned at calibration step — see Document 05.)*

### 4. Development Sequence (8 Steps)

```
Step 1: Toolchain + material library  → pyproject, material_properties.yml
Step 2: physics_utils                → angle math, sampling kernels
Step 3: yield_computer + topography  → SE/BSE yield maps (I4-input tests)
Step 4: edge_effects + charging      → full phys_signal → I4 verified
Step 5: psf_generator + blur_applier → PSF convolution (FFT)
Step 6: shot_noise + detector_noise  → noise models → I5 verified
Step 7: image_former                 → SEMImage → I6 verified
Step 8: validation suite             → L1–L4 physics gates
```

---

## Phase 5.4 Knowledge Required

Phase 5.4 must answer: **"How should the Geometry Engine and SEM Physics Engine be integrated into a complete simulator, the dataset generation pipeline established, and end-to-end validation executed?"** — orchestration integration (I4–I8), config→CLI→batch flow, dataset pipeline, and full end-to-end regression.

---

## Conventions Used

| Level | Meaning |
|---|---|
| **Frozen Specification** | Certified decision from Phases 1–4 — cannot change |
| **Implementation Decision** | New decision made here — frozen for Phase 5.3's scope |
| **Future Optimization** | Noted but explicitly deferred |

---

## Sources

- Phase 2.1–2.6 — SEM Physics Engine (certified).
- Phase 4.2 — Interface contracts I4, I5, I6.
- Phase 5.2 — Geometry Engine blueprint (frozen).
- Phase 5.1 — Implementation roadmap.
- [P1] H. Seiler, "Secondary electron emission in the scanning electron microscope," *J. Appl. Phys.*, vol. 54, 1983.
- [P2] T. E. Everhart, R. F. M. Thornley, "Wide-band detector for micro-microampere low-energy electron currents," *J. Sci. Instrum.*, vol. 37, 1960.
