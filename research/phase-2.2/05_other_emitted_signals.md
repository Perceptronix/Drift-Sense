# Other Emitted Signals

**Research Phase:** 2.2
**Document:** 05_other_emitted_signals.md
**Date:** 2026-07-30

---

## 1. Introduction

While SE and BSE are the primary signals for SEM imaging, the electron–sample interaction generates several additional signals. Each carries specific information about the sample and is useful for particular applications. This document characterizes each signal and evaluates its relevance to semiconductor inspection and SEM simulation.

---

## 2. Auger Electrons

### 2.1 Physical Origin

Auger electrons are emitted during the relaxation of an ionized atom. When a primary electron ejects an inner-shell electron, the resulting vacancy can be filled by an electron from a higher shell. The energy released by this transition can eject a second electron from a higher shell — this ejected electron is an **Auger electron**.

**Fact:** Auger emission and X-ray fluorescence are competing relaxation processes. The probability of Auger emission is highest for low-Z elements and for inner shells with low binding energies.

### 2.2 Energy and Escape Depth

| Property | Value |
|---|---|
| Energy range | 50 eV – ~2 keV |
| Escape depth | 0.5–3 nm (similar to SEs) |
| Yield | Low ($10^{-5}$–$10^{-3}$ per incident electron) |

### 2.3 Information Content

- **Elemental identification:** Auger electron energies are characteristic of the emitting element, enabling surface composition analysis (Auger Electron Spectroscopy, AES).
- **Extreme surface sensitivity:** The short escape depth (0.5–3 nm) makes AES the most surface-sensitive of all SEM signals for elemental analysis.

### 2.4 Relevance to Semiconductor Inspection

| Use Case | Relevance | Notes |
|---|---|---|
| Surface contamination detection | Moderate | Can identify thin contaminant layers |
| Thin film composition | Low | EDS is preferred for thicker films |
| CD metrology | **None** | Signal is too weak for imaging |

### 2.5 Engineering Conclusion

**Recommendation:** Auger electron emission can be **safely ignored** for SEM imaging simulation in the context of semiconductor inspection. The signal is too weak to contribute to grayscale image formation under typical CD-SEM conditions. It is relevant only for dedicated surface analysis (AES).

---

## 3. Characteristic X-Rays

### 3.1 Physical Origin

When an inner-shell vacancy is filled by an outer-shell electron, the energy difference can be released as an X-ray photon. The X-ray energy equals the difference between the binding energies of the two shells involved:

$$E_{X\text{-ray}} = E_B(\text{shell}_1) - E_B(\text{shell}_2)$$

These energies are characteristic of the emitting element — hence "characteristic X-rays."

### 3.2 Naming Convention

X-ray lines are named according to the shell being filled and the origin of the filling electron:

| Line | Transition | Typical Energy (Si) | Typical Energy (Cu) |
|---|---|---|---|
| Kα₁ | L₃ → K | 1.74 keV | 8.05 keV |
| Kβ₁ | M₃ → K | 1.84 keV | 8.90 keV |
| Lα₁ | M₅ → L₃ | — | 0.93 keV |
| Lβ₁ | M₄ → L₃ | — | 0.95 keV |

### 3.3 Energy and Escape Depth

| Property | Value |
|---|---|
| Energy range | 0.1–20 keV (for elements relevant to semiconductors) |
| Escape depth | 0.1–5 μm (limited by absorption in the sample) |
| Yield (fluorescence yield) | 0.01–0.50 depending on Z |

### 3.4 Information Content

- **Unambiguous elemental identification:** Each element has a unique set of characteristic X-ray lines.
- **Quantitative composition:** The X-ray intensity is proportional to the elemental concentration (after matrix corrections).
- **Thin film thickness:** The relative intensity of substrate and film lines can indicate film thickness.

### 3.5 Relevance to Semiconductor Inspection

