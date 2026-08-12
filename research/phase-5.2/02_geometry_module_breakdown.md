# Geometry Module Breakdown

**Research Phase:** 5.2
**Document:** 02_geometry_module_breakdown.md
**Date:** 2026-07-30

---

## 1. Module Hierarchy

The Geometry Engine's three public interfaces (I1–I3) are implemented by three public modules, internally decomposed into 8 implementation modules:

```
semicon.geometry
│
├── raster.py          ← PUBLIC: geo_raster (I1 producer)
│   ├── gdsii_reader.py       (internal)
│   ├── polygon_rasterizer.py (internal)
│   └── mask_builder.py       (internal)
│
├── process.py         ← PUBLIC: geo_process (I2 producer)
│   ├── layer_stack.py        (internal)
│   ├── deposition.py         (internal)
│   ├── lithography.py        (internal)
│   ├── etch.py               (internal)
│   ├── cmp.py                (internal)
│   ├── corner_rounding.py    (internal)
│   └── heightfield_gen.py    (internal)
│
└── variability.py     ← PUBLIC: geo_variability (I3 producer)
    ├── edge_detector.py      (internal)
    ├── ler_generator.py      (internal)
    ├── overlay_engine.py     (internal)
    ├── cdu_engine.py         (internal)
    └── variability_applier.py (internal)
```

---

## 2. geo_raster (M1) Internal Modules

### 2.1 gdsii_reader

| Aspect | Specification |
|---|---|
| **Responsibility** | Read GDSII file; extract polygons, paths, SREF, AREF; resolve cell references; convert to unified polygon list in physical units (µm → nm) |
| **Inputs** | GDSII file path, layer number |
| **Outputs** | `list[Polygon]` where Polygon = array of (x_nm, y_nm) vertices; polygons per requested layer only |
| **Dependencies** | gdspy library; semicon.foundation.units |
| **Validation strategy** | Unit tests: known GDSII files → expected polygon counts/areas; error cases (missing file, missing layer, empty layer) |

**Key detail:** The reader must resolve hierarchical references (SREF/AREF recursion) and flatten the tree so the rasterizer only ever sees leaf polygons. Cell explosion is handled by visited-cell memoization.

### 2.2 polygon_rasterizer

| Aspect | Specification |
|---|---|
| **Responsibility** | Rasterize a list of polygons onto an M×N grid at pixel_size_nm, producing a fractional coverage mask (anti-aliased) |
| **Inputs** | `list[Polygon]` (nm), M, N, pixel_size_nm, origin_nm |
| **Outputs** | `np.ndarray[M, N] float32` — coverage fraction per pixel ∈ [0, 1] |
| **Dependencies** | numpy; semicon.foundation.math_utils |
| **Validation strategy** | Golden reference: rasterize a known square → exact coverage map; property tests: coverage total = polygon area / pixel area ± tolerance; translation invariance |

**Algorithm (frozen as implementation decision):** Edge-function scanline fill with 8×8 sub-pixel supersampling per pixel. For each pixel, count sub-samples inside polygon → coverage = count/64. Handles concave polygons, holes (even-odd rule), self-intersections (clip).

### 2.3 mask_builder

| Aspect | Specification |
|---|---|
| **Responsibility** | Combine reader + rasterizer into the I1 contract: GDSII → PixelMask (M×N uint8, 0/1). Applies thresholding (coverage ≥ 0.5 → 1), FOV selection, dimension validation |
| **Inputs** | GDSII path, layer, M, N, pixel_size_nm, field_center_nm (optional) |
| **Outputs** | `PixelMask` (M×N uint8 ∈ {0,1}); ValidationRecord (coverage stats, polygon count) |
| **Dependencies** | gdsii_reader, polygon_rasterizer |
| **Validation strategy** | I1 interface test: pixel_size, dimensions, values ∈ {0,1}; golden structures (line, contact, dense array) |

---

## 3. geo_process (M2) Internal Modules

### 3.1 layer_stack

| Aspect | Specification |
|---|---|
| **Responsibility** | Resolve LayerStack spec (D4) into an ordered processing plan: materials, thicknesses, order; validate against material library |
| **Inputs** | LayerStack (list of layer specs), MaterialLibrary |
| **Outputs** | `ProcessPlan` — ordered list of (operation, params) to execute |
| **Dependencies** | semicon.config; semicon.foundation.units |
| **Validation strategy** | Unit tests: valid stack → plan; unknown material → error; zero thickness → error |

### 3.2 deposition

