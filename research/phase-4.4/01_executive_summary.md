# Phase 4.4 Executive Summary: Dataset Packaging & Output Specification

**SEMICON 2026 Research Repository**
**Applied Materials**
**Date:** 2026-07-30
**Classification:** Research-Only (Phase 4.4)

---

## Purpose

This phase answers: **"What should a complete synthetic SEM dataset contain, and how should it be packaged for downstream machine learning, benchmarking, and reproducible research?"**

Phases 4.1–4.3 defined **how the system executes**. This phase defines **what it produces** — the frozen specification for datasets, output artifacts, ground truth, metadata, validation, and distribution.

---

## Key Findings

### 1. Dataset Organization

| Aspect | Recommendation |
|---|---|
| **Directory hierarchy** | `dataset_name/images/`, `dataset_name/ground_truth/`, `dataset_name/metadata/` |
| **Naming convention** | `{structure_type}_{parameters_hash}_{seed_hash}.tiff` |
| **Dataset versioning** | Semver (major.minor.patch) applied to the complete dataset |
| **Splits** | Train / Validation / Test directories at dataset level |
| **Manifest** | One `dataset_index.json` with summary + per-sample entries |

### 2. Output Artifacts (Per Sample)

| Artifact | File | Format | Priority |
|---|---|---|---|
| SEM Image | `images/*.tiff` | 16-bit grayscale TIFF | **Required** |
| Ground Truth | `ground_truth/*.json` | JSON | **Required** |
| Height Field | `ground_truth/*.npy` | NumPy .npy | **Recommended** |
| Material Map | `ground_truth/*_material.png` | 16-bit PNG | **Recommended** |
| Yield Maps | `ground_truth/*_yields.npz` | NumPy .npz | **Optional** |
| Configuration Snapshot | `metadata/*_config.json` | JSON | **Required** |
| Metadata Record | `metadata/*_metadata.json` | JSON | **Required** |
| Cache Log | `metadata/*_timing.json` | JSON | **Optional** |

### 3. Ground Truth Content

| Component | Content | Precision |
|---|---|---|
| **Edge position maps** | Signed distance to nearest edge (nm) | 0.1 nm |
| **CD values** | Top CD, bottom CD, height per feature | 0.1 nm |
| **Material segmentation** | Per-pixel material ID | Material ID (uint8) |
| **Contour lines** | Edge coordinates in nm | 0.1 nm |
| **Edge type** | Top edge, bottom edge, boundary | Categorical |
| **Visibility** | Feature fully/partially visible | Boolean |

### 4. Metadata Content

| Category | Fields | Required |
|---|---|---|
| **Structure** | Type, dimensions, materials, layer stack | Yes |
| **Geometry process** | Sidewall angle, CD bias, corner radii | Yes |
| **Variability** | LER σ, ξ, ρ; overlay; CDU | Yes |
| **Physics** | Beam energy, probe current, PSF, noise | Yes |
| **Seeds** | Master → structure → image → stage chain | Yes |
| **Version** | Application, config schema, library hashes | Yes |
| **Provenance** | Timestamp, duration, platform | Yes |

### 5. Dataset Validation

| Check | Method |
|---|---|
| File completeness | Expected files present (vs manifest) |
| Metadata consistency | Cross-check parameter values across files |
| Ground truth consistency | Edges match height field; CDs match parameters |
| Version compatibility | All files from same dataset version |
| Reproducibility | Config + seed → same output hash |

---

## Phase 4.5 Knowledge Required

Phase 4.5 must answer **one question**: **"Is the complete simulator specification consistent, complete, and ready for implementation?"**

This is the final end-to-end integration audit, reviewing:
- Cross-phase consistency (Phases 1–4.4)
- Interface completeness (every I1–I8 contract)
- Scientific correctness (physics models, geometry models)
- Implementation feasibility (computational cost, dependency availability)

**After Phase 4.5, the project transitions from research to implementation.**

---

## Sources

- [D1] M. G. Creek et al., "Best Practices for Scientific Computing," *Nature Physics*, vol. 12, 2016.
- [D2] N. P. C. Marwick, "How to Make Reproducible Research a Reality," *Nature*, vol. 578, 2020.
- [D3] J. Lamprecht et al., "Towards FAIR Principles for Research Software," *Data Science*, vol. 3, 2020.
- Phase 4.2 — Canonical data objects.
- Phase 4.3 — Runtime execution.
