# Library & Dependency Selection

**Research Phase:** 5.2
**Document:** 03_library_and_dependency_selection.md
**Date:** 2026-07-30

---

## 1. Dependency Stack Overview

| Category | Library | Status | Version Policy |
|---|---|---|---|
| GDSII parsing | **gdspy** | Core | `gdspy>=1.6,<2.0` |
| Numerical core | **NumPy** | Core | `numpy>=1.25,<2.0` |
| Scientific operations | **SciPy** | Core | `scipy>=1.11,<2.0` |
| Image processing | **scikit-image** | Core | `scikit-image>=0.21,<1.0` |
| Image I/O | **Pillow** | Core | `pillow>=10.0,<11.0` |
| Testing | **pytest** + pytest-cov | Dev | Pin exact for CI |
| Linting | **ruff** | Dev | Pin exact |
| Formatting | **black**, **isort** | Dev | Pin exact |
| Static analysis | **mypy** (strict) | Dev | Pin exact |
| Documentation | **Sphinx** + numpydoc | Dev | Pin exact |

---

## 2. GDSII Parsing

### 2.1 Selected: gdspy

| Aspect | Assessment |
|---|---|
| **Why selected** | The de-facto standard Python GDSII library; active maintenance (2013–present); full support for all GDSII record types (BOUNDARY, PATH, SREF, AREF, TEXT); clean geometry API (`get_polygons()` returns flattened vertex arrays); pure-Python → no compilation; deterministic |
| **Alternatives** | **python-gdsii** (pure parser, no geometry API — requires manual flattening, low maintenance); **gdstk** (C++-backed successor by same author, faster, but younger and GDSII-flavored binary format focus); **custom parser** (full control but months of effort, high risk) |
| **Trade-offs** | gdspy is slower than gdstk for very large layouts (>10⁵ polygons) — acceptable for CD-SEM FOVs which contain at most a few hundred polygons; python-gdsii simpler but incomplete |
| **Long-term maintainability** | gdspy is frozen-stable API; if it ever becomes unmaintained, gdstk is a drop-in successor (same author, compatible API) — mitigation documented |

**Implementation decision:** Use `gdspy.GdsLibrary().load_gds(path)` then `.top_level()` cells → `.get_polygons(by_spec=True)` filtered by (layer, datatype). Flatten SREF/AREF recursion with visited-cell memoization.

### 2.2 Rationale Detail

| Criterion | gdspy | python-gdsii | gdstk | Custom |
|---|---|---|---|---|
| Maturity | ✅ High (10 yr) | ⚠️ Low | ⚠️ Medium | ❌ None |
| GDSII completeness | ✅ Full | ⚠️ Partial | ✅ Full | Depends |
| Flattening support | ✅ Built-in | ❌ Manual | ✅ Built-in | Manual |
| Determinism | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| Maintenance activity | ✅ Active | ❌ Stale | ✅ Active | N/A |
| Learning cost | ✅ Low | ⚠️ Medium | ⚠️ Medium | ❌ High |

---

## 3. Numerical Core: NumPy + SciPy

### 3.1 NumPy

**Why:** Non-negotiable foundation. All array operations, vectorized kernels, dtype control (float64 height fields, uint8 material maps), deterministic reduction control. No alternative exists for this ecosystem.

### 3.2 SciPy

| Function Family | Used For |
|---|---|
| `scipy.ndimage.distance_transform_edt` | Chebyshev/Euclidean distance for deposition, corner rounding |
| `scipy.ndimage.sobel`, `laplace` | Edge detection, gradient orientation |
| `scipy.ndimage.shift` | Overlay translation (order-1 spline) |
| `scipy.ndimage.uniform_filter` | CMP local polish window |
| `scipy.fft` | LER spectral synthesis (Gaussian random field) |
| `scipy.ndimage.label` | Connected components for edge/feature grouping |

**Alternatives:** None serious — scipy.ndimage is the standard. OpenCV `distanceTransform` is faster but C++-typed outputs complicate determinism; custom implementations duplicate well-tested code.

---

## 4. Image Processing: scikit-image

