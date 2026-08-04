# Repository Organization

**Research Phase:** 4.1
**Document:** 06_repository_organization.md
**Date:** 2026-07-30

---

## 1. Repository Topology

Two viable strategies were evaluated:

| Strategy | Description | Pros | Cons | Verdict |
|---|---|---|---|---|
| **Monorepo** | All modules in a single repository | Simpler dependency management; atomic commits; unified testing | Larger clone; requires discipline at scale | **Recommended** |
| Multi-repo | Each module in its own repository | Clear ownership; independent versioning | Complex CI; version coordination overhead | Not recommended for this team size |

**Engineering Decision:** Monorepo.

---

## 2. Top-Level Directory Layout

```
semicon-sim/
│
├── src/                          # Source code
│   ├── geometry/                 # Geometry Engine modules
│   │   ├── raster/               #   geo_raster: GDSII → PixelMask
│   │   ├── process/              #   geo_process: PixelMask → HeightField
│   │   └── variability/          #   geo_variability: HeightField + LER
│   ├── physics/                  # SEM Physics Engine modules
│   │   ├── signal/               #   phys_signal: HeightField → YieldMap
│   │   ├── degrade/              #   phys_degrade: YieldMap → YieldMap (degraded)
│   │   └── formation/            #   phys_formation: YieldMap → SEMImage
│   ├── dataset/                  # Dataset assembly modules
│   │   ├── writer/               #   data_writer: SEMImage → files
│   │   └── groundtruth/          #   data_groundtruth: HeightField → labels
│   ├── orchestration/            # Pipeline orchestration
│   │   ├── pipeline/             #   orch_pipeline: single structure
│   │   └── job/                  #   orch_job: batch execution
│   ├── foundation/               # L2: shared utilities
│   │   ├── math_utils.py
│   │   ├── image_io.py
│   │   ├── rng_utils.py
│   │   └── units.py
│   └── api/                      # L6: public Python API
│       ├── __init__.py           #   Convenience imports
│       └── cli.py                #   Command-line interface
│
├── config/                       # Configuration files
│   ├── library/                  # Structure library definitions (YAML)
│   │   ├── lines/
│   │   ├── contacts/
│   │   ├── fins/
│   │   └── library_index.yml
│   ├── materials/                # Material property files
│   │   └── material_library.yml
│   └── defaults/                 # Default parameter files
│       ├── n5_defaults.yml
│       └── n7_defaults.yml
│
├── tests/                        # All tests
│   ├── unit/                     # Per-module unit tests
│   │   ├── geometry/
│   │   ├── physics/
│   │   ├── dataset/
│   │   ├── orchestration/
│   │   └── foundation/
│   ├── integration/              # Cross-module integration tests
│   ├── regression/               # Image regression tests
│   ├── fixtures/                 # Test data files
│   │   ├── gdsii/               #   Sample GDSII layouts
│   │   ├── configs/             #   Sample configs
│   │   └── expected/            #   Expected outputs for regression
│   └── conftest.py               # Pytest configuration
│
├── docs/                         # Documentation
│   ├── architecture/             # Architecture decisions
│   │   └── adr_*.md             #   Architecture Decision Records
│   ├── api/                      # API reference
│   ├── tutorials/                # Tutorials and examples
│   ├── reference/                # Reference (parameter tables, etc.)
│   └── contributing.md           # How to contribute
│
├── research/                     # Research repository (this work)
├── scripts/                      # Utility scripts
│   ├── generate_dataset.py       #   Dataset generation entry point
│   ├── visualize_geometry.py     #   Geometry visualization
│   └── validate_output.py        #   Validation scripts
│
├── outputs/                      # Generated data (git-ignored)
│   ├── images/
│   ├── datasets/
│   └── logs/
│
├── lib/                          # External dependencies (if vendored)
│
├── pyproject.toml                # Package metadata, dependencies
├── setup.cfg                     # Test configuration, linting
├── README.md                     # Project overview
├── LICENSE                       # License file
└── .gitignore                    # Git ignore rules
```

