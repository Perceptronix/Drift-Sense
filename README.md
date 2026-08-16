# SEMICON 2026 : Synthetic SEM Image Generator (Drift-Sense)

**Applied Materials Hackathon** · Synthetic Scanning Electron Microscope (SEM) image generator for semiconductor inspection, defect detection, and navigation-error recovery (Drift-Sense) benchmarking.

> A deterministic, physics-based simulator that generates large-scale, scientifically-grounded synthetic SEM datasets with pixel-accurate ground truth from GDSII semiconductor layouts to training-ready 16-bit TIFF images

> DataSet : https://huggingface.co/datasets/yogeshn07/SEMICON-2026-Localization-DS5-v1

---

## Component 2 Submission Quick-Run (Mandatory Files)

This repository now includes the exact standalone scripts needed for direct evaluation:

- `dataset_generator.py` (standalone synthetic pair generator)
- `localization_inference.py` (standalone localization inference entry point)
- `model_weights/siamese_baseline_best.pt` (DL weight artifact, if needed)
- `src/train_siamese.py` (training script)
- `requirements.txt` (full pinned environment list)
- `CITATION_REFERENCES.md` (augmentation/noise reference list)

### Fresh-machine setup

```bash
git clone https://github.com/Perceptronix/Drift-Sense.git
cd Drift-Sense
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 1) Generate sample image pairs (Reference + Search + GT center)

```bash
python dataset_generator.py \
  --architecture-style DRAM \
  --num-pairs 3 \
  --output-dir submission_demo
```

Ground truth is saved in:
- `submission_demo/ground_truth.json`
- `submission_demo/ground_truth.csv`

Each entry stores the true center `(center_x, center_y)` of the reference patch in the search image.

### 2) Run localization inference (the script used for scoring)

```bash
python localization_inference.py \
  --reference-image submission_demo/reference/pair_00000_reference.png \
  --search-image submission_demo/search/pair_00000_search.png
