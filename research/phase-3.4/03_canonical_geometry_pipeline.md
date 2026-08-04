# Canonical Geometry Pipeline

**Research Phase:** 3.4
**Document:** 03_canonical_geometry_pipeline.md
**Date:** 2026-07-30

---

## 1. Pipeline Overview

The complete Geometry Engine pipeline transforms a GDSII layout into a 2.5D height field and material map for the SEM physics engine. It consists of 4 internal stages with 4 defined interfaces.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            GEOMETRY ENGINE                                       │
│                                                                                  │
│  GDSII Layout (per layer)                                                        │
│         │                                                                        │
│         ▼                                                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐     │
│  │  STAGE 1: LAYER STACK                                                    │     │
│  │  Input:  GDSII layout files (one per layer)                               │     │
│  │  Process: Define layer order, materials, thicknesses from config         │     │
│  │  Output: Layer stack spec (material, thickness, GDSII layer per entry)    │     │
│  └─────────────────────────────────────────────────────────────────────────┘     │
│         │                                                                        │
│         ▼                                                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐     │
│  │  INTERFACE I1: LAYER STACK SPEC                                           │     │
│  │  Format: List of {layer_num, material_id, thickness_nm,                  │     │
│  │                    sidewall_angle, cd_bias, corner_radius}                │     │
│  └─────────────────────────────────────────────────────────────────────────┘     │
│         │                                                                        │
│         ▼                                                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐     │
│  │  STAGE 2: PROCESS MODEL (deterministic)                                   │     │
│  │  For each layer (bottom to top):                                          │     │
│  │    Deposition → Lithography → Etch → Strip → CMP                         │     │
│  │  Output: Deterministic height field + material map                        │     │
│  └─────────────────────────────────────────────────────────────────────────┘     │
│         │                                                                        │
│         ▼                                                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐     │
│  │  INTERFACE I2: DETERMINISTIC GEOMETRY                                     │     │
│  │  Format: {height_det[M][N]: float, material_det[M][N]: uint8,             │     │
│  │           metadata: {pixel_size, layer_stack_info}}                       │     │
│  └─────────────────────────────────────────────────────────────────────────┘     │
│         │                                                                        │
│         ▼                                                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐     │
│  │  STAGE 3: MANUFACTURING VARIABILITY ENGINE                                │     │
│  │  3a: LER/LWR generation (edge perturbation)                               │     │
│  │  3b: Sidewall angle variation (per feature)                               │     │
│  │  3c: Thickness / corner radius variation                                   │     │
│  │  3d: Overlay shift (per layer)                                             │     │
│  │  3e: CMP dishing/erosion variation                                         │     │
│  │  Output: Variable height field + material map                              │     │
│  └─────────────────────────────────────────────────────────────────────────┘     │
│         │                                                                        │
│         ▼                                                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐     │
│  │  INTERFACE I3: VARIABLE GEOMETRY                                          │     │
│  │  Format: {height_var[M][N]: float, material_var[M][N]: uint8,             │     │
│  │           variability_metadata: {LER_σ, CDU_σ, overlay_xy, etc.}}         │     │
│  └─────────────────────────────────────────────────────────────────────────┘     │
│         │                                                                        │
│         ▼                                                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐     │
│  │  STAGE 4: OUTPUT ENCODER                                                  │     │
│  │  4a: Quantize height to 16-bit DN (0.1 nm resolution)                    │     │
│  │  4b: Write height_map.png (16-bit PNG)                                    │     │
│  │  4c: Write material_map.png (16-bit PNG)                                  │     │
│  │  4d: Write metadata.txt (JSON)                                            │     │
│  │  Output: Two 16-bit PNG files + metadata                                  │     │
│  └─────────────────────────────────────────────────────────────────────────┘     │
│         │                                                                        │
│         ▼                                                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐     │
│  │  INTERFACE I4: PHYSICS ENGINE INPUT (FROZEN)                              │     │
│  │  Format: height_map.png (16-bit PNG)                                       │     │
│  │           material_map.png (16-bit PNG)                                    │     │
│  │           metadata.{pixel_size_nm, pixel_to_nm_scale, struct_name, ...}   │     │
│  └─────────────────────────────────────────────────────────────────────────┘     │
│         │                                                                        │
│         ▼                                                                        │
│         SEM PHYSICS ENGINE                                                       │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Interface Specifications

### 2.1 Interface I1: Layer Stack Spec

