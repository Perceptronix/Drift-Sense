# Secondary Electron Contrast Mechanisms

**Research Phase:** 2.3
**Document:** 03_secondary_electron_contrast.md
**Date:** 2026-07-30

---

## 1. Introduction

Secondary electron contrast — the variation in detected SE signal across a sample — is the primary mechanism for revealing topographic and material information in SEM images. This document examines every physical mechanism that contributes to SE contrast, with emphasis on those relevant to semiconductor wafer inspection.

**Fact:** SE contrast is the combination of four factors:
1. How many SEs are emitted (yield)
2. How many emitted SEs reach the detector (collection)
3. How the detector converts SEs to signal (efficiency)
4. How the signal is processed into pixel values (gain)

---

## 2. Topographic Contrast (Surface Angle Dependence)

### 2.1 The $\sec\theta$ Law

**Fact:** The most important contrast mechanism in SE imaging is the dependence of SE yield on the local angle between the incident beam and the surface normal. For a flat surface tilted by angle $\theta$ relative to the beam, the SE yield increases as:

$$\delta(\theta) = \delta_0 \cdot \sec\theta$$

where $\delta_0$ is the SE yield at normal incidence ($\theta = 0^\circ$).

**Physical origin:** When the surface is tilted, the interaction volume is closer to the surface on the "uphill" side. The increased probability that SEs generated along the tilted trajectory can escape leads to higher yield.

### 2.2 Quantitative Impact

| Surface Angle $\theta$ | $\sec\theta$ | Normalized SE Yield |
|---|---|---|
| 0° (flat, normal incidence) | 1.00 | 1.00 |
| 30° | 1.15 | 1.15 |
| 45° | 1.41 | 1.41 |
| 60° | 2.00 | 2.00 |
| 70° | 2.92 | 2.92 |
| 80° | 5.76 | 5.76 |
| 85° | 11.5 | 11.5 |

**Inference:** For a typical vertical sidewall (θ ≈ 80°–90° relative to the beam direction, depending on geometry), the SE yield enhancement can reach 5–10× compared to a flat surface. This is the physical origin of the bright edges seen in SEM images of patterned wafers.

**Important caveat:** The $\sec\theta$ law is strictly valid only for gently varying surfaces where the interaction volume is not truncated by the presence of a nearby edge. At sharp corners and vertical sidewalls, the geometry modifies the yield behavior (see Section 4 on edge brightening).

### 2.3 Experimental Validation

**Fact:** The $\sec\theta$ dependence has been validated by numerous experimental measurements and Monte Carlo simulations (Seiler, 1983; Reimer, 1998). The agreement is excellent for $\theta < 70^\circ$. Above 70°, the measured yield often deviates below the $\sec\theta$ prediction because some SEs generated near the surface are reabsorbed by the surface itself at very grazing angles.

---

## 3. Escape Probability Modulation

### 3.1 Depth-Dependent Escape

The probability that an SE generated at depth $z$ reaches the surface is:

$$P_{\text{escape}}(z) = \exp\left(-\frac{z}{\lambda \cos\phi}\right)$$

where $\lambda$ is the inelastic mean free path (IMFP) for SEs and $\phi$ is the escape angle relative to the surface normal.

**Inference:** For a flat surface, the escape probability is symmetric. For a tilted surface, the effective depth to the surface is modified. On the "uphill" side of the interaction volume, SEs have a shorter path to the surface and are more likely to escape.

### 3.2 Effective Escape Depth

| Material Class | $\lambda$ (nm) for 1–10 eV SE | Effective Escape Depth (nm) |
|---|---|---|
| Metals (Cu, W) | 0.5–1.5 | 0.5–2 |
| Semiconductors (Si) | 1–3 | 1–5 |
| Insulators (SiO₂, resist) | 5–20 | 5–30 |

**Inference:** The escape depth sets the ultimate resolution limit for topographic contrast. Metals give the sharpest edge contrast; insulators give smoother (and somewhat lower resolution) contrast because SEs can escape from deeper within the material.

---

## 4. Collection Efficiency

### 4.1 Detector Geometry Function

The detected SE signal depends not only on how many SEs are emitted but on what fraction reach the detector:

