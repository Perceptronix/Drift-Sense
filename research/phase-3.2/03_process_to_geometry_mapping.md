# Process-to-Geometry Mapping

**Research Phase:** 3.2
**Document:** 03_process_to_geometry_mapping.md
**Date:** 2026-07-30

---

## 1. Mapping Framework

This document defines, for every process step, the geometric transformation it applies to the 2.5D height field. Each step is treated as a **function** that takes a geometry input and produces a geometry output.

---

## 2. Deposition Mapping

### 2.1 Conformal Deposition (CVD/ALD)

| Aspect | Detail |
|---|---|
| **Geometric input** | Existing height field $h_{\text{in}}(x,y)$ and material map $m_{\text{in}}(x,y)$ |
| **Material** | Deposited material ID $m_{\text{dep}}$ |
| **Thickness** | $T_{\text{dep}}$ (nm) along surface normal |
| **Height modification** | $h_{\text{out}}(x,y) = h_{\text{in}}(x,y) + T_{\text{dep}} / \cos(\theta(x,y))$ |
| **Material modification** | $m_{\text{out}}(x,y) = m_{\text{dep}}$ on surfaces exposed to deposition |
| **Sidewall effect** | Material added to sidewalls (thickness $T_{\text{dep}}$ measured normal to surface) |
| **Topology effect** | Conformal — sharp corners are preserved but offset outward |

**Implementation concept:** Conformal deposition offsets the surface outward along the surface normal by distance $T_{\text{dep}}$. This is equivalent to an offset (dilation) of the solid.

**Inference:** Conformal deposition preserves feature shape while thickening all surfaces uniformly.

### 2.2 Bottom-Up Fill (ECP/Electrochemical)

| Aspect | Detail |
|---|---|
| **Geometric input** | Existing height field with trenches/vias |
| **Material** | Deposited material ID $m_{\text{fill}}$ |
| **Thickness** | $T_{\text{fill}}$ (nm) measured from bottom of features upward |
| **Height modification** | Bottom of features filled upward; sidewalls not covered |
| **Material modification** | $m_{\text{out}} = m_{\text{fill}}$ in filled regions |
| **Topology effect** | Creates planar filler layer in trenches |

**Implementation concept:** Bottom-up fill raises the lowest points of the height field in seed regions, limited by the feature opening.

### 2.3 PVD (Directional)

| Aspect | Detail |
|---|---|
| **Geometric input** | Existing height field |
| **Material** | Deposited material ID $m_{\text{dep}}$ |
| **Thickness** | $T_{\text{dep}}$ on horizontal surfaces; reduced on sidewalls |
| **Height modification** | $h_{\text{out}}(x,y) = h_{\text{in}}(x,y) + T_{\text{dep}}$ (mainly vertical) |
| **Sidewall effect** | Typically $T_{\text{dep}}/3 - T_{\text{dep}}/5$ on vertical sidewalls |

---

## 3. Lithography Mapping

### 3.1 Resist Coat + Expose + Develop

| Aspect | Detail |
|---|---|
| **Geometric input** | Existing height field; GDSII layout pattern for this layer |
| **Material** | Photoresist ($m = 6$) |
| **Height modification** | Flat resist coating: $h_{\text{coat}} = h_{\text{top}} + T_{\text{resist}}$ (planar coating assumption) |
| **Pattern transfer** | Regions with resist removed develop down to underlying material |
| **Sidewall effect** | Resist sidewall angle $\theta_{\text{res}}$ (85–89°) |

**Simplified model:**

```
1. Apply flat coating of resist at height = max_h_current + T_resist
2. Apply GDSII pattern:
   - Exposed regions: resist removed (height reduced to underlying layer)
   - Unexposed regions: resist remains
3. Apply sidewall angle θ_res at pattern edges
4. Apply corner rounding (R_top, R_bottom) at pattern corners
```

**Engineering Decision:** For positive-tone resist (most common), exposed regions are removed. For negative-tone resist, the opposite applies. The tone is a configurable parameter.

---

## 4. Etch Mapping

### 4.1 Anisotropic Etch (RIE)

| Aspect | Detail |
|---|---|
| **Geometric input** | Height field with masking layer (resist or hardmask) |
| **Etch selectivity** | Ratio of etch rates: $S = R_{\text{film}} / R_{\text{mask}}$ |
| **Depth** | Film etched to depth $D_{\text{etch}}$ where mask is open |
| **Sidewall angle** | $\theta_{\text{etch}}$ (85–89°) — the etched feature sidewall |
| **CD bias** | $\Delta\text{CD}$ — final CD = mask CD − 2 ⋅ bias |
| **Bottom corner** | Radius $R_{\text{cb}}$ at bottom of etch profile |
| **Height modification** | $h_{\text{out}} = h_{\text{in}} - D_{\text{etch}}$ in unmasked regions |
| **Material modification** | Subsurface material exposed after etch |

**Implementation concept:** The etch step removes all material within the mask opening down to depth $D_{\text{etch}}$, with a tapered sidewall:

```
Before etch:
  ██████████████████████████  ← Mask (resist/hardmask)
  ██████████████████████████
  ┌────────────┬────────────┐  ← Film to be etched
  │            │            │
  │            │            │
  └────────────┴────────────┘
  ───────────────────────────  ← Etch stop layer

After etch:
  ██████████████████████████  ← Mask (partially consumed if selectivity < ∞)
  ▄▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄▄
  ▐  \        /▌▐\        / ▌  ← Tapered sidewall
  ▐   \      / ▐▐ \      /  ▌
  ▐    ▄▄▄▄  /  ▐▐  ▄▄▄▄    ▌
  ─────▼────▼────▼──▼────▼──────  ← Etch stop (e.g., Si substrate)
```