| Field | Type | Example | Description |
|---|---|---|---|
| `layer_num` | int | 1 | GDSII layer number (0 = substrate) |
| `name` | string | "contact" | Human-readable name |
| `material_id` | int | 5 (W) | Material ID from frozen library |
| `thickness_nm` | float | 100.0 | Deposition thickness |
| `cmp_target_nm` | float | 100.0 | CMP target height (0 = no CMP) |
| `sidewall_angle_deg` | float | 87.0 | Etch sidewall angle |
| `cd_bias_nm` | float | 2.0 | CD bias (mask → final) |
| `corner_radius_nm` | float | 5.0 | Bottom corner radius |
| `conformality` | string | "conformal" | conformal / bottom_up / pvd |
| `resist_thickness_nm` | float | 150.0 | Lithography resist thickness |
| `resist_angle_deg` | float | 87.0 | Resist sidewall angle |
| `overlay_translation_x_nm` | float | 0.0 | Overlay shift X (applied in Stage 3) |
| `overlay_translation_y_nm` | float | 0.0 | Overlay shift Y |

### 2.2 Interface I2: Deterministic Geometry

| Field | Type | Units | Description |
|---|---|---|---|
| `height_det` | float[M][N] | nm | Height at each pixel (no variation) |
| `material_det` | uint8[M][N] | — | Material ID at each pixel |
| `pixel_size_nm` | float | nm | Pixel spacing |
| `M, N` | int | pixels | Image dimensions |
| `layer_stack_info` | JSON | — | List of layers applied |

### 2.3 Interface I3: Variable Geometry

| Field | Type | Units | Description |
|---|---|---|---|
| `height_var` | float[M][N] | nm | Height with all variations applied |
| `material_var` | uint8[M][N] | — | Material ID (may differ from I2 near edges) |
| `LER_3sigma_nm` | float | nm | Applied LER amplitude |
| `LER_xi_nm` | float | nm | Applied LER correlation length |
| `CDU_sigma_nm` | float | nm | Applied CDU |
| `overlay_x_nm` | float | nm | Applied overlay shift X |
| `overlay_y_nm` | float | nm | Applied overlay shift Y |

### 2.4 Interface I4: Physics Engine Input (Frozen)

| File | Format | Content |
|---|---|---|
| `height_map.png` | 16-bit grayscale PNG | Height encoded as DN (scale: 0.1 nm/DN) |
| `material_map.png` | 16-bit grayscale PNG | Material IDs 0–6 (values 7+ reserved) |
| `metadata.json` | JSON | `{pixel_size_nm, pixel_to_nm_scale, structure_name, substrate_material, ...}` |

See Phase 2.6, Document 06 for the complete specification.

---

## 3. Stage Execution Order

### 3.1 Single Execution

```
1. Load GDSII layouts (one per layer)
2. Initialize height = 0, material = Si
3. For layer L in stack (bottom to top):
   a. Deposit layer L on current geometry
   b. Rasterize GDSII layer L → mask
   c. Apply lithography: mask → resist pattern
   d. Apply etch: resist pattern → film profile
   e. Strip resist
   f. Apply CMP (if applicable)
   g. Update current geometry = h_L, m_L
4. Apply variability:
   a. LER/LWR to feature edges
   b. Sidewall angle variation
   c. Thickness/corner variation
   d. Overlay shift
   e. CMP dishing/erosion
5. Encode output: height_map.png, material_map.png, metadata.json
```

### 3.2 For Non-Overlapping Layers

When layers do not overlap in the layout (common in BEOL), each layer is processed independently on the current topography. The topography from previous layers provides the starting surface for the next layer.

### 3.3 For Overlapping Layers

When layers overlap (e.g., contact going through ILD to substrate), the etch step on layer L opens windows through the previously deposited films. The etch depth is the sum of all layers between the surface and the target layer.

---

## 4. Pipeline Properties

| Property | Value |
|---|---|
| Deterministic | Stage 2 is deterministic for a given parameter set |
| Stochastic | Stage 3 introduces random variation per realization |
| Composability | Layers can be added/removed without changing the algorithm |
| Scalability | Processing time ∝ number of layers × image area |
| Reproducibility | Same seed → same output (important for testing) |

---

## Sources

- Phase 2.6, Document 06 — Geometry interface specification.
- Phase 3.2, Document 06 — Canonical process model.
- Phase 3.3, Documents 02–06 — Variability models.
- [E8] GDSII Stream Format, Calma, 1978.
- [F1] J. D. Plummer, *Silicon VLSI Technology*, Prentice Hall, 2000.
