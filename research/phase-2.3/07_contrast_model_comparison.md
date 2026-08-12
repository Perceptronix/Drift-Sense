# Contrast Model Comparison

**Research Phase:** 2.3
**Document:** 07_contrast_model_comparison.md
**Date:** 2026-07-30

---

## 1. Introduction

Multiple models have been developed to describe the conversion from sample properties to SEM image intensity. They range from simple geometric approximations to full Monte Carlo simulations. This document compares the major published models, evaluates their accuracy for semiconductor wafer imaging, and recommends which should form the foundation of a synthetic SEM simulator.

---

## 2. Model Classification

The models can be grouped into three categories:

| Category | Approach | Examples |
|---|---|---|
| **Geometric/optical analogies** | Treat SE emission like light reflection | Lambertian model, Phong shading |
| **Physical yield models** | Derive intensity from SE/BSE yield physics | $\sec\theta$ model, combined yield + detector model |
| **Empirical/metrology models** | Fit functions to measured CD-SEM profiles | Error-function + Gaussian, threshold model |
| **Computation-intensive** | Full physics simulation | Monte Carlo, Boltzmann transport |

---

## 3. Geometric/Optical Analogy Models

### 3.1 Lambertian (Diffuse) Model

**Description:** Assumes SEs are emitted like a Lambertian light source — intensity proportional to $\cos\theta$ where $\theta$ is the angle between surface normal and detector direction.

**Mathematical form:**

$$I(\theta) = I_0 \cdot \cos\theta$$

**Predicted behavior:** Surfaces perpendicular to the detector appear brightest. Flat surfaces facing the detector appear bright.

**Accuracy assessment for CD-SEM:**

| Aspect | Assessment |
|---|---|
| **Topographic contrast** | **Poor** — predicts decreasing signal at grazing angles (cosine), opposite to the actual $\sec\theta$ behavior |
| **Edge brightening** | **Fails** — cannot predict bright edges because it predicts the opposite |
| **Material contrast** | **Not included** |
| **Computational cost** | Very low |

**Verdict:** The Lambertian model is physically wrong for SE emission. SEs are *not* light — they are emitted via inelastic scattering with the opposite angular dependence. **This model should not be used for SEM simulation.**

**Why the confusion persists:** The cosine angular *distribution* of emitted SEs (emission pattern) is sometimes confused with the yield *dependence* on surface angle (contrast). The two are different phenomena:
- **Emission distribution:** $\frac{dN}{d\Omega} \propto \cos\phi$ (Lambertian emission pattern) — correct.
- **Contrast:** $\delta(\theta) \propto \sec\theta$ (yield increases with tilt) — correct.
A Lambertian emitter can produce $\sec\theta$ contrast if the total emitted flux increases with tilt even though the angular distribution is cosine.

### 3.2 Phong Shading Model

**Description:** Borrowed from computer graphics, combines diffuse and specular reflection.

**Mathematical form:**

$$I = k_a I_a + k_d I_d \cos\theta + k_s I_s (\cos\alpha)^n$$

**Accuracy:** Poor for SEM. The specular term has no physical basis in SE imaging.

**Verdict:** **Not recommended.**

---

## 4. Physical Yield Models

### 4.1 Simple $\sec\theta$ Model

**Description:** The SE yield is proportional to the secant of the angle between the beam and the surface normal.

**Mathematical form:**

$$I(x,y) = G \cdot I_P \cdot \delta_0(Z) \cdot \sec\theta(x,y)$$

**Accuracy assessment:**

| Aspect | Assessment |
|---|---|
| **Topographic contrast** | **Good** — correctly predicts increased signal at tilted surfaces |
| **Edge brightening** | **Good** — correctly predicts bright edges (high $\theta$) |
| **Material contrast** | **Moderate** — captured via $\delta_0(Z)$, but relies on known yield values |
| **Detector effects** | **Not included** — assumes perfect collection |
| **SE-II contribution** | **Not included** — edge profile underestimates tail width |
| **Computational cost** | Low |

**Verdict:** **Recommended as the base model.** Captures the dominant physics ($\sec\theta$ topographic contrast) at minimal computational cost.

**Limitation:** Requires modification for:
- Detector collection efficiency (especially for side-mounted detectors).
- Material boundaries (discontinuity in $\delta_0(Z)$).
- Very high angles ($\theta > 70^\circ$) where $\sec\theta$ overestimates the yield.

### 4.2 $\sec\theta$ + Detector Response Model

**Description:** Extends the $\sec\theta$ model by including the detector collection function.

**Mathematical form:**

$$I(x,y) = G \cdot I_P \cdot \delta_0(Z) \cdot \sec\theta(x,y) \cdot \eta_{\text{coll}}(x,y) + B$$

where $\eta_{\text{coll}}(x,y)$ is the detector collection efficiency and $B$ is a background term.

**Accuracy assessment:**

| Aspect | Assessment |
|---|---|
| **Topographic contrast** | **Good** — same as $\sec\theta$ model |
| **Edge brightening** | **Good** — correctly positioned |
| **Detector asymmetry** | **Good** — $\eta_{\text{coll}}$ captures collection effects |
| **Shadowing** | **Moderate** — if $\eta_{\text{coll}}$ includes line-of-sight |
| **SE-II contribution** | **Not included** |
| **Computational cost** | Low to moderate |

