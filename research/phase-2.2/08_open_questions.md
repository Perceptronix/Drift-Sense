# Open Questions (Phase 2.2)

**Research Phase:** 2.2
**Document:** 08_open_questions.md
**Date:** 2026-07-30

---

## 1. Answered Within Phase 2.2

| Question | Answer | Document |
|---|---|---|
| What is the interaction volume and how does it form? | The 3D region where primary electrons deposit energy; shaped by elastic/inelastic scattering balance. Size scales as $E^{1.7}$ approximately, decreases with Z and density. | 02_electron_sample_interaction.md |
| What signals are generated when the beam hits the sample? | SE (0–50 eV), BSE (>50 eV), Auger, characteristic X-rays, bremsstrahlung, CL, specimen current, transmitted electrons. | 02, 03, 04, 05 |
| Why do SEs dominate semiconductor SEM? | Highest resolution (escape depth 1–5 nm), strong topographic contrast ($\sec\theta$ dependence), high yield ($\delta_{\text{max}} > 1$), compatible with low-voltage operation. | 03_secondary_electron_physics.md |
| When are BSEs useful? | Compositional contrast (Z-contrast), voltage contrast for electrical defect detection, subsurface structure imaging. | 04_backscattered_electron_physics.md |
| What is the SE-I/SE-II/SE-III distinction? | SE-I from primary beam impact (highest resolution); SE-II from exiting BSEs (reduces resolution); SE-III from chamber walls (background). | 03_secondary_electron_physics.md |
| How does the BSE yield depend on atomic number? | $\eta$ increases monotonically with Z. $\eta$ ranges from ~0.06 (C) to ~0.52 (W). | 04_backscattered_electron_physics.md |
| Which signals are essential for simulation? | SE-I, SE-II, BSE (Z-dependent). All others can be ignored. | 07_engineering_conclusions.md |
| How does material choice affect the interaction? | Interaction depth varies by ~25× between W (~2 nm) and photoresist (~50 nm) at 500 eV. SE yield varies by ~3× between materials. | 06_material_interaction.md |

---

## 2. Questions Deferred to Phase 2.3

These are the critical questions that must be answered to bridge from "understanding signal generation" to "understanding how the grayscale SEM image is formed."

### 2.1 Contrast Formation

| # | Question | Description |
|---|---|---|
| Q1 | How does the SE/BSE signal at each point on the sample translate into grayscale contrast across a patterned wafer? | Need to connect local yield to image brightness variation. |
| Q2 | What is edge brightening and what is its physical origin? | The enhanced SE signal at topographic edges — critical for CD detection. |
| Q3 | How do different materials produce different grayscale levels in SE and BSE images? | The material-dependent yield must be mapped to relative brightness. |
| Q4 | How does surface topography modulate the detected signal at slopes, shadowed surfaces, and tilted sidewalls? | The $\sec\theta$ law alone may be insufficient for complex 3D geometries. |
| Q5 | What are the contrast mechanisms in CD-SEM that enable precise edge detection? | Need to identify which features of the signal profile correspond to pattern edges. |

### 2.2 Signal Collection and Detection

| # | Question | Description |
|---|---|---|
| Q6 | How does the detector collection efficiency vary with position on the sample? | The detector has a finite acceptance angle; not all emitted electrons are collected. |
| Q7 | How does the detector transfer function map emitted electrons to pixel intensity? | The relationship between electron flux and grayscale value. |
| Q8 | How does the TTL SE detector selectively collect SE-I vs. SE-II? | The magnetic field of the objective lens acts as a spectrometer. |

### 2.3 Pixel Formation

| # | Question | Description |
|---|---|---|
| Q9 | How is the pixel grayscale value determined from the number of detected electrons? | The statistical and electronic processes linking electron counts to digital values. |
| Q10 | How does the beam probe shape affect the signal profile at pattern edges? | The convolution of the probe with the sample's yield function determines the edge profile. |
| Q11 | What is the role of pixel sampling in measuring sub-pixel feature positions? | Essential for understanding CD measurement precision. |

