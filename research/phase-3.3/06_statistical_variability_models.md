# Statistical Variability Models

**Research Phase:** 3.3
**Document:** 06_statistical_variability_models.md
**Date:** 2026-07-30

---

## 1. Model Selection Framework

Each variability mechanism is assigned the simplest statistical model that captures its essential behavior.

| Selection Criterion | Weight | Description |
|---|---|---|
| **Physical basis** | High | Model should match the known physical origin |
| **Parameter count** | High | Prefer 1–3 parameters per source (fewer is better) |
| **Validation** | Medium | Model output should match published data |
| **Implementation simplicity** | Medium | Must be feasible within the geometry generator |

---

## 2. Model Candidate Comparison

### 2.1 LER Edge Displacement

| Model | Parameters | Physical Basis | Implementation Complexity | Verdict |
|---|---|---|---|---|
| **Gaussian random process with exponential autocorrelation** | $\sigma_{\text{LER}}, \xi$ | Matches measured LER PSD [M1][M3] | Moderate | **Selected** |
| White noise (uncorrelated) | $\sigma_{\text{LER}}$ | No — LER has known correlation | Low | Rejected (no correlation) |
| Fractal (power-law PSD) | $\sigma_{\text{LER}}, \alpha$ | Some physical basis [M3] | High | Rejected (over-parameterized) |
| Perlin noise | $\sigma_{\text{LER}}$, octaves | No physical basis | Low | **Rejected** (no literature support) |
| AR(1) process | $\sigma_{\text{LER}}, \phi$ | Equivalent to exponential ACF | Low | Acceptable (discrete form) |

**Selected model:** Gaussian random process with exponential autocorrelation $R(\Delta y) = \sigma_{\text{LER}}^2 \cdot \exp(-|\Delta y| / \xi)$.

### 2.2 CD Uniformity (Field-Level)

| Model | Parameters | Verdict |
|---|---|---|
| **Gaussian** | $\mu, \sigma$ | **Selected** — central limit theorem applies |
| Truncated Gaussian | $\mu, \sigma$, bounds | Acceptable (clamp at ±3σ) |
| Log-normal | $\mu, \sigma$ | Not applicable (CD can be below nominal) |

### 2.3 Overlay Error

| Model | Parameters | Verdict |
|---|---|---|
| **Gaussian** | $\mu = 0, \sigma$ | **Selected** — standard semiconductor overlay model |
| Truncated Gaussian | $\mu = 0, \sigma$, bounds | Acceptable with clamp at ±3σ |

**Inference:** Overlay errors are the sum of many small independent contributions (alignment sensor noise, stage positioning, mask alignment). The central limit theorem applies → Gaussian.

### 2.4 Sidewall Angle

| Model | Parameters | Verdict |
|---|---|---|
| **Truncated Gaussian** | $\mu, \sigma$, bounds [85°, 89°] | **Selected** — bounded by physics |
| Beta distribution | $\alpha, \beta$ | Acceptable but over-parameterized |
| Uniform within range | min, max | Not recommended (no peak at nominal) |

### 2.5 Film Thickness

| Model | Parameters | Verdict |
|---|---|---|
| **Gaussian (relative)** | $\mu, \sigma_{\text{rel}}$ | **Selected** — supported by deposition data [M15] |
| Truncated Gaussian | $\mu, \sigma$, bounds [−5%, +5%] | Acceptable |

### 2.6 CMP Dishing

| Model | Parameters | Verdict |
|---|---|---|
| **Parabolic profile + Gaussian depth** | $d_0, \text{CD}_0, \beta, \sigma$ | **Selected** — physics-based [M16] |
| Uniform random depth | $d_{\min}, d_{\max}$ | Rejected — no dishing shape |
| Full mechanistic CMP model | Many | Overkill for geometry generation |

---

## 3. Selected Models Summary

| Variation | Model | Parameters | Generation Method |
|---|---|---|---|
| **LER** | Gaussian random process, exponential ACF | $\sigma_{\text{LER}}$, $\xi$ | Filtered Gaussian noise (Section 4) |
| **LWR** | Derived from two correlated LER realizations | $\sigma_{\text{LER}}$, $\xi$, $\rho$ | $d_{\text{right}} = \rho d_{\text{left}} + \sqrt{1-\rho^2} g_{\text{ind}}$ |
| **CDU (field)** | Gaussian | $\mu_{\text{CD}}$, $\sigma_{\text{CD}}$ | Random offset per field |
| **CDU (wafer)** | Gaussian + radial parabolic | $A$, $R$, $\sigma_{\text{wafer}}$ | $\Delta\text{CD}(r) = A(r/R)^2 + \epsilon$ |
| **Overlay (trans.)** | Gaussian | $0$, $\sigma_{\text{overlay}}$ | Random shift per layer |
| **Overlay (rotation)** | Gaussian | $0$, $\sigma_{\theta}$ | Random rotation per layer |
| **Sidewall angle** | Truncated Gaussian | $\mu_\theta$, $\sigma_\theta$, [85°, 89°] | Per-feature random sample |
| **Thickness** | Gaussian relative | $\mu_T$, $\sigma_{T,\text{rel}}$ | Per-layer random sample |
| **Corner radius** | Gaussian | $\mu_R$, $\sigma_R$ | Per-feature random sample |
| **CMP dishing** | Parabolic + Gaussian | $d_0$, $\text{CD}_0$, $\sigma_{\text{dish}}$ | Deterministic profile + depth noise |
| **CMP erosion** | Density-linear + Gaussian | $e_0$, $\gamma$, $\sigma_{\text{erosion}}$ | $h = h_0(1 - e_0 \rho_{\text{pattern}}) + \epsilon$ |

