# Engineering Conclusions for SEM Simulation

**Research Phase:** 2.2
**Document:** 07_engineering_conclusions.md
**Date:** 2026-07-30

---

## 1. Purpose

This document classifies every interaction mechanism from Phase 2.2 into one of three categories:

| Category | Meaning | Action |
|---|---|---|
| **Essential** | Must be modeled for physically realistic SEM simulation | Build into core physics engine |
| **Useful background** | Improves accuracy or understanding but not required for first implementation | Add in later iterations if needed |
| **Can be safely ignored** | Negligible impact on semiconductor inspection simulation | Document for completeness; do not implement |

---

## 2. Classification Criteria

The classification uses the following criteria:

**Essential:**
- The mechanism directly determines the number or spatial distribution of detected electrons.
- Without it, simulated images would be physically incorrect.
- The mechanism operates at the length scale of CD metrology (0.5–10 nm).

**Useful background:**
- The mechanism refines quantitative accuracy but the first-order behavior is captured by essential mechanisms alone.
- The mechanism operates at an intermediate scale (10–100 nm) where its effect is measurable but not dominant.

**Can be safely ignored:**
- The mechanism operates at a scale >100 nm (far larger than CD features).
- The signal strength is <1% of the primary signal.
- The mechanism is relevant only for non-imaging analytical modes.
- The mechanism is relevant only for non-semiconductor materials.

---

## 3. Classified Mechanisms

### 3.1 Fundamental Scattering Processes

| Mechanism | Classification | Justification |
|---|---|---|
| **Elastic scattering (Rutherford/Mott)** | **Essential** | Determines BSE generation and angular distribution; controls trajectory shape |
| **Inelastic scattering (Bethe slowing)** | **Essential** | Determines energy deposition profile; controls penetration depth |
| **Multiple scattering (plural regime)** | **Essential** | Dominant scattering regime for CD-SEM energies (500 eV–1.5 keV) |
| **Diffusion (thick sample)** | **Useful** | Relevant at higher energies (>5 keV); less important for low-voltage CD-SEM |
| **Single scattering (thin sample)** | **Useful** | Relevant for very thin films (<10 nm); not dominant for bulk wafer imaging |
| **Plasmon excitation** | **Useful** | Dominant energy loss mechanism in some materials; improves quantitative accuracy of energy loss modeling |

### 3.2 Generated Signals

| Signal | Classification | Justification |
|---|---|---|
| **SE-I generation** | **Essential** | Primary information carrier for CD-SEM; determines spatial resolution |
| **SE-II generation** | **Essential** | Contributes significant SE signal at pattern edges; important for line profile shape |
| **SE-III** | **Can be ignored** | Adds uniform background only; does not affect relative contrast |
| **BSE generation (elastic)** | **Essential** | Determines compositional contrast; needed for voltage contrast modeling |
| **BSE low-loss (near $E_0$)** | **Useful** | Carries higher resolution than bulk BSE; refinements for surface sensitivity |
| **Auger electrons** | **Can be ignored** | Signal too weak (<0.1% of SE yield) to affect grayscale imaging |
| **Characteristic X-rays** | **Can be ignored** | Only relevant for EDS; spatial resolution far too coarse for CD imaging |
| **Bremsstrahlung** | **Can be ignored** | Only relevant for EDS background; no imaging information |
| **Cathodoluminescence** | **Can be ignored** | Negligible from Si and most semiconductor materials; only relevant for optoelectronics |
| **Specimen current** | **Can be ignored** | Complementary to SE/BSE; lower resolution; not used for CD imaging |
| **Transmitted electrons** | **Can be ignored** | Wafers are bulk (not electron-transparent) |

### 3.3 SE Physics

| Mechanism | Classification | Justification |
|---|---|---|
| **SE energy distribution** | **Essential** | Determines escape probability (via IMFP energy dependence) |
| **SE escape depth (IMFP)** | **Essential** | Determines which SEs reach the surface; controls resolution |
| **SE yield $\delta$ (magnitude)** | **Essential** | Determines signal strength and material contrast |
| **SE angular distribution (cosine)** | **Essential** | Determines collection efficiency variation with topography |
| **$\sec\theta$ angular dependence of $\delta$** | **Essential** | The physical origin of topographic contrast; must be modeled |
| **SE energy dependence of $\delta(E)$** | **Essential** | Determines optimal operating voltage; needed for multi-voltage simulation |
| **SE-I vs. SE-II ratio** | **Essential** | Determines resolution and signal profile shape at edges |
| **Material dependence of $\delta$** | **Essential** | Determines grayscale contrast between different materials |
| **Surface contaminant effects on $\delta$** | **Useful** | Can affect absolute yield but relative contrast is the main concern for CD |
| **Crystallographic orientation effects** | **Useful** | Channeling contrast in crystalline materials; minor for most semiconductor structures |
| **SE temperature dependence** | **Can be ignored** | Wafers are at ambient temperature; negligible effect |

