# SEMICON 2026 Synthetic SEM Image Generator — DG1

**Version:** 0.1.0 | **Status:** DG1 Complete | **License:** CC BY 4.0

A deterministic, physics-based simulator that generates synthetic SEM images
from GDSII semiconductor layouts.  Implements the frozen specifications from
Phases 1–5.5 of the Applied Materials SEMICON 2026 research program.

---

## Quick Start

```bash
cd simulator
pip install -e .                     # install package
python generate.py build-library --out structure_library/semicon.gds
python generate.py self-check        # verify system health (0.3 s)
python generate.py run               # single iso_line image
python generate.py batch --n 20 --out demo_output  # 20-image demo dataset
```

---

## Project Structure

```
simulator/
├── generate.py                  CLI entry point
├── src/semicon/                 Source package
│   ├── foundation/              Data types, RNG, math, units, I/O
│   ├── geometry/                Geometry Engine (I1→I3)
│   │   ├── raster.py            Public I1 producer
│   │   ├── process.py           Public I2 producer
│   │   ├── variability.py       Public I3 producer
│   │   ├── structures.py        10 structure builders
│   │   ├── _raster/             GDSII reader/writer, rasterizer, mask builder
│   │   ├── _process/            Process simulator, recipes
│   │   └── _variability/        Random fields, LER, overlay, CDU
│   ├── physics/                 SEM Physics Engine (I4→I6)
│   │   ├── signal.py            Public I4 producer
│   │   ├── degrade.py           Public I5 producer
│   │   ├── formation.py         Public I6 producer
│   │   ├── _signal/             Yield, edge effects, charging
│   │   ├── _degrade/            PSF, blur, shot noise, detector noise
│   │   ├── _formation/          Digitisation
│   │   └── _shared/             Material property library
│   ├── dataset/                 Ground truth, writer, splits
│   └── orchestration/           Config, pipeline, job runner, CLI
├── configs/                     defaults.yml, materials.yml, demo.yml
├── structure_library/           GDSII structure fixtures
├── tests/                       Unit, interface, pipeline, scientific tests
├── demo_output/                 Generated demo dataset (20 images)
├── docs/                        (placeholder for full docs)
└── scripts/                     (utility scripts)
```

---

## Architecture (Frozen, Phase 5.1–5.4)

```
Config YAML ─→ Geometry Engine ─→ Physics Engine ─→ Dataset
  (M9)          (I1:GDSII →           (I4:I4 →        (I7,I8:
                  M1→M2→M3: H/M)       M4→M5→M6:      GT, writer)
                                          image)
```

**Key interfaces:** I1 (raster mask), I2 (det H/M), I3 (var H/M), I4 (yield maps), I5 (degraded yield), I6 (SEMImage), I7 (ground truth), I8 (file writer)

**Frozen specifications:** Phases 1–5.5 (210 research documents)

---

## Structure Types (10 Frozen)

| Type | Features | Material Contrast |
|---|---|---|
| iso_line | Single line | Topographic |
| dense_ls | Line/space array | Topographic |
| contact | Contact hole array | Material (W in SiO₂) |
| via | Via hole array | Material (Cu in SiO₂) |
| trench | Recessed trench | Topographic |
| fin | Raised fins | Topographic + material |
| gate | Gate bar over fins | Multi-material |
| sti | Shallow trench isolation | Material (SiO₂ in Si) |
| bimaterial | Side-by-side blocks | Pure material contrast |
| pitch_std | Mixed-pitch lines | Multi-pitch |

---

## Material Properties (v1, Phase 2.6–5.3)

