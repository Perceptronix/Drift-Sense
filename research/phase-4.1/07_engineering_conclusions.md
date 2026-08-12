# Engineering Conclusions

**Research Phase:** 4.1
**Document:** 07_engineering_conclusions.md
**Date:** 2026-07-30

---

## 1. Frozen Architecture Decisions

| # | Decision | Value | Justification |
|---|---|---|---|
| AD1 | **Architectural style** | Pipeline (sequential stages, immutable data) | Matching the inherently sequential geometry→physics→dataset flow |
| AD2 | **Layer count** | 6 (Presentation, Configuration, Orchestration, Core Engines, Foundation, External) | Clear separation of concerns; each layer has one responsibility |
| AD3 | **Module count** | 10 (3 geometry, 3 physics, 2 dataset, 2 orchestration) | Single Responsibility Principle; each module does one thing |
| AD4 | **Communication model** | Direct function-call orchestration | Simplest possible; no RPC, no events, no message bus |
| AD5 | **Data model** | Immutable data structures passing between stages | Enables reproducibility, parallel execution, debugging |
| AD6 | **Repository topology** | Monorepo | Single source of truth; simple dependency management |
| AD7 | **Configuration strategy** | External YAML/TOML → parsed Config object | All parameters externalized; code is parameter-free |
| AD8 | **Execution model** | Deterministic per pipeline run (seeded RNG) | Same config + same seed → same output |
| AD9 | **Engine independence** | Geometry Engine and Physics Engine independent; connected via I4 | Either engine can be used or tested separately |
| AD10 | **Testing strategy** | Unit (per module) + Integration (cross-module) + Regression (image comparison) | Multi-level testing for scientific simulation |

---

## 2. Frozen Module Boundaries

| # | Boundary | Left Side | Right Side | Data Crossing |
|---|---|---|---|---|
| B1 | Design rule | `geo_raster` | `geo_process` | `PixelMask` (binary, M×N) |
| B2 | I2 | `geo_process` | `geo_variability` | `HeightField_det` + `MaterialMap_det` |
| B3 | I4 (I3→physics) | `geo_variability` | `phys_signal` | `HeightField_var` + `MaterialMap_var` |
| B4 | Physics internal | `phys_signal` | `phys_degrade` | `YieldMap_SE` + `YieldMap_BSE` |
| B5 | Physics internal | `phys_degrade` | `phys_formation` | `YieldMap_SE_degraded` |
| B6 | Dataset input | `phys_formation` | `data_writer` | `SEMImage` (M×N, uint) |
| B7 | Ground truth | `geo_variability` | `data_groundtruth` | `HeightField_var` + `MaterialMap_var` |

---

## 3. Frozen Architectural Principles

| Principle | Statement |
|---|---|
| **P1: Single Responsibility** | Every module does exactly one thing and knows nothing about other modules |
| **P2: Immutable Data** | No module modifies data received from another module |
| **P3: Stateless Modules** | Modules carry no mutable state between pipeline calls (except for RNG state, which is managed per seed) |
| **P4: Configuration-Driven** | All parameters are externalized. Code contains no hard-coded values |
| **P5: Fail Fast** | Input validation happens at module boundaries |
| **P6: Deterministic by Default** | Seeded RNG ensures reproducibility |
| **P7: Testable at All Levels** | Unit, integration, and regression tests are required for all modules |
| **P8: Independent Engines** | Geometry Engine and Physics Engine can be used separately and tested separately |

---

## 4. Repository Frozen Structure

| Path | Content | Frozen |
|---|---|---|
| `src/geometry/` | GE: raster, process, variability | ✅ |
| `src/physics/` | SEM PE: signal, degrade, formation | ✅ |
| `src/dataset/` | Dataset: writer, groundtruth | ✅ |
| `src/orchestration/` | Control: pipeline, job | ✅ |
| `src/foundation/` | Shared: math, image_io, rng, units | ✅ |
| `config/library/` | Structure definitions | ✅ |
| `config/materials/` | Material property tables | ✅ |
| `tests/{unit,integration,regression}/` | All tests | ✅ |
| `docs/architecture/` | ADRs | ✅ |
| `research/` | Completed research (/!\ Not for implementation) | ✅ |

---

## 5. Communication Model Justification

| Model | Considered | Reason for/against |
|---|---|---|
| **Direct function calls (selected)** | ✅ | Simple, fast, debuggable. The pipeline is linear — no need for events or messages |
| Event-driven (message bus) | ❌ | Adds complexity without benefit. Pipeline has no branches, events, or asynchronous triggers |
| Service-oriented (RPC) | ❌ | Overkill for single-process simulation. No distributed deployment requirement |
| Shared mutable objects | ❌ | Antithetical to reproducibility. Two modules mutating the same state is a bug |
| Publish-subscribe | ❌ | No module needs to react independently to another module's output |

**Inference:** The pipeline has one producer and one consumer per stage. No branching, no fan-out, no asynchronous triggers. Direct function calls are optimal.

---

## Sources

- [S1] L. Bass et al., *Software Architecture in Practice*, Addison-Wesley, 2021.
- [S2] E. Gamma et al., *Design Patterns*, Addison-Wesley, 1994.
- [S5] J. K. Ousterhout, *A Philosophy of Software Design*, Yaknyam Press, 2018.
- [S8] R. C. Martin, *Clean Architecture*, Prentice Hall, 2017.
- [S10] F. Buschmann et al., *POSA, Volume 1*, Wiley, 1996.
- Phase 3.4 — Geometry Engine specification.
- Phase 2.6 — SEM Physics Engine specification.
