# Line Edge and Line Width Roughness

**Research Phase:** 3.3
**Document:** 02_line_edge_and_line_width_roughness.md
**Date:** 2026-07-30

---

## 1. Physical Origin of LER

Line edge roughness arises from three fundamental sources in the lithography process:

| Source | Origin | Typical Contribution | Mitigation |
|---|---|---|---|
| **Photon shot noise** | Random arrival of EUV photons in the resist | Large contributor at EUV (fewer photons per area) | Higher dose, thinner resist |
| **Acid diffusion** | Random walk of photo-acid during PEB | Medium — blurs the image but also smoothes shot noise | Optimized PEB time |
| **Polymer dissolution** | Statistical nature of polymer chain deprotection | Medium — resist-dependent | Improved resist chemistry |
| **Mask roughness** | Phase errors, multilayer roughness | Small (<10% of total) | Improved mask blank quality |

**Inference:** At EUV wavelengths (13.5 nm), photon shot noise is the dominant LER source because the number of photons per unit area is ~14× fewer than at 193 nm for the same intensity. This makes EUV LER fundamentally different from 193 nm lithography in both magnitude and correlation structure.

### 1.1 LER Transfer Through Pattern Transfer

The resist LER is partially transferred to the underlying layer during etching:

| Transfer Step | LER Amplitude Change | Notes |
|---|---|---|
| Resist → Hardmask | Attenuated (S = 0.5–1.0) | Etch selectivity smooths or preserves |
| Hardmask → Film | Attenuated or amplified | Depends on etch chemistry |
| Film → Substrate | Additional roughness from etch | Sidewall roughness from ion scattering |

**Fact:** The final post-etch LER is the result of resist LER convolved with the etch transfer function. Etch can either smooth (isotropic component) or amplify (anisotropic, ion scattering) the initial resist roughness [M14].

---

## 2. LER Characterization

### 2.1 Key Parameters

| Parameter | Symbol | Definition | Units |
|---|---|---|---|
| RMS amplitude | $\sigma_{\text{LER}}$ | Standard deviation of edge position from mean | nm |
| 3σ amplitude | $3\sigma_{\text{LER}}$ | Peak-to-peak (99.7% confidence) | nm |
| Correlation length | $\xi$ | Distance over which roughness is correlated | nm |
| Roughness exponent | $\alpha$ | High-frequency roll-off (0 < α < 1) | — |
| PSD integral | $\sigma^2$ | Variance = power spectral density integral | nm² |

### 2.2 Typical Values by Technology Node

| Node | Lithography | LER 3σ (nm) | Correlation Length ξ (nm) | Source |
|---|---|---|---|---|
| 45 nm | 193 nm immersion | 3.5–5.0 | 30–50 | [M3][M5] |
| 28 nm | 193 nm immersion + SADP | 3.0–4.5 | 25–40 | [M3] |
| 14 nm | EUV + SAQP | 2.5–3.5 | 20–30 | [M1][M10] |
| 7 nm (N7) | EUV single | 2.0–3.0 | 15–25 | [M10][M11] |
| 5 nm (N5) | EUV + multi-patterning | 1.8–2.8 | 15–20 | [M1] |
| 3 nm (N3) | EUV + LELE | 1.5–2.5 | 10–20 | [M10] |

**Engineering Decision:** The default LER amplitude is 2.4 nm (3σ) with correlation length 25 nm. This represents a typical N5 EUV process.

### 2.3 Autocorrelation Function

The standard model for LER autocorrelation is exponential:

$$R(\Delta y) = \sigma_{\text{LER}}^2 \cdot \exp\left(-\frac{|\Delta y|}{\xi}\right)$$

| Model | Form | Suitability |
|---|---|---|
| **Exponential** | $\exp(-\mid\Delta y\mid / \xi)$ | **Recommended** — simplest, matches measured LER well |
| Gaussian | $\exp(-\Delta y^2 / \xi^2)$ | Overestimates correlation at large distances |
| Fractal (power law) | $(\mid\Delta y\mid)^{-2\alpha}$ | No correlation length — unphysical for lithography |
| Exponential + fractal | $(\Delta y)^\alpha \cdot \exp(-\mid\Delta y\mid / \xi)$ | More accurate for EUV; requires two parameters |
| Exponentially damped cosine | $\exp(-\mid\Delta y\mid / \xi) \cdot \cos(q_0 \Delta y)$ | Oscillatory component visible in some resists |

