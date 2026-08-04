# Pixel Intensity Models

**Research Phase:** 2.3
**Document:** 05_pixel_intensity_models.md
**Date:** 2026-07-30

---

## 1. Introduction

The grayscale value of each pixel in an SEM image is the end result of a long chain of physical and electronic processes. This document develops the complete mathematical model relating the pixel intensity to the underlying sample properties.

**Goal:** From first principles, derive how pixel intensity $I(x,y)$ depends on:
- SE yield $\delta$ (material and angle-dependent)
- BSE yield $\eta$ (Z-dependent)
- Collection efficiency $\eta_{\text{coll}}$
- System gain and offset
- Probe current and dwell time
- Detector transfer function

---

## 2. Fundamental Pixel Intensity Equation

### 2.1 General Form

The pixel intensity at image coordinate $(i,j)$ corresponding to sample position $(x,y)$ is:

$$I_{ij} = G \cdot \left[ \underbrace{S_{\text{SE}}(x,y)}_{\text{SE signal}} + \underbrace{S_{\text{BSE}}(x,y)}_{\text{BSE signal}} \right] + I_{\text{offset}}$$

where $G$ is the total system gain and $I_{\text{offset}}$ is the dark-level offset.

### 2.2 SE Signal Component

The SE contribution to the pixel intensity is:

$$S_{\text{SE}}(x,y) = I_P \cdot \tau \cdot \left[ \delta_{\text{SE-I}}(x,y) \cdot \eta_{\text{coll}}^{\text{SE}}(x,y) + S_{\text{SE-II}}(x,y) \right]$$

where:
- $I_P$ = probe current (A)
- $\tau$ = pixel dwell time (s)
- $\delta_{\text{SE-I}}$ = SE-I yield at position $(x,y)$
- $\eta_{\text{coll}}^{\text{SE}}$ = SE collection efficiency
- $S_{\text{SE-II}}$ = SE-II contribution (from exiting BSEs)

### 2.3 SE-I Yield Model

The SE-I yield at a point is the product of material-dependent and geometry-dependent factors:

$$\delta_{\text{SE-I}}(x,y) = \delta_0(Z) \cdot f_{\text{angle}}(\theta, \phi)$$

where:
- $\delta_0(Z)$ = SE yield for material $Z$ at normal incidence
- $f_{\text{angle}}(\theta, \phi)$ = angular enhancement factor

The standard model for the angular factor is:

$$f_{\text{angle}}(\theta) = \frac{1}{\cos\theta} \quad \text{(for } \theta < 70^\circ\text{)}$$

For $\theta > 70^\circ$, the enhancement is somewhat less than $\sec\theta$ due to surface reabsorption effects.

---

## 3. Dominant Variables

### 3.1 Variable Sensitivity Analysis

| Variable | Physical Range | Impact on Pixel Intensity | Rank |
|---|---|---|---|
| **Local surface angle $\theta$** | 0°–90° | 1–11× change | **1 (dominant)** |
| **Material $Z$ (via $\delta_0$)** | 4–74 (semiconductor materials) | 0.7–2.5× change | **2** |
| **Collection efficiency $\eta_{\text{coll}}$** | 0–1 (position-dependent) | 0–1× change | **3** |
| **BSE yield $\eta(Z)$** | 0.06–0.52 | Modifies background | 4 |
| **Probe current $I_P$** | 5–200 pA | Linear scaling | User-controlled |
| **Dwell time $\tau$** | 0.1–100 μs | Linear scaling | User-controlled |

**Inference:** For CD-SEM imaging of patterned wafers, the surface angle $\theta$ is the dominant variable — it varies by ~10× across a typical structure while material $Z$ varies by only ~3×. This is why SE images emphasize topography over composition.

### 3.2 The Role of Material

Although $\theta$ dominates, material contrast is still significant:

| Scene | What Determines Contrast |
|---|---|
| **Single-material surface (e.g., bare Si)** | Only $\theta$ variation (topography only) |
| **Two materials, flat (e.g., oxide on Si)** | Only $\delta_0(Z)$ variation (material contrast only) |
| **Patterned wafer (e.g., photoresist lines on Si)** | Both $\theta$ and $\delta_0(Z)$ — mixture of topographic and material contrast |

---

## 4. Collection Efficiency Model

### 4.1 TTL Detector Model

For a through-the-lens detector in a CD-SEM:

$$\eta_{\text{coll}}^{\text{TTL}}(\theta_e, \phi_e) \approx \eta_0 \cdot \exp\left(-\frac{\theta_e^2}{2\theta_{\text{acc}}^2}\right)$$

where:
- $\theta_e$ = emission angle relative to the surface normal
- $\theta_{\text{acc}}$ = acceptance angle (typically 40°–60°)
- $\eta_0$ = peak collection efficiency (typically 0.6–0.9)

### 4.2 E-T Detector Model

For an Everhart-Thornley detector at azimuth $\phi_0$:

$$\eta_{\text{coll}}^{\text{ET}}(\theta_e, \phi_e) \propto \max(0, \cos(\phi_e - \phi_0) \cdot \cos\theta_e + \text{bias term})$$

This model produces the characteristic three-dimensional shading.

### 4.3 Combined Model

Modern CD-SEMs with TTL detection are approximately axially symmetric:

$$\eta_{\text{coll}}(x,y) \approx \eta_0 \cdot \Omega(\theta(x,y), \phi(x,y)) / 2\pi$$

where $\Omega$ is the solid angle of the detector aperture as seen from the emission point.

---

## 5. Complete Pixel Intensity Model

### 5.1 First-Principles Model

Combining all contributions:

$$I_{ij} = G \cdot I_P \tau \cdot \left[ \delta_0(Z) \cdot \sec\theta(x,y) \cdot \eta_{\text{coll}}(x,y) + \eta(Z) \cdot \eta_{\text{coll,BSE}}(x,y) + \Delta_{\text{SE-II}}(x,y) \right] + I_{\text{off}}$$

### 5.2 Reduced Model for CD Metrology

For CD-SEM imaging of patterned wafers, the following simplifications are generally valid:

| Term | Full Form | Simplified Form | Validity |
|---|---|---|---|
| SE emission | $\delta_0(Z) \cdot \sec\theta$ | $A \cdot \sec\theta$ | $A$ is material coefficient |
| SE collection | $\eta_{\text{coll}}(x,y)$ | $\eta_0$ (constant) | TTL detector, near-axial |
| BSE contribution | $\eta(Z) \cdot \eta_{\text{coll,BSE}}$ | $B$ (constant background) | BSE signal is slowly varying |
| SE-II | $\Delta_{\text{SE-II}}(x,y)$ | Neglected (first order) | Adds broadening |

**Reduced model:**

$$I_{ij} \approx G_{\text{eff}} \cdot A(Z) \cdot \sec\theta(x,y) + B_{\text{eff}} + I_{\text{off}}$$

**Inference:** To first order, the pixel intensity in a CD-SEM image of a patterned wafer is directly proportional to $\sec\theta$, modulated by material coefficients.

---

## 6. Detector Transfer Function

### 6.1 Electron-to-Signal Conversion

The detector converts emitted electrons to a voltage signal through:

| Process | Efficiency | Notes |
|---|---|---|
| SE / BSE collection | $\eta_{\text{coll}}$ = 0.3–0.9 | Fraction of emitted electrons reaching detector |
| Scintillator conversion | $\epsilon_{\text{scint}}$ = 50–200 photons/electron | Depends on scintillator material |
| Light guide transmission | $\epsilon_{\text{guide}}$ = 0.5–0.9 | Losses in light pipe |
| PMT quantum efficiency | QE = 0.1–0.25 | Photocathode efficiency |
| PMT dynode gain | $G_{\text{PMT}}$ = $10^5$–$10^7$ | Multiplication stages |
| Transimpedance conversion | $V = I \times R_f$ | $R_f$ = 1–100 MΩ |

### 6.2 Overall Gain

The total system gain $G$ is:

$$G = \frac{V_{\text{out}}}{I_{\text{emit}}} = \eta_{\text{coll}} \cdot \epsilon_{\text{scint}} \cdot \epsilon_{\text{guide}} \cdot \text{QE} \cdot G_{\text{PMT}} \cdot R_f$$

For a typical CD-SEM at moderate gain:
- Total gain ≈ $10^8$–$10^{10}$ V/A (output volts per amp of emitted electron current)
- A 1 pA emitted current → 0.1–10 V output signal

---

## 7. Digitization and Grayscale Value

### 7.1 ADC Conversion

The analog voltage $V_{\text{out}}$ is converted to an $N$-bit digital value:

