# Engineering Conclusions for SEM Image Formation

**Research Phase:** 2.3
**Document:** 08_engineering_conclusions.md
**Date:** 2026-07-30

---

## 1. Purpose

This document classifies every image formation mechanism from Phase 2.3 into three categories based on its importance for building a synthetic SEM image simulator for semiconductor wafer inspection.

| Category | Meaning | Action |
|---|---|---|
| **Essential** | Must be modeled or the image is physically incorrect | Build into core renderer |
| **Useful background** | Improves accuracy but not required for first implementation | Add in later iterations |
| **Can be safely ignored** | Negligible impact on semiconductor SEM images | Document but do not implement |

---

## 2. Classification Criteria

**Essential:**
- The mechanism is required to produce the characteristic SEM appearance of semiconductor structures.
- Without it, the image would lack key features (edge brightening, material contrast, shadowing).
- The mechanism operates at the nanometer scale relevant to CD metrology.

**Useful:**
- The mechanism refines quantitative accuracy.
- The first-order behavior is captured by essential mechanisms alone.
- The mechanism affects secondary aspects (profile tail shape, asymmetry magnitude).

**Can be ignored (for first implementation):**
- The mechanism operates at scales irrelevant to semiconductor inspection.
- The signal contribution is <1% of the total image intensity.
- The effect is negligible for the structures and operating conditions considered.

---

## 3. Classified Mechanisms

### 3.1 Contrast Mechanisms

| Mechanism | Classification | Justification |
|---|---|---|
| **Topographic ($\sec\theta$)** | **Essential** | The single most important contrast mechanism; determines edge signal |
| **Material (Z-dependent SE yield)** | **Essential** | Determines baseline brightness differences between materials |
| **Material (Z-dependent BSE yield)** | **Essential** | Required for compositional contrast and voltage contrast |
| **Detector collection anisotropy** | **Essential** | Determines how emitted signal maps to detected signal |
| **Voltage contrast (BSE mode)** | **Useful** | Important for defect detection but not for primary CD metrology |
| **Shadowing (topographic blocking)** | **Useful** | Relevant for high-aspect-ratio structures (deep trenches, DRAM) |
| **Crystallographic channeling** | **Can be ignored** | Not relevant for amorphous/polycrystalline semiconductor films |
| **Magnetic contrast** | **Can be ignored** | Non-magnetic materials in semiconductor fabrication |
| **SE-III (chamber wall SE)** | **Can be ignored** | Uniform background; does not affect contrast |

### 3.2 Edge Brightening Components

| Component | Classification | Justification |
|---|---|---|
| **Geometric ($\sec\theta$) edge enhancement** | **Essential** | The dominant mechanism creating bright edges |
| **Sidewall SE-II contribution** | **Essential** | Broadens edge profile; affects CD measurement accuracy |
| **Probe convolution (finite beam size)** | **Essential** | Determines the spatial extent of edge peaks |
| **Corner effect (2D enhancement)** | **Useful** | Important for contact holes, vias, line ends |
| **Detector shadowing of deep features** | **Useful** | Reduces bottom signal in high-aspect-ratio features |
| **Material boundary contrast at edge** | **Useful** | Contributes to profile asymmetry |

### 3.3 Pixel Intensity Model Components

| Component | Classification | Justification |
|---|---|---|
| **SE yield $\delta_0(Z)$ per material** | **Essential** | Required for absolute signal level |
| **BSE yield $\eta(Z)$ per material** | **Essential** | Required for material contrast |
| **$\sec\theta$ angular factor** | **Essential** | Core topographic contrast model |
| **Probe current $I_P$ scaling** | **Essential** | Linear scaling of all signals |
| **Dwell time $\tau$ scaling** | **Essential** | Linear scaling |
| **System gain $G$** | **Essential** | User-controllable brightness |
| **Detector collection function** | **Essential** | Spatial variation of collection efficiency |
| **Background offset $B$** | **Essential** | Dark level reference |
| **SE-II spatial distribution** | **Useful** | Broadens edge profile tails |
| **SE energy distribution** | **Useful** | Affects detector collection details |
| **Monte Carlo correction for $\theta > 70^\circ$** | **Useful** | $\sec\theta$ overestimates yield at extreme angles |

### 3.4 Line/Space Profile Components

| Component | Classification | Justification |
|---|---|---|
| **Edge peak positions (edges)** | **Essential** | Determines measured CD |
| **Edge peak amplitude** | **Essential** | Determines contrast for edge detection |
| **Edge peak width (probe convolution)** | **Essential** | Determines resolution |
| **Flat-surface background level** | **Essential** | Reference for contrast ratio |
| **Top surface signal level** | **Essential** | Determines peak-to-valley ratio |
| **SE-II tail width** | **Useful** | Broadens peak base |
| **Sidewall angle-dependent amplitude** | **Useful** | Affects peak height variation |

### 3.5 Detector Models

| Detector Type | Classification | Justification |
|---|---|---|
| **TTL (in-lens) SE detector** | **Essential** | Primary detector for CD-SEM |
| **Annular solid-state BSE detector** | **Essential** | Secondary detector for material/VC imaging |
| **Everhart-Thornley (side-mounted)** | **Useful** | Common in general-purpose SEMs; less common in CD-SEM |
| **In-lens energy filter** | **Useful** | Allows SE/BSE separation |

