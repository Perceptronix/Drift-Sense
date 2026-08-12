# Validation Strategy

**Research Phase:** 2.6
**Document:** 05_validation_strategy.md
**Date:** 2026-07-30

---

## 1. Validation Philosophy

Validation proceeds in four layers:

| Layer | Scope | Method | Target |
|---|---|---|---|
| **Unit** | Individual modules | Synthetic input → known output | Each module independently |
| **Profile** | 1D line scans | Compare to MC and literature | Edge positions, peak amplitudes, widths |
| **Image** | Full 2D images | Qualitative comparison | Visual realism |
| **Metrology** | CD measurement | Input CD vs. measured CD | CD bias and precision |

---

## 2. Reference Structures

### 2.1 Primary Validation Structures

| ID | Structure | Material | CD (nm) | Pitch (nm) | Height (nm) | Sidewall Angle | Purpose |
|---|---|---|---|---|---|---|---|
| S01 | Isolated line | Resist on Si | 50 | — | 100 | 88° | Edge profile, CD bias |
| S02 | Isolated line | Resist on Si | 20 | — | 100 | 88° | Resolution test |
| S03 | Dense L/S 1:1 | Resist on Si | 15 | 30 | 60 | 87° | Pitch measurement |
| S04 | Dense L/S 1:3 | Resist on Si | 10 | 40 | 60 | 87° | Isolated vs. dense |
| S05 | Trench | SiO₂/Si | 30 | — | 50 | 89° | Trench profile |
| S06 | Contact hole | SiO₂ on Si | 30 (diameter) | — | 100 | 89° | Annular ring |
| S07 | FinFET fin | Si on SiO₂ | 8 | 30 | 40 | 90° | Narrow fin profile |
| S08 | Material boundary | Si / SiO₂ step | — | — | 50 | 90° | Material contrast |

### 2.2 Secondary Validation Structures

| ID | Structure | Purpose |
|---|---|---|
| S09 | Bi-material line (W on SiO₂) | Strong Z-contrast |
| S10 | DRAM capacitor array | Complex periodic structure |
| S11 | 70° sloped sidewall | Non-vertical edge test |

---

## 3. Ground-Truth Generation

### 3.1 Monte Carlo Reference

The primary ground truth will be generated using CASINO (or equivalent MC code):

| Parameter | Value | Notes |
|---|---|---|
| **Code** | CASINO V2.42+ or PENELOPE | Open-source, validated |
| **Number of trajectories** | $10^6$ per beam position | Converged to <1% statistical error |
| **Beam positions** | 51 positions across each edge | ±25 nm from edge, 1 nm step |
| **Materials** | All 6 target materials | Separate simulation per material |
| **Energy** | 1 keV (nominal) | Also 500 eV, 5 keV if time permits |
| **Output** | SE yield, BSE yield, angular distribution, radial SE distribution | |

### 3.2 Analytical Reference

For simple structures, analytical expressions provide the expected behavior:

| Structure | Analytical Expectation |
|---|---|
| Flat surface | $I = G \cdot [\delta_0 \eta_{\text{coll,SE}} + \eta \eta_{\text{coll,BSE}}] + I_{\text{off}}$ |
| Isolated line (wide) | Two peaks at edges, flat top with $I_{\text{top}} = I_{\text{flat}}$ |
| Step edge (infinitely sharp) | Blurred error function: $I(x) = A \cdot \text{erf}(x / \sigma\sqrt{2})$ |

### 3.3 Literature Reference

Published CD-SEM profiles from:
- Villarrubia et al. (NIST, 2004) [J1] — edge profiles for Si lines
- Bunday et al. (SPIE, 2003) [J6] — CD-SEM measurement methodology
- Archie (AIP, 2005) [J2] — CD metrology fundamentals

---

## 4. Metrics

### 4.1 Quantitative Metrics

| Metric | Symbol | Definition | Target | Structure |
|---|---|---|---|---|
| **Edge position error** | $\Delta x_{\text{edge}}$ | |Distance between simulated and reference edge position| | $< 0.5$ nm | S01–S08 |
| **CD bias** | $\Delta\text{CD}$ | CD$_{\text{sim}} -$ CD$_{\text{input}}$ | $< 1.0$ nm | S01, S03, S04 |
| **Peak position error** | $\Delta x_{\text{peak}}$ | Distance between simulated and reference peak | $< 0.5$ nm | S01, S02 |
| **Peak amplitude error** | $\Delta I_{\text{peak}}$ | |(I$_{\text{sim}} - I_{\text{ref}}) / I_{\text{ref}}$| | $< 20\%$ | S01, S05 |
| **Material contrast ratio** | $C_{\text{mat}}$ | $I_{\text{mat1}} / I_{\text{mat2}}$ (flat regions) | $\pm 20\%$ of MC | S08 |
| **Noise variance** | $\sigma^2$ | Variance vs. mean signal level | $\sigma^2 = \mu \cdot G_{\text{eff}}$ | All flat regions |
| **Edge rise distance (10–90%)** | $R_{10-90}$ | Distance from 10% to 90% of edge step | $\pm 20\%$ of expected | S01 |
| **SNR** | $I / \sigma$ | Measured SNR vs. theoretical | $\pm 2$ dB of theory | All flat |

### 4.2 Qualitative Metrics

