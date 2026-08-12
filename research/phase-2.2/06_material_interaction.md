# Material Interaction Behavior for Semiconductor Materials

**Research Phase:** 2.2
**Document:** 06_material_interaction.md
**Date:** 2026-07-30

---

## 1. Introduction

Different materials interact with the electron beam in fundamentally different ways. For semiconductor wafer inspection, the primary beam encounters a diverse set of materials — conductors, semiconductors, and insulators — each with distinct scattering properties, SE yields, and BSE yields. Understanding these differences is essential for interpreting SEM signals and for any physics-based simulation.

This document characterizes the electron interaction behavior of the six most relevant semiconductor materials.

---

## 2. Material Properties Reference

### 2.1 Key Physical Parameters

| Material | Formula | Avg Z | Density (g/cm³) | Work Function (eV) | Band Gap (eV) | Conductivity |
|---|---|---|---|---|---|---|
| **Silicon** | Si | 14 | 2.33 | 4.85 | 1.12 | Semiconductor |
| **Silicon dioxide** | SiO₂ | ~10 | 2.20 | ~0.9 (e⁻ affinity) | 8.9 | Insulator |
| **Silicon nitride** | Si₃N₄ | ~11 | 3.10 | ~1.5 (e⁻ affinity) | 5.3 | Insulator |
| **Copper** | Cu | 29 | 8.96 | 4.65 | — | Conductor (metal) |
| **Tungsten** | W | 74 | 19.3 | 4.55 | — | Conductor (metal) |
| **Photoresist** | Organic (C,H,O,N) | ~4–6 | ~1.05–1.20 | ~0.5–1.0 (e⁻ affinity) | >4 (insulator) | Insulator |

**Note:** For insulators (SiO₂, Si₃N₄, photoresist), the electron affinity (energy from vacuum to conduction band minimum) replaces the work function as the relevant parameter for electron escape.

---

## 3. Scattering and Energy Loss

### 3.1 Elastic Scattering (by Material)

| Material | Elastic MFP at 1 keV | Elastic MFP at 10 keV | Scattering Regime at 1 keV |
|---|---|---|---|
| Si | ~10 nm | ~100 nm | Plural (tens of events) |
| SiO₂ | ~15 nm | ~150 nm | Plural |
| Si₃N₄ | ~12 nm | ~120 nm | Plural |
| Cu | ~3 nm | ~30 nm | Multiple (hundreds of events) |
| W | ~1 nm | ~10 nm | Multiple (hundreds of events) |
| Photoresist | ~30 nm | ~300 nm | Single to plural |

### 3.2 Stopping Power (Bethe)

| Material | $dE/ds$ at 1 keV | $dE/ds$ at 10 keV | Bethe Range at 1 keV | Bethe Range at 10 keV |
|---|---|---|---|---|
| Si | ~0.8 eV/nm | ~0.2 eV/nm | ~50 nm | ~5 μm |
| SiO₂ | ~0.7 eV/nm | ~0.18 eV/nm | ~70 nm | ~6 μm |
| Si₃N₄ | ~0.9 eV/nm | ~0.22 eV/nm | ~45 nm | ~4.5 μm |
| Cu | ~1.8 eV/nm | ~0.45 eV/nm | ~20 nm | ~1.5 μm |
| W | ~3.5 eV/nm | ~0.9 eV/nm | ~8 nm | ~0.6 μm |
| Photoresist | ~0.4 eV/nm | ~0.1 eV/nm | ~150 nm | ~12 μm |

### 3.3 Interaction Volume Size

| Material | Penetration at 500 eV | Penetration at 1 keV | Penetration at 5 keV | Shape |
|---|---|---|---|---|
| Si | ~15 nm | ~30 nm | ~500 nm | Teardrop |
| SiO₂ | ~25 nm | ~50 nm | ~800 nm | Teardrop |
| Si₃N₄ | ~15 nm | ~35 nm | ~500 nm | Teardrop |
| Cu | ~7 nm | ~15 nm | ~200 nm | Intermediate |
| W | ~2 nm | ~5 nm | ~50 nm | Hemispherical |
| Photoresist | ~50 nm | ~100 nm | ~2 μm | Very teardrop (low Z, low density) |

