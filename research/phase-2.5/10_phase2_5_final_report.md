# Phase 2.5 Final Report: The Canonical SEM Simulator Specification

**SEMICON 2026 Research Repository**
**Applied Materials**
**Date:** 2026-07-30
**Classification:** Research-Only (Phase 2.5)

---

## Executive Summary

Phase 2.5 answers the engineering question: **"What exactly will our SEM simulator implement?"**

This is the definitive specification document. All parameters are frozen. All mathematical models are selected. The rendering pipeline is designed. The module architecture is specified. The assumptions are documented. The implementation roadmap is laid out.

**This specification is the bridge between physics research and software implementation.** Every decision is justified by literature (38 cited sources), by inference from established physics, or by an explicit engineering decision when the literature does not uniquely determine the choice.

---

## 1. Phase Results by Document

### 1.1 Frozen Physical Parameters (Document 02)

| Category | Count | Key Parameters |
|---|---|---|
| **Fixed** | 18 | $e$, $k_B$, $\eta_{\text{coll}}^{\text{SE}}$, $F$, $V_{\text{range}}$, $\alpha$, $\Delta E$ |
| **Configurable** | 14 | $E_0$ (1 keV nominal), $I_P$ (15 pA), $d_p$ (1.0 nm), $\tau$ (1 μs), $\Delta x$ (1 nm) |
| **Material library** | 8/material | $\delta_0$, $\eta$, $\Lambda$, $f_c$, $\gamma$, type, $Z$, $L_{\text{SE-II}}$ |
| **Randomized** | 1 | Poisson noise per pixel |

Nominal operating point: 1 keV, 15 pA, 1.0 nm probe, 1 μs dwell, 1 nm pixel, TTL detection, 16-bit ADC.

### 1.2 Frozen Mathematical Models (Document 03)

| Phenomenon | Model | Key Parameters |
|---|---|---|
| **SE yield (angular)** | $\delta(\theta) = \delta_0 \cdot \sec^\gamma\theta$, clamp $\theta > 70^\circ$ | $\gamma=1.0$ |
| **BSE yield** | Reimer formula + Joy energy correction | $Z$, $E_0$ |
| **Pixel intensity** | Linear combination: $I = G[\delta \sec^\gamma\theta \cdot \eta_{\text{coll}}^{\text{SE}} + \eta \cdot \eta_{\text{coll}}^{\text{BSE}} + I_{\text{SE-II}}] + I_{\text{off}}$ | Per-pixel |
| **Probe PSF** | Gaussian with $\sigma_p = d_p / 2.355$ | $d_p$ |
| **Escape depth blur** | Gaussian added in quadrature: $\sigma_m = \Lambda / 2.355$ | $\Lambda$ (material) |
| **SE-II background** | Exponential convolution of $\eta$ with decay length $L_{\text{SE-II}}$ | $L_{\text{SE-II}}$, $k_{\text{SE-II}}$ |
| **Shot noise** | Poisson($I / G_{\text{eff}}$) $\cdot G_{\text{eff}}$ | $I_P$, $\tau$, $\eta_{\text{coll}}$ |
| **PMT excess noise** | Variance scaling by $F^2$ | $F=1.2$ |
| **Charging** | $\delta_{\text{eff}} = \delta \cdot f_c$ for insulators | $f_c \in [0.3,0.8]$ |
| **Digitization** | Linear ADC with saturation, $N_{\text{bits}} = 16$ | $N_{\text{bits}}$, $V_{\text{max}}$ |

### 1.3 Canonical Rendering Pipeline (Document 04)

14 stages in 4 phases:

| Pipeline Phase | Stages | Purpose |
|---|---|---|
| **Pre-processing** | 1–3 | Geometry → normals → angles |
| **Signal generation** | 4–8 | Yields → intensity (deterministic physics) |
| **Degradation** | 9–13 | Blur → noise (stochastic) |
| **Digitization** | 14 | ADC → final image |

Ordering justification: deterministic geometry → deterministic physics → stochastic physics → electronic processing. Blur before noise (physically correct).

### 1.4 Module Architecture (Document 05)

