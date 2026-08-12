# Feature Cross-Section Models

**Research Phase:** 3.2
**Document:** 04_feature_cross_section_models.md
**Date:** 2026-07-30

---

## 1. Methodology

For each semiconductor feature, this document compares:
1. **Ideal CAD geometry** — as drawn in GDSII
2. **Fabricated geometry** — as produced by manufacturing processes
3. **Modeled geometry** — the simplified geometric model for the renderer

---

## 2. BEOL Features

### 2.1 Isolated Metal Line

| Aspect | Ideal CAD | Fabricated | Modeled |
|---|---|---|---|
| **Cross-section** | Rectangle | Trapezoid with rounded corners | **Trapezoid + corner radii** |
| **Sidewall** | Vertical (90°) | 86–89° taper | $\theta_{\text{taper}}$ (parameter) |
| **Top corners** | Sharp (90°) | $R = 3$–10 nm | $R_{\text{top}}$ (parameter) |
| **Bottom corners** | Sharp (90°) | $R = 5$–15 nm | $R_{\text{bottom}}$ (parameter) |
| **Top surface** | Flat | Flat or slightly concave | Flat |
| **CD** | $\text{CD}_{\text{mask}}$ | $\text{CD}_{\text{top}} < \text{CD}_{\text{bottom}}$ | $\text{CD}_{\text{mean}} = \text{CD}_{\text{mask}} - \Delta\text{CD}$ |
| **Height** | $H$ (nominal) | $H \pm 5$% | $H$ (target) |

**Modeled cross-section:**
```
      R_top           R_top       ← Top CD (rounded)
    ╱    ╲           ╱    ╲
   ╱      ╲         ╱      ╲
  ╱        ╲       ╱        ╲    ← Sidewall angle θ_taper (85-89°)
 ▕          ▐     ▐          ▏
 ▕          ▐     ▐          ▏
    R_bottom     R_bottom    ← Bottom CD (rounded)
```

**Dominant geometric differences from ideal:**
1. Non-vertical sidewalls (1–5° from vertical) — **essential to model**
2. Corner rounding (3–15 nm radius) — **essential to model**
3. CD bias (0–10 nm) — **essential to model**

### 2.2 Dense Line/Space Array

| Aspect | Fabricated Difference from Ideal |
|---|---|
| **Sidewall angle** | Same as isolated lines, but may differ due to pattern density |
| **Feature height** | May be lower in dense regions (etch lag) |
| **Space bottom** | May have residues or micro-trenching in high AR spaces |
| **CD variation** | Dense vs. isolated CD difference (pitch-dependent etch bias) |

**Modeled cross-section:**
```
   ▐███▌  ▐███▌  ▐███▌  ▐███▌  ← Tapered profile
  ▐███▌  ▐███▌  ▐███▌  ▐███▌
 ▐███▌  ▐███▌  ▐███▌  ▐███▌
 ████████████████████████████  ← Substrate
```

### 2.3 Contact Hole

| Aspect | Fabricated Difference from Ideal |
|---|---|
| **Shape** | Slightly conical (top diameter > bottom diameter) |
| **Top opening** | Rounded edge |
| **Bottom** | Rounded or flat with corner rounding |
| **Sidewall** | 87–89° taper |
| **Fill** | Can have recess (dishing) after CMP |

**Modeled cross-section:**
```
Plan view:        Cross-section:
   ▄▄▄▄▄            Top opening
  ▐     ▌     ▄▄▄▄▄▄▄▄▄▄▄▄  ← Cap layer
  ▐     ▌    ▐  \    /  ▌
  ▐ CNC ▌    ▐   \  /   ▌    ← Tapered sidewall
  ▐     ▌    ▐    ██    ▌    ← Fill metal (W or Cu)
  ▐     ▌    ▐   /  \   ▌
   ▀▀▀▀▀      ▀▀▀▀▀▀▀▀▀▀  ← Bottom (smaller CD)
```

### 2.4 Via

