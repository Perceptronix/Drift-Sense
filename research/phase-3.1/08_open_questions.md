# Open Questions

**Research Phase:** 3.1
**Document:** 08_open_questions.md
**Date:** 2026-07-30

---

## 1. Questions Answered Within Phase 3.1

| Question | Answer | Document |
|---|---|---|
| What is the optimal geometry representation for the SEM renderer? | 2.5D height field (height map + material ID map) | 02_geometry_representation_survey.md |
| What are the candidate representations and why are they rejected? | 6 surveyed; SDF, voxel, direct property rejected | 02_geometry_representation_survey.md |
| How are common semiconductor features represented? | 11 feature types catalogued with 2.5D representation | 03_semiconductor_feature_representation.md |
| What is the coordinate system? | X (fast scan), Y (slow scan), Z (height), origin top-left | 04_coordinate_system_specification.md |
| How are materials encoded? | Integer ID per pixel with external lookup table (frozen 0–6) | 05_material_encoding.md |
| What are the required geometry inputs for SEM rendering? | Height map + material map + metadata + pixel spacing | 06_canonical_geometry_inputs.md |
| Which representations should be used for which purpose? | GDSII (source), layer stack (generator), height field (renderer) | 07_engineering_conclusions.md |

---

## 2. Questions for Phase 3.2 (Process Model)

| # | Question | Nature | Impact |
|---|---|---|---|
| Q1 | **What process model converts GDSII layout + parameters to 2.5D height field?** | The core of Phase 3.2. Must simulate deposition, etch, CMP, lithography to produce realistic cross-sections from 2D layout. | Determines the realism of generated geometry. |
| Q2 | **What are the exact layer stack specifications for the target technology node?** | The sequence of materials, their thicknesses, and patterning steps define the starting point for geometry generation. | Required before any realistic structure can be generated. |
| Q3 | **What sidewall angle range is realistic for each etch step?** | Sidewall angles depend on the etch chemistry, aspect ratio, and material. Need typical values for each layer. | Affects CD-SEM edge profile directly. |
| Q4 | **What is the typical corner rounding radius for each etch/dep step?** | Corner rounding depends on lithography and etch. Affects CD-SEM profile at line ends and hole edges. | Affects contact hole and line-end SEM profiles. |
| Q5 | **What is the realistic range for bottom vs. top CD (taper) for each feature?** | Taper angle varies with aspect ratio and etch conditions. | Directly affects CD-SEM bias between top and bottom CD. |
| Q6 | **What CMP dishing and erosion values are typical for BEOL layers?** | CMP introduces non-planarity that affects SEM contrast and CD measurement. | Affects height uniformity across the field. |

---

## 3. Questions for Phase 3.3 and Beyond (Variation)

| # | Question | Phase | Nature |
|---|---|---|---|
| Q7 | What LER/LWR values are typical for the target node? | 3.3 | Statistical variation |
| Q8 | What film thickness variation range is realistic? | 3.3 | Statistical variation |
| Q9 | What is the pitch walk magnitude for self-aligned double patterning? | 3.3 | Systematic variation |
| Q10 | How should mask error (MEEF) be simulated? | 3.3 | Systematic variation |

---

## 4. Questions Deferred (Out of Scope for Phase 3.x)

| # | Question | Reason for Deferral |
|---|---|---|
| D1 | Should true 3D geometries (overhangs) be supported? | <5% of CD-SEM use cases; adds significant complexity |
| D2 | Should the geometry engine read GDSII directly or accept pre-rasterized layouts? | Implementation decision — no research needed |
| D3 | Should the geometry engine produce images or accept parameters and generate automatically? | Implementation decision — depends on use case |
| D4 | Should line edge roughness be applied to the GDSII polygons or the height field? | Implementation decision — Phase 3.3 will decide |

---

## 5. Summary of Unresolved Items

| Item | Critical for Phase A? | Resolution Path | Required By |
|---|---|---|---|
| Process model definition | **Yes** | Phase 3.2 research | Phase A implementation |
| Layer stack specification | **Yes** | Phase 3.2 research | Phase A implementation |
| Sidewall angle values | **Yes** | Phase 3.2 research | Phase A implementation |
| Corner rounding values | **No** (can use defaults) | Phase 3.2 research | Phase B implementation |
| CMP dishing values | **No** (can use flat) | Phase 3.2 research | Phase C implementation |
| LER/LWR values | **No** | Phase 3.3 research | Phase C implementation |
| True 3D support | **No** | Deferred | Project evolution |
| Direct GDSII import | **No** | Implementation decision | Phase A implementation |

---

## Sources

- [E4] M. Quirk and J. Serda, *Semiconductor Manufacturing Technology*, Prentice Hall, 2001.
- [E10] ITRS, 2022 edition.
- [E11] Y. Taur and T. H. Ning, *Fundamentals of Modern VLSI Devices*, 3rd ed. Cambridge, 2021.
- Phase 3.1 Documents 02–07 (this phase).
