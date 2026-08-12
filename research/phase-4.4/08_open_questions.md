# Open Questions

**Research Phase:** 4.4
**Document:** 08_open_questions.md
**Date:** 2026-07-30

---

## 1. Questions Answered Within Phase 4.4

| Question | Answer | Document |
|---|---|---|
| How should datasets be organized? | `images/`, `ground_truth/`, `metadata/`, `splits/` directories + `dataset_index.json` manifest | 02 |
| What artifact files are produced per sample? | 7 artifacts (4 required, 2 recommended, 1 optional) | 03 |
| What does ground truth contain? | Edge maps, CD values, material segmentation, contour lines, edge types | 04 |
| What metadata is recorded per sample? | 7 categories (Structure, Process, Variability, Physics, Seeds, Version, Provenance) | 05 |
| How is dataset integrity verified? | 5 validation levels (completeness, consistency, GT, version, reproducibility) | 06 |
| How are datasets distributed? | `.tar.gz` of canonical tree + SHA256SUMS + CC BY 4.0 license | 06 |

---

## 2. Questions for Phase 4.5 (Final Integration Audit)

| # | Question | Nature | Impact |
|---|---|---|---|
| Q1 | **Is the complete system specification consistent across all 16 phases?** | Cross-phase consistency — do decisions made in Phase 1 contradict decisions in Phase 4.4? | Determines if the system is ready for implementation. |
| Q2 | **Are all interfaces I1–I8 fully specified with no gaps?** | Interface completeness — are there any underspecified data fields, missing preconditions, or unhandled error conditions? | Determines if implementation can proceed. |
| Q3 | **Are the physics models scientifically sound for the intended use cases?** | Scientific correctness — are the SE/BSE yield models, PSF models, and noise models appropriate for CD-SEM simulation? | Determines if the simulator produces realistic images. |
| Q4 | **Are the geometry models sufficient for the intended structure library?** | Geometry completeness — do the process model and variability model cover all 10 structure types? | Determines if the simulator can generate all specified structures. |
| Q5 | **Is the computational cost within acceptable bounds for proposed deployment?** | Implementation feasibility — estimated wall time, memory, disk for a 10,000-image dataset on a typical workstation. | Determines if the system is practical. |
| Q6 | **Are all dependencies available (open-source or otherwise) for implementation?** | Dependency feasibility — are the required libraries (GDSII parser, image I/O, convolution, etc.) available? | Determines if implementation can start immediately. |
| Q7 | **Is the FAIR compliance of the dataset specification adequate?** | Findable, Accessible, Interoperable, Reusable — does the dataset spec meet FAIR principles? | Determines long-term dataset value. |

---

## 3. Questions Deferred (Implementation)

| # | Question | Reason for Deferral |
|---|---|---|
| D1 | Which specific GDSII library (gdspy, python-gdsii, custom)? | Implementation decision |
| D2 | Which specific TIFF library (tifffile, PIL, OpenCV)? | Implementation decision |
| D3 | What is the exact command-line interface? | Implementation decision |
| D4 | Should JSON files be compact or pretty-printed? | Implementation choice (compact recommended for storage) |
| D5 | Should height fields be compressed (npz) or uncompressed (npy)? | Implementation trade-off (npz recommended) |

---

## 4. Outstanding Risk Items

| Risk | Likelihood | Impact | Notes |
|---|---|---|---|
| JSON file size for large datasets | Low | Low | Even full ground truth is < 50 KB per sample |
| TIFF compatibility with all downstream tools | Low | Moderate | TIFF is well-supported but some machine learning frameworks have limited 16-bit support |
| License compatibility with downstream projects | Low | Low | CC BY 4.0 is permissive and well-understood |

---

## Sources

- Phase 4.1, Document 08 — Open questions from architecture phase.
- Phase 4.2, Document 08 — Open questions from interface phase.
- Phase 4.3, Document 08 — Open questions from runtime phase.
- Phase 4.4 — This document.
