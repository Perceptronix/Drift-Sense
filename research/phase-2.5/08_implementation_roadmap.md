# Implementation Roadmap

**Research Phase:** 2.5
**Document:** 08_implementation_roadmap.md
**Date:** 2026-07-30

---

## 1. Overview

The implementation is divided into four phases, each producing a working renderer with increasing realism. Each phase is independently testable and provides value on its own.

| Phase | Name | Output | Dependencies | Estimated Complexity |
|---|---|---|---|---|
| **A** | Core Contrast Renderer | Noiseless, sharp SE image with material and topographic contrast | None | Low |
| **B** | Physics Enhancements | Blurred image with SE-II, PSF, and basic noise | Phase A | Moderate |
| **C** | Full Degradation | Image with charging, PMT noise, saturation | Phase B | Moderate |
| **D** | Performance & Validation | Multi-configuration, validation suite | Phase C | Low–Moderate |

---

## 2. Phase A: Core Contrast Renderer

### 2.1 Objective

Produce a noiseless, sharp, physically-correct grayscale image showing:
- Material contrast (different $\delta_0$, $\eta$ per material)
- Topographic contrast ($\sec^\gamma\theta$ at edges)
- Correct edge brightening (bright peaks at sidewalls)
- Correct relative brightness between different materials

### 2.2 Pipeline Stages

```
1. Geometry Loading       (geometry → height field + material ID map)
2. Material Assignment    (material ID → δ₀, η, γ, Λ, f_c)
3. Surface Normal Calc.   (height field → surface normals → θ map)
4. SE Yield               (δ = δ₀ · secᵞ(θ), clamped)
5. BSE Yield              (η lookup from material library)
6. Detector Collection    (constants: η_coll_SE = 0.7, η_coll_BSE = 0.5)
8. Raw Pixel Intensity    (I = G · [δ · η_coll_SE + η · η_coll_BSE])
11. Gain Scaling & Offset (I_scaled = I · G + I_off)
14. ADC Digitization      (round + clamp → 16-bit output)
```

### 2.3 What Is Omitted

- SE-II background (Phase B)
- Probe PSF / blur (Phase B)
- Charging correction (Phase C)
- Shot noise (Phase C)
- PMT excess noise (Phase C)
- Frame averaging (Phase D)

### 2.4 Input Format

Simplified input for Phase A:
- **Height map:** CSV or image file, 1 channel per pixel (height in nm).
- **Material ID map:** Image file, 1 channel per pixel (integer 0–5).

Or: a single file encoding both (e.g., PNG with height as 16-bit value and material ID in separate metadata).

### 2.5 Output Format

- **16-bit grayscale TIFF** or PNG.
- Pixel size metadata embedded in file.
- No compression (lossless only).

### 2.6 Dependencies

- Geometry loading/validation
- Material library (table lookup)
- Basic math library (trig, clamping)

### 2.7 Validation

| Test Case | Expected Behavior |
|---|---|
| **Flat Si surface** | Uniform grayscale value from $\delta_0$ |
| **Flat SiO₂ on Si** | Brighter oxide region due to higher $\delta_0$ |
| **Isolated line (Si)** | Two bright edge peaks, flat top |
| **Isolated trench (Si)** | Two bright edge peaks, dark bottom |
| **Contact hole (SiO₂)** | Bright annulus, dark center |
| **FinFET fin** | Very bright narrow peaks |

### 2.8 Acceptance Criteria

1. Material contrast ratios match literature values (±20% relative).
2. Edge peak positions correspond to physical feature edges.
3. $\sec\theta$ behavior produces correct edge brightening pattern.
4. No artifacts, no unphysical values.

---

## 3. Phase B: Physics Enhancements

### 3.1 Objective

Add blur and realistic signal physics:
- Probe PSF convolution (Gaussian blur)
- Material-dependent escape depth (position-dependent blur)
- SE-II background (exponential convolution)
- Basic shot noise (Poisson)

### 3.2 New Pipeline Stages

```
Add between Phase A stages 11 and 14:
  7. SE-II Background      (exp convolution of η map)
  9. Probe PSF Convolution  (Gaussian blur with σ_eff)
  12. Shot Noise            (Poisson per pixel)
```

### 3.3 What Is Added

| Feature | Implementation | Effect on Image |
|---|---|---|
| **Gaussian probe PSF** | Convolve with kernel $\sigma_p = d_p/2.355$ | Blurs edges, reduces peak height |
| **Escape depth PSF** | Per-material $\sigma_m = \Lambda/2.355$, added in quadrature | Additional blur on insulators |
| **SE-II background** | $\eta$ convolved with exponential kernel | Low-intensity halo around bright features |
| **Shot noise** | Poisson($I/G_{\text{eff}}$) · $G_{\text{eff}}$ per pixel | Signal-dependent noise |

### 3.4 Dependencies

- Phase A renderer working and verified
- PSF kernel generation
- 2D convolution implementation
- Poisson random number generator
- $\Lambda$ (escape depth) values in material library

### 3.5 Validation

| Test Case | Expected Behavior |
|---|---|
| **Phase A test cases** | Same edge positions but blurred |
| **Edge profile width** | 10–90% rise distance ≈ 1.5–3 nm (probe + escape depth) |
| **SE-II halo** | Low-intensity tail outside edge peaks |
| **Shot noise on flat surface** | $\sigma(I) \propto \sqrt{I}$, verified by statistics |

### 3.6 Acceptance Criteria

1. Edge profile widths match expected values from probe diameter + escape depth.
2. Noise magnitude matches Poisson statistics ($\sigma^2 = \mu$ in electron units).
3. SE-II background visible and correctly parameterized.

---

## 4. Phase C: Full Degradation

### 4.1 Objective

