# Phase 2.3 Final Report: From Emitted Electrons to the Grayscale SEM Image

**SEMICON 2026 Research Repository**
**Applied Materials**
**Date:** 2026-07-30
**Classification:** Research-Only (Phase 2.3)

---

## Executive Summary

Phase 2.3 answers the question: **"How do emitted electrons become the final grayscale SEM image?"** This phase bridges signal generation physics (Phase 2.2) with the visual appearance of SEM images — explaining why some areas appear bright, why edges glow, and how different semiconductor structures produce characteristic intensity profiles.

### Key Results

1. **The $\sec\theta$ law is the dominant contrast mechanism.** SE yield increases as $1/\cos\theta$ with surface tilt, producing 2–10× signal enhancement at pattern edges. This single mechanism explains both topographic contrast and edge brightening.

2. **Edge brightening has three physical origins:** geometric ($\sec\theta$) enhancement at sidewalls (primary), SE-II generation from BSE exiting sidewalls (secondary), and 2D corner effects (tertiary). For CD metrology, the geometric effect is the most important.

3. **The pixel intensity model** combines SE yield ($\delta_0$), BSE yield ($\eta$), $\sec\theta$ angular factor, detector collection efficiency ($\eta_{\text{coll}}$), and system gain. Local surface angle $\theta$ is the dominant variable (1–11× variation), followed by material $Z$ (0.7–2.5×).

4. **Five essential components** are identified for a synthetic SEM simulator: material property library, $\sec\theta$ topographic contrast, BSE compositional contrast, Gaussian probe convolution, and the basic pixel intensity equation.

5. **Recommended forward model:** The $\sec\theta$ + detector + combined SE/BSE model, calibrated against Monte Carlo for accuracy.

---

## 1. Phase Results by Document

### 1.1 Signal-to-Image Pipeline (Document 02)

The conversion from emitted electrons to grayscale image involves six stages:
1. **Emission** — SE and BSE generation at the sample surface.
2. **Transport** — Electron trajectories from sample to detector through vacuum, influenced by collection fields.
3. **Detection** — Scintillator + PMT conversion with gain of $10^5$–$10^7$.
4. **Amplification** — Transimpedance and video amplification with bandwidth matching dwell time.
5. **Digitization** — ADC conversion to N-bit digital values (8–16 bit).
6. **Mapping** — Grayscale transfer function (linear or gamma) for display.

The collection efficiency $\eta_{\text{coll}}$ is the most influential stage after the emission physics itself.

### 1.2 SE Contrast (Document 03)

| Contrast Mechanism | Physical Origin | Magnitude |
|---|---|---|
| **Topographic ($\sec\theta$)** | Surface tilt increases SE yield | 1–10× |
| **Material (Z)** | Different SE yields per material | 1–3× |
| **Collection anisotropy** | Detector position preference | 1–5× |
| **Shadowing** | Topography blocks SE paths | 0–1× |
| **Voltage contrast** | Local fields modify SE/BSE emission | 0.1–2× |

### 1.3 Edge Brightening (Document 04)

**Mechanisms ranked by importance:**
1. **Geometric ($\sec\theta$) effect** (primary, 2–10× enhancement)
2. **SE-II sidewall escape** (secondary, 1.5–2× broadening)
3. **Corner enhancement** (tertiary, 3–8× at 2D corners)

**Recommendation:** For the simulator, the $\sec\theta$ model captures the primary origin. SE-II broadening is required for correct profile shape. Corner effects are useful for contact/via simulation.

### 1.4 Pixel Intensity Models (Document 05)

The complete model:

$$I(x,y) = G \cdot I_P \tau \cdot \left[ \delta_0(Z) \cdot \sec\theta(x,y) \cdot \eta_{\text{coll}}(x,y) + \eta(Z) \cdot \eta_{\text{coll,BSE}}(x,y) + \Delta_{\text{SE-II}}(x,y) \right] + I_{\text{off}}$$

**Dominant variables ranked:**
1. Local surface angle $\theta$ (1–10× variation)
2. Material $Z$ via $\delta_0$ and $\eta$ (0.7–2.5×)
3. Detector collection efficiency $\eta_{\text{coll}}$ (0–1×)

### 1.5 Line/Space Profiles (Document 06)

All semiconductor structures produce characteristic SE profiles. Key findings:

| Structure | Profile Shape | Metrology Feature |
|---|---|---|
| **Isolated line** | Two bright peaks | Peak separation |
| **Dense lines** | Periodic peaks | Pitch, edge positions |
| **Contact hole** | Bright annulus | Ring diameter |
| **FinFET** | Narrow double peak | Peak separation |

The edge brightening peaks mark pattern edges, enabling CD measurement.

### 1.6 Contrast Model Comparison (Document 07)

| Model | Recommendation | Rationale |
|---|---|---|
| **Lambertian** | **Reject** | Physically wrong for SE emission |
| **$\sec\theta$** | **Base model** | Captures dominant contrast |
| **$\sec\theta$ + detector** | **Recommended** | Best balance of accuracy and speed |
| **Combined SE/BSE** | **For realism** | Adds compositional contrast |
| **MC (full)** | **Ground truth** | Too slow for real-time use |
| **Hybrid MC + analytical** | **Best approach** | Balances accuracy and computational cost |

