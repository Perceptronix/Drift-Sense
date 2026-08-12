# Engineering Classification

**Research Phase:** 2.4
**Document:** 07_engineering_classification.md
**Date:** 2026-07-30

---

## 1. Purpose

This document classifies every degradation mechanism from Phase 2.4 into implementation tiers for the synthetic SEM image renderer. The classification is based on:

1. **Physical impact** — Does the mechanism significantly change the image for semiconductor structures?
2. **Engineering complexity** — Is the mechanism practical to model without a full hardware simulation?
3. **Relevance to CD metrology** — Does the mechanism affect edge detection or linewidth measurement accuracy?

---

## 2. Classification Tiers

| Tier | Definition | Action |
|---|---|---|
| **Essential** | Without modeling this, the synthetic image is not physically realistic for semiconductor metrology | Must implement in core renderer |
| **Recommended** | Improves realism or quantitative accuracy; justifies the implementation effort | Add in subsequent iterations |
| **Optional** | Adds minor realism; model only if the target application requires it | Implement when needed |
| **Can ignore** | Effect too small, unpredictable, or irrelevant for semiconductor CD-SEM | Document but do not implement |

---

## 3. Blur Mechanisms

### 3.1 Probe PSF

| Mechanism | Tier | Justification |
|---|---|---|
| **Gaussian probe PSF (finite probe diameter)** | **Essential** | The single most important degradation mechanism. Without finite probe convolution, edge profiles are unrealistically sharp. |
| **Beam broadening in sample (SE escape depth)** | **Essential** | Material-dependent resolution limit. Determines the difference between edge profiles on metals vs. insulators. |
| **SE-II long-range background** | **Recommended** | Broadens edge profile tails. Important for accurate profile shape at line/space pattern bases. |
| **Defocus** | **Optional** | Small effect if autofocus is assumed (<10% increase in probe diameter). Model only if simulating focus variation. |
| **Astigmatism** | **Optional** | Negligible in modern CD-SEM with autostigmation. Model only for off-nominal conditions. |
| **Spherical aberration** | **Optional** | Captured within the effective Gaussian probe diameter at optimum aperture. |
| **Chromatic aberration** | **Optional** | Captured within the effective Gaussian probe diameter. Dominant at low kV but included in the effective $d_p$. |
| **Diffraction** | **Can ignore** | <0.1 nm at CD-SEM energies. Several orders of magnitude smaller than probe diameter. |

**Recommendation for PSF model:**

$$\text{PSF}(r) = \frac{1}{2\pi(\sigma_p^2 + \sigma_m^2)} \exp\left(-\frac{r^2}{2(\sigma_p^2 + \sigma_m^2)}\right)$$

where $\sigma_p$ is from the probe diameter and $\sigma_m$ is from the material-dependent SE escape depth. This combined Gaussian captures the essential blur with a single parameter per material.

### 3.2 Mechanical and Environmental Blur

| Mechanism | Tier | Justification |
|---|---|---|
| **Vibration** | **Optional** | Adds Gaussian blur with tool-dependent amplitude (0.1–0.3 nm for well-isolated tools). Model as additional Gaussian if amplitude is significant. |
| **Magnetic interference** | **Can ignore** | 50/60 Hz periodic displacement, typically <0.5 nm. Difficult to model generically. |

---

## 4. Noise Mechanisms

### 4.1 Primary Noise Sources

| Noise Source | Tier | Justification |
|---|---|---|
| **Shot noise (Poisson)** | **Essential** | Fundamental noise limit in electron detection. Without shot noise, images are unrealistically smooth. Must be signal-dependent. |
| **PMT excess noise** | **Recommended** | Adds 10–30% to shot noise. Simple to model as a variance scaling factor. |
| **Amplifier (Johnson) noise** | **Optional** | Typically 1–10% of shot noise magnitude. Model only for high-bandwidth (fast scan) scenarios. |
| **Quantization noise** | **Optional** | Negligible for 16-bit ADC (<1% of shot noise). Model only for 8-bit output. |
| **Dark current** | **Can ignore** | <1 electron per pixel at typical dwell times. |
| **Scan noise** | **Can ignore** | <0.1% of scan range. |
| **Source emission noise** | **Can ignore** | Low-frequency drift, not pixel-to-pixel noise. |

