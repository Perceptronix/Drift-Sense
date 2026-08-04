# Repository Structure

**Research Phase:** 5.3
**Document:** 06_repository_structure.md
**Date:** 2026-07-30

---

## 1. Physics Engine Source Tree

```
src/semicon/physics/
│
├── __init__.py                     ← Public API re-exports
│
├── signal.py                       ← PUBLIC phys_signal (M4, I4 producer)
│
├── _signal/                        ← phys_signal internals
│   ├── __init__.py
│   ├── yield_computer.py           ← SE + BSE yield per pixel
│   ├── topography_engine.py        ← Surface normals, cosθ
│   ├── edge_effects.py             ← Edge brightening
│   ├── charging_engine.py          ← Charging modulation
│   └── signal_assembler.py         ← SE1+SE2 assembly, I4 validation
│
├── degrade.py                      ← PUBLIC phys_degrade (M5, I5 producer)
│
├── _degrade/                       ← phys_degrade internals
│   ├── __init__.py
│   ├── psf_generator.py            ← Gaussian PSF kernel
│   ├── blur_applier.py             ← FFT convolution
│   ├── shot_noise.py               ← Poisson noise
│   ├── detector_noise.py           ← Gaussian read noise
│   └── degrade_assembler.py        ← Degradation order, I5 validation
│
├── formation.py                    ← PUBLIC phys_formation (M6, I6 producer)
│
├── _formation/                     ← phys_formation internals
│   ├── __init__.py
│   └── image_former.py             ← Digitization, saturation
│
└── _shared/                        ← Shared internals
    ├── __init__.py
    ├── material_properties.py      ← MaterialRecord dataclass, store, lookup
    └── physics_utils.py            ← Sampling kernels, PSF sizing, angle math
```

---

## 2. Public vs Internal API Policy

| Level | Convention | Access Rule |
|---|---|---|
| **Public** | `semicon.physics.signal`, `.degrade`, `.formation` | Stable API — follows Phase 4.2 contracts. Exported in `physics/__init__.py` |
| **Internal** | `semicon.physics._signal.*`, `._degrade.*`, `._formation.*`, `._shared.*` | Private (leading underscore). May change. Not exported |

### Public API Surface (frozen)

```
semicon.physics.signal.compute_yields(height_field, material_map, physics_config) → YieldMaps
semicon.physics.degrade.degrade_yields(yield_maps, degradation_config, seed) → YieldMaps
semicon.physics.formation.form_image(yield_maps, detector_config) → SEMImage, FormationRecord
semicon.physics.signal.load_material_library(path=None) → MaterialLibrary
```

All return **dataclass objects** from Phase 4.2 (D7–D9): `YieldMaps`, `SEMImage`, `FormationRecord`, plus the material library handle.

### Internal API Example

```
_signal.yield_computer.compute_se1(material_props, cos_theta, tilt_exponent) → np.ndarray[float64]
_signal.yield_computer.compute_bse(material_eta, material_map) → np.ndarray[float64]
_degrade.psf_generator.gaussian_kernel(fwhm_nm, pixel_size_nm) → np.ndarray[float64]
_degrade.blur_applier.convolve_fft(signal, kernel) → np.ndarray[float64]
_formation.image_former.digitize(signal, gain, offset, bit_depth) → np.ndarray[uint16]
```

---

## 3. Data Object Module (Foundation)

The physics engine consumes/produces objects defined in `semicon.foundation.datatypes` (Phase 4.2, D3–D9):

```
semicon/foundation/datatypes.py
├── HeightField      (D5 — float64 M×N, nm)
├── MaterialMap      (D6 — uint8 M×N, IDs 0–6)
├── YieldMaps        (D7 — se_yield + bse_yield, float64)
├── SEMImage         (D8 — uint16/uint8 M×N + FormationRecord)
├── GroundTruth      (D9 — produced downstream)
└── Config objects   (D1 — PhysicsConfig, DegradationConfig, DetectorConfig)
```