$$I_{\text{digital}} = \left\lfloor \frac{V_{\text{out}} - V_{\text{black}}}{V_{\text{white}} - V_{\text{black}}} \cdot (2^N - 1) + 0.5 \right\rfloor$$

where $V_{\text{black}}$ and $V_{\text{white}}$ are the black-level and white-level reference voltages.

### 7.2 Grayscale Resolution

| N (bits) | Levels | Increment in Signal | Typical Use |
|---|---|---|---|
| 8 | 256 | 0.39% of range | Display only |
| 12 | 4,096 | 0.024% of range | CD-SEM measurement |
| 16 | 65,536 | 0.0015% of range | High-precision averaging |

---

## 8. Comparison of Published Models

### 8.1 Model Hierarchy

| Model | Form | Parameters | Accuracy | Speed |
|---|---|---|---|---|
| **Lambertian** | $I(\theta) \propto \cos\theta$ | 0 | Low | Fastest |
| **$\sec\theta$ yield** | $I \propto \delta_0 \cdot \sec\theta$ | 1 per material | Moderate | Fast |
| **$\sec\theta$ + detector** | $I \propto \delta_0 \cdot \sec\theta \cdot \eta_{\text{coll}}$ | 1 per mat + geometry | Good | Fast |
| **Linearized empirical** | $I = A + B \cdot \text{erf}(x) + C \cdot \exp(-x^2)$ | 5 per edge | Good (edge-focused) | Fast |
| **Monte Carlo** | Full trajectory simulation | Many | Best | Very slow |

### 8.2 Which Model for Which Purpose

| Purpose | Recommended Model | Reason |
|---|---|---|
| **Realistic image synthesis** | $\sec\theta$ + detector | Captures dominant physics, fast enough |
| **CD metrology simulation** | $\sec\theta$ + detector + probe convolution | Ensures correct edge profile shape |
| **Ground-truth validation** | Monte Carlo | Most physically accurate |
| **Analytical edge detection** | Linearized empirical | Fits measured profiles well |

---

## 9. Summary: Dominant and Negligible Variables

### 9.1 Dominant Variables (Must Include)

| Variable | Why | Form |
|---|---|---|
| **Local surface angle $\theta$** | Controls the SE yield via $\sec\theta$ | $\sec\theta(x,y)$ |
| **Material $Z$** | Determines baseline SE and BSE yields | $\delta_0(Z)$, $\eta(Z)$ |
| **Probe current $I_P$** | Linear scaling of signal | $I_P$ |
| **Detector geometry** | Determines which electrons are collected | $\eta_{\text{coll}}(x,y)$ |

### 9.2 Secondary Variables (Useful Refinements)

| Variable | When Important |
|---|---|
| Beam energy $E_0$ | When comparing images at different kV |
| SE-II contribution | When modeling profile tails at edges |
| Dwell time $\tau$ | When considering SNR (Phase 2.4 topic) |

### 9.3 Variables That Can Be Ignored (First Implementation)

| Variable | Why Ignored |
|---|---|
| SE energy distribution | Affects collection efficiency details but not first-order contrast |
| SE angular distribution | Captured by $\sec\theta$ and $\eta_{\text{coll}}$ models |
| Crystallography | Not relevant for amorphous/polycrystalline semiconductor films |
| Temperature | Negligible effect at room temperature |

---

## Sources

- L. Reimer, *Scanning Electron Microscopy: Physics of Image Formation and Microanalysis*, 2nd ed. Springer, 1998.
- J. I. Goldstein, D. E. Newbury, J. R. Michael, et al., *Scanning Electron Microscopy and X-Ray Microanalysis*, 4th ed. Springer, 2017.
- H. Seiler, "Secondary electron emission in the scanning electron microscope," *J. Appl. Phys.*, vol. 54, 1983.
- J. S. Villarrubia, A. E. Vladar, and M. T. Postek, "Scanning electron microscope measurement of width and shape of fabricated nanostructures," *J. Res. NIST*, vol. 109, 2004.
- M. T. Postek and A. E. Vladar, "Critical dimension metrology," in *Handbook of Semiconductor Manufacturing Technology*, CRC Press, 2007.
- D. C. Joy, *Monte Carlo Modeling for Electron Microscopy and Microanalysis*. Oxford University Press, 1995.
- C. N. Archie, "Critical dimension metrology," *AIP Conf. Proc.*, vol. 788, 2005.
