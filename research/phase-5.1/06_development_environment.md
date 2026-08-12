# Development Environment

**Research Phase:** 5.1
**Document:** 06_development_environment.md
**Date:** 2026-07-30

---

## 1. Canonical Development Stack

| Component | Specification | Justification |
|---|---|---|
| **Language** | Python 3.11+ | Scientific computing standard; NumPy/SciPy ecosystem; broad library support |
| **Package management** | pip + virtualenv (or conda) | Standard; reproducible through `requirements.txt` / `pyproject.toml` |
| **Build system** | setuptools + pyproject.toml | PEP 517/518 compliant; single source of truth |
| **Testing** | pytest 7+ + pytest-cov | Industry standard; fixture system; coverage reporting |
| **Static analysis** | mypy (strict mode), ruff/flake8, black, isort | Type safety; style consistency; automated formatting |
| **CI/CD** | GitHub Actions (or GitLab CI) | Standard; integration with GitHub workflow |
| **Documentation** | Sphinx + autodoc (or MkDocs + mkdocstrings) | Auto-generates API docs from docstrings |
| **Version control** | Git + GitHub/GitLab | Industry standard |
| **Editor** | VS Code (recommended) or PyCharm | LSP support; integrated debugging; Python tooling |

---

## 2. Repository Structure

```
semicon-sim/
│
├── pyproject.toml                ← Build config, dependencies, entry points
├── README.md                     ← Project overview
├── LICENSE                       ← License file
├── .gitignore                    ← Ignore patterns
│
├── src/
│   └── semicon/                  ← Main package
│       ├── __init__.py           ← Version, public API exports
│       │
│       ├── foundation/           ← L2: Shared utilities
│       │   ├── __init__.py
│       │   ├── math_utils.py     ← Convolution, distance transform, interpolation
│       │   ├── rng_utils.py      ← Seed manager, random field generation
│       │   ├── image_io.py       ← TIFF/PNG read/write
│       │   └── units.py          ← Physical constants
│       │
│       ├── geometry/             ← L3: Geometry Engine
│       │   ├── __init__.py
│       │   ├── raster.py         ← M1: GDSII rasterizer
│       │   ├── process.py        ← M2: Process model
│       │   └── variability.py    ← M3: Variability engine
│       │
│       ├── physics/              ← L3: SEM Physics Engine
│       │   ├── __init__.py
│       │   ├── signal.py         ← M4: Signal generator
│       │   ├── degrade.py        ← M5: Degradation model
│       │   └── formation.py      ← M6: Image former
│       │
│       ├── dataset/              ← L4: Dataset assembly
│       │   ├── __init__.py
│       │   ├── groundtruth.py    ← M7: Ground truth generator
│       │   └── writer.py         ← M8: Dataset writer
│       │
│       ├── config/               ← L5: Configuration
│       │   ├── __init__.py
│       │   └── parser.py         ← M9: Config parser
│       │
│       ├── orchestration/        ← L6: Orchestration
│       │   ├── __init__.py
│       │   ├── pipeline.py       ← M10a: Pipeline controller
│       │   └── job.py            ← M10b: Batch job manager
│       │
│       ├── validation/           ← Validation suite
│       │   ├── __init__.py
│       │   └── validator.py      ← L1–L5 validation
│       │
│       └── cli.py                ← CLI entry point
│
├── config/                       ← Default configurations
│   ├── defaults.yml              ← Default parameters
│   ├── library/
│   │   ├── structures.yml        ← Structure library
│   │   └── materials.yml         ← Material property table
│   └── examples/                 ← Example configs
│       ├── iso_line.yml
│       ├── dense_ls.yml
│       └── ...
│
├── tests/                        ← Test suite
│   ├── conftest.py               ← Shared fixtures
│   ├── unit/                     ← L0: Unit tests
│   │   ├── foundation/
│   │   ├── geometry/
│   │   ├── physics/
│   │   └── dataset/
│   ├── module/                   ← L1: Module validation
│   ├── interface/                ← L2: Interface validation
│   ├── pipeline/                 ← L3: Pipeline tests
│   ├── scientific/               ← L4: Scientific validation
│   └── data/                     ← Reference data for tests
│       ├── reference_images/
│       ├── test_gdsii/
│       └── regression_hashes/
│
├── docs/                         ← Documentation
│   ├── conf.py                   ← Sphinx config
│   ├── index.rst                 ← Documentation root
│   ├── user_guide/               ← User-facing documentation
│   ├── api/                      ← API reference (auto-generated)
│   └── architecture/             ← ADRs
│       ├── adr_001_initial_architecture.md
│       └── ...
│
├── scripts/                      ← Development scripts
│   ├── setup_test_data.py        ← Generate test data
│   └── run_benchmark.py          ← Performance benchmark
│
└── datasets/                     ← Generated datasets (git-ignored)
    └── .gitkeep
```

