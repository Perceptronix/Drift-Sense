# Material Property Library

**Research Phase:** 5.3
**Document:** 05_material_property_library.md
**Date:** 2026-07-30

---

## 1. Material ID Mapping (Frozen Specification)

The material ID encoding is **frozen** from Phase 1 / Phase 3.1 / Phase 4.4 (unchanged):

| ID | Material | Notes |
|---|---|---|
| 0 | Vacuum | No material — zero yield contribution |
| 1 | Silicon (Si) | Substrate, line/feature material |
| 2 | Silicon Dioxide (SiO₂) | Dielectric, STI fill |
| 3 | Silicon Nitride (Si₃N₄) | Spacer, hard mask |
| 4 | Copper (Cu) | Interconnect metal |
| 5 | Tungsten (W) | Contact fill, barrier |
| 6 | Photoresist (PR) | Patterning layer |

---

## 2. Property Record Definition

Each material record (frozen dataclass `MaterialRecord`) contains the certified physics parameters:

| Field | Type | Unit | Meaning | Source |
|---|---|---|---|---|
| `material_id` | uint8 | — | Frozen encoding (0–6) | Phase 1 |
| `name` | str | — | Canonical name | Phase 1 |
| `atomic_number` | float | — | Z for Everhart BSE model | Phase 2.2 |
| `se_yield_delta0` | float | — | δ₀: peak SE yield factor | Phase 2.2 |
| `se_decay_length` | float | nm | Λ: SE escape-length parameter | Phase 2.2 |
| `se_tilt_exponent` | float | — | f: tilt dependence (default 1.0) | Phase 2.3 |
| `bse_yield_eta` | float | — | η: BSE yield (or computed from Z) | Phase 2.2 |
| `se_bulk_generator` | float | — | g_bulk: SE2 bulk-generation efficiency | Phase 2.3 |
| `ebinding` | float | keV | E_b: binding/ionization energy | Phase 2.2 |
| `density` | float | g/cm³ | Mass density (reference only) | Phase 2.1 |
| `mass_number` | float | — | A (reference only) | Phase 2.1 |

---

## 3. Certified Reference Values

Reference parameter set (Phase 2-certified ranges; **final values pinned at calibration step**, Step 1 of the development sequence, with literature cross-checks):

| ID | Material | Z | δ₀ | Λ (nm) | f | η | g_bulk | E_b (keV) |
|---|---|---|---|---|---|---|---|---|
| 0 | Vacuum | 0 | 0.0 | 0.0 | 1.0 | 0.0 | 0.0 | 0.0 |
| 1 | Si | 14 | 0.15 | 2.5 | 1.0 | 0.215* | 0.5 | 0.0018 |
| 2 | SiO₂ | 10.8 | 0.16 | 2.8 | 1.0 | 0.180* | 0.5 | 0.0040 |
| 3 | Si₃N₄ | 10.4 | 0.15 | 2.6 | 1.0 | 0.175* | 0.5 | 0.0035 |
| 4 | Cu | 29 | 0.12 | 1.8 | 1.0 | 0.310* | 0.5 | 0.0011 |
| 5 | W | 74 | 0.10 | 1.5 | 1.0 | 0.500* | 0.5 | 0.0010 |
| 6 | PR | 5 | 0.20 | 4.0 | 1.0 | 0.070* | 0.5 | 0.0060 |

*\* η computed from Everhart polynomial at load time (Algorithm P3); the listed value is the resulting check value. δ₀ values are v1 calibration references within Phase 2 certified ranges — the material library supports per-version override (see §5 Versioning).*

---

## 4. Data Organization

| Aspect | Decision |
|---|---|
| **Primary source** | YAML file `config/library/materials.yml` (human-editable, version-controlled) |
| **Runtime representation** | Frozen dataclass `MaterialRecord` in `_shared/material_properties.py` |
| **In-memory store** | Immutable dict `{material_id: MaterialRecord}` + `{name: MaterialRecord}` index |
| **Vacuum handling** | ID 0 always returns zero-yield record; never looked up in Everhart polynomial |

### YAML structure (conceptual, not a schema):

