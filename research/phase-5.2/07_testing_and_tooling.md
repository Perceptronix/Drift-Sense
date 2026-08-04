# Testing Strategy & Tooling

**Research Phase:** 5.2
**Document:** 07_testing_and_tooling.md
**Date:** 2026-07-30

---

## 1. Test Tier Architecture

Five test tiers, each with distinct purpose and gate:

```
Tier 1: Unit Tests          (L0 — every PR)
Tier 2: Golden Reference    (L0/L1 — regression safety)
Tier 3: Property-Based      (L0 — invariant guarantees)
Tier 4: Numerical Validation (L4 — scientific accuracy)
Tier 5: Regression Suite    (L1–L4 — release gate)
```

---

## 2. Tier 1: Unit Tests

| Aspect | Specification |
|---|---|
| **Scope** | Every internal module; every public function; error paths |
| **Framework** | pytest with parametrize and fixtures |
| **Coverage target** | ≥ 85% line per geometry module (above the 80% project floor) |
| **Style** | Arrange–Act–Assert; one behavior per test; no network; no randomness (seeded) |

**Representative unit tests:**

| Module | Tests |
|---|---|
| gdsii_reader | Valid file → polygons; missing file → GeometryError; missing layer → GeometryError; empty layer → empty list; SREF recursion depth; AREF arrays; PATH → polygon conversion |
| polygon_rasterizer | Unit square coverage = 1.0 center, 0.25 corner; 45° line coverage monotonic; concavity; hole even-odd; sub-pixel shifts change coverage linearly |
| mask_builder | Threshold 0.5 boundary; dimension mismatch error; center offset FOV |
| layer_stack | Valid plan ordering; unknown material error; zero-thickness error |
| deposition | Conformal: floor + walls both +t; PVD: partial fill by conformality |
| etch | Vertical (90°) sidewall; angled (85°) trapezoid Δx = h/tan(θ); isotropic undercut |
| cmp | Global clip; local polish window; over-polish depth |
| corner_rounding | Radius at corner; no change away from corner |
| ler_generator | Zero amplitude → identity; seeded → reproducible; mean-zero |
| overlay_engine | Integer shift lossless; sub-pixel shift bilinear; out-of-FOV zero-fill |
| variability_applier | Application order; record fields; dimensions preserved |

---

## 3. Tier 2: Golden Reference Tests

| Aspect | Specification |
|---|---|
| **Purpose** | Pin outputs to known-good values; catch regressions on every refactor |
| **Mechanism** | Precomputed reference arrays (`.npy`) + recorded SHA-256 hashes; `pytest-regressions` for numeric arrays |
| **Fixtures** | 10 GDSII structure fixtures → golden PixelMask, HeightField_det, MaterialMap_det, HeightField_var |
| **Tolerance** | Bitwise for determinism-critical outputs; `atol=1e-9` for float geometry ops |
| **Golden generation** | `scripts/generate_golden.py` — run once, reviewed, committed; regeneration only via documented procedure |

**Golden hash registry:**

| Artifact | Hash Registry |
|---|---|
| PixelMask (10 fixtures) | `reference_hashes.json` |
| HeightField_det (10) | `reference_hashes.json` |
| MaterialMap_det (10) | `reference_hashes.json` |
| HeightField_var (10, fixed seeds) | `reference_hashes.json` |

---

## 4. Tier 3: Property-Based Tests

| Aspect | Specification |
|---|---|
| **Purpose** | Discover counterexamples where hand-written cases miss |
| **Framework** | Hypothesis (seeded, shrinking, example recording) |
| **Seed policy** | Fixed `random.Random(0)` per test module for reproducibility |

**Property tests defined:**

| Property | Invariant |
|---|---|
| Rasterization area conservation | Σ coverage = polygon_area / pixel_area ± 1 px² (for any polygon) |
| Rasterization boundedness | coverage ∈ [0, 1] always |
| Rasterization translation | shift polygon by k px → coverage shifts by k px |
| LER zero-mean | mean(displacement) ≈ 0 for any seed |
| Overlay invertibility | shift by (dx, dy) then (−dx, −dy) → original (integer shifts) |
| CMP monotonicity | CMP output height ≤ input height everywhere |
| Deposition monotonicity | deposition output height ≥ input height everywhere |
| Material ID validity | MaterialMap values always ∈ {0..6} after any operation sequence |