```

Output format is a single coordinate line:
```text
x,y
```

## Table of Contents

- [1. Project Overview](#1-project-overview)
- [2. The Challenge](#2-the-challenge)
- [3. Key Features](#3-key-features)
- [4. Repository Structure](#4-repository-structure)
- [5. System Architecture](#5-system-architecture)
- [6. Scientific Foundations](#6-scientific-foundations)
- [7. Dataset Specification (DS1–DS5)](#7-dataset-specification-ds1ds5)
- [8. How Datasets Are Generated](#8-how-datasets-are-generated)
- [9. Ground Truth Format](#9-ground-truth-format)
- [10. Metadata Schema & Usage](#10-metadata-schema--usage)
- [11. Training Guide](#11-training-guide)
- [12. Validation & Quality Gates](#12-validation--quality-gates)
- [13. Quick Start](#13-quick-start)
- [14. Testing](#14-testing)
- [15. Project Status (DG1–DG7)](#15-project-status-dg1dg7)
- [16. Research Documentation](#16-research-documentation)
- [17. License & Citation](#17-license--citation)

---

## 1. Project Overview

The **SEMICON 2026 Synthetic SEM Image Generator** is a production-grade, physics-based simulation system that synthesizes realistic Scanning Electron Microscope (SEM) images of semiconductor structures — DRAM arrays and FinFET logic — together with pixel-accurate ground truth and full scientific metadata with proper image datasets in hugging face.

It was developed through **21 research phases** (210+ documents) that froze the physics, geometry, architecture, and dataset specifications before a single line of implementation code was written. The result is a simulator that is:

- **Deterministic** — same seed + config + platform → bitwise-identical images (SHA-256 verified).
- **Physics-based** — grounded in published SEM literature (SE/BSE yield models, PSF, noise, charging).
- **Reproducible** — every sample carries the full provenance chain (seeds, config, version, hashes).
- **Scalable** — checkpointed, resumable, chunked production generation of 100,000-image datasets.

The project targets the **Drift-Sense navigation-error recovery task**: locating a small, high-resolution SEM reference image inside a larger, lower-resolution search image of the same semiconductor die.

| Attribute | Value |
|---|---|
| Simulator package | `semicon-sim` v0.1.0 |
| Language | Python ≥ 3.10 |
| License | CC BY 4.0 |
| Primary deliverable | DS5 — 100,000 training images @ 1024×1024, 16-bit, 1.0 nm/px |
| Master seeds | DS1=1001, DS2=2002, DS3=3003, DS4=4004, DS5=5005 (frozen) |

---

## 2. The Challenge

Semiconductor fabs use CD-SEM (Critical Dimension — Scanning Electron Microscopy) for in-line inspection. During wafer navigation, a tool can lose its positional reference ("drift") and must re-localize a stored high-magnification reference image within a newly acquired, lower-magnification search image. This is the **navigation-error recovery** problem.

The challenge demands:

1. **Semantically correct synthetic SEM data** — realistic physics, geometry, and manufacturing variability.
2. **Scale** — a production training dataset of 100,000 images.
3. **Ground truth** — sub-nanometer-accurate labels for CD, edge position, segmentation, and materials.
4. **Reproducibility** — a scientific benchmark others can verify and extend.

The core geometric constraint is the **10× scale relationship** (1 nm/px reference vs 10 nm/px search), requiring structure diversity across DRAM (2D crystallographic lattice, per-cell contact landmarks) and FinFET (two non-commensurate pitches, weakly-self-similar fins).

---

## 3. Key Features

| Feature | Description |
|---|---|
| **GDSII geometry** | Pure-Python GDSII reader/writer; anti-aliased rasterizer (supersampling = 4) |
| **10 structure types** | iso_line, dense_ls, contact, via, trench, fin, gate, sti, bimaterial, pitch_std |
| **Process simulation** | Deposit / etch / planarize / corner-rounding 2.5D process emulator |
| **Manufacturing variability** | LER (exponential-ACF Gaussian field), CDU, overlay misalignment |
| **SEM physics** | Universal SE yield, Everhart BSE yield, edge brightening, charging, SE-II background |
| **Image degradation** | Gaussian probe PSF, Poisson shot noise, Gaussian detector noise, 16-bit digitization |
| **Ground truth** | Edge maps, CD measurements (0.1 nm), contours, segmentation, material maps, height fields |
| **Full metadata** | Per-sample structure/process/variability/physics/seeds/version/provenance |
| **Checkpointed generation** | Automatic resume, failure recovery, duplicate detection, checksums |
| **65 passing tests** | Unit, interface, pipeline, and L4 scientific validation (12/12 physics targets) |

---

## 4. Repository Structure

```
SEMICON-2026/
├── README.md                     ← You are here
├── .gitignore
│
├── docs/                         Reference material
│   ├── Problem Statement (pptx)  Applied Materials PS 2
│   ├── SEM-CLIP paper (pdf)      Few-shot defect detection reference
│   └── Dataset Discovery Plan
│
├── research/                     21 research phases (210+ documents)
│   ├── phase-1/                  DRAM & FinFET geometry specification
│   ├── phase-2.1 … 2.6/          SEM physics (instrument → imaging artifacts)
│   ├── phase-3.1 … 3.4/          Geometry engine
│   ├── phase-4.1 … 4.5/          System architecture & certification
│   └── phase-5.1 … 5.5/          Implementation roadmap & final audit
│
├── simulator/                    The semicon-sim Python package
│   ├── generate.py               CLI entry point
│   ├── pyproject.toml            Build config (semicon-sim 0.1.0)
│   ├── requirements.txt          numpy, scipy, scikit-image, Pillow, PyYAML
│   ├── configs/                  defaults.yml, materials.yml, demo.yml
│   ├── src/semicon/
│   │   ├── foundation/           datatypes, rng, math, units, image I/O
│   │   ├── geometry/             Geometry Engine (I1→I3)
│   │   ├── physics/              SEM Physics Engine (I4→I6)
│   │   ├── dataset/              ground truth, writer, splitter
│   │   └── orchestration/        config, pipeline, job, CLI
│   ├── structure_library/        GDSII structure fixtures
│   └── tests/                    65 tests across 4 suites
│
├── datasets/                     Dataset specs + generated data
│   ├── generation_configs/       Frozen YAML configs for DS1–DS5
│   ├── manifests/                Sample-plan manifest schema + templates
│   ├── metadata/                 Schema + dataset-level metadata records
│   ├── checksums/                SHA-256 template + verify script
│   ├── documentation/            GT format, schemas, validation spec
│   └── ds1 … ds5/                Dataset outputs (images/GT/metadata/splits)
│
├── validation/                   Generation & audit scripts
│   ├── generate_ds1.py           DS1 smoke test
│   ├── generate_ds2_ds3_ds4.py   DS2–DS4 generation
│   ├── generate_ds5_final.py     DS5 production (checkpointed)
│   ├── run_ds5_production.py     Production orchestrator
│   ├── run_full_audit.py         Integrity / coverage / storage audit
│   └── reports/                  DG completion reports
│
├── reports/                      Operational reports (generation, integrity,
│                                 storage, performance, coverage)
├── statistics/                   ds5_statistics.json, ds5_storage_report.json
├── logs/                         Generation logs
├── tmp_bench/  tmp_profile/      Temporary artifacts (gitignored)
└── .claude/                      Claude Code config (gitignored)
```

---

## 5. System Architecture

### 5.1 High-Level Data Flow

```
┌──────────┐    ┌───────────────────┐    ┌──────────────────┐    ┌──────────┐
│  Config  │───▶│  Geometry Engine  │───▶│   Physics Engine │───▶│ Dataset  │
│   YAML   │    │    (I1→I3)        │    │     (I4→I6)      │    │  Writer  │
└──────────┘    └───────────────────┘    └──────────────────┘    └──────────┘
                      │                        │                      │
                    GDSII                    yield maps           images + GT
                    mask                     SE/BSE                + metadata
                    height field             PSF/charging/         + checksums
                    + material map           noise → image
