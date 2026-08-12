# Signal-to-Image Pipeline

**Research Phase:** 2.3
**Document:** 02_signal_to_image_pipeline.md
**Date:** 2026-07-30

---

## 1. Overview

The conversion from "electrons emitted from the sample" to "digital pixel values in a grayscale image" passes through six distinct physical and electronic stages. Each stage applies a transfer function that can amplify, attenuate, or distort the signal.

**The complete pipeline:**

```
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ SE/BSE       │ → │ Electron     │ → │ Detector     │
│ Emission     │   │ Transport    │   │ Collection   │
│ (at sample)  │   │ (in vacuum)  │   │ (scintillator│
│              │   │              │   │  + PMT)      │
└──────────────┘   └──────────────┘   └──────┬───────┘
                                            │
                                            ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ Grayscale    │ ← │ Pixel        │ ← │ Amplifier    │
│ Image        │   │ Mapping      │   │ & ADC        │
│ (display)    │   │ (digital)    │   │ (electronic) │
└──────────────┘   └──────────────┘   └──────────────┘
```

---

## 2. Stage 1: SE/BSE Emission from the Sample

### 2.1 What Is Produced

At each beam position $(x,y)$, the sample emits:
- **Secondary electrons** ($I_{\text{SE}}$) — energy < 50 eV, from top 1–20 nm
- **Backscattered electrons** ($I_{\text{BSE}}$) — energy > 50 eV, from top 0.1–1 μm

The total emitted current at position $(x,y)$ is:

$$I_{\text{emit}}(x,y) = I_P \cdot [\delta(x,y) + \eta(x,y)]$$

where $I_P$ is the probe current, $\delta$ is the SE yield, and $\eta$ is the BSE yield.

### 2.2 Angular Distribution of Emitted Electrons

**Fact:** Both SE and BSE are emitted with characteristic angular distributions:

- **SE:** The emission follows a cosine distribution: $\frac{dN}{d\Omega} \propto \cos\phi$, where $\phi$ is the angle from the surface normal. This is approximately Lambertian.
- **BSE:** The angular distribution depends on beam energy and atomic number. For flat surfaces at normal incidence, the distribution is approximately $\propto \cos\theta$. For tilted surfaces, BSEs peak in the forward direction.

### 2.3 Energy Distribution

- **SE energy distribution:** Peaks at 2–5 eV, tail to 50 eV (Chung-Everhart distribution).
- **BSE energy distribution:** Broad, from 50 eV to $E_0$, with most BSEs having >50% of $E_0$.

**Inference:** The low energy of SEs means their transport is strongly influenced by electric and magnetic fields near the sample. BSEs, being much more energetic, follow nearly straight-line trajectories.

---

## 3. Stage 2: Electron Transport in Vacuum

### 3.1 Trajectory from Sample to Detector

After emission, electrons travel from the sample surface to the detector through the vacuum chamber. Their trajectories are influenced by:

| Influence | Effect on SE | Effect on BSE |
|---|---|---|
| **Extraction field** (Everhart-Thornley grid bias: +200–300 V) | Strong — pulls SEs toward detector | Weak — BSEs too energetic to be significantly deflected |
| **Objective lens magnetic field** (through-the-lens detection) | Strong — SEs follow magnetic field lines to detector | Moderate — can redirect some BSEs |
| **Sample surface field** (local charging) | Strong at low energies | Negligible |
| **Electric fields from nearby structures** | Moderate for isolated features | Negligible |

### 3.2 Through-the-Lens (TTL) Detection

In modern CD-SEMs, the TTL detector collects SEs that travel upward through the objective lens:

1. The magnetic field of the objective lens acts as a magnetic "mirror."
2. Low-energy SEs (2–50 eV) are captured by the field lines and follow helical trajectories up through the lens bore.
3. The SEs are separated from the primary beam path by a beam separator (Wien filter or magnetic deflection) and directed to the detector.
4. BSEs, with much higher energy, are largely unaffected by the lens field and follow ballistic trajectories.

**Fact:** The TTL detection system provides two critical advantages:
- High collection efficiency for SEs (large solid angle, effectively ~2π sr).
- Rejection of most BSEs, ensuring the detected signal is primarily SE-I (highest resolution).

### 3.3 Everhart-Thornley Detection

In side-mounted E-T detection:

1. A Faraday cage with positive bias (+200–300 V) is placed near the sample, off-axis.
2. SEs are attracted to the positively biased collector.
3. Once collected, SEs strike a scintillator coated with a thin conductive layer (e.g., tin-doped indium oxide) biased to +10–12 kV.
4. The scintillator emits photons upon electron impact.

