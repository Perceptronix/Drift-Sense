# Open Questions

**Research Phase:** 3.3
**Document:** 08_open_questions.md
**Date:** 2026-07-30

---

## 1. Questions Answered Within Phase 3.3

| Question | Answer | Document |
|---|---|---|
| What is the physical origin of LER? | EUV photon shot noise, acid diffusion, polymer dissolution statistics | 02 |
| How should LER be modeled? | Gaussian random process with exponential autocorrelation; σ = 2.4 nm, ξ = 25 nm | 02 |
| What is LWR and how does it relate to LER? | LWR = derived from two correlated LER realizations; σ_LWR ≈ √2 σ_LER for ρ = 0.3 | 02 |
| What are the CD variation components? | Across-feature (LER), across-die, across-wafer — with well-separated spatial scales | 03 |
| Which overlay components are visible in SEM? | Only translation (>2 nm); rotation and scaling negligible at typical FOV | 04 |
| Which shape variations affect SEM appearance? | Sidewall angle variation, corner rounding, CMP dishing — all classified E/R/O/I | 05 |
| What statistical models are appropriate? | Gaussian (CDU, overlay), truncated Gaussian (sidewall, thickness), PSD-based (LER) | 06 |
| Which variability mechanisms are essential? | LER and LWR — all others are recommended, optional, or ignore | 07 |

---

## 2. Questions for Phase 3.4 (Reusable Libraries)

| # | Question | Nature | Impact |
|---|---|---|---|
| Q1 | **How are parameterized variable-geometry structures organized into a reusable library?** | The library specification: should it be a parameter database, a code library, or a file format? | Determines how structures are generated and shared. |
| Q2 | **What is the feature library schema?** | For each feature type: which parameters are stored, validation rules, versioning scheme. | Needed for maintaining the library across project phases. |
| Q3 | **How should the geometry generator accept a layout and produce variable-geometry height fields?** | The integration between the GDSII input → process model → variability engine. | Defines the end-to-end workflow. |
| Q4 | **Should the library include pre-generated height fields for common test structures?** | Performance tradeoff: generate on demand or pre-compute? | Affects startup time and reuse. |
| Q5 | **How are multi-layer structures referenced and combined?** | Layer stack definition coupled with overlay variation between layers. | Needed for multi-layer SEM simulation. |
| Q6 | **What is the naming and versioning convention for library structures?** | Structure naming, parameter versioning, backward compatibility. | Needed for traceability. |

---

## 3. Questions Deferred (Beyond Phase 3.x)

| # | Question | Reason for Deferral |
|---|---|---|
| D1 | Should LER be applied to contact holes (radial roughness)? | Implementation decision — contact LER is different from line LER |
| D2 | Should the LER model include high-frequency "sidewall roughness" (≈1 nm spatial period)? | Below CD-SEM resolution limit — can be ignored |
| D3 | Should parametric variation be sampled from wafer fab SPC data? | Requires access to fab data — out of research scope |
| D4 | Should variation be correlated across layers (e.g., gate CD and fin CD)? | Phase D enhancement — first-order model assumes independence |
| D5 | Should feed-forward correction (intentional CD bias to compensate known variation) be modeled? | Too process-specific |

---

## 4. Summary of Unresolved Items

| Item | Critical for Phase A? | Resolution Path | Required By |
|---|---|---|---|
| LER generation implementation | **Yes** (essential variability) | Phase 3.3 model is complete — implement in geometry engine | Phase A |
| LWR generation (correlated edges) | **Yes** (essential variability) | Model defined — implement as derived from LER | Phase A |
| Sidewall angle variation | No (Phase C) | Model defined — no further research needed | Phase C |
| CDU field/wafer models | No (Phase C) | Model defined — no further research needed | Phase C |
| Overlay implementation | No (Phase C) | Model defined — no further research needed | Phase C |
| CMP dishing variation | No (Phase D) | Model defined — no further research needed | Phase D |
| Feature library specification | **Yes** | Phase 3.4 research | Phase A–B |
| Parameter correlation | No | Deferred to Phase D | Phase D |
| Contact hole LER | No | Implementation decision | Phase C |

---

## Sources

- [M1] Habermas et al., "LER and LWR metrology," *Proc. SPIE*, vol. 10583, 2018.
- [M3] C. A. Mack, "Line edge roughness," *J. Micro/Nanolith. MEMS MOEMS*, vol. 8, 2009.
- Phase 3.2 — Canonical process model.
- Phase 3.3 Documents 02–07 — Variability models.
