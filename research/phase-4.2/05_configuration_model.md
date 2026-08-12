# Configuration Model

**Research Phase:** 4.2
**Document:** 05_configuration_model.md
**Date:** 2026-07-30

---

## 1. Configuration Philosophy

| Principle | Description |
|---|---|
| **Externalized** | All parameters are in configuration files. Code contains no hard-coded values. |
| **Hierarchical** | Configuration is organized by subsystem (global, structure, geometry, physics, dataset). |
| **Self-describing** | Config files carry a version field. Unrecognized keys are warned, not silently ignored. |
| **Minimal required keys** | Sensible defaults for all optional parameters. Users specify only what differs from defaults. |
| **Library-based** | Named structures (from `config/library/`) carry their own default parameters. |
| **Validated at entry** | All configuration is validated before any computation begins. |

---

## 2. Logical Configuration Sections

### 2.1 Section: Version

| Key | Type | Required | Description |
|---|---|---|---|
| **version** | String (semver) | Yes | Schema version, e.g., "1.0.0" |

**Inference:** The version field enables backward compatibility. Future schema changes increment the version.

### 2.2 Section: Global

| Key | Type | Required | Default | Description |
|---|---|---|---|---|
| **seed** | Integer (uint32) | Yes | — | Master random seed. 0 = system entropy (non-reproducible) |
| **output_directory** | String | Yes | — | Path to write output files. Created if not existing |
| **log_level** | Enum | No | "info" | "debug", "info", "warn", "error" |
| **structure_name** | String | No | Auto-generated | Override for output file naming |

**Validation rules:**
- seed ≥ 0 (seed = 0 → warning: non-reproducible)
- output_directory must be writable (validated after parsing)

### 2.3 Section: Structure

| Key | Type | Required | Default | Description |
|---|---|---|---|---|
| **type** | Enum | Yes | — | Structure type from library: "iso_line", "dense_ls", "contact", "via", "trench", "fin", "gate", "sti", "bimaterial", "pitch_std" |
| **parameters** | Dict | Yes | Structure defaults | Structure-specific parameter overrides |
| **parameters.cd_nm** | Float | Conditional | Per structure | Critical dimension (top), nm |
| **parameters.height_nm** | Float | Conditional | Per structure | Feature height, nm |
| **parameters.material** | String or Integer | Conditional | Per structure | Material name or ID |
| **parameters.substrate** | String or Integer | Conditional | "Si" | Substrate material |
| **parameters.pitch_nm** | Float | For arrays | Per structure | Line pitch for dense arrays |
| **parameters.count** | Integer | For arrays | Per structure | Number of lines/features |
| **variability** | Dict (nested) | No | Null | Variability parameters |
| **variability.ler_3sigma_nm** | Float | No | 2.4 | LER 3σ amplitude (nm) |
| **variability.ler_xi_nm** | Float | No | 25.0 | LER correlation length (nm) |
| **variability.ler_rho** | Float | No | 0.3 | LER left–right correlation |
| **variability.overlay_sigma_nm** | Float | No | 0.0 | Overlay translation σ (nm) |
| **variability.sidewall_angle_sigma_deg** | Float | No | 0.0 | Sidewall angle variation σ (°) |
| **variability.include_ler** | Bool | No | true | Master LER toggle |
| **variability.include_cdu** | Bool | No | false | Master CDU toggle |
| **variability.include_overlay** | Bool | No | false | Master overlay toggle |
| **variability.seed** | Integer | No | Global seed | Structure-specific seed override |

**Inference:** Variability defaults are conservative (LER on by default with N5 values; overlay and CDU off by default). Users enable additional effects explicitly.

### 2.4 Section: Geometry

| Key | Type | Required | Default | Description |
|---|---|---|---|---|
| **image_width_pixels** | Integer | Yes | 1024 | Image width (N, columns) |
| **image_height_pixels** | Integer | Yes | 1024 | Image height (M, rows) |
| **pixel_size_nm** | Float | Yes | 1.0 | Pixel spacing |
| **process_model** | Dict (nested) | No | Null | Process model overrides |
| **process_model.sidewall_angle_deg** | Float | No | 87.0 | Main etch sidewall angle |
| **process_model.cd_bias_nm** | Float | No | 2.0 | CD bias |
| **process_model.top_corner_radius_nm** | Float | No | 3.0 | Top corner radius |
| **process_model.bottom_corner_radius_nm** | Float | No | 5.0 | Bottom corner radius |
| **process_model.deposition_type** | Enum | No | "conformal" | "conformal", "bottom_up", "pvd" |

**Validation rules:**
- image_width_pixels ∈ [64, 4096]
- image_height_pixels ∈ [64, 4096]
- pixel_size_nm ∈ (0, 100]
- sidewall_angle_deg ∈ [80, 90]

