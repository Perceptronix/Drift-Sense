# Charging Physics

**Research Phase:** 2.4
**Document:** 04_charging_physics.md
**Date:** 2026-07-30

---

## 1. Introduction

Charging is the accumulation of net electrical charge on the sample surface during electron beam irradiation. It is the most complex degradation mechanism in SEM imaging because it affects the image through multiple simultaneous pathways.

**Fact:** Charging occurs when the total electron emission yield $\sigma = \delta + \eta$ deviates from 1. If $\sigma > 1$, the sample emits more electrons than it receives → positive charging. If $\sigma < 1$, the sample absorbs more electrons than it emits → negative charging.

---

## 2. Physical Cause

### 2.1 Charge Balance

At each pixel, the net charge deposited is:

$$\Delta Q = I_P \cdot \tau \cdot (1 - \sigma)$$

where $I_P$ is the probe current, $\tau$ is the dwell time, and $\sigma = \delta + \eta$ is the total electron yield.

| Condition | Net Charge | Charging Polarity |
|---|---|---|
| $\sigma > 1$ | Positive (net electron loss) | **Positive charging** |
| $\sigma < 1$ | Negative (net electron gain) | **Negative charging** |
| $\sigma = 1$ | Neutral | **Charge-neutral condition** |

### 2.2 Material-Specific Behavior

| Material | $\sigma$ at 500 eV | $\sigma$ at 1 keV | $\sigma$ at 5 keV | Polarity at 1 keV |
|---|---|---|---|---|
| Si | ~1.20 | ~1.05 | ~0.48 | Near-neutral / slightly positive |
| SiO₂ | ~2.36 | ~1.93 | ~0.58 | **Strong positive** |
| Cu | ~1.33 | ~1.43 | ~0.72 | Positive |
| W | ~1.22 | ~1.32 | ~0.85 | Positive |
| Photoresist | ~2.30 | ~2.10 | ~0.57 | **Strong positive** |

**Inference:** At typical CD-SEM energies (500 eV–1.5 keV), most semiconductor materials have $\sigma > 1$, leading to **positive charging**. Insulators (SiO₂, resist) have $\sigma \approx 2$, which means they lose twice as many electrons as they receive — strong positive charging.

### 2.3 Conductivity and Charge Dissipation

| Material Type | Conductivity | Charge Dissipation | Charging Severity |
|---|---|---|---|
| **Metal (Cu, W, Al)** | High | Fast — charge dissipates instantly | **None to minimal** |
| **Semiconductor (Si, lightly doped)** | Moderate | Slow — may charge if beam current is high | **Low to moderate** |
| **Doped semiconductor (Si, heavily doped)** | Moderate-high | Moderate | **Low** |
| **Dielectric (SiO₂, Si₃N₄)** | Very low | Very slow — charge accumulates | **Severe** |
| **Photoresist (organic)** | Very low | Very slow | **Severe** |

---

## 3. Positive Charging

### 3.1 Physical Mechanism

When $\sigma > 1$, the sample loses net electrons to the vacuum, developing a positive surface potential $V_{\text{surf}} > 0$.

**Effects on imaging:**

1. **Reduced SE yield:** The positive potential attracts emitted SEs back to the surface (SE recapture). The effective detected SE signal decreases.

2. **Reduced BSE yield (for strong charging):** Very high positive potentials can influence BSE trajectories, though this requires potentials of hundreds of volts.

3. **Beam deflection (for significant charging):** The positive surface potential acts as an electrostatic lens, deflecting the primary beam. This distorts the apparent position of features.

### 3.2 Visual Appearance

