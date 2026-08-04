# Ground Truth Specification

**Research Phase:** 4.4
**Document:** 04_ground_truth_specification.md
**Date:** 2026-07-30

---

## 1. Ground Truth Components

The ground truth contains up to 5 components:

| Component | Content | Determination |
|---|---|---|
| **Edge position maps** | Signed distance to nearest edge per pixel | Direct — from height field |
| **CD values** | Top CD, bottom CD, height per feature | Direct — from height field |
| **Material segmentation** | Material ID per pixel | Direct — from material map |
| **Contour lines** | Edge coordinates in physical units | Direct — from height field |
| **Edge type map** | Classification of each pixel's edge type | Derived — from edge geometry |

---

## 2. Coordinate Conventions

| Convention | Value |
|---|---|
| **Image axes** | Row = Y (slow scan direction), Column = X (fast scan direction) |
| **Origin** | Top-left pixel = (0, 0) in pixel coordinates |
| **Pixel coordinates** | Integer (i, j) where i = row, j = column |
| **Physical coordinates** | Float (x_nm, y_nm) = (j × pixel_size_nm, i × pixel_size_nm) |
| **Signed distance direction** | Positive = outside the feature (toward vacuum/space), Negative = inside the feature (toward material), Zero = on the edge |

---

## 3. Edge Position Maps

### 3.1 Specification

| Field | Type | Description |
|---|---|---|
| `edge_distance` | float64[M×N] | Signed distance to nearest feature edge (nm) |
| `edge_type` | uint8[M×N] | 0 = no edge, 1 = top edge, 2 = bottom edge, 3 = boundary edge |

### 3.2 Edge Extraction Method

The edge position map is computed from the height field:

```
For each pixel at (x, y):
  z = height_field[x, y]

  if z >= edge_threshold:
    pixel is "inside" (feature present)
  else:
    pixel is "outside" (no feature at this height)

  signed_distance = distance to nearest pixel where z crosses edge_threshold
  where crossing is detected by 4-connectivity (up, down, left, right)
```

### 3.3 Edge Type Classification

| Type | Value | Criteria |
|---|---|---|
| **No edge** | 0 | Pixel is not near an edge |
| **Top edge** | 1 | Edge is at the top surface of a feature (height = feature_max) |
| **Bottom edge** | 2 | Edge is at the base of a feature (height ≈ substrate) |
| **Boundary edge** | 3 | Edge at image boundary (feature continues beyond FOV) |

### 3.4 Edge Detection Parameters

| Parameter | Default | Description |
|---|---|---|
| **edge_threshold_height_nm** | 0.5 × feature_height | Height at which the "feature exists" decision is made |
| **distance_field_pixels** | 10 | Maximum distance (in pixels) to compute signed distance |
| **edge_type_height_ratio** | 0.8 | Edges with height > 0.8 × max_height are "top edges" |

---

## 4. CD Values

### 4.1 Specification

```
For each feature (identified by connected components in the material map):
```

| Field | Type | Description |
|---|---|---|
| `feature_id` | int | Unique identifier within this sample |
| `feature_type` | string | Structure type from library |
| `cd_top_nm` | float | Top critical dimension (width at top edge) |
| `cd_bottom_nm` | float | Bottom critical dimension (width at bottom edge) |
| `height_nm` | float | Feature height (max Z − substrate Z) |
| `sidewall_angle_deg` | float | Derived sidewall angle from CD_top, CD_bottom, and height |
| `pitch_nm` | float (if applicable) | Distance to next feature (line/space arrays) |
| `position_x_nm` | float | Feature center X in physical coordinates |
| `position_y_nm` | float | Feature center Y in physical coordinates |
| `is_partial` | bool | Feature extends beyond image boundary |
| `line_edge_roughness_3sigma_nm` | float | Measured LER 3σ (actual, not configured) |
| `line_width_roughness_3sigma_nm` | float | Measured LWR 3σ (actual, not configured) |

### 4.2 CD Measurement Method

| Measurement | Method |
|---|---|
| **CD_top** | Width of feature at height = (feature_max − edge_threshold) |
| **CD_bottom** | Width of feature at height = substrate + epsilon (typically 1 nm above substrate) |
| **Height** | Max Z in feature region − substrate Z |
| **Sidewall angle** | θ = arctan(2 × height / (CD_bottom − CD_top)) |
| **LER 3σ** | Standard deviation of edge position along the edge (3 × σ) |

---

## 5. Material Segmentation

| Field | Type | Description |
|---|---|---|
| `material_segmentation` | uint8[M×N] | Material ID per pixel (0–6) |

The segmentation uses the same encoding as the material map:

| ID | Material |
|---|---|
| 0 | Vacuum |
| 1 | Silicon |
| 2 | Silicon Dioxide |
| 3 | Silicon Nitride |
| 4 | Copper |
| 5 | Tungsten |
| 6 | Photoresist |

---

## 6. Contour Lines

| Field | Type | Description |
|---|---|---|
| `contour_lines` | array of objects | Ordered edge contours in physical coordinates |

Each contour object:

| Field | Type | Description |
|---|---|---|
| `feature_id` | int | Feature this contour belongs to |
| `contour_number` | int | 1, 2, ... (one contour edge = one continuous boundary; features may have multiple contours for holes) |
| `edge_type` | uint8 | 1 = top edge, 2 = bottom edge |
| `x_nm` | float64[N_points] | X coordinates along contour (nm) |
| `y_nm` | float64[N_points] | Y coordinates along contour (nm) |
| `closed` | bool | Whether the contour forms a closed loop |

**Engineering Decision:** Contours are stored as **ordered point sequences** in physical units (nm), not as pixel indices. This avoids pixel quantization artifacts in downstream metrology applications.

---

## 7. Precision Requirements

| Measurement | Precision | Resolution |
|---|---|---|
| Edge position | ±0.1 nm | Sub-pixel (edge detection by interpolation) |
| CD value | ±0.1 nm | From edge positions |
| Height | ±0.1 nm | From height field |
| Sidewall angle | ±0.1° | Derived |
| LER 3σ | ±0.1 nm | Statistical; depends on line length |
| Contour points | ±0.1 nm | Sub-pixel accuracy |

---

## 8. Visibility Rules

| Rule | Application |
|---|---|
| Feature fully inside FOV | `is_partial = false`; CD computed normally |
| Feature partially outside FOV | `is_partial = true`; CD marked as approximate |
| No feature detected | All CD values = `null`; `feature_found = false` |
| Edge at image boundary | Edge type = `boundary_edge (3)`; contour is open |
| Two features overlapping (unusual) | Both features — IDs increase with overlap order |

---

## Sources

- Phase 4.2, Document 03 — Canonical data objects.
- Phase 3.3, Document 02 — LER measurement methodology.
- [D7] B. D. Bunday et al., "CD-SEM Metrology," *Proc. SPIE*, vol. 5038, 2003.
- [D8] International Technology Roadmap for Semiconductors, "Metrology," 2015.
