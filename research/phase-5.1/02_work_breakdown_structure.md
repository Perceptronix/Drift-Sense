# Work Breakdown Structure

**Research Phase:** 5.1
**Document:** 02_work_breakdown_structure.md
**Date:** 2026-07-30

---

## 1. WBS Overview

27 work packages organized into 4 stages:

| WBS ID | Package Name | Stage | Est. Effort | Dependencies |
|---|---|---|---|---|
| **Stage 0: Foundation (Weeks 1–3)** | | | | |
| 0.1 | Project scaffold | 0 | 2 dev-days | None |
| 0.2 | math_utils | 0 | 1 week | 0.1 |
| 0.3 | rng_utils | 0 | 3 dev-days | 0.1 |
| 0.4 | image_io | 0 | 3 dev-days | 0.1 |
| 0.5 | units module | 0 | 1 dev-day | 0.1 |
| 0.6 | testing framework setup | 0 | 2 dev-days | 0.1 |
| **Stage 1: Core Pipeline (Weeks 3–14)** | | | | |
| 1.1 | geo_raster (M1) | 1 | 3 weeks | 0.2, 0.5 |
| 1.2 | geo_process (M2) | 1 | 5 weeks | 1.1 |
| 1.3 | geo_variability (M3) | 1 | 3 weeks | 1.2 |
| 1.4 | phys_signal (M4) | 1 | 4 weeks | 1.3 (I4) |
| 1.5 | phys_degrade (M5) | 1 | 2 weeks | 1.4 |
| 1.6 | phys_formation (M6) | 1 | 1 week | 1.5 |
| 1.7 | data_writer (M8) | 1 | 2 weeks | 0.4 |
| 1.8 | orch_pipeline (M10) | 1 | 2 weeks | 1.1–1.7 |
| **Stage 2: Automation (Weeks 14–24)** | | | | |
| 2.1 | data_groundtruth (M7) | 2 | 3 weeks | 1.3 (I7) |
| 2.2 | config_parser (M9) | 2 | 2 weeks | 0.1 |
| 2.3 | orch_job (M10 batch) | 2 | 3 weeks | 2.2, 1.8 |
| 2.4 | CLI entry point | 2 | 2 weeks | 2.2, 2.3 |
| 2.5 | validation suite L1–L3 | 2 | 3 weeks | 1.1–2.1 |
| 2.6 | self-check mode | 2 | 1 week | 2.4 |
| **Stage 3: Production (Weeks 24–36)** | | | | |
| 3.1 | caching subsystem | 3 | 3 weeks | 1.3 |
| 3.2 | worker pool (parallel) | 3 | 3 weeks | 2.3 |
| 3.3 | checkpoint & recovery | 3 | 2 weeks | 2.3 |
| 3.4 | regression suite L4–L5 | 3 | 2 weeks | 2.5 |
| 3.5 | documentation | 3 | 3 weeks | All |
| 3.6 | distribution packaging | 3 | 2 weeks | All |
| 3.7 | performance profiling | 3 | 2 weeks | 3.1–3.2 |

---

## 2. Detailed Work Package Descriptions

### 2.1 Stage 0: Foundation

#### WP 0.1: Project Scaffold

| Aspect | Specification |
|---|---|
| **Scope** | Initialize monorepo structure: `src/`, `config/`, `tests/`, `docs/`, `scripts/`, `pyproject.toml` |
| **Deliverables** | Working `pyproject.toml`; directory tree with `__init__.py` files; README; `.gitignore` |
| **Dependencies** | None |
| **Est. complexity** | Low (2 dev-days) |
| **Validation milestone** | `pip install -e .` succeeds; `import semicon` works |

#### WP 0.2: math_utils

| Aspect | Specification |
|---|---|
| **Scope** | Array utilities: 2D convolution, distance transform, interpolation, gradient computation, edge detection kernels |
| **Deliverables** | Module `semicon.foundation.math_utils` with 10–15 utility functions |
| **Dependencies** | 0.1 |
| **Est. complexity** | Medium (1 week) |
| **Validation milestone** | Unit tests: each function on known input → expected output |

#### WP 0.3: rng_utils

| Aspect | Specification |
|---|---|
| **Scope** | Seeded RNG manager: hierarchical seed derivation, per-stage RNG creation, deterministic sequence generation, Gaussian random field generation for LER |
| **Deliverables** | Module `semicon.foundation.rng_utils`; function `create_seed_chain(master_seed, structure_index, params) → dict`; function `make_gaussian_field(M, N, sigma, xi, seed) → array` |
| **Dependencies** | 0.1 |
| **Est. complexity** | Medium (3 dev-days) |
| **Validation milestone** | Fixed seed → exact known output; reproducibility unit test |