| Charging Level | Visual Effect | Characteristic |
|---|---|---|
| **Mild** ($V_{\text{surf}} < 5$ V) | Slightly reduced brightness on insulators | Darker regions correspond to insulators |
| **Moderate** ($5 < V_{\text{surf}} < 50$ V) | Dark insulator regions with noticeable contrast reduction | Low contrast between materials |
| **Strong** ($V_{\text{surf}} > 50$ V) | Very dark insulators; beam distortion near charged regions | "Waterfall" effect — image distortion at material boundaries |
| **Severe** ($V_{\text{surf}} > 100$ V) | Complete loss of signal from insulators; gross beam deflection | Image unusable for metrology |

---

## 4. Negative Charging

### 4.1 Physical Mechanism

When $\sigma < 1$, the sample accumulates net negative charge. This occurs at higher beam energies (>3–5 keV for most materials).

**Effects on imaging:**

1. **Increased SE yield (apparent):** The negative surface potential repels SEs, increasing the number that escape to the detector. Insulators appear bright.

2. **Beam repulsion:** The negative potential deflects the primary beam away from the charged region, causing distortion.

### 4.2 Visual Appearance

| Charging Level | Visual Effect |
|---|---|
| **Mild** | Slightly increased brightness on insulators |
| **Moderate** | Bright blobs around insulating features |
| **Strong** | Bright halos; beam deflection |

**Fact:** Negative charging is less common in CD-SEM than positive charging because CD-SEM operating energies (300 eV–1.5 keV) are typically below $E_2$ (the upper crossover energy where $\sigma = 1$).

---

## 5. Dielectric Charging Dynamics

### 5.1 Time-Dependent Charging

Charging of dielectrics is a dynamic process:

1. **Initial irradiation:** The surface begins to charge almost immediately. Within the first pixel dwell time (1–10 μs), the charge state may already deviate from neutral.

2. **Steady state:** The surface potential evolves toward an equilibrium where leakage currents balance the beam current. For thick dielectrics, this can take seconds to minutes.

3. **Beam-off decay:** When the beam is blanked or moved away, the surface charge decays through leakage to the substrate (time constant $\tau = RC$, where $R$ is the leakage resistance and $C$ is the capacitance of the dielectric film).

**Approximate time constants:**

| Dielectric | Thickness | RC Time Constant | Notes |
|---|---|---|---|
| SiO₂ (thin gate) | 1–10 nm | μs–ms | Fast leakage through thin film |
| SiO₂ (field oxide) | 100–500 nm | ms–s | Moderate |
| SiO₂ (thick) | 1–10 μm | s–min | Slow |
| Photoresist | 50–500 nm | s–min | Very slow |
| Si₃N₄ | 50–500 nm | s–min | Slow |

**Inference:** For thin gate oxides (<10 nm), charge dissipates quickly enough that steady-state charging is minimal. For thick dielectrics and photoresist, charging can accumulate over the entire image acquisition, causing progressive drift and distortion.

### 5.2 Charge Diffusion and Lateral Spreading

Charge does not remain at the point of deposition — it spreads laterally, creating a charge distribution that extends beyond the scan area:

$$V_{\text{surf}}(r) \propto \int \frac{\rho(r')}{|r - r'|} d^2r'$$

where $\rho(r')$ is the charge density distribution and $V_{\text{surf}}(r)$ is the resulting surface potential.

**Length scale:** The lateral extent of charging-induced fields is typically 1–100 μm, far larger than the feature sizes being imaged. This means charging affects the entire image, not just the beam position.

---

## 6. Effects on CD-SEM Measurement

### 6.1 Specific Effects on Linewidth Measurement

| Charging Effect | Impact on CD Measurement | Severity |
|---|---|---|
| **Edge signal reduction** | Local charging at edges reduces SE yield → lower edge peak amplitude → harder edge detection | Moderate |
| **Asymmetric edge profiles** | Differential charging on different sides of a line | Moderate |
| **Drift during measurement** | Slow accumulation of charge shifts apparent feature positions | High for long acquisitions |
| **Proximity effect** | Charging of one feature affects signal from nearby features | Moderate for dense patterns |

### 6.2 Voltage Contrast vs. Charging

**Important distinction:** Not all "charging-like" effects are artifacts. **Voltage contrast** is a deliberate use of the signal dependence on local potential to detect electrical defects (open contacts, floating gates). The physics is the same as charging, but VC is intentional and measured at the first scan (before significant charge accumulation).

---

## 7. Charging Mitigation Strategies

### 7.1 Operating Parameter Selection

| Strategy | Effect | Practical Limit |
|---|---|---|
| **Select $E$ where $\sigma \approx 1$** | Minimizes net charge deposition | Not all materials have same crossover energy |
| **Reduce beam current** | Reduces charge deposition rate | Lower SNR |
| **Reduce pixel dwell time** | Reduces charge per pixel | Lower SNR |
| **Use frame averaging** | Distributes charge across repeated scans | Limited by drift |

### 7.2 Sample Modifications

| Strategy | Effect | Applicability |
|---|---|---|
| **Conductive coating (C, Au, Pt)** | Provides charge dissipation path | Not acceptable on production wafers |
| **Reduce dielectric thickness** | Faster charge leakage | Not always possible |

---

## 8. Engineering Classification for Simulator

| Charging Effect | Essential for Simulator? | Justification | Model Form |
|---|---|---|---|
| **Charge-dependent SE yield modification** | **Essential** | Directly alters pixel intensity, especially on insulators | $\delta_{\text{eff}} = \delta_0 \cdot f(V_{\text{surf}})$ |
| **Contrast reduction from local charging** | **Recommended** | Reduces material contrast on insulating regions | Modified effective $\delta$ |
| **Beam deflection by surface charge** | **Optional** | Complex to model; affects high-aspect-ratio features significantly | Electrostatic deflection model |
| **Progressive drift during acquisition** | **Optional** | Time-dependent; requires sequential simulation | Frame-by-frame charging evolution |
| **Dielectric charging dynamics** | **Optional** | Only relevant for long acquisitions on thick insulators | RC circuit model per pixel |
| **Flashover / discharge events** | **Can ignore** | Rare, unpredictable; not part of controlled measurement | N/A |
| **Voltage contrast intentionally** | **Can ignore** | This is a measurement mode, not an artifact | Separate from degradation model |

### 8.1 Recommendation

**Fact:** For a first implementation of a synthetic SEM renderer, charging can be approximated by:

1. **Identifying insulating regions** in the structure (SiO₂, Si₃N₄, photoresist).
2. **Reducing the effective SE yield** for those regions by a fixed factor (e.g., 0.5–0.8 × nominal $\delta_0$).
3. **Optionally adding a blur kernel** to simulate the lateral spread of charge effects.

This simplified model captures the first-order visual effect (insulators appear darker than their nominal SE yield would suggest) without requiring a full self-consistent electrostatic simulation.

For a more accurate implementation, the full charging model requires:
- Self-consistent solution of charge deposition and electrostatic potential.
- Time-dependent charging evolution.
- Beam trajectory modification by surface fields.

---

## Sources

- L. Reimer, *Scanning Electron Microscopy: Physics of Image Formation and Microanalysis*, 2nd ed. Springer, 1998.
- J. I. Goldstein, D. E. Newbury, J. R. Michael, et al., *Scanning Electron Microscopy and X-Ray Microanalysis*, 4th ed. Springer, 2017.
- R. F. Egerton, *Physical Principles of Electron Microscopy*, 2nd ed. Springer, 2016.
- D. C. Joy and C. S. Joy, "Low-voltage scanning electron microscopy," *Micron*, vol. 27, 1996.
- M. T. Postek and A. E. Vladar, "Critical dimension metrology," in *Handbook of Semiconductor Manufacturing Technology*, CRC Press, 2007.
- A. E. Vladar, M. T. Postek, and R. Vane, "CD-SEM and the 45-nm node," *Proc. SPIE*, vol. 6518, 2007.
- C. N. Archie, "Critical dimension metrology," *AIP Conf. Proc.*, vol. 788, 2005.
