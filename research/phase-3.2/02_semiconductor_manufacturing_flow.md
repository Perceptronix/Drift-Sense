# Semiconductor Manufacturing Flow

**Research Phase:** 3.2
**Document:** 02_semiconductor_manufacturing_flow.md
**Date:** 2026-07-30

---

## 1. Simplified Front-End Flow

### 1.1 Generic Process Sequence

Modern semiconductor fabrication involves hundreds of process steps. For geometry generation purposes, the flow can be condensed into a repeating sequence of operations:

```
Layer Stack Definition
    │
    ▼
┌─────────────────────────────────────────────────┐
│          REPEAT FOR EACH LAYER                   │
├─────────────────────────────────────────────────┤
│                                                  │
│  1. Material Deposition    (film on wafer)       │
│  2. Photoresist Coating    (mask layer)          │
│  3. Lithography            (pattern transfer)    │
│  4. Etching                (pattern into film)   │
│  5. Photoresist Strip      (remove mask)         │
│  6. CMP / Planarization    (if needed)           │
│                                                  │
└─────────────────────────────────────────────────┘
```

**Fact:** A modern FinFET process uses 60–80 mask layers, each requiring the sequence above. For geometry generation, each layer in the stack is processed in sequence, building up the 3D structure.

### 1.2 Process Step Categories

| Category | Steps | Geometric Effect | Complexity |
|---|---|---|---|
| **Additive** | Deposition | Adds material (conformal or bottom-up fill) | Moderate |
| **Subtractive** | Etch, CMP | Removes material (selectively) | Moderate |
| **Patterning** | Lithography | Transfers layout to resist | High (curvilinear, OPC) |
| **Planarization** | CMP | Flattens topography | Moderate |
| **Modification** | Implant, Anneal | Changes material properties (no geometry change) | Not modeled |

---

## 2. Lithography

### 2.1 Process Description

| Step | Action | Geometric Effect |
|---|---|---|
| **Photoresist coating** | Spin-cast liquid resist to uniform thickness | Creates flat film of thickness $T_{\text{resist}}$ |
| **Soft bake** | Evaporate solvent | Minor shrinkage (<5%) |
| **Exposure** | UV/EUV through mask | Chemically alters exposed regions |
| **Post-exposure bake** | Activate chemical reaction | Minor diffusion of acid (<5 nm) |
| **Development** | Dissolve soluble resist regions | Creates resist pattern with sidewall profile |
| **Hard bake** | Stabilize resist | Minor shrinkage, slight flow (corner rounding) |

### 2.2 Geometric Parameters

| Parameter | Symbol | Typical Range | SEM Relevance |
|---|---|---|---|
| Resist thickness | $T_{\text{res}}$ | 50–300 nm | Affects etch selectivity and profile |
| Sidewall angle (resist) | $\theta_{\text{res}}$ | 85–89° | Transfers to underlying layer during etch |
| Corner rounding (top) | $R_{\text{top}}$ | 5–30 nm | Affects line top profile |
| Corner rounding (bottom) | $R_{\text{bottom}}$ | 5–30 nm | Affects line base profile |
| Critical dimension (mask) | $\text{CD}_{\text{mask}}$ | Per design | Starting point for all downstream CDs |
| Line edge roughness | $\sigma_{\text{LER}}$ | 2–5 nm (3σ) | **Deferred to Phase 3.3** |

### 2.3 Resist Profile Model

**Inference:** For geometry generation, the lithography step creates a trapezoidal resist profile with rounded corners:

```
         ▄▄▄▄▄▄▄▄▄▄▄▄▄       ← Top CD (rounded edges)
        ▐            ▌
        ▐            ▌        ← Sidewall angle θ_res
        ▐            ▌
         ▀▀▀▀▀▀▀▀▀▀▀▀▀       ← Bottom CD (rounded edges)

Profile parameters: Top CD, Bottom CD > Top CD (for resist, typically)
Height = T_res
Sidewall angle = 85–89°
Corner radius (top) = R_top
Corner radius (bottom) = R_bottom
```

**Engineering Decision:** The lithography model produces a trapezoidal resist profile parameterized by $\text{CD}_{\text{mask}}$, $T_{\text{res}}$, $\theta_{\text{res}}$, $R_{\text{top}}$, and $R_{\text{bottom}}$. Curvilinear effects (OPC, assist features) are beyond the scope of geometry generation — the layout is assumed to be the target mask shape.

---

## 3. Etching

