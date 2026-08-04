# Material Encoding

**Research Phase:** 3.1
**Document:** 05_material_encoding.md
**Date:** 2026-07-30

---

## 1. Encoding Methods Survey

Four methods were evaluated for assigning materials to geometry:

| Method | Description | Complexity | Flexibility | Verdict |
|---|---|---|---|---|
| **Integer ID lookup** | Each pixel stores an integer material ID; external table maps ID → properties | Low | High | **Recommended** |
| **Layer-based encoding** | Material = layer number + pattern type; semantics determined by process flow | Medium | High | **Acceptable** |
| **Direct property storage** | Each pixel stores physical properties directly ($\delta_0$, $\eta$, $\Lambda$, etc.) | High | Very high | Not recommended |
| **Color-mapped** | Material ID stored as RGB values | Low | Low | Not recommended |

---

## 2. Selected Method: Integer Material ID with Lookup

### 2.1 Specification

| Field | Specification |
|---|---|
| **Storage** | 16-bit unsigned integer per pixel |
| **File format** | Single-channel 16-bit grayscale PNG (lossless) |
| **Value range** | 0–65535 |
| **Used values** | 0–6 (frozen), 7–65535 reserved for future |
| **Lookup** | External material library file (JSON, YAML, or table in code) |

### 2.2 Material ID Table (Frozen)

| ID | Name | Symbol | Short Tag | Material Type | Used In |
|---|---|---|---|---|---|
| 0 | Vacuum | — | `vacuum` | Background | Everywhere (no material) |
| 1 | Silicon | Si | `silicon` | Substrate | Substrate, fins |
| 2 | Silicon Dioxide | SiO₂ | `oxide` | Dielectric | STI, ILD, spacers |
| 3 | Silicon Nitride | Si₃N₄ | `nitride` | Dielectric | Spacers, hardmask |
| 4 | Copper | Cu | `copper` | Conductor | BEOL lines, vias |
| 5 | Tungsten | W | `tungsten` | Conductor | Contacts, local interconnect |
| 6 | Photoresist | Resist | `resist` | Organic | Patterning layer |

### 2.3 Implementation: Material Lookup Table

```yaml
# material_library.yaml
materials:
  - id: 0
    name: vacuum
    tag: vacuum
    type: background
    delta_0: null      # No SE emission
    eta: null
    escape_depth_nm: null
    charge_factor: null

  - id: 1
    name: silicon
    tag: silicon
    type: semiconductor
    delta_0: 0.85
    eta: 0.18
    escape_depth_nm: 2.0
    charge_factor: 1.0

  - id: 2
    name: silicon_dioxide
    tag: oxide
    type: dielectric
    delta_0: 1.8
    eta: 0.14
    escape_depth_nm: 10.0
    charge_factor: 0.6

  - id: 3
    name: silicon_nitride
    tag: nitride
    type: dielectric
    delta_0: 1.3
    eta: 0.15
    escape_depth_nm: 5.0
    charge_factor: 0.7

  - id: 4
    name: copper
    tag: copper
    type: conductor
    delta_0: 1.1
    eta: 0.32
    escape_depth_nm: 1.0
    charge_factor: 1.0

  - id: 5
    name: tungsten
    tag: tungsten
    type: conductor
    delta_0: 0.8
    eta: 0.49
    escape_depth_nm: 0.5
    charge_factor: 1.0

  - id: 6
    name: photoresist
    tag: resist
    type: organic
    delta_0: 2.0
    eta: 0.08
    escape_depth_nm: 15.0
    charge_factor: 0.5
```

---

## 3. Layer-Based Encoding (Secondary Method)

### 3.1 Concept

In the geometry generator (not the renderer), materials can be identified by their process layer:

| Layer | Description | Material |
|---|---|---|
| L1 | Substrate | Si |
| L2 | STI fill | SiO₂ |
| L3 | Gate oxide | SiO₂ |
| L4 | Poly gate | Polysilicon or metal |
| L5 | Spacer | Si₃N₄ |
| L6 | Contact dielectric | SiO₂ |
| L7 | Contact fill | W |
| L8 | M1 dielectric | SiO₂ |
| L9 | M1 metal | Cu |

### 3.2 Mapping

The layer-based system is converted to the integer ID system before the material map is written:

```
Layer ID → Process Description → Material ID (frozen)
L1 (substrate) → Si → ID 1
L2 (STI) → SiO₂ → ID 2
L4 (gate) → poly-Si → ID 1 (Si)
L5 (spacer) → Si₃N₄ → ID 3
L7 (contact) → W → ID 5
L9 (M1) → Cu → ID 4
```

### 3.3 Advantages

| Advantage | Explanation |
|---|---|
| **Direct mapping to process** | Each layer corresponds to a fabrication step |
| **Automatic material assignment** | The process layer determines the material |
| **Natural parameterization** | Varying a layer's thickness automatically updates the material |

**Engineering Decision:** The geometry generator internally uses layer-based encoding for process-aware generation. The output material map uses the frozen integer ID system for the renderer. A mapping table converts between them.

---

## 4. Material Boundaries

### 4.1 Sharp vs. Graded Interfaces

| Interface Type | Specification | SEM Effect |
|---|---|---|
| **Sharp** | Material ID changes in a single pixel | Discontinuous contrast change |
| **Graded** | Material ID changes over 2–5 pixels | Gradual contrast transition |

**Fact:** Real semiconductor interfaces are not atomically sharp. There is always some interdiffusion or interface roughness. However, for CD-SEM simulation at 1 nm/pixel resolution, the interface width (0.5–2 nm) is comparable to the pixel size.

**Recommendation:** Use sharp interfaces (single-pixel transitions) for the initial Phase A implementation. Graded interfaces can be added as an optional blur of the material map boundary.

### 4.2 Sidewall Representation

Sidewalls are represented in the height map as a smooth transition from the feature top to the surrounding layer:

```
Material map (cross-section):
   ▄▄▄▄▄▄▄▄▄▄▄▄
   █            █          ← ID 6 (resist)
   █            █
▀▀▀▀▼▀▀▀▀▀▀▀▀▀▀▼▀▀▀▀  ← ID 1 (Si) at interface

Height map:
   ▄▄▄▄▄▄▄▄▄▄▄▄▄▄
   █▌             ▐█
   █▌             ▐█
▀▀▀▀█▀▀▀▀▀▀▀▀▀▀▀▀█▀▀▀▀  ← Height transitions over 2-3 pixels
```

The sidewall angle is encoded in the slope of the height transition:
- 1-pixel transition at 1 nm/pixel × 100 nm height → ~89° sidewall
- 3-pixel transition at 1 nm/pixel × 100 nm height → ~88° sidewall
- 10-pixel transition at 1 nm/pixel × 100 nm height → ~84° sidewall

---

## 5. Extending the Material Library

### 5.1 Adding a New Material

| Step | Action |
|---|---|
| 1 | Assign a new unused integer ID (>6) |
| 2 | Define the material name, tag, and type |
| 3 | Determine $\delta_0$, $\eta$, $\Lambda$, $f_c$ from literature or Monte Carlo |
| 4 | Add entry to material library table |
| 5 | Distribute updated library to all consuming modules |

### 5.2 Candidate Future Materials

| Material | Likely ID | Application | Priority |
|---|---|---|---|
| Cobalt (Co) | 7 | BEOL liner/cap | Medium (next-gen) |
| Ruthenium (Ru) | 8 | BEOL metal | Medium (next-gen) |
| Molybdenum (Mo) | 9 | Gate metal | Low |
| SiGe (Si₀.₇Ge₀.₃) | 10 | Source/drain, channel | Medium |
| TiN | 11 | Barrier, work-function metal | Medium |
| Al₂O₃ | 12 | High-k dielectric | Low |
| Amorphous Carbon | 13 | Hardmask | Medium |
| Spin-on Carbon (SOC) | 14 | Lithography stack | Medium |

---

## Sources

- [E4] M. Quirk and J. Serda, *Semiconductor Manufacturing Technology*, Prentice Hall, 2001.
- [E6] Synopsys, "Sentaurus Structure Editor User Guide," 2023.
- [E9] OpenAccess Database Specification, Si2, 2023.
- Phase 2.2 (Documents 03, 04, 06) — Material property definitions.
- Phase 2.5 (Document 02) — Frozen physical parameters.
- Phase 2.6 (Document 06) — Geometry interface specification.
