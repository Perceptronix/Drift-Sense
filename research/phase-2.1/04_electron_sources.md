# Electron Sources

**Research Phase:** 2.1
**Document:** 04_electron_sources.md
**Date:** 2026-07-30

---

## 1. Introduction

The electron source (electron gun) is the starting point of all SEM imaging. It must provide a stable, intense, and well-collimated beam of electrons that can be focused to a nanometer-scale probe. The choice of electron source is the single most important determinant of ultimate microscope performance.

Three fundamental source technologies exist, distinguished by their electron emission mechanism:
1. **Thermionic emission** (tungsten filament, LaB₆/CeB₆ crystals)
2. **Schottky field emission** (field-assisted thermionic emission)
3. **Cold field emission** (pure field emission / Fowler-Nordheim tunneling)

---

## 2. Thermionic Electron Guns

### 2.1 Working Principle

In thermionic emission, electrons gain sufficient thermal energy to overcome the work function barrier of the emitter material. The emitted current density is described by the **Richardson-Dushman equation**:

$$J = A T^2 \exp\left(-\frac{\Phi}{k_B T}\right)$$

where:
- $J$ = current density (A/m²)
- $A$ = Richardson constant (≈ 120 A/cm²·K² for most metals)
- $T$ = temperature (K)
- $\Phi$ = work function (eV)
- $k_B$ = Boltzmann constant

The emitter is heated resistively (tungsten) or indirectly (LaB₆) to temperatures where a substantial fraction of electrons have energy exceeding the work function.

### 2.2 Tungsten Filament

| Parameter | Value |
|---|---|
| Work function | ~4.5 eV |
| Operating temperature | ~2,700–2,800 K |
| Brightness | ~10⁴–10⁵ A/cm²·sr |
| Source size | ~50 μm diameter |
| Energy spread | ~2–3 eV |
| Vacuum required | ~10⁻⁵ torr |
| Lifetime | ~100 hours |
| Cost | Very low |
| Resolution (30 kV) | ~3–5 nm |

**Advantages:**
- Lowest cost of any electron source.
- Simple construction — a bent tungsten wire.
- Tolerant of lower vacuum (10⁻⁵ torr).
- Easy to replace.

**Disadvantages:**
- Large source size (~50 μm) limits minimum probe diameter.
- Low brightness compared to FEG sources.
- Short lifetime (~100 hours) due to thermal evaporation of tungsten.
- Thermal drift during warm-up.
- Frequent beam current adjustments needed as filament ages.

### 2.3 Lanthanum Hexaboride (LaB₆) Filament

| Parameter | Value |
|---|---|
| Work function | ~2.7 eV |
| Operating temperature | ~1,800–2,000 K |
| Brightness | ~10⁵–10⁶ A/cm²·sr |
| Source size | ~10 μm diameter |
| Energy spread | ~1–2 eV |
| Vacuum required | ~10⁻⁷ torr |
| Lifetime | ~500–1,000 hours |
| Cost | Moderate |
| Resolution (30 kV) | ~2–3 nm |

**Advantages:**
- Ten times the brightness of tungsten at any accelerating voltage.
- 5–10× longer lifetime than tungsten.
- Lower operating temperature reduces thermal drift.
- Sharper tip enables smaller source size.

**Disadvantages:**
- Requires better vacuum than tungsten (10⁻⁷ torr).
- More expensive than tungsten.
- Brittle material — sensitive to mechanical shock.
- Requires careful alignment.

**Cerium Hexaboride (CeB₆):** A variant offering better oxidation resistance and more stable emission than LaB₆. Increasingly preferred over LaB₆ in modern thermionic SEMs.

### 2.4 When Thermionic Sources Are Used
Thermionic guns are found in:
- Cost-sensitive SEMs for education and routine imaging.
- Instruments where FEG performance is not needed (magnifications below 50,000×).
- Older-generation CD-SEMs (before ~2000).

**Fact:** No major semiconductor CD-SEM manufactured after ~2005 uses a thermionic source. FEG sources have completely displaced thermionic emitters in semiconductor inspection.

---

## 3. Schottky Field Emission Gun (Schottky FEG)

### 3.1 Working Principle

Schottky emission combines thermionic and field emission mechanisms. The emitter is heated (≈1,800 K) while a strong electric field (≈10⁸ V/m) at the tip lowers the effective work function through the **Schottky effect**:

$$\Phi_{\text{eff}} = \Phi_0 - e \sqrt{\frac{eE}{4\pi \epsilon_0}}$$

where $E$ is the electric field at the emitter surface. The barrier lowering reduces the required temperature compared to pure thermionic emission, while the field stabilizes the emission site.

### 3.2 Construction

- **Emitter:** Single-crystal tungsten wire oriented along the <100> axis, sharpened to a tip radius of approximately 0.5–1 μm.
- **Coating:** Zirconium oxide (ZrO₂) is applied to the tip. ZrO₂ diffuses to the tip surface, reducing the work function from ~4.5 eV (clean W) to approximately ~2.7 eV.
- **Suppressor electrode:** A negatively biased electrode surrounds the emitter shaft, preventing unwanted electron emission from the shank.
- **Extractor electrode:** A positively biased electrode (typically 2–7 kV relative to the tip) generates the extraction field.

