# Edge Brightening in SEM Imaging

**Research Phase:** 2.3
**Document:** 04_edge_brightening.md
**Date:** 2026-07-30

---

## 1. Introduction

Edge brightening — the characteristic increase in SE signal at topographic edges — is the most important contrast mechanism for semiconductor CD metrology. The bright edges in a CD-SEM image mark the positions of pattern sidewalls, enabling edge detection and linewidth measurement.

**Definition:** Edge brightening is the localized enhancement of the detected SE signal (typically 2–10× above the flat-surface background) that occurs when the primary electron beam is positioned at or near a topographic edge.

---

## 2. Physical Mechanisms

### 2.1 Geometric Channeling Effect ($\sec\theta$ Enhancement)

The dominant mechanism: at a vertical step edge, the beam sequentially samples surfaces with varying tilt angles. As the beam approaches an edge:

1. **On the top surface, approaching the edge:** The beam footprint is close enough to the edge that the interaction volume "spills out" over the edge. Some of the deposited energy is closer to the sidewall surface than it would be on an infinite flat surface. The effective escape probability increases.

2. **At the edge corner:** The beam interacts with both the top surface and the sidewall simultaneously. The interaction volume is bounded by two exit surfaces. The effective solid angle for SE escape increases significantly.

3. **On the sidewall:** If the sidewall has high tilt angle (θ ≈ 80°–90°), the SE yield is enhanced by $\sec\theta$ (2–10× enhancement).

4. **Below the edge (bottom of trench/line):** The beam may be shadowed from the detector by the overhanging feature, reducing the detected signal.

### 2.2 Sidewall Escape (SE-II Contribution)

**Fact:** A second mechanism contributes to edge brightening especially for high-aspect-ratio structures:

1. The primary beam generates SEs along its trajectory in the material.
2. Some of the primary beam energy is deposited near the sidewall surface — even when the beam is positioned some distance away from the physical edge.
3. SEs generated in this region can escape through the sidewall surface.
4. This extends the "bright region" beyond the geometric edge position.

**The SE-II contribution:** Backscattered electrons that exit through the sidewall also generate SE-II as they cross the surface. These additional SE-II are emitted from the sidewall and contribute to the edge brightening signal at distances up to ~1 μm from the physical edge.

### 2.3 Corner Effects

At 2D topographic features (corners of lines, edge of contact holes), the edge brightening is amplified because:
- The beam is simultaneously near two perpendicular edges.
- The interaction volume is bounded by two or three near-vertical surfaces.
- The SE escape probability is further enhanced.

**Fact:** Corners can appear 1.5–2× brighter than straight edges, making them easily identifiable in CD-SEM images. This effect is particularly important for contact hole and via metrology.

---

## 3. Knife-Edge Effect

### 3.1 Definition

The "knife-edge" effect is the limiting case of edge brightening where the beam approaches a sharp, near-vertical edge of a thick sample. It describes the transition of the SE signal from the top surface (high signal at the edge) to the region beyond the sample (no signal).

### 3.2 Signal Profile Shape

For an ideal knife-edge, the SE signal as a function of beam position takes the form:

```
Signal
  │
  │     ╱╲
  │    ╱  ╲
  │   ╱    ╲_________
  │  ╱
  │ ╱
──╲╱──────────────────── Position
   ↑
  Edge position
```

- **Rising edge approach:** As the beam moves from the flat-top surface toward the edge, the signal begins to increase at a distance of ~1–2× the interaction radius from the edge.
- **Peak:** The signal maximum occurs when the beam is at or slightly inside the edge, where the interaction volume is less confined.
- **Decay:** As the beam moves past the edge (off the sample), the signal drops to near zero (if no SE-III contribution).

### 3.3 Parameters of the Edge Profile

| Parameter | Controlling Factors | Impact on CD Metrology |
|---|---|---|
| **Peak amplitude** | Edge angle, material, beam energy, probe size | Determines contrast for edge detection |
| **Peak position** | Physical edge location (to first order) | Determines CD measurement accuracy |
| **Rise distance** (10–90%) | Probe diameter, interaction volume, escape depth | Determines edge detection resolution |
| **Background level** | Flat-surface SE yield, SE-III, BSE | Determines baseline for contrast |