**Engineering Decision:** The exponential autocorrelation model is selected as the baseline. The roughness exponent α is added as a secondary parameter (α = 0.5) for the PSD model.

### 2.4 Power Spectral Density (PSD)

The PSD of LER determines the frequency content of the roughness:

$$PSD(f) = \frac{2\sigma^2_{\text{LER}} \xi}{1 + (2\pi f \xi)^2}$$

This is the Lorentzian PSD corresponding to the exponential autocorrelation.

**Engineering Decision:** LER is generated in the **spatial domain** using the autocorrelation function (not the frequency domain) for simplicity. The PSD is used for validation against published CD-SEM LER measurements.

---

## 3. LWR — Line Width Roughness

### 3.1 Relation to LER

Line width roughness is derived from the LER of the left and right edges:

$$\text{LWR}(y) = \text{LER}_{\text{left}}(y) + \text{LER}_{\text{right}}(y)$$

| Property | Value | Derivation |
|---|---|---|
| LWR variance | $\sigma^2_{\text{LWR}} = 2\sigma^2_{\text{LER}}(1 + \rho)$ | $\rho$ = correlation between left and right edges |
| Uncorrelated edges | $\sigma_{\text{LWR}} = \sqrt{2} \sigma_{\text{LER}}$ | If $\rho = 0$ |
| Fully correlated | $\sigma_{\text{LWR}} = 2\sigma_{\text{LER}}$ | If $\rho = 1$ (unphysical; edges move together) |
| Typical ($\rho$ ≈ 0.5) | $\sigma_{\text{LWR}} \approx 1.73\sigma_{\text{LER}}$ | Moderate correlation from EUV |

**Fact:** For EUV lithography, the left and right edge roughnesses are partially correlated because both edges originate from the same resist image [M11]. The cross-correlation coefficient is typically $\rho$ = 0.2–0.5.

### 3.2 LWR Characterization

| Parameter | Symbol | Relationship to LER | Default Value (N5) |
|---|---|---|---|
| LWR RMS | $\sigma_{\text{LWR}}$ | $\sqrt{2} \sigma_{\text{LER}}$ (uncorrelated) | 3.4 nm |
| LWR correlation length | $\xi_{\text{LWR}}$ | Same as $\xi_{\text{LER}}$ | 25 nm |
| LWR spectrum | $PSD_{\text{LWR}}$ | Broadened vs. LER PSD | — |

**Engineering Decision:** LWR is modeled by generating LER independently for the left and right edges of each line with $\rho = 0.3$ cross-correlation, then computing width as the difference.

---

## 4. LER Implementation Model

### 4.1 Generation Method: Correlated Gaussian Random Process

```
For each edge:
  1. Sample i.i.d. Gaussian random variables: g(k) ~ N(0, 1)
     at positions y_k = k × Δy (Δy = pixel size)
  
  2. Apply correlation via exponential filter:
     h(n) = exp(-|n × Δy| / ξ)
     d(y) = σ_LER × (g * h)(y) / ||h||
     where * is convolution, ||h|| normalizes variance
  
  3. Apply to nominal edge position:
     x_edge(y) = x_nominal(y) + d(y)
  
  4. Clamp amplitude to [−3σ, +3σ] to prevent unphysical excursions
```

### 4.2 Cross-Correlation for LWR

```
Step 1: Generate LER_left and LER_right with correlation ρ:
    d_left(y) = independent_realization(y, σ_LER, ξ)
    d_right(y) = ρ·d_left(y) + √(1-ρ²)·independent_realization(y, σ_LER, ξ)

Step 2: Compute width:
    CD(y) = x_right(y) - x_left(y)
    where x_right = x_nominal_right + d_right
          x_left  = x_nominal_left + d_left

Result: σ²_LWR = σ²_LER + σ²_LER - 2ρ·σ²_LER = 2σ²_LER(1 - ρ)
```

### 4.3 Impact on SEM Appearance

