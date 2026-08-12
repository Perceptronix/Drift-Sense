# Assumptions and Limitations

**Research Phase:** 2.5
**Document:** 07_assumptions_and_limitations.md
**Date:** 2026-07-30

---

## 1. Introduction

Every model in this specification involves assumptions and simplifications. This document makes them explicit, explains why each is acceptable for the Applied Materials semiconductor localization challenge, and identifies cases where the model may break down.

---

## 2. Physics Assumptions

### 2.1 SE Yield Model

| Assumption | Statement | Justification |
|---|---|---|
| **A1** | SE yield follows $\sec^\gamma\theta$ with $\gamma=1$ | Well-established for $\theta < 70^\circ$ [B1][J7]. Validated by decades of SEM imaging. |
| **A2** | $\sec^\gamma\theta$ applies identically to all materials | Material dependence is captured by $\delta_0$. The exponent $\gamma$ is material-independent to first order. |
| **A3** | Yield saturates (clamps) for $\theta > 70^\circ$ | Prevents unphysical yield values at grazing incidence. The exact form of saturation is not critical because sidewalls of typical semiconductor features are 80–90°, and the peak position (used for CD detection) is determined by geometry, not the exact yield value. |
| **A4** | No azimuthal dependence of SE yield | Valid for TTL detection with rotational symmetry. Neglects small effects from crystal orientation or surface roughness. |

**Breakdown condition:** For extremely high aspect ratios (>10:1), the standard $\sec\theta$ model may not capture shadowing and re-deposition effects. These are rare in standard CD-SEM targets but may affect DRAM deep trench imaging.

### 2.2 BSE Yield Model

| Assumption | Statement | Justification |
|---|---|---|
| **A5** | BSE yield depends only on $Z$ and $E_0$ (not on $\theta$) | BSE angular dependence is captured by the detector model, not the yield magnitude. The total BSE yield does increase with $\theta$ [B1], but for CD-SEM at normal incidence, this effect is small. |
| **A6** | Reimer formula with Joy correction is accurate for $E_0 \geq 0.5$ keV | Published values agree within ±15% for $Z > 10$ at 1 keV. For photoresist ($Z \approx 5$), the formula is extrapolated. |

**Breakdown condition:** Below 500 eV, the Joy correction becomes less accurate. For operation at 300 eV, a lookup table from Monte Carlo simulations should replace the analytical formula.

### 2.3 Escape Depth

| Assumption | Statement | Justification |
|---|---|---|
| **A7** | SE escape probability decays exponentially with depth $P(z) \propto \exp(-z/\Lambda)$ | Standard model [B1][B3]. The characteristic decay length $\Lambda$ is the IMFP at the most probable SE energy (2–5 eV). |
| **A8** | $\Lambda$ is constant per material (independent of $\theta$) | The escape depth is a material property. The angle dependence of SE escape is captured by $\sec\theta$ yield enhancement, not by modifying $\Lambda$. |

### 2.4 Charging

| Assumption | Statement | Justification |
|---|---|---|
| **A9** | Charging reduces SE yield by a constant factor $f_c$ for insulators. | This is the strongest simplification in the model. Full charging physics is self-consistent and time-dependent. The constant factor captures the first-order effect at the cost of losing dynamic behavior (drift, beam deflection). |
| **A10** | Charging does not affect the primary beam position. | Beam deflection from surface potential is neglected. For sub-micron fields and mild charging ($V_{\text{surf}} < 10$ V), this is a reasonable approximation. For strong charging ($V_{\text{surf}} > 50$ V), beam deflection becomes significant. |
| **A11** | Conductors do not charge. | True for metals and heavily doped semiconductors at typical beam currents. Lightly doped Si may charge slightly; the factor $f_c=1.0$ assumes conductive or near-neutral behavior at 1 keV ($\sigma \approx 1.03$). |

**Breakdown condition:** For thick resist (>500 nm) on insulating substrates with strong total yield ($\sigma > 2$), the constant-factor charging model underestimates the complexity of charging effects. For these cases, a more sophisticated model should be considered.