| Aspect | Specification |
|---|---|
| **Responsibility** | Model conformal, isotropic (PVD), and bottom-up deposition onto current topography |
| **Inputs** | Current HeightField (2.5D), deposition params (thickness, conformality ∈ [0,1], material_id) |
| **Outputs** | Updated HeightField, updated MaterialMap |
| **Dependencies** | scipy.ndimage; semicon.foundation.math_utils |
| **Validation strategy** | Conformal: known trench → conformal thickness on walls; PVD: known trench → fill fraction per conformality |

**Algorithm:** Conformal deposition = grow topography by thickness t along surface normal. For 2.5D height field: `H_new = max(H, t − distance_to_mask_region)` implemented via Chebyshev distance transform on the mask → isosurface offset. PVD: partial fill where fill_height = conformality × t within exposed regions.

### 3.3 lithography

| Aspect | Specification |
|---|---|
| **Responsibility** | Apply lithographic patterning: CD bias, resist profile on top surface |
| **Inputs** | Current HeightField, PixelMask (pattern), litho params (cd_bias_nm, resist_thickness_nm) |
| **Outputs** | Updated HeightField (patterned resist), MaterialMap (resist ID where patterned) |
| **Dependencies** | polygon_rasterizer (reuse for bias), scipy.ndimage |
| **Validation strategy** | CD bias: measured top CD = configured CD + bias ± 0.1 nm |

### 3.4 etch

| Aspect | Specification |
|---|---|
| **Responsibility** | Model anisotropic (vertical/angled) and isotropic etch through masked layers; synthesizes trapezoidal sidewall profile |
| **Inputs** | Current HeightField, MaterialMap, Mask, etch params (sidewall_angle_deg ∈ [80°, 90°], depth_nm, iso_bias_nm) |
| **Outputs** | Updated HeightField (with sidewalls), updated MaterialMap |
| **Dependencies** | scipy.ndimage; semicon.foundation.math_utils |
| **Validation strategy** | Trapezoid: cross-section matches top/bottom CD from sidewall angle within 0.1 nm; vertical etch: sidewall = 90° |

**Algorithm (sidewall synthesis):** For each pixel at the mask edge, the height decreases linearly from top_CD edge to bottom_CD edge over a horizontal run `Δx = depth / tan(angle)`. The etch front propagates downward, carving a trapezoid: `bottom_CD = top_CD + 2 × depth / tan(angle)` for a line. Implemented by per-column trapezoid rasterization into the height field.

### 3.5 cmp

| Aspect | Specification |
|---|---|
| **Responsibility** | Planarize topography to a target height with optional over-polish; models global and local planarization |
| **Inputs** | Current HeightField, cmp params (target_height_nm, over_polish_nm, planarization_window_px) |
| **Outputs** | Updated HeightField (planar top surface), updated MaterialMap |
| **Dependencies** | scipy.ndimage (uniform_filter for local polish window) |
| **Validation strategy** | Planar region: height = target ± 0.1 nm; over-polish: material removal below target |

**Algorithm:** Global CMP = clip all heights above target to target. Local polish = moving-average erosion within window, then clip. Over-polish reduces target by over_polish_nm.

### 3.6 corner_rounding

| Aspect | Specification |
|---|---|
| **Responsibility** | Apply top and bottom corner radius via distance-field sculpting |
| **Inputs** | HeightField, MaterialMap, corner params (top_radius_nm, bottom_radius_nm) |
| **Outputs** | Updated HeightField |
| **Dependencies** | scipy.ndimage (distance_transform_edt) |
| **Validation strategy** | Corner curvature radius matches configured radius ± 0.2 nm |

**Algorithm:** Signed distance transform of the material mask; heights near corners are reduced where distance_to_corner < radius, following a quarter-circle fillet in the corner profile.

### 3.7 heightfield_gen

| Aspect | Specification |
|---|---|
| **Responsibility** | Execute the ProcessPlan in order; assemble final HeightField_det + MaterialMap_det; validate I2 postconditions |
| **Inputs** | PixelMask, LayerStack, ProcessConfig |
| **Outputs** | `HeightField_det` (M×N float64 nm), `MaterialMap_det` (M×N uint8) |
| **Dependencies** | All geo_process internals; orchestration of the plan |
| **Validation strategy** | I2 interface test: dimensions, finite values, material IDs ∈ {0..6}, trapezoid invariant (top_CD ≤ bottom_CD) |

---

## 4. geo_variability (M3) Internal Modules

### 4.1 edge_detector

| Aspect | Specification |
|---|---|
| **Responsibility** | Locate feature edges on the height field via gradient magnitude; classify top/bottom/boundary edges; produce per-edge pixel sets for displacement |
| **Inputs** | HeightField_var input (or det), MaterialMap |
| **Outputs** | Edge maps: binary edge mask, edge orientation (dx, dy), per-edge connected components |
| **Dependencies** | scipy.ndimage (sobel/laplace); semicon.foundation.math_utils |
| **Validation strategy** | Known line → detected edges at expected positions ± 1 px; orientation correct |