**Frozen rule:** Physics modules never define their own copies of these objects; they import from foundation.

---

## 4. Config & Library Data Tree

```
config/
├── defaults.yml                     ← Default PhysicsConfig / DegradationConfig / DetectorConfig
├── library/
│   ├── materials.yml                ← Material library (v1 pinned: materials_v1.yml)
│   └── materials_v1.yml             ← Pinned certified reference set
└── examples/
    ├── iso_line_sem.yml             ← Full physics section example
    └── physics_only.yml             ← Physics-test config
```

---

## 5. Test Tree

```
tests/
├── conftest.py                     ← Physics fixtures (synthetic HeightField, reference yield maps)
├── unit/
│   └── physics/
│       ├── test_material_properties.py
│       ├── test_physics_utils.py
│       ├── test_yield_computer.py
│       ├── test_topography_engine.py
│       ├── test_edge_effects.py
│       ├── test_charging_engine.py
│       ├── test_signal_assembler.py
│       ├── test_psf_generator.py
│       ├── test_blur_applier.py
│       ├── test_shot_noise.py
│       ├── test_detector_noise.py
│       ├── test_degrade_assembler.py
│       └── test_image_former.py
├── module/
│   └── test_physics_modules.py     ← L1: public module contracts
├── interface/
│   ├── test_i4_geometry_physics.py ← L2: geometry → physics boundary
│   ├── test_i5_physics_internal.py
│   └── test_i6_physics_image.py
├── pipeline/
│   └── test_physics_pipeline.py    ← L3: HeightField → SEMImage
├── scientific/
│   └── test_physics_scientific.py  ← L4: yield vs published, noise stats, PSF width
└── data/
    ├── reference_yields/           ← golden .npy yield maps
    ├── reference_images/           ← golden .tiff SEM images
    ├── reference_hashes.json       ← regression hashes
    └── materials_test.yml          ← test fixture library
```

---

## 6. File Organization Rules

| Rule | Description |
|---|---|
| One responsibility per file | Matches module breakdown (Doc 02) |
| Internal packages use underscore | `_signal`, `_degrade`, `_formation`, `_shared` |
| Public modules expose only contract functions | No extra public symbols |
| All functions typed | mypy --strict compliant |
| NumPy docstrings on public functions | Sphinx-documented |
| Material property constants colocated | In `_shared/material_properties.py`, not scattered |

---

## 7. Import Dependency Rules (No Cycles)

```
foundation ← physics._shared ← physics._signal ← physics.signal (I4)
foundation ← physics._shared ← physics._degrade ← physics.degrade (I5)
foundation ← physics._formation ← physics.formation (I6)
geometry (datatypes only) ← physics.*     [import direction: geometry does NOT import physics]
physics → dataset, orchestration          [forbidden — physics is downstream-only producer]
```

**Frozen rule:** Physics modules import geometry **data-object types only** (`HeightField`, `MaterialMap` from foundation.datatypes). No geometry algorithms. Physics never imports dataset or orchestration.

---

## 8. Golden Reference Data

| Fixture | Purpose | Generated By |
|---|---|---|
| Flat Si reference | Baseline yield map | Step 3 synthetic |
| 45° slope reference | Topographic contrast | Step 3 synthetic |
| Line/space SEM image | I6 end-to-end golden | Step 7 |
| Contact array SEM image | High-density golden | Step 7 |
| Noise-off reference | Determinism baseline | Step 6 |
| Charging-off reference | Charging identity check | Step 4 |

Golden hashes recorded in `tests/data/reference_hashes.json`.

---

## Sources

- Phase 4.2, Document 03 — Canonical data objects (D3–D9).
- Phase 4.2, Document 04 — API contracts (I4, I5, I6).
- Phase 5.2, Document 05 — Geometry repository structure (conventions reused).
- Phase 5.1, Document 06 — Development environment.
- [G8] S. McConnell, *Code Complete*, 2nd ed., 2004 (file organization).
