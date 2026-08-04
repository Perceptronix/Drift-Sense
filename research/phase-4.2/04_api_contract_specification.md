# API Contract Specification

**Research Phase:** 4.2
**Document:** 04_api_contract_specification.md
**Date:** 2026-07-30

---

## 1. Contract Model

Every interface contract has four parts:

| Part | Description | Examples |
|---|---|---|
| **Inputs** | Data the interface accepts | PixelMask, LayerStack, VariabilityConfig |
| **Outputs** | Data the interface produces | HeightField_det, MaterialMap_det |
| **Preconditions** | Conditions that must be true before call | PixelMask dimensions positive; LayerStack non-empty |
| **Postconditions** | Conditions guaranteed after call | HeightField same dimensions as input; all heights finite |
| **Validation rules** | Checks applied at the interface boundary | Type check, range check, consistency check |

---

## 2. Interface I1: GDSII Rasterizer Contract

| Aspect | Specification |
|---|---|
| **Interface ID** | I1 |
| **Module** | M1 GDSII Rasterizer |
| **Direction** | Configuration → Geometry |

**Inputs:**

| Input | Type | Description |
|---|---|---|
| gdsii_file_path | String | Path to valid GDSII file |
| layer_number | Integer (uint32) | GDSII layer to rasterize |
| m | Integer | Output image height in pixels |
| n | Integer | Output image width in pixels |
| pixel_size_nm | Float | Pixel spacing in nm |
| field_center_nm_x | Float (optional) | FOV center X (default: layout center) |
| field_center_nm_y | Float (optional) | FOV center Y (default: layout center) |

**Outputs:**

| Output | Type | Description |
|---|---|---|
| pixel_mask | PixelMask (D3) | Binary mask: 1 = feature, 0 = no feature |
| transform_record | Struct | GDSII → pixel coordinate transform used |

**Preconditions:**

| # | Condition | On Violation |
|---|---|---|
| 1 | File exists and is readable | Fatal: "GDSII file not found" |
| 2 | Layer number exists in file | Fatal: "Layer not found" |
| 3 | M > 0, N > 0 | Fatal: "Invalid dimensions" |
| 4 | pixel_size_nm > 0 | Fatal: "Invalid pixel size" |
| 5 | FOV = (M × pixel_size_nm) ≤ layout extent | Warning: clip, or fatal as configured |

**Postconditions:**

| # | Condition | Guarantee |
|---|---|---|
| 1 | pixel_mask dimensions = M × N | Always |
| 2 | All pixel_mask values ∈ {0, 1} | Always |
| 3 | pixel_mask pixel_size_nm matches input | Always |
| 4 | Polygons within FOV are rasterized | Always |
| 5 | Polygons outside FOV are clipped at boundary | Always |

**Validation rules applied at interface:**

| Rule | Implementation |
|---|---|
| Type: file_path is string | Check String |
| Range: pixel_size_nm ∈ (0, 1000] | Check Float range |
| Consistency: M, N match config.image dimensions | Cross-check |

**Performance expectation:** < 100 ms for 1024×1024.

---

## 3. Interface I2: Process Model Contract

| Aspect | Specification |
|---|---|
| **Interface ID** | I2 |
| **Module** | M2 Process Model |
| **Direction** | Inside Geometry subsystem |

**Inputs:**

| Input | Type | Description |
|---|---|---|
| pixel_mask | PixelMask (D3) | Binary mask for one layer |
| layer_stack | LayerStack (D4) | Ordered list of layers with parameters |
| process_config | Struct | Deposition type, etch overrides, CMP config |

**Outputs:**

| Output | Type | Description |
|---|---|---|
| height_field | HeightField_det (D5) | Deterministic height field (nm) |
| material_map | MaterialMap_det (D6) | Deterministic material IDs |

**Preconditions:**

