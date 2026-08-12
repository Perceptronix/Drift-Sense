# Parameter Library

**Research Phase:** 2.5
**Document:** 06_parameter_library.md
**Date:** 2026-07-30

---

## 1. Parameter Conventions

| Convention | Standard |
|---|---|
| **Parameter naming** | snake_case (e.g., `probe_current_pA`) |
| **Symbol naming** | As defined in Phase 2.2–2.4 documents |
| **Units** | SI with commonly used subunits (nm, pA, μs, keV) |
| **Data type** | float32 for continuous, int32 for discrete, string for labels |
| **Category** | `F` = Fixed, `C` = Configurable, `M` = Material library, `R` = Randomized |

---

## 2. Complete Parameter Table

### 2.1 Instrument Parameters

| # | Name | Symbol | Units | Category | Default | Range | Source | Used By |
|---|---|---|---|---|---|---|---|---|
| 1 | accelerating_voltage | $E_0$ | keV | C | 1.0 | 0.3–5.0 | [B1][B4] | Yield, Charging |
| 2 | probe_current | $I_P$ | pA | C | 15.0 | 5–200 | [B1][B2] | Yield, Noise |
| 3 | probe_diameter_fwhm | $d_p$ | nm | C | 1.0 | 0.5–2.0 | [B1][J1] | PSF |
| 4 | convergence_angle | $\alpha$ | mrad | F | 10.0 | — | [B1] | (probe formation context) |
| 5 | working_distance | $W$ | mm | C | 5.0 | 3–8 | [B1] | Detector |
| 6 | beam_energy_spread | $\Delta E$ | eV | F | 0.5 | — | [B1][B2] | (aberrations context) |
| 7 | pixel_size | $\Delta x$ | nm | C | 1.0 | 0.2–5.0 | [J1][J6] | All (image size) |
| 8 | image_width_pixels | $M$ | — | C | 1024 | 256–4096 | [J1][J2] | All (image size) |
| 9 | image_height_pixels | $N$ | — | C | 1024 | 256–4096 | [J1][J2] | All (image size) |
| 10 | pixel_dwell_time | $\tau$ | μs | C | 1.0 | 0.1–10 | [B2][J2] | Yield, Noise |
| 11 | num_averaged_frames | $N_{\text{avg}}$ | — | C | 1 | 1–256 | [J2][J6] | Noise (future) |

### 2.2 Detector Parameters

| # | Name | Symbol | Units | Category | Default | Range | Source | Used By |
|---|---|---|---|---|---|---|---|---|
| 12 | detector_type | — | — | C | "TTL" | "TTL"/"E-T" | [B1][B2] | Detector |
| 13 | se_collection_efficiency | $\eta_{\text{coll}}^{\text{SE}}$ | — | F | 0.7 | — | [B1][B2] | Detector, Yield |
| 14 | bse_collection_efficiency | $\eta_{\text{coll}}^{\text{BSE}}$ | — | F | 0.5 | — | [B1][B2] | Detector, Yield |
| 15 | pmt_excess_noise_factor | $F$ | — | F | 1.2 | — | [B2] | Noise |
| 16 | adc_resolution | $N_{\text{bits}}$ | bits | C | 16 | 8–16 | [J2] | Digitization |
| 17 | adc_voltage_range | $V_{\text{range}}$ | V | F | 5.0 | — | [J2] | Digitization |
| 18 | pmt_quantum_efficiency | QE | — | F | 0.20 | — | [B2] | Noise (context) |
| 19 | scintillator_efficiency | $\epsilon_{\text{scint}}$ | ph/e⁻ | F | 100 | — | [B2] | Noise (context) |
| 20 | tia_feedback_resistance | $R_f$ | MΩ | F | 10 | — | [B2] | Digitization |

### 2.3 Material Parameters (Per Material)

