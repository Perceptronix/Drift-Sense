# SEM Image Acquisition Workflow

**Research Phase:** 2.1
**Document:** 06_image_acquisition_workflow.md
**Date:** 2026-07-30

---

## 1. Scope

This document describes the complete image acquisition pipeline of a scanning electron microscope from electron generation through digital image formation. It is deliberately limited to the **acquisition workflow** — the sequential chain of physical processes that result in an image.

This document does **not** explain:
- How the sample generates contrast
- Why different materials produce different signal levels
- How secondary vs. backscattered electrons differ in information content
- How noise, blur, or artifacts affect image quality

Those topics belong to Phase 2.2.

---

## 2. The Complete Acquisition Pipeline

The SEM image acquisition pipeline consists of seven sequential stages:

```
┌─────────────────────┐
│  1. Electron        │  Electrons generated at the gun
│     Generation      │
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│  2. Beam            │  Electrons accelerated to final energy
│     Acceleration    │
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│  3. Beam            │  Beam demagnified and shaped by optics
│     Conditioning    │
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│  4. Beam            │  Focused beam scanned in raster pattern
│     Scanning        │
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│  5. Sample          │  Electron beam interacts with sample
│     Irradiation     │  (details deferred to Phase 2.2)
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│  6. Signal          │  Emitted electrons collected by detector
│     Collection      │
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│  7. Image           │  Detector signal converted to digital
│     Formation       │  pixels, displayed as grayscale image
└─────────────────────┘
```

---

## 3. Stage 1: Electron Generation

**What happens:** The electron source produces free electrons through field-assisted thermionic emission (Schottky FEG) or pure field emission (cold FEG).

**Key parameters determined at this stage:**
- Source brightness (β) — determines maximum available probe current
- Source size — sets the lower bound on achievable probe diameter
- Energy spread (ΔE) — determines chromatic aberration contribution
- Emission current stability — affects measurement precision over time

**Output:** A diverging beam of electrons emerging from the gun region, with well-defined angular current density.

**For a Schottky FEG source:**
- Tip temperature: ~1,800 K
- Extraction voltage: 2–7 kV
- Virtual source diameter: 15–30 nm
- Total emission current: 100–200 μA
- Energy spread: 0.3–1.0 eV

---

## 4. Stage 2: Beam Acceleration

**What happens:** Electrons are accelerated from the cathode potential to the ground potential, acquiring kinetic energy equal to the accelerating voltage multiplied by the electron charge.

**Acceleration configurations:**

| Configuration | Description | Effect |
|---|---|---|
| Full acceleration | Electrons accelerated to final voltage immediately | Simplest design |
| Booster (dual-stage) | Beam accelerated to intermediate voltage, held at high energy in column, decelerated at sample | Reduces Coulomb interactions and chromatic aberration |

**Control parameter:** Accelerating voltage ($V_{\text{acc}}$), typically 300 V–5 kV for semiconductor inspection.

**Output:** A collimated beam of monoenergetic electrons (within the source energy spread) traveling at a velocity determined by:

$$v = \sqrt{\frac{2 e V_{\text{acc}}}{m_e}}$$

At 1 kV: $v \approx 1.9 \times 10^7$ m/s (~6% of the speed of light).

---

## 5. Stage 3: Beam Conditioning

**What happens:** The raw beam from the gun is refined into a focused probe with controlled diameter, current, and convergence angle.

**Sub-stages:**

### 5.1 Demagnification (Condenser Lenses)
- C1 lens: Reduces the beam crossover by 10×–100×.
- C2 lens: Further reduces by 5×–20×.
- Total demagnification: 50×–2,000×.

### 5.2 Aperture Limitation
- The beam-defining aperture (BDA) blocks off-axis electrons.
- Sets the convergence half-angle (α) and probe current ($I_p$).
- Typical BDA: 20–40 μm diameter.

### 5.3 Final Focusing (Objective Lens)
- Focuses the conditioned beam to a minimum-diameter probe on the sample.
- Typical probe diameter: 0.5–2 nm for CD-SEM.
- Working distance: 3–10 mm.

**Output:** A focused electron probe with well-defined diameter $d_p$, convergence angle $\alpha$, and current $I_p$, centered on the optical axis at the sample plane.

---

## 6. Stage 4: Beam Scanning

**What happens:** The focused beam is deflected by the scan coils to sweep across the sample surface in a precisely controlled raster pattern.

### 6.1 Scan Pattern

```
Line 1:  ████████████████████████████████████  →  (fast X scan)
Line 2:  ████████████████████████████████████  →
Line 3:  ████████████████████████████████████  →
 ...
          ↓ (slow Y step)
Line N:  ████████████████████████████████████  →
```