| # | Condition | On Violation |
|---|---|---|
| 1 | layer_stack non-empty | Fatal: "Empty layer stack" |
| 2 | All material IDs ∈ {0..6} | Fatal: "Invalid material ID" |
| 3 | All thicknesses > 0 | Fatal: "Non-positive thickness" |
| 4 | All sidewall angles ∈ [80°, 90°] | Warning and clamp |
| 5 | pixel_mask dimensions = stage input dimensions | Fatal: "Dimension mismatch" |
| 6 | CMP target ≤ sum of deposited thicknesses | Fatal: "CMP below substrate" |

**Postconditions:**

| # | Condition | Guarantee |
|---|---|---|
| 1 | height_field dimensions = pixel_mask dimensions | Always |
| 2 | material_map dimensions = pixel_mask dimensions | Always |
| 3 | All height_field values ∈ [0, max_stack_height] | Always |
| 4 | All height_field values are finite (no NaN, no Inf) | Always |
| 5 | All material_map values ∈ {0..6} | Always |
| 6 | Profile is trapezoidal (top_CD ≤ bottom_CD) | Always |

**Validation rules:**

| Rule | Implementation |
|---|---|
| Type: pixel_mask is PixelMask | Instance check |
| Range: all heights ≥ 0 | Array min check |
| Consistency: height_field and material_map same size | Shape check |
| Unit: values assumed nm | Implicit |

---

## 4. Interface I3: Variability Engine Contract

| Aspect | Specification |
|---|---|
| **Interface ID** | I3 |
| **Module** | M3 Variability Engine |
| **Direction** | Within Geometry subsystem |

**Inputs:**

| Input | Type | Description |
|---|---|---|
| height_field_det | HeightField_det (D5) | Deterministic geometry input |
| material_map_det | MaterialMap_det (D6) | Deterministic material input |
| variability_config | Struct | LER 3σ, ξ, ρ; overlay σ; sidewall σ; thickness σ; corner R σ; seed |
| structure_spec | Struct | Feature type, dimensions (for edge detection) |

**Outputs:**

| Output | Type | Description |
|---|---|---|
| height_field_var | HeightField_var (D5) | Variable height field (nm) |
| material_map_var | MaterialMap_var (D6) | Variable material IDs |
| variability_record | Struct | Actual LER σ applied, overlay applied, seed used |

**Preconditions:**

| # | Condition | On Violation |
|---|---|---|
| 1 | height_field_det finite everywhere | Fatal: "NaN in height field" |
| 2 | LER 3σ ≤ 0.5 × min(CD) | Warning: "LER may cause edge crossing" |
| 3 | ξ ≥ 2 × pixel_size_nm | Warning: "LER correlation less than 2 pixels" |
| 4 | ρ ∈ [0, 1] | Fatal: "Invalid correlation coefficient" |
| 5 | overlay σ ≤ 0.1 × min(M, N) × pixel_size_nm | Warning: "Overlay may crop features" |

**Postconditions:**

| # | Condition | Guarantee |
|---|---|---|
| 1 | height_field_var dimensions = input dimensions | Always |
| 2 | material_map_var dimensions = input dimensions | Always |
| 3 | Feature edges have LER with specified σ and ξ | Always |
| 4 | mean(CD_along_line) = nominal CD (unbiased) | Always |
| 5 | ∀ features: left_edge < right_edge (no crossing) | Always |
| 6 | material_map_var unchanged except near edges | Always |

**Validation rules:**

| Rule | Implementation |
|---|---|
| Range: LER 3σ ≥ 0 | Check |
| Range: ξ ≥ 0 | Check |
| Consistency: HeightField M,N unchanged | Cross-check |
| Physical: mean CD zero bias | Statistical check across feature |

---

## 5. Interface I4: Signal Generator Contract

| Aspect | Specification |
|---|---|
| **Interface ID** | I4 |
| **Module** | M4 Signal Generator |
| **Direction** | Geometry → Physics (I4 is the certified boundary) |

**Inputs:**

| Input | Type | Description |
|---|---|---|
| height_field | HeightField_var (D5) | Variable geometry input |
| material_map | MaterialMap_var (D6) | Variable material input |
| physics_config | Struct | Beam energy (keV), probe current (pA), SE/BSE model selection, material property table, charging configuration |

