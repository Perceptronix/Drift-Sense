# Geometry Interface Specification

**Research Phase:** 2.6
**Document:** 06_geometry_interface_specification.md
**Date:** 2026-07-30

---

## 1. Purpose

This document freezes the interface between the geometry engine (which provides sample structure information) and the SEM physics engine (which renders the SEM image). **This interface must remain stable during Phase A implementation.**

---

## 2. Data Model

The input geometry is a **2.5D height field** represented as two registered 2D arrays (images) of the same dimensions.

### 2.1 File Format

| Field | Specification |
|---|---|
| **Format** | 16-bit grayscale PNG (lossless) |
| **Number of files** | 2 per structure (height map + material ID map) |
| **Naming convention** | `<structure_name>_height.png`, `<structure_name>_material.png` |
| **Metadata** | Embedded as PNG text chunks (see Section 5) |

### 2.2 Height Map

| Field | Specification |
|---|---|
| **Encoding** | 16-bit unsigned integer per pixel |
| **Units** | Nanometers (nm) |
| **Scale factor** | Height (nm) = pixel_value × pixel_to_nm_scale |
| **Default scale** | 0.1 nm per digital number (DN) |
| **Z-origin** | 0 = substrate bottom (see coordinate convention) |
| **Maximum height** | 6553.5 nm at 0.1 nm/DN scale (sufficient for any CD-SEM structure) |
| **Flat areas** | Set to constant height value for the region |

### 2.3 Material ID Map

| Field | Specification |
|---|---|
| **Encoding** | 16-bit unsigned integer per pixel |
| **Material IDs** | Defined in Table below |
| **Unused values** | Reserved for future materials (6–65535) |
| **Background** | 0 = vacuum (no material, below top surface) |

### 2.4 Material ID Table

| ID | Name | Symbol | Tag |
|---|---|---|---|
| 0 | Vacuum (no material) | — | Background |
| 1 | Silicon | Si | Primary substrate |
| 2 | Silicon Dioxide | SiO₂ | Dielectric |
| 3 | Silicon Nitride | Si₃N₄ | Dielectric |
| 4 | Copper | Cu | Conductor (BEOL) |
| 5 | Tungsten | W | Conductor (contact/via) |
| 6 | Photoresist | Resist | Organic (pattern transfer) |

---

## 3. Coordinate Convention

### 3.1 Coordinate System

```
Z (height, upward)
│
│   Y (scan slow axis)
│  /
│ /
│/────────── X (scan fast axis)
       (origin)
```

| Axis | Direction | Convention |
|---|---|---|
| **X** | Horizontal in image (fast scan axis) | Increases left → right |
| **Y** | Vertical in image (slow scan axis) | Increases top → bottom |
| **Z** | Height (out-of-plane) | Increases upward (surface → detector) |

**Origin:** (0, 0) = top-left pixel of the image. Z = 0 at the bottom of the substrate.

### 3.2 Image Registration

The two maps (height and material) are registered pixel-for-pixel:

```
height_png[y][x] = height at pixel (x, y)
material_png[y][x] = material ID at pixel (x, y)
```

### 3.3 Surface Normal Convention

Surface normals $\hat{n}$ point outward from the material (upward for flat surfaces):

| Surface | $\hat{n}$ | $\theta$ |
|---|---|---|
| Flat (horizontal) | (0, 0, 1) | 0° |
| Vertical sidewall (facing +X) | (1, 0, 0) | 90° |
| Vertical sidewall (facing −X) | (−1, 0, 0) | 90° |
| 45° slope | (0.707, 0, 0.707) | 45° |

---

## 4. Coordinate Computation

### 4.1 From Image Pixel to Physical Position

```
x_physical (nm) = pixel_x × pixel_size_nm
y_physical (nm) = pixel_y × pixel_size_nm
z_physical (nm) = height_png[pixel_y][pixel_x] × pixel_to_nm_scale
```

where `pixel_size_nm` is provided in metadata.

### 4.2 Surface Normal from Height Field

The surface normal at pixel $(x,y)$ is computed from the height field gradients:

```
dx = (height(y, x+1) - height(y, x-1)) / (2 × pixel_size_nm)   [central difference]
dy = (height(y+1, x) - height(y-1, x)) / (2 × pixel_size_nm)   [central difference]

n = normalize(-dx, -dy, 1.0)
```