| Aspect | Fabricated Difference from Ideal |
|---|---|
| **Shape** | Conical (similar to contact but shallower) |
| **Barrier/liner** | Thin conformal layer inside via before fill |
| **Bottom interface** | May have interface resistance layer (∼1 nm) |
| **CMP recess** | Dishing after CMP (shallower than wide lines) |

**Fact:** Vias are structurally similar to contacts but positioned between metal layers. Their aspect ratio is typically 1:1 to 3:1 (vs. 5:1 to 15:1 for contacts).

---

## 3. FEOL Features

### 3.1 FinFET Fin

| Aspect | Ideal | Fabricated | Modeled |
|---|---|---|---|
| **Cross-section** | Rectangle | Trapezoid with rounded top | **Trapezoid** |
| **Fin top** | Flat (sharp corners) | Rounded top (R = 2–4 nm) | $R_{\text{top}}$ |
| **Fin width** | $\text{CD}_{\text{mask}}$ | Bottom > Top (taper) | $\text{CD}_{\text{top}}$, $\text{CD}_{\text{bottom}}$ |
| **Fin height** | $H$ | $H$ | $H$ |
| **Sidewall** | 90° | 87–89° | $\theta_{\text{taper}}$ |
| **STI recess** | Sharp step | Gradual transition | Rounded corner |

**Modeled cross-section:**
```
      R_top
    ╱▔▔▔╲         ← Fin top (rounded)
   ╱     ╲
  ╱       ╲       ← Tapered sidewall (87-89°)
 ▕         ▐
 ▕         ▐
 ▕  ▄▄▄▄▄  ▐
  ▕▐█████▌▐       ← STI oxide recessed from fin sidewall
   ▀▀▀▀▀▀▀
   █████████████  ← Si substrate (below STI)
```

**Inference:** Fins are the most sensitive structure to sidewall angle. A 1° taper on a 40 nm tall fin changes the bottom CD by ∼1.4 nm — significant at 5–8 nm fin width.

### 3.2 Gate Stack

| Aspect | Ideal | Fabricated | Modeled |
|---|---|---|---|
| **Cross-section** | Rectangular stack | Multi-layer trapezoid | **Multi-trapezoid** |
| **Work function metals** | Not represented | 2–4 distinct metal layers | As separate material layers |
| **Spacers** | Not represented | SiN/SiO₂ on sidewalls | Conformal deposition on gate |
| **Gate length** | $\text{CD}_{\text{mask}}$ | $\text{CD}_{\text{bottom}}$ defines channel | $\text{CD}_{\text{mean}}$ |
| **Height** | $H$ | $H$ | $H$ |

**Modeled cross-section:**
```
      ▄▄▄▄▄▄▄▄▄▄▄▄          ← Gate metal (e.g., W, TiN/WF)
     ╱ ▄▄▄▄▄▄▄▄▄▄ ╲
    ╱  ▐          ▌ ╲        ← Spacer (Si₃N₄) on sidewalls
   ╱   ▐   HK/MG  ▌   ╲
  ╱    ▐    Gate   ▌    ╲
 ▕     ▐__________▌      ▏
 ▕     │          │      ▏
 ▕   Fin        Fin      ▏
```

### 3.3 Shallow Trench Isolation (STI)

| Aspect | Ideal | Fabricated | Modeled |
|---|---|---|---|
| **Cross-section** | Rectangular trench | Tapered trench | **Trapezoidal trench** |
| **Top corners** | Sharp (90°) | Rounded (R = 5–20 nm) | $R_{\text{top}}$ |
| **Bottom corners** | Sharp (90°) | Rounded (R = 5–30 nm) | $R_{\text{bottom}}$ |
| **Sidewall** | Vertical | 87–89° | $\theta_{\text{taper}}$ |
| **Fill** | Oxide to top | Slight recess (CMP) | Flat at surface |

