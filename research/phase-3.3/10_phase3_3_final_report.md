# Phase 3.3 Final Report: Manufacturing Variability

**SEMICON 2026 Research Repository**
**Applied Materials**
**Date:** 2026-07-30
**Classification:** Research-Only (Phase 3.3)

---

## Executive Summary

Phase 3.3 answers the engineering question: **"How should deterministic geometry be transformed into realistic manufactured geometry?"**

Eleven variability mechanisms were researched and classified. Models were selected for each based on physical correctness, parameter count, and implementability. LER and LWR are the **essential** mechanisms — without them, simulated edge profiles are unphysically sharp.

---

## 1. Research Results

### 1.1 LER and LWR (Document 02)

| Finding | Specification |
|---|---|
| **Physical origin** | EUV photon shot noise, acid diffusion, polymer dissolution |
| **Recommended model** | Gaussian random process with exponential autocorrelation |
| **Default σ_LER** | 2.4 nm (3σ) — typical N5 EUV |
| **Correlation length ξ** | 25 nm |
| **LWR relation** | $\sigma_{\text{LWR}} = \sqrt{2(1-\rho)} \cdot \sigma_{\text{LER}}$, default ρ = 0.3 |
| **Generation method** | Filtered Gaussian noise (FIR convolution) |

**Key insight:** LER is the single most important variability mechanism for SEM realism. Without it, edges appear too sharp and CD measurement precision is unrealistically high.

### 1.2 CD Variation (Document 03)

| Component | Spatial Scale | Model | Classification |
|---|---|---|---|
| Across-feature (LER/LWR) | 1–100 nm | Gaussian random process | **Essential** |
| Across-die (field) | 1–30 mm | Gaussian μ + low-order polynomial | **Optional** |
| Across-wafer | 10–300 mm | Gaussian μ + radial parabolic | **Optional** |

**Inference:** At a single CD-SEM image FOV (∼1 μm), only LER/LWR is visible. Field and wafer variation appear as constant offsets per image.

### 1.3 Overlay and Alignment (Document 04)

| Component | Magnitude (3σ) | Classification |
|---|---|---|
| Translation X | 4.0 nm | **Recommended** |
| Translation Y | 4.0 nm | **Recommended** |
| Rotation | 0.15 μrad | **Optional** |
| Scaling | <0.1 nm at 1 μm FOV | **Ignore** |

**Key insight:** Overlay translation is visible in multi-layer SEM images when >2 nm. Rotation and higher-order distortion are negligible at CD-SEM resolution.

### 1.4 Shape and Surface Variations (Document 05)

| Variation | Model | Default | Classification |
|---|---|---|---|
| Sidewall angle | Truncated Gaussian | $\sigma_\theta = 1^\circ$ | **Recommended** |
| Corner radius | Gaussian | $\sigma_R = 1$ nm | **Recommended** |
| Film thickness | Gaussian relative | $\sigma_T = 5\%$ | **Optional** |
| CMP dishing | Parabolic + Gaussian depth | $d_0 = 15$ nm | **Recommended** |
| CMP erosion | Density-linear + Gaussian | $e_0 = 0.05$ | **Optional** |

### 1.5 Statistical Models (Document 06)

| Variation Type | Selected Model | Parameters | Reason |
|---|---|---|---|
| LER | Gaussian random process, exponential ACF | $\sigma$, $\xi$ | Physical — matches PSD |
| CDU | Gaussian | $\mu$, $\sigma$ | Central limit theorem |
| Overlay | Gaussian | $0$, $\sigma$ | Standard semiconductor model |
| Sidewall angle | Truncated Gaussian | $\mu$, $\sigma$, bounds | Bounded by physics |
| Thickness | Gaussian relative | $\mu$, $\sigma_{\text{rel}}$ | Deposition data confirmed |
| CMP dishing | Parabolic + Gaussian | $d_0$, $\beta$, $\sigma$ | Physics-based |

### 1.6 Engineering Classification (Document 07)

| Classification | Count | Mechanisms | Implementation Phase |
|---|---|---|---|
| **Essential** | 2 | LER, LWR | Phase A |
| **Recommended** | 4 | Sidewall angle variation, corner rounding, CMP dishing, overlay translation | Phase C |
| **Optional** | 3 | CDU field, thickness variation, CMP erosion | Phase D |
| **Ignore** | 2 | Scanner distortion, wafer warpage | Never |

---

## 2. Frozen Default Parameters