Each "█" represents one pixel position where the beam dwells and signal is collected.

### 6.2 Key Scanning Parameters

| Parameter | Typical Values | Effect |
|---|---|---|
| Pixel resolution | 512×512, 1024×1024, 2048×2048, 4096×4096 | Spatial sampling density |
| Dwell time per pixel | 0.1–100 μs | Signal level, noise, speed |
| Frame time | 0.03–100 s | Total acquisition time |
| Scan area | 100 nm × 100 nm to 1 mm × 1 mm | Determines magnification |
| Line averaging | 1–256 frames averaged | Improves SNR at cost of speed |

### 6.3 Synchronization

The scan generator produces synchronized signals for:
1. **X-deflection coil:** Sawtooth waveform (fast axis).
2. **Y-deflection coil:** Staircase waveform (slow axis).
3. **Data acquisition trigger:** ADC samples the detector at each pixel position.

**Fact:** The synchronization between scanning and pixel acquisition must be precise to within nanoseconds. Any jitter or drift in the scan-deflection relationship appears as image distortion.

**Output:** A temporally sequenced set of beam positions $(x_i, y_j)$ at the sample, with known dwell time at each position.

---

## 7. Stage 5: Sample Irradiation

**What happens:** The focused primary electron beam impinges on the sample surface at each scan position. Electrons penetrate the sample and undergo scattering events.

**This stage is the boundary between Phase 2.1 and Phase 2.2.**

What is important for the acquisition workflow:
- The beam deposits energy into the sample.
- The sample emits signals (secondary electrons, backscattered electrons, X-rays, etc.).
- The number and type of emitted signals depend on the sample material and geometry.

What is **deferred to Phase 2.2**:
- The physics of electron-sample interactions.
- How the sample composition and topography affect signal emission.
- The interaction volume and its dependence on beam energy.

**Output:** An emitted signal flux at each beam position, containing information about the sample at that point.

---

## 8. Stage 6: Signal Collection

**What happens:** Emitted electrons are collected by a detector system and converted into an electrical signal.

### 8.1 Detector Types

| Detector | Collects | Signal Conversion |
|---|---|---|
| Through-the-lens (TTL) SE detector | Secondary electrons | Scintillator → PMT → voltage |
| Everhart-Thornley (E-T) detector | SE or BSE (switchable) | Scintillator → PMT → voltage |
| Solid-state BSE detector | Backscattered electrons | Electron-hole pairs → current → voltage |
| In-lens BSE detector | Backscattered electrons | Scintillator or solid-state → voltage |

### 8.2 Signal Chain

The detector signal follows a standard chain:

```
Electron collection
    ↓
Scintillator (converts e⁻ to photons)
    ↓
Light guide (transmits photons to PMT)
    ↓
Photomultiplier tube (amplifies signal by 10⁶–10⁷)
    ↓
Current-to-voltage converter (transimpedance amplifier)
    ↓
Video amplifier (further amplification, bandwidth limiting)
    ↓
Output: analog voltage proportional to detected electron flux
```

### 8.3 Signal Bandwidth and Dwell Time

The detector and amplifier system must have sufficient bandwidth to respond within a single pixel dwell time:

$$f_{\text{BW}} \geq \frac{1}{2 \tau_{\text{dwell}}}$$

For $\tau_{\text{dwell}} = 100$ ns (fast TV-rate scanning): $f_{\text{BW}} \geq 5$ MHz.
For $\tau_{\text{dwell}} = 10$ μs (slow high-quality imaging): $f_{\text{BW}} \geq 50$ kHz.

**Output:** A time-varying analog voltage signal $V(t)$ proportional to the detected electron flux at each scan position.

---

## 9. Stage 7: Image Formation

### 9.1 Analog-to-Digital Conversion

The analog detector signal is converted to a digital pixel value by an analog-to-digital converter (ADC):

$$I(x_i, y_j) = \frac{V_{ij} - V_{\text{offset}}}{V_{\text{gain}}} \times (2^N - 1)$$

where:
- $V_{ij}$ = measured analog voltage at pixel position $(i, j)$
- $V_{\text{offset}}$ = dark level (signal with no beam)
- $V_{\text{gain}}$ = amplifier gain per signal electron
- $N$ = ADC bit depth (typically 8–16 bits)

### 9.2 Pixel Values

| ADC Resolution | Grayscale Levels | Typical Use |
|---|---|---|
| 8-bit | 256 (0–255) | Quick viewing, CD-SEM with high throughput |
| 12-bit | 4,096 (0–4,095) | High dynamic range imaging |
| 16-bit | 65,536 (0–65,535) | Quantitative measurement, low-noise averaging |

