# Phase 3.2 Final Report: Semiconductor Process Model

**SEMICON 2026 Research Repository**
**Applied Materials**
**Date:** 2026-07-30
**Classification:** Research-Only (Phase 3.2)

---

## Executive Summary

Phase 3.2 answers the engineering question: **"How should an ideal GDSII layout be transformed into a realistic fabricated semiconductor structure?"**

The canonical process model transforms a GDSII layout through a sequence of deposition → lithography → etch → resist strip → CMP steps per layer, producing a realistic 2.5D height field and material map that captures all essential geometric effects of semiconductor fabrication.

---

## 1. Research Results

### 1.1 Manufacturing Flow (Document 02)

Eight process steps are relevant to geometry generation:

| Step | Essential? | Geometric Effect |
|---|---|---|
| Lithography | **Essential** | Pattern transfer, sidewall profile, corner rounding |
| Etching | **Essential** | Tapered profiles, CD bias, bottom corner rounding |
| Deposition | **Essential** | Film thickness, conformality, sidewall coverage |
| CMP | **Essential** | Planarization, target height, dishing |
| Resist coating | **Recommended** | Part of lithography flow |
| Resist strip | **Recommended** | Clean removal after etch |
| Implantation | **Ignore** | No geometric effect |
| Annealing | **Ignore** | No geometric change visible in SEM |

### 1.2 Process-to-Geometry Mapping (Document 03)

Each process step transforms the height and material fields:

| Step | Height Change | Material Change | Sidewall | Corners |
|---|---|---|---|---|
| Conformal deposition | $+T / \cos\theta$ | New material on all surfaces | Preserved | Rounded outward |
| Bottom-up fill | +$T_{\text{fill}}$ in trenches | Fill material | None | Planar |
| Lithography | +$T_{\text{res}}$ coat, −$T_{\text{res}}$ develop | Resist at pattern | $\theta_{\text{res}}$ | $R_{\text{top}}$, $R_{\text{bottom}}$ |
| Anisotropic etch | −$D_{\text{etch}}$ in openings | Exposes underlying | $\theta_{\text{etch}}$ | $R_{\text{cb}}$ |
| CMP | $\min(h, H_{\text{CMP}})$ | None at surface | None | Slight |
| Resist strip | −$T_{\text{res}}$ where present | Remove resist | None | None |

### 1.3 Feature Cross-Section Models (Document 04)

| Feature | Ideal CAD | Fabricated | Key Parameters |
|---|---|---|---|
| Metal line | Rectangle | Trapezoid + rounded corners | $\theta=87°$, $R=3-15$ nm |
| Contact hole | Circular cylinder | Conical + rounded edges | $\theta=88°$, $R=2-10$ nm |
| FinFET fin | Rectangle | Trapezoid + rounded top | $\theta=87°$, $R_{\text{top}}=3$ nm |
| Gate stack | Rectangle | Multi-trapezoid with spacers | $\theta=87°$, spacer width = 7 nm |
| STI trench | Rectangle | Trapezoid + rounded corners | $\theta=87°$, $R=5-20$ nm |

### 1.4 Process Simplifications (Document 05)

| Classification | Count | Key Examples |
|---|---|---|
| **Essential** | 8 | Sidewall taper, CD bias, corner rounding, etch depth, film thickness, conformality, CMP target, resist CD |
| **Recommended** | 5 | Top corner rounding, resist profile, Cu dishing, non-conformal deposition, spacer formation |
| **Optional** | 11 | Over-etch, micro-trenching, etch lag, CMP erosion, thickness variation |
| **Ignore** | 12 | Implantation, annealing, standing waves, voids, sidewall roughness, silicidation |

### 1.5 Canonical Process Model (Document 06)

The complete geometry generation pipeline:

```
GDSII Layout → Layer Stack Init → [Deposition → Lithography → Etch → Strip → CMP] per layer → Height Field + Material Map
```

