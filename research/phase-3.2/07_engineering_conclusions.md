# Engineering Conclusions

**Research Phase:** 3.2
**Document:** 07_engineering_conclusions.md
**Date:** 2026-07-30

---

## 1. Frozen Process Model

The canonical process model defined in Document 06 is the recommended pipeline for the Geometry Engine. It consists of:

| Stage | Purpose | Essential Parameters |
|---|---|---|
| 1. Layer Stack Init | Define substrate and layer sequence | Layer count, materials, thicknesses |
| 2a. Deposition | Add film material to current topography | Material ID, thickness, conformality type |
| 2b. Lithography | Transfer GDSII pattern to resist | Mask CD, resist sidewall angle, corner radii |
| 2c. Etch | Transfer resist pattern into film | Etch depth, sidewall angle, CD bias, corner radius |
| 2d. Resist Strip | Remove masking layer | None (unconditional removal) |
| 2e. CMP | Planarize to target height | Target height, dishing parameters (optional) |
| Repeat 2a–2e for each layer, then output height + material maps |

---

## 2. Fixed vs. Configurable Parameters

### 2.1 Fixed Assumptions

| Assumption | Value | Justification |
|---|---|---|
| Substrate is Si | Z = 0 reference | Standard semiconductor substrate |
| Positive-tone lithography | Exposed regions removed | Default process; can be inverted |
| Anisotropic RIE for main etch | Tapered sidewall (85–89°) | Standard for most layers |
| Conformal CVD for dielectrics | Uniform thickness | Standard for SiO₂, Si₃N₄ deposition |
| Clean resist strip | No residue | All resist fully removed |
| CMP target height per layer | Each layer planarized separately | Standard process integration |

### 2.2 Configurable Parameters

| Parameter | Default | Range | Used In |
|---|---|---|---|
| Layer count | Per design | 1–100 | Stack init |
| Per-layer thickness | Per design | 1–1000 nm | Deposition |
| Per-layer material ID | Per design | 0–6 (frozen) | Deposition |
| Deposition conformality | "conformal" | {"conformal", "bottom_up", "pvd"} | Deposition |
| Resist sidewall angle | 87° | 85–89° | Lithography |
| Resist thickness | 150 nm | 50–300 nm | Lithography |
| Etch sidewall angle | 87° | 85–89° | Etch |
| CD bias | 2 nm | 0–20 nm | Etch |
| Bottom corner radius | 5 nm | 2–20 nm | Etch |
| Top corner radius | 3 nm | 1–10 nm | Lithography |
| Etch selectivity | 20:1 | 5:1–100:1 | Etch |
| CMP target height | Per layer | 0–1000 nm | CMP |
| Dishing depth | 0 nm (disabled) | 0–50 nm | CMP |
| Dishing threshold width | 1 μm | 0.5–10 μm | CMP |

---

## 3. Simplifications Summary

| Effect | Classification | Reason |
|---|---|---|
| Sidewall taper | **Essential** | Directly determines SEM profile width |
| CD bias | **Essential** | Determines final CD from mask CD |
| Corner rounding | **Essential** | Affects SEM edge intensity |
| Conformality | **Essential** | Determines sidewall thickness |
| CMP target | **Essential** | Determines final heights |
| Dishing (wide lines) | **Recommended** | Affects wide-feature SEM contrast |
| Resist profile | **Recommended** | Transferred through etch |
| Over-etch | **Optional** | Limited SEM visibility |
| Micro-trenching | **Optional** | Bottom of features; limited visibility |
| Etch lag (ARDE) | **Optional** | Only matters for high AR features |
| Thickness variation | **Optional** | <5% variation; minor effect |
| Standing waves | **Ignore** | Sub-nm; not topographically visible |
| Implantation | **Ignore** | No geometric effect |
| Annealing | **Ignore** | No geometric effect |
| Voids | **Ignore** | Process defect; not modeled |

---

## 4. Technology Node Dependencies

| Parameter | Node Dependence | Configuration |
|---|---|---|
| CD values | Strong | Configurable per layer |
| Sidewall angles | Weak (85–88° across all nodes) | Configurable, default stable |
| Corner radii | Moderate (scales with CD) | Configurable, default = 0.1× CD |
| Layer thicknesses | Strong | Configurable per layer |
| Materials | Strong (new materials at each node) | Configurable via material library |
| Number of layers | Strong | Configurable |

**Inference:** The process model structure is node-independent. All node-specific values are configurable parameters. The algorithm itself does not change with node scaling.

---

## 5. Recommended Implementation Order

| Priority | Module | Depends On | Effort |
|---|---|---|---|
| 1 | Layer stack initialization | GDSII reader | Low |
| 2 | Deposition (conformal) | Height field library | Moderate |
| 3 | Lithography (pattern + taper) | GDSII rasterizer | Moderate |
| 4 | Etch (anisotropic) | Lithography output | Moderate |
| 5 | Resist strip | Etch output | Low |
| 6 | CMP (ideal) | Previous layers | Low |
| 7 | Layer loop executor | All above | Moderate |
| 8 | Output writer (PNG) | Final height/maps | Low |
| 9 | Corner rounding | Lithography + Etch | Moderate |
| 10 | Deposition (bottom-up) | Conformal deposition | Low |
| 11 | CMP dishing | Ideal CMP | Low |
| 12 | Over-etch model | Etch | Low |

---

## 6. Consistency with Previous Phases

| Phase | Decision | Phase 3.2 Consistency |
|---|---|---|
| Phase 2.6 | Geometry interface = height map + material map | ✓ Process model outputs exactly this |
| Phase 3.1 | 2.5D height field as renderer input | ✓ Process model produces 2.5D height fields |
| Phase 3.1 | Integer material IDs 0–6 | ✓ Process model uses same ID table |
| Phase 3.1 | Coordinate convention: X fast, Y slow, Z up | ✓ Process model maintains this convention |
| Phase 3.1 | Layer stack as generator internal | ✓ Canonical process model uses layer stack internally |
| Phase 1 | GDSII as source format | ✓ Process model accepts GDSII input per layer |

**No conflicts with any previous frozen decisions.**

---

## Sources

- [F1] J. D. Plummer, *Silicon VLSI Technology*, Prentice Hall, 2000.
- [F10] S. Franssila, *Introduction to Microfabrication*, Wiley, 2010.
- [F14] C. T. Gabriel, "Sidewall profile modeling," *J. Vac. Sci. Technol. B*, vol. 28, 2010.
- Phase 2.6, Document 06.
- Phase 3.1, Documents 06, 07.
