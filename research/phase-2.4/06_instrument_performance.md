# Instrument Performance

**Research Phase:** 2.4
**Document:** 06_instrument_performance.md
**Date:** 2026-07-30

---

## 1. Introduction

Instrument performance parameters link the physical degradation mechanisms (blur, noise, charging, artifacts) to the user-controlled settings on the SEM. Understanding these relationships is essential for a realistic simulator because the same sample can produce very different images depending on the instrument settings.

This document covers:
- How resolution is defined and measured in SEM
- Modulation Transfer Function (MTF)
- Signal-to-noise ratio trade-offs
- Dynamic range and its limits
- Pixel sampling requirements
- Scan speed and its consequences
- Frame averaging optimization

---

## 2. Resolution Definitions

### 2.1 Traditional Resolution Criteria

| Criterion | Definition | Used In |
|---|---|---|
| **Rayleigh** | Two point sources resolved when the dip between them is 26% of peak intensity | Light microscopy, not SEM |
| **10–90% edge rise** | Distance over which signal rises from 10% to 90% of the step height | CD-SEM metrology |
| **FWHM of Gaussian probe** | Full width at half maximum of the probe current density | SEM specification |
| **Sparrow** | Two points just resolved when the dip between them disappears | Some SEM literature |
| **Fourier ring** | Spatial frequency at which the SNR crosses a threshold | TEM, some SEM |

**Fact:** For CD-SEM, the most commonly used resolution metric is the **10–90% edge rise distance**, measured on a sharp edge of known material (typically Si). This metric directly captures the effect of all blur contributions on the signal that matters for CD measurement.

### 2.2 Resolution vs. Probe Diameter

The relationship between the probe diameter $d_p$ (FWHM of Gaussian) and the 10–90% edge rise distance $R_{10-90}$ depends on the specific edge model:

| Edge Model | $R_{10-90}$ / $d_p$ |
|---|---|
| **Gaussian probe, ideal step edge** | 1.0 (approximately) |
| **Gaussian probe + escape depth** | 1.0–1.5 (material-dependent) |
| **Gaussian probe + SE-II tail** | 1.5–3.0 (profile-dependent) |

**Inference:** The edge rise distance is typically 1.5–3× larger than the probe diameter in CD-SEM, due to the combined effects of the SE escape depth and SE-II background.

---

## 3. Modulation Transfer Function (MTF)

### 3.1 Definition

The MTF is the magnitude of the Fourier transform of the point spread function, normalized to DC (zero spatial frequency):

$$\text{MTF}(f) = \frac{|\mathcal{F}\{\text{PSF}(x)\}|}{|\mathcal{F}\{\text{PSF}(x)\}|_{f=0}}$$

It describes how contrast varies with spatial frequency.

### 3.2 MTF in CD-SEM

**Fact:** The CD-SEM MTF is primarily determined by the Gaussian probe shape. For a Gaussian probe with standard deviation $\sigma$:

$$\text{MTF}(f) = \exp\left(-2\pi^2 \sigma^2 f^2\right)$$

At the spatial frequency $f_c = 1/(2\sigma)$, the MTF falls to $\exp(-\pi^2/2) \approx 0.007$ — essentially zero contrast.

### 3.3 Practical MTF Measurements

For a CD-SEM with $d_p = 1.5$ nm (FWHM), $\sigma = 0.64$ nm:

| Spatial Frequency (period) | MTF |
|---|---|
| DC (flat signal) | 1.0 |
| 100 nm pitch | 0.97 |
| 50 nm pitch | 0.88 |
| 20 nm pitch | 0.50 |
| 10 nm pitch | 0.16 |
| 5 nm pitch | 0.01 |

**Inference:** Features with pitch smaller than ~20 nm are imaged with significantly reduced contrast. Below ~10 nm pitch, the contrast is too low for reliable CD measurement. This is a fundamental limitation of the finite probe diameter.

---

## 4. Signal-to-Noise Ratio

### 4.1 SNR Definition

The SNR in SEM is typically defined as:

$$\text{SNR} = \frac{\mu}{\sigma}$$

where $\mu$ is the mean signal level and $\sigma$ is the standard deviation due to noise (shot noise plus other contributions).

### 4.2 Maximum Achievable SNR

From the shot noise model (Document 03), the maximum SNR is:

$$\text{SNR}_{\text{max}} = \sqrt{\frac{I_P \cdot \tau \cdot (\delta + \eta) \cdot \eta_{\text{coll}}}{e}}$$

**Contour plot of SNR as function of $I_P$ and $\tau$ (for $\delta + \eta = 1.0$, $\eta_{\text{coll}} = 0.7$):**