**Edge handling:** For pixels on the image border, use forward/backward differences:
- Left edge (x=0): forward difference
- Right edge (x=M-1): backward difference
- Same for Y edges

### 4.3 Local Angle Computation

```
θ = acos(n·ẑ) = acos(n_z)
```

where $\hat{z} = (0, 0, 1)$.

---

## 5. Metadata

Metadata is embedded in both PNG files as **text chunks** (PNG standard).

### 5.1 Required Metadata

| Key | Value Type | Example | Description |
|---|---|---|---|
| `pixel_size_nm` | float | `1.000` | Physical size of one pixel in nanometers |
| `pixel_to_nm_scale` | float | `0.100` | Scale factor: height = pixel_value × this |
| `substrate_material` | int | `1` | Material ID of the substrate (always present) |
| `structure_name` | string | `resist_line_50nm` | Human-readable identifier |
| `max_height_nm` | float | `100.0` | Maximum height in the structure |
| `generator_version` | string | `1.0.0` | Version of the geometry generator |

### 5.2 Optional Metadata

| Key | Value Type | Example | Description |
|---|---|---|---|
| `created_date` | string | `2026-07-30` | Date of creation |
| `notes` | string | `Nominal CD = 50 nm` | Free text |

### 5.3 Example: Reading Metadata (Python)

```python
from PIL import Image
import json

img = Image.open("line_50nm_height.png")
metadata = {
    "pixel_size_nm": float(img.info["pixel_size_nm"]),
    "pixel_to_nm_scale": float(img.info["pixel_to_nm_scale"]),
    "substrate_material": int(img.info["substrate_material"]),
    "structure_name": img.info["structure_name"],
}
```

---

## 6. Example Geometry Files

### 6.1 Flat Si Surface

- Material map: All pixels = 1 (Si)
- Height map: All pixels = 1000 (representing 100 nm at 0.1 nm/DN)

### 6.2 Isolated Resist Line on Si (50 nm CD, 100 nm height)

| Region | Material ID | Height |
|---|---|---|
| Substrate (below pixel) | — | Not in image (assumed infinite) |
| Substrate surface | 1 (Si) | 0 nm |
| Line (x = 300–350 pixels at 1 nm/pixel) | 6 (Resist) | 100 nm |
| Line edges | 6 (Resist) | 0–100 nm (linear interpolation for sloped sidewall) |

**Note:** Sidewalls are represented by intermediate height values at the transition between the line top and the substrate. The number of transition pixels determines the sidewall angle:
- 1 pixel transition at 1 nm/pixel → near-vertical sidewall (~88° for 100 nm height)
- Multiple pixel transition → sloped sidewall

### 6.3 Contact Hole in SiO₂ (30 nm diameter)

| Region | Material ID | Height |
|---|---|---|
| Top surface | 2 (SiO₂) | 50 nm |
| Hole interior | same as hole material (1 for Si if landing on Si) | 0 nm |
| Hole edge pixels | 2 (SiO₂) | Interpolated 50→0 |
| Substrate surface | 1 (Si) | 0 nm |

---

## 7. Interface Contract

### 7.1 Geometry Engine Output

```
Geometry {
    height_map[M][N]     : uint16    // PNG 16-bit
    material_map[M][N]   : uint16    // PNG 16-bit
    metadata              : Key-value pairs (as above)
    pixel_size_nm         : float
    M                     : int (width in pixels)
    N                     : int (height in pixels)
}
```

### 7.2 Physics Engine Derived Quantities

From the geometry, the physics engine computes:

```
Derived {
    θ[M][N]              : float    // Local surface angle (radians)
    n̂[M][N]              : vec3     // Surface normal
    δ₀[M][N]             : float    // SE yield from material lookup
    η[M][N]              : float    // BSE yield from material lookup
    Λ[M][N]              : float    // Escape depth from material lookup
    f_c[M][N]            : float    // Charging factor from material lookup
}
```

---

## 8. Backward Compatibility

| Version | Changes | Date |
|---|---|---|
| 1.0 | Initial specification | 2026-07-30 |

**Changes to this interface must be reviewed and approved by both the geometry generation team and the physics engine team.**

---

## Sources

- [B1] L. Reimer, *Scanning Electron Microscopy*, 2nd ed. Springer, 1998.
- [T2] ISO 16700, "Microbeam analysis — Guidelines for calibrating image magnification."
- PNG Specification (ISO/IEC 15948), text chunk standard.
