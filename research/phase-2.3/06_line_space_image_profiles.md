# Line/Space Image Profiles

**Research Phase:** 2.3
**Document:** 06_line_space_image_profiles.md
**Date:** 2026-07-30

---

## 1. Introduction

The appearance of semiconductor structures in the SEM is the result of the contrast mechanisms described in previous documents applied to specific geometries. This document describes the characteristic SE intensity profiles produced by common semiconductor features, explains why each profile takes its shape, and identifies the features used for metrology.

---

## 2. Isolated Line (CD > 50 nm)

### 2.1 Profile Shape

For an isolated line on a flat substrate, the SE intensity across the line has this characteristic form:

```
Intensity
  │
  │    ╱╲          ╱╲
  │   ╱  ╲        ╱  ╲
  │  ╱    ╲______╱    ╲
  │ ╱                       ╲
──╱─────────────────────────╲─── Position
  ↑       ↑       ↑       ↑
  Left    Left    Right   Right
  foot    peak    peak    foot
```

**Key features:**
- Two bright peaks at the line edges (edge brightening).
- A plateau or gentle slope between the peaks (top of the line).
- A flat, lower-intensity region outside the lines (substrate).
- The peak intensity is 2–5× the flat-surface background.

### 2.2 Physical Origin

| Profile Region | Physical Mechanism |
|---|---|
| **Left foot (rising)** | Beam approaches left edge; interaction volume begins to sample the sidewall; $\sec\theta$ enhancement starts |
| **Left peak** | Beam at left edge; maximum $\sec\theta$ enhancement from the sidewall; additional escape through the sidewall |
| **Top plateau** | Beam on the flat top surface; near-normal incidence; baseline SE yield of the line material |
| **Minimum between peaks** | If the line is wide enough, the edge effects from opposite sides do not overlap |
| **Right peak and foot** | Same as left side, mirrored |

### 2.3 Dependence on Line Width

| Line Width | Profile Characteristic | Metrology Impact |
|---|---|---|
| Large (>100 nm) | Two well-separated peaks, flat top | Easy to resolve edges; CD = peak-to-peak distance |
| Moderate (30–100 nm) | Two peaks, no flat top (rounded top) | Edge positions still distinguishable |
| Small (10–30 nm) | One broad peak (peaks merge) | Edge detection requires model-based approaches |
| Very small (<10 nm) | Single peak; line acts as a ridge | CD extracted from shape and height of single peak |

**Fact:** The transition from "two peaks" to "one peak" occurs when the line width is comparable to the sum of the edge brightening widths from each edge (typically when CD < ~2× the interaction radius, or roughly 20–40 nm for a 1 keV beam).

---

## 3. Dense Lines (Periodic Line/Space Array)

### 3.1 Profile Shape

For a periodic array of lines and spaces:

```
Intensity
  │   ╱╲  ╱╲  ╱╲  ╱╲
  │  ╱  ╲╱  ╲╱  ╲╱  ╲
  │ ╱                    ╲
──╱──────────────────────╲─── Position
```

### 3.2 Key Differences from Isolated Lines

| Effect | Isolated Line | Dense Array |
|---|---|---|
| **SE-II background** | Low (substrate only) | Higher (multiple lines contribute) |
| **Edge peak symmetry** | Symmetric on both sides | May be asymmetric (left vs. right pitch) |
| **Space (trench) signal** | Open to substrate | Constrained by neighboring lines |
| **Top material** | Same material | Same material |

### 3.3 Pitch and Duty Cycle Effects

| Pitch / Duty Cycle | Profile Characteristics |
|---|---|
| **Equal L/S (1:1)** | Peaks at edges; valleys in spaces and on line tops |
| **Dense lines (space < line)** | Narrower space valleys; possible SE-II filling of spaces |
| **Dense spaces (line < space)** | Isolated-like profiles if pitch > interaction radius |

**Inference:** The SE-II contribution from adjacent lines can significantly affect the signal level in narrow spaces. For sub-50 nm pitch structures, the space between lines may appear brighter than expected from the substrate yield alone because SE-II from the adjacent line sidewalls adds to the local signal.

