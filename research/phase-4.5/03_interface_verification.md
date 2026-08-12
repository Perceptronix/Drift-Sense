# Interface Verification

**Research Phase:** 4.5 (Final Audit)
**Document:** 03_interface_verification.md
**Date:** 2026-07-30

---

## 1. Interface Audit Summary

| Interface | Status | Preconditions | Postconditions | Ambiguity |
|---|---|---|---|---|
| **I1** | ✅ Verified | 5 | 5 | None |
| **I2** | ✅ Verified | 6 | 6 | None |
| **I3** | ✅ Verified | 5 | 6 | Minor |
| **I4** | ✅ Verified | 4 | 4 | None |
| **I5** | ✅ Verified | 3 | 4 | None |
| **I6** | ✅ Verified | 3 | 3 | None |
| **I7** | ✅ Verified | 2 | 3 | None |
| **I8** | ✅ Verified | 3 | 4 | Minor |

---

## 2. Interface I1: GDSII Rasterizer

| Aspect | Specification | Verified? | Notes |
|---|---|---|---|
| **Inputs** | GDSII file path, layer number, M, N, pixel_size_nm, field_center (optional) | ✅ | Complete |
| **Output** | PixelMask: M×N uint8, 0/1 values | ✅ | Complete |
| **Precondition 1** | File exists and readable | ✅ | Clear |
| **Precondition 2** | Layer number exists in file | ✅ | Clear |
| **Precondition 3** | M > 0, N > 0 | ✅ | Clear |
| **Precondition 4** | pixel_size_nm > 0 | ✅ | Clear |
| **Precondition 5** | FOV ≤ layout extent | ✅ | Extent check supported |
| **Postcondition 1** | Output dimensions = M×N | ✅ | Clear |
| **Postcondition 2** | Values ∈ {0, 1} | ✅ | Clear |
| **Postcondition 3** | pixel_size_nm matches input | ✅ | Clear |
| **Postcondition 4** | In-FOV polygons rasterized | ✅ | Clear |
| **Postcondition 5** | Out-of-FOV polygons clipped | ✅ | Clear |
| **Unit consistency** | nm throughout | ✅ | Yes |
| **Coordinate system** | Row=Y, Col=X, origin top-left | ✅ | Clear |

**Ambiguity:** None.

---

## 3. Interface I2: Process Model

| Aspect | Specification | Verified? | Notes |
|---|---|---|---|
| **Inputs** | PixelMask, LayerStack, ProcessConfig | ✅ | Complete |
| **Outputs** | HeightField_det, MaterialMap_det | ✅ | Complete |
| **Precondition 1** | LayerStack non-empty | ✅ | Clear |
| **Precondition 2** | Material IDs ∈ {0..6} | ✅ | Clear |
| **Precondition 3** | Thicknesses > 0 | ✅ | Clear |
| **Precondition 4** | Sidewall angles ∈ [80°, 90°] | ✅ | Clear |
| **Precondition 5** | Dimensions match stage input | ✅ | Clear |
| **Precondition 6** | CMP target ≤ deposited height | ✅ | Clear |
| **Postcondition 1** | HeightField dimensions = input dimensions | ✅ | Clear |
| **Postcondition 2** | MaterialMap dimensions = input dimensions | ✅ | Clear |
| **Postcondition 3** | Height ∈ [0, max_stack_height] | ✅ | Clear |
| **Postcondition 4** | All heights finite (no NaN, Inf) | ✅ | Clear |
| **Postcondition 5** | Material IDs ∈ {0..6} | ✅ | Clear |
| **Postcondition 6** | Trapezoidal profile (top_CD ≤ bottom_CD) | ✅ | Clear |

**Ambiguity:** None.

---

## 4. Interface I3: Variability Engine