---

## 4. The CD-SEM Edge Profile

### 4.1 Characteristic Shape

For a line on a semiconductor wafer, the SE signal profile across a single edge has been characterized extensively in the CD-SEM literature:

```
I(x) = I_b + I_p \cdot \exp\left(-\frac{(x - x_0)^2}{2\sigma_{\text{probe}}^2}\right) * \Pi\left(\frac{x - x_0}{L}\right)
```

where $*$ denotes convolution, $I_b$ is the background (flat-surface) signal, $I_p$ is the peak enhancement, $x_0$ is the edge position, $\sigma_{\text{probe}}$ is the effective probe radius, and $\Pi$ is the rectangular function representing the surface tilt variation across the edge.

### 4.2 Material and Geometry Dependence

The edge profile shape varies with:

| Parameter | Effect on Profile |
|---|---|
| **Beam energy** | Higher energy → larger interaction volume → broader edge peak |
| **Sidewall angle** | Steeper sidewall → stronger peak |
| **Material (top)** | Higher $\delta$ → higher peak and background |
| **Material (bottom)** | Different yield at foot of sidewall → asymmetric profile |
| **Probe diameter** | Larger probe → broader, lower peak |
| **Detector configuration** | Collection asymmetry → asymmetric profile |

### 4.3 Profile Asymmetry

**Fact:** In CD-SEM images of lines on semiconductor wafers, the left and right edge profiles are often asymmetric. This can arise from:
- **Sidewall angle asymmetry:** The left and right sidewalls of a line may have different slopes.
- **Material asymmetry:** Different materials on opposite sides of the edge.
- **Detector asymmetry:** If using a side-mounted detector, edges parallel to the detector direction will appear different from perpendicular edges.

---

## 5. Detector Shadowing Effects

### 5.1 Shadowing at Deep Features

For high-aspect-ratio structures (deep trenches, DRAM capacitors), the detector may not have a direct line-of-sight to the bottom of the feature:

- **TTL detector:** The collection field can extract SEs from moderate depths (up to ~1 μm depth for narrow features). Deeper features show reduced signal at the bottom.
- **E-T detector:** Significant shadowing. The bottom of deep features appears dark because SEs cannot escape to the off-axis detector.

### 5.2 Re-Entrant Features

For re-entrant profiles (undercut features, common in certain etching processes):

- The top of the feature overhangs, blocking SEs from the bottom from reaching the detector.
- The bottom edges may appear dark even though they are topographic edges.
- This shadowing provides useful process information but complicates CD measurement.

---

## 6. Corner Effects in Detail

### 6.1 2D Edge Enhancement

At a 90° corner where two edges meet:

| Feature | Edge Enhancement | Corner Enhancement | Ratio |
|---|---|---|---|
| Straight edge (1D) | 2–5× | — | 1.0 |
| 90° outside corner | — | 4–8× | 1.5–2× |
| 90° inside corner (trench corner) | — | 1.5–3× | 0.5–0.8× |

**Inference:** Outside corners (the end of a line, the outer edge of a via pad) produce stronger SE signal than inside corners (the bottom of a trench corner). This is useful for identifying feature endpoints in CD-SEM images.

### 6.2 Contact Hole Ring Profile

For a cylindrical contact hole, the radial SE profile shows:
- Sharp peak at the top edge (entrance of the hole).
- Possibly a second, weaker peak at the bottom edge (if the hole is shallow enough for SE escape).
- Reduced signal from the bottom of the hole (if deep).
- The top-edge ring is the feature used for CD measurement.

---

## 7. Competing Models for Edge Brightening

### 7.1 Pure Geometric Model

**Model:** $I(x) \propto \sec(\theta(x))$
- **Prediction:** Edge signal peak occurs where the local surface angle is maximum.
- **Limitation:** Does not account for finite probe size or SE generation below the surface.

### 7.2 Convolution Model