| # | Name | Symbol | Units | Category | Default (Si) | Range | Source | Used By |
|---|---|---|---|---|---|---|---|---|
| 21 | se_yield_normal | $\delta_0$ | — | M | 0.85 | 0.5–2.5 | [B1][J7] | Yield |
| 22 | bse_yield | $\eta$ | — | M | 0.18 | 0.06–0.52 | [B1][B4] | Yield |
| 23 | se_escape_depth | $\Lambda$ | nm | M | 2.0 | 0.5–20 | [B1][T1] | PSF |
| 24 | charging_factor | $f_c$ | — | M | 1.0 | 0.3–1.0 | Phase 2.4 | Charging |
| 25 | secant_exponent | $\gamma$ | — | M | 1.0 | — | [J7] | Yield |
| 26 | material_type | — | — | M | CONDUCTOR | 3 types | Phase 2.2 | Charging |
| 27 | atomic_number_avg | $Z$ | — | M | 14 | 4–74 | Periodic table | Yield (BSE) |
| 28 | density | $\rho$ | g/cm³ | M | 2.33 | 1.05–19.3 | [B2] | (context) |

### 2.4 Material Values (All 6 Materials at 1 keV)

| Material | $\delta_0$ | $\eta$ | $\Lambda$ (nm) | $f_c$ | $\gamma$ | Type | $Z$ | $\rho$ |
|---|---|---|---|---|---|---|---|---|
| **Si** | 0.85 | 0.18 | 2.0 | 1.0 | 1.0 | SEMICONDUCTOR | 14 | 2.33 |
| **SiO₂** | 1.80 | 0.14 | 10.0 | 0.6 | 1.0 | INSULATOR | 10 | 2.20 |
| **Si₃N₄** | 1.30 | 0.15 | 5.0 | 0.7 | 1.0 | INSULATOR | 11 | 3.10 |
| **Cu** | 1.10 | 0.32 | 1.0 | 1.0 | 1.0 | CONDUCTOR | 29 | 8.96 |
| **W** | 0.80 | 0.49 | 0.5 | 1.0 | 1.0 | CONDUCTOR | 74 | 19.3 |
| **Photoresist** | 2.00 | 0.08 | 15.0 | 0.5 | 1.0 | INSULATOR | 5 | 1.10 |

### 2.5 Noise Parameters

| # | Name | Symbol | Units | Category | Default | Range | Source | Used By |
|---|---|---|---|---|---|---|---|---|
| 29 | electron_charge | $e$ | C | F | $1.602\times10^{-19}$ | — | Physical constant | Yield, Noise |
| 30 | boltzmann_constant | $k_B$ | J/K | F | $1.381\times10^{-23}$ | — | Physical constant | Noise (context) |
| 31 | amplifier_temperature | $T$ | K | F | 300 | — | Standard | Noise (context) |
| 32 | amplifier_bandwidth | $\Delta f$ | MHz | F | 1.0 | — | [J2] | Noise (context) |
| 33 | amplifier_voltage_noise | $v_n$ | nV/√Hz | F | 5 | — | Typical | Noise (context) |
| 34 | pmt_dynode_gain_per_stage | $\delta_{\text{dyn}}$ | — | F | 4 | — | [B2] | Noise (context) |
| 35 | pmt_num_dynodes | $N_{\text{dyn}}$ | — | F | 12 | — | [B2] | Noise (context) |

### 2.6 PSF Parameters

| # | Name | Symbol | Units | Category | Default | Range | Source | Used By |
|---|---|---|---|---|---|---|---|---|
| 36 | se2_characteristic_length | $L_{\text{SE-II}}$ | nm | M | 50 (Si) | 10–200 | Phase 2.2 | PSF (SE-II) |
| 37 | se2_efficiency | $k_{\text{SE-II}}$ | — | M | 0.3 | 0.1–0.5 | Phase 2.2 | PSF (SE-II) |
| 38 | psf_kernel_radius_factor | $k_{\text{rad}}$ | — | F | 3.0 | — | Engineering | PSF |

### 2.7 Display/Output Parameters

| # | Name | Symbol | Units | Category | Default | Range | Source | Used By |
|---|---|---|---|---|---|---|---|---|
| 39 | system_gain | $G$ | — | C | 1.0 | 0.1–10 | Phase 2.3 | Digitization |
| 40 | signal_offset | $I_{\text{off}}$ | DN | C | 0 | — | Phase 2.3 | Digitization |
| 41 | output_bit_depth | $N_{\text{out}}$ | bits | C | 16 | 8, 16 | [J2] | Digitization |
| 42 | random_seed | — | — | C | 42 | any | Engineering | Noise (reproducibility) |

### 2.8 Derived Parameters