$$S(x,y) = \int_{0}^{2\pi} \int_{0}^{\pi/2} \frac{d^2N_{\text{SE}}}{d\Omega dE} \cdot \eta_{\text{coll}}(\theta_e, \phi_e) \cdot R(E) \, d\Omega \, dE$$

where:
- $d^2N_{\text{SE}} / d\Omega dE$ = angular and energy distribution of emitted SEs
- $\eta_{\text{coll}}(\theta_e, \phi_e)$ = detector collection function (0 to 1)
- $R(E)$ = detector response function (energy-dependent efficiency)

### 4.2 TTL Detector Collection

In through-the-lens (TTL) detection — the standard for CD-SEM — the collection function is approximately:

$$\eta_{\text{coll}}^{\text{TTL}}(\theta_e) \approx \eta_0 \cdot \begin{cases} 1 & \text{if } \theta_e < \theta_{\text{max}} \\ \text{decaying} & \text{if } \theta_e > \theta_{\text{max}} \end{cases}$$

where $\theta_{\text{max}}$ is determined by the acceptance angle of the lens field (typically 50°–70° from vertical).

**Characteristic of TTL detection:**
- Nearly uniform collection for SEs emitted within the acceptance cone.
- Weak dependence on azimuthal angle (symmetric about the beam axis).
- SEs emitted at grazing angles to the surface are less efficiently collected.

### 4.3 Everhart-Thornley Detector Collection

For side-mounted E-T detectors, the collection function is strongly anisotropic:

$$\eta_{\text{coll}}^{\text{ET}}(\theta_e, \phi_e) \propto \begin{cases} \text{high} & \text{if } (\theta_e, \phi_e) \text{ points toward detector} \\ \text{low} & \text{if } (\theta_e, \phi_e) \text{ points away from detector} \end{cases}$$

**Fact:** The E-T detector produces characteristic "three-dimensional" shading because surfaces tilted toward the detector are collected more efficiently than surfaces tilted away. This is the dominant contrast mechanism in many conventional SEM images but is less relevant for CD-SEM.

### 4.4 Practical Consequences for CD-SEM

| Detector | Collection Symmetry | Shadowing | Best For |
|---|---|---|---|
| **TTL (in-lens)** | Near-symmetric (azimuthal) | Minimal | CD metrology, symmetric edge profiles |
| **E-T side-mounted** | Strongly asymmetric | Significant | General topography, 3D appearance |
| **In-lens BSE** | Annular (azimuthally symmetric) | None | Z-contrast, voltage contrast |

**Recommendation:** For CD-SEM simulation, assume TTL detection with near-symmetric collection. The azimuthal dependence can be neglected to first order.

---

## 5. Material Contrast in SE

### 5.1 SE Yield Variation with Material

**Fact:** The SE yield $\delta$ varies significantly between materials at a given beam energy:

| Material | SE Yield at 500 eV | SE Yield at 1 keV |
|---|---|---|
| Si | ~1.0 | ~0.85 |
| SiO₂ | ~2.2 | ~1.8 |
| Cu | ~1.0 | ~1.1 |
| W | ~0.7 | ~0.8 |
| Photoresist (organic) | ~2.2 | ~2.0 |

**Inference:** At a fixed beam energy, different materials on a wafer produce different SE yields. This is a significant contrast mechanism in semiconductor structures:
- Photoresist on Si: ~2× SE contrast at 500 eV (resist brighter)
- SiO₂ on Si: ~2× SE contrast at 500 eV (oxide brighter)
- W on SiO₂: ~3× SE contrast (oxide brighter)

### 5.2 Why Material Contrast Exists

Three physical factors determine the SE yield for a given material:
1. **Work function / electron affinity:** Lower work function → easier SE escape → higher yield.
2. **Band gap:** Insulators typically have higher SE yields than conductors because SEs can travel farther (longer IMFP) and escape from greater depths.
3. **Atomic density:** Higher density → more SEs generated per unit volume → potentially higher yield, but also shorter escape depth.

---

## 6. Voltage Contrast (Local Field Effects)

### 6.1 Origin

**Fact:** When a conductor is electrically floating, it charges under the electron beam. The local electric field from this charged region can modify the SE yield:

- **Positively charged region:** The field attracts SEs back to the sample → reduced detected signal (dark).
- **Negatively charged region:** The field repels SEs from the sample → increased detected signal (bright) if the detector can collect them, or reduced signal if SEs are deflected away from the detector.

### 6.2 Application in Semiconductor Inspection

Voltage contrast in BSE imaging is a standard technique for detecting open contacts and vias:
- A grounded contact → normal SE/BSE signal.
- An open (floating) contact → charges to a different potential → altered SE/BSE signal.
- Open contacts appear darker (negative charging) or brighter (positive charging) than grounded ones.

---

## 7. Magnetic Contrast

### 7.1 Type-I Magnetic Contrast (SE)

**Fact:** SE trajectories can be deflected by local magnetic fields above the sample surface. The Lorentz force on the SEs changes their trajectory, affecting collection efficiency. This is observed in ferromagnetic materials but is **not relevant** for standard semiconductor materials (Si, SiO₂, Cu, W are non-magnetic).

### 7.2 Engineering Conclusion

**Recommendation:** Magnetic contrast can be safely ignored for semiconductor SEM simulation.

---

## 8. Summary of SE Contrast Mechanisms

| Contrast Mechanism | Physical Origin | Magnitude | Relevance for CD-SEM |
|---|---|---|---|
| **Topographic ($\sec\theta$)** | Surface tilt modifies emission | 1–10× | **Primary** — edge detection |
| **Material (compositional)** | Z-dependent SE yield | 1–3× | **Significant** — material boundaries |
| **Collection anisotropy** | Detector position relative to sample | 1–5× | **Important** — detector geometry model |
| **Escape depth modulation** | IMFP variation with material | Modifies edge sharpness | **Moderate** — affects resolution |
| **Voltage contrast** | Local charging modifies emission/collection | 0.1–2× | **Important** — defect detection |
| **Shadowing** | Topography blocks SE paths | 0–1× | **Moderate** — high aspect ratios |
| **Magnetic** | Lorentz deflection of SE | Small | **None** (Si, Cu, W non-magnetic) |

---

## 9. Mathematical Contrast Model

The total SE signal at position $(x,y)$ can be written as:

$$I_{\text{SE}}(x,y) = G \cdot \eta_{\text{coll}}(x,y) \cdot \left[ \underbrace{\delta_{\text{mat}}(Z) \cdot \sec\theta(x,y)}_{\text{emission}} + \Delta I_{\text{SE-II}}(x,y) \right] + I_0$$

where:
- $G$ = system gain
- $\eta_{\text{coll}}$ = detector collection efficiency
- $\delta_{\text{mat}}(Z)$ = material-dependent SE yield at normal incidence
- $\theta(x,y)$ = local surface angle (from surface normal)
- $\sec\theta$ = topographic enhancement factor
- $\Delta I_{\text{SE-II}}$ = SE-II contribution from backscattered electrons
- $I_0$ = constant background

**Dominant terms for CD-SEM:**
- The $\sec\theta$ term dominates at pattern edges (1–10× variation).
- The $\delta_{\text{mat}}(Z)$ term determines the baseline brightness difference between materials (1–3× variation).
- The SE-II term broadens the edge profile.

---

## Sources

- H. Seiler, "Secondary electron emission in the scanning electron microscope," *J. Appl. Phys.*, vol. 54, R1–R18, 1983.
- L. Reimer, *Scanning Electron Microscopy: Physics of Image Formation and Microanalysis*, 2nd ed. Springer, 1998.
- J. I. Goldstein, D. E. Newbury, J. R. Michael, et al., *Scanning Electron Microscopy and X-Ray Microanalysis*, 4th ed. Springer, 2017.
- D. C. Joy, *Monte Carlo Modeling for Electron Microscopy and Microanalysis*. Oxford University Press, 1995.
- R. F. Egerton, *Physical Principles of Electron Microscopy*, 2nd ed. Springer, 2016.
- M. S. Chung and T. E. Everhart, "Role of electron energy distribution in secondary electron emission," *J. Appl. Phys.*, vol. 45, 1974.
- O. C. Wells, *Scanning Electron Microscopy*. McGraw-Hill, 1974.