### 3.4 BSE Physics

| Mechanism | Classification | Justification |
|---|---|---|
| **BSE yield $\eta$ (Z-dependence)** | **Essential** | Foundation of compositional contrast |
| **BSE energy distribution** | **Essential** | Determines SE-II generation; affects detector response |
| **BSE angular distribution** | **Essential** | Determines collection efficiency and signal distribution |
| **BSE escape depth** | **Essential** | Determines resolution and subsurface sensitivity |
| **BSE energy dependence of $\eta(E)$** | **Essential** | Required for multi-voltage modeling |
| **BSE low-loss component** | **Useful** | Improves high-resolution surface sensitivity |
| **BSE at very low energies (<500 eV)** | **Useful** | Characterized by Joy model; Reimer formula loses accuracy |
| **BSE crystallographic channeling** | **Useful** | Orientation contrast in crystalline materials; minor for fine-grained or amorphous regions |
| **BSE magnetic contrast (Type-I, Type-II)** | **Can be ignored** | Relevant only for magnetic materials |

### 3.5 Material Properties

| Property | Classification | Justification |
|---|---|---|
| **Atomic number / composition** | **Essential** | Required for all scattering calculations |
| **Material density** | **Essential** | Required for Bethe range and interaction volume |
| **Work function / electron affinity** | **Essential** | Required for SE escape probability |
| **Mean ionization potential $J$** | **Essential** | Required for Bethe stopping power |
| **Band gap** | **Essential** | Required for charging modeling (later phase); affects SE yield |
| **Plasmon energy** | **Useful** | Improves energy loss distribution accuracy |
| **Elastic constants (crystallinity)** | **Useful** | Needed for channeling contrast if modeling single-crystal substrates |
| **Thermal conductivity** | **Can be ignored** | Relevant for beam damage modeling (later phase) |
| **Optical constants / dielectric function** | **Useful** | Needed for advanced energy loss modeling (dielectric theory) |

### 3.6 Interaction Volume Geometry

| Aspect | Classification | Justification |
|---|---|---|
| **Penetration depth vs. energy** | **Essential** | Determines sampling volume; varies with material |
| **Lateral spread of interaction** | **Essential** | Determines BSE resolution and SE-II generation region |
| **Shape (teardrop vs. hemispherical)** | **Essential** | Characteristic shape determines signal distribution |
| **Energy deposition profile** | **Essential** | Determines SE generation profile |
| **Monte Carlo trajectory modeling** | **Essential** | The correct approach for computing interaction effects |
| **CSDA (continuous slowing down)** | **Essential** | Foundation for mean energy loss calculation |

### 3.7 Interaction Parameters

| Parameter | Classification | Justification |
|---|---|---|
| **Accelerating voltage** | **Essential** | Primary control over all interaction effects |
| **Beam incident angle** | **Essential** | Controls SE yield via $\sec\theta$; determines topographic contrast |
| **Material composition (local)** | **Essential** | Determines local yield; must be sampled per-pixel |
| **Surface geometry (local slope)** | **Essential** | Determines local SE yield; must be derived from 3D structure |
| **Feature size / proximity** | **Essential** | Determines SE-II background from nearby features |
| **Bulk vs. thin-film configuration** | **Essential** | Affects energy deposition and scattering in layered stacks |

---

## 4. Summary: What a Physics Simulator Must Include

For a physically realistic SEM image formation simulator, the following are the **minimum essential mechanisms**:

### Core Physics Engine (Required)

