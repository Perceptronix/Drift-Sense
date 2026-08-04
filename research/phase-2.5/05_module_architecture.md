# Module Architecture

**Research Phase:** 2.5
**Document:** 05_module_architecture.md
**Date:** 2026-07-30

---

## 1. Module Overview

The renderer is organized into 8 logical modules. Each module has a single responsibility, a well-defined interface, and no side effects.

```
┌─────────────────────────────────────────────────────────────────┐
│                     Renderer Coordinator                         │
│  (orchestrates pipeline execution, manages config, calls modules) │
└──┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬──────────┘
   │   │   │   │   │   │   │   │   │   │   │   │   │   │
   ▼   ▼   ▼   ▼   ▼   ▼   ▼   ▼   ▼   ▼   ▼   ▼   ▼   ▼
┌─────┐┌─────┐┌─────┐┌─────┐┌─────┐┌─────┐┌─────┐┌─────┐
│ Geom ││ Mat ││Yield││ Det ││ PSF ││Charge││Noise││Digit│
│ etry ││erial││     ││ector││     ││ ing ││     ││ izat│
│      ││ Lib ││     ││     ││     ││     ││     ││ ion │
└─────┘└─────┘└─────┘└─────┘└─────┘└─────┘└─────┘└─────┘
```

---

## 2. Module Specifications

### 2.1 Geometry Module

| Aspect | Specification |
|---|---|
| **Responsibility** | Load, validate, and process the 3D structure. Compute surface normals and local angles. |
| **Input** | Geometry file (format TBD — 2.5D height map recommended). Material ID per pixel. |
| **Output** | Height field $h[M][N]$, Material ID field $m[M][N]$, Surface normal field $\hat{n}[M][N]$, Local angle field $\theta[M][N]$ |
| **Core computation** | $\theta(x,y) = \arccos(\hat{n}(x,y) \cdot \hat{z})$ where $\hat{n}$ is computed from height gradients via central differences. |
| **Memory** | $4 \times M \times N$ floats for $(h, \theta, n_x, n_y)$, plus $M \times N$ ints for material IDs |
| **Dependencies** | None |
| **Validation** | Verify normals are unit vectors ($|n| = 1 \pm \epsilon$). Verify $\theta \in [0, \pi/2]$. |

**Edge case handling:**
- Vertical sidewalls ($\theta \approx 90^\circ$): The $\sec\theta$ model uses the clamped value for $\theta > 70^\circ$.
- Re-entrant features ($\theta > 90^\circ$): Treat as $\theta = 90^\circ$ for yield estimation; flag for detector shadowing.
- Flat regions ($\theta \approx 0^\circ$): Normal yield — no special handling.

### 2.2 Material Library

| Aspect | Specification |
|---|---|
| **Responsibility** | Provide per-material physical properties used by all other modules. |
| **Input** | Material ID (integer), beam energy $E_0$ |
| **Output** | Property vector: $\{\delta_0, \eta, \Lambda, f_c, \gamma, \text{type}, Z\}$ |
| **Core data** | Table of 6 materials × 7 properties (frozen — see Parameter Library) |
| **Memory** | Negligible ($< 1$ KB for 6 materials) |
| **Dependencies** | None |
| **Validation** | Verifiable against Phase 2.2 and literature values [B1][B2][B4] |

**Material table structure:**

```
MaterialDef {
    int material_id;
    string name;            // e.g., "Si", "SiO2"
    float Z_avg;            // average atomic number
    float density;          // g/cm³
    float delta_0;          // SE yield at normal incidence
    float eta;              // BSE yield
    float escape_depth_nm;  // SE escape depth (nm)
    float charge_factor;    // 0.0–1.0 charging scaling
    float gamma;            // secant exponent (usually 1.0)
    MaterialType type;      // CONDUCTOR, SEMICONDUCTOR, INSULATOR
};
```

### 2.3 Yield Engine

| Aspect | Specification |
|---|---|
| **Responsibility** | Compute per-pixel SE and BSE yield from material properties and surface geometry. |
| **Input** | $\delta_0[M][N]$, $\eta[M][N]$, $\theta[M][N]$, $\gamma$ |
| **Output** | $\delta[M][N]$, $\eta[M][N]$ (per-pixel yield arrays) |
| **Core computation** | $$\delta(x,y) = \delta_0(x,y) \cdot \sec^\gamma(\theta(x,y))$$ with clamping: if $\theta > 70^\circ$, $\delta = \delta_0 \cdot \sec^\gamma(70^\circ)$ |
| **Memory** | $2 \times M \times N$ floats |
| **Dependencies** | Geometry module (for $\theta$), Material Library (for $\delta_0$, $\eta$, $\gamma$) |

