# Electron Beam Formation

**Research Phase:** 2.1
**Document:** 05_beam_formation.md
**Date:** 2026-07-30

---

## 1. Overview

The electron beam formation process transforms a raw electron emission into a finely focused, nanometer-scale probe that can be precisely positioned on the sample. This process involves five sequential stages:

```
Generation → Acceleration → Demagnification → Aperture Limitation → Final Focusing
```

Each stage is performed by a dedicated subsystem, and the total chain determines the final probe diameter, beam current, and convergence angle at the sample.

---

## 2. Beam Generation

### 2.1 Electron Extraction

The process begins at the electron source. For a Schottky FEG (the recommended source for semiconductor inspection):

1. The tungsten tip is heated to ~1,800 K.
2. A high voltage (2–7 kV) is applied between the tip (cathode) and the extractor electrode.
3. The electric field at the tip surface (~10⁸ V/m) lowers the work function barrier (Schottky effect).
4. Electrons are emitted from the tip through field-assisted thermionic emission.

### 2.2 Initial Beam Properties

| Property | Value (Schottky FEG) |
|---|---|
| Virtual source diameter | 15–30 nm |
| Angular current density | 100–1,000 μA/sr |
| Total emission current | 100–200 μA |
| Initial beam divergence | Approximately 0.1–0.5 rad |
| Crossover location | Below the emitter, or suppressed by gun lens |

### 2.3 Wehnelt Electrode (Grid)

The Wehnelt electrode (also called the grid cap) surrounds the emitter and is biased negative relative to the cathode (typically −50 to −500 V). Its functions are:

- **Current control:** Adjusting the Wehnelt bias changes the effective emission area, controlling the total beam current.
- **Beam shaping:** The electrostatic field between the emitter, Wehnelt, and anode forms a "crossover" — a demagnified image of the emitter that becomes the effective source for the column optics.
- **Cutoff:** At sufficient negative bias, the beam is completely suppressed (cutoff condition).

**Fact:** The crossover is the first point in the beam path where the electron beam diameter is reduced from the physical emitter size (≈1 μm tip) to a much smaller virtual source size (15–30 nm for Schottky FEG).

---

## 3. Beam Acceleration

### 3.1 Acceleration Mechanism

After extraction, electrons are accelerated to their final kinetic energy by the electric field between the cathode and the anode:

$$E_k = e V_{\text{acc}}$$

where $E_k$ is electron kinetic energy (eV), $e$ is electron charge, and $V_{\text{acc}}$ is the accelerating voltage (V).

**Typical accelerating voltages (semiconductor inspection):** 0.3–5 kV (300–5,000 eV electron energy).

### 3.2 Single vs. Multi-Stage Acceleration

| Configuration | Description | Use |
|---|---|---|
| Single-stage | Beam accelerated directly to final voltage between cathode and anode | Simple, lower cost |
| Multi-stage | Beam accelerated in steps; booster lenses maintain high energy until just before the sample | Reduced chromatic aberration, better low-kV performance |

**Recommendation:** For CD-SEM, multi-stage acceleration with a beam booster is preferred. The beam is accelerated to a higher energy (e.g., 8 kV) in the column, then decelerated to the final landing energy (e.g., 500 eV) by a retarding field near the sample. This reduces Coulomb interactions and chromatic aberrations in the column.

### 3.3 Landsberg Retarding Field

A retarding field (also called beam deceleration or "Landsberg" configuration) applies a negative bias to the sample stage relative to the final lens. This decelerates the beam just before it hits the sample, allowing high column energy (for good optics) with low landing energy (for low beam damage and reduced charging).

---

## 4. Beam Demagnification (Condenser System)

### 4.1 Why Demagnification Is Required

The source produces a virtual electron source of diameter 15–30 nm (Schottky FEG). To form a 1–2 nm probe at the sample, the beam must be demagnified by a factor of approximately 10–30×.

**Important principle:** The demagnification is not performed in a single stage. It is distributed across multiple lenses to control aberrations and beam current independently.

### 4.2 Condenser Lens Operation

Each condenser lens is an electromagnetic coil that generates a rotationally symmetric magnetic field. The lens strength is controlled by the coil current:

$$f \propto \frac{V}{(N I)^2}$$

where $f$ is the focal length, $V$ is the accelerating voltage, $N$ is the number of turns, and $I$ is the coil current.

**Stronger excitation (higher current) → shorter focal length → greater demagnification.**

### 4.3 Two-Lens Condenser System

**First Condenser Lens (C1):**
- Primary demagnification stage (10×–100×).
- Produces the first intermediate crossover.
- C1 excitation is the main control for spot size.

