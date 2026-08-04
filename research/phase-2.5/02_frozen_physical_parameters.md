# Frozen Physical Parameters

**Research Phase:** 2.5
**Document:** 02_frozen_physical_parameters.md
**Date:** 2026-07-30

---

## 1. Parameter Classification

Every parameter in the simulator falls into one of three categories:

| Category | Definition | Example | Who Sets It |
|---|---|---|---|
| **Fixed** | Constant across all simulations. Not user-adjustable. | Electron charge $e$, Boltzmann constant $k_B$ | Physics — cannot be changed |
| **Material library** | Constant for a given material at a given beam energy. | SE yield $\delta_0$, escape depth $\Lambda$ | Physics — determined by material choice |
| **Configurable (User)** | Adjustable by the operator to control imaging conditions. | Probe current $I_P$, dwell time $\tau$, pixel size $\Delta x$ | User — operator or recipe parameter |
| **Randomized** | Sampled from a probability distribution during rendering. | Shot noise realization | Random — noise generator |

---

## 2. Instrument Parameters

### 2.1 Primary Beam Parameters

| Parameter | Symbol | Category | Nominal Value | Valid Range | Source |
|---|---|---|---|---|---|
| Accelerating voltage | $E_0$ | Configurable | 1.0 keV | 300 eV – 5 keV | [B1][B2][B4] |
| Probe current | $I_P$ | Configurable | 15 pA | 5 – 200 pA | [B1][B4] |
| Probe diameter (FWHM) | $d_p$ | Configurable | 1.0 nm | 0.5 – 2.0 nm | [B1][B2][J1] |
| Convergence half-angle | $\alpha$ | Fixed | 10 mrad | — | [B1] — set by aperture |
| Working distance | $W$ | Configurable | 5 mm | 3 – 8 mm | [B1][B4] |
| Beam energy spread | $\Delta E$ | Fixed | 0.5 eV (Schottky FEG) | — | [B1][B2] |

**Engineering Decision:** Nominal values are chosen to match typical CD-SEM operating conditions for sub-10 nm metrology. The configurable ranges span the practical limits of a modern CD-SEM with Schottky FEG source.

### 2.2 Scanning Parameters

| Parameter | Symbol | Category | Nominal Value | Valid Range | Source |
|---|---|---|---|---|---|
| Pixel dwell time | $\tau$ | Configurable | 1 μs | 0.1 – 10 μs | [B1][B2][J2] |
| Pixel size (scan increment) | $\Delta x$ | Configurable | 1.0 nm | 0.2 – 5.0 nm | [J1][J2] |
| Image width (pixels) | $M$ | Configurable | 1024 | 256 – 4096 | [J1][J2] |
| Image height (pixels) | $N$ | Configurable | 1024 | 256 – 4096 | [J1][J2] |
| Field of view | FOV | Derived | $M \cdot \Delta x$ | — | — |
| Number of averaged frames | $N_{\text{avg}}$ | Configurable | 1 | 1 – 256 | [J2][J6] |

**Engineering Decision:** The 1024×1024 pixel grid with 1 nm pixel size and 1 μs dwell gives a 1 μm FOV and ~1 s frame time — the standard for CD-SEM measurements.

### 2.3 Detection Parameters

| Parameter | Symbol | Category | Nominal Value | Valid Range | Source |
|---|---|---|---|---|---|
| SE collection efficiency (TTL) | $\eta_{\text{coll,SE}}$ | Fixed | 0.7 | — | [B1][B2] |
| BSE collection efficiency (annular) | $\eta_{\text{coll,BSE}}$ | Fixed | 0.5 | — | [B1][B2] |
| PMT dynode multiplication per stage | $\delta_{\text{dynode}}$ | Fixed | 4 | — | [B2] |
| Number of PMT dynodes | $N_{\text{dyn}}$ | Fixed | 12 | — | [B2] |
| PMT excess noise factor | $F$ | Fixed | 1.2 | — | [B2][W2] |
| ADC resolution | $N_{\text{bits}}$ | Configurable | 16 bit | 8 – 16 bit | [J2] |
| ADC voltage range | $V_{\text{range}}$ | Fixed | 5 V | — | [J2] |
| PMT quantum efficiency (photocathode) | QE | Fixed | 0.20 | — | [B2] |
| Scintillator conversion efficiency | $\epsilon_{\text{scint}}$ | Fixed | 100 photons/electron | — | [B2] |
| Light guide transmission | $\epsilon_{\text{guide}}$ | Fixed | 0.7 | — | [B2] |
| Feedback resistor (TIA) | $R_f$ | Fixed | 10 MΩ | — | [B2] |
| Video amplifier bandwidth | $\Delta f$ | Fixed | 1 MHz | — | [J2] |