**Model:** $I(x) = [\delta(x) * G(x)] \cdot \eta_{\text{coll}}(x)$
- $\delta(x)$ is the local yield (including $\sec\theta$)
- $G(x)$ is the probe intensity distribution (Gaussian)
- $\eta_{\text{coll}}(x)$ is the collection efficiency
- **Prediction:** Edge profile is the convolution of the material topography with the probe shape.
- **Limitation:** Requires knowledge of the probe shape.

### 7.3 Monte Carlo Trajectory Model

**Model:** Full trajectory simulation for each beam position.
- **Prediction:** Most accurate edge profile, including SE-I and SE-II contributions.
- **Limitation:** Computationally intensive; not suitable for real-time use.

### 7.4 Empirical Gaussian Peak Model

**Model (CD-SEM standard):** The edge profile is modeled as:

$$I(x) = A + B \cdot \text{erf}\left(\frac{x - x_0}{\sigma\sqrt{2}}\right) + C \cdot \exp\left(-\frac{(x - x_0)^2}{2\omega^2}\right)$$

where the error function term represents the material step and the Gaussian term represents the edge brightening peak.

- **Prediction:** Fits measured CD-SEM edge profiles with high accuracy.
- **Limitation:** Empirical — parameters $A$, $B$, $C$, $\sigma$, $\omega$ do not directly correspond to physical quantities.

---

## 8. Which Mechanisms Dominate Semiconductor SEM

| Mechanism | Dominance | Evidence |
|---|---|---|
| **Geometric channeling ($\sec\theta$)** | **Dominant** | Predicts 2–10× enhancement consistent with measurements |
| **SE-II sidewall escape** | **Significant** | Broadens edge peak beyond probe diameter |
| **Probe convolution** | **Significant** | Determines how sharp the edge transition appears |
| **Corner enhancement** | **Important for specific features** | Visible at line ends, contact/via edges |
| **Detector shadowing** | **Important for deep features** | Reduces signal in high-aspect-ratio structures |
| **Material contrast at edges** | **Moderate** | Contributes to profile asymmetry |
| **Bulk SE-II (from substrate)** | **Minor** | Adds background; degrades contrast |

---

## 9. Engineering Summary

### 9.1 Essential Mechanisms for Simulator

| Mechanism | Why Essential |
|---|---|
| $\sec\theta$ yield model | Captures the primary origin of edge brightening |
| Probe convolution | Determines the spatial extent of edge peaks |
| SE-I escape through near-edge surfaces | Determines the shape of the rising edge |

### 9.2 Useful Refinements

| Mechanism | When to Include |
|---|---|
| SE-II sidewall contribution | When modeling signal profile shape for CD extraction |
| Corner enhancement | When simulating line ends or contact holes |
| Detector position/collection function | When imaging deep/high-aspect-ratio features |

### 9.3 Can Be Ignored in First Implementation

| Mechanism | Why |
|---|---|
| SE-III background | Uniform, does not affect edge profile shape |
| Crystallographic channeling | Not relevant for amorphous or polycrystalline semiconductor films |
| Magnetic contrast | Not present in non-magnetic materials |

---

## Sources

- L. Reimer, *Scanning Electron Microscopy: Physics of Image Formation and Microanalysis*, 2nd ed. Springer, 1998.
- J. I. Goldstein, D. E. Newbury, J. R. Michael, et al., *Scanning Electron Microscopy and X-Ray Microanalysis*, 4th ed. Springer, 2017.
- H. Seiler, "Secondary electron emission in the scanning electron microscope," *J. Appl. Phys.*, vol. 54, 1983.
- J. S. Villarrubia, A. E. Vladar, and M. T. Postek, "Scanning electron microscope measurement of width and shape of fabricated nanostructures," *J. Res. NIST*, vol. 109, 2004.
- M. T. Postek and A. E. Vladar, "Critical dimension metrology," in *Handbook of Semiconductor Manufacturing Technology*, CRC Press, 2007.
- R. Shimizu and Z.-J. Ding, "Monte Carlo modelling of electron-solid interactions," *Rep. Prog. Phys.*, vol. 55, 1992.
- D. C. Joy, *Monte Carlo Modeling for Electron Microscopy and Microanalysis*. Oxford University Press, 1995.
- O. C. Wells, *Scanning Electron Microscopy*. McGraw-Hill, 1974.