**Fact:** The interaction volume in photoresist at 1 keV is approximately 3× deeper than in Si and 20× deeper than in W. This means that when imaging photoresist patterns on Si, most of the beam energy is deposited in the resist, not the substrate.

---

## 4. Secondary Electron Yield

### 4.1 SE Yield Values

| Material | $\delta_{\text{max}}$ | $E_{\text{max}}$ (eV) | $\delta$ at 500 eV | $\delta$ at 1 keV | $\delta$ at 5 keV |
|---|---|---|---|---|---|
| Si | ~1.1 | ~250 | ~1.0 | ~0.85 | ~0.30 |
| SiO₂ | ~2.5 | ~400 | ~2.2 | ~1.8 | ~0.45 |
| Si₃N₄ | ~1.8 | ~350 | ~1.6 | ~1.3 | ~0.35 |
| Cu | ~1.3 | ~600 | ~1.0 | ~1.1 | ~0.40 |
| W | ~1.0 | ~700 | ~0.7 | ~0.8 | ~0.35 |
| Photoresist | ~2.5 | ~250 | ~2.2 | ~2.0 | ~0.50 |

**Note:** SE yield values are approximate and depend on surface condition, contamination, and measurement method. Conflicting values exist in the literature, particularly for SiO₂ and photoresist.

### 4.2 SE Yield at CD-SEM Energies

At the operating energies used for CD-SEM (300 eV–1.5 keV):

| Material | SE Yield at 300 eV | SE Yield at 800 eV | SE Yield at 1.5 keV |
|---|---|---|---|
| Si | ~0.9 | ~0.9 | ~0.7 |
| SiO₂ | ~1.8 | ~2.0 | ~1.5 |
| Si₃N₄ | ~1.4 | ~1.5 | ~1.1 |
| Cu | ~0.7 | ~1.0 | ~1.0 |
| W | ~0.5 | ~0.7 | ~0.8 |
| Photoresist | ~2.0 | ~2.2 | ~1.7 |

**Inference:** At typical CD-SEM energies (500–800 eV), SE yields vary significantly across materials:
- Photoresist and SiO₂ have the highest yields (1.8–2.2).
- Tungsten has the lowest yield (0.5–0.7).
- This material-dependent SE yield is one source of contrast in SEM images of semiconductor structures.

---

## 5. Backscattered Electron Yield

### 5.1 BSE Yield Values

| Material | Z | $\eta$ at 1 keV | $\eta$ at 5 keV | $\eta$ at 10 keV | $\eta$ at 20 keV |
|---|---|---|---|---|---|
| Si | 14 | ~0.20 | ~0.18 | ~0.17 | ~0.17 |
| SiO₂ | ~10 | ~0.16 | ~0.14 | ~0.13 | ~0.13 |
| Si₃N₄ | ~11 | ~0.18 | ~0.15 | ~0.14 | ~0.14 |
| Cu | 29 | ~0.33 | ~0.32 | ~0.31 | ~0.31 |
| W | 74 | ~0.52 | ~0.50 | ~0.49 | ~0.49 |
| Photoresist | ~5 | ~0.10 | ~0.08 | ~0.07 | ~0.07 |

**Fact:** The BSE yield increases at low energies for all materials. This effect is more pronounced for high-Z materials. At 500 eV, the BSE yield for W can exceed 0.55.

### 5.2 Compositional Contrast Between Materials

**BSE contrast at 500 eV (CD-SEM typical):**

| Material Pair | Z Difference | $\eta_A$ | $\eta_B$ | Contrast $C_Z$ |
|---|---|---|---|---|
| W vs. SiO₂ | 64 | 0.52 | 0.16 | 0.53 |
| Cu vs. SiO₂ | 19 | 0.33 | 0.16 | 0.35 |
| Cu vs. Si | 15 | 0.33 | 0.20 | 0.25 |
| Si vs. SiO₂ | 4 | 0.20 | 0.16 | 0.11 |
| Si₃N₄ vs. SiO₂ | 1 | 0.18 | 0.16 | 0.06 |
| Photoresist vs. SiO₂ | 5 | 0.10 | 0.16 | 0.23 |

