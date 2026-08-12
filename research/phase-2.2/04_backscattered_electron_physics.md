# Backscattered Electron Physics

**Research Phase:** 2.2
**Document:** 04_backscattered_electron_physics.md
**Date:** 2026-07-30

---

## 1. Introduction

Backscattered electrons (BSEs) are primary beam electrons that escape from the sample after undergoing one or more large-angle elastic scattering events. They carry information about the sample's composition and subsurface structure. While they do not offer the spatial resolution of SEs, their strong atomic-number dependence makes them invaluable for material identification and voltage contrast in semiconductor inspection.

**Definition:** BSEs are primary electrons that re-emerge from the sample surface with energy greater than 50 eV (the conventional cutoff between SE and BSE).

---

## 2. Generation Mechanism

### 2.1 Elastic Scattering Escape

A primary electron becomes a BSE when it undergoes elastic scattering through a cumulative angle >90° such that its trajectory is directed back toward the surface, and it reaches the surface with sufficient energy to escape. This process can involve:

- **Single large-angle event:** A single close approach to a nucleus deflects the electron through >90° (rare, especially at high energies).
- **Multiple small-angle events:** A series of smaller deflections cumulatively redirect the electron back toward the surface (the most common path for BSE generation).

**Fact:** In low-Z materials, most BSEs result from multiple small-angle scattering events. In high-Z materials, single large-angle events contribute more significantly because the nuclear charge is larger.

### 2.2 Energy Characteristics

Unlike SEs (which have energies <50 eV), BSEs retain a significant fraction of the primary beam energy $E_0$:

| Class | Energy | Typical $E/E_0$ |
|---|---|---|
| Low-loss BSE | Near $E_0$ | 0.9–1.0 |
| Moderate-loss BSE | Intermediate | 0.5–0.9 |
| High-loss BSE | Near SE cutoff | 0.05–0.5 |

**Fact:** The BSE energy spectrum is broad, extending from ~50 eV up to the primary beam energy $E_0$. The highest energy BSEs (those with $E/E_0 > 0.9$) are generated very close to the surface and carry the highest spatial resolution.

### 2.3 Angular Distribution

For a flat surface at normal incidence, BSEs are emitted with an approximately **cosine angular distribution**:

$$\frac{dN_{\text{BSE}}}{d\Omega} \propto \cos\theta$$

where $\theta$ is measured from the surface normal.

**Inference:** The cosine distribution means BSEs are most likely to be emitted normal to the surface, with decreasing probability at glancing angles.

---

## 3. Atomic Number Dependence

### 3.1 The BSE Yield $\eta$

The BSE yield $\eta$ is defined as the number of BSEs emitted per incident primary electron:

$$\eta = \frac{I_{\text{BSE}}}{I_P}$$

**Fact:** The most important characteristic of BSE imaging is that $\eta$ increases monotonically with atomic number $Z$. This is the physical basis for compositional (Z-contrast) imaging.

### 3.2 Empirical Relationship

Several empirical relationships have been developed. A commonly used one (Reimer, 1998) for energies >10 keV is:

$$\eta = -0.0254 + 0.016 Z - 0.000186 Z^2 + 8 \times 10^{-7} Z^3$$

For the energy range 5–30 keV, a simpler approximation (Arnal, 1969) is:

$$\eta = 0.025 + 0.016 Z - 0.00023 Z^2 + 2.8 \times 10^{-7} Z^3$$

**Fact:** At low atomic numbers, $\eta$ increases approximately linearly with $Z$. At high $Z$, the increase becomes sub-linear.

| Material | Z | $\eta$ (10–20 keV) | $\eta$ at 1 keV |
|---|---|---|---|
| Photoresist (C) | 6 | ~0.06–0.08 | ~0.08–0.10 |
| SiO₂ (avg) | ~10 | ~0.12–0.14 | ~0.14–0.18 |
| Si | 14 | ~0.17–0.19 | ~0.18–0.22 |
| Si₃N₄ (avg) | ~11 | ~0.13–0.15 | ~0.15–0.19 |
| Cu | 29 | ~0.31–0.33 | ~0.30–0.35 |
| W | 74 | ~0.49–0.52 | ~0.45–0.55 |

**Note:** The values at 1 keV are less certain because the empirical formulas were primarily developed for higher energies (>5 keV). There is significant spread in published measurements for low keV BSE yields.

### 3.3 Pendry (Joy) Model for Low Energy