### 3.6 Contrast Model Selection

| Model Choice | Classification | Justification |
|---|---|---|
| **$\sec\theta$ + detector + combined SE/BSE** | **Essential** | Recommended forward model |
| **Hybrid MC + analytical** | **Useful** | Ground-truth validation |
| **Empirical erf + Gaussian** | **Useful** | For CD metrology algorithm testing |
| **Lambertian / Phong** | **Can be ignored** | Physically wrong for SE emission |

---

## 4. Summary: Essential Components for a Synthetic SEM Simulator

### 4.1 Absolute Minimum (Phase 1 Implementation)

```
1. Material property library
   - δ₀(Z) — SE yield at normal incidence
   - η(Z) — BSE yield
   - Per material

2. Secθ topographic contrast
   - I_SE(θ) = δ₀ · secθ(θ_local)
   - For all surface elements

3. BSE material contrast
   - I_BSE(Z) = η(Z)
   - Per material region

4. Gaussian probe convolution
   - Convolve yield map with beam profile
   - σ = f(probe diameter)

5. Basic pixel equation
   - I(x,y) = G · [I_SE(x,y) + I_BSE(x,y)] + offset
```

**This minimum captures:** edge brightening, topographic contrast, material contrast, and finite resolution.

### 4.2 Recommended Full Implementation

```
Add to the minimum:

6. Detector collection function
   - η_coll(x,y) for TTL detector
   - Position-dependent collection efficiency

7. SE-II contribution
   - Background from BSE exiting the surface
   - Convolution with ~1 μm kernel

8. SE yield saturation correction for θ > 70°
   - Modified secθ to prevent unphysical yield values

9. Multiple material boundary handling
   - Smooth transition at material boundaries
   - Mixed signals from interfacial regions
```

### 4.3 Future Enhancement (Later Phase)

```
10. Probe position-dependent effects (scan coil)
11. Asymmetric detector collection (E-T mode)
12. Voltage contrast model (BSE VC)
13. Corner effect enhancement factor (2D geometry)
```

---

## 5. Accuracy Requirements

For a synthetic SEM image generator intended for CD metrology algorithm development, the following accuracies are sufficient:

| Quantity | Required Accuracy | Achievable with Recommended Model |
|---|---|---|
| **Edge peak position** | ±0.5 nm | Yes (with correct geometry + probe convolution) |
| **Edge peak amplitude** | ±20% | Yes (with material yield library) |
| **Edge peak width (FWHM)** | ±20% | Yes (with probe convolution) |
| **Material contrast ratio** | Qualitative (A brighter than B) | Yes |
| **Flat-surface background** | ±30% | Yes |
| **Profile shape (relative)** | Good match to expected shape | Yes |

**Inference:** CD metrology algorithms detect edges primarily from the **position** of bright peaks, not from their absolute intensity. As long as the peak position is accurate and the overall shape is qualitatively correct, the simulator will be useful for algorithm development.

---

## 6. Implementation Boundary Conditions

| Parameter | CD-SEM Range | Simulator Default |
|---|---|---|
| Beam energy | 300 eV–5 keV | 500 eV, 1 keV |
| Probe diameter | 0.5–2 nm | 1 nm |
| Probe current | 5–50 pA | 15 pA |
| Working distance | 3–8 mm | 5 mm |
| Detector type | TTL SE + annular BSE | TTL SE + BSE |
| Pixel size | 0.2–5 nm | 1 nm |
| Field of view | 0.1–10 μm | 1 μm |

---

## 7. Conclusion

The engineering analysis identifies **five essential components** for the first implementation of a synthetic SEM image simulator:

1. **Material property library** (SE and BSE yields per material)
2. **$\sec\theta$ topographic contrast** (the dominant contrast mechanism)
3. **BSE compositional contrast** (required for multi-material structures)
4. **Gaussian probe convolution** (required for realistic edge profiles)
5. **Basic pixel intensity equation** (scaling and offset)

These five components will produce images that qualitatively match real SEM images of semiconductor structures — with correct edge brightening, material contrast, and finite resolution — and provide a sufficient foundation for CD metrology algorithm development.

---

## Sources

- L. Reimer, *Scanning Electron Microscopy: Physics of Image Formation and Microanalysis*, 2nd ed. Springer, 1998.
- J. I. Goldstein, D. E. Newbury, J. R. Michael, et al., *Scanning Electron Microscopy and X-Ray Microanalysis*, 4th ed. Springer, 2017.
- H. Seiler, "Secondary electron emission in the scanning electron microscope," *J. Appl. Phys.*, vol. 54, 1983.
- J. S. Villarrubia, A. E. Vladar, and M. T. Postek, "Scanning electron microscope measurement of width and shape of fabricated nanostructures," *J. Res. NIST*, vol. 109, 2004.
- D. C. Joy, *Monte Carlo Modeling for Electron Microscopy and Microanalysis*. Oxford University Press, 1995.
- C. N. Archie, "Critical dimension metrology," *AIP Conf. Proc.*, vol. 788, 2005.
- M. T. Postek and A. E. Vladar, "Critical dimension metrology," in *Handbook of Semiconductor Manufacturing Technology*, CRC Press, 2007.
