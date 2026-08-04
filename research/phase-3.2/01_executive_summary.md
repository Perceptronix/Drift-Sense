# Phase 3.2 Executive Summary: Semiconductor Process Model

**SEMICON 2026 Research Repository**
**Applied Materials**
**Date:** 2026-07-30
**Classification:** Research-Only (Phase 3.2)

---

## Purpose

This phase answers the engineering question: **"How should an ideal GDSII layout be transformed into a realistic fabricated semiconductor structure?"**

The Phase 3.1 geometry specification defined **what** to provide to the SEM physics engine (2.5D height field + material map). This phase defines **how to generate those inputs from a layout and process parameters** — the canonical process model for the Geometry Engine.

---

## Key Findings

### 1. Manufacturing Flow → Geometry Flow

Eight major process steps are relevant to geometry generation:

| Step | Geometric Effect | Essential? |
|---|---|---|
| **Lithography** | Transfers layout pattern to resist; creates mask with sidewall angles | **Essential** |
| **Etching** | Transfers resist pattern into underlying layer; defines sidewall angle, bottom CD, corner rounding | **Essential** |
| **Deposition** | Adds conformal material; defines layer thicknesses, step coverage | **Essential** |
| **CMP** | Planarizes topography; defines layer heights, dishing, erosion | **Essential** |
| **Photoresist coating** | Creates flat masking layer | Recommended (part of lithography) |
| **Photoresist strip** | Removes masking layer after etch | Recommended (part of process loop) |
| **Implantation** | Doping — negligible geometric effect (cannot be directly seen by SEM) | **Ignore** |
| **Annealing** | Causes diffusion — negligible geometric change at process scale | **Ignore** |

### 2. Ideal vs. Fabricated Geometry

| Parameter | Ideal CAD | Fabricated |
|---|---|---|
| Sidewall angle | 90° (vertical) | 85–89° (slightly tapered) |
| Bottom corners | Sharp (90°) | Rounded (R = 3–10 nm) |
| Top corners | Sharp (90°) | Rounded (R = 2–5 nm) |
| Line CD | Constant | Top CD < Bottom CD (tapered profile) |
| Contact shape | Perfect cylinder | Slightly conical (taper) |
| Film surfaces | Perfectly flat | Slight roughness (CMP dishing) |
| Material interfaces | Atomically sharp | ∼1 nm interdiffusion |

**Inference:** The dominant geometric differences between ideal and fabricated structures are **sidewall taper, corner rounding, and non-vertical profiles**. These are the essential effects to model.

### 3. Canonical Process Model

```
GDSII Layout
    │
    ▼
┌─────────────────────┐
│ Layer Stack         │ ← Material and thickness per layer
│ (input parameters)  │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ Lithography Model   │ ← Transfer pattern to resist with corner rounding
│ (mask → resist)     │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ Etch Model          │ ← Transfer resist to layer with taper & bias
│ (anisotropic / iso) │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ Deposition Model    │ ← Add conformal materials
│ (conformal / fill)  │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ CMP Model           │ ← Planarize: remove topography to target height
│ (planarization)     │
└────────┬────────────┘
         │  (repeated for each layer in stack)
         ▼
┌─────────────────────┐
│ 2.5D Height Field   │ → To SEM Physics Engine
│ + Material Map      │
└─────────────────────┘
```

**The model is applied iteratively:** For each layer in the stack, lithography → etch → deposition → CMP are applied in sequence, building up the 3D structure layer by layer.

### 4. Process Simplifications

| Effect | Classification | Justification |
|---|---|---|
| Sidewall taper (85–89°) | **Essential** | Directly affects SEM edge profile |
| Corner rounding (top/bottom) | **Essential** | Affects SEM intensity at edges |
| CD bias (etch → final) | **Essential** | Determines final CD from mask CD |
| Trench bottom rounding | **Recommended** | Affects trench SEM profile |
| Conformal deposition thinning | **Recommended** | Affects sidewall material thickness |
| CMP dishing | **Optional** | Affects BEOL SEM profiles |
| CMP erosion | **Optional** | Affects dense vs. isolated features |
| Resist sidewall angle | **Recommended** | Affects final sidewall angle |
| Over-etch | **Recommended** | Creates micro-trenching at feature bottom |
| Film stress deformation | **Ignore** | <1 nm for standard films |
| Annealing diffusion | **Ignore** | Negligible geometry change |
| Implantation damage | **Ignore** | No SEM-visible geometry change |
| Microloading effects | **Ignore** | First-order model sufficient |
| Aspect-ratio-dependent etch | **Ignore** | Only matters for AR > 20:1 |

### 5. Technology Node Parameters

The process model is parameterized per technology node:

| Parameter | Mature (130 nm) | Planar (45 nm) | FinFET (N5) |
|---|---|---|---|
| Minimum CD | 130 nm | 45 nm | 7–10 nm |
| Fin width | N/A | N/A | 5–8 nm |
| Contact diameter | 180 nm | 60 nm | 20–30 nm |
| Gate length | 90 nm | 35 nm | 12–18 nm |
| Typical etch sidewall | 88–90° | 86–89° | 85–88° |
| Corner radius | 20–50 nm | 5–15 nm | 2–5 nm |
| Aspect ratio (contacts) | 3:1 | 5:1 | 8–15:1 |

**Engineering Decision:** The process model does not aim to simulate exact fabrication. It aims to produce **realistic-looking 2.5D structures** with correct geometric parameters for SEM simulation. The model prioritizes geometric fidelity over process accuracy.

---

## Phase 3.3 Knowledge Required

Phase 3.3 must answer:

1. **Manufacturing variability model:** How are realistic random and systematic variations (LER, CDU, thickness variation, overlay error) added to the ideal process model output?

2. **Statistical parameter distributions:** What are the typical distributions (type, sigma, range) for each process parameter at the target node?

3. **Correlation models:** Which process variations are correlated (e.g., LER correlation length, CD vs. thickness coupling)?

---

## Sources

- [F1] J. D. Plummer, M. D. Deal, P. B. Griffin, *Silicon VLSI Technology*, Prentice Hall, 2000.
- [F2] S. Wolf and R. N. Tauber, *Silicon Processing for the VLSI Era*, Lattice Press, 2002.
- [F3] C. Mack, *Fundamental Principles of Optical Lithography*, Wiley, 2007.
- [F4] M. Quirk and J. Serda, *Semiconductor Manufacturing Technology*, Prentice Hall, 2001.
- [F5] J. Lienig and J. Scheible, *Fundamentals of Layout Design*, Springer, 2020.
- [F6] M. J. Madou, *Fundamentals of Microfabrication and Nanotechnology*, CRC Press, 2011.
- [F7] K. Ahmed and K. Schuegraf, "Transistor wars," *IEEE Spectrum*, 2011.
- [F8] Y. Taur and T. H. Ning, *Fundamentals of Modern VLSI Devices*, Cambridge, 2021.
- [F9] imec, "Core technology scaling," *imec Technology Forum*, 2023.