---

## 5. Tier 4: Numerical Validation

| Aspect | Specification |
|---|---|
| **Purpose** | Verify scientific accuracy against the frozen specifications (Phase 3.4, Phase 4.4 GT precision) |
| **When** | L4 gate (M1) |
| **Pass criteria** | |

| Metric | Target | Method |
|---|---|---|
| CD accuracy | |CD_meas − CD_config| ≤ 0.1 nm | Ground-truth measurement on generated height field |
| Trapezoid angle | ± 0.1° | Profile fit |
| Conformal thickness | ± 0.1 nm | Wall cross-section |
| LER 3σ | configured ± 0.3 nm | Edge position statistics |
| LER ξ | configured ± 10% | Exponential fit of measured ACF |
| LER ρ | configured ± 0.05 | Cross-correlation of paired edges |
| Overlay shift | ± 0.1 nm | Feature centroid displacement |
| CDU batch spread | σ_config ± 0.1 nm | Across-batch CD histogram |
| Corner radius | ± 0.2 nm | Fillet curvature fit |

**Statistical rigor:** LER statistics require line length ≥ 20ξ for stable estimates; batch CDU requires ≥ 100 samples per sigma. Test fixtures sized accordingly.

---

## 6. Tier 5: Regression Suite

| Aspect | Specification |
|---|---|
| **Purpose** | Full Geometry Engine release gate — catches cross-module breakage |
| **Scope** | Tier 1–4 all green + interface tests + pipeline test + determinism test |
| **Determinism test** | Run full geometry pipeline twice with same config + seed → SHA-256 of HeightField_var identical |
| **Cross-seed independence** | Seed A ≠ seed B → outputs differ |
| **Execution** | `pytest` full suite; CI runs on every merge to `develop` and `main` |

---

## 7. Tooling Configuration

### 7.1 Python & Build

| Tool | Selection | Why |
|---|---|---|
| Python 3.11+ | — | Frozen in Phase 5.1 |
| setuptools + pyproject.toml | — | PEP 517/518; single config source |
| Package name | `semicon` | Frozen namespace |
| Dependency pinning | `<2.0` minors | Reproducibility + ecosystem stability |

### 7.2 Code Quality

| Tool | Config | Role |
|---|---|---|
| **black** | line-length 88; skip-string-normalization=false | Deterministic formatting |
| **isort** | profile="black" | Import ordering consistent with black |
| **ruff** | select E,F,W,I,N,D; ignore D2xx for internals | Lint + docstring enforcement |
| **mypy** | --strict; disallow_untyped_defs; warn_unused_ignores | Type safety |

### 7.3 Pre-commit Hooks

| Hook | Runs |
|---|---|
| black --check | Formatting |
| ruff check | Lint |
| mypy | Types |
| pytest (unit + property, fast) | Tests |

### 7.4 Documentation Generation

| Tool | Config | Output |
|---|---|---|
| Sphinx + numpydoc | autodoc, napoleon | `docs/api/` HTML |
| Docstring requirement | All public functions | Enforced by ruff D rules |

---

## 8. Tooling Justification Summary

| Tool | Selected Over | Decision Rationale |
|---|---|---|
| pytest | unittest | Fixtures, parametrize, plugin ecosystem |
| hypothesis | manual property loops | Automatic shrinking; recorded counterexamples |
| ruff | flake8 + isort | One fast tool; Rust-based |
| black | yapf, autopep8 | Zero-config determinism |
| mypy | pyright | Scientific-ecosystem default; strict mode |
| Sphinx+numpydoc | MkDocs | Auto API docs from NumPy-style docstrings |
| pytest-regressions | manual golden files | Numeric-array golden comparison built-in |

---

## Sources

- [G9] J. B. Rainsberger, *JUnit Recipes*, Manning, 2004 (test structure).
- [G10] D. MacIver, *Property-Based Testing with PropEr, Erlang, and Hypothesis*, 2019.
- Phase 4.5, Document 08 — Validation strategy L0–L5.
- Phase 5.1, Document 05 — Validation gates.
- Phase 5.1, Document 06 — Development environment.
- Phase 3.4 — Geometry Engine certification criteria (numerical tolerances).
