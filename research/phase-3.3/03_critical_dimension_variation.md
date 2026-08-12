# Critical Dimension Variation

**Research Phase:** 3.3
**Document:** 03_critical_dimension_variation.md
**Date:** 2026-07-30

---

## 1. CD Variation Components

CD variation has three spatial components:

| Component | Spatial Scale | Source | Magnitude (3σ, N5) |
|---|---|---|---|
| **Across-feature** | Feature level (nm–μm) | LER, LWR, local etch variation | 2–5 nm |
| **Across-die** | Die level (mm–cm) | Mask CDU, lens aberrations, dose variation | 1–3 nm |
| **Across-wafer** | Wafer level (10–300 mm) | CMP uniformity, etch radial variation, thermal effects | 2–8 nm |

**Fact:** Across-feature variation (LER/LWR) is modeled in Document 02 as the dominant contribution. Across-die and across-wafer variation add larger-scale CD changes that are visible in SEM images at moderate-to-large FOV.

---

## 2. Across-Die CD Variation

### 2.1 Sources

| Source | Origin | Pattern | Magnitude (3σ, N5) |
|---|---|---|---|
| **Mask CDU** | Mask writer and etch | Fixed pattern per mask | 1.0–1.5 nm |
| **Lens aberrations** | Projection optics | Low-order Zernike polynomials | 0.5–1.0 nm |
| **Dose variation** | Source intensity | Radial or slit-uniform | 0.5–1.5 nm |
| **Focus variation** | Wafer topography | Field position dependent | 0.5–1.0 nm |

### 2.2 Across-Field CD Model

For a given die (scanner field), the CD variation is modeled as a smooth spatial function:

$$\Delta\text{CD}(x, y) = \Delta\text{CD}_{\text{dose}} + \Delta\text{CD}_{\text{aberration}}(r) + \Delta\text{CD}_{\text{linear}}(x, y) + \Delta\text{CD}_{\text{random}}$$

where:
| Term | Model | Parameters |
|---|---|---|
| $\Delta\text{CD}_{\text{dose}}$ | Uniform shift | ∼0–2 nm (field-level) |
| $\Delta\text{CD}_{\text{aberration}}(r)$ | $a_2 r^2 + a_4 r^4$ (radial) | $a_2 = 0.1$, $a_4 = 0.01$ nm⁻² |
| $\Delta\text{CD}_{\text{linear}}(x, y)$ | $b_x x + b_y y$ | $b_x$, $b_y$ = 0.01–0.05 nm/mm |
| $\Delta\text{CD}_{\text{random}}$ | $\mathcal{N}(0, \sigma_{\text{CDU}})$ | $\sigma_{\text{CDU}} = 0.5$–1.0 nm |

**Engineering Decision:** Across-die CD variation is modeled as a smooth low-order spatial function plus a small random component. The magnitude is scaled so that 3σ of ΔCD across the field = 2 nm at N5.

---

## 3. Across-Wafer CD Variation

### 3.1 Sources

| Source | Pattern | Magnitude (3σ, N5) |
|---|---|---|
| **CMP thickness variation** | Radial (center-to-edge) | 3–8 nm |
| **Etch rate radial variation** | Radial (center faster) | 2–5 nm |
| **Deposition uniformity** | Radial | 2–5% of thickness |
| **Thermal budget variation** | Edge vs. center | 1–3 nm |

### 3.2 Wafer-Level CD Model

$$\Delta\text{CD}_{\text{wafer}}(r) = A \cdot \left(\frac{r}{R}\right)^2 + \text{micro-loading}(\text{density}) + \mathcal{N}(0, \sigma_{\text{wafer}})$$

| Term | Model | Typical Value |
|---|---|---|
| Radial parabolic | $A \cdot (r/R)^2$ | A = 3 nm, R = 150 mm |
| Micro-loading | $k \cdot (\text{pattern density} - 0.5)$ | k = 2–5 nm |
| Random residual | $\mathcal{N}(0, \sigma)$ | $\sigma = 1$ nm |

---

## 4. CDU Model Implementation

### 4.1 Scale-Separated CD Variation

```
CD(x, y) = CD_nominal + ΔCD_LER(y) + ΔCD_die(x, y) + ΔCD_wafer(r)

where:
  ΔCD_LER(y)     = local variation from LER (high-frequency, along edge)
  ΔCD_die(x, y)  = field-level systematic (low-order polynomial)
  ΔCD_wafer(r)   = wafer-level radial variation (very low frequency)
```

**Fact:** The three components have well-separated spatial scales: LER at 1–100 nm, die-level at 1–30 mm, wafer-level at 10–300 mm. At the CD-SEM FOV (0.5–10 μm), only the LER component is fully visible. Die-level and wafer-level variation appear as a constant offset at a single measurement location.

### 4.2 Within-FOV CD Variation

At a single CD-SEM measurement site (∼1 μm FOV):

| Component | Variation Observed | Modeling Needed? |
|---|---|---|
| LER | Yes (along-line variation) | **Essential** — Document 02 |
| Die-level systematic | Subtle (∼0.001 nm change across 1 μm) | No — <0.01% of CD |
| Wafer-level radial | None (constant offset at one site) | **No** — constant shift per image |

**Inference:** For a single SEM image (Phase A–B), the only visible CD variation is LER/LWR. Across-die and across-wafer variation becomes relevant only when generating multiple images at different die positions (Phase C–D).

### 4.3 Implementation Priority

| Component | Implementation Phase | Visibility in SEM |
|---|---|---|
| LER/LWR (along-edge) | Phase A (essential) | Directly visible |
| Die-level systematic | Phase C (optional) | Visible across array images |
| Wafer-level radial | Phase D (optional) | Visible in wafer map |

---

## 5. CD Variation Validation

| Data Source | CD Variation (3σ) | Notes |
|---|---|---|
| IRDS 2023 [M2] | 1.0–2.5 nm (N5 contact) | Target values |
| Applied Materials Yield [M6] | 1.5–3.0 nm (N7 BEOL) | Production data |
| imec N5 CDU [M10] | 1.8–2.2 nm | MEOL/contact CDU |
| Hitachi CD-SEM data [M7] | 2.0–4.0 nm (19 nm node) | Mature node reference |

---

## Sources

- [M1] Habermas et al., "LER and LWR metrology," *Proc. SPIE*, vol. 10583, 2018.
- [M2] IRDS, "Lithography and Metrology Roadmap," 2023.
- [M3] C. A. Mack, "Line edge roughness," *J. Micro/Nanolith. MEMS MOEMS*, vol. 8, 2009.
- [M6] Applied Materials, "Yield characterization of advanced nodes," Technical report, 2020.
- [M7] H. Kawada et al., "CD-SEM measurement of CDU," *Proc. SPIE*, vol. 9778, 2016.
- [M10] imec, "EUV lithography variability at N5," *Proc. SPIE*, vol. 10957, 2019.
- [M12] C. N. Archie, "CD metrology," *AIP Conf. Proc.*, vol. 788, 2005.