### 2.5 PSF and Blur

| Assumption | Statement | Justification |
|---|---|---|
| **A12** | The probe current density is Gaussian. | Excellent approximation for Schottky FEG sources [B1][B2]. Non-Gaussian tails are negligible for CD-SEM. |
| **A13** | The PSF is the convolution of two Gaussians (probe + escape depth). | Adding Gaussians in quadrature is correct for independent Gaussian distributions. The probe and escape distributions are physically independent. |
| **A14** | The PSF is spatially invariant (same kernel for all pixels) for the probe contribution, but material-dependent for the escape depth contribution. | The probe shape is constant across the field for small FOV. The escape depth varies per material, requiring per-pixel kernel variation. This is the standard approach. |
| **A15** | Defocus, astigmatism, and vibration are negligible. | Their combined contribution to the effective PSF is <0.5 nm for a well-tuned CD-SEM (see Phase 2.4, Document 02). |

### 2.6 Noise

| Assumption | Statement | Justification |
|---|---|---|
| **A16** | Shot noise follows a Poisson distribution. | Fundamental physics of electron detection [B2]. This is not an assumption — it is a fact. |
| **A17** | PMT excess noise can be modeled as a variance scaling factor $F = 1.2$. | Standard model for PMT statistics [B2]. The excess noise factor accounts for the stochastic multiplication process. |
| **A18** | Noise is independent per pixel (no spatial correlation). | True for shot noise and Johnson noise. Some sources (1/f noise, pick-up) have correlation, but these are negligible for CD-SEM. |
| **A19** | Johnson noise, dark current, and quantization noise are negligible. | Their combined contribution is <5% of shot noise at nominal operating conditions (see Phase 2.4, Document 03). |

### 2.7 SE-II Background

| Assumption | Statement | Justification |
|---|---|---|
| **A20** | SE-II background can be modeled as an exponential convolution of BSE yield. | The SE-II signal is generated by BSEs exiting the surface. The exponential kernel approximates the radial distribution of BSE exit points [B1]. |
| **A21** | The SE-II characteristic length $L_{\text{SE-II}}$ is constant per material. | In reality, the SE-II distribution has a more complex shape (sum of exponential + power-law), but the exponential approximation captures the dominant effect (profile tail broadening). |

---

## 3. Geometry Assumptions

| Assumption | Statement | Justification |
|---|---|---|
| **A22** | The geometry is a 2.5D height field (one height per pixel). | This excludes true 3D geometries with overhangs and undercuts. However, most CD-SEM targets (lines, trenches, contacts, vias, FinFETs) are well-represented as height fields. True 3D structures are out of scope. |
| **A23** | The geometry is perfectly aligned with the scan grid. | No rotation between the structure and the scan axes. This is a convenience assumption for the first implementation. Rotation can be added later. |
| **A24** | The structure is static during acquisition (no drift). | Drift is a degradation effect deferred to later phases. The first implementation produces drift-free images. |

---

## 4. Numerical Simplifications

| Simplification | Statement | Justification |
|---|---|---|
| **S1** | Flat-region yield calculation neglects surface roughness. | Surface roughness modifies the effective SE yield [B1], but for the smooth surfaces of semiconductor wafers (RMS roughness < 1 nm), this effect is negligible. |
| **S2** | Material boundaries are sharp (no interdiffusion or grading). | True for most semiconductor structures. Graded interfaces exist in some advanced devices but are out of scope. |
| **S3** | The detector collection efficiency is constant across the field. | Valid for TTL detectors at small FOV (<1 μm). At larger FOV, the collection efficiency varies — this can be added in a future enhancement. |
| **S4** | The amplifier is perfectly linear up to saturation. | Good approximation for modern transimpedance and video amplifiers. Nonlinearity < 0.1% in the linear range. |
| **S5** | The ADC is ideal (no differential nonlinearity, no missing codes). | Modern CD-SEM ADCs have DNL < 0.5 LSB. The ideal ADC assumption is safe. |