---

## 4. Random Process Generation: LER

### 4.1 Algorithm: Filtered Gaussian Noise

This is the standard method for generating LER with a specified autocorrelation:

```
Input: σ_LER, ξ (nm), Δy (pixel size, nm), L (line length, nm)

1. N = L / Δy (number of samples)

2. Generate white noise:
   g[k] ~ N(0, 1), for k = 0, 1, ..., N-1

3. Generate autocorrelation filter:
   h[n] = exp(-|n·Δy| / ξ), for n = -(N-1), ..., N-1
   Normalize: h = h / ||h||_2

4. Convolve:
   d = σ_LER · (g * h)
   where * = convolution

5. Boundary handling:
   d[k] valid for k where filter fits in domain
   Edge padding: reflect or zero-pad

6. Optional: Clamp to ±3σ_LER

Output: d[k] (edge displacement in nm at each position k)
```

### 4.2 Computational Complexity

| Parameter | Cost |
|---|---|
| Convolution (direct) | O(N × N) — slow for N > 1000 |
| Convolution (FFT) | O(N log N) — efficient |
| Convolution (FIR, truncated) | O(N × M) where M = 5ξ/Δy |

**Fact:** A typical line of 1024 pixels with ξ = 25 nm and Δy = 1 nm gives a filter length M ≈ 5 × 25 = 125. Direct FIR convolution: 1024 × 125 ≈ 128K operations — negligible for a single line.

### 4.3 Validation Against Published Data

The generated LER should match:
- $\sigma_{\text{LER}}$: measured RMS amplitude (±5% of target)
- Correlation length $\xi$: measured ACF 1/e point (±10% of target)
- PSD shape: Lorentzian $PSD(f) \propto (1 + (2\pi f \xi)^2)^{-1}$

---

## 5. Correlated Random Variables

### 5.1 Generating Correlated Parameters

For parameters that are correlated (e.g., CD and sidewall angle), the method is:

```
Input: Correlation matrix Σ, parameter means μ, standard deviations σ

1. Cholesky decomposition: Σ = LL^T
2. Generate independent standard normals: z ~ N(0, I)
3. Transform: x = μ + σ · Lz
   (where σ is the diagonal matrix of standard deviations)
```

**Engineering Decision:** Only LER left/right correlation is modeled explicitly (ρ). Most other parameters (CD, thickness, sidewall angle) are treated as independent to first order. Correlation between parameters is a Phase D enhancement.

### 5.2 Spatial Correlation

| Variation | Spatial Correlation | Correlation Length |
|---|---|---|
| LER along edge | **Exponential ACF** | 15–25 nm |
| CDU across wafer | **Radial** | 10–300 mm |
| Thickness | **Radial** | 50–300 mm |
| Sidewall angle | **Radial** (systematic) | 50–300 mm |

---

## 6. Recommended Default Random Seeds

| Use Case | Seed | Rationale |
|---|---|---|
| **Validation** | Fixed (e.g., 42) | Reproducible output |
| **Single image generation** | Random | Different each time |
| **Array generation for statistics** | Systematic (seed = scene_id × 1000) | Traceable |
| **Testing** | Fixed | Deterministic tests |

---

## 7. Model Implementation Priority

| Model | Complexity | Phase | Priority |
|---|---|---|---|
| LER (filtered Gaussian noise) | Moderate | Phase A | 1 |
| LWR (two correlated edges) | Low | Phase A | 2 |
| Sidewall angle variation | Low | Phase C | 3 |
| Thickness variation | Low | Phase C | 4 |
| Corner radius variation | Low | Phase C | 5 |
| CDU field | Low | Phase C | 6 |
| Overlay translation | Low | Phase C | 7 |
| CMP dishing variation | Moderate | Phase D | 8 |
| CDU wafer (radial) | Low | Phase D | 9 |
| Overlay rotation | Low | Phase D | 10 |
| CMP erosion | Moderate | Phase D | 11 |
| Cross-parameter correlation | High | Future | 12 |

---

## Sources

- [M1] Habermas et al., "LER and LWR metrology," *Proc. SPIE*, vol. 10583, 2018.
- [M3] C. A. Mack, "Line edge roughness," *J. Micro/Nanolith. MEMS MOEMS*, vol. 8, 2009.
- [M11] Lorusso et al., "LER transfer in EUV lithography," *Proc. SPIE*, vol. 9776, 2016.
- [M14] Goldfarb et al., "Pattern transfer of LER," *J. Vac. Sci. Technol. B*, vol. 30, 2012.
- [M15] Olsen et al., "Thickness variation effects," *IEEE Trans. Semi. Manuf.*, vol. 18, 2005.
- [M16] Park et al., "CMP modeling," *J. Electrochem. Soc.*, vol. 149, 2002.
- [M17] T. Mitsui et al., "Stochastic modeling of EUV LER," *Proc. SPIE*, vol. 10957, 2019.
