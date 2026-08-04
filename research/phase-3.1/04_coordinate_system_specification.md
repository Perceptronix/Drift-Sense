# Coordinate System Specification

**Research Phase:** 3.1
**Document:** 04_coordinate_system_specification.md
**Date:** 2026-07-30

---

## 1. Coordinate Convention

### 1.1 Axis Definition

| Axis | Direction | Physical Meaning | SEM Scan Relation |
|---|---|---|---|
| **X** | Horizontal, left → right | Fast scan axis (line scan) | Corresponds to SEM horizontal scan |
| **Y** | Vertical, top → bottom | Slow scan axis (frame scan) | Corresponds to SEM vertical scan |
| **Z** | Vertical, upward | Height (out-of-plane) | Up = toward detector |

### 1.2 Orientation

```
Z (height, upward)
│
│   Y (slow scan)
│  /
│ /
│/────────── X (fast scan)
       (origin at top-left)
```

**Right-handed system:** X × Y = Z (if the Y-axis is considered to go downward for image coordinates, the right-hand rule is maintained by the image-scan convention).

### 1.3 Origin

| Coordinate | Origin | Definition |
|---|---|---|
| X = 0 | Left edge of the image | First pixel column |
| Y = 0 | Top edge of the image | First pixel row |
| Z = 0 | Bottom substrate surface | Lowest point in the simulation domain |

**Fact:** The Z = 0 reference is the bottom surface of the substrate (typically the Si wafer surface after CMP). Features are built upward from Z = 0.

---

## 2. Coordinate Spaces

### 2.1 Pixel Coordinates

| Parameter | Symbol | Definition |
|---|---|---|
| Pixel column | $u$ | Integer $0 \leq u < M$ (image width in pixels) |
| Pixel row | $v$ | Integer $0 \leq v < N$ (image height in pixels) |
| Pixel value | $h[u][v]$ | Height at pixel $(u,v)$ in digital numbers (DN) |
| Material ID | $m[u][v]$ | Material at pixel $(u,v)$ |

### 2.2 World Coordinates

| Parameter | Symbol | Units | Formula |
|---|---|---|---|
| X position | $x$ | nm | $x = u \times \Delta x$ |
| Y position | $y$ | nm | $y = v \times \Delta x$ (same spacing for square pixels) |
| Z position | $z$ | nm | $z = h[u][v] \times s_z$ |

where $\Delta x$ is the pixel size (nm/pixel) and $s_z$ is the height scale factor (nm/DN).

### 2.3 Coordinate Transformations

**Pixel → World:**
```
x_world = pixel_x * pixel_size_nm
y_world = pixel_y * pixel_size_nm
z_world = height_DN * pixel_to_nm_scale
```

**World → Pixel:**
```
pixel_x = floor(x_world / pixel_size_nm)  // integer pixel column
pixel_y = floor(y_world / pixel_size_nm)  // integer pixel row
height_DN = round(z_world / pixel_to_nm_scale)
```

---

## 3. Height Reference

### 3.1 Absolute vs. Relative Height

| Source | Convention | Example |
|---|---|---|
| **Height map values** | **Absolute height** from Z = 0 reference | A 100 nm tall line on Si: height = 100 nm |
| **Process layer thickness** | **Relative** (thickness from bottom of each layer) | Resist thickness = 100 nm → height = 100 nm |

**Engineering Decision:** The height map stores **absolute** height from the Z = 0 reference plane. This is simpler for rendering (no need to traverse a layer stack to compute pixel height). Layer thicknesses are converted to absolute heights by the geometry generator.

### 3.2 Default Height Reference Values

| Material | Z Reference | Notes |
|---|---|---|
| Si substrate bottom | Z = 0 | Base of simulation domain |
| STI oxide top | Z = 0 (after CMP) | Planarized surface |
| BEOL dielectric top | Depends on layer | M1 = 100 nm, M2 = 250 nm (example) |

---

## 4. Alignment Convention

### 4.1 Feature Orientation

| Feature | Default Orientation | Notes |
|---|---|---|
| Lines and trenches | Parallel to Y axis | X = constant → line edge; lines run vertically in image |
| Contact holes | Circular | Centered at specified (X, Y) |
| Fins | Parallel to Y axis | Matches line convention |
| Gates | Perpendicular to fins (X direction) | Crosses fins horizontally |

### 4.2 Rotation Support

| Rotation | Support |
|---|---|
| 0° (default) | Full support — lines aligned to Y-axis |
| 90° | Full support — lines aligned to X-axis |
| Arbitrary angle | Supported by geometry generator; height field is pixel-aligned after rotation |
| Staggered/via chains | Supported by specifying (X, Y) positions |

**Fact:** The 2.5D height field representation inherently aligns features to the pixel grid. Rotations must be applied before height field generation (i.e., the geometry generator rotates the layout, then generates the height field on the pixel-aligned grid).

---

## 5. Field of View and Resolution

### 5.1 Image Dimensions

| Parameter | Symbol | Default Value | Valid Range |
|---|---|---|---|
| Image width | $M$ | 1024 pixels | 256–4096 |
| Image height | $N$ | 1024 pixels | 256–4096 |
| Pixel size | $\Delta x$ | 1.0 nm | 0.2–5.0 nm |
| Field of view (X) | FOV$_x$ | 1024 nm | 51.2 nm – 20.48 μm |
| Field of view (Y) | FOV$_y$ | 1024 nm | 51.2 nm – 20.48 μm |

### 5.2 Height Range

| Parameter | Default | Maximum |
|---|---|---|
| Height range | 0–100 nm | 0–6553.5 nm (for 16-bit at 0.1 nm/DN) |
| Height precision | 0.1 nm | 0.1 nm (fixed for 16-bit quantization) |

**Inference:** The 0.1 nm height precision exceeds the SEM resolution (1.5–4 nm), ensuring that height quantization is never the limiting factor for CD-SEM simulation accuracy.

---

## 6. Consistency with Phase 2.6 Interface

This coordinate specification is **identical** to the geometry interface defined in Phase 2.6, Document 06:

| Item | Phase 2.6 | Phase 3.1 | Match? |
|---|---|---|---|
| X axis | Horizontal, left→right | Horizontal, left→right | ✓ |
| Y axis | Vertical, top→bottom | Vertical, top→bottom | ✓ |
| Z axis | Height, upward | Height, upward | ✓ |
| Origin | Top-left pixel | Top-left pixel | ✓ |
| Z = 0 | Substrate bottom | Substrate bottom | ✓ |
| Height units | nm | nm | ✓ |
| Pixel size | Configurable | Configurable | ✓ |
| Material IDs | 0–6 | 0–6 | ✓ |

**No conflicts.** The Phase 3.1 specification is a superset of the Phase 2.6 interface, adding conventions for coordinate transformations, alignment, and rotation that are internal to the geometry engine.

---

## Sources

- [E5] T. Dillinger, *VLSI Design*, Springer, 2020.
- [E8] GDSII Stream Format (Calma), 1978.
- [E9] OpenAccess Database Specification, Si2, 2023.
- [E10] ISO 16700, "Microbeam analysis — Guidelines for calibrating image magnification."
- Phase 2.6, Document 06: "Geometry Interface Specification."
