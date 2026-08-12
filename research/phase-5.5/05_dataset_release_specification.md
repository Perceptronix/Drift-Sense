# Dataset Release Specification

**Research Phase:** 5.5
**Document:** 05_dataset_release_specification.md
**Date:** 2026-07-30

---

## 1. Release Package Structure

```
datasets/
├── README.md                     ← Dataset portfolio overview, citation, license
├── generation_configs/           ← Frozen YAML generation templates
│   ├── ds1_development.yml
│   ├── ds2_unit_test.yml
│   ├── ds3_validation.yml
│   ├── ds4_scientific_benchmark.yml
│   └── ds5_final_training.yml
├── ds1_development/              ← Populated after implementation
├── ds2_unit_test/
├── ds3_validation/
├── ds4_scientific_benchmark/
├── ds5_final_training/
├── manifests/                    ← Generation manifests (sample plans)
│   ├── ds1_manifest.json         ← Sample manifests (generated per dataset)
│   ├── ds2_manifest.json
│   ├── ds3_manifest.json
│   ├── ds4_manifest.json
│   └── ds5_manifest.json
├── metadata/                     ← Schema definitions + dataset-level metadata
│   ├── sample_metadata_schema.json
│   ├── dataset_index_schema.json
│   ├── ds1_metadata.json         ← Dataset-level metadata records
│   ├── ds2_metadata.json
│   ├── ds3_metadata.json
│   ├── ds4_metadata.json
│   └── ds5_metadata.json
├── checksums/                    ← SHA-256 registries (generated after generation)
│   ├── SHA256SUMS.template       ← Registry template
│   └── verify_checksums.sh       ← Verification script (reference)
└── documentation/                ← Dataset documentation
    ├── dataset_readme_template.md
    ├── ground_truth_format.md
    ├── metadata_schema.md
    ├── validation_specification.md
    └── release_notes_template.md
```

---

## 2. Dataset Specifications (All Five)

### DS1: Development Dataset (50)

| Aspect | Specification |
|---|---|
| **Purpose** | Development smoke tests; module debugging; fast iteration |
| **Size** | 50 images (5 × 10 structures) |
| **Structure distribution** | Uniform: 5 per structure type |
| **Material distribution** | Default stacks (Si substrate; SiO₂/SiN; Cu/W; PR) |
| **Parameter ranges** | Nominal mid-range values |
| **Seed policy** | `master_seed: 1001`; per-sample derived |
| **Expected size** | ~200 MB core |
| **Ground truth** | Full |
| **Metadata schema** | Full (Phase 4.4 doc 05) |
| **Validation gates** | L1, L2 |
| **Release criteria** | All 50 valid; index consistent; determinism spot-check |
| **Versioning** | `dev_vX.Y.Z` — regenerated freely |

### DS2: Unit-Test Dataset (100)

| Aspect | Specification |
|---|---|
| **Purpose** | CI regression; golden-reference pinning |
| **Size** | 100 (10 × 10 structures) at 512×512 |
| **Structure distribution** | Uniform: 10 per type |
| **Material distribution** | Default + one edge-case per structure |
| **Parameter ranges** | Nominal + boundary values |
| **Seed policy** | `master_seed: 2002`; fixed per-sample hashes committed |
| **Expected size** | ~100 MB |
| **Ground truth** | Full |
| **Metadata schema** | Full |
| **Validation gates** | L1, L2, L5 (determinism) |
| **Release criteria** | Golden hashes match; CI green |
| **Versioning** | `unit_vX.Y.Z` — bump on schema change |

### DS3: Validation Dataset (1,000)

| Aspect | Specification |
|---|---|
| **Purpose** | Milestone gates; L1–L5 validation; cross-module consistency |
| **Size** | 1,000 (100 × 10 structures) at 1024×1024 |
| **Structure distribution** | Stratified: 100 per type |
| **Material distribution** | Full range of stacks |
| **Parameter ranges** | Full certified ranges stratified (CD 10–500, height 20–200, pitch 20–1000, LER 0–5 nm) |
| **Seed policy** | `master_seed: 3003`; fixed for release cycle |
| **Expected size** | ~4 GB |
| **Ground truth** | Full |
| **Metadata schema** | Full |
| **Validation gates** | L1–L5 |
| **Release criteria** | All L1–L5 pass; stats report produced |
| **Versioning** | `val_vX.Y.Z` — per release cycle |

### DS4: Scientific-Benchmark Dataset (200)