---

## 3. Material Parameters (Frozen at 1 keV)

### 3.1 SE and BSE Yields

| Material | Symbol Si | SiO₂ | Si₃N₄ | Cu | W | Photoresist | Source |
|---|---|---|---|---|---|---|---|
| **SE yield** $\delta_0$ | 0.85 | 1.8 | 1.3 | 1.1 | 0.8 | 2.0 | [B1][B2][J7] |
| **BSE yield** $\eta$ | 0.18 | 0.14 | 0.15 | 0.32 | 0.49 | 0.08 | [B1][B4] |
| **Total yield** $\sigma = \delta + \eta$ | 1.03 | 1.94 | 1.45 | 1.42 | 1.29 | 2.08 | — |

**Engineering Decision:** These values are frozen at 1 keV (the nominal energy). For other energies, scaling laws from Reimer [B1] and Joy [B4] are used. Conflicting values exist in the literature (spread of ±10–30% for SE yields, ±5–15% for BSE yields). The values above are the mid-range of published measurements.

### 3.2 Escape Depths

| Material | SE Escape Depth $\Lambda$ (nm) | SE-I Resolution $\sigma_m$ (nm) | Source |
|---|---|---|---|
| Si | 2.0 | 0.85 | [B1][B3][T1] |
| SiO₂ | 10.0 | 4.25 | [B1][B3] |
| Si₃N₄ | 5.0 | 2.12 | [B1] |
| Cu | 1.0 | 0.43 | [B1][T1] |
| W | 0.5 | 0.21 | [B1][T1] |
| Photoresist | 15.0 | 6.37 | [B1] |

**Source:** Primarily from NIST SRD 71 (IMFP database) [T1] and Reimer [B1]. The SE escape depth is approximately 0.3–0.5× the IMFP at 5 eV (near the peak of the SE energy distribution).

### 3.3 Charging Factors

| Material | Charge Behavior | Charging Factor $f_c$ | Polarity at 1 keV | Source |
|---|---|---|---|---|
| Si | Slight positive | 1.0 (no correction) | Slightly positive | [B1][B2] |
| SiO₂ | Strong positive | 0.6 | Positive | [B1][B2][J4] |
| Si₃N₄ | Moderate positive | 0.7 | Positive | [B1] |
| Cu | None (conductor) | 1.0 (no correction) | None | [B1][B2] |
| W | None (conductor) | 1.0 (no correction) | None | [B1][B2] |
| Photoresist | Strong positive | 0.5 | Positive | [B1][B2] |

**Engineering Decision:** The charging factor $f_c$ is a simplification — it lumps charge accumulation, SE recapture, and trajectory modification into a single multiplier. Values are calibrated to produce visually realistic insulator brightness relative to conductors. Full electrostatic simulation is deferred.

---

## 4. Noise Parameters (Frozen)

| Parameter | Symbol | Value | Source |
|---|---|---|---|
| Electron charge | $e$ | $1.602 \times 10^{-19}$ C | Physical constant |
| Boltzmann constant | $k_B$ | $1.381 \times 10^{-23}$ J/K | Physical constant |
| Temperature (amplifier) | $T$ | 300 K | Standard assumption |
| PMT excess noise factor | $F$ | 1.2 | [B2] |
| Dark current (referred to PMT anode) | $I_{\text{dark}}$ | 1 nA (negligible) | [B2] |
| Amplifier input voltage noise | $v_n$ | 5 nV/√Hz | Typical for low-noise op-amp |
| Amplifier input current noise | $i_n$ | 0.5 fA/√Hz | Typical for JFET input |