At energies below ~5 keV, the Reimer formula becomes inaccurate. The Joy model provides an alternative:

$$\eta(E_0) = \frac{1}{1 + k \Gamma E_0^{0.5}}$$

where $k$, $\Gamma$ are material-dependent parameters. This model predicts that BSE yield **increases** as beam energy decreases below ~5 keV.

**Inference:** At CD-SEM operating energies (300 eV–1.5 keV), BSE yield can be 1.5–3× higher than at 10–20 keV. This means BSE signals contribute more to the total emitted current at low voltages than is commonly expected.

---

## 4. Penetration Depth and Escape

### 4.1 BSE Escape Depth

BSEs escape from significantly greater depths than SEs. The maximum escape depth for BSEs is approximately:

$$z_{\text{BSE, max}} \approx 0.3 \times R_{\text{Bethe}}$$

where $R_{\text{Bethe}}$ is the Bethe range (total path length).

| Material | BSE Escape Depth at 1 keV | BSE Escape Depth at 10 keV |
|---|---|---|
| Si | ~10 nm | ~0.5 μm |
| Cu | ~5 nm | ~0.2 μm |
| W | ~2 nm | ~0.05 μm |

**Fact:** BSE images contain information from significantly deeper within the sample than SE images. This has two consequences:
1. Subsurface features are visible in BSE mode.
2. Lateral resolution is degraded because BSEs can emerge from a wide area around the beam impact point.

### 4.2 Spatial Resolution of BSE

The effective resolution of a BSE image is limited by the lateral extent of the escape region:

| Parameter | SE (at 1 keV) | BSE (at 1 keV) | BSE (at 10 keV) |
|---|---|---|---|
| Effective resolution | ~1–3 nm | ~5–20 nm | ~100–500 nm |
| Information depth | ~1–5 nm | ~5–20 nm | ~0.1–1 μm |

---

## 5. Angular Distribution and Dependence

### 5.1 Dependence on Incident Angle

As the beam incident angle $\theta$ (measured from surface normal) increases:

1. The BSE yield increases.
2. The angular distribution of emitted BSEs shifts from cosine to peaked in the forward direction.

**Fact:** For a tilted sample, more BSEs emerge in the direction of the incident beam (forward scattering) than in the opposite direction.

### 5.2 Dependence on Beam Energy

The energy dependence of $\eta$ varies by regime:

| Regime | Energy | Behavior |
|---|---|---|
| High | >20 keV | $\eta$ is approximately constant |
| Medium | 5–20 keV | $\eta$ slowly decreases slightly with increasing $E$ |
| Low | 0.5–5 keV | $\eta$ increases as $E$ decreases |
| Very low | <0.5 keV | $\eta$ rises sharply; Reimer formula breaks down |

---

## 6. BSE Contrast Mechanisms

### 6.1 Compositional (Z) Contrast

**Fact:** The monotonic Z-dependence of $\eta$ is the foundation of compositional BSE imaging. A material with higher Z produces more BSEs and appears brighter in the image.

For semiconductor structures:
- W (Z=74) appears much brighter than Si (Z=14).
- Cu lines (Z=29) appear brighter than surrounding SiO₂ (Z~10).
- Photoresist on Si shows very low contrast because both are low-Z materials.

The compositional contrast between two materials A and B is:

$$C_{\text{Z}} = \frac{\eta_A - \eta_B}{\eta_A + \eta_B}$$

**Representative contrast values (at 10 keV):**

| Material Pair | Z Difference | BSE Contrast $C_Z$ |
|---|---|---|
| W vs. SiO₂ | 64 | ~0.55 |
| Cu vs. SiO₂ | 19 | ~0.36 |
| Cu vs. Si | 15 | ~0.22 |
| Si vs. SiO₂ | 4 | ~0.11 |
| Photoresist vs. Si | ~8 | ~0.08 |

**Inference:** Compositional contrast is strong for metal-dielectric interfaces but weak for resist-on-silicon structures. This is a limitation of BSE imaging for resist metrology.

### 6.2 Topographic BSE Contrast

**Fact:** BSE images also contain topographic information, though it is weaker than in SE images. Topographic contrast in BSE arises from:
- The tilt dependence of $\eta$.
- Shadowing of BSEs by topography features.
- Detection geometry (annular BSE detectors can produce topographic contrast by differencing opposite quadrants).

### 6.3 Voltage Contrast

**Fact:** In semiconductor inspection, BSE imaging in voltage contrast (VC) mode is a critical technique for detecting electrical defects:

- A grounded conductor emits a certain BSE signal.
- A floating (electrically isolated) conductor charges under the beam, developing a negative potential.
- The negative potential repels BSEs, reducing the detected signal.
- Open contacts and vias appear dark relative to grounded ones.

**Inference:** Voltage contrast is an essential application of BSE imaging in semiconductor defect review. It enables detection of electrical defects (opens, shorts) without physical contact.

---

## 7. Experimental Measurement of BSE Signals

### 7.1 Detector Considerations

| Detector Type | Suitable for BSE? | Notes |
|---|---|---|
| **Solid-state annular BSE** | Yes | Best for compositional imaging; 4-quadrant allows topographic separation |
| **In-lens BSE** | Yes | High collection efficiency; good for low beam currents |
| **Everhart-Thornley (negative bias)** | Yes | Switchable between SE and BSE mode |
| **TTL SE (positive bias)** | No | Only collects low-energy SEs |

### 7.2 Distinguishing BSE from SE

In many detector configurations, SE and BSE signals are mixed. The distinction in practice relies on:
- **Detector bias:** Positive bias collects SEs; negative bias repels SEs, collecting only BSEs.
- **Energy filtering:** Some detectors apply an energy threshold to separate signals.
- **Time-of-flight:** BSEs arrive at the detector earlier than SEs due to their higher velocity.

---

## 8. SE vs. BSE: When to Use Each

### 8.1 Decision Matrix

| Application | Best Signal | Reason |
|---|---|---|
| CD measurement (lines, contacts) | SE | Highest resolution, strong edge signal |
| Resist profile measurement | SE | Surface sensitivity, topographic contrast |
| Metal gate CD | SE or BSE | SE for edge definition, BSE for material boundary |
| Void detection in metal lines | BSE | Z-contrast reveals voids in metal |
| Contact open detection | BSE (voltage contrast) | Electrical state detection |
| Material identification | BSE | Z-contrast discrimination |
| Thin film thickness measurement | BSE | Depth-dependent signal |
| Defect review (general) | SE + BSE | Combined topographic and compositional information |

### 8.2 Recommendation for CD-SEM

**Inference:** For CD-SEM, the primary imaging signal should be SE (SE-I) for its superior spatial resolution. BSE should be used as a secondary channel for:
- Material identification when composition is in question.
- Voltage contrast inspection for contact/via opens.
- Situations where the SE signal is weak (e.g., very flat surfaces with no topographic variation).

---

## 9. Summary of BSE Physical Parameters

| Parameter | Range | Critical for Simulation? |
|---|---|---|
| Energy range | 50 eV – $E_0$ | Yes — determines escape behavior |
| Yield $\eta$ | 0.05–0.55 | Yes — determines signal strength |
| Z-dependence | $\eta \propto Z$ (approx.) | Yes — the basis of Z-contrast |
| Escape depth | 0.3× Bethe range | Yes — determines resolution |
| Angular distribution | Cosine (flat surface) | Yes — affects collection |
| Energy dependence | $\eta$ increases at low kV | Yes — relevant for CD-SEM |
| Spatial resolution | 5–500 nm (energy-dependent) | Yes — determines when BSE is useful |

---

## Sources

- L. Reimer, *Scanning Electron Microscopy: Physics of Image Formation and Microanalysis*, 2nd ed. Springer, 1998.
- J. I. Goldstein, D. E. Newbury, J. R. Michael, et al., *Scanning Electron Microscopy and X-Ray Microanalysis*, 4th ed. Springer, 2017.
- R. F. Egerton, *Physical Principles of Electron Microscopy*, 2nd ed. Springer, 2016.
- D. C. Joy and S. Luo, "An empirical model for the electron backscattering coefficient," *Scanning*, vol. 11, pp. 176–180, 1989.
- F. Arnal, J. L. Verdier, and P. D. Vincensini, "Coefficient de retrodiffusion dans le cas d'electrons monokinetiques," *C. R. Acad. Sci. Paris*, vol. 268, 1969.
- D. C. Joy, *Monte Carlo Modeling for Electron Microscopy and Microanalysis*. Oxford University Press, 1995.
- H. Niedrig, "Electron backscattering from thin films," *J. Appl. Phys.*, vol. 53, 1982.
- H. Seiler, "Secondary electron emission in the scanning electron microscope," *J. Appl. Phys.*, vol. 54, 1983.
- Nanoscience Instruments, "Scanning Electron Microscopy," technical resource.
