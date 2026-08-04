# Geometry Representation Survey

**Research Phase:** 3.1
**Document:** 02_geometry_representation_survey.md
**Date:** 2026-07-30

---

## 1. Survey Introduction

This document surveys every practical geometry representation for semiconductor structures. Each representation is evaluated against the requirements of the SEM physics engine.

### 1.1 Evaluation Criteria

| Criterion | Weight | Definition |
|---|---|---|
| **SEM rendering suitability** | High | Can the representation capture all features needed for SEM image formation (surface normals, material boundaries, topography)? |
| **Memory efficiency** | High | How much memory per unit area at typical CD-SEM resolution (1 nm/pixel)? |
| **Computational efficiency** | High | How expensive are the operations required by the SEM renderer (surface normal computation, material lookup)? |
| **EDA tool compatibility** | Medium | Can the representation be generated from standard EDA formats (GDSII, OASIS, OpenAccess)? |
| **Ease of validation** | Medium | Is the representation human-interpretable? Can it be checked for correctness? |
| **Manufacturing variation support** | Medium | Can manufacturing variations (sidewall angle, corner rounding, thickness variation) be represented? |

---

## 2. Candidate Representations

### 2.1 Polygon-Based Layout (GDSII / OASIS)

| Aspect | Detail |
|---|---|
| **Description** | 2D polygons with layer assignments. Standard in EDA. GDSII [E8] and OASIS are industry standards for IC layout. |
| **Data structure** | List of polygons, each with: layer number, datatype, vertices (X,Y coordinate pairs) |
| **Memory usage** | Very compact — ~100 bytes per polygon |
| **Strengths** | • Industry standard (GDSII is universal) <br> • Extremely compact <br> • Supports all IC designs |
| **Weaknesses** | • **No Z information** — 2D only (no height, no sidewall angles) <br> • No material properties — only layer numbers <br> • Requires process model to convert to 3D <br> • Cannot directly render SEM images |
| **Z-axis representation** | None — must be inferred from layer stack and process model |
| **Surface normal support** | None — normals require 3D topography |
| **Verdict** | **Recommended as source format** but not as renderer input. Every IC design begins here. |

**Fact:** GDSII has been the standard IC layout format since 1978 [E8]. It represents ICs as 2D polygons on layers. A typical modern chip has millions of polygons across 60-100 layers.

### 2.2 2.5D Height Field (Height Map)

| Aspect | Detail |
|---|---|
| **Description** | A 2D grid where each pixel stores the height of the top surface. Material ID stored in a second registered grid. |
| **Data structure** | Two 2D arrays: $h[y][x]$ (height), $m[y][x]$ (material ID) |
| **Memory usage** | Very low — $2 \times M \times N \times 2$ bytes (M=N=1024 → 4 MB) |
| **Strengths** | • **Minimal memory** — linear in area, not volume <br> • **Directly renders** SEM images — surface normals computed from height gradients <br> • **Intuitive** — easy to visualize and validate <br> • **Material per pixel** captures all relevant information |
| **Weaknesses** | • **Cannot represent overhangs** — a single height per pixel (re-entrant features not supported) <br> • **No volumetric information** — subsurface scattering relies on escape depth model, not full volume <br> • Limited vertical sidewall representation (discontinuity in height field) |
| **Z-axis representation** | Single height value per pixel |
| **Surface normal support** | Trivially computed: $\hat{n} = \text{normalize}(-\partial h/\partial x, -\partial h/\partial y, 1)$ |
| **Verdict** | **Recommended as renderer input.** The SEM physics engine (Phase 2.6) already specifies this format. |

**Inference:** The 2.5D height field is the optimal representation for CD-SEM simulation because:
- CD-SEM measures the **top-down** geometry — height variation is what creates contrast
- All common semiconductor test structures (lines, trenches, contacts) are 2.5D
- The interface with the SEM physics engine is already defined

### 2.3 Full 3D Triangle Mesh