**Second Condenser Lens (C2):**
- Secondary demagnification stage (5×–20×).
- Controls beam current by determining how much of the beam passes through the downstream beam-defining aperture.
- Produces the second intermediate crossover (or parallel beam, depending on design).

**Typical demagnification chain:**

| Stage | Demagnification | Beam Diameter |
|---|---|---|
| Virtual source | 1× | 20 nm |
| C1 lens | 20× | 1.0 nm (at first crossover) |
| C2 lens | 10× | 0.1 nm (at second crossover — before aberrations) |
| Objective lens | 2× | 0.05 nm (ideal geometric — before aberrations) |

**Fact:** The geometric demagnification can produce a probe much smaller than 1 nm. In practice, lens aberrations and diffraction limit the final probe size to 0.5–2 nm.

---

## 5. Aperture Limitation

### 5.1 Function of Apertures

Apertures are circular holes in metal (typically platinum or molybdenum) disks placed in the beam path. They serve three purposes:

1. **Beam current control:** Block off-axis electrons to reduce the beam current to the desired level.
2. **Convergence angle definition:** Determine the angular spread of electrons arriving at the sample.
3. **Aberration reduction:** Block marginal rays that would contribute excessive spherical and chromatic aberration.

### 5.2 Beam-Defining Aperture (BDA)

The BDA is the most important aperture in the column. It is typically located between the condenser lenses and the objective lens.

**Effect on beam parameters:**

| Parameter | Large Aperture | Small Aperture |
|---|---|---|
| Convergence angle (α) | Large | Small |
| Probe current | High | Low |
| Spherical aberration | High | Low |
| Diffraction (at low kV) | Low | High |
| Depth of field | Small | Large |
| Signal-to-noise ratio | High | Low |

**Typical BDA diameters in CD-SEM:** 10–100 μm, with 20–40 μm being most common for high-resolution imaging.

### 5.3 The Brightness Limit

The maximum probe current for a given probe size is fundamentally limited by source brightness:

$$I_{\text{probe}} = \beta \cdot (\pi \alpha^2) \cdot A_{\text{probe}}$$

where:
- $\beta$ = source brightness (A/cm²·sr)
- $\alpha$ = convergence half-angle (rad)
- $A_{\text{probe}}$ = probe area at the sample (cm²)

**Inference:** For a fixed probe diameter and convergence angle, the only way to increase signal is to use a brighter source. This is why FEG sources dominate semiconductor inspection — they provide 100–1,000× more probe current at a given resolution than thermionic sources.

---

## 6. Final Focusing (Objective Lens)

### 6.1 Objective Lens Function

The objective lens performs the final focusing of the demagnified and aperture-limited beam onto the sample surface. It is the most critical optical element in the column.

**Key parameters:**
- **Focal length:** 2–20 mm (semiconductor SEM: typically 3–8 mm)
- **Working distance (WD):** The distance from the lens polepiece face to the sample
- **Aberration coefficients:** Cs (spherical) and Cc (chromatic)

### 6.2 Probe Size Budget

The final probe diameter $d_p$ is determined by a quadrature sum of contributions:

$$d_p^2 = d_g^2 + d_s^2 + d_c^2 + d_d^2$$

where:
- $d_g$ = Gaussian (geometric) image of the source
- $d_s$ = Spherical aberration disk $( \frac{1}{2} C_s \alpha^3 )$
- $d_c$ = Chromatic aberration disk $( C_c \frac{\Delta E}{E} \alpha )$
- $d_d$ = Diffraction disk $( 0.61 \lambda / \alpha )$

**Fact:** For a well-optimized Schottky FEG-SEM operating at 1 kV with a 10 mrad convergence angle:
- $d_g \approx 0.5$ nm
- $d_s \approx 0.3$ nm
- $d_c \approx 0.4$ nm
- $d_d \approx 0.2$ nm
- **Total $d_p \approx 0.7$–1.0 nm**

### 6.3 Objective Lens Operating Modes

| Mode | WD | α | Best For |
|---|---|---|---|
| High resolution | Short (3–5 mm) | Large (~15 mrad) | Smallest probe, highest magnification |
| Analytical | Medium (8–10 mm) | Medium (~10 mrad) | Balanced imaging and X-ray detection |
| Large depth of field | Long (15–20 mm) | Small (~5 mrad) | Rough topography, large field of view |

**Recommendation for CD-SEM:** High-resolution mode with short working distance (3–5 mm) and moderate convergence angle (5–10 mrad). This provides the smallest probe consistent with adequate depth of field for planar structures.

### 6.4 Stigmation Correction

Astigmatism — a non-circular beam spot — is corrected by a **stigmator**, a pair of quadrupole lenses that apply an adjustable elliptical field to compensate for imperfections in the objective lens and column alignment. Automatic stigmation is standard in all modern semiconductor SEMs.

