# Canonical Data Objects

**Research Phase:** 4.2
**Document:** 03_canonical_data_objects.md
**Date:** 2026-07-30

---

## 1. Data Object Principles

| Principle | Description |
|---|---|
| **Immutability** | Once created, data objects are never modified. Transformations produce new objects. |
| **Explicit ownership** | Each object has exactly one owner at any time. Ownership is transferred, not shared. |
| **Semantic typing** | Fields carry their physical meaning, not just raw types. A `HeightField` is not just a 2D array — it is a 2D array of heights in nm. |
| **Completeness** | Objects carry all the information needed for their role. No hidden dependencies on global state. |
| **Valid at creation** | Objects are validated upon construction. An object that exists is guaranteed to be internally consistent. |

---

## 2. Data Object Catalog

### 2.1 Object D1: Config

| Field | Type | Required | Description |
|---|---|---|---|
| version | Semantic version string | Yes | Schema version for backward compatibility |
| global | Nested struct | Yes | Seed, output directory, log level |
| structure | Nested struct | Yes | Type, parameters, variability config |
| geometry | Nested struct | Yes | Image dimensions, pixel size, process overrides |
| physics | Nested struct | Yes | Beam, detector, degradation config |
| dataset | Nested struct | No | Output format, ground truth inclusion |
| validation | Nested struct | No | Validation flags and tolerances |

**Immutability:** Full — never modified after creation.
**Validated by:** M9 Config Parser.
**Used by:** M10 Pipeline Controller (top-level), all modules (relevant subsections).

### 2.2 Object D2: GDSII Path Reference

| Field | Type | Required | Description |
|---|---|---|---|
| file_path | String | Yes | Path to GDSII file on disk |
| layer_number | Integer (uint32) | Yes | GDSII layer number to rasterize |
| field_center_x | Float (nm) | No | FOV center X (default: 0 = center of layout) |
| field_center_y | Float (nm) | No | FOV center Y |

**Immutability:** Full.
**Validated by:** M1 Rasterizer.
**Produced by:** Config.Structure.

### 2.3 Object D3: PixelMask

| Field | Type | Required | Description |
|---|---|---|---|
| data | 2D [M×N] uint8 | Yes | 0 = no feature, 1 = feature present |
| m | Integer | Yes | Number of rows (height in pixels) |
| n | Integer | Yes | Number of columns (width in pixels) |
| pixel_size_nm | Float | Yes | Pixel spacing in nm |
| layer_number | Integer | Yes | Source GDSII layer |

**Properties:**
- Coordinate system: Y axis = row index (fast scan = X), origin at top-left
- Anti-aliased values in [0, 1] at sub-pixel edges
- Total pixel count = M × N

**Immutability:** Full.
**Produced by:** M1 GDSII Rasterizer.
**Consumed by:** M2 Process Model.

### 2.4 Object D4: LayerStack

| Field | Type | Required | Description |
|---|---|---|---|
| layers | Array of LayerEntry | Yes | Ordered from bottom (index 0) to top |
| total_height_nm | Float | Computed | Sum of all layer thicknesses |

**LayerEntry:**

| Field | Type | Required | Description |
|---|---|---|---|
| name | String | Yes | Human-readable, e.g., "M1_metal" |
| layer_number | Integer (uint32) | Yes | GDSII layer number |
| material_id | Integer (uint8) | Yes | Material ID from frozen table (0–6) |
| thickness_nm | Float | Yes | Deposition thickness (nm) |
| cmp_target_nm | Float | No | CMP target (nm); omitted = no CMP |
| sidewall_angle_deg | Float | No | Etch sidewall angle (default: 87°) |
| cd_bias_nm | Float | No | CD bias (default: 2 nm) |
| corner_radius_nm | Float | No | Bottom corner radius (default: 5 nm) |
| conformality | Enum | No | "conformal", "bottom_up", "pvd" (default: conformal) |
| resist_thickness_nm | Float | No | Lithography resist thickness (default: 150 nm) |
| resist_angle_deg | Float | No | Resist sidewall angle (default: 87°) |