**Recommendation for noise model:**

$$I_{\text{noisy}}(x,y) = \text{Poisson}\left(\frac{I_{\text{ideal}}(x,y)}{G_{\text{eff}}}\right) \cdot G_{\text{eff}}$$

where $I_{\text{ideal}}$ is the noiseless pixel intensity in digital units, and $G_{\text{eff}}$ is the effective gain relating detected electrons to digital units. The Poisson distribution naturally captures the signal-dependent noise.

---

## 5. Charging Mechanisms

| Mechanism | Tier | Justification |
|---|---|---|
| **SE yield modification by surface charge** | **Essential** | Directly alters pixel intensity on insulating regions. Without this, insulators appear unrealistically bright. |
| **Contrast reduction from charging** | **Recommended** | Reduces material contrast on insulating regions. Effect is partially captured by SE yield modification. |
| **Beam deflection by surface potential** | **Optional** | Complex to model; significant only for strong charging or high-aspect-ratio features. |
| **Progressive charging drift** | **Optional** | Time-dependent; only relevant for long acquisitions on thick insulators. |
| **Dielectric flashover/discharge** | **Can ignore** | Rare, unpredictable, not systematic. |

**Recommendation for charging model (simplified):**

For a first implementation, apply a **material-dependent effective SE yield reduction** for insulating materials:

$$\delta_{\text{eff}} = \delta_0 \times \begin{cases}
0.7\text{–}0.9 & \text{(mild charging, } \sigma \approx 1.2\text{–}1.5) \\
0.4\text{–}0.7 & \text{(moderate charging, } \sigma \approx 1.5\text{–}2.0) \\
0.2\text{–}0.4 & \text{(strong charging, } \sigma > 2.0)
\end{cases}$$

This simplified model captures the first-order visual effect without a self-consistent electrostatic simulation.

---

## 6. Artifacts

| Artifact | Tier | Justification |
|---|---|---|
| **Detector saturation (edge blooming)** | **Recommended** | Simple clip function at maximum pixel value. Important when simulating high-contrast edges. |
| **Scan distortion (full FOV)** | **Optional** | Only relevant for full-field images (FOV > 1 μm). Polynomial distortion model. |
| **Drift (progressive)** | **Optional** | Only relevant for frame-averaged simulation or very long acquisitions. |
| **Vibration artifacts** | **Optional** | Model as additional Gaussian blur for poor environments. |
| **SE-II halo** | **Recommended** | Already part of the SE-II model from Phase 2.3. Long-range convolution kernel. |
| **Banding (periodic)** | **Can ignore** | <1% amplitude in modern CD-SEM. |
| **Streaking** | **Can ignore** | Unpredictable, tool-dependent. |
| **Dead pixels** | **Can ignore** | Corrected by CD-SEM calibration. |
| **Line skipping** | **Can ignore** | Rare timing glitch. |

---

## 7. Instrument Parameters

| Parameter | Tier | Justification |
|---|---|---|
| **Probe diameter (effective Gaussian)** | **Essential** | Sets the overall resolution of the simulated image. |
| **Probe current** | **Essential** | Scales shot noise and SNR. |
| **Pixel dwell time** | **Essential** | Scales shot noise and SNR. |
| **Pixel size** | **Essential** | Determines sampling. |
| **Beam energy (via SE yield library)** | **Essential** | Controls contrast magnitudes. |
| **Frame averaging** | **Recommended** | Modifies SNR and drift effects. |
| **ADC bit depth** | **Optional** | 16-bit is essentially ideal. |
| **PMT gain** | **Optional** | Captured in the overall gain calibration. |

---

## 8. Comprehensive Classification Table

