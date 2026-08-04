# Validation Gates

**Research Phase:** 5.1
**Document:** 05_validation_gates.md
**Date:** 2026-07-30

---

## 1. Gate Architecture

Six validation gates from L0 (unit) to L5 (acceptance):

```
L0: Unit Tests
  ↓  (merge to feature branch)
L1: Module Validation
  ↓  (merge to main)
L2: Interface Validation
  ↓  (milestone complete)
L3: Pipeline Validation
  ↓  (Stage 1 complete)
L4: Scientific Validation
  ↓  (Stage 2 complete)
L5: Acceptance Gate
  ↓  (Stage 3 complete → Release)
```

---

## 2. Gate Specifications

### 2.1 L0: Unit Tests

| Aspect | Specification |
|---|---|
| **Scope** | Every public function, every module, every class |
| **When applied** | Before merge to feature branch |
| **Execution** | `pytest tests/unit/` |
| **Pass criteria** | All tests pass; no `xfail` or `skip` without documented reason |
| **Coverage** | ≥ 80% line coverage per module (measured by `pytest-cov`) |
| **What is tested** | Known input → expected output; edge cases; boundary values; error conditions |
| **Failure action** | PR blocked; must fix or document exception |
| **Owner** | Developer |

**Examples:**

| Module | Test Cases |
|---|---|
| math_utils | Convolution: identity kernel → same image. Distance transform: known shape → known distances. Gradient: flat region → zero gradient. |
| rng_utils | Fixed seed → exact known sequence. Two different seeds → different sequences. Hierarchical seed → deterministic derivation. |
| geo_raster | Known GDSII polygon → known pixel mask. Anti-aliasing: 45° line → correct edge pixels. |
| phys_signal | Flat surface → constant yield. Vertical sidewall → step change. |

---

### 2.2 L1: Module Validation

| Aspect | Specification |
|---|---|
| **Scope** | Complete module works as specified in Phase 4.2 interface contract |
| **When applied** | Before merge to main |
| **Execution** | `pytest tests/module/{module_name}/` |
| **Pass criteria** | All module-level tests pass; preconditions, postconditions verified; all error conditions exercised |
| **What is tested** | Module accepts all specified inputs; produces all specified outputs; handles all error conditions correctly |
| **Failure action** | PR blocked; interface violation must be fixed |
| **Owner** | Module lead |

**Module validation tests:**

| Module | Key Tests |
|---|---|
| geo_raster | GDSII file not found → error; layer not found → error; all GDSII data types handled |
| geo_process | Empty layer stack → error; each structure type produces correct dimensions |
| geo_variability | LER 3σ measured = configured 3σ ± tolerance; overlay shift verified |
| phys_signal | Material property missing → error; beam energy outside table → warning |
| phys_degrade | Zero probe → no blur; nonzero → measurable; noise off → no noise |
| phys_formation | Negative gain → error; saturation fractions computed correctly |
| data_groundtruth | Edge threshold too high → warning; no features detected → handled |
| data_writer | Output directory not writable → error; valid TIFF produced |

---

### 2.3 L2: Interface Validation

| Aspect | Specification |
|---|---|
| **Scope** | Paired modules satisfy their I-interface contract |
| **When applied** | At each interface boundary, before milestone declaration |
| **Execution** | `pytest tests/interface/` |
| **Pass criteria** | I-interface preconditions and postconditions verified; data objects match spec |
| **What is tested** | Each I1–I8 interface: known input → expected output; unit consistency; coordinate system consistency |
| **Failure action** | Milestone blocked; interface mis-match must be resolved |
| **Owner** | Pair of module leads |

**Interface pairs:**

| Interface | Producer | Consumer | Test |
|---|---|---|---|
| I1 | geo_raster | geo_process | geo_raster output → geo_process input; dimensions, values, pixel_size match |
| I2 | geo_process | geo_variability | HeightField_det + MaterialMap_det → both consumed |
| I3 | geo_variability | phys_signal (I4) | HeightField_var + MaterialMap_var → correct dimensions, finite values |
| I3 | geo_variability | data_groundtruth (I7) | HeightField_var + MaterialMap_var → GT correct |
| I4 | phys_signal | phys_degrade (I5) | YieldMaps dimensions, range correct |
| I5 | phys_degrade | phys_formation (I6) | YieldMaps_degraded correct |
| I6 | phys_formation | data_writer (I8) | SEMImage bit depth, dimensions correct |

