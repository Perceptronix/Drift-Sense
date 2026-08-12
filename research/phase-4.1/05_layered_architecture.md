# Layered Architecture

**Research Phase:** 4.1
**Document:** 05_layered_architecture.md
**Date:** 2026-07-30

---

## 1. Layer Model

The system is organized into 6 layers. Each layer depends only on the layer below it.

```
                    ┌─────────────────────────────────────────┐
                    │           L6: PRESENTATION              │
                    │  CLI, Python API, Jupyter notebooks     │
                    │  User-facing interface                   │
                    └────────────────────┬────────────────────┘
                                         │ depends on
                    ┌────────────────────▼────────────────────┐
                    │           L5: CONFIGURATION             │
                    │  Config parsing, validation, library    │
                    │  YAML/TOML → Config object              │
                    └────────────────────┬────────────────────┘
                                         │ depends on
                    ┌────────────────────▼────────────────────┐
                    │           L4: ORCHESTRATION             │
                    │  Pipeline controller, job manager       │
                    │  Stage sequencing, parallel execution   │
                    └────────────────────┬────────────────────┘
                                         │ depends on
                    ┌────────────────────▼────────────────────┐
                    │           L3: CORE ENGINES              │
                    │  ┌──────────────┐ ┌──────────────┐      │
                    │  │  Geometry    │ │   SEM Physics│      │
                    │  │  Engine      │ │   Engine     │      │
                    │  └──────────────┘ └──────────────┘      │
                    └────────────────────┬────────────────────┘
                                         │ depends on
                    ┌────────────────────▼────────────────────┐
                    │           L2: FOUNDATION                │
                    │  Math utilities, image I/O,             │
                    │  random number generation, logging      │
                    └────────────────────┬────────────────────┘
                                         │ depends on
                    ┌────────────────────▼────────────────────┐
                    │           L1: EXTERNAL                  │
                    │  Python, NumPy, SciPy, image libs       │
                    │  (language runtime + ecosystem)         │
                    └─────────────────────────────────────────┘
```

---

## 2. Layer Specifications

### 2.1 L1: External Dependencies

| Component | Role | Specificity |
|---|---|---|
| **Python** | Runtime environment | Required |
| **NumPy** | N-dimensional arrays, linear algebra | Required |
| **SciPy** | Signal processing, convolution, statistics | Required |
| **Image I/O** | TIFF/PNG reading and writing | Required |
| **YAML/TOML parser** | Configuration file reading | Required |
| **GDSII parser** | Layout file reading | Required (custom or library) |

**Rule:** Dependencies do not leak upward. L1 is the only layer that imports external libraries.

### 2.2 L2: Foundation Layer

| Module | Purpose | Exports |
|---|---|---|
| **math_utils** | Interpolation, line fitting, edge detection | `interpolate()`, `line_fit()`, `normal_from_gradient()` |
| **image_io** | Read/write images in supported formats | `read_image()`, `write_image()`, `image_stats()` |
| **rng_utils** | Seeded random number generation | `seeded_rng(seed)`, `gaussian_noise(shape, sigma, seed)` |
| **logger** | Structured logging with levels | `info()`, `debug()`, `warn()`, `error()` |
| **units** | Physical unit handling and conversion | `nm` ↔ `um`, `keV` ↔ `eV` |

**Layer property:** Foundation modules are stateless utility collections. No module in this layer knows about geometry, physics, or datasets.

### 2.3 L3: Core Engines Layer

This is the heart of the system. It contains two independent engine groups:

| Engine Group | Modules | Purpose |
|---|---|---|
| **Geometry Engine** | `geo_raster`, `geo_process`, `geo_variability` | Transform layout → 2.5D height field |
| **SEM Physics Engine** | `phys_signal`, `phys_degrade`, `phys_formation` | Transform height field → SEM image |

**Layer properties:**
- Engine modules know about each other only through the I4 interface (height field + material map)
- Each engine can be used independently (geometry engine can output height fields for inspection; physics engine can accept externally generated height fields)
- Both engines use L2 foundation utilities

### 2.4 L4: Orchestration Layer

| Module | Purpose |
|---|---|
| **orch_pipeline** | Single-structure pipeline: executes L3 modules in sequence |
| **orch_job** | Multi-structure batch: manages parallel pipeline executions |

**Layer property:** Orchestration is the only layer that knows the execution order. L3 modules do not know about each other's order of execution.

### 2.5 L5: Configuration Layer

| Component | Purpose |
|---|---|
| Config parser | Read YAML/TOML → `Config` object |
| Config validator | Validate types, ranges, dependencies |
| Structure library | Resolve structure type name → parameter set |

**Layer property:** Configuration is entirely data — no mutable state, no side effects. The config object flows through the pipeline unchanged.

### 2.6 L6: Presentation Layer

| Component | Purpose |
|---|---|
| **CLI** | Command-line interface for batch dataset generation |
| **Python API** | Importable Python module for programmatic use |
| **Scripts** | Jupyter notebooks for interactive exploration |

**Rule:** The presentation layer contains only thin wrappers over the orchestration layer. No business logic.

---

## 3. Layer Dependency Rules

| Rule | Violation Example | Consequence |
|---|---|---|
| A layer depends only on layers below it | L3 imports from L5 | → Circular dependency → redesign |
| L1 dependencies do not leak upward | L3 directly imports scipy.ndimage | → Acceptable (but prefer L2 wrapper) |
| No layer sees L6 | L3 creates CLI help text | → Coupling to presentation |
| L2 modules are stateless | L2 module caches results | → Hidden state → non-determinism |
| L4 is the only layer with sequence logic | L3 module calls another L3 module | → Module coupling → complex testing |

---

## 4. Layer Comparison with Alternatives

| Architecture | Layers | Pros | Cons | Verdict |
|---|---|---|---|---|
| **Strict layering (selected)** | 6 | Clear dependencies; testable; maintainable | More files; indirection | **Recommended** |
| Flat (no layers) | 1 | Simple to start | Tight coupling; untestable | Rejected |
| Onion (domain-centric) | 4+ | Domain isolation | Over-engineered for this project | Not recommended |
| Hexagonal (ports/adapters) | 3+ | Excellent testability | Too abstract | Rejected |
| Microkernel (core + plugins) | 2 | Extensibility | Plugin overhead | Future consideration |

---

## 5. Layer-Based Testing

| Layer | Test Strategy | What to Test |
|---|---|---|
| L2 Foundation | Unit tests | Math correctness; edge cases; I/O round-trips |
| L3 Core Engines | Unit + integration | Module-level: known input → expected output |
| L4 Orchestration | Integration | Pipeline: config → image end-to-end |
| L5 Configuration | Unit | Parse, validate, resolve, error messages |
| L6 Presentation | Acceptance | CLI: correct flags → correct pipeline invocation |

---

## Sources

- [S1] L. Bass et al., *Software Architecture in Practice*, Addison-Wesley, 2021.
- [S8] R. C. Martin, *Clean Architecture*, Prentice Hall, 2017.
- [S10] F. Buschmann et al., *Pattern-Oriented Software Architecture, Volume 1*, Wiley, 1996.
- [S11] C. Alexander, *The Timeless Way of Building*, Oxford, 1979 (architectural patterns — the original reference for layering).
- Phase 3.4 — Module decomposition from Geometry Engine.
- Phase 2.6 — Module decomposition from SEM Physics Engine.