**Engineering Decision:** At nominal current (15 pA) and dwell (1 μs), the detected signal is ~100 electrons per pixel giving SNR ~10:1. Shot noise dominates all other noise sources by at least 10:1.

---

## 5. Operating Scenarios

### 5.1 Standard Scenarios

| Scenario | $E_0$ | $I_P$ | $d_p$ | $\tau$ | $\Delta x$ | $N_{\text{avg}}$ | Use Case |
|---|---|---|---|---|---|---|---|
| **High-resolution CD** | 1 keV | 15 pA | 1.0 nm | 2 μs | 0.5 nm | 8 | Precision CD measurement |
| **Standard CD** | 1 keV | 15 pA | 1.0 nm | 1 μs | 1.0 nm | 1 | Routine measurement |
| **Fast inspection** | 1 keV | 50 pA | 1.5 nm | 0.5 μs | 2.0 nm | 1 | High-throughput |
| **High-voltage** | 5 keV | 100 pA | 2.0 nm | 1 μs | 1.0 nm | 4 | Deep trench / voltage contrast |
| **Low-voltage** | 500 eV | 10 pA | 0.8 nm | 2 μs | 0.5 nm | 16 | Surface-sensitive / charging mitigation |

---

## 6. Previously Frozen Parameters (Confirmed)

The following parameters were established in Phases 2.2–2.4 and are confirmed:

| Parameter | Value | Phase | Document |
|---|---|---|---|
| Elastic scattering cross-section | Mott | 2.2 | 02_electron_sample_interaction |
| Inelastic scattering model | Bethe CSDA | 2.2 | 02_electron_sample_interaction |
| SE energy distribution | Chung-Everhart | 2.2 | 03_secondary_electron_physics |
| SE angular emission | Cosine distribution | 2.2 | 03_secondary_electron_physics |
| BSE angular emission | Cosine (flat), peaked forward (tilted) | 2.2 | 04_backscattered_electron_physics |
| SE-I escape probability | Exponential $P(z) \propto \exp(-z/\Lambda)$ | 2.2 | 03_secondary_electron_physics |
| Topographic contrast | $\sec\theta$ with $\gamma$ exponent | 2.3 | 03_secondary_electron_contrast |
| Material contrast | $\delta_0(Z)$ per material | 2.3 | 06_material_interaction |
| Detector type | TTL SE + annular BSE | 2.3 | 02_signal_to_image_pipeline |
| PSF (first order) | Gaussian probe | 2.4 | 02_resolution_and_blur |
| Noise (first order) | Poisson shot noise | 2.4 | 03_noise_models |
| Charging (first order) | Effective yield reduction | 2.4 | 04_charging_physics |

---

## Sources

- [B1] L. Reimer, *Scanning Electron Microscopy: Physics of Image Formation and Microanalysis*, 2nd ed. Springer, 1998.
- [B2] J. I. Goldstein, D. E. Newbury, J. R. Michael, et al., *Scanning Electron Microscopy and X-Ray Microanalysis*, 4th ed. Springer, 2017.
- [B3] R. F. Egerton, *Physical Principles of Electron Microscopy*, 2nd ed. Springer, 2016.
- [B4] D. C. Joy, *Monte Carlo Modeling for Electron Microscopy and Microanalysis*. Oxford University Press, 1995.
- [B7] M. T. Postek and A. E. Vladar, "Critical dimension metrology," in *Handbook of Semiconductor Manufacturing Technology*, CRC Press, 2007.
- [J1] J. S. Villarrubia, A. E. Vladar, and M. T. Postek, "Scanning electron microscope measurement of width and shape of fabricated nanostructures," *J. Res. NIST*, vol. 109, 2004.
- [J2] C. N. Archie, "Critical dimension metrology," *AIP Conf. Proc.*, vol. 788, 2005.
- [J4] D. C. Joy and C. S. Joy, "Low-voltage scanning electron microscopy," *Micron*, vol. 27, 1996.
- [J6] B. D. Bunday et al., "CD-SEM metrology," *Proc. SPIE*, vol. 5038, 2003.
- [J7] H. Seiler, "Secondary electron emission in the scanning electron microscope," *J. Appl. Phys.*, vol. 54, 1983.
- [T1] NIST, "Electron Inelastic Mean Free Path Database" (SRD 71).