| Effect | Description | Magnitude |
|---|---|---|
| **Edge profile broadening** | LER blurs the SEM edge profile | ∼σ_LER additional blur |
| **CD measurement variance** | CD varies along the line | 3σ_CD ≈ LWR |
| **Peak position variation** | Brightness peaks shift locally | ∼σ_LER |
| **Local contrast reduction** | Rough edges reduce apparent contrast | Small for σ < 3 nm |

---

## 5. LER Validation Against Literature

| Source | σ_LER (3σ) | ξ (nm) | Measurement Method | Match with Default? |
|---|---|---|---|---|
| Habermas et al. 2018 [M1] | 2.0–3.0 | 15–25 | CD-SEM, N7 EUV | ✓ (2.4 nm in range) |
| Mack 2009 [M3] | 3.0–5.0 | 30–50 | CD-SEM, 193 nm | ∼(different node) |
| Bunday et al. 2003 [M4] | 3.5–6.0 | — | CD-SEM, various | ∼(mature nodes) |
| Lorusso et al. 2016 [M11] | 2.5–3.5 | 20–30 | CD-SEM, EUV | ✓ (in range) |
| imec N5 data [M10] | 1.8–2.8 | 15–20 | CD-SEM + AFM | ✓ (2.4 nm selected) |
| ITRS 2022 [M2] | 2.2 (target) | — | Roadmap | Close |

**Inference:** The selected default values are consistent with published data for the target node. The spread in published values (factor of 2 between different studies at the same nominal node) reflects real differences in process maturity and measurement methodology.

---

## 6. LER in 2.5D Height Field

### 6.1 Application to Height Field

LER is applied as an **edge perturbation** to the height field:

```
For each feature edge (identified from material map):
  1. Extract the nominal edge position as a function of Y:
     x_nominal(y) = position where material ID changes
  
  2. Generate LER displacement d(y) with specified σ and ξ
  
  3. Apply displacement:
     x_edge(y) = x_nominal(y) + d(y)
  
  4. Recompute height field:
     - For each pixel (x, y), compute distance to the displaced edge
     - If x < x_edge(y): material = feature (e.g., resist)
     - If x > x_edge(y): material = surrounding (e.g., substrate)
     - Height is interpolated across the transition width
```

**Fact:** This approach preserves the 2.5D height field structure while adding realistic edge roughness. The height field remains single-valued (no overhangs) — the roughness is a lateral displacement of the feature boundary.

### 6.2 Constraints

| Constraint | Rationale |
|---|---|
| LER ≤ 0.3 × CD | Prevents rough edges from overlapping on narrow lines |
| LER cannot cross neighboring features | Enforced by clamping at line midpoints |
| Correlation length ≥ 2× pixel size | Prevents aliasing of high-frequency roughness |

---

## 7. Recommended Defaults

| Parameter | Symbol | Default | Rationale |
|---|---|---|---|
| LER 3σ | 2.4 nm | Typical N5 EUV | |
| Correlation length | ξ | 25 nm | Typical EUV |
| Roughness exponent | α | 0.5 | Standard value |
| Left-right correlation | ρ | 0.3 | Moderate EUV correlation |
| LWR 3σ | (derived) | 3.4 nm | √2 × LER for ρ = 0.3 |
| Max LER (clamp) | | 3σ | Prevent unphysical excursions |

---

## Sources

- [M1] A. Habermas et al., "LER and LWR metrology: overview and roadmap," *Proc. SPIE*, vol. 10583, 2018.
- [M2] IRDS, "Lithography and Metrology Roadmap," 2023.
- [M3] C. A. Mack, "Line edge roughness," *J. Micro/Nanolith. MEMS MOEMS*, vol. 8, no. 4, 2009.
- [M4] B. D. Bunday et al., "CD-SEM metrology," *Proc. SPIE*, vol. 5038, 2003.
- [M5] P. P. Naulleau et al., "EUV lithography variability," *Proc. SPIE*, vol. 8679, 2013.
- [M10] imec, "EUV lithography variability at N5," *Proc. SPIE*, vol. 10957, 2019.
- [M11] G. F. Lorusso et al., "LER transfer in EUV lithography," *Proc. SPIE*, vol. 9776, 2016.
- [M14] D. L. Goldfarb et al., "Pattern transfer of LER," *J. Vac. Sci. Technol. B*, vol. 30, 2012.
