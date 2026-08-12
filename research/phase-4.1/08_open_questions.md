# Open Questions

**Research Phase:** 4.1
**Document:** 08_open_questions.md
**Date:** 2026-07-30

---

## 1. Questions Answered Within Phase 4.1

| Question | Answer | Document |
|---|---|---|
| What architectural style? | Pipeline (sequential, immutable data) | 02 |
| How many layers? | 6 (Presentation → Config → Orchestration → Core → Foundation → External) | 05 |
| How many modules? | 10 (3 geometry, 3 physics, 2 dataset, 2 orchestration) | 03 |
| How do modules communicate? | Direct function calls via orchestrator | 07 |
| What data model? | Immutable data structures at interfaces | 04 |
| Repository topology? | Monorepo | 06 |
| Repository directory layout? | `src/`, `config/`, `tests/`, `docs/`, `outputs/`, etc. | 06 |
| Testing strategy? | Unit + Integration + Regression | 05 |

---

## 2. Questions for Phase 4.2 (API and Interface Design)

| # | Question | Nature | Impact |
|---|---|---|---|
| Q1 | **What are the precise function signatures for each module's public entry points?** | Core of Phase 4.2. Each module's exported functions need full signature specification — parameter names, types, defaults, return types. | Determines how modules are called by the orchestrator. |
| Q2 | **What is the configuration schema?** | The exact YAML/TOML schema for all configuration — keys, types, defaults, validation rules, structural constraints. | Determines how users configure the system. |
| Q3 | **What is the dataset metadata schema?** | Image naming convention, folder layout, ground-truth file format, metadata fields, index file structure. | Determines the output format consumed by downstream tools. |
| Q4 | **What are the precise I1–I4 data structure definitions?** | Field names, types, units, physical ranges, validation rules for every data structure crossing a module boundary. | Determines module contracts. |
| Q5 | **What is the structure library format?** | The exact YAML schema for defining structure types in `config/library/`. | Determines how users define new structures. |
| Q6 | **What error codes and error messages should modules produce?** | Error taxonomy, error message format, recovery suggestions. | Determines how failures are reported to users. |
| Q7 | **How should parallel batch execution be configured?** | Job-level configuration — array of parameter sets, repetition counts, seed assignment strategy. | Determines the user interface for dataset generation. |

---

## 3. Questions Deferred (Implementation)

| # | Question | Reason for Deferral |
|---|---|---|
| D1 | Which specific Python version? | Implementation decision — Python 3.10+ recommended |
| D2 | Which specific GDSII library? | Implementation decision — `gdspy` or `python-gdsii` or custom |
| D3 | Which specific image library? | Implementation decision — `tifffile` or `PIL` or `OpenCV` |
| D4 | Should we use `dask` or `ray` for parallel batch execution? | Implementation decision — depends on scale |
| D5 | Should we provide Docker containers? | Deployment decision — not architecture |
| D6 | How to handle version pinning of dependencies? | DevOps decision — not architecture |

---

## 4. Summary of Unresolved Items

| Item | Critical for Phase A? | Resolution Path | Required By |
|---|---|---|---|
| Module API signatures | **Yes** | Phase 4.2 | Phase A |
| Configuration schema | **Yes** | Phase 4.2 | Phase A |
| Dataset metadata schema | **Yes** | Phase 4.2 | Phase A |
| I1–I4 data structures | **Yes** | Phase 4.2 | Phase A |
| Structure library format | **Yes** | Phase 4.2 | Phase A |
| Error handling specification | **Recommended** | Phase 4.2 | Phase B |
| Parallel execution spec | **No** | Phase 4.2 | Phase C |
| LER generation implementation | **Yes** | Phase A implementation | Phase A |

---

## Sources

- [S1] L. Bass et al., *Software Architecture in Practice*, Addison-Wesley, 2021.
- Phase 3.4 — Geometry Engine specification.
- Phase 2.6 — SEM Physics Engine specification.
- Phase 4.1 — System architecture (this phase).
