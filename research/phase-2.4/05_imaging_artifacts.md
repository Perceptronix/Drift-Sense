# Imaging Artifacts

**Research Phase:** 2.4
**Document:** 05_imaging_artifacts.md
**Date:** 2026-07-30

---

## 1. Introduction

Beyond blur, noise, and charging — which are continuous degradation mechanisms — there exist discrete imaging artifacts that produce specific, identifiable features in SEM images. This document catalogs all important artifacts, explains their physical origins, and classifies them for the synthetic renderer.

---

## 2. Edge Blooming

### 2.1 Physical Origin

Edge blooming is the apparent widening of bright edge regions beyond their true size. It occurs when:

1. The signal from a very bright edge peak saturates the detector or the ADC.
2. The signal reaches the amplifier voltage limit (saturation), causing the bright peak to spread into adjacent pixels.
3. Alternatively, the finite bandwidth of the video amplifier causes the signal to "bleed" into neighboring pixels.

### 2.2 Visual Appearance

```
Ideal:           Actual (blooming):
  ╱╲                ╱▔▔▔▔╲
 ╱  ╲              ╱      ╲
╱    ╲_           ╱        ╲_
```

The bright edge peaks appear flatter at the top and wider at the base than physically justified.

### 2.3 Severity

| Condition | Blooming Severity |
|---|---|
| Low gain, low signal | None |
| High gain, moderate signal | Moderate — peak clipped |
| Very high gain, bright edge | Severe — edge appears wider |

**Inference:** Edge blooming is a real concern for CD-SEM when the signal amplifier gain is set too high. However, when the SEM is properly adjusted (gain set so that the brightest features fill ~80% of the ADC range), blooming should be minimal.

**Recommendation:** **Optional** — model only if saturating the signal at high gain. The effect is avoided by proper instrument setup.

---

## 3. Halo Effects

### 3.1 Physical Origin

Halos are bright or dark rings that appear around features, distinct from the edge brightening signal. They arise from:

- **Charging halos:** A positive charge region around an insulating feature repels local SEs, creating a dark halo; a negative charge region attracts SEs, creating a bright halo.
- **SE-II halos:** The long-range SE-II signal from BSEs creates a low-intensity "glow" around bright features with extent up to ~1 μm.

### 3.2 Visual Appearance

```
Cross-section:
Intensity
  │   ╱╲      ╱╲
  │ ╱  ╲    ╱  ╲    ← SE-II tails (halo)
  │╱    ╲  ╱    ╲
──╱──────╲╱──────╲─── Position
```

**Inference:** The SE-II halo is a real physical effect that broadens edge profiles. It is distinct from "blooming" (which is an electronic artifact). The SE-II halo should be modeled as a convolution with a long-range kernel.

### 3.3 Classification

| Halo Type | Origin | Width | Model? |
|---|---|---|---|
| **SE-II halo** | Physical (BSE excitation) | ~1 μm kernel | **Recommended** — part of SE-II model |
| **Charging halo** | Charging | Varies | **Optional** — complex |
| **Detector halo** | Internal scattering in detector | Small | **Can ignore** |

---

## 4. Streaking

### 4.1 Physical Origin

Streaking is the appearance of bright or dark horizontal lines across the image, caused by:

- **Sudden discharge events:** Dielectric breakdown discharges charge, causing a transient bright line.
- **Beam blanking artifacts:** When the beam is blanked between lines or frames, imperfect blanking can leave a bright line.
- **AC interference:** 50/60 Hz interference in the detector electronics causes periodic intensity modulation.

### 4.2 Visual Appearance

```
Image (single line artifacts):
┌─────────────────────┐
│ normal image        │
├─────────────────────┤ ← Bright or dark streak
│ normal image        │
└─────────────────────┘
```

### 4.3 Severity

| Streak Type | Frequency | Severity |
|---|---|---|
| **Dielectric discharge** | Low — unpredictable | Moderate to high |
| **Beam blanking** | Low — well-designed tools | Low |
| **AC line interference** | Moderate — periodic | Low to moderate |

**Recommendation:** **Can ignore** for synthetic image generation. Streaks are unpredictable and tool-dependent; simulating them would require a stochastic model with low added value for metrology algorithm development.

---

## 5. Banding

### 5.1 Physical Origin

Banding is the appearance of quasi-periodic horizontal or vertical intensity variations, caused by:

- **Scan coil nonlinearity:** The scan waveform is not perfectly linear, causing brighter lines where the beam slows down.
- **Detector drift:** Slow changes in PMT gain or amplifier offset during scanning.
- **AC magnetic fields:** Line-frequency modulation of the beam position causes periodic brightness changes.

### 5.2 Visual Appearance

```
Image (vertical banding):
┌────┬────┬────┬────┬────┐
│    │    │    │    │    │ → Alternating bright/dark
└────┴────┴────┴────┴────┘
```

**Inference:** Banding in modern CD-SEMs is typically very small (<1% of signal amplitude) and does not significantly affect CD measurement.

**Recommendation:** **Optional** — can be modeled as a periodic sinusoidal modulation of the gain ($G = G_0(1 + A \sin(2\pi f x))$) if high realism is needed. For most purposes, **can ignore**.

---

## 6. Scan Distortion

### 6.1 Physical Origin

Scan distortion is the systematic deviation of the actual beam position from the intended raster pattern. Causes include:

- **Scan coil nonlinearity:** Perfectly linear ramp currents produce slightly nonlinear deflection.
- **Magnetic hysteresis:** Residual magnetization affects scan reproducibility.
- **Eddy currents:** Induced currents in the column walls distort the scan field at high speeds.
- **Lens distortion:** The objective lens may introduce pin-cushion or barrel distortion.

### 6.2 Visual Appearance

| Distortion Type | Appearance |
|---|---|
| **Pincushion** | Lines bend inward at image edges |
| **Barrel** | Lines bend outward at image edges |
| **S-curve** | S-shaped bending of horizontal lines |
| **Magnification variation** | Features appear larger/smaller at different positions |

### 6.3 Magnitude

| Distortion Source | Typical Magnitude (for FOV = 1 μm @ 1 keV) |
|---|---|
| Scan coil nonlinearity | <0.1% of FOV (<1 nm) |
| Lens distortion | <0.5% of FOV (<5 nm) |
| Hysteresis | <0.2% of FOV (<2 nm) |

**Inference:** For CD-SEM metrology, scan distortion is significant only at field edges or for very large fields of view. In the center 50% of the field, distortion is typically <0.1%.

**Recommendation:** **Optional** — only needed if modeling full-field (not cropped) images. A 2D polynomial distortion model can be added if required.

---

## 7. Drift

### 7.1 Physical Origin

Drift is the slow, continuous displacement of the image during acquisition, caused by:

- **Thermal drift:** Heating of column components causes expansion and beam shift.
- **Sample drift:** Creep in the stage mechanism or thermal expansion of the sample.
- **Charging drift:** Accumulation of charge changes the surface potential, deflecting the beam.

### 7.2 Effect on Image

Drift produces progressive image distortion, especially visible in:
- **Frame-averaged images:** If drift exceeds 1 pixel during averaging, edges become blurred asymmetrically.
- **Long-acquisition images:** The top and bottom of the image may appear shifted.

### 7.3 Typical Drift Rates

| Drift Source | Typical Rate | Observable Over |
|---|---|---|
| **Thermal (column)** | 0.1–0.5 nm/min | >30 s |
| **Sample (stage creep)** | 0.5–2 nm/min | >10 s |
| **Charging** | 0–50 nm/min | >1 s (severe cases) |

**Fact:** The drift effect on line profiles is that the apparent edge position shifts during the acquisition. For a single line scanned in <1 ms, the drift within the line is negligible. For a full-frame image taking 1–10 s, drift can shift the image by 1–10 nm.

**Recommendation:** **Optional.** Drift can be ignored for single-line profiles but may need to be included for full-frame simulation. A simple model: add time-dependent position offset to each scan line:

$$x_{\text{actual}}(t) = x_{\text{ideal}}(t) + \Delta x(t)$$

where $\Delta x(t)$ is a slowly varying random walk or monotonic displacement.

---

## 8. Vibration Artifacts

### 8.1 Physical Origin

Mechanical vibration produces periodic beam-to-sample displacement. Sources: building vibration, vacuum pumps, cooling fans, floor traffic.

### 8.2 Appearance

| Vibration Frequency | Effect on Image | Appearance |
|---|---|---|
| **Very low** (<1 Hz) | Gradual image shift | Motion blur |
| **Low** (1–20 Hz) | Line-to-line variation | Wavy edges |
| **High** (20 Hz – frame rate) | Within-line variation | Edge ripple |
| **Very high** (>frame rate) | Averaged over multiple lines | Gaussian blur |

### 8.3 Magnitude in CD-SEM Environments

