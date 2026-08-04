# Canonical Rendering Pipeline

**Research Phase:** 2.5
**Document:** 04_canonical_rendering_pipeline.md
**Date:** 2026-07-30

---

## 1. Pipeline Overview

The rendering pipeline consists of 14 stages organized into 4 phases:

```
┌─────────────────────────────────────────────────────────────────────┐
│  PRE-PROCESSING (deterministic geometry)                            │
├─────────────────────────────────────────────────────────────────────┤
│  1. Geometry Loading & Validation                                   │
│  2. Material Assignment                                             │
│  3. Surface Normal Computation                                      │
└─────────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────────┐
│  SIGNAL GENERATION (deterministic physics)                          │
├─────────────────────────────────────────────────────────────────────┤
│  4. SE Yield Estimation                                             │
│  5. BSE Yield Estimation                                            │
│  6. Detector Collection Efficiency                                  │
│  7. SE-II Background Calculation                                    │
│  8. Raw Pixel Intensity (no blur, no noise)                         │
└─────────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────────┐
│  DEGRADATION (blur, charging, noise)                                │
├─────────────────────────────────────────────────────────────────────┤
│  9. Probe PSF Convolution (Gaussian blur)                           │
│  10. Charging Correction (yield reduction)                          │
│  11. Gain Scaling & Offset                                          │
│  12. Shot Noise (Poisson)                                           │
│  13. PMT Excess Noise                                               │
└─────────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────────┐
│  DIGITIZATION                                                       │
├─────────────────────────────────────────────────────────────────────┤
│  14. ADC Saturation & Quantization                                  │
│  → Final Image                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Stage-by-Stage Specification

### Stage 1: Geometry Loading & Validation

| Aspect | Specification |
|---|---|
| **Input** | 3D structure file (2.5D height map format: per-pixel height + material ID) |
| **Process** | Validate format, dimensions, material IDs. Ensure no out-of-range values. |
| **Output** | Validated height field $h(x,y)$ and material ID field $m(x,y)$ |
| **Dependencies** | None |
| **Reference** | ISO 16700, SEM image magnification calibration [T2] |

### Stage 2: Material Assignment

| Aspect | Specification |
|---|---|
| **Input** | Material ID field $m(x,y)$ |
| **Process** | Map each material ID to a property vector: $\{\delta_0, \eta, \Lambda, f_c, \gamma\}$ |
| **Output** | Per-pixel material property arrays |
| **Dependencies** | Material library (loaded once at initialization) |
| **Reference** | Phase 2.2, Document 06; Reimer [B1] |

### Stage 3: Surface Normal Computation

| Aspect | Specification |
|---|---|
| **Input** | Height field $h(x,y)$ |
| **Process** | Compute surface normal $\hat{n}(x,y)$ from height gradients: $n_x = \partial h / \partial x$, $n_y = \partial h / \partial y$, $n_z = -1$ (downward). Normalize. Then $\cos\theta = \hat{n} \cdot \hat{z}$ |
| **Output** | Surface normal map $\hat{n}(x,y)$, local angle map $\theta(x,y)$ |
| **Dependencies** | None |
| **Reference** | Standard 2.5D geometry processing |

**Engineering Decision:** Gradients are computed using central finite differences for interior pixels and forward/backward at edges. This O(M×N) computation is trivial.

### Stage 4: SE Yield Estimation

| Aspect | Specification |
|---|---|
| **Input** | $\delta_0(x,y)$ per material, $\theta(x,y)$, $\gamma$ |
| **Process** | $\delta(x,y) = \delta_0 \cdot \sec^\gamma(\theta(x,y))$, clamped for $\theta > 70^\circ$ |
| **Output** | Per-pixel SE yield $\delta(x,y)$ |
| **Dependencies** | Stage 3 (surface normals), Stage 2 (material $\delta_0$) |
| **Reference** | Seiler [J7], Reimer [B1] |

### Stage 5: BSE Yield Estimation

| Aspect | Specification |
|---|---|
| **Input** | $\eta(Z)$ per material |
| **Process** | Lookup $\eta(x,y)$ from material library. No angular dependence (BSE angular dependence is handled by the detector model). |
| **Output** | Per-pixel BSE yield $\eta(x,y)$ |
| **Dependencies** | Stage 2 (material library) |
| **Reference** | Reimer [B1], Joy [B4] |

### Stage 6: Detector Collection Efficiency

| Aspect | Specification |
|---|---|
| **Input** | Surface normal $\hat{n}$, pixel position $(x,y)$, detector geometry |
| **Process** | For TTL (default): $\eta_{\text{coll}}^{\text{SE}} = 0.7$ (constant). For enhanced: compute solid angle. For BSE annular: $\eta_{\text{coll}}^{\text{BSE}} = 0.5$ (constant). |
| **Output** | $\eta_{\text{coll}}^{\text{SE}}(x,y)$, $\eta_{\text{coll}}^{\text{BSE}}(x,y)$ |
| **Dependencies** | Stage 3 (surface normals) |
| **Reference** | Reimer [B1] Chapter 6, Goldstein [B2] Chapter 4 |

### Stage 7: SE-II Background Calculation

| Aspect | Specification |
|---|---|
| **Input** | Primary yield map $\delta(x,y)$, BSE yield $\eta(x,y)$ |
| **Process** | Convolve $\eta(x,y)$ with exponential kernel: $$I_{\text{SE-II}}(x,y) = k_{\text{SE-II}} \cdot \eta(x,y) * \exp(-r / L_{\text{SE-II}})$$ |
| **Output** | SE-II background map $I_{\text{SE-II}}(x,y)$ |
| **Dependencies** | Stage 5 (BSE yield) |
| **Reference** | Phase 2.2, Reimer [B1] |

### Stage 8: Raw Pixel Intensity

| Aspect | Specification |
|---|---|
| **Input** | $\delta$, $\eta$, $\eta_{\text{coll}}^{\text{SE}}$, $\eta_{\text{coll}}^{\text{BSE}}$, $I_{\text{SE-II}}$, $I_P$, $\tau$ |
| **Process** | $$I_{\text{raw}}(x,y) = \frac{I_P \tau}{e} \left[ \delta \cdot \eta_{\text{coll}}^{\text{SE}} + \eta \cdot \eta_{\text{coll}}^{\text{BSE}} \right] + I_{\text{SE-II}}$$ |
| **Output** | Raw intensity map (units: electrons per pixel, before gain) |
| **Dependencies** | Stages 4, 5, 6, 7 |
| **Reference** | Phase 2.3, Document 05 |

### Stage 9: Probe PSF Convolution (Blur)

| Aspect | Specification |
|---|---|
| **Input** | Raw intensity $I_{\text{raw}}(x,y)$, probe diameter $d_p$, escape depth $\Lambda(x,y)$ |
| **Process** | $$\sigma_p = d_p / 2.355$$ $$\sigma_m(x,y) = \Lambda(x,y) / 2.355$$ $$\sigma_{\text{eff}}^2(x,y) = \sigma_p^2 + \sigma_m^2(x,y)$$ $$I_{\text{blurred}} = I_{\text{raw}} * G(\sigma_{\text{eff}})$$ |
| **Output** | Blurred intensity map |
| **Dependencies** | Stage 8 (raw intensity), Stage 2 (material $\Lambda$) |
| **Reference** | Phase 2.4, Document 02 |

### Stage 10: Charging Correction

| Aspect | Specification |
|---|---|
| **Input** | $\delta(x,y)$, charging factor $f_c(x,y)$ |
| **Process** | For each pixel: if material is insulator, $\delta_{\text{eff}} = \delta(x,y) \cdot f_c$. Recompute intensity with modified $\delta$. |
| **Output** | Charge-corrected intensity map |
| **Dependencies** | Stage 2 (material $f_c$), Stage 4 (SE yield) |
| **Reference** | Phase 2.4, Document 04 |

### Stage 11: Gain Scaling & Offset

| Aspect | Specification |
|---|---|
| **Input** | Intensity in electrons/pixel, system gain $G$, offset $I_{\text{off}}$ |
| **Process** | $$I_{\text{scaled}}(x,y) = I_{\text{blurred}}(x,y) \cdot G + I_{\text{off}}$$ |
| **Output** | Scaled intensity (analog voltage, arbitrary units) |
| **Dependencies** | Stage 9 (blurred intensity), Stage 10 (charging) |
| **Reference** | Phase 2.3, Document 02 |

### Stage 12: Shot Noise

| Aspect | Specification |
|---|---|
| **Input** | Scaled intensity, effective gain $G_{\text{eff}}$ |
| **Process** | $$I_{\text{shot}} \sim \text{Poisson}\left(\frac{I_{\text{scaled}}}{G_{\text{eff}}}\right) \cdot G_{\text{eff}}$$ |
| **Output** | Noise-corrupted intensity |
| **Dependencies** | Stage 11 |
| **Reference** | Phase 2.4, Document 03 |

### Stage 13: PMT Excess Noise

| Aspect | Specification |
|---|---|
| **Input** | Shot noise intensity, excess noise factor $F$ |
| **Process** | $$I_{\text{noisy}} = I_{\text{shot}} + \sqrt{(F^2 - 1) \cdot I_{\text{shot}} \cdot G_{\text{eff}}} \cdot \mathcal{N}(0,1)$$ |
| **Output** | Final analog intensity |
| **Dependencies** | Stage 12 |
| **Reference** | Phase 2.4, Document 03 |

### Stage 14: ADC Digitization

| Aspect | Specification |
|---|---|
| **Input** | Analog intensity $I_{\text{noisy}}$, ADC resolution $N_{\text{bits}}$, max voltage $V_{\text{max}}$ |
| **Process** | $$I_{\text{pixel}} = \left\lfloor \min\left(\max\left(\frac{I_{\text{noisy}}}{V_{\text{max}}}, 0\right), 1\right) \cdot (2^{N_{\text{bits}}} - 1) + 0.5 \right\rfloor$$ |
| **Output** | Final 16-bit grayscale pixel value |
| **Dependencies** | Stage 13 |
| **Reference** | Phase 2.4, Document 06 |

---

## 3. Pipeline Ordering Justification

| Stage # | Why This Position |
|---|---|
| **1–3** (Geometry) | First because all subsequent physics depends on knowing what the sample looks like. |
| **4–6** (Yields) | Must follow geometry (yields depend on material and angle). Must precede intensity calculation. |
| **7** (SE-II) | SE-II is a signal component, not a degradation — it adds signal, not blur. Placed before blur because SE-II has its own spatial distribution. |
| **8** (Raw intensity) | The first "image" — no blur, no noise. Pure physical signal. Useful for debugging. |
| **9** (Blur) | Applied before noise because blur is deterministic and reduces high-frequency signal energy. Blurring after noise would incorrectly smooth noise (a common mistake). |
| **10** (Charging) | Applied during or before intensity calculation. Charging modifies the effective yield before gain and noise. |
| **11** (Gain) | Gain converts physical units (electrons) to electronics units (volts). Must precede electronic noise sources. |
| **12–13** (Noise) | Noise is best added last in the analog chain. Shot noise is signal-dependent, so it must follow gain. |
| **14** (ADC) | Digitization is the final step — converting the analog voltage to digital pixel values. |

**Engineering Decision:** The ordering ensures that:
- Deterministic physics (yields, geometry) is computed first.
- Blur is applied to the signal before adding noise (correct for SEM).
- Noise is added in the analog domain before digitization (correct for the hardware chain).

---

## 4. Intermediate Outputs for Validation

| Stage | Intermediate Output | Validation Purpose |
|---|---|---|
| Stage 3 | Surface normal map | Verify correct geometry interpretation |
| Stage 8 | Raw intensity (pre-blur, pre-noise) | Verify yield model produces correct material contrast |
| Stage 9 | Blurred intensity | Verify PSF convolution produces correct edge profile width |
| Stage 11 | Scaled intensity | Verify gain and offset are applied correctly |
| Stage 13 | Full analog signal | Verify noise statistics match Poisson distribution |
| Stage 14 | Final image | Verify pixel values are in expected range (0–65535 for 16-bit) |

---

## 5. Pipeline Variations (Future Phases)

### 5.1 Fast Mode (Phase A, No Degradation)

```
1 → 2 → 3 → 4 → 5 → 6 → 8 → 11 → 14
```

Skips SE-II, PSF, charging, and noise. Produces a noiseless, sharp image for quick validation.

### 5.2 High-Realism Mode (Phase C+, Full Degradation)

Full 14-stage pipeline. Optionally add:
- Frame averaging (loop Stages 12–14 with different noise realizations)
- Drift (position offset varying per frame)
- Distortion (polynomial warp before Stage 14)

---

## Sources

- [B1] L. Reimer, *Scanning Electron Microscopy: Physics of Image Formation and Microanalysis*, 2nd ed. Springer, 1998.
- [B2] J. I. Goldstein, D. E. Newbury, J. R. Michael, et al., *Scanning Electron Microscopy and X-Ray Microanalysis*, 4th ed. Springer, 2017.
- [J7] H. Seiler, "Secondary electron emission in the scanning electron microscope," *J. Appl. Phys.*, vol. 54, 1983.
- [T2] ISO 16700, "Microbeam analysis — Guidelines for calibrating image magnification."