```

The system is a **pipeline architecture with immutable data passing** — no RPC, no events, no shared mutable state. Each stage consumes a frozen interface and produces the next.

### 5.2 Six-Layer Architecture

| Layer | Responsibility |
|---|---|
| **Presentation** | CLI (`generate.py`, `semicon-sim`) |
| **Configuration** | YAML config system with validation and defaults |
| **Orchestration** | Pipeline controller, job manager, batch runner, checkpoints |
| **Geometry** | GDSII reader, process model, variability engine → height + material maps |
| **Physics** | Signal model, degradation model, image formation → SEM image |
| **Dataset** | Ground truth generator, dataset writer, splits, checksums |

### 5.3 Frozen Interfaces (I1–I8)

| Interface | Producer → Consumer | Data |
|---|---|---|
| **I1** | Rasterer → Process | Rasterized GDSII mask |
| **I2** | Process → Variability | Deterministic height/material field |
| **I3** | Variability → Physics | Variable height + material map |
| **I4** | Signal → Degrade | SE/BSE yield maps |
| **I5** | Degrade → Formation | Degraded (blurred + noisy) yield |
| **I6** | Formation → Dataset | Final SEM image (16-bit TIFF) |
| **I7** | Geometry → Dataset | Ground truth (edges, CD, contours) |
| **I8** | Dataset Writer | All files written to disk |

### 5.4 Module Decomposition (10 modules, 5 subsystems)

| Subsystem | Modules |
|---|---|
| **Geometry** | GDSII Reader, Process Model, Variability Engine |
| **Physics** | Signal Model, Degradation Model, Image Formation |
| **Dataset** | Dataset Writer, Ground Truth Generator |
| **Orchestration** | Pipeline Controller, Job Manager |

### 5.5 Key Design Principles

1. **Single Responsibility** — each module does one thing.
2. **Immutable Interfaces** — data crosses boundaries read-only.
3. **Configuration-Driven** — everything tunable from YAML.
4. **Deterministic by Default** — same seed ⇒ same image.
5. **Progressive Complexity** — physics can be toggled on/off.
6. **Fail Early** — validate config and inputs before work begins.

---

## 6. Scientific Foundations

### 6.1 Frozen Physical Parameters (Phase 2.5)

| Parameter | Frozen Value |
|---|---|
| Accelerating voltage | 1 keV (configurable 0.3–30 keV) |
| Probe current | 50 pA (1–1000 pA) |
| Probe diameter | 3 nm (0.5–10 nm) |
| Pixel dwell time | 1 µs |
| Pixel size | 1.0 nm |
| Si SE yield (1 keV) | 0.50 |
| Si BSE yield (1 keV) | 0.22 (Everhart model) |
| SE escape depth | ~2.5 nm |

### 6.2 Frozen Mathematical Models

- **SE yield**: angular `sec(θ)` law with tilt exponent.
- **BSE yield**: Everhart polynomial from atomic number Z.
- **Pixel intensity**: linear combination of SE + BSE signals.
- **Probe blur**: Gaussian PSF (FWHM tied to probe diameter).
- **Shot noise**: Poisson (electron counting statistics).
- **Charging**: constant-factor charge model with lateral diffusion.

### 6.3 Canonical 14-Stage Rendering Pipeline

1. Geometry
2. Material assignment
3. Surface normals
4. SE yield
5. BSE yield
6. Detector collection
7. SE-II background
8. Probe convolution (PSF)
9. Charging correction
10. Pixel integration
11. Gain scaling
12. Shot noise
13. Excess/detector noise
14. Digitization (16-bit, round-half-even)

### 6.4 Material Library

| ID | Material | Z | SE yield δ₀ | BSE η | Escape (nm) | Type |
|---|---|---|---|---|---|---|
| 0 | Vacuum | 0 | 0.00 | 0.00 | 0.0 | — |
| 1 | Silicon | 14 | 0.50 | 0.22 | 2.5 | Semiconductor |
| 2 | SiO₂ | 10.8 | 0.60 | 0.18 | 2.8 | Dielectric |
| 3 | SiN | 10.4 | 0.52 | 0.18 | 2.6 | Dielectric |
| 4 | Copper | 29 | 0.40 | 0.35 | 1.8 | Conductor |
| 5 | Tungsten | 74 | 0.35 | 0.53 | 1.5 | Conductor |
| 6 | Photoresist | 5 | 0.80 | 0.03 | 4.0 | Organic |

### 6.5 Structure Types (10, frozen)

| Type | Description | Contrast Mechanism |
|---|---|---|
| `iso_line` | Single isolated line | Topographic |
| `dense_ls` | Dense line/space array | Topographic |
| `contact` | Contact-hole array | Material (W in SiO₂) |
| `via` | Via-hole array | Material (Cu in SiO₂) |
| `trench` | Recessed trench | Topographic |
| `fin` | Raised fins | Topographic + material |
| `gate` | Gate bar over fins | Multi-material |
| `sti` | Shallow-trench isolation | Material (SiO₂ in Si) |
| `bimaterial` | Side-by-side blocks | Pure material contrast |
| `pitch_std` | Mixed-pitch lines | Multi-pitch |

---

## 7. Dataset Specification (DS1–DS5)

Five datasets form the production portfolio (frozen in Phase 5.5).

| Dataset | Purpose | Samples | Size | Master Seed | Validation Gates |
|---|---|---|---|---|---|
| **DS1** development | Smoke tests, module debugging | 50 | ~56 MB | 1001 | L1–L2 |
| **DS2** unit-test | CI regression, golden hashes | 100 @512² | ~99 MB | 2002 | L1–L5 |
| **DS3** validation | Milestone gates | 1,000 | ~1 GB | 3003 | L1–L5 |
| **DS4** scientific-benchmark | Physics accuracy (L4) | 200 | ~200 MB | 4004 | L1–L5 |
| **DS5** final-training | ML/CD-SEM benchmark release | **100,000** | ~205 GB | 5005 | L1–L5 (L4 sampling) |

### 7.1 DS5 — The Primary Deliverable

| Aspect | Value |
|---|---|
| Image | 1024×1024, 16-bit, 1.0 nm/px, TIFF (LZW) |
| Samples | 100,000 |
| Master seed | 5005 |
| Splits | train 70,000 / val 15,000 / test 15,000 (stratified, disjoint) |
| Config | `datasets/generation_configs/ds5_final_training.yml` |

**Structure weighting (application-weighted):**

| Structure | Weight | Count |
|---|---|---|
| dense_ls | 20.0% | 20,000 |
| contact | 15.0% | 15,000 |
| iso_line | 15.0% | 15,000 |
| via | 10.0% | 10,000 |
| fin | 10.0% | 10,000 |
| gate | 10.0% | 10,000 |
| trench | 8.0% | 8,000 |
| sti | 5.0% | 5,000 |
| bimaterial | 4.0% | 4,000 |
| pitch_std | 3.0% | 3,000 |

**Sampled parameter ranges (random sampling, full certified ranges):**

| Parameter | Range |
|---|---|
| CD (critical dimension) | 10–500 nm |
| Height | 20–200 nm |
| Pitch | 20–1000 nm |
| LER 3σ | 0–5 nm |
| LER correlation length ξ | 5–100 nm |
| Overlay | 0–10 nm |
| CDU σ | 0–2 nm |
| Beam energy | 0.3–30 keV |
| Probe current | 1–1000 pA |
| Probe diameter | 0.5–10 nm |

### 7.2 Canonical Per-Sample Layout

```
{dataset_name}/
├── dataset_index.json          sample index + aggregate stats + hashes
├── SHA256SUMS                  integrity registry
├── README.md
├── images/<sample>.tiff        SEM image (16-bit)
├── ground_truth/
│   ├── <sample>_gt.json        edge maps, CD, contours, segmentation
│   ├── <sample>_material.png   material segmentation map
│   └── <sample>_height.npy     height field (float64) — regenerable
├── metadata/
│   ├── <sample>_config.json    exact generation config
│   ├── <sample>_metadata.json  full scientific metadata
│   └── <sample>_timing.json    generation timing
└── splits/
    ├── train.txt  val.txt  test.txt