### 3.3 Performance

| Parameter | Value |
|---|---|
| Work function (ZrO₂/W) | ~2.7 eV |
| Operating temperature | ~1,800 K |
| Brightness | ~10⁷–10⁸ A/cm²·sr |
| Source size | ~15–30 nm |
| Energy spread | ~0.3–1.0 eV |
| Vacuum required | ≤10⁻⁹ torr |
| Lifetime | >10,000 hours |
| Cost | High |
| Resolution (30 kV) | ~1.0–1.5 nm |
| Current stability | <0.5% / hour |

### 3.4 Advantages

1. **High brightness:** ~100× brighter than LaB₆, enabling smaller probe diameters at usable currents.
2. **Excellent stability:** Emission current drift <0.5%/hour after warm-up. This is critical for quantitative metrology.
3. **Long lifetime:** >10,000 hours of operation. Typical replacement interval is 2–3 years.
4. **Low energy spread:** ~0.3–1.0 eV reduces chromatic aberration, enabling higher resolution at low kV.
5. **Moderate vacuum:** Operates at 10⁻⁹ torr, achievable with standard ion pumps.
6. **Rapid startup:** Ready for imaging within minutes of power-on.
7. **Robust:** Resistant to vacuum accidents and tip contamination.

### 3.5 Disadvantages

1. **Cost:** Significantly more expensive than thermionic sources.
2. **Vacuum requirement:** Requires 10⁻⁹ torr, adding pumping system cost.
3. **Heating:** The thermal power dissipated in the gun chamber must be managed.

---

## 4. Cold Field Emission Gun (Cold FEG)

### 4.1 Working Principle

Cold field emission relies on **Fowler-Nordheim (FN) tunneling**. A very strong electric field (≈10⁹ V/m) at the emitter tip narrows the potential barrier sufficiently that electrons tunnel directly from the Fermi level into vacuum, with no thermal assistance:

$$J = \frac{a F^2}{\Phi} \exp\left(-\frac{b \Phi^{3/2}}{F}\right)$$

where $F$ is the local electric field, $\Phi$ is the work function, and $a$ and $b$ are constants.

### 4.2 Construction

- **Emitter:** Single-crystal tungsten wire oriented along the <310> or <111> axis, electrochemically etched to a tip radius of approximately 30–100 nm.
- **No coating:** The emission is from clean tungsten.
- **Heating:** No heating is applied during operation (hence "cold"). The emitter operates at room temperature.
- **Flash cleaning:** The tip is periodically heated (flashed) to remove adsorbed gas molecules that degrade emission.
- **Extractor:** A positively biased electrode extracts electrons.

### 4.3 Performance

| Parameter | Value |
|---|---|
| Work function (clean W) | ~4.5 eV |
| Operating temperature | Room temperature (~300 K) |
| Brightness | ~10⁸–10⁹ A/cm²·sr |
| Source size | ~3–5 nm |
| Energy spread | ~0.2–0.5 eV |
| Vacuum required | ≤10⁻¹⁰ torr |
| Lifetime | >10,000 hours |
| Cost | Very high |
| Resolution (30 kV) | ~0.5–1.0 nm |
| Current stability | Requires periodic flashing |

### 4.4 Advantages

1. **Highest brightness:** The brightest available source, 10× brighter than Schottky.
2. **Smallest source size:** ~3–5 nm virtual source, enabling the smallest probe diameters.
3. **Lowest energy spread:** ~0.2–0.5 eV minimizes chromatic aberration.
4. **Highest resolution:** Best possible SEM resolution (sub-0.5 nm achievable at 30 kV).
5. **No thermal drift:** Room temperature operation eliminates thermal drift.

### 4.5 Disadvantages

1. **Emission instability:** The emission current fluctuates due to adsorption/desorption of residual gas molecules on the tip. This is the most significant drawback.
2. **Flashing requirement:** The tip must be heated (flashed) every 4–12 hours to restore stable emission. This interrupts measurement sequences.
3. **Extreme vacuum:** Requires 10⁻¹⁰ torr or better, requiring additional pumping.
4. **Sensitivity:** Extremely sensitive to vacuum quality and contamination.
5. **Slow startup:** Takes 1–4 hours to achieve stable emission after flashing.
6. **Cost:** Highest cost among all source types.

---

## 5. Comprehensive Comparison

### 5.1 Performance Comparison Table

