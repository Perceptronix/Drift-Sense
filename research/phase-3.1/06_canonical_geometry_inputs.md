# Canonical Geometry Inputs

**Research Phase:** 3.1
**Document:** 06_canonical_geometry_inputs.md
**Date:** 2026-07-30

---

## 1. Required Inputs

The SEM physics engine requires exactly **four data structures** plus supporting metadata to render an image.

### 1.1 Input Package

| # | Input | Symbol | Format | Required? | Produced By |
|---|---|---|---|---|---|
| 1 | Height map | $h[u][v]$ | 16-bit grayscale PNG | **Yes** | Geometry engine |
| 2 | Material ID map | $m[u][v]$ | 16-bit grayscale PNG | **Yes** | Geometry engine |
| 3 | Metadata | — | PNG text chunks + JSON | **Yes** | Geometry engine |
| 4 | Pixel spacing | $\Delta x$ | Float (nm) | **Yes** | Part of metadata |

### 1.2 What the Physics Engine Derives from These

| Derived Quantity | Computation | Used By Module |
|---|---|---|
| Surface normals $\hat{n}[u][v]$ | Central difference of $h$ | Yield, Detector |
| Local angle $\theta[u][v]$ | $\theta = \arccos(n_z)$ | Yield |
| SE yield $\delta_0[u][v]$ | Lookup $m \to$ material library | Yield |
| BSE yield $\eta[u][v]$ | Lookup $m \to$ material library | Yield |
| Escape depth $\Lambda[u][v]$ | Lookup $m \to$ material library | PSF |
| Charging factor $f_c[u][v]$ | Lookup $m \to$ material library | Charging |
| Mean atomic number $Z[u][v]$ | Lookup $m \to$ material library | BSE model |

**Engineering Decision:** The geometry engine provides height and material — **everything else is derived by the physics engine**. This separation ensures the geometry engine focuses purely on geometric fidelity without needing to understand SEM physics.

---

## 2. Input Justification

### 2.1 Why Height Map?

| Reason | Explanation |
|---|---|
| Surface normals required | The $\sec\theta$ topographic contrast model requires the local surface angle $\theta$. Height gradients are the only way to compute $\theta$. |
| Z-position for charging | Charging depends on local height (step edges charge differently). |
| Shadowing | With TTL detection, high features may shadow adjacent low features. |
| CD measurement | CD metrology relates lateral dimensions to top-down SEM intensity. Height provides the missing third dimension. |

### 2.2 Why Material ID Map?

| Reason | Explanation |
|---|---|
| Material contrast | $\delta_0$ and $\eta$ are material-dependent. Without material IDs, the renderer cannot produce material contrast. |
| Energy-dependent yield | SE and BSE yields depend on material composition. |
| Charging behavior | Conductors, semiconductors, and insulators charge differently. The charging model needs to know which material is at each pixel. |
| Escape depth | The SE escape depth (which determines material-dependent resolution) varies significantly between materials. |

### 2.3 Why Pixel Spacing?

| Reason | Explanation |
|---|---|
| Physical scaling | The height map pixel values are in digital numbers — pixel spacing converts them to physical dimensions. |
| Probe diameter scaling | The PSF convolution kernel is defined in physical nanometers and must be converted to pixels. |
| CD measurement | Final CD values are in physical nanometers, not pixels. |

### 2.4 Why Metadata?

| Reason | Explanation |
|---|---|
| Self-documenting | Metadata ensures the renderer can validate that it received the expected input. |
| Error prevention | Pixel spacing and height scale mismatches are common integration bugs. Metadata enables validation before rendering. |
| Traceability | Structure name, generator version, and creation date aid debugging. |

---

## 3. Input Validation Rules

### 3.1 File Validation

| Check | Rule | Action on Failure |
|---|---|---|
| File exists | Both PNG files must be present | Error: "Missing input file" |
| File format | Must be valid 16-bit grayscale PNG | Error: "Invalid format" |
| Dimensions match | Height and material maps must have same (M, N) | Error: "Dimension mismatch" |
| Pixel count | M × N within valid range (256–4096)² | Warning: "Unexpected dimension" |

### 3.2 Content Validation

| Check | Rule | Action on Failure |
|---|---|---|
| Material IDs | All values in [0, 6] (current library) | Error: "Unknown material ID" |
| Height values | All h[u][v] ≥ 0 | Warning: "Negative height" |
| Height range | max(h) ≤ 6553.5 nm | Warning: "Height exceeds range" |
| Metadata present | pixel_size_nm, pixel_to_nm_scale, structure_name present | Error: "Missing metadata" |

### 3.3 Derived Quantity Validation

| Check | Rule | Action on Failure |
|---|---|---|
| Surface normal magnitude | $\|\hat{n}\| = 1 \pm 0.001$ | Warning: "Non-unit normal" |
| Local angle | $\theta \in [0, \pi/2]$ | Warning: "Angle out of range" |

---

## 4. Generator Constraints

The geometry engine must produce height and material maps that satisfy:

| Constraint | Reason |
|---|---|
| **No overhangs** | Single Z per (X,Y) — 2.5D limitation |
| **No floating material islands** | Every material pixel must have a path to the substrate |
| **Substrate forms the base** | Z=0 is a continuous Si surface |
| **Feature heights ≤ stack height** | No feature exceeds the total layer stack height |
| **Material boundaries ≤ 3 pixels** | Sharp boundaries represent realistic interfaces |

---

## 5. Optional Inputs (Future Phases)

| Input | Phase | Purpose |
|---|---|---|
| Surface roughness map | C | Add nm-scale random height perturbations |
| Line edge roughness (LER) | C | Add correlated edge displacement |
| Mask layer map | B | Identify which layer patterns were used for OPC/model verification |
| Feature type ID | B | Classify each region (line, space, hole, pad) for metrology labeling |

---

## Sources

- Phase 2.4 — Degradation physics (justifies need for height + material).
- Phase 2.5, Document 06 — Parameter library.
- Phase 2.6, Document 06 — Geometry interface specification.
- [E10] ISO 16700, "Microbeam analysis — Guidelines for calibrating image magnification."