```
1. Elastic scattering (Mott cross-sections)
   - Determines BSE generation and trajectory shape
   - Z-dependent, energy-dependent
   - Required for all materials

2. Inelastic scattering (Bethe stopping power or modified)
   - Determines energy deposition profile
   - Z-dependent, energy-dependent
   - Provides the basis for SE generation

3. SE-I generation and escape
   - Generated along the primary trajectory
   - Escape probability governed by IMFP (universal curve)
   - Energy distribution (Chung-Everhart model)
   - Yield magnitude (material-dependent)

4. SE-II generation and escape
   - Generated by BSEs exiting the surface
   - Extends signal generation region laterally
   - Important for correct line profile shape

5. BSE generation
   - Elastic backscattering yield (Z-dependent)
   - Energy and angular distribution
   - Escape depth ~0.3× Bethe range

6. Material property library
   - Z, density, work function, mean ionization potential
   - Per-material SE and BSE yields

7. Geometry-dependent yield modulation
   - Local angle (secθ dependence for SE)
   - Composition boundaries (material assignment)
```

### Refinements (Add in Later Iterations)

```
8. Low-energy BSE model (Joy model)
   - For accurate η at <5 keV energies

9. Plasmon loss structure
   - Improves energy loss distribution accuracy

10. Crystallographic channeling
    - Minor effect for most semiconductor patterns
```

### Excluded (Do Not Implement)

```
11. Auger emission
12. X-ray generation (characteristic + bremsstrahlung)
13. Cathodoluminescence
14. Specimen current as primary signal
15. Transmitted electrons
16. SE-III background
```

---

## 5. Physical Accuracy Requirements

### 5.1 Energy Range

The simulation must be valid for $E_0 = 300$ eV to 30 keV, with primary focus on **500 eV–1.5 keV** (CD-SEM range).

### 5.2 Spatial Resolution

- The simulation must capture effects at the **1 nm scale** (typical CD-SEM pixel size).
- SE-I localization: ~1–2 nm.
- BSE lateral extent: up to 1 μm.
- The simulation must span from single-nanometer to micron scales.

### 5.3 Yield Accuracy

For the simulation to be useful for CD metrology modeling:

| Parameter | Required Accuracy | Achievable |
|---|---|---|
| SE yield (relative, material-to-material) | ±20% | Literature ±10–30% |
| BSE yield (absolute) | ±10% | Empirical formulas ±5–15% |
| SE angular dependence | Qualitative | Well-established $\sec\theta$ |
| SE/BSE energy distribution | Qualitative | Well-established shapes |

**Fact:** Absolute yield values are not critical for most CD-SEM applications because the image brightness and contrast are adjusted by the operator. What matters is the **relative yield variation** across the sample — which determines the grayscale contrast in the image.

### 5.4 Recommended Simulation Approach

| Approach | Advantages | Disadvantages | Recommendation |
|---|---|---|---|
| Full Monte Carlo (CASINO, PENELOPE) | Most physically accurate | Computationally expensive per pixel | Ground truth reference; offline precomputation |
| Analytical model (yield functions) | Fast, suitable for real-time | Less accurate for complex geometries | Core approach for renderer |
| Hybrid (MC precomputed + analytical) | Best balance of speed and accuracy | Implementation complexity | **Recommended approach** |

---

## 6. Conclusion

The engineering analysis identifies **seven core physical mechanisms** that must be included in any physics-based SEM simulator for semiconductor inspection:

1. Elastic scattering (Mott)
2. Inelastic scattering (Bethe/CSDA)
3. SE-I generation and escape
4. SE-II generation
5. BSE generation (Z-dependent)
6. Material property library
7. Geometry-dependent yield modulation (local angle effect)

All other mechanisms can be added as refinements or ignored entirely, as documented in this section.

---

## Sources

- L. Reimer, *Scanning Electron Microscopy: Physics of Image Formation and Microanalysis*, 2nd ed. Springer, 1998.
- J. I. Goldstein, D. E. Newbury, J. R. Michael, et al., *Scanning Electron Microscopy and X-Ray Microanalysis*, 4th ed. Springer, 2017.
- D. C. Joy, *Monte Carlo Modeling for Electron Microscopy and Microanalysis*. Oxford University Press, 1995.
- D. Drouin, A. R. Couture, D. Joly, et al., "CASINO V2.42," *Scanning*, vol. 29, 2007.
- H. Seiler, "Secondary electron emission in the scanning electron microscope," *J. Appl. Phys.*, vol. 54, 1983.
- R. F. Egerton, *Physical Principles of Electron Microscopy*, 2nd ed. Springer, 2016.
