# Phase 2.4 Executive Summary: Why Real SEM Images Are Imperfect

**SEMICON 2026 Research Repository**
**Applied Materials**
**Date:** 2026-07-30
**Classification:** Research-Only (Phase 2.4)

---

## Purpose

Phases 2.1–2.3 established how an ideal SEM image is formed — from beam generation through electron–sample interaction to contrast formation and grayscale pixel mapping. Phase 2.4 addresses the central question: **why is a real SEM image imperfect?**

This phase investigates every major degradation mechanism that separates real SEM images from the ideal model, establishing the physical understanding needed to add realistic degradation to synthetic images.

---

## Key Findings

### 1. Four Families of Degradation

All imperfections in real SEM images fall into four categories:

| Category | Root Cause | Examples | Impact on CD Metrology |
|---|---|---|---|
| **Blur** | Convolution of the ideal signal with a finite probe + beam broadening | Probe PSF, defocus, astigmatism, beam broadening in sample | Broadens edge profiles; reduces apparent edge contrast |
| **Noise** | Stochastic nature of electron generation and detection | Shot noise, PMT excess noise, amplifier noise, quantization noise | Limits measurement precision; increases edge detection variance |
| **Charging** | Net charge accumulation in insulating materials | Positive/negative surface charging, dielectric charging | Distorts beam position; alters effective SE yield; introduces drift |
| **Artifacts** | Instrumental or sample-induced non-idealities | Scan distortion, drift, vibration, detector saturation, banding | Degrades image fidelity; can cause systematic CD bias |

### 2. Blur: The Finite Probe

The dominant blur mechanism in CD-SEM is **the convolution of the sample's ideal signal with the probe current density distribution**. The effective point spread function (PSF) has multiple components:

$$\text{PSF}_{\text{total}}^2 = \text{PSF}_{\text{probe}}^2 + \text{PSF}_{\text{aberr}}^2 + \text{PSF}_{\text{broadening}}^2 + \text{PSF}_{\text{vibration}}^2$$

| Component | Typical Magnitude (CD-SEM, 1 keV) | Dominance |
|---|---|---|
| **Gaussian probe** (source + condenser) | 0.5–1.5 nm FWHM | **Dominant** |
| **Lens aberrations** ($C_s$, $C_c$) | 0.2–0.5 nm | Moderate (at optimum aperture) |
| **Beam broadening** in sample | 0.5–3 nm (energy-dependent) | **Significant** for SE-II |
| **Diffraction** | <0.1 nm at 1 keV | Negligible |
| **Vibration** | 0.1–0.3 nm | Small (in well-isolated tools) |

**Fact:** For a well-tuned CD-SEM at 1 keV, the total effective resolution (10–90% edge rise distance) is approximately 1.5–3 nm, limited primarily by the Gaussian probe diameter.

### 3. Noise: Shot Noise Dominates

The fundamental noise source in SEM is **shot noise** — the Poisson statistics of electron detection:

$$\sigma_{\text{shot}} \propto \sqrt{N_{\text{detected}}}$$

where $N_{\text{detected}}$ is the number of detected electrons per pixel.

| Noise Source | Magnitude (relative units) | Typically Dominant? |
|---|---|---|
| **Shot noise** (SE/BSE detection) | $\sqrt{N}$ | **Yes** — fundamental limit |
| **PMT excess noise** | 1.1–1.3× shot noise | Adds 10–30% to shot noise |
| **Amplifier (Johnson) noise** | Depends on bandwidth | Minor at typical CD-SEM currents |
| **Quantization noise** | $\Delta / \sqrt{12}$ | Negligible (16-bit ADC) |
| **Dark current** | <1 electron/pixel | Negligible (cooled PMT) |

**Fact:** The signal-to-noise ratio in a CD-SEM is fundamentally limited by the number of detected electrons per pixel. For a typical 15 pA probe current, 1 μs dwell time, and 10% detection efficiency, only ~1,000 electrons are detected per pixel, giving a maximum SNR of ~30:1.