**Detector shadowing:** Because the E-T detector is located to one side, it preferentially collects SEs emitted in its direction. Surfaces tilted toward the detector appear brighter; those tilted away appear darker. This produces a characteristic "three-dimensional" shading effect.

---

## 4. Stage 3: Detector Collection and Scintillation

### 4.1 Scintillator Physics

When an energetic electron (accelerated to 10–12 kV by the final scintillator bias) strikes the scintillator material, it produces photons through cathodoluminescence. Common scintillator materials:

| Material | Decay Time | Efficiency | Wavelength |
|---|---|---|---|
| YAG:Ce (Yttrium Aluminum Garnet) | ~70 ns | High | ~550 nm (green) |
| YAP:Ce (Yttrium Aluminum Perovskite) | ~25 ns | High | ~370 nm (UV) |
| P47 powder phosphor | ~80 ns | Moderate | ~430 nm (blue) |

**Fact:** The scintillator efficiency (photons per incident electron) determines the ultimate quantum efficiency of the detection chain. Typical values: 50–200 photons per 10 keV electron.

### 4.2 Photomultiplier Tube (PMT)

The light from the scintillator is conducted via a light guide (typically quartz or acrylic) to a photomultiplier tube:

1. **Photocathode:** Converts incident photons to photoelectrons (quantum efficiency ~10–25%).
2. **Dynode chain:** 8–14 stages of electron multiplication. Each dynode produces 3–6 secondary electrons per incident electron.
3. **Total gain:** $10^5$–$10^7$ (depending on number of dynodes and applied voltage).

**Detector gain control:** The PMT gain is controlled by varying the high voltage across the dynode chain. Higher voltage → higher gain → brighter image for a given signal level.

### 4.3 Solid-State BSE Detectors

For BSE detection, solid-state detectors convert electrons directly to electron-hole pairs without the scintillator-PMT chain:

- **Operation:** A reverse-biased p-n junction generates electron-hole pairs proportional to the incident electron energy.
- **Typical gain:** ~1 electron-hole pair per 3.6 eV (Si) of incident energy.
- **Time response:** ~10–50 ns.

---

## 5. Stage 4: Amplification and Signal Conditioning

### 5.1 Transimpedance Amplifier

The current output from the detector (PMT anode current or solid-state diode current) is converted to a voltage signal by a transimpedance amplifier:

$$V_{\text{out}} = -I_{\text{in}} \times R_f$$

where $R_f$ is the feedback resistor (typically 1–100 MΩ).

### 5.2 Video Amplifier

The voltage signal is further amplified and bandwidth-limited by a video amplifier:

- **Gain:** 10–100× (additional to PMT gain).
- **Bandwidth:** Matched to the pixel dwell time. For 1 μs dwell: $f_{\text{3dB}} \geq 500$ kHz. For 100 ns dwell: $f_{\text{3dB}} \geq 5$ MHz.

### 5.3 DC Offset and Black Level

A controllable DC offset is added to the signal to establish the black level (minimum pixel value). This is typically set to correspond to zero detected signal or a reference background level.

---

## 6. Stage 5: Analog-to-Digital Conversion

### 6.1 ADC Operation

The analog voltage is converted to a digital value by an N-bit analog-to-digital converter:

$$I_{\text{digital}} = \text{round}\left( \frac{V_{\text{signal}} - V_{\text{offset}}}{V_{\text{range}}} \times (2^N - 1) \right)$$

| Resolution | Levels | Typical Use |
|---|---|---|
| 8-bit | 256 (0–255) | Quick viewing, high throughput |
| 12-bit | 4,096 (0–4,095) | Intermediate quality |
| 16-bit | 65,536 (0–65,535) | Quantitative metrology |

**Fact:** Modern CD-SEMs typically acquire at 16-bit resolution internally and compress to 8-bit for display. The measurement algorithms use the full 16-bit data.

### 6.2 Digitization Error

The quantization error from the ADC is:

$$\Delta I = \frac{V_{\text{range}}}{2^N - 1}$$

For a 12-bit ADC with 5 V range: $\Delta I \approx 1.2$ mV per count.

---

## 7. Stage 6: Pixel Mapping and Grayscale Display

### 7.1 Image Memory

The digital pixel values are stored in a frame buffer organized as a 2D array:

$$M \times N \times B \text{ bits}$$

