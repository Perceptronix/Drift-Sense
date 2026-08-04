# Open Questions

**Research Phase:** 4.2
**Document:** 08_open_questions.md
**Date:** 2026-07-30

---

## 1. Questions Answered Within Phase 4.2

| Question | Answer | Document |
|---|---|---|
| What data crosses each module boundary? | 10 data objects defined: Config, GDSIIRef, PixelMask, LayerStack, HeightField, MaterialMap, YieldMaps, SEMImage, GroundTruth, Metadata | 03 |
| What are the exact pre/post conditions? | 8 interfaces with 31 preconditions and 35 postconditions defined | 04 |
| How is configuration structured? | 6 sections (Version, Global, Structure, Geometry, Physics, Dataset) with hierarchical inheritance | 05 |
| How are errors handled? | 6 categories (Configuration, Input, Domain, Runtime, Validation, Recoverable) with severity and handling | 07 |
| How is interface compliance verified? | 5 validation levels (Schema, Range, Consistency, Unit, Regression) | 06 |

---

## 2. Questions for Phase 4.3 (Runtime and Execution)

| # | Question | Nature | Impact |
|---|---|---|---|
| Q1 | **How should pipeline stages be scheduled and monitored?** | Execution orchestration: should the pipeline controller be sequential (simple) or support caching/recovery? | Determines runtime control flow. |
| Q2 | **Should intermediate results be cached?** | Reproducibility / performance trade-off: deterministic stages can be cached. But caching adds complexity. | Affects performance for repeated parameter sweeps. |
| Q3 | **How should batch jobs handle partial failures?** | Error recovery: skip failed structure and continue, or abort entire batch? How are results aggregated? | Affects dataset generation reliability. |
| Q4 | **How is full reproducibility maintained across runs?** | Seed management, config recording, version pinning, dependency tracking. | Critical for scientific reproducibility. |
| Q5 | **How should parallel batch execution work?** | Process pool? Distributed? GPU vs. CPU scheduling? | Affects large-dataset generation performance. |
| Q6 | **What is the checkpoint/restart strategy for long-running jobs?** | Generation of >10⁵ images may take hours. Checkpoints enable restart. | Affects batch job reliability. |
| Q7 | **What logging and progress reporting is needed?** | Per-image progress, timing statistics, remaining time estimation. | Affects user experience. |
| Q8 | **How are built-in tests / self-checks organized?** | A test mode that runs a minimal pipeline to verify system integrity. | Affects deployment reliability. |

---

## 3. Questions Deferred (Implementation)

| # | Question | Reason for Deferral |
|---|---|---|
| D1 | Which specific YAML/TOML library? | Implementation decision |
| D2 | Which specific image I/O library? | Implementation decision |
| D3 | Which parallel execution library (multiprocessing, Ray, Dask)? | Implementation decision |
| D4 | What is the exact command-line interface? | Implementation decision |
| D5 | Should we use strict typing (dataclasses, pydantic)? | Implementation decision |
| D6 | What is the logging library and format? | Implementation decision |

---

## 4. Summary of Unresolved Items

| Item | Critical for Phase A? | Resolution Path | Required By |
|---|---|---|---|
| Execution scheduling | Yes | Phase 4.3 | Phase A |
| Caching strategy | No (Phase B enhancement) | Phase 4.3 | Phase C |
| Partial failure handling | Yes | Phase 4.3 | Phase A |
| Reproducibility workflow | Yes | Phase 4.3 | Phase A |
| Parallel execution | No (Phase C) | Phase 4.3 | Phase C |
| Checkpoint/restart | No (Phase D) | Phase 4.3 | Phase D |
| Progress reporting | Yes | Phase 4.3 | Phase A |
| Self-check/test mode | Yes | Phase 4.3 | Phase A |

---

## Sources

- Phase 4.1, Document 08 — Open questions from architecture phase.
- Phase 4.2 — This document.
- [I1] C. Larman, *Applying UML and Patterns*, Prentice Hall, 2004.
- [I2] B. Meyer, *Object-Oriented Software Construction*, Prentice Hall, 1997.
