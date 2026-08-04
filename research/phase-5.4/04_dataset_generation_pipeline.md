# Dataset Generation Pipeline

**Research Phase:** 5.4
**Document:** 04_dataset_generation_pipeline.md
**Date:** 2026-07-30

---

## 1. Generation Modes

| Mode | CLI | Purpose | Scale |
|---|---|---|---|
| **Single** | `semicon-sim run --config c.yml` | One image; debugging, unit tests | 1 |
| **Batch** | `semicon-sim batch --manifest m.json` | Deterministic parameter grid | 10²–10⁴ |
| **Sweep** | `semicon-sim sweep --ranges r.yml --n 5000` | Randomized sampling over ranges | 10³–10⁶ |

All three modes share the identical per-image pipeline (Doc 02); only sample generation differs.

---

## 2. Canonical Dataset Generation Process (Frozen)

```
DATASET DEFINITION
    Config: dataset section {name, version, n_samples, mode, splits,
                             structures, materials, parameter_ranges,
                             rng: {master_seed}, artifacts}
        │
        ▼
SAMPLE PLAN GENERATION
    For each sample i ∈ [0, n):
        structure_type  ← sampled from distribution (frozen policy)
        parameters      ← sampled from ranges via seeded RNG
        sample_seed     ← derive(master_seed, dataset_name, i)
        config_i        ← merged dataset config + sample parameters
    Write job_manifest.json (list of resolved per-sample configs + seeds)
        │
        ▼
BATCH EXECUTION (orch_job)
    Worker pool (processes, n_workers)
    For each sample: cache check → run_pipeline → validate → write
    Checkpoint per sample; retry transient; record failures
        │
        ▼
DATASET FINALIZATION
    Aggregate dataset_index.json
    Compute dataset_statistics.json
    Generate splits (train/val/test)
    Generate SHA256SUMS
    Run validation L1–L5
    Write README.md + LICENSE
        │
        ▼
PACKAGING
    dataset_name_vX.Y.Z.tar.gz + .sha256
```

---

## 3. Random Seed Strategy

| Seed | Derivation | Frozen Ref |
|---|---|---|
| **Master seed** | Dataset config `rng.master_seed` (default 42; must be non-zero) | Phase 4.3 RD7 |
| **Structure seed** | `derive(master, dataset_name, structure_id)` | Phase 4.3 |
| **Image seed** | `derive(master, dataset_name, sample_index)` | Phase 4.3 |
| **Stage seeds** | `derive(image_seed, stage_name)` for LER, overlay, CDU, noise | Phase 4.3 |
| **Parameter seeds** | `derive(image_seed, "params")` — drives parameter sampling | Operational policy |

**Determinism guarantee:** Same dataset definition (name, master_seed, version) → identical sample plan → identical dataset. Verified by SHA-256 at L5.

---

## 4. Parameter Sampling

| Strategy | Use Case | Implementation |
|---|---|---|
| **Grid (batch)** | Exhaustive coverage of discrete parameters | Explicit cartesian list in manifest |
| **Stratified (sweep)** | Uniform coverage of continuous ranges | Seeded RNG stratified per decile |
| **Random (sweep)** | Distributional coverage | Seeded uniform/normal per range |
| **Fixed** | One-off targeted samples | Pin parameter in config |

**Sampling policy (operational policy):**

| Parameter | Range | Distribution |
|---|---|---|
| CD | 10–500 nm | Uniform log or explicit set |
| Height | 20–200 nm | Uniform |
| Pitch | 20–1000 nm | Explicit set |
| LER 3σ | 0–5 nm | Uniform |
| LER ξ | 5–100 nm | Log-uniform |
| Beam energy | 0.3–30 keV | Explicit set |
| Probe current | 1–1000 pA | Log-uniform |

---

## 5. Metadata Capture

Every sample produces (frozen Phase 4.4):

| Artifact | Content | Mandatory |
|---|---|---|
| `*_config.json` | Full resolved config | ✅ |
| `*_metadata.json` | Seeds, versions, timing, warnings, provenance | ✅ |
| `*_timing.json` | Per-stage durations | Optional |

**Dataset-level metadata** in `dataset_index.json`:

| Field | Content |
|---|---|
| dataset name/version/schema | Identity |
| generation date | ISO 8601 |
| n_samples / n_success / n_failed | Counts |
| parameter ranges | Sampled coverage |
| structure distribution | Counts per type |
| material distribution | Counts per material |
| rng master seed | Reproducibility anchor |
| git hash / app version | Provenance |
| license | CC BY 4.0 |

---

## 6. Ground Truth Generation

| Aspect | Decision | Frozen Ref |
|---|---|---|
| **Module** | data_groundtruth (M7), parallel with physics stages | Phase 4.3 RD5 |
| **Content** | Edge maps, CD, segmentation, contours, edge types | Phase 4.4 doc 04 |
| **Precision** | 0.1 nm | Phase 4.4 doc 04 |
| **Enabling** | `dataset.include_ground_truth` (default true for training datasets) | Phase 4.4 doc 03 |
| **Optional extras** | Height field (.npy), material map (.png), yield maps (.npz) — flag-gated | Phase 4.4 doc 03 |

---

## 7. Output Organization (Frozen)

```
{dataset_name}/
├── dataset_index.json
├── dataset_schema.txt
├── LICENSE
├── README.md
├── images/*.tiff
├── ground_truth/*.json, *_height.npy, *_material.png, *_yields.npz
├── metadata/*_config.json, *_metadata.json, *_timing.json
├── splits/train.txt, val.txt, test.txt
├── logs/
└── SHA256SUMS
```

Frozen refs: Phase 4.4 docs 02, 03.

---

## 8. Dataset Versioning

| Version event | Bump | Trigger |
|---|---|---|
| Bug fix / regeneration | patch | No schema change |
| New structure/physics feature | minor | Backward-compatible addition |
| Schema/semantics change | major | Breaking change |

`dataset_id = (name, version, generation_date)` — recorded in index and every metadata file.

---

## 9. Reproducibility at Dataset Level

| Check | Method |
|---|---|
| Sample-plan determinism | Same config+master_seed → identical manifest |
| Per-image determinism | SHA-256 of image equals reference |
| Dataset-level determinism | Full regeneration → identical SHA256SUMS (same platform) |
| Cache independence | Cache disabled regenerates identical output |
| Version traceability | Every artifact carries dataset version + hashes |

---

## 10. Pipeline Validation of Generated Datasets

| Check | Level | Gate |
|---|---|---|
| File completeness | L1 | Every manifest entry on disk |
| Metadata consistency | L2 | Cross-field agreement |
| GT accuracy | L3 | CD within tolerance |
| Version compatibility | L4 | Uniform schema |
| Reproducibility | L5 | SHA-256 match |
| Statistics | — | Per-type counts, parameter coverage |

Frozen refs: Phase 4.4 doc 06.

---

## Sources

- Phase 4.3 — Runtime decisions (seed chain RD7, parallelism RD3/RD5, cache RD8, checkpoint RD10).
- Phase 4.4 — Dataset spec (organization, artifacts, GT, metadata, validation).
- Phase 5.1 — WBS (orch_job, CLI, validation).
- [S4] J. Kleppmann, *Designing Data-Intensive Applications*, O'Reilly, 2017.
- [S5] Wilkinson et al., "The FAIR Guiding Principles," *Scientific Data*, vol. 3, 2016.