**Outputs:**

| Output | Type | Description |
|---|---|---|
| se_yield | YieldMap (D7) | Per-pixel SE yield (e⁻/e⁻) |
| bse_yield | YieldMap (D7) | Per-pixel BSE yield (e⁻/e⁻) |

**Preconditions:**

| # | Condition | On Violation |
|---|---|---|
| 1 | Material library contains all material IDs present | Fatal: "Material properties not found" |
| 2 | Beam energy ∈ material table range | Warning: "Extrapolating material properties" |
| 3 | height_field and material_map dimensions match | Fatal: "Dimension mismatch" |
| 4 | height_field finite everywhere | Fatal: "NaN in height field" |

**Postconditions:**

| # | Condition | Guarantee |
|---|---|---|
| 1 | se_yield, bse_yield dimensions = input dimensions | Always |
| 2 | All yield values ∈ [0, 10] | Always |
| 3 | SE yield variance matches topographic contrast relation | Always |
| 4 | Material contrast follows material property table | Always |

---

## 6. Interface I5: Degradation Model Contract

| Aspect | Specification |
|---|---|
| **Interface ID** | I5 |
| **Module** | M5 Degradation Model |
| **Direction** | Within Physics subsystem |

**Inputs:**

| Input | Type | Description |
|---|---|---|
| se_yield | YieldMap (D7) | Ideal SE yield |
| bse_yield | YieldMap (D7) | Ideal BSE yield |
| degradation_config | Struct | Probe diameter (nm); PSF model; enable_shot_noise (bool); enable_detector_noise (bool); enable_charging (bool); seed |
| sem_config | Struct (optional) | Scan parameters for beam degradation model |

**Outputs:**

| Output | Type | Description |
|---|---|---|
| se_yield_degraded | YieldMap (D7) | Degraded SE yield |
| bse_yield_degraded | YieldMap (D7) | Degraded BSE yield (or omitted if not degraded) |

**Preconditions:**

| # | Condition | On Violation |
|---|---|---|
| 1 | se_yield and bse_yield dimensions match | Fatal: "Dimension mismatch" |
| 2 | Probe diameter ≥ 0 | Fatal: "Negative probe diameter" |
| 3 | PSF kernel ≤ image dimensions | Warning: "Performance impact" |

**Postconditions:**

| # | Condition | Guarantee |
|---|---|---|
| 1 | All yield values ∈ [0, 10] | Always (clamped) |
| 2 | PSF applied if probe_diameter > 0 | Always |
| 3 | Shot noise added if enabled | Always |
| 4 | No systematic DC shift from PSF (conserved mean) | Always |

---

## 7. Interface I6: Image Former Contract

| Aspect | Specification |
|---|---|
| **Interface ID** | I6 |
| **Module** | M6 Image Former |
| **Direction** | Within Physics subsystem |

**Inputs:**

| Input | Type | Description |
|---|---|---|
| se_yield_degraded | YieldMap | Yield after degradation |
| detector_config | Struct | Gain (float > 0); offset (float); saturation_level (float); bit_depth (uint: 8 or 16); detector_efficiency_map (optional) |

**Outputs:**

| Output | Type | Description |
|---|---|---|
| sem_image | SEMImage (D8) | Digitized SEM image |
| formation_record | Struct | Applied gain, offset, saturation fraction |

**Preconditions:**

| # | Condition | On Violation |
|---|---|---|
| 1 | Gain > 0 | Fatal: "Non-positive gain" |
| 2 | Bit_depth ∈ {8, 16} | Fatal: "Unsupported bit depth" |
| 3 | Offset may be any float | No check |

**Postconditions:**

| # | Condition | Guarantee |
|---|---|---|
| 1 | SEMImage dimensions = yield dimensions | Always |
| 2 | All pixel values ∈ [0, 2^bit_depth − 1] | Always |
| 3 | Mapping: I = min(max(gain × yield + offset, 0), max_DN) | Always |

