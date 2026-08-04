# Resolution and Blur

**Research Phase:** 2.4
**Document:** 02_resolution_and_blur.md
**Date:** 2026-07-30

---

## 1. Introduction

Resolution in SEM is the ability to distinguish closely spaced features as separate. Blur — the loss of high-frequency spatial information — is the primary factor limiting resolution. This document examines every mechanism that contributes to blur in SEM imaging, with emphasis on CD-SEM operating conditions.

**Fact:** The final SEM image is the convolution of the ideal sample signal with a point spread function (PSF) that combines contributions from the probe, the interaction physics, the detector, and instrumental instabilities:

$$I_{\text{measured}}(x,y) = I_{\text{ideal}}(x,y) * \text{PSF}(x,y) + \text{noise}$$

where $*$ denotes convolution.

---

## 2. The Point Spread Function (PSF)

### 2.1 Definition for SEM

In SEM, the PSF is the spatial distribution of the detected signal produced by an idealized point feature (a sharp edge, a single atomic column, a quantum dot). The PSF is not purely optical — it includes contributions from electron scattering in the sample and the detection process.

### 2.2 PSF Components

The total PSF is the sum (in quadrature for Gaussian components) of multiple contributions:

$$\text{PSF}_{\text{total}} = \text{PSF}_{\text{probe}} * \text{PSF}_{\text{aberr}} * \text{PSF}_{\text{sample}} * \text{PSF}_{\text{detector}} * \text{PSF}_{\text{vibration}}$$

For CD-SEM operating conditions, the contributions are:

| Component | Physical Origin | Shape | Typical Width (FWHM) | Notes |
|---|---|---|---|---|
| **Gaussian probe** | Demagnified source image | Gaussian | 0.5–2.0 nm | Dominant term |
| **Lens aberrations** | Spherical ($C_s$), Chromatic ($C_c$) | Disk (spherical), energy-dependent (chromatic) | 0.1–0.5 nm at optimum aperture | Minimized by aperture selection |
| **Diffraction** | Wave nature of electron | Airy pattern | <0.1 nm at 1 keV | Negligible for SEM (unlike TEM) |
| **Beam broadening in sample** | Elastic scattering within sample | Approximately exponential tail | 0–3 nm (SE-I), 10–100 nm (SE-II) | Energy, Z-dependent |
| **Signal delocalization (SE)** | SE generation and escape region | Exponential decay | 0.5–2 nm (metals), 2–20 nm (insulators) | Materials-dependent |
| **Detector PSF** | Finite detector geometry, collection efficiency | Gaussian or top-hat | 0.1–0.5 nm | Minor for TTL detectors |
| **Vibration** | Mechanical/environmental | Gaussian | 0.1–0.3 nm | Tool-dependent |
| **Magnetic interference** | AC magnetic fields | Periodic displacement | 0.1–0.5 nm | Frequency-dependent |

### 2.3 The Effective PSF for CD-SEM

**Fact:** For a well-tuned CD-SEM operating at 1 keV, the total PSF is dominated by two contributions:

1. **The Gaussian probe** (FWHM 0.5–1.5 nm) — determines the sharpness of the edge rise.
2. **Beam broadening + SE delocalization** (effective width 1–3 nm) — broadens the SE-I edge profile and creates the SE-II tail.

The effective resolution (10–90% edge rise distance) is typically 1.5–3 nm for state-of-the-art CD-SEM.

---

## 3. The Probe Diameter and Shape

### 3.1 Probe Formation

The probe is the demagnified image of the electron source at the sample plane. Its size is determined by:

$$d_p^2 = d_g^2 + d_s^2 + d_c^2 + d_d^2$$

where:
- $d_g$ = Gaussian image of the source (demagnified source diameter)
- $d_s$ = Spherical aberration disk: $0.5 C_s \alpha^3$
- $d_c$ = Chromatic aberration disk: $C_c (\Delta E / E) \alpha$
- $d_d$ = Diffraction disk: $0.61 \lambda / \alpha$