where $M$ = width in pixels, $N$ = height in pixels, $B$ = bits per pixel.

Common SEM frame sizes: 512×512, 1024×1024, 2048×2048, 4096×4096.

### 7.2 Grayscale Mapping

The stored pixel values are mapped to display brightness through a transfer function:

$$I_{\text{display}} = f(I_{\text{raw}})$$

Common mapping functions:

| Mapping | Equation | Effect |
|---|---|---|
| **Linear** | $I_{\text{disp}} = a \cdot I_{\text{raw}} + b$ | Preserves relative intensity |
| **Gamma (γ)** | $I_{\text{disp}} = c \cdot I_{\text{raw}}^\gamma$ | Enhances contrast in bright (γ < 1) or dark (γ > 1) regions |
| **Sigmoid** | S-curve mapping | Enhances mid-range contrast at expense of extremes |
| **Auto-contrast** | $I_{\text{disp}} = (I_{\text{raw}} - \min) / (\max - \min)$ | Maximizes displayed contrast |

**Fact:** For quantitative CD metrology, the linear mapping (or known gamma) is essential. In CD-SEM, the mapping is calibrated and stored in the measurement recipe.

### 7.3 Final Display

The digital image is rendered on a display where:
- **Minimum pixel value** (0) → black (no signal).
- **Maximum pixel value** ($2^N-1$) → white (maximum signal).
- The grayscale is linear in the mapped intensity.

---

## 8. Complete Transfer Function

The overall conversion from emitted electron current to digital pixel value can be expressed as a series of transfer functions:

$$I_{\text{pixel}} = T_{\text{ADC}}\left( G_{\text{amp}} \cdot G_{\text{PMT}} \cdot \eta_{\text{coll}}(x,y) \cdot [\delta(x,y) + \eta(x,y)] \cdot I_P \right)$$

| Component | Transfer Function | Variable |
|---|---|---|
| Emission | $I_{\text{emit}} = (\delta + \eta) \cdot I_P$ | Sample-dependent |
| Collection | $I_{\text{coll}} = \eta_{\text{coll}} \cdot I_{\text{emit}}$ | Detector geometry-dependent |
| PMT amplification | $I_{\text{anode}} = G_{\text{PMT}} \cdot I_{\text{coll}}$ | Controllable (gain setting) |
| Electronic amplification | $V_{\text{out}} = G_{\text{amp}} \cdot I_{\text{anode}}$ | Controllable |
| Digitization | $I_{\text{pixel}} = \text{ADC}(V_{\text{out}})$ | Resolution-dependent |

**Inference:** The operator controls only three parameters: probe current $I_P$, PMT gain $G_{\text{PMT}}$, and amplifier gain $G_{\text{amp}}$. The sample-dependent signals ($\delta$, $\eta$) and collection efficiency ($\eta_{\text{coll}}$) are fixed by the sample and detector geometry.

---

## 9. Summary

| Stage | Physical Process | Effect on Signal | Length Scale |
|---|---|---|---|
| **1. Emission** | SE/BSE generation at sample | Produces signal proportional to $(\delta + \eta)$ | 1–1000 nm |
| **2. Transport** | Electron trajectories to detector | Angular filtering by collection geometry | 1–10 mm |
| **3. Detection** | Scintillator + PMT conversion | Electron → photon → electron amplification ($10^5$–$10^7$) | ~1 cm |
| **4. Amplification** | Transimpedance + video amp | Current → voltage, bandwidth limiting | Electronic |
| **5. Digitization** | ADC conversion | Voltage → digital value ($N$ bits) | Electronic |
| **6. Mapping** | Grayscale transfer function | Raw → display brightness | Electronic |

---

## Sources

- L. Reimer, *Scanning Electron Microscopy: Physics of Image Formation and Microanalysis*, 2nd ed. Springer, 1998.
- J. I. Goldstein, D. E. Newbury, J. R. Michael, et al., *Scanning Electron Microscopy and X-Ray Microanalysis*, 4th ed. Springer, 2017.
- R. F. Egerton, *Physical Principles of Electron Microscopy*, 2nd ed. Springer, 2016.
- M. T. Postek and A. E. Vladar, "Critical dimension metrology," in *Handbook of Semiconductor Manufacturing Technology*, CRC Press, 2007.
- P. W. Hawkes and J. C. H. Spence, *Springer Handbook of Microscopy*, Springer, 2019.
- Wikipedia, "Scanning Electron Microscope," accessed July 2026.