| Aspect | Assessment |
|---|---|
| **Why selected** | `distance_transform_edt`, `find_contours`, `measure.label` — clean, tested, array-native; pure Python + Cython → deterministic; integrates with NumPy typing |
| **Alternatives** | **OpenCV** (faster but float32-only intermediate types break float64 determinism contract; awkward Python API); **custom** (redundant with skimage) |
| **Trade-offs** | skimage is heavier dependency than OpenCV; acceptable for research tooling |
| **Long-term maintainability** | skimage is a SciPy-ecosystem project with conservative releases |

**Implementation decision:** Use skimage `distance_transform_edt` in preference to scipy.ndimage for corner-rounding fillets (metric control: Euclidean vs Chebyshev per step).

---

## 5. Image I/O: Pillow

| Aspect | Assessment |
|---|---|
| **Why selected** | Standard, maintained, pure-Python-readable; supports 16-bit TIFF (LZW) and PNG for MaterialMap debugging outputs and test fixtures |
| **Alternatives** | **tifffile** (better TIFF fidelity, GeoTIFF tags, but heavier); **imageio** (wrapper over Pillow) |
| **Trade-offs** | Pillow has limited TIFF tag customization — irrelevant since Phase 4.4 writes metadata as sidecar JSON, not TIFF tags |
| **Long-term maintainability** | Pillow is one of the most maintained Python libraries |

---

## 6. Testing and Tooling

| Tool | Why Selected | Alternatives Considered |
|---|---|---|
| **pytest 7+** | De-facto standard; fixtures, parametrize, approx; golden-file plugins (`pytest-regressions`) | unittest (stdlib — verbose, no parametrize) |
| **hypothesis** | Property-based testing for rasterizer invariants | QuickCheck port; manual property loops |
| **ruff** | Fast linting (Rust), superset of flake8+isort | flake8 (slow), pylint (noisy) |
| **black** | Deterministic auto-format; zero-config style | yapf (config-heavy), autopep8 (pep8-only) |
| **mypy --strict** | Industry-standard gradual typing | pyright (Microsoft, less common in scientific) |
| **Sphinx + numpydoc** | Auto-API docs; NumPy docstring convention | MkDocs (good, but autodoc weaker) |

---

## 7. Dependency Risk Mitigations

| Risk | Mitigation |
|---|---|
| gdspy unmaintained | gdstk drop-in path documented; reader wrapped behind internal `gdsii_reader` abstraction |
| skimage version churn | Pin `<1.0`; only use stable `distance_transform_edt` + `find_contours` |
| NumPy 2.0 migration | Pin `<2.0` until ecosystem settles; keep dtype discipline (float64, uint8) |
| Hypothesis non-determinism | Property tests use fixed `random.Random` seed; failing examples auto-shrunk and recorded |

---

## 8. Dependency Summary Table

| Library | Role | Required By | Min Version | Alternative(s) |
|---|---|---|---|---|
| gdspy | GDSII parsing | geo_raster | 1.6 | gdstk, python-gdsii, custom |
| numpy | Numerical core | All geometry | 1.25 | — |
| scipy | ndimage, fft, signal | geo_process, geo_variability | 1.11 | OpenCV (partial) |
| scikit-image | distance transform, contours | geo_process, geo_variability | 0.21 | OpenCV, custom |
| pillow | Image I/O (test fixtures, debug) | geometry tests | 10.0 | tifffile, imageio |
| pytest | Testing | All | 7.0 | unittest |
| hypothesis | Property testing | rasterizer tests | 6.0 | — |
| ruff | Linting | Dev toolchain | latest | flake8, pylint |
| black | Formatting | Dev toolchain | latest | yapf, autopep8 |
| mypy | Static typing | Dev toolchain | 1.0 | pyright |
| sphinx | Documentation | Dev toolchain | 7.0 | MkDocs |

---

## Sources

- [G1] H. Koppelaar, *gdspy: A Python Library for GDSII Layout*, 2015.
- [G2] J. D. Foley et al., *Computer Graphics: Principles and Practice*, 3rd ed. Addison-Wesley, 1995.
- [G3] S. van der Walt et al., "scikit-image: image processing in Python," *PeerJ*, 2014.
- [G4] C. R. Harris et al., "Array programming with NumPy," *Nature*, vol. 585, 2020.
- [G5] P. Virtanen et al., "SciPy 1.0," *Nature Methods*, vol. 17, 2020.
- Phase 5.1, Document 06 — Development environment (toolchain baseline).
