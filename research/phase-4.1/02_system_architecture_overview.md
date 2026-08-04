# System Architecture Overview

**Research Phase:** 4.1
**Document:** 02_system_architecture_overview.md
**Date:** 2026-07-30

---

## 1. Architecture Style Comparison

Four candidate architectural styles were evaluated:

| Style | Description | Flexibility | Complexity | Suitability | Verdict |
|---|---|---|---|---|---|
| **Pipeline** | Sequential stages, output of one = input to next | High | Low | Excellent for fixed processing chain | **Recommended** |
| Event-driven | Components react to events; loose coupling via message bus | Very high | Very high | Overkill for linear pipeline | Rejected |
| Service-oriented | Independent services communicating via network protocols | High | Very high | Overkill for single-machine simulation | Rejected |
| Plugin-based | Core framework with loadable modules | High | High | Useful for extensibility but adds complexity | Not recommended for initial version |
| **Monolithic + modular** | Single process with well-defined internal modules | Moderate | Low | Simple to implement and test | **Acceptable fallback** |

### 1.1 Recommendation: Pipeline Architecture

**Engineering Decision:** The pipeline architecture is recommended because:
1. The processing chain is inherently sequential (geometry → physics → dataset).
2. Each stage has one well-defined input and one well-defined output.
3. The architecture minimizes coupling between stages.
4. Adding or removing stages is straightforward.
5. Testing can be done stage by stage with known inputs and expected outputs.

---

## 2. End-to-End System

### 2.1 Complete Workflow

```
User Configuration File
        │
        ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 1. CONFIGURATION PARSING                                             │
│    Read YAML/TOML config. Validate all parameters.                   │
│    Resolve defaults. Seed RNG with specified seed.                   │
└─────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 2. STRUCTURE DEFINITION                                              │
│    Resolve structure type from library (line, contact, fin, etc.).   │
│    Apply structure parameters from config.                           │
│    Produce: StructureSpec (type, dimensions, materials, variations)  │
└─────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 3. GEOMETRY ENGINE                                                   │
│    a. GDSII Rasterization: layout → pixel mask                       │
│    b. Process Model: deposition → lithography → etch → CMP          │
│    c. Variability: LER, CDU, overlay, shape variations               │
│    Produce: HeightMap + MaterialMap (I4)                             │
└─────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 4. SEM PHYSICS ENGINE                                                │
│    a. Signal Generation: SE/BSE yield per pixel                     │
│    b. Degradation: PSF convolution, noise, charging                 │
│    c. Image Formation: gain, offset, digitization                    │
│    Produce: SEMImage (2D array of intensities)                       │
└─────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 5. DATASET ASSEMBLY                                                  │
│    a. Save SEM image (TIFF/PNG)                                      │
│    b. Generate ground truth (CD labels, edge maps, material maps)    │
│    c. Write metadata (parameters, seed, timestamps)                  │
│    Produce: Dataset (images + labels + metadata)                     │
└─────────────────────────────────────────────────────────────────────┘
        │
        ▼
    Output Directory
    ├── images/
    ├── ground_truth/
    ├── metadata/
    └── dataset_index.json
```

### 2.2 System Boundaries

| Boundary | What Enters | What Leaves | Format |
|---|---|---|---|
| System input | User config file | — | YAML / TOML |
| System output | — | Image dataset + metadata | TIFF/PNG + JSON |
| I1 (Layer spec) | — | Between Stage 1 and 2 | Internal data structure |
| I2 (Deterministic geometry) | — | Between Stage 2 and 3 | Internal data structure |
| I3 (Variable geometry) | — | Between Stage 3 and 4 | Internal data structure |
| I4 (Physics input) | — | Between Stage 3 and 4 | Internal data structure (frozen) |

---

## 3. Architectural Quality Attributes

| Attribute | Requirement | How Achieved |
|---|---|---|
| **Modularity** | Each module independently replaceable | Module = 1 directory, 1 public API, clear contract |
| **Testability** | Each stage testable in isolation | Known input → expected output at each interface |
| **Reproducibility** | Same config + seed → same result | Deterministic pipeline; seeded RNG throughout |
| **Scalability** | From 1 to 100,000 images | Batch mode with job manager |
| **Extensibility** | New structure types, models, variations | Library-based; new items = new library entry |
| **Performance** | Reasonable single-image time | Pipeline overhead negligible vs compute in each stage |

---

## 4. Configuration Philosophy

The system is **configuration-driven**:

```
config.yml
├── global
│   ├── seed: 42
│   ├── output_dir: "./output"
│   └── log_level: "info"
├── structure
│   ├── type: "iso_line"
│   ├── parameters:
│   │   ├── cd_nm: 50
│   │   ├── height_nm: 100
│   │   └── material: "Si"
│   └── variability:
│       ├── ler_3sigma_nm: 2.4
│       └── seed: 42 (structure-specific)
├── geometry
│   ├── process_model: "standard"
│   └── sidewall_angle_deg: 87
├── physics
│   ├── beam_energy_keV: 1.0
│   ├── probe_current_pA: 10.0
│   └── pixel_size_nm: 1.0
└── dataset
    ├── include_ground_truth: true
    └── image_format: "tiff"
```

---

## Sources

- [S1] L. Bass, P. Clements, R. Kazman, *Software Architecture in Practice*, 4th ed. Addison-Wesley, 2021.
- [S2] E. Gamma et al., *Design Patterns*, Addison-Wesley, 1994.
- [S3] M. Fowler, *Patterns of Enterprise Application Architecture*, Addison-Wesley, 2002.
- [S4] I. Gorton, *Essential Software Architecture*, 2nd ed. Springer, 2011.
- [S5] J. K. Ousterhout, *A Philosophy of Software Design*, Yaknyam Press, 2018.
- [S8] R. C. Martin, *Clean Architecture*, Prentice Hall, 2017.
- Phase 2.6 — SEM Physics Engine specification.
- Phase 3.4 — Geometry Engine specification.
