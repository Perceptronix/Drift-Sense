# Phase 2.5 Executive Summary: The Canonical SEM Simulator Specification

**SEMICON 2026 Research Repository**
**Applied Materials**
**Date:** 2026-07-30
**Classification:** Research-Only (Phase 2.5)

---

## Purpose

This is the definitive engineering specification for the SEM image simulator. Every previous phase (2.1–2.4) established the physics of SEM image formation. This phase **freezes every parameter, model, and architectural decision** into a canonical specification that all future implementation must follow.

**Phase 2.5 does not generate code.** It produces the blueprints from which code will be built.

---

## Key Deliverables

| # | Document | What It Contains |
|---|---|---|
| 1 | Executive Summary | This overview |
| 2 | Frozen Physical Parameters | Voltage, current, probe, dwell time, materials, noise, charging — all with categories and ranges |
| 3 | Frozen Mathematical Models | SE yield, BSE contrast, topographic contrast, PSF, noise, charging — selected models with justification |
| 4 | Canonical Rendering Pipeline | 14-stage processing sequence with ordering justification |
| 5 | Module Architecture | 8 logical modules with responsibilities, inputs, outputs, interfaces |
| 6 | Parameter Library | 50+ parameters in canonical table format (name, symbol, units, range, default, source) |
| 7 | Assumptions and Limitations | 20+ documented assumptions, simplifications, and ignored physics |
| 8 | Implementation Roadmap | 4-phase plan from MVP to full simulator |
| 9 | Reference List | All cited sources |
| 10 | Final Report | Consolidated specification document |

---

## Frozen Parameter Summary (Core)

| Parameter | Symbol | Frozen Value | Category |
|---|---|---|---|
| Accelerating voltage | $E_0$ | 1 keV (nominal) | **Configurable** (500 eV–5 keV) |
| Probe current | $I_P$ | 15 pA (nominal) | **Configurable** (5–200 pA) |
| Probe diameter (FWHM) | $d_p$ | 1.0 nm (nominal) | **Configurable** (0.5–2.0 nm) |
| Pixel dwell time | $\tau$ | 1 μs (nominal) | **Configurable** (0.1–10 μs) |
| Pixel size | $\Delta x$ | 1 nm (nominal) | **Configurable** (0.5–2 nm) |
| SE yield (Si, 1 keV) | $\delta_0$ | 0.85 | **Fixed** (material library) |
| BSE yield (Si, 1 keV) | $\eta$ | 0.18 | **Fixed** (material library) |
| SE escape depth (Si) | $\Lambda$ | 2 nm | **Fixed** (material library) |
| PMT excess noise factor | $F$ | 1.2 | **Fixed** |

---

## Frozen Mathematical Model Summary

| Model | Selected Form | Key Parameters |
|---|---|---|
| **SE yield (angular)** | $\delta(\theta) = \delta_0 \cdot \sec^{\gamma}(\theta)$ | $\gamma = 1.0$ (baseline), material-modulated |
| **BSE yield** | $\eta(Z, E_0)$ from Reimer/Joy model | Z-dependent, energy-dependent |
| **Pixel intensity** | $I = G[ \delta_0 \sec^\gamma\theta \cdot \eta_{\text{coll}} + \eta \cdot \eta_{\text{coll,BSE}} + I_{\text{SE-II}} ]$ | Per-pixel linear combination |
| **Probe PSF** | Gaussian: $G(r) \propto \exp(-r^2 / 2\sigma^2)$ | $\sigma = d_p / 2.355$ |
| **Escape depth PSF** | Gaussian: added in quadrature to probe PSF | $\sigma_m = \Lambda / 2.355$ |
| **Noise** | Poisson (shot) + variance scaling (PMT excess) | $\sigma^2 \propto F^2 \cdot I$ |
| **Charging** | Effective SE yield reduction for insulators | $\delta_{\text{eff}} = \delta_0 \cdot f_c$, $f_c \in [0.3, 0.8]$ |

