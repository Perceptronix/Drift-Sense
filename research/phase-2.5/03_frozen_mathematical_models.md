# Frozen Mathematical Models

**Research Phase:** 2.5
**Document:** 03_frozen_mathematical_models.md
**Date:** 2026-07-30

---

## 1. Selection Framework

Every model in this document was evaluated against three criteria:

| Criterion | Weight | Description |
|---|---|---|
| **Physical accuracy** | High | Does the model reproduce the known SEM physics for semiconductor structures? |
| **Computational efficiency** | High | Can the model be evaluated per-pixel in a practical renderer? |
| **Parameter availability** | Medium | Are the required parameters known for all six target materials? |

**Approach taken:** For each phenomenon, the most accurate model that can be evaluated in O(1) per pixel was selected. More accurate but slower models (full Monte Carlo) are reserved for validation.

---

## 2. Secondary Electron Yield Model

### 2.1 Selected Model: Power-Law Secant

$$\delta(\theta) = \delta_0 \cdot \sec^\gamma(\theta)$$

| Parameter | Symbol | Value | Status |
|---|---|---|---|
| Normal-incidence SE yield | $\delta_0$ | Per material (0.85 for Si) | Material library (frozen) |
| Angular exponent | $\gamma$ | 1.0 (nominal) | Fixed |

### 2.2 Alternatives Considered

| Model | Form | Rejected Because |
|---|---|---|
| **Linear secant** [B1][J7] | $\delta(\theta) = \delta_0 \sec\theta$ | No free parameter; accepted as baseline ($\gamma=1$) |
| **Seiler model** [J7] | $\delta(\theta) = \delta_0 (1 + b\theta^2)$ | Polynomial form diverges at high angles; less physical |
| **Monte Carlo full simulation** | Full trajectory tracking | O(N) per pixel — too slow |

### 2.3 Limitations

1. The $\sec^\gamma$ model overestimates yield for $\theta > 70^\circ$ because surface reabsorption becomes significant [B1].
2. No azimuthal dependence — assumes rotational symmetry around the surface normal.
3. Does not distinguish SE-I and SE-II contributions (SE-II is handled separately — see Section 6).

### 2.4 Correction for High Angles ($\theta > 70^\circ$)

For $\theta > 70^\circ$, the secant model is modified:

$$\delta(\theta) = \delta_0 \cdot \min(\sec^\gamma(\theta), \ \delta_{\max})$$

where $\delta_{\max} = \delta_0 \cdot \sec^\gamma(70^\circ)$ (clamp at 70° equivalent). This prevents unphysical yield values at grazing incidence.

---

## 3. Backscattered Electron Model

### 3.1 Selected Model: Atomic-Number-Dependent Yield

$$\eta(Z, E_0) = \eta_{\text{Reimer}}(Z) \cdot f_{\text{energy}}(E_0)$$

where $\eta_{\text{Reimer}}(Z)$ is the Reimer formula [B1]:

$$\eta_{\text{Reimer}}(Z) = -0.0254 + 0.016Z - 0.000186Z^2 + 8 \times 10^{-7} Z^3$$

and $f_{\text{energy}}(E_0)$ is the Joy low-energy correction [B4]:

$$f_{\text{energy}}(E_0) = \frac{1}{1 + k\Gamma E_0^{0.5}}$$

### 3.2 Alternatives Considered

| Model | Rejected Because |
|---|---|
| **Arnal formula** [B1] | Similar accuracy to Reimer; no reason to prefer |
| **Linear Z fit** | Insufficient accuracy for Z-contrast |
| **Experimental values only** | Not available for all materials at all energies |

**Engineering Decision:** The Reimer formula with Joy energy correction is used for its coverage of all Z and energy values. For the specific 1 keV nominal energy, the frozen values in the material library are used directly.

### 3.3 Limitations

1. The Reimer formula was developed for $E_0 > 10$ keV. The Joy correction extends it to lower energy with ~15% accuracy [B4].
2. Does not account for thin-film effects (important for <50 nm films).

---

## 4. Pixel Intensity Equation

### 4.1 Selected Model: Linear Combination

$$I(x,y) = G \cdot \Big[ \underbrace{\delta_0(Z) \cdot \sec^\gamma\theta(x,y)}_{\text{SE-I}} \cdot \eta_{\text{coll}}^{\text{SE}}(x,y) + \underbrace{\eta(Z) \cdot \eta_{\text{coll}}^{\text{BSE}}(x,y)}_{\text{BSE}} + \underbrace{I_{\text{SE-II}}(x,y)}_{\text{SE-II background}} \Big] + I_{\text{off}}$$

