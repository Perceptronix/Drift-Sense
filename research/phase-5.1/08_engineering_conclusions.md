# Engineering Conclusions

**Research Phase:** 5.1
**Document:** 08_engineering_conclusions.md
**Date:** 2026-07-30

---

## 1. Frozen Implementation Decisions

| ID | Decision | Value | Justification |
|---|---|---|---|
| **ID1** | Programming language | Python 3.11+ | Scientific computing standard; NumPy/SciPy ecosystem; research-to-production fluency |
| **ID2** | Build system | setuptools + pyproject.toml | PEP 517/518 compliant; industry standard |
| **ID3** | Testing framework | pytest 7+ + pytest-cov | Industry standard; fixture model |
| **ID4** | Version control | Git + GitHub/GitLab | Standard |
| **ID5** | Branching model | Git Flow (feature/ → develop → main) | Stable main; integration in develop |
| **ID6** | Code quality | black + ruff + mypy --strict | Consistent formatting; type safety |
| **ID7** | Documentation | Sphinx + autodoc (NumPy docstrings) | Auto-generated from source |
| **ID8** | CI/CD | GitHub Actions | Standard; integrated with PR workflow |
| **ID9** | Repository structure | src/ layout — one package per layer | Separation of concerns |
| **ID10** | Implementation order | Risk-driven: high-risk modules first | Early validation; late integration |
| **ID11** | Validation gates | L0–L5 (unit → acceptance) | Incremental quality |
| **ID12** | Versioning | SemVer (major.minor.patch) | Industry standard |
| **ID13** | Dependency pinning | Minor version for core; exact for dev | Reproducible builds |
| **ID14** | Team structure | 4 teams (A: Found., B: Geom., C: Phys., D: Integ.) | Maximizes parallelism |

---

## 2. Frozen Implementation Order

| Priority | Work Package | Week | Team | Gate |
|---|---|---|---|---|
| **1** | Foundation utilities (0.2–0.6) | 1–3 | A | L0 |
| **2** | Config parser (2.2) | 3–5 | A | L1 |
| **3** | geo_raster (1.1) | 3–6 | B | L1 |
| **4** | geo_process (1.2) | 6–10 | B | L1 |
| **5** | geo_variability (1.3) | 10–13 | B | L1 |
| **6** | phys_signal (1.4) | 13–17 | C | L1 |
| **7** | phys_degrade (1.5) | 17–19 | C | L1 |
| **8** | phys_formation (1.6) | 19–20 | C | L1 |
| **9** | data_writer (1.7) | 13–15 | D | L1 |
| **10** | data_groundtruth (2.1) | 13–16 | B | L1 |
| **11** | orch_pipeline (1.8) | 20–22 | D | L3 |
| **12** | orch_job (2.3) | 22–25 | D | L3 |
| **13** | CLI (2.4) | 25–27 | D | L3 |
| **14** | Validation L1–L3 (2.5) | 25–28 | D | L3 |
| **15** | Self-check (2.6) | 27–28 | D | L3 |
| **16** | Caching (3.1) | 22–25 | B | L1 |
| **17** | Parallel (3.2) | 25–28 | D | L5 |
| **18** | Checkpoint (3.3) | 28–30 | D | L5 |
| **19** | Regression L4–L5 (3.4) | 28–30 | D | L5 |
| **20** | Docs (3.5) | 30–33 | All | L5 |
| **21** | Distribution (3.6) | 30–32 | A | L5 |
| **22** | Profiling (3.7) | 30–32 | All | L5 |

---

## 3. Milestone Structure

| Milestone | Week | Gate | Dependencies |
|---|---|---|---|
| **M0: Foundation** | 3 | L0 | None |
| **M1: Geometry** | 13 | L0–L2 | M0 |
| **M2: Physics** | 20 | L0–L2 | M1 (I4) |
| **M3: Single-Image** | 22 | L3 | M2 |
| **M4: Ground Truth** | 16 | L4 | M1 (I7) |
| **M5: Batch** | 28 | L3–L4 | M3, M4 |
| **M6: Production** | 30 | L1–L4 | M5 |
| **M7: Final Release** | 36 | L5 | M6 |

---

## 4. Validation Gate Map

| Gate | When | What | Who |
|---|---|---|---|
| **L0: Unit** | Every PR | Per-function tests | Developer |
| **L1: Module** | Module merge | Interface contract | Module lead |
| **L2: Interface** | Milestone | Paired module contract | Module leads |
| **L3: Pipeline** | M3, M5 | End-to-end | Integration lead |
| **L4: Scientific** | M4, M5 | CD accuracy, physics | Scientific lead |
| **L5: Acceptance** | M7 | Full system | Program manager |

---

## 5. Development Flow

```
Week 1  3    6    10   13   17   20   22   28   30   36
        │    │    │    │    │    │    │    │    │    │
Team A: Found.  Config Parser                Dist Doc
        ████████░░░░░░████░░░░░░░░░░░░░░░░░███████

Team B:   geo_raster  geo_proc  geo_var  GT  Cache
          ░░██████████████████████████████████░░

Team C:                      phys_sig  deg form
                              ░░░████████████░░░

Team D:                         wrtr orch_pipe  orch_job  CLI  Val  Par  Chk
                                 ░░░███████████████████████████████████████

Milestones:
         M0   └────────────────┘ M1          M2  M3     M4   M5     M6  M7
```

---

## Sources

- Phase 4.5, Document 08 — Final certification.
- Phase 4.2, Document 02 — Module interface inventory.
- [I10] A. Oram, G. Wilson, *Making Software*, O'Reilly, 2010.
- [I11] V. Driessen, "A Successful Git Branching Model," 2010.
- [I12] ISO/IEC 15939, "Software Measurement Process," 2007.
- [I13] R. E. Park et al., "Goal/Question/Metric Paradigm," CMU/SEI, 1994.