---

## 7. Beam Scanning

### 7.1 Scan Coil Operation

After focusing, the beam is scanned across the sample in a raster pattern by two pairs of electromagnetic deflector coils:

1. **X-deflection coils:** Sweep the beam left-to-right (fast scan axis).
2. **Y-deflection coils:** Step the beam top-to-bottom (slow scan axis).

The deflection angle is proportional to the coil current and inversely proportional to the square root of the accelerating voltage:

$$\theta \propto \frac{N I L}{\sqrt{V}}$$

### 7.2 Double-Deflection Scanning

Modern SEMs use a double-deflection system:

```
First deflector: Tilts beam off-axis.
Second deflector: Re-centers beam so it passes through the objective lens on-axis.
```

Benefits:
- The beam always passes through the center of the objective lens, regardless of scan position.
- Off-axis aberrations are minimized.
- The beam remains perpendicular to the sample surface.

### 7.3 Scan and Magnification

Magnification is determined by the ratio of the display size to the scan area:

$$M = \frac{D_{\text{display}}}{L_{\text{scan}}}$$

where $D_{\text{display}}$ is the display width and $L_{\text{scan}}$ is the scan length on the sample.

- Scanning 100 μm × 100 μm at full screen → ~1,000× magnification
- Scanning 1 μm × 1 μm at full screen → ~100,000× magnification
- Scanning 100 nm × 100 nm at full screen → ~1,000,000× magnification

**Fact:** Magnification in an SEM has no optical limit in the sense of a light microscope. The practical limit is set by the probe diameter — once the probe diameter exceeds the pixel spacing, further magnification produces only "empty magnification" (blown-up pixels with no additional detail).

### 7.4 Scan Modes

| Mode | Description | Use |
|---|---|---|
| Raster | Continuous horizontal lines, top to bottom | Standard imaging |
| Slow scan | Extended dwell time per pixel | High signal-to-noise, low-drift samples |
| TV rate | 30 frames/sec | Dynamic observation, focusing |
| Spot mode | Beam fixed at one point | Point analysis, beam current measurement |
| Line scan | Beam scans one line repeatedly | Line profile measurement |
| Digital zoom | Subset of full scan area | High magnification without stage movement |

---

## 8. Complete Beam Formation Summary

```
┌──────────────────────────────────────────────────────────────────┐
│                  COMPLETE BEAM FORMATION CHAIN                    │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [Source]   Electrons emitted from ZrO/W tip (Schottky FEG)      │
│     │       Virtual source: 15–30 nm                             │
│     ▼                                                            │
│  [Acceleration]  Electrons accelerated to 0.3–30 keV              │
│     │       (or boosted to higher energy, then retarded)          │
│     ▼                                                            │
│  [C1 Lens]  Primary demagnification: 10×–100×                    │
│     │       First crossover formed                               │
│     ▼                                                            │
│  [Spray Aperture]  Blocks scattered electrons from C1            │
│     ▼                                                            │
│  [C2 Lens]  Secondary demagnification: 5×–20×                    │
│     │       Controls beam current through aperture                │
│     ▼                                                            │
│  [BDA]  Beam-defining aperture sets α and I_probe                │
│     │    Typical: 20–40 μm diameter                              │
│     ▼                                                            │
│  [Scan Coils]  X/Y raster deflection                             │
│     │       Double-deflection for on-axis lens entry             │
│     ▼                                                            │
│  [Objective Lens]  Final focus onto sample                       │
│     │       Typical probe: 0.5–2 nm at 3–5 mm WD                │
│     ▼                                                            │
│  [Sample]  Focused probe rastered across wafer surface           │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

**Fact:** The entire beam formation chain operates under high vacuum (<10⁻⁷ torr in the column). Any deviation in vacuum, lens current stability, or mechanical alignment degrades the final probe quality.

---

## Sources

- L. Reimer, *Scanning Electron Microscopy: Physics of Image Formation and Microanalysis*, 2nd ed. Springer, 1998.
- J. I. Goldstein, D. E. Newbury, J. R. Michael, et al., *Scanning Electron Microscopy and X-Ray Microanalysis*, 4th ed. Springer, 2017.
- R. F. Egerton, *Physical Principles of Electron Microscopy*, 2nd ed. Springer, 2016.
- A. Khursheed, *Scanning Electron Microscope Optics and Spectrometers*, World Scientific, 2011.
- P. W. Hawkes and J. C. H. Spence, *Springer Handbook of Microscopy*, Springer, 2019.
- Nanoscience Instruments, "Scanning Electron Microscopy," technical resource.
