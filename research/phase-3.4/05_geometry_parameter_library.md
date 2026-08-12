# Geometry Parameter Library

**Research Phase:** 3.4
**Document:** 05_geometry_parameter_library.md
**Date:** 2026-07-30

---

## 1. Parameter Organization

All geometry parameters are organized into 5 categories:

| Category | Count | Description |
|---|---|---|
| **Global** | 5 | Resolution, coordinate, output parameters |
| **Material** | 7 | Material IDs (frozen, per Phase 2.2) |
| **Feature geometry** | 18 | Dimensions, angles, radii per feature type |
| **Process** | 10 | Deposition, lithography, etch, CMP parameters |
| **Variability** | 8 | LER, CDU, overlay, shape variation parameters |
| **Total** | **48** | |

---

## 2. Global Parameters

| # | Parameter | Symbol | Units | Default | Range | Category | Source |
|---|---|---|---|---|---|---|---|
| 1 | Image width | M | pixels | 1024 | 256–4096 | Configurable | Phase 3.1 |
| 2 | Image height | N | pixels | 1024 | 256–4096 | Configurable | Phase 3.1 |
| 3 | Pixel size | Δx | nm | 1.0 | 0.2–5.0 | Configurable | Phase 2.6 |
| 4 | Height scale | s_z | nm/DN | 0.1 | 0.1–1.0 | Fixed | Phase 3.1 |
| 5 | Coordinate origin | — | — | Top-left pixel | — | Fixed | Phase 3.1 |

---

## 3. Material Parameters

| # | ID | Name | Tag | Type | Used As |
|---|---|---|---|---|---|
| 6 | 0 | Vacuum | vacuum | Background | Empty space |
| 7 | 1 | Silicon | silicon | Semiconductor | Substrate, fins |
| 8 | 2 | Silicon Dioxide | oxide | Dielectric | STI, ILD, spacers |
| 9 | 3 | Silicon Nitride | nitride | Dielectric | Spacers, hardmask |
| 10 | 4 | Copper | copper | Conductor | BEOL lines, vias |
| 11 | 5 | Tungsten | tungsten | Conductor | Contacts |
| 12 | 6 | Photoresist | resist | Organic | Lithography mask |

---

## 4. Feature Geometry Parameters

| # | Parameter | Symbol | Units | Default | Range | Used In | Source |
|---|---|---|---|---|---|---|---|
| 13 | Line CD (top) | CD_top | nm | 20.0 | 5–500 | Lines, LS arrays | Phase 3.2 |
| 14 | Line CD (bottom) | CD_bot | nm | 22.0 | 5–505 | Lines, LS arrays | Phase 3.2 |
| 15 | Line pitch | P | nm | 40.0 | 10–1000 | LS arrays | Phase 3.2 |
| 16 | Line height | H | nm | 50.0 | 5–500 | Lines, LS arrays | Phase 3.2 |
| 17 | Contact top diameter | D_top | nm | 30.0 | 10–200 | Contacts | Phase 3.2 |
| 18 | Contact bottom diameter | D_bot | nm | 26.0 | 8–196 | Contacts | Phase 3.2 |
| 19 | Contact depth | D_cont | nm | 100.0 | 20–500 | Contacts | Phase 3.2 |
| 20 | Via top diameter | D_via_top | nm | 20.0 | 10–100 | Vias | Phase 3.2 |
| 21 | Via bottom diameter | D_via_bot | nm | 18.0 | 8–98 | Vias | Phase 3.2 |
| 22 | Via depth | D_via | nm | 40.0 | 15–200 | Vias | Phase 3.2 |
| 23 | Fin top CD | CD_fin_top | nm | 6.0 | 4–15 | Fins | Phase 3.2 |
| 24 | Fin bottom CD | CD_fin_bot | nm | 8.0 | 5–18 | Fins | Phase 3.2 |
| 25 | Fin height | H_fin | nm | 40.0 | 20–80 | Fins | Phase 3.2 |
| 26 | Fin pitch | P_fin | nm | 30.0 | 20–60 | Fins | Phase 3.2 |
| 27 | Gate length | L_gate | nm | 16.0 | 10–40 | Gates | Phase 3.2 |
| 28 | Gate height | H_gate | nm | 50.0 | 20–80 | Gates | Phase 3.2 |
| 29 | Spacer width | W_spacer | nm | 7.0 | 3–15 | Gates | Phase 3.2 |
| 30 | STI depth | D_sti | nm | 300.0 | 100–500 | STI | Phase 3.2 |

