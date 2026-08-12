# Module Interface Inventory

**Research Phase:** 4.2
**Document:** 02_module_interface_inventory.md
**Date:** 2026-07-30

---

## 1. Module Index

All 10 modules from Phase 4.1 are inventoried with their complete interface specifications.

| Module ID | Module Name | Subsystem | Interface ID |
|---|---|---|---|
| M1 | GDSII Rasterizer | Geometry | I1 |
| M2 | Process Model | Geometry | I2 |
| M3 | Variability Engine | Geometry | I3 |
| M4 | Signal Generator | Physics | I4 |
| M5 | Degradation Model | Physics | I5 |
| M6 | Image Former | Physics | I6 |
| M7 | Ground Truth Generator | Dataset | I7 |
| M8 | Dataset Writer | Dataset | I8 |
| M9 | Config Parser | Configuration | C1 |
| M10 | Pipeline Controller | Orchestration | — |

---

## 2. Module Specifications

### 2.1 Module M1: GDSII Rasterizer

| Aspect | Specification |
|---|---|
| **Purpose** | Convert GDSII layout polygons into a binary pixel mask for one layer |
| **Inputs** | GDSII file path; layer number (int); rasterization resolution (M×N, pixels); pixel size (nm); field of view center (x, y, nm) — optional |
| **Outputs** | PixelMask (M×N, uint8: 0 = no feature, 1 = feature present) |
| **Depends on** | GDSII file format parser; Phase 4.1 L2 Foundation: math_utils |
| **Dependencies (internal)** | Polygon-to-pixel rasterization; anti-aliasing kernel |
| **Error conditions** | GDSII file not found → fatal; layer number not in file → fatal; polygon exceeds field of view → warning (clip or error as configured) |
| **Performance expectation** | <100 ms for typical layout region at 1024×1024 |
| **Boundary behavior** | Sub-pixel edge positions are anti-aliased to prevent systematic CD bias |
| **Side effects** | None (stateless) |
| **Determinism** | Deterministic for same GDSII file and parameters |

### 2.2 Module M2: Process Model

| Aspect | Specification |
|---|---|
| **Purpose** | Apply semiconductor process steps to generate deterministic 2.5D geometry from a pixel mask |
| **Inputs** | PixelMask; LayerStack (ordered list of layers with materials, thicknesses, sidewall angles, CD bias, corner radii); ProcessModelConfig (deposition type, etch type, CMP target heights) |
| **Outputs** | HeightField_det (M×N, float64, nm); MaterialMap_det (M×N, uint8, material IDs) |
| **Depends on** | Phase 4.1 L2 Foundation: math_utils (interpolation, distance transform) |
| **Dependencies (internal)** | Conformal deposition geometry; trapezoidal profile generation; corner rounding; CMP clipping |
| **Error conditions** | Layer stack empty → fatal; invalid material ID → fatal; thickness ≤ 0 → fatal; sidewall angle outside [80°, 90°] → warning (clamped) |
| **Performance expectation** | <500 ms per layer at 1024×1024 |
| **Boundary behavior** | Etch depth may exceed deposited thickness → warning; CMP target may be below feature bottom → error |
| **Side effects** | None (stateless) |
| **Determinism** | Fully deterministic for given inputs and parameters |

### 2.3 Module M3: Variability Engine

| Aspect | Specification |
|---|---|
| **Purpose** | Apply manufacturing variability to deterministic geometry — LER, CDU, overlay, shape variation |
| **Inputs** | HeightField_det; MaterialMap_det; VariabilityConfig (LER 3σ, correlation length ξ, left–right correlation ρ, overlay σ, sidewall angle σ, thickness σ, seed); StructureSpec (for feature identification) |
| **Outputs** | HeightField_var (M×N, float64, nm); MaterialMap_var (M×N, uint8) |
| **Depends on** | Phase 4.1 L2 Foundation: rng_utils; math_utils (convolution, edge detection) |
| **Dependencies (internal)** | Gaussian random process generation (exponential ACF); feature edge detection; edge displacement; correlated left–right edge generation |
| **Error conditions** | LER 3σ > 0.5 × minimum CD → warning (edges may cross); random seed = 0 → warning (fallback to system RNG); overlay σ > 0.1 × FOV → warning |
| **Performance expectation** | <2 s at 1024×1024 for moderate feature count; O(N_lines × M_filter) for LER |
| **Boundary behavior** | LER clamped to prevent edge crossing; overlay shift may crop features at image boundary → warning |
| **Side effects** | RNG state consumed (must be seeded externally for reproducibility) |
| **Determinism** | Deterministic for given seed and parameters |

### 2.4 Module M4: Signal Generator

