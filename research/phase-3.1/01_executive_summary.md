# Phase 3.1 Executive Summary: Geometry Engine Research

**SEMICON 2026 Research Repository**
**Applied Materials**
**Date:** 2026-07-30
**Classification:** Research-Only (Phase 3.1)

---

## Purpose

This phase answers the engineering question: **"What geometric representation should be provided to the SEM physics engine?"**

The SEM physics specification (Phases 2.1–2.6) defined the canonical rendering pipeline and the geometry interface format (2.5D height field). This phase provides the **foundation for the Geometry Engine** — the component that generates the 3D semiconductor structure representations consumed by the renderer.

---

## Key Findings

### 1. Chosen Geometry Representation: 2.5D Height Field

| Property | Recommendation |
|---|---|
| **Primary representation** | 2.5D height field (height map + material ID map) |
| **Format** | Two registered 16-bit grayscale PNGs |
| **Precision** | 0.1 nm height resolution, 1 nm lateral resolution |
| **Range** | 0–6553.5 nm height, unlimited lateral extent |
| **Alternatives rejected** | Full 3D mesh (overkill), voxel grid (memory-bound), SDF (too complex for 2.5D structures) |

**Engineering Decision:** The 2.5D height field is the optimal representation for CD-SEM structures because:
- All standard semiconductor targets (lines, spaces, contacts, trenches, fins, vias) are 2.5D
- Memory usage is O(M×N) instead of O(M×N×Z) for full 3D
- Surface normals are trivially computed from height gradients
- The format is directly consumable by the SEM physics renderer

### 2. Six Representations Surveyed

| Representation | Memory | Surface Normals | 2.5D Suitability | Complexity | Verdict |
|---|---|---|---|---|---|
| **Polygon (GDSII)** | Compact | Indirect | Good | Moderate | Recommended (layout source) |
| **2.5D Height Field** | Very low | Direct | **Excellent** | Low | **Recommended (renderer input)** |
| **Full 3D Mesh** | Moderate | Direct | Overkill | High | Acceptable (special cases) |
| **Signed Distance Field** | High | Direct | Overkill | High | Not recommended |
| **Voxel Grid** | Very high | Indirect | Overkill | High | Not recommended |
| **Layer stack** | Ultra-low | None | Limited | Low | Acceptable (process-aware) |

### 3. Semiconductor Features Catalogued

| Feature Type | 2.5D Representable? | Key Parameters | SEM Relevance |
|---|---|---|---|
| Metal line | Yes | CD, height, sidewall angle, spacing | High (CD-SEM target) |
| Trench | Yes | Depth, CD, taper, bottom CD | High |
| Contact hole | Yes (approximated) | Diameter, depth, aspect ratio | High |
| Via | Yes (approximated) | Diameter, depth, taper | High |
| FinFET fin | Yes | Width, height, pitch | High |
| Gate structure | Yes | Length, height, spacer width | High |
| STI region | Yes | Depth, width, corner rounding | Moderate |

### 4. Coordinate System Frozen

| Convention | Specification |
|---|---|
| X | Horizontal (fast scan axis), left → right |
| Y | Vertical (slow scan axis), top → bottom |
| Z | Height (out-of-plane), upward |
| Origin | Top-left pixel, Z=0 at substrate bottom |
| Units | Nanometers (all axes) |

Consistent with the Phase 2.6 geometry interface.

### 5. Material Encoding

**Chosen method:** Integer material ID per pixel with external lookup table.

This is the simplest, most maintainable approach, already specified in Phase 2.6. Layer-based encoding can be added as a secondary indexing scheme for process-aware generation.

---

## Phase 3.2 Knowledge Required

Phase 3.2 requires:

1. **Process emulation** — models that convert a nominal layout (GDSII) into a 3D structure with realistic cross-sections (sidewall angles, corner rounding, trench bottom curvature).

2. **Layer stack specification** — the exact layer sequence (substrate → active → gate → contact → BEOL) for the target technology node.

3. **CD and pitch values** — the specific critical dimensions and pitches for each feature type at the target node.

---

## Sources

- [E1] S. M. Sze and M. K. Lee, *Semiconductor Devices: Physics and Technology*, 3rd ed. Wiley, 2012.
- [E2] C. Mack, *Fundamental Principles of Optical Lithography*, Wiley, 2007.
- [E3] J. Lienig and J. Scheible, *Fundamentals of Layout Design for Electronic Circuits*, Springer, 2020.
- [E4] M. Quirk and J. Serda, *Semiconductor Manufacturing Technology*, Prentice Hall, 2001.
- [E5] T. Dillinger, *VLSI Design*, Springer, 2020.
- [E6] Synopsys, "Sentaurus Structure Editor User Guide," 2023.
- [E7] J. W. Smith et al., "SEM image synthesis for metrology," *Proc. SPIE*, vol. 10145, 2017.
- [E8] GDSII Stream Format (Calma), 1978.
- [E9] OpenAccess Database Specification, Si2, 2023.
- [E10] ISO 16700, "Microbeam analysis — Calibrating image magnification."