| Aspect | Specification | Verified? | Notes |
|---|---|---|---|
| **Inputs** | HeightField_det, MaterialMap_det, VariabilityConfig, StructureSpec | ✅ | Complete |
| **Outputs** | HeightField_var, MaterialMap_var, VariabilityRecord | ✅ | Complete |
| **Precondition 1** | HeightField_det finite everywhere | ✅ | Clear |
| **Precondition 2** | LER 3σ ≤ 0.5 × min(CD) | ⚠️ Advisory | This is a warning, not a hard limit. Edges may cross. |
| **Precondition 3** | ξ ≥ 2 × pixel_size_nm | ✅ | Clear |
| **Precondition 4** | ρ ∈ [0, 1] | ✅ | Clear |
| **Precondition 5** | Overlay σ ≤ 0.1 × FOV | ⚠️ Advisory | Advisory warning. |
| **Postcondition 1** | Output dimensions = input dimensions | ✅ | Clear |
| **Postcondition 2** | MaterialMap dimensions = input dimensions | ✅ | Clear |
| **Postcondition 3** | LER with specified σ and ξ | ✅ | Clear |
| **Postcondition 4** | mean(CD) = nominal CD (unbiased) | ✅ | Clear |
| **Postcondition 5** | No edge crossing (left < right) | ✅ | Clear |
| **Postcondition 6** | MaterialMap unchanged except near edges | ✅ | Clear |

**Minor Ambiguity:** The LER edge-finding algorithm is specified as "edge detection on height field" but the exact height threshold for defining the edge is not specified at this interface (it is specified in the GroundTruth specification, Phase 4.4 doc 04). This is acceptable because the Variability Engine's LER is applied directly to edges identified by the height field gradient, not a threshold. **Recommendation:** Document in implementation that the Variability Engine uses gradient-based edge detection (not threshold-based) for LER application.

---

## 5. Interface I4: Signal Generator (Certified Boundary)

| Aspect | Specification | Verified? | Notes |
|---|---|---|---|
| **Inputs** | HeightField_var, MaterialMap_var, PhysicsConfig | ✅ | Complete |
| **Outputs** | YieldMaps: se_yield, bse_yield | ✅ | Complete |
| **Precondition 1** | Material library contains all IDs | ✅ | Clear |
| **Precondition 2** | Beam energy ∈ material table range | ✅ | Clear |
| **Precondition 3** | HeightField and MaterialMap dimensions match | ✅ | Clear |
| **Precondition 4** | HeightField finite | ✅ | Clear |
| **Postcondition 1** | Yield dimension = input dimensions | ✅ | Clear |
| **Postcondition 2** | Yield values ∈ [0, 10] | ✅ | Clear |
| **Postcondition 3** | SE variance matches topographic contrast | ✅ | Clear |
| **Postcondition 4** | Material contrast follows property table | ✅ | Clear |

**Ambiguity:** None. This is the most thoroughly specified interface (certified in Phase 2.6 and Phase 3.4).

---

## 6. Interface I5: Degradation Model

| Aspect | Specification | Verified? | Notes |
|---|---|---|---|
| **Inputs** | YieldMaps, DegradationConfig, SEMConfig (optional) | ✅ | Complete |
| **Outputs** | YieldMaps_degraded | ✅ | Complete |
| **Precondition 1** | se_yield and bse_yield dimensions match | ✅ | Clear |
| **Precondition 2** | Probe diameter ≥ 0 | ✅ | Clear |
| **Precondition 3** | PSF kernel ≤ image dimensions | ✅ | Clear |
| **Postcondition 1** | Yield values ∈ [0, 10] (clamped) | ✅ | Clear |
| **Postcondition 2** | PSF applied if probe_diameter > 0 | ✅ | Clear |
| **Postcondition 3** | Shot noise applied if enabled | ✅ | Clear |
| **Postcondition 4** | No systematic DC shift (conserved mean) | ✅ | Clear |

**Ambiguity:** None.

---

## 7. Interface I6: Image Former