| Aspect | Specification |
|---|---|
| **Purpose** | Compute per-pixel SE and BSE yield from geometry and material |
| **Inputs** | HeightField_var; MaterialMap_var; PhysicsConfig (beam energy keV, probe current pA, material property table, SE yield model selection, charging model parameters) |
| **Outputs** | YieldMaps: se_yield (M×N, float64), bse_yield (M×N, float64) |
| **Depends on** | Phase 4.1 L2 Foundation: math_utils (gradient computation); Material library (δ₀, η, escape depth per material) |
| **Dependencies (internal)** | Surface normal computation; topographic contrast (secθ); material contrast; edge brightening; charging modulation |
| **Error conditions** | Unknown material ID → fatal; beam energy outside material property table range → warning (extrapolation); negative yield → warning (clamped to 0) |
| **Performance expectation** | <200 ms at 1024×1024 |
| **Boundary behavior** | Edge brightening width characteristic of escape depth; charging model valid only for isolated structures |
| **Side effects** | None (stateless) |
| **Determinism** | Deterministic for same inputs and beam parameters |

### 2.5 Module M5: Degradation Model

| Aspect | Specification |
|---|---|
| **Purpose** | Apply PSF convolution, noise, and charging degradation to ideal yield maps |
| **Inputs** | YieldMaps (se_yield, bse_yield); DegradationConfig (probe diameter nm, PSF model, enable_shot_noise, enable_detector_noise, enable_charging, seed); SEMConfig (scan parameters if beam degradation model) |
| **Outputs** | YieldMaps_degraded: se_yield_degraded (M×N, float64), bse_yield_degraded (M×N, float64) |
| **Depends on** | Phase 4.1 L2 Foundation: rng_utils, math_utils (convolution) |
| **Dependencies (internal)** | PSF kernel generation (Gaussian); image convolution; Poisson noise generator; Gaussian detector noise; charging blur |
| **Error conditions** | Probe diameter ≤ 0 → fatal; PSF kernel larger than image → warning (performance impact); noise seed = 0 → warning |
| **Performance expectation** | <500 ms at 1024×1024 (FFT convolution for large PSF); O(M×N×K²) for spatial convolution with small kernel |
| **Boundary behavior** | PSF convolution: edges padded via reflection; negative noise values → clamped to 0 |
| **Side effects** | RNG state consumed |
| **Determinism** | Deterministic for given seed and parameters |

### 2.6 Module M6: Image Former

| Aspect | Specification |
|---|---|
| **Purpose** | Convert physical yield signal to digitized SEM image |
| **Inputs** | YieldMaps_degraded; DetectorConfig (gain, offset, saturation_level, bit_depth, detector_efficiency_map — optional) |
| **Outputs** | SEMImage (M×N, uint16): digitized pixel intensities; metadata: applied_gain, applied_offset, bit_depth, saturation_fraction |
| **Depends on** | Phase 4.1 L2 Foundation: math_utils (scaling) |
| **Dependencies (internal)** | Signal scaling; gain/offset application; saturation/clipping; digitization; optional shading correction |
| **Error conditions** | Gain ≤ 0 → fatal; bit_depth not in {8, 16} → error; saturation_fraction > 0.1 → warning (image may be overexposed) |
| **Performance expectation** | <50 ms at 1024×1024 (pure arithmetic) |
| **Boundary behavior** | Saturation = clamp to max DN value; sub-DN values = rounding; negative DN values = clamped to 0 |
| **Side effects** | None (stateless) |
| **Determinism** | Fully deterministic |

### 2.7 Module M7: Ground Truth Generator

| Aspect | Specification |
|---|---|
| **Purpose** | Generate ground-truth labels for metrology algorithm training and evaluation |
| **Inputs** | HeightField_var; MaterialMap_var; StructureSpec (feature type, expected CD range, material definitions); GroundTruthConfig (edge_threshold_height nm, include_contours bool, include_segmentation bool, include_cd_values bool) |
| **Outputs** | GroundTruth: edge_position_maps (M×N, float64, nm), cd_values (dict per feature: top_cd, bottom_cd, height), material_segmentation (M×N, uint8), contour_lines (list of (x,y) arrays) |
| **Depends on** | Phase 4.1 L2 Foundation: math_utils (edge detection, line fitting) |
| **Dependencies (internal)** | Height threshold extraction; edge tracing; CD computation; contour extraction |
| **Error conditions** | Edge threshold higher than maximum height → warning (no edges detected); feature type not recognized → fatal |
| **Performance expectation** | <200 ms at 1024×1024 |
| **Boundary behavior** | Edges at image boundary are marked as boundary edges; features partially outside FOV are labeled as partial |
| **Side effects** | None (stateless) |
| **Determinism** | Deterministic for same height field and parameters |

