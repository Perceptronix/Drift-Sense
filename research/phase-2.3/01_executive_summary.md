# Phase 2.3 Executive Summary: From Emitted Electrons to the Grayscale SEM Image

**SEMICON 2026 Research Repository**
**Applied Materials**
**Date:** 2026-07-30
**Classification:** Research-Only (Phase 2.3)

---

## Purpose

Phase 2.2 established how the electron beam generates signals (SE, BSE, etc.) when it strikes a semiconductor wafer. Phase 2.3 answers the next question: **how do those emitted electrons become the final grayscale SEM image?**

This phase bridges the gap between signal generation physics and the visual appearance of SEM images — explaining why some areas appear bright, why edges glow, and how different semiconductor structures produce characteristic intensity profiles.

---

## Key Findings

### 1. The Signal-to-Image Pipeline

The conversion from emitted electrons to grayscale image involves six distinct stages:

```
SE/BSE Emission → Electron Transport in Vacuum → Detector Collection →
Scintillator & PMT → Amplifier & ADC → Pixel Mapping → Grayscale Image
```

Each stage imposes a transfer function that modulates the final pixel value. The detector collection function — which depends on detector geometry, bias, and position relative to the sample — is the most influential stage after the emission physics itself.

### 2. Topographic Contrast: The $\sec\theta$ Law

The dominant contrast mechanism in SE imaging is the dependence of SE yield on the local surface angle $\theta$ (measured from the surface normal):

$$\delta(\theta) = \delta_0 \cdot \frac{1}{\cos\theta}$$

**Fact:** This $\sec\theta$ law is the physical origin of topographic contrast. A surface tilted by 60° produces approximately 2× the SE signal of a flat surface. At 80°, the factor reaches ~5.8×.

**Why this matters for semiconductor metrology:** Pattern edges (sidewalls) have high local tilt angles (70°–90° from normal), producing the characteristic bright edges in CD-SEM images that enable edge detection and linewidth measurement.

### 3. Edge Brightening: The Critical Mechanism

Edge brightening in semiconductor SEM arises from three physical mechanisms:

| Mechanism | Contribution | Length Scale | Dominant For |
|---|---|---|---|
| **Angular (geometric) effect** — $\sec\theta$ yield increase at sidewalls | Primary (2–5× enhancement) | ~1–10 nm (probe-limited) | All edges |
| **Sidewall exposure** — BSE generated at the bottom of a trench can escape from the sidewall, increasing SE-II production | Secondary (1.5–2× enhancement) | ~10–100 nm | Deep trenches, high aspect ratios |
| **Corner enhancement** — 2D topography (vias, contacts) produces multiple adjacent high-tilt surfaces | Tertiary (3–8× for corners vs. 2–4× for edges) | ~1–10 nm | Contact holes, FinFET fins |

**Inference:** For semiconductor CD metrology, the angular (geometric) effect dominates. The sidewall exposure (SE-II) contribution broadens the bright edge region but does not shift the peak position used for edge detection.

### 4. Pixel Intensity Model

The complete grayscale formation model has the form:

$$I(x,y) = G \cdot \left[ \delta(\theta(x,y),\phi(x,y)) \cdot \eta_{\text{coll}}(x,y) + \eta(Z) \cdot \eta_{\text{coll,BSE}}(x,y) \right] + I_{\text{offset}}$$

where:
- $G$ = overall system gain (controllable)
- $\delta$ = local SE yield (dependent on surface angle and material)
- $\eta$ = local BSE yield (dependent on atomic number $Z$)
- $\eta_{\text{coll}}$ = detector collection efficiency (dependent on position and geometry)
- $I_{\text{offset}}$ = dark level signal

**Dominant variables for semiconductor CD-SEM:**
1. **Local surface angle $\theta$** — determines edge signal (the dominant effect for pattern imaging)
2. **Material $Z$** — determines baseline brightness between different materials
3. **Detector geometry** — determines which emitted electrons reach the detector
4. **Feature geometry** — determines shadowing and SE-II generation patterns

### 5. Line/Space Profiles

All semiconductor structures produce characteristic SE intensity profiles:

| Structure | SE Profile Shape | Key Feature for Metrology |
|---|---|---|
| Isolated line (CD > 50 nm) | Two bright peaks (edges), flat top | Peak-to-peak distance |
| Dense lines (pitch < 50 nm) | Modulated intensity with peaks at each edge | Valley-to-peak contrast |
| Trench | Bright edges, dark bottom | Edge position |
| Contact hole (isolated) | Bright annular ring | Ring diameter |
| Via | Similar to contact, depth-reduced signal | Ring position |
| FinFET | Very narrow double peak | Peak separation |
| DRAM cell | Complex periodic modulation | Pitch, depth contrast |

### 6. Contrast Model Comparison

| Model | Type | Accuracy | Speed | Suitability for Simulator |
|---|---|---|---|---|
| **Lambertian** | Simple geometric | Low (cosine) | Very fast | Too inaccurate for CD-SEM |
| **Yield ($\sec\theta$)** | First-principles | Moderate | Fast | **Recommended base model** |
| **Yield + detector** | Semi-empirical | Good | Fast | **Recommended for realism** |
| **Monte Carlo (MC)** | First-principles | Best | Very slow | Ground-truth reference only |
| **Empirical CD-SEM** | Data-driven | Good (for specific cases) | Fast | Useful if validated for target structures |

**Recommendation:** For a synthetic SEM simulator, use the **yield + detector response model** as the core engine. This captures the dominant physics (topographic contrast via $\sec\theta$, material contrast via Z) while remaining computationally tractable. Use Monte Carlo precomputation for calibration and validation, not per-pixel execution.

---

## Phase 2.4 Knowledge Required

1. How does noise (shot noise, detector noise) degrade the ideal signal profile and affect CD measurement precision?
2. How does image blur (finite probe size, electron diffusion, mechanical vibration) affect the edge profile shape and CD measurement accuracy?
3. How does sample charging modify the effective SE yield and distort the image?
4. How do drift and scan distortion affect measurement repeatability?
5. What is the complete instrument transfer function that converts the "ideal" image to the "measured" image?
6. How should CD-SEM measurement algorithms (threshold, linear regression, model-based) be implemented?
7. What are the trade-offs between measurement precision, accuracy, and throughput?

---

## Sources

- L. Reimer, *Scanning Electron Microscopy: Physics of Image Formation and Microanalysis*, 2nd ed. Springer, 1998.
- J. I. Goldstein, D. E. Newbury, J. R. Michael, et al., *Scanning Electron Microscopy and X-Ray Microanalysis*, 4th ed. Springer, 2017.
- J. S. Villarrubia, A. E. Vladar, and M. T. Postek, "Scanning electron microscope measurement of width and shape of fabricated nanostructures," *J. Res. NIST*, vol. 109, 2004.
- M. T. Postek and A. E. Vladar, "Critical dimension metrology," in *Handbook of Semiconductor Manufacturing Technology*, CRC Press, 2007.
- H. Seiler, "Secondary electron emission in the scanning electron microscope," *J. Appl. Phys.*, vol. 54, 1983.
- R. Shimizu and Z.-J. Ding, "Monte Carlo modelling of electron-solid interactions," *Rep. Prog. Phys.*, vol. 55, 1992.
- D. C. Joy, *Monte Carlo Modeling for Electron Microscopy and Microanalysis*. Oxford University Press, 1995.
- C. N. Archie, "Critical dimension metrology," *AIP Conf. Proc.*, vol. 788, 2005.
- Wikipedia, "Scanning Electron Microscope," accessed July 2026.