### 4. Charging: The Most Complex Degradation

Charging is the most difficult degradation mechanism to model because it affects the image in multiple ways simultaneously:

| Charging Effect | Physical Mechanism | Visual Appearance |
|---|---|---|
| **SE yield modification** | Surface potential changes effective $\delta$ | Altered brightness | 
| **Secondary electron trajectory deflection** | Local field repels/attracts SEs | Dark/bright halos |
| **Primary beam deflection** | Surface field deflects the beam | Local distortion, "waterfall" effect |
| **Drift** | Accumulating charge changes surface potential over time | Progressive image shift |
| **Flashover/discharge** | Sudden breakdown of insulating layer | Sharp bright streaks |

**Inference:** For the Applied Materials challenge, charging is the most complex degradation to model. A simplified model (effective potential → SE yield modification) captures the first-order effect, while full charging simulation requires self-consistent field calculation.

### 5. Engineering Classification

All degradation mechanisms classified for the synthetic SEM renderer:

| Tier | Count | Includes |
|---|---|---|
| **Essential** | 4 | Gaussian probe PSF, shot noise, effective SNR model, contrast degradation from charging |
| **Recommended** | 5 | Defocus, astigmatism, PMT excess noise, beam broadening, scan distortion |
| **Optional** | 6 | Vibration, drift, detector saturation, banding, flashover, dead pixels |
| **Ignore** | 5 | Most artifact types (line skipping, frame averaging effects, etc.) for first implementation |

**Recommendation:** Start with the **4 essential** mechanisms. Add the **5 recommended** ones in subsequent iterations. The **optional** and **ignore** categories can be deferred indefinitely for the target application.

---

## Phase 2.5 Knowledge Required

This is the final research phase before renderer design. Phase 2.5 must:

1. **Freeze the forward model parameters** — specify every parameter value (probe diameter, beam current, dwell time, pixel size, noise magnitude, charging level) as concrete constants for the renderer.

2. **Define the image formation equation** — the complete mathematical model from ideal contrast image to degraded pixel values, incorporating all essential degradation mechanisms.

3. **Specify the geometry input format** — how the 3D structure (material IDs, surface normals, heights) is provided to the renderer.

4. **Choose the rendering approach** — ray-casting vs. rasterization; analytical vs. hybrid; CPU vs. GPU; once the physics is frozen.

5. **Define the output format** — pixel resolution, bit depth, file format, metadata requirements.

---

## Sources

- L. Reimer, *Scanning Electron Microscopy: Physics of Image Formation and Microanalysis*, 2nd ed. Springer, 1998.
- J. I. Goldstein, D. E. Newbury, J. R. Michael, et al., *Scanning Electron Microscopy and X-Ray Microanalysis*, 4th ed. Springer, 2017.
- D. C. Joy, *Monte Carlo Modeling for Electron Microscopy and Microanalysis*. Oxford University Press, 1995.
- R. F. Egerton, *Physical Principles of Electron Microscopy*, 2nd ed. Springer, 2016.
- J. S. Villarrubia, A. E. Vladar, and M. T. Postek, "Scanning electron microscope measurement of width and shape of fabricated nanostructures," *J. Res. NIST*, vol. 109, 2004.
- M. T. Postek and A. E. Vladar, "Critical dimension metrology," in *Handbook of Semiconductor Manufacturing Technology*, CRC Press, 2007.
- A. E. Vladar, M. T. Postek, and R. Vane, "CD-SEM and the 45-nm node," *Proc. SPIE*, vol. 6518, 2007.
- C. N. Archie, "Critical dimension metrology," *AIP Conf. Proc.*, vol. 788, 2005.
- Wikipedia, "Point Spread Function," accessed July 2026.
- Wikipedia, "Shot noise," accessed July 2026.
- Wikipedia, "Scanning Electron Microscope," accessed July 2026.