---

## 3. Branching Strategy

| Branch | Purpose | Base | Protected? |
|---|---|---|---|
| `main` | Production-ready code | — | ✅ Yes |
| `develop` | Integration branch | `main` | ✅ Yes |
| `feature/...` | Individual features | `develop` | No |
| `fix/...` | Bug fixes | `develop` | No |
| `release/v*.*.*` | Release candidates | `main` | ✅ Yes |

**Workflow:**

```
feature/geo_raster → develop → main (after milestone M1)
feature/phys_signal → develop → main (after milestone M2)
feature/orch_pipeline → develop → main (after milestone M3)
...
release/v1.0.0 → main (after M7 acceptance)
```

**Engineering Decision:** Feature branches merge to `develop` for integration testing before merging to `main`. Milestones are tagged from `main`. This keeps `main` stable at all times.

---

## 4. Code Review Process

| Review Level | Required For | Reviewers | Minimum Approvals |
|---|---|---|---|
| **Normal** | Feature branch → develop | 1 peer | 1 |
| **Interface** | Changes to I1–I8 contracts | Module lead of affected module | 2 |
| **Scientific** | Changes to physics/geometry models | Scientific lead | 2 |
| **Release** | develop → main | All module leads | 3 |
| **Hotfix** | Fix → main (emergency) | 1 module lead + architect | 2 |

---

## 5. Coding Standards

| Standard | Tool | Configuration |
|---|---|---|
| **Formatting** | black | Line length 88; auto-format on save |
| **Import sorting** | isort | Black-compatible profile |
| **Linting** | ruff | Select: E, F, W, I, N, D (docstring) |
| **Type checking** | mypy | Strict mode; disallow untyped defs |
| **Docstring style** | NumPy | Required for all public functions |

---

## 6. CI/CD Pipeline

```
Push → Branch:
  ├── Lint (ruff, black --check, isort --check)
  ├── Type check (mypy)
  ├── Unit tests (pytest tests/unit/ --cov)
  ├── Build (package install)
  └── Result: pass/fail

Merge to develop:
  ├── All of the above
  ├── Module tests (pytest tests/module/)
  ├── Interface tests (pytest tests/interface/)
  └── Result: pass/fail

Merge to main:
  ├── All of the above
  ├── Pipeline tests (pytest tests/pipeline/)
  ├── Scientific tests (pytest tests/scientific/)
  └── Tag release
```

---

## 7. Dependency Pinning

| Category | Policy |
|---|---|
| **Core dependencies** | Pin minor version: `numpy>=1.25,<2.0` |
| **Development dependencies** | Pin exact versions for CI reproducibility |
| **Python version** | `python_requires = ">=3.11"` |
| **Lock file** | `requirements.txt` for reproducible environments |

---

## 8. Versioning

The application version follows SemVer:

| Component | Source |
|---|---|
| **Major** | Breaking change to frozen specification |
| **Minor** | New feature, backward-compatible |
| **Patch** | Bug fix, no contract change |
| **Pre-release** | `-alpha`, `-beta`, `-rc1` |

Version is stored in `src/semicon/__init__.py` as `__version__`.

---

## Sources

- [I10] A. Oram, G. Wilson, *Making Software: What Really Works, and Why We Believe It*, O'Reilly, 2010.
- [I11] V. Driessen, "A Successful Git Branching Model," nvie.com, 2010.
- Phase 4.1, Document 06 — Repository organization.
- Phase 4.1, Document 03 — Module decomposition.
