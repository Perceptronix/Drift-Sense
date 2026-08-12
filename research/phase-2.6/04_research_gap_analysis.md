# Research Gap Analysis

**Research Phase:** 2.6
**Document:** 04_research_gap_analysis.md
**Date:** 2026-07-30

---

## 1. Gap Classification

| Severity | Definition | Action Required |
|---|---|---|
| **Critical** | Missing physics that materially affects semiconductor localization accuracy | Must be addressed before or during Phase A |
| **Important** | Missing physics that affects image realism or quantitative accuracy | Should be addressed before Phase D |
| **Minor** | Missing physics that affects edge cases or advanced applications | Address if time permits |
| **Safe to ignore** | Physics with negligible impact on target application | Document and close |

---

## 2. Gap Assessment

### 2.1 G1 — Geometry Interface Not Specified

| Aspect | Detail |
|---|---|
| **Severity** | **Critical** |
| **Description** | The 2.5D height field format (file type, pixel encoding, material ID encoding, coordinate convention, units) is not specified in Phases 2.1–2.5. |
| **Impact** | Blocks all rendering. The renderer cannot be built without knowing the input format. |
| **Status** | **Addressed in Phase 2.6, Document 06** |
| **Recommendation** | Freeze the geometry interface as specified in Document 06 before coding begins. |

### 2.2 G2 — Validation Protocol Not Defined

| Aspect | Detail |
|---|---|
| **Severity** | **Critical** |
| **Description** | No metrics, reference structures, or acceptance thresholds are defined for verifying simulator output. |
| **Impact** | Cannot verify that the simulator produces correct output. Risk of undetected errors. |
| **Status** | **Addressed in Phase 2.6, Document 05** |
| **Recommendation** | Adopt the validation protocol in Document 05 before Phase B begins. |

### 2.3 G3 — SE Yield Uncertainty at 1 keV

| Aspect | Detail |
|---|---|
| **Severity** | **Important** |
| **Description** | Frozen $\delta_0$ values at 1 keV have estimated ±20–30% uncertainty. The photoresist value (2.0) has limited independent verification. |
| **Impact** | Absolute contrast levels may be off by ±30%, but relative contrast (material A vs material B) and edge peak positions are largely unaffected. |
| **Mitigation** | Validate against CASINO Monte Carlo simulations for all 6 materials at 1 keV. If MC values differ by >20%, update the material library. |
| **Recommendation** | Perform MC validation before Phase B (when material contrast ratios affect quantitative comparisons). |

### 2.4 G4 — Charging Model (Constant $f_c$) Limitations

| Aspect | Detail |
|---|---|
| **Severity** | **Important** |
| **Description** | The constant $f_c$ factor does not capture: (a) time-dependent charging, (b) beam deflection from surface potential, (c) recovery between frames, (d) charging interaction between adjacent features. |
| **Impact** | For thick insulators (resist > 500 nm) at high beam current (>50 pA), the charging artifact will differ from real SEM images. |
| **Mitigation** | The $f_c$ model is acceptable for Phase A–B. If time-dependent effects are needed (Phase C+), implement a dynamic charging model: $V_{\text{surf}}(t) = V_0(1 - \exp(-t/\tau_{\text{charge}}))$ with charge dissipation between frames. |
| **Recommendation** | Document the limitation clearly for downstream users. Implement dynamic charging if strong insulator artifacts are required for validation. |

### 2.5 G5 — No Line Edge Roughness (LER) Model

| Aspect | Detail |
|---|---|
| **Severity** | **Minor** |
| **Description** | Real semiconductor lines have edge roughness (LER) with characteristic correlation length and amplitude (typically 1–5 nm, 10–50 nm correlation length). The simulator produces perfectly straight edges. |
| **Impact** | Simulated CD-SEM images without LER will appear "too clean." For CD metrology algorithm development, the absence of LER may under-estimate edge detection variance. |
| **Mitigation** | Add LER as an optional geometry perturbation in Phase C: apply a correlated random displacement to the edge positions using an exponential autocorrelation function. |
| **Recommendation** | Implement LER as an optional feature before using the simulator for CD precision studies. |

### 2.6 G6 — No BSE Angular Dependence for Detector

| Aspect | Detail |
|---|---|
| **Severity** | **Important** |
| **Description** | The specification uses constant $\eta_{\text{coll,BSE}} = 0.5$ regardless of emission angle. Real annular BSE detectors have collection efficiency that varies with emission angle and surface normal. |
| **Impact** | BSE compositional contrast magnitude is approximate. For flat surfaces, the constant is adequate. For structured surfaces (trenches, sidewalls), the angular dependence matters. |
| **Mitigation** | For Phase A, the constant is acceptable. For Phase C, implement $\eta_{\text{coll,BSE}}(\theta) = \eta_0 \cdot (1 + \cos\theta)/2$ as a simple angular model. |
| **Recommendation** | Document that BSE contrast is approximate. Add angular model in Phase C if BSE imaging is a priority. |

### 2.7 G7 — SE-II Characteristic Length Uncertainty

| Aspect | Detail |
|---|---|
| **Severity** | **Important** |
| **Description** | The SE-II characteristic length $L_{\text{SE-II}}$ is specified as 50 nm for Si, but the actual value depends on beam energy and material with significant spread in the literature. |
| **Impact** | The SE-II halo width directly affects the edge profile tail, which affects CD bias in threshold-based edge detection. |
| **Mitigation** | Use CASINO Monte Carlo to determine $L_{\text{SE-II}}$ for each material at 1 keV before Phase B. |
| **Recommendation** | Validate SE-II parameters with MC before Phase B implementation. |

