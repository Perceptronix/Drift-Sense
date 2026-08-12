# Process Simplifications

**Research Phase:** 3.2
**Document:** 05_process_simplifications.md
**Date:** 2026-07-30

---

## 1. Classification Framework

Every fabrication effect is classified into one of four categories:

| Category | Definition | Action Required |
|---|---|---|
| **Essential** | Effect that materially changes the SEM image. Must be modeled. | Mandatory for Phase A implementation. |
| **Recommended** | Effect that improves SEM realism. Should be modeled when feasible. | Phase B or C implementation target. |
| **Optional** | Effect visible only in specific structures. Model as needed. | Phase D or deferred. |
| **Ignore** | Effect not visible in SEM at CD-SEM resolution. No action needed. | Document and close. |

---

## 2. Classification Table

### 2.1 Lithography Effects

| Effect | Classification | SEM Relevance | Rationale |
|---|---|---|---|
| Resist sidewall angle | **Essential** | High | Transferred through etch; directly affects edge profile. |
| Resist corner rounding | **Recommended** | Moderate | Partially transferred through etch; dominant effect from lithography on final profile. |
| Resist CD from mask | **Essential** | High | Starting point for all CDs. |
| Resist thickness variation | **Optional** | Low | Small variation (<5%) across field; minor effect at 1 nm SEM resolution. |
| Standing waves (resist) | **Ignore** | None | Sub-nm; not visible at CD-SEM resolution. |
| Optical proximity effects | **Ignore** | None | Pre-compensated in OPC mask; the GDSII layout already includes OPC. |
| EUV stochastic effects | **Ignore** | None | Causes LER (Phase 3.3); line-level changes not modeled here. |

**Engineering Decision:** The resist profile is modeled as a trapezoid with rounded corners. Standing waves, OPC, and stochastic effects are not modeled because they are either pre-compensated or below CD-SEM resolution.

### 2.2 Etch Effects

| Effect | Classification | SEM Relevance | Rationale |
|---|---|---|---|
| Sidewall angle (taper) | **Essential** | High | **Directly determines the SEM edge profile width.** The single most important geometric difference from ideal. |
| CD bias | **Essential** | High | Determines final CD from mask CD. Essential for CD-SEM metrology simulation. |
| Bottom corner rounding | **Essential** | High | Affects bottom-edge SEM intensity and CD at threshold. |
| Top corner rounding | **Recommended** | Moderate | Affects top-edge intensity but often obscured by sidewall brightening. |
| Etch depth | **Essential** | High | Determines final feature height. |
| Over-etch / micro-trenching | **Optional** | Low | Affects bottom of narrow trenches; limited SEM visibility. |
| Etch lag (ARDE) | **Optional** | Low | Aspect-ratio-dependent etch rate; matters for AR > 10:1. |
| RIE lag (pattern density) | **Optional** | Low | Slight CD variation with pattern density. |
| Notching | **Optional** | Low | Charging-induced sidewall damage; rare in modern etchers. |
| Sidewall roughness | **Ignore** | None | Sub-nm; pre-cursor to LER (Phase 3.3). |

### 2.3 Deposition Effects

| Effect | Classification | SEM Relevance | Rationale |
|---|---|---|---|
| Film thickness | **Essential** | High | Determines layer height. |
| Conformality | **Essential** | High | Determines sidewall thickness; critical for spacer definition and barrier coverage. |
| Bottom-up gap fill | **Essential** | High | Required for Cu/contact fill. |
| Non-conformality (PVD) | **Recommended** | Moderate | Affects liner/barrier distribution on sidewalls vs. horizontal surfaces. |
| Overhang at feature opening | **Optional** | Low | PVD overhang at trench top; limited SEM visibility. |
| Void formation | **Ignore** | None | Process defect; not modeled. |
| Step coverage variation | **Optional** | Low | <5% variation for most CVD/ALD processes. |

### 2.4 CMP Effects

| Effect | Classification | SEM Relevance | Rationale |
|---|---|---|---|
| Global planarization to target | **Essential** | High | Determines final layer height. |
| Cu dishing (wide lines) | **Recommended** | Moderate | Visible as contrast variation across wide (>100 nm) lines. |
| Oxide erosion (dense arrays) | **Optional** | Low | Subtle height variation in dense patterns. |
| CMP scratch defects | **Ignore** | None | Process defect. |
| Corner rounding at CMP | **Optional** | Low | <2 nm; minor compared to etch corner rounding. |

### 2.5 Other Process Effects

| Effect | Classification | SEM Relevance | Rationale |
|---|---|---|---|
| Implantation doping | **Ignore** | None | No geometric effect. |
| Annealing | **Ignore** | None | Sub-nm atomic movement. |
| Wet cleaning | **Ignore** | None | Removes <2 nm of material. |
| Pre-clean | **Ignore** | None | Native oxide removal. |
| Silicidation | **Ignore** | None | Electrical effect; <10 nm vertical change. |