---

## 3. Directory Naming Convention

| Convention | Example | Rationale |
|---|---|---|
| **Lowercase with underscores** (Python PEP 8) | `geo_variability/`, `phys_signal/` | Follows Python package naming convention |
| **Singular directory names** | `test/fixture/` not `test/fixtures/` | Simpler; conventional in Python |
| **Module directory = module name** | `geo_raster/` matches module name | No mental mapping |
| **Sub-directories only when needed** | Flatten within each subsystem | Avoid deep nesting (>3 levels) |
| **Top-level directories are well-known** | `src/`, `tests/`, `docs/`, `config/` | Standard for research + production projects |

---

## 4. File Naming Convention

| File Type | Convention | Example |
|---|---|---|
| Python module | `snake_case.py` | `edge_ler.py` |
| Python package | `snake_case/` directory with `__init__.py` | `process/` |
| Configuration | `kebab-case.yml` | `n5-defaults.yml` |
| Test file | `test_<module>.py` | `test_geo_process.py` |
| Test data | `kebab-case.gds` | `line-pitch-40nm.gds` |
| Documentation | `snake_case.md` | `architecture_overview.md` |
| Image output | `kebab-case.tiff` | `iso-line-cd50nm.tiff` |

---

## 5. Module Internal Organization

Each module follows a consistent internal structure:

```
module_name/
├── __init__.py          # Public API: exported functions and classes
├── core.py              # Core logic (if module is non-trivial)
├── utils.py             # Module-specific utilities (if needed)
└── tests/               # Module-level unit tests
    └── test_core.py
```

**Rule:** The public API in `__init__.py` is the contract. All internal functions are prefixed with `_` or placed in non-exported modules.

---

## 6. Boundary Between `src/` and `config/`

| Directory | Contains | Ownership |
|---|---|---|
| `src/` | Code only — algorithms, data structures, transformations | Implementation team |
| `config/` | Data only — parameters, material properties, structure definitions | Process engineers, metrology team |
| `tests/` | Test code and fixtures | Implementation team |
| `docs/` | Documentation | All |

**Inference:** The boundary between code (src/) and data (config/) is the most important organizational separation. Parameters do not live in code. Code does not hard-code parameters.

---

## 7. Generation vs. Versioning

| File Type | Version Control | Regeneration |
|---|---|---|
| Source code (`src/`) | ✅ Yes | N/A |
| Configuration (`config/`) | ✅ Yes | Manual edit |
| Tests (`tests/`) | ✅ Yes | Manual edit |
| Documentation (`docs/`) | ✅ Yes | Manual edit |
| Research (`research/`) | ✅ Yes | Manual |
| **Outputs (`outputs/`)** | ❌ No (`.gitignore`) | Generated automatically |
| Test fixtures (expected) | ✅ Yes | Generated + verified |
| Test fixtures (temporary) | ❌ No | Generated during test |

---

## 8. Python Package Structure

```
pyproject.toml
├── [project] name = "semicon-sim"
├── [project] dependencies = ["numpy", "scipy", ...]
├── [project.scripts] generate-dataset = "semicon.api.cli:main"
├── [tool.pytest] ...
└── [tool.mypy] ...
```

The package is installable via `pip install -e .` for development.

---

## Sources

- [S8] R. C. Martin, *Clean Architecture*, Prentice Hall, 2017.
- [S12] H. M. Deitel and P. J. Deitel, *Python for Programmers*, Pearson, 2019.
- [S13] Python Packaging Authority, "Packaging Python Projects," pyPA, 2023.
- [S14] J. Humble and D. Farley, *Continuous Delivery*, Addison-Wesley, 2010 (repository structure best practices).
- Phase 3.4 — Geometry Engine library specification.
- Phase 2.6 — SEM Physics Engine specification.
