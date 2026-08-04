# Engineering Classification

**Research Phase:** 3.3
**Document:** 07_engineering_classification.md
**Date:** 2026-07-30

---

## 1. Classification Summary

Every variability mechanism is classified into one of four categories:

| Category | Definition | Count | Implementation Priority |
|---|---|---|---|
| **Essential** | Must model — materially affects SEM appearance | 2 | Phase A |
| **Recommended** | Should model — improves SEM realism | 4 | Phase C |
| **Optional** | Model as needed — visible in specific scenarios | 3 | Phase D |
| **Ignore** | Not modeled — negligible effect at CD-SEM resolution | 2 | Never |

---

## 2. Classification Table

| Variability Source | Classification | Justification | SEM Visibility |
|---|---|---|---|
| **Line edge roughness (LER)** | **Essential** | Directly determines edge sharpness and CD measurement noise | High |
| **Line width roughness (LWR)** | **Essential** | Derived from LER; directly affects CD precision | High |
| Sidewall angle variation | **Recommended** | Changes edge profile width subtly | Moderate |
| Corner rounding variation | **Recommended** | Changes edge intensity peak shape | Moderate |
| CMP dishing (wide features) | **Recommended** | Visible on wide lines >200 nm | Moderate |
| Overlay translation | **Recommended** | Layer-to-layer shift >2 nm visible | Moderate |
| CDU (field-level) | **Optional** | Constant across single image; matters for array | Low |
| Film thickness variation | **Optional** | Small (<5%) effect on SEM intensity | Low |
| CMP erosion (dense arrays) | **Optional** | Subtle height variation across array | Low |
| Overlay rotation | **Optional** | <0.001 nm across typical FOV | Negligible |
| CDU (wafer-level radial) | **Optional** | Constant offset at single image FOV | Negligible |
| Scanner distortion | **Ignore** | <0.01 nm at 1 μm FOV | Negligible |
| Wafer warpage | **Ignore** | <0.01 nm at 1 μm FOV | Negligible |

---

## 3. Essential Variability: Detailed Justification

### 3.1 Line Edge Roughness

| Why Essential | Evidence |
|---|---|
| All real semiconductor lines have LER | Published CD-SEM data from multiple nodes [M1][M3][M4] |
| LER directly broadens the SEM edge profile | ∼σ_LER additional blur on observed edge [M3] |
| LER sets the fundamental limit on CD precision | ITRS identifies LER as a critical metrology challenge [M2] |
| Without LER, edges are unphysically sharp | Unrealistic edges → unrealistic CD algorithm behavior |

**Effect of not modeling LER:**
- Edge profiles appear too sharp (error > 50% in edge width)
- CD measurement precision is under-estimated
- The simulator produces visibly unrealistic images

### 3.2 Line Width Roughness

| Why Essential | Evidence |
|---|---|
| LWR is the direct observable in CD-SEM (width variation along a line) | [M1][M4] |
| LWR = LER_left + LER_right — requires both edges to be rough | Statistical derivation |
| CD measurement uncertainty scales with LWR | [M3] |

**Effect of not modeling LWR:**
- Lines have constant width along their length — unrealistic
- CD measurement shows zero variance along line — unrealistic

---

## 4. Recommended Variability: Justification

| Source | Why Not Essential | Why Still Recommended |
|---|---|---|
| **Sidewall angle variation** | SEM edge profile dominated by mean sidewall angle (Phase 3.2), not its variation | Variation of ±1–2° changes CD by ∼1–2 nm for tall features |
| **Corner rounding variation** | Mean corner radius (Phase 3.2) dominates the SEM edge peak shape | Variation of ±2 nm changes peak shape subtly |
| **CMP dishing** | Only visible on wide lines (>200 nm); not present on standard CD-SEM targets | BEOL reliability applications require it |
| **Overlay translation** | Not relevant for single-layer structures | Essential for multi-layer images (FOV > 2 μm) |

---

## 5. Optional Variability: Justification

| Source | When to Model |
|---|---|
| **CDU (field-level)** | When generating multiple images across a die for statistical studies |
| **Film thickness variation** | When studying sensitivity of SEM to process variation |
| **CMP erosion** | For large-FOV images (>5 μm) of dense arrays |
| **Overlay rotation** | Only for die-scale overlay studies (>100 μm FOV) |

---

## 6. Ignored Variability: Justification

| Source | Reason |
|---|---|
| **Scanner distortion** | <0.01 nm at CD-SEM FOV (1 μm) — pixel-level analysis impossible |
| **Wafer warpage** | Same — negligible at typical FOV |
| **Chamber-to-chamber matching** | Affects large-scale process parameters, not within-image geometry |
| **Dose variation across slit** | Already captured in field-level CDU as radial systematic |

---

## 7. Frozen Parameters

### 7.1 Essential (Must Be Configurable)

| Parameter | Symbol | Default | Range | Model |
|---|---|---|---|---|
| LER 3σ | $\sigma_{\text{LER}}$ | 2.4 nm | 1.0–5.0 nm | Gaussian random process |
| LER correlation length | $\xi$ | 25 nm | 10–50 nm | Exponential ACF |
| LER roughness exponent | $\alpha$ | 0.5 | 0.3–0.7 | PSD shape parameter |
| LER left–right correlation | $\rho$ | 0.3 | 0.0–0.7 | Cross-correlation coefficient |
| LWR (derived) | $\sigma_{\text{LWR}}$ | 3.4 nm | 1.4–7.1 nm | $\sqrt{2(1-\rho)} \cdot \sigma_{\text{LER}}$ |

### 7.2 Recommended (Should Be Configurable)

| Parameter | Symbol | Default | Range | Model |
|---|---|---|---|---|
| Sidewall angle σ | $\sigma_\theta$ | 1.0° | 0.5–2.0° | Truncated Gaussian |
| Corner radius σ | $\sigma_R$ | 1.0 nm | 0.5–2.0 nm | Gaussian |
| CMP dishing depth | $d_0$ | 15 nm | 5–50 nm | Parabolic |
| Overlay translation | $\sigma_{\text{ovl}}$ | 4.0 nm | 2.0–8.0 nm | Gaussian |

### 7.3 Fixed Assumptions

| Assumption | Value | Rationale |
|---|---|---|
| LER autocorrelation | Exponential | Matches published data [M1][M3] |
| CDU distribution | Gaussian | Central limit theorem |
| Overlay distribution | Gaussian | Standard semiconductor model |
| Random variables independent | Unless ρ specified | Simplest assumption |

---

## Sources

- [M1] Habermas et al., "LER and LWR metrology," *Proc. SPIE*, vol. 10583, 2018.
- [M2] IRDS, "Lithography and Metrology Roadmap," 2023.
- [M3] C. A. Mack, "Line edge roughness," *J. Micro/Nanolith. MEMS MOEMS*, vol. 8, 2009.
- [M4] B. D. Bunday et al., "CD-SEM metrology," *Proc. SPIE*, vol. 5038, 2003.
- [M11] Lorusso et al., "LER transfer in EUV lithography," *Proc. SPIE*, vol. 9776, 2016.
- [M12] C. N. Archie, "CD metrology," *AIP Conf. Proc.*, vol. 788, 2005.
