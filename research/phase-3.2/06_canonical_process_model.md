# Canonical Process Model

**Research Phase:** 3.2
**Document:** 06_canonical_process_model.md
**Date:** 2026-07-30

---

## 1. Model Overview

The canonical process model defines the complete geometry generation pipeline — from GDSII layout to final 2.5D height field and material map.

### 1.1 Pipeline

```
GDSII Layout (per layer)
    │
    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 1. LAYER STACK INITIALIZATION                                       │
│    a. Define substrate: Si (h = 0, m = 1)                          │
│    b. Define layer stack: {material, thickness, GDSII layer #}      │
│    c. Initialize current height field h⁰(x,y) = 0, m⁰(x,y) = 1     │
└─────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 2. FOR EACH LAYER L in stack (bottom to top):                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ 2a. DEPOSITION                                                │  │
│  │    Input:  hᴸ⁻¹(x,y), mᴸ⁻¹(x,y)                               │  │
│  │    Params: T_L (nm), material m_L, conformality type           │  │
│  │    Output: h_dep(x,y), m_dep(x,y)                              │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              │                                       │
│                              ▼                                       │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ 2b. LITHOGRAPHY                                               │  │
│  │    Input:  h_dep(x,y), GDSII polygon for layer L               │  │
│  │    Params: CD_mask, θ_res, R_top_res, R_bottom_res            │  │
│  │    Output: h_litho(x,y), m_litho(x,y)                         │  │
│  │    Process: 1. Coat resist (h_coat = h_max + T_resist)        │  │
│  │             2. Pattern: open where GDSII layer L exists       │  │
│  │             3. Taper resist edges: θ_res                      │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              │                                       │
│                              ▼                                       │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ 2c. ETCH                                                      │  │
│  │    Input:  h_litho(x,y), m_litho(x,y) (resist mask)            │  │
│  │    Params: D_etch (= T_L), θ_etch, ΔCD, R_cb, O_e            │  │
│  │    Output: h_etch(x,y), m_etch(x,y)                            │  │
│  │    Process: 1. Remove material in unmasked regions to D_etch  │  │
│  │             2. Apply tapered sidewall θ_etch                  │  │
│  │             3. Round bottom corners R_cb                      │  │
│  │             4. Apply CD bias to mask opening                  │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              │                                       │
│                              ▼                                       │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ 2d. RESIST STRIP                                              │  │
│  │    Input:  h_etch(x,y), m_etch(x,y)                            │  │
│  │    Process: Remove all pixels with m = 6 (resist)             │  │
│  │    Output: h_strip(x,y), m_strip(x,y)                          │  │
│  │    Height: Resist pixels replaced by underlying layer height  │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              │                                       │
│                              ▼                                       │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ 2e. CMP (if applicable)                                       │  │
│  │    Input:  h_strip(x,y), m_strip(x,y)                          │  │
│  │    Params: H_CMP, dish_depth (if wide metal)                  │  │
│  │    Output: hᴸ(x,y), mᴸ(x,y)                                   │  │
│  │    Process: 1. Remove all material above H_CMP                │  │
│  │             2. Apply dishing for wide features (optional)     │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
    │ (after all layers processed)
    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 3. FINAL OUTPUT                                                     │
│    Output: h_final(x,y), m_final(x,y)                              │
│    Format: 16-bit PNG height map + 16-bit PNG material map         │
│    Metadata: pixel_size_nm, structure_name, layer stack info       │
│    → To SEM Physics Engine                                         │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Stage Specifications

### 2.1 Stage 1: Layer Stack Initialization

| Aspect | Specification |
|---|---|
| **Input** | Layer stack definition (see Section 3) |
| **Substrate** | Si material (ID = 1), height = 0 nm |
| **Empty space** | Vacuum material (ID = 0), height = 0 nm |
| **Output** | $h^0(x,y) = 0$, $m^0(x,y) = 1$ everywhere |

### 2.2 Stage 2a: Deposition

**Geometric transformation:**

| Conformality Type | Height Update | Material Update |
|---|---|---|
| **Conformal** | $h_{\text{dep}}(x,y) = h_{\text{in}}(x,y) + T_L / \cos\theta(x,y)$ | $m_{\text{dep}} = m_L$ on all surfaces above previous top |
| **Bottom-up** | $h_{\text{dep}} = \max(h_{\text{in}}, \text{local\_min} + T_L)$ in seed regions | $m_{\text{dep}} = m_L$ in fill regions |
| **PVD (directional)** | $h_{\text{dep}}(x,y) = h_{\text{in}}(x,y) + T_L$ (top); $T_L/3$ (sidewall) | $m_{\text{dep}} = m_L$ |

### 2.3 Stage 2b: Lithography

**Input:** GDSII layout polygon(s) for the current layer.

**Procedure:**
1. Rasterize GDSII layer to image mask $M(x,y)$: 1 where layout exists, 0 elsewhere.
2. Apply resist coating: $h_{\text{coat}} = \max(h_{\text{dep}}) + T_{\text{resist}}$
3. Apply pattern: in regions where mask $M = 0$ (positive-tone), develop resist: $h_{\text{dev}} = h_{\text{dep}}$
4. Apply sidewall angle: transition between $h_{\text{coat}}$ and $h_{\text{dev}}$ over $\Delta x = T_{\text{resist}} / \tan(90^\circ - \theta_{\text{res}})$
5. Apply corner rounding: smooth convex/concave corners with $R_{\text{top}}$ and $R_{\text{bottom}}$

**Output:** Resist pattern with tapered sidewalls on top of the deposited film.

### 2.4 Stage 2c: Etch

**Procedure:**

```
For each pixel (x,y):
  if M_mask(x,y) == 0:   // Mask is open (region to be etched)
    // Remove material down to D_etch
    h_etch(x,y) = max(h_litho(x,y) - D_etch, h_stop(x,y))
    m_etch(x,y) = material_at_depth(h_stop(x,y))
  else:                   // Mask is closed (region not etched)
    // Optionally consume some mask (if selectivity < ∞)
    h_etch(x,y) = h_litho(x,y) - D_etch / S_selectivity
    m_etch(x,y) = m_dep