#### WP 0.4: image_io

| Aspect | Specification |
|---|---|
| **Scope** | TIFF read/write, PNG read/write, metadata embedding, dimension validation |
| **Deliverables** | Module `semicon.foundation.image_io`; functions `read_tiff`, `write_tiff`, `read_png`, `write_png` |
| **Dependencies** | 0.1 |
| **Est. complexity** | Low (3 dev-days) |
| **Validation milestone** | Round-trip test: write → read → pixel-identical |

#### WP 0.5: units module

| Aspect | Specification |
|---|---|
| **Scope** | Physical unit constants, unit conversion, validation helpers |
| **Deliverables** | Module `semicon.foundation.units`; constants (nm, keV, pA), validation decorators |
| **Dependencies** | 0.1 |
| **Est. complexity** | Very Low (1 dev-day) |
| **Validation milestone** | Unit tests for each constant and conversion |

#### WP 0.6: Testing Framework Setup

| Aspect | Specification |
|---|---|
| **Scope** | pytest configuration, coverage configuration, CI script, test fixtures, reference data directory |
| **Deliverables** | `pytest.ini`, `.coveragerc`, `tests/` structure with conftest.py, reference images |
| **Dependencies** | 0.1 |
| **Est. complexity** | Low (2 dev-days) |
| **Validation milestone** | `pytest` discovers and runs all tests |

---

### 2.2 Stage 1: Core Pipeline

#### WP 1.1: geo_raster

| Aspect | Specification |
|---|---|
| **Scope** | GDSII file reader, polygon extraction, pixel rasterization, anti-aliasing, field-of-view selection |
| **Deliverables** | Module `semicon.geometry.raster`; function `rasterize(gdsii_path, layer, M, N, pixel_size_nm, center) → PixelMask` |
| **Dependencies** | 0.2 (math_utils), 0.5 (units) |
| **Est. complexity** | Medium-High (3 weeks) |
| **Validation milestone** | Known GDSII → known PixelMask; unit tests with test structures |

#### WP 1.2: geo_process

| Aspect | Specification |
|---|---|
| **Scope** | Layer stack model, conformal deposition, trapezoidal etch profiles, CMP planarization, corner rounding; 10 structure types |
| **Deliverables** | Module `semicon.geometry.process`; function `build_geometry(pixel_mask, layer_stack, config) → HeightField, MaterialMap` |
| **Dependencies** | 1.1 (geo_raster) |
| **Est. complexity** | High (5 weeks) — **critical path** |
| **Validation milestone** | Each structure type produces correct height field and material map |

#### WP 1.3: geo_variability

| Aspect | Specification |
|---|---|
| **Scope** | LER (exponential ACF), LWR, CDU, overlay shift, sidewall angle variation, shape variation; all applied to height field edges |
| **Deliverables** | Module `semicon.geometry.variability`; function `apply_variability(height_field, material_map, config, seed) → HeightField_var, MaterialMap_var` |
| **Dependencies** | 1.2 (geo_process) |
| **Est. complexity** | Medium-High (3 weeks) |
| **Validation milestone** | LER 3σ measured on output matches configured 3σ within tolerance; overlay shift verified |

#### WP 1.4: phys_signal

| Aspect | Specification |
|---|---|
| **Scope** | SE yield (universal model), BSE yield (Everhart model), topographic contrast, material contrast, edge brightening, charging modulation, SE2 contribution |
| **Deliverables** | Module `semicon.physics.signal`; function `compute_yields(height_field, material_map, physics_config) → se_yield, bse_yield` |
| **Dependencies** | 1.3 (I4 boundary) |
| **Est. complexity** | High (4 weeks) |
| **Validation milestone** | Known height field → expected yield values; edge brightening verified at feature edges |

#### WP 1.5: phys_degrade

| Aspect | Specification |
|---|---|
| **Scope** | PSF kernel generation (Gaussian), 2D convolution, Poisson shot noise, Gaussian detector noise, charging blur |
| **Deliverables** | Module `semicon.physics.degrade`; function `degrade_yields(se_yield, bse_yield, config, seed) → se_yield_d, bse_yield_d` |
| **Dependencies** | 1.4 (phys_signal) |
| **Est. complexity** | Medium (2 weeks) |
| **Validation milestone** | Zero probe diameter → no blur; nonzero probe → measurable blur; noise-free mode → no noise |

#### WP 1.6: phys_formation