### 2.8 Module M8: Dataset Writer

| Aspect | Specification |
|---|---|
| **Purpose** | Save generated SEM images, ground-truth labels, and metadata to disk in organized directory structure |
| **Inputs** | SEMImage; GroundTruth (optional); Metadata (complete record of parameters, seed, timestamps, version); DatasetConfig (output_format, directory_structure, compression) |
| **Outputs** | Files on disk: image.tiff, ground_truth.json, metadata.json, dataset_index.json |
| **Depends on** | Phase 4.1 L2 Foundation: image_io; Configuration: dataset schema |
| **Dependencies (internal)** | TIFF/PNG encoding; JSON serialization; directory creation; index file management |
| **Error conditions** | Output directory not writable → fatal; disk full → fatal; file write fails → recoverable (retry) |
| **Performance expectation** | <100 ms per image + label write |
| **Boundary behavior** | Overwrite existing files = configured (overwrite or create new); long metadata → truncation warning |
| **Side effects** | Writes files to disk; creates directories; updates dataset index |
| **Determinism** | Deterministic file contents (file timestamps not deterministic) |

### 2.9 Module M9: Config Parser

| Aspect | Specification |
|---|---|
| **Purpose** | Read and validate configuration file, resolve defaults, produce validated Config object |
| **Inputs** | Config file path; optional override parameters (dictionary); optional library directory path |
| **Outputs** | Config (validated, resolved) |
| **Depends on** | YAML/TOML parser library; Structure library files; Material library files; Default parameter files |
| **Dependencies (internal)** | Schema validation; type coercion; default resolution; cross-field validation; library resolution |
| **Error conditions** | File not found → fatal; schema violation → fatal with specific message; type error → fatal; library entry not found → fatal |
| **Performance expectation** | <1 s for typical configuration |
| **Boundary behavior** | Unknown keys → ignored with warning; missing optional keys → replaced with defaults |
| **Side effects** | None (stateless) |
| **Determinism** | Deterministic for same files and keys |

### 2.10 Module M10: Pipeline Controller

| Aspect | Specification |
|---|---|
| **Purpose** | Orchestrate single-pipeline execution: sequence modules M1–M8 in correct order, pass data between them, handle errors, accumulate timing |
| **Inputs** | Config (validated from M9) |
| **Outputs** | Dataset Sample (SEMImage + GroundTruth + Metadata) |
| **Depends on** | M1–M8 (all pipeline modules) |
| **Dependencies (internal)** | Module invocation; data passing (immutable copy or reference); timing recorder; error handler |
| **Error conditions** | Any module failure → pipeline failure with diagnostic trace; missing intermediate data → fatal |
| **Performance expectation** | Pipeline overhead < 10 ms |
| **Boundary behavior** | Non-fatal warnings propagated to metadata; all intermediate data available for debugging |
| **Side effects** | None (calls other modules which may have side effects) |
| **Determinism** | Deterministic if all modules are deterministic (required) |

---

## 3. Interface Summary

| Interface ID | From Module | To Module | Data Crossing |
|---|---|---|---|
| I1 | M9 (Config Parser) | M1 (Rasterizer) | Config.Structure, GDSII path, layer number |
| I2 | M1 (Rasterizer) | M2 (Process Model) | PixelMask, LayerStack, ProcessModelConfig |
| I3 | M2 (Process Model) | M3 (Variability Engine) | HeightField_det, MaterialMap_det, VariabilityConfig |
| I4 | M3 (Variability Engine) | M4 (Signal Generator) | HeightField_var, MaterialMap_var, PhysicsConfig |
| I5 | M4 (Signal Generator) | M5 (Degradation Model) | YieldMaps, DegradationConfig |
| I6 | M5 (Degradation Model) | M6 (Image Former) | YieldMaps_degraded, DetectorConfig |
| I7 | M3 (Variability Engine) | M7 (Ground Truth Gen.) | HeightField_var, MaterialMap_var, GroundTruthConfig |
| I8 | M6 (Image Former) + M7 + Metadata | M8 (Dataset Writer) | SEMImage, GroundTruth, Metadata |

---

## Sources

- Phase 4.1, Document 03 — Module decomposition.
- Phase 3.4 — Geometry Engine specification.
- Phase 2.6 — SEM Physics Engine specification.
- [I1] C. Larman, *Applying UML and Patterns*, Prentice Hall, 2004.
- [I2] B. Meyer, *Object-Oriented Software Construction*, Prentice Hall, 1997.
- [I3] R. C. Martin, *Clean Architecture*, Prentice Hall, 2017.