| Aspect | Evaluation Method | Target |
|---|---|---|
| **Edge brightening** | Visual inspection of line profiles | Correct double-peak shape |
| **Material contrast** | Compare brightness of adjacent materials | Correct ordering (resist > SiO₂ > Si > Cu > W) |
| **Noise appearance** | Visual — "salt-and-pepper" texture | Realistic, signal-dependent |
| **Charging effect** | Insulator brightness reduction | Darker than MC without charging |
| **Overall realism** | Expert review | "Passable as real SEM image to non-expert" |

---

## 5. Acceptance Thresholds

### 5.1 Phase A (Core Contrast)

| Metric | Minimum | Target | Excellent |
|---|---|---|---|
| Edge position error (nm) | < 1.0 | < 0.5 | < 0.3 |
| Peak position error (nm) | < 1.0 | < 0.5 | < 0.3 |
| Material contrast ratio | Ordering correct | Within 30% of MC | Within 15% of MC |
| CD bias (nm) | < 2.0 | < 1.0 | < 0.5 |

### 5.2 Phase B (With Blur + Noise)

| Metric | Minimum | Target | Excellent |
|---|---|---|---|
| Edge rise distance | Within 50% of expected | Within 30% | Within 20% |
| SNR vs. theory | Within 5 dB | Within 3 dB | Within 2 dB |
| Noise variance ratio | $\sigma^2/\mu \in [0.5, 2.0]$ | $\sigma^2/\mu \in [0.8, 1.2]$ | $\sigma^2/\mu \in [0.9, 1.1]$ |

### 5.3 Phase C (With Charging)

| Metric | Minimum | Target | Excellent |
|---|---|---|---|
| Insulator brightness reduction | Visible effect | Factor consistent with $f_c$ | Factor matches MC |
| Saturation behavior | Peaks clip | Correct clipping at $I_{\text{max}}$ | No post-clip artifacts |

---

## 6. Validation Protocol

### 6.1 Per-Module Unit Tests

| Module | Test Input | Expected Output | Test Type |
|---|---|---|---|
| **Geometry** | Flat surface | $\theta = 0$ everywhere | Pass/fail |
| **Geometry** | 45° sloped surface | $\theta = 45°$ | Numeric within 0.1° |
| **Material** | Material ID 0 (Si) | $\delta_0 = 0.85$, $\eta = 0.18$ | Exact match |
| **Yield** | $\theta = 0°, \delta_0 = 1.0$ | $\delta = 1.0$ | Exact match |
| **Yield** | $\theta = 60°, \delta_0 = 1.0$ | $\delta = 2.0$ ($\sec 60° = 2.0$) | Numeric within 0.001 |
| **Yield** | $\theta = 80°$ (clamped) | $\delta = \delta_0 \sec 70°$ | Numeric within 0.001 |
| **PSF** | Gaussian blur of unit impulse | Expected Gaussian output | Numeric within 1% |
| **Noise** | Constant input $I$ | $\sigma = \sqrt{I/G_{\text{eff}}}$ | Statistical within 5% |
| **Digitization** | $I = V_{\text{max}}$, 16-bit | $I_{\text{pixel}} = 65535$ | Exact match |
| **Digitization** | $I = 0$, 16-bit | $I_{\text{pixel}} = 0$ | Exact match |

### 6.2 End-to-End Tests

| Test | Structures | Metrics | Frequency |
|---|---|---|---|
| Contrast correctness | S08 (material boundary) | Contrast ratio | Every build |
| Edge profile shape | S01 (50 nm line) | Edge position, CD bias | Every build |
| Resolution | S02 (20 nm line) | Peak separation | Every build |
| Noise statistics | Flat Si | SNR, variance | Every build |
| Charging | SiO₂ flat | Brightness reduction | Phase C+ |
| Frame averaging | S01 | SNR improvement $\propto \sqrt{N}$ | Phase D+ |

### 6.3 Comparison Protocol

```
For each reference structure:
  1. Generate input geometry (height map + material ID map)
  2. Run simulator → output image
  3. Extract 1D line profiles at specified positions
  4. Compute metrics vs. reference:
     - Edge positions (threshold 50%)
     - Peak positions (local maximum)
     - Contrast ratios (flat regions)
     - Noise variance (flat regions)
  5. Compare against acceptance thresholds
  6. Report pass/fail for each metric
```

---

## 7. Version Tracking

| Version | Simulator Version | Validation Date | Metrics File |
|---|---|---|---|
| Baseline | Phase A output | TBD | `validation/vA_results.csv` |
| With blur | Phase B output | TBD | `validation/vB_results.csv` |
| With degradation | Phase C output | TBD | `validation/vC_results.csv` |
| Final | Complete | TBD | `validation/vD_results.csv` |

---

## Sources

- [B1] L. Reimer, *Scanning Electron Microscopy*, 2nd ed. Springer, 1998.
- [J1] J. S. Villarrubia, A. E. Vladar, and M. T. Postek, "Scanning electron microscope measurement of width and shape of fabricated nanostructures," *J. Res. NIST*, vol. 109, 2004.
- [J2] C. N. Archie, "Critical dimension metrology," *AIP Conf. Proc.*, vol. 788, 2005.
- [J6] B. D. Bunday et al., "CD-SEM metrology," *Proc. SPIE*, vol. 5038, 2003.
- [J9] D. Drouin et al., "CASINO V2.42," *Scanning*, vol. 29, 2007.