---

## 8. Interface I7: Ground Truth Generator Contract

| Aspect | Specification |
|---|---|
| **Interface ID** | I7 |
| **Module** | M7 Ground Truth Generator |
| **Direction** | Geometry → Dataset |

**Inputs:**

| Input | Type | Description |
|---|---|---|
| height_field | HeightField_var | Variable geometry |
| material_map | MaterialMap_var | Variable materials |
| ground_truth_config | Struct | Edge threshold height; include_contours; include_segmentation; include_cd_values |

**Outputs:**

| Output | Type | Description |
|---|---|---|
| ground_truth | GroundTruth (D9) | Edge maps, CD values, segmentation |

**Preconditions:**

| # | Condition | On Violation |
|---|---|---|
| 1 | height_field and material_map dimensions match | Fatal: "Dimension mismatch" |
| 2 | Edge threshold ∈ [0, height_field.max] | Warning: "No edges detected" |

**Postconditions:**

| # | Condition | Guarantee |
|---|---|---|
| 1 | All edge positions are in nm (not pixels) | Always |
| 2 | Edge results in physically meaningful contours | Always |
| 3 | CD values = true CD from height field | Always |

---

## 9. Interface I8: Dataset Writer Contract

| Aspect | Specification |
|---|---|
| **Interface ID** | I8 |
| **Module** | M8 Dataset Writer |
| **Direction** | All → Output |

**Inputs:**

| Input | Type | Description |
|---|---|---|
| sem_image | SEMImage (D8) | Image to write |
| ground_truth | GroundTruth (D9, optional) | Labels to write |
| metadata | Metadata (D10) | Generation metadata |
| dataset_config | Struct | Output format (tiff/png), directory structure |

**Outputs:**

| Output | Type | Description |
|---|---|---|
| file_list | Array of String | Paths of files written |
| dataset_index_entry | Struct | Entry added to dataset index |

**Preconditions:**

| # | Condition | On Violation |
|---|---|---|
| 1 | Output directory writable | Fatal: "Output directory not writable" |
| 2 | Disk space sufficient | Recoverable: retry, then fatal |
| 3 | image data not null | Fatal: "No image data" |

**Postconditions:**

| # | Condition | Guarantee |
|---|---|---|
| 1 | Image file exists on disk | Always |
| 2 | File is valid TIFF/PNG (readable by standard tools) | Always |
| 3 | Metadata file exists and is valid JSON | Always |
| 4 | Dataset index updated | Always |

---

## 10. Interface Summary Table

| Interface | From | To | Key Data | Critical Precondition |
|---|---|---|---|---|
| I1 | Config | Rasterizer | GDSII path, layer, dimensions | File exists; layer exists |
| I2 | Rasterizer | Process Model | PixelMask, LayerStack | Non-empty stack; valid materials |
| I3 | Process Model | Variability | HeightField_det, MatMap_det | No NaN; LER < 0.5 × CD |
| I4 | Variability | Signal Gen. | HeightField_var, MatMap_var | Material properties known |
| I5 | Signal Gen. | Degradation | YieldMaps | Dimensions match; PSF valid |
| I6 | Degradation | Image Former | YieldMaps_degraded | Gain > 0 |
| I7 | Variability | Ground Truth | HeightField_var, MatMap_var | Threshold valid |
| I8 | Image Former + GT | Dataset Writer | SEMImage, GroundTruth, Metadata | Output writable |

---

## Sources

- [I1] C. Larman, *Applying UML and Patterns*, Prentice Hall, 2004.
- [I2] B. Meyer, *Object-Oriented Software Construction*, Prentice Hall, 1997.
- [I3] R. C. Martin, *Clean Architecture*, Prentice Hall, 2017.
- Phase 4.1, Documents 03, 04 — Module decomposition and data flow.
- Phase 3.4 — Geometry Engine specification.
- Phase 2.6 — SEM Physics Engine specification.
