# Risk Assessment

**Research Phase:** 2.6
**Document:** 07_risk_assessment.md
**Date:** 2026-07-30

---

## 1. Risk Methodology

Each risk is evaluated using:

| Factor | Scale | Definition |
|---|---|---|
| **Probability** | Low / Moderate / High | Likelihood of the risk materializing |
| **Impact** | Low / Moderate / High / Critical | Severity if the risk materializes |
| **Overall** | Low / Medium / High / Critical | Combination of probability and impact |

**Risk = Probability × Impact**

---

## 2. Identified Risks

### R1 — Model Error from Simplified Charging

| Aspect | Detail |
|---|---|
| **Category** | Physics fidelity |
| **Description** | The constant $f_c$ charging model does not capture time-dependent charging, beam deflection, or charging interactions between adjacent features. For thick insulators at high beam current, the simulated image may differ noticeably from real SEM images. |
| **Probability** | **Moderate** — depends on target structures |
| **Impact** | **Moderate** — affects absolute brightness of insulators but not edge positions (which are the primary interest for CD metrology) |
| **Overall** | **Medium** |
| **Mitigation** | 1. Document limitation for downstream users. 2. Apply $f_c$ only when insulator structures are present. 3. If dynamic effects are needed, implement a time-dependent charging model in Phase C: $\delta_{\text{eff}}(t) = \delta_0[1 - f_c(1 - \exp(-t/\tau))]$. |
| **Fallback** | Disable charging entirely if the simplified model introduces visible artifacts. |

### R2 — SE Yield Parameter Uncertainty

| Aspect | Detail |
|---|---|
| **Category** | Physics parameter accuracy |
| **Description** | Frozen $\delta_0$ values at 1 keV have ±20–30% uncertainty in the literature. The photoresist value (2.0) has limited independent verification. |
| **Probability** | **High** — uncertainty is known and quantified |
| **Impact** | **Low** — relative contrast (material A vs B) is what matters for CD metrology, not absolute values. Edge positions are unaffected by yield magnitude. |
| **Overall** | **Low** |
| **Mitigation** | 1. Validate against CASINO Monte Carlo before Phase B. 2. If MC indicates >20% deviation, adjust the material library. |
| **Fallback** | Tune $\delta_0$ as a single adjustable parameter to match a reference image. |

### R3 — Geometry Format Mismatch

| Aspect | Detail |
|---|---|
| **Category** | Interface specification |
| **Description** | If the geometry generation team produces files in a format different from what the renderer expects (different coordinate convention, different unit scaling, different material encoding), the renderer will produce incorrect output or fail. |
| **Probability** | **Low** — the interface is now frozen in Document 06 |
| **Impact** | **High** — blocks integration between geometry generator and renderer |
| **Overall** | **Medium** (becomes Low once interface is adopted by both teams) |
| **Mitigation** | 1. Freeze interface before coding (done — Document 06). 2. Write a schema validator that rejects non-compliant geometry files. 3. Create sample geometry files for testing. |
| **Fallback** | Implement a format converter as a compatibility layer. |

### R4 — Missing LER for Localization Accuracy

| Aspect | Detail |
|---|---|
| **Category** | CD metrology relevance |
| **Description** | Without line edge roughness (LER), simulated edges are perfectly straight. When used for CD metrology algorithm development, this may under-estimate edge detection variance. |
| **Probability** | **Moderate** — depends on the precision requirements of downstream CD algorithms |
| **Impact** | **Low–Moderate** — the mean CD is correct; only the precision (variance) may be underestimated. |
| **Overall** | **Low** |
| **Mitigation** | 1. Add LER as an optional geometry perturbation in Phase C. 2. Use a correlated random displacement model: $\Delta x(y) = \text{RMS}_{\text{LER}} \cdot \exp(-y / L_{\text{LER}})$. |
| **Fallback** | CD algorithm developers can add their own LER as a post-processing step. |

### R5 — SE-II Parameter Uncertainty

| Aspect | Detail |
|---|---|
| **Category** | Physics parameter accuracy |
| **Description** | The SE-II characteristic length $L_{\text{SE-II}}$ and efficiency $k_{\text{SE-II}}$ have limited published values at 1 keV. These directly affect the edge profile tail. |
| **Probability** | **Moderate** |
| **Impact** | **Moderate** — affects CD bias in threshold-based edge detection (typically < 0.5 nm bias error for ±50% uncertainty in $L_{\text{SE-II}}$) |
| **Overall** | **Medium** |
| **Mitigation** | 1. Determine $L_{\text{SE-II}}$ from CASINO MC before Phase B. 2. Perform sensitivity analysis: vary $L_{\text{SE-II}}$ by ±50% and measure the change in CD bias. |
| **Fallback** | Set $k_{\text{SE-II}} = 0$ (disable SE-II) if parameters cannot be validated. The edge profile will be sharper but the edge position is unaffected. |