Apply sidewall taper:
  // Transition from mask CD to bottom CD
  CD_bottom = CD_mask + 2 * D_etch / tan(90° - θ_etch)
  // Interpolate height in transition region

Apply bottom corner rounding:
  R_cb: Smooth the bottom corner using circular arc
  // Implementation: convolution of bottom edge with R_cb kernel

Apply CD bias:
  CD_final = CD_mask - ΔCD
  // Narrow the etch opening by ΔCD
```

**Output:** Etched feature profile with tapered sidewalls and rounded bottom corners.

### 2.5 Stage 2d: Resist Strip

```
For each pixel (x,y):
  if m_etch(x,y) == 6 (resist):
    m_strip(x,y) = underlying material (from pre-lithography)
    h_strip(x,y) = underlying height
```

**Simplification:** The resist is assumed to be removed cleanly. Residual resist (scum) is not modeled.

### 2.6 Stage 2e: CMP

**Procedure:**

```
H_CMP: target CMP height

For each pixel (x,y):
  if h_strip(x,y) > H_CMP:
    h_cmp(x,y) = H_CMP
    m_cmp(x,y) = material at h = H_CMP from the layer stack

Optional — Dishing:
  if feature is wide (CD > W_threshold) and material is soft (e.g., Cu):
    h_cmp(x,y) -= dish_depth * (1 - (2*x / CD)^2)  // parabolic
