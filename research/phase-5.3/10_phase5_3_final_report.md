# Phase 5.3 Final Report: SEM Physics Engine Implementation Blueprint

**SEMICON 2026 Research Repository**
**Applied Materials**
**Date:** 2026-07-30
**Classification:** Implementation-Planning

---

## Executive Summary

Phase 5.3 answers: **"How should the SEM Physics Engine be implemented from the first line of code to a fully validated module?"**

The certified SEM Physics Engine (Phase 2.6) is translated into a complete, frozen implementation blueprint: 9 internal modules across 3 public modules, 10 algorithm mappings (P1–P10) tied to certified physics specifications, a versioned material property library, a canonical source tree, an 8-step risk-driven development sequence, 6 test tiers, and a fully specified toolchain.

---

## 1. Key Results

### 1.1 Module Breakdown (Document 02)

| Public Module | Interface | Internal Modules |
|---|---|---|
| `phys_signal` | I4 | yield_computer, topography_engine, edge_effects, charging_engine, signal_assembler |
| `phys_degrade` | I5 | psf_generator, blur_applier, shot_noise, detector_noise, degrade_assembler |
| `phys_formation` | I6 | image_former |
| `_shared` | — | material_properties, physics_utils |

### 1.2 Library Selection (Document 03)

| Library | Role | Alternatives Considered |
|---|---|---|
| **NumPy** | Array core, PCG64 RNG | — |
| **SciPy** | fftconvolve, ndimage | PyFFTW (rejected), OpenCV (rejected) |
| **scikit-image** | PSF sizing, masks | OpenCV |
| **Pillow / PyYAML** | I/O, material library | tifffile, TOML |
| **cProfile / line_profiler** | Profiling | py-spy |

### 1.3 Algorithm Mapping (Document 04)

| # | Algorithm | Frozen Spec | Complexity |
|---|---|---|---|
| P1 | Surface normals / cosθ | Phase 2.3 | O(M·N) |
| P2 | Universal SE yield | Phase 2.2 | O(M·N) |
| P3 | Everhart BSE yield | Phase 2.2 | O(1) precomp |
| P4 | SE2 (BSE-induced) | Phase 2.3 | O(M·N) |
| P5 | Edge brightening | Phase 2.3 | O(M·N) |
| P6 | Charging modulation | Phase 2.4 | O(M·N) |
| P7 | PSF gen + FFT convolution | Phase 2.4 | O(MN log MN) |
| P8 | Poisson shot noise | Phase 2.4 | O(M·N) |
| P9 | Gaussian detector noise | Phase 2.4 | O(M·N) |
| P10 | Digitization | Phase 2.5 | O(M·N) |

### 1.4 Material Property Library (Document 05)

| ID | Material | δ₀ | Λ (nm) | η (Everhart) | E_b (keV) |
|---|---|---|---|---|---|
| 0 | Vacuum | 0.0 | 0.0 | 0.0 | 0 |
| 1 | Si | 0.15 | 2.5 | 0.215 | 0.0018 |
| 2 | SiO₂ | 0.16 | 2.8 | 0.180 | 0.0040 |
| 3 | Si₃N₄ | 0.15 | 2.6 | 0.175 | 0.0035 |
| 4 | Cu | 0.12 | 1.8 | 0.310 | 0.0011 |
| 5 | W | 0.10 | 1.5 | 0.500 | 0.0010 |
| 6 | PR | 0.20 | 4.0 | 0.070 | 0.0060 |

### 1.5 Development Sequence (Document 07)

| Step | Week | Deliverable | Gate |
|---|---|---|---|
| 1 | 0–0.5 | Toolchain + material library | Material tests |
| 2 | 0.5–1 | physics_utils | Utility tests |
| 3 | 1–2 | yield_computer + topography | Yield tests |
| 4 | 2–3.5 | edge effects + charging | **I4 verified** |
| 5 | 3.5–4.5 | PSF + blur | PSF tests |
| 6 | 4.5–5.5 | noise models | **I5 verified** |
| 7 | 5.5–6 | image_former | **I6 verified** |
| 8 | 6–7 | validation suite | **L1–L4 pass** |

---

