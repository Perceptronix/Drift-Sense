# Phase 2.4 Final Report: Why Real SEM Images Are Imperfect

**SEMICON 2026 Research Repository**
**Applied Materials**
**Date:** 2026-07-30
**Classification:** Research-Only (Phase 2.4)

---

## Executive Summary

Phase 2.4 answers the question: **"Why is a real SEM image imperfect?"** This is the final physics research phase before the synthetic SEM renderer design (Phase 2.5). It investigates every major degradation mechanism — blur, noise, charging, and artifacts — that separates real images from the ideal model established in Phases 2.1–2.3.

### Key Results

1. **Blur is dominated by the finite probe diameter.** The Gaussian probe PSF (FWHM 0.5–2 nm) is the single most important degradation mechanism. Material-dependent SE escape depth adds 0.5–3 nm. All other blur sources are secondary.

2. **Shot noise is the fundamental noise floor.** The SNR in CD-SEM is $\sqrt{N_{\text{det}}}$, where $N_{\text{det}}$ ≈ 65–130 electrons per pixel at standard conditions (15 pA, 1 μs dwell). This gives SNR ≈ 8–11:1.

3. **Charging is the most complex degradation** because it affects the image through multiple pathways simultaneously (SE yield modification, beam deflection, drift). A simplified model — per-material SE yield reduction for insulators — captures the first-order effect.

4. **Artifacts are manageable.** Detector saturation (edge blooming) and SE-II halos are the most important. Streaking, banding, dead pixels, and discharge can be safely ignored.

5. **25 mechanisms were classified** into four tiers: Essential (4), Recommended (5), Optional (6), Can ignore (10).

---

## 1. Phase Results by Document

### 1.1 Resolution and Blur (Document 02)

| Blur Source | Typical FWHM | Rank |
|---|---|---|
| Gaussian probe | 0.5–1.5 nm | **Dominant** |
| SE escape depth | 0.5–3 nm | **Significant** (material-dependent) |
| Lens aberrations | 0.2–0.5 nm | Moderate |
| SE-II background | 10–500 nm (tail) | Profile shape |
| Diffraction | <0.1 nm | Negligible |
| Vibration | 0.1–0.3 nm | Minor |

**Effective resolution (10–90% edge rise):** 1.5–4 nm for typical CD-SEM conditions.

### 1.2 Noise Models (Document 03)

| Noise Source | % of Total | Stationary/Signal-Dependent |
|---|---|---|
| **Shot noise** | ~70–80% | Signal-dependent ($\sigma \propto \sqrt{I}$) |
| PMT excess noise | ~15–20% | Signal-dependent |
| Amplifier (Johnson) | <5% | Stationary |
| Quantization (16-bit) | <1% | Stationary |
| Dark current | <1% | Stationary |

**Unified model:** Shot noise is sufficient for first implementation. PMT excess noise can be added as a variance scaling factor $F \approx 1.2$.

### 1.3 Charging Physics (Document 04)

| Charging Mode | $\sigma$ condition | Effect on Image |
|---|---|---|
| **Positive** ($\sigma > 1$) | $\delta + \eta > 1$ | Darker insulators, reduced SE yield |
| **Negative** ($\sigma < 1$) | $\delta + \eta < 1$ | Brighter insulators (less common at low kV) |
| **Neutral** ($\sigma = 1$) | $\delta + \eta = 1$ | Minimal charging artifacts |

**Recommendation for simulator:** Apply material-dependent effective SE yield reduction factor for insulators. A full self-consistent electrostatic model is not required for first implementation.

### 1.4 Imaging Artifacts (Document 05)

| Artifact | Severity | Should Model? |
|---|---|---|
| **Edge blooming (saturation)** | Moderate | Yes — simple clip function |
| **SE-II halo** | Moderate | Yes — part of SE-II model |
| **Scan distortion** | Low (center of FOV) | Optional |
| **Drift** | Moderate (long acquisition) | Optional |
| **Vibration** | Low (isolated tool) | Optional |
| **Banding, streaking, dead pixels** | Very low | **No** |

### 1.5 Instrument Performance (Document 06)

**Central trade-off:** Probe current vs. resolution.

$$I_P \uparrow \rightarrow \text{SNR} \uparrow \text{ but } d_p \uparrow \text{(more blur)}$$

**Fixed parameters for renderer design (recommended):**
- Beam energy: 1 keV (baseline)
- Probe diameter: 1.0 nm FWHM
- Probe current: 15 pA
- Dwell time: 1 μs
- Pixel size: 1 nm
- ADC: 16-bit

### 1.6 Engineering Classification (Document 07)

| Tier | Count | Mechanisms | Implementation Phase |
|---|---|---|---|
| **Essential** | 4 | Gaussian probe PSF, escape depth blur, shot noise, charging SE yield reduction | Phase A (MVP) |
| **Recommended** | 5 | PMT excess noise, SE-II background, detector saturation, frame averaging, effective beam energy | Phase B |
| **Optional** | 6 | Defocus, astigmatism, scan distortion, drift, vibration, amplifier noise | Phase C |
| **Can ignore** | 10 | Diffraction, dark current, banding, streaking, dead pixels, flashover, source noise, scan noise, magnetic interference, line skipping | Never |

---

## 2. Complete Degradation Model

### 2.1 Forward Model from Ideal Contrast to Realistic Pixel Values