```

---

## 3. Layer Stack Definition

### 3.1 Layer Record

Each layer is defined by:

```
Layer {
    int layer_number;           // GDSII layer number
    string name;                // e.g., "M1", "CONTACT"
    int material_id;            // Material ID for deposited film
    float thickness_nm;         // Target deposition thickness
    float cmp_target_height_nm; // CMP target height (0 = no CMP)
    float etch_depth_nm;        // Etch depth (typically = thickness)
    float sidewall_angle_deg;   // Etch sidewall angle (85-89°)
    float cd_bias_nm;          // CD bias (etch → final)
    float corner_radius_nm;    // Bottom corner radius
    string conformality;        // "conformal", "bottom_up", "pvd"
    bool is_mask;               // Is this a mask layer only?
};
```

### 3.2 Example: Simplified N5 FinFET Layer Stack

| Layer | Name | Material | Thickness (nm) | CMP Target | Sidewall Angle |
|---|---|---|---|---|---|
| — | Substrate | Si (1) | — | — | — |
| L1 | STI trench | SiO₂ (2) | 300 | 0 | 87° |
| L2 | Fin hardmask | Si₃N₄ (3) | 30 | None | 87° |
| L3 | Fin recess | Si (1) | 50 | None | 88° |
| L4 | Gate oxide | SiO₂ (2) | 2 | None | — |
| L5 | Gate workfunction | Metal | 5 | None | 87° |
| L6 | Gate fill | W (5) | 50 | 50 | 88° |
| L7 | Spacer | Si₃N₄ (3) | 7 | None | 87° |
| L8 | ILD0 | SiO₂ (2) | 100 | 100 | — |
| L9 | Contact | W (5) | 100 | 100 | 87° |
| L10 | M1 ILD | SiO₂ (2) | 80 | 80 | — |
| L11 | M1 trench | Cu (4) | 80 | 80 | 87° |

---

## 4. Model Properties

### 4.1 Sequence Invariance

The order of operations is grounded in fabrication reality:

| Step Order | Reason |
|---|---|
| Deposition before lithography | You cannot pattern a film that hasn't been deposited |
| Lithography before etch | The resist pattern defines where to etch |
| Etch before resist strip | Resist must protect during etch |
| CMP after etch/dep | CMP planarizes the topography created by etching/deposition |

### 4.2 Composability

The process model is **composable**: layers can be added, removed, or reordered without changing the algorithm. Each layer execution is independent except for depending on the output of the previous layer's height field.

### 4.3 Parameter Inheritance

If a parameter is not specified for a layer, it inherits from the previous layer:

| Parameter | Inheritance Rule |
|---|---|
| Sidewall angle | Inherits from global default (87°) if not specified |
| Corner radius | Inherits from global default (5 nm) if not specified |
| CD bias | Specified per layer (etch chemistry dependent) |

---

## 5. Boundary Between Geometry Engine and SEM Physics Engine

The canonical process model produces **exactly** the geometry interface specified in Phase 2.6 and Phase 3.1:

```
Geometry Engine Output:
  ├── height_map.png      (16-bit PNG)
  ├── material_map.png    (16-bit PNG)
  └── metadata.json       (pixel_size_nm, structure_name, ...)

→ Consumed by SEM Physics Engine
```

The process model's responsibility ends at this interface. All SEM physics calculations (SE yield, PSF, noise, charging) are the responsibility of the physics engine.

---

## 6. Validation of the Process Model

| Check | Method | Criteria |
|---|---|---|
| Cross-section matches ideal | Compare to F1, F8 (textbook profiles) | All features trapezoidal with correct parameters |
| Sidewall angle correct | Measure profile | ±0.5° of specified angle |
| CD correct | Measure bottom and top CD | ±1 nm of specified CD |
| Corner rounding present | Inspect corners | Smooth transition (not sharp) |
| Layer stack correct | Cross-section of multi-layer structure | Layer order, materials, thicknesses correct |

---

## Sources

- [F1] J. D. Plummer, *Silicon VLSI Technology*, Prentice Hall, 2000.
- [F2] S. Wolf, *Silicon Processing for the VLSI Era*, Lattice Press, 2002.
- [F3] C. Mack, *Fundamental Principles of Optical Lithography*, Wiley, 2007.
- [F10] S. Franssila, *Introduction to Microfabrication*, Wiley, 2010.
- [F12] J. M. Steigerwald, *CMP of Microelectronic Materials*, Wiley, 2004.
- [F14] C. T. Gabriel, "Sidewall profile modeling," *J. Vac. Sci. Technol. B*, vol. 28, 2010.
- Phase 2.6, Document 06 — Geometry interface specification.
- Phase 3.1, Document 06 — Canonical geometry inputs.
