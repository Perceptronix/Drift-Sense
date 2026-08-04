# Metadata Specification

**Research Phase:** 4.4
**Document:** 05_metadata_specification.md
**Date:** 2026-07-30

---

## 1. Metadata Organization

Metadata is organized into 7 categories:

| Category | Priority | Fields Count | Purpose |
|---|---|---|---|
| **Structure** | Required | 8 | Geometry type, dimensions, materials |
| **Geometry Process** | Required | 6 | Process model parameters |
| **Variability** | Required | 8 | LER, CDU, overlay applied values |
| **Physics** | Required | 10 | Beam, detector, signal parameters |
| **Seeds** | Required | 6 | Full seed hierarchy for reproducibility |
| **Version** | Required | 5 | Software, schema, library versions |
| **Provenance** | Required | 6 | Timestamps, duration, warnings |

---

## 2. Metadata Field Catalog

### 2.1 Structure Metadata

| Field | Type | Example | Description |
|---|---|---|---|
| `structure_type` | string | `"iso_line"` | Structure type from library |
| `structure_name` | string | `"iso_line_cd30nm"` | Human-readable name |
| `structure_library_version` | string | `"1.0.0"` | Structure library version |
| `cd_nm` | float | 30.0 | Top critical dimension |
| `height_nm` | float | 50.0 | Feature height |
| `pitch_nm` | float (optional) | 60.0 | Pitch (for arrays) |
| `material_name` | string | `"Si"` | Feature material |
| `substrate_material` | string | `"Si"` | Substrate material |
| `layer_stack_summary` | string | `"Si/SiO2/Cu"` | Quick layer summary |

### 2.2 Geometry Process Metadata

| Field | Type | Example | Description |
|---|---|---|---|
| `sidewall_angle_deg` | float | 87.0 | Etch sidewall angle |
| `cd_bias_nm` | float | 2.0 | CD bias |
| `top_corner_radius_nm` | float | 3.0 | Top corner radius |
| `bottom_corner_radius_nm` | float | 5.0 | Bottom corner radius |
| `process_model` | string | `"standard"` | Process model identifier |
| `deposition_type` | string | `"conformal"` | Deposition model |

### 2.3 Variability Metadata

| Field | Type | Example | Description |
|---|---|---|---|
| `ler_3sigma_nm` | float | 2.4 | Applied LER amplitude |
| `ler_xi_nm` | float | 25.0 | LER correlation length |
| `ler_rho` | float | 0.3 | LER left–right correlation |
| `lwr_3sigma_nm` | float | 3.4 | Resulting LWR (measured, not configured) |
| `cdu_sigma_nm` | float | 0.0 | Applied CDU variation |
| `overlay_x_nm` | float | 1.2 | Applied overlay translation X (this sample) |
| `overlay_y_nm` | float | -0.8 | Applied overlay translation Y (this sample) |
| `sidewall_angle_var_deg` | float | 0.0 | Applied sidewall angle variation |

### 2.4 Physics Metadata

| Field | Type | Example | Description |
|---|---|---|---|
| `beam_energy_keV` | float | 1.0 | Beam energy |
| `probe_current_pA` | float | 10.0 | Probe current |
| `probe_diameter_nm` | float | 1.5 | Probe diameter (PSF) |
| `se_yield_model` | string | `"universal"` | SE yield model name |
| `bse_yield_model` | string | `"everhart"` | BSE yield model name |
| `edge_brightening_enabled` | bool | true | Edge brightening flag |
| `charging_enabled` | bool | false | Charging model flag |
| `shot_noise_enabled` | bool | true | Shot noise flag |
| `detector_noise_enabled` | bool | true | Detector noise flag |
| `detector_gain` | float | 1.0 | Applied detector gain |
| `detector_offset` | float | 0.0 | Applied detector offset |
| `saturation_fraction` | float | 0.02 | Fraction of pixels saturated |

### 2.5 Seed Metadata