$$I_{\text{final}} = \text{Clip}\left( \text{Poisson}\left( \frac{I_{\text{blurred}} + I_{\text{SE-II}}}{G_{\text{eff}}} \right) \cdot G_{\text{eff}} \cdot F, \ 0, \ I_{\text{max}} \right)$$

where:
- $I_{\text{blurred}} = I_{\text{ideal}} * \text{PSF}_{\text{probe}} * \text{PSF}_{\text{escape}}$ — ideal image convolved with probe and escape depth PSFs
- $I_{\text{SE-II}}$ — long-range SE-II background (convolution with ~1 μm kernel)
- $G_{\text{eff}}$ — effective gain (electrons → digital units)
- $F$ — PMT excess noise factor (1.0–1.3)
- $\text{Poisson}(\lambda)$ — Poisson-distributed random variate with mean $\lambda$
- $\text{Clip}$ — detector/ADC saturation at $I_{\text{max}}$

### 2.2 Charging Modification

Before the pipeline: modify the SE yield for insulating materials:

$$\delta_{\text{eff}}(Z_{\text{insulator}}) = \delta_0(Z_{\text{insulator}}) \cdot f_{\text{charge}}$$

where $f_{\text{charge}} = 0.3$–$0.8$ depending on the insulating material and charging severity.

---

## 3. Critical Unresolved Questions

| # | Question | Impact on Renderer |
|---|---|---|
| U1 | Exact PSF shape for given instrument conditions | Determines blur kernel |
| U2 | SE escape depth per material at each energy | Material-dependent resolution |
| U3 | Charging factor per insulator | Brightness of insulators |
| U4 | SE-II correlation length | Edge profile tails |
| U5 | Noise power spectrum of CD-SEM | Confirms white noise assumption |

---

## 4. Knowledge Required for Phase 2.5

Phase 2.4 is the **final physics research phase**. Phase 2.5 must **freeze all parameters and design the synthetic SEM renderer**.

### 4.1 Parameters to Freeze Before Renderer Design

| Parameter | Baseline Value | Alternatives to Support |
|---|---|---|
| Proton beam energy | 1 keV | 500 eV, 800 eV |
| Probe diameter (FWHM) | 1.0 nm | 0.8, 1.5 nm |
| Probe current | 15 pA | 5, 50 pA |
| Pixel dwell time | 1 μs | 0.5, 2, 5 μs |
| Pixel size | 1 nm | 0.5, 2 nm |
| ADC bit depth | 16-bit | — |
| Frame averaging | 1, 8, 16 frames | — |
| Detector type | TTL SE | TTL SE + annular BSE |
| Emission collection efficiency | 0.7 | — |
| PMT excess noise factor | 1.2 | — |
| SE escape depth per material | From Phase 2.2 + 2.4 | Confirm final values |

### 4.2 Engineering Decisions for Phase 2.5

| Decision | Options | Recommended |
|---|---|---|
| PSF model | Gaussian only, Gaussian + exponential (SE-II), full convolution | Gaussian + exponential |
| Noise model | Pure Poisson, Poisson + Gaussian, Poisson + excess | Poisson + excess |
| Charging model | Yield scaling, electrostatic simulation, ignore | Yield scaling |
| Artifact model | Saturation only, full catalog, none | Saturation + SE-II |
| Geometry input format | 2.5D height map, 3D mesh, voxel grid | 2.5D height map (initial) |
| Detector model | Simple $\eta_{\text{coll}}$ function, full angular integral | Simple $\eta_{\text{coll}}$ |

### 4.3 Deliverables from Phase 2.5

Phase 2.5 should produce:

1. **The frozen parameter list** — every physical constant used in the renderer.
2. **The image formation equation** — the complete mathematical model from input geometry to final pixel values.
3. **The PSF library** — precomputed convolution kernels for each relevant material and energy.
4. **The material property table** — $\delta_0$, $\eta$, escape depth, charging factor per material.
5. **The noise model specification** — how shot noise and excess noise are generated per pixel.
6. **The renderer architecture** — engine design, input/output format, interface specification.

---

## 5. Phase 2.4 Success Criteria

| Criterion | Status | Evidence |
|---|---|---|
| ✓ Why real SEM images are blurred | Achieved | Document 02 |
| ✓ Why noise appears | Achieved | Document 03 |
| ✓ Which artifacts are physically important | Achieved | Documents 04, 05 |
| ✓ Which degradation mechanisms matter for semiconductor metrology | Achieved | Documents 06, 07 |
| ✓ Which effects a realistic SEM simulator must include | Achieved | Document 07 (engineering classification) |
| ✓ Without deciding how they will be implemented | Maintained | Deferred to Phase 2.5 |

---

## 6. Phase 2.4 Document Map

```
research/phase-2.4/
│
├── 01_executive_summary.md              ← High-level overview of all findings
├── 02_resolution_and_blur.md            ← Probe PSF, aberrations, beam broadening, defocus
├── 03_noise_models.md                   ← Shot, PMT, Johnson, quantization, complete model
├── 04_charging_physics.md               ← Positive/negative charging, dielectrics, mitigation
├── 05_imaging_artifacts.md              ← Blooming, halos, streaking, banding, drift, vibration
├── 06_instrument_performance.md         ← MTF, SNR trade-offs, pixel sampling, frame averaging
├── 07_engineering_classification.md     ← 25 mechanisms classified into 4 tiers
├── 08_open_questions.md                 ← Answered, unresolved, and deferred questions
├── 09_complete_reference_list.md        ← All cited sources
└── 10_phase2_4_final_report.md          ← This consolidated report
```

---

*End of Phase 2.4 Final Report*
