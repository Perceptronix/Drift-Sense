# Shape and Surface Variations

**Research Phase:** 3.3
**Document:** 05_shape_and_surface_variations.md
**Date:** 2026-07-30

---

## 1. Variation Types

Beyond LER/LWR and overlay, five additional shape variations affect manufactured geometry:

| Variation | Description | Source | Typical Magnitude (N5) |
|---|---|---|---|
| Sidewall angle variation | Fluctuation of etch slope | Etch non-uniformity | ±1–3° from nominal |
| Height / thickness variation | Film thickness non-uniformity | Deposition, CMP | ±2–5% of nominal |
| Corner rounding variation | Incomplete corner transfer | Lithography, etch | R = 2–10 nm (variable) |
| CMP dishing | Concave surface on wide features | CMP of soft (Cu) material | 5–50 nm (CD-dependent) |
| CMP erosion | Height loss in dense arrays | CMP of dense features | 5–30 nm (density-dependent) |

---

## 2. Sidewall Angle Variation

### 2.1 Sources

| Source | Effect | Magnitude | Spatial Scale |
|---|---|---|---|
| Etch rate radial non-uniformity | Systematic angle change wafer center → edge | ±1° | Wafer level |
| Aspect ratio dependence (ARDE) | Steeper sidewall in narrow / deep features | 0.5–2° | Feature level |
| Mask selectivity variation | Angle depends on mask erosion | ±0.5° | Feature level |
| Random etch non-uniformity | Local angle fluctuations | ±0.5° | 10–100 μm |

### 2.2 Model

Sidewall angle per feature is modeled as:

$$\theta_{\text{SW}} = \theta_{\text{nominal}} + \Delta\theta_{\text{systematic}} + \Delta\theta_{\text{random}}$$

| Component | Distribution | Parameters |
|---|---|---|
| $\theta_{\text{nominal}}$ | Fixed per layer | 87° (default) |
| $\Delta\theta_{\text{systematic}}$ | Radial: $a \cdot (r/R)^2$ | a = 0.5–2° |
| $\Delta\theta_{\text{random}}$ | Truncated $\mathcal{N}(0, \sigma_\theta)$ | $\sigma_\theta = 0.5^\circ$, clamped to [85°, 89°] |

**Engineering Decision:** Sidewall angle variation is modeled as a truncated Gaussian per feature, with the systematic radial component optionally applied for multi-site generation.

---

## 3. Thickness / Height Variation

### 3.1 Sources

| Source | Effect | Magnitude |
|---|---|---|
| CVD deposition non-uniformity | Thicker center, thinner edge | ±2–5% |
| CMP rate variation | Systematic (center faster) | ±3–8% |
| Spin coating variation | Thickness depends on pattern density | ±2–5% |
| Thermal growth variation | Small (thermal oxidation) | ±1–2% |

### 3.2 Model

Layer thickness $T$ is a random variable:

$$T = T_0 \cdot (1 + \epsilon_T)$$

where $\epsilon_T \sim \mathcal{N}(0, \sigma_{T,\text{rel}})$ with $\sigma_{T,\text{rel}} = 0.02$–$0.05$ (2–5% relative variation).

**Fact:** Thickness variation changes the total feature height, which in turn affects the SEM intensity (more SE yield from taller features due to larger sidewall area). However, the effect is typically small: a 5% height change produces <5% intensity change.

---

## 4. Corner Rounding Variation

### 4.1 Sources

| Source | Effect | Magnitude |
|---|---|---|
| Lithography optical blur | Rounded convex corners | R = λ / (2NA) ∼ 15 nm (EUV) |
| Acid diffusion during PEB | Additional blur | 5–10 nm |
| Etch transfer | Rounded corners transferred from resist | 3–10 nm |
| CMP corner rounding | Additional rounding from polish | 2–5 nm |

### 4.2 Model

Effective corner radius after all process steps:

$$R_{\text{eff}} = \sqrt{R_{\text{litho}}^2 + R_{\text{etch}}^2 + R_{\text{CMP}}^2}$$

where each $R$ is modeled as a random variable:

| Radius | Distribution | Default (N5) | Range |
|---|---|---|---|
| $R_{\text{litho}}$ | $\mathcal{N}(R_{\text{litho, nominal}}, \sigma)$ | 5 nm | 3–10 nm |
| $R_{\text{etch}}$ | $\mathcal{N}(R_{\text{etch, nominal}}, \sigma)$ | 3 nm | 2–5 nm |
| $R_{\text{CMP}}$ | $\mathcal{N}(0, \sigma_{\text{CMP}})$ | 0 nm (no added) | 0–2 nm |

---

## 5. CMP Dishing

### 5.1 Physical Model

CMP dishing creates a concave surface on wide metal features:

| Parameter | Value | Notes |
|---|---|---|
| Depth | 5–50 nm | Scales with feature width |
| Width | Approximately feature CD × 0.7 | Parabolic profile |
| Shape | Parabolic: $h(x) = h_0 - d_{\text{dish}} \cdot (2x / \text{CD})^2$ | Maximum at center |
| Width threshold | Features wider than ∼200 nm dish measurably | Narrower lines are unaffected |

### 5.2 Variation Model

Dishing depth is modeled as:

$$d_{\text{dish}} = d_0 \cdot \left(\frac{\text{CD}}{\text{CD}_0}\right)^\beta + \epsilon_{\text{dish}}$$

| Parameter | Default | Distribution |
|---|---|---|
| $d_0$ (dishing at CD₀ = 1 μm) | 15 nm | Gaussian, σ = 3 nm |
| $\beta$ (exponent) | 0.5 | Fixed |
| $\epsilon_{\text{dish}}$ | 0 nm | $\mathcal{N}(0, 2$ nm$)$ |

---

## 6. CMP Erosion

### 6.1 Physical Model

CMP erosion reduces feature height in dense pattern areas:

| Parameter | Value | Notes |
|---|---|---|
| Depth | 5–30 nm | Scales with pattern density |
| Density dependence | $\propto \text{pattern density} ^ \gamma$ | γ ≈ 1.0 |
| Dense array erosion | Typically 5–15 nm | For 50% pattern density |

### 6.2 Erosion Model

$$h_{\text{erosion}} = h_0 \cdot \left(1 - e_0 \cdot \rho_{\text{pattern}}\right)$$

where $\rho_{\text{pattern}}$ is the local pattern density within a 5–10 μm window.

**Engineering Decision:** CMP erosion is **Optional**. It adds subtle, large-scale height variation that is only visible in large-FOV SEM images (>5 μm).

---

## 7. Variation Summary Table

| Variation | Model | Default (3σ) | Classification | Phase |
|---|---|---|---|---|
| Sidewall angle | Truncated Gaussian per feature | $\sigma = 1^\circ$ | **Recommended** | C |
| Thickness (layer) | Gaussian, relative (%) | 5% of T | **Optional** | C |
| Corner radius | Gaussian, per feature | $\sigma = 1$ nm | **Recommended** | C |
| CMP dishing | Parabolic + Gaussian depth | $\sigma_{\text{dish}} = 3$ nm | **Recommended** | D |
| CMP erosion | Density-dependent height | $\sigma_{\text{erosion}} = 3$ nm | **Optional** | D |

---

## Sources

- [F1] J. D. Plummer, *Silicon VLSI Technology*, Prentice Hall, 2000.
- [F10] S. Franssila, *Introduction to Microfabrication*, Wiley, 2010.
- [F12] J. M. Steigerwald, *CMP of Microelectronic Materials*, Wiley, 2004.
- [M3] C. A. Mack, "Line edge roughness," *J. Micro/Nanolith. MEMS MOEMS*, vol. 8, 2009.
- [M12] C. N. Archie, "CD metrology," *AIP Conf. Proc.*, vol. 788, 2005.
- [M15] S. H. Olsen et al., "Thickness variation effects," *IEEE Trans. Semi. Manuf.*, vol. 18, 2005.
- [M16] T. Park et al., "CMP modeling," *J. Electrochem. Soc.*, vol. 149, 2002.