| Aspect | Specification |
|---|---|
| **Scope** | Signal scaling, gain/offset application, saturation/clipping, digitization to uint16, metadata recording |
| **Deliverables** | Module `semicon.physics.formation`; function `form_image(yield_map, detector_config) → SEMImage` |
| **Dependencies** | 1.5 (phys_degrade) |
| **Est. complexity** | Low (1 week) |
| **Validation milestone** | Known yield → known pixel values; saturation clipping verified |

#### WP 1.7: data_writer

| Aspect | Specification |
|---|---|
| **Scope** | Image file output (TIFF), JSON metadata writing, directory creation, dataset index update, file naming convention |
| **Deliverables** | Module `semicon.dataset.writer`; function `write_sample(image, metadata, ground_truth, config) → file_list` |
| **Dependencies** | 0.4 (image_io) |
| **Est. complexity** | Low-Medium (2 weeks) |
| **Validation milestone** | Written files are valid TIFF/JSON; round-trip read verified |

#### WP 1.8: orch_pipeline

| Aspect | Specification |
|---|---|
| **Scope** | Sequential pipeline orchestration: call M1–M8 in order, pass data objects, accumulate timing, handle errors |
| **Deliverables** | Module `semicon.orchestration.pipeline`; function `run_pipeline(config) → SEMImage, GroundTruth, Metadata` |
| **Dependencies** | 1.1–1.7 (all core modules) |
| **Est. complexity** | Medium (2 weeks) |
| **Validation milestone** | Full end-to-end run: known config → known output; regression test passes |

---

### 2.3 Stage 2: Automation

#### WP 2.1: data_groundtruth

| Aspect | Specification |
|---|---|
| **Scope** | Edge detection (height threshold → signed distance), CD measurement (top/bottom/height), contour extraction, material segmentation, edge type classification |
| **Deliverables** | Module `semicon.dataset.groundtruth`; function `generate_ground_truth(height_field, material_map, config) → GroundTruth` |
| **Dependencies** | 1.3 (I7 boundary: HeightField_var) |
| **Est. complexity** | Medium (3 weeks) |
| **Validation milestone** | CD values match height field within 0.1 nm; edge positions verified |

#### WP 2.2: config_parser

| Aspect | Specification |
|---|---|
| **Scope** | YAML/TOML parser, schema validation, type coercion, default resolution, cross-field validation, library resolution |
| **Deliverables** | Module `semicon.config.parser`; function `load_config(path) → Config`; structure and material library loaders |
| **Dependencies** | 0.1 |
| **Est. complexity** | Medium (2 weeks) |
| **Validation milestone** | Known YAML → known Config object; missing keys → default resolution; invalid → clear error |

#### WP 2.3: orch_job (Batch)

| Aspect | Specification |
|---|---|
| **Scope** | Job manifest generation, worker pool management, result aggregation, progress reporting, error handling, retry logic |
| **Deliverables** | Module `semicon.orchestration.job`; class `JobManager`; function `run_batch(config) → DatasetIndex` |
| **Dependencies** | 2.2 (config_parser), 1.8 (orch_pipeline) |
| **Est. complexity** | Medium (3 weeks) |
| **Validation milestone** | 100-image batch generates all files correctly; progress reported |

#### WP 2.4: CLI Entry Point

| Aspect | Specification |
|---|---|
| **Scope** | Command-line argument parsing, config file override, mode selection (single/batch/sweep/self-check), exit codes |
| **Deliverables** | Entry point `semicon-sim` in `pyproject.toml`; script `cli.py` with argparse |
| **Dependencies** | 2.2, 2.3 |
| **Est. complexity** | Low (2 weeks) |
| **Validation milestone** | `semicon-sim --help` works; each mode executes correctly |

#### WP 2.5: Validation Suite (L1–L3)

| Aspect | Specification |
|---|---|
| **Scope** | File completeness (L1), metadata consistency (L2), ground truth accuracy (L3) — implemented as functions callable from CLI |
| **Deliverables** | Module `semicon.validation`; function `validate_dataset(path) → ValidationReport` |
| **Dependencies** | 1.1–2.1 (all output-producing modules) |
| **Est. complexity** | Medium (3 weeks) |
| **Validation milestone** | Validation suite detects intentionally corrupted files |

#### WP 2.6: Self-Check Mode

| Aspect | Specification |
|---|---|
| **Scope** | Minimal pipeline with fixed seed → compare output hash to reference; all stages tested |
| **Deliverables** | CLI `--self-check` flag; reference output hashes embedded in code |
| **Dependencies** | 2.4 (CLI) |
| **Est. complexity** | Low (1 week) |
| **Validation milestone** | `--self-check` passes on clean install; fails if any module is modified |

