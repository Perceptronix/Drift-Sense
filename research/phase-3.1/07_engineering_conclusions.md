# Engineering Conclusions

**Research Phase:** 3.1
**Document:** 07_engineering_conclusions.md
**Date:** 2026-07-30

---

## 1. Classification Summary

Every geometry representation and encoding scheme has been classified:

| Category | Count | Includes |
|---|---|---|

---

## 1. Classification Summary

Every geometry representation and encoding scheme has been classified:

| Category | Count | Includes |
|---|---|---|
| **Recommended** | 2 | 2.5D height field (for renderer input), integer material ID lookup (for material encoding) |
| **Acceptable** | 3 | GDSII/OASIS (for layout source), layer stack (for geometry generator internals), 3D mesh (for special cases) |
| **Not recommended** | 3 | Signed distance fields (for renderer input), voxel grids (for renderer input), direct property storage |

---

## 2. Recommended: 2.5D Height Field (Renderer Input)

| Aspect | Detail |
|---|---|
| **Representation** | Height map + material ID map (two 16-bit PNGs) |
| **Memory** | ~4 MB for 1024×1024 |
| **Surface normals** | Trivially computed from height gradients |
| **SEM suitability** | **Excellent** — captures all topographic and material information needed for CD-SEM simulation |
| **Limitation** | No overhangs (single Z per X,Y). Acceptable for >95% of CD-SEM targets. |
| **Implementation priority** | Phase A — this is the input format for the renderer |

**Justification:** The 2.5D height field is the optimal representation because:
1. CD-SEM measures **topography** — height variation is what creates contrast.
2. The SEM physics engine requires per-pixel height and material — exactly what the height field provides.
3. It uses minimal memory (2 bytes/pixel/material).
4. Surface normals are a trivial gradient computation.

---

## 3. Recommended: Integer Material ID with Lookup

| Aspect | Detail |
|---|---|
| **Representation** | 16-bit integer per pixel; external lookup table |
| **Memory** | 2 MB for 1024×1024 |
| **Flexibility** | High — adding materials requires only a new ID and library entry |
| **Maintainability** | High — lookup table is human-readable and version-controllable |
| **Implementation priority** | Phase A |

**Justification:** Integer ID lookup is the most maintainable encoding. The frozen table has 7 entries (IDs 0–6) with room for expansion. The external lookup table makes material properties trivially configurable without changing the geometry representation.

---

## 4. Acceptable Representations (With Constraints)

### 4.1 GDSII / OASIS (Layout Source)

| Condition | Detail |
|---|---|
| **Role** | Source format for the geometry generator |
| **Constraint** | Must be combined with process model to produce 3D geometry |
| **When to use** | Always — every IC design originates here |
| **Conversion needed** | GDSII + process model → height field |

### 4.2 Layer Stack (Geometry Generator Internal)

| Condition | Detail |
|---|---|
| **Role** | Internal intermediate format in the geometry generator |
| **Constraint** | Must be rasterized to height field before rendering |
| **When to use** | When generating geometry from process flow parameters |
| **Conversion needed** | Layer stack + pattern → height field |

### 4.3 3D Triangle Mesh (Special Cases)

| Condition | Detail |
|---|---|
| **Role** | For structures not representable in 2.5D (overhangs, re-entrant profiles) |
| **Constraint** | Requires ray casting or rasterization to convert to pixel image |
| **When to use** | Only when the target structure has overhangs (<5% of CD-SEM use cases) |
| **Conversion needed** | Mesh + camera → height field (via Z-buffer) |

---

## 5. Not Recommended Representations

| Representation | Reason for Rejection |
|---|---|
| **Signed Distance Field** | 1000× memory overhead vs. height field; no benefit for 2.5D structures |
| **Voxel Grid** | 256× memory overhead vs. height field; SEM imaging only needs surface information |
| **Direct property storage** | Duplicates physics model parameters into geometry; mixing of concerns |
| **Color-mapped material** | No advantage over integer IDs; wastes bit depth on RGB; harder to validate |

---

## 6. Geometry Pipeline Summary

```
┌────────────┐    ┌──────────────────┐    ┌───────────────┐
│   Input    │    │   Geometry Gen   │    │  Output       │
│  (source)  │    │   (internal)     │    │  (to renderer)│
└─────┬──────┘    └────────┬─────────┘    └───────┬───────┘
      │                    │                       │
┌─────▼──────┐    ┌───────▼─────────┐    ┌────────▼───────┐
│ GDSII      │───▶│ Layer stack +   │───▶│ Height map     │
│ OASIS      │    │ process model   │    │ Material map   │
│ OpenAccess │    │ (parameterized) │    │ + metadata     │
└────────────┘    └─────────────────┘    └────────────────┘
                         │
                    ┌────▼────┐
                    │ 3D Mesh │ (optional, special cases)
                    └─────────┘
```

| Stage | Representation | Format | Responsible |
|---|---|---|---|
| Input | GDSII/OASIS | Polygon-based | Layout team / EDA |
| Generator | Layer stack + parameters | Internal data structure | Geometry engine |
| Output | Height map + material map | 2×16-bit PNG | Geometry → Physics engine |
| Special | 3D mesh | OBJ/STL/PLY | Geometry engine (future) |

---

## 7. Key Engineering Decisions

| # | Decision | Rationale |
|---|---|---|
| E1 | 2.5D height field as renderer input | Minimal memory; direct surface normals; matches CD-SEM geometry |
| E2 | Integer material ID with lookup | Simple, maintainable, extensible |
| E3 | Layer stack as generator internal | Directly maps to process flow; enables process-aware generation |
| E4 | GDSII as source format | Industry standard; every IC design is available in GDSII |
| E5 | No full 3D unless overhangs | 2.5D covers >95% of CD-SEM use cases with minimal overhead |
| E6 | Sharp material boundaries initially | Interface width (0.5–2 nm) comparable to pixel size (1 nm) |
| E7 | Height map stores absolute Z | Simplest for rendering; layer-to-height conversion done in generator |

---

## Sources

- [E1] S. M. Sze, *Semiconductor Devices*, 3rd ed. Wiley, 2012.
- [E3] J. Lienig, *Fundamentals of Layout Design*, Springer, 2020.
- [E4] M. Quirk and J. Serda, *Semiconductor Manufacturing Technology*, Prentice Hall, 2001.
- [E5] T. Dillinger, *VLSI Design*, Springer, 2020.
- [E6] Synopsys "Sentaurus Structure Editor," 2023.
- [E7] J. W. Smith et al., *Proc. SPIE*, vol. 10145, 2017.
- [E8] GDSII Stream Format (Calma), 1978.
- [E9] OpenAccess Database Specification, Si2, 2023.
- Phase 2.6, Document 06 — Geometry interface.