**Verdict:** **Recommended for synthetic SEM image generation.** The additional complexity of the detector model is justified by the improved realism, especially for off-axis features.

### 4.3 Combined SE/BSE Model

**Description:** Models both SE and BSE signals with distinct mechanisms.

**Mathematical form:**

$$I(x,y) = G_{\text{SE}} \cdot \delta_0(Z) \cdot \sec\theta \cdot \eta_{\text{coll}}^{\text{SE}} + G_{\text{BSE}} \cdot \eta(Z) \cdot \eta_{\text{coll}}^{\text{BSE}} + B$$

**Accuracy assessment:**

| Aspect | Assessment |
|---|---|
| **Topographic contrast** | **Good** (SE channel) |
| **Material contrast** | **Better** — BSE channel adds Z-contrast |
| **Edge brightening** | **Good** (SE channel) |
| **Voltage contrast** | **Possible** (if BSE channel includes VC model) |
| **Computational cost** | Moderate |

**Verdict:** **Recommended for multi-channel simulation.** Particularly useful when modeling materials with strong Z-contrast (W vs. SiO₂, Cu vs. Si).

---

## 5. Empirical CD-SEM Metrology Models

### 5.1 Error-Function + Gaussian Peak Model

**Description:** Represents the CD-SEM line profile as the sum of error functions (for material steps) and Gaussian peaks (for edge brightening).

**Mathematical form (Villarrubia et al., 2004):**

$$I(x) = A + \sum_{k} \left[ B_k \cdot \text{erf}\left(\frac{x - x_k}{\sigma_k \sqrt{2}}\right) + C_k \cdot \exp\left(-\frac{(x - x_k)^2}{2\omega_k^2}\right) \right]$$

where $A$ is the background, $x_k$ are edge positions, $B_k$ and $\sigma_k$ describe material step contrast, and $C_k$ and $\omega_k$ describe edge brightening.

**Accuracy assessment:**

| Aspect | Assessment |
|---|---|
| **Profile fitting** | **Excellent** — fits measured profiles with high accuracy |
| **Edge detection** | **Excellent** — peak centers correlate well with physical edges |
| **Physical interpretability** | **Limited** — parameters are empirical, not directly physical |
| **Generalizability** | **Limited** — requires re-fitting for each structure type |
| **Computational cost** | Low |

**Verdict:** **Recommended for CD metrology algorithm development.** This is the standard model used in CD-SEM data analysis. However, it is not suitable as a forward simulator of image formation because it does not generate images from first principles.

### 5.2 Threshold Model

**Description:** The simplest model for edge detection: the edge is located at the position where the signal crosses a specified threshold (e.g., 50% of the peak height).

**Mathematical form:**

$$x_{\text{edge}} = \text{arg}\{I(x) = T\}$$

where $T$ is the threshold level (typically 20–80% of the maximum signal between background and peak).

**Accuracy assessment:**

| Aspect | Assessment |
|---|---|
| **Simplicity** | Highest — industry standard for edge detection |
| **Accuracy for symmetric profiles** | Moderate |
| **Accuracy for asymmetric profiles** | Poor (threshold-dependent bias) |
| **Physical basis** | Weak |

**Verdict:** **Useful as a reference** but not suitable as a forward model.

### 5.3 Model-Based Metrology (MBM)

**Description:** Uses a physics-based forward model (often Monte Carlo) to build a library of expected profiles, then matches measured profiles against the library.

**Mathematical form:** Inverse problem:

$$\hat{p} = \arg\min_p \| I_{\text{meas}} - I_{\text{sim}}(p) \|^2$$

where $p$ are the structural parameters (CD, sidewall angle, height, etc.).

**Accuracy assessment:**

| Aspect | Assessment |
|---|---|
| **Accuracy** | Best (if the forward model is accurate) |
| **Computational cost** | Very high (requires library precomputation) |
| **Robustness** | Good (if the structure is in the library) |

**Verdict:** **Best approach for accurate CD extraction** but not relevant for the forward renderer itself.

---

## 6. Monte Carlo Models

### 6.1 Full MC Trajectory Simulation

**Description:** Simulates each primary electron's trajectory as a random walk through the solid, tracking all scattering events and emitted electrons (CASINO, PENELOPE, Geant4).

**Accuracy assessment:**

| Aspect | Assessment |
|---|---|
| **Physical accuracy** | **Best** — captures all relevant physics |
| **Material flexibility** | **Best** — can handle arbitrary compositions |
| **Geometric flexibility** | **Good** — can handle complex 3D geometries |
| **Computational cost** | **Very high** — minutes to hours per image |
| **Real-time capability** | **None** |

**Verdict:** **Ideal as a ground-truth reference** for developing and validating simpler models. **Not suitable** for real-time or production rendering.

### 6.2 Hybrid MC + Analytical Models

**Description:** Uses MC to precompute key parameters (yield, angular distributions, SE-II spread) and analytical functions for real-time rendering.

