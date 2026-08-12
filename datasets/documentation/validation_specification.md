# Dataset Validation Specification

**Frozen:** Phase 4.4 doc 06; Phase 5.4 doc 05 (integration testing).

---

## Validation Levels

| Level | Scope | Pass Criteria |
|---|---|---|
| **L1: File completeness** | All expected files exist | 100% of manifest entries present |
| **L2: Metadata consistency** | Cross-field agreement | 100% cross-references pass |
| **L3: Ground-truth accuracy** | GT vs structure config | CD within ± 0.1 nm |
| **L4: Scientific validation** | Physics/geometry accuracy | All targets met (see table) |
| **L5: Reproducibility** | Determinism | SHA-256 match on same platform |

---

## L4 Scientific Targets

| Metric | Target |
|---|---|
| CD accuracy | ± 0.1 nm |
| LER 3σ | ± 0.3 nm |
| LER ξ | ± 10% |
| LER ρ | ± 0.05 |
| Overlay shift | ± 0.1 nm |
| Si SE yield (1 keV) | δ ∈ [0.4, 0.8] |
| Si BSE yield (1 keV) | η ∈ [0.15, 0.25] |
| Material contrast | Cu SE < Si SE; W BSE > Cu BSE > Si BSE |
| PSF FWHM | ± 1% |
| Edge brightening ratio | ± 0.5% |

---

## Per-Dataset Validation Gates

| Dataset | L1 | L2 | L3 | L4 | L5 |
|---|---|---|---|---|---|
| DS1 development | ✅ | ✅ | ✅ | — | spot |
| DS2 unit-test | ✅ | ✅ | ✅ | — | ✅ |
| DS3 validation | ✅ | ✅ | ✅ | — | ✅ |
| DS4 scientific-benchmark | ✅ | ✅ | ✅ | ✅ | ✅ |
| DS5 final-training | ✅ | ✅ | ✅ | sampling | ✅ |

---

## Release Criteria per Dataset

| Dataset | Release When |
|---|---|
| DS1 | Pipeline M3 complete; L1–L2 pass |
| DS2 | Golden hashes committed; CI green |
| DS3 | L1–L5 pass; stats report produced |
| DS4 | L4 scientific targets met |
| DS5 | All gates + stakeholder weighting review |

---

## Validation Commands (post-implementation)

```
semicon-sim --validate <dataset_root> --level L1
semicon-sim --validate <dataset_root> --level L2
semicon-sim --validate <dataset_root> --level L3
semicon-sim --validate <dataset_root> --level L4
semicon-sim --validate <dataset_root> --level L5
sh checksums/verify_checksums.sh <dataset_root>
```

---

*Frozen in Phase 5.5; derived from Phase 4.4 doc 06.*