**Fact:** Modern CD-SEM tools typically acquire 16-bit images and compress to 8-bit for display, maintaining the full dynamic range for measurement algorithms.

### 9.3 Image Construction

The digital image is constructed pixel-by-pixel:

```
For each Y position (j = 1 to Ny):
    For each X position (i = 1 to Nx):
        Position beam at (xi, yj)
        Wait for dwell time τ
        Sample detector signal → ADC → pixel value Iij
        Store Iij in image buffer at (i, j)
    Advance Y deflection to next line
```

Each pixel $I_{ij}$ represents the signal intensity at the corresponding sample position $(x_i, y_j)$.

### 9.4 Image Display

The digital image buffer is rendered on a display:

- **Grayscale mapping:** Pixel values are mapped to display brightness. A linear mapping is typical, but nonlinear mappings (sigmoid, logarithmic) may be used to enhance contrast in specific signal ranges.
- **Automatic brightness and contrast:** The display system typically auto-scales the pixel range to use the full display dynamic range.

### 9.5 Magnification Revisited

Magnification is determined by the ratio of display size to scan area:

$$M = \frac{\text{Display width}}{\text{Scan width on sample}}$$

| Scan Width | Display Width | Magnification |
|---|---|---|
| 100 μm | 200 mm | 2,000× |
| 10 μm | 200 mm | 20,000× |
| 1 μm | 200 mm | 200,000× |
| 200 nm | 200 mm | 1,000,000× |

**Fact:** Changing magnification in an SEM does not change the optical system (unlike a zoom lens in a light microscope). It simply changes the area scanned by the deflection coils.

---

## 10. Complete Acquisition Pipeline Diagram

```
Time base → Scan Generator → Scan Coils ──→ Beam Position (X, Y)
                                  │
                                  ▼
Electron Source → Lenses → Focused Beam ──→ Sample → Signals
                                                     │
                                                     ▼
                                              Detector → Amplifier → ADC
                                                                      │
                                                                      ▼
                                                               Image Memory
                                                                      │
                                                                      ▼
                                                               Display
```

**Key synchronization:** The scan generator simultaneously controls beam position and triggers pixel acquisition, ensuring that each pixel value corresponds to the correct sample location.

---

## 11. Acquisition Modes

### 11.1 Single-Frame Mode
- Beam scans the full frame once.
- Fastest acquisition.
- Used for focusing and stage navigation.

### 11.2 Integration Mode (Multiple Frame Averaging)
- Multiple frames are acquired and averaged pixel-by-pixel.
- Signal-to-noise ratio improves as $\sqrt{N_{\text{frames}}}$.
- Used for high-quality imaging of stationary samples.

### 11.3 Drift-Corrected Mode
- A reference image is acquired first.
- Subsequent frames are aligned to the reference before averaging.
- Compensates for thermal drift during long acquisitions.
- Essential for CD-SEM precision measurement.

### 11.4 Line Scan Mode
- The beam scans the same line repeatedly.
- Signal is plotted as intensity vs. position.
- Used for CD measurement (line width extraction) and focus monitoring.

---

## 12. Summary

The SEM image acquisition workflow is a fully synchronized pipeline:

| Stage | What Is Created | Key Parameter |
|---|---|---|
| 1. Generation | Electron beam from source | Brightness, stability |
| 2. Acceleration | High-energy beam | Accelerating voltage |
| 3. Conditioning | Focused probe | Probe diameter, beam current |
| 4. Scanning | Raster scan pattern | Scan area, dwell time |
| 5. Irradiation | Sample interaction | (Phase 2.2) |
| 6. Collection | Electrical signal | Detector gain, bandwidth |
| 7. Formation | Digital image | ADC resolution, grayscale levels |

Each pixel in the final image corresponds to one beam position, and the pixel's grayscale value is determined by the amount of signal detected at that position. The mechanism by which the sample modulates the detected signal — and thus creates the observed grayscale contrast — is the subject of Phase 2.2.

---

## Sources

- L. Reimer, *Scanning Electron Microscopy: Physics of Image Formation and Microanalysis*, 2nd ed. Springer, 1998.
- J. I. Goldstein, D. E. Newbury, J. R. Michael, et al., *Scanning Electron Microscopy and X-Ray Microanalysis*, 4th ed. Springer, 2017.
- R. F. Egerton, *Physical Principles of Electron Microscopy*, 2nd ed. Springer, 2016.
- P. W. Hawkes and J. C. H. Spence, *Springer Handbook of Microscopy*, Springer, 2019.
- Nanoscience Instruments, "Scanning Electron Microscopy," technical resource.
