# Interface Validation Strategy

**Research Phase:** 4.2
**Document:** 06_interface_validation_strategy.md
**Date:** 2026-07-30

---

## 1. Validation Philosophy

| Principle | Description |
|---|---|
| **Fail fast** | Validate at module boundaries before computation begins |
| **Defensive at the boundary, trusting at the core** | Thorough validation between modules; minimal checks within modules |
| **Clear error messages** | Every validation failure produces a message that identifies the specific field, the value found, the expected range or type, and the remedy |
| **Warnings are not errors** | Conditions that are non-ideal but not impossible produce warnings, not failures |

---

## 2. Validation Levels

| Level | Scope | By | Timing |
|---|---|---|---|
| **L1: Schema** | Required fields, types | Config Parser (M9) | Before pipeline |
| **L2: Range** | Value bounds | Interface boundary guard | At module entry |
| **L3: Consistency** | Cross-field relationships | Interface boundary guard | At module entry |
| **L4: Physical** | Unit correctness, physical plausibility | Interface boundary guard | At module entry |
| **L5: Regression** | Output matches reference | Post-generation | After pipeline |

---

## 3. Schema Validation (L1)

| Rule | Check | Error Message Pattern |
|---|---|---|
| Required field present | Key exists | `"Missing required key: 'structure.type'"` |
| Type correct | Value isinstance | `"Expected integer for 'global.seed', got string"` |
| Enum membership | Value in allowed set | `"Unknown structure type: 'iso_line_'. Expected one of: iso_line, dense_ls, ..."` |
| No unknown keys | Key in schema | `"Unknown key 'physics.beam_current_pA'. Did you mean 'probe_current_pA'?"` |

**Inference:** L1 validation catches the majority of user errors. Clear messages with suggestions (fuzzy matching on unknown keys) significantly improve user experience.

---

## 4. Range Validation (L2)

| Data Object | Field | Valid Range | Check Location |
|---|---|---|---|
| PixelMask | M, N | [64, 4096] | I1 entry |
| PixelMask | pixel_size_nm | (0, 100] | I1 entry |
| LayerStack | thickness_nm | > 0 | I2 entry |
| LayerStack | sidewall_angle_deg | [80, 90] | I2 entry |
| HeightField | data | [−100, 65535] | I3, I4 entry |
| HeightField | data | All finite (no NaN, no Inf) | I3, I4 entry |
| MaterialMap | data | [0, 6] | I3, I4 entry |
| YieldMaps | se_yield | [0, 10] | I5 entry |
| YieldMaps | bse_yield | [0, 5] | I5 entry |
| SEMImage | data | [0, 65535] | I8 entry |
| SEMImage | bit_depth | [8, 16] | I6 entry |
| Config | beam_energy_keV | (0, 50] | After parse |
| Config | image_width_pixels | [64, 4096] | After parse |
| Variability | ler_3sigma_nm | [0, 50] | I3 entry |
| Variability | ler_xi_nm | [2 × pixel_size, 1000] | I3 entry |
| Variability | ler_rho | [0, 1] | I3 entry |

---

## 5. Consistency Validation (L3)

| # | Check | Rule | Error Message |
|---|---|---|---|
| C1 | HeightField × MaterialMap dimensions | M, N, pixel_size_nm must match | "HeightField (1024×1024) and MaterialMap (512×512) dimension mismatch" |
| C2 | Material ID in material library | All material IDs have entries | "Material ID 7 not found in material library. Frozen IDs: 0–6" |
| C3 | CMP target vs. stack height | CMP target ≤ total deposited height | "CMP target 120 nm exceeds total deposited height 100 nm" |
| C4 | LER vs. minimum feature CD | LER 3σ ≤ 0.5 × CD_min | "LER 4 nm exceeds 50% of minimum CD 6 nm. Edges may cross." |
| C5 | FOV vs. layout extent | FOV ≤ layout extent + margin | "FOV (2 μm) exceeds layout extent (1.5 μm). Structure partially outside view." |
| C6 | Yield vs. saturation | Expected yield × gain ≤ saturation | "Expected max DN 98000 exceeds 16-bit max 65535. Reduce gain or increase saturation." |

---

## 6. Unit Validation (L4)