| Module | Input | Output | Core Equation |
|---|---|---|---|
| **Geometry** | Height file | Normals, $\theta$ map | $\theta = \arccos(\hat{n} \cdot \hat{z})$ |
| **Material Lib** | Material ID | $\delta_0$, $\eta$, $\Lambda$, $f_c$, $\gamma$, type, $Z$ | Table lookup |
| **Yield Engine** | $\delta_0$, $\theta$, $\gamma$ | $\delta$, $\eta$ maps | $\delta = \delta_0 \sec^\gamma\theta$ |
| **Detector** | $\hat{n}$, pixel pos | $\eta_{\text{coll}}^{\text{SE}}$, $\eta_{\text{coll}}^{\text{BSE}}$ | Constants (0.7, 0.5) |
| **PSF** | $I_{\text{raw}}$, $d_p$, $\Lambda$ | $I_{\text{blurred}}$ | $I * G(\sigma_{\text{eff}})$ |
| **Charging** | $\delta$, $f_c$, type | $\delta_{\text{eff}}$ | $\delta_{\text{eff}} = \delta \cdot f_c$ |
| **Noise** | $I$, $G_{\text{eff}}$, $F$ | $I_{\text{noisy}}$ | Poisson + excess |
| **Digitization** | $I$, ADC params | $I_{\text{pixel}}$ | Saturation + quantization |

### 1.5 Parameter Library (Document 06)

A canonical table of 50 parameters indexed by name, symbol, units, category (F/C/M/R), default value, valid range, source, and using module.

### 1.6 Assumptions and Limitations (Document 07)

| Category | Count of Assumptions | Key Simplification |
|---|---|---|
| **Physics** | 21 | Charging as constant factor ($f_c$); Gaussian probe; Poisson noise |
| **Geometry** | 3 | 2.5D only; no drift; aligned scan |
| **Numerical** | 5 | Sharp interfaces; constant $\eta_{\text{coll}}$; ideal ADC |
| **Ignored physics** | 10 | Diffraction, channeling, magnetic, thermal, X-rays, etc. |

All simplifications are justified for CD-SEM semiconductor imaging.

### 1.7 Implementation Roadmap (Document 08)

| Phase | Name | Key Added Capability | Validation |
|---|---|---|---|
| **A** | Core Contrast | Material + topographic contrast | Flat, line, trench, contact profiles |
| **B** | Physics Enhancement | PSF blur, SE-II, shot noise | Edge profile widths, noise stats |
| **C** | Full Degradation | Charging, PMT noise, saturation | Insulator brightness, noise level |
| **D** | Performance & Validation | Multi-config, Monte Carlo validation | Full scenario matrix |

---

## 2. Canonical Image Formation Equation

The complete forward model, in a single expression:

$$I_{\text{pixel}} = \text{round}\left( \min\left( \max\left( \frac{ \text{Poisson}\left( \frac{ G \cdot [\delta_0 \sec^\gamma\theta \cdot \eta_{\text{coll}}^{\text{SE}} + \eta \cdot \eta_{\text{coll}}^{\text{BSE}} + I_{\text{SE-II}}] * G(\sigma_{\text{eff}}) + I_{\text{off}} }{G_{\text{eff}}} \right) \cdot G_{\text{eff}} + \sqrt{(F^2-1)I_{\text{shot}}G_{\text{eff}}} \cdot \mathcal{N}(0,1) }{V_{\text{max}}}, 0 \right), 1 \right) \cdot (2^{N_{\text{bits}}} - 1) \right)$$

where:
- $\delta_0$, $\eta$, $\Lambda$, $f_c$, $L_{\text{SE-II}}$ depend on material $Z$
- $\theta$ depends on local surface normal
- $\sigma_{\text{eff}}^2 = (d_p/2.355)^2 + (\Lambda/2.355)^2$
- $\eta_{\text{coll}}^{\text{SE}} = 0.7$, $\eta_{\text{coll}}^{\text{BSE}} = 0.5$ (constants for TTL)
- Charging modifies $\delta$ by $f_c$ for insulating materials
- $*$ denotes convolution

---

## 3. Engineering Decisions Summary

| Decision | Choice | Rationale |
|---|---|---|
| **PSF model** | Gaussian | Matches Schottky FEG probe shape; efficient to compute |
| **Noise model** | Poisson + excess | Captures the dominant physics |
| **Charging model** | Constant factor | Lumps all charging effects into a single multiplier |
| **SE-II model** | Exponential convolution | Captures the dominant long-range signal |
| **Detector model** | Constant efficiency | Valid for small-FOV TTL imaging |
| **BSE angular dependence** | Neglected | Second-order effect for CD-SEM |
| **2.5D geometry** | Height map | Sufficient for CD-SEM targets |
| **Saturation** | Hard clip | Simple, physically correct |