| Parameter | Default | Range | Distribution | Classification |
|---|---|---|---|---|
| LER 3σ | 2.4 nm | 1.0–5.0 nm | Gaussian random process | **Essential** |
| LER correlation length ξ | 25 nm | 10–50 nm | Exponential ACF | **Essential** |
| LER left-right correlation ρ | 0.3 | 0.0–0.7 | — | **Essential** |
| LWR (derived) | 3.4 nm | 1.4–7.1 nm | Derived from LER | **Essential** |
| Sidewall angle σ | 1.0° | 0.5–2.0° | Truncated Gaussian | **Recommended** |
| Corner radius σ | 1.0 nm | 0.5–2.0 nm | Gaussian | **Recommended** |
| CMP dishing d₀ | 15 nm | 5–50 nm | Parabolic + noise | **Recommended** |
| Overlay translation σ | 4.0 nm | 2.0–8.0 nm | Gaussian | **Recommended** |
| CDU field σ | 2.0 nm | 1.0–4.0 nm | Gaussian | **Optional** |
| Thickness σ_rel | 5% | 2–10% | Gaussian relative | **Optional** |
| CMP erosion e₀ | 0.05 | 0.02–0.10 | Density-linear | **Optional** |

---

## 3. Engineering Decisions

| # | Decision | Rationale |
|---|---|---|
| ED1 | LER model = Gaussian random process with exponential ACF | Matches measured PSD; simplest adequate model |
| ED2 | LWR derived from two correlated LER realizations | Physically correct; captures left–right correlation |
| ED3 | CDU modeled as Gaussian at each spatial scale | Central limit theorem applies |
| ED4 | Overlay modeled as Gaussian translation only | Higher-order terms negligible at CD-SEM FOV |
| ED5 | Sidewall angle variation modeled as truncated Gaussian | Bounded by etch physics (85–89°) |
| ED6 | CMP dishing modeled as parabolic + Gaussian depth | Physics-based; captures both shape and variation |
| ED7 | Random variables assumed independent | Simplest assumption; correlation deferred to Phase D |
| ED8 | LER generation via spatial domain FIR convolution | FFT not needed; filter length ∼125 samples |

---

## 4. Phase 3.3 Success Criteria

| Criterion | Status | Evidence |
|---|---|---|
| ✓ How normal variability changes geometry | **Achieved** | 11 mechanisms characterized |
| ✓ Which variations dominate SEM appearance | **Achieved** | LER and LWR are essential |
| ✓ Appropriate statistical models | **Achieved** | 6 model types selected with justification |
| ✓ Essential mechanisms for realistic data | **Achieved** | LER, LWR essential; 4 recommended; 3 optional |
| ✓ Frozen variability specification | **Achieved** | 11 parameters with defaults and ranges |

---

## 5. Knowledge Required for Phase 3.4

Phase 3.3 establishes **how to transform deterministic geometry into realistic variable geometry**. Phase 3.4 must answer:

1. **How are parameterized variable-geometry structures organized into a reusable library?** The library specification — schema, naming convention, versioning, storage format — that makes it possible to generate, share, and reuse geometry definitions across the project.

2. **What is the end-to-end geometry generation workflow?** From GDSII input → process model (Phase 3.2) → variability engine (Phase 3.3) → final height field and material map. The integration of all three geometry phases into a single generator.

3. **Should the library include pre-generated height fields or generate on demand?** The trade-off between storage size, generation time, and flexibility.

Phase 3.4 transitions from **individual variability mechanisms** to **reusable geometry specifications** — the final piece needed before the geometry engine outputs can be passed to the SEM physics renderer for image generation.

---

## 6. Phase 3.3 Document Map

```
research/phase-3.3/
│
├── 01_executive_summary.md              ← Research overview and key findings
├── 02_line_edge_and_line_width_roughness.md ← LER/LWR physics, models, defaults
├── 03_critical_dimension_variation.md   ← CDU components: across-feature/die/wafer
├── 04_overlay_and_alignment_errors.md   ← Overlay components and SEM visibility
├── 05_shape_and_surface_variations.md   ← Sidewall, thickness, corner, CMP variations
├── 06_statistical_variability_models.md ← Model selection, generation algorithms
├── 07_engineering_classification.md     ← 11 mechanisms classified E/R/O/I
├── 08_open_questions.md                ← 6 questions for Phase 3.4
├── 09_complete_reference_list.md        ← 17 primary + cross-phase references
└── 10_phase3_3_final_report.md          ← This consolidated report
```

---

*End of Phase 3.3 Final Report*