### 2.8 G8 — SEM Column Aberrations Merged Into Effective $d_p$

| Aspect | Detail |
|---|---|
| **Severity** | **Minor** |
| **Description** | The specification treats the effective probe diameter as a single configurable parameter, collapsing all aberration contributions into one value. |
| **Impact** | This is standard practice. No significant impact on image realism because the Gaussian PSF is the dominant effect. |
| **Mitigation** | None needed. The effective $d_p$ approach is standard. |
| **Recommendation** | No action required. |

### 2.9 G9 — No Surface Roughness Model

| Aspect | Detail |
|---|---|
| **Severity** | **Safe to ignore** |
| **Description** | Semiconductor surfaces in CD-SEM are smooth (RMS < 1 nm). Surface roughness modifies SE yield locally but at a scale below CD-SEM resolution. |
| **Impact** | Negligible for CD metrology. |
| **Recommendation** | No action required. |

### 2.10 G10 — No Scan Distortion Model

| Aspect | Detail |
|---|---|
| **Severity** | **Minor** |
| **Description** | Scan distortion (pin-cushion, barrel, S-curve) is deferred to Phase C as "optional." |
| **Impact** | For small FOV (<1 μm), scan distortion is <0.1% in modern CD-SEM, corresponding to <1 nm error. Negligible. |
| **Mitigation** | Add 2D polynomial distortion model if large-FOV simulation is needed. |
| **Recommendation** | Keep as deferred. Not needed for standard CD-SEM simulation. |

### 2.11 G11 — No Frame-to-Frame Consistency (Frame Averaging)

| Aspect | Detail |
|---|---|
| **Severity** | **Minor** |
| **Description** | Frame averaging is listed as a configurable parameter, but no model specifies how multiple frames are generated (independent noise realizations? correlated noise? drift between frames?). |
| **Impact** | If frame averaging is enabled with the current spec, frames will have independent noise at the same pixel positions — this is correct for shot noise but doesn't capture drift between frames. |
| **Mitigation** | Specify: frame averaging = average of $N$ independent noise realizations of the same signal. If drift simulation is enabled, add position offset per frame. |
| **Recommendation** | Clarify in implementation: $I_{\text{avg}} = \frac{1}{N}\sum_{k=1}^N I_{\text{noisy},k}$ where each $I_{\text{noisy},k}$ has independent Poisson noise. |

### 2.12 G12 — Resist Shrinkage Under Beam

| Aspect | Detail |
|---|---|
| **Severity** | **Safe to ignore** |
| **Description** | Electron beam exposure causes photoresist to shrink (CD change of 1–5 nm for high-dose imaging). This is a metrology concern, not an image formation concern. |
| **Impact** | Affects actual CD measurements on real wafers but not the image of a given structure. The simulator takes the structure as input and renders its image — shrinkage is pre-existing in the input geometry. |
| **Recommendation** | No action required. Document as intentional exclusion. |

---

## 3. Gap Summary

| # | Gap | Severity | Phase When Addressed | Effort to Fix |
|---|---|---|---|---|
| G1 | Geometry interface not specified | **Critical** | Pre-implementation (this document) | Low |
| G2 | Validation protocol not defined | **Critical** | Pre-implementation (this document) | Moderate |
| G3 | SE yield uncertainty at 1 keV | **Important** | Before Phase B | Low (MC simulation) |
| G4 | Charging model ($f_c$) limitations | **Important** | Phase C (dynamic model) | Moderate |
| G5 | No LER model | **Minor** | Phase C | Low |
| G6 | No BSE angular detector model | **Important** | Phase C | Low |
| G7 | SE-II length uncertainty | **Important** | Before Phase B | Low (MC simulation) |
| G8 | Aberrations in effective $d_p$ | **Minor** | Already handled | None |
| G9 | No surface roughness | **Safe to ignore** | Never | None |
| G10 | No scan distortion | **Minor** | Phase D | Low |
| G11 | Frame averaging specification gap | **Minor** | Before Phase D | Low |
| G12 | Resist shrinkage | **Safe to ignore** | Never | None |

---

## 4. Critical Gaps Resolution

### G1 Status: RESOLVED (Document 06 of this review)

The geometry interface specification in Document 06 defines:
- 2.5D height map format
- Material ID encoding
- Coordinate convention
- Units
- Metadata requirements

### G2 Status: RESOLVED (Document 05 of this review)

The validation protocol in Document 05 defines:
- Reference structures
- Ground truth generation
- Metrics and thresholds
- Qualitative and quantitative evaluation

**No remaining critical gaps.**

---

## 5. Important Gaps Resolution Plan

| Gap | Resolution Action | Responsible | Timeline |
|---|---|---|---|
| G3 | CASINO MC simulation for all 6 materials at 1 keV | Physics team | Before Phase B |
| G4 | Document limitation; implement dynamic charging model | Implementation team | Phase C |
| G6 | Add angular-dependent BSE collection | Implementation team | Phase C |
| G7 | CASINO MC for SE-II parameters | Physics team | Before Phase B |

---

## Sources

- [B1] L. Reimer, *Scanning Electron Microscopy*, 2nd ed. Springer, 1998.
- [B4] D. C. Joy, *Monte Carlo Modeling*, Oxford University Press, 1995.
- [J1] J. S. Villarrubia et al., *J. Res. NIST*, vol. 109, 2004.
- [J9] D. Drouin et al., "CASINO V2.42," *Scanning*, vol. 29, 2007.