---

## 4. Trench (Recessed Feature)

### 4.1 Profile Shape

For a recessed trench in a flat surface:

```
Intensity
  │   ╱╲            ╱╲
  │  ╱  ╲__________╱  ╲
  │ ╱                    ╲
──╱──────────────────────╲─── Position
```

### 4.2 Characteristics

| Feature | Behavior | Cause |
|---|---|---|
| **Trench edges** | Bright peaks | $\sec\theta$ from sidewalls (same as line edges) |
| **Trench bottom** | Dark | Beam lands on flat bottom (no tilt); possible shadowing from sidewalls; SE-II from sidewalls may slightly elevate signal |
| **Outside surface** | Flat baseline | Normal flat-surface SE yield |

---

## 5. Contact Hole (Isolated)

### 5.1 Profile Shape

For a cylindrical contact hole in a dielectric layer:

**Radial intensity profile:**

```
Intensity
  │
  │    ╱╲
  │   ╱  ╲
  │  ╱    ╲______
  │ ╱              ╲__
──╱─────────────────── Radius
  ↑    ↑        ↑
  Edge Center  Outside
  (peak)
```

### 5.2 Characteristics

| Region | Signal Level | Cause |
|---|---|---|
| **Outside (radial)** | Flat baseline | Normal flat-surface SE yield |
| **Top edge (ring)** | High peak (2–5×) | Corner effect (2D enhancement) + $\sec\theta$ |
| **Inside (near edge)** | Decreasing | Beam enters the hole; depth shadowing |
| **Center** | Lowest | Deepest point; minimal SE escape if hole is deep |
| **Bottom edge** | Weak (possible) | Only visible if the hole is shallow (< escape depth) |

**Fact:** The bright ring at the top edge of a contact hole is typically the feature used for CD measurement. The ring diameter (measured at a specific threshold or slope criterion) defines the measured contact hole CD.

---

## 6. Via

### 6.1 Similarity to Contact Hole

Vias (vertical interconnect access) have the same general profile as contact holes — a bright annular ring at the top edge and reduced signal inside.

**Key difference:** Vias often have a metal cap (e.g., Cu or W) at the bottom, which can produce:
- Increased SE-II signal in the via if the cap has high SE yield.
- A different signal level at the bottom compared to the sidewall material.

---

## 7. FinFET Fin

### 7.1 Profile Shape

For a FinFET fin (a narrow, tall silicon ridge):

```
Intensity
  │      ╱╲      ╱╲
  │     ╱  ╲    ╱  ╲
  │    ╱    ╲  ╱    ╲
  │   ╱      ╲╱      ╲
──╲_╱──────────────────╲_╱─── Position
```

### 7.2 Characteristics

| Feature | Behavior | Cause |
|---|---|---|
| **Fin sidewall edges** | Strong bright peaks | Very high tilt angle (~90°) → maximum $\sec\theta$ |
| **Fin top** | Narrow, often reduced signal | If the fin is narrow, the top surface contributes less area; the sidewall peaks may merge |
| **Between fins** | Reduced signal | Shadowing by tall, narrow fins |

**Fact:** FinFETs (with aspect ratios of 3:1 or higher) produce strong edge brightening from the near-vertical sidewalls. The CD measured is typically the distance between the outer edge peaks or a model-based estimate of the fin width.

---

## 8. DRAM Cell

### 8.1 Profile Shape

DRAM cells consist of periodic arrays of deep trenches with complex 3D geometry:

```
Intensity
  │  ╱╲  ╱╲  ╱╲  ╱╲
  │ ╱  ╲╱  ╲╱  ╲╱  ╲
  │╱                    ╲
──╱──────────────────────╲─── Position
```

### 8.2 Characteristics

| Feature | Behavior |
|---|---|
| **Top surface** | Periodic modulation — wordline and bitline structures |
| **Deep trench openings** | Bright edges with dark interiors |
| **Buried structures** | Not visible in SE mode (too deep) unless high kV is used |
| **Capacitor trenches** | Only the top opening is visible in SE mode |