Add all remaining degradation mechanisms:
- Charging correction (insulator yield reduction)
- PMT excess noise
- Detector saturation (clipping)

### 4.2 New Pipeline Stages

```
Add between Phase B stages 9 and 11:
  10. Charging Correction    (δ_eff = δ · f_c for insulators)

Modify Phase B stage 12 → 12+13:
  12. Shot Noise             (Poisson step)
  13. PMT Excess Noise       (variance scaling)
  14. ADC Digitization       (with saturation: clamp before quantize)
```

### 4.3 What Is Added

| Feature | Implementation | Effect on Image |
|---|---|---|
| **Charging correction** | Multiply SE yield by $f_c$ for insulators | Darker SiO₂, resist regions |
| **PMT excess noise** | Add $\sqrt{(F^2-1) \cdot I \cdot G_{\text{eff}}} \cdot \mathcal{N}(0,1)$ | ~20% more noise |
| **Detector saturation** | Clamp $I$ to $V_{\text{max}}$ before ADC | Flat-topped bright peaks at high gain |

### 4.4 Dependencies

- Phase B renderer working and verified
- $f_c$ (charging factor) values in material library
- $F$ (excess noise factor) parameter

### 4.5 Validation

| Test Case | Expected Behavior |
|---|---|
| **Phase B test cases** | Slightly darker insulators, same otherwise |
| **SiO₂ flat region** | Reduced brightness compared to Phase B (charging factor applied) |
| **High-gain imaging** | Edge peaks saturate (flat tops) |
| **Noise variance** | Slightly higher than pure Poisson |

### 4.6 Acceptance Criteria

1. Insulators appear realistically darker than conductors.
2. Saturation behavior is correct.
3. Overall noise level is ~20% higher than pure Poisson.

---

## 5. Phase D: Performance and Flexibility

### 5.1 Objective

Make the renderer fully configurable and validated:
- Support all configurable parameters (energy, current, diameter, dwell, etc.)
- Multiple operating scenarios (predefined parameter sets)
- Frame averaging simulation
- Output in industry-standard formats
- Validation suite against Monte Carlo reference

### 5.2 New Features

| Feature | Implementation |
|---|---|
| **Multi-scenario support** | Predefined configs: high-res CD, standard CD, fast inspection, etc. |
| **Frame averaging** | Render N frames with independent noise → average |
| **Validation suite** | Scripted comparison vs. CASINO Monte Carlo |
| **Parameter file loading** | JSON or YAML config files |
| **Output formats** | TIFF 16-bit, PNG 8-bit, CSV profiles |

### 5.3 Dependencies

- Phase C renderer working and verified
- CASINO Monte Carlo simulation results for reference structures
- Validation test cases defined

### 5.4 Validation Matrix

| Scenario | $E_0$ | $I_P$ | $d_p$ | $\tau$ | $\Delta x$ | Validation Target |
|---|---|---|---|---|---|---|
| High-res CD | 1 keV | 15 pA | 1.0 nm | 2 μs | 0.5 nm | CASINO line/space |
| Standard CD | 1 keV | 15 pA | 1.0 nm | 1 μs | 1.0 nm | CASINO line/space |
| Fast inspect | 1 keV | 50 pA | 1.5 nm | 0.5 μs | 2.0 nm | Literature profiles |
| High-voltage | 5 keV | 100 pA | 2.0 nm | 1 μs | 1.0 nm | CASINO (if available) |

---

## 6. Summary Timeline

```
Phase A: Core Contrast Renderer
├── Geometry module
├── Material library
├── Yield engine
├── Pixel intensity
├── Digitization
└── Validate: line/space, contact, material contrast

Phase B: Physics Enhancements
├── PSF module (Gaussian convolution)
├── Escape depth (material-dependent blur)
├── SE-II background
├── Shot noise (Poisson)
└── Validate: edge profiles, noise statistics

Phase C: Full Degradation
├── Charging module
├── PMT excess noise
├── Detector saturation
└── Validate: charging effects, saturation

Phase D: Performance & Validation
├── Multi-scenario configs
├── Frame averaging
├── Parameter file I/O
├── Validation suite vs Monte Carlo
└── Documentation
```

---

## 7. Dependency Graph

```
Phase A     Phase B     Phase C     Phase D
┌───────┐   ┌───────┐   ┌───────┐   ┌───────┐
│ Geom  │──▶│ PSF   │──▶│Charge │──▶│Config │
└───────┘   └───────┘   └───────┘   └───────┘
┌───────┐   ┌───────┐   ┌───────┐   ┌───────┐
│ MatLib│──▶│ SE-II │──▶│Excess │──▶│Averag │
└───────┘   └───────┘   └───────┘   └───────┘
┌───────┐   ┌───────┐   ┌───────┐   ┌───────┐
│Yield  │──▶│ Noise │──▶│Sat/ADC│──▶│Valida │
└───────┘   └───────┘   └───────┘   └───────┘
     │           │           │           │
     ▼           ▼           ▼           ▼
   Image A     Image B     Image C     Image D
```

Each phase builds on the previous. The architecture allows independent testing at each stage.

---

## Sources

- [B1] L. Reimer, *Scanning Electron Microscopy: Physics of Image Formation and Microanalysis*, 2nd ed. Springer, 1998.
- [B2] J. I. Goldstein, D. E. Newbury, J. R. Michael, et al., *Scanning Electron Microscopy and X-Ray Microanalysis*, 4th ed. Springer, 2017.
- [J1] J. S. Villarrubia, A. E. Vladar, and M. T. Postek, "Scanning electron microscope measurement of width and shape of fabricated nanostructures," *J. Res. NIST*, vol. 109, 2004.
- [J6] B. D. Bunday et al., "CD-SEM metrology," *Proc. SPIE*, vol. 5038, 2003.