| Aspect | Detail |
|---|---|
| **Description** | Collection of triangles forming the surface of the 3D structure. Each triangle has 3 vertices, a normal, and optionally a material ID. |
| **Data structure** | Vertex array + triangle index array + per-triangle material ID |
| **Memory usage** | Moderate — ~50 bytes per triangle. A 1 μm² surface at 1 nm resolution: ~2 million triangles → ~100 MB |
| **Strengths** | • **Supports arbitrary 3D geometry** — overhangs, true 3D structures <br> • Industry standard for 3D representation <br> • Surface normals are per-triangle (exact) |
| **Weaknesses** | • **Larger than height field** — 25× more memory for equivalent resolution <br> • **Gridless** — irregular sampling may require resampling for pixel-based rendering <br> • **More complex** — requires ray casting or rasterization for pixel rendering |
| **Z-axis representation** | Full 3D (multiple Z values per X,Y) |
| **Surface normal support** | Per-triangle normals (exact) |
| **Verdict** | **Acceptable for special cases** (structures with overhangs). Not recommended as the primary representation. |

**Engineering Decision:** A 3D mesh is necessary if the target includes re-entrant profiles (undercut after etching). However, for CD-SEM metrology targets, such structures are rare (<5% of use cases). The 2.5D height field covers 95%+ of cases.

### 2.4 Signed Distance Field (SDF)

| Aspect | Detail |
|---|---|
| **Description** | A volumetric grid storing the signed distance from each point to the nearest surface. Negative = inside material, positive = outside. |
| **Data structure** | 3D array of floats: $d[x][y][z]$ |
| **Memory usage** | Very high — $M \times N \times K \times 4$ bytes. For 1024×1024×256: ~1 GB |
| **Strengths** | • Excellent for computing surface normals (gradient of SDF) <br> • Handles arbitrary topology <br> • Smooth interpolation |
| **Weaknesses** | • **Extremely memory-intensive** for high resolution <br> • Requires conversion from layout → SDF (computationally expensive) <br> • Massive overhead for 2.5D structures <br> • Over-engineering for CD-SEM targets |
| **Z-axis representation** | Full volumetric |
| **Surface normal support** | Excellent — normal = gradient of SDF |
| **Verdict** | **Not recommended** for the primary application. High memory cost with no benefit over height fields for 2.5D structures. Used in some advanced process TCAD tools [E6]. |

### 2.5 Voxel Grid (Uniform 3D Grid)

| Aspect | Detail |
|---|---|
| **Description** | A regular 3D grid where each voxel stores a material ID or density value. |
| **Data structure** | 3D array of uint8/int8: $v[y][x][z]$ |
| **Memory usage** | High — $M \times N \times K \times 1$ bytes. For 1024×1024×256: ~256 MB (compressed) |
| **Strengths** | • Captures full 3D structure <br> • Simple data structure <br> • Standard for Monte Carlo simulation input [B4] |
| **Weaknesses** | • **Memory-intensive** — 256× the height field for equivalent lateral resolution <br> • Surface normals require gradient computation or interpolation <br> • Resolution limited by voxel size <br> • Most MC simulation can compute scattering without full volume representation |
| **Z-axis representation** | Full volumetric |
| **Surface normal support** | Via gradient of ID field (approximate) |
| **Verdict** | **Not recommended** as renderer input. Monte Carlo simulation tools (CASINO) internally use voxel grids [J9], but the SEM renderer does not need volume data. |

### 2.6 Layer-Stack Representation (Process-Aware)