### 2.4 First-Order Image Properties

| # | Question | Description |
|---|---|---|
| Q12 | What does an SEM image of a simple line/space pattern look like and why? | The most basic pattern in semiconductor metrology. |
| Q13 | How does the line profile (intensity vs. position across a line) form from the underlying physics? | The fundamental measurement in CD-SEM. |
| Q14 | How do SE and BSE images of the same structure differ? | Complementary information; need to understand both. |

### 2.5 Summary of Phase 2.3 Requirements

Phase 2.3 must address:

- **Contrast mechanisms:** How topography, material composition, and voltage state modulate the detected signal.
- **Edge signal formation:** The physical origin of the edge brightening profile used for CD detection.
- **Detector model:** How emitted electrons are collected and converted to pixel values.
- **Probe-sample convolution:** How the finite probe size affects the image of a patterned structure.
- **Basic line profile:** The intensity distribution across a line/space structure in SE and BSE modes.

These topics build directly on the signal generation physics established in Phase 2.2.

---

## 3. Questions for Later Phases (Beyond Phase 2.3)

| # | Question | Likely Phase |
|---|---|---|
| Q15 | How does noise affect the line profile and CD measurement precision? | Phase 3 (Noise) |
| Q16 | How do image blur mechanisms (delocalization, vibration, drift) degrade CD measurement? | Phase 3 (Blur) |
| Q17 | How does sample charging affect the electron trajectories and image formation? | Phase 3 (Charging) |
| Q18 | How should the complete SEM image formation chain be modeled for accurate simulation? | Phase 3 or Phase 4 (Simulation Framework) |
| Q19 | How does the SEM line profile relate to the true feature shape (inverse problem)? | Phase 3 (Model-Based Metrology) |

---

## 4. Unresolved Questions

| # | Question | Nature of Uncertainty |
|---|---|---|
| U1 | What is the exact SE-I / SE-II ratio for a given material and beam energy? | The ratio depends on the material, beam energy, and surface geometry. Published values range from 30:70 to 70:30 depending on conditions. |
| U2 | What are the exact BSE yields for thin films (e.g., 10 nm SiO₂ on Si) at low voltages (<1 keV)? | BSE yield from thin films depends on both film and substrate. Existing empirical formulas are validated for bulk materials. Thin-film corrections are less established. |
| U3 | What is the effective escape depth for SE in SiO₂ at very low energies (<200 eV)? | The IMFP for insulators at very low energies is not as well-characterized as for metals. |
| U4 | What is the angular dependence of SE yield for non-sinusoidal topographies (e.g., vertical sidewalls, re-entrant profiles)? | The $\sec\theta$ model is valid for gently sloping surfaces. Its applicability to extreme topographic features in 3D NAND structures (high aspect ratio, re-entrant profiles) is less certain. |
| U5 | What is the correct Bethe stopping power for organic photoresists at low keV energies? | Photoresist composition varies (polymer + photoacid generator + quencher). The mean ionization potential $J$ is not precisely known for these mixtures. |

**Recommendation:** For simulation purposes, use the best available literature values and flag these uncertainties for sensitivity analysis. If the simulation results are insensitive to the exact values (i.e., CD measurements change by <1% over the plausible range), then the uncertainty is acceptable.

---

## 5. Process for Resolving Open Questions

1. **Phase 2.3** will answer Q1–Q14 (contrast formation, detection, pixel formation, basic image properties).
2. **Unresolved questions (U1–U5)** should be addressed by:
   - A focused literature review of low-voltage SEM interactions (papers by Joy, Reimer, Seiler).
   - Monte Carlo simulations (CASINO or PENELOPE) to quantify the sensitivity of image properties to uncertain parameters.
   - If quantitative accuracy is needed: experimental measurements on a calibrated SEM using test structures.
