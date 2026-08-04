# Production Dataset Strategy

**Research Phase:** 5.4
**Document:** 07_production_dataset_strategy.md
**Date:** 2026-07-30

---

## 1. Dataset Portfolio

Five production datasets are defined:

| ID | Dataset | Purpose | Size | Structures |
|---|---|---|---|---|
| DS1 | **Development** | Development smoke tests, module debugging | 50 | 10 |
| DS2 | **Unit-test** | CI regression, golden-reference pinning | 100 | 10 |
| DS3 | **Validation** | Milestone gates, cross-module checks | 1,000 | 10 |
| DS4 | **Scientific-benchmark** | Physics/geometry accuracy benchmarking | 200 | 10 |
| DS5 | **Final-training** | Release deliverable for ML benchmarking | 100,000 | 10 |

---

## 2. DS1: Development Dataset (50)

| Aspect | Specification |
|---|---|
| **Purpose** | Fast iteration; exercise every structure + artifact path |
| **Size** | 50 images (5 per structure × 10 types) |
| **Structure distribution** | Uniform: 5 samples per structure type |
| **Material distribution** | Matches structure library defaults (Si substrate; SiO₂/NiN dielectrics; Cu/W metals; PR top) |
| **Parameter coverage** | Mid-range nominal values only |
| **Metadata** | Full (Phase 4.4) |
| **Ground truth** | Full |
| **Artifacts** | Core (image + GT + config + metadata) |
| **Versioning** | `dev_v1.0.0` |
| **Regeneration** | Any dev change; not version-pinned beyond dev |

---

## 3. DS2: Unit-Test Dataset (100)

| Aspect | Specification |
|---|---|
| **Purpose** | CI regression; golden-reference hashes committed to repo |
| **Size** | 100 (10 per structure) |
| **Structure distribution** | Uniform: 10 per type |
| **Parameter coverage** | Nominal + one edge-case parameter per structure |
| **Determinism** | Fixed master_seed; bitwise-pinned hashes in `tests/data/reference_hashes.json` |
| **Ground truth** | Full |
| **Artifacts** | Core; images kept small (512×512) for speed |
| **Versioning** | `unit_v2.3.0`-style, bumps on schema change |
| **Regeneration** | Reviewed golden regeneration procedure only |

---

## 4. DS3: Validation Dataset (1,000)

| Aspect | Specification |
|---|---|
| **Purpose** | Milestone gates (M3–M5); L1–L5 validation; cross-module consistency |
| **Size** | 1,000 |
| **Structure distribution** | Stratified: 100 per structure type |
| **Parameter coverage** | Full certified ranges (CD 10–500 nm, height 20–200 nm, pitch 20–1000 nm, LER 0–5 nm) stratified |
| **Metadata** | Full |
| **Ground truth** | Full |
| **Artifacts** | Core + optional height fields |
| **Image size** | 1024×1024 |
| **Versioning** | `val_v1.0.0` per release cycle |
| **Regeneration** | On every minor release; diff against previous via hashes |

---

## 5. DS4: Scientific-Benchmark Dataset (200)

| Aspect | Specification |
|---|---|
| **Purpose** | L4 scientific validation; physics accuracy; published-value cross-checks |
| **Size** | 200 (20 per structure) |
| **Structure distribution** | Uniform |
| **Material coverage** | Explicit multi-material structures: Si/SiO₂/SiN; Si/Cu; Si/W; PR-on-Si |
| **Parameter coverage** | Tuned calibration set (known analytic results) |
| **Metadata** | Full + `material_library_hash` + physics config |
| **Ground truth** | Full |
| **Artifacts** | Core + **yield maps** (SE/BSE) for physics benchmarking |
| **Benchmark metrics** | CD accuracy, LER stats, yield values, PSF width, noise statistics, edge brightening ratio |
| **Versioning** | `bench_v1.0.0` — frozen, audited |

---

## 6. DS5: Final-Training Dataset (100,000)

| Aspect | Specification |
|---|---|
| **Purpose** | Primary deliverable — ML/CD-SEM benchmarking dataset |
| **Size** | 100,000 |
| **Structure distribution** | **Application-weighted** (operational policy): dense_ls 20%, contact 15%, via 10%, iso_line 15%, fin 10%, gate 10%, trench 8%, sti 5%, bimaterial 4%, pitch_std 3% |
| **Material distribution** | Realistic process stacks (from Phase 1 structure library) |
| **Parameter coverage** | Full certified ranges; random sampling (sweep mode) |
| **Variability** | LER/CDU/overlay sampled across full ranges |
| **Image size** | 1024×1024 |
| **Metadata** | Full |
| **Ground truth** | Full (training requires labels) |
| **Artifacts** | Core |
| **Splits** | Train 70,000 / Val 15,000 / Test 15,000 (deterministic split, no overlap) |
| **Storage** | ~400 GB |
| **Versioning** | `train_v1.0.0` — frozen release |
| **Generation** | ~1 day at 4 workers |

---

## 7. Split Policy

| Split | DS3 | DS5 | Rule |
|---|---|---|---|
| Train | 700 | 70,000 | 70% |
| Validation | 150 | 15,000 | 15% |
| Test | 150 | 15,000 | 15% |
| **Stratification** | Per structure type | Per structure type | Balanced within split |
| **Leakage control** | Seed-derived split; no structure shared across splits | Same | Splits are disjoint sample sets |

**Frozen rule:** Split assignment is deterministic from `(dataset_name, sample_index)` — never random at split time; documented in README.

---

## 8. Dataset Generation Plan (Timeline)

| Week | Dataset | Gate |
|---|---|---|
| 14 (M3) | DS1 dev (50) | Pipeline works |
| 20 (M4/M5) | DS2 unit (100) | CI regression pinned |
| 24 (M5) | DS3 validation (1,000) | L1–L5 pass |
| 26 (M5) | DS4 benchmark (200) | L4 scientific pass |
| 34 (M7) | DS5 final-training (100,000) | Acceptance |

---

## 9. Dataset Governance

| Aspect | Policy |
|---|---|
| **Ownership** | Dataset Engineering lead |
| **Audit trail** | Every dataset: generation config, git hash, master seed, log files |
| **Change control** | Version bump + ADR for any dataset-affecting change |
| **Storage** | Versioned archive on network storage; SHA256SUMS verified |
| **Retirement** | Superseded versions archived, not deleted |
| **Citation** | README BibTeX + DOI when published |

---

## Sources

- Phase 4.4 — Dataset organization, validation, distribution.
- Phase 5.1 — Milestones M3–M7 (dataset gates).
- Phase 5.4 doc 04 — Dataset generation pipeline.
- [S5] Wilkinson et al., "The FAIR Guiding Principles," *Scientific Data*, 2016.
- [S9] Deng et al., "ImageNet: A Large-Scale Hierarchical Image Database," CVPR, 2009 (benchmark dataset governance).