---

## 5. Ignored Physics

| Physics | Reason for Ignoring | Impact |
|---|---|---|
| **Electron beam diffraction** | Wavelength <0.1 nm at 1 keV, far below probe diameter | None |
| **Magnetic contrast** | All semiconductor materials are non-magnetic | None |
| **Crystallographic channeling** | Most semiconductor films are amorphous or polycrystalline; minor effect for single-crystal Si | Minor BSE yield modulation |
| **Thermal effects on SE yield** | Temperature changes during imaging are <1°C | None |
| **Pressure/density effects** | Vacuum environment is assumed ideal | None |
| **X-ray generation** | X-rays are not used for imaging (EDS is separate) | None |
| **Auger electron generation** | Signal too weak for grayscale imaging | None |
| **Cathodoluminescence** | Negligible for Si and most semiconductor materials | None |
| **Beam damage / resist shrinkage** | Important for process control but not for image formation physics | Affects CD accuracy in long exposures |
| **Resist contamination (carbon deposition)** | Important for very long exposures but negligible for standard imaging | Affects SE yield over time |

---

## 6. Limitations Summary

| Limitation | Effect | Acceptable? | Mitigation |
|---|---|---|---|
| **Charging is simplified to a constant factor** | Dynamic charging effects (drift, beam deflection) are missing | **Acceptable** for first-order contrast simulation | Add dynamic charging model in Phase D if required |
| **No re-entrant features** | Undercut profiles cannot be represented | **Acceptable** for most CD-SEM targets | Add true 3D geometry in a major revision |
| **No drift** | All images are drift-free | **Acceptable** for ideal image generation | Add drift model in Phase C if required |
| **No crystallographic effects** | Possible minor BSE channeling errors in single-crystal Si | **Acceptable** — channeling contrast is <5% of BSE signal | Add channeling model if Z-contrast accuracy is critical |
| **No surface roughness** | Very fine texture contrast is missing | **Acceptable** for smooth semiconductor surfaces | Add roughness model in Phase D |
| **Approximate SE yields** | Absolute yield values have ±15% uncertainty | **Acceptable** — relative contrast is what matters for CD metrology | Validate against Monte Carlo |
| **No voltage contrast simulation** | Cannot simulate electrical defect detection | **Acceptable** — separate scope | Add VC model if required for defect review simulation |

---

## 7. Validation Philosophy

The simplified models in this specification are acceptable because:

1. **The primary use case is CD metrology** — edge detection, linewidth measurement, profile characterization. These depend on the *position* of intensity features (peaks, thresholds), not their absolute intensity.

2. **CD-SEM operators adjust contrast/brightness** — absolute yield accuracy is secondary to relative contrast between materials and across edges.

3. **The key physical effects are captured** — the $\sec\theta$ topographic contrast, material contrast via $\delta_0$ and $\eta$, finite resolution via Gaussian PSF, and noise via Poisson statistics.

4. **Validation against Monte Carlo** (CASINO simulations) will quantify the remaining model error.

---

## Sources

- [B1] L. Reimer, *Scanning Electron Microscopy: Physics of Image Formation and Microanalysis*, 2nd ed. Springer, 1998.
- [B2] J. I. Goldstein, D. E. Newbury, J. R. Michael, et al., *Scanning Electron Microscopy and X-Ray Microanalysis*, 4th ed. Springer, 2017.
- [B3] R. F. Egerton, *Physical Principles of Electron Microscopy*, 2nd ed. Springer, 2016.
- [B4] D. C. Joy, *Monte Carlo Modeling for Electron Microscopy and Microanalysis*. Oxford University Press, 1995.
- [J7] H. Seiler, "Secondary electron emission in the scanning electron microscope," *J. Appl. Phys.*, vol. 54, 1983.
- [T1] NIST, "Electron Inelastic Mean Free Path Database" (SRD 71).