**Immutability:** Full.
**Produced by:** Config → Structure resolution.
**Consumed by:** M2 Process Model.

### 2.5 Object D5: HeightField

| Field | Type | Required | Description |
|---|---|---|---|
| data | 2D [M×N] float64 | Yes | Height at each pixel (nm) |
| m | Integer | Yes | Number of rows |
| n | Integer | Yes | Number of columns |
| pixel_size_nm | Float | Yes | Pixel spacing |
| min_height_nm | Float | Computed | Minimum Z value |
| max_height_nm | Float | Computed | Maximum Z value |

**Properties:**
- Substrate = 0 nm reference
- Positive Z = upward from substrate
- Single-valued (no overhangs) — guaranteed by 2.5D representation
- NaN forbidden — each pixel has a defined height

**Immutability:** Full.
**Variants:** `HeightField_det` (deterministic), `HeightField_var` (with variability applied).
**Produced by:** M2 Process Model (det), M3 Variability Engine (var).
**Consumed by:** M3, M4 Signal Generator, M7 Ground Truth Generator.

### 2.6 Object D6: MaterialMap

| Field | Type | Required | Description |
|---|---|---|---|
| data | 2D [M×N] uint8 | Yes | Material ID at each pixel |
| m | Integer | Yes | Number of rows |
| n | Integer | Yes | Number of columns |
| pixel_size_nm | Float | Yes | Pixel spacing |
| material_ids | Array of uint8 | Computed | Unique IDs present in the map |

**Material ID encoding (frozen):**
| ID | Material |
|---|---|
| 0 | Vacuum |
| 1 | Silicon |
| 2 | Silicon Dioxide |
| 3 | Silicon Nitride |
| 4 | Copper |
| 5 | Tungsten |
| 6 | Photoresist |
| 7+ | Reserved |

**Constraint:** Dimensions must match the corresponding HeightField exactly (same M, N, pixel_size_nm).

**Immutability:** Full.
**Variants:** `MaterialMap_det`, `MaterialMap_var`.
**Produced by:** M2 Process Model, M3 Variability Engine.
**Consumed by:** M4 Signal Generator, M7 Ground Truth Generator.

### 2.7 Object D7: YieldMaps

| Field | Type | Required | Description |
|---|---|---|---|
| se_yield | 2D [M×N] float64 | Yes | Secondary electron yield (e⁻ per incident e⁻) |
| bse_yield | 2D [M×N] float64 | Yes | Backscattered electron yield (e⁻ per incident e⁻) |
| m | Integer | Yes | Number of rows |
| n | Integer | Yes | Number of columns |
| pixel_size_nm | Float | Yes | Pixel spacing |
| beam_energy_keV | Float | Yes | Beam energy used for computation |

**Properties:**
- All values ≥ 0 (valid yield)
- Units: electrons per incident electron (dimensionless)
- se_yield + bse_yield ≤ total yield (typically 0.1–2.0 for SE, 0.1–0.5 for BSE)

**Immutability:** Full.
**Variant:** `YieldMaps_degraded` (after PSF/noise).
**Produced by:** M4 Signal Generator, M5 Degradation Model.
**Consumed by:** M5, M6 Image Former.

### 2.8 Object D8: SEMImage

| Field | Type | Required | Description |
|---|---|---|---|
| data | 2D [M×N] uint16 | Yes | Digitized pixel intensities |
| m | Integer | Yes | Number of rows |
| n | Integer | Yes | Number of columns |
| pixel_size_nm | Float | Yes | Pixel spacing |
| bit_depth | Integer | Yes | 8 or 16 |
| max_digital_value | Integer | Computed | Maximum possible value (2^bit_depth − 1) |
| applied_gain | Float | No | Detector gain used |
| applied_offset | Float | No | Detector offset used |
| saturation_fraction | Float | Computed | Fraction of pixels at max value (>0.1 → warning) |