Key properties:
- **Composable:** layers can be added/removed/reordered
- **Parameterized:** all node-specific values are configurable
- **Consistent:** output matches Phase 2.6 geometry interface

### 1.6 Engineering Conclusions (Document 07)

| Category | Count | Status |
|---|---|---|
| Fixed assumptions | 7 | Frozen |
| Configurable parameters | 27 | Frozen with defaults |
| Recommended implementation order | 12 modules | Defined |
| Consistency with previous phases | 5 checks | All pass |

---

## 2. Engineering Decisions

| # | Decision | Rationale |
|---|---|---|
| ED1 | Anisotropic RIE as default etch | Standard for semiconductor patterning |
| ED2 | Trapezoidal profile with corner rounding | Captures >90% of geometric difference from ideal |
| ED3 | Layer-by-layer sequential processing | Matches fabrication reality |
| ED4 | CMP modeled as height clipping + optional dishing | Sufficient for CD-SEM simulation |
| ED5 | Implantation and annealing ignored | No geometric effect visible in SEM |
| ED6 | Analytical profiles (trapezoid + arcs) rather than numerical level sets | Simpler implementation; sufficient accuracy for CD-SEM |
| ED7 | Configurable parameters per layer | Enables multi-node support without changing the model |

---

## 3. Phase 3.2 Success Criteria

| Criterion | Status | Evidence |
|---|---|---|
| ✓ How ideal layout becomes fabricated structure | **Achieved** | Process model defined: GDSII → 8 step transformations |
| ✓ Fabrication steps that modify geometry | **Achieved** | 4 essential, 2 recommended, 2 ignore classified |
| ✓ Canonical process model | **Achieved** | 6-stage per-layer pipeline defined with full specification |
| ✓ Required geometric outputs | **Achieved** | Height field + material map + metadata |
| ✓ Simplified fabrication effects | **Achieved** | 36 effects classified; 12 ignored with justification |

---

## 4. Knowledge Required for Phase 3.3

Phase 3.2 establishes **how to transform an ideal layout into a realistic structure**. Phase 3.3 must answer **how to add realistic manufacturing variability**.

Phase 3.3 must answer:

1. **Statistical process parameter distributions:** What are the wafer-level and wafer-to-wafer distributions (type, sigma, range) for:
   - CD per feature type (CDU)
   - Sidewall angle and corner radius
   - Film thickness
   - CMP dishing and erosion depth
   - Overlay alignment between layers

2. **Line edge roughness model:** What LER model (autocorrelation function, RMS amplitude, correlation length) best represents EUV lithography at the target node?

3. **Systematic variation models:** What are the known systematic patterns:
   - Across-wafer CD variation (radial, field position)
   - Etch micro-loading (dense vs. isolated CD bias)
   - CMP pattern density effects (erosion vs. pattern density function)

4. **Correlation structure:** Which process parameters are correlated and what is the correlation coefficient?

5. **Defect models (if required):** Should realistic process defects (missing features, bridges, particles) be simulated?

**Phase 3.3 transitions from deterministic geometry to statistical geometry. It is the final geometry research phase before integration with the SEM physics engine.**

---

## 5. Phase 3.2 Document Map

```
research/phase-3.2/
│
├── 01_executive_summary.md              ← Research overview and key findings
├── 02_semiconductor_manufacturing_flow.md ← 8 process steps with geometric effects
├── 03_process_to_geometry_mapping.md    ← Height/material transformations per step
├── 04_feature_cross_section_models.md   ← 9 feature types: ideal vs. fabricated vs. modeled
├── 05_process_simplifications.md        ← 36 effects classified E/R/O/I
├── 06_canonical_process_model.md        ← Complete geometry generation pipeline
├── 07_engineering_conclusions.md        ← Frozen parameters and implementation order
├── 08_open_questions.md                ← 7 questions for Phase 3.3
├── 09_complete_reference_list.md        ← 17 primary + 17 cross-phase references
└── 10_phase3_2_final_report.md          ← This consolidated report
```

---

*End of Phase 3.2 Final Report*
