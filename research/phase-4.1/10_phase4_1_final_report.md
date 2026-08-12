# Phase 4.1 Final Report: System Integration Architecture

**SEMICON 2026 Research Repository**
**Applied Materials**
**Date:** 2026-07-30
**Classification:** Research-Only (Phase 4.1)

---

## Executive Summary

Phase 4.1 answers the engineering question: **"How should the Geometry Engine and SEM Physics Engine be integrated into one modular synthetic SEM image generation system?"**

The complete system architecture is designed: 6 layers, 10 modules, 4 internal interfaces, pipeline-based execution with immutable data passing, organized in a monorepo with 8 top-level directories.

---

## 1. Architecture Decisions

| # | Decision | Value | Rationale |
|---|---|---|---|
| AD1 | Architecture style | **Pipeline** (sequential, immutable data) | Matches linear geometry→physics→dataset flow |
| AD2 | Layer count | **6** | Clear separation of concerns |
| AD3 | Module count | **10** | Single Responsibility Principle |
| AD4 | Communication | **Direct function calls** | Simplest for linear pipeline; no branches |
| AD5 | Data model | **Immutable data at interfaces** | Enables reproducibility, testing, parallel execution |
| AD6 | Repository | **Monorepo** | Single source of truth |
| AD7 | Configuration | **External YAML/TOML** | Code is parameter-free |
| AD8 | Execution | **Deterministic (seeded RNG)** | Same seed → same output |
| AD9 | Engine coupling | **Independent via I4** | Test separately, use separately |
| AD10 | Testing | **Unit + Integration + Regression** | Multi-level validation |

---

## 2. Layer Architecture

| Layer | Modules | Responsibility |
|---|---|---|
| **L6: Presentation** | CLI, Python API | User-facing interface |
| **L5: Configuration** | Parser, Validator | Config file → Config object |
| **L4: Orchestration** | Pipeline Controller, Job Manager | Stage sequencing, batch execution |
| **L3: Core Engines** | Geometry Engine (3 mods), Physics Engine (3 mods) | Actual computation |
| **L2: Foundation** | Math, I/O, RNG, Units | Shared utilities |
| **L1: External** | Python, NumPy, SciPy, ... | Runtime + dependencies |

---

## 3. Module Decomposition

| Subsystem | Module | Input | Output |
|---|---|---|---|
| **Geometry** | GDSII Rasterizer | GDSII file, layer | PixelMask |
| **Geometry** | Process Model | PixelMask, params | HeightField_det, MaterialMap_det |
| **Geometry** | Variability Engine | HeightField_det, var params | HeightField_var, MaterialMap_var |
| **Physics** | Signal Generation | HeightField_var, MaterialMap_var | YieldMap_SE, YieldMap_BSE |
| **Physics** | Degradation Model | YieldMaps, noise params | YieldMap_SE_degraded |
| **Physics** | Image Formation | YieldMap, detector params | SEMImage |
| **Dataset** | Dataset Writer | SEMImage, metadata | Files on disk |
| **Dataset** | Ground Truth | HeightField, MaterialMap | Labels, CD values |
| **Orchestration** | Pipeline Controller | Config → all modules | Completed dataset entry |
| **Orchestration** | Job Manager | Batch config | Completed dataset |

---

## 4. Data Flow

```
Config → [StructureSpec] → [PixelMask] → [HeightField_det + MatMap_det]
  → [HeightField_var + MatMap_var] → [YieldMap_SE + YieldMap_BSE]
  → [YieldMap_SE_degraded] → [SEMImage] → [Files on disk]
```

All data is **immutable** — each stage produces new data and never modifies what it received.

---

## 5. Repository Structure

```
semicon-sim/
├── src/geometry/{raster, process, variability}/
├── src/physics/{signal, degrade, formation}/
├── src/dataset/{writer, groundtruth}/
├── src/orchestration/{pipeline, job}/
├── src/foundation/{math, image_io, rng, units}/
├── config/{library, materials, defaults}/
├── tests/{unit, integration, regression}/
├── docs/{architecture, api, tutorials}/
├── scripts/
├── outputs/                 (git-ignored)
├── research/                (completed phases)
├── pyproject.toml
└── README.md
```

---

## 6. Phase 4.1 Success Criteria

| Criterion | Status | Evidence |
|---|---|---|
| ✓ Complete end-to-end system architecture | **Achieved** | 6-layer pipeline defined (Document 02) |
| ✓ Every major software module | **Achieved** | 10 modules with full spec (Document 03) |
| ✓ Module responsibilities | **Achieved** | Purpose, I/O, dependencies defined per module |
| ✓ Layered architecture | **Achieved** | 6 layers, strict dependency rules (Document 05) |
| ✓ Repository organization | **Achieved** | Monorepo, 8 top-level directories (Document 06) |
| ✓ Data flow | **Achieved** | Immutable data pipeline with 10 stages (Document 04) |
| ✓ Frozen architecture | **Achieved** | 10 architecture decisions frozen (Document 07) |

---

## 7. Knowledge Required for Phase 4.2

Phase 4.1 establishes **how the system is organized**. Phase 4.2 must define **how the modules communicate at the API level**:

1. **Precise module API signatures:** Function names, parameter names, parameter types, return types for every public function in every module.

2. **Configuration schema:** The exact YAML/TOML schema — all keys, types, defaults, validation rules, structural constraints.

3. **Dataset metadata schema:** Image naming, folder layout, ground-truth encoding, metadata fields, index file format.

4. **Data structure definitions (I1–I4):** Field names, types, units, physical ranges, validation rules for every data structure crossing a module boundary.

5. **Structure library format:** The YAML schema for defining new structure types.

**Phase 4.2 transitions from architecture (how the system is organized) to interface contracts (how the modules connect). After Phase 4.2, implementation can begin.**

---

## 8. Phase 4.1 Document Map

```
research/phase-4.1/
│
├── 01_executive_summary.md              ← Architecture overview, frozen decisions
├── 02_system_architecture_overview.md   ← Complete workflow, architecture style
├── 03_module_decomposition.md          ← 10 modules: spec, I/O, dependencies
├── 04_data_flow_architecture.md        ← Immutable data pipeline, 10 stages
├── 05_layered_architecture.md          ← 6 layers, dependency rules, testing
├── 06_repository_organization.md       ← Monorepo, 8 top-level directories
├── 07_engineering_conclusions.md       ← 10 frozen architecture decisions
├── 08_open_questions.md               ← 7 questions for Phase 4.2
├── 09_complete_reference_list.md        ← 14 architecture references
└── 10_phase4_1_final_report.md          ← This consolidated report
```

---

*End of Phase 4.1 Final Report — System Integration Architecture*