| Component | Term | Notes |
|---|---|---|
| SE-I signal | $\delta_0 \cdot \sec^\gamma\theta \cdot \eta_{\text{coll}}^{\text{SE}}$ | Primary topographic signal |
| BSE signal | $\eta \cdot \eta_{\text{coll}}^{\text{BSE}}$ | Compositional contrast |
| SE-II background | $I_{\text{SE-II}}$ | Long-range halo (Section 6) |
| System gain | $G$ | Controllable (covers PMT gain + amplifier gain) |
| Offset | $I_{\text{off}}$ | Dark level reference |

### 4.2 Alternatives Considered

| Model | Rejected Because |
|---|---|
| **Nonlinear combination** | No physical basis for nonlinearity at normal signal levels |
| **Lambertian reflectance** | Physically wrong for SE emission [Phase 2.3] |
| **Phong shading** | Specular term has no physical basis in SE imaging |

---

## 5. Probe Point Spread Function

### 5.1 Selected Model: Gaussian

$$\text{PSF}(r) = \frac{1}{2\pi\sigma_p^2} \exp\left(-\frac{r^2}{2\sigma_p^2}\right)$$

where $\sigma_p = d_p / 2.355$ (conversion from FWHM to Gaussian standard deviation).

For material-dependent resolution (escape depth), an additional Gaussian is added in quadrature:

$$\sigma_{\text{eff}}^2 = \sigma_p^2 + \sigma_m^2$$

where $\sigma_m = \Lambda / 2.355$ and $\Lambda$ is the SE escape depth.

### 5.2 Justification

- The Gaussian model is the standard approximation for Schottky FEG probes in CD-SEM [B1][B2].
- It matches measured edge profiles to within ±10% for well-tuned instruments [J1].
- It is computationally efficient (convolution can be implemented spatially or in the frequency domain).

### 5.3 Alternatives Considered

| Model | Rejected Because |
|---|---|
| **Lorentzian** | Broader tails than observed |
| **Bessel (Airy) probe** | Too complex; diffraction negligible in SEM |
| **Empirical multi-Gaussian** | Overfits; requires calibration per tool |

### 5.4 SE-II Background Model

The SE-II background is modeled as a long-range exponential convolution:

$$I_{\text{SE-II}}(x,y) = \eta(Z) \cdot k_{\text{SE-II}} \cdot \iint I_{\text{primary}}(x',y') \cdot \exp\left(-\frac{|r - r'|}{L_{\text{SE-II}}}\right) dx' dy'$$

where $L_{\text{SE-II}}$ is the characteristic decay length (10–100 nm, material-dependent) and $k_{\text{SE-II}}$ is the SE-II generation efficiency.

---

## 6. Detector Collection Model

### 6.1 Selected Model: Simplified Acceptance Function

For TTL detection (default for CD-SEM):

$$\eta_{\text{coll}}^{\text{SE}}(x,y) = \eta_0^{\text{SE}} \cdot \Omega(x,y) / 2\pi$$

where $\Omega(x,y)$ is the solid angle subtended by the detector aperture from point $(x,y)$ and $\eta_0^{\text{SE}}$ is the peak collection efficiency (0.7).

For BSE detection (annular solid-state detector):

$$\eta_{\text{coll}}^{\text{BSE}}(x,y) = \eta_0^{\text{BSE}} \cdot \frac{1}{2}\left[1 + \cos\psi(x,y)\right]$$

where $\psi$ is the angle between the surface normal and the detector axis.

### 6.2 Simplification for First Implementation

$$\eta_{\text{coll}}^{\text{SE}}(x,y) = \text{constant} = 0.7$$

$$\eta_{\text{coll}}^{\text{BSE}}(x,y) = \text{constant} = 0.5$$

**Fact:** For TTL detection at normal incidence and small fields of view, the collection efficiency is approximately uniform. Position-dependent collection adds secondary realism (shadowing, asymmetry) and can be added in Phase B.

---

## 7. Noise Model

### 7.1 Selected Model: Poisson + Excess Noise Scaling

**Stage 1 — Shot noise:**

$$I_{\text{shot}} \sim \text{Poisson}\left(\frac{I_{\text{ideal}}}{G_{\text{eff}}}\right) \cdot G_{\text{eff}}$$

where $G_{\text{eff}}$ is the effective gain relating electrons to digital units:

$$G_{\text{eff}} = \frac{I_P \cdot \tau \cdot (\delta + \eta) \cdot \eta_{\text{coll}} \cdot G}{e \cdot (2^N - 1) / V_{\text{range}}}$$

**Stage 2 — Excess noise (PMT):**

$$I_{\text{noisy}} = I_{\text{shot}} + \sqrt{(F^2 - 1) \cdot I_{\text{shot}} \cdot G_{\text{eff}}} \cdot \mathcal{N}(0,1)$$

where $F = 1.2$ is the PMT excess noise factor and $\mathcal{N}(0,1)$ is standard normal.

### 7.2 Alternatives Considered

| Model | Rejected Because |
|---|---|
| **Additive Gaussian only** | Does not capture signal-dependent noise (incorrect for dark regions) |
| **Pure Poisson** | Sufficient for first implementation; excess noise adds realism |
| **Full Monte Carlo noise** | Too computationally expensive for the same result |

---

## 8. Charging Correction Model

### 8.1 Selected Model: Effective Yield Reduction

$$\delta_{\text{eff}}(Z_{\text{insulator}}) = \delta_0(Z_{\text{insulator}}) \cdot f_c(Z_{\text{insulator}})$$

where $f_c$ is the charging factor (0.3–0.8 for insulators, 1.0 for conductors).

### 8.2 Physical Basis

At positive charging ($\sigma > 1$), the surface potential $V_{\text{surf}} > 0$ attracts emitted SEs back to the sample. The fraction recaptured depends on the surface potential:

$$\frac{\delta_{\text{eff}}}{\delta_0} = 1 - \exp\left(-\frac{V_{\text{surf}}}{V_{\text{SE, mean}}}\right)$$

where $V_{\text{SE, mean}}$ is the mean SE energy (~5 eV). For a charging insulator at 1 keV, $V_{\text{surf}}$ can reach 5–50 V, reducing effective yield by 30–70%.

### 8.3 Simplification

Since $V_{\text{surf}}$ depends on the local charge density, film thickness, conductivity, and time — all of which are complex to simulate — the effective yield reduction is simplified to a material-dependent scaling factor:

$$f_c(\text{SiO}_2) = 0.6 \quad (\text{moderate charging})$$
$$f_c(\text{resist}) = 0.5 \quad (\text{strong charging})$$
$$f_c(\text{conductor}) = 1.0 \quad (\text{no correction})$$

### 8.4 Alternatives Considered

| Model | Rejected Because |
|---|---|
| **Self-consistent electrostatic simulation** | Too complex for first implementation; requires iterative field solution |
| **Time-dependent charging** | Only relevant for long acquisitions |
| **Ignoring charging entirely** | Insulators would appear unrealistically bright |

---

## 9. Digitization Model

### 9.1 Selected Model: Linear ADC with Saturation

$$I_{\text{pixel}} = \text{round}\left( \min\left( \max\left( \frac{I_{\text{noisy}} - I_{\text{off}}}{G_{\text{total}}}, 0 \right), 1 \right) \cdot (2^{N_{\text{bits}}} - 1) \right)$$

### 9.2 Gain and Offset

$$G_{\text{total}} = \frac{I_P \cdot \tau \cdot \eta_{\text{coll}} \cdot G_{\text{PMT}} \cdot R_f}{e \cdot V_{\text{range}}}$$

where all terms are hardware parameters from the parameter library.

---

## 10. Summary: Complete Forward Model

```
Input: Geometry (material ID map + surface normal map)

1. Material Lookup
   δ₀ = mat_lib[mat_id].delta_0
   η  = mat_lib[mat_id].eta
   Λ  = mat_lib[mat_id].escape_depth
   f_c = mat_lib[mat_id].charge_factor

2. SE Yield
   δ = δ₀ · secᵞ(θ)  [clamped for θ > 70°]

3. BSE Contribution
   I_BSE = η · η_coll_BSE

4. Pixel Intensity (pre-blur, pre-noise)
   I_raw = G · [δ · η_coll_SE + I_BSE + I_SE-II_conv] + I_off

5. Probe Convolution
   I_blurred = I_raw * PSF(σ_eff)  [Gaussian]
   where σ_eff² = σ_p² + σ_m²

6. Charging Correction
   δ_eff = δ · f_c  [applied to δ for insulators]

7. Noise
   I_shot ~ Poisson(I_blurred / G_eff) · G_eff
   I_noisy = I_shot + √((F²-1) · I_shot · G_eff) · N(0,1)

8. Digitization
   I_final = round(clamp(I_noisy, 0, I_max) · (2^N_bits - 1))
```

---

## Sources

- [B1] L. Reimer, *Scanning Electron Microscopy: Physics of Image Formation and Microanalysis*, 2nd ed. Springer, 1998.
- [B2] J. I. Goldstein, D. E. Newbury, J. R. Michael, et al., *Scanning Electron Microscopy and X-Ray Microanalysis*, 4th ed. Springer, 2017.
- [B4] D. C. Joy, *Monte Carlo Modeling for Electron Microscopy and Microanalysis*. Oxford University Press, 1995.
- [J1] J. S. Villarrubia, A. E. Vladar, and M. T. Postek, "Scanning electron microscope measurement of width and shape of fabricated nanostructures," *J. Res. NIST*, vol. 109, 2004.
- [J7] H. Seiler, "Secondary electron emission in the scanning electron microscope," *J. Appl. Phys.*, vol. 54, 1983.
- [J4] D. C. Joy and C. S. Joy, "Low-voltage scanning electron microscopy," *Micron*, vol. 27, 1996.
