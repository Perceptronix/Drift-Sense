# Phase 3.3 Executive Summary: Manufacturing Variability

**SEMICON 2026 Research Repository**
**Applied Materials**
**Date:** 2026-07-30
**Classification:** Research-Only (Phase 3.3)

---

## Purpose

This phase answers the engineering question: **"How should deterministic geometry be transformed into realistic manufactured geometry?"**

Phase 3.2 defined how to generate ideal fabricated structures from a GDSII layout. This phase introduces the **normal process variability** that makes manufactured structures differ from their nominal design — the line edge roughness, CD variation, overlay errors, and shape variations that every real wafer exhibits.

---

## Key Findings

### 1. Six Variability Mechanisms Identified

| Mechanism | Typical Magnitude | SEM Visibility | Classification |
|---|---|---|---|
| Line edge roughness (LER) | σ = 1.5–3.0 nm, ξ = 15–40 nm | **High** — affects edge sharpness | **Essential** |
| Line width roughness (LWR) | 3σ = 2–5 nm | **High** — correlates with LER | **Essential** |
| Critical dimension uniformity (CDU) | 3σ = 1–3 nm per field | **Moderate** — visible across array | **Recommended** |
| Overlay error | μ = 0–5 nm, 3σ = 2–8 nm | **Low–Moderate** — subtle at typical FOV | **Optional** |
| Shape variation (sidewall, height) | ±3–5° sidewall, ±5% thickness | **Moderate** — visible in profile | **Recommended** |
| CMP topography (dishing, erosion) | 5–30 nm | **Moderate** — visible across wide features | **Recommended** |

### 2. LER Is the Dominant Effect

Line edge roughness is the **single most important variability mechanism** for CD-SEM appearance:

| Aspect | Specification |
|---|---|
| **Physical origin** | Photon shot noise in EUV resist, acid diffusion during PEB, polymer dissolution statistics |
| **Model type** | PSD-based Gaussian random process with exponential autocorrelation |
| **Default RMS amplitude (3σ)** | 2.4 nm (at target node) |
| **Correlation length** | 25 nm (typical for EUV) |
| **Roughness exponent** | α = 0.5 |

**Inference:** LER directly determines the SEM edge profile width and is the primary source of CD measurement uncertainty in CD-SEM. Without LER, simulated edges are unrealistically sharp.

### 3. Variability Classification

| Classification | Count | Key Examples |
|---|---|---|
| **Essential** | 2 | LER, LWR |
| **Recommended** | 4 | CDU, overlay, sidewall angle variation, CMP dishing |
| **Optional** | 3 | Height variation, thickness variation, CMP erosion |
| **Ignore** | 2 | Chamber-to-chamber matching, wafer bow |

### 4. Statistical Model Selection

| Variation Type | Model | Parameters | Justification |
|---|---|---|---|
| LER (edge displacement) | Gaussian random process with exponential PSD | RMS, ξ, α | Physical — PSD measured by CD-SEM [M1][M3] |
| LWR (width) | Derived from two LER realizations (left + right edges) | RMS_LWR ≈ √2 × RMS_LER | Statistical — two independent edges |
| CDU (field-level) | Gaussian (truncated at ±3σ) | μ = nominal CD, 3σ = 1–3 nm | Central limit theorem applies |
| Overlay (translation) | Gaussian per layer | μ = 0, 3σ = 2–8 nm | Standard semiconductor model |
| Overlay (rotation) | Gaussian per field | μ = 0, 3σ = 0.1–0.3 μrad | Standard model |
| Sidewall angle variation | Truncated Gaussian | μ = 87°, σ = 1° | Bounded (85–89°) |
| Thickness variation | Gaussian | μ = nominal T, σ = 2–5% | Deposition data confirmed |
| CMP dishing | Parabolic profile + Gaussian depth variation | μ_dish = 10 nm for CD > 1 μm | Dishing physics + process variation |

### 5. Frozen Default Parameters

| Parameter | Default (3σ) | Range | Source |
|---|---|---|---|
| LER amplitude | 2.4 nm | 1.5–4.0 nm | imec EUV data [M1][M10] |
| LER correlation length ξ | 25 nm | 10–50 nm | SPIE LER studies [M3][M11] |
| LWR amplitude | 3.4 nm | 2.0–5.0 nm | LER × √2 |
| CDU (field) | 2.0 nm | 1.0–4.0 nm | IRDS [M2] |
| Overlay (translation) | 4.0 nm | 2.0–8.0 nm | IRDS [M2] |
| Sidewall angle variation | 2.0° | 1.0–4.0° | Process data |
| Thickness variation | 5% of T | 2–10% | Deposition data |

---

## Phase 3.4 Knowledge Required

Phase 3.4 must answer:

1. **Reusable feature library specification:** How are the parameterized, variable geometry structures organized into a library of test structures for SEM simulation?

2. **Layout-to-variable-geometry integration:** How does the complete geometry engine (deterministic + variability) accept a layout and produce a set of variable geometry height fields for SEM rendering?

---

## Sources

- [M1] A. Habermas et al., "LER and LWR metrology," *Proc. SPIE*, vol. 10583, 2018.
- [M2] IRDS, "Lithography and Metrology Roadmap," 2023.
- [M3] C. A. Mack, "Line edge roughness," *J. Micro/Nanolith. MEMS MOEMS*, vol. 8, 2009.
- [M4] B. D. Bunday et al., "CD-SEM metrology," *Proc. SPIE*, vol. 5038, 2003.
- [M10] imec, "EUV lithography variability," *Proc. SPIE*, vol. 10957, 2019.
- [M11] G. F. Lorusso et al., "LER transfer in EUV lithography," *Proc. SPIE*, vol. 9776, 2016.