| Dimension | Accepted Units | Check |
|---|---|---|
| Length | nm (all internal) | Verify from config. No unit conversion needed — all internal computation in nm. |
| Energy | keV (beam), eV (binding) | Beam energy must be in keV. Material properties in consistent units. |
| Current | pA | Probe current to e⁻/pixel conversion uses physical constants. |
| Angle | degrees (configuration); radians (internal) | Interface accepts degrees. Conversion to radians happens at module boundary. |

**Inference:** Units are kept consistent throughout the system (nm, keV, pA, degrees). No unit conversion between modules is needed. Validation checks that input units match expectations.

---

## 7. Regression Validation (L5)

| # | Test | Method | Description |
|---|---|---|---|
| R1 | Image hash | Compute SHA-256 of SEMImage data | Same config + seed → same hash (determinism check) |
| R2 | CD accuracy | Compare CD from GroundTruth to parameter CD | |CD_measured − CD_parameter| ≤ LER 3σ + 0.5 nm |
| R3 | Edge count | Verify feature count matches expected | Number of detected edges = expected (lines: 2 × N_lines, contacts: N_contacts) |
| R4 | Height bounds | Verify heights within expected range | Max height ≤ total deposited thickness + 5% tolerance |
| R5 | Material coverage | Verify known materials only | All material IDs in image present in config |

**Regression test data:** A set of 10–20 canonical configurations with known outputs. Generated once, stored with the reference, and checked periodically.

---

## 8. Validation Execution Model

```
                    ┌──────────────────────────────────────────────────────┐
                    │                 PIPELINE EXECUTION                   │
                    └──────────────────────────────────────────────────────┘

Config Parser (M9):
  L1 Schema Validation ────→ L2 Range Validation ────→ L3 Consistency
  ────→ Resolved Config
       │
       ▼
I1 (Rasterizer):
  L2 Range: dimensions, pixel_size
  ────→ PixelMask
       │
       ▼
I2 (Process Model):
  L2 Range: thickness, angle, radius
  L3 Consistency: CMP vs stack
  ────→ HeightField_det, MaterialMap_det
       │
       ▼
I3 (Variability):
  L2 Range: LER σ, ξ, ρ
  L3 Consistency: LER vs CD
  L4 Unit: nm consistency
  ────→ HeightField_var, MaterialMap_var
       │
       ▼
I4 (Signal Generator):
  L2 Range: beam energy
  L3 Consistency: material properties available
  ────→ YieldMaps
       │
       ▼
I5 (Degradation):
  L2 Range: probe diameter, yield
  ────→ YieldMaps_degraded
       │
       ▼
I6 (Image Former):
  L2 Range: gain, bit depth
  L3 Consistency: saturation
  ────→ SEMImage
       │
       ▼
I7 (Ground Truth):
  L2 Range: threshold height
  ────→ GroundTruth
       │
       ▼
I8 (Dataset Writer):
  L2: output writable, disk space
  ────→ Files on disk
       │
       ▼
  L5 Regression (post-generation, optional)
```

---

## 9. Performance Impact

| Validation Level | Average Cost per Check | Notes |
|---|---|---|
| L1 Schema | < 1 μs | String matching, dict lookup |
| L2 Range | < 1 μs per scalar; < 10 μs per array (min/max) | Array min/max is O(M×N) but cache-friendly |
| L3 Consistency | < 1 μs per scalar check | Simple comparisons |
| L4 Unit | < 1 μs per field | No-op (system uses consistent units) |
| L5 Regression | 1–100 ms | Image hash: O(M×N), CD comparison: O(N_edges) |

**Inference:** L1–L4 validation overhead is negligible (< 0.1% of pipeline time). L5 regression validation depends on the test but is optional (off by default).

---

## Sources

- [I1] C. Larman, *Applying UML and Patterns*, Prentice Hall, 2004.
- [I2] B. Meyer, *Object-Oriented Software Construction*, Prentice Hall, 1997.
- [I3] R. C. Martin, *Clean Architecture*, Prentice Hall, 2017.
- [I7] B. W. Kernighan and R. Pike, *The Practice of Programming*, Addison-Wesley, 1999.
- Phase 4.1, Document 06 — Validation strategy.
- Phase 3.4, Document 06 — Geometry validation strategy.