**Properties:**
- 0 = black (minimum signal), max_value = white (saturation)
- Linear mapping from yield to digital count (after gain/offset)

**Immutability:** Full.
**Produced by:** M6 Image Former.
**Consumed by:** M8 Dataset Writer.

### 2.9 Object D9: GroundTruth

| Field | Type | Required | Description |
|---|---|---|---|
| edge_position_maps | 2D [M×N] float64 | Yes | Signed distance to nearest edge (nm); 0 = on edge, >0 = outside feature, <0 = inside feature |
| cd_values | Dict | No | Keyed by feature index: `{cd_top_nm, cd_bottom_nm, height_nm}` |
| material_segmentation | 2D [M×N] uint8 | No | Pixel-wise material ID (same as MaterialMap) |
| contour_lines | Array of {feature_id, x_nm[], y_nm[]} | No | Edge contours as ordered point sequences |
| edge_type | 2D [M×N] uint8 | No | 0 = no edge, 1 = top edge, 2 = bottom edge, 3 = boundary edge |
| structure_type | String | Yes | Type of structure (from library: "iso_line", "contact", etc.) |

**Immutability:** Full.
**Produced by:** M7 Ground Truth Generator.
**Consumed by:** M8 Dataset Writer.

### 2.10 Object D10: Metadata

| Field | Type | Required | Description |
|---|---|---|---|
| structure_name | String | Yes | Structure identifier, e.g., "iso_line_cd50nm" |
| parameters | Dict | Yes | All generation parameters (flattened) |
| seed | Integer | Yes | Master random seed |
| ler_3sigma_nm | Float | No | Applied LER (if variability enabled) |
| ler_xi_nm | Float | No | LER correlation length |
| overlay_x_nm | Float | No | Applied overlay shift X |
| overlay_y_nm | Float | No | Applied overlay shift Y |
| geometry_version | String | No | Geometry Engine version |
| physics_version | String | No | Physics Engine version |
| generation_timestamp | String (ISO 8601) | Yes | When the image was generated |
| pipeline_duration_ms | Float | No | Total pipeline execution time |
| warnings | Array of String | No | Warnings encountered during generation |

**Immutability:** Full.
**Produced by:** M10 Pipeline Controller (accumulated from all stages).
**Consumed by:** M8 Dataset Writer.

---

## 3. Data Object Relationships

```
         ┌──────────┐
         │  Config  │  (D1) — governs every other object
         └────┬─────┘
              │
              ▼
         ┌──────────┐
         │ GDSIIRef │  (D2) — points to source file
         └────┬─────┘
              │
              ▼
         ┌──────────┐     ┌────────────┐
         │PixelMask │────▶│ LayerStack │  (D3, D4)
         └────┬─────┘     └────────────┘
              │
              ▼
     ┌───────────────┐
     │ HeightField   │  ─┐
     │ MaterialMap   │    ├── (D5, D6) — core geometry
     └───────┬───────┘  ─┘
             │
             ▼
     ┌───────────────┐
     │  YieldMaps    │  (D7) — physics signal
     └───────┬───────┘
             │
             ▼
     ┌───────────────┐     ┌──────────────┐
     │  SEMImage     │     │ GroundTruth  │  (D8, D9)
     └───────┬───────┘     └──────┬───────┘
             │                    │
             ▼                    │
     ┌───────────────┐            │
     │   Metadata    │◄───────────┘  (D10)
     └───────┬───────┘
             │
             ▼
         Files on Disk
```

---

## Sources

- Phase 4.1, Document 04 — Data flow architecture.
- Phase 3.1 — Geometry representation.
- Phase 2.6 — SEM Physics Engine interface.
- [I1] C. Larman, *Applying UML and Patterns*, Prentice Hall, 2004.
- [I4] M. Fowler, *Analysis Patterns: Reusable Object Models*, Addison-Wesley, 1997.