---

## Canonical Pipeline (14 Stages)

```
Geometry → Material Assignment → Surface Normals → SE/BSE Yield → 
Detector Collection → SE-II Background → Probe Convolution → 
Charging Correction → Pixel Integration → Gain Scaling → 
Shot Noise → Excess Noise → Digitization → Final Image
```

Justification for ordering: Processes proceed from deterministic geometry → deterministic physics → stochastic physics → electronic processing. This ordering ensures physically meaningful intermediate results.

---

## Module Architecture (8 Modules)

| Module | Responsibility | Core Equation |
|---|---|---|
| **Geometry** | Load/validate 3D structure, compute surface normals | Per-triangle normal |
| **Material** | Look up $\delta_0$, $\eta$, $\Lambda$, $f_c$ per material | Material ID → property vector |
| **Yield** | Compute per-pixel SE/BSE yield | $\delta(\theta) = \delta_0 \sec^\gamma\theta$ |
| **Detector** | Compute collection efficiency | $\eta_{\text{coll}}$ per pixel |
| **PSF** | Build and apply convolution kernels | Gaussian + optional exponential tail |
| **Charging** | Apply yield reduction to insulators | $\delta_{\text{eff}} = \delta_0 \cdot f_c$ |
| **Noise** | Generate Poisson/distribution | $I_{\text{noisy}} \sim \text{Poisson}(I/G) \cdot G$ |
| **Digitization** | Gain, offset, clipping, ADC | $I_{\text{pixel}} = \min(\max(I_{\text{noisy}},0), 2^N-1)$ |

---

## Implementation Phases

| Phase | Name | Modules | Timeline (estimate) |
|---|---|---|---|
| **A** | Core Contrast Renderer | Geometry, Material, Yield, Pixel intensity | Foundation |
| **B** | Physics Enhancements | SE-II, PSF convolution, basic noise | +1 increment |
| **C** | Full Degradation | Charging, PMT noise, saturation, digitization | +1 increment |
| **D** | Performance & Flexibility | Configurable parameters, multiple energies, validation tools | +1 increment |

---

## Phase 2.6 Knowledge Required

Before coding begins, two items require resolution:

1. **Geometry input format** — The 2.5D height map format must be specified (encoding of material IDs + heights + surface normals). A reference implementation or schema must be provided.

2. **Validation protocol** — A set of reference test cases (line/space at known CD, contact hole, material boundary) with expected outputs must be defined. Without validation, the renderer cannot be verified.

These are not physics decisions — they are engineering specifications that bridge specification and implementation.

---

## Sources

- L. Reimer, *Scanning Electron Microscopy: Physics of Image Formation and Microanalysis*, 2nd ed. Springer, 1998.
- J. I. Goldstein, D. E. Newbury, J. R. Michael, et al., *Scanning Electron Microscopy and X-Ray Microanalysis*, 4th ed. Springer, 2017.
- R. F. Egerton, *Physical Principles of Electron Microscopy*, 2nd ed. Springer, 2016.
- D. C. Joy, *Monte Carlo Modeling for Electron Microscopy and Microanalysis*. Oxford University Press, 1995.
- J. S. Villarrubia, A. E. Vladar, and M. T. Postek, "Scanning electron microscope measurement of width and shape of fabricated nanostructures," *J. Res. NIST*, vol. 109, 2004.
- M. T. Postek and A. E. Vladar, "Critical dimension metrology," in *Handbook of Semiconductor Manufacturing Technology*, CRC Press, 2007.
- D. Drouin, A. R. Couture, D. Joly, et al., "CASINO V2.42," *Scanning*, vol. 29, 2007.
- H. Seiler, "Secondary electron emission in the scanning electron microscope," *J. Appl. Phys.*, vol. 54, 1983.
- C. N. Archie, "Critical dimension metrology," *AIP Conf. Proc.*, vol. 788, 2005.