| # | Name | Symbol | Units | Formula | Used By |
|---|---|---|---|---|---|
| 43 | field_of_view | FOV | nm | $\Delta x \cdot M$ | Context |
| 44 | frame_time | $T_f$ | s | $M \cdot N \cdot \tau \cdot 10^{-6}$ | Context |
| 45 | electrons_per_pixel | $N_e$ | — | $I_P \tau / e$ | Noise (context) |
| 46 | signal_to_noise_ratio_max | SNR_max | — | $\sqrt{N_e \cdot (\delta + \eta) \cdot \eta_{\text{coll}}}$ | Context |
| 47 | probe_sigma_p | $\sigma_p$ | nm | $d_p / 2.355$ | PSF |
| 48 | escape_sigma_m | $\sigma_m$ | nm | $\Lambda / 2.355$ | PSF |
| 49 | effective_gain | $G_{\text{eff}}$ | e⁻/DN | Derived from $G$, ADC range, $N_bits$ | Noise |
| 50 | se2_convolution_kernel | $K_{\text{SE-II}}$ | — | $\exp(-r / L_{\text{SE-II}})$ | PSF |

---

## 3. Category Summary

| Category | Count | Examples |
|---|---|---|
| **Fixed (F)** | 18 | $e$, $k_B$, $\eta_{\text{coll}}^{\text{SE}}$, $F$, $V_{\text{range}}$, $\alpha$, $\Delta E$ |
| **Configurable (C)** | 14 | $E_0$, $I_P$, $d_p$, $\tau$, $\Delta x$, $M$, $N$, $N_{\text{bits}}$, $N_{\text{avg}}$, $G$ |
| **Material library (M)** | 8 per material | $\delta_0$, $\eta$, $\Lambda$, $f_c$, $\gamma$, type, $Z$, $L_{\text{SE-II}}$ |
| **Randomized (R)** | 1 | Poisson noise per pixel |
| **Derived** | 8 | $\sigma_p$, $\sigma_m$, $G_{\text{eff}}$, SNR, FOV, frame time, $N_e$ |

---

## 4. Parameter Grouping for the Renderer API

The renderer should accept configuration as a parameter struct:

```
RendererConfig {
    // Beam
    float accelerating_voltage_keV;   // default 1.0
    float probe_current_pA;           // default 15.0
    float probe_diameter_fwhm_nm;     // default 1.0

    // Scan
    float pixel_size_nm;              // default 1.0
    int image_width_pixels;           // default 1024
    int image_height_pixels;          // default 1024
    float pixel_dwell_time_us;        // default 1.0
    int num_averaged_frames;          // default 1

    // Detection
    string detector_type;             // default "TTL"
    int adc_resolution_bits;          // default 16

    // Display
    float system_gain;                // default 1.0
    float signal_offset_dn;           // default 0
    int output_bit_depth;             // default 16

    // Control
    int random_seed;                  // default 42
    bool enable_se2;                  // default true (Phase B+)
    bool enable_charging;             // default true (Phase B+)
    bool enable_blur;                 // default true (Phase A)
    bool enable_noise;                // default true (Phase A)
};
```

---

## Sources

- [B1] L. Reimer, *Scanning Electron Microscopy: Physics of Image Formation and Microanalysis*, 2nd ed. Springer, 1998.
- [B2] J. I. Goldstein, D. E. Newbury, J. R. Michael, et al., *Scanning Electron Microscopy and X-Ray Microanalysis*, 4th ed. Springer, 2017.
- [B4] D. C. Joy, *Monte Carlo Modeling for Electron Microscopy and Microanalysis*. Oxford University Press, 1995.
- [J1] J. S. Villarrubia, A. E. Vladar, and M. T. Postek, "Scanning electron microscope measurement of width and shape of fabricated nanostructures," *J. Res. NIST*, vol. 109, 2004.
- [J2] C. N. Archie, "Critical dimension metrology," *AIP Conf. Proc.*, vol. 788, 2005.
- [J6] B. D. Bunday et al., "CD-SEM metrology," *Proc. SPIE*, vol. 5038, 2003.
- [J7] H. Seiler, "Secondary electron emission in the scanning electron microscope," *J. Appl. Phys.*, vol. 54, 1983.
- [T1] NIST, "Electron Inelastic Mean Free Path Database" (SRD 71).