| Aspect | Detail |
|---|---|
| **Description** | A compact representation storing the layer stack (material, thickness) plus per-layer 2D pattern information. |
| **Data structure** | List of layers: each with {material, thickness, pattern (polygon list or bitmap)} |
| **Memory usage** | Very low — compact for planar films: $O(N_{\text{layers}})$ plus pattern data |
| **Strengths** | • **Directly maps to process flow** — each layer corresponds to a deposition/etch step <br> • **Minimal memory** for planar layers <br> • **Natural parameterization** — easy to vary thickness, pattern dimension |
| **Weaknesses** | • **Does not directly represent a geometry** — must be combined into a height field or mesh for rendering <br> • Complex for non-planar topographies (e.g., over-fin deposition) |
| **Z-axis representation** | Implicit — built from layer stack |
| **Surface normal support** | None — must be derived after constructing the combined geometry |
| **Verdict** | **Acceptable as an intermediate representation** for the geometry generator. The layer stack naturally maps to process flow. The output must be converted to a height field for the renderer. |

---

## 3. Comparison Matrix

| Criterion | **Polygon (GDSII)** | **2.5D Height Field** | **3D Mesh** | **SDF** | **Voxel** | **Layer Stack** |
|---|---|---|---|---|---|---|
| SEM rendering | ⚠ Requires conversion | **★★★★★** | ★★★★ | ★★★ | ★★★ | ⚠ Requires conversion |
| Memory (1 μm², 1 nm) | ~10 KB | **~4 MB** | ~100 MB | ~1 GB | ~256 MB | ~50 KB |
| Surface normals | N/A | **Direct** (gradient) | **Exact** (per-tri) | Good (gradient) | Approximate | N/A |
| Industry standard | **★★★★★** | ★★★★ (rendering) | ★★★★ (CAD) | ★★ | ★★★ | ★★★ |
| Manufacturing variation | ⚠ Requires model | ★★★★ | ★★★★ | ★★★★ | ★★★ | **★★★★★** |
| Overhang support | N/A | **No** | **Yes** | **Yes** | **Yes** | ⚠ Limited |
| EDA tool compatible | **★★★★★** | ★★ | ★★ | ★★ | ★★ | ★★★★ |

---

## 4. Recommended Architecture

Based on the survey, the recommended architecture uses **three representations** at different stages:

```
┌──────────┐    ┌─────────────┐    ┌──────────────┐
│ GDSII    │───▶│ Layer Stack │───▶│ 2.5D Height  │───▶ SEM Physics
│ Layout   │    │ + Process   │    │ Field +      │    Engine
│ (source) │    │ Model       │    │ Material Map │
└──────────┘    └─────────────┘    └────── ───────┘
                      │
                      ▼
              ┌──────────────┐
              │ 3D Mesh      │ (special cases:
              │ (optional)   │  overhangs)
              └──────────────┘
```

| Stage | Representation | Responsibility |
|---|---|---|
| **Source** | GDSII / OASIS | Standard IC layout (frozen design intent) |
| **Intermediate** | Layer stack + process model | Converts design intent to 3D cross-sections with manufacturing effects |
| **Final** | 2.5D Height Field + Material Map | Input to SEM physics engine (frozen format) |
| **Optional** | 3D Triangle Mesh | For overhang structures not representable in 2.5D |

**Engineering Decision:** The project uses the 2.5D height field as the primary input to the SEM physics engine. The layer stack representation is the recommended internal format for the geometry generator. Full 3D meshes are supported for special cases.

---

## Sources

- [E1] S. M. Sze, *Semiconductor Devices: Physics and Technology*, 3rd ed. Wiley, 2012.
- [E3] J. Lienig, *Fundamentals of Layout Design for Electronic Circuits*, Springer, 2020.
- [E6] Synopsys, "Sentaurus Structure Editor User Guide," 2023.
- [E7] J. W. Smith et al., "SEM image synthesis for metrology," *Proc. SPIE*, vol. 10145, 2017.
- [E8] GDSII Stream Format (Calma), 1978.
- [E9] OpenAccess Database Specification, Si2, 2023.
- [J9] D. Drouin et al., "CASINO V2.42," *Scanning*, vol. 29, 2007.
- [B4] D. C. Joy, *Monte Carlo Modeling for Electron Microscopy*. Oxford University Press, 1995.