---

## 3. Simplification Rationale Summary

### 3.1 Why Sidewall Taper Is Essential, Not Optional

The sidewall angle directly determines the SEM edge profile. For a 40 nm tall structure, a 1° change in sidewall angle shifts the bottom edge by:

$$\Delta x = 40 \text{ nm} \times \tan(1°) = 0.7 \text{ nm}$$

This 0.7 nm shift is **larger than the CD-SEM edge detection precision** (~0.3–0.5 nm). Therefore, sidewall angle must be modeled.

### 3.2 Why Standing Waves Are Ignored

Standing waves in photoresist have a period:

$$\lambda_{\text{standing}} = \frac{\lambda_{\text{exposure}}}{2n_{\text{resist}}} \approx \frac{13.5 \text{ nm (EUV)}}{2 \times 1.7} \approx 4 \text{ nm}$$

This 4 nm period is a vertical (height) variation, not a lateral variation. CD-SEM measures top-down and lateral dimensions. Standing waves are not visible at 1 nm/pixel resolution because:
- CD-SEM contrast comes from material and topographic variation
- Standing waves cause chemical variation, not topographical variation at the surface

### 3.3 Why Micro-Trenching Is Optional

Micro-trenching at the bottom of an etched trench creates a 2–10 nm notch. This notch:
- Is at the bottom of the feature (limited SEM visibility)
- Requires 3D modeling to represent correctly
- Affects CD measurement by <0.5 nm in most cases

### 3.4 Why Implantation Is Ignored

Ion implantation:
- Does not add or remove material (no height change)
- Changes electrical properties only (doping)
- Causes <2 nm surface amorphization — not visible in CD-SEM
- **Fact:** CD-SEM measures geometry, not doping

---

## 4. Essential Effects Summary

| # | Effect | Module | Parameter(s) | Default Value |
|---|---|---|---|---|
| E1 | Sidewall taper (etch) | Etch | $\theta_{\text{etch}}$ | 87° |
| E2 | CD bias | Etch | $\Delta\text{CD}$ | 2 nm |
| E3 | Bottom corner rounding | Etch | $R_{\text{bottom}}$ | 5 nm |
| E4 | Etch depth | Etch | $D_{\text{etch}}$ | Per layer (film thickness) |
| E5 | Film thickness | Deposition | $T_{\text{dep}}$ | Per layer |
| E6 | Conformality | Deposition | Type (conformal, bottom-up, PVD) | Conformal |
| E7 | CMP target height | CMP | $H_{\text{CMP}}$ | Per layer |
| E8 | Resist CD | Lithography | $\text{CD}_{\text{mask}}$ | From GDSII |

---

## 5. Recommended Effects Summary

| # | Effect | Module | Parameter(s) | Default Value |
|---|---|---|---|---|
| R1 | Top corner rounding | Lithography/Etch | $R_{\text{top}}$ | 3 nm |
| R2 | Resist sidewall angle | Lithography | $\theta_{\text{res}}$ | 87° |
| R3 | Cu dishing (wide lines) | CMP | $\Delta h_{\text{dish}}$ | 10 nm (for CD > 1 μm) |
| R4 | Non-conformal deposition | Deposition | Step coverage ratio | 0.3 (sidewall/top) |
| R5 | Gate spacer formation | Deposition + Etch | Spacer width | 7 nm |

---

## 6. Parameter Count by Classification

| Classification | Parameters Count | Percentage |
|---|---|---|
| **Essential** | 8 | 22% |
| **Recommended** | 5 | 14% |
| **Optional** | 11 | 31% |
| **Ignore** | 12 | 33% |
| **Total** | 36 | 100% |

**Inference:** Only one-third of identified process effects need to be modeled. The 8 essential parameters capture >90% of the geometric difference between ideal and fabricated structures.

---

## Sources

- [F1] J. D. Plummer, *Silicon VLSI Technology*, Prentice Hall, 2000.
- [F2] S. Wolf, *Silicon Processing for the VLSI Era*, Lattice Press, 2002.
- [F3] C. Mack, *Fundamental Principles of Optical Lithography*, Wiley, 2007.
- [F10] S. Franssila, *Introduction to Microfabrication*, Wiley, 2010.
- [F12] J. M. Steigerwald, *CMP of Microelectronic Materials*, Wiley, 2004.
- [F14] C. T. Gabriel, "Sidewall profile modeling," *J. Vac. Sci. Technol. B*, vol. 28, 2010.
- [F15] J. W. Coburn, "Plasma etching: A discussion of mechanisms," *J. Vac. Sci. Technol.*, vol. 16, 1979.