### 4.2 Isotropic Etch

| Aspect | Detail |
|---|---|
| **Direction** | All directions equally |
| **Profile** | Undercuts mask (side etch = vertical etch) |
| **Sidewall** | Curved (circular arc profile) |
| **Use case** | Sacrificial layers, spacer formation, cleaning |

**Implementation concept:** Isotropic etch produces a circular profile under the mask edge:

```
  ██████████████████████████  ← Mask
  ██████████████████████████
  │    ◠◠◠◠◠◠◠◠◠◠    │      ← Isotropic etch profile
  │  ◠              ◠ │
  │ ◠                ◠│
  ─┴─────────────────────      ← Undercut extends under mask
```

---

## 5. CMP Mapping

### 5.1 Global Planarization

| Aspect | Detail |
|---|---|
| **Geometric input** | Height field $h_{\text{in}}(x,y)$ with topography from previous steps |
| **Target height** | $H_{\text{CMP}}$ — all material above this is removed |
| **Material selectivity** | Different rates for different materials |
| **Height modification** | $h_{\text{out}} = \min(h_{\text{in}}(x,y), H_{\text{CMP}})$ for ideal planarization |
| **Material modification** | None (material above H_CMP was removed; now material at H_CMP becomes the surface) |

### 5.2 Dishing and Erosion

**Dishing** — concave surface in wide soft features (e.g., Cu in wide trenches):

| Parameter | Symbol | Typical Value |
|---|---|---|
| Dishing depth | $\Delta h_{\text{dish}}$ | 5–50 nm (linewidth-dependent) |
| Dishing width | $W_{\text{dish}}$ | ∼0.7 × feature width |
| Minimum dishing | — | 0 for features < 2× erosion width |

**Erosion** — height loss in dense pattern regions (dielectric + metal thinning):

| Parameter | Symbol | Typical Value |
|---|---|---|
| Erosion depth | $\Delta h_{\text{erosion}}$ | 5–30 nm (density-dependent) |
| Pattern density dependence | — | $\propto$ local pattern density |

---

## 6. Complete Geometrical Transformation

### 6.1 Per-Layer Transformation

Each layer processing loop transforms the geometry as:

$$h_{L+1} = \text{CMP}_{\text{target}}(\text{Strip}(\text{Etch}_{\text{profile}}(\text{Litho}_{\text{pattern}}(\text{Deposit}_{\text{film}}(h_L)), G_L, P_L)))$$

where:
- $h_L$ = height field after processing L layers
- $G_L$ = GDSII layout pattern for layer L
- $P_L$ = process parameters for layer L

### 6.2 Transformation Summary Table

| Step | Height Change | Material Change | Sidewall Profile | Corner Effect |
|---|---|---|---|---|
| **Deposition (conformal)** | +$T \sec\theta$ | New material on all surfaces | Preserved | Rounded outward |
| **Deposition (bottom-up)** | +$T_{\text{fill}}$ (bottom only) | New material in trenches | None | Planar top |
| **Lithography** | +$T_{\text{res}}$ (coating), −$T_{\text{res}}$ (development) | Resist added/removed | $\theta_{\text{res}}$ | $R_{\text{top}}$, $R_{\text{bottom}}$ |
| **Etch (anisotropic)** | −$D_{\text{etch}}$ (mask open) | Exposes underlying material | $\theta_{\text{etch}}$ | $R_{\text{cb}}$ |
| **Etch (isotropic)** | −$D_{\text{etch}}$ + undercut | Exposes underlying material | Circular | Circular |
| **CMP (ideal)** | $\min(h, H_{\text{CMP}})$ | None at planarized surface | None at CMP surface | Slight at edges |
| **CMP (dishing)** | −$\Delta h_{\text{dish}}$ (wide features) | None | Shallow concave | Smooth edge |
| **Resist strip** | −$T_{\text{res}}$ (where present) | Resist removed | None | None |

---

## 7. Material Transformation Rules

During each process step, the material map changes as follows:

| Step | Rule |
|---|---|
| **Deposition** | Mask/deposited material overlays existing materials; no mixing |
| **Etch** | Material is removed; underlying material is exposed |
| **CMP** | Material at the planarized surface is thinned but unchanged in ID |
| **Resist strip** | All IDs = 6 (resist) change to the material beneath (normally vacuum or the surface material prior to coating) |

**Engineering Decision:** The material map is always single-valued per pixel. The material at each pixel is the **topmost material** at that location. Subsurface materials are irrelevant for SEM rendering (the escape depth model handles depth information statistically).

---

## Sources

- [F1] J. D. Plummer, *Silicon VLSI Technology*, Prentice Hall, 2000.
- [F2] S. Wolf, *Silicon Processing for the VLSI Era*, Lattice Press, 2002.
- [F3] C. Mack, *Fundamental Principles of Optical Lithography*, Wiley, 2007.
- [F6] M. J. Madou, *Fundamentals of Microfabrication*, CRC Press, 2011.
- [F10] S. Franssila, *Introduction to Microfabrication*, 2nd ed. Wiley, 2010.
- [F11] K. Seshan, *Handbook of Thin Film Deposition*, Elsevier, 2012.
- [F12] J. M. Steigerwald, S. P. Murarka, R. J. Gutmann, *Chemical Mechanical Planarization of Microelectronic Materials*, Wiley, 2004.