**Inference:** For DRAM metrology, the top-down SEM image measures the critical dimensions of the top openings (trench or capacitor top CD). The depth of the structures affects the SE signal level at the bottom but does not provide accurate depth measurement by itself.

---

## 9. Profile Summary Table

| Structure | SE Profile Type | Key Metrology Feature | Modulation |
|---|---|---|---|
| **Isolated line (CD > 50 nm)** | Two peaks, flat top | Peak-to-peak distance | 2–5× |
| **Isolated line (CD < 30 nm)** | Single broad peak | Peak width / model-based | 1.5–3× |
| **Dense lines (pitch < pitch_res)** | Periodic peaks | Edge positions, pitch | 1.5–4× |
| **Trench** | Two peaks, dark bottom | Edge positions | 2–5× |
| **Contact hole** | Annular ring | Ring diameter (threshold) | 2–5× |
| **Via** | Annular ring (may differ at bottom) | Ring diameter | 2–4× |
| **FinFET fin** | Narrow double peak (may merge) | Peak separation | 3–8× |
| **DRAM cell** | Complex periodic | Top opening CD | 2–4× |

---

## 10. Factors Affecting Profile Shape

### 10.1 Beam Energy

| Energy | Effect on Profiles |
|---|---|
| Higher (5–30 keV) | Broader edge peaks, lower contrast, more subsurface information |
| Lower (300 eV–1.5 keV) | Sharper edge peaks, higher surface sensitivity, better CD accuracy |

### 10.2 Sidewall Angle

| Sidewall Angle | Effect on Peak Amplitude |
|---|---|
| 90° (vertical) | Maximum edge peak (5–10× enhancement) |
| 80° | Strong peak (3–5×) |
| 70° | Moderate peak (2–3×) |
| 45° (sloped) | Weak peak (1.5–2×) |

### 10.3 Material Composition

| Top/Bottom Material | Effect on Profile |
|---|---|
| Resist on Si | High SE from resist, moderate from Si → good contrast |
| SiO₂ on Si | High SE from oxide, moderate from Si → good contrast |
| Cu on SiO₂ | High BSE from Cu → complex mixed contrast |
| W on SiO₂ | Low SE from W, high SE from SiO₂ → inverted contrast |

---

## 11. Recommendations for Simulation

### 11.1 Essential Physics for Profile Generation

1. **Local surface angle calculation** from the 3D structure geometry.
2. **$\sec\theta$ yield model** for each surface element.
3. **Probe convolution** (Gaussian probe) to account for finite resolution.
4. **Material assignment** per region (to set $\delta_0$ and $\eta$).

### 11.2 Profile Validation

For each structure type, the simulated profile should be validated against:
- Published CD-SEM images and line profiles from the literature.
- Monte Carlo simulations (CASINO or similar) for selected cross-sections.
- Expected behavior: peak positions, peak amplitudes, and overall shape.

---

## Sources

- J. S. Villarrubia, A. E. Vladar, and M. T. Postek, "Scanning electron microscope measurement of width and shape of fabricated nanostructures," *J. Res. NIST*, vol. 109, 2004.
- M. T. Postek and A. E. Vladar, "Critical dimension metrology," in *Handbook of Semiconductor Manufacturing Technology*, CRC Press, 2007.
- L. Reimer, *Scanning Electron Microscopy: Physics of Image Formation and Microanalysis*, 2nd ed. Springer, 1998.
- C. N. Archie, "Critical dimension metrology," *AIP Conf. Proc.*, vol. 788, 2005.
- B. D. Bunday et al., "CD-SEM metrology," *Proc. SPIE*, vol. 5038, 2003.
- A. E. Vladar, M. T. Postek, and R. Vane, "CD-SEM and the 45-nm node," *Proc. SPIE*, vol. 6518, 2007.
- J. I. Goldstein, D. E. Newbury, J. R. Michael, et al., *Scanning Electron Microscopy and X-Ray Microanalysis*, 4th ed. Springer, 2017.
