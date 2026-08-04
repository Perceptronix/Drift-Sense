# Open Questions

**Research Phase:** 3.2
**Document:** 08_open_questions.md
**Date:** 2026-07-30

---

## 1. Questions Answered Within Phase 3.2

| Question | Answer | Document |
|---|---|---|
| Which manufacturing steps modify geometry? | 8 identified: deposition, lithography (coat + expose + develop), etch (anisotropic, isotropic), CMP, resist strip | 02 |
| What is the geometric transformation per process step? | Height, material, profile, and corner effects defined for each step | 03 |
| What are realistic cross-sections vs. ideal layout? | Trapezoidal profiles, tapered sidewalls, rounded corners; catalogued for 9 feature types | 04 |
| Which process effects can be simplified? | 36 effects classified: 8 essential, 5 recommended, 11 optional, 12 ignore | 05 |
| What is the canonical process model sequence? | Layer stack → Deposition → Lithography → Etch → Strip → CMP (per layer) → Output | 06 |
| What are the fixed vs. configurable parameters? | 27 parameters classified as fixed assumptions or configurable with defaults | 07 |

---

## 2. Questions for Phase 3.3 (Manufacturing Variability)

| # | Question | Nature | Impact |
|---|---|---|---|
| Q1 | **What are the statistical distributions of key process parameters at the target node?** | The distributions of sidewall angle, CD, thickness, corner radius across the wafer and wafer-to-wafer. | Determines realistic variation ranges for SEM simulation. |
| Q2 | **How is line edge roughness (LER) correlated along an edge?** | LER correlation length (ξ) and RMS amplitude for EUV lithography at the target node. | Directly affects SEM edge profile width and CD precision. |
| Q3 | **What CD uniformity (CDU) values are typical for the target node?** | CDU (3σ) per feature type across the field. | Determines how much CD variation is visible in the simulation. |
| Q4 | **What are the systematic variation patterns (pitch-dependent, position-dependent)?** | Across-field CD variation, etch micro-loading, CMP pattern-density effects. | Determines large-scale variation visible in large-FOV SEM. |
| Q5 | **What overlay and alignment budgets apply?** | Mask-to-wafer alignment variation between layers. | Affects contact-to-gate overlay, via-to-line overlay in SEM images. |
| Q6 | **Are LER, CDU, and thickness variations correlated?** | Process parameters may be correlated (e.g., higher etch rate → wider CD + thinner film). | Correlated variations change the SEM image differently from independent variations. |
| Q7 | **What edge roughness models best represent EUV resist?** | Exponential autocorrelation vs. fractal vs. power-law models. | Determines LER implementation in the geometry generator. |

---

## 3. Questions Deferred (Implementation Decisions)

| # | Question | Reason for Deferral |
|---|---|---|
| D1 | Should the geometry engine accept GDSII directly or pre-rasterized bitmaps? | Implementation decision — depends on interface with layout tools. |
| D2 | Should the process model use analytical profiles (trapezoid + circle segments) or numerical operations (level set, morphological)? | Implementation decision — analytical is simpler; numerical is more flexible. |
| D3 | How should the geometry engine handle complex OPC'd mask shapes? | OPC is assumed to be included in the GDSII; the mask is the target shape. |
| D4 | What scripting API should the geometry engine expose? | Implementation decision — Python, JSON config, GUI? |

---

## 4. Summary of Unresolved Items

| Item | Critical for Phase A? | Resolution Path | Required By |
|---|---|---|---|
| Process parameter distributions | **No** (Phase A uses nominal only) | Phase 3.3 | Phase C |
| LER model and values | **No** (Phase A uses smooth edges) | Phase 3.3 | Phase C |
| CDU distributions | **No** (Phase A uses nominal CD) | Phase 3.3 | Phase C |
| Overlay model | **No** (Phase A uses perfect alignment) | Phase 3.3 | Phase C |
| Correlated variations | **No** | Phase 3.3 | Phase D |
| GDSII import method | **Yes** | Implementation decision | Phase A |
| Analytical vs. numerical profile | **Yes** | Implementation decision | Phase A |

---

## Sources

- [F1] J. D. Plummer, *Silicon VLSI Technology*, Prentice Hall, 2000.
- [F3] C. Mack, *Fundamental Principles of Optical Lithography*, Wiley, 2007.
- [F9] imec, "Core technology scaling," 2023.
- [F16] H. J. Levinson, *Principles of Lithography*, 3rd ed. SPIE, 2010.
- [F17] C. A. Mack, "Line edge roughness," *J. Micro/Nanolith. MEMS MOEMS*, vol. 8, 2009.