**Typical values for CD-SEM (Schottky FEG, 1 keV, 10 mrad convergence angle):**

| Term | Value (nm) |
|---|---|
| Gaussian $d_g$ | 0.3–0.8 |
| Spherical $d_s$ | 0.15–0.3 |
| Chromatic $d_c$ | 0.2–0.4 |
| Diffraction $d_d$ | 0.05–0.1 |
| **Total $d_p$** | **0.5–1.2** |

**Inference:** At CD-SEM energies (500 eV–1.5 keV), chromatic aberration is the dominant aberration term. The energy spread $\Delta E$ of the Schottky FEG (0.3–1.0 eV) determines the chromatic disk size.

### 3.2 Probe Current Density Distribution

The probe is not a sharp-edged disk. It has a current density distribution that is approximately Gaussian:

$$J(r) = \frac{I_P}{2\pi \sigma^2} \exp\left(-\frac{r^2}{2\sigma^2}\right)$$

where $\sigma = d_p / 2.355$ (for Gaussian approximation) and $I_P$ is the total probe current.

**Fact:** For modern CD-SEMs with Schottky FEG sources, the probe current density is well-approximated by a Gaussian distribution. Small deviations from Gaussian (non-Gaussian tails) can affect high-contrast edge profiles but are generally negligible for semiconductor metrology.

### 3.3 Defocus

When the sample is not exactly at the focal plane of the objective lens, the probe diameter increases as:

$$d(z) = \sqrt{d_0^2 + (\alpha \cdot \Delta z)^2}$$

where $d_0$ is the in-focus probe diameter, $\alpha$ is the convergence semi-angle, and $\Delta z$ is the defocus distance.

| Defocus $\Delta z$ | Increase in $d_p$ (for $\alpha = 10$ mrad) |
|---|---|
| 0 nm (in focus) | 0% |
| 100 nm | ~8% |
| 500 nm | ~40% |
| 1 μm | ~80% |

**Inference:** In CD-SEM operation, the autofocus routine typically maintains focus to within ±100 nm, so defocus contributes <10% increase to the probe diameter — much less than the variability from other sources.

---

## 4. Lens Aberrations

### 4.1 Spherical Aberration ($C_s$)

**Physical origin:** Outer zones of the lens focus more strongly than inner zones. Electrons passing through the lens at larger radii are over-focused relative to paraxial electrons.

**Disk diameter:** $d_s = \frac{1}{2} C_s \alpha^3$

**Typical $C_s$ for CD-SEM objective lenses:** 1–5 mm (semi-in-lens or immersion design).

**Inference:** Spherical aberration scales as $\alpha^3$. The convergence angle $\alpha$ can be reduced to minimize $d_s$, but this also reduces probe current (since $I_P \propto \alpha^2$) — a fundamental trade-off.

### 4.2 Chromatic Aberration ($C_c$)

**Physical origin:** Electrons with different energies (from the source energy spread $\Delta E$) are focused at different axial positions. Lower-energy electrons are focused more strongly.

**Disk diameter:** $d_c = C_c \frac{\Delta E}{E} \alpha$

**Typical $C_c$ for CD-SEM objective lenses:** 1–4 mm.

**Energy spread $\Delta E$:**
- Schottky FEG: 0.3–1.0 eV
- Cold FEG: 0.2–0.5 eV
- LaB₆: 1–2 eV

**Inference:** Chromatic aberration is the dominant aberration at low voltages (<2 keV) because it scales as $\Delta E / E$. At 500 eV with a Schottky FEG ($\Delta E \approx 0.5$ eV), the chromatic term is 2–4× larger than at 5 keV. This is why ultra-high resolution at low kV is challenging.

### 4.3 Astigmatism