**Modeled cross-section:**
```
   ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄   ← Substrate surface
  ╱    ▄▄▄▄▄▄▄     ╲
 ╱    ▐  Oxide ▐     ╲        ← Tapered trench
▕     ▐  Fill  ▐      ▏
▕     ▐        ▐      ▏
▕     ▐________▐      ▏       ← Rounded bottom
▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔  ← Si substrate
```

---

## 4. Dielectric Layer Effects

### 4.1 Inter-Layer Dielectric (ILD)

| Effect | Description | Magnitude | Modeled? |
|---|---|---|---|
| **Global planarization** | CMP removes topography | Full step height | **Yes** |
| **Local thinning over patterns** | ILD thinner over dense features | 5–20% | Optional |
| **Gap fill** | Can have voids in high AR gaps | Voids possible | **Not modeled** |

### 4.2 Conformal Dielectric (e.g., Sidewall Spacer)

| Effect | Description | Magnitude | Modeled? |
|---|---|---|---|
| **Sidewall thickness** | Conformal on vertical surfaces | Uniform | **Yes** |
| **Corner thinning** | Slightly thinner at convex corners | 5–10% | Optional |

---

## 5. Cross-Section Parameter Summary

| Feature | Parameter | Unit | Typical (N5) | Modeled in Geometry Engine |
|---|---|---|---|---|
| **All features** | Sidewall angle | ° | 85–88 | **Yes** — configurable per layer |
| **All features** | Top corner radius | nm | 2–5 | **Yes** |
| **All features** | Bottom corner radius | nm | 3–10 | **Yes** |
| **Metal line** | CD bias | nm | 2–8 | **Yes** |
| **Contact/via** | Taper angle | ° | 87–89 | **Yes** |
| **Contact/via** | Fill recess | nm | 0–10 | Optional |
| **Fin** | Fin top CD | nm | 5–8 | **Yes** |
| **Fin** | Fin bottom CD | nm | 6–10 | **Yes** |
| **Gate** | Spacer width | nm | 5–10 | **Yes** |
| **STI** | Corner radius | nm | 5–20 | **Yes** |
| **ILD** | Local thinning | nm | 0–10 | Optional |

---

## 6. Critical vs. Non-Critical Differences

### 6.1 Critical (Must Model)

- **Sidewall taper** — directly affects SEM edge profile width and CD measurement
- **Corner rounding (top and bottom)** — affects SEM edge intensity maximum
- **CD bias** — determines final CD from mask CD
- **Feature height** — determines intensity scaling

### 6.2 Important (Should Model)

- **CMP dishing** — affects wide feature SEM profile (visible as contrast variation across wide lines)
- **Spacer formation** — affects gate SEM profile (sidewall material contrast)
- **Over-etch / micro-trenching** — affects trench bottom SEM profile

### 6.3 Minor (Model if Time Permits)

- **Resist corner rounding** — secondary effect transferred through etch
- **CMP erosion in dense arrays** — subtle height difference
- **Local ILD thinning** — small effect on planarity

### 6.4 Ignored

- **Line edge roughness** (Phase 3.3)
- **Voids in dielectrics** (rare, process-dependent)
- **Silicide formation** (no geometric effect)
- **Epitaxial growth faceting** (SiGe S/D shaping — complex, limited SEM visibility)

---

## Sources

- [F1] J. D. Plummer, *Silicon VLSI Technology*, Prentice Hall, 2000.
- [F2] S. Wolf, *Silicon Processing for the VLSI Era*, Lattice Press, 2002.
- [F8] Y. Taur, *Fundamentals of Modern VLSI Devices*, Cambridge, 2021.
- [F9] imec, "Core technology scaling," 2023.
- [F10] S. Franssila, *Introduction to Microfabrication*, Wiley, 2010.
- [F12] J. M. Steigerwald, *CMP of Microelectronic Materials*, Wiley, 2004.
- [F13] B. Wu and A. Kumar, *Extreme Ultraviolet Lithography*, McGraw-Hill, 2009.
- [F14] C. T. Gabriel, "Sidewall profile modeling," *J. Vac. Sci. Technol. B*, vol. 28, 2010.