---

## 4. Critical Unresolved Decisions

### 4.1 Geometry Input Format (Requires Resolution Before Coding)

The geometry input format is the **last unresolved specification**. Two options:

| Format | Pros | Cons |
|---|---|---|
| **2.5D height map** (single image: height per pixel + material ID map) | Simple; small file size; easy to generate from GDS + process simulation | No overhangs; limited 3D |
| **3D mesh** (triangle mesh with material labels) | Full 3D capability; industry standard | More complex; requires mesh generation pipeline |

**Recommendation:** Start with 2.5D height maps. Extend to 3D meshes in Phase D.

### 4.2 Validation Protocol (Requires Resolution Before Coding)

A reference set of test structures with known CDs must be defined:

| Structure | Material Stack | Nominal CD | Expected SEM Profile |
|---|---|---|---|
| Isolated line (CD 50 nm) | Resist on Si | Top CD 50 nm | Two peaks separated by ~50 nm |
| Dense L/S (pitch 40 nm) | Resist on Si | CD 20 nm | Periodic modulation |
| Contact hole | SiO₂ on Si | Diameter 30 nm | Annular ring |
| Si trench in SiO₂ | Si in SiO₂ | CD 30 nm | Bright edges, dark bottom |

---

## 5. Phase 2.5 Success Criteria

| Criterion | Status | Evidence |
|---|---|---|
| ✓ Frozen physical parameters | Achieved | Document 02 |
| ✓ Frozen mathematical models | Achieved | Document 03 |
| ✓ Canonical rendering pipeline | Achieved | Document 04 |
| ✓ Complete module architecture | Achieved | Document 05 |
| ✓ Parameter library | Achieved | Document 06 |
| ✓ Clear implementation roadmap | Achieved | Document 08 |
| ✓ Assumptions documented | Achieved | Document 07 |

---

## 6. Knowledge Required for Phase 2.6

Phase 2.5 freezes **what** the simulator will implement. Phase 2.6 must resolve **how** to implement it.

### 6.1 Decisions for Phase 2.6

1. **Geometry input format specification.** Define the exact file format for 2.5D height maps (or 3D meshes). Provide sample files for all standard structures.

2. **Validation protocol definition.** Define the reference test structures, the validation metrics (CD bias, edge position error, profile shape error), and the acceptance thresholds.

3. **Monte Carlo reference dataset.** Generate (or reference existing) CASINO simulation results for the 6 target materials at 1 keV, for simple structures. This provides ground truth for validation.

4. **Implementation language / platform selection.** Not a physics decision, but necessary for the implementation phase.

5. **Coordinate system convention.** Define the coordinate system (origin, axes, handedness) for geometry input.

### 6.2 What Phase 2.6 Should Produce

| Deliverable | Description | Format |
|---|---|---|
| **Geometry format spec** | Schema for 2.5D height map input | Technical document |
| **Test structure library** | 5+ geometry files with known CDs | Geometry files |
| **Validation protocol** | Metrics, thresholds, test cases | Technical document |
| **MC reference data** | CASINO profiles for validation | Data files + document |
| **Engineering implementation plan** | Language, libraries, testing framework | Technical document |

**This is the last phase before coding begins.**

---

## 7. Phase 2.5 Document Map

```
research/phase-2.5/
│
├── 01_executive_summary.md              ← The complete specification overview
├── 02_frozen_physical_parameters.md     ← 50+ parameters with categories and ranges
├── 03_frozen_mathematical_models.md     ← 10 selected models with justification
├── 04_canonical_rendering_pipeline.md   ← 14-stage pipeline with ordering rationale
├── 05_module_architecture.md            ← 8 modules with I/O specifications
├── 06_parameter_library.md              ← Canonical parameter table
├── 07_assumptions_and_limitations.md    ← 24 assumptions, 5 simplifications, 10 ignored effects
├── 08_implementation_roadmap.md         ← 4-phase plan from MVP to full validation
├── 09_complete_reference_list.md        ← 38 cited sources
└── 10_phase2_5_final_report.md          ← This consolidated report
```

---

*End of Phase 2.5 Final Report — End of Physics Research Line*