---

### 2.4 L3: Pipeline Validation

| Aspect | Specification |
|---|---|
| **Scope** | End-to-end pipeline from config to output files |
| **When applied** | At M3 milestone (week 14) |
| **Execution** | `semicon-sim --self-check`; `pytest tests/pipeline/` |
| **Pass criteria** | Full pipeline runs without errors; self-check mode passes; output files are valid; regression hash matches reference |
| **What is tested** | Config → end-to-end → files on disk. All 10 structure types (minimal test). Determinism: same seed → same output. |
| **Failure action** | Milestone blocked; pipeline bug must be fixed |
| **Owner** | Integration lead |

---

### 2.5 L4: Scientific Validation

| Aspect | Specification |
|---|---|
| **Scope** | Scientific correctness of outputs |
| **When applied** | At M4-M5 milestones (weeks 17–22) |
| **Execution** | `pytest tests/scientific/` |
| **Pass criteria** | |

**CD accuracy:** |CD_measured − CD_configured| ≤ LER_3sigma + 0.5 nm

**Edge positions:** Signed distance map zero-crossings match expected edges within 0.1 nm

**Yield values:** SE yield within ±20% of published values for known materials (e.g., Si at 1 keV → δ_SE ≈ 0.5–0.7)

**Noise statistics:** Shot noise variance ≈ mean signal; detector noise Gaussian with configured σ

**PSF blur:** Line spread function width matches configured probe diameter

**Failure action** | Milestone delayed; scientific model bug must be fixed before dataset generation |
| **Owner** | Scientific lead |

---

### 2.6 L5: Acceptance Gate

| Aspect | Specification |
|---|---|
| **Scope** | Complete system ready for production dataset generation |
| **When applied** | At M7 milestone (week 36) |
| **Execution** | Full validation suite: `semicon-sim --validate` on a 1000-image benchmark dataset |
| **Pass criteria** | |

**All L0–L4 tests pass**

**Reproducibility:** Same config + seed on same platform → bitwise identical SEMImage (SHA-256 match)

**Performance:** Average per-image time < 3 s at 1024×1024 on reference workstation

**Parallel scaling:** 4 workers → ≥ 3.5× speedup over sequential (Amdahl efficiency ≥ 87%)

**Cache hit rate:** ≥ 50% for repeated structures with different variability seeds

**Checkpoint resume:** 1000-image batch, kill at image 423, resume → image 424 continues correctly

**Documentation:** All public functions documented; user guide complete; API reference passes doc build

**Install:** `pip install .` in fresh Python environment → all tests pass

**Failure action** | Release blocked; specific failures must be resolved |
| **Owner** | Program manager |

---

## 3. Gate Summary Table

| Gate | Name | When | Coverage | Pass Criteria | Owner |
|---|---|---|---|---|---|
| **L0** | Unit | Every PR | Per-function | All tests pass; ≥ 80% coverage | Developer |
| **L1** | Module | Module merge | Per-module | Interface contract satisfied | Module lead |
| **L2** | Interface | Milestone | Per-interface pair | Pre/post conditions verified | Module leads (pair) |
| **L3** | Pipeline | M3 milestone | End-to-end | Self-check passes; regression hash matches | Integration lead |
| **L4** | Scientific | M4–M5 milestone | Scientific output quality | CD accuracy ±0.1 nm; yield within 20% of reference | Scientific lead |
| **L5** | Acceptance | M7 milestone | Complete system | All metrics; reproducibility; performance; install | Program manager |

---

## 4. Gate Violation Response

| Violation | Response |
|---|---|
| L0 failure in PR | Blocked; fix before merge |
| L1 failure in module merge | Blocked; interface regression |
| L2 failure at interface | I-interface investigation; coordinate fix |
| L3 pipeline failure | Root cause analysis; regression test before fix |
| L4 scientific failure | Scientific model review; physics/geometry bug fix |
| L5 acceptance failure | Bug fix or risk acceptance (documented waiver) |

---

## Sources

- [I8] S. McConnell, *Code Complete*, 2nd ed. Microsoft Press, 2004.
- [I9] G. J. Myers, C. Sandler, T. Badgett, *The Art of Software Testing*, 3rd ed. Wiley, 2011.
- Phase 4.2, Document 06 — Interface Validation Strategy (L1–L5 framework).
- Phase 4.5, Document 08 — Final certification.
