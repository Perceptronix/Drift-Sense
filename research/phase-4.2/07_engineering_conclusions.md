# Engineering Conclusions

**Research Phase:** 4.2
**Document:** 07_engineering_conclusions.md
**Date:** 2026-07-30

---

## 1. Frozen Module Interfaces

| Interface ID | Module | Inputs | Outputs | Preconditions | Postconditions |
|---|---|---|---|---|---|
| **I1** | GDSII Rasterizer | GDSII file path, layer, dims | PixelMask (D3) | 5 preconditions | 5 postconditions |
| **I2** | Process Model | PixelMask, LayerStack, ProcessConfig | HeightField_det (D5), MaterialMap_det (D6) | 6 preconditions | 6 postconditions |
| **I3** | Variability Engine | HeightField_det, MaterialMap_det, VarConfig | HeightField_var (D5), MaterialMap_var (D6) | 5 preconditions | 6 postconditions |
| **I4** | Signal Generator | HeightField_var, MaterialMap_var, PhysicsConfig | YieldMaps (D7) | 4 preconditions | 4 postconditions |
| **I5** | Degradation Model | YieldMaps, DegradationConfig | YieldMaps_degraded (D7) | 3 preconditions | 4 postconditions |
| **I6** | Image Former | YieldMaps_degraded, DetectorConfig | SEMImage (D8) | 3 preconditions | 3 postconditions |
| **I7** | Ground Truth Gen. | HeightField_var, MaterialMap_var, GTConfig | GroundTruth (D9) | 2 preconditions | 3 postconditions |
| **I8** | Dataset Writer | SEMImage, GroundTruth, Metadata, DatasetConfig | Files on disk | 3 preconditions | 4 postconditions |

---

## 2. Frozen Canonical Data Objects

| Object ID | Name | Key Fields | Validated By | Consumed By |
|---|---|---|---|---|
| **D1** | Config | version, global, structure, geometry, physics, dataset | M9 Config Parser | All modules |
| **D2** | GDSII Reference | file_path, layer_number, field_center | M1 Rasterizer | M1 |
| **D3** | PixelMask | data, M, N, pixel_size_nm | M1 | M2 |
| **D4** | LayerStack | layers[material, thickness, sidewall, ...] | Config + library | M2 |
| **D5** | HeightField | data[m][n] float64, M, N, pixel_size_nm | M2, M3 | M3, M4, M7 |
| **D6** | MaterialMap | data[m][n] uint8, M, N, pixel_size_nm | M2, M3 | M4, M7 |
| **D7** | YieldMaps | se_yield, bse_yield, M, N | M4 | M5, M6 |
| **D8** | SEMImage | data[m][n] uint16, bit_depth, gain | M6 | M8 |
| **D9** | GroundTruth | edge_maps, cd_values, segmentation, contours | M7 | M8 |
| **D10** | Metadata | parameters, seed, timestamp, version | Pipeline | M8 |

---

## 3. Frozen Configuration Model

| Section | Purpose | Required Keys | Optional Keys |
|---|---|---|---|
| **Version** | Schema compatibility | version | — |
| **Global** | Seed, output, logging | seed, output_directory | log_level, structure_name |
| **Structure** | What to generate | type, parameters | variability {ler, overlay, seed} |
| **Geometry** | Image resolution, process params | image_width_pixels, image_height_pixels, pixel_size_nm | process_model {angle, bias, radii} |
| **Physics** | Beam, signal, degradation | beam_energy_keV, probe_current_pA | signal_model, degradation, detector |
| **Dataset** | Output format, GT inclusion | — | output_format, include_ground_truth, compress |

---

## 4. Frozen Error Model

| Error Category | Severity | Examples | Reporting |
|---|---|---|---|
| Configuration | **Fatal** | Missing key, unknown key, invalid type | Error message + exit code 1 |
| Input | **Fatal** | File not found, layer not found | Error message + exit |
| Domain | **Fatal** | NaN in height field, material ID not in library | Error message + pipeline abort |
| Runtime | **Error** | RNG failure, write failure, disk full | Error message + retry/fail |
| Validation | **Warning** | LER exceeds 50% of CD, unknown config keys | Warning printed, pipeline continues |
| Recoverable | **Warning** | Slight saturation in image, minor clipping | Warning recorded in Metadata |

---

## 5. Frozen Validation Levels

| Level | Scope | When | Cost |
|---|---|---|---|
| **L1 Schema** | Required fields, types, enums | Config parse | < 1 μs |
| **L2 Range** | Value bounds (numeric, array) | Module entry | < 10 μs |
| **L3 Consistency** | Cross-field invariants | Module entry | < 1 μs |
| **L4 Unit** | Unit correctness | Module boundary | < 1 μs |
| **L5 Regression** | Determinism, CD accuracy | Post-generation | 1–100 ms (optional) |

---

## 6. Frozen Contract Summary

| Aspect | Status | Reference |
|---|---|---|
| Module interfaces (10 modules) | ✅ Frozen | Document 02 |
| Canonical data objects (10 objects) | ✅ Frozen | Document 03 |
| Interface contracts (8 interfaces) | ✅ Frozen | Document 04 |
| Configuration model (6 sections) | ✅ Frozen | Document 05 |
| Error model (6 categories) | ✅ Frozen | Document 07 |
| Validation strategy (5 levels) | ✅ Frozen | Document 06 |

**15 engineering decisions frozen in this phase.**

---

## Sources

- Phase 4.1, Documents 03, 05, 07 — Module decomposition, layered architecture, engineering conclusions.
- Phase 3.4 — Geometry Engine specification.
- Phase 2.6 — SEM Physics Engine specification.
- [I1] C. Larman, *Applying UML and Patterns*, Prentice Hall, 2004.
- [I2] B. Meyer, *Object-Oriented Software Construction*, Prentice Hall, 1997.
- [I3] R. C. Martin, *Clean Architecture*, Prentice Hall, 2017.