**Typical approach:**
1. MC precomputation: For a given material and energy, compute $\delta_0$, $\eta$, angular dependence, SE-II range.
2. Real-time rendering: Use analytical $\sec\theta$ + detector model with MC-derived parameters.

**Verdict:** **Recommended approach** for the synthetic SEM simulator. Balances physical accuracy with computational feasibility.

---

## 7. Model Comparison Summary Table

| Model | Type | Topographic Contrast | Material Contrast | Edge Profile | Detector Effects | Speed | Recommended for Simulator? |
|---|---|---|---|---|---|---|---|
| **Lambertian** | Geometric | **Wrong** (cosine) | No | No | No | Very fast | **No** |
| **Phong shading** | Geometric | **Wrong** | No | No | No | Fast | **No** |
| **Simple $\sec\theta$** | Physical | **Good** | Moderate (via $\delta_0$) | Good (edges) | No | Fast | **Yes — base model** |
| **$\sec\theta$ + detector** | Physical | **Good** | Moderate | Good | **Good** | Fast | **Yes — recommended** |
| **Combined SE/BSE** | Physical | **Good** | **Good** | Good | **Good** | Moderate | **Yes — for realism** |
| **Erf + Gaussian** | Empirical | N/A (fits profile) | N/A | **Excellent** | N/A | Fast | **For metrology only** |
| **Threshold model** | Empirical | N/A | N/A | Moderate | N/A | Very fast | **For edge detection only** |
| **Monte Carlo (full)** | First-principles | **Best** | **Best** | **Best** | **Best** | Very slow | **Ground truth only** |
| **Hybrid MC + analytical** | Mixed | **Good** | **Good** | **Good** | **Good** | Moderate | **Yes — recommended approach** |

---

## 8. Recommendation for Synthetic SEM Simulator

### 8.1 Primary Recommendation: $\sec\theta$ + Detector + Combined SE/BSE

The recommended forward model is:

$$I(x,y) = G \cdot \left[ \delta_0(Z) \cdot \sec\theta(x,y) \cdot \eta_{\text{coll}}(x,y) \cdot I_P \tau + \eta(Z) \cdot \eta_{\text{coll,BSE}}(x,y) \cdot I_P \tau \right] + I_{\text{off}}$$

**Rationale:**
- Captures the dominant physics: topographic contrast ($\sec\theta$), material contrast ($\delta_0$, $\eta$), and collection effects ($\eta_{\text{coll}}$).
- Computationally efficient — can be evaluated per pixel with O(1) cost per material.
- Can be upgraded later to include SE-II (as a convolution term) and probe convolution.

### 8.2 Validation Strategy

1. **Compare against Monte Carlo** for simple structures (line/space, isolated line, contact hole).
2. **Tune $\sec\theta$ behavior** at high angles using MC results (apply correction for $\theta > 70^\circ$).
3. **Validate edge profile widths** — compare simulated vs. MC for probe diameter and SE-II contributions.
4. **Calibrate material parameters** ($\delta_0$, $\eta$) against literature values.

### 8.3 Implementation Priority

| Component | Priority | Notes |
|---|---|---|
| $\sec\theta$ yield | P0 (essential) | Core of the model |
| Material $\delta_0$, $\eta$ library | P0 (essential) | Required for material contrast |
| Probe convolution (Gaussian) | P0 (essential) | Required for realistic edge width |
| Detector collection function | P1 (important) | Adds asymmetry realism |
| SE-II background model | P1 (important) | Broadens edge tails correctly |
| BSE + voltage contrast | P2 (enhancement) | Adds compositional and VC imaging |

---

## Sources

- J. S. Villarrubia, A. E. Vladar, and M. T. Postek, "Scanning electron microscope measurement of width and shape of fabricated nanostructures," *J. Res. NIST*, vol. 109, 2004.
- L. Reimer, *Scanning Electron Microscopy: Physics of Image Formation and Microanalysis*, 2nd ed. Springer, 1998.
- J. I. Goldstein, D. E. Newbury, J. R. Michael, et al., *Scanning Electron Microscopy and X-Ray Microanalysis*, 4th ed. Springer, 2017.
- H. Seiler, "Secondary electron emission in the scanning electron microscope," *J. Appl. Phys.*, vol. 54, 1983.
- D. C. Joy, *Monte Carlo Modeling for Electron Microscopy and Microanalysis*. Oxford University Press, 1995.
- R. Shimizu and Z.-J. Ding, "Monte Carlo modelling of electron-solid interactions," *Rep. Prog. Phys.*, vol. 55, 1992.
- D. Drouin, A. R. Couture, D. Joly, et al., "CASINO V2.42," *Scanning*, vol. 29, 2007.
- C. N. Archie, "Critical dimension metrology," *AIP Conf. Proc.*, vol. 788, 2005.
- M. T. Postek and A. E. Vladar, "Critical dimension metrology," in *Handbook of Semiconductor Manufacturing Technology*, CRC Press, 2007.
- A. E. Vladar, M. T. Postek, and R. Vane, "CD-SEM and the 45-nm node," *Proc. SPIE*, vol. 6518, 2007.
