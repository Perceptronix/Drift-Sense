# Open Questions (Phase 2.4)

**Research Phase:** 2.4
**Document:** 08_open_questions.md
**Date:** 2026-07-30

---

## 1. Questions Answered Within Phase 2.4

| Question | Answer | Document |
|---|---|---|
| What are the dominant blur mechanisms in CD-SEM? | Gaussian probe diameter (0.5–1.5 nm) primarily; beam broadening/escape depth (0.5–3 nm) secondarily. Diffraction is negligible. | 02_resolution_and_blur.md |
| What is the dominant noise source? | Shot noise (Poisson statistics of electron detection). All other noise sources are secondary. | 03_noise_models.md |
| How does charging affect the image? | Reduces effective SE yield on insulators (positive charging at CD-SEM energies). Also causes beam deflection and drift in severe cases. | 04_charging_physics.md |
| Which artifacts are important? | Detector saturation (edge blooming) and SE-II halos are the most important. Streaking, banding, dead pixels can be ignored. | 05_imaging_artifacts.md |
| What is the central trade-off in CD-SEM? | Probe current vs. resolution: higher current improves SNR but increases probe diameter and blur. | 06_instrument_performance.md |
| Which mechanisms are essential for the renderer? | Gaussian probe PSF, escape depth blur, shot noise, charging yield reduction, pixel scaling (4 mechanisms). | 07_engineering_classification.md |

---

## 2. Parameters Requiring Frozen Values

Before the synthetic SEM renderer can be built, the following parameters must be specified as constants (or limited ranges):

### 2.1 Instrument Parameters

| Parameter | Current Uncertainty | Suggested Frozen Value(s) |
|---|---|---|
| **Probe diameter (FWHM)** | 0.5–2.0 nm depending on current and energy | 1.0 nm (nominal), 0.8 nm (high-res), 1.5 nm (high-current) |
| **Probe current** | 5–200 pA depending on aperture | 15 pA (nominal), 50 pA (high-SNR) |
| **Beam energy** | 300 eV–5 keV | 500 eV, 800 eV, 1 keV (3 standard values) |
| **Pixel dwell time** | 0.1–10 μs | 1 μs (nominal) |
| **Pixel size** | 0.2–5 nm | 1 nm (nominal), 0.5 nm (high-res) |
| **ADC resolution** | 8–16 bit | 16-bit internal, 8-bit output |
| **Frame averaging** | 1–256 frames | 1, 8, 16 (3 standard values) |
| **Working distance** | 3–8 mm | 5 mm (nominal) |

### 2.2 Detector Parameters

| Parameter | Current Uncertainty | Suggested Frozen Value |
|---|---|---|
| **Collection efficiency (TTL)** | 0.5–0.95 | 0.7 |
| **PMT excess noise factor $F$** | 1.0–1.5 | 1.2 |
| **Maximum linear output** | Saturation level | +3 dB above nominal max signal |

### 2.3 Material Parameters (from Phase 2.2)

| Parameter | Status | Needed for Phase 2.5 |
|---|---|---|
| SE yield $\delta_0$ per material | Frozen in Phase 2.2 | Confirm values |
| BSE yield $\eta$ per material | Frozen in Phase 2.2 | Confirm values |
| SE escape depth per material | Estimated | Need final values per material |
| BSE yield $\eta$ per material | Frozen | Use directly |
| Charging reduction factor | **Not frozen** — recommended values: 0.3–0.8× | Need to define per insulating material |

---

## 3. Unresolved Technical Questions

| # | Question | Nature of Uncertainty | Impact |
|---|---|---|---|
| U1 | **What is the exact PSF shape for a given set of instrument conditions?** | The PSF is the convolution of multiple contributions (probe, aberrations, escape depth, SE-II). The relative weights are tool- and energy-dependent. | Determines the effective blur kernel for rendering. |
| U2 | **What is the correct escape depth $\Lambda_{\text{escape}}$ for each relevant material at each CD-SEM energy?** | The IMFP for low-energy SEs in compound materials (SiO₂, Si₃N₄, photoresist) has measurement spread. | Affects material-dependent resolution. |
| U3 | **What is the charging severity factor for each insulating material at each beam energy?** | Effective SE yield reduction depends on the local charge balance, which depends on film thickness, conductivity, and time. | Affects the brightness of insulators. |
| U4 | **What is the correlation length for SE-II background?** | The SE-II spatial distribution function is material- and energy-dependent. | Affects edge profile tails. |
| U5 | **What is the noise power spectrum (NPS) of a CD-SEM under typical operating conditions?** | While shot noise is white (uncorrelated), the full noise spectrum includes non-uniformities. | Confirms whether white shot noise approximation is sufficient. |

**Recommendation for U1–U5:** Use single operating condition (1 keV, 15 pA, 1 nm probe, 1 μs dwell) as the baseline renderer. Conduct sensitivity analysis on uncertain parameters. If CD measurement bias from the simulator changes by <0.5 nm across the plausible range, freeze at nominal values.

---

## 4. Questions Deferred to Phase 2.5 (Renderer Design)

| # | Question | Domain |
|---|---|---|
| D1 | How should the 3D semiconductor structure be represented as input? | Data format |
| D2 | Should the renderer use ray-casting, rasterization, or a hybrid approach? | Rendering algorithm |
| D3 | How should the PSF convolution be implemented (spatial vs. frequency domain)? | Implementation |
| D4 | How should shot noise be generated (per-pixel Poisson sampling)? | Implementation |
| D5 | How should the material property lookup be done (per-pixel, per-triangle)? | Architecture |
| D6 | What coordinate system / geometry input format should be used? | Data format |
| D7 | Should the renderer handle isotropic or anisotropic pixel scales? | Rendering parameters |
| D8 | How is the detector collection efficiency per pixel computed? | Physics-Implementation interface |

---

## 5. Summary of Open Items for Applied Materials Decision

| Item | Type | Required By |
|---|---|---|
| **Probe diameter** (FWHM) — single value or range? | Parameter freeze | Phase 2.5 |
| **Beam energy** — one, few, or continuous? | Parameter freeze | Phase 2.5 |
| **Material escape depth** — final values | Parameter freeze | Phase 2.5 |
| **Charging reduction factor** — per insulator | Parameter freeze | Phase 2.5 |
| **PSF model** — Gaussian only or more complex? | Model selection | Phase 2.5 |
| **Noise model** — pure Poisson or with excess noise? | Model selection | Phase 2.5 |
| **Degree of realism** — essential only or recommended also? | Scope decision | Phase 2.5 |