**Physical origin:** Non-rotationally symmetric lens fields (due to mechanical imperfections or contamination aperture) cause the beam to focus at different axial positions in the X and Y directions. The beam becomes elliptical rather than circular.

**Correction:** A stigmator (pair of quadrupole lenses) applies a compensating elliptical field. In modern CD-SEMs, astigmatism is corrected automatically.

**Residual astigmatism after correction:** <0.1 nm (negligible for CD-SEM).

### 4.4 Diffraction

The wave nature of electrons imposes a fundamental limit on the minimum probe diameter:

$$d_d = \frac{0.61 \lambda}{\alpha}$$

where $\lambda$ (nm) = $1.226 / \sqrt{E\text{ (eV)}}$.

| Energy | $\lambda$ | $d_d$ for $\alpha = 10$ mrad |
|---|---|---|
| 500 eV | 0.054 nm | 0.003 nm |
| 1 keV | 0.039 nm | 0.002 nm |
| 10 keV | 0.012 nm | <0.001 nm |

**Fact:** Diffraction is **negligible** in SEM (unlike TEM) because the electron wavelength is orders of magnitude smaller than the probe diameter. The diffraction term only becomes comparable to the probe diameter at convergence angles below ~0.1 mrad, which are not used in practice.

---

## 5. Beam Broadening in the Sample

### 5.1 Elastic Scattering Broadening

As the primary beam penetrates the sample, elastic scattering causes the beam to spread laterally. This broadening affects:

- **SE-I:** Generated along the primary trajectory within the escape depth. The broadening within the top 1–5 nm is limited (~0.5–2 nm).
- **SE-II:** Generated by BSEs re-emerging from the surface. These BSEs can emerge up to ~1 μm from the beam impact point, producing a low-intensity background halo.

### 5.2 The SE-I Resolution Limit

The SE-I resolution is determined by the volume within which SEs can be generated and still escape:

$$R_{\text{SE-I}} \approx \sqrt{d_p^2 + (2\Lambda_{\text{escape}})^2}$$

where $\Lambda_{\text{escape}}$ is the SE escape depth.

| Material | $\Lambda_{\text{escape}}$ | SE-I Resolution Contribution |
|---|---|---|
| W | 0.5 nm | 1.0 nm |
| Cu | 1 nm | 2.0 nm |
| Si | 2 nm | 4.0 nm |
| SiO₂ | 10 nm | 20 nm |

**Inference:** On insulating materials (SiO₂, photoresist), the SE escape depth is the dominant resolution-limiting factor — not the probe diameter. On metals, the probe diameter dominates.

### 5.3 SE-II Contribution

The SE-II signal is generated by BSEs exiting the surface over a region with diameter approximately equal to the BSE escape radius (~0.3× the interaction radius). This adds a long-range background to the image:

$$I_{\text{SE-II}}(r) \propto I_P \eta \cdot \exp(-r / r_{\text{SE-II}})$$

where $r_{\text{SE-II}}$ is the characteristic decay length (10–500 nm depending on beam energy and material).

---

## 6. Detector PSF

### 6.1 TTL Detector Response

In through-the-lens detection, the detector collects SEs that follow magnetic field lines. The finite acceptance angle and collection efficiency create a detector PSF:

| Detector Type | Detector PSF (FWHM) | Significance |
|---|---|---|
| TTL SE (in-lens) | 0.1–0.5 nm | Minor — well-matched to probe |
| Annular BSE (solid-state) | 1–10 nm | Moderate — limits BSE resolution |
| E-T (side-mounted) | 1–5 nm | Minor for axial collection |

### 6.2 Finite Detector Aperture

The detector's finite acceptance aperture creates a smoothing effect. For TTL detectors, the acceptance angle is large (~50°–70°), so this effect is minimal.

---

## 7. Vibration and Environmental Factors

### 7.1 Mechanical Vibration

Building vibration, vacuum pumps, cooling fans, and stage motion all contribute to mechanical displacement of the beam relative to the sample:

- **Typical amplitude (well-designed CD-SEM lab):** 0.1–0.3 nm peak-to-peak.
- **Typical amplitude (marginal environment):** 1–5 nm peak-to-peak.
- **Effect:** Gaussian blur with standard deviation approximately equal to RMS vibration amplitude.

### 7.2 Magnetic Interference

AC magnetic fields from power lines (50/60 Hz) and nearby equipment deflect the beam:

- **Effect:** Periodic beam displacement at the interference frequency.
- **Magnitude:** 0.1–0.5 nm in well-shielded tools; can reach 10+ nm in poorly shielded environments.
- **Appearance:** Edge waviness or double images in severe cases.

### 7.3 Acoustic Noise

Sound waves can cause mechanical vibration of column components or scan coils:

- **Typically negligible** in CD-SEM cleanroom environments (<55 dB at column height).

---

## 8. Summary: Blur Budget for CD-SEM

| Blur Source | Typical Value (nm FWHM) | Mitigation |
|---|---|---|
| **Gaussian probe diameter** | 0.8–1.5 | Source choice, demagnification |
| **Spherical aberration** | 0.2–0.3 | Aperture selection |
| **Chromatic aberration** | 0.2–0.4 | Energy filter, high-voltage stability |
| **Beam broadening (SE-I)** | 0.5–2 (material-dependent) | Low energy, thin features |
| **SE-II tail** | 10–500 (length constant) | TTL detector rejects partial SE-II |
| **Defocus** | 0.1–0.3 | Autofocus |
| **Astigmatism** | 0–0.1 | Autostigmation |
| **Vibration** | 0.1–0.3 | Environmental isolation |
| **Diffraction** | <0.1 | — |

**Effective total resolution (10–90% edge rise):**
- Best case (low-kV, metal): **1.5–2.5 nm**
- Typical (1 keV, Si/resist): **2–4 nm**
- Worst case (low-kV, thick insulator): **5–20 nm**

---

## 9. Engineering Conclusions

| Mechanism | Essential for Simulator? | Justification |
|---|---|---|
| **Gaussian probe PSF** | **Essential** | Determines edge profile width |
| **Probe diameter ($d_p$)** | **Essential** | Single most important resolution parameter |
| **Beam broadening (SE-I)** | **Essential** | Material-dependent resolution limit |
| **SE-II (long-range blur)** | **Recommended** | Adds profile tail; affects CD bias |
| **Defocus** | **Optional** | Small effect if autofocus assumed |
| **Astigmatism** | **Optional** | Negligible in modern tools |
| **Vibration** | **Optional** | Tool-dependent; can be modeled as added Gaussian blur |
| **Diffraction** | **Can ignore** | Negligible in SEM |
| **Magnetic interference** | **Can ignore** | Minor in well-shielded tools |

---

## Sources

- L. Reimer, *Scanning Electron Microscopy: Physics of Image Formation and Microanalysis*, 2nd ed. Springer, 1998.
- J. I. Goldstein, D. E. Newbury, J. R. Michael, et al., *Scanning Electron Microscopy and X-Ray Microanalysis*, 4th ed. Springer, 2017.
- R. F. Egerton, *Physical Principles of Electron Microscopy*, 2nd ed. Springer, 2016.
- D. C. Joy, *Monte Carlo Modeling for Electron Microscopy and Microanalysis*. Oxford University Press, 1995.
- J. S. Villarrubia, A. E. Vladar, and M. T. Postek, "Scanning electron microscope measurement of width and shape of fabricated nanostructures," *J. Res. NIST*, vol. 109, 2004.
- M. T. Postek and A. E. Vladar, "Critical dimension metrology," in *Handbook of Semiconductor Manufacturing Technology*, CRC Press, 2007.
- C. N. Archie, "Critical dimension metrology," *AIP Conf. Proc.*, vol. 788, 2005.
- Wikipedia, "Point Spread Function," accessed July 2026.
