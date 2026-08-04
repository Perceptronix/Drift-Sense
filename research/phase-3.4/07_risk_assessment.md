# Risk Assessment

**Research Phase:** 3.4
**Document:** 07_risk_assessment.md
**Date:** 2026-07-30

---

## 1. Risk Framework

| Factor | Scale | Definition |
|---|---|---|
| **Probability** | Low / Moderate / High | Likelihood of risk materializing |
| **Impact** | Low / Moderate / High / Critical | Severity if it does |
| **Overall** | Low / Medium / High / Critical | Combined assessment |

---

## 2. Identified Risks

### R1 — LER Generation Performance with Large Images

| Aspect | Detail |
|---|---|
| **Category** | Computational performance |
| **Description** | LER generation requires FIR convolution for each edge. For a dense L/S array with 100 lines, each 1024 pixels long, convolution cost = N_lines × N_pixels × M_filter. At 100 × 1024 × 125 = 12.8M operations. |
| **Probability** | **Low** — cost is small even for worst case |
| **Impact** | **Moderate** — would increase geometry generation time by factor of 2–5 |
| **Overall** | **Low** |
| **Mitigation** | Use FFT convolution for large line counts; pre-generate LER at structure level and apply to all lines |
| **Fallback** | Generate LER once per structure and tile for arrays |

### R2 — Overlay Not Visible at Small FOV

| Aspect | Detail |
|---|---|
| **Category** | Relevance to SEM simulation |
| **Description** | Overlay error is hidden if FOV < 2 × overlay magnitude. At default σ_ovl = 4 nm and 1 μm FOV, overlay is barely visible. |
| **Probability** | **High** — depends on user-selected FOV |
| **Impact** | **Low** — correct behavior (overlay should be invisible at small FOV) |
| **Overall** | **Low** |
| **Mitigation** | Document the relationship: overlay_visible ≈ σ_ovl / FOV. User should increase FOV to see overlay effects. |

### R3 — Material ID Granularity Too Coarse

| Aspect | Detail |
|---|---|
| **Category** | Interface completeness |
| **Description** | The material map stores 1 material ID per pixel. For structures with multiple stacked materials (e.g., gate: SiO₂/WF/MG/Spacer), only the top material is visible in the top-down material map. The SEM renderer uses the top material for surface properties, which is correct for SE imaging. However, if the escape depth is larger than the top layer thickness, the renderer may need sub-surface material information. |
| **Probability** | **Moderate** — depends on feature type |
| **Impact** | **Moderate** — affects accuracy for thin films on high-Z materials |
| **Overall** | **Medium** |
| **Mitigation** | Single top-surface material is the correct behavior for SE imaging. BSE imaging (which samples deeper) may need extension. Document as a limitation. |
| **Fallback** | Add secondary material map for buried interfaces if BSE simulation requires it. |

### R4 — 2.5D Height Field Cannot Represent Re-entrant Profiles

| Aspect | Detail |
|---|---|
| **Category** | Geometric limitation |
| **Description** | Some fabrication effects (undercut etch, isotropic etch under mask) create re-entrant profiles where Z is not single-valued at a given (X,Y). The 2.5D height field cannot represent this. |
| **Probability** | **Low** — undercut is rare in CD-SEM targets |
| **Impact** | **Moderate** — cannot simulate specific undercut scenarios |
| **Overall** | **Low–Medium** |
| **Mitigation** | Document the limitation. Use 3D mesh for structures with known undercut. |
| **Fallback** | A 3D mesh renderer path can be added as an optional extension. |

### R5 — Process Parameter Defaults Not Validated Against Real Fabrication Data

| Aspect | Detail |
|---|---|
| **Category** | Parameter accuracy |
| **Description** | Default values (sidewall angle = 87°, CD bias = 2 nm, corner radius = 5 nm) are derived from published literature, not from a specific fab process. Actual values vary by process, tool, and recipe. |
| **Probability** | **High** — defaults are generic |
| **Impact** | **Low** — all parameters are configurable; defaults serve as starting points |
| **Overall** | **Low** |
| **Mitigation** | Make all parameters configurable. Provide a range of presets for common nodes (N5, N7, N28). |
| **Fallback** | Users can calibrate parameters to match their own process by adjusting the configurable values. |

### R6 — GDSII Rasterization Resolution

| Aspect | Detail |
|---|---|
| **Category** | Implementation complexity |
| **Description** | Rasterizing GDSII polygons to a pixel grid at 1 nm/pixel with curved edges requires an accurate polygon-to-grid conversion. Sub-pixel accuracy at line edges is needed for correct CD in the height field. |
| **Probability** | **Moderate** — implementation complexity |
| **Impact** | **Moderate** — sub-pixel rasterization errors affect CD accuracy |
| **Overall** | **Medium** |
| **Mitigation** | Use anti-aliased rasterization (LUT-based or supersampling). Validate CD accuracy against input. |
| **Fallback** | Increase rasterization resolution by 2× and downsample for higher edge accuracy. |

---

## 3. Risk Register

| ID | Risk | Probability | Impact | Overall | Priority |
|---|---|---|---|---|---|
| R1 | LER generation performance | Low | Moderate | **Low** | 6 |
| R2 | Overlay invisible at small FOV | High | Low | **Low** | 5 |
| R3 | Material ID granularity | Moderate | Moderate | **Medium** | 2 |
| R4 | 2.5D re-entrant limitation | Low | Moderate | **Low–Medium** | 4 |
| R5 | Parameter defaults generic | High | Low | **Low** | 3 |
| R6 | GDSII rasterization resolution | Moderate | Moderate | **Medium** | 1 |

---

## 4. Risk Mitigation Timeline

| Phase | Risks | Actions |
|---|---|---|
| **Pre-Phase A** | R5, R6 | Implement configurable parameters; design anti-aliased rasterizer |
| **Phase A** | R1, R4 | Test LER performance with worst-case arrays; document 2.5D limitation |
| **Phase B** | R3 | Validate material map behavior for thin-film stacks |
| **Phase C** | R2 | Provide guidance on overlay visibility vs. FOV |
| **Ongoing** | All | Maintain risk register; re-evaluate as implementation progresses |