**BSE note:** $\eta(x,y) = \eta_0(x,y)$ — BSE yield has no angular dependence at this level (the flat-surface yield is used directly).

### 2.4 Detector Module

| Aspect | Specification |
|---|---|
| **Responsibility** | Compute collection efficiency for SE and BSE channels based on detector geometry. |
| **Input** | Surface normals $\hat{n}[M][N]$, pixel positions, detector type |
| **Output** | $\eta_{\text{coll}}^{\text{SE}}[M][N]$, $\eta_{\text{coll}}^{\text{BSE}}[M][N]$ |
| **Core computation (Phase A)** | Constants: $\eta_{\text{coll}}^{\text{SE}} = 0.7$, $\eta_{\text{coll}}^{\text{BSE}} = 0.5$ |
| **Core computation (Phase C)** | TTL: solid-angle based; E-T: cosine-weighted directional |
| **Memory** | $2 \times M \times N$ floats |
| **Dependencies** | Geometry module |

### 2.5 PSF Module

| Aspect | Specification |
|---|---|
| **Responsibility** | Build and apply the point spread function convolution kernel. |
| **Input** | Raw intensity $I_{\text{raw}}[M][N]$, probe diameter $d_p$, escape depth map $\Lambda[M][N]$ |
| **Output** | Blurred intensity $I_{\text{blurred}}[M][N]$ |
| **Core computation** | Build Gaussian kernel: $K(r) \propto \exp(-r^2 / 2\sigma_{\text{eff}}^2)$ where $\sigma_{\text{eff}}^2 = (d_p/2.355)^2 + (\Lambda(x,y)/2.355)^2$. Convolve $I * K$. |
| **Memory** | $M \times N$ floats (output), plus kernel (small, e.g., $31 \times 31$) |
| **Dependencies** | Yield engine (for intensity), Material Library (for $\Lambda$) |

**Implementation notes:**
- Use separable Gaussian convolution (1D horizontal + 1D vertical) for efficiency.
- Kernel radius = $3\sigma_{\text{eff}}$ (typical $5 \times 5$ to $15 \times 15$ pixels).
- Material-dependent $\sigma_m$ requires position-dependent kernel. Use the local $\Lambda$ at each pixel — this is physically correct for the escape depth contribution.

### 2.6 Charging Module

| Aspect | Specification |
|---|---|
| **Responsibility** | Apply charging correction to SE yield for insulating materials. |
| **Input** | $\delta[M][N]$, charging factor $f_c[M][N]$, material type |
| **Output** | Modified $\delta_{\text{eff}}[M][N]$ |
| **Core computation** | For each pixel: if material is INSULATOR, $\delta_{\text{eff}} = \delta \cdot f_c$. Otherwise $\delta_{\text{eff}} = \delta$. |
| **Memory** | $M \times N$ floats |
| **Dependencies** | Material Library (for $f_c$, type), Yield Engine (for $\delta$) |

### 2.7 Noise Module

| Aspect | Specification |
|---|---|
| **Responsibility** | Apply shot noise (Poisson) and PMT excess noise to the signal. |
| **Input** | Pre-noise intensity $I[M][N]$, effective gain $G_{\text{eff}}$, excess noise factor $F$, random seed |
| **Output** | Noise-corrupted intensity $I_{\text{noisy}}[M][N]$ |
| **Core computation** | $$I_{\text{shot}} \sim \text{Poisson}(I / G_{\text{eff}}) \cdot G_{\text{eff}}$$ $$I_{\text{noisy}} = I_{\text{shot}} + \sqrt{(F^2 - 1) \cdot I_{\text{shot}} \cdot G_{\text{eff}}} \cdot \mathcal{N}(0,1)$$ |
| **Memory** | $M \times N$ floats |
| **Dependencies** | PSF Module (for $I$) |

**Implementation notes:**
- For Poisson generation, use a standard algorithm (e.g., Knuth's algorithm or Marsaglia's method for $\lambda > 30$).
- The random seed allows reproducible noise generation.

### 2.8 Digitization Module

| Aspect | Specification |
|---|---|
| **Responsibility** | Convert analog voltage to digital pixel values. Apply saturation and quantization. |
| **Input** | Analog intensity $I_{\text{noisy}}[M][N]$, ADC bits $N_{\text{bits}}$, max voltage $V_{\text{max}}$ |
| **Output** | Final pixel values $I_{\text{pixel}}[M][N]$ (16-bit integers) |
| **Core computation** | $$I_{\text{pixel}} = \text{round}\left( \min\left(\max\left(\frac{I_{\text{noisy}}}{V_{\text{max}}}, 0\right), 1\right) \cdot (2^{N_{\text{bits}}} - 1) \right)$$ |
| **Memory** | $M \times N$ 16-bit ints (output) |
| **Dependencies** | Noise Module |