| Material | ID | δ₀ (SE) | η (BSE) | Escape (nm) | Type |
|---|---|---|---|---|---|
| Vacuum | 0 | 0.00 | 0.00 | 0.0 | — |
| Silicon | 1 | 0.50 | 0.22 | 2.5 | Semiconductor |
| SiO₂ | 2 | 0.60 | 0.18 | 2.8 | Dielectric |
| SiN | 3 | 0.52 | 0.18 | 2.6 | Dielectric |
| Copper | 4 | 0.40 | 0.35 | 1.8 | Conductor |
| Tungsten | 5 | 0.35 | 0.53 | 1.5 | Conductor |
| Photoresist | 6 | 0.80 | 0.03 | 4.0 | Organic |

---

## Testing

```bash
pytest tests/                      # all 65 tests
pytest tests/unit/                 # unit tests only
pytest tests/scientific/           # L4 scientific validation
```

---

## Demo Dataset

The `demo_output/` directory contains a 20-sample engineering smoke-test dataset:

| Item | Count |
|---|---|
| Images | 20 (16-bit TIFF, 320×320) |
| Ground truth | 20 (JSON with edge maps, CD values, contours) |
| Material maps | 20 (PNG, false-colour) |
| Metadata | 20 config + 20 metadata JSON |
| Checksums | SHA-256 registry (144 files verified) |
| Splits | train=10, val=0, test=10 (small-stratum rounding) |

**Not DS1** — This is an engineering smoke test only.

---

## DG1 Completion Report

### Features Implemented

| Feature | Status |
|---|---|
| GDSII parser (pure-Python, read + write) | ✅ |
| 10 structure types (polygon generators) | ✅ |
| Anti-aliased rasterizer (SS=4) | ✅ |
| 2.5D process simulator (deposit/etch/planarize/corner) | ✅ |
| LER (exponential-ACF Gaussian process) | ✅ |
| Overlay and CDU | ✅ |
| Universal SE yield (P2 formula) | ✅ |
| Everhart BSE yield | ✅ |
| SE2 contribution | ✅ |
| Edge brightening (P5) | ✅ |
| Charging model (P6, isolated-only guard) | ✅ |
| Gaussian PSF convolution | ✅ |
| Shot noise (Poisson) | ✅ |
| Detector noise (Gaussian) | ✅ |
| Digitisation (round-half-even) | ✅ |
| Ground truth (edge maps, CD, contours) | ✅ |
| Dataset writer (canonical layout, checksums) | ✅ |
| Config system (YAML, defaults, validation) | ✅ |
| Pipeline orchestrator | ✅ |
| Batch job runner | ✅ |
| CLI (build-library, run, batch, self-check) | ✅ |

### Validation Results

| Level | Status | Tests |
|---|---|---|
| Unit (L0) | ✅ 52 tests pass | Per-module correctness |
| Interface (I1–I6) | ✅ All postconditions verified | Cross-module handoff |
| Pipeline (L3) | ✅ End-to-end | Config → image → output |
| Scientific (L4) | ✅ Si δ ∈ [0.4,0.8]; ordering; PSF; CD | Published-range compliance |
| Regression | ✅ Deterministic | Same seed → bit-identical image |

### Performance

| Metric | Value |
|---|---|
| Per-image (320×320) | ~0.24 s (sequential) |
| Per-image (1024×1024) | ~0.5 s (sequential) |
| 20-image demo | ~5 s |
| Memory (1024×1024) | ~50 MB RSS |

### Known Limitations

| Limitation | Impact | Plan |
|---|---|---|
| Pure-Python GDSII (not gdspy) | Slower for >10⁵ polygons | Migrate to gdstk when available |
| cosθ clamp at 0.7 (~45° max effective tilt) | Wall signal limited | Acceptable for CD-SEM |
| 2.5D only (no overhangs) | Cannot represent undercut profiles | 3D mesh optional in DG2 |
| Corner rounding: median filter blurs straight edges | Minor CD offset on smoothed lines | Acceptable for demo |
| Stratum rounding in splits | Small datasets show val=0 | Expected behavior |

---

*Generated 2026-07-30. Implements frozen Phases 1–5.5 specifications.*