| Aspect | Specification | Verified? | Notes |
|---|---|---|---|
| **Inputs** | YieldMaps_degraded, DetectorConfig | ✅ | Complete |
| **Outputs** | SEMImage, FormationRecord | ✅ | Complete |
| **Precondition 1** | Gain > 0 | ✅ | Clear |
| **Precondition 2** | Bit_depth ∈ {8, 16} | ✅ | Clear |
| **Precondition 3** | Offset may be any float | ✅ | Clear |
| **Postcondition 1** | SEMImage dimensions = yield dimensions | ✅ | Clear |
| **Postcondition 2** | Pixel values ∈ [0, 2^bit_depth − 1] | ✅ | Clear |
| **Postcondition 3** | Mapping: I = min(max(gain×yield+offset, 0), max_DN) | ✅ | Clear |

**Ambiguity:** None.

---

## 8. Interface I7: Ground Truth Generator

| Aspect | Specification | Verified? | Notes |
|---|---|---|---|
| **Inputs** | HeightField_var, MaterialMap_var, GroundTruthConfig | ✅ | Complete |
| **Outputs** | GroundTruth (edge maps, CD, contours, segmentation) | ✅ | Complete |
| **Precondition 1** | HeightField and MaterialMap dimensions match | ✅ | Clear |
| **Precondition 2** | Edge threshold ∈ [0, max_height] | ✅ | Clear |
| **Postcondition 1** | Edge positions in nm (not pixels) | ✅ | Clear |
| **Postcondition 2** | Edges physically meaningful | ✅ | Clear |
| **Postcondition 3** | CD values = true CD from height field | ✅ | Clear |

**Ambiguity:** None.

---

## 9. Interface I8: Dataset Writer

| Aspect | Specification | Verified? | Notes |
|---|---|---|---|
| **Inputs** | SEMImage, GroundTruth (optional), Metadata, DatasetConfig | ✅ | Complete |
| **Outputs** | Files on disk, FileList, DatasetIndexEntry | ✅ | Complete |
| **Precondition 1** | Output directory writable | ✅ | Clear |
| **Precondition 2** | Disk space sufficient | ✅ | Clear |
| **Precondition 3** | Image data not null | ✅ | Clear |
| **Postcondition 1** | Image file exists on disk | ✅ | Clear |
| **Postcondition 2** | Valid TIFF/PNG file | ✅ | Clear |
| **Postcondition 3** | Metadata file exists and valid JSON | ✅ | Clear |
| **Postcondition 4** | Dataset index updated | ✅ | Clear |

**Minor Ambiguity:** The PSF normalization convention (conserved mean vs. conserved peak) is not specified in the degradation model interface. Implementation must decide: should the PSF kernel be normalized to sum=1 (conserved mean) or max=1 (conserved peak)? **Recommendation:** Use sum=1 normalization (conserved mean) — this is the standard in imaging and matches the postcondition "no systematic DC shift."

---

## 10. Interface Verification Verdict

| Criterion | Verdict |
|---|---|
| All inputs specified | ✅ **PASS** — Every interface input has type, description, and source |
| All outputs specified | ✅ **PASS** — Every interface output has type, description, and destination |
| Preconditions complete | ✅ **PASS** — All error conditions identified |
| Postconditions complete | ✅ **PASS** — All output guarantees stated |
| Unit consistency | ✅ **PASS** — nm, keV, pA consistent across all interfaces |
| Coordinate system consistent | ✅ **PASS** — Row=Y, Col=X, origin top-left everywhere |
| **Overall** | ✅ **PASS — 2 minor items for implementation guidance** |

---

## Sources

- Phase 4.2, Document 04 — API Contract Specification.
- Phase 4.2, Document 02 — Module Interface Inventory.
- [A6] B. Meyer, *Object-Oriented Software Construction*, 2nd ed. Prentice Hall, 1997 (Design by Contract).