| Field | Type | Example | Description |
|---|---|---|---|
| `master_seed` | uint32 | 42 | Master seed from config |
| `structure_seed` | uint32 | 12345678 | Structure-level seed |
| `image_seed` | uint32 | 87654321 | Image-level seed |
| `ler_seed` | uint32 | 11223344 | LER generation seed |
| `overlay_seed` | uint32 | 22334455 | Overlay generation seed |
| `noise_seed` | uint32 | 33445566 | Noise generation seed |

### 2.6 Version Metadata

| Field | Type | Example | Description |
|---|---|---|---|
| `application_version` | string | `"0.2.0-rc1"` | Application version |
| `application_git_hash` | string | `"a1b2c3d4e5f6..."` | Exact git commit |
| `config_schema_version` | string | `"1.0.0"` | Config schema version |
| `material_library_hash` | string | `"sha256:abc123..."` | Material library SHA-256 |
| `structure_library_hash` | string | `"sha256:def456..."` | Structure library SHA-256 |

### 2.7 Provenance Metadata

| Field | Type | Example | Description |
|---|---|---|---|
| `generation_timestamp` | string (ISO 8601) | `"2026-07-30T14:30:00Z"` | When generated |
| `pipeline_duration_ms` | float | 1520.0 | Total pipeline execution time |
| `worker_id` | int | 3 | Worker process ID |
| `hostname` | string | `"workstation-01"` | Machine hostname (optional) |
| `warnings` | array of string | `[]` | Warnings during generation |
| `is_success` | bool | true | Whether generation was successful |

---

## 3. Mandatory vs. Optional Fields

| Category | Always Required? | Fields Always Required | Fields Optional |
|---|---|---|---|
| Structure | ✅ Yes | type, cd_nm, height_nm, material_name, substrate_material | pitch_nm, layer_stack_summary |
| Geometry Process | ✅ Yes | sidewall_angle_deg, cd_bias_nm, process_model | corner radii, deposition_type |
| Variability | ✅ Yes | ler_3sigma_nm, ler_xi_nm, ler_rho | cdu_sigma_nm, overlay_x/y_nm |
| Physics | ✅ Yes | beam_energy_keV, probe_current_pA, se/bse_yield_model | saturation_fraction, probe_diameter_nm |
| Seeds | ✅ Yes | master_seed, image_seed | ler_seed, overlay_seed, noise_seed |
| Version | ✅ Yes | application_version, git_hash, schema_version | library_hashes |
| Provenance | ✅ Yes | generation_timestamp | worker_id, hostname, warnings |

---

## 4. Metadata Completeness Rules

| Rule | Description | Violation |
|---|---|---|
| Every sample must have a config snapshot and a metadata record | Both files required | Fatal (missing file) |
| Metadata and config must agree on structure type | Cross-reference check | Error (inconsistency) |
| Seed chain must be tractable to master seed | Hierarchical derivation verified | Warning (non-standard seed) |
| Timestamps must be present and in ISO 8601 format | Format check | Warning (format) |

---

## 5. Metadata for Dataset (Not Per-Sample)

Dataset-level metadata covers aggregates:

| Field | Type | Description |
|---|---|---|
| `dataset_name` | string | Human-readable name |
| `dataset_version` | string | Semver version |
| `schema_version` | string | Metadata schema version |
| `generation_date` | string (ISO 8601) | When the dataset was generated |
| `n_samples` | int | Total samples in dataset |
| `structure_types_present` | array of string | All structure types included |
| `parameter_ranges` | dict | Range of each varied parameter |
| `total_storage_bytes` | int | Cumulative size of all files |
| `license` | string | License identifier |
| `citation` | string (optional) | Preferred citation |

---

## Sources

- Phase 4.2, Document 03 — Canonical data objects (Metadata object D10).
- Phase 4.3, Document 05 — Reproducibility strategy (seed chain).
- [D1] M. G. Creek et al., "Best Practices for Scientific Computing," *Nature Physics*, 2016.
- [D3] J. Lamprecht et al., "Towards FAIR Principles for Research Software," *Data Science*, 2020.