---

## 3. Module Interfaces Summary

| Module | Inputs | Outputs | Called By |
|---|---|---|---|
| **Geometry** | Geometry file | $h$, $m$, $\hat{n}$, $\theta$ | Coordinator |
| **Material Lib** | Material ID, $E_0$ | $\delta_0$, $\eta$, $\Lambda$, $f_c$, $\gamma$, type, $Z$ | All modules |
| **Yield Engine** | $\delta_0$, $\eta$, $\theta$, $\gamma$ | $\delta$, $\eta$ | Coordinator → Detector |
| **Detector** | $\hat{n}$, pixel position | $\eta_{\text{coll}}^{\text{SE}}$, $\eta_{\text{coll}}^{\text{BSE}}$ | Coordinator |
| **PSF** | $I_{\text{raw}}$, $d_p$, $\Lambda$ | $I_{\text{blurred}}$ | Coordinator |
| **Charging** | $\delta$, $f_c$, material type | $\delta_{\text{eff}}$ | Coordinator (between Yield and PSF) |
| **Noise** | $I$, $G_{\text{eff}}$, $F$, seed | $I_{\text{noisy}}$ | Coordinator |
| **Digitization** | $I_{\text{noisy}}$, $N_{\text{bits}}$, $V_{\text{max}}$ | $I_{\text{pixel}}$ | Coordinator (final stage) |

---

## 4. Data Flow Diagram

```
Geometry File
    │
    ▼
┌─────────┐    ┌──────────────┐
│Geometry │    │Material Lib  │
│Module   │    │(initialized  │
│         │    │ once at load)│
└────┬────┘    └──────┬───────┘
     │                │
     ▼                ▼
┌─────────┐    ┌──────────────┐
│Yield    │◄───│ δ₀, η, γ, Λ │
│Engine   │    └──────────────┘
└────┬────┘
     │ δ, η           ┌──────────┐
     ▼                │SE-II     │
┌─────────┐◄─────────│(from BSE)│
│Detector │           └──────────┘
└────┬────┘
     │ η_coll_SE, η_coll_BSE
     ▼
┌─────────┐     ┌──────────┐
│Pixel    │◄────│ PSF      │
│Intensity│────►│(blur)    │
│(raw)    │     └────┬─────┘
└────┬────┘          │
     │               ▼
     │          ┌─────────┐    ┌──────────┐
     │          │Charging │    │(modifies │
     └─────────►│Correction│   │ δ for    │
                │         │    │insulators│
                └────┬────┘    └──────────┘
                     │
                     ▼
                ┌─────────┐
                │Gain +   │
                │Offset   │
                └────┬────┘
                     │
                     ▼
                ┌─────────┐
                │Noise    │
                │(Poisson)│
                └────┬────┘
                     │
                     ▼
                ┌─────────┐
                │Digitize │
                │(ADC)    │
                └────┬────┘
                     │
                     ▼
               Final Image
```

---

## 5. Module Design Principles

| Principle | Application |
|---|---|
| **Single responsibility** | Each module does exactly one thing (yield, blur, noise, etc.). |
| **Deterministic where possible** | Geometry, material, yield, detector, and PSF modules are deterministic (same input → same output). Only the noise module is stochastic. |
| **No side effects** | Modules compute outputs from inputs and return. They do not modify global state. |
| **Ease of testing** | Each module can be tested independently with synthetic inputs. |
| **Configurable** | The `RendererCoordinator` holds all config (probe diameter, current, dwell time, etc.) and passes relevant parameters to each module. |
| **Phase evolution** | Modules can be upgraded from constant (Phase A) to physics-based (Phase C) without changing their interfaces. |

---

## Sources

- [B1] L. Reimer, *Scanning Electron Microscopy: Physics of Image Formation and Microanalysis*, 2nd ed. Springer, 1998.
- [B2] J. I. Goldstein, D. E. Newbury, J. R. Michael, et al., *Scanning Electron Microscopy and X-Ray Microanalysis*, 4th ed. Springer, 2017.
- [B4] D. C. Joy, *Monte Carlo Modeling for Electron Microscopy and Microanalysis*. Oxford University Press, 1995.
- [J1] J. S. Villarrubia, A. E. Vladar, and M. T. Postek, "Scanning electron microscope measurement of width and shape of fabricated nanostructures," *J. Res. NIST*, vol. 109, 2004.
