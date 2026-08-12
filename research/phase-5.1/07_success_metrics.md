# Success Metrics

**Research Phase:** 5.1
**Document:** 07_success_metrics.md
**Date:** 2026-07-30

---

## 1. Metric Framework

| Category | When Measured | Who Measures | Action if Below Target |
|---|---|---|---|
| **Milestone completion** | At each milestone | Program manager | Schedule re-plan |
| **Test coverage** | Continuous (CI) | Developers | Block PR if below threshold |
| **Scientific validation** | At L4 gate | Scientific lead | Scientific review |
| **Performance** | At L5 gate | Performance lead | Optimization sprint |
| **Reproducibility** | At L5 gate | QA lead | Bug resolution |
| **Dataset readiness** | At M7 | Dataset lead | Final polish |

---

## 2. Progress Metrics

### 2.1 Milestone Completion

| Metric | Target | Measurement |
|---|---|---|
| **Milestones on schedule** | 100% (8/8) | Actual completion date vs. planned |
| **Milestone deliverables met** | 100% | Pass/fail at milestone gate |
| **Work packages completed** | 27/27 | Count per stage |

### 2.2 Module Completion

| Module | Completion Criteria | Verification |
|---|---|---|
| M1: geo_raster | All GDSII features; all structure types; anti-aliasing | L1 gate: module validation |
| M2: geo_process | 10 structure types; all process steps; correct profiles | L1 gate + visual inspection |
| M3: geo_variability | LER, CDU, overlay; determinism verified | L1 gate: LER statistics |
| M4: phys_signal | SE/BSE yield; topographic/material/edge contrast | L1 gate + L4 scientific |
| M5: phys_degrade | PSF, noise, charging; zero-diameter bypass | L1 gate |
| M6: phys_formation | Digitization; gain/offset; saturation detection | L1 gate |
| M7: data_groundtruth | Edge maps; CD values; contours; segmentation | L1 + L4 (CD accuracy) |
| M8: data_writer | TIFF/JSON output; naming; index | L1 gate |
| M9: config_parser | YAML/TOML; validation; defaults; libraries | L1 gate |
| M10: orch_pipeline | Sequential execution; timing; error handling | L3 gate |

---

## 3. Quality Metrics

### 3.1 Test Coverage

| Level | Target | Tool |
|---|---|---|
| **Line coverage** (unit tests) | ≥ 80% | pytest-cov |
| **Branch coverage** (unit tests) | ≥ 70% | pytest-cov |
| **Interface coverage** | 8/8 interfaces tested | pytest |
| **Pipeline coverage** | All 10 structure types | pytest |

### 3.2 Code Quality

| Metric | Target | Tool |
|---|---|---|
| **Type coverage** | 100% of public functions typed | mypy --strict |
| **Lint score** | 0 errors, 0 warnings | ruff |
| **Formatting compliance** | 100% | black --check |
| **Documented public API** | 100% of public functions | Sphinx autodoc |

---

## 4. Scientific Validation Metrics

### 4.1 CD Accuracy

| Structure Type | Target | Tolerance |
|---|---|---|
| Isolated line | |CD_meas − CD_config| ≤ 0.1 nm |
| Dense line/space | |CD_meas − CD_config| ≤ 0.15 nm |
| Contact hole | |CD_meas − CD_config| ≤ 0.15 nm |
| Via | |CD_meas − CD_config| ≤ 0.15 nm |
| Trench | |CD_meas − CD_config| ≤ 0.1 nm |
| Fin | |CD_meas − CD_config| ≤ 0.15 nm |

### 4.2 LER Accuracy

| Metric | Target |
|---|---|
| **LER 3σ measured vs configured** | |LER_meas − LER_config| ≤ 0.3 nm |
| **LER correlation length** | ξ_meas within ±10% of ξ_config |
| **LER mean CD bias** | |mean(CD_meas) − CD_config| ≤ 0.5 nm (unbiased) |

### 4.3 Physics Accuracy

| Metric | Target | Method |
|---|---|---|
| **SE yield (Si, 1 keV)** | δ ∈ [0.4, 0.8] | Published literature range |
| **BSE yield (Si, 1 keV)** | η ∈ [0.15, 0.25] | Published literature range |
| **SE edge brightening** | Edge × [1.5, 3.0] × flat signal | Measured at 45° edge |
| **PSF width** | LSF_FWHM within ±10% of configured probe diameter | Line profile measurement |
| **Noise variance** | σ²(shot) = mean±5%; σ(detector) = configured σ | Empirical measurement |

---

## 5. Performance Metrics

### 5.1 Per-Image Timing

| Image Size | Target (Single Thread) | Target (4 Workers) |
|---|---|---|
| 512×512 | < 1 s | < 0.4 s effective |
| 1024×1024 | < 3 s | < 1.0 s effective |
| 2048×2048 | < 12 s | < 4 s effective |
| 4096×4096 | < 60 s | < 20 s effective |

### 5.2 Batch Performance

| Dataset Size | Target Wall Time (4 Workers) | Speedup vs Sequential |
|---|---|---|
| 100 images | < 30 s | ≥ 3.5× |
| 1,000 images | < 5 min | ≥ 3.5× |
| 10,000 images | < 45 min | ≥ 3.5× |
| 100,000 images | < 8 hr | ≥ 3.5× |

### 5.3 Memory

| Condition | Target |
|---|---|
| Single image (1024×1024) | < 500 MB RSS |
| 4 parallel workers (1024×1024) | < 2 GB RSS total |
| Max peak (4096×4096) | < 4 GB RSS per worker |

### 5.4 Disk

| Component | Target |
|---|---|
| Image file size (1024×1024, 16-bit, LZW TIFF) | < 3 MB |
| JSON metadata per sample | < 50 KB |
| Dataset index (100,000 samples) | < 100 MB |

---

## 6. Dataset Metrics

| Metric | Target |
|---|---|
| **Validation L1** (file completeness) | 100% of expected files present |
| **Validation L2** (metadata consistency) | 100% cross-references pass |
| **Validation L3** (ground truth accuracy) | All CD values within tolerance |
| **Validation L4** (version compatibility) | 100% uniform schema version |
| **Validation L5** (reproducibility) | SHA-256 match across runs |
| **Cache hit rate** (repeated structures) | ≥ 50% |
| **Checkpoint resume accuracy** | 100% of images resumed correctly |

---

## 7. Dashboard

All metrics are tracked in a project dashboard:

```
MILESTONE TRACKING
  □ M0: Foundation        □ M4: Ground Truth
  □ M1: Geometry          □ M5: Batch Execution
  □ M2: Physics           □ M6: Production
  □ M3: Single Pipeline   □ M7: Final Release

TEST COVERAGE
  ▓▓▓▓▓▓▓▓▓▓ 85% (target: 80%)

SCIENTIFIC ACCURACY
  ▓▓▓▓▓▓▓▓▓▓ CD accuracy: 0.08 nm (target: 0.10 nm)
  ▓▓▓▓▓▓▓░░░ LER accuracy: 0.31 nm (target: 0.30 nm)

PERFORMANCE
  ▓▓▓▓▓▓░░░░ 1024×1024: 2.1 s (target: 3.0 s)
  ▓▓▓▓▓▓▓▓▓▓ Parallel speedup: 3.7× (target: 3.5×)
```

---

## Sources

- [I12] ISO/IEC 15939, "Software Engineering — Software Measurement Process," 2007.
- [I13] R. E. Park et al., "Goal/Question/Metric Paradigm," CMU/SEI, 1994.
- Phase 4.3 — Runtime performance estimates.
- Phase 4.4 — Dataset validation specifications.