### 3.1 Process Classification

| Etch Type | Directionality | Typical Sidewall | Selectivity | Used For |
|---|---|---|---|---|
| **Anisotropic (RIE)** | Vertical | 85–89° | 10:1–50:1 (to mask) | Main etches (lines, contacts, trenches) |
| **Isotropic (wet)** | All directions | <90° (undercut) | High | Sacrificial layers, cleaning |
| **Bosch (DRIE)** | Pseudo-vertical | 88–90° (scalloped) | 100:1 | Deep trenches, MEMS |
| **Atomic Layer Etch (ALE)** | Perfect vertical | ~90° | Very high | Advanced nodes (<10 nm) |

### 3.2 RIE Etch Parameters

| Parameter | Symbol | Typical Range | SEM Relevance |
|---|---|---|---|
| Etch depth | $D_{\text{etch}}$ | Per film thickness | Determines final height |
| Sidewall angle | $\theta_{\text{etch}}$ | 85–89° | **Directly affects edge profile** |
| CD bias | $\Delta\text{CD}$ | 0–10 nm | Final CD = mask CD − bias |
| Bottom corner radius | $R_{\text{cb}}$ | 3–10 nm | **Affects bottom edge profile** |
| Top corner radius | $R_{\text{ct}}$ | 2–5 nm | **Affects top edge profile** |
| Over-etch | $O_e$ | 5–20% | Affects trench bottom |
| Micro-trenching | — | 2–10 nm notch | Optional trench bottom artifact |

### 3.3 Etch Profile Model

```
Resist mask:
  ▄▄▄▄▄▄▄▄▄▄▄▄▄▄
 ▐                ▌
 ▐                ▌
  ▀▀▀▀▀▀▀▀▀▀▀▀▀▀
      │
      ▼  (etch direction)
      │
┌─────┴─────┐
│  Etched   │
│  Profile  │        ← Sidewall angle θ_etch (typically 86-89°)
│           │        ← Taper: Top CD < Bottom CD (for positive profile)
│    ▄▄▄    │        ← Bottom corner rounding (R_cb)
│   ▐  ▌    │
│   ▐  ▌    │        ← Micro-trenching (optional)
│   ▀  ▀    │
└───────────┘
```

**Fact:** The etched profile follows a characteristic tapered shape. For an anisotropic RIE process with a finite sidewall angle, the bottom CD is wider than the top CD by $2D_{\text{etch}} \tan(90° - \theta_{\text{etch}})$.

---

## 4. Deposition

### 4.1 Process Classification

| Deposition Type | Conformality | Typical Uses | Geometry Effect |
|---|---|---|---|
| **PVD (sputtering)** | Poor — directional | Metal seed layers, liners | Thicker on horizontal surfaces |
| **CVD** | Good — conformal | Dielectrics, poly-Si, W | Uniform thickness on all surfaces |
| **ALD** | Excellent — atomic | High-k dielectrics, metal barriers | <1 nm uniform coverage |
| **Electrochemical (ECP)** | Bottom-up fill | Cu interconnects | Fills trenches from bottom |
| **Spin-on** | Planar | Resist, SOC, SOG | Flat top surface |

### 4.2 Conformality Model

**Inference:** For geometry generation, deposition adds a layer of material with thickness $T_{\text{dep}}$. The deposited material follows the underlying topography:

| Deposition Type | Top Surface | Sidewall | Bottom (trench) |
|---|---|---|---|
| **Conformal (CVD/ALD)** | $T_{\text{dep}}$ | $T_{\text{dep}}$ | $T_{\text{dep}}$ |
| **Bottom-up (ECP)** | $T_{\text{dep}}$ | 0 (negligible) | $T_{\text{dep}}$ (fills from bottom) |
| **PVD (directional)** | $T_{\text{dep}}$ ($\cos\theta$) | $T_{\text{dep}}/3$ (shadowed) | $T_{\text{dep}}/2$ |
| **Spin-on** | $T_{\text{dep}}$ (planar) | Thin | Thin (planarizes) |

---

## 5. Chemical Mechanical Planarization (CMP)

### 5.1 Process Description

| Aspect | Detail |
|---|---|
| **Action** | Mechanical abrasion + chemical etching with slurry |
| **Result** | Removes topography to create flat surface |
| **What it removes** | Material above a target planarization height |
| **Typical removal** | 50–500 nm (depending on step height) |
| **Selectivity** | Different materials remove at different rates |

