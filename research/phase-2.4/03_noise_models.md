# Noise Models

**Research Phase:** 2.4
**Document:** 03_noise_models.md
**Date:** 2026-07-30

---

## 1. Introduction

Noise in SEM images is the random, unwanted variation in pixel intensity that obscures the true signal. It arises from the fundamental physics of electron emission and detection, and from the electronic components used to process the signal.

**Fact:** At the typical beam currents and pixel dwell times used in CD-SEM (5–50 pA, 0.5–5 μs), noise is **signal-limited** — the number of detected electrons per pixel is small enough that Poisson (shot) statistics dominate.

---

## 2. Shot Noise (Poisson Noise)

### 2.1 Physical Origin

Shot noise arises from the discrete, quantized nature of electron detection. Each detected electron is an independent event; the number of electrons detected in a fixed time interval follows a Poisson distribution:

$$P(N) = \frac{\lambda^N e^{-\lambda}}{N!}$$

where $\lambda$ is the mean number of detected electrons per pixel and $N$ is the actual number detected.

**Fact:** The standard deviation of the Poisson distribution is:

$$\sigma_{\text{shot}} = \sqrt{\lambda}$$

The signal-to-noise ratio (SNR) is:

$$\text{SNR}_{\text{shot}} = \frac{\lambda}{\sqrt{\lambda}} = \sqrt{\lambda}$$

### 2.2 Number of Detected Electrons

The number of detected electrons per pixel is:

$$N_{\text{det}} = \frac{I_{\text{emit}} \cdot \tau \cdot \eta_{\text{coll}}}{e} = \frac{I_P \cdot (\delta + \eta) \cdot \tau \cdot \eta_{\text{coll}}}{e}$$

where:
- $I_P$ = probe current (A)
- $\tau$ = pixel dwell time (s)
- $\delta$ = SE yield
- $\eta$ = BSE yield
- $\eta_{\text{coll}}$ = detector collection efficiency
- $e$ = electron charge (1.602 × 10⁻¹⁹ C)

**Typical values for CD-SEM:**

| Parameter | Low Signal | Moderate Signal | High Signal |
|---|---|---|---|
| Probe current $I_P$ | 5 pA | 15 pA | 50 pA |
| Pixel dwell time $\tau$ | 0.5 μs | 2 μs | 10 μs |
| SE yield $\delta$ | 0.5 (W) | 1.0 (Si) | 2.0 (resist) |
| Collection efficiency $\eta_{\text{coll}}$ | 0.5 | 0.7 | 0.9 |
| **Electrons per pixel $N_{\text{det}}$** | **~8** | **~130** | **~5,600** |
| **Shot noise $\sigma$** | 2.8 | 11.4 | 75 |
| **SNR = $\sqrt{N_{\text{det}}}$** | **~3:1** | **~11:1** | **~75:1** |

**Inference:** For typical CD-SEM conditions (15 pA, 1 μs dwell), approximately 65–130 electrons are detected per pixel, giving an SNR of 8:1 to 11:1. This is barely adequate for edge detection. Longer dwell times or higher beam current improve SNR but reduce throughput or resolution.

### 2.3 Signal-Dependent Nature

**Fact:** Shot noise is signal-dependent — the noise variance increases linearly with signal. In brighter image regions, the absolute noise level is higher, but the relative noise (coefficient of variation: $\sigma/\mu = 1/\sqrt{\mu}$) is lower.

This has important implications:
- Bright regions (e.g., edges) have better SNR than dark regions (e.g., trench bottoms).
- Any model of shot noise must make the noise magnitude proportional to $\sqrt{I_{\text{signal}}}$.

---

## 3. Detector Noise

### 3.1 PMT Excess Noise

The photomultiplier tube multiplies the primary photoelectron signal through a dynode chain. The multiplication process itself introduces excess noise (beyond pure Poisson):

$$\sigma_{\text{PMT}} = \sqrt{\frac{1}{\delta_{\text{dynode}} - 1}} \cdot \sigma_{\text{shot}}$$

where $\delta_{\text{dynode}}$ is the dynode multiplication factor (typically 3–6 per stage).

**Excess noise factor:** Typically 1.1–1.3, meaning the PMT adds 10–30% more noise beyond pure shot noise.

**Recommendation:** PMT excess noise can be modeled by increasing the effective shot noise by the excess noise factor:

$$\sigma_{\text{total}} = F \cdot \sigma_{\text{shot}}$$

where $F \approx 1.1$–$1.3$.

### 3.2 Johnson-Nyquist Noise (Thermal Noise)

**Physical origin:** Random thermal motion of charge carriers in resistors. Present in all electronic components, especially the transimpedance amplifier's feedback resistor.

$$\sigma_{\text{Johnson}} = \sqrt{\frac{4k_B T \cdot \Delta f}{R_f}}$$