### 4.2 ler_generator

| Aspect | Specification |
|---|---|
| **Responsibility** | Generate LER displacement fields along line edges using 1D Gaussian random fields with exponential ACF (frozen spec: LER 3σ, ξ, ρ) |
| **Inputs** | Edge pixel sets, edge orientation, LER params (3σ_nm, ξ_nm, ρ), seed (from rng_utils chain) |
| **Outputs** | Per-edge normal displacement array (nm per edge point) |
| **Dependencies** | semicon.foundation.rng_utils (Gaussian random field), numpy.fft |
| **Validation strategy** | Measured 3σ = configured ± 0.3 nm; measured ξ = configured ± 10%; left–right correlation = ρ ± 0.05; mean displacement ≈ 0 |

**Algorithm:** Spectral synthesis. For a line edge of length L sampled at pixel spacing, build PSD from exponential ACF, populate FFT coefficients from seeded RNG (rng_utils), inverse-transform → correlated Gaussian profile. Apply same field to both left/right edges with correlation ρ.

### 4.3 overlay_engine

| Aspect | Specification |
|---|---|
| **Responsibility** | Apply translational overlay shift to the entire topography |
| **Inputs** | HeightField, MaterialMap, overlay params (dx_nm, dy_nm sampled per structure), seed |
| **Outputs** | Shifted HeightField, shifted MaterialMap |
| **Dependencies** | scipy.ndimage.shift (spline_order=1) |
| **Validation strategy** | Shift magnitude = configured ± 0.1 nm; edge positions moved by exact shift |

**Implementation decision:** Overlay is applied as a single integer+subpixel translation via separable interpolation. Sub-pixel shifts use bilinear (order-1) spline to preserve determinism.

### 4.4 cdu_engine

| Aspect | Specification |
|---|---|
| **Responsibility** | Apply CD variation (CDU): sample per-structure CD bias from seeded normal distribution and rescale edge positions |
| **Inputs** | HeightField, CDU params (sigma_nm), seed |
| **Outputs** | Rescaled HeightField (uniform CD change) |
| **Dependencies** | rng_utils |
| **Validation strategy** | CD spread across batch = configured sigma ± 0.1 nm |

### 4.5 variability_applier

| Aspect | Specification |
|---|---|
| **Responsibility** | Assemble all variability operations in order; update material map at edge pixels; validate I3 postconditions |
| **Inputs** | HeightField_det, MaterialMap_det, VariabilityConfig, seed chain |
| **Outputs** | `HeightField_var`, `MaterialMap_var`, `VariabilityRecord` |
| **Dependencies** | All geo_variability internals |
| **Validation strategy** | I3 interface test: dimensions preserved; LER measured on output; mean CD unbiased; material IDs valid |

**Variability application order (frozen as implementation decision):**
```
1. CDU (global CD bias)
2. LER (per-edge displacement)
3. Sidewall angle variation (if enabled)
4. Overlay (translational shift) — last, so it moves everything consistently
```

---

## 5. Module Dependency Graph

```
geo_raster
├── gdsii_reader → polygon_rasterizer → mask_builder (public I1)

geo_process
└── layer_stack → [deposition → lithography → etch → cmp → corner_rounding]
    → heightfield_gen (public I2)

geo_variability
├── edge_detector → ler_generator
├── cdu_engine
└── overlay_engine
    → variability_applier (public I3)
```

All modules depend on Foundation (math_utils, rng_utils, units, image_io). geo_raster and geo_process are strictly upstream of geo_variability.

---

## 6. Validation Responsibility Map

| Gate | Who Tests | What |
|---|---|---|
| **L0 unit** | Internal module owner | Each internal module on synthetic inputs |
| **L1 module** | Module lead | Public API: raster/process/variability satisfy their interface contract |
| **L2 interface** | Module leads (pair) | I1, I2, I3 cross-module data passing |
| **L3 pipeline** | Integration lead | End-to-end geometry: GDSII → HeightField_var |
| **L4 scientific** | Scientific lead | LER statistics, CD accuracy, trapezoid fidelity |

---

## Sources

- Phase 3.1 — Geometry representation.
- Phase 3.2 — Process model (deposition, litho, etch, CMP).
- Phase 3.3 — Manufacturing variability (LER, CDU, overlay).
- Phase 3.4 — Geometry Engine certification.
- Phase 4.2 — Interfaces I1, I2, I3 contracts.