---

## 5. Process Parameters

| # | Parameter | Symbol | Units | Default | Range | Category | Source |
|---|---|---|---|---|---|---|---|
| 31 | Sidewall angle (etch) | θ_etch | deg | 87.0 | 85–89 | Essential | Phase 3.2 |
| 32 | Sidewall angle (resist) | θ_res | deg | 87.0 | 85–89 | Recommended | Phase 3.2 |
| 33 | CD bias | ΔCD | nm | 2.0 | 0–20 | Essential | Phase 3.2 |
| 34 | Bottom corner radius | R_cb | nm | 5.0 | 2–20 | Essential | Phase 3.2 |
| 35 | Top corner radius | R_ct | nm | 3.0 | 1–10 | Recommended | Phase 3.2 |
| 36 | Resist thickness | T_res | nm | 150.0 | 50–300 | Recommended | Phase 3.2 |
| 37 | Etch selectivity to mask | S_etch | — | 20.0 | 5–100 | Optional | Phase 3.2 |
| 38 | Over-etch fraction | O_e | % | 10.0 | 0–50 | Optional | Phase 3.2 |
| 39 | CMP target height | H_CMP | nm | Per layer | — | Essential | Phase 3.2 |
| 40 | Film thickness | T_dep | nm | Per layer | — | Essential | Phase 3.2 |

---

## 6. Variability Parameters

| # | Parameter | Symbol | Units | Default | Range | Category | Source |
|---|---|---|---|---|---|---|---|
| 41 | LER 3σ | σ_LER | nm | 2.4 | 1.0–5.0 | Essential | Phase 3.3 |
| 42 | LER correlation length | ξ | nm | 25.0 | 10–50 | Essential | Phase 3.3 |
| 43 | LER roughness exponent | α | — | 0.5 | 0.3–0.7 | Essential | Phase 3.3 |
| 44 | LER left–right correlation | ρ | — | 0.3 | 0.0–0.7 | Essential | Phase 3.3 |
| 45 | Sidewall angle σ | σ_θ | deg | 1.0 | 0.5–2.0 | Recommended | Phase 3.3 |
| 46 | Corner radius σ | σ_R | nm | 1.0 | 0.5–2.0 | Recommended | Phase 3.3 |
| 47 | Overlay translation σ | σ_ovl | nm | 4.0 | 2.0–8.0 | Recommended | Phase 3.3 |
| 48 | CMP dishing depth | d_dish | nm | 15.0 | 5–50 | Recommended | Phase 3.3 |

---

## 7. Parameter Dependency Rules

| Rule | Description |
|---|---|
| CD_bot = CD_top + 2 × H / tan(90° − θ) | Sidewall taper relationship |
| LWR = √(2 × (1 − ρ)) × LER | LWR from LER and correlation |
| Pitch = CD + Space | Covers entire array width |
| Aspect ratio = Depth / CD_top | For contacts and trenches |
| CMP dish depth ∝ CD^0.5 | Dishing scales with feature size |

---

## Sources

- Phase 2.5, Document 02 — Frozen physical parameters.
- Phase 2.6, Document 06 — Geometry interface specification.
- Phase 3.1, Documents 04, 06 — Coordinate system, canonical inputs.
- Phase 3.2, Documents 04, 06, 07 — Feature cross-sections, process model.
- Phase 3.3, Documents 02, 06, 07 — LER, statistical models, classification.