| Parameter | Tungsten | LaB₆ | Schottky FEG | Cold FEG |
|---|---|---|---|---|
| **Emission mechanism** | Thermionic | Thermionic | Field-assisted thermionic | Field emission (FN) |
| **Work function (eV)** | 4.5 | 2.7 | 2.7 (ZrO₂/W) | 4.5 |
| **Temperature (K)** | 2,800 | 1,900 | 1,800 | 300 |
| **Brightness (A/cm²·sr)** | 10⁴–10⁵ | 10⁵–10⁶ | 10⁷–10⁸ | 10⁸–10⁹ |
| **Virtual source size (nm)** | 50,000 | 10,000 | 15–30 | 3–5 |
| **Energy spread (eV)** | 2–3 | 1–2 | 0.3–1.0 | 0.2–0.5 |
| **Total emission current (μA)** | ~100 | ~100 | ~100–200 | ~5–20 |
| **Angular current density (μA/sr)** | ~1 | ~10 | ~100–1,000 | ~100–1,000 |
| **Vacuum required (torr)** | ≤10⁻⁵ | ≤10⁻⁷ | ≤10⁻⁹ | ≤10⁻¹⁰ |
| **Lifetime (hours)** | ~100 | ~500–1,000 | >10,000 | >10,000 |
| **Current stability** | Moderate | Good | Excellent | Fair (needs flashing) |
| **Warm-up time** | Minutes | Minutes | Minutes | Hours |
| **Relative cost** | 1× | 3–5× | 10–20× | 15–30× |
| **SEM resolution at 30 kV** | 3–5 nm | 2–3 nm | 1.0–1.5 nm | 0.5–1.0 nm |

### 5.2 Brightness Interpretation

Brightness ($\beta$) is the most fundamental figure of merit for an electron source because it determines the maximum current that can be focused into a given probe size:

$$I_p = \beta \, (\pi \alpha^2) \, (\pi r_p^2)$$

where $I_p$ is probe current, $\alpha$ is convergence half-angle, and $r_p$ is probe radius.

**Inference:** A Schottky FEG provides 100–1,000× the brightness of tungsten. This means for a given probe diameter, the Schottky source delivers 100–1,000× more current, resulting in proportionally higher signal-to-noise ratio.

---

## 6. Source Selection for Semiconductor Metrology

### 6.1 Dominant Choice: Schottky FEG

**Recommendation:** For semiconductor CD-SEM and defect review, the Schottky FEG is the preferred electron source.

**Rationale:**

1. **Stability:** Schottky FEG emission current drift is typically below 0.5%/hour after a 30-minute warm-up. This stability is essential for quantitative CD metrology, where measurement precision below 0.2 nm (3σ) is required. Cold FEG cannot meet this stability requirement without frequent flashing interruptions.

2. **Brightness:** At 10⁷–10⁸ A/cm²·sr, Schottky provides sufficient current in a sub-2 nm probe for high-resolution imaging. The additional brightness of cold FEG is not needed for semiconductor node geometries (currently 3–10 nm features require ~1–2 nm probes).

3. **Operational simplicity:** Schottky FEG is ready to image within minutes of power-on and requires no periodic tip maintenance. Cold FEG flashing interrupts production workflows.

4. **Vacuum compatibility:** At 10⁻⁹ torr, Schottky vacuum requirements are achievable with standard pumping. Cold FEG at 10⁻¹⁰ torr requires additional system complexity.

5. **Proven track record:** Major CD-SEM manufacturers (Applied Materials, Hitachi, JEOL) use Schottky FEG sources in their semiconductor inspection products.

### 6.2 When Cold FEG Wins

Cold FEG is preferred in:
- Ultra-high-resolution research SEMs (for imaging below 0.5 nm).
- Applications where energy spread must be minimized (e.g., high-resolution EELS).
- Dedicated STEM instruments.

### 6.3 When Thermionic Sources Are Sufficient

Thermionic sources (LaB₆) are adequate for:
- Routine imaging below 50,000× magnification.
- Cost-sensitive environments.
- Applications where sub-2 nm resolution is not required.

---

## 7. Summary

| Recommendation | Source | Context |
|---|---|---|
| **Primary** | Schottky FEG | All semiconductor CD-SEM and defect review |
| **Alternative** | Cold FEG | Ultra-high-resolution SEM research |
| **Legacy** | LaB₆ | Older instruments, low-magnification applications |
| **Obsolete** | Tungsten | No longer competitive for semiconductor inspection |

---

## Sources

- L. Reimer, *Scanning Electron Microscopy: Physics of Image Formation and Microanalysis*, 2nd ed. Springer, 1998.
- J. I. Goldstein, D. E. Newbury, J. R. Michael, et al., *Scanning Electron Microscopy and X-Ray Microanalysis*, 4th ed. Springer, 2017.
- R. F. Egerton, *Physical Principles of Electron Microscopy*, 2nd ed. Springer, 2016.
- P. W. Hawkes and J. C. H. Spence, *Springer Handbook of Microscopy*, Springer, 2019.
- Y. Zhu (Ed.), *Modern Techniques for Characterizing Magnetic Materials*, Springer, 2005.
- Wikipedia, "Field Emission Gun," accessed July 2026.
- Wikipedia, "Field Electron Emission," accessed July 2026.
- Wikipedia, "Scanning Electron Microscope," accessed July 2026.
- Nanoscience Instruments, "Scanning Electron Microscopy," technical resource.