### 5.2 CMP Geometry Effects

| Effect | Description | Magnitude | SEM Relevance |
|---|---|---|---|
| **Global planarization** | Overall topography reduction | Full step height | **Essential** |
| **Dishing** | Concave surface in wide metal lines | 5–50 nm depth | **Important** |
| **Erosion** | Height loss in dense pattern regions | 5–30 nm | **Important** |
| **Corner rounding** | Slight edge rounding at dielectric/metal interface | 2–10 nm | **Minor** |

### 5.3 CMP Model

```
Before CMP:
  ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄       ← Topography (e.g., deposited metal)
 ▐█████████████████▌
 ▐███        █████▌
 █████      ███████
████████████████████████  ← Barrier layer

After CMP:
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀  ← Planarized surface (target height)
 █          ████           ← Metal dishing (concave)
▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄  ← Dielectric at target height
```

**Engineering Decision:** CMP is modeled as removal of all material above a target height $H_{\text{CMP}}$ with a material-dependent dishing depth $\Delta h_{\text{dish}}$ applied to wide features.

---

## 6. Process Integration: The Layer Loop

### 6.1 Single-Layer Processing

For each layer in the stack, the geometry generator applies:

```
Input: Current 3D structure (from previous layers)
               │
               ▼
┌──────────────────────────────────┐
│  Deposition: Add film of material │  (→ new top layer on existing topography)
│  Thickness = T_dep                │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│  Lithography: Apply resist mask   │  (→ patterned resist on film)
│  from GDSII layer                 │
│  CD = CD_mask, Sidewall = θ_res  │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│  Etch: Transfer pattern into film │  (→ etched pattern in film)
│  Bias = ΔCD, Sidewall = θ_etch   │
│  Over-etch = O_e                  │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│  Resist Strip: Remove resist      │  (→ film with etched pattern)
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│  CMP (if needed): Planarize      │  (→ flat surface at target height)
│  Target height = H_CMP           │
└──────────────┬───────────────────┘
               │
               ▼
       Output: Updated 3D structure (height map + material map)
```

### 6.2 Layer Stack Processing

The layers are processed sequentially from bottom to top:

```
Substrate (Si)
Layer 1: STI → SiO₂ deposition + lithography + etch + CMP
Layer 2: Gate → poly/metal deposition + lithography + etch
Layer 3: Spacer → Si₃N₄ deposition + isotropic etch
Layer 4: Contact ILD → SiO₂ deposition + CMP
Layer 5: Contact → lithography + etch + W fill + CMP
Layer 6: M1 ILD → SiO₂ deposition
Layer 7: M1 trench → lithography + etch + Cu fill + CMP
... and so on for each BEOL layer
```

**Engineering Decision:** Each layer's processing depends on the topography created by all previous layers. The geometry engine must process layers in order, maintaining a 2.5D height field that evolves as each step is applied.

---

## 7. Steps with No Geometric Effect

| Step | Why No Geometric Effect |
|---|---|
| **Implantation** | Changes doping (electrical properties only). No geometric change visible in SEM. |
| **Annealing** | Causes dopant diffusion. <5 nm material movement. Negligible for CD-SEM. |
| **Cleaning** | Removes residues (sub-nm). No geometric change. |
| **Pre-clean** | Native oxide removal (1–2 nm). Too thin to affect SEM contrast. |
| **Silicidation** | Forms silicide at interface. Electrical effect only. |
| **Dehydration bake** | Removes moisture. No geometric change. |

---

## Sources

- [F1] J. D. Plummer, M. D. Deal, P. B. Griffin, *Silicon VLSI Technology*, Prentice Hall, 2000.
- [F2] S. Wolf and R. N. Tauber, *Silicon Processing for the VLSI Era*, Lattice Press, 2002.
- [F3] C. Mack, *Fundamental Principles of Optical Lithography*, Wiley, 2007.
- [F4] M. Quirk and J. Serda, *Semiconductor Manufacturing Technology*, Prentice Hall, 2001.
- [F6] M. J. Madou, *Fundamentals of Microfabrication and Nanotechnology*, CRC Press, 2011.
- [F8] Y. Taur and T. H. Ning, *Fundamentals of Modern VLSI Devices*, Cambridge, 2021.
- [F10] S. Franssila, *Introduction to Microfabrication*, 2nd ed. Wiley, 2010.
- [F11] K. Seshan, *Handbook of Thin Film Deposition*, 3rd ed. Elsevier, 2012.