---

### 2.4 Stage 3: Production

#### WP 3.1: Caching Subsystem

| Aspect | Specification |
|---|---|
| **Scope** | Deterministic height field cache, cache key = hash(input), LRU eviction, invalidation on config change, `--no-cache` flag |
| **Deliverables** | Module `semicon.orchestration.cache`; class `GeometryCache` |
| **Dependencies** | 1.3 (geo_variability — the beneficiary) |
| **Est. complexity** | Medium (3 weeks) |
| **Validation milestone** | Repeated generation with same params → cache hit; changed params → cache miss |

#### WP 3.2: Worker Pool (Parallel)

| Aspect | Specification |
|---|---|
| **Scope** | Static pool (batch) and dynamic pool (sweep), process isolation, result aggregation, error isolation, progress reporting |
| **Deliverables** | Enhancement to `orch_job` — parallel worker pool replacing sequential loop |
| **Dependencies** | 2.3 (orch_job) |
| **Est. complexity** | Medium (3 weeks) |
| **Validation milestone** | 100-image batch with 4 workers completes in ~25% of sequential time |

#### WP 3.3: Checkpoint & Recovery

| Aspect | Specification |
|---|---|
| **Scope** | Per-image checkpoint (output file = checkpoint), crash recovery (scan for incomplete files), failed jobs tracking, `--resume` flag |
| **Deliverables** | Enhancement to `orch_job` — checkpoint-aware execution; module `semicon.orchestration.checkpoint` |
| **Dependencies** | 2.3 (orch_job) |
| **Est. complexity** | Medium (2 weeks) |
| **Validation milestone** | Kill and restart mid-batch → resumes from last completed image |

#### WP 3.4: Regression Suite (L4–L5)

| Aspect | Specification |
|---|---|
| **Scope** | Version compatibility (L4), reproducibility (L5), output hash comparison, CD accuracy regression, cross-platform tolerance |
| **Deliverables** | Enhancement to `semicon.validation` — L4 and L5 checks; reference dataset stored in repository |
| **Dependencies** | 2.5 (validation suite) |
| **Est. complexity** | Medium (2 weeks) |
| **Validation milestone** | Same config + seed → same hash across runs |

#### WP 3.5: Documentation

| Aspect | Specification |
|---|---|
| **Scope** | API reference docs (docstrings → Sphinx/MkDocs), user guide, configuration reference, structure library guide, dataset format guide |
| **Deliverables** | `docs/` directory with Sphinx/MkDocs configuration; user-facing documentation |
| **Dependencies** | All modules |
| **Est. complexity** | Medium (3 weeks) |
| **Validation milestone** | Docs build without warnings; every public function documented |

#### WP 3.6: Distribution Packaging

| Aspect | Specification |
|---|---|
| **Scope** | pip-packageable distribution, dependency pinning, platform wheels, versioning scheme |
| **Deliverables** | Updated `pyproject.toml` with dependencies; `setup.cfg`/`setup.py`; `MANIFEST.in` for library data |
| **Dependencies** | All modules |
| **Est. complexity** | Low (2 weeks) |
| **Validation milestone** | `pip install .` in fresh environment → all tests pass |

#### WP 3.7: Performance Profiling

| Aspect | Specification |
|---|---|
| **Scope** | Per-stage timing, memory profiling, disk I/O profiling, bottleneck identification, optimization recommendations |
| **Deliverables** | Performance report; optimized hot paths (if any); baseline benchmarks |
| **Dependencies** | 3.1–3.2 |
| **Est. complexity** | Medium (2 weeks) |
| **Validation milestone** | Per-image time meets target (< 3 s at 1024×1024) |

---

## 3. WBS Summary

| Stage | Packages | Effort (team-weeks) | Dependencies |
|---|---|---|---|
| Stage 0: Foundation | 6 | 3 | None |
| Stage 1: Core Pipeline | 8 | 22 | Stage 0 |
| Stage 2: Automation | 6 | 14 | Stage 1 |
| Stage 3: Production | 7 | 17 | Stage 2 |
| **Total** | **27** | **56** | — |

*Note: Parallel execution reduces wall-clock time from 56 team-weeks to ~36 weeks with 3–4 developers.*

---

## Sources

- [I3] PMI, *Practice Standard for Work Breakdown Structures*, 3rd ed. PMI, 2019.
- [I4] S. McConnell, *Software Estimation: Demystifying the Black Art*, Microsoft Press, 2006.
- Phase 4.2, Document 02 — Module Interface Inventory (10 modules).
- Phase 4.5, Document 08 — Final Certification (recommended implementation order).