**Inference:** The strongest BSE compositional contrast is between metals (Cu, W) and dielectrics (SiO₂). The contrast between Si and SiO₂ is relatively weak, and contrast between Si₃N₄ and SiO₂ is very weak — these material pairs may be difficult to distinguish by BSE alone.

---

## 6. Charging Behavior

### 6.1 Total Yield and Charge Balance

The total electron emission yield $\sigma = \delta + \eta$ determines whether the sample charges positively, negatively, or is neutral:

| Material | $\sigma$ at 500 eV | $\sigma$ at 1 keV | $\sigma$ at 5 keV |
|---|---|---|---|
| Si | ~1.2 | ~1.05 | ~0.48 |
| SiO₂ | ~2.36 | ~1.93 | ~0.58 |
| Si₃N₄ | ~1.78 | ~1.48 | ~0.50 |
| Cu | ~1.03 | ~1.43 | ~0.72 |
| W | ~1.02 | ~1.32 | ~0.85 |
| Photoresist | ~2.30 | ~2.10 | ~0.57 |

**Inference:**
- At 500 eV: Most materials have $\sigma > 1$ → positive charging (net electron emission).
- At 1 keV: Varied behavior. Si is near-neutral ($\sigma \approx 1$). Insulators are still $\sigma > 1$ (positive charging).
- At 5 keV: All materials have $\sigma < 1$ → negative charging (net electron absorption).

**Fact:** The charge-neutral condition ($\sigma = 1$) occurs at different energies for different materials. Operating at the neutral energy minimizes charging artifacts. For Si, this is around 1 keV. For SiO₂, it is around 800 eV.

---

## 7. Material-Specific Considerations

### 7.1 Silicon (Si)
- **Most common substrate material.**
- Moderate SE yield, moderate BSE yield.
- Conductive enough to prevent severe charging (if lightly doped).
- Interaction volume at 1 keV: ~30 nm penetration.
- **In CD-SEM:** Si lines on buried oxide (SOI) or Si substrates produce clear SE edge signals.

### 7.2 Silicon Dioxide (SiO₂)
- **Primary interlayer dielectric (ILD) material.**
- High SE yield (δ ~2 at 800 eV) → strong topographic signal.
- Insulator → prone to charging, which can distort CD measurements.
- Charge-neutral at ~600–800 eV (depending on film thickness).
- **In CD-SEM:** Often used in CMP inspection; high SE yield helps image shallow trenches.

### 7.3 Silicon Nitride (Si₃N₄)
- **Used as etch stop, spacer, hard mask.**
- Similar average Z to SiO₂ (Z~11 vs. Z~10) → weak BSE contrast against SiO₂.
- Higher density than SiO₂ (3.10 vs. 2.20 g/cm³) → smaller interaction volume.
- SE yield between Si and SiO₂.
- **In CD-SEM:** Lower topographic contrast than resist on Si.

### 7.4 Copper (Cu)
- **Primary BEOL conductor material.**
- Higher Z (29) → strong BSE signal, good contrast against dielectrics.
- Moderate SE yield.
- Conductive (no charging).
- Higher energy backscatter can excite SE-II in surrounding dielectrics.
- **In CD-SEM:** Cu damascene lines are imaged well by both SE (edge definition) and BSE (material contrast for void detection).

### 7.5 Tungsten (W)
- **Used for contacts, vias, and hard masks.**
- Very high Z (74) → strongest BSE signal; highest Z-contrast.
- Lowest SE yield of common semiconductor materials.
- Conductive (no charging).
- Very small interaction volume at CD-SEM energies (~5 nm at 1 keV).
- **In CD-SEM:** Bright in BSE images; dark in SE images (low SE yield). Contact holes filled with W are easily distinguished from surrounding oxide.