### 1.7 Engineering Conclusions (Document 08)

**Five essential components for first implementation:**
1. Material property library ($\delta_0$, $\eta$ per material)
2. $\sec\theta$ topographic contrast model
3. BSE compositional contrast
4. Gaussian probe convolution
5. Basic pixel intensity equation (scaling + offset)

These five components will produce physically realistic SEM images of semiconductor structures suitable for CD metrology algorithm development.

---

## 2. Critical Unresolved Questions

| # | Question | Impact |
|---|---|---|
| U1 | What is the exact $\sec\theta$ correction factor for $\theta > 70^\circ$? | Affects edge peak amplitude at near-vertical sidewalls |
| U2 | What is the precise SE-II spatial distribution function for typical CD-SEM conditions? | Affects edge profile tail width |
| U3 | What is the optimal detector collection model for TTL detection in modern CD-SEM? | Affects absolute signal level and asymmetry |
| U4 | What is the correct $\delta_0(Z)$ value for each material at each CD-SEM energy? | Material contrast accuracy |

**Recommendation:** Use Monte Carlo simulations (CASINO) to calibrate the simpler analytical model for the specific materials and energies of interest.

---

## 3. Knowledge Required for Phase 2.4

Phase 2.3 has established **how the ideal grayscale image is formed** from the emitted electron signals. Phase 2.4 must address the question:

**How does the "perfect" image from Phase 2.3 become degraded by noise, blur, and artifacts in a real SEM?**

### Required Topics

#### Noise
1. What is shot noise in electron detection and how does Poisson statistics govern the pixel intensity distribution?
2. What are the detector noise contributions (PMT excess noise, Johnson noise, amplifier noise)?
3. How does pixel dwell time and beam current determine the signal-to-noise ratio?
4. How does frame averaging reduce noise and what are the practical limits?
5. What are the noise characteristics of a CD-SEM image and how does noise affect edge detection precision?

#### Blur and Resolution
6. What is the point spread function (PSF) of an SEM and what are its physical components?
7. How does the finite probe diameter contribute to image blur (probe PSF)?
8. How does electron diffusion and SE generation in the sample contribute to signal delocalization?
9. How do microscope instabilities (vibration, magnetic interference, thermal drift) contribute to blur?
10. What is the effective modulation transfer function (MTF) of a CD-SEM?

#### Charging and Artifacts
11. How does sample charging modify the effective SE yield and distort the image?
12. How does charging affect CD measurement accuracy?
13. What are the common SEM image artifacts (scan distortion, banding, edge ringing) and their physical origins?

#### Complete Instrument Model
14. How should the instrument transfer function be formulated to convert the "ideal" image to the "measured" image?
15. What is the complete forward model from ideal contrast to measured pixel values including all degradation effects?

### Scope of Phase 2.4

Phase 2.4 should produce a comprehensive understanding of:
- **Noise statistics** of electron detection and the SNR-limited precision of CD measurements
- **Blur mechanisms** that degrade spatial resolution beyond the probe diameter
- **Charging physics** and its effects on SEM imaging
- **Common artifacts** and their physical origins
- **The complete instrument forward model** that transforms the ideal contrast image into a realistic simulated SEM image

This knowledge is the final prerequisite before a physically realistic SEM renderer can be specified and built.

---

## 4. Phase 2.3 Success Criteria

| Criterion | Status | Evidence |
|---|---|---|
| ✓ Why SEM images appear bright or dark | Achieved | Documents 03, 05 ($\sec\theta$, material Z) |
| ✓ Why semiconductor edges become bright | Achieved | Document 04 (edge brightening mechanisms) |
| ✓ How grayscale intensity is formed | Achieved | Document 05 (pixel intensity model) |
| ✓ How semiconductor structures produce characteristic profiles | Achieved | Document 06 (line/space profiles) |
| ✓ Which contrast models the renderer should use | Achieved | Documents 07, 08 (model comparison, engineering conclusions) |
| ✓ Without image degradation or artifacts | Maintained | Deferred to Phase 2.4 |

---

## 5. Phase 2.3 Document Map

```
research/phase-2.3/
│
├── 01_executive_summary.md              ← High-level overview
├── 02_signal_to_image_pipeline.md        ← 6-stage emission-to-image pipeline
├── 03_secondary_electron_contrast.md     ← All SE contrast mechanisms
├── 04_edge_brightening.md                ← Edge brightening physics and models
├── 05_pixel_intensity_models.md          ← Complete grayscale formation model
├── 06_line_space_image_profiles.md       ← Characteristic profiles for all structures
├── 07_contrast_model_comparison.md       ← Comparison of 9 published models
├── 08_engineering_conclusions.md         ← Essential/useful/ignore classification
├── 09_complete_reference_list.md         ← All cited sources
└── 10_phase2_3_final_report.md           ← This consolidated report
```

---

*End of Phase 2.3 Final Report*