where:
- $k_B$ = Boltzmann constant (1.38 × 10⁻²³ J/K)
- $T$ = temperature (K)
- $\Delta f$ = amplifier bandwidth (Hz)
- $R_f$ = feedback resistance (Ω)

**Typical magnitude:** For $T = 300$ K, $\Delta f = 1$ MHz, $R_f = 10$ MΩ:

$$\sigma_{\text{Johnson}} \approx 0.4\text{ nV} / \sqrt{\text{Hz}} \times \sqrt{10^6\text{ Hz}} \approx 0.4\text{ μV}$$

**Inference:** Johnson noise is typically 10–100× smaller than shot noise for CD-SEM conditions and can usually be neglected. It becomes relevant only when the PMT gain is very low (high signal levels) or the signal bandwidth is very high (>10 MHz).

### 3.3 Dark Current

**Physical origin:** Thermionic emission from the PMT photocathode and dynodes produces a small signal even in the absence of incident light. Dark current is temperature-dependent:

$$I_{\text{dark}} \propto T^2 \exp(-\Phi/k_B T)$$

where $\Phi$ is the work function of the photocathode.

**Typical magnitude:** 0.1–10 nA at the PMT anode (corresponding to 0.01–1 photoelectrons/second at the photocathode, depending on PMT quality and cooling).

**For CD-SEM:** Dark current is negligible at typical dwell times (<1 electron per thousand pixels in a cooled PMT).

---

## 4. Electronic Amplifier Noise

### 4.1 Transimpedance Amplifier

The current-to-voltage conversion stage introduces both Johnson noise (from the feedback resistor) and amplifier input voltage/current noise:

| Noise Source | Typical Value | Unit | Importance |
|---|---|---|---|
| **Feedback resistor Johnson** | 0.4–4 | nV/√Hz | Minor |
| **Amplifier voltage noise** | 1–10 | nV/√Hz | Minor |
| **Amplifier current noise** | 0.1–1 | fA/√Hz | Minor to moderate |

**Fact:** Amplifier noise is typically <10% of total noise for well-designed CD-SEM electronics, where shot noise from electron detection dominates.

### 4.2 Video Amplifier Noise

The video amplifier adds further noise, but its contribution scales with amplifier bandwidth:

$$P_{\text{noise, amp}} \propto \Delta f \propto 1/\tau_{\text{dwell}}$$

**Inference:** For fast scanning (short dwell times), amplifier noise becomes relatively more important because the signal bandwidth is higher. For slow scanning (long dwell times), shot noise dominates.

---

## 5. Quantization Noise

### 5.1 ADC Quantization Error

The analog-to-digital converter introduces quantization noise when converting the continuous voltage signal to a discrete digital value:

$$\sigma_{\text{quant}} = \frac{\Delta}{\sqrt{12}}$$

where $\Delta$ is the voltage increment per least significant bit (LSB).

For an N-bit ADC with range $V_{\text{range}}$:

$$\Delta = \frac{V_{\text{range}}}{2^N - 1}$$

### 5.2 Typical Magnitudes

| ADC Resolution | $\Delta$ (for 5V range) | Quantization Noise $\sigma$ | Significance |
|---|---|---|---|
| 8-bit | 19.6 mV | 5.7 mV | **Significant** — can equal shot noise |
| 12-bit | 1.22 mV | 0.35 mV | **Minor** — much less than shot noise |
| 16-bit | 0.076 mV | 0.022 mV | **Negligible** |

**Inference:** For CD-SEM, 16-bit ADC is standard, making quantization noise negligible. 8-bit acquisition is used only for "quick view" modes and should be avoided for quantitative measurement.

---

## 6. Scan Noise

### 6.1 Scan Generator Jitter

Fluctuations in the scan coil current or the scan generator timing cause the beam to sample slightly different positions than intended:

- **Horizontal jitter:** Random variation in the X-scan position within a line.
- **Vertical jitter:** Random variation in the Y-step between lines.
- **Effect:** Apparent noise in the image that is not signal-dependent.

### 6.2 Scan Coil Current Noise

Noise in the scan coil driver current causes fluctuations in the beam position. This is typically very small for modern CD-SEMs (<0.1% of scan range).

**Recommendation:** Scan noise can be ignored for most simulation purposes. It becomes relevant only for the highest-precision CD measurements (sub-0.5 nm precision).

---

## 7. Brightness Fluctuations

### 7.1 Source Emission Noise

Fluctuations in the electron source emission current produce correlated noise across all image pixels:

- **Schottky FEG:** Emission stability <0.5%/hour after warm-up. Noise is low-frequency drift, not pixel-to-pixel shot noise.
- **Cold FEG:** Higher frequency fluctuations requiring periodic tip flashing.

**Recommendation:** For typical CD-SEM (Schottky FEG), emission noise is negligible for single-image acquisition (<1 second to <1 minute). It can be ignored for synthetic image generation.