| Use Case | Relevance | Notes |
|---|---|---|
| Elemental contamination | High (EDS) | Identification of particles and residues |
| Thin film composition | High (EDS) | Quantification of film stoichiometry |
| CD metrology | **None** | X-rays are not used for CD measurement |
| Defect review | Moderate | EDS is a standard add-on for elemental defect identification |

### 3.6 Engineering Conclusion

**Recommendation:** Characteristic X-ray generation can be **safely ignored** for SEM imaging simulation in this project. The spatial resolution of X-ray signals (micrometer-scale) is far too coarse to contribute to nanometer-scale image formation. X-rays are relevant only for EDS elemental analysis, which is a separate analytical mode.

---

## 4. Bremsstrahlung (Continuum) X-Rays

### 4.1 Physical Origin

Bremsstrahlung ("braking radiation") is emitted when a primary electron is decelerated by the Coulomb field of a nucleus. The energy loss appears as a photon with energy up to the primary beam energy $E_0$.

### 4.2 Characteristics

| Property | Value |
|---|---|
| Energy range | 0 – $E_0$ (continuous spectrum) |
| Angular distribution | Forward-peaked at high energies |
| Intensity | Approximately proportional to $Z^2$ |

### 4.3 Relevance

- **EDS background:** Bremsstrahlung forms the background continuum in EDS spectra, limiting detection sensitivity.
- **No imaging value:** The continuous spectrum carries no elemental information.

### 4.4 Engineering Conclusion

**Recommendation:** Bremsstrahlung can be **safely ignored** for SEM imaging simulation. It is relevant only for EDS spectral analysis.

---

## 5. Cathodoluminescence (CL)

### 5.1 Physical Origin

Cathodoluminescence is the emission of photons (visible, UV, or IR) from a material excited by the electron beam. In semiconductors and insulators, the electron beam creates electron-hole pairs across the band gap. When these recombine radiatively, photons are emitted with energy approximately equal to the band gap.

### 5.2 Characteristics

| Property | Value |
|---|---|
| Energy range | 1–5 eV (near-IR to UV) |
| Escape depth | Depends on absorption; typically hundreds of nm to μm |
| Yield | Low; typically $10^{-5}$–$10^{-3}$ photons per incident electron |

### 5.3 Information Content

- **Band gap energy:** CL wavelength indicates the band gap of the material.
- **Defect states:** CL peaks at sub-band-gap energies indicate defect or impurity levels.
- **Crystal quality:** CL intensity is affected by non-radiative recombination at defects.

### 5.4 Relevance to Semiconductor Inspection

| Use Case | Relevance | Notes |
|---|---|---|
| Wide band gap materials (GaN, SiC) | Moderate | CL reveals defects in power semiconductors |
| Silicon | **None** | Si has low CL efficiency (indirect band gap) |
| CD metrology | **None** | CL lacks spatial resolution for sub-μm features |

### 5.5 Engineering Conclusion

**Recommendation:** Cathodoluminescence can be **safely ignored** for this simulation project. It is relevant only for specialized defect analysis in optoelectronic materials, not for standard semiconductor CD-SEM inspection.

---

## 6. Specimen Current (Absorbed Current)

### 6.1 Physical Origin

The specimen current (also called absorbed current or beam current) is the net current flowing from the sample to ground. It represents the portion of the primary beam current that is not emitted as SE or BSE:

$$I_{\text{specimen}} = I_P - I_{\text{SE}} - I_{\text{BSE}}$$

### 6.2 Characteristics

| Property | Value |
|---|---|
| Magnitude | Typically 50–95% of $I_P$ (varies with material) |
| Polarity | Negative (electrons flowing to ground) |
| Sign convention | $I_{\text{specimen}} = I_P(1 - \sigma)$ where $\sigma = \delta + \eta$ |

### 6.3 Information Content

- **Complementary to SE/BSE:** Specimen current is highest when SE + BSE emission is lowest.
- **Charging indicator:** A drifting specimen current indicates charging of the sample.
- **Material contrast:** The specimen current varies inversely with SE/BSE yield, providing an inverted contrast mechanism.