| $I_P$ | $\tau = 0.5$ μs | $\tau = 2$ μs | $\tau = 10$ μs |
|---|---|---|---|
| **5 pA** | 3.3 | 6.6 | 14.8 |
| **15 pA** | 5.7 | 11.4 | 25.6 |
| **50 pA** | 10.5 | 20.9 | 46.7 |

**Inference:** The SNR in CD-SEM is typically modest (10:1 to 30:1) for standard operating conditions. This is significantly lower than most optical imaging systems.

### 4.3 SNR Requirements for CD Metrology

| Application | Required SNR (typical) |
|---|---|
| **Rough imaging / navigation** | 3:1 |
| **Qualitative inspection** | 5:1 |
| **CD measurement (low precision)** | 10:1 |
| **CD measurement (high precision)** | 20:1 |
| **Model-based metrology** | 30:1+ |

---

## 5. Dynamic Range

### 5.1 Definition and Limits

Dynamic range is the ratio of the maximum measurable signal to the noise floor:

$$\text{DR} = \frac{I_{\text{max}}}{\sigma_{\text{floor}}}$$

| Component | Dynamic Range (bits) | Dynamic Range (dB) |
|---|---|---|
| **PMT (analog)** | 16–20 bits | 96–120 dB |
| **Transimpedance amplifier** | 12–16 bits | 72–96 dB |
| **12-bit ADC** | 12 bits | 72 dB |
| **16-bit ADC** | 16 bits | 96 dB |
| **Display (8-bit)** | 8 bits | 48 dB |

**Fact:** For CD-SEM, the dynamic range is limited by the ADC (12 or 16 bits) rather than the detector. 16-bit ADC provides ~96 dB dynamic range, sufficient for most applications.

### 5.2 Practical Dynamic Range

In real imaging, the useful dynamic range is reduced by:
- The signal level occupying only a fraction of the ADC range.
- Noise increasing the effective "floor."
- The need to reserve headroom for the brightest features.

**Typical useful DR:** 8–10 bits (48–60 dB) after considering these factors.

---

## 6. Pixel Sampling

### 6.1 Nyquist Criterion for SEM

The pixel spacing must satisfy the Nyquist criterion:

$$\Delta x \leq \frac{1}{2 f_{\text{max}}}$$

where $f_{\text{max}}$ is the highest spatial frequency present in the image. For a Gaussian probe with $\sigma$:

$$f_{\text{max}} \approx \frac{1}{\pi \sigma}$$

$$\Delta x_{\text{Nyquist}} \leq \frac{\pi \sigma}{2} \approx 1.57 \sigma$$

### 6.2 Recommended Pixel Sizes

| Probe Diameter (FWHM) | Nyquist Pixel Size | Typical CD-SEM Pixel Size |
|---|---|---|
| 0.5 nm | <0.3 nm | 0.5 nm |
| 1.0 nm | <0.6 nm | 1.0 nm |
| 1.5 nm | <1.0 nm | 1.0–1.5 nm |
| 2.0 nm | <1.3 nm | 1.5–2.0 nm |

**Fact:** Most CD-SEMs oversample relative to Nyquist by a factor of 1.5–2×. This provides redundancy that improves edge detection precision.

---

## 7. Scan Speed

### 7.1 Line Time and Frame Time

The relationship between pixel dwell time $\tau$, image width $M$, and height $N$:

$$T_{\text{frame}} = M \times N \times \tau$$

| $\tau$ | Frame time ($1024 \times 1024$) | Typical Use |
|---|---|---|
| 0.1 μs | 0.1 s | Fast survey imaging |
| 0.5 μs | 0.5 s | Scan-to-find |
| 1 μs | 1.05 s | Standard CD measurement |
| 5 μs | 5.2 s | High precision CD |
| 10 μs | 10.5 s | Very high SNR |

### 7.2 Speed-Quality Trade-off

**Fact:** The trade-off is fundamental and unavoidable:
- **Faster scan** → Lower SNR, less drift, lower throughput cost.
- **Slower scan** → Higher SNR, more drift, higher throughput cost.
- The optimum scan speed depends on the required measurement precision and the stability of the tool.

---

## 8. Frame Averaging

### 8.1 Benefit

Averaging $N$ frames improves SNR by $\sqrt{N}$, at the cost of $N \times$ longer total acquisition time.

### 8.2 Drift Limitation

The maximum useful number of averaged frames is limited by drift:

$$N_{\text{max}} = \left(\frac{\text{drift tolerance}}{\text{drift rate} \times T_{\text{frame}}}\right)^2$$

