# Phase 3.1 Final Report: Geometry Engine Research

**SEMICON 2026 Research Repository**
**Applied Materials**
**Date:** 2026-07-30
**Classification:** Research-Only (Phase 3.1)

---

## Executive Summary

Phase 3.1 answers the engineering question: **"What geometric representation should be provided to the SEM physics engine?"**

Six candidate representations were surveyed. The **2.5D height field** (height map + material ID map) was selected as the optimal representation for CD-SEM simulation. The coordinate system was specified, material encoding was frozen, and the required inputs to the SEM physics engine were defined.

**All decisions in this phase are consistent with the frozen geometry interface from Phase 2.6, Document 06.**

---

## 1. Research Results

### 1.1 Geometry Representation Survey (Document 02)

| Representation | Verdict | Role |
|---|---|---|
| **Polygon/GDSII** | **Recommended** | Layout source format |
| **2.5D Height Field** | **Recommended** | Renderer input |
| **3D Triangle Mesh** | **Acceptable** | Special cases (overhangs) |
| **Layer stack** | **Acceptable** | Generator internal format |
| **Signed Distance Field** | **Not recommended** | Overkill for 2.5D; memory-bound |
| **Voxel Grid** | **Not recommended** | 256× memory overhead; no benefit for surface rendering |

**Key finding:** The 2.5D height field is optimal because:
- All common CD-SEM targets are 2.5D (no overhangs)
- Memory is O(M×N) instead of O(M×N×Z)
- Surface normals are a trivial gradient computation
- Directly consumable by the SEM physics renderer

### 1.2 Semiconductor Feature Representation (Document 03)

| Feature Type | 2.5D OK? | Key Parameters | Material Count |
|---|---|---|---|
| Metal line | ✓ | CD, height, pitch, sidewall angle | 2 |
| Trench | ✓ | Depth, CD, taper | 2 |
| Contact hole | ⚠ (circular, approx.) | Diameter, depth, aspect ratio | 2–3 |
| FinFET fin | ✓ | Width, height, pitch | 1–2 |
| Gate structure | ✓ | Length, height, spacer width | 3–5 |
| STI | ✓ | Depth, width, corner rounding | 2 |
| DRAM capacitor | ✓ | Diameter, depth (high AR) | 2–3 |

**Minimum geometric information per feature:** CD, height, material(s), and pitch (for periodic structures). Sidewall angle and corner rounding are optional with defaults.

### 1.3 Coordinate System (Document 04)

| Convention | Value |
|---|---|
| X axis | Fast scan (horizontal, left→right) |
| Y axis | Slow scan (vertical, top→bottom) |
| Z axis | Height (out-of-plane, upward) |
| Origin | Top-left pixel |
| Z = 0 | Substrate bottom |
| Units | Nanometers (all axes) |
| Height encoding | Absolute Z (not relative layer thickness) |

**Consistent with Phase 2.6 geometry interface.** No conflicts.

### 1.4 Material Encoding (Document 05)

| Method | Verdict |
|---|---|
| **Integer ID lookup** | **Recommended** (frozen: IDs 0–6) |
| Layer-based encoding | **Acceptable** (generator internal) |
| Direct property storage | **Not recommended** |
| Color-mapped | **Not recommended** |

**Frozen material ID table:**
- 0 = Vacuum, 1 = Si, 2 = SiO₂, 3 = Si₃N₄, 4 = Cu, 5 = W, 6 = Photoresist
- IDs 7–65535 reserved for future expansion

### 1.5 Canonical Geometry Inputs (Document 06)

| Required Input | Format | Reason |
|---|---|---|
| Height map $h[u][v]$ | 16-bit PNG | Surface normals, topography |
| Material ID map $m[u][v]$ | 16-bit PNG | Material contrast, yield, charging |
| Pixel spacing $\Delta x$ | Float (metadata) | Physical scaling |
| Metadata | PNG text + JSON | Validation, traceability |

All other quantities (surface normals, $\theta$, $\delta_0$, $\eta$, $\Lambda$, $f_c$) are **derived** by the physics engine from these four inputs.

---

## 2. Engineering Decisions

