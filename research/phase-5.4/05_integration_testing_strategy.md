# Integration Testing Strategy

**Research Phase:** 5.4
**Document:** 05_integration_testing_strategy.md
**Date:** 2026-07-30

---

## 1. Test Layers

Six integration test layers, mapped to gates:

| Layer | Scope | Gate |
|---|---|---|
| **T1: Interface I1–I6** | Each frozen interface pair | L2 |
| **T2: End-to-end pipeline** | Config → SEMImage (full 10 stages) | L3 |
| **T3: Cross-module consistency** | Data invariants across all boundaries | L2/L3 |
| **T4: Golden dataset validation** | Full generated dataset vs reference | L3/L5 |
| **T5: Scientific validation** | Physics/geometry accuracy on output images | L4 |
| **T6: Failure injection** | Error handling, recovery, retry | L5 |

---

## 2. T1: Interface I1–I6 Validation

| Interface | Producer | Consumer | Test |
|---|---|---|---|
| I1 | geo_raster | geo_process | mask dims, values, pixel_size |
| I2 | geo_process | geo_variability | H/M dims, finiteness, IDs |
| I3 | geo_variability | phys_signal | I4 input valid (dims, range) |
| I3 | geo_variability | data_groundtruth | GT inputs valid |
| I4 | phys_signal | phys_degrade | YieldMaps range, dims |
| I5 | phys_degrade | phys_formation | Degraded range, finite |
| I6 | phys_formation | data_writer | SEMImage dtype, dims |

Each interface test: **real producer output → real consumer input**, checking every frozen postcondition (Phase 4.2).

---

## 3. T2: End-to-End Pipeline Tests

| Test | Fixture | Verifies |
|---|---|---|
| Full pipeline: iso_line | line GDSII + config | All 10 stages complete; files on disk |
| Full pipeline: dense_ls | dense GDSII + config | Cross-module handoff |
| Full pipeline: contact | contact GDSII + config | High-density geometry |
| Full pipeline: all 10 structures | structure library | Coverage across types |
| No-noise config | noise disabled | Identical to reference no-noise output |
| Determinism | run twice, same seed | SHA-256 identical |

**Golden end-to-end outputs:** SEMImage TIFF + GT JSON for 5 representative structures committed to `tests/data/reference_images/` + `reference_hashes.json`.

---

## 4. T3: Cross-Module Consistency

| Invariant | Check |
|---|---|
| Dimensions M×N everywhere | Assert at every boundary |
| Coordinate system | Edge positions in GT match image features (within 1 px) |
| Material IDs | MaterialMap → yield → GT segmentation consistent |
| Pixel size | Config → raster → physics → GT all share pixel_size_nm |
| Units | nm everywhere; keV/pA in config |
| No NaN/Inf | Global assert over every intermediate |

**Test:** run full pipeline with instrumentation that captures every intermediate D-object; run invariant assertions over the chain.

---

## 5. T4: Golden Dataset Validation

| Aspect | Specification |
|---|---|
| **Reference dataset** | Small fixed dataset (e.g., 20 samples, 2 per structure) generated once, reviewed, hashes committed |
| **Validation** | Regenerate and compare: per-file SHA-256, dataset_index.json structure, GT values, metadata fields |
| **Cross-run** | Same platform → bitwise identical |
| **Cross-platform** | Documented tolerance (float re-association may differ; documented, not enforced) |
| **Corruption detection** | Tamper with one image → validation L1/L5 detects |

---

## 6. T5: Scientific Validation

| Metric | Target | Where |
|---|---|---|
| CD accuracy | ± 0.1 nm | GT vs structure config |
| LER 3σ/ξ/ρ | ± 0.3 nm / ± 10% / ± 0.05 | Measured from edges |
| SE yield Si | δ(1 keV) ∈ [0.4, 0.8] | Flat-region intensity calibration |
| BSE contrast ordering | W > Cu > Si | Multi-material test structure |
| PSF width | FWHM ± 1% | Line-profile on image |
| Edge brightening | ratio = factor ± 0.5% | Edge vs flat intensity |
| Noise statistics | mean ± 1%; σ ± 2% | Empirically over flat region |
| Digitization | value bounds exact | Histogram check |
| Saturation detection | saturation fraction = recorded | Flagged in metadata |

---

## 7. T6: Failure Injection

| Failure | Injection | Expected Behavior |
|---|---|---|
| Invalid GDSII path | Point at missing file | Config/geometry error → sample FAILED, batch continues |
| Corrupt GDSII | Malformed fixture | Permanent error, clear message |
| Material ID out of range | MaterialMap tampered | Yield lookup error → sample FAILED |
| NaN in height field | Tampered fixture | Postcondition check catches → FAILED |
| Disk full (simulated) | Fill temp dir | Transient RETRY × 3 → then FAILED |
| Worker crash (simulated) | Kill worker mid-image | Manifest shows partial → resume re-runs |
| Config schema error | Invalid YAML | Fail-fast before batch |
| Seed collision | Two identical config+seed | Warning in manifest (permitted duplicates documented) |
| Numerical instability | Extreme params (CD=10 nm, LER=5 nm) | Advisory warnings; clamped outputs |

**Recovery tests:**

| Test | Verifies |
|---|---|
| Kill at sample 47/100 → resume | Continues at 48, no duplicate/corrupt files |
| Partial `.tmp` file present | Cleanup on resume |
| Retry succeeds after transient | Sample completes on 2nd attempt |
| Batch abort on critical | Completed samples preserved |

---

## 8. Regression & Determinism Suite

| Test | Method |
|---|---|
| Per-module regression | Golden hashes (Phase 5.2/5.3) |
| Interface regression | I1–I8 contract tests |
| End-to-end regression | Golden SEM images |
| Dataset regression | Golden dataset SHA-256 |
| Determinism | Run twice → identical; hash chain |
| Seed independence | seed A ≠ seed B → different outputs |
| Library version pin | CI checks pinned versions |

**CI trigger:** full regression on every merge to `develop`; nightly on `main`; golden dataset regeneration weekly in staging.

---

## Sources

- Phase 4.2 — Interface contracts (I1–I8) and validation.
- Phase 4.4 — Dataset validation (L1–L5).
- Phase 5.1 — Validation gates (L0–L5).
- Phase 5.2/5.3 — Module testing conventions.
- [G9] J. B. Rainsberger, *JUnit Recipes*, Manning, 2004.
- [S6] M. Utting, B. Legeard, *Practical Model-Based Testing*, Morgan Kaufmann, 2007.