### 6.4 Relevance to Semiconductor Inspection

| Use Case | Relevance | Notes |
|---|---|---|
| Charge monitoring | Moderate | Useful for detecting charging conditions |
| Imaging | Low | Specimen current imaging has worse SNR and resolution than SE/BSE |
| CD metrology | **None** | Not used for dimensional measurement |

### 6.5 Engineering Conclusion

**Recommendation:** Specimen current can be **safely ignored** for the primary imaging simulation. However, understanding the specimen current is useful background because it relates to sample charging (to be addressed in a later phase).

---

## 7. Transmitted Electrons

### 7.1 Physical Origin

For thin samples, some primary electrons pass completely through the sample (transmitted electrons). While SEM generally uses bulk samples, transmitted electrons can be detected in STEM-in-SEM mode.

### 7.2 Relevance to Semiconductor Inspection

| Use Case | Relevance | Notes |
|---|---|---|
| Bulk wafers | **None** | Wafers are too thick for transmission |
| Thin lamella (FIB-prepared) | Moderate | STEM-in-SEM is used for thin sections |
| CD metrology | **None** | Not applicable |

### 7.3 Engineering Conclusion

**Recommendation:** Transmitted electrons can be **safely ignored** for this simulation project, which assumes bulk semiconductor samples.

---

## 8. Summary Table: All Signals

| Signal | Energy | Escape Depth | Information | Relevant for Semiconductor SEM? | Include in Simulator? |
|---|---|---|---|---|---|
| **SE‑I** | 0–50 eV | 0–2 nm | Highest-res topography | **Yes — primary** | **Essential** |
| **SE‑II** | 0–50 eV | 0–20 nm | Moderate-res topography | **Yes — background** | **Useful** |
| **BSE** | 50 eV – $E_0$ | 0.1–1 μm | Composition (Z) | **Yes — secondary** | **Essential** |
| Auger | 50 eV – 2 keV | 0.5–3 nm | Surface composition | No — too weak | Ignore |
| Char. X-ray | 0.1–20 keV | 0.1–5 μm | Elemental ID | No — EDS only | Ignore |
| Bremsstrahlung | 0 – $E_0$ | Bulk | None | No — EDS background | Ignore |
| Cathodoluminescence | 1–5 eV | 0.1–5 μm | Band gap, defects | No — Si is non-CL | Ignore |
| Specimen current | DC current | Full volume | Complement to SE/BSE | No — low resolution | Ignore |
| Transmitted | $E_0$ - loss | Through thin sample | Internal structure | No — wafer is thick | Ignore |

---

## 9. Conclusion

For the purpose of SEM imaging simulation in semiconductor inspection, **only three signals need to be modeled:**

1. **SE-I** (primary information carrier — highest resolution)
2. **SE-II** (resolution-degrading background)
3. **BSE** (compositional signal, secondary information carrier)

All other signals (Auger, X-rays, CL, specimen current, transmitted electrons) can be safely ignored because they:
- Do not contribute to the grayscale image formation under typical CD-SEM conditions.
- Require specialized detectors not used for standard imaging.
- Have spatial resolutions too coarse to matter at the nanometer scale.
- Have signal strengths too weak to affect the pixel values.

---

## Sources

- L. Reimer, *Scanning Electron Microscopy: Physics of Image Formation and Microanalysis*, 2nd ed. Springer, 1998.
- J. I. Goldstein, D. E. Newbury, J. R. Michael, et al., *Scanning Electron Microscopy and X-Ray Microanalysis*, 4th ed. Springer, 2017.
- R. F. Egerton, *Physical Principles of Electron Microscopy*, 2nd ed. Springer, 2016.
- D. C. Joy, *Monte Carlo Modeling for Electron Microscopy and Microanalysis*. Oxford University Press, 1995.
- H. Seiler, "Secondary electron emission in the scanning electron microscope," *J. Appl. Phys.*, vol. 54, 1983.