### R6 — Computational Performance

| Aspect | Detail |
|---|---|
| **Category** | Implementation feasibility |
| **Description** | Per-pixel computations are O(M×N) with M=N=1024 → ~10⁶ pixels. Gaussian convolution is O(K²×M×N) where K is the kernel size. With K=15 (3σ for σ=5), this is ~2.5×10⁸ operations per convolution. Poisson random number generation for 10⁶ pixels requires ~10⁷ operations. |
| **Probability** | **Low** — the specified computation is well within the capability of modern CPUs/GPUs |
| **Impact** | **Moderate** — if unoptimized, render times could be seconds per image, which is acceptable for the target application |
| **Overall** | **Low** |
| **Mitigation** | 1. Use separable Gaussian convolution (O(K×M×N) instead of O(K²×M×N)). 2. Use optimized Poisson RNG. |
| **Fallback** | Reduce image resolution during development; use full resolution for final renders. |

### R7 — MC Validation Not Available

| Aspect | Detail |
|---|---|
| **Category** | Validation dependency |
| **Description** | The validation strategy relies on CASINO Monte Carlo simulations for ground truth. If CASINO is not available, cannot be installed, or produces results inconsistent with the literature, validation is blocked. |
| **Probability** | **Low–Moderate** — CASINO is open-source and available |
| **Impact** | **Moderate** — without MC validation, parameter uncertainty (R2, R5) cannot be resolved |
| **Overall** | **Medium** |
| **Mitigation** | 1. Install CASINO V2.42 or later. 2. If CASINO is unavailable, use published experimental yield values as fallback. 3. Sensitivity analysis without MC: vary parameters within their uncertainty ranges and evaluate impact on CD. |
| **Fallback** | Use published yield data from Seiler [J7] and Reimer [B1] without MC correction. Accept ±30% uncertainty in absolute yield. |

### R8 — Project Scope Creep

| Aspect | Detail |
|---|---|
| **Category** | Project management |
| **Description** | The specification defines 4 phases with increasing realism. There is a risk that stakeholders request additional features (voltage contrast, true 3D, line roughness, dynamic charging, etc.) before Phase A is complete. |
| **Probability** | **Moderate** — common in research-to-engineering transitions |
| **Impact** | **Moderate** — delays completion of the core renderer |
| **Overall** | **Medium** |
| **Mitigation** | 1. Freeze Phase A scope explicitly. 2. Document all "nice-to-have" features for Phase C/D. 3. Deliver Phase A working renderer before accepting new feature requests. |
| **Fallback** | Implement new features in parallel branches; merge only after Phase A acceptance. |

---

## 3. Risk Register Summary

| ID | Risk | Probability | Impact | Overall | Priority |
|---|---|---|---|---|---|
| R1 | Charging model fidelity | Mod | Mod | **Medium** | 3 |
| R2 | SE yield uncertainty | High | Low | **Low** | 5 |
| R3 | Geometry format mismatch | Low | High | **Medium** | 2 |
| R4 | Missing LER | Mod | Low–Mod | **Low** | 6 |
| R5 | SE-II parameter uncertainty | Mod | Mod | **Medium** | 4 |
| R6 | Computational performance | Low | Mod | **Low** | 7 |
| R7 | MC validation unavailable | Low–Mod | Mod | **Medium** | 4 |
| R8 | Scope creep | Mod | Mod | **Medium** | 1 |

---

## 4. Risk Mitigation Timeline

| Phase | Risks to Address | Actions |
|---|---|---|
| **Pre-Phase A** | R3 (geometry format) | Freeze interface; create validator; create sample files |
| **Phase A** | R5 (SE-II), R6 (performance) | Validate SE-II with MC; optimize convolution |
| **Before Phase B** | R2 (yield), R5 (SE-II) | CASINO MC for all materials |
| **Phase B** | R1 (charging), R4 (LER) | Charging sensitivity study; LER model |
| **Ongoing** | R7 (MC), R8 (scope) | Install CASINO; manage scope |

---

## Sources

- [B1] L. Reimer, *Scanning Electron Microscopy*, 2nd ed. Springer, 1998.
- [J7] H. Seiler, "Secondary electron emission in the scanning electron microscope," *J. Appl. Phys.*, vol. 54, 1983.
- [J9] D. Drouin et al., "CASINO V2.42," *Scanning*, vol. 29, 2007.