### 7.2 High-Voltage Ripple

Residual AC ripple on the accelerating voltage causes correlated brightness changes and focus fluctuations:

- **Magnitude:** <0.1 ppm rms for modern CD-SEM power supplies.
- **Effect:** Negligible.

---

## 8. Complete Noise Model

### 8.1 Unified Noise Equation

The total pixel noise (variance) is the sum of all independent noise sources:

$$\sigma_{\text{total}}^2 = \sigma_{\text{shot}}^2 + \sigma_{\text{PMT}}^2 + \sigma_{\text{Johnson}}^2 + \sigma_{\text{amp}}^2 + \sigma_{\text{quant}}^2$$

### 8.2 Dominant Terms

For a typical CD-SEM (Schottky FEG, 15 pA, 1 μs dwell, 16-bit ADC):

| Noise Source | Variance Contribution | Fraction of Total |
|---|---|---|
| **Shot noise** | $\lambda$ (where $\lambda \approx 100$) | **~65–80%** |
| **PMT excess noise** | $(F^2 - 1)\lambda \approx 0.2\lambda$ | **~15–20%** |
| **Johnson (amplifier)** | $\ll \lambda$ | <5% |
| **Quantization** | ~0.01 | <1% |
| **Dark current** | ~0 | <1% |

**Fact:** Shot noise dominates. The simplified model for CD-SEM simulation is:

$$I_{\text{noisy}} = I_{\text{ideal}} + \sqrt{I_{\text{ideal}} \cdot G \cdot F} \cdot \mathcal{N}(0, 1)$$

where $\mathcal{N}(0,1)$ is standard Gaussian noise, $G$ is the gain factor converting electrons to digital units, and $F$ is the excess noise factor (~1.2).

---

## 9. SNR Scalings

### 9.1 SNR as Function of Beam Current

$$\text{SNR} \propto \sqrt{I_P}$$

Doubling the beam current increases SNR by a factor of $\sqrt{2}$ (~41% improvement), but increases probe diameter, reducing resolution.

### 9.2 SNR as Function of Dwell Time

$$\text{SNR} \propto \sqrt{\tau}$$

Doubling the dwell time increases SNR by $\sqrt{2}$ at the cost of slower acquisition and increased drift susceptibility.

### 9.3 SNR from Frame Averaging

$$\text{SNR} \propto \sqrt{N_{\text{avg}}}$$

Averaging $N$ frames improves SNR by $\sqrt{N}$. 16-frame averaging gives 4× SNR improvement but takes 16× longer.

**Inference:** The practical limits of frame averaging are set by drift — if the sample drifts by more than one pixel during the acquisition, spatial resolution is degraded.

---

## 10. Engineering Classification

| Noise Source | Essential for Simulator? | Model Form |
|---|---|---|
| **Shot noise (Poisson)** | **Essential** | $N_{\text{det}} \sim \text{Poisson}(\lambda)$, $\lambda = I_{\text{emit}} \tau \eta_{\text{coll}} / e$ |
| **PMT excess noise** | **Recommended** | Scale shot noise variance by $F^2$ ($F \approx 1.2$) |
| **Johnson noise** | **Optional** | Add Gaussian noise with $\sigma^2 = 4k_B T \Delta f / R_f$ |
| **Quantization noise** | **Optional** | Uniform $\pm \Delta/2$, variance $\Delta^2/12$ |
| **Dark current** | **Can ignore** | <1 e⁻ per pixel |
| **Scan noise** | **Can ignore** | <0.1% of scan range |
| **Source emission noise** | **Can ignore** | Low-frequency drift, not pixel noise |

**Recommendation:** For the first implementation, model only **shot noise** with the correct Poisson statistics. Add **PMT excess noise** as a simple variance scaling. All other noise sources can be deferred.

---

## Sources

- L. Reimer, *Scanning Electron Microscopy: Physics of Image Formation and Microanalysis*, 2nd ed. Springer, 1998.
- J. I. Goldstein, D. E. Newbury, J. R. Michael, et al., *Scanning Electron Microscopy and X-Ray Microanalysis*, 4th ed. Springer, 2017.
- R. F. Egerton, *Physical Principles of Electron Microscopy*, 2nd ed. Springer, 2016.
- D. C. Joy, *Monte Carlo Modeling for Electron Microscopy and Microanalysis*. Oxford University Press, 1995.
- M. T. Postek and A. E. Vladar, "Critical dimension metrology," in *Handbook of Semiconductor Manufacturing Technology*, CRC Press, 2007.
- C. N. Archie, "Critical dimension metrology," *AIP Conf. Proc.*, vol. 788, 2005.
- A. E. Vladar, M. T. Postek, and R. Vane, "CD-SEM and the 45-nm node," *Proc. SPIE*, vol. 6518, 2007.
- Wikipedia, "Shot noise," accessed July 2026.
