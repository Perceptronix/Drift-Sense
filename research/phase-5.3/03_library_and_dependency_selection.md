# Library & Dependency Selection

**Research Phase:** 5.3
**Document:** 03_library_and_dependency_selection.md
**Date:** 2026-07-30

---

## 1. Dependency Stack Overview

| Category | Library | Status | Version Policy |
|---|---|---|---|
| Numerical core | **NumPy** | Core | `numpy>=1.25,<2.0` |
| Scientific ops | **SciPy** | Core | `scipy>=1.11,<2.0` |
| Image processing | **scikit-image** | Core | `scikit-image>=0.21,<1.0` |
| Image I/O | **Pillow** | Core | `pillow>=10,<11` |
| Configuration | **PyYAML** | Core | `pyyaml>=6.0,<7.0` |
| Testing | pytest, hypothesis | Dev | Pin exact |
| Profiling | cProfile, line_profiler, memory_profiler | Dev | Pin exact |
| Quality | black, ruff, mypy | Dev | Pin exact |
| Docs | Sphinx + numpydoc | Dev | Pin exact |

---

## 2. Numerical Computation: NumPy + SciPy

| Function | Used For |
|---|---|
| `numpy.fft` / `scipy.signal.fftconvolve` | PSF convolution (blur_applier) |
| `scipy.ndimage.map_coordinates` | Surface-normal sampling, PSF kernel resampling |
| `scipy.ndimage.sobel` / central-difference gradients | Surface normals (topography_engine) |
| `scipy.ndimage.uniform_filter` | Isolated-structure masks for charging (smoothing) |
| `scipy.ndimage.label` | Connected components (edge/feature classification) |
| `numpy.random.Generator` | Deterministic seeded RNG (via rng_utils) |

**Alternatives considered:**

| Alternative | Verdict |
|---|---|
| **PyFFTW** | Faster FFT, but adds C dependency and non-trivial determinism concerns; `fftconvolve` suffices for 1024×1024 |
| **OpenCV** | Faster convolution, but float32 intermediate types break the float64 determinism contract (same rejection as Phase 5.2) |
| **Numba** | JIT acceleration possible later; adds compile-time complexity and risks deterministic first-call overhead — deferred to Future Optimization |

**Long-term maintainability:** NumPy/SciPy are the most-maintained scientific libraries in Python; no migration risk.

---

## 3. RNG Strategy

| Aspect | Decision |
|---|---|
| **Source** | `rng_utils` from foundation — single source for all seeded randomness |
| **Generator type** | `numpy.random.Generator` (PCG64) — not legacy `RandomState` (MT19937) |
| **Why PCG64** | Statistically robust; reproducible across platforms; modern default |
| **Noise seeds** | Derived from `noise_seed` in the hierarchical chain (Phase 4.3): Poisson + detector noise each get derived sub-seeds |
| **Alternatives** | `secrets` (non-deterministic — rejected); Python `random` (slower, weaker); external `randomgen` (adds dependency — unnecessary) |

**Implementation decision:** Poisson sampling via `Generator.poisson(lam, size)`. Gaussian via `Generator.normal(loc, scale, size)`. Both accept the same seeded Generator instance per image for a single deterministic stream.

---

## 4. Interpolation: scipy.ndimage

| Use | Method | Why |
|---|---|---|
| Surface normal computation | Central differences (no interpolation needed) | Exact on height-field grid |
| PSF kernel resampling (non-integer σ) | `map_coordinates`, order=3 | Smooth sub-pixel kernel |
| Overlay already handled in geometry | — | Not physics' concern |
| Charging potential smoothing | `uniform_filter` (box) | Deterministic, cheap |

**Alternative:** `scipy.interpolate.RegularGridInterpolator` — more flexible but heavier; only needed if off-grid queries arise (not in the frozen pipeline).

---

## 5. Array Acceleration

| Option | Status | Trade-off |
|---|---|---|
| **Vectorized NumPy** (primary) | **Implementation Decision** | Fully vectorized per-pixel operations; adequate for 1024×1024 (< 200 ms/step) |
| **NumPy + Cython** | Future Optimization | ~2–5× speedups; compile complexity; only if profiling demands |
| **Numba JIT** | Future Optimization | Easy decorators; first-call compile; determinism caveats |
| **GPU (CuPy / PyTorch)** | Rejected for v1 | Certified in Phase 4.3 (RD6): GPU not required; adds infra cost |

**Implementation decision:** Stay CPU-vectorized for v1. All algorithms are designed to be expressed as array ops, keeping the GPU path a straightforward future migration.

---

## 6. Image I/O & Config

| Library | Why | Alternative |
|---|---|---|
| **Pillow** | 16-bit TIFF/PNG for fixtures and test images | tifffile (heavier) |
| **PyYAML** | Material library + test configs in YAML (human-readable) | TOML (std library `tomllib` read-only; writing needs third-party) |

---

## 7. Profiling Tools

| Tool | Purpose | Alternative |
|---|---|---|
| **cProfile** (stdlib) | Function-level timing | py-spy (sampling, harder on Windows) |
| **line_profiler** | Per-line hot-spot analysis | — |
| **memory_profiler** | RSS/peak memory per stage | tracemalloc (stdlib, allocation-level) |

**Profiling policy:** Profile at Steps 3, 5, 7 gates with a standard 1024×1024 workload. Targets: each physics step < 200 ms; full physics pipeline < 1 s (matches Phase 5.1 per-image budget < 3 s).

---

## 8. Dependency Risk Mitigations

| Risk | Mitigation |
|---|---|
| FFT convolution memory for 4096×4096 | Pad-to-next-fast-size; `fftconvolve` handles in-place chunks; document 4096 max (≈ 128 MB per map) |
| NumPy 2.0 migration | Pin `<2.0`; keep dtype discipline |
| SciPy `fftconvolve` boundary modes | Use mode='same' + explicit padding policy (reflect for yield maps) |
| Poisson RNG speed | Vectorized `Generator.poisson` is fast; no loop |

---

## 9. Dependency Summary Table

| Library | Role | Used By | Min Version | Alternatives |
|---|---|---|---|---|
| numpy | Array core, RNG | All physics | 1.25 | — |
| scipy | fftconvolve, ndimage, gradients | blur_applier, topography_engine | 1.11 | PyFFTW (FFT only), OpenCV |
| scikit-image | distance transform (PSF sizing), measure | psf_generator, charging masks | 0.21 | OpenCV |
| pillow | Image I/O fixtures | tests | 10.0 | tifffile |
| pyyaml | Material library format | material_properties | 6.0 | TOML |
| cProfile / line_profiler | Profiling | dev | stdlib/latest | py-spy |
| pytest, hypothesis | Testing | all tests | 7.0 / 6.0 | unittest |
| black, ruff, mypy | Quality | dev toolchain | latest | yapf, flake8, pyright |
| sphinx + numpydoc | Docs | dev toolchain | 7.0 | MkDocs |

---

## Sources

- [P3] C. R. Harris et al., "Array programming with NumPy," *Nature*, vol. 585, 2020.
- [P4] P. Virtanen et al., "SciPy 1.0," *Nature Methods*, vol. 17, 2020.
- [P5] M. Matsumoto, T. Nishimura, "Mersenne Twister" (RNG background), 1998.
- [P6] M. E. O'Neill, "PCG: A Family of Simple Fast Space-Efficient Statistically Good Algorithms for Random Number Generation," 2014.
- Phase 4.3, Document 05 — Reproducibility strategy (seed chain).
- Phase 5.2, Document 03 — Geometry library selection (conventions reused).