```
materials:
  - id: 1
    name: "Si"
    atomic_number: 14
    se_yield_delta0: 0.15
    se_decay_length_nm: 2.5
    se_tilt_exponent: 1.0
    bse_yield_eta: 0.215
    se_bulk_generator: 0.5
    ebinding_keV: 0.0018
    density_g_cm3: 2.33
    mass_number: 28.09
```

---

## 5. Lookup Strategy

| Operation | Strategy | Complexity |
|---|---|---|
| Material by ID | Dict lookup `records[mat_id]` | O(1) |
| Material by name | Dict lookup `by_name[name]` | O(1) |
| Bulk yield precompute | At load: precompute η(Z) once per record | O(n_materials) |
| Per-pixel material properties | Vectorized `np.take(property_array, material_map)` → property map | O(M·N) |

**Implementation decision:** Precompute per-material derived values (η, δ₀, Λ, f) into flat NumPy arrays indexed by material ID. Per-pixel property lookup becomes a single `np.take` on the MaterialMap — vectorized, deterministic, fast.

---

## 6. Versioning

| Version element | Mechanism |
|---|---|
| **File version** | `version:` field in `materials.yml` (semver) |
| **Runtime hash** | SHA-256 of the canonical (sorted) material file — recorded in Metadata (Phase 4.4 `material_library_hash`) |
| **Change policy** | Any change to physical values → minor version bump + ADR; **breaking change to the ID encoding** → major version + full re-certification (frozen: ID encoding never changes in v1) |
| **Pinning** | The calibration Step 1 freezes v1.0.0 reference values into `materials_v1.yml`; the live file loads the pinned version by default |

---

## 7. Extensibility

| Extension | Mechanism | Impact |
|---|---|---|
| New material | Add record with new ID (≥ 7) + update material library YAML | None to certified IDs 0–6 |
| New property field | Add field to `MaterialRecord` dataclass + YAML entry; default value for existing records | Backward-compatible with defaults |
| Model variant | Add `model:` field per material selecting yield model (universal, joy_luo, experimental) | Model dispatch in yield_computer |
| Experimental calibration | Ship `materials_experimental.yml` override alongside certified v1 | Explicit, reviewed, versioned |

**Frozen rule:** Certified material IDs 0–6 and their semantic meanings are **immutable** in v1. Extensions use IDs ≥ 7.

---

## 8. Validation

| Validation | Method | Gate |
|---|---|---|
| File completeness | Every material ID 0–6 present; no duplicate IDs | L0 unit |
| Value bounds | δ₀ ∈ [0.05, 0.5]; Λ ∈ [1, 6] nm; f ∈ [0.5, 2.0]; η ∈ [0.02, 0.6]; E_b > 0 | L0 unit |
| Physical consistency | η from polynomial matches stored η ± 1e-3; density > 0; Z ∈ [1, 92] | L0 unit |
| Literature cross-check | Si δ(1 keV) ∈ [0.4, 0.8]; Cu δ < Si δ (ordering); W η > Cu η > Si η (ordering) | L4 scientific |
| Hash registry | materials.yml SHA-256 matches recorded hash in metadata | L1 module |

---

## 9. Default vs. Certified Modes

| Mode | Behavior |
|---|---|
| **Certified** (default) | Loads pinned `materials_v1.yml` — the audited reference set |
| **Experimental** | `--material-override` flag loads alternate YAML; marks every generated image metadata with `material_library_hash` of the override + warning |
| **Programmatic** | Python API `load_material_library(path)` for test injection |

---

## Sources

- Phase 1 — Material ID encoding (frozen).
- Phase 2.1, 2.2 — Material physics parameters (SE, BSE, E_b).
- Phase 2.6 — SEM Physics Engine certification (parameter ranges).
- Phase 4.4 — Metadata `material_library_hash` (provenance).
- Phase 5.2 — Geometry MaterialMap (uint8 encoding, producer).
- [P1] Seiler (1983) — SE yield reference values.
- [P8] L. Reimer, *Scanning Electron Microscopy*, 2nd ed. Springer, 1998 — material parameter tables.