## 2. Frozen Scientific Tolerances

| Metric | Target |
|---|---|
| Si δ(1 keV) | ∈ [0.4, 0.8] |
| Si η(1 keV) | ∈ [0.15, 0.25] |
| Material contrast | Cu SE < Si SE; W BSE > Cu BSE > Si BSE |
| Edge brightening ratio | factor ± 0.5% |
| PSF FWHM | configured ± 1% |
| Shot noise | mean ± 1%; var ≈ mean ± 5% |
| Detector noise | σ ± 2% |
| Determinism | bitwise (SHA-256) |

---

## 3. Engineering Decisions Frozen (20)

| ID | Decision | Document |
|---|---|---|
| PD1–PD20 | Module hierarchy, library stack, algorithms P1–P10, PSF sum-1, PCG64 RNG, material library design, 8-step sequence, 6 test tiers, toolchain | 02–07, 08 |

---

## 4. Physics Engine Implementable Without Revisiting Research

**Certification:** An engineering team can implement `phys_signal`, `phys_degrade`, and `phys_formation` from Phase 5.3 alone because:

1. Every algorithm maps to a certified physics specification.
2. Every library choice has a justified alternative.
3. Material properties are frozen, versioned, and literature-validated.
4. The 8-step sequence is risk-driven (I4 boundary first).
5. Scientific tolerances are numerically pinned.

---

## 5. Knowledge Required for Phase 5.4

Phase 5.4 must answer: **"How should the Geometry Engine and SEM Physics Engine be integrated into a complete simulator, the dataset generation pipeline established, and end-to-end validation executed?"**

| Question | Why It Matters |
|---|---|
| 1. **Orchestration integration** — how do orch_pipeline and orch_job wire M1–M8 (geometry + physics + dataset) together with data-object handoff at each I-interface? | Completes the runnable simulator |
| 2. **Config → CLI flow** — how does the YAML config (structure, process, variability, physics, degradation, detector, dataset sections) flow through config_parser into module calls? | Operational usability |
| 3. **Dataset pipeline** — how do data_writer, data_groundtruth, dataset_index, and splits assemble the Phase 4.4 canonical dataset? | Dataset production |
| 4. **End-to-end validation** — what is the full-pipeline regression (config → SEMImage → dataset), and how is it automated (self-check mode)? | Quality certification |
| 5. **Performance budget** — how are the Phase 5.1 per-image targets (< 3 s at 1024×1024) met and measured across the integrated pipeline? | Feasibility verification |
| 6. **Batch execution** — how do parallel workers, checkpointing, and caching operate at the dataset scale (Phase 4.3 RD decisions)? | Production throughput |
| 7. **Integration testing strategy** — which fixtures, golden outputs, and determinism tests span the complete simulator? | Release gate |

**Phase 5.4 begins where Phase 5.3 ends: at the I6 boundary, producing the first complete synthetic SEM image end-to-end.**

---

## 6. Document Map

```
research/phase-5.3/
│
├── 01_executive_summary.md              ← Blueprint overview
├── 02_physics_module_breakdown.md       ← 9 internal modules
├── 03_library_and_dependency_selection.md ← NumPy/SciPy/PCG64 stack
├── 04_algorithm_mapping.md              ← P1–P10 algorithm specifications
├── 05_material_property_library.md      ← Versioned material records
├── 06_repository_structure.md           ← Source tree, public/private API
├── 07_development_sequence_and_testing.md ← 8 steps + 6 test tiers
├── 08_engineering_conclusions.md       ← 20 frozen decisions (PD1–PD20)
├── 09_complete_reference_list.md        ← 11 references
└── 10_phase5_3_final_report.md          ← This consolidated report
```

---

## 7. Cumulative Repository Status

| Metric | Count |
|---|---|
| Research phases | **20** (Phase 1 – Phase 5.3) |
| Total documents | **190** |
| Geometry Engine blueprint | ✅ Complete (Phase 5.2) |
| Physics Engine blueprint | ✅ **Complete — frozen (this phase)** |
| Next phase | **5.4: Simulator Integration & Dataset Pipeline** |

---

*End of Phase 5.3 Final Report — SEM Physics Engine Implementation Blueprint*
