# Overlay and Alignment Errors

**Research Phase:** 3.3
**Document:** 04_overlay_and_alignment_errors.md
**Date:** 2026-07-30

---

## 1. Overlay Error Components

Overlay error has six standard components in semiconductor manufacturing:

| Component | Symbol | Description | Magnitude (N5, 3σ) |
|---|---|---|---|
| Translation (X) | $t_x$ | Shift in X direction | 2–8 nm |
| Translation (Y) | $t_y$ | Shift in Y direction | 2–8 nm |
| Rotation | $\theta$ | Field rotation | 0.1–0.3 μrad |
| Isotropic scaling | $S$ | Uniform magnification | 0.1–0.5 ppm |
| Anisotropic scaling | $S_x$, $S_y$ | X/Y magnification difference | 0.05–0.2 ppm |
| Higher-order distortion | $d_{HO}$ | Lens distortion residuals | 0.5–2 nm |

**Engineering Decision:** Only translation and rotation are modeled. Scaling and higher-order distortion are negligible at CD-SEM FOV (sub-nm across 1 μm).

---

## 2. Overlay Error Model

### 2.1 Linear Overlay Model (Standard in Lithography)

The overlay error at position $(x, y)$ in the scanner field is:

$$\begin{pmatrix} \Delta x \\ \Delta y \end{pmatrix} = \begin{pmatrix} t_x \\ t_y \end{pmatrix} + \begin{pmatrix} \theta_{xy} & \theta_{yy} \\ \theta_{xx} & \theta_{yy} \end{pmatrix} \begin{pmatrix} x \\ y \end{pmatrix}$$

For the simplified model used in geometry generation:

$$\Delta x = t_x + \theta \cdot (y - y_0)$$
$$\Delta y = t_y - \theta \cdot (x - x_0)$$

where both translation and rotation are Gaussian random variables per layer.

### 2.2 Parameter Values

| Parameter | Symbol | Distribution | Default (3σ) | Range (3σ) |
|---|---|---|---|---|
| X translation | $t_x$ | $\mathcal{N}(0, \sigma_{tx})$ | 4.0 nm | 2.0–8.0 nm |
| Y translation | $t_y$ | $\mathcal{N}(0, \sigma_{ty})$ | 4.0 nm | 2.0–8.0 nm |
| Rotation | $\theta$ | $\mathcal{N}(0, \sigma_{\theta})$ | 0.15 μrad | 0.05–0.30 μrad |

**Fact:** Overlay requirements at N5 are approximately 3.0–4.5 nm (3σ) for critical layers (contact-to-gate). The default values reflect IRDS targets [M2].

---

## 3. Impact on Geometry

### 3.1 Which Layers Are Affected

Overlay affects the **relative alignment** between layers. In the layer-by-layer process model:

| Layer Pair | Overlay Relevance | Impact on SEM Image |
|---|---|---|
| Contact → Gate | **High** | Contact position relative to gate affects device performance |
| Via → M1 | **High** | Via-to-line interface visible in SEM |
| Gate → Fin | **High** | Gate-to-fin alignment critical for FinFET |
| M1 → Via | **Moderate** | BEOL alignment |
| STI → Active | **Low** | Non-critical for CD-SEM at surface |

### 3.2 Implementation in Geometry Engine

Overlay is applied as a **layer-level shift** in the process model:

```
For each layer L in the stack:
  1. Generate translation t_x, t_y ~ N(0, σ_overlay)
  2. Apply to the GDSII pattern for layer L:
     x'(y) = x(y) + t_x
     y'(x) = y(x) + t_y
  3. Process the shifted pattern through etch/deposition
```

**Engineering Decision:** Overlay is applied as a rigid shift to the **entire GDSII pattern** for a given layer. This assumes that all features on a single mask layer experience the same overlay error, which is correct for scanner field-level overlay.

### 3.3 Visual Impact in SEM

| Overlay Magnitude | Visibility at 1 μm FOV | Effect |
|---|---|---|
| 0–2 nm | **Barely visible** | <2 pixel shift at 1 nm/pixel |
| 2–5 nm | **Moderately visible** | 2–5 pixel shift; asymmetric interfaces |
| 5–10 nm | **Clearly visible** | Feature position shift, asymmetric contact-to-line |

**Inference:** At a 1 μm FOV with 1 nm/pixel resolution, overlay errors of <2 nm are not visible. At the N5 default of 4 nm, overlay is visible as a small displacement between layers.

---

## 4. Local Distortion Models

### 4.1 Distortion Types

| Type | Source | Magnitude | Impact at 1 μm FOV |
|---|---|---|---|
| Lens distortion | Projection optics | < 2 nm | < 0.002 nm → negligible |
| Wafer warpage | Stress from films | 1–5 nm across die | < 0.01 nm → negligible |
| Chuck flatness | Wafer mounting | < 1 nm | Negligible |
| Pattern-dependent | Etch microloading | 2–5 nm | < 0.005 nm → negligible |

### 4.2 Distortion Model Selection

| Distortion Model | Apply? | Rationale |
|---|---|---|
| Translation | **Yes** | Dominant overlay component |
| Rotation | **Yes** | Second largest component |
| Scaling | **No** | <0.1 nm at 1 μm FOV |
| Higher-order | **No** | <0.01 nm at 1 μm FOV |

---

## 5. Overlay Classification

| Component | Classification | Justification |
|---|---|---|
| Horizontal translation (t_x) | **Recommended** | Visible at >2 nm; affects contact-to-gate alignment |
| Vertical translation (t_y) | **Recommended** | Same as t_x |
| Rotation (θ) | **Optional** | ∼0.001 nm shift across 1 μm → invisible |
| Scaling | **Ignore** | Negligible at CD-SEM FOV |
| Higher-order distortion | **Ignore** | Negligible at CD-SEM FOV |
| Wafer warpage | **Ignore** | Negligible at CD-SEM FOV |

**Final Recommendation:** Overlay translation is **Recommended** for Phase C. It is visible in SEM when misalignment exceeds 2–3 nm. Rotation and higher-order terms are effectively invisible at typical CD-SEM FOV and can be ignored.

---

## Sources

- [M2] IRDS, "Lithography and Metrology Roadmap," 2023.
- [M8] G. J. Dick, "Overlay metrology," in *Handbook of Semiconductor Manufacturing Technology*, CRC Press, 2007.
- [M9] B. W. Smith et al., "Overlay error sources," *Proc. SPIE*, vol. 4344, 2001.
- [M12] C. N. Archie, "CD metrology," *AIP Conf. Proc.*, vol. 788, 2005.
- [M13] M. E. Mason, "Scanner overlay performance," *Proc. SPIE*, vol. 6518, 2007.