| Aspect | Specification |
|---|---|
| **Purpose** | L4 scientific validation; physics accuracy vs literature |
| **Size** | 200 (20 × 10 structures) |
| **Structure distribution** | Uniform: 20 per type |
| **Material distribution** | Explicit multi-material: Si/SiO₂/SiN; Si/Cu; Si/W; PR-on-Si |
| **Parameter ranges** | Calibration set (analytic results known) |
| **Seed policy** | `master_seed: 4004`; frozen, audited |
| **Expected size** | ~1 GB (includes yield maps) |
| **Ground truth** | Full + yield maps (SE/BSE) |
| **Metadata schema** | Full + physics config + material_library_hash |
| **Validation gates** | L4 (scientific), L1–L3 |
| **Release criteria** | Yield values within published ranges; CD/LER accuracy met |
| **Versioning** | `bench_vX.Y.Z` — frozen |

### DS5: Final-Training Dataset (100,000)

| Aspect | Specification |
|---|---|
| **Purpose** | Primary deliverable; ML/CD-SEM benchmarking |
| **Size** | 100,000 at 1024×1024 |
| **Structure distribution** | Application-weighted: dense_ls 20%, contact 15%, via 10%, iso_line 15%, fin 10%, gate 10%, trench 8%, sti 5%, bimaterial 4%, pitch_std 3% |
| **Material distribution** | Realistic process stacks (Phase 1 library) |
| **Parameter ranges** | Full certified ranges; random sweep sampling |
| **Seed policy** | `master_seed: 5005`; deterministic sample plan |
| **Expected size** | ~400 GB |
| **Ground truth** | Full |
| **Metadata schema** | Full |
| **Validation gates** | L1–L5; statistical coverage checks |
| **Splits** | Train 70,000 / Val 15,000 / Test 15,000 (deterministic) |
| **Release criteria** | L1–L5 pass; benchmark-readiness review; stakeholder sign-off on weighting |
| **Versioning** | `train_vX.Y.Z` — frozen release |

---

## 3. Generation Config Template (Common Structure)

Every `generation_configs/ds*.yml` follows the canonical schema:

```yaml
dataset:
  name: dsN_<type>
  version: 1.0.0
  mode: batch | sweep
  n_samples: N
  master_seed: NNNN
  image:
    width: 1024
    height: 1024
    pixel_size_nm: 1.0
  structure_distribution: {type: weight, ...}
  materials: [...]
  parameter_ranges: {...}
  variability: {ler_3sigma: [...], xi: [...], overlay: [...]}
  physics: {beam_energy_keV: [...], probe_current_pA: [...], ...}
  ground_truth: true
  artifacts: [image, gt, config, metadata]
  splits: {train: 0.70, val: 0.15, test: 0.15}
  license: CC BY 4.0
```

---

## 4. Metadata Schema

| Category | Fields | Mandatory |
|---|---|---|
| Structure | structure_type, cd_nm, pitch_nm, height_nm | ✅ |
| Process | layer_stack, process_steps | ✅ |
| Variability | ler_3sigma, ler_xi, overlay_dx_dy, cdu_sigma | ✅ |
| Physics | beam_energy, probe_current, detector_config | ✅ |
| Seeds | master_seed, sample_seed, stage_seeds | ✅ |
| Version | app_version, git_hash, schema_version, material_library_hash | ✅ |
| Provenance | generation_date, dataset_name, dataset_version, warnings | ✅ |

---

## 5. Validation Gates per Dataset

| Dataset | L1 Files | L2 Metadata | L3 GT | L4 Scientific | L5 Reproducibility |
|---|---|---|---|---|---|
| DS1 | ✅ | ✅ | ✅ | — | spot |
| DS2 | ✅ | ✅ | ✅ | — | ✅ |
| DS3 | ✅ | ✅ | ✅ | — | ✅ |
| DS4 | ✅ | ✅ | ✅ | ✅ | ✅ |
| DS5 | ✅ | ✅ | ✅ | sampling | ✅ |

---

## 6. Release Criteria Summary

| Dataset | Release When |
|---|---|
| DS1 | Pipeline M3 complete |
| DS2 | Golden hashes committed; CI green |
| DS3 | L1–L5 pass on 1,000 samples |
| DS4 | L4 scientific targets met |
| DS5 | All gates + stakeholder weighting review |

---

## Sources

- Phase 4.4 — Dataset specification.
- Phase 5.4 — Production dataset strategy (DS1–DS5).
- [S5] Wilkinson et al., FAIR principles, 2016.
