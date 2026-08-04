# Complete Reference List — Phase 5.4

**Research Phase:** 5.4
**Document:** 09_complete_reference_list.md
**Date:** 2026-07-30

---

## A. Architecture & Integration Patterns

| Ref | Author(s) | Title | Publisher | Year | Cited In |
|---|---|---|---|---|---|
| [S1] | M. Fowler | *Patterns of Enterprise Application Architecture* | Addison-Wesley | 2002 | 01, 02 |
| [S2] | G. Hohpe, B. Woolf | *Enterprise Integration Patterns* | Addison-Wesley | 2003 | 01 |
| [S3] | B. Burns | *Designing Distributed Systems* | O'Reilly | 2018 | 03 |
| [S4] | J. Kleppmann | *Designing Data-Intensive Applications* | O'Reilly | 2017 | 03, 04 |

---

## B. Performance & Parallelism

| Ref | Author(s) | Title | Publisher | Year | Cited In |
|---|---|---|---|---|---|
| [S7] | G. Amdahl | "Validity of the single processor approach to achieving large scale computing capabilities" | AFIPS Conf. Proc., vol. 30 | 1967 | 06 |
| [S8] | J. L. Hennessy, D. A. Patterson | *Computer Architecture: A Quantitative Approach*, 6th ed. | Morgan Kaufmann | 2017 | 06 |

---

## C. Testing & FAIR

| Ref | Author(s) | Title | Publisher | Year | Cited In |
|---|---|---|---|---|---|
| [G9] | J. B. Rainsberger | *JUnit Recipes* | Manning | 2004 | 05 |
| [S6] | M. Utting, B. Legeard | *Practical Model-Based Testing* | Morgan Kaufmann | 2007 | 05 |
| [S5] | M. D. Wilkinson et al. | "The FAIR Guiding Principles for scientific data management and stewardship" | *Scientific Data*, vol. 3 | 2016 | 04, 07 |
| [S9] | J. Deng et al. | "ImageNet: A Large-Scale Hierarchical Image Database" | CVPR | 2009 | 07 |

---

## D. Cross-Phase References

| Ref | Phase | Documents | Title | Cited In |
|---|---|---|---|---|
| [P4.1] | 4.1 | All | System Architecture (AD1–AD10) | 01, 02, 03 |
| [P4.2] | 4.2 | 03, 04 | Data Objects D1–D10; Interfaces I1–I8 | 01, 02, 05 |
| [P4.3] | 4.3 | All | Runtime Decisions RD1–RD13 | 02, 03, 04, 06 |
| [P4.4] | 4.4 | 02–07 | Dataset Specification | 01, 02, 04, 05, 07 |
| [P5.1] | 5.1 | All | Implementation Roadmap | 01, 03, 06, 07 |
| [P5.2] | 5.2 | All | Geometry Engine Blueprint | 02, 05 |
| [P5.3] | 5.3 | All | Physics Engine Blueprint | 02, 05 |

---

## E. Key Reference Summary

### Integration Patterns
- [S1] Fowler (2002) — Pipeline/controller patterns. Basis for master controller.
- [S3] Burns (2018) — Worker pools, checkpointing. Basis for orch_job.
- [S4] Kleppmann (2017) — Idempotency, journals. Basis for resume/checkpoint.

### Performance
- [S7] Amdahl (1967) — Parallel speedup law. Basis for scaling targets.
- [S8] Hennessy & Patterson (2017) — Quantitative architecture. Memory/runtime budgets.

### Dataset Governance
- [S5] Wilkinson et al. (2016) — FAIR principles.
- [S9] Deng et al. (2009) — Benchmark dataset governance.

---

*End of Reference List — Phase 5.4*