### 2.5 Section: Physics

| Key | Type | Required | Default | Description |
|---|---|---|---|---|
| **beam_energy_keV** | Float | Yes | — | Primary beam energy |
| **probe_current_pA** | Float | Yes | — | Beam probe current |
| **material_library_path** | String | No | "config/materials/material_library.yml" | Path to material properties |
| **signal_model** | Dict (nested) | No | Default | Signal model selection |
| **signal_model.se_yield_model** | Enum | No | "universal" | SE yield model: "universal", "joy_luo", "experimental" |
| **signal_model.bse_yield_model** | Enum | No | "everhart" | BSE yield model |
| **signal_model.edge_brightening** | Bool | No | true | Enable edge brightening |
| **signal_model.charging** | Bool | No | false | Enable charging model |
| **degradation** | Dict (nested) | No | Disabled | Degradation configuration |
| **degradation.probe_diameter_nm** | Float | No | 0.0 | PSF blur (0 = no blur) |
| **degradation.shot_noise** | Bool | No | false | Enable shot noise |
| **degradation.detector_noise** | Bool | No | false | Enable detector noise |
| **detector** | Dict (nested) | No | Default | Detector configuration |
| **detector.gain** | Float | No | 1.0 | Signal gain |
| **detector.offset** | Float | No | 0.0 | Signal offset |
| **detector.saturation_level** | Float | No | 65535.0 | Saturation (for 16-bit) |
| **detector.bit_depth** | Enum | No | 16 | Output bit depth: 8 or 16 |

**Validation rules:**
- beam_energy_keV ∈ (0, 50]
- probe_current_pA ∈ [0.1, 10000]
- probe_diameter_nm ≥ 0

### 2.6 Section: Dataset

| Key | Type | Required | Default | Description |
|---|---|---|---|---|
| **output_format** | Enum | No | "tiff" | Image output format: "tiff", "png" |
| **include_ground_truth** | Bool | No | false | Save ground-truth labels |
| **include_metadata** | Bool | No | true | Save metadata JSON |
| **include_edge_maps** | Bool | No | false | Include edge position maps in GT |
| **include_contours** | Bool | No | false | Include contour lines in GT |
| **include_segmentation** | Bool | No | false | Include material segmentation in GT |
| **edge_threshold_height_nm** | Float | No | 0.5 × height | Threshold for edge detection |
| **compress** | Bool | No | true | Enable compression (TIFF LZW / PNG) |
| **overwrite** | Enum | No | "error" | "error", "overwrite", "rename_new" |

---

## 3. Configuration Inheritance

Configuration is resolved in this order:

```
1. Default system config (hard-coded in parser)
   ↓
2. Technology node default file (e.g., n5_defaults.yml)
   ↓
3. Structure library entry (structure-specific defaults)
   ↓
4. User config file (user overrides)
   ↓
5. Command-line overrides (highest priority)
```

**Inference:** Each level overrides the previous. A user config file may specify only the keys that differ from defaults. The result is a complete, validated configuration with every key resolved.

---

## 4. Configuration Validation Pipeline

```
Raw file (YAML/TOML) → Parse → Schema validation → Type coercion → Default resolution → Cross-field validation → Resolved Config object
```

| Stage | Checks | Failure Mode |
|---|---|---|
| Parse | Well-formed YAML/TOML | Fatal: "Parse error at line X" |
| Schema validation | Required keys present | Fatal: "Missing required key" |
| Schema validation | No unknown keys | Warning: "Unknown key ignored" |
| Type coercion | String→type conversion | Fatal: "Type error for key" |
| Default resolution | Missing optional keys filled | Not a failure |
| Cross-field validation | Dependent keys consistent | Fatal: "Inconsistent config" |

---

## 5. Batch Configuration

For generating multiple images (dataset mode), the configuration supports a batch structure:

```
Config
├── global ...       (shared)
├── structures        (list, not single)
│   ├── structure[0]  (type, parameters, variability)
│   ├── structure[1]
│   └── ...
└── physics ...       (shared, or per-structure override)
```

Each structure in the batch list generates one or more images (controlled by `repetitions` or a parameter sweep).

---

## Sources

- [S1] L. Bass et al., *Software Architecture in Practice*, Addison-Wesley, 2021.
- [I3] R. C. Martin, *Clean Architecture*, Prentice Hall, 2017.
- [I5] M. Fowler, *Configuration Management Patterns*, 2012.
- [I6] C. Walls, *Managing Configuration in Scientific Software*, 2019.
- Phase 4.1, Documents 05, 07 — Layered architecture, engineering conclusions.
- Phase 3.4 — Geometry parameter library.
- Phase 2.5 — SEM physics parameters.