For a CD-SEM with 1 nm drift tolerance and 0.5 nm/min drift rate at 1 s/frame:

$$N_{\text{max}} \approx \left(\frac{1\text{ nm}}{0.5\text{ nm/min} \times 1/60\text{ min}}\right)^2 \approx (120)^2 (\text{!})$$

In practice, the drift rate is higher during scanning (sample heating), so $N_{\text{max}}$ is typically 16–64 frames for high-quality CD-SEM measurements.

### 8.3 Recommended Averaging

| Purpose | Frames | SNR Improvement |
|---|---|---|
| **Quick check** | 1 | 1× |
| **Standard measurement** | 8–16 | 2.8–4× |
| **High precision** | 32–64 | 5.7–8× |
| **Ultra-high precision** | 128–256 | 11–16× |

---

## 9. Probe Current vs. Resolution Trade-off

This is the central trade-off in CD-SEM:

| Probe Current $I_P$ | Probe Diameter $d_p$ | Shot Noise (for 1 μs dwell) | Relative SNR |
|---|---|---|---|
| 5 pA | 0.8 nm | 3.8×10⁻¹⁹ C | 1.0 (reference) |
| 15 pA | 1.0 nm | 1.1×10⁻¹⁸ C | 1.7× |
| 50 pA | 1.5 nm | 3.1×10⁻¹⁸ C | 3.2× |
| 200 pA | 3.0 nm | 1.3×10⁻¹⁷ C | 6.3× |

**Inference:** Increasing the probe current by 10× improves SNR by ~3× but increases the probe diameter (blur) by ~2×. The choice of operating point is a strategic decision based on the trade-off between resolution and precision.

---

## 10. User-Controlled Parameters and Their Effects

| Parameter | Primary Effect | Secondary Effect | Typical Range for CD-SEM |
|---|---|---|---|
| **Accelerating voltage** | Penetration depth, SE yield, probe size | Charging behavior, beam damage | 300 V – 5 kV |
| **Probe current** | Signal level, SNR | Probe diameter (higher current → larger probe) | 5–200 pA |
| **Working distance** | Probe size, collection efficiency | Aberration magnitude | 3–8 mm |
| **Aperture size** | Probe current, convergence angle | Diffraction, depth of field | 10–50 μm |
| **Pixel dwell time** | SNR, scan time | Drift blur | 0.1–10 μs |
| **Pixel size** | Sampling resolution | FOV, SNR per pixel | 0.2–5 nm |
| **PMT gain** | Amplitude | Noise, saturation | Variable |
| **Frame averaging** | SNR | Acquisition time, drift blur | 1–256 |
| **Scan direction** | Thermal drift asymmetry | Scan distortion | Horizontal, vertical |

---

## 11. Engineering Summary

| Parameter | Essential to Model? | Notes |
|---|---|---|
| **Probe diameter (Gaussian)** | **Essential** | Sets the resolution limit |
| **SNR / shot noise** | **Essential** | Determines measurement precision |
| **Pixel size** | **Essential** | Determines sampling |
| **Dwell time** | **Essential** | Determines SNR scaling |
| **Frame averaging** | **Recommended** | Impacts SNR and blur |
| **MTF** | **Recommended** | Derived from probe PSF |
| **Dynamic range / ADC** | **Optional** | 16-bit ADC is effectively ideal |
| **Scan speed trade-offs** | **Context** | Not a rendering parameter |
| **Probe current-res. trade-off** | **Context** | Not a rendering parameter |

---

## Sources

- L. Reimer, *Scanning Electron Microscopy: Physics of Image Formation and Microanalysis*, 2nd ed. Springer, 1998.
- J. I. Goldstein, D. E. Newbury, J. R. Michael, et al., *Scanning Electron Microscopy and X-Ray Microanalysis*, 4th ed. Springer, 2017.
- R. F. Egerton, *Physical Principles of Electron Microscopy*, 2nd ed. Springer, 2016.
- J. S. Villarrubia, A. E. Vladar, and M. T. Postek, "Scanning electron microscope measurement of width and shape of fabricated nanostructures," *J. Res. NIST*, vol. 109, 2004.
- M. T. Postek and A. E. Vladar, "Critical dimension metrology," in *Handbook of Semiconductor Manufacturing Technology*, CRC Press, 2007.
- C. N. Archie, "Critical dimension metrology," *AIP Conf. Proc.*, vol. 788, 2005.
- A. E. Vladar, M. T. Postek, and R. Vane, "CD-SEM and the 45-nm node," *Proc. SPIE*, vol. 6518, 2007.