| Environment | Typical Vibration Amplitude (peak-peak) |
|---|---|
| **Cleanroom (active isolation)** | <0.3 nm |
| **Standard lab (passive isolation)** | 1–3 nm |
| **Noisy environment (no isolation)** | 5–20 nm |

**Recommendation:** **Optional** — apply as an additional Gaussian blur for well-isolated tools. For poorest environments, a periodic displacement model may be needed.

---

## 9. Detector Saturation

### 9.1 Physical Origin

When the detected electron flux exceeds the linear range of the detector or amplifier, the output signal saturates. This occurs at very high SE yields, very high beam currents, or very high PMT gain.

### 9.2 Effect

```python
I_output = min(I_signal, I_max)
```

Signal levels above $I_{\text{max}}$ are clipped to the maximum output value.

### 9.3 Relevance for CD-SEM

- **Edge peaks** can saturate if the gain is too high.
- **Saturation flattens the edge peak**, potentially affecting CD measurement accuracy.

**Recommendation:** **Recommended** — simple to model and physically important. A clipping function at the maximum pixel value captures the effect:

$$I_{\text{saturated}} = \min(I, I_{\text{sat}})$$

---

## 10. Dead Pixels and Line Skipping

### 10.1 Dead Pixels

Occasional detector or ADC failures produce individual pixels with zero or fixed intensity regardless of the signal. In modern CD-SEMs, these are detected during calibration and corrected via interpolation.

**Recommendation:** **Can ignore** — does not occur in properly maintained CD-SEMs.

### 10.2 Line Skipping / Dropout

Rarely, a scan line is not properly acquired (timing glitch, beam blanking). The line repeats the previous line or appears as a zero-intensity line.

**Recommendation:** **Can ignore** for first implementation.

---

## 11. Frame Averaging Effects

### 11.1 Motion Blur from Frame Averaging

When frames are averaged and drift occurs, the resulting image shows blur proportional to the total drift across all frames:

| Number of Frames Averaged | Drift Allowed (at 1 nm/min) | Blur Added |
|---|---|---|
| 1 | 0 nm (single frame) | None |
| 16 (at 1 s/frame) | ~0.27 nm | Negligible |
| 64 (at 1 s/frame) | ~1.1 nm | Small but measurable |
| 256 (at 1 s/frame) | ~4.3 nm | Significant |

**Inference:** Frame averaging is always a trade-off between noise reduction (benefit ∝ $\sqrt{N}$) and drift blur (cost ∝ $N$). The optimum number of averaged frames depends on the drift rate.

**Recommendation:** **Optional** — can model as added Gaussian blur proportional to the total acquisition time.

---

## 12. Artifact Classification Summary

| Artifact | Essential | Optional | Can Ignore | Notes |
|---|---|---|---|---|
| **Edge blooming** | | ✓ | | Simple saturation model |
| **Halo (SE-II)** | | ✓ | | Part of SE-II model |
| **Halo (charging)** | | | ✓ | Complex, unpredictable |
| **Streaking** | | | ✓ | Unpredictable |
| **Banding** | | | ✓ | Negligible in modern tools |
| **Scan distortion** | | ✓ | | For full-field images |
| **Drift** | | ✓ | | For frame-averaged simulation |
| **Vibration** | | ✓ | | Simplified as Gaussian blur |
| **Detector saturation** | | ✓ | | Simple clip function |
| **Dead pixels** | | | ✓ | Corrected by CD-SEM |
| **Line skipping** | | | ✓ | Rare glitch |
| **Frame averaging blur** | | ✓ | | Adds Gaussian proportional to N |

---

## Sources

- L. Reimer, *Scanning Electron Microscopy: Physics of Image Formation and Microanalysis*, 2nd ed. Springer, 1998.
- J. I. Goldstein, D. E. Newbury, J. R. Michael, et al., *Scanning Electron Microscopy and X-Ray Microanalysis*, 4th ed. Springer, 2017.
- M. T. Postek and A. E. Vladar, "Critical dimension metrology," in *Handbook of Semiconductor Manufacturing Technology*, CRC Press, 2007.
- C. N. Archie, "Critical dimension metrology," *AIP Conf. Proc.*, vol. 788, 2005.
- T. Ishitani, H. Todokoro, and M. Kump, "Scanning electron microscope distortion," *J. Electron Microsc.*, vol. 43, 1994.
- Wikipedia, "Scanning Electron Microscope," accessed July 2026.