| # | Mechanism | Category | Tier | Model Complexity |
|---|---|---|---|---|
| 1 | Gaussian probe PSF | Blur | **Essential** | Convolution kernel |
| 2 | Beam broadening / escape depth | Blur | **Essential** | Material-dependent $\sigma$ |
| 3 | Shot noise (Poisson) | Noise | **Essential** | Per-pixel random variate |
| 4 | SE yield modification (charging) | Charging | **Essential** | Material-dependent scaling |
| 5 | PMT excess noise | Noise | **Recommended** | Variance scaling factor |
| 6 | SE-II background (blur) | Blur | **Recommended** | Long-range convolution |
| 7 | Detector saturation | Artifact | **Recommended** | Clip function |
| 8 | Frame averaging | Instrument | **Recommended** | SNR enhancement + drift blur |
| 9 | Defocus | Blur | **Optional** | Variable probe $\sigma$ |
| 10 | Astigmatism | Blur | **Optional** | Non-circular PSF |
| 11 | Scan distortion | Artifact | **Optional** | Polynomial warp |
| 12 | Drift (time-dependent) | Artifact | **Optional** | Time-dependent shift |
| 13 | Vibration (as blur) | Blur | **Optional** | Added Gaussian blur |
| 14 | Amplifier noise | Noise | **Optional** | Additive Gaussian |
| 15 | Quantization noise | Noise | **Optional** | Uniform distribution |
| 16 | Charging beam deflection | Charging | **Optional** | Electrostatic model |
| 17 | Charging progressive drift | Charging | **Optional** | Time-dependent |
| 18 | Diffraction | Blur | **Can ignore** | <0.1 nm |
| 19 | Dark current | Noise | **Can ignore** | <1 e⁻/pixel |
| 20 | Scan noise | Noise | **Can ignore** | <0.1% |
| 21 | Source emission noise | Noise | **Can ignore** | Low-frequency |
| 22 | Banding | Artifact | **Can ignore** | <1% |
| 23 | Streaking | Artifact | **Can ignore** | Unpredictable |
| 24 | Dead pixels | Artifact | **Can ignore** | Corrected |
| 25 | Flashover / discharge | Charging | **Can ignore** | Rare |

---

## 9. Implementation Priority

### Phase A — Minimum Viable Renderer (Essential)

```
1. Gaussian probe PSF (convolution of ideal image with σ_probe)
2. Material-dependent escape depth (σ_material per material)
3. Shot noise (Poisson random per pixel)
4. Charging yield reduction (material-dependent δ reduction)
5. Pixel scaling (gain, dwell time, current → digital values)
```

### Phase B — Realistic Enhancement (Recommended)

```
6. PMT excess noise (variance scaling)
7. SE-II background (long-range convolution)
8. Detector saturation (clip)
9. Frame averaging simulation
```

### Phase C — Full Realism (Optional)

```
10. Defocus/astigmatism
11. Scan distortion
12. Drift
13. Vibration as blur
14. Charging beam deflection
```

### Phase D — Special Cases (Can Ignore for Now)

```
15. Diffraction, dark current, banding, streaking, discharge, dead pixels
```

---

## Sources

- L. Reimer, *Scanning Electron Microscopy: Physics of Image Formation and Microanalysis*, 2nd ed. Springer, 1998.
- J. I. Goldstein, D. E. Newbury, J. R. Michael, et al., *Scanning Electron Microscopy and X-Ray Microanalysis*, 4th ed. Springer, 2017.
- R. F. Egerton, *Physical Principles of Electron Microscopy*, 2nd ed. Springer, 2016.
- J. S. Villarrubia, A. E. Vladar, and M. T. Postek, "Scanning electron microscope measurement of width and shape of fabricated nanostructures," *J. Res. NIST*, vol. 109, 2004.
- M. T. Postek and A. E. Vladar, "Critical dimension metrology," in *Handbook of Semiconductor Manufacturing Technology*, CRC Press, 2007.
- C. N. Archie, "Critical dimension metrology," *AIP Conf. Proc.*, vol. 788, 2005.
- D. C. Joy, *Monte Carlo Modeling for Electron Microscopy and Microanalysis*. Oxford University Press, 1995.