### 7.6 Photoresist
- **Primary patterning material.**
- Very low average Z (~4–6) → very low BSE yield, low BSE contrast against Si.
- Very high SE yield (δ ~2+ at CD-SEM energies).
- Insulator → significant charging at higher energies.
- **Extremely beam-sensitive:** Shrinks and deforms under electron beam exposure.
- Low density → large interaction volume.
- **In CD-SEM:** Imaged almost exclusively by SE signal. The high SE yield provides strong topographic signal at pattern edges. Resist line slimming under the beam is a well-known measurement challenge.

---

## 8. Interaction Parameter Comparison at CD-SEM Conditions (500 eV)

| Parameter | Si | SiO₂ | Si₃N₄ | Cu | W | Resist |
|---|---|---|---|---|---|---|
| SE yield δ | ~1.0 | ~2.2 | ~1.6 | ~1.0 | ~0.7 | ~2.2 |
| BSE yield η | ~0.20 | ~0.16 | ~0.18 | ~0.33 | ~0.52 | ~0.10 |
| Total yield σ | 1.20 | 2.36 | 1.78 | 1.33 | 1.22 | 2.30 |
| SE escape depth (nm) | ~2 | ~10 | ~5 | ~1 | ~0.5 | ~20 |
| BSE escape depth (nm) | ~10 | ~15 | ~10 | ~5 | ~2 | ~40 |
| Interaction depth (nm) | ~15 | ~25 | ~15 | ~7 | ~2 | ~50 |
| Charging tendency | Neutral+ | Strong + | Moderate + | Neutral | Neutral | Strong + |

---

## 9. Summary

### 9.1 Key Takeaways for Simulation

1. **SE yield varies by a factor of ~3** between materials (W ~0.7, resist ~2.2). This is a significant source of grayscale contrast.

2. **BSE yield varies by a factor of ~5** between materials (resist ~0.10, W ~0.52). This is the basis for compositional imaging.

3. **Escape depths differ dramatically:** SE escape depth ranges from ~0.5 nm (W) to ~20 nm (resist). This affects the spatial resolution achievable on each material.

4. **Interaction volume size varies by ~25×** between photoresist (~50 nm) and W (~2 nm) at 500 eV. High-Z materials confine the interaction much more tightly.

5. **Charging state depends strongly on material and beam energy.** Operation at the charge-neutral condition requires energy selection based on the specific film stack.

### 9.2 Material Library for Simulation

The following properties must be defined for each material in a physics-based SEM simulator:

| Required Property | Why |
|---|---|
| Atomic number (Z) or composition | Elastic cross-section, BSE yield |
| Density (ρ) | Stopping power, range |
| Work function or electron affinity | SE escape probability |
| Density of states (implicitly via $J$) | Mean ionization potential |
| Band gap (insulators) | Charging behavior |

---

## Sources

- L. Reimer, *Scanning Electron Microscopy: Physics of Image Formation and Microanalysis*, 2nd ed. Springer, 1998.
- J. I. Goldstein, D. E. Newbury, J. R. Michael, et al., *Scanning Electron Microscopy and X-Ray Microanalysis*, 4th ed. Springer, 2017.
- R. F. Egerton, *Physical Principles of Electron Microscopy*, 2nd ed. Springer, 2016.
- D. C. Joy, *Monte Carlo Modeling for Electron Microscopy and Microanalysis*. Oxford University Press, 1995.
- H. Seiler, "Secondary electron emission in the scanning electron microscope," *J. Appl. Phys.*, vol. 54, 1983.
- Y. Lin and D. C. Joy, "A new examination of secondary electron yield data," *Surf. Interface Anal.*, vol. 37, 2005.
- NIST, "Electron Inelastic Mean Free Path Database" (SRD 71).
- S. Tanuma, C. J. Powell, and D. R. Penn, "Calculations of electron inelastic mean free paths," *Surf. Interface Anal.*, vol. 21, 1994.