| # | Decision | Rationale |
|---|---|---|
| ED1 | 2.5D height field as renderer input | Minimal memory; direct surface normals; matches CD-SEM targets |
| ED2 | Integer material ID with external lookup | Simple, maintainable, extensible |
| ED3 | Layer stack as generator internal format | Maps to process flow; enables process-aware generation |
| ED4 | GDSII as source format | Industry standard |
| ED5 | No full 3D unless overhangs exist | 2.5D covers >95% of use cases |
| ED6 | Sharp material boundaries initially | Interface width (∼1 nm) ≈ pixel size (1 nm) |
| ED7 | Height map stores absolute Z (not relative) | Simplest for rendering; conversion done in generator |

---

## 3. Recommendations for Implementation

| Priority | Recommendation | Phase |
|---|---|---|
| 1 | Implement height field + material map as two 16-bit PNGs | Phase A |
| 2 | Implement material lookup library (YAML/JSON) | Phase A |
| 3 | Implement surface normal computation from height gradients | Phase A |
| 4 | Implement input validation (format, materials, metadata) | Phase A |
| 5 | Implement layer-stack to height-field conversion engine | Phase 3.2 |
| 6 | Implement GDSII reader for layout import | Phase 3.2 |
| 7 | Add optional 3D mesh support for overhangs | Phase D |
| 8 | Add graded material interfaces | Phase C |

---

## 4. Phase 3.1 Success Criteria

| Criterion | Status | Evidence |
|---|---|---|
| ✓ Optimal geometry representation selected | **Achieved** | 2.5D height field recommended |
| ✓ Canonical coordinate system defined | **Achieved** | Document 04 |
| ✓ Material encoding strategy frozen | **Achieved** | Integer ID + lookup (Document 05) |
| ✓ Required geometry inputs specified | **Achieved** | Height + material + metadata (Document 06) |
| ✓ Frozen geometry specification complete | **Achieved** | Consistent with Phase 2.6 interface |
| ✓ All representations classified | **Achieved** | 6 surveyed, 3 recommended, 3 rejected |
| ✓ Semiconductor features catalogued | **Achieved** | 11 feature types (Document 03) |

---

## 5. Knowledge Required for Phase 3.2

Phase 3.1 established **what** geometry to provide. Phase 3.2 must establish **how to generate it from a layout**.

Phase 3.2 must answer:

1. **Process model definition:** How does the geometry generator convert GDSII layout + process parameters into a realistic 3D structure? This is the core of Phase 3.2.

2. **Layer stack specification:** The exact sequence of materials, thicknesses, and pattern names for the target technology node (e.g., N5 FinFET BEOL). Without this, no realistic structures can be generated.

3. **Process parameter values:** Realistic ranges for:
   - Sidewall angles per etch step (e.g., 85–89° for metal etch)
   - Corner rounding radii (e.g., 3–10 nm for lithography)
   - Taper angles per feature type
   - CMP dishing and erosion values
   - Film deposition conformality

4. **CD target values:** The specific CDs and pitches for each feature type at the target node, needed to validate that generated geometry matches industrial targets.

5. **Layer-thickness-to-height conversion algorithm:** How the layer stack + process model produces absolute Z values for the height field.

**The output of Phase 3.2 is the geometry generator specification — the engine that produces realistic 2.5D height fields from process-aware parameters.**

---

## 6. Phase 3.1 Document Map

```
research/phase-3.1/
│
├── 01_executive_summary.md              ← Research overview and key findings
├── 02_geometry_representation_survey.md ← 6 representations surveyed and compared
├── 03_semiconductor_feature_representation.md ← 11 feature types catalogued
├── 04_coordinate_system_specification.md ← Frozen coordinate conventions
├── 05_material_encoding.md             ← Integer ID + lookup strategy
├── 06_canonical_geometry_inputs.md     ← Required renderer inputs
├── 07_engineering_conclusions.md       ← Classification of all approaches
├── 08_open_questions.md               ← Questions for Phase 3.2 and beyond
├── 09_complete_reference_list.md       ← All cited sources
└── 10_phase3_1_final_report.md         ← This consolidated report
```

---

*End of Phase 3.1 Final Report*