```

---

## 8. How Datasets Are Generated

### 8.1 Generation Workflow

```
1. Load frozen generation config:  generation_configs/dsN_*.yml
2. Derive deterministic sample plan from master seed + config
3. Generate each sample through the geometry → physics → dataset pipeline
4. Write images, ground truth, metadata, checksums
5. Verify integrity + coverage
6. Compute SHA-256 checksums
7. Produce statistics and release report
```

### 8.2 DS5 Production Pipeline (validation/generate_ds5_final.py)

The DS5 generation script provides a production-grade pipeline:

| Feature | Behavior |
|---|---|
| **Parallel execution** | Multiprocessing worker pool (2 workers validated on 25 GB RAM) |
| **Chunked generation** | 10,000 samples per chunk (10 chunks) |
| **Checkpointing** | `checkpoint.json` written every 500 samples |
| **Automatic resume** | Continues from the latest completed sample index |
| **Failure recovery** | 3 retry attempts per sample |
| **Progress logging** | Throughput, ETA, coverage to `logs/` |
| **Storage monitoring** | Disk space checked before each chunk; height.npy purged after chunks |
| **Integrity verification** | All artifacts present; checksums verified |
| **Duplicate detection** | Identifies identical hashes |
| **Coverage verification** | Structure-type + parameter-range coverage vs targets |
| **Stratified splits** | 70/15/15, disjoint, stratified by structure type |

### 8.3 Storage Architecture & Optimization

| Component | Per-sample | 100k Total | Disposition |
|---|---|---|---|
| `images/*.tiff` (16-bit LZW) | ~2.0 MB | ~200 GB | **Kept** (required) |
| `ground_truth/*_gt.json` | ~40 KB | ~4 GB | **Kept** (required) |
| `ground_truth/*_material.png` | ~3 KB | ~0.3 GB | **Kept** (required) |
| `ground_truth/*_height.npy` | ~8.0 MB | ~800 GB | **Deleted after chunk** (regenerable) |
| `metadata/*.json` | ~10 KB | ~1 GB | **Kept** (required) |
| **Release total** | ~2 MB | **~205 GB** | Fits under 250 GB target |

> The height field is an *input* to ground-truth derivation, not a canonical ground-truth artifact (Phase 4.4). Deleting `*_height.npy` after each chunk saves ~800 GB with **zero** effect on image pixels, ground truth correctness, determinism, or reproducibility — the height field is always regenerable from seed + config.

### 8.4 Reproducibility Guarantee

Same `generation_configs/dsN_*.yml` + pinned software versions + same platform → **bitwise-identical dataset** (SHA-256 verified). Cross-platform bitwise equality is not guaranteed (documented tolerance). Every sample records its full seed hierarchy (`master_seed → sample_seed → stage_seeds`).

---

## 9. Ground Truth Format

Ground truth is emitted as per-sample JSON plus optional raster artifacts (precision 0.1 nm).

| Artifact | File | Format |
|---|---|---|
| Edge maps | `<sample>_gt.json` | edge IDs, types, vertex coordinates (nm) |
| CD measurements | `<sample>_gt.json` | per-feature CD with 0.1 nm accuracy |
| Segmentation | `<sample>_gt.json` | RLE-encoded class maps |
| Contours | `<sample>_gt.json` | polygon vertex lists (nm) |
| Edge types | `<sample>_gt.json` | top_left / top_right / bottom … |
| Height field | `<sample>_height.npy` | float64 M×N, nm |
| Material map | `<sample>_material.png` | uint8 palette PNG |

**Coordinate system (frozen):** row = Y, column = X; top-left origin; `nm = index × pixel_size_nm`.

**Example GT JSON:**

```json
{
  "sample": "ds3_validation_000123",
  "structure_type": "iso_line",
  "pixel_size_nm": 1.0,
  "edges": [
    {
      "edge_id": 0,
      "edge_type": "top_left",
      "points_nm": [[30.0, 10.0], [30.0, 500.0]],
      "cd_target": 30.0
    }
  ],
  "cd_measurements": [
    { "feature": "line_top", "cd_nm": 30.1 },
    { "feature": "line_bottom", "cd_nm": 32.4 },
    { "feature": "space", "cd_nm": 60.2 }
  ],
  "segmentation": {
    "classes": { "0": "vacuum", "1": "Si", "2": "SiO2", "3": "SiN", "4": "Cu", "5": "W", "6": "PR" },
    "encoding": "rle",
    "data": { "1": "RLE-run-length-string" }
  }
}
```

---

## 10. Metadata Schema & Usage

Every sample carries a JSON metadata record with **7 mandatory categories**. Use it to filter, stratify, and trace any sample back to its exact generation provenance.

| Category | Key fields | Purpose |
|---|---|---|
| **structure** | structure_type, cd_nm, pitch_nm, height_nm | Which structure & nominal dimensions |
| **process** | layer_stack, process_steps | Material stack & fabrication flow |
| **variability** | ler_3sigma_nm, ler_xi_nm, overlay_dx/dy_nm, cdu_sigma_nm | Manufacturing perturbations applied |
| **physics** | beam_energy_keV, probe_current_pA, probe_diameter_nm, detector_config | Exact instrument settings |
| **seeds** | master_seed, sample_seed, stage_seeds | Full RNG provenance |
| **version** | app_version, git_hash, schema_version, material_library_hash | Software provenance |
| **provenance** | generation_date, dataset_name, dataset_version, warnings | Dataset provenance |

**Dataset-level index** (`dataset_index.json`) aggregates counts, structure distribution, parameter ranges, splits, and per-sample SHA-256 hashes — enabling full-dataset audits without scanning every file.

### Common metadata usage patterns

- **Stratified sampling** — group by `structure_type` for balanced batches.
- **Filtering by difficulty** — select by `variability.ler_3sigma_nm` or `physics.noise_enabled`.
- **Reproducing a sample** — replay `seeds.sample_seed` + `*_config.json` to regenerate bitwise.
- **Auditing coverage** — compare `structure_distribution` and `parameter_ranges` to config targets.

---

## 11. Training Guide

### 11.1 What You Get Per Sample

```
sample_id_000123/
├── images/sample_id_000123.tiff      # input image  (X)
├── ground_truth/sample_id_000123_gt.json   # labels (y)
├── ground_truth/sample_id_000123_material.png
├── metadata/sample_id_000123_metadata.json # conditioning info
```

### 11.2 Task Mappings

| Task | Input | Ground-truth label |
|---|---|---|
| **CD metrology / regression** | image → CD prediction | `cd_measurements` |
| **Edge detection** | image → edge maps | `edges` / `contours` |
| **Semantic segmentation** | image → class map | `material.png` / `segmentation` |
| **Defect classification** | image → defect/no-defect | structure + variability fields |
| **Navigation / Drift-Sense** | reference patch in search image | coordinate ground truth |

### 11.3 Recommended Data Loading

```python
import json
import numpy as np
from PIL import Image
from torch.utils.data import Dataset

CLASS_MAP = {"vacuum": 0, "Si": 1, "SiO2": 2, "SiN": 3, "Cu": 4, "W": 5, "PR": 6}

class SEMICONDataset(Dataset):
    def __init__(self, split_file, root="datasets/ds5_final_training"):
        self.samples = [s.strip() for s in open(split_file)]
        self.root = root

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, i):
        sid = self.samples[i]
        image = np.array(Image.open(f"{self.root}/images/{sid}.tiff")).astype(np.float32)
        image = (image / 65535.0).astype(np.float32)            # normalize 16-bit

        gt = json.load(open(f"{self.root}/ground_truth/{sid}_gt.json"))
        seg = np.array(Image.open(f"{self.root}/ground_truth/{sid}_material.png"))
        seg = np.vectorize(CLASS_MAP.get)(seg).astype(np.int64)  # material → class id

        meta = json.load(open(f"{self.root}/metadata/{sid}_metadata.json"))
        # meta["structure"]["cd_nm"], meta["variability"]["ler_3sigma_nm"], ...
        return {"image": image, "segmentation": seg,
                "cd_targets": gt["cd_measurements"], "metadata": meta}
```

### 11.4 Training Tips

1. **Always normalize 16-bit TIFF** to [0,1] (`/65535`) — never assume uint8.
2. **Use the metadata for curriculum learning**: train on low-LER samples first, ramp up `ler_3sigma_nm`.
3. **Stratify batches by `structure_type`** — the dataset is intentionally unbalanced (dense_ls 20% vs pitch_std 3%).
4. **Split files are pre-generated and disjoint** — use `splits/train.txt`, `val.txt`, `test.txt` verbatim to avoid leakage.
5. **Reproducibility**: the same sample IDs are stable across regenerations on the same platform — cache predictions by sample ID.

---

## 12. Validation & Quality Gates

### 12.1 Validation Levels (L1–L5)

| Level | Scope | Pass Criteria |
|---|---|---|
| **L1** | File completeness | 100% of manifest entries present |
| **L2** | Metadata consistency | 100% cross-references pass |
| **L3** | Ground-truth accuracy | CD within ±0.1 nm of config |
| **L4** | Scientific validation | Physics targets met (below) |
| **L5** | Reproducibility | SHA-256 match on same platform |

### 12.2 L4 Scientific Targets (verified)

| Metric | Target | Measured |
|---|---|---|
| Si SE yield @ 1 keV | δ ∈ [0.4, 0.8] | 0.571 ✅ |
| Si BSE yield @ 1 keV | η ∈ [0.15, 0.25] | 0.215 ✅ |
| BSE ordering | W > Cu > Si | 0.36 > 0.28 > 0.22 ✅ |
| Edge brightening | 1.5–2.5 | 2.000 ✅ |
| PSF FWHM | ±2% | 4.000 ✅ |
| Shot noise mean | < 0.02 | 0.0004 ✅ |
| Shot noise variance | [0.2, 3.0] | 0.978 ✅ |
| PSF mean preservation | < 0.005 | 0.0000 ✅ |
| 16-bit dtype | uint16 | uint16 ✅ |
| Value range | [0, 65535] | ✅ |
| CD accuracy | ≤ 2.0 nm | 0.0 nm ✅ |

---

## 13. Quick Start

```bash
cd simulator
pip install -e .                     # install semicon-sim

python generate.py self-check        # verify system health (~0.3 s)
python generate.py run               # single iso_line image
python generate.py build-library --out structure_library/semicon.gds
python generate.py batch --n 20 --out demo_output   # 20-image demo
```

### CLI Reference

| Command | Description |
|---|---|
| `python generate.py self-check` | Run self-diagnostics |
| `python generate.py run` | Generate one sample |
| `python generate.py batch --n N --out DIR` | Generate N samples to DIR |
| `python generate.py build-library --out FILE` | Build structure library |
| `semicon-sim --validate <dataset> --level L1..L5` | Run validation gate |

### Project Configuration

```bash
# Frozen DS5 generation config (do not edit — sealed for reproducibility)
datasets/generation_configs/ds5_final_training.yml
```

---

## 14. Testing

```bash
cd simulator
pytest tests/            # all 65 tests
pytest tests/unit/       # unit tests (foundation/geometry/physics/variability)
pytest tests/interface/  # I1–I8 interface contracts
pytest tests/pipeline/   # end-to-end pipeline
pytest tests/scientific/ # L4 scientific validation (12 tests)
```

**Suite totals:** 65/65 passing — 30 unit, 8 interface, 2 pipeline, 12 scientific + variability/regression.

**Determinism regression:** same seed → bit-identical image, verified in CI.

---

## 15. Project Status (DG1–DG7)

| Milestone | Description | Status |
|---|---|---|
| **DG1** | Simulator implementation (semicon-sim) | ✅ Complete |
| **DG2** | Validation & certification | ✅ Complete |
| **DG3** | Production framework + DS2–DS4 | ✅ Complete |
| **DG4** | DS5 production generation (100k) | 🔄 In progress |
| **DG5** | Dataset validation & benchmarking | ⏳ Blocked by DG4 |
| **DG6** | Release packaging | ⏳ Pending |
| **DG7** | Documentation & submission | ⏳ Pending |

**DS1–DS4:** 1,350 samples generated (~1.3 GB) — complete.

**DS5 generation status:** checkpointed production run; images written under `datasets/ds5_final_training/`, progress tracked in `logs/` and `reports/`. See `reports/dg4_final_report.md` for the live DG4 report.

---

## 16. Research Documentation

The full research program (210+ documents across 21 phases) lives in `research/`:

| Phase Group | Topic | Highlights |
|---|---|---|
| **Phase 1** | Geometry spec | DRAM 6F² cells, FinFET, 10× scale constraint |
| **Phase 2.1–2.6** | SEM physics | Instrument, beam-sample interaction, contrast, noise, frozen 14-stage pipeline |
| **Phase 3.1–3.4** | Geometry engine | 2.5D height-field representation, 10 structures, 48 parameters |
| **Phase 4.1–4.5** | Architecture | 6-layer pipeline, 8 interfaces, FAIR dataset spec, certification 95/100 |
| **Phase 5.1–5.5** | Implementation | Roadmap, module breakdown, release spec, final audit 94/100 |

Each phase folder contains numbered documents (`01_executive_summary.md` → `10_phaseX_final_report.md`) with complete reference lists.

---

## 17. License & Citation

All code and datasets are licensed under **CC BY 4.0** (Attribution).

When publishing work that uses this repository, please cite:

> **SEMICON 2026 Synthetic SEM Image Generator (Drift-Sense)** — Applied Materials SEMICON 2026 Hackathon. Deterministic physics-based synthetic SEM dataset generator with pixel-accurate ground truth.

---

*Generated for the Applied Materials SEMICON 2026 Hackathon. Research frozen by Phase 5.5 certification; simulator implemented in DG1; DS5 production generation tracked under DG4.*
